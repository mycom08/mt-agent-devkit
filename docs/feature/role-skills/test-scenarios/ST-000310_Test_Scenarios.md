# ST-000310 Test Scenarios — Developer and common skills distribution

**Story:** ST-000310 (issue 310, PR 318) · **Validated head:** `5e3c49df873983006eb36fa45c4d25b02b48c9d3` (TL Approved-SHA) · **Base:** `56b7474`
**Type:** behavioral · **Layout:** internal (target output exercised by real installs) · **Mode:** github

## Happy path

| # | Scenario | Method | Expected |
|---|---|---|---|
| AC1 | Phase 2 skill templates for every common and Developer skill except `change-metadata`; canonical plus wrapper; `project-docs` omits `_template` rule | Compare `.mt-agent-devkit/skills/*` with `distribution/phase2/templates/skills/*`; grep `_template` in project-docs template; real installs per provider | Same set minus `change-metadata`; 34 canonical skills and a wrapper for each in the install; no `_template` rule |
| AC2 | Phase 2 generated blocks sourced only from Phase 2 skill templates; `generate_common_blocks.py --check` green | Run check; tamper a Phase 2 skill template (token-efficiency) and a byte-copy template (shell-rules) | Green clean; tamper makes check exit non-zero |
| AC3 | Each design §9 row has its text in the named skill template, with layer differences | Read §9 table; inspect pre-pr-gate, dev-verify, working-record, clean-code, project-docs templates | Check table with target commands; pre-merge items 1-6, no `status:done`; target-only endpoint and sandbox sections; per-project cap; Development Standard rules |
| AC4 | Target `common`, `bootstrap`, `role_sources` route Developer to skills; target Developer manifests resolve and validate for every task and trigger | Installed `read_manifest.py` from a fresh install per provider: build and validate every Developer task x (no trigger + every applicable trigger); `test_read_manifest.py` | All build and validate; no old Developer rules, Common or `change-metadata` read; every read exists in the install |
| AC5 | Old Developer templates stay in bundle, unused | Inspect bundle `deployment.json`; installed target; frozen corpus diff | Developer_Rules_*, Story_Standard_Dev, Clean_Code_Rules still shipped; `.claude/agents/templates` diff vs base is empty |
| AC6 | Bundle regenerated; `build_bundle.py --check` green; canonical+wrapper check covers bundle; fresh install per provider receives skills | `build_bundle.py --check`; remove a wrapper from `deployment.json`, run `validate_internal_harness.py`; `lifecycle.py init --apply` + `deployment.py verify` for claude, antigravity, codex into scratch targets; `test_phase2_deployment.py` | Check green; removal reported as an error; each install verifies, holds skills and only its own provider's wrappers, no `change-metadata` |
| AC7 | All gates | Run each on the head worktree | All exit 0 |

## Error and edge cases

- Missing bundle wrapper is detected (validator error `bundle lacks provider skill wrapper`).
- Generated block drift from a Phase 2 skill template is detected by `--check`.
- `change-metadata` must not appear in the bundle or in any install.
- Non-Developer target manifests are unchanged (covered by `test_read_manifest.py`).
- Strict mode and other providers covered by `test_read_manifest.py` all-provider-mode matrix and `test_phase2_deployment.py`.
