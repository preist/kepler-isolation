"""
GameEngine — the UI-agnostic façade for KEPLER ISOLATION.

Both front-ends (the classic print/input loop and the Textual TUI) drive the
game through this one object: feed it a command with submit(), read back a
TurnResult, and pull panel data from the accessors. All shared player-facing
text (intro body, role flavor, death lines, the ending) lives here so the two
front-ends can never drift apart — each only decides how to *frame* it.
"""

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_state import GameState
from item import Item
from map_builder import create_rooms
from parser import Parser
from player import Player

# --- Shared content (single source of truth for both front-ends) ---

ROLES = {
    "1": ("Mara Vale", "crew"),
    "2": ("Valdorf", "synthetic"),
    "3": ("Jonah Rusk", "contractor"),
}
ROLE_GENDERS = {
    "crew": "female",
    "synthetic": "neutral",
    "contractor": "male",
}
ROLE_FLAVOR = {
    "crew": "You know the ship's routines. Or you thought you did.\nThe dead are not strangers.",
    "synthetic": "Your revival log shows a gap. Eleven hours, unrecorded.\nThe other synthetics may know what happened before you do.",
    "contractor": "You were stored until you were needed.\nYou are alive partly because no one remembered you were here.\nThat should sting.",
}

DEATH_TEXT = {
    "crew": "You know this doorframe. You walked through it every morning.\nThe ship remembers. You do not.",
    "synthetic": "Final diagnostic runs in the dark. No order saves you.\nThe last entry writes itself and sends nowhere.",
    "contractor": "Your contract did not say survive.\nIt did not forbid it either.",
}

# The ordered roster of all three characters.  When building the queue we put
# the chosen character first; the remaining two follow in this fixed order.
_ALL_CHARACTERS = [
    {"name": "Mara Vale", "type": "crew", "gender": "female"},
    {"name": "Valdorf", "type": "synthetic", "gender": "neutral"},
    {"name": "Jonah Rusk", "type": "contractor", "gender": "male"},
]

_DEATH_EPITAPH = {
    "crew": "Listed by MOTHER-LACUNA as a misplaced personnel event.",
    "synthetic": "Final diagnostic filed. No response to ping.",
    "contractor": "The contract did not cover this.",
}

_POD_LABEL = {
    "crew": "MARA VALE — CREW",
    "synthetic": "VALDORF — UNIT 7 — SYNTHETIC",
    "contractor": "JONAH RUSK — CONTRACTOR",
}


def _build_char_queue(role_choice: str) -> list:
    idx = {"1": 0, "2": 1, "3": 2}.get(role_choice, 0)
    chosen = _ALL_CHARACTERS[idx]
    rest = [c for c in _ALL_CHARACTERS if c is not chosen]
    return [chosen] + rest


INTRO_BODY = [
    "USCSS Nightglass. Commercial research vessel.",
    "Survey mission, Kepler-186f-Lacuna. Contract holder: Halloway-Tanaka Industries.",
    "",
    "You wake before the pod finishes opening.",
    "For a moment you are nowhere — no name, no ship.",
    "Only cold glass and the sound of your own breathing.",
    "",
    "The lid releases. Blue emergency light fills the cryo bay.",
    "Five other pods stand closed. One is empty. One is cracked from the inside.",
    "",
    "  Good morning.",
    "",
    "The pause after that is too long.",
    "",
    "  Your revival was not scheduled. Please remain calm.",
    "  There are currently no medical personnel available to assist you.",
    "  This is not optimal.",
    "",
    "On the monitoring desk, a cracked hand terminal blinks awake.",
    "Far away — deep in the aft ship — something moves.",
    "",
    "The cave below the planet has already been explored.",
    "The mistake has already been made.",
]

# The ending, as content the front-ends frame however they like.
ENDING_TRANSMISSION = "TRANSMISSION SENT."
ENDING_WARNING = "> DO NOT BOARD. DO NOT RECOVER SAMPLES."
ENDING_HEADER = ["HALLOWAY-TANAKA RELAY STATION", "SEVENTEEN DAYS LATER"]
ENDING_DIALOGUE = [
    '  "Play it again."',
    '  "Do not board. Do not recover samples."',
    '  "We have the vessel on file. USCSS Nightglass. Declared lost."',
    '  "The crew is a rounding error. We want what the Nightglass found."',
    '  "Survivors?"',
    '  "One transmission. One voice. That is all."',
    '  "Is it intelligent?"',
    '  "It learned our signal protocols and aimed them back at us. Yes."',
]
ENDING_PAUSE = "  A pause. Someone checks a manifest."
ENDING_WAKE = '  "Wake the recovery team. Full containment kit. Quietly."'
ENDING_RECLASSIFIED = "The Nightglass is reclassified: priority acquisition."
ENDING_INVITED = ["They are not warned.", "They are invited."]
ENDING_MISTAKE = "The warning was sent. That was the mistake."


@dataclass
class TurnResult:
    """What one submitted command produced."""

    lines: list[str] = field(default_factory=list)
    advanced: bool = False
    room_changed: bool = False
    boarded_now: bool = False  # the creature came aboard on this turn
    dead: str | None = None  # death cause, or None (final death — no lives left)
    next_life: bool = False  # a character died but the next one just woke up
    won: bool = False
    quit: bool = False
    restart: bool = False


class GameEngine:
    def __init__(self):
        self.gs = GameState()
        self.parser = Parser(self.gs)

    # ------------------------------------------------------------------ #
    def new_game(self, role_choice="1", player=None):
        """Start a fresh game."""
        if player is None:
            name, ptype = ROLES.get(role_choice, ROLES["1"])
            gender = ROLE_GENDERS.get(ptype, "neutral")
            player = Player(name, gender, ptype)
        self.gs.player = player
        self.gs.rooms = create_rooms()
        self.gs.current_room_id = "c09"
        self.gs.rooms["c09"].visited = True
        self.gs.visited_rooms = {"c09"}
        self.gs.game_phase = "exploring"
        self.gs.death_state = None
        self.gs.win_state = False
        self.gs.turn_count = 0
        self.gs.sound_level = "silent"
        self.gs.last_action_sound = 0
        self.gs.advance = False
        self.gs.flags = {
            "has_terminal": False,
            "monster_boarded": False,
            "generator_running": False,
            "radio_built": False,
            "ai_overridden": False,
            "warning_sent": False,
        }
        # Three-life queue always rebuilt fresh on new_game.
        self.gs.character_queue = _build_char_queue(role_choice)
        self.gs.lives_used = 0
        # Monster starts active at the aft of the ship (full state reset).
        self.gs.board_monster("g11")
        # Scatter bodies and synthetics across the ship.
        self.gs.spawn_random_entities()
        return player

    def sleeping_pod_text(self) -> str:
        """One-time flavour shown just after role selection: the other pods."""
        sleeping = self.gs.character_queue[1:]
        if not sleeping:
            return ""
        labels = "\n".join(f"  {_POD_LABEL[c['type']]}" for c in sleeping)
        return (
            f"Two pods beside yours are sealed.\n"
            f"Frost on the glass. Labels visible:\n"
            f"{labels}\n"
            f"They do not know what you are waking into."
        )

    @property
    def lives_left(self) -> int:
        """Characters still available, including the current one."""
        return max(len(self.gs.character_queue), 0)

    def submit(self, command: str) -> TurnResult:
        """Run one command through the same pipeline the classic loop used:
        parse → (win short-circuits the world) → advance → resolve."""
        gs = self.gs
        before = gs.current_room_id
        was_aboard = gs.get_flag("monster_boarded")

        text = self.parser.parse_command(command)
        lines = [text] if text else []

        if gs.quit_requested:
            return TurnResult(lines, quit=True)
        if gs.restart_requested:
            return TurnResult(lines, restart=True)
        # Sending the warning wins outright — never resolve the world on that turn.
        if gs.win_state:
            return TurnResult(lines, won=True)

        advanced = gs.advance
        if advanced:
            lines += gs.advance_world()
        boarded_now = gs.get_flag("monster_boarded") and not was_aboard

        if gs.death_state:
            if len(gs.character_queue) > 1:
                next_lines = self._transition_to_next_life(lines)
                return TurnResult(next_lines, advanced=advanced, next_life=True, boarded_now=boarded_now)
            return TurnResult(lines, advanced=advanced, dead=gs.death_state, boarded_now=boarded_now)
        if gs.win_state:
            return TurnResult(lines, advanced=advanced, won=True, boarded_now=boarded_now)
        return TurnResult(
            lines, advanced=advanced, room_changed=(gs.current_room_id != before), boarded_now=boarded_now
        )

    # ------------------------------------------------------------------ #
    def _transition_to_next_life(self, death_lines: list[str]) -> list[str]:
        """Record the dead player, wake the next character, return narrative."""
        gs = self.gs
        prev = gs.character_queue[0]
        next_char = gs.character_queue[1]

        # Drop all inventory to the death room so the next player can find it.
        death_room_id = gs.current_room_id
        death_room = gs.rooms[death_room_id]
        death_room_name = death_room.name
        if gs.player is not None:
            for item in list(gs.player.inventory):
                death_room.items.append(item)
            for item in list(gs.player.worn_items):
                item.worn = False
                death_room.items.append(item)
            gs.player.inventory.clear()
            gs.player.worn_items.clear()

        # Leave a body so the next player knows where they fell.
        alias_name = prev["name"].lower().replace(" ", ",")
        epitaph = _DEATH_EPITAPH.get(prev["type"], "")
        predecessor_body = Item(
            name="body",
            aliases=f"body,corpse,predecessor,{alias_name},remains",
            description=(f"{prev['name']}.\n{epitaph}\nThey made it as far as {death_room_name}."),
            portable=False,
        )
        death_room.items.append(predecessor_body)

        # Advance the queue, reset world-state for the new player.
        gs.character_queue.pop(0)
        gs.lives_used += 1
        gs.death_state = None
        gs.advance = False

        new_player = Player(next_char["name"], next_char["gender"], next_char["type"])
        gs.player = new_player  # parser reads player via gs, so no parser update needed
        gs.current_room_id = "c09"

        # Build the transition narrative.
        remaining = gs.character_queue[1:]  # still sleeping after this wake
        life_num = gs.lives_used + 1  # e.g. 2 of 3
        divider = "─" * 58

        # Monster status — world state is preserved; cryo section is sealed.
        m = gs.monster
        if m.active and m.current_room_id:
            mroom = gs.rooms.get(m.current_room_id)
            monster_note = (
                f"The organism is still aboard. Last confirmed position: {mroom.name if mroom else 'unknown'}."
            )
        else:
            monster_note = "The organism is still aboard."

        lines = death_lines + [
            "",
            divider,
            "",
            f"{prev['name']} is dead.",
            epitaph,
            "",
            "The cryo system registers the absence.",
            "Another pod opens in Bay Alpha.",
            "",
            "  Good morning.",
            "  Your revival was not scheduled.",
            (
                f"  There is {len(remaining)} other occupant in cryo."
                if len(remaining) == 1
                else f"  There are {len(remaining)} other occupants in cryo."
                if remaining
                else "  You are the last."
            ),
            "",
            ROLE_FLAVOR[next_char["type"]],
            "",
            f"You are {next_char['name']}.",
            "",
            monster_note,
            "The cryo section is sealed. It cannot follow you here.",
            "",
            f"Somewhere on this ship — in {death_room_name} —",
            f"there is a body that answers to {prev['name']}.",
            "Everything they were carrying is there.",
            "",
            divider,
            f"[Life {life_num} of 3]",
        ]
        return lines

    # --- Panel / status accessors -------------------------------------- #
    @property
    def player(self) -> Player:
        assert self.gs.player is not None, "engine.player accessed before new_game()"
        return self.gs.player

    @property
    def location_name(self) -> str:
        return self.gs.current_room.name

    def room_text(self) -> str:
        return self.gs.current_room.describe(self.gs)

    @property
    def exits(self) -> list[str]:
        return list(self.gs.current_room.exits.keys())

    @property
    def room_items(self) -> list[str]:
        return [i.name for i in self.gs.current_room.items]

    @property
    def inventory(self) -> list[str]:
        p = self.player
        return [i.name for i in p.inventory] + [f"{i.name} (worn)" for i in p.worn_items]

    @property
    def sound_level(self) -> str:
        return self.gs.sound_level

    @property
    def suit_status(self) -> str:
        return "worn" if self.player.suit_worn else "none"

    @property
    def turn_count(self) -> int:
        return self.gs.turn_count

    @property
    def phase(self) -> str:
        return self.gs.game_phase

    @property
    def has_terminal(self) -> bool:
        return self.player.has_terminal

    @property
    def toxic_here(self) -> bool:
        return self.gs.current_room.toxic

    def death_text(self) -> str:
        ptype = self.gs.player.type if self.gs.player else "crew"
        return DEATH_TEXT.get(ptype, DEATH_TEXT["crew"])

    def motion(self) -> dict:
        """Structured scanner reading (front-ends decide how to show it).
        kind ∈ no_device | none | interference | seen | here | lost | bearing."""
        gs = self.gs
        if not self.player.has_terminal:
            return {"kind": "no_device"}
        m = gs.monster
        if not m.active:
            return {"kind": "none"}
        if gs.current_room.scanner_interference:
            return {"kind": "interference"}
        if m.turns_since_seen <= 1:
            return {"kind": "seen"}
        tracked = m.tracked_room_id or m.current_room_id
        if tracked is None:
            return {"kind": "lost"}
        if tracked == gs.current_room_id:
            return {"kind": "here"}
        dist, _ = gs.shortest_path(gs.current_room_id, tracked)
        if dist is None:
            return {"kind": "lost"}
        # Intercardinal compass (NE/SW etc.) from two-hop lookahead.
        direction = gs.compass_direction(gs.current_room_id, tracked)
        meters = dist * 15
        confidence = max(20, min(90, 90 - dist * 8))
        if self.player.type == "synthetic":
            confidence = min(95, confidence + 10)
        motion_desc = {
            "feeding": "still",
            "searching": "slow",
            "investigating": "irregular",
            "hunting": "rapid",
        }.get(m.state, "slow")
        return {
            "kind": "bearing",
            "direction": direction,
            "meters": meters,
            "confidence": confidence,
            "motion_desc": motion_desc,
        }


# Compact abbreviations for every compass string the scanner can return.
_COMPASS_ABBR: dict[str, str] = {
    "north": "N",
    "south": "S",
    "east": "E",
    "west": "W",
    "northeast": "NE",
    "northwest": "NW",
    "southeast": "SE",
    "southwest": "SW",
    "up": "UP",
    "down": "DN",
    "in": "IN",
    "out": "OUT",
}


def motion_label(m: dict) -> str | None:
    """Collapse a motion() dict into a one-line status string for the classic
    status bar, or None when there is no device."""
    kind = m["kind"]
    if kind == "no_device":
        return None
    if kind == "seen":
        return "SEEN"
    if kind == "here":
        return "HERE"
    if kind == "bearing":
        abbr = _COMPASS_ABBR.get(m.get("direction") or "", "?")
        return f"{abbr} ~{m['meters']}m"
    return kind  # none / interference / lost
