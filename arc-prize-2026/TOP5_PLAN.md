# Top-5 plan (written 2026-09-29)

## Where we are
- **Us:** rank 55 of about 3,380, best hidden score 5.28 (plain B81).
- **Top five:** 45.33, 36.73, 26.55, 22.24, 20.53. Fifth place needs about 4x our score.

## The one lever that can close a 4x gap
Milestone prize money requires that "participants who open source their solutions by the milestone deadlines are
eligible" (arcprize.org). Milestone #2 closes **Sep 30**, so any top team that wants its $25K / $10K / $2.5K must
make its code public by then. After Milestone #1, the winner (Tufa Labs' Duck) was published, and every public
notebook since is built on it.

## Steps
1. **Oct 1, first thing:** look on the Kaggle Code tab (sort by Most Votes and Recently Run) and in the discussion
   forum for Milestone #2 releases from Tufa Labs, Yi-Chia Chen, Daniel Franzen, Lord Han Solo or Tong Hui Kang.
2. **Adopt it the same day:** run `python3 tools/adopt.py OWNER/SLUG` (default `--variant d3`). It builds two copies:
   - `out/adopt-<slug>`, left unchanged, as the control;
   - `out/adopt-<slug>-ours`, with the Depth Engine added. Each graft is wrapped so a harness mismatch skips it.
3. **Test both** with a Phase A run (`kaggle kernels push -p ...`). **Submit the unchanged one first**, since its
   hidden score becomes our new baseline. Submit ours the next day.
4. **Keep whichever wins over 2–3 draws.** The leaderboard keeps the best draw; the final uses 2 picks. Pick one
   safe and one ambitious.

## Honest odds (estimates)
- A 20–45-point notebook gets published by Oct 1: about 50–70%. Top teams want the prize money.
- If published, we reach 20+: about 70%, since we only need to run it.
- Top 5 on the **final private** leaderboard: about 3–8%. Hundreds of teams will copy the same notebook, and the
  original authors will keep improving, so winning a place needs our additions plus luck.
- If nothing is published: top 5 below 1%. Then we focus on the Paper Track.
