# ST-000379 Test Scenarios: Plan Sprint sprint-label check

Story: issue 379. PR: 382. Head under test: 72f79f1c9ae1c43deafb14b23e417757e16fcb1a.

Method: inspection of the devkit and shipped sources, the GitHub listing query run read-only and against fixtures, and the repository gates. No live Plan Sprint run.

| ID | AC | Scenario | Expected |
|---|---|---|---|
| T1 | AC1 | Order of the check in the devkit and shipped Plan Sprint workflows and `po-plan-sprint` skills | Runs before any other planning step |
| T2 | AC1 | Rules in `sprint-status` section 6 compared with the ST-000368 label criterion | `backlog` has no sprint; open, ready, in-progress, review, testing, hotfix, blocked have exactly one; done and on-hold not checked |
| T3 | AC1 | Fixtures: backlog with sprint, open with none, ready with two, blocked with none | Each is a violation and is listed to the user |
| T4 | AC1 | Fixtures: compliant issues, done, on-hold, issue with no status label | No violation |
| T5 | AC1 | Strict mode: rule applied to `**Status:**` and `**Sprint:**` | Covered by the shipped skill and workflow |
| T6 | AC2 | Open topic: blocked, no sprint, `analysis-open-topic` label; strict: `**Analysis Open Topic:**` line | Skipped |
| T7 | AC3 | One or more violations | All reported, user asked whether to continue; declining stops |
| T8 | AC3 | No label or story field change without confirmation | Stated in workflow and skill |
| T9 | AC3 | No violation | Planning continues without a question |
| T10 | AC4 | Shipped templates, bundle, `changes.json`, `CHANGELOG.md` | All updated and consistent |
| T11 | AC4 | Harness, wrapper, common-block, template, bundle and script gates; CI at head | All pass |
| T12 | AC4 | Remove the check line from a workflow copy and run the new test | Test fails |
| T13 | Regression | Existing sprint-status sections, size limits, `init` and `sync` fixtures | Unchanged behavior |
