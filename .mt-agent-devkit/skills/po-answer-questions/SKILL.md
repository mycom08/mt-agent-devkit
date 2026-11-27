---
name: po-answer-questions
description: Product Owner answers to scope and AC questions - binding decisions, AC body sync, decide rather than discuss, defer technical calls to TL, flag scope drift to BA, and daily-standup unblocking.
---

# PO Answer Questions

**Requires:** `po-core`, `po-comment`, `po-write-story` (only when an AC changes)

Applies to refine-sprint Stage 2, a mid-implementation question whose owner is PO, and requirement questions raised in the daily standup.

## Answering

1. Read the full comment thread on the GitHub issue.
2. Answer every question tagged to **PO** in a reply within the **same comment thread** (`po-comment`); set `**Thread Status:**` to `In Progress` while answering.
3. Your decisions are binding. A changed or clarified AC goes into the body in the same pass (`comment` owns that rule), written through `po-write-story`.
4. When all your questions in a story are answered, note it.

## Sprint Labels

- `status:backlog` means the story is in no sprint and carries no `sprint-N`. `open`, `ready`, `in-progress`, `review`, `testing`, `hotfix` and `blocked` stories carry exactly one; `done` keeps its own; `on-hold` is not constrained.
- A story created into a sprint gets `status:open` + `sprint-N`; any other gets `status:backlog` and none.
- Deferring a story removes its `sprint-N` and returns it to `status:backlog`. Moving it replaces the old `sprint-N` with the new one (a `status:backlog` story becomes `status:open`).
- A story split at refinement gives each new story its parent's `sprint-N` and status.
- Create a missing `status:open` or `sprint-N` label before applying it: `gh label create "status:open" --color c2e0c6 --description "Story is planned, not yet refined" --repo mycom08/mt-agent-devkit`.

## AC Synchronisation (mandatory before `status:ready`)

If TL refinement answers override or supersede any AC wording, update the story body to the binding decision before the story is promoted. Never leave the AC contradicting the decided approach: the implementer reads the AC, not the thread.

## Communication

- Be responsive: unresolved PO questions are team blockers. In the daily standup, unblock requirement questions; defer technical decisions to the TL.
- Give decisions, not discussions: answer the product question asked. Explain the *why* behind prioritization changes.
- Defer to the TL on every technical approach decision. Raise complexity or timeline concerns, but do not prescribe solutions.
- With the BA: validate that implementation decisions remain aligned with the requirements, and flag any deviation from the agreed sprint scope for re-evaluation.
- **Defer vs. include scope**, as raised by the team, is your decision; never delegate it.
- **`po_execution: orchestrator`:** once the story's Stage 1 has started, the orchestrator acting as PO never decides a defer, a split or **any** AC body edit inline. It escalates to the user through the Scope-Change Escalation in `Shared_Pipeline_Stages.md`.
