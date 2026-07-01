# Retrospective — ST-000015
**Date:** 2026-07-01
**Story:** Fix devkit-internal workflow bugs: Build/Init/Update (RF-015/016/017)

## Implementer — Developer
### Impediments & Unclear Points
- `[workflow]` RF-016 AC said "fix whichever makes the two consistent" — had to read both workflow files in full before confirming the Init side was wrong; a cross-reference note in Init_Project_Workflow.md pointing to Update's expected path would have made this obvious without a two-file read.
- `[context]` RF-017: the source table annotation said ×7 but the glob `*_Workflow_template.md` only captured 6 — the mismatch between annotation and glob was not caught at authoring time; a grep or count step at authoring would have revealed it.

### Process Suggestions
- `[workflow]` When two workflow files reference the same path (e.g., Init writes to path X, Update reads from path X), add a comment in each file naming the other as the owner/consumer — makes mismatches visible without cross-file reads.
- `[workflow]` For pipeline-state write-timing, the write-rules section of the state file header (Build_Software_Workflow.md) states "Update Stage to the last completed stage" but the body stages violated this by writing at entry — adding a "write at completion, never at entry" guardrail to the write-rules block would catch future violations.

### What Worked Well
- AC explicitly stated which side to fix for RF-016 if the mismatch was ambiguous — reduced decision uncertainty.
- `validate_templates.py` exit 0 confirmed no regressions from all three edits in a single pass.
- Resume rules for Stage 4 (checking `build_state.md` per repo) are idempotent — the completion-point fix works cleanly with the existing resume logic, no additional resume-rule changes needed.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- `[workflow]` RF-016 was scoped as "devkit-internal, no version bump," but a *complete* fix necessarily edits versioned templates (CLAUDE_Shared roster/integrity, 5 rules "Reference from", Create_Stories_Shared read path). A path-move that changes where files land is almost never containable to the writer alone — it ripples to every reference. The AC's "no version bump" boxed the story into a fix that cannot actually be completed within scope.
- `[review]` The Developer's `validate_templates.py` exit-0 was cited as "no regressions," but the validator does not check instruction-path consistency between the roster/rules and the actual write location — a clean validator run gave false confidence. The regression (broken fresh-scaffold roster) was only visible via a manual grep of `_instructions` across all templates.

### Process Suggestions
- `[workflow]` For any story that changes a file's target *location* (not just its content), add a mandatory step: grep the entire template + workflow corpus for references to the old path before opening the PR, and enumerate every referrer. RF-016 had 8 referrers across 3 file classes; only the writer was updated.
- `[workflow]` When Update-side migration logic keys off a directory/marker's existence (self-healing "old→new" branch), moving Init to pre-create that marker silently disables the self-heal. Add a guardrail note in Update_Project_Workflow.md: "if Init pre-creates `instructions/`, the migration branch will not fire — Init must then own full scaffold consistency."
- `[process]` Consider a validator invariant that cross-checks the CLAUDE roster/rules "Reference from" paths against the actual instruction-file target path in Init's source table, so a location/reference divergence fails CI instead of shipping.

### What Worked Well
- RF-015 and RF-017 were cleanly separable and independently correct — being able to approve two of three RFs on their own merits kept the block precise rather than rejecting the whole PR.
- The reviewer-focus checklist explicitly directed "check whether the CLAUDE template / rules still point at the flat path" — that single instruction is what surfaced the incomplete fix; without it the roster breakage would likely have shipped.
- Story_Standard §12 "introduced vs pre-existing" gave a clean rule for separating the blocking roster/rules breakage (introduced by the file-move) from the pre-existing non-split-annotation quirk (follow-up).

## QA
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Product Owner
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Orchestrator
### Observations
*(pending)*
