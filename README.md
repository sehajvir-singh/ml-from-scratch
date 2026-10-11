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
| 7 | **RSCA**, Rule-Search Cellular Automaton (**new, training-free**) | no gradient training: searches for the simplest cell rule that explains a few examples (`arena/rulesearch.py`) |

Every file opens with a docstring that explains the model and cites its paper.

## Run it

```bash
pip install -r requirements.txt
python -m arena.run                          # train all six and print the leaderboard
python -m arena.run --models nca lireca      # just some of them
python -m arena.run --steps 300              # quick test run
```

On a Mac it uses the Apple GPU (MPS) automatically. Results are saved to `results/arena.json`.

The training-free model runs in the few-shot setting instead:

```bash
python -m arena.fewshot                       # 3 demos per puzzle, 100 puzzles per task
```

## Leaderboard

Trained models: 1,500 steps x 64 grids (96,000 examples), told which task it is, CPU run.
RSCA: no training; it sees only 3 demonstration pairs per puzzle and must infer the task itself.

| model | training | params | recolor | outline | flip | gravity | flood | **mean** |
|---|---|---|---|---|---|---|---|---|
| **RSCA** (new) | none, 3 demos | rule table built at test time | 100% | 100% | 100% | 79% | 78% | **91%** |
| NCA | 96K examples | 85K | 98% | 96% | 0% | 88% | 46% | **66%** |
| **LiReCA** (new) | 96K examples | 259K | 94% | 89% | 0% | 3% | 50% | **47%** |
| Liquid (CfC) | 96K examples | 102K | 100% | 98% | 0% | 0% | 14% | **42%** |
| JEPA | 96K examples | 806K | 100% | 0% | 0% | 0% | 15% | **23%** |
| TRM | 96K examples | 413K | 92% | 0% | 0% | 0% | 0% | **18%** |
| KAN | 96K examples | 1.35M | 0% | 0% | 0% | 0% | 0% | **0%** |

### What it shows

- **Local rules win.** NCA, the smallest trained model, beats every bigger global model. Grid
  puzzles are mostly local, and a shared cell rule bakes that in.
- **No trained model learned `flip`** in this budget. It needs moving information across the
  whole grid to an exact mirrored position.
- **TRM and JEPA are under-trained here.** The TRM paper trains far longer. These numbers are a
  short-budget comparison, not a verdict on the architectures.
- **LiReCA** beats NCA on `flood` (50% vs 46%) but has not learned `gravity` yet.
- **RSCA's 91% has a home advantage.** Its menu of rule views (neighbours, mirror positions) was
  written by the same person who designed these puzzles. The fair next test is real ARC tasks.
