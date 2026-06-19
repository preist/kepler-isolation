"""
Save / load for KEPLER ISOLATION.

The map's *static* structure (exits, vents, hazards, descriptions) is rebuilt
from map_builder on load — we only persist the things that actually change
during play: where items are, what the player carries, room/hiding state, the
monster, and the flags. Everything is plain JSON, so a save is inspectable and
survives small code changes.
"""

import json
import os

from map_builder import create_rooms
from player import Player

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "savegame.json")
VERSION = 1

# Item attributes we round-trip (covers items wherever they live).
_ITEM_FIELDS = (
    "name",
    "aliases",
    "description",
    "portable",
    "wearable",
    "worn",
    "readable_text",
    "use_effect",
    "install_target",
    "sound_on_use",
    "required_for_win",
)


def _item_to_dict(item):
    d = {f: getattr(item, f) for f in _ITEM_FIELDS}
    # Synthetic NPCs carry extra state (introduced flag, dialogue).
    if item.synthetic_data is not None:
        d["synthetic_data"] = {
            "profile": item.synthetic_data["profile"],
            "name": item.synthetic_data["name"],
            "lines": item.synthetic_data["lines"],
            "lines_synthetic": item.synthetic_data.get("lines_synthetic", []),
            "introduced": item.synthetic_data.get("introduced", False),
        }
    else:
        d["synthetic_data"] = None
    return d


def _item_from_dict(d):
    from item import Item

    item = Item(
        d["name"],
        d["aliases"],
        d["description"],
        portable=d["portable"],
        wearable=d["wearable"],
        worn=d["worn"],
        readable_text=d["readable_text"],
        use_effect=d["use_effect"],
        install_target=d["install_target"],
        sound_on_use=d["sound_on_use"],
        required_for_win=d["required_for_win"],
    )
    if d.get("synthetic_data"):
        item.synthetic_data = d["synthetic_data"]
    return item


def to_dict(gs) -> dict:
    p = gs.player
    return {
        "version": VERSION,
        "current_room_id": gs.current_room_id,
        "turn_count": gs.turn_count,
        "game_phase": gs.game_phase,
        "sound_level": gs.sound_level,
        "last_action_sound": gs.last_action_sound,
        "flags": dict(gs.flags),
        "visited_rooms": sorted(gs.visited_rooms),
        "player": {
            "name": p.name,
            "gender": p.gender,
            "type": p.type,
            "health": p.health,
            "suit_worn": p.suit_worn,
            "outside_exposure_turns": p.outside_exposure_turns,
            "hidden": p.hidden,
            "hidden_spot_name": p.hidden_spot["name"] if p.hidden_spot else None,
            "last_room_id": p.last_room_id,
            "stayed_turns_in_room": p.stayed_turns_in_room,
            "has_terminal": p.has_terminal,
            "has_coil": p.has_coil,
            "has_crystal": p.has_crystal,
            "has_regulator": p.has_regulator,
            "has_coupler": p.has_coupler,
            "radio_built": p.radio_built,
            "inventory": [_item_to_dict(i) for i in p.inventory],
            "worn": [_item_to_dict(i) for i in p.worn_items],
        },
        "character_queue": gs.character_queue,
        "lives_used": gs.lives_used,
        "monster": dict(gs.monster.__dict__),
        "rooms": {
            rid: {
                "visited": room.visited,
                "items": [_item_to_dict(i) for i in room.items],
                "hiding_spots": [{"name": s["name"], "reuse": s["reuse"]} for s in room.hiding_spots],
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
    p.has_coil = pd.get("has_coil", False)
    p.has_crystal = pd.get("has_crystal", False)
    p.has_regulator = pd.get("has_regulator", False)
    p.has_coupler = pd.get("has_coupler", False)
    p.radio_built = pd.get("radio_built", False)
    p.inventory = [_item_from_dict(i) for i in pd["inventory"]]
    p.worn_items = [_item_from_dict(i) for i in pd["worn"]]
    # Re-link the hiding spot to the real dict in the current room.
    if pd["hidden"] and pd["hidden_spot_name"]:
        p.hidden_spot = gs.rooms[gs.current_room_id].find_hiding_spot(pd["hidden_spot_name"])
    gs.player = p

    # Three-life system.
    gs.character_queue = data.get("character_queue", [])
    gs.lives_used = data.get("lives_used", 0)

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
