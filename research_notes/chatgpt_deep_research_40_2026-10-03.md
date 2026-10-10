# Raising an ARC-AGI-3 hidden score from approximately 27 to 40+

Research cutoff: October 3, 2026. Target submission deadline: November 2, 2026. Scores and gains below use the 0–100 scale.

## Executive summary — 10 lines

1. **Inference:** 40+ is a credible stretch target, but improving goal revision and action efficiency is more promising than adding streams.
2. **Calculation:** Your two hidden results average 26.83; reaching 40 requires approximately +13.2 points.
3. I found no verified Aug–Oct replacement combining better relevant performance, one 96 GB GPU, a ≥1M-token shared cache, and demonstrated SM120 serving.
4. **Inference:** Keep Qwen3.8-Flash-Next as the main actor and spend the first week on evidence retention, cache reuse, and failure classification.
5. Tufa publicly described generated-game RL and reward shaping in its July 1 [MLST interview](https://app.rescript.info/api/public/sessions/23f8cebdc5ce8f5f/pdf); its current winning method remains undisclosed.
6. Public simulator results are substantial, but predominantly use frontier models, large budgets, or development followed by replay; they do not establish your hidden-game gain.
7. **Inference:** Use optional partial simulators with checked predictions; requiring a complete simulator before every action is too risky.
8. [Axolotl’s Flash-Next examples](https://docs.axolotl.ai/docs/models/qwen3.8-flash-next.html), checked October 3, require approximately 110–120 GiB even with offload; full-model LoRA is a poor deadline bet.
9. **Inference:** Use paired public-game experiments and reserve hidden submissions for a few frozen finalists; one noisy 25-game win is insufficient.
10. **Inference:** My subjective probabilities for reproducibly reaching 30 / 35 / 40 hidden are approximately 80% / 45% / 20%, conditional on the plan and a comparable hidden distribution.

**Evidence convention.** “Reported” means a primary author’s result, not an independent replication. Your notebook configuration, hidden draws, ablations, and sirikilohit numbers are accepted as user-supplied facts where their full underlying write-ups could not be retrieved. “Inference” marks forecasts, transfers between models, and proposed implementation choices. No result published after October 3 is assumed.

## 1. What are the leaders likely doing?

### What is public

| Source and date | Recoverable evidence | What it does not establish |
|---|---|---|
| Tufa’s [Duck blog](https://tufalabs.ai/research/duck-harness/), July 1, 2026, and [repository](https://github.com/Tufalabs/duck-harness), checked October 3 | Minimal Python REPL; observations in Python variables; images plus text; automatic eviction; Qwen3.6-27B-FP8. Public evaluation used 25 games × 20 attempts. | The architecture or weights behind the current approximately 52.5 score. |
| [Kaggle discussion 717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133), linked by Tufa July 1 | This is Tufa’s original technical write-up. The [June milestone notebook](https://www.kaggle.com/code/jeroencottaar/tufa-labs-duck-harness-june-30-milestone-winner) is public. | The discussion’s full current body was not retrievable. Its URL is verified; I cannot claim to have audited all edits or comments. |
| MLST technical episode, [publisher’s X link](https://x.com/MLStreetTalk/status/2072326433922297975), linked July 1 | Tufa’s blog identifies this as the technical companion episode. | The linked post was blocked; I could not verify additional technical statements from it. |
| MLST broader episode, [YouTube](https://www.youtube.com/watch?v=Vg6FBKTlfOw), [Spotify](https://open.spotify.com/episode/7hVLVJYN4ABeekPUgyzCi7), and [publisher-associated transcript](https://app.rescript.info/api/public/sessions/23f8cebdc5ce8f5f/pdf), July 1 | Direct statements from Cottaar, Smit, Crouzier, and other team members about exploration, reasoning length, training, and wrong-goal loops. | A measured RL ablation or disclosure of the current submitted checkpoint. |
| Jeroen Cottaar, Dries Smit, Benjamin Crouzier X searches; checked October 3 | Older release/promotion material surfaced. [Smit’s own site](https://driessmit.github.io/) links the milestone and earlier preview work. | I recovered no verified current-method disclosure from their personal X posts. This is an access/indexing limitation, not evidence that none exists. |
| Yi-Chia Chen’s [Kaggle profile](https://www.kaggle.com/threerabbits) and [discussion history](https://www.kaggle.com/threerabbits/discussion), checked October 3 | The competitor is associated with threerabbits. | No reproducible current ARC-AGI-3 method found. Several researchers share this name; their unrelated papers must not be attributed to this competitor. |

The most informative additional evidence is the **July interview at 54:54–56:47**. Smit describes generating additional games, end-to-end RL, reward shaping, shorter training sequences, and rewards involving level progress, RHAE, code execution, and reasoning length. At 53:28, Viel describes agents becoming trapped after incorrect goal hypotheses. At 02:42, Cottaar gives a concrete failure: the agent reaches an apparent exit but refuses the extra outward move needed to finish. These are direct statements about their research, not proof of their current leaderboard recipe. ([MLST transcript, July 1, 2026](https://app.rescript.info/api/public/sessions/23f8cebdc5ce8f5f/pdf).)

**Inference — medium confidence:** Tufa’s current advantage may include trained weights, synthetic environments, and shorter, better-directed reasoning, alongside serving and harness improvements. The interview makes training substantially more plausible than an explanation involving only prompt tweaks. There is insufficient evidence to assign the approximately 25-point gap to any one component.

**Inference — lower confidence:** Better experiment infrastructure and repeated evaluation probably contribute. Your reported 153 submissions show iteration volume, but do not reveal training compute, techniques, or how much of the displayed best score reflects selection under noise. I cannot infer Chen’s method beyond the same broad possibilities.

### Releases above 30 since September 30

The search-indexed [CLIST leaderboard mirror](https://clist.by/standings/arc-prize-2026-arc-agi-3-general-knowledge-and-reasoning-artificial-intelligence-custom-metric-66453356/), accessed October 3, surfaced Tufa 52.51, Chen 48.07, lalalia 35.79, gng 34.77, and markintell 34.21. **This is a secondary snapshot:** direct retrieval returned an older table, and primary Kaggle indexing also returned stale scores.

I could not verify a publicly reproducible **30+ notebook or method write-up published September 30–October 3**. I found leaderboard entries above 30, not their recipes. Franzen’s [Milestone-2 notebook](https://www.kaggle.com/code/dfranzen/arc-agi-3-milestone-2-solution) and [sirikilohit’s notebook](https://www.kaggle.com/code/sirikilohit/arc-agi-3-duck-18-1gc-submit) are relevant releases, but their supplied scores, 27.89 and 22.53, are below that threshold. This search cannot certify that no newer release exists.

**Recommendation — inference:** Borrow published mechanisms, not presumed leader secrets. Allocate at most one hour every few days to checking new releases; do not hold the month’s plan hostage to an unpublished solution.

## 2. Model choice on one 96 GB GPU, offline

**Finding:** I found no verified new model satisfying all four requirements: stronger relevant performance than Flash-Next, practical single-card memory, a ≥1M-token shared cache, and measured RTX PRO 6000 serving. “No verified candidate found” is narrower than “no such candidate exists.”

| Model / exact Hugging Face IDs | Release or source date | Quantization and memory evidence | Serving and measured RTX PRO 6000 evidence | Decision — inference |
|---|---|---|---|---|
| [Qwen/Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next); [Intel/Qwen3.8-Flash-Next-W4A16-AutoRound](https://huggingface.co/Intel/Qwen3.8-Flash-Next-W4A16-AutoRound); [Saren/Qwen3.8-Flash-Next-W4A16-AutoRound-hybrid-MTP_int4RTN](https://huggingface.co/Saren/Qwen3.8-Flash-Next-W4A16-AutoRound-hybrid-MTP_int4RTN) | Base August 26, 2026; quant cards checked October 3 | Intel W4A16 target, INT4 MTP variant. The hybrid card reports checkpoint footprint 71.4 → 67.9 GiB. Your run demonstrates feasibility with its existing pool. | SGLang/Pennyroyal supports your working route. No independently verified tokens/s measurement found for this exact quant plus 10-stream ARC workload. The hybrid-card speed tests use DGX Spark, not SM120. | Keep as the reference. |
| [RadixArk/Qwen3.8-Flash-Next-NVFP4](https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4) | August 2026; Pennyroyal measurements September 2026 | NVFP4 routed experts; CPU/RAM-backed PLE; optional online FP8 dense paths. Pennyroyal qualifies a 1,000,000-token pool on one 96 GB card. | Single-card SM120 SGLang measurements: approximately 207 output tok/s for a warmed single stream; see §3 for concurrency and context. | A serving/quantization experiment, not a smarter model. |
| [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), [Qwen/Qwen3.8-27B-FP8](https://huggingface.co/Qwen/Qwen3.8-27B-FP8); draft [incoai/Qwen3.8-27B-DFlash2](https://huggingface.co/incoai/Qwen3.8-27B-DFlash2) | August 2026 | FP8 target with FP8 target/draft KV. Pennyroyal’s related profile qualifies a 1,118,784-token pool. | Measured 108.3 tok/s single-stream and approximately 375 aggregate tok/s at concurrency four, **using orcarouter/Qwen3.8-27B-Uncensored-FP8**, not the official target. vLLM and SGLang support exist. | A training/diagnostic sibling; no evidence it beats the current actor. |
| [apodex/Apodex-1.1-mini](https://huggingface.co/apodex/Apodex-1.1-mini), [FP8](https://huggingface.co/apodex/Apodex-1.1-mini-FP8), [GPTQ-Int4](https://huggingface.co/apodex/Apodex-1.1-mini-GPTQ-Int4) | August 24, 2026 | Qwen3.5-35B-A3B-derived model; official quantizations. **Inference:** likely memory-feasible with a large aggregate cache, but no exact qualified ≥1M SM120 configuration found. | Author supports SGLang/vLLM; no relevant RTX throughput or ARC result found. Strong professional-work results are not a matched Flash-Next coding comparison. | One short test only if the main plan stalls. |
| [zai-org/GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) | August 2026 | 320B total, 18B active. **Calculation:** raw four-bit weights alone are approximately 160 GB; two-bit approximately 80 GB before overhead. | Official SGLang/vLLM support. No verified one-card ≥1M-cache quantized RTX result found. | Attractive capability claim; unqualified deployment for this deadline. |
| [deepseek-ai/DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) | September 2026 | Official vLLM recipe lists 552B total, 8–16B active. **Calculation:** four-bit weights alone approximately 276 GB. | Official recipe requires architecture-supporting nightly images; no matching RTX single-card result found. | Reject for this constrained deployment. |
| [rmonsurate/Victoria](https://huggingface.co/rmonsurate/Victoria) | September 30 release announcement; card checked October 3 | Pruned Flash-Next, 512 → 288 experts. NVFP4 resident weights 48 GiB plus a 95.4 GiB lookup table in its documented vLLM GPU configuration. GGUF uses approximately 49.17 GiB weights with separate table handling. | Card reports 279.6 tok/s on **B300**, not RTX, and a different runtime/build. Reported coding quality is below its original model. | Extra headroom does not establish a better actor; skip. |

Sources for the measured profiles: [Pennyroyal RESULTS](https://github.com/jpezzulli/sglang-rtxpro6000/blob/pennyroyal-main-sm120-final/RESULTS.md), September measurements, and [BUILD](https://github.com/jpezzulli/sglang-rtxpro6000/blob/pennyroyal-main-sm120-final/BUILD.md)/[RUN](https://github.com/jpezzulli/sglang-rtxpro6000/blob/pennyroyal-main-sm120-final/RUN.md), checked October 3. These are developer measurements, not ARC quality ablations. DeepSeek architecture/deployment details: [official vLLM recipe](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4.1-Flash.yaml), September 2026.

Flash-Next’s own [model card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next), August 26 release, reports DeepSWE 1.1 **58.7 versus 42.2** for 27B and SWE-bench Pro **62.5 versus 61.7**. These are vendor harness measurements, not evidence of a corresponding ARC difference. Its 125B main model, additional 51B n-gram table, and 6B active parameters explain why “6B active” is not a six-billion-parameter training or storage budget.

**Important distinction:** A 1M shared cache is not ten independent 128k contexts. Ten fully occupied contexts require 1.28M token positions before state and runtime overhead. Sparse attention reduces attention computation; it does not make all stored history free. Pennyroyal separately budgets recurrent/Mamba states.

**Recommendation — inference:** Keep the present model and 128k context initially. Audit whether historical reasoning actually survives the client/parser round trip. Flash-Next defaults to preserved thinking, but a client that discards reasoning content can defeat that setting. Do not extrapolate model-card “supported by vLLM” into a proven one-card recipe: an August 27 [firsthand deployment report](https://blog.kubesimplify.com/running-qwen3-8-flash-next-on-dgx-spark-and-rtx-pro-6000) allocated single-card NVFP4 memory but never obtained a ready server.

## 3. Throughput levers for this exact stack

### What has actually been measured

Pennyroyal’s September tests use **RadixArk NVFP4, not your Intel W4A16 target**. They establish plausible levers, not an automatic gain on your notebook.

| Lever | Same-hardware reported measurement | Practical limitation |
|---|---|---|
| Online FP8 dense paths | Short-context C1 decode: 161.5 → 207.1 tok/s, +28.3%; whole-request: 153.1 → 187.8, +22.7%. At 128k/C4 aggregate decode: 367.1 → 422.0, +15.0%. | Long cold-prefill measurements improve much less end to end. |
| FR-Spec reduced draft vocabulary | C1: 156.8 → 171.9 tok/s, +9.7%; C4: 417.9 → 447.0 aggregate tok/s, +7.0%, using one reported control per comparison. | Different baseline/control runs; not a 10-stream ARC experiment. |
| A 1M shared pool with online FP8 | Qualified with graphs retained; warmed C1 approximately 206.9 tok/s. | Capacity qualification is not evidence of higher game score. |
| 27B/DFlash2 | 108.3 tok/s C1; approximately 375 aggregate C4. | Different target and speculative architecture; not a causal comparison with Flash-Next. |

([Pennyroyal RESULTS](https://github.com/jpezzulli/sglang-rtxpro6000/blob/pennyroyal-main-sm120-final/RESULTS.md), September 5–11, 2026; checked October 3.)

**Speculation.** The qualified Flash-Next recipe uses NEXTN with **steps/top-k/draft capacity = 3/1/4**, plus a **65,536-token FR-Spec map**. The reduced vocabulary applies to the drafter, leaving target vocabulary and acceptance policy unchanged. SGLang documents single and accumulated acceptance thresholds defaulting to **1.0**. ([RUN](https://github.com/jpezzulli/sglang-rtxpro6000/blob/pennyroyal-main-sm120-final/RUN.md); [SGLang speculative-decoding documentation](https://docs.sglang.io/docs/advanced_features/speculative_decoding), checked October 3, 2026.)

**Recommendation — inference:** First test draft depths 1, 2, 3, and 4 with branching one and the matching verification capacities. Use saved ARC reasoning/code prompts at concurrency 10 and 12, including warm histories around 16k, 64k, and 110k. Optimize delivered aggregate output per wall second, not acceptance percentage. Keep thresholds at 1.0; accepting more aggressively is not a demonstrated quality-preserving optimization. A draft-depth win at C1 can disappear at C10.

Your INT4 MTP already captures the draft-memory saving. The [hybrid INT4 card](https://huggingface.co/Saren/Qwen3.8-Flash-Next-W4A16-AutoRound-hybrid-MTP_int4RTN), checked October 3, reports only modest speed changes on DGX Spark. Do not claim these as new RTX gains.

**Dense FP8.** Pennyroyal exposes **SGLANG_SM120_ONLINE_MXFP8=true** for its supported profile. This is quantization of selected formerly BF16 projections, not a switch that makes the whole model FP8. It changes numerical precision and uses shape-specific SM120 kernels. ([FP8 notes](https://github.com/jpezzulli/sglang-rtxpro6000/blob/pennyroyal-main-sm120-final/FP8.md), checked October 3.)

**Recommendation — inference:** Spend a two-hour compatibility/performance budget on the exact Intel checkpoint. If the supported path is unavailable, the measured alternative requires changing the target quantization to RadixArk NVFP4. Treat that as a separate quality experiment, not a harmless flag. Stop if it requires substantial kernel work.

**KV and recurrent state.** The reference Flash profile uses four running requests and 24 Mamba slots; its optional six-request profile uses 36 slots. RAM-backed PLE occupies approximately **47.68 GiB host memory**, in addition to its **32 GB HiCache** setting and other runtime allocations. ([RUN](https://github.com/jpezzulli/sglang-rtxpro6000/blob/pennyroyal-main-sm120-final/RUN.md), checked October 3.)

**Recommendation — inference:** Record actual profiled token capacity, recurrent-slot admission, cache evictions, host memory, and minimum free VRAM. A larger KV pool cannot fix insufficient recurrent-state slots. Do not copy the desktop’s host-cache defaults without checking Kaggle RAM. Your safe 12-stream test is useful evidence, but shows that additional admission capacity is not currently a demonstrated score lever.

**CUDA graphs.** Published fast profiles retain graphs. Their capture memory competes with KV and recurrent states; no isolated ARC graph-on/off gain was found.

**Recommendation — inference:** Keep the working graph configuration. Measure actual batch shapes during ten-stream play before adding captures for 10/12 requests. Account for cold loading, graph capture, compilation, and media processing in the nine-hour budget. Do not enlarge every graph bucket merely because VRAM remains.

**Prefix caching.** SGLang’s [HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design), checked October 3, describes GPU/host/storage cache tiers. Cache reuse depends on matching prefixes; hybrid models also need coherent recurrent state. Flash-Next’s [card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) explicitly links preserved thinking with cache utilization.

**Recommendation — inference:** Inspect how solved-level memory is inserted. Rewriting an early system message after every update can invalidate reuse of the later history. Keep the base system message stable; append evidence records, and compact at deliberate boundaries. Compare cached-token fraction and prefill time before changing the weakly positive memory behavior. Perform any compaction experiment separately, since shorter context can lose useful evidence.

Finally, [Pennyroyal v2.5.3](https://github.com/jpezzulli/sglang-rtxpro6000/releases/tag/pennyroyal-v2.5.3), September 28, fixes an accepted-token-boundary recurrent-state bug associated with phantom tokens and file-writing failures. **You already report this version, so upgrading to it is not a new gain.** Verify that the packaged source contains the fix; a version label alone is weaker than a pinned source/build.

## 4. Executable world models and small offline models

### The evidence, separated by evaluation regime

| Work and date | Author-reported numbers / mechanism | Relevance to your constraint |
|---|---|---|
| [Twin, arXiv 2608.14490](https://arxiv.org/html/2608.14490v1), August 14, 2026 | GPT-5.6 Sol: 93.3 public RHAE versus 61.1 without Twin; 179/183 levels. Approximately 2.60B processed tokens and 91.4 hours over 25 games; over 98% of processed tokens were cached reads. | Strong simulator evidence, but no small-open-model ablation or hidden Kaggle result. Processed tokens are not generated tokens. |
| [Kepler, arXiv 2610.00834](https://arxiv.org/html/2610.00834v1), submitted September 30, 2026 | Opus 5 final replay: 100 public RHAE; approximately 858M processed tokens, 97.37% cached, approximately $778 list-equivalent cost. | Programs were developed against the public games before final replay. The headline is not a first-exposure hidden-game result. |
| [Prime Agent, arXiv 2608.23552](https://arxiv.org/html/2608.23552v1), August 24, 2026; [author blog](https://www.primeintellect.ai/blog/prime-agent) | Opus 5 around 95.5 public RHAE; persistent REPL, programmatic context, learned harness/skills/memory. | Learning the harness is not necessarily weight fine-tuning. No comparable ≤30B-active open-model result found. |
| [Executable World Models, arXiv 2605.05138 v2](https://arxiv.org/html/2605.05138v2), June 6 revision | GPT-5.5 high: 58.12; GPT-5.4 high: 41.29 public RHAE. | Earlier, lower-capability versions should not be confused with later results. Still frontier-model evidence. |
| [EWM component ablation, arXiv 2607.15439 v2](https://arxiv.org/html/2607.15439v2), August 27 revision | Verification ranks first across the main four model/effort settings, costing 1.82–3.26× the accounted tokens. GPT-5.5 xhigh: textual 72.51, verification 74.78. | Merely requiring executable code is not consistently beneficial. Verification’s cost matters under your limit. |
| [Agno “Learning Machines”](https://www.agno.com/articles/learning-machines), August 30, 2026 | Seeded learning-store results include GLM-5.2 7.92 → 83.46 and Gemini 3.7 Flash 37.33 → 96.42 on public games. | Warm, task-informed memory; not evidence for a cold hidden-game small model or LoRA. |
| [AERA, arXiv 2605.25931](https://arxiv.org/html/2605.25931v1), May 2026 | Claims approximately 21.16 public RHAE using Qwen2.5-0.5B. | [Tycho](https://arxiv.org/html/2607.28287v1), July 2026, reports that its released evaluator conflates WIN, GAME_OVER, and None returns. Treat the headline as disputed, not verified small-model evidence. |
| arc3cb, searched October 3 | No identifiable primary repository, paper, or result recovered under this exact name. | I cannot attach a method or score to an unresolved reference. |

Kepler also documents reconstruction and validation caveats: the commit boundary is not uniformly a strict complete-history correctness gate. Do not equate “has a simulator” with “every action follows a verified simulator.” ([Kepler, September 30, 2026](https://arxiv.org/html/2610.00834v1).)

**Is there ANY ≤30B-active open-model evidence? Yes, in adjacent benchmarks.** [PatchWorld v4](https://arxiv.org/html/2605.30880v4), July 28, 2026, induces executable models with **DeepSeek-V4-Flash, 13B active**, and **MiMo-V2.5, 15B active**. Both reach approximately **0.70 next-observation token F1** across seven AgentGym environments. However, their total models are approximately 284B and 310B: this is not a demonstrated one-96-GB configuration. The main planning comparison uses Qwen3-Coder-480B-A35B, which exceeds the requested active-size limit.

PatchWorld also exposes an important distinction: a fine-tuned Qwen3.5-4B neural predictor has **0.85 F1** but **63.5% planning success**, whereas the simpler executable model achieves **76.4%** under a larger-model planner. Better prediction metrics do not automatically yield better decisions. ([PatchWorld v4, July 28](https://arxiv.org/html/2605.30880v4); [DeepSeek card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash); [MiMo card](https://huggingface.co/XiaomiMiMo/MiMo-V2.5), checked October 3.)

**Finding:** There is genuine open-weight evidence for useful program induction at small *active* size, but I found no clean demonstration that your resource-compatible actor gains hidden ARC points by building full simulators.

### Minimal version worth testing inside Duck

**Proposed design — inference; all budgets and thresholds here are starting values, not measured optima.**

1. **Keep an immutable transition record outside the prose history.** Save level, initial/current observations, all animation frames, action, returned status, and level count. Preserve the evidence even when text is compacted.
2. **Offer a small model interface.** The agent may define initialization, step/predict, render, and optional outcome functions. A prediction can abstain on unknown cells. Report both correctness and coverage; an empty mask or a background-only prediction is not a verified model of the relevant mechanics.
3. **Replay recorded transitions automatically.** Give the agent the first few concrete counterexamples: action, affected region, expected versus observed values. Validate a proposed repair against the wider record so one fix cannot silently regress older behavior.
4. **Commit predictions before actions.** Keep the model version and prediction that existed before the outcome. Later fitting should not be reported as successful prospective prediction. Identical visible boards may hide different states, so initialize recurrent belief from history where necessary.
5. **Plan only within demonstrated scope.** Start with depth 4–6, at most 2,000 nodes, and a 0.5–1 second CPU limit. Use valid keys and a bounded set of agent-proposed click locations. Execute short routes and check every returned observation/status before proceeding.
6. **Allow ordinary probes and direct actions.** After at most one or two repair attempts, return control to Duck. Never require a globally correct simulator merely to continue exploring. Initially cap model-writing/repair output at roughly 5–10% of the game’s token allocation.

There is ARC evidence for selective rather than compulsory modeling. Tycho’s matched Opus-4.8 comparison reports **79.07** without a world model, **88.49** with actor-requested delegation, and **83.07** with automatically triggered repairs. The automatic policy produced better transition matches but spent more inference and completed fewer games. This is frontier evidence, not a forecast for Qwen. ([Tycho, July 2026](https://arxiv.org/html/2607.28287v1).)

**Recommendation — inference:** First implement prediction checking for existing agent-written functions. Test planning only after the logs show useful prospective predictions. A verified three-rule movement model can be worthwhile; a long, incomplete recreation of the whole game may consume the run.

## 5. Goal inference and wrong-goal loops

Tufa’s interview supplies direct qualitative evidence of wrong-goal persistence. Twin reports **156/179 cleared-level goals inferred before the first positive reward**. Its goal search uses generic signals: disappearing colors, new colors, a compact burst of changed cells, a large scene change, and a fallback novelty measure. These rank hypotheses; they do not identify the true goal. ([MLST, July 1](https://app.rescript.info/api/public/sessions/23f8cebdc5ce8f5f/pdf); [Twin, August 14](https://arxiv.org/html/2608.14490v1).)

**Proposed methods — inference:**

| Cheap detector | Initial trigger | Response |
|---|---|---|
| Contradicted goal | A proposed terminal predicate is true on an ordinary, ongoing decision state of the current level. | Mark this version contradicted, attach the actual state/status, and require an explicit refinement or alternative. |
| Expected win did not occur | The committed plan/prediction says the goal is reached, but status and level count do not advance. | Separate an incorrect dynamics prediction from an incorrect goal. Consider one bounded confirmation/boundary action if the goal may require activation; otherwise revise it. |
| Repeated ineffective route | The same short state/action pattern recurs twice without a new confirmed mechanic or candidate being tested. | Surface the concrete repeated pattern and its observed outcomes. |
| Extended stall | Approximately 16–24 actions or 8–12k generated tokens since useful new evidence or level progress. | Make one short fresh-context hypothesis-review call using the same Qwen server. Preserve facts, functions, and negative evidence while challenging the current goal. |
| Exhausted hypothesis | Two attempted revisions reproduce the same contradicted objective. | Suspend this game’s main budget; retain a small rescue allocation for one alternative later. |

Twin’s negative-goal check requires care: its argument relies on winning frames being replaced when completion is reported. For your implementation, grade **ordinary ongoing states of the same level**, not a new level’s initial board, GAME_OVER screens, or arbitrary intermediate animation frames. An observed success certifies the preceding state/action transition; it need not reveal a stable picture of the winning board. ([Twin, August 14, 2026](https://arxiv.org/html/2608.14490v1).)

**Inference:** A fresh-context reviewer can reduce commitment to the old narrative. Use a compact evidence packet, approximately 2–4k text tokens plus necessary visual evidence, and a short answer: two different goal candidates, what existing observation contradicts each, and one discriminating probe. Do this on a stall, not every action. It consumes an existing inference stream, not a second loaded model.

**Inference:** Avoid blanket no-op blocking based only on a board hash. Timers, hidden state, or confirmation actions can make visually repeated actions meaningful. A public [Taaf Anim write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369), 2026, reports that its initially attractive 12–20% action reduction was confounded by wall-time limits; blocked actions still cost LLM turns.

**Recommendation — inference:** Begin with factual counterexamples rather than generic advice. Your own evidence that advice hurts makes “rethink the goal” paragraphs a weak bet. A message saying “candidate G7 predicted completion here; actual status remains ongoing” is more constrained and testable.

## 6. Fine-tuning on free Kaggle GPU/TPU

### Direct ARC-AGI-3 evidence

Manas Joshi’s [Kaggle trajectory-LoRA write-up, discussion 739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047), 2026, retrieved October 3, reports **1.25 → 1.94**, an absolute **+0.69**, using Qwen3.6-27B’s own level-completing Duck trajectories. The author explicitly warns about variance, worse results with naively more data, and base-model dependence. Another participant reports LoRA regressions.

Released artifact names are **arc3-sft-trajectories**, **arc3-duck-lora-sft**, and **duck-eval-results**, described as CC0. The practical notes are assistant-token-only loss, flattened tool calls before templating, and preserving the multimodal architecture/processor when merging and serving. This is positive preliminary evidence, not a replicated +0.69 estimate and certainly not justification for multiplying your 27 by the reported relative improvement.

The [naestro-agi3-27b card](https://huggingface.co/star-ga/naestro-agi3-27b), checked October 3, also describes a rank-16 QLoRA ARC-style model. I found no reliable comparable hidden-score gain from it.

### What fits

[Axolotl’s Flash-Next guide](https://docs.axolotl.ai/docs/models/qwen3.8-flash-next.html), checked October 3, documents approximately **120 GiB** for text QLoRA with PLE offload and **110 GiB** for vision/text QLoRA; corresponding non-offload examples require approximately 216/207 GiB. Its NVFP4 MoE-LoRA example is approximately 223 GiB. Some fast LoRA kernels and attention options are unsupported.

**Finding:** The documented Flash-Next training routes do not fit your 96 GB card. More specialized freezing/offloading might change that, but no qualified free-Kaggle recipe was found. Six-billion active parameters do not remove the inactive expert weights from training memory.

**Feasibility assessment — inference:**

| Experiment | Starting size/data budget | Compute and likely value |
|---|---|---|
| Qwen3.8-27B QLoRA | Four-bit base; rank 8–16; 4–8k sequences; batch one with accumulation; assistant-only loss. Pilot 1–5M curated assistant tokens; only scale toward 5–20M if the pilot wins. | Plausibly fits 96 GB with checkpointing. Benchmark training throughput before reserving hours. A sibling improvement is not automatically a gain over Flash-Next. |
| Small procedural-skill student | Approximately 4–9B total model; a narrow task such as action-coordinate extraction, prediction repair, or hypothesis contrast. | Lower training cost, but deployment requires proving that saved main-model work outweighs additional memory/runtime. Do not assume both servers fit beside the current cache. |
| Full Flash-Next adaptation | Requires a new below-96-GB training recipe. | Excessive engineering uncertainty by November 2. |
| TPU training | Requires a working XLA/JAX route for the exact architecture and multimodal processing. | Your 20 TPU-h are not a drop-in substitute for SGLang/CUDA inference or CUDA-oriented QLoRA. No turnkey successful ARC3 recipe found. |

**Data recommendation — inference:** Train the process, not game IDs or winning action strings. Prefer efficient probe construction, coordinate correctness, executable repairs, and explicit corrections after falsification. Include verified recovery examples, not only effortless wins. Generate teacher traces using your existing offline model or properly licensed public data; paid teacher APIs are unnecessary.

Hold out whole games and procedural families, not random turns from the same game. Train a small number of configurations and evaluate them against their own unfine-tuned sibling before considering deployment. The official [April 22 technical report](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf) states that the public demo set is easier and intentionally does not cover the private mechanics.

**Recommendation — inference:** Limit fine-tuning to a **4–6 GPU-hour pilot after the harness changes**, with a strict stop rule. A realistic planning range is roughly **−3 to +2 hidden points**, with zero entirely plausible. I would not allocate the first half of October to it.

## 7. Compute allocation across 110 games

### The score makes later-level progress valuable

The official [scoring documentation](https://docs.arcprize.org/methodology), checked October 3, confirms:

\[
e_k=\min\!\left(1.15,\left(\frac{H_k}{A_k}\right)^2\right),\quad
S_g=100\min\!\left(\frac{c(c+1)}{K(K+1)},
\frac{\sum_{k=1}^{c} k e_k}{K(K+1)/2}\right).
\]

Here K is the total number of levels and c the cleared count. The cap is the **weighted completed fraction**, not c/K. Four of five levels cap the game at **66.7%**. In an eight-level game, clearing one, four, or seven levels caps it at **2.78%, 27.78%, or 77.78%**.

**Calculations:** Before clipping/capping, reducing actions by 10% increases that level’s efficiency term by **23.5%**; reducing them by 20% increases it by **56.3%**. Across 110 equally weighted games, moving one game from 0 to 100 adds **0.91 overall points**. A +13-point improvement requires **14.3 full-game-equivalents**, distributed across completions and efficiency improvements.

The visible leaderboard may average a 55-game half of the 110-game run; in that case one full-game swing on that subset is **1.82 points**. Host-linked public discussion confirms that submissions play all 110, while questions about identical seeds/splits across scored runs remained unanswered in the retrieved material. ([Discussion 738762](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738762), 2026, retrieved October 3.) Distinguish the displayed subset score from a mean over the entire run.

### How much inference is available?

**Idealized calculation from your budget:** Nine hours equals 32,400 GPU wall seconds, or **294.5 seconds per game** if shared equally.

| Sustained whole-job aggregate generation | Generated tokens in nine hours | Average per 110 games |
|---|---:|---:|
| 200 tok/s | 6.48M | 58.9k |
| 400 tok/s | 12.96M | 117.8k |
| 500 tok/s | 16.20M | 147.3k |

These are accounting scenarios, not measured notebook yields. Loading, prefill, CPU tools, idle time, and media reduce the usable budget. Ten streams share one GPU: do not multiply these totals by ten.

**Finding:** I found no reliable token-versus-score curve for Flash-Next on the 110 hidden games under this run limit. Frontier papers’ processed-token totals are not that curve. The EWM ablation shows that more verification can consume 1.82–3.26× tokens for comparatively modest gains in some settings; it does not identify your optimum.

**Scheduler recommendation — inference:** Keep P=(A+B)×C as control. First add a minimum initial allocation and a stall/rescue mechanism; do not replace it with an unvalidated elaborate scheduler.

- Initial proposal: **25%** of generation for an opening allocation across all games, **60%** for continuation where evidence suggests useful progress, **15%** for revisiting uncertain or stalled games.
- Make decisions in roughly **2–4k generated-token blocks**, recording GPU service/prefill cost as well as elapsed game time.
- Prefer expected additional weighted score per GPU second, estimated from public logs, over raw level count or sheer activity.
- Give later levels with reusable verified mechanics a fair continuation budget; deprioritize repeated contradiction loops.
- Resume an existing open game/session. The host says a second make() attempt is invalid in competition mode; returning to the still-open game is allowed. ([Host answer, discussion 693307](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/693307), 2026.)

**Inference:** Estimate empirical curves by truncating unchanged-policy public runs at 25/50/75/100% of token or service budget. Record where levels unlock and where inference is wasted. These curves need not be concave: goal discovery creates jumps. Truncation diagnoses the existing policy; it does not prove the outcome of an adaptive alternative.

## 8. Evaluation under noise

**Recommendation — inference:** Build a staged paired design. Your two hidden draws cannot reliably estimate hidden variance. Your 11-better/7-worse public comparison is encouraging, but a sign count ignores magnitude; its simple two-sided sign-test p-value is approximately **0.48** after dropping ties.

1. **Choose a diagnostic panel from your own baseline logs.** Use 8–10 games covering perception, wrong goals, dynamics, long plans, and later-level transfer. Include approximately two reliably solved controls and two persistently difficult controls. Keep sb26 as a repeated volatility test, not a reason to discard unfavorable outcomes.
2. **Pair game and seed.** Match baseline/candidate game initialization, model sampling seeds, order, launch configuration, and budgets. Batch scheduling can remain nondeterministic, so pairing reduces rather than eliminates noise.
3. **Screen cheaply, confirm broadly.** One or two paired short-panel passes can reject obvious regressions. Promote only promising variants to all 25 games. A panel gain is not an estimate of hidden-score gain.
4. **Use two comparisons.** Equal generated-token budgets test reasoning/action efficiency. Equal wall-time budgets test the actual submission product, including throughput, cache, and CPU overhead.
5. **Report the actual paired deltas.** Score, cleared levels, actions on commonly cleared levels, time/tokens after the last clear, and failure category. Also report the full mean with and without each single game; the official mean remains the primary statistic.
6. **Separate two uncertainties.** Resampling paired games assesses dependence on the public game mix. Repeated seeds assess stochastic run variance. Neither proves transfer to harder private mechanics. Do not treat individual levels or actions as independent benchmark samples.

Tycho explicitly distinguishes game-resampling intervals from run-to-run variance. Its large public +9.42 effect remained +7.63 to +10.14 after deleting any one game; smaller policy differences had intervals crossing zero. This is a useful reporting pattern, not a reason to expect the same power for a +3 Qwen change. ([Tycho, July 2026](https://arxiv.org/html/2607.28287v1).)

### How many draws detect +3?

**Calculation:** For a pre-specified two-sided 5% test with 80% power, the normal approximation for independent paired full-panel means is

\[
n_{\rm pairs}\approx(1.96+0.84)^2(s_\Delta/3)^2.
\]

| SD of a paired full-panel difference | Approximate independent pairs | Total runs |
|---:|---:|---:|
| 2 points | 4 | 8 |
| 3 | 8 | 16 |
| 4 | 14 | 28 |
| 5 | 22 | 44 |
| 6 | 32 | 64 |

Small samples with estimated variance require more than these normal approximations. ([NIST sample-size methodology](https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm), undated reference, accessed October 3, 2026.)

For unpaired hidden aggregate submissions, assuming per-run SD **2**, the same approximation requires approximately **7 submissions per arm**, 14 total. If SD is 1.5 or 2.5, it requires approximately **4 or 11 per arm**. These SDs are hypothetical; the two observed scores do not establish one.

**Hidden-test recommendation — inference:** Use only the strongest one or two frozen candidates. Alternate A/B in balanced order, for example ABBA, while recording code/data hashes and all scores. This controls some time drift; it is not genuine game/seed pairing when only aggregate scores are returned. Avoid best-of-many selection and do not infer private gains from one high draw.

### Reconcile the evaluation plan with quota

**Calculation:** October 3–November 2 provides approximately **129 GPU-hours** and **86 TPU-hours** at the stated weekly allowances. Two nine-hour runs daily would consume **126 GPU-hours/week**, violating your budget. Two short approximately two-hour runs daily nearly exhaust 30 hours/week.

**Recommendation — inference:** Check the actual quota debit for committed/scoring runs once and maintain a ledger. If a nine-hour scored run debits your allowance, reserve one such run/week and use the remaining approximately 21 hours for short tests; daily hidden runs cannot coexist with that quota. If organizer rescoring does not debit it, the one-submission/day limit can be used independently, but notebook preparation/local runs still consume their measured hours.

A practical 30-hour development week is approximately **12×1.5-hour diagnostic slots = 18 hours**, **two four-hour confirmation slots = 8 hours**, and **4 hours buffer**. If scoring is charged, replace 9 hours of that work rather than exceeding the cap. Two concurrent sessions increase scheduling flexibility, not total available GPU-hours.

## 9. Ranked changes and the plan to November 2

**All gains, effort estimates, risks, scheduling decisions, and probabilities in this section are inference.** Ranges are rough net hidden-point forecasts, not confidence intervals; they are not additive and can include regressions. Existing UNDO, animation access, upscaling, solved-level memory, and 12-stream feasibility are already in your baseline and are not counted as newly available gains.

| Rank | Change | Net hidden-point planning range | Evidence supporting the choice | Implementation hours | Risk |
|---:|---|---:|---|---:|---|
| 1 | Preserve reasoning and factual evidence; make memory insertion cache-friendly; store contradictions and witnessed transitions alongside winning sequences | −1 to +4 | Your weakly positive memory test; supplied sirikilohit ablations; [OpenAI’s July 29 public study](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/) reports 13.3 → 38.3 with retained reasoning plus compaction and 6× fewer output tokens, on a different model/harness | 8–12 | Low–medium: compaction can erase evidence; an already-correct retention path adds no gain |
| 2 | Goal falsification, factual stall notices, and one fresh-context hypothesis review | −2 to +5 | Tufa’s July interview identifies the failure; Twin supports explicit goal checking, but supplies no Qwen ablation | 8–16 | Medium: false stalls and costly reviewers |
| 3 | Optional partial prediction checking followed by bounded planning and checked execution | −3 to +6 | EWM verification; Tycho’s selective-model comparison; adjacent open-model program induction | 16–28 | Medium–high: repair overhead or confidently wrong models |
| 4 | One controlled serving sweep: FR-Spec/draft depth first, compatible dense FP8 second, prefix/graph measurements throughout | −2 to +3 | September SM120 measurements give roughly 7–28% improvements in specific profiles, not guaranteed score gains | 6–12 | Medium: exact-quant incompatibility, precision changes, lost cache or startup time |
| 5 | Minimum game allocation plus marginal-progress scheduling and a small rescue reserve | −2 to +3 | Weighted RHAE favors later progress; no direct hidden scheduler ablation found | 6–10 | Medium: abandoning games immediately before a breakthrough |
| 6 | Select visual evidence by event: transient-only crops, animation metadata, initial/current/goal evidence rather than indiscriminate additional images | −1 to +2 | Taaf Anim reports token cost 384 → 449/action, +17%, and no significant small-panel gain; your baseline already has key perception features | 4–8 | Low–medium: omitting the crucial frame |
| 7 | Optional small/sibling QLoRA pilot for demonstrable procedural weaknesses | −3 to +2 | Direct ARC3 author report +0.69 on a much weaker 27B baseline; no matched gain at your baseline | 20–40 | High: overfit, serving/merge problems, opportunity cost |

The OpenAI memory study is evidence that retention can matter enormously, **not a prediction of +25 points for a Duck harness that already retains long history**. Likewise, the animation write-up reports a +1.4 public-score change with p=0.92 on 6 games × 4 passes; it does not justify adding more images indiscriminately. ([OpenAI, July 29, 2026](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/); [Taaf Anim, 2026](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369).)

**October 3–9 — measurement and inexpensive fixes.** Freeze the reference; audit reasoning round-trip and cache placement; classify approximately 100–200 public stall episodes; build paired evaluation and a quota ledger. Implement evidence records and factual goal contradictions. Microbenchmark the existing serving stack without changing target weights.

**October 10–16 — rescue wrong hypotheses.** Test stall review separately from memory changes. Add prediction checking to existing functions. Advance simulator planning only if prospective predictions are useful and overhead remains bounded.

**October 17–23 — exploit what worked.** Test bounded planning, the small scheduler amendment, and one serving candidate. Run full public confirmation on the strongest combinations. Fine-tune only if a specific procedural failure remains and earlier gains are stable.

**October 24–28 — select and freeze.** Stop broad exploration. Compare two complete candidates under full wall-time and realistic concurrency; use repeated hidden measurements within actual quota. Retain the working baseline as fallback.

**October 29–November 2 — offline delivery and repeatability.** Ship the exact public Kaggle weights/data, tokenizer/processor, wheelhouse, harness, and pinned runtime provenance. Run with internet disabled and account for startup/JIT time. Leave time to recover from queue or packaging failures; avoid an untested final model swap.

**Inference — probability assessment:** For a stable selected variant, not the luckiest single draw, I estimate approximately **80% for ≥30, 45% for ≥35, and 20% for ≥40** on a hidden distribution comparable to your current draws. These are subjective engineering probabilities, not a fitted statistical model. The final private subset adds unmeasured distribution uncertainty.

**Inference:** The plan’s likely productive outcome is several points from better evidence and fewer wasted hypotheses, with simulator planning providing the largest uncertain upside. Reaching 40 requires that these changes unlock enough genuinely difficult levels or materially reduce scored actions; throughput tuning alone is unlikely to supply the required approximately thirteen points.
