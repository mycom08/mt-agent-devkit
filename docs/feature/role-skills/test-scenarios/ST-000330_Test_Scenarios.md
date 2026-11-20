# ST-000330 Test Scenarios — Target Retirement of the Technical Lead Files

**Story:** ST-000330 (issue #330), PR #341, head `bca61daa8e9163655adee6f1b6eee305c9b3e083`
**Type:** behavioral (target retirement and routing). **Mode:** github, target layout, providers claude, antigravity, codex.
**Date:** 2026-11-20

## Scenarios

| ID | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| S1 | 1 | Phase 2 `templates/rules` and `bundle/assets` list | No `Technical_Lead_Rules_*` or `Story_Standard_TL` file; no ownership-JSON TL rows | PASS |
| S2 | 2 | `deployment.json` retirement entries for the three files | 15 entries (shared + per-provider/mode), all `required: false`; per-file survivors present in every plan | PASS |
| S3 | 2 | Install base `dec22bc` (legacy TL files present, 6 `tl-*` skills), then `lifecycle.sh update` with PR head, per provider | 3 stock copies retire on their own (`generated retirement:` x3); 6 skills + 6 wrappers remain; receipt verifies | PASS |
| S4 | 2 | Fresh `lifecycle.sh init` at PR head, per provider | No TL rules files; 6 skills + 6 wrappers | PASS |
| S5 | 2 edge | Base install, append a line to installed `Technical_Lead_Rules_Bootstrap.md`, update | Sync stops (rc 2, reviewed retirement required); file untouched | PASS |
| S6 | 2 | `read_manifest.py build` in each updated target: TL implementation, review, question | Reads `tl-core` plus task skill; no legacy TL file; every source exists | PASS |
| S7 | 3 | `validate_retired_citations.py` on the repo | No citations in internal corpus, Phase 2 templates, bundle assets | PASS |
| S8 | 3 | Seeded test: scratch corpus citing each TL name (template, rules template, bundle asset, `TL Bootstrap §5`) plus a `**Previous:**` history line | 4 findings, history line exempt, baseline empty | PASS |
| S9 | 3 | Repo unit tests `test_retired_citation_validator_rejects_tl_files_in_templates_and_bundle` and `test_bundle_retires_tl_templates_behind_their_own_survivors` | Pass | PASS |
| S10 | 4 | `changes.json` `0.1.58-SNAPSHOT` entry and `CHANGELOG.md` `[0.1.58] Unreleased` | Both record ST-000330 (removals, edits, ST-000330 bullet) | PASS |
| S11 | carry-over | Installed `tl-review`/`tl-implement` in all three targets vs legacy base text | non-zero test count, NFR skip-list entry, `BREAKING CHANGE:` footer each present once; trims are wording only; `tl-review` at 3999 of 4000 bytes | PASS |
| S12 | 5 | `validate_templates.py`, `run.sh`, `validate_internal_harness.py`, `generate_wrappers.py --check`, `generate_common_blocks.py --check`, `unittest scripts.test.test_internal_harness` (89 tests) | All exit 0 | PASS |

## Notes

- Environment: only `python3` on PATH; a scratchpad `python` shim was used. Temp targets and the base worktree were disposable.
- Frozen legacy Phase 1 templates under `.claude/agents/templates/rules/` still hold the three TL files, as they do for the Developer and PO files; they are outside the AC scope.
