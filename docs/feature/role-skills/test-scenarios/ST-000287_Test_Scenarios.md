# ST-000287 Agent-Security Skill Test Scenarios

## Scope and acceptance

Validate the shared `agent-security` skill: canonical file, generated discovery wrappers, generated inline blocks in Core/Bootstrap and their Phase 2 templates, the orchestrator load, the Phase 0 ripple and the gates. Source under test: PR 293, branch `ST-000287/agent-security-skill`, functional head `2f5e793556ea30bca860c2a8dc90be9e0484aee9` (the TL Approved-SHA). Result: AC1-AC6 PASS. Python gates ran with a PATH shim (`python` -> `python3`) outside the repo.

## Scenarios

| AC | Scenario | Input / action | Required result | Result / evidence |
|---|---|---|---|---|
| AC1 | Happy path | Inspect `.mt-agent-devkit/skills/agent-security/SKILL.md` | `name`/`description` frontmatter; parts A, B, C; Shell Safety full-read rule in C; credential gate untouched | PASS; 2435 bytes, limit 2560; diff of Core/Bootstrap against main shows only added markers |
| AC2 | Happy path | `generate_wrappers.py --check`; inspect `.claude/`, `.antigravity/`, `.codex/` skills and bundle `deployment.json` | Frontmatter plus one pointer line per provider; bundle ships shared managed canonical plus three wrappers | PASS; exit 0; bundle canonical `cmp`-identical; 408-byte wrappers with `name: agent-security` |
| AC2 | Error case | Rename `name:` in a scratch-worktree `.claude` wrapper | `generate_wrappers.py --check` and `validate_internal_harness.py` fail | PASS; both exit 1 |
| AC3 | Happy path | `generate_security_blocks.py --check`; inspect CI step in `validate-templates.yml` | Blocks in Core, Bootstrap and both templates equal the skill byte-for-byte; check runs in CI | PASS; exit 0; CI step and `.codex/skills/**` path trigger present |
| AC3 | Error / edge case | One-character change inside each of the 4 generated blocks, then in `SKILL.md` (scratch worktree) | `--check` exits 1 with block drift; restoring returns exit 0 and a clean tree | PASS; 5 of 5 perturbations exit 1; restored exit 0; worktree removed, primary tree clean |
| AC3 | Edge case | Search generated blocks and Bootstrap for the Shell Safety reference | Part C not inlined | PASS; 0 inside blocks, 0 in Bootstrap; Core's one mention is the pre-existing §1, outside the blocks |
| AC4 | Happy path | Read `orchestrator_instructions.md`, `Sprint_Workflow.md`, Phase 2 shared templates | Skill and Shell Safety loaded at workflow start; load recorded in pipeline state | PASS; paragraph at line 14; `**Security Skill:**` line in the Sprint state format |
| AC4 | Edge case | Order check; grep `read-routing.json` and `read_manifest.py` | Load precedes the first `gh issue`/`gh pr` reference; no manifest entry | PASS; no `gh` reference before line 14; 0 `agent-security` matches in routing files |
| AC5 | Happy path | Check Core/Bootstrap §2 and §4 headings; grep citations; parse `ST-000264_Common_Ownership.json` | Every citation resolves; moved ownership recorded; worker text unchanged | PASS; headings present; JSON valid; owners now SKILL.md parts A/B |
| AC6 | Happy path | Run all gates at head | Every gate exits 0 | PASS; `generate_security_blocks.py --check`, `generate_wrappers.py --check`, `python3 .mt-agent-devkit/distribution/phase2/build_bundle.py --root . --output .mt-agent-devkit/distribution/phase2/bundle --check` (180 assets, 568 files), `validate_internal_harness.py`, `unittest scripts.test.test_internal_harness` (37 OK), `validate_templates.py`, `bash scripts/test/run.sh` (10 passed) |

## Notes and limitations

- The `build_bundle.py` path in the original brief (`.mt-agent-devkit/scripts/`) was wrong; the script lives under `.mt-agent-devkit/distribution/phase2/`.
- Non-blocking observations: `Refine_Sprint_Workflow.md` state format lacks a `**Security Skill:**` line; `build_bundle.py --check` is not in CI.
- This is a behavioral guidance and generator story with no runtime service; native provider skill discovery is not exercised (Codex has no verified discovery), only file and frontmatter validity.
- Validation report: issue 287 comment `6540754557`.
