# ST-000332 Test Scenarios — QA Skills in Targets

**Story:** ST-000332 (PR 343, head `1072b19`, base `49c5ae6`) — **Feature:** `role-skills` — **Mode:** github
**Method:** read the changed templates, registry and bundle; run each gate in a detached worktree at the head SHA (`python` shim to `python3`, `LC_ALL=C.UTF-8`).

| # | AC | Scenario | Type | Expected | Result |
|---|---|---|---|---|---|
| 1 | 1 | Five `qa-*` Phase 2 templates exist, frontmatter equal to the internal skills | Happy | `qa-core`, `qa-validate`, `qa-testing`, `qa-regression`, `qa-hotfix` under `templates/skills/<name>/SKILL_template.md` | PASS |
| 2 | 1 | `QA_SKILLS` in `build_bundle.py` is part of `SHARED_SKILLS`; `deployment.json` lists each skill for the shared dir and the claude, antigravity and codex wrappers | Happy | 4 destinations per skill | PASS |
| 3 | 1 | Target text differs from internal only as Ownership Map §16a states (API spec step, scripts commit, project testing rules, automation suite) | Edge | Differences match §16a; the three §15 drops stay dropped | PASS |
| 4 | 1 | No `change-metadata` or legacy QA file reference in the new templates | Error | `grep QA_Rules\|Story_Standard_QA` empty | PASS |
| 5 | 2 | Registry has no QA `layouts.target` override; `standard`, `qa_validate`, `qa_testing` read skills in both layouts; `regression_check` and `post_done_bug` lose `layouts: [internal]` | Happy | Diff shows only removals; `bootstrap`, `common`, `role_sources` gain `target` equal to internal | PASS |
| 6 | 2 | Target QA instructions template has a Load Map and no `QA_Rules_`/`Story_Standard_QA` | Happy | Present; unit test asserts it for every provider | PASS |
| 7 | 2 | Shared Pipeline Stages Stage 3 steps and Story Standard section 9 name the skills (TL CR-1 fix) | Edge | No dangling QA rules citation | PASS |
| 8 | 2 | `validate_retired_citations.py` still passes with registry layouts covered | Error | exit 0 | PASS |
| 9 | 3 | Fresh install per provider (claude, antigravity, codex) delivers the five skills and the Load Map instructions | Happy | `SkillInstallTests` fresh-install test OK | PASS |
| 10 | 3 | `sync devkit` over an install without the QA skills delivers them | Happy | sync test OK, skills present in `.mt-agent-devkit/skills` and `.claude/skills` | PASS |
| 11 | 3 | Legacy QA templates still ship (unread) until ST-000333 | Edge | 15 legacy bundle entries remain | PASS |
| 12 | 4 | `changes.json` `0.1.58-SNAPSHOT` lists the 6 new/changed QA templates, the registry, Story Standard and Pipeline Stages clauses as `[ST-000332] ...` | Happy | Compact clause lists, no narrative | PASS |
| 13 | 4 | `CHANGELOG.md` has one `[ST-000332]` entry under the unreleased section | Happy | Present | PASS |
| 14 | 5 | `validate_templates.py` | Gate | exit 0 | PASS |
| 15 | 5 | `bash scripts/test/run.sh` | Gate | exit 0, 10 passed | PASS |
| 16 | 5 | `validate_internal_harness.py`, `generate_wrappers.py --check`, `unittest scripts.test.test_internal_harness` (100 tests), `generate_common_blocks.py --check`, `validate_retired_citations.py` | Gate | all exit 0 | PASS |
| 17 | 5 | Wider suites `test_phase2_deployment.SkillInstallTests` and `test_read_manifest` (43 tests) | Regression | OK | PASS |
| 18 | 5 | CI run 45111174030 on the head SHA | Gate | Layer-1 invariant check pass | PASS |
