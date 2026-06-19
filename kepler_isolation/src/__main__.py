#!/usr/bin/env python3
"""
KEPLER ISOLATION — a terminal survival-horror text adventure.

Run:  python3 src/__main__.py           (classic text mode, zero dependencies)
      python3 src/__main__.py --tui      (rich Textual UI; needs `pip install textual`)

This file is the classic plain print/input front-end. The game logic lives in
GameEngine (engine.py); both this and the Textual UI (tui.py) drive that.
"""

import os
import sys
import textwrap
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import leaderboard as lb
from engine import (
    ENDING_DIALOGUE,
    ENDING_HEADER,
    ENDING_INVITED,
    ENDING_MISTAKE,
    ENDING_PAUSE,
    ENDING_RECLASSIFIED,
    ENDING_TRANSMISSION,
    ENDING_WAKE,
    ENDING_WARNING,
    INTRO_BODY,
    ROLE_FLAVOR,
    GameEngine,
    motion_label,
)
from player import Player

RULE = "-" * 60
WIDTH = 74


class ClassicGame:
    """The plain terminal front-end, driven by GameEngine."""

    def __init__(self):
        self.engine = GameEngine()
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
            sys.stdout.isatty() and "--no-color" not in sys.argv and not os.environ.get("NO_COLOR")
        )

    @property
    def gs(self):
        return self.engine.gs

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
        self.main_loop()

    def intro(self):
        print()
        print("K E P L E R   I S O L A T I O N")
        print(RULE)
        for line in INTRO_BODY:
            print(line)
        print(RULE)
        print()

    def create_character(self):
        print("NIGHTGLASS PERSONNEL — assign identity:")
        print("  1. Crew        — Mara Vale")
        print("  2. Synthetic   — Valdorf")
        print("  3. Contractor  — Jonah Rusk")
        choice = input("> ").strip()
        player = self.engine.new_game(choice)
        label = player.type.replace("_", " ").title()
        print(f"\n{player.name}. {label}.")
        print(ROLE_FLAVOR[player.type])
        print("\nType 'help' at any time.\n")

    # ------------------------------------------------------------------ #
    def status_line(self):
        room = self.gs.current_room
        suit = "worn" if self.engine.player.suit_worn else "none"

        sound = self.gs.sound_level
        sound_code = {"audible": "33", "loud": "31", "violent": "1;31"}.get(sound, "2")
        suit_code = "31" if (suit == "none" and room.toxic) else "2"

        parts = [
            f"{self.c('Location:', '2')} {room.name}",
            f"{self.c('Sound:', '2')} {self.c(sound, sound_code)}",
            f"{self.c('Suit:', '2')} {self.c(suit, suit_code)}",
        ]

        motion = motion_label(self.engine.motion())
        if motion is not None:
            if motion in ("SEEN", "HERE"):
                code = "1;31"
            elif motion in ("interference", "lost", "none"):
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

            result = self.engine.submit(command)
            for line in result.lines:
                print("\n" + line)

            if result.quit:
                return
            if result.restart:
                self.restart()
                return
            if result.won:
                self.show_ending()
                if self.prompt_again():
                    self.restart()
                return
            # The moment it comes aboard earns a held breath.
            if result.boarded_now:
                self.beat()
            if result.dead:
                self.handle_death()
                if self.prompt_again():
                    self.restart()
                return

            # Re-render the full room after a move or a look; otherwise just status.
            if result.room_changed or command.lower() in ("look", "l"):
                self.render_room()
            else:
                print("\n" + self.status_line())

    # ------------------------------------------------------------------ #
    def handle_death(self):
        print()
        print(RULE)
        if self.gs.death_state == "monster":
            self.say(self.c(self.engine.death_text(), "31"), slow=True)
        elif self.gs.death_state == "toxic":
            pass  # already printed by the simulation
        print(RULE)
        print(self.c("\nYou died.", "1;31"))

    def show_ending(self):
        self.beat()
        print()
        print(RULE)
        self.say(self.c(ENDING_TRANSMISSION, "1;36"), slow=True)
        print()
        self.say(self.c(ENDING_WARNING, "1;36"), slow=True)
        print()
        for line in ENDING_HEADER:
            print(line)
        print()
        for line in ENDING_DIALOGUE:
            self.say(line, slow=True)
        print()
        print(ENDING_PAUSE)
        print()
        self.say(ENDING_WAKE, slow=True)
        print()
        self.say(ENDING_RECLASSIFIED, slow=True)
        print()
        for line in ENDING_INVITED:
            self.say(self.c(line, "1;36"), slow=True)
        print(RULE)
        print("\n" + ENDING_MISTAKE)
        self._leaderboard_prompt()

    def _leaderboard_prompt(self):
        moves = self.gs.turn_count
        player = self.gs.player
        scores = lb.load()
        print()
        print(RULE)
        print(self.c("TOP 10  —  fewest moves to win", "1"))
        if lb.qualifies(moves, scores):
            print(f"\nYou won in {moves} moves — that qualifies for the top 10!")
            default = player.name if player else "Unknown"
            try:
                raw = input(f"Enter your name (up to 40 chars) [{default}]: ").strip()
            except (KeyboardInterrupt, EOFError):
                raw = ""
            name = raw[: lb.MAX_NAME_LEN] or default
            role = player.type if player else "human"
            scores, rank = lb.insert(name, role, moves, scores)
            print(self.c(f"\nRank #{rank}  —  {name}  —  {moves} moves", "1;32"))
        else:
            print(f"\nYou won in {moves} moves.")
        print()
        for line in lb.format_table(scores):
            print(line)
        print(RULE)

    def prompt_again(self):
        try:
            choice = input("\nrestart / quit > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return False
        return choice.startswith("r")

    def restart(self):
        # Keep the same character to skip re-creation; new_game resets the world.
        prev = self.engine.player
        player = Player(prev.name, prev.gender, prev.type)
        self.engine.new_game(player=player)
        print("\n" + RULE)
        print("The cryo cycle resets. Again.")
        print(RULE)
        self.main_loop()


USAGE = """KEPLER ISOLATION — a terminal survival-horror text adventure.

  You wake aboard the USCSS Nightglass. Something else woke too.
  Collect radio components, craft a signal, override the AI, and send the warning.

Usage:
  ./play [options]          (or: python3 src/__main__.py [options])

Options:
  --tui         Launch the rich Textual UI (needs: pip install textual).
  --classic     Force the plain text mode (the default).
  --fast        Skip the typewriter pacing on dramatic beats.
  --color       Force ANSI color (on by default for a terminal).
  --no-color    Disable color. (NO_COLOR is also respected.)
  -h, --help    Show this help and exit.

In-game, type 'help' for the command list."""


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(USAGE)
        return
    if "--tui" in sys.argv and "--classic" not in sys.argv:
        try:
            import tui
        except ImportError:
            print("The rich UI needs Textual:  pip install textual")
            print("Or run the classic text mode:  ./play")
            return
        tui.run()
        return
    ClassicGame().start()


if __name__ == "__main__":
    main()
