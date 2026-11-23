# ST-000322 Test Scenarios: agent_models Override

PR 351, head 099fc89169c0cdebe675096c2116ed5c03b417ac. Python via `python3` shim, `LC_ALL=C.UTF-8`. Resolver scenarios ran against scratch settings files under the scratchpad (`project_settings.py agent_models --root <scratch> --role --policy`), never the real `.mt-agent-devkit/project_settings.json`.

| # | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| 1 | AC1 | Role-only block (`Developer`: model opus, effort high) | `{"effort":"high","model":"opus"}` | PASS |
| 2 | AC1 | Policy-only block (`implementation`: model haiku) | `{"model":"haiku"}` | PASS |
| 3 | AC1 | `UI/UX Designer` role, `standard` policy, effort only | `{"effort":"low"}` | PASS |
| 4 | AC1 | Case mismatch in file keys (`developer`, `Implementation`) and in arguments | ignored/no override, one report line per key | PASS |
| 5 | AC2 | Absent file; absent key; empty `agent_models` object | `{}`, no report, rc 0 | PASS |
| 6 | AC2 | Role model + policy model/effort | merged per field, role model wins, policy effort fills | PASS |
| 7 | AC2 | Role effort only + policy model/effort | role effort wins, policy model fills | PASS |
| 8 | AC2 | Wrong shape: block is a list; role entry a string | `{}` / policy-only result, one stderr line | PASS |
| 9 | AC2 | Non-string `model` (5) and empty-string `model` | that entry gives no override (whole entry), one report line | PASS |
| 10 | AC2 | Unknown role key and unknown field (`color`) | ignored, one report line each, valid fields kept | PASS |
| 11 | AC2 | Unreadable JSON | `{}` with one report line, never a guess | PASS |
| 12 | AC2 | `po_execution` unchanged; `--role` with `po_execution` | `subagent`; argparse error rc 2 | PASS |
| 13 | AC2 | Unit tests `AgentModelsTests` (10 tests) cover each case | all present, run OK | PASS |
| 14 | AC3 | `test_precedence_each_tier_wins_over_the_tiers_below_it`, `test_file_tier_composes_with_user_and_adapter_tiers`; precedence text in orchestrator, pipeline stages | five tiers in documented order, each tier tested | PASS |
| 15 | AC4 | Orchestrator instruction, Sprint and Refine state blocks, write rules | resolved once, `**Agent Models:**` pinned, resume keeps it, legacy state file pins once | PASS |
| 16 | AC5 | Three adapters (claude, antigravity, codex) | unexposed model or unsupported effort falls back per field and is reported; non-settable field keeps default, reported as not applied | PASS |
| 17 | AC6 | `test_init_creates_no_overrides_and_sync_update_keep_an_existing_block` (build bundle, deploy, write block, redeploy twice, verify) | fresh init has no `agent_models`; existing block byte-identical after two re-runs; manifest entry is `project_owned`/`create_if_absent` | PASS |
| 18 | AC7 | Orchestrator text: telemetry row records model actually used; claude adapter says the same | present | PASS |
| 19 | AC8 | Diff vs main for `CLAUDE.md`, `AGENTS.md`; test asserts deployed `CLAUDE.md` lacks `agent_models` | zero changes | PASS |
| 20 | AC9 | Orchestrator, Shared_Pipeline_Stages, Workflow_Guide: devkit copies and Phase 2 templates | each has the setting and one example | PASS |
| 21 | AC9 | Frozen `.claude/agents/templates/` | zero files in diff | PASS |
| 22 | AC10 | `changes.json` snapshot entry and CHANGELOG | five `[ST-000322]` descriptions in compact form; CHANGELOG bullet | PASS |
| 23 | AC11 | validate_templates, run.sh (17), validate_internal_harness, generate_wrappers and generate_common_blocks `--check`, test_internal_harness + test_project_settings (119), build_bundle `--check` | all exit 0 | PASS |

Edge note: an entry with one bad field drops the whole entry (valid sibling field included), consistent with AC2 "no override for that entry".
