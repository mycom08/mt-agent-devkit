# Retrospective — ST-000144
**Date:** 2026-09-03
**Story:** [ST-000144][DEVKIT] No rule forces production-build verification for build-dependent behaviour

## Implementer — Developer
### Impediments & Unclear Points
- `[workflow]` Implementation spanned two sessions with the first session's context lost, and the bookkeeping half of the story (version bump + change-manifest entry) was the part left undone — the resumed session had to re-derive the whole story state from the branch diff before it could tell which AC were already satisfied. A rule-text change lands in one commit and reads as "done" even when its release bookkeeping has not started.
- `[failure]` The rule-text commit alone left two of the story's own AC unmet with a green validator and a clean working tree — no local signal distinguished "rule written" from "story finished". The validator checks corpus invariants, not story completeness.

### Process Suggestions
- `[workflow]` Where a story's AC include release-bookkeeping steps (version bump, change manifest, changelog), do them in the **same** commit as the content change rather than a follow-up commit — the two-commit habit is exactly what a lost session drops on the floor.
- `[failure]` A mid-story handoff should carry the AC checklist state explicitly, not just the branch name — a resumed implementer's cheapest correct move is re-reading the issue AC one by one against the diff, and that should be the stated first step, not an inference.

### What Worked Well
- The mandatory issue re-read caught that the content AC were genuinely satisfied by the prior session's commit, so no rule text was rewritten needlessly — the resume cost was bookkeeping only.
- The template-update procedure's explicit ordering (edit template → bump `version.txt` → prepend the newest-first manifest entry) made the remaining work mechanical; the newest-first ordering rule is not validator-enforced, so having it stated in the procedure is what prevented a silent mis-insert.
- The stub/TODO scan over the changed files returned only documented convention placeholders (`ST-XXXXXX` story-ID forms), confirming no incomplete work shipped.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- `[failure]` The PR's only required check never ran. `[skip ci]` on the head commit `0dcb2be` suppressed `validate-templates.yml`, whose `pull_request` path filter (`.claude/agents/templates/**`) this PR matches — so `statusCheckRollup` was empty and the reviewer CI gate had nothing to read. The review had to substitute a local run at the exact head SHA for the missing CI evidence.
- `[rules]` `Developer_Rules_Bootstrap` §6 permits `[skip ci]` when every file in the push is `*.md`, but `.claude/agents/templates/**` is simultaneously all-`*.md` **and** the CI path filter. The rule and the workflow contradict each other for this repo's single most common change class. Pre-existing, not caused by ST-000144.
- `[workflow]` The branch carried a merge of `main` (`4a8f878`) bringing unrelated pipeline changes into the diff. Reviewable only because the PR description and the spawn prompt both named the in-scope commits explicitly; a bare `gh pr diff` would have mixed them in.

### Process Suggestions
- `[rules]` File a story to reconcile §6's `[skip ci]` condition with `validate-templates.yml`'s path filter — the exclusion should be by CI path filter, not by file extension. Until then, a reviewer should treat an empty `statusCheckRollup` on a `templates/**` PR as "check suppressed", not "check passed", and reproduce the gate locally at the exact head SHA before approving.
- `[review]` When a branch contains a merge of `main`, review `git show <sha>` per in-scope commit rather than `gh pr diff` — and expect the PR description to name the in-scope commits, as this one did.
- `[review]` Cross-check a suspected bookkeeping nit against the file's own history before writing it up. The 0.1.47 CHANGELOG bullet sits under `[Unreleased]` with no `## 0.1.47` heading, which reads as an omission — a two-line script comparing `changes.json` keys against CHANGELOG headings showed 20+ prior versions do the same, so it is the convention and not a finding. Cost less than the fix round a false CR would have caused.

### What Worked Well
- Verifying the three copies by extracting the rule blocks from each file and diffing the two mirrors against **their own state on `main`** separated real drift from the pre-existing `.claude`/`.antigravity` path substitutions cleanly — the 7-line delta was identical on both sides, so no drift was introduced (Memory Fact 11 applied as intended).
- Framework-neutrality was checkable mechanically rather than by judgement: the added text contains no tool/framework name and, notably, no new `{placeholder}` token — so it needed no `validate_templates.py` allowlist registration, which is the failure mode a placeholder-bearing template change usually hits.
- The implementer's PR evidence named which verification path it took ("individual gate — no aggregate entry point exists") — i.e. the story's own new rule was already being obeyed by the PR that introduced it, which made the evidence line self-verifying.
- Non-blocking nits were stated as fold-in-later items with that framing explicit, so an approval did not turn into an implied fix round.

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
