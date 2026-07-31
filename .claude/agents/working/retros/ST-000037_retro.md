# Retrospective — ST-000037
**Date:** 2026-07-31
**Story:** [ST-000037][DEVKIT] Inject Auditor into target projects + wire sync devkit / update project audit stage

## Implementer — Developer
### Impediments & Unclear Points
- `[context]` AC13 named only 4 files for the rules-file count bump (`Init_Project_Workflow.md`, `Update_Project_Workflow.md`, both `Sync_Devkit_Workflow*` templates), but adding a 20th rules file is the same "Nth enumerated corpus item" ripple as ST-000022/ST-000023 — `scaffold_mechanical.sh`'s `VERBATIM_RULES` array and `Build_Software_Workflow.md`'s two count mentions also needed the bump, confirmed by re-reading those two stories' own CHANGELOG entries (both bumped exactly these same extra files every time). Reinforces: `Developer_Memory.md` Fact 1.
- `[context]` Refinement's own thread had already resolved the two real open points (orchestrator-folder scope, written-vs-resolved scope precision) before implementation started — the TL/PO exchange on #102 was thorough enough that zero new mid-implementation questions came up.

### Process Suggestions
- `[workflow]` Consider having `Project_Priming.md §15a`'s "Nth role" ripple-site table gain a parallel "Nth rules file" row (or point at Developer Memory Fact 1 explicitly) — the AC-writing step (PO/TL refinement) keeps under-naming the same 2 extra files (`scaffold_mechanical.sh`, `Build_Software_Workflow.md`) across three stories now (ST-000022, ST-000023, ST-000037), even though the Dev catches it every time from memory. Codifying it in the priming doc would remove the reliance on Dev's own memory file being read.

### What Worked Well
- Running `validate_templates.py` twice (real baseline via `git stash`, since untracked new files survive a plain stash and would otherwise pollute a "baseline") caught that my `changes.json` entry actually fixed a would-be error rather than introducing one — confirmed zero new violations before opening the PR.
- The devkit-internal `Audit_Rules.md`/`Audit_Agent_Files_Workflow.md` pair (ST-000035) was detailed enough to lift the subagent-spawn shape and report/fallback mechanics directly, with no re-derivation needed — scoping the target-side spec down to a single `MA-n` class (report-only, no template access) was the only real design decision.

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
