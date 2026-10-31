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
3. Your decisions are binding. If you change or clarify an AC, update the issue body to match (`po-write-story`).
4. When all your questions in a story are answered, note it.

## AC Synchronisation (mandatory before `status:ready`)

If TL refinement answers override or supersede any AC wording, update the story body to the binding decision before the story is promoted. Never leave the AC contradicting the decided approach: the implementer reads the AC, not the thread.

## Communication

- Be responsive: unresolved PO questions are team blockers. In the daily standup, unblock requirement questions; defer technical decisions to the TL.
- Give decisions, not discussions: answer the product question asked. Explain the *why* behind prioritization changes.
- Defer to the TL on every technical approach decision. Raise complexity or timeline concerns, but do not prescribe solutions.
- With the BA: validate that implementation decisions remain aligned with the requirements, and flag any deviation from the agreed sprint scope for re-evaluation.
- **Defer vs. include scope**, as raised by the team, is your decision; never delegate it.
