# Retrospective — ST-000147
**Date:** 2026-09-04
**Story:** sync devkit follows released tags instead of main

## Implementer — Developer
### Impediments & Unclear Points
- `[failure]` A resumed story left work uncommitted in the tree with zero commits on the branch. The half-finished state had renamed a workflow variable in a sibling file without defining it there, leaving a dangling reference that no gate would have caught — a session that ends mid-story should commit WIP rather than rely on the next session reconstructing intent from a diff.
- `[failure]` Renaming a placeholder token in a template requires a matching allow-list entry in the invariant checker; the validator failed on 25 instances of the new token until it was registered. The rename and the allow-list entry are one change, but nothing links them.
- `[context]` The AC enumerated the files needing the field-shape change by name, but a corpus-wide grep found more call sites than the AC listed (a prototype-scaffold workflow deriving a fetch base from the field, plus the repo's own root files). AC-as-file-list is not a substitute for the grep.

### Process Suggestions
- `[failure]` When a story renames a placeholder/variable token used across templates, add a step: grep the invariant checker for a token allow-list and register the new name in the same commit. Otherwise the gate fails late, after all content edits are done.
- `[workflow]` A story that changes the *shape* of a value read from a config field should require an explicit consumer inventory (grep for every reader and writer, classify each as writes / reads / merely mentions) before editing, rather than trusting the AC's file list.
- `[context]` The editing tool rewrote whole files to CRLF on this platform; only `core.autocrlf` kept the committed content LF. Worth stating in project context that the safety net exists, so the next agent does not spend a check re-deriving it.

### What Worked Well
- Building a real fixture (a temp project root, a substituted copy of each script, and a genuinely tagged public repo) exercised all six specified behaviours of both scripts end-to-end — including the two silent-exit paths that no static check can prove.
- Running both language twins against the identical case matrix caught that they agree, which a per-script syntax gate alone would not have shown.
- The template-update rule's dual-update + carve-out guidance resolved the one file with no working mirror without needing a consultation round-trip.

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
