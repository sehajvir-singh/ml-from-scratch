"""Offline check of grafts/affordance.py (Depth Engine part 1) on the REAL solver module.

A synthetic game: clicking any red cell changes the board, every other click does nothing, UP always moves
something and LEFT never does. Objects move between states, so the model has to learn "red", not a position.
Needs torch (CPU) and numpy; skipped without them.
"""
from __future__ import annotations

import os
import random
import sys
import unittest
from pathlib import Path

AGENT = Path(__file__).resolve().parents[1]
SOLVER = AGENT / "vendor" / "anim_solver"
os.environ.setdefault("LOCAL_ANALYZER_BASE_URL", "http://127.0.0.1:9/v1")
os.environ.setdefault("LOCAL_ANALYZER_MODEL_ID", "fake-model")
sys.path.insert(0, str(SOLVER / "ARC3-Inference"))
sys.path.insert(0, str(SOLVER / "tufa-arc-agi-framework" / "src"))

import inference.agent.tool_agent as tool_agent  # noqa: E402
from inference.agent.runtime_state import Frame  # noqa: E402

try:
    import torch  # noqa: F401
    HAVE_TORCH = True
except Exception:
    HAVE_TORCH = False

ORIGINALS = {}
NS = {}


def setUpModule():
    ORIGINALS.update(sig=tool_agent.board_signature, observe=tool_agent.NoopGuard.observe,
                     build=tool_agent.ToolAgent._build_user_prompt)
    if HAVE_TORCH:
        NS.update({"_tool_agent": tool_agent, "__name__": "aff"})
        exec(compile((AGENT / "grafts" / "affordance.py").read_text(), "affordance", "exec"), NS)


def tearDownModule():
    tool_agent.board_signature = ORIGINALS["sig"]
    tool_agent.NoopGuard.observe = ORIGINALS["observe"]
    tool_agent.ToolAgent._build_user_prompt = ORIGINALS["build"]


def make_state(rng):
    grid = [[0] * 64 for _ in range(64)]
    for color, size in ((8, 3), (9, 2), (4, 4)):
        r, c = rng.randrange(2, 60 - size), rng.randrange(2, 60 - size)
        for dr in range(size):
            for dc in range(size):
                grid[r + dr][c + dc] = color
    return tuple(tuple(row) for row in grid)


def cells_of(grid, color):
    return [(r, c) for r in range(64) for c in range(64) if grid[r][c] == color]


@unittest.skipUnless(HAVE_TORCH, "torch not installed")
class AffordanceTests(unittest.TestCase):
    def test_learns_which_clicks_and_moves_matter(self):
        rng = random.Random(0)
        guard = tool_agent.NoopGuard()
        for _ in range(260):
            grid = make_state(rng)
            sig = tool_agent.board_signature(grid)   # the patched version remembers the grid
            kind = rng.random()
            if kind < 0.15:
                action, changed = "UP", True
            elif kind < 0.3:
                action, changed = "LEFT", False
            else:
                color = rng.choice([8, 8, 9, 4, 0])
                cells = cells_of(grid, color) or cells_of(grid, 0)   # overlapping objects can hide a color
                r, c = rng.choice(cells)
                color = grid[r][c]
                action, changed = f"MOUSE(row={r}, col={c})", color == 8
            guard.observe(level=1, board_before_sig=sig, action_sig=action, board_changed=changed)
        learner = guard.__dict__["_ours_affordance"]
        self.assertIsNotNone(learner.trusted(), f"model not trusted: recent={list(learner.recent)[-10:]}")
        test = make_state(random.Random(99))
        lines = NS["_af_hint_lines"](learner, Frame(test, 1, 1), ["UP", "LEFT", "MOUSE"])
        text = "\n".join(lines)
        red = cells_of(test, 8)
        first = NS["_AF_MOUSE_RE"].search(text.replace("(row=", "MOUSE(row="))
        self.assertIsNotNone(first, text)
        self.assertIn((int(first.group(1)), int(first.group(2))), red, text)
        self.assertIn("LEFT", text)
        self.assertNotIn("UP ", text.split("Likely no effect")[-1])
        self.assertEqual(NS["OURS_AFFORDANCE_COUNTS"]["errors"], 0)

    def test_timer_tick_is_not_an_effect(self):
        before = [[0] * 64 for _ in range(64)]
        tick = [row[:] for row in before]
        tick[0][63] = 5                      # vc33-style countdown: one cell on the top edge
        moved = [row[:] for row in before]
        for r in range(30, 34):
            moved[r][30] = 8                 # a real object change in the middle of the board
        real = NS["_af_real_change"]
        self.assertFalse(real(before, before))
        self.assertFalse(real(before, tick))
        self.assertTrue(real(before, moved))
        both = [row[:] for row in moved]
        both[0][63] = 5
        self.assertTrue(real(before, both))

    def test_untrained_model_adds_nothing(self):
        guard = tool_agent.NoopGuard()
        grid = make_state(random.Random(1))
        guard.observe(level=1, board_before_sig=tool_agent.board_signature(grid), action_sig="UP", board_changed=True)
        learner = guard.__dict__["_ours_affordance"]
        self.assertIsNone(learner.trusted())
        self.assertEqual(NS["_af_hint_lines"](learner, Frame(grid, 1, 1), ["UP", "MOUSE"]), [])


if __name__ == "__main__":
    unittest.main()
