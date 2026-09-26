# Handoff prompt: ARC Prize 2026 – ARC-AGI-3 (paste everything below into another AI assistant)

---

You are helping me compete in the Kaggle competition **ARC Prize 2026 – ARC-AGI-3**
(https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3).

Please be honest: separate verified facts from guesses, and don't promise wins.
Everything below is the state as of **2026-09-26**.

## 1. The competition (verified)

**What agents do**
- Agents play **interactive, turn-based grid games** (64×64 grid, 16 colours) with no instructions.
- Actions:
  - ACTION1–4: up/down/left/right
  - ACTION5: interact
  - ACTION6: click (x, y)
  - ACTION7: undo in some games
  - RESET
- Each game has ≥6 levels.

**Scoring**
- Per level: `min(1.15, (human_actions / agent_actions)^2)`.
- Level *k* has weight *k*.
- An uncleared level scores 0.
- Every executed action counts, including clicks that change nothing and RESET.

**Kaggle setup**
- A notebook-only code competition.
- One RTX Pro 6000 Blackwell (96 GB), a **9-hour** limit, **no internet**.
- 1 submission per UTC day; 2 final selections.
- Every submission plays **110 hidden games**:
  - 55 drive the public leaderboard;
  - 55 drive the final private leaderboard.

**How a submission runs**
- **Phase A:** Kaggle's "Save & Run All" must succeed first (offline, on the public games).
- **Phase B:** the scored rerun, which talks to a gateway at `http://gateway:8001`.

**Dates (UTC)**

| Date | What |
|---|---|
| Sep 30 | Milestone #2 |
| Oct 26, 11:59 | Entry and team-merge deadline |
| Nov 2 | Final submission deadline |
| Nov 8 | Paper Track deadline (Kaggle says Nov 9) |
| Dec 4 | Results |

**Prizes**
- Final: $40K / $15K / $10K / $5K / $5K.
- Milestones: $25K / $7.5K / $5K (per the Kaggle rules).
- Paper Track: $50K / $20K / $5K, plus a $375K pool shared by papers rated above 4.5/5.
- Winners must open-source their code (CC-BY 4.0).

## 2. Leaderboard (2026-09-25)

| Rank | Team | Score |
|---|---|---|
| 1 | Lord Han Solo | 19.45 |
| 2 | Tufa Labs | 18.81 |
| 3 | Yi-Chia Chen | 18.63 |
| 4 | Daniel Franzen | 16.68 |
| 5 | NVARC3 (NVIDIA) | 16.07 |
| 6 | Tong Hui Kang | 15.02 |

- The best **public** notebooks score about 4.5.
- The median team is about 0.3 (3,320 teams).

**Verified about the top teams**
- None has published its method.
- NVARC3 runs Qwen3.8-Flash-Next on a vLLM fork with an **fp8 KV cache**. Their team leader wrote vLLM PR #55557,
  merged Sep 16, which gives about 1.77× more KV capacity.
- Tufa Labs forked RL/post-training repos (miles, verl, sglang, vLLM) on Sep 9, between their 11.04 and 18.81 scores.
  The forks contain no visible changes of their own.
- One competitor trained Flash-Next with RL on a rented H200 node and got **no gain**. They said the RTX 6000 Pro
  can't train ~100B models.

**Not verified (guesses)**
- That the top teams fine-tuned or rented GPUs.
- What Lord Han Solo and Franzen do.
- Tong Hui Kang said he will "very likely" publish at Milestone #2 if no higher team does.

## 3. What we built

GitHub repo `sehajvir-singh/ml-from-scratch`, branch `claude/arc-prize-2026-research-bribdf`.

**Base**
- Thuitanium's public **B81** notebook (MIT-0): Tufa Labs' Duck harness plus the animation-aware solver
  (jakobbrggen, CC0).
- It serves Qwen3.8-Flash-Next NVFP4 with vLLM (KV cache 7 GiB, MTP off, 28 concurrent requests).
- Known B81 hidden scores: 4.50, 3.86, 3.03, 5.36.

**Our grafts** (code pasted into notebook cell 9; each fails open)

| Graft | What it does |
|---|---|
| `note_fill.py` | Fills the harness's "working world model" note from the model's reasoning when its visible reply is empty (adapted from Thuitanium a10) |
| `prompt_extras.py` | Adds the exact scoring rule, time left per game and actions spent on the level; adds up to 8 salient non-HUD click candidates; drops object classes clicked 2+ times with no visible change |
| `keep_on_death.py` | (m3 only) Keeps the world-model note across a GAME_OVER on the same level; still wipes on a real level change |

**Variants**
- `base` = B81 unchanged.
- `m2` = B81 + note_fill + prompt_extras.
- `m3` = m2 + keep_on_death.

**Tools** (in `arc-prize-2026/agent/`)

| File | Purpose |
|---|---|
| `build_notebook.py` | Builds a variant into `out/<slug>/` |
| `go.py` | Builds, pushes to Kaggle and watches Phase A |
| `tools/adopt.py` | Pulls a published notebook and adds our grafts |
| `tools/e2e_mock.py` | Runs the real solver on real games with a mock model |
| `tests/test_grafts.py` | 12 offline tests |

**Docs**

| File | Contents |
|---|---|
| `reports/ARC AGI 3 winning strategy.md` | Main research report |
| `reports/ARC AGI 3 path to top five.md` | Follow-up on reaching the top 5, with odds |
| `research_notes/` | Source notes behind the reports |
| `arc-prize-2026/TRACKER.md` | Deadlines and status |
| `arc-prize-2026/agent/LEDGER.md` | Every submission |
| `arc-prize-2026/OCTOBER_PLAN.md` | October plan |
| `arc-prize-2026/TRAINING_PLAN.md` | Training plan (needs money we don't have) |

## 4. Results so far

- **m2 Phase A on Kaggle** (3 games at 1,800 s):
  - vc33 3/7 levels, tn36 1/7, bp35 1/9;
  - all graft markers OK, 0 graft errors;
  - the only Traceback is a known harmless one in `serving_teardown.py`.
- **m2 hidden score, submission 1: 3.41.** That is inside B81's normal range.
- m2 submission 2: running (Sep 26).
- m3: pushed as `hackersinghrai/arc3-m3-smoke-r1`, Phase A running. Submit it Sep 27 UTC.

## 5. Key lessons (evidence-based)

- One hidden draw varies by about ±50%, so never judge a change from one run.
- Local public-25 scores don't predict the leaderboard.
- Community tests found these did **not** help:
  - 64K context;
  - lower temperature;
  - genre playbooks;
  - multi-agent roles;
  - more KV alone;
  - prefix caching;
  - model swaps (Qwen3.5-122B scored 0 levels).
- Only model upgrades moved scores 2–3×.
- **Fine-tuning Flash-Next on Kaggle is not feasible:** the weights take about 82 GB of 96 GB, and no tool
  supports it. A Qwen3.8-27B LoRA fits on Kaggle but starts at about 1.5% (vs about 4%), and one team's attempt
  got worse.

## 6. Constraints and decisions

- **No money:** Kaggle GPUs only, no rented GPUs.
- The user runs everything from a Mac using the **fish** shell and the `kaggle` CLI. Kaggle username: `hackersinghrai`.
- The AI assistant cannot log in to Kaggle; the user pushes and submits.

## 7. Daily commands

```fish
cd ~/ml-from-scratch; git pull; cd arc-prize-2026/agent
python3 go.py --variant m3            # build + push + watch Phase A (use m2 / m3 / base)
kaggle competitions submit -c arc-prize-2026-arc-agi-3 -f submission.parquet -k hackersinghrai/arc3-m3-smoke-r1 -v 1 -m "m3 r1"
kaggle competitions submissions -c arc-prize-2026-arc-agi-3
python3 tools/adopt.py <owner>/<notebook>   # adopt a newly published top notebook
```

## 8. Plan

| When | Action |
|---|---|
| Sep 27 | Submit m3 |
| Sep 28 | Submit m2 |
| Sep 29 | Submit m3 (alternating, for a fair A/B) |
| Sep 30 | Check the Code tab for top notebooks published at Milestone #2; adopt immediately with `adopt.py`; don't publish ours unless we're competitive |
| October | Speed build: fp8 KV (PR #55557) + 3 waves instead of 4; paired A/B testing; look for teammates (merges close Oct 26) |
| Nov 2 | Pick 2 final submissions (one safe, one ambitious) |
| By Nov 8 | Paper Track write-up (≤1,500 words + public notebook). This is our best prize chance, because it's judged on quality, not score |

## 9. Honest odds (our estimates)

| Outcome | Chance |
|---|---|
| Top 5 | about 1% |
| Top 100 | about 25% |
| Best score of 5% or more | about 50% |
| Paper Track top 3 | about 3–5% |

## 10. What I want from you

- Help me carry this plan out.
- Check each Kaggle log I paste.
- Keep the ledger honest.
- Suggest free, testable improvements.
- Help write the Paper Track paper.
- Ask me for missing details rather than guessing.
