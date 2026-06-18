"""
Leaderboard for KEPLER ISOLATION — top 10 wins by fewest moves.

Scores are stored in ~/.kepler_isolation_scores.json and persist across runs.
"""

import json
from datetime import date
from pathlib import Path

LEADERBOARD_PATH = Path.home() / ".kepler_isolation_scores.json"
MAX_ENTRIES = 10
MAX_NAME_LEN = 40


def load() -> list:
    try:
        data = json.loads(LEADERBOARD_PATH.read_text())
        return data.get("scores", [])
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def _save(scores: list) -> None:
    try:
        LEADERBOARD_PATH.write_text(json.dumps({"scores": scores}, indent=2))
    except OSError:
        pass


def qualifies(moves: int, scores: list) -> bool:
    """True if this move count earns a spot in the current top 10."""
    if len(scores) < MAX_ENTRIES:
        return True
    return moves < scores[-1]["moves"]


def insert(name: str, role: str, moves: int, scores: list) -> tuple:
    """Add a new entry, keep top 10 sorted by moves ascending.

    Returns (updated_scores, rank) where rank is 1-based.
    """
    name = name[:MAX_NAME_LEN].strip() or "Unknown"
    entry = {
        "name": name,
        "role": role,
        "moves": moves,
        "date": date.today().isoformat(),
    }
    scores = scores + [entry]
    scores.sort(key=lambda e: e["moves"])
    scores = scores[:MAX_ENTRIES]
    _save(scores)
    rank = next((i + 1 for i, e in enumerate(scores) if e["name"] == name
                 and e["moves"] == moves and e["date"] == entry["date"]), None)
    return scores, rank


def format_table(scores: list) -> list:
    """Return display lines for the leaderboard (no trailing newline)."""
    header = f"  {'#':>2}  {'NAME':<40}  {'MOVES':>5}  DATE"
    sep    = "  " + "-" * (len(header) - 2)
    if not scores:
        return [header, sep, "      (no scores yet)"]
    lines = [header, sep]
    for i, e in enumerate(scores):
        lines.append(f"  {i+1:>2}  {e['name']:<40}  {e['moves']:>5}  {e['date']}")
    return lines
