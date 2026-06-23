# Retrospective — ST-000006
**Date:** 2026-06-23
**Story:** Split mixed-mode templates into github/ and strict/ folders

## Implementer — Developer
### Impediments & Unclear Points
- Tracked file was named `CLAUDE_TEMPLATE.md` (all-caps TEMPLATE) while the design doc referenced `CLAUDE_template.md` — required `git ls-files` check before `git rm` could be issued. Design docs should specify exact filenames (case-sensitive) when naming files to be deleted.

### Process Suggestions
- When a story names files to delete, the TL design comment should include the exact `git ls-files` path so the developer can issue `git rm` without a discovery step.

### What Worked Well
- `<!-- SHARED-START -->` / `<!-- SHARED-END -->` marker strategy was clean and easy to implement consistently across all 8 split candidates.
- TL mandatory correction was unambiguous — no interpretation needed.

## Reviewer — Technical Lead
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## QA
### Impediments & Unclear Points
*(stage skipped)*

### Process Suggestions
*(stage skipped)*

### What Worked Well
*(stage skipped)*

## Product Owner
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Orchestrator
### Observations
*(none)*
