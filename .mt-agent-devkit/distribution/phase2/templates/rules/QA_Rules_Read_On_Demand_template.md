# QA Rules — Read On Demand (Scenario-Conditional)

**Applies to:** QA agent. `QA_Rules_Bootstrap.md` and `Story_Standard_QA.md` are each read in full on every QA spawn regardless of task; the two sections below apply only when QA is acting as the story Implementer — rare. Read this file **only when the matching scenario actually occurs**. `QA_Rules_Bootstrap.md` §9 and §10 each still carry a one-line pointer to their relocated section here.

---

## 1. Pre-PR Gate (when acting as Implementer)

Triggered from `QA_Rules_Bootstrap.md §9`. When QA is the story Implementer, run the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`) before opening a PR. It is the same gate for every implementer.

---

## 2. Live User Instruction Conflicts (when acting as Implementer)

Triggered from `QA_Rules_Bootstrap.md §10`. The rule is `raise-question` section 5 (`.mt-agent-devkit/skills/raise-question/SKILL.md`).

---

## 3. Hotfix (Post-Done Bug) — QA Role

Triggered from `Story_Standard_QA.md` §6. When a bug is found after story is `status:done`:

1. **Report:** Post Comment on original issue describing the bug; tag Dev and TL
2. After Dev creates a fix branch and fix PR → **re-test** all affected AC against the API spec
3. Report re-test results in Comment; notify PO

---

## Version

**Version:** 1.2 — §1 points to `pre-pr-gate`, §2 to `raise-question` section 5 (ST-000312).
**Previous:** 1.1 — Added §3 (Hotfix — QA Role), relocated from `Story_Standard_QA_template.md` §6 per devkit issue #133 (ST-000134), extending the same trim already validated on the devkit's own team.
**Previous:** 1.0 — Split out of `QA_Rules_template.md` v3.7 (former section 9 Pre-PR Gate and former section 10 Live User Instruction Conflicts, both "when acting as Implementer", relocated here as §1–§2), mirroring the boundary already validated on the devkit's own team.
**Created:** 2026-08-25
