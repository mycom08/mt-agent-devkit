# Business Analyst Rules

**Applies to:** Business Analyst agent  
**Reference from:** `.claude/agents/business_analyst_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any analysis or documentation work:

1. **Read Project Priming** — `.claude/agents/context/Project_Priming.md`
2. **Read your Working Record** — `.claude/agents/working-record/Business_Analyst_Working_Record.md`
3. **Read the relevant GitHub Issues** — filter by `{feature-label}` label for the current task

---

## 2. Pre-PR Gate (when acting as Implementer)

When BA is the story Implementer, run the applicable local checks before opening a PR. Do not open the PR if any check fails.

| Change type | Required local check |
|---|---|
| Source code changed | `{test-command}` must pass AND run `{integration-test-command}` against the sandbox; all assertions must pass |
| Integration test collection or config changed | Run the relevant integration suite against the sandbox; all assertions must pass |
| Both source and tests changed | Both checks above required |
| CI workflow (`.github/workflows/`) changed | Validate YAML syntax; verify job structure and step ordering are correct |
| Docs or config only | Exempt |

Include a one-line test result note in the PR description (e.g., "`{test-command}` — PASS · integration tests — PASS").

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 3. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/rules/Agent_Common.md §6`.

---

## 4. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker (tests won't run, sandbox won't start, automation runner cannot connect, script/CI/auth errors), follow the check-memory → fix → record-to-memory protocol in `.claude/agents/rules/Agent_Common.md §3`.

---

## Version

**Version:** 1.1 — §4 Troubleshooting Protocol: mandatory diagnose-fix-record loop for tooling/environment blockers  
**Previous:** 1.0 — Initial rules file  
**Created:** 2026-05-25
