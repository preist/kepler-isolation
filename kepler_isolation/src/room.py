"""
Room class for KEPLER ISOLATION game
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from item import Item


class Room:
    def __init__(self, name: str, description: str, items: list, exits: dict, hidden_items: list):
        self.id = None  # Will be set by the map builder
        self.name = name
        self.description = description
        self.items = items
        self.exits = exits  # direction -> room_id
        self.hidden_items = hidden_items
        # State-keyed description variants, e.g. {"aboard": "...", "triggered": "..."}.
        # describe() swaps these in so the ship can change under the player.
        self.variants = {}

        # Room properties
        self.hazards = []
        # Vent shortcuts the monster can use once aboard (direction-less list of room_ids).
        self.vent_exits = []
        # Hiding spots: list of dicts {"name", "quality", "reuse"}
        self.hiding_spots = []
        self.monster_allowed = True
        self.toxic = False                # lethal atmosphere if not wearing a suit
        self.scanner_interference = False  # scanner is unreliable here
        self.ambient_sound = 0            # 0 silent .. 3 loud; masks/echoes player sound
        self.visited = False

    def describe(self, game_state) -> str:
        """Return the description for the current world state. Most dramatic
        variant wins: a boarded monster reframes the room over the mere fact
        that the cave was triggered."""
        if game_state.get_flag("monster_boarded") and "aboard" in self.variants:
            return self.variants["aboard"]
        if game_state.get_flag("cave_triggered") and "triggered" in self.variants:
            return self.variants["triggered"]
        return self.description

    def add_exit(self, direction: str, room_id: str):
        self.exits[direction] = room_id

    def get_item(self, item_name: str):
        for item in self.items:
            if item.matches_name(item_name):
                return item
        return None

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def find_hiding_spot(self, name: str = None):
        """Return a hiding spot dict. If name is given, match it; otherwise pick
        the highest-quality spot available."""
        if not self.hiding_spots:
            return None
        if name:
            name = name.lower().strip()
            for spot in self.hiding_spots:
                if name in spot["name"].lower() or spot["name"].lower() in name:
                    return spot
            return None
        return max(self.hiding_spots, key=lambda s: s["quality"])
