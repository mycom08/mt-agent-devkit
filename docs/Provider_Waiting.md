# Provider-aware waiting

ST-000217 adds bounded CI evidence and launch-once local verification to the
active Phase 2 distribution. Canonical usage lives in
[CI Watch](../.mt-agent-devkit/contracts/Wait_Work.md) and
[Local Verification](../.mt-agent-devkit/contracts/Local_Verify.md).
Provider-local skills point to the same shared helpers; installed receipt/state
bindings determine where identities, evidence and private logs belong.

CI aggregates visible check contexts and Actions workflows, protected required
contexts and applicable required-status rules. Explicit `--required-check`
inputs cover additional expected names. Missing names remain pending; a passed
single run cannot hide pending/failing required checks. PR inputs bind the
first full head SHA. Commit inputs include third-party check-runs and statuses,
but carry `approval_scope: commit-only` and cannot substitute for PR review.

The helper returns evidence, not a merge decision. Earlier passing runs remain
NO RUN candidates with changed-file scope for the existing explicit zero-check
exception. Review/merge still require exact-head and approval-scope validation,
current acceptance evidence, and independent Technical Lead/QA judgment.

| Evidence category | Coverage / limitation |
|---|---|
| Deterministic CI fixtures | PASS, FAIL, cancellation/timeouts, expected/missing checks, multiple workflows including identical display names, saturated results, pending windows, delayed discovery, stale heads, prior scope, repeated waits, authentication/network errors |
| Deterministic local fixtures | Real subprocess success/failure/exit124, missing ID, launch failure, pending/repeat, no duplicate launch, provider confinement, redacted private logs, bounded summaries |
| Mechanical deployment | Claude/Antigravity/Codex × GitHub/strict × repository/project-root profiles; deployed helpers exercised, skills and shared contracts installed, existing runtime history preserved |
| Observed native Codex | Shared helper executed against live GitHub evidence; long local aggregate launched once through `exec_command`, returned a session ID and used its supported completion wait |
| Native Claude | Not executed in this session. Use the selected adapter's verified Bash/completion API and bounded foreground fallback; installation fixtures do not certify wakeup |
| Native Antigravity | Not executed; command/wakeup mapping remains unverified here. Inspect enabled schemas or report unavailable. An available foreground shell supports the sequential fallback |

Native evidence records are provider-local and excluded from Git. No paid or
unavailable external runtime is an acceptance prerequisite. Ending a worker turn
is never asserted to wake it later. Bounded windows retain the original command
and run identity; waiting never launches duplicate verification or shortens the
project's required suite. Strict local operations never invoke GitHub.

The inspected sibling-project experimental scripts informed silent waiting and
compact summaries. The actual referenced commit `940e212` was available. Its
single-run selection, automatic earlier-run PASS, global temporary IDs and
reactive-wakeup claims were not copied. An unseen follow-up commit is not
certified. Historical `.claude/agents/templates/` remains unchanged.

GitHub evidence interfaces: [CLI required-check selection](https://cli.github.com/manual/gh_pr_checks)
and [active branch rules](https://docs.github.com/en/rest/repos/rules#get-rules-for-a-branch).
Unsupported required-workflow rules and incomplete/truncated evidence fail
closed. Authentication/network recovery never rewrites credentials or proxies.
There is no measured token-savings claim.
