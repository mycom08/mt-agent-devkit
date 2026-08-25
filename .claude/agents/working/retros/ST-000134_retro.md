# Retrospective — ST-000134
**Date:** 2026-08-25
**Story:** Carry Story_Standard_<role>.md trim into templates/ (Claude + Antigravity)

## Implementer — Developer
### Impediments & Unclear Points
- `[context]` The story pointed at a reference commit's diff to derive the trim boundary, but the target paths in that commit were already stale (renamed by a later split). Confirming the *current* diff meant re-deriving it by diffing the working copy against the template pair per role rather than reading the commit diff directly — cheap once identified, but easy to miss and act on the stale paths instead.
- `[workflow]` A multi-number slash-separated section citation in a Version-footer sentence (`` §4/§6/§12 ``) trips the corpus validator's bare-`§N` check, because its regex only recognizes a filename-prefixed citation for the first number in the chain — every number after a `/` reads as unqualified. The existing "write 'section N', never '§N'" convention for gap-documenting prose (Project_Priming §15) already covers the fix, but it isn't obviously discoverable from the error message alone for a multi-number citation that isn't itself a numbering gap.

### Process Suggestions
- `[workflow]` When relocating content from a numbered section into a companion on-demand file, checking for an internal self-citation inside the destination file (a citation that pointed at the now-empty source section) and re-pointing it to "§N above" turned out to matter — the devkit's own already-validated working copy had already done this for one of the four roles, and mirroring it kept the corpus from citing a chain instead of a direct answer. Worth calling out explicitly as a checklist step in the split-file guidance, not just inferred from precedent.

### What Worked Well
- Diffing the reference commit's per-role hunks first, then diffing the current working copy against the current template pair before writing any edit, caught the exact section-boundary and content differences (Reviewer Gate subsection folding into the same on-demand section as the notify-comment procedure, Role Boundaries collapse applying to Dev/TL/PO but not QA) that a prose summary alone would have glossed over.
- The corpus-wide grep for `Story_Standard_<role>(_template)?\.md.{0,15}§[0-9]` before editing confirmed that no external citation needed repointing, since section *numbers* never moved (only the content under them shrank to pointers) — this matched the validated working-copy precedent exactly and avoided an unnecessary wide-radius edit pass.

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
