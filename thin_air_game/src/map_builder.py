"""
Map builder for THE THIN AIR game.
Creates and initializes all rooms with their exits, items, hazards, vents,
hiding spots, and sound/scanner properties.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from room import Room
from item import Item

# Monster-only vent shortcuts (bidirectional).
VENTS = [
    ("airlock", "ventral_service"),
    ("cargo_bay", "reactor_room"),
    ("observation", "central_corridor"),
    ("med_bay", "maintenance_junction"),
]

# room_id -> list of hiding spots
HIDING_SPOTS = {
    "med_bay": [{"name": "cabinet", "quality": 45, "reuse": 0}],
    "crew_quarters": [{"name": "under bunk", "quality": 35, "reuse": 0}],
    "cargo_bay": [{"name": "behind crates", "quality": 50, "reuse": 0}],
    "engineering_access": [{"name": "crawlspace", "quality": 40, "reuse": 0}],
    "communications": [{"name": "under console", "quality": 30, "reuse": 0}],
    "storage": [{"name": "shelving", "quality": 40, "reuse": 0}],
}

TOXIC_ROOMS = {"surface", "landing_gear", "ridge", "cave_mouth", "signal_cave", "black_pool"}


def create_rooms():
    """Create all 22 rooms with their properties and exits."""
    rooms = {}

    # --- Ship ---
    rooms["cockpit"] = Room(
        name="Cockpit",
        description="Dead stars in the glass. The console waits with one green light.",
        items=[Item("hand terminal", "terminal,scanner", "A rugged motion scanner. It reads direction and distance.", portable=True)],
        exits={"south": "central_corridor"},
        hidden_items=[],
    )
    rooms["central_corridor"] = Room(
        name="Central Corridor",
        description="Low ceiling. Handrails. Old boot marks. The lights hum in pairs.",
        items=[],
        exits={"north": "cockpit", "east": "airlock", "south": "med_bay", "west": "engineering_access"},
        hidden_items=[],
    )
    rooms["airlock"] = Room(
        name="Airlock",
        description="A narrow chamber. Suit locker, outer hatch, inner hatch.\nA red card reads: TWO MOVES WITHOUT SEAL.",
        items=[Item("EVA suit", "suit,eva", "A full EVA suit. Helmet, gloves, hard seals.", portable=True, wearable=True)],
        exits={"west": "central_corridor", "out": "surface"},
        hidden_items=[],
    )
    rooms["med_bay"] = Room(
        name="Med Bay",
        description="Medical supplies behind glass. A recorder log sits on the table.",
        items=[
            Item("medkit", "medic,kit", "A small medical kit.", portable=True),
            Item("recorder log", "log,note,recording", "A crew recording.", portable=True,
                 readable_text="\"I can't hear it anymore.\nIt's in the walls.\""),
        ],
        exits={"north": "central_corridor", "east": "crew_quarters"},
        hidden_items=[],
    )
    rooms["crew_quarters"] = Room(
        name="Crew Quarters",
        description="Bunks and personal lockers. A faint smell of old coffee.",
        items=[Item("access card", "card,id", "A corporate access card.", portable=True)],
        exits={"west": "med_bay", "south": "galley"},
        hidden_items=[],
    )
    rooms["galley"] = Room(
        name="Galley",
        description="A cramped kitchen. Loose cans scattered across the floor.",
        items=[Item("loose can", "can", "An empty can. Light. Throwable.", portable=True, sound_on_use=3)],
        exits={"north": "crew_quarters", "west": "storage"},
        hidden_items=[],
    )
    rooms["storage"] = Room(
        name="Storage",
        description="Boxes and crates. Maintenance tags curl off a shelf.",
        items=[
            Item("power coupler", "coupler", "A power coupling unit. Heavy.", portable=True, required_for_win=True),
            Item("flare", "flares", "An emergency flare. Burns loud and bright.", portable=True, sound_on_use=3),
        ],
        exits={"east": "galley", "south": "cargo_bay", "west": "engineering_access"},
        hidden_items=[],
    )
    rooms["engineering_access"] = Room(
        name="Engineering Access",
        description="A narrow passage. A panel hangs open over a crawlspace.",
        items=[Item("repair kit", "kit,tools", "A basic repair kit.", portable=True)],
        exits={"east": "central_corridor", "south": "reactor_room", "west": "storage"},
        hidden_items=[],
    )
    rooms["reactor_room"] = Room(
        name="Reactor Room",
        description="The reactor roars with heat. The noise drowns everything small.",
        items=[Item("signal relay", "relay", "A signal transmission relay.", portable=True, required_for_win=True)],
        exits={"north": "engineering_access"},
        hidden_items=[],
    )
    rooms["cargo_bay"] = Room(
        name="Cargo Bay",
        description="Tall crates and a dead forklift. The dark pools in the corners.",
        items=[Item("antenna key", "key", "An antenna tuning key.", portable=True, required_for_win=True)],
        exits={"north": "storage", "east": "maintenance_junction", "south": "lower_hold"},
        hidden_items=[],
    )
    rooms["lower_hold"] = Room(
        name="Lower Hold",
        description="A dead-end space. Scratch marks rake the walls, low down.",
        items=[Item("beacon fragment", "fragment", "A shard of an old distress beacon.", portable=True)],
        exits={"north": "cargo_bay"},
        hidden_items=[],
    )
    rooms["maintenance_junction"] = Room(
        name="Maintenance Junction",
        description="A junction of service tunnels. A tool rack, mostly empty.",
        items=[],
        exits={"west": "cargo_bay", "east": "comms_hall", "north": "ventral_service"},
        hidden_items=[],
    )
    rooms["ventral_service"] = Room(
        name="Ventral Service",
        description="A mechanical crawl. A fan turns somewhere, ragged.",
        items=[],
        exits={"south": "maintenance_junction", "east": "observation"},
        hidden_items=[],
    )
    rooms["observation"] = Room(
        name="Observation",
        description="A long window. The planet presses its dark face against the glass.",
        items=[],
        exits={"west": "ventral_service", "south": "comms_hall"},
        hidden_items=[],
    )
    rooms["comms_hall"] = Room(
        name="Comms Hall",
        description="The final approach. Equipment lines the walls. The air feels watched.",
        items=[],
        exits={"north": "observation", "west": "maintenance_junction", "east": "communications"},
        hidden_items=[],
    )
    rooms["communications"] = Room(
        name="Communications",
        description="A dead microphone. A damaged transmitter with three open sockets.",
        items=[],
        exits={"west": "comms_hall"},
        hidden_items=[],
    )

    # --- Surface / cave ---
    rooms["surface"] = Room(
        name="Surface",
        description="Black dust moves like smoke. Your light finds the ridge east.",
        items=[],
        exits={"in": "airlock", "east": "ridge", "south": "landing_gear"},
        hidden_items=[],
    )
    rooms["landing_gear"] = Room(
        name="Landing Gear",
        description="A bent strut. Later there will be slime here. Not yet.",
        items=[],
        exits={"north": "surface"},
        hidden_items=[],
    )
    rooms["ridge"] = Room(
        name="Ridge",
        description="A narrow spine of rock. The cave mouth gapes east.",
        items=[],
        exits={"west": "surface", "east": "cave_mouth"},
        hidden_items=[],
    )
    rooms["cave_mouth"] = Room(
        name="Cave Mouth",
        description="The signal is louder here. Not stronger. Louder.",
        items=[],
        exits={"west": "ridge", "down": "signal_cave"},
        hidden_items=[],
    )
    rooms["signal_cave"] = Room(
        name="Signal Cave",
        description="Wet walls, strange markings. A beacon blinks in the dark.",
        items=[Item("distress beacon", "beacon,signal", "A beacon, old but undegraded. That should not be possible.",
                    portable=False, readable_text="DO NOT OPEN THE—")],
        exits={"up": "cave_mouth", "east": "black_pool"},
        hidden_items=[],
    )
    rooms["black_pool"] = Room(
        name="Black Pool",
        description="A still pool of black liquid. Something folded lies at its edge, like wet paper.",
        items=[Item("old helmet", "helmet", "A cracked helmet. Not from your crew.", portable=True)],
        exits={"west": "signal_cave"},
        hidden_items=[],
    )

    # --- Apply IDs and shared properties ---
    for room_id, room in rooms.items():
        room.id = room_id
        if room_id in TOXIC_ROOMS:
            room.toxic = True
        if room_id in HIDING_SPOTS:
            room.hiding_spots = HIDING_SPOTS[room_id]

    # Ambient sound / scanner interference
    rooms["reactor_room"].ambient_sound = 3
    rooms["reactor_room"].scanner_interference = True
    rooms["cargo_bay"].ambient_sound = 2
    rooms["galley"].ambient_sound = 1
    for cave_id in ("signal_cave", "black_pool", "cave_mouth"):
        rooms[cave_id].scanner_interference = True

    # --- Dread pass: how each room reads once the creature is aboard ---
    # The trick is repetition-with-variation: a familiar detail, changed.
    aboard = {
        "cockpit": "Dead stars in the glass. The one green light still waits.\n"
                   "Your own reflection sits in the chair behind you. You are standing.",
        "central_corridor": "The lights hum in pairs. One pair has gone dark.\n"
                            "The old boot marks lead somewhere they didn't before.",
        "airlock": "Inner hatch, outer hatch. The outer seal is scored from the\n"
                   "outside. The red card still reads: TWO MOVES WITHOUT SEAL.",
        "med_bay": "Supplies behind cracked glass. The recorder log lies untouched.\n"
                   "The cabinet door hangs open. You did not open it.",
        "crew_quarters": "Bunks and lockers. The smell of old coffee is gone.\n"
                         "Something low and animal has taken its place.",
        "galley": "The cans are scattered wider now. A few are flattened,\n"
                  "as if something heavy passed without caring.",
        "storage": "Boxes shoved aside. A path cleared through them, low to the\n"
                   "floor, the width of a body that does not walk upright.",
        "engineering_access": "The narrow passage. The open panel over the\n"
                              "crawlspace gapes wider than you left it.",
        "reactor_room": "The reactor roars with heat. Good — the noise hides you.\n"
                        "The noise hides it, too.",
        "cargo_bay": "Tall crates, the dead forklift, the pooling dark.\n"
                     "The dark is arranged differently than before.",
        "lower_hold": "A dead end. The scratch marks are fresh now, and wet,\n"
                      "and they go higher up the wall than your reach.",
        "maintenance_junction": "The junction of tunnels. One vent grille has been\n"
                               "peeled outward from inside. Petals of bright metal.",
        "ventral_service": "The fan has stopped. In the new quiet you can hear it\n"
                           "move through the ducts. Unhurried.",
        "observation": "The long window holds the planet's dark face.\n"
                       "Twice now, something has crossed it — on the inside of the glass.",
        "comms_hall": "The final approach. The equipment lights flicker in sequence,\n"
                      "as if something keeps brushing the wall. The air is watched.",
        "communications": "A dead microphone. The transmitter, three sockets open.\n"
                          "Behind you, the corridor breathes.",
        "landing_gear": "The bent strut. Fresh slime threads the metal — a trail\n"
                        "leading up the hull, toward the airlock. Toward inside.",
    }
    for room_id, text in aboard.items():
        rooms[room_id].variants["aboard"] = text

    # Vents (monster only)
    for a, b in VENTS:
        rooms[a].vent_exits.append(b)
        rooms[b].vent_exits.append(a)

    return rooms
