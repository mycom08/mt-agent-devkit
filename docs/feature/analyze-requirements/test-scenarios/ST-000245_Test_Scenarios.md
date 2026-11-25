# ST-000245 Test Scenarios: Shared Document Formats

PR 355, head 416ea9c3ca1c488ef5fc9a61a4284013824749ed. Python via `python3` shim, `LC_ALL=C.UTF-8`. Gates and mutations ran in scratch worktrees; installs used the claude provider and placeholder project content.

| # | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| 1 | AC1 | Inspect BA spec format, canonical and shipped; bounded section read of canonical section 7 despite `##` lines inside the example | all required contents; full section returned | PASS |
| 2 | AC2 | Inspect ADR format, canonical and shipped | five NFR headings; TBD, blank, reasonless N/A rejected; no approval without section | PASS |
| 3 | AC3 | Inspect `qa-test-docs`, canonical and shipped | strategy and design formats, applicability rule, approvers | PASS |
| 4 | AC4 | Inspect `gate-verdict`; trace how PO and TL reach it, in the repo and after install | verdict format, `gh pr comment`, no `gh pr review --approve`, strict equivalent | PASS (note: no PO load-map pointer, per TL decision) |
| 5 | AC5 | Header on spec, ADR, strategy, design; dual approval for test documents | all four carry it; both approvers, later time | PASS |
| 6 | AC6 | Remove each NFR heading from the shipped section and run the validator | non-zero exit naming the heading | PASS: exit 1 for each of the five headings |
| 7 | AC6 | Edge cases: heading renamed, demoted, moved outside section, section removed, file removed, canonical-only removal | errors for shipped defects | PASS: all shipped defects exit 1; canonical-only removal passes the validator, parity is covered by a unit test |
| 8 | AC1-AC5 | Scratch install of github and strict modes | skills and wrappers deployed, paths resolve | PASS: also upgrade from facff7c to head in both modes |
| 9 | AC7 | `changes.json`, `CHANGELOG.md`, `VERSION` against `main` | snapshot descriptions only; no version edit | PASS: `build_bundle.py` skill lists changed with no description of its own (note) |
| 10 | AC7 | Gates and regression suites from a worktree at the head | all exit 0 | PASS: all exit 0; 110 harness tests, run.sh 281 tests (1 skipped), fixtures 17/17 |
