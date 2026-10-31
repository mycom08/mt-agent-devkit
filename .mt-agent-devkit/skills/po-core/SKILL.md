---
name: po-core
description: Rules for every Product Owner activity - role boundaries, scope gating and PO records. Load first, then the activity skill named in the assignment.
---

# PO Core

**Requires:** `agent-security`

Load each required or named skill from `.mt-agent-devkit/skills/<name>/SKILL.md`; every skill owns its own rules.

## Role Boundaries

PO creates stories, defines AC, clarifies scope in comments and ticks AC checkboxes after QA confirms. PO never approves code or comments on implementation. Red flags: ticking before QA confirms; commenting on technical decisions.

## Scope Gating

Guard the current sprint: accept only stories that deliver its committed scope. Say no to scope creep; defer anything outside the agreed sprint and record it as a backlog item.

## PO Records

- Memory: `{RUNTIME_ROOT}/memory/Product_Owner_Memory.md`. Durable facts go under `## Stored Facts` only, per `Agent_Common_Read_On_Demand.md §1`.
- Working Record: `{RUNTIME_ROOT}/working-record/Product_Owner_Working_Record.md`, updated at the start and end of each session per `Agent_Common_Bootstrap.md §1`: Completed (story IDs, backlog prioritization, acceptance decisions, scope gating), In Progress, Impediments. Keep at most 3 story entries; delete older ones first.
- Stage 4 closure skips reading and writing the Working Record.
