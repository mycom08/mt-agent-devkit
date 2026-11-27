# ST-000257 Test Scenarios: GitHub Comment Hook

**Scope tested:** PR 384, head `20964cca28c84936815d07344bff437bf68a824e`.
**Method:** feed hook input JSON to the configured command; install and sync into scratch targets. Never post to GitHub.

## Scenarios

| ID | AC | Scenario | Expected |
|---|---|---|---|
| S01 | 1 | `gh pr review --approve` and `-a`, including chained and prefixed forms | Deny |
| S02 | 1 | `--request-changes`, `--comment`, and `gh` text that is only an argument | Pass |
| S03 | 1 | `@name` and bare `#N` in prose on all three commands | Deny |
| S04 | 1 | The same inside inline code, fences, URLs, emails | Pass |
| S05 | 1 | Fenced command or test output | Deny |
| S06 | 1 | Fenced commands and source code | Pass |
| S07 | 1 | `gh pr checks` table in a PR comment, then in an issue comment | Pass, then deny |
| S08 | 1 | Body from `--body`, `--body-file`, heredoc, PowerShell here-string | Same verdicts |
| S09 | 2 | Over 200 words without and with a stated exception | Warn, then pass |
| S10 | 2 | `**Thread Status:**` without and with `**Decision:**` | Warn, then pass |
| S11 | 2 | Warning-only bodies | Never deny |
| S12 | 3 | Claude and Antigravity envelopes through each configured command | Provider-shaped answer, exit 0 |
| S13 | 3 | Under `sh` and `bash`: missing, unreadable, broken or crashing script; missing or failing interpreters; broken input | Exit 0, command not blocked |
| S14 | 3 | `python3` absent or failing but `python` present | Hook still denies |
| S15 | 4 | Fresh install, github and strict modes, `repo` and `project_root` profiles | Script and both configs installed |
| S16 | 4 | Install over project hooks, then run again | Project hooks kept; second run changes nothing |
| S17 | 4 | Sync from the previous release with project hooks | Hook installed after the documented second run |
| S18 | 4 | Sync with an existing `.agents/hooks.json` | Documented adaptation path works |
| S19 | 4 | Invalid JSON in a target hook file; local script of the same name | No overwrite |
| S20 | 4 | Devkit repo hook | Denies natively |
| S21 | 5, 6 | Hook tests, harness and template gates, `changes.json`, `CHANGELOG.md` | All exit 0; entries present |

## Results (2026-11-27)

| AC | Verdict | Scenarios |
|---|---|---|
| 1 | PASS | S01 to S08; S01 also denied natively in Claude Bash |
| 2 | PASS | S09 to S11; warning also seen natively in Claude |
| 3 | PASS | S12 to S14, against the revised AC3 |
| 4 | PASS | S15 to S20; existing targets need two sync runs |
| 5 | PASS | S21 |
| 6 | PASS | S21 |

Signed off on the revised criteria: issue comment 7215173918. AC3 was rewritten by a user-approved scope split (comment 7215140750). The earlier report (7214329746) marked the original AC3 NOT VERIFIED.

Limits seen: `@` or `#N` in indented code blocks and HTML code tags is denied; fenced `git log` and `git push` output passes; invalid JSON in a hook file ends in a traceback with nothing written.

## Native runtime limits

Antigravity, Windows and the PowerShell tool need their own runtimes. A scripted envelope does not certify them. All runs were on Linux.

Native Antigravity behaviour is tracked in issue 385 and stays NOT VERIFIED. That run (user permission first, per `docs/Workflow_Test_Guide.md`) must show: `.agents/hooks.json` is loaded, an approval is denied, a warning does not block, a clean command runs, and a missing script blocks nothing.

Windows is not named by AC3 or issue 385.
