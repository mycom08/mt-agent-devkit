# Business Analyst Rules — Bootstrap

**Applies to:** Business Analyst agent — devkit's own team only (`.claude/agents/working/`).
**Reference from:** `.claude/agents/working/instructions/business_analyst_instructions.md`
**Purpose:** The whole of BA's bootstrap-tier rules — everything true on *every* BA spawn regardless of task. Read this file in full per the Pre-Work Checklist. Read `Business_Analyst_Rules_Read_On_Demand.md` only when a trigger in §6 actually fires.

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any analysis or documentation work:

1. **Read Project Priming** — `.claude/agents/working/context/Project_Priming_Bootstrap.md`
2. **Read your Working Record** — `.claude/agents/working/working-record/Business_Analyst_Working_Record.md`
3. **Read the relevant GitHub Issues** — filter by `sprint-N` label for the current task

---

## 3. Story Comment Rules

When posting comments on GitHub Issues:

- Post all BA clarifications, scope notes, and follow-up replies as **comments on the GitHub Issue** — do not create standalone files for normal discussion
- Reply in the same comment thread when following up on the same topic — do not open a new comment for each follow-up
- Follow the Comment Standard in `Story_Standard.md §9` for thread format and field usage
- Never reference stories with just a bare number — always use `ST-XXXXXX` format

---

## 4. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/working/rules/Agent_Common_Read_On_Demand.md §5`.

---

## 5. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker, follow the check-memory → fix → record-to-memory protocol in `.claude/agents/working/rules/Agent_Common_Read_On_Demand.md §2`.

---

## 6. On-Demand Rules — Routing Table

§1, §3–§5 above are loaded at spawn. Nothing in `Business_Analyst_Rules_Read_On_Demand.md` is. When a trigger below fires, fetch **only** the named section with the `read-section` skill — not the whole file.

| Trigger | Fetch |
|---|---|
| Orchestrator assigns BA as story implementer | `Business_Analyst_Rules_Read_On_Demand.md §1` (Pre-PR Gate) |

> Triggers shared by all six roles that are not restated here — writing a memory fact, the end-of-work retro, credential-gated verification, stage-transition commit, troubleshooting — are routed by `Agent_Common_Bootstrap.md §5` and §4–§5 above.

---

## Version

**Version:** 2.0 — Split into `Business_Analyst_Rules_Bootstrap.md` (this file) + `Business_Analyst_Rules_Read_On_Demand.md`, matching the Dev/TL/QA/PO bootstrap/on-demand convention. §2 (Pre-PR Gate, when acting as Implementer — rare, BA is not usually the story implementer) moved to the on-demand file; §1/§3–§5 stayed, being needed at spawn regardless of task. Added §6 routing table. `§2`'s number is retired, not reused.
**Previous:** 1.0 — Initial devkit-specific version
**Created:** 2026-06-16
