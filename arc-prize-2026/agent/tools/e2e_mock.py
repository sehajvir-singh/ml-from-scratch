"""End-to-end smoke of the REAL solver on REAL public games with a mock model (0 GPU).

Starts a tiny OpenAI-compatible server that answers every chat request with a random valid action written as a
python tool call (plus labelled world-model lines in the reasoning), installs the grafts from a BUILT notebook's
cell 9 onto the real solver, and runs `inference.framework.run` inline against local environment_files. This
verifies mechanics only -- that the grafts survive real frames, real histories, level transitions and the
sandboxed python tool -- never score.

Usage (Python 3.12 venv with arc_agi 0.9.9 + arcengine 0.9.3 + matplotlib/numpy/scipy/pillow/requests/dotenv):
  python tools/e2e_mock.py --notebook out/<slug> --env-dir <environment_files> --games ls20,vc33 \
      --max-actions 25 [--competition]
Writes the prompts it received to <run dir>/mock_prompts.jsonl and prints a summary.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AGENT = Path(__file__).resolve().parents[1]
SOLVER = AGENT / "vendor" / "anim_solver"

ACTION_CODE = """
import random
va = [a for a in valid_actions if a != 'RESET']
a = random.choice(va) if va else 'RESET'
if a == 'MOUSE':
    nodes = current_frame.segmentation['nodes']
    node = random.choice(nodes)
    r, c = node['boundary'][0]
    r, c = min(max(int(r), 0), 63), min(max(int(c), 0), 63)
    res = action([{'action': 'MOUSE', 'row': r, 'col': c}])
else:
    res = action([a])
print({k: res.get('action_result', res).get(k) for k in ('executed', 'board_changed', 'level')})
"""

PROMPTS: list[dict] = []
LOCK = threading.Lock()


class MockHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silence
        pass

    def do_GET(self):
        body = json.dumps({"data": [{"id": "mock-model", "object": "model"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length) or b"{}")
        messages = request.get("messages", [])
        users = [m for m in messages if m.get("role") == "user"]
        last = users[-1]["content"] if users else ""
        if isinstance(last, list):
            last = "\n".join(p.get("text", "") for p in last if p.get("type") == "text")
        with LOCK:
            PROMPTS.append({"n_messages": len(messages), "user": last})
            n = len(PROMPTS)
        reasoning = (
            f"World model: mock hypothesis #{n}.\nGoal model: unknown yet.\n"
            f"Plan: probe a random valid action (request {n})."
        )
        message = {
            "role": "assistant",
            "content": "",
            "reasoning_content": reasoning,
            "tool_calls": [{
                "id": f"call_{n}",
                "type": "function",
                "function": {"name": "python", "arguments": json.dumps({"code": ACTION_CODE})},
            }],
        }
        body = json.dumps({
            "id": f"mock-{n}", "object": "chat.completion", "model": "mock-model",
            "choices": [{"index": 0, "message": message, "finish_reason": "tool_calls"}],
            "usage": {"prompt_tokens": 1000, "completion_tokens": 50, "total_tokens": 1050},
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)


def graft_block(nb_dir: Path) -> str:
    nb = json.loads(next(nb_dir.glob("*.ipynb")).read_text())
    s9 = "".join(nb["cells"][9]["source"])
    if "# ======== ours: grafts" not in s9:
        return ""
    start = s9.index("# ======== ours: grafts")
    end = s9.index('print("OURS_GRAFTS ok variant=m2", flush=True)\n')
    return s9[start:end]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebook", required=True, type=Path, help="a built out/<slug> directory")
    ap.add_argument("--env-dir", required=True, type=Path)
    ap.add_argument("--games", default="ls20,vc33")
    ap.add_argument("--max-actions", type=int, default=25)
    ap.add_argument("--minutes", type=float, default=5.0)
    ap.add_argument("--competition", action="store_true", help="use TAAF's local competition-Arcade simulator")
    ap.add_argument("--run-dir", type=Path, default=AGENT / "out" / "e2e")
    args = ap.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", 0), MockHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    os.environ.update({
        "LOCAL_ANALYZER_BASE_URL": f"http://127.0.0.1:{port}/v1",
        "LOCAL_ANALYZER_MODEL_ID": "mock-model",
        "LOCAL_ANALYZER_PROVIDER": "vllm",
        "MULTIMODAL_CONTEXT": "",
        "ONLY_RESET_LEVELS": "true",
        "TAAF_MINIMAL_DIAGNOSTICS": "1",
    })
    sys.path[:0] = [str(SOLVER / "ARC3-Inference"), str(SOLVER / "tufa-arc-agi-framework" / "src")]
    random.seed(0)

    import inference.agent.tool_agent as _tool_agent  # noqa: F401  (grafts expect this name)

    block = graft_block(args.notebook)
    namespace = {"_tool_agent": _tool_agent, "__name__": "cell9"}
    if block:
        exec(compile(block, "cell9-grafts", "exec"), namespace)
    else:
        print("E2E: base notebook, no grafts installed", flush=True)

    from inference.framework import run as solver_run

    args.run_dir.mkdir(parents=True, exist_ok=True)
    argv = [
        "run", "--model", "mock-model", "--deployment-target", "inline", "--timeout", "60",
        "--game", args.games, "--environments-dir", str(args.env_dir),
        "--max-actions", str(args.max_actions), "--max-runtime-minutes", str(args.minutes),
        "--n-passes", "1", "--concurrent-jobs", "2",
        "--experiments-dir", str(args.run_dir), "--run-name", "mock",
    ]
    if args.competition:
        argv.append("--simulate-competition-arcade")
    sys.argv = argv
    try:
        solver_run.main()
    finally:
        server.shutdown()
        (args.run_dir / "mock_prompts.jsonl").write_text("".join(json.dumps(p) + "\n" for p in PROMPTS))
        counts = {k: v for k, v in namespace.items() if k.startswith("OURS_") and k.endswith("_COUNTS")}
        with_extras = sum("Scoring (exact)" in p["user"] for p in PROMPTS)
        with_clicks = sum("Click candidates" in p["user"] for p in PROMPTS)
        with_note = sum("World model: mock hypothesis" in p["user"] for p in PROMPTS)
        print(f"E2E_SUMMARY requests={len(PROMPTS)} with_scoring={with_extras} with_clicks={with_clicks} "
              f"with_note={with_note} counts={counts}", flush=True)


if __name__ == "__main__":
    main()
