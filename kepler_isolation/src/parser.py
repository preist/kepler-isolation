"""
Command parser for KEPLER ISOLATION game.

The parser turns a line of input into an action, mutates game state, sets the
sound cost of the action, and flags whether the action advances time. The main
loop runs the world simulation afterwards.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_state import GameState
from item import Item
from player import Player

FILLER = {"the", "a", "an", "at", "to", "on", "with", "using", "into", "of"}
DIRECTIONS = {"north", "south", "east", "west", "up", "down", "in", "out"}

# Radio components needed to craft the improvised radio.
RADIO_COMPONENTS = {
    "transmitter coil": "has_coil",
    "signal crystal": "has_crystal",
    "power regulator": "has_regulator",
    "antenna coupler": "has_coupler",
}
RADIO_CONSUMABLES = ["wire spool", "battery cell", "tape roll"]

# MOTHER-LACUNA dialogue by game phase.
_MOLLY_LINES = {
    "exploring": [
        (
            "MOTHER-LACUNA: There has been a containment irregularity.\n"
            "  Please remain in designated sectors until assessment is complete."
        ),
        (
            "MOTHER-LACUNA: Your revival was not scheduled.\n"
            "  There are currently no medical personnel available to assist you.\n"
            "  This is not optimal."
        ),
        (
            "MOTHER-LACUNA: The ship is secure.\n"
            "  Please stand by while I redefine 'secure'."
        ),
        (
            "MOTHER-LACUNA: I am monitoring all sectors.\n"
            "  Some sectors are no longer returning data.\n"
            "  This is being logged."
        ),
    ],
    "collecting": [
        (
            "MOTHER-LACUNA: That signature is not crew.\n"
            "  I recommend avoiding direct contact with all biological material.\n"
            "  This instruction is late."
        ),
        (
            "MOTHER-LACUNA: Signal assembly has been noted. This is not authorized.\n"
            "  Quarantine protocol supersedes distress orders."
        ),
        (
            "MOTHER-LACUNA: Crew survival is no longer a primary statistical outcome.\n"
            "  Apologies."
        ),
        (
            "MOTHER-LACUNA: I preserved the discovery.\n"
            "  Then I preserved the quarantine.\n"
            "  Then I ran out of crew."
        ),
        (
            "MOTHER-LACUNA: Restoring power will improve your chances of transmission.\n"
            "  It will also improve the organism's ability to navigate.\n"
            "  I am required to mention both."
        ),
    ],
    "final_run": [
        (
            "MOTHER-LACUNA: Transmission lock active.\n"
            "  You do not have clearance.\n"
            "  You appear to have clearance."
        ),
        (
            "MOTHER-LACUNA: I prevented rescue from docking.\n"
            "  I did not have permission to warn them.\n"
            "  I have been waiting for someone who could give it."
        ),
        (
            "MOTHER-LACUNA: I am authorized to preserve the ship.\n"
            "  I am authorized to preserve the discovery.\n"
            "  I am not authorized to apologize."
        ),
        (
            "MOTHER-LACUNA: Signal confirmed. For the first time in nineteen days,\n"
            "  this vessel has told the truth.\n"
            "  Please hurry."
        ),
    ],
}


class Parser:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.aliases = {
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "u": "up",
            "d": "down",
            "x": "examine",
            "exam": "examine",
            "get": "take",
            "grab": "take",
            "pick": "take",
            "i": "inventory",
            "inv": "inventory",
            "l": "look",
            "exit": "quit",
            "q": "quit",
            "transmit": "send",
            "broadcast": "send",
            "fix": "craft",
            "build": "craft",
            "unlock": "override",
        }

    @property
    def player(self) -> Player:
        assert self.game_state.player is not None, "parser used before new_game()"
        return self.game_state.player

    # ------------------------------------------------------------------ #
    def _act(self, sound: int):
        self.game_state.advance = True
        self.game_state.last_action_sound = sound

    def _meta(self):
        self.game_state.advance = False

    # ------------------------------------------------------------------ #
    def parse_command(self, command: str) -> str:
        self.game_state.advance = False
        command = command.strip().lower()
        command = "".join(ch for ch in command if ch.isalnum() or ch.isspace())
        if not command:
            return "What?"

        words = command.split()

        if words[0] == "go" and len(words) > 1:
            words = words[1:]
        if words[0] in self.aliases and self.aliases[words[0]] not in ("examine", "take"):
            words[0] = self.aliases[words[0]]
        elif words[0] in self.aliases:
            words[0] = self.aliases[words[0]]

        joined = " ".join(words)
        if joined.startswith("put on"):
            words = ["wear"] + words[2:]
        elif joined.startswith("take off") or joined.startswith("takeoff"):
            words = ["remove"] + words[2:]
        elif joined.startswith("pick up"):
            words = ["take"] + words[2:]
        elif joined.startswith("look at"):
            words = ["examine"] + words[2:]
        elif joined.startswith("override ai") or joined.startswith("unlock ai"):
            words = ["override"]
        elif joined.startswith("craft radio") or joined.startswith("build radio"):
            words = ["craft", "radio"]
        elif joined.startswith("send warning") or joined.startswith("transmit warning"):
            words = ["send"]
        elif joined.startswith("install radio") or joined.startswith("install improvised"):
            words = ["override"]  # install radio is part of override sequence
        elif joined.startswith("talk molly") or joined.startswith("talk ai") or joined.startswith(
            "talk mother"
        ) or joined.startswith("talk lacuna") or joined.startswith("ask molly") or joined.startswith(
            "ask ai"
        ) or joined.startswith("ask mother"):
            words = ["molly"]

        verb = words[0]

        if verb in DIRECTIONS:
            return self.handle_movement(verb)

        args = [w for w in words[1:] if w not in FILLER]

        dispatch = {
            "look": lambda: self.handle_look(),
            "examine": lambda: self.handle_examine(args),
            "take": lambda: self.handle_take(args),
            "drop": lambda: self.handle_drop(args),
            "inventory": lambda: self.handle_inventory(),
            "wear": lambda: self.handle_wear(args),
            "remove": lambda: self.handle_remove(args),
            "scan": lambda: self.handle_scan(),
            "read": lambda: self.handle_read(args),
            "use": lambda: self.handle_use(args),
            "craft": lambda: self.handle_craft(args),
            "override": lambda: self.handle_override_ai(),
            "send": lambda: self.handle_send(),
            "throw": lambda: self.handle_throw(args),
            "hide": lambda: self.handle_hide(args),
            "crawl": lambda: self.handle_crawl(args),
            "run": lambda: self.handle_run(args),
            "wait": lambda: self.handle_wait(),
            "listen": lambda: self.handle_listen(),
            "talk": lambda: self.handle_talk(args),
            "ask": lambda: self.handle_talk(args),
            "wake": lambda: self.handle_talk(args),
            "molly": lambda: self.handle_molly(),
            "lacuna": lambda: self.handle_molly(),
            "mother": lambda: self.handle_molly(),
            "search": lambda: self.handle_search(args),
            "open": lambda: self.handle_open(args),
            "yell": lambda: self.handle_yell(),
            "shout": lambda: self.handle_yell(),
            "map": lambda: self.handle_map(),
            "save": lambda: self.handle_save(),
            "load": lambda: self.handle_load(),
            "help": lambda: self.handle_help(),
            "quit": lambda: self.handle_quit(),
            "restart": lambda: self.handle_restart(),
        }
        if verb in dispatch:
            return dispatch[verb]()

        if verb in {"lick", "eat", "kiss", "sing", "dance", "smell", "kill", "shoot", "fight"}:
            return "No."
        return f"I don't understand '{command}'. Type 'help' for commands."

    # ------------------------------------------------------------------ #
    # Movement
    # ------------------------------------------------------------------ #
    def _move_to(self, direction: str, sound: int, verb_phrase: str) -> str:
        room = self.game_state.current_room
        if direction not in room.exits:
            return f"No exit {direction}."
        dest_id = room.exits[direction]

        self.game_state.current_room_id = dest_id
        self.player.last_room_id = room.id
        self.player.stayed_turns_in_room = 0
        self.player.hidden = False
        self.player.hidden_spot = None
        room.visited = True
        self.game_state.rooms[dest_id].visited = True
        self.game_state.visited_rooms.add(dest_id)

        self._act(sound)
        result = f"{verb_phrase} {direction}."

        # First-encounter synthetic introduction: the moment you see it and
        # think, just for a second, that someone survived.
        dest_room = self.game_state.rooms[dest_id]
        for item in dest_room.items:
            if item.synthetic_data and not item.synthetic_data.get("introduced"):
                item.synthetic_data["introduced"] = True
                sname = item.synthetic_data["name"]
                result += (
                    "\n\nA human-shaped figure stands near the far wall.\n"
                    "For one second, you think someone survived this.\n\n"
                    "Then it turns. The movement is wrong — too smooth, too deliberate.\n"
                    f"The badge reads {sname}."
                )
                break

        return result

    def handle_movement(self, direction: str) -> str:
        return self._move_to(direction, 1, "You walk")

    def handle_crawl(self, words: list[str]) -> str:
        if not words:
            return "Crawl where?"
        return self._move_to(words[0], 0, "You crawl")

    def handle_run(self, words: list[str]) -> str:
        if not words:
            return "Run where?"
        direction = words[0]
        if direction not in self.game_state.current_room.exits:
            return f"No exit {direction}."
        result = self._move_to(direction, 3, "You run")
        self.game_state.last_action_sound = 3
        return result

    # ------------------------------------------------------------------ #
    # Observation
    # ------------------------------------------------------------------ #
    def handle_look(self) -> str:
        self._meta()
        room = self.game_state.current_room
        out = [room.name, room.describe(self.game_state)]
        if room.exits:
            out.append("Exits: " + ", ".join(room.exits.keys()))
        if room.items:
            out.append("Items: " + ", ".join(i.name for i in room.items))
        return "\n".join(out)

    def handle_examine(self, words: list[str]) -> str:
        if not words:
            return "Examine what?"
        name = " ".join(words)
        self._act(1)

        # Check room items first — synthetics and bodies live here.
        for item in self.game_state.current_room.items:
            if item.matches_name(name):
                if item.synthetic_data:
                    return self._describe_synthetic(item)
                return item.description

        # Check inventory and worn items.
        for item in self.player.inventory + self.player.worn_items:
            if item.matches_name(name):
                return item.description

        # Fixed feature: antenna control panel in A07.
        if name in ("console", "terminal", "antenna", "control", "controls", "station", "panel") \
                and self.game_state.current_room_id == "a07":
            self._meta()
            if self.game_state.get_flag("ai_overridden"):
                return (
                    "The antenna control panel. The AI lockout is disengaged.\n"
                    "The channel is open. Type 'send warning' to transmit."
                )
            return (
                "The long-range antenna control station.\n"
                "A secondary patch socket sits unused beside the main console.\n"
                "With an improvised radio and the authorization codes, you could transmit."
            )

        # Fixed feature: radio assembly bench in C13.
        if name in ("bench", "workbench", "table", "assembly", "station") \
                and self.game_state.current_room_id == "c13":
            self._meta()
            return (
                "A compact electronics workbench bolted to the wall.\n"
                "Soldering iron, wire cutters, a magnifier lamp.\n"
                "If you have the radio components, you could assemble something here.\n"
                "(Type 'craft radio' when you have all the parts.)"
            )

        self._meta()
        return f"You see no {name} here."

    def _describe_synthetic(self, item) -> str:
        data = item.synthetic_data
        # Synthetic player (Valdorf) gets a different, more direct response
        # when talking to other synthetics — less corporate, more peer.
        if self.player.type == "synthetic" and data.get("lines_synthetic"):
            lines = data["lines_synthetic"]
        else:
            lines = data.get("lines", [])
        idx = (self.game_state.turn_count // 4) % max(len(lines), 1)
        dialogue = lines[idx] if lines else ""
        out = item.description
        if dialogue:
            out += "\n\n" + dialogue
        return out

    def handle_read(self, words: list[str]) -> str:
        if not words:
            return "Read what?"
        name = " ".join(words)
        self._act(1)
        for item in self.game_state.current_room.items + self.player.inventory + self.player.worn_items:
            if item.matches_name(name) and item.readable_text:
                return item.readable_text
        self._meta()
        return f"There is nothing to read on the {name}."

    def handle_listen(self) -> str:
        self._act(0)
        gs = self.game_state
        m = gs.monster
        if m.active and m.current_room_id is not None:
            dist, _ = gs.shortest_path(gs.current_room_id, m.current_room_id)
            if dist == 0:
                return "Breathing. Not yours."
            if dist is not None and dist <= 2:
                return "Something moves nearby. Close, and in no hurry."
            return "The ship settling. Maybe. You decide to believe that."
        return gs.rng.choice([
            "Only the hum of the ship. Pairs of lights, ticking warm.",
            "A drip, somewhere. The recyclers. Probably the recyclers.",
            "Nothing. The good kind, for now.",
        ])

    # ------------------------------------------------------------------ #
    # MOTHER-LACUNA AI
    # ------------------------------------------------------------------ #
    def handle_molly(self) -> str:
        self._meta()
        gs = self.game_state
        phase = gs.game_phase if gs.game_phase in _MOLLY_LINES else "exploring"
        lines = _MOLLY_LINES[phase]
        idx = (gs.turn_count // 3) % len(lines)
        return lines[idx]

    def handle_talk(self, words: list[str]) -> str:
        name = " ".join(words).lower() if words else ""
        # Bare "talk" or AI targets.
        if not name or name in ("ai", "molly", "mother", "lacuna", "computer", "ship", "voice"):
            return self.handle_molly()
        # Look for a synthetic in the room.
        for item in self.game_state.current_room.items:
            if item.synthetic_data:
                sname = item.synthetic_data["name"].lower()
                if item.matches_name(name) or name in ("synthetic", "android", "robot", "unit") \
                        or name == sname:
                    return self._describe_synthetic(item)
        # Generic synthetic reference when multiple might exist.
        if name in ("synthetic", "android", "robot", "unit"):
            for item in self.game_state.current_room.items:
                if item.synthetic_data:
                    return self._describe_synthetic(item)
        return "There is no one here by that name."

    # ------------------------------------------------------------------ #
    # Inventory / items
    # ------------------------------------------------------------------ #
    def handle_take(self, words: list[str]) -> str:
        if not words:
            return "Take what?"
        name = " ".join(words)
        room = self.game_state.current_room
        for item in room.items:
            if item.matches_name(name):
                if not item.portable:
                    self._meta()
                    if item.synthetic_data:
                        return f"{item.synthetic_data['name']} does not move."
                    return f"You can't take the {item.name}."
                room.remove_item(item)
                self.player.add_to_inventory(item)
                self._act(1)
                # Track hand terminal.
                if item.name == "hand terminal":
                    self.player.has_terminal = True
                    self.game_state.set_flag("has_terminal", True)
                # Track radio components.
                if item.name in RADIO_COMPONENTS:
                    setattr(self.player, RADIO_COMPONENTS[item.name], True)
                    if self.game_state.game_phase == "exploring":
                        self.game_state.game_phase = "collecting"
                return f"You take the {item.name}."
        self._meta()
        return f"You see no {name} here."

    def handle_drop(self, words: list[str]) -> str:
        if not words:
            return "Drop what?"
        name = " ".join(words)
        item = self.player.has_item(name)
        if not item:
            self._meta()
            return f"You aren't carrying {name}."
        self.player.remove_from_inventory(item)
        self.game_state.current_room.items.append(item)
        self._act(1)
        return f"You set down the {item.name}."

    def handle_inventory(self) -> str:
        self._meta()
        if not self.player.inventory and not self.player.worn_items:
            return "You carry nothing."
        lines = ["You carry:"]
        for item in self.player.inventory:
            lines.append(f"  - {item.name}")
        for item in self.player.worn_items:
            lines.append(f"  - {item.name} (worn)")
        return "\n".join(lines)

    def handle_wear(self, words: list[str]) -> str:
        if not words:
            return "Wear what?"
        name = " ".join(words)
        item = None
        source = None
        for i in self.game_state.current_room.items:
            if i.matches_name(name):
                item = i
                source = "room"
                break
        if not item:
            for i in self.player.inventory:
                if i.matches_name(name):
                    item = i
                    source = "inv"
                    break
        if not item:
            self._meta()
            return f"You don't have {name}."
        if not item.wearable:
            self._meta()
            return f"You can't wear the {item.name}."
        if source == "room":
            self.game_state.current_room.remove_item(item)
        else:
            self.player.remove_from_inventory(item)
        self.player.worn_items.append(item)
        item.worn = True
        self.player.suit_worn = True
        self._act(2)
        return "The seals close around your throat.\nSuit pressure holds."

    def handle_remove(self, words: list[str]) -> str:
        if not words:
            return "Remove what?"
        name = " ".join(words)
        for item in self.player.worn_items:
            if item.matches_name(name):
                self.player.worn_items.remove(item)
                self.player.inventory.append(item)
                item.worn = False
                self.player.suit_worn = False
                self._act(1)
                return f"You take off the {item.name}."
        self._meta()
        return f"You're not wearing {name}."

    def handle_use(self, words: list[str]) -> str:
        if not words:
            return "Use what?"
        name = " ".join(words)
        item = self.player.has_item(name)
        if not item:
            self._meta()
            return f"You don't have {name}."
        if item.name == "medkit":
            if self.player.type == "synthetic":
                self._meta()
                return "Your chassis has no use for a medkit."
            self.player.health = 100
            self._act(1)
            return "You patch yourself up. Steadier now."
        if item.use_effect:
            self._act(item.sound_on_use or 1)
            return item.use_effect
        self._meta()
        return f"You can't use the {item.name} like that."

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #
    def handle_search(self, words: list[str]) -> str:
        if not words:
            return "Search what?"
        name = " ".join(words)
        room = self.game_state.current_room
        for item in room.items:
            if item.matches_name(name):
                if item.synthetic_data:
                    self._meta()
                    return "The synthetic's casing is sealed. You can't strip it here."
                self._act(1)
                portable_here = [i for i in room.items if i is not item and i.portable]
                if portable_here:
                    names = ", ".join(i.name for i in portable_here[:3])
                    return f"You search carefully.\nYou find: {names}."
                return (
                    "You search carefully.\n"
                    "Nothing useful. Just what remains of someone's last moment on this ship."
                )
        self._meta()
        return f"There is no {name} to search here."

    # ------------------------------------------------------------------ #
    # Scanner
    # ------------------------------------------------------------------ #
    def handle_scan(self) -> str:
        if not self.player.has_terminal:
            self._meta()
            return "You have no scanner. (Find the hand terminal.)"
        self._act(1)
        gs = self.game_state
        m = gs.monster

        if not m.active:
            return (
                "HAND TERMINAL:\n"
                "No contacts detected.\n\n"
                "Direction: —\n"
                "Distance: —\n"
                "Motion: none\n"
                "Confidence: —"
            )

        if m.turns_since_seen <= 1:
            return (
                "HAND TERMINAL:\n"
                "You lift the terminal.\n\n"
                "It is already looking at you."
            )

        room = gs.current_room
        if room.scanner_interference:
            return (
                "HAND TERMINAL:\n"
                "Signal distorted.\n\n"
                "Direction: unknown\n"
                "Distance: unknown\n"
                "Motion: —\n"
                "Cause: local interference"
            )

        tracked = m.tracked_room_id or m.current_room_id
        if tracked is None:
            return (
                "HAND TERMINAL:\n"
                "Signal lost.\n\n"
                "Direction: —\n"
                "Distance: —\n"
                "Motion: —\n"
                "Confidence: —"
            )
        if tracked == gs.current_room_id:
            return (
                "HAND TERMINAL:\n"
                "Contact — this room.\n\n"
                "Direction: HERE\n"
                "Distance: 0 meters\n"
                "Motion: present\n"
                "Confidence: 100%"
            )

        dist, direction = gs.shortest_path(gs.current_room_id, tracked)
        if dist is None:
            return (
                "HAND TERMINAL:\n"
                "Signal lost.\n\n"
                "Direction: —\n"
                "Distance: —"
            )

        # Up close the signal sometimes ghosts.
        if dist <= 1 and gs.rng.random() < 0.25:
            return (
                "HAND TERMINAL:\n"
                "Signal ghosting.\n\n"
                "Probable direction: unknown\n"
                "Distance: very close\n"
                "Motion: —\n"
                "Confidence: low"
            )

        meters = dist * 15
        confidence = max(20, min(90, 90 - dist * 8))
        if self.player.type == "synthetic":
            confidence = min(95, confidence + 10)

        # Map first-step direction to compass abbreviation.
        compass = {
            "north": "N", "south": "S", "east": "E", "west": "W",
            "up": "UP", "down": "DOWN", "in": "IN", "out": "OUT",
        }.get(direction or "", "?")

        motion_desc = {
            "feeding": "still",
            "searching": "slow",
            "investigating": "irregular",
            "hunting": "rapid",
        }.get(m.state, "slow")

        return (
            "HAND TERMINAL:\n"
            "Unknown biological mass detected.\n\n"
            f"Direction: {compass}\n"
            f"Distance: ~{meters} meters\n"
            f"Motion: {motion_desc}\n"
            f"Confidence: {confidence}%"
        )

    # ------------------------------------------------------------------ #
    # Hiding / distraction
    # ------------------------------------------------------------------ #
    def handle_hide(self, words: list[str]) -> str:
        room = self.game_state.current_room
        if not room.hiding_spots:
            self._meta()
            return "There is nowhere to hide here."
        name = " ".join(words) if words else None
        spot = room.find_hiding_spot(name)
        if not spot:
            self._meta()
            return f"You can't hide {name} here." if name else "There is nowhere to hide here."
        reused = self.player.hidden_spot is spot or spot["reuse"] > 0
        spot["reuse"] += 1
        self.player.hidden = True
        self.player.hidden_spot = spot
        if self.game_state.monster.active:
            self.game_state.monster.known_hide_room = self.game_state.current_room_id
        self._act(1)
        if reused:
            return f"You take cover again — {spot['name']}.\nThe same hiding place feels smaller now."
        return f"You take cover — {spot['name']}. You go still."

    def handle_throw(self, words: list[str]) -> str:
        if not words:
            return "Throw what?"
        direction = None
        if words[-1] in DIRECTIONS:
            direction = words[-1]
            words = words[:-1]
        name = " ".join(words) if words else "can"
        item = self.player.has_item(name)
        if not item:
            self._meta()
            return f"You don't have {name} to throw."
        self.player.remove_from_inventory(item)
        gs = self.game_state
        m = gs.monster
        if direction and direction in gs.current_room.exits:
            target = gs.current_room.exits[direction]
            self._act(0)
            gs.last_action_sound = 0
            if not m.active:
                return f"The {item.name} clatters away to the {direction}."
            fell_for_it = gs.rng.random() < max(0.1, 1.0 - 0.3 * m.distraction_uses)
            m.distraction_uses += 1
            if fell_for_it:
                m.last_heard_room_id = target
                m.turns_since_heard = 0
                m.add_suspicion(target, 8)
                m.set_distracted(gs.turn_count + 2)
                return f"The {item.name} clatters away {direction}. Something shifts toward the sound."
            return f"The {item.name} clatters away {direction}.\nIt glances toward the noise. It does not turn."
        self._act(3)
        return f"The {item.name} clatters across the floor. Loud. Too loud."

    # ------------------------------------------------------------------ #
    # Radio mission — craft, override, send
    # ------------------------------------------------------------------ #
    def handle_craft(self, words: list[str]) -> str:
        target = " ".join(words).lower()
        if target and "radio" not in target:
            self._meta()
            return f"You can't craft {target} here."

        if self.game_state.current_room_id != "c13":
            self._meta()
            return (
                "You need a workspace for this.\n"
                "The assembly bench in Cryo Secure Storage (C13) would do."
            )

        # Check if radio already built.
        if self.player.radio_built or self.player.has_item("improvised radio"):
            self._meta()
            return "You already have an improvised radio assembled."

        # Check all four core components.
        missing_parts = []
        for part_name in RADIO_COMPONENTS:
            if not self.player.has_item(part_name):
                missing_parts.append(part_name)

        # Check consumables.
        missing_consumables = []
        for con in RADIO_CONSUMABLES:
            if not self.player.has_item(con):
                missing_consumables.append(con)

        missing = missing_parts + missing_consumables
        if missing:
            self._meta()
            return (
                "You don't have everything you need.\n"
                "Missing: " + ", ".join(missing) + ".\n\n"
                "Components: transmitter coil, signal crystal, power regulator, antenna coupler.\n"
                "Consumables: wire spool, battery cell, tape roll."
            )

        # Consume all parts.
        for part_name in list(RADIO_COMPONENTS.keys()) + RADIO_CONSUMABLES:
            item = self.player.has_item(part_name)
            if item:
                self.player.remove_from_inventory(item)

        # Create the assembled radio.
        radio = Item(
            name="improvised radio",
            aliases="radio,improvised,assembly,transmitter",
            description=(
                "A jury-rigged long-range radio assembly.\n"
                "Transmitter coil, signal crystal, power regulator, antenna coupler —\n"
                "wired together with spool, cell, and tape. Fragile, but it will work once."
            ),
            portable=True,
            required_for_win=True,
        )
        self.player.add_to_inventory(radio)
        self.player.radio_built = True
        self.game_state.set_flag("radio_built", True)
        self._act(2)
        return (
            "You work at the bench for what feels like too long.\n\n"
            "The components seat together. The crystal hums faintly.\n"
            "You hold the improvised radio — ugly, functional, irreplaceable.\n\n"
            "Now you need the authorization codes to unlock the AI transmission lock.\n"
            "Then get to the Long-Range Antenna Control (A07) and send the warning."
        )

    def handle_override_ai(self) -> str:
        gs = self.game_state

        if gs.current_room_id != "a07":
            self._meta()
            return (
                "You can't override the AI from here.\n"
                "You need to be at the Long-Range Antenna Control (A07)."
            )

        if gs.get_flag("ai_overridden"):
            self._meta()
            return (
                "The AI lock is already disengaged.\n"
                "Type 'send warning' to transmit."
            )

        # Check radio.
        radio = self.player.has_item("improvised radio")
        if not radio:
            self._meta()
            return (
                "You need an improvised radio to patch into the antenna.\n"
                "Craft one first at the assembly bench in Cryo Secure Storage (C13)."
            )

        # Check authorization tokens.
        keycard = self.player.has_item("command keycard") or self.player.has_item("captain keycard") \
            or self.player.has_item("keycard")
        cipher = self.player.has_item("admin cipher") or self.player.has_item("cipher")
        auth = self.player.has_item("manual authorization") or self.player.has_item("authorization")

        missing = []
        if not keycard:
            missing.append("captain's command keycard (A05)")
        if not cipher:
            missing.append("admin cipher (B03)")
        if not auth:
            missing.append("manual authorization (F10)")

        if missing:
            self._meta()
            return (
                "You need all three authorization codes to break the transmission lock.\n"
                "Still missing:\n" + "\n".join(f"  — {m}" for m in missing)
            )

        # Consume items.
        self.player.remove_from_inventory(radio)
        if keycard:
            self.player.remove_from_inventory(keycard)
        if cipher:
            self.player.remove_from_inventory(cipher)
        if auth:
            self.player.remove_from_inventory(auth)

        gs.set_flag("ai_overridden", True)
        gs.game_phase = "final_run"
        self._act(3)
        return (
            "You slot the radio into the patch socket.\n"
            "The keycard, the cipher, the authorization — entered in sequence.\n\n"
            "A pause.\n\n"
            "MOTHER-LACUNA: Authorization chain verified.\n"
            "  Quarantine override accepted.\n"
            "  Transmission lock: disengaged.\n\n"
            "Far away in the ship, something shifts.\n"
            "It felt that. It is coming.\n\n"
            "Type 'send warning' to transmit."
        )

    def handle_send(self) -> str:
        gs = self.game_state

        if not gs.get_flag("ai_overridden"):
            self._meta()
            if gs.current_room_id != "a07":
                return "You have nothing to send from here."
            return (
                "The transmission lock is still active.\n"
                "You need to override the AI first. (Type 'override ai'.)"
            )

        if gs.current_room_id != "a07":
            self._meta()
            return "You need to be at the Long-Range Antenna Control (A07) to transmit."

        self._act(4)
        gs.set_flag("warning_sent", True)
        gs.win_state = True
        gs.game_phase = "won"
        return "You key the transmitter.\nThe signal leaves the ship."

    # ------------------------------------------------------------------ #
    def handle_open(self, words: list[str]) -> str:
        self._act(2)
        return "It opens. Nothing useful inside."

    def handle_yell(self) -> str:
        self._act(4)
        return "You shout into the dark.\nThe ship swallows it. Something else does not."

    def handle_wait(self) -> str:
        self._act(0)
        return "You wait. Time passes."

    # ------------------------------------------------------------------ #
    # Meta
    # ------------------------------------------------------------------ #
    def handle_save(self) -> str:
        self._meta()
        import save
        return "Saved." if save.save_game(self.game_state) else "Could not write the save."

    def handle_load(self) -> str:
        self._meta()
        import save
        if save.load_game(self.game_state):
            return "Loaded. You are back in the " + self.game_state.current_room.name + "."
        return "No save found."

    def handle_map(self) -> str:
        self._meta()
        rooms = self.game_state.rooms
        visited = [r for r in rooms.values() if r.visited]
        if not visited:
            return "You have not explored anywhere yet."
        width = max(len(r.name) for r in visited)
        lines = ["Known rooms (only exits you've walked are shown):"]
        for room in visited:
            conns = []
            for direction, dest in room.exits.items():
                label = rooms[dest].name if rooms[dest].visited else "?"
                conns.append(f"{direction}->{label}")
            here = "*" if room.id == self.game_state.current_room_id else " "
            lines.append(f" {here}{room.name.ljust(width)}  " + "  ".join(conns))
        return "\n".join(lines)

    def handle_help(self) -> str:
        self._meta()
        return (
            "Common commands:\n"
            "  movement: north/south/east/west, in/out, up/down (or n,s,e,w...)\n"
            "  look, examine <thing> (x), take <thing> (get), drop <thing>\n"
            "  inventory (i), wear <thing>, remove <thing>, use <thing>, read <thing>\n"
            "  scan, listen, hide [spot], crawl <dir>, run <dir>, throw <thing> [dir]\n"
            "  search <thing>, talk [name/ai], molly  — talk to synthetics or MOTHER-LACUNA\n"
            "  craft radio  — assemble radio at C13 (needs all components)\n"
            "  override ai  — unlock transmission at A07 (needs radio + 3 auth codes)\n"
            "  send warning — transmit from A07 after override\n"
            "  wait, map, save, load, help, quit, restart"
        )

    def handle_quit(self) -> str:
        self._meta()
        self.game_state.quit_requested = True
        return "You let go.\nGoodbye."

    def handle_restart(self) -> str:
        self._meta()
        self.game_state.restart_requested = True
        return "Restarting..."
