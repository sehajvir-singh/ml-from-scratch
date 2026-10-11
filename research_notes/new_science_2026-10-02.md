# Can we build a stronger model or new science for ARC-AGI-3? (2026-10-02)

## The new science: agents that write and verify their own world model
- **Twin** (arXiv 2608.14490): a frontier coding agent writes an *executable world model* of the game: Python that
  predicts the next frame from the current frame and an action.
  - Before each move, the harness makes that program **replay every past transition**. Each mismatch is a
    counterexample the agent must fix.
  - Result: **179/183 public levels (97.8%)**, 88% of them more efficient than humans, and goals inferred before any
    reward in 87% of levels.
  - The base model alone scored 7.8%, with a plain harness 61.1%, and with Twin 93.3%.
- **Prime Agent** (arXiv 2608.23552): a persistent IPython REPL, memory across trajectories and recursive sub-agents.
  ARC-AGI-3 RHAE rose from 30% to **95.5%**. Open source (CC BY 4.0).
- Earlier, executable world models (arXiv 2605.05138) fully solved 15/25 public games with GPT-5.5.
- **What this means:** the harness that turns "playing" into "programming a simulator, then planning in it" is now the
  frontier, and with frontier models it nearly solves the public set.
- **The catch:** every one of these results uses large frontier API models. Kaggle allows only offline models on one
  RTX PRO 6000 (Qwen3.8-Flash-Next, a few billion active parameters). No published result shows a small local model
  writing correct world models.

## Training our own stronger model: honest assessment
- **From scratch: impossible.** Competitive LLMs cost millions in compute. We have about 30 GPU-h and about 20 TPU-h a
  week on Kaggle.
- **Fine-tuning the model we serve:** Qwen3.8-Flash-Next is too large to LoRA-train on a free TPU v5e-8 in our quota.
  sirikilohit tried a LoRA on Qwen3.8-27B with Kaggle TPU and it "scored badly". There are only 25 public games of
  data, and the hidden 110 are different.
- **Distilling frontier traces into the local model:** plausible in principle, with the weights shipped as a Kaggle
  dataset. But it is a weeks-long research project with high risk. The rules on generating training data with API
  models must be checked first.
- **Verdict:** training is not the path for us by Nov 2. The harness is.

## What we can build: "Twin-lite" on Franzen's notebook
Franzen's harness already gives the agent a persistent Python sandbox, keeps its functions for the whole game, and
records every frame. Missing is the **verification loop**:
1. The agent may define `predict(frame, action) -> frame` (persistent across turns).
2. After each action, the harness runs `predict` on the recorded history and reports **one short line**: "your model
   matches 41/45 past transitions; first mismatch at step 17 (cell r,c expected X got Y)".
3. The agent can plan with `predict` in Python (search over action sequences) before spending real actions.

**Why it could work locally:**
- It adds *evidence*, not advice. sirikilohit and our m-series both found advice hurts, while evidence helps.
- It makes the model's code do the precise work the small model is bad at.

**Risks:**
- A small model may rarely write a useful `predict`.
- The extra replay compute must stay tiny. Keep it on CPU with a time cap.
- Measure it with the same Phase A protocol, and only trust a repeated gain.

**Paper value: high.** It is the first test of the Twin idea under the competition's offline, small-model limits,
whatever the score.

## Order of work
1. Finish the settings tests (RESET, inventory) and the baseline noise run.
2. Solved-level memory (proven +2.8 elsewhere).
3. Twin-lite prototype, tested locally with the mock model first, then in Phase A.
