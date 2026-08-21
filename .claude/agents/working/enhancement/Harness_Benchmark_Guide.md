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

## 8. Prior runs

| Date | Story | Arms | Outcome |
|---|---|---|---|
| 2026-08-20 | ST-000131 | `c33b96f` (treatment) vs `87d49b9` (baseline) | Confounded — shared issue, arm names inverted. See `Agent_Common_Split_Findings.md` |
| 2026-08-21 | #144 / #145 | `agent-enhancement` vs `main` | Read set −43.5%; first actual-vs-actual pair. See `Bench_2026-08-21_Findings.md` |

---

## Version

**Version:** 1.2 — Added §4a. The v1.1 attribution was wrong: emptying the trace directory did not stop the leak. The real source is session-level (auto-memory + the session-start `<env>` commit log), and the agent confabulated the filenames on top of it.
**Previous:** 1.1 — §4 hardened: empty the trace directory rather than equalising it. **Created:** 2026-08-21. Extracted from the ST-000131 and #134 test rounds; codifies the baseline-choice, story-choice, and contamination rules those runs learned the hard way. Devkit-internal, not mirrored to `templates/`.
