# Contributing to THE THIN AIR

Small, testable steps. One logical change per commit. The game stays playable
at every commit.

## Before you change anything

Read [`ROADMAP.md`](ROADMAP.md), especially **§0 Design pillars**. They are the
spine — every change is judged against them. The short version:

- The fear is in *not*-seeing. The scanner is useful but never perfect.
- You can never win a fight. Agency is routing, hiding, distracting, timing.
- Tension is a wave: quiet lulls make the spikes land.
- The monster is modeled, never faked. Telegraph its *state* through prose.
- Economy of words (see the Tone Bible, §4). Fair deaths only.
- Low resolution, high finish. No combat, no open world, no RPG stats.

## Running things

```sh
./play                      # play it
python3 -m pytest tests/    # run the test suite (must stay green)
python3 tools/balance.py    # headless balance harness over many seeds
```

The test suite uses a **seeded RNG** for determinism (`conftest.build_game`).
If you touch monster behaviour or detection, run `tools/balance.py` and keep the
win rates in a fair band — a blind rush should die more often than not; careful
play should be comparably safe. Add a regression test for any bug you fix.

## Code style

- Match the surrounding code. Comments explain **why**, not what, and only at
  genuinely non-obvious spots.
- Prose follows the Tone Bible: second person, present tense, concrete nouns,
  short lines, the unsaid. The creature is never named by the narrator.
- Player-facing strings live with the code that emits them; keep them terse.

## Architecture (where things live)

| File | Responsibility |
|------|----------------|
| `src/__main__.py` | Entry point, character creation, UI/render, main loop, pacing/color |
| `src/game_state.py` | World state, pathfinding, sound, monster AI, the turn pipeline |
| `src/parser.py` | Command parsing and action handling |
| `src/map_builder.py` | The 22-room graph, items, vents, hiding spots, dread variants |
| `src/save.py` | JSON save/load |
| `src/room.py` `item.py` `player.py` `monster.py` | Data models |
