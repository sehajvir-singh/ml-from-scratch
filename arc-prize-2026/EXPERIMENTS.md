# Experiments on Franzen's notebook (from 2026-10-02)

Baseline: Franzen's Milestone #2 notebook, unchanged. Hidden draws: 27.89 (his), **25.78** (ours, Oct 1).
Phase A demo (10 games × 25 min): 36.56 (his own run).

**Method:**
- `tools/fz_variant.py NAME --set KEY=VALUE` builds a copy that changes only harness settings.
- Each test is one Phase A run, about 40 minutes and about 0.7 GPU-hours, on the same 10 demo games.
- A variant is submitted only if its demo mean beats the baseline by at least about 3 points.
- **Noise warning:** one 10-game demo varies by several points. A gain under about 3 is unreadable, so a promising
  variant gets a second Phase A run before it uses a submission.

| # | Variant | Settings | Why (evidence) | Phase A | Hidden |
|---|---|---|---|---|---|
| 0 | baseline r2 | none | a second baseline draw | **fz-base (our unchanged rerun) = 49.17 (4.70 levels)**, against Franzen's own 36.56 | draw 2 submitted Oct 2 |
| 1 | reset | `EXPOSE_RESET=on` | Thrashing: 11 of 25 census games spent more than a human's whole-level budget on the stuck level. RESET lets the agent restart a ruined level. In his code, off by default. | **43.69** (4.30 levels) against 36.56 (4.00); RESET used only 7 times in 1,690 actions. Per game: r11l +33, tr87 +24, sc25 +19, re86 +11, lp85 −14, tu93 −9. Probably mostly noise. Needs a rerun plus a same-day baseline run | – |
| 2 | inventory | `ARC3_LEVEL_INVENTORY=1` (run 1 ERROR after 6 s: `/kaggle/taaf-kaggle-source-share/src` missing, i.e. the dataset was not mounted; unrelated to the setting; rerun) | Depth: it highlights new object types at the start of each new level, where the agent has to learn new mechanics. | | |
| 3 | autodiff | `ARC3_AUTO_FRAME_DIFF=1` | The agent is shown what changed after every action without asking for it. Fewer wasted turns. | | |
| 4 | mem12 | server `MAXREQ=12 CUDAGRAPH_MAXBS=12 MAMBA_CACHE=72 MEMFRAC=0.97` plus `ARC3_MAX_ACTIVE_STREAMS=12` | Memory and throughput are binding: Franzen left 4.25 GB free; Lord Han Solo ran 14 streams. The Mamba cache must be at least 6× the running requests. Risk: out-of-memory at start-up, which the log shows. | **48.74** (4.70 levels) against base 49.17, i.e. the same. The server started fine with 12 slots; KV pool 1,032,960 (+2%; the 72 Mamba slots used most of the extra memory); 3.22 GB still free. **The demo has only 10 games, so the 11th and 12th streams were never used.** It must be tested with more than 10 games (`--all-games`) | – |
| 5 | sm25 | `--graft solved_memory_fz` (25 games) | Pins each cleared level's winning action sequence in the system prompt. sirikilohit: the only text addition that helped (+2.8). Evidence, not advice. Tested offline (4 tests) and against Franzen's real `tool_agent` module | | |

**Honest target:** 40 needs +55% over 25.78. Settings alone will probably not do it. Realistically:
- settings: about +1 to +4;
- harness ideas (solved-level memory from sirikilohit, the strategy audit from Lord Han Solo, our census-fitted
  stall prior): about +2 to +6;
- together, about 28–35.

## Lesson (Oct 2): the 10-game demo is far too noisy
- Same unchanged notebook: Franzen 36.56, ours **49.17**. The RESET variant (43.69) sits in between.
- The **spread is about ±6 points on the 10-game mean**, so RESET's "+7" was noise.
- The 7 RESETs appear in the unchanged baseline too, so they are the automatic resets after death, not the agent's
  own choice.
- **New protocol:**
  - test on **all 25 public games** (`--all-games`) to cut noise;
  - compare **paired per-game** against a baseline run made the same day;
  - only trust a gain that repeats.
- Hidden submissions are judged by their average over draws.

## Oct 2–3: first 25-game paired test (base25 vs mem25, 40 min, run side by side)
- **Mean over 25 games:** base 10.65 (1.68 levels), mem 14.40 (2.00 levels).
- **Paired:** +3.75; better in 7 games, worse in 4, same in 14.
- **Almost all of the gain is one game:** sb26 scored 2.78 → 100.00 (+97, which alone is +3.9 on the mean).
  - Without sb26 the paired difference is **−0.14**.
  - Other big swings: ft09 +33, re86 −25, tr87 −5, sc25 −19.
- **Verdict:** mem12 shows no harm and no proven gain. Keep it, because the hidden run has 110 games and keeps
  12 slots busy.
- **Lesson:** single all-or-nothing games dominate the mean. Report the paired mean **without the largest |diff|**,
  plus the win/loss counts.
- These 25-game scores (about 10–14) sit far below the 10-game demo (about 49): the 15 extra games are hard, and with
  25 games sharing 10–12 slots each game got less time, as the low action counts show (g50t 17 and 3 actions, cd82
  25). Not comparable with the hidden scores.
