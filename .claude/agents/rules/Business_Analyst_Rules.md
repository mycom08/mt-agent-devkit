# Business Analyst Rules

**Applies to:** Business Analyst agent  
**Reference from:** `.claude/agents/business_analyst_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any analysis or documentation work:

1. **Read Project Priming** — `.claude/agents/context/PROJECT_PRIMING.md`
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

Before signaling completion to the orchestrator and handing off to the next stage, BA **must** commit any updates to working record or memory files made during the session:

- **What to commit:** Changes to your Working Record or any agent memory files
- **Commit message:** `Agent: <short description>` — total length under 50 characters
- **Examples:** `Agent: Update working record`, `Agent: Update BA memory`
- Push the commit before reporting stage completion to the orchestrator

> **Gate:** Do not signal stage completion until the commit is pushed.

---

## 4. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

When you cannot run tests, start the sandbox, or execute scripts due to an environment or tooling error, follow these steps in order.

**Step 1 — Check memory first**
Before diagnosing, scan `Business_Analyst_Memory.md` for a matching entry under `## Troubleshooting Facts`. If a fix is recorded, apply it directly — do not re-diagnose.

**Step 2 — Diagnose and fix**
If no match, identify the root cause and fix it properly. Do not work around it or skip the failing step.

**Step 3 — Save to memory (mandatory)**
After resolving the blocker, record the fix in `Business_Analyst_Memory.md` under `## Troubleshooting Facts` before resuming work. Use the format defined in `business_analyst_instructions.md`.

> **Gate:** Do not resume the blocked task until the fix is recorded in memory.

**Applies to:** `{test-command}` fails to run · Docker / sandbox fails to start or become healthy · integration test suite cannot connect · test script errors · CI YAML errors · auth/credential failures in test scripts

---

## Version

**Version:** 1.1 — §4 Troubleshooting Protocol: mandatory diagnose-fix-record loop for tooling/environment blockers  
**Previous:** 1.0 — Initial rules file  
**Created:** 2026-05-25
