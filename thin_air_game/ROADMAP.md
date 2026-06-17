# THE THIN AIR — Roadmap to a Terminal Masterpiece

> Goal: a text adventure that earns the comparison to *Alien: Isolation* — at a
> deliberately **low resolution** of world and complexity, but a **high
> resolution of dread**. Small map. Few systems. Every word load-bearing.

This document is the plan for the next versions. It is meant to be *airtight*:
every item is concrete, scoped, ordered, and has a definition of done. We build
in small, testable steps — no monolithic rewrites.

---

## 0. Design pillars (the spine — do not violate these)

These are the rules we judge every change against.

1. **The fear is in not-seeing.** The scanner must be *useful but imperfect*. A
   blip with no creature in the room is scarier than the creature. Never let the
   player have perfect information.
2. **You cannot win a fight.** The creature is unkillable. Player agency is
   *reading, routing, hiding, distracting, and timing* — never combat.
3. **Tension is a wave, not a wall.** Dread needs lulls. Quiet, almost-safe
   moments are what make the spikes land. A constantly-screaming game is noise.
4. **The monster is modeled, never faked.** It has a real room, real path, real
   memory. We telegraph its *state* through prose, never through numbers.
5. **Economy of words.** Second person, present tense, concrete nouns, short
   lines. The unsaid does the work. (See the Tone Bible, §6.)
6. **Fair death teaches.** Every death must, in hindsight, have been avoidable.
   The warnings were there. No random unavoidable kills.
7. **Low resolution, high finish.** ~22 rooms, ~3 systems. We do not add an open
   world, combat, or RPG stats. We polish what exists until it gleams.

---

## 1. Current state (honest assessment)

**Working:** map graph + pathfinding, movement, inventory, suit/toxic death,
cave trigger, monster boarding, BFS scanner, suspicion-driven monster AI,
same-room detection, hiding, distractions, repair → send → ending, restart.

**Thin / missing:**
- Prose is functional but rarely *frightening*. Rooms are static; the ship never
  changes after the creature boards.
- No `play` launcher; running the game is a paragraph of instructions.
- Sparse code comments at the genuinely tricky spots (AI, turn pipeline).
- No automated tests — every change is hand-verified.
- The monster is smart but doesn't *visibly learn*; the player can't feel its
  intelligence.
- Scanner is honest to a fault (no lag/uncertainty), so it leaks tension.
- No Sable NPC, no save/load, no first-encounter pacing beats.
- The "you let something in" moment — the emotional core — is one line and easy
  to miss.

---

## 2. The three phases

### Phase 1 — **Foundations & the Dread Pass** (v1.1) — ✅ DONE
*Low risk, highest atmosphere-per-line-of-code. Ship this first.*

**1.1 Dev ergonomics**
- [x] Add an executable **`play`** launcher at the repo root:
  ```sh
  #!/usr/bin/env bash
  # THE THIN AIR — launcher
  cd "$(dirname "$0")/thin_air_game" && exec python3 src/__main__.py
  ```
  `chmod +x play`. Document `./play` in the README as the one-liner to start.
- [x] Add **sparse, human comments** at the genuinely non-obvious code only
  (target ~1 short comment per crucial block, not line-by-line):
  - `game_state.advance_world()` — the 7-step turn pipeline order matters.
  - `game_state._resolve_same_room()` — the detection formula and why each term.
  - `game_state.shortest_path()` — why first-direction is recorded during BFS.
  - `game_state._choose_target()` / `_move_monster()` — target priority + speed.
  - `game_state._resolve_boarding()` — countdown + failsafe intent.
  - `parser.parse_command()` — the alias / filler / multiword normalization.
  Comments explain **why**, never restate the code.
- [x] Add a **pytest suite** (`thin_air_game/tests/`): parser aliases, map
  reachability, toxic death (human=2, synthetic=3), scanner direction/distance,
  monster boards after cave return, same-room kill, win requires all parts.
  Use a fixed RNG seed for determinism (`GameState.random_seed`).

**1.2 The Dread Pass (the heart of v1.1)**
- [x] **Dynamic room descriptions.** Each room gains *state variants* keyed to
  `game_phase` / flags. The ship is clean and humming pre-cave; after the
  creature boards it is *wrong*: peeled vent grilles, a smell, a sound that
  stops when you enter. Implement as `Room.describe(game_state)` returning the
  variant. Example (Central Corridor):
  - pre-cave: *"Low ceiling. Handrails. Old boot marks. The lights hum in pairs."*
  - monster aboard: *"The lights hum in pairs. One pair has stopped. The boot
    marks lead somewhere they didn't before."*
- [x] **Prose rewrite for dread** across all 22 rooms + key items, following the
  Tone Bible (§6). Terse, specific, present tense, the unsaid.
- [x] **The boarding beat.** Make the emotional core land. When the hatch seals
  after the cave, slow it down with a confirmed-pacing beat:
  ```
  The inner hatch cycles. Pressure equalizes.

  When it closes, something soft knocks once. Outside.

  Then inside.
  ```
  (Optionally a "press enter" gate on the biggest beats — see 1.3.)
- [x] **Sparse environmental storytelling** for the previous crew: the recorder
  log, the cracked helmet in Black Pool, scratch marks in Lower Hold, the slime
  on the landing gear (appears only *after* boarding). No lore dumps — fragments.
- [x] **Listen / scan flavor** expanded so quiet turns still breathe dread
  (distant settling, a drip, the fan that wasn't running before).

**1.3 Output rhythm**
- [x] Optional **typewriter pacing** for key beats (death, boarding, ending) —
  small per-character delay, skippable, off by default via `--fast`/env so tests
  and impatient players aren't punished.
- [x] Consistent **blank-line rhythm** and text wrapping to a sane width (~70).
- [x] **"Press enter"** gates only on the 3–4 biggest story beats. Used sparingly.

**Phase 1 Definition of Done:** `./play` launches; all rooms have a pre/post
variant; full prose pass merged; pytest green; a first-time player feels the
hatch-knock moment land.

---

### Phase 2 — **The Intelligence** (v1.2) — ✅ DONE
*Make the creature feel like it is thinking. This is what earns the
"Isolation" comparison.*

- [x] **Visible learning.** The monster adapts to the player's habits:
  - Reusing the **same hide spot** is already penalized internally — surface it:
    *"It goes to the cabinet first now."*
  - **Distraction fatigue:** each thrown-can trick raises a counter; past a
    threshold the creature stops chasing thrown sounds (*"It glances at the
    noise. It does not turn."*). Distractions become a scarce, real resource.
  - It **patrols toward your objective** late-game (camps Comms Hall during the
    final repair), not just toward your last sound.
- [x] **Line-of-sight / "it saw you" state.** If the monster enters your room
  while you're unhidden and you survive a distraction, set a `seen` memory so the
  scanner can deliver the spec's gut-punch line:
  ```
  > scan
  You lift the terminal.
  It is already looking at you.
  ```
- [x] **Vent ambushes, telegraphed.** When the monster takes a vent, the prior
  turn shows a sign in an *adjacent* room (*"The grille two rooms over is
  peeled outward."*). Vents are spice, not teleportation (cap usage).
- [x] **Scanner imperfection** (per design pillar #1):
  - One-turn **lag**: the scanner shows where it was, not where it is.
  - **Interference rooms** already scramble it (reactor/cave); add *intermittent
    dropouts* near the creature so a strong signal sometimes flickers to "lost".
  - Synthetic gets a *slightly* tighter read (already hooked; implement the diff).
- [x] **Sable, the synthetic NPC** (optional, one-shot heart):
  - Found in Crew Quarters or Maintenance Junction; activates after boarding.
  - Gives 1–2 sparse hints; can open one route; can **sacrifice itself once** to
    save the player from an otherwise-lethal same-room event. (Spec §17 prose.)
- [x] **State surfaced through prose, never numbers.** Audit every monster state
  (hunting/searching/investigating/feeding) for a distinct, sparse tell.

**Phase 2 DoD:** a playtester can describe, unprompted, a moment where "it
learned what I was doing." Scanner can lie/lag without ever feeling unfair.

---

### Phase 3 — **Polish & Persistence** (v1.3)
*The finish coat.*

- [ ] **Save / load** (single JSON snapshot of GameState; `save`/`load`
  commands). Enables longer sessions and recovery.
- [ ] **Optional ANSI color**, behind a `--color` flag / `NO_COLOR` respect:
  red for toxic warnings, dim for ambient, a single accent for the scanner.
  Restrained — pillar #7. Never rainbow.
- [ ] **ASCII map** command upgrade: show visited rooms in a small connected
  layout, not just a list. Never reveal unvisited rooms.
- [ ] **Balance pass / full playtest** to the 30-minute target:
  - Tune `board_countdown`, aggression curve, and the detection formula so the
    cave path is winnable with careful play but punishes the careless.
  - Verify no softlocks (e.g. creature permanently camping the only door — confirm
    distraction counterplay always exists).
  - First-timers die 1–2 times; a careful second run wins.
- [ ] **Docs:** finalize README (commands, install, spoiler-free intro), a short
  CONTRIBUTING note, and a `--help` CLI flag.
- [ ] **Ending polish:** tighten the relay-station sting; ensure the tragedy
  (the warning *invites* them) reads cold and clean.

**Phase 3 DoD:** a stranger can `./play`, finish in ~30 min, and the ending
lands without explanation.

---

## 3. System-by-system improvement notes

**Sound** — keep the 0–4 model. Refine modifiers: reactor *masks* small sounds
(done), cargo *echoes* (sound +1 for take/drop there), galley *clatters* (cans
loud). Running and the final repair remain the loud mistakes.

**Scanner** — the most important *feel* tool. Lag + interference + dropouts give
uncertainty without unfairness. The status-line `Motion:` summary stays; `scan`
gives the detailed read at the cost of a quiet turn.

**Hiding** — quality + reuse penalty exist. Add `max_safe_turns` so *staying*
hidden too long escalates danger (pillar #3: stillness is not safety). Surface
reuse to the player in prose.

**Distractions** — can (sound) + flare (sound + light). Limited supply. Fatigue
counter (Phase 2). Throwing *away from* the creature is the skill.

**Monster** — the model is good; the gap is *expression*. Phase 2 is mostly
about making the existing intelligence *legible* to the player through sparse
signs and the scanner.

---

## 4. The Tone Bible (how we write dread)

Rules for every line of prose we add:

- **Second person, present tense.** "You hear it" not "There was a sound."
- **Concrete over abstract.** "The grille is peeled outward" beats "It seems
  dangerous." Name the object; let the reader feel the threat.
- **The unsaid.** Never describe the creature fully. Hands, weight, wetness,
  wrongness — fragments only. It is never named by the narrator.
- **Short lines, hard stops.** Fragments are allowed. "Then inside." A period is
  a held breath.
- **Repetition with variation.** A returning detail that has *changed* is the
  cheapest, strongest dread (the boot marks; the hum; the stopped fan).
- **Restraint at peaks.** The biggest moment gets the *fewest* words.

Reference voice samples (target quality bar):

```
Something taps once in the vent.
```
```
A handprint, high on the wall. Too many fingers, and too high.
```
```
The scanner shows motion west. Then north. Then west again.
It is learning the corridors.
```
```
You make it a few more steps.
That is all.
```

---

## 5. Sequencing & risk

- **Do Phase 1 first.** It is low-risk (mostly content + ergonomics) and delivers
  most of the atmospheric payoff. Tests added here protect Phases 2–3.
- **Phase 2 is the riskiest** (AI behavior changes can introduce unfair deaths) —
  the Phase 1 test suite + a fixed seed make it safe to iterate.
- **Phase 3 is additive** (save/load, color, map) and can ship piecemeal.

Each checkbox is one small commit. Test before commit. Game stays playable at
every step.

## 6. Non-goals (so the knife stays sharp)

No combat. No open world. No RPG leveling. No procedural generation. No
multiplayer. No graphics beyond clean terminal text and optional restrained
color. No lore database. We are making one sharp, lethal, 30-minute knife.
