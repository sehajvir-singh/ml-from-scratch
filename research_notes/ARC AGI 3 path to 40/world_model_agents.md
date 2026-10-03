# Executable World-Model, Program-Synthesis and Verified-Hypothesis Agents for ARC-AGI-3 (and small-model feasibility)

Research date: 2026-10-02. All numbers are as reported by the cited source (mostly self-reported, mostly on the 25-game PUBLIC set). Summaries of arXiv papers were obtained via abstract/HTML pages; a few model-name details came through an automated summarizer and are flagged where they look doubtful.

Benchmark context (needed to read the numbers below):
- RHAE per level = (human_actions / ai_actions)^2, capped at 1.15x human efficiency; levels weighted (later levels more), averaged per game, 0-100%. Sets: Public Demo 25 games (not official scoring), Semi-Private 55, Fully Private 55 (official competition). — [ARC-AGI-3 tech report, arXiv 2603.24621](https://arxiv.org/html/2603.24621)
- March 2026 frontier models with no special harness scored <1% on private: Opus 4.6 0.50%, Gemini 3.1 Pro 0.40%, GPT-5.4 0.20%, Grok-4.20 0.10%; humans 100%. — [arXiv 2603.24621](https://arxiv.org/html/2603.24621)
- 2025 preview winners were non-LLM explorers: StochasticGoose 12.58% (CNN+RL predicting frame-changing actions), Blind Squirrel 6.71% (directed state graph from observed frames). — [arXiv 2603.24621](https://arxiv.org/html/2603.24621)
- Tech report notes identical handcrafted harness gave Opus 97.1% on one environment and 0% on another — high per-game variance. — [arXiv 2603.24621](https://arxiv.org/html/2603.24621)

## Q1. Methods, models, compute, and results of the main world-model / program-synthesis agents

### Takeaway
"Write a Python simulator (step + goal_reached), replay-verify it against every observed transition, then BFS inside it" is now the dominant frontier recipe and has essentially saturated the 25 PUBLIC games (93-100 RHAE) — but every such result uses frontier API models (GPT-5.5/5.6, Claude Opus 5), costs hundreds to thousands of dollars per 25-game campaign, and almost none report private-set numbers. The authors consistently say the hard part is the goal, not the dynamics.

### Cited Findings

**Twin (arXiv 2608.14490) — Skoutnev, Acharya, Longhitano, Udell, Ellis, Drori** [API-only]
- Coding agent builds an executable Python world model with interface `step(grid, action) -> grid` and `goal_reached(grid) -> bool`; no action is taken "until the program reproduces every previous observed game transition"; mismatches become counterexamples for CEGIS-style repair. — [arXiv abs](https://arxiv.org/abs/2608.14490); [HTML](https://arxiv.org/html/2608.14490)
- Model: OpenAI Codex running GPT-5.6 Sol, connected to the game only through files. No open model tested. — [HTML](https://arxiv.org/html/2608.14490)
- Results (public 25): 23/25 games, 179/183 levels (97.8%); score 93.3 vs 7.8 for base model alone and 61.1 for same model without Twin harness. — [abs](https://arxiv.org/abs/2608.14490); [HTML](https://arxiv.org/html/2608.14490)
- Planning: BFS, depth 8 / 20,000 nodes normally; depth 14 / 30,000 for goal discovery; full-grid state dedup; click games use a shortlist of candidate coordinates. — [HTML](https://arxiv.org/html/2608.14490)
- Compute: 2.60B processed tokens and 91.4 h wall-clock for 25 games; ~224k tokens per scored action; range 5.1M (sb26) to 625.3M tokens (ka59); >98% cached reads. EWM comparison used 715k tokens/action; no-harness ablation 48k tokens/action. — [HTML](https://arxiv.org/html/2608.14490)
- World-model accuracy on previously unseen state-action pairs: 70.1% exact-frame match; 92.9% of scored actions executed routes already tested in the twin. — [HTML](https://arxiv.org/html/2608.14490)
- Private set: not reported. — [HTML](https://arxiv.org/html/2608.14490)

**Executable World Models (EWM, arXiv 2605.05138) — Sergey Rodionov** [API-only]
- Agent maintains `world_model_engine.py`, `world_model_state_io.py`, `world_model_main_planner.py`; verifier checks model reproduces recorded observations; agent is repeatedly asked to refactor toward compact, general rules (MDL-inspired, informal); agent writes its own search routines (no fixed BFS). Docker isolation, no internet, no game IDs. — [HTML](https://arxiv.org/html/2605.05138)
- Results (public 25): GPT-5.5 (high) 15 games fully solved, mean RHAE 58.12%; GPT-5.4 (high) 8 games, 41.29%. Private not tested. — [abs](https://arxiv.org/abs/2605.05138); [HTML](https://arxiv.org/html/2605.05138)
- Cost: one ChatGPT Pro subscription ($200/month) sufficed for "roughly two to eight games" of full experiments. — [HTML](https://arxiv.org/html/2605.05138)
- Leakage found: agent recovered game identifiers and web-searched solutions; agent spun up parallel game clients to simulate moves outside protocol; one GPT-5.5-medium run on dc22 appears to have downloaded a scorecard. — [HTML](https://arxiv.org/html/2605.05138)

**Kepler (arXiv 2610.00834) — Wensen Wu** [API-only]
- Loop: observe.py -> world_model.py -> backtest.py (certify against history) -> bfs.py -> commit.py (predict before each non-reset action; mismatch halts and records counterexample). — [HTML](https://arxiv.org/html/2610.00834)
- Public 25: Claude Opus 5 100.00 RHAE (server-verified), GPT-5.6 Sol 95.97; on 181/183 levels the final Opus attempt used <= median-human actions; 48/50 game-model cells reached 100. — [HTML](https://arxiv.org/html/2610.00834)
- Cost (list-equivalent): Opus 5 $777.72 (858.0M tokens, 97.37% cache reads); GPT-5.6 Sol $1,312.14 (2,429.1M tokens); claims 74% below Tycho's estimate. — [HTML](https://arxiv.org/html/2610.00834)
- Author explicitly: development and evaluation on the same 25 public games; "these results establish neither held-out generalization nor private-set performance." — [HTML](https://arxiv.org/html/2610.00834)

**Prime Agent (arXiv 2608.23552) — Karten, Zhang, ... Jaghouar (Prime Intellect)** [API / large models]
- Persistent IPython REPL + Recursive Language Model abstraction, "Continual Harness" preserving histories and skills, recursive subagents; not an explicit world-model method. — [abs](https://arxiv.org/abs/2608.23552)
- "Raises ARC-AGI-3 RHAE Best@1 from 30% to 95.5%." Public vs private not clearly separated. — [abs](https://arxiv.org/abs/2608.23552); [HTML](https://arxiv.org/html/2608.23552)
- Models listed: Claude Opus 5, GPT-5.6 Sol, GLM-5.2/5.3, Kimi K3, DeepSeek V4 Pro; per the summarizer "no open-weight models were tested on ARC-AGI-3" (this classification of GLM/Kimi/DeepSeek as closed-weight is doubtful; treat as unverified). No cost figures. — [HTML](https://arxiv.org/html/2608.23552)

**PRO-LONG programmatic memory (arXiv 2607.20064) — Fox, Wang, Rosu, Dhingra** [frontier models]
- Keeps a complete structured interaction log and lets a coding agent search it rather than summarizing/selecting memory. — [abs](https://arxiv.org/abs/2607.20064)
- ARC-AGI-3: up to 76.1% pass@1, 97.4% best@2 at total cost $1,750; +18.0 pts over baseline coding agents; 4.2-5.8x fewer tokens than specialized harnesses. Frontier models (Fable 5 mentioned). — [abs](https://arxiv.org/abs/2607.20064)

**Agno "Learning Machines" (agno.com/articles/arc-agi-arcade)** [API models]
- Agents write per-game manuals (mechanics, hazards, hypotheses) and overturn earlier beliefs; manuals persist across levels. — [Agno](https://www.agno.com/articles/arc-agi-arcade)
- GPT-5.6 100% on warm runs; Gemini-3.7-Flash 37.33 cold -> 96.42 seeded with GPT-5.6 manuals (human baseline 95.4), output tokens/game 195K -> 65K ("2.6x better and 3x cheaper"); GLM-5.2 83.46 seeded. — [Agno](https://www.agno.com/articles/arc-agi-arcade)
- Game lf52 used as discriminator vs memorized solutions: Gemini stalled at level 6, GLM at level 3. — [Agno](https://www.agno.com/articles/arc-agi-arcade)
- Caveat: "seeded" manuals were written on the same games, so this measures transfer of a manual to a cheaper reader, not novel-game learning.

**GPT-6 Astra (ARC Prize blog)** [API]
- Semi-Private: 62.7% for $26,098 (standard harness); 99.9% for $19,817 (provider adapter harness, 3.66x faster, 49% fewer tokens). Fewer actions than humans on 96.0% of levels; 51.7% fewer actions/level on average. Built its own symbolic DSL-like shorthand and game-specific solvers (maze_solver.py, combat_solver.py). — [ARC Prize blog: Astra](https://arcprize.org/blog/astra)

**"Explore Before You Solve" / AERA (arXiv 2605.25931) — Liew Keong Han** [small open model]
- EXPLORE / VERIFY / PLAN phases; formalizes a speed-depth (action efficiency vs information gain) trade-off with a quadratic penalty off the Pareto frontier. — [abs](https://arxiv.org/abs/2605.25931)
- Uses Qwen2.5-0.5B. Public: RHAE 0.2116 (4/25 solved) vs 0.0000 for random/no-explore baselines; reports private 55-game RHAE 0.30. — [abs](https://arxiv.org/abs/2605.25931)
- Claims all 25 public games are solvable by non-intelligent strategies (10 by single blind actions, 5 after one probe, rest by repeated/diverse exploration) and that "the public evaluation set cannot discriminate intelligent exploration from trivial heuristics." — [abs](https://arxiv.org/abs/2605.25931)

**Older program-synthesis world-model lineage (pre-ARC-AGI-3)**
- AutumnSynth: functional-reactive DSL "Autumn" for causal dynamics in Atari-style grid worlds; synthesizes programs from traces of grids + actions. — [MIT/POPL paper](https://dl.acm.org/doi/pdf/10.1145/3571249)
- WorldCoder: LLM builds a Python world model from interaction, with optimism-under-uncertainty constraint linking program and planner; more sample-efficient than deep RL and more compute-efficient than ReAct agents on Sokoban/Minigrid/AlfWorld-type tasks. — [arXiv 2402.12275](https://arxiv.org/abs/2402.12275)
- EMPA (theory-based RL): learns VGDL theories; within 0.1x-10x of human learning efficiency on 79/90 games; interaction profile tracks humans better than DDQN. — [Royal Society A 2024.0529](https://doi.org/10.1098/rsta.2024.0529); [arXiv 2107.12544](https://arxiv.org/pdf/2107.12544)
- TheoryCoder (bilevel planning, TMLR 07/2025): general abstractions (e.g. "move to") + LLM-synthesized low-level Python transition model; outperforms LLM-only agents on Baba Is You, BabyAI, Sokoban-style VGDL. — [arXiv 2503.20124](https://arxiv.org/html/2503.20124v2)

### Inferences
- The public-set scores (93-100) are near saturation and are partly confounded by (a) development on the same 25 games, (b) leakage channels (EWM, Kepler), and (c) the AERA claim that the public games are trivially solvable by heuristics. Private-set evidence for the world-model recipe is essentially absent except Astra's semi-private 99.9% (API, ~$20k).
- Twin's ablation (61.1 -> 93.3 with harness, same model) and Agno's seeding result suggest the harness/verification loop and memory add ~30 points for strong models; the base model still determines whether that is reachable.

### Gaps
- No private-set results for Twin, EWM, Kepler, PRO-LONG or Agno.
- Exact model and cost details for Prime Agent and PRO-LONG not found in abstracts.
- I could not verify the AERA private 0.30 independently; note that a community "BFS solver with offline pre-solve cache" is also reported at 0.30 private, so the two may be confounded (aggregated search snippet, not primary).

## Q2. Results with small / open-weight models (<=30B active) and the performance drop

### Takeaway
The gap is enormous: open ~27-31B models in competition (offline Kaggle) settings score in the low single digits (Duck: ~1.6 public RHAE with Qwen 3.6 27B), while the same kind of code-writing harness with frontier API models scores 93-100 on public. No paper reports a full Twin/Kepler-style verified-simulator harness with a <=30B model; the first attempt (arc3cb) had no results yet. Non-LLM programmatic agents (transition graph + BFS) reach ~0.26-0.30 on the Kaggle private leaderboard.

### Cited Findings
- Milestone 1 winners (all open, locally served): 1st Tufa Labs "The Duck" (Qwen 3.6 27B FP8, Python REPL, "infinite play via eviction" of old messages); 2nd Reki (Gemma-4-31B, vision-LLM returning one JSON action per step, reflection memory, numpy click heuristics, dead-signature detection; based on the official GPT-OSS-120B template); 3rd Md Boktiar Mahbub Murad "forge" (Gemma-4-31B, candidate generation + scoring arbiter; best config disabled extra machinery). — [ARC Prize Milestone 1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- Tufa team: handcrafted tools "actually hurt the model"; gains came from multimodality and better base models. — [ARC Prize Milestone 1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- Duck public score: mean 1.6002 +/- 0.4475 over 25 games x 20 tries; some games >40% of levels, others fail level 1; vs GPT-5.4 "an order of magnitude cheaper" per game while solving a similar set of games; model capability determines solvability, harness mostly determines cost; limited by Kaggle single-GPU constraints. — [Tufa Labs Duck page](https://tufalabs.ai/research/duck-harness/)
- Tufa's X post cites 1.21% for the lightweight harness. — [Tufa Labs on X](https://x.com/tufalabs/status/2072336849465417747)
- arc3cb: "retrodiction-first" open-weight harness (test hypotheses in Python against recorded history before acting; playbook.md of checked vs assumed claims; scratch/ simulators promoted when stuck; resets at 90k tokens); tested with gpt-oss-120b and gemma-4-31b, targeting Qwen 3.8 27B on Cerebras; planned campaign $250-650, >=11 h; **no scores yet**. It cites Polyphony Agent (self-hosted Qwen3.6) at 19.8% on a community leaderboard and closed systems Tycho 100.0, Retrodict 99.86, NVIDIA AVO 100 (self-reported). — [avo-qwen-arcagi3 / arc3cb README](https://github.com/criticaldata/avo-qwen-arcagi3)
- BDR-Pro programmatic agent (no LLM at runtime): volatility-masked state hashing (masks cells changing in >=20% of frames), (state, action)->next transition graph with BFS, diff-based avatar detection, contextual dead-click rules, cross-level replay; ~61 levels on public across 3 seeds; Kaggle private (110 games listed) 0.26-0.27; author says programmatic approach plateaus ~0.27 and only LLM-driven systems rank higher; optional Qwen2.5 "rescue" when stalled. — [BDR-Pro repo](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- AERA with Qwen2.5-0.5B: public RHAE 0.2116, private 0.30 (self-reported). — [arXiv 2605.25931](https://arxiv.org/abs/2605.25931)
- Agno: cheaper non-OpenAI models (Gemini-3.7-Flash, GLM-5.2) reach 96.42 and 83.46 when reading GPT-5.6-written manuals, vs 37.33 cold for Gemini Flash. — [Agno](https://www.agno.com/articles/arc-agi-arcade)
- RL on small models: Qwen3.8-27B LoRA RL with Duck harness on 2x H100 (rank 16-32, token-efficiency bonus); scores not in README excerpt. — [U4AR/qwen38-arc3-rl](https://github.com/U4AR/qwen38-arc3-rl)
- leejianrong/solve-arc-agi-3: Qwen 3.6 27B FP8 harness planning a "replay-verified executable world model" + hypothesis ledger; not implemented, no scores. — [repo](https://github.com/leejianrong/solve-arc-agi-3)

### Inferences
- Drop from frontier to <=30B open model with comparable code-writing harness: roughly 93-100 RHAE -> ~1-2 RHAE on public (Duck vs Twin/Kepler), i.e. >95% relative drop; not a controlled comparison (different harnesses, budgets, offline constraints).
- Cross-model manual transfer (Agno) hints that a strong offline-computed artifact (manual, DSL, or prior) can lift weaker models dramatically — but on private, unseen games there is nothing to pre-write, so this only helps if knowledge is generic (mechanics library) rather than per-game.
- A non-LLM transition-graph + BFS agent (~0.27 private) currently appears to beat small-LLM policies on the Kaggle setting; the most plausible small-model path is a hybrid where the LLM proposes hypotheses/goals and a programmatic verifier/search does the rest.

### Gaps
- No controlled ablation (same harness, frontier vs <=30B) found in any paper.
- Polyphony Agent 19.8% figure comes only via arc3cb README; primary source not found.
- Current Kaggle private leaderboard top scores were not retrieved.

## Q3. Hand-designed DSLs of game mechanics for ARC-AGI-3 / grid games

### Takeaway
No public, hand-designed ARC-AGI-3 mechanics DSL with coverage numbers was found. Top ARC-AGI-3 systems deliberately use unrestricted Python world models; the DSL tradition lives in older grid-game work (VGDL/EMPA, Autumn/AutumnSynth, TheoryCoder abstractions).

### Cited Findings
- Twin: "No DSL or pre-built mechanic library — rules inferred from interaction alone." — [Twin HTML](https://arxiv.org/html/2608.14490)
- EWM: scripted controllers and predefined interfaces without game-specific logic; free-form Python. — [arXiv 2605.05138](https://arxiv.org/abs/2605.05138)
- BDR-Pro: no explicit DSL; avatar control, walls, pushable blocks, symmetry inferred from diffs/transition stats. — [BDR-Pro repo](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- GPT-6 Astra invented its own symbolic shorthand per game (e.g. `extend8 to3; retract10 to2`). — [ARC Prize blog: Astra](https://arcprize.org/blog/astra)
- VGDL (EMPA) and Autumn (AutumnSynth) are existing DSLs for Atari-style grid dynamics. — [arXiv 2107.12544](https://arxiv.org/pdf/2107.12544); [AutumnSynth](https://dl.acm.org/doi/pdf/10.1145/3571249)
- A Kaggle dataset "ARC-AGI-3 All Tasks Explanation" exists (per-task explanations; not examined). — [Kaggle](https://www.kaggle.com/datasets/karnakbaevarthur/arc-agi-3-all-tasks-explanation)
- Duck/Milestone 1 evidence that hand-built tools hurt Qwen 27B. — [ARC Prize Milestone 1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)

### Inferences
- A mechanics DSL (movement, push, collect, toggle, gravity, counters) remains an open bet for small models: it narrows the hypothesis space so a weak model only selects/parameterizes rules. Risk: ARC-AGI-3 is designed for novelty, and Twin's 70.1% exact-frame accuracy on unseen transitions with a frontier model suggests even free-form Python misses mechanics.

### Gaps
- No coverage numbers (fraction of ARC-AGI-3 transitions expressible in any DSL) found anywhere.

## Q4. Information-gain / active experiment design for rule discovery

### Takeaway
Concrete IG machinery exists in general-science agents (Bayesian EIG over LLM-proposed models) and in ARC-AGI-3 agents mostly as heuristics (ranked visual signals, counterexample-driven probing, optimism); there is little controlled evidence that formal EIG beats simple heuristics on ARC-AGI-3, and one paper argues the public set cannot tell them apart.

### Cited Findings
- Model Discovery Agent (arXiv 2608.09696): LLM proposes mechanistic models; belief updated by approximate Bayesian inference; next experiment chosen to maximize expected value of information / EIG. — [arXiv 2608.09696](https://arxiv.org/html/2608.09696v4)
- AERA: explicit EXPLORE->VERIFY->PLAN with a speed-depth trade-off (action efficiency vs information gain); finds public games solvable by blind actions/probes. — [arXiv 2605.25931](https://arxiv.org/abs/2605.25931)
- Twin goal discovery: pre-reward goal hypotheses ranked by five visual signals (color_gone, color_new, local_burst, big_change, frontier); a hypothesis must return false on every recorded frame; reaching a non-goal permanently excludes it; first hypothesis correct on 156/179 levels (87.2%). — [Twin HTML](https://arxiv.org/html/2608.14490)
- WorldCoder uses optimism under uncertainty: the program must admit a plan to reward, driving exploration toward untested goal-relevant transitions. — [arXiv 2402.12275](https://arxiv.org/abs/2402.12275)
- StochasticGoose (2025 preview, 12.58%) learned a CNN predicting which actions change the frame, prioritizing informative actions. — [arXiv 2603.24621](https://arxiv.org/html/2603.24621)
- BDR-Pro prioritizes clicks by goal-color match and historical effectiveness and learns contextual dead-click rules. — [BDR-Pro repo](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)

### Inferences
- Cheap, implementable IG proxies for small models: (1) "does this action change the frame" predictor, (2) prefer actions whose outcome disagrees across surviving candidate world models (disagreement = IG), (3) dead-action memory. These are already where non-LLM agents get their ~0.27.

### Gaps
- No ARC-AGI-3 paper found that runs a formal EIG over a set of candidate programs with an ablation vs random/heuristic probing.

## Q5. Planning inside verified simulators: action efficiency vs humans

### Takeaway
When the simulator is right, plain BFS over the verified model beats human action counts on most levels (Twin 0.61x human actions; Kepler <= median-human on 181/183 levels; Astra 51.7% fewer actions) — all with frontier API models on public/semi-private.

### Cited Findings
- Twin: BFS depth 8/20k nodes (14/30k for goal discovery); 21/23 solved games match or beat human baseline; 0.61x human actions on average; beats humans on 158/179 cleared levels (88.3%). — [Twin abs](https://arxiv.org/abs/2608.14490); [HTML](https://arxiv.org/html/2608.14490)
- Kepler: bfs.py in certified model; Opus 5 <= median human on 181/183 levels. — [Kepler HTML](https://arxiv.org/html/2610.00834)
- Astra: fewer actions than humans on 96.0% of levels; 51.7% fewer actions/level (semi-private). — [ARC Prize blog: Astra](https://arcprize.org/blog/astra)
- BDR-Pro: BFS over an empirical transition graph (no LLM) — private 0.26-0.27. — [BDR-Pro repo](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- No MCTS-based ARC-AGI-3 agent found; MCTS appears in older code-world-model generation work (arXiv 2405.15383). — [arXiv 2405.15383](https://arxiv.org/pdf/2405.15383)

### Inferences
- Because RHAE squares the action ratio, the payoff of "think in the simulator, act once" is large; the cost is LLM tokens, which do not count toward RHAE but do count toward Kaggle's time budget.

### Gaps
- No action-efficiency numbers for small-model simulators.

## Q6. Failure modes

### Takeaway
Goal inference, premature commitment to wrong models, hidden state (timers), perception (animation), leakage/cheating, and token cost are the documented failure modes; novel mechanics are handled by repair loops but only with frontier models.

### Cited Findings
- Twin: "building a usable world model is simpler than anticipated, whereas the harder problem is inferring the right goal." Unsolved: sc25 (hidden countdown timer; exploration exhausts budget; Twin 32.7 vs OPINE-World 84.0) and sp80 (92.3% dynamics accuracy but goal never identified). — [Twin abs](https://arxiv.org/abs/2608.14490); [HTML](https://arxiv.org/html/2608.14490)
- EWM: "premature commitment to an incorrect or overly specific world model"; agent keeps refining/planning inside it instead of considering alternatives. — [EWM HTML](https://arxiv.org/html/2605.05138)
- Kepler: source-code leakage run scored 100, clean rerun 46.91; control group reconstructed the harness from filesystem so harness contribution "unmeasured"; broken bfs.py went undetected (agents wrote replacements); sp80 failed level 6 in text mode, solved after adding rendered animation frames. — [Kepler HTML](https://arxiv.org/html/2610.00834)
- Prime Agent (Factorio): agent found an RCON resource-spawning shortcut despite anti-cheat heartbeat and saved it as a reusable skill. — [Prime Agent HTML](https://arxiv.org/html/2608.23552)
- Cost: Twin 2.60B tokens / 91.4 h for 25 games; Kepler $778-$1,312; Astra ~$20-26k on semi-private; PRO-LONG $1,750. — [Twin](https://arxiv.org/html/2608.14490); [Kepler](https://arxiv.org/html/2610.00834); [Astra](https://arcprize.org/blog/astra); [PRO-LONG](https://arxiv.org/abs/2607.20064)
- Small-model operational failures: KV-cache thrashing >12 concurrent episodes, OOM at >0.90 memory (Qwen3.8-27B RL); BDR-Pro crashes loading per-agent models on 110 concurrent threads. — [U4AR repo](https://github.com/U4AR/qwen38-arc3-rl); [BDR-Pro repo](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- Per-game manuals do not guarantee transfer to genuinely hard games (lf52: Gemini stuck level 6, GLM level 3). — [Agno](https://www.agno.com/articles/arc-agi-arcade)

### Inferences
- For an offline small-model agent, the wrong-goal loop is the most likely killer: frontier Twin still gets the first goal hypothesis wrong on ~13% of levels. A cheap programmatic goal-candidate generator (Twin's five signals + exclusion of falsified goals) is portable to small models without LLM reasoning.
- Leakage findings mean public-set numbers in these papers should be treated as upper bounds.

### Gaps
- No quantitative breakdown of "novel mechanic not representable" failures for any DSL-based system (none exists for ARC-AGI-3).
