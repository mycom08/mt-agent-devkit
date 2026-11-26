# ST-000372 Test Scenarios — Branch preflight judges runtime files by path

**Story:** ST-000372 (issue 372, PR 374)
**Scope validated:** 23939b4b685ced36d85f5b22b18eb5c4aad06cbf (base 7689c4e1f828ea1e4365c9397db1ef75a1823bff)

All scenarios use disposable repositories. "Copies" means the internal script, the Phase 2 template and the bundle asset.

| ID | AC | Type | Scenario | Expected |
|----|----|------|----------|----------|
| T1 | 1, 3 | Happy | Repro Command: strict base whose tip subject starts with `Agent:` | PASS |
| T2 | 1, 3 | Happy | Pushed plan-document `Agent:` commit, github and strict, all copies | PASS, agent state `no` |
| T3 | 1 | Edge | Unpushed `Agent:` plan-document commit, github | BLOCKED as ahead, agent state `no` |
| T4 | 2 | Error | Force-added file in each of 12 `agents/working/` runtime folders, in base tree | BLOCKED, path as evidence |
| T5 | 2 | Error | Same 12 folders, unpushed commit | BLOCKED as ahead, agent state `yes` |
| T6 | 2 | Error | Runtime file buried below a later ordinary commit | BLOCKED |
| T7 | 2 | Error | Previously listed runtime folders still block | BLOCKED |
| T8 | 2 | Edge | `agents/working/rules/`, `retros/` (ST-000373) and look-alike paths | PASS |
| T9 | 1, 2 | Edge | `create` on a passing `Agent:` base | Story branch created |
| T10 | 2 | Regression | This repository's own tracked tree against the new prefixes | No match |
| T11 | 4 | Inspection | Search rules, skills, workflows and guides for the prefix check or workaround | No stale description |
| T12 | 5 | Tests | New tests pass at head and fail against the base script | Pass / fail |
| T13 | 6 | Gates | Template and harness validators, wrapper check, unit tests, run.sh, bundle check, `bash -n` not applicable | All exit 0 |
| T14 | 6 | Metadata | `changes.json` description, CHANGELOG bullet, bundle hash, version untouched | Per `change-metadata` |
| T15 | 6 | Regression | Scratch init: installed script is the fixed one, github and strict, all providers | Identical to bundle asset |

## Results (2026-11-26, revision 23939b4)

All AC PASS.

- T1: head PASS; base 7689c4e BLOCKED.
- T2 to T5, T8, T9: pass on all three copies.
- T6, T7: pass for every folder each copy lists. `.<provider>/agents/runtime/` is listed by the internal script only, same as at base, so it is expected to pass the preflight on the template and bundle copies.
- T10: no tracked file matches the prefixes.
- T11: no stale description in active rules, skills, workflows or guides.
- T12: 27 tests pass at head; the same tests against base give 30 subtest failures.
- T13: wrappers, common blocks, harness and template validators and bundle check exit 0; run.sh 287 tests, 1 skipped, 17/17 fixtures.
- T14: `changes.json` and CHANGELOG entries present; VERSION untouched.
- T15: scratch init, 3 providers x 2 modes, installs the bundle script byte for byte.

Not exercised: a legacy v0.1.48-0.1.50 target on its first bridge pass (frozen copy keeps the old check; accepted by TL on issue 372). Retros are out of scope (ST-000373).
