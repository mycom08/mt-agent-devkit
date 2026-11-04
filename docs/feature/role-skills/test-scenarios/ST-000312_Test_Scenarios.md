# ST-000312 Test Scenarios — Other roles point to common skills (target templates)

**Story:** ST-000312 (issue 312, PR 319) · **Validated head:** `cceecb050f8a6cd0366725f14430b98c40f47df7` (TL Approved-SHA) · **Base:** `9c20789`
**Type:** behavioral · **Layout:** target (Phase 2 templates and routing) · **Mode:** github

## Happy path

| # | Scenario | Method | Expected |
|---|---|---|---|
| AC1 | Phase 2 TL, QA, UI/UX, BA rule templates and `po-*`/`comment` skill templates point to common skill templates where the internal versions do | Diff skill-pointer sets internal vs template per file; read the QA, po-core diffs; check each pointed skill has a shipped template and bundle entry | Pointers match the internal files, except internal-only `change-metadata` and intended target adaptations; all 11 pointed skills ship |
| AC2 | No Phase 2 template cites `Clean_Code_Rules.md` except Sync_Devkit and legacy Developer templates; TL Bootstrap points to `clean-code` | `grep -rl Clean_Code_Rules` over Phase 2; read TL Bootstrap line 34 | Only `Developer_Rules_Bootstrap_template.md` and `Sync_Devkit_Workflow_template.md` (plus bundle copies and routing) cite it; TL Bootstrap cites `clean-code` |
| AC3 | Stricter TL-as-implementer gate in TL On-Demand template | Read section 3 | Points to `pre-pr-gate`; no docs/config exemption table |
| AC4 | Non-Developer `layouts.target` overrides removed; target TL/QA/UI/UX manifests validate for every task and trigger, read the skills, never read TL On-Demand section 3 or `Clean_Code_Rules.md` | Enumerate remaining `layouts.target` in `read-routing.json`; `test_read_manifest.py` (InstalledTests) | Remaining overrides are Developer rows, the pre-existing TL review row and `tl_implementation_3` (off); 31 tests OK |
| AC5 | `Project_Priming_template.md` section 6 is a pointer; `Document_Index_template.md` is the single path list | Read both; diff Document_Index | Section 6 is one pointer paragraph; index absorbs the former paths |
| AC6 | Bundle regenerated; `build_bundle.py --check` and `generate_common_blocks.py --check` exit 0 | Run both on the head worktree | Both exit 0 |
| AC7 | All existing gates exit 0 | validate_templates, validate_internal_harness, generate_wrappers --check, test_internal_harness, scripts/test/run.sh | All exit 0 |

## Error and edge cases

- Seeded negative: appending `Clean_Code_Rules.md` to the QA Bootstrap template fails `Phase2OtherRolesPointerTests`.
- Seeded negative: restoring the "Docs or config only | Exempt" row in the TL On-Demand template fails the same class.
- Frozen `.claude/agents/templates/` corpus untouched (`git diff --stat` empty).
- Developer target rows keep their `layouts.target` overrides until ST-000311.
- Strict mode and other providers covered by the `test_read_manifest.py` provider/mode matrix.
