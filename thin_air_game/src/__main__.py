#!/usr/bin/env python3
"""
THE THIN AIR - Terminal-based text adventure game
"""

import sys
from typing import Dict, List, Optional

# Game components
from .game_state import GameState
from .player import Player
from .room import Room
from .item import Item
from .monster import Monster
from .parser import Parser


class ThinAirGame:
    def __init__(self):
        self.game_state = GameState()
        self.parser = Parser(self.game_state)
        
    def start_game(self):
        print("THE THIN AIR")
        print("=" * 20)
        
        # Character creation
        self.create_character()
        
        # Initialize game
        self.initialize_game()
        
        # Start main game loop
        self.main_loop()
        
    def create_character(self):
        print("Name?")
        name = input("> ").strip()
        if not name:
            name = "Player"
            
        print("Gender?")
        gender = input("> ").strip()
        if not gender:
            gender = "neutral"
            
        print("Type?")
        print("1. Human crewmember")
        print("2. Synthetic")
        print("3. Contract specialist")
        
        type_choice = input("> ").strip()
        player_type = "human"  # default
        if type_choice == "2":
            player_type = "synthetic"
        elif type_choice == "3":
            player_type = "contract_specialist"
            
        self.game_state.player = Player(name, gender, player_type)
        print(f"\nWelcome, {name} the {player_type}.\n")
        
    def initialize_game(self):
        # Create rooms
        self.create_rooms()
        
        # Set initial room
        self.game_state.current_room_id = "cockpit"
        
        # Add items to rooms
        self.add_items_to_rooms()
        
        # Set game phase
        self.game_state.game_phase = "intro"
        
    def create_rooms(self):
        # Create all rooms based on specification
        rooms = {
            "cockpit": Room("Cockpit", "Dead stars in the glass. The console waits with one green light.", [], {}, []),
            "central_corridor": Room("Central Corridor", "Low ceiling. Handrails. Old boot marks. The lights hum in pairs.", [], {}, []),
            "airlock": Room("Airlock", "Suit locker. Outer hatch. Inner hatch. A red card says: TWO MOVES WITHOUT SEAL.", [], {}, []),
            "med_bay": Room("Med Bay", "Medical supplies. A recorder log lies on the table.", [], {}, []),
            "crew_quarters": Room("Crew Quarters", "Bunks and personal lockers.", [], {}, []),
            "galley": Room("Galley", "Loose cans. Water recycler.", [], {}, []),
            "storage": Room("Storage", "Boxes and crates. Maintenance tags.", [], {}, []),
            "engineering_access": Room("Engineering Access", "Narrow passage. A locked panel hangs open.", [], {}, []),
            "reactor_room": Room("Reactor Room", "Hot reactor controls. The hum is loud.", [], {}, []),
            "cargo_bay": Room("Cargo Bay", "Large crates. Forklift. Dark corners.", [], {}, []),
            "lower_hold": Room("Lower Hold", "Old distress beacon fragment. Scratch marks.", [], {}, []),
            "maintenance_junction": Room("Maintenance Junction", "Tool rack. Repair kit.", [], {}, []),
            "ventral_service": Room("Ventral Service", "Crawl route. Noisy fan.", [], {}, []),
            "observation": Room("Observation", "A long window. The planet presses its dark face against it.", [], {}, []),
            "comms_hall": Room("Comms Hall", "Console and wiring. Tension in the air.", [], {}, []),
            "communications": Room("Communications", "Damaged transmitter. Console and parts slots.", [], {}, [])
        }
        
        self.game_state.rooms = rooms
        
    def add_items_to_rooms(self):
        # Add items to rooms based on specification
        self.game_state.rooms["cockpit"].items = [Item("hand terminal", "scanner", "A portable scanner.", portable=True, wearable=False)]
        self.game_state.rooms["airlock"].items = [Item("EVA suit", "suit", "A full EVA suit with helmet and gloves.", portable=False, wearable=True)]
        self.game_state.rooms["storage"].items = [Item("power coupler", "coupler", "A power coupling unit.", portable=True, wearable=False)]
        self.game_state.rooms["reactor_room"].items = [Item("signal relay", "relay", "A signal transmission relay.", portable=True, wearable=False)]
        self.game_state.rooms["cargo_bay"].items = [Item("antenna key", "key", "An antenna tuning key.", portable=True, wearable=False)]
        self.game_state.rooms["med_bay"].items = [Item("recorder log", "log", "A recording of past events.", portable=True, wearable=False, readable_text="The signal was not from a distress beacon. It was from something inside the ship.")]  
        self.game_state.rooms["crew_quarters"].items = [Item("access card", "card", "An access card for restricted areas.", portable=True, wearable=False)]
        self.game_state.rooms["maintenance_junction"].items = [Item("repair kit", "kit", "A basic repair kit.", portable=True, wearable=False)]
        self.game_state.rooms["galley"].items = [Item("loose can", "can", "A loose metal can.", portable=True, wearable=False)]
        
    def main_loop(self):
        print("Type 'help' for commands.")
        print()
        
        while True:
            # Display current room
            self.display_room()
            
            # Get player input
            try:
                command = input("> ").strip().lower()
                if not command:
                    continue
                
                # Process command
                result = self.parser.parse_command(command)
                print(result)
                
                # Check for win/lose conditions
                if self.game_state.win_state:
                    print("\nTRANSMISSION SENT.")
                    print("\nFARLAND-GUTTENBER RELAY STATION")
                    print("SEVENTEEN DAYS LATER")
                    print()
                    print("\"Play it again.\"")
                    print("\"Do not come here.\"")
                    print("\"Was there contact?\"")
                    print("\"Yes.\"")
                    print("\"Hostile?\"")
                    print("\"Intelligent.\"")
                    print()
                    print("A pause.")
                    print("\"Wake Survey Team One.\"")
                    print()
                    print("LV-417c is upgraded to priority recovery.")
                    break
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
    
    def display_room(self):
        room = self.game_state.rooms[self.game_state.current_room_id]
        print(f"\n{room.name}")
        print(room.description)
        
        # Show exits
        if room.exits:
            exits = ", ".join(room.exits.keys())
            print(f"Exits: {exits}")
        
        # Show items
        if room.items:
            items = ", ".join([item.name for item in room.items])
            print(f"Items: {items}")
        else:
            print("Items: none")
        
        # Show status bar
        sound_level = self.game_state.sound_level
        suit_status = "worn" if self.game_state.player.suit_worn else "not worn"
        print(f"\nSound: {sound_level} | Suit: {suit_status}")


def main():
    game = ThinAirGame()
    game.start_game()


if __name__ == "__main__":
    main()