# Developer Memory

> Two-tier memory (devkit-internal pilot, `Agent_Common.md §12`, issue #118). This is the lean, always-read index — titles and grep-able keywords only, no fact bodies. Full text lives in `Developer_Memory_Archive.md`. Before starting a task, scan the titles/keywords below for a match; if one matches, retrieve just that fact per §12's bounded-read recipe — never read the whole archive.

## Standing Checks

*(none yet — no current fact reduces to an unconditional always-do action; entries move here if a future fact qualifies)*

## Keyword Index

### Fact 1 — Nth-item ripple into hardcoded counts/lists
Keywords: enumerated corpus, hardcoded count, Nth role, Nth rules file, Nth split workflow, `scaffold_mechanical.sh`, `SPLIT_WORKFLOWS`, `Init_Project_Workflow.md`, `Update_Project_Workflow.md`, `Build_Software_Workflow.md`, `Sync_Devkit_Workflow_template.md`, ripple

### Fact 2 — Templates must never reference devkit-only paths as executable steps
Keywords: `templates/`, devkit-only path, `.claude/agents/working/scripts`, `Build_Software_Workflow.md`, `{DEVKIT_SOURCE_URL}`, `Sync_Devkit_Workflow_template.md`, WebFetch, curl fallback

### Fact 3 — Thin mode variants are comment-only; github/strict deploy byte-identical files
Keywords: `scaffold_mechanical.sh`, awk merge, thin variant, github mode, strict mode, mode-specific behavior, split workflow

### Fact 4 — Every resume-state value needs its own explicit branch
Keywords: state file, resume, pipeline loop, terminal value, `ended`, `done`, `refine_prototype_state.md`, fall-through, active branch

### Fact 5 — `validate_templates.py` internals (Layer-1 invariant checker)
Keywords: `validate_templates.py`, `RETIRED_TRIGGERS`, `--test-retired-trigger`, `_is_shared`, `_is_thin_variant`, `path.parts`, `RUNTIME_PATH_PREFIXES`, `working-record/`, `tmp/`, `docs/`, `retros/`

### Fact 6 — `changes.json` is newest-first; add new entries at the top
Keywords: `changes.json`, version entry, newest-first, descending order, semver

### Fact 7 — GitHub Actions workflow needs a push trigger on `ci-validation`
Keywords: `validate-templates.yml`, `on.push.branches`, `ci-validation`, `pull_request` paths, `CICD_Validation_Guide`, workflow trigger

### Fact 8 — Vague once-per-sprint scheduling AC → Sprint Workflow's "Sprint end" sequence
Keywords: once-per-sprint, `Sprint_Workflow_Shared_template.md`, Sprint end, Batch Retro Review, Consolidated Summary, Devkit Contribution, Cleanup, Memory Pruning, `Retro_Rules.md`

### Fact 9 — `Story_Standard` rules restated in 6 places, not 5 (Strict Mode guide is the miss)
Keywords: `Story_Standard_template.md`, `Story_Standard_Dev/PO/QA/TL_template.md`, `Strict_Mode_Story_Guide_template.md`, restatement drift, no working mirror

### Fact 10 — Before hardening a principle to an absolute, grep for a rule that mandates the forbidden act
Keywords: never, always, must not, gate checklist, named carve-out, `Story_Standard_template.md §9`, `§12`, override, absolute vs principle

### Fact 11 — Splitting a shared devkit config file ripples 3 ways beyond the split itself
Keywords: sync/update workflow expected-files list, merge-tier check, project-mutable section, mechanical file, remote fetch, `{DEVKIT_SOURCE_URL}`, `scaffold_mechanical.sh`, `Refine_Prototype_Workflow`, `.claude/skills`

### Fact 12 — Inline ALL-CAPS shell variable in prose trips the validator's placeholder check
Keywords: `validate_templates.py` Invariant #2, single-backtick code span, `${START}`, placeholder false positive, lowercase shell variable

### Fact 13 — Flat `## Na.` is the live convention; SKILL.md's `### Na` example is stale
Keywords: flat heading convention, `## N.`, `## Na.`, `### Na` stale, `read-section` SKILL.md, over-read, whole numbered family, `Product_Owner_Rules.md`, `Project_Priming.md §15a`, section boundary scan

## Troubleshooting Facts

### Fix 1 — Working-record refs fail CI reference-integrity
- **Problem:** Reference-integrity check fails in CI but passes locally.
- **Symptoms:** `[ERROR]` on `.claude/agents/working-record/…` paths cited in instruction templates.
- **Root Cause:** Those files are gitignored in the devkit, so the CI runner never checks them out and Root-2 resolution fails.
- **Fix:** Add `.claude/agents/working-record/` to `RUNTIME_PATH_PREFIXES` in `validate_templates.py`.
- **Prevention:** Any path that is gitignored or generated at runtime belongs in `RUNTIME_PATH_PREFIXES` before it is cited in a template. Not reproducible locally — only surfaces on a real CI run.
