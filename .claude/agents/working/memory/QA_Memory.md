# QA Memory

> Two-tier memory (devkit-internal pilot, `Agent_Common_Read_On_Demand.md §8`, issue #118). This is the lean, always-read index — titles and grep-able keywords only, no fact bodies. Full text lives in `QA_Memory_Archive.md`. Before starting a task, scan the titles/keywords below for a match; if one matches, retrieve just that fact per §8's bounded-read recipe — never read the whole archive.

## Standing Checks

*(none yet — no current fact reduces to an unconditional always-do action; entries move here if a future fact qualifies)*

## Keyword Index

### Fact 1 — The full devkit automation suite (no runtime, no API)
Keywords: `python scripts/validate_templates.py`, `bash scripts/test/run.sh`, corpus invariant check, fixture self-test, `docs/Template_Test_Strategy.md`, 6 invariants, risk tiers A/B/C, AC-as-oracle

### Fact 2 — Always run the Layer-1 gate from a matched `git worktree`, never the primary tree
Keywords: `git worktree add`, `git worktree remove --force`, differential base-vs-head, gitignored runtime files, `working-record/*.md`, `_resolve_file_ref`, polluted baseline

### Fact 3 — Worktree checkouts may materialize CRLF vs. a primary LF tree
Keywords: `git worktree`, CRLF, LF, spurious whole-file diff, `diff -rq`, `tr -d '\r'`, `.gitattributes`

### Fact 4 — `scaffold_mechanical.sh` changes need a two-mode scratch-scaffold diff, not just the script pair
Keywords: `scaffold_mechanical.sh`, `Type: behavioral`, scratch scaffold, github, strict, `diff -rq`, `origin/main` worktree, deployment regression

### Fact 5 — One-grep verification for the devkit-only-path defect class
Keywords: `templates/**`, devkit-only path, `grep -n "agents/working/\|Build_Software_Workflow"`, clean fix, QA-side check

### Fact 6 — Verify "untouched" claims with a scoped `git diff`, never infer from absence
Keywords: `git diff main origin/<branch>`, untouched bullet, zero `+`/`-` lines, review verdict

### Fact 7 — Hand-construct an adversarial input for any CLI-as-correctness-mechanism AC
Keywords: `gh` query, idempotency, dedup, filters, adversarial input, prefix-title case, exact-line-match

### Fact 8 — Regression scope for additive-only PRs
Keywords: `git diff main..HEAD --name-only`, additive-only, `.claude/agents/templates/`, `.claude/agents/workflows/`, non-template PR

### Fact 9 — `validate_templates.py` `[KNOWN_ISSUE]` vs `[ERROR]`, and fixture flags
Keywords: `[KNOWN_ISSUE]`, `Blocked_Request_Template.md`, capital-T typo, `--test-retired-trigger`, `RETIRED_TRIGGERS`, Invariant #4, Invariant #5

### Fact 10 — Locate the real mechanism behind a "described but not visibly implemented" AC claim
Keywords: runtime mechanism, files logged by an earlier stage, computed at runtime, pre-existing rule/instruction text, unverified claim

## Troubleshooting Facts

No troubleshooting facts recorded yet.
