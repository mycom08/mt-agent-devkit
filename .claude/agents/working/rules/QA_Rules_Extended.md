# QA Rules — Extended (Scenario-Conditional)

**Applies to:** QA agent — devkit's own team only (`.claude/agents/working/`). Relocated out of `QA_Rules.md` 2026-08-20, applying the pattern from issue #123 to the devkit's own agent team first (the distributable `.claude/agents/templates/` role rules are unchanged — a separate story). `QA_Rules.md` is read in full on every QA spawn regardless of task; the two sections below apply only when QA is acting as the story Implementer, which is rare. Read this file **only when that scenario actually occurs**. `QA_Rules.md` §9/§10 each still carry a one-line pointer to their relocated section here.

---

## 1. Pre-PR Gate (when acting as Implementer)

Triggered from `QA_Rules.md §9`. When QA is the story Implementer, run the applicable local checks before opening a PR:

| Change type | Required local check |
|---|---|
| `.sh` files changed | `bash -n <each changed .sh file>` — zero errors |
| `.ps1` files changed | PowerShell syntax check — zero parse errors |
| `.github/workflows/` changed | Validate YAML syntax; verify job structure and step ordering |
| `.claude/agents/templates/**` or `.claude/agents/workflows/**` changed | `python scripts/validate_templates.py` + `bash scripts/test/run.sh` — both exit 0 (see `docs/Template_Test_Strategy.md`) |
| Docs only (no templates, workflows, or scripts) | Exempt |

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 2. Live User Instruction Conflicts (when acting as Implementer)

Triggered from `QA_Rules.md §10`.

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread, the live instruction takes precedence. Acknowledge the conflict, proceed with the live instruction, and document the override in the PR description.

---

## Version

**Version:** 1.0 (created 2026-08-20, split out of `QA_Rules.md` v1.4 per devkit issue #123).
