# Top Kaggle ARC-AGI-3 Teams: Methods, Scores, Lessons (as of 2026-10-02)

Scope: public sources only. Dates are 2026 unless stated. "LB" = Kaggle public leaderboard. The hardware for every number below is the Kaggle box: one RTX PRO 6000 (96 GB), 9 h runtime, 110 games, so it matches the target setup (single offline RTX Pro 6000).

## Q1. Tufa Labs (#1, ~52.5 public LB, 153 submissions): what have they published?

### Takeaway
Tufa Labs has only published its **Milestone 1** solution (Duck harness, Qwen 3.6 27B FP8, 1.21% LB, dated July 1). It has published nothing that explains the jump to ~52.5. Their public lessons cover four things: the REPL-as-interface design, context eviction, the perception limits of small models, and goal-inference failures (energy bar, invented goals, being stuck on a wrong hypothesis). The "36%" figure is **not** a Tufa score. It is Symbolica's frontier-model ARCgentica result, which Tufa cites as prior art.

### Cited Findings
**Current standing**
- Kaggle leaderboard (search snippet, early Oct): Tufa Labs is #1 with **52.51**, **153 entries**, and Yi-Chia Chen is #2 with **48.07** — [Kaggle leaderboard via search](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard). I could not load the page directly because it is JS-rendered and the API returned 401/403. Treat these numbers as search-snippet-level evidence.
- Trajectory: in a cached snapshot of the public LB (pulled about Sep 25), Lord Han Solo was #1 at 19.45, Tufa Labs #2 at 18.81, Yi-Chia Chen #3 at 18.63, Daniel Franzen #4 at 16.68, NVARC3 #5 at 16.07, Tong Hui Kang #6 at 15.02, "the last dance" #7 at 13.70, and Matija Ludvig & Zhongwei Wang #8 at 11.64, out of 3,320 teams. Source: Kaggle LeaderboardService JSON cached in the scratchpad. Tufa therefore went from about 19 to about 52.5 in roughly one week, around and after the Sep 30 milestone.
- Franzen briefly held 1st place "on September 6th, 2026, but I was quickly overtaken by Tufa Labs" — [Franzen WRITEUP](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)

**The Milestone 1 solution (the "Duck")**
- Milestone 1 (deadline June 30; blog July 6) went to: 1st Tufa Labs "The Duck", 2nd Reki (Gemma-4-31B, vision-LLM-as-policy with JSON actions and reflection memory), 3rd Md Boktiar Mahbub Murad "forge" (Gemma-4-31B) — [ARC Prize Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- The Kaggle write-up is discussion 717133, posted 2026-07-01. Authors: Harold Bessis, Jeroen Cottaar, Isaiah Pressman, Dries Smit, Michal Tešnar, Stefano Viel. Key points from it:
  - The Duck is the successor to Stochastic Goose, which won the ARC-AGI-3 preview.
  - Base model is Qwen 3.6 27B FP8 served on vLLM.
  - The best LB score was **1.21%**. An initial 1.30% was retracted. The same submission scored as low as **0.77%**, and public-game std was up to 0.4.
  - Mean on 25 public games × 20 tries was **1.6002 ± 0.4475**.
  - Source: [Kaggle discussion 717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133); [tufalabs.ai blog](https://tufalabs.ai/research/duck-harness)
- Architecture, from discussion 717133:
  - Game state is exposed as Python REPL variables: `current_frame` with `.ascii` and `.segmentation`, `previous_frame`, `history`, `transitions`, `last_action_result`, `valid_actions`.
  - Tool calls have a 30 s limit and 4,096-char output. The REPL is reset between calls.
  - Actions have natural names (UP/DOWN/LEFT/RIGHT/SPACE/MOUSE/RESET).
  - **UNDO was deliberately NOT exposed**: "the model fails to use it efficiently: it undoes big batches of actions that wastes energy."
  - Source: [Kaggle discussion 717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)
- Context management (M1):
  - Max context is 64k. The harness tries to keep about 32k input by evicting the oldest user message and the assistant turns that follow it.
  - The system prompt is always kept.
  - "We currently do not optimally use prefix caching on the vLLM engine." Later Milestone 2 teams exploited exactly this weakness.
  - A "World model:" note is carried across turns.
  - Source: [717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)
- Perception (M1):
  - A 4× upscaled board image is injected every turn. This matches Qwen's 16×16 patches, and 4× gave "the best visual understanding".
  - "We also tried injecting more frames or video animations, but … small models struggle", so the model did not see animations. The write-up names `sb26` and `tn36` as games where animations matter.
  - A 4-connected-component segmentation tool is provided because models "dump full boards into the context that dilutes their attention."
  - Source: [717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)
- Lessons stated by Tufa (M1):
  - "The main driver of improvement … came from better base models and introducing multi-modality."
  - "hand-crafting specific tools for the model did not help, as it seems to hinder the creative abilities of the model."
  - Prompts had to stop the model from "treating the energy bar as the objective or inventing nonsensical goals like moving a block to a fixed position". They also had to stop it from hallucinating classic sprites or Atari-style play.
  - Suggested next steps: compaction/memory for context, and better perception.
  - Source: [717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)

**"Wrong-goal loops"**
- Tufa (MLST/Rescript material): agents that adopt an incorrect hypothesis and then switch to another incorrect one are "very hard to get … out of the loop". Agents often think "reducing the energy bar to the minimum is the goal or that stepping 10 times in a region is the goal". LLMs show "a recurring failure mode of locking onto wrong hypotheses and failing to shift abstraction levels" — [Rescript MLST transcript, Tufa Labs](https://app.rescript.info/share/463d7f031349b4b9db428553eed88230?t=2795) (quoted via search snippet; the full page did not render); [daily.dev summary](https://daily.dev/posts/the-benchmark-with-no-instructions-tufa-labs-arc-agi-3--nagrqjc2f)

**The "36% number"**
- Symbolica's ARCgentica (built for frontier models; recursive self-calling sub-agents in the style of Recursive Language Models / CodeAct) "achieved a score of 36% the day after the release of the public official games" — [717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133); the blog also gives "36.08% within the first day" — [tufalabs.ai](https://tufalabs.ai/research/duck-harness)
- The MLST episode summary says "The 36% leaderboard score reflects action efficiency penalties, not raw solve rate", and that "Frontier models can solve 50–66% of training games but inefficiently" — [daily.dev summary of the MLST episode](https://daily.dev/posts/the-benchmark-with-no-instructions-tufa-labs-arc-agi-3--nagrqjc2f). This is a secondary summary and its exact framing is unverified.
- The blog also cites Executable World Models at **58.12%** with frontier APIs, and says the Duck is "an order of magnitude cheaper" per game. It compares against GPT 5.4 inside the Duck harness — [tufalabs.ai](https://tufalabs.ai/research/duck-harness)

**Other channels**
- MLST episodes:
  - The Duck showcase is linked via [MLST on X](https://x.com/MLStreetTalk/status/2072326433922297975).
  - A progress discussion is at [YouTube Vg6FBKTlfOw](https://www.youtube.com/watch?v=Vg6FBKTlfOw).
  - Tim Scarfe recorded with the team in Zurich ([search summary](https://tufalabs.ai/research/duck-harness/)).
- The Tufa X announcement says: "built on Qwen 3.6 27B … We hit 1.21%" — [X @tufalabs](https://x.com/tufalabs/status/2072336849465417747)
- GitHub [Tufalabs/duck-harness](https://github.com/Tufalabs/duck-harness) contains:
  - the TAAF framework, solver, prompts, an example run (25 games × 20 passes), a viewer, and the Kaggle notebook;
  - local vLLM or OpenRouter backends;
  - about 90 stars and 24 forks.
- In August a commenter asked Tufa to add a LICENSE, because the rules require an explicit OSS license on third-party components — [717133 comments](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)

### Inferences
- Tufa's M1 statement that "model upgrades drive most gains" agrees with every M2 winner. The fastest single lever is probably the Qwen3.8-Flash-Next stack, not new prompts.
- Tufa's M1 choices were reversed by the M2 winners, who gained from each reversal:
  - no UNDO
  - no animations
  - 4× images
  - short 32k context
  - poor prefix caching
- Tufa's current ~52.5 almost certainly includes undisclosed changes beyond what anyone has published. No public source explains it.

### Gaps
- No public Tufa write-up, notebook, or post found that describes their Aug–Oct method (models, scheduling, context) behind 52.5. X pages returned HTTP 402, so I could not read recent X posts.
- I could not retrieve full MLST transcript text. The "wrong-goal loop" quotes come from search snippets and the daily.dev summary.
- The 153-entry count and the 52.51 score are from a leaderboard search snippet. I could not confirm them directly or attach a date to them.

## Q2. Yi-Chia Chen (#2, ~48): any public write-up?

### Takeaway
No public write-up, notebook, or post was found. The only public trace is a single ARC Prize X post announcing a 28.34% new 1st place, plus the leaderboard rows.

### Cited Findings
- ARC Prize posted "New ARC Prize 2026 - ARC-AGI-3 High Score 28.34% by Yi-Chia Chen (new 1st place)". The post is undated in the snippet, and its body returned 402 — [X @arcprize](https://x.com/arcprize/status/2104590501915787290)
- Kaggle LB snippet shows Yi-Chia Chen at #2 with 48.07 — [Kaggle leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard)
- In the cached ~Sep 25 public LB snapshot, Yi-Chia Chen was #3 at 18.63 (Kaggle LeaderboardService JSON).
- A Yi-Chia Chen is a researcher listed at [NVIDIA Research (Taiwan)](https://research.nvidia.com/labs/twn/author/yi-chia-chen/), and a different profile appears as a UCLA-affiliated cognitive modeling scientist. **Identity is unconfirmed**; there is no evidence linking either profile to the Kaggle team.

### Inferences
- The scores went from about 18.6 (around Sep 25) to 28.34 (new 1st, before Tufa's jump) to about 48. That path suggests a major unpublished change in late September or early October, similar in size to Tufa's jump.
- Yi-Chia Chen did not open-source for M2 (not among the M2 winners), so the method is likely to stay private until the final.

### Gaps
- No method details, model, or GitHub link found. [GitHub Yi-Chia-Chen](https://github.com/Yi-Chia-Chen) exists, but I found no ARC repo in the search results.

## Q3. Milestone #2 open-sourced winners: measured gains, what did not work, variance

### Takeaway
All three winners share one recipe:
- the Tufa Duck harness;
- Qwen3.8-Flash-Next (4-bit experts, PLE table offloaded to host RAM);
- an FP8 KV cache;
- an MTP speculative decoding head;
- long rolling history trimmed in big blocks so the prefix cache stays hot;
- UNDO and animations exposed.

The only clean single-change ablation published is Lohit's FP8 KV plus longer history: **14.49 → 22.53** with no prompt changes. Every winner reports very large run-to-run variance.

### Cited Findings
**Official result**
- Milestone #2 (Sep 30): 1st Daniel Franzen 27.9% ($25K), 2nd Lord Han Solo 23.8% ($7.5K), 3rd Lohit Siriki 22.5% ($5K) — [ARC Prize search summary / arcprize.org](https://arcprize.org/competitions/2026/arc-agi-3)
- The competition page lists M2 prizes as $25K/$10K/$2.5K — [arcprize.org](https://arcprize.org/competitions/2026/arc-agi-3). This conflicts with the $7.5K/$5K reported in the search summary.
- Tong Hui Kang's summary calls these winners "tentative, to be confirmed by the organizers" — [SUMMARY.md](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md)

**Daniel Franzen (27.89)** — [WRITEUP.md](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- Model path: Qwen3.6-27B → Qwen3.8-27B → Qwen3.8-Flash-Next. "Each switch brought a substantial improvement."
  - Weights moved from RadixArk NVFP4 to **Intel W4A16 AutoRound**, which gave "similar quality and throughput, while leaving more VRAM for KV".
  - BF16 PLE table offloaded to host RAM.
  - Albucino INT4 MTP draft with 3 speculative steps.
- Serving: Pennyroyal (John Pezzulli's SGLang fork for RTX PRO 6000) v2.5.3 with patches:
  - low-M BF16 GEMM;
  - spec-state memory budget fix;
  - Marlin scale-dtype fix;
  - a Mamba prefix-cache checkpoint patch (keep only the final prefill checkpoint, refresh its LRU position);
  - shard-prefetch with resharding.
- Configuration:
  - 10 streams;
  - 128 Ki harness context, 12 Ki output, 136 Ki server limit;
  - drain to about 58 Ki;
  - FP8 E4M3 KV, 60 Mamba slots, mem fraction 0.96, chunked prefill 8,192;
  - temperature 0.7, top-p 0.95, top-k 20.
- Cache efficiency (earlier demo run):
  - **93.43%** of prompt tokens reused from cache;
  - P90 prefill 10,552.6 tok/s, P90 decode 836.6 tok/s, harness throughput 609 tok/s;
  - prefill took 15.25% of wall time;
  - long-prompt miss rate 0.03% (1/3,248).
- Caching tactics:
  - Admission is limited to 10 streams so that returning games find their prefix still cached.
  - Trimming uses hysteresis: drop a big block at once.
- Retaining the model's thinking in history is deliberate. "Removing it leads to a large regression in score."
- Gains he reports, qualitative only, no per-change numbers:
  - **Animations**: "of all perception changes … the strongest benefit". Intermediate frames are exposed as REPL variables, along with a timeline, and the model gets a hint only when there are "transient pixels". Inspired by Jakob Brüggen's TAAF-anim notebook.
  - **Image upscale 10×** (instead of 4×) gave the "biggest score improvement in terms of images".
  - Other perception changes: `frame_diff()` object-level diffs, difference images, and showing the fatal frame after game over.
  - **UNDO** exposed as `UNDO` (ACTION7). It helped clearly on `su15`. "On the competition set, the combination of undo, action information, level-transfer guidance, and persistent functions produced a large improvement." UNDO was not isolated.
  - Other prompt changes: detailed game-over diagnosis prompts ("do NOT re-submit this same series of moves"), and a "BAR RULE" for interpreting the budget bar.
  - Persisting model-defined Python functions across the whole game.
  - No-op, stale-state, and terminal-state action guards, using an interior-board change test that excludes a 4-cell border.
  - Priority scheduler:
    - A = immediate gain from finishing the current level, normalized by $55/(N(N+1)/2)$;
    - B = heuristic continuation value by remaining levels;
    - C = penalty for actions and tokens spent without completion;
    - the future value is faded near the end of the run;
    - games are re-queued only at context-eviction points so caching survives;
    - calibrated on 725 attempts (557 completed).
- What did NOT clearly help:
  - **structured world-model updates** (disabling the mechanism entirely was best once context was large);
  - **summarization**, whether inserted or replacing history;
  - shorter or different **resume prompts**. Yielding is now triggered at 2,048 generated tokens instead of a time limit;
  - **composite animation images** and auto-inserted timelines (these hurt some games);
  - more prescriptive **verification hints**, plus repeated-state, no-op, and death-ledger guards;
  - **more elaborate priority rules** (pace adjustment, empirical continuation lookup).
- Compute: mostly Kaggle quota plus about **150 rented RTX PRO 6000 GPU-hours** in the final phase. No training. He could not run the final config on the full demo set before the deadline.

**Lohit Siriki / rellik13 / sirikilohit (22.53)** — [WRITEUP.md](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md); [README](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution)
- Solo entry, 44 submissions. Measured score history (public LB):

| Date | Score | Change |
|---|---|---|
| Aug 11 | 0.99 | Duck harness |
| Sep 2 | 3.81 | Qwen3.8-Flash-Next |
| Sep 18 | 6.42 | SGLang Pennyroyal, more games at once |
| Sep 25 | 7.14 | Bigger context (49k, trimmed in large chunks) |
| Sep 26 | 9.96 | Solved-level memory (**+2.8**) |
| Sep 27 | 13.40 | Wang's harness design (stricter sandbox, object segmentation, code-testing prompts) |
| Sep 29 | 14.49 | Harness fixes: rename ACTION7 → `UNDO`; "game over" → "Level restarted"; delete the prompt line telling the agent to ignore the budget bar; expose animation frames; 40-min scheduler slices |
| Sep 30 | **22.53** | FP8 KV, longer history; prompts, model, and sampling unchanged |

- The final change, in detail:
  - KV moved from BF16 to FP8, giving a pool of about 1.0M tokens (1,004,288).
  - The trim window moved from 36,864→26,624 to **57,344→45,056**.
  - Context went from 49,152 to 69,632.
  - Games at once went from 15 to 16.
- Rationale: transcripts showed the agent "often had the right goal but lost track of what it had tried". Server logs showed the cache pool was **91–97% full** all run, and requests queued for cache space.
- Solved-level memory pins the rule the agent wrote, plus the last 30 winning actions of each cleared level, into the system prompt. It is "the only text addition that helped".
- **More prompt text hurt**:
  - adding text dropped the score from 6.42 to 4.16;
  - a level-start advice block dropped it from 13.40 to 9.98.
  - His interpretation: instructions displace the agent's own recent turns.
- Did not work (one or two runs each):
  - per-action "what changed" notes and summaries;
  - **restarting a stuck level with fresh context** ("chance of clearing a level didn't fall with time spent on it");
  - temperature 1.0 vs 0.6;
  - an assumption ledger (the agent never used it);
  - **pruning 25% of experts**;
  - higher-resolution board images (this contradicts Franzen's 10× finding);
  - Swift 1.5 fine-tune (no better per token, about 35% slower);
  - LoRA on Qwen3.8-27B on Kaggle TPU (scored badly);
  - an earlier FP8-KV test was confounded by an MXFP8 requant of non-expert layers, which was about 25% slower to decode.
- Held back: a priority scheduler. His reasoning is that games stagnate late, so reallocating time "would mostly move stagnant time". He actually uses a one-pool UCB scheduler: 2,400 s slices over a shared pool of about 31k s, with extra slices going to games with the most levels cleared per token.
- **Variance**:
  - the same notebook submitted three times scored **5.02, 5.50, 6.42**;
  - a notebook scoring 37 on his 25-game practice set got **9.98** on LB, and one scoring 32 got **13.40**;
  - "The first 30 minutes of a run say little about the result."
  - Coping methods: compare runs at an equal number of generated tokens per game, prefer full-length runs, and read transcripts.
- Resources: Kaggle weekly quota, about 12 h of rented RTX PRO 6000, and Claude Code for implementation and log reading.

**Lord Han Solo (23.84)** — Kaggle notebook [lordhansolo/arc-agi-3-milestone-2](https://www.kaggle.com/code/lordhansolo/arc-agi-3-milestone-2?scriptVersionId=353922905); details via [SUMMARY.md](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md)
- No write-up or GitHub published.
- Model: primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8 with a built-in NVFP4 MTP head (3 draft tokens, 32k draft vocab).
- Serving: **vLLM 0.29.1rc1 nightly** with patches:
  - align-state Mamba retention;
  - prompt-tail state caching;
  - BF16 PLE safeguard;
  - pinned-host embed_tokens.
- Capacity: KV pool 1,417,100 tokens (the largest of the three), gpu util 0.98, context 147,072 server / 127,488 harness.
- Context and scheduling:
  - trim at about 126k down to **81,536**, with no turn cap;
  - 14 streams;
  - 3,918 s cap per game;
  - temperature 0.6.
- Prompting and harness:
  - rewritten system prompt;
  - a **strategy-audit prompt** once a level has used 25% of the game's time;
  - saved Python modules persist per game;
  - the tool agent was rewritten (1,745 lines).
- He was #1 at 19.45 in the ~Sep 25 cached LB snapshot.

### Inferences
- Memory for history is the clearest lever that was measured: +8 points from one server flag plus trim settings. All three winners converged on FP8 KV and 45k–128k retained context with block trimming.
- What helps is "restore evidence the agent loses" or "remove misleading harness text". Added advice does not help. This matches the Tufa "wrong-goal" insight that the agent's own trajectory is its best evidence.
- Lohit's variance numbers (±~1 point on identical runs at the ~6 level, and practice-to-LB ratios of 3–4×) mean single-submission deltas under ~3 points are not trustworthy.
- The two disagreements between teams should be tested locally rather than copied:
  - image resolution: Franzen found 10× upscale best, Lohit found higher resolution did not help;
  - scheduling: Franzen uses a priority scheduler, Lohit uses UCB and is skeptical of priority scheduling.

### Gaps
- Franzen gives no numeric per-change deltas. He has promised a full demo-set run "next week".
- Lohit has promised a full 2.5 h public-game run. No result is published yet.
- Lord Han Solo's own rationale and ablations are unpublished.

## Q4. Comparison of the three M2 notebooks (Tong Hui Kang SUMMARY.md)

### Takeaway
All three fit Qwen3.8-Flash-Next into about 72–74 GB of VRAM. Each leaves 16–20 GB for KV plus Mamba state and offloads about 95 GB (the PLE table) to host RAM, and gets about 950–1,160 peak decode tok/s. They differ mainly in context length and concurrency. Franzen's setup is fewer streams with very long context and a priority scheduler. Lohit's is more streams with shorter context and a UCB scheduler.

### Cited Findings
All from [tonghuikang/daniel-franzen-arc-agi-3 kaggle/SUMMARY.md](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md) (last commit Sep 30). There is also a 261-line COMPARISON.md in the same folder.

| | dfranzen | lordhansolo | sirikilohit |
|---|---|---|---|
| Public LB | 27.89 | 23.84 | 22.53 |
| Server | SGLang Pennyroyal v2.5.3 | vLLM 0.29.1rc1 nightly | SGLang Pennyroyal v2.5.0 |
| Weights | Intel W4A16 AutoRound + BF16 PLE; Albucino INT4 MTP draft | primitive-ai mixed NVFP4/FP8 + BF16 PLE, built-in MTP | Intel W4A16 AutoRound + RadixArk FP8 PLE; RadixArk NVFP4 MTP |
| Weights on GPU | 73.64 GB | 71.94 GB | 73.57 GB |
| KV + Mamba on GPU | 15.94 GB | 19.69 GB | 16.97 GB |
| Offloaded to host | 95.37 GB | 96.55 GB | 95.68 GB (47.68 FP8 PLE + 48 GB hierarchical KV/Mamba host tier) |
| KV dtype / pool | fp8_e4m3 / 1,011,264 tok | fp8_e4m3 / 1,417,100 tok | fp8_e4m3 / 1,004,288 tok |
| Context server/harness | 139,264 / 131,072 | 147,072 / 127,488 | 69,632 / 69,632 |
| Trim | at 118k down to ~59k; 150 assistant-msg cap | at ~126k down to 81,536; no cap | at 57k down to 45k, using the server tokenizer |
| Streams | 10 (all 110 live) | 14 (14 live) | 16 (28 live) |
| Startup | 531 s | 544 s | 615 s |
| Peak decode | 946 tok/s | 1,135 tok/s | 1,159 tok/s |
| Temperature | 0.7 | 0.6 | 0.6 |
| Budget per game | priority re-queue at each trim | 3,918 s cap, 8 waves of 14 | 2,400 s slices + UCB over a ~31k s pool |
| Level handover | history + Python functions kept | history + saved modules kept | rule + last 30 winning actions pinned; fresh sandbox |

### Inferences
- The highest scorer had the *lowest* decode throughput (946 tok/s) and the fewest streams. Throughput alone does not predict score. Long context, cache hits, and allocation matter at least as much.
- For a 96 GB card, the template is 4-bit experts, PLE in host RAM, FP8 KV, and an MTP draft with 3 steps. This needs about 96 GB of free host RAM.

### Gaps
- No per-notebook full-run scores on identical game sets exist, so I cannot separate harness effects from serving effects.

## Q5. Other strong public notebooks/discussions (>25) since Oct 1; official M2 announcement; public LB = ~50%

### Takeaway
I found no public notebook or discussion scoring above 25 after Oct 1, other than the M2 winners (Franzen 27.89 is the only one above 25). Kaggle metadata confirms the public LB uses **50%** of the hidden test data, with 1 submission per day and a final deadline of **Nov 2, 2026**. Given the observed variance, a large shake-up is likely.

### Cited Findings
- Kaggle competition metadata (cached API JSON, scratchpad `comp.json`):
  - `"leaderboardPercentage": 50`, `"maxDailySubmissions": 1`, `"deadline": "2026-11-02T23:59:00Z"`;
  - team-merger and new-entrant deadline Oct 26;
  - **kernel-publishing disabled after Oct 26**;
  - `onlyAllowKernelSubmissions: true`, maxTeamSize 8;
  - `witholdFinalLeaderboardUntilItHasBeenVerified: true`.
  - Source: [Kaggle competition](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview)
- Kaggle rules: the Public LB is "against a representative sample of the test data", and winners are "determined solely by … the Private Leaderboard" — [Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)
- arcprize.org states "All code and methods must be open sourced to be eligible for prizes" — [arcprize.org](https://arcprize.org/competitions/2026/arc-agi-3)
- The ARC Prize M2 blog URL (`/blog/arc-prize-2026-milestone-2`) returned 404 on Oct 2. The winners and amounts came only from a search summary and are described as "tentative" on GitHub ([SUMMARY.md](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md)).
- Related public work cited by the winners:
  - Jakob Brüggen's TAAF-anim notebook, the source of the animation idea — [Kaggle](https://www.kaggle.com/code/jakobbrggen/taaf-anim-arc-agi-3-solver)
  - Wang (Zhongwei Wang; team "Matija Ludvig & Zhongwei Wang", 11.64 on ~Sep 25) had a public harness repo with sandbox, segmentation, and prompts, now private — [Lohit WRITEUP](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md)
  - Serving forks: [jpezzulli/sglang-rtxpro6000](https://github.com/jpezzulli/sglang-rtxpro6000), [gabrielolympie/sglang-flashnext-sm120](https://github.com/gabrielolympie/sglang-flashnext-sm120), [mratsim/sglang-qwen38fn-sm120-turbo](https://github.com/mratsim/sglang-qwen38fn-sm120-turbo)

### Inferences
- Shake-up risk is high:
  - the public LB covers only ~55 of 110 games;
  - identical notebooks vary by ±10–20% relative (Lohit 5.02–6.42; Tufa M1 0.77–1.30);
  - practice-set scores map poorly to LB.
- Gaps of a few points between ranks are within noise.
- The 52.5 and 48 leaders are far enough ahead that their lead is probably real.
- Kernel publishing closes Oct 26, so any further open-sourced notebooks will appear before then.

### Gaps
- I could not browse the Kaggle Code and Discussion tabs for posts after Oct 1. The Kaggle internal API returned 403 and the pages are JS-rendered. Strong new public notebooks may exist that I could not see.
- The official ARC Prize M2 announcement text, with exact prize amounts, could not be retrieved. The 2nd/3rd prize amounts conflict between sources ($10K/$2.5K on the competition page vs $7.5K/$5K in the search summary).
