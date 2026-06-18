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
        self.type = player_type  # human, synthetic, contract_specialist

        # Health and status
        self.health = 100
        self.suit_worn = False
        self.outside_exposure_turns = 0

        # Game state
        self.hidden = False
        self.hidden_spot: dict | None = None  # the spot dict the player is using
        self.last_room_id: str | None = None
        self.stayed_turns_in_room = 0

        # Inventory
        self.inventory = []
        self.worn_items = []

        # Progress flags mirrored for convenience
        self.has_terminal = False
        self.has_power_coupler = False  # installed in transmitter
        self.has_signal_relay = False
        self.has_antenna_key = False
        self.transmitter_repaired = False

    # --- toxic exposure tolerance by type ---
    @property
    def toxic_tolerance(self) -> int:
        """How many turns in toxic air before death (without a suit)."""
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

    def installed_parts(self) -> int:
        return sum([self.has_power_coupler, self.has_signal_relay, self.has_antenna_key])
