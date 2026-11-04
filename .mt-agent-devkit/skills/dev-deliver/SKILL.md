---
name: dev-deliver
description: Developer delivery after the PR opens - PR-opened comment, status transitions, AC self-check, fix rounds (address, re-run pre-pr-gate, push, re-request review), Deliverables links and the review-to-testing handoff. Load after opening the PR and on each fix round.
---

# Dev Deliver

**Requires:** `comment` (before any comment or body edit), `pre-pr-gate` (before each fix push), `git-workflow` (push and merge sync)

## 1. After the PR Opens

1. Post on the GitHub Issue: "PR #XX opened for review — <one-line summary of what was implemented>." Tag **TL** to request review.
2. Labels: remove `status:in-progress`, add `status:review`.
3. Self-check every AC before review. Never tick an AC.

## 2. Fix Rounds (TL feedback)

1. Address each review item on the dev branch.
2. Load and re-run `pre-pr-gate` before every fix push, even in a resumed session.
3. Push, then re-request review with a short fix summary on the PR.

## 3. After TL Approval

1. Add the PR and commit links to the issue Deliverables; announce the body edit per `comment`.
2. Notify QA and perform the mechanical `status:review` → `status:testing` label handoff. QA owns the Testing work and verdict.
3. Never bypass the independent QA sign-off required before merge. After QA passes, follow `git-workflow` section 5 (merge sync).
