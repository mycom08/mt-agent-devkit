# ST-000307 Test Scenarios

**Story:** ST-000307 (A1, common skills and generated Common blocks) · **PR:** 315 · **Validated head:** 2991de13fe62ff0c59a77802f1e670787b3aaa3d · **Date:** 2026-11-03

| AC | Type | Scenario | Expected | Result |
|---|---|---|---|---|
| AC1 | Happy | Count, size, frontmatter, `Requires:` line and 3 provider wrappers for each of the 17 skills | 17 skills, each at most 4096 bytes (largest `agent-memory` 3999), `name`/`description` present, `**Requires:**` names skills, wrappers exist | PASS |
| AC2 | Happy | Read Ownership Map section 5 | Section lists Claude, Codex, Antigravity and repo names; no collision; `agent-memory` vs `memory` explained | PASS |
| AC3 | Happy | Read `retro` and `retro-contribution` | `retro` holds detection and records on detection; `retro-contribution` is separate, requires `retro`, loaded after a recorded trigger | PASS |
| AC4 | Happy / Error | Run `generate_common_blocks.py --check`; grep for callers of `generate_security_blocks.py` | exit 0; old script absent; no caller (only history text, CHANGELOG and an absence assertion) | PASS |
| AC4 | Error | Scratch worktree: edit a generated block, delete a block, duplicate a block, add a part with no target | each `--check` exits 1; clean tree exits 0 | PASS |
| AC5 | Happy | Run the four unit tests named `test_check_fails_on_*` | differing, missing, duplicated, no-target tests exist and pass | PASS |
| AC6 | Edge | Count generated markers per Common file; compare headings, ids and references with base | 10 Common files carry blocks; headings unchanged; the only reference differences are route-neutral rewordings listed in the map | PASS |
| AC7 | Happy | Read ownership map and `ST-000264_Common_Ownership.json` diff | Every absorbed rule mapped; `current_owner` and `compatibility` updated per generated section | PASS |
| AC8 | Happy | Read Proposal revision 6 | Revision 6 row and text record B, D, A2-P2 (#312) placement and the `layouts.target` overrides | PASS |
| AC9 | Happy | Check `migration-inventory.json` and `generate_wrappers.py --check` | `skill` entry for each of the 17; wrapper check exit 0 | PASS |
| AC10 | Happy | `unittest scripts.test.test_common_capabilities` | 13 tests pass on generated text | PASS |
| AC11 | Regression | Run all gates with a `python` shim | `validate_internal_harness`, `generate_wrappers --check`, `unittest test_internal_harness` (66), `validate_templates`, `run.sh` (10 fixtures), `build_bundle --check`, `generate_common_blocks --check` all exit 0; no change under `.claude/agents/templates/` | PASS |
