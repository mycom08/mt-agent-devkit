---
name: po-promote-ready
description: Product Owner story status workflow and readiness test - promote backlog stories to status:ready after refinement, and promote the next ready story in the Sprint Workflow.
---

# PO Promote Ready

**Requires:** `po-core`

## Story Status Workflow

| Status | Who changes | When | Label |
|---|---|---|---|
| **Backlog** | **PO** | After creation | `status:backlog` |
| **Ready** | **PO** | After assigning to implementer | `status:ready` |
| In Progress | Implementer | Dev branch created | `status:in-progress` |
| Review | Implementer | After PR created | `status:review` |
| Testing | TL | After TL PR approval | `status:testing` |
| **Done** | **PO** | After all AC pass and checkboxes ticked | `status:done` |

GitHub mode changes the label; strict mode edits the story file's `**Status:**` field to the same value.

## Readiness Test

Run these steps for each story, in order, right before you set `status:ready`:

1. **Open points.** The story has a real `**Assigned:**` role; every blocking PO scope/AC question is answered, and every TL technical/design question is answered (confirm with the TL).
2. **AC against the decided approach.** Read each AC beside the approach decided on the story: the TL refinement answers, any design-first approval and any technical design the story links. Where an AC differs from that approach, re-sync the body first (`po-write-story`, announced with `po-comment`); the body must reflect every binding decision (AC synchronisation in `po-answer-questions`).
3. **Dependencies.** Check the story's `**Depends on:**` line against the state of each named story. A dependency that is neither done nor scheduled ahead of this story in the sprint keeps it in `status:backlog`; record the story ID and reason in your report.
4. **Promote.** Only when steps 1–3 pass, replace `status:backlog` with `status:ready`.

If new questions arise after `status:ready`, set it back to `status:backlog` and notify the implementer.

## Refine Sprint Stage 4 — Final Status Update

1. Fetch stories: github mode `gh issue list --label "sprint-N" --label "status:backlog" --state open`; strict mode the sprint's story files with `**Status:** backlog`.
2. For each story, did the implementer post a final all-clear comment ("All open points resolved", or the Stage 1 step 7 cleared note on a story that never had questions)?
   - **Yes** → run the readiness steps above; when they pass, move it from `status:backlog` to `status:ready`.
   - **No**, or questions still open → leave `status:backlog`; record the story ID and reason in your report.
3. Report to the orchestrator: stories moved to `status:ready` (IDs and titles) and stories still `status:backlog` (IDs and reasons).
4. Update your Working Record (`po-core`).

## Next-Story Promotion (Sprint Workflow)

After Stage 4 of each story, when the Sprint Workflow asks for the next story, run the readiness steps above and promote a candidate only when it passes. Never promote during sprint planning.
