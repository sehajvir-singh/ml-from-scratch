# Open-weight LLM/VLM selection and inference configuration for an offline ARC-AGI-3 agent on Kaggle (as of 2026-09-25)

Scope: which open models to run inside the Kaggle ARC-AGI-3 submission notebook, what fits on each Kaggle GPU, how to serve them (vLLM / SGLang / llama.cpp), and what throughput and token budget that gives per game. Evidence comes from the Tufa Labs "Duck" repo (the Milestone #1 winner). I cloned it and parsed its real vLLM logs and benchmark JSON. Other sources are Hugging Face model cards, vLLM docs and recipes, community RTX PRO 6000 benchmarks, and competitor repos.

---

## Q1. Kaggle hardware and competition constraints: which GPU, how long, how many games?

### Takeaway
The GPU that matters for ARC-AGI-3 is Kaggle's "RTX 6000". It is the **96 GB RTX PRO 6000 Blackwell Server Edition** (GCP `g4-standard-48`), not the 48 GB Ada card. It supports FP8 and NVFP4 natively. Several independent competitor sources put the runtime at **9 hours**, with no internet. The hidden-game count conflicts between sources: 55 private games, or 110 games in the Kaggle rerun (plausibly 55 semi-private plus 55 private). Budget for 110 to be safe.

### Cited Findings
- The ARC-AGI-3 Kaggle starter lists these accelerators: CPU, "Nvidia T4 ×2" (default), "Nvidia P100", and "Nvidia RTX 6000 (`g4-standard-48`)". It says the RTX 6000 is reserved for ARC-AGI-3 and "burns GPU quota faster". All accelerated sessions have internet disabled — [ARC Prize 2026 docs](https://docs.arcprize.org/arc-prize-2026)
- GCP `g4-standard-48` is one NVIDIA RTX PRO 6000 Blackwell Server Edition with **96 GB GDDR7**, 48 vCPUs and 180 GB RAM. The GPU has 24,064 CUDA cores, 5th-gen Tensor Cores and ~1,586 GB/s memory bandwidth — [TechPowerUp](https://www.techpowerup.com/342057/google-cloud-g4-vms-with-nvidia-rtx-pro-6000-blackwell-gpu-now-generally-available); [Embedded.com](https://www.embedded.com/google-cloud-unveils-new-g4-vms-based-on-nvidia-rtx-pro-6000-blackwell-server-edition/); [Google Cloud blog](https://cloud.google.com/blog/products/compute/g4-vms-powered-by-nvidia-rtx-6000-blackwell-gpus-are-ga)
- The Duck's Kaggle launcher asserts the GPU type `rtx-pro-6000` (`GPU_NAME_PATTERNS = {'rtx-pro-6000': ('rtx pro 6000',) ...}`, default `KAGGLE_GPU_TYPE='rtx-pro-6000'`). Its run config uses Kaggle accelerator `"NvidiaRtxPro6000"`. Its deploy code says "The default honors R2.52: RTX6000 GPU with internet disabled" — [duck-harness kaggle.py](https://github.com/Tufalabs/duck-harness/blob/main/ARC3-Inference/inference/framework/kaggle.py); [deploy_kaggle.py](https://github.com/Tufalabs/duck-harness/blob/main/tufa-arc-agi-framework/src/taaf/deploy_kaggle.py)
- Tufa: "evaluation on the semi-private/private test set on Kaggle is constrained to a single GPU" — [Tufa Labs Duck write-up](https://tufalabs.ai/research/duck-harness/)
- **Runtime:** "Kaggle runtime limit: 9 hours (hard envelope)". The same memo budgets "Main inference and interaction: 390 minutes" — [leejianrong strategy memo 2026-09-20](https://github.com/leejianrong/solve-arc-agi-3/blob/main/docs/research/2026-09-20-current-state-and-strategy.md). A second repo says "9 hours total with one 96GB Blackwell GPU" — [anandsingh8687 agent repo](https://github.com/anandsingh8687/arc-prize-2026-arc-agi-3-agent). This conflicts with Tufa's framework default `max_runtime_s: float = 12 * 3600.0`. That value is a self-imposed soft budget, not necessarily Kaggle's limit — [deploy_kaggle.py](https://github.com/Tufalabs/duck-harness/blob/main/tufa-arc-agi-framework/src/taaf/deploy_kaggle.py)
- **Game count:** one repo says "110 games in competition set" — [anandsingh8687](https://github.com/anandsingh8687/arc-prize-2026-arc-agi-3-agent). An arXiv paper reports "RHAE=0.30 on the full 55-game private evaluation" — [Explore Before You Solve, arXiv 2605.25931](https://arxiv.org/abs/2605.25931). The public demo set is 25 games with 183 levels — [leejianrong memo](https://github.com/leejianrong/solve-arc-agi-3/blob/main/docs/research/2026-09-20-current-state-and-strategy.md)
- Throughput matters more than engine speed: "0.577 actions/sec sustained" is needed to reach level 3 on all games. The game engine runs "~800 actions/sec on CPU", so model inference dominates the budget — [anandsingh8687](https://github.com/anandsingh8687/arc-prize-2026-arc-agi-3-agent)
- 5 official submissions per day — [rvats20 starter-based repo](https://github.com/rvats20/ARC-AGI-3-agent)
- Milestone #2 deadline is Sept 30, 2026. All code and methods must be open-sourced to be prize-eligible. No internet during evaluation — [ARC Prize competition page](https://arcprize.org/competitions/2026/arc-agi-3)

### Inferences
- The two game counts are probably consistent: one Kaggle rerun may play the 55-game semi-private set and the 55-game private set together, which gives 110. Plan the time budget for **110 games in ~9 h**. If it turns out to be 55, the per-game budget simply doubles.
- T4×2 and P100 are only useful for cheap development and debugging, such as testing prompts with a small or quantized model. The submission should target the RTX PRO 6000.
- The 180 GB of host RAM on g4-standard-48 makes CPU offload of rarely used weights feasible (for example Qwen3.8-Flash-Next's n-gram embeddings). It is untested.

### Gaps
- I could not load the Kaggle competition Overview or Rules page (it renders with JavaScript). The 9 h limit and the 110-vs-55 game count come only from competitor repos and an arXiv paper, not from the official Kaggle text.
- I could not confirm whether the ARC Prize "official template" uses GPT-OSS-120B. One search snippet mentioned "the official ARC Prize GPT-OSS-120B template", but I could not fetch its notebook.

---

## Q2. Candidate open models (Sep 2026): sizes, licenses, vision, context, benchmarks

### Takeaway
The best fit for one 96 GB card is a **~27–31B dense VLM in FP8**. **Qwen3.8-27B (Apache-2.0, released 2026-08-14)** is a same-architecture, drop-in successor to the Duck's Qwen3.6-27B, with large gains on agentic coding and visual reasoning. **Gemma-4-31B-it** (Apache-2.0) is the strongest alternative and powered the 2nd- and 3rd-place Milestone #1 entries. GPT-OSS-120B fits but is text-only and a year old. Every frontier-scale open model released Jul–Sep 2026 is 300B+ total parameters and does not fit.

### Cited Findings
**What the winners used**
- Milestone #1 results: 1st, Tufa Labs "The Duck", **Qwen 3.6 27B FP8** run locally, a code-writing REPL agent. 2nd, Reki, **Gemma-4-31B**, a vision-LLM that outputs one JSON action per step. 3rd, "forge", also **Gemma-4-31B** — [ARC Prize Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- Exact checkpoint in the Duck: `vrfai/Qwen3.6-27B-FP8`, shipped to Kaggle as dataset `driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot` — [duck-harness configs/inference.json](https://github.com/Tufalabs/duck-harness/blob/main/ARC3-Inference/configs/inference.json); [kaggle.py](https://github.com/Tufalabs/duck-harness/blob/main/ARC3-Inference/inference/framework/kaggle.py)
- Duck score: 1.6002 ± 0.4475 mean over 25 public games, run locally — [Tufa write-up](https://tufalabs.ai/research/duck-harness/). Tufa's tweet says "We hit 1.21%" — [Tufalabs on X](https://x.com/tufalabs/status/2072336849465417747). AlphaSignal reports 1.03 on Kaggle — [AlphaSignal](https://alphasignal.ai/news/tufa-labs-wins-25k-beating-frontier-ai-on-the-world-s-hardest-benchmark). These are different eval sets or runs, so they are not directly comparable.
- Other competitors: one runs `Gemma-4-26B-A4B-NVFP4` in-process with vLLM on an RTX PRO 6000, with 32,768-token context, 85% GPU memory and native thinking — [adityav31121999/arcgames](https://github.com/adityav31121999/arcgames). Another reportedly runs Qwen3.8-27B-FP8 under vLLM offline, with a Python REPL that writes and verifies a per-game world model — [JustAdev742 repo (search snippet, not fetched directly)](https://github.com/JustAdev742/Arc-Agi-3-Kaggle-comp)

**Qwen3.8-27B** — [HF model card](https://huggingface.co/Qwen/Qwen3.8-27B); FP8: [Qwen/Qwen3.8-27B-FP8](https://huggingface.co/Qwen/Qwen3.8-27B-FP8)
- License Apache-2.0. 27.8B parameters. Native vision-language model (images and video). Architecture `qwen3_5`, the same as Qwen3.6-27B. 64 layers laid out as 16 × (3 × Gated DeltaNet + 1 × Gated Attention). Gated Attention has 24 Q heads and 4 KV heads with head dim 256. Context is 262,144 native, extensible to 1M. MTP was "trained with multiple steps".
- Thinking is on by default and can be disabled per request. `reasoning_effort` accepts `xhigh` (default), `medium` and `low`. `preserve_thinking` keeps reasoning from past turns.
- Benchmarks, Qwen3.8-27B vs Qwen3.6-27B: Terminal Bench 2.1 73.0 vs 63.4. SWE-bench Pro 61.7 vs 53.5. DeepSWE 1.1 42.2 vs 13.3. NL2Repo 42.3 vs 36.2. LiveCodeBench v6 90.3 vs 83.9. GPQA-D 89.2 vs 87.8. HLE 30.8 vs 24.0. IFBench 79.5 vs 69.1. OSWorld-Verified 84.3 vs 63.9. WebArena-Verified 64.8 vs 48.8. AndroidWorld 81.9 vs 70.3. **BabyVision (general visual reasoning) 65.7 vs 28.9 without code interpreter (85.6 with CI)**. RealWorldQA 85.9 vs 84.1. ERQA 65.5 vs 62.5.
- Recommended sampling: thinking uses temp 1.0, top_p 0.95, top_k 20. Non-thinking uses temp 0.7, top_p 0.8, top_k 20, presence_penalty 1.5. The card recommends SGLang, vLLM or TokenSpeed.

**Qwen3.6-27B / Qwen3.6-35B-A3B**
- Qwen3.6-27B: 27.8B parameters, Apache-2.0, image-text-to-text, official FP8 checkpoint `Qwen/Qwen3.6-27B-FP8` — [HF](https://huggingface.co/Qwen/Qwen3.6-27B); [HF FP8](https://huggingface.co/Qwen/Qwen3.6-27B-FP8)
- Qwen3.6-35B-A3B: 36.0B total parameters (MoE, arch `qwen3_5_moe`), Apache-2.0, vision, official FP8 checkpoint — [HF](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)

**Qwen3.8-Flash-Next (released 2026-08-27)** — [HF model card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- 125B total with 6B active, plus 51B of n-gram embeddings and 4B of MTP weights (HF counts 180B). 512 experts, 10 routed + 1 shared. Uses the new "Qwen Sparse Attention". Native vision. 262K context. **License `qwen-community-1.0` (not Apache)**. The card calls it an "experimental preview of the architecture that will underpin Qwen4".
- Benchmarks vs Qwen3.8-27B: SWE-bench Pro 62.5 vs 61.7. DeepSWE 58.7 vs 42.2. NL2Repo 48.1 vs 42.3. CoWorkBench 73.9 vs 70.7. JobBench 55.7 vs 33.4.
- The card says n-gram embeddings are "more amenable to offloading than MoE". Community quants exist, such as `lovedheart/Qwen3.8-Flash-Next-NVFP4-W4A16-ATTN-FP8-MTP-NVFP4` — [HF search](https://huggingface.co/models?search=Qwen3.8-Flash-Next)

**Gemma 4** — [google/gemma-4-31B-it card](https://huggingface.co/google/gemma-4-31B-it)
- License Apache-2.0. 31B dense has 30.7B parameters, 60 layers, 1024-token sliding window interleaved with global layers, 256K context, a ~550M vision encoder, and configurable thinking. 26B-A4B MoE has 25.2B total / 3.8B active, 8 of 128 experts plus 1 shared, 256K context, vision — [gemma-4-26B-A4B-it](https://huggingface.co/google/gemma-4-26B-A4B-it)
- 31B vs 26B-A4B: LiveCodeBench v6 80.0% vs 77.1%. Codeforces ELO 2150 vs 1718. GPQA-D 84.3% vs 82.3%. Tau2 76.9% vs 68.2%. MMMU Pro 76.9% vs 73.8%. BigBench Extra Hard 74.4% vs 64.8%. MRCR v2 at 128K 66.4% vs 44.1%.

**GPT-OSS** — [openai/gpt-oss-120b card](https://huggingface.co/openai/gpt-oss-120b); [gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)
- 120b has 117B parameters with 5.1B active. 20b has 21B with 3.6B active. Both are Apache-2.0, **text-only**, post-trained with MXFP4 MoE weights. 120b fits "a single 80GB GPU"; 20b runs "within 16GB of memory". Reasoning effort is low, medium or high. They require the harmony chat format. A Kaggle Models copy exists — [Kaggle: gpt-oss-120b](https://www.kaggle.com/models/danielhanchen/gpt-oss-120b)

**Too large for one 96 GB GPU (sizes from HF)**
- GLM-5.3-Flash: 321B, MIT, vision — [HF](https://huggingface.co/zai-org/GLM-5.3-Flash). GLM-5.3: 753B, license "other" — [HF](https://huggingface.co/zai-org/GLM-5.3)
- DeepSeek-V4.1-Flash (2026-09-10): HF reports 763B, MIT, vision — [HF](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash). The Qwen3.8-Flash-Next card lists DeepSeek-V4-Flash-0731 at 284B total / 13B active — [Qwen3.8-Flash-Next card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- Kimi-K3: 2.78T parameters, license "other" — [HF](https://huggingface.co/moonshotai/Kimi-K3)
- Xiaomi MiMo-V2.6-Flash-RL (2026-09-22): 311B, MIT, multimodal — [HF](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL)
- Mistral-Small-4-119B-2603: 119.4B, Apache-2.0, with an official NVFP4 checkpoint and an EAGLE draft model — [HF](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603); [NVFP4](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603-NVFP4). **Llama:** the meta-llama org lists no new 2026 releases; the newest are Llama-4 Scout and Maverick from April 2025 — [HF meta-llama](https://huggingface.co/meta-llama)

### Inferences
- **Primary recommendation: Qwen3.8-27B-FP8.** It uses the same `qwen3_5` architecture, the same parsers and the same `preserve_thinking` template as the Duck's Qwen3.6-27B, so switching is a drop-in change. Its jumps on BabyVision (28.9 → 65.7), OSWorld (63.9 → 84.3), DeepSWE (13.3 → 42.2) and Terminal Bench cover the capabilities ARC-AGI-3 needs: visual perception, long-horizon tool use, and writing and debugging code. Tufa itself credited "better base models" for its gains.
- **Secondary: Gemma-4-31B-it**, for a pure VLM-policy design (Reki-style) or as an ensemble or ablation baseline. Its coding scores are below Qwen3.8-27B (LCB v6 80.0 vs 90.3).
- **Fast option: an MoE (Qwen3.6-35B-A3B or Gemma-4-26B-A4B).** About 4–8× less compute per token than a 27B dense model. Use it where call count matters more than depth, for example cheap per-step perception or policy calls, with the 27B dense model reserved for world-model and code writing. Both can be co-served only if memory allows: about 34 + 36 GB in FP8 fits in 96 GB, but leaves little KV cache.
- **GPT-OSS-120B** fits (roughly 61–65 GB of MXFP4 weights by my estimate) and decodes fast (5.1B active), but it has no vision and is older. It is only worth considering for a text-only code-writing agent.
- **Qwen3.8-Flash-Next** is the only frontier-class new model that might squeeze in: 4-bit experts at ~63 GB plus n-gram embeddings offloaded to the 180 GB host RAM. It is high-risk: an experimental architecture (`qwen4_exp`) that needs a very new vLLM, and a non-Apache license whose competition eligibility must be checked.

### Gaps
- I could not verify GPT-OSS benchmark numbers in this session (openai.com returned 403, and the HF card has no benchmark table).
- Gemma-4-31B, Qwen3.8-27B and GPT-OSS have not been compared side by side on ARC-AGI-3 under the same harness. The Milestone blog does not quantify the model-versus-harness contribution.
- The license text of `qwen-community-1.0` was not reviewed.

---

## Q3. What fits on which Kaggle GPU, and which quantization formats run where?

### Takeaway
**RTX PRO 6000 (Blackwell, sm_120, 96 GB):** runs everything, including BF16, FP8 W8A8, NVFP4 and MXFP4. A 27B model in FP8 uses about 34 GiB, leaving about 45 GiB for KV cache. **T4 (sm_75, 16 GB each):** vLLM works but only in FP16 (no bf16, no FP8 compute), so 4-bit AWQ/GPTQ is needed and a 27–31B model just fits across 2×T4 with TP=2. **P100 (sm_60):** vLLM does not support it; only llama.cpp or GGUF will run.

### Cited Findings
- vLLM requires "compute capability 7.5 or higher". T4 is supported; Pascal P100 is not. Blackwell requires CUDA ≥ 12.8 wheels — [vLLM GPU installation docs](https://docs.vllm.ai/en/latest/getting_started/installation/gpu.html); see also [vLLM issue #1284 (P100)](https://github.com/vllm-project/vllm/issues/1284)
- BF16 needs compute capability ≥ 8.0, so T4 and P100 are FP16-only. FP8 W8A8 runs on Ada, Hopper and Blackwell. Turing and Ampere get only weight-only FP8 (W8A16) through Marlin kernels — [vLLM FP8 docs (via search summary)](https://docs.vllm.ai/en/stable/features/quantization/llm_compressor/fp8/)
- A report notes that AWQ, GPTQ and FP8 models "cannot be served" by vLLM or SGLang on Pascal and Volta — [odysseus issue #6402](https://github.com/odysseus-dev/odysseus/issues/6402)
- Measured on the Duck's server: "Model loading took 33.66 GiB memory" for `vrfai/Qwen3.6-27B-FP8`. With `gpu_memory_utilization=0.92` and `max_model_len=32768`, the KV cache was 516,656 tokens — [duck-harness example-run/server-0.log](https://github.com/Tufalabs/duck-harness/tree/main/example-run)
- Peak VRAM for Qwen3.6-27B FP8 was about 72.3 GB in an A100 concurrency sweep. The Kaggle model snapshot is 35.9 GB — [leejianrong qwen36-vllm-artifact](https://github.com/leejianrong/solve-arc-agi-3/blob/main/docs/baselines/qwen36-vllm-artifact.md)
- The vLLM recipe for Qwen3.6-27B on RTX Pro 6000 validates the **NVFP4** checkpoint `nvidia/Qwen3.6-27B-NVFP4`: MLP linears in NVFP4 (W4A16), attention and KV cache in FP8. It needs vLLM ≥ 0.28 nightly — [vLLM recipes: Qwen3.6-27B](https://recipes.vllm.ai/Qwen/Qwen3.6-27B)
- A FlashInfer sampler JIT crash on sm_120 is fixed with `VLLM_USE_FLASHINFER_SAMPLER=0`; the same thread also sets `VLLM_USE_DEEP_GEMM=0` — [HF discussion Qwen3.8-27B-FP8 #9](https://huggingface.co/Qwen/Qwen3.8-27B-FP8/discussions/9)
- GGUF quants of new models exist, for example `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF` (trending) — [HF trending](https://huggingface.co/models?sort=trending); and `unsloth/gpt-oss-120b-GGUF` — [HF](https://huggingface.co/unsloth/gpt-oss-120b-GGUF)

### Inferences (fit table; memory = weights only, my estimates from parameter counts)
| Model | BF16 | FP8 | 4-bit (AWQ/GPTQ/NVFP4/MXFP4) | 2×T4 (32 GB, FP16 compute) | P100 16 GB | RTX PRO 6000 96 GB |
|---|---|---|---|---|---|---|
| Qwen3.8/3.6-27B (dense VLM) | ~56 GB | ~34 GiB (measured) | ~16–18 GB | AWQ/GPTQ int4, TP=2, small KV (~8–10 GB) | GGUF Q3/Q2 only, poor | FP8 + ~45 GiB KV; or NVFP4 + more KV |
| Gemma-4-31B (dense VLM) | ~62 GB | ~31–33 GB | ~17–19 GB | int4 TP=2, tight | no | FP8 comfortable |
| Qwen3.6-35B-A3B / Gemma-4-26B-A4B (MoE VLM) | ~52–72 GB | ~27–37 GB | ~14–20 GB | int4 fits well | GGUF Q3/Q4 tight | FP8 comfortable, fastest decode |
| GPT-OSS-20B (text) | – | – | MXFP4 "within 16 GB" | fits (llama.cpp safest) | fits (llama.cpp GGUF) | trivial |
| GPT-OSS-120B (text) | – | – | MXFP4 ~61–65 GB | no | no | fits, ~25–30 GB for KV |
| Mistral-Small-4-119B (text) | – | ~120 GB | NVFP4 ~60–65 GB | no | no | NVFP4 fits |
| Qwen3.8-Flash-Next 125B-A6B (+51B n-gram) | – | – | ~63 GB experts + embeddings | no | no | only with embedding offload to host RAM; risky |

- KV math for Qwen3.x-27B: only the 16 gated-attention layers keep a growing KV cache. That is 16 × 2 × 4 KV heads × 256 dim × 2 bytes = **64 KiB per token in BF16, 32 KiB in FP8**, plus a fixed recurrent state per sequence for the 48 DeltaNet layers. The Duck's 516,656-token KV pool at 0.92 utilization matches an 80 GB H100: 73.6 GB − 33.7 GiB weights − overhead ≈ 31.5 GiB, which is 516K × 64 KiB. On the 96 GB RTX PRO 6000, expect about **740K tokens with BF16 KV or about 1.5M with FP8 KV**. That is enough for 32 concurrent games at 32K context, or 16 at 64K with BF16 KV.
- On T4 there are no FP8 tensor cores and no bf16. Because Qwen and Gemma are bf16-trained, FP16 inference risks overflow and activation issues. Test before relying on T4 for faithful development runs.

### Gaps
- No measured tokens/sec for any of these models on T4 or P100 was found.
- Whether current vLLM's MXFP4 path (GPT-OSS) runs on T4 (sm_75) was not verified.

---

## Q4. Serving stack: vLLM vs SGLang vs llama.cpp; prefix caching, speculative decoding (MTP/EAGLE), batching, max-model-len, offline install

### Takeaway
Use **vLLM, the proven path**: the Duck won with vLLM 0.19.0 on Kaggle, via an offline wheelhouse attached as a Kaggle dataset. Turn on **prefix caching**, **MTP speculative decoding (n=2–3)** which the Duck did not use, **FP8 KV cache**, and **16–32 concurrent games** against one OpenAI-compatible server. Use max-model-len 32K–64K and keep the prompt append-only so the prefix cache keeps hitting. SGLang is officially supported by Qwen3.8 but has no ARC-AGI-3 track record. llama.cpp is only for the P100 or T4 development boxes.

### Cited Findings
- **The Duck's Kaggle vLLM launch** (from its source): `python -m vllm.entrypoints.openai.api_server --model <path> --tensor-parallel-size 1 --enable-auto-tool-choice --tool-call-parser qwen3_coder --generation-config vllm --enable-prefix-caching --default-chat-template-kwargs '{"preserve_thinking": true}' --reasoning-parser qwen3 --max-model-len 65536`. The wheelhouse is `vllm==0.19.0 torch==2.10.0 flashinfer==0.6.6`. The smoke test sends `chat_template_kwargs: {enable_thinking: False}` — [kaggle.py](https://github.com/Tufalabs/duck-harness/blob/main/ARC3-Inference/inference/framework/kaggle.py)
- Cluster config: `gpu_memory_utilization 0.92`, `enable_prefix_caching true`, `context_window 32768`, `concurrent_jobs 32` (per GPU, one server per GPU), `max_runtime_minutes 45` per game, `n_passes 20`. No speculative decoding flag is set — [configs/inference.json](https://github.com/Tufalabs/duck-harness/blob/main/ARC3-Inference/configs/inference.json); [example-run server log non-default args](https://github.com/Tufalabs/duck-harness/tree/main/example-run)
- **Offline install on Kaggle:** the Duck notebook attaches datasets `driessmit1/arc3-vllm-h100-wheelhouse-v3` and `driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot`. It installs the competition's `arc-agi` package with `pip install --no-index --find-links /kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels`. It prepends `/usr/local/nvidia/lib64` to `LIBRARY_PATH` so vLLM and torch link against libcuda. It checks both `/kaggle/input/<slug>` and `/kaggle/input/datasets/<owner>/<slug>` mount paths — [taaf-duck-harness-kaggle-share.ipynb](https://github.com/Tufalabs/duck-harness/blob/main/taaf-duck-harness-kaggle-share.ipynb)
- The wheelhouse is 5.1 GB, pinned with a 179-entry SHA256SUMS manifest and installed with `--no-index`. Model load took 351.3 s on a RunPod Blackwell. HF, datasets and Transformers offline flags are set — [leejianrong qwen36-vllm-artifact](https://github.com/leejianrong/solve-arc-agi-3/blob/main/docs/baselines/qwen36-vllm-artifact.md)
- **Measured prefix-cache hit rate** in the Duck run was about 48.6% (vLLM log) — [example-run/server-0.log](https://github.com/Tufalabs/duck-harness/tree/main/example-run). The Duck "continuously pops the oldest messages" to play indefinitely — [Milestone blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- **MTP on the RTX PRO 6000:** Qwen3.8-27B-FP8 with stock vLLM 0.27.1 reached 46.8 tok/s without MTP and 62.2 tok/s with MTP depth 2 (300 W Max-Q card). A tuned 600 W card reached 80–100 tok/s at MTP depth 3. Depth 5 with poor settings gave 23 tok/s (acceptance 2.32). Optimal depth depends on power: 2 for the 300 W card, 3 for the 600 W — [HF discussion #9](https://huggingface.co/Qwen/Qwen3.8-27B-FP8/discussions/9)
- Qwen3.6-27B NVFP4 + MTP on 2× RTX PRO 6000 Max-Q gave about 190 tok/s decode. MTP mean acceptance length was 3.19, per-position acceptance 0.87/0.72/0.60, average draft acceptance 73% — [loFT LLC benchmark](https://loftllc.dev/en/docs/tech/llm-research/qwen3-6-27b-nvfp4-mtp-vllm-benchmark/)
- One guide reports about 100 tok/s per GPU for Qwen3.6-27B INT4 + MTP n=3 + FP8 KV, and about 170 tok/s for the 35B-A3B FP8 MoE, on RTX PRO 6000 with prefix caching and chunked prefill on — [lastloop-ai vllm-blackwell-guide (search summary)](https://github.com/lastloop-ai/vllm-blackwell-guide)
- The vLLM recipe for Qwen3.6-27B uses `--kv-cache-dtype fp8 --attention-backend flashinfer --speculative-config '{"method":"mtp","num_speculative_tokens":5}' --reasoning-parser qwen3 --tool-call-parser qwen3_coder --enable-prefix-caching` (DGX Spark example) — [vLLM recipes](https://recipes.vllm.ai/Qwen/Qwen3.6-27B)
- Qwen3.8 officially supports SGLang (cookbook), vLLM (recipe) and TokenSpeed — [Qwen3.8-27B card](https://huggingface.co/Qwen/Qwen3.8-27B). Community DFlash speculators are appearing, for example `inference-optimization/qwen3.8-27B-speculator.dflash2...` — [HF search](https://huggingface.co/models?search=Qwen3.8). EAGLE-3 with gpt-oss-120b had open vLLM bugs — [vLLM issue #26328](https://github.com/vllm-project/vllm/issues/26328)
- Another competitor uses vLLM's in-process API (no HTTP server) with eager execution, 85% GPU memory and 32K context — [adityav31121999/arcgames](https://github.com/adityav31121999/arcgames)

### Inferences
- **Suggested launch for the RTX PRO 6000** (Qwen3.8-27B-FP8; adjust flag syntax to the vLLM version in your wheelhouse):
  ```
  VLLM_USE_FLASHINFER_SAMPLER=0 HF_HUB_OFFLINE=1 python -m vllm.entrypoints.openai.api_server \
    --model /kaggle/input/<qwen3-8-27b-fp8-snapshot> --served-model-name qwen \
    --max-model-len 65536 --gpu-memory-utilization 0.92 --max-num-seqs 32 \
    --enable-prefix-caching --kv-cache-dtype fp8 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":2}' \
    --reasoning-parser qwen3 --tool-call-parser qwen3_coder --enable-auto-tool-choice \
    --default-chat-template-kwargs '{"preserve_thinking": true}' --generation-config vllm
  ```
  A new wheelhouse is needed: Qwen3.8 needs a newer vLLM (0.27.x has been used) than the Duck's 0.19.0. Blackwell needs CUDA ≥ 12.8 builds. Build it on a matching Kaggle RTX 6000 image with internet on, then upload it as a dataset.
- **MTP helps most at low concurrency.** When 16–32 games are batched, decode becomes more compute-bound and speculative gains shrink. Benchmark n ∈ {0, 1, 2, 3} at your actual concurrency. Late in the run, when few games are still active, MTP matters more.
- **Prefix-cache-friendly eviction.** Popping the oldest message on every turn changes the prefix right after the system prompt, which forces a full re-prefill of the history. Evicting in large chunks (for example, drop the oldest 50% when 90% full) keeps most turns append-only. That should lift the ~49% hit rate a lot, and it matters because prefill dominated the Duck's GPU load (see Q5).
- **max-model-len:** the Duck's prompt budget was 32K (`context_window`), served with 64K on Kaggle. More context costs KV slots and prefill. 32K–64K with retained reasoning plus compaction (Q6) looks like the sweet spot.
- **SGLang:** its RadixAttention prefix cache could suit multi-branch agents that share prefixes, but no ARC-AGI-3 competitor evidence exists. The switching cost is a new offline wheelhouse. **llama.cpp:** use only for P100 or T4 development boxes (GGUF). Its multi-sequence batching and throughput are far below vLLM for 16–32 concurrent games.

### Gaps
- No direct vLLM vs SGLang benchmark on RTX PRO 6000 for Qwen3.8-27B was found.
- No measured aggregate tokens/sec at 16–32 concurrency on a single RTX PRO 6000 was found. Millstone tested only up to 5 concurrent requests.

---

## Q5. Throughput math: token budget per game and how often the LLM can be called

### Takeaway
On one RTX PRO 6000 over ~7.5 usable hours, a 27B dense FP8 model can generate roughly **8–20M tokens total**. That is about **75–180K generated tokens per game for 110 games, or 150–360K for 55**, which is about **1.3–3 Duck-style passes per game**. Prefill, not decode, dominated the Duck's GPU load: about 11 prompt tokens were processed per generated token. Prompt length and cache hits are therefore as important as thinking length. At about 1.4K generated tokens per call, you can afford roughly **50–130 LLM calls per game (110 games)**. Each call must emit multiple actions or code, because a single game's human baseline is about 750 actions.

### Cited Findings
- **Duck example run (25 public games × 20 passes = 500 runs, 2 GPUs, one vLLM server each, up to 32 concurrent per GPU):** duration 6 h 10 m 31 s. 29,599,016 generated tokens in total, "generated tokens/sec: 1331.42 (job wallclock)". 68,682 actions. Mean score 1.60 — [example-run/summary.txt](https://github.com/Tufalabs/duck-harness/tree/main/example-run)
- My parse of `example-run/benchmark.json`, per run: mean **59,198 generated tokens** (median 59,840, p90 72,511). Mean **42 LLM calls** (p90 57). Mean **137 actions** (p90 217). That is **1,406 generated tokens per call** and **3.26 actions per call** — [benchmark.json](https://github.com/Tufalabs/duck-harness/tree/main/example-run)
- My parse of the vLLM logs, per server: mean generation throughput 717–726 tok/s (808–826 when ≥ 12 requests were running). Mean prompt throughput **8,024–8,329 tok/s** (9,874–10,208 when busy). Mean 17.5 running requests. Prefix-cache hit rate about 48.6% — [example-run/server-0.log, server-1.log](https://github.com/Tufalabs/duck-harness/tree/main/example-run)
- Human baseline actions per level for game ar25 are [32, 50, 75, 37, 89, 159, 233, 73], about 748 in total — [benchmark.json](https://github.com/Tufalabs/duck-harness/tree/main/example-run)
- **Single RTX PRO 6000, Qwen3.6-27B FP8, vLLM, no MTP, no prompt caching:** 46.1 tok/s single-user decode at 1K context, 30.4 at 256K. Peak **189.3 tok/s at 5 concurrent (1K context)**. 92.5 tok/s at 5 concurrent with 32K context. Peak prefill **9,854 tok/s**. TTFT 170 ms at 1K context and 70 s at 256K — [Millstone AI benchmark](https://www.millstoneai.com/inference-benchmark/qwen3-6-27b-fp8-1x-rtx-pro-6000-blackwell)
- RunPod Blackwell at concurrency 1: TTFT 0.885 s, prefill 1,819 tok/s, decode 38.7 tok/s — [leejianrong artifact doc](https://github.com/leejianrong/solve-arc-agi-3/blob/main/docs/baselines/qwen36-vllm-artifact.md)
- Leejianrong's memo budgets 390 minutes of the 9 h for inference and interaction — [leejianrong memo](https://github.com/leejianrong/solve-arc-agi-3/blob/main/docs/research/2026-09-20-current-state-and-strategy.md)

### Inferences (explicit assumptions; verify on Kaggle)
- **GPU seconds per Duck pass:** the example run used 2 GPUs × 22,231 s = 44,462 GPU-seconds for 500 passes, or **about 89 GPU-s per pass**. From the KV-pool size and the "h100" wheelhouse name, I infer the cluster GPU was an 80 GB H100 (3.35 TB/s, versus 1.6 TB/s on the RTX PRO 6000). Assume the RTX PRO 6000 is 1.5–2.5× slower on this mixed prefill and decode load, so **about 130–220 GPU-s per Duck-style pass**.
- **Usable time:** 9 h minus ~6 min install and load minus ~30–45 min safety margin gives about 7.5–8 h, or 27,000–28,800 s.
- **Passes affordable:** 27,000 / 220 to 28,800 / 130 gives about **120–220 Duck-equivalent passes per submission**. That is **1.1–2.0 passes per game at 110 games, or 2.2–4.0 at 55**.
- **Generated-token budget:** multiply by 59K generated tokens per pass. That is about 7–13M tokens total, or **65–120K per game at 110 games**. If MTP and prefix-cache fixes cut prefill cost, the aggregate can be pushed toward about 20M, or about 180K per game.
- **Call cadence:** at about 1.4K tokens per call, that is **about 50–130 calls per game**. At the Duck's 3.3 actions per call, about 160–430 actions per game. Human baselines are hundreds of actions per game, and the anandsingh8687 target is 0.577 actions/s. The LLM therefore cannot be called every step. Use it to write or verify code (world models, BFS or planners) or to emit multi-action plans, and let cheap CPU code take most actions. The game engine runs about 800 actions/s on CPU.
- **Prefill is the hidden cost.** The Duck processed about 11× more prompt tokens than it generated. On the RTX PRO 6000, peak prefill of about 9.9K tok/s means each uncached 10K-token prompt costs about 1 s of full GPU time. One generated token costs about as much GPU time as ~10–15 uncached prompt tokens at high batch. The biggest levers are cutting prompt size (compact observations, images instead of 4K-token grids, see Q7) and raising the cache hit rate with chunked eviction.
- **Concurrency:** run about 16–32 games at a time against one server. Keep a global deadline monitor, and reallocate time from solved or stuck games to promising ones. The Duck's cluster runs capped each game at 45 minutes.
- **MoE alternative:** Qwen3.6-35B-A3B or Gemma-4-26B-A4B have about 3–4B active parameters versus 27B, so decode is several times cheaper. This could give roughly 3–5× more calls per game at lower per-call quality. It is a real trade-off worth ablating: a per-step policy on the MoE with a code-writer on the dense model.

### Gaps
- The GPU model in the Duck example run is not stated in the logs. The H100 inference is based on the KV-pool size and the wheelhouse name.
- No public measurement of the Duck (or any ARC agent) running end-to-end on a Kaggle RTX PRO 6000 with tokens/s at 16–32 concurrency was found.
- Whether vLLM's "Avg prompt throughput" counts prefix-cache hits could not be verified here. If it does, the uncached prefill load is lower than stated.

---

## Q6. Reasoning ("thinking") vs non-thinking for agentic game play

### Takeaway
The evidence favors **thinking ON with reasoning retained across turns** (`preserve_thinking`), plus context compaction. The winning Duck ran Qwen3.6-27B with thinking on and `preserve_thinking: true`. OpenAI reported that retaining reasoning and compaction roughly tripled a frontier model's ARC-AGI-3 score while using about 6× fewer output tokens. Use Qwen3.8's `reasoning_effort` (low/medium) to fit the token budget, rather than turning thinking off.

### Cited Findings
- Duck config: `analyzer.thinking: true`, temperature 0.6, top_p 0.95, top_k 20, per-request timeout 120 s. The server uses `default_chat_template_kwargs: {"preserve_thinking": true}` and `reasoning_parser: qwen3` — [configs/inference.json](https://github.com/Tufalabs/duck-harness/blob/main/ARC3-Inference/configs/inference.json). This averaged about 1,406 generated tokens per call, thinking included — [benchmark.json analysis](https://github.com/Tufalabs/duck-harness/tree/main/example-run)
- OpenAI (July 30, 2026): with retained reasoning and compaction, GPT-5.6 Sol's public-set score went from 13.3% to 38.3% "while using 6× fewer tokens". Without retention the model "had to figure out the game anew with each action" and "dwelled a long time on each action". With it, the model "spent less time thinking before each action". The standard harness had used rolling truncation above ~175,000 characters — [OpenAI post (via search summary; direct fetch returned 403)](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/); [explainx summary](https://explainx.ai/blog/openai-arc-agi-3-retained-reasoning-compaction-july-2026)
- Reasoning effort matters for frontier models: GPT-5.5 at high effort fully solved 15 of 25 public games (58.12% mean RHAE), versus 8 games (41.29%) for GPT-5.4 at high effort — [ARC Prize analysis (search summary)](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis)
- Qwen3.8 supports `reasoning_effort` xhigh (default), medium and low, plus `preserve_thinking` — [Qwen3.8-27B card](https://huggingface.co/Qwen/Qwen3.8-27B). Gemma 4 has configurable thinking via `enable_thinking` — [Gemma 4 card](https://huggingface.co/google/gemma-4-31B-it). GPT-OSS has low, medium and high — [gpt-oss-120b card](https://huggingface.co/openai/gpt-oss-120b)
- A competitor enables "native thinking for Brain decisions and failed-attempt reviews" only, which is a selective-thinking design — [adityav31121999/arcgames](https://github.com/adityav31121999/arcgames)
- The "Explore Before You Solve" paper frames ARC-AGI-3 as a speed–depth trade-off. Score has "a quadratic penalty" for deviating from the Pareto frontier between action efficiency and information gain. It also notes that many public games are reachable by trivial strategies (10 in a single blind step, 8 via repeated single actions) — [arXiv 2605.25931](https://arxiv.org/abs/2605.25931)

### Inferences
- **Recommended policy:** thinking on, `preserve_thinking` on, `reasoning_effort=medium` by default. Escalate to high or xhigh only for world-model or code-writing and failure-analysis calls. Use non-thinking or low effort for routine "execute plan / parse frame" calls. Mixing modes per call is free because it is a per-request flag.
- Retained reasoning inflates the context, so it must be paired with compaction (summarize old turns) rather than dropping them. Otherwise it collides with the prefix-cache and prefill costs in Q5.
- Cap `max_tokens` per call (for example 2–4K) so one runaway thought cannot stall a game slot. The Duck's chat config used `max_tokens: 2048`.

### Gaps
- No controlled ARC-AGI-3 ablation of thinking vs non-thinking for an open 27–31B model was found. The Duck and the Milestone blog report no such ablation.
- Whether Reki or forge (the Gemma-4-31B agents) enabled thinking is not stated in the Milestone blog.

---

## Q7. Vision: do image inputs help vs ASCII grids for 64×64, 16-colour frames?

### Takeaway
Yes, qualitatively. The winning Duck used **both an image and a text representation**, and Tufa says "the gains came from multimodality and better base models". Both Gemma-4-31B podium entries were image-based policies. Images are also **far cheaper in tokens**: a 64×64 frame upscaled to 256×256 costs about 64 visual tokens in Qwen3.x, versus about 4,100 text tokens for a compact ASCII grid. Qwen3.8-27B's jump on BabyVision (28.9 → 65.7) suggests perception is where the newer model helps most.

### Cited Findings
- Duck: "The model uses both image and text representations of the grid" — [Tufa write-up](https://tufalabs.ai/research/duck-harness/). Multimodal perception includes "rendered images, ASCII grid, segmentation tool". "Gains came from multimodality and better base models, not hand-built tools" and "hand-crafted tools actually hurt the model" — [Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1); [search summary of Tufa / X](https://x.com/tufalabs/status/2072336849465417747)
- Duck multimodal config: `"multimodal": {"context": "current_grid", "upscale": 4}`, so only the current frame is sent as an image, upscaled 4× — [configs/inference.json](https://github.com/Tufalabs/duck-harness/blob/main/ARC3-Inference/configs/inference.json)
- The Tufa article does not provide a quantitative ablation showing the multimodal benefit, and it lists "perception" as an area to improve — [Tufa write-up](https://tufalabs.ai/research/duck-harness/)
- Reki (2nd place): "renders the recent frames as labeled images" for Gemma-4-31B and returns one JSON object with what changed, a short plan and 1–4 actions. It keeps a reflection memory refreshed every ~10 steps — [Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- Another competitor passes the previous and current board as PNG images to an "Eye" chain that checks transitions — [adityav31121999/arcgames](https://github.com/adityav31121999/arcgames)
- Qwen3.6-27B image processor: `patch_size 16`, `merge_size 2`, `shortest_edge 65536` pixels minimum. So a 256×256 image is (256/32)² = **64 visual tokens** — [Qwen3.6-27B preprocessor_config.json](https://huggingface.co/Qwen/Qwen3.6-27B/blob/main/preprocessor_config.json). Gemma 4 uses `max_soft_tokens: 280` per image (patch 16, pooling 3) — [gemma-4-31B-it processor_config.json](https://huggingface.co/google/gemma-4-31B-it/blob/main/processor_config.json)
- **My measurement** with the models' `tokenizer.json`: a 64×64 grid as one hex character per cell (64 rows) is **4,097 tokens** for both Qwen3.6 and Gemma-4. Space-separated decimal is **8,287 tokens**. So digits are tokenized about one per cell — [Qwen3.6-27B tokenizer.json](https://huggingface.co/Qwen/Qwen3.6-27B/blob/main/tokenizer.json); [gemma-4-31B-it tokenizer.json](https://huggingface.co/google/gemma-4-31B-it/blob/main/tokenizer.json)
- Qwen3.8-27B vs Qwen3.6-27B visual reasoning: BabyVision 65.7 vs 28.9 (no code interpreter), ERQA 65.5 vs 62.5, RealWorldQA 85.9 vs 84.1 — [Qwen3.8-27B card](https://huggingface.co/Qwen/Qwen3.8-27B)

### Inferences
- **Send the image by default, and keep the text grid for code.** Put the current frame (and possibly a diff image) in the prompt as an image of about 64–256 tokens. Keep the exact grid inside the Python REPL as a numpy array rather than in the prompt, as the Duck does by exposing game state as Python variables. This cuts per-call prefill by about 4K tokens per frame, the main cost driver in Q5, while keeping exact cell access through code.
- Upscale to at least 256×256 (Qwen's minimum pixel count) so that each 32×32-pixel visual token covers a 4×4 block of cells. An upscale of 8 (512×512, 256 tokens) may help fine detail at a still-modest cost. This is worth an ablation.
- For Gemma-4, images cost a fixed ~280 soft tokens, which is still about 15× cheaper than the ASCII grid.

### Gaps
- No public quantitative ablation (images vs ASCII vs both) on ARC-AGI-3 for open models was found.
- I did not verify how Qwen3.x handles the exact colour palette, that is, whether 16 ARC colours are reliably distinguishable after resizing. It needs a quick test.

---

## Q8. Fine-tuning: would LoRA on synthetic trajectories or world-model-writing traces help? Is anyone doing it?

### Takeaway
None of the Milestone #1 winners report any fine-tuning. The winner explicitly favored a stronger base model and a lighter harness. Fine-tuning is feasible: train off-Kaggle, then ship merged weights or a LoRA as a Kaggle dataset, and open-source it for eligibility. But there is **no ARC-AGI-3 evidence yet** that it helps. Model upgrades (Qwen3.6 → 3.8) are the cheaper, proven lever before Milestone #2.

### Cited Findings
- The Tufa write-up discloses no fine-tuning. Its gains came from "multimodality and better base models" — [Tufa write-up](https://tufalabs.ai/research/duck-harness/); [Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- A competitor's strategy memo says "Fine-tuning is not part of the initial critical path". QLoRA or adapters are considered only under specific conditions, and end-to-end imitation is lower priority — [leejianrong memo](https://github.com/leejianrong/solve-arc-agi-3/blob/main/docs/research/2026-09-20-current-state-and-strategy.md)
- Non-LLM competitors exist, for example a learned transition model with "No LLM at runtime" — [BDR-Pro repo](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3). Another uses a behavior-cloning (BC) policy — [AR6420 repo](https://github.com/AR6420/arc-agi-3-agent). A symbolic Go-Explore BFS agent scores about 0.33 — [samrishtt repo](https://github.com/samrishtt/arc-agi-3-kaggle-competition)
- Relevant methods literature: a systematic study of trajectory-data curation for LoRA fine-tuning of code agents (QLoRA r=64, α=128 on all linear projections of Qwen2.5-Coder-7B) — [arXiv 2607.17205](https://arxiv.org/pdf/2607.17205). "Executable World Models for ARC-AGI-3" uses coding agents to write world models; Tufa says the Duck is "an order of magnitude cheaper" than that approach — [arXiv 2605.05138](https://arxiv.org/html/2605.05138v2); [Tufa write-up](https://tufalabs.ai/research/duck-harness/)
- Tooling: Unsloth provides a Gemma 4 fine-tuning guide — [Unsloth docs](https://unsloth.ai/docs/models/gemma-4/train). All Qwen3.x, Gemma 4 and GPT-OSS weights are Apache-2.0, so fine-tuned derivatives are permitted — [HF cards: Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), [Gemma-4-31B](https://huggingface.co/google/gemma-4-31B-it), [gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b)

### Inferences
- The most plausible fine-tuning target is **distilled world-model-writing traces**. Collect successful traces from a strong teacher (a frontier API or Qwen3.8-Flash-Next offline) that write verified Python world models or planners for public and synthetic games. Then LoRA the 27B student on the assistant turns. This targets the expensive, high-leverage call type.
- Risks: (a) the private games are novel by design, so trajectory imitation on 25 public games risks overfitting; (b) LoRA can degrade general coding and vision; (c) serving a LoRA on top of FP8 in vLLM adds overhead, so merging and re-quantizing to FP8 is preferable.
- With Milestone #2 on Sept 30 (5 days away), fine-tuning is out of scope for this milestone. It is a candidate for the final phase only after harness and model upgrades plateau.

### Gaps
- No ARC-AGI-3 competitor was found reporting a fine-tuned LLM result, positive or negative.
- The size of any synthetic ARC-AGI-3-like game generator was not assessed here. The Duck deploy references a `re-arc-3` repo, but its contents were not examined.
