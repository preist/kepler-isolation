#!/usr/bin/env python3
"""
Headless balance harness for KEPLER ISOLATION.

Drives a "careful but non-adaptive" player (quiet crawling, grabs the parts,
makes the warning) across many RNG seeds and reports the spread of outcomes.
A fair game should let this rote run win *sometimes* — not always (then the
monster is toothless), not never (then it's unfair). A real, adaptive player
will always do better than this baseline.

Run:  python3 tools/balance.py [N]
"""

import os
import sys
import random

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, SRC)

from game_state import GameState
from player import Player
from parser import Parser
from map_builder import create_rooms

# A quiet route: cave (trigger) -> back -> three parts -> communications -> send.
ROUTE = [
    "take hand terminal",
    "crawl south", "crawl east", "wear suit",
    "crawl out", "crawl east", "crawl east", "crawl down",   # signal_cave: trigger
    "crawl up", "crawl west", "crawl west", "crawl in",       # back to airlock
    "crawl west", "crawl west", "crawl south",                # -> reactor_room
    "take signal relay",
    "crawl north", "crawl west", "take power coupler",        # storage
    "crawl south", "take antenna key",                        # cargo_bay
    "crawl east", "crawl east", "crawl east",                 # -> communications
    "repair transmitter", "send do not come here",
]


def _new_game(seed):
    gs = GameState()
    gs.rng = random.Random(seed)
    gs.rooms = create_rooms()
    gs.player = Player("Sim", "n", "human")
    gs.current_room_id = "cockpit"
    return gs, Parser(gs)


def _step(gs, parser, cmd):
    parser.parse_command(cmd)
    if gs.win_state:           # win short-circuits the world (see main loop)
        return
    if gs.advance:
        gs.advance_world()


def play(seed):
    """Non-adaptive: walk the route, never react to the monster."""
    gs, parser = _new_game(seed)
    for cmd in ROUTE:
        _step(gs, parser, cmd)
        if gs.death_state:
            return ("death", gs.death_state, gs.turn_count)
        if gs.win_state:
            return ("win", None, gs.turn_count)
    return ("incomplete", None, gs.turn_count)


def _monster_dist(gs):
    if not gs.monster.active:
        return None
    d, _ = gs.shortest_path(gs.current_room_id, gs.monster.current_room_id)
    return d


def _dest(gs, cmd):
    """Destination room of a movement command, else None."""
    if cmd.startswith("crawl "):
        return gs.current_room.exits.get(cmd.split()[1])
    return None


def play_smart(seed):
    """Adaptive: keep moving quietly, never step into the creature's room, and
    take brief cover only when the path is blocked. Models careful human play."""
    gs, parser = _new_game(seed)
    queue = list(ROUTE)
    guard = 0
    while queue and guard < 400:
        guard += 1
        mon = gs.monster.current_room_id if gs.monster.active else None
        room = gs.current_room
        dist = _monster_dist(gs)

        # Mobile-with-selective-cover: keep moving (that holds your lead), and
        # only take cover when actually cornered — the creature in your room, or
        # the next step walking straight into it. Don't hide-spam.
        if gs.player.hidden:
            _step(gs, parser, queue.pop(0) if (dist is None or dist >= 2) else "wait")
        elif mon == gs.current_room_id:
            _step(gs, parser, "hide" if room.hiding_spots else queue.pop(0))
        elif _dest(gs, queue[0]) == mon and mon is not None:
            _step(gs, parser, "hide" if room.hiding_spots else "wait")
        else:
            _step(gs, parser, queue.pop(0))

        if gs.death_state:
            return ("death", gs.death_state, gs.turn_count)
        if gs.win_state:
            return ("win", None, gs.turn_count)
    return ("incomplete", None, gs.turn_count)


def _report(label, fn, n):
    wins = deaths = incomplete = 0
    causes = {}
    turns = []
    for seed in range(n):
        outcome, cause, t = fn(seed)
        if outcome == "win":
            wins += 1
            turns.append(t)
        elif outcome == "death":
            deaths += 1
            causes[cause] = causes.get(cause, 0) + 1
        else:
            incomplete += 1
    line = (f"{label:16s} wins {100*wins//n:3d}%  deaths {100*deaths//n:3d}% "
            f"{causes}  incomplete {incomplete}")
    if turns:
        line += f"  | win turns avg {sum(turns)//len(turns)}"
    print(line)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    print(f"seeds: {n}")
    _report("careless rush", play, n)
    _report("careful (hides)", play_smart, n)


if __name__ == "__main__":
    main()
