"""
GameEngine — the UI-agnostic façade for KEPLER ISOLATION.

Both front-ends (the classic print/input loop and the Textual TUI) drive the
game through this one object: feed it a command with submit(), read back a
TurnResult, and pull panel data from the accessors. All shared player-facing
text (intro body, role flavor, death lines, the ending) lives here so the two
front-ends can never drift apart — each only decides how to *frame* it.
"""

import sys
import os
from dataclasses import dataclass, field
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_state import GameState
from player import Player
from parser import Parser
from map_builder import create_rooms

# --- Shared content (single source of truth for both front-ends) ---

ROLES = {
    "1": ("Elias Cole", "human"),
    "2": ("Jonah", "synthetic"),
    "3": ("Rourke Dunmore", "contract_specialist"),
}
ROLE_FLAVOR = {
    "human": "You signed for the hazard pay. There is a face you mean to get back to.",
    "synthetic": "The company's standing order sits in you, quiet. You decide, once\nmore, to ignore it.",
    "contract_specialist": "You have read enough Halloway-Tanaka paper to know exactly what\n'recoverable' means.",
}

DEATH_TEXT = {
    "human": "The room becomes very small.\n"
             "You think of the face you meant to get back to. Then nothing.",
    "synthetic": "It finds you. There is no fear — only the order, satisfied at last,\n"
                 "and a final entry no one will read.",
    "contract_specialist": "No clause covers this. You almost laugh.\n"
                           "The contract was always going to be honoured this way.",
}

INTRO_BODY = [
    "Survey lander LANTERN-9, grounded on LV-1187. They called it Kepler's Rest.",
    "Contract holder: Halloway-Tanaka Industries.",
    "",
    "You wake on the ground. You do not remember the landing.",
    "",
    "  Landing complete.",
    "  Atmosphere: lethal.",
    "  Signal source: local. Origin: below.",
    "  Crew status: one.",
    "  Crew status (revised): one.",
    "",
    "A signal is coming up through the rock. It is old. It has not degraded,",
    "and that should not be possible. The contract calls it a rescue.",
    "The contract calls you recoverable.",
]

# The ending, as content the front-ends frame however they like.
ENDING_TRANSMISSION = "TRANSMISSION SENT."
ENDING_WARNING = "> DO NOT COME HERE."
ENDING_HEADER = ["HALLOWAY-TANAKA RELAY STATION", "SEVENTEEN DAYS LATER"]
ENDING_DIALOGUE = [
    '  "Play it again."',
    '  "Do not come here."',
    '  "We have this voice on file. Older transmission. Same rock."',
    '  "Then it confirms the site is viable for the asset."',
    '  "Survivors?"',
    '  "The crew is a rounding error. We want what they found."',
    '  "Is it intelligent?"',
    '  "It learned our beacon and aimed it back at us. Yes."',
]
ENDING_PAUSE = "  A pause. Someone pours coffee."
ENDING_WAKE = '  "Wake the recovery team. Quietly."'
ENDING_RECLASSIFIED = "LV-1187 is reclassified: priority acquisition."
ENDING_INVITED = ["They are not warned.", "They are invited."]
ENDING_MISTAKE = "The warning was sent. That was the mistake."


@dataclass
class TurnResult:
    """What one submitted command produced."""
    lines: List[str] = field(default_factory=list)
    advanced: bool = False
    room_changed: bool = False
    boarded_now: bool = False     # the creature came aboard on this turn
    dead: Optional[str] = None    # death cause, or None
    won: bool = False
    quit: bool = False
    restart: bool = False


class GameEngine:
    def __init__(self):
        self.gs = GameState()
        self.parser = Parser(self.gs)

    # ------------------------------------------------------------------ #
    def new_game(self, role_choice="1", player=None):
        """Start a fresh game. Pass an existing player to keep them across a
        restart (skips re-selecting a role)."""
        if player is None:
            name, ptype = ROLES.get(role_choice, ROLES["1"])
            player = Player(name, "male", ptype)
        self.gs.player = player
        self.gs.rooms = create_rooms()
        self.gs.current_room_id = "cockpit"
        self.gs.rooms["cockpit"].visited = True
        self.gs.visited_rooms.add("cockpit")
        self.gs.game_phase = "pre_cave"
        return player

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
            return TurnResult(lines, advanced=advanced, dead=gs.death_state,
                              boarded_now=boarded_now)
        if gs.win_state:
            return TurnResult(lines, advanced=advanced, won=True,
                              boarded_now=boarded_now)
        return TurnResult(lines, advanced=advanced,
                          room_changed=(gs.current_room_id != before),
                          boarded_now=boarded_now)

    # --- Panel / status accessors -------------------------------------- #
    @property
    def player(self):
        return self.gs.player

    @property
    def location_name(self) -> str:
        return self.gs.current_room.name

    def room_text(self) -> str:
        return self.gs.current_room.describe(self.gs)

    @property
    def exits(self) -> List[str]:
        return list(self.gs.current_room.exits.keys())

    @property
    def room_items(self) -> List[str]:
        return [i.name for i in self.gs.current_room.items]

    @property
    def inventory(self) -> List[str]:
        return ([i.name for i in self.gs.player.inventory]
                + [f"{i.name} (worn)" for i in self.gs.player.worn_items])

    @property
    def sound_level(self) -> str:
        return self.gs.sound_level

    @property
    def suit_status(self) -> str:
        return "worn" if self.gs.player.suit_worn else "none"

    @property
    def turn_count(self) -> int:
        return self.gs.turn_count

    @property
    def phase(self) -> str:
        return self.gs.game_phase

    @property
    def has_terminal(self) -> bool:
        return self.gs.player.has_terminal

    @property
    def toxic_here(self) -> bool:
        return self.gs.current_room.toxic

    def death_text(self) -> str:
        ptype = self.gs.player.type if self.gs.player else "human"
        return DEATH_TEXT.get(ptype, DEATH_TEXT["human"])

    def motion(self) -> dict:
        """Structured scanner reading (front-ends decide how to show it).
        kind ∈ no_device | none | outside | interference | seen | here | lost | bearing."""
        gs = self.gs
        if not gs.player.has_terminal:
            return {"kind": "no_device"}
        m = gs.monster
        if not m.active:
            return {"kind": "outside" if gs.get_flag("cave_triggered") else "none"}
        if gs.current_room.scanner_interference:
            return {"kind": "interference"}
        if m.turns_since_seen <= 1:
            return {"kind": "seen"}
        tracked = m.tracked_room_id or m.current_room_id
        if tracked == gs.current_room_id:
            return {"kind": "here"}
        dist, direction = gs.shortest_path(gs.current_room_id, tracked)
        if dist is None:
            return {"kind": "lost"}
        return {"kind": "bearing", "direction": direction, "distance": dist}


def motion_label(m: dict) -> Optional[str]:
    """Collapse a motion() dict into the legacy one-line status string
    ('none' / 'outside' / 'interference' / 'SEEN' / 'HERE' / 'lost' /
    '<dir> <dist>'), or None when there is no device."""
    kind = m["kind"]
    if kind == "no_device":
        return None
    if kind == "seen":
        return "SEEN"
    if kind == "here":
        return "HERE"
    if kind == "bearing":
        return f"{m['direction']} {m['distance']}"
    return kind  # none / outside / interference / lost
