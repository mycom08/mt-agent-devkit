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
- **Working Record.** A comment is part of the PO activity it serves; the record is updated at that activity's start and end (`po-core`), not per comment.

## Before Each Post

Run these steps for every post, right before it:

1. Write the body to a temporary file.
2. Run the word count before posting: `wc -w <body-file>` must be within the `comment` length cap. If it is over, remove the bundled second topic or pasted detail, then count again.
3. Run the `comment` skill's Commenter gate on the same file.
4. Post it (github mode with `--body-file`; strict mode by appending the checked text to the story file's `## Comments` section), then delete the file.
