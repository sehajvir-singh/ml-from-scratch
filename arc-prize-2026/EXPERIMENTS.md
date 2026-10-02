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
| 0 | baseline r2 | none | a second baseline draw | – | – |
| 1 | reset | `EXPOSE_RESET=on` | Thrashing: 11 of 25 census games spent more than a human's whole-level budget on the stuck level. RESET lets the agent restart a ruined level. In his code, off by default. | **43.69** (4.30 levels) against 36.56 (4.00); RESET used only 7 times in 1,690 actions. Per game: r11l +33, tr87 +24, sc25 +19, re86 +11, lp85 −14, tu93 −9. Probably mostly noise. Needs a rerun plus a same-day baseline run | – |
| 2 | inventory | `ARC3_LEVEL_INVENTORY=1` | Depth: it highlights new object types at the start of each new level, where the agent has to learn new mechanics. | | |
| 3 | autodiff | `ARC3_AUTO_FRAME_DIFF=1` | The agent is shown what changed after every action without asking for it. Fewer wasted turns. | | |

**Honest target:** 40 needs +55% over 25.78. Settings alone will probably not do it. Realistically:
- settings: about +1 to +4;
- harness ideas (solved-level memory from sirikilohit, the strategy audit from Lord Han Solo, our census-fitted
  stall prior): about +2 to +6;
- together, about 28–35.
