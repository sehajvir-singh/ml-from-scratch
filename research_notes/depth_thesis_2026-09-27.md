# The Depth Thesis (2026-09-27)

Slide deck: https://claude.ai/artifact/KFU2kv8aL5cUTDYN29Qagj (private to the owner). Reproduce the numbers with
`python3 arc-prize-2026/agent/tools/depth_ladder.py [kaggle logs]`.

## Claim
On ARC-AGI-3, the score is limited mostly by **how many levels are cleared (depth)**, not by action efficiency.
The scoring rules cap a game's score at the weighted share of levels cleared (level k has weight k), so later levels
are worth much more than early ones.

## Evidence (verified)
- **Depth ladder over the 25 public games** (6–10 levels, mean 7.32). Clearing the first k levels in every game
  gives at most 3.52 / 10.57 / 21.14 / 35.24 / 52.85% for k = 1 to 5. Levels 1–3 hold only 21% of the weight.
- **Our Phase A smoke runs** (m2, m3; 3 games at 1,800 s each): in 4 of 6 game runs the score equals the depth cap
  exactly (vc33 3/7, tn36 1/7), so being more efficient than humans earned nothing. On bp35, efficiency limited
  the score.
- **Leaderboard** (Sep 27): our 4.07 is close to "level 1 everywhere". Tufa Labs' 27.29 falls between 3 and 4
  levels everywhere. That reading of averages is a GUESS, because game spread and the hidden games' level counts
  are unknown.

## Idea: the Depth Engine (a proposal; nothing built yet)
1. **An in-game action-effect CNN**, StochasticGoose style: it predicts, for this game's own transitions, which
   actions and clicks change the frame. It trains on the CPUs and its predictions feed the LLM agent.
   StochasticGoose reached 12.58% on the preview with no LLM (github.com/DriesSmit/ARC3-solution).
2. **Skill carry-over**: the harness wipes the world-model note at each level change. Instead, carry forward the
   rules that were confirmed by what happened.
3. **A depth-first clock**: spend less reasoning on moves that are already predicted, and save the time for new
   levels.

## Next measurement
Run the full 25-game Phase A once (`python3 go.py --variant base --phase-a full`, about 2.3 GPU hours), then run
depth_ladder.py on its log. This shows why each game stops (time, or one blocking level). That result decides
which part of the engine matters most, and it becomes the data for the Paper Track paper.

## Risks
- Tufa found that handcrafted tools hurt Duck. A learned hint might hurt in the same way, and only an A/B test
  can tell.
- So far only 3 games have been analysed.
- The CNN needs CPU time and must not slow the LLM down.
