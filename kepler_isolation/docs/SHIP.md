# SHIP_DOWNSIZED.markdown
# USCSS *NIGHTGLASS* — Downsized Single-Deck Version

A compact, playable ship map for a text-only interactive-fiction horror game.

This version keeps the same design DNA as the larger *Nightglass*:

- single deck only,
- cryo safe haven,
- alien starts far opposite the player,
- synthetics spawn randomly,
- bodies spawn randomly,
- hidden maintenance maze,
- radio-building endgame,
- *Alien: Isolation*-style stalking tension.

Scale target:

```text
Visible rooms: 75
Secret / maintenance places: 30
```

The visible count is slightly above 60 because the safe haven, airlocks, and symmetrical ship logic need breathing room. It should still play like a smaller, tighter map.

---

# Exterior Silhouette

```text
                         /\
                        /OBS\
                       /----\
                      /BRIDGE\
                     /--------\
                    / SECURITY \
                   /------------\
                  / MED CRYO SCI \
                 /----------------\
                / HAB  COMMONS  HAB\
               /--------------------\
              / INDUSTRIAL / POWER   \
             /------------------------\
            / CARGO / DOCKING / PODS   \
           /____________________________\
```

---

# One-Deck Rule

This ship has **one explorable deck**.

There are no elevators, no upper decks, no lower decks, and no multi-floor puzzles.

Hidden routes are still same-deck spaces:

```text
vents
crawlspaces
service gaps
underfloor trenches
ceiling voids
pipe runs
wall hollows
```

The complexity comes from:

- loops,
- locked doors,
- hidden exits,
- sound,
- line-of-sight,
- stalking routes,
- random spawns.

Not vertical navigation.

---

# Core Layout

```text
NORTH / BOW

                  A COMMAND
                      |
              B SECURITY / ADMIN
                      |
        D MEDICAL -- C CRYO -- D SCIENCE
                      |
         E HAB WEST -- COMMONS -- HAB EAST
                      |
              F INDUSTRIAL / ENGINEERING
                      |
              G CARGO / DOCKING / PODS

SOUTH / AFT
```

---

# Player and Alien Starts

## Player Start

Fixed player start:

```text
C09 Cryo Pod Bay Alpha
```

The player wakes from deep sleep.

Initial accessible rooms:

```text
C09 Cryo Pod Bay Alpha
C10 Cryo Pod Bay Beta
C11 Cryo Monitoring Station
C12 Cryo Backup Power Closet
C13 Cryo Secure Storage
```

Opening feeling:

```text
You wake before the pod finishes opening.
The glass is fogged from the inside.
No technician waits outside.
No voice comes from Command.
Far away, deep in the aft ship, something moves.
```

## Alien Start

Fixed recommended alien start:

```text
G11 Aft Beacon Service
```

This is opposite the player and gives the game a clear pressure curve.

Alien starting region:

```text
G11 Aft Beacon Service
G08 Escape Pod Corridor
G06 Main Airlock
G05 Docking Control
G02 Cargo Bay A
G03 Cargo Bay B
```

Alien early migration:

```text
G11 -> G08 -> G06 -> G05 -> G01 -> F11
```

Alien hidden migration after power is restored:

```text
F11 -> M28 -> M29 -> G02/G03 -> M30 -> G06
```

---

# Safe Haven

## Safe Haven Core

The safe haven is the cryo core:

```text
C09 Cryo Pod Bay Alpha
C10 Cryo Pod Bay Beta
C11 Cryo Monitoring Station
C12 Cryo Backup Power Closet
C13 Cryo Secure Storage
```

The alien can never enter these rooms.

## Four-Sided Airlock Shell

The safe haven has four approaches.

```text
North:
C01 Cryo Vestibule North -> C05 North Double-Lock Airlock -> C09

East:
C02 Cryo Vestibule East -> C06 East Double-Lock Airlock -> C10

South:
C03 Cryo Vestibule South -> C07 South Double-Lock Airlock -> C10/C11

West:
C04 Cryo Vestibule West -> C08 West Double-Lock Airlock -> C10
```

## Alien Boundary

Alien forbidden rooms:

```text
C09
C10
C11
C12
C13
```

Alien may wait outside:

```text
C01
C02
C03
C04
C05
C06
C07
C08
```

## Safe Haven Uses

Inside the safe haven, the player can:

- save,
- rest,
- craft,
- store items,
- review notes,
- assemble the improvised radio,
- check cryo monitoring,
- wait indefinitely.

Inside the safe haven, the player cannot:

- complete the main objective,
- contact Earth,
- restore main power,
- access the antenna,
- override AI containment,
- collect all radio components.

The safe haven is not victory. It is oxygen.

## Safe Haven Door Logic

Each airlock has two doors.

Only one door opens at a time.

Normal cycle:

```text
outer opens
player enters
outer closes
scan runs
inner opens
player enters cryo
inner closes
```

Emergency cycle:

```text
outer opens
player dives inside
outer slams shut
inner delays
something moves outside
inner unlocks late
```

The alien still cannot enter. The fear is at the threshold.

---

# ASCII Floor Plan

```text
                                NORTH
                                  ^
                                  |

                              [A01]
                                |
                         [A02]-[A03]-[A06]
                                |     |
                         [A05]-[A04]-[A07]
                                |     |
                         [A08]-[B01]-[B03]
                                |     |
                         [B06]-[B02]-[B04]-[B05]
                                |
                              [C01]
                                |
                              [C05]
                                |
                [D01]-[C04]-[C09]-[C02]-[D07]
                  |     |      |      |     |
                [D02] [C08]  [C11]  [C06] [D08]
                  |     |      |      |     |
                [D03]-[D04]-[C10]-[D09]-[D10]
                  |     |      |      |     |
                [D05]-[D06]  [C12]  [D11]-[D12]
                                |
                              [C13]
                                |
                              [C07]
                                |
                              [C03]
                                |
             [E01]-[E02]-[E03]-[E05]-[E10]-[E11]-[E12]
               |                 |                 |
             [E04]             [E06]             [E13]
                                 |
                               [E07]
                                 |
                               [E08]
                            [E09]
                                |
                              [F01]
                      [F02]---[F07]---[F04]
                        |       |       |
                      [F03]---[F08]---[F05]
                                |       |
                              [F10]---[F06]
                                |
                              [F11]---[F12]
                                |
                              [G01]
                       [G02]--[G04]--[G03]
                                |
                              [G05]--[G07]
                                |
                              [G06]
                                |
                       [G09]--[G08]--[G10]
                                |
                              [G11]

                                  |
                                  v
                                SOUTH
```

---

# Visible Rooms


## A. Forward Command

- `A01` — Observation Dome
- `A02` — Forward Sensor Walk
- `A03` — Navigation Control
- `A04` — Bridge Control
- `A05` — Captain's Ready Room
- `A06` — Communications Center
- `A07` — Long-Range Antenna Control
- `A08` — Command Archive

## B. Security / Admin

- `B01` — Security Checkpoint
- `B02` — Security Hub
- `B03` — Surveillance Theater
- `B04` — Armory
- `B05` — Detention Cell
- `B06` — Admin Records

## C. Cryo Safe Haven

- `C01` — Cryo Vestibule North
- `C02` — Cryo Vestibule East
- `C03` — Cryo Vestibule South
- `C04` — Cryo Vestibule West
- `C05` — North Double-Lock Airlock
- `C06` — East Double-Lock Airlock
- `C07` — South Double-Lock Airlock
- `C08` — West Double-Lock Airlock
- `C09` — Cryo Pod Bay Alpha
- `C10` — Cryo Pod Bay Beta
- `C11` — Cryo Monitoring Station
- `C12` — Cryo Backup Power Closet
- `C13` — Cryo Secure Storage

## D. Medical / Science West-East Band

- `D01` — Medical Reception
- `D02` — Triage
- `D03` — Diagnostics
- `D04` — Surgery
- `D05` — Pharmacy
- `D06` — Morgue
- `D07` — Science Reception
- `D08` — Materials Lab
- `D09` — Spectrometry Lab
- `D10` — Xenobiology Lab
- `D11` — Specimen Storage
- `D12` — Quarantine Chamber

## E. Habitation / Commons

- `E01` — Hab West Corridor
- `E02` — Crew Quarters West
- `E03` — Laundry West
- `E04` — Lounge West
- `E05` — Main Concourse
- `E06` — Cafeteria
- `E07` — Kitchen
- `E08` — Freezer
- `E09` — Chapel
- `E10` — Hab East Corridor
- `E11` — Crew Quarters East
- `E12` — Laundry East
- `E13` — Lounge East

## F. Industrial / Engineering

- `F01` — Industrial Checkpoint
- `F02` — Fabrication Bay
- `F03` — Tool Cage
- `F04` — Environmental Control
- `F05` — Water Processing
- `F06` — Waste Processing
- `F07` — Engineering Control
- `F08` — Power Distribution
- `F09` — Generator Room
- `F10` — Reactor Monitoring
- `F11` — Reactor Chamber
- `F12` — Coolant Control

## G. Cargo / Docking

- `G01` — Cargo Spine
- `G02` — Cargo Bay A
- `G03` — Cargo Bay B
- `G04` — Cargo Sorting Office
- `G05` — Docking Control
- `G06` — Main Airlock
- `G07` — Pressure Suit Locker
- `G08` — Escape Pod Corridor
- `G09` — Escape Pod A
- `G10` — Escape Pod B
- `G11` — Aft Beacon Service

---

# Secret / Maintenance Places

- `M01` — Forward Cable Crawl
- `M02` — Bridge Underspace
- `M03` — Command Duct
- `M04` — Security Ceiling Run
- `M05` — Armory Service Gap
- `M06` — Cryo North Lock Service
- `M07` — Cryo East Lock Service
- `M08` — Cryo South Lock Service
- `M09` — Cryo West Lock Service
- `M10` — Cryo Power Crawl
- `M11` — Medical Ceiling Run
- `M12` — Surgery Sterilizer Gap
- `M13` — Morgue Cold Pipe
- `M14` — Science Filter Space
- `M15` — Specimen Vent Chase
- `M16` — Quarantine Drain Duct
- `M17` — West Laundry Pipe
- `M18` — East Laundry Pipe
- `M19` — Commons Upper Vent
- `M20` — Kitchen Service Crawl
- `M21` — Freezer Compressor Gap
- `M22` — Chapel Wall Hollow
- `M23` — Industrial Pipe Junction
- `M24` — Water Return Crawl
- `M25` — Waste Return Crawl
- `M26` — Engineering Cable Trench
- `M27` — Generator Service Pit
- `M28` — Reactor Crawlspace
- `M29` — Cargo Overhead Track
- `M30` — Airlock Bypass Tube

---

# Visible Room Exits

- `A01`: S:A02
- `A02`: N:A01, S:A03, W:M01(hidden)
- `A03`: N:A02, S:A04, E:A06, W:A05
- `A04`: N:A03, S:B01, E:A07, W:A08, Down:M02(hidden)
- `A05`: E:A03, S:A08
- `A06`: W:A03, S:A07
- `A07`: N:A06, W:A04, S:B03
- `A08`: N:A05, E:A04, S:B06
- `B01`: N:A04, S:C01, E:B02, W:B06
- `B02`: W:B01, E:B03, S:E05, Up:M04(hidden)
- `B03`: N:A07, W:B02, S:D07
- `B04`: W:B02, S:B05, Down:M05(hidden)
- `B05`: N:B04
- `B06`: N:A08, E:B01, S:D01
- `C01`: N:B01, S:C05, E:C02, W:C04
- `C02`: W:C01, S:C06, E:D07
- `C03`: N:C07, S:E05, E:C02, W:C04
- `C04`: E:C01, S:C08, W:D01
- `C05`: N:C01, S:C09, W:M06(hidden)
- `C06`: N:C02, S:C10, E:M07(hidden)
- `C07`: N:C11, S:C03, W:M08(hidden)
- `C08`: N:C04, S:C10, W:M09(hidden)
- `C09`: N:C05, E:C11, S:C10
- `C10`: N:C09, E:C11, S:C07, W:C08
- `C11`: W:C09/C10, S:C13, E:C12
- `C12`: W:C11, Down:M10(hidden)
- `C13`: N:C11
- `D01`: E:C04, S:D02, W:D05
- `D02`: N:D01, S:D03
- `D03`: N:D02, S:D04, E:E05
- `D04`: N:D03, S:D06, W:M12(hidden)
- `D05`: E:D01, S:D06
- `D06`: N:D04/D05, E:E04, W:M13(hidden)
- `D07`: W:C02, N:B03, S:D08, E:D10
- `D08`: N:D07, S:D09, Up:M14(hidden)
- `D09`: N:D08, S:D10
- `D10`: N:D07, W:D09, S:D11
- `D11`: N:D10, S:D12, Up:M15(hidden)
- `D12`: N:D11, W:E05, Down:M16(hidden)
- `E01`: N:D06, S:E02, E:E05
- `E02`: N:E01, S:E03
- `E03`: N:E02, S:E04, W:M17(hidden)
- `E04`: N:E03, E:E05
- `E05`: N:B02/C03, S:F01, W:E04/D03, E:E10/D12
- `E06`: N:E05, S:E07, W:E09
- `E07`: N:E06, S:E08, Down:M20(hidden)
- `E08`: N:E07, Down:M21(hidden)
- `E09`: E:E06, Down:M22(hidden)
- `E10`: N:D12, S:E11, W:E05
- `E11`: N:E10, S:E12
- `E12`: N:E11, S:E13, E:M18(hidden)
- `E13`: N:E12, W:E05
- `F01`: N:E05, S:F07, W:F02, E:F04
- `F02`: E:F01, S:F03, Down:M23(hidden)
- `F03`: N:F02
- `F04`: W:F01, S:F05
- `F05`: N:F04, S:F06, Down:M24(hidden)
- `F06`: N:F05, W:F07, Down:M25(hidden)
- `F07`: N:F01, S:F08, E:F06
- `F08`: N:F07, S:F10, W:F09, E:F12, Down:M26(hidden)
- `F09`: E:F08, Down:M27(hidden)
- `F10`: N:F08, S:F11
- `F11`: N:F10, S:G01, Down:M28(hidden)
- `F12`: W:F08, S:F11
- `G01`: N:F11, S:G05, W:G02, E:G03
- `G02`: E:G01, S:G04, Up:M29(hidden)
- `G03`: W:G01, S:G04, Up:M29(hidden)
- `G04`: N:G02/G03, S:G05
- `G05`: N:G01/G04, S:G06, E:G07
- `G06`: N:G05, S:G08, Down:M30(hidden)
- `G07`: W:G05
- `G08`: N:G06, S:G11, W:G09, E:G10
- `G09`: E:G08
- `G10`: W:G08
- `G11`: N:G08

---

# Secret Connectivity

- `M01` connects: A02, A05, M03
- `M02` connects: A04, M03
- `M03` connects: M01, M02, A07, M04
- `M04` connects: B02, B03, M03, M05
- `M05` connects: B04, M04, B05
- `M06` connects: C05, M10
- `M07` connects: C06, M10
- `M08` connects: C07, M10
- `M09` connects: C08, M10
- `M10` connects: C12, M06, M07, M08, M09, M11
- `M11` connects: D03, D04, M12
- `M12` connects: D04, M11, M13
- `M13` connects: D06, M12, M17
- `M14` connects: D08, D09, M15
- `M15` connects: D11, M14, M16
- `M16` connects: D12, M15, M18
- `M17` connects: E03, M13, M19
- `M18` connects: E12, M16, M19
- `M19` connects: E05, M17, M18, M20, M22
- `M20` connects: E07, M19, M21
- `M21` connects: E08, M20, M23
- `M22` connects: E09, M19, M23
- `M23` connects: F02, M21, M22, M24
- `M24` connects: F05, M23, M25
- `M25` connects: F06, M24, M26
- `M26` connects: F08, M25, M27
- `M27` connects: F09, M26, M28
- `M28` connects: F11, M27, M29
- `M29` connects: G02, G03, M28, M30
- `M30` connects: G06, G08, M29

---

# Critical Hidden Maze Routes

These routes create the horror-map feeling.

```text
A02 Forward Sensor Walk
  -> M01 Forward Cable Crawl
  -> A05 Captain's Ready Room
  -> M03 Command Duct
  -> A07 Long-Range Antenna Control

B04 Armory
  -> M05 Armory Service Gap
  -> B05 Detention Cell

D06 Morgue
  -> M13 Morgue Cold Pipe
  -> M17 West Laundry Pipe
  -> E03 Laundry West

D12 Quarantine Chamber
  -> M16 Quarantine Drain Duct
  -> M18 East Laundry Pipe
  -> E12 Laundry East

E07 Kitchen
  -> M20 Kitchen Service Crawl
  -> M21 Freezer Compressor Gap
  -> F02 Fabrication Bay

E09 Chapel
  -> M22 Chapel Wall Hollow
  -> M23 Industrial Pipe Junction
  -> F04 Environmental Control

F11 Reactor Chamber
  -> M28 Reactor Crawlspace
  -> M29 Cargo Overhead Track
  -> G02/G03 Cargo Bays

G06 Main Airlock
  -> M30 Airlock Bypass Tube
  -> G08 Escape Pod Corridor
```

---

# Random Spawn System

## Synthetics

Spawn exactly:

```text
3 synthetics per game
```

Choose one from each category.

### Maintenance / Engineering Pool

```text
F02 Fabrication Bay
F04 Environmental Control
F05 Water Processing
F08 Power Distribution
F09 Generator Room
F12 Coolant Control
```

### Medical / Science Pool

```text
D03 Diagnostics
D05 Pharmacy
D08 Materials Lab
D11 Specimen Storage
D12 Quarantine Chamber
```

### Security / Operations Pool

```text
B03 Surveillance Theater
B04 Armory
B06 Admin Records
G05 Docking Control
G07 Pressure Suit Locker
```

### Synthetic Spawn Restrictions

Do not spawn synthetics in:

```text
C09-C13 safe haven core
C05-C08 airlocks
G11 alien starting room
```

Avoid adjacent synthetic spawns unless hard mode is enabled.

## Synthetic Behavior Profiles

Assign one profile to each synthetic.

### Caretaker

Tries to send player back to cryo.

### Maintenance

Repairs systems and creates noise.

### Containment

Treats the player as a biological risk.

### Security

Blocks doors, confiscates tools, monitors access.

### Broken

Repeats old orders and behaves unpredictably.

---

# Body Placement

Spawn exactly:

```text
20 bodies per game
```

Choose from the 50-location pool below.

Never place bodies in:

```text
C05-C13
```

That keeps the safe haven clean and psychologically distinct.

## Body Spawn Pool


01. A02 Forward Sensor Walk
02. A05 Captain's Ready Room
03. A08 Command Archive
04. B01 Security Checkpoint
05. B03 Surveillance Theater
06. B05 Detention Cell
07. B06 Admin Records
08. D01 Medical Reception
09. D02 Triage
10. D03 Diagnostics
11. D04 Surgery
12. D06 Morgue
13. D08 Materials Lab
14. D09 Spectrometry Lab
15. D10 Xenobiology Lab
16. D11 Specimen Storage
17. D12 Quarantine Chamber
18. E02 Crew Quarters West
19. E03 Laundry West
20. E04 Lounge West
21. E06 Cafeteria
22. E07 Kitchen
23. E08 Freezer
24. E09 Chapel
25. E11 Crew Quarters East
26. E12 Laundry East
27. E13 Lounge East
28. F02 Fabrication Bay
29. F03 Tool Cage
30. F04 Environmental Control
31. F06 Waste Processing
32. F07 Engineering Control
33. F08 Power Distribution
34. F10 Reactor Monitoring
35. F11 Reactor Chamber
36. F12 Coolant Control
37. G02 Cargo Bay A
38. G03 Cargo Bay B
39. G04 Cargo Sorting Office
40. G07 Pressure Suit Locker
41. G08 Escape Pod Corridor
42. G11 Aft Beacon Service
43. M13 Morgue Cold Pipe
44. M16 Quarantine Drain Duct
45. M17 West Laundry Pipe
46. M18 East Laundry Pipe
47. M20 Kitchen Service Crawl
48. M23 Industrial Pipe Junction
49. M28 Reactor Crawlspace
50. M29 Cargo Overhead Track

## Recommended Body Distribution

For 20 bodies:

```text
3 Command / Security
4 Medical / Science
4 Habitation / Commons
4 Industrial / Engineering
3 Cargo / Docking
2 Secret maintenance spaces
```

## Body Detail Rolls

### Cause of Death

Roll 1d10:

1. Chest trauma
2. Crushed by a sealed door
3. Synthetic-inflicted neck injury
4. Electrical burn
5. Suffocation
6. Frozen in hiding
7. Surgical table fatality
8. Torn open in crawlspace
9. Acid damage nearby
10. Unknown

### Useful Item

Roll 1d12:

1. Battery cell
2. Wire spool
3. Level-1 keycard
4. Level-2 keycard
5. Maintenance tag
6. Audio log
7. Painkillers
8. Tape roll
9. Broken access tuner
10. Personal photo
11. Flashlight
12. Nothing

### Hazard Body

Some bodies are traps:

```text
tracker still beeping
tool drops loudly
door cannot close over body
keycard removal triggers alarm
live cable under body
synthetic watching nearby
vent opening above body
```

---

# Default Authored Spawn Example

Use this as a strong first test layout.

```text
PLAYER_START = C09 Cryo Pod Bay Alpha
ALIEN_START = G11 Aft Beacon Service

SYNTHETIC_1 = F09 Generator Room
SYNTHETIC_2 = D03 Diagnostics
SYNTHETIC_3 = B03 Surveillance Theater
```

Default bodies:

```text
A05 Captain's Ready Room
B01 Security Checkpoint
D02 Triage
D04 Surgery
D06 Morgue
D10 Xenobiology Lab
D12 Quarantine Chamber
E02 Crew Quarters West
E03 Laundry West
E06 Cafeteria
E07 Kitchen
E09 Chapel
E11 Crew Quarters East
E12 Laundry East
F02 Fabrication Bay
F06 Waste Processing
F10 Reactor Monitoring
F11 Reactor Chamber
G02 Cargo Bay A
G07 Pressure Suit Locker
```

---

# Main Missions

## Mission 1: Wake in Cryo

Start:

```text
C09 Cryo Pod Bay Alpha
```

Objectives:

- exit pod,
- reach `C11 Cryo Monitoring Station`,
- restore local cryo lights from `C12 Cryo Backup Power Closet`,
- unlock `C13 Cryo Secure Storage`,
- learn that the rest of the ship is compromised.

Reward:

- safe haven becomes fully available.

## Mission 2: Restore Emergency Generator

Main locations:

```text
F09 Generator Room
F08 Power Distribution
F03 Tool Cage
F12 Coolant Control
```

Steps:

1. Find insulated gloves in `F03 Tool Cage`.
2. Reset power routing in `F08 Power Distribution`.
3. Stabilize coolant in `F12 Coolant Control`.
4. Start generator in `F09 Generator Room`.

Complication:

- generator startup attracts the alien from aft cargo/docking toward engineering.

## Mission 3: Collect Four Radio Components

### Component 1: Transmitter Coil

Location:

```text
A07 Long-Range Antenna Control
```

Danger type:

```text
command lockdown / security synthetic
```

### Component 2: Signal Crystal

Location:

```text
D09 Spectrometry Lab
```

Danger type:

```text
science quarantine / specimen traces
```

### Component 3: Power Regulator

Location:

```text
F08 Power Distribution
```

Danger type:

```text
electrical hazard / generator noise
```

### Component 4: Antenna Coupler

Location:

```text
G11 Aft Beacon Service
```

Danger type:

```text
alien territory
```

## Mission 4: Build the Improvised Radio

Build site:

```text
C13 Cryo Secure Storage
```

Required components:

```text
Transmitter Coil
Signal Crystal
Power Regulator
Antenna Coupler
Wire Spool
Battery Cell
Tape or Sealant
```

## Mission 5: Override AI Containment

Locations:

```text
A08 Command Archive
B03 Surveillance Theater
F10 Reactor Monitoring
```

Need:

```text
Captain token
Admin cipher
Manual power authorization
```

## Mission 6: Alert Earth

Final transmission room:

```text
A07 Long-Range Antenna Control
```

Final sequence:

1. connect improvised radio,
2. align antenna,
3. divert generator power,
4. broadcast warning,
5. survive 9-12 parser turns while the message repeats.

Transmission text:

```text
This is the USCSS Nightglass. Do not board. Do not recover samples.
We have encountered a hostile organism of unknown origin.
It is adaptive, silent, and lethal.
Quarantine this vessel. Warn Earth.
```

---

# Side Missions

## Reactivate the Ship Map

Collect map fragments from:

```text
B06 Admin Records
F07 Engineering Control
G04 Cargo Sorting Office
D01 Medical Reception
```

Reward:

- reveals all visible rooms,
- does not reveal secret places.

## Trap the Alien Aft

Use:

```text
G05 Docking Control
F10 Reactor Monitoring
F04 Environmental Control
```

Reward:

- temporarily slows alien movement north.

Risk:

- alien later learns the secret route `F11 -> M28 -> M29 -> G02/G03`.

## Handle the Synthetics

Options:

- shut one down,
- reprogram one as bait,
- avoid all three,
- lure alien toward one,
- use one to open a locked door.

## Recover Crew Logs

Important logs:

```text
A05 Captain's Ready Room
D06 Morgue
D12 Quarantine Chamber
E09 Chapel
G11 Aft Beacon Service
```

---

# Access Progression

## Level 0

Starting access.

Allows:

- cryo interior,
- some commons,
- basic corridors.

## Level 1

Found in Medical or on bodies.

Allows:

- medical,
- habitation,
- some admin.

## Level 2

Found in Security or Admin.

Allows:

- security,
- science,
- command support.

## Level 3

Found in Captain's Ready Room or through AI override.

Allows:

- bridge,
- long-range comms,
- final transmission.

---

# Tools

## Cutting Torch

Suggested location:

```text
F03 Tool Cage
```

Uses:

- opens vents,
- cuts jammed panels,
- enters maintenance spaces.

## Access Tuner

Suggested location:

```text
B03 Surveillance Theater
```

Uses:

- hacks doors,
- reroutes locks,
- distracts synthetics.

## Motion Tracker

Suggested location:

```text
B02 Security Hub
```

Uses:

- detects movement,
- unreliable near reactor,
- cannot distinguish alien from synthetic at first.

## Insulated Gloves

Suggested location:

```text
F03 Tool Cage
```

Uses:

- repairs generator,
- handles power regulator,
- survives electrical hazards.

---

# Sound Rules

Loud actions attract the alien.

## Loud

```text
running
forcing doors
starting generator
dropping tools
cycling airlock
activating antenna
firing weapon
knocking shelves
```

## Quiet

```text
crawling
waiting
listening
hiding
closing doors slowly
examining
```

## Warning Cues

Use these before direct danger:

```text
A vent cover ticks once.
A pipe flexes overhead.
The motion tracker chirps, then dies.
Something moves behind the wall.
A synthetic voice begins speaking two rooms away.
The lights dim from south to north.
```

---

# Alien Encounter Tiers

## Tier 0: Distant

```text
Far aft, something heavy moves through cargo.
```

## Tier 1: Nearby

```text
The ceiling gives a soft metallic pop.
```

## Tier 2: Adjacent

```text
The room seems to listen before you do.
```

## Tier 3: Same Room

```text
It unfolds from the dark too smoothly to be an animal.
```

---

# Fairness Rules

Never:

- spawn alien near cryo at start,
- allow alien inside safe haven,
- spawn bodies in safe haven,
- spawn all synthetics in one zone,
- block every route to a required component,
- trap the player forever outside cryo.

Always ensure:

- one route from cryo to commons,
- one route from commons to engineering,
- one route from engineering to cargo,
- one route from cargo back to cryo,
- one route to command,
- one way to build the radio,
- one way to transmit.

## Anti-Camping Rule

If alien waits outside safe haven:

```text
after 5 turns: alien investigates another nearby sound
after 8 turns: alien moves to adjacent corridor
after 12 turns: alien leaves cryo boundary unless final mission is active
```

---

# Parser Command Suggestions

```text
LOOK
LOOK NORTH
GO NORTH
OPEN DOOR
LOCK DOOR
HIDE
LISTEN
WAIT
SEARCH BODY
SEARCH ROOM
ENTER VENT
CRAWL EAST
USE KEYCARD
USE ACCESS TUNER ON DOOR
TAKE ITEM
DROP ITEM
CRAFT RADIO
CHECK TRACKER
READ TERMINAL
SAVE
REST
```

---

# Quick Implementation Constants

```text
VISIBLE_ROOM_COUNT = 75
SECRET_PLACE_COUNT = 30
SYNTHETICS_PER_GAME = 3
BODY_SPAWN_POOL = 50
BODIES_PER_GAME = 20

PLAYER_START_ROOM = C09
ALIEN_START_ROOM = G11

SAFE_HAVEN_CORE = C09,C10,C11,C12,C13
SAFE_HAVEN_AIRLOCKS = C05,C06,C07,C08
ALIEN_FORBIDDEN = C09,C10,C11,C12,C13

GENERATOR_ROOM = F09
RADIO_BUILD_ROOM = C13
FINAL_TRANSMISSION_ROOM = A07
```

---

# Designer Note

This downsized version should feel less like a full space station and more like a tight commercial research ship.

The player should be able to learn the whole vessel, but not relax inside it.

The ship is small enough to remember.
The walls are still full of teeth.
