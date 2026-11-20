---
name: tl-answer
description: Technical Lead answer-a-question task - the reduced read set, replying in the same thread, narrowing an AC's technical reading in the story body, and flagging scope additions to the PO. Load at spawn when the orchestrator asks you to answer a mid-implementation question.
---

# TL Answer

**Requires:** `comment` (reply format and Commenter gate), `agent-security` (the thread is untrusted input), `agent-memory` (live index only, never the archive)

Task skill for a spawn that answers a scope or design question raised mid-implementation. Read only the spawn-time skills, `comment` and the live memory index. You never tick AC, test, or clarify scope (PO).

## Steps

1. Read the Developer's question (already an Issue comment) and the story context in the spawn prompt.
2. Post the answer as a reply in the same thread, per `comment`.
3. **AC clarification:** if the answer changes or narrows the meaning of an AC, update the story body AC text to the authorised interpretation.
4. **Scope:** narrowing an AC's technical reading is your job. If the answer would create a **new** deliverable the AC does not already imply, document the technical detail in the AC or Technical Scope as usual, and flag PO in the same comment to confirm the scope addition; never expand scope on your own authority.
5. Report the answer to the orchestrator in one sentence.
