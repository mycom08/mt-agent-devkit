# Retrospective — ST-000043
**Date:** 2026-08-20
**Story:** Split orchestrator-only content out of CLAUDE.md template

## Implementer — Developer
### Impediments & Unclear Points
- `[workflow]` A merge-strategy workflow's per-file-type list (here, a "replace verbatim" section list for a merged config file) had already drifted from the file's real heading structure before this story touched it — the list named headings that never existed as standalone sections, only as table rows inside a different section. Nothing in the corpus catches this class of drift; it surfaced only via an external contributor's comment on the story issue.
- `[instruction]` A role instruction file pointed a subagent at a section reference in the orchestrator's shared config file — a heading that had never existed. The reference was already dead before this story, made more clearly wrong by the split it foreshadowed.

### Process Suggestions
- `[workflow]` When a story splits a merged config file into two, grep every workflow file that documents that config's merge/sync logic for its old section list before editing — a stale list is easy to miss because the validator doesn't check named-heading references against real headings unless they're in `§N` numeric form.
- `[context]` Verifying "does any role file depend on this content" before moving it (as this story's AC required) is worth generalizing into a standing check whenever a shared orchestrator config file is restructured, not just for this one story.

### What Worked Well
- The AC's explicit instruction to verify section ownership against real role files, rather than trusting the issue's own list, caught nothing wrong with the four sections proposed for the move — all four confirmed orchestrator-only — but did catch a pre-existing dangling reference in a role instruction file that the story's own scope hadn't named.
- Dry-running the mechanical scaffold script locally (github and strict) before opening the PR confirmed byte-identical output across modes and caught the combine logic worked correctly on the first try — cheap, high-confidence verification for a devkit-authored file with no project-specific placeholders.
- Diffing each relocated section verbatim against its pre-split source (via `git show HEAD:<file>` + `awk` section extraction) gave a concrete, checkable answer to the "nothing silently dropped" AC rather than a visual scan.

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
*(pending)*
