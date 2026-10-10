# ChatGPT Deep Research prompt: ARC-AGI-3 from ~27 to 40 (Kaggle-only)

Paste everything below the line into ChatGPT with Deep Research turned on.

---

I compete in the Kaggle competition **ARC Prize 2026 – ARC-AGI-3** (interactive game-playing benchmark, scored by
RHAE: per level min(1.15,(human_actions/agent_actions)^2), level k weighted k, game score capped by levels cleared,
mean over games). I need a deep, sourced, practical research report on how to raise my hidden-leaderboard score from
**~27 to 40+ by Nov 2, 2026**, under these hard constraints:

**Constraints**
- Free Kaggle only: one RTX PRO 6000 Blackwell (96 GB) per run, **no internet during the run**, ~30 GPU-h/week,
  ~20 TPU-h/week, 1 submission/day, max 2 concurrent GPU sessions. The scored run plays ~110 hidden games in ~9 hours.
- Final submission must be a Kaggle notebook; weights/data must be shipped as public Kaggle datasets/models.
- No paid APIs or rented GPUs.

**Where I am (facts)**
- Base: Daniel Franzen's open-sourced Milestone-2 notebook (public LB 27.89):
  - Tufa Labs' Duck harness (the LLM plays via a Python REPL);
  - Qwen3.8-Flash-Next (Intel W4A16 AutoRound + INT4 MTP drafter);
  - SGLang Pennyroyal v2.5.3, FP8 KV cache (~1.0M tokens), 128k context, 10 concurrent streams;
  - a priority scheduler P=(A+B)·C;
  - UNDO, animations, 10× images, diff images, persistent Python functions, the world-model note switched off.
- My hidden draws of that notebook: 25.78, 27.88.
- My own tested additions:
  - 12 streams + more memory: safe, no clear gain;
  - "solved-level memory", which pins each cleared level's winning action sequence in the system prompt: safe,
    weakly positive (better in 11 of 25 public games, worse in 7);
  - RESET exposure: no effect.
- Local 25-game tests are very noisy: one all-or-nothing game such as sb26 swings the mean by ±4.
- Leaders: Tufa Labs ~52.5 (153 submissions), Yi-Chia Chen ~48. Neither has published their current method.
- Known from public write-ups:
  - Evidence and memory help, advice text hurts (sirikilohit: FP8 KV + longer history took 14.49→22.53; solved-level
    memory +2.8; added advice cost −2 to −4).
  - Franzen: better models, perception (animations, upscaling), UNDO and throughput mattered most.

**Research questions (answer each with sources, numbers, and a concrete recommendation)**
1. **What are the leaders likely doing?**
   - Collect everything public about Tufa Labs (Duck harness blog, Kaggle discussion 717133, MLST podcast episodes,
     X/Twitter posts by Jeroen Cottaar, Dries Smit, Benjamin Crouzier) and about Yi-Chia Chen.
   - Collect any Kaggle discussion posts or notebooks scoring above 30 since Sep 30, 2026.
   - Separate facts from inference.
2. **Model choice under one 96 GB GPU, offline:**
   - Is there any open-weight model released Aug–Oct 2026 that beats Qwen3.8-Flash-Next for agentic coding or
     game-playing and fits (quantized) with ≥1M tokens of KV cache?
   - Give exact Hugging Face IDs, quantizations, measured tokens/s on RTX PRO 6000 / sm120, and SGLang or vLLM
     support.
3. **Throughput levers** for this exact stack:
   - speculative decoding settings (draft size, acceptance thresholds);
   - FP8 dense layers;
   - KV/Mamba cache sizing;
   - CUDA graphs;
   - prefix caching for long agent histories.
   - Which have measured gains, and what are the risks?
4. **Executable world models / verified simulators with small offline models:**
   - Twin (arXiv 2608.14490), Kepler (arXiv 2610.00834), Prime Agent (arXiv 2608.23552), executable world models
     (arXiv 2605.05138), Agno "Learning Machines", AERA, arc3cb.
   - Is there ANY evidence that a ≤30B-active open model can write useful game simulators or verify hypotheses?
   - What minimal version could work inside the Duck harness (e.g. auto-checking an agent-written `predict()` against
     history, goal falsification from Twin's visual goal signals)?
5. **Goal inference and "wrong-goal loops":** concrete, cheap, evidence-backed methods to detect a stuck level and
   switch hypothesis, with any ARC-AGI-3 results.
6. **Fine-tuning feasibility on free Kaggle TPU/GPU:**
   - LoRA or distillation of Qwen3.8-Flash-Next (or a smaller sibling) on ARC-AGI-3 public-game transcripts.
   - Has anyone done this successfully for ARC-AGI-3 or similar interactive benchmarks?
   - What size and data would be needed, and what is the realistic gain?
7. **Compute allocation across 110 games:** priority scheduling versus equal time. Is there evidence on how score
   scales with tokens per game (diminishing returns curve)?
8. **Evaluation under noise:** the best protocol to compare variants with ~2 GPU runs/day and 1 hidden submission/day
   (paired designs, which games to test on, how many draws are needed to detect +3 points).
9. **Prioritized plan:** a ranked list of the 5–8 changes most likely to add points by Nov 2. For each:
   - expected gain range;
   - evidence;
   - implementation effort in hours;
   - risk.

   Then give an honest probability of reaching 30, 35 and 40 hidden.

**Output format**
- An executive summary (10 lines).
- One section per question.
- A final ranked action table.
- Inline citations with URLs and dates.
- Mark every inference as inference.
- Prefer 2026 sources.
- Be honest where evidence is missing.
