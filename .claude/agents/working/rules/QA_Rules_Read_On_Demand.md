# QA Rules — Read On Demand (Scenario-Conditional)

**Applies to:** QA agent — devkit's own team only (`.claude/agents/working/`). Relocated out of `QA_Rules_Bootstrap.md` (formerly `QA_Rules.md`) and `Story_Standard_QA.md` 2026-08-20, applying the pattern from issue #123 (and its extension to the Story_Standard views, issue #133) to the devkit's own agent team first (the distributable `.claude/agents/templates/` role rules are unchanged — a separate story). Renamed from `QA_Rules_Extended.md` to match `Developer_Rules_Read_On_Demand.md`'s naming convention — see `Bootstrap_OnDemand_Split_Notes.md`. `QA_Rules_Bootstrap.md` and `Story_Standard_QA.md` are each read in full on every QA spawn regardless of task; the three sections below apply only when QA is acting as the story Implementer, or a post-Done bug surfaces — both rare. Read this file **only when the matching scenario actually occurs**. `QA_Rules_Bootstrap.md` §9/§10, `Story_Standard_QA.md` §6, and `qa_instructions.md`'s "When Acting as Story Implementer" / "Post-Done Bug (Hotfix)" sections each still carry a one-line pointer to their relocated section here.

---

## 1. Pre-PR Gate (when acting as Implementer)

Triggered from `QA_Rules_Bootstrap.md §9`. When QA is the story Implementer, run the applicable local checks before opening a PR:

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

Triggered from `QA_Rules_Bootstrap.md §10`.

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread, the live instruction takes precedence. Acknowledge the conflict, proceed with the live instruction, and document the override in the PR description.

---

## 3. Hotfix (Post-Done Bug) — QA Role

Triggered from `Story_Standard_QA.md §6`. When a bug is found after story is `status:done`:

1. **Report:** Post Comment on original issue describing the bug; tag Dev and TL
2. After Dev creates a fix branch and fix PR → **re-validate** all affected AC
3. Report re-test results in Comment; notify PO

---

## Version

**Version:** 1.2 — Renamed from `QA_Rules_Extended.md` to `QA_Rules_Read_On_Demand.md`, matching `Developer_Rules_Read_On_Demand.md`'s naming convention (no content change) — see `Bootstrap_OnDemand_Split_Notes.md`.
**Previous:** 1.1 — Added §3 (Hotfix — QA Role), relocated from `Story_Standard_QA.md` §6 per devkit issue #133 (extends the #123 pattern to the Story_Standard views).
**1.0:** (created 2026-08-20, split out of `QA_Rules.md` v1.4 per devkit issue #123).
