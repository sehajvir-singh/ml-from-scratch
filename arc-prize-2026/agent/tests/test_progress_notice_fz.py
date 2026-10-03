import os
import types
import unittest
from pathlib import Path

GRAFTS = Path(__file__).resolve().parents[1] / "grafts"


class Frame:
    def __init__(self, level, board=0):
        self.level = level
        self.grid = ((board,),)


def make_env(*names, **env):
    os.environ.update({"OURS_SM_MODE": "append", **env})

    class ToolAgent:
        def __init__(self):
            self._system_prompt = "SYS"
            self._history_messages = []

        def _prepare_auto_diff(self, current_frame, previous_step_summary):
            return ["orig"]

    ns = {"_tool_agent": types.SimpleNamespace(ToolAgent=ToolAgent)}
    for name in names:
        exec(compile((GRAFTS / f"{name}.py").read_text(), name, "exec"), ns)
    return ToolAgent, ns


def turn(i, n=10, **kw):
    return {"executed_actions": ["UP"] * n, "start_action_num": i * n, "end_action_num": i * n + n - 1,
            "executed_count": n, **kw}


class ProgressNoticeTest(unittest.TestCase):
    def test_doubling_thresholds_and_level_reset(self):
        ToolAgent, ns = make_env("progress_notice_fz", OURS_PN_ACTIONS="40", OURS_PN_STALE_TURNS="99")
        a = ToolAgent()
        a._prepare_auto_diff(Frame(1, 0), None)
        shown = []
        for i in range(1, 9):   # 80 actions on level 1, new board every turn
            out = a._prepare_auto_diff(Frame(1, i), turn(i))
            shown.append(len(out) > 1)
        self.assertEqual([i + 1 for i, s in enumerate(shown) if s], [4, 8])   # at 40 and 80 actions
        last = a._prepare_auto_diff(Frame(1, 9), turn(9))
        self.assertEqual(last, ["orig"])
        # level 2: counters restart, level-transition actions are not counted
        out = a._prepare_auto_diff(Frame(2, 100), turn(10, level_transition=True))
        self.assertEqual(out, ["orig"])
        self.assertEqual(a._ours_pn["actions"], 0)
        self.assertEqual(ns["OURS_PN_COUNTS"]["errors"], 0)

    def test_stale_board_once_and_text_is_facts(self):
        ToolAgent, ns = make_env("progress_notice_fz", OURS_PN_ACTIONS="1000", OURS_PN_STALE_TURNS="3")
        a = ToolAgent()
        a._prepare_auto_diff(Frame(1, 0), None)
        outs = [a._prepare_auto_diff(Frame(1, 0), turn(i, n=2, game_over=(i == 2))) for i in range(1, 7)]
        notes = [o[-1] for o in outs if len(o) > 1]
        self.assertEqual(len(notes), 1)
        self.assertIn("1 game over(s)", notes[0])
        self.assertIn("1 distinct boards", notes[0])
        for word in ("should", "try", "consider", "must"):
            self.assertNotIn(word, notes[0].lower())
        # a new board re-arms the stale notice
        a._prepare_auto_diff(Frame(1, 5), turn(7, n=2))
        outs = [a._prepare_auto_diff(Frame(1, 5), turn(i, n=2)) for i in range(8, 12)]
        self.assertEqual(sum(len(o) > 1 for o in outs), 1)

    def test_resumed_summary_counted_once_and_fail_open(self):
        ToolAgent, ns = make_env("progress_notice_fz", OURS_PN_ACTIONS="1000", OURS_PN_STALE_TURNS="99")
        a = ToolAgent()
        a._prepare_auto_diff(Frame(1, 0), None)
        s = turn(1)
        a._prepare_auto_diff(Frame(1, 1), s)
        a._prepare_auto_diff(Frame(1, 1), dict(s))
        self.assertEqual(a._ours_pn["actions"], 10)
        self.assertEqual(a._prepare_auto_diff(None, {"executed_actions": 5}), ["orig"])

    def test_stacks_with_solved_memory(self):
        ToolAgent, ns = make_env("solved_memory_fz", "progress_notice_fz", OURS_PN_ACTIONS="10",
                                 OURS_PN_STALE_TURNS="99")
        a = ToolAgent()
        a._prepare_auto_diff(Frame(1, 0), None)
        a._prepare_auto_diff(Frame(1, 1), turn(1, n=3))
        out = a._prepare_auto_diff(Frame(2, 2), turn(2, n=1, level_transition=True))
        self.assertTrue(any("Solved levels" in x for x in out))
        out = a._prepare_auto_diff(Frame(2, 3), turn(3, n=12))
        self.assertTrue(out[-1].startswith("Progress count (harness, level 2): 12 actions"))
        self.assertEqual(ns["OURS_PN_COUNTS"]["errors"] + ns["OURS_SM_COUNTS"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
