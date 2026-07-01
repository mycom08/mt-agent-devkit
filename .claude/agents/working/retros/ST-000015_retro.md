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
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

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
