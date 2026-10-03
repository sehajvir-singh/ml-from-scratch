# ARC-AGI-3 Kaggle agent: Milestone #2 build and runbook

This folder builds the Kaggle notebooks we submit to
[ARC Prize 2026 – ARC-AGI-3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3).

We did not write a new solver. We start from the strongest openly licensed public build and add three small,
tested patches ("grafts"). The research behind this choice is in
[`../../reports/ARC AGI 3 winning strategy.md`](../../reports/ARC%20AGI%203%20winning%20strategy.md).

## What we submit

| Variant | What it is | Why |
|---|---|---|
| `base` | Thuitanium's **B81** build, unchanged. That is Tufa Labs' Duck harness with the animation-aware solver, running Qwen3.8-Flash-Next NVFP4 on vLLM with KV cache 7 GiB, speculative decoding (MTP) off and 28 concurrent requests. | Best measured public build: four hidden-set draws of 4.50 / 3.86 / 3.03 / 5.36 (mean 4.19). It is our control and our fallback. |
| `m2` | `base` plus three grafts in cell 9 (below). | The Milestone #2 candidate. |

The three grafts, all in [`grafts/`](grafts/) and all fail-open (if one hits an error, the turn goes on unchanged):

1. **`note_fill.py`**. The harness carries a "working world model" note from turn to turn, but it only fills
   that note from the model's visible text. Flash-Next usually thinks and then calls the tool with no visible
   text, so the note stayed empty for whole games. This graft fills empty slots from the model's reasoning,
   capped at 488 characters. It is adapted from Thuitanium's `thui-a10` (MIT-0), which already ran cleanly on
   Kaggle.
2. **`prompt_extras.py`**, which adds two short lines to each turn's prompt:
   - **Scoring.** The exact scoring rule. The harness never states it, and it matters because dead clicks and
     RESETs count as actions.
   - **Pacing.** Minutes left for this game and actions spent on this level, plus a nudge to change hypothesis
     after 150 actions on one level.
3. **Click candidates** (also in `prompt_extras.py`). When MOUSE is a valid action, the prompt lists up to 8
   salient objects with their center cells. It leaves out backgrounds and thin HUD bars along the edges. It
   also leaves out object classes that were clicked 2+ times on this level with no visible change, and names
   those classes instead.

   Together, patches 2 and 3 match the one prompt change with published hidden-set evidence: 1.12 → 1.43 on a
   27B build (Kaggle discussion 743060).

What the patches cost: about 150–180 extra prompt tokens per turn, under 1% of a typical request.

**Honest expectation:** these are small levers. The run-to-run noise of one hidden draw is about ±50%. Every
"harness trick" the community has measured on this chassis was within noise, and only model changes moved
scores 2–3×. `m2` should do no worse than `base` and may do a little better. It will not reach the 15–19%
the top teams have.

## Verified offline (0 GPU)

- `python3 -m unittest discover -s arc-prize-2026/agent/tests -v` (11 tests):
  - Builds every variant and checks that only the intended notebook cells change. The scored rerun branch is
    never touched by the smoke option.
  - Installs the grafts **from the built notebook** onto the real solver code. That code is vendored in
    `vendor/anim_solver`, copied from Thuitanium's `localrig` (which says it is the exact anim bundle source).
  - Drives the grafts through `ToolAgent.analyze()` with a scripted model, running the real python-tool sandbox.
- `tools/e2e_mock.py`: runs the **full solver on real public games** with a mock model that plays random valid
  actions. It runs in TAAF's local competition-Arcade simulator. Last run: 4 games (ls20, vc33, ft09, tn36),
  160 model calls, click candidates on all 3 click games, the dead-click filter fired 37 times, and 0 graft
  errors. (The mock scores 0; this checks mechanics only.)

What is **not** verified here: anything on the Kaggle GPU. Phase A (below) is where the real model runs for the
first time. Every graft asserts its hook points at import, so if the Kaggle bundle's code differed, cell 9
would fail loudly in Phase A, before you could submit.

## Runbook: from zero to a scored submission

**One-time setup:**
1. Use a Kaggle account that is **phone-verified** (needed for GPUs), and accept the competition rules on the
   competition page.
2. Install the CLI with `pip install kaggle`. Create an API token (Kaggle → Settings → API → Create New Token)
   and save it to `~/.kaggle/kaggle.json` with `chmod 600`.
3. Check your GPU quota: Kaggle → Settings → Quotas. The RTX Pro 6000 draws on the weekly GPU quota, about 30 h.

**Each build:**
```bash
cd arc-prize-2026/agent
python3 build_notebook.py --variant m2 --owner <your-kaggle-username> --phase-a smoke --run 1
kaggle kernels push -p out/arc3-m2-smoke-r1
```
- `--phase-a smoke` makes the required "Save & Run" play 3 public games for 30 min each, about 0.6 GPU-hours.
  `--phase-a full` plays all 25 public games at the real clock, about 2.3 GPU-hours, and prints a public-25
  score.
- Either way, **the scored rerun is identical**: every hidden game at 7,920 s, 28 at a time.
- The push attaches the model, the vLLM runtime and the solver datasets listed in `kernel-metadata.json`, on
  the RTX Pro 6000, with internet off. If the push complains about the pinned `docker_image`, delete that one
  line from `kernel-metadata.json` and push again.

**Check Phase A.** Open the notebook on Kaggle and wait for the run to finish. The log must contain all of:
`THUI_A5_PROFILE ok`, `THUI_ANIMFAST_GRAFT ok`, `OURS_NOTE_FILL ok`, `OURS_PROMPT_EXTRAS ok`, `OURS_GRAFTS ok`,
`OURS_SMOKE 3 games` (smoke only), and no traceback in cell 15. For a full Phase A you also get a
`PUBLIC25_AUDIT` line, and `score.json` appears in the output.

**Submit.** On the notebook page, click **Submit to Competition** and pick `submission.parquet`. You get one
submission per UTC day. A scored run takes up to ~9 h, and RTX queues have been as long as 12 h.

**Record it.** Add a row to [`LEDGER.md`](LEDGER.md) with the date, variant, kernel version, Phase A result
and hidden score.

## Plan to Milestone #2 (Sep 30, 23:59 UTC)

| UTC day | Submit | Note |
|---|---|---|
| Sep 25–26 | `m2` (smoke Phase A) | First real run of the grafts. If Phase A fails, submit `base` instead and send me the log. |
| Sep 27 | `m2` again | The leaderboard shows your **best** draw, so more draws of the best config help. |
| Sep 28 | `m2`, or `base` if `m2` looked broken | Last comfortable slot. |
| Sep 29 | `m2` | Final candidate. It must be submitted by Sep 29, because a 9 h run plus a queue can miss Sep 30. |
| Sep 30 | Decide whether to publish | See below. |

**Publish or hold.** The Milestone #2 prize goes to the best **open-sourced** notebooks on the public
leaderboard. To qualify:
- Make the notebook **public** before 23:59 UTC Sep 30.
- License it under **CC-BY 4.0**. Our own code is also MIT-0.
- Keep the datasets it attaches public. They already are.

Tong Hui Kang (about 15%) said he will likely publish. If our score is far below the best notebook likely to
be published, publishing gains nothing and gives our work to 3,000 teams. So publish only if we are in range.

## Files

| Path | What |
|---|---|
| `build_notebook.py` | Builds `out/<slug>/` (notebook + `kernel-metadata.json`). Checks that the vendored base is byte-identical to B81 (sha256). |
| `grafts/` | Our patches, pasted into cell 9 after the solver import. |
| `vendor/b81/` | Thuitanium's B81 notebook and metadata (MIT-0). |
| `vendor/anim_solver/` | Solver source (Tufa Labs MIT + anim bundle CC0), used only by the offline tests. |
| `tests/test_grafts.py` | Offline tests (see above). |
| `tools/e2e_mock.py`, `tools/make_env_files.py` | Real-engine mock runs; builds the offline `environment_files/` tree. |
| `LEDGER.md` | One row per Kaggle submission. |

## Credits and licences

- Tufa Labs' Duck harness (MIT): Harold Bessis, Jeroen Cottaar, Isaiah Pressman, Andries Smit, Michal Tesnar,
  Stefano Viel.
- Animation-aware solver bundle by jakobbrggen (CC0).
- Serving stack by Keith Tyser.
- Notebook chassis, serving profile and the `thui-a10` note-fill idea by Thuitanium / Knowless Crew (MIT-0,
  `vendor/THUITANIUM-LICENSE-MIT0.txt`).
- Model: Qwen3.8-Flash-Next NVFP4 (Qwen Community License 1.0).
- Our code in `grafts/`, `tests/` and `tools/`, plus `build_notebook.py`: MIT-0 and CC-BY 4.0.
