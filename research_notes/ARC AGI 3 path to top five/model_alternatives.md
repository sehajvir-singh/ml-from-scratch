# Model and inference alternatives to Qwen3.8-Flash-Next NVFP4 for an offline ARC-AGI-3 agent on Kaggle (as of 2026-09-25)

Scope: find any open-weight model, or any inference change, available by 2026-09-25 that could plausibly give ≥1.5× over the current ~4% hidden score. Hardware: 1× RTX PRO 6000 Blackwell 96 GB, 180 GB host RAM, 9 h, offline, 110 hidden games at 28 concurrent.

Local evidence comes from Thuitanium's campaign repo (clone at `scratchpad/thui`). Its files are cited by path, because they are primary run records (kernel names, submission IDs, p-values). Key baselines from that repo:
- Flash-Next chassis, hidden draws: B69 3.21; B71 3.74 / 3.41 / 2.90; B81 4.50 / 3.26; B88 3.86 / 3.51; B78 (MTP off) 3.49 — `notes/wayfinder/MAP.md` rows B81 and B88; `notes/LEDGER-all-runs.md` lines 21–25 and 81–82.
- So "~4% hidden" is the top of a ~2.9–4.5 same-chassis spread, with a pooled same-build sd of about 0.43 (MAP B88). A 1.5× step change means about 6% hidden.

---

## Q1. Open-weight models released Aug–Sep 2026 that fit (96 GB VRAM, possibly with 180 GB host offload): how do they compare with Flash-Next?

### Takeaway
No open-weight model released by 2026-09-25 is both stronger than Qwen3.8-Flash-Next on agentic, vision and coding benchmarks **and** able to fit this card at usable throughput.

The only models that beat it on vendor benchmarks are GLM-5.3-Flash (320B/18B active; NVFP4 is 204 GB) and MiMo-V2.6-Flash-RL (309B/15B active; FP8 is 178 GB). Neither fits in 96 GB. They would need 110–130 GB of experts in host RAM, which is almost certainly throughput-fatal at 28-way concurrency.

Everything that does fit is either the same active-parameter class or older, or it is text-only (Nemotron-3-Super). Some are already measured worse in this harness: Gemma-4-31B, Qwen3.5-122B-A10B, Qwen3.6-35B-A3B.

### Cited Findings
**Qwen3.8-Flash-Next (incumbent, 2026-08-27)**
- 125B total, **6B activated**, plus 51B n-gram embedding and 4B MTP. 48 layers: 12 × (3 Gated DeltaNet + 1 Qwen Sparse Attention). 512 experts with 10 routed + 1 shared. 262K context. Described as "experimental preview of the architecture that will underpin Qwen4" — [Qwen3.8-Flash-Next card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- Its benchmarks vs Qwen3.8-27B:
  - SWE-bench Pro 62.5 vs 61.7
  - LiveCodeBench v6 91.9 vs 90.3
  - DeepSWE 1.1 58.7 vs 42.2
  - Toolathlon 73.5 vs 67.1
  - OSWorld 2.0 binary/partial 19.4/52.3 vs 19.4/48.0
  - ERQA 72.3 vs 65.5
  - RealWorldQA 88.5 vs 85.9
  - MathVision (no CI) 90.6 vs 90.0
  - JobBench 55.7 vs 33.4
  - The card does **not** report BabyVision or any ARC-AGI number — [Qwen3.8-Flash-Next card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- The Qwen3.8-27B card reports BabyVision 65.7 (vs 28.9 for Qwen3.6-27B) — cited in prior notes from the [Qwen3.8-27B card](https://huggingface.co/Qwen/Qwen3.8-27B)
- The card warns: "lower reasoning effort does not always reduce overall task completion time… can also lead to insufficient analysis, more failures, and repeated retries" — [Qwen3.8-Flash-Next card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- The NVFP4 checkpoint is 135,195,303,851 bytes. Routed experts are NVFP4 W4A4; other parts and MTP stay BF16; PLE tables are FP8 — `notes/B79-quantization-counterparts.md`. On GPU the weights take 81.8 GiB of 94.4 GiB free, and the PLE tables sit in host RAM — MAP B81 row.
- The NVIDIA NVFP4 variant reports architecture `qwen4_exp` — [nvidia/Qwen3.8-Flash-Next-NVFP4](https://hf.co/nvidia/Qwen3.8-Flash-Next-NVFP4)

**GLM-5.3-Flash (zai-org, weights ~Sep 2026; NVIDIA NVFP4 created 2026-09-02)**
- 320B total, 18B active. Natively multimodal, hybrid sparse+linear attention, MIT license. Reasoning effort is low/high/max; `clear_thinking` defaults to false — [GLM-5.3-Flash card](https://huggingface.co/zai-org/GLM-5.3-Flash)
- Vs Flash-Next: DeepSWE 63.4 vs 58.7; Toolathlon 78.4 vs 73.5; Terminal-Bench 2.1 84.3 — [Featherless comparison](https://featherless.ai/blog/glm-5-3-flash-vs-qwen-3-8-flash-next-vs-qwen-3-8-27b)
- Vs Qwen3.8-27B: CharXiv-R 89.4 vs 90.2. Qwen3.8-27B is **better on BabyVision**; exact numbers are not shown on the page — [llm-stats](https://llm-stats.com/models/compare/glm-5.3-flash-vs-qwen3.8-27b)
- `nvidia/GLM-5.3-Flash-NVFP4` safetensors total **204.4 GB** (HF API, blobs=true, fetched 2026-09-25) — [HF](https://hf.co/nvidia/GLM-5.3-Flash-NVFP4)
- Artificial Analysis Intelligence Index: GLM-5.3 and Kimi K3 at 44, GLM-5.3-Flash 42, Qwen3.8 2.4T-A95B 40 — [Artificial Analysis on X](https://x.com/ArtificialAnlys/status/2097025645889069094)

**MiMo-V2.6-Flash-RL (Xiaomi, 2026-09-21/22)**
- 309B total / 15B activated. Omnimodal, 1M context, 5-layer MTP, MIT license. Benchmarks: OSWorld-Verified 80.8, DeepSWE v1.1 67.9, Toolathlon-Verified 73.6, Agents' Last Exam 27.6 (Flash-Next 24.3 pass@1), JobBench 61.2 — [MiMo-V2.6-Flash-RL card](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL)
- FP8 safetensors total **177.7 GB** (HF API, fetched 2026-09-25). No NVFP4 checkpoint was found.
- Also released: `MiMo-V2.6-Distill-Qwen-9B` (image-text-to-text, trending) — [HF trending](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B)

**Models that fit in VRAM but are not stronger**
- **NVIDIA Nemotron-3-Super-120B-A12B NVFP4:** 80.3 GB, released 2026-03-11, **text-only** (`text-generation`), Mamba-2+MoE+attention with MTP. LiveCodeBench v6 78.69 (Flash-Next 91.9), GPQA 79.2 (Flash-Next 91.7), HLE 18.3 (Flash-Next 35.9) — [Nemotron-3-Super NVFP4 card](https://hf.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4)
- **Mistral-Small-4-119B-2603:** 119B / **6.5B active**, 128 experts with 4 active, vision, Apache-2.0. It has an official NVFP4 checkpoint (70.8 GB, created 2026-03-03) and an EAGLE draft head. Compared only against GPT-OSS-120B (LCR 0.72; LiveCodeBench "outperforms GPT-OSS 120B") — [Mistral Small 4 card](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603)
- **DeepSeek-V4.1-Flash (2026-09-10):** 763B, MIT. NVIDIA NVFP4 exists, but at that size it cannot fit — [nvidia/DeepSeek-V4.1-Flash-NVFP4](https://hf.co/nvidia/DeepSeek-V4.1-Flash-NVFP4)
- **Kimi K3** is 2.78T parameters and does not fit — prior notes, [HF](https://huggingface.co/moonshotai/Kimi-K3)
- **Other new models trending on HF (Sep 2026)** are small or low-active:
  - XingChen Xing4.0-29B-A4B
  - ZDTaichu5.0-9B
  - yandex AliceAI-Foundation-80B-A3B-Base (a base model, no post-training)
  - prism-ml Ternary-Bonsai-2-27B
  - Source: [HF trending](https://huggingface.co/models?sort=trending)
- No official "Qwen4" open-weight release was found. HF searches for "Qwen4" return only small community fine-tunes (e.g. `qwen4b-*`). Flash-Next itself is the Qwen4-architecture preview — [HF search](https://huggingface.co/models?search=Qwen4); [Qwen3.8-Flash-Next card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- **Flash-Next derivatives released in September:**
  - `ukisai/Swift-1.5-Qwen3.8-Flash-Next-NVFP4` (2026-09-24)
  - `peonist-ai/halogen-qwen3.8-flash-next` (2026-09-23)
  - `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF`
  - `turboderp/Qwen3.8-Flash-Next-exl3`
  - None report ARC or agentic-game numbers — [HF search](https://huggingface.co/models?search=Qwen3.8-Flash-Next)

**ARC-AGI-3 numbers for any open model**
- The ARC-AGI-3 leaderboard (2026-09-24) lists GPT-6 Astra 62.7%, Claude Opus 5 30.2% and Gemini 3.8 Flash 10.4%. No open-weight entry was found in the summary — [BenchLM ARC-AGI-3](https://benchlm.ai/benchmarks/arcagi3); [ARC Prize leaderboard](https://arcprize.org/leaderboard)

### Inferences
- **Hard fit arithmetic (my estimate):**
  - GLM-5.3-Flash NVFP4 (204 GB) would need roughly 120 GB of weights in host RAM. That leaves ~60 GB of the 180 GB for the OS, PLE-style tables, the game engine and 28 agents.
  - MiMo-V2.6-Flash FP8 (178 GB) would need ~95 GB in host RAM. It might fit at ~4-bit if someone quantized it (≈90–100 GB), but no such checkpoint was found.
  - With 18B/15B active and 28 concurrent sequences, nearly all experts are touched every decode step. Offloaded experts must then either stream over PCIe (~64 GB/s theoretical for Gen5 x16, so ~2 s per step for 120 GB) or run on the 48 vCPUs, KTransformers-style.
  - Either way, aggregate throughput would likely fall by ≥10× from the ~336–503 tok/s the current stack achieves (MAP B87/B92).
  - The Duck/Flash-Next campaign shows throughput and depth both matter. v20 (7,656 actions, 3 levels) shows throughput without quality is useless. B69 shows a model-plus-serving change that kept throughput was the only lever that ever cleared p<0.05.
  - Result: offloaded GLM/MiMo is not a plausible 1.5× path inside 9 h and 110 games.
- **Benchmark deltas are small:** GLM-5.3-Flash vs Flash-Next is +4.7 on DeepSWE and +4.9 on Toolathlon. Flash-Next vs 27B on the benchmarks that matter here (vision, SWE) is also small, yet the Qwen3.6→3.8 swap was worth +37% on this harness (B6). Vendor-benchmark deltas of ~5 points do not predict ARC-AGI-3 play quality (B94 is the counter-example below).
- **Most likely model-side upgrade:** a future Qwen4 release in the Flash-Next size class (same architecture, same serving stack). None exists as of 2026-09-25.

### Gaps
- No BabyVision number for Flash-Next or GLM-5.3-Flash could be retrieved. The GLM card shows it only in an image (`bench_53.png`); llm-stats gives only a direction.
- No open-weight model has a published ARC-AGI-1/2/3 score on the official leaderboard summaries I reached.
- No measured throughput exists for GLM-5.3-Flash or MiMo-V2.6-Flash with expert offload on an RTX PRO 6000. The PCIe/CPU estimate above is mine.
- Microsoft, IBM, AI2 and xAI: no Aug–Sep 2026 open release relevant to this size class appeared in HF trending or search results. I did not search each organization exhaustively.

---

## Q2. What model swaps has the community (and Thuitanium) tried, and with what results?

### Takeaway
Every measured swap away from the Qwen3.8 line has lost, often badly:
- Gemma-4-31B: 0.41 public vs a ~4.5–8.7 band
- Qwen3.6-35B-A3B: 0.18
- Qwen3.5-122B-A10B NVFP4: 0 levels in a 3-game smoke vs 6
- The Flash-Next swap itself is the only model or serving change that ever cleared p<0.05: 17 up / 6 down, p=0.002 public. On hidden it gives ~3.2–4.5, not a separate band from Qwen3.8-27B's best.

There is no public evidence that any top-5 team uses a different model. None of the top-20 teams has a public competition notebook.

### Cited Findings
- **B94, Qwen3.5-122B-A10B-NVFP4 swap (closed 2026-09-22):**
  - Step 0 passed: ~7.9B vs ~5.1B active per token by the repo's count, the architecture is in the pinned image, and weights are 73.24 GiB of 94.43 GiB free, leaving 434,920 KV tokens at 7 GiB.
  - Smoke `yocybercode/thui-b94-q35-122b-smoke` (3 games tn36/vc33/bp35 @ 1,800 s): **1,640 actions / 0 levels** vs reference 211 actions / 6 levels.
  - Reasoning ran on 383/383 turns, but the median was only 444 chars.
  - Failure mode was action policy: bp35 clicked HUD edge `MOUSE(63,30)` ~700 times in 64-action identical batches.
  - Killed on play quality — `notes/wayfinder/MAP.md` row B94
- **The lead that motivated B94:** Kaggle user `ippeiogawa` went 3.47 → 6.65 on the board between 2026-09-17 and 09-21. He owns dataset `ippeiogawa/qwen35-122b-a10b-nvfp4` (71.3 GB). Whether he runs it on ARC-AGI-3 is **UNVERIFIED**, and "no top-20 team owns a public competition notebook" — MAP row B94
- **B64/thui-gemma-v1, Gemma-4-31B-it swap:** public **0.41**; 5 levels vs the chassis's 24 from the same ~1,500-action budget; 1.85× slower per request (185 s median, 45 timeouts); p = 0.0, WORSE — `notes/LEDGER-all-runs.md` line 83; design in `notes/B64-gemma-4-31b-duck-agent-design.md`
- Gemma-4-31B was the model of Milestone #1 2nd (Reki) and 3rd (forge), and Qwen3.6-27B FP8 powered 1st (Tufa Duck) — [ARC Prize Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- **v20, Qwen3.6-35B-A3B (MoE, 3B active):** **0.18** public. 7,656 actions (4.7×) but 3 levels vs 28 — MAP row B25
- **B6, Qwen3.6-27B → Qwen3.8-27B:** 3.31 public, 22 levels, "first run above every prior band" (+37%) — MAP row B6
- **B69, Keith Tyser's Flash-Next NVFP4 + MTP-3 stack (`keithtyser/duck-qwen3-8-flash-next-nvfp4-mtp`):**
  - His run: 6.76 public, 36 levels, 3,695 actions — `notes/B69-flash-next-serving-design.md`
  - Thuitanium pooled 8.69 / 38.5 levels vs the 27B pool: +4.30, 17 up 6 down, **p = 0.002**
  - Hidden 3.21 on first draw — `notes/LEDGER-all-runs.md` lines 81–82
- **Rank-21 team (ataraxian, 2.37 hidden at the time)** ran Qwen3.8 with `reasoning_effort=medium` — `notes/R26-reasoning-effort.md`
- **Other public repos:**
  - [adityav31121999/arcgames](https://github.com/adityav31121999/arcgames) runs Gemma-4-26B-A4B-NVFP4
  - Several are non-LLM, e.g. [BDR-Pro](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3) (learned transition model, "No LLM at runtime") and [AR6420](https://github.com/AR6420/arc-agi-3-agent) (BC policy)
- One GitHub agent reports 2.37 public on Kaggle, with a matched local run of 5.27 clearing 31/183 levels (per search snippet; model not stated in snippet) — [search result listing](https://github.com/anandsingh8687/arc-prize-2026-arc-agi-3-agent)

### Inferences
- The lane shows a sharp **quality floor** that small or older models fall through: 35B-A3B, 26B/31B Gemma and the 122B-A10B Qwen3.5. More actions did not help; they amplify degenerate click loops.
- B94 also shows a **harness-coupling effect.** Prompts and harness are tuned to Qwen3.8's behaviour, so any swap pays a re-tuning tax that a 3-game smoke cannot separate from model quality.
- Taken together, a new model would need to be clearly stronger than Flash-Next *and* be re-tuned. Nothing released by 2026-09-25 meets the first condition inside the hardware box (see Q1).
- ippeiogawa's +3.18 public jump is the only rival datapoint hinting at a different model. It is unverified, and it is a public-board number (public ≈ 2–2.5× hidden on this chassis, per LEDGER pairs such as 9.32 public / 3.21 hidden).

### Gaps
- Kaggle discussion content could not be read. The internal JSON endpoint `discussions.DiscussionsService/GetTopicListByForumId` returned 403 `forums.get denied` without auth, and earlier sessions note the discussion SPA has no body. No community table of model-swap results was found.
- Top-5 teams' models are unknown. None of them publishes a competition notebook (MAP B94).

---

## Q3. Quantization and offload options on the RTX PRO 6000: speed/quality trade-off

### Takeaway
For Flash-Next, NVFP4 (W4A4 experts) is already the best-measured format under concurrency:
- 930.7 tok/s aggregate at C16, vs 697 tok/s for EXL3 4-bit
- Single-stream 151–171 tok/s
- About 48 GiB of PLE n-gram tables offloaded to host RAM

fp8 KV is dead on the pinned build. The real binder on Kaggle is KV and prefill, not weights: weights 81.8 GiB, KV 7–12 GiB. So squeezing weights (3-bit) would matter only to buy KV. Offloading *experts* (not PLE) of a bigger model to RAM is not viable at 28-way concurrency.

### Cited Findings
- **Optimized SGLang, 1× RTX PRO 6000, RadixArk NVFP4 Flash-Next** — [NVIDIA Developer Forum](https://forums.developer.nvidia.com/t/optimized-qwen3-8-flash-next-on-1x-rtx-pro-6000-171-tok-s-524k-and-hicache-nixl-persistence/381722)
  - Decode: C1 171.09 tok/s; C4 427.54 tok/s aggregate
  - Prefill: 10,104 tok/s at 64K
  - PLE: "Flash-Next normally keeps roughly 47.7 GiB of PLE resident in system RAM"
  - KV: FP8 KV (SGLang), GPU KV pool 824,384 tokens
  - MTP: mean accepted length 2.58, acceptance 52.74%
  - Online FP8 path: +28.3% short-context decode
- **EXL3 4-bit vs NVFP4 on RTX PRO 6000** — [tpurtell/sm12x-exl3-qwen3.8-flash-next](https://github.com/tpurtell/sm12x-exl3-qwen3.8-flash-next)
  - C1: 152.82 vs 151.11 tok/s
  - C16 aggregate: **696.96 vs 930.71 tok/s** (NVFP4 33% faster at concurrency)
  - EXL3 resident payload ~95 GiB; EXL3-PLE8 ~48 GiB
  - No perplexity or KLD comparison is published
- Search-snippet figures: SGLang + MTP single-stream 164.7 tok/s; "4-bit expert formats decode at approximately 82 tok/s single-stream with ~680 ms TTFT" (per [Kubesimplify](https://blog.kubesimplify.com/running-qwen3-8-flash-next-on-dgx-spark-and-rtx-pro-6000), search snippet, not fetched)
- **On Kaggle, Thuitanium's measured serving profile (pinned vLLM dev image)**
  - KV 7 GiB: 263,568 tokens, Running 10, Waiting 15, KV 95%
  - KV 12 GiB: 452,340 tokens, Running 17, generation 408 tok/s, no OOM
  - Queue time converts to decode time almost 1:1, and levels stay 18/18/18 — MAP B87
- Stripping re-sent reasoning cut prompt tokens −35% and raised generation +49% (336 → 503 tok/s), but actions fell −30% and levels 18 → 11 — MAP B92
- **fp8 KV** is rejected at startup by the QSA backend on this build (`kv_cache_dtype` bf16-only; checkpoint ships no k/v scales) — MAP B86
- Prefix caching: hit rate only 0.196, costs 8% of KV and 15× preemptions, because history is trimmed from the front — MAP B91
- **Official Flash-Next FP8** is 185.5 GB and not a drop-in for a single 96 GB card. Qwen3.8-27B NVFP4 (Unsloth) is 23.4 GB and FP8 is 30.9 GB — `notes/B79-quantization-counterparts.md`
- **GGUF 3-bit / low-bit** Flash-Next quants exist (`unsloth/Qwen3.8-Flash-Next-GGUF`, `ISTA-DASLab/...GSQ-RCO-GGUF`), but llama.cpp-style serving has no vLLM-class batched throughput evidence at 28-way concurrency — [HF search](https://huggingface.co/models?search=Qwen3.8-Flash-Next)
- **MXFP4:** gpt-oss-120b ships MXFP4 MoE weights (5.1B active, text-only), and the lane already set it aside as the dead low-active class — prior notes, [gpt-oss-120b card](https://huggingface.co/openai/gpt-oss-120b); MAP B94

### Inferences
- A 3-bit Flash-Next could free ~15–20 GB of weights for KV (my estimate). B87 shows extra KV raises concurrency (Running 10 → 17) but did not move levels. So quantizing down for KV is not a demonstrated score lever, and it risks quality with no published KLD.
- Online-FP8 or EXL3 variants are single-stream optimizations. At C16+, NVFP4 wins.
- For a *bigger* model, even perfect NVFP4 leaves GLM-5.3-Flash (204 GB) and MiMo (178 GB FP8) beyond the 96 GB card. The PLE offload that works for Flash-Next works because n-gram embedding lookups are sparse and cheap. MoE experts touched at every step are not (the Flash-Next card itself says n-gram embedding is "more amenable to offloading than MoE").

### Gaps
- No measured ARC-harness quality delta between NVFP4 and FP8 for Flash-Next exists. FP8 does not fit, so it cannot be tested on Kaggle hardware.
- No KLD or perplexity data for EXL3 or GGUF 3-bit Flash-Next was found.

---

## Q4. Inference-time strategies with evidence on ARC-AGI-3 or similar agentic benchmarks

### Takeaway
On this harness, the serving-side levers have all been measured null or negative:
- MTP on/off
- KV size
- prefix cache
- reasoning effort `medium` (−57% levels, p=0.0052 WORSE)
- stripping reasoning

The one strategy with strong evidence elsewhere is **retaining reasoning plus compaction or verification**: GPT-5.6-Sol went 13.3% → 38.3% with retained reasoning, and verification variants reach ~99% human-relative efficiency. But that evidence is on frontier closed models.

Best-of-n or parallel rollouts on real game actions are penalised by RHAE's squared action-efficiency. Whether a *separate* local simulator copy can be used for free look-ahead in the Kaggle evaluation is not documented. There is no published evidence for self-consistency or a small+big model pair on ARC-AGI-3.

### Cited Findings
**Scoring (what rollouts cost)**
- RHAE: "Each turn where the agent submits a command… counts as an action"; internal operations (tool calls, reasoning, retries) are not counted. Per-level efficiency relative to the upper-median human is **squared**, so 10 vs 100 actions scores (10/100)² = 1% — [ARC-AGI-3 methodology](https://docs.arcprize.org/methodology); [ARC-AGI-3 paper](https://arxiv.org/html/2603.24621v1)
- The game score is the level-index-weighted average of per-level scores — [methodology](https://docs.arcprize.org/methodology)
- Thuitanium found a second cap: `completion_cap = 100·Σ(done levels)/W`. 7 of 25 games already sit at it, and "depth is the only axis left: +1 level/game = 12.07 public (×2.56)" — MAP row B20
- UNDO (ACTION7) "is real and free; it is not a lever": B76 pooled −1.70 public, p=0.46 — `notes/LEDGER-all-runs.md` lines 25–27

**Reasoning budget**
- Qwen3.8 template: `reasoning_effort` defaults to xhigh ("think carefully… validate key assumptions"); medium appends nothing; low asks for brevity — `notes/R26-reasoning-effort.md`, verified against [Qwen3.8-27B-FP8 chat_template](https://huggingface.co/Qwen/Qwen3.8-27B-FP8)
- **v21 (effort=medium):** tokens per action −39%, actions +83%, **levels 28 → 12, 1.25 public, p = 0.0052 WORSE** — `notes/LEDGER-all-runs.md` line 62
- Qwen's own card warns lower effort can increase failures and retries in multi-turn agentic tasks — [Qwen3.8-Flash-Next card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- Retaining reasoning plus compaction moved GPT-5.6 Sol from 13.3% to 38.3% on the public set "while using 6× fewer tokens" — prior notes, citing OpenAI (July 30, 2026)
- On Flash-Next, stripping re-sent reasoning (B92) cut levels 18 → 11. B100 (strip only from levels already left) is built but unrun — MAP B92, B100

**Speculative decoding (MTP / EAGLE-3 / DFlash)**
- **B78, MTP-3 → MTP-0 on Flash-Next:** 4,049 actions vs a 3,739 baseline (ratio 1.083), 40 vs 38.5 levels, p = 0.5163 NOT-DISTINGUISHABLE, hidden 3.49 — `notes/B78-mtp-off.md`; LEDGER line 23. At 28-way concurrency, MTP buys nothing measurable.
- Flash-Next native MTP acceptance on the RTX PRO 6000 is 52.74% (mean accepted length 2.58) — [NVIDIA forum](https://forums.developer.nvidia.com/t/optimized-qwen3-8-flash-next-on-1x-rtx-pro-6000-171-tok-s-524k-and-hicache-nixl-persistence/381722)
- General evidence:
  - "Expert routing can make speculative acceptance less predictable… weaker gains on MoE systems"
  - At batch 32–64, EAGLE-3 acceptance falls while MTP keeps ~2× (vendor blog)
  - DFlash reports 2.5–2.7× at concurrency 16 on a dense 9B
  - Sources: [Spheron MTP guide](https://www.spheron.network/blog/multi-token-prediction-mtp-gpu-cloud-deployment-guide/); [DFlash paper](https://arxiv.org/pdf/2602.06036)
- No EAGLE-3 or DFlash speculator for Flash-Next was found on HF (search "Flash-Next speculator eagle3 dflash" returned 0) — [HF search](https://huggingface.co/models)

**Executable world models / verification (closest thing to simulation-based search)**
- Codex with gpt-5.4/5.5/5.6-sol on 25 public games:
  - The verification variant completes every public level at ~99% human-relative action efficiency
  - The textual variant beat flexible executable world models in both gpt-5.5 conditions
  - Verification "uses substantially more resources"
  - The paper has no best-of-n or rollout study
  - Source: [arXiv 2607.15439](https://arxiv.org/abs/2607.15439)
- The game engine runs "~800 actions/sec on CPU", so model inference dominates the budget — prior notes, [anandsingh8687](https://github.com/anandsingh8687/arc-prize-2026-arc-agi-3-agent)

**Throughput versus quality**
- More actions without depth is useless: v20 had 4.7× actions and 3 vs 28 levels (MAP B25); B81 had +48% actions and was ND; B87 had +21% generation with levels 18/18/18.
- Tokens: prompt tokens are 94% of GPU work (9.42M prompt vs 0.62M generated) — MAP B91

**Two models (small plus big)**
- A 31B dense Gemma alone was 1.85× slower per request than Flash-Next under 25-way load (LEDGER line 83).
- A second resident model would have to share 96 GB with Flash-Next's 81.8 GiB of weights, leaving ≤5 GB. In practice a second model means swapping Flash-Next for 27B-class models (Qwen3.8-27B NVFP4 23.4 GB + another) — B79.
- No ARC-AGI-3 evidence for a draft/fast model plus big model split was found.

### Inferences
- **Best-of-n / parallel rollouts on the scored environment:**
  - Each extra real action enters the squared efficiency, and RESET/UNDO do not erase counted actions (UNDO measured "free" only in the sense of not being a lever).
  - Real-action best-of-n therefore trades directly against score and is only positive when a level would otherwise not be cleared at all. The B20 depth finding makes that exact regime plausible, but no one has measured it.
- **Look-ahead in a private simulator:** because the engine is ~800 actions/s on CPU, "free" look-ahead in a *private copy* of a game would be the most powerful inference-time change, if the Kaggle harness lets the agent instantiate or copy game state without the actions counting. I found no rule text allowing or forbidding it. This must be verified against the competition's `arc-agi` package and rules before investing.
- **Self-consistency:** sampling k analyses per turn multiplies the dominant cost (prefill of ~17k-token prompts, 94% of GPU work) by ~k. With KV already the binder, k=3 would cut turns per game by ~3× (my estimate), in the same direction as v21, which lost.
- **Speculative decoding:** no headroom. MTP already exists and is ND. EAGLE-3 is unavailable for Flash-Next, and spec-decode gains shrink at the 10–17 running sequences this stack sustains.
- **Reasoning budget:** the only tested direction (less) was strongly worse. More than xhigh is not available. "Retain more reasoning / pin cleared-level traces" (B99, B100) is the remaining direction, supported by the GPT-5.6 retention result and B89/B92.
- **Overall:** no inference-strategy change has evidence of ≥1.5× on this stack. The candidates with any directional support are harness-level (memory/retention, verification) rather than decoding-level.

### Gaps
- Whether RESET counts as an action, and whether an agent may run a local game copy for look-ahead in the Kaggle eval: not stated on the methodology pages fetched ([docs](https://docs.arcprize.org/arc-prize-2026), [methodology](https://docs.arcprize.org/methodology)).
- No published best-of-n, self-consistency or small+big-model result on ARC-AGI-3 with open models.
- No measurement of DFlash or EAGLE-3 on hybrid GDN/QSA MoE architectures.

---

## Q5. Is there any evidence that the top teams use a different model?

### Takeaway
No direct evidence exists. No top-20 team has a public competition notebook. The only indirect signal is ippeiogawa's public jump 3.47 → 6.65 (17–21 Sep) plus his public Qwen3.5-122B-A10B NVFP4 dataset. That same model scored 0 levels in Thuitanium's smoke, so if he uses it, his gain likely comes from harness changes, not the model.

### Cited Findings
- "no top-20 team owns a public competition notebook"; ippeiogawa 3.47 → 6.65, dataset `ippeiogawa/qwen35-122b-a10b-nvfp4` (71,314,010,751 bytes, updated 2026-07-17); "Whether he runs it on ARC-AGI-3 is UNVERIFIED: his other public kernels are AIMO3" — MAP row B94
- On 2026-09-10 the top-five boundary was 6.17 and first place 11.04 (board read at 12:3xZ) — `notes/B78-mtp-off.md`
- Milestone #1 winners used Qwen3.6-27B FP8 (1st) and Gemma-4-31B (2nd, 3rd) — [ARC Prize Milestone #1](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- Keith Tyser's public Flash-Next NVFP4 + MTP kernel (6.76 public, n=1) is the public origin of the current chassis — `notes/B69-flash-next-serving-design.md`

### Inferences
- The top board (6–11) is 1.5–3× above the Flash-Next chassis (~3.2–4.5). With every public model and serving swap measured flat or worse, the gap is more likely harness, memory or strategy than weights. Milestone #2 open-sourcing (deadline 2026-09-30) should reveal the top teams' models; checking those write-ups right after is the cheapest way to settle this.

### Gaps
- Kaggle leaderboard team notebooks, discussions and Milestone #2 write-ups were not accessible or not yet published as of 2026-09-25.
