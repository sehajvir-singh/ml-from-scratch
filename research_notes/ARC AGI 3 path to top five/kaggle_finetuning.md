# Fine-tuning the ARC-AGI-3 agent model on Kaggle-only compute (as of 2026-09-25)

**Bottom line for the report writer:** With Kaggle compute only, fine-tuning **Qwen3.8-Flash-Next** is not feasible before Nov 2, 2026. The NVFP4 weights leave almost no training headroom on the 96 GB card. No training framework supports this architecture with a 4-bit MoE base. Nobody reports doing it on an RTX PRO 6000, and the one competitor who trained it used a full H200 node. Fine-tuning a **smaller model** (Qwen3.8-27B) is feasible on Kaggle, and Thuitanium's `thui-lora` already did it. However, that model starts at roughly 1.2–1.7 hidden, against about 4 for Flash-Next. The best public LoRA gain was +0.69 hidden (1.25 → 1.94), and Thuitanium's own careful LoRA made held-out games worse. A fine-tuned 27B therefore has no realistic path to beating the served Flash-Next. The recommendation is **"not feasible / not worth the quota."** The one exception is a cheap serving smoke test, described in Q3 and Q7, to keep a Flash-Next adapter path open in case a training route appears.

Sources are labelled [OFFICIAL] for host or vendor text, [CODE] for repo contents, and [COMMUNITY] for participant claims. Kaggle discussions were read verbatim through Kaggle's internal JSON endpoint (`discussions.DiscussionsService/GetForumTopicById`).

## Q1. What Kaggle compute does one user get (RTX PRO 6000, TPU, T4×2, P100)?

### Takeaway
One user gets about **30 GPU-hours per week**, shared across all GPU types. The RTX PRO 6000 "burns quota faster", by an unpublished factor. Sessions last at most **about 9 h**, not 12 h. Two sessions can run at once, and RTX queues have recently lasted up to 12 h. A **TPU v5e-8** is also available, with about 20 h/week, 128 GB total HBM and about 9 h sessions. It is proven for inference but has no ARC-relevant training recipe. T4×2 and P100 are useless for training any candidate model.

### Cited Findings
- **Session length.** The ARC-AGI-3 code rules say "GPU Notebook <= 9 hours run-time; Internet access disabled". The host confirmed "For v3 it is 9hrs. Where do you see 12 hours?" [OFFICIAL] — [Code Requirements](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/code-requirements); [discussion 729985](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/729985) (via prior notes `rules_infra_sdk.md`). The competition metadata sets `maxGpuRuntimeMinutes: 540` — [competition page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3) (via prior notes).
- **Accelerators.** Four are offered: CPU, T4×2 (the default), P100, and "RTX 6000" (`g4-standard-48`, the 96 GB RTX PRO 6000 Blackwell). The RTX is "ARC-AGI-3 exclusive, burns GPU quota faster" [OFFICIAL] — [ARC-AGI-3-Kaggle-Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter); [docs.arcprize.org](https://docs.arcprize.org/arc-prize-2026). The kernel metadata uses `"machine_shape": "NvidiaRtxPro6000"` [CODE] — [Thuitanium thui-lora/train/kernel-metadata.json](https://github.com/Sahasawatt/arc-agi-3-agent/tree/main/thui-lora).
- **Weekly quota.** A participant says "when I reach the 30-hour GPU limit". A linked Colab Pro subscription adds "extra 15 hour GPU quota", which is paid and outside the user's Kaggle-only constraint. A new version needs some free quota to start, but the scored competition rerun does not consume quota [COMMUNITY] — [discussion 734585](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734585). An aggregator also reports about 30 h/week shared across GPU types — [aimultiple](https://aimultiple.com/free-cloud-gpu).
- **Queues and concurrency.** One thread reports RTX queues of "11 hours, and still being queued" and "Almost 12 HOURS" (2026-09-21), and says the allowed concurrency is 2 RTX sessions per user. Staff replied: "Capacity is restored… Queue has fully cleared" (2026-09-22). The thread blames part of the load on non-ARC training jobs running on the RTX [COMMUNITY + STAFF reply] — [discussion 742148](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742148). Earlier reports describe the RTX accelerator as "flaking… on, then off" — [discussion 724890](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/724890).
- **Submissions.** One submission per day is allowed [OFFICIAL] — prior notes `rules_infra_sdk.md` (citing the Kaggle competition settings). Participants say you need "at least like 5" submissions to judge a notebook version because hidden variance is large — [discussion 732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).
- **TPU.** Kaggle announced "New TPU v5e-8s! Phasing out v3-8s" — [Kaggle product announcement 607202](https://www.kaggle.com/product-announcements/607202). The CLI accelerator ID is `TpuV5E8` — [kaggle-cli PR #1198](https://github.com/Kaggle/kaggle-cli/pull/1198). A community project reports "around 20 TPU hours a week" and sessions of "a little under nine hours". It serves Qwen3.8-27B in bf16 at about 130 tok/s for one stream and about 540 tok/s at 8 streams, using vllm-tpu, and GLM-5.3-Flash (320B MoE) with its own JAX engine. It covers **inference only** — [ARahim3/kaggle-tpu-lab](https://github.com/ARahim3/kaggle-tpu-lab). A search snippet says vllm-tpu 0.28.0 shipped Pallas kernels for DeltaNet layers (Aug 2026); this was not verified at the primary source — [Kitkitkittt/kaggle-tpu-lab (search result)](https://github.com/Kitkitkittt/kaggle-tpu-lab).
- **TPU v5e HBM.** Google Cloud's spec is 16 GB HBM per v5e chip, so a v5e-8 has 128 GB in total. This is from Google's v5e documentation and was not re-fetched in this session — [Cloud TPU v5e docs](https://cloud.google.com/tpu/docs/v5e).
- **T4 and P100.** A T4 has 16 GB, sm_75, and no bf16 or FP8. vLLM runs on T4 only in FP16. A P100 (sm_60) is not supported by vLLM — prior notes `open_models_inference.md` (sources cited there).

### Inferences
- If the RTX multiplier were 2×, which is an unverified guess, the 30 h/week budget would give only about 15 RTX-hours per week. That is fewer than two 9 h sessions. Thuitanium's training run alone took about 7 h (see Q5). **Quota, not VRAM, becomes the second binding constraint** for any training plan.
- A TPU v5e-8 could run a Qwen3.8-27B bf16 LoRA in terms of memory: about 54 GB of weights out of 128 GB of HBM. The obstacle is software. Nobody has published a JAX or PyTorch/XLA training implementation of the Gated-DeltaNet hybrid `qwen3_5` or `qwen4_exp` architectures on Kaggle TPUs, so building one would itself be a multi-week project. Flash-Next in bf16 (about 250 GB, plus 51B n-gram parameters) does not fit on a v5e-8.
- T4×2 and P100 can at most do CPU-side work such as game simulation, data cleaning and tokenization. They can also QLoRA models of 4B parameters or smaller, but such models do not matter for this competition.

### Gaps
- There is no official number for the RTX PRO 6000 quota multiplier, and no official statement of the weekly GPU quota for Sep–Oct 2026. The 30 h figure is community-reported.
- I could not load the text of Kaggle's TPU documentation (the page rendered empty), so the 20 h/week TPU quota comes from a community repository. I found no evidence that a TPU v6e is offered on Kaggle notebooks.
- It is unknown whether TPU quota and GPU quota are independent. Historically they were separate.

## Q2. Can Qwen3.8-Flash-Next, or a MoE of that size, be LoRA/QLoRA fine-tuned on one 96 GB card?

### Takeaway
**No, not in practice.** The NVFP4 checkpoint leaves only about 15–20 GB of headroom, and no training stack supports this architecture on a 4-bit MoE base. Unsloth, PEFT with bitsandbytes, torchtune and ms-swift all lack a supported path to train `qwen4_exp` with modelopt-NVFP4 frozen experts. Unsloth advises against 4-bit MoE QLoRA even for supported models. A bf16 LoRA would need more than 250 GB. Offloading experts to the 180 GB of host RAM does not rescue it. The only public report of training Flash-Next used a full H200 node and says the RTX 6000 Pro "can not be used".

### Cited Findings
- **Architecture.** `Qwen4ExpForConditionalGeneration`, `model_type: qwen4_exp`. It has 48 layers laid out as 12 × (3 Gated DeltaNet + 1 Qwen Sparse Attention), each followed by a MoE. Each MoE has 512 experts with 10 routed + 1 shared active and expert intermediate size 640, and the hidden size is 2560. Other features are Gated Residual (4 branches, rank 320) and n-gram embeddings. Parameters: "125B with 6B activated, plus 51B n-gram embedding and 4B MTP". Required `transformers_version: 5.8.0.dev0`. License `qwen-community-1.0`, not Apache — [Qwen/Qwen3.8-Flash-Next config.json and README](https://huggingface.co/Qwen/Qwen3.8-Flash-Next).
- **The served NVFP4 checkpoint.** `RadixArk/Qwen3.8-Flash-Next-NVFP4` is `quant_method: modelopt`, `quant_algo: NVFP4`, with W4A4 FP4 and group size 16, produced by modelopt 0.46.0. Several module groups are **excluded from quantization** and stay bf16: `*.self_attn.*`, `*.linear_attn.*`, `*.mlp.gate*`, `*.mlp.shared_expert.*`, `*hyper_connection*`, `*.ple.*`, the vision tower, the embeddings, `lm_head` and MTP. The n-gram (PLE) embeddings are stored in `float8_e4m3fn`. Only the routed experts are FP4 — [RadixArk/Qwen3.8-Flash-Next-NVFP4 config.json](https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4).
- **Fitting inference alone** already requires FP4 plus host-offloaded n-gram embeddings: "fits the RTX PRO 6000 only via FP4 + host-offloaded N-gram embeddings" [COMMUNITY] — [discussion 743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060) (via prior notes). The public serving profile uses "KV cache 5 GiB", which shows how little VRAM remains — prior notes `kaggle_top_approaches.md` (keithtyser/wuliao0 notebooks).
- **Direct statements.**
  - "I successfully built and validated rl training pipeline of Qwen 3.8 Next Flash based miles, but I did not gain any performance… I used a full H200 node. rtx 6000 pro can not be used for training of any ~100B model even with aggressive cpu offload and quantization" [COMMUNITY] — [discussion 742835](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742835).
  - "SFT on flash-next nvfp4 is nearly impossible with 96g RTX PRO 6000, at least for most of us" (Ya Xu).
  - "RL is possible for the qwen 3.8 27b after high quantization… but on the flash next model its impossible unless you are an nvidia guy" (OverfitOracle).
  - Both from [discussion 732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854). The 742835 thread author also writes: "I know that the RTX Pro is more than capable of finetuning Qwen 3.8 27B, but the gap in capability between 27B and flash next is quite large" — [742835](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742835).
- **Unsloth, MoE.** Supported MoE families are Qwen3 (30B-A3B etc.), gpt-oss, GLM 4.5–4.7 and DeepSeek V3.x; Qwen3.5/3.6/3.8 MoE and Qwen3-Next are not listed. "Training MoE models in 4-bit QLoRA isn't recommended right now because BitsandBytes doesn't support it." LoRA on expert `gate_up_proj`/`down_proj` is supported, and the router is frozen by default. Measured bf16 LoRA VRAM: Qwen3-30B-A3B 80.9–85.5 GB; gpt-oss-20b 40.9–55.1 GB — [Unsloth: Faster MoE](https://unsloth.ai/docs/basics/faster-moe).
- **Unsloth, Qwen3.5.** "Qwen3.5-35B-A3B – bf16 LoRA works on 74GB VRAM"; "Qwen3.5-122B-A10B – bf16 LoRA works on 256GB VRAM"; dense 27B bf16 LoRA 56 GB. "It is not recommended to do QLoRA (4-bit) training on the Qwen3.5 models, no matter MoE or dense, due to higher than normal quantization differences" — [Unsloth Qwen3.5 fine-tune guide](https://unsloth.ai/docs/models/qwen3.5/fine-tune).
- **Search result.** Unsloth's Qwen3-Next (80B) page says it "fits on a single B200 GPU in bf16 LoRA" — [Unsloth Qwen3-Coder-Next](https://unsloth.ai/docs/models/qwen3-coder-next) (search snippet).
- **Host hardware.** The g4-standard-48 has about 180 GB of host RAM. Offloading n-gram embeddings "is untested" for inference, per prior notes — `open_models_inference.md`.

### Inferences
- **Memory arithmetic** (my estimate from the config):
  - Routed experts: 512 × 48 layers × 3 matrices × 2560 × 640 ≈ 121B parameters. At NVFP4 (about 4.5 bits per weight with FP8 scales per 16 values) that is **about 68 GB**.
  - bf16 non-expert modules (attention, DeltaNet, shared experts, hyper-connections, lm_head, vision tower): roughly 4–6B parameters, so **about 8–12 GB**.
  - The 51B FP8 n-gram table (about 51 GB) must live in host RAM.
  - Static GPU memory is therefore about 76–80 GB, leaving about 15–20 GB for LoRA weights, optimizer states, activations with gradient checkpointing, and the fp32 logits. The logits alone take about 4 GB at a 4K sequence length with a 248K vocabulary.
  - Compare Thuitanium's 27B FP8 run (about 28 GB of weights). It still hit OOM at 8,192 tokens and had to cap at 4,096 (Q5). Flash-Next would have about a third of that headroom.
- **Software is the harder blocker.** Training LoRA on the bf16 modules (attention, linear_attn, shared_expert) while freezing FP4 experts needs a differentiable NVFP4 grouped-GEMM: the input gradient of the frozen FP4 experts must flow backward. vLLM's NVFP4 MoE kernels are inference-only. PEFT/bitsandbytes cannot load modelopt NVFP4 as a trainable base. Unsloth does not list `qwen4_exp`. Someone would have to write the backward kernels, the DeltaNet/QSA training path and the n-gram-offload-under-autograd path, then debug them on a card that is quota-limited and queue-limited. That cannot be done in 5 weeks with a free-tier budget.
- **Expert offload to 180 GB host RAM.** bf16 experts (about 242 GB) do not fit in host RAM at all. NVFP4 experts do fit in host RAM, but streaming about 68 GB over PCIe for every forward and backward pass takes several seconds per micro-step even at best-case bandwidth. That turns a small SFT into days of compute and still needs the missing FP4 autograd path. Offload helps inference, not training.
- **The plausible intermediate target.** A "35B-A3B-class" MoE (Qwen3.6-35B-A3B) fits a bf16 LoRA on one 96 GB card (about 74 GB per Unsloth's Qwen3.5-35B-A3B figure). But sonpham-org found 35B MoE swaps "underperformed significantly" in the Duck harness (Q4). So feasibility of training does not translate into a better agent.

### Gaps
- I did not verify whether NVIDIA Transformer Engine or ModelOpt offers an NVFP4 QAT/LoRA backward pass on sm_120 (RTX PRO 6000) that could be adapted. If one exists, the software blocker is smaller than stated, but the VRAM headroom problem remains.
- No one has published a measured VRAM figure for any Flash-Next training attempt on 96 GB.
- The Qwen3.8-Flash-Next tech report (whether it lists Muon parameters or fine-tuning guidance) was not read.

## Q3. Could an adapter be served by the pinned vLLM runtime (LoRA on MoE, modelopt_fp4)?

### Takeaway
**Unproven for Flash-Next.** vLLM supports MoE-expert LoRA in general. Thuitanium proved on Kaggle that an FP8-base Qwen3.8-27B with a LoRA serves on vLLM 0.19. But nobody has shown a LoRA served on the `qwen4_exp` NVFP4 checkpoint. The Duck repo's `vllm_runtime_lora_guard` exists precisely because vLLM **silently drops** adapter modules it does not support. The only near-term low-risk target would be an attention/DeltaNet-only adapter, since those modules are bf16 in the NVFP4 checkpoint. It must be smoke-tested with a B=0 identity adapter before any training.

### Cited Findings
- **vLLM docs.** They describe MoE LoRA adapters in 2D (megatron) and 3D (peft) formats, `--enable-mixed-moe-lora-format`, `--max-lora-rank` ("Avoid setting it too high… wastes memory"), and `--lora-target-modules` for restricting targets. The LoRA page does **not** state compatibility with quantized bases (FP8, modelopt, NVFP4) — [vLLM LoRA docs](https://docs.vllm.ai/en/latest/features/lora.html). vLLM also ships "LoRA-aware FlashInfer TRT-LLM MoE experts in BF16" (search snippet) — [vLLM fused_moe experts API](https://docs.vllm.ai/en/latest/api/vllm/model_executor/layers/fused_moe/experts/).
- **The Duck guard** [CODE] — [Tufalabs/duck-harness `ARC3-Inference/inference/tools/vllm_runtime_lora_guard.py`](https://github.com/Tufalabs/duck-harness).
  - It hooks `vllm.lora.worker_manager.logger.warning_once`.
  - It turns vLLM's warnings "not in the model's supported LoRA target modules" and "not in the deployment-time target_modules restriction" into a `RuntimeError`, unless the module is an expected child of a packed runtime module.
  - The packed aliases are `qkv_proj→q/k/v_proj`, `gate_up_proj→gate/up_proj`, `in_proj_ba→in_proj_b/in_proj_a` (the DeltaNet input projection) and `linear_fc1→gate/up_proj`.
  - This shows Tufa hit silent module-dropping on the hybrid DeltaNet architecture.
- **Thuitanium `thui-lora-v0` smoke** [CODE + results]. It ran vLLM 0.19 with Qwen3.8-27B-FP8 and `--enable-lora --lora-modules smoke=<dir>`. The adapter was a rank-8 dummy with B=0 on the `q_proj`/`v_proj` of the **16 full-attention layers only**, because "48 are linear_attention with no q_proj/v_proj". Results: P1 (served in `/v1/models`) PASS, P2 (chat completion via the adapter) PASS, P3 (agent plays with the adapter mounted) PASS. "FP8 base + LoRA adapter serves on this stack." Its rationale notes that "FP8-base + LoRA is a pairing that has genuinely broken in some vLLM versions" — [Sahasawatt/arc-agi-3-agent `thui-lora/build_notebook.py`, `agents/thui/lora/thui-lora-v0.md`](https://github.com/Sahasawatt/arc-agi-3-agent).
- **Merging gotcha.** For the multimodal Qwen3.6, "merge/serve as Qwen3_5ForConditionalGeneration (a text-only save gets rejected by vLLM), and copy the processor configs into the merged checkpoint" [COMMUNITY] — [discussion 739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047).
- **Current serving profile.** The public Flash-Next profile uses ModelOpt NVFP4 with 3-token NEXTN MTP speculative decoding and CUDA graphs — prior notes `kaggle_top_approaches.md`.

### Inferences
- Merging a LoRA into the Flash-Next weights would require re-running ModelOpt NVFP4 quantization on a 125B bf16 model. That needs more than 250 GB of memory, which is impossible on Kaggle. So an adapter would have to be served unmerged.
- An unmerged adapter would be limited to modules vLLM's `qwen4_exp` implementation registers as LoRA-capable. Whether that class declares `SupportsLoRA` at all is unverified. Unmerged LoRA also adds per-token overhead and may conflict with MTP speculative decoding and CUDA graphs. Throughput is the binding constraint in this competition (every Duck game ends on the clock), so any slowdown is a direct score cost.
- If anyone does pursue this, the first step should copy Thuitanium's approach: a B=0 dummy adapter on Flash-Next's bf16 `self_attn` (and optionally `linear_attn` via `in_proj_*`), served with the Duck guard installed, with a tok/s comparison against no adapter. That costs about 1–2 RTX-hours and settles the serving risk before any training effort.

### Gaps
- It is unverified whether the vLLM version pinned in our Flash-Next wheelhouse supports LoRA for `qwen4_exp`, or together with `modelopt` NVFP4, MTP and CUDA graphs. There is no public smoke result.
- I found no measured LoRA serving overhead on Blackwell for this model.

## Q4. Alternative: fine-tune a smaller dense or MoE model. What would it need to beat Flash-Next?

### Takeaway
A 27B LoRA is **feasible on Kaggle** (proven) but **not competitive**. The 27B Duck lineage scores about 1.2–1.7 hidden against about 4 for Flash-Next. To beat Flash-Next, a fine-tuned 27B would need roughly a **2.5–3.5× hidden gain at similar or lower throughput**. The best published LoRA gain is about 1.55× (1.25 → 1.94, on a much weaker base), and Thuitanium's own LoRA was negative on held-out games. Gemma-4-31B and 35B-A3B MoEs are weaker than the 27B in this harness.

### Cited Findings
- **27B hidden scores.** Thuitanium's ledger records the 27B Duck (anim bundle + Qwen3.8-27B, "v10out") at **public 4.55 / hidden 1.70**, and the AVO arm on 27B at **public 4.32 / hidden 1.15** [CODE/ledger] — [Sahasawatt/arc-agi-3-agent `notes/LEDGER-all-runs.md`](https://github.com/Sahasawatt/arc-agi-3-agent). The same notes conclude that "the harness lane is model-bound at our model class" — `notes/B60-exploration-prior-design.md` (same repo).
- **Flash-Next vs 27B.**
  - "On the seven games the 27B never clears, Flash-Next clears every one at matched clock" — [sonpham-org/arc-3 HARNESS-NOTES.md](https://github.com/sonpham-org/arc-3) (via prior notes).
  - Public Flash-Next Duck notebooks score 3.38–4.50 on the LB — prior notes `kaggle_top_approaches.md`.
  - The 742835 author: "the gap in capability between 27B and flash next is quite large in my experiments" — [742835](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742835).
  - Model card benchmarks: Flash-Next vs 27B on DeepSWE 58.7 vs 42.2, JobBench 55.7 vs 33.4, and SWE-bench Pro 62.5 vs 61.7 — [Qwen3.8-Flash-Next card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next).
- **Other small models.** sonpham-org reports that "Attempted swaps (35B MoE, GLM-4.6V, Gemma-31B) all underperformed significantly, with scores ranging 0.000–0.156" in their harness — [sonpham-org/arc-3](https://github.com/sonpham-org/arc-3). Fususu found Gemma 4 31B "falls far behind" Qwen in logic and coding — [discussion 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938) (via prior notes).
- **Throughput.**
  - 27B FP8 Duck runs generate about 1.9–2.2M tokens per 2 h 12 m public run, with an input:output ratio of about 10.7:1. All 25 games hit the 7,920 s clock — Thuitanium ledger rows v26 and thui-v1 (same repo).
  - Flash-Next public notebooks run at about 235–280 generated tok/s — prior notes `kaggle_top_approaches.md`.
- **Trainability of the 27B.** Unsloth gives 27B bf16 LoRA at 56 GB and advises against QLoRA — [Unsloth Qwen3.5 guide](https://unsloth.ai/docs/models/qwen3.5/fine-tune). Thuitanium trained a LoRA on the FP8 27B on one RTX PRO 6000 (Q5).

### Inferences
- **Break-even arithmetic.** Assume Flash-Next hidden is about 4.0 and the 27B baseline is about 1.2–1.7. A LoRA must then lift the 27B by 2.3–2.8 absolute points, a factor of about 2.4–3.3×, just to tie. The only positive public LoRA result is +0.69 absolute on Qwen3.6-27B at a low base. Scott Le Grand's behavioural cloning moved *local* 11.04 → 12.97 (+17%), and local score correlates poorly with hidden. Nothing in the evidence approaches 2.4×.
- Throughput does not rescue the 27B. Its generated tok/s is in the same range as Flash-Next's, so the 27B has no "more thinking per game" advantage to offset its weaker reasoning.
- Qwen3.6-35B-A3B would train on one card in bf16 LoRA, but it starts below the 27B in this harness. That makes it strictly worse as a candidate.

### Gaps
- Our own team's hidden score for a 27B build is not in hand. The 1.15–1.70 figures come from Thuitanium's ledger, and they note one-draw hidden variance is large.
- No one has published a hidden-set comparison of a *fine-tuned* 27B against *base* Flash-Next.

## Q5. Evidence from ARC-AGI-3 competitors who fine-tuned

### Takeaway
There are three concrete data points. **manas joshi (739047):** STaR LoRA on Qwen3.6-27B, hidden 1.25 → 1.94, high variance, and "naively scaling the data hurt". **Thuitanium (`thui-lora`):** r16 LoRA on Qwen3.8-27B-FP8 trained on Kaggle in about 7 h, held-out games **worse** (2.45 / 3.69 vs base 4.61 / 6.35), so the arm was closed as null. **Scott Le Grand (732854):** behavioural cloning moved local 11.04 → 12.97, with no hidden result and no method disclosed. The negatives are Ya Xu ("only backfired") and Fususu (human-play imitation did not beat base Qwen 3.8). An RL pipeline on Flash-Next (H200 node) gave no gain.

### Cited Findings
- **manas joshi (discussion 739047)** [COMMUNITY] — [discussion 739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047).
  - **Data:** "ran the open duck harness (TAAF, MIT) with Qwen3.6-27B, kept only the games the agent won (reached a level), and LoRA-SFT'd on those winning trajectories (STaR / reject-sampling)". The trajectories are chat-JSONL (system → reasoning → Python tool-calls → results).
  - **Gotchas:** "Train assistant-tokens-only; the tool-calls are OpenAI-format, flatten before templating."
  - **Hidden result:** "it was a big jump went from 1.25 to 1.94… took me from 300~ rank to 133~".
  - **Caveats:** "High variance — same recipe, different runs, scores swung a lot"; "Naively scaling the data hurt — more trajectories at the same recipe made it worse. Curation > quantity"; "Base-model-specific — an adapter that helps one model won't necessarily help a different/stronger one".
  - **Claimed mechanism:** "behavior-cloning the harness's own winning trajectories… SFT on the process — how it wrote probes, used the segmentation, structured its reasoning and tool calls".
  - **Released (CC0):** [arc3-sft-trajectories](https://www.kaggle.com/datasets/justforgags/arc3-sft-trajectories), [arc3-duck-lora-sft](https://www.kaggle.com/datasets/justforgags/arc3-duck-lora-sft) (Qwen3.6 `qwen3_5` adapter) and [duck-eval-results](https://www.kaggle.com/datasets/justforgags/duck-eval-results).
  - **Not disclosed:** rank, learning rate, epochs, dataset size and training hardware.
  - **Ya Xu's reply:** "I used to believe that LORA was the trick and spent a lot of time on it, but the result only backfired on me." They also cited Chollet: the public 25 are a "demonstration set… not meant to be used as training data".
- **Thuitanium `thui-lora` arm** [CODE; local clone read in full] — [Sahasawatt/arc-agi-3-agent `thui-lora/`](https://github.com/Sahasawatt/arc-agi-3-agent). Setup:
  - **Data:** "1,826 single-turn samples extracted from levels that duck/thui runs actually CLEARED" (Tufa Duck harness on Qwen3.8-27B). Six games were held out: cd82, ft09, ka59, ls20, su15, wa30.
  - **Hyperparameters** (from `train/taaf-thui-lora-train.ipynb`):
    - `RANK=16`
    - LoRA on `q_proj`/`v_proj` of the 16 full-attention layers only
    - `EPOCHS=2`
    - `MAX_LEN=4096`
    - `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`
    - base `jakobbrggen/qwen3-8-27b-fp8-hf-snapshot` in FP8, with the HF `kernels-community/finegrained-fp8` Triton kernels shipped offline
    - PEFT from an offline wheel dataset
  - **Timing and memory:** "75s/step at MAX_LEN 4096 (v14) -> 2 epochs x ~166 steps ~ 7h, fits the cap". The notebook records: "v13 OOM at step 60: 7.58GiB alloc, 2.15 free — logits+activations at 8192 bust 95GB". The trainer needed a "15-push ladder" (commit `e598cbe`, per `agents/thui/lora/thui-lora-v0.md`).
  - **Eval:** `eval/taaf-thui-lora-e1.ipynb` served the adapter with `--enable-lora --lora-modules thui-lora=…` on only the 6 held-out games, with a 5,400 s/game cap.
  - **Result:** "LoRA SFT on our own winning turns: held-out 2.45 / 3.69 vs base 4.61 / 6.35 → null (thui-lora e1 ×2)". The arm showed the signature "gain where the base is dead, loss where it is alive". It was closed null, and no hidden slot was spent — `notes/B60-exploration-prior-design.md`.
- **Scott Le Grand (discussion 732854)** [COMMUNITY] — [discussion 732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).
  - "the highest I've hit locally without fine tuning the model is 11.04, 12.97 with (behavioral cloning not spoonfed solutions and you have to use reasoning traces from the same model or it's a regression in my experience…)".
  - His hidden best is "3.2", and the base harness is "the stock duck client for nvp4 [Flash-Next NVFP4]… increase the sequence concurrency to 16".
  - When asked "How do you fine-tune? Qwen 3.8 is so big", he did not reply in the thread.
- **Others (732854).** Hidden variance is severe. Examples: "Public 7.6% → 3.35% … Public 10.2% → 3.05% … Public 7.7% → 4.42%" (Nick Pellegrin); "public 22.26 → LB 5.37; 17.34 → 6.91" (Fususu).
- **Human-play imitation.** Fususu: human-play imitation data did not beat base Qwen 3.8 — [discussion 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938) (via prior notes).
- **RL on Flash-Next.** A pipeline built "based miles" on a full H200 node gave "did not gain any performance" — [discussion 742835](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742835).
- **Other LoRA work.** Jason Feng released "Gorilla" (a LoRA adapter plus an RPS training dataset) and "Chimpanzee-1.1: An RPS-Trained Model". The CoTRD notebooks scored 2.78 / 3.16 public — [discussion 732823](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732823) (via prior notes); [discussion 734092](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734092).

### Inferences
- **Every positive result comes from a weak base, and every rigorous result is null or negative.**
  - The positive results are joshi's (Qwen3.6, hidden 1.25) and Le Grand's (local only).
  - Thuitanium ran the most rigorous test: held-out games, paired, two draws. It was null or negative on a Qwen3.8-27B base.
  - The pattern fits "SFT sharpens behaviours the base already has on seen-like games, and harms mid-plan behaviour elsewhere."
- **Reusable recipe details:**
  - train on the assistant tokens only;
  - use traces from the *same* model (Le Grand);
  - curate rather than scale (joshi);
  - use a 4K max length on 96 GB for 27B FP8;
  - expect about 7 h for about 1.8K samples × 2 epochs;
  - hold out games and pair evaluations against the same-seed base.

### Gaps
- I could not retrieve joshi's LoRA hyperparameters. The Kaggle dataset metadata endpoint returned empty.
- `train_lora.py` itself lives inside the private Kaggle dataset `sahasawatt/thui-lora-train-v1` and is not in the git clone. The learning rate, alpha, batch size and accumulation are therefore unknown. About 11 samples per optimizer step is inferred from 1,826 / 166.
- It is unclear what the held-out "2.45 / 3.69 vs 4.61 / 6.35" numbers are exactly. They are most likely per-draw mean scores on the six held-out games; the notes do not define them further.
- Scott Le Grand's model, hardware and hidden result for the behavioural-cloning build were not disclosed.

## Q6. What training data can we generate on Kaggle, and what are the rules?

### Takeaway
Three kinds of data are obtainable:
- **Winning trajectories** from our own Flash-Next Duck runs on the public 25. They are cheap but few (about 5–8 games cleared per run) and are the "demonstration set" Chollet warns against training on.
- **Synthetic games:** sonpham-org's 927 (571 AI-generated, 252 RedBluePill, 50 arena, 29 custom, 25 official), plus theredbluepill/arc-interactive and NVIDIA dream-team's 25.
- **Game ports** such as PushWorld.

Self-generated synthetic data is, per CPMP's precedent, not "External Data", but there is no host ruling yet. Anything used must be publicly releasable under the winner obligations. The real constraint is GPU time to *play* the games, not data availability.

### Cited Findings
- **Synthetic game pools.**
  - sonpham-org/arc-3 hosts **927 games**: AI-generated 571, RedBluePill community 252, reviewed "arena" 50, custom 29, official 25.
  - Its `ARC3-Inference/distill/` holds a "Phase-1 rejection-sampling SFT extractor".
  - Its custom-games pass scored "7.89 mean over 17 games".
  - It is MIT-licensed — [sonpham-org/arc-3](https://github.com/sonpham-org/arc-3).
  - Its pipeline is synthetic games → Duck plays → keep solved levels → SFT — prior notes `kaggle_top_approaches.md` citing `docs/how-this-feeds-kaggle.md`.
- **Other game sources.** [theredbluepill/arc-interactive](https://github.com/theredbluepill/arc-interactive/tree/main); [NVIDIA/dream-team](https://github.com/NVIDIA/dream-team) ("ships 25 curated Game-Creator-generated games"); a partial PushWorld port at arc3.games — [discussion 736540](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/736540).
- **Rules on synthetic data (742940).** The question was whether self-generated synthetic data is "External Data" under §6, which requires it be "publicly available and equally accessible". CPMP (Grandmaster, ARC-AGI-2 winner) answered: "It never was considered as external data in past competition… we generated a large dataset last year and won arc agi2 competition with it. We shared it with our solution, after competition deadline." **No host answer yet** [COMMUNITY] — [discussion 742940](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742940).
- **Rules on external data and models.** "Freely & publicly available external data is allowed, including pre-trained models" [OFFICIAL] — [Code Requirements](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/code-requirements). Winners must deliver training code and methodology [OFFICIAL] — [Kaggle rules §2.5, §2.8](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules) (via prior notes `rules_infra_sdk.md`).
- **Chollet's caution.** "the set of public ARC 3 games is called 'demonstration set' not 'eval set' nor 'training set'. It is not meant to be used as training data" (screenshot quoted in the thread) — [discussion 739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047).
- **Yield of winning data.** "Across runs of one config, 17/25 games were cracked at least once, but only ~5–8 in any single run" — [discussion 743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060) (via prior notes). Thuitanium accumulated 1,826 single-turn winning samples from many 27B runs (Q5).
- **Trace quality.** Traces must come from the same model ("you have to use reasoning traces from the same model or it's a regression") — [732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854). Under Flash-Next, 66.8% of Qwen tool-call responses had no visible content, and the world-model note stayed empty — prior notes `kaggle_top_approaches.md` ([734843](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734843); tantan0327).

### Inferences
- Playing is GPU-bound: one 25-game Duck pass takes about 2.2 RTX-hours. At an optimistic 15–30 RTX-hours per week, a user gets about 5–12 passes per week, or about 150–300 game-plays. Most synthetic AI-generated games are "unreviewed" and of unknown difficulty. Harvesting a curated SFT set of a few thousand winning turns from them would take most of the remaining quota before any training begins.
- For Flash-Next specifically, harvested traces would have no trainer to consume them (Q2). They could still be used without training, as retrieved in-context exemplars or prompt distillation, but that is outside this note's scope.

### Gaps
- There is no host ruling on 742940.
- The quality and difficulty distribution of the 571 AI-generated sonpham games is not measured, and no hidden-set result from training on them has been published.

## Q7. Week-by-week Kaggle-quota budget to Nov 2, 2026, and the overall verdict

### Takeaway
**Verdict: not feasible.** Training a model that beats our served Flash-Next NVFP4 with only Kaggle compute before Nov 2 is not feasible:
- Flash-Next cannot be trained on one 96 GB card with existing software.
- The trainable alternative (27B LoRA) starts about 2.5× lower on hidden and has no evidence of closing that gap.
- The 5.5 remaining weeks give roughly 150–180 GPU-hours in total, of which only an unknown fraction is RTX time.

If the user still wants a hedge, the only rational spend is a small, capped experiment. It is costed below, with kill criteria. Everything else should go to Flash-Next inference and harness work.

### Cited Findings
- Weekly quota is about 30 GPU-h, with RTX consuming it faster by an unquantified factor. Up to 2 concurrent sessions are allowed, sessions last at most 9 h, and there is 1 submission per day. A scored rerun does not consume quota — Q1 sources ([734585](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734585); [742148](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742148); [Code Requirements](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/code-requirements)).
- A 27B LoRA training run takes about 7 h on RTX (1.8K samples × 2 epochs at 4K). A 6-game held-out eval runs at 5,400 s/game — [Thuitanium thui-lora](https://github.com/Sahasawatt/arc-agi-3-agent).
- A public 25-game Duck pass takes about 2 h 12 m wall-clock — Thuitanium ledger; prior notes.
- Judging one notebook version needs "at least like 5" submissions, because hidden variance spans roughly 3–4.4 for near-identical builds — [732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).

### Inferences
**Optional hedge plan, "Flash-Next adapter feasibility, capped at about 12 RTX-hours total".** Stop at the first failed gate.

| Week | Dates | Kaggle work | Quota (est.) | Gate / kill criterion |
|---|---|---|---|---|
| W1 | Sep 25 – Oct 1 | (a) **Serving smoke.** Add a B=0 identity LoRA on Flash-Next's bf16 `self_attn` q/v (12 full-attention layers) to the existing NVFP4 + MTP vLLM profile, with `vllm_runtime_lora_guard` installed. Check that `/v1/models` lists it, that a chat completion works, and compare tok/s with and without the adapter. (b) Offline CPU work, no GPU: turn existing Phase A logs into assistant-only SFT JSONL, keeping only cleared levels and same-model (Flash-Next) turns. | ~2 RTX-h | Kill if vLLM rejects the adapter, silently drops modules (the guard raises), or throughput falls by more than 10%. |
| W2 | Oct 2 – Oct 8 | **Training-path probe.** Load RadixArk NVFP4 in transformers 5.8.0.dev0 with the n-gram table on CPU. Attempt one forward and backward pass of an attention-only LoRA at 2K tokens. Log peak VRAM and s/step. | ~3 RTX-h | Kill if there is no backward through the FP4 experts, if it hits OOM at ≥2K tokens, or if a step takes more than 120 s. This is the expected outcome, per Q2. |
| W3 | Oct 9 – Oct 15 | Only if W2 passed: a single SFT run of ≤1.5K curated same-model winning turns, 1 epoch, r=8–16, attention-only. | ~7–9 RTX-h | — |
| W4 | Oct 16 – Oct 22 | Paired public eval with held-out games (Thuitanium's method: hold out ≥6 games; two draws per arm against the same-seed base). | ~5–9 RTX-h | Kill unless held-out **levels** beat the same-seed base in both draws. |
| W5 | Oct 23 – Oct 29 | Hidden submissions: at most 3–5 of the 1/day slots, alternating adapter and base. | submissions only | Keep only if the adapter's hidden mean is at or above the base's hidden mean. |
| W6 | Oct 30 – Nov 2 | Final selection. | — | — |

- **Expected outcome.** The plan is expected to stop at W1 or W2, costing about 5 RTX-hours, and the result would still be informative. This is the only fine-tuning path that could *beat* the current model, because it keeps the Flash-Next base.
- **Rejected alternative: 27B LoRA.** It would cost about 7 h training plus about 10 h eval plus 5 hidden slots. The expected result is a hidden score around 2, per joshi and Thuitanium, well below Flash-Next's ~4. It cannot win.
- **Rejected alternative: TPU v5e-8** (about 20 h/week, separate from GPU). No JAX or XLA training code exists for `qwen4_exp`, and Flash-Next's bf16 weights (about 250 GB) exceed the 128 GB HBM. TPU is not a route for this model.
- **Why not "just gather data now and train later"?** The competition ends Nov 2, and there is no post-deadline benefit. Every RTX-hour spent collecting traces for a model we cannot train is taken from harness and inference A/B work. That work is also bottlenecked by the same quota and by the 1/day submission cap.

### Gaps
- The RTX quota multiplier is unknown. If it is ≥3×, the whole plan above exceeds a week's budget and should be cut to the W1 serving smoke only.
- Two things were not verified in this session: whether our pinned wheelhouse's vLLM has LoRA enabled for `qwen4_exp`, and whether transformers 5.8.0.dev0 can load a modelopt NVFP4 checkpoint for training. These are exactly what W1 and W2 test.
