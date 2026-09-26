# Submission ledger

We get one scored submission per UTC day, and a single hidden draw varies by about ±50%. So record every run
here, and never judge a change from one draw.

| UTC date | Variant | Kernel (owner/slug, version) | Phase A (smoke/full, OK?) | Public-25 score (full only) | Hidden LB score | Notes |
|---|---|---|---|---|---|---|
| 2026-09-25 | m2 | hackersinghrai/arc3-m2-smoke-r1, v1 | smoke OK: 3 games @1800 s: vc33 3/7 (21.43), tn36 1/7 (3.57), bp35 1/9 (0.56); 5 levels, 225 actions; note-fill 10/166, 0 errors. The teardown Traceback is the known upstream one | smoke mean 8.52 (3 games, not comparable to the full 25) | **3.41** | Submitted 2026-09-25 ~21:00 UTC. Scored run succeeded. Inside the B81 range (3.03–5.36) |
| 2026-09-26 | m2 | hackersinghrai/arc3-m2-smoke-r1, v1 (resubmit) | same notebook as above | – | **4.07** | Second draw of the identical notebook: +0.66 is pure run-to-run noise. m2 mean of 2 draws = 3.74 (B81 mean of 4 = 4.19) |
| 2026-09-27 (planned) | m3 | hackersinghrai/arc3-m3-smoke-r1, v1 | smoke OK: vc33 3/7 (21.43), tn36 1/7 (3.57), bp35 1/9 (1.25; L1 in 28 actions vs 42 on m2); all 4 OURS_* markers incl. KEEP_ON_DEATH and variant=m3 | smoke mean 8.75 (noise-level vs m2 8.52) | – | Phase A finished 2026-09-26 ~14:20 user time. Submit after 00:00 UTC Sep 27 |

External reference draws on the same chassis:
- B81, as reported by Thuitanium via tantan0327's SOLUTION.md: 4.50, 3.86, 3.03, 5.36.
- B81 plus note fill (Thuitanium `thui-a10`, one draw): 3.03.
