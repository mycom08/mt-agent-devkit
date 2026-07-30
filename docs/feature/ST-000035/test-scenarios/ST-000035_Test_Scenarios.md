# Test Scenarios — ST-000035

**Story:** Audit agent files workflow (devkit-only, Tier A detection)
**Date:** 2026-07-30
**Branch:** ST-000035/audit-agent-files-workflow
**PR:** #103

---

## Scope

Two new files (`Audit_Rules.md` — Tier A detection spec; `Audit_Agent_Files_Workflow.md` — trigger,
subagent spawn, report/approval/apply/revert mechanics), a `CLAUDE.md` trigger row (no roster
entry), a `.gitignore` addition (`.claude/agents/internal/`), a `RUNTIME_PATH_PREFIXES` addition in
`scripts/validate_templates.py`, and a `CHANGELOG.md` entry. No file under `.claude/agents/templates/`
touched — no `version.txt` bump, no `changes.json` entry (matches AC18). `Type: non-behavioral`
(Markdown/`.gitignore`/`CLAUDE.md` only) but the story's own AC demand detection-mechanics
correctness, so this pass traces the spec's logic by hand rather than rubber-stamping presence.
TL approved twice (independent A/B re-run, same verdict both times). This QA pass independently
re-derives all 18 AC from live branch file content and re-executes the differential validator gate
rather than trusting either round's summary numbers.

---

## Test Scenarios

### TS-01 — AC1/AC2/AC3: Tier A scope boundaries, wordiness and intra-file repetition out of scope

**File:** `Audit_Rules.md` §1

**Expected:** Four finding classes only (`D-n`/`RP-n`/`C-n`/`X-n`); sentence-level wordiness
rewriting explicitly out of scope; intra-file repetition explicitly out of scope with rationale
tying back to the `#77` defect (deleting the deliberate double-statement of "PO ticks AC" would
reintroduce a shipped bug).

**Result:** PASS. §1 table lists exactly the four classes. "Explicitly out of scope" bullet covers
both wordiness and intra-file repetition verbatim, citing `QA_Rules_template.md §3`'s intentional
duplication and `#77` by name — matches AC2/AC3 exactly.

---

### TS-02 — AC4: dedup common gate (>=15 contiguous lines AND target already on mandatory read list)

**File:** `Audit_Rules.md` §2 "Common gate"

**Expected:** A finding is raised only when both the length floor and the mandatory-read-list
condition hold; a file only reachable via a conditional trigger pointer does not satisfy the
read-list condition.

**Result:** PASS. Both conditions stated as a conjunction ("only raised when both hold"). Read-list
condition defined precisely: `Agent_Common.md §1`'s Project Priming/Rules/Memory sequence, plus that
role's own Rules file's own "Mandatory Reading" section — explicitly excluding conditional trigger
pointers.

**Independent detection-mechanics check (heading-match coverage):** grepped `"Mandatory Reading"`
across all 6 role Rules files (`Developer_Rules.md`, `Technical_Lead_Rules.md`, `QA_Rules.md`,
`Product_Owner_Rules.md`, `Business_Analyst_Rules.md`, `UI_UX_Designer_Rules.md`) — the literal
heading exists in only 2 of 6 (`Developer_Rules.md`, `UI_UX_Designer_Rules.md`), confirming TL's
non-blocking nit is real. Traced whether this is a correctness defect or only reduced coverage: the
gate's read-list definition is `Agent_Common.md §1`'s baseline sequence **plus** (additive) that
role's own "Mandatory Reading" section if one exists — a role's Rules file lacking that heading only
means it contributes nothing beyond the shared baseline, it does not cause the gate to accept a file
that shouldn't qualify. This can only **narrow** detection (fewer eligible targets recognized),
never produce a false-positive dedup proposal. Confirms TL round-2's classification independently
rather than trusting it. **Non-blocking**, consistent with both TL rounds.

---

### TS-03 — AC5: `RP-n` matching mechanics, uniform substitution, N>=3, frontmatter/`## Your Role` excluded, own report section, opt-in-only default

**Files:** `Audit_Rules.md` §2 "`RP-n` — role-parallel duplication"; `Audit_Agent_Files_Workflow.md`
Stage 3 approval semantics

**Expected:** Whitespace collapse + closed role-alias substitution; uniform substitution within one
instance (no cross-mapped role tokens between instances); N>=3 (vs N>=2 for `D-n`); never against
YAML frontmatter or `## Your Role`; own report section, never mixed with `D-n`; defaults to **not
selected**, user opts in per finding, no batch "approve all duplication" covers it.

**Result:** PASS. All conditions present verbatim in `Audit_Rules.md` §2, including the "file A uses
`Developer` at one point / `QA` at another, file B swaps which role appears where — not a match"
example that makes uniform substitution concrete rather than just named. Workflow Stage 3: "**never
accept a batch phrase like 'approve all duplication' or 'approve all RP' as approving every `RP-n`
finding — require each ID named explicitly**" — matches the AC's "never via a batch" clause exactly,
including the explicit carve-out that naming several IDs in one reply is fine (that is still
per-finding, just batched typing of individually-named approvals — not a semantic batch-accept).

---

### TS-04 — AC6: `<!-- audit:keep -->` absolute exclusion across all finding types

**File:** `Audit_Rules.md` §1 "Absolute exclusion"

**Expected:** Marked content never proposed for change under any finding class; checked before any
other rule; overrides every matching condition.

**Result:** PASS. Stated once in §1 as an absolute, cross-referenced in §3's contradiction carve-outs
and in the workflow Stage 1 subagent prompt's C-n instruction. No finding class is exempted from the
exclusion in the file text.

---

### TS-05 — AC7: contradiction three-condition test + four carve-outs

**File:** `Audit_Rules.md` §3

**Expected:** Same subject (actor+artifact+action) + both unconditional in their own file +
co-reachable, ALL three required; carve-outs for mode bifurcation (github/strict template dirs
excluded from scanning entirely), template-vs-`working/`-mirror pairs, role-scoped views, different
lifecycle phases.

**Result:** PASS. All three conditions and all four carve-outs present, each with the same rationale
given in the issue thread (thin-variant comment-only stripping for mode bifurcation; `Project_Priming
§15`'s sanctioned intentional divergence for the mirror carve-out; `Story_Standard.md` vs
`Story_Standard_QA.md` as the worked example for role-scoped views).

**Independent scan-scope check:** confirmed `Audit_Agent_Files_Workflow.md` Stage 1's subagent prompt
excludes `.claude/agents/templates/github/**` and `.claude/agents/templates/strict/**` "entirely"
from Step 2's scan paths — the carve-out is enforced at the scan-instruction level, not left to the
subagent's judgment at match time. Consistent with `Audit_Rules.md §3`'s "excluded from scanning
entirely" wording.

---

### TS-06 — AC8: `C-n` report-only, no edit, no winning side, approval = stated resolution

**Files:** `Audit_Rules.md` §3 "Reporting and approval"; `Audit_Agent_Files_Workflow.md` Stage 3

**Expected:** Contradiction findings propose no edit and never select a winning side; "approval" for
a `C-n` finding means the user states the resolution in their reply, not a file-edit accept/reject.

**Result:** PASS. `Audit_Rules.md`: "the audit proposes no edit and never selects a winning side."
Workflow Stage 3: "`C-n` — never an edit target. Ask the user to state the resolution for each `C-n`
finding they want to address; record their stated resolution as a note appended under that finding
... no file in the corpus changes because of a `C-n` finding by itself." Traced through Stage 4's
gate ("Runs only when at least one `D-n`/`RP-n`/`X-n` finding was approved") — `C-n` is deliberately
excluded from Stage 4's trigger condition, so a run with only `C-n` resolutions correctly skips the
apply stage entirely and goes straight to Stage 5. Internally consistent.

---

### TS-07 — AC9/AC10: workflow file + trigger; subagent spawn is self-contained, names the spec, scan paths, report format; returns findings only; no new role

**File:** `Audit_Agent_Files_Workflow.md` header, Stage 1

**Expected:** File exists, triggered by `"audit agent files"`; spawns one general-purpose subagent
with a fully self-contained prompt naming `Audit_Rules.md` as the behavior spec, the three scan
paths (with the github/strict exclusions and the `working/` runtime-path exclusions), and the exact
report format; subagent returns the finding list only, never raw corpus text; no
`auditor_instructions.md`, no roster entry.

**Result:** PASS. Stage 1's prompt is inline and self-contained — includes the spec path, all three
scan roots with their exclusions spelled out, the per-class application instructions, and the exact
section-header/line format the subagent must return. Closing instruction: "Do not edit any file. Do
not write the report file yourself — return the finding list as your final response." Header note:
"There is no `auditor_instructions.md` and no roster entry." Confirmed via grep — no
`auditor_instructions.md` file exists under `.claude/agents/working/instructions/` (6 files present,
all existing roles); `CLAUDE.md`'s Agent Roster table (lines 20–26) has no Audit/Auditor row.

---

### TS-08 — AC11: single timestamped report, `Status` header, explicit per-finding approval before any edit

**File:** `Audit_Agent_Files_Workflow.md` "Report File" section, Stage 3

**Expected:** `.claude/agents/internal/audit_report_YYYYMMDD_HHMMSS.md`, one report in flight; header
carries `**Status:** pending-approval | applying | complete`; no file edited before explicit
per-finding approval (class-specific semantics per AC5/AC8 above).

**Result:** PASS. Path, header block, and "only one report is ever in flight" all present. Stage 4
("Apply Batch") is gated behind Stage 3 ("Runs only when at least one ... finding was approved") —
traced the stage sequence and confirmed no code path reaches a file edit without passing through
Stage 3's approval gate first.

---

### TS-09 — AC12: startup crash-recovery — all three `Status` values have an explicit, non-overlapping branch

**File:** `Audit_Agent_Files_Workflow.md` Stage 0 table

**Expected:** `pending-approval` → report stale timestamp, delete silently, continue to fresh scan;
`applying` → halt, print report path + finding IDs, instruct manual `git status`/`git diff`
resolution, no auto-delete, no scan; `complete` → delete, continue. Every value the header can hold
must have a branch; none may fall through to another.

**Result:** PASS — traced by hand as a three-way switch over the closed `Status` enum:
1. Header can only ever hold one of the three literal values (per the header format `pending-approval
   | applying | complete` — no other value is ever written anywhere in the file by any stage).
2. Stage 0's table gives one row per value, with explicit action text per row and no "else"/default
   branch that could silently swallow an unrecognized value into the wrong row.
3. `applying` is the only row that halts rather than continuing — correctly the most conservative
   choice, since only this state means a corpus file may be mid-edit.
4. `complete` is documented as "should be unobservable" (both normal exits delete the file) but still
   gets an explicit branch rather than being left to fall into `pending-approval`'s row — this is the
   exact class of gap TL's memory (Fact 4, referenced in the TL retro) flags as a recurring defect
   pattern, and it is handled correctly here.
No value is left unhandled; no two rows overlap in the same crash scenario.

---

### TS-10 — AC13: report deleted on completion, whether applied or cancelled; one manual exception

**File:** `Audit_Agent_Files_Workflow.md` Stage 2 step 2, Stage 5 steps 1–2

**Expected:** Report deleted on both the applied path and the cancelled/no-op path; the only
exception is the Stage 0 `applying`-crash halt, which is manual cleanup, not automatic.

**Result:** PASS. Stage 2 step 2: zero-findings run deletes the report immediately, skips Stage 3
entirely. Stage 5 steps 1–2 (reached from both the "kept" and "reverted" outcomes of Stage 4, per
TS-11 below): set `Status: complete`, then delete. Stage 5 step 2 states the one exception explicitly
("never reached from this stage — halts before Stage 5"). Traced all three exit paths (zero-findings,
approved-then-applied, approved-then-reverted) and confirmed each one reaches a delete step except
the `applying`-crash halt, which by definition never reaches Stage 5 in the same run.

---

### TS-11 — AC15/AC16: validator explicit-path gate + dedicated-branch git-scoped revert, traced end to end

**File:** `Audit_Agent_Files_Workflow.md` Stage 4

**Expected:** Baseline and post-edit validator runs both use explicit paths
(`.claude/agents/templates .claude/agents/workflows .claude/agents/working`); any new `[ERROR]` line
after the batch (regardless of file) reverts the whole batch; revert is `git checkout --` scoped to
exactly the files in the post-edit `git diff --stat`, never a broader destructive command; apply runs
on a dedicated `audit/apply-<timestamp>` branch, never the invoking branch.

**Result:** PASS — traced Stage 4 as a 7-step sequence:
1. `Status: applying` set **before** any corpus file is touched (this is what makes it a valid crash
   marker for TS-09's `applying` row).
2. Dedicated branch created from the current branch — never edits in place.
3. Baseline `git diff --stat` (expected empty) + baseline validator run, explicit paths, both
   `[ERROR]`/`[KNOWN_ISSUE]` lines recorded verbatim.
4. Edits applied per `Audit_Rules.md`'s per-class proposed-edit description.
5. Post-edit `git diff --stat` (now non-empty — this becomes the revert scope) + second validator run,
   same explicit paths as step 3.
6. Differential comparison: any `[ERROR]` line in post-edit not present in baseline → revert via
   `git checkout -- <every file in the post-edit diff --stat>`; no new line → commit on the dedicated
   branch.
7. Restates git (not the validator verdict) as the primary revert mechanism, scoped, never a wider
   `reset`/`clean`.
Confirmed both outcomes (revert and keep) converge at Stage 5 (TS-10), so the report always gets
cleaned up regardless of which way Stage 4 resolves — no path leaves a report parked on the
`applying` status without a starting halt condition.

**Second-round TL nit re-verified:** the revert path leaves the user checked out on the freshly
created `audit/apply-<timestamp>` branch with no commits (Stage 5's "branch ready for review" message
is conditional on the batch being *kept*, per Stage 5 step 3's parenthetical). Confirmed this
reading is correct — traced Stage 5 step 3's message template: the "tell the user it is ready for
review/merge" sentence is scoped to "if a branch was created **and kept**." On a revert, the branch
still exists (created in step 2) but is left with zero commits and no instruction to switch the user
back or delete it. **Non-blocking** (matches TL's classification — no data loss, no incorrect
behavior, just a leftover empty branch and no checkout-back instruction) — same follow-up bucket as
TL's other three nits, correctly deferred to ST-000036 rather than blocking this PR.

---

### TS-12 — AC14: `.gitignore` addition

**File:** `.gitignore`

**Expected:** `.claude/agents/internal/` added to the root `.gitignore`.

**Result:** PASS. Diff confirms the line added with an explanatory comment, correctly grouped near
the existing `working-record/`/`tmp/` gitignore entries.

---

### TS-13 — AC17: `CLAUDE.md` trigger table + full section; no roster entry

**File:** `CLAUDE.md`

**Expected:** New row in the "Available Commands" help table; new `## Audit Agent Files Workflow`
section following the pattern of the other 5 top-level devkit commands; no Agent Roster row.

**Result:** PASS. Both the Available Commands table row (line 105 area) and a full section (lines
297–305) were added, matching the precedent of Analyst/Init Project/Update Project/Build
Software/Apply Retros (each gets both). Confirmed via grep: `## Agent Roster` table (lines 20–26)
lists only the 6 existing Scrum roles — no Audit/Auditor row added anywhere in `CLAUDE.md`.

---

### TS-14 — AC18: no `templates/` file touched; no `version.txt`/`changes.json` change

**Commands:** `git diff main..HEAD --stat -- .claude/agents/templates/ .claude/agents/working/instructions/ version.txt changes.json`

**Expected:** Empty diff.

**Result:** PASS. Zero files under `.claude/agents/templates/` appear in the PR diff; `version.txt`
and `changes.json` are both absent from the changed-file list. `CHANGELOG.md`'s new entry is
correctly labeled "internal — devkit operational workflow only, no template/version change."

---

### TS-15 — Layer-1 automation gate (regression suite), differential, worktree-vs-worktree methodology

**Commands (both run via `git worktree add`, per QA_Memory Fact 2/3 — never against the live working
tree, which has uncommitted retro edits per this run's own instructions):**
```
python scripts/validate_templates.py .claude/agents/templates .claude/agents/workflows .claude/agents/working
```
run against an `origin/main` worktree and an `origin/ST-000035/audit-agent-files-workflow` (PR head,
`d5515c8`) worktree.

**Expected:** Zero new `[ERROR]`/`[KNOWN_ISSUE]` lines on the PR branch versus `main`.

**Result:** PASS, with a methodology correction worth recording. An initial run directly in the
primary working directory (not a worktree) produced **53** `[ERROR]` lines — 14 fewer than either TL
round's reported baseline (~70 / 67). Root cause: several gitignored `.claude/agents/working/working-
record/*.md` files physically exist on disk in the primary working directory (left over from prior
agent sessions) but are absent from a fresh `git worktree` checkout (worktrees only materialize
git-tracked files). `_resolve_file_ref`'s repo-verbatim root checks actual disk presence, so those 14
"unresolved reference" errors silently disappear whenever the check is run from a directory that
happens to have those runtime files present — an environment artifact, not a PR effect. Re-ran both
sides from matched `git worktree` checkouts (main and PR head), which is the correct apples-to-apples
methodology: both sides now report **67 `[ERROR]` + 3 `[KNOWN_ISSUE]` = 70 total**, and a full sorted
diff of the two output sets is **byte-identical (0 lines differ)** — confirming TL round 2's "67
`[ERROR]`, zero new" figure independently, and correcting round 1's "~70 violations" phrasing (which
conflated `[ERROR]` and `[KNOWN_ISSUE]` counts, as TL round 2 itself already flagged). Neither new
file (`Audit_Rules.md`, `Audit_Agent_Files_Workflow.md`) appears in any violation on either side.

**Note for QA memory:** worktree-based validator comparison is not merely a convenience for avoiding
working-tree disturbance (Fact 2's stated reason) — it is load-bearing for correctness, because
gitignored runtime files present in a long-lived primary working directory can silently change the
error count depending on which directory the command is run from. A non-worktree run should never be
treated as a baseline measurement for a differential gate.

**CI cross-check:** `gh api repos/mycom08/mt-agent-devkit/commits/bbd85f5/check-runs` — `Layer-1
invariant check`: `success`. The PR head commit (`d5515c8`) shows no CI run, correctly explained by
both the CI workflow's `pull_request.paths` filter (`templates/**`+`workflows/**`) and that commit
touching only `working/memory/`+`working/retros/` — matches TL round 2's structural explanation,
re-derived independently rather than trusted.

**Skip-CI tag check:** `git log` on the code-bearing commit (`bbd85f5`) — message
`"[ST-000035][DEVKIT]: add audit agent files workflow (Tier A detection)"`, no `[skip ci]` tag.
Matches the story's explicit "do not skip CI" instruction (PR #99 precedent).

---

### TS-16 — Stub-marker scan

**Command:** grep `TODO|PLACEHOLDER|FIXME|XXX|<insert|TBD` (case-insensitive) across both new files.

**Expected:** No matches.

**Result:** PASS. Zero matches in `Audit_Agent_Files_Workflow.md` or `Audit_Rules.md`.

---

## Summary

All 18 AC independently re-derived from live branch file content — PASS. Detection-mechanics traced
by hand for all four finding classes (`D-n`, `RP-n`, `C-n`, `X-n`) and all three crash-recovery
states (`pending-approval`/`applying`/`complete`) — internally consistent with the AC and with each
other; no dangling state, no fall-through branch, no path that edits a corpus file without clearing
the approval gate first. TL's four non-blocking nits spot-checked (the "Mandatory Reading" heading
coverage gap and the reverted-batch leftover-branch gap) and independently confirmed as genuinely
non-blocking (narrows detection / leaves a harmless empty branch — neither is a correctness defect),
consistent with TL's own classification. Differential Layer-1 validator gate re-run from matched
`git worktree` checkouts (not the disturbed primary working tree) — 70 total findings on both `main`
and PR head, byte-identical sorted diff, zero new. CI green on the code-bearing commit; no `[skip
ci]` tag applied. No stub markers. No `templates/` file touched; no `version.txt`/`changes.json`
change, consistent with AC18.

QA sign-off granted 2026-07-30.
