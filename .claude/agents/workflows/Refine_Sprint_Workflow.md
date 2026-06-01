# Refine Sprint Workflow

Triggered by: `"refine sprint"` or `"/refine-sprint"` in CLAUDE.md

**Sprint identification:** Read `Product_Backlog.md` to find the sprint marked `🔲 Planned`. That sprint's stories (labeled `sprint-N` + `status:backlog` on GitHub) are the target set.

---

## Stage 1 — Implementer Story Review

1. Orchestrator fetches all stories in the target sprint: `gh issue list --label "sprint-N" --label "status:backlog"`, reads each story's `**Assigned:**` field from the issue body, and groups stories by assignee role
2. **Spawn or resume** each required agent **in parallel** (one per role group), tracking sessions as `dev_session`, `tl_session`, `qa_session`, `ba_session` as needed — pass each agent only the story IDs assigned to their role
3. Each agent reads its own instruction files (instructions + memory + rules)
4. Each agent reads the full issue body for each of their assigned stories (User Story, AC, Technical Scope, API Spec Reference)
5. For each story with open points, the agent posts **one GitHub issue comment** following `STORY_STANDARD_DEV.md` §9 comment format:
   - Technical / design questions → tag **TL**
   - Scope / AC questions → tag **PO**
   - A single comment per story may contain questions for both agents
6. Stories with no open points require no comment — agent marks them as clear internally
7. Each agent reports to orchestrator: which stories have comments filed (agents tagged), which stories are already clear
8. Orchestrator collects all agent reports before proceeding to Stage 2

**Completion report:** Each agent returns max 5 bullets to orchestrator — story IDs reviewed, how many had comments, agent tags.

---

## Stage 2 — TL and PO Answer Questions

1. Orchestrator collates all implementer reports to determine which agents have tagged questions
2. **Spawn or resume** only the agents that have questions — **in parallel** (reuse `tl_session` / `po_session` if active):
   - TL answers all technical questions across all stories in a single pass
   - PO answers all scope/AC questions across all stories in a single pass
3. Each agent replies within the same GitHub issue comment thread; does not open new comment threads for the same topic
4. Each agent signals completion to the orchestrator (max 5-bullet summary)

---

## Stage 3 — Implementer Confirmation

1. **Resume each implementer agent** via their saved session (spawn new if expired) — only agents whose stories had questions need to be resumed
2. For each story that had questions, the assigned agent reads all TL and PO replies:
   - **If all answers are clear** → agent posts a final comment on the story:
     > "All open points resolved — story is ready for development. PO please move to ready."
     > Set `**Thread Status:** Resolved`
   - **If answers raise new questions** → agent posts follow-up in the same thread; reports back to orchestrator (loop to Stage 2)
3. **Loop limit:** Max 3 Impl→TL/PO cycles per story. If a story is still unresolved after cycle 3 → orchestrator escalates that story to the user and skips it; remaining stories continue
4. Each implementer agent reports to orchestrator when all their stories have either a final "all clear" comment or are escalated (max 5-bullet summary)

---

## Stage 4 — PO Status Update

1. **Spawn or resume** Product Owner agent via `po_session`
2. PO checks each story in the target sprint independently:
   - Implementer posted final "all clear" comment → remove `status:backlog`, add `status:ready`
   - No final comment or questions still open → leave as `status:backlog`
3. PO reports summary (max 5-bullet):
   - Stories moved to `status:ready` (IDs + titles)
   - Stories still `status:backlog` (IDs + reason)
4. Orchestrator reports PO summary to user

---

## Pipeline Rules

- **Parallel story processing** — each implementer reviews their assigned stories in one pass; TL/PO answer all tagged questions in one pass per cycle
- **Per-story independence** — each story progresses through the loop independently; a resolved story is not held back by a blocked one
- **Session reuse** — always resume an existing session before spawning
- **Loop limit** — max 3 Impl→TL/PO cycles per story before escalating to user
- **Comment discipline** — one comment thread per topic per story; no new threads for follow-up on the same question
- **Completion reports** — each agent returns max 5 bullets to the orchestrator; details go in Working Records
