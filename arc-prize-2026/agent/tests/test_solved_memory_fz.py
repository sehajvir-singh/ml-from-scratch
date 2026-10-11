import os
import types
import unittest
from pathlib import Path

GRAFT = Path(__file__).resolve().parents[1] / "grafts" / "solved_memory_fz.py"


class Frame:
    def __init__(self, level):
        self.level = level


def make_env(mode="system"):
    calls = []
    os.environ["OURS_SM_MODE"] = mode

    class ToolAgent:
        def __init__(self):
            self._system_prompt = "SYS"
            self._history_messages = []

        def _prepare_auto_diff(self, current_frame, previous_step_summary):
            calls.append((current_frame.level, previous_step_summary))
            return ["orig"]

    ns = {"_tool_agent": types.SimpleNamespace(ToolAgent=ToolAgent)}
    exec(compile(GRAFT.read_text(), str(GRAFT), "exec"), ns)
    return ToolAgent, ns, calls


class SolvedMemoryTest(unittest.TestCase):
    def test_pins_winning_attempt_and_resets_on_death(self):
        ToolAgent, ns, calls = make_env()
        a = ToolAgent()
        self.assertEqual(a._prepare_auto_diff(Frame(1), None), ["orig"])
        a._prepare_auto_diff(Frame(1), {"executed_actions": ["UP", "UP"]})
        a._prepare_auto_diff(Frame(1), {"executed_actions": ["LEFT"], "game_over": True})   # death: forget
        a._prepare_auto_diff(Frame(1), {"executed_actions": ["RIGHT", "RIGHT", "RIGHT"]})
        a._prepare_auto_diff(Frame(2), {"executed_actions": ["MOUSE(row=3, col=4)"], "level_transition": True})
        self.assertIn("Level 1 (4 actions): RIGHT x3, MOUSE(row=3, col=4)", a._system_prompt)
        self.assertTrue(a._system_prompt.startswith("SYS\n\n"))
        self.assertNotIn("LEFT", a._system_prompt)
        self.assertNotIn("UP", a._system_prompt)
        # level 2 cleared too: both pinned, base prompt kept once
        a._prepare_auto_diff(Frame(2), {"executed_actions": ["DOWN"]})
        a._prepare_auto_diff(Frame(3), {"executed_actions": ["SPACE"], "level_transition": True})
        self.assertIn("Level 2 (2 actions): DOWN, SPACE", a._system_prompt)
        self.assertEqual(a._system_prompt.count("SYS"), 1)
        self.assertEqual(ns["OURS_SM_COUNTS"]["errors"], 0)
        self.assertEqual(len(calls), 7)   # original called on every turn

    def test_fail_open_and_stale(self):
        ToolAgent, ns, _ = make_env()
        a = ToolAgent()
        a._prepare_auto_diff(Frame(1), {"executed_actions": ["UP"], "stale": True, "level_transition": True})
        self.assertEqual(a._system_prompt, "SYS")
        b = ToolAgent()   # malformed summary must not break the turn
        b._prepare_auto_diff(Frame(1), None)
        self.assertEqual(b._prepare_auto_diff(Frame(1), {"executed_actions": None, "level_transition": True}), ["orig"])
        self.assertEqual(b._system_prompt, "SYS")

    def test_same_summary_counted_once(self):
        ToolAgent, ns, _ = make_env()
        a = ToolAgent()
        a._prepare_auto_diff(Frame(1), None)
        s1 = {"executed_actions": ["UP", "UP"], "start_action_num": 1, "end_action_num": 2, "executed_count": 2}
        a._prepare_auto_diff(Frame(1), s1)
        a._prepare_auto_diff(Frame(1), dict(s1))   # resumed turn, same summary
        a._prepare_auto_diff(Frame(2), {"executed_actions": ["LEFT"], "start_action_num": 3, "end_action_num": 3,
                                        "executed_count": 1, "level_transition": True})
        self.assertIn("Level 1 (3 actions): UP x2, LEFT", a._system_prompt)

    def test_long_level_is_capped(self):
        ToolAgent, ns, _ = make_env()
        a = ToolAgent()
        a._prepare_auto_diff(Frame(1), None)
        a._prepare_auto_diff(Frame(1), {"executed_actions": [f"MOUSE(row={i}, col=1)" for i in range(500)]})
        a._prepare_auto_diff(Frame(2), {"executed_actions": ["UP"], "level_transition": True})
        self.assertIn("501 actions, last 60 shown", a._system_prompt)
        self.assertLess(len(a._system_prompt), 2000)


class AppendModeTest(unittest.TestCase):
    """Default mode: the system prompt never changes (prefix cache); the block rides on the opener lines."""

    def test_shown_once_then_reshown_after_eviction(self):
        ToolAgent, ns, _ = make_env("append")
        a = ToolAgent()
        self.assertEqual(a._prepare_auto_diff(Frame(1), None), ["orig"])
        a._prepare_auto_diff(Frame(1), {"executed_actions": ["UP", "UP"]})
        lines = a._prepare_auto_diff(Frame(2), {"executed_actions": ["LEFT"], "level_transition": True})
        self.assertEqual(lines[0], "orig")
        self.assertIn("Level 1 (3 actions): UP x2, LEFT", lines[-1])
        self.assertEqual(a._system_prompt, "SYS")
        # the opener carrying it is now in history: not repeated
        a._history_messages = [{"role": "user", "content": [{"type": "text", "text": "x\n" + lines[-1]}]}]
        self.assertEqual(a._prepare_auto_diff(Frame(2), {"executed_actions": ["DOWN"]}), ["orig"])
        # trimmed out of history: shown again
        a._history_messages = [{"role": "user", "content": "later turn"}]
        again = a._prepare_auto_diff(Frame(2), {"executed_actions": ["DOWN"]})
        self.assertIn("Level 1 (3 actions)", again[-1])
        self.assertEqual(ns["OURS_SM_COUNTS"]["shown"], 1)
        self.assertEqual(ns["OURS_SM_COUNTS"]["reshown"], 1)
        self.assertEqual(ns["OURS_SM_COUNTS"]["errors"], 0)
        self.assertEqual(a._system_prompt, "SYS")

    def test_nothing_before_first_clear(self):
        ToolAgent, ns, _ = make_env("append")
        a = ToolAgent()
        for _ in range(3):
            self.assertEqual(a._prepare_auto_diff(Frame(1), {"executed_actions": ["UP"]}), ["orig"])
        self.assertEqual(ns["OURS_SM_COUNTS"]["shown"] + ns["OURS_SM_COUNTS"]["reshown"], 0)


if __name__ == "__main__":
    unittest.main()
