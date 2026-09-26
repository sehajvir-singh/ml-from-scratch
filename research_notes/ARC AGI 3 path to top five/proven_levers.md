# Proven levers on the Duck-harness / Flash-Next chassis: what has moved the HIDDEN score (as of 2026-09-25)

Terminology used throughout:
- **Hidden** means the Kaggle leaderboard score. It comes from the 55 visible games of the 110 hidden games. The other 55 are private and are sealed at run time.
- **Public-25** means offline or Save-&-Run scores on the 25 public games.
- The host says one execution plays both halves and private scores "are calc'd at original run time. They aren't rerun" — [Thui MAP B95, quoting host Greg Kamradt in discussion 729985](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- Board context on 2026-09-25: #1 Lord Han Solo 19.45, #2 Tufa Labs 18.81, #3 Yi-Chia Chen 18.63, #4 Daniel Franzen 16.68, #5 NVARC3 16.07. Rank 30 is 5.63, rank 50 is 4.99 and rank 100 is 4.32, across 3,320 teams. Source: the Kaggle leaderboard JSON pulled 2026-09-25 ~15:00 (local `scratchpad/lb.json`, from the [leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard)).
- **The top-5 bar is now 16.07 hidden.** It is about 4x anything any Duck/Flash-Next lever in this document has produced.

## Q0. Ranked list of levers that measurably raise the HIDDEN score (synthesis)

### Takeaway
Only one lever has hidden evidence that approaches significance: the vLLM serving profile, used together with the animation bundle.
- The profile is B81: MTP off, KV cache 7 GiB, `max_num_seqs` 28.
- Six hidden draws of builds on that profile average 3.92. Eight earlier Flash-Next draws average 3.21.
- The difference is +0.71, with an exact permutation p = 0.0496. This is my pooled computation across heterogeneous grafts, not a registered test.

Every other lever is ND (not distinguishable) or n = 1 on hidden, including the three grafts in our build. No harness lever on this chassis has produced anything near the 16+ scores at the top of the board.

### Cited Findings
**Rank 1 — Serving profile B81 (MTP 0 / KV 7 GiB / max_num_seqs 28) on the anim bundle.**
- Mechanism: median Running went 3 → 10, actions +48% (2,008 → 2,965).
- Public: 9.56 → 8.72, levels 39 → 41, p = 0.6491 ND.
- Hidden: 4.50 / 3.26 (mean 3.88) vs B71's 3.74 / 3.41 / 2.90 (mean 3.35). The diff is +0.53, permutation p = 0.50, and the smallest p reachable at n = 2 v 3 is 0.20.
- Source: [Thui MAP B81](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- tantan0327 moved its daily submission to a byte-identical B81 copy from 2026-09-25. They cite four hidden draws of this profile, "4.50, 3.86, 3.03, 5.36, mean 4.19", against their own floor of 2.88 over 20 draws — [tantan SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent/blob/main/SOLUTION.md).

**Rank 2 — Note backfill from reasoning (our graft #1; Thui B93 = tantan "candidate B").**
- tantan hidden: 2.77, 3.55, 3.67, 2.62, mean 3.15. Floor: 2.87 (n = 14, sd 0.47), on the older flash-next-asis vehicle, not B81 — [tantan graft-inventory.md](https://github.com/tantan0327/arc-agi-3-agent/blob/main/docs/graft-inventory.md).
- Thui B93 on B81, public, pooled over 3 pairs: 8.82 → 12.22, levels 41.67 → 46.33, 16 up / 6 down, p = 0.1079 ND. Its single hidden draw was 3.03 (best public run, 15.88), below B81's controls 3.26 / 3.86 / 4.50 / 2.90 — [Thui MAP B93](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- Thui's B96 mechanism test: 689 fill-turns across 25/25 games. The paired permutation gave p = 0.7184, per-game delta +0.0038. A placebo on the control arm gave the same +0.0030 — "The association is not the mechanism" — [Thui MAP B96](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).

**Rank 3 — Scoring-formula + time-pacing prompt lines together with connected-component click candidates (our grafts #2 and #3, from gedouluhui's P3.1).**
- Hidden: P1 = 1.12 (Qwen3.8-27B FP8, stock Duck) → P3.1 = 1.43 (+28%). That is n = 1 per arm, with both changes bundled together.
- Public-25: P2.1 (click hints only) = 2.81, single pass. P3.1 over 3 runs = 1.88 / 3.03 / 1.19. The author's own σ is about 0.8–0.9 per 25-game pass.
- Source: [Kaggle discussion 743060, 2026-09-24](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060).

**Rank 4 — Newer vLLM engine with MTP (27B-era only).**
- tantan's "dflash v7" scored 2.27 against its family band of 1.9–2.2. It is "the one modification that beat its baselines — of more than fourteen submitted", and it scored +7 levels offline — [tantan SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent/blob/main/SOLUTION.md).
- On Flash-Next the opposite setting (MTP off) is what freed KV memory. See rank 1 and Q3.

**Levers that are ND or negative on hidden or public (do not expect gains):**
- **B76 ACTION7 = UNDO:** hidden 3.32 / 2.68 (mean 3.00) vs B69's 3.21; public pooled p = 0.46.
- **B80-L1 no-impact detection:** hidden 3.60 / 2.82 (mean 3.21), equal to B69.
- **B88 context 64k:** hidden 3.86 / 3.51 (mean 3.685) vs B81 3.88; public p = 0.459.
- **B99 RungPin:** hidden 5.36 (n = 1, rank 33/3,258), but on public B99 = B81. Two B99 runs averaged 41.0 levels per game vs 41.25 for four B81 runs, and the matched per-game gate failed at 8 up / 4 down.
- Source for all four: [Thui MAP](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).

### Inferences
- Our build is B81 plus the note from reasoning, the pacing prompt and click candidates. The only hidden-supported part of that is the B81 base. The three grafts have a positive-leaning but non-significant record.
  - Note backfill: +0.28 over the floor on 4 vs 14 draws (se ≈ 0.27), plus one B93 draw below its controls.
  - Prompt + clicks: +0.31 on 1 vs 1 draws on a different, weaker model.
- None of the grafts is a proven hidden lever, and none is proven harmful.
- The pooled p ≈ 0.05 for the profile rests on draws taken on different days with different grafts. It is suggestive, not a controlled result.
- Expected effect sizes: B81 profile ≈ +0.5 to +0.7 hidden. Each graft is 0 to +0.3 hidden, and indistinguishable from 0 at current n.

### Gaps
- No lever measured anywhere public raises hidden by more than ~1 point with p < 0.05.
- What the top 8 (≥ 11.6) do is undisclosed. Tufa has said it will not open-source for milestone 2 ([discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801)). Scott Le Grand speculates the gap is "some fine tuning".

## Q1. Thuitanium's experiment ledger, B82–B101: wins, nulls, hidden draws, pending

### Takeaway
There are no distinguishable wins in B82–B101 on either board. Every build is closed as ND, KILL or PARK, except B98 (open, stage 2 blocked) and B101 (open, on HOLD). B99 produced the campaign's best hidden draw (5.36), but it did not replicate on public.

### Cited Findings
All of the following are from [Thui MAP.md, rows B81–B101 (repo HEAD cc164a7, 2026-09-25)](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).

**Complete list of Flash-Next hidden draws recorded:**

| Build | Hidden draws | Mean |
|---|---|---|
| B69 | 3.21 | 3.21 |
| B76 | 3.32, 2.68 | 3.00 |
| B80-L1 | 3.60, 2.82 | 3.21 |
| B71 | 3.74, 3.41, 2.90 | 3.35 |
| B81 | 4.50, 3.26 | 3.88 |
| B88 | 3.86, 3.51 | 3.685 |
| B93 | 3.03 | 3.03 |
| B99 | 5.36 | 5.36 |

- No draw is recorded after `56472759` (submitted 2026-09-22).
- The same-build hidden sd is about 0.43.

**Row-by-row results:**
- **B82 executable world model:** the smoke failed on cost. The action rate fell to 0.95 / 0.48 / 0.24 of control, and `verify_world_model()` was called once. No full run.
- **B83 remove cross-level notes:** Step 0 KILL. Notes are written in only 3/25 games. No build.
- **B84 graph explorer (arXiv 2512.24156) as a stuck-level hand-off:** PARK. Priced at +0.01 to +1.13 public per run, inside draw sd ≈ 1.2.
- **B85 probe-and-repeat opener (AERA claim):** KILL. It cleared 0 of 104 STUCK stalls, and 300 blind presses gave 0 level-ups.
- **B86 fp8 KV cache:** DEAD. The QSA backend raises `NotImplementedError` unless the KV cache is bf16. Prefix caching is off and has a 0% hit rate on this profile.
- **B87 KV 7 → 10 → 12 GiB (public smoke, n = 1):**
  - Running 10 → 14 → 17; Waiting 15 → 10 → 7.
  - Generation +21% (336.5 → 408.1 tok/s).
  - Actions 678 / 749 / 719; levels 18 / 18 / 18.
  - Verdict NO-GAIN: "KV is no longer the binder, decode compute is".
- **B88 context 64k:** public 8.72 → 10.31, levels 41 → 45, p = 0.459. Hidden 3.86 / 3.51 vs B81's 4.50 / 3.26. Closed ND.
- **B89 drop chat history at level transition:** public 8.72 → 5.89, levels 41 → 35, p = 0.1721. L2+ clears went 19 → 12, so the history is load-bearing.
- **B90 dwell-90 supervisor redirect:** public 8.72 → 7.58, levels 41 → 37, p = 0.6311 ND. It fired only 4 times.
- **B91 prefix caching on:** it runs, but the hit rate is only 0.196. It costs 8% of KV capacity and preemptions go 22 → 344. Actions 683 vs 678, levels 19 vs 18. Verdict NO-CACHE: history is dropped from the front, so the prefix is not stable.
- **B92 stop re-sending stored reasoning:**
  - Prompt tokens per request fell 35%, and generation rose 49%.
  - Actions fell 678 → 478 and levels 18 → 11.
  - The stored reasoning is load-bearing.
- **B93 reasoning-derived slot fill:** PARK at k = 3, underpowered. Public p = 0.1079, hidden 3.03.
- **B94 Qwen3.5-122B-A10B-NVFP4 swap:** KILLED at the smoke. 1,640 actions / 0 levels vs 211 actions / 6 levels.
- **B95:** the host confirmed one run is played and private scores are sealed at run time.
- **B96:** the note-fill mechanism fails its gate (p = 0.7184; placebo identical).
- **B97 context × KV (built as ctx 48k × KV 13.5 GiB):** closed 2026-09-24 without serving. The arm errored in about 2 minutes on a window-anchor assert.
  - `ANALYZER_CONTEXT = 32_768` is ONE knob. It feeds both `--max-model-len` and the analyzer window.
  - `serving_setup.py` checks its own sha256, so the constant cannot be patched in place.
  - The row pre-registered "no level gain is predicted", because both halves are already flat alone (B54 levels 28 → 28; B87 18 / 18 / 18).
  - B100's vLLM log shows median Waiting 14–15 and KV use 95% with Running 10–11 out of 28 seqs, so the queue is KV-bound. That log covers only the first ~31 minutes.
- **B98 controller-owned hypothesis compile/verify:** OPEN. The kill rule was revised to an availability bar (≥ 30% of held-out decisions). A peer's stage 1 on the old bar failed: 5/33 hypotheses compile faithfully, with decisive verdicts in 3 games vs 12 needed. Stage 2 is blocked.
- **B99 RungPin:** FAILED its full-pair gate. Details:
  - Treatment r2: public 9.08, 45 levels. Control r5: 9.26, 40 levels. 8 up / 4 down / 13 tied, where the gate needed ≥ 12 up and ≤ 6 down. p = 0.9226.
  - Byte-identical B99 r1 vs r2 went 37 → 45 levels, so +5 is inside noise.
  - The one hidden draw was 5.36. It is still unproven that the pin reached the model.
- **B100 OutcomeSieve (strip reasoning only from levels already left):** KILL on the pre-registered gate. Details:
  - L2+ clears went 5 → 3 in the smoke, with n ≈ 4 flagged beforehand as able to decide it.
  - Every other gate passed: 50.5% of post-clear reasoning stripped; actions/min 0.83 → 0.97.
  - Post-clear prompt tokens fell 18.8%, and total levels went 15 → 18 (+3).
- **B101 keep the six note slots across game_over:** OPEN / HOLD 2026-09-24. Details:
  - A peer's census found non-empty slots wiped at 45 of 109 deaths (41%).
  - The mechanism barely fires at 1,800 s: 0–1 affected game-runs, vs 6–10 at 7,920 s. So there is no cheap stage, and it needs a ~4.8 GPU-h full-clock pair.
  - The registered 25-game test has "~0 power even at full clock", per a peer claim that Thui has not verified.

### Inferences
- Thui's own conclusion, shared by tantan: on this chassis every in-prompt or memory lever reads ND at the sample sizes affordable. B81's serving change is the only one with a positive hidden mean over more than one draw.
- B99's 5.36 is the single best hidden draw, but given the public pair it should be treated as a lucky ticket, not a lever.
- Pending items (B98, B101) cannot be resolved before the 2026-09-30 milestone with pre-registered power.

### Gaps
- There are no hidden draws of B97, B100 or B101, and none are scheduled in the MAP.
- The two B81 hidden draws came from different days. It is not known whether game seeds are identical across scored runs (B95 leaves this open).

## Q2. tantan0327 and sonpham-org: latest measured levers

### Takeaway
- tantan0327 concluded that harness engineering does not raise the ceiling. Their board-positive items are:
  - the note backfill (hidden mean 3.15 vs 2.87);
  - an engine swap (newer vLLM + MTP, 2.27 vs a 1.9–2.2 band, 27B era).
- From 2026-09-25 they submit an as-is copy of Thui's B81.
- sonpham-org publishes offline and behavioural studies but no hidden A/B of a lever. Their team sits at rank 14–16 (7.36 on 2026-09-21).

### Cited Findings
**tantan0327**
- Measured null on full offline runs (band of 32–41 levels), with no board gain: animation channel (40 levels), perception-facts oracle (37), goto tools (35; "null as an offered tool"), physics planner as player (41).
- Also closed as null or negative: stall amnesia, strip reasoning, no-op guard, and context / KV / max-num-seqs / image-off / output-cap / history-cap arms.
- Source: [tantan graft-inventory.md (2026-09-22)](https://github.com/tantan0327/arc-agi-3-agent/blob/main/docs/graft-inventory.md).
- Earlier hidden results on the 27B era: per-game clock 7,920 → 25,200 s scored 0.58 vs 0.98 unmodified; the click-effect tally scored 0.69; MoE 35B-A3B scored 0.42; temperature 1.0 scored 0.72 despite the best offline runs. Offline vs board Pearson r = −0.39 — [tantan SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent/blob/main/SOLUTION.md).
- "98.3% of a solving trajectory's decisions occur at a board state never seen before in that game ... no harness engineering raises that ceiling" — [tantan SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent/blob/main/SOLUTION.md).
- Stock vLLM 0.19 with Qwen3.8-27B-FP8 boots at 403 tok/s. A nightly vLLM 0.26.1rc1 + DFlash2/MTP wheelhouse exists (`tantan0327/arc3-vllm-dflash-wheelhouse`) — [graft-inventory.md §D](https://github.com/tantan0327/arc-agi-3-agent/blob/main/docs/graft-inventory.md).

**sonpham-org**
- Standing on 2026-09-21: rank 14 of 3,206, score 7.36, 55 submissions. Ranks 11–16 span 7.39–7.22, "inside the seed noise" — [sonpham docs/how-this-feeds-kaggle.md §7](https://github.com/sonpham-org/arc-3/blob/main/docs/how-this-feeds-kaggle.md).
- **No-score-pressure arm (2026-09-21, IN PROGRESS, offline, Qwen3.8-27B BF16 on a GB10):** this is the opposite of our pacing graft. It removes the `(human/agent)^2` efficiency bullet and the HUD/timer-suspicion lines, and reframes the model as "playing a video game". sonpham's `main` separately landed `ed5fd27e4`, "remove scoring pressure and gauge-suspicion coaching". No results are reported yet — [sonpham trace-finding 2026-09-21-no-score-pressure-wide.md](https://github.com/sonpham-org/arc-3/blob/main/docs/trace-findings/2026-09-21-no-score-pressure-wide.md).
- The earlier-reported no-impact detection "+55% levels at equal budget" (offline) did not transfer to Thui's fast base: public p = 0.369, hidden mean 3.21 = B69 — [Thui MAP B80](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- On 2026-09-23 Son Pham said DeepSeek V4 Flash needs quantization and expert pruning to fit, and "the token efficiency just wasn't equal to Flash Next" — [discussion 742788](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742788).

### Inferences
- sonpham removed the scoring-pressure text while gedouluhui added it. Neither has a controlled hidden A/B on Flash-Next, so our pacing-prompt graft has contested sign.
- tantan's 25,200 s clock result probably reflects running past the 9 h envelope on a 4-wave hidden schedule (see Q4). That makes it evidence against raising the clock without reducing waves, not evidence against time as such. This is my inference; tantan lists it as "undiagnosed".

### Gaps
- sonpham's repo does not document which build produced 7.36, or any hidden A/B of a lever.
- The no-score-pressure arm has no results yet.

## Q3. Kaggle discussions, last 2–3 weeks (A/B results on time, serving, prompt, context)

### Takeaway
There are few real A/Bs, and almost all are n = 1.
- **Time allocation:** giving more time to games that reach L2+ helped public (7.6 → ~13) but was "a slight digression" on hidden.
- **Serving:** raising sequence concurrency (Scott, to 16; Thui B81, to 28 with MTP off) is the one serving change with hidden support.
- **Context:** 64k context lost on hidden for gedouluhui, and was ND for Thui.
- **Prompt:** the pacing and scoring lines are +0.31 hidden at n = 1.

### Cited Findings
**Time allocation**
- Scott Le Grand (2026-09-12) gave more time to games that hit L2 or higher. It "got me to ~13 (up from 7.6) on the public data ... But it was a slight digression on the hidden data". His explanation: "if your solver is at ~3.5 or less, you're mostly not solving any level 2 or up of the hidden games" — [discussion 740812](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740812).
- Avinav Sahoo suggests "try depth priority scheduling after FIFO", with no data — [discussion 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).

**Concurrency and serving**
- Scott Le Grand (2026-09-17): "most of what I have done is just take the stock duck client for nvp4 and increase the sequence concurrency to 16 ... That will get you to the brink of the top 10%, but all of my harness engineering beyond that has been utterly useless". His best was 3.2 hidden with 12 public — [discussion 732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854).
- On 2026-09-23 he reported #38 at 5.19 "on harness fixes alone", details undisclosed — [discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
- Rakha Abid Bangsawan: pinning the serving profile (model / runtime / MTP / concurrency, with startup validation) "produced a more reliable improvement than several complicated prompting experiments". His best went 1.65 → 2.86, and to 3.48 after about 3 resubmits. He suspects continuous batching as a variance source — [discussion 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938).

**Prompt and context**
- gedouluhui P3.1 (2026-09-24), Qwen3.8-27B FP8 stock Duck:
  - Click candidates plus two prompt lines (the scoring rule, and "Action results report time_remaining_seconds. Use it to pace yourself ... change the hypothesis class") took hidden from 1.12 to 1.43.
  - Rejected changes: 64k context + 4,096 output cap scored 1.20, with throughput 283 → 195 tok/s. T = 0.3 scored 0.95 (games with any progress fell 12 → 8). An archetype playbook scored 1.54 against a 3.5 keep-line.
  - Whether 1.20 / 0.95 / 1.54 are hidden or public-25 is ambiguous in the post. The 3.5 keep-line suggests public.
  - "17 of 25 games have been cracked at least once, but only ~5–8 are cracked in any single run."
  - Source: [discussion 743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060).
- Muurur got his "highest score by clearly naming this action 'UNDO'", with the caveat "not sure if it's ... just variance luck" — [discussion 742477](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742477).
- Thui's B76 measured the same UNDO labelling as ND.

**Noise and multimodal upscale**
- MULTIMODAL_UPSCALE 4 vs 8 has no posted A/B. Two identical passes of one notebook gave public-25 means of 2.85 and 4.75 (spread 1.90) — [discussion 739801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739801).

**Top teams and resources**
- Tufa Labs (#2) will not open-source for milestone 2 (2026-09-30). CPMP (NVARC3) will not share either — [discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).
- Kaggle RTX Pro 6000 queues ran up to 8–10+ h around 2026-09-21/22 (CPMP: "Darragh waited more than 10 hours") — [discussion 742148](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742148).

### Inferences
- Taken together, the evidence says serving and concurrency changes that add actions help at most modestly on hidden, while prompt and context changes are noise-dominated.
- Public-25 gains driven by deep-level time do not transfer, because hidden games are harder: Scott's and Thui's shrink ratio is about 2.1–4x public-to-hidden.

### Gaps
- No discussion post in the window reports an A/B of newer vLLM, MTP on/off, FP8 KV or prefix caching on hidden.
- Scott's 5.19 changes are undisclosed.

## Q4. Scheduling: is a fixed 7,920 s × 28 concurrent games optimal? Early-stopping zero-progress games?

### Takeaway
No reallocation scheme has hidden evidence of a gain, and the measured evidence prices it small.
- Doubling every game's clock bought +2 levels over 25 games (ND).
- Reallocating from dead games is bounded below that.
- The one hidden report of time-to-progressing-games was slightly negative.

The fixed schedule is a consequence of the harness's wave arithmetic. The only way to give more clock without busting 9 h is fewer waves, which means higher concurrency, and that trades per-request throughput.

### Cited Findings
**How the harness sets the per-game clock**
- Per-game runtime = experiment envelope / waves, with waves = ceil(games × passes / concurrent_jobs) — [Thui localrig run.py `_max_runtime_minutes_per_game`, lines 559–600](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/localrig/ARC3-Inference/inference/framework/run.py).
- Thui: `max_runtime_s_per_game = 7920` "is 32400/4 less a 180 s margin, i.e. derived from the four-wave hidden-110 schedule". Public-25 runs in 1 wave and so uses only 24.6% of the envelope — [Thui MAP](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- The host says "For v3 it is 9hrs", and 110 games are played — [MAP B95](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).

**Game clocks and level-ups on the 27B era**
- B33: 125/125 run-games end at the wall (median 7,920.5 s, `gave_up`). The last level-up sits at a median 0.613 of the game's action sequence — [Thui MAP B33](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- B34 clock 2x (7,920 → 15,840 s, public-25, 27B era):
  - Actions per game 63.5 → 105.5 and levels 28 → 30.
  - Public mean 4.71 → 6.40, 10 up / 6 down, p = 0.2761 ND.
  - This cannot ship, because 4 waves × 15,840 s exceeds 9 h.
  - Source: [Thui MAP B34](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- B35/B36 reallocation from dead or plateaued games:
  - Stopping games still silent at k = 40 actions frees the clock of 47.5% of games but "destroys 22 level-ups = 23.2%" of what it cuts.
  - Perfect-foreknowledge reallocation is priced at +0.86 public.
  - B36 was closed 2026-08-27 as "measured-and-too-small": reallocation gives live games +30% actions where doubling gave +100%, and doubling bought under 1 level per run.
  - Source: [Thui MAP B35/B36](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).

**Concurrency and throughput**
- B16 (27B era): raising effective concurrency 11.3x → 21.2x gave more actions (1,285 → 1,633) and fewer levels (22 → 19) — [Thui MAP B16](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- On Flash-Next, B81's 28 seqs + MTP 0 gave +48% actions, ND public, and +0.53 hidden mean (ND).
- B87 shows extra KV turns queue time into decode time almost one-for-one: mean end-to-end latency fell only 11%, and levels were flat.

**Hidden and public reports on time**
- tantan: a per-game clock of 25,200 s scored 0.58 vs 0.98 hidden, "undiagnosed" — [tantan SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent/blob/main/SOLUTION.md).
- Scott Le Grand: more time for L2+ games raised public 7.6 → ~13, with "a slight digression on the hidden data" — [discussion 740812](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740812).

**Scoring**
- Scoring: level_score = (human/AI actions)^2, capped. The game score is the level-index-weighted mean over ALL levels, reached or not, and the final score is the mean over games — [tantan SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent/blob/main/SOLUTION.md).
- When the completion cap binds, actions cannot move the score (77% of decided cells) — [Thui MAP B35](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- An L2 clear weighs 2x an L1, and L1 is a tutorial by design — [MAP B101 citing arXiv 2603.24621](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).

### Inferences
**Why the clocks stay fixed**
- Early-stopping a game in the current harness does not hand its time to other games. Each game's cap stays at 7,920 s, and the pool simply starts the next queued game earlier.
- A real reallocation needs a dynamic per-game budget that is still bounded by the 32,400 s envelope. tantan's 25,200 s × 4 waves ≈ 28 h is a plausible cause of its loss, because the run would be killed or truncated. This is my inference.

**Where a stopped game's time could go**
- Within a wave, stopping a stalled game does free GPU decode share for the concurrent live games, because the queue is KV/decode-bound (B87, B97).
- B81 and B87 show extra throughput buys actions but little depth. So the expected gain is small, on the order of B36's under-1-level-per-run ceiling (≈ +0.1–0.3 hidden by the ~2.5–3x public/hidden shrink).

**Wave count**
- With 110 games, `concurrent_jobs` 28 → 4 waves (the 4th wave has 26 games). 37 → 3 waves, which would be 10,800 s per game. 55 → 2 waves (16,200 s).
- A 3-wave schedule is the only way to get +36% clock per game within 9 h. It costs about 1.3x more contention per request; the B16 and B81 evidence says contention converts clock into actions, not levels.
- Untested on hidden. I found no evidence it helps.

**Scoring asymmetry**
- A game at 0 levels scores 0. Reaching L2 is worth 2/Σw of the game, so time on games that have cleared L1 has higher marginal value per level.
- Hidden games are harder, and Scott's report says the L2+ reallocation did not transfer. A defensible compromise is to stop only games with zero board-changing progress after a large fraction of the clock, and keep the fixed 7,920 s cap. This is untested.

### Gaps
- The precise mapping between `concurrent_jobs` (worker pool) and vLLM `max_num_seqs` (28) in the B81 notebook was not verified here.
- Nobody has published a hidden A/B of dropping level-0 games, of hard-games-last ordering, or of 3-wave vs 4-wave scheduling.

## Q5. Public notebooks / kernels with hidden score ≥ 5%

### Takeaway
None found. The highest-scoring public kernel on 2026-09-25 is 4.50 (`chiakazirim/duck-qwen3-8-tuned`). All ≥ 5 scores (Thui's B99 5.36; board ranks ≤ ~48) come from private kernels.

### Cited Findings
Top public kernels by `bestPublicScore` (Kaggle kernels listing, SCORE_DESCENDING, pulled 2026-09-25 ~15:01, local `scratchpad/kern_SCORE_DESCENDING.json`, 60 kernels returned):

| Score | Kernel | Date |
|---|---|---|
| 4.50 | [chiakazirim "Duck Qwen3.8 (Tuned)"](https://www.kaggle.com/code/chiakazirim/duck-qwen3-8-tuned) | 2026-09-04 |
| 4.33 | [wuliao0 "Duck Qwen3.8 Anim Base"](https://www.kaggle.com/code/wuliao0/duck-qwen3-8-anim-base) | 09-18 |
| 4.16 | [muhibullahansir "Duck Qwen3.8 Anim Base"](https://www.kaggle.com/code/muhibullahansir/duck-qwen3-8-anim-base) | 09-24 |
| 4.09 | ghazarosghazaros "Duck Qwen3.8 Anim Base" | 09-09 |
| 4.08 | [amanatar "ARC-AGI-3 Hybrid REPL Agent"](https://www.kaggle.com/code/amanatar/arc-agi-3-hybrid-repl-agent) | 09-12 |
| 4.08 | [matthewblakeward "MickTheTrainer"](https://www.kaggle.com/code/matthewblakeward/mickthetrainer) | 09-25 |
| 3.92 | [tantan0327 "ARC3 flashnext asis"](https://www.kaggle.com/code/tantan0327/arc3-flashnext-asis) | — |
| 3.74 | yocybercode thui-animfast-b71 | — |
| 3.71 | yanggod "Duck Flash Next MTP" | — |
| 3.38 | keithtyser "Duck Qwen3.8 Flash Next NVFP4 MTP" | — |

- The same 4.50 appears on Thui's B81 (private) — [Thui MAP B81](https://github.com/Sahasawatt/arc-agi-3-agent/blob/master/notes/wayfinder/MAP.md).
- Scott Le Grand's 5.19 at #38 uses undisclosed "harness fixes" — [discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801).

### Inferences
- The public-kernel ceiling (4.50, several ~4.1–4.3 anim-base forks) coincides with the B81 / anim family's hidden range of 3.0–4.5. There is no public recipe above that.
- The "Tuned" and "Anim Base" forks differ from their parents in unread ways. The ≥ 4 scores are likely draws from the same distribution, given the same-build sd ≈ 0.43 (inference).

### Gaps
- I did not diff the top public kernels (chiakazirim "Tuned", MickTheTrainer, amanatar Hybrid REPL) against their parents, so what they changed is unknown.
- The kernel listing returned 60 rows (`totalCount` 0), so a ≥ 5 public kernel outside that page cannot be fully excluded.
