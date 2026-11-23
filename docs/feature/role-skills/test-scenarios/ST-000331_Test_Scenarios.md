# ST-000331 — Test Scenarios (QA skills, internal)

**Story:** ST-000331 (issue #331), PR #342, feature `role-skills`, sprint-12
**Validated head:** `45ff0fbdd77dbdedd55d7ce55fa4092f93a4d9f9` (base main `188e40ff70e6db149ee1542a87f471cefe517029`)
**Tester:** QA, 2026-11-23. Only `python3` exists on the host; `scripts/test/run.sh` ran with a scratchpad `python` shim.

Method: read-only checks of the PR head; fabricated-citation tests ran in a `git archive` copy outside the repo.

## Scenarios

| # | AC | Scenario | Type | Expected | Result |
|---|---|---|---|---|---|
| 1 | 1 | Five `qa-*` skills exist under `.mt-agent-devkit/skills/` with frontmatter, one `**Requires:**` line and a wrapper per provider (15 wrappers) | Happy | Present, within size budgets | PASS |
| 2 | 1 | Spot-check 14 rules from `git show main:` of the three deleted files against Ownership Map §15 and the skill text (locating work 1-4; §14 verdicts; scenario-first and exceptions; `bash -n`; `changes.json` clause check; failure policy; post-pass commit; regression 1-5 and local-verify; CI-equivalent exception; hotfix 1-3; per-AC single comment and cap exemption; red flags; status table; pointer rows 9-13) | Happy | Each rule has an owner skill and the text is present | PASS |
| 3 | 2 | Each source rule has exactly one owner in §15a/§15b; the four drops (UI-mirror note, version history, QA setting `status:done`, "confirm merged before testing") are named with a reason and each contradicts a kept rule | Edge | No silent loss; drops justified | PASS |
| 4 | 3 | `qa_instructions.md` Load Map lists `qa-core` and common skills at spawn, `qa-validate` and `qa-testing` for validation, `qa-regression`, `qa-hotfix` at point of use | Happy | Matches the registry | PASS |
| 5 | 3 | Rebuild the QA manifest for story validation (`read_manifest.py build`) | Happy | Reads the same skills as the Load Map; no deleted file | PASS |
| 6 | 3 | Manifest with `regression_check` trigger | Edge | Adds `qa-regression` (14 calls) | PASS |
| 7 | 3 | Three QA files and six wrappers are absent; six `retired` entries by ST-000331 in `migration-inventory.json` (same shape as ST-000328) | Happy | Deleted and ledgered | PASS |
| 8 | 3 | `validate_retired_citations.py` on a scratch copy with `QA_Rules_Bootstrap.md` in a skill, `Story_Standard_QA.md` and `QA Bootstrap §` in an instruction file, and `QA_Rules_Read_On_Demand.md` in the non-target registry | Error | exit 1, each citation reported | PASS |
| 9 | 3 | Same validator on the repo, where target layouts and Phase 2 files still name the files | Edge | exit 0 (exempt until ST-000332) | PASS |
| 10 | 4 | `qa-hotfix` is QA-only and names `dev-hotfix` | Happy | Note present, 654 bytes | PASS |
| 11 | 5 | Recompute before/after bytes and calls: base manifest from the base tree, head manifest from the head tree, derive refinement and question | Happy | Equal to `QA_Skills_Measurement.md` | PASS |
| 12 | 6 | The four gate commands, `scripts/validate_templates.py`, `scripts/test/run.sh`, `test_read_manifest`, `test_common_capabilities` | Happy | All exit 0 | PASS |
| 13 | 6 | Tests cover the QA route (`QaSkillsTests`, `QaSkillRoutingTests`, 11 tests) | Happy | Present and passing | PASS |
| 14 | any | Manifest and role instruction disagree on routing | Edge | No disagreement | none found |

## Evidence summary

- Gates: `validate_internal_harness.py`, `generate_wrappers.py --check`, `generate_common_blocks.py --check` exit 0; `unittest scripts.test.test_internal_harness` 96 tests OK; `validate_templates.py` OK; `run.sh` 10 passed, 0 failed; read_manifest and common_capabilities suites 58 tests OK.
- Measurement (bytes / calls, before to after): validation 58,478/8 to 45,804/13; regression 58,478/8 to 47,855/14; refinement 53,420/7 to 35,310/10; question 58,235/8 to 40,125/11. All reproduced.
