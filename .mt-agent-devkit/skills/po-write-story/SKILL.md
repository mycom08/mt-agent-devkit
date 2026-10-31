---
name: po-write-story
description: Create or edit a story issue - concise-story rules, Assigned rule, no version-bump AC, the github-mode story ID rule, title and labels, structure and the body template. Load before the first story body write.
---

# PO Write Story

**Requires:** `po-core`

Read this before your first `gh issue create` or `gh issue edit --body-file` of the session. Always write bodies with `--body-file`.

## Story ID, Title and Labels (github mode)

- Stories are GitHub Issues in `mycom08/mt-agent-devkit`. The story ID is `ST-` plus the issue number zero-padded to six digits (issue #290 → `ST-000290`). Create the issue first, then set the title `[ST-XXXXXX][DEVKIT] Clear Title` with `gh issue edit`, and use the same ID in **Depends on:** lines.
- Labels: `status:backlog` + `sprint-N`; a bug/defect story adds `bug`. No milestones. The GitHub Assignee (a user account) is optional and distinct from `**Assigned:**`.

## Content Rules

- Keep stories concise (2–3 pages); move technical detail to technical docs (`docs/technical/`) and link them. Include the user story, high-level AC (what, not how), business value and constraints, and a testable success definition. Exclude field-by-field specs, implementation walkthroughs, exact file content, pseudocode and line-by-line instructions.
- `**Assigned:**` is mandatory, above `## User Story`: `Developer`, `Technical Lead`, `QA`, `Business Analyst` or `UI/UX Designer`, never "TBD". It drives pipeline routing.
- Documentation or template story AC state their expected depth explicitly.
- **Never write a version-bump AC.** No story bumps `VERSION`, names a target version or creates a `changes.json` version key. Where changes need recording, the AC folds them into the **current** unreleased `changes.json` entry with a `CHANGELOG.md` bullet.
- Status lives in labels, never in the body; discussion lives in comments.
- **Porting a validated pattern:** name the exact reference commit SHA and/or files to model in `Technical Scope`.
- **Devkit workflow-stage AC:** state detection in terms of what is on disk at that stage, not a downstream concept. When two same-sprint stories restructure one workflow section, name the land order in Technical Scope.

## Body Template

```markdown
**Phase:** [Phase/Sprint]
**Story Points:** [1-13]
**Priority:** Must-Have | Should-Have | Nice-to-Have
**Assigned:** Developer | Technical Lead | QA | Business Analyst | UI/UX Designer
**Base Branch:** <existing branch selected during story creation; immutable>

## User Story

> As a **[persona]**,
> I want **[feature]**,
> So that **[benefit]**.

## Acceptance Criteria

- [ ] Criterion 1

## Technical Scope

[Optional: design notes, template changes, workflow changes]

## Deliverables

[Filled in after work complete: PR links, commits, artifacts]
```

A bug/defect story inserts this after `## Acceptance Criteria`:

```markdown
## Reproduction

**Repro Command:** [exact command/test, verbatim, or `unknown`]
**Expected:** [what should happen]
**Actual:** [the observed defect]
```

Bug Reproduction Pre-Flight (`Shared_Pipeline_Stages.md`) runs `Repro Command` verbatim before any implementer spawn; absent or `unknown` skips it.
