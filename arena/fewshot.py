"""Few-shot Mini-ARC, the real ARC setting: each episode shows only K demonstration pairs of a
puzzle (no task name), and the solver must produce the output for a new input.

    python -m arena.fewshot                 # 3 demos per episode, 100 episodes per task
    python -m arena.fewshot --demos 2 --episodes 50
"""
import argparse
import time
from collections import Counter

import numpy as np

from .rulesearch import RuleSearchCA
from .tasks import TASKS, _GEN


def episode(task, rng, k):
    pairs = [_GEN[task](rng) for _ in range(k + 1)]
    xs, ys = zip(*pairs[:k])
    return np.stack(xs), np.stack(ys), pairs[k][0], pairs[k][1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demos", type=int, default=3)
    ap.add_argument("--episodes", type=int, default=100)
    ap.add_argument("--seed", type=int, default=777)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    print(f"RSCA, training-free, {args.demos} demos per puzzle\n")
    print("| task | solved | most common rule found | avg seconds |")
    print("|---|---|---|---|")
    scores = []
    for task in TASKS:
        solved, found, start = 0, Counter(), time.time()
        for _ in range(args.episodes):
            xs, ys, tx, ty = episode(task, rng, args.demos)
            solver = RuleSearchCA()
            hyp = solver.fit(xs, ys, tx)
            found[hyp.describe() if hyp else "no rule found"] += 1
            solved += np.array_equal(solver.predict(tx), ty)
        acc = solved / args.episodes
        scores.append(acc)
        top = found.most_common(1)[0][0]
        print(f"| {task} | {acc:.0%} | {top} | {(time.time() - start) / args.episodes:.2f} |", flush=True)
    print(f"\nmean: {np.mean(scores):.0%}")


if __name__ == "__main__":
    main()
