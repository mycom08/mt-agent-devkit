# Retrospective — ST-000028
**Date:** 2026-07-28
**Story:** New workflow: UI/UX Refine — direct orchestrator/user prototype iteration loop

## Implementer — Developer
### Impediments & Unclear Points
- None blocking. The pre-flight design review (this session's own earlier round, comments `5099613122`/`5099644762`/`5099680121`/`5099690439` on issue #84) had already resolved the three genuinely architectural questions (repo-creation convention scope, state-file location, drafted-story destination repo) before implementation started, so no mid-implementation consultation was needed.
- The "8th split workflow" ripple was larger than the AC text implied: adding one new template file required touching workflow-file-count prose/lists in 6 separate places (`scaffold_mechanical.sh`'s `SPLIT_WORKFLOWS` array, `Init_Project_Workflow.md` ×5 occurrences, `Update_Project_Workflow.md` ×2 lists, `Sync_Devkit_Workflow_template.md` ×3 spots, its working mirror ×2, `Build_Software_Workflow.md` ×2) — none of these were named in the story's AC/Technical Scope; found them only by grepping existing enumerations of `Refine_Sprint_Workflow` before starting, per the pattern already flagged in Developer Memory for rules-file additions.
- Confirmed empirically (dry-run of `scaffold_mechanical.sh` against a scratch target) that a thin-variant file's comment-only lines are devkit-maintainer notes only and are never injected into the deployed target-project file — the mode differentiation has to live inline in the shared file's own "**GitHub mode:**/**Strict mode:**" bullets. This wasn't stated anywhere in prose; only visible by reading the script's awk-filter logic and reproducing it. Worth stating explicitly in `Init_Project_Workflow.md`'s Stage 2 "Split candidates" section for the next implementer who adds a split workflow.

### Process Suggestions
- Add a line to `Project_Priming.md §15` or `Developer_Memory.md` generalizing the rules-file-count ripple note to workflow files too: "adding an Nth split workflow file touches `scaffold_mechanical.sh`'s `SPLIT_WORKFLOWS` array plus every workflow-file-count enumeration in `Init_Project_Workflow.md`/`Update_Project_Workflow.md`/`Sync_Devkit_Workflow_template.md`(+mirror)/`Build_Software_Workflow.md` — grep `Refine_Sprint_Workflow` across `.claude/agents/` before starting a similar story." Recorded this fact in Developer Memory this session.

### What Worked Well
- The prior TL/PO decision comments on issue #84 were specific enough (exact repo-creation steps, exact state-file rationale, exact drafted-story destination) that implementation required zero interpretation or guessing — a clean example of design-first paying off.
- Dry-running `scaffold_mechanical.sh` against a scratch target before opening the PR caught the thin-variant-appendix behavior above cheaply, without needing to inspect a real target-project scaffold.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- `[failure]` A workflow file that is *injected into another project* was written with executable references to files that exist only in the originating toolkit — a script path under a maintainer-only directory, plus "follow file X exactly" pointing at a file the receiving project never gets. Both read as correct while editing, because the author's own working tree contains them. This is a distinct failure mode from a stale reference: the target exists, just not where the file will run. Evidence: PR review comment CR-1/CR-2.
- `[failure]` Automated corpus validation gave false assurance here. The reference-integrity check resolves candidate paths against the **toolkit repo root**, so a toolkit-only path inside an injected template resolves clean, and its regex covers `.md` only, so script paths are never examined at all. A green validator run says nothing about whether an injected template's references resolve in a receiving project. Reinforces the same-shaped lesson recorded for path-move stories (TL memory, ST-000015).
- `[workflow]` A new pipeline-state file specified a terminal status value and a "delete only after the final step" write rule, but the resume rule enumerated branches for only the non-terminal values. The interrupted-window the write rule explicitly anticipates had no routing. Third story running where a resume rule's branch set lagged the states its own write rules create.

### Process Suggestions
- `[workflow]` Add a review-checklist line for template/workflow stories: for any file that is deployed into another project, verify every executable path and "read file X" pointer against the *deployed* file inventory, not the authoring repo's tree. The deployed inventory is already enumerated in the sync/update workflows' "Expected files" lists — that list is the authority, and checking against it is a two-minute grep.
- `[workflow]` Extend the corpus validator with an invariant scoped to injected templates only: no reference to a path outside the deployed inventory, and widen the reference regex beyond `.md` to cover script extensions. Both blocking findings this round would have been caught mechanically.
- `[workflow]` When a story's technical scope says design-first, a pre-flight Q&A that resolved the *architectural* questions is not a substitute for the design draft. The questions answered up front were about placement and ownership; the defects landed in mechanics — "in the receiving project, what actually executes this step?" — which is exactly what a draft surfaces before a file is written.

### What Worked Well
- Reproducing the scaffold from both the PR branch and the base branch into scratch targets, then diffing the outputs, converted three separate claims into evidence in one step: no regression to the existing workflows, correct file count in both modes, and — unexpectedly — proof that mode-specific thin-variant comments are stripped before deployment, which is precisely why the mode branching had to live in the shared file for the mode-dependent AC to hold at all.
- Re-deriving the count ripple independently (grepping for the *stale* phrasings rather than confirming the listed locations) turned "did they get all 6?" into a zero-hit result that needs no trust in the enumeration. Reinforces: TL memory, ST-000026 — an enumerated list in a change request invites being treated as exhaustive; the same applies to an enumerated list in a completion claim.
- Checking cross-referenced section numbers by resolving each one to its actual heading, not by pattern-matching the citation, held up: all five resolved. Direct application of the §-citation lesson from the previous story.

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
