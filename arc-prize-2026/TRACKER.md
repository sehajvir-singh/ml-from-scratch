# ARC-AGI-3 tracker

Updated: 2026-09-25 20:40 UTC. The per-submission log is [`agent/LEDGER.md`](agent/LEDGER.md).

## Deadlines

| Date (UTC) | What | Status |
|---|---|---|
| Sep 29 | Last safe day to submit the Milestone #2 candidate | Open |
| **Sep 30, 23:59** | Milestone #2: publish-or-hold decision (plan: hold) | Open |
| **Oct 26, 11:59** | Entry and team-merge deadline; make the Paper Track notebook public | Open |
| **Nov 2, 23:59** | Pick the 2 final submissions | Open |
| **Nov 8** | Paper Track write-up due | Open |

## Daily submissions (1 per UTC day)

| Day | Plan | Done? | Hidden score |
|---|---|---|---|
| Sep 25 | m2 smoke r1 | Submitted | **3.41** |
| Sep 26 | m2 (resubmit same version) | Submitted | **4.07** (best so far) |
| Sep 27 | **m3** (first draw of the keep-on-death build) | Submitted 07:05 UTC | **2.93** |
| Sep 28 | planned lean; **base (the census notebook) was submitted instead** | Submitted 12:54 UTC | **5.28** (best so far) |
| Sep 29 | **d2 v2** (lean + CNN learner + level carry; Depth Engine parts 1–2) | Submitted 13:53 UTC | pending |
| Sep 30 | **d3 v2** (d2 + stall breaker; parts 1–3), after its Phase A passes; watch whether Tong Hui Kang or others publish; hold ours | | |

## Leaderboard snapshot (2026-09-27 13:32 UTC, from the CLI download)

- **Us: rank 175 of 3,378 teams, 4.07** (team "Sehajvir singh").
- #1 Tufa Labs 27.29 (up from 18.81 on Sep 25), #2 Daniel Franzen 21.01 (up from 16.68). The top is moving fast.
- Check again with: `kaggle competitions leaderboard -c arc-prize-2026-arc-agi-3 --download -p lb`

## Leaderboard snapshot (2026-09-29, pasted by the user)

- #1 Tufa Labs **45.33** (27.29 on Sep 27, 18.81 on Sep 25), #2 Yi-Chia Chen 36.73, #3 Daniel Franzen 26.55,
  #4 Lord Han Solo 22.24, #5 Tong Hui Kang 20.53. On the depth ladder, 45 is roughly 4–5 levels cleared in every game.
- **Us: rank 55** with 5.28 (up from 175 at 4.07 on Sep 27).
- Milestone #2 closes Sep 30. If the winners publish as the Milestone #1 winners did, adopt their notebook
  immediately (`tools/adopt.py`) and put the Depth Engine on top.

## Milestone #2 releases (2026-10-01)

- Published: Franzen 27.89, Lord Han Solo 23.84, sirikilohit 22.53. Tufa and Yi-Chia Chen did not publish.
  Notes are in `research_notes/milestone2_releases_2026-10-01.md`.
- **Next submission: Franzen's notebook unchanged** (`dfranzen/arc-agi-3-milestone-2-solution`). Our grafts do not
  port: he switched the world-model note off and already has border-aware change detection and a stall-aware
  scheduler.

## Build status

- [x] Research reports: winning strategy, and path to the top five
- [x] m2 build: grafts, tests, go.py
- [x] First push to Kaggle
- [x] Grafts install on the real Kaggle GPU (all OURS_* markers ok)
- [x] Phase A completes (only the harmless upstream teardown Traceback)
- [x] First submission made
- [x] First hidden score recorded: 3.41
- [x] m3 build: m2 + keep-on-death graft (tested offline and on the real engine)
- [ ] fp8-KV / 3-wave build (needs the vLLM PR #55557 check)
- [x] Depth census launched (base, full 25-game Phase A, 2026-09-27)
- [x] d1 build: grafts/affordance.py, 3 offline tests; e2e on vc33/tn36/ls20 with a mock model: 593 actions observed, 65 trainings, 184 prompts with hints, 0 errors
- [x] d1 Phase A smoke on Kaggle: torch 2.13.0+cu130 present, learner loaded, hints shown on tn36 and vc33 (accuracy 87–93%); vc33 3/7 (21.43), tn36 1/7 (3.57), bp35 1/9 (0.90). Tweaked after: candidates at most 5% of the board, hints from about 40 actions
- [x] Paper Track draft v0.1 (`paper/DEPTH_THESIS_PAPER.md`); fill hidden-draw TODOs as scores land

## Open questions

- ~~Does PR #55557 change only Python code?~~ Answered 2026-09-26: Python plus a **Triton** kernel (`ops/qsa.py`), which is JIT-compiled, so no CUDA rebuild is needed. Flag: `--kv-cache-dtype fp8_e4m3`, in vLLM 0.30+. About 1.77x KV tokens; no RULER or tool-calling regression; about 7–11% slower with speculative decoding (B81 has MTP off). The runtime is a custom build, vLLM `0.1.dev20073+g8e685d198` (from the m3 Phase A log). Whether it includes the PR is unknown, so fp8 KV needs a patch plus a test, not just a flag. The same log shows the model uses 74.34 GiB, the KV cache 7 GiB, max_model_len is 32768, vLLM start-up takes 955 s, and m3's keep_on_death fired 10 times with 0 errors.
- How fast does the RTX Pro 6000 use up the weekly Kaggle GPU quota?
- Teammates: each one adds about 30 GPU-hours a week. Merges close Oct 26.
