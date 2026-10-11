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

## Part 1 built (2026-09-27): `grafts/affordance.py`, variant `d1`
- **Model:** a small CNN (3 conv layers, a 64x64 click head and a key head) trained on CPU during each game. It
  predicts whether an action makes a real change to the board.
- **Label fix found on real games:** vc33 and tn36 tick a one-cell step counter on the border on every action, so
  the harness's `board_changed` flag is almost always true. A diff of at most 3 collinear cells near the border
  counts as a timer tick, not an effect.
- **Offline test:** the synthetic "red is clickable" rule was learned in about 260 actions, independent of position.
- **Real games with a mock model making random moves** (vc33, tn36, ls20; 200 actions each):
  - 593 actions observed, 202 of them real effects; 65 trainings; 184 prompts carried a hint; 0 errors.
  - On tn36 the top hints named the 3-cell white objects. In the logs, every click on white changed the board
    (12 of 12), while clicks on the dominant colors mostly did not.
- **Gate:** a hint appears only when predict-then-learn accuracy over the last 30 actions is at least 80% and
  beats always guessing the majority label.
- **Not yet known:** whether this raises the hidden score. That needs Kaggle draws.

## Census results (2026-09-27): base B81, all 25 public games at the production clock (7,920 s per game)
Raw lines are in `research_notes/census/base_full_r1_2026-09-27.txt`.
- **Scores:** public-25 mean 8.24, median 3.57. Every game ended when the clock ran out (`gave_up`).
- **Levels cleared:** 0 levels in 3 games, 1 in 12, 2 in 4, 3 in 2, 4 in 4. Most games stop at level 1.
- **What limits each game:** the depth cap in 14 games, efficiency in 11. The thesis holds more weakly than the
  3-game smoke suggested. Efficiency matters too, mainly through a few catastrophic levels (ft09 level 4 took 360
  actions against a human's 28, losing about 24 points in that game).
- **Counterfactuals on the public 25:**
  - perfect efficiency on the levels already cleared: 8.24 -> 10.50 (+2.3);
  - one more level cleared in every game (at the cap): 8.24 -> **19.92 (+11.7)**.
  - Depth is still worth about 5x more than efficiency.
- **New finding: thrashing on the level in progress.** When the clock ran out, the unfinished level had often
  already taken far more actions than a human needs for the whole level: vc33 264 vs 61, sc25 254 vs 32, s5i5 218
  vs 89, su15 145 vs 42, g50t 148 vs 78, cd82 129 vs 55. Even a late clear there would score close to zero
  ((61/264)^2 = 0.05), and the time is gone. This points to part 3 of the engine: detect stalls and change
  strategy (a new hypothesis, a reset, or systematic exploration) instead of repeating.
- **Hidden-score context:** m-series draws are 3.41, 4.07 and 2.93 (mean 3.47), below B81's mean of 4.19. That
  supports dropping the prompt extras, which the lean draw on Sep 28 tests.
- **d2 smoke:** tn36 cleared 2 levels (10.71), the first time in 5 runs of that game (m2, m3, d1 and the census all
  cleared 1). It is only one game and could be noise, but it points the right way.
