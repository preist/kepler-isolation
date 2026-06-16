"""
Parser class for THE THIN AIR game
"""

from typing import List, Tuple, Optional
from .game_state import GameState
from .player import Player
from .room import Room
from .item import Item


class Parser:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.player = game_state.player
        
        # Command aliases
        self.aliases = {
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "u": "up",
            "d": "down",
            "x": "examine",
            "get": "take",
            "i": "inventory",
            "inv": "inventory",
            "l": "look",
            "scan": "scan",
            "read": "read",
            "use": "use",
            "wear": "wear",
            "remove": "remove",
            "put on": "wear",
            "take off": "remove",
            "repair": "repair",
            "install": "install",
            "throw": "throw",
            "hide": "hide",
            "crawl": "crawl",
            "run": "run",
            "wait": "wait",
            "listen": "listen",
            "map": "map",
            "help": "help",
            "quit": "quit",
            "restart": "restart"
        }
        
    def parse_command(self, command: str) -> str:
        # Normalize command
        command = command.strip().lower()
        
        # Handle empty commands
        if not command:
            return "What?"
        
        # Split into words
        words = command.split()
        
        # Handle aliases
        if words[0] in self.aliases:
            words[0] = self.aliases[words[0]]
            command = " ".join(words)
        
        # Handle movement commands
        if words[0] in ["north", "south", "east", "west", "up", "down", "in", "out"]:
            return self.handle_movement(words[0])
        
        # Handle basic commands
        elif words[0] == "look" or words[0] == "l":
            return self.handle_look()
        
        elif words[0] == "examine" or words[0] == "x":
            return self.handle_examine(words[1:])
        
        elif words[0] == "take" or words[0] == "get":
            return self.handle_take(words[1:])
        
        elif words[0] == "inventory" or words[0] == "i" or words[0] == "inv":
            return self.handle_inventory()
        
        elif words[0] == "wear":
            return self.handle_wear(words[1:])
        
        elif words[0] == "remove":
            return self.handle_remove(words[1:])
        
        elif words[0] == "scan":
            return self.handle_scan()
        
        elif words[0] == "read":
            return self.handle_read(words[1:])
        
        elif words[0] == "use":
            return self.handle_use(words[1:])
        
        elif words[0] == "repair":
            return self.handle_repair(words[1:])
        
        elif words[0] == "install":
            return self.handle_install(words[1:])
        
        elif words[0] == "throw":
            return self.handle_throw(words[1:])
        
        elif words[0] == "hide":
            return self.handle_hide(words[1:])
        
        elif words[0] == "crawl":
            return self.handle_crawl(words[1:])
        
        elif words[0] == "run":
            return self.handle_run()
        
        elif words[0] == "wait":
            return self.handle_wait()
        
        elif words[0] == "listen":
            return self.handle_listen()
        
        elif words[0] == "map":
            return self.handle_map()
        
        elif words[0] == "help":
            return self.handle_help()
        
        elif words[0] == "quit" or words[0] == "exit":
            return self.handle_quit()
        
        elif words[0] == "restart":
            return self.handle_restart()
        
        else:
            return f"I don't understand '{command}'. Type 'help' for commands."
    
    def handle_movement(self, direction: str) -> str:
        current_room = self.game_state.rooms[self.game_state.current_room_id]
        
        if direction in current_room.exits:
            new_room_id = current_room.exits[direction]
            
            # Check if moving to outside room without suit
            if new_room_id in ["surface", "landing_gear", "ridge", "cave_mouth", "signal_cave", "black_pool"]:
                if not self.player.is_wearing_suit():
                    self.player.outside_exposure_turns += 1
                    if self.player.outside_exposure_turns >= 2:
                        return self.handle_toxic_death()
                    else:
                        return "You are not wearing a suit. The air burns immediately."
                
            # Move player
            self.game_state.current_room_id = new_room_id
            self.player.last_room_id = current_room.id
            self.player.stayed_turns_in_room = 0
            
            # Update room visited status
            current_room.visited = True
            
            # Add sound cost (walking)
            self.game_state.sound_level = "quiet"
            self.game_state.last_action_sound = 1
            
            return f"Moved {direction}."
        else:
            return f"No exit {direction}."
    
    def handle_look(self) -> str:
        # Look command doesn't advance time
        current_room = self.game_state.rooms[self.game_state.current_room_id]
        return f"{current_room.name}\n{current_room.description}"
    
    def handle_examine(self, words: List[str]) -> str:
        if not words:
            return "Examine what?"
        
        item_name = " ".join(words)
        current_room = self.game_state.rooms[self.game_state.current_room_id]
        
        # Check room items
        for item in current_room.items:
            if item.matches_name(item_name):
                return item.description
        
        # Check inventory
        for item in self.player.inventory:
            if item.matches_name(item_name):
                return item.description
        
        # Check worn items
        for item in self.player.worn_items:
            if item.matches_name(item_name):
                return item.description
        
        return f"You see no {item_name} here."
    
    def handle_take(self, words: List[str]) -> str:
        if not words:
            return "Take what?"
        
        item_name = " ".join(words)
        current_room = self.game_state.rooms[self.game_state.current_room_id]
        
        # Find item in room
        for item in current_room.items:
            if item.matches_name(item_name):
                if not item.portable:
                    return f"You can't take {item.name}."
                
                # Move item to inventory
                current_room.remove_item(item)
                self.player.add_to_inventory(item)
                
                # Add sound cost (taking)
                self.game_state.sound_level = "quiet"
                self.game_state.last_action_sound = 1
                
                return f"Taken."
        
        return f"You see no {item_name} here."
    
    def handle_inventory(self) -> str:
        if not self.player.inventory and not self.player.worn_items:
            return "You carry nothing."
        
        items = []
        for item in self.player.inventory:
            items.append(item.name)
        
        for item in self.player.worn_items:
            items.append(f"{item.name}, worn")
        
        return f"You carry:\n- {', '.join(items)}"
    
    def handle_wear(self, words: List[str]) -> str:
        if not words:
            return "Wear what?"
        
        item_name = " ".join(words)
        current_room = self.game_state.rooms[self.game_state.current_room_id]
        
        # Find item in room or inventory
        item = None
        for i in current_room.items:
            if i.matches_name(item_name):
                item = i
                break
        
        if not item:
            for i in self.player.inventory:
                if i.matches_name(item_name):
                    item = i
                    break
        
        if not item:
            return f"You don't have {item_name}."
        
        if not item.wearable:
            return f"You can't wear {item.name}."
        
        # Remove from inventory and add to worn items
        if item in self.player.inventory:
            self.player.remove_from_inventory(item)
        
        self.player.worn_items.append(item)
        self.player.suit_worn = True
        
        # Add sound cost (wearing suit)
        self.game_state.sound_level = "audible"
        self.game_state.last_action_sound = 2
        
        return f"You put on the {item.name}."
    
    def handle_remove(self, words: List[str]) -> str:
        if not words:
            return "Remove what?"
        
        item_name = " ".join(words)
        
        # Find item in worn items
        for item in self.player.worn_items:
            if item.matches_name(item_name):
                self.player.worn_items.remove(item)
                self.player.inventory.append(item)
                self.player.suit_worn = False
                
                # Add sound cost (removing suit)
                self.game_state.sound_level = "quiet"
                self.game_state.last_action_sound = 1
                
                return f"You remove the {item.name}."
        
        return f"You're not wearing {item_name}."
    
    def handle_scan(self) -> str:
        # Check if player has terminal
        if not self.player.has_terminal:
            return "You don't have a scanner."
        
        # Add sound cost (scanning)
        self.game_state.sound_level = "quiet"
        self.game_state.last_action_sound = 1
        
        # Check monster phase
        if not self.game_state.monster.active:
            return "No internal motion detected."
        
        # For now, just return a generic scan result
        return "MOTION: west\nDISTANCE: 5+ moves\nSIGNAL: intermittent"
    
    def handle_read(self, words: List[str]) -> str:
        if not words:
            return "Read what?"
        
        item_name = " ".join(words)
        current_room = self.game_state.rooms[self.game_state.current_room_id]
        
        # Check room items
        for item in current_room.items:
            if item.matches_name(item_name) and item.readable_text:
                return item.readable_text
        
        # Check inventory
        for item in self.player.inventory:
            if item.matches_name(item_name) and item.readable_text:
                return item.readable_text
        
        return f"You can't read {item_name}."
    
    def handle_use(self, words: List[str]) -> str:
        if not words:
            return "Use what?"
        
        item_name = " ".join(words)
        
        # Check inventory
        for item in self.player.inventory:
            if item.matches_name(item_name):
                if item.use_effect:
                    return item.use_effect
                else:
                    return f"You can't use {item.name} like that."
        
        return f"You don't have {item_name}."
    
    def handle_repair(self, words: List[str]) -> str:
        if not words:
            return "Repair what?"
        
        target = " ".join(words)
        
        # Check if we're in communications room
        if self.game_state.current_room_id != "communications":
            return "You can only repair the transmitter here."
        
        # Check if all parts are collected
        if (self.player.has_power_coupler and 
            self.player.has_signal_relay and 
            self.player.has_antenna_key):
            
            # Add sound cost (repairing)
            self.game_state.sound_level = "loud"
            self.game_state.last_action_sound = 3
            
            self.player.transmitter_repaired = True
            self.game_state.win_state = True
            return "TRANSMISSION READY.\nMessage?"
        else:
            return "You need all parts to repair the transmitter."
    
    def handle_install(self, words: List[str]) -> str:
        if not words:
            return "Install what?"
        
        item_name = " ".join(words)
        
        # Check if we're in communications room
        if self.game_state.current_room_id != "communications":
            return "You can only install parts here."
        
        # Find the item
        item = None
        for i in self.player.inventory:
            if i.matches_name(item_name):
                item = i
                break
        
        if not item:
            return f"You don't have {item_name}."
        
        # Check if it's a required part
        if item.name == "power coupler":
            self.player.has_power_coupler = True
            self.player.remove_from_inventory(item)
            return "Power coupler installed."
        elif item.name == "signal relay":
            self.player.has_signal_relay = True
            self.player.remove_from_inventory(item)
            return "Signal relay installed."
        elif item.name == "antenna key":
            self.player.has_antenna_key = True
            self.player.remove_from_inventory(item)
            return "Antenna key installed."
        else:
            return f"You can't install {item.name} here."
    
    def handle_throw(self, words: List[str]) -> str:
        if not words:
            return "Throw what?"
        
        item_name = " ".join(words)
        
        # Check inventory
        for item in self.player.inventory:
            if item.matches_name(item_name):
                self.player.remove_from_inventory(item)
                
                # Add sound cost (throwing)
                self.game_state.sound_level = "loud"
                self.game_state.last_action_sound = 3
                
                return f"You throw the {item.name}."
        
        return f"You don't have {item_name}."
    
    def handle_hide(self, words: List[str]) -> str:
        # For now, just return a generic response
        return "You hide."
    
    def handle_crawl(self, words: List[str]) -> str:
        if not words:
            return "Crawl where?"
        
        direction = words[0]
        current_room = self.game_state.rooms[self.game_state.current_room_id]
        
        if direction in current_room.exits:
            new_room_id = current_room.exits[direction]
            
            # Move player
            self.game_state.current_room_id = new_room_id
            self.player.last_room_id = current_room.id
            self.player.stayed_turns_in_room = 0
            
            # Add sound cost (crawling)
            self.game_state.sound_level = "quiet"
            self.game_state.last_action_sound = 1
            
            return f"You crawl {direction}."
        else:
            return f"No exit {direction}."
    
    def handle_run(self) -> str:
        # Add sound cost (running)
        self.game_state.sound_level = "loud"
        self.game_state.last_action_sound = 3
        
        return "You run."
    
    def handle_wait(self) -> str:
        # Add sound cost (waiting)
        self.game_state.sound_level = "silent"
        self.game_state.last_action_sound = 0
        
        return "You wait."
    
    def handle_listen(self) -> str:
        return "You listen."
    
    def handle_map(self) -> str:
        # Return a simple map of visited rooms
        visited_rooms = [room.name for room in self.game_state.rooms.values() if room.visited]
        if not visited_rooms:
            return "No rooms visited yet."
        
        return f"Known rooms:\n- {chr(10) + '- '.join(visited_rooms)}"
    
    def handle_help(self) -> str:
        return "Common commands:\n  north/south/east/west, in/out, up/down\n  look, examine <thing>, take <thing>\n  inventory, wear <thing>, use <thing>\n  scan, listen, hide, crawl <direction>\n  repair <thing>, read <thing>\n  map, help, quit"
    
    def handle_quit(self) -> str:
        return "Goodbye!"
    
    def handle_restart(self) -> str:
        return "Restarting game..."
    
    def handle_toxic_death(self) -> str:
        # Handle toxic air death
        return "You make it four steps.\nThat is all."
