# Roadmap: from 25.78 toward 100 (2026-10-02)

Start: **25.78** hidden (Franzen's notebook, unchanged), rank about 115. Deadlines: final submissions Nov 2, paper Nov 8.
Method ("progressive overload"): one proven step at a time. Each step is measured against the step before; nothing is
kept on one lucky run.

## What 100 means
- 100% = every level of every hidden game cleared at about human action counts or better.
- That is the **$700K Grand Prize** (an agent at 100% of the evaluation). No team is close: #1 is about 50.
- Frontier API models with executable world models fully solve about 15/25 public games (arXiv 2605.05138), and the
  Kaggle hardware cannot run anything like them.
- **Honest view:** 100 will not happen in this competition, for us or anyone. The realistic ladder for us stops at about
  35 by Nov 2.

## Evidence from the three published Milestone #2 write-ups
- **Memory beats instructions.** sirikilohit went from 14.49 to 22.53 (+55%) by changing only the FP8 KV cache and a
  longer kept history, with no prompt changes. Every time he added advice text, the score dropped (6.42→4.16,
  13.40→9.98). Our m-series showed the same (3.47 against 4.41).
- **Solved-level memory:** pinning the rule from each cleared level was "the only text addition that helped" (+2.8 on
  his base). Franzen keeps the history across levels but does not pin these rules.
- **Throughput is binding:** Franzen says scores were "still improving near the end of runs". Lord Han Solo's server
  peaks at 1,135 tok/s against Franzen's 946.
- **Variance is brutal:** sirikilohit's same notebook scored 5.02 / 5.50 / 6.42. Practice scores of 37 and 32 became
  9.98 and 13.40 on the leaderboard, in the opposite order. **Our RESET demo +7 (43.69 vs 36.56) must not be trusted
  until it repeats.**
- **Restarting stuck levels:** sirikilohit found that a fresh-context restart did not help ("the chance of clearing a
  level didn't fall with time spent on it"). That is a warning for the RESET idea too.

## The ladder

| Stage | Target (hidden) | What it takes | Evidence | When |
|---|---|---|---|---|
| 0 | 25.78 | Franzen's notebook unchanged | done | Oct 1 |
| 1 | **~28** | Second baseline draw. Settings tests: RESET, level inventory, auto-diff. Keep only what repeats. | our demo runs (noisy) | Oct 2–6 |
| 2 | **~30** | Solved-level memory: pin each cleared level's rule and winning actions. A code graft on Franzen's `tool_agent`; adds evidence, not advice. | sirikilohit +2.8 | Oct 6–12 |
| 3 | **~33** | More thinking per GPU-minute: server and flag tuning (Lord Han Solo's faster setup, speculative-decoding settings, cache sizes, streams 10→12 if KV allows). | Franzen "still improving at the end"; Lord Han Solo +20% tok/s | Oct 10–20 |
| 4 | **~35** | Time allocation across the 110 hidden games: fit the scheduler's stall curve to our census data instead of the hand-tuned constants. | census thrashing, Franzen's C curve | Oct 15–25 |
| 5 | 40–50 (where #1 is) | Unknown private advances, probably far more experiments, better serving, maybe fine-tuning. | none public; sirikilohit's LoRA trial "scored badly" | out of reach by Nov 2 |
| 6 | 50–85 | A stronger model on the same GPU, or agents that build and verify executable world models. | executable world models need frontier API models | 2027+ |
| 7 | 100 | The Grand Prize | – | not this year |

## Daily routine (what the person on the Kaggle account does)
1. **Up to 2 test runs at a time** (Kaggle's limit), each about 40 minutes and about 0.7 GPU-hours. Paste the
   `tools/fz_results.py` table.
2. **One submission a day:** the variant with the best repeated gain, otherwise a baseline draw.
3. **GPU quota is about 30 h/week, which is about 35 test runs.** No runs outside the plan.

## Odds (honest)

| Outcome | Chance |
|---|---|
| 30+ by Nov 2 | ~50% |
| 35+ | ~20–25% |
| 40+ | ~5% |
| Top 5 | ~1–3% |
| 100 | ~0% |
| Paper Track prize | ~5–10% |
