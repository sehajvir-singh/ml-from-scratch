"""Adopt a published Kaggle notebook (e.g. a top team's Milestone #2 release) and add our grafts to it.

    python3 tools/adopt.py <owner>/<kernel-slug> [--no-grafts] [--run 1]

Steps:
  1. `kaggle kernels pull -m` the notebook and its metadata into out/adopt-<slug>/.
  2. Report what it runs: model, datasets, accelerator, whether it uses the Duck/TAAF solver.
  3. If the Duck `tool_agent` import anchor is present, paste our grafts right after it
     (same code as build_notebook.py's m2 variant); otherwise leave the notebook unchanged and say so.
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


def username() -> str:
    cfg = Path.home() / ".kaggle" / "kaggle.json"
    return json.loads(cfg.read_text())["username"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("kernel", help="owner/slug of the published notebook")
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
            flags = {"scoring": True, "pacing": True, "clicks": True}
            block = build_notebook.graft_block("m2", flags)
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
        name = f"adopt-{slug[:40]}{variant}-r{args.run}"
        m = dict(meta, id=f"{me}/{name}", title=name, code_file=nb_path.name, is_private=True)
        (out / nb_path.name).write_text(json.dumps(new, indent=1))
        (out / "kernel-metadata.json").write_text(json.dumps(m, indent=2))
        print(f"built {out.relative_to(HERE)} (grafts {'applied' if applied else 'none'}) -> kaggle kernels push -p {out}")


if __name__ == "__main__":
    main()
