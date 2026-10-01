"""Build a variant of Franzen's Milestone #2 notebook that changes only its configuration.

    python3 tools/fz_variant.py NAME [--set KEY=VALUE ...] [--minutes 25] [--all-games]

Reads the unchanged copy pulled by `tools/adopt.py dfranzen/arc-agi-3-milestone-2-solution --no-grafts`
(out/adopt-arc-agi-3-milestone-2-solution) and writes out/fz-NAME/, ready for `kaggle kernels push -p out/fz-NAME`.

What changes, and nothing else:
  --set KEY=VALUE   harness environment overrides (e.g. EXPOSE_RESET=on, ARC3_LEVEL_INVENTORY=1). They are applied
                    after the notebook's own settings, so they hold in Phase A AND in the scored rerun.
  --minutes M       Phase A only: minutes per demo game (default 25, as in Franzen's own demo run).
  --all-games       Phase A only: play all 25 public games instead of his 10-game demo subset.
The default Phase A (10 demo games, 25 min) is directly comparable with Franzen's run (mean 36.56) and ours.
Read results with: python3 tools/depth_ladder.py out/logs-fz-NAME/*.log
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SRC = HERE / "out" / "adopt-arc-agi-3-milestone-2-solution"
ENV_ANCHOR = "os.environ.update({k: str(v) for k,v in setup_env.items()})"
DEMO_MINUTES = "bm.solver.max_runtime_s_per_game = 25*60"
DEMO_EXCLUDED = "demo_excluded_games = [] if TRUE_SUBMISSION else ["


def build(name: str, sets: dict[str, str], minutes: int, all_games: bool, owner: str) -> Path:
    nb_path = next(SRC.glob("*.ipynb"))
    nb = json.loads(nb_path.read_text())
    meta = json.loads((SRC / "kernel-metadata.json").read_text())
    cells = nb["cells"]
    env_i = next(i for i, c in enumerate(cells) if ENV_ANCHOR in "".join(c["source"]))
    cfg_i = next(i for i, c in enumerate(cells) if DEMO_MINUTES in "".join(c["source"]))

    changed = []
    if sets:
        s = "".join(cells[env_i]["source"])
        assert s.count(ENV_ANCHOR) == 1
        block = ("# ---- ours: configuration overrides (tools/fz_variant.py) ----\n"
                 f"setup_env.update({json.dumps(sets)})\n"
                 f"print('OURS_FZ_VARIANT {name}', {json.dumps(sets)}, flush=True)\n")
        cells[env_i]["source"] = s.replace(ENV_ANCHOR, block + ENV_ANCHOR).splitlines(keepends=True)
        changed.append(env_i)
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
    print(f"built out/{slug}: cells changed {sorted(set(changed))}; overrides {sets or 'none'}; "
          f"Phase A {'25' if all_games else '10'} games x {minutes} min")
    print(f"push:   kaggle kernels push -p out/{slug}")
    print(f"status: kaggle kernels status {owner}/{slug}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="short variant name, e.g. reset")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--minutes", type=int, default=25)
    ap.add_argument("--all-games", action="store_true")
    ap.add_argument("--owner", default=None, help="Kaggle username (default: from ~/.kaggle/kaggle.json)")
    args = ap.parse_args()
    if not SRC.is_dir():
        sys.exit("Run first: python3 tools/adopt.py dfranzen/arc-agi-3-milestone-2-solution --no-grafts")
    if not re.fullmatch(r"[a-z0-9-]{1,40}", args.name):
        sys.exit("name: lowercase letters, digits and dashes only")
    sets = dict(kv.split("=", 1) for kv in args.set)
    owner = args.owner or json.loads((Path.home() / ".kaggle" / "kaggle.json").read_text())["username"]
    build(args.name, sets, args.minutes, args.all_games, owner)


if __name__ == "__main__":
    main()
