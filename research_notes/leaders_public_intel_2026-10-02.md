# What the leaders are doing, from public sources only (2026-10-02)

Only public information is used here: blog posts, podcasts, the leaderboard and published papers. Private code and
data of other teams are off-limits.

## Leaderboard (search snapshot, 2026-10-02)
- **#1 Tufa Labs: 52.51, from 153 submissions.**
- **#2 Yi-Chia Chen: 48.07.**
- Us: 25.78 from 8 submissions.
- **The public leaderboard is computed on about 50% of the hidden test set.** The final ranking uses the rest, so
  places shift at the end and over-tuning to the public score is risky.

## Tufa Labs: public facts
- **Team:** Benjamin Crouzier (founder), Jeroen Cottaar, Dries Smit (author of StochasticGoose, the CNN+RL agent at
  12.58% in the preview), Stefano Viel, Michal Tešnar, Harold Bessis, Isaiah Pressman. A full research lab, 3rd in ARC
  Prize 2025.
- **Duck harness (their Milestone #1 post):**
  - The game is treated as a programming problem: observations become Python variables in a REPL.
  - Boards are shown as both images and text, and old messages are evicted to keep the context short.
  - It scored 1.60 ± 0.45 on the public 25 over 20 tries with Qwen3.6-27B.
  - Versus executable world models with GPT-5.4, it solves a similar set of games at about 10× lower cost. They
    conclude that **"model capability drives which games are solved; the harness drives cost."**
  - Next areas they named: **context management and perception.**
- **MLST podcast:**
  - The score measures action efficiency, not games solved.
  - **"Wrong-goal loops":** agents lock onto a wrong goal and cannot climb back out.
  - Also discussed: goal acquisition, two kinds of planning, why ARC-AGI-3 resists brute force.
- **Their real edge is iteration.** 153 submissions against our 8, plus a team running experiments every day. That is
  how 27 (Sep 27) became 45 (Sep 29) and then 52.5.
- **Our guess, not public:** they likely combine the same public ingredients (Flash-Next, long context with an FP8 KV
  cache, scheduling, perception and animation fixes) with many tuned harness changes and far more evaluation runs.

## Yi-Chia Chen
- No public write-up found.

## Frontier results (API models; not runnable on Kaggle, but they show what works)
- **Twin** (test-time executable world model, verified on all past transitions): 97.8% of public levels.
- **Prime Agent** (REPL, continual memory, sub-agents): 95.5%.
- **Agno "Learning Machines":**
  - The agent writes a per-game *manual* of mechanics, hazards and hypotheses, and revises wrong beliefs.
  - gpt-5.6 reached 100% on the public set "warm", i.e. reusing manuals from earlier runs.
  - Gemini-3.7-Flash using those manuals scored 96.42 with fewer tokens.
  - Warm reuse is impossible on the hidden set (new games). Within a game, though, a manual carried across levels is
    allowed, and it is the same idea as **solved-level memory**.

## What this means for us
1. The common thread is **evidence-based memory inside a game**, not advice:
   - solved-level memory (sirikilohit +2.8);
   - manuals that revise beliefs (Agno);
   - world models verified against the history (Twin).
2. **Wrong-goal loops** are Tufa's name for our census "thrashing". A verification line ("your model mismatches past
   step 17") is a concrete way out.
3. We cannot match Tufa's iteration speed. So test fewer, better-grounded ideas, and repeat each test before trusting
   it.
