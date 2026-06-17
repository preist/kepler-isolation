#!/usr/bin/env python3
"""
KEPLER ISOLATION - a terminal survival-horror text adventure.

Run:  python3 src/__main__.py
"""

import sys
import os
import time
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_state import GameState, TOXIC_ROOMS
from player import Player
from parser import Parser
from map_builder import create_rooms

RULE = "-" * 60
WIDTH = 74

DEATH_TEXT = {
    "toxic": "",  # message already printed by the simulation
    "monster": {
        "human": "The room becomes very small.\n"
                 "You think of the face you meant to get back to. Then nothing.",
        "synthetic": "It finds you. There is no fear — only the order, satisfied at last,\n"
                     "and a final entry no one will read.",
        "contract_specialist": "No clause covers this. You almost laugh.\n"
                               "The contract was always going to be honoured this way.",
    },
}


class ThinAirGame:
    def __init__(self):
        self.gs = GameState()
        self.parser = Parser(self.gs)
        self.last_room_id = None
        # Typewriter pacing is for atmosphere only: skip it for --fast, when the
        # env var is set, or when input/output isn't a real terminal (piped runs,
        # tests). That keeps scripted play and CI snappy and clean.
        fast_flag = "--fast" in sys.argv or os.environ.get("KEPLER_FAST")
        self.interactive = sys.stdin.isatty() and sys.stdout.isatty()
        self.paced = self.interactive and not fast_flag
        # Color is on for a real terminal by default; --color forces it,
        # --no-color / NO_COLOR turn it off. Restrained palette only.
        self.color = "--color" in sys.argv or (
            sys.stdout.isatty()
            and "--no-color" not in sys.argv
            and not os.environ.get("NO_COLOR"))

    def c(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.color else text

    # ------------------------------------------------------------------ #
    # Output helpers
    # ------------------------------------------------------------------ #
    def wrap(self, text: str) -> str:
        """Wrap prose to WIDTH while preserving deliberate line breaks."""
        out = []
        for line in text.split("\n"):
            out.append("\n".join(textwrap.wrap(line, WIDTH)) if line.strip() else "")
        return "\n".join(out)

    def say(self, text: str, slow: bool = False):
        """Print a line, optionally with a typewriter cadence for big beats."""
        if not (slow and self.paced):
            print(text)
            return
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(0.018)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def beat(self):
        """A held breath before a major moment — only when interactive."""
        if self.paced:
            try:
                input()
            except (KeyboardInterrupt, EOFError):
                pass

    # ------------------------------------------------------------------ #
    def start(self):
        self.intro()
        self.create_character()
        self.setup_world()
        self.main_loop()

    def intro(self):
        print()
        print("K E P L E R   I S O L A T I O N")
        print(RULE)
        print("Survey lander LANTERN-9, grounded on LV-1187. They called it Kepler's Rest.")
        print("Contract holder: Halloway-Tanaka Industries.")
        print()
        print("You wake on the ground. You do not remember the landing.")
        print()
        print("  Landing complete.")
        print("  Atmosphere: lethal.")
        print("  Signal source: local. Origin: below.")
        print("  Crew status: one.")
        print("  Crew status (revised): one.")
        print()
        print("A signal is coming up through the rock. It is old. It has not degraded,")
        print("and that should not be possible. The contract calls it a rescue.")
        print("The contract calls you recoverable.")
        print(RULE)
        print()

    # Fixed personnel — one face per role. (All male, per the manifest.)
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

    def create_character(self):
        print("HALLOWAY-TANAKA PERSONNEL — assign role:")
        print("  1. Crew        — Elias Cole")
        print("  2. Synthetic   — Jonah")
        print("  3. Contractor  — Rourke Dunmore")
        choice = input("> ").strip()
        name, ptype = self.ROLES.get(choice, self.ROLES["1"])
        self.gs.player = Player(name, "male", ptype)
        label = ptype.replace("_", " ").title()
        print(f"\n{name}. {label}.")
        print(self.ROLE_FLAVOR[ptype])
        print("The manifest lists him, and no one else.")
        print("\nType 'help' at any time.\n")

    def setup_world(self):
        self.gs.rooms = create_rooms()
        self.gs.current_room_id = "cockpit"
        self.gs.rooms["cockpit"].visited = True
        self.gs.visited_rooms.add("cockpit")
        self.gs.game_phase = "pre_cave"

    # ------------------------------------------------------------------ #
    def motion_summary(self):
        """Short scanner readout for the status line, if the player has a terminal."""
        if not self.gs.player.has_terminal:
            return None
        m = self.gs.monster
        if not m.active:
            return "outside" if self.gs.get_flag("cave_triggered") else "none"
        if self.gs.current_room.scanner_interference:
            return "interference"
        if m.turns_since_seen <= 1:
            return "SEEN"
        tracked = m.tracked_room_id or m.current_room_id
        if tracked == self.gs.current_room_id:
            return "HERE"
        dist, direction = self.gs.shortest_path(self.gs.current_room_id, tracked)
        if dist is None:
            return "lost"
        return f"{direction} {dist}"

    def status_line(self):
        room = self.gs.current_room
        suit = "worn" if self.gs.player.suit_worn else "none"

        sound = self.gs.sound_level
        sound_code = {"audible": "33", "loud": "31", "violent": "1;31"}.get(sound, "2")
        suit_code = "31" if (suit == "none" and room.toxic) else "2"

        parts = [f"{self.c('Location:', '2')} {room.name}",
                 f"{self.c('Sound:', '2')} {self.c(sound, sound_code)}",
                 f"{self.c('Suit:', '2')} {self.c(suit, suit_code)}"]

        motion = self.motion_summary()
        if motion is not None:
            if motion in ("SEEN", "HERE"):
                code = "1;31"
            elif motion in ("interference", "lost", "outside", "none"):
                code = "2"
            elif motion[-1:].isdigit() and int(motion.split()[-1]) <= 2:
                code = "31"
            else:
                code = "33"
            parts.append(f"{self.c('Motion:', '2')} {self.c(motion, code)}")
        return self.c(" | ", "2").join(parts)

    def render_room(self):
        room = self.gs.current_room
        print()
        print(self.status_line())
        print()
        print(self.wrap(room.describe(self.gs)))
        print()
        print(self.c("Exits:", "2") + " " + (", ".join(room.exits.keys()) if room.exits else "none"))
        if room.items:
            print(self.c("Items:", "2") + " " + ", ".join(i.name for i in room.items))
        self.last_room_id = self.gs.current_room_id

    # ------------------------------------------------------------------ #
    def main_loop(self):
        self.render_room()
        while True:
            try:
                command = input("\n> ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye.")
                return

            if not command:
                continue

            before_room = self.gs.current_room_id
            result = self.parser.parse_command(command)
            if result:
                print("\n" + result)

            if self.gs.quit_requested:
                return
            if self.gs.restart_requested:
                self.restart()
                return

            # Sending the warning wins outright — you can't be killed on the
            # keystroke that saves everyone. So resolve the win before the world.
            if self.gs.win_state:
                self.show_ending()
                if self.prompt_again():
                    self.restart()
                return

            if self.gs.advance:
                was_aboard = self.gs.get_flag("monster_boarded")
                for msg in self.gs.advance_world():
                    print("\n" + msg)
                # The moment it comes aboard earns a held breath.
                if self.gs.get_flag("monster_boarded") and not was_aboard:
                    self.beat()

            if self.gs.death_state:
                self.handle_death()
                if self.prompt_again():
                    self.restart()
                return
            if self.gs.win_state:
                self.show_ending()
                if self.prompt_again():
                    self.restart()
                return

            # Re-render the full room after a move or a look; otherwise just status.
            if self.gs.current_room_id != before_room or command.lower() in ("look", "l"):
                self.render_room()
            else:
                print("\n" + self.status_line())

    # ------------------------------------------------------------------ #
    def handle_death(self):
        print()
        print(RULE)
        if self.gs.death_state == "monster":
            text = DEATH_TEXT["monster"].get(self.gs.player.type, DEATH_TEXT["monster"]["human"])
            self.say(self.c(text, "31"), slow=True)
        elif self.gs.death_state == "toxic":
            pass  # already printed by the simulation
        print(RULE)
        print(self.c("\nYou died.", "1;31"))

    def show_ending(self):
        self.beat()
        print()
        print(RULE)
        self.say(self.c("TRANSMISSION SENT.", "1;36"), slow=True)
        print()
        self.say(self.c("> DO NOT COME HERE.", "1;36"), slow=True)
        print()
        print("HALLOWAY-TANAKA RELAY STATION")
        print("SEVENTEEN DAYS LATER")
        print()
        for line in ('  "Play it again."',
                     '  "Do not come here."',
                     '  "We have this voice on file. Older transmission. Same rock."',
                     '  "Then it confirms the site is viable for the asset."',
                     '  "Survivors?"',
                     '  "The crew is a rounding error. We want what they found."',
                     '  "Is it intelligent?"',
                     '  "It learned our beacon and aimed it back at us. Yes."'):
            self.say(line, slow=True)
        print()
        print("  A pause. Someone pours coffee.")
        print()
        self.say('  "Wake the recovery team. Quietly."', slow=True)
        print()
        self.say("LV-1187 is reclassified: priority acquisition.", slow=True)
        print()
        self.say(self.c("They are not warned.", "1;36"), slow=True)
        self.say(self.c("They are invited.", "1;36"), slow=True)
        print(RULE)
        print("\nThe warning was sent. That was the mistake.")

    def prompt_again(self):
        try:
            choice = input("\nrestart / quit > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return False
        return choice.startswith("r")

    def restart(self):
        game = ThinAirGame()
        # Keep the same character to skip re-creation.
        game.gs.player = Player(self.gs.player.name, self.gs.player.gender, self.gs.player.type)
        game.parser = Parser(game.gs)
        game.setup_world()
        print("\n" + RULE)
        print("The descent sedation lifts. Again.")
        print(RULE)
        game.main_loop()


USAGE = """KEPLER ISOLATION — a terminal survival-horror text adventure.

  You land on a toxic planet, explore a cave, and come back with a passenger.
  Reach Communications, repair the transmitter, and send the warning.

Usage:
  ./play [options]          (or: python3 src/__main__.py [options])

Options:
  --fast        Skip the typewriter pacing on dramatic beats.
  --color       Force ANSI color (on by default for a terminal).
  --no-color    Disable color. (NO_COLOR is also respected.)
  -h, --help    Show this help and exit.

In-game, type 'help' for the command list."""


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(USAGE)
        return
    ThinAirGame().start()


if __name__ == "__main__":
    main()
