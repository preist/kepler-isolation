"""
Game state class for THE THIN AIR game
"""

class GameState:
    def __init__(self):
        self.player = None
        self.rooms = {}
        self.current_room_id = "cockpit"
        self.inventory = []
        self.worn_items = []
        self.turn_count = 0
        self.game_phase = "intro"  # intro, pre_cave, outside, cave_triggered, returned_to_ship, monster_aboard, final_repair, won, dead
        
        # Monster
        self.monster = None
        
        # Sound system
        self.sound_level = "silent"
        self.last_action_sound = 0
        
        # Flags
        self.flags = {
            "has_terminal": False,
            "suit_taken": False,
            "suit_worn": False,
            "went_outside": False,
            "entered_cave": False,
            "examined_beacon": False,
            "cave_triggered": False,
            "returned_after_cave": False,
            "monster_boarded": False,
            "saw_window_creature": False,
            "comms_damaged_known": False,
            "has_power_coupler": False,
            "has_signal_relay": False,
            "has_antenna_key": False,
            "transmitter_repaired": False,
            "warning_sent": False,
            "sable_awake": False,
            "sable_alive": False,
            "sable_following": False,
            "sable_sacrifice_used": False
        }
        
        # Additional tracking
        self.visited_rooms = set()
        self.death_state = None
        self.win_state = False
        self.message_log = []
        self.random_seed = 42
        
    def get_flag(self, flag_name: str) -> bool:
        return self.flags.get(flag_name, False)
        
    def set_flag(self, flag_name: str, value: bool):
        self.flags[flag_name] = value
        
    def increment_turn(self):
        self.turn_count += 1
        
    def add_to_message_log(self, message: str):
        self.message_log.append(message)
        
    def get_room_by_id(self, room_id: str) -> object:
        return self.rooms.get(room_id)
        
    def initialize_monster(self):
        from .monster import Monster
        self.monster = Monster()
        self.monster.current_room_id = "airlock"  # Start in airlock
        self.monster.set_active(False)
        self.monster.set_phase("dormant")
