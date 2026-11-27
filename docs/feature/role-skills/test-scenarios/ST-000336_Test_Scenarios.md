# ST-000336 Test Scenarios: sprint capacity as a project setting

Story: issue 336. PR: 383. Head under test: ccc7a88e396fea367654015a3c54d9fd8561b305.

Method: inspection of the devkit and shipped sources, the resolver run against hand-built settings files, a scratch install and re-apply of the bundle in both modes, and the repository gates. No live Plan Sprint run.

| ID | AC | Scenario | Expected |
|---|---|---|---|
| T1 | AC1 | Fresh install from the PR bundle, github and strict | `project_settings.json` holds `sprint_capacity: 60` |
| T2 | AC1 | Set 30, then re-apply the bundle | Value preserved |
| T3 | AC1 | Existing project with only `po_execution` upgrades from the base bundle | File unchanged; resolver gives 60 silently |
| T4 | AC2 | File absent, key absent | 60, no stderr |
| T5 | AC2 | Positive integers, including 1 and a very large value | Printed as written, no stderr |
| T6 | AC2 | String, float, NaN, Infinity, 0, negative, boolean, null, array, object | 60, exactly one stderr line, exit 0 |
| T7 | AC2 | Unreadable JSON, non-object JSON, UTF-8 BOM, non-UTF-8 bytes | Same handling as `po_execution` |
| T8 | AC2 | Installed script in the scratch target, and the devkit's own script path | Both resolve `sprint_capacity` |
| T9 | AC3 | Devkit and shipped Plan Sprint workflows, installed copies in both modes | Stage 0 resolves once, passes it to every PO assignment, no state file |
| T10 | AC4 | Search workflows and skills for a literal capacity | None; all refer to `sprint_capacity` |
| T11 | AC5 | Resolver tests run, then the boolean guard and the default are broken | Tests pass, then fail |
| T12 | AC6 | Shipped sources, bundle `--check`, `changes.json`, `CHANGELOG.md`, gates, CI at head | All updated and passing |
| T13 | Regression | `po_execution` and `agent_models` resolution compared with the base script | Unchanged output |
