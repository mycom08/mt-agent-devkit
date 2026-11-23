---
name: qa-regression
description: QA regression check before sign-off - blast radius, init project and sync devkit impact, the template and harness regression suites, the local-verify contract and the CI-equivalent exception. Load once every AC is verified, before sign-off.
---

# QA Regression

**Requires:** `qa-core`, `raise-question` (blockers)

Mandatory before merge sign-off. For long local verification use `.mt-agent-devkit/contracts/Local_Verify.md` (local-verify) with the full required command, the selected provider bindings and a new run ID. Launch once; resume only supported waits on that identity. Missing completion is not success. Keep provider-local logs and independent verification gates.

After all story AC are verified, run the full automation regression suite:

1. Start the sandbox: `{sandbox-start-command}`.
2. Run `{automation-suite-command}`.
3. All tests pass: proceed to merge sign-off.
4. Any test fails: post a regression comment on the story issue tagging **Dev**; treat it as a QA failure and loop back for a fix before re-running.

**Gate:** no merge sign-off until the automation suite passes. A story that breaks existing automation is not QA-complete, even when its own AC pass.

**No-skip rule:** QA cannot skip or self-approve skipping the run. If the sandbox cannot start or the suite cannot run, post a blocker comment on the story and escalate to the user; no sign-off until the user approves the skip or the issue is resolved. "Sandbox not in scope for this session" is not a justification.

**CI-equivalent exception:** when the Technical Scope is `.github/workflows/**` only and the CI run QA is watching already runs a job equivalent to the suite (for example `build-and-test` with the same command), cite that passing job instead of also running the suite locally. It never applies to a story that touches source, schema or test files.
