"""Train every model on Mini-ARC and print a leaderboard.

    python -m arena.run                       # all models, default steps
    python -m arena.run --models nca trm      # just some
    python -m arena.run --steps 500           # quick smoke run
"""
import argparse
import json
import os

import torch

from .common import n_params, pick_device, train
from .models import MODELS
from .tasks import TASKS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=list(MODELS), choices=list(MODELS))
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/arena.json")
    args = ap.parse_args()

    device = pick_device()
    print(f"device: {device}")
    results = {}
    if os.path.exists(args.out):
        with open(args.out) as f:
            results = json.load(f)
    for name in args.models:
        torch.manual_seed(args.seed)
        model = MODELS[name]()
        print(f"\n=== {name}  ({n_params(model):,} params) ===")
        results[name] = train(model, steps=args.steps, batch_size=args.batch, seed=args.seed, device=device)
        results[name]["steps"] = args.steps
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)

    print("\n## Leaderboard (exact-match accuracy: the whole grid must be right)\n")
    print("| model | params | " + " | ".join(TASKS) + " | mean | train time |")
    print("|---|---|" + "---|" * len(TASKS) + "---|---|")
    for name, r in sorted(results.items(), key=lambda kv: -kv[1]["exact_mean"]):
        cells = " | ".join(f"{r['exact'][t]:.0%}" for t in TASKS)
        print(f"| {name} | {r['params']:,} | {cells} | **{r['exact_mean']:.0%}** | {r['train_seconds']:.0f}s |")


if __name__ == "__main__":
    main()
