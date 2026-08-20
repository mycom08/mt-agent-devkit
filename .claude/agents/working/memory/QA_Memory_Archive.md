# QA Memory Archive

> Full-text archive for `QA_Memory.md`'s Keyword Index tier — devkit-internal two-tier memory pilot (`Agent_Common.md §12`, issue #118). Not read every spawn; open only when an index line's keywords match your current task, using the `read-section` skill (`.claude/skills/read-section/`, heading marker `^### Fact `) — never a full-file read.

## Stored Facts

### Fact 1
- **Rule:** The full automation suite for this devkit (no runtime, no API) is `python scripts/validate_templates.py` (corpus invariant check) + `bash scripts/test/run.sh` (fixture self-test). Both must exit 0. `docs/Template_Test_Strategy.md` is the canonical *why/how* — 3-layer model, 6 invariant specs, risk tiers A/B/C, AC-as-oracle pattern.
- **Applies when:** validating any template or workflow change.
- **Evidence:** wired into `QA_Rules §8/§9` and `Project_Priming §8`.
- **Expires when:** a Layer-2/3 gate lands and changes the required command set.

### Fact 2
- **Rule:** Run the Layer-1 gate against a PR branch via `git worktree add <scratch> origin/<branch>`, then `git worktree remove <scratch> --force` — **always**, even when the primary tree is already checked out to the dev branch. Never run directly against the primary working tree: gitignored runtime files left on disk from prior sessions (e.g. `working-record/*.md`) are read by `_resolve_file_ref`'s repo-verbatim root and can silently shift the `[ERROR]` count depending on which directory the command runs from — independent of any PR change. For a differential base-vs-head comparison, run **both** sides from matched worktrees so neither side is polluted. Corrected: 2026-07-30 (ST-000035) — removed the "if already on dev branch, run directly" carve-out; that shortcut produced a wrong baseline (53 vs. the true 67 `[ERROR]` lines) in this story.
- **Applies when:** testing a PR branch, especially any differential (base-vs-head) validator comparison.
- **Evidence:** standing technique; ST-000035 PR #103 (methodology correction).
- **Expires when:** never.

### Fact 3
- **Rule:** A `git worktree` checkout may materialize CRLF while the primary tree is LF, producing spurious whole-file diffs. Before treating any such diff as a regression, normalize with `diff <(tr -d '\r' < A) <(tr -d '\r' < B)` and confirm the delta collapses.
- **Applies when:** any `diff -rq` across a worktree boundary.
- **Evidence:** ST-000028.
- **Expires when:** repo-wide `.gitattributes` normalization lands.

### Fact 4
- **Rule:** For a `Type: behavioral` story that touches `scaffold_mechanical.sh`, the regression check must include a two-mode scratch scaffold diffed against `origin/main` — not just the Layer-1 script pair. `validate_templates.py` only validates the devkit's own template tree, never scaffolded output, so it cannot catch a file-count or deployed-content regression from a hardcoded-array edit. Technique: run `scaffold_mechanical.sh <devkit_root> <scratch> github|strict` from the PR branch into two scratch dirs, repeat from an `origin/main` worktree, then `diff -rq`.
- **Applies when:** any change to `scaffold_mechanical.sh` or the workflow/rules template set.
- **Evidence:** ST-000028.
- **Expires when:** a Layer-2 deployment gate automates this.

### Fact 5
- **Rule:** For an injected `templates/**` file referencing a devkit-only path, verify the fix with one grep — `grep -n "agents/working/\|Build_Software_Workflow\|<script-name>"` across the changed file. A clean fix leaves at most an explanatory sentence, never a literal invocation or "follow file X" pointer. This is a QA-side grep; the automated gate cannot cover it (the validator's reference regex is `.md`-only and resolves against the devkit root, where devkit-only paths resolve clean).
- **Applies when:** verifying a fix to the devkit-only-path defect class.
- **Evidence:** ST-000028.
- **Expires when:** the validator gains deployment-scoped resolution.

### Fact 6
- **Rule:** When a PR claims a bullet or rule is "untouched", verify with `git diff main origin/<branch> -- <file>` scoped to that bullet's text and confirm it appears only as context with zero `+`/`-` lines. Never infer "untouched" from the absence of a hunk elsewhere, or from the reviewer's summary.
- **Applies when:** a review verdict rests on something not having changed.
- **Evidence:** ST-000025, ST-000026 precedent.
- **Expires when:** never.

### Fact 7
- **Rule:** For any AC whose correctness mechanism is a `gh`/CLI query (idempotency, dedup, filters), hand-construct at least one adversarial input — e.g. a prefix-title case against an exact-line-match idempotency key — rather than only re-reading the fix's prose.
- **Applies when:** validating a CLI-as-correctness-mechanism story.
- **Evidence:** ST-000026.
- **Expires when:** never.

### Fact 8
- **Rule:** For additive-only PRs (scripts/docs/CI only), the regression check is confirming `git diff main..HEAD --name-only` contains nothing under `.claude/agents/templates/` or `.claude/agents/workflows/`.
- **Applies when:** scoping regression effort on a non-template PR.
- **Evidence:** standing convention.
- **Expires when:** never.

### Fact 9
- **Rule:** `validate_templates.py` emits `[KNOWN_ISSUE]` (not `[ERROR]`) for the `Blocked_Request_Template.md` capital-T typo in two shared workflow files. Expected — does not block CI or QA sign-off. Invariant #4's fixture needs `--test-retired-trigger TEST_RETIRED_TRIGGER_DO_NOT_USE` because `RETIRED_TRIGGERS` is empty in production; invariant #5 has no standalone bad fixture and is validated against the full corpus.
- **Applies when:** interpreting validator output or its fixture suite.
- **Evidence:** ST-000016 / PR #34.
- **Expires when:** the typo is fixed or the fixture design changes.

### Fact 10
- **Rule:** For any AC whose correctness claim rests on a described-but-not-visibly-implemented runtime mechanism (e.g. "files logged by an earlier stage," "the scope computed at runtime"), locate the actual pre-existing rule/instruction text the claim depends on before accepting the scope as real — do not accept the prose describing the mechanism as sufficient evidence the mechanism exists.
- **Applies when:** an AC's scope or exclusion list is defined in terms of a log, state, or computed set rather than a static file list.
- **Evidence:** ST-000037 (Stage 4 audit-pass scope traced to Stage 2's written-files log + "Log every file written" + "Checksum skip is silent" rules, all pre-existing).
- **Expires when:** never.
