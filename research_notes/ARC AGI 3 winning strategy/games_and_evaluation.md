# ARC-AGI-3 Games (Public-Set Catalog, Mechanics, Design Rules) and Reliable Local Evaluation

Research date: 2026-09-25. Primary data was pulled directly from the ARC API (`https://three.arcprize.org/api/games`, using an anonymous key from `/api/games/anonkey`) and from the game source files served at `/api/games/{game_id}/source`. The toolkit wheels (`arc-agi 0.9.9`, `arcengine 0.9.3`, `arc-agi-core 0.1.14`, `arc-agi-dsl 0.0.3`) were downloaded to `/tmp/arcpkgs` and inspected. Per-game mechanic descriptions come mainly from the community "arc-explainer" write-ups, which were checked against the game source ([arc-explainer shared/arc3Games](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games)). I spot-checked them against the obfuscated source myself, for example the action sets and the lose conditions.

## Q1. Catalog of the 25 public ARC-AGI-3 games: mechanics, levels, human baselines, controls, goal signals

### Takeaway
There are 25 public games with 183 levels in total, and each game has 6–10 levels. Controls split into 4 keyboard-only games, 8 click-only games and 13 mixed games. Every game is a "configure the board to match a visible target, or reach a visible goal, within a budget" puzzle. The goal is almost always shown on screen as a reference pattern, outline, marker, exit tile or target dot. Nothing ever states the goal in text. Human baselines per level range from 6 to 578 actions.

### Cited Findings

**Official metadata (live API, fetched 2026-09-25).** The full list below comes from `GET https://three.arcprize.org/api/games` ([ARC API; the endpoint used by arc-agi toolkit `_fetch_from_api`](https://pypi.org/project/arc-agi/)). Game IDs carry a version hash, for example `ls20-9607627b`. The fields are `tags` (`keyboard` / `click` / `keyboard_click`) and `baseline_actions` (one entry per level, so its length equals the number of levels). Summing the level counts gives 183 levels, which matches the "25 public games … 183 levels total" reported by [Twin (arXiv 2608.14490)](https://arxiv.org/html/2608.14490).

The table combines three sources:
- The API data (levels, baselines, tag).
- `available_actions` read from each game's source (`/api/games/{id}/source`).
- Mechanic and goal descriptions from the arc-explainer write-ups ([per-game .ts files](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games)), which are "corrected against source". I quote or paraphrase them.

| Game (informal name) | Levels | Human baseline actions per level (API) | Sum | API tag / `available_actions` in source | Core mechanic (arc-explainer) | Goal signal / win condition |
|---|---|---|---|---|---|---|
| ar25 (Axis Reflectors) | 8 | 32,50,75,37,89,159,233,73 | 748 | keyboard_click / [1–7] | Move pieces and axis-aligned mirrors. A5 cycles the selection, A6 selects by click, A7 undoes. | "Live reflections must cover every target dot" |
| bp35 (Buoyant Pontoons) | 9 | 21,48,44,38,33,87,86,131,163 | 651 | keyboard_click / [3,4,6,7] | Move left/right only while an automatic "pull" carries you. Clicking blocks changes them: Green breaks, Orange toggles solid, Red flips the pull, Purple breaks and grows. The world is bigger than the viewport, so you must scroll to find the exit. | Reach the light-pink plus. Touching a purple spike loses. |
| cd82 (Compass Dye) | 6 | 55,8,41,21,23,23 | 171 | keyboard_click / [1–6] | Move a selector among 8 compass dye stations, fire with A5, pick a colour with A6. | Recreate the reference pattern shown in the corner before the move countdown runs out. |
| cn04 (Coded Notches) | 6 | 29,54,85,300,208,113 | 789 | keyboard_click / default [1–6] | Select a part (A6), slide it (A1–4) and rotate it (A5). | Every printed mark must meet its matching mark on another part. |
| dc22 (Deck Control) | 6 | 59,102,67,98,324,578 | 1228 | keyboard_click / [1,2,3,4,6] | Walk a green square while clicking panel buttons that swing, flip, extend or slide floor pieces. From level 5 you also drive a claw. | Reach the yellow goal square. A press that pulls the floor from under you costs 20 steps. |
| ft09 (Functional Tiles) | 6 | 43,12,23,28,65,37 | 208 | (no tag; click-only) / [6] | Clicking a tile steps it to its next colour. | Marker squares show a centre colour, and their border cells say whether the adjacent tile must (white) or must not (gray) be that colour. Win when all markers are satisfied within the click budget. |
| g50t (Ghost Twin) | 7 | 78,175,179,230,96,54,67 | 879 | keyboard / [1–5] | Your moves are recorded. A5 sends you back to the start and spawns a ghost twin that replays them, for example to hold a pressure plate. | Reach the goal before the timer bar drains. |
| ka59 (Kick Away) | 7 | 28,109,51,51,33,132,326 | 730 | keyboard_click / [1,2,3,4,6] | Select a box and push; bumped pieces fly about 15 cells. Bombs appear from level 5. | "Every outline frame on the board holds a piece of its size" |
| lf52 (Leapfrog) | 10 | 32,81,60,71,205,148,244,109,164,225 | 1339 | click / [1,2,3,4,6,7] | Peg solitaire played by clicking. From level 2, arrow keys drive rail carts that carry pegs between rooms. | Get down to one peg within the move budget. |
| lp85 (Loop and Pull) | 8 | 17,38,31,16,41,60,26,159 | 388 | click / [6] | Red/green buttons rotate loops of coloured squares backward or forward. | Every yellow (and on levels 3–4, orange) square sits inside a target of its colour, marked by four corner dots. |
| ls20 (Locksmith) | 7 | 22,123,73,84,96,192,186 | 776 | keyboard / [1–4] | Navigate onto transformer tiles that change the key's shape, colour and rotation. Refill pickups appear from level 2, launch pads from level 3, sliding tiles from level 5, and fog-of-war on the last level. | Reach the door with a key that matches the lock. Level 6 has two doors. |
| m0r0 (Mirror Rendezvous) | 6 | 30,111,203,26,500,237 | 1107 | keyboard_click / [1–6] | Two tokens move as mirror images. Bump one into a wall to desync them. From level 3, clicking a blue block lets you move it. | Both twins land on the same tile within 150 actions. |
| r11l (Reaching Lurch) | 6 | 22,33,51,26,52,49 | 233 | click / [6] | Drag a blob by its limbs. From level 5, bodies start white and must eat coloured food. | Body sits on its outline with an exactly matching colour (a colour-mixing flavour). |
| re86 (Reach Emblems) | 8 | 26,42,86,108,189,139,424,241 | 1255 | keyboard_click / [1–5] | Slide the selected outline piece and cycle selection with A5. Colour pads arrive at level 4; walls that bend or squash pieces appear in the last 3 levels. | "Every small target dot sits under a piece of its own color" |
| s5i5 (Sliding Indicator) | 8 | 20,89,106,54,162,38,86,83 | 638 | click / [6] | Grow or shrink colour-coded rods via slider buttons, and rotate them from level 6. | Markers riding the rods sit on every pin. |
| sb26 (Sequence Belt) | 8 | 18,28,18,19,31,23,58,18 | 213 | keyboard_click / [5,6,7] | Place coloured tiles into container slots (A6) and run them (A5). A7 undoes. | The output matches a required colour sequence, with 64 energy per level. |
| sc25 (Sigil Caster) | 6 | 36,6,32,83,143,50 | 350 | keyboard_click / [1,2,3,4,6] | Walk a wizard and draw patterns on a toggle grid. A matching sigil casts teleport, grow/shrink or fireball. | Reach the exit. |
| sk48 (Skewer Kebabs) | 8 | 61,177,101,103,230,181,125,92 | 1070 | keyboard_click / [1,2,3,4,6,7] | Extend, retract or slide a skewer that pushes beads. Select with A6, undo with A7. | Beads on each skewer match the reference skewers at the bottom. |
| sp80 (Streaming Purple) | 6 | 39,58,25,148,96,152 | 518 | keyboard_click / [1–6] | Select and move red bars (and purple L pieces from level 5). A5 pours. | One pour fills every yellow cup without touching a spill line. |
| su15 (Sucking Up) | 9 | 22,42,26,115,36,31,8,40,41 | 361 | click / [6,7] | Each click vacuum-pulls pieces within 8 cells, and same-size blocks fuse. A7 undoes for free. | The blue circles hold exactly the pieces listed in the top-centre "shopping list". |
| tn36 (Toggle Navigator) | 7 | 32,72,26,40,30,55,62 | 317 | click / [6] | Toggle switches to program move/rotate/scale/recolour instructions, then press run. From level 2 there are demo programs. | The token matches the target. |
| tr87 (Toggle Runes) | 6 | 54,58,40,45,71,146 | 414 | keyboard / [1–4] | Cycle glyphs (A1/A2) and move a bracket (A3/A4). Translate a phrase using a rune dictionary; in levels 5–6 you repair the dictionary instead. | The answer row is a correct translation. |
| tu93 (Trail Unwind) | 9 | 19,16,34,42,123,80,14,23,111 | 462 | keyboard_click (tag) / source [1–4] | Move a token along wires past enemies that bite from the front, patrol, or follow your trail. | Reach the green exit before the pink step bar runs out. One hit loses. |
| vc33 (Volume Control) | 7 | 7,18,44,61,131,34,152 | 447 | click / [6] | Click pumps to move liquid between tanks and gates to move riders. Tanks may be sideways or upside-down. | Each rider is level with a mark of its own colour, within the click budget. |
| wa30 (Warehouse Associates) | 9 | 71,119,183,98,368,68,79,442,415 | 1843 | keyboard / [1–5] | Sokoban with grab/release on A5. From level 2 other haulers move crates, sometimes against you. | Crates in their bays within the move budget. |

- Original preview games (2025): ls20 "Navigate a map while bringing a matching symbol to another object. The symbol must go through various transformations"; ft09 "Match the pattern seen on the screen. Patterns occasionally overlap"; vc33 "Alternate volume of objects in order to match levels to pre-specified heights" — [ARC Prize 30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings). The docs label them ls20 = "Agent reasoning", ft09 = "Elementary Logic", vc33 = "Orchestration" ([docs: available games](https://docs.arcprize.org/available-games)). arc-explainer notes that vc33, ls20, ft09 and sp80 have "original version" recordings, meaning they were reworked, and that ls20 had 8 levels originally and 7 now ([arc-explainer types.ts / ls20.ts](https://github.com/82deutschmark/arc-explainer/blob/main/shared/arc3Games/ls20.ts)).
- The official lab analysis describes these mechanics: cd82 uses "container rotation (ACTION3)" and "dipping/pouring (ACTION5)"; cn04 is "rotate-then-place"; ka59 has "character teleportation via clicking; shape-matching and pushing in later levels"; ar25 is "mirrored movement around divider; movable-axis mechanic". GPT-5.5 mistook ls20 for Breakout — [ARC Prize: Analyzing GPT-5.5 & Opus 4.7](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis). (The cd82 rotation wording differs from arc-explainer's "selector/stations" wording; both describe the same game from different angles.)
- Human first-run data on the public set: 342 human replays across the 25 games and 145 total solves. For example, "10 out of 10 participants solved r11l, whereas only 6 out of 12 solved tr87" — [ARC Prize: Measuring Human Performance](https://arcprize.org/blog/arc-agi-3-human-dataset).
- Relative difficulty for frontier agents on the public games (single runs, GPT-5.5 with a coding-agent world-model harness):
  - Full or near-full: ar25, ka59, lp85, tr87 and tu93 at 100%; g50t 95%, cn04 96%, cd82 93%, r11l 89%, sb26 84%.
  - Near zero: dc22 0%, s5i5 0.25%, bp35 4.4%, wa30 9.1%, sk48 11%.
  - Source: [Executable World Models, arXiv 2605.05138, Table 2](https://arxiv.org/abs/2605.05138).
  - Twin cleared 23 of 25 games; only sc25 (32.7) and sp80 (81.2) stayed unsolved. It says bp35, lf52 and sk48 were cleared only by Twin among the systems it compared — [Twin, arXiv 2608.14490](https://arxiv.org/html/2608.14490).

### Inferences
- The API `tags` are coarse and sometimes inaccurate. tu93 is tagged `keyboard_click` but the source exposes only ACTION1–4. re86 is tagged `keyboard_click` but uses ACTION1–5 with no click. ft09 has no tag. An agent should read `available_actions` from each frame rather than trust tags.
- Counted by actual action sets:
  - Keyboard-only (ACTION1–5): ls20, g50t, wa30, tr87, tu93, re86.
  - Click-only (ACTION6, maybe ACTION7): ft09, lp85, r11l, s5i5, tn36, vc33, su15.
  - Mixed: all the others.
  - Mixed games typically use the click as a **selector** ("click to select which object the arrows control") rather than as the main verb.
- In every game the win state is a *visible relation* between on-screen objects: matching a reference pattern, a target outline or marker, a coloured goal tile, or a lock shape. An agent can therefore search for "goal-like" static objects (outlines, corner-dot frames, small reference panels, distinctively coloured single tiles) and treat "make X match / overlap Y" as its default goal hypothesis.
- Level 1 is a cheap tutorial: 7–78 actions, with a median of about 30. Later levels grow roughly 3–10×, for example vc33 goes from 7 to 152 and dc22 from 59 to 578. Because levels are weighted by index (see Q7), most of a game's score sits in the late levels, which introduce new mechanics mid-game.

### Gaps
- I did not verify the level-by-level mechanic introductions for every game beyond the arc-explainer write-ups. Those are community-authored (partly by LLMs, then "corrected against source") and are not official.
- The ARC Prize game pages (three.arcprize.org/games/{id}) did not return descriptive text through fetch, so there are no official per-game mechanic descriptions beyond the 3 preview games and the 5 games named in the GPT-5.5/Opus analysis blog.
- The API does not expose per-level human variance, only one baseline number per level. The human-dataset blog says baselines are now the median human per level.

## Q2. Recurring mechanic families

### Takeaway
The 25 public games draw on about 10 families: avatar navigation under a budget, pushing/Sokoban, select-then-move of multiple objects ("orchestration"), click-to-cycle/toggle state, matching against a reference, fluids/volumes, geometric transforms (rotate/scale/mirror), temporal record-replay, autonomous or adversarial actors, and partial observability. Most games combine 2–4 of these, and new ones are added in later levels. The official design intentionally avoids single-mechanic games, and the private set is stated to have "limited overlap" with public mechanics. An agent should therefore learn general *meta-skills*, not specific families.

### Cited Findings
- Families and example games, derived from the arc-explainer descriptions quoted in Q1 ([arc-explainer](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games)):
  - **Avatar navigation / maze + resource budget:** ls20, tu93, dc22, bp35, sc25, g50t, m0r0.
  - **Push / Sokoban / collision physics:** wa30 (explicitly "Sokoban-style crate hauling"), ka59 (kick boxes into frames), sk48 (skewer pushes beads), re86 (slide pieces onto dots), cn04 (slide parts).
  - **Select-then-move multiple objects (orchestration):** ar25, re86, ka59, sp80, cn04, sk48, m0r0 (level 3+), lf52.
  - **Click-to-cycle / toggle:** ft09 (tile colour cycling), tn36 (switch toggles), sc25 (sigil grid toggles), tr87 (glyph cycling via keys), bp35 (orange blocks toggle solid).
  - **Match a reference / target pattern:** ft09, cd82, sk48, sb26, tr87, tn36, su15, r11l, re86, lp85, ka59.
  - **Fluids / volume:** vc33 (tank levels), sp80 (pour stream into cups), bp35 (flooded shaft).
  - **Geometric transforms:** rotate (cn04, tn36, s5i5 from level 6, ls20 key rotation); scale/grow (s5i5, sc25, cn04 stacked parts, su15 fusing); mirror/symmetry (ar25 reflections, m0r0 mirrored twins).
  - **Key/lock:** ls20 (key shape, colour and rotation must match the door).
  - **Colour change / mixing:** ft09 (cycle colours), cd82 (dye), r11l (eat coloured food to match), re86 (colour pads repaint pieces), tn36 (recolour instruction).
  - **Temporal / record-replay / memory:** g50t (ghost twin replays your moves).
  - **Autonomous or adversarial agents:** wa30 (other haulers), tu93 (patrolling or following enemies), ka59 (bombs on fuse from level 5).
  - **Partial observability / scrolling camera:** ls20 final level fog-of-war; bp35 (the viewport shows "about 10 rows of a shaft 32 to 50 rows tall").
  - **Rule induction / symbolic mapping:** tr87 (translate using a rune dictionary), sc25 (sigil → spell), lf52 (peg solitaire jump rule).
- "Environments centered on a single mechanic that scaled in size or difficulty are treated as an anti-pattern." "Difficulty … is intended to arise from the composition of reasoning demands acquired over the course of play" — [ARC-AGI-3 paper](https://arxiv.org/html/2603.24621v1).
- The private set covers "a broader and more diverse set of mechanics with limited overlap with the mechanics found in the public environments" — [ARC-AGI-3 paper](https://arxiv.org/html/2603.24621v1).
- Frontier-model failure modes seen in replays: "True local effect, false world model"; "Wrong level of abstraction from training data" (mapping to Tetris, Frogger, Sokoban, Breakout); "Solved the level, didn't learn the game" — [ARC Prize analysis blog](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis).
- Two other framings from the docs and DataCamp: "agent based (moving around a single object on screen)" versus "orchestration based (viewing and manipulating multiple objects at once)" — [DataCamp](https://www.datacamp.com/blog/arc-agi-3); ls20 = "Agent reasoning", ft09 = "Elementary Logic", vc33 = "Orchestration" — [docs](https://docs.arcprize.org/available-games).

### Inferences
- The reusable structure in the public games is the **interaction grammar**, more than the specific families:
  1. Identify the controllable object(s), which may need click-selection.
  2. Identify a visible target configuration.
  3. Find each action's effect, including hidden multi-frame effects such as sliding until blocked.
  4. Watch a budget bar.
  5. Expect a new mechanic every 1–3 levels.

  This grammar is set by ARCEngine conventions (see Q6), so it is likely to carry over to private games even where specific families do not.
- The "Wrong level of abstraction" failure (for example, calling wa30 "Sokoban") cuts both ways. Priors like "push", "select", "toggle" and "match the reference" are useful, but an agent that locks onto a known game's rules fails when the private game breaks them (for instance, wa30's other haulers).

### Gaps
- There is no official taxonomy of mechanics for the semi-private or private sets. By design, the mix of families in the private set is unknown.

## Q3. What the paper and docs say about designing the private and semi-private games

### Takeaway
There are 135 environments: 25 public, 55 semi-private and 55 fully private. Rules for all of them:
- Core-Knowledge priors only; no language or cultural symbols.
- Novel relative to existing video games *and* to the other ARC-AGI-3 environments.
- At least 6 levels, with level 1 as an easy tutorial.
- Solvable by humans within a ~20-minute session.
- Independently solved by at least 2 humans before inclusion.

The private set is explicitly harder and out-of-distribution relative to the public set.

### Cited Findings
- Split: public demo 25 / semi-private 55 / fully private 55 — [ARC-AGI-3 paper](https://arxiv.org/html/2603.24621v1). "135 environments across public, semi-private, and fully private sets" — [DataCamp](https://www.datacamp.com/blog/arc-agi-3).
- "Each environment is required to be novel both with respect to preexisting video games, and with respect to the previously created set of environments." — [paper](https://arxiv.org/html/2603.24621v1)
- Core Knowledge priors: "objectness, basic geometry/topology, basic physics, and agentness", avoiding "language or cultural symbols" — [paper](https://arxiv.org/html/2603.24621v1).
- "Environments are developed with a level-based structure, with at least six levels per environment." "The first level in an environment functions as a tutorial level and is intentionally easy." — [paper](https://arxiv.org/html/2603.24621v1)
- Solvable "within a bounded play session of approximately 20 minutes (but most environments can be solved in only a few minutes)". Human testing used a soft limit of 20 minutes and a hard cutoff of 30 minutes per environment. There were 486 unique participants across 414 candidate environments, 427.9 hours of play, and a median attempt of 7.4 minutes. "Only environments that could be fully solved by at least two human participants (independently) were considered" — [paper](https://arxiv.org/html/2603.24621v1).
- Public vs private: the public set is "intentionally easier for both humans and AI". The private set is "significantly more difficult for both humans and AI, and … intentionally out-of-distribution relative to the public set". "The public set does not comprehensively represent the mechanics found in the private set" — [paper](https://arxiv.org/html/2603.24621v1).
- Action space: "Five key actions, plus an Undo action" and "one action to select (e.g. click on) a cell from the 64x64 grid" — [paper](https://arxiv.org/html/2603.24621v1). The docs say ACTION1–4 are typically movement, ACTION5 is "a game-specific interaction", ACTION6 is the complex (x,y) action, and ACTION7 is "undo" — [docs: games](https://docs.arcprize.org/games).
- Lessons from the preview: "Some preview games were too friendly to random search … A few game designs could be brute-forced without reasoning", which prompted making "future games more resistant to brute force". The planned changes included undo buttons and clearer indicators of which actions are available — [30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings).
- Design tenets on the product page: "Easy for humans to pick up quickly", "No pre-loaded knowledge or hidden prompts", "Clear goals + meaningful feedback", "Novelty that prevents brute-force memorization" — [arcprize.org/arc-agi/3](https://arcprize.org/arc-agi/3).
- Environments are "handcrafted by a team of human game designers" — [ARC-AGI toolkit / docs search snippet](https://github.com/arcprize/arc-agi).
- On Kaggle, the public leaderboard is computed on about 50% of the hidden test data and final standings on the other 50% — [Kaggle leaderboard page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard). The competition has no internet access during evaluation, and code must be open-sourced to win prizes — [competition page](https://arcprize.org/competitions/2026/arc-agi-3).

### Inferences
- The private games were built to punish exactly what makes public games easy: random search, repeated single actions and memorized mechanics. A local evaluation that rewards those strategies will overestimate private performance.
- Because every private game must clear the "≥2 independent humans solved it" and "~20 min" bars, private games still share the public set's legibility: visible targets, a small set of actions, and tutorial first levels. Priors about how games are presented (UI, budget bars, targets) will carry over better than priors about mechanics.

### Gaps
- It is not public how the 55 private games split between the Kaggle public and private leaderboards, or whether each Kaggle split uses all 55 or a subset. The "~50%" figure is Kaggle's standard text.
- No per-game detail about semi-private or private games is published, which is intentional.

## Q4. Common UI conventions: step counters, energy bars, levels, lives, GAME_OVER

### Takeaway
Nearly every public game draws a **per-level action budget** as a bar or row of pips on the frame edge. Running it out calls `self.lose()`, and the state becomes `GAME_OVER`. A few games add lives (ls20: 3 per level) or instant-death hazards (tu93 enemies, bp35 spikes). `RESET` after any action restarts the current level. A level is completed through `next_level()`, which increments `levels_completed`, and the game state becomes `WIN` after the last level. Nothing in the frame states the goal. Progress signals are the level counter and, in some games, a visible target panel.

### Cited Findings
- Engine states: `NOT_PLAYED`, `NOT_FINISHED`, `WIN`, `GAME_OVER` ("The run ended without a win") — [docs: games](https://docs.arcprize.org/games); the same enum is in `arcengine/enums.py` ([arcengine on PyPI](https://pypi.org/project/arcengine/)).
- Engine fixed rules (arcengine `OVERVIEW.md`):
  - 64×64 output with 16 colours.
  - At most 6 actions plus RESET.
  - Turn-based: "no time advances without input".
  - "Each input generates 1–N frames", since animations are returned as multiple frames.
  - `next_level()` increments the score and calls `win()` after the last level.
  - RESET "restart[s] the current level … if any actions have been taken; otherwise, perform[s] a full game reset".

  Source: [arcengine package](https://pypi.org/project/arcengine/) and [ARCEngine repo](https://github.com/arcprize/ARCEngine).
- Lose conditions found in the game source files, which I read directly from `/api/games/{id}/source`:
  - Step-counter lose (`if self._action_count >= limit: self.lose()`, or a `current_steps` counter hitting 0): cd82, cn04, m0r0 (hard-coded 150), r11l, sc25, ka59, re86, s5i5, su15, sp80, ft09 and lp85 (via a budget object).
  - Lives or other conditions:
    - ls20 decrements a counter and loses at 0.
    - r11l also loses after 5 failures of some kind.
    - bp35 loses on "landed_on_spike".
    - ka59 loses when a sprite collides with a specific enemy position.
    - su15 loses if all blocks are gone.
    - sp80 has an ACTION5 usage condition (`if self.lyremoheq >= 4: self.lose()`).
- Community write-ups (checked against source) give these budget details ([arc-explainer](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games)):
  - ls20: a "hidden step meter of 42 units, drawn as a bar of pips at the bottom-left". Levels 2/3/5/7 drain 2 units per move. "Three lives PER LEVEL, shown as three red pips at the bottom-right." The third loss ends the run, and RESET refills lives and the meter.
  - re86: budget of 100/100/200/200/250/200/300/400 across levels, shown as "the purple bar along the bottom row".
  - s5i5: 50/150/200/100/150/150/200/200 clicks, shown as a bar along the bottom row.
  - sb26: 64 energy; undo is free but does not refund energy.
  - sk48: 196 energy per level; clicks and undo are free.
  - sc25: 50/25/50/35/65/60.
  - tr87: 128 actions (256 on level 6).
  - su15: 32 or 48 clicks.
  - sp80: a green bar.
  - g50t: a timer bar tied to action count.
  - tu93: a pink step bar; "one hit ends the attempt, there are no lives".
  - dc22: a bad press costs 20 steps.
  - vc33, wa30: per-level budgets, lose on exhaustion.
- The paper shows the ls20 level-1 state graph with "three repeating states – an artifact of the three-life mechanic" — [paper](https://arxiv.org/html/2603.24621v1).
- Ben Goertzel's description of ls20: "Every move costs one unit of health, so wandering around exploring is not free" — [Goertzel substack](https://bengoertzel.substack.com/p/playing-around-with-the-arc-agi-3).
- The only feedback signal is level completion. When the step limit expires, the environment resets (per a search summary of [Graph-Based Exploration, arXiv 2512.24156](https://arxiv.org/html/2512.24156v1)).
- In competition-style harnesses, "If GAME_OVER is reached, the benchmark-provided RESET action can be used to restart the current level attempt … RESET … counts against the action budget. The agent cannot restart the whole game … cannot return to previously completed levels." In local mode, "sending RESET before taking any action on a level can restart the whole game from the first level" — [Executable World Models, arXiv 2605.05138](https://arxiv.org/abs/2605.05138).
- Engine code: `handle_reset()` performs `level_reset()` whenever the env var `ONLY_RESET_LEVELS == "true"` (and the game is not WON). Otherwise it performs `full_reset()` when `_action_count == 0` — arcengine 0.9.3 `base_game.py` ([arcengine](https://pypi.org/project/arcengine/)).
- ACTION7 is implemented as undo in the source of ar25 (pops a state stack), sk48, su15, sb26 and lf52 (`STORES_UNDO = True`), and as a distinct action in bp35. In sb26 and sk48, undo does not refund energy, per arc-explainer.

### Inferences
- A general agent should:
  - Detect the budget bar: a contiguous strip on the frame edge that shrinks by a constant amount per action.
  - Use it to estimate the remaining action budget and when a GAME_OVER is coming.
  - Detect lives: small pips that drop after a budget exhaustion.
  - Mask the budget bar and other HUD elements out of its state hashing, because they change on every action and would otherwise make every state look new.
- Budgets are typically about 1.5–4× the human baseline. For example, re86's level-1 budget is 100 against a baseline of 26, and s5i5's is 50 against 20. Budgets therefore allow some exploration but not blind search in later levels.
- RESET is double-edged. It refills budget and lives (ls20), but every RESET counts as an action. In local/NORMAL mode, a RESET with zero actions taken on a level sends you back to level 1. Set `ONLY_RESET_LEVELS=true` (or use COMPETITION mode) locally to avoid this non-competition behaviour.

### Gaps
- There is no official document listing the budget bar and lives as required conventions for private games. The evidence comes from the 25 public games' source, and private games may differ.
- I did not confirm whether the "5× human baseline per level" hard cutoff mentioned in the paper is enforced in the Kaggle harness. I did not find it in `arc_agi 0.9.9` `scorecard.py`'s per-level scoring code.

## Q5. Can the engine be used to create synthetic games? Are there community game sets?

### Takeaway
Yes. `arcengine` (MIT-licensed, `pip install arcengine`, Python ≥3.12) is the same engine the official games subclass, and it is designed for writing new games. Community sets already exist, the largest being `theredbluepill/arc-interactive` with 249 games, a solvability checker and offline runners. `arc-agi-dsl` and `arc-agi-core` are **not** ARC-AGI-3 game tools: they are ARC-AGI-1/2 static-grid utilities.

### Cited Findings
- To write a game with arcengine, you subclass `ARCBaseGame`, implement `step()`, build `Level([Sprite(...)])`, and call `perform_action(ActionInput(id=GameAction.ACTION1))`. Constructor: `__init__(game_id, levels, camera=None, debug=False, win_score=1, available_actions=[1,2,3,4,5,6], seed=0)`. Helpers include `try_move`, `next_level`, `win`, `lose`, and `level_reset`/`full_reset`. The engine also provides:
  - Sprites with scaling, 90° rotation, layers and collision modes (`NOT_BLOCKED`, `BOUNDING_BOX`, `PIXEL_PERFECT`).
  - Interaction modes (`TANGIBLE`, `INTANGIBLE`, `INVISIBLE`, `REMOVED`).
  - A Camera with auto-upscaling to 64×64 and letterboxing.
  - `RenderableUserDisplay` and `ToggleableUserDisplay` for HUDs.

  Source: arcengine 0.9.3 README ([PyPI arcengine](https://pypi.org/project/arcengine/)); licence "MIT … Copyright (c) 2026 ARC Prize Foundation".
- The ARCEngine repo ships example games: "Simple Maze", "Merge", "Complex Maze" (demonstrates `ToggleableUserDisplay`) and "Merge/Detach" (custom `RenderableUserDisplay`) — [ARCEngine OVERVIEW examples](https://github.com/arcprize/ARCEngine/blob/main/examples/simple_maze.py).
- The `arc-agi` toolkit's OFFLINE mode scans an `environment_files/{game_id}/{version}/` directory containing `metadata.json` (`game_id`, `title`, `tags`, `baseline_actions`, `class_name`) and `{class_name}.py`. You can therefore drop synthetic games in beside the official ones and score them with the same scorecard code — arc_agi 0.9.9 `base.py` (`_scan_for_environments`, `_download_game`) ([PyPI arc-agi](https://pypi.org/project/arc-agi/)).
- Community sets:
  - arc-interactive: "249 interactive games", built on `ARCBaseGame` with the same `environment_files/{game_id}/v1/` + `metadata.json` layout. Actions use the standard mapping (WASD+Space → ACTION1–5, click → ACTION6, undo/restart → ACTION7). It supports offline, online and competition modes, and includes `devtools/verify_level_solvability.py` and tutorial stems ez01–ez04. Genres include Memory Match, Sokoban, Bridge Builder, Rule Switcher, Mirror Maker, Sapper and Slide Puzzle. It is MIT-licensed and positioned as a "massive testing ground" for generalization — [theredbluepill/arc-interactive](https://github.com/theredbluepill/arc-interactive).
  - The arc-explainer repo also contains write-ups for non-public games "as66" and "slipperySeven" — [arc-explainer directory listing](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games). Their provenance is unclear.
- `arc-agi-dsl 0.0.3` contains only `transformation`/`rewrite` utilities and D8 symmetry primitives (rotate_90/180/270, flips) and depends on `arc-agi-core`. `arc-agi-core 0.1.14` ("Research tool-kit for tackling ARC") provides `Grid`, `Pair`, `Task` and `Dataset` loaders for ARC1/ARC2 training and evaluation. Neither package has any ARC-AGI-3 game or engine code. Both come from inspecting the wheels ([PyPI arc-agi-dsl](https://pypi.org/project/arc-agi-dsl/), [PyPI arc-agi-core](https://pypi.org/project/arc-agi-core/)).
- Kaggle top teams use the local simulator as an "offline oracle", for example the `tgaer` PR "use the local simulator as an offline oracle" ([charleneleong-ai/tgaer PR #31](https://github.com/charleneleong-ai/tgaer/pull/31)).

### Inferences
- A held-out "private-like" local benchmark is feasible. Build or collect 20–50 ARCEngine games that the agent has never seen, from arc-interactive or self-authored with an LLM + `verify_level_solvability.py`. Give them ≥6 levels, a budget bar, visible targets and mechanics that do not appear in the 25 public games. Set `baseline_actions` from a BFS-optimal solution times a human-like slack factor (about 1.3–2×), or from a few human plays.
- Such a set is a better proxy for the private leaderboard than the public 25. It must be kept strictly held out: never used for prompt tuning or for designing heuristics.
- Community games are likely of lower quality and easier than ARC's hand-crafted, human-calibrated ones, and are often LLM-written. Filter out games solvable by random or single-action-repeat baselines, in the same way AERA tested the public games.

### Gaps
- I did not verify the quality, difficulty distribution or human-solvability of the arc-interactive games, and there is no human-baseline data for them.
- I found no official ARC Prize "game-authoring kit" docs page beyond the arcengine README and examples. I found no officially endorsed community game set.

## Q6. What the shipped public-game source code reveals about game structure

### Takeaway
Each public game is a single Python file of 777 to 41,463 lines. It defines one `ARCBaseGame` subclass, a list of 6–10 `Level` objects built from pixel-array `Sprite`s, HUD classes (`RenderableUserDisplay`), and a custom `step()` that ends in `next_level()` or `lose()`. All identifiers (sprite names, tags, methods, variables) are **obfuscated into random strings**, so the source gives exact dynamics but no semantic hints. The games are deterministic, so local runs are reproducible.

### Cited Findings (from direct inspection of `/api/games/{id}/source`, all 25 files downloaded)
- Line counts: cd82 777, sp80 868, m0r0 924, sk48 982, tr87 1,121, sb26 1,146, cn04 1,182, wa30 1,254, tu93 1,272, ar25 1,847, r11l 1,849, ls20 2,060, vc33 2,124, re86 2,158, su15 2,172, s5i5 2,247, ft09 2,520, tn36 2,647, sc25 2,750, g50t 2,855, bp35 4,565, lf52 5,872, dc22 10,892, lp85 21,451, ka59 41,463. The largest files are mostly embedded sprite pixel arrays.
- Every file carries an "MIT License … Copyright (c) 2026 ARC Prize Foundation" header. Most files lay out their levels with `# Level 1 … # Level N` comments (22 of the 25 files use them). Per the API, all 25 games have ≥6 levels: 9 games have 6 levels, 5 have 7, 6 have 8, 4 have 9 and 1 (lf52) has 10, for 183 levels in total.
- Structure:
  - `class Xxxx(ARCBaseGame)` (the class name is the first 4 characters of the game ID, capitalized).
  - Module constants `BACKGROUND_COLOR` / `PADDING_COLOR`.
  - `available_actions` lists: ft09 `[6]`; ls20 `[1,2,3,4]`; g50t `[1,2,3,4,5]`; dc22 `[1,2,3,4,6]`; sb26 `[5,6,7]`; su15 `[6,7]`; ar25 `[1..7]`; bp35 `[3,4,6,7]`; lf52 `[1,2,3,4,6]+[7]`.
  - Custom camera subclasses in s5i5, tu93 and wa30, used for scrolling or viewports.
  - Clickable sprites carry a literal `"sys_click"` tag, which the games query via `get_sprite_at(x, y, "sys_click")`. Other tags are obfuscated, for example `"0006lxjtqggkmi"` in ar25 and `"bsT"` in ft09.
- Randomness: only tr87 (`random.Random(seed_per_level)`, deterministic) and one `np.random.shuffle` helper in lf52 use randomness. The rest are deterministic given the action sequence.
- Scoring code in `arc_agi 0.9.9 scorecard.py` ([PyPI arc-agi](https://pypi.org/project/arc-agi/)):
  - Per-level score = `min((baseline/actions)^2 * 100, 115)`.
  - Environment score = the weighted average of per-level scores with weight = level index, then capped at `(sum of weights of levels with score>0)/(total weights) * 100`.
  - `EnvironmentScoreList.score` returns `max(run.score for run in self.runs)`, although its docstring says "average".
- Baseline definition: the ARC-AGI-3 paper defines the human baseline as "the second-best human by number of actions used", with a per-level cap of 1.0 and a 5× hard cutoff ([paper](https://arxiv.org/html/2603.24621v1)). The later human-dataset blog says the baseline "moves from 2nd-best player to median player per level" and the "per-level score cap increases from 100% to 115%" ([ARC Prize human dataset blog](https://arcprize.org/blog/arc-agi-3-human-dataset)). The 115 cap matches the shipped code.

### Inferences
- The source is fully readable, and the games are deterministic. Two consequences:
  1. BFS/A* over the true simulator can compute optimal action counts per level. This allows exact "oracle" analysis of how efficient an agent is relative to optimal, not just relative to humans.
  2. Any agent that reads the source or the simulator at test time is invalid for the private set, where source is not available. Local evaluations must use the environment only through the frame/action API, just as the hidden games do.
- The obfuscation shows ARC Prize anticipates source-level leakage, and semantic names will not be available.
- The per-level score is squared. Taking 2× the human baseline yields only 25 points, and 3× yields about 11. Efficiency on the late, heavily weighted levels dominates the score, so local metrics should report RHAE with this exact formula, not raw levels solved.
- Because of the `max()` over runs, **putting several runs of the same game into one local scorecard inflates the score** to best-of-N. Use one scorecard per run, or average manually.

### Gaps
- I did not de-obfuscate the full mechanics of each game myself. The mechanic column in Q1 relies on arc-explainer, which says it verified its claims against these source files.
- I could not confirm whether the Kaggle competition server runs `arcengine 0.9.3` / `arc_agi 0.9.9` or a patched version.

## Q7. Evaluation pitfalls and how many runs are needed

### Takeaway
Public-game scores are a weak, and possibly misleading, proxy for the hidden leaderboard:
- The public games are easier and in-distribution.
- Several are reachable by trivial strategies or a library bug.
- Frontier harnesses score 93–100% on them while the same class of systems scores in the low single digits on hidden games.
- Kaggle competitors report that local public checks did not track their leaderboard scores.

Run-to-run variance is large: game-level RHAE can swing from 0% to 60%, and total scores vary by ±0.4–0.5 points on the leaderboard scale. Comparisons therefore need many seeds (≥10–20 runs per arm) and paired, per-game analysis.

### Cited Findings
**Trivial solvability of the public set (AERA).**
- The AERA paper ([arXiv 2605.25931](https://arxiv.org/html/2605.25931)) states that "every one [of the 25 public games] is reachable through non-intelligent strategies". Its breakdown:
  - 10 games in a single blind step: FT09, CN04, M0R0, LF52, BP35 via ACTION6, plus R11L, VC33, LP85, TN36, S5I5.
  - 5 after one probing action: SB26, CD82, AR25, SK48, DC22.
  - 1 by repeated ACTION1: SP80.
  - 1 by diverse exploration: SU15.
  - 8 by a single repeated action with a budget of 50–200: TU93, RE86, TR87, KA59, LS20, SC25, G50T, WA30.
- The same paper reports "a library-level null-coordinate vulnerability" in which ACTION6 with x=None, y=None produced WIN in 18 of 25 games. The authors call this "not a legitimate solve", and note it has not been confirmed on the Kaggle server.
- AERA's own legitimate agent scored RHAE 0.2116 on the 25 games (4 solved) with Qwen2.5-0.5B. Random and no-explore baselines scored 0.0000. Over 8 runs, the mean was 0.164 ± 0.059 (95% CI [0.115, 0.213]), and FT09 was solved in 8/8 runs.
- Caveat: the abstract does not define "reachable" ([abs page](https://arxiv.org/abs/2605.25931)). The claims conflict with the source-verified mechanics and budgets. For example, a single click cannot legitimately satisfy all of ft09's markers when its level-1 baseline is 43 clicks, and ls20 requires key transformations under a 42-unit meter with 3 lives. So "reachable/solved" probably means reaching a first level-completion or WIN signal in a particular (possibly buggy) library version, not a full legitimate clear. This should be treated as evidence of weak discrimination, not as literal full solves.

**Public scores are saturated and not predictive.**
- Scores on the public set:
  - Twin: mean 93.3, 23/25 games cleared ([arXiv 2608.14490](https://arxiv.org/html/2608.14490)).
  - Agno: 100% with GPT-5.6 in "warm" mode, reusing manuals from previous plays. The authors note "The runs scoring 100% are warm runs … ARC-AGI-3's primary basis for evaluation is its private sets, which are harder, out-of-distribution … Nobody has beaten ARC-AGI-3." Warm runs scored 100.00 versus 94.81 ([Agno](https://www.agno.com/articles/arc-agi-arcade)).
  - Retrodict claims "99.86% mean RHAE, all 25 games solved" ([ryanbbrown/Retrodict](https://github.com/ryanbbrown/Retrodict), search snippet only).
  - Schema claims "~99% on ARC-AGI-3 Public" ([schema-harness](https://schema-harness.github.io/)).
- Scores on the semi-private set: GPT-5.5 0.43% and Opus 4.7 0.18% ([ARC Prize analysis](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis)).
- The docs and third parties stress that the public set "should not be used as a measure of progress", and that ARC released a replay harness scoring 100% on every public environment to make that point (per a search-result summary of the [ARC Prize 2026 docs](https://docs.arcprize.org/arc-prize-2026)). I did not see this text directly.
- "forge" was the 3rd-place Milestone-1 entry by Md Boktiar Mahbub Murad: Gemma-4-31B, reflection memory, a generator plus an arbiter. Its "top-scoring run … used a profile that turns off all of the extra machinery" ([ARC Prize Milestone 1](https://arcprize.org/blog/arc-prize-2026-milestone-1)). A search summary of the Kaggle discussion says the author "mentioned that local public-game checks weren't a reliable leaderboard proxy" ([Kaggle discussion 725002](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/725002)); I could not open the Kaggle page to read the text itself.
- Concrete mismatches between local and leaderboard scores:
  - One team's "matched 25-game local run scored 5.265" but its Kaggle submission scored "2.37 on the public leaderboard", clearing "31 of 183 levels" ([anandsingh8687 repo](https://github.com/anandsingh8687/arc-prize-2026-arc-agi-3-agent)).
  - Another (Duck-based) team reported local results of about 0.80 per game against a public leaderboard of about 2.7–3.6 ([jvilladuque90 repo](https://github.com/jvilladuque90/arc-prize-2026-arc-agi-3)).
  - So the direction of the mismatch is not consistent.

**Variance across runs.**
- Tufa Labs "The Duck" won Milestone 1: an agent that writes code, running Qwen 3.6 27B FP8 locally with a Python REPL ([Milestone 1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)). Its harness README describes an example run of "25 official games × 20 passes" ([Tufalabs/duck-harness](https://github.com/Tufalabs/duck-harness)). I could **not** find the specific "±0.45" figure in accessible sources. It is likely in the Tufa Kaggle write-up or blog, which I could not access.
- The same code resubmitted gave Kaggle scores {1.17, 1.03, 0.76, 0.96}: mean 0.98, range 0.41. A public kernel re-sampled at 3.55 → 2.69 and 3.54 ([jvilladuque90 repo](https://github.com/jvilladuque90/arc-prize-2026-arc-agi-3)).
- The Executable World Models paper shows the same harness scoring:
  - ft09: 100.00% RHAE with GPT-5.4 versus 57.80% with GPT-5.5.
  - wa30: 49.77% versus 9.11%.
  - cn04 across playthroughs: 62.15% and 0.01%.
  - g50t across playthroughs: 21.43% and 34.03%.

  The paper also warns that interrupted-run exclusion "could introduce a selection bias" ([arXiv 2605.05138](https://arxiv.org/abs/2605.05138)).
- The tgaer variance PR used 5 seeds × 25 games. Suite sd was about 0.03 (mean about 0.156). A change that looked like +0.20 in a single rollout was actually −0.004, "INSIDE NOISE". The author found that "effective n is well below the seed count" because the tie-breaks produced few distinct trajectories. A related search summary says "single runs can swing ±3 levels on seed luck alone" ([charleneleong-ai/tgaer PR #32](https://github.com/charleneleong-ai/tgaer/pull/32)).

**Harness pitfalls (engine or toolkit level).**
- A RESET with zero actions taken restarts the whole game in local mode unless `ONLY_RESET_LEVELS=true` ([arcengine base_game.py](https://pypi.org/project/arcengine/); [arXiv 2605.05138](https://arxiv.org/abs/2605.05138)).
- Local scorecards take the `max` over runs of the same game ([arc_agi scorecard.py](https://pypi.org/project/arc-agi/)).
- The ACTION6 null-coordinate WIN bug ([AERA](https://arxiv.org/html/2605.25931)).
- The OFFLINE/COMPETITION operation modes are selected by env var, and COMPETITION takes precedence ([arc_agi base.py](https://pypi.org/project/arc-agi/)).

### Inferences
- **How many runs?** For a two-arm comparison of mean total score with per-run SD σ, detecting a difference Δ at α=0.05 (two-sided) with 80% power needs about n ≈ 15.7·σ²/Δ² runs per arm, unpaired.
  - Using the Kaggle-scale spread seen above (range 0.41 over 4 runs implies σ ≈ 0.2), or the reported ±0.45 if that is 1 SD:
    - σ=0.2, Δ=0.2: about 16 runs per arm.
    - σ=0.45, Δ=0.3: about 35 runs per arm.
    - σ=0.45, Δ=0.45: about 16 runs per arm.
  - On the RHAE scale, AERA's σ=0.059 means about 16 runs per arm to detect Δ=0.06, or about 4 runs for Δ=0.12.
  - Duck's 20 passes per game give a standard error of σ/√20 ≈ 0.22σ, enough to resolve differences of about 0.6σ.
  - Pairing (the same games and seeds in both arms) and per-game paired differences cut the required n further. With few seeds, report per-game solve frequencies, not a single level count.
- **Recommended local setup:**
  1. Run in competition-equivalent mode (`OPERATION_MODE=competition` semantics, `ONLY_RESET_LEVELS=true`, no source or simulator access, and ACTION6 coordinates always validated).
  2. Score with the exact shipped RHAE formula, per run, with no best-of-N.
  3. Evaluate on the public 25 only as a smoke test, preferably ignoring the levels that trivial baselines clear.
  4. Keep a separate held-out set of novel ARCEngine games (community or self-authored, filtered against random and repeat-action baselines) as the primary development metric.
  5. Use ≥10–20 seeds per arm and paired tests.
  6. Always also run trivial baselines (random, repeat-each-action, click-every-sys-click-object) and subtract their score. A change that helps the trivial-exploitable games but not the held-out set is overfitting.
- Because the public games are deterministic, run-to-run variance comes entirely from the agent (LLM sampling, tie-breaks, timeouts and interruptions). Fixing agent seeds and temperature locally gives spuriously low variance. The Kaggle environment adds timing and hardware nondeterminism, so local variance estimates should use genuinely diverse seeds.

### Gaps
- I could not access the Duck write-up with its "20 runs per game, ±0.45" statistic, or forge's Kaggle discussion text. Both are cited above only via the harness README and search-engine summaries.
- There is no published correlation coefficient between public-set scores and private or semi-private scores across many submissions. The evidence is anecdotal: individual teams' mismatches plus the official design statements.
- It is unclear whether the AERA null-coordinate bug and the local RESET→full-reset behaviour exist on the Kaggle scoring server. AERA explicitly did not confirm this.
- The claim that AERA's v31 "achieves RHAE=0.30 on the full 55-game private evaluation" comes from its abstract. I could not confirm it against the Kaggle leaderboard.
