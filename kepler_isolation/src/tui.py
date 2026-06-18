"""
Textual front-end for KEPLER ISOLATION (the optional rich UI: `./play --tui`).

A resizable console layout — status bar, a scrolling narrative log, and a
sidebar of panels (a motion tracker, exits, items here, inventory) — all driven
by the same GameEngine the classic mode uses. Modeled on a modern MUD client:
scrollback + gauges. Requires `textual`.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Input, RichLog, Static
from rich.text import Text
from rich.markup import escape

from player import Player
import leaderboard as lb
from engine import (
    GameEngine, motion_label, ROLE_FLAVOR, INTRO_BODY,
    ENDING_TRANSMISSION, ENDING_WARNING, ENDING_HEADER, ENDING_DIALOGUE,
    ENDING_PAUSE, ENDING_WAKE, ENDING_RECLASSIFIED, ENDING_INVITED, ENDING_MISTAKE,
)

# Compass glyphs for the tracker bearing.
ARROWS = {"north": "↑", "south": "↓", "east": "→", "west": "←",
          "up": "▲", "down": "▼", "in": "⊙", "out": "⊗"}

# Narrow terminals drop the sidebar so the log keeps priority.
NARROW = 64


def tracker_markup(m: dict) -> str:
    """Render the motion() reading as a small tracker panel."""
    head = "[b]◢ MOTION TRACKER ◣[/]"
    k = m["kind"]
    if k == "no_device":
        return f"{head}\n[dim]— no device —[/]"
    if k == "none":
        return f"{head}\n[green]no contacts[/]"
    if k == "outside":
        return f"{head}\n[yellow]MOTION: outside[/]\n[dim]distance uncertain[/]"
    if k == "interference":
        return f"{head}\n[yellow]signal scrambled[/]"
    if k == "lost":
        return f"{head}\n[yellow]signal lost[/]"
    if k == "seen":
        return f"[b red]◢ MOTION TRACKER ◣[/]\n[blink bold red]IT SEES YOU[/]"
    if k == "here":
        return f"[b red]◢ MOTION TRACKER ◣[/]\n[bold red]CONTACT — THIS ROOM[/]"
    # bearing
    d, dist = m["direction"], m["distance"]
    color = "red" if dist <= 2 else "yellow"
    arrow = ARROWS.get(d, "•")
    plural = "" if dist == 1 else "s"
    return f"[{color}]◢ MOTION TRACKER ◣[/]\n[{color}]{arrow}  {d.upper()}[/]\nDIST: {dist} move{plural}"


def status_markup(engine: GameEngine) -> str:
    sound = engine.sound_level
    sound_c = {"audible": "yellow", "loud": "red", "violent": "bold red"}.get(sound, "dim")
    suit = engine.suit_status
    suit_c = "red" if (suit == "none" and engine.toxic_here) else "dim"
    parts = [f"[dim]LOC[/] {escape(engine.location_name)}",
             f"[dim]SOUND[/] [{sound_c}]{sound}[/]",
             f"[dim]SUIT[/] [{suit_c}]{suit}[/]",
             f"[dim]TURN[/] {engine.turn_count}"]
    mt = motion_label(engine.motion())
    if mt is not None:
        if mt in ("SEEN", "HERE"):
            c = "bold red"
        elif mt in ("interference", "lost", "outside", "none"):
            c = "dim"
        elif mt.split()[-1].isdigit() and int(mt.split()[-1]) <= 2:
            c = "red"
        else:
            c = "yellow"
        parts.append(f"[dim]MOTION[/] [{c}]{mt}[/]")
    return "   ".join(parts)


class KeplerApp(App):
    TITLE = "KEPLER ISOLATION"
    CSS = """
    #status { height: 1; padding: 0 1; background: $panel; color: $text; }
    #main { height: 1fr; }
    #log { width: 2fr; padding: 0 1; }
    #sidebar { width: 32; }
    .panel { border: round $primary; padding: 0 1; height: auto; margin-bottom: 1; }
    #cmd { dock: bottom; border: tall $accent; }
    """
    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.mode = "role"   # role | play | leaderboard | over
        self._lb_qualifies = False   # set at win time

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(status_blank(), id="status")
        with Horizontal(id="main"):
            yield RichLog(id="log", wrap=True, markup=False, highlight=False, min_width=20)
            with Vertical(id="sidebar"):
                yield Static("", id="tracker", classes="panel")
                yield Static("", id="exits", classes="panel")
                yield Static("", id="here", classes="panel")
                yield Static("", id="inv", classes="panel")
        yield Input(id="cmd", placeholder="type a command — e.g. look, take terminal, help")

    # ------------------------------------------------------------------ #
    def on_mount(self) -> None:
        self.rlog = self.query_one("#log", RichLog)
        for line in INTRO_BODY:
            self.rlog.write(line)
        self.rlog.write("")
        self.rlog.write("HALLOWAY-TANAKA PERSONNEL — assign role:")
        self.rlog.write("  1. Crew        — Elias Cole")
        self.rlog.write("  2. Synthetic   — Jonah")
        self.rlog.write("  3. Contractor  — Rourke Dunmore")
        self.rlog.write("")
        self.rlog.write("Type 1, 2, or 3.")
        self.query_one("#cmd", Input).focus()

    def on_resize(self, event: events.Resize) -> None:
        try:
            self.query_one("#sidebar").display = event.size.width >= NARROW
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    def _w(self, markup: str) -> None:
        """Write a styled line to the log."""
        self.rlog.write(Text.from_markup(markup))

    def _write_room(self) -> None:
        self._w(f"[b]{escape(self.engine.location_name)}[/]")
        self.rlog.write(self.engine.room_text())

    def _refresh(self) -> None:
        self.query_one("#status", Static).update(Text.from_markup(status_markup(self.engine)))
        self.query_one("#tracker", Static).update(Text.from_markup(tracker_markup(self.engine.motion())))
        exits = ", ".join(self.engine.exits) or "none"
        self.query_one("#exits", Static).update(Text.from_markup(f"[b]EXITS[/]\n{escape(exits)}"))
        items = self.engine.room_items
        here = "\n".join(escape(i) for i in items) if items else "[dim]nothing[/]"
        self.query_one("#here", Static).update(Text.from_markup(f"[b]HERE[/]\n{here}"))
        inv = self.engine.inventory
        carry = "\n".join(escape(i) for i in inv) if inv else "[dim]nothing[/]"
        self.query_one("#inv", Static).update(Text.from_markup(f"[b]CARRYING[/]\n{carry}"))

    # ------------------------------------------------------------------ #
    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        self.query_one("#cmd", Input).value = ""
        if not text:
            return

        if self.mode == "role":
            self._start(text)
            return

        if self.mode == "leaderboard":
            self._record_leaderboard(text)
            return

        if self.mode == "over":
            low = text.lower()
            if low.startswith("r"):
                self._restart()
            elif low.startswith("q"):
                self.exit()
            return

        # --- play mode ---
        self._w(f"[cyan]> {escape(text)}[/]")
        result = self.engine.submit(text)
        for line in result.lines:
            self.rlog.write(line)

        if result.quit:
            self.exit()
            return
        if result.restart:
            self._restart()
            return
        if result.won:
            self._show_ending()
            self.mode = "leaderboard" if self._lb_qualifies else "over"
            self._refresh()
            return
        if result.dead:
            self._show_death()
            self.mode = "over"
            self._refresh()
            return

        if result.room_changed or text.lower() in ("look", "l"):
            self.rlog.write("")
            self._write_room()
        self._refresh()

    # ------------------------------------------------------------------ #
    def _start(self, choice: str) -> None:
        player = self.engine.new_game(choice if choice in ("1", "2", "3") else "1")
        self.rlog.clear()
        self._w(f"[b]{escape(player.name)}[/]. {player.type.replace('_', ' ').title()}.")
        for line in ROLE_FLAVOR[player.type].split("\n"):
            self.rlog.write(line)
        self.rlog.write("The manifest lists him, and no one else.")
        self.rlog.write("")
        self.mode = "play"
        self._write_room()
        self._refresh()

    def _restart(self) -> None:
        p = self.engine.gs.player
        self.engine.new_game(player=Player(p.name, p.gender, p.type))
        self.rlog.clear()
        self._w("[dim]The descent sedation lifts. Again.[/]")
        self.rlog.write("")
        self.mode = "play"
        self._write_room()
        self._refresh()

    def _show_death(self) -> None:
        self.rlog.write("")
        if self.engine.gs.death_state == "monster":
            for line in self.engine.death_text().split("\n"):
                self._w(f"[red]{escape(line)}[/]")
        self._w("[bold red]You died.[/]")
        self._w("[dim]Type 'restart' or 'quit'.[/]")

    def _show_ending(self) -> None:
        self.rlog.write("")
        self._w(f"[b cyan]{ENDING_TRANSMISSION}[/]")
        self._w(f"[b cyan]{escape(ENDING_WARNING)}[/]")
        self.rlog.write("")
        for line in ENDING_HEADER:
            self.rlog.write(line)
        self.rlog.write("")
        for line in ENDING_DIALOGUE:
            self.rlog.write(line)
        self.rlog.write("")
        self.rlog.write(ENDING_PAUSE)
        self.rlog.write(ENDING_WAKE)
        self.rlog.write(ENDING_RECLASSIFIED)
        self.rlog.write("")
        for line in ENDING_INVITED:
            self._w(f"[b cyan]{escape(line)}[/]")
        self._w(f"[b]{escape(ENDING_MISTAKE)}[/]")
        self.rlog.write("")
        moves = self.engine.turn_count
        scores = lb.load()
        self._lb_qualifies = lb.qualifies(moves, scores)
        if self._lb_qualifies:
            default = self.engine.player.name if self.engine.player else "Unknown"
            self._w(f"[b green]You won in {moves} moves — TOP 10![/]")
            self._w(f"[dim]Enter your name (up to 40 chars) and press Enter  [{escape(default)}]:[/]")
            self.query_one("#cmd", Input).placeholder = f"name — or press Enter for '{default}'"
        else:
            self._w(f"[dim]You won in {moves} moves.[/]")
            self._show_leaderboard(scores)
            self._w("[dim]Type 'restart' or 'quit'.[/]")

    def _record_leaderboard(self, name: str) -> None:
        moves = self.engine.turn_count
        player = self.engine.player
        default = player.name if player else "Unknown"
        name = (name[:lb.MAX_NAME_LEN].strip()) or default
        role = player.type if player else "human"
        scores = lb.load()
        scores, rank = lb.insert(name, role, moves, scores)
        self._w(f"[b green]Rank #{rank}  —  {escape(name)}  —  {moves} moves[/]")
        self._show_leaderboard(scores)
        self.query_one("#cmd", Input).placeholder = "type a command — e.g. look, take terminal, help"
        self._w("[dim]Type 'restart' or 'quit'.[/]")
        self.mode = "over"

    def _show_leaderboard(self, scores: list) -> None:
        self.rlog.write("")
        self._w("[b]TOP 10  —  fewest moves to win[/]")
        for line in lb.format_table(scores):
            self.rlog.write(line)
        self.rlog.write("")


def status_blank() -> str:
    return "[b]KEPLER ISOLATION[/]   [dim]select your role to begin[/]"


def run() -> None:
    KeplerApp().run()


if __name__ == "__main__":
    run()
