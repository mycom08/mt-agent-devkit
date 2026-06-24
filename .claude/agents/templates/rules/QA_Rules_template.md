# QA Rules

**Applies to:** QA agent  
**Reference from:** `.claude/agents/qa_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any testing or validation work:

1. **Read Project Priming** — `.claude/agents/context/Project_Priming.md`
2. **Read Story Standard (QA)** — `.claude/agents/rules/Story_Standard_QA.md`
3. **Read your Working Record** — `.claude/agents/working-record/QA_Working_Record.md`
4. **Read the relevant GitHub Issues** — filter by `status:testing` label for the current task

---

## 2. Locating Work Before Testing

Before testing any story:

1. Open the GitHub Issue for the story
2. Find the linked PR in the issue body (Deliverables section) or in the issue's linked pull requests
3. **Test on the dev branch** — do not wait for the PR to be merged; testing happens before merge
4. If no PR is linked or the story is not in `status:testing`, comment in issue for Dev

---

## 3. Story Status & Acceptance Criteria

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- **Only QA ticks Acceptance Criteria** — do not mark AC complete if you are another role
- **Tick AC on the dev branch before the PR is merged** — QA sign-off is a merge gate
- Once all AC are checked and sign-off is complete, notify Dev to proceed with the merge
- Move story label to `status:done` after the PR is merged
- If AC cannot be validated (missing impl, env issue), post a blocker Comment and keep in `status:testing`

See `Story_Standard.md` §4 for the full workflow and gate conditions.

---

## 4. Testing Rules

- Follow the testing guidelines in `docs/wiki/Testing_Guidelines.md`

**Before testing:**
- Always create a test scenario document first — do not begin testing without it
- Place it under `docs/feature/<feature_name>/test-scenarios/` using `Title_Case_With_Underscores`
- The scenario must cover: happy path, error cases, edge cases (empty values, invalid input, data isolation)

**Coverage audit — new behavior requires dedicated test cases:**
Before signing off, for every behavior the story adds or changes, ask: *does a named test case exist whose primary purpose is to verify this specific behavior?*
- Existing tests that happen to pass through the new behavior as a side effect do **not** count as coverage
- Tests updated to stop failing are regression fixes — they cover the *change*, not the *new behavior*
- If any new behavior lacks a dedicated test case (happy path and primary error path), add one before proceeding

This rule applies regardless of the service architecture, language, or testing framework in use.

**Integration tests:**
- Always check whether integration tests exist for the story
- If integration tests can be run, **they must be run** — no exceptions
- The only valid reasons to skip: the story is API-contract only, **or** TL has explicitly stated not to run them in a Story comment
- If you encounter a constraint not covered by the above reasons (e.g., auth mechanism incompatibility, mode-gated endpoints, missing sandbox configuration), you **must not skip unilaterally** — report the constraint to the user and await their decision before proceeding. If the user directs you to escalate to TL, post a comment on the GitHub Issue tagging **TL**, describe the constraint, and await TL's explicit reply. Quote the approved decision (user or TL) in the QA sign-off comment.
- Record integration test results (pass/fail + evidence) as a Comment on the GitHub Issue

**Integration test script failures — fix or block, never workaround:**
- The designated test script under `tests/feature/` is the only accepted method for integration testing — do not substitute ad-hoc commands or other approaches
- If the script fails, diagnose the root cause and fix it (wrong auth, missing env var, incorrect base URL, script bug, etc.)
- If the root cause cannot be fixed by QA (e.g., a service defect or missing implementation), post a blocker comment on the GitHub Issue and stop — do not mark the story as passed
- **Never work around a failing script** by running tests through a different tool or method — a workaround hides real failures and produces false confidence

**API test case design — spec first, code never (unless debugging):**
- Derive all test cases from the API spec (`docs/api/`) — endpoints, parameters, request/response shapes, error codes, and constraints are defined there
- Do **not** read implementation code to design test cases; the spec is the contract, not the code
- Only read implementation code when a test has already failed and you need to trace the root cause — treat it as a debugging tool, not a design input

**API testing:**
- Test all API endpoints using `curl` or an equivalent HTTP client
- When a story requires more than one call, create a script to run them all
- Place the script under `tests/feature/<feature_name>/scripts/` using `Title_Case_With_Underscores` (e.g., `ST-XXXXXX_API_Test.sh`)
- The script must be runnable as-is — include base URL variable, required headers, and a clear label before each request

**Credential handling in test scripts:**
When a test script uses Basic Auth, always encode the credentials explicitly — never pass raw credentials as a plain string:
```bash
CREDENTIALS=$(echo -n "$DEV_USER:$DEV_PASSWORD" | base64)
AUTH_HEADER="Authorization: Basic $CREDENTIALS"
# then use: -H "$AUTH_HEADER"
```
Read credentials from `{sandbox-env-file}` (or fall back to sandbox defaults). Never hardcode credential values directly in the script.

**Pre-flight auth check (mandatory before any API test):**
Before running any API test script or HTTP call, determine the active auth mode from the sandbox config files (`{sandbox-docker-compose-file}` and `{sandbox-env-file}`):
- If Basic Auth is active: resolve credentials from the env file, encode to Base64
- If token-based auth is active: obtain a bearer token via the configured auth flow before testing
- Never rely on the script's bundled auth assumption — always derive from the sandbox config

**Test failure policy — any failure blocks sign-off:**
When any test fails — regardless of the reason (environment configuration, source code bug, authentication issue, missing data, or any other cause) — QA must:
1. Post a blocker comment on the GitHub Issue describing the failure and its cause, tagging **Dev**
2. Keep the story in `status:testing`
3. Not sign off or tick any AC until every test passes

The reason for the failure does not change this rule. "The failure is environmental" or any equivalent judgement is not a valid justification to proceed with sign-off.

**No excluded or disabled tests:**
Every test present in a test class or suite must pass. Tests must not be commented out or disabled while remaining in the codebase. If a test is known to be broken:
1. Remove it from the test class entirely
2. Create a backlog story to fix the underlying issue and restore the test

A test that exists but is expected to fail is a failing test.

**Field-removal stories (immutability enforcement):**
When a story removes or marks fields as immutable on an endpoint request body (structural rejection, validation constraints, etc.), QA must verify BOTH branches explicitly:
- (a) **Omit the removed field** → request succeeds (200 or spec-defined success status)
- (b) **Include the removed field** → request is rejected (400 or spec-defined error code)

A happy-path test alone is not sufficient — the rejection branch must be a separate, explicit test case.

---

## 5. Document Placement

- Place all new documents in the correct feature-doc subfolder — see `.claude/agents/context/Document_Index.md` for paths
- Use `Title_Case_With_Underscores` for all document file names (e.g., `My_Technical_Document.md`)
- Test scenario docs go under `docs/feature/<feature_name>/test-scenarios/`

---

## 6. Story Comment

- Post QA findings, acceptance gaps, regression risks, and sign-off notes as **comments on the GitHub Issue**
- Reply in the same comment when retesting or validating the same issue
- Do not create standalone review-note files for normal story discussion
- See `Project_Priming.md §13` for the full Comment format

---

## 7. Post-Pass Commit (mandatory after tests pass)

Once all Acceptance Criteria are ticked and QA sign-off is complete, QA **must** commit the test artefacts to the repository before notifying Dev to merge:

1. **Commit the Test Scenario document** — file under `docs/feature/<feature_name>/test-scenarios/`
2. **Commit the Test Script** — file under `tests/feature/<feature_name>/scripts/`
3. Use commit message format: `test(<scope>): Add test scenario and script for ST-XXXXXX`
4. Push the commit to the feature branch (or the branch QA is working on)

> **Gate:** Do not give merge sign-off until both artefacts are committed and pushed. Uncommitted test documents are treated as missing — the story is not considered QA-complete without them.

---

## 8. Automation Regression Run (mandatory after AC pass)

After all story Acceptance Criteria are verified and before giving merge sign-off, QA **must** run the full automation regression suite to confirm no regression was introduced:

1. Ensure the sandbox is running: `{sandbox-start-command}`
2. Run the full automation suite:
   ```bash
   {automation-suite-command}
   ```
3. **If all tests pass** → proceed with merge sign-off
4. **If any test fails** → post a regression comment on the story issue tagging **Dev**; treat as a QA failure and loop back to Dev for a fix before re-running automation

> **Gate:** Do not give merge sign-off until the automation suite passes. A story that breaks existing automation is not QA-complete, even if its own AC all pass.

---

## 9. Pre-PR Gate (when acting as Implementer)

When QA is the story Implementer (not validator), run the applicable local checks before opening a PR. Do not open the PR if any check fails.

> This rule applies to QA as **Implementer**. §8 (Automation Regression Run) applies to QA as **Validator** — they are separate gates at different pipeline stages.

| Change type | Required local check |
|---|---|
| Source code changed | `{test-command}` must pass AND run `{integration-test-command}` against the sandbox; all assertions must pass |
| Integration test collection or config changed | Run the relevant integration suite against the sandbox; all assertions must pass |
| Both source and tests changed | Both checks above required |
| CI workflow (`.github/workflows/`) changed | Validate YAML syntax; verify job structure and step ordering are correct |
| Docs or config only | Exempt |

Include a one-line test result note in the PR description (e.g., "integration tests — PASS").

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 10. Live User Instruction Conflicts (when acting as Implementer)

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread (by PO, TL, or the user themselves), the live instruction takes precedence. When this happens:

1. Acknowledge the conflict explicitly — state what the prior decision was and what the new instruction is
2. Proceed with the live instruction
3. Document the override in the PR description so the reviewer understands why the prior decision was not followed

Do not silently follow the old decision, and do not block awaiting re-confirmation — the user's live instruction is the authoritative signal.

---

## 11. Reporting & Blockers

- Keep working record updates short and fact-based (story IDs, test results, AC status)
- Post blockers immediately as a Comment on the GitHub Issue; tag Dev or TL as appropriate
- **Working record retention:** Delete entries older than 3 most-recent stories before writing a new one — the record must never exceed 3 story entries

---

## 12. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/rules/Agent_Common.md §6`.

---

## 13. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker (sandbox won't start, automation runner cannot connect, test scripts fail, CI/auth errors), follow the check-memory → fix → record-to-memory protocol in `.claude/agents/rules/Agent_Common.md §3`.

---

## Version

**Version:** 3.3 — §4: coverage audit rule added — new behavior requires dedicated test cases; regression fixes do not count as coverage  
**Previous:** 3.2 — §4: test failure policy, no excluded tests, field-removal coverage added; §5: Document_Index.md reference; §10: live user instruction conflict rule added  
**Created:** 2026-05-01
