# Agent Common Working Record

## 1. Trigger and Snapshot

Interruption, blocking, multi-session continuation or explicit status snapshot activates this capability. Read/write only own bound record after guidance; initialize missing own record locally. Clean single-session work is exempt. Sync authoritative tracker status before reporting.

   **Updating it (every session, start and end):** rewrite-in-place snapshot semantics — the record holds only the current-state snapshot, not an append-only log; nothing outside the owning agent ever reads it, so nothing is lost by replacing rather than appending. At session end, overwrite Completed / In Progress / Impediments with this session's current state (never appended alongside a prior session's). Access control: read and update only your own record, never another agent's.

   **Retention:** Keep only the **3 most recent story entries** — the retention unit is story entries, not calendar days (all roles). Delete older entries before writing the new one. The enforced cap is the value of **`**Working record cap:**`** in this project's `{{ROOT_FILE}}` (default **4,000** if the field is absent), measured with `wc -c` — not a line count. `≤ 60 lines` is retained only as non-enforced structural guidance for a soft-wrapped, one-bullet-per-entry format; it is not itself checked. Working Records are gitignored — never commit them.

   **Snapshot entry format** — one entry per story:
   - **Story:** ST-XXXXXX
   - **Completed:** What was done (tasks, features, bug fixes — with file paths, PR numbers)
   - **In Progress:** Current work and next priorities
   - **Impediments:** Any blockers, questions, or dependencies (none if clear)

   **Blockers & Watch-outs** (own section, capped at **≤ 5 lines**): sprint-scoped conditions that are too transient for a memory file and too cross-story for a per-story retro (e.g. "a shared fixture is flaky — expect a retry" for the rest of the sprint). Unlike the per-story snapshot above, this section **carries forward across rewrites** — it is not replaced when you overwrite Completed/In Progress/Impediments — until the condition is resolved or the sprint ends, whichever comes first.

   **Inclusion test (apply before adding any line to any section):** *would the next agent take a different action if this line were missing?* If no, cut it.

   **Entry-writing rules:**
   - **Bullets, not paragraphs.** 3–6 bullets under Completed, one line each (story ID + outcome + PR/commit ref); one bullet per open hand-off under In Progress.
   - **Evidence by pointer.** Detail lives in the retro, PR, issue comment, or memory fact — the record links to them, never re-narrates the session. A resuming agent needs "what shipped, what's awaiting whom, any traps" — not a transcript.
   - Key decisions only — session trivia (starting tools, deleting throwaway files) doesn't belong in the record.
