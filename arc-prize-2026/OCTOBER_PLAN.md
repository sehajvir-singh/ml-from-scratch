# October plan: from ~4% toward the top 10, plus the Paper Track

*Written 2026-09-25. Evidence is in [`../reports/ARC AGI 3 winning strategy.md`](../reports/ARC%20AGI%203%20winning%20strategy.md)
and the notes in [`../research_notes/`](../research_notes/).*

## The one fact that sets the plan

The top five sit at 16–19%. The best public build (our `base`) is at about 4%. Every public harness tweak on
this chassis has measured within noise, and only model changes moved scores 2–3×. Tufa Labs went from 11% to
19% in one week with no new public model, which points to **fine-tuning or better data, not prompts**.
A byte-identical-fork team also measured that 98% of the decisions in a solving trajectory happen on a board
state never seen before in that game. So the ceiling is the model's reasoning on new boards.

That leaves two workstreams: **(A) train the model on its own successful play** and **(B) a measurement setup
honest enough to tell whether A worked**. Harness work goes only where it buys decisions per minute.

## Decision (2026-09-25): Kaggle GPUs only, no rented GPUs

What that means for the plan:
- **Serving model:** Flash-Next (~180B MoE) cannot be fine-tuned on the Kaggle card, so our served model stays
  untrained. Section A is on hold.
- **Our levers:**
  - daily `m2` draws, since the leaderboard shows the best draw;
  - harness A/Bs (section C), measured with the Phase A public-25 run plus a small held-out set that runs on
    Kaggle;
  - the Paper Track (section D), which does not require a high score.
- **Weekly GPU quota:** about 30 hours. Spend it on 1 smoke Phase A per day (~0.6 h each) and 2–3 full
  Phase A measurement runs per week (~2.3 h each).
- **Optional fine-tuning on Kaggle:** a QLoRA of Qwen3.8-27B fits one 96 GB card inside a 12 h session. But a
  27B build (1.43 hidden with fixes) starts well below Flash-Next (~4), so only try it if we have spare quota.
  Expect it to lose.

## A. Self-play fine-tuning (on hold: needs non-Kaggle GPUs for Flash-Next)

Goal: a LoRA on the model we serve, trained on verified winning trajectories. This is the STaR / rejection-
sampling recipe. On Qwen3.6-27B it went from 1.25 to 1.94 on the leaderboard (discussion 739047), and another
team reported 11.04 → 12.97 locally (discussion 732854).

1. **Model choice.**
   - Flash-Next (~180B MoE) cannot be trained on the Kaggle card, so it needs a rented H200/B200-class node.
   - Qwen3.8-27B (Apache-2.0, dense) can take a QLoRA on one 80–96 GB GPU.
   - Decide by budget. **This is the one decision only you can make: how much GPU money is available?**
     - With **no budget**, stay on the Flash-Next `m2` line and skip training.
     - With about **$300–1,000**, train a LoRA on 27B first. It is cheaper, and a 27B build with fixes
       already measured 1.43 hidden.
     - With **more**, train Flash-Next on rented H200s.
2. **Data.**
   - Play many games (public-25 plus synthetic, below) with the harness on rented GPUs.
   - Keep only turns from runs that **cleared a level**, taking the turns on the path to the clear.
   - The traces must come from the **same model** you fine-tune (discussion 732854), and the dataset must
     stay small: "naively scaling the data hurt".
3. **Rules check.**
   - Self-generated synthetic data is not yet ruled on by the host (discussion 742940). Ask in the forum
     before relying on it.
   - Publish the adapter weights as a public Kaggle model, as the open-source rule requires.
4. **Serving.** Load the adapter as a LoRA in vLLM on Kaggle. The Duck repo already ships a
   `vllm_runtime_lora_guard`.

## B. Measurement that predicts the hidden score

Local public-25 scores have run 2–4× above the leaderboard, sometimes with the ordering reversed. Build instead:

1. **A held-out set of 40–60 unseen games.**
   - Sources: `theredbluepill/arc-interactive` (249 games) and `sonpham-org/arc-3` (927 games).
   - Drop any game solved by random play, by repeating one action, or by clicking every object.
   - Set baselines at BFS-optimal × 1.5.
   - Lay the games out with `agent/tools/make_env_files.py` (same `environment_files/` format).
2. **Competition-faithful runs.** Use `--simulate-competition-arcade` (already exercised by `agent/tools/e2e_mock.py`)
   and the exact shipped scoring formula.
3. **Paired, multi-pass comparisons.**
   - At least 4 passes per game, the same games in both arms, and per-game sign tests.
   - Only send the leaderboard a change that wins by more than ~50% locally.
4. **Track what predicts the leaderboard:**
   - games with any level cleared;
   - games that cleared level 2 or later;
   - actions per game-hour;
   - share of games that end on the clock;
   - infrastructure failures.

## C. Harness changes worth testing (only against B)

| Change | Why | Risk |
|---|---|---|
| Chunked context eviction + a structured summary instead of dropping the oldest message each turn | Frontier harnesses gained 3× from keeping reasoning and compacting (OpenAI 13.3 → 38.3). The Duck's per-turn eviction breaks the prefix cache (hit rate 48.6%). | Thuitanium measured compaction variants as not distinguishable on this chassis |
| Reasoning-length control (compact prompt + per-call token cap) | 874 → 595 tokens per action, +43% actions per clock (sonpham) | Score gain unproven |
| Keep the world-model note across a GAME_OVER (Thuitanium B101) | Deaths currently wipe the note | Untested |

Rejected by existing evidence, so don't spend slots on them:
- 64K context;
- lower temperature;
- genre playbooks;
- multi-agent roles;
- hand-built tools;
- extra frames or video for the model.

## D. Paper Track (deadline Nov 8; plan for Nov 8, not Kaggle's Nov 9)

- **Format:** at most 1,500 words plus a public notebook. The code does not need to score well.
- **Prizes:** $50K / $20K / $5K, plus a $375K pool shared by papers rated above 4.5/5.
- **Working title:** "What moves the hidden score in ARC-AGI-3: a measured ledger of harness levers on an
  open-weight agent."
- **Outline:**
  1. **The problem.** Offline, one GPU, 110 games, 9 h. The scoring rule and why depth dominates. (200 words)
  2. **Base system and grafts.** The B81 chassis, and what each graft changes. (250 words)
  3. **Measurement.**
     - The held-out synthetic set and its trivial-baseline filter.
     - Paired multi-pass statistics.
     - How local results mapped to the leaderboard: our own ledger, plus published pairs. (400 words)
  4. **Results.** Which levers moved held-out and hidden scores and which were noise, including fine-tuning if
     A lands. (400 words)
  5. **Lessons.** Throughput versus reasoning ceiling, and why public-25 tuning misleads. (250 words)
- **Assets to collect from now on:** every `LEDGER.md` row, every Phase A log, and the held-out results.

## Timeline

| Dates | Work |
|---|---|
| Oct 1–7 | Build the B held-out set and runner. Rent a GPU for the paired runs. Start collecting A traces. |
| Oct 8–14 | First LoRA, if budget allows. A/B the C1 compaction. |
| Oct 15–21 | Confirm the best arm on the leaderboard (≥ 2 draws). |
| **Oct 26, before 11:59 UTC** | Accept the rules and finish any team merge. Make public anything the paper notebook needs. |
| Oct 27–Nov 1 | Submit the two finalists at least 3 times each. Pick one safe and one ambitious final by Nov 1. |
| Nov 3–8 | Write the paper. Release the code under CC-BY 4.0 / MIT-0. |
