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
- `[workflow]` Reinforces: Story-Level Lessons (empty rollup ≠ pass) and Memory Fact 19. This story is the *opposite* direction of devkit#189: there a matching path filter had its run suppressed by `[skip ci]`; here no filter matches at all. `validate-templates.yml`'s `paths:` omits `scripts/**`, so a PR editing the gate script itself never runs the gate — filed as N4 in PR #193 comment 5535235071.
- `[instruction]` `CICD_Validation_Guide.md`'s `workflow_dispatch` exception scopes cleanly to the dispatch file, but the guide has no branch for a PR where *no* workflow fires on *any* changed path, so the reviewer has to reason from first principles about whether the empty rollup is a waiver or a gap. Same gap the implementer hit from the other side.

### Process Suggestions
- `[workflow]` The reviewer gate should require the implementer to state which workflow (if any) is eligible for the PR's changed paths, not just cite a run URL — the URL alone cannot distinguish "the right check ran" from "a different check ran and nothing covers the rest". Evidence: the cited run was `validate-templates.yml`, correct here only because the retro commit was the sole delta from the validated SHA.
- `[instruction]` When a spawn prompt hands over an implementer's stated rationale for a deliberate divergence, re-derive the rationale rather than the conclusion. Here the conclusion (`- ` over `-`) was right and the stated reason was wrong — the driver is the `---` the workflow's own bump-forward step emits, not the CHANGELOG's pre-existing separators, which sit outside every version section.

### What Worked Well
- Rehearsing both jobs' pipelines against copies of the branch's real files in a `git worktree` was the only way to adjudicate a dispatch-only job that cannot run pre-merge; it independently confirmed the stamp, the `0,/re/` newest-key rename, newest-first ordering after bump-forward, and — the thing no AC asked for — that the post-release empty manifest entry still passes the validator, so a release cannot break the next PR's gate.
- Running `validate_templates.py` from a detached worktree at the exact head SHA (the standing watch-out in my working record) substituted cleanly for the absent CI result, and the script's `REPO_ROOT = Path(__file__).parent.parent` derivation made the worktree run genuinely independent of the main checkout.

## QA
### Impediments & Unclear Points
- `[context]` The primary checkout was already on the story branch when I was spawned (not `main`, as the session's initial git-status snapshot suggested), with a reviewer's own uncommitted retro edits sitting in the working tree. Nothing in my instructions said to expect a non-`main` starting branch, so I spent a `git worktree add` cycle before realizing the primary tree already matched the PR head. Not harmful (used `--detach`, cleaned up after), just unbudgeted.

### Process Suggestions
- `[failure]` None beyond the two environment quirks now recorded as `QA_Memory.md` Troubleshooting Facts 1–2 (MSYS colon-path mangling on `git show ref:path`; `python3` resolving to a broken Windows Store stub instead of the real interpreter) — both are platform-level, not story-specific, so kept out of this retro's signal bullets per the privacy/scope rule.

### What Worked Well
- Rehearsing the stamp and bump-forward jobs *chained* (job 2 run against job 1's actual output, not a fresh copy of the original files) caught the same newest-first/`json.load`-clean guarantees TL reported, and additionally exercised TS-07's empty-section counterfactual against the real section `post-release` opens — reusing the Dev/TL scratch-rehearsal methodology end to end was sufficient to validate a job that literally cannot be run.
- `git show <ref>:<path>` (rather than `git worktree checkout` + `cat`) for pulling exact blob bytes made the CRLF-vs-blob distinction (`QA_Memory.md` Fact 3) a one-command check instead of a checkout-and-compare.

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
