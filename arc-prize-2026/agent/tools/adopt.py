"""Adopt a published Kaggle notebook (e.g. a top team's Milestone #2 release) and add our grafts to it.

    python3 tools/adopt.py <owner>/<kernel-slug> [--variant d3|d2|d1|lean] [--no-grafts] [--run 1]

Steps:
  1. `kaggle kernels pull -m` the notebook and its metadata into out/adopt-<slug>/.
  2. Report what it runs: model, datasets, accelerator, whether it uses the Duck/TAAF solver.
  3. If the Duck `tool_agent` import anchor is present, paste our grafts right after it (default: the Depth
     Engine, variant d3). Each graft is wrapped so that if the published harness changed the internals it
     patches, that graft prints OURS_<NAME> skipped and switches itself off instead of crashing the notebook.
     Without an anchor the notebook is left unchanged and the tool says so.
  4. Rewrite the metadata to your account (private) so `kaggle kernels push -p out/adopt-<slug>-ours` works.
Always push the UNCHANGED copy (out/adopt-<slug>) once as a control: a published notebook's own score
is the baseline our grafts must beat.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import build_notebook  # noqa: E402

ANCHORS = (
    "import inference.agent.tool_agent as _tool_agent\n",
    "import inference.agent.tool_agent\n",
    "from inference.agent import tool_agent\n",
)


GRAFTS = {
    "lean": ["note_fill.py"],
    "d1": ["note_fill.py", "affordance.py"],
    "d2": ["note_fill.py", "affordance.py", "level_carry.py"],
    "d3": ["note_fill.py", "affordance.py", "level_carry.py", "stall_breaker.py"],
}


def safe_graft_block(variant: str) -> str:
    """Each graft runs in its own try/except, so one that no longer matches the published harness is skipped."""
    parts = ["# ======== ours: grafts (github.com/sehajvir-singh/ml-from-scratch, arc-prize-2026/agent/grafts) ========\n"]
    for name in GRAFTS[variant]:
        src = (build_notebook.GRAFTS / name).read_text()
        compile(src, name, "exec")
        tag = name[:-3].upper()
        parts.append(
            f"try:\n    exec(compile({src!r}, {name!r}, 'exec'), globals())\n"
            f"except Exception as _ours_exc:\n    print('OURS_{tag} skipped', type(_ours_exc).__name__, _ours_exc, flush=True)\n"
        )
    parts.append(f'print("OURS_GRAFTS ok variant={variant} (adopted)", flush=True)\n')
    return "".join(parts)


def username() -> str:
    cfg = Path.home() / ".kaggle" / "kaggle.json"
    return json.loads(cfg.read_text())["username"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("kernel", help="owner/slug of the published notebook")
    ap.add_argument("--variant", default="d3", choices=("d3", "d2", "d1", "lean"),
                    help="which graft set to add (default d3: note_fill + affordance + level_carry + stall_breaker)")
    ap.add_argument("--no-grafts", action="store_true")
    ap.add_argument("--run", default="1")
    args = ap.parse_args()
    owner, slug = args.kernel.split("/", 1)
    src = HERE / "out" / f"adopt-{slug}"
    src.mkdir(parents=True, exist_ok=True)
    subprocess.run(["kaggle", "kernels", "pull", args.kernel, "-p", str(src), "-m"], check=True)
    nb_path = next(src.glob("*.ipynb"))
    nb = json.loads(nb_path.read_text())
    meta = json.loads((src / "kernel-metadata.json").read_text())
    text = "\n".join("".join(c["source"]) for c in nb["cells"])

    print("\n== What it runs ==")
    print("accelerator:", meta.get("machine_shape") or meta.get("accelerator"))
    print("datasets:", meta.get("dataset_sources"))
    print("models:", meta.get("model_sources"))
    models = sorted(set(re.findall(r"Qwen[\w./-]+|gemma[\w./-]+|gpt-oss[\w./-]+", text)))
    print("model names seen:", models[:10])
    print("uses Duck/TAAF solver:", "inference.agent" in text or "taaf" in text)

    me = username()
    for variant, graft in (("", False), ("-ours", not args.no_grafts)):
        out = HERE / "out" / f"adopt-{slug}{variant}"
        out.mkdir(parents=True, exist_ok=True)
        new = json.loads(json.dumps(nb))
        applied = False
        if graft:
            block = safe_graft_block(args.variant)
            for cell in new["cells"]:
                s = "".join(cell["source"])
                anchor = next((a for a in ANCHORS if a in s), None)
                if anchor and cell["cell_type"] == "code":
                    if anchor != build_notebook.IMPORT_ANCHOR:
                        block = f"_tool_agent = __import__('inference.agent.tool_agent', fromlist=['x'])\n" + block
                    cell["source"] = s.replace(anchor, anchor + block, 1).splitlines(keepends=True)
                    applied = True
                    break
            if not applied:
                print(f"\n!! no tool_agent import anchor found; {out.name} is left unchanged. Send the notebook to Claude.")
        name = f"adopt-{slug[:30]}{variant}-r{args.run}"
        # A pulled kernel's metadata may omit the accelerator; the scored rerun needs the RTX Pro 6000, offline.
        m = dict(meta, id=f"{me}/{name}", title=name, code_file=nb_path.name, is_private=True,
                 machine_shape="NvidiaRtxPro6000", enable_gpu=True, enable_internet=False)
        m.pop("id_no", None)   # the source kernel's numeric id would point the push at the owner's kernel
        (out / nb_path.name).write_text(json.dumps(new, indent=1))
        (out / "kernel-metadata.json").write_text(json.dumps(m, indent=2))
        print(f"built {out.relative_to(HERE)} (grafts {'applied' if applied else 'none'}) -> kaggle kernels push -p {out}")


if __name__ == "__main__":
    main()
