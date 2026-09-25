# Program-Synthesis and Executable World Models for ARC-AGI-3 and Similar Interactive Benchmarks (literature up to 2026-09-25)

Scope note: all ARC-AGI-3 system results below are on the **25-game public demonstration set (183 levels)** unless a line says otherwise. None of the world-model papers found report semi-private or fully-private results. Numbers are copied as the papers state them. Primary sources are the arXiv abs and HTML full-text pages, read in full or in large sections for the four named papers and in targeted extracts for the rest.

## Q1. "Executable World Models for ARC-AGI-3 in the Era of Coding Agents" (Rodionov, arXiv 2605.05138), plus its ablation follow-up (arXiv 2607.15439)

### Takeaway
A single Codex coding agent keeps a Python world model (engine + state I/O/renderer + planner). A fixed controller prompts it to verify the model against recorded frames, refactor it toward simpler rules, and execute plans through a halt-on-mismatch executor. With GPT-5.5-high this scored a mean per-game RHAE of 58.12% (15/25 games fully solved) on the public set. The follow-up ablation found that model capability and reasoning effort matter more than the harness components; verification ranks first but costs the most tokens. All results use closed OpenAI models through a $200/month ChatGPT Pro subscription. There are no open-weight results.

### Cited Findings
**Paper metadata and code**
- Author: Sergey Rodionov (SingularityNET). v2 dated 06 Jun 2026. Code and full run artifacts: https://github.com/astroseger/arc-3-agents-baseline1 — [arXiv 2605.05138](https://arxiv.org/abs/2605.05138)

**Architecture**
- Runtime is Codex CLI 0.128.0. A scripted external controller starts the game, passes observations to the agent, and monitors whether the level is running, completed, or GAME_OVER. It sends predefined prompts in each case and does not solve levels itself. — [HTML](https://arxiv.org/html/2605.05138)
- Before normal continuation, and when progress stalls, the controller asks the agent to "simplify and refactor its world model". On GAME_OVER the controller issues RESET, returns the new observation, and asks for a refactor. — [HTML](https://arxiv.org/html/2605.05138)
- The workspace starts with templates containing only predefined interfaces: `world_model_engine.py` (transition dynamics), `world_model_state_io.py` (state reconstruction and rendering), and `world_model_main_planner.py` (planning). The agent fills and maintains them. — [HTML](https://arxiv.org/html/2605.05138)
- Helper programs:
  - The **world-model verifier** checks that the model reproduces recorded observations from previous attempts.
  - The **planner verifier** checks that the planner reaches LEVEL_COMPLETED inside the model for solved levels.
  - Planner-running utilities run plans from the current state, from a level's initial state, or from an intermediate point of a past attempt. — [HTML](https://arxiv.org/html/2605.05138)
- **Plan executor.** It simulates a proposed action sequence in the model and executes the same actions in the real game. After each non-terminal step it compares the predicted settled ASCII frame with the observed one. It stops immediately on divergence and records mismatch artifacts; it also stops on LEVEL_COMPLETED or GAME_OVER. The agent can still bypass the executor. The prompt tells it to use the executor early and to treat any mismatch as a blocking modeling error. — [HTML](https://arxiv.org/html/2605.05138)
- **Refactoring loop.** Framed as a "practical proxy for an MDL-like bias": replace special cases with shared rules, simplify state reconstruction, remove ad hoc rendering overrides, and keep the planner expressed in terms of the engine. — [HTML](https://arxiv.org/html/2605.05138)
- **Runtime recovery.** If Codex crashes or stalls, only the agent process restarts, with a recovery prompt. At most ten recoveries are allowed per game run. — [HTML](https://arxiv.org/html/2605.05138)

**Prompts and interfaces**
- The verification-variant main prompt is reproduced verbatim in the ablation paper (Appendix 12.2.3). Key text:
  - "Your primary objective is to build and maintain an executable world model of the game... Actions taken in the real game are costly... Simulation inside the world model is free."
  - "Later levels usually extend earlier mechanics rather than replacing them."
  - "final settled ASCII frames are usually the best frame source."
  - "You are forbidden to call RESET by yourself."
  - Required deliverables per level: `world_model.md`, `world_model_engine.py`, `world_model_state_io.py`, `world_model_main_planner.py`, optional `level_N_planner_i.py`, `level_N_reasoning_log.md`, and `level_N_report.md`. — [arXiv 2607.15439 HTML](https://arxiv.org/html/2607.15439)
- The interface contract in that prompt:
  - `world_model_engine(state, action)` returns `(new_state, game_status)` with game_status in {RUNNING, LEVEL_COMPLETED, GAME_OVER}.
  - The state is a dict with an obligatory `level` field. The action is a dict with `name` and optional `x`, `y` (for ACTION6).
  - `initial_state_reconstruction(level_index, initial_frame)` lives in `world_model_state_io.py`.
  - "Do **not** hardcode level layouts or ad hoc special cases... It is strictly forbidden to load real game observations into the world model engine." — [arXiv 2607.15439 HTML](https://arxiv.org/html/2607.15439)
- Other prompts in the appendix:
  - Death-analysis: "You have reached the `GAME_OVER` state... Consider whether the failure has a simple explanation that can generalize across levels."
  - Stuck reminder: "...If you do not move, you will lose."
  - Recovery: "You have been interrupted. Please review your world model, reasoning logs, and the current game state..."
  - The simplification prompts come in several steps: light, steps 1–3, and planner refactoring. — [arXiv 2607.15439 HTML](https://arxiv.org/html/2607.15439)

**Verifier details (from the ablation paper)**
- The principal verifier replays every recorded attempt from level 1 up to the current level. It checks that the renderer reproduces the initial settled 64×64 ASCII frame exactly. It then requires a cell-exact match of the settled frame and status at each step.
- Intermediate animation frames are evidence only; they are not part of the exact test.
- A renderer "override hook" is reported as a warning and labelled "modeling debt". — [arXiv 2607.15439 HTML](https://arxiv.org/html/2607.15439)

**Protocol**
- Each playthrough uses a fresh agent and a clean workspace, with one exposure per game and no whole-game restart. The per-level cap is 1500 environment actions.
- Runs used the ARC-AGI-3 library in local mode with competition rules enforced by the harness, not competition scorecard mode. The reason given is that scorecard mode closes after 15 min of inactivity and after 24 h total. — [HTML](https://arxiv.org/html/2605.05138)

**Leakage audit**
- Earlier harness versions leaked the game ID through a server API field, process args visible via `ps`, and container internet access with web search. One GPT-5.5-medium run on dc22 "appears to have downloaded a scorecard". An older GPT-5.4 run appears to have started a second game client.
- The current harness removes game names and ARC references, blocks internet (OpenAI-only proxy), disables web search, and rejects a second client. — [HTML](https://arxiv.org/html/2605.05138)

**Headline results (public 25)**
- GPT-5.5 high: 15/25 games fully solved, mean per-game RHAE 58.12%.
- GPT-5.4 high: 8/25, 41.29%.
- "Performance on the private validation set... remains to be tested." — [arXiv 2605.05138](https://arxiv.org/abs/2605.05138)

**Per-game RHAE, GPT-5.5 high (levels solved)** — [HTML Table 2](https://arxiv.org/html/2605.05138)
- ar25 100.00% (8/8), bp35 4.43% (5/9), cd82 92.91% (6/6), cn04 96.34% (6/6), dc22 0.00% (0/6)
- ft09 57.80% (6/6), g50t 95.08% (7/7), ka59 100.00% (7/7), lf52 35.48% (6/10), lp85 100.00% (8/8)
- ls20 57.02% (7/7), m0r0 67.33% (6/6), r11l 89.29% (6/6), re86 40.10% (5/8), s5i5 0.25% (2/8)
- sb26 83.78% (8/8), sc25 20.23% (3/6), sk48 11.26% (7/8), sp80 39.21% (4/6), su15 56.85% (9/9)
- tn36 74.98% (7/7), tr87 100.00% (6/6), tu93 100.00% (9/9), vc33 21.43% (3/7), wa30 9.11% (4/9)

**Per-game RHAE, GPT-5.4 high** — [HTML Table 1](https://arxiv.org/html/2605.05138)
- ar25 92.80%, bp35 2.73%, cd82 100%, cn04 0.33%, dc22 36.84%
- ft09 100%, g50t 59.25%, ka59 9.29%, lf52 1.82%, lp85 100%
- ls20 77.26%, m0r0 0.01%, r11l 18.45%, re86 27.78%, s5i5 41.67%
- sb26 73.87%, sc25 16.71%, sk48 2.78%, sp80 4.76%, su15 1.72%
- tn36 3.57%, tr87 100%, tu93 100%, vc33 10.73%, wa30 49.77%
- Several runs in both tables are marked "interrupted" (OpenAI outages or Codex usage limits) and were not restarted.

**Cost**
- With GPT-5.5 high, one ChatGPT Pro subscription (USD 200/month) was enough for "roughly two to eight games" per weekly Codex usage limit.
- Difficult games "may take up to roughly 48 hours". A full 25-game evaluation "usually takes several days".
- No token counts appear in paper 1. — [HTML](https://arxiv.org/html/2605.05138)

**Stated failure mode**
- "premature commitment to an incorrect or overly specific world model". Proposed fixes: competing-hypothesis tracking, falsification-seeking actions, multiple parallel world models, and reusable skills (BFS, A*, constraint solving). — [HTML](https://arxiv.org/html/2605.05138)

**Ablation paper (arXiv 2607.15439, v2 27 Aug 2026)**
- Four nested Codex variants: textual (twma), flexible executable (ewma), + simplification (ewma_s), and fixed-interface + simplification + exact replay verification (ewma_sv). — [arXiv 2607.15439](https://arxiv.org/abs/2607.15439)
- Mean RHAE over 25 public games, reported as textual / executable / simplification / verification: — [HTML Table 2](https://arxiv.org/html/2607.15439)
  - gpt-5.4-high: 34.16 / 33.54 / 30.60 / 39.16
  - gpt-5.4-xhigh: 40.67 / 44.72 / 53.10 / 53.72
  - gpt-5.5-high: 58.85 / 51.16 / 58.35 / 65.64
  - gpt-5.5-xhigh: 72.51 / 69.70 / 73.09 / 74.78
  - Averaged across the four variants: 34.36, 48.05, 58.50, and 72.52 respectively.
- Cost tokens (a weighted proxy, in millions, over 25 games): verification used 147.65 (gpt-5.4-high), 204.01 (gpt-5.4-xhigh), and 205.10 (gpt-5.5-high). Textual and executable variants are "substantially cheaper". — [HTML Table 3](https://arxiv.org/html/2607.15439)
- Cost-token formula: C = T_cached/60 + (T_input − T_cached)/6 + T_output. One million cost tokens ≈ USD 15 (gpt-5.4) or USD 30 (gpt-5.5) at API prices. The author warns that this underestimates API cost because subscription runs had higher cache hit rates. — [HTML §5.2](https://arxiv.org/html/2607.15439)
- Follow-ups (RHAE, unsolved games/levels, actions, cost tokens): — [HTML Table 4](https://arxiv.org/html/2607.15439)
  - ewma_sv_v1.5, gpt-5.5-xhigh: 82.01 (5/9), 207.41M
  - twma_v1.6, gpt-5.6-sol-xhigh: 92.34 (2/5), 32.32M
  - ewma_sv_v1.6, sol-xhigh: 98.97 (0/0), 8,347 actions, 90.75M
  - twma_v1.6, sol-max: 95.97 (0/0), 10,111 actions, 30.60M
  - ewma_sv_v1.6, sol-max: 98.77 (0/0), 7,758 actions, 103.49M
  - Human baseline total: 17,135 actions.
- Conclusion: "at max, the three imposed mechanisms are not required for action-efficient public-set completion"; "results indicate public-set saturation only". — [arXiv 2607.15439](https://arxiv.org/abs/2607.15439)
- The v1.5 "trouble prompt" fires on reset after more than 50 extra actions on a level. It asks the agent to look for overlooked evidence and form a new hypothesis. — [HTML §8.1](https://arxiv.org/html/2607.15439)
- Compute environment: Linux VM with 32 vCPUs (AMD EPYC 9454) and 64 G[B] RAM. — [HTML §5.3](https://arxiv.org/html/2607.15439)

### Inferences
- Other papers cite "baseline1"/EWM as **63.8 RHAE, 14 games won, 146 levels** ([OPINE-World](https://arxiv.org/html/2607.01531); [Twin](https://arxiv.org/html/2608.14490)). That is not the paper's own GPT-5.5 run: the paper reports 58.12% and 15 wins, and its Table 2 sums to 145 levels. OPINE's baseline1 per-game rows also differ (e.g., dc22 4/6 vs 0/6 in the paper; m0r0 5/6 vs 6/6). So "63.8" most likely comes from a different run, probably a community-leaderboard submission. Report both numbers with their provenance.
- Two things transfer directly to an offline harness: the interface contract (engine/state_io/planner plus exact-replay verifier and halt-on-mismatch executor) and the prompts. The loop depends on a coding agent that can write and debug roughly 100s of lines of Python per game over many hours.
- The ablation shows a steep capability gradient, from 34 (gpt-5.4-high) to 73 (gpt-5.5-xhigh) averaged over variants. A ~30B open model would likely sit below the gpt-5.4-high regime. This is extrapolation; it was not tested.

### Gaps
- Paper 1 reports no token counts or dollar costs, only the subscription estimate. The ablation gives cost tokens, not dollars.
- No private or semi-private results, and no open-weight runs.
- The GitHub repo could not be fetched from this environment (the GitHub API was blocked by the proxy). Prompt text above comes from the ablation paper's appendix.

## Q2. "OPINE-World" (Courtis, Li, Sanner, arXiv 2607.01531)

### Takeaway
OPINE-World uses two cooperating Claude Opus 4.8 agents. An actor plays; a synthesizer writes an object-centric Python world model that is admitted only if it replays every recorded transition exactly. Rewrites are triggered only by counterexamples, a periodic critic pushes against overfitting, and a Dirichlet-based "ontology error" steers exploration. It reports **78.4 RHAE and 20/25 games (160/183 levels) on the public set**, with a single run per game. No compute cost and no code link are given, and there are internal inconsistencies about whether engine sprite data was used.

### Cited Findings
**Metadata and models**
- University of Toronto. v2 dated 15 Jul 2026.
- "The synthesis and action agents run Claude Opus 4.8 behind a filesystem sandbox."
- No per-game training or demonstrations. Evaluated on the "public evaluation set of 25 games". — [HTML](https://arxiv.org/html/2607.01531)

**World-model artifact**
- A single file, `game_engine.py`, exposing `transition_function(state, action)` and `reward_function(state)`. The latter returns predicted reward plus a goal flag.
- Optional exports: a `planner()` hook and, in frames mode, `extract_objects(frame)` for 64×64 frames. Internal organization is left to the agent. — [HTML App. A.1](https://arxiv.org/html/2607.01531)

**State and model structure**
- State is a set of typed objects o = (κ key, τ type, v attributes: position, visibility, rotation, small pixel pattern).
- The model is factored per type: f_τ(object, action, local context u = ψ(o, s)) → object. Each rule is repaired one type at a time. — [HTML §3.1](https://arxiv.org/html/2607.01531)

**Two agents plus critic**
- The goal-directed action agent reads the log with file tools and short scripts, chooses actions, and never edits the model.
- The world-model agent writes and repairs the program. The two communicate only through the replay buffer and a "short structured handoff".
- A critic "runs on a fixed cadence" and asks which parts are "tailored to one level". The synthesizer is restarted from a fresh context at each counterexample. — [HTML §3.2](https://arxiv.org/html/2607.01531); [abs](https://arxiv.org/abs/2607.01531)

**CEGIS and replay verification**
- A program is admitted only when T̂(s_i, a_i) = s′_i for all buffer transitions, "attribute for attribute and object for object".
- Each transition is run twice; nondeterministic outputs are rejected, which removes hidden module-level state.
- The goal predicate is checked the same way once reward has been observed. A static check rejects predicates that recognize the goal "by reading a cached future state". — [HTML §3.3, App. A.3](https://arxiv.org/html/2607.01531)
- Synthesis cadence: build the first model "once enough transitions exist". After that, rewrite only on a misprediction (counterexample). A short deferral window batches a few counterexamples. A stall guard stops re-firing "after two rounds that fail to improve transition accuracy". — [HTML App. A.4](https://arxiv.org/html/2607.01531)

**Ontology error**
- Effect signature: e = ρ(Δ), where Δ is the set of changed attributes, with values discarded. The alphabet grows from observations (no_change, x, "x,y", pixels, gone, born).
- The local effect table has rows j = (τ, a, u) that count signatures.
- A symmetric Dirichlet prior gives the posterior mean q̂_j(e) = (α0 + C(j,e)) / (mα0 + Σ C).
- U_type = H[Pr(τ|D)]/log K. U_row = H(q̂_j)/log m. Per-object η = 1 − (1 − U_type)(1 − U_row), averaged into η_t.
- High η directs probing, type refinement, or adding context features. Correctness is decided only by exact replay. — [HTML §3.4](https://arxiv.org/html/2607.01531)
- "Crystallization" (committing the ontology): the idealized gate uses reward seen, U_type ≤ ε, and row count and modal-fraction thresholds. In the ARC-3 implementation, "the operational trigger is simpler: successful level completion plus confident non-decorative aliases." — [HTML App. P](https://arxiv.org/html/2607.01531)

**Planning**
- After a model is admitted and at least one level is cleared, the synthesizer writes a bounded forward search, citing width-based planners.
- The planner is verified offline by planning to reward from the entry states of cleared levels. Plans run one step at a time; a mismatch aborts the plan, logs a counterexample, and blocks the planner until the next synthesis.
- Per-node LLM scoring is explicitly avoided. — [HTML §3.5, App. B.4, App. R](https://arxiv.org/html/2607.01531)
- There is no synthesized reward "in the WorldCoder sense" (no optimism constraint). The goal predicate is fitted only after reward has been observed. — [HTML App. B.1](https://arxiv.org/html/2607.01531)
- Multi-tick actions: the model predicts the settled after-state, and intermediate tick frames are shown to the synthesizer as evidence. — [HTML App. A.5](https://arxiv.org/html/2607.01531)
- Context: on crossing a per-game token threshold, an agent writes a structured handoff and its session is reset. — [HTML App. A.6](https://arxiv.org/html/2607.01531)

**Results (public 25)** — [HTML Table 1](https://arxiv.org/html/2607.01531)

| System | Score | Wins | Mean levels cleared | Note |
|---|---|---|---|---|
| OPINE-World | 78.4 | 20/25 | 0.90 | |
| baseline1 | 63.8 | 14 | 0.80 | |
| Vision† | 63.2 | 12 | 0.73 | "pre-trains on eval set" |
| WorldCoder | 0.0 | 0 | | |
| Latent world models (Dreamer/MuZero family) | 0.0 | 0 | | |

- Other headline figures: 160 of 183 levels cleared. On 16 of 20 wins OPINE-World used fewer actions than humans. The mean human/agent action ratio over wins is 1.7, with the largest on m0r0 (4.3), lp85 (3.5), and cn04 (3.0). — [HTML §4, §7](https://arxiv.org/html/2607.01531)
- Games not won (actions, levels): ka59 (1076, 6+/7), sk48 (596, 4+/8), lf52 (593, 3+/10), bp35 (512, 2+/9), s5i5 (638, 4+/8). — [HTML Table 3](https://arxiv.org/html/2607.01531)
- On six games that baseline1 fails (re86, tn36, vc33, m0r0, sc25, sp80), OPINE clears all six in 2,578 actions. baseline1 spent 10,874 and humans 3,994. — [HTML Table 2](https://arxiv.org/html/2607.01531)

**Limitations and integrity**
- Stated limitations: hidden-state games are out of scope, the planner is a naive bounded search, "Single run per game... no variance estimate", and there are no per-component ablations because of "heavy interdependency". — [HTML §4 Ablations, §6](https://arxiv.org/html/2607.01531)
- Integrity: agents were filesystem-confined. A transcript audit across "four sweeps" found no access to game source or the network. — [HTML App. C](https://arxiv.org/html/2607.01531)

**Perception mode (conflicting statements)**
- Remark 1 says the reported experiments use the "spriteless regime", with objects produced by the synthesized `extract_objects`.
- Appendix H also describes a "sprite-based implementation" in which object records "come directly from the ARC engine" via its sprite list.
- Appendix C says "The structured-state results reported here...".
- Appendix E labels the system "D3M" rather than OPINE-World. — [HTML App. C, E, H](https://arxiv.org/html/2607.01531)

**Code**
- No code or repository link appears on the arXiv abstract or HTML pages. — [arXiv 2607.01531](https://arxiv.org/abs/2607.01531)

### Inferences
- The perception inconsistencies (structured-state wording, the sprite-adapter description, the "D3M" label) mean a reimplementer cannot be sure whether engine sprite metadata (names, tags, positions) was available in the reported run. Engine sprite data would make perception much easier than raw frames and is presumably unavailable on Kaggle.
- The Dirichlet effect table and ontology error are cheap non-LLM components. They could be built without any LLM to prioritize exploration, but the paper gives no ablation of their value.
- The absence of cost reporting, together with two concurrent Opus 4.8 agents and many fresh-context restarts, suggests heavy API usage. Magnitude unknown.

### Gaps
- No compute, token, dollar, or wall-clock figures.
- No code link.
- No per-component ablation.
- No open-weight runs.
- The identity of the "Vision" continual-learning agent is not given.

## Q3. "Explore Before You Solve" / AERA (Liew, arXiv 2605.25931)

### Takeaway
AERA is a three-phase EXPLORE/VERIFY/PLAN prompting agent run with **Qwen2.5-0.5B-Instruct (and 1.5B) on CPU**. It reports 0.2116 on the 25 public games (4 "solved"), plus a critique that all public games are "trivially solvable". **The "RHAE 0.30 on the full 55-game private evaluation" claim is not supported by the paper's own text.** Section 4.1 calls 0.30 the Kaggle **public-leaderboard** score as of 2026-05-17, notes that private evaluation "may differ", and says it comes from a separate BFS solver kernel, not the Qwen agent. AERA's scoring and "solve" criteria also diverge from the official metric and from what other papers observe.

### Cited Findings
**Metadata**
- Author: Keong Han Liew, independent researcher. v1 dated 25 May 2026. Code: https://github.com/farmountain/aera-arc3-paper (CC0). — [arXiv 2605.25931](https://arxiv.org/abs/2605.25931)

**Phases** — [HTML §4](https://arxiv.org/html/2605.25931)
- EXPLORE: budget B_max = max(5, min(30, ⌊0.4·H_{E,1}⌋)), where H_{E,1} is the human level-1 count. The LLM returns a structured HYPOTHESIS / UNCERTAIN / NEXT_ACTION / REASON block, and ACTION7 (undo) is preferred after exploratory moves. The phase ends when len(UNCERTAIN) ≤ θ; the length of the UNCERTAIN field is the "entropy proxy".
- VERIFY: 1–3 targeted falsification actions. If falsified, re-enter EXPLORE.
- PLAN + EXECUTE: the LLM outputs PLAN / CONFIDENCE / FALLBACK, and execution aborts to EXPLORE on an unexpected observation.
- Memory: a summary of the last 10 steps.
- The 0.4 factor was "fit on a small ablation (n=1 environment)". — [HTML §1, §3.2](https://arxiv.org/html/2605.25931)

**Setup and results**
- Hardware and models: "Kaggle P100 GPU (16 GB VRAM), model on CPU at FP32", Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct. — [HTML §5.1](https://arxiv.org/html/2605.25931)
- 5-game study (sb26, ft09, cd82, tu93, r11l): AERA b=1 scored 0.5290 (2/5), adaptive 0.2645 (1/5), no-explore 0.0000, random 0.0000. At 1.5B, no-explore scored 0.2645 and b=1 scored 0.0000. — [HTML Tables 1, 10](https://arxiv.org/html/2605.25931)
- 25 public games: b=1 scored 0.2116 (4/25: VC33, FT09, LP85, S5I5); b=5 scored 0.2116 (VC33, FT09, LP85, R11L).
- Across 8 runs: mean 0.164 ± 0.059. The adaptive budget averaged 0.194 ± 0.061.
- ReAct scored 0.388 (8/25), but 10/25 games produced an invalid ACTION8. — [HTML Tables 4–6](https://arxiv.org/html/2605.25931)

**The 0.30 claim, verbatim and in context**
- The abstract says "The linked code track entry achieves RHAE=0.30 on the full 55-game private evaluation." — [abs](https://arxiv.org/abs/2605.25931)
- Section 4.1 says the Kaggle kernel `arc-agi3-v31-zorojuro-hybrid-v9` has a "public score RHAE = 0.30" and uses "a breadth-first search over the game's action space at episode start... caching all game states that reach a solved condition... BFS depth d and time limit 180s/level". The kernel falls back to a heuristic planner.
- It continues: "Public leaderboard score: RHAE = 0.30 (30%)... Caveat: the Kaggle public leaderboard uses a subset of evaluation games; private evaluation (full 55-game set) may differ. The score reported here is the public score as of 2026-05-17." — [HTML §4.1](https://arxiv.org/html/2605.25931)
- Section 5.6 again says "achieves RHAE = 0.30 on the full 55-game private evaluation (public leaderboard score)". — [HTML §5.6](https://arxiv.org/html/2605.25931)
- The paper explains that the LLM agent was not used for the competition entry because it "cannot call external LLM APIs (Kaggle sandbox, no internet)". — [HTML §4.1](https://arxiv.org/html/2605.25931)
- The kernel URL is given as https://www.kaggle.com/code/farmountain/arc-agi3-v31-zorojuro-hybrid-v9. — [HTML §5.1](https://arxiv.org/html/2605.25931)

**Comparison figure is misattributed**
- AERA compares 0.30 against a "community best at ARC-AGI-3 benchmark release (March 2026)... ≈12.58%". — [HTML §4.1](https://arxiv.org/html/2605.25931)
- The benchmark paper attributes 12.58% to StochasticGoose, the winner of the **July–August 2025 preview competition** on 3 hidden games. — [ARC-AGI-3 paper HTML §6.1](https://arxiv.org/html/2603.24621)

**Critique claims**
- "10 in a single blind step, 5 after one probing action, 1 via repeated ACTION1 presses, 1 via diverse exploration, and 8 via single repeated actions... (50–200 steps)". A null-coordinate ACTION6 call "triggers a TypeError... returns as a WIN signal" on 18 games, confirmed on local arc_agi v0.9.8 and "not confirmed to work on the Kaggle competition server". — [abs](https://arxiv.org/abs/2605.25931); [HTML §5.8](https://arxiv.org/html/2605.25931)
- AERA's scoring formula is RHAE = (1/|L|) Σ min(H_l/A_l, 1.15)². There is no level weighting and no per-environment cap. — [HTML Eq. 1](https://arxiv.org/html/2605.25931)
- The official metric uses linear level weights w_l = l and caps each environment at the weighted fraction of levels completed, so an environment scores at most 100%. — [ARC-AGI-3 paper HTML §4.1](https://arxiv.org/html/2603.24621)

**Conflict with other papers' view of the same games**
- AERA says "FT09 solved in 1 action".
- Rodionov reports ft09 as a 6-level game solved in 109 (GPT-5.4) and 474 (GPT-5.5) actions. OPINE gives the ft09 human baseline as 208 actions. — [AERA HTML §5.5](https://arxiv.org/html/2605.25931); [Rodionov HTML](https://arxiv.org/html/2605.05138); [OPINE HTML Table 3](https://arxiv.org/html/2607.01531)
- The benchmark's validation required that non-tutorial levels "remain unbeaten under uninformed random play" over 1,000,000 steps, and that a random policy not solve a level more often than 1 in 10,000. — [ARC-AGI-3 paper HTML §3.5](https://arxiv.org/html/2603.24621)

### Inferences
- **Verification of "RHAE 0.30 private": not supported.** The paper's own body says 0.30 was a Kaggle public-leaderboard score on a subset, as of 2026-05-17, from a BFS kernel, not from the Qwen2.5-0.5B agent. Treat the abstract's "full 55-game private evaluation" wording as an overstatement unless a Kaggle private-leaderboard record confirms it.
- AERA's reported RHAE values are exact multiples of 1.3225/N (= 1.15²/N):
  - 0.5290 = 2×1.3225/5
  - 0.2645 = 1×1.3225/5
  - 0.2116 = 4×1.3225/25
  - 0.1587 = 3×1.3225/25
  - 0.1058 = 2×1.3225/25
  - 0.0529 = 1×1.3225/25
  - Each "solved" game was therefore credited with one capped level score and no environment cap. That is not the official RHAE, so AERA numbers are not comparable to other papers. (ReAct's 0.388 does not fit this pattern.)
- "Solved in 1 action" and "8 games won by repeating one action 50–200 times" conflict with the benchmark's random-play validation and with multi-level results elsewhere. The most likely explanation is that AERA's win detection or harness counted something other than full-game completion, such as a level-1 or tutorial win, a misparsed state, or an exception path. The public-set "trivially solvable" critique should therefore not be relied on without independent reproduction. This is an inference; the paper itself flags the crash-win path as a library bug.
- The BFS "offline pre-solve cache" idea means searching the real environment by resetting it. The paper does not explain how this avoids spending scored actions on unseen private games.

### Gaps
- No independent confirmation of the Kaggle score (public vs private leaderboard) was found; the Kaggle page was not fetched.
- AERA reports no world-model or program-synthesis results. Its only Kaggle-relevant component (BFS) is not described in enough detail to reimplement from the paper.

## Q4. The ARC-AGI-3 benchmark paper (ARC Prize Foundation, arXiv 2603.24621)

### Takeaway
ARC-AGI-3 consists of 64×64, 16-colour, turn-based games with at least 6 levels, hidden goals, and small action sets. There are 25 public, 55 semi-private, and 55 fully private environments; private games are designed to be harder and out of distribution. Scoring is RHAE: a squared, capped per-level efficiency against the upper-median human, with linearly weighted levels and a per-environment completion cap. Frontier models scored ≤0.5% on semi-private at launch with no harness. The paper does not define "game families".

### Cited Findings
**Metadata and components**
- v2 dated 17 Apr 2026, authored by the ARC Prize Foundation (lead designer Hunter Henry; F. Chollet, M. Knoop, G. Kamradt). — [HTML](https://arxiv.org/html/2603.24621)
- Four evaluated components: Exploration, Modeling, Goal-Setting, and Planning and Execution. "The agent is never told the objective nor provided instructions." — [HTML §2.1](https://arxiv.org/html/2603.24621)

**Format**
- A 64×64 grid with 16 colours per frame. Each turn returns a frame or frame sequence (animations).
- The action space is a subset of five key actions plus Undo and one select-cell (x, y) action. Internal tool calls or reasoning are not counted as actions.
- The engine is Python and runs at 1,000+ FPS. — [HTML §2.3, §3.3](https://arxiv.org/html/2603.24621)

**Design principles**
- Core Knowledge priors only: objectness, basic geometry and topology, basic physics, agentness. No numbers, letters, clip-art, or cultural conventions.
- Novelty test: "whether a single program could solve two different environments while being at least 50% shorter than the concatenation of two independent solution programs".
- Human solvable in about 20 minutes. Difficulty comes through composition. Level 1 is a tutorial ("random agents can occasionally stumble into success"). Multiple mechanics per environment. At least 6 levels. Four-character IDs. — [HTML §3.4](https://arxiv.org/html/2603.24621)

**Validation**
- Random play for up to 50,000 steps must not beat any level by accident. Over 1,000,000 steps, non-tutorial levels must remain unbeaten. Graph-based state-space exploration sets an acceptance threshold that "a random policy should not successfully solve a level more often than 1 in 10,000 times". — [HTML §3.5](https://arxiv.org/html/2603.24621)

**Datasets**
- Public Demo: 25. Semi-Private (tests models behind an API): 55. Fully Private (competition): 55.
- The private set is "significantly more difficult for both humans and AI, and... intentionally out-of-distribution relative to the public set". — [HTML §3.6, Table 1](https://arxiv.org/html/2603.24621)

**Scoring**
- Level score S = min(1.15, h/a)², where h is the upper-median best human action count among 10 testers.
- Environment score E = min(Σ_{l≤k} w_l / Σ w_l, Σ w_l S_l / Σ w_l), with w_l = l.
- Total score T is the mean of E over environments.
- Leaderboard runs cap actions at 5× the human median per level. — [HTML §4.1, §4.3](https://arxiv.org/html/2603.24621)

**Official leaderboard**
- No harness; a single fixed system prompt: "You are playing a game. Your goal is to win. Reply with the exact action you want to take. The final action in your reply will be executed next turn. Your entire reply will be carried to the next turn."
- At release on semi-private: Opus 4.6 (Max) 0.50%, Gemini 3.1 Pro Preview 0.40%, GPT 5.4 (High) 0.20%, Grok-4.20 0.10%.
- Public-set scores "will never" be reported officially, and a released harness "scores 100% on all public environments, using human replay". — [HTML §4.3.1, Table 2](https://arxiv.org/html/2603.24621)

**Harness overfitting evidence**
- "in a variant of environment TR87, Opus 4.6 scores 0.0% with no harness and 97.1% with the Duke harness... yet in environment BP35, Opus 4.6 scores 0.0% under both configurations." — [HTML §4.3.1](https://arxiv.org/html/2603.24621)

**Preview competition (Jul 18 – Aug 19, 2025; 3 public and 3 hidden games)**
- StochasticGoose (Tufa Labs), 12.58%: a CNN plus RL that predicts frame-changing actions (18 levels).
- Blind Squirrel, 6.71%: a directed state graph.
- Also noted: the Duke harness (Python code over the action history) and Symbolica's Arcgentica (orchestrator plus subagents) solved the 3 public preview environments. — [HTML §6](https://arxiv.org/html/2603.24621)

**Human data**
- 486 participants, 414 candidate environments, 2,893 attempts. Median attempt 7.4 min.
- Each environment was attempted by 10 people and needed at least 2 independent full solves. — [HTML §5](https://arxiv.org/html/2603.24621)

**ARC Prize 2026**
- $2M total prize pool. Both tracks run on Kaggle, and prize winners must open-source their solutions. — [HTML §7](https://arxiv.org/html/2603.24621)

### Inferences
- Public-set numbers (all world-model papers) say little about the private set, which is designed to be harder and out of distribution. By construction, public-set RHAE is an optimistic upper bound for a Kaggle entry.
- Papers paraphrase the level-score cap inconsistently. The benchmark paper squares the ratio after capping it at 1.15 (max 1.3225). OPINE writes "(human/agent)² capped at 1.15", and Twin writes e = min{1.15, (h/a)²} ([OPINE HTML](https://arxiv.org/html/2607.01531); [Twin HTML](https://arxiv.org/html/2608.14490)). The per-environment cap makes the difference small for fully cleared games.

### Gaps
- The paper does not list "game families". Other sources describe control schemes only: keyboard, click, and keyboard_click ([Graph-exploration paper](https://arxiv.org/html/2512.24156); [AERA](https://arxiv.org/html/2605.25931)).
- Human baselines changed after launch. DreamTeam reports that 15 games were republished on April 14, 2026, with total baseline actions +11.3% weighted ([arXiv 2605.09650 HTML](https://arxiv.org/html/2605.09650)). Cross-paper scores may therefore use different baselines and game versions.

## Q5. Other 2025–2026 papers reporting ARC-AGI-3 numbers

### Takeaway
An arXiv full-text search for "ARC-AGI-3" returns 19 papers (as of 2026-09-25). By Aug–Sep 2026 the public set is effectively saturated by frontier-model coding-agent harnesses:
- Twin: 93.3 (GPT-5.6 Sol)
- Tycho: 100.00 (GPT-5.6 Sol and Opus 5), 88.49 with Opus 4.8
- Rodionov verification variant: 98.97 (GPT-5.6 Sol)
- Prime Agent: 95.5 (Opus 5)
- PRO-LONG: 97.4 best@2 (Fable 5)
- Schema: self-reported 98.98

Every one of these uses closed frontier models and between 10^7 and 10^9+ tokens. The only no-LLM approach with published numbers is graph exploration, which clears many levels but with near-zero action efficiency.

### Cited Findings
**Search coverage**
- The arXiv search for "ARC-AGI-3" returned 19 results, including 2512.24156, 2603.17683, 2605.05138, 2605.09650, 2605.13037, 2605.25931, 2607.01531, 2607.15439, 2607.20064, 2607.20709, 2607.28287, 2608.04066, 2608.14490, 2608.23552, and 2609.21032. — [arXiv search](https://arxiv.org/search/?query=%22ARC-AGI-3%22&searchtype=all)

**Twin (Skoutnev, Acharya, Longhitano, Udell, Ellis, Drori; arXiv 2608.14490, 14 Aug 2026)** — [abs](https://arxiv.org/abs/2608.14490); [HTML](https://arxiv.org/html/2608.14490)
- Setup: GPT-5.6 Sol through OpenAI Codex, connected to the game only through files, with no game-specific tools.
- Contract: `step(grid, action) -> grid` and `goal_reached(grid) -> bool` on raw 64×64 grids. Internally the model may parse objects and render back to pixels. It starts as an identity stub.
- **Harness-enforced validation**: no scored move is issued while replay of the full log shows any mismatch. This check is enforced by the harness, not left to the prompt.
- Explore, dynamics wall: failing transitions are grouped by local context and ranked by failure frequency, outcome variety, and how little evidence backs the current rule.
- Explore, goal wall: search the twin without R̂ on a larger budget. Rank reachable states by five progress signals: a colour appears, a colour disappears, a compact region changes, the global scene changes, or a new frontier is reached. Shorter paths are preferred on ties.
- Plan: BFS with T̂ as the successor function and R̂ as the goal test, deduplicating full-grid states, with a shortlist of click coordinates.
  - Budgets are depth 8 / 20,000 nodes, widened to 14 / 30,000 for goal discovery.
- ExecuteChecked halts at the first mismatch and adds the transition to the log.
- Goal discovery:
  - A tentative R̂ must be false on every logged frame.
  - Candidates reached without a level boundary are excluded permanently.
  - A level boundary confirms the candidate.
  - If no candidate exists, Probe takes one informative action (an untried control or an unexplored click).
- Levels: twin, log, and context persist across a game's levels. At each level boundary the agent refactors the twin, and cross-level pairs are excluded from the log.
- Results (public 25):
  - 93.3 score; 23/25 games; 179/183 levels; 18 games at 100.0.
  - Fewer actions than first-time humans on 158/179 levels. The first goal hypothesis was correct on 156/179 levels.
  - Same model and bridge without the harness: 61.1 (13 games, 148 levels). Direct play: 7.8.
  - On 13 games that Twin, EWM, and OPINE all fully clear: Twin 3,357 actions vs OPINE 5,367, EWM 5,381, and human 7,485.
  - 92.9% of scored actions executed plans already tested in simulation; 7.1% were probes. Outcomes disagreed with the twin on 20.1% of actions.
  - Worst games: sc25 at 32.7 (a hidden countdown on level 4) and sp80 at 82.1.
- **Compute**: "2.60 billion processed tokens and 91.4 hours of wall-clock inference, averaging roughly 224,000 tokens per scored action". Per-game usage ranged from 5.1M to 625M tokens, and ka59 took 24% of all tokens.
- Code: https://github.com/Alexyskoutnev/TWIN-ARC-AGI-3. Replays: https://arc-agi-3-twin.vercel.app/
- Reported by Twin about other systems: Schema (Zeng et al. 2026) "self-reports 98.98 on the public set through a best-of-two-models fallback per game", and "Claude Opus 5... reports a verified 30.2% on the semi-private evaluation set" in direct play.

**Tycho (Lehmann, Aioanei, Vahdati; arXiv 2607.28287)** — [abs](https://arxiv.org/abs/2607.28287); [HTML](https://arxiv.org/html/2607.28287)
- Formalizes games as "parameterized rendered deterministic Moore machines". Separates actionable observations from animation, level-completion, and game-over frames. The model is a free-form executable hypothesis that the agent may use or bypass.
- Four policies compared with Claude Opus 4.8 under matched budgets: direct (no model), single-actor modeling, actor-requested delegation to a builder subagent (orchestrator), and automatic repair triggered on verification failure.
  - Orchestrator: 88.49 RHAE.
  - Trigger: 83.07.
  - Paired deltas for orchestrator: +9.42 vs no model, +3.14 vs single, +5.43 vs trigger.
- The orchestrator policy with GPT-5.6 Sol reached 100.00 RHAE (183 levels, 7,766 actions). With Opus 5 it reached 100.00 (6,641 actions), using "61% fewer scored actions than the aggregate official human baselines".
- Trigger reached 88.1% accepted transition match but lower RHAE: "Transition match indicates whether a simulator reproduces observed dynamics, not whether it has identified the objective."
- API-equivalent cost, mean / median per game:

| Policy | Mean | Median |
|---|---|---|
| No model | $226 | $106 |
| Single | $291 | $151 |
| Orchestrator | $231 | $169 |
| Trigger | $321 | $264 |
| GPT transfer | $179 | $114 |
| Opus 5 | $119 | $97 |

- Orchestrator token totals over 25 games: 24.1k calls, 390M fresh, 3,286M cache-read, 207M cache-write, and 35.8M output tokens.
- Open-weight comparisons are listed only as future work.
- Code: https://github.com/NIMI-research/Tycho

**PRO-LONG (Fox, Wang, Rosu, Dhingra — the Duke group; arXiv 2607.20064)** — [abs](https://arxiv.org/abs/2607.20064); [HTML](https://arxiv.org/html/2607.20064)
- No mandated world model. The agent keeps a complete, structured interaction log and a coding agent searches it programmatically.
- Results:
  - +18.0 pp on average over a base coding agent across frontier models.
  - Up to 76.1% pass@1, using 4.2–5.8× fewer tokens.
  - Fable 5: 94.6 pass@1 at a 2,000-action budget for $1,500 (150M billed tokens); 97.4% best@2 at $1,750. bp35 alone cost $298.
- GPT-5.5 tool ladder: read-only 23.1 → +grep 27.2 → +Python 38.3 → +write/edit 41.2.
- Log ablation: 41.2 ± 3.5 with the log vs 24.0 ± 2.0 without it.
- Engine: arc_agi 0.9.7 with pinned game versions.
- Code: https://github.com/alexisfox7/PRO-LONG
- PRO-LONG reports that Schema's logs total $6,447 for 99.0 best@2.

**Prime Agent (Prime Intellect; arXiv 2608.23552)**
- A persistent IPython REPL following Recursive Language Models, plus a "Continual Harness" (persisted memories, skills, and prompts) and recursive subagents.
- "raises ARC-AGI-3 RHAE Best@1 from 30% to 95.5%". — [abs](https://arxiv.org/abs/2608.23552)
- Twin reports Prime Agent at 78.3 (164 levels) with GPT-5.6 Sol and 95.5 (179 levels) with Opus 5. — [Twin HTML](https://arxiv.org/html/2608.14490)
- Uses an autonomous prompt adapted from PRO-LONG. — [HTML §3.1](https://arxiv.org/html/2608.23552)
- Code: https://github.com/PrimeIntellect-ai/prime-agent

**DreamTeam / Workspace Optimization (Sarafian, Kaplun, Banner, Soudry, Ginsburg; arXiv 2605.09650)**
- A multi-agent harness with roles: Observer, Simulator, Inductive Explorer, Transductive Explorer, Critic, and others.
- Artifacts: `observable.py` (render, render_event), `dynamics.py` (predict, history, HYPOTHESES), and `strategy.py` (SUB_GOALS, POLICIES).
- Field ownership routes each counterexample to the role that owns the violated schema field.
- Models are mixed Opus 4.6 and GPT-5.5.
- Score: 38.4% RHAE averaged over two runs, versus a prior 36%, with 31% fewer actions. — [abs](https://arxiv.org/abs/2605.09650); [HTML](https://arxiv.org/html/2605.09650)

**NVIDIA Object-Oriented Agents / NOOA (arXiv 2607.20709)**
- A single agent with a world-model skill plus a memory subsystem, under a two-hour fleet cap:
  - GPT-5.5: 50.2% (118 levels), vs 41.7% for the baseline skill and 38.4% with markdown notes instead of memory.
  - GPT-5.6-sol: 85.1%.
- Open models (Nemotron 3 Ultra, Nemotron 3 Nano 30B, GLM-5.2, Kimi K2.6) appear in the paper's capability tests. The ARC-AGI-3 results found are on GPT models only. — [HTML §4.4](https://arxiv.org/html/2607.20709)

**MAP: Map-then-Act (arXiv 2605.13037)**
- Global exploration, then a task-specific cognitive map, then knowledge-augmented execution.
- ARC-AGI-3 with Claude 4.6 Opus: ReAct is near zero, and MAP clears 2–4 levels on the six games shown (level scores 3.34–11.59). "22 of 25" games rise above near-zero.
- The fine-tuned open model MAP-4B (Qwen3-4B-Thinking) is evaluated on ALFWorld, TextCraft, and ScienceWorld, not ARC-AGI-3. — [abs](https://arxiv.org/abs/2605.13037); [HTML](https://arxiv.org/html/2605.13037)

**Graph-Based Exploration (Rudakov, Shock, Cowley; arXiv 2512.24156)**
- Training-free and LLM-free: frame segmentation, salience-prioritized actions, and a directed graph of states and transitions that targets the shortest path to untested state-action pairs.
- "median of 30 out of 52 levels across six games". Ranked 3rd on the preview private leaderboard.
- Code: https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore — [abs](https://arxiv.org/abs/2512.24156)
- Twin characterizes it as reaching deep states "at near-zero action efficiency". — [Twin HTML](https://arxiv.org/html/2608.14490)

**Negative or small results**
- Sensi (arXiv 2603.17683): v1 solved 2 levels, v2 solved 0.
- "The LLM Proposes, the Executive Disposes" (arXiv 2608.04066): "zero level completions across 52 gated runs". — [Sensi](https://arxiv.org/abs/2603.17683); [2608.04066](https://arxiv.org/abs/2608.04066)

**Scaling Discovery through Test-Time Communication (arXiv 2609.21032)**
- On ARC-AGI-3, "a team of k communicating agents... matches the success rate of 4k independent agents". — [abs](https://arxiv.org/abs/2609.21032)

### Inferences
- The converged recipe across EWM, OPINE, Twin, Tycho, and DreamTeam:
  1. Keep an append-only transition log.
  2. Have an LLM write an executable model.
  3. Accept it only on exact replay.
  4. Plan with classical search inside the model.
  5. Execute step by step and halt at the first mismatch.
  6. Repair using the counterexample.
- The differences lie in who enforces validation (harness vs prompt), when the goal is hypothesized (before vs after the first reward), and how modeling labor is split (one agent vs actor/builder).
- Harness gains are real but capability-bound. The same Sol model scores 7.8 direct, 61.1 in plain Codex, and 93.3 in Twin.

### Gaps
- "Schema (Zeng et al. 2026)" (98.98 self-reported) did not appear in the arXiv "ARC-AGI-3" search; no primary source was located.
- The team@k paper's ARC-AGI-3 models and absolute scores were not extracted.
- No paper reports semi-private or private results for a world-model harness.

## Q6. Related (pre-ARC-AGI-3) program-synthesis and theory-based world-model literature

### Takeaway
The ARC-AGI-3 systems descend directly from four lines: WorldCoder's optimism-constrained CEGIS world models, Code World Models (GIF-MCTS, and DeepMind's CWM + MCTS for games), PoE-World's products of programmatic experts, and theory-based RL (EMPA, TheoryCoder). Only the Code World Models / GIF-MCTS work reports a sizable open-weight model (Llama 3 70B). **WorldCoder scores 0.0 on ARC-AGI-3 as run by OPINE.**

### Cited Findings
**WorldCoder (Tang, Key, Ellis; arXiv 2402.12275)** — [abs](https://arxiv.org/abs/2402.12275); [HTML](https://arxiv.org/html/2402.12275)
- A Python world model that must explain its interactions while being "optimistic about what reward it can achieve", with optimism framed as a logical constraint between program and planner.
- Evaluated on gridworlds and task planning. It "can transfer its knowledge across environments by editing its code".
- Uses GPT-4 at temperature 1, with at most 50 LLM requests per synthesis problem, a bandit-based refinement process, and "world models with 250+ lines of code".
- On ARC-AGI-3 as reported by OPINE: 0.0 score, 0 games. — [OPINE HTML Table 1](https://arxiv.org/html/2607.01531)

**Code World Models / GIF-MCTS (Dainese, Merler, Alakuijala, Marttinen; arXiv 2405.15383)** — [abs](https://arxiv.org/abs/2405.15383); [HTML](https://arxiv.org/html/2405.15383)
- Generate, Improve, and Fix steps inside MCTS over code generations. Introduces the CWMB benchmark (18 RL environments).
- CWMB results: — [HTML Table 2](https://arxiv.org/html/2405.15383)
  - Llama 3 70B (3 seeds, 50 LLM calls): GIF-MCTS discrete accuracy 0.84 ± 0.03, return 0.76 ± 0.03; continuous 0.35 / 0.22. WorldCoder re-implementation: 0.79 / 0.60 discrete, 0.32 / 0.19 continuous.
  - GPT-4 Turbo (1 seed, 10 calls): GIF-MCTS 0.91 / 0.81 discrete, 0.40 / 0.26 continuous. WorldCoder: 0.87 / 0.79 and 0.24 / 0.20.
- RTFM: Llama 3 70B GIF-MCTS (50 calls) reached accuracy 0.58 with return −0.11. GPT-4 Turbo reached 0.71 / 0.31 with 10 calls and 1.00 / 1.00 with 50 calls. "The generated CWM is only able to match the performance of the ground-truth simulator when the program is perfect." — [HTML Table 3](https://arxiv.org/html/2405.15383)
- APPS competition (pass@20) with Llama 3 70B: GIF-MCTS 28.3 ± 1.4, WorldCoder 25.1 ± 1.4, zero-shot CoT 23.2 ± 1.3. — [HTML](https://arxiv.org/html/2405.15383)
- Llama 3 generation settings: max_new_tokens 1500, temperature 1.0, top_k 100, top_p 0.8. — [HTML Table 5](https://arxiv.org/html/2405.15383)

**Code World Models for General Game Playing (Lehrach et al., DeepMind; arXiv 2510.04542)**
- The LLM translates rules and trajectories into Python (transition function, legal moves, termination). The code is used as the simulator for MCTS, together with LLM-written heuristic value functions and hidden-state inference functions.
- Across 10 games (4 novel) it "outperforms or matches Gemini 2.5 Pro in 9 out of the 10". — [abs](https://arxiv.org/abs/2510.04542)

**PoE-World (Piriyakulkij, Liang, Tang, Weller, Kryven, Ellis; arXiv 2505.10819)**
- The world model is an exponentially-weighted product of many small LLM-synthesized programmatic experts. It learns stochastic, non-gridworld models (Atari Pong, Montezuma's Revenge) "from just a few observations" and generalizes to unseen levels. — [abs](https://arxiv.org/abs/2505.10819)
- LLM: "gpt-4o-2024-08-06". — [HTML](https://arxiv.org/html/2505.10819)

**TheoryCoder (Ahmed, Tenenbaum, Bates, Gershman; arXiv 2503.20124)**
- Theory-based RL with hierarchical theories. General-purpose abstractions (e.g., "move to") are provided, and the low-level transition model is a Python program synthesized by an LLM from observations. Bilevel planning. Evaluated on grid-world games. — [abs](https://arxiv.org/abs/2503.20124)
- OPINE notes that TheoryCoder hand-writes its PDDL schema. — [OPINE HTML App. B.2](https://arxiv.org/html/2607.01531)
- **TheoryCoder-2** (arXiv 2602.00929) learns abstractions from experience. It is "significantly more sample-efficient than... WorldCoder" on BabyAI, MiniHack, and VGDL games such as Sokoban. — [abs](https://arxiv.org/abs/2602.00929)

**Autumn / AutumnBench (Warrier et al.; arXiv 2510.19788)**
- The WorldTest protocol evaluates environment-level queries.
- AutumnBench has 43 interactive grid-world environments and 129 tasks across three query families, tested with 517 human participants and five frontier models. "humans substantially outperform these models", a gap the authors attribute to exploration and belief updating. — [abs](https://arxiv.org/abs/2510.19788)

**EMPA (Tsividis et al.; arXiv 2107.12544)**
- "performs Bayesian inference to learn probabilistic generative models expressed as programs for a game-engine simulator". Uses object-based relational exploration and heuristic planning.
- "closely matches human learning efficiency on a suite of 90 challenging Atari-style video games". No LLM is involved. — [abs](https://arxiv.org/abs/2107.12544)

**OneLife (arXiv 2510.12088)**
- Conditionally-activated programmatic laws (precondition → effect) inside a probabilistic programming framework, for stochastic worlds, on Crafter-OO. Beats a strong baseline on 16 of 23 scenarios. — [abs](https://arxiv.org/abs/2510.12088)

**Distilling GameCWM generation into small open models (arXiv 2605.24375)**
- SFT + RLVR on Qwen2.5-3B-Instruct over 30 games. SFT improves syntactic correctness and RLVR improves rule adherence of the generated code world models. — [abs](https://arxiv.org/abs/2605.24375)

### Inferences
- WorldCoder's failure on ARC-AGI-3 (0.0 in OPINE's run) and the success of the later systems both point to three ingredients WorldCoder lacks: object discovery from raw frames, strict exact replay rather than an optimism criterion, and long agentic debugging sessions. OPINE attributes the difference to single-program search not scaling to pixel worlds with unknown ontology. — [OPINE abs](https://arxiv.org/abs/2607.01531)
- PoE-World's product-of-small-experts design and OneLife's precondition-effect laws are natural fits for weaker models: small local programs are easier to write and repair than one monolithic engine. Neither has been tested on ARC-AGI-3.

### Gaps
- The original AutumnSynth paper (Das et al., POPL 2023, "Combining Functional and Automata Synthesis to Discover Causal Reactive Programs") was not retrieved. Its method and numbers are not covered.
- Object-centric model-based RL specifically (e.g., OC-STORM, Schema Networks) was not researched beyond citations inside the ARC-AGI-3 papers (Kansky et al. 2017; Kipf et al. 2020).
- Exact WorldCoder, PoE-World, and TheoryCoder numeric results were not extracted; abstract-level claims only.

## Q7. Which methods have been demonstrated with OPEN-weight models, and at what performance drop?

### Takeaway
**No executable-world-model or program-synthesis ARC-AGI-3 paper reports results with an open-weight model.** Every strong ARC-AGI-3 result uses GPT-5.4/5.5/5.6 Sol, Claude Opus 4.8/5, or Fable 5. The only ARC-AGI-3 open-weight result is AERA's Qwen2.5-0.5B/1.5B prompting agent. It is not a world-model method and its scoring is non-standard (0.2116, or 0.164 ± 0.059 mean over 8 runs). The best evidence of an open-vs-closed drop in code world models is GIF-MCTS: Llama 3 70B vs GPT-4 Turbo on CWMB and RTFM.

### Cited Findings
- AERA uses Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct on CPU FP32. 25-game b=1 score 0.2116 (4/25). Its Kaggle entry replaced the LLM with BFS because API LLMs are unavailable offline. — [AERA HTML](https://arxiv.org/html/2605.25931)
- Tycho lists "comparisons across frontier and open-weight models" as future work. — [Tycho HTML](https://arxiv.org/html/2607.28287)
- Prime Agent evaluates open models (Kimi K3, DeepSeek V4 Pro, GLM 5.3; GLM-5.2 in long-context tables) on non-ARC tasks. The ARC-AGI-3 scores found are for GPT-5.6 Sol and Opus 5. — [Prime Agent HTML](https://arxiv.org/html/2608.23552); [Twin HTML](https://arxiv.org/html/2608.14490)
- NOOA lists Nemotron 3 Nano 30B, Nemotron 3 Ultra, GLM-5.2, and Kimi K2.6 in capability tests ("Small/efficient models pass 96.0% of records; large/frontier models pass 99.2%"). Its ARC-AGI-3 results are on GPT-5.5 and GPT-5.6-sol. — [NOOA HTML](https://arxiv.org/html/2607.20709)
- GIF-MCTS on CWMB: — [GIF-MCTS HTML Table 2](https://arxiv.org/html/2405.15383)
  - Discrete accuracy / return: Llama 3 70B 0.84 / 0.76 (50 LLM calls) vs GPT-4 Turbo 0.91 / 0.81 (10 calls).
  - Continuous: 0.35 / 0.22 vs 0.40 / 0.26.
- GIF-MCTS on RTFM: Llama 3 70B 0.58 accuracy / −0.11 return (50 calls) vs GPT-4 Turbo 0.71 / 0.31 (10 calls) and 1.00 / 1.00 (50 calls). — [GIF-MCTS HTML Table 3](https://arxiv.org/html/2405.15383)
- Capability dependence within closed models on ARC-AGI-3 (Rodionov ablation, mean over variants): 34.36 (gpt-5.4-high) → 48.05 (gpt-5.4-xhigh) → 58.50 (gpt-5.5-high) → 72.52 (gpt-5.5-xhigh). — [arXiv 2607.15439 HTML](https://arxiv.org/html/2607.15439)
- Direct play, the same GPT-5.6 Sol model: 7.8 without a harness vs 93.3 with Twin. — [Twin abs](https://arxiv.org/abs/2608.14490)
- MAP-4B (fine-tuned Qwen3-4B-Thinking) and the GameCWM distillation (Qwen2.5-3B) are open-weight, but neither was evaluated on ARC-AGI-3. — [MAP HTML](https://arxiv.org/html/2605.13037); [2605.24375](https://arxiv.org/abs/2605.24375)

### Inferences
- On the older, easier CWMB setting, a 70B open model with 5× more LLM calls came within about 0.05–0.07 accuracy of GPT-4 Turbo. On the harder RTFM task, it fell short of a perfect model, and a non-perfect code world model gave near-zero or negative return.
- ARC-AGI-3 rewards only near-perfect models: exact replay plus correct goal. The ablation shows a roughly 38-point swing across closed-model capability levels alone. Expect a much larger drop for a ~30B open model than the CWMB gap suggests. This is not measured anywhere.

### Gaps
- No measured ARC-AGI-3 RHAE for any open-weight model of about 27–32B in any world-model harness.

## Q8. Common verified insights: state representation, goal inference, level transfer, mismatch handling

### Takeaway
The papers agree on five points:
1. Verify at the level of the **exact settled 64×64 grid** while letting the model use objects internally.
2. Predict the **settled** frame after animations.
3. Keep **one model that must replay all prior levels** and refactor it at level boundaries.
4. Treat any mismatch as a **blocking counterexample**.
5. Goal inference, not dynamics, is the harder problem.

They disagree on two points: whether to hypothesize goals before the first reward (Twin) or only after (OPINE), and whether automatic repair helps (Tycho found it hurt).

### Cited Findings
**State representation**
- EWM: settled ASCII frames. The engine state is a dict with `level` plus an internal representation chosen by the agent. The renderer must reproduce frames cell-exactly, and override hooks count as "modeling debt". — [arXiv 2607.15439 HTML](https://arxiv.org/html/2607.15439)
- OPINE: typed objects (key, type, attributes such as position, visibility, rotation, and pixel pattern) from a synthesized `extract_objects`. Rules are per type with local context. — [OPINE HTML §3.1, App. H](https://arxiv.org/html/2607.01531)
- Twin: raw-grid contract. "Raw-grid outputs permit cell-by-cell verification, while the implementation may parse objects, update an abstract state, and render back to pixels for more efficient search." — [Twin HTML](https://arxiv.org/html/2608.14490)
- Tycho: separates actionable observations from animation, level-complete, and game-over frames. Deterministic Moore-machine formalization. — [Tycho abs](https://arxiv.org/abs/2607.28287)
- DreamTeam: ZState fields (object_positions, object_states, sprite_overrides) with render and predict functions. — [DreamTeam HTML](https://arxiv.org/html/2605.09650)

**Animations and multi-frame actions**
- Predict the settled frame and use intermediate frames as evidence only. — [OPINE App. A.5](https://arxiv.org/html/2607.01531); [Rodionov ablation §4.6](https://arxiv.org/html/2607.15439)

**Goal inference**
- OPINE: before the first level-clear, act on the observed reward. The goal predicate is fitted only after reward, checked by replay, and screened by a static anti-cheat check. The planner is gated on at least one cleared level. — [OPINE HTML](https://arxiv.org/html/2607.01531)
- Twin: hypothesize goals before any reward. Rank candidate states by five progress signals; a candidate must be false on all logged frames; reached non-goals are excluded. The first hypothesis was correct on 156/179 cleared levels.
  - "Building a usable world model is simpler than anticipated, whereas the harder problem is inferring the right goal." — [Twin abs/HTML](https://arxiv.org/abs/2608.14490)
- EWM: the engine returns LEVEL_COMPLETED as part of `game_status`, and the planner verifier requires plans to reach LEVEL_COMPLETED on solved levels. — [EWM HTML](https://arxiv.org/html/2605.05138)
- Tycho: higher transition accuracy under automatic repair did not yield higher RHAE, because the objective must also be identified. — [Tycho abs](https://arxiv.org/abs/2607.28287)

**Level transfer**
- Benchmark design: "Later levels are... expected to require the accumulation and integration of concepts learned earlier." — [ARC-AGI-3 HTML §3.4](https://arxiv.org/html/2603.24621)
- EWM: the model must "remain valid for all solved levels so far", and levels "usually extend earlier mechanics". — [2607.15439 prompt](https://arxiv.org/html/2607.15439)
- Twin: persistent twin, log, and context across levels, with a refactor at each boundary. — [Twin HTML](https://arxiv.org/html/2608.14490)
- OPINE: per-type rules transfer, and the planner is re-verified from the entry states of all cleared levels. — [OPINE HTML](https://arxiv.org/html/2607.01531)

**Mismatch handling**
- EWM: the executor halts and records artifacts; the prompt says a mismatch is blocking, but the agent can bypass the executor. — [EWM HTML](https://arxiv.org/html/2605.05138)
- OPINE: mismatch → counterexample → synthesizer re-fires in a fresh context, with a deferral window and a stall guard. — [OPINE App. A.4](https://arxiv.org/html/2607.01531)
- Twin: the harness blocks scored actions until the twin replays the full log. 20.1% of actions mismatched. 31 previously mispredicted situations recurred and were all predicted correctly after repair. — [Twin HTML](https://arxiv.org/html/2608.14490)
- Tycho: automatic repair triggered on verification failure (83.07) scored below actor-requested delegation (88.49). — [Tycho abs](https://arxiv.org/abs/2607.28287)
- Hidden state and timers are the recurring failure source: OPINE puts hidden-state games out of scope, and Twin's worst game, sc25, has a hidden countdown. — [OPINE §6](https://arxiv.org/html/2607.01531); [Twin HTML](https://arxiv.org/html/2608.14490)

### Inferences
- A robust design pattern:
  - Raw-grid exact-replay verification, harness-enforced.
  - An object layer internal to the model.
  - Settled-frame prediction.
  - A single cumulative model across levels.
  - Explicit goal-candidate generation before the first reward (Twin-style), with a Twin-like "false on all logged frames" filter.
  - Counterexample-triggered repair with a stall guard.
- Where to spend LLM effort: when to model, repair, or bypass matters as much as model fidelity (Tycho).

### Gaps
- No controlled ablation isolates goal-before-reward (Twin) vs goal-after-reward (OPINE) under the same model.

## Q9. Feasibility under Kaggle constraints (offline, one GPU, open-weight ~27–32B, limited time)

### Takeaway
None of the published world-model systems has been shown to run under Kaggle-like constraints. Their token and time budgets exceed a single-GPU offline setting by one to two orders of magnitude:
- Twin: 2.60B tokens and 91.4 h for 25 games.
- Tycho: about 36M output tokens and about 3.9B total tokens for 25 games.
- EWM: up to about 48 h per hard game.

Their accuracy also depends heavily on frontier-model capability. The pieces that transfer cheaply are the non-LLM ones: the exact-replay verifier, halt-on-mismatch executor, BFS planner with state dedupe, goal-candidate ranking, the Dirichlet effect table, and graph exploration.

### Cited Findings
- Compute and token budgets:
  - Twin: 2.60B processed tokens; 91.4 h of wall-clock inference; about 224k tokens per scored action; 5.1M–625M tokens per game. — [Twin HTML](https://arxiv.org/html/2608.14490)
  - Tycho, Opus 4.8 orchestrator over 25 games: 35.8M output tokens, 390M fresh input, 3,286M cache-read. Opus 5 run: 23.4M output tokens, mean $119 per game. — [Tycho HTML Table 6](https://arxiv.org/html/2607.28287)
  - EWM: difficult games "may take up to roughly 48 hours". — [EWM HTML](https://arxiv.org/html/2605.05138)
  - Rodionov ablation: verification variant 90–205M cost tokens per 25 games. — [2607.15439 HTML](https://arxiv.org/html/2607.15439)
  - PRO-LONG: 150M billed tokens for Fable 5 at a 2,000-action budget. — [PRO-LONG HTML](https://arxiv.org/html/2607.20064)
- AERA states that API LLM agents are "not competition-eligible as-is" because of the no-internet sandbox. — [AERA HTML §4.1](https://arxiv.org/html/2605.25931)
- Non-LLM components with published numbers:
  - Graph exploration: 30/52 preview levels (median), 3rd on the preview private leaderboard. — [2512.24156](https://arxiv.org/abs/2512.24156)
  - Twin's BFS limits: depth 8 / 20k nodes, and 14 / 30k for goal discovery. — [Twin HTML](https://arxiv.org/html/2608.14490)
- The private set is harder and out of distribution relative to public. — [ARC-AGI-3 HTML §3.6](https://arxiv.org/html/2603.24621)

### Inferences
- Rough budget arithmetic (my assumption, not from the papers): single-stream decode for a ~30B model on one GPU runs at roughly 30–60 tokens/s. At that rate, even Tycho-Opus-5's roughly 0.94M output tokens per game (23.4M / 25) would take about 4–9 hours of decode per game, before prefill. Across 55 private games that is far outside a typical Kaggle time limit. Any Kaggle port must cut LLM output by at least 10–100×. Options include batching or parallelizing across games, using the LLM only for rule proposals on counterexamples (OPINE-style cadence), and doing search and verification in plain Python.
- Most promising Kaggle-feasible hybrid (inference):
  - A non-LLM core: segmentation into objects, a graph or BFS explorer, and a Dirichlet effect table for exploration priority.
  - A cumulative per-type rule model with exact replay against settled frames.
  - An open ~30B coder LLM called sparingly to propose or repair small per-type rules (PoE-World/OneLife-style small programs) and goal predicates (Twin's candidate filter).
  - There is no published evidence for its score.
- Public-set scores (58–100 for frontier harnesses) should not be taken as estimates for the private Kaggle set.

### Gaps
- No paper reports any world-model harness running offline on one GPU, or with a 27–32B open model, on ARC-AGI-3.
- The Kaggle 2026 competition's exact hardware and time limits were not researched here (outside this scope).
