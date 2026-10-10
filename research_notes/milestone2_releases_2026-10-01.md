# Milestone #2 releases (2026-10-01)

Source: github.com/tonghuikang/daniel-franzen-arc-agi-3, a mirror and comparison of the three open-sourced
Milestone #2 winners. Its `kaggle/SUMMARY.md` lists them as tentative winners, still to be confirmed by the
organisers.

| Team | Public LB | Notebook | Server | Model |
|---|---|---|---|---|
| Daniel Franzen | **27.89** | `dfranzen/arc-agi-3-milestone-2-solution` | SGLang (Pennyroyal v2.5.3) | Intel W4A16 AutoRound + INT4 MTP drafter |
| Lord Han Solo | 23.84 | `lordhansolo/arc-agi-3-milestone-2` | vLLM nightly e975732 | mixed NVFP4/FP8 with built-in MTP |
| sirikilohit | 22.53 | `sirikilohit/arc-agi-3-duck-18-1gc-submit` | SGLang (Pennyroyal v2.5.0) | W4A16 + NVFP4 draft |

Tufa Labs (45.33) and Yi-Chia Chen (36.73) did not open-source. All three published notebooks run the Duck harness
on TAAF with Qwen3.8-Flash-Next, an fp8 KV cache and a context of about 130k tokens. B81 has a 32k context and
about 7 GiB of KV cache.

## What Franzen found, compared with our Depth Thesis
- **Our "timer tick" label fix is his `gameplay_changed`.** He excludes a 4-cell border, and his guards stop a batch
  after an action with no interior change. We reached the same fix independently.
- **Our thrashing finding is his scheduler.** It computes a priority P = (A + B) · C, where C decays with the actions
  and tokens spent on the current level. C is calibrated on 725 level attempts. He also keeps 10 active slots
  across 110 games, with an end-of-run fade. He did at the scheduler level what our stall breaker tries at the
  prompt level.
- **He switched off the world-model note entirely** ("the largest improvement in this area"). Our `note_fill` and
  `level_carry` grafts act on that note, so on his harness they have nothing to act on. That is consistent with
  our m-series result that prompt extras hurt.
- **No clear gain from** prescriptive verification hints, repeated-state guards, summaries, or shorter resume
  prompts. This predicts that our stall breaker is unlikely to help on his harness.
- **What helped:** better models, larger context and throughput (prefix-cache work), animations, 10× board images
  plus diff images, UNDO, keeping the Python functions the model writes, and the priority scheduler.

## Consequences for us
1. **Adopt Franzen's notebook unchanged.** Hidden score is expected around 20–30 with noise, against our 5.28.
   `tools/adopt.py` finds no graft anchor and leaves the cells identical (tested with a fake CLI), and it now
   forces the RTX Pro 6000 and drops the source `id_no`.
2. **Our current grafts do not port.** Their hooks are absent or switched off. Novelty has to come from what he did
   *not* try:
   - an in-game learned action-effect model as a calibrated advisor (our part 1, adapted to his `frame_diff` and
     tools);
   - a scheduler C fitted per game from a learned stall predictor;
   - depth-aware use of time near the end.
3. **Paper.** Independent convergence (the border-tick label, and stall-aware compute) supports the Depth Thesis.
   Cite his write-up.

## Franzen's own Phase A run (the notebook output the user uploaded; run on 2026-09-30, 34 min)
- **Setup:** the cells are identical to the mirror. Image: Python 3.12.13, SGLang 0.5.19, torch 2.13 + cu130,
  RTX PRO 6000 Blackwell. The harness patch applied cleanly.
- **Demo mode:** 10 public games, all at once, **25 minutes each** (our census gave 132 minutes per game).
- **Same 10 games, our B81 census (132 min/game) vs his run (25 min/game):**

| Game | B81 census | Franzen |
|---|---|---|
| ar25 | 27.78 (4 levels) | 41.67 (5 levels) |
| ft09 | 23.48 (4) | 47.62 (4) |
| lp85 | 24.54 (4) | 41.67 (5) |
| r11l | 14.29 (2) | 14.29 (2) |
| re86 | 23.40 (4) | 16.67 (3) |
| sb26 | 2.78 (1) | **93.34 (8, won)** |
| sc25 | 12.47 (2) | 28.57 (3) |
| tr87 | 4.76 (1) | 47.62 (4) |
| tu93 | 5.14 (3) | 13.07 (3) |
| vc33 | 15.60 (3) | 21.08 (3) |
| **Mean** | **15.42 (2.8 levels)** | **36.56 (4.0 levels)** |

- **He scores 2.4× higher with about one fifth of the clock per game.** He also reaches about the same number of
  actions per game (about 130) in 25 minutes as B81 did in 132.
- **Depth explains most of the gain:** 4.0 levels against 2.8. That fits the Depth Thesis.
- **These 10 demo games are easier than the hidden set:** 36.6 here against 27.89 on the leaderboard.
- **One problem shows in the log:** 5 analyzer requests timed out on the server, at a read timeout of 5–37 s.
  Work was lost there.
