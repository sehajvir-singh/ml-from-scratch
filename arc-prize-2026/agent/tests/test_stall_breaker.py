"""Offline check of grafts/stall_breaker.py (Depth Engine part 3) on the REAL ToolAgent prompt builder."""
from __future__ import annotations

import os
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
from inference.agent.runtime_state import Frame, HistoryEntry  # noqa: E402

ORIGINAL = {}
NS = {}


def setUpModule():
    ORIGINAL["build"] = tool_agent.ToolAgent._build_user_prompt
    NS.update({"_tool_agent": tool_agent, "__name__": "sb"})
    exec(compile((AGENT / "grafts" / "stall_breaker.py").read_text(), "stall_breaker", "exec"), NS)


def tearDownModule():
    tool_agent.ToolAgent._build_user_prompt = ORIGINAL["build"]


def board():
    grid = [[0] * 64 for _ in range(64)]
    for r0, c0, size, color in ((10, 10, 3, 8), (30, 40, 2, 9), (50, 20, 4, 4)):
        for r in range(r0, r0 + size):
            for c in range(c0, c0 + size):
                grid[r][c] = color
    for c in range(5, 30):
        grid[1][c] = 11                      # a step-counter bar on the top border: never a click suggestion
    return tuple(tuple(row) for row in grid)


class StallBreakerTests(unittest.TestCase):
    def test_lists_untried_objects_and_keys_after_threshold(self):
        grid = board()
        # 90 actions on level 1: clicks only on the red 3x3 at (10,10) and UP presses; an earlier level-0 entry
        history = [HistoryEntry("DOWN", Frame(grid, 0, 0))]
        history += [HistoryEntry("MOUSE(row=11, col=11)" if i % 2 else "UP", Frame(grid, i + 1, 1)) for i in range(90)]
        line = NS["_sb_line"](Frame(grid, 91, 1), history, ["UP", "DOWN", "LEFT", "MOUSE"])
        self.assertIsNotNone(line)
        self.assertIn("90 actions", line)
        self.assertIn("bx4", line)                  # the blue 2x2 was never clicked
        self.assertIn("cx16", line)                 # the color-4 4x4 was never clicked
        self.assertNotIn("Rx9", line)               # the red 3x3 was clicked
        self.assertIn("DOWN", line)                 # DOWN was only pressed on the previous level
        self.assertIn("LEFT", line)
        self.assertNotIn("row=1,", line)
        self.assertNotIn("keys UP", line)

    def test_silent_before_threshold(self):
        grid = board()
        history = [HistoryEntry("UP", Frame(grid, i, 1)) for i in range(40)]
        self.assertIsNone(NS["_sb_line"](Frame(grid, 40, 1), history, ["UP", "DOWN", "MOUSE"]))
        self.assertEqual(NS["OURS_STALL_COUNTS"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
