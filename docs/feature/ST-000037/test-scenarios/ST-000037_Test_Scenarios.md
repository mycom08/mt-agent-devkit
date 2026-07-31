# Test Scenarios — ST-000037

**Story:** Inject Auditor into target projects + wire sync devkit / update project audit stage
**Date:** 2026-07-31
**Branch:** ST-000037/inject-auditor-target-projects
**PR:** #104 (head `7988eda`; CI-verified template state `88bd8dc` — the later commit is TL's own retro addendum, not a template change)

---

## Scope

New injectable rules file (`Audit_Rules_template.md`), a carve-out in the existing `## Agent File
Integrity` section of `CLAUDE_Shared_template.md`, a new detect-only "Stage 4 — Audit Pass" in
`Sync_Devkit_Workflow_template.md` and `Update_Project_Workflow.md`, the matching enumeration bump
(9→10 rules files) across `Init_Project_Workflow.md`, `Update_Project_Workflow.md`, both
`Sync_Devkit_Workflow*` templates, `scaffold_mechanical.sh`, `Build_Software_Workflow.md`, and (round-2
CR-1 fix) `Refine_Prototype_Workflow_Shared_template.md`. `version.txt` bumped 0.1.40→0.1.41,
`changes.json` entry with 4 files (1 `new`, 3 `modified`) and per-file descriptions. `Type: behavioral`
— touches `scaffold_mechanical.sh` and the sync/update pipelines, so both the Layer-1 gate and a
scaffold-output regression diff are required (`QA_Memory.md` Fact 4). TL approved on round 2 after a
round-1 CR-1 finding (missed 20th-rules-file ripple site in `Refine_Prototype_Workflow_Shared_template.md`).
This QA pass independently re-derives all 14 AC from live branch content rather than trusting either
review round's summary.

---

## Test Scenarios

### TS-01 — AC1: `Audit_Rules_template.md` created, injectable counterpart scoped correctly

**File:** `.claude/agents/templates/rules/Audit_Rules_template.md`

**Expected:** New file under `templates/rules/` with `_template` suffix; single `MA-n` finding class
(mode-adaptation artifact only); explicitly states it has no `templates/` access and cannot compare
against source; devkit-internal Tier A classes (`D-n`/`RP-n`/`C-n`/`X-n`) explicitly out of scope;
`<!-- audit:keep -->` absolute exclusion.

**Result:** PASS. File exists, 55 lines, correct suffix. §"The Only Finding Class" defines exactly one
class (`MA-n`) with 4 shapes (orphan heading, dangling GitHub reference, internal contradiction from
partial strip, broken internal cross-reference). Preamble states "has no access to
`.claude/agents/templates/`... cannot compare a written file against its source template." `<!--
audit:keep -->` listed as "Absolute exclusion... checked before every other rule below."

---

### TS-02 — AC2: Agent File Integrity carve-out, correct scope, `Project_CLAUDE_template.md` untouched

**File:** `.claude/agents/templates/shared/CLAUDE_Shared_template.md`

**Expected:** New bullet inside the existing `## Agent File Integrity` section (not a new section);
names the audit as a workflow step, not an agent role or a third writer of protected paths; names
`sync devkit`/`update project` as the only two permitted invokers; `Project_CLAUDE_template.md`
untouched (it has no mode-adapted file and `update project` doesn't reach it).

**Result:** PASS. `git show 88bd8dc:.../CLAUDE_Shared_template.md` line 63 — the new "**Audit
carve-out.**" bullet sits directly under the pre-existing "only operation that may update protected
paths is `sync devkit`" bullet, inside `## Agent File Integrity` (confirmed by reading the full
section, not just the diff hunk). Ends "No other workflow may invoke this audit pass." Confirmed
`.claude/agents/templates/Project_CLAUDE_template.md` is absent from the PR's changed-file list and
`grep -i audit` on that file at `88bd8dc` returns zero hits.

---

### TS-03 — AC3: no agent-role artifacts added

**Command:** `git ls-tree -r 88bd8dc --name-only | grep -i auditor`; grep for an `**Assigned:**`
enumeration entry and an Agent Roster row.

**Expected:** No `auditor_instructions_template.md`; no roster table entry; no `**Assigned:**`
valid-values entry.

**Result:** PASS. No file matching `auditor*` anywhere in the tree. `Story_Standard_template.md`'s
`**Assigned:**` valid-values list (lines 41/443) still reads `Developer | Technical Lead | QA |
Business Analyst | UI/UX Designer` — unchanged, 5 roles, no "Auditor" added. `CLAUDE_Shared_template.md`
Agent Roster table (lines 20–26, pre-existing) has no Audit/Auditor row — the carve-out from TS-02
lives in the File Integrity section, not the roster.

---

### TS-04 — AC4: `sync devkit` Stage 4 — scope, exclusions, silent-when-clean

**File:** `.claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md` — new "Stage 4 — Audit
Pass (detect-only)"

**Expected:** Runs only if Stage 2 wrote ≥1 in-scope file; scope = files Stage 2's written-files log
actually wrote this run whose strategy is model-generated (`rules/` adapt-to-mode, `instructions/`
merge, `CLAUDE.md` merge); excludes verbatim-overwrite writes (workflow/script files), wiki files, and
resolved-but-not-written files (checksum skip, failed fetch); empty scope → skip silently, "print
nothing, spawn nothing."

**Result:** PASS. Text matches exactly. Traced the cited mechanism rather than accepting the prose:
Stage 2's own preamble ("Log each file as it is written. If any file fails, log the error and
continue" — line 113) plus the Pipeline Rule "**Log every file written**" (line 396) plus "**Checksum
skip is silent**... do not appear in the final written-files report" (line 395) together make the
scope list a real, computable runtime artifact, not unbacked hand-waving. The strategy taxonomy the
scope list depends on (`#### Rules files — Adapt to mode` / `#### Instruction files — Merge` /
`#### CLAUDE.md — Merge` vs `#### Workflow files — Overwrite` / `#### Script files — Overwrite`) exists
as real subheadings in the same file.

---

### TS-05 — AC5: `update project` Stage 4 — same stage, narrowed exclusion (no checksum pre-filter)

**File:** `.claude/agents/workflows/Update_Project_Workflow.md` — new "Stage 4 — Audit Pass
(detect-only)"

**Expected:** Same scope/exclusion shape as AC4, except only the failed-write exclusion applies (this
workflow has no checksum pre-filter).

**Result:** PASS. Text at line 257 explicitly states: "This workflow has no checksum pre-filter
(unlike `sync devkit`), so only the **failed-write** exclusion applies here." Confirmed the underlying
written-files-log mechanism exists here too (line 70: "Log each file as it is written. If any file
fails, log the error and continue"; line 315: "Log every file written").

---

### TS-06 — AC6: `init project` does not run the audit

**File:** `.claude/agents/workflows/Init_Project_Workflow.md`

**Expected:** No stage spawns the audit subagent; only incidental mentions (rules-file enumeration,
`.gitignore` comment) are permitted.

**Result:** PASS. `grep -i audit` on `Init_Project_Workflow.md` at `88bd8dc` returns exactly 2 hits:
the `Audit_Rules` name inside the verbatim-rules-file enumeration (line 208) and a `.gitignore`
heredoc comment ("# Audit workflow reports — runtime output, never committed", line 340). Neither is a
stage invocation. No `## Stage` heading in the file mentions spawning an audit subagent.

---

### TS-07 — AC7: target-side scan isolation — fresh general-purpose subagent, self-contained prompt

**Files:** Both Stage 4 sections (`Sync_Devkit_Workflow_template.md`, `Update_Project_Workflow.md`);
compared against `Audit_Agent_Files_Workflow.md` Stage 1 (ST-000035 precedent).

**Expected:** "Spawn one general-purpose subagent (never a persistent role or session — fresh every
run)"; prompt is self-contained and names the deployed `Audit_Rules.md` copy as the complete behavior
spec; same isolation mechanism as the devkit-internal audit's Stage 1.

**Result:** PASS. Both Stage 4 sections open with "**1. Spawn one general-purpose subagent** (never a
persistent role or session — fresh every run)" — identical wording. The inline prompt is fully
self-contained: names `.claude/agents/rules/Audit_Rules.md` (sync devkit, the project's own deployed
copy) or `{TARGET_PROJECT}/.claude/agents/rules/Audit_Rules.md` (update project) as "the complete and
only behavior spec," lists the scope files inline, and instructs "Do not edit any file... the
orchestrator persists it if non-empty." Matches `Audit_Agent_Files_Workflow.md`'s own "anonymous
general-purpose subagent, spawned fresh on every run" pattern (confirmed by reading that file's header
at `88bd8dc` directly, not from memory).

---

### TS-08 — AC8: findings file an Issue labelled `audit:contribution`, never `retro:contribution`

**Files:** Both Stage 4 sections.

**Expected:** `gh issue create --repo mycom08/mt-agent-devkit --label "audit:contribution"`.

**Result:** PASS. Both Stage 4 §3.b use `--label "audit:contribution"` verbatim. Grepped both files
for `retro:contribution` — zero hits (would only be a problem if accidentally copy-pasted from the
`apply retros` fallback this pattern is modeled on).

---

### TS-09 — AC9: `gh` unavailable/unauthenticated fallback matches `Sprint_Workflow_Shared_template.md`

**Files:** Both Stage 4 sections §3.b; compared against `Sprint_Workflow_Shared_template.md`'s Devkit
Contribution export fallback.

**Expected:** Same `gh auth status` → authenticated/not-authenticated branch shape; on the fallback
path, write the report and instruct the user to open the Issue manually.

**Result:** PASS. Both files: "**Not authenticated or `gh` unavailable:** tell the user the report has
been written to `<path>` and instruct them to open an Issue labeled `audit:contribution` on
`mycom08/mt-agent-devkit` with the report's contents." Structurally identical to
`Sprint_Workflow_Shared_template.md`'s "Not authenticated or `gh` unavailable: inform the user that the
export file has been written to... Instruct them to open an Issue labeled `retro:contribution`..." —
same two-branch shape, correctly substituting the audit's own label and path. Deliberate divergence
correctly present: `sync devkit`'s fallback path explicitly leaves the report file in place ("it is
the only record until the user files it manually"), matching the Sprint fallback's non-deletion
behavior, while the authenticated path deletes it after filing.

---

### TS-10 — AC10: report file deleted after Issue is filed

**Files:** Both Stage 4 sections §3.b (authenticated branch).

**Expected:** After `gh issue create` succeeds, the local report file is deleted; only the fallback
(manual-filing) path retains it.

**Result:** PASS. Both files: "Report the Issue URL to the user, then **delete the report file** — the
Issue is now the record." Confirmed this line is present only in the authenticated branch, and the
"Not authenticated" branch explicitly says "Leave the report file in place in this case."

---

### TS-11 — AC11: `.claude/agents/internal/` added to target project `.gitignore` by the scaffold step

**File:** `.claude/agents/working/scripts/scaffold_mechanical.sh`; `Init_Project_Workflow.md`'s
documented `.gitignore` block.

**Expected:** github-mode `.gitignore` gains a `.claude/agents/internal/` entry; strict mode's blanket
`.claude/agents/` entry already covers it, so no separate strict-mode line is required.

**Result:** PASS — confirmed both by reading the script and by an executable diff (see TS-15). The
script's github-mode `.gitignore` heredoc gains:
```
# Audit workflow reports — runtime output, never committed
.claude/agents/internal/
```
`Init_Project_Workflow.md`'s documented block gains the same 3 lines, with an explicit note
immediately after the strict-mode block: "`Mode: strict`'s blanket `.claude/agents/` entry already
covers `.claude/agents/internal/`... no separate line is added for strict mode." The executable
scaffold run (TS-15) confirms this empirically: github `.gitignore` output differs, strict does not.

---

### TS-12 — AC12: `audit:contribution` label exists on the devkit repo

**Command:** `gh label list --repo mycom08/mt-agent-devkit --search audit --json name,description`

**Expected:** Label exists with an accurate description.

**Result:** PASS.
```json
[{"description":"Target-project mode-adaptation audit finding, reported from sync devkit / update project","name":"audit:contribution"}]
```

---

### TS-13 — AC13: devkit-internal file-count tables updated (4 sites)

**Files:** `Init_Project_Workflow.md`, `Update_Project_Workflow.md`, `Sync_Devkit_Workflow_template.md`,
`.claude/agents/working/workflows/Sync_Devkit_Workflow.md` (mirror).

**Expected:** All 4 sites bumped from the 9/19-rules-file count to 10/20; no stale `9 verbatim`/`19
rules`/`of 19` text remaining anywhere outside historical record (CHANGELOG, memory, retros).

**Result:** PASS. `Init_Project_Workflow.md` bumped in 4 places (Stage 2 tier summary ×2, source-table
row, mechanical-tier prose, Stage 4 restated count, closing pipeline-rule bullet — 6 total occurrences,
all consistent at 10/20). `Update_Project_Workflow.md` and both `Sync_Devkit_Workflow*` files have
their "Applies to:" and "Expected files — `rules/`" enumerations bumped to include `Audit_Rules.md`.
Corpus-wide grep for `9 verbatim|19 rules|of 19|9/19` across `.claude/agents/` (excluding
`retros/`/`Developer_Memory.md`/`Technical_Lead_Memory.md`/`CHANGELOG.md`, which are historical record
by design) returns **zero** remaining hits — the ripple is fully closed, including the round-1 CR-1
site (`Refine_Prototype_Workflow_Shared_template.md`) that was outside AC13's literal 4-file
enumeration but is the same ripple class.

---

### TS-14 — AC14: `version.txt` bump + `changes.json` entry with per-file descriptions

**Files:** `version.txt`, `changes.json`

**Expected:** `version.txt` 0.1.40→0.1.41; new `0.1.41` entry at the top of `changes.json`, descriptive
per-file entries for every `new`/`modified` path.

**Result:** PASS. `version.txt` = `0.1.41`. `changes.json`'s `0.1.41` entry: 1 `new`
(`Audit_Rules_template.md`), 3 `modified` (`CLAUDE_Shared_template.md`, `Sync_Devkit_Workflow_template.md`,
`Refine_Prototype_Workflow_Shared_template.md` — the last one added by the round-2 CR-1 fix). Parsed
the JSON directly: valid, version-key order still strictly descending (`0.1.41` → `0.1.40` → …),
`descriptions` key set is exactly the union of `new`+`modified` (4 keys, 4 descriptions, no orphan, no
omission), and all 4 referenced paths exist on disk at `88bd8dc`.

---

### TS-15 — Layer-1 automation gate (regression suite), differential, matched-worktree methodology

**Command (both sides run from `git worktree add`, per `QA_Memory.md` Fact 2):**
```
python scripts/validate_templates.py .claude/agents/templates .claude/agents/workflows .claude/agents/working
```
Run against an `origin/main` worktree (`0c7d144`) and an `88bd8dc` worktree (CI-verified head).

**Expected:** Zero new `[ERROR]`/`[KNOWN_ISSUE]` lines versus `main`.

**Result:** PASS. Both sides: **67 `[ERROR]`, 0 `[KNOWN_ISSUE]`** (exit 1 on both, expected per
`QA_Memory.md` Fact 2 — the corpus baseline is non-zero on `main` too). Sorted-output diff is a single
line: `Sync_Devkit_Workflow.md:194` → `:196`, the same pre-existing unresolved-reference finding
shifted by the 2-line intentional-divergence note this story adds — not a new violation. Neither
`Audit_Rules_template.md` nor any other changed file appears in any violation on either side.
Independently confirms TL round 2's identical figure without trusting it.

**Fixture self-test:** `bash scripts/test/run.sh` from the PR worktree — `5 passed, 0 failed`
(invariants 1/2/3/4/6; invariant 5 has no standalone fixture per `QA_Memory.md` Fact 9).

**Shell syntax:** `bash -n scaffold_mechanical.sh` — zero errors.

**CI cross-check:** `gh api .../commits/88bd8dc.../check-runs` — `Layer-1 invariant check`:
`completed`/`success`, `head_sha` matches `88bd8dc` exactly (the PR's CI-verified template state).

---

### TS-16 — Scaffold-output regression diff (Type: behavioral, touches `scaffold_mechanical.sh` —
`QA_Memory.md` Fact 4)

**Command:** `scaffold_mechanical.sh` run for both `github` and `strict` mode from both an `origin/main`
worktree and the `88bd8dc` worktree, into 4 scratch directories, then `diff -rq` each mode's pair.

**Expected:** Only the intended deltas appear — new `Audit_Rules.md` in `rules/`, updated
`Sync_Devkit_Workflow.md`/`Refine_Prototype_Workflow.md`, bumped `devkit_version.txt`, and (github mode
only) the `.gitignore` addition. No unexpected file added, removed, or changed.

**Result:** PASS. github-mode diff: exactly `devkit_version.txt` (0.1.40→0.1.41, expected),
`Audit_Rules.md` added under `rules/` (expected, new file), `Refine_Prototype_Workflow.md` and
`Sync_Devkit_Workflow.md` content differ (expected — Stage 4 + enumeration bump), `.gitignore` differs
(expected — `.claude/agents/internal/` addition, confirmed via `diff` to be exactly those 3 added
lines). strict-mode diff: same 4 deltas minus the `.gitignore` diff (expected — strict mode's blanket
ignore already covers `internal/`, matching TS-11 and the explicit note in `Init_Project_Workflow.md`).
No unexpected file appeared in either mode.

---

### TS-17 — Stub-marker scan

**Command:** grep `TODO|PLACEHOLDER|FIXME|XXX|<insert|TBD` (case-insensitive) across the 4
story-relevant changed files (`Audit_Rules_template.md`, `CLAUDE_Shared_template.md`,
`Sync_Devkit_Workflow_template.md`, `Update_Project_Workflow.md`).

**Expected:** No genuine stub markers — pre-existing legitimate uses of "placeholder"/`[UPDATE
REQUIRED]` in unrelated, unchanged sections of these files are not stub markers.

**Result:** PASS. All hits are pre-existing, legitimate design language in unrelated sections
(`{{PLACEHOLDER}}` merge-step vocabulary, `[UPDATE REQUIRED]` markers Sync/Update already write for
missing sections, `ST-XXXXXX` literal examples) — none inside the new Stage 4 sections or
`Audit_Rules_template.md`, and none is a literal `TODO`/`FIXME`/`XXX` left by the implementer.

---

## Summary

All 14 AC independently re-derived from live branch content at `88bd8dc` (CI-verified head) — PASS.
Both new mechanisms this story depends on (Stage 2's written-files log; the strict/github
`.gitignore`/blanket-ignore split) were traced to real, pre-existing structure rather than accepted as
prose. The round-1 CR-1 fix (missed 20th-rules-file site in
`Refine_Prototype_Workflow_Shared_template.md`) was independently re-verified via a corpus-wide grep
returning zero remaining stale sites. Differential Layer-1 validator gate: 67 `[ERROR]`/0
`[KNOWN_ISSUE]` both sides, single pre-existing line-number-shift diff, zero new. Fixture suite 5/5
PASS. `bash -n` clean. CI green, head_sha matches exactly. Executable scaffold-output regression diff
(both modes) shows only the intended deltas — no unexpected file. No stub markers.

QA sign-off granted 2026-07-31.
