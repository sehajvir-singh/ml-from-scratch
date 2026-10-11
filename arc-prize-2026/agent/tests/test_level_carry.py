"""Offline check of grafts/level_carry.py (Depth Engine part 2) on the REAL ToolAgent knowledge-update method."""
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

ORIGINAL = {}
NS = {}


def setUpModule():
    ORIGINAL["update"] = tool_agent.ToolAgent._update_summarized_knowledge_from_step_summary
    NS.update({"_tool_agent": tool_agent, "__name__": "lc"})
    exec(compile((AGENT / "grafts" / "level_carry.py").read_text(), "level_carry", "exec"), NS)


def tearDownModule():
    tool_agent.ToolAgent._update_summarized_knowledge_from_step_summary = ORIGINAL["update"]


class FakeAgent:
    """Just the two attributes the method reads; the real method is called unbound on it."""

    def __init__(self):
        self._summarized_knowledge = tool_agent._empty_world_model()
        self._last_step_summary = None


def update(agent):
    tool_agent.ToolAgent._update_summarized_knowledge_from_step_summary(agent)


class LevelCarryTests(unittest.TestCase):
    def test_level_clear_carries_knowledge_and_still_wipes(self):
        agent = FakeAgent()
        agent._summarized_knowledge.update(world_model="blue key opens the red door",
                                           goal_model="reach the green exit", action_model="MOUSE toggles tiles",
                                           current_plan="click (3,4) then UP")
        agent._last_step_summary = {"level_transition": True, "run_complete": False, "game_over": False,
                                    "level": 2, "executed_actions": ["UP", "UP", "MOUSE(row=3, col=4)"]}
        update(agent)
        k = agent._summarized_knowledge
        self.assertEqual(k["world_model"], "")          # the original wipe still happens
        self.assertEqual(k["current_plan"], "")
        notes = k["cross_level_notes"]
        self.assertIn("blue key opens the red door", notes)
        self.assertIn("reach the green exit", notes)
        self.assertIn("MOUSE(row=3, col=4)", notes)
        self.assertNotIn("click (3,4) then UP", notes)  # the old plan is not carried

    def test_keeps_only_two_levels_and_caps_length(self):
        agent = FakeAgent()
        for i in range(4):
            agent._summarized_knowledge.update(world_model=f"rule {i} " + "x" * 400)
            agent._last_step_summary = {"level_transition": True, "run_complete": False, "executed_actions": []}
            update(agent)
        notes = agent._summarized_knowledge["cross_level_notes"]
        self.assertNotIn("rule 0", notes)
        self.assertNotIn("rule 1", notes)
        self.assertIn("rule 3", notes)
        self.assertLessEqual(len(notes), NS["_LC_MAX_CHARS"])

    def test_game_over_is_untouched(self):
        agent = FakeAgent()
        agent._summarized_knowledge.update(world_model="w")
        agent._last_step_summary = {"level_transition": False, "run_complete": False, "game_over": True}
        update(agent)
        self.assertEqual(agent._summarized_knowledge["cross_level_notes"], "")
        self.assertEqual(NS["OURS_LEVEL_CARRY_COUNTS"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
