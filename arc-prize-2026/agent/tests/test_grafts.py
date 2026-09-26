"""Offline (0-GPU) checks for our notebook builds and grafts.

The grafts are extracted from the BUILT notebook's cell 9 and installed on the REAL solver module
(vendor/anim_solver, the exact tree the Kaggle bundle ships), then driven through ToolAgent.analyze()
with a scripted fake model and a fake environment. The python tool runs in the solver's real sandbox.

Run:  python -m unittest discover -s arc-prize-2026/agent/tests -v
Needs: pillow, requests (the solver imports them).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AGENT = Path(__file__).resolve().parents[1]
SOLVER = AGENT / "vendor" / "anim_solver"
os.environ.setdefault("LOCAL_ANALYZER_BASE_URL", "http://127.0.0.1:9/v1")
os.environ.setdefault("LOCAL_ANALYZER_MODEL_ID", "fake-model")
sys.path.insert(0, str(SOLVER / "ARC3-Inference"))
sys.path.insert(0, str(SOLVER / "tufa-arc-agi-framework" / "src"))

import inference.agent.tool_agent as tool_agent  # noqa: E402
from inference.agent.runtime_state import Frame, HistoryEntry, write_runtime_state, load_runtime_state  # noqa: E402

OWNER = "testowner"
BUILDS = {}


def build(variant: str, phase_a: str, *extra: str) -> Path:
    cmd = [sys.executable, str(AGENT / "build_notebook.py"), "--variant", variant, "--owner", OWNER,
           "--phase-a", phase_a, "--run", "t", *extra]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    line = [l for l in out.splitlines() if l.startswith("built ")][0]
    return AGENT / line.split()[1].rstrip(":")


def cell(nb_dir: Path, index: int) -> str:
    nb = json.loads(next(nb_dir.glob("*.ipynb")).read_text())
    return "".join(nb["cells"][index]["source"])


def graft_block(nb_dir: Path) -> str:
    s9 = cell(nb_dir, 9)
    start = s9.index("# ======== ours: grafts")
    end = s9.index('print("OURS_GRAFTS ok variant=m2", flush=True)\n')
    return s9[start:end]


def setUpModule():
    BUILDS["m2_smoke"] = build("m2", "smoke")
    BUILDS["m2_full"] = build("m2", "full")
    BUILDS["base_full"] = build("base", "full")
    BUILDS["m2_noclicks"] = build("m2", "smoke", "--no-clicks")
    namespace = {"_tool_agent": tool_agent, "__name__": "cell9"}
    exec(compile(graft_block(BUILDS["m2_smoke"]), "cell9-grafts", "exec"), namespace)
    BUILDS["ns"] = namespace


def board(fill=0, objects=()):
    grid = [[fill] * 64 for _ in range(64)]
    for r0, c0, h, w, color in objects:
        for r in range(r0, r0 + h):
            for c in range(c0, c0 + w):
                grid[r][c] = color
    return tuple(tuple(row) for row in grid)


# a white background, a red 3x3 "button", a blue 2x2 token, and a HUD bar along the bottom edge
BOARD = board(0, [(10, 10, 3, 3, 8), (30, 40, 2, 2, 9), (62, 0, 2, 50, 11)])


class FakeModel:
    """Scripted chat completions. Each script entry is (reasoning, content, python_code or None)."""

    def __init__(self, script):
        self.script = list(script)
        self.requests = []

    def __call__(self, agent, messages, *, tools=None, request_timeout_seconds=None):
        self.requests.append(json.loads(json.dumps(messages)))
        reasoning, content, code = self.script.pop(0)
        message = {"role": "assistant", "content": content, "reasoning_content": reasoning}
        if code is not None:
            message["tool_calls"] = [{
                "id": f"call{len(self.requests)}", "type": "function",
                "function": {"name": "python", "arguments": json.dumps({"code": code})},
            }]
        return tool_agent._ChatCompletionResult(message=message, finish_reason="tool_calls" if code else "stop", usage={})


class FakeEnv:
    """Clicks never change the board; each executed action is appended to the runtime history."""

    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.actions = 0

    def __call__(self, request):
        frame, history = load_runtime_state(self.state_path)
        action = request["actions"][0]
        self.actions += 1
        display = f"MOUSE(row={action.get('row')}, col={action.get('col')})" if action.get("action") == "MOUSE" else action.get("action")
        new_frame = Frame(grid=frame.grid, step=frame.step + 1, level=frame.level)
        write_runtime_state(self.state_path, current_frame=new_frame, history=[*history, HistoryEntry(action=display, frame=new_frame)])
        return {
            "executed": True, "action_num": self.actions, "level": 1, "score": 0, "state": "NOT_FINISHED",
            "valid_actions": ["UP", "MOUSE"], "board_changed": False, "done": False, "level_completed": False,
            "game_over": False, "run_complete": False, "action_display": display, "executed_actions": [display],
            "run_elapsed_seconds": 100.0, "time_remaining_seconds": 1500.0,
        }


def last_user_text(messages) -> str:
    content = [m for m in messages if m["role"] == "user"][-1]["content"]
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if part.get("type") == "text")
    return content


class BuildTests(unittest.TestCase):
    def test_cells_changed(self):
        base_nb = json.loads((AGENT / "vendor" / "b81" / "b81.ipynb").read_text())
        for key, expected in (("m2_smoke", [0, 9, 15]), ("m2_full", [0, 9]), ("base_full", [0, 9])):
            nb = json.loads(next(BUILDS[key].glob("*.ipynb")).read_text())
            changed = [i for i, (a, b) in enumerate(zip(base_nb["cells"], nb["cells"])) if a != b]
            self.assertEqual(changed, expected, key)

    def test_base_has_no_grafts(self):
        s9 = cell(BUILDS["base_full"], 9)
        self.assertIn("OURS_GRAFTS none", s9)
        self.assertNotIn("_nf_meta", s9)

    def test_metadata(self):
        meta = json.loads((BUILDS["m2_full"] / "kernel-metadata.json").read_text())
        self.assertTrue(meta["id"].startswith(f"{OWNER}/arc3-m2-full"))
        self.assertEqual(meta["machine_shape"], "NvidiaRtxPro6000")
        self.assertFalse(meta["enable_internet"])
        self.assertIn("jakobbrggen/taaf-kaggle-source-anim-20260807-anim", meta["dataset_sources"])

    def test_smoke_only_touches_offline_branch(self):
        s15 = cell(BUILDS["m2_smoke"], 15)
        rerun_branch = s15.split("if TRUE_SUBMISSION:", 1)[1].split("else:", 1)[0]
        self.assertNotIn("OURS_SMOKE", rerun_branch)
        self.assertIn("bm.games = _competition_games()", rerun_branch)
        full15 = cell(BUILDS["m2_full"], 15)
        self.assertEqual(full15, "".join(json.loads((AGENT / "vendor" / "b81" / "b81.ipynb").read_text())["cells"][15]["source"]))

    def test_flags_are_embedded(self):
        self.assertIn("'clicks': False", cell(BUILDS["m2_noclicks"], 9))


class GraftTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmp.name) / "game" / "tool_runtime_state.json"
        start = Frame(grid=BOARD, step=0, level=1)
        write_runtime_state(self.state_path, current_frame=start, history=[HistoryEntry(action="", frame=start)])
        self.agent = tool_agent.ToolAgent(model="fake-model", hard_noop_guard=False)

    def tearDown(self):
        self.tmp.cleanup()

    def run_turns(self, script):
        fake = FakeModel(script)
        env = FakeEnv(self.state_path)
        original = tool_agent.ToolAgent._chat_completion
        tool_agent.ToolAgent._chat_completion = lambda agent, messages, **kw: fake(agent, messages, **kw)
        try:
            for turn in range(len(script)):
                self.agent.analyze(self.state_path, env.actions, valid_actions=["UP", "MOUSE"], step_env=env, analysis_step=turn)
        finally:
            tool_agent.ToolAgent._chat_completion = original
        return fake, env

    def test_end_to_end_prompt_and_note(self):
        click = "action([{'action': 'MOUSE', 'row': 11, 'col': 11}])"
        reasoning = "World model: the red 3x3 square is a button.\nGoal model: make the blue token red.\nPlan: click the red button."
        fake, env = self.run_turns([(reasoning, "", click), ("", "", click), ("", "", click)])
        self.assertEqual(env.actions, 3, "the sandboxed python tool must execute the scripted clicks")

        first = last_user_text(fake.requests[0])
        self.assertIn("Scoring (exact): a cleared level scores min(1.15", first)
        self.assertIn("Actions spent on this level: 0.", first)
        self.assertIn("Click candidates", first)
        self.assertIn("(row=11, col=11) Rx9", first, "the red 3x3 button should be a candidate at its center")
        self.assertIn("(row=30, col=40) bx4", first)
        self.assertNotIn("Yx100", first, "the HUD bar along the bottom edge must be excluded")

        second = last_user_text(fake.requests[1])
        self.assertIn("World model: the red 3x3 square is a button.", second, "note must be filled from reasoning")
        self.assertIn("Plan: click the red button.", second)
        self.assertIn("Time left for this game: about 25 min.", second)
        self.assertIn("Actions spent on this level: 1.", second)

        third = last_user_text(fake.requests[2])
        self.assertIn("Actions spent on this level: 2.", third)
        self.assertIn("Clicked on this level 2+ times with no visible board change (omitted above): Rx9.", third)
        self.assertNotIn("(row=11, col=11) Rx9", third, "a dead click class is dropped from the candidates")

        counts = BUILDS["ns"]["OURS_PROMPT_COUNTS"]
        self.assertEqual(counts["errors"], 0)
        self.assertEqual(BUILDS["ns"]["OURS_NOTE_FILL_COUNTS"]["errors"], 0)
        self.assertGreaterEqual(BUILDS["ns"]["OURS_NOTE_FILL_COUNTS"]["responses_filled"], 1)

    def test_visible_note_wins_over_reasoning(self):
        reasoning = "World model: from thinking.\nPlan: thinking plan."
        content = "Plan: visible plan."
        fake, _ = self.run_turns([(reasoning, content, "action(['UP'])"), ("", "", "action(['UP'])")])
        second = last_user_text(fake.requests[1])
        self.assertIn("World model: from thinking.", second)
        self.assertIn("Plan: visible plan.", second)
        self.assertNotIn("thinking plan", second)

    def test_no_mouse_no_candidates(self):
        prompt = self.agent._build_user_prompt(0, valid_actions=["UP", "DOWN"], current_frame=Frame(BOARD, 0, 1), history_entries=[])
        self.assertIn("Scoring (exact)", prompt)
        self.assertNotIn("Click candidates", prompt)

    def test_fail_open_on_bad_frame(self):
        before = BUILDS["ns"]["OURS_PROMPT_COUNTS"]["errors"]

        class Broken:
            level = 1
            step = 0

            @property
            def grid(self):
                raise RuntimeError("boom")

            @property
            def ascii(self):
                return ""

        prompt = tool_agent.ToolAgent._build_user_prompt.__wrapped__(self.agent, 0, valid_actions=["MOUSE"], current_frame=Frame(BOARD, 0, 1), history_entries=[])
        wrapped = self.agent._build_user_prompt(0, valid_actions=["MOUSE"], current_frame=Broken(), history_entries=[])
        self.assertTrue(wrapped.startswith(prompt.split("\n")[0]))
        self.assertEqual(BUILDS["ns"]["OURS_PROMPT_COUNTS"]["errors"], before + 1)

    def test_engine_action_names_and_edge_buttons(self):
        # the solver passes engine names; a 4x4 button flush with the right edge is a candidate, a 1-row bar is not
        grid = board(0, [(24, 60, 4, 4, 9), (0, 0, 1, 64, 7)])
        prompt = self.agent._build_user_prompt(0, valid_actions=["ACTION6"], current_frame=Frame(grid, 0, 1), history_entries=[])
        self.assertIn("Click candidates", prompt)
        self.assertIn("bx16", prompt)
        self.assertNotIn("Px64", prompt)

    def test_keep_on_death(self):
        m3 = build("m3", "smoke")
        s9 = cell(m3, 9)
        self.assertIn("OURS_KEEP_ON_DEATH ok", s9)
        self.assertIn('OURS_GRAFTS ok variant=m3', s9)
        ns = BUILDS.setdefault("kd_ns", {"_tool_agent": tool_agent, "__name__": "kd"})
        if "OURS_KEEP_ON_DEATH_COUNTS" not in ns:
            exec(compile((AGENT / "grafts" / "keep_on_death.py").read_text(), "keep_on_death", "exec"), ns)
        agent = self.agent
        agent._summarized_knowledge["world_model"] = "red square is the player"
        agent._last_step_summary = {"game_over": True, "level_transition": False, "run_complete": False}
        agent._update_summarized_knowledge_from_step_summary()
        self.assertEqual(agent._summarized_knowledge["world_model"], "red square is the player")
        self.assertIn("GAME_OVER", agent._summarized_knowledge["recent_findings"])
        agent._last_step_summary = {"game_over": False, "level_transition": True, "run_complete": False}
        agent._update_summarized_knowledge_from_step_summary()
        self.assertEqual(agent._summarized_knowledge["world_model"], "", "a real level transition still wipes")
        self.assertEqual(ns["OURS_KEEP_ON_DEATH_COUNTS"]["errors"], 0)

    def test_stall_hint(self):
        frame = Frame(BOARD, 200, 1)
        history = [HistoryEntry(action="UP", frame=frame) for _ in range(160)]
        prompt = self.agent._build_user_prompt(160, valid_actions=["UP"], current_frame=frame, history_entries=history)
        self.assertIn("Actions spent on this level: 160.", prompt)
        self.assertIn("test a different hypothesis", prompt)


if __name__ == "__main__":
    unittest.main()
