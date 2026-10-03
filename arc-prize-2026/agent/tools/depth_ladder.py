"""The depth ladder: how much score each extra cleared level is worth, and what limits a game's score.

ARC-AGI-3 scoring (docs.arcprize.org/methodology): per level min(1.15, (human/agent actions)^2), level k has
weight k, and a game's score is capped at the weighted share of the levels it cleared. The total is the mean over games.

    python3 tools/depth_ladder.py                     # ladder over the 25 public games
    python3 tools/depth_ladder.py out/logs-m3/*.log   # also decompose each [finished] line in Kaggle logs
"""
from __future__ import annotations

import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_env_files import PUBLIC_GAMES  # noqa: E402

FINISHED = re.compile(r"\[finished\] (\w{4})-\w+ .*?level=(\d+)/\d+ .*?per-level=([\d/,]+)")


def ladder() -> None:
    counts = [len(b) for _, b in PUBLIC_GAMES.values()]
    print(f"{len(counts)} public games, {min(counts)}-{max(counts)} levels (mean {statistics.mean(counts):.2f})")
    for k in range(1, 8):
        caps = [100 * sum(range(1, min(k, n) + 1)) / sum(range(1, n + 1)) for n in counts]
        print(f"  clear the first {k} levels in every game -> at most {statistics.mean(caps):5.2f}%")


def decompose(text: str) -> None:
    for game, cleared, per_level in FINISHED.findall(text):
        pairs = [tuple(map(int, p.split("/"))) for p in per_level.strip(",").split(",")]
        n = len(pairs)
        weight = n * (n + 1) / 2
        # level=X/N counts cleared levels; the level in progress also shows actions, so it is excluded
        done = [(i + 1, a, h) for i, (a, h) in enumerate(pairs[: int(cleared)])]
        eff = sum(k * min(1.15, (h / a) ** 2) for k, a, h in done) / weight
        cap = sum(k for k, _, _ in done) / weight
        limit = "depth" if cap <= eff else "efficiency"
        print(f"  {game}: cleared {len(done)}/{n}  efficiency {100 * eff:.2f}  depth cap {100 * cap:.2f}  "
              f"score {100 * min(eff, cap):.2f}  limited by {limit}")


if __name__ == "__main__":
    ladder()
    for path in sys.argv[1:]:
        print(path)
        decompose(Path(path).read_text(errors="ignore"))
