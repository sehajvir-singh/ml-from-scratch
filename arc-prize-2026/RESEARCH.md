# ARC Prize 2026 – ARC-AGI-3 (Kaggle): Research & Plan to Win

_Research compiled 2026-09-25. Competition page: <https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3>_

> **TL;DR**
> - This is an **offline, single-GPU agent competition** on *interactive games*: no rules and no stated goal. Frontier APIs are not allowed at evaluation time.
> - **Kaggle scores are still tiny.** The Milestone #1 winner scored about **1–2 %**. Small, real gains are enough to place.
> - The scoring rewards two things: **completing levels** (later levels weigh more) and **using few actions** (the penalty is quadratic).
> - The strongest direction in current research is a **hybrid agent**:
>   1. cheap, non-LLM exploration over a state graph,
>   2. a local LLM that writes an **executable Python world model** and checks it against logged transitions,
>   3. a search planner that runs inside that model.
> - It keeps **knowledge from level to level** within a game.
> - **Key dates:** Milestone #2 is **Sep 30** (5 days away). Entry/team-merge deadline is **Oct 26**, final submission is **Nov 2**, and winners are announced **Dec 4**.

---

## 1. Competition facts

| Item | Detail |
|---|---|
| Launch | Mar 25, 2026 |
| Milestone #1 | Jun 30, 2026 (awarded Jul 6) |
| **Milestone #2** | **Sep 30, 2026**. 1st $25K / 2nd $10K / 3rd $2.5K per arcprize.org. You must open-source by the deadline to be eligible. |
| Entry / team merge deadline | Oct 26, 2026 |
| **Final submission** | **Nov 2, 2026** |
| Results | Dec 4, 2026 |
| Final top-score prizes | $40K / $15K / $10K / $5K / $5K |
| Grand Prize | $700K for the first agent to score 100 % (effectively out of reach this year) |
| Internet | **None** during evaluation. No GPT/Claude/Gemini APIs; open weights only. |
| Open source | Required for any prize, and must be reproducible. |
| Hardware options (starter kit) | CPU, 2×T4 (default), P100, or **RTX 6000 (`g4-standard-48`, offered only for ARC-AGI-3; uses quota fast)** |
| Submission | Kaggle notebook, run in two phases: A validates the code, B plays the hidden games. Output is `submission.parquet`. |
| Local engine | The `arc-agi` PyPI package runs the same game engine as the Kaggle gateway. |
| Not confirmed | Exact runtime limit (hours), daily submission cap. Check the Rules tab. |

**Datasets.** 25 public demo games, 55 semi-private games (API testing), and 55 **fully private games (the ones Kaggle scores)**. The public leaderboard uses about half of the test data; the final result uses the other half.

**Environment.** Turn-based games on a **64×64 grid with 16 colours**:
- **Actions:** 5 key actions, Undo, and a click on any (x, y) cell. `RESET` is also available.
- **Levels:** at least 6 per game.
- **Instructions:** none.
- **Knowledge needed:** only Core-Knowledge priors (objects, geometry/topology, intuitive physics, agency). No language, numbers or cultural symbols.
- **Humans:** 486 people made 2,893 attempts and solved 100 % of the games. The median first solve took about 7.4 minutes.

## 2. Scoring (RHAE): what it means for strategy

```
level_score = min(1.15, (human_baseline_actions / ai_actions)^2)
game_score  = Σ(level_idx · level_score) / Σ(level_idx)   # level weights = 1, 2, 3, ...
total       = mean(game_score over games)
```

- **Human baseline:** the "upper-median" first-time human per level (the second-best human in the paper).
- **What counts as an action:** only commands that change the environment. Thinking, tool calls and simulation are **free**.

Strategic consequences:
1. **Completing a level matters more than anything else.** An unfinished level scores 0.
2. **Later levels weigh more.** In a 6-level game, level 6 is worth 6/21 ≈ 29 % and level 1 only about 5 %. So you may spend actions exploring on level 1, as long as you **carry what you learned** into later levels and play them efficiently.
3. **The penalty is quadratic.** Using 2× the human action count gives 0.25; 3× gives 0.11. Even so, a slow solve beats no solve.
4. **Thinking is free.** Put your compute budget into simulating an internal model, and send the real game as few actions as possible.
5. **Stop hopeless games.** Stop sending actions to a game you can't progress on, and move your time budget to other games. Extra actions only add wall-clock time.

## 3. What has worked so far (evidence)

### Kaggle (offline, single GPU): the setting that matters
| Result | Approach |
|---|---|
| **M1 1st – Tufa Labs "The Duck"** ([code](https://github.com/Tufalabs/duck-harness), [post](https://tufalabs.ai/research/duck-harness/)) | Qwen 3.6 27B FP8 via vLLM.<br>• The game is posed as a coding problem: observations are Python variables in a REPL, and the model inspects them with code.<br>• Perception uses three views: rendered image, ASCII grid, and a segmentation tool.<br>• "Infinite play via eviction": the oldest messages are dropped from context.<br>• **Hand-crafted tools *hurt*; a lightweight, generic harness worked best.**<br>• Scored about 1.2–1.6 %. |
| **M1 2nd – Reki** | Gemma-4-31B vision-LLM as the policy, built on the official GPT-OSS-120B template.<br>• Input: labelled images of recent frames. Output: JSON with what changed, a short plan, and 1–4 actions.<br>• Reflection memory refreshed about every 10 steps.<br>• A **numpy click heuristic** prefers small, rare-coloured, button-like shapes.<br>• **"Dead-signature" pruning** stops clicking object types that never change anything.<br>• Features can be switched on/off with env vars for ablations. |
| **M1 3rd – "forge"** | Similar Gemma-4-31B JSON-action agent.<br>• Generates several candidate actions and scores them with an arbiter.<br>• A "confidence" mode makes safe, reversible moves when the model is unsure.<br>• **Observed that local public-game results didn't predict the leaderboard.** |
| Preview 1st – StochasticGoose (12.6 % on preview) | CNN + RL that predicts **which actions change the frame**, which makes exploration much cheaper. |
| Preview 2nd – Blind Squirrel | Builds a **state graph** from frame hashes and prunes loops and no-op actions. A ResNet18 value model is retrained on solved paths. |

### Research papers (mostly frontier LLMs, public games)
- **Executable World Models** ([arXiv 2605.05138](https://arxiv.org/abs/2605.05138)):
  - A coding agent maintains a *Python world model*, checks it with verifier programs against observations, refactors it into simpler abstractions, and plans inside it. No game-specific code.
  - GPT-5.5: **15/25 public games fully solved, 58 % RHAE**.
- **OPINE-World** ([arXiv 2607.01531](https://arxiv.org/abs/2607.01531)):
  - Two agents: one plays the game, the other writes the world-model program.
  - The model is refined in a counterexample-guided loop (CEGIS) and verified by replaying logged transitions.
  - Exploration is steered by **"ontology error"**: a Bayesian measure of how well the current set of object types explains what is seen.
  - **20/25 games, 78.4 RHAE.** The current state of the art for program-synthesis world models.
- **Explore Before You Solve / AERA** ([arXiv 2605.25931](https://arxiv.org/abs/2605.25931)):
  - A three-phase loop: EXPLORE, then VERIFY, then PLAN.
  - **Warning:** many public games can be beaten with trivial strategies (10 with a single blind step, 5 after one probe). **Public-game scores are a poor proxy for the private set.**
- OpenAI reports that **keeping reasoning across turns and compacting context** roughly tripled GPT-5.x scores (13.3 % → 38.3 % on the official harness). The same idea applies to local models: keep a persistent, compact memory of findings.

**Summary.** Programs you can run and check (world models) plus search are what give high RHAE. The limit on Kaggle is running this with a ~27–32B open model on one GPU within the time limit.

## 4. Recommended architecture ("verify-then-plan hybrid")

```
                ┌──────────────────────── per game ────────────────────────┐
 frame ──► Perception (numpy, no LLM)                                       │
            • connected components → objects {color, bbox, shape-hash}     │
            • diff vs previous frame → moved/changed objects, player guess │
            • frame hash → state-graph node                                │
                     │                                                      │
                     ▼                                                      │
 Explorer (no LLM, cheap)                                                   │
   • state graph, dedup by hash; prune no-op/loop actions                   │
   • clicks only on object centroids (not 4096 pixels); dead-signature list │
   • novelty/frontier BFS; use UNDO/RESET to backtrack cheaply              │
                     │ transition log (s, a, s')                            │
                     ▼                                                      │
 World-model synthesizer (local LLM, e.g. Qwen3.6-27B / Gemma-4-31B, vLLM)  │
   • writes Python `step(state, action) -> state`, `is_win(state)`          │
   • verifier replays ALL logged transitions; mismatches → counterexamples  │
   • CEGIS loop until model fits (budgeted); keep simplest passing program  │
                     │                                                      │
                     ▼                                                      │
 Planner: BFS / A* / MCTS inside the model (free actions!)                  │
   • execute shortest plan; on prediction mismatch → log & re-synthesize    │
                     │                                                      │
 Level cleared ──► carry world model + goal hypothesis to next level        │
                └───────────────────────────────────────────────────────────┘
 Fallbacks: VLM-JSON policy (Reki-style) if synthesis keeps failing;
            give up on a game after N actions without progress.
```

Why this design:
- **Explorer.** Almost every early win came from cutting down the action space: frame-change prediction, no-op pruning, and clicking objects instead of pixels. It costs no LLM tokens and raises the level-1 solve rate.
- **World model + planner.** The best research results (58–78 RHAE) use it, and it directly reduces the number of actions sent to the game.
- **Cross-level transfer.** Later levels weigh the most, and the same game mechanics repeat across levels. Once a model is verified, later levels mostly just need planning.
- **Thin harness around the LLM.** Tufa found that specialised tools hurt. Give the model a REPL with the parsed objects and the transition log, and let it write code.

### LLM serving tips for one GPU
- Pick the RTX 6000 accelerator. Use **FP8/AWQ Qwen 3.6 27B** (M1 winner) or Gemma-4-31B, with vLLM **prefix caching**. Keep prompts short and stable so the cache hits.
- Evict old history, but keep a **persistent "facts" block**: the verified model code, known object roles and the goal hypothesis. This is the local version of OpenAI's "retained reasoning + compaction".
- Run several games at once to keep the GPU busy, since vLLM batches requests.
- Set a time budget for each game and each level, and a watchdog. A timeout usually costs more than a weak answer.

## 5. Evaluation & iteration discipline
- Public games give an **inflated, misleading** signal (see AERA; "forge" saw the same). To get a better local proxy:
  - Report **levels ≥ 2 completed** and **actions ÷ human baseline**, not just the RHAE total.
  - Hold out games; never tune prompts on the games you evaluate on.
  - Make or borrow **new games** with the ARC-AGI-3 game engine / DSL (`arc-agi[dsl]`) to test generalisation.
- Make every component switchable with an env var (Reki's approach) and run ablations.
- Save full traces (frames, actions, model code) and view them in a trace viewer. The Duck repo has a good one.

## 6. Action plan / timeline

| When | Do |
|---|---|
| **Now → Sep 30 (Milestone #2)** | Fork the Duck harness (the proven Kaggle pipeline). Add the **numpy explorer layer**: object-centroid clicks, no-op/dead-signature pruning, state-hash dedup. Submit, and **open-source before the deadline** to be eligible. Low risk, likely beats M1 scores. |
| Oct 1 → Oct 20 | Build the world-model synthesiser, verifier and BFS planner, with cross-level transfer. Run ablations on held-out and self-made games. |
| By **Oct 26** | Accept the rules and finalise any team merge. |
| Oct 20 → Nov 2 | Tune time budgets, harden against crashes and timeouts, and pick the 2 final submissions: one safe, one ambitious. Publish code and a write-up (the write-up also feeds the Paper Track). |

**Biggest risks:**
- Runtime timeouts. Budget time strictly.
- Overfitting to public games.
- Non-reproducibility. Pin versions and weights, and publish the code.

## Sources
- Competition: [Kaggle ARC-AGI-3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3) · [arcprize.org ARC-AGI-3 track](https://arcprize.org/competitions/2026/arc-agi-3) · [ARC Prize 2026 docs / starter kit](https://docs.arcprize.org/arc-prize-2026) · [Scoring methodology](https://docs.arcprize.org/methodology)
- Benchmark paper: [ARC-AGI-3 (arXiv 2603.24621)](https://arxiv.org/abs/2603.24621)
- Winners: [Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1) · [Duck harness code](https://github.com/Tufalabs/duck-harness) · [Tufa write-up](https://tufalabs.ai/research/duck-harness/) · [Preview 30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings)
- Research: [Executable World Models (2605.05138)](https://arxiv.org/abs/2605.05138) · [OPINE-World (2607.01531)](https://arxiv.org/abs/2607.01531) · [Explore Before You Solve (2605.25931)](https://arxiv.org/abs/2605.25931) · [OpenAI: two settings tripled ARC-AGI-3 scores](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/)
- Starter-kit forks: [rvats20/ARC-AGI-3-agent](https://github.com/rvats20/ARC-AGI-3-agent)
