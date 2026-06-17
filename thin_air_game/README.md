# THE THIN AIR

A short terminal survival-horror text adventure. You land on a toxic planet,
explore a cave, and return to your ship with something you didn't invite.
Repair the transmitter, send the warning — and try not to be found.

## Play

```sh
python3 src/__main__.py
```

Requires Python 3 (standard library only).

## How to play

You wake in the **Cockpit**. Goal: reach **Communications**, install the three
repair parts (power coupler, signal relay, antenna key), repair the
transmitter, and `send` a warning.

- **Move:** `north`/`south`/`east`/`west`, `in`/`out`, `up`/`down` (or `n`,`s`,`e`,`w`...)
- **Look:** `look`, `examine <thing>` (`x`), `read <thing>`, `listen`, `scan`, `map`
- **Items:** `take <thing>` (`get`), `drop`, `inventory` (`i`), `use <thing>`
- **Suit:** `wear suit`, `remove suit`
- **Survive:** `hide [spot]`, `crawl <dir>`, `run <dir>`, `throw <thing> <dir>`
- **Win:** `install <part>`, `repair transmitter`, `send <message>`
- **Meta:** `help`, `quit`, `restart`

## Rules that will kill you

- **The air is lethal.** Outside the ship, wear the EVA suit (in the Airlock)
  or you die in two moves (synthetics get three).
- **Sound draws the monster.** Walking is quiet; running, throwing, and the
  final repair are loud. The status line and `scan` show its direction and
  distance once it's aboard.
- **Hiding is temporary.** A spot works once or twice. Reusing it, or lingering,
  gets you found. A thrown can or flare can buy a single pass.

## Source layout

| File | Responsibility |
|------|----------------|
| `__main__.py` | Entry point, character creation, UI rendering, main loop |
| `game_state.py` | World state, pathfinding, sound, monster AI, turn pipeline |
| `parser.py` | Command parsing and action handling |
| `map_builder.py` | The 22-room graph, items, vents, hiding spots |
| `room.py` / `item.py` / `player.py` / `monster.py` | Data models |
