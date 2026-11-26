# ST-000371 Test Scenarios — Runtime root forms in the retro completion and wait helpers

**Story:** ST-000371 (issue 371, PR 375)
**Scope validated:** 0a84ab13f00b0112b9541bd7f7835a701ad917ac (base 990e09c45c1bab1f0635a94d3cda2d1f675b2357)

Scenarios run in disposable projects. "Installed" means a scratch install from the bundle for each provider and mode.

| ID | AC | Type | Scenario | Expected |
|----|----|------|----------|----------|
| T1 | 3 | Error | Story Repro Command (absolute path outside, empty target) | Rejected; message names the accepted forms |
| T2 | 1 | Happy | Installed retro helper: relative and absolute form of the installed binding, `record` and `check` | Accepted; same record |
| T3 | 1 | Edge | Absolute form through a symlinked project parent; `--target` relative or defaulted | Accepted |
| T4 | 2, 3 | Error | Non-installed folder, outside path, `..`, project root, backslash or drive form, `./` prefix, empty | Rejected; forms named |
| T5 | 2, 3 | Error | Inner link at provider dir, runtime dir, `harness/`, `state-paths.json`; dangling link | Rejected; forms named |
| T6 | 2, 3 | Error | Binding missing, invalid JSON, not an object, foreign provider root or prefix | Rejected; forms named; no traceback |
| T7 | 5 | Happy/Error | Installed wait helper over the T2 to T6 inputs | Same accept and reject result as the retro helper |
| T8 | 4 | Inspection | `retro` skill, Common Core and Bootstrap, templates, bundle assets, installed copies | All state the accepted form |
| T9 | 6 | Tests | New tests pass at head and fail against the base scripts | Pass / fail |
| T10 | 6 | Gates | Harness, template, wrapper, common-block, bundle checks, unit tests, run.sh | All exit 0 |
| T11 | 6 | Metadata | `changes.json` descriptions, CHANGELOG bullet, version untouched | Per `change-metadata` |
| T12 | 6 | Regression | Scratch install, 3 providers x 2 modes; helpers leave no cache files from the retro import | Installed files match the bundle |

## Results (2026-11-26, revision 0a84ab13f00b0112b9541bd7f7835a701ad917ac)

All AC PASS.

- T1: exit 2; message names the installed `RUNTIME_ROOT` from `.claude/harness/state-paths.json`, relative or absolute.
- T2 to T7, T12: 492 scripted checks over 3 providers x 2 modes, 0 failures. Installed helpers match the bundle assets and internal scripts byte for byte.
- T8: skill, Common Core and Common Bootstrap (internal, bundle, installed) state the form; no `concrete-runtime-root` text remains outside docs.
- T9: 72 tests pass at head; the same tests against the base scripts give 13 failures and 7 errors.
- T10: harness, wrapper, common-block, template and bundle checks, 110 harness tests and run.sh (17/17 fixtures) exit 0, launched through the wait helper with an absolute runtime root. CI passed at head.
- T11: `changes.json` and CHANGELOG entries present; VERSION and version.txt untouched.

Not exercised: native Windows drive paths (no Windows host); only their rejection on POSIX was run.
