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
- `[failure]` Reproducing a script's behavioural matrix surfaced a locale-dependent failure the implementer's own green run could not have shown: a PCRE-mode regex flag is refused outright under a non-UTF-8 locale, and because the call suppresses stderr the whole check goes silently inert. Same-environment verification cannot prove environment-independence; the failure is invisible precisely where it matters.
- `[context]` A change that alters the *shape* of a persisted config field only self-heals when the merge step owning that field is actually scheduled to run. Here it is not, so the migration rests permanently on every consumer's fallback parser — correct as built, but nothing in the review inputs states that dependency, so a later change could delete one fallback believing the field had migrated.

### Process Suggestions
- `[workflow]` For a story that changes how a value is *resolved* (a fetch base, a version lookup), the reviewer's differential should be "every consumer of the old shape" from a corpus grep, not the diff's file list — the mirror-tree delta line count before and after is a cheap proxy for whether a mirror was converted completely or only partly.
- `[failure]` Reinforces the retro's implementer bullet on token allow-lists: when a story registers a new token in an invariant checker, the checker file itself is often outside the paths that trigger the checker's own CI job. Worth a standing note that a gate-script edit may not be gated.

### What Worked Well
- Re-running the implementer's stated six-case matrix independently in both languages, rather than accepting the reported table, confirmed every claim and separately exposed the locale defect — a case where duplicating the implementer's verification was worth its cost rather than wasteful.
- Normalising placeholder substitutions before diffing a template against its working mirror reduced a 44 KB whole-file diff to a single line, making the mirror-drift check (Memory Fact 11) actually usable on a large file.
- The story's explicit "accepted trade-off, do not treat as a defect" and "deliberate asymmetry" notes removed two would-be findings before they cost a round — story-level pre-emption of predictable reviewer objections works.

## QA
### Impediments & Unclear Points
- `[context]` Reinforces: TL's bullet above on the PCRE-lookbehind locale failure. Independently reproduced the same silent-inert path against the unchanged (pre-existing, non-diff) extraction line, in a shell environment whose `locale` output itself reported a UTF-8 category yet still refused the flag — confirming the defect is real and environment-triggering conditions are wider than "non-UTF-8 locale" alone.
- `[workflow]` Validating a "resolves highest release tag" AC against this repo's own history is impossible while it holds 0 tags (a known, already-raised sequencing gap) — every live-tag assertion had to target external fixture repos instead, which a story's technical scope never names in advance. A story that gates behavior on this repo's own tags should say so explicitly enough that QA doesn't have to invent fixtures from scratch each time.

### Process Suggestions
- `[workflow]` For a silent-failure AC ("exit 0 without output when X"), test the *distinct* failure sub-paths separately (unreachable transport vs. reachable-but-empty-result) rather than one representative case — they can share an identical observable outcome while exercising different code, and a matrix that collapses them risks missing a defect unique to one path.
- `[failure]` When two upstream roles report agreeing on the same claimed matrix, re-deriving it against different fixture data (not just re-running the same fixture) is what actually adds signal — repeating the identical repo/case set would only confirm determinism, not correctness.

### What Worked Well
- Building fresh scratch fixtures per case (six directories, each a substituted copy of both script twins) let every AC be exercised end-to-end in both languages side by side, including the two silent-exit paths that no static/syntax check can prove.
- Testing the tag filter against a repo with real pre-release-suffixed tags (`v1.38.0-alpha.0` sorting above the true latest release) went beyond the story's own worked example and gave independent confidence in the regex anchoring itself, not just the sort-order claim.
- The dual-update carve-out guidance (accounting for the `.antigravity/` mirror's pre-existing leaner shape rather than expecting byte-parity) avoided a false mismatch finding on a file that was already asymmetric before this story touched it.

## Product Owner
### Impediments & Unclear Points
- `[context]` The story's 11 AC spanned three file categories (shell scripts, PowerShell scripts, Markdown workflows) plus dual-update requirements (working copies + templates + mirrors). QA's independent fixture builds and validator cross-checks were essential to verify completeness; a static checklist would have been blind to platform-specific defects (the locale-triggered PCRE failure TL caught).
- `[context]` The accepted trade-off (sync devkit becomes invisible until release) was critical to state upfront because it reverses user-visible behavior post-deployment. Early scope documentation prevented later scope disputes.

### Process Suggestions
- `[workflow]` Stories with dual-update requirements should carry an explicit checklist (working copies, templates, mirrors, each file listed by path) to hand off to QA. The rule exists in memory; making it AC-visible eliminates one class of incompleteness gaps.
- `[workflow]` For stories that alter a persisted config field shape, add an AC criterion naming the consumers and fallback-compatibility commitment (this story did this well: "schema changes" + "derived at use time"). Prevents reviewers from blocking on un-stated assumptions about how old instances will self-heal.

### What Worked Well
- Scope was precisely bounded by 11 specific, testable AC. No feature creep, no scope disputes during implementation.
- The story's pre-emptive framing of the accepted trade-off ("sync devkit becomes invisible until release; do not treat as a defect") prevented reviewer objections on a deliberate decision.
- QA's independent fixture-based validation (real tagged repos, locale testing, multiple silent-exit paths tested separately) proved both the happy path and all five failure modes, giving confidence no edge case was missed.
- Release delivery was immediate post-merge (v0.1.48 tagged within the merge window), proving the mechanism works end-to-end and the story's business value is realized at delivery time.

## Orchestrator
### Observations
*(pending)*
