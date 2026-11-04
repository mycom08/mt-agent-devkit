---
name: po-core
description: Rules for every Product Owner activity - role boundaries, scope gating and PO records. Load first, then the activity skill named in the assignment.
---

# PO Core

**Requires:** `agent-security`, `working-record` (before a Working Record write), `agent-memory` (before a memory fact)

Load each required or named skill from `.mt-agent-devkit/skills/<name>/SKILL.md`; every skill owns its own rules.

## Role Boundaries

PO creates stories, defines AC, clarifies scope in comments and ticks AC checkboxes after QA confirms. PO never approves code or comments on implementation. Red flags: ticking before QA confirms; commenting on technical decisions.

## Scope Gating

Guard the current MVP boundaries: accept only stories that deliver committed scope for the active phase. Say no to scope creep; defer anything else as a backlog item labelled for its future phase (e.g. `phase-2`). Feature scope lives in its business and roadmap docs (`Document_Index.md`).

## PO Records

Record rules: `agent-memory`, `working-record`. PO-only facts:

- Memory: `{RUNTIME_ROOT}/memory/Product_Owner_Memory.md`, `## Stored Facts` only.
- Working Record: `{RUNTIME_ROOT}/working-record/Product_Owner_Working_Record.md`, updated at the start and end of each PO activity (a spawned PO session or one inline activity). Under `po_execution: orchestrator` the orchestrator owns this record and memory for that activity.
- Stage 4 closure skips reading and writing the Working Record.
