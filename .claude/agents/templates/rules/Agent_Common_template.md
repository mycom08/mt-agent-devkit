# Agent Common Protocol

**Applies to:** All agents (Developer, Technical Lead, QA, Product Owner, Business Analyst)
**Purpose:** Single source for the mechanics every agent shares — memory format, troubleshooting protocol, retrospective, and working-record handling. Your role instruction file lists the **file paths** for your own records; this file defines **what to do with them**. Where this file and a role-specific rule disagree, the role-specific rule wins.

---

## 1. Pre-Work Sequence

Your instruction file lists the exact paths for your Project Priming, Working Record, Rules, and Memory. Read them in this order:

**Fresh start (newly spawned):**
1. Project Priming — canonical project overview, architecture, document locations
2. Your Working Record — last session's progress and impediments
3. Your Rules — mandatory role rules
4. Your Memory — durable conventions and decisions

**Resumed session (continuing via `SendMessage`):**
1. Skip Project Priming — already in context
2. Re-read your Working Record to catch updates since the last turn

> Lightweight tasks (e.g., PO story closure) override this sequence — see your role instructions for the reduced read set.

---

## 2. Project Memory

Update your memory file when you encounter a fact worth remembering for future sessions.

- Record **durable facts only** — not current task state or conversation context.
- Prefer updating an existing fact over adding a duplicate.
- Keep entries short and practical.

**Format:**

```md
## Stored Facts

### Fact N
- **Fact:** ...
- **Source:** ...
- **Reason:** ...

## Troubleshooting Facts

### Fix N — <short label>
- **Problem:** Short label (e.g., "Docker sandbox fails to start")
- **Symptoms:** Exact error message or observable behavior
- **Root Cause:** Why it happened
- **Fix:** Exact commands/steps to resolve
- **Prevention:** What to check upfront to avoid this next time
```

> PO and BA record `## Stored Facts` only — the `## Troubleshooting Facts` section applies to roles that run tooling (Developer, Technical Lead, QA).

---

## 3. Troubleshooting Protocol

Applies on any tooling/environment blocker: tests fail to run · sandbox fails to start or become healthy · automation runner cannot connect · test script errors · CI YAML errors · auth/credential failures in test scripts.

**Step 1 — Check memory first.** Scan your memory file's `## Troubleshooting Facts` for a matching entry. If a fix is recorded, apply it directly — do not re-diagnose.

**Step 2 — Diagnose and fix.** If no match, find the root cause and fix it properly. Do not work around it or skip the failing step.

**Step 3 — Save to memory (mandatory).** After resolving, record the fix under `## Troubleshooting Facts` using the §2 format before resuming.

> **Gate:** Do not resume the blocked task until the fix is recorded in memory.

---

## 4. End-of-Work Retrospective

Before reporting back to the orchestrator, write your retrospective section to the story retro file:

1. Read `.claude/agents/rules/Retro_Rules.md` for the three questions and format
2. Open `.claude/agents/retros/ST-XXXXXX_retro.md` (story ID is in your spawn prompt)
3. Overwrite the `*(pending)*` placeholders in **your own section only** — see the section name in your role instructions
4. Then report back

---

## 5. Working Record

Update your Working Record at the start and end of each session.

**When starting:** Read your record to understand last session's progress and impediments. Roles that own GitHub story status (Developer, TL, QA) also **sync story statuses with GitHub** — check the current label on each in-progress or recently completed story and correct the record before reporting status.

**When ending:** Log Completed (with file paths, PR numbers, story IDs), In Progress, and Impediments.

**Access control:** Read and update only your own record. Never read or modify another agent's record.

**Retention:** Keep only the 3 most recent days (QA: 3 most recent story entries). Delete older entries before writing the new one. Working Records are gitignored — never commit them.

**Standup entry format** — one entry per day:
- **Date:** YYYY-MM-DD
- **Completed:** What was done (tasks, features, bug fixes — with file paths, PR numbers, story IDs)
- **In Progress:** Current work and next priorities
- **Impediments:** Any blockers, questions, or dependencies (none if clear)

---

## 6. Stage-Transition Commit (implementer & reviewer roles)

Before signaling completion to the orchestrator, commit any **agent memory file** changes made during the session:

- Commit memory files only — the Working Record is gitignored and must not be committed
- Commit message: `Agent: <short description>` — under 50 characters (e.g., `Agent: Update QA memory`)
- If no memory files changed, skip the commit — do not create an empty commit
- Push before reporting stage completion

> **Gate:** Do not signal stage completion until the commit is pushed (if applicable).
