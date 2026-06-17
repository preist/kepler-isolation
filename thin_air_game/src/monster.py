"""
Monster class for THE THIN AIR game

The monster is a real entity on the map. Its behaviour (pathfinding, target
selection, detection) is driven by GameState, which has access to the room
graph. This class holds the monster's state and a few small helpers.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Monster:
    def __init__(self):
        self.active = False
        # dormant, following, aboard
        self.phase = "dormant"
        self.current_room_id = None
        # behavioural state: aboard, investigating, hunting, searching, feeding
        self.state = "dormant"
        self.target_room_id = None
        self.last_heard_room_id = None
        self.last_seen_room_id = None
        self.suspicion_by_room = {}
        self.turns_since_seen = 999
        self.turns_since_heard = 999
        self.movement_cooldown = 0
        self.aggression = 0              # 0 low .. 3 very high
        self.distracted_until_turn = 0
        self.can_use_vents = False
        # how many times in a row it has been in the player's room while the
        # player stayed hidden (escalates detection)
        self.searching_streak = 0

    def add_suspicion(self, room_id: str, amount: int):
        if not room_id:
            return
        self.suspicion_by_room[room_id] = self.suspicion_by_room.get(room_id, 0) + amount

    def get_highest_suspicion_room(self):
        if not self.suspicion_by_room:
            return None
        room_id = max(self.suspicion_by_room, key=self.suspicion_by_room.get)
        if self.suspicion_by_room[room_id] <= 0:
            return None
        return room_id

    def clear_suspicion(self):
        self.suspicion_by_room.clear()

    def update_suspicion_decay(self):
        for room_id in list(self.suspicion_by_room.keys()):
            self.suspicion_by_room[room_id] -= 1
            if self.suspicion_by_room[room_id] <= 0:
                del self.suspicion_by_room[room_id]

    def is_distracted(self, current_turn: int) -> bool:
        return current_turn < self.distracted_until_turn

    def set_distracted(self, until_turn: int):
        self.distracted_until_turn = until_turn
