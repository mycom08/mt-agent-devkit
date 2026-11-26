# Workflow Test Guide

How to run a devkit workflow against a real target project. For template and deployment tests see [Template Test Strategy](Template_Test_Strategy.md).

**Ask the user before every run.** Knowing about the testbed is not permission. Agree the spend cap, the permission mode and which commands will run.

## 1. Testbed

`mycom08/mt-agent-devkit-testbed` (private, reusable). Do not create another test repo.

- `main` holds only the sample app, Team Todo (Node, no dependencies). Never install the devkit on `main`.
- Each run gets a branch `test-run/<run-id>` off `main`, set as the repository default branch for the run.
- Run IDs are `T001`, `T002`, ... Take the next number from the run record issues.

## 2. Install the devkit under test

Clone the testbed into a temporary directory and create the run branch. Install from the local devkit checkout, not `sync devkit`, which installs the last release. Follow `.mt-agent-devkit/workflows/commands/Target_Project_Deployment_Workflow.md`.

Commit and push the installed files. No repository name needs filling in.

## 3. Drive the session

Keep the input documents outside the target repo (a dirty tree blocks branch preflight). Write an answer sheet before the first turn and never give it to the session.

Run from the target directory, then answer each stop with `--resume <session_id>`:

```bash
claude -p "<command>" --model sonnet --setting-sources project --strict-mcp-config \
  --add-dir <input-dir> --permission-mode acceptEdits --max-budget-usd <remaining> \
  --output-format json --allowedTools <list> --disallowedTools <list>
```

- Permission mode: `acceptEdits` with an allow-list is enough for `analyze requirements`, `plan next sprint` and most of `refine sprint`. A story run must write under `.claude/agents/`, which headless sessions refuse in that mode even with an allow rule. T001 used `--permission-mode auto` for it, chosen by the user. Never choose a wider mode yourself.
- Allowed in T001: Read, Glob, Grep, Skill, Agent, SendMessage, TodoWrite and Bash for `git`, `gh`, `python3`, `ls`, `mkdir`, `wc`, `node --test`, `npm test`. In auto mode Claude Code decides what runs; keep the disallow list and the `gh` wrapper.
- Disallow repository create, edit and delete, force push and web access.
- Put a `gh` wrapper first on `PATH` that refuses other repositories. It only catches mistakes: `git`, `gh` and `python3` can bypass it and the session has the host's `gh` login. A hard boundary needs a token limited to the testbed.
- `total_cost_usd` is the session total, not the turn. `--max-budget-usd` applies to one invocation, so pass what is left of the cap.
- In `acceptEdits` mode, agent records and retrospectives are not exercised. A clone-local exclude edit may also be refused; add the line yourself and note it.
- `refine sprint` and `continue sprint` take every story in scope. To limit them, remove `sprint-N` from the other stories and restore it afterwards.
- Long turns run in the background. A stopped turn reports no cost. After a usage limit, resume the same session and tell it not to repeat completed steps.

## 4. Check the result

Do not accept the session's summary. Read the files, issues, PRs and comments and compare them with the story's acceptance criteria. Report pass, fail or not tested, and keep test-environment limits apart from devkit faults.

## 5. Mark and record the run

- Label: `test-run:<run-id>-<topic>` on every issue and PR the run created. Add it after the run; never tell the workflow agents. New items are those numbered above the highest number before the run, so run one test at a time.
- Start feature slugs with the run ID, such as `t001-due-dates`.
- Leave workflow titles and branch names unchanged.
- File one issue `Test run <run-id>: <topic>` with the label, devkit commit, method, cost, results, findings, environment limits and what was not tested.

## 6. Cleanup

Clean up before the next run: issues and sprint labels are repo-wide, so an open story left in a sprint makes the next run's planning stop on an unfinished sprint. Keep a run's open items only while something else will test against them (for example `continue sprint` on its remaining stories).

1. Close the run's unfinished stories as not planned and remove their `sprint-N` label.
2. Close the run record issue and any other open issue or PR from the run.
3. Delete the run's leftover story and analysis branches.
4. Set the default branch back to `main`.
5. Check that no issue or PR is open: `gh issue list` and `gh pr list` on the testbed.

Keep the `test-run/<run-id>` branch, merged PRs, closed issues and labels as the run's history. Done stories keep `sprint-N`, so a later run starts at the next number; remove those labels too when a run must start at `sprint-1`.

A local clone may be kept for a later run. Before reusing it, discard uncommitted files, update from `main` and install again.

## 7. Proven so far

Run T001, GitHub mode, Claude provider, orchestrator model sonnet:

| Command | Result | Cost |
|---|---|---|
| `analyze requirements` | Merged docs PR and three backlog stories | $5.61 |
| `plan next sprint <feature>`, run twice | Planned by feature label; second run stopped | $0.99 |
| `refine sprint`, one story | Question raised and answered; `status:ready` | $1.11 |
| `start story` | Built, reviewed, QA validated, merged and closed | $3.04 |

Not yet run this way: `continue sprint`, strict mode, open-topic and correction rounds, blocked documents, fix rounds, dependent stories, other providers. Findings are in the testbed run record.
