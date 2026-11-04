---
name: pre-pr-gate
description: Local checks before any implementer (Developer, TL or QA) opens a PR - checks by change type, aggregate local-CI command, short-circuiting gates, production-build evidence, local-verify, rename sweep, PR check note and pre-merge checklist. Load before opening a PR and before each fix push.
---

# Pre-PR Gate

**Requires:** `credential-gate` (a check needs a missing secret), `dev-verify` (behavioral and endpoint verification)

**Gate:** all applicable checks pass before a PR opens. No exceptions, and the same rule applies to every implementer role. Never open a draft PR expecting QA or TL to catch failures.

## 1. Checks

| Check | Applies when | Command | Pass |
|---|---|---|---|
| Build | Always | `{build-command}` | Zero errors |
| Unit tests | Always | `{test-command}` | All tests pass |
| Lint / format | Any source or test file changed, **including test files you just authored** | `{lint-command}` | Zero errors |
| API spec lint | Spec changed (`docs/api/{api-spec-file}` or lint config) | `{api-lint-command}` | Zero errors |
| API spec drift | Spec changed and code generation is used | `{code-gen-command}` then `git diff --exit-code {generated-file-path}` | No diff |
| Integration tests | Source code changed | `{integration-test-command}` (start the sandbox first) | All assertions pass |

A behavioral change, or a story with an existing integration script, also runs `dev-verify` section 3 before the PR; for affected endpoints confirm the `dev-verify` section 2 spec match before merge.

## 2. How to Run Them

1. **Aggregate first.** If the repo has one entry point that runs the full local check set (resolve it from the project's priming or command surface), run that. Only without one, run the gates individually **in the order CI runs them**.
2. **Short-circuiting gates.** If a gate CI runs earlier fails or was never run, no later result is evidence. Fix it and re-run from that gate onward.
3. **Long checks** use `.mt-agent-devkit/contracts/Local_Verify.md` (local-verify) with the full command, selected provider bindings and a new run ID. Launch once; resume only supported waits on that identity. Missing completion is not success.
4. **Production build.** If the change depends on bundling or chunk splitting, asset/stylesheet injection order, CSS cascade between separate stylesheets, minification or tree-shaking, or code compiled out of one build mode, a dev-server observation is not evidence: verify a production build (the project's own build and preview commands) and report that observation.
5. **Rename or refactor sweep.** When a story renames or refactors (title or scope says so, or a function, class, constant, file or path is renamed or deleted), run `grep -rn "<old-name>" docs/` and over the source tree, and fix every stale reference before the PR.
6. **Missing credential.** Stop and report through `credential-gate`; never substitute a dummy value and call it verified.

## 3. PR Note

Add a one-line check result to the PR description (e.g. "`{test-command}` — PASS · integration tests — PASS"), naming which path was taken: the aggregate command or individual gates in CI order.

## 4. Pre-Merge Checklist

1. All applicable checks above pass locally.
2. Source files follow the naming convention (`clean-code`).
3. The rename or refactor sweep is done (section 2 step 5).
4. PR titled `[ST-XXXXXX][FEATURE] Story title`.
5. TL reviewed and approved the PR.
6. QA tested on the dev branch and signed off every AC (PO ticks the AC at story closure).
