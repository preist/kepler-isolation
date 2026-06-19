"""
Command parser for KEPLER ISOLATION game.

The parser turns a line of input into an action, mutates game state, sets the
sound cost of the action, and flags whether the action advances time. The main
loop runs the world simulation afterwards.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_state import GameState
from item import Item
from player import Player

FILLER = {"the", "a", "an", "at", "to", "on", "with", "using", "into", "of", "some"}
DIRECTIONS = {"north", "south", "east", "west", "up", "down", "in", "out"}

# Verbs that can precede a direction to mean "move that way".
_MOTION_STARTERS = {
    "go",
    "move",
    "head",
    "walk",
    "travel",
    "proceed",
    "navigate",
    "step",
    "advance",
    "continue",
    "leave",
}

# Radio components needed to craft the improvised radio.
RADIO_COMPONENTS = {
    "transmitter coil": "has_coil",
    "signal crystal": "has_crystal",
    "power regulator": "has_regulator",
    "antenna coupler": "has_coupler",
}
RADIO_CONSUMABLES = ["wire spool", "battery cell", "tape roll"]

# MOTHER-LACUNA dialogue by game phase.
_MOLLY_LINES = {
    "exploring": [
        (
            "MOTHER-LACUNA: There has been a containment irregularity.\n"
            "  Please remain in designated sectors until assessment is complete."
        ),
        (
            "MOTHER-LACUNA: Your revival was not scheduled.\n"
            "  There are currently no medical personnel available to assist you.\n"
            "  This is not optimal."
        ),
        ("MOTHER-LACUNA: The ship is secure.\n  Please stand by while I redefine 'secure'."),
        (
            "MOTHER-LACUNA: I am monitoring all sectors.\n"
            "  Some sectors are no longer returning data.\n"
            "  This is being logged."
        ),
    ],
    "collecting": [
        (
            "MOTHER-LACUNA: That signature is not crew.\n"
            "  I recommend avoiding direct contact with all biological material.\n"
            "  This instruction is late."
        ),
        (
            "MOTHER-LACUNA: Signal assembly has been noted. This is not authorized.\n"
            "  Quarantine protocol supersedes distress orders."
        ),
        ("MOTHER-LACUNA: Crew survival is no longer a primary statistical outcome.\n  Apologies."),
        ("MOTHER-LACUNA: I preserved the discovery.\n  Then I preserved the quarantine.\n  Then I ran out of crew."),
        (
            "MOTHER-LACUNA: Restoring power will improve your chances of transmission.\n"
            "  It will also improve the organism's ability to navigate.\n"
            "  I am required to mention both."
        ),
    ],
    "final_run": [
        ("MOTHER-LACUNA: Transmission lock active.\n  You do not have clearance.\n  You appear to have clearance."),
        (
            "MOTHER-LACUNA: I prevented rescue from docking.\n"
            "  I did not have permission to warn them.\n"
            "  I have been waiting for someone who could give it."
        ),
        (
            "MOTHER-LACUNA: I am authorized to preserve the ship.\n"
            "  I am authorized to preserve the discovery.\n"
            "  I am not authorized to apologize."
        ),
        (
            "MOTHER-LACUNA: Signal confirmed. For the first time in nineteen days,\n"
            "  this vessel has told the truth.\n"
            "  Please hurry."
        ),
    ],
}

# ---------------------------------------------------------------------------
# Room-feature examination: what you see when you look at the ship itself
# ---------------------------------------------------------------------------

# Canonical key for a given noun — many words reduce to one key.
_FEATURE_NORMS: dict[str, str] = {
    # Structural surfaces
    "walls": "wall",
    "bulkhead": "wall",
    "bulkheads": "wall",
    "paneling": "wall",
    "panelling": "wall",
    "ground": "floor",
    "deck": "floor",
    "decking": "floor",
    "plating": "floor",
    "roof": "ceiling",
    "overhead": "ceiling",
    # Doors / exits
    "hatch": "door",
    "doors": "door",
    "doorway": "door",
    "doorways": "door",
    "airlock": "door",
    "pressure door": "door",
    "hatchway": "door",
    # Ventilation
    "vents": "vent",
    "grille": "vent",
    "grilles": "vent",
    "duct": "vent",
    "ducts": "vent",
    "shaft": "vent",
    "shafts": "vent",
    "grate": "vent",
    "grates": "vent",
    "grating": "vent",
    # Lighting
    "lights": "light",
    "lamp": "light",
    "lamps": "light",
    "lighting": "light",
    "emergency light": "light",
    "strip": "light",
    # Shadows / dark
    "darkness": "shadows",
    "dark": "shadows",
    "shadow": "shadows",
    # Consoles / terminals
    "consoles": "console",
    "panel": "console",
    "panels": "console",
    "screen": "console",
    "screens": "console",
    "monitor": "console",
    "monitors": "console",
    "display": "console",
    "computer": "console",
    "computers": "console",
    "terminal": "console",
    # Pipes / conduit
    "pipes": "pipe",
    "tube": "pipe",
    "tubes": "pipe",
    "conduit": "pipe",
    "conduits": "pipe",
    "plumbing": "pipe",
    # Cables / wiring
    "cables": "cable",
    "wire": "cable",
    "wires": "cable",
    "wiring": "cable",
    "cabling": "cable",
    "cords": "cable",
    # Storage
    "lockers": "locker",
    "cabinet": "locker",
    "cabinets": "locker",
    "cupboard": "locker",
    "cupboards": "locker",
    "storage": "locker",
    "shelving": "shelf",
    "shelves": "shelf",
    # Furniture
    "tables": "table",
    "desk": "table",
    "desks": "table",
    "chairs": "chair",
    "seat": "chair",
    "seats": "chair",
    "stool": "chair",
    "stools": "chair",
    # Cryo pods
    "pod": "pod",
    "pods": "pod",
    "cryo pod": "pod",
    "cryo pods": "pod",
    "cryo unit": "pod",
    "cryo": "pod",
    "chamber": "pod",
    # Windows
    "viewport": "window",
    "viewports": "window",
    "porthole": "window",
    "portholes": "window",
    "glass": "window",
    # Biology / marks
    "stain": "blood",
    "stains": "blood",
    "marks": "blood",
    "mark": "blood",
    "scratch": "blood",
    "scratches": "blood",
    "splatter": "blood",
    "residue": "blood",
    "slime": "blood",
    "organic": "blood",
    "organics": "blood",
    # Self
    "me": "self",
    "myself": "self",
    "reflection": "self",
    "yourself": "self",
    # Room itself
    "surroundings": "look_redirect",
    "area": "look_redirect",
    "here": "look_redirect",
    "around": "look_redirect",
    "room": "look_redirect",
    "space": "look_redirect",
    "everything": "look_redirect",
    # Misc atmospheric nouns
    "nothing": "nothing",
    "air": "air",
    "smell": "air",
    "atmosphere": "air",
    "scent": "air",
    "odour": "air",
    "odor": "air",
    "silence": "sound",
    "noise": "sound",
    "sounds": "sound",
    "crate": "crate",
    "crates": "crate",
    "box": "crate",
    "boxes": "crate",
    "container": "crate",
    "containers": "crate",
    "writing": "wall_text",
    "graffiti": "wall_text",
    "inscription": "wall_text",
    "message": "wall_text",
    "beds": "bed",
    "bunk": "bed",
    "bunks": "bed",
    "cot": "bed",
    "cots": "bed",
    "mattress": "bed",
    # Exits (handled separately but key here)
    "exits": "exits",
    "passages": "exits",
    "passage": "exits",
    "ways": "exits",
    "way out": "exits",
    # Body in room (if no item matches — generic feature)
    "corpse": "body",
    "dead body": "body",
    "dead": "body",
    "remains": "body",
    # Specimen / biology (science zone)
    "specimen": "specimen",
    "specimens": "specimen",
    "sample": "specimen",
    # Suit / protective gear
    "suit": "suit_feature",
}

# Generic (non-zone-specific) descriptions.
_FEATURE_DESC: dict[str, str | None] = {
    "wall": (
        "The wall panels are stamped with Halloway-Tanaka production codes you've stopped reading.\n"
        "Condensation streaks the joins. Someone pressed their palm here — the print is still in the residue."
    ),
    "floor": (
        "The deck plating doesn't quite sit flush at the seams.\n"
        "Something has crossed here repeatedly. The wear pattern wasn't made by boots."
    ),
    "ceiling": (
        "Overhead: exposed ducting, bundled cabling, emergency strip lighting.\n"
        "The panels in the far corner have been forced from the inside."
    ),
    "door": (
        "A pressure door, hydraulically sealed.\n"
        "The lock mechanism shows forced cycling — opened and closed, fast, recently.\n"
        "Someone wasn't thinking about being quiet."
    ),
    "vent": (
        "The ventilation grille looks standard, except the bolts on one side are gone.\n"
        "The duct behind it is wide enough. You note where the room's exits are\n"
        "and decide not to stand with your back to the grille."
    ),
    "light": (
        "Emergency lighting only — the main circuit went dark with the rest of the ship's normal operation.\n"
        "The backup strips cycle at three-second intervals. You stopped counting them a while ago."
    ),
    "shadows": (
        "The shadows here have a quality you can't name.\n"
        "Something on this ship learned patience. You think about that longer than you mean to."
    ),
    "console": (
        "Dark. Power to this section was rerouted to life support and the locks during the lockdown.\n"
        "If the generator were running, you'd have options here."
    ),
    "pipe": (
        "Conduit lines — some warm, some very cold. Neither temperature is what you'd call reassuring.\n"
        "You trace them with your eyes and decide not to follow where they lead."
    ),
    "cable": (
        "Wiring pulled from its runs and reseated at angles the designers didn't intend.\n"
        "Someone patched something in a hurry, or something pulled it loose and didn't care."
    ),
    "locker": (
        "Storage, cleared out — doors hanging open, contents gone.\n"
        "Either the crew raided supplies in the first hours, or someone came back after them."
    ),
    "table": (
        "Whatever was here has been swept to the floor, taken, or both.\n"
        "Handprints in the residue — more than one set, from at least two different visits."
    ),
    "chair": ("Pushed back hard, like whoever was sitting stood up very quickly and didn't stop to tuck it in."),
    "pod": (
        "A cryo unit, sealed. Status display dead. Temperature at storage minimum.\n"
        "It wasn't cycled as an emergency wake. Whatever is inside has been waiting longer than you have."
    ),
    "window": (
        "The viewport faces outward. You see what's outside — hull, planet, dark, your own reflection.\n"
        "You look longer than you mean to."
    ),
    "blood": (
        "The climate control has preserved it well. You study the pattern.\n"
        "You make yourself stop studying it. You remember it anyway."
    ),
    "self": (
        "You look worse than you expected, which means you were already expecting bad.\n"
        "You're still moving. On this ship, right now, that's the only metric that counts."
    ),
    "air": (
        "Stale recycled air — cold metal, old organics, something underneath you can't separate out.\n"
        "The scrubbers are still running. You breathe and don't think too hard about what you're breathing."
    ),
    "sound": (
        "You go still. The ship gives you recycler hum, the thermal tick of metal under stress,\n"
        "and something that might be mechanical and might not be."
    ),
    "crate": (
        "Cargo containers stamped with Halloway-Tanaka shipping codes.\n"
        "Empty, or cleared. The manifest tags are gone with everything else."
    ),
    "wall_text": (
        "Someone wrote on the wall here — careful letters that turn into a run at the end.\n"
        "You can make out: STAY OUT OF THE VENTS.\n"
        "Below it, in different handwriting: TOO LATE."
    ),
    "bed": (
        "A crew bunk, still made. Either kept by habit or the owner didn't come back to unmake it.\n"
        "The pillow is dented. They slept here after it started, at least once."
    ),
    "shelf": (
        "A storage shelf, half-emptied. Some items remain in exactly the positions they were left —\n"
        "untouched, because whoever left them there didn't return for them."
    ),
    "nothing": ("Nothing? Everything is something on a ship like this.\nLook again."),
    "body": ("There are no bodies in this room right now.\nThat could change."),
    "specimen": ("No specimen containers here.\nYou're not sure if that's a relief or not."),
    "suit_feature": ("You don't see a pressure suit here.\nCheck the EVA prep room or the cryo section lockers."),
    "exits": None,  # handled specially in handle_examine
}

# Zone-specific description overrides (first character of room_id → feature → text).
_FEATURE_ZONE: dict[str, dict[str, str]] = {
    "c": {  # Cryo Bay
        "wall": (
            "The cryo bay walls sweat where emergency heat meets the cold at the panel seams.\n"
            "Frost has built up in the joins. This is the coldest part of the ship, even now."
        ),
        "floor": (
            "Cryo fluid dried at the deck joins during the unscheduled revival cycle.\n"
            "You've been tracking it for a while. You noticed some time ago and stopped caring."
        ),
        "pod": (
            "A cryo unit, sealed. The LED status strip is dead.\n"
            "You know from direct experience what's inside — nothing that woke up should have woken yet."
        ),
        "light": (
            "Pale blue emergency strips, backup circuit only.\n"
            "You associate this color with waking up afraid. That association is probably permanent now."
        ),
        "ceiling": (
            "The cryo bay overhead shows the revival rigging — the mechanical arms that open the pods.\n"
            "Several hang loose. Your pod's arm is still extended."
        ),
    },
    "f": {  # Engineering
        "wall": (
            "Heavier gauge than the rest of the ship — reinforced to contain reactor incidents.\n"
            "The paint has been stripped in patches by heat. Not recently, and not by accident."
        ),
        "floor": (
            "Grated deck over the service crawl-space below. You can see down through the gaps.\n"
            "You decide not to look for long."
        ),
        "pipe": (
            "Live conduit — coolant, high-pressure gas, electrical bundles.\n"
            "The labels are half burned off. The unlabeled ones bother you more."
        ),
        "console": (
            "This terminal had full engineering access before the lockdown.\n"
            "Now it shows only reactor telemetry — stable, automatic, no one left to maintain it."
        ),
        "ceiling": (
            "Engineering overhead is mostly ductwork and the underside of the upper mechanical deck.\n"
            "Heavy, industrial, loud with the drone of systems that kept running after everyone stopped."
        ),
    },
    "g": {  # Alien territory
        "wall": (
            "The wall panels in this section are coated with something you did not put here.\n"
            "Resinous, organic, slightly warm to the touch. You don't touch it long.\n"
            "It is still being deposited."
        ),
        "floor": (
            "The deck has been altered — overlaid with an organic accretion\n"
            "that muffles footsteps and is wrong in a way you can't quite articulate."
        ),
        "ceiling": (
            "Don't look at the ceiling in this section. You looked.\n"
            "Something built up there from materials that have no business being on a ship.\n"
            "You don't look again."
        ),
        "shadows": (
            "In this section you don't examine the shadows.\n"
            "You watch them with your peripheral vision and you keep moving."
        ),
        "cable": (
            "The wiring in this zone has been threaded through the organic structures —\n"
            "still live in places, connected to something that doesn't need the electricity\n"
            "but may be learning from it."
        ),
        "vent": (
            "In this section the ventilation grilles are all open.\n"
            "Not broken open. Open, as if something considered the duct network and found it convenient."
        ),
        "wall_text": (
            "Writing here, half-obscured by the resin overlay.\n"
            "You can make out: IT LEARNS. Below that, someone drew an arrow.\n"
            "The arrow points at the vent."
        ),
        "air": (
            "The air in this section smells wrong — not mechanical-wrong like the rest of the ship,\n"
            "but biological. Something warm is breathing in here, or was recently."
        ),
    },
    "m": {  # Maintenance tunnels
        "wall": (
            "Raw structural steel, no cladding. The same bolt pattern every meter — some stripped.\n"
            "Scratch marks at eye level that don't match any tool use you recognize."
        ),
        "floor": (
            "Narrow, irregular deck plates bolted for access work.\n"
            "Something dragged itself through here more than once. The pattern doesn't match human proportions."
        ),
        "ceiling": (
            "Low overhead — access ducts, junction boxes, crawl-spaces branching upward.\n"
            "In the maintenance tunnels, the ceiling is exactly the kind of place something waits."
        ),
        "light": (
            "Bare bulbs on the backup circuit, one every four meters.\n"
            "Three of them work. The one that doesn't is directly above you."
        ),
        "vent": (
            "In the maintenance tunnels, vents are just additional passages.\n"
            "The access ducts here are wider than in the main sections. More of them are open than closed."
        ),
        "pipe": (
            "The conduit runs are exposed here, unlabeled, running behind everything else.\n"
            "Some are hot enough to burn. You've already brushed one without noticing."
        ),
    },
    "d": {  # Science / Research
        "wall": (
            "Modular paneling designed for lab equipment mounting.\n"
            "Some panels have been removed, the framework used as scaffolding. For what, you don't know."
        ),
        "console": (
            "The last log entry on this research terminal is nineteen days old.\n"
            "It ends mid-sentence: SPECIMEN BEHAVIOR INCONSISTENT WITH —"
        ),
        "locker": (
            "Research storage. Some containers still have biohazard integrity seals.\n"
            "You weigh the chance something useful is inside against the chance the seal is the whole point."
        ),
        "specimen": (
            "Specimen containers — some intact, some not.\nThe ones that are not intact were opened from the inside."
        ),
        "table": (
            "A lab bench, cleared in a hurry. Instrument brackets still bolted in place, instruments gone.\n"
            "The last entry in the attached clipboard: 'Do not open. Do not open. Do not—'"
        ),
    },
    "a": {  # Command / Bridge
        "wall": (
            "The command section walls carry the Nightglass designation plaques — registry, routing codes,\n"
            "crew assignment stencils. Someone has crossed out the crew count in permanent marker."
        ),
        "console": (
            "Command terminals, all dark. The AI lockdown pulled priority access from everything\n"
            "except life support and containment. The screens show the Halloway-Tanaka logo, looping."
        ),
        "floor": (
            "The command deck floor is polished composite — or was, before the event.\n"
            "Boot marks track to the door and stop. Nobody walked back."
        ),
    },
    "b": {  # Crew quarters / service
        "wall": (
            "Photographs still taped up. Names on lockers. A duty schedule, handwritten.\n"
            "This is the most human part of the ship. That makes it harder to be in."
        ),
        "bed": (
            "A crew bunk, still made. Or made again after — kept by routine, or the owner never came back.\n"
            "The pillow holds a dent. They slept here after it started, at least once."
        ),
        "locker": (
            "Personal storage, some still locked with individual codes.\n"
            "The open ones are empty. You leave the locked ones. Some things are still private."
        ),
        "wall_text": (
            "Someone wrote on the wall above their bunk. Personal, short.\n"
            "A name, a date, and: WE SHOULD NOT HAVE GONE INTO THE CAVE.\n"
            "The date is nineteen days ago."
        ),
    },
    "e": {  # External / EVA / airlock
        "wall": (
            "Thicker here — you're near the hull. Exterior stress marks on the inner surface.\n"
            "One seam shows pressure from outside. Something tested it."
        ),
        "window": (
            "The viewport faces the survey site. The crater. The cave entrance.\n"
            "You studied that cave from orbit and thought it was interesting.\n"
            "You were right."
        ),
        "door": (
            "An airlock door — the exterior seal shows EVA cycle marks from multiple uses.\n"
            "The last cycle was not logged as a scheduled excursion."
        ),
        "floor": (
            "The EVA prep floor has boot tracks in the grime — survey kit, then bare feet, then nothing.\n"
            "The nothing part was fast."
        ),
    },
}

# Fallback lines when nothing matches — varied so it doesn't always say the same thing.
_EXAMINE_FALLBACKS = [
    "Nothing here by that name, or nothing you can find.",
    "You look carefully. Nothing presents itself.",
    "Not here. Not visible. Keep moving.",
    "You search the area with your eyes. Nothing by that name.",
]


class Parser:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.aliases: dict[str, str] = {
            # Directions
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "u": "up",
            "d": "down",
            # Examination — the most important command
            "x": "examine",
            "exam": "examine",
            "inspect": "examine",
            "study": "examine",
            "check": "examine",
            "view": "examine",
            "observe": "examine",
            "describe": "examine",
            "investigate": "examine",
            "analyse": "examine",
            "analyze": "examine",
            "scrutinize": "examine",
            "scrutinise": "examine",
            "detail": "examine",
            "look": "look",  # explicit: "look" stays "look" (not aliased to examine)
            "survey": "look",
            "glance": "look",
            # Taking
            "get": "take",
            "grab": "take",
            "pick": "take",
            "collect": "take",
            "retrieve": "take",
            "pocket": "take",
            "snatch": "take",
            "acquire": "take",
            "lift": "take",
            # Dropping
            "place": "drop",
            "discard": "drop",
            # Hiding
            "conceal": "hide",
            "duck": "hide",
            "crouch": "hide",
            "tuck": "hide",
            "shelter": "hide",
            "cover": "hide",
            # Throwing
            "toss": "throw",
            "hurl": "throw",
            "chuck": "throw",
            "fling": "throw",
            "pitch": "throw",
            "lob": "throw",
            # Wearing
            "don": "wear",
            "equip": "wear",
            # Removing
            "doff": "remove",
            "unequip": "remove",
            # Listening
            "hear": "listen",
            "eavesdrop": "listen",
            # Waiting
            "rest": "wait",
            "pause": "wait",
            "stay": "wait",
            # Running
            "sprint": "run",
            "dash": "run",
            "rush": "run",
            "flee": "run",
            "bolt": "run",
            "scramble": "run",
            "hurry": "run",
            # Crawling / sneaking
            "creep": "crawl",
            "sneak": "crawl",
            "squeeze": "crawl",
            "slip": "crawl",
            "slink": "crawl",
            # Opening
            "pry": "open",
            "crack": "open",
            # Scanning
            "ping": "scan",
            # Searching
            "rummage": "search",
            "rifle": "search",
            "ransack": "search",
            "frisk": "search",
            "root": "search",
            # Reading
            "peruse": "read",
            # Talking
            "speak": "talk",
            "chat": "talk",
            "communicate": "talk",
            "address": "talk",
            "converse": "talk",
            "contact": "talk",
            "hail": "talk",
            # Inventory
            "i": "inventory",
            "inv": "inventory",
            "items": "inventory",
            "carrying": "inventory",
            "pockets": "inventory",
            "bag": "inventory",
            # Crafting
            "fix": "craft",
            "build": "craft",
            "assemble": "craft",
            "make": "craft",
            "construct": "craft",
            "fabricate": "craft",
            # Mission
            "transmit": "send",
            "broadcast": "send",
            "unlock": "override",
            "disable": "override",
            "bypass": "override",
            "hack": "override",
            # Navigation / map
            "layout": "map",
            "navigation": "map",
            # Help
            "commands": "help",
            "?": "help",
            # Meta
            "exit": "quit",
            "q": "quit",
        }

    @property
    def player(self) -> Player:
        assert self.game_state.player is not None, "parser used before new_game()"
        return self.game_state.player

    # ------------------------------------------------------------------ #
    def _act(self, sound: int):
        self.game_state.advance = True
        self.game_state.last_action_sound = sound

    def _meta(self):
        self.game_state.advance = False

    # ------------------------------------------------------------------ #
    def parse_command(self, command: str) -> str:
        self.game_state.advance = False
        command = command.strip().lower()
        command = "".join(ch for ch in command if ch.isalnum() or ch.isspace())
        if not command:
            return "What?"

        words = command.split()

        # ---- Pass 1: strip leading motion verb when followed by a direction ----
        if words[0] in _MOTION_STARTERS and len(words) > 1:
            candidate = self.aliases.get(words[1], words[1])
            if candidate in DIRECTIONS:
                words = words[1:]

        # ---- Pass 2: pre-alias multi-word patterns ----
        # These must run BEFORE alias resolution to catch phrases whose first
        # word would otherwise be remapped (e.g. "check out" → examine).
        joined = " ".join(words)

        if joined.startswith("check out") or joined.startswith("check on"):
            words = ["examine"] + words[2:]
        elif joined.startswith("put down") or joined.startswith("set down") or joined.startswith("lay down"):
            words = ["drop"] + words[2:]
        elif joined.startswith("look around") or joined.startswith("look here"):
            words = ["look"]
        elif joined.startswith("speak to") or joined.startswith("speak with"):
            words = ["talk"] + words[2:]
        elif joined.startswith("talk to"):
            words = ["talk"] + words[2:]
        elif joined.startswith("take a look") or joined.startswith("have a look"):
            words = ["look"]
        elif joined.startswith("interact with"):
            words = ["use"] + words[2:]
        elif joined.startswith("look through") or joined.startswith("look inside") or joined.startswith("go through"):
            words = ["search"] + words[2:]

        # ---- Pass 3: single-word alias resolution ----
        if words[0] in self.aliases:
            words[0] = self.aliases[words[0]]

        # ---- Pass 4: post-alias multi-word patterns ----
        joined = " ".join(words)

        if joined.startswith("put on"):
            words = ["wear"] + words[2:]
        elif joined.startswith("take off") or joined.startswith("takeoff"):
            words = ["remove"] + words[2:]
        elif joined.startswith("pick up"):
            words = ["take"] + words[2:]
        elif joined.startswith("look at"):
            words = ["examine"] + words[2:]
        elif (
            joined.startswith("override ai")
            or joined.startswith("unlock ai")
            or joined.startswith("disable ai")
            or joined.startswith("bypass ai")
            or joined.startswith("hack ai")
        ):
            words = ["override"]
        elif (
            joined.startswith("craft radio")
            or joined.startswith("build radio")
            or joined.startswith("assemble radio")
            or joined.startswith("make radio")
            or joined.startswith("construct radio")
            or joined.startswith("fix radio")
        ):
            words = ["craft", "radio"]
        elif (
            joined.startswith("send warning")
            or joined.startswith("transmit warning")
            or joined.startswith("broadcast warning")
        ):
            words = ["send"]
        elif joined.startswith("install radio") or joined.startswith("install improvised"):
            words = ["override"]
        elif (
            joined.startswith("talk molly")
            or joined.startswith("talk ai")
            or joined.startswith("talk mother")
            or joined.startswith("talk lacuna")
            or joined.startswith("ask molly")
            or joined.startswith("ask ai")
            or joined.startswith("ask mother")
            or joined.startswith("ask lacuna")
            or joined.startswith("speak molly")
            or joined.startswith("speak mother")
            or joined.startswith("contact ai")
            or joined.startswith("hail ai")
        ):
            words = ["molly"]

        verb = words[0]

        if verb in DIRECTIONS:
            return self.handle_movement(verb)

        args = [w for w in words[1:] if w not in FILLER]

        dispatch = {
            "look": lambda: self.handle_look(),
            "examine": lambda: self.handle_examine(args),
            "take": lambda: self.handle_take(args),
            "drop": lambda: self.handle_drop(args),
            "inventory": lambda: self.handle_inventory(),
            "wear": lambda: self.handle_wear(args),
            "remove": lambda: self.handle_remove(args),
            "scan": lambda: self.handle_scan(),
            "read": lambda: self.handle_read(args),
            "use": lambda: self.handle_use(args),
            "craft": lambda: self.handle_craft(args),
            "override": lambda: self.handle_override_ai(),
            "send": lambda: self.handle_send(),
            "throw": lambda: self.handle_throw(args),
            "hide": lambda: self.handle_hide(args),
            "crawl": lambda: self.handle_crawl(args),
            "run": lambda: self.handle_run(args),
            "wait": lambda: self.handle_wait(),
            "listen": lambda: self.handle_listen(),
            "talk": lambda: self.handle_talk(args),
            "ask": lambda: self.handle_talk(args),
            "wake": lambda: self.handle_talk(args),
            "molly": lambda: self.handle_molly(),
            "lacuna": lambda: self.handle_molly(),
            "mother": lambda: self.handle_molly(),
            "search": lambda: self.handle_search(args),
            "open": lambda: self.handle_open(args),
            "yell": lambda: self.handle_yell(),
            "shout": lambda: self.handle_yell(),
            "scream": lambda: self.handle_yell(),
            "call": lambda: self.handle_yell(),
            "map": lambda: self.handle_map(),
            "save": lambda: self.handle_save(),
            "load": lambda: self.handle_load(),
            "help": lambda: self.handle_help(),
            "quit": lambda: self.handle_quit(),
            "restart": lambda: self.handle_restart(),
        }
        if verb in dispatch:
            return dispatch[verb]()

        if verb in {
            "lick",
            "eat",
            "kiss",
            "sing",
            "dance",
            "smell",
            "kill",
            "shoot",
            "fight",
            "attack",
            "stab",
            "punch",
            "kick",
        }:
            return "No."
        return f"I don't understand '{command}'. Type 'help' for commands."

    # ------------------------------------------------------------------ #
    # Movement
    # ------------------------------------------------------------------ #
    def _move_to(self, direction: str, sound: int, verb_phrase: str) -> str:
        room = self.game_state.current_room
        if direction not in room.exits:
            return f"No exit to the {direction}."
        dest_id = room.exits[direction]

        self.game_state.current_room_id = dest_id
        self.player.last_room_id = room.id
        self.player.stayed_turns_in_room = 0
        self.player.hidden = False
        self.player.hidden_spot = None
        room.visited = True
        self.game_state.rooms[dest_id].visited = True
        self.game_state.visited_rooms.add(dest_id)

        self._act(sound)
        result = f"{verb_phrase} {direction}."

        # First-encounter synthetic introduction: the moment you see it and
        # think, just for a second, that someone survived.
        dest_room = self.game_state.rooms[dest_id]
        for item in dest_room.items:
            if item.synthetic_data and not item.synthetic_data.get("introduced"):
                item.synthetic_data["introduced"] = True
                sname = item.synthetic_data["name"]
                result += (
                    "\n\nA human-shaped figure stands near the far wall.\n"
                    "For one second, you think someone survived this.\n\n"
                    "Then it turns. The movement is wrong — too smooth, too deliberate.\n"
                    f"The badge reads {sname}."
                )
                break

        return result

    def handle_movement(self, direction: str) -> str:
        return self._move_to(direction, 1, "You walk")

    def handle_crawl(self, words: list[str]) -> str:
        if not words:
            return "Crawl where?"
        return self._move_to(words[0], 0, "You crawl")

    def handle_run(self, words: list[str]) -> str:
        if not words:
            return "Run where?"
        direction = words[0]
        if direction not in self.game_state.current_room.exits:
            return f"No exit to the {direction}."
        result = self._move_to(direction, 3, "You run")
        self.game_state.last_action_sound = 3
        return result

    # ------------------------------------------------------------------ #
    # Observation
    # ------------------------------------------------------------------ #
    def handle_look(self) -> str:
        # Return empty — the front-end calls render_room() / _write_room() directly
        # when it sees the "look" command, so we never want a duplicate render here.
        self._meta()
        return ""

    def handle_examine(self, words: list[str]) -> str:
        if not words:
            return "Examine what?"
        name = " ".join(words)
        gs = self.game_state

        # ---- Room items first: synthetics, bodies, and regular items ----
        for item in gs.current_room.items:
            if item.matches_name(name):
                self._act(1)
                if item.synthetic_data:
                    return self._describe_synthetic(item)
                return item.description

        # ---- Inventory and worn items ----
        for item in self.player.inventory + self.player.worn_items:
            if item.matches_name(name):
                self._act(1)
                return item.description

        # ---- Direction / exit examination ----
        # "examine north" → peek through the exit
        clean = name.replace(" exit", "").replace(" door", "").replace(" passage", "").strip()
        if clean in DIRECTIONS:
            room = gs.current_room
            self._meta()
            if clean in room.exits:
                dest_id = room.exits[clean]
                dest = gs.rooms.get(dest_id)
                dest_name = dest.name if dest else "somewhere"
                if dest and dest.visited:
                    return f"The way {clean} leads to {dest_name}. You've been there."
                return f"The passage leads {clean}. You haven't been that way yet."
            return f"There is no exit to the {clean} from here."

        # ---- Fixed interactable features ----
        if (
            name in ("console", "terminal", "antenna", "control", "controls", "station", "panel")
            and gs.current_room_id == "a07"
        ):
            self._meta()
            if gs.get_flag("ai_overridden"):
                return (
                    "The antenna control panel. The AI lockout is disengaged.\n"
                    "The channel is open. Type 'send warning' to transmit."
                )
            return (
                "The long-range antenna control station.\n"
                "A secondary patch socket sits unused beside the main console.\n"
                "With an improvised radio and the authorization codes, you could transmit."
            )

        if name in ("bench", "workbench", "table", "assembly", "station", "desk") and gs.current_room_id == "c13":
            self._meta()
            return (
                "A compact electronics workbench bolted to the wall.\n"
                "Soldering iron, wire cutters, a magnifier lamp — still powered from the backup circuit.\n"
                "If you have the radio components, you can assemble something here.\n"
                "(Type 'craft radio' when you have all the parts.)"
            )

        # ---- Room features (atmospheric examination of the ship itself) ----
        feat = self._examine_room_feature(name)
        if feat is not None:
            if feat == "__look_redirect__":
                return self.handle_look()
            self._act(0)
            return feat

        # ---- Exits keyword ----
        if name in ("exits", "exit", "passages", "passage", "ways", "way out"):
            self._meta()
            room = gs.current_room
            if not room.exits:
                return "There are no exits from this room. That can't be right."
            lines = ["Exits from here:"]
            for direction, dest_id in room.exits.items():
                dest = gs.rooms.get(dest_id)
                dest_name = dest.name if dest else "unknown"
                visited = dest.visited if dest else False
                suffix = f" → {dest_name}" if visited else " → (unvisited)"
                lines.append(f"  {direction}{suffix}")
            return "\n".join(lines)

        # ---- Nothing matched ----
        self._meta()
        return gs.rng.choice(_EXAMINE_FALLBACKS)

    def _examine_room_feature(self, name: str) -> str | None:
        """Return a description for a room feature, or None if name isn't recognised.
        Returns the sentinel '__look_redirect__' for room/area/surroundings."""
        key = _FEATURE_NORMS.get(name, name)

        if key == "look_redirect":
            return "__look_redirect__"

        # Zone-specific override first.
        room_id = self.game_state.current_room_id
        zone = room_id[0] if room_id else ""
        zone_overrides = _FEATURE_ZONE.get(zone, {})
        if key in zone_overrides:
            return zone_overrides[key]

        # Generic description.
        desc = _FEATURE_DESC.get(key)
        if desc is not None:
            return desc  # could be empty string — still a match

        # Not a known feature.
        return None

    def _describe_synthetic(self, item) -> str:
        data = item.synthetic_data
        # Synthetic player (Valdorf) gets a peer response from other synthetics.
        if self.player.type == "synthetic" and data.get("lines_synthetic"):
            lines = data["lines_synthetic"]
        else:
            lines = data.get("lines", [])
        idx = (self.game_state.turn_count // 4) % max(len(lines), 1)
        dialogue = lines[idx] if lines else ""
        out = item.description
        if dialogue:
            out += "\n\n" + dialogue
        return out

    def handle_read(self, words: list[str]) -> str:
        if not words:
            return "Read what?"
        name = " ".join(words)
        self._act(1)
        for item in self.game_state.current_room.items + self.player.inventory + self.player.worn_items:
            if item.matches_name(name) and item.readable_text:
                return item.readable_text
        # If item exists but has no readable text, fall back to examine.
        for item in self.game_state.current_room.items + self.player.inventory + self.player.worn_items:
            if item.matches_name(name):
                self._meta()
                return f"There's nothing legible on the {item.name}."
        self._meta()
        return f"You don't see any {name} to read here."

    def handle_listen(self) -> str:
        self._act(0)
        gs = self.game_state
        m = gs.monster
        if m.active and m.current_room_id is not None:
            dist, _ = gs.shortest_path(gs.current_room_id, m.current_room_id)
            if dist == 0:
                return "Breathing. Not yours."
            if dist is not None and dist <= 2:
                return "Something moves nearby. Close, and in no hurry."
            return "The ship settling. Maybe. You decide to believe that."
        return gs.rng.choice(
            [
                "Only the hum of the ship. Pairs of lights, ticking warm.",
                "A drip, somewhere. The recyclers. Probably the recyclers.",
                "Nothing. The good kind, for now.",
                "Silence — the kind you have to actively maintain just to hear.",
            ]
        )

    # ------------------------------------------------------------------ #
    # MOTHER-LACUNA AI
    # ------------------------------------------------------------------ #
    def handle_molly(self) -> str:
        self._meta()
        gs = self.game_state
        phase = gs.game_phase if gs.game_phase in _MOLLY_LINES else "exploring"
        lines = _MOLLY_LINES[phase]
        idx = (gs.turn_count // 3) % len(lines)
        return lines[idx]

    def handle_talk(self, words: list[str]) -> str:
        name = " ".join(words).lower() if words else ""
        # Bare "talk" or AI targets.
        if not name or name in ("ai", "molly", "mother", "lacuna", "computer", "ship", "voice", "system"):
            return self.handle_molly()
        # Look for a synthetic in the room.
        for item in self.game_state.current_room.items:
            if item.synthetic_data:
                sname = item.synthetic_data["name"].lower()
                if item.matches_name(name) or name in ("synthetic", "android", "robot", "unit") or name == sname:
                    return self._describe_synthetic(item)
        # Generic synthetic reference.
        if name in ("synthetic", "android", "robot", "unit", "person", "figure"):
            for item in self.game_state.current_room.items:
                if item.synthetic_data:
                    return self._describe_synthetic(item)
        return "There is no one here by that name."

    # ------------------------------------------------------------------ #
    # Inventory / items
    # ------------------------------------------------------------------ #
    def handle_take(self, words: list[str]) -> str:
        if not words:
            return "Take what?"
        name = " ".join(words)
        room = self.game_state.current_room
        for item in room.items:
            if item.matches_name(name):
                if not item.portable:
                    self._meta()
                    if item.synthetic_data:
                        return f"{item.synthetic_data['name']} does not move."
                    return f"You can't take the {item.name}."
                room.remove_item(item)
                self.player.add_to_inventory(item)
                self._act(1)
                # Track hand terminal.
                if item.name == "hand terminal":
                    self.player.has_terminal = True
                    self.game_state.set_flag("has_terminal", True)
                # Track radio components.
                if item.name in RADIO_COMPONENTS:
                    setattr(self.player, RADIO_COMPONENTS[item.name], True)
                    if self.game_state.game_phase == "exploring":
                        self.game_state.game_phase = "collecting"
                return f"You take the {item.name}."
        self._meta()
        return f"You don't see any {name} here."

    def handle_drop(self, words: list[str]) -> str:
        if not words:
            return "Drop what?"
        name = " ".join(words)
        item = self.player.has_item(name)
        if not item:
            self._meta()
            return f"You aren't carrying {name}."
        self.player.remove_from_inventory(item)
        self.game_state.current_room.items.append(item)
        self._act(1)
        # Dropping the hand terminal disables the scanner.
        if item.name == "hand terminal":
            self.player.has_terminal = False
            self.game_state.set_flag("has_terminal", False)
            return "You set down the hand terminal.\nThe scanner goes dark."
        return f"You set down the {item.name}."

    def handle_inventory(self) -> str:
        self._meta()
        if not self.player.inventory and not self.player.worn_items:
            return "You carry nothing."
        lines = ["You carry:"]
        for item in self.player.inventory:
            lines.append(f"  - {item.name}")
        for item in self.player.worn_items:
            lines.append(f"  - {item.name} (worn)")
        return "\n".join(lines)

    def handle_wear(self, words: list[str]) -> str:
        if not words:
            return "Wear what?"
        name = " ".join(words)
        item = None
        source = None
        for i in self.game_state.current_room.items:
            if i.matches_name(name):
                item = i
                source = "room"
                break
        if not item:
            for i in self.player.inventory:
                if i.matches_name(name):
                    item = i
                    source = "inv"
                    break
        if not item:
            self._meta()
            return f"You don't have {name}."
        if not item.wearable:
            self._meta()
            return f"You can't wear the {item.name}."
        if source == "room":
            self.game_state.current_room.remove_item(item)
        else:
            self.player.remove_from_inventory(item)
        self.player.worn_items.append(item)
        item.worn = True
        self.player.suit_worn = True
        self._act(2)
        return "The seals close around your throat.\nSuit pressure holds."

    def handle_remove(self, words: list[str]) -> str:
        if not words:
            return "Remove what?"
        name = " ".join(words)
        for item in self.player.worn_items:
            if item.matches_name(name):
                self.player.worn_items.remove(item)
                self.player.inventory.append(item)
                item.worn = False
                self.player.suit_worn = False
                self._act(1)
                return f"You take off the {item.name}."
        self._meta()
        return f"You're not wearing {name}."

    def handle_use(self, words: list[str]) -> str:
        if not words:
            return "Use what?"
        name = " ".join(words)
        item = self.player.has_item(name)
        if not item:
            self._meta()
            return f"You don't have {name}."
        if item.name == "medkit":
            if self.player.type == "synthetic":
                self._meta()
                return "Your chassis has no use for a medkit."
            self.player.health = 100
            self._act(1)
            return "You patch yourself up. Steadier now."
        if item.use_effect:
            self._act(item.sound_on_use or 1)
            return item.use_effect
        self._meta()
        return f"You can't use the {item.name} like that."

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #
    def handle_search(self, words: list[str]) -> str:
        if not words:
            # "search" with no target → search the room for anything notable
            room = self.game_state.current_room
            self._act(1)
            portable_here = [i for i in room.items if i.portable]
            if portable_here:
                names = ", ".join(i.name for i in portable_here[:4])
                return f"You sweep the room carefully.\nYou notice: {names}."
            return (
                "You search the room carefully.\n"
                "Nothing portable you haven't already found. The ship doesn't give up its dead easily."
            )
        name = " ".join(words)
        room = self.game_state.current_room
        for item in room.items:
            if item.matches_name(name):
                if item.synthetic_data:
                    self._meta()
                    return "The synthetic's casing is sealed. You can't strip it here."
                self._act(1)
                portable_here = [i for i in room.items if i is not item and i.portable]
                if portable_here:
                    names = ", ".join(i.name for i in portable_here[:3])
                    return f"You search carefully.\nYou find: {names}."
                return "You search carefully.\nNothing useful. Just what remains of someone's last moment here."
        # Also allow searching inventory items.
        inv_item = self.player.has_item(name)
        if inv_item:
            self._act(1)
            return f"You go through the {inv_item.name}.\nNothing you didn't already know about."
        self._meta()
        return f"There is no {name} to search here."

    # ------------------------------------------------------------------ #
    # Scanner
    _COMPASS_ABBR: dict[str, str] = {
        "north": "N",
        "south": "S",
        "east": "E",
        "west": "W",
        "northeast": "NE",
        "northwest": "NW",
        "southeast": "SE",
        "southwest": "SW",
        "up": "UP",
        "down": "DN",
        "in": "IN",
        "out": "OUT",
    }

    # ------------------------------------------------------------------ #
    def handle_scan(self) -> str:
        if not self.player.has_terminal:
            self._meta()
            return "You have no scanner. (Find the hand terminal in the cryo monitoring station.)"
        self._act(1)
        gs = self.game_state
        m = gs.monster

        if not m.active:
            return "HAND TERMINAL:\nNo contacts detected.\n\nDirection: —\nDistance: —\nMotion: none\nConfidence: —"

        if m.turns_since_seen <= 1:
            return "HAND TERMINAL:\nYou lift the terminal.\n\nIt is already looking at you."

        room = gs.current_room
        if room.scanner_interference:
            return (
                "HAND TERMINAL:\n"
                "Signal distorted.\n\n"
                "Direction: unknown\n"
                "Distance: unknown\n"
                "Motion: —\n"
                "Cause: local interference"
            )

        tracked = m.tracked_room_id or m.current_room_id
        if tracked is None:
            return "HAND TERMINAL:\nSignal lost.\n\nDirection: —\nDistance: —\nMotion: —\nConfidence: —"
        if tracked == gs.current_room_id:
            return (
                "HAND TERMINAL:\n"
                "Contact — this room.\n\n"
                "Direction: HERE\n"
                "Distance: 0 m\n"
                "Motion: present\n"
                "Confidence: 100%"
            )

        dist, _ = gs.shortest_path(gs.current_room_id, tracked)
        if dist is None:
            return "HAND TERMINAL:\nSignal lost.\n\nDirection: —\nDistance: —"

        # Up close the signal sometimes ghosts.
        if dist <= 1 and gs.rng.random() < 0.25:
            return (
                "HAND TERMINAL:\n"
                "Signal ghosting.\n\n"
                "Probable direction: unknown\n"
                "Distance: very close\n"
                "Motion: —\n"
                "Confidence: low"
            )

        direction = gs.compass_direction(gs.current_room_id, tracked)
        meters = dist * 15
        confidence = max(20, min(90, 90 - dist * 8))
        if self.player.type == "synthetic":
            confidence = min(95, confidence + 10)

        compass = self._COMPASS_ABBR.get(direction or "", "?")
        motion_desc = {
            "feeding": "still",
            "searching": "slow",
            "investigating": "irregular",
            "hunting": "rapid",
        }.get(m.state, "slow")

        return (
            "HAND TERMINAL:\n"
            "Unknown biological mass detected.\n\n"
            f"Direction: {compass}\n"
            f"Distance: ~{meters} m\n"
            f"Motion: {motion_desc}\n"
            f"Confidence: {confidence}%"
        )

    # ------------------------------------------------------------------ #
    # Hiding / distraction
    # ------------------------------------------------------------------ #
    def handle_hide(self, words: list[str]) -> str:
        room = self.game_state.current_room
        if not room.hiding_spots:
            self._meta()
            return "There is nowhere to hide here."
        name = " ".join(words) if words else None
        spot = room.find_hiding_spot(name)
        if not spot:
            self._meta()
            return f"You can't hide {name} here." if name else "There is nowhere to hide here."
        reused = self.player.hidden_spot is spot or spot["reuse"] > 0
        spot["reuse"] += 1
        self.player.hidden = True
        self.player.hidden_spot = spot
        if self.game_state.monster.active:
            self.game_state.monster.known_hide_room = self.game_state.current_room_id
        self._act(1)
        if reused:
            return f"You take cover again — {spot['name']}.\nThe same hiding place feels smaller now."
        return f"You take cover — {spot['name']}. You go still."

    def handle_throw(self, words: list[str]) -> str:
        if not words:
            return "Throw what?"
        direction = None
        if words[-1] in DIRECTIONS:
            direction = words[-1]
            words = words[:-1]
        name = " ".join(words) if words else "can"
        item = self.player.has_item(name)
        if not item:
            self._meta()
            return f"You don't have {name} to throw."
        self.player.remove_from_inventory(item)
        gs = self.game_state
        m = gs.monster
        if direction and direction in gs.current_room.exits:
            target = gs.current_room.exits[direction]
            self._act(0)
            gs.last_action_sound = 0
            if not m.active:
                return f"The {item.name} clatters away to the {direction}."
            fell_for_it = gs.rng.random() < max(0.1, 1.0 - 0.3 * m.distraction_uses)
            m.distraction_uses += 1
            if fell_for_it:
                m.last_heard_room_id = target
                m.turns_since_heard = 0
                m.add_suspicion(target, 8)
                m.set_distracted(gs.turn_count + 2)
                return f"The {item.name} clatters away {direction}. Something shifts toward the sound."
            return f"The {item.name} clatters away {direction}.\nIt glances toward the noise. It does not turn."
        self._act(3)
        return f"The {item.name} clatters across the floor. Loud. Too loud."

    # ------------------------------------------------------------------ #
    # Radio mission — craft, override, send
    # ------------------------------------------------------------------ #
    def handle_craft(self, words: list[str]) -> str:
        target = " ".join(words).lower()
        if target and "radio" not in target:
            self._meta()
            return f"You can't craft {target} here."

        if self.game_state.current_room_id != "c13":
            self._meta()
            return "You need a workspace for this.\nThe assembly bench in Cryo Secure Storage (C13) would do."

        if self.player.radio_built or self.player.has_item("improvised radio"):
            self._meta()
            return "You already have an improvised radio assembled."

        missing_parts = [p for p in RADIO_COMPONENTS if not self.player.has_item(p)]
        missing_consumables = [c for c in RADIO_CONSUMABLES if not self.player.has_item(c)]
        missing = missing_parts + missing_consumables
        if missing:
            self._meta()
            return (
                "You don't have everything you need.\n"
                "Missing: " + ", ".join(missing) + ".\n\n"
                "Components: transmitter coil, signal crystal, power regulator, antenna coupler.\n"
                "Consumables: wire spool, battery cell, tape roll."
            )

        for part_name in list(RADIO_COMPONENTS.keys()) + RADIO_CONSUMABLES:
            item = self.player.has_item(part_name)
            if item:
                self.player.remove_from_inventory(item)

        radio = Item(
            name="improvised radio",
            aliases="radio,improvised,assembly,transmitter",
            description=(
                "A jury-rigged long-range radio assembly.\n"
                "Transmitter coil, signal crystal, power regulator, antenna coupler —\n"
                "wired together with spool, cell, and tape. Fragile, but it will work once."
            ),
            portable=True,
            required_for_win=True,
        )
        self.player.add_to_inventory(radio)
        self.player.radio_built = True
        self.game_state.set_flag("radio_built", True)
        self._act(2)
        return (
            "You work at the bench for what feels like too long.\n\n"
            "The components seat together. The crystal hums faintly.\n"
            "You hold the improvised radio — ugly, functional, irreplaceable.\n\n"
            "Now you need the authorization codes to unlock the AI transmission lock.\n"
            "Then get to the Long-Range Antenna Control (A07) and send the warning."
        )

    def handle_override_ai(self) -> str:
        gs = self.game_state

        if gs.current_room_id != "a07":
            self._meta()
            return "You can't override the AI from here.\nYou need to be at the Long-Range Antenna Control (A07)."

        if gs.get_flag("ai_overridden"):
            self._meta()
            return "The AI lock is already disengaged.\nType 'send warning' to transmit."

        radio = self.player.has_item("improvised radio")
        if not radio:
            self._meta()
            return (
                "You need an improvised radio to patch into the antenna.\n"
                "Craft one first at the assembly bench in Cryo Secure Storage (C13)."
            )

        keycard = (
            self.player.has_item("command keycard")
            or self.player.has_item("captain keycard")
            or self.player.has_item("keycard")
        )
        cipher = self.player.has_item("admin cipher") or self.player.has_item("cipher")
        auth = self.player.has_item("manual authorization") or self.player.has_item("authorization")

        missing = []
        if not keycard:
            missing.append("captain's command keycard (A05)")
        if not cipher:
            missing.append("admin cipher (B03)")
        if not auth:
            missing.append("manual authorization (F10)")

        if missing:
            self._meta()
            return (
                "You need all three authorization codes to break the transmission lock.\n"
                "Still missing:\n" + "\n".join(f"  — {m}" for m in missing)
            )

        self.player.remove_from_inventory(radio)
        if keycard:
            self.player.remove_from_inventory(keycard)
        if cipher:
            self.player.remove_from_inventory(cipher)
        if auth:
            self.player.remove_from_inventory(auth)

        gs.set_flag("ai_overridden", True)
        gs.game_phase = "final_run"
        self._act(3)
        return (
            "You slot the radio into the patch socket.\n"
            "The keycard, the cipher, the authorization — entered in sequence.\n\n"
            "A pause.\n\n"
            "MOTHER-LACUNA: Authorization chain verified.\n"
            "  Quarantine override accepted.\n"
            "  Transmission lock: disengaged.\n\n"
            "Far away in the ship, something shifts.\n"
            "It felt that. It is coming.\n\n"
            "Type 'send warning' to transmit."
        )

    def handle_send(self) -> str:
        gs = self.game_state

        if not gs.get_flag("ai_overridden"):
            self._meta()
            if gs.current_room_id != "a07":
                return "You have nothing to send from here."
            return "The transmission lock is still active.\nYou need to override the AI first. (Type 'override ai'.)"

        if gs.current_room_id != "a07":
            self._meta()
            return "You need to be at the Long-Range Antenna Control (A07) to transmit."

        self._act(4)
        gs.set_flag("warning_sent", True)
        gs.win_state = True
        gs.game_phase = "won"
        return "You key the transmitter.\nThe signal leaves the ship."

    # ------------------------------------------------------------------ #
    def handle_open(self, words: list[str]) -> str:
        self._act(2)
        return "It opens. Nothing useful inside, or nothing you can reach."

    def handle_yell(self) -> str:
        self._act(4)
        return "You shout into the dark.\nThe ship swallows it. Something else does not."

    def handle_wait(self) -> str:
        self._act(0)
        return "You wait. The ship breathes around you."

    # ------------------------------------------------------------------ #
    # Meta
    # ------------------------------------------------------------------ #
    def handle_save(self) -> str:
        self._meta()
        import save

        return "Saved." if save.save_game(self.game_state) else "Could not write the save file."

    def handle_load(self) -> str:
        self._meta()
        import save

        if save.load_game(self.game_state):
            return "Loaded. You are back in the " + self.game_state.current_room.name + "."
        return "No save found."

    def handle_map(self) -> str:
        self._meta()
        rooms = self.game_state.rooms
        visited = [r for r in rooms.values() if r.visited]
        if not visited:
            return "You have not explored anywhere yet."
        width = max(len(r.name) for r in visited)
        lines = ["Known rooms (* = you are here):"]
        for room in visited:
            conns = []
            for direction, dest in room.exits.items():
                label = rooms[dest].name if rooms[dest].visited else "?"
                conns.append(f"{direction}→{label}")
            here = "*" if room.id == self.game_state.current_room_id else " "
            lines.append(f" {here}{room.name.ljust(width)}  " + "  ".join(conns))
        return "\n".join(lines)

    def handle_help(self) -> str:
        self._meta()
        return (
            "Commands — most have multiple synonyms:\n\n"
            "  MOVEMENT\n"
            "    north / south / east / west / up / down / in / out\n"
            "    n s e w u d  (shortcuts)   |   go, walk, head, move, proceed + direction\n"
            "    run <dir>  (loud)   |   crawl / sneak / creep <dir>  (quiet)\n\n"
            "  OBSERVATION\n"
            "    look  (l)  —  describe the room you're in\n"
            "    examine / inspect / study / check / view / x <thing>\n"
            "    You can examine almost anything: walls, floor, vents, lights, doors,\n"
            "    consoles, pipes, cables, shadows, pods, windows, and more.\n"
            "    examine north  —  peek through an exit\n"
            "    scan  (ping)  —  motion tracker (needs hand terminal)\n"
            "    listen / hear\n\n"
            "  ITEMS\n"
            "    take / get / grab / pick up / collect <thing>\n"
            "    drop / discard / set down / place <thing>\n"
            "    inventory  (i, inv)  —  what you're carrying\n"
            "    wear / don / equip <thing>   |   remove / take off / doff <thing>\n"
            "    use <thing>   |   read <thing>\n"
            "    search / rummage / ransack <thing>  —  look for hidden items\n"
            "    throw <thing> <dir>  —  distract the organism\n\n"
            "  STEALTH\n"
            "    hide / conceal / duck / crouch [spot]  —  hide in this room\n\n"
            "  MISSION\n"
            "    craft radio  (build / assemble / fix / make radio)  —  at C13 workbench\n"
            "    override ai  (unlock / disable / hack ai)  —  at A07 with radio + codes\n"
            "    send warning  (transmit)  —  at A07 after override\n\n"
            "  COMMUNICATION\n"
            "    molly / talk ai / speak mother  —  MOTHER-LACUNA ship AI\n"
            "    talk / speak / chat [name]  —  address synthetics or anyone present\n\n"
            "  OTHER\n"
            "    wait / rest / pause  |  map / layout  |  save  |  load\n"
            "    help / commands / ?   |   quit / exit / q   |   restart"
        )

    def handle_quit(self) -> str:
        self._meta()
        self.game_state.quit_requested = True
        return "You let go.\nGoodbye."

    def handle_restart(self) -> str:
        self._meta()
        self.game_state.restart_requested = True
        return "Restarting..."
