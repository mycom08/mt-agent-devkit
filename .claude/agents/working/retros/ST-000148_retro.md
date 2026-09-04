# Retrospective — ST-000148
**Date:** 2026-09-04
**Story:** Remove manual version bumping from the agent corpus

## Implementer — Developer
### Impediments & Unclear Points
- `[workflow]` A "remove instruction X from the corpus" story is a classification task, not a replace task: a repo-wide grep for the retired term returned hits in four distinct classes — live instructions to fix, deliberate carve-outs to keep, historical records to leave alone, and same-named-but-unrelated artifacts (a derived per-install stamp file whose name contained the retired term as a substring). Blanket replacement would have corrupted three of the four. The AC named the removal but not the classification, so the taxonomy had to be derived first.
- `[context]` Removing an instruction leaves a functional residue the AC does not cover: several workflows still *read* the retired file to derive a value, which is not the banned hand-edit but is now stale. That residue is invisible to a grep for the banned phrasing and only surfaces by asking, per hit, "is this still true?" Raised as a consultation rather than fixed in scope.

- `[failure]` Reinforces the existing `[skip ci]`-keys-on-the-path-filter rule, which is bootstrap-tier and was read this session — and still missed. The rule is stated per *push*, but the decision that matters is per *PR head commit*: a bookkeeping commit whose own files are outside the filter still suppresses the whole PR's check run when it lands on top of content that is inside it. The result was an empty rollup, caught only because the checks command was run explicitly rather than assumed. Suggest restating the rule at the level of "the PR's head commit", not "this push's files".

### Process Suggestions
- `[workflow]` When a story removes a scattered instruction, do the classification pass as an explicit first step and record the four-class split before editing anything — the count of grep hits is not the count of edits, and the ratio here was roughly one edit per three hits.
- `[failure]` Mirrored-corpus edits are safer applied mechanically than by hand: diffing the primary file against its committed parent and replaying the hunks into the mirror, matching on path-normalised context, caught the mirror's own path-prefix divergences that a hand-repeated edit set would have flattened. Verified by re-normalising both diffs and asserting equality — worth making the standard technique for any dual-surface change.

### What Worked Well
- The dual-update + drift-check rule in the template-update procedure paid off directly: the TL rules file turned out to have no template counterpart at all, and the "no working mirror exists" carve-out meant that was a recognised state rather than a suspected miss.
- Running the corpus validator against the branch *and* against a stashed baseline, and comparing error counts rather than reading the output, cleanly separated 160 pre-existing findings from zero regressions in about one tool call.

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
*(stage skipped)*

### Process Suggestions
*(stage skipped)*

### What Worked Well
*(stage skipped)*

## Orchestrator
### Observations
*(pending)*
