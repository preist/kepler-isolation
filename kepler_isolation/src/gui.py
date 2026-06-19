"""
PySide6 GUI front-end for KEPLER ISOLATION.

Run:  python3 src/__main__.py --gui
      or: make gui

Same GameEngine as the TUI and classic modes — no game logic here.

Room images are optional. Drop zone images into:
    kepler_isolation/assets/zones/{zone}.jpg   (or .png / .webp)
where {zone} is the first character of the room_id:
    a  Command / Bridge
    b  Operations / Crew quarters
    c  Cryo Bay
    d  Science / Medical
    e  Commons / EVA
    f  Engineering
    g  Cargo / Alien territory
    m  Maintenance tunnels
"""

import html as _html
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QKeyEvent,
    QPalette,
    QPixmap,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

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

# ---------------------------------------------------------------------------
# Colour palette — hardcoded dark theme, consistent on all platforms
# ---------------------------------------------------------------------------
_BG = "#0e0e0e"
_PANEL = "#161616"
_BORDER = "#2a2a2a"
_TEXT = "#c8c8b8"
_DIM = "#585848"
_CYAN = "#5bb8d4"
_BRIGHT_CYAN = "#80d4ea"
_RED = "#b03030"
_BRIGHT_RED = "#e05040"
_AMBER = "#c89820"
_GREEN = "#4a7c50"

# ---------------------------------------------------------------------------
# Asset resolution
# ---------------------------------------------------------------------------
_ROOMS_DIR = Path(__file__).parent.parent / "assets" / "rooms"


def _room_pixmap(room_id: str) -> "QPixmap | None":
    """Return a QPixmap for this room, or None.

    Drop square PNGs into:  kepler_isolation/assets/rooms/{room_id}.png
    e.g. c09.png, a07.png, g11.png
    """
    if not room_id:
        return None
    p = _ROOMS_DIR / f"{room_id}.png"
    if p.exists():
        px = QPixmap(str(p))
        if not px.isNull():
            return px
    return None


# ---------------------------------------------------------------------------
# Command input with ↑/↓ history
# ---------------------------------------------------------------------------
class _CmdInput(QLineEdit):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._hist: list[str] = []
        self._idx = 0

    def push(self, text: str) -> None:
        if text and (not self._hist or self._hist[-1] != text):
            self._hist.append(text)
        self._idx = len(self._hist)

    def keyPressEvent(self, ev: QKeyEvent) -> None:  # type: ignore[override]
        if ev.key() == Qt.Key.Key_Up:
            if self._idx > 0:
                self._idx -= 1
                self.setText(self._hist[self._idx])
            return
        if ev.key() == Qt.Key.Key_Down:
            if self._idx < len(self._hist) - 1:
                self._idx += 1
                self.setText(self._hist[self._idx])
            else:
                self._idx = len(self._hist)
                self.clear()
            return
        super().keyPressEvent(ev)


# ---------------------------------------------------------------------------
# Sidebar panel — bordered box with a dim header + body text
# ---------------------------------------------------------------------------
class _Panel(QFrame):
    def __init__(self, header: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background:{_PANEL}; border:1px solid {_BORDER}; border-radius:3px;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 5, 8, 7)
        lay.setSpacing(3)

        hdr = QLabel(header.upper())
        hdr.setStyleSheet(f"color:{_DIM}; font-size:9px; font-weight:700; border:none; letter-spacing:1px;")
        lay.addWidget(hdr)

        self._body = QLabel()
        self._body.setWordWrap(True)
        self._body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._body.setStyleSheet(f"color:{_TEXT}; border:none;")
        lay.addWidget(self._body)

    def set_text(self, text: str) -> None:
        self._body.setText(text)

    def set_html(self, markup: str) -> None:
        self._body.setText(markup)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class KeplerGUI(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.engine = GameEngine()
        self.mode = "role"  # role | play | leaderboard | over
        self._lb_qualifies = False
        self._font = self._make_mono(11)
        self._small_font = self._make_mono(10)
        self._apply_palette()
        self._build_ui()
        self._show_intro()

    # ------------------------------------------------------------------ #
    # Fonts and palette
    # ------------------------------------------------------------------ #
    @staticmethod
    def _make_mono(size: int) -> QFont:
        f = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        f.setPointSize(size)
        return f

    def _apply_palette(self) -> None:
        pal = QPalette()
        for role, hex_col in [
            (QPalette.ColorRole.Window, _BG),
            (QPalette.ColorRole.WindowText, _TEXT),
            (QPalette.ColorRole.Base, _PANEL),
            (QPalette.ColorRole.AlternateBase, _BG),
            (QPalette.ColorRole.Text, _TEXT),
            (QPalette.ColorRole.PlaceholderText, _DIM),
            (QPalette.ColorRole.Button, "#202020"),
            (QPalette.ColorRole.ButtonText, _TEXT),
            (QPalette.ColorRole.Highlight, "#1e3d4f"),
            (QPalette.ColorRole.HighlightedText, _TEXT),
        ]:
            pal.setColor(role, QColor(hex_col))
        QApplication.instance().setPalette(pal)  # type: ignore[union-attr]

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        self.setWindowTitle("KEPLER ISOLATION")
        self.resize(1120, 740)
        self.setMinimumSize(820, 560)

        root = QWidget()
        root.setStyleSheet(f"background:{_BG};")
        root_lay = QVBoxLayout(root)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)
        self.setCentralWidget(root)

        # ── Top status bar ────────────────────────────────────────────
        self._status = QLabel()
        self._status.setFont(self._small_font)
        self._status.setContentsMargins(12, 0, 12, 0)
        self._status.setFixedHeight(26)
        self._status.setStyleSheet(f"background:{_PANEL}; color:{_DIM}; border-bottom:1px solid {_BORDER};")
        root_lay.addWidget(self._status)

        # ── Main area: log | sidebar ──────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet(f"QSplitter::handle {{ background:{_BORDER}; }}")
        root_lay.addWidget(splitter, stretch=1)

        # Narrative log
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(self._font)
        self._log.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self._log.setStyleSheet(f"QTextEdit {{ background:{_BG}; color:{_TEXT}; border:none; padding:10px 14px; }}")
        self._log.document().setDefaultStyleSheet(
            f"body, p, span {{ font-family: monospace; font-size: 11pt; color: {_TEXT}; }}"
        )
        splitter.addWidget(self._log)

        # Sidebar (scrollable)
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sidebar_scroll.setStyleSheet(
            f"QScrollArea {{ background:{_BG}; border:none; }}"
            f"QScrollBar:vertical {{ background:{_BG}; width:5px; border:none; }}"
            f"QScrollBar::handle:vertical {{ background:{_BORDER}; border-radius:2px; min-height:20px; }}"
        )

        sidebar_inner = QWidget()
        sidebar_inner.setStyleSheet(f"background:{_BG};")
        sidebar_lay = QVBoxLayout(sidebar_inner)
        sidebar_lay.setContentsMargins(8, 8, 8, 8)
        sidebar_lay.setSpacing(7)

        # Room image — optional 400×400; hidden when no image file found
        self._img_frame = QFrame()
        self._img_frame.setFixedHeight(400)
        self._img_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._img_frame.setStyleSheet(f"background:#080808; border:1px solid {_BORDER}; border-radius:3px;")
        img_lay = QVBoxLayout(self._img_frame)
        img_lay.setContentsMargins(0, 0, 0, 0)
        self._img_label = QLabel()
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_label.setStyleSheet("border:none;")
        self._img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        img_lay.addWidget(self._img_label)
        sidebar_lay.addWidget(self._img_frame)

        # Tracker / exits / here / carrying panels
        self._p_tracker = _Panel("motion tracker")
        self._p_exits = _Panel("exits")
        self._p_here = _Panel("here")
        self._p_carry = _Panel("carrying")
        for panel in (self._p_tracker, self._p_exits, self._p_here, self._p_carry):
            panel.set_text("—")
            sidebar_lay.addWidget(panel)

        sidebar_lay.addStretch()
        sidebar_scroll.setWidget(sidebar_inner)

        # Sidebar minimum width fits the image at 400 + margins
        sidebar_scroll.setMinimumWidth(240)
        splitter.addWidget(sidebar_scroll)
        splitter.setSizes([680, 432])

        # ── Input bar ─────────────────────────────────────────────────
        input_frame = QFrame()
        input_frame.setFixedHeight(38)
        input_frame.setStyleSheet(f"background:{_PANEL}; border-top:1px solid {_BORDER};")
        input_lay = QHBoxLayout(input_frame)
        input_lay.setContentsMargins(12, 0, 12, 0)
        input_lay.setSpacing(8)

        prompt_lbl = QLabel(">")
        prompt_lbl.setFont(self._font)
        prompt_lbl.setStyleSheet(f"color:{_CYAN}; border:none;")
        input_lay.addWidget(prompt_lbl)

        self._cmd = _CmdInput()
        self._cmd.setFont(self._font)
        self._cmd.setStyleSheet(f"QLineEdit {{ background:transparent; color:{_TEXT}; border:none; }}")
        self._cmd.setPlaceholderText("type a command — e.g.  look   take terminal   help")
        self._cmd.returnPressed.connect(self._on_submit)
        input_lay.addWidget(self._cmd)

        root_lay.addWidget(input_frame)
        self._cmd.setFocus()

    # ------------------------------------------------------------------ #
    # Intro
    # ------------------------------------------------------------------ #
    def _show_intro(self) -> None:
        self._w_rule()
        for line in INTRO_BODY:
            self._w(line)
        self._w_rule()
        self._w("")
        self._w("NIGHTGLASS PERSONNEL — assign identity:", color=_DIM)
        self._w("  1.  Crew        — Mara Vale")
        self._w("  2.  Synthetic   — Valdorf")
        self._w("  3.  Contractor  — Jonah Rusk")
        self._w("")
        self._w("Type 1, 2, or 3.", color=_DIM)
        self._status.setText("  KEPLER ISOLATION  —  select your role to begin")

    # ------------------------------------------------------------------ #
    # Log writing
    # ------------------------------------------------------------------ #
    @staticmethod
    def _esc(text: str) -> str:
        return _html.escape(text)

    def _w(
        self,
        text: str = "",
        color: str | None = None,
        bold: bool = False,
    ) -> None:
        escaped = self._esc(text)
        style = ""
        if color:
            style += f"color:{color};"
        if bold:
            style += "font-weight:bold;"
        if style:
            fragment = f'<span style="{style}">{escaped}</span>'
        else:
            fragment = escaped
        self._log.append(fragment)
        self._log.moveCursor(QTextCursor.MoveOperation.End)

    def _w_rule(self) -> None:
        self._w("─" * 58, color=_BORDER)

    def _w_result(self, lines: list[str]) -> None:
        """Write engine result lines with light heuristic colouring."""
        for line in lines:
            if not line:
                self._w("")
                continue
            lo = line.lower()
            if any(k in lo for k in ("is dead", "it sees", "dead.", "searching streak")):
                self._w(line, color=_BRIGHT_RED)
            elif any(k in lo for k in ("organism", "contact", "it is in", "it checks")):
                self._w(line, color=_RED)
            elif any(k in lo for k in ("mother-lacuna",)):
                self._w(line, color=_DIM)
            elif line.startswith("─") or line.startswith("[Life"):
                self._w(line, color=_DIM)
            else:
                self._w(line)

    def _write_room(self) -> None:
        self._w("")
        room = self.engine.gs.current_room
        self._w(room.name, bold=True)
        self._w(room.describe(self.engine.gs))
        exits = ", ".join(room.exits.keys()) if room.exits else "none"
        self._w(f"Exits: {exits}", color=_DIM)
        if room.items:
            self._w("Items: " + ", ".join(i.name for i in room.items), color=_DIM)

    # ------------------------------------------------------------------ #
    # Status bar + sidebar
    # ------------------------------------------------------------------ #
    def _refresh(self) -> None:
        self._refresh_status()
        self._refresh_sidebar()
        self._refresh_image()

    def _refresh_status(self) -> None:
        e = self.engine
        sound = e.sound_level
        s_col = {"audible": _AMBER, "loud": _RED, "violent": _BRIGHT_RED}.get(sound, _DIM)
        suit = e.suit_status
        t_col = _RED if (suit == "none" and e.toxic_here) else _DIM

        def sp(label: str, value: str, vc: str) -> str:
            return f'<span style="color:{_DIM}">{label}</span>&nbsp;<span style="color:{vc}">{self._esc(value)}</span>'

        parts = [
            sp("LOC", e.location_name, _TEXT),
            sp("SOUND", sound, s_col),
            sp("SUIT", suit, t_col),
            sp("TURN", str(e.turn_count), _TEXT),
        ]

        ml = motion_label(e.motion())
        if ml is not None:
            if ml in ("SEEN", "HERE"):
                mc = _BRIGHT_RED
            elif ml in ("interference", "lost", "none"):
                mc = _DIM
            else:
                try:
                    mv = int(ml.split("~")[1].replace("m", "").strip())
                    mc = _RED if mv <= 30 else _AMBER
                except (IndexError, ValueError):
                    mc = _AMBER
            parts.append(sp("MOTION", ml, mc))

        sep = f'&nbsp;<span style="color:{_BORDER}">│</span>&nbsp;'
        self._status.setText(sep.join(parts))

    def _refresh_sidebar(self) -> None:
        e = self.engine
        m = e.motion()
        kind = m["kind"]

        _arrow = {
            "north": "↑",
            "south": "↓",
            "east": "→",
            "west": "←",
            "northeast": "↗",
            "northwest": "↖",
            "southeast": "↘",
            "southwest": "↙",
            "up": "▲",
            "down": "▼",
            "in": "⊙",
            "out": "⊗",
        }
        _abbr = {
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

        if kind == "no_device":
            tracker = f'<span style="color:{_DIM}">— no device —</span>'
        elif kind == "none":
            tracker = f'<span style="color:{_GREEN}">no contacts</span>'
        elif kind in ("interference", "lost"):
            tracker = f'<span style="color:{_AMBER}">signal {kind}</span>'
        elif kind == "seen":
            tracker = f'<span style="color:{_BRIGHT_RED}"><b>IT SEES YOU</b></span>'
        elif kind == "here":
            tracker = f'<span style="color:{_BRIGHT_RED}"><b>CONTACT — THIS ROOM</b></span>'
        else:
            d = m.get("direction") or "?"
            meters = m.get("meters", 0)
            conf = m.get("confidence", 70)
            desc = m.get("motion_desc", "slow")
            col = _RED if meters <= 30 else _AMBER
            arrow = _arrow.get(d, "•")
            abbr = _abbr.get(d, d.upper())
            tracker = (
                f'<span style="color:{col};font-size:14px">{arrow}</span>'
                f'&nbsp;<span style="color:{col};font-weight:bold">{abbr}</span>'
                f'<br><span style="color:{_TEXT}">~{meters} m &nbsp; {desc}</span>'
                f'<br><span style="color:{_DIM}">confidence {conf}%</span>'
            )
        self._p_tracker.set_html(tracker)

        self._p_exits.set_text(", ".join(e.exits) if e.exits else "none")
        items = e.room_items
        self._p_here.set_text(", ".join(items) if items else "nothing")
        inv = e.inventory
        self._p_carry.set_text(", ".join(inv) if inv else "nothing")

    def _refresh_image(self) -> None:
        room_id = self.engine.gs.current_room_id
        px = _room_pixmap(room_id)
        if px is None:
            # Hide the image panel entirely when no image is available.
            self._img_frame.setVisible(False)
            return

        self._img_frame.setVisible(True)
        # Cover: scale the square PNG to fill the frame (max 400×400), centre-crop
        # any overflow so neither dimension ever shows a gap.
        fw = min(self._img_frame.width() or 400, 400)
        fh = min(self._img_frame.height() or 400, 400)
        side = max(fw, fh)  # square images → one scale step covers both axes
        scaled = px.scaled(
            QSize(side, side),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        ox = (scaled.width() - fw) // 2
        oy = (scaled.height() - fh) // 2
        self._img_label.setPixmap(scaled.copy(ox, oy, fw, fh))
        self._img_label.setText("")

    # ------------------------------------------------------------------ #
    # Command dispatch
    # ------------------------------------------------------------------ #
    def _on_submit(self) -> None:
        text = self._cmd.text().strip()
        self._cmd.clear()
        if not text:
            return
        self._cmd.push(text)
        self._w(f"> {text}", color=_CYAN)

        if self.mode == "role":
            self._start(text)
            return
        if self.mode == "leaderboard":
            self._record_leaderboard(text)
            return
        if self.mode == "over":
            lo = text.lower()
            if lo.startswith("r"):
                self._restart()
            elif lo.startswith("q"):
                QApplication.quit()
            return

        # play ──────────────────────────────────────────────────────────
        result = self.engine.submit(text)
        self._w_result(result.lines)

        if result.quit:
            QApplication.quit()
            return
        if result.restart:
            self._restart()
            return
        if result.won:
            self._show_ending()
            return
        if result.next_life:
            self._write_room()
            self._refresh()
            return
        if result.dead:
            self._show_death()
            return
        if result.room_changed or text.lower() in ("look", "l"):
            self._write_room()
        self._refresh()

    # ------------------------------------------------------------------ #
    # Game flow helpers
    # ------------------------------------------------------------------ #
    def _start(self, choice: str) -> None:
        player = self.engine.new_game(choice if choice in ("1", "2", "3") else "1")
        self._log.clear()
        self._w(f"{player.name}.  {player.type.replace('_', ' ').title()}.", bold=True)
        self._w("")
        for line in ROLE_FLAVOR[player.type].split("\n"):
            self._w(line)
        pod_text = self.engine.sleeping_pod_text()
        if pod_text:
            self._w("")
            for line in pod_text.split("\n"):
                self._w(line)
        self._w("")
        self._w("Type 'help' at any time.", color=_DIM)
        self.mode = "play"
        self._write_room()
        self._refresh()

    def _restart(self) -> None:
        p = self.engine.player
        role = {"crew": "1", "synthetic": "2", "contractor": "3"}.get(p.type, "1")
        self.engine.new_game(role, player=Player(p.name, p.gender, p.type))
        self._log.clear()
        self._w("The cryo cycle resets. Again.", color=_DIM)
        self._w("")
        self.mode = "play"
        self._write_room()
        self._refresh()

    def _show_death(self) -> None:
        self._w("")
        self._w_rule()
        for line in self.engine.death_text().split("\n"):
            self._w(line, color=_RED)
        self._w_rule()
        self._w("All three crew members dead. The mission is over.", color=_BRIGHT_RED, bold=True)
        self._w("")
        self._w("Type 'restart' or 'quit'.", color=_DIM)
        self.mode = "over"
        self._refresh()

    def _show_ending(self) -> None:
        self._w("")
        self._w_rule()
        self._w(ENDING_TRANSMISSION, color=_BRIGHT_CYAN, bold=True)
        self._w(ENDING_WARNING, color=_BRIGHT_CYAN)
        self._w("")
        for line in ENDING_HEADER:
            self._w(line, color=_DIM)
        self._w("")
        for line in ENDING_DIALOGUE:
            self._w(line)
        self._w("")
        self._w(ENDING_PAUSE, color=_DIM)
        self._w("")
        self._w(ENDING_WAKE)
        self._w(ENDING_RECLASSIFIED, color=_DIM)
        self._w("")
        for line in ENDING_INVITED:
            self._w(line, color=_BRIGHT_CYAN, bold=True)
        self._w(ENDING_MISTAKE, bold=True)
        self._w_rule()
        self._w("")

        moves = self.engine.turn_count
        scores = lb.load()
        self._lb_qualifies = lb.qualifies(moves, scores)
        if self._lb_qualifies:
            default = self.engine.player.name
            self._w(f"You won in {moves} moves — TOP 10!", color=_GREEN, bold=True)
            self._w(f"Enter your name and press Enter  [{default}]:", color=_DIM)
            self.mode = "leaderboard"
        else:
            self._w(f"You won in {moves} moves.", color=_DIM)
            self._show_leaderboard(scores)
            self._w("Type 'restart' or 'quit'.", color=_DIM)
            self.mode = "over"
        self._refresh()

    def _record_leaderboard(self, name: str) -> None:
        moves = self.engine.turn_count
        player = self.engine.player
        default = player.name
        name = (name[: lb.MAX_NAME_LEN].strip()) or default
        scores = lb.load()
        scores, rank = lb.insert(name, player.type, moves, scores)
        self._w(f"Rank #{rank}  —  {name}  —  {moves} moves", color=_GREEN, bold=True)
        self._show_leaderboard(scores)
        self._w("Type 'restart' or 'quit'.", color=_DIM)
        self.mode = "over"

    def _show_leaderboard(self, scores: list) -> None:
        self._w("")
        self._w("TOP 10  —  fewest moves to win", bold=True)
        for line in lb.format_table(scores):
            self._w(line, color=_DIM)
        self._w("")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def run() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("KEPLER ISOLATION")
    win = KeplerGUI()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
