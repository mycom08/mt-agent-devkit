# ST-000246 Test Scenarios: Analyze Requirements Workflow

PR 356, head feed9b09cffacc39eef781443886092302fa5caa. Python via `python3` shim, `LC_ALL=C.UTF-8`. Gates and installs ran in scratch worktrees and targets.

Scope note: the AC numbers below are the original twelve. A user scope split moved AC3-AC10 to ST-000357 (issue 357), still NOT VERIFIED. The original AC1, AC2, AC11 and AC12 are now AC1-AC4 of ST-000246; their gates were rerun at the same head.

| # | AC | Scenario | Expected | Result |
|---|---|---|---|---|
| 1 | AC1 | Inspect shared and variant templates, trigger row, `changes.json`, bundle | all present and consistent | PASS: all present; bundle current (`build_bundle.py --check` exit 0) |
| 2 | AC1 | Scratch install of github and strict at head; upgrade from base bc688e5 | one compiled workflow per mode with the trigger row | PASS: github and strict, claude, antigravity and codex; offline sync path from bc688e5 added the workflow, equal to a fresh install |
| 3 | AC2 | Document index rows, template and installed | analysis folders listed | PASS for the template; note: the target index is project owned, sync kept the existing one without the new rows |
| 4 | AC3-AC8 | Inspect each rule and resolve every path, skill and section it cites in the installed targets | rules complete; references resolve | PASS as inspection only: cited paths, skills, BA section 6 and policies resolve; does not verify behavior |
| 5 | AC7, AC9, AC10 | Execute intake Git steps in a scratch repo: inspect, create, `.gitignore`, local exclude, branch switch, second preflight | preflight accepted; `tmp/` never tracked or shown | PASS (Git steps only): clean on the base branch, next preflight PASS; control without the exclude line BLOCKED. `gh` story and PR steps not run |
| 6 | AC10 | Edge: existing `.gitignore`, folder without `State.md`, linked worktree exclude path | nothing overwritten; path resolves | PASS for the exclude path (linked worktree, subdirectory). Existing-folder and never-overwrite handling: NOT VERIFIED (needs a run) |
| 7 | AC3-AC10 | Run the workflow with an agent in a target project, both modes | behavior matches the AC | NOT VERIFIED: needs a live run (user, BA and PO agents; a disposable GitHub repository for github mode) |
| 8 | AC11 | Sweep for standalone `analyze` triggers; Build Software still calls the workflow | none left | PASS: no standalone trigger left; Build Software still reads the workflow |
| 9 | AC12 | Gates and regression suites from a worktree at the head | all exit 0 | PASS: all exit 0; 110 harness tests, run.sh 281 tests (1 skipped), fixtures 17/17 |
