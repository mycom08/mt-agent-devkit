# ST-000248 Test Scenarios — Analyze Requirements: UI/UX Feature Design Step

Scope: PR 360, head `6ea47fd1595e676bce5db818e1a7469adabb35fe`, github mode devkit. Type: behavioral.

Method: instruction inspection against scenarios, deployment into scratch targets, validators and regression suites. No live run of the workflow (user decision: tested on a real project after ST-000249).

| ID | AC | Scenario | Type | Expected |
|---|---|---|---|---|
| S1 | 1 | An approved spec touches a screen; no approved spec does; specs do not settle it | Happy, Edge | `required` and designer spawned; `not required` and stage skipped; user asked. Reason recorded |
| S2 | 1 | Requirements change adds or removes a screen, also after `test-approved` | Edge | Decision re-made; unchanged approved design stays approved; user told when a file no longer applies |
| S3 | 2 | Standard registered at an existing path | Happy | Designer receives that file; writes `ui-ux/<Feature_Name>_Design.md` on the feature design template with all states, deviations and promotion candidates |
| S4 | 3 | Row `not registered`, row absent, row naming a missing path | Happy, Edge, Error | Shipped standard used and step continues for the first two; user asked for the third |
| S5 | 4 | ADR writing, roadmap and QA while the design is unfinished, in review or blocked | Happy, Edge | Designer and TL spawned independently; Stages 6 and 7 do not wait or take the design; only Completion waits |
| S6 | 4 | Interrupted run; early stop; state file without the new fields | Edge | Design resumes from its own fields; missing fields read as `undecided` and `none` |
| S7 | 5 | PO approves or requests changes; blank state; third round | Happy, Error | `[PO] ... UI-DESIGN` verdict with revision on the docs PR; status header updated; cap 2 then user |
| S8 | 1-5 | Fresh install into scratch targets (3 providers, 2 modes) and update from base | Happy | Installed workflow, skill, templates and orchestrator row match sources; every referenced path exists; designer in the roster |
| S9 | 6 | Validators, wrapper and bundle checks, unit tests, `run.sh` at head; CI at head | Happy | All exit 0 |
| S10 | 6 | `changes.json` and `CHANGELOG.md` | Happy | Entries folded into the current snapshot; version files unchanged |
