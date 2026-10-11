# Path 3: train our own model on rented GPUs

*Written 2026-09-26. Evidence is in `research_notes/ARC AGI 3 path to top five/`, especially `kaggle_finetuning.md` and
`top_team_intel.md`.*

## Why this is the path to ~20%

- Tufa Labs went from 11.04 to 18.81 between Sep 6 and Sep 13, with no new public model in between.
- On Sep 9 they forked a reinforcement-learning training stack (verl, miles).
- The most likely explanation is post-training. Nothing on Kaggle's free GPU can do that.

**Honest risks:**
- The one competitor who trained Flash-Next on an H200 node reported *no gain*.
- Thuitanium's LoRA on 27B made held-out games *worse*.

Training is how you win, and it is also easy to get wrong. So we go in cheap stages, each with a go/no-go check.

## The model and the target

| Option | Why | Why not |
|---|---|---|
| **A. LoRA on Qwen3.8-Flash-Next** (what we serve now, ~4%) | Starts from the strongest base; anything it learns adds to 4% | Needs 8×H200 / B200-class for training; serving the adapter is untested; licence is Qwen Community (not Apache) |
| **B. LoRA on Qwen3.8-27B** (~1.2–1.7% base) | Cheap: 1 GPU; the adapter is known to serve on vLLM | Must gain 2.5–3× just to tie A's base |

Recommendation: **start with A, gated.** B only pays if A's adapter cannot be served on Kaggle.

## Stages (stop at the first failed gate)

| Stage | What | Rented hardware | Est. cost | Gate |
|---|---|---|---|---|
| 0 | **Serving check**: load a dummy LoRA on Flash-Next in the pinned Kaggle vLLM with the adapter guard on | Kaggle (free) | $0 | Adapter loads, throughput within 10% of no-LoRA |
| 1 | **Data**: run our m2 harness on many games (public 25 plus 200–400 synthetic games from arc-interactive / sonpham / NVIDIA dream-team), several passes each; keep only turns from runs that **cleared a level** | 1× RTX PRO 6000 or B200 (NVFP4 needs Blackwell) | ~$150–400 (60–150 GPU-h) | ≥ 2,000 clean winning turns, from ≥ 100 distinct games |
| 2 | **SFT (STaR)**: LoRA on attention + shared layers, 1–2 epochs, small learning rate; hold out 20% of games | 8× H200 or 4× B200 for ~6–12 h | ~$300–800 | Held-out games: more levels than base, over ≥ 3 passes |
| 3 | **Kaggle A/B**: publish the adapter as a Kaggle model; alternate daily base vs adapter | Kaggle (free) | $0 | Adapter mean > base mean over ≥ 4 draws each |
| 4 | *(optional)* **RL (GRPO) on levels cleared** | 8× H200, days | $2,000+ | Only if stage 3 wins |

Stages 0–3 cost about **$500–1,200** in total.

## What went wrong last time (0% after renting)

That was almost certainly setup, not the GPUs. Common causes:
- a different vLLM or model build than Kaggle;
- missing chat template or tool parser;
- evaluating with different settings.

This time:
- Use the **same pinned vLLM runtime and model files** as the Kaggle notebook.
- Check every stage against the same public-25 smoke run we already ran on Kaggle (5 levels on tn36/vc33/bp35). The rented machine must reproduce about that before any training.

## Rules to respect

- Winning code **and weights** must be open-sourced; publish the adapter as a public Kaggle model.
- There is no host ruling on self-generated synthetic data. CPMP (NVARC3) argues it isn't "external data". Ask in the forum before the final submission.
- Never train on the 25 public games' solutions as an answer key. Train only on the agent's own play.

## What we need from you

1. A budget cap (e.g. $500 or $1,500), and which GPU cloud you want to use (RunPod, Lambda, Vast.ai, etc.).
2. Nothing else until Stage 0 passes on Kaggle.

## Timeline

| Dates | Stage |
|---|---|
| Sep 26–29 | Daily m2 submissions; Stage 0 serving check (free) |
| Sep 30 | Path 1: adopt any top notebook published at Milestone #2 (`agent/tools/adopt.py`) |
| Oct 1–7 | Stage 1 data collection |
| Oct 8–12 | Stage 2 training |
| Oct 13–25 | Stage 3 Kaggle A/B |
| Oct 26 | Team merges close |
| Nov 2 | Pick the two final submissions |
