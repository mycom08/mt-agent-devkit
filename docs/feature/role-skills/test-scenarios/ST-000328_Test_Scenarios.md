# ST-000328 Test Scenarios — Technical Lead Skills (internal)

**Story:** ST-000328 (issue #328), PR #339, head `ee4d058f9eab3bb30c5e1cfbfe6419bffe9a084d`
**Type:** behavioral (harness routing and rule ownership). **Mode:** github, internal layout, provider claude.
**Date:** 2026-11-20

## Scenarios

| ID | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| S1 | 1 | Compare every rule in base `Technical_Lead_Rules_Bootstrap.md`, `Technical_Lead_Rules_Read_On_Demand.md`, `Story_Standard_TL.md` with the six `tl-*` skills | Every TL-only rule is in `tl-core`, `tl-design`, `tl-review`, `tl-answer`, `tl-implement` or `tl-anchor`; common rules stay in common skills | PASS |
| S2 | 2 | Walk Ownership Map section 12a and 12b against the base files | Each rule has one owner and a change class; dropped rows are history only | PASS |
| S3 | 2 | Edge: the weakened-rule check (Testing row, UI prototype note, `gh api` alternative) | Each deviation is named in the map | PASS |
| S4 | 3 | Build TL manifests (implementation, review, review+`design_standards`, question) | Every source exists, no retired file, every `after` resolves, `tl-core` plus the task skill read | PASS |
| S5 | 3 | Three internal TL files and their wrappers absent; `retired` entries in `migration-inventory.json` | Files absent from every provider; entries present with `retired_by: ST-000328` | PASS |
| S6 | 3 | Negative: append a citation of a retired file to a skill and to the instructions file | `validate_retired_citations.py` exits 1 naming file and line (restored after) | PASS |
| S7 | 4 | `tl-review` requires `pr-review`; `pr-review` line 10 points to `tl-review`; load map says `pr-review` first | All three hold | PASS |
| S8 | 5 | Recompute bytes and calls with `read_manifest.py` at head and at base `ee4d058^` | Match `TL_Skills_Measurement.md` | PASS (review-before by components) |
| S9 | 6 | Run the four gates plus the template and citation validators | All exit 0 | PASS |
| S10 | regression | `bash scripts/test/run.sh`, `validate_templates.py`, full `scripts/test` unittest discovery | All exit 0 | see report |

## Notes

- Target templates are out of scope (ST-000329); the registry keeps `layouts.target` sources, so installed targets are unchanged.
- Environment: only `python3` on PATH; a scratchpad `python` shim and `LC_ALL=C.UTF-8` were used.
