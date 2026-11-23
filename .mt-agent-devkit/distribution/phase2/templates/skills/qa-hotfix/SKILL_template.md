---
name: qa-hotfix
description: QA post-Done bug task - report the bug on the original issue, re-validate every affected AC after the fix PR and report the re-test to the PO. Load at spawn when a bug is found after a story is status:done.
---

# QA Hotfix

**Requires:** `qa-core`, `qa-validate` (re-validation), `comment`

QA-only. The Developer's fix follows `dev-hotfix`: fix branch, `status:hotfix`, PR and TL review.

1. **Report:** post a comment on the original issue describing the bug; tag Dev and TL.
2. After Dev creates the fix branch and the fix PR, **re-test** every affected AC against the API spec.
3. Report the re-test results in a comment; notify PO.
