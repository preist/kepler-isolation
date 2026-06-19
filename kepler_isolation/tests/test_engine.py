"""Tests for the GameEngine façade (engine.py).

These lock the front-end-facing contract: submit() advances the world and
reports outcomes, and the panel accessors return what a UI needs.
"""

import random

from engine import GameEngine, motion_label


def make_engine(role="1", seed=0):
    e = GameEngine()
    e.new_game(role)
    e.gs.rng = random.Random(seed)
    return e


def test_submit_moves_and_reports():
    e = make_engine()
    # From C09, take the first exit.
    first_exit = next(iter(e.gs.current_room.exits))
    r = e.submit(first_exit)
    assert e.gs.current_room_id != "c09"
    assert r.room_changed
    assert not r.dead and not r.won


def test_take_updates_inventory_and_terminal():
    e = make_engine()
    e.submit("take hand terminal")
    assert "hand terminal" in e.inventory
    assert e.has_terminal is True


def test_panel_accessors():
    e = make_engine()
    assert "Cryo" in e.location_name  # C09 = Cryo Monitoring Station
    assert len(e.exits) > 0
    assert "hand terminal" in e.room_items
    assert e.suit_status == "none"
    assert e.sound_level == "silent"


def test_motion_no_device_then_bearing():
    e = make_engine()
    assert e.motion()["kind"] == "no_device"  # no terminal yet
    e.gs.player.has_terminal = True
    e.gs.monster.active = True
    e.gs.monster.turns_since_seen = 9
    e.gs.monster.current_room_id = "a07"
    e.gs.monster.tracked_room_id = "a07"
    e.gs.current_room_id = "c09"
    m = e.motion()
    assert m["kind"] == "bearing"
    assert "direction" in m
    assert "meters" in m
    assert "confidence" in m
    assert "motion_desc" in m
    label = motion_label(m)
    assert m["direction"] in label


def test_win_via_full_radio_path():
    e = make_engine()
    gs = e.gs
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
        e.submit(f"take {item_name}")

    gs.current_room_id = "c13"
    e.submit("craft radio")

    for room_id, item_name in [
        ("a05", "command keycard"),
        ("b03", "admin cipher"),
        ("f10", "manual authorization"),
    ]:
        gs.current_room_id = room_id
        e.submit(f"take {item_name}")

    gs.current_room_id = "a07"
    e.submit("override ai")
    r = e.submit("send warning")
    assert r.won is True


def test_meta_and_control_flags():
    e = make_engine()
    r = e.submit("help")
    assert r.lines and not r.advanced
    assert e.submit("restart").restart is True
    assert e.submit("quit").quit is True


def test_bodies_and_synthetics_spawn():
    e = make_engine()
    gs = e.gs
    bodies = sum(1 for r in gs.rooms.values() for i in r.items if i.name == "body")
    synths = sum(1 for r in gs.rooms.values() for i in r.items if i.synthetic_data)
    assert bodies == 20
    assert synths == 3


def test_monster_blocked_from_safe_haven():
    e = make_engine()
    gs = e.gs
    gs.monster.current_room_id = "c08"
    gs.monster.aggression = 3
    for _ in range(5):
        gs.advance_world()
        assert gs.monster.current_room_id not in {"c09", "c10", "c11", "c12", "c13"}
