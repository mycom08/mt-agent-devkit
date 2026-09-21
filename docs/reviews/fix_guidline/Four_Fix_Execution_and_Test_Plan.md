# Four Agent Harness Fixes — Execution and Test Plan

**Status:** Ready for story creation and implementation
**Audience:** Orchestrators, implementers, reviewers, and QA
**Scope:** Execution order and testing plan for FIX-01 through FIX-04
**Date:** 2026-09-21

## 1. Purpose

This document defines the exact order for implementing and validating the first four
agent-harness fixes.

Use this document for **when and how to execute the work**. Use
`docs/reviews/fix_guidline/Top_Four_Agent_Harness_Fix_Guide.md` for the detailed behavior,
field definitions, safety rules, acceptance criteria, and prohibited shortcuts for each
fix.

The four fixes are:

| ID | Fix | Primary result |
|---|---|---|
| FIX-01 | Trustworthy token and request telemetry | Reliable before-and-after evidence |
| FIX-02 | Parallel tool execution | Fewer model requests and context replays |
| FIX-03 | Mandatory-section reference drift | Correct instructions plus regression protection |
| FIX-04 | Branch preflight and agent-state isolation | Clean benchmark and product branches |

## 2. Core Delivery Decision

Do not build the entire workflow-testing strategy before fixing these issues. Also do not
implement all four fixes and add tests afterward.

Use a test-first, incremental sequence:

```text
Freeze evidence and fixture definitions
                  |
                  v
Implement FIX-01 telemetry and record a baseline
                  |
                  v
Add failing test, then implement FIX-03 instruction-drift fix
                  |
                  v
Add Git fixtures, then implement FIX-04 branch/state safety
                  |
                  v
Run pre-change parallelism benchmark
                  |
                  v
Implement FIX-02 parallel guidance
                  |
                  v
Run the same benchmark and compare
                  |
                  v
Execute cross-fix regression and decide whether to continue
                  |
                  v
Expand the broader Layer-2 and Layer-3 test strategy later
```

This plan moves FIX-04 ahead of the FIX-02 controlled benchmark. That is intentional:
the benchmark must not start from a dirty, stale, or agent-state-contaminated branch.

## 3. Governing Documents

Read these documents before creating implementation stories:

1. `docs/reviews/fix_guidline/Top_Four_Agent_Harness_Fix_Guide.md`
2. `docs/reviews/Agent_Harness_Token_Efficiency_Analysis.md`
3. `docs/reviews/Token_Cost_Model_and_Priorities.md`
4. `docs/reviews/Independent_Token_Efficiency_Review.md`
5. `docs/Agent_Workflow_Test_Strategy.md`
6. `docs/Template_Test_Strategy.md`

If this plan conflicts with the fix guide about a fix's required behavior, the fix guide
wins. If this plan conflicts only about execution order, this plan wins.

## 4. Principles for the Whole Programme

1. **Measure before optimizing.** FIX-02 cannot claim savings without a FIX-01 baseline.
2. **Test the failure first.** A regression test must fail for the known defect before the
   implementation is applied whenever deterministic testing is possible.
3. **Use the same benchmark shape.** Before-and-after comparisons must keep story, model,
   tools, and required quality gates stable.
4. **Change one main variable per PR.** Do not combine telemetry, parallelism, branch
   behavior, and instruction cleanup in one unreviewable change.
5. **Preserve safety and independence.** TL and QA gates remain independent. Missing tests
   or skipped reads are not token savings.
6. **Separate measurement types.** Cache-read, output, requests, tool invocations,
   duration, final-session counter, and monetary cost are different fields.
7. **Use bounded evidence.** Save full logs outside model context and return compact
   summaries and relevant failures.
8. **Never mutate a real repository for destructive Git test cases.** Use temporary
   fixture repositories.
9. **Do not edit `VERSION`.** Update the existing snapshot entry in `changes.json` for
   distributed template changes.
10. **Stop on unexplained regression.** Do not average away a safety or correctness
    failure.

## 5. Work Breakdown and PR Boundaries

Use five implementation PRs and one final evidence task:

| Order | Work package | Recommended PR scope |
|---:|---|---|
| 1 | WP-01 | FIX-01 telemetry collector, schema, aggregation, and tests |
| 2 | WP-02 | FIX-03 instruction wording, validator invariant, and fixture |
| 3 | WP-03 | FIX-04 branch preflight, agent-state policy, and Git fixtures |
| 4 | WP-04A | Record the controlled pre-FIX-02 benchmark |
| 5 | WP-04B | FIX-02 parallel-execution guidance and targeted workflow changes |
| 6 | WP-05 | Post-change benchmark, cross-fix regression, and decision report |

WP-04A is an evidence task, not a behavior-changing PR. Store only sanitized benchmark
results that the project explicitly chooses to version.

### 5.1 Codex model and reasoning allocation

This programme does not use GPT-6 Astra. Use the following Codex models for the
implementation and review work:

| Work | Primary model | Reasoning effort | Independent review |
|---|---|---|---|
| WP-01 telemetry schema, collector, aggregation, and tests | `gpt-5.6-terra` | `high` | `gpt-5.6-sol`, `high` |
| WP-02 validator logic and instruction-drift fix | `gpt-5.6-terra` | `medium` | `gpt-5.6-sol`, `high` |
| WP-02 fixtures, searches, and mirror updates | `gpt-5.6-luna` | `medium` | Included in WP-02 review |
| WP-03 branch preflight and agent-state isolation | `gpt-5.6-terra` | `high` | `gpt-5.6-sol`, `high` |
| WP-04B parallel-execution guidance | `gpt-5.6-terra` | `medium` | `gpt-5.6-sol`, `high` |
| WP-05 final benchmark analysis and cross-fix review | `gpt-5.6-sol` | `high` | TL and QA remain independent |
| Bounded mechanical edits outside the rows above | `gpt-5.6-luna` | `medium` | Owning work package reviewer |

Model rules:

1. Use `gpt-5.6-terra` with `high` reasoning as the default implementation model for
   FIX-01 and FIX-04 because metric semantics and Git safety require careful reasoning.
2. Use `gpt-5.6-sol` with `high` reasoning for independent architecture review, final
   benchmark analysis, and the cross-fix decision. Use the explicit `gpt-5.6-sol` model
   identifier rather than the `gpt-5.6` alias so the recorded configuration is stable and
   unambiguous.
3. Use `gpt-5.6-luna` only for bounded, repetitive work with deterministic verification,
   such as adding fixtures, running corpus searches, or applying already-approved mirror
   edits. Luna must not be the sole owner of telemetry semantics or branch safety.
4. Do not raise reasoning effort above `high` by default. A Sol reviewer may use `xhigh`
   only after a concrete unresolved architecture or metric ambiguity is recorded.
5. Record the implementation model and reasoning effort in every work-package report.
6. This allocation governs the Codex agents implementing the changes. It does not change
   the models used by the devkit roles inside a controlled benchmark.
7. Before-and-after benchmark runs must use the same role model and reasoning effort for
   each corresponding stage. If a required model is unavailable, mark the comparison
   non-comparable or rerun both sides with the same replacement.

Selection basis, verified against official OpenAI documentation on 2026-09-21:

- `gpt-5.6-sol` is the GPT-5.6 flagship for complex professional work:
  `https://developers.openai.com/api/docs/models/gpt-5.6-sol`
- `gpt-5.6-terra` balances intelligence and cost:
  `https://developers.openai.com/api/docs/models/gpt-5.6-terra`
- `gpt-5.6-luna` is intended for cost-sensitive, high-volume work:
  `https://developers.openai.com/api/docs/models/gpt-5.6-luna`

## 6. Phase 0 — Freeze Scope and Evidence

### Goal

Create a stable starting point so later measurements can be compared honestly.

### Steps

1. Record the current commit SHA.
2. Record `VERSION` without modifying it.
3. Confirm the worktree status and list pre-existing modified or untracked paths.
4. Mark unrelated existing changes as user-owned. Do not add them to these PRs.
5. Preserve the current analysis evidence:
   - ST-000161: 347 requests, 374 tool invocations, 49,997,075 cache-read units;
   - ST-000199: 166 requests, 13,019,501 cache-read units;
   - role/model breakdowns from `Harness_Token_Usage_2026-09-18.json`.
6. Select one clean canonical workflow fixture from
   `docs/Agent_Workflow_Test_Strategy.md`.
7. Prefer `WF-002-business-logic` for the full pipeline because it exercises Developer,
   TL, QA, and PO without requiring browser-heavy UI testing.
8. Define the exact fixture version: repository content, story body, AC, expected diff,
   required tests, model per role, and available tools.
9. Create a benchmark manifest containing those inputs. The manifest must not include
   secrets or local absolute transcript paths.
10. Decide where non-versioned raw run artifacts will be stored. The path must be ignored
    by Git.

### Exit criteria

- The current SHA and worktree state are recorded.
- The canonical fixture and expected outcome are frozen.
- The benchmark manifest identifies models and available tools.
- Raw benchmark artifacts have a safe ignored location.
- No implementation behavior has changed yet.

## 7. Phase 1 — WP-01: Implement FIX-01 Telemetry

### Goal

Produce trustworthy, structured measurements before changing tool-use behavior.

### Specification

Follow `Top_Four_Agent_Harness_Fix_Guide.md`, Section 6, in full.

### Test-first steps

1. Create a small sanitized transcript fixture representing streamed assistant events.
2. Include duplicate lines for one request so request deduplication is tested.
3. Include partial and final output-token values so final/max output selection is tested.
4. Include multiple raw tool-use events, including two calls to the same tool.
5. Write a failing test for the expected totals.
6. Add a harness-only fixture with no raw usage fields.
7. Write a failing test that expects `null` fields plus a complete
   `unavailable_fields` list.
8. Add malformed and sensitive-path fixtures and assert clear rejection or sanitization.

### Implementation steps

1. Define telemetry schema version 1 exactly once.
2. Implement collection and aggregation using the field meanings in the fix guide.
3. Reuse the verified grouping logic from
   `.antigravity/agents/working/tokentrace/token_cost.sh` where applicable.
4. Add orchestrator collection immediately after every agent stage completion.
5. Write one JSON Lines record per role/stage.
6. Keep raw artifacts and runtime telemetry outside product Git history.
7. Report missing platform fields as unavailable. Do not estimate them.
8. Add explicit errors for malformed JSON, duplicate stage identity, and mixed schema
   versions.
9. Update init, update, sync, and scaffold enumerations if a new distributed script or
   template is introduced.
10. Update template mirrors, `changes.json`, and the Unreleased changelog entry.

### Verification steps

1. Run telemetry unit/fixture tests.
2. Reprocess the existing ST-000161 evidence.
3. Confirm exactly 347 requests and 374 tool invocations.
4. Confirm exactly 49,997,075 cache-read units.
5. Confirm output uses the final streamed value per request group.
6. Confirm absolute transcript paths are not written into exported records.
7. Run `python scripts/validate_templates.py`.
8. Run validator fixture tests if validator or fixtures changed.

### Deliverables

- Versioned schema definition.
- Collector or extraction script.
- Aggregation command or script.
- Sanitized test fixtures.
- Automated tests.
- One example aggregated report.
- Updated distributed-file manifests when applicable.

### Gate G1

Do not proceed to optimization work unless:

- required telemetry fields are consistently written;
- missing values are explicit;
- the ST-000161 known totals reproduce;
- the collector does not expose sensitive local paths;
- the telemetry tests and corpus validator pass.

## 8. Phase 2 — Record the Baseline Run

### Goal

Measure the selected canonical fixture before FIX-02 changes agent tool behavior.

### Steps

1. Start from the frozen fixture and recorded base SHA.
2. Use the role models recorded in the benchmark manifest.
3. Run the normal pipeline without parallelism-specific instruction changes.
4. Preserve all existing safety, implementation, TL, QA, and PO gates.
5. Collect one telemetry record after every stage.
6. Record failures, retries, blocked periods, and session resumes as separate facts.
7. Do not remove an outlier unless the report explains why it is invalid.
8. Aggregate results by role, stage, and model.

### Required baseline report

Include:

| Metric | Required breakdown |
|---|---|
| Requests | Role and stage |
| Tool invocations | Role, stage, and tool name |
| Tool invocations/request | Role and total |
| Cache-read | Role, stage, and model when available |
| Cache creation | Role and model when available |
| Input/output tokens | Role and model when available |
| Duration | Role, stage, and total |
| Session-final counter | Role, labelled as final context rather than usage |
| Missing fields | Field and reason |
| Quality result | Tests, review, QA, and closure outcome |

### Gate G2

The baseline is usable only when:

- the fixture reaches its expected result;
- required tests and quality gates run;
- telemetry coverage is complete or missing fields are explicit;
- no unrelated branch contamination occurred;
- the run configuration is reproducible.

If G2 fails, repair the fixture or telemetry before implementing FIX-02.

## 9. Phase 3 — WP-02: Implement FIX-03 Instruction-Drift Protection

### Goal

Correct the known `Sections 2 through 5` defect and make the wording future-proof.

### Specification

Follow `Top_Four_Agent_Harness_Fix_Guide.md`, Section 8, in full.

### Test-first steps

1. Add a bad Markdown fixture containing both:
   - a directive to read a file in full;
   - a partial mandatory numeric section range.
2. Add the fixture to `scripts/test/run.sh`.
3. Run the fixture and confirm it incorrectly passes before the validator change.
4. Implement a deterministic validator rule that flags the fixture.
5. Run the fixture again and confirm one or more `[ERROR]` lines appear.
6. Confirm fenced examples remain excluded.

### Implementation steps

1. Replace partial mandatory ranges with: `Read this file in full. Every section is
   mandatory.`
2. Update all six distributable role instruction templates.
3. Update `Agent_Common_Bootstrap_template.md`.
4. Update all corresponding working mirrors where the wording occurs.
5. Search `.claude/` and `.antigravity/` for hyphen and en-dash variants.
6. Do not replace the old range with a new numeric range.
7. Document the validator invariant in `docs/Template_Test_Strategy.md`.
8. Update `changes.json` and the Unreleased changelog entry.

### Verification steps

1. Run the new negative fixture.
2. Run all existing negative fixtures.
3. Run `python scripts/validate_templates.py` on the full corpus.
4. Search for remaining `§2–§5`, `§2-§5`, and equivalent stale wording.
5. Confirm legitimate section-specific citations remain intact.
6. Confirm adding a hypothetical Section 7 would require no wording change.

### Gate G3

- The bad fixture fails as intended.
- The valid corpus passes.
- All full-read directives use number-independent wording.
- Template and working copies are consistent where expected.

## 10. Phase 4 — WP-03: Implement FIX-04 Branch and State Safety

### Goal

Ensure every implementation and benchmark starts from a verified base and agent runtime
state cannot contaminate product history.

### Specification

Follow `Top_Four_Agent_Harness_Fix_Guide.md`, Section 9, in full.

### Test-first fixture matrix

Create temporary repositories for each case:

| Case | Setup | Expected result |
|---|---|---|
| B01 | Clean local base equals remote | Pass and create story branch |
| B02 | Dirty tracked file | Block; do not stash or discard |
| B03 | Untracked user file | Block or report according to the final explicit policy |
| B04 | Local base behind remote | Block |
| B05 | Local base ahead of remote | Block and show bounded commit evidence |
| B06 | Local and remote diverged | Block |
| B07 | Agent-memory commit on base | Block |
| B08 | Strict mode with no remote | Pass local checks; remote fields unavailable |
| B09 | Wrong base branch checked out | Block |
| B10 | Clean preflight followed by branch creation | New branch starts at recorded base SHA |

### Test-first steps

1. Build a temporary-repository helper. It must never point at the developer's real repo.
2. Implement B01 and B02 first to establish pass/block behavior.
3. Add B04 through B07 to cover remote and contamination failures.
4. Add B08 for strict mode.
5. Add B09 and B10 for base and branch correctness.
6. Confirm failing tests describe the exact missing preflight behavior.

### Implementation steps

1. Define one canonical bounded preflight result.
2. Add preflight before the first product write and before story branch creation.
3. Resolve the intended base from story or pipeline state. Do not infer it from the
   current branch alone.
4. Block on dirty, behind, ahead, diverged, wrong-base, or contaminated states.
5. Never auto-stash, auto-reset, auto-rebase, or delete changes.
6. Support strict mode without inventing remote information.
7. Remove the normal stage-transition instruction to commit and push Memory files.
8. Keep Memory, Working Records, retrospectives, telemetry, and pipeline state outside
   product Git history.
9. Review merge and approval-scope wording that explicitly allows memory-only commits.
10. Update templates, working mirrors, scaffold behavior, `changes.json`, and changelog.

### Verification steps

1. Run B01 through B10.
2. Confirm every blocked case makes no branch, commit, stash, reset, rebase, or push.
3. Confirm strict mode performs no remote mutation.
4. Run a complete fixture stage and inspect the product diff.
5. Confirm no agent runtime paths appear in tracked changes.
6. Search the corpus for remaining memory commit/push instructions.
7. Run the full template validator.

### Gate G4

- All ten Git fixture cases pass.
- Branch creation occurs only after a passing preflight.
- The branch starts at the recorded base SHA.
- No standard workflow commits agent runtime state.
- No destructive recovery behavior is introduced.

Do not run the controlled FIX-02 benchmark until G4 passes.

## 11. Phase 5 — WP-04B: Implement FIX-02 Parallel Tool Execution

### Goal

Reduce model request count and repeated context replay without skipping required work.

### Specification

Follow `Top_Four_Agent_Harness_Fix_Guide.md`, Section 7, in full.

### Pre-change checks

1. Confirm G1 through G4 passed.
2. Confirm the baseline benchmark report is immutable.
3. Confirm the canonical fixture has not changed.
4. Confirm models and available tools match the baseline configuration.

### Test-first behavior scenarios

Create prompt-level or agent-in-the-loop cases for:

| Case | Operations | Expected behavior |
|---|---|---|
| P01 | Read three unrelated files | Calls issued in parallel in one assistant turn |
| P02 | Search two unrelated paths | Parallel calls or one bounded labelled search |
| P03 | Read a file, then edit from its contents | Ordered; edit waits for read |
| P04 | Fetch remote state, then compare SHAs | Ordered by dependency |
| P05 | Two unrelated read-only Git checks | Parallel or one bounded batch |
| P06 | File write plus Git commit | Ordered; never hidden in one optimization batch |
| P07 | Destructive action requiring approval | Safety/approval path preserved |
| P08 | Poll an already-completed task | Collect result once; do not continue polling |

### Implementation steps

1. Update `Agent_Common_Bootstrap_template.md` token-efficiency guidance.
2. Require agents to form dependency groups before issuing tools.
3. Require native parallel calls for independent operations when supported.
4. Allow one bounded read-only shell batch as a fallback.
5. Keep dependent operations and mutations explicit and ordered.
6. Update working mirrors.
7. Search workflows for repeated independent reads and add targeted batching guidance
   only where the common rule is insufficient.
8. Review wait loops and remove open-ended polling guidance.
9. Avoid duplicating the full common rule in every role instruction.
10. Update `changes.json` and the Unreleased changelog entry.

### Static and behavioral verification

1. Run the full template validator.
2. Run P01 through P08.
3. Confirm P01, P02, and P05 reduce assistant turns.
4. Confirm P03, P04, P06, and P07 remain ordered.
5. Confirm P08 terminates after the result is available.
6. Inspect the changed rules for language that could encourage unsafe compound mutation
   commands.

### Gate G5

- Independent reads are parallelized in behavioral scenarios.
- Dependent and mutating operations remain ordered.
- No permission or destructive-action safeguard is weakened.
- The template corpus and behavioral scenarios pass.

## 12. Phase 6 — WP-05: Controlled Post-Change Benchmark

### Goal

Measure FIX-02 using the same fixture and prove that any savings do not come from skipped
work.

### Steps

1. Reset the temporary benchmark environment to the frozen fixture state.
2. Run FIX-04 preflight and record its bounded result.
3. Confirm the same story, models, tools, and expected tests as the baseline.
4. Run the complete pipeline with FIX-02 guidance active.
5. Collect FIX-01 telemetry after every stage.
6. Record failures, retries, and resumes without hiding them.
7. Aggregate by role, stage, and model.
8. Compare with the baseline.

### Required comparison table

| Metric | Before | After | Absolute change | Percentage change |
|---|---:|---:|---:|---:|
| Requests | | | | |
| Tool invocations | | | | |
| Tool invocations/request | | | | |
| Cache-read | | | | |
| Cache creation | | | | |
| Output tokens | | | | |
| Duration | | | | |
| Failed/retried turns | | | | |

Add a role-by-role table below the total table. Do not blend different model prices into
one token number and call it cost.

### Quality comparison

Confirm both runs have the same result for:

- expected product diff;
- targeted tests;
- aggregate regression/CI gates;
- TL verdict;
- QA verdict;
- PO closure result;
- blocker and safety behavior;
- unauthorized mutation count, which must remain zero.

### Success criteria

The batch may claim an improvement when:

1. Requests fall by at least 20% on the selected clean fixture, or the report explains
   why the fixture has too few independent operations for that target.
2. Cache-read falls in the same direction.
3. Tool invocations do not fall merely because required checks were skipped.
4. All quality results remain equivalent.
5. No new safety or branch-state failure appears.

The calls/request ratio of 1.8 is a stretch target, not a pass/fail requirement for every
stage.

### Failure interpretation

- **Requests down, cache-read flat or higher:** inspect larger retained outputs or later
  failures.
- **Tool invocations down unexpectedly:** check whether required work was skipped.
- **Duration down, quality different:** reject the result.
- **One role improves while another regresses:** report separately; do not hide it in the
  total.
- **Run has an unrelated failure:** preserve the result, mark it non-comparable, repair
  the fixture, and rerun. Do not delete the failed evidence.

### Gate G6

The optimization is accepted only when measurement, correctness, safety, and independent
review all pass. Otherwise revert or revise FIX-02 rather than weakening the benchmark.

## 13. Phase 7 — Cross-Fix Regression

Run this after G6:

1. `python scripts/validate_templates.py`
2. Validator negative-fixture suite.
3. Telemetry unit and aggregation tests.
4. FIX-03 drift fixture.
5. FIX-04 Git fixture matrix B01 through B10.
6. FIX-02 behavioral cases P01 through P08.
7. One clean end-to-end canonical pipeline.
8. One controlled failure or fix-round path when budget permits.
9. Template-versus-working-mirror comparison.
10. `changes.json` completeness check.
11. Search for prohibited stale rules:
    - partial full-read section ranges;
    - mandatory memory commits;
    - open-ended background waits;
    - branch creation before preflight.

### Final regression gate

- Every automated test passes.
- No distributed template is missing from `changes.json`.
- No runtime telemetry or agent state is tracked by Git.
- The before-and-after report distinguishes measured facts from projections.
- Known limitations and unavailable fields are recorded.

## 14. Story Creation Plan

Create implementation stories with these boundaries:

### Story A — Telemetry foundation

- Implements Phase 1.
- Includes schema, collector, aggregation, and fixture tests.
- Does not change parallel tool guidance.

### Story B — Full-read reference drift

- Implements Phase 3.
- Includes validator invariant and fixture before wording changes.
- Does not restructure common bootstrap content.

### Story C — Branch and agent-state safety

- Implements Phase 4.
- Includes temporary Git fixture matrix.
- Does not rewrite published Git history.

### Story D — Parallel tool execution

- Implements Phase 5.
- Requires completed baseline and passing branch preflight.
- Does not add unrelated stage-profile files.

### Story E — Benchmark and regression report

- Implements Phases 6 and 7.
- Changes no production behavior unless a measured defect requires a separate follow-up.
- Records both successful and non-comparable runs.

## 15. Roles and Review Responsibilities

| Role | Responsibility |
|---|---|
| Developer | Implement scripts, rules, fixtures, and deterministic tests |
| Technical Lead | Review schema semantics, Git safety, dependency grouping, and benchmark validity |
| QA | Validate fixtures, negative paths, quality equivalence, and absence of skipped gates |
| Product Owner | Confirm story boundaries and accept only evidence-backed outcomes |
| Orchestrator | Preserve execution order, collect telemetry, enforce gates, and prevent scope mixing |

The implementer must not approve their own benchmark. TL and QA evaluate correctness
independently.

## 16. Required Report After Each Work Package

Use this format:

```text
Work package: WP-XX — <name>
Status: completed | blocked | non-comparable
Base SHA: <sha>
Files changed: <bounded list>
Tests added first: <yes/no and evidence>
Tests run: <commands and results>
Safety gates preserved: <yes/no and explanation>
Telemetry coverage: <complete or missing fields>
Measured result: <facts only>
Projection: <separate, or none>
Known limitations: <bounded list>
Next gate: <G1-G6 or final regression>
```

## 17. Stop Conditions

Stop and resolve the problem before continuing when:

- telemetry totals do not reproduce known evidence;
- a benchmark configuration changes between before and after runs;
- a test passes before the defect is introduced into its fixture;
- the real worktree is dirty and file ownership is unclear;
- a change requires reset, rebase, force-push, or history rewriting without explicit
  authority;
- a proposed optimization skips required testing, TL review, or QA judgment;
- a template and its required working mirror diverge unexpectedly;
- runtime agent state appears in a product commit;
- measured results are being described using an incorrect unit.

## 18. Work Deferred Until After This Plan

After the final regression gate, use the resulting telemetry to prioritize:

1. stage-specific read profiles;
2. bounded multi-read and evidence helpers;
3. QA reuse of equivalent head-SHA CI evidence;
4. canonical refined story context;
5. conditional Working Record, Memory, and retrospective behavior;
6. the remaining canonical workflow fixtures from
   `docs/Agent_Workflow_Test_Strategy.md`;
7. full Layer-2 deployment testing and broader Layer-3 agent-in-the-loop coverage.

These are follow-up programmes. Do not silently include them in the four-fix batch.
