# Refine Sprint Workflow

Triggered by: `"refine sprint"` or `"/refine-sprint"` in CLAUDE.md

**Sprint identification (non-feature sprint):**
Run `gh label list | grep "sprint-"` to list all sprint labels, then run `gh issue list --label "sprint-N" --label "status:backlog" --state open` for the highest-numbered sprint that returns open issues. That sprint is the target.

**Story fetch:**
`gh issue list --label "sprint-N" --label "status:backlog" --state open`

---

## Pipeline State

The orchestrator maintains `.claude/agents/working/tmp/refine_pipeline_state.md` to support resumption after unexpected termination and to preserve session IDs across stages.

**On pipeline start — always check this file first:**
- If the file **exists** → read it and resume from the recorded stage and sessions
- If the file **does not exist** → start fresh from Stage 1

**State file format:**
```markdown
# Refine Pipeline State
**Sprint:** sprint-N
**Stage:** <1 | 2 | 3 | 4>
**Loop Count:** <per-story loop counts, e.g. "#125: 1, #126: 1">
**Sessions:**
- dev_session: <agentId or empty>
- tl_session: <agentId or empty>
- qa_session: <agentId or empty>
- ba_session: <agentId or empty>
- po_session: <agentId or empty>
**Updated:** YYYY-MM-DDTHH:MM
**Observations:**
```

**Write rules:** Create at Stage 1 entry. Update `Stage` + `Updated` after each stage transition. Update `Sessions` on spawn only — never overwrite a session ID when resuming via SendMessage. Increment per-story loop count at the start of Stage 3. Append a one-line bullet to `Observations:` whenever the orchestrator makes a judgment call not covered by this workflow. Delete after workflow review is complete (see Stage 4).

---

## Stage 1 — Implementer Story Review

1. Orchestrator fetches all stories in the target sprint (using the story fetch method above), reads each story's `**Assigned:**` field, and groups stories by assignee role
2. **Orchestrator pre-fetches full story content** and passes it directly in each agent prompt — agents do not need to re-fetch stories
3. **Spawn** one agent per role that has assigned stories; save session IDs to state file as `dev_session`, `tl_session`, `qa_session`, `ba_session`. If all stories belong to one role, spawn a single agent — no parallel spawn needed. If multiple roles are present, spawn them in parallel simultaneously.
4. Each agent reads its own instruction files (instructions + memory + rules)
5. Each agent reviews the story bodies passed in the prompt and performs two mandatory checks per story:
   - **API surface check:** For every endpoint, field, or behavior referenced in the ACs, confirm it exists in the project's API spec (check `docs/api/` or equivalent) or is explicitly scoped for delivery within the same sprint. If not found, flag as an open question to TL.
   - **Unit-test AC check:** If the story introduces new service-layer methods or functions, confirm an explicit unit-test AC is present (e.g., "Unit tests added for all new service methods"). If missing, flag as an open question to PO.
6. For each story with open points, the agent records questions: post **one GitHub issue comment** following `Story_Standard_Dev.md` §9 comment format; technical/design questions → tag **TL**; scope/AC questions → tag **PO**; a single comment per story may contain questions for both agents
7. Stories with no open points require no comment — agent marks them as clear internally
8. Each agent reports to orchestrator: which stories have comments filed (agents tagged), which stories are already clear
9. Orchestrator collects all agent reports → updates state file (`Stage: 2`) → proceeds to Stage 2

**Completion report:** Each agent returns max 5 bullets to orchestrator — story IDs reviewed, how many had comments, agent tags.

---

## All-Clear Shortcut (check after Stage 1 completes)

After all implementer agents report back, check: **did every agent report all their stories clear — i.e., no GitHub comment was filed on any story?**

- **Yes — all clear:** Skip Stages 2 and 3 entirely. Go directly to Stage 4 (PO promotes stories to `status:ready`). Update state file: `Stage: 4`.
- **No — at least one story has comments:** Proceed to Stage 2 as normal.

---

## Stage 2 — TL and PO Answer Questions

1. Orchestrator collates all implementer reports to determine which agents have tagged questions
2. **Spawn or resume** TL first (reuse `tl_session` if active); save/update `tl_session` in state file
3. TL answers all technical questions across all stories in a single pass and signals completion
4. **Then spawn or resume** PO (reuse `po_session` if active); save/update `po_session` in state file — pass TL's answers summary so PO has full technical context before making scope decisions
5. PO answers all scope/AC questions across all stories in a single pass. If answering a question changes or clarifies an AC: PO updates the issue body (`--body-file` per `Story_Standard_PO.md` §15)
6. Each agent appends answers in the same comment thread — does not open new threads for the same topic
7. Each agent signals completion to the orchestrator (max 5-bullet summary)
8. Orchestrator updates state file (`Stage: 3`) → proceeds to Stage 3

> **Why TL before PO:** TL answers first so PO has full technical context when making scope decisions. This avoids TL/PO conflicts that require an extra resolution cycle.

---

## Stage 3 — Implementer Confirmation

1. **Resume each implementer agent** via saved session ID from state file (spawn new if expired); update `Sessions` in state file only if a new agent was spawned
2. Only agents whose stories had questions need to be resumed
3. For each story that had questions, the assigned agent reads all TL and PO replies. Before editing any story body, check whether TL or PO already made the edit — do not duplicate an update that was already applied.
   - **If all answers are clear** → agent posts a final comment: "All open points resolved — story is ready for development. PO please move to ready." Set `**Thread Status:** Resolved`
   - **If answers raise new questions** → agent appends follow-up to the same comment thread; reports back to orchestrator (loop to Stage 2)
4. **Loop limit:** Max 3 Impl→TL/PO cycles per story. If a story is still unresolved after cycle 3 → orchestrator escalates that story to the user and skips it; remaining stories continue
5. Orchestrator increments each story's loop count in the state file at the **start of Stage 3** — each time the implementer reads TL/PO replies and may post follow-ups counts as one cycle. Updates `Stage: 4` when all stories are resolved or escalated → proceeds to Stage 4
6. Each implementer agent reports to orchestrator when all their stories have either a final "all clear" comment or are escalated (max 5-bullet summary)

---

## Stage 4 — PO Status Update

1. **Resume** PO agent via `po_session` from state file (spawn new if expired)
2. PO checks each story in the target sprint independently:
   - Implementer posted final "all clear" comment → update story status to `ready`: remove `status:backlog`, add `status:ready`
   - No final comment or questions still open → leave as `status:backlog` (no change)
3. PO reports summary (max 5-bullet):
   - Stories moved to `status:ready` (IDs + titles)
   - Stories still `status:backlog` (IDs + reason)
4. Orchestrator reports PO summary to user
5. **Workflow review:** read `Observations:` from the state file
   - If **non-empty**: present each observation as a proposed improvement to the user; apply approved changes to this workflow file
   - If **empty**: no action needed
6. Orchestrator deletes `.claude/agents/working/tmp/refine_pipeline_state.md`, then deletes any remaining files in `.claude/agents/working/tmp/` with `rm .claude/agents/working/tmp/*.md`

---

## Pipeline Rules

- **Check state file first** — always read `refine_pipeline_state.md` before spawning any agent; resume from recorded stage if it exists
- **Session IDs in state file** — save on spawn; never overwrite on resume
- **TL before PO in Stage 2** — TL answers technical questions first; PO reads TL answers before making scope decisions
- **Story bodies in prompt** — orchestrator pre-fetches and passes issue content; agents do not re-fetch
- **Parallel implementers** — each implementer reviews their assigned stories in one pass; spawn in parallel at Stage 1
- **Per-story independence** — each story progresses through the loop independently; a resolved story is not held back by a blocked one
- **Loop limit** — max 3 Impl→TL/PO cycles per story before escalating to user; track counts in state file
- **Comment discipline** — one comment thread per topic per story; no new threads for follow-up on the same question
- **Completion reports** — each agent returns max 5 bullets to the orchestrator; details go in Working Records. Agents may append an optional `**Observations:**` section for workflow friction (unclear instructions, rule gaps, uncovered edge cases); orchestrator appends each item to `Observations:` in the state file, prefixed with the agent role
