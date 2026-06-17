"""
Map builder for THE THIN AIR game
Creates and initializes all rooms with their correct exits as specified in the requirements.
"""

from .room import Room
from .item import Item


def create_rooms():
    """
    Create all 22 rooms with their properties and exits according to the specification.
    """
    rooms = {}
    
    # Ship rooms
    rooms["cockpit"] = Room(
        name="Cockpit",
        description="Dead stars in the glass. The console waits with one green light.",
        items=[Item("hand terminal", "terminal,scanner", "A portable scanner that can detect motion.", portable=True, wearable=False)],
        exits={"south": "central_corridor"},
        hidden_items=[]
    )
    
    rooms["central_corridor"] = Room(
        name="Central Corridor",
        description="Low ceiling. Handrails. Old boot marks. The lights hum in pairs.",
        items=[],
        exits={"north": "cockpit", "east": "airlock", "south": "med_bay", "west": "engineering_access"},
        hidden_items=[]
    )
    
    rooms["airlock"] = Room(
        name="Airlock",
        description="Suit locker. Outer hatch. Inner hatch. A red card says: TWO MOVES WITHOUT SEAL.",
        items=[Item("EVA suit", "suit,eva", "A full EVA suit for surface exploration.", portable=True, wearable=True)],
        exits={"west": "central_corridor", "out": "surface"},
        hidden_items=[]
    )
    
    rooms["med_bay"] = Room(
        name="Med Bay",
        description="Medical supplies. A recorder log sits on the table.",
        items=[Item("medkit", "medic,health", "A small medical kit for treating injuries.", portable=True), Item("recorder log", "log,note", "A recording of previous crew member's last moments.", portable=False, readable_text="I can't hear it anymore. It's in the walls.")],
        exits={"north": "central_corridor", "east": "crew_quarters"},
        hidden_items=["cabinet"]
    )
    
    rooms["crew_quarters"] = Room(
        name="Crew Quarters",
        description="Bunks and personal lockers. A faint smell of old coffee lingers.",
        items=[Item("access card", "card,id,identification", "A corporate access card for restricted areas.", portable=True), Item("bunk", "bed", "A simple bunk bed.", portable=False)],
        exits={"west": "med_bay", "south": "galley"},
        hidden_items=["under bunk"]
    )
    
    rooms["galley"] = Room(
        name="Galley",
        description="A small kitchen area. Loose cans are scattered on the floor.",
        items=[Item("loose can", "can,food", "A loose food can that makes noise when moved.", portable=True), Item("water recycler", "recycler,water", "A water recycling machine.", portable=False)],
        exits={"north": "crew_quarters", "west": "storage"},
        hidden_items=[]
    )
    
    rooms["storage"] = Room(
        name="Storage",
        description="Boxes and crates. A musty smell fills the air.",
        items=[Item("power coupler", "coupler,part", "A power coupling part needed for transmitter repair.", portable=True, required_for_win=True)],
        exits={"east": "galley", "south": "cargo_bay", "west": "engineering_access"},
        hidden_items=["shelving"]
    )
    
    rooms["engineering_access"] = Room(
        name="Engineering Access",
        description="A narrow passage. A panel hangs open.",
        items=[],
        exits={"east": "central_corridor", "south": "reactor_room", "west": "storage"},
        hidden_items=["crawlspace"]
    )
    
    rooms["reactor_room"] = Room(
        name="Reactor Room",
        description="The reactor hums with heat. A control panel glows dimly.",
        items=[Item("signal relay", "relay,part", "A signal relay part needed for transmitter repair.", portable=True, required_for_win=True)],
        exits={"north": "engineering_access"},
        hidden_items=[]
    )
    
    rooms["cargo_bay"] = Room(
        name="Cargo Bay",
        description="Large crates and forklift tracks. The air is thick with dust.",
        items=[Item("antenna key", "key,part", "An antenna key needed for transmitter repair.", portable=True, required_for_win=True), Item("crate", "box", "A large crate.", portable=False)],
        exits={"north": "storage", "east": "maintenance_junction", "south": "lower_hold"},
        hidden_items=["behind crates"]
    )
    
    rooms["lower_hold"] = Room(
        name="Lower Hold",
        description="A dark, narrow space. Scratch marks on the walls.",
        items=[Item("beacon fragment", "fragment,part", "A piece of a distress beacon.", portable=True)],
        exits={"north": "cargo_bay"},
        hidden_items=[]
    )
    
    rooms["maintenance_junction"] = Room(
        name="Maintenance Junction",
        description="A junction point for maintenance tunnels. Tools are scattered.",
        items=[Item("repair kit", "kit,tool", "A repair kit for fixing equipment.", portable=True)],
        exits={"west": "cargo_bay", "east": "comms_hall", "north": "ventral_service"},
        hidden_items=[]
    )
    
    rooms["ventral_service"] = Room(
        name="Ventral Service",
        description="A mechanical room with noisy fans. Ventilation ducts lead everywhere.",
        items=[],
        exits={"south": "maintenance_junction", "east": "observation"},
        hidden_items=[]
    )
    
    rooms["observation"] = Room(
        name="Observation",
        description="A long window. The planet presses its dark face against it.",
        items=[],
        exits={"west": "ventral_service", "south": "comms_hall"},
        hidden_items=[]
    )
    
    rooms["comms_hall"] = Room(
        name="Comms Hall",
        description="A corridor leading to the communications room. The walls are lined with equipment.",
        items=[],
        exits={"north": "observation", "west": "maintenance_junction", "east": "communications"},
        hidden_items=[]
    )
    
    rooms["communications"] = Room(
        name="Communications",
        description="The heart of the ship's communication system. The transmitter is damaged.",
        items=[Item("transmitter", "radio,comm,transmit", "A damaged communication transmitter that needs repair.", portable=False, install_target="transmitter")],
        exits={"west": "comms_hall"},
        hidden_items=[]
    )
    
    # Surface/cave rooms
    rooms["surface"] = Room(
        name="Surface",
        description="Black dust moves like smoke. Your suit light finds the cave mouth east.",
        items=[],
        exits={"in": "airlock", "east": "ridge", "south": "landing_gear"},
        hidden_items=[]
    )
    
    rooms["landing_gear"] = Room(
        name="Landing Gear",
        description="The landing gear is damaged. Strange slime marks are on the metal.",
        items=[Item("slime mark", "mark,slime", "A strange mark that looks like it was left by something organic.", portable=False)],
        exits={"north": "surface"},
        hidden_items=[]
    )
    
    rooms["ridge"] = Room(
        name="Ridge",
        description="The ridge is narrow. The cave mouth is just east.",
        items=[],
        exits={"west": "surface", "east": "cave_mouth"},
        hidden_items=[]
    )
    
    rooms["cave_mouth"] = Room(
        name="Cave Mouth",
        description="The signal is louder here. Not stronger. Louder.",
        items=[],
        exits={"west": "ridge", "down": "signal_cave"},
        hidden_items=[]
    )
    
    rooms["signal_cave"] = Room(
        name="Signal Cave",
        description="A narrow cave with strange markings on the walls. The signal is strongest here.",
        items=[Item("distress beacon", "beacon,signal", "A damaged distress beacon that triggered the rescue mission.", portable=False, readable_text="DO NOT OPEN THE...")],
        exits={"up": "cave_mouth", "east": "black_pool"},
        hidden_items=[]
    )
    
    rooms["black_pool"] = Room(
        name="Black Pool",
        description="A small pool of black liquid. The walls are covered in strange marks.",
        items=[Item("old helmet", "helmet,head", "An old helmet that looks like it was worn by someone else.", portable=True)],
        exits={"west": "signal_cave"},
        hidden_items=[]
    )
    
    # Set room IDs
    for room_id, room in rooms.items():
        room.id = room_id
        
    return rooms