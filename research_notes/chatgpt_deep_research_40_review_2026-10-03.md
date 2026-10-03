# Review of the ChatGPT Deep Research report (Oct 3, 2026)

Source: `chatgpt_deep_research_40_2026-10-03.md` (ChatGPT output, kept verbatim). This note checks it against our own
measurements and turns it into the build order.

## What it adds that we did not have
- **Prefix-cache warning about our own graft.** Franzen rebuilds `[{"role":"system","content": self._system_prompt},
  *history]` on every request (`tool_agent.py` ~6696). His comments measure a 15% vs 99% shared prefix when the
  start of the prompt changes, and prefix reuse falling from 75% to 45%. Our solved-memory graft rewrote the system
  prompt on every cleared level, so each clear forced a full prefill of the history (~60–120k tokens). **Fixed:** see
  "Built" below.
- **Explicit stall and goal triggers:**
  - a predicate the model stated is contradicted by the frame;
  - a predicted win does not happen;
  - the same route repeats;
  - roughly 16–24 actions or 8–12k tokens pass with no progress.

  It suggests one fresh-context review with a 2–4k evidence packet. These are concrete and cheap, and fit
  "evidence, not advice".
- **Selective world-model use** (Tycho: 88.49 when the model chooses when to delegate, against 83.07 when it always
  does). This supports *optional* `predict()` checking, not a forced world model.
- **Evaluation numbers.**
  - The sign test on our sm25 11-vs-7 split gives p ≈ 0.48, which is noise.
  - Detecting +3 needs about 8 / 16 / 28 paired runs for a per-run paired SD of 2 / 3 / 4.
  - Alternate hidden submissions A, B, B, A.
- **Leaders from public sources:**
  - CLIST mirror: Tufa 52.51, Chen 48.07, then 35.79, 34.77, 34.21.
  - In MLST (54:54–56:47), Dries Smit describes generated games, end-to-end RL and reward shaping.
  - This matches our reading: the top two train. Everyone at about 35 or below is a harness-plus-model entry like us.

## Where we disagree
- **Odds.** It gives 80% for ≥30, 45% for ≥35 and 20% for ≥40. Our hidden draws are 25.78 and 27.88, and no change we
  made has a significant effect yet. Our estimate is about **55% for ≥30, 20% for ≥35 and 5–8% for ≥40**. Its gain
  ranges are uncalibrated guesses: none of them was measured on this stack.
- **Serving gains** (online FP8 +15–28%, FR-Spec +7–10%) were measured on NVFP4 Pennyroyal builds, not on the Intel
  W4A16 checkpoint we run. Worth one sweep, not a plan.
- **QLoRA:** it agrees this doesn't fit (110–120 GiB). Joshi's +0.69 was on a weak base. Dropped.

## Build order (Oct 3 → Nov 2)
1. **Cache-friendly solved memory.** Built Oct 3, needs a paired run. Expected effect: small but positive. It keeps
   sm25's signal and removes the prefill cost.
2. **Stall and goal-contradiction notices,** factual only, with no advice wording. After N actions with no new level
   and no new frame region, add one line stating the facts: the actions since progress, routes repeated, and how many
   deaths occurred at the same point. Then trigger at most one fresh-context review per level.
3. **Reasoning retention audit.** Confirm that `ARC3_REASONING_HISTORY_KEY=reasoning_content` round-trips in the
   transcripts. This only needs reading logs, no GPU.
4. **Serving sweep:** draft depth 1–4 and the online-FP8 flag, measured in tokens/s on one 10-game run each.
5. **Optional `predict()` check:** if the agent defines `predict(frame, action)`, the harness checks it against the
   last 20 transitions and reports the hit rate as a fact.

Per-variant protocol:
- 25 games, paired against a same-day baseline;
- report the mean without the largest swing, plus wins and losses;
- promote to a hidden submission only if it is positive twice.
