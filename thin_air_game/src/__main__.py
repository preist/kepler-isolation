#!/usr/bin/env python3
"""
THE THIN AIR - a terminal survival-horror text adventure.

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
        "human": "The room becomes very small.\nThen it is over.",
        "synthetic": "It finds you. There is no fear to feel.\nOnly the end of input.",
        "contract_specialist": "The handbook did not cover this.\nNothing does, now.",
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
        fast_flag = "--fast" in sys.argv or os.environ.get("THIN_AIR_FAST")
        self.interactive = sys.stdin.isatty() and sys.stdout.isatty()
        self.paced = self.interactive and not fast_flag

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
        print("T H E   T H I N   A I R")
        print(RULE)
        print("Survey lander LANTERN-9. Contract: Farland-Guttenber Recovery & Survey.")
        print()
        print("Landing complete.")
        print("Atmosphere: lethal.")
        print("Signal source: local.")
        print("Crew status: one.")
        print(RULE)
        print()

    def create_character(self):
        name = input("Name? > ").strip() or "Crew"
        gender = input("Gender? > ").strip() or "unspecified"
        print("Type?")
        print("  1. Human crewmember")
        print("  2. Synthetic")
        print("  3. Contract specialist")
        choice = input("> ").strip()
        ptype = {"2": "synthetic", "3": "contract_specialist"}.get(choice, "human")
        self.gs.player = Player(name, gender, ptype)
        label = ptype.replace("_", " ")
        print(f"\nWelcome aboard, {name}. ({label})")
        print("Type 'help' at any time.\n")

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
        parts = [f"Location: {room.name}",
                 f"Sound: {self.gs.sound_level}",
                 f"Suit: {suit}"]
        motion = self.motion_summary()
        if motion is not None:
            parts.append(f"Motion: {motion}")
        return " | ".join(parts)

    def render_room(self):
        room = self.gs.current_room
        print()
        print(self.status_line())
        print()
        print(self.wrap(room.describe(self.gs)))
        print()
        print("Exits: " + (", ".join(room.exits.keys()) if room.exits else "none"))
        if room.items:
            print("Items: " + ", ".join(i.name for i in room.items))
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
            self.say(text, slow=True)
        elif self.gs.death_state == "toxic":
            pass  # already printed by the simulation
        print(RULE)
        print("\nYou died.")

    def show_ending(self):
        self.beat()
        print()
        print(RULE)
        self.say("TRANSMISSION SENT.", slow=True)
        print()
        self.say("> DO NOT COME HERE.", slow=True)
        print()
        print("FARLAND-GUTTENBER RELAY STATION")
        print("SEVENTEEN DAYS LATER")
        print()
        for line in ('  "Play it again."',
                     '  "Do not come here."',
                     '  "Was there contact?"',
                     '  "Yes."',
                     '  "Hostile?"',
                     '  "Intelligent."'):
            self.say(line, slow=True)
        print()
        print("  A pause.")
        print()
        self.say('  "Wake Survey Team One."', slow=True)
        print()
        self.say("LV-417c is upgraded to priority recovery.", slow=True)
        print(RULE)
        print("\nYou won. They are coming anyway.")

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


def main():
    ThinAirGame().start()


if __name__ == "__main__":
    main()
