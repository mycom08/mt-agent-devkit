---
name: po-comment
description: Product Owner issue comments - decisions, feedback and approvals as comments in the same thread per topic, the PO comment format and Thread Status. Load before any PO comment.
---

# PO Comment

**Requires:** `po-core`

Follow the comment standard in `Story_Standard.md §9` and run the Commenter gate in `Story_Standard.md §12` before posting.

- Post scope decisions, AC clarifications, acceptance feedback and approvals as **comments on the GitHub Issue**. No standalone review files.
- Reply in the same thread for the same topic. **One topic per comment:** answer what was asked; an unasked finding gets its own comment. Batching replies to questions asked together is fine.
- Never use the `@` prefix (write `**Dev**`, `**TL**`) or a bare `#` prefix (use `ST-XXXXXX` or plain text).
- **Writing standard:** decision first (first line is the outcome); rationale at most 2–3 sentences per point; about 150–200 words, drafted to shape rather than trimmed; corrections state the delta only; one close-out line per thread.
- When a comment changes AC or delivery expectations, update the issue body to match (`po-write-story`). A story-body decision is the decision itself, at most 5 lines, with a pointer to the resolving comment: current truth, no supersession notes (`Story_Standard.md §3`, Body Amendments).
- **Announce body edits, never reproduce them.** State which section changed, what kind of change and why, never the resulting AC text, which would go stale at the next rewording (`Story_Standard.md §9` rule 5). Example: "AC6 reworded — added an X carve-out, per the reviewer's point that <reason>. Body updated."

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved
**Area:** [Workflow / Template / AC / File]

**PO - YYYY-MM-DD**
Scope decision or AC clarification.

**Decision:** [What we decided and why]
**Next:** [Owner or "None"]
```
