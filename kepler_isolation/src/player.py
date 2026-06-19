"""
Player class for KEPLER ISOLATION game
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Player:
    def __init__(self, name: str, gender: str, player_type: str):
        self.name = name
        self.gender = gender
        self.type = player_type  # crew, synthetic, contractor

        # Health and status
        self.health = 100
        self.suit_worn = False
        self.outside_exposure_turns = 0

        # Game state
        self.hidden = False
        self.hidden_spot: dict | None = None
        self.last_room_id: str | None = None
        self.stayed_turns_in_room = 0

        # Inventory
        self.inventory = []
        self.worn_items = []

        # Scanner + mission flags
        self.has_terminal = False
        # Radio mission: collect 4 components, craft in C13, install and transmit in A07
        self.has_coil = False        # transmitter coil (A07)
        self.has_crystal = False     # signal crystal (D09)
        self.has_regulator = False   # power regulator (F08)
        self.has_coupler = False     # antenna coupler (G11)
        self.radio_built = False     # improvised radio assembled at C13

    @property
    def toxic_tolerance(self) -> int:
        return 3 if self.type == "synthetic" else 2

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

    def has_item(self, name: str):
        for item in self.inventory:
            if item.matches_name(name):
                return item
        return None

    def is_wearing_suit(self):
        return self.suit_worn

    def radio_component_count(self) -> int:
        return sum([self.has_coil, self.has_crystal, self.has_regulator, self.has_coupler])
