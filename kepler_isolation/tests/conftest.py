"""Test fixtures for KEPLER ISOLATION.

Builds a fully-initialized game with a *seeded* RNG so monster behaviour and
detection rolls are deterministic.
"""

import os
import random
import sys

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, SRC)

from game_state import GameState  # noqa: E402
from map_builder import create_rooms  # noqa: E402
from parser import Parser  # noqa: E402
from player import Player  # noqa: E402


def build_game(player_type="human", seed=0):
    gs = GameState()
    gs.rng = random.Random(seed)
    gs.rooms = create_rooms()
    gs.player = Player("Test", "n", player_type)
    gs.current_room_id = "cockpit"
    parser = Parser(gs)
    return gs, parser


@pytest.fixture
def game():
    return build_game()
