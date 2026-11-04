# ST-000309 Test Scenarios — Developer skills, load map and manifest routing

**Story:** ST-000309 (issue 309, PR 317) · **Validated head:** `15019fb285f96d6c328541f0c4fe1a17b42ec24c` · **Base:** `4f40388`
**Type:** behavioral · **Layout:** internal · **Mode:** github

## Happy path

| # | Scenario | Method | Expected |
|---|---|---|---|
| AC1 | Six `dev-*` skills with wrappers and size budgets | `wc -c` on each SKILL.md; wrapper presence under `.claude/.codex/.antigravity/skills` | dev-core 1,464 B (<= 1.5 KB); others <= 4 KB; 18 wrappers; dev-core repeats the point-of-use map |
| AC2 | `developer_instructions.md` slimmed | Read file | Role summary, record paths, Feature Context, Load Map; no "Selected Common Routing", no "read Agent_Common_Bootstrap in full"; no-task-skill report rule present |
| AC3 | `common`, `bootstrap`, `role_sources` overrides | Read `read_manifest.py` diff and registry; build Developer manifests | Skill list per source, one entry per skill, full coverage, dedup with `after` rewritten; `orchestrator_instructions.md:14` amended |
| AC4 | `capability_routes` skipped for `common` override; bare lookups raise `Blocked` | Run `test_common_capabilities` tests | Developer route keeps skills under a verified provider; missing entry raises `Blocked` with reason |
| AC5 | Unit tests for overrides and `role_sources` | Run `test_read_manifest.py` | list mapping, coverage reset, dedup tests present and pass |
| AC6 | TL/QA sample role plus Developer skip test | Read test diff | Sample role changed; Developer skip test added |
| AC7 | Developer rows resolve to skills; target manifests unchanged | Build manifests on base and head, all roles/tasks/layouts/providers/modes/session states | Only internal Developer routes differ; Developer routes name no deleted rules file |
| AC8 | Packets, deletions, ledger, citation validator | Read workflow diff; grep deleted names; run `validate_internal_harness.py`; inspect `retired` entries and ownership JSON | Packets name task skill; 4 files + 8 wrappers deleted; 8 `retired` entries; citations rejected internally |
| AC9 | Measurement table | Read `Dev_Skills_Measurement.md` | Bytes and calls per spawn type (story, peer review, refinement, question), before and after |
| AC10 | Inventory `skill` entries and wrapper check | Inspect `migration-inventory.json`; `generate_wrappers.py --check` | 6 skills x 3 providers; check exits 0 |
| AC11 | All gates | Run each gate on the head worktree | All exit 0 |

## Error and edge cases

- Roles other than Developer keep the shared Common file and capability routes (TL/QA still resolve to `Agent_Common_Core.md` under a verified provider).
- A role with no `common` override but with `role_sources`: `role_sources` must not replace the Common anchor (self-caught bug, covered by test).
- Invalid `common` or `role_sources` value (not a non-empty list of skill paths) blocks with a reason.
- Target-layout Developer rows keep their pre-skill sources; Phase 2 templates are untouched.
- Retired citations in the Phase 2 templates are out of scope for the internal validator (ST-000311).
- `**Previous:**` history lines naming retired files are allowed.

## Regression

Base-vs-head manifest comparison for every role, task, layout, provider, mode and session state; full automation suite; Phase 2 bundle check.
