# ST-000370 Test Scenarios — Installed files without repository placeholders

**Story:** ST-000370 (issue 370, PR 376)
**Scope validated:** ce2345faebe1a538344b3dcfab3a53c93b06a0f4 (base 524a46ac4c93e3084990ddcf16bd96ebd1f70fa1)

Scenarios run in disposable projects. "Installed" means a scratch install from the bundle. The workflow-start guard is instruction text, so its prescribed commands are run by hand in scratch repositories.

| ID | AC | Type | Scenario | Expected |
|----|----|------|----------|----------|
| T1 | 1 | Happy | Story Repro Command, then a fresh GitHub-mode install for 3 providers and both profiles, searched for repository placeholders in any form | No installed rule, skill, workflow or instruction needs one |
| T2 | 1 | Edge | Installed `gh` commands, including the check-runs API call, run without a repository argument | `gh` fills the repository itself |
| T3 | 2 | Inspection | The guard is in the installed GitHub-mode orchestrator instructions and every workflow route reaches it before its first `gh` command | Reachable |
| T4 | 2 | Happy | Default matches the base remote (also differing only in letter case, SSH and `.git` URL forms) | Continue |
| T5 | 2 | Error | Default names another repository (two remotes, and one remote) | Mismatch visible; stop and ask; default untouched |
| T6 | 2 | Happy/Edge | No default: one GitHub remote; several including `upstream`; base tracks a non-`origin` remote | One remote continues; several set the base remote's repository |
| T7 | 2 | Error | Base remote missing or not on GitHub; SSH host alias URL | Stop and ask |
| T8 | 3 | Inspection | Prose that named the repository in installed files | Still says which repository |
| T9 | 4 | Happy | Install at base, update to head with no adaptation for the repository name; install and update at head | No conflict; no customised copy |
| T10 | 5 | Regression | Strict-mode install at base and at head compared | No behavior change |
| T11 | 6 | Error | Placeholder seeded into a rule, skill, workflow and instruction source; build run | Build fails and names the file |
| T12 | 6 | Edge | Installed destinations not covered by the build check | No rule, skill or workflow outside it |
| T13 | 6, 7 | Tests | New tests at head and against the base sources | Pass / fail |
| T14 | 7 | Gates | Harness, wrapper, common-block, template and bundle checks, unit tests, run.sh, CI at head | All pass |
| T15 | 7 | Metadata | `changes.json` descriptions, CHANGELOG bullet, version untouched | Per `change-metadata` |

## Results (2026-11-26, revision ce2345faebe1a538344b3dcfab3a53c93b06a0f4)

All AC PASS.

- T1: Repro Command lists 5 files at base, none at head. No `{github-org}` or `{repo-name}` in 12 scratch installs (3 providers, 2 modes, 2 profiles). Remaining `<repo-name>` text names Build Software companion repositories.
- T2: with a default set in a two-remote scratch repository, `gh issue list`, `gh pr view`, `gh pr diff`, `gh pr checks` and the check-runs API call used it.
- T3: guard present in installed GitHub-mode `orchestrator_instructions.md` (3 providers), absent in strict; the installed entrypoint requires that file before any workflow.
- T4 to T6 (gh 2.103.2): matching default, including different letter case; mismatch with two remotes and with one remote shows the other repository; no default with one remote resolves to it; with `upstream` present and no default `gh` chose `upstream`, and step 5 moved it to the base remote's repository (HTTPS, `ssh://`, scp-style, non-`origin` base remote). Only `.git/config` changed.
- T7: missing and non-GitHub base remote are detectable at step 1. SSH host alias URL: `gh repo set-default` rejects both URL and `OWNER/REPO`.
- T8: both `Story_Standard` sentences name this project's repository and the remote rule.
- T9: base install updated to head, 3 providers x 2 modes: no conflict, no placeholder left, guard added in GitHub mode only. A hand-filled copy still raises the existing conflict (out of scope).
- T10: strict installs differ only in placeholder removal and Location prose in shared files, plus the shipped `build_bundle.py`; strict orchestrator instructions unchanged.
- T11, T12: seeded placeholders in rule, skill, workflow, orchestrator and contract-derived skill sources fail the build; no installed rule, skill or workflow lies outside the checked folders.
- T13: the two new tests fail against base sources (4 failures) and pass at head.
- T14: harness, wrapper, common-block, template and bundle checks exit 0; run.sh 298 tests (1 skipped), 17/17 fixtures; CI passed at head.
- T15: `changes.json` and CHANGELOG entries present; VERSION and version.txt untouched.

Not exercised: the guard run by a live agent session; GitHub Enterprise hosts.
