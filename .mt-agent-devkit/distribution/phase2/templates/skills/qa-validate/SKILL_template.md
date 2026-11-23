---
name: qa-validate
description: QA story validation task - locating the PR and issue, per-AC verdicts, the one per-AC comment, sign-off and merge handoff, and the post-pass test-scenario commit. Load at spawn for a story validation assignment.
---

# QA Validate

**Requires:** `qa-core`, `comment` (before any comment), `raise-question` (blockers), `project-docs` (scenario location)

Task skill for a story validation spawn. Do the steps in order; none is optional.

## Locate the Work

1. Open the GitHub Issue for the story and read its AC; list the stories to test by the `status:testing` label. Verify the API spec (`docs/api/`) for every endpoint tested and use it as the reference, not live behavior; a missing or inconsistent spec: comment tagging **TL** before testing.
2. Find the linked PR in the issue's Deliverables section or its linked pull requests.
3. **Test on the dev branch.** Do not wait for the PR to merge; testing happens before merge.
4. No PR linked or story not in `status:testing`: comment on the issue for Dev.

## Verdicts

5. Before validation or sign-off read `Story_Standard.md §14`, the PASS/FAIL/NOT VERIFIED and acceptance-disposition contract. Test each criterion against live code, cross-referencing the API spec, and report current scope or revision and evidence per AC. An unperformed or insufficiently evidenced check is NOT VERIFIED, with the reason and missing evidence. Authorized skips do not certify the unexercised behavior.
6. Post one comment per story, one line per AC (criterion, verdict, pointer); reply in the same thread when re-validating. Your per-AC report may exceed the ~150–200 word cap: state the exemption in the comment to satisfy the gate's `wc -w` item. It exempts the cap only, never the transcript or one-topic rules.
7. Never tick a checkbox: `- [ ]` is not yet signed off, `- [x]` is signed off by PO after QA confirms.
8. An AC fails, or cannot be validated (missing implementation, unclear behavior): post a blocker comment tagging Dev, request the fix and keep the story in `status:testing`. No sign-off until every AC passes.

## Sign-off

9. Record sign-off as a comment on the issue (or the story MD in strict mode) before merge. No testing-pass, sign-off or done notification while any remaining AC is FAIL or NOT VERIFIED, or before the regression check (`qa-regression`) is complete.
10. **Post-pass commit, before notifying Dev to merge:** commit and push the test scenario document (`docs/feature/<feature_name>/test-scenarios/`) and the test script (`tests/feature/<feature_name>/scripts/`) to the branch QA works on with `test(<scope>): Add test scenario and script for ST-XXXXXX`. Do not give merge sign-off until both are pushed (a `qa-testing` exception has no document to commit).
11. Notify Dev to proceed with the merge and notify PO that every AC passed; PO ticks the AC and sets `status:done` at Stage 4. Gates: `Story_Standard.md §4`, `Shared_Pipeline_Stages.md` Stage 3 and 4.
