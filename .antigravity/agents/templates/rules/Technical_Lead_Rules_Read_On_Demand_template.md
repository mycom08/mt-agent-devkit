# Technical Lead Rules — Read On Demand (Scenario-Conditional)

**Applies to:** Technical Lead agent. `Technical_Lead_Rules_Bootstrap.md` and `Story_Standard_TL.md` are each read in full on every TL spawn regardless of task; the three sections below apply only in scenarios that don't arise on most spawns (TL acting as story implementer instead of reviewer, the resulting implementer-only pre-PR gate, and the post-session context-anchoring note). §2 Code Review & PR Approval and the Reviewer Gate — the reason TL exists on most spawns — stay in `Technical_Lead_Rules_Bootstrap.md`/`Story_Standard_TL.md`. Read this file **only when the matching scenario actually occurs**. `Technical_Lead_Rules_Bootstrap.md` §5 and §9 and §10 each still carry a one-line pointer to their relocated section here.

---

## 1. When Acting as Implementer

Triggered from `Technical_Lead_Rules_Bootstrap.md §5`. Rare — only when the orchestrator assigns TL as the story implementer.

1. Create a dev branch from the feature branch — **never work directly on the feature branch or master**:
   ```
   git checkout -b ST-XXXXXX/short-description
   ```
2. Push all implementation work to that dev branch
3. Open a PR from the dev branch → **feature branch** (NOT master)
4. PR title: `[ST-XXXXXX][FEATURE] Story title`

> **Gate:** Do not open a PR targeting master. The feature branch is the merge target for all story PRs.

---

## 2. Context Anchoring (after each working session on an unfinished feature)

Triggered from `Technical_Lead_Rules_Bootstrap.md §9`.

After each working session on an unfinished feature, create or update a context-anchoring note so work can resume without losing state.

**Placement:** `docs/feature/<feature_name>/questions/` unless another subfolder is a better fit
**Filename:** Must contain the feature name, `Title_Case_With_Underscores`
**Length:** Under 50 lines — decisions with reasoning, active constraints, open questions, and a done/remaining checklist

Template:
```md
# Feature: <feature_name>

## Decisions
| Decision | Reason | Rejected Alternative |
|----------|--------|----------------------|

## Constraints

## Open Questions

## State
```

---

## 3. Pre-PR Gate (when acting as Implementer)

Triggered from `Technical_Lead_Rules_Bootstrap.md §10`. When TL is the story Implementer (not reviewer), run the applicable local checks before opening a PR. Do not open the PR if any check fails.

| Change type | Required local check |
|---|---|
| Source code changed | `{test-command}` must pass AND run `{integration-test-command}` against the sandbox; all assertions must pass |
| API spec changed (`docs/api/{api-spec-file}` or lint config) | `{api-lint-command}` (zero errors) AND `{code-gen-command}` then `git diff --exit-code {generated-file-path}` (no diff) — skip code-gen check if project does not use spec-driven generation |
| Integration test collection or config changed | Run the relevant integration suite against the sandbox; all assertions must pass |
| Both source and tests changed | Both checks above required |
| CI workflow (`.github/workflows/`) changed | Validate YAML syntax; verify job structure and step ordering are correct |
| Docs or config only | Exempt |

Include a one-line test result note in the PR description (e.g., "`{test-command}` — PASS · integration tests — PASS").

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 4. TL as Implementer — Status Transitions

Triggered from `Story_Standard_TL.md` §4. When `**Assigned:** Technical Lead` and TL is running Stage 1 (implementation):

### Status: In Progress → Review
1. Remove `status:in-progress`, add `status:review`
2. Create PR with title: `[ST-XXXXXX][FEATURE] Story title`
3. **Add PR link to issue Deliverables section** — edit the issue body to include the PR URL under `## Deliverables` (use `gh issue edit --body-file`)
4. Post a brief comment on the story notifying the Developer reviewer:

   ```
   ## PR ready for peer review
   **Thread Status:** Open
   **Area:** Implementation

   **TL - YYYY-MM-DD**
   PR #NNN opened for peer review. <one-line summary of changes>

   **Next:** Developer
   ```

### Status: Review → In Progress (Developer feedback)
1. Address all CR items in the branch
2. Push new commits
3. Re-request review via issue comment

---

## Version

**Version:** 1.1 — Added §4 (TL as Implementer — Status Transitions), relocated from `Story_Standard_TL_template.md` §4 per devkit issue #133 (ST-000134), extending the same trim already validated on the devkit's own team.
**Previous:** 1.0 — Split out of `Technical_Lead_Rules_template.md` v2.2 (former section 5's "When acting as Implementer" subsection, former section 9 Context Anchoring, former section 10 Pre-PR Gate as Implementer relocated here as §1–§3), mirroring the boundary already validated on the devkit's own team.
**Created:** 2026-08-25
