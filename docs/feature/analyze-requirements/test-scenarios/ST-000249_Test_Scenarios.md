# ST-000249 Test Scenarios — Analyze Requirements: Backlog Story Creation

Scope: PR 362, head `147c06e066bf0155cd47adb81ae2e25b12b95f77`, github mode devkit. Type: behavioral.

Method: instruction inspection against scenarios, deployment into scratch targets, validators and regression suites. No trial run of the workflow (user decision: tested on a real project).

| ID | AC | Scenario | Type | Expected |
|---|---|---|---|---|
| S1 | 1 | Roadmap or strategy blocked or not approved; a spec, ADR, UI design or test design unfinished without a user block; docs PR unmerged | Error, Edge | No story created; workflow waits or stops |
| S2 | 1 | Spec, ADR, design or test design blocked by a user decision | Edge | Stage 8 reachable; `Blocked:` line recorded; never counts as approval |
| S3 | 2 | CI green, failing, pending, zero checks; document edited after verdict; PR closed unmerged, refused, already merged | Happy, Error | Merge only on green and unchanged; otherwise stop; merged PR skips the merge |
| S4 | 3 | Resume after partial creation; renamed candidate; roadmap under drain and Plan Sprint step 7 | Error, Edge | Marker lookup prevents duplicates; unmatched marker reported first; drain does not fire |
| S5 | 4 | Candidate with no blocked dependency; depends on blocked document; depends on skipped candidate | Happy, Edge | Backlog story with points, label, spec and tracking links; others skipped |
| S6 | 5 | Blocked document with and without waiting candidates; sprint start, resume, plan and done-story fallback meet the open-topic story | Happy, Edge | One story per document, never picked up as sprint work |
| S7 | 6 | Strict mode install and Stage 8 text | Happy, Edge | Local story format, roadmap link, no PR or label commands |
| S8 | 7 | Tracking comment; tracking close with and without open topics | Happy, Edge | Lists created and skipped; closes only when none remain |
| S9 | 8 | Answer given, missing, ambiguous; other input on a `done` feature; missing `State.md`; second round; blocked UI design; spec dropped | Happy, Error, Edge | One new PR per round, only missing stories, resolved topics closed, affected stories reported, never edited |
| S10 | 1-8 | Fresh install into scratch targets (3 providers, 2 modes) and update from base | Happy | Installed workflows and skill match sources; referenced paths and labels exist |
| S11 | 9 | Validators, wrapper and bundle checks, unit tests, `run.sh` at head; CI at head; `changes.json` | Happy | All exit 0; entries folded into the current snapshot |
