"""Behavioural tests for KEPLER ISOLATION.

These lock in the rules that are easy to break while iterating on atmosphere:
the parser's forgiveness, map integrity, the scanner, the monster behaviour,
the win gate, and save/load.
"""

from collections import deque

from conftest import build_game
from item import Item


# --------------------------------------------------------------------------- #
# Parser
# --------------------------------------------------------------------------- #
def test_direction_aliases_move(game):
    gs, parser = game
    # Start in C09; south exit leads to C08 (cryo airlock inner).
    gs.current_room_id = "c09"
    parser.parse_command("s")
    assert gs.current_room_id != "c09"


def test_get_is_take_and_sets_terminal(game):
    gs, parser = game
    gs.current_room_id = "c09"
    out = parser.parse_command("get hand terminal")
    assert "take" in out.lower()
    assert gs.player.has_terminal is True


def test_examine_alias_and_filler(game):
    gs, parser = game
    gs.current_room_id = "c09"
    out = parser.parse_command("x the hand terminal")
    assert len(out) > 0
    assert "?" not in out[:5]  # didn't fail to parse


def test_unknown_command_is_graceful(game):
    gs, parser = game
    assert "help" in parser.parse_command("frobnicate the whatsit").lower()


def test_crawl_in_and_down_directions(game):
    gs, parser = game
    # C09 -> south leads to C08; crawl should also work.
    gs.current_room_id = "c09"
    exits = gs.current_room.exits
    first_dir = next(iter(exits))
    parser.parse_command(f"crawl {first_dir}")
    assert gs.current_room_id == exits[first_dir]


# --------------------------------------------------------------------------- #
# Map integrity
# --------------------------------------------------------------------------- #
def test_all_rooms_reachable_from_c09(game):
    gs, _ = game
    seen, q = {"c09"}, deque(["c09"])
    while q:
        for dest in gs.rooms[q.popleft()].exits.values():
            assert dest in gs.rooms, f"Exit destination {dest!r} not in rooms"
            if dest not in seen:
                seen.add(dest)
                q.append(dest)
    assert seen == set(gs.rooms), f"Unreachable rooms: {set(gs.rooms) - seen}"


def test_required_parts_placed(game):
    gs, _ = game
    placed = {i.name for r in gs.rooms.values() for i in r.items}
    for part in ("transmitter coil", "signal crystal", "power regulator", "antenna coupler"):
        assert part in placed, f"Required part missing from map: {part}"


def test_safe_haven_rooms_block_monster(game):
    gs, _ = game
    safe = {"c09", "c10", "c11", "c12", "c13"}
    for rid in safe:
        assert gs.rooms[rid].monster_allowed is False, f"{rid} should block monster"


# --------------------------------------------------------------------------- #
# Scanner
# --------------------------------------------------------------------------- #
def test_scan_no_device(game):
    gs, parser = game
    gs.player.has_terminal = False
    out = parser.parse_command("scan")
    assert "no scanner" in out.lower()


def test_scan_reports_direction_and_distance(game):
    gs, parser = game
    gs.player.has_terminal = True
    gs.monster.active = True
    gs.monster.current_room_id = "a07"
    gs.monster.tracked_room_id = "a07"
    gs.monster.turns_since_seen = 99
    gs.current_room_id = "c09"
    out = parser.parse_command("scan")
    assert "Direction:" in out
    assert "Distance:" in out
    assert " m" in out  # unified meters display: "~75 m"
    assert "Confidence:" in out


def test_scan_here_when_same_room(game):
    gs, parser = game
    gs.player.has_terminal = True
    gs.monster.active = True
    gs.monster.current_room_id = "c09"
    gs.monster.tracked_room_id = "c09"
    gs.current_room_id = "c09"
    assert "here" in parser.parse_command("scan").lower()


def test_scan_uses_lagged_belief(game):
    gs, parser = game
    gs.player.has_terminal = True
    gs.monster.active = True
    gs.monster.turns_since_seen = 99
    gs.current_room_id = "c09"
    # Truth: g11, belief: a07
    gs.monster.current_room_id = "g11"
    gs.monster.tracked_room_id = "a07"
    out = parser.parse_command("scan")
    _, belief_dir = gs.shortest_path("c09", "a07")
    compass = {"north": "N", "south": "S", "east": "E", "west": "W"}.get(belief_dir or "", "")
    assert compass in out  # reports belief direction


def test_scan_reports_seen_after_same_room(game):
    gs, parser = game
    gs.player.has_terminal = True
    gs.monster.active = True
    gs.monster.turns_since_seen = 0
    gs.current_room_id = "c09"
    gs.monster.current_room_id = "a07"
    assert "looking at you" in parser.parse_command("scan").lower()


# --------------------------------------------------------------------------- #
# Monster behaviour
# --------------------------------------------------------------------------- #
def test_monster_cannot_enter_safe_haven(game):
    gs, _ = game
    gs.monster.active = True
    gs.monster.current_room_id = "c08"
    gs.monster.aggression = 3
    # Force the monster to try to walk into c09 (safe haven).
    # It should be blocked by monster_allowed=False.
    for _ in range(5):
        gs.advance_world()
        assert gs.monster.current_room_id not in {"c09", "c10", "c11", "c12", "c13"}


def test_monster_starts_active_at_g11(game):
    gs, _ = game
    assert gs.monster.active is True
    assert gs.monster.current_room_id == "g11"


def test_final_run_phase_camps_a07(game):
    gs, _ = game
    gs.monster.active = True
    gs.monster.current_room_id = "g08"
    gs.game_phase = "final_run"
    target = gs._choose_target()
    assert target == "a07"


def test_distraction_fatigue(game):
    gs, parser = game
    gs.monster.active = True
    gs.monster.current_room_id = "d06"
    gs.current_room_id = "c09"
    exits = gs.current_room.exits
    first_dir = next(iter(exits))
    ignored = 0
    for _ in range(8):
        gs.player.inventory.append(Item("loose can", "can", "x", portable=True))
        out = parser.parse_command(f"throw can {first_dir}")
        if "does not turn" in out:
            ignored += 1
    assert gs.monster.distraction_uses == 8
    assert ignored >= 1


# --------------------------------------------------------------------------- #
# Bodies and synthetics
# --------------------------------------------------------------------------- #
def test_bodies_spawn_in_world():
    gs, _ = build_game()
    gs.spawn_random_entities()
    bodies = sum(1 for r in gs.rooms.values() for i in r.items if i.name == "body")
    assert bodies == 20


def test_synthetics_spawn_in_world():
    gs, _ = build_game()
    gs.spawn_random_entities()
    synths = sum(1 for r in gs.rooms.values() for i in r.items if i.synthetic_data)
    assert synths == 3


def test_examine_body(game):
    gs, parser = game
    gs.spawn_random_entities()
    for rid, room in gs.rooms.items():
        bodies = [i for i in room.items if i.name == "body"]
        if bodies:
            gs.current_room_id = rid
            out = parser.parse_command("examine body")
            assert len(out) > 20
            assert "?" not in out[:5]
            break


def test_talk_molly(game):
    gs, parser = game
    out = parser.parse_command("molly")
    assert "MOTHER-LACUNA" in out


def test_molly_phase_response(game):
    gs, parser = game
    gs.game_phase = "collecting"
    out = parser.parse_command("talk molly")
    assert "MOTHER-LACUNA" in out


# --------------------------------------------------------------------------- #
# Win gate — radio crafting
# --------------------------------------------------------------------------- #
def test_craft_requires_all_parts(game):
    gs, parser = game
    gs.current_room_id = "c13"
    out = parser.parse_command("craft radio")
    assert gs.win_state is False
    assert "missing" in out.lower()


def test_craft_radio_full_path(game):
    gs, parser = game
    # Teleport and grab all components + consumables.
    for room_id, item_name in [
        ("a07", "transmitter coil"),
        ("d09", "signal crystal"),
        ("f08", "power regulator"),
        ("g11", "antenna coupler"),
        ("b06", "wire spool"),
        ("c12", "battery cell"),
        ("d05", "tape roll"),
    ]:
        gs.current_room_id = room_id
        parser.parse_command(f"take {item_name}")

    gs.current_room_id = "c13"
    out = parser.parse_command("craft radio")
    assert gs.player.radio_built is True
    assert gs.player.has_item("improvised radio") is not None
    assert "components seat together" in out.lower()


def test_override_requires_radio_and_tokens(game):
    gs, parser = game
    gs.current_room_id = "a07"
    out = parser.parse_command("override ai")
    assert gs.get_flag("ai_overridden") is False
    assert "need" in out.lower() or "radio" in out.lower()


def test_full_win_path(game):
    gs, parser = game
    # Grab terminal.
    gs.current_room_id = "c09"
    parser.parse_command("take hand terminal")

    # Grab all 7 radio parts.
    for room_id, item_name in [
        ("a07", "transmitter coil"),
        ("d09", "signal crystal"),
        ("f08", "power regulator"),
        ("g11", "antenna coupler"),
        ("b06", "wire spool"),
        ("c12", "battery cell"),
        ("d05", "tape roll"),
    ]:
        gs.current_room_id = room_id
        parser.parse_command(f"take {item_name}")

    # Craft.
    gs.current_room_id = "c13"
    parser.parse_command("craft radio")
    assert gs.player.radio_built is True

    # Grab override tokens.
    for room_id, item_name in [
        ("a05", "command keycard"),
        ("b03", "admin cipher"),
        ("f10", "manual authorization"),
    ]:
        gs.current_room_id = room_id
        parser.parse_command(f"take {item_name}")

    # Override at A07.
    gs.current_room_id = "a07"
    parser.parse_command("override ai")
    assert gs.get_flag("ai_overridden") is True
    assert gs.game_phase == "final_run"

    # Send warning.
    parser.parse_command("send warning")
    assert gs.win_state is True


# --------------------------------------------------------------------------- #
# Save / load
# --------------------------------------------------------------------------- #
def test_save_load_roundtrip(game, tmp_path):
    import save

    gs, parser = game
    parser.parse_command("take hand terminal")
    gs.monster.active = True
    gs.monster.current_room_id = "f08"
    gs.monster.suspicion_by_room = {"e05": 5}
    gs.game_phase = "collecting"

    path = str(tmp_path / "s.json")
    assert save.save_game(gs, path)

    # Trash live state, then restore.
    old_room = gs.current_room_id
    gs.current_room_id = "g11"
    gs.player.inventory = []
    gs.monster.current_room_id = "g11"
    assert save.load_game(gs, path)

    assert gs.current_room_id == old_room
    assert gs.player.has_terminal is True
    assert any(i.name == "hand terminal" for i in gs.player.inventory)
    assert gs.monster.current_room_id == "f08"
    assert gs.monster.suspicion_by_room == {"e05": 5}
    assert gs.game_phase == "collecting"
