# ARC-AGI-3 game mechanics, design principles and human-baseline structure: how much could a hand-built mechanics library cover?

Notes compiled 2026-10-02. Source tiers, used throughout:
- **[Official]** ARC Prize technical report, docs, blog.
- **[Code]** The public game source (`arcengine` Python, downloadable through the ARC-AGI toolkit) and its `metadata.json`.
- **[Community]** The arc-explainer per-game write-ups. They were written largely by Claude agents, cite game source line by line, and are marked "corrected" several times. Treat them as high-quality secondary sources, not ground truth.
- **[Paper]** arXiv preprints.
- Anything marked "Inference" is my own reasoning.

---

## Q1. Design principles, engine, action/observation space, levels, human baselines, scoring (RHAE)

### Takeaway
- **What a game is.** Each ARC-AGI-3 game is a hand-made Python environment.
  - The agent sees a 64x64 grid in 16 colours and has at most 7 actions plus RESET.
  - There are at least 6 levels, and the first one is a tutorial.
  - Games are restricted to core-knowledge priors and must combine multiple mechanics.
  - Each game must be novel against existing video games and against the other ARC-AGI-3 games.
- **How it is scored (RHAE).**
  - Level score = min(1.15, (human/AI actions)²).
  - Each game's score is a level-index-weighted average, capped by the share of levels completed.
  - The human baseline is the (upper-)median first-time human per level, from about 10 testers per game.

### Cited Findings

**Design goals and environment format**
- ARC-AGI-3 tests four components: Exploration, Modeling, Goal-Setting, and Planning & Execution. "The agent is never told the objective nor provided instructions. It must autonomously infer the mechanics of each new environment, including the win conditions." — [ARC-AGI-3 Technical Report, §2.1](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- Environments are turn-based and a level ends at a win condition (terminal frame). "The environment's state does not change asynchronously from the agent's actions." — [Tech Report §2.3](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- **Observation:** a 64x64 grid where each cell is one of 16 colours (a "frame"). Each turn returns one frame or a sequence of frames, and a sequence encodes a non-interactive animation (e.g. an object moving across the screen). — [Tech Report §2.3.1](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
  - The docs add: values 0–15, (0,0) at top-left, (x,y) format, "Maximum 64x64". — [Game Schema docs](https://docs.arcprize.org/game-schema)
  - Game states are NOT_PLAYED, NOT_FINISHED, WIN and GAME_OVER. — [Game Schema docs](https://docs.arcprize.org/game-schema)

**Action space**
- Each environment uses a subset of: five key actions, plus Undo, plus one select/click action on the 64x64 grid. "This small action space ensures that the complexity of the benchmark lies in the logic of the environment, not the difficulty of the controls." — [Tech Report §2.3.2](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)

| Action | What the docs say |
|---|---|
| RESET | Initialises or restarts the game or level |
| ACTION1–4 | "Semantically mapped to" up / down / left / right |
| ACTION5 | Game-specific: "interact, select, rotate, attach/detach, execute, etc." |
| ACTION6 | Click at x,y in the 0–63 range |
| ACTION7 | Undo |

  — [Actions docs](https://docs.arcprize.org/actions)
- `available_actions` comes back in every frame's metadata. For ACTION6, only its availability is given, not which coordinates are active. — [Actions docs](https://docs.arcprize.org/actions)
- In a GAME_OVER state only RESET is valid; any other action returns HTTP 400. — [Actions docs](https://docs.arcprize.org/actions)
- Tool calls and reasoning are not counted as actions. Every turn that submits a command is counted. — [Methodology docs](https://docs.arcprize.org/methodology)

**Engine and game file structure**
- Games run on a custom in-house Python engine. Unity was tried first and dropped as "too heavy and too slow". The engine targets at least 1,000 FPS. — [Tech Report §3.3](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- A game file contains:
  - a sprite dictionary: named rectangular pixel arrays with tags, `visible` and `collidable` flags;
  - a list of `Level` objects, each holding sprite placements and `grid_size`;
  - a `Camera` with background and letterbox colours, which scales a smaller logical grid up to 64x64;
  - a class extending `ARCBaseGame`, with `step()`, `on_set_level()`, a win check, `next_level()` and `complete_action()`.

  Sprites support `.clone()`, `.color_remap()`, `.set_scale()` and `.set_position()`. The game ID is 4 characters plus a version. — [Create ARC-AGI-3 Environment docs](https://docs.arcprize.org/add_game)
- `metadata.json` may include `baseline_actions`, described in the docs as an "Array of average action counts per level", plus `tags`. — [add_game docs](https://docs.arcprize.org/add_game)
  - [Code] The local metadata for the 25 public games holds per-level baseline arrays. Examples: ls20 `[22,123,73,84,96,192,186]`, vc33 `[7,18,44,61,131,34,152]`, dc22 `[59,102,67,98,324,578]`, wa30 `[71,119,183,98,368,68,79,442,415]`.
  - [Code] The tags are `keyboard`, `click` or `keyboard_click`. These come from the public game files downloaded via the [ARC-AGI toolkit](https://github.com/arcprize/ARC-AGI).

**Design principles (Tech Report §3.4)** — [Tech Report §3.4](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- Core-knowledge priors only:
  - Objectness: entities persist, move, collide and can be occluded.
  - Basic geometry and topology: symmetry, rotation, inside/outside, connectedness, holes.
  - Basic physics: gravity, momentum, bouncing.
  - Agentness: some objects act with intent.
  - No language or cultural symbols: no numbers, letters, recognisable clip-art "like flowers or keys", or conventions like "green meaning go".
- Novelty: each environment must be novel against existing video games and against the environments already built. The practical test asks whether one program could solve two environments while being at least 50% shorter than the two separate solution programs concatenated. If yes, the two are "likely insufficiently distinct".
- Solvable by humans in about 20 minutes, and most take only a few minutes.
- "Difficulty through composition": "Later levels are therefore expected to require the accumulation and integration of concepts learned earlier in the environment."
- The first level is an intentionally easy tutorial, and random agents may sometimes stumble into success there.
- "Multiple mechanics: Each environment contains multiple mechanics. Environments centered on a single mechanic that scaled in size or difficulty are treated as an anti-pattern."
- At least six levels per environment.
- The 4-character IDs hide informal names "to avoid sharing semantic information about the environment's goal or mechanics."

**Validation pipeline**
- A random agent runs 50k steps and must beat no level by accident.
- A 1M-step random run must leave non-tutorial levels unbeaten.
- A further 1M-step fuzz run checks for crashes, plus replays of known recordings.
- A state graph is built per level (hash-merged states, cycle detection). The acceptance threshold is that a random policy wins a level no more than 1 in 10,000 times. ls20 level 1 has P(win) of exactly 1 in 355, and its graph shows "three repeating states – an artifact of the three-life mechanic".

  — [Tech Report §3.5](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)

**Production process**
- A studio of about 10–17 named developers built the games.
- Pipeline: Specification (concept reviewed before build) → Internal prototype and team test → External human test → Done, then sorted into one of the sets.
- Throughput was best when one developer had 3–4 environments in flight at once.
- "Idea generation for new environments, rather than implementation, was often the most challenging part".
- Surge AI helped brainstorm early concepts.

  — [Tech Report §3.2, §3.4, Acknowledgments](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)

**Human testing**
- Each environment was tried by 10 members of the public. It was kept only if at least 2 people independently solved every level on first sight; "many" were solved by 6 or more.
- Sessions lasted 90 minutes, with a soft 20-minute limit and a hard 30-minute cutoff per environment.
- Testers could RESET the current level but could not revisit completed levels.
- Totals: 486 participants, 414 candidate environments, 2,893 attempts, 427.9 hours. The median attempt took 7.4 minutes (8.1 for successful ones).

  — [Tech Report §5](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- The human-dataset blog gives slightly different numbers:
  - 458 participants;
  - 342 human replays released across the 25 public games;
  - 145 solves from 342 plays (about 42%);
  - r11l was solved by 10 of 10 testers, bp35 and sp80 by only 2 of 12–14 each.

  It also says the baseline moved "from 2nd-best player to median player per level." — [ARC Prize blog: Measuring Human Performance](https://arcprize.org/blog/arc-agi-3-human-dataset). The 486-vs-458 discrepancy is unresolved.

**Scoring (RHAE)**
- Level score S = min(1.15, (h/a)²), where h is the "upper-median best human action count" for that level.
  - With an even number of finishers, the upper of the two middle ones is used: 3rd of 4, and also 3rd of 5.
- Game score: E = min(Σ_{l≤k} w_l / Σ w_l, Σ w_l·S_l / Σ w_l), with weight w_l = l. Uncompleted levels score 0, and levels must be completed in order.
- Total score: the mean of the game scores.

  — [Tech Report §4.1–4.2](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf); [Methodology docs](https://docs.arcprize.org/methodology)
- Worked examples: 10 human actions vs 100 AI actions gives 1%. Completing 4 of 5 levels caps the game at 10/15 = 66.7%. vc33 level 6 needs about 10x the actions of level 1 (50 vs fewer than 5), which is why scoring is per level. — [Tech Report §4.2](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- Three human reference points are tracked: optimal playthrough, best first-run, and the baseline (upper-median first-run). The gap between optimal and first-run "captures the amount of actions that need to be expended for initial exploration and mechanics learning." — [Tech Report §5.3.2](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- The official leaderboard stops an agent after 5x the human median action count per level. It uses no harness and the same minimal system prompt for every model. Public-set scores are never reported officially. — [Tech Report §4.3](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- The same harness gives bimodal results by game: Opus 4.6 scored 0.0% without a harness and 97.1% with the Duke harness on a TR87 variant, but 0.0% either way on BP35. — [Tech Report §4.3.1](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)

### Inferences
- **Squared efficiency makes wasted actions very expensive.**
  - Taking twice the human action count earns 25%; taking 3x earns about 11%.
  - Late levels carry most of the weight: in an 8-level game, level 8 alone is 8/36 = 22%.
  - So a "mechanics DSL + planner" that wins by identifying the mechanic fast and then planning near-optimally is exactly what the metric rewards.
  - Exhaustive probing to fit a model is penalised quadratically, unless probes are few and highly informative.
- **The human baseline already includes human exploration cost**, since it is a first-run median and not the optimum. An agent that recognises a known primitive within a few actions and then plans optimally can plausibly score at or above 1.0 on levels where the primitive applies.
- **The formula text says "n = 5" levels and gives 5-level examples, yet every public game has 6–10 levels.** The weighting and cap generalise; the "5" looks like a leftover from an earlier draft.

### Gaps
- The baseline arrays in public `metadata.json` are described in the docs as "average action counts" but in the report as "upper-median". I could not verify whether the shipped arrays are the scoring baselines.
- Per-level human baselines for private games are not public.
- Whether the Kaggle competition uses the same 5x action cap as the official leaderboard: not confirmed in the sources I read.

---

## Q2. What mechanics do the 25 public games use?

### Takeaway
- The 25 public games are well documented by source-cited community write-ups, and the game code itself is public.
- They mostly use a common set of primitives:
  - a selectable avatar or piece moved on a grid;
  - push, slide or "fling until blocked";
  - click-to-toggle or cycle;
  - mirror-linked or replayed agents;
  - colour/shape/rotation transforms by "stepping on tiles";
  - pattern- or template-matching win checks;
  - budget bars (nearly universal);
  - hidden or latent counters, timers and chasing agents.
- Each game layers 3–8 new pieces across levels.
- A few games carry idiosyncratic sub-systems that a generic library would not foresee:
  - tn36: 6-bit opcode switches;
  - tr87: a rune translation dictionary with a "repair" mode;
  - sb26: tile sequences with nested ring "subroutine calls";
  - sp80: fluid stream routing;
  - su15: vacuum-merge with size chains and chasing creatures.

### Cited Findings

**Per-game summary.** Rows are compiled from the arc-explainer per-game files ([github.com/82deutschmark/arc-explainer/shared/arc3Games/](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games)), each of which cites `<game>.py` line numbers. The controls column gives the available actions from the game code; the "levels" column is the length of `baseline_actions` in [Code] metadata. "Lk" means the piece first appears on level k.

| ID (informal name) | Controls / levels | Core mechanics (documented) | What later levels add |
|---|---|---|---|
| **ls20** (Locksmith) | arrows only / 7 | Avatar walks a maze. Tiles change the key's rotation, colour or shape. Walk into a door while the key matches the door's picture. Hidden 42-unit step meter, three lives per level. | L2 step-refill rings. L3 colour tile and launch pads (slide until wall). L4 shape tile (6 shapes). L5 tiles moving on hidden paths. L6 two doors. L7 fog-of-war (radius 20 px). |
| **ft09** (Functional Tiles) | click only / 6 | Click a 3x3 tile to cycle its colour. Markers state constraints: centre colour = target, white border = neighbour must equal target, grey = must differ. Click budget. | L2 multiple markers. L4 3-colour cycle. L5 tiles that also cycle their neighbours (Lights-Out style). L6 every tile is coupled to the one above. |
| **vc33** (Volume Control) | click only / 7 | Pumps move liquid between tanks across walls. Riders sit on the liquid surface; win when every rider is level with its colour stripe. Gravity direction changes per level. | L2 three tanks. L3 three riders. L4 gates open when both sides are level and swap riders. L6 bars limit pumping. |
| **ar25** (Axis Reflectors) | arrows, ACTION5 cycle, click select, undo / 8 | Move pieces and axis-aligned mirrors. Live reflections must cover every yellow target cell. Step budget. | L2 the mirror moves. L3 horizontal mirror and two pieces. L5 two mirrors at once (up to 3 reflections). |
| **bp35** (Buoyant Pontoons) | L/R, click, undo / 9 | Sideways step, then slide in the "pull" direction until blocked (gravity). Click green blocks to remove them. Scrolling camera: the exit is usually off-screen. | Rising hazard mass. L2 spikes. L3 click toggles a block solid/ghost. L4 red block flips gravity. L7 128-action bar. L8 clicking purple breaks it but spreads it to neighbours (bridge building). |
| **cd82** (Compass Dye) | arrows move a bucket around 8 stations, ACTION5 throw, click colour swatch / 6 | Throw paint over half or a triangle of a 10x10 canvas. Later throws overwrite earlier ones (order matters). Match a reference on 80 of 100 cells. | L2/L3 more colours. L3 a 4x3 "dab" nozzle. |
| **cn04** (Coded Notches) | arrows slide, ACTION5 rotate, click pick / 6 | Slide and rotate parts so every red mark sits on a mark of the same hidden kind. Two mark kinds look identical (hidden attribute). | L3 parts not held are drawn grey (memory). L5 parts that grow/shrink through a size cycle. L6 two parts sharing one grow direction. |
| **dc22** (Deck Control) | arrows, click panel buttons / 6 | Walk to the goal. Panel buttons rotate bars, toggle floor solid/non-solid, extend bridges, slide slabs. A press that leaves you with no floor costs 20 steps. | L2 hidden buttons revealed by tokens. L3 teleport pads. L4 cyclic 8-press and 6-press mechanisms. L5/L6 a claw that grabs and carries floor. L6 buttons that appear only while you stand on a tile; a pad recolourer. |
| **g50t** (Ghost Twin) | arrows, ACTION5 rewind / 7 | Your moves are recorded. Rewind spawns a ghost that replays them. Ghosts press plates that hold gates open. Timer bar. | L3 toggle plates. L4 plate-triggered pad swap. L6 a patrol on a hidden route (kills on contact). L7 several pads plus a patrol. |
| **ka59** (Kick Away) | click select, arrows / 7 | Drive a box 3 cells per press. Hitting a piece knocks it about 15 cells (chain push). Purple zones block only the driven box. Win when every frame holds a piece of its size. | L2 several shapes. L3 large blocks movable only by knocking. L5 bombs on fuses that blast pieces. |
| **lf52** (Leapfrog) | click, arrows, undo / 10 | Peg solitaire (hop over a same-colour peg, which removes it). Win at one peg left. | L2 rail carts carry pegs between rooms. L3 several carts move together, scrolling view. L4 purple blocks you can hop but not remove. L6 an unremovable red peg. L8 blue pegs that don't count toward the goal. |
| **lp85** (Loop and Pull) | click only / 8 | Buttons rotate loops of slots forward or back. Get the yellow squares into yellow targets. | L2 crossing loops (shared slots). L3 orange pair. L4 duplicated buttons. L5 nested loops. L6–L8 one button drives several loops. |
| **m0r0** (Mirror Rendezvous) | arrows, ACTION5 (no-op), click / 6 | Two twins: vertical moves are the same for both, horizontal moves are mirrored. Desync them on walls until they meet. | L2 traps reset positions. L3 clicking selects pushable blocks. L5 gates held open by buttons a twin stands on. |
| **r11l** (Reaching Lurch) | click only / 6 | Click to place an arm. The body jumps to the mean position of its arms. Get each body onto its outline. | L2 two blobs and hazard zones (strike counter, 5 strikes = loss). L4 multi-colour blobs and decoy outlines. L5 white bodies "eat" colour pellets (order matters) to match outlines. |
| **re86** (Reach Emblems) | arrows, ACTION5 cycle selection / 8 | Slide outline pieces (crosses, X, diamond, line) so each target dot is covered by a piece of the same colour. | L4 colour pads repaint pieces. L6 walls bend crosses and squash squares (permanent deformation). |
| **s5i5** (Sliding Indicator) | click only / 8 | Slider buttons grow or shrink every rod of their colour. Markers ride the rods; get markers onto pins. Collisions cancel the whole click. | L2 chained rods (kinematic tree). L3 passive bars. L4 one button drives many rods. L6 rotate buttons. L8 a pinwheel. |
| **sb26** (Sequence Belt) | click, ACTION5 run, undo / 8 | Place coloured tiles in machine slots. "Run" reads them against a goal colour sequence. | L2 ring tiles jump to another machine (subroutine call). L4 loose rings. L5 the same machine read twice; a ring loop fails the run. L7 nesting 3 deep. L8 two goal rows and a recursive ring. |
| **sc25** (Sigil Caster) | arrows, click 3x3 grid / 6 | Draw a lit pattern on a 3x3 toggle grid to cast a spell: grow/shrink, teleport, or fireball. Reach the exit. | L2 teleport pads and gates only a small wizard fits through. L3 fireball clears blocks via target. L4 pickups that refund 10 budget. L5/L6 size-dependent teleport pads, multiple pads in rotation. |
| **sk48** (Skewer Kebabs) | arrows, click select, undo / 8 | Extend or retract a rod. The tip pushes beads; a stuck bead gets skewered. Bead order must match a reference. | L3 fixed rods. L4 targets on rods you don't control. L5 walls. L6 two rods. L7 a shared bead. L8 restricted rails. |
| **sp80** (Streaming Purple) | click select, arrows, ACTION5 pour / 6 | Position bars, then one pour: liquid falls and splits at bar ends. Fill every cup without touching a spill line. | L2 upside-down levels. L3 three spouts. L4 a bar that is itself a spout. L5 L-pieces turn the stream 90° and sideways streams appear. L6 several L types and a standing bar. |
| **su15** (Sucking Up) | click, undo / 9 | Click to vacuum everything within 8 cells to a point. Same-size blocks fuse one size up (9-size chain). Hold an exact count in circles. | Fouls with an escalating penalty. L4 creatures chase blocks and shrink them on contact. L5 creatures fuse (3-tier chain). L6 targets include creatures. L9 a fast creature. |
| **tn36** (Toggle Navigator) | click only / 7 | Columns of binary switches encode opcodes (sum of 1/2/4/8/16/32). Run the program to move, rotate, scale or recolour a token onto a target. | L2 demo panel plays preset programs (learn opcodes by observation). L3 walls (jumps skip them). L6 save points. L7 beam emitters after instruction 3. |
| **tr87** (Toggle Runes) | arrows only / 6 | Translate a phrase into another glyph alphabet using an on-screen dictionary of glyph pairs. Up/down cycles a glyph; tilt is irrelevant. | L2 1→many entries. L3 many→1. L4 two-step translation. L5 "repair mode": fix the dictionary instead. L6 branching. |
| **tu93** (Trail Unwind) | arrows only / 9 | Move a token pad-to-pad along wires to the exit, with a step budget. | L2 static biting enemies (directional). L4 patrollers. L5 a decoy enemy that looks like you. L7 sleepers that wake and follow your path two steps behind. |
| **wa30** (Warehouse Associates) | arrows, ACTION5 grab/release / 9 | Sokoban with grab-to-pull. Every crate must end in a bay and not be held. | L2 helper agent auto-hauls crates to bays. L3 barrier lines only crates can cross. L4 several helpers. L6 a thief hauls crates out. L8 helpers and thieves together. |

**Other documented facts**
- as66 ("Always Sliding": a sliding block, enemies, colour-matching exit) was one of the 2025 preview games and was later withdrawn from the live 25. — [arc-explainer as66.ts](https://github.com/82deutschmark/arc-explainer/blob/main/shared/arc3Games/as66.ts)
- Budget bars:
  - Every one of the 25 write-ups lists a visible on-screen step, energy, timer or click bar that ends the run when empty.
  - ls20 also has 3 lives per level that RESET restores.
  - r11l has an invisible 5-strike counter.
  - su15 has an escalating foul penalty.

  — arc-explainer per-game files, budget entries (e.g. [ls20.ts](https://github.com/82deutschmark/arc-explainer/blob/main/shared/arc3Games/ls20.ts), [r11l.ts](https://github.com/82deutschmark/arc-explainer/blob/main/shared/arc3Games/r11l.ts))
- Undo (ACTION7) exists only in some games: ar25, bp35, lf52, sb26, sk48 and su15 per the write-ups, and sb26, sk48 and su15 per [Code] `available_actions`.
  - In several games undo does not refund budget: ar25, sk48, sb26, su15. In bp35 undo itself fills a cell of the bar.
  - lf52's undo does refund the move.

  — arc-explainer [sb26.ts](https://github.com/82deutschmark/arc-explainer/blob/main/shared/arc3Games/sb26.ts), [lf52.ts](https://github.com/82deutschmark/arc-explainer/blob/main/shared/arc3Games/lf52.ts), [bp35.ts](https://github.com/82deutschmark/arc-explainer/blob/main/shared/arc3Games/bp35.ts)
- Size of the public game code [Code]:
  - most games are 800–2,900 lines;
  - outliers: dc22 about 10.9k, ka59 about 41k, lp85 about 21k, lf52 about 5.9k, bp35 about 4.6k (largely level and sprite data).

  Source: public game files from the [ARC-AGI toolkit](https://github.com/arcprize/ARC-AGI) (`environment_files/<id>/<ver>/<id>.py`).
- Control scheme by game [Code `available_actions`/tags]:
  - Click only: ft09, lp85, r11l, s5i5, tn36, vc33 (su15 is click plus undo).
  - Keyboard only: ls20, tr87, tu93 (arrows); g50t, re86, wa30 (arrows plus ACTION5).
  - The other 12 games mix keyboard and click.
- Docs' informal one-word labels for the three demo games: ls20 "Agent reasoning", ft09 "Elementary Logic", vc33 "Orchestration". — [Available Games docs](https://docs.arcprize.org/available-games)
- The public-set validity critique (AERA paper):
  - The claim: "every one [of the 25 games] is reachable through non-intelligent strategies: 10 in a single blind step, 5 after one probing action ... 8 via single repeated actions with sufficient budget", plus a "library-level null-coordinate vulnerability" that "bypasses 18 games in 1 step".
  - Caution: this almost certainly refers to clearing level 1 or getting a nonzero score, not to solving whole games. It conflicts with the official validator's 1-in-10,000 random-win threshold for non-tutorial levels.

  — [arXiv 2605.25931](https://arxiv.org/abs/2605.25931); [Tech Report §3.5](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)

### Inferences
- **Recurring primitive families across the public 25.** Counts are my tally from the table above.
  1. Grid avatar movement with wall collision: ls20, tu93, m0r0, g50t, wa30, sc25, dc22, bp35 (8 games).
  2. Selected-piece manipulation (click or cycle to select, arrows to move): ar25, cn04, ka59, re86, sp80, sk48, m0r0 L3, lf52 (8).
  3. Slide until blocked or knock-back: ls20 pads, bp35, ka59, as66 (3–4).
  4. Push and grab chains (Sokoban-like): wa30, ka59, sk48 (3).
  5. Click-cycle or toggle state, including neighbour coupling: ft09, tn36 switches, sc25 grid, dc22 toggling floor (4).
  6. Attribute transform by contact (colour, shape, rotation, size): ls20, re86 pads, r11l pellets, sc25 grow (4).
  7. Linked or derived agents (mirror twin, replay ghost, path follower, helper/thief AI, chasing creature, patrol): m0r0, g50t, tu93, wa30, su15 (5).
  8. Fluid or level physics (pumps, streams, gravity flip): vc33, sp80, bp35 (3).
  9. Kinematic linkages (rod growth/rotation trees, arms→centroid body, loops of slots): s5i5, r11l, lp85, sk48 (4).
  10. Symbolic or program-like systems (opcode switches, translation dictionary, tile-sequence interpreter with calls, spell sigils): tn36, tr87, sb26, sc25 (4).
  11. Merge or arithmetic systems (size-chain fusion, exact counts, peg removal): su15, lf52 (2).
  12. Painting or overwrite order: cd82, r11l L5 (2).
- **Win conditions are mostly declarative pattern checks**:
  - "every target X covered or filled by a Y with matching colour/size/shape";
  - "reach the exit";
  - "sequence or translation equals reference";
  - "exact count".

  That makes them well suited to a small, typed goal-predicate DSL (coverage, matching, reachability, equality to an on-screen reference, count).
- **Even within the public 25, about a third of games have at least one sub-mechanic that is unlike any other game**:
  - tn36: binary opcodes;
  - tr87: dictionary repair;
  - sb26: nested ring calls;
  - su15: escalating fouls and creature fusion;
  - dc22: claw plus conditional buttons;
  - re86: deforming crosses and squashing squares;
  - s5i5: rods that fold back get a half turn.

  A hand-built library written from the public games would cover the core of most public games. It would still miss level-specific twists, which by design arrive on the heavily weighted later levels.

### Gaps
- I did not independently re-read all 25 game sources to verify each community claim. The ls20 claims were cross-checked against the code layout but not line by line.
- Per-level counts of distinct mechanics per game (a "mechanic density" metric) are not published officially.

---

## Q3. How different is the private set (110 games), and how are games authored?

### Takeaway
- **The split.** There are 135 environments in total: 25 public, 55 semi-private and 55 fully private. 414 candidate environments were human-tested.
- **The official position on the private sets.** They are "significantly more difficult", "intentionally out-of-distribution relative to the public set", and have "limited overlap with the mechanics found in the public environments". The public set "does not comprehensively represent the mechanics found in the private set."
- **What we don't know.** No private game mechanics have been published.

### Cited Findings
- Dataset sizes: Public Demo 25, Semi-Private 55 (used to test frontier models behind an API), Fully Private 55 (used for the competition; "only given to a very limited number of partners"). — [Tech Report Table 1](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf); 135 in total per [ARC Prize launch blog](https://arcprize.org/blog/arc-agi-3-launch)
- The public set is "intentionally easier for both humans and AI, with a stronger emphasis on clarity and fun." It "does not comprehensively represent the mechanics found in the private set, reducing the risk of overfitting or targeted optimization." — [Tech Report §3.6](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- The private set is "significantly more difficult for both humans and AI ... intentionally out-of-distribution relative to the public set. They cover a broader and more diverse set of mechanics with limited overlap with the mechanics found in the public environments ... involving deeper compositional reasoning." — [Tech Report §3.6](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- The public:private ratio is inverted relative to ARC-AGI-2 (which was roughly 10:1 public-heavy). "The public set shifts from a training resource to a demonstration interface". — [Tech Report §3.6](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- The novelty rule applies against all previously created environments: the 50%-shorter joint-program test. — [Tech Report §3.4](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- The Tech Report names "domain-specific overfitting" as including "a harness that contains ARC-AGI-3 specific strategies", and says such scores are excluded from the official leaderboard. Harness scores belong on the self-reported community leaderboard. — [Tech Report §4.3](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- In the 2025 preview, 3 public and 3 private games were used; winners relied on informed exploration or search (StochasticGoose 12.58%, Blind Squirrel 6.71%). — [Tech Report §6.1](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
  - Per arc-explainer, the 3 "private" preview games were sp80, as66 and lp85. sp80 and lp85 are now in the public 25. — [arc-explainer ARC3_Games.md](https://github.com/82deutschmark/arc-explainer/blob/main/docs/reference/arc3/ARC3_Games.md)
- From the Milestone #1 writeups, one author noted that "local public-game checks weren't a reliable leaderboard proxy". Tufa Labs found that "hand-crafted tools actually hurt the model; letting it improvise worked better." — [ARC Prize 2026 Milestone 1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- Public-vs-private evidence from papers:
  - The AERA paper reports RHAE 0.2116 on the public 25 with Qwen2.5-0.5B and "RHAE=0.30 on the full 55-game private evaluation". The units are ambiguous: it could be 0.30% or 0.30 as a fraction.
  - Rodionov's executable world model (58.12% public with GPT-5.5) states "Performance on the private validation set ... remains to be tested."

  — [arXiv 2605.25931](https://arxiv.org/abs/2605.25931); [arXiv 2605.05138](https://arxiv.org/abs/2605.05138)
- Frontier models on the semi-private set:
  - at launch: Opus 4.6 0.50%, Gemini 3.1 Pro 0.40%, GPT-5.4 0.20%, Grok 4.20 0.10% — [Tech Report Table 2](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf);
  - later: GPT-5.5 0.43%, Opus 4.7 0.18% — [ARC Prize blog: GPT-5.5 & Opus 4.7 analysis](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis).
- Kaggle competition context (from our own prior notes, sourced from the public leaderboard):
  - top score 52.51 (Tufa Labs);
  - the public leaderboard uses about 50% of the hidden test set.

  — [leaders_public_intel_2026-10-02.md](../leaders_public_intel_2026-10-02.md). This is secondary; verify against the Kaggle leaderboard.

### Inferences
- **The private set is built to be out-of-distribution for a mechanics library written from the public games.** Combine three facts:
  - private mechanics are "limited overlap" by design;
  - the novelty test penalises any pair of games solvable by a shared program at less than half the combined length;
  - each game must have multiple mechanics.

  So a library written from the 25 public games should expect to directly cover only a minority of private-game mechanics.
- **What should still transfer is the vocabulary of low-level physics and object primitives**, because the core-knowledge restriction is shared: movement, collision, push, slide-until-blocked, gravity, toggle, select, attribute change on contact, follow or mirror agents, budget bars, coverage/match goals. The specific compositions, and the "twist" rules on later levels, mostly would not.
- **Private-set scores show both that general strategies transfer and that a gap remains.** The Kaggle top score (about 52 on a hidden split of the private games) is far above frontier-API semi-private scores (under 1%) but well below the public-set scores of world-model systems (78–93%).
  - This is consistent with a substantial public→private drop for public-tuned systems, but there is no controlled comparison.

### Gaps
- No public description of any private game's mechanics was found. ARC Prize keeps them confidential.
- No published controlled comparison of the same system on public vs private sets, apart from the AERA claim with ambiguous units.
- The share of private games using keyboard vs click vs mixed controls is unknown.

---

## Q4. Public analyses that categorise mechanics or report which mechanic types agents fail on

### Takeaway
- **Analyses converge on goal inference as the bottleneck, not dynamics.**
  - Systems that learn executable code world models reach 79–92% accuracy on dynamics. Their remaining failures are goals that cannot be inferred and hidden or temporal state (hidden countdowns, history-dependent rules).
  - Frontier LLMs without such scaffolding fail by mapping games onto familiar genres, and by locking in a theory from level 1 that later levels contradict.

### Cited Findings

**Twin (test-time digital twin)** — [arXiv 2608.14490](https://arxiv.org/abs/2608.14490) / [HTML](https://arxiv.org/html/2608.14490)
- A coding agent writes `step(grid, action)` and `goal_reached(grid)` in Python and must replay every past transition before it acts.
- Results:
  - clears 179/183 public levels (97.8%);
  - more efficient than humans on 158/179;
  - infers the goal before any reward on 156 levels (87.2%);
  - overall score 93.3, versus 7.8 for the bare model and 61.1 for an off-the-shelf harness.
- "Building a usable world model is simpler than anticipated, whereas the harder problem is inferring the right goal."
- Named failures:
  - sc25 (score 32.7): "sinks 647 of its 701 actions" on level 4 against "a hidden countdown"; goal never found.
  - sp80 (score 81.1): sixth level's "goal resists" despite 92.3% dynamics accuracy.
- Out of scope by the authors' own account: "Truly latent state ... stays out of scope" and "Mechanics driven by long temporal context, history the grid does not show".
- bp35's scrolling camera was handled by "buying the hidden map one probe per place".
- Goal search was costly on ka59 (1,291 extra actions over five levels) and tn36 (1.5x human actions).
- Caveat: the per-game level counts in my WebFetch extraction of Twin's table were garbled. Only the aggregates and named failures are cited. The aggregate 183 levels does match the sum of the [Code] baseline arrays: 8+9+6+6+6+6+7+7+10+8+7+6+6+8+8+8+6+8+6+9+7+6+9+7+9 = 183.

**OPINE-World** — [arXiv 2607.01531](https://arxiv.org/abs/2607.01531)
- An object-centric programmatic world model built by CEGIS (counterexample-guided synthesis), with exploration steered by "ontology error".
- Solves 20 of 25 games and scores 78.4 RHAE "without per-game training".

**Executable world models (Rodionov)** — [arXiv 2605.05138](https://arxiv.org/abs/2605.05138)
- A verifier-driven Python world model with no game-specific code.
- GPT-5.5: 15/25 games fully solved, mean RHAE 58.12%. GPT-5.4: 8/25 and 41.29%.
- Hardest games: dc22 0/6 (GPT-5.5), bp35 partial (3/9 or 5/9), lf52 (1/10 or 6/10).
- Suspected cause: "premature commitment to an incorrect or overly specific world model."

**ARC Prize analysis of GPT-5.5 and Opus 4.7** — [arcprize.org blog](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis). Three failure modes:
1. "True local effect, false world model":
   - cd82: knew rotate and pour but never formed the plan "orient bucket, then dip".
   - cn04: found rotate-then-place but optimised whole-shape overlap.
2. "Wrong level of abstraction from training data": mapping games onto Tetris, Frogger, Sokoban, Powder Toy, Flood-It, MiniGrid, Breakout and others.
   - GPT-5.5 on cd82 anchored on sand/Flood-It.
   - On ls20 it applied Breakout logic.
3. "Solved the level, didn't learn the game":
   - ka59: Opus solved L1 in 37 actions with a wrong "click teleports" theory and never recovered at L2.
   - ar25: drifted into hallucinated "punching holes" rules.

**Tufa Labs on the MLST podcast** (via our prior notes): "wrong-goal loops", where agents lock onto a wrong goal. — [leaders_public_intel_2026-10-02.md](../leaders_public_intel_2026-10-02.md) (secondary)

**Hardest public games for humans** — [ARC Prize human dataset blog](https://arcprize.org/blog/arc-agi-3-human-dataset)
- bp35 and sp80 were solved by 2 of 12–14 testers.
- r11l was solved by 10 of 10.
- In cd82, 2 of 11 testers stalled at level 2 ("steep onboarding curve").

**arc-explainer difficulty labels** (community, subjective):
- AI "very-hard": ls20, bp35, g50t, lf52, sk48, tn36, wa30.
- AI "easy": ar25, ft09, lp85, re86, tu93, vc33.

  — [arc-explainer shared/arc3Games/*.ts](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games)

### Inferences
- **Mechanic types that are repeatedly hard for strong agents**:
  - hidden or latent state: hidden countdowns, step meters with variable drain, invisible strike counters, two kinds of marks that look identical, patrols on undrawn routes;
  - history- or temporal-dependent agents: replay ghosts, path-followers two steps behind;
  - off-screen state behind scrolling cameras;
  - goals that are ambiguous until late: sc25, sp80 L6, tn36, ka59.
- **A pure "mechanics DSL" mainly helps with dynamics, which is the part the best systems already solve.** The bottleneck these analyses identify is goal inference and latent state.
- **So the DSL's value depends on what else it carries.** It needs goal-predicate templates and latent-variable templates (counters, timers, hidden attributes, recorded action history) to help where agents actually fail.

### Gaps
- No public, systematic per-mechanic failure statistics (e.g. failure rate by mechanic class across many agents) were found.
- The Twin and OPINE per-game tables were not fully extracted. Read the PDFs directly for per-level detail.

---

## Q5. What this implies for a "mechanics DSL + verifier + planner" agent

### Takeaway
- **Public-set evidence strongly supports a verifier-plus-planner architecture**: code world models replayed against all past transitions reach 78–93 RHAE on the public set.
- **A *hand-built fixed library* of mechanic primitives is at odds with ARC-AGI-3's explicit design**: novelty test, out-of-distribution private set, multiple mechanics per game, harness-specific overfitting excluded from the official board.
- **The defensible version is an open-ended library**: low-level, core-knowledge primitives used as priors and building blocks inside a synthesised world model, with a fallback to free-form code. A closed catalogue of game-level mechanics is not defensible.

### Cited Findings
- The two most successful published public-set systems write free-form Python world models with verification and do not rely on a fixed primitive set:
  - Twin: "nothing in it is hard-coded to ARC-AGI-3";
  - Rodionov: "no hand-coded game-specific logic";
  - OPINE: object-centric typing learned online.

  — [arXiv 2608.14490](https://arxiv.org/html/2608.14490); [arXiv 2605.05138](https://arxiv.org/abs/2605.05138); [arXiv 2607.01531](https://arxiv.org/abs/2607.01531)
- The 2020 Kaggle ARC-AGI-1 winner used "brute-force program search over a library of hand-crafted primitives" and reached about 20%. That approach dominated for three years, before test-time-training and LRM approaches overtook it. — [Tech Report §1.2](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- Harnesses built for ls20, ft09 and vc33 showed "extreme bimodal performance" on unseen public games: 97.1% vs 0.0% (TR87 variant vs BP35). — [Tech Report §4.3.1](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
- Tufa Labs: "hand-crafted tools actually hurt the model; letting it improvise worked better." — [Milestone 1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- The engine's own abstractions are sprites (pixel arrays with tags and collidable/visible flags), levels (sprite placements plus grid size), a camera (scaling, letterbox, scrolling) and a `step()` function that is arbitrary Python. — [add_game docs](https://docs.arcprize.org/add_game)
- The validation pipeline already builds hash-merged state graphs and random-policy win bounds. It is evidence that ARC designers reason about games as explicit state graphs. — [Tech Report §3.5](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)

### Inferences

**Coverage estimate (inference, rough).**
- *Public 25:* a library of about 30–50 primitives drawn from the 12 families in Q2 could express the core level-1–3 dynamics of perhaps 18–22 of the 25 games. Full all-level dynamics would be covered for fewer, maybe 10–15, because of game-unique twists: opcodes, translation repair, nested calls, deformation, fouls, kinematic exceptions.
- *Private 110:* given the design rules, the direct game-level coverage of a public-derived library is plausibly well under half. Low-level primitives ("object moves 1 cell; blocked by collidable; slides until blocked; attribute changes on overlap; counter decrements; agent follows rule R") should keep high reuse.

**Where the library should sit in the architecture.**
- *Matching the engine:* the agent's representation should be sprites (connected objects with colour, shape and bounding box) plus a `step()` code region. In practice:
  - perception into objects;
  - a DSL of per-object update rules;
  - an escape hatch to arbitrary Python for game-unique logic.

  That way the library speeds up hypothesis proposal but does not limit what can be expressed.
- *Must-have non-dynamics templates,* driven by where agents fail:
  - goal predicates: coverage/match-to-reference, reach-exit, all-targets-filled, sequence-equals-reference, exact-count;
  - latent variables: step/energy budget with variable drain, lives, strike counters, timers, a recorded action history for ghost/follower agents, hidden object attributes;
  - camera/scrolling for partial observability.
- *Verifier:* replay every observed transition (Twin, Rodionov). Budget and HUD bars give free supervision for latent counters, because every game in the public 25 shows a bar.
- *Planner:* RHAE squares efficiency and weights late levels most, so planning must be near-optimal (BFS/A* over the model) once the model is verified. Exploration actions should be chosen for information gain.
  - Note for exploration: free actions exist in several games (clicks on nothing in ft09, lp85, sb26, sc25 cost nothing in-game), but every submitted action still counts toward RHAE. In-game "free" does not mean scoring-free.
- *Level-to-level transfer:* the design principle that "later levels require accumulation and integration of concepts learned earlier" means a verified model from level k should be carried to level k+1 and extended. A new piece type per level is the norm (see the Lk entries in Q2).

**Main risks to flag for the report writer.**
- Over-fitting the library to the public 25 runs against an explicit design goal of the private set.
- The bottleneck is goal inference and latent state, not dynamics vocabulary.
- An agent built around a hand-made mechanics library may be classed as "domain-specific overfitting" for the official leaderboard. This does not affect Kaggle eligibility.

### Gaps
- No published ablation measures how much a fixed primitive library helps on private games versus free-form code synthesis.
- No public statistics on how often private games reuse low-level physics primitives (gravity, push, slide) versus introducing new ones.
