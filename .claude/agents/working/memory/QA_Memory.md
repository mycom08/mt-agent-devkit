# QA Memory

> Two-tier memory (devkit-internal pilot, `Agent_Common_Read_On_Demand.md §8`, issue #118). This is the lean, always-read index — titles and grep-able keywords only, no fact bodies. Full text lives in `QA_Memory_Archive.md`. Before starting a task, scan the titles/keywords below for a match; if one matches, retrieve just that fact per §8's bounded-read recipe — never read the whole archive.

## Standing Checks

*(none yet — no current fact reduces to an unconditional always-do action; entries move here if a future fact qualifies)*

## Keyword Index

### Fact 1 — The full devkit automation suite (no runtime, no API)
Keywords: `python scripts/validate_templates.py`, `bash scripts/test/run.sh`, corpus invariant check, fixture self-test, `docs/Template_Test_Strategy.md`, 6 invariants, risk tiers A/B/C, AC-as-oracle

### Fact 2 — Always run the Layer-1 gate from a matched `git worktree`, never the primary tree
Keywords: `git worktree add`, `git worktree remove --force`, differential base-vs-head, gitignored runtime files, `working-record/*.md`, `_resolve_file_ref`, polluted baseline

### Fact 3 — Worktree checkouts may materialize CRLF vs. a primary LF tree
Keywords: `git worktree`, CRLF, LF, spurious whole-file diff, `diff -rq`, `tr -d '\r'`, `.gitattributes`

### Fact 4 — `scaffold_mechanical.sh` changes need a two-mode scratch-scaffold diff, not just the script pair
Keywords: `scaffold_mechanical.sh`, `Type: behavioral`, scratch scaffold, github, strict, `diff -rq`, `origin/main` worktree, deployment regression

### Fact 5 — One-grep verification for the devkit-only-path defect class
Keywords: `templates/**`, devkit-only path, `grep -n "agents/working/\|Build_Software_Workflow"`, clean fix, QA-side check

### Fact 6 — Verify "untouched" claims with a scoped `git diff`, never infer from absence
Keywords: `git diff main origin/<branch>`, untouched bullet, zero `+`/`-` lines, review verdict

### Fact 7 — Hand-construct an adversarial input for any CLI-as-correctness-mechanism AC
Keywords: `gh` query, idempotency, dedup, filters, adversarial input, prefix-title case, exact-line-match

### Fact 8 — Regression scope for additive-only PRs
Keywords: `git diff main..HEAD --name-only`, additive-only, `.claude/agents/templates/`, `.claude/agents/workflows/`, non-template PR

### Fact 9 — `validate_templates.py` `[KNOWN_ISSUE]` vs `[ERROR]`, and fixture flags
Keywords: `[KNOWN_ISSUE]`, `Blocked_Request_Template.md`, capital-T typo, `--test-retired-trigger`, `RETIRED_TRIGGERS`, Invariant #4, Invariant #5

### Fact 10 — Locate the real mechanism behind a "described but not visibly implemented" AC claim
Keywords: runtime mechanism, files logged by an earlier stage, computed at runtime, pre-existing rule/instruction text, unverified claim

## Troubleshooting Facts

### Fix 1 — `git show <ref>:<path>` fails with "unknown revision" in this Bash tool
- **Problem:** `git show origin/<branch>:<path/with/slashes>` errors instead of printing the blob.
- **Symptoms:** `fatal: ambiguous argument 'origin\<branch>\<path>;<file>': unknown revision or path not in the working tree.` — the `/` and `:` in the argument have been silently mangled to `\` and `;`.
- **Root Cause:** MSYS/Git-Bash path-conversion heuristics rewrite any argument that looks like a path, and a colon-syntax `ref:path` git argument matches that heuristic even though it is not a filesystem path.
- **Fix:** prefix the command with `MSYS_NO_PATHCONV=1`, e.g. `MSYS_NO_PATHCONV=1 git show origin/<branch>:<path>`.
- **Prevention:** always set `MSYS_NO_PATHCONV=1` for any git command whose argument contains a literal `:` (colon-syntax `ref:path`, `refspec:refspec`, etc.) run via the Bash tool on this platform.

### Fix 2 — Which Python name exists depends on the machine
- **Problem:** Gates and `scripts/test/run.sh` call bare `python`; on some machines only `python3` exists (devkit Linux host, seen in ST-000287, 288, 290, 291, 292).
- **Symptoms:** `python: command not found`; every gate fails before running.
- **Root Cause:** the environment, not the repo. On the Windows host `python3` is an App Execution Alias stub and `python` is real; on the Linux host it is the reverse.
- **Fix:** check `command -v python python3` first; if only `python3` exists, point a scratchpad shim named `python` at it and put that dir on `PATH`.
- **Prevention:** never assume one name; do not edit the shared runner for this.

### Fix 3 — `grep -oP` (PCRE lookbehind) silently fails in this Bash tool's default shell locale
- **Problem:** A shell script using `grep -oP '(?<=...)...'` produces empty output and the script falls through its own "field missing"/silent-exit guard — even though the same script works correctly on a normal developer machine or CI.
- **Symptoms:** `grep: -P supports only unibyte and UTF-8 locales` is the message when the grep line is run standalone; when the surrounding script suppresses stderr (`2>/dev/null`), there is no visible symptom at all — the script just behaves as if the pattern never matched.
- **Root Cause:** This Bash tool's default shell environment has `LANG`/`LC_ALL` unset even though `locale` reports `C.UTF-8` for the individual `LC_*` categories; `grep -P` refuses to run under that combination.
- **Fix:** prefix the command (or `export` once per session) with `LC_ALL=C.UTF-8` before running or testing any script that contains `grep -P`.
- **Prevention:** when behaviorally testing a shell script that uses `grep -P` under this Bash tool, always set `LC_ALL=C.UTF-8` first — otherwise a real extraction/parsing step can silently no-op and get misread as an intentional silent-exit path. This is an environment quirk of the tool, not a defect in a script that behaves this way only because of it — confirm the affected line is unchanged by the diff under review before reporting it as a finding.
