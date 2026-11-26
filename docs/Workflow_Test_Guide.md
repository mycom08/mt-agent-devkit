# Workflow Test Guide

How to run a devkit workflow against a real target project. For template and deployment tests see [Template Test Strategy](Template_Test_Strategy.md).

**Ask the user before every run.** Knowing about the testbed is not permission. Agree the spend cap, the permissions and which commands will run.

## 1. Testbed

`mycom08/mt-agent-devkit-testbed` (private, reusable). Do not create another test repo.

- `main` holds only the sample app, Team Todo (Node, no dependencies). Never install the devkit on `main`.
- Each run gets a branch `test-run/<run-id>` off `main`, set as the repository default branch for the run.
- Run IDs are `T001`, `T002`, ... Take the next number from the run record issues.

## 2. Install the devkit under test

Clone the testbed into a temporary directory and create the run branch. Install from the local devkit checkout, not `sync devkit`, which installs the last release. Follow `.mt-agent-devkit/workflows/commands/Target_Project_Deployment_Workflow.md`.

Fill `{github-org}` and `{repo-name}` through the adaptations file: `init` leaves them in several installed rules and skills and does not warn. Check with `grep -rE '\{github-org\}|\{repo-name\}'`, then commit and push.

## 3. Drive the session

Keep the input documents outside the target repo (a dirty tree blocks branch preflight). Write an answer sheet before the first turn and never give it to the session.

Run from the target directory, then answer each stop with `--resume <session_id>`:

```bash
claude -p "<command>" --model sonnet --setting-sources project --strict-mcp-config \
  --add-dir <input-dir> --permission-mode acceptEdits --max-budget-usd <remaining> \
  --output-format json --allowedTools <list> --disallowedTools <list>
```

- Allowed in T001: Read, Glob, Grep, Skill, Agent, SendMessage, TodoWrite and Bash for `git`, `gh`, `python3`, `ls`, `mkdir`, `wc`, `node --test`, `npm test`. A sprint run needs more for implementation.
- Disallow repository create, edit and delete, force push and web access.
- Put a `gh` wrapper first on `PATH` that refuses other repositories. It only catches mistakes: `git`, `gh` and `python3` can bypass it and the session has the host's `gh` login. A hard boundary needs a token limited to the testbed.
- `total_cost_usd` is the session total, not the turn. `--max-budget-usd` applies to one invocation, so pass what is left of the cap.
- Writes under `.claude/agents/` are refused headless, so agent records and retrospectives are not exercised. A clone-local exclude edit may also be refused; add the line yourself and note it.
- Long turns run in the background. After a usage limit, resume the same session and tell it not to repeat completed steps.

## 4. Check the result

Do not accept the session's summary. Read the files, issues, PRs and comments and compare them with the story's acceptance criteria. Report pass, fail or not tested, and keep test-environment limits apart from devkit faults.

## 5. Mark and record the run

- Label: `test-run:<run-id>-<topic>` on every issue and PR the run created. Add it after the run; never tell the workflow agents. New items are those numbered above the highest number before the run, so run one test at a time.
- Start feature slugs with the run ID, such as `t001-due-dates`.
- Leave workflow titles and branch names unchanged.
- File one issue `Test run <run-id>: <topic>` with the label, devkit commit, method, cost, results, findings, environment limits and what was not tested.

## 6. Cleanup

Close the run's open issues and PRs once nothing else will test against them; keep the labels. Sprint numbers are repo-wide: remove `sprint-N` labels from older runs when a run must start at `sprint-1`.

## 7. Proven so far

| Run | Covered | Cost |
|---|---|---|
| T001 | `analyze requirements`, GitHub mode, to merged docs PR and backlog stories | $5.61 |

Not yet run this way: sprint commands, `start story`, strict mode, open-topic and correction rounds, other providers.
