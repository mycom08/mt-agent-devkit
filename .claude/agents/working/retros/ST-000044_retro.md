# ST-000044 Retro

## Story-Level Lessons

*(none recorded yet)*

## Implementer — Developer

### Impediments & Unclear Points
- `[context]` The story pointed at a suggested fix location (a Claude Code skill under a skills directory) but this repo had no prior scaffolding path from `templates/` into anything outside `.claude/agents/` — required tracing the mechanical-scaffold, sync, update-project, and remote-fetch merge mechanisms from scratch (four separate files) to add one new deployable file type end to end.
- `[context]` The issue's own file count for the pattern it found (a fixed number of hand-rolled citations) did not transfer to this repo — a fresh audit was required, and it surfaced a much larger citation count of a different dominant symptom (bare citations, not the off-by-one) than the issue emphasized. Reports of a pattern found in a downstream deployment should not be assumed to reflect the source repo's current state without re-auditing.

### Process Suggestions
- `[workflow]` When a story explicitly grants scope-judgment authority (as this one did) for a corpus-wide cleanup with a very large hit count, stating the proportionality boundary explicitly (e.g., "fix the named example only, plus the mechanism, not every site") in the CHANGELOG/PR up front made the judgment call auditable — worth keeping as a pattern for future "closing a systemic gap" stories.

### What Worked Well
- A newly-created skill became visible in this very session's own available-skills listing immediately after the file was written — confirmed the fix actually closes the discoverability gap the issue described, rather than just asserting it would.
- The existing "new mechanical-tier file" ripple pattern (scaffold script → sync workflow → update-project workflow → remote-fetch Universal set) from a prior story's fix generalized cleanly to a file type living outside `.claude/agents/` entirely, with only one adjustment (treating it as a sibling directory rather than a nested one).
