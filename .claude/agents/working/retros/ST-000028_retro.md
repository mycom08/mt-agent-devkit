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
