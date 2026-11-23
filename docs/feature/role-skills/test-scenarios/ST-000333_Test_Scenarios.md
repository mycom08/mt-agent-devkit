# ST-000333 Test Scenarios — QA Skills Retirement in Targets

**Story:** ST-000333 (PR 344, head `d5543a1`, base `8162981`) — **Feature:** `role-skills` — **Mode:** github
**Method:** read the diff, `build_bundle.py`, `deployment.json`, the citation validator and the changes metadata; run each gate in a detached worktree at the head SHA (`python` shim to `python3`, `LC_ALL=C.UTF-8`).

| # | AC | Scenario | Type | Expected | Result |
|---|---|---|---|---|---|
| 1 | 1 | The three `*_template.md` files are absent under `phase2/templates/rules/` | Happy | `ls` fails for each; diff shows `D` | PASS |
| 2 | 1 | Their bundle assets (`rules_QA_Rules_Bootstrap.md`, `rules_QA_Rules_Read_On_Demand.md`, `rules_Story_Standard_QA.md`) are deleted and no `assets` entry names them | Happy | `D` in diff; no asset id or path match in `deployment.json` | PASS |
| 3 | 1 | Frozen legacy templates under `.claude/agents/templates/rules/` remain (same as the Developer and TL retirements) | Edge | Present, not part of the Phase 2 distribution | PASS |
| 4 | 2 | `RETIRED_SURVIVORS` has an entry for each QA file; survivors match Ownership Map section 17 and include `instructions/qa_instructions.md` | Happy | 3 entries, survivors equal the section 17 table | PASS |
| 5 | 2 | `deployment.json` has a shared retirement entry per file plus per-provider/mode entries (claude, antigravity; github, strict), all `required: false` | Happy | 15 retirement entries, all `required: false` | PASS |
| 6 | 2 | Survivors are shared canonical IDs present in every plan, no provider suffix | Edge | `test_bundle_retires_qa_templates_behind_their_own_survivors` OK | PASS |
| 7 | 2 | Installed legacy copies retire on a fresh install and `sync devkit` for every provider | Regression | `test_phase2_legacy_contracts` and `test_phase2_deployment` OK | PASS |
| 8 | 3 | `validate_retired_citations.py` on the head tree | Happy | exit 0, scope names the internal corpus, Phase 2 templates and bundle assets | PASS |
| 9 | 3 | Seeded negative: append a `QA_Rules_Bootstrap.md` citation to a Phase 2 template | Error | validator exits 1 with the file and line | PASS |
| 10 | 3 | Unit seeded test covers the three QA names, `QA Bootstrap` and `QA Rules` section citations, templates, bundle assets, both registry layouts; history lines and ledgers exempt | Edge | `test_retired_citation_validator_rejects_qa_files_in_templates_and_bundle` OK | PASS |
| 11 | 3 | Remaining grep hits of the QA names are ledgers, history, tests, the validator, the retire lists, frozen legacy templates or working copies | Edge | No live citation in a skill, shipped template or document | PASS |
| 12 | 4 | `changes.json` `0.1.58-SNAPSHOT` lists the three removed templates and the two Sync templates as `[ST-000333] ...` clauses | Happy | Compact clause lists, earlier clauses kept, no narrative | PASS |
| 13 | 4 | `CHANGELOG.md` has one `[ST-000333]` entry under the unreleased section | Happy | Present | PASS |
| 14 | 5 | `python scripts/validate_templates.py` | Gate | exit 0 | PASS |
| 15 | 5 | `bash scripts/test/run.sh` | Gate | exit 0 | PASS |
| 16 | 5 | `validate_internal_harness.py`, `generate_wrappers.py --check`, `generate_common_blocks.py --check`, `unittest scripts.test.test_internal_harness` (101 tests) | Gate | all exit 0 | PASS |
| 17 | 5 | Wider suites `test_phase2_legacy_contracts`, `test_phase2_deployment`, `test_read_manifest` (81 tests) | Regression | OK | PASS |
| 18 | 5 | CI run 45140676828 on the head SHA | Gate | Layer-1 invariant check pass | PASS |
