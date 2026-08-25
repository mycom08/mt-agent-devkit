# QA Rules — Read On Demand (Scenario-Conditional)

**Applies to:** QA agent. `QA_Rules_Bootstrap.md` and `Story_Standard_QA.md` are each read in full on every QA spawn regardless of task; the two sections below apply only when QA is acting as the story Implementer — rare. Read this file **only when the matching scenario actually occurs**. `QA_Rules_Bootstrap.md` §9 and §10 each still carry a one-line pointer to their relocated section here.

---

## 1. Pre-PR Gate (when acting as Implementer)

Triggered from `QA_Rules_Bootstrap.md §9`. When QA is the story Implementer, run the applicable local checks before opening a PR:

| Change type | Required local check |
|---|---|
| Source code changed | `{test-command}` must pass AND run `{integration-test-command}` against the sandbox; all assertions must pass |
| Integration test collection or config changed | Run the relevant integration suite against the sandbox; all assertions must pass |
| Both source and tests changed | Both checks above required |
| CI workflow (`.github/workflows/`) changed | Validate YAML syntax; verify job structure and step ordering are correct |
| Docs or config only | Exempt |

Include a one-line test result note in the PR description (e.g., "integration tests — PASS").

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 2. Live User Instruction Conflicts (when acting as Implementer)

Triggered from `QA_Rules_Bootstrap.md §10`.

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread (by PO, TL, or the user themselves), the live instruction takes precedence. When this happens:

1. Acknowledge the conflict explicitly — state what the prior decision was and what the new instruction is
2. Proceed with the live instruction
3. Document the override in the PR description so the reviewer understands why the prior decision was not followed

Do not silently follow the old decision, and do not block awaiting re-confirmation — the user's live instruction is the authoritative signal.

---

## 3. Hotfix (Post-Done Bug) — QA Role

Triggered from `Story_Standard_QA.md` §6. When a bug is found after story is `status:done`:

1. **Report:** Post Comment on original issue describing the bug; tag Dev and TL
2. After Dev creates a fix branch and fix PR → **re-test** all affected AC against the API spec
3. Report re-test results in Comment; notify PO

---

## Version

**Version:** 1.1 — Added §3 (Hotfix — QA Role), relocated from `Story_Standard_QA_template.md` §6 per devkit issue #133 (ST-000134), extending the same trim already validated on the devkit's own team.
**Previous:** 1.0 — Split out of `QA_Rules_template.md` v3.7 (former section 9 Pre-PR Gate and former section 10 Live User Instruction Conflicts, both "when acting as Implementer", relocated here as §1–§2), mirroring the boundary already validated on the devkit's own team.
**Created:** 2026-08-25
