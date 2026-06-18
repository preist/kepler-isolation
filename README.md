# KEPLER ISOLATION

*A short, lethal terminal horror game. Zork's parser by way of Alien: Isolation's dread.*

---

A distress signal is coming from beneath a dead world. It is old. It has not
degraded. That should not be possible.

You are contract labour for **Halloway-Tanaka Industries**, aboard the survey
lander **LANTERN-9**. The air outside kills in two breaths without a suit. The
signal is coming from a cave below the landing site, and your contract says to
find out what's making it.

You will. And it will come back up with you.

What follows is one creature — not a scripted jump scare but a real thing moving
through a real ship, hunting by sound. A motion scanner that is useful, and
never quite enough. Hiding that works once or twice, not forever. A transmitter
to repair and a warning to send, before it finds you in the dark.

It takes about thirty minutes. You will probably die first. That's how you learn
the ship.

---

## Quick start

You need **Python 3.8 or newer**. The game uses only the standard library — no
packages to install, nothing to download but this repository.

**macOS / Linux:**

```sh
git clone https://github.com/preist/kepler-isolation.git
cd kepler-isolation
./play
```

**Windows** (PowerShell or Command Prompt):

```sh
git clone https://github.com/preist/kepler-isolation.git
cd kepler-isolation
python kepler_isolation\src\__main__.py
```

That's it. Type `help` at any time in the game.

> No `git`? On the GitHub page click **Code → Download ZIP**, unzip it, open a
> terminal in the unzipped folder, and run the same launch command.

---

## Don't have Python yet?

Check first — open a terminal and run `python3 --version` (macOS/Linux) or
`python --version` (Windows). If you see a version number `3.8` or higher,
you're ready. Otherwise:

- **macOS** — Install from [python.org/downloads](https://www.python.org/downloads/),
  or with [Homebrew](https://brew.sh): `brew install python`.
- **Windows** — Install from [python.org/downloads](https://www.python.org/downloads/).
  **Tick "Add python.exe to PATH"** in the installer. Then use `python` (or `py`).
- **Linux** — It's almost certainly already installed. If not, e.g. on
  Debian/Ubuntu: `sudo apt install python3`.

No editor, virtual environment, or `pip install` is required.

---

## How to play — the first few minutes

You wake in the **Cockpit**. The game reads your typed commands; movement and
common verbs have short aliases, and it forgives minor wording.

A gentle opening run (no spoilers):

```text
> look                 see where you are
> take hand terminal   your motion scanner — grab it first
> read company memo    there's reading material aboard; it pays to look
> south                move between rooms (or n/s/e/w, in/out, up/down)
> scan                 once things stir, this shows direction + distance
```

Your goal is to reach **Communications**, fit the three repair parts, and
**send the warning**. The parts are aboard the ship; you'll have to explore to
find them. Before you ever step outside, find the **EVA suit** in the Airlock
and `wear` it — the atmosphere is not survivable otherwise.

When the ship stops being safe, you have options: move quietly (`crawl`),
`hide`, `throw` something to pull attention away, and watch the `scan` and the
status line. Loud actions — running, the final repair — carry.

Type `help` for the full command list, and `map` to see where you've been.

### Commands at a glance

| Do | Type |
|----|------|
| Move | `north` `south` `east` `west` `in` `out` `up` `down` (or `n` `s` `e` `w`…) |
| Look around | `look` · `examine <thing>` (`x`) · `read <thing>` · `listen` |
| Carry | `take <thing>` (`get`) · `drop <thing>` · `inventory` (`i`) · `use <thing>` |
| Suit | `wear suit` · `remove suit` |
| Survive | `scan` · `hide [spot]` · `crawl <dir>` · `run <dir>` · `throw <thing> <dir>` |
| Win | `install <part>` · `repair transmitter` · `send <message>` |
| Meta | `map` · `save` · `load` · `help` · `restart` · `quit` |

### Survival tips (no spoilers)

- The suit comes off the clock the moment you're sealed — but the air bites the
  instant you remove it outside.
- Quiet is life. Walking is quiet; **running and loud actions are not**.
- A hiding place is a reprieve, not a fortress. Don't linger, and don't trust
  the same spot twice.
- The scanner can lag or scramble in some rooms. Trust it — but not blindly.

### Options

```sh
./play --help        # usage and flags
./play --fast        # skip the typewriter pacing on dramatic beats
./play --no-color    # plain text (color is on by default in a terminal)
```

You can `save` and `load` a single game in progress from inside the game.

---

## For the curious

The full design notes and roadmap live in
[`kepler_isolation/ROADMAP.md`](kepler_isolation/ROADMAP.md), and contributor notes in
[`kepler_isolation/CONTRIBUTING.md`](kepler_isolation/CONTRIBUTING.md). To run the test
suite:

```sh
python3 -m pytest kepler_isolation/tests/
```

Built as a focused, terse, lethal little knife of a game. Good luck. Stay quiet.
