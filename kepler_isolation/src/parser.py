"""
Command parser for KEPLER ISOLATION game.

The parser turns a line of input into an action, mutates game state, sets the
sound cost of the action, and flags whether the action advances time. The main
loop runs the world simulation afterwards.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_state import TOXIC_ROOMS, GameState
from player import Player

# Words we can safely drop from an argument. Deliberately excludes the
# direction words (in/out/up/down) — "crawl down" and "run in" need them.
FILLER = {"the", "a", "an", "at", "to", "on", "with", "using", "into", "of"}

DIRECTIONS = {"north", "south", "east", "west", "up", "down", "in", "out"}


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
            "fix": "repair",
        }

    @property
    def player(self) -> Player:
        assert self.game_state.player is not None, "parser used before new_game()"
        return self.game_state.player

    # ------------------------------------------------------------------ #
    def _act(self, sound: int):
        """Mark the current command as time-advancing with a sound cost."""
        self.game_state.advance = True
        self.game_state.last_action_sound = sound

    def _meta(self):
        self.game_state.advance = False

    # ------------------------------------------------------------------ #
    def parse_command(self, command: str) -> str:
        self.game_state.advance = False
        command = command.strip().lower()
        # Strip punctuation (keep letters, digits, spaces).
        command = "".join(ch for ch in command if ch.isalnum() or ch.isspace())
        if not command:
            return "What?"

        words = command.split()

        # Normalization happens in layers so the parser stays forgiving:
        # drop a leading "go", expand single-word aliases, rewrite multiword
        # verb phrases ("put on" -> wear), then strip filler from the object.
        # Standalone direction or "go <dir>".
        if words[0] == "go" and len(words) > 1:
            words = words[1:]
        if words[0] in self.aliases and self.aliases[words[0]] not in ("examine", "take"):
            words[0] = self.aliases[words[0]]
        elif words[0] in self.aliases:
            words[0] = self.aliases[words[0]]

        # Multiword verb phrases.
        joined = " ".join(words)
        if joined.startswith("put on"):
            words = ["wear"] + words[2:]
        elif joined.startswith("take off") or joined.startswith("takeoff"):
            words = ["remove"] + words[2:]
        elif joined.startswith("pick up"):
            words = ["take"] + words[2:]
        elif joined.startswith("look at"):
            words = ["examine"] + words[2:]

        verb = words[0]

        if verb in DIRECTIONS:
            return self.handle_movement(verb)

        # Strip filler from the argument portion for object-taking verbs.
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
            "repair": lambda: self.handle_repair(args),
            "install": lambda: self.handle_install(args),
            "send": lambda: self.handle_send(args),
            "throw": lambda: self.handle_throw(args),
            "hide": lambda: self.handle_hide(args),
            "crawl": lambda: self.handle_crawl(args),
            "run": lambda: self.handle_run(args),
            "wait": lambda: self.handle_wait(),
            "listen": lambda: self.handle_listen(),
            "talk": lambda: self.handle_sable(),
            "wake": lambda: self.handle_sable(),
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

        # Obvious nonsense gets a curt reply; everything else gets help.
        if verb in {"lick", "eat", "kiss", "sing", "dance", "smell", "kill"}:
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

        # Flags driven by location.
        if dest_id in TOXIC_ROOMS:
            self.game_state.set_flag("went_outside", True)
        if dest_id in ("signal_cave", "black_pool"):
            self.game_state.set_flag("entered_cave", True)
        if dest_id == "signal_cave":
            self.game_state.trigger_cave()

        self._act(sound)
        return f"{verb_phrase} {direction}."

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
        if "sable" in name:
            return self.handle_sable()
        self._act(1)
        for item in self.game_state.current_room.items:
            if item.matches_name(name):
                # Examining the beacon triggers the cave event.
                if "beacon" in item.name and self.game_state.get_flag("entered_cave"):
                    self.game_state.set_flag("examined_beacon", True)
                    self.game_state.trigger_cave()
                return item.description
        for item in self.player.inventory + self.player.worn_items:
            if item.matches_name(name):
                return item.description
        # A couple of fixed features.
        if name in ("transmitter", "console") and self.game_state.current_room_id == "communications":
            self.game_state.set_flag("comms_damaged_known", True)
            return "The transmitter is dead. Three sockets gape open:\npower coupler, signal relay, antenna key."
        self._meta()
        return f"You see no {name} here."

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
        if m.active and m.phase == "aboard":
            dist, _ = gs.shortest_path(gs.current_room_id, m.current_room_id)
            if dist == 0:
                return "Breathing. Not yours."
            if dist is not None and dist <= 2:
                return "Something moves nearby. Close, and in no hurry."
            return "The ship settling. Maybe. You decide to believe that."
        if gs.current_room_id in TOXIC_ROOMS:
            return gs.rng.choice(
                [
                    "Wind over the dust. Your own breath, loud in the helmet.",
                    "The signal, under everything. Not a voice. Almost a voice.",
                ]
            )
        if gs.get_flag("cave_triggered"):
            return gs.rng.choice(
                [
                    "The hum of the ship. And under it, something you can't place.",
                    "Quiet. The kind that arrives after a sound, not before one.",
                ]
            )
        return gs.rng.choice(
            [
                "Only the hum of the ship. Pairs of lights, ticking warm.",
                "A drip, somewhere. The recyclers. Probably the recyclers.",
                "Nothing. The good kind, for now.",
            ]
        )

    def handle_sable(self) -> str:
        gs = self.game_state
        if gs.get_flag("sable_sacrifice_used") and not gs.get_flag("sable_alive"):
            self._meta()
            return "Sable is gone. The hatch it closed stays closed."
        if gs.get_flag("sable_following"):
            self._meta()
            return 'Sable keeps pace at your shoulder. "Keep moving," it says.'
        if gs.current_room_id != "crew_quarters":
            self._meta()
            return "There is no one here by that name."
        # Wake it: one sparse hint, then it falls in behind you.
        gs.set_flag("sable_awake", True)
        gs.set_flag("sable_alive", True)
        gs.set_flag("sable_following", True)
        self._act(1)
        return (
            'The synthetic\'s eyes find you. "Sable. I came down with the last crew."\n'
            '"I watched it learn the doors. Then the names. Stay quiet. Keep moving."\n'
            "Sable rises and falls into step behind you."
        )

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
                    return f"You can't take the {item.name}."
                room.remove_item(item)
                self.player.add_to_inventory(item)
                if item.name == "hand terminal":
                    self.player.has_terminal = True
                    self.game_state.set_flag("has_terminal", True)
                self._act(1)
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
        for i in self.game_state.current_room.items:
            if i.matches_name(name):
                item = i
                source = "room"
                break
        else:
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
        self.game_state.set_flag("suit_worn", True)
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
                self.game_state.set_flag("suit_worn", False)
                self._act(1)
                warn = ""
                if self.game_state.current_room_id in TOXIC_ROOMS:
                    warn = "\nThe air bites instantly. Get sealed or get inside."
                return f"You take off the {item.name}.{warn}"
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
        # Medkit: humans/specialists only.
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
            if gs.get_flag("cave_triggered"):
                return "MOTION: outside\nDISTANCE: uncertain\nSIGNAL: intermittent"
            return "No internal motion detected."

        # It has recently had you in its room: the gut-punch.
        if m.turns_since_seen <= 1:
            return "You lift the terminal.\n\nIt is already looking at you."

        room = gs.current_room
        if room.scanner_interference:
            return "MOTION: interference\nDISTANCE: unknown\nSIGNAL: scrambled"

        # Read the scanner's *belief*, not the truth — it can be a turn stale.
        tracked = m.tracked_room_id or m.current_room_id
        if tracked == gs.current_room_id:
            return "MOTION: here\nDISTANCE: 0\nSIGNAL: inside the room"

        dist, direction = gs.shortest_path(gs.current_room_id, tracked)
        if dist is None:
            return "MOTION: none\nDISTANCE: ---\nSIGNAL: lost"
        # Up close the signal sometimes ghosts out entirely.
        if dist <= 1 and gs.rng.random() < 0.25:
            return "MOTION: ---\nDISTANCE: signal lost\nSIGNAL: ghosting"
        signal = "strong" if dist <= 2 else "intermittent"
        moves = "1 move" if dist == 1 else f"{dist} moves"
        return f"MOTION: {direction}\nDISTANCE: {moves}\nSIGNAL: {signal}"

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
        # If it's aboard, it files away where you went to ground.
        if self.game_state.monster.active:
            self.game_state.monster.known_hide_room = self.game_state.current_room_id
        self._act(1)
        if reused:
            return f"You take cover again — {spot['name']}.\nThe same hiding place feels smaller now."
        return f"You take cover — {spot['name']}. You go still."

    def handle_throw(self, words: list[str]) -> str:
        if not words:
            return "Throw what?"
        # Allow "throw can east".
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
            # The decoy makes noise over there, not here.
            self._act(0)
            gs.last_action_sound = 0
            if not m.active:
                return f"The {item.name} clatters away to the {direction}."
            # It learns. Each trick is less likely to work than the last.
            fell_for_it = gs.rng.random() < max(0.1, 1.0 - 0.3 * m.distraction_uses)
            m.distraction_uses += 1
            if fell_for_it:
                m.last_heard_room_id = target
                m.turns_since_heard = 0
                m.add_suspicion(target, 8)
                m.set_distracted(gs.turn_count + 2)
                return f"The {item.name} clatters away {direction}. Something shifts toward the sound."
            return f"The {item.name} clatters away {direction}.\nIt glances toward the noise. It does not turn."
        # No direction: just noise where you are. Loud, and a mistake.
        self._act(3)
        return f"The {item.name} clatters across the floor. Loud. Too loud."

    # ------------------------------------------------------------------ #
    # Repair / win
    # ------------------------------------------------------------------ #
    def handle_install(self, words: list[str]) -> str:
        if self.game_state.current_room_id != "communications":
            self._meta()
            return "There is nothing to install here."
        if not words:
            return "Install what?"
        name = " ".join(words)
        item = self.player.has_item(name)
        if not item:
            self._meta()
            return f"You aren't carrying {name}."
        mapping = {
            "power coupler": "has_power_coupler",
            "signal relay": "has_signal_relay",
            "antenna key": "has_antenna_key",
        }
        if item.name not in mapping:
            self._meta()
            return f"The {item.name} doesn't fit any socket."
        setattr(self.player, mapping[item.name], True)
        self.player.remove_from_inventory(item)
        self._act(2)
        left = 3 - self.player.installed_parts()
        tail = "" if left == 0 else f" {left} socket{'s' if left != 1 else ''} still open."
        return f"The {item.name} seats with a click.{tail}"

    def handle_repair(self, words: list[str]) -> str:
        if self.game_state.current_room_id != "communications":
            self._meta()
            return "There is nothing here to repair."
        # Auto-install any carried parts, to be forgiving.
        for part, attr in (
            ("power coupler", "has_power_coupler"),
            ("signal relay", "has_signal_relay"),
            ("antenna key", "has_antenna_key"),
        ):
            item = self.player.has_item(part)
            if item:
                setattr(self.player, attr, True)
                self.player.remove_from_inventory(item)
        if self.player.installed_parts() < 3:
            missing = []
            if not self.player.has_power_coupler:
                missing.append("power coupler")
            if not self.player.has_signal_relay:
                missing.append("signal relay")
            if not self.player.has_antenna_key:
                missing.append("antenna key")
            self._act(2)
            return "The transmitter stays dead. Still missing: " + ", ".join(missing) + "."
        self.player.transmitter_repaired = True
        self.game_state.set_flag("transmitter_repaired", True)
        self.game_state.game_phase = "final_repair"
        self._act(3)  # loud — draws the monster
        return (
            "You force the panel shut. Current sings through the transmitter.\n\n"
            "TRANSMISSION READY.\nMessage? (type: send <your message>)"
        )

    def handle_send(self, words: list[str]) -> str:
        if not self.player.transmitter_repaired:
            self._meta()
            if self.game_state.current_room_id != "communications":
                return "You have nothing to send from here."
            return "The transmitter is dead. Repair it first."
        self._act(2)
        self.game_state.set_flag("warning_sent", True)
        self.game_state.win_state = True
        self.game_state.game_phase = "won"
        return "You key the transmitter."

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
                # Don't spoil rooms you haven't entered yet.
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
            "  install <part>, repair transmitter, send <message>\n"
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
