# Retrospective — ST-000016
**Date:** 2026-06-30
**Story:** Establish template test strategy + Layer-1 validation tool & CI gate

## Implementer — Developer
### Impediments & Unclear Points
- The CICD_Validation_Guide requires `on.push.branches: [ci-validation]` but the CI gate is PR-triggered (`on: pull_request`). The guide's pre-merge validation procedure does not explicitly address PR-only workflows. Resolution: added the push trigger permanently to the workflow so ci-validation runs on push. A note in the guide about PR-only workflows would prevent this confusion in future stories.
- Working-record files (`.claude/agents/working-record/`) are gitignored in the devkit, causing the reference integrity check to fail in CI even though resolution works locally via Root 2. This was discovered only after the first ci-validation run (not catchable by local testing alone). Resolution: added the prefix to `RUNTIME_PATH_PREFIXES`. A note in `Developer_Rules.md` or the CICD guide about gitignored reference paths would help future devs.
- The three-root file resolution strategy (verbatim / working mirror / template source) produces correct results locally but requires CI-driven iteration to surface gitignored-path failures.

### Process Suggestions
- The CICD_Validation_Guide should document a "PR-triggered workflow" case: state that the push trigger for ci-validation must also be included so the guide's pre-merge validation flow works.
- For stories that add validators or CI gates, add a local "gitignore simulation" step to the AC or pre-PR gate: `git ls-files --others --exclude-standard` to surface files the CI runner won't have.

### What Worked Well
- Separating the 4 root-cause bug categories (single-brace regex, section-ref separator, heading-detection regex, version-ordering) before rewriting the validator kept the rewrite targeted and verifiable.
- The `--test-retired-trigger` flag is a clean pattern for testing empty-seed invariants without contaminating production constants.
- `_is_shared` / `_is_thin_variant` being path-part-based (not TEMPLATES_DIR-relative) allowed fixture files in `scripts/test/fixtures/bad/shared/` to trigger shared-block checks without duplication.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- `[workflow]` The AC said "one fixture per invariant class" but its own enumerated examples covered only a subset of invariants, and one global/manifest-level invariant cannot be isolated to a single per-file negative fixture under the tool's scan-target model. Required a reviewer judgement call to decide whether the missing fixture was a gap or an acceptable design limit. Story authors should distinguish per-file invariants from global invariants when specifying fixture coverage.
- `[context]` One sub-check's literal AC wording ("versions ascending") contradicted the actual data file convention (descending/newest-first). The authorised interpretation was already captured in the design-first comment, but only confirmable by re-reading that thread — the body AC text was never reconciled to it.

### Process Suggestions
- `[workflow]` When an AC specifies "one negative fixture per check," add a clause that global/aggregate checks (those that read a single shared manifest rather than scanning each file) are exempt or require a parameter-override to be testable — prevents a false "missing coverage" flag at review.
- `[instruction]` Reviewer rules already require updating the body AC when an interpretation narrows it; reinforce that design-first approval comments that supersede body wording should trigger a same-pass body-AC edit, so reviewers in later stages don't have to reconcile the two sources manually.

### What Worked Well
- Running the validator and the fixture self-test locally before approving confirmed the PR's captured outputs were reproducible — caught nothing wrong here, but is the right gate and gave high confidence.
- The design-first approval comment from the earlier session fully specified the invariant set (including the narrowed retired-trigger check), so review was a straight conformance check against an approved spec rather than a fresh design debate.
- The PR description transparently documented the invariant #5 fixture limitation rather than hiding it — made the reviewer judgement call fast and well-evidenced.

## QA
### Impediments & Unclear Points
- None.

### Process Suggestions
- `[workflow]` QA Rules §4 says "Always create a test scenario document first — do not begin testing without it," but the spawn prompt directed immediate execution. The pre-work rule and the orchestrator spawn sequence are in tension for tooling stories: consider adding a note that for execution-driven validation, the test scenario can be drafted in parallel with the first run rather than as a strict prerequisite gate.
- `[context]` For tooling stories where the "full automation suite" is the deliverable itself, the regression suite IS the new tool runs. The QA Rules §8 regression check guidance ("check `init project`, `sync devkit` behavior") could have a note for additive-only PRs: confirm no templates or workflows were modified (blast-radius check), then skip the behavioral walkthrough.

### What Worked Well
- Running the validator and fixture self-test by execution (not just reading) confirmed both the clean-pass result and that each invariant fires — exactly the right validation method for a tooling story.
- The `git diff main..HEAD --name-only` command provided an immediate blast-radius view: no templates or workflows in the diff, confirming zero regression risk in a single step.
- The known-issue allowlist pattern (`KNOWN_ISSUE_REFS`) is well-designed: it produces informational output without blocking CI, and the PR description disclosed the known issues transparently, making QA sign-off straightforward.

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
