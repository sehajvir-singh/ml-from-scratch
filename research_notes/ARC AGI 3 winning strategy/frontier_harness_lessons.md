# Frontier ARC-AGI-3 Harness Lessons and What Transfers to a Local ~30B Model on Kaggle (as of 2026-09-25)

Scope note: "Frontier-API" = results that call closed models (OpenAI/Anthropic/Google/xAI) over the internet. None of these can run in the Kaggle ARC Prize 2026 ARC-AGI-3 competition, which has internet disabled during evaluation. "Kaggle-eligible" = offline, open-weight, single-machine submissions. Every section below keeps the two apart.

Research method caveat: openai.com returned HTTP 403, and X/Kaggle discussion pages often returned only titles or 402. Several numbers therefore come from secondary coverage (officechai, dev.to, TheNextWeb, the-decoder) or from WebFetch summaries of primary pages. Where a number was only in a search snippet or conflicts across sources, this is flagged.

---

## Q1. OpenAI, "How enabling two settings tripled our ARC-AGI-3 scores": the settings, numbers and mechanism

### Takeaway
The two settings are **retained reasoning** (the model keeps its private chain of thought across actions) and **compaction** (older context is summarized instead of truncated). Together they took GPT-5.6 Sol from **13.3% to 38.3%** on the ARC-AGI-3 *public* set, with **about 6x fewer output tokens**. The mechanism: the official harness threw away the model's reasoning after every action and truncated history once it passed 175,000 characters, so the model had to "re-figure the game from scratch on each turn".

### Cited Findings
- The two settings are "retained reasoning and compaction". OpenAI already uses both in ChatGPT and Codex. — [OpenAI (title and snippet via search)](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/); [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/)
- Scores: GPT-5.6 Sol got 13.3% on the ARC-AGI-3 public set with the official harness and 38.3% with retained reasoning and compaction. Output tokens dropped by "roughly six times fewer output tokens per game". — [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/); [dev.to](https://dev.to/alifar/openai-says-two-api-settings-tripled-gpt-56-sols-arc-agi-3-score-1de8)
- Mechanism, as quoted in coverage: "After every action the agent took, its private reasoning was thrown away, so the model had to re-figure the game from scratch on each turn." The official harness also used "rolling truncation, discarding the oldest parts of the conversation once it grew past 175,000 characters". — [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/)
- Compaction "summarizes older context instead of dropping it outright". — [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/)
- OpenAI's recommendation is to "use the Responses API rather than the older Chat Completions API, keep reasoning retained across turns". Reasoning "persists across turns by default if a developer passes along the previous response ID". — [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/)
- Publication date: July 30, 2026. — [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/); [dev.to](https://dev.to/alifar/openai-says-two-api-settings-tripled-gpt-56-sols-arc-agi-3-score-1de8)
- Summary quote on X: "The harness was not letting it remember what it had learned. We found that enabling two API settings tripled our scores with 6x fewer output tokens." — [Viv (@Vtrivedy10) on X](https://x.com/Vtrivedy10/status/2082623033785618695)
- ARC Prize defended its setup. It uses a "no harness" setup to "prevent developers from tuning a harness around a specific model's quirks". — [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/)
- The official ARC Prize (semi-private) score for GPT-5.6 is 7.78% (Jul 9, 2026). This is lower than OpenAI's public-set 13.3%/38.3% because the set and configuration differ. — [ARC Prize results](https://arcprize.org/results); [dev.to](https://dev.to/alifar/openai-says-two-api-settings-tripled-gpt-56-sols-arc-agi-3-score-1de8)
- On Hacker News, commenters questioned harness fairness. They asked whether each lab's "standard commercial harness" should count, and whether Anthropic's Opus 5 registered scores used the same settings. — [HN thread](https://news.ycombinator.com/item?id=49104184)

### Inferences
- The effect is large because ARC-AGI-3 is a long-horizon POMDP. The key state is the agent's current hypothesis about the game's rules, and a stateless-reasoning harness destroys exactly that. The 6x drop in output tokens fits the model no longer re-deriving the same hypothesis on every step.
- For a local model, "retained reasoning" simply means not stripping earlier `<think>` blocks from the message history (or keeping a condensed version of them). "Compaction" means summarizing old turns instead of dropping them. Both are pure harness choices and need no API feature. **Unverified from my own knowledge:** many open-weight reasoning models (for example Qwen3-family chat templates) strip earlier-turn reasoning by default, so this has to be overridden deliberately. Retaining it may also be slightly off the model's training distribution. Test this empirically.

### Gaps
- I could not read the OpenAI article directly (403). I did not get its full ablation (each setting alone versus both), its per-game breakdown, or its cost figures.
- Whether 38.3% was pass@1 or best-of-k is not stated in the coverage I retrieved.

---

## Q2. Official ARC-AGI-3 leaderboard (Sep 2026): top systems, scores, cost, harness

### Takeaway
On the **official ARC Prize (semi-private) leaderboard**, the like-for-like "Standard harness" order is: GPT-6 Astra **62.7%** (max reasoning, about $26K total), Claude Opus 5 **30.16%** (High), Gemini 3.8 Flash 10.4% (BenchLM only), GPT-5.6 **7.78%**, Grok 4.6 **2.11%**, GPT-6 Luna 0.59%. ARC Prize now also reports a separate **"Provider Adapter" harness** (native retained reasoning plus compaction), under which Astra reaches **96.7 to 99.95%**. On the 25 public games, third-party custom harnesses around Claude Opus 5 reach **99.95 to 100%**. All of these are frontier-API results and none are Kaggle-eligible. Kaggle-eligible systems (Qwen 3.6 27B / Gemma-4-31B) score in the low single digits on the public set.

### Cited Findings: official ARC Prize results (frontier API, NOT Kaggle-eligible)
- ARC Prize results page, ARC-AGI-3 column: GPT-6 Astra 99.95% (Sep 2, 2026); Grok 4.6 2.11% (Aug 11); Claude Opus 5 30.16% (Jul 24); GPT-5.6 7.78% (Jul 9); GPT-6 Luna 0.59% (Sep 22); Claude Opus 5.5 listed Sep 22 with no ARC-AGI-3 score yet. — [ARC Prize results](https://arcprize.org/results)
- Astra by harness (semi-private): Standard harness at max reasoning is 62.71% at $26,098 total cost. Provider Adapter at max reasoning is 98.55% at $17,332. Provider Adapter at high reasoning is 99.95% at $18,817. — [Kingy AI summary of ARC Prize evidence update, Sep 4 2026](https://kingy.ai/news/astra-arc-agi-3-benchmark-paradox/); [ARC Prize Astra blog](https://arcprize.org/blog/astra)
- The ARC Prize Astra blog says Standard harness scores range from 17.5% (low reasoning) to 62.7% (max), and Provider Adapter scores from 96.7% to 99.9%. The adapter used "49% fewer tokens" and "3.66x faster aggregate elapsed time". — [ARC Prize, "OpenAI's GPT-6 Astra on ARC-AGI-3"](https://arcprize.org/blog/astra)
- Astra used fewer actions than humans on 96% of levels and averaged 51.7% fewer actions per level. The human baseline comes from about 500 general-public participants. — [ARC Prize Astra blog](https://arcprize.org/blog/astra)
- Harness definitions from ARC Prize. **Standard:** "provider-neutral text history and asks the model to preserve useful discoveries in visible notes", with `manual_rolling` context. **Provider Adapter:** "uses the provider's native conversation and reasoning state", with `continuous_conversation`, "native compaction when the provider supplies it and a domain-neutral harness summary otherwise". For Anthropic it "preserves native thinking blocks between actions" and uses prompt caching. For xAI it uses "xAI-native encrypted reasoning replay and separate Responses compaction". "Both harnesses use the same games, actions, limits, and scoring." — [arcprize/arc-agi-3-benchmarking GitHub](https://github.com/arcprize/arc-agi-3-benchmarking)
- Cost per game: Chollet said Astra reaches "nearly 100% with a continuous conversation harness and custom compaction, at a cost of roughly $360 per game", and "66%" with the standard harness. Note that 66% conflicts with the 62.7% on the ARC Prize blog, and this figure comes from a search snippet of the X post. — [François Chollet on X](https://x.com/fchollet/status/2095598451115614371)
- Opus 5 (High) scored 30.16% and was tested only at High "due to short testing window". It fully solved 5 public demo environments (AR25, FT09, LP85, R11L, S5I5), "five additional Public Demo environments that no model had previously beaten". The results page shows no cost per game. — [ARC Prize Opus 5 results](https://arcprize.org/results/anthropic-claude-opus-5)
- BenchLM (Sep 2026) ranks: GPT-6 Astra 62.7%, Claude Opus 5 30.2%, Gemini 3.8 Flash 10.4%, GPT-5.6 Sol 7.8%, Grok 4.6 2.1%, Claude Opus 4.8 1.5%, GPT-5.6 Terra 0.8%, and 7 others at 0.1 to 0.4%. BenchLM notes that "ARC Prize reports Standard and Provider Adapter harness runs separately". — [BenchLM ARC-AGI-3](https://benchlm.ai/benchmarks/arcagi3)
- At launch (March 2026) all frontier models scored under 1%: Gemini 3.1 Pro Preview 0.37%, GPT-5.4 (High) 0.26%, Opus 4.6 (Max) 0.25%, Grok-4.20 0.00%. — [ARC-AGI-3 technical report, arXiv 2603.24621](https://arxiv.org/html/2603.24621v1)
- In May 2026, GPT-5.5 scored 0.43% and Opus 4.7 scored 0.18% on the semi-private set. — [ARC Prize analysis blog](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis)
- The official leaderboard shows only systems that cost under $10,000 to run. — [ARC Prize leaderboard](https://arcprize.org/leaderboard). This conflicts with the Astra runs listed at $17K to $26K. They may appear only on the results page rather than the leaderboard plot.

### Cited Findings: custom (community) harnesses, frontier API, public set only, NOT Kaggle-eligible
- **Strands Agents (AWS), Claude Opus 5:** completed all 183 levels across the 25 public environments with **99.95% RHAE** in one 8-hour run, spending about **$830** in tokens. It matched or beat human action efficiency on 160 of 183 levels and got the maximum per-level score on 150. — [Strands blog](https://strandsagents.com/blog/our-production-sdk-hit-99-95-on-arc-agi-3/); [AWS Builder Center](https://builder.aws.com/content/3IY3vnU0okFHvXMjiHnEpwG1WBA/how-a-strands-agent-took-claude-opus-5-from-30percent-to-9995percent-on-arc-agi-3)
- **NVIDIA AVO, Claude Opus 5:** **100.00 RHAE** on all 25 public environments and 183 levels using **6,624 environment actions**, about 12% fewer than VISTA's 7,542. Observations were "an exact 64 x 64 text grid, with no images". — [NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/)
- **PRO-LONG (academic, arXiv 2607.20064):** Fable 5 reaches **97.4% best@2 at $1,750 total**. It adds +18.0 pp on average over a base coding agent and uses 4.2 to 5.8x fewer tokens than specialized harnesses. — [arXiv 2607.20064](https://arxiv.org/abs/2607.20064); [GitHub](https://github.com/alexisfox7/PRO-LONG)
- **Tycho (programmatic world models, arXiv 2607.28287):** GPT-5.6 Sol and Opus 5 both reach **100.00 RHAE** (all 183 levels). Opus 5 used 61% fewer scored actions than official human baselines. — [arXiv 2607.28287](https://arxiv.org/abs/2607.28287)
- **Schema (Impossible Research):** "~99%" on the 25 public games with frontier models. — [schema-harness.github.io](https://schema-harness.github.io/)
- ARC Prize's policy: the official leaderboard "explicitly excludes domain-specific harnesses", and a separate community leaderboard allows them. — [ARC-AGI-3 technical report](https://arxiv.org/html/2603.24621v1)

### Cited Findings: Kaggle-eligible (offline, open weights)
- Milestone #1 (June 30, 2026) winners: 1st **Tufa Labs "The Duck"** (Qwen 3.6 27B FP8, local), 2nd **Reki** (Gemma-4-31B, local), 3rd **Md Boktiar Mahbub Murad "forge"** (Gemma-4-31B, local). — [ARC Prize Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- The Duck scored a mean of **1.6002 ± 0.4475** over 25 public games × 20 tries. The unit appears to be RHAE %, but the source does not say explicitly. Some games are solved consistently for over 40% of levels, and some never pass level 1. It is "an order of magnitude cheaper on each game" than GPT-5.4. — [Tufa Labs Duck write-up](https://tufalabs.ai/research/duck-harness/)
- A Medium post (low-quality aggregator) says Tufa Labs leads the current Kaggle leaderboard phase, which is computed on about 50% of the test data. — [Medium/syntellect_ai](https://medium.com/@ccro8990/the-official-live-leaderboard-for-the-arc-agi-3-machine-learning-competition-hosted-on-kaggle-part-06dbe491c8dc)
- Kaggle environment: "Nvidia T4 ×2" is the default. "RTX 6000 is reserved for ARC-AGI-3 notebooks". Internet is disabled in all accelerated sessions. — [ARC Prize 2026 docs](https://docs.arcprize.org/arc-prize-2026). Tufa Labs describes the constraint as a single GPU. — [Tufa Labs](https://tufalabs.ai/research/duck-harness/)
- Prizes: $700K grand prize for 100%, $75K for top scores, and $75K in milestone prizes (Milestone #2 on Sep 30, 2026). All code must be open-sourced to be eligible. — [ARC Prize 2026 ARC-AGI-3 competition page](https://arcprize.org/competitions/2026/arc-agi-3)

### Inferences
- Rough cost per game: Astra Provider Adapter at $18,817 over 55 semi-private games is about $342/game, which matches Chollet's "~$360 per game". Standard max at $26,098/55 is about $475/game. Strands' $830 over 25 public games is about $33/game, which suggests a lean file-based harness is roughly 10x cheaper per game than Astra's native-context runs. These are my own divisions, not published figures.
- The gap between the Standard harness (62.7%) and the Provider Adapter (99.9%) for the same model is about 37 pp. For Opus 5 the gap between official (30%) and custom (about 100%) is about 70 pp. Harness choices matter as much as model generation, which motivates reproducing the harness pieces locally.
- The Kaggle-eligible frontier (about 1.6 on the public set for the Milestone 1 winner) is roughly 20 to 60x below frontier-API results. Harness lessons may transfer, but the base-model gap is huge.

### Gaps
- I could not fetch the live Kaggle ARC-AGI-3 leaderboard (the page returned only its title), so I have no current September public-LB scores.
- I have no official per-game costs for Opus 5, Grok 4.6, or Gemini 3.8 Flash.
- Gemini 3.8 Flash (10.4%) appears only on BenchLM, not on the ARC Prize results page I fetched. Its harness and verification status are unconfirmed.
- The exact Kaggle runtime limit (hours) and the RTX 6000 variant (Ada 48 GB or Pro 96 GB) were not found.

---

## Q3. Lab and third-party writeups: harness choices (Anthropic, Google DeepMind, xAI, NVIDIA, AWS Strands, academics)

### Takeaway
The labs mostly published scores and a few observed behaviors. OpenAI is the only lab with a harness writeup (Q1). The detailed harness engineering came from third parties: AWS Strands, NVIDIA AVO, PRO-LONG, Tycho, Schema, and Symbolica's Arcgentica. The winning pattern in all of them is a **coding agent with a Python sandbox**, **lossless external state on disk** (a board file plus an append-only log), **the agent writing its own game model or solver code**, and **some form of stagnation or loop control**.

### Cited Findings
- **Anthropic / Opus 5:** ARC Prize attributes the 30.2% to "stronger logical reasoning, which enables more autonomous exploration, planning, and execution". Opus 5 spontaneously translated tasks into **algebraic notation** and wrote "reflection equations". Official scores count only the model, and coverage speculates it "would likely score even higher if used within Claude Code". — [The Decoder, Jul 26 2026](https://the-decoder.com/anthropics-opus-5-blows-past-fable-5-and-gpt-5-6-sol-on-the-benchmark-designed-to-measure-real-intelligence/)
- **OpenAI / Astra:** it built "custom algebraic notation to track game state compactly (e.g., `L8: hub q2 (8↓). Lengths: 14=1…`)". Given a sandbox (the PRO-LONG harness), it "created game-specific tools including parsers, solvers, and libraries". — [ARC Prize Astra blog](https://arcprize.org/blog/astra)
- **xAI / Grok 4.6:** 2.11% official. The Provider Adapter run uses "xAI-native encrypted reasoning replay and separate Responses compaction". — [ARC Prize results](https://arcprize.org/results); [arc-agi-3-benchmarking](https://github.com/arcprize/arc-agi-3-benchmarking)
- **Google DeepMind:** I found no official Google harness writeup for ARC-AGI-3. A "Continual Harness: An Efficient Self-Improving Agent on ARC-AGI-3" study (Ruirong Feng, Seth Karten et al.) was supported with Gemini API credits from Google DeepMind (per the search snippet; the page returned HTTP 402). — [Seth Karten on X](https://x.com/sethkarten/article/2072034978112889328)
- **AWS Strands harness:** tools are bash, Python, file read/write, and grep. The numeric grid is rendered as text. State lives in `current_board.txt`, and each move is appended to `logs.txt`. The agent writes a plan to `actions.json`, and a runner validates and executes it with a per-cycle action cap (`_action_cap`). The agent generated 734 scripts across 25 games. This design follows the PRO-LONG research. — [Strands blog](https://strandsagents.com/blog/our-production-sdk-hit-99-95-on-arc-agi-3/)
- **NVIDIA AVO ("Agentic Variation Operators"):** persistent memory of "prior implementations, evaluation results… and accumulated reasoning". A **supervisor** "monitors the broader trajectory for stagnation or repeated unproductive cycles and can redirect the main agent". The loop inspects context, plans, implements, and evaluates. No ablations and no open-weight results were published. — [NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/)
- NVIDIA's VP of Product says the supervisor "nudges the main agent like a CEO would". The same article mentions that Nemotron 3 Ultra in LangChain's "Deep Agents" harness reached "roughly the same level as Claude Opus 4.8" at $4.48 versus $43.48 per run. NVIDIA cautions these "are not a direct comparison", and the benchmark behind that claim is unclear. — [XenoSpectrum](https://xenospectrum.com/en/nvidia-avo-harness-arc-agi-3/)
- **PRO-LONG architecture:** write = append to `logs.txt` "a header (the action number, level, attempt, and score), the agent's summarized plan, the selected action, and the resulting board". Read = programmatic search with grep, regex, and Python (stdlib only). The prompt is about 30 lines. Its principles are simplicity, losslessness, and compatibility with coding agents. Search stays tractable over logs of "100k+ lines". — [PRO-LONG arXiv HTML](https://arxiv.org/html/2607.20064v2)
- **PRO-LONG tool ablation (GPT-5.5, public set):** read-only 23.1%, + grep/regex 27.2%, + Python 38.3%, + write/edit 41.2%. Python alone adds about 10.8 pp. — [PRO-LONG](https://arxiv.org/html/2607.20064v2)
- **PRO-LONG memory ablation:** clearing the workspace after each call barely hurts (40.7% vs 41.2%), but removing the log drops performance (19.9% vs 24.0% in the reported comparison). Conclusion: "the programmatic log rather than self-authored notes drives gains". — [PRO-LONG](https://arxiv.org/html/2607.20064v2)
- **PRO-LONG pass@1 (500-action budget):** GPT-5.5 41.2% (vs WorldModeler 45.1% at 5.8x higher cost). Opus 4.6 42.4% (prior best about 9%). GPT-5.5 best@5 60.1%. The large pass@1-to-best@k gap indicates high variance. — [PRO-LONG](https://arxiv.org/html/2607.20064v2). The abstract says "up to 76.1% pass@1". The fetched summary also reports 82.1% for Fable 5 against Schema's 84.4%, with an unclear metric. — [arXiv abs](https://arxiv.org/abs/2607.20064). Treat the exact Fable 5 pass@1 as unresolved.
- **PRO-LONG, where memory helps:** the gains are largest when "the current board does not fully determine the game dynamics" (for example g50t with hidden "ghost" mechanics and 320,000+ line logs, and the m0r0 multi-agent maze). It adds little on ft09 and cd82. One agent spontaneously wrote `regress.py` to "replay every action in log.txt and verify its coded game model predicts the logged board states". — [PRO-LONG](https://arxiv.org/html/2607.20064v2)
- **Baselines compared in PRO-LONG:** WorldModeler (Rodionov; about 600-line prompt, vision-enabled, GPT-5.5/Codex). Schema (Impossible Research; 12 custom MCP tools, a `step(grid, action)` function, BFS planning). Arcgentica (Symbolica; 4-agent orchestration with a shared hypothesis database). — [PRO-LONG](https://arxiv.org/html/2607.20064v2). In Arcgentica, an orchestrator delegates to subagents that "return compressed textual summaries, constraining context growth". — search snippet via [Chollet-related results / ARC-AGI-3 report](https://arxiv.org/pdf/2603.24621)
- **Tycho:** builds executable, game-specific world models (formalized as parameterized Moore machines). It separates actionable frames from animation and completion frames, and it models, tests, plans, and repairs hypotheses, with a policy for when to build, repair, or bypass the model. Automatic repair improved model accuracy but lowered RHAE to 83.07, versus 88.49 for actor-requested model-builder delegation (Opus 4.8). That shows a tension between transition accuracy and efficient play. — [Tycho arXiv 2607.28287](https://arxiv.org/abs/2607.28287)

### Inferences
- The strongest cross-system signal is **lossless external memory plus code search plus self-written world-model code**, not bigger context windows. PRO-LONG, Strands, Astra-in-sandbox and Tycho all converge on this. It needs no frontier-only API feature and runs offline.
- The supervisor and stagnation-detection idea (AVO) is cheap to reproduce with rule-based checks: a repeated board hash, no score change for N actions, or the same action loop.

### Gaps
- There is no official Anthropic or Google DeepMind harness blog for ARC-AGI-3 in what I found. Anthropic's numbers are ARC Prize-run.
- No ablation from AVO or Strands isolates which component (the supervisor or the file memory) mattered most.
- I found no published PRO-LONG or Tycho result with open-weight models (the PRO-LONG paper explicitly evaluates only frontier models).

---

## Q4. ARC Prize analyses: what makes ARC-AGI-3 hard, and frontier-agent failure modes

### Takeaway
ARC-AGI-3 gives no instructions or goal. Agents must explore, build a world model, infer the goal and plan. The score is **quadratic action efficiency** against the second-best human, so wasted exploration is penalized. ARC Prize's trace analysis (May 2026) found that **perception is not the main bottleneck**. The dominant failures are (1) seeing local effects but **failing to abstract** them into rules, (2) **anchoring to known games** from training data, and (3) **"success without understanding"**, where early level wins harden wrong theories. Looping and failure to commit also appear, as model-specific "wrong compression" versus "failure to compress".

### Cited Findings
- Structure: 135 environments (25 public demo, 55 semi-private, 55 fully private). A 64×64 grid of 16 colors, at least 6 levels per environment. Five key actions plus Undo, plus coordinate selection. "The agent is never told the objective nor provided instructions." — [ARC-AGI-3 technical report](https://arxiv.org/html/2603.24621v1)
- Scoring (RHAE): per-level `S = min(1, h/a)^2`, where h is "the second-best human action count". Later levels are weighted more heavily. Agents are cut off at 5x human actions per level. — [ARC-AGI-3 technical report](https://arxiv.org/html/2603.24621v1)
- The four capabilities tested are Exploration, Modeling, Goal-Setting, and Planning and Execution. Core-knowledge priors only (objectness, geometry/topology, basic physics, agentness). No numbers, letters or cultural conventions. The human median is 7.4 minutes per environment. — [ARC-AGI-3 technical report](https://arxiv.org/html/2603.24621v1)
- Failure mode 1, **local observation without abstraction:** for example Opus noticed "ACTION3 rotates the container" but never turned it into "orient first, then apply effect". The analysis suggests "perception itself wasn't the bottleneck". — [ARC Prize GPT-5.5/Opus 4.7 analysis, May 1 2026](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis)
- Failure mode 2, **training-data misdirection:** models map mechanics onto Tetris, Frogger, Sokoban or Breakout. A "local visual resemblance becomes a full gameplay theory". — [ARC Prize analysis](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis)
- Failure mode 3, **success without understanding:** Opus cleared level 1 of `ka59` with a wrong theory about clicking, and the misconception "hardened" in level 2. Early progress is "a noisy signal of comprehension". Continual learning across levels failed when misconceptions were not explicitly re-examined. — [ARC Prize analysis](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis)
- Model styles: Opus 4.7 had stronger short-horizon discovery but committed to false invariants ("wrong compression"). GPT-5.5 generated broader hypotheses but struggled to commit and follow through ("failure to compress"). The analysis covered 160 replays and traces. — [ARC Prize analysis](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis); [Epium summary](https://epium.com/news/arc-agi-3-analysis-finds-three-reasoning-failure-patterns-in-frontier-models/)
- The Milestone #1 blog notes that local game checks "weren't a reliable leaderboard proxy". The hidden hold-out set rewards "on-the-fly learning". — [ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1)

### Inferences
- Harness countermeasures that follow from these failure modes:
  - an explicit **hypothesis ledger** with evidence for and against each hypothesis;
  - a forced **re-validation step at each level transition** (replay the log against the current rules, as in `regress.py`);
  - a prompt rule against naming known games;
  - **commit-then-test** planning, to counter GPT-style non-commitment.
- Because the score is quadratic in action ratio, a harness that plans offline inside a learned model (BFS over the agent's own `step()` code) before spending real actions directly raises the score. This explains why Schema, Tycho and Astra beat humans on action count.
- Perception mattered less than abstraction for frontier models, but small open models are likely weaker at reading a 64×64 grid. That is presumably why the Kaggle winners added images, segmentation and labeled renders (Q6).

### Gaps
- I found no ARC Prize quantification of how often each failure mode occurs (percentages).
- I found no newer ARC Prize failure analysis of Opus 5 or Astra traces beyond the behavior notes above.

---

## Q5. ARC Prize 2025 (ARC-AGI-2) winning approaches and what carries over to ARC-AGI-3

### Takeaway
The ARC Prize 2025 winners on Kaggle relied on **test-time training (TTT) plus synthetic data**: NVARC 24.03%, the ARChitects 16.53% with a 2D masked-diffusion LM, and MindsAI 12.64%. The paper winners were tiny recursive or MDL models (TRM, CompressARC) and SOAR self-improving program synthesis. ARC Prize framed 2025 as the year of the **"refinement loop"**: iterative per-task program or model optimization driven by a feedback signal. The *refinement-loop* idea transfers directly to ARC-AGI-3, as world-model code checked against the logged transitions. The *specific* ARC-AGI-2 recipes (grid-to-grid TTT, augmentation ensembles) have no documented use among the top ARC-AGI-3 Kaggle entries so far.

### Cited Findings
- ARC Prize 2025 Kaggle: 1,455 teams and 15,154 entries. Top score 24% on the ARC-AGI-2 private set. — [ARC Prize 2025 technical report, arXiv 2601.10904](https://arxiv.org/abs/2601.10904)
- 1st **NVARC (24.03%)** "builds upon the 2024 ARChitects winning entry (which leverages test-time training) and makes heavy use of synthetic data generation", at about $0.20/task. 2nd **the ARChitects (16.53%)**: "a 2D-aware, masked-diffusion language model with recursive self-refinement and perspective-based scoring". 3rd **MindsAI (12.64%)**: a "heavily-engineered test-time-training pipeline" with augmentation ensembles and tokenizer dropout. 4th Lonnie 6.67%, 5th G. Barbadillo 6.53%. — [arXiv 2601.10904 HTML](https://arxiv.org/html/2601.10904v1)
- Paper awards: 1st TRM (7M params; 45% ARC-AGI-1, 8% ARC-AGI-2; up to 16 improvement steps). 2nd SOAR (self-improving program synthesis, up to +52% on ARC-AGI-1 without a DSL). 3rd CompressARC (76K params, MDL, 20% ARC-AGI-1, about 20 min per puzzle on an RTX 4070). — [arXiv 2601.10904 HTML](https://arxiv.org/html/2601.10904v1)
- Refinement loop definition: "a refinement loop iteratively transforms one program into another, where the objective is to incrementally optimize a program towards a goal based on a feedback signal." Also: "you can add refinement loops at the application layer to meaningfully improve task reliability instead of relying solely on provider reasoning systems". For example, Poetiq's Gemini 3 Pro loop went from 31% at $0.81/task to 54% at $31/task on ARC-AGI-2. — [ARC Prize 2025 results blog](https://arcprize.org/blog/arc-prize-2025-results-analysis)
- ARC Prize flagged "knowledge overfitting": a model used "correct! ARC color mappings in its reasoning", suggesting ARC data is well represented in training corpora. — [ARC Prize 2025 results blog](https://arcprize.org/blog/arc-prize-2025-results-analysis)
- ARC-AGI-3 was announced as requiring "Exploration, Planning, Memory, Goal Acquisition, Alignment". — [ARC Prize 2025 results blog](https://arcprize.org/blog/arc-prize-2025-results-analysis)
- Tufa Labs, 3rd in ARC Prize 2025, is the ARC-AGI-3 Milestone #1 winner. — [Medium aggregator](https://medium.com/@ccro8990/the-official-live-leaderboard-for-the-arc-agi-3-machine-learning-competition-hosted-on-kaggle-part-06dbe491c8dc); [ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1). Note that the arXiv report fetch lists MindsAI 3rd on Kaggle. "3rd" for Tufa may refer to a different ranking, so this is unresolved.

### Inferences
- **What carries over:**
  - The refinement loop: propose a game model or plan, then verify it against the log. Tycho's repair loop and PRO-LONG's `regress.py` are ARC-AGI-3 versions of it.
  - Program synthesis, now "write Python that simulates the game".
  - Cheap verification over expensive generation.
- **What probably does not carry over directly:** grid-in/grid-out TTT with dihedral augmentations. ARC-AGI-3 has no input/output demonstration pairs, and the "training data" per game is the agent's own trajectory. A possible bridge is TTT or LoRA-on-the-fly of a small transition model on the logged (state, action, next_state) tuples, following the "Twin: test-time digital twin" idea ([arXiv 2608.14490](https://arxiv.org/pdf/2608.14490), not read in detail). This is speculative and has no documented Kaggle ARC-AGI-3 result.
- The TRM/CompressARC line (tiny networks trained per task) is the only 2025 line that is naturally "offline and small". I found no evidence it has been applied to ARC-AGI-3.

### Gaps
- The ARC Prize 2025 report's own explicit statements on what transfers to ARC-AGI-3 were not in what I retrieved. The WebFetch summarizer claimed the report says "refinement loops at test time appear most transferable", but I could not verify that wording, so treat it as unverified.
- NVARC's and the ARChitects' ARC-AGI-3 activity in 2026 was not found.

---

## Q6. Kaggle-eligible harness evidence: what the top offline ARC-AGI-3 entries do

### Takeaway
All three Milestone #1 winners run **~27 to 31B open models locally** (Qwen 3.6 27B FP8, Gemma-4-31B). The winner (Tufa Labs' Duck) is a **minimal REPL coding agent with oldest-message eviction and multimodal perception**. ARC Prize's key observation is that **"hand-crafted tools actually hurt the model; letting it improvise worked better."** The runners-up use a **vision-LLM-as-policy** design with periodic reflection memory, legal-action constraints and loop detection.

### Cited Findings
- **Duck (1st):** a code-writing agent in a Python REPL. The game state is exposed as Python variables, and the loop is: reason, call helpers, run code, act, observe. Perception combines a rendered image, the raw ASCII grid, and a segmentation/zoom tool. Context management is **"infinite play via eviction"**: pop the oldest messages and keep the system prompt plus recent history. The philosophy is "keep the harness lightweight and generic and let the model drive", with gains expected from multimodality and better base models rather than hand-built tools. — [ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1); [Tufa Labs](https://tufalabs.ai/research/duck-harness/)
- The Duck is built on TAAF (Tufa ARC-AGI Framework) and supports local vLLM or OpenRouter. Code: [GitHub Tufalabs/duck-harness](https://github.com/Tufalabs/duck-harness). Tufa says future work targets "context management and perception". — [Tufa Labs](https://tufalabs.ai/research/duck-harness/)
- **Reki (2nd) and forge (3rd):** render frames as labeled images and output a JSON action. "Reflection memory refreshed approximately every 10 steps", legal-action constraints, and JSON self-repair. Reki adds a numpy click heuristic with "Dead-signature" detection. forge adds a multi-candidate action generator with arbiter scoring. — [ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- ARC Prize highlights that "hand-crafted tools actually hurt the model; letting it improvise worked better", that multimodality and better base models drove improvements, and that frameworks designed for ablation help. — [ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1)

### Inferences
- None of the three Kaggle winners (as described) uses **lossless on-disk logs with code search** (PRO-LONG), **retained reasoning**, or **summarizing compaction**, although these are the harness features with the biggest measured frontier gains. The Duck's eviction is essentially the "rolling truncation" OpenAI blamed for Sol's 13.3%. This is the clearest open opportunity for an offline ~30B entry.
- "Hand-crafted tools hurt" (Kaggle, small model) contrasts with Schema's 12 custom tools plus BFS (frontier). The consistent reading: give *generic* primitives (Python, grep, the log, a `step`-replay helper) and let the model write game-specific tools itself, as Astra and Strands did. Do not hard-code game-specific heuristics.

### Gaps
- There are no published ablations from the Duck, Reki or forge (for example eviction versus summarization, or image versus text-only).
- The Duck's context length, eviction window and thinking-retention settings were not visible in the pages I could fetch. The Kaggle discussion 717133 returned only its title.

---

## Q7. Statements from Chollet, Knoop and ARC Prize (interviews, podcasts, X) on how to win and what winning solutions should look like

### Takeaway
I found **no MLST or Latent Space episode in 2026** specifically on winning ARC-AGI-3. Public statements come mainly from X and ARC Prize blogs. Chollet expects 2026 to be a year of harness innovation, acknowledges a "parity issue" around compaction, and, with Knoop, insists that saturating ARC-AGI-3 is **not proof of AGI**. ARC Prize's stated ideal is that "future AGI systems will not need task-specific external handholding".

### Cited Findings
- Chollet on Astra: "a step-function change in model capability for interactive reasoning problems. It scores 66% on ARC-AGI-3 using our standard harness, and nearly 100% with a continuous conversation harness and custom compaction, at a cost of roughly $360 per game." — [François Chollet on X](https://x.com/fchollet/status/2095598451115614371)
- Chollet (search-snippet paraphrase) on "a lot of back and forth with OpenAI about how to best test their models, especially with regard to compaction", conceding "a potential parity issue". — [Context Studios blog](https://www.contextstudios.ai/blog/arc-agi-3-measured-the-harness-not-just-the-model); [Chollet on X](https://x.com/fchollet/status/2095598451115614371). Not verified against the original text.
- Chollet: "if it saturates ARC 3, is it AGI? We're not making this claim… solving it is not p[roof of AGI]". — [Chollet on X](https://x.com/fchollet/status/2095599835932135919)
- Knoop: "GPT-6 Astra is the new SOTA on ARC-AGI-3… the pace of progress is frankly surprising. That said, we lack evidence to call this AGI yet." — [Mike Knoop on X](https://x.com/mikeknoop/status/2095600676919455857)
- ARC Prize expected 2026 to bring "significant progress on harness innovation" and added a secondary community leaderboard for harness-driven results. — search snippet referencing [ARC-AGI-3 technical report](https://arxiv.org/pdf/2603.24621)
- The ARC-AGI-3 report states that "future AGI systems will not need task-specific external handholding". — [ARC-AGI-3 technical report](https://arxiv.org/html/2603.24621v1)
- Stanford researchers (Reuel, Hardy) called rerunning evaluations under different conditions "benchmaxxing". OpenAI's Astra launch had a pre-publication draft of 98.6% and a live figure of 99.99%. — [TheNextWeb, Sep 6 2026](https://thenextweb.com/news/openai-astra-arc-agi-3-harness-62-7-vs-99-9-benchmark-revisions)
- Chollet and Sam Altman held a fireside chat at the ARC-AGI-3 launch (Mar 25, 2026, YC HQ). — [ARC-AGI-3 launch](https://arcprize.org/blog/arc-agi-3-launch)

### Inferences
- The Kaggle hold-out is private and has fresh games, and ARC Prize repeatedly praises "on-the-fly learning". Winning solutions should therefore be generic learning-in-the-loop agents, not game-specific solvers. That matches the Duck philosophy and PRO-LONG's "domain-neutral" design.

### Gaps
- No 2026 MLST or Latent Space transcript on ARC-AGI-3 strategy was found, and no Tufa Labs interview was found. The Knoop podcasts found (No Priors, Sequoia Training Data) are from 2024 and predate ARC-AGI-3.
- Chollet's "66%" conflicts with ARC Prize's 62.7% Standard figure. The cause (a different run or rounding) is unknown.

---

## Q8. Synthesis: which harness lessons can be reproduced with a local ~30B model on Kaggle

### Takeaway
Almost every frontier harness *mechanism* is reproducible offline, because none of them requires a proprietary API. **Retained reasoning, compaction, lossless logs with code search, a Python sandbox, self-written world-model code with replay verification, and stagnation supervision** are all local harness code. What does not transfer is the **raw capability and token budget**: frontier runs spend about $33 to $475 per game on tokens, and 30B models are far weaker at abstraction. So priorities should be token-efficient mechanisms (PRO-LONG-style logs, compact state notation), not long-context ones.

### Cited Findings (evidence base for each lesson)
- **Retained reasoning:** 13.3% → 38.3% with ~6x fewer output tokens (together with compaction). — [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/). Anthropic's adapter "preserves native thinking blocks between actions". — [arc-agi-3-benchmarking](https://github.com/arcprize/arc-agi-3-benchmarking)
- **Compaction vs truncation:** rolling truncation at 175K characters was the failure. Compaction "summarizes older context instead of dropping it". — [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/). ARC Prize's adapter falls back to "a domain-neutral harness summary" when there is no native compaction. — [arc-agi-3-benchmarking](https://github.com/arcprize/arc-agi-3-benchmarking)
- **Lossless log plus code search beats self-written notes:** no-log 19.9% vs 24.0%, workspace-clear only −0.5 pp, Python +10.8 pp, 4.2 to 5.8x fewer tokens. — [PRO-LONG](https://arxiv.org/html/2607.20064v2)
- **Code execution and self-built tools:** Astra built parsers and solvers in a sandbox ([ARC Prize Astra](https://arcprize.org/blog/astra)). Strands generated 734 scripts ([Strands](https://strandsagents.com/blog/our-production-sdk-hit-99-95-on-arc-agi-3/)). The Duck is REPL-based ([Tufa Labs](https://tufalabs.ai/research/duck-harness/)).
- **Executable world model plus planning:** Schema `step(grid, action)` plus BFS; `regress.py` replay verification ([PRO-LONG](https://arxiv.org/html/2607.20064v2)); Tycho Moore-machine models with repair ([Tycho](https://arxiv.org/abs/2607.28287)).
- **Compact state notation:** Astra and Opus 5 invented algebraic notations. — [ARC Prize Astra](https://arcprize.org/blog/astra); [The Decoder](https://the-decoder.com/anthropics-opus-5-blows-past-fable-5-and-gpt-5-6-sol-on-the-benchmark-designed-to-measure-real-intelligence/)
- **Supervisor / loop detection:** AVO supervisor for "stagnation or repeated unproductive cycles" ([NVIDIA](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/)); Reki's "Dead-signature" detection ([ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1)).
- **Perception for small models:** image plus ASCII plus segmentation (Duck) and labeled images (Reki/forge) ([ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1)). Frontier AVO used text-only 64×64 grids ([NVIDIA](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/)).
- **Generic over hand-crafted tools for small models:** "hand-crafted tools actually hurt the model; letting it improvise worked better". — [ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- **Variance:** PRO-LONG GPT-5.5 went from 41.2% pass@1 to 60.1% best@5 ([PRO-LONG](https://arxiv.org/html/2607.20064v2)). The Duck's standard deviation is ±0.45 on a mean of 1.60 over 20 tries ([Tufa Labs](https://tufalabs.ai/research/duck-harness/)).

### Inferences (transferability matrix for a ~30B local model; all are my own judgments)

| Lesson | Frontier evidence | Reproducible on Kaggle ~30B? | Notes and adaptation |
|---|---|---|---|
| Retained reasoning | +25 pp (with compaction) for GPT-5.6 Sol | **Yes (harness-only)** | Do not strip earlier `<think>` blocks, or keep a condensed version. Keep only the last K turns of full reasoning to fit context. Check the chat template behavior, since it may drop prior reasoning by default. |
| Compaction (summarize, don't truncate) | Core of OpenAI/ARC Prize adapter | **Yes, but costs local tokens/time** | The same model writes a structured summary (rules believed, evidence, open questions, level progress) when context exceeds a threshold. This beats the Duck's pure eviction in principle, but it is untested on Kaggle. |
| Lossless append-only log plus Python/grep search (PRO-LONG) | +18 pp average; 4 to 6x fewer tokens; the log beats notes | **Yes, the most promising** | Stdlib Python only, so it works offline. Small context need. Makes eviction safe, because nothing is lost. |
| Python sandbox / REPL | Python alone about +10.8 pp | **Yes (already used by the Duck)** | Keep primitives generic. |
| Self-written world model plus BFS/replay verification | Schema, Tycho, `regress.py`; beats humans on action count | **Partially** | 30B models write weaker simulators. Prefer small incremental rules checked against logged transitions. BFS on a verified model saves real actions, and actions count quadratically in RHAE. |
| Compact state notation | Emergent in Astra and Opus 5 | **Yes** | Give it as a prompt convention or a helper (object list with positions, diff between frames) to save tokens. |
| Supervisor / stagnation detection | AVO; Reki dead-signature | **Yes, cheaply with rules** | Board-hash repeats, no score change for N steps, forced hypothesis reset. |
| Level-transition re-validation (anti "success without understanding") | ARC Prize failure analysis | **Yes** | At each new level, force a replay check of the current theory before acting. |
| Multimodal perception (image plus grid plus segmentation) | Kaggle winners | **Yes (if the VLM fits)** | Frontier models did fine with text only; small models seem to benefit from images and segmentation. |
| Multi-agent orchestration (Arcgentica, AVO supervisor LLM) | Frontier | **Limited** | GPU time budget. A second LLM call per N steps is feasible, but full multi-agent runs likely are not. |
| Massive sampling / best@k | PRO-LONG best@k gains | **No for scoring** | Kaggle scores one run per game. Test-time diversity is useful only within a game (for example parallel hypotheses in the sandbox). |
| Spending $300 to $500/game of frontier tokens | Astra | **No** | Budget per game is bounded by the Kaggle GPU hours. |
| ARC-AGI-2-style TTT | NVARC/ARChitects | **Unproven** | Possible as on-the-fly fitting of a transition model; no evidence yet. |

- Suggested priority for an offline entry, inferred from the evidence above:
  1. Duck-style REPL agent (a proven Kaggle baseline).
  2. Add a PRO-LONG lossless log with grep/Python search, so eviction no longer loses information.
  3. Add retained reasoning for the last few turns plus a structured compaction summary.
  4. Add a supervisor/loop detector and a level-transition re-validation.
  5. Add a self-written `step()` model with a replay check and BFS only when the check passes.

### Gaps
- There is no public ablation of retained reasoning or compaction on *open-weight* models for ARC-AGI-3. Whether ~30B models get the same 3x effect is unknown.
- No PRO-LONG, Tycho or Strands-style harness has been reported with Qwen/Gemma-class models.
- The Kaggle per-game time budget and GPU memory (and therefore the usable context length for a 27 to 31B FP8 model) were not confirmed.
