# Agent Common Working Record

## 1. Trigger and Snapshot

Interruption, blocking, multi-session continuation or explicit status snapshot activates this capability. Read/write only own bound record after guidance; initialize missing own record locally. Clean single-session work is exempt. Sync authoritative tracker status before reporting.

   **Updating it (every session, start and end):** rewrite-in-place snapshot semantics — the record holds only the current-state snapshot, not an append-only log; nothing outside the owning agent ever reads it, so nothing is lost by replacing rather than appending. At session end, overwrite Completed / In Progress / Impediments with this session's current state (never appended alongside a prior session's). Access control: read and update only your own record, never another agent's.

   **Retention:** keep only the 3 most recent story entries (unit is story entries, not calendar days) — delete older entries before writing the new one. Enforced cap: **≤ 10,000 characters** (`wc -c`, not a line count; `≤ 60 lines` is non-enforced structural guidance only). Gitignored — never commit.

   **Snapshot entry format**, one per story: **Story:** ST-XXXXXX · **Completed:** what was done, with file paths/PR numbers · **In Progress:** current work and next priorities · **Impediments:** blockers/questions/dependencies (none if clear). Bullets, not paragraphs — 3–6 one-line bullets under Completed (story ID + outcome + PR/commit ref), one bullet per open hand-off under In Progress. Evidence by pointer — link to the retro/PR/issue/memory fact, never re-narrate the session; key decisions only, no session trivia.

   **Blockers & Watch-outs** (own section, ≤ 5 lines): sprint-scoped conditions too transient for memory and too cross-story for a per-story retro (e.g. "a shared fixture is flaky — expect a retry" for the rest of the sprint). Unlike the snapshot above, this section carries forward across rewrites — not replaced — until resolved or the sprint ends.

   **Inclusion test:** would the next agent take a different action if this line were missing? If no, cut it.
