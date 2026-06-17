"""
Monster class for THE THIN AIR game
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from room import Room
class Monster:
    def __init__(self):
        self.active = False
        self.phase = "dormant"  # dormant, following, aboard, hunting, investigating, searching, same_room, attacking, feeding
        self.current_room_id = None
        self.state = "dormant"
        self.target_room_id = None
        self.last_heard_room_id = None
        self.last_seen_room_id = None
        self.suspicion_by_room = {}
        self.turns_since_seen = 0
        self.turns_since_heard = 0
        self.movement_cooldown = 0
        self.aggression = 0
        self.rooms_checked_recently = []
        self.known_hiding_spots = {}
        self.distracted_until_turn = 0
        self.can_use_vents = False
        
    def set_active(self, active: bool):
        self.active = active
        
    def set_phase(self, phase: str):
        self.phase = phase
        
    def set_state(self, state: str):
        self.state = state
        
    def add_suspicion(self, room_id: str, amount: int):
        if room_id not in self.suspicion_by_room:
            self.suspicion_by_room[room_id] = 0
        self.suspicion_by_room[room_id] += amount
        
    def get_highest_suspicion_room(self):
        if not self.suspicion_by_room:
            return None
        return max(self.suspicion_by_room, key=self.suspicion_by_room.get)
        
    def clear_suspicion(self):
        self.suspicion_by_room.clear()
        
    def update_suspicion_decay(self):
        for room_id in list(self.suspicion_by_room.keys()):
            self.suspicion_by_room[room_id] = max(0, self.suspicion_by_room[room_id] - 1)
            if self.suspicion_by_room[room_id] <= 0:
                del self.suspicion_by_room[room_id]
        
    def is_distracted(self, current_turn: int) -> bool:
        return current_turn < self.distracted_until_turn
        
    def set_distracted(self, until_turn: int):
        self.distracted_until_turn = until_turn