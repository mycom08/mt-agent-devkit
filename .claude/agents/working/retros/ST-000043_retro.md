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

### Round 2 addendum (TL CHANGES REQUESTED — CR-1, CR-2)
- `[failure]` "Verify no subagent needs this content" (this story's own AC1 check) is necessary but not sufficient for deciding a section can move into an always-overwritten file — it misses that the section might be **project-mutable** (edited/preserved locally by another workflow, e.g. a path repair or a lean-role override), which is a different ownership question entirely. Both checks are needed before reclassifying a section's merge tier, not just the read-need one.
- `[workflow]` A workflow that scaffolds a new repo via **remote fetch** (`{DEVKIT_SOURCE_URL}`) has its own separate enumeration of "every devkit-scaffolded repo gets these" and cannot benefit from a local mechanical-script update — this is the same ripple-miss shape Memory Fact 1 already tracks for role/rules/workflow additions, now confirmed to extend to any new mechanical-tier file, not just those three categories.
- Reinforces: Memory Fact 11 (extended in place with both round-2 lessons rather than duplicated as new facts).

## Reviewer — Technical Lead
### Impediments & Unclear Points
- `[failure]` Relocating a section between files silently changes its **merge contract**, and no AC or checklist asks about that. One relocated section had deliberately been excluded from the merge workflow's "replace verbatim" list — i.e. it was project-preserved — and landed in a file documented as "always overwrite in full". Two downstream mechanisms depended on the old contract and broke without any diff hunk touching them. Evidence: PR CR-2.
- `[failure]` Adding an Nth item to an enumerated corpus set missed a ripple site for the 5th consecutive story, and for the 2nd time in the *same* file — a deployed workflow template whose scaffold set is written out longhand because it fetches remotely and cannot call the local scaffold script. Evidence: PR CR-1; prior occurrence recorded in the reviewer working record's Blockers & Watch-outs.
- `[workflow]` The corpus's own validator emits ~36 findings of one class purely as a path-separator artifact on one OS, so a differential run is the only usable signal. This story added 4 more of that same class, which is indistinguishable from 4 real regressions without classifying them by hand.

### Process Suggestions
- `[workflow]` Any story that **moves** content between two files should require the implementer to state, per moved section, its before/after write strategy (preserved vs. overwritten, adaptive vs. verbatim) — a content-identity diff proves nothing about this, and a content-identity diff is exactly what the "no content loss" AC asks for.
- `[workflow]` Extend the enumerated-set ripple check to cover *scaffold sets written longhand for remote-fetch contexts* — these cannot inherit a local scaffold script's changes, so a new deployed file is invisible to them by construction.
- `[failure]` Where a validator has a known one-OS false-positive class, record the baseline count in the corpus so a reviewer can subtract it instead of re-deriving the classification each story.

### What Worked Well
- Refusing to accept the implementer's "diffed verbatim, zero content loss" claim and re-extracting all sections from the pre-split file independently: it confirmed the claim exactly as stated, which then made it safe to spend the remaining effort on the contract question the claim could never have covered.
- Actually executing the scaffold script for both modes rather than reading it — cheap, and it converted an AC from "looks right" to "produced the right bytes".
- Reading the removed lines of the merge-strategy list as *evidence about the old behavior*, not just as churn. The one section absent from that list was the whole of the second blocking finding.

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
