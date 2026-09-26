# ChatGPT prompt pack: ARC-AGI-3 research, end to end

How to use this:
1. Start a **new ChatGPT chat**. Use the strongest model you have, and turn on **Deep Research** or web search if available.
2. Upload `~/Desktop/arc3-full-research.zip`. Rebuild it first so it has the latest files:
   ```fish
   cd ~/ml-from-scratch; git pull
   git archive --format=zip -o ~/Desktop/arc3-full-research.zip HEAD arc-prize-2026 reports research_notes
   ```
3. Paste **Prompt 0**, then all of `arc-prize-2026/HANDOFF_PROMPT.md`.
4. Then run Prompts 1–8 one at a time, **each in its own message**. Wait for each answer before the next.
5. Bring every answer back to Claude, so both assistants check each other.

Never paste your Kaggle API key, `kaggle.json`, or passwords into any chat.

---

## Prompt 0: rules (paste first)

```
You are my research partner for the Kaggle competition "ARC Prize 2026 - ARC-AGI-3".
I attached a zip of my repo and I will paste a full handoff document next.

Rules for every answer:
1. Separate VERIFIED facts (with a link or a file path from my zip) from GUESSES. Label each one.
2. Never invent leaderboard numbers, team methods, GitHub PRs, or Kaggle notebooks. If you cannot find it, say "not found".
3. Hard constraints: Kaggle GPU only (1x RTX Pro 6000, 96 GB, 9 hours, no internet at run time), no money, no rented GPUs,
   1 submission per UTC day. Reject any idea that breaks these.
4. One hidden run swings about +-50%. Never call something an improvement from one score.
5. I use macOS with the fish shell. Give commands that work in fish (no <placeholders>, no bash-only syntax).
6. Be short and concrete. End each answer with: "Top 3 actions for tomorrow" and "What would prove me wrong".
Reply "ready" and wait for the handoff document.
```

---

## Prompt 1: what the top teams really do

```
Deep research task. Find everything public, up to today, about how the top teams on the ARC-AGI-3 Kaggle leaderboard work:
Lord Han Solo, Tufa Labs, Yi-Chia Chen, Daniel Franzen, NVARC3 (NVIDIA), Tong Hui Kang.
Search: Kaggle discussions and Code tab, arcprize.org blog (Milestone #1 winners' write-ups), GitHub (their forks and commits),
X/Twitter, LinkedIn, arXiv, YouTube talks, Discord summaries.
For each team give: model, serving setup (vLLM version, KV cache type, context), harness style, any training or fine-tuning,
evidence links, and a confidence level. Then list the 3 ideas most likely to explain the jump from ~4 to ~19.
```

## Prompt 2: Milestone #2 watch (run on Oct 1 and again every few days)

```
Milestone #2 of ARC-AGI-3 closed on Sep 30, 2026. Search the Kaggle Code tab (sort by score and by most recent), the discussion
forum and arcprize.org for any notebook or write-up published since Sep 28 that claims a leaderboard score above 5.
For each one give: exact Kaggle URL in the form owner/slug, claimed score, license, model, and what differs from Thuitanium's B81
(the base described in my handoff). Rank them by how quickly I could adopt them with my tools/adopt.py.
```

## Prompt 3: faster serving (fp8 KV cache)

```
Read vLLM PR #55557 (fp8 KV cache, merged Sep 16, 2026) and anything related.
Tell me: (a) does it change only Python code, or also compiled CUDA kernels? (b) is it in a released vLLM wheel, and which version?
(c) can it run offline on Kaggle inside the B81 notebook's vLLM runtime (see vendor/b81 in my zip)? (d) exact config flags for
Qwen3.8-Flash-Next NVFP4 with fp8 KV on a 96 GB RTX Pro 6000, (e) the risks (accuracy loss, crashes), (f) a test plan
that uses at most 2 Kaggle smoke runs.
```

## Prompt 4: review my code

```
Review the files in arc-prize-2026/agent/grafts/ (note_fill.py, prompt_extras.py, keep_on_death.py) and build_notebook.py.
Look for real bugs, ways they could hurt the score (wasted actions, longer prompts that slow the model), and anything that
could crash Phase B. For each finding give the file, the line, the problem, and a minimal fix. Do not suggest large rewrites.
```

## Prompt 5: cheap ideas that could really move the score

```
Given the lessons in section 5 of my handoff (most harness tweaks measured as noise; only model upgrades moved scores 2-3x),
list at most 5 ideas that fit Kaggle-only constraints and have real evidence (a paper, a public score, or a clear mechanism)
of a gain of 20% or more. For each: evidence link, expected gain, cost in Kaggle GPU hours, and how to test it with 1-2
submissions. Sort by expected gain divided by cost. Say plainly if you think nothing on the list will beat noise.
```

## Prompt 6: my daily log checker (reuse daily)

```
Here is my latest Kaggle output (log lines and/or the Submissions page). Check:
1) Did all OURS_* markers print, with the right variant? 2) Any Traceback other than the known serving_teardown.py one?
3) Per-game results against my ledger. 4) What to submit next, following the plan (alternate m2 and m3 until Sep 29).
Update my ledger table and give it back as markdown.
[paste log here]
```

## Prompt 7: teammates

```
The team-merge deadline is Oct 26, 2026. Help me find teammates who score above 4.07 on the ARC-AGI-3 leaderboard.
Draft (a) a short Kaggle discussion post and (b) a direct message. Be honest: our best score is 4.07, and we have a tested
graft framework, a full research write-up and a daily submission routine. Explain what we offer and what we want.
Also list the Kaggle rules on merging (total submissions, how GPU quota works for a team).
```

## Prompt 8: Paper Track draft

```
Help me write the ARC Prize 2026 Paper Track submission (due Nov 8; at most 1,500 words plus a public notebook).
Read the Paper Track rules at arcprize.org/competitions/2026/paper first and list how papers are judged.
Proposed topic: "Measuring harness changes under +-50% draw noise on ARC-AGI-3", using our ledger, our A/B method, and what
did and did not work. Give an outline, a first draft, and the figures and tables we need. Only use numbers from my ledger.
```
