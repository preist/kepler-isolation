"""Behavioural tests for THE THIN AIR.

These lock in the rules that are easy to break while iterating on atmosphere:
the parser's forgiveness, map integrity, the toxic clock, the scanner, the
boarding event, and the win gate.
"""

from collections import deque

from conftest import build_game


# --------------------------------------------------------------------------- #
# Parser
# --------------------------------------------------------------------------- #
def test_direction_aliases_move(game):
    gs, parser = game
    gs.current_room_id = "central_corridor"
    parser.parse_command("n")
    assert gs.current_room_id == "cockpit"
    parser.parse_command("s")
    assert gs.current_room_id == "central_corridor"


def test_get_is_take_and_sets_terminal(game):
    gs, parser = game
    out = parser.parse_command("get hand terminal")
    assert "take" in out.lower()
    assert gs.player.has_terminal is True


def test_examine_alias_and_filler(game):
    gs, parser = game
    # "x the hand terminal" -> examine, with filler "the" stripped.
    out = parser.parse_command("x the hand terminal")
    assert "scanner" in out.lower()


def test_unknown_command_is_graceful(game):
    gs, parser = game
    assert "help" in parser.parse_command("frobnicate the whatsit").lower()


# --------------------------------------------------------------------------- #
# Map integrity
# --------------------------------------------------------------------------- #
def test_all_rooms_reachable_from_cockpit(game):
    gs, _ = game
    seen, q = {"cockpit"}, deque(["cockpit"])
    while q:
        for dest in gs.rooms[q.popleft()].exits.values():
            assert dest in gs.rooms
            if dest not in seen:
                seen.add(dest)
                q.append(dest)
    assert seen == set(gs.rooms)


def test_required_parts_placed(game):
    gs, _ = game
    placed = {i.name for r in gs.rooms.values() for i in r.items}
    for part in ("power coupler", "signal relay", "antenna key"):
        assert part in placed


# --------------------------------------------------------------------------- #
# Toxic atmosphere
# --------------------------------------------------------------------------- #
def test_human_dies_on_second_toxic_turn():
    gs, _ = build_game("human")
    gs.current_room_id = "surface"
    gs.advance_world()
    assert gs.death_state is None      # warning only
    gs.advance_world()
    assert gs.death_state == "toxic"


def test_synthetic_survives_longer():
    gs, _ = build_game("synthetic")
    gs.current_room_id = "surface"
    gs.advance_world()
    gs.advance_world()
    assert gs.death_state is None      # synthetic gets a third turn
    gs.advance_world()
    assert gs.death_state == "toxic"


def test_suit_prevents_toxic_death():
    gs, _ = build_game("human")
    gs.current_room_id = "surface"
    gs.player.suit_worn = True
    for _ in range(5):
        gs.advance_world()
    assert gs.death_state is None


# --------------------------------------------------------------------------- #
# Scanner
# --------------------------------------------------------------------------- #
def test_scan_reports_direction_and_distance(game):
    gs, parser = game
    gs.player.has_terminal = True
    gs.monster.active = True
    gs.monster.phase = "aboard"
    gs.monster.current_room_id = "communications"
    gs.current_room_id = "cockpit"
    out = parser.parse_command("scan")
    dist, direction = gs.shortest_path("cockpit", "communications")
    assert f"MOTION: {direction}" in out
    assert f"{dist} moves" in out


def test_scan_here_when_same_room(game):
    gs, parser = game
    gs.player.has_terminal = True
    gs.monster.active = True
    gs.monster.phase = "aboard"
    gs.monster.current_room_id = "cockpit"
    gs.current_room_id = "cockpit"
    assert "here" in parser.parse_command("scan").lower()


# --------------------------------------------------------------------------- #
# Boarding
# --------------------------------------------------------------------------- #
def test_monster_boards_after_cave_return(game):
    gs, _ = game
    gs.set_flag("cave_triggered", True)
    gs.set_flag("went_outside", True)
    gs.current_room_id = "airlock"
    for _ in range(6):
        gs.advance_world()
        if gs.get_flag("monster_boarded"):
            break
    assert gs.get_flag("monster_boarded") is True
    assert gs.monster.active is True


# --------------------------------------------------------------------------- #
# Win gate
# --------------------------------------------------------------------------- #
def test_repair_requires_all_parts(game):
    gs, parser = game
    gs.current_room_id = "communications"
    out = parser.parse_command("repair transmitter")
    assert gs.win_state is False
    assert "missing" in out.lower()


def test_full_repair_and_send_wins(game):
    gs, parser = game
    gs.current_room_id = "communications"
    gs.player.has_power_coupler = True
    gs.player.has_signal_relay = True
    gs.player.has_antenna_key = True
    parser.parse_command("repair transmitter")
    assert gs.player.transmitter_repaired is True
    parser.parse_command("send do not come here")
    assert gs.win_state is True
