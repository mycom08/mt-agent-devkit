# Technical Lead Rules — Extended (Scenario-Conditional)

**Applies to:** Technical Lead agent — devkit's own team only (`.claude/agents/working/`). Relocated out of `Technical_Lead_Rules.md` 2026-08-20, applying the pattern from issue #123 to the devkit's own agent team first (the distributable `.claude/agents/templates/` role rules are unchanged — a separate story). `Technical_Lead_Rules.md` is read in full on every TL spawn regardless of task; the three sections below apply only in scenarios that don't arise on most spawns (TL acting as story implementer instead of reviewer, and the resulting implementer-only pre-PR gate; the post-session context-anchoring note). §2 Code Review & PR Approval — the reason TL exists on most spawns — was deliberately **not** moved; that stays in `Technical_Lead_Rules.md`. Read this file **only when the matching scenario actually occurs**. `Technical_Lead_Rules.md` §5/§11/§13 each still carry a one-line pointer to their relocated section here.

---

## 1. When Acting as Implementer

Triggered from `Technical_Lead_Rules.md §5`. Rare — only when the orchestrator assigns TL as the story implementer.

1. Create a dev branch from `main` — **never work directly on `main`**:
   ```
   git checkout -b ST-XXXXXX/short-description
   ```
2. Push all implementation work to that dev branch
3. Open a PR from the dev branch → `main`
4. PR title: `[ST-XXXXXX][DEVKIT] Story title`

---

## 2. Context Anchoring (after each working session on an unfinished story)

Triggered from `Technical_Lead_Rules.md §11`.

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

Triggered from `Technical_Lead_Rules.md §13`. Applies only when TL is acting as Implementer per §1 above.

| Change type | Required local check |
|---|---|
| `.sh` files changed | `bash -n <each changed .sh file>` — zero errors |
| `.ps1` files changed | PowerShell syntax check — zero parse errors |
| `.github/workflows/` changed | Validate YAML syntax; verify job structure and step ordering |
| Template / workflow / rules / docs only | Exempt |

Include a one-line check result note in the PR description.

> **Gate:** Do not open a PR until all applicable checks pass.

---

## Version

**Version:** 1.0 (created 2026-08-20, split out of `Technical_Lead_Rules.md` v1.3 per devkit issue #123).
