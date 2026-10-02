"""Build a variant of Franzen's Milestone #2 notebook that changes only its configuration.

    python3 tools/fz_variant.py NAME [--set KEY=VALUE ...] [--server KEY=VALUE ...] [--graft NAME ...] [--minutes 25] [--all-games]

Reads the unchanged copy pulled by `tools/adopt.py dfranzen/arc-agi-3-milestone-2-solution --no-grafts`
(out/adopt-arc-agi-3-milestone-2-solution) and writes out/fz-NAME/, ready for `kaggle kernels push -p out/fz-NAME`.

What changes, and nothing else:
  --set KEY=VALUE   harness environment overrides (e.g. EXPOSE_RESET=on, ARC3_LEVEL_INVENTORY=1). They are applied
                    after the notebook's own settings, so they hold in Phase A AND in the scored rerun.
  --server KEY=VALUE  model-server overrides of the notebook's CFG dict (e.g. MAXREQ=12, MAMBA_CACHE=72,
                    MEMFRAC=0.97, CUDAGRAPH_MAXBS=12). Values are Python literals. Applies to Phase A AND the rerun.
  --graft NAME      add one of our grafts for Franzen's harness (grafts/NAME.py, e.g. solved_memory_fz) at the top of
                    the customization cell. Each runs in try/except and prints OURS_<NAME> ok|skipped. Applies to both.
  --minutes M       Phase A only: minutes per demo game (default 25, as in Franzen's own demo run).
  --all-games       Phase A only: play all 25 public games instead of his 10-game demo subset.
The default Phase A (10 demo games, 25 min) is directly comparable with Franzen's run (mean 36.56) and ours.
Read results with: python3 tools/fz_results.py out/logs-fz-NAME [more runs ...]
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SRC = HERE / "out" / "adopt-arc-agi-3-milestone-2-solution"
ENV_ANCHOR = "os.environ.update({k: str(v) for k,v in setup_env.items()})"
DEMO_MINUTES = "bm.solver.max_runtime_s_per_game = 25*60"
DEMO_EXCLUDED = "demo_excluded_games = [] if TRUE_SUBMISSION else ["
SERVER_ANCHOR = 'VENV = f"{PREFIX}/venv"'
PATHS_ANCHOR = "SERVED_MODEL_NAME = 'flashnext'"
# Two Phase A runs (fz-inventory, fz-reset2) died in 6 s because /kaggle/input/datasets/dfranzen/... was not there.
# This guard waits briefly for late mounts, falls back to any directory with the same slug, and otherwise prints
# what IS mounted, so the failure is diagnosable. Inserted in every variant.
PATHS_GUARD = r"""
# ---- ours: input-path guard (tools/fz_variant.py) ----
def _ours_resolve(path, wait_s=120):
    import glob as _g, os as _o, time as _t
    slug = path.rstrip('/').split('/datasets/')[-1].split('/')[-1] if '/datasets/' in path else None
    t0 = _t.time()
    while True:
        if _o.path.exists(path):
            return path
        if slug:
            hits = [h for h in _g.glob('/kaggle/input/**/' + slug, recursive=True) if _o.path.isdir(h)]
            if hits:
                print('OURS_PATH fallback', path, '->', hits[0], flush=True)
                return hits[0]
        if _t.time() - t0 > wait_s:
            print('OURS_PATH missing', path, '| /kaggle/input has:', sorted(_g.glob('/kaggle/input/*/*'))[:40], flush=True)
            return path
        _t.sleep(10)
WHEELHOUSE_DIR = _ours_resolve(WHEELHOUSE_DIR)
ORIG_BUNDLE_DIR = _ours_resolve(ORIG_BUNDLE_DIR)
MODEL_DIR = _ours_resolve(MODEL_DIR)
DRAFT_MODEL_DIR = _ours_resolve(DRAFT_MODEL_DIR)
"""


def build(name: str, sets: dict[str, str], minutes: int, all_games: bool, owner: str,
          server: dict | None = None, grafts: list[str] | None = None) -> Path:
    nb_path = next(SRC.glob("*.ipynb"))
    nb = json.loads(nb_path.read_text())
    meta = json.loads((SRC / "kernel-metadata.json").read_text())
    cells = nb["cells"]
    env_i = next(i for i, c in enumerate(cells) if ENV_ANCHOR in "".join(c["source"]))
    cfg_i = next(i for i, c in enumerate(cells) if DEMO_MINUTES in "".join(c["source"]))

    changed = []
    p_i = next(i for i, c in enumerate(cells) if PATHS_ANCHOR in "".join(c["source"]))
    s = "".join(cells[p_i]["source"])
    assert s.count(PATHS_ANCHOR) == 1
    cells[p_i]["source"] = s.replace(PATHS_ANCHOR, PATHS_ANCHOR + "\n" + PATHS_GUARD).splitlines(keepends=True)
    changed.append(p_i)
    if server:
        srv_i = next(i for i, c in enumerate(cells) if SERVER_ANCHOR in "".join(c["source"]))
        s = "".join(cells[srv_i]["source"])
        assert s.count(SERVER_ANCHOR) == 1 and "CFG = dict(" in s
        unknown = [k for k in server if not re.search(rf"^\s+{k}=", s, re.M)]
        assert not unknown, f"not in the notebook's CFG: {unknown}"
        block = ("# ---- ours: server overrides (tools/fz_variant.py) ----\n"
                 f"CFG.update({server!r})\n"
                 f"print('OURS_FZ_SERVER {name}', {server!r}, flush=True)\n")
        cells[srv_i]["source"] = s.replace(SERVER_ANCHOR, block + SERVER_ANCHOR).splitlines(keepends=True)
        changed.append(srv_i)
    if sets:
        s = "".join(cells[env_i]["source"])
        assert s.count(ENV_ANCHOR) == 1
        block = ("# ---- ours: configuration overrides (tools/fz_variant.py) ----\n"
                 f"setup_env.update({json.dumps(sets)})\n"
                 f"print('OURS_FZ_VARIANT {name}', {json.dumps(sets)}, flush=True)\n")
        cells[env_i]["source"] = s.replace(ENV_ANCHOR, block + ENV_ANCHOR).splitlines(keepends=True)
        changed.append(env_i)
    if grafts:
        s = "".join(cells[cfg_i]["source"])
        block = ["# ---- ours: grafts for Franzen's harness (tools/fz_variant.py) ----\n",
                 "import inference.agent.tool_agent as _tool_agent\n"]
        for g in grafts:
            src = (HERE / "grafts" / f"{g}.py").read_text()
            compile(src, g, "exec")
            block.append(f"try:\n    exec(compile({src!r}, {g + '.py'!r}, 'exec'), globals())\n"
                         f"except Exception as _ours_exc:\n"
                         f"    print('OURS_{g.upper()} skipped', type(_ours_exc).__name__, _ours_exc, flush=True)\n")
        cells[cfg_i]["source"] = ("".join(block) + "\n" + s).splitlines(keepends=True)
        changed.append(cfg_i)
    if minutes != 25 or all_games:
        s = "".join(cells[cfg_i]["source"])
        assert s.count(DEMO_MINUTES) == 1
        s = s.replace(DEMO_MINUTES, f"bm.solver.max_runtime_s_per_game = {minutes}*60")
        if all_games:
            assert s.count(DEMO_EXCLUDED) == 1
            s = re.sub(r"demo_excluded_games = \[\] if TRUE_SUBMISSION else \[[^\]]*\]",
                       "demo_excluded_games = []", s)
        cells[cfg_i]["source"] = s.splitlines(keepends=True)
        changed.append(cfg_i)
    for i in set(changed):   # syntax check; IPython "!" and "%" lines become "pass"
        code = re.sub(r"(?m)^(\s*)[!%].*$", r"\1pass", "".join(cells[i]["source"]))
        compile(code.replace("await ", ""), f"cell{i}", "exec")

    slug = f"fz-{name}"
    out = HERE / "out" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / nb_path.name).write_text(json.dumps(nb, indent=1))
    m = dict(meta, id=f"{owner}/{slug}", title=slug, code_file=nb_path.name, is_private=True,
             machine_shape="NvidiaRtxPro6000", enable_gpu=True, enable_internet=False)
    m.pop("id_no", None)
    (out / "kernel-metadata.json").write_text(json.dumps(m, indent=2))
    print(f"built out/{slug}: cells changed {sorted(set(changed))}; overrides {sets or 'none'}; server {server or 'none'}; grafts {grafts or 'none'}; "
          f"Phase A {'25' if all_games else '10'} games x {minutes} min")
    print(f"push:   kaggle kernels push -p out/{slug}")
    print(f"status: kaggle kernels status {owner}/{slug}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="short variant name, e.g. reset")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--server", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--graft", action="append", default=[], metavar="NAME")
    ap.add_argument("--minutes", type=int, default=25)
    ap.add_argument("--all-games", action="store_true")
    ap.add_argument("--owner", default=None, help="Kaggle username (default: from ~/.kaggle/kaggle.json)")
    args = ap.parse_args()
    if not SRC.is_dir():
        sys.exit("Run first: python3 tools/adopt.py dfranzen/arc-agi-3-milestone-2-solution --no-grafts")
    if not re.fullmatch(r"[a-z0-9-]{1,40}", args.name):
        sys.exit("name: lowercase letters, digits and dashes only")
    sets = dict(kv.split("=", 1) for kv in args.set)
    server = {k: ast.literal_eval(v) for k, v in (kv.split("=", 1) for kv in args.server)}
    owner = args.owner or json.loads((Path.home() / ".kaggle" / "kaggle.json").read_text())["username"]
    for g in args.graft:
        if not (HERE / "grafts" / f"{g}.py").is_file():
            sys.exit(f"no graft grafts/{g}.py")
    build(args.name, sets, args.minutes, args.all_games, owner, server, args.graft)


if __name__ == "__main__":
    main()
