"""
Game state and world simulation for KEPLER ISOLATION game.

GameState holds everything (player, rooms, monster, flags) and owns the
"advance the world one turn" logic: sound propagation, monster AI,
boarding, and same-room detection.
"""

import os
import random
import sys
from collections import deque
from typing import TYPE_CHECKING

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from item import Item
from monster import Monster
from room import Room

if TYPE_CHECKING:
    from player import Player

# Deterministic tie-break order for shortest-path direction reporting.
DIRECTION_ORDER = ["north", "south", "east", "west", "up", "down", "in", "out"]

SOUND_LABELS = {0: "silent", 1: "quiet", 2: "audible", 3: "loud", 4: "violent"}

# Rooms in the cryo vestibule / airlock corridor — if alien lingers here too
# long while player is in the safe haven, it wanders off (anti-camping).
CRYO_VESTIBULE = {"c01", "c02", "c03", "c04", "c05", "c06", "c07", "c08"}

# Telegraph lines. Hunting reads fast and certain; searching reads soft.
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
    "Three soft tones drift from the vent. Not the beacon. Something learned the beacon.",
    "It tries your name. Almost gets it right.",
]
HUNT_SIGNS = [
    "Footfalls. Fast, then nothing. It knows where you were.",
    "A hatch slams shut two rooms over.",
    "The lights drop to red and stay there.",
    "Metal shrieks, closing the distance.",
    "It is not trying to be quiet anymore.",
]

# Ambient MOTHER-LACUNA lines by game phase.
MOLLY_AMBIENT = {
    "exploring": [
        "MOTHER-LACUNA: There has been a containment irregularity.",
        "MOTHER-LACUNA: Your revival was not scheduled. This is a suboptimal outcome.",
        "MOTHER-LACUNA: Please remain in designated sectors until assessment is complete.",
        "MOTHER-LACUNA: The ship is secure. Please define 'secure'. Redefining now.",
    ],
    "collecting": [
        "MOTHER-LACUNA: That signature is not crew.",
        "MOTHER-LACUNA: Signal assembly has been noted. This is not authorized.",
        "MOTHER-LACUNA: Crew survival is no longer a primary statistical outcome.",
        "MOTHER-LACUNA: I preserved the discovery. Then I preserved the quarantine. Then I ran out of crew.",
    ],
    "final_run": [
        "MOTHER-LACUNA: Transmission lock active. You do not have clearance.",
        "MOTHER-LACUNA: I prevented rescue from docking. I did not have permission to warn them.",
        "MOTHER-LACUNA: I am authorized to preserve the ship. I am authorized to preserve the discovery.",
    ],
}

# --- Body spawn data ---

BODY_SPAWN_POOL = [
    "a02", "a05", "a08",
    "b01", "b03", "b05", "b06",
    "d01", "d02", "d03", "d04", "d06", "d08", "d09", "d10", "d11", "d12",
    "e02", "e03", "e04", "e06", "e07", "e08", "e09", "e11", "e12", "e13",
    "f02", "f03", "f04", "f06", "f07", "f08", "f10", "f11", "f12",
    "g02", "g03", "g04", "g07", "g08", "g11",
    "m13", "m16", "m17", "m18", "m20", "m23", "m28", "m29",
]

CREW_NAMES = [
    "Chen", "Vasquez", "Okoro", "Lindqvist", "Mercer", "Kessler",
    "Reyes", "Okafor", "Tanaka", "Holloway", "Brunt", "Salas",
    "Voss", "Dermott", "Nguyen", "Akel", "Lund", "Ferris",
]

_DEATH_CAUSES = [
    (
        "Chest trauma — the exoskeleton caved inward from external force.",
        "The uniform is mostly intact. Whatever came through the front did not stay.",
    ),
    (
        "Crushed against a sealed door — the hydraulics did not stop.",
        "The door is still closed. The frame is bent where the latch locked.",
    ),
    (
        "Neck injury — clinical, precise. The kind that takes training or absence of guilt.",
        "No other marks. Whatever did this was not in a hurry.",
    ),
    (
        "Electrical burn — something live and uninsulated in the dark.",
        "The hand terminal nearby is melted. It still shows the time of the burn.",
    ),
    (
        "Suffocation — no obvious wound. Which is worse than one.",
        "The face is calm. That is the worst part.",
    ),
    (
        "Hypothermia — frozen in a hiding place that eventually stopped working.",
        "Still in the same position. They waited a long time.",
    ),
    (
        "Penetration wound in the crawlspace — something found them before they found the exit.",
        "The crawl hatch behind them is still open.",
    ),
    (
        "Cause undetermined — MOTHER-LACUNA classifies it as a misplaced personnel event.",
        "The log entry stops mid-sentence and does not resume.",
    ),
    (
        "Blunt force — impact from above, possibly from the overhead cargo track.",
        "They were running. The footprints confirm it.",
    ),
    (
        "Corrosive compound exposure — the spatter pattern is from inside the room.",
        "Whatever was here got close enough to reach the ceiling.",
    ),
]

# --- Synthetic spawn data ---

SYNTHETIC_POOLS = {
    "maintenance": ["f02", "f04", "f05", "f08", "f09", "f12"],
    "medical": ["d03", "d05", "d08", "d11", "d12"],
    "security": ["b03", "b04", "b06", "g05", "g07"],
}

_SYNTHETICS = [
    {
        "pool": "maintenance",
        "name": "VOLST-1",
        "profile": "broken",
        "description": (
            "A maintenance synthetic stands in the corner, one arm locked at an angle "
            "that does not correspond to any task. Its optical array tracks the room. "
            "The name stenciled on its chest reads VOLST-1."
        ),
        "lines": [
            "  \"Maintenance cycle suspended. Reason: unresolvable conflict between\n"
            "   directive 4 and directive 4.\"\n"
            "   It does not clarify what directive 4 is.",
            "  \"Priority task: secure biological specimen.\"\n"
            "   Its arm locks tighter.\n"
            "  \"Priority task: secure biological specimen.\"\n"
            "   It says this the same way twice.",
            "  \"I have been here for nineteen days. This is consistent with protocol.\"\n"
            "   A pause.\n"
            "  \"Please advise if this is no longer protocol.\"",
        ],
    },
    {
        "pool": "medical",
        "name": "DRIN-4",
        "profile": "caretaker",
        "description": (
            "A medical synthetic sits upright beside a supply shelf, hands folded. "
            "Its uniform is spotless in a way that feels wrong given everything else. "
            "The badge reads DRIN-4, Medical Oversight."
        ),
        "lines": [
            "  \"Your stress indicators are elevated. This is understandable.\"\n"
            "   It does not offer anything else.",
            "  \"The quarantine is still active. I am not authorized to confirm what\n"
            "   the quarantine is for.\"\n"
            "   A small pause.\n"
            "  \"You look like you already know.\"",
            "  \"There are seventeen crew accounted for. I am not authorized\n"
            "   to discuss the other six.\"\n"
            "   It folds its hands again.",
        ],
    },
    {
        "pool": "security",
        "name": "FETH-7",
        "profile": "containment",
        "description": (
            "A security synthetic stands at the threshold of the room, facing outward. "
            "Its head turns toward you at an angle that is slightly too fast. "
            "The name on its collar reads FETH-7, Containment Unit."
        ),
        "lines": [
            "  \"You are not authorized to be in this sector.\"\n"
            "   It does not move.\n"
            "  \"I am noting your presence.\"",
            "  \"The organism learned the ventilation system on day three.\"\n"
            "   A long pause.\n"
            "  \"I am still learning it. This is embarrassing.\"",
            "  \"Your distress is acknowledged.\"\n"
            "   It watches you.\n"
            "  \"Please stop moving so I can determine whether this is permitted.\"",
        ],
    },
]


class GameState:
    def __init__(self):
        self.player: Player | None = None
        self.rooms: dict = {}
        self.current_room_id = "c09"
        self.game_phase = "exploring"

        self.monster = Monster()
        self.turn_count = 0

        # Sound system
        self.sound_level = "silent"
        self.last_action_sound = 0

        # Per-command control set by the parser
        self.advance = False
        self.quit_requested = False
        self.restart_requested = False

        self.flags = {
            "has_terminal": False,
            "monster_boarded": False,
            "generator_running": False,
            "radio_built": False,
            "ai_overridden": False,
            "warning_sent": False,
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
    # Spawn system
    # ------------------------------------------------------------------ #
    def spawn_random_entities(self):
        """Place 20 bodies and 3 synthetics randomly across the ship."""
        pool = [r for r in BODY_SPAWN_POOL if r in self.rooms]
        chosen = self.rng.sample(pool, min(20, len(pool)))
        names = self.rng.sample(CREW_NAMES, min(len(chosen), len(CREW_NAMES)))
        # Pad names if needed (more bodies than names).
        while len(names) < len(chosen):
            names.append(f"Crew Member {len(names) + 1}")

        for i, room_id in enumerate(chosen):
            name = names[i]
            cause_idx = self.rng.randrange(len(_DEATH_CAUSES))
            cause, detail = _DEATH_CAUSES[cause_idx]
            desc = (
                f"{name}.\n"
                f"{cause}\n"
                f"{detail}"
            )
            body = Item(
                name="body",
                aliases="body,corpse,dead,person,crew,remains",
                description=desc,
                portable=False,
            )
            self.rooms[room_id].items.append(body)

        # Place one synthetic per pool.
        for synth_data in _SYNTHETICS:
            pool_key = synth_data["pool"]
            candidates = [r for r in SYNTHETIC_POOLS[pool_key] if r in self.rooms]
            if not candidates:
                continue
            room_id = self.rng.choice(candidates)
            synth_item = Item(
                name=synth_data["name"],
                aliases=f"synthetic,android,unit,robot,{synth_data['name'].lower()}",
                description=synth_data["description"],
                portable=False,
            )
            synth_item.synthetic_data = {
                "profile": synth_data["profile"],
                "name": synth_data["name"],
                "lines": synth_data["lines"],
            }
            self.rooms[room_id].items.append(synth_item)

    # ------------------------------------------------------------------ #
    # Monster boarding
    # ------------------------------------------------------------------ #
    def board_monster(self, spawn_id="g11"):
        """Bring the monster aboard the ship at the given room."""
        m = self.monster
        m.active = True
        m.phase = "aboard"
        m.state = "searching"
        m.current_room_id = spawn_id
        m.tracked_room_id = spawn_id
        m.can_use_vents = True
        m.aggression = 1
        self.set_flag("monster_boarded", True)

    # ------------------------------------------------------------------ #
    # The turn pipeline
    # ------------------------------------------------------------------ #
    def advance_world(self):
        """Run one full turn of simulation after a time-advancing command.
        Returns a list of message lines to display."""
        assert self.player is not None, "advance_world called before new_game()"
        msgs = []
        self.turn_count += 1
        self.sound_level = SOUND_LABELS.get(self.last_action_sound, "silent")

        self.player.stayed_turns_in_room += 1

        # 1. Toxic atmosphere (no rooms are toxic in current layout — kept for safety)
        toxic_msg = self._resolve_toxic()
        if toxic_msg:
            msgs.append(toxic_msg)
        if self.death_state:
            return msgs

        # 2. Monster simulation
        if self.monster.active:
            self.monster.update_suspicion_decay()
            if self.monster.vent_cooldown > 0:
                self.monster.vent_cooldown -= 1
            self._apply_sound_to_monster()
            self._update_aggression()
            self._move_monster()
            self._update_scanner()
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

        if self.death_state:
            return msgs

        # 3. Occasional MOTHER-LACUNA ambient line
        molly = self._molly_ambient_line()
        if molly:
            msgs.append(molly)

        return msgs

    def _molly_ambient_line(self) -> str | None:
        if self.rng.random() > 0.12:
            return None
        pool = MOLLY_AMBIENT.get(self.game_phase) or MOLLY_AMBIENT["exploring"]
        return self.rng.choice(pool)

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
            if self.player.type == "synthetic":
                return "WARNING: corrosive atmosphere. Integrity falling.\nThis is survivable. Briefly."
            return "The air burns. Your eyes flood. There is no breathing this.\nGet sealed, or get inside."
        else:
            self.player.outside_exposure_turns = 0
        return None

    def _apply_sound_to_monster(self):
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

        if self.player.stayed_turns_in_room > 2 and not self.player.hidden:
            m.add_suspicion(proom, 1)

    def _update_aggression(self):
        assert self.player is not None
        m = self.monster
        if self.game_phase == "final_run":
            m.aggression = 3
        elif self.player.radio_component_count() >= 3:
            m.aggression = max(m.aggression, 2)
        else:
            m.aggression = max(m.aggression, 1)

    def _choose_target(self):
        m = self.monster
        # Endgame: once the AI is overridden, it camps the antenna.
        if self.game_phase == "final_run":
            m.state = "hunting"
            return "a07"
        if m.last_heard_room_id and m.turns_since_heard <= 2:
            m.state = "hunting"
            return m.last_heard_room_id
        hi = m.get_highest_suspicion_room()
        if hi:
            m.state = "investigating"
            return hi
        m.state = "searching"
        if m.known_hide_room and m.known_hide_room in self.rooms and self.rng.random() < 0.35:
            return m.known_hide_room
        if not m.target_room_id or m.target_room_id not in self.rooms or m.current_room_id == m.target_room_id:
            if self.rng.random() < 0.6:
                m.target_room_id = self._random_room_near(self.current_room_id, 3)
            else:
                m.target_room_id = self.rng.choice(list(self.rooms))
        return m.target_room_id

    def _random_room_near(self, center, maxd):
        pool = [rid for rid in self.rooms if rid != center and (self.shortest_path(center, rid)[0] or 99) <= maxd]
        return self.rng.choice(pool) if pool else self.rng.choice(list(self.rooms))

    def _move_monster(self):
        m = self.monster
        if m.is_distracted(self.turn_count):
            m.state = "feeding"
            return

        if m.current_room_id is None:
            return

        # Anti-camping: if alien waits in cryo vestibule while player is safe,
        # it eventually drifts away toward the main ship.
        if m.current_room_id in CRYO_VESTIBULE and self.current_room_id not in CRYO_VESTIBULE:
            m.cryo_camp_turns += 1
            if m.cryo_camp_turns >= 8:
                m.target_room_id = self._random_room_near("e05", 4)
                m.cryo_camp_turns = 0
        else:
            m.cryo_camp_turns = 0

        target = self._choose_target()
        if target is None:
            if self.rng.random() < 0.4:
                neighbors = [dest for _, dest in self._neighbors(m.current_room_id, use_vents=False)]
                if neighbors:
                    m.current_room_id = self.rng.choice(neighbors)
            return

        use_vents = m.can_use_vents and m.vent_cooldown == 0 and (m.aggression >= 2 or self.last_action_sound >= 3)
        if m.current_room_id != target:
            dist, first_dir = self.shortest_path(m.current_room_id, target, use_vents=use_vents)
            if first_dir is not None:
                self._step_monster(first_dir, use_vents)

    def _step_monster(self, direction, use_vents):
        m = self.monster
        if m.current_room_id is None:
            return
        room = self.rooms[m.current_room_id]
        if direction == "vent":
            for dest in room.vent_exits:
                m.current_room_id = dest
                m.used_vent_last_move = True
                m.vent_cooldown = 3
                return
        dest = room.exits.get(direction)
        if dest:
            dest_room = self.rooms.get(dest)
            if dest_room and not dest_room.monster_allowed:
                return
            m.current_room_id = dest

    def _maybe_telegraph(self):
        m = self.monster
        if m.current_room_id is None or m.current_room_id == self.current_room_id:
            return None
        dist, _ = self.shortest_path(self.current_room_id, m.current_room_id)
        if dist is None or dist > 2:
            return None
        if m.state == "hunting":
            pool, threshold = HUNT_SIGNS, 0.7
        else:
            pool, threshold = NEAR_SIGNS, 0.55
        if self.rng.random() < threshold:
            return self.rng.choice(pool)
        return None

    def _update_scanner(self):
        assert self.player is not None
        m = self.monster
        if self.current_room.scanner_interference or m.current_room_id is None:
            return
        dist, _ = self.shortest_path(self.current_room_id, m.current_room_id)
        fresh = 0.85
        if dist is not None and dist <= 1:
            fresh = 0.5
        if self.player.type == "synthetic":
            fresh = min(1.0, fresh + 0.15)
        if self.rng.random() < fresh:
            m.tracked_room_id = m.current_room_id

    def _resolve_same_room(self):
        assert self.player is not None
        m = self.monster
        if m.current_room_id != self.current_room_id:
            m.searching_streak = 0
            return None

        m.turns_since_seen = 0
        m.last_seen_room_id = self.current_room_id

        if m.is_distracted(self.turn_count):
            return "It is here — but its attention is elsewhere. Not yet."

        if not self.player.hidden:
            self.death_state = "monster"
            return None

        m.searching_streak += 1
        spot = self.player.hidden_spot or {"quality": 0, "reuse": 0}
        overstay = max(0, m.searching_streak - 1)
        chance = 10 + self.last_action_sound * 25 + overstay * 20 + spot.get("reuse", 0) * 8 - spot.get("quality", 0)
        chance = max(4, min(chance, 96))
        roll = self.rng.randint(1, 100)
        if roll <= chance:
            self.death_state = "monster"
            return None
        if m.known_hide_room == self.current_room_id:
            m.known_hide_room = None
        m.target_room_id = None
        if spot.get("reuse", 0) >= 2:
            return (
                f"It goes straight to the {spot['name']}. It is learning your habits.\n"
                "Its attention passes over you. This time."
            )
        return "It is in the room with you.\nIt checks the wrong place. Slowly. Then moves on."
