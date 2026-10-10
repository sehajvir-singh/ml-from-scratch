"""Compare Phase A runs of Franzen-based variants, game by game.

    python3 tools/fz_results.py out/logs-fz-reset [out/logs-fz-inventory ...]

Reads each run's benchmark.json (TAAF format) and prints score, levels and actions per game next to Franzen's own
demo run on the same games (mean 36.56), plus how often each action type was used (e.g. RESET, UNDO).
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

# Franzen's own Phase A run, 2026-09-30 (10 demo games x 25 min): score, levels.
BASELINE = {
    "ar25": (41.67, 5), "ft09": (47.62, 4), "lp85": (41.67, 5), "r11l": (14.29, 2), "re86": (16.67, 3),
    "sb26": (93.34, 8), "sc25": (28.57, 3), "tr87": (47.62, 4), "tu93": (13.07, 3), "vc33": (21.08, 3),
}


def load(run_dir: Path) -> dict[str, dict]:
    data = json.loads((run_dir / "benchmark.json").read_text())
    out = {}
    for r in data["game_runs"]:
        acts = collections.Counter(h["action"]["id"] for h in r.get("history", []))
        out[r["game_id"][:4]] = {
            "score": float(r.get("final_score") or 0.0),
            "levels": int(r.get("levels_completed") or 0),
            "n": int(r.get("number_of_levels") or 0),
            "actions": sum(acts.values()),
            "kinds": acts,
            "state": r.get("state"),
        }
    return out


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    dirs = []
    for p in sys.argv[1:]:
        if (Path(p) / "benchmark.json").is_file():
            dirs.append(p)
        else:
            print(f"skipping {p}: no benchmark.json yet (run not finished, or not downloaded)")
    if not dirs:
        sys.exit("nothing to compare yet")
    runs = [(Path(p).name.replace("logs-", ""), load(Path(p))) for p in dirs]
    games = sorted(set(BASELINE) | {g for _, r in runs for g in r})
    head = f"{'game':6}{'franzen':>14}" + "".join(f"{name:>22}" for name, _ in runs)
    print(head)
    print("-" * len(head))
    for g in games:
        b = BASELINE.get(g)
        row = f"{g:6}" + (f"{b[0]:8.2f} ({b[1]} lv)" if b else f"{'-':>14}")
        for _, r in runs:
            x = r.get(g)
            row += f"{x['score']:10.2f} ({x['levels']}/{x['n']} lv) {x['actions']:3d}a" if x else f"{'-':>22}"
        print(row)
    print("-" * len(head))
    common = [g for g in BASELINE if all(g in r for _, r in runs)]
    base_mean = sum(BASELINE[g][0] for g in common) / max(1, len(common))
    line = f"{'mean':6}{base_mean:14.2f}"
    for _, r in runs:
        line += f"{sum(r[g]['score'] for g in common) / max(1, len(common)):22.2f}"
    print(line + f"   (over {len(common)} common games)")
    lv = f"{'levels':6}{sum(BASELINE[g][1] for g in common) / max(1, len(common)):14.2f}"
    for _, r in runs:
        lv += f"{sum(r[g]['levels'] for g in common) / max(1, len(common)):22.2f}"
    print(lv)
    allc = sorted(set.intersection(*[set(r) for _, r in runs]))
    if len(allc) > len(common):   # e.g. 25-game runs: also compare over every game all runs played
        line = f"{'mean*':6}{'':14}"
        for _, r in runs:
            line += f"{sum(r[g]['score'] for g in allc) / len(allc):22.2f}"
        print(line + f"   (* over all {len(allc)} games every run played)")
        lv = f"{'lv*':6}{'':14}"
        for _, r in runs:
            lv += f"{sum(r[g]['levels'] for g in allc) / len(allc):22.2f}"
        print(lv)
    if len(runs) == 2:   # paired view: per-game difference of the second run against the first
        (n1, a), (n2, b) = runs
        diffs = [b[g]["score"] - a[g]["score"] for g in allc]
        wins = sum(d > 0.5 for d in diffs); losses = sum(d < -0.5 for d in diffs)
        print(f"\npaired {n2} vs {n1} over {len(allc)} games: mean diff {sum(diffs)/len(diffs):+.2f}, "
              f"better in {wins}, worse in {losses}, same in {len(diffs)-wins-losses}")
        if len(diffs) > 2:   # one all-or-nothing game can dominate: show the mean without the largest swing
            big = max(range(len(diffs)), key=lambda i: abs(diffs[i]))
            rest = diffs[:big] + diffs[big + 1:]
            print(f"   without the largest swing ({allc[big]} {diffs[big]:+.1f}): mean diff {sum(rest)/len(rest):+.2f}")
    for (name, r), p in zip(runs, dirs):
        kinds = sum((x["kinds"] for x in r.values()), collections.Counter())
        print(f"\n{name}: action types {dict(kinds.most_common())}")
        for log in Path(p).rglob("serve*.log"):   # server memory facts, if the log was saved
            for line in log.read_text(errors="ignore").splitlines():
                if any(k in line for k in ("max_total_num_tokens", "KV Cache is allocated", "avail mem", "OutOfMemory")):
                    print("   server:", line.strip()[:200])
    print("\nRule: one 10-game run varies by several points; only a gain of about 3+ in the mean counts as a signal.")


if __name__ == "__main__":
    main()
