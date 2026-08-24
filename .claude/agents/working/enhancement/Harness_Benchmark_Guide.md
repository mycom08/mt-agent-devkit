# Harness Benchmark Guide

> **Devkit-internal only — deliberately not mirrored to `templates/`.** This measures our own harness's spawn cost; it is not a feature target projects receive. Same intentional divergence as the Token-Trace Log (`Orchestrator_Guide.md`).
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
- **No version bump.** Both arms would bump to the same number from different bases, producing divergent releases. Put `version.txt` and `changes.json` explicitly out of scope in the story body.
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
4. **Paste the trace block verbatim** from `Orchestrator_Guide.md § Token-Trace Log`. Without it the agent produces no trace and the run is wasted.
5. On completion, append the real `subagent_tokens` to the trace file, labelled `session-cumulative` or `per-call` — or `(unlabelled)` if the report does not say. Never write a derived figure as a measurement.
6. Restore the snapshot from step 2.
7. `git checkout -b bench-a/<slug> <treatment>` — repeat steps 3–5 for arm A.
8. Compare, then clean up (§7).

## 6. Reading the result

Compare **pre-work read sets first, cost second.** The read set is the thing the harness actually controls; token totals are downstream of it and noisier.

Known traps, all previously hit:

- **`subagent_tokens` is unresolved.** Rounds have reported 70,652 / 77,975 / 77,274 where round 3 made zero tool calls and still came in lower than round 2 — neither per-call nor strictly cumulative. Do not derive from it beyond the labelled subtraction in `Orchestrator_Guide.md`.
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

## 9. Cumulative verdict — does the split earn its place?

**Update this section after every round that adds an actual-vs-actual data point (§1's rule).** It answers three questions any stakeholder will ask before trusting §8's table. Superseded by a later round's numbers; keep only the current read.

### 9a. Does it bring value, and how much?

Real, but smaller than the headline number and shrinking, not flat:

| Round | Shape | Read set (byte-measured) | `subagent_tokens` (self-reported, noisy — §6) |
|---|---|---|---|
| 2026-08-21 (#144/#145) | Narrow, single Developer spawn | −43.5% (58,019→32,780) | −12.7% |
| 2026-08-24 (#154/#155) | Narrow, single Developer spawn | −25.7% (67,468→50,157) | −10.2% |

The drop between rounds is attributable, not noise: `be3988b` (post-round-1) moved `Developer_Rules` §1–§6 back into bootstrap to close a compliance gap, so that file now contributes **~0%** of the saving — all of round 4's gain is `Agent_Common` (−49.0%) and `Project_Priming` (−46.8%) alone.

**Both measured rounds are the shape that favours the split.** No full TL→Dev→QA story spawn has been benchmarked. The one indirect signal on that shape (`Bootstrap_OnDemand_Split_Notes.md`, pre-`be3988b`) measured `Developer_Rules` at **+15% on a full spawn** vs **−63% on a narrow task** — the workload this repo actually runs most is the one direction of evidence points against, and it is untested end-to-end since the revert.

### 9b. Do the two arms' *output* differ, and which is better?

**No difference found, on the one round checked by diffing the actual PRs rather than trusting self-reports.** Round 4: `git diff`ing PR #156 (baseline) against PR #157 (treatment) showed the code change to `Story_Standard_Dev_template.md` was **byte-for-byte identical** — same table cell, same step removed, same renumbering — and both passed `validate_templates.py` and every AC. The only difference was a cosmetic CHANGELOG tag (arm A resolved the real `ST-000113` number via an extra `gh issue view`; arm B echoed its benchmark issue's own tag) — an artifact of which issue each arm was given, not a harness effect.

This is n=1 for a literal diff comparison. It is reassuring (cheaper with no observed quality cost) but does not cover a story ambiguous enough that thinner upfront context could plausibly cause a real mistake — none tested so far have been.

### 9c. Is it worth it?

**Qualified yes — worth keeping the branch, not yet worth trusting a specific percentage.**

For it: two independent byte-measured rounds, both positive; zero quality cost found where actually checked; the one correctness risk the split introduced (Developer_Rules reads skipped) was caught and fixed before it shipped.

Against full confidence: the effect is shrinking as more content returns to bootstrap for correctness, not stable; the workload run most often (full multi-role story) is unmeasured post-fix and the only related prior signal is unfavourable; `subagent_tokens` remains unreliable per §6 and should never be the headline figure.

**Next round that would resolve this:** a full TL→Dev→QA story spawn, `agent-enhancement` vs `main`, run from a genuinely separate baseline session (§4a) rather than the same-session shortcut — this is the load-bearing gap, not another narrow-task round.

---

## Version

**Version:** 1.5 — Added §9, a cumulative verdict section (value / arm-quality / worth-it) that updates after each actual-vs-actual round instead of leaving readers to reconstruct the answer from §8's table. First pass covers rounds 1 and 4.
**Previous:** 1.4 — Recorded round 4 (2026-08-24, #154/#155) in §8: read set −25.7%, with the shrunken effect traced to a specific post-round-1 commit rather than left as unexplained noise. Third occurrence of the §4a confabulation leak, from a spawn prompt that named zero filenames — strengthens §4a's evidence, no wording change needed. **Created:** 2026-08-21. Extracted from the ST-000131 and #134 test rounds; codifies the baseline-choice, story-choice, and contamination rules those runs learned the hard way. Devkit-internal, not mirrored to `templates/`.
