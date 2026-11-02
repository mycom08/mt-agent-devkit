---
name: po-write-story
description: Create or edit a story issue - concise-story rules, Assigned rule, no version-bump AC, the github-mode story ID rule, title and labels, structure and the body template. Load before the first story body write.
---

# PO Write Story

**Requires:** `po-core`

Read this before your first story create or body edit of the session. In github mode always write bodies with `--body-file`.

## Story ID, Title and Labels

- **GitHub mode:** stories are GitHub Issues in this project's repository. The ID is `ST-` plus the issue number zero-padded to six digits (issue #290 → `ST-000290`). Create the issue first, then set the title `[ST-XXXXXX][FEATURE] Clear Title` with `gh issue edit`, and use the same ID in **Depends on:** lines.
- **Strict mode:** follow `Create_Stories_Workflow.md` Step 4 (story counter, `{RUNTIME_ROOT}/docs/stories/ST-XXXXXX.md`).
- Labels: feature story `status:backlog`, `feature:<name>`, `phase-N`, `sprint-N`; other stories `status:backlog`, `sprint-N`. Omit `sprint-N` until assigned. Any defect, regression or infrastructure failure adds `bug`. No milestones. The GitHub Assignee is optional and distinct from `**Assigned:**`.

## Content Rules

- Concise (2–3 pages): user story, high-level AC (what, not how), business value and constraints, a testable success definition, links to technical docs (`docs/feature/`). No field-by-field definitions, schemas, code samples or step-by-step instructions.
- `**Assigned:**` is mandatory, above `## User Story`: `Developer`, `Technical Lead`, `QA`, `Business Analyst` or `UI/UX Designer`, never "TBD".
- Documentation story AC state their expected depth explicitly.
- PATCH/PUT stories state each request field's mutability before `status:ready`.
- Every endpoint or field an AC names exists in the API spec or is in scope this sprint; otherwise name the dependency. New service logic gets a unit-test AC. A scoped-removal AC ends with "Files outside this list are out of scope for this story."
- **Never write a version-bump AC.** `VERSION` belongs to the release process; record changes against the current unreleased `CHANGELOG.md` section.
- Status lives in labels (strict: the `**Status:**` field), never in prose; discussion lives in comments.

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

## API Spec Reference

[Affected endpoints and spec link, or "N/A"]

## Technical Scope

[Optional: architecture notes, API changes, migrations]

## Deliverables

[Filled in after work complete]
```

A bug story inserts after `## Acceptance Criteria`:

```markdown
## Reproduction

**Repro Command:** [exact command, verbatim, or `unknown`]
**Expected:** [what should happen]
**Actual:** [the observed defect]
```

Bug Reproduction Pre-Flight (`Shared_Pipeline_Stages.md`) runs `Repro Command` verbatim; absent or `unknown` skips it.
