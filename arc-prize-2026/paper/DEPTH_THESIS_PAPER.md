# The Depth Thesis: Why ARC-AGI-3 Agents Stall, and a Depth Engine That Targets It

**Draft v0.1, 2026-09-29.** ARC Prize 2026 Paper Track, ARC-AGI-3 track. Team "Sehajvir singh".
Linked Kaggle entry: `hackersinghrai/arc3-base-full-r1` (hidden score 5.28), plus the Depth Engine variants d2/d3.
Due Nov 8. Sections marked **[TODO]** wait on hidden-score draws that are still running.

---

## Abstract

ARC-AGI-3 scores an agent per level by `min(1.15, (human/agent)^2)`, weights level k by k, and caps each game at
the weighted share of levels cleared. We analyse what this implies and measure where a strong open LLM agent loses
points.

- **The depth ladder.** Clearing the first k levels of every public game is worth at most 3.5 / 10.6 / 21.1 / 35.2 /
  52.9% for k = 1..5. Levels 1–3 hold only 21% of the total weight.
- **The census.** We ran the public B81 agent (Qwen3.8-Flash-Next, NVFP4, one Kaggle RTX Pro 6000) on all 25 public
  games at the production clock. It scored 8.24, and every game ended on the clock.
  - One more level cleared in every game would lift the score to 19.92 (+11.7).
  - Perfect efficiency on the levels it already clears would lift it only to 10.50 (+2.3).
- **The failure mode.** In 11 of 25 games, the level in progress had already consumed more actions than a human
  needs for the whole level. At that point, even a late clear scores near zero. We call this *thrashing*.

We then build a **Depth Engine** from three small, fail-safe additions to the agent:
1. an in-game action-effect CNN, gated by its own recent accuracy;
2. carry-over of the confirmed world model across levels;
3. a stall breaker that lists untried interactions.

We report hidden-set results against repeated baseline draws **[TODO]**, and a negative result: generic prompt
additions lowered the hidden score (3.47 vs 4.41 mean).

## 1. Scoring arithmetic: the depth ladder

- Level k of an n-level game has weight k, so level k contributes k / (n(n+1)/2) of the game.
- A level scores `min(1.15, (h/a)^2)`, where h is the human action count and a is the agent's.
- A game's score is capped at the weighted share of cleared levels.

**Consequences:**
1. **Depth dominates.** Across the 25 public games (6–10 levels, mean 7.32), the maximum score after clearing k
   levels everywhere is:

   | k | 1 | 2 | 3 | 4 | 5 |
   |---|---|---|---|---|---|
   | max % | 3.52 | 10.57 | 21.14 | 35.24 | 52.85 |

2. **Efficiency is quadratic, but bounded.** Being 2× slower than a human costs 75% of a level's value. Being faster
   than a human gains at most 15%.
3. **Late clears are nearly worthless.** A level cleared at 4× the human count scores 6% of its value. So once a
   level is far over budget, the remaining clock is better spent on exploration that could unlock the *next*
   levels.

Reproduce with `agent/tools/depth_ladder.py`.

## 2. The census: where a strong open agent loses points

**Setup:**
- Agent: the public B81 notebook (Tufa Duck harness plus anim solver); Qwen3.8-Flash-Next (NVFP4) on vLLM.
- Clock: all 25 public games at 7,920 s per game.
- Raw lines: `research_notes/census/base_full_r1_2026-09-27.txt`.

**Findings:**

| Metric | Value |
|---|---|
| Public-25 mean / median | 8.24 / 3.57 |
| Games by levels cleared (0 / 1 / 2 / 3 / 4) | 3 / 12 / 4 / 2 / 4 |
| Games ending on the clock | 25 / 25 |
| Actions per game (median / mean) | 133 / 159 (about 60 s per action) |
| Games limited by the depth cap vs by efficiency | 14 vs 11 |
| Counterfactual: perfect efficiency on cleared levels | 10.50 (+2.3) |
| Counterfactual: one more level everywhere | **19.92 (+11.7)** |

- **Thrashing.** In 11 of 25 games, the unfinished level had already used more actions than a human needs for the
  whole level:

  | Game | Agent actions | Human actions |
  |---|---|---|
  | vc33 | 264 | 61 |
  | sc25 | 254 | 32 |
  | s5i5 | 218 | 89 |
  | su15 | 145 | 42 |
  | g50t | 148 | 78 |
  | cd82 | 129 | 55 |
  | lf52 | 117 | 81 |

  The agent repeats one hypothesis rather than switching strategy.
- **Catastrophic levels.** Efficiency losses concentrate in a few levels. On ft09, level 4 took 360 actions against
  a human's 28, costing about 24 points in that game.
- **Time is the binding resource.** At about 60 s per action, a game gets only about 130 actions. That is fewer
  than a human needs to clear four levels in many games. Depth and speed are therefore coupled.

## 3. The Depth Engine

Every part is a graft that wraps an existing harness hook. It fails open: any exception returns the original
behaviour. Each part adds at most one short line to the prompt. This is motivated by Tufa's report, and our own
negative result, that extra prompt tools can hurt.

### 3.1 In-game action-effect learner (`grafts/affordance.py`)
- **Model:** a 3-layer CNN with a 64×64 click head and a 6-key head, trained on CPU inside each game (StochasticGoose
  style).
- **Label: real change.** A diff of at most 3 collinear cells within 2 cells of the border counts as a timer tick,
  not an effect. Without this correction, the step counters in vc33 and tn36 made every action look effective and
  the learner never trained.
- **Calibration gate.** A hint appears only when predict-then-learn accuracy over the last 20 actions is at least
  0.8 *and* beats always guessing the majority label. The model stays silent unless it is demonstrably right in
  this game.
- **Candidate filter:** only objects up to 5% of the board; backgrounds and HUD are excluded.

### 3.2 Level carry-over (`grafts/level_carry.py`)
- **Problem:** the harness wipes its six knowledge slots at every level transition.
- **Fix:** on a level clear, we keep the World, Goal and Actions understanding plus the last 6 actions in
  `cross_level_notes` (the last 2 levels, at most 900 characters). Mechanics usually persist across levels.

### 3.3 Stall breaker (`grafts/stall_breaker.py`)
- **Trigger:** after 80 actions on one level.
- **Output:** one line naming the object classes (colour × size) never clicked on this level, and the valid keys
  never pressed. Nothing is blocked or forced.

### 3.4 Engineering results
- **Tests:** offline unit tests and an end-to-end run on real game engines with a mock policy (593 actions, 65
  trainings, 0 errors).
- **Phase A smoke:** all parts load on the Kaggle GPU image.
- **d2 smoke:** tn36 cleared 2 levels for the first time in 5 runs of that game.

## 4. Hidden-set results

We get one scored draw per day, and draws of the same notebook vary by roughly ±30%. So we report every draw.

| Variant | Hidden draws | Mean |
|---|---|---|
| B81 baseline (external draws plus ours) | 4.50, 3.86, 3.03, 5.36, 5.28 | 4.41 |
| m-series (generic prompt extras) | 3.41, 4.07, 2.93 | 3.47 |
| d2 (learner + carry-over) | 4.79 | 4.79 (1 draw; inside the B81 range, inconclusive) |
| d3 (+ stall breaker) | not submitted; superseded by the move to Franzen's harness | |

**[TODO]**: add a significance statement (Welch's t-test or bootstrap) once there are at least 3 draws per arm.

## 5. Negative result: generic prompt additions hurt

- **m2/m3** added generic advice: scoring and pacing text, click candidates, and keep-on-death. They loaded and ran
  without errors, yet scored below the baseline mean in all three draws.
- **Our reading:** an LLM agent with a tight clock pays for every extra prompt token, both in latency and in
  attention. This is why each Depth Engine part adds at most one line, and speaks only when it is calibrated.

## 6. Universality and limits

- **Universality.** The ladder analysis applies to any agent on ARC-AGI-3. The grafts depend on only four hook
  points (`NoopGuard.observe`, `board_signature`, `_build_user_prompt`, and the knowledge-summary updater).
  `tools/adopt.py` applies them to any Duck-derived notebook. **[TODO]**: results on a published top notebook
  after Oct 1.
- **Limits:**
  - The census is a single run.
  - The hidden set has different games.
  - The CNN predicts effects, not goals. Goal inference remains the LLM's job, and it is the hard part.

## 7. Toward 85%: what the analysis implies

1. **Speed is depth.** Halving the time per action doubles the action budget, and that budget is currently binding
   in every game. Candidates:
   - an fp8 KV cache;
   - shorter prompts;
   - skipping LLM calls on moves the learner already predicts.
2. **Stop the thrashing.** Once a level is far over the human budget, the value of finishing it is near zero. The
   agent should switch to exploration that transfers to later levels.
3. **Advisors, not replacements.** Small learned models (CNN now, JEPA-lite later) are most useful as calibrated
   advisors that stay silent unless accurate.

## Reproducibility

- Code: `arc-prize-2026/agent/` (grafts, `build_notebook.py`, `go.py`, `tools/depth_ladder.py`, `tools/adopt.py`).
- Tests: `python3 -m unittest discover -s tests` (21 tests).
- Every Kaggle run: `agent/LEDGER.md`.

## Rubric self-check (0–5, to raise before Nov 8)

| Criterion | Now | How to raise it |
|---|---|---|
| Accuracy | 1 | Adopt a top published notebook plus the Depth Engine |
| Universality | 2 | Show the grafts help on a second harness |
| Progress | 2 | Measure how many more actions the speed work buys |
| Theory | 3 | Section 1 is exact; add a simple model of how speed turns into levels |
| Completeness | 2 | Hidden draws per arm, plus an ablation of parts 1–3 |
| Novelty | 3 | Calibrated silent advisor, and thrashing as a named failure mode |
