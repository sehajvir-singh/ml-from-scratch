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
| Sep 25/26 | m2 smoke r1 | Phase A OK; submit next | – |
| Sep 27 | m2 | | |
| Sep 28 | m2 (or base if m2 is broken) | | |
| Sep 29 | m2 | | |
| Sep 30 | Watch whether Tong Hui Kang or others publish; hold ours | | |

## Build status

- [x] Research reports: winning strategy, and path to the top five
- [x] m2 build: grafts, tests, go.py
- [x] First push to Kaggle
- [x] Grafts install on the real Kaggle GPU (all OURS_* markers ok)
- [x] Phase A completes (only the harmless upstream teardown Traceback)
- [ ] First submission made
- [ ] First hidden score recorded
- [ ] fp8-KV / 3-wave build (needs the vLLM PR #55557 check)
- [ ] Paper Track draft

## Open questions

- Does PR #55557 change only Python code, or also compiled kernels? The answer decides whether we patch or rebuild the vLLM runtime.
- How fast does the RTX Pro 6000 use up the weekly Kaggle GPU quota?
- Teammates: each one adds about 30 GPU-hours a week. Merges close Oct 26.
