# ST-000290 Test Scenarios

Revision under test: `0eed284378a60923d44306b7f435d307c1951bd3` (PR 296). Modes: github and strict; providers: claude, antigravity, codex.

| ID | Scenario | Expected | Result |
|---|---|---|---|
| S1 | Inspect built `deployment.json` for the 3 retired PO files | 15 retirement entries (shared + claude/antigravity x github/strict), `required` explicit, survivors = shared `skills/po-*` + `product_owner_instructions.md`; no PO template/asset in bundle | PASS |
| S2 | Stock receipt file (adapted false, stock hash present, hash == rendered) | auto-resolved, `after_sha256` null, reason `stock retirement in <version>`, listed as `generated retirement:` | PASS (6 provider/mode combos) |
| S3 | Missing `adapted`, missing `stock_sha256`, stock file edited after install | stay conflict, target unchanged | PASS |
| S4 | `adapted: true` retired file via sync; adapted and edited; raw `deployment.plan` without resolution | porting conflict (sync) / exact-resolution conflict (engine); nothing deleted | PASS |
| S5 | Adapted file with bad `before_sha256`, non-null `after_sha256`, empty reason, partial paths | conflict, target unchanged; exact reviewed resolution for every path deletes | PASS |
| S6 | v0.1.48/49/50 fixtures x provider x mode x bridge stamp, manual reviewed resolution | no PO rule file remains, `po-*` skills + wrappers present | PASS |
| S7 | Inject retired-file citation into a Phase 2 template and a bundle asset | `validate_retired_citations.py` exits 1; clean tree exits 0 | PASS |
| S8 | Sync workflow template and CHANGELOG | describe porting step and sync between sprints | PASS |
| S9 | All gates (internal harness, wrappers, unittest, templates, run.sh, build_bundle --check, read_manifest) | exit 0 | PASS |
