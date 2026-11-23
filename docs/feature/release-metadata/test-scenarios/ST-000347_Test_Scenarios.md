# ST-000347 Test Scenarios: Trim changes.json History

PR 350, head bb91368ff35b0018326777237b5024b5941cafaf. Python via `python3` shim, `LC_ALL=C.UTF-8`. Script scenarios ran on scratch copies under the scratchpad, never on the real `changes.json`.

| # | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| 1 | AC1 | Scratch copy of the pre-trim 66-entry file (snapshot stamped 0.1.58), `open_next_snapshot.py 0.1.59-SNAPSHOT` | keys `0.1.59-SNAPSHOT, 0.1.58, 0.1.57, 0.1.56`; older dropped | PASS |
| 2 | AC1 | Run again on that result with `0.1.60-SNAPSHOT` (edge: unstamped snapshot is counted as released) | `0.1.60-SNAPSHOT, 0.1.59-SNAPSHOT, 0.1.58, 0.1.57`; documented release flow stamps first | PASS (note) |
| 3 | AC1 | Scratch trimmed file, run once | four entries; retained 0.1.58 entry unchanged | PASS |
| 4 | AC1 | `test_next_snapshot_keeps_snapshot_plus_newest_three_released` (five released in, fewer than three in) | 4 keys; 2 keys when one released entry | PASS |
| 5 | AC2 | Real `changes.json`: key list, count, JSON validity, trailing newline | `0.1.58-SNAPSHOT, 0.1.57, 0.1.56, 0.1.55`; 4 entries; newest-first | PASS |
| 6 | AC2 | Compare retained entries to `main:changes.json` | 0.1.57/56/55 identical, first four keys of main in order | PASS |
| 7 | AC3 | Diff of four Phase 2 rules templates | footers name `CHANGELOG.md`, one line each, nothing else | PASS |
| 8 | AC3 | grep Phase 2 templates for "see `changes.json`"; frozen `.claude/agents/templates/` diff | no leftovers; zero frozen files touched | PASS |
| 9 | AC3 | `build_bundle.py --check`; bundle assets and `deployment.json` hashes for the four files | exit 0, bundle matches templates | PASS |
| 10 | AC4 | README, change-metadata SKILL, Template_Test_Strategy diffs | retained-versions rule stated in each | PASS |
| 11 | AC5 | validate_templates, run.sh (17), validate_internal_harness, wrappers and common-blocks `--check`, test_internal_harness (101), test_phase2_sync, build_bundle `--check` | all exit 0 | PASS |
| 12 | AC6 | Snapshot `descriptions` and CHANGELOG | four `[ST-000347]` descriptions, CHANGELOG bullet present | PASS |
