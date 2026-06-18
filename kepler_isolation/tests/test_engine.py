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
    r = e.submit("south")  # cockpit -> central_corridor
    assert e.location_name == "Central Corridor"
    assert r.room_changed
    assert not r.dead and not r.won


def test_take_updates_inventory_and_terminal():
    e = make_engine()
    e.submit("take hand terminal")
    assert "hand terminal" in e.inventory
    assert e.has_terminal is True


def test_panel_accessors():
    e = make_engine()
    assert e.location_name == "Cockpit"
    assert "south" in e.exits
    assert "hand terminal" in e.room_items
    assert e.suit_status == "none"
    assert e.sound_level == "silent"


def test_motion_no_device_then_bearing():
    e = make_engine()
    assert e.motion()["kind"] == "no_device"  # no terminal yet
    e.gs.player.has_terminal = True
    e.gs.monster.active = True
    e.gs.monster.phase = "aboard"
    e.gs.monster.turns_since_seen = 9
    e.gs.monster.current_room_id = "communications"
    e.gs.current_room_id = "cockpit"
    m = e.motion()
    assert m == {"kind": "bearing", "direction": "south", "distance": 7}
    assert motion_label(m) == "south 7"


def test_win_via_send():
    e = make_engine()
    e.gs.current_room_id = "communications"
    e.gs.player.has_power_coupler = True
    e.gs.player.has_signal_relay = True
    e.gs.player.has_antenna_key = True
    e.submit("repair transmitter")
    r = e.submit("send do not come here")
    assert r.won is True


def test_toxic_death_result():
    e = make_engine("1")
    e.gs.current_room_id = "surface"  # toxic, no suit
    e.submit("wait")
    r = e.submit("wait")
    assert r.dead == "toxic"


def test_meta_and_control_flags():
    e = make_engine()
    r = e.submit("help")
    assert r.lines and not r.advanced
    assert e.submit("restart").restart is True
    assert e.submit("quit").quit is True
