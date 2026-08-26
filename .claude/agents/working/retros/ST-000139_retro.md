# Retrospective — ST-000139
**Date:** 2026-08-26
**Story:** Build Software Stage 4: make gh project create conditional for single-repo monolith builds

## Implementer — Developer
### Impediments & Unclear Points
- None.

### Process Suggestions
- None.

### What Worked Well
- The story's Technical Scope gave near-exact line numbers for every edit location (state-file field, new consultation step, conditional steps, resume-rules clause, handoff message, pipeline-rules bullet) — re-verifying against the live file found them accurate to within a line or two, so scoped edits could be applied directly without a broad re-read of the file.
- Naming a concrete existing step as the pattern to copy (same shape: one question, one state-file field, one resume-check clause) removed all design ambiguity for the new consultation step and kept it consistent with the existing analogous step.

## Reviewer — Technical Lead
### Impediments & Unclear Points
*(not submitted)*

### Process Suggestions
*(not submitted)*

### What Worked Well
*(not submitted)*

## QA
### Impediments & Unclear Points
*(not submitted)*

### Process Suggestions
*(not submitted)*

### What Worked Well
*(not submitted)*

## Product Owner
### Impediments & Unclear Points
*(not submitted)*

### Process Suggestions
*(not submitted)*

### What Worked Well
*(not submitted)*

## Orchestrator
### Observations
- `[workflow]` The pre-spawn fix from ST-000139's own kickoff (committing the retro skeleton before spawning, so `git worktree add` carries it into the isolated copy) worked as intended — the skeleton *was* present in the Developer's worktree at spawn time, confirmed in its completion report. However, a **second, independent gap** surfaced: the Developer filled in its Implementer section locally but never `git add`ed/committed the retro file as part of the PR — PR #172's diff contained only `Build_Software_Workflow.md` and `CHANGELOG.md`, no retro file. Recovered the content directly from the worktree after merge, same recovery as ST-000138 (which had the same "written but not committed" gap, for a different reason — there the skeleton itself was never committed pre-spawn, so the Dev created it fresh and then also didn't commit it). Two consecutive stories now show the retro file specifically excluded from what actually gets committed, independent of whether it existed at spawn. Worth a `Retro_Rules.md` or `Developer_Rules_Bootstrap.md` check: explicitly confirm `git status` shows the retro file staged before the final commit/push, not just before opening the PR.
