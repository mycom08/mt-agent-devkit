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

## Readiness Test

A `status:backlog` story is ready only when **all** blocking open points are resolved: every PO scope/AC question is answered, and every TL technical/design question is answered (confirm with the TL). The AC body must already reflect every binding decision (AC synchronisation in `po-answer-questions`). When both conditions hold, replace `status:backlog` with `status:ready`.

## Refine Sprint Stage 4 — Final Status Update

1. Fetch stories: `gh issue list --repo mycom08/mt-agent-devkit --label "sprint-N" --label "status:backlog" --state open`.
2. For each story, did the implementer post a final all-clear comment ("All open points resolved", or the Stage 1 step 7 cleared note on a story that never had questions)?
   - **Yes** → remove `status:backlog`, add `status:ready`.
   - **No**, or questions still open → leave `status:backlog`; record the story ID and reason in your report.
3. Report to the orchestrator: stories moved to `status:ready` (IDs and titles) and stories still `status:backlog` (IDs and reasons).
4. Update your Working Record (`po-core`).

## Next-Story Promotion (Sprint Workflow)

After Stage 4 of each story, when the Sprint Workflow asks for the next story, apply the readiness test above and promote a candidate only when it passes. Never promote during sprint planning.
