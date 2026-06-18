"""
Game state and world simulation for KEPLER ISOLATION game.

GameState holds everything (player, rooms, monster, flags) and owns the
"advance the world one turn" logic: sound propagation, monster AI, the toxic
atmosphere, the boarding event, and same-room detection.
"""

import os
import random
import sys
from collections import deque
from typing import TYPE_CHECKING

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monster import Monster
from room import Room

if TYPE_CHECKING:
    from player import Player

# Deterministic tie-break order for shortest-path direction reporting.
DIRECTION_ORDER = ["north", "south", "east", "west", "up", "down", "in", "out"]

SOUND_LABELS = {0: "silent", 1: "quiet", 2: "audible", 3: "loud", 4: "violent"}

# Rooms whose atmosphere is lethal without a suit.
TOXIC_ROOMS = {"surface", "landing_gear", "ridge", "cave_mouth", "signal_cave", "black_pool"}

# Sparse telegraph lines. We never print the monster's state as a word — we let
# these stand in for it. Hunting reads fast and certain; searching reads soft.
NEAR_SIGNS = [
    "Something taps once in the vent.",
    "A handprint appears high on the wall. Too many fingers.",
    "The grille over the duct is peeled outward.",
    "Somewhere close, metal flexes and settles.",
    "A wet sound, then nothing.",
    "The lights stutter, then hold.",
    "The air goes warm and close, the way breath does.",
    "Something is breathing in time with you. You stop. It does not.",
    "A smell finds you first. Old water. Something underneath it.",
    "Three soft tones drift from the vent. The beacon's call. In here, now.",
    "It tries your name. Almost gets it right, in a voice the ship doesn't have.",
]
HUNT_SIGNS = [
    "Footfalls. Fast, then nothing. It knows where you were.",
    "A hatch slams shut two rooms over.",
    "The lights drop to red and stay there.",
    "Metal shrieks, closing the distance.",
    "It is not trying to be quiet anymore.",
]


class GameState:
    def __init__(self):
        self.player: Player | None = None
        self.rooms: dict = {}
        self.current_room_id = "cockpit"
        self.turn_count = 0
        # intro, pre_cave, outside, cave_triggered, returned_to_ship,
        # monster_aboard, final_repair, won, dead
        self.game_phase = "pre_cave"

        self.monster = Monster()

        # Sound system
        self.sound_level = "silent"
        self.last_action_sound = 0

        # Per-command control set by the parser
        self.advance = False  # did this command advance time?
        self.quit_requested = False
        self.restart_requested = False

        # Boarding countdown (turns until the monster comes aboard, or None)
        self.board_countdown = None

        self.flags = {
            "has_terminal": False,
            "suit_taken": False,
            "suit_worn": False,
            "went_outside": False,
            "entered_cave": False,
            "examined_beacon": False,
            "cave_triggered": False,
            "returned_after_cave": False,
            "monster_boarded": False,
            "saw_window_creature": False,
            "comms_damaged_known": False,
            "transmitter_repaired": False,
            "warning_sent": False,
            # Sable, the synthetic who can spend itself to save you — once.
            "sable_awake": False,
            "sable_alive": False,
            "sable_following": False,
            "sable_sacrifice_used": False,
        }

        self.visited_rooms = set()
        self.death_state = None
        self.win_state = False
        self.message_log = []
        self.random_seed = None
        self.rng = random.Random()

    # ------------------------------------------------------------------ #
    # Small helpers
    # ------------------------------------------------------------------ #
    def get_flag(self, name: str) -> bool:
        return self.flags.get(name, False)

    def set_flag(self, name: str, value: bool):
        self.flags[name] = value

    def get_room(self, room_id: str) -> "Room | None":
        return self.rooms.get(room_id)

    @property
    def current_room(self) -> Room:
        return self.rooms[self.current_room_id]

    def add_message(self, message: str):
        self.message_log.append(message)

    # ------------------------------------------------------------------ #
    # Pathfinding over the room graph
    # ------------------------------------------------------------------ #
    def _neighbors(self, room_id: str, use_vents: bool):
        """Yield (direction, neighbor_id) in deterministic order."""
        room = self.rooms.get(room_id)
        if not room:
            return
        ordered = sorted(
            room.exits.items(), key=lambda kv: DIRECTION_ORDER.index(kv[0]) if kv[0] in DIRECTION_ORDER else 99
        )
        for direction, dest in ordered:
            yield direction, dest
        if use_vents:
            for dest in room.vent_exits:
                yield "vent", dest

    def shortest_path(self, start: str, goal: str, use_vents: bool = False):
        """Return (distance, first_direction) of the shortest path, or
        (None, None) if unreachable. first_direction is the exit to take from
        `start`."""
        if start == goal:
            return 0, None
        # Standard BFS, but each frontier node carries the *first* direction we
        # took out of `start` — that's what the scanner reports ("MOTION: west").
        # Seeding neighbours in DIRECTION_ORDER makes ties deterministic.
        queue = deque()
        seen = {start}
        for direction, dest in self._neighbors(start, use_vents):
            if dest not in seen:
                seen.add(dest)
                queue.append((dest, direction, 1))
        while queue:
            room_id, first_dir, dist = queue.popleft()
            if room_id == goal:
                return dist, first_dir
            for _, dest in self._neighbors(room_id, use_vents):
                if dest not in seen:
                    seen.add(dest)
                    queue.append((dest, first_dir, dist + 1))
        return None, None

    # ------------------------------------------------------------------ #
    # Events: cave trigger and boarding
    # ------------------------------------------------------------------ #
    def trigger_cave(self):
        if self.get_flag("cave_triggered"):
            return
        self.set_flag("cave_triggered", True)
        self.game_phase = "cave_triggered"
        self.monster.phase = "following"
        self.monster.state = "following"

    def board_monster(self, spawn_id="airlock"):
        """Bring the monster aboard the ship."""
        m = self.monster
        m.active = True
        m.phase = "aboard"
        m.state = "searching"
        m.current_room_id = spawn_id
        m.tracked_room_id = spawn_id
        m.can_use_vents = True
        m.aggression = 1
        self.set_flag("monster_boarded", True)
        self.game_phase = "monster_aboard"
        self.board_countdown = None

    # ------------------------------------------------------------------ #
    # The turn pipeline
    # ------------------------------------------------------------------ #
    def advance_world(self):
        """Run one full turn of simulation after a time-advancing command.
        Returns a list of message lines to display."""
        assert self.player is not None, "advance_world called before new_game()"
        # The order below is deliberate: toxic air can kill before the monster
        # ever moves, and boarding must resolve before we simulate an aboard
        # monster on the same turn it arrives.
        msgs = []
        self.turn_count += 1
        self.sound_level = SOUND_LABELS.get(self.last_action_sound, "silent")

        # Track how long the player has lingered in this room.
        self.player.stayed_turns_in_room += 1

        # 1. Toxic atmosphere
        toxic_msg = self._resolve_toxic()
        if toxic_msg:
            msgs.append(toxic_msg)
        if self.death_state:
            return msgs

        # 2. Boarding logic
        msgs += self._resolve_boarding()

        # 3. Monster simulation (only once truly aboard)
        if self.monster.active and self.monster.phase == "aboard":
            self.monster.update_suspicion_decay()
            if self.monster.vent_cooldown > 0:
                self.monster.vent_cooldown -= 1
            self._apply_sound_to_monster()
            self._update_aggression()
            self._move_monster()
            self._update_scanner()
            # A vent move announces itself — the peeled grille is the tell.
            if self.monster.used_vent_last_move:
                self.monster.used_vent_last_move = False
                msgs.append("A grille shrieks somewhere close. Peeled open from inside.")
            else:
                sign = self._maybe_telegraph()
                if sign:
                    msgs.append(sign)
            death = self._resolve_same_room()
            if death:
                msgs.append(death)

        return msgs

    def _resolve_toxic(self):
        assert self.player is not None
        room = self.current_room
        if room.toxic and not self.player.is_wearing_suit():
            self.player.outside_exposure_turns += 1
            n = self.player.outside_exposure_turns
            tol = self.player.toxic_tolerance
            if n >= tol:
                self.death_state = "toxic"
                if self.player.type == "synthetic":
                    return "Corrosion finds something vital. Your optics white out.\nA last entry, unsent."
                return "You make it a few more steps.\nThe planet does not even pause to watch."
            # Warning(s) before death
            if self.player.type == "synthetic":
                return "WARNING: corrosive atmosphere. Integrity falling.\nThis is survivable. Briefly."
            return "The air burns. Your eyes flood. There is no breathing this.\nGet sealed, or get inside."
        else:
            # Safe: reset exposure.
            self.player.outside_exposure_turns = 0
        return None

    def _resolve_boarding(self):
        msgs = []
        # Start the countdown when the player returns to the airlock after the cave.
        if (
            self.get_flag("cave_triggered")
            and not self.get_flag("monster_boarded")
            and self.board_countdown is None
            and self.current_room_id == "airlock"
            and self.get_flag("went_outside")
        ):
            self.set_flag("returned_after_cave", True)
            self.board_countdown = self.rng.randint(4, 6)
            msgs.append(
                "The inner hatch cycles shut behind you.\n"
                "Warm air. The old hum. For a moment everything is almost normal."
            )

        # Failsafe: if the player lingers on the ship a long time after the cave
        # trigger without the airlock event, the thing finds another way in.
        # No free pacifist run: if the player lingers aboard and never triggers
        # the cave, the thing got in some other way. Generous threshold — the
        # intended cave trip trips boarding long before this.
        if (
            not self.get_flag("cave_triggered")
            and not self.get_flag("monster_boarded")
            and self.board_countdown is None
            and self.turn_count > 25
            and self.current_room_id not in TOXIC_ROOMS
        ):
            self.set_flag("cave_triggered", True)
            self.monster.phase = "following"
            self.board_countdown = 2

        # Failsafe so the game can't stall: if the player triggers the cave but
        # somehow never returns through the airlock, the thing finds another way
        # in eventually. (In practice the airlock event above pre-empts this.)
        if (
            self.get_flag("cave_triggered")
            and not self.get_flag("monster_boarded")
            and self.board_countdown is None
            and self.current_room_id not in TOXIC_ROOMS
            and self.turn_count > 0
            and self.monster.turns_since_seen > 18
        ):
            self.board_countdown = 1

        if self.board_countdown is not None and not self.get_flag("monster_boarded"):
            self.board_countdown -= 1
            if self.board_countdown <= 0:
                # It came in through the airlock, behind you. Spawning at your
                # back (not at the objective-rich stern) makes the hunt a fair
                # chase: you move away from it toward the parts, not into it.
                spawn = "airlock" if self.get_flag("returned_after_cave") else self._distant_spawn()
                self.board_monster(spawn)
                msgs.append(
                    "Far down the ship, something knocks. Once. Soft.\n"
                    "Then three soft tones — the beacon's call, answered from inside.\n\n"
                    "It came in with you."
                )
        # Count turns since "seen" grows while dormant (used by failsafe).
        if not self.get_flag("monster_boarded"):
            self.monster.turns_since_seen += 1
        return msgs

    def _distant_spawn(self):
        """Pick an aboard spawn room that is far from the player."""
        candidates = ["airlock", "ventral_service", "reactor_room", "lower_hold"]
        best, best_dist = "airlock", -1
        for rid in candidates:
            dist, _ = self.shortest_path(self.current_room_id, rid)
            if dist is not None and dist > best_dist:
                best, best_dist = rid, dist
        return best

    def _apply_sound_to_monster(self):
        """Translate the player's last action sound into suspicion."""
        assert self.player is not None
        m = self.monster
        sound = self.last_action_sound
        proom = self.current_room_id
        if m.current_room_id is None:
            dist = 99
        else:
            dist, _ = self.shortest_path(proom, m.current_room_id, use_vents=False)
            if dist is None:
                dist = 99

        # Ambient reactor masking: small sounds vanish near the reactor.
        room = self.current_room
        if room.ambient_sound >= 3 and sound <= 1:
            sound = 0

        if sound >= 2:
            m.last_heard_room_id = proom
            m.turns_since_heard = 0
        else:
            m.turns_since_heard += 1
        m.turns_since_seen += 1

        gain = {0: 0, 1: 1 if dist <= 3 else 0, 2: 3, 3: 7, 4: 12}.get(sound, 0)
        if gain:
            m.add_suspicion(proom, gain)
            adj = sound // 2
            if adj:
                for _, dest in self._neighbors(proom, use_vents=False):
                    m.add_suspicion(dest, adj)

        # Lingering in one place leaks position.
        if self.player.stayed_turns_in_room > 2 and not self.player.hidden:
            m.add_suspicion(proom, 1)

    def _update_aggression(self):
        assert self.player is not None
        m = self.monster
        if self.game_phase == "final_repair":
            m.aggression = 3
        elif self.player.installed_parts() >= 2:
            m.aggression = max(m.aggression, 2)
        else:
            m.aggression = max(m.aggression, 1)

    def _choose_target(self):
        # Target priority, highest first: a fresh loud sound beats accumulated
        # suspicion, which beats a blind drift toward the player. The drift is
        # intentionally partial (see below) so the player gets breathing room.
        m = self.monster
        # Endgame: once the transmitter is live it camps the objective — the
        # send is meant to be a knife-edge, not a victory lap.
        if self.game_phase == "final_repair":
            m.state = "hunting"
            return "communications"
        if m.last_heard_room_id and m.turns_since_heard <= 2:
            m.state = "hunting"
            return m.last_heard_room_id
        hi = m.get_highest_suspicion_room()
        if hi:
            m.state = "investigating"
            return hi
        m.state = "searching"
        # With no fresh evidence it does NOT know exactly where you are
        # (pillar #1). It checks a spot it's caught you using, then patrols
        # toward a goal biased to your general area — close enough to intercept,
        # vague enough to dodge. Staying quiet keeps it guessing.
        if m.known_hide_room and m.known_hide_room in self.rooms and self.rng.random() < 0.35:
            return m.known_hide_room
        if not m.target_room_id or m.target_room_id not in self.rooms or m.current_room_id == m.target_room_id:
            if self.rng.random() < 0.6:
                m.target_room_id = self._random_room_near(self.current_room_id, 3)
            else:
                m.target_room_id = self.rng.choice(list(self.rooms))
        return m.target_room_id

    def _random_room_near(self, center, maxd):
        """A random room within maxd of center (its general quadrant)."""
        pool = [rid for rid in self.rooms if rid != center and (self.shortest_path(center, rid)[0] or 99) <= maxd]
        return self.rng.choice(pool) if pool else self.rng.choice(list(self.rooms))

    def _move_monster(self):
        m = self.monster
        if m.is_distracted(self.turn_count):
            m.state = "feeding"
            return

        # Speed control: when calm and far, move every other turn.
        if m.current_room_id is None:
            return
        target = self._choose_target()
        if target is None:
            # Patrol: random neighbour occasionally.
            if self.rng.random() < 0.4:
                neighbors = [dest for _, dest in self._neighbors(m.current_room_id, use_vents=False)]
                if neighbors:
                    m.current_room_id = self.rng.choice(neighbors)
            return

        # It always moves exactly one room per turn — same pace as you. You hold
        # your lead by keeping moving; a backtrack, a dead-end, or a pause is
        # what lets it close. A pure, fair pursuit.
        steps = 1

        # Vents are spice, not teleportation: only when agitated, and on a cooldown.
        use_vents = m.can_use_vents and m.vent_cooldown == 0 and (m.aggression >= 2 or self.last_action_sound >= 3)
        for _ in range(steps):
            if m.current_room_id == target:
                break
            dist, first_dir = self.shortest_path(m.current_room_id, target, use_vents=use_vents)
            if first_dir is None:
                break
            self._step_monster(first_dir, use_vents)

    def _step_monster(self, direction, use_vents):
        m = self.monster
        if m.current_room_id is None:
            return
        room = self.rooms[m.current_room_id]
        if direction == "vent":
            # Vents are not direction-keyed; take the first one and pay the
            # cooldown so the next moves are back on foot.
            for dest in room.vent_exits:
                m.current_room_id = dest
                m.used_vent_last_move = True
                m.vent_cooldown = 3
                return
        dest = room.exits.get(direction)
        if dest:
            m.current_room_id = dest

    def _maybe_telegraph(self):
        m = self.monster
        if m.current_room_id is None or m.current_room_id == self.current_room_id:
            return None
        dist, _ = self.shortest_path(self.current_room_id, m.current_room_id)
        if dist is None or dist > 2:
            return None
        # Hunting telegraphs harder and more often than a blind search.
        if m.state == "hunting":
            pool, threshold = HUNT_SIGNS, 0.7
        else:
            pool, threshold = NEAR_SIGNS, 0.55
        if self.rng.random() < threshold:
            return self.rng.choice(pool)
        return None

    def _update_scanner(self):
        """The scanner is useful but never perfect (design pillar #1). It lags,
        and it flickers when the creature is close or near interference — so a
        reading can be a turn stale, which is exactly where dread lives."""
        assert self.player is not None
        m = self.monster
        if self.current_room.scanner_interference or m.current_room_id is None:
            return  # handle_scan reports "scrambled"; leave the belief stale
        dist, _ = self.shortest_path(self.current_room_id, m.current_room_id)
        fresh = 0.85
        if dist is not None and dist <= 1:
            fresh = 0.5  # the signal panics when it's on top of you
        if self.player.type == "synthetic":
            fresh = min(1.0, fresh + 0.15)  # crisper optics
        if self.rng.random() < fresh:
            m.tracked_room_id = m.current_room_id
        # else: keep the previous belief — a one-turn lie.

    def _safe_adjacent(self, exclude):
        """First non-toxic neighbour that isn't the given room (for an escape)."""
        room = self.current_room
        for direction in DIRECTION_ORDER:
            dest = room.exits.get(direction)
            if dest and dest != exclude and dest not in TOXIC_ROOMS:
                return dest
        return None

    def _sable_saves(self):
        """If Sable is following and hasn't been spent, it dies in your place.
        Returns the rescue text, or None if Sable can't help."""
        assert self.player is not None
        if not (self.get_flag("sable_following") and not self.get_flag("sable_sacrifice_used")):
            return None
        self.set_flag("sable_sacrifice_used", True)
        self.set_flag("sable_following", False)
        self.set_flag("sable_alive", False)
        dest = self._safe_adjacent(self.monster.current_room_id)
        if dest:
            self.player.last_room_id = self.current_room_id
            self.current_room_id = dest
            self.player.stayed_turns_in_room = 0
            self.player.hidden = False
            self.player.hidden_spot = None
        # The feeding buys you a few turns.
        self.monster.set_distracted(self.turn_count + 3)
        self.monster.state = "feeding"
        return (
            "Sable moves before you can — it has done this before.\n"
            "It sets itself between you and the dark.\n\n"
            '"The order says save the specimen," it says. "The order is wrong. Go."\n\n'
            "The hatch closes before the sound begins."
        )

    def _resolve_same_room(self):
        """The monster is in the player's room. Decide what happens."""
        assert self.player is not None
        m = self.monster
        if m.current_room_id != self.current_room_id:
            m.searching_streak = 0
            return None

        # It is in the room. Whatever happens next, it now knows you are near —
        # that memory powers the scanner's "it is already looking at you".
        m.turns_since_seen = 0
        m.last_seen_room_id = self.current_room_id

        # Distraction (a thrown object) buys one pass.
        if m.is_distracted(self.turn_count):
            return "It is here — but its attention is elsewhere. Not yet."

        if not self.player.hidden:
            saved = self._sable_saves()
            if saved:
                return saved
            self.death_state = "monster"
            return None  # death message printed by the main loop

        # Player is hidden: roll detection. The first shared turn is grace — a
        # good spot reliably survives it (hiding *works*, briefly). Danger then
        # climbs the longer you overstay, plus noise this turn and how worn the
        # spot is, offset by quality. Never 0% or 100%: stillness isn't safety.
        m.searching_streak += 1
        spot = self.player.hidden_spot or {"quality": 0, "reuse": 0}
        overstay = max(0, m.searching_streak - 1)
        chance = 10 + self.last_action_sound * 25 + overstay * 20 + spot.get("reuse", 0) * 8 - spot.get("quality", 0)
        chance = max(4, min(chance, 96))
        roll = self.rng.randint(1, 100)
        if roll <= chance:
            saved = self._sable_saves()
            if saved:
                return saved
            self.death_state = "monster"
            return None
        # It checked and came up empty: it loses the thread and moves on, so a
        # well-timed hide buys real escape (it doesn't camp your spot forever).
        if m.known_hide_room == self.current_room_id:
            m.known_hide_room = None
        m.target_room_id = None
        if spot.get("reuse", 0) >= 2:
            return (
                f"It goes straight to the {spot['name']}. It is learning your habits.\n"
                "Its attention passes over you. This time."
            )
        return "It is in the room with you.\nIt checks the wrong place. Slowly. Then moves on."
