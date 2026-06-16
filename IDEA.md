---

# INSTRUCTIONS FOR AGENT DEVELOPMENT

## CORE MISSION

Build **THE THIN AIR**: a complete, polished, playable terminal text adventure game.

**Core loop:** Player lands on toxic planet → explores cave → returns with unwanted passenger → must repair transmitter and send warning to win.

**Target:** 30-minute playthrough, fully playable, excellent terminal UI, thoroughly tested.

---

## CRITICAL SUCCESS FACTORS

1. **Terminal UI is first-class** - Use clean formatting, clear status lines, readable descriptions. This is more important than feature completeness. Players should feel like they're using a modern CLI tool, not a 1980s game.

2. **200+ iterations with git commits** - **This is non-negotiable.** Work in small cycles and commit after each iteration:
   - Fix one thing, test it, commit (one commit)
   - Add one feature, test it, commit
   - Polish one interaction, test it, commit
   - Do not build everything at once
   - **You should have 200+ commits by the time you're done**
   - Each commit should be atomic and testable
   - Use clear commit messages describing what changed

3. **Creative improvements** - Do not blindly follow this spec. Think about:
   - What UI touches make scanning feel visceral?
   - How can sound be visualized to feel urgent?
   - What room descriptions make exploration genuinely scary?
   - Can hiding feel fair but desperate?
   - How should the monster's presence be telegraphed subtly?

4. **Complete and documented** - By the end:
   - Fully playable from start to win/death
   - In-game help system with clear affordances
   - README explaining how to play
   - Code that's clean and commented where needed
   - 200+ commits showing iterative progress

---

## DEVELOPMENT PHASES (200+ Iterations)

### Phase 1-2: Core Loop (iterations 1-30)
- Rooms and movement working
- Inventory system functional
- Basic UI rendering
- Each small improvement: one commit

### Phase 3-4: Terminal UI Polish (iterations 31-70)
- Status bar clean and informative
- Room descriptions readable
- Exits and items clearly displayed
- Help system in place
- Iterative UI refinement with visual feedback

### Phase 5-6: Core Mechanics (iterations 71-110)
- Suit and toxic atmosphere working
- Scanner system functional
- Sound system with visual feedback
- Cave trigger event
- Bug fixes and edge case handling

### Phase 7-8: Monster & Pressure (iterations 111-150)
- Monster AI moves through map
- Sound affects monster behavior
- Hiding mechanics work
- Transmitter repair sequence
- Monster behavior tuning

### Phase 9+: Polish & Final (iterations 151-200+)
- Death messages feel good
- Ending is impactful
- Edge cases handled
- Game is genuinely fun to play
- Final balance tuning
- Documentation and README

**Each iteration = one commit. 200+ commits by completion.**

---

## WHY 200+ ITERATIONS?

Small, committed steps compound into polish. A game built in 200 small iterations will have:
- Better thought-out UI (each interaction tuned)
- Fewer bugs (testing after every change)
- Clearer codebase (small changes, not monolithic rewrites)
- Visible progress history (200 commits = proof of work)
- Better game feel (iterative refinement, not one-shot implementation)

**200 iterations is not excessive. It's the difference between "works" and "feels good."**

## YOU HAVE CREATIVE FREEDOM

Change anything in this spec if the game will be better for it:
- Adjust room layout if it flows better
- Rewrite descriptions to be scarier
- Simplify monster behavior if it's clearer
- Add flavor text where it helps
- Remove features if they clutter the experience

The goal is a **sharp, focused, genuinely good game** — not blind adherence to a spec.

## GIT WORKFLOW REQUIREMENTS

1. **Initialize git repo** if not already initialized
2. **Commit after each iteration** - use `git commit -m "description of change"`
3. **Keep commits atomic** - one logical change per commit
4. **Test before committing** - game should be playable (or fix should be documented)
5. **Use clear messages** - future-you will read these to understand the game's evolution
6. **Push/sync regularly** - maintain a remote backup

By iteration 200, `git log` should tell the complete story of how the game was built.

---

## GIT COMMITS ARE YOUR MILESTONE TRACKER

- **Commit after every iteration.** One iteration = one testable change = one commit.
- Use clear commit messages: "Add room north exit", "Fix sound calculation", "Polish UI spacing"
- Each commit should leave the game in a playable state (or clearly document why not).
- Track progress by counting commits: `git log --oneline | wc -l`
- Target: **200+ commits by completion**

## REPORT PROGRESS LIKE THIS

After ~30-50 iterations (30-50 commits):
- ✅ What's working well
- ⚠️ What needs work  
- 🔄 Next 30-50 iterations will focus on...
- 📊 Current commit count (should be ~30-50)

After ~100 iterations (100 commits):
- Halfway through development
- Game should be substantially playable
- Core mechanics in place
- Heavy UI/UX iteration ongoing

After ~150 iterations (150 commits):
- Game is feature-complete
- Monster AI working
- Death/win sequences implemented
- Final polish phase beginning

At ~200+ iterations (200+ commits):
- Game is complete and polished
- All acceptance criteria met
- Every change tracked in git history
- Ready to ship

---

# DETAILED SPECIFICATION (Reference Material Below)

You are building a complete terminal-based text adventure game called **THE THIN AIR**.

It is a short psychological sci-fi horror game inspired by the feel of classic parser adventures like Zork, combined with the tension of a stalking predator survival game.

The final result should be playable in a terminal, comfortable to use, and finishable in about 30 minutes.

The game must be text-only.

Do not use graphics beyond clean terminal formatting, optional ASCII panels, simple dividers, and possibly an ASCII map.

The game should feel modern and smooth, like a good CLI tool: fast, readable, forgiving, and clear.

Please don't stop - continue to develop, polish, explore, extend. Just keep improving it, continue to work and work like an open source developer. Perfect it!

---

## 1. Core Game Summary

The player lands on a toxic planet after receiving a distress signal from a cave.

They must wear an EVA suit before going outside.

If they go outside without the suit, the atmosphere kills them in two moves.

They explore the cave and return to the ship.

They do not realize they have let an intelligent organism inside.

After that, the monster moves autonomously through the ship, tracking sound, searching rooms, using vents, and moving toward the player with imperfect but frightening intelligence.

The player must collect repair parts from around the ship, reach Communications, repair the transmitter, and send a warning to Farland-Guttenber headquarters:

> Do not come here.

The player wins when the warning is sent.

The ending reveals that headquarters is now more interested in the planet because of the warning.

---

## 2. Required Deliverables

Build a playable terminal game with:

1. Character creation:
   - name
   - gender
   - type: human crewmember, synthetic, or contract specialist

2. Parser command system:
   - movement
   - looking/examining
   - taking/dropping items
   - inventory
   - wearing/removing suit
   - scanning
   - opening/closing
   - repairing/installing
   - hiding/crawling/running/waiting
   - reading
   - throwing distractions
   - help/map commands

3. Real map model:
   - ship rooms
   - surface rooms
   - cave rooms
   - graph-based exits
   - monster traverses the same graph

4. Inventory system:
   - portable items
   - worn items
   - repair parts
   - consumables
   - readable logs

5. EVA suit and toxic atmosphere:
   - outside without suit causes death in two moves
   - clear warnings before death
   - synthetic may have slightly different flavor but still cannot ignore the hazard indefinitely

6. Sound system:
   - every action has a sound cost
   - visible sound indicator
   - sound affects monster behavior
   - loud/violent sounds attract the monster fast

7. Hand terminal / scanner:
   - found in first 2-3 moves
   - reports monster relative direction and distance
   - distance measured in map moves
   - direction is N/S/E/W/etc. based on shortest path
   - same room is reported as "here" or equivalent
   - scanner may have interference in some rooms

8. Monster AI:
   - dormant before trigger
   - boards after cave return, or eventually enters if player refuses to leave ship
   - has real room position
   - uses pathfinding
   - responds to sound
   - searches
   - uses vents
   - has suspicion memory
   - biased toward player but not omniscient
   - can be temporarily distracted
   - can kill player if same room and player is exposed

9. Hiding system:
   - temporary only
   - each hiding spot has quality
   - repeated hiding becomes less safe
   - staying still increases danger

10. Main repair objective:
    - communications damaged
    - required parts:
      - power coupler
      - signal relay
      - antenna key
    - parts placed around ship
    - final repair creates sound and attracts monster
    - player sends warning to win

11. Ending:
    - message sent
    - cut to Farland-Guttenber receiving station
    - short tragic conversation
    - headquarters decides to come anyway

12. Comfortable terminal UI:
    - status area
    - location
    - sound indicator
    - suit status
    - scanner summary if terminal owned
    - concise room description
    - exits
    - visible prompt
    - helpful errors
    - command aliases
    - optional map

---

## 3. Recommended Tech Direction

Use any suitable terminal-friendly stack.

Recommended choices:

### Python

Good for rapid implementation.

Possible libraries:

- `rich` for terminal formatting
- `prompt_toolkit` for command history/autocomplete
- standard library for game loop and data models

### TypeScript / Node.js

Good for modern CLI feel.

Possible libraries:

- `ink` if building React-like terminal UI
- `enquirer` or `prompts` for setup
- `chalk` for simple styling
- `readline` for input

### Ruby

Good for clean parser/game object modeling.

Possible libraries:

- standard `readline`
- simple ANSI formatting

Pick one stack and complete the game.

Do not over-engineer.

Prioritize a working, enjoyable vertical slice over architecture theater.

---

## 4. Game Feel Requirements

The game must be:

- terse
- readable
- tense
- fair
- fast
- replayable
- small enough to finish

The writing should be brief.

Avoid long paragraphs.

Avoid explaining too much.

Room descriptions should be short.

Example:

```text
Central Corridor

Low ceiling. Handrails. Old boot marks.
The lights hum in pairs.

Exits: north, east, south, west
```

Monster signs should be sparse:

```text
Something taps once in the vent.
```

Death should be short:

```text
You make it four steps.
That is all.
```

---

## 5. Main Data Models

Implement these or close equivalents.

### GameState

Fields:

- player
- rooms
- items
- current_room_id
- inventory
- worn_items
- turn_count
- game_phase
- monster
- sound_level
- last_action_sound
- flags
- visited_rooms
- death_state
- win_state
- message_log
- random_seed

Game phases:

- `intro`
- `pre_cave`
- `outside`
- `cave_triggered`
- `returned_to_ship`
- `monster_aboard`
- `final_repair`
- `won`
- `dead`

### Player

Fields:

- name
- gender
- type
- health
- suit_worn
- outside_exposure_turns
- hidden
- hidden_spot
- last_room_id
- stayed_turns_in_room
- panic_level, optional
- has_terminal

Player types:

- `human`
- `synthetic`
- `contract_specialist`

### Room

Fields:

- id
- name
- description
- exits: dict direction -> room_id
- items
- hidden_items
- hazards
- hiding_spots
- monster_allowed
- scanner_interference
- ambient_sound
- visited
- dynamic_description_flags
- vent_exits, optional

### Item

Fields:

- id
- name
- aliases
- description
- portable
- wearable
- worn
- readable_text
- use_effect
- install_target
- sound_on_use
- required_for_win

### Monster

Fields:

- active
- phase
- current_room_id
- state
- target_room_id
- last_heard_room_id
- last_seen_room_id
- suspicion_by_room
- turns_since_seen
- turns_since_heard
- movement_cooldown
- aggression
- rooms_checked_recently
- known_hiding_spots
- distracted_until_turn
- can_use_vents

Monster states:

- `dormant`
- `following`
- `aboard`
- `investigating`
- `hunting`
- `searching`
- `same_room`
- `attacking`
- `feeding`

---

## 6. Map Implementation

Represent the map as a graph.

Each room must have explicit exits.

The monster must move through this graph.

Do not fake monster proximity with random text only.

### Required Rooms

Ship:

1. cockpit
2. central_corridor
3. airlock
4. med_bay
5. crew_quarters
6. galley
7. storage
8. engineering_access
9. reactor_room
10. cargo_bay
11. lower_hold
12. maintenance_junction
13. ventral_service
14. observation
15. comms_hall
16. communications

Surface/cave:

17. surface
18. landing_gear
19. ridge
20. cave_mouth
21. signal_cave
22. black_pool

### Required Exit Graph

Use this graph unless there is a good reason to refine it.

```text
cockpit:
  south: central_corridor

central_corridor:
  north: cockpit
  east: airlock
  south: med_bay
  west: engineering_access

airlock:
  west: central_corridor
  out: surface

surface:
  in: airlock
  east: ridge
  south: landing_gear

landing_gear:
  north: surface

ridge:
  west: surface
  east: cave_mouth

cave_mouth:
  west: ridge
  down: signal_cave

signal_cave:
  up: cave_mouth
  east: black_pool

black_pool:
  west: signal_cave

med_bay:
  north: central_corridor
  east: crew_quarters

crew_quarters:
  west: med_bay
  south: galley

galley:
  north: crew_quarters
  west: storage

storage:
  east: galley
  south: cargo_bay
  west: engineering_access

engineering_access:
  east: central_corridor
  south: reactor_room
  west: storage

reactor_room:
  north: engineering_access

cargo_bay:
  north: storage
  east: maintenance_junction
  south: lower_hold

lower_hold:
  north: cargo_bay

maintenance_junction:
  west: cargo_bay
  east: comms_hall
  north: ventral_service

ventral_service:
  south: maintenance_junction
  east: observation

observation:
  west: ventral_service
  south: comms_hall

comms_hall:
  north: observation
  west: maintenance_junction
  east: communications

communications:
  west: comms_hall
```

### Monster Vent Shortcuts

Optional but recommended:

```text
airlock <-> ventral_service
cargo_bay <-> reactor_room
observation <-> central_corridor
med_bay <-> maintenance_junction
```

Monster can use vents only after it is aboard.

Vents should not be available to the player unless specifically implemented as crawl routes.

---

## 7. Item Placement

Required placements:

- hand terminal: cockpit
- EVA suit: airlock
- power coupler: storage
- signal relay: reactor_room
- antenna key: cargo_bay
- repair kit: maintenance_junction or engineering_access
- medkit: med_bay
- flare: storage or cargo_bay
- loose can: galley
- access card: crew_quarters
- recorder log: med_bay
- distress beacon: signal_cave

Optional:

- beacon fragment: lower_hold
- old helmet: black_pool
- corporate memo: cockpit or communications

---

## 8. Parser Requirements

Support simple verb-noun commands.

Examples:

```text
look
look around
examine console
x console
take terminal
get hand terminal
inventory
i
go north
north
n
open locker
take suit
wear suit
put on suit
remove suit
scan
use terminal
listen
wait
hide
hide under bunk
crawl west
run east
throw can east
read log
repair transmitter
install relay
use power coupler on transmitter
send warning
help
map
quit
restart
```

### Parser Behavior

- Normalize lowercase.
- Strip punctuation.
- Support aliases.
- Support directions directly.
- Support common filler words: `the`, `at`, `to`, `on`, `with`, `using`.
- Return helpful errors.
- Do not punish minor wording differences.
- Prefer intent recognition over strict syntax.

Example:

```text
> put on the eva suit

The seals close around your throat.
Suit pressure holds.
```

Bad input:

```text
> lick wall

No.
```

Unknown object:

```text
> take banana

You see no banana here.
```

Impossible command:

```text
> go north

No exit north.
```

---

## 9. Turn System

Every command is either:

- meta command
- observation command
- time-advancing command

Recommended:

### Does not advance time

- help
- map
- inventory
- look, optional
- quit
- restart

### Advances time quietly

- examine
- read
- scan
- take
- drop
- wear
- remove
- open/close quiet object
- hide

### Advances time normally

- movement
- use
- repair
- install
- throw
- crawl

### Advances time loudly

- run
- force
- shoot if implemented
- yell
- noisy repair
- opening stuck panel

After each time-advancing command:

1. Apply player action.
2. Compute sound.
3. Update room stay count.
4. Apply environmental hazards.
5. Update monster suspicion from sound.
6. Move/update monster.
7. Resolve same-room detection.
8. Render result.

---

## 10. Sound System

Implement sound as numeric and labeled.

Suggested numeric values:

```text
0 = silent
1 = quiet
2 = audible
3 = loud
4 = violent
```

Display labels:

- silent
- quiet
- audible
- loud
- violent

Base action sound:

```text
look: 0
inventory: 0
examine: 1
read: 1
scan: 1
take: 1
drop: 1 or 2 depending item
wear suit: 2
walk movement: 1
crawl movement: 0 or 1
run movement: 3
open normal door: 2
close normal door: 1
open stuck panel: 3
repair: 2 or 3
install part: 2
throw can: 3
flare: 3
yell: 4
shoot: 4
wait: 0
hide: 1
```

Ambient room modifiers:

- Reactor masks small sounds.
- Galley increases dropped/touched item noise.
- Cargo Bay echoes.
- Cave has no monster yet or limited monster behavior.

Monster response:

- sound 0: no new suspicion, but staying still risk continues
- sound 1: small suspicion if monster nearby
- sound 2: investigate
- sound 3: hunt
- sound 4: direct hunt, arrival likely in 2-3 turns

Visible UI:

```text
Sound: quiet
```

or:

```text
Sound: loud
```

---

## 11. Scanner System

The hand terminal should be obtainable early.

If player has terminal, status can show scanner summary.

The `scan` command should show more detail.

Scanner output depends on monster phase.

Before monster active:

```text
No internal motion detected.
```

After cave trigger but before aboard:

```text
MOTION: outside
DISTANCE: uncertain
SIGNAL: intermittent
```

After aboard:

```text
MOTION: west
DISTANCE: 4 moves
SIGNAL: intermittent
```

At 2 moves:

```text
MOTION: north
DISTANCE: 2 moves
SIGNAL: strong
```

At 1 move:

```text
MOTION: east
DISTANCE: 1 move
SIGNAL: strong
```

Same room:

```text
MOTION: here
DISTANCE: 0
SIGNAL: inside the room
```

If monster has line of sight or detects player:

```text
You lift the terminal.

It is already looking at you.
```

### Direction Calculation

Use shortest path from player room to monster room.

Direction is the first exit direction from player room along that path.

If multiple equal paths, use deterministic order:

```text
north, south, east, west, up, down, in, out
```

If scanner interference:

```text
MOTION: interference
DISTANCE: unknown
```

### Scanner Cost

Scanning should cost a quiet turn.

This means scanning is useful but not free.

---

## 12. Monster AI Detailed Design

The monster should feel smart but not unfair.

It should not always know the player’s exact location.

It should maintain suspicion scores.

### Suspicion

For each room, maintain a suspicion score.

When player makes sound:

```text
suspicion[current_room] += sound_value * multiplier
```

Multipliers:

- quiet: +1 if monster within 3 rooms, else +0
- audible: +3
- loud: +7
- violent: +12

Also increase adjacent rooms slightly:

```text
adjacent += floor(sound / 2)
```

When player moves:

- Add tiny suspicion to previous room.
- If running, add suspicion to both previous and new room.

When player stays too long:

- Every turn after 2 turns in same room adds suspicion.
- Hiding reduces immediate visibility but does not erase suspicion.

Suspicion decays slowly:

```text
score = max(0, score - 1) every few turns
```

### Monster Target Selection

Priority:

1. If violent/loud sound recently heard: target that room.
2. If saw player: target player room.
3. If same room but player hidden: search current room.
4. Highest suspicion room.
5. Patrol route.
6. Random adjacent room with bias toward player quadrant.

### Monster Movement

On each monster update:

- If distracted, move toward distraction or stay feeding.
- If hunting, move one room toward target by shortest path.
- If investigating, move one room toward target, sometimes pause.
- If searching, check adjacent suspicious rooms.
- If no target, patrol.

Aggression increases as game progresses:

- Before cave: dormant.
- After cave: low.
- After returning to ship: medium.
- After collecting 2 parts: high.
- During final repair: very high.

### Monster Speed

Default:

- Moves once per player turn when active.

But adjust:

- If far away and calm, may move every other turn.
- If hunting after loud sound, moves every turn.
- If final phase, may move every turn and use vents.
- If distracted/feeding, may pause for 1-3 turns.

### Vents

Monster may use vent shortcuts when:

- hunting
- final phase
- sound is loud/violent
- route through vent is shorter

Do not use vents constantly.

They are spice, not teleportation.

### Same-Room Detection

If monster enters player room:

- If player is not hidden: likely death.
- If player is hidden: roll/check against hiding quality.
- If player makes noise: death.
- If player waits repeatedly: death chance increases.
- If player crawls quietly away: possible survival.
- If player runs: likely death unless monster is distracted.

Possible detection formula:

```text
detection_chance =
  base_by_monster_state
  + sound_value * 25
  + same_room_turns * 15
  + reused_hide_spot_penalty
  - hiding_spot_quality
  - distraction_bonus
```

Do not rely only on randomness.

Use clear stateful pressure.

---

## 13. Hiding System

Implement hide spots in selected rooms.

Rooms with hide spots:

- med_bay: cabinet
- crew_quarters: under bunk
- cargo_bay: behind crates
- engineering_access: crawlspace
- communications: under console
- storage: shelving

Each hiding spot:

- quality: 20-60
- reuse_count
- max_safe_turns: 1-2
- description

Rules:

- `hide` uses best available spot in room.
- `hide behind crates` selects specific spot.
- Hiding sets player.hidden = true.
- Moving cancels hidden.
- Loud action cancels hidden.
- Waiting hidden after safe turns increases danger.
- Reusing same hide spot adds penalty.

Messages:

```text
You lower yourself behind the crates.
```

```text
The same hiding place feels smaller now.
```

```text
It checks the cabinet.
Slowly.
```

---

## 14. Toxic Atmosphere

Outside rooms:

- surface
- landing_gear
- ridge
- cave_mouth
- signal_cave
- black_pool

The cave may have toxic air too.

If player is not wearing suit:

Human/contract specialist:

- first outside move: severe warning
- second outside move: death

Synthetic:

- first outside move: warning
- second/third outside move: system failure warning
- shortly after: death/failure

If wearing suit:

- safe outside.
- Suit remains worn when returning unless removed.

If player removes suit outside:

- immediate warning and exposure count begins.

---

## 15. Game Events and Flags

Implement flags:

```text
has_terminal
suit_taken
suit_worn
went_outside
entered_cave
examined_beacon
cave_triggered
returned_after_cave
monster_boarded
saw_window_creature
comms_damaged_known
has_power_coupler
has_signal_relay
has_antenna_key
transmitter_repaired
warning_sent
sable_awake
sable_alive
sable_following
sable_sacrifice_used
```

### Event: Creature Outside If Player Delays

If player refuses to go outside for enough turns:

- After maybe 8-12 meaningful turns, show window sighting if in cockpit/observation or via ship alert.
- After more turns, creature boards anyway.

This ensures the game progresses.

### Event: Cave Trigger

When player examines distress beacon or enters Signal Cave deeply:

- Set `cave_triggered = true`.
- Monster phase becomes `following`.

Do not reveal too much.

### Event: Return to Ship

When player enters airlock after cave trigger:

- Set `returned_after_cave = true`.
- Start boarding sequence.
- After 1-3 turns, set monster aboard.
- Place monster in airlock, ventral_service, or landing_gear route depending on chosen event.

### Event: Communications Objective

When player checks communications or ship computer after return:

- Reveal transmitter damaged.
- Show missing parts.

### Event: Final Repair

When player starts/completes repair:

- Sound becomes loud.
- Monster targets communications.
- Final pressure begins.

---

## 16. Character Type Differences

Keep differences useful but small.

All types can finish same story.

### Human

- Standard toxic death rule.
- Can use medkit.
- Panic flavor near monster.
- Slightly less efficient repairs.

Example:

```text
Your breath crowds the helmet.
```

### Synthetic

- Better repair: maybe one fewer required repair command.
- Scanner output slightly more precise.
- Cannot use medkit.
- Toxic exposure flavor is system corrosion, not suffocation.
- Monster still lethal.

Example:

```text
Your left optical channel records movement before naming it.
```

### Contract Specialist

- Better corporate log interpretation.
- Starts with or more easily finds access card.
- Objective hints slightly clearer.
- Average survival.

Example:

```text
The Farland-Guttenber seal makes the lie official.
```

---

## 17. Sable, Synthetic NPC

Implement if feasible.

Sable is an optional helpful synthetic NPC.

Location:

- Crew Quarters or Maintenance Junction.

Activation:

- Player examines or repairs Sable.
- Or Sable appears after monster boards.

Behavior:

- Gives one or two short hints.
- Can follow player.
- Can open one door or reduce repair difficulty.
- Can sacrifice itself once to save player from monster.

Do not make Sable complicated.

Sable lines should be sparse.

Examples:

```text
"I can open Engineering."
```

```text
"You should move now."
```

```text
"It has learned doors."
```

Sacrifice:

If Sable is alive/following and player would die:

- consume Sable
- move player to adjacent safe room or delay monster
- show short text

```text
Sable pushes you through the hatch.

The shape drops.

Sable says, "Go."

The hatch closes before the sound begins.
```

---

## 18. Win Condition

Player must be in Communications.

They must have or install:

- power coupler
- signal relay
- antenna key

Commands should be flexible:

```text
repair transmitter
install power coupler
install coupler
install signal relay
install relay
use antenna key
repair communications
fix transmitter
send warning
send message
transmit warning
```

Once all components installed:

```text
TRANSMISSION READY.

Message?
```

Allow the player to type any message.

Then display canonical transmission:

```text
DO NOT COME HERE.
```

Set `win_state = true`.

Show ending.

---

## 19. Ending Text

Use this or a close variant:

```text
TRANSMISSION SENT.
```

Then:

```text
FARLAND-GUTTENBER RELAY STATION
SEVENTEEN DAYS LATER

"Play it again."

"Do not come here."

"Was there contact?"

"Yes."

"Hostile?"

"Intelligent."

A pause.

"Wake Survey Team One."
```

Final line:

```text
LV-417c is upgraded to priority recovery.
```

Then offer:

```text
restart / quit
```

---

## 20. Death Handling

Death should stop the game but allow restart/undo if implemented.

Required deaths:

- toxic air
- monster attack
- final repair failure
- optional environmental hazard

Death style:

Short. Cold. Fair.

Examples:

```text
You make it four steps.
That is all.
```

```text
The room becomes very small.
```

```text
The shot is still echoing when the vent opens.
```

```text
It checks the same place twice.
This time it is right.
```

---

## 21. Terminal UI

Make the UI comfortable.

Suggested screen format:

```text
THE THIN AIR
Location: Central Corridor | Sound: quiet | Suit: worn | Motion: west, 4 moves

Low ceiling. Handrails. Old boot marks.
The lights hum in pairs.

Exits: north, east, south, west
Items: none

> 
```

Rules:

- Keep output compact.
- Avoid giant walls of text.
- Use blank lines generously.
- Repeat useful status.
- Show exits.
- Show visible items.
- Show sound after actions.
- Show scanner status only if player has terminal.
- Make help useful.

### Help Command

`help` should show:

```text
Common commands:
  north/south/east/west, in/out, up/down
  look, examine <thing>, take <thing>
  inventory, wear <thing>, use <thing>
  scan, listen, hide, crawl <direction>
  repair <thing>, read <thing>
  map, help, quit
```

### Map Command

Optional but recommended.

Should show known visited rooms only, or a simple list:

```text
Known rooms:
- Cockpit
- Central Corridor
- Airlock
- Surface
```

Do not reveal all hidden rooms unless desired.

---

## 22. Implementation Strategy

Build in phases.

### Phase 1: Static Adventure

- Implement rooms and movement.
- Implement look/examine.
- Implement inventory.
- Implement suit.
- Implement toxic atmosphere.
- Implement cave trigger.
- Implement win room and basic repair.

Goal:

Player can walk from cockpit to cave and back, collect parts, repair transmitter, and win without monster AI.

### Phase 2: Parser Comfort

- Add aliases.
- Add helpful errors.
- Add command normalization.
- Add inventory display.
- Add status bar.
- Add help.
- Add map.

Goal:

Game feels playable and forgiving.

### Phase 3: Sound and Turns

- Add turn system.
- Add sound costs.
- Add sound indicator.
- Add room stay count.
- Add time-advancing vs non-time commands.

Goal:

Player actions have consequences.

### Phase 4: Scanner

- Add terminal item.
- Add scan command.
- Add shortest path distance.
- Add relative direction.
- Add interference.

Goal:

Scanner works before full monster behavior.

### Phase 5: Monster AI

- Add monster entity.
- Add dormant/following/aboard phases.
- Add graph pathfinding.
- Add suspicion.
- Add sound response.
- Add hunting/searching.
- Add same-room detection.
- Add death.

Goal:

Monster feels real.

### Phase 6: Hiding and Distractions

- Add hiding spots.
- Add hide command.
- Add crawl.
- Add throw can / flare.
- Add reuse penalties.
- Add temporary survival in same-room scenarios.

Goal:

Player has tense but limited defensive options.

### Phase 7: Polish

- Add type-specific flavor.
- Add Sable synthetic NPC.
- Add final repair pressure.
- Add dynamic room descriptions.
- Add ending.
- Add save/load or undo if feasible.
- Add tests.

Goal:

Complete horror experience.

---

## 23. Testing Checklist

Create tests or manual test scripts for:

### Parser

- `n` equals `north`
- `x console` equals `examine console`
- `get terminal` equals `take terminal`
- `put on suit` works
- unknown commands are handled gracefully

### Map

- all exits work both directions where intended
- no required room is unreachable
- communications reachable
- cave reachable
- required items reachable

### Suit/Toxic Air

- human dies after two outside moves without suit
- suit prevents toxic death
- removing suit outside is dangerous
- synthetic gets distinct flavor

### Inventory

- take/drop works
- worn suit appears as worn
- required parts tracked

### Scanner

- before monster: no motion
- after monster: direction/distance correct
- same-room monster reports here
- interference works

### Monster

- dormant before trigger
- boards after cave return
- responds to loud sound
- violent sound brings monster quickly
- monster uses map pathfinding
- monster can kill player
- hiding can save temporarily
- staying hidden too long becomes dangerous

### Win

- cannot repair transmitter without parts
- can install required parts
- can send warning
- ending displays correctly

---

## 24. Balancing Guidelines

The game should be tense, not impossible.

Target:

- First-time players die once or twice.
- Careful players can finish in 30 minutes.
- Scanner should be useful.
- Monster should be scary but fair.
- Death should teach something.

Tuning:

- Monster should not board instantly after cave return.
- Give player a few turns to understand danger.
- Loud actions should matter.
- Hiding should work once or twice, not forever.
- Required path should include loops, not only dead ends.
- Avoid random unavoidable death.

---

## 25. Acceptance Criteria

The game is done when:

1. A player can start a new game, choose character info, and play in terminal.
2. The parser supports common Zork-like commands.
3. The player can wear the EVA suit and survive outside.
4. Forgetting the suit kills the player in two moves.
5. The cave sequence triggers the monster boarding.
6. The monster exists in the map as a moving entity.
7. The scanner shows relative direction and distance.
8. Sound affects monster behavior.
9. Inventory works.
10. Required repair parts can be collected.
11. Communications can be repaired.
12. The warning can be sent.
13. The ending shows Farland-Guttenber choosing to come anyway.
14. The whole game can be completed in about 30 minutes.
15. The writing is terse, atmospheric, and clear.

---

## 26. Non-Goals

Do not build:

- a huge open world
- complex combat
- RPG leveling
- long cutscenes
- verbose lore database
- graphical UI
- multiplayer
- procedural map generation unless everything else is done
- overly complex NPC behavior
- perfect natural-language understanding

This is a focused, lethal, elegant text adventure.

Make the knife sharp.

---

## 27. Final Creative Direction

The player should rarely be confused about what to do.

They should often be afraid to do it.

The story is simple:

You went outside.

Something came back in.

Now you must warn people who will not listen.

------




# Game Story: **THE THIN AIR**

## 1. Core Pitch

**THE THIN AIR** is a short, high-tension, text-only survival horror adventure.

It should feel like:

- **Zork** in its command style, object puzzles, room descriptions, inventory, and terse feedback.
- **Alien: Isolation** in its predator pressure, sound-based danger, stalking, and constant dread.
- A modern terminal tool in its readability, responsiveness, helpful affordances, and clean interface.

The player lands on a dead planet after receiving a distress signal from beneath the surface.

The planet’s air is toxic.

The cave is not empty.

The ship is not safe after you return.

The goal is simple:

> Reach the communications room, repair the transmitter, and send a warning to headquarters:  
> **do not come here.**

The ending is tragic:

The warning is received.

Headquarters becomes more interested.

They are coming.

---

## 2. Tone

The story must be told with **economy of words**.

Do not over-explain.

Do not write lore dumps.

Do not describe every fear directly.

Let the player infer.

Use short descriptions.

Use silence.

Use repeated small details changing over time.

The game should often feel like this:

> You are not alone.  
> You are not sure when that became true.

### Preferred prose style

Room descriptions should be compact:

```text
Airlock

A narrow chamber. Suit locker. Outer hatch. Inner hatch.
The floor is scratched white near the drain.

Exits: in, out
```

Tension descriptions should also be restrained:

```text
Something taps once in the vent.
```

Avoid purple prose.

Avoid long cutscenes.

Avoid explaining the monster.

---

## 3. Working Title

**THE THIN AIR**

Alternative titles:

- **Two Moves of Air**
- **Far Side Signal**
- **Blackweather**
- **The Quiet Hatch**
- **Do Not Come Here**

Recommended title: **THE THIN AIR**

It works because:

- The planet’s atmosphere kills quickly.
- The ship’s safety is fragile.
- The game’s horror lives in negative space.
- “Thin air” also implies disappearance.

---

## 4. Opening Premise

The player is aboard the survey lander **LANTERN-9**, contracted by **Farland-Guttenber Recovery & Survey**.

The lander has touched down on **LV-417c**, a small dead planet with a toxic atmosphere.

A distress signal is coming from a cave mouth 200 meters east of the landing site.

The signal is old, but not degraded.

That should not be possible.

The player wakes from descent sedation with the lander already grounded.

The ship computer reports:

```text
Landing complete.
Atmosphere: lethal.
Signal source: local.
Crew status: one.
```

The player must first answer a short character setup.

---

## 5. Character Setup

At the beginning, ask:

```text
Name?
Gender?
Type?
```

Available types:

1. **Human crewmember**
2. **Synthetic**
3. **Contract specialist**

The player’s choice should affect abilities and flavor, not the main story outcome.

All types can finish the game.

The ending remains the same.

### 5.1 Human Crewmember

Humans are fragile but intuitive.

Traits:

- Can panic under extreme danger.
- Can read emotional cues in logs and corpses better.
- Uses stimulants or medkits.
- Makes more sound when injured.
- Descriptions include bodily fear: breath, sweat, heartbeat.

Mechanical ideas:

- Slightly worse at technical repairs.
- Better at noticing human details.
- May get short panic text if the monster is close.
- Toxic exposure kills quickly without suit.

Sample flavor:

```text
Your hand shakes before you notice it.
```

### 5.2 Synthetic

Synthetics are calm, precise, and useful.

Traits:

- Better at repairs.
- Immune to panic.
- Can survive limited toxic exposure longer than humans.
- Cannot use medkits.
- Notices patterns and measurements.
- Other synthetics recognize them differently.

Mechanical ideas:

- Repairs take fewer steps.
- Scanner information may be slightly more precise.
- Toxic air gives warnings before damage rather than immediate panic.
- Monster still kills the synthetic if caught.

Important rule:

> Synthetics are helpful in this world.

If the player meets a synthetic NPC, that synthetic should cooperate.

If the monster attacks, the synthetic NPC will usually sacrifice itself to save the player.

Sample flavor:

```text
Fear is not present.
Something adjacent to fear is.
```

### 5.3 Contract Specialist

A compromise class.

Traits:

- Better inventory handling.
- Better at reading corporate logs.
- Can identify Farland-Guttenber equipment.
- Average repairs.
- Average physical resilience.

Mechanical ideas:

- Starts with a small access card or diagnostic note.
- Gets clearer hints from corporate terminals.
- Slightly better at finding required parts.

Sample flavor:

```text
The company handbook did not cover this.
```

---

## 6. Farland-Guttenber

Farland-Guttenber Recovery & Survey is a corporate exploration and salvage firm.

It should feel cold, procedural, and polite.

Do not directly mention or copy Alien franchise corporations.

Farland-Guttenber’s voice:

```text
Safety is recoverable.
Loss is reportable.
Discovery is permanent.
```

They care about assets, discoveries, and recoverable technology.

People are important only when people are useful.

The player’s contract is simple:

- Locate distress signal.
- Recover data if possible.
- Report biological, geological, or technological anomalies.
- Preserve company assets.

The tragedy is that the player’s warning only increases the company’s interest.

---

## 7. The Planet

Name: **LV-417c**, informally called **Morrow**

Surface conditions:

- Toxic air.
- Cold wind.
- Low visibility.
- Dark dust.
- No known native life.
- Cave system near landing site.
- Distress signal from underground structure or wreckage.

The air kills humans quickly.

If the player exits without a suit:

- First move outside: warning.
- Second move outside: death.

Example:

```text
> out

Surface

The air burns immediately.
Your eyes fill.

You are not wearing a suit.

Exits: in, east
```

Then:

```text
> east

You make it four steps.
That is all.
```

For synthetics:

- They may survive a little longer outside without a suit.
- But they still need the suit or protection because dust and corrosive atmosphere damage systems.
- They should receive warnings and then fail.

---

## 8. The Suit Rule

Before going outside, the player must wear an EVA suit.

The suit is in the lander airlock or suit locker.

Required commands should be flexible:

```text
take suit
wear suit
put on suit
equip suit
```

The game should clearly but not obnoxiously teach this.

Early room:

```text
Airlock

Suit locker. Outer hatch. Inner hatch.
A red card says: TWO MOVES WITHOUT SEAL.
```

If the player forgets, the game allows the mistake.

This is important.

The world is dangerous.

The player learns through consequence.

But the death should feel fair because the warnings were there.

---

## 9. The Cave

The cave is the first external exploration area.

It should feel quiet, dead, and too close.

Purpose of cave sequence:

- Teach movement.
- Teach inventory.
- Teach examining.
- Teach the scanner/terminal idea.
- Let the player collect or discover the first key object.
- Let the player unknowingly create the main problem by returning to the ship.

Important:

> The player explores the cave first and returns to the ship without realizing they let the creature in.

This can happen through:

- Spores on the suit.
- A small organism clinging under the suit seal.
- The creature itself following in the player’s blind spot.
- Something entering through the outer hatch during decompression.
- A tiny larval state that later grows rapidly.

Recommended version:

The cave contains a fist-sized organism folded like wet black paper.

It is never called an egg.

It is never fully described.

When the player enters the cave, it wakes.

When the player leaves, it follows the warmth and pressure cycle back into the ship.

The player does not see it enter.

Possible hint:

```text
When the hatch closes, something soft knocks once outside.

Then inside.
```

---

## 10. The Monster

The monster is inspired by:

- A xenomorph-like predator: silent, physical, lethal, spatially intelligent.
- Calvin from *Life* (2017): adaptive, curious, strong, problem-solving, unpleasantly clever.

Do not call it a xenomorph.

Suggested names used by systems/NPCs:

- **Specimen**
- **Organism**
- **The passenger**
- **The shape**
- **Contact**
- **Black animal**
- **Nonhuman motion**

Never over-describe it.

The player should build a picture from fragments:

```text
A handprint appears high on the wall.
Too many fingers.
```

```text
The vent grille is peeled outward.
```

```text
Something passes the window.
Not walking.
```

```text
The scanner shows motion west.
Then north.
Then west again.
It is learning the corridors.
```

### 10.1 Monster Behavior

Once aboard, the monster must be a real autonomous entity in the game model.

It has:

- Current room.
- Target room or suspicion target.
- Awareness state.
- Last heard sound location.
- Last seen player location.
- Search memory.
- Movement cooldown or speed.
- Bias toward the player without perfect knowledge.

The monster should feel smart, not random.

It should usually know the general direction of the player, especially after noise.

But it should not teleport or cheat obviously.

### 10.2 Monster States

Recommended states:

1. **Dormant**
   - Before cave trigger.
   - Not active on ship.

2. **Following**
   - After cave encounter, before visible ship entry.
   - Player may notice small signs.

3. **Aboard**
   - Monster is on ship.
   - Tension rises.
   - Scanner becomes essential.

4. **Hunting**
   - Monster has recent evidence: sound, sight, door use, running.
   - Moves toward last known player location.

5. **Searching**
   - Monster lost the player.
   - Checks nearby rooms, vents, corridors.

6. **Investigating**
   - Monster heard a smaller sound.
   - Moves toward source but slower or less directly.

7. **Attack**
   - Monster is in same room and sees/hears player.
   - Player may survive only with a very narrow set of actions.

8. **Feeding/Delayed**
   - After killing an NPC or synthetic.
   - Temporarily distracted.

### 10.3 Monster Should Not Be Everywhere

The monster must be terrifying because it is modeled.

It should have limitations:

- It moves through map connections.
- It can use vents between certain rooms.
- It responds to sound.
- It patrols likely routes.
- It may pause.
- It may investigate wrong rooms if deceived.

But it should also be dangerous:

- Running creates loud sound.
- Shooting or yelling is almost guaranteed to bring it in 2-3 moves.
- Staying in one place too long increases risk.
- Hiding is temporary.
- Reusing the same hiding place increases risk.

---

## 11. The Scanner / Terminal

The player should find a portable terminal or motion scanner in the first 2-3 moves.

Suggested object: **hand terminal**

Location: cockpit or equipment locker.

It is similar in function to Alien: Isolation’s scanner.

It shows:

- Whether motion is detected.
- Relative direction from the player: N, S, E, W.
- Approximate distance in moves/rooms.
- Urgency.

Example:

```text
> scan

MOTION: west
DISTANCE: 5 moves
SIGNAL: intermittent
```

Closer:

```text
> scan

MOTION: north
DISTANCE: 2 moves
SIGNAL: strong
```

Same room, not seeing player:

```text
> scan

MOTION: here
DISTANCE: 0
SIGNAL: inside the room
```

If the monster sees the player:

```text
> scan

You lift the terminal.

It is already looking at you.
```

The scanner should not be perfect.

Limitations:

- It may flicker near power failures.
- It may detect moving machinery.
- It may fail in shielded rooms.
- It may lag by one move.
- It should not ruin suspense.

But it must be useful and fair.

The player should trust it enough to use it often.

---

## 12. Sound System

Every action carries a sound cost.

Sound is visible in the UI.

The player should always see current sound level or recent sound.

Example interface:

```text
Sound: quiet
```

Or:

```text
Sound: loud
```

Sound levels:

1. **silent**
2. **quiet**
3. **audible**
4. **loud**
5. **violent**

Actions produce sound:

| Action | Sound |
|---|---:|
| look | silent |
| inventory | silent |
| examine | quiet |
| take item | quiet |
| open normal door | audible |
| close door | quiet/audible |
| walk | quiet |
| crawl | silent/quiet |
| run | loud |
| repair | audible/loud |
| force door | loud |
| shoot | violent |
| yell | violent |
| throw object | audible/loud |
| hide | quiet |
| wait | silent but risky |

Sound affects monster AI:

- Quiet sounds may be ignored unless nearby.
- Audible sounds draw investigation.
- Loud sounds draw hunting.
- Violent sounds almost guarantee arrival within 2-3 monster turns if a route exists.

Important rule:

> Hiding is temporary. Staying still is not safety.

The game should track how long the player remains in one room.

If they stay too long:

- The monster’s search bias toward them increases.
- Random environmental sounds may occur.
- The scanner may pick up movement.
- The monster may check the room.

---

## 13. Player Goal

The player must send a warning to headquarters.

To do this, they must repair the communications device in the ship’s communications room.

The transmitter is damaged.

Required repair parts should be placed around the ship.

Keep it simple.

Recommended required parts:

1. **Signal relay**
2. **Power coupler**
3. **Antenna key**
4. **Ceramic fuse**

The player needs all four to repair the transmitter.

Optional simplification:

Use only three parts:

1. Signal relay
2. Power coupler
3. Antenna key

Recommended: three parts for a 30-minute game.

### Final repair sequence

The player reaches communications with the parts.

Commands:

```text
repair transmitter
install relay
install coupler
use antenna key
send warning
```

The parser should allow flexible equivalents.

When complete:

```text
TRANSMISSION READY.

Message?
```

The player may type anything.

The system should send a canonical warning anyway.

Example:

```text
> send do not come here

Signal sent.

Farland-Guttenber receives.
```

Then ending scene.

---

## 14. Ending

After the player sends the warning, they win.

But show a brief tragic conversation on the receiving end.

It should be short and cold.

Example:

```text
FARLAND-GUTTENBER RELAY STATION
SEVENTEEN DAYS LATER

"Repeat the message."

"Do not come here."

"Biological threat?"

"Unclear."

"Intelligent?"

"Likely."

A pause.

"Prep Recovery Team One."
```

Final line:

```text
Farland-Guttenber marks LV-417c as high priority.
```

Or:

```text
They are not warned.

They are invited.
```

This should be the final sting.

No sequel bait speech.

No explanation.

---

## 15. Core Map

The ship should feel vast, but not be too large.

Target playtime: about **30 minutes** for a thoughtful player.

Recommended map size:

- 14-18 ship rooms.
- 4-6 cave/surface rooms.
- 3-4 vent-only or monster-shortcut routes.
- Some locked or blocked routes to create loops.

The map should be fully modeled as a graph.

Every room has:

- ID
- Display name
- Description
- Exits
- Items
- Hazards
- Sound modifiers
- Hiding spots
- Whether monster can enter
- Whether scanner works
- Whether vents connect

## 16. Proposed Map

### 16.1 Ship: LANTERN-9

#### 1. Cockpit

Starting room.

Contains:

- Flight chair
- Ship computer
- hand terminal / scanner
- viewport

Exits:

- south to Central Corridor

Notes:

- If player never leaves ship, they may eventually see the creature through viewport.
- This proves the world progresses without player obedience.

Sample description:

```text
Cockpit

Dead stars in the glass.
The console waits with one green light.

Exits: south
```

#### 2. Central Corridor

Main hub.

Exits:

- north to Cockpit
- east to Airlock
- south to Med Bay
- west to Engineering Access

Description:

```text
Central Corridor

Low ceiling. Handrails. Old boot marks.
The lights hum in pairs.

Exits: north, east, south, west
```

#### 3. Airlock

Contains:

- suit locker
- EVA suit
- inner hatch
- outer hatch

Exits:

- west to Central Corridor
- out to Surface

Rules:

- Cannot go out safely without suit.
- Creature later uses airlock or hull breach to enter.

#### 4. Med Bay

Contains:

- medkit
- recorder log
- hiding cabinet

Exits:

- north to Central Corridor
- east to Crew Quarters

Potential part:

- Ceramic fuse, if using four-part version.

#### 5. Crew Quarters

Contains:

- bunks
- personal locker
- possible NPC synthetic later
- access card

Exits:

- west to Med Bay
- south to Galley

Hiding:

- under bunk, temporary only.

#### 6. Galley

Contains:

- loose cans
- water recycler
- throwable object

Exits:

- north to Crew Quarters
- west to Storage

Sound feature:

- Moving quickly here makes extra noise.

#### 7. Storage

Contains:

- power coupler
- flare
- maintenance tags

Exits:

- east to Galley
- south to Cargo Bay
- west to Engineering Access

#### 8. Engineering Access

A narrow passage.

Exits:

- east to Central Corridor
- south to Reactor Room
- west to Storage

Contains:

- locked panel
- crawlspace entrance

Monster:

- Can pass through here often.

#### 9. Reactor Room

Contains:

- reactor controls
- heat
- noise
- possible repair hazard

Exits:

- north to Engineering Access

Part:

- signal relay or power coupler.

Sound:

- Ambient loudness may mask small player sounds.

Risk:

- Scanner may be less reliable due to interference.

#### 10. Cargo Bay

Large room.

Contains:

- crates
- forklift
- dark corners
- antenna key

Exits:

- north to Storage
- east to Maintenance Junction
- south to Lower Hold

Hiding:

- behind crates.

Monster:

- Excellent ambush room.
- Monster can enter from vents.

#### 11. Lower Hold

Optional scary dead-end.

Contains:

- old distress beacon fragment
- scratch marks
- maybe corpse/suit

Exits:

- north to Cargo Bay

Purpose:

- Atmosphere and optional lore.
- Could hold one required part if game needs more exploration.

#### 12. Maintenance Junction

Loop connector.

Exits:

- west to Cargo Bay
- east to Comms Hall
- north to Ventral Service

Contains:

- tool rack
- repair kit

#### 13. Ventral Service

Small mechanical room.

Exits:

- south to Maintenance Junction
- east to Observation

Contains:

- crawl route
- noisy fan

Monster:

- Can use vent here.

#### 14. Observation

Window room.

Exits:

- west to Ventral Service
- south to Comms Hall

Important:

- If player delays before cave, they may see the creature outside.
- If monster is aboard, player may see it pass outside/inside.

Description:

```text
Observation

A long window.
The planet presses its dark face against it.

Exits: west, south
```

#### 15. Comms Hall

Before communications room.

Exits:

- north to Observation
- west to Maintenance Junction
- east to Communications

Tension:

- Final approach corridor.
- Monster pressure should be high here.

#### 16. Communications

Final objective room.

Contains:

- damaged transmitter
- console
- parts slots
- dead microphone

Exits:

- west to Comms Hall

Goal:

- Repair transmitter.
- Send warning.

Monster:

- Should be able to interrupt if player makes too much noise during repair.

---

### 16.2 Surface and Cave

#### 17. Surface

Outside lander.

Requires suit.

Exits:

- in to Airlock
- east to Ridge
- south to Landing Gear

Description:

```text
Surface

Black dust moves like smoke.
Your suit light finds the cave mouth east.

Exits: in, east, south
```

#### 18. Landing Gear

Optional surface room.

Contains:

- damaged strut
- strange slime mark after cave event

Exits:

- north to Surface

Purpose:

- Foreshadow creature boarding.

#### 19. Ridge

Between ship and cave.

Exits:

- west to Surface
- east to Cave Mouth

Event:

- Signal gets stronger.

#### 20. Cave Mouth

Exits:

- west to Ridge
- down to Signal Cave

Description:

```text
Cave Mouth

The signal is louder here.
Not stronger.
Louder.

Exits: west, down
```

#### 21. Signal Cave

Contains:

- distress beacon
- first impossible clue
- organism trigger

Exits:

- up to Cave Mouth
- east to Black Pool

Event:

- On first examination of beacon or room, organism wakes.

#### 22. Black Pool

Small optional cave room.

Contains:

- black liquid
- old helmet
- nonhuman mark

Exits:

- west to Signal Cave

Purpose:

- Optional dread.
- Maybe contains access card or clue.

After the player returns to the ship, the monster is eventually aboard.

---

## 17. Story Flow

### Act 1: Wake

Player starts in cockpit.

Immediate objectives:

- Learn command style.
- Find/take hand terminal.
- Read distress.
- Find airlock.
- Wear suit.

Possible early commands:

```text
look
examine console
take terminal
inventory
south
east
open locker
take suit
wear suit
out
```

### Act 2: Outside

Player crosses surface to cave.

Risks:

- Toxic atmosphere if unsuited.
- Low visibility.
- Signal oddness.

No monster attack yet.

The cave triggers infection/following.

The player finds the distress beacon.

The beacon may say:

```text
DON'T OPEN THE—
```

or:

```text
WE BROUGHT IT BACK INSIDE.
```

But the player does not yet understand.

### Act 3: Return

When the player returns to the ship:

- Airlock cycles.
- A small sound occurs.
- Ship status changes subtly.
- Scanner eventually detects motion.

Important moment:

```text
The inner hatch opens.

For one second, the ship smells like rain.
```

This is wrong.

The monster is aboard or soon will be.

### Act 4: Repair Objective

Ship computer reports communications failure.

The player must repair communications.

The parts are scattered:

- **Power coupler** in Storage.
- **Signal relay** in Reactor Room.
- **Antenna key** in Cargo Bay or Lower Hold.

The player uses map knowledge, scanner, sound management, and movement to gather parts.

### Act 5: Hunt

The monster actively moves.

Tension rises:

- More vents opened.
- More room descriptions altered.
- Scanner pings closer.
- Staying still becomes dangerous.
- Loud actions invite death.

Synthetics:

- The player may meet a synthetic NPC, **Sable**.
- Sable helps with one repair or gives a hint.
- If the monster catches up during a specific scene, Sable sacrifices itself.

Keep Sable useful but brief.

Sample:

```text
Sable waits in Crew Quarters.

"I can open Engineering," it says.
"It has already learned doors."
```

If attacked:

```text
Sable steps between you and the black shape.

"Go," it says.

The door closes on the rest.
```

### Act 6: Transmission

The player reaches Communications with all parts.

Repairing makes sound.

The monster should be drawn toward the player during the final repair.

The player may need to:

- Close a door.
- Crawl away and return.
- Use flare/noise distraction.
- Let Sable sacrifice itself if available.
- Finish the repair under pressure.

### Act 7: Ending

The warning is transmitted.

Then the receiving end conversation reveals the failure of the warning.

The player wins.

The company chooses curiosity.

---

## 18. Inventory

The player must have an inventory.

Command aliases:

```text
inventory
i
inv
```

Inventory should display:

```text
You carry:
- hand terminal
- EVA suit, worn
- power coupler
- flare
```

Items can be:

- portable
- wearable
- usable
- installable
- consumable
- noisy
- distracting
- required for ending

Recommended items:

| Item | Use |
|---|---|
| hand terminal | scan monster proximity |
| EVA suit | survive outside |
| medkit | heal human player |
| repair kit | required or helps repair |
| power coupler | transmitter repair |
| signal relay | transmitter repair |
| antenna key | transmitter repair |
| flare | distract monster / light cave |
| access card | open engineering or storage |
| loose can | throwable noise distraction |
| recorder log | story fragment |
| beacon fragment | story clue |

---

## 19. Commands

The parser should support familiar text adventure commands.

Required movement:

```text
north / n
south / s
east / e
west / w
up / u
down / d
in
out
go north
```

Core verbs:

```text
look
examine / x
take / get
drop
inventory / i
use
wear
remove
open
close
unlock
repair
install
scan
listen
wait
hide
crawl
run
throw
read
help
map
```

Combat should be minimal.

If there is a weapon, it should not be a solution.

Shooting is a panic option.

It is loud.

It brings the monster.

It may delay but not kill.

Recommended: no gun, or a flare pistol with one use that only scares/distracts briefly.

---

## 20. Deaths

Deaths should be short and fair.

Examples:

### Toxic air

```text
You make it four steps.
That is all.
```

### Monster sees player

```text
The room becomes very small.
```

### Too loud

```text
The shot is still echoing when the vent opens.
```

### Waiting too long

```text
You wait.

The handle turns.
```

### Failed hide

```text
It checks the same place twice.
This time it is right.
```

After death, allow:

```text
restart
restore
undo
quit
```

The game should support at least one-turn undo if feasible.

---

## 21. Interface Requirements

The game is terminal-only but should feel modern and comfortable.

Inspired by Codex CLI style:

- Clear prompt.
- Clean panels.
- Minimal visual noise.
- Fast commands.
- Helpful autocomplete if possible.
- Good error messages.
- Command history.
- Optional map view.
- Status bar.

Suggested layout:

```text
THE THIN AIR

Location: Central Corridor
Sound: quiet
Suit: worn
Motion: west, 4 moves

Low ceiling. Handrails. Old boot marks.
The lights hum in pairs.

Exits: north, east, south, west
Items: none

> _
```

The status area should include:

- Location
- Sound indicator
- Suit status
- Monster scanner summary if terminal owned
- Health/system status
- Objective hint, optional

Important:

The interface should not spoil hidden information.

If the player does not have the terminal:

```text
Motion: unknown
```

If scanner is off/interfered:

```text
Motion: interference
```

---

## 22. Monster Movement Model

The monster must use the same map as the player.

Each player command advances time unless it is a meta-command.

Time-advancing commands:

- movement
- take/drop
- open/close
- use
- repair
- wait
- scan
- hide
- crawl
- throw

Non-time commands:

- help
- inventory maybe silent but can still cost a turn if desired
- map
- look, optionally no turn or low turn

Recommended:

- `look`, `inventory`, `help`, `map` do not advance monster.
- `scan` does advance monster slightly or has a cooldown.
- Movement and actions advance monster.

### Monster routing

The monster should compute paths on the graph.

It should know:

- Player last known room.
- Last sound room.
- Rooms recently visited by player, maybe as scent.
- Current suspicion score per room.

When sound occurs:

- Add suspicion to current player room.
- Loud sounds overwrite monster target.
- Violent sounds cause direct hunting.

When no sound occurs:

- Monster follows suspicion gradients.
- Monster patrols between central rooms.
- Monster may check rooms adjacent to player with some bias.
- Monster uses vents occasionally.

### Distance

Scanner distance should be shortest path length between player room and monster room.

Display:

- 5+ moves: `5+ moves`
- 4 moves
- 3 moves
- 2 moves
- 1 move
- here

Relative direction:

Use first step on shortest path from player to monster.

If multiple paths, choose the first route by deterministic ordering or show `unclear`.

Examples:

```text
MOTION: east
DISTANCE: 3 moves
```

```text
MOTION: here
DISTANCE: 0
```

### Same room rule

If monster and player are in the same room:

- If player is hidden and quiet, monster may not immediately see them.
- Each turn in same room increases detection risk.
- Any noisy action reveals player.
- Crawling away may work if an exit exists and monster is not focused.
- Running almost always reveals player.
- Hiding again in same room is poor.

Possible same-room messages:

```text
Something breathes above the lockers.
```

```text
The scanner has no direction to give.
```

```text
It is in the room.
```

---

## 23. Hiding

Hiding is temporary.

Each hide spot has:

- name
- quality
- max safe turns
- reuse penalty
- allowed room

Example hide spots:

- Med Bay cabinet
- Cargo crates
- Crew Quarters bunk
- Engineering crawlspace
- Communications console shadow

Rules:

- Hiding lowers immediate detection.
- Waiting while hidden increases danger after 1-2 turns.
- Reusing the same hiding place lowers effectiveness.
- Monster can learn hiding places.

Commands:

```text
hide
hide under bunk
hide behind crates
crawl east
wait
```

Good hiding message:

```text
You fold yourself behind the crates.
The scanner clicks once.
```

Bad hiding message:

```text
You use the same cabinet again.
The door does not close all the way.
```

---

## 24. NPC Synthetic: Sable

Optional but recommended.

Name: **Sable**

Location:

- Initially inactive in Crew Quarters or Maintenance Junction.
- Can be repaired or awakened.
- Joins player briefly.

Role:

- Gives one practical hint.
- Opens one route or speeds one repair.
- May sacrifice itself to save player.

Sable should not become a companion simulator.

Keep it simple.

Behavior:

- Follows player if active.
- Does not fight unless sacrifice moment triggers.
- Can be used to distract monster once, but do not let the player abuse this.

Sample lines:

```text
"I hear it in the walls," Sable says.
"I do not have hearing."
```

```text
"You should move now."
```

```text
"It has learned the airlock."
```

Sacrifice:

If monster would kill player and Sable is present, Sable can save once:

```text
Sable takes your shoulder and pushes.

The thing drops from the ceiling.

Sable does not scream.
The door shuts.
```

After that, Sable is gone.

---

## 25. Puzzle Design

Keep puzzles readable.

No moon logic.

The main puzzle is route planning under pressure.

Required repair loop:

1. Get terminal.
2. Wear suit.
3. Explore cave.
4. Return.
5. Learn comms are damaged.
6. Find required parts.
7. Avoid monster.
8. Repair transmitter.
9. Send warning.

Part locations:

- Power coupler: Storage.
- Signal relay: Reactor Room.
- Antenna key: Cargo Bay.

Locks:

- Engineering Access may require access card from Crew Quarters.
- Communications may require antenna key or repair kit.

Hazards:

- Toxic air outside.
- Monster.
- Noisy rooms.
- Broken doors.
- Scanner interference in Reactor Room.
- Final repair noise.

Distractions:

- Throw can.
- Light flare.
- Trigger remote alarm, optional.
- Close/open doors to slow route, optional.

---

## 26. Important Dynamic Events

### If player never goes outside

The creature should still appear outside after some time.

Example after enough turns:

```text
Something crosses the cockpit glass.

Too tall for the landing gear.
Too close to the ship.
```

Then it eventually finds a way in.

This prevents the game from waiting forever.

### If player goes outside without suit

Death in two moves.

### If player explores cave and returns

Creature boarding sequence begins.

### If player makes violent sound

Monster heads toward player and should arrive within 2-3 monster moves if connected.

### If player stays in one room too long

Monster suspicion increases.

### If player scans too much

Scanning should be useful, but maybe not free.

It can advance time.

The player can over-rely on it and let the monster close distance.

### If player reaches communications without parts

The game clearly tells what is missing.

Example:

```text
The transmitter is open.

Missing:
- power coupler
- signal relay
- antenna key
```

---

## 27. Sample Opening Transcript

```text
THE THIN AIR

Name?
> Mara

Gender?
> woman

Type?
1. Human crewmember
2. Synthetic
3. Contract specialist
> human

Cockpit

Dead stars in the glass.
The console waits with one green light.

Exits: south

> examine console

FARLAND-GUTTENBER RECOVERY & SURVEY
LANTERN-9 STATUS

Landing complete.
Atmosphere: lethal.
Signal source: east, local.
Crew status: one.

A hand terminal rests beside the console.

> take terminal

Taken.

> scan

No internal motion detected.

> south

Central Corridor

Low ceiling. Handrails. Old boot marks.
The lights hum in pairs.

Exits: north, east, south, west

> east

Airlock

Suit locker. Outer hatch. Inner hatch.
A red card says: TWO MOVES WITHOUT SEAL.

Exits: west, out

> open locker

Opened.

> take suit

Taken.

> wear suit

The seals close around your throat.
Suit pressure holds.

> out

Surface

Black dust moves like smoke.
Your suit light finds the cave mouth east.

Exits: in, east, south
```

---

## 28. Sample Midgame Transcript

```text
> in

Airlock

The cycle completes.
For one second, the ship smells like rain.

Exits: west, out

> west

Central Corridor

The lights hum in pairs.

Exits: north, east, south, west

> scan

MOTION: east
DISTANCE: 5+ moves
SIGNAL: intermittent

> west

Engineering Access

The passage is narrow.
A panel hangs open.

Exits: east, south, west

> scan

MOTION: east
DISTANCE: 4 moves

> open panel

The panel shrieks.

Sound: loud

> scan

MOTION: east
DISTANCE: 2 moves
SIGNAL: strong

> crawl west

You crawl into Storage.

Sound: quiet
```

---

## 29. Sample Ending

```text
> repair transmitter

You install the power coupler.
You install the signal relay.
You turn the antenna key.

The dish finds the sky.

Sound: loud

> scan

MOTION: west
DISTANCE: 1 move
SIGNAL: strong

> send warning

Message?
> do not come here

TRANSMISSION SENT.
```

Then:

```text
FARLAND-GUTTENBER RELAY STATION
SEVENTEEN DAYS LATER

"Play it again."

"Do not come here."

"Was there contact?"

"Yes."

"Hostile?"

A pause.

"Intelligent."

Another pause.

"Wake Survey Team One."
```

Final line:

```text
LV-417c is upgraded to priority recovery.
```

---

## 30. Design Pillars

1. **Brevity creates fear.**
   The game should imply more than it states.

2. **The monster is real.**
   It moves through the map. It hears. It searches. It learns.

3. **Sound is a currency.**
   Every action has a noise cost.

4. **The scanner is comfort and danger.**
   It helps, but using it spends time.

5. **The ship is a maze, not a mansion.**
   Enough rooms to feel large. Few enough to learn quickly.

6. **The player always has a clear goal.**
   Repair communications. Send warning.

7. **The ending is victory with corporate horror.**
   The player succeeds. It does not matter enough.

---

## 31. Must-Have Features

- Text parser.
- Inventory.
- Wearable suit.
- Toxic atmosphere death rule.
- Ship/cave map graph.
- Items and repair parts.
- Hand terminal scanner.
- Sound indicator.
- Sound penalties per action.
- Monster AI after boarding.
- Monster pathfinding.
- Hiding as temporary safety.
- Dynamic room descriptions after monster boards.
- Win condition by repairing transmitter.
- Tragic corporate ending.

---

## 32. Nice-to-Have Features

- Save/load.
- Undo last move.
- Command history.
- Fuzzy parser suggestions.
- Optional ASCII map.
- Type-specific flavor.
- Synthetic NPC companion.
- Multiple death texts.
- Adaptive monster suspicion memory.
- Replay seed support.
- Accessibility setting for reduced panic text.
