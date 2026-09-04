# Test Scenarios — ST-000147

**Story:** `sync devkit` follows released tags instead of `main`
**Date:** 2026-09-04
**Branch:** `ST-000147/sync-devkit-follows-released-tags`
**PR:** #195 (head `a27a3a1`; implementation commit `a22950b`; `0014199` is retro+memory, `[skip ci]`)
**Type:** behavioral — full validation path

---

## Scope

`check_devkit_version.sh` / `.ps1` (tag resolution replacing `version.txt` fetch), `Sync_Devkit_Workflow_template.md`
and `Sync_Devkit_Project_Workflow_template.md` (Stage 0 tag resolution, `{DEVKIT_RAW_BASE}` pinned fetch base),
`Refine_Prototype_Workflow_Shared_template.md` (same derivation for scaffold-repo fetches), the `**Devkit source:**`
field shape change propagated to `Update_Project_Workflow.md`, `AGENTS.md`/`CLAUDE.md`, and the `.antigravity/`
mirror. TL approved at `a27a3a1`, 0 blocking findings, 5 nits (1–4 backlog/fold-in, not blockers).

Dev and TL both reported a six-case matrix (canonical URL / legacy raw URL / unreachable repo / no matching tag /
missing field / already-current) run against a real tagged public repo, agreeing on all six. Per this pass's
brief, that claim is not inherited — the matrix below was independently designed from the AC and executed fresh,
using different fixture repos than either prior report is known to have used, plus one filter case neither
reported (pre-release-suffixed tags).

This repo (`mt-agent-devkit`) currently has 0 tags, so all live-tag assertions use external fixture repos:
`https://github.com/cli/cli` (semver-tagged, `v2.100.0` highest), `https://github.com/octocat/Hello-World`
(reachable, zero tags), `https://github.com/kubernetes/kubernetes` (mixed semver + pre-release-suffixed tags),
and a deliberately nonexistent org/repo path for the unreachable case.

---

## Test Scenarios

### TS-01 — AC2/AC3: canonical URL resolves highest `vX.Y.Z` tag via `git ls-remote`, never the REST API

**Files:** `check_devkit_version.sh`, `check_devkit_version.ps1`

**Expected:** With `**Devkit source:**` = `https://github.com/cli/cli` and an older installed version, both
scripts print `{"systemMessage": "Devkit update available: v<old> -> v2.100.0. ..."}"` and exit 0. Neither script
contains any GitHub REST API reference.

**Result:** PASS. Built a scratch fixture (`CLAUDE.md` + `.claude/agents/devkit_version.txt` = `2.0.0`) and ran
both the substituted `.sh` and `.ps1` scripts directly. Both printed the identical update message resolving to
`v2.100.0` and exited 0. `git ls-remote --tags --refs --sort=-v:refname https://github.com/cli/cli.git` run live
confirms `v2.100.0` sorts above `v2.99.0` (the story's own worked example), independently reproducing that ordering
claim rather than trusting it. `grep -niE "api\.github\.com|Invoke-RestMethod|curl.*api|releases/latest"` against
both scripts: zero matches.

---

### TS-02 — AC1: legacy raw-base URL is normalized and still resolves

**Files:** `check_devkit_version.sh`, `check_devkit_version.ps1`

**Expected:** With `**Devkit source:**` still holding an old-shape raw base
(`https://raw.githubusercontent.com/cli/cli/main`), both scripts reduce it to the canonical repo URL internally
and resolve the same `v2.100.0` tag — same output as TS-01.

**Result:** PASS. Identical output and exit code to TS-01 in both scripts.

---

### TS-03 — AC4 (unreachable repo): silent `exit 0`, no output

**Files:** `check_devkit_version.sh`, `check_devkit_version.ps1`

**Expected:** With a nonexistent org/repo path, `git ls-remote` fails and both scripts exit 0 with zero stdout.

**Result:** PASS. `git ls-remote` against the fixture path fails with exit 128 (`remote: Repository not found` /
`fatal: repository ... not found`), independently reproducing the TL's cited exit code. Traced both scripts with
`bash -x` and a manual PowerShell `$LASTEXITCODE` check — both detect the non-zero exit and fall through to a
silent `exit 0`. No `-e`/`pipefail` is set in the shell script, confirming the failure is reached deliberately via
the empty-`LATEST_TAG` guard, not by an unrelated short-circuit.

---

### TS-04 — AC4 (no matching tag): silent `exit 0`, no output — distinct from unreachable

**Files:** `check_devkit_version.sh`, `check_devkit_version.ps1`

**Expected:** Against a real, reachable repo with zero tags (`octocat/Hello-World`), both scripts exit 0 with zero
output — same outcome as TS-03 but via a different code path (empty tag list, not a fetch failure).

**Result:** PASS. Confirmed `git ls-remote --tags --refs` against `octocat/Hello-World` itself exits 0 (reachable)
while returning zero tag lines — a genuinely distinct case from TS-03's unreachable fixture. Both scripts printed
no output and exited 0.

---

### TS-05 — AC1/AC4 (missing field): silent `exit 0`, no output

**Files:** `check_devkit_version.sh`, `check_devkit_version.ps1`

**Expected:** With no `**Devkit source:**` line in `CLAUDE.md` at all, both scripts exit 0 with zero output before
ever attempting a network call.

**Result:** PASS. Both scripts exited 0 with empty stdout.

---

### TS-06 — AC4 (already current): silent `exit 0`, no output

**Files:** `check_devkit_version.sh`, `check_devkit_version.ps1`

**Expected:** With the installed version already equal to the resolved latest tag (`2.100.0`), both scripts
resolve the tag successfully but print nothing since `CURRENT == LATEST`.

**Result:** PASS. Both scripts exited 0 with empty stdout.

---

### TS-07 — AC2 filter correctness beyond the story's own worked example: pre-release-suffixed tags are excluded

**Files:** `check_devkit_version.sh`, `check_devkit_version.ps1`

**Expected:** The `^v[0-9]+\.[0-9]+\.[0-9]+$` filter (shell) / `^v\d+\.\d+\.\d+$` filter (PowerShell) rejects a
tag with a pre-release suffix even when it sorts above a clean release under `--sort=-v:refname`.

**Result:** PASS — new case, not covered by either prior report. `kubernetes/kubernetes`'s highest tag by
`--sort=-v:refname` is `v1.38.0-alpha.0`, which does not match either anchored regex. Ran the shell pipeline
(`sed`+`grep -E`) and the PowerShell `-match` filter against the live tag list independently — both correctly skip
every `-alpha`/`-beta`/`-rc` tag and resolve to `v1.37.0`, the true latest stable release.

---

### TS-08: `Sync_Devkit_Workflow.md` Stage 0 / `{DEVKIT_RAW_BASE}` propagation and dual-update completeness

**Files:** `Sync_Devkit_Workflow_template.md`, `Sync_Devkit_Project_Workflow_template.md`,
`Refine_Prototype_Workflow_Shared_template.md`, `Update_Project_Workflow.md` (both copies), `AGENTS.md`,
`CLAUDE.md`, `.antigravity/` mirror

**Expected:** Stage 0 in both sync workflow templates resolves `LATEST_VERSION` from the highest release tag (not
a file on `main`); `{DEVKIT_RAW_BASE}` = `https://raw.githubusercontent.com/{owner}/{repo}/v{LATEST_VERSION}` is
used for every remote file/`changes.json` fetch in Stage 1–2, replacing the old `{DEVKIT_SOURCE_URL}` raw-base
usage; `Update_Project_Workflow.md` only changes the `**Devkit source:**` field shape (no tag-fetching added,
since it reads local files); every change is mirrored to `.claude/agents/working/`,
`.claude/agents/templates/`, and `.antigravity/`.

**Result:** PASS. Read the full diff for every changed file. Confirmed `grep -n "DEVKIT_SOURCE_URL"` in both sync
workflow templates finds zero raw-fetch usages (only the prototype-scaffold template still reads
`{DEVKIT_SOURCE_URL}` — correctly, only to derive `{DEVKIT_RAW_BASE}` from it, not as a fetch base itself), and
`grep -n "/main"` finds zero remaining fetch-from-main references. `.antigravity/agents/working/workflows/`
mirror carries the identical Stage-0/`{DEVKIT_RAW_BASE}` substance (confirmed line-by-line against its own diff;
the mirror is pre-existing leaner than the `.claude/` copy — 337 vs 424 lines on `main` — so a raw line-count
diff is not the right comparison, but every semantic addition is present in both). `Update_Project_Workflow.md`
diff (both `.claude/` and `.antigravity/` copies) confirmed as field-shape-only, no tag-fetch logic added.

---

### TS-09: Bookkeeping — `changes.json`, `CHANGELOG.md`, `validate_templates.py`

**Files:** `changes.json`, `CHANGELOG.md`, `scripts/validate_templates.py`

**Expected:** Every touched file under `.claude/agents/templates/` is listed in the `0.1.48-SNAPSHOT` entry of
`changes.json` with a one-line `[ST-000147] <delta>` description; a `CHANGELOG.md` bullet exists under the current
Unreleased section; `validate_templates.py` registers the new `DEVKIT_RAW_BASE` single-brace token.

**Result:** PASS. All 5 touched template files (`check_devkit_version.sh`/`.ps1`,
`Sync_Devkit_Workflow_template.md`, `Sync_Devkit_Project_Workflow_template.md`,
`Refine_Prototype_Workflow_Shared_template.md`) present in `changes.json`'s `0.1.48-SNAPSHOT.modified` array,
each with a compact one-line `[ST-000147]` description (no narrative/rationale prose). `CHANGELOG.md` carries a
`[ST-000147]` bullet under `## [0.1.48-SNAPSHOT] - Unreleased`. `KNOWN_SINGLE_BRACE_TOKENS` gains `DEVKIT_RAW_BASE`.

---

## Regression Check

- `python scripts/validate_templates.py` — exit 0, zero `[ERROR]`/`[KNOWN_ISSUE]` lines.
- `bash scripts/test/run.sh` — 5/5 fixture checks PASS.
- `init project` — untouched by this story (no diff touches `Init_Project_Workflow` or its templates).
- `sync devkit` (both `github` and `strict` mode) — intended change, applied consistently to both sync workflow
  templates and both working-copy mirrors; no mode-specific asymmetry found.

## Sign-off

All 11 AC (from issue #191) independently validated PASS. QA sign-off posted on issue #191.
