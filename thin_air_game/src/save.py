"""
Save / load for THE THIN AIR.

The map's *static* structure (exits, vents, hazards, descriptions) is rebuilt
from map_builder on load — we only persist the things that actually change
during play: where items are, what the player carries, room/hiding state, the
monster, and the flags. Everything is plain JSON, so a save is inspectable and
survives small code changes.
"""

import os
import json

from player import Player
from map_builder import create_rooms

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "savegame.json")
VERSION = 1

# Item attributes we round-trip (covers items wherever they live).
_ITEM_FIELDS = ("name", "aliases", "description", "portable", "wearable", "worn",
                "readable_text", "use_effect", "install_target", "sound_on_use",
                "required_for_win")


def _item_to_dict(item):
    return {f: getattr(item, f) for f in _ITEM_FIELDS}


def _item_from_dict(d):
    from item import Item
    return Item(d["name"], d["aliases"], d["description"],
                portable=d["portable"], wearable=d["wearable"], worn=d["worn"],
                readable_text=d["readable_text"], use_effect=d["use_effect"],
                install_target=d["install_target"], sound_on_use=d["sound_on_use"],
                required_for_win=d["required_for_win"])


def to_dict(gs) -> dict:
    p = gs.player
    return {
        "version": VERSION,
        "current_room_id": gs.current_room_id,
        "turn_count": gs.turn_count,
        "game_phase": gs.game_phase,
        "sound_level": gs.sound_level,
        "last_action_sound": gs.last_action_sound,
        "board_countdown": gs.board_countdown,
        "flags": dict(gs.flags),
        "visited_rooms": sorted(gs.visited_rooms),
        "player": {
            "name": p.name, "gender": p.gender, "type": p.type,
            "health": p.health, "suit_worn": p.suit_worn,
            "outside_exposure_turns": p.outside_exposure_turns,
            "hidden": p.hidden,
            "hidden_spot_name": p.hidden_spot["name"] if p.hidden_spot else None,
            "last_room_id": p.last_room_id,
            "stayed_turns_in_room": p.stayed_turns_in_room,
            "has_terminal": p.has_terminal,
            "has_power_coupler": p.has_power_coupler,
            "has_signal_relay": p.has_signal_relay,
            "has_antenna_key": p.has_antenna_key,
            "transmitter_repaired": p.transmitter_repaired,
            "inventory": [_item_to_dict(i) for i in p.inventory],
            "worn": [_item_to_dict(i) for i in p.worn_items],
        },
        "monster": dict(gs.monster.__dict__),
        "rooms": {
            rid: {
                "visited": room.visited,
                "items": [_item_to_dict(i) for i in room.items],
                "hiding_spots": [{"name": s["name"], "reuse": s["reuse"]}
                                 for s in room.hiding_spots],
            }
            for rid, room in gs.rooms.items()
        },
    }


def load_into(gs, data: dict):
    """Rebuild the world inside the *existing* GameState object so all the
    references held by the parser and main loop stay valid."""
    gs.rooms = create_rooms()  # fresh static structure
    gs.current_room_id = data["current_room_id"]
    gs.turn_count = data["turn_count"]
    gs.game_phase = data["game_phase"]
    gs.sound_level = data["sound_level"]
    gs.last_action_sound = data["last_action_sound"]
    gs.board_countdown = data["board_countdown"]
    gs.flags = dict(data["flags"])
    gs.visited_rooms = set(data["visited_rooms"])
    gs.death_state = None
    gs.win_state = False

    # Rooms: overlay item placement, visited flags, hiding-spot wear.
    for rid, rd in data["rooms"].items():
        room = gs.rooms[rid]
        room.visited = rd["visited"]
        room.items = [_item_from_dict(i) for i in rd["items"]]
        wear = {s["name"]: s["reuse"] for s in rd["hiding_spots"]}
        for spot in room.hiding_spots:
            spot["reuse"] = wear.get(spot["name"], 0)

    # Player.
    pd = data["player"]
    p = Player(pd["name"], pd["gender"], pd["type"])
    p.health = pd["health"]
    p.suit_worn = pd["suit_worn"]
    p.outside_exposure_turns = pd["outside_exposure_turns"]
    p.hidden = pd["hidden"]
    p.last_room_id = pd["last_room_id"]
    p.stayed_turns_in_room = pd["stayed_turns_in_room"]
    p.has_terminal = pd["has_terminal"]
    p.has_power_coupler = pd["has_power_coupler"]
    p.has_signal_relay = pd["has_signal_relay"]
    p.has_antenna_key = pd["has_antenna_key"]
    p.transmitter_repaired = pd["transmitter_repaired"]
    p.inventory = [_item_from_dict(i) for i in pd["inventory"]]
    p.worn_items = [_item_from_dict(i) for i in pd["worn"]]
    # Re-link the hiding spot to the real dict in the current room.
    if pd["hidden"] and pd["hidden_spot_name"]:
        p.hidden_spot = gs.rooms[gs.current_room_id].find_hiding_spot(pd["hidden_spot_name"])
    gs.player = p

    # Monster: every field is JSON-safe, so a straight update is enough.
    gs.monster.__dict__.update(data["monster"])


def save_game(gs, path=SAVE_PATH) -> bool:
    try:
        with open(path, "w") as fh:
            json.dump(to_dict(gs), fh, indent=2)
        return True
    except OSError:
        return False


def load_game(gs, path=SAVE_PATH) -> bool:
    if not os.path.exists(path):
        return False
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return False
    if data.get("version") != VERSION:
        return False
    load_into(gs, data)
    return True
