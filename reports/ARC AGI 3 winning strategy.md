# Model Throughput, Not Harness Cleverness, Wins ARC-AGI-3

Winning the ARC Prize 2026 ARC-AGI-3 Kaggle competition now takes roughly **20% or more on 55 hidden games**. Those games are played inside a **9-hour, single RTX PRO 6000 (96 GB), no-internet** notebook run. That is far above the ~1–2% that won Milestone #1. On 2026-09-25 the public leaderboard is led by **Lord Han Solo at 19.45%**, followed by Tufa Labs at 18.81% and Yi-Chia Chen at 18.63%, and nine teams are above 10%. The best open notebook, the Milestone #1 "Duck" harness running Qwen3.8-Flash-Next-NVFP4, sits near **4.5%** ([Kaggle leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard); [Duck Qwen3.8 (Tuned)](https://www.kaggle.com/code/chiakazirim/duck-qwen3-8-tuned)). Every large jump so far followed a stronger base checkpoint or more model decisions per wall-clock minute. In controlled tests, prompt changes moved hidden scores by about 30% at most, and multi-agent or hand-tooled harnesses have not beaten the lean Duck ([discussion 743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060); [ARC Prize Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)). Frontier research systems that write executable world models and check them against logged transitions reach 93–100% on the 25 public games. They do so only with closed models and roughly 100× Kaggle's token budget, and no open-weight result exists ([Twin](https://arxiv.org/abs/2608.14490); [Tycho](https://arxiv.org/abs/2607.28287)). The scoring rule makes depth decisive. **Perfect level-1 clears on every game top out near 3.5%**, so the 15–19% teams must be clearing two or three levels on most hidden games **[Inference]**. The practical path has three stages. First, ship a hardened, throughput-tuned Duck + Flash-Next build with the known cheap fixes before Milestone #2 (Sep 30, 23:59 UTC). Second, spend October testing four things on a held-out suite of synthetic games: retained reasoning, context compaction, lossless logs and fine-tuning on the agent's own wins. Third, lock two robust final submissions by Nov 1, because only one submission per day is allowed and RTX queues have reached 12 hours. The top five have disclosed nothing. The jump from ~4.5% to ~19% is therefore both the central unknown and the main opportunity.

*How to read this report.* Facts carry inline citations to host pages, shipped code, papers, or participant posts. Kaggle-discussion claims are community evidence unless attributed to a host; the hosts cited include Greg Kamradt, María Cruz and other Kaggle or ARC Prize staff. Anything marked **[Inference]** is my own reasoning or arithmetic from those sources. Scores are percentages on a 0–100 scale. "Public-25" means the 25 public demo games run locally. "LB" means the Kaggle public leaderboard, which is computed on 55 semi-private games. The final section resolves conflicts between sources. It also corrects figures from an earlier version of this analysis that are now out of date.

## Nine hours, one Blackwell card, 110 hidden games: the rules that bind

### Dates, prizes and eligibility

This is a notebook-only code competition. Its settings fix **540 minutes of runtime for both CPU and GPU notebooks, one submission per day, two final selections, and teams of at most eight**. Identity verification is mandatory ([Kaggle overview](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview)). The daily cap was raised to five by mistake on May 27. Staff restored one per day on June 8 and invalidated the extra submissions ([discussion 705405](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705405)), so the official starter README's "5 official submissions per day" is stale ([ARC-AGI-3-Kaggle-Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter)). Every submission plays **all 110 hidden games**. The 55 semi-private games drive the public leaderboard and the 55 fully private games drive the final ranking. Private scores are computed at the time of the run, and there is no rerun at the end of the competition ([Kaggle data page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/data); [discussion 684852](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/684852); [host in discussion 729985](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/729985)). The public demo games were made easier than the semi-private set by design ([host in discussion 703990](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990)).

| Event | Date (23:59 UTC unless noted) | What it means for you |
|---|---|---|
| Milestone #2 | Sep 30, 2026 | Ranked on the public LB. The notebook must be public under an open-source license by the deadline ([prizes page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/prizes); [discussion 713634](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713634)) |
| Entry and team-merger deadline | Oct 26, 2026. The settings JSON puts the new-entrant cutoff at **11:59 AM** UTC | Accept the rules and finish team merges before noon UTC ([Kaggle overview](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview)) |
| Notebook publishing disabled | Oct 26, 2026 | Make public anything that must be public (dependencies, a Paper Track notebook) before this date **[Inference]** |
| Final submission deadline | Nov 2, 2026 | Select two final submissions ([timeline](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/timeline)) |
| Paper Track deadline | Nov 9 (Kaggle) vs Nov 8 (arcprize.org) | Plan for Nov 8 ([Kaggle Paper Track](https://www.kaggle.com/competitions/arc-prize-2026-paper-track); [arcprize.org](https://arcprize.org/competitions/2026)) |
| Winners announced | Dec 4, 2026 | ([timeline](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/timeline)) |

The legally binding Kaggle rules (§1.5) set the final prizes at **$40K / $15K / $10K / $5K / $5K** and each milestone at **$25K / $7.5K / $5K**. A $700K bonus is split among up to five teams that reach 100% ([Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)). arcprize.org lists the milestones as $25K / $10K / $2.5K instead ([arcprize.org ARC-AGI-3](https://arcprize.org/competitions/2026/arc-agi-3)); this report follows the rules text.

Milestone prizes require the notebook to be public under an open-source license by 23:59 UTC on the milestone date ([discussion 713634](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713634)). Participants read the ranking as the public leaderboard, with the prize moving down to the best-ranked open-sourced entry ([discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801)).

Final-prize winners must license their code under **CC-BY 4.0**. They must also use an open-source system, model and weights as defined by the OSI, with an exception for pretrained models whose licenses are incompatible ([Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)). arcprize.org asks for CC0 or MIT-0 on self-authored code ([arcprize.org/competitions/2026](https://arcprize.org/competitions/2026)). Dual-licensing your own code under CC-BY 4.0 and MIT-0 satisfies both **[Inference]**. Winners must also deliver their training and inference code and do an interview with a technical writer provided by the host ([Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)).

The Paper Track is a separate Kaggle competition. It asks for a writeup of at most 1,500 words plus an attached public notebook. Prizes are $50K / $20K / $5K, plus a $375K pool for papers scoring above 4.5/5, and the linked code does not need to score well ([Kaggle Paper Track](https://www.kaggle.com/competitions/arc-prize-2026-paper-track); [arcprize.org paper track](https://arcprize.org/competitions/2026/paper)). Ties on the leaderboard go to the earlier entry ([Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)).

### Hardware and runtime envelope

The accelerator that matters is Kaggle's "RTX 6000". It is an **NVIDIA RTX PRO 6000 Blackwell with 96 GB** on GCP machine type `g4-standard-48`. Only notebooks attached to this competition can use it, and internet is always off ([Kaggle overview](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview); [discussion 697720](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697720)). Third-party catalogs list the machine at 48 vCPUs and 180 GB of RAM ([Spare Cores](https://sparecores.com/server/gcp/g4-standard-48)). The only container limits staff have relayed are a 30 GB memory cgroup, a 4-core allocation, a 20 GB quota on `/kaggle/working` and 10 MB of container logs. Those were stated for CPU notebooks, so the RAM and cores of RTX sessions remain unconfirmed ([discussion 724841](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/724841)).

The hardware history is short:
- H100s appeared on Apr 28 and disappeared in a stockout on May 7.
- The runtime rose from 6 to 9 hours on May 7.
- A hidden 6-hour cap stayed in place until May 19 ([discussion 697720](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697720); [discussion 699208](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699208)).

The Kaggle image runs Python 3.11 while `arc-agi` needs 3.12, so installs must come from the wheels the competition provides ([discussion 699517](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699517)). vLLM needs Blackwell-aware builds on this card; one participant hit `ptxas fatal: Value 'sm_120a' is not defined` ([discussion 703506](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703506)). RTX queues backed up on Aug 14, Sep 8 and Sep 21–22, and waits reached 8–12 hours before capacity was restored ([discussion 742148](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742148); [discussion 735147](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735147)).

### How a scored run actually executes

A scored submission runs twice.
- **Phase A ("Save & Run All")** executes without the hidden games and must write a dummy `submission.parquet`.
- **Phase B** reruns the notebook with `KAGGLE_IS_COMPETITION_RERUN` set. It starts a gateway sidecar at `http://gateway:8001` that serves the `arc-agi` Flask API in competition mode. The gateway records every action and writes the scored parquet itself ([starter build_notebook.py](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter/blob/main/scripts/build_notebook.py); [docs.arcprize.org](https://docs.arcprize.org/arc-prize-2026)).

The official Phase B pattern:
1. Wait for `/api/games` to respond.
2. Copy the ARC-AGI-3-Agents framework.
3. Write a `.env` with `OPERATION_MODE=online` and `ARC_API_KEY=test-key-123`.
4. Run `main.py`, which opens one scorecard, creates every game and starts **one thread per game, all 110 at once** ([ARC-AGI-3-Agents](https://github.com/arcprize/ARC-AGI-3-Agents)).

Competition mode imposes these rules:
- one scorecard;
- one `make` call per game;
- no scoring of an in-flight scorecard;
- game resets are turned into level resets;
- games never played are created when the scorecard closes and score 0.

([competition-mode docs](https://docs.arcprize.org/toolkit/competition_mode); [arc-agi 0.9.9 source](https://pypi.org/project/arc-agi/0.9.9/))

The toolkit auto-closes a scorecard after 15 idle minutes. That is why the official GPT-OSS template enforces a **14-minute deadline for the first action** and sends an early RESET while vLLM is still loading ([GPT-OSS-120B notebook](https://www.kaggle.com/code/gregkamradt/arc-agi-3-gpt-oss-120b); [scorecard docs](https://docs.arcprize.org/scorecards)). The hosts have not published whether the hidden gateway uses the same idle timer, so load the model before the scorecard opens **[Inference]**.

Staff analyzed 500 failed submissions:
- About a third got stuck with no visible error.
- About 20% were submitted without a GPU.
- The rest were a long tail of missing datasets, CUDA out-of-memory errors, calls to the public API host, and writes to the read-only `/kaggle/input`.

([discussion 727119](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/727119))

### The game API and its traps

Each game is turn-based on a 64×64 grid with colors 0–15. The actions are RESET plus ACTION1–7:
- ACTION1–4 mean up, down, left and right.
- ACTION5 is a game-specific interact.
- ACTION6 is a click at (x, y), each 0–63, with (0, 0) at the top left.
- ACTION7 is undo, in games that support it.

([docs: actions](https://docs.arcprize.org/actions); [arcengine 0.9.3](https://pypi.org/project/arcengine/0.9.3/))

Every action returns one or more frames (animations). With them come:
- `state`: NOT_PLAYED, NOT_FINISHED, WIN or GAME_OVER;
- `levels_completed`;
- `win_levels`;
- `available_actions`, which the host says is constant per game;
- `guid`;
- `full_reset`.

([discussion 702079](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/702079))

Games are seeded and deterministic, except for lf52's transition noise ([discussion 694153](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/694153)). The engine runs at 2,000+ FPS ([changelog](https://docs.arcprize.org/changelog)). There is **no 5× action cap on Kaggle**; compute is the only cap ([host in discussion 713921](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713921)). The traps below cost real points.

| Trap | What actually happens | Mitigation |
|---|---|---|
| RESET at the start of a level, or two RESETs in a row | Locally (NORMAL mode) this is a **full reset back to level 1**. On Kaggle full resets are blocked, but per the server code the ignored RESET still adds one action ([arc-agi 0.9.9 api.py](https://pypi.org/project/arc-agi/0.9.9/); [discussion 692135](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/692135)) | Never RESET when the level's action count is 0. Test locally with `ONLY_RESET_LEVELS=true` or in competition mode |
| Dead clicks | Clicks that change nothing still count. On lp85, 100 no-op ACTION6 clicks counted as exactly 100 actions; the host said "Yes, they match" ([discussion 718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638)) | No-op and dead-signature guards |
| Mid-level RESET and failed attempts | Each RESET costs +1, and every action lands on the current level's count because full resets are impossible ([scorecard.py](https://pypi.org/project/arc-agi/0.9.9/)) | Budget exploration per level |
| GAME_OVER | Only RESET is accepted. Other actions return HTTP 400 and are not counted. RESET restarts the current level ([docs: actions](https://docs.arcprize.org/actions)) | Detect the state and send exactly one RESET |
| In-game soft resets | In some games (e.g., ls20) running out of energy resets the level automatically while actions keep adding up ([discussion 697423](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697423)) | Detect budget bars; treat a reset frame as a failed attempt |
| `MAX_ACTIONS = 80` in the agent base class | The agent silently stops after 81 actions ([discussion 734054](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734054)) | Override it |
| Multi-frame responses | The Duck reads only `frame[-1]`. 13 of the 25 public games return multi-frame responses; sp80 returns 22 frames ([discussion 734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369)) | Give the model compact animation metadata |
| ACTION7 | Present only in some games. Duck forks hit index errors, and models misread it as "jump" ([discussion 742477](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742477)) | Read `available_actions`; label it UNDO |
| Local NORMAL mode | Allows full resets and repeated plays, and the scorecard keeps the **max** over runs ([arc-agi scorecard.py](https://pypi.org/project/arc-agi/0.9.9/)) | Use a competition-mode server with one scorecard per run |
| ACTION6 with null coordinates | A TypeError that the local wrapper reported as WIN in 18 of 25 games; not confirmed on Kaggle ([AERA](https://arxiv.org/abs/2605.25931)) | Validate coordinates; never rely on it |
| Game tags | API tags are wrong in places, e.g. tu93 is tagged keyboard_click but exposes only ACTION1–4 ([ARC API game list](https://three.arcprize.org/api/games)) | Trust `available_actions` |
| HTTP and idle timeouts | The remote wrapper times out each request after 10 s; scorecards close after 15 idle minutes ([arc-agi 0.9.9](https://pypi.org/project/arc-agi/0.9.9/)) | Load models before the scorecard opens; use a watchdog |

## Depth beats frugality: perfect level-1 play tops out near 3.5%

In the shipped scorer, a completed level scores `min(115, 100·(h/a)²)`. Here h is the human baseline and a counts every action spent on that level, including RESETs and failed attempts. An uncompleted level scores 0 ([arc-agi 0.9.9 scorecard.py](https://pypi.org/project/arc-agi/0.9.9/)). The game score is the mean of the level scores weighted by level index (weights 1 to n). It is then **capped at 100 × (weights of completed levels ÷ all weights)**, and the total is the mean across games ([methodology](https://docs.arcprize.org/methodology); [discussion 705022](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705022)).

On Apr 14 two things changed: the baseline became the **upper-median first-time human per level**, replacing the second-best human, and the per-level cap rose from 1.0 to 1.15 ([changelog](https://docs.arcprize.org/changelog); [human-dataset blog](https://arcprize.org/blog/arc-agi-3-human-dataset)). Kaggle's data and evaluation pages still show the old `min(h/a, 1)²` formula. The host confirmed the 1.15 per-level cap and the 100% per-game cap ([Kaggle data](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/data); [discussion 705022](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705022)).

A worked example from the shipped scorer: cd82 has six levels with baselines 55, 8, 41, 21, 23 and 23. Clearing the first four perfectly and stopping scores **47.6**. Taking twice the baseline on all six scores **25.0** ([discussion 728299](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/728299)). In competition mode the API strips `baseline_actions` from the game metadata ([arc-agi 0.9.9](https://pypi.org/project/arc-agi/0.9.9/)).

**[Inference]** The completion cap makes depth the dominant variable. The 25 public games have nine 6-level games, five 7-level, six 8-level, four 9-level and one 10-level, for 183 levels in total ([ARC API game list](https://three.arcprize.org/api/games); [Twin](https://arxiv.org/html/2608.14490)). With that mix, perfect play gives these maximum game scores:

| Levels in game | Public games | Max score, level 1 only | Levels 1–2 | Levels 1–3 |
|---|---|---|---|---|
| 6 | 9 | 4.76 | 14.3 | 28.6 |
| 7 | 5 | 3.57 | 10.7 | 21.4 |
| 8 | 6 | 2.78 | 8.3 | 16.7 |
| 9 | 4 | 2.22 | 6.7 | 13.3 |
| 10 | 1 | 1.82 | 5.5 | 10.9 |
| **Public-mix average** | 25 | **3.5** | **10.6** | **21.1** |

**[Inference]** Two consequences follow, assuming the hidden games have a similar mix of level counts (the mix is not published).
1. An agent that clears only level 1 everywhere, perfectly, scores at most about 3.5%. This matches a participant's observation that below ~3.5 LB "you're mostly not solving any level 2 or up of the hidden games" ([discussion 740812](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740812)).
2. A score of 19.45% needs roughly near-human clears of levels 1–3 on almost every hidden game, or deeper clears on a subset. At twice the human action count, every number in the table shrinks by 4×.

The strategic rules follow from the formula:
- **A clear is all-or-nothing.** A slow clear always beats no clear.
- **Later levels are worth more.** Level 6 of a 6-level game is 28.6% of that game's cap ([discussion 728299](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/728299)).
- **Inefficiency is punished hard.** Twice the human action count gives 25 points per level; three times gives about 11.
- **[Inference] Actions only cost points on levels you eventually clear.** A level that is never completed scores zero however many actions it took, so on a stuck level only compute is scarce. On a level the agent will eventually clear, every probe, dead click and RESET lowers the score.
- **The 1.15 cap** lets beating the human on completed levels offset inefficiency elsewhere, but never beyond the completion cap.
- **Thinking is free in score but not in wall clock.** Every Duck-lineage run ends on its per-game clock, not on an action limit or a win ([discussion 734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369)). Tokens, not actions, are the scarce resource.
- **Unplayed games score zero,** so every game must at least be started.
- **Cracks are stochastic.** One configuration cracked 17 of the 25 public games in at least one run, but only 5–8 in any single run ([discussion 743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)). **[Inference]** Abandoning zero-progress games early therefore trades possible late cracks for time elsewhere.

## Model releases and undisclosed tricks lifted the top from 1.3% to 19.45%

### Standings on 2026-09-25

| # | Team | Public LB | Submissions |
|---|---|---|---|
| 1 | Lord Han Solo (solo) | **19.45** | 73 |
| 2 | Tufa Labs (Milestone #1 winner) | 18.81 | 146 |
| 3 | Yi-Chia Chen (solo) | 18.63 | 11 |
| 4 | Daniel Franzen (solo) | 16.68 | 82 |
| 5 | NVARC3 (CPMP, Darragh, ivan/sorokin, Elad Sarafian, Gal Kaplun, Yeyin Zhu) | 16.07 | 20 |
| 6 | Tong Hui Kang (solo) | 15.02 | 83 |
| 7 | the last dance | 13.70 | 62 |
| 8 | Matija Ludvig & Zhongwei Wang | 11.64 | 84 |
| 9 | Fususu | 10.66 | 90 |
| 10 | Third Intelligence | 8.81 | 56 |
| 14 | mostik.ai (last submitted Sep 6) | 7.51 | 47 |
| 16 | Son Pham & Mark Barney | 7.36 | 59 |
| 31 | "i want to go lab" (Reki, Milestone #1 2nd) | 5.57 | n/a |

Source: [Kaggle leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard) and [arc3.huikang.dev](https://arc3.huikang.dev/leaderboard).

Of 3,320 scored teams, **9 score at least 10, 49 at least 5, and 849 at least 2**. The median is 0.31. Rank 100 sits at 4.32, rank 500 at 3.23 and rank 1,000 at 1.39 ([Kaggle leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard)).

The history of the top score reads like a model-release calendar ([arc3.huikang.dev](https://arc3.huikang.dev/leaderboard)):
- April–May: at most 0.42.
- June 8: Tufa at 1.21.
- June 30: 1.31.
- July 1: Tufa open-sourced the Duck. By July 8, 115 teams were at 1.0 or higher, and the top stayed near 1.86 into August.
- About Aug 14 (the Qwen3.8-27B release): Daniel Franzen reached 2.58.
- Sep 1 (after Qwen3.8-Flash-Next shipped on Aug 27 ([HF model card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next))): mostik.ai reached 7.51.
- Sep 6: Tufa at 11.04. Sep 13: Tufa at 18.81.
- Sep 19: NVARC3 at 16.07.
- Sep 22: Lord Han Solo at 19.40, then 19.45 on Sep 24.
- Sep 24: Yi-Chia Chen at 18.63, up from 12.88 on Sep 19.

One participant reported that Qwen3.8-27B gives "a consistent 2x score on the local 25 dataset" ([discussion 735243](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735243)).

### What won Milestone #1, and why

All three Milestone #1 winners ran one local open-weight model on the RTX PRO 6000. Their scores were tiny: **Tufa Labs "The Duck" 1.21, Reki 0.86 and forge 0.86** ([Tufa write-up, discussion 717133](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133); [Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution); [forge notebook](https://www.kaggle.com/code/mbmmurad/arc-agi-3-lb-0-86-3rd-place-candidate-milestone)). The leaderboard leader at the June 30 deadline, Ravi's Agi at 1.31, is not among the winners ([arc3.huikang.dev](https://arc3.huikang.dev/leaderboard)). That fits the prize passing down to open-sourced notebooks **[Inference]**.

**The Duck** (MIT-licensed, [GitHub](https://github.com/Tufalabs/duck-harness)) treats the game as a coding problem. Its main parts:
- **Model and serving:** `vrfai/Qwen3.6-27B-FP8` under vLLM 0.19 with `--enable-prefix-caching`, `preserve_thinking`, the `qwen3_coder` tool parser and `--max-model-len 65536`. Thinking is on, with temperature 0.6, top_p 0.95 and top_k 20.
- **Turn budget:** each turn yields after 60 s and may make unlimited tool calls.
- **Tool:** a single `python` tool that starts a fresh interpreter on every call. It has a 30-second timeout, output capped at 4,096 characters, and an allowlist of standard-library imports.
- **State access:** preloaded variables such as `current_frame.segmentation`, `history`, `transitions` and `last_action_result`. The model acts by calling `action([...])` inside Python. The raw numeric grid is hidden and UNDO is withheld.
- **Perception:** a 4× upscaled PNG of the current frame only, plus 4-connected component segmentation. Segmentation was added because the model kept printing whole grids into its own context.
- **Memory:** the harness keeps about **32K tokens of working context by evicting the oldest messages** (FIFO), capped at 30 assistant turns. A "working world model" note is parsed from the model's visible text and reset at each level transition.

Tufa writes that "hand-crafting specific tools for the model did not help, as it seems to hinder the creative abilities of the model." They admit the harness "has not been scrutinized and ablated" and that they "do not optimally use prefix caching" ([Tufa write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133); [duck-harness source](https://github.com/Tufalabs/duck-harness)). The bundled example run covers 25 games × 20 passes: mean 1.60, **median 0.07**, zero full-game wins, 68,682 actions and 29.6M generated tokens ([example-run summary](https://github.com/Tufalabs/duck-harness)). Tufa's framing is that solvability is set by the model and cost by the harness ([Tufa blog](https://tufalabs.ai/research/duck-harness/)).

**Reki** and **forge** both fork the public ko0kip Gemma-4-31B reflection agent (LB 0.64), which returns JSON actions ([ko0kip notebook](https://www.kaggle.com/code/ko0kip/arc-agi-3-gemma-4-31b-reflection-agent)).
- **Reki** added two cheap numpy click rules that can each be switched off. The first is a salience-ranked "button-like" click fallback (0.5 × color rarity + 0.5 × a size score). The second is a "dead-signature" rule: any object class, keyed by (color, size, is_rect, twin count), whose clicks change nothing twice is banned for the rest of the level ([Reki notebook](https://www.kaggle.com/code/ruichardliu/milestone1-2nd-solution)).
- **forge's** best run "used a profile that turns off all of the extra machinery", including its multi-candidate arbiter ([ARC Prize Milestone #1 blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)). An untouched copy of the same notebook later scored 0.00, which Reki attributed to an infrastructure or timeout failure ([discussion 725002](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/725002)).

**[Inference]** The two +0.22 gains over the 0.64 base are within the run-to-run noise reported for the Duck (0.7–1.3 for the same notebook), so the value of the specific tricks is unproven ([discussion 716696](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716696)).

### The public recipe and the community's A/B ledger

Almost every high-scoring public notebook after July is a Duck fork. The best public recipe is **the Duck harness unchanged, the model swapped to `RadixArk/Qwen3.8-Flash-Next-NVFP4`, 28 concurrent games and 7,920 s (132 min) per game**. That is four waves of 132 minutes inside the 540-minute limit. Its public bests are **4.50 ("Tuned"), 4.33 ("Anim Base") and 3.38 ("Flash Next NVFP4 MTP")**. The same builds score 5.2–6.8 on the public-25 ([Anim Base](https://www.kaggle.com/code/wuliao0/duck-qwen3-8-anim-base); [Tuned](https://www.kaggle.com/code/chiakazirim/duck-qwen3-8-tuned); [Flash Next NVFP4 MTP](https://www.kaggle.com/code/keithtyser/duck-qwen3-8-flash-next-nvfp4-mtp)). Their vLLM profile uses NVFP4 weights with BF16 compute, 3-token MTP speculative decoding, 32K context, 8 sequences, a 5 GiB KV cache and prefix caching off, plus a watchdog that restarts vLLM after four failures. The table records the controlled or semi-controlled results participants have published.

| Change | Result reported | Verdict |
|---|---|---|
| Qwen3.6 → Qwen3.8-27B | ~2× local score ([735243](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735243)); hidden 1.12 with no other change ([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)) | Keep |
| 27B → Qwen3.8-Flash-Next NVFP4 | "On the seven games the 27B never clears, Flash-Next clears every one at matched clock" ([sonpham-org/arc-3](https://github.com/sonpham-org/arc-3)); public forks at 3.4–4.5 LB | Keep |
| "B81" serving profile: MTP off, 7 GiB KV, 28 sequences, fixed sampler seed, 180 s yield | KV holds 263,568 tokens; time to first token 126 → 66 s; model calls 1,369 → 1,780; 45 levels vs 32–41; hidden draws 4.50 / 3.86 / 3.03 / 5.36 (mean 4.19) vs a ~2.88 mean over 20 draws of the earlier Flash-Next build ([tantan0327 SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent)) | Keep |
| Newer vLLM with MTP on | The only one of 14+ modifications that beat its baseline (2.27 vs a 1.9–2.2 band, +7 levels) ([tantan0327](https://github.com/tantan0327/arc-agi-3-agent)) | Keep; measure MTP against KV headroom |
| Pinned, deterministic serving with preflight checks | "More reliable improvement than several complicated prompting experiments" ([739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938)) | Keep |
| Backfill the world-model note from hidden reasoning | 66.8% of Qwen tool-call responses had no visible text; local score 9 → 11% on DeepSeek V4 Flash ([734843](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734843)); 38 vs 32 levels ([tantan0327](https://github.com/tantan0327/arc-agi-3-agent)) | Keep |
| Click candidates + true scoring rule + `time_remaining_seconds` pacing | 1.12 → 1.43 hidden (+28%) ([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)) | Keep |
| Animation tool and metadata | +1.4% mean, p = 0.92; +17% tokens per action ([734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369)) | Neutral |
| Hard no-op guard | Claimed 12–20% fewer actions, later discounted because runs are time-bound ([734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369)) | Keep (free) |
| Compact-reasoning prompt | Tokens per action 874 → 595, +43% actions per clock, 19/25 games improved (p = 0.007); the score gain "rests entirely on one game" ([sonpham-org/arc-3](https://github.com/sonpham-org/arc-3)) | Promising |
| STaR LoRA on the agent's own wins (Qwen3.6-27B) | LB 1.25 → 1.94; "naively scaling the data hurt" ([739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047)). Others: "only backfired"; behavioral cloning 11.04 → 12.97 local if the traces come from the same model ([732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854)) | Promising, contested |
| Context 32K → 64K | 1.20 vs 1.43; decode 283 → 195 tok/s; bp35 produced zero actions ([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)) | Reject |
| Temperature 0.6 → 0.3 | 0.95; "games with any progress collapsed from 12 to 8" ([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)) | Reject |
| Archetype playbook (navigation, pattern, physics…) | 1.54, below its pre-registered bar, because of "premature commitment" ([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)) | Reject |
| Observer/Theory/Action/Advisor roles; strategy library; human-play imitation | 5× the calls; game-specific bias; no gain over base Qwen3.8 ([739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938)) | Reject |
| More time for games that reach level 2 | Public 7.6 → ~13, but a "slight digression" on hidden games ([740812](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740812)) | Reject |
| Upscale 4× vs 8× | No clean A/B; identical passes scored 2.85 vs 4.75 ([739801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739801)) | Unresolved |

**[Inference]** The pattern is consistent. Changes that raise tokens per second or cut tokens per action buy decisions and levels. Changes that add tokens per action (more context, more frames, more roles) cost moves. Prompt edits move hidden scores by at most ~±30%, while model swaps moved them 2–3×.

### What the top five probably know

None of the top five has disclosed a method. Tufa and NVARC3 have said they will not open-source before the end of the competition ([discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801)). The top five sit at **3.5–4.5× the best public notebook**, and the public forks all run the same Duck + Flash-Next stack, so the top teams must have something that is not public.

**[Inference]** Several clues point to fine-tuning, synthetic data and harness memory fixes rather than prompts:
- Tufa jumped 11.04 → 18.81 in one week (Sep 6 → Sep 13) with no public model release in between.
- Yi-Chia Chen went 12.88 → 18.63 in five days with only 11 total submissions.
- NVARC3's roster includes Elad Sarafian and Gal Kaplun, co-authors of the DreamTeam multi-agent world-model harness ([arXiv 2605.09650](https://arxiv.org/abs/2605.09650)).
- NVARC won ARC Prize 2025 on the ARC-AGI-2 track largely through synthetic data and test-time training ([ARC Prize 2025 report](https://arxiv.org/abs/2601.10904)); that NVARC3 continues that approach is also an inference.
- One participant speculates that Tufa's lead is "part… some fine tuning" ([discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801)).
- Another concludes that "the only path forward is a winning recipe for SFT/RL on an existing model" ([discussion 732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854)).

A useful counterpoint comes from a byte-identical Flash-Next fork: "98.3% of a solving trajectory's decisions occur at a board state never seen before in that game… no harness engineering raises that ceiling" ([tantan0327 SOLUTION.md](https://github.com/tantan0327/arc-agi-3-agent)). **[Inference]** Read the two together: the missing ingredient is better reasoning about novel configurations. Training on diverse mechanics provides that; prompt tuning on the public-25 does not.

**[Inference]** Displayed LB scores are the maximum over many noisy draws. Tufa has 146 submissions, but Yi-Chia Chen's 18.63 rests on only 11, so it is less inflated by that effect. The final private ranking among the top five can reshuffle.

### Why runs fail

Wall-clock is the binding constraint: "Every run in both arms hits the 132-minute wallclock cap. Nothing ends because of an action limit and nothing ends in a win" ([discussion 734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369)).

Qwen3.8-27B wastes much of that clock. Its reasoning blocks average ~5,380 characters, 88.5% contain "wait/hmm/actually", and every game ended by giving up on the per-game clock ([sonpham-org/arc-3](https://github.com/sonpham-org/arc-3)).

Other recurring failures:
- **Context bloat** from full-board dumps ([Tufa write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)).
- **Lost memory** when reasoning stays in hidden thinking ([734843](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734843)).
- **Hypothesis fixation**: "once [the world model] is wrong, no amount of in-run recovery helps within the time budget" ([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)).
- **Confusing the HUD or energy bar with the goal** ([Tufa write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)).
- **Infrastructure zeros**: identical notebooks scoring 0.93 and then 0.00 ([738762](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738762)).

Run-to-run variance is also large. Eleven official submissions of one identical Duck harness ranged from **0.55 to 1.29** ([discussion 731522](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/731522)), and public forks report "same code can bring you from 2.5-5.5" ([discussion 737617](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/737617)). Continuous batching can change a trajectory even with a fixed seed ([discussion 739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938)).

## World models reach 93–100% on public games, at 100× Kaggle's budget

### The converged frontier recipe

By August 2026 the public-25 was effectively saturated by coding-agent harnesses around closed models. None of these systems reports semi-private or private results.

| System | Model | Public-25 RHAE | Core mechanism | Compute reported |
|---|---|---|---|---|
| Executable World Models ([2605.05138](https://arxiv.org/abs/2605.05138)) | GPT-5.5 high | 58.12 (15/25 games) | Codex maintains engine, state I/O and planner files; exact-replay verifier; halt-on-mismatch executor; refactor toward simpler rules | ChatGPT Pro; up to ~48 h per hard game |
| Its ablation v1.6 ([2607.15439](https://arxiv.org/abs/2607.15439)) | GPT-5.6 Sol xhigh | 98.97 | Fixed interface + simplification + verification | 90.75M cost tokens |
| OPINE-World ([2607.01531](https://arxiv.org/abs/2607.01531)) | Two Opus 4.8 agents | 78.4 (20/25; 160/183 levels) | Actor plus synthesizer; CEGIS with exact replay; Dirichlet "ontology error" steers exploration | Not reported |
| Twin ([2608.14490](https://arxiv.org/abs/2608.14490)) | GPT-5.6 Sol | **93.3** (23/25; 179/183) | Harness-enforced replay before any scored move; goal hypotheses before first reward; BFS inside the model | **2.60B tokens; 91.4 h** |
| Tycho ([2607.28287](https://arxiv.org/abs/2607.28287)) | Opus 5 / GPT-5.6 Sol | **100.00** | Moore-machine models; actor requests a builder subagent | ~$119 per game mean (Opus 5) |
| PRO-LONG ([2607.20064](https://arxiv.org/abs/2607.20064)) | Fable 5 | 94.6 pass@1; 97.4 best@2 | Lossless interaction log searched with code; no mandated model | $1,500–1,750 total |
| Prime Agent ([2608.23552](https://arxiv.org/abs/2608.23552)) | Opus 5 | 95.5 | Persistent IPython REPL; continual harness | n/a |
| NOOA ([2607.20709](https://arxiv.org/html/2607.20709)) | GPT-5.6 Sol | 85.1 | World-model skill + memory subsystem | 2-hour fleet cap |
| DreamTeam ([2605.09650](https://arxiv.org/abs/2605.09650)) | Opus 4.6 + GPT-5.5 | 38.4 | Multi-role workspace with ownership of schema fields | n/a |

The shared recipe has six steps:
1. Keep an append-only transition log.
2. Have the LLM write an executable `step(state, action)` and a goal predicate.
3. Accept the model only if it replays the whole log cell-exactly, predicting the *settled* frame after animations.
4. Plan with classical search inside the model.
5. Execute step by step and halt at the first mismatch.
6. Repair from the counterexample and refactor at each level boundary.

([Twin](https://arxiv.org/html/2608.14490); [OPINE](https://arxiv.org/html/2607.01531); [Rodionov ablation](https://arxiv.org/html/2607.15439))

Twin's numbers show why this works:
- 92.9% of scored actions executed plans already tested in simulation.
- Real outcomes disagreed with the model on 20.1% of actions.
- The first goal hypothesis was correct on 156 of 179 levels.
- The authors conclude that "building a usable world model is simpler than anticipated, whereas the harder problem is inferring the right goal."
- The same model scores 7.8 in direct play and 61.1 in plain Codex.

([Twin](https://arxiv.org/abs/2608.14490))

Tycho adds a warning. Automatic repair on verification failure raised transition accuracy but lowered RHAE: 83.07, versus 88.49 when the actor chose when to delegate. "Transition match indicates whether a simulator reproduces observed dynamics, not whether it has identified the objective" ([Tycho](https://arxiv.org/abs/2607.28287)). Rodionov's ablation found that capability dominates the harness. The four variants average **34.36 (gpt-5.4-high) → 48.05 → 58.50 → 72.52 (gpt-5.5-xhigh)**, and "at max, the three imposed mechanisms are not required for action-efficient public-set completion" ([arXiv 2607.15439](https://arxiv.org/abs/2607.15439)).

Two sources report different numbers for the Executable World Models baseline. The paper itself reports 58.12 with 15 wins; OPINE and Twin cite 63.8 with 14 wins. The per-game rows differ too, so the 63.8 figure likely comes from a different run.

### The older program-synthesis lineage

The ARC-AGI-3 systems descend from four lines of work:
- **WorldCoder's optimism-constrained code world models** ([2402.12275](https://arxiv.org/abs/2402.12275)). **It scored 0.0 on ARC-AGI-3 as run by OPINE** ([OPINE](https://arxiv.org/html/2607.01531)).
- **Code World Models / GIF-MCTS** ([2405.15383](https://arxiv.org/abs/2405.15383)) and DeepMind's code world models for general game playing with MCTS ([2510.04542](https://arxiv.org/abs/2510.04542)).
- **PoE-World's products of small programmatic experts** ([2505.10819](https://arxiv.org/abs/2505.10819)).
- **Theory-based RL**: EMPA ([2107.12544](https://arxiv.org/abs/2107.12544)) and TheoryCoder/TheoryCoder-2 ([2503.20124](https://arxiv.org/abs/2503.20124); [2602.00929](https://arxiv.org/abs/2602.00929)).

OneLife's precondition→effect laws ([2510.12088](https://arxiv.org/abs/2510.12088)) and PoE-World's small experts suit weaker models, because small local programs are easier to write and repair than one monolithic engine **[Inference]**. Neither has been tested on ARC-AGI-3.

Only GIF-MCTS reports a sizable open model. On the easy CWMB discrete tasks, Llama 3 70B reached **0.84 accuracy / 0.76 return** against GPT-4 Turbo's 0.91 / 0.81. On RTFM it managed **0.58 / −0.11** against GPT-4 Turbo's 1.00 / 1.00 at 50 calls, and "the generated CWM is only able to match the performance of the ground-truth simulator when the program is perfect" ([GIF-MCTS](https://arxiv.org/html/2405.15383)). A small-model distillation (SFT + RLVR on Qwen2.5-3B) improves code-world-model generation, but it has not been tested on ARC-AGI-3 ([2605.24375](https://arxiv.org/abs/2605.24375)).

### Honest feasibility on one GPU with open weights

**No executable-world-model or program-synthesis paper reports ARC-AGI-3 results with an open-weight model.** The only open-weight ARC-AGI-3 paper result is AERA's Qwen2.5-0.5B prompting agent. It is not a world-model method, and it uses non-standard scoring ([AERA](https://arxiv.org/abs/2605.25931)).

The budget gap is the decisive fact.
- **Twin** used ~224,000 processed tokens *per scored action* and 5.1M–625M tokens per game ([Twin](https://arxiv.org/html/2608.14490)).
- **Tycho's** Opus 5 run emitted about 0.94M output tokens per game (23.4M over 25 games) ([Tycho](https://arxiv.org/html/2607.28287)).
- **A Kaggle entry** generates roughly 70–120K tokens per game (see the throughput section) and processes about 11× that in prompts.

**[Inference]** That is about 100× less total processing than Twin and roughly an order of magnitude less generation than Tycho, with a much weaker model. The capability gradient in Rodionov's ablation and the GIF-MCTS results imply a far larger accuracy drop than the ~0.07 CWMB gap suggests. ARC-AGI-3 rewards only near-perfect models: exact replay plus the correct goal.

Kaggle practice points the same way. A top-15 team reports that "AVO style ideas… haven't… beat our current harness" ([discussion 737617](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/737617)). Tufa reports that GPT-5.4 inside the Duck solves "a similar set of games" to the Executable World Models agent at "an order of magnitude cheaper on each game" ([Tufa blog](https://tufalabs.ai/research/duck-harness/)). **[Inference]** A REPL agent already captures much of the world-model benefit when the model is strong enough.

**[Inference]** What transfers cheaply are the non-LLM pieces:
- an exact-replay checker;
- a halt-on-mismatch executor;
- BFS with state deduplication;
- Twin's rule that a goal predicate must be false on every logged frame;
- OPINE's Dirichlet effect table for exploration priority.

These are best offered as generic, opt-in functions in the REPL, not as a mandatory pipeline.

## Frontier harnesses teach memory and verification, not hand-built tools

The largest measured harness effect is about memory. OpenAI reported that enabling **retained reasoning and compaction** lifted GPT-5.6 Sol on the public set from **13.3% to 38.3% with roughly 6× fewer output tokens**. The original harness had discarded the model's reasoning after every action and truncated history past 175,000 characters, so the model had to "re-figure the game from scratch on each turn" ([OpenAI](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/), via [officechai](https://officechai.com/ai/openai-says-gpt-5-6s-score-on-arc-agi-3-tripled-after-turning-on-two-api-settings/); the primary page could not be fetched).

ARC Prize now reports two harness modes for the semi-private set:
- The **Standard harness** keeps provider-neutral visible notes with rolling context.
- The **Provider Adapter** keeps native reasoning and uses compaction.

([arc-agi-3-benchmarking](https://github.com/arcprize/arc-agi-3-benchmarking)). **GPT-6 Astra scores 62.7% Standard (max reasoning, $26,098 total) versus 96.7–99.95% with the Adapter**, and the Adapter used 49% fewer tokens ([ARC Prize Astra blog](https://arcprize.org/blog/astra)). For reference, the other semi-private scores are: Claude Opus 5 at 30.16%, GPT-5.6 at 7.78% ([ARC Prize results](https://arcprize.org/results)), and every frontier model below 1% at launch ([ARC-AGI-3 paper](https://arxiv.org/html/2603.24621)).

**[Inference]** The Duck's FIFO eviction and its note parsed only from visible text are the local equivalent of the "rolling truncation" OpenAI blamed. This makes memory the most under-exploited lever relative to its evidence.

PRO-LONG supplies the second lesson: **a lossless, append-only log that the agent searches with code beats self-authored notes**.
- GPT-5.5 climbs from 23.1 (read-only) to 27.2 (+grep), 38.3 (+Python) and 41.2 (+write/edit).
- Clearing the agent's workspace after each call barely hurts (40.7 vs 41.2).
- Removing the log hurts a lot, although secondary readings of the paper disagree on the exact figure; see the final section.
- One agent spontaneously wrote `regress.py` to replay the log against its own game model.

([PRO-LONG](https://arxiv.org/html/2607.20064v2)). The AWS Strands harness took Opus 5 to **99.95% on the public-25 for about $830**. It used only bash, Python, files and grep, keeping a `current_board.txt` and an appended `logs.txt` ([Strands](https://strandsagents.com/blog/our-production-sdk-hit-99-95-on-arc-agi-3/)). NVIDIA's AVO adds a **supervisor** that watches for "stagnation or repeated unproductive cycles" ([NVIDIA](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/)). Astra and Opus 5 both invented compact algebraic notations for game state ([Astra blog](https://arcprize.org/blog/astra)).

ARC Prize's trace analysis found that **perception is not the main bottleneck for frontier models**. The dominant failures are:
- **Local effects never abstracted into rules.**
- **Anchoring on known games** (Tetris, Frogger, Sokoban, Breakout).
- **"Success without understanding"**: an early level cleared on a wrong theory, which then hardens in later levels.

([ARC Prize analysis](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis))

ARC Prize 2025 (ARC-AGI-2) was won by test-time training with synthetic data (NVARC 24.03%), and ARC Prize framed that year around the "refinement loop" ([ARC Prize 2025 results](https://arcprize.org/blog/arc-prize-2025-results-analysis)). The loop transfers to ARC-AGI-3 as model code checked against the log. Grid-to-grid test-time training does not, because ARC-AGI-3 has no demonstration pairs **[Inference]**.

| Frontier lesson | Evidence | Transfer to a Kaggle ~27B/6B-active model **[Inference]** |
|---|---|---|
| Retained reasoning + compaction | 13.3 → 38.3 (GPT-5.6 Sol); Astra 62.7 → 96.7–99.95 | Yes, harness-only: keep `preserve_thinking` for recent turns; summarize instead of FIFO-evicting; untested on open models |
| Lossless log + code search | PRO-LONG tool ladder; Strands | Yes; standard library only; makes eviction safe |
| Python sandbox | +10.8 pp from Python alone | Already in the Duck; make REPL state persistent |
| Self-written world model + replay + BFS | Twin, Tycho, `regress.py` | Partial; opt-in tools only; capability-bound |
| Compact state notation | Emergent in Astra and Opus 5 | Yes; object lists and diffs as REPL variables |
| Supervisor / stagnation detection | AVO; Reki's dead-signature rule | Yes, with cheap rules |
| Level-transition re-validation | ARC Prize failure analysis | Yes; replay the note's claims against the log at each level |
| Multi-agent orchestration; best-of-k | Arcgentica; PRO-LONG best@5 60.1 vs 41.2 | No: GPU time rules it out, and Kaggle scores one play per game |

## Non-LLM exploration sets a floor and filters actions, but cannot score alone

The 2025 preview was won by search agents that scored through brute-force coverage:
- **StochasticGoose** (Tufa Labs; 12.58%, 18 levels, **255,964 actions**) trained a CNN online to predict which actions change the frame ([code](https://github.com/DriesSmit/ARC3-solution/blob/main/custom_agents/action.py)). It uses a 4,096-logit fully convolutional click head, one gradient step every 5 actions, and a buffer of up to 200K deduplicated entries that is reset every level.
- **Blind Squirrel** (6.71%, 13 levels) built a state graph with no-op and loop pruning, per-color connected-component clicks, and a ResNet18 value model retrained after each level ([code](https://github.com/wd13ca/ARC-AGI-3-Agents/blob/main/agents/blind_squirrel.py)).
- **Rudakov's frame-graph explorer** (3rd by levels; 12 of 25 private levels, and a median of 17 after a reset-loop bug fix) prioritized segments in tiers and walked to the nearest untested edge ([code](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore); [arXiv 2512.24156](https://arxiv.org/abs/2512.24156)).

([30-day learnings](https://arcprize.org/blog/arc-agi-3-preview-30-day-learnings))

Under squared efficiency these methods collapse. Rudakov needed ~3.2K steps for ls20 level 2 and ~36K for sp80 level 2 ([arXiv 2512.24156](https://arxiv.org/html/2512.24156)). The benchmark's validation step requires that random play not beat non-tutorial levels ([ARC-AGI-3 paper](https://arxiv.org/html/2603.24621)). On Kaggle, non-LLM entries plateau below about 0.5:
- the official Random Agent at 0.18, "Just Explore" at 0.19 and Stochastic Goose at 0.25;
- BDR-Pro's mature programmatic agent at 0.26–0.27;
- "Persistent Memory BFS" at 0.46.

([Stochastic Goose sample](https://www.kaggle.com/code/inversion/arc3-sample-submission-stochastic-goose); [Random Agent](https://www.kaggle.com/code/inversion/arc3-sample-submission-random-agent); [BDR-Pro](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3); [code tab](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/code))

BDR-Pro found that "even correct bug fixes and a +50% local mean moved the LB by ±0.01", and switched to calling an LLM on stalls ([BDR-Pro](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3)). In April, the leading public notebooks (~0.44) ran offline BFS over the 25 public game engines. That approach does not transfer to hidden games ([discussion 687950](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/687950)).

The techniques are still worth having as a cheap substrate under the LLM:
- **Click reduction.** Segment clicks into same-color connected components. Rudakov ranks five tiers, from G0 (salient color with a 2–32 px bounding box) down to G4 (status bars); Blind Squirrel orders by regularity then area. Blind Squirrel's author estimates this cuts the click space ~100×.
- **HUD masking before hashing.** Rudakov masks edge segments with aspect ratio ≥5 or "twins". BDR-Pro's volatility mask covers cells changing in ≥20% of frames, or rows and columns changing in ≥40%, which catches depleting energy bars.
- **Dead-click pruning.** BDR-Pro skips colors clicked ≥8 times with no effect. Its "cell (x, y) showing color c does nothing" rule, applied after 4 no-ops, was credited with a +68% local mean. Because the rule is keyed by appearance, a button that changes color can escape the ban.
- **Avatar detection.** Diff frames after each direction and vote on per-color displacement. Reject colors that move identically under three or more actions (gravity, conveyors). BDR-Pro's opening probe presses each action 3× and converges in ~12–24 actions.
- **Goal-color carry-over.** Colors that shrank when the score rose become the next level's target hypothesis.
- **Banked-prefix replay.** Replay the best known prefix after a death instead of re-earning progress.

([heuristic_agent.py](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore/blob/main/agents/heuristic_agent.py); [BDR-Pro](https://github.com/BDR-Pro/arc-prize-2026-arc-agi-3))

Twin ranks candidate goal states with five domain-neutral signals: a color disappears, a new color appears, a local burst of ≥5 changed cells, a large change of more than 25% of cells, and frontier novelty. It exploits the fact that "every recorded frame is a certified negative" for the goal ([Twin](https://arxiv.org/abs/2608.14490)). No ARC-AGI-3 result exists for neural curiosity (RND, ICM). Rudakov doubts that surprise tracks goal relevance ([README](https://github.com/dolphin-in-a-coma/arc-agi-3-just-explore)).

**[Inference]** The deterministic, fully observable games make exact-hash visit counts a better novelty signal than learned novelty. Go-Explore's "return" step can only be done with RESET plus replay, which costs scored actions.

AERA's widely cited claim that most public games fall to trivial strategies (10 games "in a single blind step") does not hold up:
- Its RHAE values are exact multiples of 1.15²/N.
- A null-coordinate crash was misreported as WIN.
- Its "RHAE 0.30 on the full 55-game private evaluation" is, per its own §4.1, a Kaggle public-LB score of 0.30 (i.e., 0.30%) from a BFS kernel ([AERA](https://arxiv.org/html/2605.25931)).

One genuinely useful finding survives: a small LLM never chose ACTION6 on some click games, and forcing an early ACTION6 probe fixed this. The lesson is that small-model action priors under-select clicks, so salient objects should be probed early.

## One 96 GB card buys roughly 70–120K generated tokens per game

### Model shortlist

| Model | Size | License | Vision | Fits the 96 GB card? | ARC-AGI-3 evidence |
|---|---|---|---|---|---|
| **Qwen3.8-Flash-Next** (RadixArk NVFP4) | 125B total / 6B active + 51B n-gram embeddings ([HF](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)) | `qwen-community-1.0` (not Apache) | Yes | Only via FP4 + host-offloaded n-gram embeddings ([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)) | Used by every top public fork (3.4–4.5 LB); clears games the 27B never clears |
| **Qwen3.8-27B** FP8 | 27.8B dense; 262K context ([HF](https://huggingface.co/Qwen/Qwen3.8-27B)) | Apache-2.0 | Yes; BabyVision 65.7 vs 28.9 for 3.6 | ~34 GiB of weights | ~2× local over Qwen3.6; hidden 1.12 alone, 1.43 with fixes |
| Qwen3.6-27B FP8 | 27.8B dense | Apache-2.0 | Yes | 33.66 GiB measured ([Duck logs](https://github.com/Tufalabs/duck-harness)) | Milestone #1 winner, 1.21 |
| Gemma-4-31B-it | 30.7B dense ([HF](https://huggingface.co/google/gemma-4-31B-it)) | Apache-2.0 | Yes | ~31–33 GB FP8 | Milestone #1 2nd/3rd (0.86); "sees better" than Qwen3.6 but "falls far behind" in logic and coding ([739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938)) |
| Gemma-4-26B-A4B; Qwen3.6-35B-A3B | MoE, 3–4B active ([HF](https://huggingface.co/google/gemma-4-26B-A4B-it)) | Apache-2.0 | Yes | Comfortable | No LB evidence; several times cheaper decode |
| GPT-OSS-120B | 117B / 5.1B active, MXFP4 ([HF](https://huggingface.co/openai/gpt-oss-120b)) | Apache-2.0 | No | ~61–65 GB | Official template; ~830 tok/s at 25 concurrent on the Kaggle RTX ([738599](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738599)); plays only through a symbolic decoder, "overly roundabout" ([739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938)) |
| DeepSeek-V4.x-Flash, GLM-5.3, Kimi-K3, MiMo-V2.6 | 284B to 2.78T | Various | Various | No | DeepSeek-V4-Flash was "only slightly better than Qwen-3.6 27B" when run off Kaggle ([735243](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735243)) |

**[Inference]** Choose Flash-Next NVFP4 for score. Keep a validated Qwen3.8-27B-FP8 build (Apache-2.0, the same `qwen3_5` parsers the Duck uses) as the fallback for eligibility. Flash-Next's non-Apache license sits in an area the rules have not settled: they demand OSI-open weights but exempt pretrained models with incompatible licenses ([Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)).

### Serving configuration

Use vLLM, the proven path. The Duck ran vLLM 0.19 from an offline wheelhouse dataset, and Qwen3.8 builds use vLLM 0.27.x or newer ([duck-harness kaggle.py](https://github.com/Tufalabs/duck-harness); [HF discussion](https://huggingface.co/Qwen/Qwen3.8-27B-FP8/discussions/9)).

- **Wheelhouse:** build it on a Kaggle RTX image with internet on, pin it with SHA256 hashes, and install with `--no-index` ([leejianrong artifact notes](https://github.com/leejianrong/solve-arc-agi-3/blob/main/docs/baselines/qwen36-vllm-artifact.md)).
- **Blackwell workaround:** set `VLLM_USE_FLASHINFER_SAMPLER=0` to avoid a FlashInfer JIT crash on sm_120 ([HF discussion](https://huggingface.co/Qwen/Qwen3.8-27B-FP8/discussions/9)).
- **KV-cache sizing for a 27B:** only 16 of Qwen3.x-27B's 64 layers keep a growing KV cache. That is about 64 KiB per token in BF16 or 32 KiB in FP8, so the 96 GB card should hold roughly 740K (BF16) to 1.5M (FP8) KV tokens beside the 27B weights **[Inference from the model card and Duck logs]**.

MTP speculative decoding helps a single stream. It raised Qwen3.8-27B-FP8 from 46.8 to 62.2 tok/s at depth 2 on a 300 W card, and to 80–100 tok/s at depth 3 on a 600 W card ([HF discussion](https://huggingface.co/Qwen/Qwen3.8-27B-FP8/discussions/9)). On Flash-Next, though, the draft head crowded out KV cache ("the server runs ~3 requests and queues ~22"), so MTP off with a 7 GiB KV cache did better, while a newer vLLM with MTP was also a win ([tantan0327](https://github.com/tantan0327/arc-agi-3-agent)). **[Inference]** Measure MTP depth against KV headroom at your real concurrency. Late in the run, when few games are still active, MTP matters more.

Concurrency reports conflict: 16 is claimed as a saturation point ([739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938)), while the B81 profile runs 28 sequences profitably. Measure it.

Prefix caching hit only **~48.6%** in the Duck's logs, because popping the oldest message on every turn changes the prefix ([Duck example-run logs](https://github.com/Tufalabs/duck-harness)). **[Inference]** Evicting in large, infrequent chunks keeps turns append-only.

### Budget arithmetic

| Quantity | Value | Basis |
|---|---|---|
| Usable wall clock | ~7.5–8 h of 9 h | **[Inference]** after install and load plus a 20–30 min buffer; participants fixed timeouts with 30-min buffers ([712719](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/712719)) |
| Scheduling | 28 concurrent games, 4 waves × 132 min | Public forks ([Anim Base](https://www.kaggle.com/code/wuliao0/duck-qwen3-8-anim-base)) |
| Aggregate generation, Flash-Next public profile | ~235–280 tok/s | Saved public-25 runs ([notebooks](https://www.kaggle.com/code/keithtyser/duck-qwen3-8-flash-next-nvfp4-mtp)) |
| Generated tokens per game | ~70–80K (Flash-Next); ~65–120K (27B estimate) | **[Inference]** ~250 tok/s × 7,920 s ÷ ~28 games; Duck logs scaled to the RTX |
| Duck per-pass profile | 59,198 generated tokens, 42 calls, 137 actions, 1,406 tokens/call, 3.26 actions/call | Duck example run ([benchmark.json](https://github.com/Tufalabs/duck-harness)) |
| Prompt : generated ratio | ~11 : 1; peak prefill ~9.9K tok/s on this card | Duck logs; [Millstone benchmark](https://www.millstoneai.com/inference-benchmark/qwen3-6-27b-fp8-1x-rtx-pro-6000-blackwell) |
| Decode at 4K vs 32K context | ~283 vs ~30 tok/s | [743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060) |
| Per-request latency | Median 4–5 min at 7 lanes | [sonpham-org/arc-3](https://github.com/sonpham-org/arc-3) |
| Human baseline per public game | 171–1,843 actions | [ARC API game list](https://three.arcprize.org/api/games) |

**[Inference]** At roughly 50 calls and 3–4 actions per call, a game gets 150–450 actions of model-directed play, while human baselines run into the hundreds or low thousands. The LLM cannot direct every step. It must emit verified multi-action batches or code (BFS, planners) and let cheap Python carry the rest. Prefill is the hidden cost. An image of a 64×64 frame upscaled to 256×256 costs about 64 visual tokens in Qwen3.x, against **4,097 tokens** for a one-character-per-cell grid ([Qwen3.6 preprocessor config](https://huggingface.co/Qwen/Qwen3.6-27B/blob/main/preprocessor_config.json); measured with the [Qwen3.6-27B tokenizer](https://huggingface.co/Qwen/Qwen3.6-27B/blob/main/tokenizer.json)). So send images and keep exact grids inside the REPL, as the Duck does.

### Thinking, vision and fine-tuning

The Duck runs with thinking on and `preserve_thinking` ([configs/inference.json](https://github.com/Tufalabs/duck-harness)). Fususu found that thinking on versus off changed little ([739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938)), and compact reasoning bought 43% more actions per clock ([sonpham-org/arc-3](https://github.com/sonpham-org/arc-3)). **[Inference]** Keep thinking on but control its length: use Qwen3.8's per-request `reasoning_effort`, a compact-style prompt, and a per-call token cap so one runaway thought cannot stall a game slot. Do not lower the temperature (0.3 hurt).

On vision, Tufa credits "multimodality and better base models" and found 4× upscaling best on Qwen3.6 ([Tufa write-up](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133)). Sending more frames or video hurt the small models.

On fine-tuning, the evidence is positive but contested:
- STaR LoRA on the Duck's own wins lifted Qwen3.6 from 1.25 to 1.94 ([739047](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739047)).
- Traces must come from the same model, and adapters are specific to the base model ([732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854)).
- The RTX PRO 6000 "can not be used for training of any ~100B model" ([742835](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742835)), so Flash-Next training needs an H200-class node off Kaggle.
- The host has not ruled on whether self-generated synthetic data counts as external data ([742940](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742940)).

## The public games teach an interaction grammar, not reusable mechanics

The 25 public games contain 183 levels, 6–10 per game, with per-level human baselines from 6 to 578 actions. In every game the goal is a *visible relation*: match a reference, fill outlines, reach a marked tile, or fit a key to a lock. The goal is never stated in text. The table below summarizes each game from the ARC API and community write-ups checked against the obfuscated source ([ARC API game list](https://three.arcprize.org/api/games); [arc-explainer](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games)).

| Game | Levels | Baseline total | Actions | Core mechanic | Win condition |
|---|---|---|---|---|---|
| ar25 | 8 | 748 | 1–7 | Move pieces and axis mirrors; A5 cycles the selection, A7 undoes | Reflections cover every target dot |
| bp35 | 9 | 651 | 3,4,6,7 | Move sideways under an automatic pull; clicks break, toggle or flip blocks; scrolling viewport | Reach the pink plus; spikes kill |
| cd82 | 6 | 171 | 1–6 | Selector among 8 dye stations; A5 fires, A6 picks a color | Recreate the corner reference before the countdown ends |
| cn04 | 6 | 789 | 1–6 | Select a part, slide it, rotate it | Printed marks meet their matching marks |
| dc22 | 6 | 1,228 | 1–4,6 | Walk while clicking buttons that move the floor; a claw from level 5 | Reach the yellow square |
| ft09 | 6 | 208 | 6 | Clicks cycle tile colors | Marker constraints satisfied within the click budget |
| g50t | 7 | 879 | 1–5 | A5 respawns you, and a ghost replays your recorded moves | Reach the goal before the timer ends |
| ka59 | 7 | 730 | 1–4,6 | Select and kick boxes (~15 cells); bombs from level 5 | Every outline holds a piece of its size |
| lf52 | 10 | 1,339 | 1–4,6,7 | Click peg solitaire; rail carts from level 2 | One peg left |
| lp85 | 8 | 388 | 6 | Buttons rotate loops of colored squares | Colored squares inside their targets |
| ls20 | 7 | 776 | 1–4 | Walk onto tiles that transform the key's shape, color and rotation; fog on the last level | Reach the door with a matching key; 3 lives per level |
| m0r0 | 6 | 1,107 | 1–6 | Mirrored twin tokens; desync them against walls | Both twins on one tile within 150 actions |
| r11l | 6 | 233 | 6 | Drag a blob by its limbs; eat colored food from level 5 | Body on the outline with a matching color |
| re86 | 8 | 1,255 | 1–5 | Slide the selected outline piece; color pads; bending walls | Every dot under a piece of its color |
| s5i5 | 8 | 638 | 6 | Slider buttons grow or shrink rods; rotation from level 6 | Markers sit on every pin |
| sb26 | 8 | 213 | 5,6,7 | Place tiles into slots, then run | Output matches the required sequence; 64 energy |
| sc25 | 6 | 350 | 1–4,6 | Walk a wizard; drawn sigils cast spells | Reach the exit (hidden countdown on level 4 per [Twin](https://arxiv.org/html/2608.14490)) |
| sk48 | 8 | 1,070 | 1–4,6,7 | A skewer extends, retracts and slides beads | Beads match the reference skewers |
| sp80 | 6 | 518 | 1–6 | Move bars; A5 pours | One pour fills every cup without spilling |
| su15 | 9 | 361 | 6,7 | Clicks vacuum pieces toward them; same-size pieces fuse | Circles hold the "shopping list" pieces |
| tn36 | 7 | 317 | 6 | Toggle program switches, then run | Token matches the target |
| tr87 | 6 | 414 | 1–4 | Cycle glyphs to translate with a rune dictionary; repair the dictionary later | Correct translation row |
| tu93 | 9 | 462 | 1–4 | Move along wires past biting and patrolling enemies | Reach the exit before the step bar runs out |
| vc33 | 7 | 447 | 6 | Pumps and gates move liquid and riders | Each rider level with its mark |
| wa30 | 9 | 1,843 | 1–5 | Sokoban with grab and release; rival haulers | Crates in their bays within budget |

The games combine about ten mechanic families:
- avatar navigation under a budget;
- pushing and Sokoban;
- select-then-move "orchestration";
- click-to-cycle toggles;
- matching a reference;
- fluids;
- geometric transforms;
- record-and-replay;
- autonomous or adversarial actors;
- partial observability.

Most games mix 2–4 families and add a new mechanic every few levels ([arc-explainer](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games)). By design, though:
- Single-mechanic games are "an anti-pattern".
- Each environment must be novel relative to existing video games *and* to the other ARC-AGI-3 environments.
- The private set is "significantly more difficult… and intentionally out-of-distribution", with "limited overlap with the mechanics found in the public environments".
- Every game has at least 6 levels, and level 1 is an easy tutorial.
- Each game was solved independently by at least two humans within a ~20-minute session.

([ARC-AGI-3 paper](https://arxiv.org/html/2603.24621))

The public games share UI conventions:
- Nearly every game draws a per-level action budget as an edge bar or a row of pips, and running it out triggers `lose()` → GAME_OVER.
- Some games add lives (ls20 has 3 per level) or instant-death hazards.
- The 25 source files are 777–41,463 lines each, with obfuscated identifiers, and all but tr87 and one lf52 helper are free of randomness.
- Clickable sprites carry a literal `sys_click` tag.

(from direct inspection of the game source files served by the [ARC API](https://three.arcprize.org/api/games), cross-checked with [arc-explainer](https://github.com/82deutschmark/arc-explainer/tree/main/shared/arc3Games) and the [arcengine package](https://pypi.org/project/arcengine/))

**[Inference]** The transferable prior is an interaction grammar:
1. Find what you control; it may need to be selected with a click.
2. Find the visible target configuration.
3. Measure each action's effect, including multi-frame effects such as sliding until blocked.
4. Watch the budget bar.
5. Expect new mechanics mid-game.

Budgets typically sit at about 1.5–4× the human baseline (e.g., re86 level 1: 100 vs 26), so some exploration fits but blind search does not. Level 1 is cheap (7–78 actions, median ~30), while later levels grow 3–10×. That is exactly where the weight, and therefore the score, sits.

## Only held-out, competition-mode, multi-pass evaluation predicts the hidden score

The public-25 misleads in both level and direction. ARC Prize built it to be easier; the host called a drop from 1.56 locally to 0.05 on the LB "inline with expectations" ([discussion 703990](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990)). Reported local → LB pairs:
- 22.26 → 5.37 and 17.34 → 6.91 / 5.19 (Fususu);
- 15.7 → 7.37;
- 9.91 → 6.23;
- 11.04 → 2.71;
- 6.8 → 1.19;
- 2.8 → 2.4.

([732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854); [736578](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/736578)). Nick Pellegrin observed that "doing better on the public set… correlates to weaker private scores" ([732854](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732854)). Frontier harnesses score 93–100 on the public-25, while the best standard-harness semi-private score is 62.7.

Noise is just as serious:
- sb26 alone swings the all-25 local score by ±23, and the standard deviation of a two-pass difference is ~21 ([sonpham-org/arc-3](https://github.com/sonpham-org/arc-3)).
- One team's +0.20 single-rollout gain was really −0.004, "INSIDE NOISE" ([tgaer PR #32](https://github.com/charleneleong-ai/tgaer/pull/32)).
- A single LB draw spreads by about ±50%.

A trustworthy local setup needs four properties.

**It must be mechanically faithful.**
- Run `Arcade.listen_and_serve(competition_mode=True)` locally and point the agent at it with `OPERATION_MODE=online` ([arc-agi 0.9.9](https://pypi.org/project/arc-agi/0.9.9/)). The starter's `play_local.py` uses NORMAL mode, which allows full resets and scores the best of repeated runs.
- Set `ONLY_RESET_LEVELS=true`.
- Use one scorecard per run.
- Score with the exact shipped formula.
- Enforce the 9-hour, 14-minute first-action and 15-minute idle limits.
- Replay the full 110-game shape. Tufa's `competition_arcade.py` clones the public games into 110 runs for this ([duck-harness](https://github.com/Tufalabs/duck-harness)).

**It must be held out.**
- Build a primary development set of 40–60 unseen ARCEngine games. `arcengine` is MIT-licensed and made for authoring games.
- Sources: `theredbluepill/arc-interactive` (249 games with a solvability checker) ([GitHub](https://github.com/theredbluepill/arc-interactive)), and the 927-game catalog in `sonpham-org/arc-3` (571 AI-generated, 252 redbluepill, 50 reviewed "arena", 29 custom) ([GitHub](https://github.com/sonpham-org/arc-3)).
- Filter out games that random, repeat-one-action or click-every-object baselines can solve.
- Set baselines at a BFS-optimal solution times a 1.3–2× slack **[Inference]**.
- Never tune prompts on this set.

**It must be statistically honest.**
- Use paired multi-pass designs: the same games in both arms, at least 4 passes per game, and per-game sign tests ([sonpham-org/arc-3](https://github.com/sonpham-org/arc-3)).
- For an unpaired test at 80% power, you need about **n ≈ 15.7σ²/Δ² runs per arm**, which is ~16 per arm when Δ equals σ **[Inference]**.

**It must track the metrics that predict the LB, not just the headline RHAE.**
- the number of games with any level cleared;
- the number of games with level 2 or later cleared;
- zero-action games;
- tokens per action;
- model calls and actions per game-hour;
- the share of games that end on the clock;
- the infrastructure failure rate.

**[Inference]** Keep a ledger that records, for every Kaggle submission, the configuration, the local held-out score, the public-25 score and the LB result. Fit your own mapping between them. Treat the LB as a calibration and confirmation channel for effects larger than ~50%, never as the primary A/B signal.

## Build plan: harden by Sep 30, test memory in October, freeze by Nov 1

### Ranked engineering changes to a Duck-style harness

The table ranks changes by expected value per unit of effort under the calendar. Impact estimates are **[Inference]** from the cited evidence, relative to a Duck + Flash-Next public baseline of roughly 3–4.5 LB.

| Rank | Change | Evidence | Expected impact **[Inference]** | Effort | Window |
|---|---|---|---|---|---|
| 1 | **Throughput-tuned Flash-Next serving.** NVFP4, MTP depth chosen by measurement, KV ≥7 GiB, ~28 sequences, CUDA graphs, fixed sampler seed, pinned wheelhouse, parser/tool-call preflight, vLLM watchdog | B81 mean 4.19 vs ~2.88 for the earlier build; +30% model calls; newer vLLM + MTP was the only winning modification ([tantan0327](https://github.com/tantan0327/arc-agi-3-agent)) | **+20–45%** over an untuned Flash-Next fork; 2–3× over 27B builds | Low | Before M2 |
| 2 | **Fail-closed infrastructure.** First action within 14 min; model loaded before the scorecard opens; global deadline with a 20–30 min buffer; `MAX_ACTIONS` override; GPU and parser checks; files written to `/tmp`; log cap | One-third of failures stuck and 20% without a GPU ([727119](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/727119)); 0.86 → 0.00 and 0.93 → 0.00 reruns | Removes zero-score draws; each zero wastes a submission day | Low | Before M2 |
| 3 | **Backfill the world-model note from hidden reasoning**, or require a visible note on each turn | 66.8% of responses had no visible text; 32 → 38 levels; 9 → 11% local ([734843](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734843)) | +10–20% levels (noisy) | Low | Before M2 |
| 4 | **Truthful prompt.** State the real scoring rule and "batch confirmed steps"; add `time_remaining_seconds` pacing and "change the hypothesis class after repeated failures"; delete false claims (100% per-level cap, "puzzle", HUD rule) | 1.12 → 1.43 with rank 6 ([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060)); a paired gain from deleting false claims ([sonpham-org](https://github.com/sonpham-org/arc-3)) | +0–30% | Low | Before M2 |
| 5 | **Zero-cost action guards.** Block exact repeats of a (level, masked board, action) no-op; guard against repeating an identical move; suppress dead click classes but re-enable them when their appearance changes; label ACTION7 as UNDO only when it is available | Dead clicks count ([718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638)); 12–20% fewer actions ([734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369)); Reki; [742477](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742477) | Small and positive on cleared levels; near-zero risk | Low | Before M2 |
| 6 | **Deterministic click candidates.** Salience-ranked component centroids exposed as a REPL variable when MOUSE is valid | Part of the +28% package; Reki; ~100× smaller click space | Included in rank 4 | Low | Before M2 |
| 7 | **Reasoning-length control.** Compact-reasoning style, a per-call `reasoning_effort` policy, and a per-call token cap | 874 → 595 tokens per action, +43% actions per clock; bp35 burned 28K tokens with zero actions | +10–40% decisions per clock; score effect unproven | Low | Oct 1–7 |
| 8 | **Prefix-cache-friendly memory.** Chunked eviction, a structured compaction summary, and reasoning retained for the last K turns, all inside a 32K window | OpenAI 13.3 → 38.3; Astra 62.7 → 99.9; Duck prefix-cache hit rate 48.6%; 64K context hurt | Largest untested upside (0 to +100%); risk of lower throughput | Medium | Oct 8–14 flagship A/B |
| 9 | **Lossless log and persistent REPL.** An append-only on-disk transition log, a persistent REPL namespace and helper library, and a REPL timeout raised from 30 s to 90–120 s | PRO-LONG log and Python ablations; the 30 s limit killed "our single most informative tool call" ([734369](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734369)) | Plausibly +10–30%; unknown at 27B/6B-active | Medium | Oct 8–14 |
| 10 | **Rule-based supervisor.** Stall detection (repeated masked-board hashes, no progress for N actions, action loops) forces a new hypothesis class; re-validate the note against the log at each level transition | ARC Prize failure modes; AVO; Rakha's "single-step verified recovery" ([739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938)) | Modest; targets hypothesis fixation | Low–medium | Oct 15–21 |
| 11 | **Self-trajectory SFT.** STaR or rejection sampling on the agent's own wins in synthetic games, using same-model traces, with the weights published | 1.25 → 1.94 LB; 11.04 → 12.97 local; "backfired" for others | +0–50%, high variance; plausibly part of the top teams' edge | High; needs external GPUs | Oct, only if compute is available |
| 12 | **Opt-in verified-plan tools.** `replay_check(step_fn)`, a halt-on-first-mismatch `execute_plan`, `bfs(step_fn, goal_fn)`, and a goal filter requiring predicates to be false on all logged frames | Frontier 93–100 on the public-25; Tycho found actor-requested delegation beats automatic repair; no open-weight evidence; Tufa found hand-crafted tools hurt | Speculative; use only as the ambitious final arm | High | Oct 15–21 |
| 13 | **Passive non-LLM facts in the REPL.** HUD/volatility mask, avatar and wall votes, goal-color carry-over, Twin's five change signals | Non-LLM ceiling ~0.3–0.5; tantan's perception layers were "not demonstrated to help" | Small or uncertain | Medium | Only if cheap |

Some changes are well supported as things *not* to do:
- widening context to 64K;
- lowering temperature;
- archetype playbooks and strategy libraries;
- multi-role LLM crews;
- multi-candidate arbiters;
- feeding more frames or video to small models;
- giving extra clock to games already at level 2;
- tuning on the public-25;
- anything built on the null-coordinate ACTION6 bug or offline caches of public-game solutions.

([743060](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/743060); [739938](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739938); [740812](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740812); [forge notebook](https://www.kaggle.com/code/mbmmurad/arc-agi-3-lb-0-86-3rd-place-candidate-milestone))

### Timeline

There are 39 UTC days from Sep 25 to Nov 2, so at most **39 scored submissions**. The table below is **[Inference]** built on the sourced constraints.

| Window | Goal | Concrete actions | Submissions |
|---|---|---|---|
| Sep 25–29 | Robust Milestone #2 candidate | Rank 1 and 2 on Sep 25; ranks 3–6 on Sep 26; repeat the best configuration Sep 27–28; submit the final M2 candidate **by Sep 29**, because a 9-hour run plus queues of up to 12 h can miss a Sep 30 deadline, and it is unconfirmed whether scoring must finish before the deadline ([705043](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705043)) | ~5 |
| Sep 30 | Publish or hold | If publishing, publish the notebook plus wheelhouse, weights and any adapters as public datasets under CC-BY 4.0 (dual-licensed MIT-0) 1–2 h before 23:59 UTC | 0–1 |
| Oct 1–7 | Measurement infrastructure | Competition-mode server; 110-slot simulator; 40–60-game held-out set with trivial-baseline filters; paired ≥4-pass runner on rented Blackwell or H100 GPUs; metrics dashboard; rank 7 | ~5 (calibration) |
| Oct 8–14 | Memory A/Bs | Ranks 8 and 9 against the rank 1–7 build; confirm any winner on the LB only if it exceeds ~50% locally | ~7 |
| Oct 15–21 | Supervisor, tools, training | Rank 10; rank 12 as a separate "ambitious" arm; rank 11 if external compute exists | ~7 |
| Oct 22–26 | Freeze architecture | Settle the team and merges and accept the rules **before 11:59 UTC Oct 26**; make public any notebook the Paper Track needs before publishing closes | ~5 |
| Oct 27–Nov 1 | Variance and robustness | Submit the two finalist configurations repeatedly (≥3 draws each); fix any infrastructure failure; pick the finals by Nov 1 | ~6 |
| Nov 2 | Final selection | Select two; keep the day as a buffer, not a work day | 0–1 |
| Nov 3–8 | Paper Track and release | ≤1,500-word writeup by Nov 8; prepare the CC-BY/MIT-0 release and the winner documentation | none |

### Milestone #2: publish or hold

**[Inference]** Tufa and NVARC3 will not publish ([742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801)), but Tong Hui Kang (15.02) will "very likely" publish if no higher team does ([742935](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742935)), and public notebooks at 4.50 already exist. A Milestone #2 prize is therefore realistic only if your public score beats the best score that will be open-sourced, which may be ~15. Publishing also hands your improvements to 3,300 teams before the final, which is Tufa's stated reason for holding back ("we worry it may not be possible to beat the best of 4000 copies"). Publish at Milestone #2 only if you are above the likely best open-sourced score. Otherwise hold, and put the week into the final.

### Choosing the two final submissions

Private scores are fixed when each run happens ([discussion 729985](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/729985)), and the rules allow up to two final selections from your submissions ([Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)). **[Inference]** Choose:
- a **safe** configuration: the highest mean across at least three LB draws with no infrastructure failure;
- an **ambitious** configuration: the best held-out local score, with at least two clean LB draws.

Among several runs of the same configuration, prefer the one with the higher public score. Public and private games differ, so a lucky public draw says nothing about private luck. But slowdowns and timeouts hit both halves of a run together, so a healthy public score is weak evidence of a healthy run.

## Where the sources disagree, and which figures are superseded

| Topic | Conflicting statements | Resolution used here |
|---|---|---|
| Milestone prize split | Kaggle rules: $25K / $7.5K / $5K; arcprize.org: $25K / $10K / $2.5K | Kaggle rules are legally binding |
| Daily submission cap | Starter README and one competitor repo: 5/day; settings, rules and staff: 1/day | 1/day (the 5/day setting was a May 27–Jun 8 mistake) |
| Runtime | Competitor repos and secondary coverage: unconfirmed; Tufa framework default: 12 h | 9 h from the settings and host; 12 h is a self-imposed soft budget |
| Number of games scored | "55-game private evaluation" (AERA, some repos) vs 110 | All 110 are played; 55 drive the public LB and 55 the final |
| Scoring | Paper v1 and the Kaggle data page: `min(1, h/a)²`, second-best human, 5× cutoff; code and host: `min(115, 100(h/a)²)`, upper-median human, 100% game cap, no 5× cap on Kaggle | Code and host govern Kaggle. The paper caps the ratio *before* squaring (max 1.3225); the code caps *after* (max 1.15) |
| Dead clicks | Scoring docs: operations that "do not alter the environment" are not counted; no ruling found in some write-ups | The host confirmed they count ([718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638)) |
| Entry deadline time | Timeline text: 11:59 PM; settings JSON: 11:59 AM on Oct 26 | Treat 11:59 AM UTC as the cutoff |
| Paper Track deadline | Kaggle: Nov 9; arcprize.org: Nov 8 | Plan for Nov 8 |
| Winner license | Kaggle: CC-BY 4.0; arcprize.org: CC0/MIT-0 | Dual-license your own code |
| Tufa's Milestone #1 score | 1.21 official; 1.30 retracted; 1.25 notebook best; 1.03 (AlphaSignal); 1.60 | 1.21 is the LB score; 1.60 is the local public-25 mean over 20 passes |
| Best model | Model-card and benchmark analysis: Qwen3.8-27B primary, Flash-Next "high-risk"; Kaggle evidence: every top public fork uses Flash-Next NVFP4 | The Kaggle evidence wins for score; keep 27B as the license fallback |
| Fine-tuning evidence | Competitor-repo survey: no fine-tuned result reported; Kaggle discussion: STaR LoRA 1.25 → 1.94 | Positive but contested evidence exists |
| MTP | Recommended at depth 2–3; Flash-Next profile did better with MTP off; newer vLLM + MTP also won | Depends on KV headroom; measure at real concurrency |
| Concurrency | Saturation beyond 16 vs 28 sequences working in B81 | Measure on your build |
| Context length | 32–64K suggested vs 64K measured to hurt | Keep a 32K working window |
| Executable World Models baseline | 58.12 / 15 wins (paper) vs 63.8 / 14 (cited by OPINE, Twin) | Different runs; cite both with provenance |
| Astra standard harness | 62.7 (ARC Prize blog) vs "66%" (Chollet on X, snippet) | 62.7 (primary blog) |
| PRO-LONG log ablation | 41.2 vs 24.0 with and without the log vs "19.9 vs 24.0" | Direction is consistent (the log matters); magnitude unresolved |
| AERA claims | "RHAE 0.30 on the full 55-game private evaluation"; 10 games solved in one blind step | Actually 0.30% public LB from a BFS kernel; its scoring is non-standard, so its trivial-solve claims are unreliable |
| Twin sp80 score | 82.1 vs 81.2 in two notes | Minor; immaterial |
| Human testers | 486 (paper) vs 458 (human-dataset blog) | Different counting windows; immaterial |

An earlier version of this analysis contained figures that the current evidence replaces:

| Earlier figure | Corrected figure |
|---|---|
| "Kaggle scores are still tiny… small, real gains are enough to place"; top scores ~1–2% | Milestone #1 was won at **1.21**. On 2026-09-25 the public LB top is **19.45**, nine teams are ≥10, 49 are ≥5, and rank 100 is 4.32 ([leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard)) |
| Duck "scored about 1.2–1.6%" | 1.21 on the LB; 1.60 was a local public-25 mean |
| Milestone prizes $25K / $10K / $2.5K | $25K / $7.5K / $5K under the Kaggle rules |
| Runtime and daily cap "not confirmed"; "RTX 6000" | 9 h, 1/day, 2 finals; the card is an RTX PRO 6000 Blackwell with 96 GB |
| "55 fully private games (the ones Kaggle scores)" | Each run plays 110 games; 55 → public LB, 55 → final; private scores are fixed at run time |
| Level score `min(1.15, (h/a)²)` with the "second-best human" | `min(115, 100(h/a)²)` against the upper-median human, plus a completion cap per game |
| OPINE-World's 78.4 is the state of the art | Twin 93.3, Tycho 100.00, EWM v1.6 98.97 (all public-set, frontier models) |
| AERA shows many public games fall to trivial strategies | AERA's scoring and win detection are unreliable; the "poor proxy" conclusion stands, supported by the design statements and the local → LB data |
| OpenAI tripled "GPT-5.x" scores 13.3 → 38.3 | GPT-5.6 Sol on the public set, with ~6× fewer output tokens |
| A world-model synthesizer + verifier + planner as the core build by Oct 20 | No open-weight evidence and ~100× over budget; demoted to an opt-in ambitious arm (rank 12) |
| "Add a numpy explorer layer… likely beats M1 scores"; recommended model Qwen 3.6 27B | Milestone #1 scores are irrelevant now; the baseline is Duck + Flash-Next at 3.4–4.5, and non-LLM layers are unproven on top of it |

## Conclusion

The competition has turned into a race of weights and systems run under a fixed token budget. What decides placement is what can be done with about 70–120K generated tokens per game on one Blackwell card. Recipes that work with frontier budgets 100× larger do not decide it. The depth arithmetic makes the target concrete **[Inference]**: if the hidden games resemble the public level mix, a leaderboard score above ~3.5% is impossible without level-2+ clears, and ~19% needs roughly three near-human levels on most hidden games. The capability that matters most is therefore carrying a correct theory from one level to the next. That is exactly what the Duck's FIFO eviction and hidden-reasoning loss break, and exactly what retained reasoning, compaction and lossless logs repaired for frontier models, tripling scores with fewer tokens. **[Inference]** Memory is the most under-exploited lever relative to its evidence. Fine-tuning on diverse synthetic mechanics is the most plausible explanation for the private gap between ~4.5% and ~19%.

Because the leaderboard shows the maximum over draws that vary by ±50%, and final scores come from two selections fixed at run time, discipline counts as much as ideas. A team that can measure small effects on held-out games, never loses a draw to infrastructure, and chooses its finals on repeated evidence can gain several places without a new trick. A team that tunes on the public-25 will be misled by it. The honest bottom line is this. Reproducing the public state of the art (~4–5%) is a few days' work. Reaching the prize zone (~16–20%+) requires rediscovering what the top five have not disclosed. The strongest bets are memory repair, self-trajectory training and throughput, tested on games the agent has never seen.
