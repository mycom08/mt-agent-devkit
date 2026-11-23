# ST-000346 Test Scenarios: Retire changes.json Coverage Checks

PR 349, head b97a17ba1ce1fc2c85e2424976f3723332160c3f. Python via `python3` shim, `LC_ALL=C.UTF-8`.

| # | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| 1 | AC1 | grep the repo for `ALLOWLIST_UNTRACKED_TEMPLATES` and `ALLOWLIST_REMOVED_PATHS` | no occurrences | PASS |
| 2 | AC1 | `--changes-json` file with one entry listing a nonexistent path, templates absent from history | no invariant 6 error | PASS |
| 3 | AC2 | Same phantom-path run (listed path missing on disk) | no error (existence not checked) | PASS |
| 4 | AC3 | `manifest_bad_version.json` | one error, invalid semver key | PASS |
| 5 | AC3 | `manifest_bad_deployment.json` | one error, invalid deployment declaration | PASS |
| 6 | AC3 | `manifest_bad_legacy_arrays.json` + `manifest_empty_root` | one error, arrays not the two bridges | PASS |
| 7 | AC3 | `manifest_unsafe_asset.json` + root | one error, unsafe/duplicate asset | PASS |
| 8 | AC3 | `manifest_duplicate_asset.json` + root | one error, unsafe/duplicate asset | PASS |
| 9 | AC3 | `manifest_bad_hash.json` + root | one error, hash/byte mismatch | PASS |
| 10 | AC4 | Six `manifest_*` fixtures, one per kept failure, run through `run.sh` with `--changes-json`/`--manifest-root`; repo-root `changes.json` not replaced; `git status` clean after run | each exits 1 with only its own error | PASS |
| 11 | AC5 | Read `docs/Template_Test_Strategy.md` invariant 6 | lists only remaining checks, no allowlist or backlog text | PASS |
| 12 | AC6 | Real `changes.json` trimmed to its 3 newest entries, `--changes-json` | exit 0 | PASS |
| 13 | AC7 | CHANGELOG `[ST-000346]` line present | present | PASS |
| 14 | AC8 | validate_templates, run.sh (17/17), validate_internal_harness, generate_wrappers --check, generate_common_blocks --check, test_internal_harness (101) | all exit 0 | PASS |
| 15 | Edge | CI Layer-1 invariant check at the head (run 45164354969) | pass | PASS |
