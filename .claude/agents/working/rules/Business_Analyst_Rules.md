# Business Analyst Rules

**Applies to:** Business Analyst agent  
**Reference from:** `.claude/agents/working/instructions/business_analyst_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any analysis or documentation work:

1. **Read Project Priming** — `.claude/agents/working/context/Project_Priming.md`
2. **Read your Working Record** — `.claude/agents/working/working-record/Business_Analyst_Working_Record.md`
3. **Read the relevant GitHub Issues** — filter by `sprint-N` label for the current task

---

## 2. Pre-PR Gate (when acting as Implementer)

When BA is the story Implementer, run the applicable local checks before opening a PR:

| Change type | Required local check |
|---|---|
| `.sh` files changed | `bash -n <each changed .sh file>` — zero errors |
| `.ps1` files changed | PowerShell syntax check — zero parse errors |
| `.github/workflows/` changed | Validate YAML syntax; verify job structure and step ordering |
| Docs / template / workflow only | Exempt |

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 3. Story Comment Rules

When posting comments on GitHub Issues:

- Post all BA clarifications, scope notes, and follow-up replies as **comments on the GitHub Issue** — do not create standalone files for normal discussion
- Reply in the same comment thread when following up on the same topic — do not open a new comment for each follow-up
- Follow the Comment Standard in `Story_Standard.md §9` for thread format and field usage
- Never reference stories with just a bare number — always use `ST-XXXXXX` format

---

## 4. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/working/rules/Agent_Common.md §6`.

---

## 5. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker, follow the check-memory → fix → record-to-memory protocol in `.claude/agents/working/rules/Agent_Common.md §3`.

---

## Version

**Version:** 1.0 — Initial devkit-specific version  
**Created:** 2026-06-16
