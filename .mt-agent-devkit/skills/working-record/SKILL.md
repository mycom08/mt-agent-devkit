---
name: working-record
description: Working Record rules - rewrite-in-place snapshot, own-record access, 3-entry retention, 10,000-character cap, entry format and Blockers & Watch-outs. Load before any Working Record write.
---

# Working Record

**Requires:** `pre-work` (when the record is read)

Canonical owner. `generate_common_blocks.py` copies part `format` into `Agent_Common_Bootstrap.md` §1 and `Agent_Common_Working_Record.md`; edit here, then regenerate.

## Before Every Write

1. Write only your own record at `{RUNTIME_ROOT}/working-record/<Role>_Working_Record.md`, at session start and end. Missing concrete bindings block.
2. Before reporting status, sync each in-progress story's tracker status and correct the record.
3. Delete entries older than the 3 most recent story entries before writing the new one.
4. Keep every line short and fact-based: file paths, PR numbers, story IDs, commits, design decisions, validation results.
5. Check the cap with `wc -c` after writing.

## Rules

<!-- part: format -->
   **Updating it (every session, start and end):** rewrite-in-place snapshot semantics — the record holds only the current-state snapshot, not an append-only log; nothing outside the owning agent ever reads it, so nothing is lost by replacing rather than appending. At session end, overwrite Completed / In Progress / Impediments with this session's current state (never appended alongside a prior session's). Access control: read and update only your own record, never another agent's. Exception: the orchestrator acting as PO under `po_execution: orchestrator` owns the PO record and memory for that activity.

   **Retention:** keep only the 3 most recent story entries (unit is story entries, not calendar days) — delete older entries before writing the new one. Enforced cap: **≤ 10,000 characters** (`wc -c`, not a line count; `≤ 60 lines` is non-enforced structural guidance only). Gitignored — never commit.

   **Snapshot entry format**, one per story: **Story:** ST-XXXXXX · **Completed:** what was done, with file paths/PR numbers · **In Progress:** current work and next priorities · **Impediments:** blockers/questions/dependencies (none if clear). Bullets, not paragraphs — 3–6 one-line bullets under Completed (story ID + outcome + PR/commit ref), one bullet per open hand-off under In Progress. Evidence by pointer — link to the retro/PR/issue/memory fact, never re-narrate the session; key decisions only, no session trivia.

   **Blockers & Watch-outs** (own section, ≤ 5 lines): sprint-scoped conditions too transient for memory and too cross-story for a per-story retro (e.g. "a shared fixture is flaky — expect a retry" for the rest of the sprint). Unlike the snapshot above, this section carries forward across rewrites — not replaced — until resolved or the sprint ends.

   **Inclusion test:** would the next agent take a different action if this line were missing? If no, cut it.
<!-- /part: format -->
