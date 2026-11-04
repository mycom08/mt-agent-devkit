---
name: dev-hotfix
description: Developer post-Done bug task - never fix on main; branch preflight for a fix branch, status:hotfix, PR and TL review, then status:testing and QA re-validation. Load at spawn when assigned a bug in a story that is already status:done.
---

# Dev Hotfix

**Requires:** `dev-core`, `git-workflow` (preflight and commits), `pre-pr-gate` (before the PR), `dev-deliver` (PR comment and fix rounds)

Task skill for a bug found after a story is `status:done`. **Never fix on the feature branch or main/master.** Full procedure with red flags: `Story_Standard.md §6`.

## Steps

1. Run `branch_preflight.py inspect` and `create` for `fix/ST-XXXXXX/short-description` from the story's immutable Base Branch (the feature branch), with the verified full Base/Remote Base SHAs. Only after a successful `create`, set the issue to `status:hotfix`. A BLOCKED preflight stops for direction.
2. Fix on that branch, run `pre-pr-gate`, open a PR targeting the **feature branch** and request TL review.
3. After TL approval: merge, set `status:testing`, and notify QA to re-test the affected AC.
4. QA reports results; PO ticks the AC and sets `status:done`. Never tick AC or set Done yourself.
