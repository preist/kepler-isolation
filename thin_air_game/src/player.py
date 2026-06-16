"""
Player class for THE THIN AIR game
"""

class Player:
    def __init__(self, name: str, gender: str, player_type: str):
        self.name = name
        self.gender = gender
        self.type = player_type  # human, synthetic, contract_specialist
        
        # Health and status
        self.health = 100
        self.suit_worn = False
        self.outside_exposure_turns = 0
        
        # Game state
        self.hidden = False
        self.hidden_spot = None
        self.last_room_id = None
        self.stayed_turns_in_room = 0
        
        # Inventory
        self.inventory = []
        self.worn_items = []
        
        # Flags
        self.has_terminal = False
        self.suit_taken = False
        self.went_outside = False
        self.entered_cave = False
        self.cave_triggered = False
        self.returned_after_cave = False
        self.monster_boarded = False
        self.comms_damaged_known = False
        self.has_power_coupler = False
        self.has_signal_relay = False
        self.has_antenna_key = False
        self.transmitter_repaired = False
        self.warning_sent = False
        
    def wear_item(self, item):
        if item.wearable:
            self.worn_items.append(item)
            return True
        return False
        
    def remove_item(self, item):
        if item in self.worn_items:
            self.worn_items.remove(item)
            return True
        return False
        
    def add_to_inventory(self, item):
        self.inventory.append(item)
        
    def remove_from_inventory(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
        
    def is_wearing_suit(self):
        return self.suit_worn
        
    def set_suit_worn(self, worn: bool):
        self.suit_worn = worn