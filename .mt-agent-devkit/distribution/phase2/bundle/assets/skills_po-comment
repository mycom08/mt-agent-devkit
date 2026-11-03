---
name: po-comment
description: Product Owner issue comments - decisions, feedback and approvals as comments in the same thread per topic, the PO comment format and Thread Status. Load before any PO comment.
---

# PO Comment

**Requires:** `po-core`, `comment`

The `comment` skill owns the template, Thread Status, writing rules, prefix bans and the Commenter gate; load it first. PO-only rules:

- Post scope decisions, AC clarifications, acceptance feedback and approvals as comments, author line `**PO - YYYY-MM-DD**`. No standalone review files.
  - **GitHub mode:** a comment on the GitHub Issue.
  - **Strict mode:** an entry in the story file's `## Comments` section (`{RUNTIME_ROOT}/docs/stories/ST-XXXXXX.md`, format in `Strict_Mode_Story_Guide.md`).
- **Same-pass body update.** When a comment changes AC or delivery expectations, update the story body to match in the same pass (`po-write-story`). A story-body decision is the decision itself, at most 5 lines, with a pointer to the resolving comment: current truth, no supersession notes (`Story_Standard.md §3`, Body Amendments). The comment announces the edit and never reproduces it (`comment` rule 5).
