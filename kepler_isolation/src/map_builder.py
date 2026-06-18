"""
Map builder for KEPLER ISOLATION game.
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
    # The reactor is a scanner-dead dead-end; cover keeps it from being a trap.
    "reactor_room": [{"name": "behind the coolant tanks", "quality": 35, "reuse": 0}],
    "communications": [{"name": "under console", "quality": 30, "reuse": 0}],
    "storage": [{"name": "shelving", "quality": 40, "reuse": 0}],
    # A slim, low-quality option on the final approach so a camped door is never
    # an outright softlock — but it's a last resort, not safe cover.
    "comms_hall": [{"name": "equipment alcove", "quality": 25, "reuse": 0}],
}

TOXIC_ROOMS = {"surface", "landing_gear", "ridge", "cave_mouth", "signal_cave", "black_pool"}

# --- Narrative readables (the story is assembled from fragments, never told) ---

MEMO_TEXT = (
    "HALLOWAY-TANAKA INDUSTRIES — INTERNAL. Re: Kepler-186f, vessel LANTERN-9.\n"
    "Objective: recover the biological specimen intact.\n"
    "Assets are recoverable. Crews perform best uninformed.\n"
    "Welcome aboard. Build something that lasts."
)

RECORDER_TEXT = (
    "\"—don't transmit. Whatever you do, don't answer it.\"\n"
    "A long pause. Then, quieter:\n"
    "\"It learned the beacon. It's using the beacon now.\"\n"
    "\"I can't hear it anymore. It's in the walls.\""
)

BEACON_TEXT = (
    "DO NOT— (static) —is not a distress call.\n"
    "We sent it to warn you. They turned it around.\n"
    "It is bait now. We are the proof. DO NOT—"
)

FRAGMENT_TEXT = (
    "A scorched transmitter shard, still warm to read:\n"
    "\"...to anyone who is not the company: turn the ship around.\n"
    "The signal is the—\" (the rest is melted slag)"
)

HELMET_TEXT = (
    "Scratched inside the shell, in a shaking hand:\n"
    "MERCER WAS HERE. MERCER IS STILL HERE."
)


def create_rooms():
    """Create all 22 rooms with their properties and exits."""
    rooms = {}

    # --- Ship ---
    rooms["cockpit"] = Room(
        name="Cockpit",
        description="Dead stars in the glass. The console holds one green light, patient.\n"
                    "Your descent pod is still warm. You don't remember climbing out.",
        items=[
            Item("hand terminal", "terminal,scanner", "A rugged hand scanner. It reads motion — direction and distance. Company-issue.", portable=True),
            Item("company memo", "memo,letter,paper", "A Halloway-Tanaka directive, printed on real paper. Someone wanted it deniable.", portable=True, readable_text=MEMO_TEXT),
        ],
        exits={"south": "central_corridor"},
        hidden_items=[],
    )
    rooms["central_corridor"] = Room(
        name="Central Corridor",
        description="Low ceiling. Handrails worn smooth by hands that aren't aboard.\n"
                    "The lights hum in pairs. A safety label has been taped over.",
        items=[],
        exits={"north": "cockpit", "east": "airlock", "south": "med_bay", "west": "engineering_access"},
        hidden_items=[],
    )
    rooms["airlock"] = Room(
        name="Airlock",
        description="A narrow chamber. Suit locker, inner hatch, outer hatch.\n"
                    "A red placard: TWO MOVES WITHOUT SEAL. Someone underlined TWO.",
        items=[Item("EVA suit", "suit,eva", "A hard-shell EVA suit. Helmet, gloves, seals. It smells faintly of someone else.", portable=True, wearable=True)],
        exits={"west": "central_corridor", "out": "surface"},
        hidden_items=[],
    )
    rooms["med_bay"] = Room(
        name="Med Bay",
        description="Supplies behind glass. A recorder log waits on the table, already cued.\n"
                    "The cot has restraint straps. They buckle on the outside.",
        items=[
            Item("medkit", "medic,kit", "A field medical kit. Stims and sealant, and a card that reads USE SPARINGLY.", portable=True),
            Item("recorder log", "log,note,recording", "A crew recording, cued to its final entry.", portable=True,
                 readable_text=RECORDER_TEXT),
        ],
        exits={"north": "central_corridor", "east": "crew_quarters"},
        hidden_items=[],
    )
    rooms["crew_quarters"] = Room(
        name="Crew Quarters",
        description="Bunks and dented lockers. Old coffee, and under it, nothing at all.\n"
                    "A synthetic sits powered-down against the wall. Its plate reads SABLE.",
        items=[Item("access card", "card,id", "A Halloway-Tanaka access card. The photo has been scratched out.", portable=True)],
        exits={"west": "med_bay", "south": "galley"},
        hidden_items=[],
    )
    rooms["galley"] = Room(
        name="Galley",
        description="A cramped galley. Cans rolled loose across the deck, never collected.\n"
                    "A mug stands half-full. The coffee in it has skinned over.",
        items=[Item("loose can", "can", "An empty ration can. Light enough to throw. Loud enough to matter.", portable=True, sound_on_use=3)],
        exits={"north": "crew_quarters", "west": "storage"},
        hidden_items=[],
    )
    rooms["storage"] = Room(
        name="Storage",
        description="Shelving and strapped crates. Maintenance tags curl in the dry air.\n"
                    "A tally is scratched into one shelf, counting down. It ends at one.",
        items=[
            Item("power coupler", "coupler", "A power coupling unit. Heavy. Stamped with a hull number that isn't this hull.", portable=True, required_for_win=True),
            Item("flare", "flares", "An emergency flare. It burns loud and bright, and tells everything exactly where you are.", portable=True, sound_on_use=3),
        ],
        exits={"east": "galley", "south": "cargo_bay", "west": "engineering_access"},
        hidden_items=[],
    )
    rooms["engineering_access"] = Room(
        name="Engineering Access",
        description="The throat of a passage. A panel hangs open over a black crawlspace.\n"
                    "The crawlspace breathes a draft that smells of the world outside.",
        items=[Item("repair kit", "kit,tools", "A repair kit. Someone already used half of it, in a hurry, badly.", portable=True)],
        exits={"east": "central_corridor", "south": "reactor_room", "west": "storage"},
        hidden_items=[],
    )
    rooms["reactor_room"] = Room(
        name="Reactor Room",
        description="The reactor roars with heat. The noise eats every smaller sound —\n"
                    "yours, and not only yours.",
        items=[Item("signal relay", "relay", "A signal relay. Company-grey. Built to make a small voice carry very far.", portable=True, required_for_win=True)],
        exits={"north": "engineering_access"},
        hidden_items=[],
    )
    rooms["cargo_bay"] = Room(
        name="Cargo Bay",
        description="Tall crates, a dead forklift, dark pooling in the corners like water.\n"
                    "The wall manifest lists more cargo than was ever unloaded.",
        items=[Item("antenna key", "key", "An antenna tuning key, worn to a shine by hands that needed it before you.", portable=True, required_for_win=True)],
        exits={"north": "storage", "east": "maintenance_junction", "south": "lower_hold"},
        hidden_items=[],
    )
    rooms["lower_hold"] = Room(
        name="Lower Hold",
        description="A dead-end. Scratch marks rake the walls, low down, as if dragged.\n"
                    "The air is colder here, and it moves when nothing should move it.",
        items=[Item("beacon fragment", "fragment", "A scorched shard of an older beacon.", portable=True, readable_text=FRAGMENT_TEXT)],
        exits={"north": "cargo_bay"},
        hidden_items=[],
    )
    rooms["maintenance_junction"] = Room(
        name="Maintenance Junction",
        description="A junction of service tunnels. A tool rack of mostly bare hooks.\n"
                    "Grease handprints climb one wall. One of them has too many fingers.",
        items=[],
        exits={"west": "cargo_bay", "east": "comms_hall", "north": "ventral_service"},
        hidden_items=[],
    )
    rooms["ventral_service"] = Room(
        name="Ventral Service",
        description="A mechanical crawl. A fan turns somewhere, ragged, like it is tired.\n"
                    "The ducts here are wide enough for a person. Or for less than one.",
        items=[],
        exits={"south": "maintenance_junction", "east": "observation"},
        hidden_items=[],
    )
    rooms["observation"] = Room(
        name="Observation",
        description="A long window. The planet leans its dark face against the glass.\n"
                    "Your reflection looks thin out here, as if the dark is using it up.",
        items=[],
        exits={"west": "ventral_service", "south": "comms_hall"},
        hidden_items=[],
    )
    rooms["comms_hall"] = Room(
        name="Comms Hall",
        description="The last stretch before Communications. Equipment lines the walls.\n"
                    "The air has the quality of being held. Of being watched, and waited on.",
        items=[],
        exits={"north": "observation", "west": "maintenance_junction", "east": "communications"},
        hidden_items=[],
    )
    rooms["communications"] = Room(
        name="Communications",
        description="A dead microphone. The transmitter gapes — three empty sockets.\n"
                    "A chair faces it, turned as if someone left mid-sentence.",
        items=[],
        exits={"west": "comms_hall"},
        hidden_items=[],
    )

    # --- Surface / cave ---
    rooms["surface"] = Room(
        name="Surface",
        description="Black dust moves like slow smoke. Your suit light gropes east, to a ridge.\n"
                    "Behind you the lander ticks as it cools. Then it stops ticking.",
        items=[],
        exits={"in": "airlock", "east": "ridge", "south": "landing_gear"},
        hidden_items=[],
    )
    rooms["landing_gear"] = Room(
        name="Landing Gear",
        description="A bent strut, fused with an old impact. Tools half-buried in the dust.\n"
                    "Nothing else out here. Not yet.",
        items=[],
        exits={"north": "surface"},
        hidden_items=[],
    )
    rooms["ridge"] = Room(
        name="Ridge",
        description="A narrow spine of rock. The cave mouth gapes east, exhaling cold.\n"
                    "The signal is stronger here. It almost sounds like a voice you know.",
        items=[],
        exits={"west": "surface", "east": "cave_mouth"},
        hidden_items=[],
    )
    rooms["cave_mouth"] = Room(
        name="Cave Mouth",
        description="The signal is louder here. Not stronger. Louder.\n"
                    "The walls are slick. Your light won't find the bottom of the dark below.",
        items=[],
        exits={"west": "ridge", "down": "signal_cave"},
        hidden_items=[],
    )
    rooms["signal_cave"] = Room(
        name="Signal Cave",
        description="Wet walls, scored with marks that are neither tools nor claws.\n"
                    "A beacon blinks in the dark, patient, repeating three soft tones.",
        items=[Item("distress beacon", "beacon,signal", "An old beacon, undegraded. That should not be possible. It listens while it calls.",
                    portable=False, readable_text=BEACON_TEXT)],
        exits={"up": "cave_mouth", "east": "black_pool"},
        hidden_items=[],
    )
    rooms["black_pool"] = Room(
        name="Black Pool",
        description="A still pool of black liquid that gives your light nothing back.\n"
                    "At its edge, folded small and wet like paper, something waits to be warm.",
        items=[Item("old helmet", "helmet", "A cracked EVA helmet. Not from your crew.", portable=True, readable_text=HELMET_TEXT)],
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
    # The trick is repetition-with-variation: a familiar detail, changed. The
    # ship stops being a ship and starts being the inside of something.
    aboard = {
        "cockpit": "Dead stars. The one green light still waits.\n"
                   "Your reflection sits in the chair behind you. You are standing.",
        "central_corridor": "The lights hum in pairs. One pair has gone dark.\n"
                            "The old boot marks lead somewhere they didn't before.",
        "airlock": "Inner hatch, outer hatch. The outer seal is scored from the\n"
                   "outside. The placard still reads: TWO MOVES WITHOUT SEAL.",
        "med_bay": "Supplies behind cracked glass. The recorder log lies untouched.\n"
                   "The cabinet hangs open. You did not open it. The straps are undone.",
        "crew_quarters": "Bunks and lockers. The smell of old coffee is gone.\n"
                         "Something low and animal has moved in to replace it.",
        "galley": "The cans are scattered wider now. A few are flattened,\n"
                  "as if something heavy passed through and did not care.",
        "storage": "Boxes shoved aside. A path cleared low to the floor, the width\n"
                   "of a body that does not walk upright.",
        "engineering_access": "The narrow passage. The open panel over the\n"
                              "crawlspace gapes wider than you left it. The draft is warm.",
        "reactor_room": "The reactor roars. Good — the noise hides you.\n"
                        "The noise hides it, too.",
        "cargo_bay": "Tall crates, the dead forklift, the pooling dark.\n"
                     "The dark is arranged differently than you left it.",
        "lower_hold": "A dead end. The scratch marks are fresh now, and wet,\n"
                      "and they reach higher up the wall than your arm can.",
        "maintenance_junction": "The junction of tunnels. One vent grille is peeled\n"
                               "outward from the inside. Bright petals of torn metal.",
        "ventral_service": "The fan has stopped. In the new quiet you can hear it\n"
                           "move through the ducts. Unhurried. Patient as the beacon.",
        "observation": "The long window holds the planet's dark face.\n"
                       "Twice now, something has crossed it — on the inside of the glass.",
        "comms_hall": "The final approach. The equipment lights flicker in sequence,\n"
                      "as if something keeps brushing the wall. The air is held.",
        "communications": "A dead microphone. The transmitter, three sockets open.\n"
                          "Behind you the corridor breathes. In, and out, and in.",
        "landing_gear": "The bent strut. Fresh slime threads the metal — a trail\n"
                        "climbing the hull, toward the airlock. Toward inside.",
    }
    for room_id, text in aboard.items():
        rooms[room_id].variants["aboard"] = text

    # Vents (monster only)
    for a, b in VENTS:
        rooms[a].vent_exits.append(b)
        rooms[b].vent_exits.append(a)

    return rooms
