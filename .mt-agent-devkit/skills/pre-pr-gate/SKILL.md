---
name: pre-pr-gate
description: Local checks before any implementer (Developer, TL or QA) opens a PR - checks by change type, aggregate local-CI command, short-circuiting gates, production-build evidence, local-verify, rename sweep, PR check note and pre-merge checklist. Load before opening a PR and before each fix push.
---

# Pre-PR Gate

**Requires:** `credential-gate` (a check needs a missing secret), `change-metadata` (devkit CHANGELOG entry)

**Gate:** all applicable checks pass before a PR opens. No exceptions, and the same rule applies to every implementer role.

## 1. Checks by Change Type

| Change | Command | Pass |
|---|---|---|
| `.sh` files | `bash -n <each changed .sh file>` | zero errors |
| `.ps1` files | `powershell -Command "& { $null = [System.Management.Automation.Language.Parser]::ParseFile('<script>', [ref]$null, [ref]$null) }"` | zero parse errors |
| `.github/workflows/` | validate YAML syntax, job structure and step ordering | correct YAML |
| `.mt-agent-devkit/**`, any provider `harness/**`, internal working wrappers/skills, root entrypoints | `python scripts/validate_internal_harness.py`, `python .mt-agent-devkit/scripts/generate_wrappers.py --check`, `python .mt-agent-devkit/scripts/generate_common_blocks.py --check`, `python -m unittest scripts.test.test_internal_harness` | all exit 0 |
| Any of the above, `.claude/agents/templates/**` or `.claude/agents/workflows/**` | `python scripts/validate_templates.py` and `bash scripts/test/run.sh` (see `docs/Template_Test_Strategy.md`) | both exit 0 |
| Docs only, outside every CI and harness path | none | exempt; shared harness Markdown is never docs-only |

The optional `--migration-preservation` audit belonged to the migration only; never require it for later releases.

## 2. How to Run Them

1. **Aggregate first.** If the repo has one entry point that runs the full local check set (resolve it from the project's priming or command surface), run that. Only without one, run the gates individually **in the order CI runs them**.
2. **Short-circuiting gates.** If a gate CI runs earlier fails or was never run, no later result is evidence. Fix it and re-run from that gate onward.
3. **Long checks** use `.mt-agent-devkit/contracts/Local_Verify.md` (local-verify) with the full command, selected provider bindings and a new run ID. Launch once; resume only supported waits on that identity. Missing completion is not success.
4. **Production build.** If the change depends on bundling or chunk splitting, asset/stylesheet injection order, CSS cascade between separate stylesheets, minification or tree-shaking, or code compiled out of one build mode, a dev-server observation is not evidence: verify a production build and report that observation.
5. **Rename or delete sweep.** When a file, path or section is renamed or deleted, grep the repo for the old name and fix every live reference before the PR.
6. **Missing credential.** Stop and report through `credential-gate`; never substitute a dummy value and call it verified.

## 3. PR Note

Add a one-line check result to the PR description (e.g. "bash -n check — PASS on all .sh files"), naming which path was taken: the aggregate command or individual gates in CI order.

## 4. Pre-Merge Checklist

1. All applicable checks above pass.
2. PR titled `[ST-XXXXXX][DEVKIT] Story title`.
3. `CHANGELOG.md` updated before the PR opened (`change-metadata`).
4. TL reviewed and approved the PR.
5. QA validated every AC on the dev branch.
