"""
Room class for THE THIN AIR game
"""

class Room:
    def __init__(self, name: str, description: str, items: list, exits: dict, hidden_items: list):
        self.id = None  # Will be set by game state
        self.name = name
        self.description = description
        self.items = items
        self.exits = exits  # direction -> room_id
        self.hidden_items = hidden_items
        
        # Room properties
        self.hazards = []
        self.hiding_spots = []
        self.monster_allowed = True
        self.scanner_interference = False
        self.ambient_sound = 0  # 0 = silent, 1 = quiet, 2 = audible, 3 = loud
        self.visited = False
        
    def add_exit(self, direction: str, room_id: str):
        self.exits[direction] = room_id
        
    def get_item(self, item_name: str):
        for item in self.items:
            if item.name.lower() == item_name.lower():
                return item
        return None
        
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False