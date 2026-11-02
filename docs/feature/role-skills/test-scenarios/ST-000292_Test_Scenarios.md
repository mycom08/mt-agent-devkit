# ST-000292 Test Scenarios — orchestrator-as-PO mode

**Story:** ST-000292 (issue 292), PR 299, head fb4a88f. **Type:** behavioral.

| AC | Scenario | Method | Expected |
|---|---|---|---|
| 1 | Section 5 matrix rows in devkit and Phase 2 templates | Inspect `orchestrator_instructions.md` and its shared template (PO Touchpoints table); inspect each of the six workflows and its `*_Shared_template.md` | Ten rows present in both; each workflow routes on the pinned `PO Execution`; added-line counts per workflow match between devkit and template |
| 1 | `subagent` unchanged | `git diff cdae0cd..HEAD` removed lines in workflows/instructions | Every removed line is re-stated as the explicit `PO Execution: subagent` branch with identical spawn, model policy and skill naming |
| 2 | Forced spawn: Plan Sprint | Inspect Plan_Sprint workflow and template; `test_forced_spawns_hold_in_both_modes` | Stages 1, 2, 4 spawn/resume a real `po_session` in both modes |
| 2 | Forced spawn: Stage 3, QA implementer | Inspect Shared_Pipeline_Stages and template | Always spawns PO (`po_validation`, `po-validate-ac`), never inline |
| 3 | Escalation | Inspect Scope-Change Escalation (Shared_Pipeline_Stages, Resume_Story, instructions); `test_scope_change_after_stage_1_escalates_to_the_user` | Defer, split, any AC body edit after Stage 1 goes to the user via Blocked Story Procedure; Resume applies the user's decision |
| 4 | Inline skill loading and state | Inspect inline procedure steps 1-2 and state templates | Canonical `SKILL.md` paths named; `po_session: inline` and `PO Skills` recorded; observation checks accept inline |
| 5 | Inline state per section 7 | Inspect procedure steps 3-7; `test_inline_procedure_state_telemetry_and_retro_follow_section_7` | Memory read at first PO activity, Working Record per po-core (closure skips), retro role `Orchestrator`, one telemetry row per activity |
| 5 | Row validity | `telemetry.py harness` on scratch metadata | PO inline row without tokens validates (`unavailable`); PO inline with tokens rejected; `Orchestrator` role with `fresh` mode rejected |
| 6 | Measured vs unmeasured | `telemetry.py compare` on scratch JSONL: measured both modes, orchestrator total unavailable, worker lacking tokens | Measured stories get `saving`; the other two are `unmeasured` with a reason, never estimated |
| 6 | Mode contamination | `compare --subagent` fed an orchestrator-mode file | Rejected with an error |
| 7 | Coverage and gates | New `OrchestratorPoModeTests` (6), telemetry tests (3); gates | validate_internal_harness, generate_wrappers --check, unittest test_internal_harness (56), validate_templates, run.sh (225), build_bundle --check all exit 0 |

Edge cases: a story with a repeated cycle (`refine-stage2-c2`), a multi-story activity using the sprint label, Create Stories with no sprint (`none`), `Owner` both in consultation (TL first, PO inline after).
