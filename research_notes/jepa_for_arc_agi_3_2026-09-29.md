# Would a JEPA world model help us on ARC-AGI-3? (2026-09-29)

JEPA (Joint Embedding Predictive Architecture, LeCun) learns an encoder plus a predictor of the *next latent state*
given an action. You can then plan by searching action sequences inside the model (V-JEPA 2-AC uses the
cross-entropy method, CEM).

## Evidence
- **V-JEPA 2-AC plans robot actions zero-shot**, but only after pre-training on over 1M hours of video plus 62 hours of
  robot video (emergentmind summary). The data scale is nothing like one ARC game (100–500 moves).
- **An ARC-AGI-3 JEPA-style agent exists** (github.com/calcrockett/ARC-AGI-3-JEPAstyle_approach). It has a latent
  world model, a mixture-of-experts predictor, an InfoGain exploration signal, a value head and a transition graph.
  It publishes **no scores** and describes itself as "not a leaderboard attempt".
- **Executable world models** (arXiv 2605.05138) keep the world model as Python code, verify it against history,
  simplify it, and plan through it. With GPT-5.5 they fully solve 15/25 public games (mean RHAE 58%). That is an API
  model, which is not allowed on Kaggle; the private set is untested.
- **StochasticGoose** (a CNN that predicts whether a frame changes, which is a very small world model) scored 12.58%
  on the preview. Our `affordance.py` already is that model, fed to the LLM.

## Assessment
- **A JEPA cannot replace the LLM.** It predicts *what happens*, not *what the goal is*. ARC-AGI-3 rewards only level
  completion, which is sparse, and goals have to be inferred. The LLM stays the goal-setter.
- **Data is the blocker.** Trained from scratch inside one game, a JEPA sees too few transitions. It needs offline
  pre-training on public-game trajectories plus synthetic games, with the weights shipped as a Kaggle dataset
  (allowed). The GPU is almost full with vLLM (74 GiB weights + KV), so the model must be small (a few M params,
  CPU or leftover GPU).
- **Useful as the next Depth Engine part.** Upgrade the in-game CNN from "does this action change the board?" to
  "what will the board look like?" (a latent JEPA-lite). Use it for two things:
  - (a) **Short lookahead:** rank candidate action sequences 2–5 steps ahead, and show the LLM the ones predicted
    to reach unseen states or to repeat the move pattern that cleared the last level.
  - (b) **Surprise signal:** a high prediction error marks a new mechanic worth probing, which directly targets
    the thrashing found in the census.

## Decision
1. First read the d2 and d3 hidden scores (Sep 29–30). If part 1, the "does it change" CNN, shows no gain, a bigger
   world model is unlikely to either, so we would stop here.
2. If part 1 helps, build **d4 = JEPA-lite** (Oct 5–18):
   - pre-train an encoder and predictor offline on the public games plus synthetic ones;
   - fine-tune online in each game;
   - lookahead and surprise go to the LLM as one short line, in the same accuracy-gated way as part 1.
3. Either way it makes a strong Paper Track section: a learned latent world model as an *advisor* to an LLM agent,
   measured by levels reached.
