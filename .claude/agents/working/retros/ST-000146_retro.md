# Retrospective — ST-000146
**Date:** 2026-09-04
**Story:** Release process: VERSION file, single CHANGELOG format, and a manual release job

## Story-Level Lessons
- A PR can open with an **empty** check rollup rather than a green one when none of its changed paths match any workflow's `paths:` filter — indistinguishable at the merge gate from "all checks passed". The repo's `[skip ci]` rule already keys on the path filter for the inverse case (suppressing a run that should fire); the same filter needs reading in this direction too, to know whether a PR gets any signal at all. Evidence: this PR changes `.github/`, `scripts/`, and three root files, none of which the sole PR-triggered workflow filters on.

## Implementer — Developer
### Impediments & Unclear Points
- `[failure]` A rehearsal script meant to run in a scratch directory ran in the repo root instead: the scratch `mkdir` failed on an unset temp-path variable, and the chained sequence continued in the original working directory, silently overwriting three tracked files mid-implementation. Nothing was committed, so `git checkout --` recovered it, but the mutation produced no error at the point of damage — only the later "changed on disk" notice made it visible.
- `[workflow]` The CI/CD validation guide's `workflow_dispatch`-only exception covers a new dispatch workflow, but this story's *other* changes also fell outside every PR path filter, so the PR gets no run at all. The guide has no branch for "no workflow fires on this PR" — see Story-Level Lessons.
- `[instruction]` The spawn prompt named an external reference implementation to model the work on and listed three intended divergences, but the reference itself carried a latent defect in one of its checks (a bullet-count pattern that also matches a horizontal-rule separator). Following the named divergences faithfully would still have copied the bug.

### Process Suggestions
- `[failure]` Any rehearsal or dry-run of a destructive script should either run in a `git worktree` or assert the scratch directory exists (`test -d "$D" || exit 1`) as its first statement, before any `cp`/`cd`. A failed `cd` leaving subsequent commands pointed at the repo root is the specific failure mode to guard.
- `[workflow]` Add a pre-PR step: read every workflow's `paths:`/`branches:` filter against the story's actual changed paths and state in the PR whether any check will fire. The `[skip ci]` rule already requires this comparison for the opposite decision; making it a single explicit check would cover both directions.
- `[instruction]` When a spawn prompt names a reference implementation, say whether it is vetted or merely a shape to copy — so the implementer knows to review its logic rather than only its structure.

### What Worked Well
- Executing both jobs' shell pipelines locally against copies of the repo's real `VERSION`/`CHANGELOG.md`/`changes.json` was the only thing that could substitute for an impossible pre-merge dispatch run — it proved the snapshot regex, section extraction, sed rewrites, and both JSON rewrites end to end, and is what surfaced the reference's separator-counted-as-bullet defect.
- The pre-start rule to read every file the story modifies caught that the four oldest CHANGELOG headings had no date at all, so the "one format" migration needed real dates recovered from `git log -S` rather than an invented placeholder.
- The validator's manifest invariant failed loudly on the new `-SNAPSHOT` key exactly as the AC predicted, making the required code change unambiguous.

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
