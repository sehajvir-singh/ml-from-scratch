# Top-team intel: how the 15–19.5% ARC-AGI-3 Kaggle teams got there (as of 2026-09-25)

Scope and method:
- This file adds new evidence on top of `research_notes/ARC AGI 3 winning strategy/kaggle_top_approaches.md`. It does not repeat the Duck description, the LB top 20, or the Milestone-1 details.
- Kaggle data were re-pulled live on 2026-09-25 (~20:10 UTC) through Kaggle's internal JSON API:
  - the 200 most active discussion topics, with every comment;
  - 1,100 public competition notebooks;
  - public datasets and models of all 49 members of the top-14 teams;
  - Kaggle profiles.
- Per-team daily score history comes from Tong Hui Kang's tracker data (`hist.json`, cached from arc3.huikang.dev earlier today).
- GitHub forks and branches were read with `git ls-remote` and `git log`.
- Every "Inference" bullet is my reasoning, not a sourced fact.

---

## Q1. What has each top team said publicly, and where?

### Takeaway
None of the top-6 teams has published a method.
- Lord Han Solo (#1), Yi-Chia Chen (#3) and Daniel Franzen (#4) have posted nothing in the competition forum, published no notebooks, and released no competition-related models or datasets.
- Tufa Labs and NVARC3 (via CPMP) have spoken only about process and open-sourcing policy.
- Tong Hui Kang has spoken only about rules and his conditional plan to share.
- The most useful hard evidence is indirect: GitHub forks and branches (Tufa, NVARC3's Ivan Sorokin) and model artifacts on public profiles.

### Cited Findings

**Forum-wide scan**
- I scanned all 200 active topics and every comment for posts by all 49 members of the top-14 teams. Nothing was posted by Lord Han Solo, Yi-Chia Chen, Daniel Franzen, ivan (Sorokin), Darragh, Elad Sarafian, Gal Kaplun or Yeyin Zhu.
  - The NVARC3 posts are all by CPMP.
  - The Tufa posts are by Jeroen Cottaar, Dries Smit and InfiniteCreativity, and none after July describes a method.
  - Source: [Kaggle discussion forum](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion), pulled via API.
- Of 1,100 public competition notebooks, the only ones from top-6 members are Tufa's June/July Milestone-1 notebooks:
  - [taaf-duck-harness-kaggle](https://www.kaggle.com/code/jeroencottaar/taaf-duck-harness-kaggle) (1.30);
  - [tufa-labs-duck-harness-june-30-milestone-winner](https://www.kaggle.com/code/jeroencottaar/tufa-labs-duck-harness-june-30-milestone-winner) (1.25);
  - [simplified-submission-approach](https://www.kaggle.com/code/jeroencottaar/simplified-submission-approach).

**Lord Han Solo (19.45; solo; 73 submissions)**
- Kaggle profile:
  - joined 2020-08-28; tier Contributor; "Software Engineer", Białystok, Poland;
  - bio: "Looking for job";
  - no GitHub, Twitter, LinkedIn or website listed.
  - Source: [kaggle.com/lordhansolo](https://www.kaggle.com/lordhansolo) (profile API).
- No public datasets or models.
- Web searches for the handle plus ARC-AGI-3 return only the leaderboard — [web search](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard).
- The only public mention of the team is Scott Le Grand's comment: "congrats to Lord Han Solo, life comes at you fast" — [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).

**Yi-Chia Chen (18.63; solo; only 11 submissions)**
- Kaggle profile: Kaggle Master; "Double Degree Student, National Taiwan University and Waseda University", Taipei — [kaggle.com/threerabbits](https://www.kaggle.com/threerabbits).
- She has no ARC-3 posts. Her public Kaggle models, all created 2026-06-24 (i.e. before her first ARC-3 LB score on 2026-08-20), show a sophisticated LLM post-training and serving skill set:
  - [`threerabbits/opd-32b-v33-s200-gptq-w4a16`](https://www.kaggle.com/models/threerabbits/opd-32b-v33-s200-gptq-w4a16): an "OPD" (on-policy distillation) run, v33 at step 200. The base is an `Olmo3SinkForCausalLM` 32B (hidden 5120, sliding/full attention). It is GPTQ W4A16 with an FP8 KV-cache scheme (per its `recipe.yaml`).
  - [`threerabbits/dflash-32b-draft-v2test-phasel`](https://www.kaggle.com/models/threerabbits/dflash-32b-draft-v2test-phasel) and an `-int4mlp` variant: a self-trained **DFlash** block-diffusion speculative-decoding draft. It has 8 layers, `block_size` 11, and taps target layers 1/10/18/27/35/44/52/61.
  - Her June datasets are named `proof-pilot-code` and `proof-pilot-env`.
  - Sources: Kaggle Models API, file listings and `config.json`/`recipe.yaml`.
- Her LB trajectory:
  - 1.60 (08-20), 3.24 (09-12), 4.79 (09-17);
  - then **12.88 (09-19)**, 15.98 (09-21), **18.63 (09-24)**.
  - Source: [arc3.huikang.dev tracker](https://arc3.huikang.dev/leaderboard).

**Daniel Franzen (16.68; solo; 82 submissions)**
- Kaggle profile: "Deep Learning Researcher at the University of Mainz… PhD Thesis on Equivariant Neural Networks"; GitHub `da-fr`; [LinkedIn](https://www.linkedin.com/in/daniel-franzen-9609b7334/) — [kaggle.com/dfranzen](https://www.kaggle.com/dfranzen).
- Of the ARChitects (1st in ARC Prize 2024, 53.5%) — [ARC Prize on X](https://x.com/arcprize/status/1865106288012623887).
- Nothing on ARC-AGI-3 is public:
  - GitHub `da-fr` was last updated 2026-04-28 (homepage). The ARC repos are 2024–2025 (`arc-prize-2024`, `Product-of-Experts-ARC-Paper`) — [github.com/da-fr](https://github.com/da-fr?tab=repositories).
  - His newest public Kaggle models are 2025-10 ARC-AGI-2 artifacts: `lladamix1400k-…-4b`, a **LLaDA** masked-diffusion LM with a custom `modeling_llada.py`, and `wb55l_nemomini_fulleval` — [Kaggle models](https://www.kaggle.com/models/dfranzen/lladamix1400k-l45-m20-k1-gg2m-3uof4lei-size230k-4b).

**NVARC3 (16.07; 20 submissions)**
- Members: CPMP (Jean-François Puget), Darragh, ivan (Ivan Sorokin, team leader), Elad Sarafian, Gal Kaplun, Yeyin Zhu — [Kaggle LB](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard).
- CPMP on open-sourcing: "I don't think we will share either… we value medals and ranking way more than money prize… We will open source our code at the end of competition if we end up in gold. As usual for NVIDIA teams." — [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
- CPMP on public code: "We only use publicly available code/models, i.e. no private sharing within NVIDIA outside Kaggle teams." — [739186](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739186).
- CPMP on compute:
  - "we are not the teams using most GPUs on Kaggle."
  - A realistic NVIDIA example: "Second place from NVIDIA [Orbit Wars] used 1 8xH100 node iirc."
  - The 512×H100 AIMO training "was for a Nemotron model NVIDIA released… the outlier."
  - Source: [740812](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740812).
- CPMP on synthetic data: self-generated synthetic data "never was considered as external data in past competition. For instance we generated a large dataset last year and won arc agi2 competition with it. We shared it with our solution, after competition deadline." — [742940](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742940).
- CPMP after Tufa's jump: "when some teams get a high score, here Tufa Labs, other teams start catching up as they see what is achievable… Similar thing happened in ARC AGI2 where our 30+ lead evaporated." — [739186](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739186).
- CPMP on queue waits (2026-09-22): "My team mate Darragh waited more than 10 hours to get his running yesterday." — [742148](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742148).

**Tufa Labs (18.81)**
- The only post since July is the 2026-09-23 no-share statement: "not so obvious that big improvements are still possible in the limited time that remains… We remain fully committed to sharing our final solution when the competition ends." — [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
- Tufa website repo: the last content commits (2026-09-07) are only a Milestone-1 news item and a Tufa Talks announcement.
  - Michal Tešnar was removed from the team page on 2026-08-18. He is also not on the Kaggle team.
  - Source: [github.com/Tufalabs/website](https://github.com/Tufalabs/website) (git log).
- The Tufa research page has no post after 2026-07-18 — [tufalabs.ai/research](https://tufalabs.ai/research/).

**Tong Hui Kang (15.02)** — see Q4.

**mostik.ai (7.51; stopped 2026-09-06)**
- CEO Sasha Malysheva tweeted: "what happens when you put 12 PhDs in one room for four months? first place on the ARC-AGI leaderboard, which I can't say much about while the competition is still running" — [x.com/aimalysheva](https://x.com/aimalysheva/status/2095232794792255848) (quoted in [739186](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739186)).
- Their public product is a learned "bridge matrix" that projects hidden states of a frozen large model (GLM-5.2, 753B) into the latent input of a small model (Qwen-3.5 4B). It claims ~80% of the large model's accuracy at ~1/20 the cost.
  - The team is 15 people including Fields medalist Stanislav Smirnov.
  - "Deliberately kept details limited while the competition is still running."
  - Source: [Ascendants article](https://ascendants.in/the-ascendants/mostik-ai-latent-space-frontier-small-model-reasoning/).

**Other ≥10% teams**
- "the last dance 🕺" (13.70): gklambauer, fses91, M I (dwellement0baser), Lukas Aichberger. It has posted nothing on method; fses91 only congratulated Tufa — [716696](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716696).
- Matija Ludvig & Zhongwei Wang (11.64): posted only a teammate search (2026-09-10) — [740604](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740604).
- Fususu (10.66, solo):
  - Is the most open. Tried Gemma 4 31B ("falls far behind… logic and coding"), a "system decoder" to pre-parse objects, and a 4–5 role LLM split (too many calls for the Kaggle budget) — [739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).
  - Tried DeepSeek V4 Flash: "decoding speed is low. And the vision not work." Holds a Kaggle model `phuongncn/arc3-dsv4-flash-weights` — [742788](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742788).
  - Local-vs-LB: "public I got 22.26, submit → LB got 5.37… 17.34 → 6.91" — [732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).

### Inferences
- Three of the top four are solo entrants with no public ARC-3 footprint. Nothing can be reproduced directly from them before the end of the competition (2026-11-02).
- Yi-Chia Chen's artifacts show she can train her own on-policy-distilled 32B models and her own DFlash speculative drafts, and quantize them with GPTQ and an FP8 KV cache. Her 11-submission climb (4.79 → 18.63 in one week) fits one of two patterns:
  1. a privately trained or distilled checkpoint (for example, OPD of Flash-Next or a 27B on self-generated ARC-3 trajectories); or
  2. a throughput jump from a custom speculative draft.
  This is speculation. Her June models are for a different (proof-oriented) task.

### Gaps
- I found no X, LinkedIn, blog or podcast statement on ARC-3 method by Lord Han Solo, Yi-Chia Chen, Daniel Franzen or any NVARC3 member. X pages returned HTTP 402 to the fetcher, so I could not scan X timelines directly.

---

## Q2. What model does each team use? Did any fine-tune, and how?

### Takeaway
No top team has confirmed its model or any fine-tuning.
- Hard evidence exists for only one team. NVARC3 is running **Qwen3.8-Flash-Next on a patched vLLM with FP8 KV cache**.
- Tufa's public trail runs through Qwen3.8-27B-FP8 (Aug 18). On 2026-09-09 they forked a full RL/serving stack (miles, verl, sglang, vllm, transformer-engine, flash-attention, flashinfer).
- Community consensus is that the top teams fine-tune, but no one has confirmed it. Community reports say full fine-tuning of Flash-Next is not possible on the RTX Pro 6000 and needs an H200 node.

### Cited Findings

**NVARC3 (confirmed engine, not weights)**
- Ivan Sorokin's vLLM fork has branches `qwen-flash-next` and `codex/qwen-flash-next-fp8-kv-cache`.
  - The first carries Alibaba's "support PLE-Offload for Qwen3.8-Flash-Next" (2026-08-26) plus fixes up to 2026-09-05.
  - The second adds commit `a4d0a70` (2026-09-07), "[Model] Qwen4Exp: fp8_e4m3 main KV cache on the QSA path — Port vLLM PR #55557 … onto qwen-flash-next. Signed-off-by: Ivan Sorokin".
  - Source: [github.com/1ytic/vllm](https://github.com/1ytic/vllm/tree/codex/qwen-flash-next-fp8-kv-cache); [commit a4d0a70](https://github.com/1ytic/vllm/commit/a4d0a70693c12713873583c8edea1761909e4983).
- Upstream PR #55557 was merged 2026-09-16. On the RTX PRO 6000 (SM120):
  - "KV pool increased from ~434K to ~772K tokens (1.77×)";
  - prefill about the same (11.0k vs 11.2k tok/s);
  - logprob deltas within noise;
  - with MTP on, draft acceptance drops ~10% and decode ~7–11%.
  - Source: [vllm PR #55557](https://github.com/vllm-project/vllm/pull/55557).
- NVARC3's first LB score came on 2026-09-06, the day before this port (3.32 → 5.96 on 09-07) — [tracker](https://arc3.huikang.dev/leaderboard).
- Sorokin's public NVARC-era Kaggle models are ARC-AGI-2 4B/2B grid SFTs (`qwen3_4b_grids15_sft139`, 2025-11-02). They have no ARC-3 weights — [Kaggle models](https://www.kaggle.com/models/sorokin/qwen3_4b_grids15_sft139).

**Tufa Labs**
- Dries Smit's public Kaggle datasets include `qwen3-8-27b-fp8-hf-017b9c7a`, updated 2026-08-18, the day before Tufa's 2.07 → 2.97 → 4.58 run on Aug 19–23. There is no public Flash-Next or fine-tuned dataset.
  - Private datasets are invisible to the API.
  - Source: [Kaggle datasets API, driessmit1](https://www.kaggle.com/driessmit1/datasets).
- Tufa's GitHub org has fresh forks, all updated **2026-09-09**:
  - **miles** (RadixArk's "enterprise-facing reinforcement learning framework for LLM and VLM post-training");
  - **verl**;
  - **sglang**, **vllm**, **transformers**, **transformer-engine**, **flash-attention**, **flashinfer**.
  - Only `main` branches are public, with no Tufa-specific commits visible.
  - Source: [github.com/Tufalabs](https://github.com/Tufalabs) (git ls-remote).
- Tufa's relevant published research:
  - "A Predictive Law for On-Policy Self-Distillation From World Feedback" (Tommy He, Jerome Sieber, Matteo Saponati; 2026-05-28). It positions OPSD as an alternative to GRPO for "richer feedback signals" — [arXiv 2605.30070](https://arxiv.org/abs/2605.30070).
  - Isaiah Pressman (a Kaggle-team member) won Kaggle Orbit Wars with PPO self-play on 4×8×B200 (~2,400 B200-hours) — [Tufa blog](https://tufalabs.ai/research/orbit-wars/).
- Community speculation:
  - Scott Le Grand: "My guess is part of that is some fine tuning" — [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
  - Penguin: "they have 10s of TB of gpu vram, allowing continuous testing of different harnesses" — [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).

**Yi-Chia Chen**
- No ARC-3 model is public. Her June 2026 OPD-32B and DFlash drafts show the capability (see Q1) — [Kaggle models](https://www.kaggle.com/models/threerabbits/opd-32b-v33-s200-gptq-w4a16).

**Lord Han Solo and Daniel Franzen**
- No evidence either way.

**Feasibility reports from the forum**
- AAAAAtjc: "I successfully built and validated rl training pipeline of Qwen 3.8 Next Flash based miles, but I did not gain any performance… I used a full H200 node. rtx 6000 pro can not be used for training of any ~100B model even with aggressive cpu offload and quantization" (2026-09-24) — [742835](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742835).
- OverfitOracle: "RL is possible for the qwen 3.8 27b after high quantization (still need good compute) but on the flash next model its impossible unless you are an nvidia guy" — [732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).
- Scott Le Grand:
  - local 11.04 without fine-tuning vs **12.97 with behavioral cloning**;
  - "you have to use reasoning traces from the same model or it's a regression";
  - Source: [732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).
  - Separately: "Not sure whether it's more promising to distill into a smaller Qwen or just fine-tune the 120B-fp4 variant" — [742788](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742788).
- manas joshi, STaR LoRA on Duck + Qwen3.6-27B:
  - LoRA-SFT on the agent's own level-completing trajectories raised the LB from **1.25 → 1.94**;
  - "naively scaling the data hurt… Curation > quantity"; adapters are base-model-specific;
  - datasets `arc3-sft-trajectories`, `arc3-duck-lora-sft`, `duck-eval-results` are CC0;
  - Source: [739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047).
- wkdrbwnd1 (2026-09-25): small adapter trained on 31 own trajectories from 20 public games; evaluated on 5 held-out games (lp85, r11l, sc25, sp80, su15).
  - "weighted" loss (tool-call tokens 1.0, reasoning 0.3): avg **25.07**.
  - "labeled" loss (game-specific reasoning down-weighted to 0.1): avg **4.99**. It collapsed into turns with no tool call (1,474 of 4,767).
  - Source: [743319](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743319).
- Ya Xu: "I used to believe that LORA was the trick… the result only backfired on me" — [739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047).

**Alternative bases others tried**
- DeepSeek V4 Flash:
  - Son Pham: to fit it "you have to do a lot of shenanigans like quantization and pruning of experts… the token efficiency just wasn't equal to Flash Next";
  - Russell Kirk and Fususu also negative;
  - Source: [742788](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742788).
- DeepSeek-V4.1-Flash (released 2026-09-10) is 552B total — [llm-stats](https://llm-stats.com/llm-updates).
- GLM-5.3-Flash-NVFP4 is 168 GB of safetensors — [HF RadixArk/GLM-5.3-Flash-NVFP4](https://huggingface.co/RadixArk/GLM-5.3-Flash-NVFP4).
- Qwen3.8-Flash-Next exposes `reasoning_effort` (xhigh/medium/low) and has both thinking and instruct modes — [local-ai-zone deep dive](https://local-ai-zone.github.io/blog/qwen3-8-flash-next-deep-dive.html).

### Inferences
- The base model for the 15–19% teams is almost certainly Qwen3.8-Flash-Next:
  - NVARC3 is confirmed at the engine level;
  - the other candidates (DeepSeek V4/V4.1 Flash, GLM-5.3-Flash) do not fit 96 GB or were reported worse.
  - Fine-tuning Flash-Next needs off-Kaggle compute (an H200/B200 node), which Tufa and NVIDIA have. The Tufa fork of miles and verl on Sep 9 fits RL or OPSD post-training (miles is the stack AAAAAtjc used for Flash-Next RL). Circumstantial, not confirmed.
- Two things are directly reproducible for B81:
  1. Port vLLM PR #55557 (FP8 KV on QSA, now merged upstream) to get ~1.77× KV capacity. That buys either more concurrent games or a larger working context without eviction. Check the MTP interaction: acceptance −10%.
  2. STaR-style SFT on the agent's own successful trajectories. Keep tool-call tokens at full weight. Do not down-weight reasoning to the point of collapse. Curate rather than scale. This is only practical on a 27B-class model or a LoRA on Flash-Next rented off-Kaggle.

### Gaps
- No top team's weights, training data or recipe is visible.
- Tufa's forks carry no public diffs.
- Whether any top team fine-tuned at all is unconfirmed.

---

## Q3. Tufa Labs jumped from 11.04 to 18.81 between Sep 6 and Sep 13. What changed?

### Takeaway
Nothing public explains it. No model release fits that window. Tufa said nothing.
- The only dated signal is Tufa's 2026-09-09 fork of an RL post-training and serving stack (miles/verl/sglang/vllm/flash-attn/flashinfer/TE). It falls between the two scores.
- The earlier step (4.71 → 11.04 on Sep 6) follows the Flash-Next release (Aug 26) and the PLE-offload vLLM support.

### Cited Findings
- Tufa's daily best:
  - 1.62 (08-10); 2.07 (08-19); 2.97 (08-20); 4.58 (08-23); 4.71 (08-30);
  - **11.04 (09-06)**; **18.81 (09-13)**; unchanged through 09-25, with the last submission 2026-09-23.
  - Source: [arc3.huikang.dev tracker](https://arc3.huikang.dev/leaderboard); [Kaggle LB API](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard).
- Model and engine dates around the window:
  - Qwen3.8-Flash-Next: released 2026-08-26 — [local-ai-zone](https://local-ai-zone.github.io/blog/qwen3-8-flash-next-deep-dive.html). The RadixArk NVFP4 was uploaded 2026-08-25 — [HF](https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4).
  - DeepSeek-V4.1-Flash: 2026-09-10, 552B — [llm-stats](https://llm-stats.com/llm-updates).
  - GLM-5.3 / GLM-5.3-Flash NVFP4: late Aug, too large — [HF RadixArk](https://huggingface.co/RadixArk).
  - vLLM FP8-KV-for-QSA PR: merged 2026-09-16 — [PR #55557](https://github.com/vllm-project/vllm/pull/55557).
  - No relevant open model fitting 96 GB was released 2026-09-06…13.
- Tufa's forks of miles, verl, sglang, vllm, transformers, transformer-engine, flash-attention and flashinfer were all updated 2026-09-09 — [github.com/Tufalabs](https://github.com/Tufalabs).
- Jeroen Cottaar (2026-09-23) wrote "we knew that our harness was just the beginning". He now doubts "big improvements are still possible in the limited time that remains" — [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
- A Tufa member researches on-policy self-distillation from world feedback — [arXiv 2605.30070](https://arxiv.org/abs/2605.30070).
- Tufa won Orbit Wars with large-scale PPO — [Tufa blog](https://tufalabs.ai/research/orbit-wars/).

### Inferences
- Most likely explanation, with medium confidence: a Tufa-trained Flash-Next (or 27B) checkpoint, post-trained with RL or OPSD/STaR on the agent's own Duck trajectories. The evidence is:
  - the timing of the Sep 9 RL-stack fork;
  - their published OPSD and PPO expertise;
  - the size of the jump (+70%) with no public model release.
- Alternatives cannot be excluded: a major harness change (Tufa is known for harness work) or a lucky draw. The LB is a max over noisy draws, and Tufa has 146 submissions.
- The fact that Tufa did not improve after Sep 13 despite continued submissions suggests 18.81 may be a high draw of that system.

### Gaps
- There is no public diff, model, blog post or tweet from Tufa about Sep 6–13.
- The X feed (@tufalabs) could not be fetched (HTTP 402).

---

## Q4. What has Tong Hui Kang said he will publish for Milestone #2, and what is in his code today?

### Takeaway
His commitment is conditional and is about his notebook only:
- "very likely to share my solution if no higher placed teams is sharing their solution. If I only make it into top 3, I might not share."

His repeated questions about whether a fine-tuned model's dataset and training script must be published hint that his solution may include a fine-tuned model. This is an inference. His public code has no current agent: only the leaderboard monitor and a May "autoresearch" imitation-learning experiment, which he himself disclaims.

### Cited Findings

**Intentions**
- [Sep 24 11:00 PST] "I am 8th place currently. Tentatively, I will share my solution if I manage to make it into top 3 who intend to share their solution."
- [Sep 24 20:00 PST] "I am 5th place currently. Tentatively, I will very likely to share my solution if no higher placed teams is sharing their solution. If I only make it into top 3, I might not share my solution. (I will keep my intention updated)"
- Source: [742935](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742935).
- He is #6 at 15.02 as of 2026-09-25, after Yi-Chia Chen's 18.63 — [Kaggle LB](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard).

**Rules questions (Aug 27 and Sep 23)**
- He expects "Top teams will publish their notebook (together with all the dependencies…) one or two hours before the deadline" and "If a fine-tuned model is used, the model has to be published before the deadline."
- He asks whether "the dataset and the fine-tuning script" must also be published.
- Sources: [705043](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705043); [742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
- In June he asked: "If I train a NN model can I just publish the weights or do I need to publish the dataset as well?" — [705043](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705043).

**Game-name note (2026-08-31)**
- He posted mnemonic names for all 25 public games, e.g. ar25 axis-reflections, bp35 buoyancy-puzzle, ft09 flip-tiles, ls20 lock-smith, sk48 sliding-kebab, tu93 traverse-unharmed, wa30 warehouse-agents. This suggests he studies games individually — [738294](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738294).

**LB trajectory**
- 0.80 (06-29); 1.06 (08-22); 2.24 (08-23); 3.39 (08-25); 4.45 (08-31); 5.13 (09-08); 6.65 (09-14); 8.72 (09-16); 10.78 (09-21); **15.02 (09-24)**.
- 83 submissions; steady, incremental gains — [tracker](https://arc3.huikang.dev/leaderboard).

**Code today**
- [github.com/tonghuikang/arc3](https://github.com/tonghuikang/arc3) (last commit 2026-07-22) contains:
  - `leaderboard/`: the minute-level Kaggle LB monitor on Modal, which serves arc3.huikang.dev.
  - `autoresearch/`: the loss and feature-layout code for a small CNN/ViT imitation policy. The input is 384 binary features per cell: 4×16-colour groups, 6 previous frames each with action one-hots and changed/clicked masks, the first and last frame of the previous level, and x/y one-hot planes. It has action, colour and click heads.
    - "The `Model` architecture itself lives in the training repo and is intentionally not published."
    - It was trained on "ideal gameplay traces" on self-made "modified games" (same engines, altered shapes) and validated on the originals.
- His blog (added Aug 2026): "I do not believe that curve-fitting a model on (history, actions) dataset is on the critical path… I have no evidence that the trained model is performing better than a model that simply takes random actions" — [blog post](https://github.com/tonghuikang/blog/blob/master/_posts/2026-05-31-autoresearch-hackathon.md).
- Other repos:
  - `inference` (Apr 2026) is a nano-vLLM clone for GB10, unrelated.
  - `nemotron` is his NVIDIA Nemotron Reasoning Challenge progress-prize-winning adapter pipeline (117★), so he has done fine-tuning before.
  - Source: [github.com/tonghuikang](https://github.com/tonghuikang?tab=repositories).
- He has no public ARC-3 Kaggle notebooks, datasets or models. His Kaggle models are Nemotron/AIMO/Qwen2.5-era — [Kaggle API](https://www.kaggle.com/huikang/models).

### Inferences
- If THK publishes on 2026-09-30, it will likely be:
  - a Duck/Flash-Next-lineage notebook; plus
  - possibly a fine-tuned checkpoint, given his repeated fine-tune publication questions and his Nemotron adapter track record.
- By his own precedent, publication would come 1–2 h before the deadline. It may be the best reproducible reference for a 15% system.

### Gaps
- There is no statement of his current base model, harness changes, or whether he fine-tunes.

---

## Q5. Is Daniel Franzen using test-time training on ARC-AGI-3?

### Takeaway
Unknown. There is no public statement, code or artifact for ARC-3.
- His score path looks like steady harness or engine iteration on the public-model waves, not a distinct TTT signature.
- TTT of a ~120B MoE inside a 9-hour, 110-game budget on one RTX Pro 6000 is implausible. A small-model TTT side component cannot be excluded.

### Cited Findings
- Franzen's LB:
  - 1.24 (07-27); **2.58 (08-14)** — the day of the Qwen 3.8 release thread; 3.04–4.05 (08-27…30); 4.49 (09-03);
  - **6.66 (09-04)**; 7.63 (09-05); **11.59 (09-16)**; 13.12 (09-17); **16.68 (09-24)**.
  - 82 submissions.
  - Sources: [tracker](https://arc3.huikang.dev/leaderboard); [Qwen 3.8 release thread 735243](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735243).
- His ARC-AGI-2 (2025) public artifacts: a 4-bit LLaDA diffusion-LM "LladaMix" and a NeMo-Minitron-8B model (Oct 2025) — [Kaggle models](https://www.kaggle.com/models/dfranzen/lladamix1400k-l45-m20-k1-gg2m-3uof4lei-size230k-4b); [HF da-fr](https://huggingface.co/da-fr).
- His ARChitects 2024 method (TTT plus product-of-experts augmentation scoring) is in [da-fr/arc-prize-2024](https://github.com/da-fr/arc-prize-2024) and [Product-of-Experts-ARC-Paper](https://github.com/da-fr/Product-of-Experts-ARC-Paper). No 2026 ARC-3 update — [github.com/da-fr](https://github.com/da-fr?tab=repositories).
- Flash-Next is a 125B MoE (+51B n-gram embeddings). Community members report even offline training does not fit an RTX 6000 Pro — [742835](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742835).

### Inferences
- His step on 08-14 lines up with Qwen 3.8 27B. The 09-04 step comes after Flash-Next and PLE-offload vLLM. The 09-16 step lines up with the FP8-KV PR merge and the cluster of other teams' jumps (see Q7). So most of his rise tracks public model and engine releases plus iteration.
- A "perspective/augmentation" idea (his PoE work) could transfer to ARC-3 as frame-representation augmentations or self-consistency voting over actions. That is speculative.

### Gaps
- No evidence about TTT, fine-tuning, or his base model.

---

## Q6. NVARC3: links to DreamTeam (arXiv 2605.09650) or NVARC's ARC-AGI-2 synthetic-data recipe?

### Takeaway
Personnel links are confirmed. Method links are not.
- Two NVARC3 members, Elad Sarafian and Gal Kaplun, are the first two authors of DreamTeam / "Workspace Optimization".
- Ivan Sorokin and CPMP are the NVARC ARC-AGI-2 winners, whose recipe was synthetic data + SFT/TTT of a 4B model.
- NVIDIA's `dream-team` repo ships a **Game Creator** and 25 generated ARC-3-style games.
- CPMP has publicly argued that self-generated synthetic data is not "External Data". This fits a plan to train on synthetic games. Not confirmed.
- The confirmed Kaggle engine is Qwen3.8-Flash-Next + vLLM + FP8 KV.

### Cited Findings
- arXiv 2605.09650, "Workspace Optimization: How to Train Your Agent":
  - authors Elad Sarafian, Gal Kaplun, Ron Banner, Daniel Soudry, Boris Ginsburg (NVIDIA), 2026-05-10;
  - DreamTeam is a multi-agent harness whose roles "build an executable world model, plan, hypothesize, probe, strategize, and route failures";
  - it scores 38.4% (vs 36%) on the 25 public games with frontier models;
  - Source: [arXiv 2605.09650](https://arxiv.org/abs/2605.09650).
- [github.com/NVIDIA/dream-team](https://github.com/NVIDIA/dream-team) contains:
  - the TeamSolver algorithm and the "beam" agent framework;
  - a standalone **Game Creator** plus "25 pre-generated curated games";
  - LLMs via OpenAI-compatible gateways (`llm_configs.yaml`);
  - an Apache-2.0 licence and no mention of Kaggle.
  - It was flagged as a source of non-official training games in [736540](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/736540).
- NVARC3 roster: CPMP, Darragh, ivan (Sorokin), Elad Sarafian, Gal Kaplun, Yeyin Zhu — [Kaggle LB](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard).
- NVARC ARC-AGI-2 (2025) won with a 4B fine-tuned model plus synthetic puzzles and TTT — [NVIDIA blog](https://developer.nvidia.com/blog/nvidia-kaggle-grandmasters-win-artificial-general-intelligence-competition/); [1ytic/NVARC](https://github.com/1ytic/NVARC).
  - Its datasets are public: `sorokin/nvarc-synthetic-puzzles`, `nvarc-augmented-puzzles`, `nvarc-artifacts-puzzles` — [Kaggle](https://www.kaggle.com/sorokin/datasets).
- CPMP on 2026-09-24: generated datasets "never was considered as external data… we generated a large dataset last year and won arc agi2 competition with it. We shared it with our solution, after competition deadline" — [742940](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742940).
- NVARC3's engine: Sorokin's `qwen-flash-next` vLLM branch with FP8 KV port, 2026-09-07 — [1ytic/vllm](https://github.com/1ytic/vllm/tree/codex/qwen-flash-next-fp8-kv-cache).
- NVARC3 LB: 3.32 (09-06) → 5.96 (09-07) → 7.69 (09-10) → 8.40 (09-11) → 11.04 (09-16) → **16.07 (09-19)**; 20 submissions — [tracker](https://arc3.huikang.dev/leaderboard).
- NVIDIA's AVO blog (100% on the public 25 with frontier models) was suggested by a participant as an inspiration source — [737617](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/737617); [NVIDIA AVO blog](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/).

### Inferences
- A plausible NVARC3 recipe:
  1. Use DreamTeam's Game Creator to generate many synthetic ARC-3 games.
  2. Roll out a local agent (and/or frontier DreamTeam) on them.
  3. Distill or SFT Flash-Next on the resulting trajectories.
  4. Run it in a DreamTeam- or Duck-style harness on vLLM with FP8 KV.
  This combines their two known assets (synthetic data at scale plus the DreamTeam world-model harness). It is unconfirmed.
- The reproducible part for us: NVIDIA's Game Creator and its 25 generated games are an Apache-2.0 source of held-out or training games. That directly addresses Scott Le Grand's point that the public 25 are easier than the hidden set — [740812](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740812).

### Gaps
- No NVARC3 statement names the harness, whether fine-tuning was done, or whether DreamTeam games were used.

---

## Q7. Leaderboard history: score jumps and whether they line up with model releases

### Takeaway
There are three waves.
1. **Qwen3.8-27B (Aug 14–23)**: top about 2.5–5.
2. **Qwen3.8-Flash-Next plus PLE-offload vLLM (Aug 24 – Sep 7)**: mostik 5.99/7.51, Franzen 6.66, NVARC3 5.96, Tufa 11.04.
3. **A non-release wave (Sep 13–24)**, triggered by Tufa's 18.81 on Sep 13. Six other teams passed 11–19 within 11 days, clustered Sep 16–24.
   - The only public artifact in that window is the vLLM FP8-KV merge (Sep 16).
   - No new model fits 96 GB.

### Cited Findings

Per-team daily score steps (date: best score). Source: [arc3.huikang.dev](https://arc3.huikang.dev/leaderboard) history as of 2026-09-25.

| Team | Steps |
|---|---|
| Lord Han Solo | 1.65 (08-04) → **2.76 (08-16)** → 3.36 (08-22) → **4.99 (08-24)** → 5.04 (09-09) → 6.43 (09-12) → 8.44 (09-13) → 8.84 (09-15) → 9.81 (09-16) → 11.54 (09-18) → **15.60 (09-19)** → **18.42 (09-20)** → 19.40 (09-22) → 19.45 (09-24) |
| Tufa Labs | 1.62 (08-10) → 2.07 (08-19) → 2.97 (08-20) → **4.58 (08-23)** → 4.71 (08-30) → **11.04 (09-06)** → **18.81 (09-13)** |
| Yi-Chia Chen | 1.60 (08-20) → 3.24 (09-12) → 4.79 (09-17) → **12.88 (09-19)** → 15.98 (09-21) → **18.63 (09-24)** |
| Daniel Franzen | 1.24 (07-27) → **2.58 (08-14)** → 3.15 (08-28) → 4.05 (08-30) → 4.49 (09-03) → **6.66 (09-04)** → 7.63 (09-05) → **11.59 (09-16)** → 13.12 (09-17) → **16.68 (09-24)** |
| NVARC3 | 3.32 (09-06) → 5.96 (09-07) → 7.69 (09-10) → 8.40 (09-11) → 11.04 (09-16) → **16.07 (09-19)** |
| Tong Hui Kang | 1.06 (08-22) → 2.24 (08-23) → 3.39 (08-25) → 4.45 (08-31) → 5.13 (09-08) → 6.65 (09-14) → 8.72 (09-16) → 10.78 (09-21) → **15.02 (09-24)** |
| the last dance | 3.54 (09-05) → 5.14 (09-14) → 6.96 (09-19) → 9.26 (09-21) → 11.09 (09-22) → **13.70 (09-24)** |
| Matija Ludvig & Zhongwei Wang | 4.17 (09-02) → 4.86 (09-09) → 6.18 (09-17) → **11.49 (09-18)** → 11.64 (09-19) |
| Fususu | 3.20 (09-01) → 5.43 (09-03) → 6.91 (09-11) → 7.49 (09-22) → 8.65 (09-23) → **10.66 (09-24)** |
| mostik.ai | 2.52 (08-11) → 3.57 (08-18) → **5.99 (08-24)** → **7.51 (08-30)**; no submissions after 09-06 |

- The tracker's daily records carry a second field of ~530–570 for most full runs. It is probably the run time in minutes; this is unverified.

Release and engine dates:
- Qwen 3.8 27B release thread: 2026-08-14. Ya Xu reported "a consistent 2x score on the local 25 dataset" — [735243](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735243).
- Tufa's Kaggle dataset of Qwen3.8-27B-FP8: 2026-08-18 — [driessmit1](https://www.kaggle.com/driessmit1/datasets).
- RadixArk Qwen3.8-27B-NVFP4: 2026-08-22.
- RadixArk Qwen3.8-27B-DSpark speculative draft (1.86B, acceptance ~3.3–4.1 tokens on code, SGLang): created 2026-08-14 — [HF](https://huggingface.co/RadixArk/Qwen3.8-27B-DSpark).
- Qwen3.8-Flash-Next: 2026-08-26 (NVFP4 by RadixArk on 08-25). vLLM "PLE-Offload for Qwen3.8-Flash-Next": 2026-08-26 — [HF](https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4); [1ytic/vllm qwen-flash-next](https://github.com/1ytic/vllm/tree/qwen-flash-next).
- Skyfall AI published a `qwen38-flash-next-vllm-nvfp4-runtime-v1` dataset on 2026-09-04 — [Kaggle](https://www.kaggle.com/alykassem202/datasets).
- vLLM FP8-KV on QSA: ported by Sorokin on 09-07; merged upstream on 09-16 — [PR #55557](https://github.com/vllm-project/vllm/pull/55557).
- DeepSeek-V4.1-Flash (552B): 2026-09-10. Too large, and community tests were negative — [llm-stats](https://llm-stats.com/llm-updates); [742788](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742788).
- Observers' comments on the wave:
  - Van-Phuc Huynh (09-07): "whenever one team moves up, the others quickly follow" — [737617](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/737617).
  - Van-Phuc Huynh again (09-20) — [739186](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739186).
  - CPMP: "we did not see any leaked solution" — [739186](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739186).

### Inferences
- Waves 1 and 2 are model-driven.
  - Franzen's jump came on 08-14 and Lord Han Solo's on 08-16, the same days as Qwen 3.8 27B.
  - Tufa's came on 08-19/23, right after their 27B-FP8 dataset upload.
  - The 5–11 range appears only after Flash-Next and PLE-offload (08-24 → 09-06).
- Wave 3 (Sep 13–24) has no public model trigger. Candidate explanations:
  - (a) private fine-tunes or distillations, which Tufa and NVIDIA can afford;
  - (b) engine and throughput gains available to everyone: FP8 KV (1.77× KV tokens), Flash-Next's MTP, `reasoning_effort` tuning;
  - (c) harness redesigns spurred by Tufa's demonstration that 18.8 is achievable;
  - (d) best-of-many selection on a very noisy LB. Public-notebook single-draw spread is about ±50%; the top teams hold 20–146 submissions.
  - Several independent solo teams (Lord Han Solo, Yi-Chia Chen, Franzen, THK, Matija) all jumped 5–9 points within Sep 16–24. That argues that at least part of the gain comes from something broadly reproducible, i.e. engine, context or throughput settings plus harness work, rather than only large-compute RL. This is speculative.
- Practical takeaway for B81 at ~4%. Before any fine-tuning, reproduce the no-release levers:
  1. FP8 KV on QSA (PR #55557);
  2. MTP/spec-decode tuning;
  3. `reasoning_effort`;
  4. a larger context and less eviction, made possible by the extra KV;
  5. test on NVIDIA Game-Creator games to avoid overfitting to the public 25;
  6. only then, STaR-style trajectory SFT (Q2).

### Gaps
- arc3.huikang.dev renders client-side and has no annotations. The event dates above are aligned by me, not by the tracker.
- Private (final) LB scores are hidden, so it is unknown whether the Sep wave holds on the 55 fully private games.
