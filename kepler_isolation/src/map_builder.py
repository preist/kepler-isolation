"""
Map builder for KEPLER ISOLATION — USCSS Nightglass layout.

75 visible rooms across 7 zones (A-G) plus 30 maintenance/vent spaces (M01-M30).
Player starts at C09 (Cryo Pod Bay Alpha). Monster starts at G11 (Aft Beacon Service).
The cryo core C09-C13 is the safe haven — the alien can never enter.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from item import Item
from room import Room

# Cryo safe haven — alien may not enter these rooms.
SAFE_HAVEN_CORE = {"c09", "c10", "c11", "c12", "c13"}

# Airlock vestibule shell — alien may wait here but not cross inward.
SAFE_HAVEN_AIRLOCKS = {"c05", "c06", "c07", "c08"}

# Rooms with heavy scanner interference.
SCANNER_INTERFERENCE_ROOMS = {
    "f10",
    "f11",
    "f12",  # reactor zone
    "f08",  # power distribution (heat bloom)
    "g02",
    "g03",  # cargo bays (dense metal)
}

# Ambient sound levels (0 = silent, 3 = loud).
AMBIENT_SOUND = {
    "f09": 3,  # generator room — deafening when running
    "f11": 3,  # reactor chamber — constant roar
    "f08": 2,  # power distribution — hum and sparks
    "f12": 2,  # coolant control — pipes and pressure
    "g02": 2,  # cargo bay A — chains, echo
    "g03": 2,  # cargo bay B
    "e06": 1,  # cafeteria — vents, faint hum
    "e07": 1,  # kitchen — refrigeration units
}

# room_id -> list of hiding spots
HIDING_SPOTS = {
    "a05": [{"name": "behind the desk", "quality": 30, "reuse": 0}],
    "a08": [{"name": "archive alcove", "quality": 35, "reuse": 0}],
    "b04": [{"name": "weapons locker", "quality": 40, "reuse": 0}],
    "b05": [{"name": "detention cell", "quality": 45, "reuse": 0}],
    "d04": [{"name": "under the surgical table", "quality": 35, "reuse": 0}],
    "d06": [{"name": "behind the morgue drawers", "quality": 40, "reuse": 0}],
    "d11": [{"name": "behind specimen cases", "quality": 40, "reuse": 0}],
    "e02": [{"name": "under a bunk", "quality": 35, "reuse": 0}],
    "e04": [{"name": "behind the lounge couch", "quality": 30, "reuse": 0}],
    "e08": [{"name": "inside the freezer unit", "quality": 50, "reuse": 0}],
    "e09": [{"name": "chapel alcove", "quality": 40, "reuse": 0}],
    "e11": [{"name": "under a bunk", "quality": 35, "reuse": 0}],
    "e13": [{"name": "behind the lounge couch", "quality": 30, "reuse": 0}],
    "f02": [{"name": "behind fabrication equipment", "quality": 45, "reuse": 0}],
    "f03": [{"name": "inside the tool cage", "quality": 50, "reuse": 0}],
    "f09": [{"name": "behind the generator housing", "quality": 35, "reuse": 0}],
    "g02": [{"name": "between cargo stacks", "quality": 50, "reuse": 0}],
    "g03": [{"name": "between cargo stacks", "quality": 50, "reuse": 0}],
    "g07": [{"name": "inside a pressure suit locker", "quality": 45, "reuse": 0}],
}

# ── Narrative readables ───────────────────────────────────────────────────────

CAPTAIN_NOTE = (
    "CAPTAIN'S NOTE — restricted:\n"
    "If Science asks again, the answer is no.\n"
    "No thaw. No transfer. No profit clause.\n\n"
    "If I am overruled, tell my wife I tried."
)

RECORDER_LOG = (
    "\"—don't transmit. Whatever you do, don't answer it.\"\n"
    "A long pause. Then, quieter:\n"
    '"It learned the signal. It\'s using the signal now."\n'
    "\"I can't hear it anymore. It's in the walls.\""
)

COMPANY_MEMO = (
    "HALLOWAY-TANAKA INDUSTRIES — INTERNAL. Re: Nightglass, Kepler-186f-Lacuna.\n"
    "Objective: recover the biological specimen intact.\n"
    "Assets are recoverable. Crews perform best uninformed.\n"
    "Welcome aboard. Build something that lasts."
)

QUARANTINE_LOG = (
    "SCIENCE LOG — Dr. Reyes, Day 14:\n"
    "The second sample has shown motility.\n"
    "I have ordered containment. The AI has noted my order.\n"
    "The AI has not confirmed it."
)

XENOBIOLOGY_NOTE = (
    "Specimen notes — partial, handwritten:\n"
    "It did not come from the cave as a creature.\n"
    "It arrived hidden in the consequences.\n\n"
    "Do not thaw the second sample.\n"
    "There is no second sample in the room."
)

CHAPEL_LOG = (
    "Personal recording, Engineer Kessler:\n"
    "I found Mercer's bunk cleared out.\n"
    "His boots were still under it.\n"
    "People don't leave without their boots."
)

AFT_BEACON_LOG = (
    "Survey team field note — surface detail:\n"
    "Signal confirmed at depth. Stable. Undegraded.\n"
    "That should not be possible.\n\n"
    "We brought a fragment back. Standard procedure.\n"
    "The fragment brought something back too."
)

MORGUE_NOTE = (
    "Medical examiner note, unofficial:\n"
    "Cause of death: listed as misplaced personnel event.\n\n"
    "I have stopped asking what that means.\n"
    "MOTHER-LACUNA has stopped answering."
)

DETENTION_LOG = (
    "Security log, Sergeant Okafor:\n"
    "Detained one crew member attempting to reach escape pods\n"
    "before mission data was secured. Per directive 2.\n\n"
    "I don't know if I did the right thing.\n"
    "He was in the pod bay when it happened."
)

AI_FRAGMENT = (
    "MOTHER-LACUNA — system log fragment:\n"
    "  Directive 1: preserve human life — ACTIVE\n"
    "  Directive 2: preserve proprietary biological discovery — ACTIVE\n"
    "  Directive 3: prevent contamination of Earth-aligned space — ACTIVE\n\n"
    "  Conflict resolution: pending.\n"
    "  Human authorization required.\n"
    "  No authorized humans remain.\n"
    "  Waiting."
)


def create_rooms() -> dict:
    """Create all 75 visible rooms of the USCSS Nightglass."""
    rooms = {}

    # ── A. Forward Command ────────────────────────────────────────────────────

    rooms["a01"] = Room(
        name="Observation Dome",
        description=(
            "A curved viewport fills the forward wall.\n"
            "The dead planet hangs below, patient and dark.\n"
            "No rescue lights in the distance. No traffic. Nothing."
        ),
        items=[],
        exits={"south": "a02"},
        hidden_items=[],
    )

    rooms["a02"] = Room(
        name="Forward Sensor Walk",
        description=(
            "A narrow catwalk of instrument panels, most dark.\n"
            "One screen still cycles through sensor data no one is reading.\n"
            "A service hatch in the west wall hangs slightly open."
        ),
        items=[],
        exits={"north": "a01", "south": "a03"},
        hidden_items=[],
    )

    rooms["a03"] = Room(
        name="Navigation Control",
        description=(
            "Charts and trajectory logs cover the main console.\n"
            "The last plotted course points back the way you came.\n"
            "No return course has been filed."
        ),
        items=[],
        exits={"north": "a02", "south": "a04", "east": "a06", "west": "a05"},
        hidden_items=[],
    )

    rooms["a04"] = Room(
        name="Bridge Control",
        description=(
            "The command center. All chairs empty, all screens live.\n"
            "The captain's chair faces a console someone left mid-sentence.\n"
            "The intercom is open on a channel no one is transmitting from."
        ),
        items=[],
        exits={"north": "a03", "south": "b01", "east": "a07", "west": "a08"},
        hidden_items=[],
    )

    rooms["a05"] = Room(
        name="Captain's Ready Room",
        description=(
            "Small and personal. A photo faces away from you on the desk.\n"
            "A note is folded under the corner of a keycard.\n"
            "The door was locked. It isn't anymore."
        ),
        items=[
            Item(
                "captain's note",
                "note,letter,captain",
                "A folded note, written by hand on real paper.",
                portable=True,
                readable_text=CAPTAIN_NOTE,
            ),
            Item(
                "command keycard",
                "keycard,card,key,command",
                "A Level-3 command keycard. Scratched from use.",
                portable=True,
            ),
        ],
        exits={"east": "a03", "south": "a08"},
        hidden_items=[],
    )

    rooms["a06"] = Room(
        name="Communications Center",
        description=(
            "The official comm array — dead. Every transmitter socket empty.\n"
            "Someone tried to send a message from here. The log shows attempts.\n"
            "Each one ended with: TRANSMISSION BLOCKED — DIRECTIVE 2."
        ),
        items=[],
        exits={"west": "a03", "south": "a07"},
        hidden_items=[],
    )

    rooms["a07"] = Room(
        name="Long-Range Antenna Control",
        description=(
            "The final room. A dish antenna coupling array faces the hull.\n"
            "Three empty mounting sockets.\n"
            "From here, a signal reaches anyone."
        ),
        items=[
            Item(
                "transmitter coil",
                "coil,transmitter",
                "A long-range transmission coil. Heavy. Built to carry a signal across nothing.",
                portable=True,
                required_for_win=True,
            ),
        ],
        exits={"north": "a06", "west": "a04", "south": "b03"},
        hidden_items=[],
    )

    rooms["a08"] = Room(
        name="Command Archive",
        description=(
            "Floor-to-ceiling data terminals, most dark or looping on error screens.\n"
            "One terminal cycles through AI system logs, unattended.\n"
            "The override station in the corner has been physically locked."
        ),
        items=[
            Item(
                "AI system log",
                "log,ai,archive,fragment",
                "A printed AI system log fragment.",
                portable=True,
                readable_text=AI_FRAGMENT,
            ),
        ],
        exits={"north": "a05", "east": "a04", "south": "b06"},
        hidden_items=[],
    )

    # ── B. Security / Admin ───────────────────────────────────────────────────

    rooms["b01"] = Room(
        name="Security Checkpoint",
        description=(
            "A reinforced threshold between command and the rest of the ship.\n"
            "The security gate is open — held that way by a wedged tool.\n"
            "There is a body on the floor, face down, just past the gate."
        ),
        items=[],
        exits={"north": "a04", "south": "c01", "east": "b02", "west": "b06"},
        hidden_items=[],
    )

    rooms["b02"] = Room(
        name="Security Hub",
        description=(
            "A circular room with camera feeds covering most of the ship.\n"
            "A motion tracker unit sits in its cradle, charge indicator green.\n"
            "Half the feeds show static. The others show empty corridors."
        ),
        items=[
            Item(
                "access tuner",
                "tuner,tool",
                "A Halloway-Tanaka access tuner. Can bypass most standard locks. Noisy.",
                portable=True,
            ),
        ],
        exits={"west": "b01", "east": "b03", "south": "e05"},
        hidden_items=[],
    )

    rooms["b03"] = Room(
        name="Surveillance Theater",
        description=(
            "A tiered room of screens, most dead. Two still cycle.\n"
            "One shows a room you recognize — it shows it a moment after you were in it.\n"
            "The other shows static and the shape of something that does not move like a person."
        ),
        items=[
            Item(
                "admin cipher",
                "cipher,card,admin",
                "An admin authorization cipher. Required to unlock AI containment.",
                portable=True,
            ),
        ],
        exits={"north": "a07", "west": "b02", "south": "d07"},
        hidden_items=[],
    )

    rooms["b04"] = Room(
        name="Armory",
        description=(
            "Weapon racks, mostly empty. The locks have been cut, not opened.\n"
            "A flare kit remains. Firearms are gone — someone thought they would help.\n"
            "They were wrong about that."
        ),
        items=[
            Item(
                "flare",
                "flares,kit",
                "An emergency flare. Burns loud and bright. The alien will hear it.",
                portable=True,
                sound_on_use=3,
            ),
            Item(
                "flare",
                "flares,kit",
                "An emergency flare. Burns loud and bright. The alien will hear it.",
                portable=True,
                sound_on_use=3,
            ),
        ],
        exits={"west": "b02", "south": "b05"},
        hidden_items=[],
    )

    rooms["b05"] = Room(
        name="Detention Cell",
        description=(
            "A single cell, door open. A personal log has been left on the bunk.\n"
            "Whoever was held here left in a hurry, or was removed.\n"
            "Scratch marks on the inside of the door, low down."
        ),
        items=[
            Item(
                "detention log",
                "log,note",
                "A security log, handwritten.",
                portable=True,
                readable_text=DETENTION_LOG,
            ),
        ],
        exits={"north": "b04"},
        hidden_items=[],
    )

    rooms["b06"] = Room(
        name="Admin Records",
        description=(
            "Filing systems and contract terminals. The company's paperwork outlasted everyone.\n"
            "A crew manifest is open on the nearest screen — twenty-three names.\n"
            "Most have a status flag. None of the flags say what you want them to say."
        ),
        items=[
            Item(
                "crew manifest",
                "manifest,list",
                "A crew manifest for the USCSS Nightglass. Twenty-three names. All flagged.",
                portable=True,
            ),
            Item(
                "wire spool",
                "wire,spool",
                "A spool of insulated copper wire. Useful for improvised electronics.",
                portable=True,
            ),
        ],
        exits={"north": "a08", "east": "b01", "south": "d01"},
        hidden_items=[],
    )

    # ── C. Cryo Safe Haven ────────────────────────────────────────────────────

    rooms["c01"] = Room(
        name="Cryo Vestibule North",
        description=(
            "A short approach corridor between Security and the cryo airlocks.\n"
            "The air is cooler here, seeping from the cryo core.\n"
            "A warning placard: BIOLOGICAL SCAN REQUIRED BEFORE ENTRY."
        ),
        items=[],
        exits={"north": "b01", "south": "c05", "east": "c02", "west": "c04"},
        hidden_items=[],
    )

    rooms["c02"] = Room(
        name="Cryo Vestibule East",
        description=(
            "A junction between the east science wing and the cryo approach.\n"
            "The scan panel here is dark — no power to this section.\n"
            "Cold air moves from the south."
        ),
        items=[],
        exits={"west": "c01", "south": "c06", "east": "d07"},
        hidden_items=[],
    )

    rooms["c03"] = Room(
        name="Cryo Vestibule South",
        description=(
            "The southern approach, where the commons meet cryo.\n"
            "Footprints in the dust lead north toward the airlocks.\n"
            "They stop just short of the inner door."
        ),
        items=[],
        exits={"north": "c07", "south": "e05", "east": "c02", "west": "c04"},
        hidden_items=[],
    )

    rooms["c04"] = Room(
        name="Cryo Vestibule West",
        description=(
            "The west approach, connecting medical to the cryo shell.\n"
            "A defibrillator unit on the wall has a cracked casing.\n"
            "It was used recently. It didn't work."
        ),
        items=[],
        exits={"east": "c01", "south": "c08", "west": "d01"},
        hidden_items=[],
    )

    rooms["c05"] = Room(
        name="North Double-Lock Airlock",
        description=(
            "A double-door pressure lock between the vestibule and cryo core.\n"
            "Both doors sealed — inner and outer. The cycle panel glows amber.\n"
            "One door open at a time. That is the rule."
        ),
        items=[],
        exits={"north": "c01", "south": "c09"},
        hidden_items=[],
    )

    rooms["c06"] = Room(
        name="East Double-Lock Airlock",
        description=(
            "East approach airlock. The inner door has a manual override bar.\n"
            "Someone has used it — the bar is scratched and bent slightly inward.\n"
            "The inner seal holds."
        ),
        items=[],
        exits={"north": "c02", "south": "c10"},
        hidden_items=[],
    )

    rooms["c07"] = Room(
        name="South Double-Lock Airlock",
        description=(
            "The south airlock, used most often. The floor shows wear.\n"
            "A panel beside the inner door reads: SCAN COMPLETE — NO CONTAMINANTS.\n"
            "The scan panel is unpowered. That reading is from before."
        ),
        items=[],
        exits={"north": "c11", "south": "c03"},
        hidden_items=[],
    )

    rooms["c08"] = Room(
        name="West Double-Lock Airlock",
        description=(
            "The west airlock, closest to medical. Smells faintly of antiseptic.\n"
            "A gurney was pushed through here and left halfway — blocking nothing, going nowhere.\n"
            "The inner door is sealed."
        ),
        items=[],
        exits={"north": "c04", "south": "c10"},
        hidden_items=[],
    )

    # Cryo safe haven core — alien cannot enter any of these.

    rooms["c09"] = Room(
        name="Cryo Pod Bay Alpha",
        description=(
            "Blue emergency light on frost-webbed glass. Five pods in a row.\n"
            "Yours is open — you're standing in it, more or less.\n"
            "One pod across the bay is cracked from the inside."
        ),
        items=[
            Item(
                "hand terminal",
                "terminal,scanner,lantern",
                "A cracked HT-9 Biometric Survey Terminal. Crew call it 'the lantern'.\n"
                "Shows heat, motion, direction, and distance. Company-issue.",
                portable=True,
            ),
        ],
        exits={"north": "c05", "east": "c11", "south": "c10"},
        hidden_items=[],
    )
    rooms["c09"].monster_allowed = False

    rooms["c10"] = Room(
        name="Cryo Pod Bay Beta",
        description=(
            "The second pod bay, mirror of Alpha. All six pods here are sealed.\n"
            "Frost on the glass. No movement inside.\n"
            "A medical kit is strapped to the wall beside the emergency panel."
        ),
        items=[
            Item(
                "medkit",
                "medic,kit,medical",
                "A field medical kit. Stims and sealant. USE SPARINGLY.",
                portable=True,
            ),
        ],
        exits={"north": "c09", "east": "c11", "south": "c07", "west": "c08"},
        hidden_items=[],
    )
    rooms["c10"].monster_allowed = False

    rooms["c11"] = Room(
        name="Cryo Monitoring Station",
        description=(
            "A half-circle of screens faces the pod bays through thick glass.\n"
            "One monitor still works, painting the room blue.\n"
            "The cryo power breaker is on the east wall, labeled C12-BACKUP."
        ),
        items=[
            Item(
                "company memo",
                "memo,paper,letter",
                "A Halloway-Tanaka directive, printed on real paper.\nSomeone wanted it deniable.",
                portable=True,
                readable_text=COMPANY_MEMO,
            ),
        ],
        exits={"west": "c09", "south": "c13", "east": "c12"},
        hidden_items=[],
    )
    rooms["c11"].monster_allowed = False

    rooms["c12"] = Room(
        name="Cryo Backup Power Closet",
        description=(
            "A utility closet behind the monitoring station.\n"
            "A red breaker panel on the wall controls local cryo lighting.\n"
            "A battery cell sits on the shelf beside a coil of wire."
        ),
        items=[
            Item(
                "battery cell",
                "battery,cell,power",
                "A charged battery cell. Useful for improvised electronics.",
                portable=True,
            ),
        ],
        exits={"west": "c11"},
        hidden_items=[],
    )
    rooms["c12"].monster_allowed = False

    rooms["c13"] = Room(
        name="Cryo Secure Storage",
        description=(
            "A locked storage room off the monitoring station.\n"
            "Shelves of labeled containers, most empty. A workbench along the south wall.\n"
            "This is the safest place on the ship. It doesn't feel like it."
        ),
        items=[],
        exits={"north": "c11"},
        hidden_items=[],
    )
    rooms["c13"].monster_allowed = False

    # ── D. Medical / Science ──────────────────────────────────────────────────

    rooms["d01"] = Room(
        name="Medical Reception",
        description=(
            "A waiting area with plastic chairs still in their rows.\n"
            "A triage clipboard on the desk, half-filled out.\n"
            "The last name on it is illegible — the pen ran out mid-stroke."
        ),
        items=[
            Item(
                "level-1 keycard",
                "keycard,card,key,level1",
                "A Halloway-Tanaka Level-1 access keycard. Grants medical and habitation access.",
                portable=True,
            ),
        ],
        exits={"east": "c04", "south": "d02", "west": "d05"},
        hidden_items=[],
    )

    rooms["d02"] = Room(
        name="Triage",
        description=(
            "The emergency intake room. Curtains, cots, monitors.\n"
            "One body lies face-down near the north door, arm stretched toward the corridor.\n"
            "The hand is open. Not reaching for help. Reaching for the lock."
        ),
        items=[],
        exits={"north": "d01", "south": "d03"},
        hidden_items=[],
    )

    rooms["d03"] = Room(
        name="Diagnostics",
        description=(
            "A diagnostic bay with scanning equipment still powered on.\n"
            "The last patient record is open. It shows elevated parasite markers.\n"
            "The patient is listed as: misplaced personnel event."
        ),
        items=[
            Item(
                "tape roll",
                "tape,sealant",
                "A roll of heavy-duty adhesive tape. Useful for holding improvised things together.",
                portable=True,
            ),
        ],
        exits={"north": "d02", "south": "d04", "east": "e05"},
        hidden_items=[],
    )

    rooms["d04"] = Room(
        name="Surgery",
        description=(
            "The operating room. Everything sterile, everything prepared, no one here.\n"
            "The procedure light is still on. It illuminates a table that has been used recently.\n"
            "Surgical notes on the tray describe something that is not a standard operation."
        ),
        items=[
            Item(
                "surgical notes",
                "notes,surgery",
                "Handwritten surgical notes, unsigned. The procedure described is not in any manual.",
                portable=True,
            ),
            Item(
                "painkillers",
                "pills,meds",
                "A blister pack of painkillers. Better than nothing.",
                portable=True,
            ),
        ],
        exits={"north": "d03", "south": "d06"},
        hidden_items=[],
    )

    rooms["d05"] = Room(
        name="Pharmacy",
        description=(
            "Medical supplies behind a locked cabinet — the lock was forced.\n"
            "Most shelves stripped. A few items remain, overlooked or left deliberately.\n"
            "A note taped to the door: TAKE WHAT YOU NEED. THERE IS NO MORE."
        ),
        items=[
            Item(
                "painkillers",
                "pills,meds",
                "A blister pack of painkillers.",
                portable=True,
            ),
            Item(
                "tape roll",
                "tape,sealant",
                "A roll of medical tape.",
                portable=True,
            ),
        ],
        exits={"east": "d01", "south": "d06"},
        hidden_items=[],
    )

    rooms["d06"] = Room(
        name="Morgue",
        description=(
            "Cold storage for the dead. The drawers are all closed.\n"
            "A medical examiner's note is taped to the outside of drawer 7.\n"
            "The drawer is labeled: SPECIMEN — DO NOT RELEASE."
        ),
        items=[
            Item(
                "morgue note",
                "note,examiner",
                "A medical examiner's unofficial note.",
                portable=True,
                readable_text=MORGUE_NOTE,
            ),
        ],
        exits={"north": "d04", "east": "e04"},
        hidden_items=[],
    )

    rooms["d07"] = Room(
        name="Science Reception",
        description=(
            "The threshold between medicine and research. A locked door ahead.\n"
            "Science clearance is required — the placard says Level-2.\n"
            "Someone has already forced the lock. The door is ajar."
        ),
        items=[],
        exits={"west": "c02", "north": "b03", "south": "d08", "east": "d10"},
        hidden_items=[],
    )

    rooms["d08"] = Room(
        name="Materials Lab",
        description=(
            "Sample analysis equipment, most powered down.\n"
            "The specimen log on the screen shows geological samples from the cave.\n"
            "The last entry reads: Sample 7 — ANOMALOUS. DO NOT TRANSFER."
        ),
        items=[
            Item(
                "specimen log",
                "log,samples",
                "A lab specimen log, electronic printout.",
                portable=True,
            ),
        ],
        exits={"north": "d07", "south": "d09"},
        hidden_items=[],
    )

    rooms["d09"] = Room(
        name="Spectrometry Lab",
        description=(
            "Dense analysis equipment, one unit still running.\n"
            "A crystal in the spectrometer tray — put there deliberately, or never removed.\n"
            "The readout shows a frequency the machine was not designed to find."
        ),
        items=[
            Item(
                "signal crystal",
                "crystal,signal",
                "A resonance crystal from the spectrometer tray.\n"
                "It reads at frequencies that should not occur naturally.",
                portable=True,
                required_for_win=True,
            ),
        ],
        exits={"north": "d08", "south": "d10"},
        hidden_items=[],
    )

    rooms["d10"] = Room(
        name="Xenobiology Lab",
        description=(
            "The core research room. Sealed sample cases, all empty.\n"
            "The whiteboard is covered in notes, half-erased. Something was being studied here.\n"
            "The something is no longer in this room."
        ),
        items=[
            Item(
                "xenobiology notes",
                "notes,xeno",
                "Research notes on the whiteboard, transcribed to a torn page.",
                portable=True,
                readable_text=XENOBIOLOGY_NOTE,
            ),
        ],
        exits={"north": "d07", "west": "d09", "south": "d11"},
        hidden_items=[],
    )

    rooms["d11"] = Room(
        name="Specimen Storage",
        description=(
            "Cold storage for biological samples. Every container is empty.\n"
            "One canister has been forced open from the inside.\n"
            "There is no biological residue inside it. The inside is clean."
        ),
        items=[],
        exits={"north": "d10", "south": "d12"},
        hidden_items=[],
    )

    rooms["d12"] = Room(
        name="Quarantine Chamber",
        description=(
            "A sealed, pressure-controlled room with a manual lock.\n"
            "The lock has been disabled — cut from the inside, not the outside.\n"
            "A science log is still running on the terminal."
        ),
        items=[
            Item(
                "quarantine log",
                "log,quarantine,science",
                "Dr. Reyes's science log, Day 14.",
                portable=True,
                readable_text=QUARANTINE_LOG,
            ),
        ],
        exits={"north": "d11", "west": "e05"},
        hidden_items=[],
    )

    # ── E. Habitation / Commons ───────────────────────────────────────────────

    rooms["e01"] = Room(
        name="Hab West Corridor",
        description=(
            "A residential corridor, fluorescent strips humming overhead.\n"
            "Three cabin doors on each side, most open.\n"
            "Personal effects visible through the doorways. Nobody collected them."
        ),
        items=[],
        exits={"north": "d06", "south": "e02", "east": "e05"},
        hidden_items=[],
    )

    rooms["e02"] = Room(
        name="Crew Quarters West",
        description=(
            "A four-bunk cabin, bunks made and unmade in equal measure.\n"
            "A child's drawing is taped inside one locker — a ship, a stick figure, and a sun.\n"
            "The sun has a smile. The ship does not."
        ),
        items=[
            Item(
                "loose can",
                "can,ration",
                "An empty ration can. Light. Loud when thrown.",
                portable=True,
                sound_on_use=3,
            ),
        ],
        exits={"north": "e01", "south": "e03"},
        hidden_items=[],
    )

    rooms["e03"] = Room(
        name="Laundry West",
        description=(
            "Washing units and drying racks, one still running on a cold cycle.\n"
            "A uniform is folded too neatly on the shelf — someone did this after.\n"
            "The sleeve has a burn mark that was not there before."
        ),
        items=[],
        exits={"north": "e02", "south": "e04"},
        hidden_items=[],
    )

    rooms["e04"] = Room(
        name="Lounge West",
        description=(
            "A recreational space. Card game still set up on the table.\n"
            "Someone's hand is face-down, mid-game, mid-play.\n"
            "The screen on the wall is showing a film nobody is watching."
        ),
        items=[
            Item(
                "loose can",
                "can,ration",
                "An empty ration can from the snack rack. Loud.",
                portable=True,
                sound_on_use=3,
            ),
        ],
        exits={"north": "e03", "east": "e05"},
        hidden_items=[],
    )

    rooms["e05"] = Room(
        name="Main Concourse",
        description=(
            "The central intersection — the widest point of the habitation deck.\n"
            "Six corridors branch from here. The overhead lights flicker in sequence.\n"
            "Someone has written something on the floor in marker: GO BACK."
        ),
        items=[],
        exits={
            "north": "b02",
            "south": "f01",
            "west": "e04",
            "east": "e10",
        },
        hidden_items=[],
    )
    # d03 and d12 also connect east/west, handled via those rooms' exits

    rooms["e06"] = Room(
        name="Cafeteria",
        description=(
            "Long tables, trays still out. A meal was interrupted here.\n"
            "The coffee machine is warm. There are no cups nearby.\n"
            "The emergency lighting makes everything the color of old film."
        ),
        items=[
            Item(
                "loose can",
                "can,ration",
                "A ration can, rolled under the serving counter.",
                portable=True,
                sound_on_use=3,
            ),
        ],
        exits={"north": "e05", "south": "e07", "west": "e09"},
        hidden_items=[],
    )

    rooms["e07"] = Room(
        name="Kitchen",
        description=(
            "Industrial kitchen equipment, grease-cold and dark.\n"
            "A cleaning duty roster on the wall — last entry, two weeks ago.\n"
            "A service crawl hatch in the floor, latched but not locked."
        ),
        items=[
            Item(
                "loose can",
                "can,ration",
                "An empty food can, dented.",
                portable=True,
                sound_on_use=3,
            ),
        ],
        exits={"north": "e06", "south": "e08"},
        hidden_items=[],
    )

    rooms["e08"] = Room(
        name="Freezer",
        description=(
            "Sub-zero food storage. The cold here is a physical presence.\n"
            "One freezer unit is open — the body inside is not frozen.\n"
            "Something used this room to wait. Or something still does."
        ),
        items=[],
        exits={"north": "e07"},
        hidden_items=[],
    )
    rooms["e08"].scanner_interference = True  # cold bloom confuses scanner

    rooms["e09"] = Room(
        name="Chapel",
        description=(
            "A small nondenominational room with folding chairs and a blank wall.\n"
            "Personal items left here — photos, letters, a folded uniform.\n"
            "A voice memo player sits on the lectern, battery dead."
        ),
        items=[
            Item(
                "chapel log",
                "log,memo,kessler",
                "A handwritten note left in the chapel.",
                portable=True,
                readable_text=CHAPEL_LOG,
            ),
        ],
        exits={"east": "e06"},
        hidden_items=[],
    )

    rooms["e10"] = Room(
        name="Hab East Corridor",
        description=(
            "The east residential corridor, mirror of the west.\n"
            "One cabin door is welded shut — someone used a torch.\n"
            "Marks on the outside of the door, not the inside."
        ),
        items=[],
        exits={"north": "d12", "south": "e11", "west": "e05"},
        hidden_items=[],
    )

    rooms["e11"] = Room(
        name="Crew Quarters East",
        description=(
            "Four bunks, two stripped bare, two still made.\n"
            "A pair of boots under the bunk by the window.\n"
            "People don't leave without their boots."
        ),
        items=[
            Item(
                "loose can",
                "can,ration",
                "An empty ration can on the bunk shelf.",
                portable=True,
                sound_on_use=3,
            ),
        ],
        exits={"north": "e10", "south": "e12"},
        hidden_items=[],
    )

    rooms["e12"] = Room(
        name="Laundry East",
        description=(
            "A second laundry room, all machines stopped.\n"
            "A uniform is caught in one of the drum doors, half-in, half-out.\n"
            "The sleeve has no arm in it."
        ),
        items=[],
        exits={"north": "e11", "south": "e13"},
        hidden_items=[],
    )

    rooms["e13"] = Room(
        name="Lounge East",
        description=(
            "Recreational space, east side. A pool table, cues still in the rack.\n"
            "A birthday banner across one wall. No one took it down.\n"
            "HAPPY 40th, MERCER. In bright letters."
        ),
        items=[
            Item(
                "loose can",
                "can,ration",
                "An empty can left on the pool table.",
                portable=True,
                sound_on_use=3,
            ),
        ],
        exits={"north": "e12", "west": "e05"},
        hidden_items=[],
    )

    # ── F. Industrial / Engineering ───────────────────────────────────────────

    rooms["f01"] = Room(
        name="Industrial Checkpoint",
        description=(
            "The boundary between habitation and engineering. A painted yellow line.\n"
            "SAFETY EQUIPMENT REQUIRED BEYOND THIS POINT. No equipment remains.\n"
            "The air already smells different here. Metal and heat."
        ),
        items=[],
        exits={"north": "e05", "south": "f07", "west": "f02", "east": "f04"},
        hidden_items=[],
    )

    rooms["f02"] = Room(
        name="Fabrication Bay",
        description=(
            "Manufacturing equipment, idle. A CNC unit still holds a half-finished part.\n"
            "The floor is marked with work zones in faded paint.\n"
            "A maintenance panel still warm from recent use."
        ),
        items=[],
        exits={"east": "f01", "south": "f03"},
        hidden_items=[],
    )

    rooms["f03"] = Room(
        name="Tool Cage",
        description=(
            "A locked cage of engineering tools, door open.\n"
            "Most tools accounted for on the board — a few gaps.\n"
            "Insulated gloves hang on a hook inside. So does a cutting torch."
        ),
        items=[
            Item(
                "insulated gloves",
                "gloves,insulated",
                "Heavy insulated work gloves. Required for handling live electrical components.",
                portable=True,
            ),
            Item(
                "cutting torch",
                "torch,cutter",
                "A handheld cutting torch. Opens vents and jammed panels. Slow and loud.",
                portable=True,
                sound_on_use=2,
            ),
        ],
        exits={"north": "f02"},
        hidden_items=[],
    )

    rooms["f04"] = Room(
        name="Environmental Control",
        description=(
            "Air pressure, temperature, and atmosphere management systems.\n"
            "The room hums with purpose — still running, still maintaining.\n"
            "A rerouting terminal could redirect airflow through certain sections."
        ),
        items=[],
        exits={"west": "f01", "south": "f05"},
        hidden_items=[],
    )

    rooms["f05"] = Room(
        name="Water Processing",
        description=(
            "Water recycling equipment, loud with pipe pressure.\n"
            "The noise here is constant and industrial — a useful cover.\n"
            "A synthetic maintenance report is logged on the wall panel."
        ),
        items=[],
        exits={"north": "f04", "south": "f06"},
        hidden_items=[],
    )

    rooms["f06"] = Room(
        name="Waste Processing",
        description=(
            "The least-visited room on the ship. Still running. Nobody's touched it.\n"
            "Conduit pipes line the walls, and a service crawl opens low on the south wall.\n"
            "Something has been through here. The grate was replaced incorrectly."
        ),
        items=[],
        exits={"north": "f05", "west": "f07"},
        hidden_items=[],
    )

    rooms["f07"] = Room(
        name="Engineering Control",
        description=(
            "The command center for ship systems. Most screens dead or looping on errors.\n"
            "A generator status terminal is active: GENERATOR OFFLINE — MANUAL RESTART REQUIRED.\n"
            "The ship map overlay on the west screen shows the whole deck."
        ),
        items=[],
        exits={"north": "f01", "south": "f08", "east": "f06"},
        hidden_items=[],
    )

    rooms["f08"] = Room(
        name="Power Distribution",
        description=(
            "A room of breaker panels, cable runs, and junction boxes.\n"
            "Main power routing — offline. The reset board has been bypassed, then re-bypassed.\n"
            "One junction box is open. Someone left it that way on purpose."
        ),
        items=[
            Item(
                "power regulator",
                "regulator,component",
                "A power regulation unit, company-grey. Precision-built.\nSurplus to the generator's requirements.",
                portable=True,
                required_for_win=True,
            ),
        ],
        exits={"north": "f07", "south": "f10", "west": "f09", "east": "f12"},
        hidden_items=[],
    )

    rooms["f09"] = Room(
        name="Generator Room",
        description=(
            "The emergency generator, offline and cold.\n"
            "A startup sequence card is taped to the panel. Half torn away.\n"
            "When this room runs, it is not a place to be."
        ),
        items=[],
        exits={"east": "f08"},
        hidden_items=[],
    )

    rooms["f10"] = Room(
        name="Reactor Monitoring",
        description=(
            "Reactor status panels, all nominal — the reactor runs without crew.\n"
            "A manual authorization terminal, bolted to the far wall.\n"
            "Someone tried to remove it. The bolts held better than they did."
        ),
        items=[
            Item(
                "manual authorization",
                "authorization,auth,manual",
                "A manual override authorization token. Required for AI containment unlock.",
                portable=True,
            ),
        ],
        exits={"north": "f08", "south": "f11"},
        hidden_items=[],
    )

    rooms["f11"] = Room(
        name="Reactor Chamber",
        description=(
            "The reactor roars. The heat is a wall.\n"
            "The noise here swallows everything — yours and not only yours.\n"
            "It has been through here. The floor shows it."
        ),
        items=[],
        exits={"north": "f10", "south": "g01"},
        hidden_items=[],
    )

    rooms["f12"] = Room(
        name="Coolant Control",
        description=(
            "Coolant pressure systems, pipes sweating in the heat from next door.\n"
            "Pressure is low — a lockout panel blinks amber.\n"
            "The manual bypass requires two hands and something between you and the live bus."
        ),
        items=[],
        exits={"west": "f08", "south": "f11"},
        hidden_items=[],
    )

    # ── G. Cargo / Docking ────────────────────────────────────────────────────

    rooms["g01"] = Room(
        name="Cargo Spine",
        description=(
            "A central loading corridor connecting cargo bays and docking.\n"
            "Cargo chains hang from the overhead rails.\n"
            "One sways. The air is still."
        ),
        items=[],
        exits={"north": "f11", "south": "g05", "west": "g02", "east": "g03"},
        hidden_items=[],
    )

    rooms["g02"] = Room(
        name="Cargo Bay A",
        description=(
            "Tall stacked containers, most still sealed with transit locks.\n"
            "The overhead cargo track runs the full length of the bay.\n"
            "Something has used it. The grease on the track is fresh and disturbed."
        ),
        items=[],
        exits={"east": "g01", "south": "g04"},
        hidden_items=[],
    )

    rooms["g03"] = Room(
        name="Cargo Bay B",
        description=(
            "A second cargo bay, similar to A but darker.\n"
            "Several containers have been shifted — dragged, not rolled.\n"
            "The manifest on the wall lists more cargo than is physically present."
        ),
        items=[],
        exits={"west": "g01", "south": "g04"},
        hidden_items=[],
    )

    rooms["g04"] = Room(
        name="Cargo Sorting Office",
        description=(
            "A small office overlooking the cargo bays through grimy glass.\n"
            "The cargo manifest is open on the desk — Sample 7 was moved here.\n"
            "The destination field reads: SCIENCE / D11 / HOLD FOR STUDY."
        ),
        items=[
            Item(
                "cargo manifest",
                "manifest,cargo,list",
                "A cargo sorting manifest. Sample 7, listed as biological: moved to D11.",
                portable=True,
            ),
        ],
        exits={"north": "g02", "south": "g05"},
        hidden_items=[],
    )

    rooms["g05"] = Room(
        name="Docking Control",
        description=(
            "Docking systems — bay doors, pressure seals, approach lights.\n"
            "The docking bay is sealed: QUARANTINE — NO EXTERNAL CONTACT PERMITTED.\n"
            "Someone added below it in marker: DON'T LET THEM IN."
        ),
        items=[],
        exits={"north": "g01", "south": "g06", "east": "g07"},
        hidden_items=[],
    )

    rooms["g06"] = Room(
        name="Main Airlock",
        description=(
            "The primary external airlock. Both doors sealed.\n"
            "The outer seal shows scoring on the inside — something tested it.\n"
            "The planet is on the other side. Nothing good is on this one."
        ),
        items=[],
        exits={"north": "g05", "south": "g08"},
        hidden_items=[],
    )

    rooms["g07"] = Room(
        name="Pressure Suit Locker",
        description=(
            "Suit storage for external operations. Two suits remain, both damaged.\n"
            "A body against the far wall in a partial suit, one glove on.\n"
            "Whatever the bare hand was reaching for is not in this room."
        ),
        items=[
            Item(
                "battery cell",
                "battery,cell,power",
                "A charged battery cell. Useful for improvised electronics.",
                portable=True,
            ),
        ],
        exits={"west": "g05"},
        hidden_items=[],
    )

    rooms["g08"] = Room(
        name="Escape Pod Corridor",
        description=(
            "The final corridor before the escape pods.\n"
            "Two pod bays on either side. One is missing — the pod was launched.\n"
            "The launch log shows it ejected during the incident. No beacon signal returned."
        ),
        items=[],
        exits={"north": "g06", "south": "g11", "west": "g09", "east": "g10"},
        hidden_items=[],
    )

    rooms["g09"] = Room(
        name="Escape Pod A",
        description=(
            "An escape pod, sealed and ready. One of two remaining.\n"
            "The launch controls are simple. One button.\n"
            "Leaving without sending the warning means nobody knows."
        ),
        items=[],
        exits={"east": "g08"},
        hidden_items=[],
    )

    rooms["g10"] = Room(
        name="Escape Pod B",
        description=(
            "A second escape pod, also sealed and ready.\n"
            "The interior smells of panic — old sweat, antiseptic, fear.\n"
            "Someone sat in here for a while before deciding not to go."
        ),
        items=[],
        exits={"west": "g08"},
        hidden_items=[],
    )

    rooms["g11"] = Room(
        name="Aft Beacon Service",
        description=(
            "The aft-most room. A beacon relay array, dead.\n"
            "A field note from the surface survey team is pinned to the wall.\n"
            "The relay cabinet is open. Something was removed. Something was also left."
        ),
        items=[
            Item(
                "antenna coupler",
                "coupler,antenna",
                "An antenna coupling unit from the beacon array.\nIt was designed to transmit. It still can.",
                portable=True,
                required_for_win=True,
            ),
            Item(
                "survey note",
                "note,survey,field",
                "A surface survey team field note.",
                portable=True,
                readable_text=AFT_BEACON_LOG,
            ),
        ],
        exits={"north": "g08"},
        hidden_items=[],
    )

    # ── M. Maintenance / Vent Network (M01-M30) ──────────────────────────────
    # Hidden crawlspace rooms. The alien uses these freely; so can the player.
    # Descriptions are sparse — these spaces are not meant to be comfortable.

    def mroom(rid, name, desc, exits_dict):
        r = Room(name=name, description=desc, items=[], exits=exits_dict, hidden_items=[])
        r.ambient_sound = 1  # pipes and air handlers, constant
        rooms[rid] = r

    # Forward section — Zones A-B
    mroom(
        "m01",
        "Forward Maintenance Shaft",
        "A low crawlway behind the forward sensor panels.\nService lights only. The panels tick and hum.",
        {"east": "a02", "south": "a05", "west": "m03"},
    )

    mroom(
        "m02",
        "Bridge Access Shaft",
        "A vertical service ladder beneath the bridge deck.\nGrease on the rungs. Fresh.",
        {"up": "a04", "east": "m03"},
    )

    mroom(
        "m03",
        "Forward Hub",
        "A wider junction where three maintenance shafts meet.\n"
        "Old inspection tags on the wall. The most recent is missing its date.",
        {"east": "m01", "west": "m02", "north": "m04", "south": "a07"},
    )

    mroom(
        "m04",
        "Security Access Shaft",
        "A shaft running through the security block.\nTwo panel covers have been removed and not replaced.",
        {"south": "m03", "down": "b02", "east": "b03", "north": "m05"},
    )

    mroom(
        "m05",
        "Security Branch",
        "A side branch off the security shaft.\nScratches on the floor. Something heavy was dragged through here.",
        {"south": "m04", "up": "b04", "east": "b05"},
    )

    # Cryo section — Zone C
    mroom(
        "m06",
        "Cryo North Shaft",
        "The maintenance passage behind the north cryo airlock.\nThe seals on this side are intact. Just.",
        {"east": "c05", "south": "m10"},
    )

    mroom(
        "m07",
        "Cryo East Shaft",
        "Behind the east airlock. The hum of the cryo systems is louder here.\nFrost forms at the panel seams.",
        {"west": "c06", "east": "m10"},
    )

    mroom(
        "m08",
        "Cryo South Shaft",
        "The maintenance passage behind the south airlock.\nA panel has been forced — from the outside.",
        {"east": "c07", "north": "m10"},
    )

    mroom(
        "m09",
        "Cryo West Shaft",
        "Behind the west airlock. The narrowest of the cryo shafts.\nSomething has left a mark at waist height.",
        {"east": "c08", "in": "m10"},
    )

    mroom(
        "m10",
        "Cryo Maintenance Hub",
        "A wider space connecting all four cryo airlock shafts.\n"
        "The air is cold enough that your breath shows.\n"
        "An access panel in the ceiling. Unlatched.",
        {"north": "m06", "west": "m07", "south": "m08", "out": "m09", "up": "c12", "east": "m11"},
    )

    # Medical/Science section — Zone D
    mroom(
        "m11",
        "Medical Maintenance Junction",
        "Where the cryo shafts meet the medical access.\n"
        "A junction box on the wall is open. Someone was in here recently.",
        {"west": "m10", "north": "d03", "south": "d04", "east": "m12"},
    )

    mroom(
        "m12",
        "Medical Spine",
        "A long maintenance corridor running behind the medical rooms.\n"
        "Emergency lighting only. Everything smells of antiseptic.",
        {"west": "m11", "east": "d04", "south": "m13"},
    )

    mroom(
        "m13",
        "Medical/Hab Junction",
        "Where the medical maintenance shaft branches toward habitation.\n"
        "Three directions, all dark. A locker on the wall, empty.",
        {"north": "m12", "east": "d06", "south": "m17"},
    )

    mroom(
        "m14",
        "Science Upper Shaft",
        "A shaft running above the science labs.\nThe floor vibrates faintly — analysis equipment below.",
        {"down": "d08", "west": "d09", "south": "m15"},
    )

    mroom(
        "m15",
        "Science Mid-Shaft",
        "Mid-level maintenance between the science labs.\nSample containment warnings on stickers. All expired.",
        {"north": "m14", "down": "d11", "south": "m16"},
    )

    mroom(
        "m16",
        "Science Lower Shaft",
        "The lowest science maintenance space, near the quarantine chamber.\n"
        "The air pressure feels wrong. Slightly off.",
        {"north": "m15", "up": "d12", "east": "m18"},
    )

    # Habitation section — Zone E
    mroom(
        "m17",
        "West Hab Shaft",
        "A maintenance passage running behind the west residential block.\n"
        "Personal items stuffed into the crawlway. Someone tried to hide things here.",
        {"north": "m13", "east": "e03", "south": "m19"},
    )

    mroom(
        "m18",
        "East Hab Shaft",
        "Behind the east residential block. Narrow.\nA boot print in the dust. Human-sized. Going south.",
        {"west": "e12", "north": "m16", "south": "m19"},
    )

    mroom(
        "m19",
        "Hab Maintenance Hub",
        "The central maintenance hub for the habitation deck.\n"
        "Five shafts branch from here. In the dark, they all look the same.",
        {"north": "m17", "west": "m18", "east": "m20", "south": "m22", "out": "e05"},
    )

    mroom(
        "m20",
        "Kitchen Shaft",
        "Behind the cafeteria and kitchen.\n"
        "Warm here — the kitchen machinery keeps this shaft above ambient temperature.",
        {"west": "m19", "up": "e07", "south": "m21"},
    )

    mroom(
        "m21",
        "Freezer Shaft",
        "Below the kitchen, near the freezer units.\n"
        "The cold comes through the wall. So does a smell you don't want to name.",
        {"north": "m20", "up": "e08", "south": "m23"},
    )

    mroom(
        "m22",
        "Chapel Shaft",
        "Behind the chapel and lounge east.\nQuiet here, even for a maintenance shaft.",
        {"north": "m19", "up": "e09", "east": "m23"},
    )

    # Engineering section — Zone F
    mroom(
        "m23",
        "Engineering Junction",
        "The maintenance hub for the engineering deck.\n"
        "Pipes everywhere, all labeled. The labels are covered in someone's handwriting:\n"
        "DO NOT RESTART. NO NO NO DO NOT RESTART.",
        {"north": "m21", "west": "m22", "up": "f02", "south": "m24"},
    )

    mroom(
        "m24",
        "Processing Shaft",
        "Behind the water and waste processing rooms.\nThe smell here has weight. You breathe through your mouth.",
        {"north": "m23", "up": "f05", "south": "m25"},
    )

    mroom(
        "m25",
        "Waste Shaft",
        "Below the waste processing unit.\nRunning liquid somewhere behind the wall. Do not think about it.",
        {"north": "m24", "up": "f06", "south": "m26"},
    )

    mroom(
        "m26",
        "Power Shaft",
        "Beneath the power distribution room.\nThe electrical noise here is a wall. Nothing reads cleanly.",
        {"north": "m25", "up": "f08", "east": "m27"},
    )
    rooms["m26"].scanner_interference = True

    mroom(
        "m27",
        "Generator Shaft",
        "Below the generator room. When the generator runs, this shaft vibrates.\n"
        "Right now it is silent. That is worse.",
        {"west": "m26", "up": "f09", "south": "m28"},
    )

    mroom(
        "m28",
        "Reactor Access Shaft",
        "The maintenance shaft beneath the reactor chamber.\n"
        "Heat radiates through the floor. Nobody stays longer than they have to.",
        {"north": "m27", "up": "f11", "south": "m29"},
    )
    rooms["m28"].ambient_sound = 2  # reactor vibration

    # Cargo section — Zone G
    mroom(
        "m29",
        "Cargo Access Hub",
        "Above the cargo bays. A junction with access down into both bays.\n"
        "Fresh scratch marks on the ceiling panel. Made from below.",
        {"north": "m28", "south": "m30", "down": "g02", "in": "g03"},
    )

    mroom(
        "m30",
        "Docking Shaft",
        "The aft-most maintenance space, above the docking level.\n"
        "A panel opens into the escape pod corridor. Emergency access.\n"
        "Something has been through here — the grate is warm.",
        {"north": "m29", "up": "g06", "out": "g08"},
    )

    # ── Hidden exits from visible rooms into the M-network ────────────────────
    # (Entries listed in SHIP.md as "hidden" — the player finds them by exploring)
    hidden_exits = {
        "a02": {"west": "m01"},
        "a04": {"down": "m02"},
        "b02": {"up": "m04"},
        "b04": {"down": "m05"},
        "c05": {"west": "m06"},
        "c06": {"east": "m07"},
        "c07": {"west": "m08"},
        "c08": {"west": "m09"},
        "c12": {"down": "m10"},
        "d04": {"west": "m12"},
        "d06": {"west": "m13"},
        "d08": {"up": "m14"},
        "d11": {"up": "m15"},
        "d12": {"down": "m16"},
        "e03": {"west": "m17"},
        "e12": {"east": "m18"},
        "e07": {"down": "m20"},
        "e08": {"down": "m21"},
        "e09": {"down": "m22"},
        "f02": {"down": "m23"},
        "f05": {"down": "m24"},
        "f06": {"down": "m25"},
        "f08": {"down": "m26"},
        "f09": {"down": "m27"},
        "f11": {"down": "m28"},
        "g02": {"up": "m29"},
        "g03": {"up": "m29"},
        "g06": {"down": "m30"},
        "g08": {"in": "m30"},
    }
    for room_id, extra_exits in hidden_exits.items():
        rooms[room_id].exits.update(extra_exits)

    # ── Apply room IDs, hiding spots, ambient sound, scanner interference ─────

    for room_id, room in rooms.items():
        room.id = room_id

    for room_id, spots in HIDING_SPOTS.items():
        if room_id in rooms:
            rooms[room_id].hiding_spots = list(spots)

    for room_id, level in AMBIENT_SOUND.items():
        if room_id in rooms:
            rooms[room_id].ambient_sound = level

    for room_id in SCANNER_INTERFERENCE_ROOMS:
        if room_id in rooms:
            rooms[room_id].scanner_interference = True

    # ── "Aboard" variants — ship changes once the alien is confirmed active ───
    aboard = {
        "a01": ("The viewport. The dead planet below.\nYour reflection in the glass is not in the right position."),
        "a02": (
            "Instrument panels. The service hatch in the west wall is wider open than before.\nYou did not open it."
        ),
        "a03": (
            "Navigation. The return course still unfiled.\n"
            "The plotted trajectory has been altered. You did not alter it."
        ),
        "a04": ("The bridge. All screens live.\nThe captain's chair is facing the wrong direction now. Slowly."),
        "a05": (
            "The ready room. The desk note, the keycard.\nThe photo on the desk is facing you now. Someone turned it."
        ),
        "a06": (
            "The comm array, dead. TRANSMISSION BLOCKED — DIRECTIVE 2.\n"
            "A sound from the east vent. Three soft taps. Then nothing."
        ),
        "a07": (
            "The antenna control room. The three empty sockets.\nThe room behind you is breathing. In, and out, and in."
        ),
        "a08": (
            "The archive. The AI log cycling.\n"
            "One terminal has been touched since you were last here. The screen is warm."
        ),
        "b01": (
            "Security checkpoint. The gate still wedged open.\n"
            "The body near the gate has been moved. Not far. Just enough."
        ),
        "b02": (
            "Security hub. The camera feeds — empty corridors.\n"
            "One feed shows a room you haven't left yet. The timestamp is wrong."
        ),
        "b03": (
            "Surveillance theater. The two live screens.\nThe second screen no longer shows static. It shows this room."
        ),
        "b04": ("Armory. The empty racks. The remaining flares.\nThe ceiling vent is open. It was closed before."),
        "b05": (
            "The detention cell. The personal log on the bunk.\n"
            "The scratch marks on the door are deeper now. Made from the outside."
        ),
        "b06": (
            "Admin records. The crew manifest. Twenty-three names.\n"
            "Someone has added a twenty-fourth, in a different hand. No name. Just a mark."
        ),
        "c01": (
            "North vestibule. Cooler here.\n"
            "The biological scan placard has been pulled from the wall and placed face-down."
        ),
        "c02": (
            "East vestibule. The dark scan panel.\n"
            "Something has pressed against the south airlock door. The seal holds."
        ),
        "c03": (
            "South vestibule. The footprints in the dust.\n"
            "New footprints now — narrower, coming from the south, not human."
        ),
        "c04": ("West vestibule. The cracked defibrillator.\nThe sound of breathing from the corridor. Not yours."),
        "d01": (
            "Medical reception. The plastic chairs. The triage clipboard.\n"
            "The pen on the clipboard is gone. The last name now has a line through it."
        ),
        "d02": (
            "Triage. The body by the north door, arm stretched toward the lock.\n"
            "The body has been moved. The arm is no longer reaching for the lock."
        ),
        "d03": (
            "Diagnostics. The patient record: misplaced personnel event.\n"
            "The scan unit has activated itself. It is tracking something in the room with you."
        ),
        "d04": (
            "Surgery. The procedure light. The used table.\n"
            "The surgical notes on the tray are no longer where you left them."
        ),
        "d05": (
            "Pharmacy. The forced cabinet, the bare shelves.\n"
            "The note on the door — TAKE WHAT YOU NEED — has been turned over."
        ),
        "d06": ("Morgue. The closed drawers. Drawer 7, labeled SPECIMEN.\nDrawer 7 is ajar. You did not open it."),
        "d07": ("Science reception. The forced door.\nThe door is closed now. You don't remember closing it."),
        "d08": ("Materials lab. The sample log on the screen.\nSample 7's entry has been deleted. Recently."),
        "d09": ("Spectrometry lab. The running unit.\nThe running unit has changed its frequency scan without input."),
        "d10": (
            "Xenobiology lab. The empty sample cases. The whiteboard notes.\n"
            "New marks on the whiteboard. Not writing. Something else."
        ),
        "d11": (
            "Specimen storage. Every container empty. The forced-open canister.\nThe canister is not where you left it."
        ),
        "d12": ("Quarantine chamber. The disabled lock.\nThe lock has been disabled from the other side now too."),
        "e01": ("Hab west corridor. Cabin doors open.\nOne cabin door is closed now. You did not close it."),
        "e02": (
            "Crew quarters west. The bunks. The child's drawing.\n"
            "The drawing is face-down. The lockers have been gone through."
        ),
        "e03": (
            "Laundry west. The machine on a cold cycle.\n"
            "The machine has stopped. The drum holds something that shouldn't be in it."
        ),
        "e05": (
            "Main concourse. The six corridors. The flickering lights.\n"
            "GO BACK on the floor. Someone has added: TOO LATE."
        ),
        "e06": (
            "Cafeteria. The warm coffee machine, still no cups.\n"
            "A tray has been overturned. A chair dragged against the wall."
        ),
        "e07": (
            "Kitchen. The cold equipment. The duty roster.\n"
            "The service crawl hatch is open. It was latched when you came through."
        ),
        "e08": (
            "Freezer. Sub-zero. The open unit. The body inside that is not frozen.\n"
            "The scanner is useless here. Whatever is in the room with you, it knows that."
        ),
        "e09": (
            "Chapel. The folding chairs, the personal items.\nOne chair faces the door. It wasn't like that before."
        ),
        "e10": ("Hab east corridor. The welded door.\nThe marks on the outside of the welded door are fresh."),
        "e11": (
            "Crew quarters east. The unmade bunks. The boots under the window bunk.\n"
            "The boots have been moved. Not taken — just moved."
        ),
        "e12": ("Laundry east. The uniform caught in the drum door.\nThe uniform is gone. The drum door is closed."),
        "e13": (
            "Lounge east. The pool table. HAPPY 40th, MERCER.\n"
            "The banner is on the floor. The pool cues are arranged differently."
        ),
        "e04": (
            "Lounge west. The card game. The face-down hand.\nThe hand has been played. Someone finished the game."
        ),
        "f01": (
            "Industrial checkpoint. The yellow safety line.\nSomething has crossed it, back and forth, many times."
        ),
        "f02": (
            "Fabrication bay. The idle CNC unit.\n"
            "The maintenance panel is cold now. Something was working here. It isn't."
        ),
        "f03": (
            "Tool cage. The insulated gloves. The cutting torch.\n"
            "The cage door is closed now. Someone pulled it shut after you."
        ),
        "f04": (
            "Environmental control. The humming systems.\n"
            "Airflow from the east vent has changed. Something is in the duct."
        ),
        "f05": ("Water processing. The loud pipe pressure.\nA new sound under the pipes — movement, not mechanical."),
        "f06": ("Waste processing. Still running.\nThe replaced grate has been moved again. The gap is large enough."),
        "f07": (
            "Engineering control. GENERATOR OFFLINE — MANUAL RESTART REQUIRED.\n"
            "The ship map overlay now shows a moving point on the deck. It is not you."
        ),
        "f08": ("Power distribution. The breaker panels.\nA panel has been opened — not to sabotage. To observe."),
        "f09": ("Generator room. Silent or roaring.\nThe noise hides you. It hides everything else too."),
        "f10": (
            "Reactor monitoring. The authorization terminal.\nThe terminal has been accessed since you were last here."
        ),
        "f11": ("Reactor chamber. The roar. The heat.\nSomething passes through here without caring about either."),
        "f12": ("Coolant control. The sweating pipes.\nA handprint on the coolant tank. Not a human handprint."),
        "g01": ("Cargo spine. The swaying chain.\nAll the chains are moving now. The air is still."),
        "g02": (
            "Cargo bay A. The overhead track, disturbed grease.\n"
            "The grease marks continue over the stacked containers. It was up there."
        ),
        "g03": ("Cargo bay B. The shifted containers.\nOne container is open. The interior has been nested."),
        "g04": (
            "Cargo sorting office. Sample 7 was here.\n"
            "The grimy office glass has a smear on the inside. From inside the office."
        ),
        "g05": (
            "Docking control. DON'T LET THEM IN.\n"
            "The quarantine seal light is blinking. Something tested the outer door."
        ),
        "g06": (
            "Main airlock. Both seals holding.\nThe scoring on the inner seal is new. It is testing from this side now."
        ),
        "g07": (
            "Pressure suit locker. The partial-suited body.\n"
            "The battery cell has been moved. Someone — something — looked at it."
        ),
        "g08": (
            "Escape pod corridor. One pod missing. Two remaining.\n"
            "The launch log has been accessed. The record has been deleted."
        ),
        "g09": ("Escape pod A. The launch button.\nLeaving is possible. The question is what you leave behind."),
        "g10": ("Escape pod B. The smell of old fear.\nNew fear now. Yours. Sitting in the same seat."),
        "g11": ("Aft beacon service. Where it began.\nYou can feel the weight of the ship above you pressing down."),
    }

    for room_id, text in aboard.items():
        if room_id in rooms:
            rooms[room_id].variants["aboard"] = text

    return rooms
