"""
Monster class for THE THIN AIR game
"""

class Monster:
    def __init__(self):
        self.active = False
        self.phase = "dormant"  # dormant, following, aboard, hunting, searching, investigating, same_room, attacking, feeding
        
        # Position and movement
        self.current_room_id = None
        self.target_room_id = None
        self.last_heard_room_id = None
        self.last_seen_room_id = None
        
        # Behavior tracking
        self.suspicion_by_room = {}  # room_id -> suspicion_score
        self.turns_since_seen = 0
        self.turns_since_heard = 0
        self.movement_cooldown = 0
        self.aggression = 0  # 0-10 scale
        
        # Memory
        self.rooms_checked_recently = []
        self.known_hiding_spots = {}
        self.distracted_until_turn = 0
        self.can_use_vents = False
        
    def set_active(self, active: bool):
        self.active = active
        
    def set_phase(self, phase: str):
        self.phase = phase
        
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
        
    def get_target_room(self, player_room_id: str, game_state):
        # Priority:
        # 1. If violent/loud sound recently heard: target that room
        # 2. If saw player: target player room
        # 3. Highest suspicion room
        # 4. Patrol route
        
        if self.last_heard_room_id and self.turns_since_heard < 5:
            return self.last_heard_room_id
        
        if self.last_seen_room_id:
            return self.last_seen_room_id
        
        # Check highest suspicion room
        highest_suspicion = self.get_highest_suspicion_room()
        if highest_suspicion:
            return highest_suspicion
        
        # Default to patrol (for now, just return player room)
        return player_room_id