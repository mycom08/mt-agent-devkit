# Technical Lead Rules — Read On Demand (Scenario-Conditional)

**Applies to:** Technical Lead agent — devkit's own team only (`.antigravity/agents/working/`). Relocated out of `Technical_Lead_Rules_Bootstrap.md` (formerly `Technical_Lead_Rules.md`) and `Story_Standard_TL.md` 2026-08-20, applying the pattern from issue #123 (and its extension to the Story_Standard views, issue #133) to the devkit's own agent team first (the distributable `.claude/agents/templates/` role rules are unchanged — a separate story). Renamed from `Technical_Lead_Rules_Extended.md` to match `Developer_Rules_Read_On_Demand.md`'s naming convention — see `Bootstrap_OnDemand_Split_Notes.md`. `Technical_Lead_Rules_Bootstrap.md` and `Story_Standard_TL.md` are each read in full on every TL spawn regardless of task; the four sections below apply only in scenarios that don't arise on most spawns (TL acting as story implementer instead of reviewer, the resulting implementer-only pre-PR gate and status-transition steps, and the post-session context-anchoring note). §2 Code Review & PR Approval and §12 Reviewer Gate — the reason TL exists on most spawns — were deliberately **not** moved; those stay in `Technical_Lead_Rules_Bootstrap.md`/`Story_Standard_TL.md`. Read this file **only when the matching scenario actually occurs**. `Technical_Lead_Rules_Bootstrap.md` §5/§11/§13, `Story_Standard_TL.md` §4, and `technical_lead_instructions.md`'s "When Acting as Story Implementer" / "Context Anchoring" sections each still carry a one-line pointer to their relocated section here.

---

## 1. When Acting as Implementer

Triggered from `Technical_Lead_Rules_Bootstrap.md §5`. Rare — only when the orchestrator assigns TL as the story implementer.

1. Create a dev branch from `main` — **never work directly on `main`**:
   ```
   git checkout -b ST-XXXXXX/short-description
   ```
2. Push all implementation work to that dev branch
3. Open a PR from the dev branch → `main`
4. PR title: `[ST-XXXXXX][DEVKIT] Story title`

---

## 2. Context Anchoring (after each working session on an unfinished story)

Triggered from `Technical_Lead_Rules_Bootstrap.md §11`.

After each working session on an unfinished story, create or update a context-anchoring note under `docs/technical/` or `docs/feature/<feature_name>/questions/`.

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

Triggered from `Technical_Lead_Rules_Bootstrap.md §13`. Applies only when TL is acting as Implementer per §1 above.

| Change type | Required local check |
|---|---|
| `.sh` files changed | `bash -n <each changed .sh file>` — zero errors |
| `.ps1` files changed | PowerShell syntax check — zero parse errors |
| `.github/workflows/` changed | Validate YAML syntax; verify job structure and step ordering |
| Template / workflow / rules / docs only | Exempt |

Include a one-line check result note in the PR description.

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 4. TL as Implementer — Status Transitions

Triggered from `Story_Standard_TL.md §4`. When `**Assigned:** Technical Lead` and TL is running Stage 1 (implementation):

### Status: In Progress → Review
1. Remove `status:in-progress`, add `status:review`
2. Create PR with title: `[ST-XXXXXX][DEVKIT] Story title`
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

**Version:** 1.2 — Renamed from `Technical_Lead_Rules_Extended.md` to `Technical_Lead_Rules_Read_On_Demand.md`, matching `Developer_Rules_Read_On_Demand.md`'s naming convention (no content change) — see `Bootstrap_OnDemand_Split_Notes.md`.
**Previous:** 1.1 — Added §4 (TL as Implementer — Status Transitions), relocated from `Story_Standard_TL.md` §4 per devkit issue #133 (extends the #123 pattern to the Story_Standard views).
**1.0:** (created 2026-08-20, split out of `Technical_Lead_Rules.md` v1.3 per devkit issue #123).
