# Non-LLM and Hybrid Exploration Methods for ARC-AGI-3 Interactive Grid Games

Research date: 2026-09-25. Code-level details below come from reading the actual source files of the open-sourced winners (cloned 2026-09-25), not only their READMEs.

---

## Q1. ARC-AGI-3 Agent Preview Competition (2025) winners: methods, code, scores

### Takeaway
All top preview entries were search/exploration agents, not reasoning agents. They are StochasticGoose (a CNN that predicts which actions change the frame), Blind Squirrel (a state graph plus a ResNet18 value model) and Rudakov's frame-graph explorer (segmentation plus priority-tiered frontier search). They scored well on the 3-game preview by brute-force coverage: up to 256k actions. That advantage does not carry over to action-efficiency scoring on the full benchmark. StochasticGoose went from 12.58% to a reported 0.25%.

### Cited Findings
**Competition setup**
- The competition ran July 18 to Aug 19, 2025, with 3 public and 3 private games. Final scoring was on the hidden set only. The organizers' summary: "Both winning approaches used an informed search approach, exploring as much of the action space of the environment as possible in the hope of encountering a winning combination by chance." — [ARC-AGI-3 tech report](https://arxiv.org/abs/2603.24621); [Preview competition page](https://arcprize.org/competitions/arc-agi-3-preview-agents)
- Final evaluation runs were capped at 8 hours of wall-clock time and 10 environment steps/sec, shared across the three private games. That allows at most 96,000 steps per game. — [Rudakov et al., arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- The organizers found that "some preview games proved vulnerable to brute-force random search," so future games need stronger resistance to it. — [ARC Prize 30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings)

**Results table** (all from [30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings))

| Agent | Score | Levels | Games | Actions used | Method (one line) |
|---|---|---|---|---|---|
| StochasticGoose (Tufa Labs; Dries Smit, adviser Jack Cole) | 12.58% | 18 | 2 | 255,964 | CNN trained online with RL to predict frame-changing actions |
| Blind Squirrel (Will Dick) | 6.71% | 13 | 1 | 109,108 | State graph, pruning, ResNet18 value model |
| Fluxonian (Chadha, Nguyen, Singhal, Dominas) | 8.04% | 5 | 0 | 11,890 | DSL + LLM hybrid |
| Play Zero Agent (Dhana Abhiraj) | 4.37% | 5 | 0 | 7,226 | Random + LLM video analysis |
| Explore It Till You Solve It (Evgenii Rudakov) | 3.64% | 12 | 0 | 278,158 | Frame-graph exploration |

- Rankings were by number of levels completed, with total actions as the tiebreaker. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- The % score measures action efficiency. That is why Fluxonian (8.04%, 5 levels) and Play Zero (4.37%, 5 levels) have higher % than Rudakov (3.64%, 12 levels) but rank below the high-coverage explorers. The organizers note "action efficiency provides a clear intelligence signal", and that even the top entry reached only ~12% of human efficiency. — [30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings)

**StochasticGoose** — code: [github.com/DriesSmit/ARC3-solution](https://github.com/DriesSmit/ARC3-solution); core file `custom_agents/action.py`
- **Input**: the last frame of the animation, one-hot encoded to 16×64×64. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Backbone**: four 3×3 convolutions at full resolution, 16→32→64→128→256 channels, with ReLU and no pooling. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Action head**: MaxPool(4) to 256×16×16, then flatten, Linear(65,536→512), dropout 0.2, and Linear(512→5) for ACTION1–5. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Click head** (fully convolutional): conv 256→128→64 (3×3), then 1×1 conv →32→1, giving 64×64 = 4,096 click logits. Clicks are not handled by a flattened MLP. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Training target**: a binary label for "the frame changed after (state, action)". Loss is BCE-with-logits on the chosen logit, minus a tiny "entropy" term (the mean sigmoid, coefficients 1e-4 for actions and 1e-5 for coordinates). — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Optimization**: Adam at lr 1e-4, batch 64, one gradient step every 5 actions. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Replay buffer**: a deque of up to 200,000 entries, deduplicated with an MD5 hash of (one-hot frame bytes + action index). Each unique (state, action) pair is stored once. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Per-level reset**: when `score` changes (a new level), the buffer and hash set are cleared, and the model and optimizer are re-initialized from scratch. The author left a TODO: "Try not resetting the networks here." — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Sampling**: sigmoid over all 5 + 4,096 logits. Coordinate probabilities are divided by 4,096 so that ACTION6 as a whole competes fairly with the simple actions. The combined vector is normalized and sampled. Unavailable actions are masked to −inf using `available_actions`. On GAME_OVER the agent sends RESET. The run stops after 8h minus 5 min. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Full-benchmark result**: when ARC-AGI-3 launched on March 25, 2026, StochasticGoose reportedly scored 0.25% on the official leaderboard, roughly frontier-LLM level. This is a secondary source; I did not find the official leaderboard entry. — [DataCamp](https://www.datacamp.com/blog/arc-agi-3)

**Blind Squirrel** — code: [github.com/wd13ca/ARC-AGI-3-Agents](https://github.com/wd13ca/ARC-AGI-3-Agents); core file `agents/blind_squirrel.py` (497 lines)
- **State key**: `(game_id, score, full frame tuple)`. There is no HUD masking. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Action set per state**: the 5 simple actions plus one click action per connected component. Components come from `scipy.ndimage.label` run separately for each of the 16 colors. They are sorted by regularity (area/bbox area) descending, then area descending, then color. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Click location**: a *random pixel inside the component mask*, not the centroid. Centroids are used only as value-model features. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Graph and pruning**: the graph stores `future_states[action]` and `prior_states`. An action is set to weight 0 (never retried) if it returns the same state (no-op) or leads back to the level-start "milestone" state (a reset or death loop). `zero_back()` then propagates dead ends backwards: if every action from a state is 0, the incoming edge is zeroed recursively. A transition that disagrees with a stored edge is logged as a "Markov Violation". — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Count-based prior for untried actions**: `max(0.1, 1 × 0.5^no)` for simple actions and `max(0.1, 0.5^rank × 0.5^no)` for the k-th click object. Here `no` counts how often that action index was a no-op at this level. An action that has worked before gets weight `yes/(no+yes)`. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Value model**: a 16-dim color embedding, then a Conv3×3 stem to 64 channels, then ImageNet-pretrained ResNet18 layers 1–4 (the stem and maxpool are removed, so it runs at full 64×64). The pooled state vector goes to 64 dims and is concatenated with a 26-dim action vector (6 action-type one-hot, 16 color one-hot, regularity, size, y and x centroid). An MLP outputs a scalar. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Value target**: BFS distances to the level-winning state in the recorded graph. The target is `(d(s) − d(s'))/max_d`, and pruned actions get −1. Training uses MSE, Adam lr 1e-4, batch 32, up to 10 epochs capped at 15 min. It retrains from scratch after every level-up on all completed levels' data. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Policy**: when score > 0 and the state has known successors, the agent picks the argmax of the model with probability 0.5 (AGENT_E=0.5). Otherwise it samples from the rule weights. MAX_ACTIONS is 50,000 and there is a 0.1 s sleep per step. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Author's retrospective**: segmenting into same-color shapes cut the click space ~100×. A neural "validity" head, as the winner used, would have beaten the rules-based validity estimate. — [Blind Squirrel README](https://github.com/wd13ca/ARC-AGI-3-Agents)

**Explore It Till You Solve It (Rudakov)** — code: [github.com/dolphin-in-a-coma/arc-agi-3-just-explore](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore) (`agents/heuristic_agent.py`, `graph_explorer.py`); paper [arXiv 2512.24156](https://arxiv.org/abs/2512.24156) (AAAI-26 workshop)
- **Official result**: 12 of 25 private levels, 3rd place. After a reset-handling bug was fixed, it solved a median of 17 private levels over 5 reruns (range 14–19), "one level below the 1st-place solution". — [README](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore)
- **The bug**: actions that triggered a reset were not marked as tested. When such an edge was the nearest untested one, the agent looped on it forever. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- **Median over the full 8h**: 30/52 levels across 6 games (16 private, 14 public). — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- **Ablation at a 4,000-interaction cap** (median of 5 runs): a random agent solves 6 private and 3 public levels. The LLM+DSL baseline solves 5 private levels, so it did worse than random. Adding segmentation and then graph exploration raises the total to 19 levels: ft09 2, ls20 2, vc33 5, sp80 1, lp85 2, as66 7. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)

**Play Zero** — code: [github.com/dhanaabhirajk/ARC-AGI-3-Agents](https://github.com/dhanaabhirajk/ARC-AGI-3-Agents) (`agents/templates/play_zero_agent.py`)
- The loop is:
  1. Random play up to an action threshold.
  2. One video-LLM call analyzes the recording and sets a goal plus a max-actions limit.
  3. Image-LLM calls choose actions and check whether the goal was reached.
  4. The agent falls back to random exploration if the limit is hit or the level changes.
- It uses Gemini 2.5 Flash, and the author reports API cost of about $5–35. — [Play Zero README](https://github.com/dhanaabhirajk/ARC-AGI-3-Agents)

**Fluxonian**
- The only description found is "DSL + LLM hybrid method", 8.04%, 5 levels, 11,890 actions. — [30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings)

### Inferences
- **What mattered in the preview**: action throughput and systematic coverage. The winners spent 100k–280k actions for 12–18 levels. Rudakov's per-level tables (Q3) show that deep levels needed 10^3–10^4+ steps each.
- **Common core worth reusing**: all three non-LLM winners share three things: (a) a hash-keyed memory of (state, action) outcomes, (b) never retrying known no-ops, and (c) reducing clicks from 4,096 pixels to object-level actions (explicitly, or through a spatial conv prior).
- **Most Kaggle-friendly winner**: StochasticGoose. It is roughly 34M parameters (my count; ~33.5M of that is the 65,536→512 FC layer), GPU-light, and trains online. Blind Squirrel's ResNet18 needs ImageNet weights pre-staged as a Kaggle dataset, because internet is off.

### Gaps
- I could not fetch the StochasticGoose Medium write-up (HTTP 403): [medium.com/@dries.epos/...](https://medium.com/@dries.epos/1st-place-in-the-arc-agi-3-agent-preview-competition-49263f6287db). Its per-game results, action throughput and compute details are therefore unverified.
- There is no public code or write-up for Fluxonian.
- I found no primary ARC Prize source for StochasticGoose's 0.25% on the full benchmark; only a secondary source (DataCamp).

---

## Q2. Handling the 64×64 click action space: segmentation, centroids, and dead-signature pruning

### Takeaway
Every successful non-LLM agent turns clicks into object-level actions:
- same-color connected components, clicked at a random pixel inside or at the centroid;
- ranked by button-likeness (medium size, salient color, rectangularity);
- then pruned aggressively with no-op memory keyed by object appearance.

The strongest documented version is the "contextual dead-click rule" in BDR-Pro's agent. Reki's dead-signature (Milestone #1, 2nd place) does the same thing at the level of an object *type*.

### Cited Findings
- **The scale problem**: click games offer more than 1,000× more actions per state than arrow games, which "mak[es] exhaustive exploration intractable without intelligent action selection." — [Rudakov et al.](https://arxiv.org/html/2512.24156)
- **Rudakov segmentation**:
  - 4-connected, single-color components.
  - Five priority tiers:
    - **G0**: salient color (6–15) AND bbox width/height in [2, 32].
    - **G1**: medium size, non-salient color (0–5).
    - **G2**: salient color, not medium size.
    - **G3**: everything else except status bars.
    - **G4**: status bars.
  - The click lands on a random pixel of the segment.
  - Arrow games put all arrow actions in G0.
  — [heuristic_agent.py](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore/blob/main/agents/heuristic_agent.py)
- **Rudakov action choice**: pick uniformly among untested actions whose priority ≤ p in the current state. If there are none, go to the nearest state with such actions. Only when the whole graph is exhausted at level p does p increase. — [arXiv 2512.24156 Algorithm 1](https://arxiv.org/html/2512.24156); [README](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore)
- **Rudakov ablation**: adding frame segmentation to a random agent let it solve 5 levels of vc33 and 2 of ft09 on public games, where random alone solved far fewer. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- **Blind Squirrel**: one click action per per-color connected component. Components are ordered by regularity, then area, and untried click k gets prior weight 0.5^k (floor 0.1). The author says this cut the action space ~100×. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py); [README](https://github.com/wd13ca/ARC-AGI-3-Agents)
- **StochasticGoose** does no segmentation. It learns a 64×64 click heatmap with a fully convolutional head, giving spatial inductive bias, and trains it on frame-change labels. This way the agent learns which pixels do anything. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **Reki, Milestone #1 2nd place** (Gemma-4-31B vision-LLM policy):
  - It includes "a numpy click heuristic mechanism (no GPU needed)". Hardcoded rules make fallback and exploratory clicks "prefer small, rare-colored, button-like shapes instead of random pixels."
  - A "Dead-signature" "notices when clicking a *type* of object never changes anything and stops wasting clicks on it for the rest of the level."
  - Both are toggled by environment variables.
  - Notebook: [kaggle.com/code/ruichardliu/milestone1-2nd-solution](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution).
  — [ARC Prize Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1); [Kaggle announcement](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/725002)
- **BDR-Pro click tiers** (non-LLM Kaggle agent):
  1. Objects whose color matches a goal color from an earlier level.
  2. Exact coordinates that changed the grid before.
  3. Objects whose color has a productive click history.
  4. Cells that break a near-perfect mirror symmetry (≤8 broken pairs).
  5. Object centroids, ring interiors and recently changed cells, shuffled.

  — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **BDR-Pro dead-click pruning**:
  - Colors clicked ≥8 times with no effect are skipped entirely.
  - The contextual dead-click rule: "cell (x, y) showing color c does nothing" after ≥4 no-op clicks in that exact appearance. Keying the rule by appearance lets a button that changes color escape the ban.
  - The author says this rule let deep runs finish: level 5 of an 8-level game was solved in 56 actions against a 41-action human baseline.
  - In the changelog, v45 (contextual dead-click rules) brought "mean score +68% over v42".
  - Click-only games probe up to 192 candidates per state (the cap was raised from 96).

  — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **Why dead clicks matter for score**: in the local toolkit (arc_agi 0.9.6 / arcengine 0.9.3), a frame-unchanged ACTION6 increments both the per-level RHAE action tally and the action budget. The scoring docs, however, say operations that "do not alter the environment … are not counted." A participant asked for an official ruling. — [Kaggle discussion 718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638)

### Inferences
- **Recommended implementation** (numpy/scipy only, cheap enough to run every frame):
  1. Run `scipy.ndimage.label` for each color.
  2. Compute per-component features: color, area, bbox, regularity, centroid, touches edge, count of same-shape "twins".
  3. Mask out likely HUD/status-bar components.
  4. Rank components: salient/rare color and medium size first.
  5. Click the centroid if it lies inside the mask, else a random mask pixel.
  6. Keep a dead-signature table keyed by `(color, shape hash or size bucket)` for the level, plus a contextual key `(x, y, color)`.
- **Which to use when**: if no-op clicks count toward RHAE, as the toolkit suggests, pruning dead clicks directly raises the score, not just exploration speed. Reki's type-level signature generalizes faster (one failure bans all look-alikes). BDR's appearance-level rule is safer for buttons that change state. A hybrid is to ban the type after k failures but re-enable it when its appearance changes.

### Gaps
- Reki's notebook source (exact signature definition, thresholds) was not accessible via fetch. The blog summary is the only source.
- There is no official ruling in the fetched material on whether no-op ACTION6 counts toward RHAE on the scored server.

---

## Q3. State hashing and dedup, no-op pruning, loop detection, RESET/UNDO backtracking, BFS/novelty search, and action counts vs humans

### Takeaway
The standard recipe is:
- hash a HUD-masked frame;
- build a directed (state, action) → state graph;
- never retry no-ops or deadly edges;
- BFS through the known graph to the nearest frontier (a state with untried actions);
- after death or RESET, replay the best known prefix.

This solves many early levels but costs 10²–10⁴+ actions per deep level, against human baselines of tens to hundreds. RHAE squares the efficiency ratio, so these agents score near zero on the full benchmark even when they complete levels.

### Cited Findings
**Hashing**
- **Rudakov**: HUD masking, then blake2b-128 over the frame packed two 4-bit cells per byte, with the shape as the personalization string. Status bars are detected with rules:
  - the segment lies fully within 3 px of an edge; and
  - either its aspect ratio is ≥5, or ≥3 same-color, same-area "twins" sit on the same edge.

  The status-bar mask is recomputed on every level-up (score change). — [heuristic_agent.py](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore/blob/main/agents/heuristic_agent.py)
- **Why masking matters (Rudakov)**: masking status bars "substantially reduc[es] recognized state count". The method degrades toward random exploration when the status bar is integrated into the scene instead of sitting at the edge. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156); [README](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore)
- **BDR-Pro "volatility-masked hashing"**:
  - Masks cells that change in ≥20% of frames, or rows/columns that change in ≥40%.
  - The row/column rule catches a depleting energy bar that flips a different cell each action.
  - The mask "self-heals as evidence accumulates."

  — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **Blind Squirrel and StochasticGoose** hash the raw frame (plus score / action index) with no masking. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py); [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- **HUD pollutes "changed" signals**: per-action counter pixels "tick on every action and would otherwise register as 'effects'". BDR therefore uses ratio-based demotion of actions that are no-ops in ≥95% of tries. — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)

**No-op pruning and loop handling**
- **Blind Squirrel**: an edge is zeroed if it maps a state to itself or back to the level-start milestone. Dead ends propagate backwards via `zero_back()`. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **BDR-Pro**, all within a TransitionModel:
  - no-op skipping;
  - death avoidance (transitions that ended the game are banned);
  - an action that "mostly *reverts* the previous transition" is treated as an undo button and demoted;
  - anti-fixation that suppresses any action dominating the recent window without progress;
  - periodic "phase reseeds" to escape ruts.

  — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **Rudakov's loop bug** was a failure of loop detection: reset-inducing edges stayed "untested", so the agent kept choosing them. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)

**RESET/UNDO**
- In the preview games, a status bar shows steps remaining. When it reaches zero, the level resets to its initial state. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- All winners send RESET on GAME_OVER / NOT_PLAYED. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py); [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- The action set is ACTION1–5 (directional/control), ACTION6 (cell select) and ACTION7 (undo). AERA prefers ACTION7 after exploratory moves "to preserve state". — [AERA, arXiv 2605.25931](https://arxiv.org/pdf/2605.25931)
- **BDR-Pro memory**: `GameMemory` keeps the "best action prefix per level-start state, pruned of visible no-ops". After death the agent replays that prefix "instead of re-earning progress". Its opening probe presses each simple action 3× (~12–24 actions). — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)

**Search**
- Rudakov's graph explorer keeps shortest-path distances to frontier nodes and follows next hops. It is a deterministic Go-Explore-like "return then explore" with no learning. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- BDR-Pro plans with BFS "to a known score-up transition, or to the nearest frontier state with untried actions". Plans are verified step by step and abandoned on the first mismatch. — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- Kaggle's early top public-LB notebooks (~0.44, April 2026) used an *offline* BFS that instantiated the 25 public game engines, solving ~12/25 at near-perfect efficiency. Commenters pointed out that hidden games are not accessible this way, so the approach does not transfer; "none of the submissions have cracked the 1% barrier". — [Kaggle discussion 687950](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/687950)

**Actions used vs humans**
- **Rudakov**, median steps to solve each level over 5 runs:
  - ls20: L1 124, L2 ~3.2k, L3 not solved.
  - ft09: L1 125, L2 177, L3 ~20k.
  - vc33: L1 9, L2 7, L3 36, L4 321, L6 ~69k.
  - sp80: L1 227, L2 ~36k, L3 ~39k.
  - lp85: L2 ~2.9k, L3 ~17k.
  - as66: L1 39, L2 44, L3 123, L5 ~2.2k.

  — [arXiv 2512.24156, Tables 1–2](https://arxiv.org/html/2512.24156)
- **Human baselines and scoring**:
  - Baseline = the "upper-median best human" action count per level, from 10 tested humans per environment.
  - Per-level score = (h/a)², capped at 1.15×.
  - Example: a 10-action human level solved in 100 actions scores 1%.
  - For official frontier-model evaluation, the agent is terminated after 5× the human-baseline median actions per level.

  — [ARC-AGI-3 tech report](https://arxiv.org/abs/2603.24621)
- **Other assessments**:
  - The Twin paper: training-free graph exploration "reaches deep states through unbounded search, but at near-zero action efficiency." — [Twin, arXiv 2608.14490](https://arxiv.org/abs/2608.14490)
  - The 30-day learnings: agents "often required excessive exploratory actions" compared with humans. — [30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings)

### Inferences
- **Rough scale**: a level where a human needs ~50 actions and graph search needs 3,000 scores (50/3000)² ≈ 0.03%. Graph search only earns meaningful RHAE on levels it clears within ~1–2× human. Mostly these are tutorial first levels, or later levels where banked prefixes and carried-over hypotheses shortcut exploration (BDR's level-5-in-42-actions example).
- **Budget cutoff**: if a 5× per-level cutoff applies on Kaggle (unconfirmed for Kaggle; see Gaps), levels needing more than 5× human actions are simply unscorable. Brute-force depth is then worthless, and pruning plus good priors dominate.
- **Masking**: HUD masking (edge-rule plus volatility-rule) should be the default state key. Unmasked hashes inflate the state count by the number of step-counter values.

### Gaps
- Whether Kaggle's scored server applies the 5× per-level cutoff, and whether RESET counts as an action, is not documented in anything I could fetch.
- No source gives BDR-Pro's or Blind Squirrel's per-level action counts vs human baselines on private games.

---

## Q4. Curiosity and intrinsic motivation (count-based novelty, Go-Explore, RND) on ARC-AGI-3

### Takeaway
There are no published ARC-AGI-3 results for neural curiosity (RND, ICM). What works in practice is tabular: "untested (state, action)" frontiers, a count-based prior over action indices, and Go-Explore-style return-to-frontier through the known graph. Twin (an LLM-coded world model) uses a Go-Explore-style novelty search inside its simulator for goal discovery. Rudakov explicitly doubts that surprise correlates with goal relevance in these games.

### Cited Findings
- **Background papers**:
  - Go-Explore remembers visited states, returns to promising ones, then explores from them. — [Go-Explore, arXiv 1901.10995](https://arxiv.org/abs/1901.10995); ["First return, then explore", arXiv 2004.12919](https://arxiv.org/abs/2004.12919)
  - RND's exploration bonus is the error of a network predicting the features of a fixed, randomly initialized network. — [RND, arXiv 1810.12894](https://arxiv.org/abs/1810.12894)
  - ICM uses prediction error as intrinsic motivation. — [Pathak et al., arXiv 1705.05363](https://arxiv.org/abs/1705.05363)
- **How Rudakov frames it**: his paper positions graph exploration against curiosity (Pathak 2017) and Go-Explore (Ecoffet 2021) as a "strong baseline" that needs no training. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- **Rudakov's skepticism**: a learned next-frame world model could improve sample efficiency, but "it's unclear whether such models would help prioritize exploration of 'interesting' states … why should the correct pattern in `ft09` be more surprising than an incorrect one?" — [README](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore)
- **Twin's goal discovery** is "a Go-Explore-style novelty search (Ecoffet et al. 2021)". BFS inside the learned twin scores reachable states on visual-change signals (Q7), with depth 14 and 30,000 states. — [Twin, arXiv 2608.14490](https://arxiv.org/abs/2608.14490)
- **Count-based variants in winning code**:
  - Blind Squirrel down-weights action indices by 0.5^(#no-ops at this level) with a floor of 0.1. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
  - Rudakov treats any untested edge as maximally novel (tested/untested flag). — [heuristic_agent.py](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore/blob/main/agents/heuristic_agent.py)
  - BDR-Pro's "momentum" repeats an action while it keeps discovering new states. — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- StochasticGoose's "frame changes" target acts as a learned *effect* predictor, not a novelty bonus. It biases the agent toward actions that do something, not toward unseen states. The dedup buffer stops repeated pairs from being overweighted. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)
- An emergentmind summary asserts that curiosity "offers no guarantee of correlation with task progress in truly novel environments". This is an aggregator, not primary evidence. — [emergentmind ARC-AGI-3 topic](https://www.emergentmind.com/topics/arc-agi-3)

### Inferences
- ARC-AGI-3 is deterministic and fully observable (both Blind Squirrel and Rudakov rely on this). Exact-hash visit counts therefore dominate learned novelty (RND) as a bonus, and cost nothing. RND is only worth considering for generalizing novelty across near-duplicate states, e.g. unmasked HUD variants. Volatility masking solves that more cheaply.
- Go-Explore's "return" step has no simulator-restore primitive on the scored server. Implement it as RESET plus replaying a banked shortest path from the level start, or as graph navigation from the current state. Each replayed action costs RHAE, so return only to high-value cells.

### Gaps
- I found no experiment reporting RND, ICM or learned-novelty agents on ARC-AGI-3 (preview or full), and no Kaggle notebook reporting their LB score.
- Two Kaggle notebooks titled "ARC-AGI-3: Graph-Based Exploration (lightweight)" and "Graph Exploration w/ Value Learning" exist; a search snippet described one as a "deterministic Go-Explore style state-graph explorer". I could not access their content or scores. — [notebook 1](https://www.kaggle.com/code/nihilisticneuralnet/arc-agi-3-graph-based-exploration-lightweight); [notebook 2](https://www.kaggle.com/code/nihilisticneuralnet/arc-agi-3-graph-exploration-w-value-learning)

---

## Q5. Online learning at test time: small CNNs that predict frame changes or level progress, and their compute costs

### Takeaway
Two proven designs exist. StochasticGoose trains an ~34M-param CNN online (every 5 actions, re-initialized each level) to predict whether an action changes the frame. Blind Squirrel retrains a ResNet18 value model after each level-up, up to 15 min per retrain, to predict progress toward the level's win state. On Kaggle (9 h, one RTX Pro 6000, 110 games) this compute has to be shared across many concurrent games, and it bought levels, not efficiency.

### Cited Findings
- **StochasticGoose** — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py):
  - One gradient step (batch 64) every 5 environment actions, Adam lr 1e-4.
  - Inference on every step.
  - Full-resolution convs up to 256 channels at 64×64.
  - The model and the 200k deduplicated buffer are reset per level.
- **StochasticGoose throughput**: 255,964 actions over the preview's 8 h shared across 3 games. — [30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings); [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- **Blind Squirrel** — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py):
  - Full-res ResNet18 (ImageNet init, stem and maxpool removed).
  - Retrained from scratch on all completed levels after each level-up.
  - 10 epochs, batch 32, capped at 15 minutes.
  - Used greedily 50% of the time once score > 0.
- **Kaggle compute**: an RTX Pro 6000 with 96 GB VRAM and 9 hours to play 110 games in any order. — [Tufa Labs write-up, Kaggle discussion 717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)
- **Kaggle options**: accelerators are cpu/t4/p100/rtx6000, with RTX 6000 "reserved for ARC-AGI-3 notebooks". Internet is disabled. — [ARC Prize 2026 docs](https://docs.arcprize.org/arc-prize-2026)
- **Concurrency**: the framework plays 110 games in concurrent threads, so a model must be loaded once and served. A per-agent load caused a GPU out-of-memory crash and a 0.00 score. BDR-Pro's CPU agent was capped at 160 s wall-clock per game with a guaranteed 4,000-action floor (budget 16,000). — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- A Kaggle participant reports H100s were offered early in the competition "but that didn't last long" (anecdotal). — [Kaggle discussion 732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854)

### Inferences
- **Budget per game**: 9 h / 110 games ≈ 295 s per game if run sequentially. StochasticGoose-style exploration (tens of thousands of actions per game with a training step every 5 actions) is not affordable per game. A shared batched model, a much smaller net, or training only while stalled is required.
- **Right-sizing**: the 33.5M-param FC action head is the obvious thing to shrink (e.g. global pooling), because the click head already carries the spatial signal.
- **Better targets than raw "frame changed"**: StochasticGoose's labels will be polluted wherever a HUD counter ticks on every action, which BDR-Pro reports as common. Train on "masked frame changed" (volatility-masked) instead.
- **Keep learning across levels**: StochasticGoose resets per level, so it gets no transfer. A cheap improvement is to fine-tune rather than reset, as the author's own TODO suggests.

### Gaps
- No source reports GPU-hours or per-step latency for StochasticGoose or Blind Squirrel.
- No source reports a CNN-based agent's Kaggle LB score under the 2026 rules. StochasticGoose's 0.25% is on the official ARC-AGI-3 leaderboard, not Kaggle.

---

## Q6. Player/agent detection: finding the controllable object by diffing frames after directional actions

### Takeaway
The only fully documented non-LLM avatar detector is BDR-Pro's. For each directional action, it diffs consecutive frames, restricts attention to the changed region's bounding box, and matches color masses to find "movers". Each move votes (color, action) → (dx, dy), and the avatar is the color whose delta is most consistent per action. Guards reject autonomous motion (gravity, conveyors).

### Cited Findings
- BDR-Pro "diffs the grid, restricts attention to the changed region's bounding box, and matches color masses to detect movers. Each observed move votes `(color, action) → (dx, dy)`. The avatar is the color whose deltas are most consistent per action." — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **Guards**:
  - Colors whose dominant delta is identical for ≥3 different actions are **autonomous** (gravity, conveyors), not the avatar.
  - Duplicate deltas across actions are dropped ("falling pieces made every key 'move down'").
  - Steps of 1–5 cells are accepted.
  - Colors that repeatedly block movement and were never walked on become **walls**.
  - Colors that ever moved under our actions are **pushable**, never walls.

  — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **Using it**: the opening probe (each simple action pressed 3×) "converges the avatar model in ~12–24 actions". Once ≥2 directions are known, navigation turns on:
  - BFS over the grid using the learned deltas, checking each crossed cell against wall colors;
  - targets in order: goal-colored cells, then rare-colored cells, then unexplored frontier;
  - on arrival, try every untried non-movement action.

  — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- BDR-Pro's changelog lists "v12: Diff-based avatar detection (bbox-restricted mover matching)". — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- None of the three preview winners detects an avatar. They operate on whole-frame hashes. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py); [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py); [heuristic_agent.py](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore/blob/main/agents/heuristic_agent.py)

### Inferences
- **Minimal implementation**:
  1. `diff = (f_t != f_{t+1})` after masking volatile cells.
  2. Label the connected components of the changed region per color.
  3. For each color present in both frames, compute the centroid shift (or find the best integer shift of the color mask within ±5 cells that maximizes overlap).
  4. Tally votes per (color, action).
  5. Accept color c as the avatar when ≥2 actions give distinct, consistent non-zero deltas and no single delta repeats across ≥3 actions.
- **Payoff**: this converts arrow games from pixel-state BFS into grid-coordinate BFS. The state space collapses to (avatar position × a few object states), which is where graph exploration stops exploding (Rudakov's ls20 L3+ failures).

### Gaps
- There are no quantitative accuracy numbers for avatar detection, and no ablation of its score contribution, in any source found.
- No other open-source non-LLM avatar detector was found for comparison.

---

## Q7. Goal inference: detecting level completion and progress signals (progress bars, step-counter pixels)

### Takeaway
Level completion is observable directly: the frame's `score` / `levels_completed` field increments, and the `state` becomes WIN at game end. Every agent uses that as its only reward. Beyond it, useful signals come from the HUD and from visual-change heuristics. First, mask step counters so they don't pollute state identity. Second, learn "goal colors" (colors that shrink when score rises). Third, rank candidate states by color_gone, color_new, local_burst and big_change.

### Cited Findings
- **Completion signal**:
  - The FrameResponse fields are game_id, guid, frame, state, levels_completed, win_levels, action_input and available_actions. — [Kaggle discussion 718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638)
  - StochasticGoose and Blind Squirrel detect a new level when `latest_frame.score` changes, and stop on `GameState.WIN`. — [action.py](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py); [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
  - "The only feedback signal is level completion." — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
- **The goal frame is never observed**: ARC-AGI-3 "replaces the winning frame when reporting completion, so a true goal frame never enters the record and every recorded frame is a certified negative." Twin uses this to reject any goal predicate that fires on a recorded frame. — [Twin, arXiv 2608.14490](https://arxiv.org/abs/2608.14490)
- **Twin's goal-discovery signals**, ranked in order:
  1. **color_gone**: a start color vanishes entirely.
  2. **color_new**: a color absent at the start appears.
  3. **local_burst**: ≥5 cells change inside one compact bbox while the rest is static.
  4. **big_change**: more than 25% of cells change at once.
  5. **frontier**: fallback, the most-different reachable state.

  The paper stresses these are "visual-change heuristics … [that] do not encode game-specific objects, actions, or goals." — [Twin, arXiv 2608.14490](https://arxiv.org/abs/2608.14490)
- **BDR-Pro goal colors**: "colors that shrank when the score went up" carry across levels, so later levels start with a target hypothesis. Goal-colored objects become the top click tier and navigation targets. Mirror-symmetry-breaking cells are a click tier for "repair the picture" puzzles. — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **Progress and step-counter HUD**:
  - Preview frames contain a status bar showing steps remaining. The level resets at zero, and most games also display levels passed. — [arXiv 2512.24156](https://arxiv.org/html/2512.24156)
  - Rudakov detects these bars by edge position, aspect ratio and twins, and masks them. — [heuristic_agent.py](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore/blob/main/agents/heuristic_agent.py)
  - BDR-Pro masks them by volatility (row/col ≥40%). — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **Learned progress estimate**: Blind Squirrel's value target, normalized BFS distance-to-win, is the only learned level-progress estimator found in the winning code. It becomes available only after the first level is solved. — [blind_squirrel.py](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)
- **Why a pre-reward hypothesis matters**: Twin reports its first goal hypothesis was correct on 156 of 179 completed levels (87.2%). A pre-reward goal hypothesis lets actions be spent on a planned route rather than on surfacing the first win. — [Twin, arXiv 2608.14490](https://arxiv.org/abs/2608.14490)

### Inferences
- **Reusing the HUD**: the masked HUD is itself a free signal.
  - A steps-remaining bar gives the per-attempt action budget before a forced reset, so the explorer can plan a RESET-free horizon.
  - A levels-passed indicator is redundant with `levels_completed`.
  - An energy bar that refills on some event is a candidate intermediate reward.
  - A cheap implementation: record masked-HUD pixel counts per color over time and flag any action whose effect on HUD counts differs from the per-step baseline.
- **A cheap non-LLM goal prior**: combine Twin's five signals (computable on real transitions, not just simulated ones) with BDR's goal-color carry-over. Before any reward, prefer actions whose outcomes produced color_gone, color_new or local_burst.

### Gaps
- No source quantifies how often HUD progress bars predict level completion across the 25 public games.
- No non-LLM implementation of Twin's signals exists as an exploration bonus on real play; Twin applies them inside an LLM-written simulator.

---

## Q8. Does the AERA paper (arXiv 2605.25931) show that trivial strategies solve many public games? Which strategies, and are they usable as a cheap first pass?

### Takeaway
Yes, the paper claims that all 25 public games are "reachable through non-intelligent strategies". But the evidence has serious validity problems:
- The author found that a null-coordinate ACTION6 crash is misreported as WIN, and it overlaps the "blind" category.
- The RHAE numbers match exactly the capped maximum per "solved" game.
- The Kaggle score the paper reports as 30% is most likely 0.30 on Kaggle's 0–100 scale.

Treat the paper as a hint for a cheap probe step (ACTION6 early, single-action repetition), not as evidence of transfer to private games.

### Cited Findings
- **The taxonomy** — [AERA PDF](https://arxiv.org/pdf/2605.25931):

| Category | Games | What wins |
|---|---|---|
| Blind depth-1 ACTION6 | FT09, CN04, M0R0, LF52, BP35 | One ACTION6, no exploration |
| Other blind depth-1 | R11L, VC33, LP85, TN36, S5I5 | One other action |
| ACTION6 after probing | SB26, CD82, AR25, SK48, DC22 | ACTION6 once the LLM has seen its effect |
| Repeated ACTION1 | SP80 | 30+ ACTION1 presses |
| Diverse exploration | SU15 | ReAct, 50 steps |
| Budget-constrained | see list below | One action repeated 50–200 times |

- **Budget-constrained games** (named "keyboard/click"): TU93 (ACTION1 ×50), RE86 (ACTION1 ×100), TR87 (ACTION1 ×128), KA59 (ACTION6 at (32,32) ×100), LS20 (ACTION2 ×129), SC25 (ACTION6 at (24,48) ×52), G50T (ACTION1 ×130), WA30 (ACTION1 ×200). — [AERA PDF, Table 9](https://arxiv.org/pdf/2605.25931)
- **Depth-4 search found nothing short**: an exhaustive depth-4 search on 13 "hard" games found no winning sequence of length ≤4 (2,401 sequences per game). — [AERA PDF](https://arxiv.org/pdf/2605.25931)
- **Null-coordinate vulnerability**: ACTION6 with `{"x": None, "y": None}` raises a TypeError in the engine, which the arc_agi wrapper "returns as a WIN signal". This affects 18/25 public games and was confirmed on local arc_agi v0.9.8. The paper says it "is not confirmed to work on the Kaggle competition server". — [AERA PDF](https://arxiv.org/pdf/2605.25931)
- **Action-selection bottleneck**: the Qwen2.5-0.5B policy never chose ACTION6 on CN04/M0R0/LF52. Forcing ACTION6 as the first exploration step solved them in 5/5 runs. The paper calls the fix "one line". — [AERA PDF](https://arxiv.org/pdf/2605.25931)
- **AERA's own results**:
  - RHAE 0.2116 (4/25) on public games with Qwen2.5-0.5B on CPU in FP32 (Kaggle P100 session).
  - An EXPLORE budget of `max(5, min(30, ⌊0.4·H⌋))`.
  - A ReAct baseline with 50 steps scored 0.388 (8/25).

  — [AERA PDF](https://arxiv.org/pdf/2605.25931)
- **Kaggle submission**: the kernel `arc-agi3-v31-zorojuro-hybrid-v9` is a BFS solver "augmented with an offline pre-solve cache". It tries action sequences up to depth d with a 180 s/level limit, falling back to a heuristic planner. It is reported as "RHAE = 0.30 (30%)", described both as a "public score" and as "on the full 55-game private evaluation", and compared against "≈12.58%" as the community best. — [AERA PDF](https://arxiv.org/pdf/2605.25931)
- **Contradicting context on the Kaggle scale**:
  - In April 2026 a commenter noted the Kaggle top score "is 0.68 – that's 0.68%". — [Kaggle discussion 687950](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/687950)
  - BDR-Pro's mature programmatic agent scored 0.26–0.27 against a leaderboard #1 of ~3.57 (earlier snapshot), and the private LB uses 110 games, not 55. — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3); [Tufa write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)
  - 12.58% was the 2025 *preview* score, not a full-benchmark community best. — [30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings)
- **Offline BFS does not transfer**: offline BFS over the 25 public engines does not apply to hidden games, which are only reachable through the submission API. — [Kaggle discussion 687950](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/687950)

### Inferences
- **The "solved" counts look like artefacts.** 0.2116 = 4 × 1.3225 / 25 exactly, and 1.3225 = 1.15², the per-level cap. So every "solved" game received the maximum capped score from a handful of actions. That is inconsistent with official RHAE, which is per-level and caps an environment at the fraction of levels completed. It suggests "solved" means a game-level WIN flag, and the null-coordinate crash-as-WIN bug covers the same "blind" games.
- **Some claims are implausible.** Examples: LS20 (a multi-level maze with a human baseline in the hundreds) won by pressing ACTION2 129 times, or whole games won in one blind step. Reproduce them with `levels_completed` checks before trusting them.
- **The 30% claim is very likely 0.30%.** It is almost certainly Kaggle's 0–100 scale (≈0.3%), similar to BDR-Pro's non-LLM ceiling (0.26–0.27).
- **What is usable as a cheap first pass** (~≤30 actions per level):
  - press each simple action a few times (BDR's opening probe, which also bootstraps the avatar model);
  - include ACTION6 on the top-ranked salient objects early, since LLM priors under-select it (AERA's bottleneck finding);
  - watch for a monotone single-action trend (the same action keeps producing new masked states), and repeat it with momentum only while it keeps yielding novelty.
- **Never rely on**: the null-coordinate exploit (likely patched, illegitimate, and not a real level solve), or offline pre-solve caches of public games.

### Gaps
- I could not verify from ARC Prize or Kaggle sources whether the null-coordinate bug still exists in current arc_agi/arcengine versions or on the scored server.
- I could not confirm whether AERA's "solved" means levels_completed == win_levels or only the wrapper's WIN flag.
- The per-game human baselines for the Table-9 games are only summarized as "350–1843 total".

---

## Q9. Evidence that non-LLM exploration performs on the full benchmark and on Kaggle (constraints and transfer)

### Takeaway
On Kaggle's hidden 110-game set, mature non-LLM programmatic agents plateau around 0.26–0.27 (on a 0–100 scale). The public LB top was 19.45 as of 2026-09-25, and the top entries run LLM agents on GPU. Non-LLM exploration is therefore best used as the backbone or floor under an LLM (perception, pruning, memory, BFS), not as a standalone solver.

### Cited Findings
- **Kaggle public leaderboard snapshot, 2026-09-25**:
  - 3,320 teams.
  - #1 "Lord Han Solo" 19.45, #2 Tufa Labs 18.81, #3 Yi-Chia Chen 18.63, #10 8.81, #100 4.32, #500 3.23.
  - About 1,663 teams score above 0.3 and about 1,232 above 1.0.

  My counts come from the leaderboard JSON a co-researcher fetched on 2026-09-25. — [Kaggle ARC-AGI-3 leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard)
- **BDR-Pro's plateau**: the non-LLM agent went from 0.00 to 0.17, then plateaued at 0.26–0.27 (v54–v79). "Past a point, local score stopped predicting the LB … Even correct bug fixes and a +50% local mean moved the LB by ±0.01." The author then inverted control: the programmatic agent drives, and a GPU LLM is called only on stalls. — [BDR-Pro README](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)
- **Public-to-private gap for LLM harnesses**: participants report local public-25 scores of 7.6–22 mapping to LB 3–7. One team: "5.0+ on 25 games and 1.6 on the 110 games". — [Kaggle discussion 732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854)
- **Milestone #1 winners** (June 30, 2026) all used locally served LLMs (Qwen 3.6 27B FP8; Gemma-4-31B) with light non-LLM helpers. Reki's helpers were the numpy click heuristic and the dead-signature rule. Tufa found "hand-crafted tools actually hurt the model." — [Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- **Harness pitfall**: the shipped ARC-AGI-3-Agents `Agent` base class has `MAX_ACTIONS = 80` (effectively 81 actions), which is not documented in the README. A subclass that doesn't override it stops mid-game. — [Kaggle discussion 734054](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734054)
- **Launch results**: ARC-AGI-3 scores humans at 100% vs frontier AI below 1% as of March 2026. — [ARC-AGI-3 tech report](https://arxiv.org/abs/2603.24621)
- **Tutorial levels**: level 1 of each environment is intentionally easy, and "random agents can occasionally stumble into success at this stage". — [ARC-AGI-3 tech report](https://arxiv.org/abs/2603.24621)

### Inferences
- **Where to spend effort**: under 9 h / 110 games on one GPU, the highest-value non-LLM parts are the per-frame cheap ones:
  - volatility plus edge HUD masking and exact hashing;
  - no-op and dead-signature pruning;
  - avatar/wall/goal-color inference;
  - banked-prefix replay after death;
  - frontier BFS.

  Online CNN training (StochasticGoose, Blind Squirrel) adds levels mainly at action counts far above human, so it adds little under squared efficiency.
- **Suggested hybrid**, following BDR-Pro's inverted control:
  1. The programmatic explorer runs a short probe budget per level and handles tutorial levels.
  2. When it stalls, it hands a compact, pruned object/action summary to the LLM. This counters the LLM's action-selection biases (AERA's ACTION6 finding) and saves context.
- **Local evaluation**: public-game local scores are a weak proxy for the LB. Evaluate mechanisms on held-out subsets and across multiple seeds rather than maximizing the public-25 mean.

### Gaps
- There is no official breakdown of LB entries by method (LLM vs non-LLM). The ~0.27 non-LLM ceiling rests on one well-documented team (BDR-Pro) plus Kaggle discussion comments.
- The private LB (final standings) and Milestone #2 results (deadline Sept 30, 2026) were not yet available on 2026-09-25.
