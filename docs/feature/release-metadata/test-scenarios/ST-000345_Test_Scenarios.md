# ST-000345 Test Scenarios: Legacy Stamp Minimum Version

PR 348, head 204af3e1bde1371d962a19609a1efc4ce76f71dc. Python via `python3` shim, `LC_ALL=C.UTF-8`.

| # | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| 1 | AC1 | `bridge_gated` on 0.1.51, 0.1.53, 0.2.0, 1.0.0, 10.0.0 | True (numeric tuple, no upper bound) | PASS |
| 2 | AC1 | 0.1.50, 0.1.5, 0.1 | False | PASS |
| 3 | AC1 | Installed stamp 0.1.51/0.1.53/1.0.0 with current bridge, bundle built from trimmed changes.json | compatible_bridge true, no error | PASS |
| 4 | AC2 | Source `build_bundle.py` no longer reads `changes.json` for versions | diff shows both lines removed | PASS |
| 5 | AC2 | Rebuilt `bridge_provenance.json` | only `bridges` key; `provenance()` shape/fallbacks `bridges` only | PASS |
| 6 | AC3 | Fixture 0.1.53, current bridge, metadata truncated to 3 entries | migration succeeds | PASS |
| 7 | AC4 | Stamps 0.1.47, 0.1.51-rc1, v0.1.52, 0.1 with bridge; 0.1.53 without bridge | "unknown older layout" | PASS |
| 8 | AC4 | 9.9.9 with `bridge=False`; tampered provenance JSON | fail closed | PASS |
| 9 | AC5 | `changes.json` unreleased entry has migration.py description in `[ST-NNNNNN]` clause form; CHANGELOG line | present | PASS |
| 10 | AC6 | validate_templates, run.sh (10/10), validate_internal_harness, generate_wrappers --check, generate_common_blocks --check, test_internal_harness (101), phase2 tests (31), build_bundle --check | all exit 0 | PASS |
| 11 | Edge | Stamp `0.1.051` (leading zero) | accepted (numeric 51); not specified by AC, noted only | OBSERVATION |
| 12 | Edge | Trailing newline, leading space, 4-part stamp | rejected | PASS |
