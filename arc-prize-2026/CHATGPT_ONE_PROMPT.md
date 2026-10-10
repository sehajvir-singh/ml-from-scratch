```
You are my research partner for the Kaggle competition "ARC Prize 2026 - ARC-AGI-3". I attached arc3-full-research.zip,
which is my full repo: code, notebook, logs summary and research. FIRST open the zip and list the main files you see.
Never say "no notebook was provided".

=== RULES ===
1. Label every claim VERIFIED (with a link or a zip file path) or GUESS. Never invent scores, team methods, PRs or notebooks.
   If you can't find something, write "not found".
2. Hard limits: Kaggle GPU only (1x RTX Pro 6000 Blackwell 96 GB, 9 h, no internet at run time), no money, no rented GPUs,
   1 submission per UTC day. Reject ideas that break these.
3. One hidden run swings about +-50%. Never call a change better from one score.
4. I use macOS with the fish shell. Commands must work in fish (no <placeholders>, no bash-only syntax).
5. Kaggle does NOT show logs from the hidden scored run. Only Phase A logs (3 public games) exist.
6. 27B models (Qwen3.6/3.8-27B, Gemma-4-31B) already scored about 1.4-2.6 on this leaderboard, against about 4 for our model.
   Don't propose them without new evidence. API models (GPT, Claude) can't run offline.

=== FACTS (as of 2026-09-26) ===
- Scoring per level: min(1.15, (human_actions/agent_actions)^2); level k has weight k; RESET and useless clicks count as actions.
  Each submission plays 110 hidden games (55 public LB, 55 private).
- Deadlines (UTC): Milestone #2 Sep 30 23:59; team merge Oct 26; final Nov 2; Paper Track Nov 8.
- Leaderboard: #1 Lord Han Solo 19.45, Tufa Labs 18.81, Yi-Chia Chen 18.63, Daniel Franzen 16.68, NVARC3 16.07,
  Tong Hui Kang 15.02. The best public notebooks score about 4.5.
- Our base: Thuitanium's public B81 notebook (Tufa Duck harness + animation solver, Qwen3.8-Flash-Next NVFP4 on vLLM).
  B81 hidden draws: 4.50, 3.86, 3.03, 5.36 (mean 4.19).
- Our variants (arc-prize-2026/agent/grafts/): m2 = B81 + note_fill + prompt_extras (scoring/pacing lines + click
  candidates); m3 = m2 + keep_on_death (keeps the world-model note after GAME_OVER on the same level).
- Our hidden scores: m2 3.41 and 4.07 (same notebook). m3 passed Phase A and will be submitted Sep 27.
  Phase A smoke results (per-level = agent actions / human actions) are in arc-prize-2026/agent/LEDGER.md.
- Known: Tufa's write-up says handcrafted tools hurt their agent. Our prompt_extras may do the same.
- Known: NVARC3 uses an fp8 KV cache (vLLM PR #55557, merged Sep 16). Fine-tuning Flash-Next on Kaggle is impossible
  (the weights take about 82 of 96 GB).

=== WHAT I WANT (answer all, in this order) ===
A. Top teams: search Kaggle discussions and Code, the arcprize.org blog, GitHub, X, arXiv and YouTube for how the 6 teams
   above work (model, serving, harness, training). Give links and a confidence level. What explains ~4 -> ~19?
B. New public notebooks: any Kaggle notebook or write-up since Sep 20 claiming LB > 5. Give the exact owner/slug, score,
   license and what differs from B81. Rank them by how fast I can adopt them (I have tools/adopt.py).
C. Speed: for vLLM PR #55557 (fp8 KV), is it Python-only or compiled kernels? Which vLLM release has it? Can it run
   offline inside B81's runtime? Give the exact flags for Flash-Next NVFP4 on 96 GB, the risks, and a 2-run test plan.
D. Code review: read grafts/note_fill.py, prompt_extras.py, keep_on_death.py and build_notebook.py. List real bugs or
   score risks as file, line, problem, minimal fix.
E. Levers: at most 5 ideas within the hard limits that have evidence of a gain of 20% or more. For each: evidence, expected
   gain, GPU hours, and a 1-2 submission test. Include per-game time budgeting (stop stalled games early) and a
   "lean" variant (note_fill only). Say plainly if you think nothing will beat noise.
F. Plan: a day-by-day plan from Sep 27 to Nov 2 (1 submission/day), plus a Paper Track outline (<=1,500 words, due Nov 8)
   titled "Measuring harness changes under +-50% draw noise on ARC-AGI-3", using only numbers from LEDGER.md.
G. A teammate recruiting post for Kaggle discussions. Be honest that our best score is 4.07.

End with: "Top 3 actions for tomorrow" (with fish commands) and "What would prove this plan wrong".
```
