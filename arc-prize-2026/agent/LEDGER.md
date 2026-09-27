# Submission ledger

We get one scored submission per UTC day, and a single hidden draw varies by about ±50%. So record every run
here, and never judge a change from one draw.

| UTC date | Variant | Kernel (owner/slug, version) | Phase A (smoke/full, OK?) | Public-25 score (full only) | Hidden LB score | Notes |
|---|---|---|---|---|---|---|
| 2026-09-25 | m2 | hackersinghrai/arc3-m2-smoke-r1, v1 | smoke OK: 3 games @1800 s: vc33 3/7 (21.43), tn36 1/7 (3.57), bp35 1/9 (0.56); 5 levels, 225 actions; note-fill 10/166, 0 errors. The teardown Traceback is the known upstream one | smoke mean 8.52 (3 games, not comparable to the full 25) | **3.41** | Submitted 2026-09-25 ~21:00 UTC. Scored run succeeded. Inside the B81 range (3.03–5.36) |
| 2026-09-26 | m2 | hackersinghrai/arc3-m2-smoke-r1, v1 (resubmit) | same notebook as above | – | **4.07** | Second draw of the identical notebook: +0.66 is pure run-to-run noise. m2 mean of 2 draws = 3.74 (B81 mean of 4 = 4.19) |
| 2026-09-27 | m3 | hackersinghrai/arc3-m3-smoke-r1, v1 | smoke OK: vc33 3/7 (21.43), tn36 1/7 (3.57), bp35 1/9 (1.25; L1 in 28 actions vs 42 on m2); all 4 OURS_* markers incl. KEEP_ON_DEATH and variant=m3 | smoke mean 8.75 (noise-level vs m2 8.52) | **2.93** | Submitted 2026-09-27 07:05 UTC (ref 56601461). The m-series (prompt extras) now reads 3.41 / 4.07 / 2.93, mean 3.47, below B81's 4.19: consistent with Tufa's "extra tools hurt" |
| 2026-09-29 (planned) | d1 | hackersinghrai/arc3-d1-smoke-r1, v1 | smoke OK: vc33 3/7 (21.43), tn36 1/7 (3.57), bp35 1/9 (0.90); OURS_AFFORDANCE ok (torch 2.13.0+cu130); hints on tn36 and vc33 | – | – | v1 predates the candidate-size and earlier-hint tweak; push v2 before submitting |
| 2026-09-27 (test only) | base | hackersinghrai/arc3-base-full-r1, v1 | **full 25-game census** at 7,920 s per game: public-25 mean 8.24, median 3.57; levels cleared 0:3, 1:12, 2:4, 3:2, 4:4 games; all 25 ended on the clock | 8.24 | – | Data in research_notes/census/. Not submitted |
| 2026-09-30 (planned) | d2 | hackersinghrai/arc3-d2-smoke-r1, v1 | smoke OK: tn36 **2/7 (10.71)**, the first time any run cleared 2 levels there; vc33 3/7 (20.47); bp35 0/9 (0.00); all markers incl. OURS_LEVEL_CARRY | smoke mean 10.39 (m2 8.52, m3 8.75, d1 8.63; noise-level with 3 games) | – | Re-push after the affordance tweak before submitting |

External reference draws on the same chassis:
- B81, as reported by Thuitanium via tantan0327's SOLUTION.md: 4.50, 3.86, 3.03, 5.36.
- B81 plus note fill (Thuitanium `thui-a10`, one draw): 3.03.
