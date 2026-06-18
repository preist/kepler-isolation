"""Behavioural tests for KEPLER ISOLATION.

These lock in the rules that are easy to break while iterating on atmosphere:
the parser's forgiveness, map integrity, the toxic clock, the scanner, the
boarding event, and the win gate.
"""

from collections import deque

from conftest import build_game
from item import Item


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


def test_crawl_in_and_down_directions(game):
    gs, parser = game
    # Direction words must survive arg filtering: crawl out/down must move.
    gs.current_room_id = "airlock"
    parser.parse_command("crawl out")
    assert gs.current_room_id == "surface"
    gs.current_room_id = "cave_mouth"
    parser.parse_command("crawl down")
    assert gs.current_room_id == "signal_cave"


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
    assert gs.death_state is None  # warning only
    gs.advance_world()
    assert gs.death_state == "toxic"


def test_synthetic_survives_longer():
    gs, _ = build_game("synthetic")
    gs.current_room_id = "surface"
    gs.advance_world()
    gs.advance_world()
    assert gs.death_state is None  # synthetic gets a third turn
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


def test_scan_uses_lagged_belief(game):
    gs, parser = game
    gs.player.has_terminal = True
    gs.monster.active = True
    gs.monster.phase = "aboard"
    gs.monster.turns_since_seen = 99
    gs.current_room_id = "cockpit"
    # Truth says reactor_room, but the scanner still believes communications.
    gs.monster.current_room_id = "reactor_room"
    gs.monster.tracked_room_id = "communications"
    _, true_dir = gs.shortest_path("cockpit", "reactor_room")
    _, belief_dir = gs.shortest_path("cockpit", "communications")
    out = parser.parse_command("scan")
    assert f"MOTION: {belief_dir}" in out  # reports the belief, not the truth


def test_scan_reports_seen_after_same_room(game):
    gs, parser = game
    gs.player.has_terminal = True
    gs.monster.active = True
    gs.monster.phase = "aboard"
    gs.monster.turns_since_seen = 0
    gs.current_room_id = "cockpit"
    gs.monster.current_room_id = "central_corridor"
    assert "looking at you" in parser.parse_command("scan").lower()


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
def test_sable_wakes_and_follows(game):
    gs, parser = game
    gs.current_room_id = "crew_quarters"
    out = parser.parse_command("examine sable")
    assert gs.get_flag("sable_following") is True
    assert "sable" in out.lower()


def test_sable_sacrifice_prevents_one_death(game):
    gs, _ = game
    gs.monster.active = True
    gs.monster.phase = "aboard"
    gs.current_room_id = "central_corridor"
    gs.monster.current_room_id = "central_corridor"
    gs.set_flag("sable_following", True)
    gs.set_flag("sable_alive", True)

    gs._resolve_same_room()  # would be a kill; Sable intercepts
    assert gs.death_state is None  # Sable takes it instead
    assert gs.get_flag("sable_sacrifice_used") is True
    assert gs.current_room_id != "central_corridor"  # pushed to safety

    # Second time — once its feeding ends — there is no one left to save you.
    gs.turn_count = 99  # past the feeding distraction window
    gs.monster.current_room_id = gs.current_room_id
    gs.player.hidden = False
    gs._resolve_same_room()
    assert gs.death_state == "monster"


def test_final_repair_camps_communications(game):
    gs, _ = game
    gs.monster.active = True
    gs.monster.phase = "aboard"
    gs.monster.current_room_id = "cargo_bay"
    gs.game_phase = "final_repair"
    assert gs._choose_target() == "communications"


def test_distraction_fatigue(game):
    gs, parser = game
    gs.monster.active = True
    gs.monster.phase = "aboard"
    gs.monster.current_room_id = "med_bay"
    gs.current_room_id = "central_corridor"
    # Spam decoys; the monster's gullibility must decay to the floor.
    ignored = 0
    for _ in range(8):
        gs.player.inventory.append(Item("loose can", "can", "x", portable=True))
        out = parser.parse_command("throw can north")
        if "does not turn" in out:
            ignored += 1
    assert gs.monster.distraction_uses == 8
    assert ignored >= 1  # it wises up


# --------------------------------------------------------------------------- #
# Win gate
# --------------------------------------------------------------------------- #
def test_repair_requires_all_parts(game):
    gs, parser = game
    gs.current_room_id = "communications"
    out = parser.parse_command("repair transmitter")
    assert gs.win_state is False
    assert "missing" in out.lower()


def test_save_load_roundtrip(game, tmp_path):
    import save

    gs, parser = game
    parser.parse_command("take hand terminal")
    parser.parse_command("south")
    gs.monster.active = True
    gs.monster.phase = "aboard"
    gs.monster.current_room_id = "reactor_room"
    gs.monster.suspicion_by_room = {"galley": 5}
    gs.set_flag("cave_triggered", True)

    path = str(tmp_path / "s.json")
    assert save.save_game(gs, path)

    # Trash live state, then restore.
    gs.current_room_id = "cockpit"
    gs.player.inventory = []
    gs.monster.current_room_id = "cockpit"
    assert save.load_game(gs, path)

    assert gs.current_room_id == "central_corridor"
    assert gs.player.has_terminal is True
    assert any(i.name == "hand terminal" for i in gs.player.inventory)
    assert gs.monster.current_room_id == "reactor_room"
    assert gs.monster.suspicion_by_room == {"galley": 5}
    assert gs.get_flag("cave_triggered") is True


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
