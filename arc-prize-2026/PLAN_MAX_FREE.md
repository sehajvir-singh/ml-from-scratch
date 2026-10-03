# Maximum-score plan on free Kaggle only (Oct 4 → Nov 2, 2026)

**Where we start:** hidden ≈ 27 (25.78, 27.88), with no proven improvement yet.

**Honest ceiling without training:** about **33–35**, which is where the best harness-only teams sit (35.79, 34.77,
34.21).
- Expected outcome: about **29–31**.
- 40+ probably needs training, which is what the top two teams appear to do.

## Budget, and why it decides everything
- **GPU:** about 30 hours a week, which is about 10–12 runs of 25 games × 40 minutes.
- **Hidden submissions:** 1 per day, about 29 left.
- **Score noise:** the same notebook scored 10.65 and 14.79. Proving +3 by score needs 8+ paired runs, so we can
  afford only about 4 score-based decisions in total.
- **Trick:** judge speed changes by **low-noise process metrics** instead of score:
  - actions per game-minute;
  - tokens/s;
  - prefix-cache hit rate;
  - turn latency.

  These settle with 1–2 runs. Spend score-based tests only on behaviour changes.

## Levers (all of them), ordered by points per GPU-hour

| # | Lever | How it is judged | Expected |
|---|---|---|---|
| 1 | Speed: 10 vs 12 streams, speculative draft depth 1–4, online FP8, context-drain knobs | actions/min, tokens/s | +1 to +3 |
| 2 | Solved memory v2 (cache-friendly) | paired score, plus check actions are not lower | 0 to +2 |
| 3 | Franzen's built-in knobs that are off: `ARC3_DEATH_LEDGER`, level inventory | paired score | −1 to +2 |
| 4 | Factual stall and goal-contradiction notices, plus one fresh-context review per stuck level | paired score | −2 to +3 |
| 5 | Optional `predict()` check, reporting the hit rate on the last 20 transitions | paired score | −1 to +2 |
| 6 | Scheduler: move time from stuck games to progressing games | replay public logs offline, no GPU | 0 to +2 |
| 7 | Reasoning-retention audit (does `reasoning_content` survive) | log reading, no GPU | 0 to +1 |
| 8 | Final pick: choose by the average of 3+ hidden draws, and keep the most robust build | hidden submissions | protects against −2 |

Gains do not add up. If all of them land, the total would be about +8; realistically 2–3 of them work.

## Calendar
- **Week 1 (Oct 4–10):**
  - speed sweep (#1) judged by process metrics;
  - sm2v25 vs base25c (#2);
  - log audit (#7);
  - scheduler replay (#6).
  - Hidden submissions: alternate base and the best candidate (A, B, B, A).
- **Week 2 (Oct 11–17):**
  - stack the winners;
  - build and test #4 (stall notices) and #3 (death ledger).
- **Week 3 (Oct 18–24):**
  - #5 (`predict()`) only if #4 worked;
  - otherwise repeat runs of the best stack.
  - Make the notebook public before Oct 26 (Paper Track).
- **Week 4 (Oct 25–Nov 2):**
  - freeze the code;
  - draws only, then pick the final 2 submissions;
  - write the paper (due Nov 8).

## Rules
- Facts, not advice, in anything the model reads.
- One change per test, paired against a same-day baseline.
- Report the mean without the largest swing, plus wins and losses.
- Promote a change only after two positive results.
