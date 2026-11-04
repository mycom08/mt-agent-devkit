# ST-000311 Test Scenarios — Developer skills retirement: remove legacy Developer rules from targets

**Story:** ST-000311 (issue 311, PR 320) · **Validated head:** `fba9db06b59e681336dacb94bffb1ef2a8da7566` (TL Approved-SHA) · **Base:** `4e8464d`
**Type:** behavioral · **Layout:** target (Phase 2 bundle, sync) · **Mode:** github · **AC3 validated against the reworded body**

## Happy path

| # | Scenario | Method | Expected |
|---|---|---|---|
| AC1 | Four files retire through `RETIRED_RULES` with their own survivors; Phase 2 templates and assets deleted; inventory untouched | Read `build_bundle.py`; parse `deployment.json` retirements and survivors; `ls` templates and assets; `git diff` on `migration-inventory.json` | 7 retired names; each has 1 shared + 4 legacy entries, `required: false`; Developer survivors exist in the manifest; Clean_Code_Rules survives only `clean-code`; 4 templates and 4 assets gone; inventory diff empty |
| AC2 | Ownership rows removed, Sync lists updated, sample legacy file changed | grep the ownership JSON before and after; grep Sync templates; read `test_phase2_sync.py` diff | 0 retired-name rows left (98 matching lines before); Sync lists drop the four names; tests use `Logging_Standard.md` |
| AC3a | Legacy 0.1.48-0.1.50 fixtures migrate leaving no retired file after the reviewed resolution | `test_phase2_legacy_contracts` (claude/antigravity x github/strict) | OK; no retired file in either layout; dev and clean-code skills installed |
| AC3b | Receipt-based: each customised retired file raises its own porting conflict | `RulesRetirementTests` incl. `test_each_customised_developer_file_raises_its_own_porting_conflict` | One conflict naming the file, state unchanged, reviewed resolution completes it |
| AC4 | Validator fails on remaining references, exempts history lines | Seeded runs of `validate_retired_citations.py` | See edge cases |
| AC5 | Apply Retros sends Developer lessons to skill templates | Read diff at lines 58, 84, 123 | Targets are `skills/<skill>/SKILL_template.md` |
| AC6 | CHANGELOG entry in the unreleased block | Read diff | ST-000311 line under the current unreleased entry |
| AC7 | All gates exit 0, bundle check last | Run each on the head worktree | All exit 0 |

## Error and edge cases (seeded, each reverted)

- Template body ref `Developer_Rules_Bootstrap.md`: validator exits 1.
- Bundle asset ref `Clean_Code_Rules.md`: exits 1.
- Short form `Dev On-Demand §`: exits 1.
- Registry (`read-routing.json`) ref: exits 1.
- `**Version:**` and `**Previous:**` lines naming retired files: exits 0 (exempt).
- A plain `Version:` body line naming a retired file: exits 1 (only the bold history lines exempt).
- Stock receipt-based install retires all seven files without a manual resolution; unknown or divergent baselines stay conflicts.
- Legacy installs have no receipt, so no `adapted` flag; every retired copy stops on the reviewed-retirement conflict until resolved (AC3 wording).

## Regression

- `validate_internal_harness`, `generate_wrappers --check`, `generate_common_blocks --check`, `validate_templates`, `validate_retired_citations`: exit 0.
- `unittest scripts.test.test_internal_harness`: 78 OK. `scripts/test/run.sh`: 238 OK (1 skipped). `build_bundle.py --check`: exit 0 (last).
- Frozen `.claude/agents/templates/` copies intentionally untouched.

## Observations (non-blocking)

- `build_bundle.py` without `--check` does not delete stale assets; a removed template's asset needs a manual `git rm`.
- Validator does not match `_template` file names (different files).
