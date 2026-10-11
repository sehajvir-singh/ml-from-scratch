# ARC-Scientist: a new agent design for small offline models (2026-10-02)

## The idea in one line
Do not ask a small LLM to *play* the game. Make it run the **scientific method**: propose rules, test them with
experiments, keep only rules verified against every past observation, then **plan inside the verified simulator**. The
model does the guessing, and code does the checking and the searching.

## Why this, and why now (evidence)
- **Frontier proof:** Twin (97.8% of public levels) and Prime Agent (95.5%) show that "write a world model, verify it
  against the history, plan in it" nearly solves ARC-AGI-3. They use large API models.
- **Small-model limit:** Tufa: "model capability drives which games are solved". A few-billion-active-parameter model
  writes buggy simulators from scratch.
- **The gap we target:** make simulator-writing easy enough for a small model. Give it a **library of verified
  mechanic building blocks** so it chooses and parameterizes instead of writing everything.
- **Supporting results:**
  - Evidence beats advice (sirikilohit, our m-series).
  - Memory inside a game across levels helps (+2.8 solved-level memory; Agno manuals).
  - Wrong-goal loops are the main failure (Tufa; our census thrashing).

## Architecture (5 parts)
1. **Perception → objects (exists).**
   - Franzen's harness already segments boards into objects with shape hashes and `frame_diff`.
2. **Mechanics library (new; the core invention).**
   - A small DSL of game primitives seen in the public games:
     - movement (player moves by a step, blocked by walls);
     - push;
     - collect or disappear on contact;
     - toggle or recolor on click;
     - counters and budget bars;
     - gravity or sliding;
     - teleport;
     - pattern copy;
     - win-on-overlap and win-on-match.
   - Each primitive is executable Python with parameters (which color is the player, which are walls, and so on).
3. **Hypothesis search with verification (new).**
   - Rule sets are generated two ways:
     - (a) by enumeration over the library, on CPU;
     - (b) by LLM proposals ("I think blue pushes yellow").
   - Each candidate is scored by replaying **all recorded transitions**.
   - Only the agent's top 1–3 *verified* rule sets and their first mismatch are shown to the LLM, as one short line.
     That is evidence, not advice.
4. **Experiment design (new).**
   - When rule sets disagree, pick the action whose outcome they disagree on most (information gain).
   - One experiment then rules out wrong hypotheses. This breaks wrong-goal loops directly.
5. **Planner + level manual.**
   - With a verified simulator, run BFS/beam search over action sequences toward the inferred goal.
   - This saves real actions, which raises the efficiency score.
   - Each cleared level's verified rules are pinned as the **manual** for the next level.

## Why it fits Kaggle
- Parts 2–5 are CPU code. The GPU stays with the LLM. The Kaggle machine has spare CPU cores during the run.
- The LLM output shrinks. It proposes rule names and parameters instead of long code, which means more turns per
  GPU-minute (throughput is the binding limit).

## The killer property: we can measure most of it without a GPU
- Run the public game engines locally on CPU with random or scripted play, record transitions, and measure:
  - **Coverage:** what share of real transitions in the 25 public games the mechanics library explains exactly.
  - **Planner success:** given the true rules, can search clear the level in at most the human action count?
- This tells us before spending any Kaggle GPU hours whether the idea can work. It also makes a strong, original paper
  section ("a mechanics DSL explains X% of ARC-AGI-3 public transitions").

## Honest risks
- The hidden games have *new* mechanics, so the library will not cover everything. The LLM-proposal path (b) and the
  plain harness remain as the fallback; the system must never be worse than Franzen's base.
- This is a large build: about 2–3 weeks to a first full test. Without the full system, the leaderboard gain by
  Nov 2 is uncertain.
- **Expected value:**
  - Paper Track: high in any case (novel, measurable).
  - Leaderboard: unknown. Plausible range is 0 to +5 if it integrates in time.

## Build order (each step measured)
| Week | Step | Measured by | GPU? |
|---|---|---|---|
| Oct 2–6 | Transition recorder + mechanics library v0 (8 primitives) + verifier | coverage on the 25 public games | no |
| Oct 6–10 | Enumerative hypothesis search + information-gain experiment picker | how many actions until the true rules are identified | no |
| Oct 10–14 | Planner in the verified simulator | levels cleared with known rules versus human action counts | no |
| Oct 14–20 | Integrate into Franzen's harness as one evidence line plus a `plan()` tool | Phase A on the 10 demo games against base, repeated | yes |
| Oct 20–Nov 2 | Tune, keep only if repeated gains; submit | hidden score | yes |
| Nov 2–8 | Paper | – | no |
