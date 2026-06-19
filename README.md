# Kepler Isolation

*A short, lethal terminal horror game. Zork's parser by way of industrial space dread.*

---

You wake inside a cryo pod aboard the **USCSS Nightglass**.

The room is half-dark. The ship is quiet in the wrong way. An onboard AI speaks from the cryo deck, calm enough to make everything worse. Nearby, a cracked hand terminal shows motion, heat, direction, and distance.

Something is alive on the ship.

It is not crew.

Your goal is simple: restore enough power, build a faster-than-light emergency radio, reach long-range antenna control, and send a warning before anyone comes looking for the ship.

The cave has already been explored.  
The mistake has already been made.  
Now the only thing left to do is make sure it does not reach Earth.

---

## What kind of game is this?

**Kepler Isolation** is a text-only interactive-fiction survival horror game.

Think:

- parser commands,
- a single-deck ship map,
- vents and maintenance crawls,
- a scanner that helps but never comforts,
- a safe cryo haven,
- random bodies,
- uncertain synthetics,
- one alien creature moving through the same world you are.

The monster is not a scripted jump scare. It moves. It listens. It learns.

---

## The four design principles

### Atmosphere

The words are the lighting.

Every room should feel like a flashlight beam cutting through dark: clear, vivid, tense. The ship should feel industrial, cold, damaged, and recently abandoned.

### Player agency

Fear works best when the player chooses.

Run or crawl. Use the hallway or the vent. Carry the heavy tool or leave space for the radio part. Trust the AI or check the terminal yourself.

The player should rarely feel powerful, but they should often feel responsible.

### Pacing

Suspense needs a heartbeat.

Quiet exploration. A bad sound. A discovery. A burst of panic. A return to cryo. A new plan.

The game should breathe so the fear has somewhere to go.

### Clarity

Text has no camera.

Room descriptions, exits, items, scanner readings, and objectives must be readable at a glance. Mystery is good. Confusion is not.

The player should know what they see, even when they do not yet understand what it means.

---

## How to play

The game reads typed commands.

Common commands:

```text
look
go north
go south
go east
go west
scan
listen
hide
crawl east
run north
take hand terminal
read terminal
search body
open door
use keycard
use access tuner on door
repair generator
craft radio
send warning
inventory
map
save
load
help
```

Short directions work too:

```text
n
s
e
w
```

The hand terminal can report directions like:

```text
N
NE
E
SE
S
SW
W
NW
```

Example scan:

```text
HAND TERMINAL:
Unknown biological mass detected.

Direction: SOUTHWEST
Distance: 84 meters
Motion: slow
Confidence: 76%
```

Trust it.

Not blindly.

---

## The ship

The game takes place on one deck of the **USCSS Nightglass**.

Major areas include:

- Cryo Safe Haven
- Medical
- Science
- Habitation
- Commons
- Security
- Command
- Industrial Operations
- Engineering
- Cargo
- Docking
- Maintenance and vent routes

The cryo area is your only true safe haven. The alien cannot enter it.

That does not mean it cannot wait outside.

---

## Character paths

At the start, choose one of three paths:

### Crew

You know the ship, or at least you think you do. The dead are not strangers.

### Synthetic

You wake with gaps in memory and systems you do not fully control. The other synthetics may know what you are before you do.

### Contractor

You were not crew. You were hired for a job, stored in cryo, and forgotten until forgetting you became useful.

Each path changes context, access, dialogue, and what the truth costs.

---

## Main objective

To win, you must:

1. wake in cryo,
2. find and use the hand terminal,
3. restore emergency power,
4. collect radio components,
5. build an improvised FTL emergency radio,
6. override containment restrictions,
7. reach long-range antenna control,
8. send the warning.

Survival is optional.

The warning is not.

---

## Survival tips

- Walking is safer than running.
- Hiding works, but not forever.
- Vents are shortcuts and traps.
- The scanner gives information, not safety.
- Synthetics are not automatically allies.
- The safe haven is for planning, not winning.
- Noise changes the ship.
- If you die, learn the route.

---

## Project tone

The game should feel like this:

```text
The ship is small enough to learn.
The walls are still full of teeth.
```

Good luck.

Stay quiet.
