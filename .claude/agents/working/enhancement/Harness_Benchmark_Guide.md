# Harness Benchmark Guide

> **Devkit-internal only — deliberately not mirrored to `templates/`.** This measures our own harness's spawn cost; it is not a feature target projects receive. Same intentional divergence as the Token-Trace Log (`orchestrator_instructions.md`).
>
> **Read by the orchestrator.** A spawned Developer must not read this file — knowing it is being benchmarked changes what it reads. Give the agent only the arm's issue and the trace block.

**Trigger:** user says **"run harness benchmark"** (aliases: "benchmark the harness", "A/B the harness").

---

## 1. What this measures, and what it cannot

An A/B of **two Developer spawns on the same story against two harness states**. The dependent variable is spawn cost: which files the agent read before starting work, how many, and how large.

It cannot measure output quality, and it cannot be trusted from a single run per arm. Two runs of ST-000131 on 2026-08-20 came in at ~31,000 and ~25,150 self-reported tokens with 15 vs 36 step lines — the variance between two runs of one story exceeded most effects worth detecting.

**One rule outranks everything below:** never quote the *nominal* baseline — what the rules said to read — as the "before" figure. Runs skip mandatory reads (see `Agent_Common_Split_Findings.md §1`), and the apparent cheapness of a non-compliant run **is** the skipped reads. Compare actual against actual, or you will publish a saving that is really a safety regression.

## 2. Choosing the baseline

The baseline branch decides which question you are answering. Pick deliberately.

| Baseline | Question it answers | Use when |
|---|---|---|
| `main` | "Is this branch worth merging over what ships today?" | Pre-merge release decision — the usual case |
| A specific commit | "Did *this one change* help?" | The branch stacks several changes and you need attribution |

`main` is correct for the merge decision and is the default. Its limit is attribution: if the branch bundles four changes, a `main` delta belongs to all four and must be reported that way — "the branch is worth merging", never "change X saved Y".

Confirm the base with `git merge-base <arm-branch> <other-arm>` rather than trusting branch names. On the 2026-08-20 pair the names inverted the arms: `ST-000131` was based on `c33b96f` (**treatment**) while `ST-000131-2` was based on `87d49b9` (**baseline**), so reading them by name reversed the result.

## 3. Choosing the story

The story must be **the same work on both arms**. Requirements:

- **Touches no file that differs between the arms.** Check with `git diff --name-only <baseline>..<treatment>` and pick a target outside that list. A story editing a file the treatment branch renamed does different work on each arm and measures nothing.
- **Small and fully specified.** Ambiguity lets the two arms diverge on judgment rather than on harness. Spell out the ACs.
- **No manifest bookkeeping.** No story bumps a version any more (the `release` workflow owns `VERSION`), but both arms would still fold into the same `changes.json` key from different bases and conflict. Put `changes.json` and `CHANGELOG.md` explicitly out of scope in the story body.
- **Realistic path.** It should still exercise branch → edit → validate → commit → PR, or it will not touch the rules the harness change affects.

Real backlog work is preferable to synthetic work — the winning arm's PR can then be reopened as genuine delivery.

## 4. Contamination controls

Four kinds of state survive a branch checkout. All four have been observed to leak.

| State | Why it leaks | Control |
|---|---|---|
| Working Record | `.gitignore:40` — untracked, survives checkout | Snapshot before arm 1; restore before arm 2 |
| `token-trace_sprint/` | `.gitignore:50` — untracked, survives checkout | **Empty it for the run**, restore after. Equalising is not enough — see below |
| The GitHub issue | No checkout touches it | **One issue per arm.** See below |
| Memory | Tracked, so it *does* flip | None needed — verify it flipped |

**Empty the trace directory, do not merely equalise it.** Retained traces are artifacts of whichever harness produced them, and agents read them as format examples. This is hygiene, not a fix for the leak below — the leak survived an empty trace directory.

**The issue is the worst of these.** Arm 1 posts comments, sets `status:review`, links a PR. Arm 2 then runs `gh issue view --json body,title,labels,comments` and sees the work already done. This is not hypothetical: on 2026-08-20 arm 1 pulled "issue body + labels" while the second arm pulled "issue body + **2 comments** + labels", and part of that run's cost difference is this and not the harness.

Create two issues with identical bodies, labelled `test:benchmark`, each naming its arm and instructing the agent not to read the other. Run the **baseline arm first** so any residue you failed to control lands on the treatment arm, where it works against the change rather than for it.

## 4a. The baseline arm cannot be made clean inside a treatment session

**This is the method's hard limit. Read it before quoting any baseline figure.**

Every spawned agent receives two startup inputs that a `git checkout` cannot touch:

1. **The `# claudeMd` system-reminder**, carrying the user's project auto-memory. If any memory names the change under test, every agent knows it exists before reading a file.
2. **The `<env>` git status block** — branch name and recent commit subjects, snapshotted at *session* start, not at spawn. An agent working on a `main`-based branch still sees the treatment branch's commit log.

Measured on 2026-08-21: both baseline-arm agents, in separate runs, reported that their spawn prompt named `*_Bootstrap.md` paths. **Neither prompt did.** Asked directly, the second agent confirmed it invented the filenames by pattern-guessing from `MEMORY.md`'s index line and the commit subjects `Apply bootstrap + read-on-demand split…`, then wrote them up as though the prompt had listed them. It also flagged a second confabulation it had presented as a finding earlier in the same run.

**What this does and does not spoil.** The read set stays valid — an agent that expects a split still reads whatever its harness actually mandates, and the wrong expectation cost only one directory listing (~250 tok). What is spoiled is **anything the agent says about its own inputs**, and any claim that the baseline arm was naive.

**Controls:**
- Treat every agent Observation about its own prompt or context as unverified. Quote it back and ask for the source before recording it as a finding. Both leaks in this series surfaced only because someone re-read the prompt.
- For a genuinely naive baseline, run the baseline arm from a **separate session started on the baseline branch**, with project auto-memories that name the change moved aside for the duration.
- Never report the baseline arm as "unaware of the treatment" without having done the above.

## 5. Runbook

1. Create the paired issues (§4) and confirm both arms' bases (§2).
2. Snapshot the two untracked directories into the scratchpad:
   `cp -r .claude/agents/working/working-record .claude/agents/working/token-trace_sprint <scratchpad>/bench-snapshot/`
3. `git checkout -b bench-b/<slug> <baseline>` — spawn Developer on the arm B issue.
4. **Paste the trace block verbatim** from `orchestrator_instructions.md § Token-Trace Log`. Without it the agent produces no trace and the run is wasted.
5. On completion, append the real `subagent_tokens` to the trace file, labelled `session-cumulative` or `per-call` — or `(unlabelled)` if the report does not say. Never write a derived figure as a measurement.
6. Restore the snapshot from step 2.
7. `git checkout -b bench-a/<slug> <treatment>` — repeat steps 3–5 for arm A.
8. Compare, then clean up (§7).

## 6. Reading the result

Compare **pre-work read sets first, cost second.** The read set is the thing the harness actually controls; token totals are downstream of it and noisier.

Known traps, all previously hit:

- **`subagent_tokens` is unresolved.** Rounds have reported 70,652 / 77,975 / 77,274 where round 3 made zero tool calls and still came in lower than round 2 — neither per-call nor strictly cumulative. Do not derive from it beyond the labelled subtraction in `orchestrator_instructions.md`.
- **Step granularity is not comparable across arms.** 15 steps vs 36 steps for the same story means the two agents chunked their own reporting differently. Compare files read, not step counts, and treat self-reported totals as ordinal at best.
- **The JSONL transcript has written 0 bytes on every run so far** — a reproducible harness limitation. Read sets are self-reported and corroborated only by behavioural tells (which grep patterns appeared, which sections got quoted). Say so in the findings.
- **Task shape flips the sign.** A tiered harness is cheaper on narrow tasks and dearer on full story spawns — measured at −63% and +15% on the same file. One story shape does not generalise; state which shape you ran.
- **Bootstrap placement guarantees loading, not application.** An agent can carry a rule in context for nineteen steps and still write from memory of its shape. Reading the file is not evidence the rule was followed; check the output for the literal details only a real read produces.

Write findings to `.claude/agents/working/enhancement/<Topic>_Findings.md` alongside the existing ones.

## 7. Cleanup

- Close both arm PRs unmerged. Reopen the winner as real work through the normal story path if the change is worth keeping.
- Close both issues; the `test:benchmark` label keeps them out of backlog counts.
- Delete both `bench-*` branches.
- Leave the trace files — they are the record. Note the run in the Orchestrator Working Record.
- **Do this in the same session that ran the round, before starting anything else.** The #148/#149 round (§8) sat open for 3 days; its untracked trace/working-record artifacts got overwritten before comparison, and the round became unrecoverable data loss rather than a finding. A pending round blocks starting a new one — §4's contamination controls assume a clean slate.

## 8. Prior runs

| Date | Story | Arms | Outcome |
|---|---|---|---|
| 2026-08-20 | ST-000131 | `c33b96f` (treatment) vs `87d49b9` (baseline) | Confounded — shared issue, arm names inverted. See `Agent_Common_Split_Findings.md` |
| 2026-08-21 | #144 / #145 | `agent-enhancement` vs `main` | Read set −43.5%; first actual-vs-actual pair. See `Bench_2026-08-21_Findings.md`. Winning arm (A) reopened as real work — PR #147, tracked under #144. |
| 2026-08-21 | #148 / #149 | `agent-enhancement` vs `main` | **Abandoned before comparison — no findings written.** Both arms completed and opened PRs (#151, #150), but were never compared or closed out; §7 cleanup ran 2026-08-24, ~3 days late. Arm A's trace file (12 steps, ~19.4k tok estimated / 69,915 unlabelled actual) survived as untracked residue and was read as this round's only surviving artifact; arm B's trace was never captured. No usable read-set comparison — treat as lost data, not a null result. |
| 2026-08-21 | #152 / #153 | (not run) | Paired issues created, never executed — no branches, no PRs, no trace. Closed 2026-08-24 as setup-only debris. |
| 2026-08-24 | #154 / #155 | `agent-enhancement` (539f3a0) vs `main` (87d49b9) | Read set −25.7% (67,468 → 50,157 bytes) — about half round 1's effect, traced to a specific cause: `be3988b` moved `Developer_Rules` §1-§6 back to bootstrap after round 1, so that file now contributes ~0% of the saving; `Agent_Common`/`Project_Priming` splits still carry it. Both arms ran in this session (§4a control not used, by explicit user choice); the confabulation leak recurred a third time regardless. See `Bench4_2026-08-24_Findings.md`. |
| 2026-08-24 | #158 / #159 | `agent-enhancement` (a6c0a2e) vs `main` (87d49b9) | **First full Dev→TL→QA pipeline round.** Byte-measured read set −27.7% as-reported (−27.2% compliance-adjusted); `subagent_tokens` sum only −5.8% — TL and QA individually ran *higher* on tokens in treatment, confirming the shape-effect risk flagged pre-`be3988b`. Two independent compliance gaps surfaced (Dev/treatment skipped a mandatory Story-Standard read; QA/baseline skipped two) — both need follow-up stories, not waved off as benchmark noise. Output diverged genuinely (different file location, different extraction strategy) yet both independently validated correct — strongest quality-parity signal so far. §4a leak recurred a fourth time. Both arms ran in this session, by explicit user choice. See `Bench5_2026-08-24_Findings.md`. |

## 9. Cumulative verdict — does the split earn its place?

**Update this section after every round that adds an actual-vs-actual data point (§1's rule).** It answers three questions any stakeholder will ask before trusting §8's table. Superseded by a later round's numbers; keep only the current read.

### 9a. Does it bring value, and how much?

Real, but smaller than the headline number and shrinking, not flat:

| Round | Shape | Read set (byte-measured) | `subagent_tokens` (self-reported, noisy — §6) |
|---|---|---|---|
| 2026-08-21 (#144/#145) | Narrow, single Developer spawn | −43.5% (58,019→32,780) | −12.7% |
| 2026-08-24 (#154/#155) | Narrow, single Developer spawn | −25.7% (67,468→50,157) | −10.2% |
| 2026-08-24 (#158/#159) | **Full Dev→TL→QA pipeline** | −27.7% sum, −27.2% compliance-adjusted (157,783→114,089 B) | **−5.8%** sum (283,800→267,437) — TL +11.6%, QA +16.5% individually |

The drop between rounds 1→4 is attributable, not noise: `be3988b` (post-round-1) moved `Developer_Rules` §1–§6 back into bootstrap to close a compliance gap, so that file now contributes **~0%** of the saving — all of round 4's gain is `Agent_Common` (−49.0%) and `Project_Priming` (−46.8%) alone.

**Round 5 is the first full-pipeline measurement, and it confirms the shape-effect risk directly rather than by indirect signal.** The byte-measured read-set saving replicates (−27 to −39% per role) but the aggregate `subagent_tokens` effect nearly vanishes (−5.8%) because implementation/verification/comment-writing work — identical in both arms — dominates a full spawn's total cost far more than it does a narrow task's. TL and QA ran individually *more* expensive in the treatment arm, driven by a benchmark-setup artifact (see `Bench5_2026-08-24_Findings.md` §4), not the split itself. **The one indirect prior signal** (`Bootstrap_OnDemand_Split_Notes.md`, pre-`be3988b`) measured `Developer_Rules` at **+15% on a full spawn** vs **−63% on a narrow task** — round 5 doesn't reproduce a net-negative sign at the aggregate level, but it does confirm the direction: full-pipeline gains are real at the read-set layer and much smaller in token terms than narrow-task rounds suggested.

Round 5 also surfaced two compliance gaps unrelated to each other: Developer/treatment skipped a mandatory `Story_Standard_Dev.md` read (same class `be3988b` was meant to close — possible regression, unconfirmed), and QA/baseline skipped two mandatory reads on `main` itself (pre-existing, unrelated to the split). Both need their own follow-up stories.

### 9b. Do the two arms' *output* differ, and which is better?

**No difference found, on either round checked by diffing the actual PRs rather than trusting self-reports.** Round 4: `git diff`ing PR #156 (baseline) against PR #157 (treatment) showed the code change to `Story_Standard_Dev_template.md` was **byte-for-byte identical**. Round 5 is a stronger test: the two arms' `read_sections.sh` implementations **genuinely diverged** (different file location, different extraction strategy — bash-array-scan-and-`sed` vs per-marker `awk` state machine), so neither arm could free-ride on the other's design. Both were independently validated as fully correct by their own arm's TL and QA, including edge cases (the `11a`/`11b` non-swallowing case, `## Version`-footer termination, EOF-as-last-section) that went beyond each Developer's own verification list. No quality gap found despite genuine implementation independence.

This is now n=2 (one trivial/identical, one genuinely divergent). Reassuring in both directions, but still does not cover a story ambiguous enough that thinner upfront context could plausibly cause a real mistake — none tested so far have been.

### 9c. Is it worth it?

**Qualified yes — worth keeping the branch, and now measured on the workload that matters most, but two open compliance questions block full confidence.**

For it: three independent byte-measured rounds, all positive, including the first full-pipeline measurement; zero quality cost found across two rounds of actual-PR diffing, one of them a genuinely divergent implementation; the split's read-set saving holds up at the role level (Dev, TL, QA all individually positive) even though the aggregate token saving is small.

Against full confidence: aggregate `subagent_tokens` on the full-pipeline shape is only −5.8%, confirming (not just risking) that most of a full spawn's cost is shape-invariant work the split cannot touch; round 5 surfaced two unresolved compliance gaps (Developer/treatment skipping a mandatory Story-Standard read — a possible regression of the exact class `be3988b` fixed; QA/baseline skipping two mandatory reads, a pre-existing gap unrelated to the split) that must be investigated before this round's read-set numbers can be trusted as clean; `subagent_tokens` remains unreliable per §6 and should never be the headline figure; the baseline arm still has not been run from a genuinely separate session (§4a) — the confabulation leak has now recurred four times.

**Next round that would resolve this:** re-run a full-pipeline round only after (a) the two compliance gaps are investigated and either fixed or explained, and (b) the baseline arm runs from a genuinely separate session per §4a. Until both land, treat round 5's numbers as directionally consistent with rounds 1 and 4, not as a clean confirmation.

---

## Version

**Version:** 1.6 — Recorded round 5 (2026-08-24, #158/#159) in §8: first full Dev→TL→QA pipeline round. Read set −27.7% (holds up per-role); `subagent_tokens` sum only −5.8%, directly confirming the shape-effect risk §9a previously carried only as indirect evidence. Two new compliance gaps found (Dev/treatment skipped a mandatory read; QA/baseline skipped two); §9b upgraded to n=2 with a genuinely divergent (not byte-identical) implementation pair, still no quality gap; §9c's "next round" now gates on fixing the compliance gaps and running a genuinely separate baseline session, not just "run a full pipeline" (done, but not cleanly).
**Previous:** 1.5 — Added §9, a cumulative verdict section (value / arm-quality / worth-it) that updates after each actual-vs-actual round instead of leaving readers to reconstruct the answer from §8's table. First pass covers rounds 1 and 4.
**Previous:** 1.4 — Recorded round 4 (2026-08-24, #154/#155) in §8: read set −25.7%, with the shrunken effect traced to a specific post-round-1 commit rather than left as unexplained noise. Third occurrence of the §4a confabulation leak, from a spawn prompt that named zero filenames — strengthens §4a's evidence, no wording change needed. **Created:** 2026-08-21. Extracted from the ST-000131 and #134 test rounds; codifies the baseline-choice, story-choice, and contamination rules those runs learned the hard way. Devkit-internal, not mirrored to `templates/`.
