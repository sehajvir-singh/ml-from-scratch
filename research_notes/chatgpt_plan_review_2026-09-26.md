# Review of ChatGPT's "ARC_AGI3_Research_Plan_2026-09-26.md"

Reviewed 2026-09-26 against our repo, ledger and earlier research.

## Main problem
ChatGPT did not use our repo. It says "no user notebook, model, trace … was available" and asks for inputs we
already have: the notebook (`agent/vendor/b81`, `agent/build_notebook.py`), the model (Qwen3.8-Flash-Next NVFP4 on
vLLM), the hardware (RTX Pro 6000 96 GB; Kaggle's Phase A log shows it) and the fact that 4.07 is a Kaggle hidden-LB
score. So most of it is a generic plan, not a diagnosis of our system.

## Correct and useful
- **Tufa's own write-up says handcrafted tools hurt Duck.** Our `prompt_extras` graft adds hint text and click
  candidates, so it could hurt the same way. Our data so far fits this, though not significantly: m2 averages 3.74 over
  2 draws against B81's 4.19 over 4. Action: keep m3 on Sep 27. If m2 and m3 both average under 4.2 after 3 draws each,
  resubmit plain `base` and consider a lean variant (note_fill only, no prompt extras).
- **Time allocation across games (their E10)** is a real lever. The harness gives every game the same budget and
  gives up at the limit (`state=gave_up` in every smoke game).
- **Diagnose by per-level action counts.** Our Phase A logs already contain this (`per-level=agent/human`). For
  example, m3 vc33 level 4 took 107 actions against a human's 61, which scores (61/107)^2 = 0.33 on that level.
- **Deadlines** match ours: Sep 30 23:59 UTC, Oct 26, Nov 2. Their Rome times (Oct 1 01:59 CEST) are the same moment.

## Wrong or not applicable to us
- **"Send the logs from the 4.07 run."** Kaggle does not return logs from the hidden scored run (Phase B). Only
  Phase A logs on the public games exist. Diagnosis has to come from Phase A logs.
- **Model candidates Qwen3.6/3.8-27B and Gemma-4-31B.** On this competition's hidden set, 27B builds measured about
  1.4–2.6, against about 4 for Flash-Next (see `research_notes/ARC AGI 3 path to top five/model_alternatives.md`
  and the public Qwen3.8-27B journal, which peaked at LB 2.56). Swapping to them is a known regression.
- **GPT-6 Astra / NOOA / PRO-LONG scores** come from API models on public games. They can't run offline on Kaggle.
- **"Publish the milestone notebook by Sep 30."** This only matters for a team that could place in the top 3 of the
  milestone. At 4.07 we can't, so we keep our plan to hold.
- **Local scorer-version reconciliation.** Useful for local proxies, but our decisions use the hidden LB score,
  which Kaggle's own gateway computes.
- The kit's trace analyzer needs an adapter to our log format and is CPU-only. It is low priority, because our
  `[finished] … per-level=` lines already give per-level cost.

## What we take from it
1. Watch for "extra tools hurt". Add a `lean` variant (note_fill only) if m2/m3 keep averaging below B81.
2. Look into a time budget per game in October: stop early on stalled games and give the time to games that are
   making progress.
3. Next time, make ChatGPT read the zip first (updated in `arc-prize-2026/CHATGPT_PROMPTS.md`).
