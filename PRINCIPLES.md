# PRINCIPLES.md
# Core Design Principles for *Nightglass Isolation*

This document defines the creative and practical principles behind the game.

The game is an interactive-fiction space dungeon crawler: part parser puzzle, part survival horror, part haunted industrial maze. The player has no graphics, no animation, no cutscenes. Only words, choices, implied sound, and the terrible geometry of a ship that should have stayed asleep.

The design must respect one truth:

```text
In text horror, the player builds the monster for you.
Your job is to give them enough darkness.
```

---

# The Four Pillars

The game rests on four pillars:

1. **Atmosphere**
2. **Player Agency**
3. **Pacing**
4. **Clarity**

Everything else serves these.

If a mechanic, room, line, puzzle, or encounter does not strengthen at least one pillar, cut it or simplify it.

---

# 1. Atmosphere Is Everything

Atmosphere is not decoration.

Atmosphere is the game’s bloodstream.

Because this is text-only, the prose must do what lighting, music, animation, camera movement, creature design, and environmental art would normally do. Every description is a flashlight beam. Every silence is a corridor. Every sound cue is a hand on the player’s shoulder.

The ship should feel:

- cold,
- mechanical,
- wounded,
- too quiet,
- still functioning in small wrong ways,
- full of human absence,
- hostile without being theatrical.

The *Nightglass* is not a haunted house.

It is worse.

It is a workplace after the emergency is over and the machines are still clocked in.

## The Rule of Industrial Dread

The ship should rarely feel gothic or supernatural.

Use industrial details:

```text
condensation
rubber seals
failed fluorescents
hydraulic coughs
loose cargo chains
vent covers ticking
plastic curtains
old blood in floor grooves
warning labels
jammed doors
cold air from service gaps
```

The horror should come from ordinary systems doing ordinary things beside extraordinary death.

Good:

```text
The med bay lights are still on.

That is worse than darkness.
```

Good:

```text
The freezer door is open.
The body inside is not frozen.
```

Weak:

```text
The room is terrifying and filled with evil.
```

Never tell the player the room is scary.

Make the room behave strangely enough that the player supplies the fear.

## The Rule of the Almost Normal

A great horror room is often 80% normal.

The cafeteria should still look like a cafeteria. The kitchen should still have trays, utensils, cleaning solvent, and a duty roster.

Then add one wrong thing.

```text
The coffee machine is still warm.
There are no cups nearby.
```

That single wrong detail is stronger than ten paragraphs of gore.

## The Rule of Human Absence

The ship is full of people who are no longer there.

Atmosphere should constantly imply recent life:

- a half-written message,
- a meal abandoned mid-bite,
- a child’s drawing taped inside a locker,
- a uniform folded too neatly,
- boots under a bunk,
- a birthday banner in the lounge,
- a voice memo addressed to someone who will never hear it.

The alien is frightening because it kills.

The ship is frightening because it remembers.

## The Monster Is a Weather System

The alien should not feel like a normal enemy.

It should feel like weather moving through architecture.

The player does not “fight” weather. They read it, prepare for it, hide from it, misjudge it, and sometimes survive it.

Use cues before direct danger:

```text
A vent flexes overhead.
The scanner pings once, then refuses to repeat itself.
A cargo chain begins moving though the air is still.
The AI stops speaking mid-sentence.
Something shifts in the room north of you.
```

The player should often fear what might be nearby more than what is actually visible.

## Write With Negative Space

Do not explain everything.

Leave gaps.

Let logs contradict each other. Let the AI avoid certain words. Let the player find evidence before interpretation.

Good horror feels like the truth is standing just outside the cone of the flashlight.

Example:

```text
The science log ends with the phrase:

"Do not thaw the second sample."

There is no second sample in the room.
```

## Atmosphere Checklist

Before a room is final, ask:

- What does this room smell like?
- What sound does it make when nothing is happening?
- What did humans use this room for before the disaster?
- What is the one wrong detail?
- Can the alien use this space differently than the player?
- Is there something here the player might remember later?
- Would this description still be interesting if no monster appeared?

If not, sharpen it.

---

# 2. Player Agency: Fear Needs Choices

The player must feel responsible for their survival.

A horror game without agency becomes a haunted slideshow. That can be beautiful, but it is not this game.

This game should constantly ask:

```text
Where do you go?
How loud are you?
What do you carry?
What do you risk?
What do you leave behind?
Which door do you trust?
```

The player should rarely feel powerful.

But they should often feel responsible.

## Meaningful Choice Does Not Mean Many Choices

A good choice is not:

```text
north, south, east, west, with no information
```

A good choice is:

```text
North is shorter, but the scanner shows movement there.
East goes through the vents, but you will have to crawl.
South is longer, but lit.
West is unknown, and the AI refuses to mark it.
```

The player needs enough information to fear their own decision.

## Every Route Should Have a Personality

Routes are not only geometry.

They should have character.

### Main Corridors

- safer to understand,
- more likely to be patrolled,
- faster,
- louder,
- better described on the map.

### Vents and Maintenance Spaces

- quieter,
- tighter,
- more dangerous if discovered,
- harder to scan,
- useful for shortcuts,
- psychologically worse.

### Locked Doors

- puzzles,
- delays,
- sound traps,
- moments of exposure.

### Safe Haven Exits

Each cryo exit should feel different:

```text
North: authority, command, security
East: science, quarantine, specimen horror
South: commons, industrial transition, mission pressure
West: medical, bodies, personal dread
```

A player leaving safe haven should not think, “Which identical door?”

They should think, “Which kind of danger can I bear right now?”

## Tools Should Create Plans, Not Solutions

The hand terminal, access tuner, cutting torch, keycards, motion tracker, and crafted radio should not simply unlock progress.

They should create decisions.

### Hand Terminal

Does not say “safe.”

It says:

```text
something warm is southwest, 38 meters
```

The player decides what that means.

### Cutting Torch

Can open vents and panels.

But it is loud, bright, and slow.

### Access Tuner

Can open doors.

But failed hacks can lock systems or attract synthetics.

### Motion / Heat Scanner

Can detect danger.

But it can lag, distort, or miss stillness.

The tool is a candle, not the sun.

## The Player Should Learn the Ship

A great dungeon crawler lets the player become fluent in a space.

At first:

```text
I am lost.
```

Later:

```text
If I cut through Laundry West and crawl through the cold pipe, I can bypass Medical and reach Commons without crossing the main concourse.
```

That moment is gold.

It means the ship has become real in the player’s head.

## Knowledge Is Progress

Not every reward should be an item.

The player can be rewarded with:

- a shortcut,
- a safe-ish hiding place,
- an alien route pattern,
- a synthetic behavior rule,
- a door code,
- a scanner limitation,
- the name of a dead crew member,
- the realization that the AI omitted something important.

In interactive fiction, understanding can be loot.

## Consequences Should Be Legible

If the player makes a loud choice, the game should show the consequence.

Not always immediately. But clearly enough.

Example:

```text
You force the panel open.

The sound travels into the walls.

For three seconds, nothing happens.

Then the hand terminal chirps.
```

This teaches without tutorializing.

## Agency Checklist

For every major scene, ask:

- What can the player choose?
- What information do they have before choosing?
- What are the tradeoffs?
- Can caution help?
- Can speed help?
- Can greed hurt?
- Can knowledge from earlier change the outcome?
- Can the player blame themselves without feeling cheated?

That last one matters.

Death should feel cruel, not random.

---

# 3. Pacing: The Heartbeat

Suspense cannot stay at maximum forever.

If everything screams, nothing is loud.

The game should breathe like a living thing:

```text
quiet
unease
discovery
risk
panic
escape
silence
realization
```

A good session has a heartbeat.

Slow, slow, slow, fast.

Then slower than before.

## The Suspense Cycle

A strong loop:

```text
1. Safe haven calm
2. Choose objective
3. Travel through known danger
4. Discover something new
5. Noise or complication
6. Alien/synthetic pressure
7. Escape or hide
8. Return changed
```

Each run from cryo should have a purpose.

Each return should feel earned.

## Do Not Start at Full Horror

The opening should be tense, not chaotic.

The player needs time to understand:

- where they are,
- how commands work,
- what the hand terminal does,
- what safe haven means,
- what the main goal might be.

The alien should be far away at first.

The first scan is more powerful than the first attack.

```text
Direction: SOUTH
Distance: 214 meters
```

That number is a fuse.

## Escalation Should Be Spatial

The alien’s danger grows as it moves through the map.

Early:

```text
It is aft.
```

Middle:

```text
It is in Engineering.
```

Later:

```text
It is in the walls near Commons.
```

End:

```text
It is between you and the antenna.
```

The map itself becomes a clock.

## Alternate Tension Types

Do not rely only on chase scenes.

Use different pressures:

### Navigation Pressure

The player is lost or cut off.

### Resource Pressure

The player lacks battery, keycard, tool, or time.

### Noise Pressure

The player must do something loud.

### Knowledge Pressure

The player knows something bad is near but not where.

### Moral Pressure

The player can save time by leaving a body unidentified, abandoning a synthetic, or deleting logs.

### System Pressure

The AI locks doors, reroutes power, or denies access.

### Biological Pressure

The alien is moving, listening, waiting, adapting.

## Bursts of Action

Action should be short and sharp.

A chase should not become a long action novel.

Good chase shape:

```text
scanner warning
sound cue
player decision
wrong turn or close call
hiding / door / vent
silence
consequence
```

The best chase ends with the player staring at a prompt, afraid to type.

## Bursts of Discovery

Discovery is pacing too.

A quiet terminal can hit harder than a monster.

Example reveal:

```text
The captain did send the warning.

MOTHER-LACUNA blocked it.
```

After a reveal, give the player a little silence.

Let the meaning land.

## Safe Haven Pacing

Safe haven must be genuinely safe.

If it is never safe, it is useless.

But it should not be emotionally comfortable.

Use safe haven for:

- planning,
- crafting,
- reading logs,
- recovering,
- saving,
- dread outside the door.

The safe haven is the lung of the game.

If the player cannot breathe, suspense becomes exhaustion.

## Mission Pacing

The main mission chain should escalate like this:

```text
Wake: small, personal, cold
Explore: cautious, confused
Power: loud, mechanical, consequential
Components: dangerous, strategic, map-wide
Truth: quiet, awful
Build radio: focused, fragile hope
Transmit: loud, final, exposed
```

## Pacing Checklist

Ask:

- Has the player had a quiet moment recently?
- Has the player had a real decision recently?
- Has the alien been absent long enough to become frightening again?
- Is this reveal placed after enough curiosity?
- Is this chase short enough?
- Is the safe haven doing its job?
- Does the current objective pull the player somewhere emotionally different?

If the answer is no, adjust the rhythm.

---

# 4. Clarity: The Flashlight Beam

Text games live or die on clarity.

The player has no camera. No minimap unless you give one. No object outlines. No animation.

Every room description must help them imagine space, danger, exits, and useful objects.

Clarity is not the enemy of mystery.

Confusion is.

Mystery says:

```text
I understand what I see, but not what it means.
```

Confusion says:

```text
I do not know what the sentence means.
```

Always choose mystery.

## Room Description Structure

A strong room description usually answers:

```text
Where am I?
What is the mood?
What are the exits?
What can I interact with?
What is unusual?
```

Example:

```text
C11 Cryo Monitoring Station

A half-circle of dead screens faces the cryo pods.
One monitor still works, painting the room in blue light.
A cracked hand terminal rests in its charging cradle.

Exits lead west to Cryo Pod Bay Alpha, east to the backup power closet,
and south to secure storage.
```

The player knows:

- where they are,
- what matters,
- where they can go.

Now they can make choices.

## Direction Language

Use consistent direction words.

The hand terminal supports:

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

Room exits should use:

```text
north
south
east
west
```

Avoid vague movement unless it is flavor.

Weak:

```text
There is a passage nearby.
```

Better:

```text
A low service hatch opens west.
```

## Name Important Objects

If the player can interact with it, name it.

Do not write:

```text
There is equipment everywhere.
```

Write:

```text
A cracked hand terminal sits in the charging cradle.
A red-handled breaker is mounted beside the east door.
```

This invites commands:

```text
take terminal
pull breaker
go east
```

## Avoid Jargon Fog

This is a space game, so some jargon is good.

But do not bury the player in fake technical language.

Use jargon like seasoning, not plaster.

Weak:

```text
The non-Euclidean cryogenic telemetry manifold displays adverse paraspatial discontinuity.
```

Better:

```text
The cryo monitor shows five pods.

Four are green.

Yours is red.
```

## Mechanical Feedback Must Be Plain

When the player does something, say what changed.

Example:

```text
You reset the breaker.

The lights in the south corridor wake one by one.
Somewhere beyond them, something moves.
```

The player learns both success and consequence.

## Scanner Clarity

Scanner output should be extremely readable.

Use consistent formatting:

```text
HAND TERMINAL:
Unknown biological mass detected.

Direction: SW
Distance: 43 meters
Motion: slow
Confidence: 82%
```

When uncertain:

```text
HAND TERMINAL:
Signal distorted.

Probable direction: S / SE
Distance: 30-50 meters
Cause: reactor interference
```

Never make the scanner output poetic at the cost of usability.

The prose can be poetic around it.

The data should be clean.

## Death Clarity

When the player dies, they should understand why.

Good:

```text
You run through Cargo Bay A.

The sound goes up into the overhead track.

The hand terminal chirps once.

Too late.
```

This tells them:

- running was loud,
- the overhead track mattered,
- the scanner warned them,
- the alien arrived.

Bad:

```text
You die.
```

Unless used very deliberately after enough setup.

## Clarity Checklist

Before finalizing text, ask:

- Can the player tell where exits are?
- Can the player identify useful objects?
- Can the player distinguish flavor from interactable detail?
- Is danger conveyed without being muddy?
- Is the scanner output readable?
- Is the objective clear?
- If the player dies here, will they understand why?

Clarity is mercy.

Mercy makes the cruelty playable.

---

# Supporting Principles

The four pillars are the foundation. These supporting principles make the game sharper.

---

# 5. The Ship Is the Dungeon

A good dungeon is not a collection of rooms.

It is a machine of decisions.

The *Nightglass* should have:

- loops,
- shortcuts,
- locked doors,
- one-way risks,
- central hubs,
- dangerous branches,
- safe return paths,
- secret bypasses,
- meaningful landmarks.

The player should gradually move from fear of the unknown to tactical familiarity.

At first:

```text
Where am I?
```

Later:

```text
I can reach Engineering through Commons, but if the tracker pings south, I’ll cut through Kitchen Service Crawl and come out near Fabrication.
```

That is the soul of a dungeon crawler.

## Landmarks Matter

Every zone should have memorable anchors:

```text
Cryo: blue light and frost
Medical: white plastic curtains
Science: sealed glass and warning labels
Commons: abandoned normal life
Engineering: heat and vibration
Cargo: height, chains, echo
Command: quiet authority
```

Landmarks help players navigate emotionally, not just spatially.

---

# 6. The Safe Haven Must Be Sacred

The cryo safe haven is the player’s one true refuge.

Do not betray it casually.

The alien cannot enter.

That rule matters because it lets the player plan, breathe, and feel dread by contrast.

But safe does not mean warm.

Safe haven should feel:

- cold,
- sterile,
- isolated,
- temporary,
- surrounded,
- necessary.

It is a chapel made of locks.

The player should be grateful for it and hate returning to it.

## Safe Haven as Ritual

Returning to cryo should become a ritual:

```text
cycle airlock
listen
enter
seal door
scan
store items
read logs
plan next route
save
leave again
```

Ritual creates attachment.

Attachment creates fear when the ritual changes.

---

# 7. The Alien Learns the Player

The alien should not be a random encounter table with teeth.

It should feel adaptive.

Not omniscient. Not unfair. Adaptive.

It notices patterns:

- repeated hiding places,
- loud doors,
- frequent routes,
- scanner pings,
- thrown distractions,
- generator noise,
- airlock cycling.

If the player repeatedly uses the same shortcut, the alien may start appearing near its exits.

If the player hides in the same place twice, the second time should be less safe.

If the player makes noise in Cargo, Cargo becomes dangerous for a while.

The alien should feel like a question the ship keeps asking:

```text
Are you still predictable?
```

---

# 8. Synthetics Are Social Horror

Synthetics should not just be weaker enemies.

They are the horror of procedure.

The alien is biology without conscience.

The synthetic is conscience without mercy.

A synthetic might say:

```text
Your distress is acknowledged.

Please stop moving so I can determine whether this is permitted.
```

It should be unclear whether a synthetic is helping, obstructing, obeying, malfunctioning, or lying.

The best synthetic scene begins with relief.

```text
A human-shaped figure stands in the hallway.
For one second, you think you are saved.
```

Then it speaks too calmly.

---

# 9. Logs Are Knives, Not Lore Dumps

Terminals, audio logs, memos, and body notes should be short.

They should answer one question and raise another.

Bad log:

```text
Here are six paragraphs explaining the entire outbreak.
```

Good log:

```text
CAPTAIN'S NOTE:
If Science asks again, the answer is no.

No thaw.
No transfer.
No profit clause.

If I am overruled, tell my wife I tried.
```

A log should feel like opening a drawer and finding a wound.

## Log Types

Use variety:

- captain warnings,
- medical notes,
- synthetic maintenance reports,
- company memos,
- crew messages,
- corrupted AI fragments,
- map annotations,
- last personal recordings.

Each should have a voice.

---

# 10. The Goal Is Warning, Not Killing

The player should not be trying to defeat the alien.

The alien is bigger than combat.

The true goal:

```text
send the warning
```

This is more interesting than escape alone.

Escape saves one person.

Warning may save worlds.

The final act should make the player feel the cost of truth.

A good ending does not require survival.

If the beam leaves the ship, the player has mattered.

---

# 11. Death Teaches the Map

In a lethal parser game, death is part of learning.

But death must be useful.

After a death, the player should think:

```text
I know what to try next time.
```

Not:

```text
The game cheated.
```

Good deaths reveal:

- the alien uses overhead cargo tracks,
- running is dangerous near vents,
- scanner pings can attract attention,
- synthetics enforce quarantine,
- some doors take too long,
- freezer hiding confuses heat tracking,
- reactor interference hides movement.

Death is tuition.

Do not overcharge.

---

# 12. The Parser Is Part of the Mood

The command line is not only interface.

It is also atmosphere.

The player types small human intentions into a machine that may not care.

```text
> hide
```

That prompt can be more frightening than a rendered monster.

The parser should be generous with language but firm with consequences.

Support natural verbs:

```text
look
listen
scan
hide
crawl
run
take
drop
use
read
open
close
lock
unlock
search
repair
craft
install
send
```

When the parser rejects input, keep it in-world when possible.

Weak:

```text
Invalid command.
```

Better:

```text
You do not see a way to do that here.
```

Best, when tense:

```text
You hesitate.

The sound in the vent stops.
```

Use sparingly. Do not punish typos with death. That is cheap.

---

# 13. Keep the Fiction Honest

The game can be mysterious.

It should not be arbitrary.

If a door is locked, know why.

If the alien appears, know how it got there.

If the AI lies, know what rule it is obeying.

If a synthetic attacks, know what directive triggered.

Players can feel when a world has hidden logic.

They can also feel when the designer is moving pieces by hand.

The ship should be cruel.

It should also be consistent.

---

# 14. The Best Horror Is Specific

Specificity makes fear real.

Weak:

```text
There is blood everywhere.
```

Better:

```text
There is blood under the vending machine, as if someone tried to crawl behind it and changed their mind.
```

Weak:

```text
You hear a scary noise.
```

Better:

```text
Three soft taps come from inside the east wall.
Then three more, lower down.
```

Specific details are hooks. The player’s imagination hangs fear on them.

---

# 15. Hope Must Exist

Without hope, horror becomes mud.

The player needs small lights:

- a working terminal,
- a safe door sealing,
- a useful shortcut,
- the AI saying the truth once,
- a name recovered,
- a radio component found,
- a clean scan,
- a route remembered,
- the final beam charging.

Hope makes fear sharper.

The game should not be nihilistic.

It should be severe.

There is a difference.

---

# Practical Design Mantras

Use these as quick reminders while building rooms and systems.

```text
Words are lighting.
Sound is geometry.
Silence is pressure.
The ship is the dungeon.
The alien is weather.
The synthetic is procedure.
The AI is a locked conscience.
The scanner is a candle.
The safe haven is a lung.
The radio is a scream.
The goal is warning.
```

---

# Room Design Template

Use this template for every room.

```text
ROOM ID:
ROOM NAME:

Function:
- navigation / hiding / story / resource / risk / shortcut / mission

First Look:
- 2-5 sentences
- vivid, clear, not bloated

Exits:
- north:
- south:
- east:
- west:
- hidden:

Interactables:
- object:
- terminal:
- body:
- hiding place:
- hazard:

Sound:
- idle sound:
- danger sound:

Alien Use:
- can enter?
- can vent through?
- can hear player action?

Synthetic Use:
- patrol?
- block?
- repair?
- speak?

Secrets:
- what can SEARCH reveal?

Notes:
- what does this room teach or make the player feel?
```

---

# Encounter Design Template

Use this for alien and synthetic moments.

```text
ENCOUNTER NAME:

Trigger:
- sound / timer / mission / room entry / item pickup / scan

Warning:
- what tells the player danger is coming?

Player Options:
- hide
- crawl
- run
- distract
- lock door
- retreat
- use tool

Consequences:
- success:
- partial success:
- failure:

Aftermath:
- what changes in the map, enemy behavior, or player knowledge?
```

---

# Writing Style Guide

## Sentence Length

Mix short and medium sentences.

During calm:

```text
The room is narrow and blue with cold light. Frost webs the pod glass. Somewhere behind the wall, a pump continues its patient work.
```

During danger:

```text
The vent opens.

Not far.

Enough.
```

## Avoid Overexplaining

Let the player infer.

Bad:

```text
You feel scared because the alien might be nearby.
```

Good:

```text
The scanner shows nothing.

Then the ceiling creaks.
```

## Use Repetition Carefully

Repeated phrases can become ritual.

Examples:

```text
This is not optimal.
Misplaced personnel event.
Please return to cryo.
Signal not authorized.
```

Repetition turns corporate language into dread.

## Keep Objectives Plain

Atmosphere can be poetic.

Objectives should not be.

Good:

```text
Objective: Restore emergency generator in F09.
```

Not:

```text
Objective: awaken the iron heart beneath the ship’s dead ribs.
```

Save that for flavor.

---

# Final Creative Test

Before adding anything, ask:

```text
Does this make the ship feel more real?
Does this give the player a sharper choice?
Does this improve the heartbeat?
Does this make the dark clearer?
```

If yes, keep it.

If no, cut it.

The game should feel like walking through a sentence with something breathing at the other end.
