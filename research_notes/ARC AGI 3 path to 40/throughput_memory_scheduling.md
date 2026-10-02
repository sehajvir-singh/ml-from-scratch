# Throughput, memory, context and scheduling for Qwen3.8-Flash-Next on one RTX PRO 6000 (ARC-AGI-3, offline)

Source key (used inline below):
- SUMMARY = https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md
- COMPARISON = https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md
- FRANZEN-WU = https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md
- FRANZEN-SERVE = https://github.com/da-fr/arc-agi-3-solution/blob/main/serving/README.md
- FRANZEN-NB = https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/dfranzen/arc-agi-3-milestone-2-solution.ipynb (launch config around lines 10690-10985)
- SIRI-WU = https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md
- SIRI-UCB = https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/af105202327dcf35bd670a50b2558adab12e8dd3/cells/44_patch_cell_v16_7_m72_one_pool_ucb_scheduler.py
- PENNY = https://github.com/jpezzulli/sglang-rtxpro6000 (README); PENNY-FP8 = .../blob/master/FP8.md; PENNY-RES = .../blob/master/RESULTS.md; PENNY-MEM = .../blob/master/MEMORY-AND-PERSISTENCE.md
- OLY = https://github.com/gabrielolympie/sglang-flashnext-sm120 (README); OLY-STATUS = .../blob/main/docs/STATUS.md; OLY-PERF = .../blob/main/docs/PERF_CEILING.md
- MRATSIM = https://github.com/mratsim/sglang-qwen38fn-sm120-turbo (README, master branch)
- HF-QWEN = https://huggingface.co/Qwen/Qwen3.8-Flash-Next ; HF-INTEL = https://huggingface.co/Intel/Qwen3.8-Flash-Next-W4A16-AutoRound ; HF-RADIX = https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4 ; HF-PRIM = https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8 ; HF-ALB = https://huggingface.co/albucino/Qwen3.8-Flash-Next-W4A16-FP8PLE

All dates below are 2026. All three Milestone-2 prize notebooks run Tufa Labs' Duck harness and serve Qwen3.8-Flash-Next on one RTX PRO 6000 (96 GB) — [SUMMARY](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md).

---

## Q1. Qwen3.8-Flash-Next architecture and the available quantizations (quality/speed tradeoffs)

### Takeaway
Flash-Next is a 125B-total / 6B-active hybrid MoE (36 Gated-DeltaNet linear-attention layers + 12 Qwen-Sparse-Attention layers, 512 experts top-10), plus a 51B n-gram "PLE" embedding table that must live in host RAM on a 96 GB card and a 4B MoE MTP head. Every public 4-bit expert format lands within noise of each other (and of BF16) on quality; speed differences come from what *else* is quantized (attention/GDN/dense stack, MTP head), and memory differences come from MTP-head and PLE precision.

### Cited Findings
**Architecture**
- 125B params with 6B activated, plus 51B n-gram embedding and 4B MTP; hidden 2560; vocab 248,320; 48 layers laid out as 12 × (3 × (Gated DeltaNet → MoE) → 1 × (Qwen Sparse Attention → MoE)) — [HF-QWEN](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- GDN: 48 V heads / 16 QK heads, head dim 128. QSA: 24 Q heads / 2 KV heads, head dim 256, RoPE dim 64; indexer is MQA with 4 query heads + 1 shared key head (dim 128); budget "512 blocks or 2048 tokens" — [HF-QWEN](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- MoE: 512 experts, 10 routed + 1 shared, expert intermediate 640; Gated Residual ("hyper-connection") with 4 branches, bottleneck rank 320; N-gram embedding of 20,000,000 entries (bigrams/trigrams at layer 2); MTP is 1 layer "trained with multi-steps"; native context 262,144, extensible to 1,000,000 with YaRN — [HF-QWEN](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- Qwen's recommended sampling: thinking mode temperature 1.0, top_p 0.95, top_k 20; non-thinking temperature 0.7, top_p 0.80, presence_penalty 1.5 — [HF-QWEN](https://huggingface.co/Qwen/Qwen3.8-Flash-Next). (Prize notebooks used 0.7 / 0.6 / 0.6 — [SUMMARY](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md); Franzen used temp 0.7, top-p 0.95, top-k 20 — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md).)
- Bytes read per decode step at bs=1 (NVFP4 checkpoint): routed experts 1.43 GB (NVFP4), GDN projections 4.17 GB, QSA 1.34 GB, HyperConnection 1.32 GB, shared expert+router 0.61 GB, lm_head 1.27 GB (all BF16) — total ≈10.14 GB/step, 85% BF16. The MTP draft layer is itself a 512-expert MoE (5.21 GB, ~0.25 GB read per draft step). PLE table 51.27 GB lives in host RAM and is gathered per token over PCIe Gen4 x16 (~32 GB/s); GDDR7 bandwidth 1,792 GB/s → no-MTP ceiling ≈177 tok/s single-stream — [OLY-PERF](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/PERF_CEILING.md)
- Steady-state MTP decode is GPU-bound (~99% busy); per-step composition after optimization: fp8 GEMMs 3.43 ms, NVFP4 MoE 3.21 ms ("at floor"), HC 1.64 ms (barrier-bound), MoE glue 0.88, small bf16 GEMMs 0.86, GDN 0.76, QSA 0.46; ~2,300 kernels/step — [OLY-PERF](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/PERF_CEILING.md)

**Quantizations**
- Intel W4A16 AutoRound: INT4 experts only (iters 200); lm_head, embed_tokens, visual, linear_attn, self_attn, hyper_connection, mlp.gate, shared_expert, PLE, MTP, indexer are left unquantized. Reported average across GSM8K/MMLU/PIQA/HellaSwag = 99.64% of BF16 (0.8332 vs 0.8362) — [HF-INTEL](https://huggingface.co/Intel/Qwen3.8-Flash-Next-W4A16-AutoRound)
- RadixArk NVFP4 (ModelOpt, W4A4 E2M1 group 16): only routed experts quantized; attention/QSA/GDN/mHC/shared/router/embeddings/lm_head and all 31 MTP tensors stay BF16; PLE tables use FP8 from the Qwen FP8 revision; 360 GB → 135 GB. GSM8K 97.27 vs BF16 97.12–97.50; AIME26 98.75 pass@1 vs 100. Caveat on card: "long agentic generations tend to run longer than BF16" — [HF-RADIX](https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4)
- primitive-ai mixed NVFP4-FP8 (v2): NVFP4 experts + FP8 full-attention and GDN projections; 84.4 tok/s single-stream and 526 tok/s @ C32 (prefix-cache-free, vLLM) vs 74.4 / 483.8 for their plain NVFP4 (+13% / +8.7%); quality identical within noise (knowledge 92.2, tool-call 84.8 vs 84.6). Requires `VLLM_GDN_DECODE_KERNEL=triton` (default CUDA kernel hangs at ~32 concurrency with FP8 GDN) — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- Same-box comparison of 4-bit builds (vLLM, 8K/512, no prefix cache): mixed 84.4 tok/s@1 / 520@32; Intel AutoRound 82.6 / 482; lvkaokao RTN 82.4 / 481; cyankiwi AWQ g32 81.6 / 422; wtdcode AWQ 82.6 / 484; nota-ai NVFP4 74.5 / 483; nvidia NVFP4 71.5 / 451. Tool-calling all 76–80.5 (±1.5 band). "Every 4-bit expert format decodes at ~82 tok/s single-stream… the speed difference in the top row is the FP8 attention, not the expert format" — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- MTP head precision tradeoff (vLLM, MTP3, 32K ctx): BF16 head 5.03 GB → KV pool 134,192 tok, 143.3 tok/s, acceptance 59.2%; FP8 head 2.52 GB → 180,224 tok, 142.1 tok/s, 57.3%; NVFP4 head 1.42 GB → 198,168 tok, 141.1 tok/s, 56.7%. "Acceptance drops about 2 points and single-stream decode about 1%, and in exchange the KV pool grows by a third to a half." — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- MTP speed-up (vLLM, real prompts, single stream, thinking on): none 91.2 tok/s; 2 spec tokens 133.2; 3 spec tokens 142.6 (+56%); `num_speculative_tokens: 1` does not boot on that image — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- PLE table quantization: FP8 per-row 49 GB, INT4 g16 32 GB, NVFP4-style 28.8 GB vs BF16 95 GB; accuracy holds; throughput within 5–6% of in-RAM BF16; MTP 129.6 tok/s (INT4 table) vs 142.6 in-RAM BF16. MTP + disk-backed BF16 table collapses the MTP gain (77.5–82.3 tok/s) — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- albucino W4A16-FP8PLE: Intel AutoRound target tensors unchanged + RadixArk FP8 PLE table (replacing the 102.4 GB BF16 table) + compact INT4 group-32 MTP draft under `runtime/mtp-int4-g32` (3.855 GiB payload, 4,639 tensors); target payload 116.183 GiB — [HF-ALB](https://huggingface.co/albucino/Qwen3.8-Flash-Next-W4A16-FP8PLE)
- Franzen switched from RadixArk NVFP4 to Intel W4A16 shortly before the deadline: "similar quality and throughput, while leaving more VRAM available for the KV cache"; kept BF16 PLE in host RAM (machine has enough RAM); used albucino INT4 MTP as separate draft — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- Notebook GPU footprints: Franzen 73.64 GB weights (69.85 target + 3.79 draft); lordhansolo (primitive-ai mixed, MTP built in) 71.94 GB; sirikilohit 73.57 GB (69.78 + 3.79) — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- Other checkpoints noted: local-inference-lab QAD NVFP4 (`qad-step-4000` branch) scored 79.4% vs 77.5% on AA-LCR and 78.69% vs 77.17% arithmetic vs published NVFP4 (served TP=2 in mratsim's example) — [MRATSIM](https://github.com/mratsim/sglang-qwen38fn-sm120-turbo); hampsonw ships an INT4 delta for the MTP experts (5.2 GB → 1.5 GB) on Intel's build "with acceptance unchanged in their runs" — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- Expert pruning (25% of experts) to free memory: "More room, worse play" (single runs) — [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md). Swift 1.5 fine-tune: no better per token and ~35% slower decode — [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md)

### Inferences
- Since all 4-bit expert formats tie on quality, the quant choice for ARC should be driven by (a) VRAM left for KV (Intel W4A16 wins slightly per Franzen) and (b) whether the serving stack can additionally shrink the BF16 dense stack (where the per-step bytes are).
- The MTP draft is a large, cheap-to-shrink memory item: going from Franzen's 3.79 GB INT4 g32 draft to an NVFP4/INT4-g128-style 1.4–1.5 GB head would free ~2.3 GB. At Franzen's observed ~11.45 KB/token FP8 KV (11.58 GB / 1,011,264 tokens, from COMPARISON), that is roughly +200k KV tokens (my arithmetic, not measured), at a cost of ~2 points of acceptance per HF-PRIM.

### Gaps
- No ARC-specific (agentic game-play) quality comparison between quantizations was found; all quality numbers are generic benchmarks or single-run ARC anecdotes.
- Tech report (github.com/QwenLM/Qwen3.8-Flash-Next tech_report.pdf) not read; QSA compression details beyond the model card not verified.

---

## Q2. SGLang vs vLLM on sm120: forks, patches, measured tok/s, Mamba prefix-cache retention, FP8 KV, speculative decoding

### Takeaway
SGLang forks (Pennyroyal + Olympie/mratsim patches) are the most-optimized single-GPU stacks: ~171–231 tok/s single-stream and 620–1,170 tok/s aggregate at C4–C8 in benchmarks; in the ARC notebooks, peak decode was 946 (SGLang, 10 streams), 1,135 (vLLM, 14), 1,159 (SGLang, 16). The key ARC-specific enabler is hybrid prefix caching (KV + Mamba/GDN state checkpoints): Franzen reached 93.43% token-weighted prefix reuse with a custom patch; lordhansolo's patched vLLM logged a 91% median hit rate.

### Cited Findings
**Pennyroyal (jpezzulli/sglang-rtxpro6000)**
- SGLang-derived runtime for one RTX PRO 6000 (SM120, TP=1); Flash-Next profile = NVFP4 target, FP8 KV, native NEXTN MTP with FR-Spec; 524,288-token context with HiCache + NIXL; author runs C=6 with an observed pool of 1,039,040 tokens; v2.5.3 fixes a native-MTP checkpoint-selection bug (phantom tokens / file writing, issue #17) — [PENNY](https://github.com/jpezzulli/sglang-rtxpro6000)
- Host memory: 32 GB HiCache + ~47.68 GiB RAM-backed FP8 PLE table by default — [PENNY](https://github.com/jpezzulli/sglang-rtxpro6000)
- Online FP8 (v2.5.0, `SGLANG_SM120_ONLINE_MXFP8=true`): converts eligible BF16 projections to MXFP8, HC mix and lm_head to row-wise FP8 at load. Single request: short 161.47 → 207.12 tok/s (+28.3%), 128K 154.70 → 195.63 (+26.5%), 490K 149.14 → 172.64 (+15.8%). C4 aggregate: 128K 367.1 → 422.0 (+15.0%), 490K 236.7 → 329.0 (+39.0%). Frees ~3.86 GiB (7.52 vs 3.66 GiB available after graphs). Cold TTFT did not improve — [PENNY-FP8](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/FP8.md); [PENNY-RES](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/RESULTS.md)
- Online FP8 is qualified for the ModelOpt NVFP4 expert layout; "other hardware and module shapes fail at startup"; for other checkpoints use "ModelOpt NVFP4 expert layout … and expected unquantized projection structure" — [PENNY-FP8](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/FP8.md)
- FR-Spec (65,536-token draft vocab, verify unchanged): single-request median 171.93 tok/s, four-request aggregate 447.04 tok/s; +4.5–7.0% aggregate vs baseline — [PENNY-RES](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/RESULTS.md)
- NVMe vs RAM PLE, C4 aggregate median 369.73 vs 428.90 tok/s — [PENNY-RES](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/RESULTS.md)
- Native NEXTN acceptance in an earlier suite: 2.58 mean accepted / 52.74% — [PENNY-RES](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/RESULTS.md)
- BF16 recurrent state reduced bytes per Mamba slot; automatic sizing raised slots 21 → 49; the speculative-intermediate SSM reserve is skipped when RecoverSSM/WY reconstructs accepted state — [PENNY-MEM](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/MEMORY-AND-PERSISTENCE.md)

**gabrielolympie/sglang-flashnext-sm120** (official SGLang `qwen4-main-squashed` + 6 patches)
- Decode C1 231 median / 243 best (temp 0.6, relaxed accept), 203 lossless greedy; C4 620–657; C8 758; prefill ~10.4K tok/s on 2.5K; TTFT ~135 ms; vs jpezzulli's 171 / 428 at the time — [OLY](https://github.com/gabrielolympie/sglang-flashnext-sm120)
- Patches: 0001b RecoverSSM + WY output-only MTP verify on FlashInfer for sm120; 0002 FP8-KV tile dequant for QSA sparse prefill ("2× KV capacity"); 0003 fp32 prefill state for sm120 GDN kernel; 0004 Triton low-M GEMM (cuBLAS-under-capture ran decode projections at 20–75% of DRAM BW; this reaches ~90%); 0005 W8A16 fp8 weight-only for the dense BF16 stack ("85% of per-step traffic"); 0006 fp8 HC mix + lm_head — [OLY](https://github.com/gabrielolympie/sglang-flashnext-sm120)
- Ladder of wins: low-M GEMM C1 142.8 → 147.9; relaxed MTP acceptance (`SPEC_ACCEPT_SINGLE/ACC`) 1.0 lossless = 179 → 0.5 = 203 → 0.3 = 231 tok/s (lossy at temp>0, "sharpens sampling; exact at temp 0"); FR-Spec 64K hot tokens +9%; 8-way profile C8 487 → 758 once Mamba cache sized up — [OLY-STATUS](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/STATUS.md); [OLY-PERF](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/PERF_CEILING.md)
- "`--max-mamba-cache-size` must be ~6× max-running-requests or the speculative CUDA graphs silently cap at bs=4 (8-way used to run *slower* than 4-way)"; 8-way config `MAXREQ=8 CUDAGRAPH_MAXBS=8 MAMBA_CACHE=48` — [OLY](https://github.com/gabrielolympie/sglang-flashnext-sm120)
- fp8 weight-only copies cost ~3.3–3.6 GB VRAM (MEMFRAC 0.95–0.96); long-context profile trades them back for KV — [OLY-STATUS](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/STATUS.md)
- Deeper drafting is closed: server refuses >4 draft tokens — "Qwen QSA requires speculative_num_draft_tokens <= the QSA compress ratio (4)"; 3 steps / 4 draft tokens is the architectural max on that branch — [OLY-PERF](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/PERF_CEILING.md)
- Closed levers: `--enable-torch-compile` (capture fails), HC block retune, CUBLAS_WORKSPACE_CONFIG — [OLY-PERF](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/PERF_CEILING.md)
- Estimated ceiling after fp8/NVFP4 "byte diet": ~7 ms/step → ≈305 tok/s at accept 2.15, ≈385 at relaxed accept 2.7; finishes at ~60–66% of that; remaining gains need fused megakernels or MTP retraining — [OLY-PERF](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/PERF_CEILING.md)

**mratsim/sglang-qwen38fn-sm120-turbo** (r24)
- RadixArk NVFP4 at TP1 (GPU power-limited 360 W, memory +3000 MT/s): 939,456 KV tokens for 4 max requests and 856,256 for 8 at 0.98 util; prefill 11–13K tok/s; aggregate ~800 tok/s at C4 (~200/stream) and 1,170 tok/s at C8 on a hard reasoning profile; up to 355 tok/s single request on easy code. TP=2 QAD checkpoint: 1,600–1,800 tok/s at C16, MTP accept length 3.2–3.5 — [MRATSIM](https://github.com/mratsim/sglang-qwen38fn-sm120-turbo)
- Its patches 0003/0007/0008 inspired Pennyroyal's online FP8; its patch 0002 (GDN RecoverSSM) budget-accounting is the source of Franzen's spec-state memory fix — [PENNY-FP8](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/FP8.md); [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)

**vLLM**
- Architecture merged into vLLM main 2026-08-31 (#53896); single-GPU PLE CPU offload (#53899) still open as of 2026-09-03; needs `--distributed-executor-backend mp`, `VLLM_PLE_CPU_OFFLOAD=1`, a long ready timeout; known startup hang (#53960) — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- vLLM NVFP4 MoE: `--moe-backend marlin` 93.2 vs 84.6 tok/s single-stream over auto FLASHINFER_CUTLASS, but −1–3% at C32 and +12% TTFT — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- lordhansolo's vLLM 0.29.1rc1 nightly overlay: 32 files, 9 ported vLLM PRs + 16 custom fixes incl. Mamba align-state retention and prompt-tail state for multi-turn prefix reuse, MTP shard prefilter (4 of 97 shards), pruned 32k draft vocab, pinned-host embed_tokens (1.18 GB off-GPU), SM120 small BF16 GEMMs for decode rows 40–64, exact CUDA graphs at 44 and 52 tokens, GDN RecoverSSM for MTP verify; rc2 was validated only on an RTX PRO 4000 laptop — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- sirikilohit chose SGLang because its prefix cache handles the hybrid full/linear attention mix and runs the native MTP head; "most public notebooks used vLLM" — [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md)

**Mamba prefix-cache retention (ARC-critical)**
- "Flash-Next needs both attention KV state and the relevant recurrent-state checkpoints for prefix reuse. Having enough KV capacity alone did not guarantee a cache hit." Franzen's patch keeps only the final prefill checkpoint (plus a limited branch checkpoint at end of system prompt) and refreshes its LRU position when decode finishes; needed because re-tokenization may not match generated tokens — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- Earlier Franzen demo run: 93.43% of prompt tokens reused; P90 effective prefill 10,552.6 tok/s; P90 aggregate decode 836.6 tok/s; harness-side generation 609.0 tok/s; prefill time fraction 15.25%; long-prompt cache miss rate 0.03% (1/3,248) — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- Franzen's server flags: `--mamba-radix-cache-strategy extra_buffer --mamba-track-interval 64 --max-mamba-cache-size 60 --mamba-ssm-dtype bfloat16 --page-size 64 --schedule-policy lpm --kv-cache-dtype fp8_e4m3 --gdn-mtp-cache-mode none`, linear-attn prefill/decode backend flashinfer, `--ple-offload-embedding` — [FRANZEN-NB](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/dfranzen/arc-agi-3-milestone-2-solution.ipynb)
- lordhansolo: prefix cache hit-rate median 91%, KV usage at peak 91% — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)

**FP8 KV**
- All three prize notebooks use `fp8_e4m3` KV — [SUMMARY](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md). sirikilohit's boot warns the FP8 KV has no scaling factors (`fp8_unscaled_warning=True`) — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- sirikilohit's jump 14.49 → 22.53 came from BF16 → FP8 KV (pool ~1.0M tokens) plus longer history (trim 57,344 → 45,056; context 49,152 → 69,632; 15 → 16 games). His earlier "FP8 hurt" result was actually caused by an MXFP8 re-quantization of non-expert layers that was "about 25% slower decoding" — [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md)
- Olympie: 76K needle middle-depth misses reproduced with BF16 KV — "model/QSA-inherent… not our fp8" — [OLY-STATUS](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/STATUS.md)

**Speculative decoding settings in prize notebooks**
- Franzen: NEXTN, 3 steps, eagle-topk 1, 4 draft tokens, albucino INT4 MTP draft (compressed-tensors), draft KV fp8, FR-Spec 64k hot-token map, **SPEC_ACCEPT_SINGLE=1.0 / SPEC_ACCEPT_ACC=1.0 (lossless)** — [FRANZEN-NB](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/dfranzen/arc-agi-3-milestone-2-solution.ipynb)
- lordhansolo: MTP 3 tokens, built-in NVFP4 MTP head, 32k draft vocab; acceptance 63–71%; sirikilohit: NEXTN 3 steps, RadixArk NVFP4 MTP draft. Median accepted draft length 2.7 / 2.9 / 2.6 — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)

### Inferences
- The SGLang route is better-proven for ARC (two of three prize notebooks, including the winner) mainly because of hybrid prefix-cache retention; vLLM with a large private patch overlay achieved comparable raw throughput and the largest KV pool, but carries higher maintenance risk (nightly + 32-file overlay).
- Franzen's stack did not use three measured single-stream levers that exist in the ecosystem: relaxed acceptance (0.3), online FP8/W8A16 for the dense stack, and fp8 lm_head/HC. Their combined benchmark effect in Olympie's build was roughly 148 → 231 tok/s C1 (+~55%), but much of it was measured at C1, not at 10 streams.

### Gaps
- No public measurement of Pennyroyal online FP8 on the Intel W4A16 (GPTQ/Marlin) checkpoint; unclear whether it boots (doc says unsupported shapes fail loud).
- No published head-to-head of SGLang vs vLLM on the *same* ARC workload with the same checkpoint.
- mratsim patch list could not be enumerated (GitHub API returned nothing).

---

## Q3. Concrete numbers from the three Milestone-2 notebooks

### Takeaway
The winner (dfranzen, 27.89) had the *lowest* peak throughput (946 tok/s) but the fewest streams (10), the longest retained context (~59k→118k), and the highest per-stream decode (~95 tok/s). More streams (14–16) raised peak aggregate only ~20%.

### Cited Findings
(All from [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md) and [SUMMARY](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md) unless noted; measured from Save & Run demo logs on 2026-09-30, not the scored reruns.)

| Metric | dfranzen | lordhansolo | sirikilohit |
|---|---|---|---|
| Public LB | 27.89 | 23.84 | 22.53 |
| Server | SGLang Pennyroyal v2.5.3 | vLLM 0.29.1rc1 nightly e975732 | SGLang Pennyroyal v2.5.0 |
| Checkpoint | Intel W4A16 + BF16 PLE; albucino INT4 MTP draft | primitive-ai mixed NVFP4-FP8 + BF16 PLE, built-in NVFP4 MTP | Intel W4A16 + RadixArk FP8 PLE; RadixArk NVFP4 MTP draft |
| MoE backend | auto (Marlin) | auto (flashinfer_cutlass) | auto (Marlin), draft flashinfer_cutlass |
| Weights on GPU | 73.64 GB | 71.94 GB | 73.57 GB |
| KV + Mamba on GPU | 15.94 GB (11.58 target KV, 0.96 draft KV, 3.40 Mamba) | 19.69 GB | 16.97 GB (11.50, 0.96, 4.51) |
| CUDA graphs | 1.14 GB | 0.46 GB | 1.59 GB |
| GPU free | 4.25 GB | 1.90 GB | 3.17 GB |
| Host offload | 95.37 GB BF16 PLE | 95.37 GB BF16 PLE + 1.18 GB embed_tokens | 47.68 GB FP8 PLE + 48 GB HiCache |
| Pool sizing | mem fraction 0.96 | gpu util 0.98, profiled | 0.97 + 48 GB host tier |
| KV pool (tokens) | 1,011,264 | 1,417,100 | 1,004,288 |
| Context server / harness | 139,264 / 131,072 | 147,072 / 127,488 | 69,632 / 69,632 |
| Trim rule | at ~118k drop to ~59k | at ~126k drop to 81,536 | 57k → 45k |
| Server slots (streams) | 10 | 14 | 16 |
| Games admitted | 110 (priority gate) | 14 | 28 |
| Prefill chunk | 8,192 (max prefill 16,384) | 2,048 | 4,096 |
| CUDA graph bs | 1,2,4,7,8,9,10 | token sizes up to 56 | 1–8,10,12,14,16 |
| Mamba cache | 60 | shared with KV | 80 |
| Schedule policy | lpm | async | default |
| Board image / tokens per board | 640 px / ~402 | 256 px / ~66 | 256 px / 66 |
| Tool output cap | 3,072 | 1,024 | 1,024 |
| Worst case tokens all slots full | 1.39M | 2.06M | 1.11M |
| Peak decode tok/s | 946 | 1,135 | 1,159 |
| p90 / median decode tok/s | 833 / 722 | 1,056 / 976 | 1,039 / 899 |
| Per-stream at peak | ~95 | ~81 | ~72 |
| Median accepted draft length | 2.7 | 2.9 | 2.6 |
| Job-wide generated tok/s | 588 | 933 | 688 |
| Notebook start → ready | 531 s | 544 s | 615 s |
| Server launch → ready (weight load) | 478 s (269 s) | 430 s (240 + 13 s) | 536 s (215 + 47 s) |
| Temperature | 0.7 | 0.6 | 0.6 |

- Notes from COMPARISON: SGLang peaks are single-batch readings while vLLM's are 10-s averages; job-wide tok/s includes boot and idle; "Peak throughput tracks the number of concurrent requests more than the server"; "The top score belongs to the build with the fewest server slots and the longest per-slot context" — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- Franzen's write-up settings: 10 streams, 128 Ki harness window, 12 Ki max output, 136 Ki server limit, 58 Ki drain, FP8 E4M3 KV, 60 Mamba slots, mem fraction 0.96, chunked prefill 8,192, 3 speculative steps — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- Franzen's 5 server patches: low-M BF16 GEMM (from Olympie 0004), speculative-state budget correction (from mratsim 0002), Marlin scale-dtype fix, prefix-cache retention, bounded checkpoint prefetch with one-shard lookahead (4 threads, 16 MiB blocks default) plus resharding of the checkpoint — [FRANZEN-SERVE](https://github.com/da-fr/arc-agi-3-solution/blob/main/serving/README.md)
- Franzen yields per turn after 2,048 generated tokens (not elapsed seconds) — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- Startup tricks: Franzen warms up with one RESET per game while the server loads and the harness retries HTTP for 900 s; 12-min startup deadline. sirikilohit: 16-thread PLE row copy, draft-only MTP folder (3 shards instead of 206), restored compiled-kernel caches — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- sirikilohit: "the cache pool was 91-97% full all run, fewer requests ran than allowed, and the rest queued for cache space. Memory was a bottleneck." — [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md)

### Inferences
- Franzen's 10 streams × steady-state 60–118k tokens ≈ 0.6–1.2M tokens of resident context vs a 1.01M pool, so his pool is roughly saturated at 10 streams; adding streams without adding pool would force shorter context or more evictions (which his design explicitly avoids).
- Job-wide 588 tok/s over a 32,400 s notebook ≈ 19M generated tokens total ≈ ~170k generated tokens per game across 110 games (my arithmetic; demo-run rate may differ from the scored run).
- The gap between Franzen's median decode (722) and job-wide (588) is ~19%: boot (~531 s, ~1.6% of 9h), tool-call gaps, prefill (~15% of wall time), and tail when few games remain.

### Gaps
- Scored competition-rerun logs are not public; all measured numbers are from short demo runs (Franzen's was 10 games × 25 min).
- Franzen had not completed a full demo run with the final config at write-up time — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md).

---

## Q4. Levers most likely to add throughput beyond Franzen's setup, and risks

### Takeaway
Most promising, in rough order of (expected gain ÷ risk): (1) shrink the dense BF16 stack via online FP8/W8A16 (+15–39% measured on NVFP4, frees or costs ~3–4 GB depending on implementation; compatibility with W4A16 unverified); (2) relaxed MTP acceptance (+13–29% C1, lossy sampling); (3) smaller MTP draft to grow KV pool (~+200k tokens); (4) modest stream increase (10→12–14) only if KV pool grows in step; (5) squeeze free VRAM (4.25 GB free). Deeper draft (>4 tokens) and torch.compile are closed.

### Cited Findings
- Online FP8 dense stack: +28.3% C1 short, +15–39% C4 aggregate; frees ~3.86 GiB; qualified only on ModelOpt NVFP4 checkpoint — [PENNY-FP8](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/FP8.md). Olympie's W8A16 approach instead adds ~3.6 GB fp8 copies — [OLY-STATUS](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/STATUS.md). primitive-ai FP8 attention/GDN: +13% single / +8.7% at C32 with no measured quality loss — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- Counter-evidence: sirikilohit's MXFP8 re-quantization of non-expert layers made decoding ~25% *slower* and coincided with a score drop in his setup — [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md) (conflicts with Pennyroyal/Olympie gains; different implementation/build likely).
- Relaxed acceptance: 1.0 → 0.5 → 0.3 gives 179 → 203 → 231 tok/s C1; lossy at temp>0 — [OLY-STATUS](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/STATUS.md). Franzen ran 1.0/1.0 — [FRANZEN-NB](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/dfranzen/arc-agi-3-milestone-2-solution.ipynb)
- Smaller draft head: NVFP4 MTP 1.42 GB vs BF16 5.03 GB grows the pool by ~48% at ~1% speed cost — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8); Franzen's INT4 draft is 3.79 GB on GPU — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- Pool-maximization tricks used by lordhansolo: gpu util 0.98 with profiling, embed_tokens pinned on host (1.18 GB), smaller CUDA graph footprint (0.46 GB) → 1,417,100 tokens vs Franzen's 1,011,264 — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md). Franzen left 4.25 GB free — same source.
- Pennyroyal tested an explicit 1,000,000-token pool with online FP8, leaving 5.21 GiB after graphs — [PENNY-FP8](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/FP8.md)
- Stream scaling in benchmarks: Olympie C4 620 → C8 758 (+22%); mratsim C4 ~800 → C8 1,170 (+46%); prize notebooks 10 → 14 → 16 streams gave 946 → 1,135 → 1,159 peak — [OLY](https://github.com/gabrielolympie/sglang-flashnext-sm120); [MRATSIM](https://github.com/mratsim/sglang-qwen38fn-sm120-turbo); [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- Mamba cache must be ~6× max running requests or spec CUDA graphs silently cap at bs=4 — [OLY](https://github.com/gabrielolympie/sglang-flashnext-sm120) (Franzen: 60 for 10 = 6×; sirikilohit: 80 for 16 = 5×).
- Draft tokens capped at 4 by QSA compress ratio; torch.compile fails — [OLY-PERF](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/PERF_CEILING.md)
- FR-Spec hot tokens: +4.5–9% (already used by Franzen with 64k map) — [PENNY-RES](https://github.com/jpezzulli/sglang-rtxpro6000/blob/master/RESULTS.md); [OLY-STATUS](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/STATUS.md)
- MoE backend: Marlin is auto for W4A16; for NVFP4, Marlin +10% single-stream but −1–3% at C32 (vLLM) — [HF-PRIM](https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8)
- Prefill share: 15.25% of wall time with 93.43% reuse; P90 prefill 10.5K tok/s — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md). Chunk sizes used: 8,192 / 2,048 / 4,096 — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- Trim hysteresis is key to keeping the prefix cache hot (Franzen drop to ~59k; sirikilohit "fewer, larger trims keep the prefix cache useful") — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md); [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md)
- sirikilohit resume re-prefill: slice length raised from 300 s to 2,400 s because "resume re-prefill costs ~10% of the GPU on 110 games" — [SIRI-UCB](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/af105202327dcf35bd670a50b2558adab12e8dd3/cells/44_patch_cell_v16_7_m72_one_pool_ucb_scheduler.py)
- Operational gotchas: keep `--cuda-graph-max-bs` small, `MAX_JOBS=4` for JIT, first bench after restart is JIT-polluted — [OLY-STATUS](https://github.com/gabrielolympie/sglang-flashnext-sm120/blob/main/docs/STATUS.md). Disabling flags via comments in launch args silently dropped them in one sirikilohit build; he added an argument-match check — [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md)

### Inferences
- Throughput per stream matters as much as aggregate: the winner had the highest per-stream rate and the longest context; more streams dilute per-game context unless the pool grows. Levers that raise *per-step speed* (FP8 dense stack, relaxed acceptance) are therefore more attractive than more streams.
- A realistic combined target: +15–30% aggregate decode at 10 streams from FP8 dense stack (if it works with the W4A16 checkpoint or by switching back to NVFP4 + online FP8), plus +10–25% from relaxed acceptance at temperature 0.7 — but relaxed acceptance changes the sampling distribution (sharper), which is an untested risk for agent quality on ARC; validate with matched-token comparisons as sirikilohit recommends.
- Pool gains (~+200k from smaller draft, ~+150–350k from using some of the 4.25 GB free and host-pinning embed_tokens) could support either 12 streams at Franzen's context or longer context at 10 streams. Evidence (sirikilohit's jump, Franzen's TL;DR) suggests longer context per game has been the more valuable use of memory so far.
- Risks: OOM from image-heavy prompts at high memory fraction (Franzen uses 640-px boards ~402 tokens each); online FP8 failing loud on unsupported checkpoints; untested nightly builds; Kaggle-quota-limited validation with large run-to-run variance (same notebook 5.02/5.50/6.42).

### Gaps
- No measurement of relaxed acceptance or online FP8 on an ARC workload, or at 10 concurrent streams with ~100k contexts.
- No published measurement of Pennyroyal v2.5.3 with HiCache tier enabled on the Kaggle box for ARC (sirikilohit used 48 GB host tier but no isolated gain reported).

---

## Q5. Scheduling compute across ~110 games in a 9-hour budget

### Takeaway
Two adaptive schedulers are public: Franzen's priority gate P = (A+B)·C with 10 admitted streams and handover at context-trim time, and sirikilohit's one-pool UCB (2,400 s slices, ported from Wang). Evidence on "more time per game keeps helping" is mixed: Franzen says scores were still improving near the end of runs and his calibration shows completion chance decaying with actions/tokens spent on a level; sirikilohit found level-clear chance did *not* fall with time spent on a level, but that games stagnate later; the UCB scheduler's source reported no isolated score gain.

### Cited Findings
- Franzen: all 110 games started simultaneously; scheduler admits 10 active games; others wait with frozen state; finished games' budget is redistributed automatically. Priority P = (A+B)·C, A = ℓ·(25/(25+a))²·55/(N(N+1)/2), C = 0.25·2^(−(a/115)²) + 0.75·2^(−(t/62000)²); B lookup by levels remaining after current (≥3: 8, 2: 7, 1: 5, 0: 0); B faded linearly to 0 in last 20% of runtime; N clipped 6–10 — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- C was calibrated from 725 observed level attempts (557 completed, 168 unfinished) across four runs; a Gaussian falloff fit better than exponential — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- Handover only at context eviction (prefix already changed), to preserve prefix reuse — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md). Per-game runtime 31,920 s shared out of a 32,400 s notebook budget — [COMPARISON](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/COMPARISON.md)
- "More elaborate priority rules" (pace adjustment, empirical continuation lookup) did not show a clear advantage — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- Franzen TL;DR: "With scores still improving near the end of runs, increasing token throughput remained a promising way to improve the score." — [FRANZEN-WU](https://github.com/da-fr/arc-agi-3-solution/blob/main/WRITEUP.md)
- sirikilohit UCB: shared ~31k s pool; warm-up gives every game one slice (now 2,400 s, originally 300 s); then each free slot goes to max UCB = priority + c·sqrt(log(1+minutes elapsed)/actions), c = 0.0002; priority = 0.5·(levels-per-token over lifetime + over last 32k generated tokens), levels weighted triangularly L(L+1)/2; games keep agent, history and sandbox between slices — [SIRI-UCB](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/af105202327dcf35bd670a50b2558adab12e8dd3/cells/44_patch_cell_v16_7_m72_one_pool_ucb_scheduler.py)
- The UCB source team's own note: "no score gain was measured for the scheduler in isolation"; sirikilohit's local 25-game score (~12.04) was ~2× board score (5.02/5.50, 110 games in 4 waves of 28) for the old fixed-clock version — [SIRI-UCB](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/af105202327dcf35bd670a50b2558adab12e8dd3/cells/44_patch_cell_v16_7_m72_one_pool_ucb_scheduler.py)
- sirikilohit: "Restarting a stuck level with a fresh context… The chance of clearing a level didn't fall with time spent on it, so a fresh start bought nothing"; but held back priority scheduling because "games stagnate in their later stages (level clears per unit of time fall off), so moving time between games would mostly move stagnant time"; "The first 30 minutes of a run say little about the result"; variance: same notebook 5.02, 5.50, 6.42 — [SIRI-WU](https://github.com/LohitSiriki/arc-agi-3-milestone2-solution/blob/main/WRITEUP.md)
- lordhansolo: fixed 3,918 s cap per game, 14 at once, ~8 waves over 110 games, with a strategy-audit prompt once a level used 25% of the game's time — [SUMMARY](https://github.com/tonghuikang/daniel-franzen-arc-agi-3/blob/main/kaggle/SUMMARY.md)
- Per-game time arithmetic implied by the configs: Franzen 10 slots × 31,920 s / 110 ≈ 2,900 slot-seconds per game on average (my arithmetic); lordhansolo 3,918 s per game.

### Inferences
- The winner used the adaptive scheduler, but it was bundled with many other changes; no clean ablation isolates the scheduler's contribution.
- The two observations are reconcilable: per-level completion hazard decays with spend on that level (Franzen's C), while across the whole game, games that are progressing keep progressing — so the useful marginal compute goes to games currently clearing levels, which is what both A·C and UCB's recent levels-per-token reward. Because scores were still rising at the end of 9-hour runs (Franzen), raw throughput gains likely convert into score.
- Keep handovers rare (Franzen: at trim; sirikilohit: 2,400 s slices) because each resume costs a re-prefill (~10% of GPU at 300 s slices on 110 games).

### Gaps
- No public curve of score vs. per-game time (e.g., same config at 1×, 1.5×, 2× budget) was found.
- Tufa Labs' technical write-up (Kaggle discussion 717133) could not be fetched (page returned no content), so Tufa's own throughput/scheduling numbers are missing.
