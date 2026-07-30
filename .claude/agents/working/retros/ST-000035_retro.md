# Retrospective — ST-000035
**Date:** 2026-07-30
**Story:** Audit agent files workflow (devkit-only, Tier A detection)

## Implementer — Developer
### Impediments & Unclear Points
- `[instruction]` The AC phrase "added to the trigger table" was ambiguous about *which* table in `CLAUDE.md` — the devkit has three candidates (the "Available Commands" help table, the Sprint Workflows `Trigger|File` table scoped to `working/workflows/*`, or a full `## X Workflow` section like every other top-level devkit command gets). Resolved by precedent-matching the five existing sibling commands (Analyst/Init Project/Update Project/Build Software/Apply Retros), which all get both a full section and a help-table row — no story-blocking question needed, but a future AC naming a specific table by its literal heading would save the judgment call.
- None otherwise — the refinement thread plus the live scope-revision comment on the issue fully pre-resolved every detection-mechanics and lifecycle decision before implementation started; zero mid-implementation consultations were needed.

### Process Suggestions
- `[workflow]` A story that introduces a new gitignored runtime-output directory referenced by a workflow/template file should explicitly prompt the implementer to check `scripts/validate_templates.py`'s `RUNTIME_PATH_PREFIXES` — I caught this only because Developer Memory Fix 1 already documents the pattern; without that fact this would have shipped a CI-breaking reference (confirmed locally: bare `validate_templates.py` — CI's actual invocation — went from exit 1 to exit 0 only after adding `.claude/agents/internal/` to the list).

### What Worked Well
- Design-first was already satisfied by the issue thread itself (TL's four-point answer + PO's promotion of three new ACs + the live user scope-revision comment) — implementation needed zero new design comments or mid-implementation consultations, a clean case of the refinement pipeline doing its job before Dev ever spawned.
- Reinforces: Developer_Memory Fix 1 — the RUNTIME_PATH_PREFIXES check caught a real CI-breaking reference before it ever reached a PR.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- `[failure]` The CI job's default scan directory list does not include the working-rules tree, so the larger of the two new files was never validated by the green check — a reviewer accepting the CI verdict would have had zero evidence for it. Reinforces: Technical_Lead_Memory Fact 2 ("a green run is not evidence"); this story is the first time the uncovered path held a **new** file rather than an edited one.
- `[workflow]` A detection spec that quotes another file's section *heading text* as a matching key is a reference class no validator checks — it resolves as prose. The quoted heading here exists in only 2 of 6 sibling rules files. Section-number and file-path citations are checked; quoted heading names are not.

### Process Suggestions
- `[workflow]` When a story's own acceptance gate is a differential tool run ("any **new** finding reverts"), the reviewer should execute that exact command against both the base and the head revision and diff the sorted output — not run it once and read the exit code. Here the shared baseline was ~70 pre-existing violations and the exit code is non-zero on both sides, so a single run proves nothing in either direction. Parallel worktrees make this a two-command check with no working-tree disruption.
- `[instruction]` A size-gate that routes a long issue thread to a digest subagent needs an explicit carve-out for the acceptance-criteria list itself: AC text is the review contract and is verified clause-by-clause, so summarising it silently thins verification. Digest the discussion; read the contract verbatim.

### What Worked Well
- The resume-branch-completeness rule caught nothing here because the implementation already satisfied it — every value the state field can produce has an explicit branch, including the unobservable terminal state left by a crash between "mark complete" and "delete". Reinforces: Technical_Lead_Memory Fact 4, first story in that series to pass clean.
- Re-deriving each AC from the final file on the branch rather than from diff hunks confirmed two absence-type criteria (no roster entry, no new role file) that a hunk-only read cannot establish. Reinforces: Technical_Lead_Memory Fact 12.
- Phrasing the non-blocking nits as "at minimum these, plus any site sharing the same pattern" kept the follow-up list open rather than presenting three items as the complete inventory. Reinforces: Technical_Lead_Memory Fact 5.

#### Addendum — second review pass (independent re-run, not the canonical pass)
A fresh reviewer session re-derived all 18 AC, the stub scan, and the differential validator run from scratch. **Verdict unchanged: approve.** Deltas only:

- **Correction:** the zero-checks state on the PR head is **path-filtered**, not `[skip ci]`-suppressed. The head commit touches only `working/memory/` and `working/retros/`, and the CI workflow's `pull_request.paths` filter is `templates/**` + `workflows/**` — the run would not have been created even without the tag. Structural reason, stronger than the tag; both land in the same "nothing runnable changed" gate outcome.
- **Metric correction:** the explicit-path baseline is **67 `[ERROR]` lines** on both base and head (round 1's "70 violations" appears to have counted `[KNOWN_ISSUE]` lines too). The load-bearing result is identical — **zero new**, neither new file named in any violation. Lesson: state the counted token, not just the number, when a differential gate's evidence is a count.
- **Classification added to the quoted-heading finding above:** the under-covered heading appears in the *second* clause of a two-clause gate whose first clause is universal, so partial coverage only **narrows** detection (fewer findings) — it cannot generate false positives. That distinction is what makes it non-blocking rather than a correctness defect, and round 1 flagged it without stating it.
- **New non-blocking nit (fourth):** on the revert path the apply stage leaves the user checked out on the freshly created apply branch with no commits — the completion stage's "tell the user the branch is ready" line is conditional on the batch being *kept*, so the reverted case gets no checkout-back or branch-cleanup instruction. Same follow-up bucket as the other three.
- `[workflow]` Cost datapoint for the digest-gate question in Process Suggestions above: reading this issue's full comment thread raw cost ~20,500 characters across 7 comments (measured; the issue body it accompanies is 9,727) of context that was then resent on every subsequent turn of the review. The verification value of the thread was near zero — every decision in it had already been folded into the issue body by design, which is the body's stated purpose. This supports digesting the *discussion* while reading the AC contract verbatim, rather than skipping the gate entirely.

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
