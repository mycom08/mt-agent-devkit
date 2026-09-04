# Test Scenarios — ST-000146

**Story:** Release process — `VERSION` file, single CHANGELOG heading format, and a manual `release.yml` job
**Date:** 2026-09-04
**Branch:** `ST-000146/release-process`
**PR:** #193 (head `b1fb4f0`; only functional commit is `4cc6246` — `b1fb4f0` adds the retro file only)
**Type:** behavioral — full validation path

---

## Scope

`VERSION` (new, `-SNAPSHOT`), `version.txt` (kept as a one-time bridge, clean value), `CHANGELOG.md`
(single heading format, one-time migration), `changes.json` (`-SNAPSHOT`-suffixed newest key),
`scripts/validate_templates.py` (tolerate the suffix), `.github/workflows/release.yml` (new,
`workflow_dispatch`-only, two jobs: `release` and `post-release`). TL approved at `b1fb4f0`, 15/15 AC
met, 0 blocking, 4 nits (N1–N3 fold-in no fix round, N4 backlog candidate for PO) — not re-litigated
here per this pass's brief.

`release.yml` mutates `main` on manual dispatch and cannot be executed to validate — it is impossible
to test the same way as a normal PR. Both Dev and TL validated it by rehearsing the jobs' shell
pipelines against copies of the branch's real `VERSION`/`CHANGELOG.md`/`changes.json` in a scratch
directory (never `main`, never pushed, never dispatched). This QA pass repeats that rehearsal
independently, from files pulled fresh via `git show` (not trusting either prior summary), entirely
under the session scratchpad.

---

## Test Scenarios

### TS-01 — AC1/AC2: `VERSION` (snapshot) and `version.txt` (clean bridge) values and shape

**Files:** `VERSION`, `version.txt`

**Expected:** `VERSION` = next patch after `main`'s `version.txt` (`0.1.47`), suffixed `-SNAPSHOT`;
single line, no trailing whitespace. `version.txt` still exists holding the same release's clean
number.

**Result:** PASS. `main:version.txt` = `0.1.47` → next patch `0.1.48`. `git show
origin/ST-000146/release-process:VERSION` = 16 bytes, hex `...534e415053484f54 0a` — `0.1.48-SNAPSHOT`
plus a single trailing `\n`, no spaces/CR (a worktree *checkout* of the same blob showed CRLF —
checkout-time line-ending materialization, not a property of the stored blob; confirmed by comparing
`git show` output, which bypasses checkout conversion, byte-for-byte). `version.txt` (branch) =
`0.1.48` — matches VERSION's numeric part, no suffix.

---

### TS-02 — AC3/AC4: CHANGELOG heading migration, entry text preserved, Contribution Convention text

**File:** `CHANGELOG.md`

**Expected:** Every `## ` heading matches `[x.y.z] - Unreleased` or `[x.y.z] - YYYY-MM-DD`; no
`## [Unreleased]` or `## x.y.z (date)` form remains; ST-000144's existing entry text is unchanged, only
relocated under the renamed heading; Contribution Convention states bullets go under the current
`- Unreleased` heading and the version number is never hand-edited.

**Result:** PASS. `grep -n "^## "` on the branch file: 8 headings, all `[x.y.z] - <Unreleased|date>`.
Reference-grepped the two named legacy forms (`^## \[Unreleased\]`, `^## [0-9]+\.[0-9]+\.[0-9]+ \(`) —
zero hits. Diffed the ST-000144 bullet text between `main` (under `## [Unreleased]`) and the branch
(under `## [0.1.48] - Unreleased`) — byte-identical, confirming "no entry text changed." Contribution
Convention section reads "The implementer adds their bullets under the current `- Unreleased` heading
as part of their own PR. **The version number is never edited by hand**."

---

### TS-03 — AC5/AC6: `changes.json` `-SNAPSHOT` key, historical keys untouched, validator tolerates the suffix

**Files:** `changes.json`, `scripts/validate_templates.py`

**Expected:** Newest key = `0.1.48-SNAPSHOT`; all older keys byte-identical to `main`; validator strips
a trailing `-SNAPSHOT` before the `int()`-per-component semver check instead of hard-failing on it.

**Result:** PASS. Branch key order: `['0.1.48-SNAPSHOT', '0.1.46', '0.1.45', ...]` vs. `main`:
`['0.1.47', '0.1.46', '0.1.45', ...]` — only the newest key changed (renamed `0.1.47` →
`0.1.48-SNAPSHOT`, matching `VERSION`; this is the same in-progress entry carried forward, not a drop —
its payload, the ST-000144 file/description entry, is unchanged). Diff confirms `0.1.46` downward is
untouched. `validate_templates.py` diff adds `base_key = version_key[:-len("-SNAPSHOT")] if
version_key.endswith("-SNAPSHOT") else version_key` before the `int()` loop — the numeric check now
runs against `base_key`. (An earlier direct `python -c` read of `changes.json` without `encoding=`
rendered the pre-existing `§` in the ST-000144 description as `Â§` in my terminal — a cp1252-vs-UTF-8
display artifact of that one-off diagnostic script, not a file defect: `xxd` on both `main` and the
branch shows byte-identical `c2 a7`, the correct UTF-8 encoding of `§`, at that offset.)

---

### TS-04 — AC15: `validate_templates.py` exits 0

**Command:** `python scripts/validate_templates.py`, run from a detached `git worktree` at the PR head
(`b1fb4f0`) — never the primary checkout, matching `QA_Memory.md` Fact 2's methodology (though the
primary tree here was already on this branch; the worktree run gives an independent confirmation
regardless).

**Result:** PASS. `OK -- all Layer-1 invariants passed`, exit 0.

---

### TS-05 — AC7/AC8: `release.yml` structure — dispatch-only, main-only guard, VERSION validation

**File:** `.github/workflows/release.yml`

**Expected:** `on: workflow_dispatch` only; a step that exits 1 when `github.ref != 'refs/heads/main'`
(not a job-level `if`, so a wrong-ref dispatch fails visibly rather than silently skipping); a step
that reads `VERSION`, hard-fails unless it matches `^[0-9]+\.[0-9]+\.[0-9]+-SNAPSHOT$`, and derives the
release version via `${SNAPSHOT%-SNAPSHOT}`.

**Result:** PASS (code review + rehearsal). File confirmed to contain exactly this shape. Rehearsed the
validate step against the branch's real `VERSION` in scratch: `SNAPSHOT=0.1.48-SNAPSHOT` passes the
regex, derived `VERSION=0.1.48`.

---

### TS-06 — AC9: tag-exists guard

**File:** `.github/workflows/release.yml` ("Check tag does not exist" step)

**Expected:** `git ls-remote --tags origin refs/tags/v{version}` — non-empty match aborts the job.

**Result:** PASS (code review only — cannot be exercised without a live `git ls-remote` against origin,
which this pass does not run per the no-dispatch/no-network-mutation constraint). Logic matches the
reference implementation's tag-exists step; `v${version}` interpolation is correct given TS-05's
derived value.

---

### TS-07 — AC10: CHANGELOG heading-exists and non-empty-section guards, incl. the `---`-separator edge case

**File:** `.github/workflows/release.yml` ("Validate CHANGELOG heading exists" / "...section is not
empty" steps)

**Expected:** Job terminates if no `^## \[{version}\]` heading exists, or if the section between that
heading and the next `## ` has zero lines matching `^[[:space:]]*- ` (dash **+ space**, not bare dash).

**Result:** PASS, and the critical nuance independently reproduced. Rehearsed against the branch's real
`0.1.48` section (2 real bullets) — 2 entries counted, guard passes, as expected. Then rehearsed against
the section the `post-release` job itself would open for `0.1.49` (fresh, empty, closed by the job's own
`---` separator): the section body is exactly
```

### Changes

### Bug Fixes

---
```
Guard as implemented (`^[[:space:]]*- `, dash+space): **0 matches → correctly rejects.** Counterfactual
using the reference's looser `^[[:space:]]*-` (bare dash, no required space): **1 match — the `---`
line itself — would incorrectly pass**, silently letting an empty section through. This independently
confirms TL adjudication 3: `- ` is required, not merely safer, and the driver is the workflow's own
`post-release` separator (which sits inside every newly opened section), not the pre-existing top-level
`---` dividers in `CHANGELOG.md` (which sit outside every version section and are never in scope for
this `awk` extraction).

---

### TS-08 — AC11/AC13: stamp commit (job 1) — VERSION, CHANGELOG date-stamp, `changes.json` key rename, single commit, no extra artifact

**Rehearsal:** Ran the "Stamp release and commit" step's exact shell (minus `git add`/`commit`/`push`,
which are not executed) against scratch copies of the branch's real `VERSION`/`CHANGELOG.md`/
`changes.json`, entirely under the session scratchpad; primary repo tree never touched (verified `pwd`
stayed at repo root throughout copy/mutate steps — no bare `mkdir`/`cd` chain that could silently fall
through to the repo root on failure).

**Expected:** `VERSION` → `0.1.48` (no suffix); `## [0.1.48] - Unreleased` → `## [0.1.48] -
2026-09-04`; `changes.json` newest key renamed `0.1.48-SNAPSHOT` → `0.1.48`; `changes.json` still
`json.load`-clean; all three files touched by one commit (per the workflow, `git add VERSION
CHANGELOG.md changes.json && git commit`), no Docker/package/CD/smoke-test step anywhere in the file
(confirmed by reading it in full — only `checkout`, shell steps, and `gh release create`).

**Result:** PASS. `VERSION` = `0.1.48`. `grep` confirms `## [0.1.48] - 2026-09-04`. `changes.json`
newest key = `0.1.48`; `python -c "import json; json.load(...)"` succeeded post-rewrite. Full file read
confirms release artifact is tag + GitHub Release only (AC13).

---

### TS-09 — AC12/AC14: tag + release creation, token source

**File:** `.github/workflows/release.yml` ("Create tag and GitHub Release" step; both jobs' `checkout`
and push steps)

**Expected:** `gh release create v{version} --target {stamp_sha} ...` after the stamp commit; both
`checkout@v4` steps use `token: ${{ secrets.RELEASE_TOKEN }}` (not the default `GITHUB_TOKEN`), and the
`gh release create` step uses `GH_TOKEN: ${{ secrets.RELEASE_TOKEN }}`.

**Result:** PASS (code review — cannot be executed; this is exactly the class of step the story's
"never dispatch, never push" constraint rules out testing live). Both jobs' `checkout` steps and the
release-creation/push steps consistently reference `secrets.RELEASE_TOKEN`, never `GITHUB_TOKEN`,
matching the AC's explicit "does not assume `GITHUB_TOKEN` can push to a protected branch."

---

### TS-10 — AC12: bump-forward commit (job 2) — next snapshot, fresh CHANGELOG section, new manifest entry, ordering preserved

**Rehearsal:** Ran "Compute next snapshot version" and "Open next version..." steps' exact shell
against the *post-stamp* scratch files from TS-08 (i.e., chained the two jobs as they would run in
sequence), same scratchpad-only discipline as TS-08.

**Expected:** `VERSION` → `0.1.49-SNAPSHOT`; a new `## [0.1.49] - Unreleased` / `### Changes` /
`### Bug Fixes` section prepended above `## [0.1.48] - 2026-09-04`; a new `0.1.49-SNAPSHOT` key
prepended to `changes.json` with an empty `new`/`modified`/`removed`/`descriptions` shape; manifest key
order remains strictly newest-first; `changes.json` still `json.load`-clean.

**Result:** PASS. `VERSION` = `0.1.49-SNAPSHOT`. Manifest keys after bump:
`['0.1.49-SNAPSHOT', '0.1.48', '0.1.46', '0.1.45']` — newest-first preserved, `json.load` clean.
CHANGELOG top-of-file shows the new empty `## [0.1.49] - Unreleased` section (with the job's own `---`
closer, which is exactly the section rehearsed empty-guard-wise in TS-07) directly above the now-dated
`## [0.1.48] - 2026-09-04`.

---

### TS-11 — Regression: `init project` / `sync devkit` behavior unaffected

**Command:** `grep -rl "version\.txt" scripts/ .claude/agents/templates/`

**Expected:** Since AC2 keeps `version.txt` alive specifically as a bridge for already-initialized
target projects' existing sync path, no consumer of `version.txt` (`check_devkit_version.sh/.ps1`,
`Sync_Devkit_Workflow*_template.md`, etc.) should need to change, and none is in this PR's file list.

**Result:** PASS. 8 files reference `version.txt`; none of them is in PR #193's changed-file list
(`.github/workflows/release.yml`, `CHANGELOG.md`, `VERSION`, `changes.json`,
`scripts/validate_templates.py`, `version.txt`, the retro file). `version.txt`'s branch value
(`0.1.48`, valid semver, no suffix) is exactly the shape these consumers already expect — zero blast
radius on `init project`/`sync devkit`.

---

## Summary

All 15 AC independently re-derived from live branch content at `b1fb4f0`, not from the TL's review
summary. Two rehearsal-only points called out in the QA brief were reproduced from scratch: (1) the
stamp/bump-forward pipelines, chained exactly as job 1 → job 2 would run, produce `VERSION 0.1.48` →
`0.1.49-SNAPSHOT`, a correctly renamed `changes.json` key, newest-first manifest ordering, and
`json.load`-clean output at every step; (2) the CHANGELOG non-empty guard's `- ` (dash+space) pattern is
not merely defensive — a bare-dash counterfactual was shown to incorrectly pass against the empty
section the workflow's own `post-release` step opens, because that section's `---` closer satisfies a
bare-dash match. `python scripts/validate_templates.py` exits 0 from a detached worktree at the PR
head. No regression risk to `init project`/`sync devkit` — no consumer of the retained `version.txt`
bridge is touched by this PR. TL's 4 nits (N1–N3 fold-in, N4 backlog) are accepted as adjudicated and
not re-litigated.

QA sign-off granted 2026-09-04.
