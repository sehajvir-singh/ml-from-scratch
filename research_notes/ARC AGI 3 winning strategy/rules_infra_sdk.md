# ARC Prize 2026 – ARC-AGI-3 (Kaggle): Rules, Infrastructure, and Game SDK/API Fact Sheet

*Research date: 2026-09-25. Primary sources were: (1) Kaggle's own competition settings and overview/rules pages, fetched as JSON through Kaggle's internal web API (`CompetitionService.GetCompetition`, `PageService.ListPages`, `DiscussionsService`, `LeaderboardService`, `KernelsService`), so they are verbatim host text; (2) source code of `arc-agi` 0.9.9 / 0.9.8 and `arcengine` 0.9.3 downloaded from PyPI; (3) the official GitHub repos `arcprize/ARC-AGI-3-Kaggle-Starter` and `arcprize/ARC-AGI-3-Agents`; (4) docs.arcprize.org markdown pages; (5) the output files of the official Kaggle sample notebooks. The labels are: **[OFFICIAL]** = Kaggle host/staff or ARC Prize text or code; **[CODE]** = what the shipped SDK source does (authoritative for the local engine, and very likely what the gateway runs, but the gateway itself is not public); **[COMMUNITY]** = participant claims.*

*Caution on the pip mirror: the sandbox's pip index only served stale `arc-agi` 0.0.7, which is a different, older ARC-AGI-1/2 toolkit that pulls in `arc-agi-core`. PyPI itself serves the real ARC-AGI-3 toolkit, `arc-agi` 0.9.9 (2026-06-10), which requires `arcengine>=0.9.3` and Python>=3.12. **`arc-agi-core`, `arc-agi-dsl` and `arc-agi-llm` are unrelated ARC-AGI-1/2 static-grid packages (Grid/Pair/Task classes, D8-symmetry DSL, a GPT wrapper) and are NOT the ARC-AGI-3 game SDK.** [pypi.org/pypi/arc-agi/json](https://pypi.org/project/arc-agi/0.9.9/), [arc-agi-core](https://pypi.org/project/arc-agi-core/)*

---

## Q1. Runtime limit, hardware (GPU options/specs, RAM, disk), internet, and daily submission cap

### Takeaway
The runtime limit is **9 hours (540 min) for both CPU and GPU notebooks**, and internet must be disabled. **You get 1 submission per day** (a 5/day setting from May 27 to Jun 8 was a mistake and has been reverted). Four accelerator choices exist: CPU, **T4×2**, **P100**, and **"RTX 6000" = NVIDIA RTX PRO 6000 Blackwell (96 GB) on GCP machine type `g4-standard-48`**, which only ARC-AGI-3 notebooks may use. H100s were offered briefly (late April to early May) and then withdrawn because of a stockout. L4 is not offered.

### Cited Findings
- **Kaggle competition settings** [OFFICIAL]: `maxCpuRuntimeMinutes = 540`, `maxGpuRuntimeMinutes = 540`, `maxDailySubmissions = 1`, `numScoredSubmissions = 2`, `maxTeamSize = 8`, `onlyAllowKernelSubmissions = true`, `requiredSubmissionFilename = "submission.parquet"`, `rowIdColumnName = "row_id"`, `usesSynchronousReruns = true`, `rerunMaxStaggerMinutes = 10`, `requiresIdentityVerification = true`, `submissionSizeLimitMb = 20480`, `scoreTruncationNumDecimals = 2`, `witholdFinalLeaderboardUntilItHasBeenVerified = true`, and evaluation metric "ARC-AGI-3 Metric" (isMax=true). All were fetched from the competition JSON on 2026-09-25. — [Kaggle competition overview](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview)
- **Code Requirements page** [OFFICIAL]: "CPU Notebook <= 9 hours run-time; GPU Notebook <= 9 hours run-time; Internet access disabled; Freely & publicly available external data is allowed, including pre-trained models; Submission file will be automatically generated." — [Kaggle Code Requirements](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/code-requirements)
- **Runtime history** [OFFICIAL]: the limit went from 6 h to 9 h on 2026-05-07, "Given the change in accelerators from H100s to RTX 6000". — [Discussion 697944 (María Cruz, Kaggle staff)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697944). After that change, submissions were still capped at 6 h because "an extra bespoke setting ... was not updated". Staff reported it fixed on 2026-05-19. — [Discussion 699208 (inversion, Kaggle admin)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699208)
- **Host confirmation that ARC-AGI-3 uses 9 h** [OFFICIAL]: "For v3 it is 9hrs. Where do you see 12 hours? we should switch that" (Greg Kamradt, 2026-07-27). — [Discussion 729985](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/729985)
- **Accelerator history** [OFFICIAL]:
  - 2026-03-25: submissions were limited to P100 / 2×T4, and staff said "Our intent is to offer H100s". — [Discussion 684724](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/684724)
  - 2026-04-28: "This competition now has access to Kaggle's pool of powerful new H100 accelerators!" — [Discussion 695158](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/695158)
  - 2026-05-07: "Kaggle faced a stockout of H100 processors ... we have changed to RTX 6000 Pro." — [Discussion 697720](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697720)
- **Machine type** [OFFICIAL]: "We've added RTX 6000 machines to the ARC-AGI-3 hardware pool ... Kaggle uses machine type `g4-standard-48`. ARC-AGI-3 Only – RTX are only available for notebooks attached to this competition, use of RTX for any other activity could result in moderation action ... all RTX sessions must have internet disabled." — [Kaggle overview, "Upgraded accelerators" section](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview). The overview first said "g2-standard-48" (4×L4). Staff corrected it to "g4-standard-48" on 2026-05-07. — [Discussion 697720 (LucyHe2, staff)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697720)
- **Starter kit accelerator table** [OFFICIAL]: `"cpu"` = no GPU; `"t4"` = Nvidia T4 ×2 (the default); `"p100"` = Nvidia P100 (single high-memory GPU); `"rtx6000"` = Nvidia RTX 6000 (`g4-standard-48`), "ARC-AGI-3 exclusive, burns GPU quota faster". The Kaggle metadata accelerator names are `none`, `nvidiaTeslaT4`, `nvidiaTeslaP100` and `nvidiaRtx6000`. — [ARC-AGI-3-Kaggle-Starter README / scripts/build_notebook.py](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter); [docs.arcprize.org/arc-prize-2026](https://docs.arcprize.org/arc-prize-2026)
- **ARC Prize names it the "RTX Pro 6000"** [OFFICIAL]: the GPT-OSS template says to "Set the accelerator to **RTX Pro 6000**" and that the model "runs slowly on the RTX hardware". — [docs.arcprize.org GPT OSS on Kaggle](https://docs.arcprize.org/partner_templates/gpt-oss-kaggle)
- **g4-standard-48 spec** (third-party cloud catalogs, not Kaggle): 1× NVIDIA RTX PRO 6000 (96 GB), 48 vCPUs, 180 GB RAM. — [Spare Cores g4-standard-48](https://sparecores.com/server/gcp/g4-standard-48); [Northflank](https://northflank.com/cloud/gcp/instances/g4-standard-48). GCP docs confirm that the G4 series uses NVIDIA RTX PRO 6000 GPUs. — [GCP accelerator-optimized machines](https://docs.cloud.google.com/compute/docs/accelerator-optimized-machines)
- **Blackwell evidence** [COMMUNITY]: vLLM/Triton on the Kaggle RTX raised `ptxas fatal: Value 'sm_120a' is not defined`, which is the Blackwell compute capability 12.0. — [Discussion 703506](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703506). One report of gpt-oss-120b on the Kaggle RTX PRO 6000: model load ~74 s, a 15.86 GiB fp8 KV cache (462k tokens), ~830 tok/s generation at 25 concurrent requests. — [Discussion 738599](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738599)
- **Kaggle container limits** [OFFICIAL, relayed by host from the Kaggle team, 2026-07-17]:
  - Docker logs are capped at 10 MB per container.
  - The disk quota is 20 GB for `/kaggle/working`. Exceeding it kills the kernel with "out of disk". Space outside that directory is temporary.
  - There is no RLIMIT_NPROC and no RLIMIT_AS.
  - Memory is enforced by cgroups: "30 GB for CPU notebooks".
  - There is a reference to a "4-core CPU allocation".
  - Segfaults show exit code 139, with no core dumps exposed.
  - Source: [Discussion 724841](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/724841)
- **Standard Kaggle GPU specs** (aggregator, not verified on Kaggle docs): P100 16 GB VRAM; T4×2 = 2×16 GB; about 30 h/week GPU quota shared across GPU types. — [aimultiple free-cloud-gpu](https://aimultiple.com/free-cloud-gpu); [Kaggle efficient GPU docs](https://www.kaggle.com/docs/efficient-gpu-usage)
- **Daily submission cap** [OFFICIAL]: Rules §2.2(a): "You may submit a maximum of 1 (1) Submissions per day." — [Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules). Staff statement of 2026-06-09: "Our intended setting for this competition had been one submission per day. However, on May 27 ... [we] mistakenly change[d] the competition settings to allow 5 submissions per day ... Yesterday, June 8, we restored the submission limit back to one submission per day ... Invalidating Surplus Submissions." — [Discussion 705405](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705405). Also: "Daily submissions moving forward at 1 per day" (Greg Kamradt, 2026-06-08). — [Discussion 705094](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705094)
- **Stale starter kit text** [OFFICIAL but outdated]: the starter README still says "You only get 5 official submissions per day". It was changed from "one" to "5" in commit eeb1535 on 2026-05-27, the same day as the settings mistake. — [ARC-AGI-3-Kaggle-Starter README](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter)
- **Queueing** [OFFICIAL]: RTX PRO 6000 queue backlogs were acknowledged on 2026-08-14, 2026-09-08 and 2026-09-21/22. Staff said "Capacity is restored, queue should start ticking down" on 2026-09-22. — [Discussion 735147](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735147); [Discussion 742148](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742148); [Discussion 740262](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/740262)
- **Quota mechanics** [COMMUNITY]: submitting a version that has not been Save-&-Run triggers a second execution that consumes GPU quota and can be cancelled without affecting the scored run. You need some free GPU quota to create a new version, but the scored rerun itself does not consume your quota. Colab Pro links add +15 GPU h. — [Discussion 731290](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/731290); [Discussion 734585](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734585)
- **Python** [OFFICIAL/COMMUNITY]: `arc-agi`/`arcengine` require Python ≥3.12 ([PyPI](https://pypi.org/project/arc-agi/0.9.9/)). The Kaggle image runs Python 3.11.15, so you must install from the competition-provided wheels, not pip. — [Discussion 699517](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699517)

### Inferences
- The effective design space is: one 96 GB Blackwell GPU (fits ~27–31B dense models in FP8/BF16 comfortably, or gpt-oss-120b in MXFP4 with a modest KV cache) plus ~48 vCPUs, **if Kaggle exposes the full g4-standard-48**. That is unconfirmed; the 30 GB RAM / 4-core figures from staff were stated for CPU notebooks.
- Because the scored rerun uses the accelerator stored in the notebook version's metadata, a GPU agent submitted with the GPU setting off will fail. Staff analysis found that this caused ~20% of errors (see Q8).

### Gaps
- There is no official Kaggle statement of the RAM, vCPU count or local disk actually allocated to RTX PRO 6000 sessions, nor of the GPU-quota multiplier for RTX ("burns GPU quota faster" is unquantified).
- Whether H100 still appears as a selectable-but-unsupported option is unclear (a CPMP comment on 2026-05-09 said it still appeared; no official answer).

---

## Q2. Final submissions, public/private split, key dates, prize amounts

### Takeaway
You select **2 final submissions**. **110 hidden games are played on every submission.** **55 (the "semi-private" set) drive the public LB and the other 55 (the fully private set) drive the final LB.** Private scores are computed at original run time, with no end-of-competition rerun. The dates are all 23:59 UTC:
- Milestone #1: Jun 30, 2026
- **Milestone #2: Sep 30, 2026**
- **Entry and team-merger deadline: Oct 26, 2026**
- Notebook publishing disabled after Oct 26, 2026
- **Final submission deadline: Nov 2, 2026**
- Winners announced: Dec 4, 2026

The prizes are:
- $850K total
- Final LB: $40K / $15K / $10K / $5K / $5K
- **Each milestone: $25K / $7.5K / $5K per the Kaggle rules** (arcprize.org says $25K / $10K / $2.5K)
- A $700K bonus only if a team reaches 100%

### Cited Findings
- **Final selections** [OFFICIAL]: "You may select up to two (2) Final Submissions for judging." — [Kaggle rules §2.2(b)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules). The settings show `numScoredSubmissions = 2`. — [Kaggle overview](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview)
- **Split** [OFFICIAL]: "Competition evaluation uses a separate, private set of 110 games that your agent has never seen. Half of these are used for the Public Leaderboard score, and the other half for the Private Leaderboard score." — [Kaggle data page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/data). The settings show `leaderboardPercentage = 50`. "Submissions run on all 110 tasks." (inversion, staff, 2026-03-26). — [Discussion 684852](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/684852). Budget time for "110 evaluations/games" (Greg Kamradt). — [Discussion 703990](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990)
- **Set composition** [OFFICIAL]: ARC-AGI-3 has 25 public-demo, 55 semi-private and 55 fully-private environments. — [ARC-AGI-3 technical report, arXiv 2603.24621](https://arxiv.org/html/2603.24621v1). "Public Demo was made to be easier than semi private (what is used for the public leaderboard)." — [Discussion 703990 (Greg Kamradt)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990)
- **No final rerun** [OFFICIAL]: "Private scores are calc'd at original run time. They aren't rerun. Yes, the submission plays both datasets. Only the 50% of pubic tasks are shown for the leaderboard." — [Discussion 729985 (Greg Kamradt, 2026-07-27)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/729985)
- **Game count discrepancy** [COMMUNITY]: CPMP wrote "There are 100 game[s] in test data. 55 ... 55 ...", which is internally inconsistent; the official number is 110. — [Discussion 697944](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697944)
- **Timeline** [OFFICIAL]: "March 25, 2026 – Start Date. June 30, 2026 (optional) – Deadline for Milestone 1. September 30, 2026 (optional) – Deadline for Milestone 2. October 26, 2026 – Entry Deadline ... October 26, 2026 – Team Merger Deadline ... November 2, 2026 – Final Submission Deadline. December 4, 2026 – Winners announcement. All deadlines are at 11:59 PM UTC." — [Kaggle timeline](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/timeline)
- **Deadline fields in the settings JSON** [OFFICIAL]: `deadline 2026-11-02T23:59:00Z`, `teamMergerExplicitDeadline 2026-10-26T23:59:00Z`, `prohibitNewEntrantsExplicitDeadline 2026-10-26T11:59:00Z` (**note: 11:59 AM in the JSON vs "11:59 PM" in the timeline text**), `kernelsPublishingDisabledDeadline 2026-10-26T23:59:00Z`. — [Kaggle overview](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview)
- **Prizes, Kaggle rules §1.5** [OFFICIAL, legally binding]:
  - "(a.1.) Final leaderboard prizes: $75,000 – First $40,000, Second $15,000, Third $10,000, Fourth $5,000, Fifth $5,000."
  - "(a.2.) Milestone prizes: $75,000 ... Milestone 1: June 30th, 2026 – First $25,000, Second $7,500, Third $5,000; Milestone 2: September 30, 2026 – 1st $25,000, 2nd $7,500, 3rd $5,000."
  - "(b) Bonus Prize: $700,000 ... in the event that a team achieves a score of 100% accuracy ... divided among the Top 5 teams that have achieved 100%: $350,000 / $175,000 / $70,000 / $70,000 / $35,000."
  - Source: [Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules); [Kaggle prizes page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/prizes)
- **Conflicting milestone split** [OFFICIAL, other source]: arcprize.org lists each milestone as "1st: $25K, 2nd: $10K, 3rd: $2.5K" and describes the $700K Grand Prize as going to "the first eligible agent achieving 100%" (carrying forward if unawarded). — [arcprize.org ARC-AGI-3 competition](https://arcprize.org/competitions/2026/arc-agi-3). Both sources total $37.5K per milestone.
- **Other overall facts** [OFFICIAL]: the ARC Prize 2026 total across all tracks is $2M (ARC-AGI-3, ARC-AGI-2, Paper); results are announced Dec 4, 2026. — [arcprize.org/competitions/2026](https://arcprize.org/competitions/2026)
- **Current public LB, fetched 2026-09-25** [OFFICIAL data]: 3,320 teams. #1 19.45 (Lord Han Solo), #2 18.81 (Tufa Labs), #3 18.63, #4 16.68, #5 16.07 (NVARC3), #10 8.81, #25 6.24, #50 4.99, #100 4.32, #500 3.23. Scores are in percent. — [Kaggle leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard)
- **Tie-break** [OFFICIAL]: "In the event of a tie, the Submission that was entered first to the Competition will be the winner." — [Kaggle rules §3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)

### Inferences
- The public LB is a 55-game sample of a different, harder distribution than the 25 public demo games. The final ranking is a different 55-game sample. Given the reported run-to-run variance (Q6), choosing the 2 finals should favour robust, repeatedly-validated configurations over single lucky public scores.
- **Treat Oct 26 as the hard practical cutoff for team changes and new entrants.** The JSON 11:59 AM value may mean entry closes 12 h earlier than the text implies.

### Gaps
- No official statement settles whether the 55/55 public/private split is fixed across submissions. It is presumably fixed, since it is a standard Kaggle solution-file split. Asked in [Discussion 738762](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738762) without a host answer.

---

## Q3. Milestone #2 eligibility, open-source/license rules, Paper Track, write-ups

### Takeaway
**For a milestone prize**, your notebook must be **made public under an open-source license by 23:59 UTC on Sep 30, 2026**. The ranking is by public LB at the deadline (community reading, confirmed by M1 practice), and prizes move down to the best open-sourced entries. **All prize winners** must license the winning submission and code under **CC-BY 4.0**, and use an OSI "open source AI" system, model and weights. They must also deliver code and documentation and do an interview with a host-provided technical writer. arcprize.org's own text says "permissive public domain license (e.g. CC0 or MIT-0)". **The Paper Track is a separate Kaggle competition** with these terms:
- Deadline **Nov 9, 2026** (arcprize.org says Nov 8)
- A Kaggle Writeup of ≤1,500 words plus a public notebook, linked to an ARC-AGI-2/3 code submission
- $50K / $20K / $5K, plus a $375K bonus split among papers scoring >4.5/5

### Cited Findings
- **Milestone rule** [OFFICIAL]: "These prizes are based on the leaderboard score on two specific dates throughout the competition. Notebooks must be made public under an open source license by the corresponding milestone dates to qualify for these prizes. All deadlines are at 11:59 PM UTC on the corresponding day." — [Kaggle prizes page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/prizes). Rules text: "Participants should have published their Notebooks by the date specified in each milestone to be considered for these prizes." — [Kaggle rules §1.5(a.2)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)
- **Deadline clarification** [OFFICIAL]: "the deadline to do so is 11:59pm UTC on the corresponding day ... the second one is on September 30th." (María Cruz, 2026-06-24). — [Discussion 713634](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713634)
- **General open-source condition** [OFFICIAL]: "participants eligible for a prize will be removed from the competition if they do not open source their solutions." — [Kaggle prizes page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/prizes)
- **Winner license** [OFFICIAL]:
  - "WINNER LICENSE TYPE: CC-BY 4.0".
  - "You hereby license ... your winning Submission and the source code used to generate the Submission under CC-BY 4.0".
  - "Submissions are required to have open source system, open source model, and open source weights/parameters, as defined in the checklist from the Open Source AI definition by the Open Source Initiative."
  - Exception: "In the event that input data or pretrained models with an incompatible license are used ... you do not need to grant an open source license ... for that data and/or model(s)."
  - Data license: Apache 2.0.
  - Source: [Kaggle rules §1.6, §2.5](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)
- **Conflicting license language** [OFFICIAL, arcprize.org]: "all code and methods authored by the submitter must be made open source under a permissive public domain license (eg. CC0 or MIT-0)", and third-party code must have "at least, an open source license which allows public sharing (eg. Apache-2.0, GPLv3)". "Participants must open source their solutions before receiving official private evaluation scores." — [arcprize.org/competitions/2026](https://arcprize.org/competitions/2026)
- **Winner's obligations** [OFFICIAL]: deliver final code (training code, inference code, environment description). Also: "Conduct an interview with the sponsor and work with a technical writer provided by the host to document their solution"; a "detailed description of methodology ... link to a code repository with complete and detailed instructions"; and a possible recorded or panel call. — [Kaggle rules §2.5(b), §2.8](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)
- **Code sharing** [OFFICIAL]: "No private sharing outside of Teams ... It's okay to share code if made available to all Participants on the forums." — [Kaggle rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules)
- **Milestone ranking basis** [COMMUNITY, not host-confirmed]: "Public for both milestones" (parthenos). — [Discussion 713634](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713634); [Discussion 710898](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/710898). "It moves down the ladder": the highest-scoring open-sourced notebook takes "1st" even if it sits lower on the LB (Nick Pellegrin). — [Discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801)
- **Milestone #1 precedent** [OFFICIAL]: the award went to 1st Tufa Labs "The Duck" (Python REPL harness, multimodal, "infinite play via eviction", Qwen 3.6 27B locally), 2nd Reki (vision-LLM-as-policy with Gemma-4-31B), and 3rd Md Boktiar Mahbub Murad "forge" (Gemma-4-31B). Total $37.5K. — [Discussion 725002 (Greg Kamradt)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/725002); [arcprize.org blog M1](https://arcprize.org/blog/arc-prize-2026-milestone-1). Winning public notebook scores [COMMUNITY/Kaggle notebook data]: Tufa "duck harness [June 30 milestone winner]" best public 1.25; the 3rd place "LB 0.86". — [Kaggle notebook list](https://www.kaggle.com/code/jeroencottaar/tufa-labs-duck-harness-june-30-milestone-winner); [Discussion 716719](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/716719)
- **M2 dynamics** [COMMUNITY]: Tufa Labs (currently #2 at 18.81) announced on 2026-09-23 that they "will not be sharing our solution on September 30 for the second milestone prize". NVIDIA's CPMP team also indicated they will not share before the end. — [Discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801)
- **Paper Track (Kaggle)** [OFFICIAL]:
  - Separate competition `arc-prize-2026-paper-track`; deadline `2026-11-09T23:59:00Z`; team max 8; "Team must match the team making a submission to either ARC-AGI-2 or ARC-AGI-3."
  - Reward: "$75,000 guaranteed prize; plus $375,000 bonus prize for papers that score above 4.5/5".
  - Submission: Kaggle Writeup "should not exceed 1,500 words", media gallery with a required cover image, "Attached Public Notebook", and an optional PDF via Project Link.
  - Rubric: six equally weighted 0–5 criteria (Accuracy, Universality, Progress, Theory, Completeness, Novelty), averaged. Rubric scores are not shared. Ties go to the earliest entry.
  - License: CC-BY-4.0.
  - Source: [Kaggle Paper Track](https://www.kaggle.com/competitions/arc-prize-2026-paper-track)
- **Paper prize split** [OFFICIAL, arcprize.org]: 1st $50K, 2nd $20K, 3rd $5K, plus a $375K outstanding-papers pool for scores >4.5. Papers must be "linked to a Kaggle code submission (ARC-AGI-2 or ARC-AGI-3 track)"; the code need not score highly. — [arcprize.org/competitions/2026/paper](https://arcprize.org/competitions/2026/paper). arcprize.org lists "Paper Deadline: November 8, 2026" — [arcprize.org/competitions/2026](https://arcprize.org/competitions/2026). This conflicts with Kaggle's Nov 9.

### Inferences
- For a Milestone #2 claim, publish the exact scoring notebook with all its dependencies (wheels, model weights, fine-tunes as public Kaggle datasets/models) under an OSI license (CC-BY 4.0 is safest) shortly before 23:59 UTC Sep 30. M1 practice was to publish 1–2 h before the deadline so that clones cannot finish scoring in time.
- The CC-BY 4.0 (Kaggle rules) versus CC0/MIT-0 (arcprize.org) discrepancy means dual-licensing your own code as CC0 or MIT-0 plus CC-BY 4.0 would satisfy both.
- The OSI "open weights" requirement plus the "incompatible license" exception suggests Gemma/Qwen-style licensed weights are tolerated. This is not explicitly adjudicated.
- A write-up is not required to win Top Score or Milestone prizes. Winners must document their work via the host process, and the Paper Track is optional and separate.

### Gaps
- No host confirmation exists on whether milestone ranking uses the public LB snapshot at submission time or at score-display time (asked in [Discussion 705043](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705043)).
- No host ruling exists on self-generated synthetic data as "External Data" ([Discussion 742940](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742940); CPMP says it was not treated as external data in past ARC competitions).
- No host ruling exists on the team-size question raised about mostik.ai ([Discussion 739186](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739186)).

---

## Q4. Kaggle evaluation gateway mechanics, package API, `submission.parquet`, Phase A vs Phase B

### Takeaway
It is a notebook-only code competition, run in two phases:

**Phase A ("Save & Run All" / commit)** runs your notebook without the hidden games. `KAGGLE_IS_COMPETITION_RERUN` is unset, and you must write a dummy `submission.parquet` so the commit succeeds.

**Phase B (clicking "Submit to Competition", selecting `submission.parquet`)** reruns the notebook with `KAGGLE_IS_COMPETITION_RERUN` set:
- A **gateway sidecar container at `http://gateway:8001`** runs the `arc-agi` Flask REST server in **competition mode** with the 110 hidden games.
- Your agent talks to it over HTTP (`OPERATION_MODE=online`, `ARC_API_KEY=test-key-123`).
- The **gateway records every action and itself emits the scored `submission.parquet`**.
- The hidden games' source files are **not** in your container.

### Cited Findings
- **Official notebook pattern** [OFFICIAL, starter kit mirrors Kaggle's "ARC3 Sample Submission – Stochastic Goose"]:
  1. `!pip install --no-index --find-links /kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels arc-agi python-dotenv`
  2. Write the agent to `/tmp/my_agent.py`.
  3. `if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):`
     - wait for the gateway: `curl --fail --retry 999 --retry-all-errors --retry-delay 5 --retry-max-time 600 http://gateway:8001/api/games`
     - copy `/kaggle/input/competitions/arc-prize-2026-arc-agi-3/ARC-AGI-3-Agents` to `/kaggle/working/`
     - register `MyAgent` in `agents/__init__.py`
     - write `.env`: `SCHEME=http HOST=gateway PORT=8001 ARC_API_KEY=test-key-123 ARC_BASE_URL=http://gateway:8001/ OPERATION_MODE=online ENVIRONMENTS_DIR= RECORDINGS_DIR=/kaggle/working/server_recording`
     - run `python main.py --agent myagent` ("The gateway records every action and emits submission.parquet")
  4. Else (commit): write a dummy parquet: `pd.DataFrame([['1_0','1',True,1]], columns=['row_id','game_id','end_of_game','score']).to_parquet('/kaggle/working/submission.parquet')`.
  - Source: [ARC-AGI-3-Kaggle-Starter scripts/build_notebook.py](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter/blob/main/scripts/build_notebook.py)
- **Two phases** [OFFICIAL]: "Phase A: Save & Run All. Kaggle runs your notebook in their real environment and validates that the code executes without errors ... Phase B: Competition Rerun. Triggered when you click Submit to Competition ... Your agent plays the hidden game set." — [docs.arcprize.org/arc-prize-2026](https://docs.arcprize.org/arc-prize-2026)
- **Submission file** [OFFICIAL]: "Submission files are automatically calculated. As long as the agent takes action on any of the games, a submission file for all of the games is created." — [Kaggle evaluation page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/evaluation). "The submission format is submission.parquet, it's generated by running the notebook against the ARC gateway API." (María Cruz). — [Discussion 705405](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705405). Asked about a manual parquet versus an inference entry point: "output a submission.parquet file manually. This is just a technical requirement of the kaggle competition but isn't used." (Greg Kamradt). — [Discussion 698507](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/698507)
- **Parquet schema** [OFFICIAL notebook outputs]: the official Random Agent, Stochastic Goose and GPT-OSS-120B outputs each contain a one-row `submission.parquet` with columns `row_id` (str '1_0'), `game_id` (str '1'), `end_of_game` (bool True), `score` (int 1), which is the commit-mode dummy. — [Kaggle: ARC3 Sample Submission – Random Agent](https://www.kaggle.com/code/inversion/arc3-sample-submission-random-agent); [Stochastic Goose](https://www.kaggle.com/code/inversion/arc3-sample-submission-stochastic-goose)
- **Select the right output** [OFFICIAL]: if extra files (e.g. `my_agent.py`) appear in `/kaggle/working`, the Submit UI may default to them, giving "Could not find provided output file my_agent.py". Write auxiliary files elsewhere (e.g. `/tmp`). — [Starter commit eeb1535](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter/commit/eeb1535404f321d280a8f9194bbc1d7aca5f05fc)
- **Competition data files** [OFFICIAL]: `ARC-AGI-3-Agents/` (a copy of the agents repo), `arc_agi_3_wheels/` (package wheels), and `environment_files/` ("location of the 25 public game files"). — [Kaggle data page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/data). The competition notebooks use arc-agi 0.9.8 [COMMUNITY] — [Discussion 728220](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/728220). **[CODE] 0.9.8 → 0.9.9 differs only in an error-log message in `remote_wrapper.py`** (source diff done for this research). — [PyPI arc-agi](https://pypi.org/project/arc-agi/#history)
- **Competition mode (forced on Kaggle)** [OFFICIAL]:
  - "Environments must be interacted with via the API."
  - "Scoring is against all available environments, even if you choose not to interact with them."
  - "Only Level Resets are permitted, Game Resets are not allowed and become Level Resets."
  - "Can only interact (call `make`) a single time for each environment."
  - "Can only open a single Scorecard."
  - "Cannot get scoring of an inflight scorecard, `get_scorecard` does not work."
  - "Note: The Kaggle Competition is forced into this mode." Enable it locally with `Arcade(operation_mode=OperationMode.COMPETITION)` or `OPERATION_MODE=COMPETITION`.
  - Source: [docs.arcprize.org/toolkit/competition_mode](https://docs.arcprize.org/toolkit/competition_mode)
- **[CODE] Competition mode in `arc_agi/api.py` (0.9.9)**:
  - A second `POST /api/scorecard/open` returns "cannot open multiple scorecards in competition mode".
  - `GET /api/scorecard/<id>` returns "cannot get scorecard that is in competition mode".
  - Once a game exists on the scorecard, creating it again returns nothing, so there is one play per game.
  - On `/api/scorecard/close`, every environment never touched is instantiated, so it scores 0.
  - A `RESET` sent when the level's `_action_count == 0` (which would otherwise be a full game reset) is **not executed**: the server returns the current observation and still calls `update_scorecard`.
  - `/api/games` and `/api/games/<id>` strip `baseline_actions`, `private_tags` and `level_tags` from the metadata.
  - Source: [arc-agi 0.9.9 sdist](https://pypi.org/project/arc-agi/0.9.9/#files)
- **[CODE] REST endpoints** served by `Arcade.listen_and_serve(host="0.0.0.0", port=8001, competition_mode=...)`:
  - `GET /api/games`
  - `GET /api/games/<game_id>`
  - `POST /api/scorecard/open` (body: `tags`, `source_url`, `opaque` ≤ 8 KB, `competition_mode`) → `card_id`
  - `POST /api/scorecard/close` (`card_id`)
  - `GET /api/scorecard/<card_id>[/<game_id>]`
  - `POST /api/cmd/RESET` (body: `game_id`, `card_id`, optional `guid`)
  - `POST /api/cmd/ACTION1..ACTION7` (body: `game_id`, `guid`, and for ACTION6 `x`, `y`; optional `reasoning` JSON ≤ 16 KB)
  - `GET /api/healthcheck`
  - Header `X-API-Key`.
  - Source: [arc-agi 0.9.9 server.py/api.py](https://pypi.org/project/arc-agi/0.9.9/#files); [docs.arcprize.org REST overview](https://docs.arcprize.org/rest_overview)
- **[CODE] Python toolkit API (`arc_agi` 0.9.9)**:
  - `Arcade(arc_api_key=..., arc_base_url=..., operation_mode=OperationMode.{NORMAL,ONLINE,OFFLINE,COMPETITION}, environments_dir="environment_files", recordings_dir=...)`. The `OPERATION_MODE=competition` env var overrides the constructor.
  - Methods: `get_environments()`; `make(game_id, seed=0, scorecard_id=None, save_recording=False, include_frame_data=True, render_mode=None|"human"|"terminal", renderer=None)`, which returns an `EnvironmentWrapper` whose construction **auto-sends the first RESET**; `open_scorecard/create_scorecard(tags, source_url, opaque)`; `close_scorecard(card_id)`, which returns an `EnvironmentScorecard`; `get_scorecard()`; `listen_and_serve(...)`.
  - Wrapper: `reset()`, `step(action: GameAction, data={'x':..,'y':..}, reasoning=dict)` → `FrameDataRaw`, plus `observation_space`, `action_space` and `info`.
  - The remote wrapper uses `requests` with **timeout=10 s** per call.
  - Source: [arc-agi 0.9.9](https://pypi.org/project/arc-agi/0.9.9/#files); [docs.arcprize.org toolkit](https://docs.arcprize.org/toolkit/overview)
- **[CODE] Agent framework (ARC-AGI-3-Agents)**:
  - `main.py` reads `/api/games`, builds a `Swarm`, opens one scorecard, calls `arc.make(g, scorecard_id)` for every game, starts **one thread per game (all games in parallel)**, joins, then closes the scorecard.
  - `Agent.main()` loops `while not is_done(...) and action_counter <= MAX_ACTIONS`, where the default `MAX_ACTIONS = 80` actually permits 81 actions.
  - `choose_action(frames, latest_frame)` receives `latest_frame` built from `arc_env.observation_space`.
  - Source: [ARC-AGI-3-Agents agents/agent.py, swarm.py, main.py](https://github.com/arcprize/ARC-AGI-3-Agents); [Discussion 734054](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/734054)
- **Hidden game files unavailable** [OFFICIAL]: public notebooks that deep-copy game objects only work on "the 25 public demo game environment files ... those same affordances aren't available on private games" (Greg Kamradt). — [Discussion 699900](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699900); [Discussion 707925](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/707925). [COMMUNITY] One participant claims game .py files were later obfuscated. — [Discussion 705405](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705405)
- **Timeout behaviour**:
  - [COMMUNITY] A random agent with effectively infinite MAX_MOVES ran 9 h and got "Notebook Timeout – Your submission notebook exceeded the allowed runtime"; the same agent with a finite cap scored 0.11. Another participant fixed timeouts with a 30-min buffer and fewer threads. — [Discussion 712719](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/712719)
  - [OFFICIAL] The GPT-OSS doc warns that too high a per-game time limit causes "`scorecard not produced in time` error, which fails the run." — [docs.arcprize.org GPT OSS](https://docs.arcprize.org/partner_templates/gpt-oss-kaggle)
- **[CODE] Scorecard auto-close**: the `ScorecardManager` defaults to `STALE_MINUTES = 15` (idle, clamp 1–60) and `MAX_OPEN_FOR_MINUTES = 4320`. The server's cleanup loop auto-closes idle scorecards every 60 s when `on_scorecard_close` is set. — [arc-agi 0.9.9 scorecard.py/api.py](https://pypi.org/project/arc-agi/0.9.9/#files). Docs: "Scorecards auto close after 15 minutes"; the online API has capped the maximum open duration at 24 h since 2026-04-14. — [docs.arcprize.org/scorecards](https://docs.arcprize.org/scorecards); [changelog](https://docs.arcprize.org/changelog)
- **First-action deadline** [OFFICIAL template code]: the GPT-OSS-120B notebook defines `FIRST_ACTION_DEADLINE_S = 14 * 60`, "Time-limit by which the agent has to return its first action to comply with Kaggle's submission guidelines", and sends an immediate initial RESET before vLLM finishes loading. — [Kaggle: ARC-AGI-3: GPT-OSS-120B (gregkamradt)](https://www.kaggle.com/code/gregkamradt/arc-agi-3-gpt-oss-120b)
- **Error visibility** [OFFICIAL]: to protect the private set, logs from scored runs are limited. In an analysis of 500 failed submissions:
  - about 1/3 got stuck with no visible error (infinite loops, deadlocks, wrong endpoint);
  - ~20% needed a GPU but submitted without one;
  - the long tail included missing datasets or dependencies, CUDA OOM, using the `three.arcprize.org` API, and writing to read-only `/kaggle/input`.
  - Source: [Discussion 727119 (Greg Kamradt)](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/727119)
- **Stagger** [OFFICIAL settings]: `rerunMaxStaggerMinutes = 10`. — [Kaggle overview](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview)

### Inferences
- **Keep the gateway "warm".** If the gateway uses the package's default 15-min idle auto-close, then (a) the first action must arrive within ~15 min of the scorecard opening, which `Swarm` does at start, and (b) no 15-min gap with zero actions can occur across all games. The template's 14-min first-action guard and its immediate initial RESET are consistent with this. Heavy model loading should happen *before* `main.py` opens the scorecard, or you should send cheap initial actions early.
- **All 110 games are created at Swarm start and played concurrently by default.** Per-game time budgeting (e.g. the template's `GAME_TIME_LIMIT_S`) plus a global wall-clock guard well under 9 h (the community uses a 10–30 min buffer) is necessary to guarantee that the gateway closes the scorecard and writes the parquet.
- Because unplayed games count as 0 and only one scorecard is allowed, a crash of the orchestrator after partial play likely still yields a partial score if the gateway later closes the scorecard. That claim comes only from a participant, not the host ([Discussion 699817](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699817)). It contradicts the "Notebook Timeout" reports, so do not rely on it.

### Gaps
- The gateway's exact configuration (idle timeout, `ONLY_RESET_LEVELS`, the scorecard-close trigger at notebook end, what happens on timeout) is not published. The gateway kernel (`gatewayKernelId 110953907`) and metric kernel (`104668730`) are private.
- The exact scored `submission.parquet` content produced by the gateway (row granularity per game or level, meaning of `end_of_game` and `score`) is not documented. Only the dummy schema is known.

---

## Q5. Precise game API: actions, frames, states, fields, RESET/UNDO/GAME_OVER semantics, caps

### Takeaway
Summary of the interface:
- **Actions:** `RESET` (id 0) and `ACTION1`–`ACTION7`. ACTION1–4 are semantically up/down/left/right, ACTION5 is a generic interact, **ACTION6 is a click at (x,y)** with 0–63 each and (0,0) top-left, and **ACTION7 is undo** where supported.
- **Observations:** each action returns **1–N frames**; each frame is a **64×64 grid of ints 0–15**.
- **Response fields:** `state ∈ {NOT_PLAYED, NOT_FINISHED, WIN, GAME_OVER}`, `levels_completed`, `win_levels` (total levels), `available_actions` (fixed per game), `guid` and `full_reset`.
- **RESET:** a mid-level RESET is a *level reset* and **costs 1 action**. RESET at the start of a level would normally be a full game reset, but **on Kaggle (competition mode) full resets are blocked**.
- **GAME_OVER:** does not auto-reset. Only RESET is accepted (other actions give HTTP 400 and are not counted), and the RESET restarts the current level.
- **No per-level action caps and no per-game time caps are imposed by the Kaggle evaluation.** The only limits are the 9 h wall clock and the idle and HTTP timeouts.

### Cited Findings
- **Action table** [OFFICIAL]: `RESET` "Initializes or restarts the game or level state"; `ACTION1`..`ACTION4` "Simple action – varies by game (semantically mapped to up / down / left / right)"; `ACTION5` "Simple action – varies by game (e.g., interact, select, rotate, attach/detach, execute, etc.)"; `ACTION6` "Complex action requiring x,y coordinates (0-63 range)"; `ACTION7` "Simple undo action". Human keybindings: W/S/A/D (or arrows) for ACTION1–4, Space/F for ACTION5, mouse click for ACTION6, Z for ACTION7. — [docs.arcprize.org/actions](https://docs.arcprize.org/actions). API docs: "ACTION7 will always be an undo action for games that support it." — [docs.arcprize.org llms.txt / API reference](https://docs.arcprize.org/api-reference/commands/execute-simple-action-7). The Kaggle data page says only "Additional simple action". — [Kaggle data](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/data)
- **[CODE] `arcengine.enums`**:
  - `GameAction`: RESET=0, ACTION1..5=1..5 (`SimpleAction{game_id}`), ACTION6=6 (`ComplexAction{game_id, x: int 0..63, y: int 0..63}`), ACTION7=7.
  - `ActionInput{id, data, reasoning}`, where `reasoning` is opaque JSON ≤16 KB, stored and echoed.
  - `GameState`: NOT_PLAYED, NOT_FINISHED, WIN, GAME_OVER.
  - `FrameData{game_id, frame: list[list[list[int]]], state, levels_completed (0..254), win_levels (0..254), action_input, guid, full_reset: bool, available_actions: list[int]}`. `FrameDataRaw` is the same with `frame` as a list of numpy arrays; the remote wrapper uses int8.
  - Source: [arcengine 0.9.3](https://pypi.org/project/arcengine/0.9.3/#files)
- **ACTION6 coordinates** [CODE/OFFICIAL]: "ACTION6 uses ComplexAction to encode screen coordinates x and y (0,0 is the top left pixel)". The engine maps display (x,y) into the camera grid with scale and letterbox via `Camera.display_to_grid`, returning None in the letterbox. — [arcengine README/camera.py](https://pypi.org/project/arcengine/0.9.3/#files). "Action 6 does not provide explicit X/Y coordinates for active areas. If Action 6 is available, only its availability will be indicated." — [docs.arcprize.org/actions](https://docs.arcprize.org/actions)
- **Frames** [OFFICIAL/CODE]:
  - Design goals: "64×64 output grid, 16 colors; Inputs: limited to 6 actions plus a RESET; Turn-based: no time advances without input; Frames: each input generates 1–N frames". — [arcengine OVERVIEW.md](https://pypi.org/project/arcengine/0.9.3/#files)
  - "Each response contains one or more 2D frame arrays plus game-state metadata"; "Maximum 64x64 grid size; Integer values 0-15; (0,0) at top-left, (x,y) format." — [docs.arcprize.org/game-schema](https://docs.arcprize.org/game-schema)
  - Host: "it is safe to assume it's 64x64." — [Discussion 707717](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/707717)
  - [CODE] The engine loops `step()` → `render()` until the action completes, with `MAX_FRAME_PER_ACTION = 1000` (raises "Action took too many frames"). — [arcengine base_game.py](https://pypi.org/project/arcengine/0.9.3/#files)
- **available_actions** [OFFICIAL]: "it is safe to assume that a game's available actions are the same throughout. Whether or not they are valid is a different story, but they'll be available." (Greg Kamradt, 2026-05-21). — [Discussion 702079](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/702079). [CODE] The engine default is `available_actions=[1,2,3,4,5,6]`. Per-game lists come in every response as raw ints. — [arcengine base_game.py](https://pypi.org/project/arcengine/0.9.3/#files)
- **levels_completed / win_levels** [CODE]: `levels_completed` = engine `_score`, incremented by `next_level()`; the game switches level on the next frame, and `win()` is called after the last level. `win_levels` = `win_score` if >1, else `len(levels)`. — [arcengine base_game.py](https://pypi.org/project/arcengine/0.9.3/#files). Older templates used `frame.score` / `frame.win_score`, which were renamed to `levels_completed` / `win_levels`. — [ARC-AGI-3-Agents commit 135f20a](https://github.com/arcprize/ARC-AGI-3-Agents/commits/main)
- **RESET semantics** [CODE, arcengine `handle_reset`]:
  - `if ONLY_RESET_LEVELS=="true" and state != WIN: level_reset()`
  - `elif _action_count == 0 or state == WIN: full_reset()` (back to level 1, `levels_completed=0`, `full_reset=True`)
  - `else: level_reset()` (restore the current level from its clean copy)
  - `_action_count` resets to 0 on every `set_level`, which includes entering a new level. **So a RESET immediately after a level transition, or a second consecutive RESET, is a *full* game reset in local/normal mode.** — [arcengine base_game.py](https://pypi.org/project/arcengine/0.9.3/#files). The community discovered this the hard way: "Trying to reset on the first move of a level can reset the game back to the start of level 1!" — [Discussion 692135](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/692135)
- **RESET on Kaggle** [OFFICIAL/CODE]: "Game Resets are not allowed and become Level Resets" — [competition_mode doc](https://docs.arcprize.org/toolkit/competition_mode). In `api.py`, when `scorecard.competition_mode and game._action_count == 0`, the server skips the step and calls `scorecard.update_scorecard(guid, observation_space, False)` — [arc-agi 0.9.9 api.py](https://pypi.org/project/arc-agi/0.9.9/#files).
- **Does RESET count as an action?** [CODE/OFFICIAL]:
  - `Scorecard.update_scorecard`: action id 0 with `full_reset=False` → `inc_reset_count`, which increments **both** `resets` and `actions` (+1). A full reset (only possible outside competition mode) → `new_play` starts a new run at 0 actions. Action ids 1–7 → +1 action. — [arc-agi 0.9.9 scorecard.py](https://pypi.org/project/arc-agi/0.9.9/#files)
  - A participant's experiment, acknowledged by host: 100 dead (no-change) ACTION6 clicks counted as exactly 100 actions. Host: "Yes, they match" and will update the wording of the methodology's "operations that do not alter the environment are not counted", which refers to "(tool calls, reasoning steps, retries)". — [Discussion 718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638)
- **GAME_OVER** [OFFICIAL]: "When a game reaches a game-over state, the only valid action is RESET. Sending any other action ... returns a 400 Bad Request error." — [docs.arcprize.org/actions](https://docs.arcprize.org/actions). [CODE] In GAME_OVER or WIN, non-RESET actions return an empty frame list, which the server turns into HTTP 400, and the scorecard is only updated when `len(frame) > 0`, **so they are not counted**. A RESET after GAME_OVER is a level reset (since `_action_count > 0`), restarting the *current* level, and costs +1 action. — [arcengine base_game.py; arc-agi wrapper.py/api.py](https://pypi.org/project/arc-agi/0.9.9/#files)
- **Game-specific soft resets** [COMMUNITY]: in some games (e.g. ls20) running out of the in-game energy bar triggers an automatic level reset rather than GAME_OVER, and actions keep accumulating. — [Discussion 697423](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697423); [Discussion 692135](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/692135)
- **Action caps** [OFFICIAL]: "We don't have the 5x action cap during the kaggle competition. We do that on the verified leaderboard to have an operational cap on testing. Kaggle has another mechanism for a cap by way of the limited compute" (Greg Kamradt, 2026-06-25). — [Discussion 713921](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713921). The 5× rule appears in the tech report for the verified leaderboard. — [arXiv 2603.24621](https://arxiv.org/html/2603.24621v1)
- **Termination** [OFFICIAL, template]: an episode ends when the agent's `is_done` returns True, when `MAX_ACTIONS` is reached, or on the 9 h limit. The environment itself does not terminate on the energy bar. — [Discussion 697423](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697423); [ARC-AGI-3-Agents agent.py](https://github.com/arcprize/ARC-AGI-3-Agents/blob/main/agents/agent.py)
- **Determinism** [OFFICIAL]: "a seed is used for each one. Games weren't designed with randomness or proc gen ... there are stable seeds." (Greg Kamradt). [COMMUNITY] The lf52 transition animation is unseeded noise. — [Discussion 694153](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/694153)
- **Game IDs** [OFFICIAL]: `<game_name>-<version>`, e.g. `ls20-9607627b`. Names are stable and versions may change. — [docs.arcprize.org/game-schema](https://docs.arcprize.org/game-schema). Public games had version bumps on 2026-04-14 (tn36, m0r0, r11l, tu93, vc33, sc25, ar25, dc22, cn04, sp80, su15, re86, ka59, s5i5, sk48). — [changelog](https://docs.arcprize.org/changelog)
- **Public set size** [COMMUNITY]: the 25 public games contain 183 levels in total (a local run log shows "Levels completed: 23/183"). — [Discussion 712719](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/712719)
- **Engine speed** [OFFICIAL]: "Run ARC-AGI-3 environments locally at 2,000+ FPS" (toolkit release, 2026-01-29, v0.9.1). — [changelog](https://docs.arcprize.org/changelog)

### Inferences
- In competition mode, **never send RESET at the very start of a level (or twice in a row).** Per the code it does nothing for the game but still increments the action and reset counters (+1), because the stored observation's `action_input` gets re-applied to the scorecard. The effect is a pure efficiency loss. Verify locally with `OPERATION_MODE=competition` plus `listen_and_serve(competition_mode=True)`.
- Because full resets are impossible on Kaggle, **every action in a game counts towards the level being played.** This includes actions in failed attempts and after GAME_OVER restarts. Exploration within a level directly inflates that level's denominator.
- ACTION7 (undo) exists in the enum, but most public games do not expose it. A community post reports that Duck forks hit index errors when querying it. Treat it as usable only when present in `available_actions`.

### Gaps
- Whether an ACTION7 undo itself counts as an action is not stated. Per the code it would count like any other action (ids 1–7 → +1).
- There is no official per-request rate limit on the Kaggle gateway. The public API is limited to 600 RPM ([docs rate limits](https://docs.arcprize.org/rate_limits)), which is irrelevant offline.

---

## Q6. Scoring (RHAE): formula, 1.15 cap, level weighting, human baseline, aggregation

### Takeaway
The formulas:
- **Per completed level:** `min(115, 100·(h/a)²)`, where `h` is the human baseline actions for that level and `a` is the AI's actions spent on that level, including resets and failed attempts. An uncompleted level scores 0.
- **Per game:** the **level-index-weighted mean** (weights 1..n), **then capped at `100·Σ(weights of completed levels)/Σ(all weights)`**. So a game can never exceed 100%, and unfinished later levels cap the game hard.
- **Total:** the mean over all 110 (reported: 55) games, displayed truncated to 2 decimals in percent.
- **Human baseline:** the per-level "upper median" first-time human, which replaced the "2nd-best human" on 2026-04-14. Kaggle's data page still shows the old 1.0 cap, but the host confirmed 1.15 per level with a 100% cap per game.

### Cited Findings
- **Methodology** [OFFICIAL]:
  - "level_score = (human_baseline_actions / ai_actions) ^ 2".
  - "The maximum score per level is capped at 1.15x human baseline."
  - "The game score is the weighted average of all per-level scores, using the 1-indexed level number as the weight."
  - "it is capped based on how many levels the AI actually completed" (example: 5 levels, first 4 completed → max (1+2+3+4)/15 = 66.7%).
  - "Total score is the average of all game scores."
  - Human baseline: "multiple first-time players are observed, and the upper median human (by fewest actions) per level is recorded as the baseline. For an even number of players, the upper of the two middle entries is selected (4 players → 3rd place; 5 players → 3rd place)."
  - Source: [docs.arcprize.org/methodology](https://docs.arcprize.org/methodology)
- **Change log** [OFFICIAL] (2026-04-14): "Human baseline now uses the median human per level (previously 2nd best human). Per-level score cap increased from 1.0x to 1.15x." — [docs.arcprize.org/changelog](https://docs.arcprize.org/changelog); [arcprize.org blog: ARC-AGI-3 human dataset](https://arcprize.org/blog/arc-agi-3-human-dataset). The blog reports 458 total human participants; public demo plays range from 10 to 54 per environment; "every environment beaten by at least two participants".
- **Kaggle pages still show the old formula** [OFFICIAL but stale]: the data page gives "Per-level score = min(human_actions / agent_actions, 1.0), then squared". The Evaluation page says "scores are capped at 100%". — [Kaggle data](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/data); [Kaggle evaluation](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/evaluation). Host clarification (2026-06-08): "per level you can score up to 1.15x. This gets capped at 100% per game. You can't score >100% on a game." — [Discussion 705022](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705022)
- **[CODE] Exact implementation** (`arc_agi/scorecard.py`, identical in 0.9.8 and 0.9.9):
  - `add_level`: if completed, `score = min(((baseline/actions_taken)**2)*100, 115.0)`, else 0.
  - `to_score`: `score = Σ(level_score_i · i)/Σ i` with `i = level_idx+1`; `max_score = Σ(i for levels with score>0)/Σ i · 100`; `score = min(score, max_score)`.
  - Per-level actions are derived from `actions_by_level`, which logs `(levels_completed, cumulative_actions)` whenever `levels_completed` changes. So level k's actions = cumulative actions at completion of k minus those at completion of k−1, **including all RESETs (+1 each) and failed attempts**.
  - The per-game `EnvironmentScoreList.score = max(run.score for runs)`, i.e. the best play when multiple plays exist (impossible in competition mode).
  - The scorecard total = the plain mean of per-game scores.
  - Unplayed environments are instantiated at close in competition mode (score 0).
  - Source: [arc-agi 0.9.9](https://pypi.org/project/arc-agi/0.9.9/#files)
- **Worked example** [COMMUNITY, computed from the shipped scorer]: for cd82 (6 levels, baselines [55, 8, 41, 21, 23, 23]), "clear the first four perfectly, then stop" → 47.6, not 66.7. Taking twice the baseline on all six levels → 25.00. — [Discussion 728299](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/728299)
- **Baseline visibility** [COMMUNITY/CODE]: on 2026-04-03 a top competitor reported `environment_info.baseline_actions` visible for the 110 test games during submission. No host answer exists. — [Discussion 687655](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/687655). In 0.9.9 the REST `/api/games` endpoints exclude `baseline_actions`. — [arc-agi 0.9.9 api.py](https://pypi.org/project/arc-agi/0.9.9/#files)
- **Variance** [COMMUNITY]:
  - 11 official submissions of one identical Duck/Qwen3.6 harness scored 1.29, 1.05, 0.71, 0.73, 0.68, 0.75, 0.55, 1.11, 1.17, 0.90 and 0.94, a 2.3× spread. — [Discussion 738762](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738762); [Discussion 731522](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/731522)
  - Participants report 2.5–5.5 from the same code. — [Discussion 736578](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/736578)
  - Local public-set scores correlate weakly with the LB (e.g. 1.56 local → 0.02–0.05 LB, which the host called "inline with expectations"). — [Discussion 703990](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990)

### Inferences
- Because of the `(h/a)²` term, each level's value decays quadratically with excess actions. Because of the cap, completing an extra (later, higher-weight) level is usually worth far more than shaving actions on early ones. For a 6-level game, level 6 alone is 6/21 ≈ 28.6% of the game's cap.
- A 1.15 per-level cap can only compensate for inefficiency on *completed* levels. It can never lift a game above its completion cap.

### Gaps
- The Kaggle metric kernel (id 104668730) is private. There is no primary confirmation that the Kaggle metric uses exactly `scorecard.py` (1.15, upper median). The host's statements plus the M1-era LB values >1.15 imply it does.

---

## Q7. Official starter kit and templates (file layout, `make` commands, random agent, GPT-OSS-120B, others)

### Takeaway
The official **ARC-AGI-3-Kaggle-Starter** (created 2026-05-27) is the local-dev path:
- You edit only `agent/my_agent.py` (class `MyAgent(Agent)` with `is_done` and `choose_action`).
- `make play-local` runs every public game locally.
- `make submit` builds and pushes the Kaggle notebook.

The Kaggle-pinned official samples by `inversion` are **Random Agent**, **Stochastic Goose** (CNN action-learning, the ARC-AGI-3 preview winner) and **Just Explore**. ARC Prize also publishes a **GPT-OSS-120B on RTX PRO 6000** template (vLLM). The upstream **ARC-AGI-3-Agents** repo carries more LLM templates, which are not usable offline without local models.

### Cited Findings
- **Starter layout** [OFFICIAL]:
  - `agent/my_agent.py` ("★ The file you edit")
  - `scripts/play_local.py` (runs your agent against real games)
  - `scripts/build_notebook.py` (packages your agent into a Kaggle notebook; `ACCELERATOR = "t4"`, one of cpu/t4/p100/rtx6000)
  - `scripts/slim_framework.py` (trims framework deps)
  - `notebooks/kernel-metadata.json` (replace `REPLACE_WITH_YOUR_USERNAME`; `enable_internet: false`; `competition_sources: ["arc-prize-2026-arc-agi-3"]`)
  - `notebooks/submission.ipynb` (auto-generated)
  - `vendor/` (cloned ARC-AGI-3-Agents), `.venv/` (Python 3.12), `.kaggle/access_token` (project-local `KGAT_...` token, read into `KAGGLE_API_TOKEN`), `Makefile`
  - Source: [ARC-AGI-3-Kaggle-Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter); [docs.arcprize.org/arc-prize-2026](https://docs.arcprize.org/arc-prize-2026)
- **Make targets** [OFFICIAL]:
  - `make setup`: venv; `pip install "arc-agi>=0.9.6" "kaggle>=2.2" python-dotenv pandas pyarrow`; clone `arcprize/ARC-AGI-3-Agents` into `vendor/`; slim `agents/__init__.py`
  - `make play-local [GAME=ls20] [STEPS=200]`: runs `scripts/play_local.py --max-steps $(STEPS)` with `Arcade(OperationMode.NORMAL)`; games download on first run into `environment_files/`
  - `make verify-local`: 50 steps on ls20 and vc33
  - `make list-games`
  - `make pull-sample`: `kaggle kernels pull inversion/arc3-sample-submission-stochastic-goose`
  - `make notebook`
  - `make submit`: `kaggle kernels push -p notebooks/`
  - `make status`: `kaggle kernels status <id>`
  - `make clean`
  - After `status` shows complete, click "Submit to Competition" and pick `submission.parquet`.
  - Source: [Starter Makefile/README](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter)
- **Starter agent** [OFFICIAL]: a random policy with `MAX_ACTIONS = 80`. It returns `RESET` on NOT_PLAYED/GAME_OVER and `is_done` on WIN. For ACTION6 it calls `action.set_data({"x": randint(0,63), "y": randint(0,63)})`. It sets `action.reasoning`. It includes an example per-game fork (on ls20, ACTION4 weighted 2×). — [agent/my_agent.py](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter/blob/main/agent/my_agent.py)
- **Kaggle-pinned official samples** [OFFICIAL] (user `inversion`, Kaggle staff):
  - "ARC3 Sample Submission – Random Agent" (best public 0.18; `MAX_ACTIONS = float('inf')`)
  - "ARC3 Sample Submission – Stochastic Goose" (0.25; CNN `ActionModel` over 16-channel one-hot 64×64 input predicting action and click logits; source DriesSmit/ARC3-solution by Dries Smit and Jack Cole, Tufa Labs; `MAX_ACTIONS = inf`)
  - "ARC3 Sample Submission – Just Explore" (0.19)
  - Source: [Random Agent](https://www.kaggle.com/code/inversion/arc3-sample-submission-random-agent); [Stochastic Goose](https://www.kaggle.com/code/inversion/arc3-sample-submission-stochastic-goose); [Just Explore](https://www.kaggle.com/code/inversion/arc3-sample-submission-just-explore)
- **GPT-OSS-120B template** [OFFICIAL]:
  - Tunable parameters: `MAX_ACTIONS` (e.g. 50, "the single best knob to tune"), `MESSAGE_LIMIT` (e.g. 2), `GAME_TIME_LIMIT_S` ("Keep this low ... otherwise `scorecard not produced in time` error"), `MAX_MODEL_LEN` and `build_user_prompt`. — [docs.arcprize.org GPT OSS on Kaggle](https://docs.arcprize.org/partner_templates/gpt-oss-kaggle)
  - Code defaults: model `/kaggle/input/models/danielhanchen/gpt-oss-120b/transformers/default/1`; `vllm serve` with `--max-num-seqs 12 --max-model-len 64000 --kv-cache-dtype fp8 --tensor-parallel-size 1 --enforce-eager --tool-call-parser openai`; `ACTION_MAX_TOKENS = 8192`, `OBSERVATION_MAX_TOKENS = 512`, `LLM_REQUEST_TIMEOUT_S = 120`, `GAME_TIME_LIMIT_S = 20 min`, `FIRST_ACTION_DEADLINE_S = 14 min`.
  - In commit mode it starts a local `arc_agi` server on 127.0.0.1:8001; the log shows `idle_for=0:15:00`, `max_open_for=3 days`.
  - Source: [Kaggle: gregkamradt/arc-agi-3-gpt-oss-120b](https://www.kaggle.com/code/gregkamradt/arc-agi-3-gpt-oss-120b)
- **Upstream framework templates** [OFFICIAL]: ARC-AGI-3-Agents registers `random`, `llm`, `fastllm` (gpt-4o-mini), `reasoningllm` (o4-mini), `guidedllm` (o3), `reasoningagent`, `langgraphfunc`, `langgraphtextonly`, `langgraphrandom`, `langgraphthinking`, `smolcodingagent`, `smolvisionagent`, `multimodalllm` (MAX_ACTIONS 40) and `openclaw` (added in May 2026). Most default to `MAX_ACTIONS = 80`. The `.env.example` now points to `https://arcprize.org/` (not `three.arcprize.org`, changed 2026-08-03). — [ARC-AGI-3-Agents](https://github.com/arcprize/ARC-AGI-3-Agents). Partner templates are listed on the docs: AgentOps, HuggingFace, Anthropic, LangChain. — [docs.arcprize.org llms.txt](https://docs.arcprize.org/llms.txt)
- **Local dev tips** [OFFICIAL]: "The local `arc-agi` PyPI package hosts the same game engine the Kaggle gateway runs. If it works locally, it works on Kaggle." — [Starter README](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter). Host advice: test no-op counting and other scoring behaviour offline in competition mode. — [Discussion 718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638)
- **De facto community baseline** [COMMUNITY]: nearly all high public notebooks build on Tufa's open "TAAF/Duck harness" (June 30 milestone winner), with Qwen 3.6/3.8 27B FP8 or "Qwen 3.8 Flash Next NVFP4" on the RTX PRO 6000. — [Discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801); [Kaggle notebooks list](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/code)

### Inferences
- The starter's `play_local.py` uses `OperationMode.NORMAL` in-process, **not** competition mode. It therefore permits full resets and multiple plays, and it takes the best run, so local scores can be optimistic. For faithful local evaluation, run `listen_and_serve(competition_mode=True)` and point the agent at it with `OPERATION_MODE=online`.
- Override `MAX_ACTIONS` (default 80 → 81 actions) or the agent silently stops early.

### Gaps
- The "Just Explore" sample source was not retrieved (only its output parquet, oddly with columns `task_id, output`). Its algorithm is not documented here.

---

## Q8. Rule changes and clarifications (March–September 2026)

### Takeaway
The important host-side changes were:
- H100s added (Apr 28), then **replaced by the RTX PRO 6000** (May 7)
- **Runtime raised from 6 h to 9 h** (May 7; fully effective May 19)
- **Scoring changed** to the upper-median baseline and 1.15 cap (Apr 14)
- **Submission cap** accidentally raised to 5/day (May 27), then **restored to 1/day with surplus submissions invalidated** (Jun 8–9)
- Milestone open-sourcing deadline clarified as 23:59 UTC (Jun 24)
- **No 5× action cap on Kaggle** (Jun 25)
- Private scores fixed at run time (Jul 27)
- RTX capacity/queue fixes (Aug–Sep)

### Cited Findings (chronological)
- **2026-03-25**: launch; only P100/2×T4 at first; "Our intent is to offer H100s". — [Discussion 684724](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/684724)
- **2026-03-26**: "Submissions run on all 110 tasks." — [Discussion 684852](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/684852)
- **2026-04-06**: local open-weight Qwen3.5 is allowed if run offline and open-sourced as required. — [Discussion 688481](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/688481)
- **2026-04-14**: scoring update (median baseline, 1.15 cap), online scorecard max-open capped at 24 h, and 15 public game version bumps. — [docs changelog](https://docs.arcprize.org/changelog)
- **2026-04-23**: games are seeded and deterministic. — [Discussion 694153](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/694153)
- **2026-04-28**: H100 accelerators added. — [Discussion 695158](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/695158)
- **2026-05-04**: "allocation for H100s fluctuates a lot". — [Discussion 696615](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/696615)
- **2026-05-07**: H100 stockout → RTX 6000 Pro (g4-standard-48). Runtime raised from 6 h to 9 h. — [Discussion 697720](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697720); [Discussion 697944](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697944)
- **2026-05-12**: "output a submission.parquet file manually ... isn't used". Frames are logged to append-only JSONL, not held in memory. — [Discussion 698507](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/698507); [Discussion 697423](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/697423)
- **2026-05-15**: using the 25 public game files (e.g. deep-copying the game) is OK because they are open source; the same affordance does not exist for private games. — [Discussion 699900](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699900)
- **2026-05-19**: the hidden 6 h ARC-specific limit was fixed, giving the full 9 h. — [Discussion 699208](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/699208)
- **2026-05-21**: available_actions are constant per game. — [Discussion 702079](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/702079)
- **2026-05-27**: official Kaggle Starter released, and the submission cap was mistakenly changed to 5/day. — [Starter repo history](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter/commits/main); [Discussion 705405](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705405)
- **2026-06-03**: the public demo is easier than the semi-private set; budget time for 110 games. — [Discussion 703990](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/703990)
- **2026-06-08/09**: cap restored to 1/day and surplus submissions from May 27–Jun 8 invalidated. Teams over the cumulative allowance (days × 1) cannot submit until back under it (e.g. "81 of 76"). — [Discussion 705405](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705405); [Discussion 705094](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705094); [Discussion 705198](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705198)
- **2026-06-08**: 1.15 per-level cap, 100% per-game cap. — [Discussion 705022](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/705022)
- **2026-06-11**: assume 64×64 grids. — [Discussion 707717](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/707717)
- **2026-06-12**: no evidence of game-file exploits on private eval games. — [Discussion 707925](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/707925)
- **2026-06-24**: milestone open-source deadline is 23:59 UTC on Jun 30 / Sep 30. — [Discussion 713634](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713634)
- **2026-06-25**: no 5× action cap on Kaggle. — [Discussion 713921](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/713921)
- **2026-07-07/08**: dead/no-op clicks count as actions; the docs wording is to be clarified. — [Discussion 718638](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/718638)
- **2026-07-13**: Milestone #1 winners announced; M2 ends Sep 30. — [Discussion 725002](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/725002)
- **2026-07-17**: Kaggle container limits (10 MB logs, 20 GB /kaggle/working, 30 GB RAM CPU cgroup, no RLIMIT_AS/NPROC). — [Discussion 724841](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/724841). The 500-errors analysis. — [Discussion 727119](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/727119)
- **2026-07-27**: private scores computed at run time, both halves played, 9 h for v3. — [Discussion 729985](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/729985)
- **2026-08-03**: ARC-AGI-3-Agents switched the default API host from `three.arcprize.org` to `arcprize.org` (PR #74). — [Discussion 732419](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/732419); [repo](https://github.com/arcprize/ARC-AGI-3-Agents)
- **2026-08-14 to 2026-09-22**: RTX PRO 6000 capacity constraints and queue fixes; the "queued" status glitch was acknowledged as display-only ("your score is valid"). — [Discussion 735147](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/735147); [Discussion 739674](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/739674); [Discussion 742148](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742148)

### Inferences
- No changes have been announced to the final deadline (Nov 2), the 2 final selections, or the 1/day cap. As of 2026-09-25 the rules page still carries the milestone split $25K / $7.5K / $5K.
- Pending issues worth watching before Nov 2:
  - requests for a "model freeze" before the end (raised in [Discussion 742801](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742801), with no host response)
  - RTX queue capacity
  - the team-size enforcement question

### Gaps
- There was no host response by 2026-09-25 on: the fixed public/private split across runs ([Discussion 738762](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/738762)), baseline visibility ([Discussion 687655](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/687655)), synthetic data ([Discussion 742940](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/742940)), or whether an arc-agi wheel update will reach the Kaggle environment ([Discussion 728220](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/728220)).
- The Discord (not staff-monitored per [Discussion 684625](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/684625)) and the ARC Prize newsletter were not searched.
