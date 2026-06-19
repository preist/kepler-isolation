"""Headless smoke test for the Textual UI.

Skipped automatically when `textual` isn't installed (the TUI is optional).
Uses Textual's pilot to drive role-select, an item take, and a move, asserting
the engine and panels respond.
"""

import asyncio
import importlib.util

import pytest

if importlib.util.find_spec("textual") is None:
    pytest.skip("textual not installed (optional UI)", allow_module_level=True)

from textual.widgets import Static

from tui import KeplerApp


def _content(app, selector):
    return str(app.query_one(selector, Static).render())


def test_tui_role_take_move():
    async def scenario():
        app = KeplerApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#cmd")

            inp.value = "1"  # pick Crew
            await pilot.press("enter")
            await pilot.pause()
            assert app.mode == "play"
            assert "Cryo" in app.engine.location_name  # C09

            inp.value = "take hand terminal"
            await pilot.press("enter")
            await pilot.pause()
            assert app.engine.has_terminal is True
            assert "CARRYING" in _content(app, "#inv")
            assert "MOTION TRACKER" in _content(app, "#tracker")

            # Move in first available direction.
            first_exit = next(iter(app.engine.exits))
            inp.value = first_exit
            await pilot.press("enter")
            await pilot.pause()
            assert app.engine.gs.current_room_id != "c09"
            assert "EXITS" in _content(app, "#exits")

    asyncio.run(scenario())
