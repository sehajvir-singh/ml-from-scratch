"""Build our ARC-AGI-3 Kaggle notebooks from the vendored B81 base.

Base: Thuitanium's `thui-a5-mtp0k7s28-full25-r1` ("B81", MIT-0): the Tufa Labs Duck harness (MIT) with the
animation-aware solver bundle (CC0) on Keith Tyser's Qwen3.8-Flash-Next NVFP4 vLLM stack, served with
KV 7 GiB / MTP off / 28 sequences. Four hidden-set draws: 4.50, 3.86, 3.03, 5.36 (mean 4.19).

Variants:
  base   B81 unchanged apart from the title cell. Our control and fallback.
  m2     B81 + grafts/note_fill.py + grafts/prompt_extras.py (scoring, pacing, click candidates).
  m3     m2 + grafts/keep_on_death.py (keep the world-model note across a GAME_OVER).
  lean   B81 + grafts/note_fill.py only (no extra prompt text; Tufa found handcrafted tools hurt Duck).

Phase A (the "Save & Run All" that must succeed before you can submit) plays the 25 public games offline.
  --phase-a=full   25 games at the production 7,920 s clock (~2.3 GPU-hours; gives a public-25 score)
  --phase-a=smoke  3 games at 1,800 s (~0.6 GPU-hours; checks the build end to end)
The competition rerun (Phase B, the scored run) is identical for both: all hidden games at 7,920 s each.

Usage:
  python build_notebook.py --variant m2 --owner <kaggle-username> [--phase-a smoke] [--no-clicks ...]
Output: out/<slug>/<slug>.ipynb + kernel-metadata.json, ready for `kaggle kernels push -p out/<slug>`.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_NB = HERE / "vendor" / "b81" / "b81.ipynb"
BASE_META = HERE / "vendor" / "b81" / "kernel-metadata.json"
BASE_SHA256 = "d7ca8d98a5ca3d1c0ab8e63302084449450dcb9fbd34137b410359fb6b79a770"
GRAFTS = HERE / "grafts"

IMPORT_ANCHOR = "import inference.agent.tool_agent as _tool_agent\n"
SMOKE_GAMES = ("tn36-ef4dde99", "vc33-5430563c", "bp35-0a0ad940")
SMOKE_CLOCK_S = 1800
C15_EXTRA_OLD = "    if missing or extra:\n"
C15_EXTRA_NEW = "    if missing or (extra and len(PUBLIC_GAME_IDS) == 25):   # smoke: a subset leaves extras by design\n"
C15_SELECT = "    bm.games = [offline_by_id[game_id] for game_id in PUBLIC_GAME_IDS]\n"

CREDITS = """Built on public, openly licensed work (full credit to the authors):
- Solver: Tufa Labs' Duck harness (MIT), Milestone #1 winner — Harold Bessis, Jeroen Cottaar, Isaiah Pressman,
  Andries Smit, Michal Tesnar, Stefano Viel.
- Animation-aware solver bundle `jakobbrggen/taaf-kaggle-source-anim-20260807-anim` (CC0).
- Serving stack by Keith Tyser (Qwen3.8-Flash-Next NVFP4 + pinned vLLM runtime).
- Notebook chassis and the KV 7 GiB / MTP 0 / 28-sequence profile: Thuitanium / Knowless Crew, build
  `thui-a5-mtp0k7s28-full25-r1` (MIT-0). The note-fill graft adapts their `thui-a10` graft.
- Model weights: Qwen3.8-Flash-Next NVFP4 (Qwen Community License 1.0).
Our own code (the graft cell) is released under MIT-0 and CC-BY 4.0."""


def load_base() -> dict:
    raw = BASE_NB.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == BASE_SHA256, f"vendored B81 notebook changed: {digest}"
    nb = json.loads(raw)
    assert "Knowless Crew" in "".join(nb["cells"][0]["source"]), "cell 0 is not the B81 title cell"
    assert IMPORT_ANCHOR in "".join(nb["cells"][9]["source"]), "cell 9 anchor missing"
    return nb


def graft_block(variant: str, flags: dict) -> str:
    if variant == "base":
        return 'print("OURS_GRAFTS none (base variant)", flush=True)\n'
    parts = [
        "# ======== ours: grafts (github.com/sehajvir-singh/ml-from-scratch, arc-prize-2026/agent/grafts) ========\n",
        f"OURS_PROMPT_FLAGS = {flags!r}\n",
    ]
    names = ["note_fill.py"] if variant == "lean" else \
        ["note_fill.py", "prompt_extras.py"] + (["keep_on_death.py"] if variant == "m3" else [])
    for name in names:
        src = (GRAFTS / name).read_text()
        compile(src, name, "exec")
        parts.append(src if src.endswith("\n") else src + "\n")
    parts.append(f'print("OURS_GRAFTS ok variant={variant}", flush=True)\n')
    return "".join(parts)


def title_cell(slug: str, variant: str, phase_a: str, flags: dict) -> str:
    what = (
        "**Variant `base`:** the B81 build unchanged (our control and fallback)."
        if variant == "base"
        else "**Variant `lean`:** B81 plus only the note-fill graft (the world-model note is filled from the model's "
        "reasoning when its visible reply is empty). No extra prompt text."
        if variant == "lean"
        else ("**Variant `m3`:** m2 plus keep-on-death (the world-model note survives a GAME_OVER on the same level).\n\n" if variant == "m3" else "")
        + "**Variant `m2`:** B81 plus three low-risk grafts in cell 9:\n"
        "1. world-model note filled from the model's reasoning when its visible reply is empty;\n"
        "2. the exact scoring rule and per-game time left stated in each turn's prompt;\n"
        f"3. salient, non-HUD click candidates when MOUSE is valid (flags: `{flags}`)."
    )
    phase = (
        "Phase A (Save & Run All) plays 3 public games at 1,800 s as a smoke check."
        if phase_a == "smoke"
        else "Phase A (Save & Run All) plays the 25 public games at the production clock."
    )
    return f"# {slug}\n\n{what}\n\n{phase} The scored competition rerun plays every hidden game at 7,920 s.\n\n" \
           f"**Select the RTX Pro 6000 accelerator, keep internet off.**\n\n{CREDITS}\n"


def apply_smoke(cell15: str) -> str:
    m = re.search(r"PUBLIC_GAME_IDS = tuple\(\[\n(?:    \"[a-z0-9]{4}-[0-9a-f]{8}\",?\n){25}\]\)\n", cell15)
    assert m, "cell 15: the 25-game PUBLIC_GAME_IDS tuple not found"
    assert all(f'"{g}"' in m.group(0) for g in SMOKE_GAMES)
    s = cell15.replace(m.group(0), "PUBLIC_GAME_IDS = tuple(" + repr(list(SMOKE_GAMES)) + ")   # smoke subset\n")
    assert s.count("!= 25") == 2 and s.count(C15_EXTRA_OLD) == 1 and s.count(C15_SELECT) == 1
    s = s.replace("!= 25", "!= len(PUBLIC_GAME_IDS)").replace(C15_EXTRA_OLD, C15_EXTRA_NEW).replace(
        C15_SELECT,
        C15_SELECT + f"    bm.solver.max_runtime_s_per_game = {SMOKE_CLOCK_S}.0   # smoke clock (offline branch only)\n"
        '    print(f"OURS_SMOKE {len(bm.games)} games @ {bm.solver.max_runtime_s_per_game} s", flush=True)\n',
    )
    # the smoke edit must live only in the offline (non-rerun) branch
    rerun_branch = s.split("if TRUE_SUBMISSION:", 1)[1].split("else:", 1)[0]
    assert "OURS_SMOKE" not in rerun_branch and "SMOKE_CLOCK" not in rerun_branch
    return s


def build(variant: str, owner: str, phase_a: str, flags: dict, run: str) -> Path:
    nb = load_base()
    orig = copy.deepcopy(nb)
    cells = nb["cells"]
    suffix = "" if all(flags.values()) or variant in ("base", "lean") else "-" + "".join(k[0] for k, v in flags.items() if v)
    slug = f"arc3-{variant}{suffix}-{phase_a}-r{run}"
    cells[0]["source"] = title_cell(slug, variant, phase_a, flags).splitlines(keepends=True)
    s9 = "".join(cells[9]["source"])
    assert s9.count(IMPORT_ANCHOR) == 1
    cells[9]["source"] = s9.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + graft_block(variant, flags)).splitlines(keepends=True)
    if phase_a == "smoke":
        cells[15]["source"] = apply_smoke("".join(cells[15]["source"])).splitlines(keepends=True)
    for i in (9, 13, 15):
        compile("".join(cells[i]["source"]), f"cell{i}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    changed = [i for i, (a, b) in enumerate(zip(orig["cells"], cells)) if a != b]
    expected = [0, 9] + ([15] if phase_a == "smoke" else [])
    assert changed == expected, (changed, expected)
    assert len(orig["cells"]) == len(cells)
    meta = json.loads(BASE_META.read_text())
    meta.update(id=f"{owner}/{slug}", title=slug, code_file=f"{slug}.ipynb", is_private=True)
    assert meta["machine_shape"] == "NvidiaRtxPro6000" and meta["enable_internet"] is False
    out = HERE / "out" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{slug}.ipynb").write_text(json.dumps(nb, indent=1))
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
    print(f"built {out.relative_to(HERE)}: cells changed {changed}; id {meta['id']}; datasets {meta['dataset_sources']}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", choices=("base", "m2", "m3", "lean"), required=True)
    ap.add_argument("--owner", required=True, help="your Kaggle username (the kernel is created under it)")
    ap.add_argument("--phase-a", choices=("full", "smoke"), default="full")
    ap.add_argument("--run", default="1", help="run tag, so repeated draws get distinct kernel slugs")
    for flag in ("scoring", "pacing", "clicks"):
        ap.add_argument(f"--no-{flag}", action="store_true", help=f"m2 only: disable the {flag} prompt line")
    args = ap.parse_args()
    flags = {f: not getattr(args, f"no_{f}") for f in ("scoring", "pacing", "clicks")}
    build(args.variant, args.owner, args.phase_a, flags, args.run)


if __name__ == "__main__":
    main()
