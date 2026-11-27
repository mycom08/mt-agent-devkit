---
name: tl-implement
description: Technical Lead as story implementer - branch and PR procedure, pre-PR gate, and the status transitions with the peer-review notify comment. Load at spawn when the orchestrator assigns you as the story implementer.
---

# TL Implement

**Requires:** `git-workflow` (before creating the branch and the PR), `pre-pr-gate` (before the PR and each fix push), `comment` (before any comment or body edit)

Rare: only when `**Assigned:** Technical Lead` and you run Stage 1 (implementation). You cannot approve your own work; a Developer does the peer review.

## 1. Branch, Commits, PR

Follow `git-workflow` as every implementer does. Run `pre-pr-gate` before opening the PR and before each fix push; harness, template and rules changes run the validators and are never exempt as docs-only.

## 2. In Progress to Review

1. Remove `status:in-progress`, add `status:review`.
2. Create the PR titled `[ST-XXXXXX][DEVKIT] Story title`.
3. Add the PR URL under `## Deliverables` (`gh issue edit --body-file`).
4. Notify the Developer reviewer on the story:

   ```
   ## PR ready for peer review
   **Thread Status:** Open
   **Area:** Implementation

   **TL - YYYY-MM-DD**
   PR #NNN opened for peer review. <one-line summary of changes>

   **Next:** Developer
   ```

## 3. Review to In Progress (Developer feedback)

1. Address all CR items in the branch.
2. Push new commits.
3. Re-request review by issue comment.
