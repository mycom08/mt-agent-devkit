# Top Four Agent Harness Fixes — Implementation Guide

**Status:** Ready for implementation planning
**Audience:** Implementers, including smaller Codex models
**Scope:** The first implementation batch from the token-efficiency reviews
**Date:** 2026-09-21

## 1. Purpose

This document turns the first four recommended fixes into explicit implementation work.
It is intentionally detailed so an implementer does not need to rediscover the analysis
or guess which behavior is required.

The four fixes in this guide are:

1. Add trustworthy token and request telemetry.
2. Make independent tool operations run in parallel or in one bounded batch.
3. Fix the stale mandatory-section references and prevent the drift from returning.
4. Add branch preflight and remove agent-memory commits from product branches.

These are the first batch because they provide measurement, reduce repeated context
replay, correct a known instruction defect, and prevent avoidable reruns caused by bad
Git state.

## 2. Source Documents

Read these before implementing any fix:

1. `docs/reviews/Agent_Harness_Token_Efficiency_Analysis.md`
2. `docs/reviews/Token_Cost_Model_and_Priorities.md`
3. `docs/reviews/Independent_Token_Efficiency_Review.md`
4. `docs/Agent_Workflow_Test_Strategy.md`
5. `docs/Template_Test_Strategy.md` when changing the validator or fixtures

The working cost model is:

> Cost is driven mainly by request count multiplied by retained context depth.

Do not treat the final session counter as total API usage or invoice cost. Do not report
estimated values as measured values.

## 3. Scope and Non-Goals

### In scope

- The four fixes listed in Section 1.
- Both distributable templates and the devkit's working mirrors.
- GitHub and strict-mode behavior where the fix applies.
- Deterministic validation and fixtures for rules that can be checked statically.
- Before-and-after measurement using the same representative story shape.

### Not in scope for this batch

- The full stage-specific read-profile migration.
- Removing Technical Lead or QA independence.
- Replacing QA behavior checks with CI.
- Rewriting all Memory, Working Record, or retrospective rules.
- Building every proposed bounded helper.
- Using session-final token thresholds as the only release gate.

Create follow-up work rather than silently expanding a fix into one of these areas.

## 4. Rules for Every Fix

Apply these rules to every implementation story created from this guide:

1. Use one focused branch and PR per fix unless two changes cannot work independently.
2. Read the current source before editing. Do not implement from this guide alone when
   repository content has changed.
3. Edit the source under `.claude/agents/templates/` first.
4. Update the corresponding working mirror in the same change when a mirror exists.
5. Search all template and working trees for the old wording before declaring the change
   complete.
6. Never edit `VERSION`. The release workflow owns it.
7. Read `VERSION`, then add changed template paths to the existing matching `-SNAPSHOT`
   entry in `changes.json`. Use `new`, `modified`, and `removed` correctly and add a
   short description. Do not create a new version key.
8. Add one concise entry under the current Unreleased heading in `CHANGELOG.md` when the
   implementation changes distributed behavior.
9. Run `python scripts/validate_templates.py` after every template or workflow change.
10. Run `bash scripts/test/run.sh` after changing the validator or its fixtures. On a
    Windows environment where Bash cannot start, execute the same fixture cases directly
    and state that substitution in the verification report.
11. Preserve unrelated user changes and pre-existing untracked files.
12. Never weaken secrets handling, authority boundaries, review gates, or truthful test
    reporting to save tokens.

## 5. Recommended Delivery Order

Use this order:

1. **FIX-01 — Telemetry.** Establish the baseline before optimizing behavior.
2. **FIX-03 — Mandatory-section drift.** Apply the small correctness fix and validator
   protection early.
3. **FIX-02 — Parallel tool execution.** Measure the change using FIX-01 telemetry.
4. **FIX-04 — Branch and agent-state safety.** This can be implemented independently,
   but must be complete before controlled workflow benchmarks.

FIX-03 and FIX-04 may proceed in parallel with FIX-01 if different implementers own them.
FIX-02 must not claim savings until FIX-01 produces a usable before-and-after comparison.

---

## 6. FIX-01 — Trustworthy Token and Request Telemetry

### 6.1 Problem

Current evidence mixes several different quantities:

- final session-context counters;
- cumulative API usage;
- cache creation and cache reads;
- output tokens;
- estimated values written by agents.

Some trace files leave the actual value blank. The same counter has also been described
as both consumption and final context size. This prevents reliable comparisons.

### 6.2 Required outcome

After every agent stage, the orchestrator must write one structured telemetry record.
The record must identify the story, role, stage, model, session mode, request count, tool
invocation count, usage fields when available, duration, and completion result.

Missing measurements must be stored as `null` with an explanation. They must never be
estimated and presented as actual measurements.

### 6.3 Canonical field definitions

Use these meanings consistently:

| Field | Required | Meaning |
|---|---:|---|
| `schema_version` | Yes | Telemetry schema version, initially `1` |
| `run_id` | Yes | Stable identifier for one pipeline run |
| `story_id` | Yes | Story identifier, for example `ST-000161` |
| `role` | Yes | Developer, TL, QA, PO, BA, or UI/UX |
| `stage` | Yes | Implementation, review, QA, closure, refinement, or another named stage |
| `session_mode` | Yes | `fresh`, `same_session_resume`, or `expired_session_resume` |
| `model` | Yes | Exact model identifier when reported; otherwise `unknown` |
| `started_at` | Yes | UTC timestamp |
| `ended_at` | Yes | UTC timestamp |
| `duration_ms` | Yes | Elapsed wall time in milliseconds |
| `completion_status` | Yes | `completed`, `blocked`, `failed`, or `interrupted` |
| `usage_source` | Yes | `raw_transcript`, `harness_report`, or `unavailable` |
| `session_final_tokens` | No | Final-call/session-context counter; not cumulative usage |
| `requests` | No | Deduplicated assistant/API requests |
| `tool_invocations` | No | Count of raw tool-use events, not count of unique tool names |
| `input_tokens` | No | Cumulative fresh input tokens |
| `cache_creation_input_tokens` | No | Cumulative cache-write input tokens |
| `cache_read_input_tokens` | No | Cumulative cache-read input tokens |
| `output_tokens` | No | Cumulative generated tokens |
| `unavailable_fields` | Yes | Array naming every unavailable optional field |
| `notes` | Yes | Short factual note; use an empty string when none |

Do not put model pricing into the trace schema. Pricing changes independently. Calculate
cost later from measured usage plus a versioned pricing table.

### 6.4 Storage rules

1. Store runtime telemetry as JSON Lines: one JSON object per completed stage.
2. Use a runtime path under the installed agent directory, for example:
   `{{AGENT_DIR_PREFIX}}/agents/tmp/token-metrics/<run-id>.jsonl`.
3. The telemetry directory must be gitignored in GitHub mode. Strict mode already ignores
   the entire installed agent directory.
4. Do not store absolute transcript paths, secrets, issue tokens, or prompt content in a
   telemetry record.
5. Do not commit runtime telemetry to a product branch.
6. A separate exported benchmark artifact may be committed only when a story explicitly
   requires it and the data has been checked for sensitive paths and content.

### 6.5 Implementation steps

1. Inspect `.antigravity/agents/working/tokentrace/token_cost.sh` and its `README.md`.
   Reuse its verified request-deduplication and output-token rules instead of inventing a
   second calculation.
2. Define the schema in one authoritative document or script. Do not define slightly
   different fields in every role instruction.
3. Add one orchestrator-owned collection step immediately after each agent completion.
   The agent must not estimate its own invisible usage.
4. Collect universally available fields first: run, story, role, stage, timestamps,
   status, session mode, and any harness-reported final counter.
5. When a raw transcript is available, deduplicate events by request/message identifier.
   Count every raw tool-use event once. Use the final output-token value in each streamed
   message group rather than the first partial value.
6. If raw usage is unavailable, write `null` for the missing usage fields, list them in
   `unavailable_fields`, and set `usage_source` correctly.
7. Add an aggregation command or script that reports per role and whole pipeline:
   requests, tool invocations, cache read, output, duration, and missing-field count.
8. Make aggregation fail clearly on malformed JSON, duplicate stage records, or mixed
   schema versions. It must not silently discard bad records.
9. Update the relevant init/sync/update/scaffold file lists if a new distributed script
   or template is added.
10. Update `changes.json` for every added or modified distributable file.

### 6.6 Tests

Add deterministic tests for at least these cases:

1. A complete raw-transcript record produces all cumulative usage fields.
2. Streamed output uses the maximum/final output count, not an early partial count.
3. Repeated transcript lines for one request do not increase `requests`.
4. Every raw tool-use event is counted once.
5. Harness-only input produces a valid record with unavailable fields set to `null`.
6. A malformed input record fails with a clear error.
7. A telemetry record never includes an absolute local transcript path.
8. Aggregation keeps roles and models separate instead of blending them into one opaque
   number.

### 6.7 Acceptance criteria

- One structured record is written after every agent stage in a benchmark pipeline.
- All required fields are present.
- Missing values are explicit and are never estimated.
- Session-final tokens are labelled as a final-context counter, not total consumption.
- Raw ST-000161 reconstruction still produces 347 requests and 374 tool invocations.
- ST-000161 cumulative cache-read remains 49,997,075 when the same source data is used.
- Aggregation can compare at least two pipeline runs by role and stage.
- Runtime metrics remain outside product Git history.

### 6.8 Do not do these things

- Do not use `subagent_tokens` as cumulative cost.
- Do not ask an agent to guess cache-read or request counts.
- Do not hard-code current model prices into workflow instructions.
- Do not fail the story merely because the current platform cannot expose an optional
  usage field. Record it as unavailable.
- Do not log prompts, secrets, or full tool outputs in the telemetry file.

---

## 7. FIX-02 — Parallel Tool Execution and Fewer Context Replays

### 7.1 Problem

Measured sessions perform only about 1.07 to 1.18 tool calls per model request. This means
most independent reads and checks are performed in separate turns. Every new turn replays
the retained transcript, so sequential execution multiplies cache-read cost.

Shell-level chaining alone does not solve the problem when each shell command is still
requested in a separate model turn.

### 7.2 Required outcome

Agent instructions must require the agent to identify independent operations and issue
them together using native parallel tool calls. When native parallel calls are not
available, the agent may use one safe, bounded read-only batch command.

Dependent operations, writes, destructive actions, permission gates, and decisions must
remain ordered.

### 7.3 Classification rule

Before issuing tools, classify operations into one of these groups:

| Group | Examples | Execution rule |
|---|---|---|
| Independent reads | Read three known files; inspect status and diff; query separate CI jobs | Run in parallel in one assistant turn |
| Independent searches | Search different directories or unrelated patterns | Run in parallel or one bounded search command |
| Dependent operations | Read then edit; fetch then compare; build then test its output | Run in dependency order |
| Mutations | File writes, Git changes, issue edits, PR comments | Keep explicit and ordered; do not batch merely for speed |
| Destructive or permission-gated work | Deletes, force actions, credential use | Follow safety/approval rules; never hide in a batch |

### 7.4 Instruction changes

Update `Agent_Common_Bootstrap_template.md` Section 3 so it says, in plain language:

1. Plan the next dependency group before calling a tool.
2. Put all independent tool calls in the same assistant turn when the platform supports
   native parallel calls.
3. Combine read-only shell checks only when the combined output is bounded and labelled.
4. Do not combine dependent commands or mutations just to increase the calls/request
   metric.
5. Do not run duplicate reads that return information already present in current context.
6. Stop polling once the required result is available.

Update working mirrors carrying the same common rule. Do not repeat the entire rule in
all six role instructions; they should point to the common rule.

### 7.5 Implementation steps

1. Capture a FIX-01 baseline on at least one clean representative story.
2. Find guidance containing `parallel`, `batch`, `tool call`, `&&`, or sequential read
   examples across templates and working mirrors.
3. Replace ambiguous guidance with the classification rule above.
4. Keep shell batching as a fallback for bounded read-only work, not as the primary
   definition of parallel execution.
5. Review workflow prompts that enumerate multiple independent reads. Add one explicit
   instruction to issue them together.
6. Review wait/poll loops. Require one bounded poll followed by a result check; prohibit
   open-ended background waits.
7. Do not create a new helper unless repeated operations cannot be expressed safely with
   available native parallel calls. Helper creation belongs in a separate scoped change.
8. Run the same benchmark again and compare requests, tool invocations, cache-read,
   duration, and correctness outcomes.

### 7.6 Benchmark rules

The before and after runs must use:

- the same story or fixture shape;
- the same role and stage;
- the same model when possible;
- the same available tools;
- the same required tests;
- no intentional failure in only one run.

Report calls/request as:

`tool_invocations / requests`

A higher ratio is useful only when total requests and cache-read fall without reducing
required work.

### 7.7 Acceptance criteria

- Common rules explicitly require native parallel execution for independent operations.
- Common rules explicitly keep dependent and mutating operations ordered.
- Role instructions do not duplicate or contradict the common rule.
- The benchmark shows fewer requests than its baseline.
- The initial improvement target is at least 20% fewer requests on the selected clean
  fixture. A calls/request ratio of 1.8 is a stretch target, not a universal correctness
  gate.
- Required tests, TL review, QA independence, and completion evidence remain unchanged.
- No new permission or destructive-action risk is introduced.

### 7.8 Do not do these things

- Do not combine commands that depend on earlier output.
- Do not hide writes or deletions inside a large compound shell command.
- Do not run unnecessary tools merely to increase calls/request.
- Do not claim a projected 39% saving as measured until the benchmark demonstrates it.
- Do not replace independent QA judgment with parallel automation.

---

## 8. FIX-03 — Mandatory-Section Reference Drift

### 8.1 Problem

`Agent_Common_Bootstrap` has six numbered sections. Distributable role instructions say
Sections 2 through 5 are mandatory, omitting Section 6. The bootstrap preamble repeats the
same stale range. Installed working instructions already contain a mixture of the old and
correct range.

The current validator passes because every section named in the stale range exists. It
does not know that a full-read instruction omitted the last section.

### 8.2 Required outcome

Every full-read directive must use number-independent wording:

> Read this file in full. Every section is mandatory.

Do not enumerate a section range after saying a file must be read in full. This prevents
future headings from making the directive stale.

The validator must reject a full-read directive that also limits mandatory content to a
numeric section range.

### 8.3 Files that are currently affected

At minimum, inspect and update:

- `.claude/agents/templates/rules/Agent_Common_Bootstrap_template.md`
- all six files under `.claude/agents/templates/instructions/`
- `.claude/agents/working/rules/Agent_Common_Bootstrap.md`
- `.antigravity/agents/working/rules/Agent_Common_Bootstrap.md`
- corresponding working role instructions when the stale wording is present

Do not assume this list is complete. Search all Markdown under `.claude/` and
`.antigravity/` for `§2–§5`, `§2-§5`, and the phrase `equally mandatory`.

### 8.4 Implementation steps

1. Replace numeric full-read ranges with the canonical number-independent wording.
2. Keep valid section-specific citations that do not claim to describe the whole file.
3. Search the entire repository for stale variants using both hyphen and en-dash forms.
4. Add a deterministic validator check:
   - find prose that says a file must be read `in full`;
   - if the same directive or paragraph uses a numeric mandatory range such as
     `§2–§5`, emit an error;
   - skip fenced code examples;
   - include file and line in the error.
5. Add a bad fixture containing a full-read directive with a partial mandatory range.
6. Add the fixture to `scripts/test/run.sh`.
7. Document the new invariant in `docs/Template_Test_Strategy.md`.
8. Run the full validator and all bad-fixture self-tests.
9. Record every modified distributable template in `changes.json`.

### 8.5 Acceptance criteria

- No full-read directive under `.claude/` or `.antigravity/` enumerates a partial
  mandatory range.
- All six distributable role instructions say every section is mandatory.
- Both common-bootstrap working mirrors use the same number-independent wording.
- The new bad fixture produces at least one `[ERROR]` line.
- `python scripts/validate_templates.py` exits zero on the valid corpus.
- All existing fixture tests still pass.
- Adding a future Section 7 would not require editing the full-read wording.

### 8.6 Do not do these things

- Do not merely change `§2–§5` to `§2–§6`; that can drift again when Section 7 is added.
- Do not renumber bootstrap sections as part of this fix.
- Do not weaken the requirement to read the bootstrap in full.
- Do not implement a heuristic validator rule that produces known false positives.

---

## 9. FIX-04 — Branch Preflight and Agent-State Isolation

### 9.1 Problem

An implementation branch can be created from a dirty, stale, or contaminated base.
ST-000166 inherited an agent-memory commit from local `main`, which required cleanup and
a complete verification rerun.

Current rules also instruct agents to commit memory files on product branches at stage
transitions. This mixes agent state with product history and can invalidate review or CI
evidence.

### 9.2 Required outcome

Before the first product write, the implementing agent must prove:

1. The worktree is clean, except for explicitly recognized user-owned changes that cause
   the agent to stop and request direction.
2. The intended base branch is checked out.
3. Remote state has been fetched when the mode and credentials permit it.
4. The local base is not behind or diverged from its expected remote.
5. There are no unpushed product or agent-state commits on the base.
6. The story branch starts from the verified base SHA.

Memory, Working Records, retrospectives, token traces, and other agent runtime state must
not be committed to product branches.

### 9.3 Canonical preflight result

The preflight must return a compact result containing:

```text
Preflight: PASS | BLOCKED
Mode: github | strict
Base branch: <name>
Base SHA: <sha>
Remote base SHA: <sha or unavailable>
Worktree: clean | dirty
Ahead/behind: <ahead>/<behind> | unavailable
Unpushed commits: <count or unavailable>
Agent-state commits detected: yes | no
Story branch: <name or not-created>
Reason: <empty on pass; exact blocker otherwise>
```

Do not dump the full Git log into the agent conversation. Return only the bounded result
and the minimum commit lines needed to explain a blocker.

### 9.4 GitHub-mode preflight steps

Run these checks before creating the story branch and before the first file write:

1. Resolve the intended base branch from the story or pipeline state. Do not guess.
2. Run `git status --porcelain`.
3. If output is non-empty, do not stash, discard, or commit the changes automatically.
   Report the exact paths and stop for direction when ownership is unclear.
4. Fetch the intended remote base using the repository's normal remote.
5. Confirm the current local base name and SHA.
6. Compare the local base with its remote counterpart using merge-base/ahead-behind
   information.
7. If the local base is behind or diverged, stop. Do not merge, rebase, reset, or force
   update without the workflow's explicit authority.
8. Check commits reachable from the local base but not the remote base. If any exist,
   stop and report them.
9. Search those unexpected commits and the base tip for agent-only paths or `Agent:`
   memory commit messages. Any hit blocks branch creation.
10. Create the story branch from the verified base SHA.
11. Confirm `HEAD` is the expected new branch and its parent/base SHA is the recorded
    verified base.

### 9.5 Strict-mode preflight steps

Strict mode may have no remote. In that case:

1. Perform the clean-worktree check.
2. Resolve the sprint or user-selected base branch from pipeline state.
3. Confirm the current branch and base SHA.
4. Record remote and ahead/behind fields as unavailable; do not invent them.
5. Confirm no agent-state files are tracked in the base.
6. Create the story branch only after the local checks pass.
7. Never push merely to satisfy a GitHub-mode rule.

### 9.6 Remove agent-memory commits from product branches

The current stage-transition rule in
`Agent_Common_Read_On_Demand_template.md` permits memory-only commits. Replace that
behavior with these rules:

1. Agent Memory is local runtime state by default.
2. Memory updates must be stored in an ignored path or another explicitly designed state
   store outside product Git history.
3. Working Records, retrospectives, telemetry, and temporary pipeline state remain
   uncommitted runtime artifacts.
4. If the project intentionally wants versioned agent knowledge, design a separate
   workflow and branch/repository policy. Do not silently commit it with story code.
5. Remove requirements to push a memory commit before reporting stage completion.
6. Remove merge logic that treats memory-only post-approval commits as normal product
   branch updates when that logic is no longer needed.

### 9.7 Files and references to inspect

Search, rather than relying only on this list:

- `.claude/agents/templates/rules/Agent_Common_Read_On_Demand_template.md`
- `.claude/agents/templates/rules/Developer_Rules_Bootstrap_template.md`
- `.claude/agents/templates/rules/Story_Standard_template.md`
- `.claude/agents/templates/rules/Story_Standard_Dev_template.md`
- `.claude/agents/templates/shared/workflows/Shared_Pipeline_Stages_Shared_template.md`
- strict-mode `Start_Story_Workflow_template.md` and `Sprint_Workflow_template.md`
- init/scaffold `.gitignore` generation
- all working mirrors of the files above
- merge and approval-scope rules mentioning memory-only commits

Search terms:

```text
memory files only
Agent:
[skip ci]
stage-transition commit
push before reporting
git checkout -b
git switch -c
memory-only
post-approval
```

### 9.8 Tests

Add tests or scripted fixtures for:

1. Clean, synchronized base: preflight passes and branch is created.
2. Dirty worktree: preflight blocks without stashing or deleting changes.
3. Local base behind remote: preflight blocks.
4. Local base ahead of remote: preflight blocks and lists bounded commit evidence.
5. Diverged base: preflight blocks.
6. Agent-memory commit on the base: preflight blocks.
7. Strict mode without a remote: local checks pass and remote fields are unavailable.
8. Runtime agent-state paths remain untracked after a complete stage.
9. No workflow requires a memory commit or memory push at stage completion.

Use temporary fixture repositories. Never run destructive branch tests in the developer's
real working repository.

### 9.9 Acceptance criteria

- Branch preflight runs before the first product write.
- A dirty, behind, ahead, diverged, or contaminated base cannot silently proceed.
- The preflight never auto-stashes, auto-resets, auto-rebases, or discards user changes.
- The new story branch records the verified base SHA.
- Strict mode works without a remote.
- No normal stage-transition path commits or pushes agent Memory.
- Agent runtime state is ignored and absent from product diffs.
- Review and CI evidence remain tied to a product-code SHA.

### 9.10 Do not do these things

- Do not use `git reset --hard` to repair a failed preflight.
- Do not stash user changes automatically.
- Do not rebase or merge a diverged base without explicit workflow authority.
- Do not delete existing memory commits from published history as part of this fix.
- Do not create a hidden push in strict mode.
- Do not let branch preflight print secrets or an unbounded Git log.

---

## 10. Cross-Fix Verification

After all four fixes are implemented, run one clean representative pipeline and verify:

1. Every role/stage produces one valid telemetry record.
2. Missing usage fields are explicit.
3. Independent tool calls are grouped where supported.
4. Total request count is lower than the recorded baseline for the same fixture.
5. No full-read instruction contains a numeric mandatory-section range.
6. Branch preflight passes before the first write and records the base SHA.
7. No agent runtime file appears in the product diff or commit history.
8. Developer implementation, TL review, QA validation, and PO closure still enforce their
   existing authority boundaries.
9. Required tests and CI gates still run.
10. `python scripts/validate_templates.py` passes.
11. Validator fixture self-tests pass.

The implementation is not complete if token use falls only because required reads,
testing, review, or evidence were skipped.

## 11. Required Completion Report for Each Fix

Use this exact structure:

```text
Fix: FIX-0X — <name>
Outcome: completed | blocked
Files changed: <bounded list>
Behavior changed: <one short paragraph>
Tests run: <commands and results>
Telemetry before: <measured values or unavailable>
Telemetry after: <measured values or unavailable>
Safety gates preserved: <yes/no plus explanation>
Known limitations: <none or bounded list>
Follow-up work: <none or story-sized items>
```

Do not write “all tests passed” without listing the commands that actually ran.

## 12. Definition of Done for the Batch

The four-fix batch is done only when:

- all four fixes meet their own acceptance criteria;
- the corpus validator and fixture suite pass;
- distributable templates and working mirrors agree where they are expected to agree;
- `changes.json` includes every changed distributable template;
- the current Unreleased changelog describes the shipped behavior;
- a controlled before-and-after result is recorded;
- measured savings are separated from projections;
- no safety, review, or QA gate was removed to obtain the improvement.

## 13. Follow-Up Work After This Batch

Once the batch has reliable telemetry and benchmark evidence, implement the next group:

1. Stage-specific `role + stage + risk` read profiles.
2. Bounded story, CI, PR-diff, and prototype-evidence helpers.
3. QA reuse of equivalent green head-SHA CI evidence while retaining independent targeted
   testing.
4. Canonical refined story context instead of all resolved issue comments.
5. Conditional Working Record, Memory, and retrospective behavior.

Do not start these follow-ups inside one of the four fixes unless the user explicitly
expands the scope.
