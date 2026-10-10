# ARC Prize 2026 – ARC-AGI-3 Kaggle competition: what top competitors actually do (current as of 2026-09-25)

Scope note: this covers the 2026 Kaggle competition (opened 2026-03-25; Milestone #1 2026-06-30; Milestone #2 2026-09-30; final deadline 2026-11-02). The 2025 Agent Preview comes up only briefly. Leaderboard data was pulled live from Kaggle's internal API on 2026-09-25 (~15:00 UTC). The Duck harness code was cloned from GitHub and read directly. Kaggle notebooks were downloaded and their code cells were read.

Competition facts used throughout. These frame every score below.
- Hardware and budget: one RTX Pro 6000 (96 GB). The run is 9 h (540 min) with no internet, and it plays 110 games in any order — [Tufa write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133); `maxGpuRuntimeMinutes: 540` in the [Kaggle competition metadata](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3). Kaggle first promised H100s. It then switched to the RTX 6000 Pro after an H100 stockout ([Update on accelerators](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697720)). The runtime was stuck at 6 h until a bug fix in May 2026 ([Submissions not running 9 hours](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699208)).
- Game sets: a submission plays all 110 hidden games — [Greg Kamradt in discussion 703990](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990). The public LB uses 50% (`leaderboardPercentage: 50`, [competition metadata](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3)). Son Pham/Mark Barney's summary of the tech report gives 25 public (demo), 55 semi-private (public LB) and 55 fully private (final) games — [sonpham-org/arc-3 docs/how-this-feeds-kaggle.md](https://github.com/sonpham-org/arc-3).
- Submissions: 1 per day (`maxDailySubmissions: 1`). Deadline 2026-11-02; team-merger deadline 2026-10-26. Kernel-only submissions. 3,317 teams, 3,626 competitors and 38,476 submissions as of 2026-09-25 — [Kaggle competition metadata](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3).
- Prizes: $850K total. That is $75K guaranteed top-score prizes (1st $40K, 2nd $15K, 3rd $10K, 4th–5th $5K each), plus $75K in milestone prizes ($25K/$10K/$2.5K per milestone), plus a $700K grand prize for 100% — [arcprize.org competition page](https://arcprize.org/competitions/2026/arc-agi-3).
- Scoring, as reverse-engineered from the shipped `arc_agi` scorer:
  - Level score = min(115, (baseline_actions/agent_actions)²×100).
  - Game score = Σ(level_index × level_score)/Σ(level_index), capped by the level-index-weighted fraction of levels completed.
  - LB score = mean over games, in percent (max 100). For example, clearing 4 of 6 levels perfectly gives 47.62, not 66.7.
  - Sources: [discussion 728299](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/728299); [discussion 743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060); [discussion 705022](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705022).
- There is no 5×-human action cap on Kaggle. Compute is the only cap — [Greg Kamradt, discussion 713921](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713921).
- Dead clicks count as actions. On lp85, 100 no-op ACTION6 clicks were counted as exactly 100 actions — [discussion 718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638).

---

## Q1. Milestone #1 winners (announced July 2026): Tufa Labs "The Duck", Reki, and Md Boktiar Mahbub Murad "forge". Exact scores and full technical details.

### Takeaway
All three winners ran one local open-weight model on the RTX Pro 6000. The winning scores were very low: 1.21% (Tufa), 0.86% (Reki) and 0.86% (forge).
- Tufa's Duck was the only "agent writes code" design. It is a Qwen 3.6 27B FP8 coding agent in an ephemeral Python REPL, with a 4× upscaled image, a segmentation view, and FIFO context eviction.
- Reki and forge are near-identical "vision-LLM-as-policy" agents on Gemma-4-31B. Both fork the public ko0kip Gemma reflection agent (0.64) and both return JSON actions.
- Reki's gain came from two cheap numpy click heuristics. Forge's gain came from turning its own extra machinery off.

### Cited Findings

**Prize and scores**
- ARC Prize awarded $37.5K for Milestone #1 (ran through June 30). 1st was Tufa Labs "The Duck"; 2nd Reki; 3rd Md Boktiar Mahbub Murad "forge" — [ARC Prize blog](https://arcprize.org/blog/arc-prize-2026-milestone-1); [Kaggle announcement 725002](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/725002).
- Tufa's official LB score was 1.21%. A 1.30% submission was retracted as an excess submission.
  - The same notebook scored as low as 0.77% on Kaggle.
  - On the 25 public games it averaged 1.6 (20 tries/game): mean 1.6002 ± 0.4475.
  - Sources: [Tufa write-up 717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133); [Tong Hui Kang in 709355](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/709355).
- Jeroen Cottaar (Tufa): unmodified reruns are "very unstable, ranging from 0.7 to 1.3" — [discussion 716696](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716696).
- Reki's notebook ("Milestone1-2nd-solution") and forge's notebook both show a best public score of 0.86 — [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution); [forge notebook](https://www.kaggle.com/code/mbmmurad/arc-agi-3-lb-0-86-3rd-place-candidate-milestone); [forge post 716719](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716719).
- LB snapshot at the June 30 deadline, reconstructed from Tong Hui Kang's minute-level history:
  - Ravi's Agi 1.31; Tufa Labs 1.21; Amil Gentili 1.08; Chew Kok Wah 0.88.
  - "i want to go lab😭" (Reki's team) 0.86; Md Boktiar Mahbub Murad 0.86.
  - Tong Hui Kang 0.80; Akhil Tolani 0.79.
  - Source: [arc3.huikang.dev/leaderboard](https://arc3.huikang.dev/leaderboard) (data endpoint `tonghuikang--arc3-leaderboard-monitor-get-history.modal.run`).
  - The prize moves down the ladder to the best open-sourced notebooks — [Nick Pellegrin in 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).

**Tufa Labs "The Duck": design and philosophy**
- Team: Harold Bessis, Jeroen Cottaar, Isaiah Pressman, Dries Smit, Michal Tešnar, Stefano Viel.
- The Duck is the successor to Dries Smit's Stochastic Goose, which won the 2025 Agent Preview. It takes "heavy inspiration" from the RGB Agent (an OpenCode wrapper over a log file) and Symbolica's ARCgentica (a recursive orchestrator, 36% on the public set) — [write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).
- Design principles:
  1. Open models that fit 96 GB, mainly Qwen 3.6 27B FP8.
  2. No game-specific information.
  3. A lightweight harness "keeping the model in the driver seat."
  - Source: [write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).
- Reported drivers of improvement: "better base models and introducing multi-modality."
  - "Against our intuition, hand-crafting specific tools for the model did not help, as it seems to hinder the creative abilities of the model."
  - The harness "has not been scrutinized and ablated over many design decisions" (no formal ablation table published).
  - Source: [write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).

**Duck: model and serving (read from code)**
- Model: `vrfai/Qwen3.6-27B-FP8`.
- Kaggle vLLM launch (`ARC3-Inference/inference/framework/kaggle.py`): `--tensor-parallel-size 1 --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3 --generation-config vllm --enable-prefix-caching --default-chat-template-kwargs {"preserve_thinking": true} --max-model-len 65536`.
- The vLLM 0.19 wheelhouse comes from dataset `driessmit1/arc3-vllm-h100-wheelhouse-v3`. Default expected GPU is `rtx-pro-6000`. Local config uses `gpu_memory_utilization 0.92`.
- Source: [github.com/Tufalabs/duck-harness](https://github.com/Tufalabs/duck-harness) (`ARC3-Inference/inference/framework/kaggle.py`, `configs/inference.json`).

**Duck: sampling and turn budgets (read from code)**
- Temperature 0.6, top_p 0.95, top_k 20, thinking on.
- `max_output` 0, meaning no explicit cap; 512 tokens are reserved for the reply.
- Per-turn "yield" time budget of 60 s.
- Unlimited tool calls per turn on Kaggle (`tool_steps=0`; the code default is 12 when unset).
- Analyzer request timeout 120 s locally. Public forks use 900–1200 s.
- Source: [duck-harness `configs/inference.json`, `kaggle.py`, `tool_agent.py`](https://github.com/Tufalabs/duck-harness).

**Duck: REPL design (read from code)**
- There is one tool, `python`. Each call starts a fresh interpreter, with nothing persisted across calls.
- Hard limits: 30 s timeout. Output capped at ~1024 tokens (4,096 chars; the write-up says "maximum output size of 4096 characters").
- Imports are allowlisted to bisect, collections, copy, fractions, functools, heapq, itertools, json, math, operator, random, re, statistics and string.
- Preloaded variables: `current_frame` (.ascii, .segmentation, .step, .level, .shape), `previous_frame`, `history` (.action/.frame), `transitions` (.before_frame/.after_frame/.result), `last_transition`, `last_action`, `last_action_result` (board_changed, level_completed, game_over, run_complete, reward, valid_actions), and `valid_actions`.
- The model acts by calling `action([...])` inside Python. It can pass a batch, or call it in loops.
- The raw numeric grid is deliberately hidden.
- Actions are renamed to UP/DOWN/LEFT/RIGHT/SPACE/MOUSE(row,col)/RESET. UNDO (ACTION7) is withheld because "it undoes big batches of actions that wastes energy."
- The write-up warns: "The REPL is not fully isolated."
- Sources: [duck-harness `prompts.py`, `tool_agent.py`, `action_names.py`](https://github.com/Tufalabs/duck-harness); [write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).

**Duck: prompt content (read from `prompts.py`)**
- The system prompt is assembled from addenda:
  - "You are a coding agent solving a grid-based puzzle game."
  - Game overview: multi-level; optimize for fewest actions; 64×64 color grids; color legend.
  - Runtime-variable spec.
  - Multimodal guidance.
  - Visual-game guidance: objects are usually multi-tile shapes; do not assume a player avatar exists; verify the background; a long edge line is usually a timer/HUD, so "DON'T" click through segmented edge bars; re-ground after a score increase; MOUSE uses row/col.
  - Python guidance: segmentation first; ascii only for small crops; never print full boards; "write an explicit search algorithm such as BFS" for navigation; probe then search; verify gameplay vs HUD changes; batch reliable sequences.
  - Tool-session rules: "Do not ration tool calls when the state is unclear."
- Source: [duck-harness `ARC3-Inference/inference/agent/prompts.py`](https://github.com/Tufalabs/duck-harness).
- Each user turn re-states:
  - how many actions the previous sequence executed and which ones;
  - whether the level advanced;
  - step/level and valid actions;
  - the tool rules;
  - a carried "working world model" (World model / Goal model / Action model / Recent findings / Open questions / Plan / Cross-level notes).
  - It also insists: "BEFORE EXECUTING NEW ACTIONS YOU MUST ALWAYS GIVE THE REVISED VERSION OF THE WORLD MODEL."
  - The world model is parsed from labelled lines in the assistant's visible text, and reset on level transition, game over or run complete.
  - Source: [duck-harness `tool_agent.py` `_build_user_prompt`, `_update_summarized_knowledge_*`](https://github.com/Tufalabs/duck-harness).

**Duck: perception**
- A 4× upscaled PNG of the current frame (64×64 → 256×256) is attached to every user turn. Tufa: "Qwen's encoder processes images in 16×16 pixel patches and we found that this upscaling gives the model the best visual understanding."
- Only the current frame is sent. "We also tried injecting more frames or video animations, but … small models struggle," so animation feedback is lost, e.g. in sb26 and tn36.
- Segmentation (`inference/utils/segmentation.py`) splits the frame into 4-connected same-color components. Each has an id, color, a position-invariant shape hash, pixel count, clockwise boundary corner points, and enclosed children, plus an adjacency list. It was added because the model tended to print whole grids and pollute its own context.
- Sources: [write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133); [duck-harness `vision_context.py`, `segmentation.py`, `configs/inference.json` (`"multimodal": {"context": "current_grid", "upscale": 4}`)](https://github.com/Tufalabs/duck-harness).

**Duck: context management and eviction**
- vLLM max context is 64k (65,536). The harness keeps the input at about 32,768 tokens minus a 512 reply reserve and a 512 safety margin, "by evicting the oldest user message and subsequent assistant turns."
- The system prompt is always kept.
- Persistent history is also capped at the last 30 assistant turns (`_PERSISTENT_HISTORY_ASSISTANT_TURNS = 30`).
- On a server context-overflow error it force-drops the oldest block and retries.
- Tufa: "We currently do not optimally use prefix caching."
- Sources: [write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133); [duck-harness `tool_agent.py` `_trim_messages_for_context`, `_drop_oldest_history_block`](https://github.com/Tufalabs/duck-harness).

**Duck: time budget and concurrency**
- Kaggle rule: 9 h to play 110 games — [write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).
- The TAAF runner derives the per-game cap as experiment_budget / waves.
- Public Duck-lineage Kaggle notebooks use `concurrency=28` and `max_runtime_s_per_game=7920` (132 min; 4 waves × 132 ≈ 528 min of 540).
- Sources: [duck-harness `run.py`](https://github.com/Tufalabs/duck-harness); [yw8837 LB 1.17 post 731522](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/731522); [Duck Qwen3.8 Anim Base notebook](https://www.kaggle.com/code/wuliao0/duck-qwen3-8-anim-base).
- The TAAF `deploy_kaggle.py` default is `max_runtime_s = 12*3600`, with a 600 s soft-deadline buffer.
- The competition-arcade simulator clones the 25 public games to 110 runs so the full submission shape can be tested locally — [duck-harness `tufa-arc-agi-framework/src/taaf/competition_arcade.py`](https://github.com/Tufalabs/duck-harness).
- The in-house benchmark config uses 45 min/game, 20 passes and 32 concurrent games per GPU on 2×B200 — [duck-harness `configs/inference.json`, `example-run/run_config.json`](https://github.com/Tufalabs/duck-harness).

**Duck: click handling**
- There is no click heuristic. The model computes `MOUSE(row=..., col=...)` from segmentation/ASCII in Python.
- The only click guidance is prompt-level: treat edge bars as HUD, and don't click through them segment by segment.
- Source: [duck-harness `prompts.py`](https://github.com/Tufalabs/duck-harness).

**Duck: bundled example run (25 official games × 20 passes = 500 runs)**
- Mean 1.60, median 0.07, 0 full game wins.
- 68,682 actions; 29.6M tokens; 6 h 10 m on 2 GPUs at 1,331 generated tok/s.
- Best game ft09 at 10.28 (1.5/6 levels). tr87 and wa30 scored 0.00.
- Source: [duck-harness `example-run/summary.txt`](https://github.com/Tufalabs/duck-harness).

**Duck: stated weaknesses and next steps**
- The prompts had to encode much ARC-specific steering: not treating the energy bar as the objective; not inventing goals like "move block to fixed position"; not hallucinating robots/Atari sprites; not dumping full boards.
- Suggested improvements: compaction/memory, and better perception.
- Source: [write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).
- Tufa's blog says frontier models in the Duck (GPT 5.4) "solve a similar set of games" to the Executable World Models agent (58.12%) at "an order of magnitude cheaper on each game." It frames solvability as model-bound and cost as harness-bound — [Tufa blog](https://tufalabs.ai/research/duck-harness/).

**Reki (2nd): overview**
- A "vision-LLM-as-policy" agent. Each turn it renders recent frames as labelled images, sends them to a local Gemma-4-31B, and asks for one JSON object: what changed, a short plan, and the next 1–4 actions.
- Reflection memory is refreshed every ~10 steps.
- It is built on the official GPT-OSS-120B template, with the model swapped out.
- Source: [ARC Prize blog](https://arcprize.org/blog/arc-prize-2026-milestone-1).
- Code: the notebook header says it is the "V25-fusion" build.
  - Two default-ON pure-numpy click-path additions sit on top of a "byte-identical 0.64 base."
  - The 0.64 base matches the public [ko0kip Gemma-4-31B Reflection Agent](https://www.kaggle.com/code/ko0kip/arc-agi-3-gemma-4-31b-reflection-agent) (LB 0.64).
  - Source: [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution).

**Reki: model and serving (read from code)**
- Model `google/gemma-4 … gemma-4-31b-it` via vLLM 0.23.0 wheels, with no quantization flag (dtype auto).
- vLLM flags: `--max-num-seqs 20 --gpu-memory-utilization 0.94 --max-model-len 32768 --enable-prefix-caching --trust-remote-code`.
- Source: [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution).

**Reki: sampling (read from code)**
- Temperature 0.6 when thinking, 0.2 when not. Action thinking is off by default (`LLM_ACTION_THINKING=0`, `/no_think`).
- top_p 0.95, top_k 20, repetition_penalty 1.08.
- `response_format={"type":"json_object"}`.
- Token limits: action 1024 max new tokens; JSON-repair 256; reflection 10,000 with `/no_think`.
- Source: [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution).

**Reki: budgets and state (read from code)**
- `MAX_ACTIONS=200` per game. `GAME_TIME_LIMIT_S=8h`. Global 9 h with a 20 min shutdown reserve.
- 14 min first-action deadline.
- Swarm runs one thread per game against a shared vLLM.
- History windows: `MAX_HISTORY=12`, `MAX_FRAME_MEMORY=11`, `ACTION_CONTEXT_FRAMES=4`.
- Reflection: `REFLECTION_INTERVAL=10`, `MAX_REFLECTION_CHARS=1800`. `MAX_PLAN_ACTIONS=4`.
- `FRAME_BORDER_IGNORE=3`. `FRAME_IMAGE_SCALE=8`, so each frame is 512×512 with a red "STEP n" label.
- Source: [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution).

**Reki: prompts (read from code)**
- Action prompt:
  - "You are the action agent for an interactive ARC-AGI-3 visual game. The images are chronological; the last is current… Infer the controllable object, causal action effects, and current objective. Prefer purposeful new states. A repeated state is not progress. Do not invent counters, bars, or goals without evidence."
  - It then lists: legal actions for this exact state; "Ineffective in this exact state" (a per-frame-hash failed-action set); reflection memory ("authoritative but revisable"); the last 4 transitions; and 1–4 actions ("use one exploratory action if uncertain").
- Reflection prompt: rewrites a Markdown memory with fixed headings `# Agent Memory / ## Rules / ## Goal / ## Progress / ## Avoid`, "Distinguish confirmed rules from hypotheses."
- Source: [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution).

**Reki: click handling (the part that is new vs the base)**
- `GEMMA_SALIENT_CLICK`: fallback and empty-plan clicks pick the most "button-like" untested connected component.
  - Saliency = 0.5·color-rarity + 0.5·size-score.
  - Size-score: ≤4 px → 1.0; ≤16 → 0.8; ≤64 → 0.5; ≤256 → 0.25; else 0.
- `GEMMA_DEADSIG`: the structural signature is (color, size, is_rect, twin-count). A class whose click never changes the frame K=2 times is suppressed for the rest of the level. Any class that ever changes the frame is protected.
- `GEMMA_DEADSIG_VETO_LLM` also vetoes the LLM's own clicks on dead classes.
- Each feature toggles with an env var so it can be ablated.
- Sources: [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution); [ARC Prize blog](https://arcprize.org/blog/arc-prize-2026-milestone-1).

**Forge (3rd)**
- A single-file `MyAgent` running local Gemma-4-31B-it through vLLM. It converts recent frames into chronological STEP-labelled images and asks for JSON actions, with JSON validation/repair and a short per-game reflection memory — [forge post 716719](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716719).
- Author credit: "My submission was an improved version of" [ko0kip's notebook](https://www.kaggle.com/code/ko0kip/arc-agi-3-gemma-4-31b-reflection-agent). Their score went from 0.33 the day before to 0.86, and they also credit "my Codex agent" — [forge post 716719](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716719).
- Scored profile `gemma31b_public_single`:
  - `LLM_ACTION_CANDIDATES=1`, `LLM_CANDIDATE_ARBITER=0`, `LLM_CONFIDENCE_PROMPT=0`, `LLM_INCLUDE_FRAME_DESCRIPTOR=0`.
  - `LLM_ACTION_CONTEXT_FRAMES=4`, `LLM_MAX_NEW_TOKENS=1024`, `LLM_MAX_PLAN_ACTIONS=4`, `LLM_REFLECTION_INTERVAL=10`, `LLM_REFLECTION_MAX_NEW_TOKENS=10000`.
  - `VLLM_LIMIT_MM_PER_PROMPT={"image":4}`, `VLLM_MAX_MODEL_LEN=32768`, `VLLM_MAX_NUM_SEQS=20`, `VLLM_GPU_MEMORY_UTILIZATION=0.94`.
  - `MAX_ACTIONS=200`, `GAME_TIME_LIMIT_S=8h`, `FRAME_IMAGE_SCALE=8`.
  - Source: [forge notebook](https://www.kaggle.com/code/mbmmurad/arc-agi-3-lb-0-86-3rd-place-candidate-milestone).
- Profiles that were switched off:
  - The default in code is `forge_v37_gemma31b_multicandidate_arbiter`, with 3 candidates. Candidates get a static score of +8×confidence, and then an LLM arbiter prompt: "You are choosing among candidate action plans…".
  - A confidence prompt tells the model: "If confidence is below 0.55" prefer safe/reversible moves.
  - "The top-scoring run… used a profile that turns off all of the extra machinery."
  - Sources: [forge notebook](https://www.kaggle.com/code/mbmmurad/arc-agi-3-lb-0-86-3rd-place-candidate-milestone); [ARC Prize blog](https://arcprize.org/blog/arc-prize-2026-milestone-1).
- Author's caveat: "local public-suite checks were useful for catching packaging and runtime failures, but they were not a perfect leaderboard proxy" — [forge notebook](https://www.kaggle.com/code/mbmmurad/arc-agi-3-lb-0-86-3rd-place-candidate-milestone).
- Forge variance: an untouched copy of the 0.86 notebook scored 0.00. Reki attributes this to an "infra/timeout failure, not the agent 'being random'" — [discussion 725002](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/725002).

### Inferences
- In practice, Milestone #1 was decided by the base model and the "act inside code" interface, not by elaborate harnesses.
  - Duck (27B coder model, REPL, batched actions) beat both Gemma JSON-policy agents by about 40%.
  - Both Gemma agents scored better with their "smart" features switched off (forge) or when the only additions were cheap deterministic click pruning (Reki).
- Reki's and forge's winning deltas over the 0.64 base, +0.22 each, are within the run-to-run noise reported elsewhere (0.7–1.3 for the same Duck notebook). How much the specific tricks contributed is therefore unproven.
- The Duck's key design choices were all copied by later top public notebooks: unlimited tool calls per turn with a 60 s turn yield, a 32k working context inside a 64k server window, and FIFO eviction plus a carried world-model note.

### Gaps
- Tufa published no quantitative ablations for image vs no-image, eviction thresholds, segmentation on/off, or tool steps. They say the harness "has not been scrutinized and ablated."
- I could not recover Reki's own ablation numbers for `GEMMA_SALIENT_CLICK`/`GEMMA_DEADSIG`. The blog and notebook only say they are toggleable.
- I found no text summary of the MLST (YouTube) interview beyond secondary summaries.
- I could not retrieve Tufa's own per-draw Milestone #1 submission list beyond 1.30 (retracted), 1.21 and a low of 0.77.

---

## Q2. Current Kaggle leaderboard (as of 2026-09-25). Are top scores ~1–5% or higher? What changed since Milestone #1?

### Takeaway
Top scores are far above 1–5%. The public LB top is 19.45%, with nine teams at 10% or more.
- The biggest jumps followed model releases:
  - Qwen 3.8 27B on about Aug 14: top went from ~1.9 to ~2.7.
  - Qwen3.8-Flash-Next NVFP4 in late Aug/early Sep: 7.5.
  - Private improvements by Tufa, NVIDIA (NVARC3) and others (Sep 6–24): 11 → 19.45.
- The best public notebooks sit at only ~4.3–4.5.
- Tufa Labs and NVARC3 say they will not open-source for Milestone #2.

### Cited Findings

**Top 20 (public LB, 2026-09-25)**
Source: [Kaggle LB](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard) via Kaggle internal API; also [arc3.huikang.dev](https://arc3.huikang.dev/leaderboard).

| # | Team | Score (%) | Submissions |
|---|---|---|---|
| 1 | Lord Han Solo (solo) | 19.45 | 73 |
| 2 | Tufa Labs (dlorah, Dries Smit, IsaiahP, Stefano Viel, InfiniteCreativity, Jeroen Cottaar) | 18.81 | 146 |
| 3 | Yi-Chia Chen (solo) | 18.63 | 11 |
| 4 | Daniel Franzen (solo) | 16.68 | 82 |
| 5 | NVARC3 (CPMP, Darragh, ivan/sorokin, Elad Sarafian, Gal Kaplun, Yeyin Zhu) | 16.07 | 20 |
| 6 | Tong Hui Kang (solo) | 15.02 | 83 |
| 7 | the last dance 🕺 (gklambauer, fses91, M I, Lukas Aichberger) | 13.70 | 62 |
| 8 | Matija Ludvig & Zhongwei Wang | 11.64 | 84 |
| 9 | Fususu | 10.66 | 90 |
| 10 | Third Intelligence | 8.81 | 56 |
| 11 | Ebi | 8.68 | 25 |
| 12 | Skyfall AI | 7.67 | 35 |
| 13 | Tanaka Ai24 | 7.55 | 51 |
| 14 | mostik.ai (8 members) | 7.51 | 47; last submitted 2026-09-06 |
| 15 | UNK | 7.37 | 65 |
| 16 | Son Pham & Mark Barney | 7.36 | 59 |
| 17 | Mark Slavin | 7.29 | 26 |
| 18 | Grigoriy Zatravkin | 7.22 | 51 |
| 19 | face-of-agi | 7.18 | 35 |
| 20 | rellik13 | 7.14 | 37 |

Other teams of interest: Reki's team "i want to go lab😭" is #31 at 5.57. Thuitanium is #37 at 5.36. tantan is #45 at 5.10.

**Score distribution**
- Of 3,320 scored teams: 9 score ≥10; 49 score ≥5; 849 score ≥2; 1,243 score ≥1.
- Median 0.31. Rank 100 = 4.32; rank 200 = 3.92; rank 500 = 3.23; rank 1000 = 1.39.
- Source: [Kaggle LB](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard) (computed from the full LB JSON).

**Timeline of the LB top** (from Tong Hui Kang's history; [arc3.huikang.dev](https://arc3.huikang.dev/leaderboard))
- April–May: ≤0.42.
- 2026-06-01: 0.66.
- 2026-06-08: Tufa 1.21.
- 2026-06-30: Ravi's Agi 1.31.
- After the Duck release on 2026-07-01: 23 teams ≥1.0; 115 teams ≥1.0 by 2026-07-08; top ~1.86 through early August.
- 2026-08-14: Daniel Franzen 2.58.
- 2026-08-16: Lord Han Solo 2.76.
- 2026-08-22: mostik.ai 3.57.
- 2026-09-01: mostik.ai 7.51.
- 2026-09-06: Tufa 11.04.
- 2026-09-13: Tufa 18.81.
- 2026-09-19: NVARC3 16.07.
- 2026-09-22: Lord Han Solo 19.40, then 19.45 on 09-24.
- 2026-09-24: Yi-Chia Chen 18.63 (from 12.88 on 09-19); Daniel Franzen 16.68; Tong Hui Kang 15.02.

**Model releases and community reaction**
- Ya Xu: Qwen 3.8 27B (released ~Aug 14) gives "a consistent 2x score on the local 25 dataset." DeepSeek-V4-Flash was "only slightly better than Qwen-3.6 27B" — [Qwen 3.8 release thread 735243](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735243).
- Several users noted the top teams jumped right after the release — [735243](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735243); [735381](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735381).
- Scott Le Grand: "I made it to position 19 back in the ancient times of Qwen 3.6, got booted to 160 or so with the advent of Qwen 3.8, and now I'm in the nosebleed bleachers with Qwen 3.8-Flash-next-nvfp4" — [discussion 737617](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/737617).
- Qwen3.8-Flash-Next is described as a "125B MoE with 6B active parameters and native 262k context" that fits the RTX PRO 6000 "only via FP4 + host-offloaded N-gram embeddings" — [gedouluhui write-up 743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060).
- Son Pham/Mark Barney: "On the seven games the 27B never clears, Flash-Next clears every one at matched clock… the checkpoint is separable" — [sonpham-org/arc-3 HARNESS-NOTES.md](https://github.com/sonpham-org/arc-3).

**Milestone #2 open-sourcing intentions**
- Tufa Labs (2026-09-23): "We… will not be sharing our solution on September 30 for the second milestone prize, since we worry it may not be possible to beat the best of 4000 copies… We still plan to release our final solution when the competition ends."
  - They also note: "all high-scoring public notebooks now building on this harness."
  - Source: [discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
- CPMP (NVARC3): "I don't think we will share either… We will open source our code at the end of competition if we end up in gold. As usual for NVIDIA teams." — [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
- Tong Hui Kang will "very likely" share if no higher-placed team does — [discussion 742935](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742935).
- Scott Le Grand speculates Tufa's lead is "part… some fine tuning" (speculation) — [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).

**Other context**
- mostik.ai held #1 (7.51 on 2026-09-01) and stopped submitting after 2026-09-06, following a thread about a claimed 12-person team vs the 8-member limit — [discussion 739186](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739186).
- A team using "AVO style ideas" (rfbr, team UNK) "haven't seen them beat our current harness yet" — [discussion 737617](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/737617).
- Frontier context, outside Kaggle constraints:
  - GPT-6 Astra: 62.7% on the semi-private set with the standard harness ($26K); 99.9% with a "Provider Adapter" harness ($19K) — [ARC Prize blog, 2026-09-03](https://arcprize.org/blog/astra).
  - Claude Opus 5: ~30% — [discussion 728934](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/728934).
  - Community leaderboard, public 25: Tycho (Opus 5) 100.0; Retrodict v2.0 99.86; NVIDIA AVO 100 (self-reported); best open-weight entry "Polyphony Agent" (Qwen3.6, self-hosted) 19.8 — [criticaldata/avo-qwen-arcagi3 docs/results.md](https://github.com/criticaldata/avo-qwen-arcagi3).

### Inferences
- The top five (15–19.5%) are 3.5–4.5× the best public notebook (4.5). The public forks all run the same Duck + Qwen3.8-Flash-Next stack, so the top teams must have something non-public. Likely candidates: fine-tuned weights (STaR/RL), a different or modified base model, much better throughput, or substantive harness changes. None of this is confirmed; no top-5 team has published its method.
- Tufa's step from 11.04 → 18.81 in one week (Sep 6 → Sep 13), with no public model release in between, suggests a proprietary change rather than a new checkpoint. This is an inference only.
- The Milestone #2 prize will probably go to whoever is the highest-placed team that open-sources. Given the stated intentions, that may be a team ranked well below the top 5.
- Two heuristics for estimating this LB: the leaderboard is a max over noisy draws, and a public notebook's single-draw spread is ±50%. So a 4–5% team is not meaningfully different from a 3% team.

### Gaps
- No top-5 team (Lord Han Solo, Tufa, Yi-Chia Chen, Daniel Franzen, NVARC3) has disclosed its approach, model or fine-tuning. I found no X/Twitter or blog post explaining the 11 → 19% jumps.
- The private (final) LB is withheld until the end, so every score here is public/semi-private.
- I could not verify the claim that the host (Greg) said the 55 semi-private games are harder than the public 25 by a specific factor. Only "Public Demo was made to be easier than semi private" is sourced ([703990](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990)).

---

## Q3. Popular public Kaggle notebooks and high-vote discussions: approaches, reported LB scores, key tricks

### Takeaway
After July, virtually every high-scoring public notebook is a Duck fork. The winning public recipe is:

> Duck harness unchanged + RadixArk Qwen3.8-Flash-Next-NVFP4 + vLLM tuning (MTP, KV size, concurrency 28, 132 min/game).

It scores 3.4–4.5 LB (5–7 on the local public 25).

Community A/Bs that survived:
- throughput tuning (MTP off with a bigger KV cache, or MTP on with a newer vLLM);
- surfacing animation frames;
- a no-op guard;
- backfilling the world-model note from hidden reasoning;
- deterministic click candidates;
- stating the true scoring formula in the prompt;
- STaR LoRA on the agent's own wins.

What failed: longer context, lower temperature, archetype playbooks, multi-role agents, and strategy libraries.

### Cited Findings

**Most-voted notebooks (votes | best public score)**
Source: Kaggle kernel list for competition 133468 (sorted by votes / by score), e.g. [code tab](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/code).
- Official "ARC3 Sample Submission – Stochastic Goose" (690 | 0.25) and "Random Agent" (626 | 0.18) — [Stochastic Goose sample](https://www.kaggle.com/code/inversion/arc3-sample-submission-stochastic-goose).
- Tufa "duck harness [June 30 milestone winner]" (334 | 1.25) — [notebook](https://www.kaggle.com/code/jeroencottaar/tufa-labs-duck-harness-june-30-milestone-winner). "taaf-duck-harness-kaggle" (251 | 1.30).
- "LB-9 arc3 duck v12 with Qwen 3.8 27B" (288 | 2.23) — [notebook](https://www.kaggle.com/code/foysalemonshanto/lb-9-arc3-duck-v12-with-qwen-3-8-27b).
- "Duck Qwen3.8 Anim Base" (260 | 4.33) — [notebook](https://www.kaggle.com/code/wuliao0/duck-qwen3-8-anim-base).
- "Duck Qwen3.8 (Tuned)" (199 | 4.50, the best public notebook score) — [notebook](https://www.kaggle.com/code/chiakazirim/duck-qwen3-8-tuned).
- "Duck Qwen3.8 Flash Next NVFP4 MTP" (183 | 3.38) — [notebook](https://www.kaggle.com/code/keithtyser/duck-qwen3-8-flash-next-nvfp4-mtp).
- "TAAF · Anim" (120 | 1.61) — [notebook](https://www.kaggle.com/code/jakobbrggen/taaf-anim-arc-agi-3-solver).
- Non-LLM search agents plateau around 0.4–0.5:
  - "[0.46] Persistent Memory BFS" (152 | 0.46);
  - "Hybrid Solver (BFS + CNN + Heuristics)" (100 | 0.42);
  - "FORGE ARC-AGI-3 Agent" by projectforty2 (165 | 0.39), a different "forge" from Murad's.

**What the top public forks actually are (read from code)**
- They are the Tufa notebook with the model swapped to `RadixArk/Qwen3.8-Flash-Next-NVFP4` and "Duck prompts, tool-use loop, game policy, and scorer… unchanged" — [Anim Base notebook](https://www.kaggle.com/code/wuliao0/duck-qwen3-8-anim-base); [Flash Next NVFP4 MTP](https://www.kaggle.com/code/keithtyser/duck-qwen3-8-flash-next-nvfp4-mtp).
- vLLM profile `kv5-bf16-mtp3-c8-cg32`: ModelOpt NVFP4 weights with BF16 compute; async scheduling; chunked prefill; 3-token NEXTN MTP speculative decoding; 32K context; 8,192 max batched tokens; 8 sequences; KV cache 5 GiB; CUDA graphs up to 32; prefix caching disabled.
- Also added: a watchdog that restarts vLLM after 4 failures.
- Run settings: `concurrency=28`, `max_runtime_s_per_game=7920`, `analyzer_timeout=900` (1200 in the "Tuned" fork, which is its main visible difference).
- Their saved public-25 runs (single pass, ~2 h 12 m, ~235–280 generated tok/s) scored 5.78 (Anim Base), 5.16 (Tuned) and 6.76 (Flash Next MTP). Their LB bests are 4.33, 4.50 and 3.38. Sources: [Anim Base notebook](https://www.kaggle.com/code/wuliao0/duck-qwen3-8-anim-base); [Tuned notebook](https://www.kaggle.com/code/chiakazirim/duck-qwen3-8-tuned); [Flash Next NVFP4 MTP notebook](https://www.kaggle.com/code/keithtyser/duck-qwen3-8-flash-next-nvfp4-mtp).

**Throughput profile (Thuitanium "B81")**
- `kv7-bf16-mtp0-c28-cg32`: MTP off, KV 7 GiB, 28 concurrent sequences, a fixed sampler seed, a 180 s yield, and Jakob's animation-aware solver bundle.
- Reasoning: "with MTP on, the draft head leaves no memory for a wider KV cache, so the server runs ~3 requests and queues ~22; with MTP off the KV cache holds 263,568 tokens and the queue halves."
  - Time to first token fell from 126 s to 66 s.
  - Model calls rose from 1,369 to 1,780.
  - 45 levels vs a 32–41 band on the public 25.
- Reported hidden-set draws: 4.50, 3.86, 3.03, 5.36 (mean 4.19).
- Sources: [tantan0327/arc-agi-3-agent SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent); original repo github.com/Sahasawatt/arc-agi-3-agent (per that SOLUTION.md).

**Serving/engine changes that helped**
- tantan: the only one of 14+ tested modifications that beat its baselines was "the same public recipe served through a newer vLLM with multi-token prediction enabled." It scored 2.27 vs the family's 1.9–2.2 band, and +7 levels offline. "Faster, losslessly identical decoding buys levels only when it changes what fits inside the per-game clock" — [tantan0327 SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent).
- Rakha Abid Bangsawan: deterministic, pinned serving (fixed model/profile, MTP and concurrency config, startup and tool-call preflight, fail-closed on the wrong parser) "produced a more reliable improvement than several complicated prompting experiments" — [discussion 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).
- Fususu: concurrency beyond 16 hits a saturation point — [739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).

**Animation access (Jakob Brüggen, "TAAF Anim", LB 1.61)**
- The API returns a list of frames, but the Duck uses only `frame[-1]`. 13 of the 25 public games return multi-frame responses; sp80 pouring returns 22 frames with 624 transient pixels.
- Added:
  1. always-on compact `animation` metadata;
  2. an `animation()` tool;
  3. a proactive hint.
- A hard no-op guard blocks exact repeats of `(level, board, action)` that were already proven to be no-ops, at zero action cost.
- Public A/B: +1.4% mean, p = 0.92 (6 games × 4 passes). Tokens/action rose from 384 to 449 (+17%). The model called the tool in 21/24 runs, but only 2 of 181 calls hit an informative animation.
- "Every run in both arms hits the 132-minute wallclock cap."
- Source: [write-up 734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369).

**Hidden-reasoning memory bug**
- Jason Feng: the Duck only updates its world-model note from visible text. With Qwen, 1,723/2,580 tool-call responses (66.8%) had zero visible content.
- With DeepSeek V4 Flash, making updates visible improved the local score from 9% to 11%.
- Source: [discussion 734843](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734843).
- tantan found the note stayed empty for whole games with Flash-Next (bp35 55/55 turns; sk48 53/53). Their patch backfills it from reasoning. In one run this gave 38 levels vs 32 for the control, with sk48 L1, m0r0 L2 and sb26 L2 newly reached — [tantan0327 SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent).

**Perception-Augmented Duck (gedouluhui, hidden 1.43 with Qwen3.8-27B FP8)**
- Kept:
  - Qwen3.6 → 3.8 swap (hidden 1.12 with no other change).
  - Deterministic connected-component click candidates (centroids ranked by salience) injected when MOUSE is valid.
  - Two prompt lines: the true quadratic scoring rule with "commit to the shortest reliable sequence and batch confirmed steps," and `time_remaining_seconds` pacing with "change the hypothesis class" after repeated failures. Together: 1.12 → 1.43 (+28%).
- Rejected:
  - Context 32k → 64k: 1.20. Throughput fell from ~283 to ~195 tok/s, and bp35 produced zero actions.
  - Temperature 0.6 → 0.3: 0.95. "Games with any progress collapsed from 12 to 8."
  - Archetype playbook (NAVIGATION/PATTERN/PHYSICS/…): 1.54, below its pre-registered line, because of "premature commitment."
- Measured serving throughput: ~283 tok/s decode at 4k context vs ~30 tok/s at 32k (prefill-dominated).
- Across runs of one config, 17/25 games were cracked at least once, but only ~5–8 in any single run.
- Source: [discussion 743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060).

**Fine-tuning on the agent's own wins**
- manas joshi LoRA-SFT'd Qwen3.6-27B on the Duck's own level-completing trajectories (STaR / rejection sampling). LB went from 1.25 to 1.94.
- "naively scaling the data hurt," and adapters are base-model-specific.
- Released: [arc3-sft-trajectories](https://www.kaggle.com/datasets/justforgags/arc3-sft-trajectories) and [arc3-duck-lora-sft](https://www.kaggle.com/datasets/justforgags/arc3-duck-lora-sft).
- Source: [discussion 739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047).
- Counter-reports:
  - Ya Xu: LoRA "only backfired."
  - Scott Le Grand: behavioral cloning took local 11.04 → 12.97, but "you have to use reasoning traces from the same model or it's a regression."
  - AAAAAtjc built an RL pipeline for Qwen3.8 Flash Next on a full H200 node ("rtx 6000 pro can not be used for training of any ~100B model") with no gain yet.
  - Sources: [739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047); [732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854); [742835](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742835).

**Other reported lessons**
- Fususu:
  - Gemma 4 31B sees better than Qwen 3.6 27B but "falls far behind" in logic/coding.
  - A symbolic "system decoder" lets GPT-OSS play, but it takes roundabout routes and adds game bias.
  - Observer/Theory/Action/Advisor roles improve reasoning but cost 5× the calls.
  - Thinking on vs off changed little.
  - Human-play imitation data didn't beat base Qwen 3.8.
  - A strategy library adds game-specific bias.
  - Source: [discussion 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).
- Rakha:
  - Single-step verified recovery beats eager recovery.
  - Memory should store verified transition facts.
  - Roles should be gated (verifier only for risky actions).
  - A progress-weighted compute allocator saved ~13.6% of actions with 0 lost progress in shadow mode.
  - Source: [739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).
- yw8837 (LB 1.17):
  - A patch to stop repeating an identical cardinal move if the board is unchanged.
  - Yield 60 → 90 s.
  - Released an 11-submission ledger: 1.29, 1.05, 0.71, 0.73, 0.68, 0.75, 0.55, 1.11, 1.17, 0.90, 0.94.
  - Source: [discussion 731522](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/731522).
- ACTION7: its docs call it "Simple undo action." Duck forks hit an index error, and models hallucinate it as "jump." Explicitly naming it UNDO gave one user their best score (anecdotal) — [discussion 742477](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742477).
- Upscale knob: the write-up found 4× best on Qwen3.6, while popular Qwen3.8 forks use `MULTIMODAL_UPSCALE=8` "documented… as the arm that moved the score." There is no clean A/B, and identical config passes scored 2.85 vs 4.75 — [discussion 739801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739801).
- Son Pham/Mark Barney, running their own A/B infrastructure on a "gx10-a108" box:
  - A compact-reasoning prompt cut tokens/action 874 → 595. The model got +43% actions at the same clock (19/25 games improved, p = 0.007), "but the apparent score gain rests entirely on one game [sb26]."
  - "Delete false claims from the prompt before adding true ones": the only prompt arm with a paired signal removed four assertions ("puzzle", 64×64 world, HUD rule, 100% cap).
  - Sources: [sonpham-org/arc-3 docs/compact-reasoning-style-experiment.md, HARNESS-NOTES.md](https://github.com/sonpham-org/arc-3).
- Scott Le Grand:
  - Claude Fable-built game-specific solvers reached ~38% RHAE on the public 25 (116/183 levels) but needed 5 days and frontier access. The general solver distilled from them "kept overfitting."
  - "Most of what I have done is just take the stock duck client for nvp4 and increase the sequence concurrency to 16. Anything else… amounted to jack."
  - Source: [discussion 732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).
- Akhil Tolani: Gemma 4 31B QAT with a pruned vocab plus a LeWM/JEPA dynamics model scored 0.6–0.8 LB — [discussion 716711](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716711).

### Inferences
- In the public domain, throughput-per-decision is the dominant lever. Every Duck-lineage run is wall-clock-bound, so changes that add tokens per action (animation, longer context, more frames) cost moves. Changes that raise tokens/sec or cut tokens/action (MTP tuning, KV sizing, compact reasoning) buy moves.
- Prompt engineering moves hidden scores by at most ~±30% in controlled tests (1.12 → 1.43). Model swaps moved them 2–3×.
- Bug fixes to the Duck (hidden-reasoning note, dropped animation frames, ACTION7 labeling) are real, cheap, and probably part of what top teams already did privately. Their measured public gains are small and noisy, though.

### Gaps
- I could not see the exact code diff between "Anim Base" (4.33) and "Flash Next NVFP4 MTP" (3.38). Both attach the same `keithtyser` datasets; the visible differences are timeouts only. The score gap is plausibly draw variance.
- There is no public, controlled evidence on SFT/RL of Qwen3.8-Flash-Next under Kaggle rules.
- I did not read every one of the 220 discussion topics. Coverage was the top ~100 by votes plus recent threads.

---

## Q4. Other open-sourced ARC-AGI-3 agents on GitHub: what they do and what they score

### Takeaway
None of the requested GitHub repos is a top-leaderboard system.
- sonpham-org/arc-3 (LB 7.36 team) is an instrumented Duck lab plus a 927-game synthetic catalog.
- tantan0327 (LB 5.10) runs byte-identical public forks, with a symbolic agent that scored 0.25.
- criticaldata/avo-qwen-arcagi3 is an unrun Cerebras "retrodiction" harness.
- dcw06, Panus15 and arodmor are process scaffolds or explainers with ~0 LB results.
- The only strong open-weight harness outside Kaggle is the community-leaderboard "Polyphony Agent" (Qwen3.6, 19.8% on the public 25, not Kaggle).

### Cited Findings
- **Tufalabs/duck-harness**: MIT. It contains the full Duck source (`ARC3-Inference`), the TAAF framework, the Kaggle notebook, a 2.8 GB example run and a viewer. Forks exist, e.g. Wang-Zhongwei/duck-harness and KazuSh1geru/duck-harness — [GitHub](https://github.com/Tufalabs/duck-harness); [license confirmation in 717133 comments](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).
- **sonpham-org/arc-3** (Son Pham & Mark Barney, LB #16 at 7.36): an "instrumented Tufa fork, GCP spot kit, run logs, reproduction matrix."
  - It hosts a catalog of 927 games: 25 official, 571 AI-generated, 252 redbluepill, 50 reviewed "arena" and 29 custom.
  - Its pipeline: author synthetic games that are "deliberately divergent on mechanics," let the Duck play them, keep only solved levels (rejection sampling), and SFT the model "on its own wins."
  - Measurement rules: never trust single-pass deltas (sb26 alone swings the all-25 score by ±23; the sd of a two-pass difference is ~21). Use paired 4-pass per-game sign tests.
  - Source: [GitHub](https://github.com/sonpham-org/arc-3) (README, HARNESS-NOTES.md, docs/how-this-feeds-kaggle.md).
- **tantan0327/arc-agi-3-agent** (team "tantan", LB 5.10):
  - A from-scratch symbolic agent scored 0.25 LB.
  - An unmodified Duck fork scored 0.98/1.14/1.11/1.23 across four byte-identical submissions.
  - It later ran byte-identical copies of keithtyser's Flash-Next build (floor ~2.88 mean over 20 draws), then Thuitanium's B81 build.
  - It contains `duck_delta/` perception layers (click_effect, noop_guard, stall_guard, physics_planner, frontier_map, …), which were "not demonstrated to help."
  - Its key analysis: "98.3% of a solving trajectory's decisions occur at a board state never seen before in that game, so what binds is the model's ability to reason about a novel configuration, and no harness engineering raises that ceiling."
  - Source: [GitHub SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent).
- **criticaldata/avo-qwen-arcagi3** ("arc3cb"): a Cerebras-API harness for open-weight models (gpt-oss-120b, gemma-4-31b, planned qwen3.8-27b). Design:
  - log-as-context (the full hex grid plus a diff line per frame in `log.txt`);
  - "retrodiction before action" (test hypotheses against the recorded history in Python);
  - plan queues with expected cells that halt on the first mismatch;
  - playbook memory with a context reset at 90k tokens;
  - escalation tiers that force an executable `step(state, action)` simulator after 300 stuck actions.
  - Status: "harness complete; campaign not yet run" (no scores). It is not a Kaggle submission, because it needs an external API.
  - Source: [GitHub README, docs/results.md](https://github.com/criticaldata/avo-qwen-arcagi3).
- **dcw06/ARC-AGI-3** ("Plan 8"): a heavily process-gated starter kit. "The E0 public score of 0.08 is a pipeline-validation baseline, not a competitiveness claim" — [GitHub README](https://github.com/dcw06/ARC-AGI-3).
- **Panus15/arc-prize-2026** (Thai-language): an ARC-AGI-3 agent with 246 passing tests, validated only on mocks. "ยังไม่ได้ submit" (not yet submitted). Its mock study found noise "destroys only learning methods" — [GitHub README](https://github.com/Panus15/arc-prize-2026).
- **arodmor/arc-agi-3**: an explainer only ("Round 1 — public explainer"). Its roadmap is an object-centric JEPA world model. No agent code or score — [GitHub README](https://github.com/arodmor/arc-agi-3).
- **Jason Feng**: open-sourced "Sandwich," "Gorilla" (with a LoRA adapter and RPS training dataset), and CoTRD (Chain-of-Thought Reinforcement Decoding). The CoTRD / CoTRD Enhanced notebooks show public scores of 2.78 / 3.16 — [discussion 732823](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732823); [CoTRD repo](https://github.com/iamjasonfeng/CoTRD); Kaggle kernel list ([CoTRD Enhanced](https://www.kaggle.com/code/iamjasonfeng/cotrd-enhanced)).
- **Community leaderboard** (public 25, not Kaggle-constrained): Polyphony Agent (Qwen3.6 self-hosted) 19.8, cost $115 — [criticaldata/avo-qwen-arcagi3 docs/results.md](https://github.com/criticaldata/avo-qwen-arcagi3); [ARC-AGI Community Leaderboard](https://arcprize.org/leaderboard/community).
- **NVIDIA AVO** (Claude Opus 5, self-reported 100 RHAE on the public 25 using 6,624 actions): text-only 64×64 grids, persistent memory, and a supervisor monitor for stagnation — [NVIDIA blog](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/).

### Inferences
- Rank-8 team member Zhongwei Wang likely owns the Wang-Zhongwei/duck-harness fork. This is inferred from the matching name only.
- Ideas from frontier harnesses (retrodiction, plan queues with expectations, executable world models) have not visibly transferred to Kaggle's 27B/6B-active budget. rfbr: "AVO style ideas… haven't… beat our current harness."

### Gaps
- No verified LB scores exist for the GitHub-only agents (criticaldata, Panus15, arodmor).
- I did not inspect the Sahasawatt/arc-agi-3-agent (Thuitanium) repo directly. Its details come from tantan0327's SOLUTION.md.

---

## Q5. The official ARC Prize GPT-OSS-120B template agent: how it works and what it scores

### Takeaway
The official GPT-OSS-120B notebook (Greg Kamradt, 2026-06-17) is a minimal JSON-action template. It sends the raw grid as text, keeps 2 messages of history, uses guided JSON over the legal actions, and caps each game at 50 actions and 20 minutes. No public LB score is attached to it. Its main role was as the scaffold that Reki's and forge's Gemma agents were built from.

### Cited Findings
- Setup: `vllm==0.19.1`; model `/kaggle/input/models/danielhanchen/gpt-oss-120b`.
- vLLM: `--tool-call-parser openai --max-num-seqs 12 --max-model-len 64000 --kv-cache-dtype fp8 --enforce-eager` (TP 1).
- The agent subclasses the framework's `LLM` agent and runs via `python main.py --agent myagent` (Swarm). In rerun mode the gateway is `http://gateway:8001`.
- Source: [notebook](https://www.kaggle.com/code/gregkamradt/arc-agi-3-gpt-oss-120b).
- Agent limits: `MAX_ACTIONS = 50`, `MESSAGE_LIMIT = 2`, `ACTION_RETRY_LIMIT = 1`, `ACTION_MAX_TOKENS = 8192`, `LLM_REQUEST_TIMEOUT_S = 120`, `GAME_TIME_LIMIT_S = 20 min`, `FIRST_ACTION_DEADLINE_S = 14 min`.
- `DO_OBSERVATION = False`: an optional extra free-form observation call is off.
- Source: [notebook](https://www.kaggle.com/code/gregkamradt/arc-agi-3-gpt-oss-120b).
- Prompt: the state prompt is `# RESULT OF PREVIOUS ACTION / State / Score / # FRAME <pretty-printed grid>`. The user prompt says: "You are playing an ARC-AGI-3 dynamic game. Your objective is to WIN and avoid GAME_OVER while minimizing the number of actions… ACTION6 is a click action and should include integer x and y coordinates from 0 to 63… Return only one JSON object."
- The action is chosen through `extra_body={"guided_json": schema}` over the available actions. The first action is a RESET.
- Source: [notebook](https://www.kaggle.com/code/gregkamradt/arc-agi-3-gpt-oss-120b).
- Score: the notebook's Kaggle listing has no best public score, and I found no LB number for it in the discussions.
  - The only other official templates with scores are "Stochastic Goose" (0.25), "Random Agent" (0.18) and "Just Explore" (0.19) — [Stochastic Goose sample](https://www.kaggle.com/code/inversion/arc3-sample-submission-stochastic-goose); [Random Agent sample](https://www.kaggle.com/code/inversion/arc3-sample-submission-random-agent).
  - Community "LB-9 arc3 duck v16/v18 with GPT-OSS 120B" notebooks exist without scores.
- Reki and forge are both "built on the official ARC Prize GPT-OSS-120B template" with Gemma-4-31B swapped in — [ARC Prize blog](https://arcprize.org/blog/arc-prize-2026-milestone-1).
- Fususu: GPT-OSS 120B/20B can play only with a symbolic "system decoder," and "tend[s] to fail by taking overly roundabout approaches" — [discussion 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).

### Inferences
- A 50-action cap and 20 min/game with no images, raw 64×64 numeric text and 2-message memory probably leave the template near random-agent level (~0.2). Its value is as infrastructure: offline vLLM on the RTX 6000, gateway handling, and the first-action deadline.

### Gaps
- There is no published LB score for the GPT-OSS-120B template itself. The score is inferred, not measured.

---

## Q6. Reported failure modes: timeouts, context overflow, click-space explosion, and local public-game scores not predicting the LB

### Takeaway
Wall-clock is the binding constraint: every Duck-lineage game ends on the timer, not on actions or a win.

Recurring failures:
- context bloat (full-board dumps, long contexts that collapse throughput);
- memory loss (hidden reasoning never written to notes);
- dead-click waste (every no-op click is counted);
- hypothesis fixation;
- HUD/timer confusion;
- infrastructure errors.

Local public-25 scores are a poor LB predictor. Public games are easier by design, and single-draw variance is ±50% or more. Several teams report negative correlation between local gains and LB.

### Cited Findings

**Timeouts and wall-clock binding**
- "Every run in both arms hits the 132-minute wallclock cap. Nothing ends because of an action limit and nothing ends in a win." "Tokens are the real currency, not actions" — [TAAF Anim write-up 734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369).
- "Every long run dies on the wall clock… Per-request latency (median 4–5 min at 7 lanes on a108) is the binding constraint" — [sonpham-org/arc-3 HARNESS-NOTES.md](https://github.com/sonpham-org/arc-3).
- Qwen3.8 27B reasoning averaged ~5,380 characters per block, and 88.5% contained "wait/hmm/actually." Every game ended `gave_up` on the per-game clock — [sonpham-org compact-reasoning experiment](https://github.com/sonpham-org/arc-3).
- A sandbox timeout killed "our single most informative tool call" (30 s Python limit) — [734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369).
- Infra: submissions were capped at 6 h until a May fix — [699208](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699208).
- A 14–15 min first-action deadline applies — [GPT-OSS template](https://www.kaggle.com/code/gregkamradt/arc-agi-3-gpt-oss-120b).
- About a third of failed submissions "just get stuck" with no visible error, and ~20% forgot to enable the GPU — [Greg Kamradt, 500 submissions analyzed 727119](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/727119).
- RTX Pro 6000 queues reached 8–12 h in Sep 2026 before capacity was restored — [discussion 742148](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742148).
- Identical notebooks have scored 0.93 and then 0.00 — [738762](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738762). For forge, 0.86 and then 0.00 ("infra/timeout failure") — [725002](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/725002).

**Context overflow and memory**
- Duck: "A common failure mode of the agent is that it tries to print the whole grid directly, which pollutes its context." FIFO eviction keeps ~32k tokens — [Tufa write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).
- Raising context to 64k dropped throughput from 283 to 195 tok/s and the score to 1.20. bp35 "burned 28k tokens producing zero actions." Decode at 32k context is ~30 tok/s vs ~283 at 4k — [743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060).
- The world-model note is lost when models reason in hidden thinking: 66.8% of Qwen tool-call responses had no visible content — [734843](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734843). The note was empty for entire games under Flash-Next — [tantan0327 SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent).
- Free-form summaries "can preserve an incorrect theory for a very long time" — [Rakha, 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).
- The MLST episode highlights "long-context consistency across hundreds of thousands of tokens" and "locking onto wrong hypotheses" as the key bottlenecks — [daily.dev summary of MLST episode](https://daily.dev/posts/the-benchmark-with-no-instructions-tufa-labs-arc-agi-3--nagrqjc2f).

**Click-space explosion and no-op waste**
- Dead ACTION6 clicks are counted in both the RHAE denominator and the budget (lp85: 100 dead clicks = 100 actions) — [718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638).
- Duck's prompt: "A common failure mode is to mistake a segmented edge bar for clickable puzzle pieces… DON'T DO THIS!" — [duck-harness prompts.py](https://github.com/Tufalabs/duck-harness).
- Mitigations:
  - Reki's saliency click plus dead-signature suppression — [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution).
  - gedouluhui's component-centroid click candidates — [743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060).
  - Jakob's hard no-op guard (a claimed 12–20% action reduction, which he later discounted because runs are time-bound) — [734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369).
- An unseeded Thompson-sampling agent choosing random ACTION6 coordinates scored 0.20 vs 0.03 on identical code — [726552](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/726552).

**Local public-25 scores vs LB**
- Greg Kamradt: "Public Demo was made to be easier than semi private… Going from 1.56 > 0.05 is inline with expectations" — [703990](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990).
- Reported local → LB pairs:
  - 22.26 → 5.37; 17.34 → 6.91 / 5.19 (Fususu).
  - 15.7 → 7.37 (Giang Rita).
  - 9.91 → 6.23 (Ya Xu).
  - 11.04 → 2.71 (Scott Le Grand).
  - 7.6/10.2/7.7 → 3.35/3.05/4.42. Pellegrin: "doing better on the public set… correlates to weaker private scores."
  - 5.0–5.4 → 1.4 (Pellegrin's own harness) vs Duck 2.1 → 1.4.
  - 6.8 → 1.19 (daoviet).
  - 2.8 → 2.4 (mikelou1).
  - Sources: [732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854); [736578](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/736578).
- Scott Le Grand's theory: giving more time to games that reach L2+ lifted his public score from 7.6 to ~13 but was a "slight digression" on hidden games. His reasoning: below ~3.5 LB "you're mostly not solving any level 2 or up of the hidden games" — [740812](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740812).
- Variance:
  - Tufa: 0.7–1.3 on the same notebook — [716696](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716696).
  - A 2.3× spread over 11 submissions (0.55–1.29) — [731522](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/731522).
  - Public forks: "Same code can bring you from 2.5-5.5" — [737617](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/737617).
  - Two identical passes over the public 25 scored 2.85 vs 4.75 — [739801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739801).
- Suspected sources of variance: continuous batching changing trajectories ("Parallelism… can effectively change the policy trajectory") — [739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938). Environments use "stable seeds" per game (Greg), except lf52's noise animation — [738762](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738762).
- Chollet reminder (via screenshot in the thread): the public 25 are a "demonstration set," not a training or eval set — [739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047). The hidden set is designed to be harder, out-of-distribution and more compositional — [sonpham-org docs/how-this-feeds-kaggle.md](https://github.com/sonpham-org/arc-3).

**Behavioral failure modes**
- Hypothesis fixation: "once [the world model] is wrong, no amount of in-run recovery helps within the time budget" — [743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060).
- Treating the energy bar as the goal; inventing goals like "move to a fixed position"; hallucinating robots/Atari sprites — [Tufa write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133).
- ACTION7 hallucinated as "jump" in bp35 — [742477](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742477).

### Inferences
- Local public-25 numbers should be treated only as a smoke test and a throughput/behavior proxy (tokens/action, actions/hour, level-1 clear rate). Tuning public-set depth (L2+) can hurt the hidden score, where level-1 clears on unseen mechanics dominate.
- Because the score is a single play per game and the LB is a max over draws, a harness change must beat roughly a ±1.5-point noise floor (on 25 games × 1 pass) to count as confirmed.

### Gaps
- There is no host confirmation that the 55 public-LB games are fixed across submissions, or that environment seeds are identical run to run ([738762](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738762) is still open).
- There is no official breakdown of submission failures by cause beyond Greg's 500-submission summary.

---

## Q7. Synthesis: what separates the ~19% entries from the ~4% public forks, i.e. what appears to beat the current Kaggle SOTA

### Takeaway
Nobody in the top 5 has disclosed a method, so the evidence is circumstantial. It points to four levers:
1. the strongest base checkpoint that fits in 96 GB, currently Qwen3.8-Flash-Next NVFP4 (125B-A6B) rather than 27B dense;
2. throughput engineering that maximizes decisions per 132-min game slot;
3. training the model on its own successful trajectories, likely on synthetic, out-of-distribution games rather than the public 25;
4. fixing the Duck's known information leaks (hidden-reasoning memory, discarded animation frames, no-op/dead-click waste, ACTION7 labeling) while keeping the harness lightweight.

Prompt-engineering and multi-agent elaborations have not shown hidden-set gains.

### Cited Findings
- Model steps drove the LB: Qwen 3.6 → 3.8 27B gave a ~2× local score, and Flash-Next clears games the 27B never clears — [735243](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735243); [sonpham-org HARNESS-NOTES.md](https://github.com/sonpham-org/arc-3).
- Tufa: "the solvability of a game being dependent on model capability, while the cost is mostly dictated by the harness" — [Tufa blog](https://tufalabs.ai/research/duck-harness/).
- Throughput evidence:
  - MTP-off plus a bigger KV cache halves the queue and gives more model calls and levels — [tantan0327 SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent).
  - A newer vLLM with MTP was the only one of 14 modifications that beat its baseline — same source.
  - Compact reasoning gave +43% actions per clock — [sonpham-org compact-reasoning experiment](https://github.com/sonpham-org/arc-3).
- Self-trajectory fine-tuning evidence: STaR LoRA took LB 1.25 → 1.94 on Qwen3.6 — [739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047). Son Pham/Mark Barney's pipeline is synthetic games → Duck plays → keep solved levels → SFT — [sonpham-org docs/how-this-feeds-kaggle.md](https://github.com/sonpham-org/arc-3).
- Scott Le Grand: "I am beginning to think the only path forward is a winning recipe for SFT/RL on an existing model" — [732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).
- Scoring economics: one cracked level is worth ~2–5 points per game (level 1 of a 6-level game ≤4.76; of a 9-level game ≤2.22). Cracked levels already score ~90–100 per level; "the gap to the leaderboard top is concentrated entirely in games where no level is cracked at all" — [743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060).
- Depth weighting: later levels carry more weight, and an unfinished game is capped at its completed weight fraction — [728299](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/728299).
- Frontier harness ceiling: Astra went from 62.7% (standard) to 99.9% (provider adapter that "preserves opaque reasoning state between requests and uses compaction") — [ARC Prize Astra blog](https://arcprize.org/blog/astra). The analogous open-weight gap is the Duck discarding hidden reasoning from its memory note ([734843](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734843)).

### Inferences
- A ~19% hidden-set score means clearing level 1 or more in a large fraction of the 55 semi-private games at near-human efficiency: at ~2–5 points per first level, roughly 20–40 games with some progress. This needs a better "opening hypothesis" on novel mechanics. That favors model capability plus training on diverse synthetic mechanics over more public-set tuning.
- Given Astra's standard vs adapter gap, preserving reasoning state across turns (instead of FIFO-evicting it and losing hidden-thinking notes) plausibly transfers to Kaggle. It is cheap to try: backfill notes, keep `preserve_thinking`, and compact rather than evict.
- Because the final ranking uses the private 55 and only two chosen submissions, robust (low-variance) configurations and per-request deterministic seeding may matter as much as mean score for final placement.

### Gaps
- There are no disclosures from Lord Han Solo, Tufa (post-July), Yi-Chia Chen, Daniel Franzen or NVARC3. Tufa and NVIDIA promise releases only after the competition ends (2026-11-02). Any claim about what the top 5 do is inference.
- There is no direct measurement of how much of the top-team gap is fine-tuning vs throughput vs harness.
