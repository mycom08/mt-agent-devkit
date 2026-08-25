# Retrospective — ST-000133
**Date:** 2026-08-25
**Story:** Carry Developer/TL/QA/PO Rules bootstrap/on-demand split into templates/ (Claude + Antigravity)

## Implementer — Developer
### Impediments & Unclear Points
A prior session's split (8 new files) had two latent bug classes that only surfaced on `validate_templates.py`: (1) cross-tier `§N`/`§N–§M` en-dash ranges where only the first number was file-qualified by the checker's regex — e.g. `` `File.md` §10–§11 `` resolves §10 but leaves §11 bare, checked against the wrong file's headings; (2) adding the new files' stems to `SECTION_REF_ALIAS` exposed a genuinely wrong citation in `Product_Owner_Rules_Bootstrap_template.md`'s version footer, where the regex bound a bare `§11a` to the nearest preceding `.md` mention (a different file) rather than the file it was actually describing. Both required rewriting the surrounding prose (`§N and §M`, or dropping the `§` glyph for historical/descriptive text) rather than a mechanical find-replace — worth flagging in the split checklist since the working-copy reference model (`Developer_Rules_Bootstrap.md` §61, `working/rules/Developer_Rules_Bootstrap.md`) has the same en-dash-range pattern uncaught only because `validate_templates.py` never scans `working/`.
Scope boundary judgment call: `.claude/agents/working/workflows/Sync_Devkit_Workflow.md` (the devkit's own installed working-copy workflow, distinct from the template) still cites the pre-split `Agent_Common.md` — meaning ST-000132 never touched this file either. Left it untouched to match that precedent rather than silently expanding scope into an unrelated pre-existing gap; flagged in the PR description instead.

### Process Suggestions
When adding a role's stems to `SECTION_REF_ALIAS`, re-run the validator immediately after — new aliases can surface previously-invisible section-ref bugs in citations that "coincidentally" passed before because the stem wasn't recognized. Don't treat a clean run before the alias addition as proof the citations were already correct.

### What Worked Well
The `git show <ST-000132-commit>` diff (`b3fdf91`) was a reliable, literal template for every mechanical step this story needed — Init/Update/Sync workflow enumeration edits, `ALLOWLIST_REMOVED_PATHS`/`SECTION_REF_ALIAS` shape, and the `changes.json` "add under the existing un-bumped version" convention all transferred directly with the four new filenames substituted in. Diffing a prior story's actual commit, not just reading its retro prose, caught details (e.g. the exact "modified" vs "new" split, the historical-entry preservation pattern) that prose summaries alone would have missed.

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
