# Test Scenarios — ST-000028

**Story:** New workflow: UI/UX Refine — direct orchestrator/user prototype iteration loop
**Date:** 2026-07-28
**Branch:** ST-000028/refine-prototype-workflow
**PR:** #87

---

## Scope

New injected workflow template (`Refine_Prototype_Workflow_Shared_template.md` + `github`/`strict`
thin variants), a trigger-table row in `CLAUDE_Shared_template.md`, workflow-file-count ripple
across `Sync_Devkit_Workflow_template.md` (+ working mirror), `Init_Project_Workflow.md`,
`Update_Project_Workflow.md`, `Build_Software_Workflow.md`, and `scaffold_mechanical.sh`'s
`SPLIT_WORKFLOWS` array (a changed `.sh` file — classified `Type: behavioral`, full validation
path, not fast-path sign-off). TL round-1 review found 3 blockers (CR-1/CR-2: repo-creation step
referenced devkit-only paths that don't exist in a target project; CR-3: `Loop Status: ended` had
no resume branch). Developer fixed all 3; TL round-2 approved. This QA pass independently
re-verifies all 9 AC against current file content and re-derives CR-1/CR-2/CR-3 from the live diff
rather than trusting the round-2 review summary.

---

## Test Scenarios

### TS-01 — AC1: explicit trigger, orchestrator acts as UI/UX Designer directly, no agent spawn

**File:** `Refine_Prototype_Workflow_Shared_template.md` lines 33–39, Pipeline Rules bullet

**Expected:** `refine prototype` trigger starts the loop; orchestrator reads UI/UX Designer
instructions/rules and acts as that role directly for the whole workflow; no Designer (or any
other) agent is spawned, including during repo setup.

**Result:** PASS. "Triggered by: `"refine prototype"`"; "**Explicit-trigger-only.** This workflow
never starts implicitly from a UI-shaped request elsewhere in a session"; "The orchestrator acts as
UI/UX Designer directly for the entire duration of this workflow ... **Do not spawn a UI/UX
Designer agent** (or any other agent) at any point in this workflow, including repo setup." Pipeline
Rules restates: "No agent spawn, ever, in this workflow."

---

### TS-02 — AC2: locate/create `-ui-prototype` repo via Build Software Path B conventions; code-empty; framework sourcing (CR-1 re-verification)

**File:** `Refine_Prototype_Workflow_Shared_template.md` Step 1 (lines 72–96)

**Expected:** Reuses an existing `<repo>-ui-prototype` companion repo if present; otherwise asks
the user where to create one, then creates it using the same repo conventions as Build Software
Stage 4 Path B (naming, `git init` + `gh repo create` in github mode only, `scaffold_mechanical.sh`
conventions, lean 3-role adaptive tier, `UI_Prototype_Rules.md` as DoD). Repo is left code-empty;
Build Software's "UI Prototype Scaffold Generation" agent is never reused. Framework comes from the
paired repo's stack, or is asked once at loop start.

**Independent re-verification of CR-1 fix (not trusting TL's round-2 summary):**
- `grep -n "agents/working\|Build_Software_Workflow\|scaffold_mechanical" ` against all 3 new
  template files returns exactly **one** hit, inside a negative/explanatory sentence: "A target
  project's own file tree has no `templates/` directory and no
  `.claude/agents/working/scripts/scaffold_mechanical.sh` — those exist only inside the devkit
  repository itself, not here." No executable reference to either path remains anywhere in the 3
  files.
- The replacement mechanism fetches every mechanical/lean-adaptive-tier file from
  `{DEVKIT_SOURCE_URL}/.claude/agents/templates/...`, reading `{DEVKIT_SOURCE_URL}`/
  `{DEVKIT_VERSION}` from the target project's own `CLAUDE.md`, reusing the fetch mechanics this
  project's own (real, injected) `Sync_Devkit_Workflow.md` documents (WebFetch + curl fallback,
  rules-mode-adaptation, split-workflow shared+mode combination) — a mechanism a target-project
  session can actually execute, unlike the removed literal script call.
- "Leave the repo code-empty ... this workflow never invokes Build Software's own repo-scaffolding
  automation (its "UI Prototype Scaffold Generation" agent reads `repo_structure.md` and
  hard-blocks without `ui_design.md`, neither of which exists here)" — confirmed present, matches
  AC2 exactly.
- `UI_Prototype_Rules.md` recorded as DoD (step 4, second-to-last bullet).
- Framework: step 5 — reuse paired-repo stack if known, else ask once at loop start, recorded in
  state. Matches AC2's framework clause.

**Result:** PASS.

---

### TS-03 — AC3: auto-detect and serve prototype locally, same convention as `run` skill

**File:** `Refine_Prototype_Workflow_Shared_template.md` Step 2 (lines 99–101)

**Expected:** Auto-detects project type and starts/serves locally using the same detection
convention as the built-in `run` skill.

**Result:** PASS. "Auto-detect the prototype's project type and start/serve it locally using the
same detection convention as the built-in `run` skill (package manager / framework detection,
dev-server start command, surfaced local URL)." Skip-serving-if-code-empty edge case for iteration
0 also covered.

---

### TS-04 — AC4: per-iteration apply → review → explicit continue/stop, no fixed cap

**File:** `Refine_Prototype_Workflow_Shared_template.md` Step 3 (lines 105–120)

**Expected:** Each iteration: orchestrator applies the requested change, user reviews it running
locally and gives feedback; after every iteration the orchestrator stops and explicitly asks
whether to continue or stop; no fixed iteration cap.

**Result:** PASS. Sub-steps 1–3 (ask/apply/review) then sub-step 6: "**Stop and ask the user
explicitly:** \"Continue iterating, or stop here?\" There is no fixed iteration cap." Continue
loops back to sub-step 1; Stop sets `Loop Status: ended` and proceeds to Step 4.

---

### TS-05 — AC5: commit directly, no PR/review gate, `prototype adaptation:` prefix, scoped exception

**File:** `Refine_Prototype_Workflow_Shared_template.md` Step 3 sub-step 4 (lines 112–115)

**Expected:** Commits go directly to the prototype repo with no PR/review gate, using commit
message prefix `prototype adaptation: <brief description>` — never `Story:`/Conventional Commits —
and this no-review exception applies only to the prototype repo, never a production repo.

**Result:** PASS. "**Commit directly to the prototype repo — no PR, no review gate.** This
no-review exception applies only to the prototype repo, never to any production repo:" followed by
the exact prefix requirement and explicit exclusion of `Developer_Rules.md §6` /
`UI_UX_Designer_Rules.md §6` for this repo's commits. Also restated in Pipeline Rules:
"**Prototype-repo commits are the only no-review-gate exception in this project** — it never
extends to a production repo."

---

### TS-06 — AC6: loop state in target project's `.claude/agents/tmp/refine_prototype_state.md`, resumable, bridges two repos

**File:** `Refine_Prototype_Workflow_Shared_template.md` Pipeline State section (lines 43–68)

**Expected:** State lives in the target project (never inside the prototype repo), exists from
iteration 0 before a prototype repo is created, same resumability convention as
`build_software_state.md`, and records `Prototype Repo Path:` (absolute) plus each iteration's
commit SHA to bridge the two working directories.

**Result:** PASS. "The orchestrator maintains `.claude/agents/tmp/refine_prototype_state.md` — **in
this target project, never inside the prototype repo**"; "This file must exist from iteration 0,
before Step 1 has produced a prototype repo at all." State file format block includes
`**Prototype Repo Path:**` and each `Iterations` entry records `Commit: <sha>`.

---

### TS-07 — AC7: mode-dependent push behavior (github live push, strict local-only)

**Files:** `Refine_Prototype_Workflow_Shared_template.md` Step 3 sub-step 4; deployed-output check
(`scaffold_mechanical.sh` dry run, see TS-11)

**Expected:** GitHub mode pushes each iteration's commit live as normal; strict mode commits
locally only, leaving push timing to the user.

**Result:** PASS. "**GitHub mode:** push the commit live immediately after committing (`git
push`). **Strict mode:** commit locally only — do **not** push. Leave it for the user to decide
whether and when to push." Confirmed this differentiation lives inline in the **shared** file (not
the thin variants) — verified empirically in TS-11 that the two thin variants are comment-only and
contribute nothing to the deployed file, so mode branching had to be inline to actually reach a
target project. Both modes' deployed `Refine_Prototype_Workflow.md` carry this text identically.

---

### TS-08 — AC8: end-of-loop story drafting reuses `Create_Stories_Workflow.md`, lands in paired production repo's tracker

**File:** `Refine_Prototype_Workflow_Shared_template.md` Step 4 (lines 123–129)

**Expected:** Orchestrator reads back the iteration log and drafts stories for changes worth
keeping, reusing `Create_Stories_Workflow.md`'s draft-and-confirm step; user decides which drafts
become real tracked issues; issues are created in the paired production repo's tracker, never the
prototype repo; nothing is auto-created.

**Result:** PASS. Step 4 sub-steps: read log → present + ask which are worth keeping → "draft
stories reusing `Create_Stories_Workflow.md`'s Step 2 (Draft Stories) and Step 4 (Create Stories)
exactly — do not duplicate that logic here. Because this workflow runs from the **paired production
repo's own session** ... reusing `Create_Stories_Workflow.md` unmodified already creates the
resulting issues/story files in the **paired production repo's tracker**, never the prototype
repo. Nothing is auto-created." Matches PO's Q3 decision from the pre-flight review thread exactly.

---

### TS-09 — AC9: trigger documented in injected `CLAUDE.md` trigger table

**File:** `CLAUDE_Shared_template.md` diff

**Expected:** New row for `refine prototype` in the Workflows trigger table.

**Result:** PASS. `| \`refine prototype\` | \`.claude/agents/workflows/Refine_Prototype_Workflow.md\` |`
added directly below the `create stories` row, consistent with the existing table's format and
column order.

---

### TS-10 — AC10 / CR-3 re-verification: `Loop Status: ended` resume branch, correct precedence

**File:** `Refine_Prototype_Workflow_Shared_template.md` resume rule (lines ~47–51) and Pipeline
Rules bullet

**Expected:** The resume rule branches three ways — empty `Prototype Repo Path:` → Step 1,
`Loop Status: active` → Step 3, `Loop Status: ended` → Step 4 — with the empty-path check
evaluated before the `Loop Status` check (iteration 0 has both empty path and `active` status
simultaneously, so order matters).

**Independent re-verification (not trusting TL's round-2 summary):**
- `grep -n` confirms all three branches present verbatim: "Empty `Prototype Repo Path:` → resume at
  Step 1", "`Loop Status: active` → resume at Step 3 (mid-loop)", "`Loop Status: ended` → resume at
  Step 4 (the loop itself already ended ... skipping straight back into the iteration loop here
  would silently drop it)".
- Branch list order in the file is empty-path first, then `active`, then `ended` — matches the
  required precedence.
- Pipeline Rules bullet restates the identical three-way branch, consistent with the resume rule
  (not left describing the old two-way version).
- Dry-run of `scaffold_mechanical.sh` (TS-11) confirms the `Loop Status: ended` branch text is
  actually present in the deployed target-project file, in both modes — not merely in the source
  template.

**Result:** PASS.

---

### TS-11 — Shell script validation + scaffold regression check (`Type: behavioral` gate)

**File:** `.claude/agents/working/scripts/scaffold_mechanical.sh` (`SPLIT_WORKFLOWS` array change)

**Commands:**
- `bash -n .claude/agents/working/scripts/scaffold_mechanical.sh`
- Dry-run scaffold from the PR branch into scratch targets, both modes
- Dry-run scaffold from `origin/main` (via `git worktree add`) into a scratch target, github mode,
  and `diff -rq` the two `.claude/agents` trees (CRLF-normalized per known worktree artifact)

**Expected:** Zero syntax errors; `Refine_Prototype_Workflow.md` appears among 10 deployed workflow
files in both modes; github/strict deployed output byte-identical (thin variants are comment-only,
confirming AC7's mode text had to live in the shared file); no unintended change to any other
deployed file versus `origin/main` beyond the expected count-ripple text and the version bump.

**Result:** PASS.
- `bash -n` — 0 errors.
- Both modes scaffolded 10 workflow files including `Refine_Prototype_Workflow.md`; `diff` between
  the github- and strict-mode deployed `Refine_Prototype_Workflow.md` — 0 differences (confirms
  TL's finding that the thin variants contribute nothing and mode text must be inline in the shared
  file, independently reproduced).
- `diff -rq` against an `origin/main` scaffold (github mode) surfaced 5 differing files:
  `devkit_version.txt` (expected — version bump 0.1.36→0.1.37), `Sync_Devkit_Workflow.md`
  (real diff, CRLF-normalized: exactly the 3 expected count-ripple lines — split-candidates list,
  "Applies to all 10 files", expected-files list), `Refine_Prototype_Workflow.md` (new file, as
  expected), and `check_devkit_version.ps1`/`check_devkit_version.sh`/`Workflow_Guide.md` — all
  three showed as whole-file diffs but were confirmed byte-identical after CRLF normalization
  (`git worktree` checkout materializes CRLF against the primary LF working tree — known artifact,
  documented in Technical_Lead_Memory for this same story). No other file in the deployed tree
  changed. No regression found.

---

### TS-12 — Layer-1 automation gate (regression suite for template/workflow changes)

**Commands (run directly on branch `ST-000028/refine-prototype-workflow`, already checked out):**
- `python scripts/validate_templates.py`
- `bash scripts/test/run.sh`

**Expected:** Both exit 0, per QA_Rules §8.

**Result:** PASS.
- `validate_templates.py` → `OK -- all hard invariants passed (3 known-issue note(s))`, exit 0. The
  3 `[KNOWN_ISSUE]` notes are the pre-existing `Blocked_Request_Template.md` capital-T typo
  (QA_Memory stored fact), unrelated to this change, all in `Resume_Story_Workflow_Shared_template.md`
  and `Shared_Pipeline_Stages_Shared_template.md`.
- `scripts/test/run.sh` → `Results: 5 passed, 0 failed`, exit 0.
- CI (`gh pr checks 87`): `Layer-1 invariant check` — pass, run
  https://github.com/mycom08/mt-agent-devkit/actions/runs/30340529542/job/90214882781.

---

### TS-13 — `changes.json` / `version.txt` / `CHANGELOG.md` consistency

**Expected:** `version.txt` bumped; `changes.json` new entry lists exactly the 5 `templates/`
files touched (3 new, 2 modified), correctly excluding devkit-internal files
(`Init_Project_Workflow.md`, `Update_Project_Workflow.md`, `Build_Software_Workflow.md`,
`scaffold_mechanical.sh`, the working `Sync_Devkit_Workflow.md` mirror); `CHANGELOG.md`
`[Unreleased]` reflects the change.

**Result:** PASS. `version.txt`: `0.1.36` → `0.1.37`. `changes.json` `"0.1.37"` entry: `new` lists
the 3 new template files (shared + github + strict), `modified` lists `CLAUDE_Shared_template.md`
and `Sync_Devkit_Workflow_template.md`, each with a description; object format matches v0.0.8+
convention; entry appended after `0.1.36` per Project_Priming §15's ascending-order rule.
`CHANGELOG.md [Unreleased]` has a new `### Added (v0.1.37 — ...)` block with 3 bullets.

---

### TS-14 — Non-blocking finding: stale `Step 3g` cross-reference (TL-flagged, verified, not held against sign-off)

**File:** `Refine_Prototype_Workflow_Shared_template.md` line 39 (Write rules) and Step 3 heading

**Observation:** Write rules say `Set \`Loop Status: ended\` when the user chooses to stop (Step
3g).` Step 3's sub-steps are numbered plainly `1`–`6` (ask, apply, review, commit, update state,
stop-and-ask) — there is no lettered `3g` anywhere in the file; the actual stop action is sub-step
6. Confirmed via `grep -n "Step 3g\|sub-step"` — only the two hits shown above, no `g`-suffixed
numbering exists in this template's convention (the existing `sub-step 1` cross-reference at Step
3 sub-step 6 uses bare numbers, consistent with the rest of the file).

This is the same instance TL flagged in the round-2 PR review as surviving both rounds and
non-blocking — unambiguous in context since only one stop point exists in Step 3. Not held against
sign-off; noted here and in the QA retro section for a follow-up touch of this file.

---

## Summary

All 9 AC independently re-derived from live file content on the PR branch — PASS. CR-1/CR-2 fix
(no remaining devkit-only executable references in any of the 3 new templates) and CR-3 fix
(`Loop Status: ended` branch, correct precedence) independently re-verified rather than trusted
from TL's round-2 summary. Shell script (`scaffold_mechanical.sh`) syntax-checked clean; scaffold
dry-run regression check against `origin/main` found no unintended changes. Layer-1 automation gate
PASS (both scripts, exit 0) and CI green on the PR head SHA. `changes.json`/`version.txt`/
`CHANGELOG.md` consistent. One non-blocking stale cross-reference (`Step 3g`) confirmed real but
not holding up sign-off, per TL's own non-blocking classification.

QA sign-off granted 2026-07-28.
