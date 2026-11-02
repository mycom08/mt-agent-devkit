# ST-000291 Test Scenarios — po_execution setting and contracts

**Story:** ST-000291 (issue 291), PR 297, head e36c943. **Type:** behavioral.

| AC | Scenario | Method | Expected |
|---|---|---|---|
| 1 | Bundle entry for `.mt-agent-devkit/project_settings.json` | Inspect `bundle/deployment.json`; `build_bundle.py --root . --output <bundle> --check` | `ownership: project_owned`, `renderer: create_if_absent`, default `{"po_execution": "subagent"}`; no entrypoint mirror |
| 1 | Init creates, sync preserves | `test_init_creates_subagent_default_and_sync_never_overwrites`, `test_project_owned_settings_created_once_and_never_overwritten` | Edited value survives re-apply; verify passes |
| 2 | Absent file/key | `project_settings.py po_execution --root <empty>` | `subagent`, no stderr |
| 2 | Unrecognised value, unreadable JSON, wrong type | CLI with `bogus`, `{bad` | `subagent`, exactly one stderr report line |
| 2 | Orchestrator pin and resume | Inspect orchestrator instructions and Sprint_Workflow state | `**PO Execution:**` pinned; resumed run uses pinned value |
| 3 | Story_Standard role table, Done row, section 14 | Diff and `PoExecutionSettingTests` | Actor phrase in Done row, PO role row, 3 times in section 14; tracked-split step 1 states the user's decision; template identical |
| 4 | Own-record rule amendment | Inspect Agent_Common_Bootstrap, Agent_Common_Working_Record and templates | Exception sentence present in all four |
| 5 | `orchestrator_inline` session mode | `test_telemetry` inline tests | PO inline row with `usage_source: unavailable` validates; measured usage rejected; transcript extraction rejected |
| 6 | Trade-off documented | Inspect resolver docstring and orchestrator instructions | Accepted trade-off stated |
| 6 | Regression gates | validate_internal_harness, generate_wrappers --check, unittest test_internal_harness, validate_templates, run.sh, build_bundle --check | All exit 0 |

Edge cases: null, list and string values for the key; non-object JSON; create_if_absent file edited between syncs (receipt re-recorded, not a no-op).
