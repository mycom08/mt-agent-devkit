# ST-000329 Test Scenarios — Technical Lead Skills in Targets

**Story:** ST-000329 (issue #329), PR #340, head `b678322db5b37c222de95b300fe2ef931eeec166`
**Type:** behavioral (target delivery and routing). **Mode:** github, target layout, providers claude, antigravity, codex.
**Date:** 2026-11-20

## Scenarios

| ID | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| S1 | 1 | Phase 2 `tl-*` templates exist; `deployment.json` lists each skill (canonical + 3 wrappers) | 6 templates, 24 bundle entries | PASS |
| S2 | 2 | Build target TL manifests (implementation, review, question, implementation + `design_standards` + `context_anchoring`) from each installed target | Read `tl-core` plus task skill; no `Technical_Lead_Rules_*` or `Story_Standard_TL`; every source exists | PASS |
| S3 | 2 | Registry: TL rows carry no `layouts.target` override naming a TL file; TL instructions template has a Load Map and no legacy citation | Only non-TL target overrides remain | PASS |
| S4 | 3 | `lifecycle.sh init` into a fresh temp target for claude, antigravity, codex | Six skills and own-provider wrappers; no foreign wrappers; status verified | PASS |
| S5 | 3 | Install base `main` first (no TL skills), then `lifecycle.sh update` with the PR head, per provider | Skills absent before, present after; status verified | PASS |
| S6 | 4 | `changes.json` unreleased entry and `CHANGELOG.md` | Both record ST-000329 | PASS |
| S7 | 5 | `validate_templates.py`, `run.sh`, harness validator, wrappers check, common blocks check, internal unittest, retired citations | All exit 0 | PASS |
| S8 | edge | Legacy TL files still ship unread until ST-000330 | Present in target, absent from every manifest | PASS |
| S9 | gap | Three legacy target rules vs the skills (non-zero test count, TL `BREAKING CHANGE:` footer, NFR design questions in the CI skip list) | Not in any AC; route to ST-000330 | NOTED |

## Notes

- Environment: only `python3` on PATH; a scratchpad `python` shim was used. Temp targets and a base worktree were disposable and removed.
