# ST-000247 Test Scenarios — Analyze Requirements: ADRs, Roadmap and Test Strategy

Scope: PR 359, head `bb48e7454ebc8790a20d608e59f66261a9cf5b58`, github mode devkit. Type: behavioral.

Method: instruction inspection against scenarios, deployment into scratch targets, validators and regression suites. No live run of the workflow (user decision: tested on a real project after ST-000249).

| ID | AC | Scenario | Type | Expected |
|---|---|---|---|---|
| S1 | 1 | All specs approved, or some blocked by user decision | Happy | TL starts ADRs only after the Spec gate; ADRs under `adr/` in the `tl-design` section 7 format |
| S2 | 1 | ADR with a missing, blank, `TBD` or reason-less `N/A` NFR entry; same at the cap | Error | PO requests changes; the round counts; no user decision waives it |
| S3 | 1 | No spec approved; ADR kept blocked | Edge | Stops at `specs-approved`; blocked ADR carried to the roadmap with no assumed decision |
| S4 | 2 | Roadmap inputs, path and sections; blocked specs | Happy | `roadmap/Feature_Roadmap.md` with phases, candidates, dependencies, release criteria, risks, blocked items |
| S5 | 2 | Roadmap against story-drain globs | Edge | No story or issue created; path not matched by `plan/*Roadmap*.md` |
| S6 | 3 | PO concern in each mode; third round | Happy, Error | Tracking story or `tmp/Discussion.md`; cap 2 then user; never auto-approved |
| S7 | 4 | Strategy and designs, decision recorded | Happy | `testing/` paths; `required` or `not required` per spec with reason |
| S8 | 4 | One approver only; one approves and the other requests changes; cap | Edge | Stays unapproved; both re-review; cap 2 per document then user |
| S9 | 4 | Blocked roadmap or strategy | Error | Later stages stop; never `test-approved` |
| S10 | 5 | Verdict format and posting for ADR, roadmap, strategy, design | Happy | `gate-verdict` format and document ID; docs PR in GitHub mode; `State.md` in strict |
| S11 | 1-4 | Resume from an older state file at `specs-approved` | Edge | Continues at Stage 5; missing fields read as zero or empty |
| S12 | 1-5 | Fresh install into scratch targets (providers and modes) and update from base | Happy | Installed workflow, skill and orchestrator rows match the templates; all referenced skills exist; no stray template tokens |
| S13 | 6 | Validators, wrapper and bundle checks, unit tests, `run.sh` from a clean worktree at head; CI at head | Happy | All exit 0 |
| S14 | 6 | `changes.json` and `CHANGELOG.md` | Happy | Entries folded into the current snapshot version; version files unchanged |
