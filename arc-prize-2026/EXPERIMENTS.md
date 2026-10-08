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

## Oct 3: sm25 (solved-level memory) vs base25
- **Mean over 25 games:** 14.19 (1.96 levels) against base 10.65 (1.68 levels).
- **Paired:** +3.54; better in 11, worse in 7, same in 7.
- **Without the largest swing** (sb26 +75): **+0.56**.
- **Graft health:** `OURS_SOLVED_MEMORY ok`, at least 10 levels pinned, 2 deaths handled, 0 errors.
- **sb26 again:** both variants cleared sb26 and base25 did not. base25's sb26 (2.78) looks like an unlucky draw,
  which inflates both comparisons.
- **Verdict:** safe, with a weakly positive signal (11 vs 7 games better). Move on to a combined build
  (mem12 + solved memory), tested paired against a **same-day** baseline.

## Oct 3: solved memory made cache-friendly (graft v2, not yet run)
- **Problem.** Our v1 graft rewrote the system prompt after each cleared level. Franzen measured that changing the
  start of the prompt drops shared prefix from 99% to 15%, so every clear forced a full prefill of the history.
  ChatGPT's report flagged this independently.
- **v2 (default `OURS_SM_MODE=append`):**
  - the system prompt is never touched;
  - the solved-levels block is appended to the turn-opener lines once per cleared level;
  - it is shown again only if the history trim evicted it.
- **A/B:** `--set OURS_SM_MODE=system` gives v1.
- **Counters:** `shown`, `reshown`.
- **Tests:** 27/27 pass; loads against the real `tool_agent`.
- **Next run:** `fz-sm2` (v2) paired against a same-day base25.

## Oct 3: combo25 (12 streams + solved memory v1) vs base25b (same day, side by side)
- **Mean over 25 games:** base25b **14.79** (2.08 levels); combo25 **11.55** (1.76 levels).
- **Paired:** **−3.25**; better in 7, worse in 12, same in 6.
- **Without the largest swing** (sb26 −41.7): **−1.64**.
- **Actions taken:** combo25 played **1,404** actions against base25b's **1,812** (−23%). It ran 12 streams; its
  graft rewrote the system prompt (10 levels pinned, 0 errors).
- **Same-notebook noise:** base25 (10.65) and base25b (14.79) are the same notebook, and they differ by **4.1**. The
  earlier "+3.5" results for mem25 and sm25 were measured against the unlucky base25.
- **Verdict:**
  - neither 12 streams nor solved memory v1 has a proven gain, and the combination looks harmful;
  - the most likely cause is fewer actions, from slower turns: 12 streams sharing the GPU, plus a full prefill after
    each system-prompt rewrite in v1;
  - v2 (append) removes the second cause; sm2v25 vs base25c tests it.

## Oct 3: action counts, and the progress-notice graft (built, not yet run)
- **Actions over 25 games:**
  - base25 1,624;
  - mem25 1,674 (+3%);
  - sm25 (v1) 1,542 (−5%);
  - combo25 vs base25b: 1,404 vs 1,812 (−23%).
- **Reading:** 12 streams do not slow games. v1 costs a little, as expected from re-reading the history after each
  rewrite. The combination's −23% is probably an interaction or chance.
- **Decision:** submit mem12 v2 hidden (Oct 4, 00:02 UTC).
- **New graft `progress_notice_fz`:** counts per level the actions, analysis turns, game overs, distinct boards at
  turn start, and turns since the last new board. It adds ONE plain-count line to the opener:
  - at 40 / 80 / 160 / ... actions (`OURS_PN_ACTIONS`);
  - once when the board has shown nothing new for 4 turns (`OURS_PN_STALE_TURNS`).

  The line contains no advice. It stacks with `solved_memory_fz`. 31 tests pass; loads on the real `tool_agent`.

## Oct 4: sm2v25 (solved memory v2, cache-friendly) vs two plain baselines
- **Mean over 25 games:** sm2v25 **16.95** (2.20 levels); base25c 14.08; base25d 12.90.
- **Paired vs base25c:** +2.87; better in 6, worse in 5; **+1.09** without the largest swing (ft09 +45.8).
- **Paired vs base25d:** +4.05; better in 9, worse in 6; **+2.14** without the largest swing (sb26 +50.0).
- **Actions:** sm2v25 1,839; base25c 1,680; base25d 1,707 (+8%). v1 had cost −5% and combo25 −23%. v2 no longer
  slows play, as expected from keeping the system prompt fixed.
- **Graft health:** 50 levels pinned, 49 shown, 4 re-shown after eviction, 5 deaths, 0 errors.
- **The four plain 25-game runs so far:** 10.65, 14.79, 14.08, 12.90 (mean 13.11, SD ≈ 1.8). sm2v25 is above all of
  them, about +2 SD. It is the first variant that beats every baseline, and it stays positive without its largest
  swing in both comparisons.
- **Verdict:** promote to hidden draws. Submit fz-sm2v25 v1 on Oct 5 and again on Oct 6, then compare with the plain
  copy's 27.33.

## Oct 4: mem12 hidden draw = 20.35 (plain copy: 27.33 ± 1.4)
- **A clear loss of about 7 points.** The local runs (10-game demo 48.74; 25 games neutral) did not predict it.
- **Lesson:**
  - server and memory settings must be judged on the hidden run, which is 110 games over 9 hours with long contexts;
  - only 3.2 GB of GPU memory was free at MEMFRAC 0.97, which leaves no headroom for long-run spikes.
- **Rule from now on:** never change server/memory settings without a hidden draw. Grafts that change only prompt
  text keep Franzen's server settings.
- sm2v25, pn25 and sp25 all use Franzen's default server settings, so this finding does not affect them.

## Oct 5–7: pn25 (progress notices) and sp25 (solved memory v2 + progress notices)
- **Means over 25 games:**
  - plain runs: 10.65, 14.79, 14.08, 12.90 (mean 13.11);
  - **sm2v25 16.95**;
  - pn25 14.50;
  - sp25 15.33.
- **pn25:**
  - paired: +0.43 vs base25c, +1.60 vs base25d;
  - without the largest swing: +2.02 and −1.34;
  - wins/losses: 8/5 and 6/6;
  - **Neutral.**
- **sp25:**
  - paired: +1.25 and +2.43;
  - without the largest swing: +3.29 and −0.48;
  - **Not better than sm2v25 alone** (15.33 vs 16.95, inside the noise).
- **Notice frequency:** the progress notices fired rarely (1 notice in the first 115 turns), so a large effect was
  unlikely either way.
- **Verdict:** progress notices are not promoted. sm2v25 stays the candidate.
- **Hidden draws:**
  - Oct 6: 28.42 (no description; notebook to be confirmed);
  - Oct 7: sm2v25 submitted.
- **Next local test:** sm2 + Franzen's built-in `ARC3_DEATH_LEDGER=1`. It shows recorded fatal continuations from
  the current board state, which is factual evidence. Prompt-only, with no server change.

## Oct 8: sm2dl25 (solved memory v2 + ARC3_DEATH_LEDGER=1) vs sm2r25 (a repeat of sm2v25)
- **Means:** sm2dl25 **16.14** (2.16 levels); sm2r25 **12.86** (1.80 levels).
- **Paired:** **+3.29**; better in 10, worse in 4, same in 11; **+1.64** without the largest swing (ft09 +42.9).
- **Actions:** 1,674 vs 1,719. The ledger costs no speed.
- **Repeat of the same notebook:** sm2r25 vs sm2v25 = **−4.09** (12.86 vs 16.95). sm2v25's 16.95 was a lucky run,
  and a single 25-game run varies by ±3–4.
- **All runs containing v2:** 16.95, 12.86, 15.33 (+progress notices), 16.14 (+ledger), mean 15.3. The four plain runs
  average 13.1. That is about +2, t ≈ 1.7: weak evidence. It matches the hidden draws (v2 28.17 vs plain 27.33).
- **Death ledger:** 10 games better and 4 worse against its same-day v2 run (sign test p ≈ 0.18). **Promising, not
  proven.** It is prompt-only and is Franzen's own code, so it is safe to promote to a hidden draw.
- **Plan:**
  - hidden: Oct 9 sm2dl25 draw 1;
  - local: repeat sm2dl25 and test + `ARC3_DEATH_REPEAT_GUARD=1`, Franzen's built-in check that blocks replaying
    a recorded fatal sequence.
