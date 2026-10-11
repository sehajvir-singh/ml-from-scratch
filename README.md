# ml-from-scratch: Model Arena

Five **non-LLM** model families plus one new hybrid, all written from scratch in PyTorch and trained on
the same small reasoning benchmark so they can be compared fairly. Everything fits on a
MacBook Air M2 with 8 GB of RAM.

## The benchmark: Mini-ARC

Five 10x10 grid puzzles in the style of [ARC-AGI](https://arcprize.org). Each one needs a different kind of thinking:

| task | what the model must do | kind of reasoning |
|---|---|---|
| `recolor` | swap every colour using a fixed rule | local, 1 cell |
| `outline` | hollow out filled rectangles | local, 3x3 neighbourhood |
| `flip` | mirror the grid left-right | global geometry |
| `gravity` | let every coloured cell fall to the bottom | iterative, per column |
| `flood` | fill every cell reachable from the seed without crossing walls | long-range search |

The score is **exact match**: the whole output grid must be right, as in ARC.

## The models (`arena/models/`)

| # | model | idea in one line |
|---|---|---|
| 1 | **TRM**, Tiny Recursive Model | one tiny network applied in loops, refining a scratchpad `z` and an answer `y` |
| 2 | **NCA**, Neural Cellular Automaton | every cell runs the same tiny rule and only sees its neighbours, like living tissue |
| 3 | **JEPA** | predicts the *meaning* (latent) of the answer instead of its pixels |
| 4 | **Liquid** (CfC) | brain-inspired neurons, each with a learned time constant |
| 5 | **KAN**, Kolmogorov-Arnold Network | learnable activation curves on every edge instead of fixed ones |
| 6 | **LiReCA**, Liquid Recursive Cellular Automaton (**new**) | NCA locality + TRM recursion and deep supervision + liquid gates + row/column broadcast |

Every file opens with a docstring that explains the model and cites its paper.

## Run it

```bash
pip install -r requirements.txt
python -m arena.run                          # train all six and print the leaderboard
python -m arena.run --models nca lireca      # just some of them
python -m arena.run --steps 300              # quick test run
```

On a Mac it uses the Apple GPU (MPS) automatically. Results are saved to `results/arena.json`.

## Leaderboard

_Filled in after the first full training run._
