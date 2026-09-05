# Retrospective — ST-000148
**Date:** 2026-09-04
**Story:** Remove manual version bumping from the agent corpus

## Implementer — Developer
### Impediments & Unclear Points
- `[workflow]` A "remove instruction X from the corpus" story is a classification task, not a replace task: a repo-wide grep for the retired term returned hits in four distinct classes — live instructions to fix, deliberate carve-outs to keep, historical records to leave alone, and same-named-but-unrelated artifacts (a derived per-install stamp file whose name contained the retired term as a substring). Blanket replacement would have corrupted three of the four. The substring collision then bit a second time in the *other* direction: filtering that unrelated artifact out of the grep with a `grep -v` on its name also hid three real read sites, because the line that reads the retired file is the same line that writes the stamp. Exclude by classification per hit, never by a pattern that can also match a hit you need. The AC named the removal but not the classification, so the taxonomy had to be derived first.
- `[context]` Removing an instruction leaves a functional residue the AC does not cover: several workflows still *read* the retired file to derive a value, which is not the banned hand-edit but is now stale. That residue is invisible to a grep for the banned phrasing and only surfaces by asking, per hit, "is this still true?" Raised as a consultation rather than fixed in scope.
- `[failure]` Reinforces the existing `[skip ci]`-keys-on-the-path-filter rule, which is bootstrap-tier, was read this session, and was still missed. The rule is stated per *push*, but what actually decides suppression is the **PR head commit's message**: a bookkeeping commit carrying `[skip ci]` emptied the whole PR's rollup even though its own files sit outside the filter. Suggest restating the rule at head-commit level rather than per-push.
- `[failure]` Diagnosing a CI gap by inference rather than by test produced a confidently-stated wrong mechanism. From two observations of an empty rollup I concluded there was also a commit-*ordering* hazard — that a new head SHA re-evaluates the `paths:` filter against the pushed commit, so a bookkeeping commit landing last drops the run. The reviewer tested it directly and it is false: a `pull_request` `paths:` filter is evaluated against the PR's whole changed-file set, and the retro-only push produced a green run. The real cause of both observations was the skip token alone. The lesson is not about CI: a mechanism inferred from symptoms and never tested should be recorded as a hypothesis, not written into a retro as a finding, because retros feed the devkit improvement process and a wrong mechanism there becomes a wrong rule.

### Process Suggestions
- `[workflow]` When a story removes a scattered instruction, do the classification pass as an explicit first step and record the four-class split before editing anything — the count of grep hits is not the count of edits, and the ratio here was roughly one edit per three hits.
- `[workflow]` The one AC miss was a **restatement**, not an omission: a contributor-facing doc spelled out the same procedure as the workflow file instead of pointing at it, so rewriting the workflow left a second live copy telling agents the opposite. Duplicated procedure is the defect; the drift is only the symptom. Suggest that any story rewriting a procedure grep for prose that *restates* it, not only for the retired term, and resolve each duplicate by making it a pointer.
- `[failure]` Mirrored-corpus edits are safer applied mechanically than by hand: diffing the primary file against its committed parent and replaying the hunks into the mirror, matching on path-normalised context, caught the mirror's own path-prefix divergences that a hand-repeated edit set would have flattened. Verified by re-normalising both diffs and asserting equality — worth making the standard technique for any dual-surface change.

### What Worked Well
- The dual-update + drift-check rule in the template-update procedure paid off directly: the TL rules file turned out to have no template counterpart at all, and the "no working mirror exists" carve-out meant that was a recognised state rather than a suspected miss.
- Running the corpus validator against the branch *and* against a stashed baseline, and comparing counts rather than reading the output, cleanly separated pre-existing findings from zero regressions in about one tool call. The absolute count is environment-dependent (160 here, 169 on the reviewer's machine) — only the base-vs-head differential is evidence, and reporting the raw count risks it being read as a verdict.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- `[workflow]` A "remove instruction X" story's grep scope was implicitly the agent corpus, but the one live residue sat in a **contributor-facing README** that restates a maintainer workflow's steps rather than pointing at it. Duplicated procedure outside the agent directories is invisible to a corpus-shaped search and to the dual-update/mirror rules, yet it is read by the same agent running that workflow.
- `[context]` Freezing a file that other workflows *read* can invert an equality comparison into a permanent no-op: an update path that stops when installed version equals source version goes inert once the source is pinned. The residue is not the stale value but the comparison built on it — a class the "removed instruction" AC has no reason to look at.
- `[failure]` The retro's existing `[skip ci]`/path-filter finding is **partly wrong and was tested rather than inherited**: a bookkeeping-only commit whose own files sit outside the CI path filter still produced a run and a green rollup at the new head. The hosted CI evaluates a pull-request path filter against the PR's whole changed-file set, not the pushed commit's — so the only mechanism that empties the rollup here is the skip-CI token in the head commit message. A reviewer inheriting the implementer's stated cause would have drawn the wrong conclusion about their own commit.
- `[review]` (round 2) A change request that names a **count** of call sites without naming the tree it counted invites a disagreement that looks like an under-delivered fix. Round 1 said "the 4th read site"; the fix commit said it had covered three. Both were right against different denominators — a dual-surface corpus where one mirror carries a `.ps1` the other has never had. Re-deriving the inventory from scratch settled it in one grep, but the round-1 CR should have stated the tree, not just the ordinal.
- `[review]` (round 2) The fix round shipped with **no PR fix-round comment** — the commit message was the entire account of what changed and why. It was recoverable here because the delta was small and legible, but it forced the reviewer to reconstruct the CR-to-hunk mapping that the implementer already had. That reconstruction is exactly the cost the fix-round comment exists to remove.

### Process Suggestions
- `[workflow]` Add a "duplicated-procedure sweep" to removal-story review: after the corpus edits, grep the retired instruction's *verb* across the whole repo including READMEs and contributor docs, not just the agent directories. Better still, treat a doc that restates a workflow's steps as a defect in its own right and replace it with a pointer.
- `[workflow]` When a mitigation is "a note at each read site", enumerate the read sites from the grep and check the note count against it — the executable site was the one missed here. Enumerate by **path**, never by count: state which files were counted, because a mirrored corpus can hold a file in one tree and not the other, and a bare ordinal ("the 4th site") then means different things to reviewer and implementer.
- `[review]` (round 2) A fix round is not exempt from the fix-round PR comment just because its commit message is descriptive. Prefer the comment; it is where the CR → hunk mapping and the "why this option over the other" belong.
- `[failure]` Correct the skip-CI rule to key on the **head commit's message token**, not on which files a push touched: a pull-request path filter is evaluated against the PR's whole changed-file set, so the "land bookkeeping first / re-touch a filtered file last" ordering advice is unnecessary and misdiagnoses the cause. Reviewers should verify a rollup claim against the run list at the head SHA rather than reasoning from the filter.

### What Worked Well
- The differential-validator discipline (same explicit-path command on base and head in parallel worktrees, line numbers stripped, sorted output diffed) separated 169 pre-existing findings from zero regressions in one comparison and made the "explicit paths produce errors on a clean tree" observation a non-event rather than an investigation.
- Checking mirror parity on the *version-bearing lines only*, path-normalised, rather than on whole files, isolated this PR's edits from the mirror's known pre-existing drift without needing to adjudicate that drift.
- The implementer raising the out-of-scope residue as an explicit consultation, with a stated decision and rationale, made the scope verdict a confirmation rather than a re-derivation — and surfaced the inert-`update project` consequence that neither the AC nor the grep would have.
- (round 2) The implementer resolved the blocking finding by **deleting the duplicated procedure and pointing at its source**, rather than correcting the copy — the option that removes the drift mechanism instead of the current instance of the drift. Offering both options in the CR and letting the implementer pick the structural one worked better than prescribing the minimal edit.
- (round 2) Re-deriving the read-site inventory from the branch tree rather than reconciling the two stated counts turned a potential fix-round dispute into a one-grep non-event, and incidentally documented a pre-existing `.claude`/`.antigravity` script asymmetry that neither round had named.

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
- [orchestrator] Story entered at `status:backlog`, which `Start_Story_Workflow.md`'s Stage Entry Check has no row for; promoted to `status:ready` by hand. Same undocumented step recorded as a retro finding in ST-000146 and skipped at that retro.
- [Developer] `[skip ci]` guidance in `Developer_Rules_Bootstrap.md §6` is stated per push, but suppression is decided by the PR head commit; a bookkeeping commit landing on top of filtered content emptied the rollup.
- [Developer] The same shape bit from the opposite direction: a bookkeeping push without `[skip ci]` also emptied the rollup, because a new head SHA re-evaluates the path filter and check runs attach to a SHA. The durable fix is ordering, not phrasing.
- [Developer] `validate_templates.py` with explicit path arguments reports 160 errors on a clean `main` here, while CI's bare invocation exits 0; `Audit_Agent_Files_Workflow.md` tells agents to use the explicit-path form.
- [Developer] "Remove instruction X from the corpus" stories need an explicit classification step in the AC, not just a grep instruction — the hit count was ~3x the edit count and three of four hit classes would be corrupted by a blanket replace.
- [Technical Lead] AC 7 said "the corpus", but the one real miss lives in a contributor-facing README outside the agent directories; corpus-shaped searches and the mirror rules both structurally exclude it.
- [Technical Lead] `community-retros/README.md` restates `Apply_Retros_Workflow.md` Stage 5 rather than pointing at it; the duplication is the real defect and will re-break on the next release-process change.
- [Technical Lead] A "note at each read site" mitigation should be verified by counting notes against the grep's site list — 3 of 4 got one, and the miss was the shell script.
- [Technical Lead] Two consecutive PRs have spent reviewer effort adjudicating empty-vs-populated check rollups on partly-wrong folk theories; the real mechanism (head-commit skip token, PR-wide path filter) deserves one authoritative line in the rules.
- [orchestrator] TL disproved the Developer's commit-ordering theory by experiment: a `pull_request` `paths:` filter is evaluated against the PR's whole changed-file set, not the pushed commit, so only a skip token in the head commit message empties the rollup.
- [orchestrator] The story was resumed in a fresh session with the Stage 2 loop-back never executed: the Developer pushed its fix commit but its session ended before it posted a fix-round PR comment or handed back, leaving an approved-looking branch stuck at `status:review`. Nothing in the state file distinguishes "reviewer not yet resumed" from "reviewer running".
- [orchestrator] The pipeline state file lives at `.claude/agents/working/tmp/`, but `orchestrator_instructions.md`'s Build Software section names `.claude/agents/tmp/` for its own state file; checking the wrong one first reads as a missing state file and invites a needless rebuild.
- [Technical Lead] The fix round landed with no PR fix-round comment, forcing the reviewer to reconstruct the CR-to-hunk mapping from the commit message alone.
- [Technical Lead] A review CR that names a call-site ordinal ("the 4th site") without naming the tree it was counted in reads as an under-delivered fix in a dual-surface corpus; round 1's "4th site" and the fix commit's "three sites" were both correct against different trees (`scaffold_mechanical.ps1` exists only under `.antigravity/`).
- [Technical Lead] PowerShell here-string syntax (`-m @'...'@`) used inside a Bash call silently produced a commit subject prefixed with a literal `@` — the `Agent_Common_Bootstrap.md §6` corruption class, in the opposite direction.
