# Test Scenarios — ST-000026

**Story:** Roadmap stories must be drained into tracked backlog issues at authoring time
**Date:** 2026-07-28
**Branch:** ST-000026/roadmap-story-drain
**PR:** #85

---

## Scope

Docs/workflow-instructions-only change (no application source code). Touches
`Product_Owner_Rules_template.md` (+ working mirror), `Plan_Sprint_Workflow_Shared_template.md`
(+ working mirror), and the devkit-internal `Build_Software_Workflow.md`. Validation is by
reading the current file content against each AC and re-deriving an independent conclusion —
not by trusting the TL review summary — plus the Layer-1 automation gate and a corpus-wide
cross-reference check for regressions outside the diff.

TL round-1 review found 4 real correctness bugs in the idempotency/resume mechanics (CR-1..CR-4);
round-2 verified all 4 fixes, including stress-testing the exact-line-match fix in both
directions. This QA pass independently re-derives each AC from the merged file content on the
PR branch and separately attempts to construct an adversarial idempotency scenario per AC3.

---

## Test Scenarios

### TS-01 — AC1: drain trigger scoped to tracker-exists context, Analyst workflow excluded

**File:** `.claude/agents/templates/rules/Product_Owner_Rules_template.md` §11a (+ working mirror
`.claude/agents/working/rules/Product_Owner_Rules.md` §11a)

**Expected:** Trigger condition explicitly requires a story tracker to already exist
(`init project` has run), and explicitly excludes the Analyst workflow's pre-repo
`implementation_roadmap.md`.

**Result:** PASS. Template §11a: "in a context where a story tracker already exists (i.e. `init
project` has already run; this rule doesn't apply to the Analyst workflow's pre-repo
`implementation_roadmap.md`, which has no tracker yet and no real story IDs)." Working mirror
adapts this correctly for the devkit's own always-on tracker context (intentional divergence,
consistent with Project_Priming §15's carve-out) without weakening the exclusion. `Build_Software_Workflow.md`
independently defers the Build-software-specific drain to Stage 5 (post `gh repo create`/`gh
project create`) precisely because no tracker exists at Stage 3 doc-splitting time — consistent
with the same scoping principle applied to a second drain path.

---

### TS-02 — AC2: drained issues tagged with roadmap phase/sprint

**Files:** `Product_Owner_Rules_template.md` §11a step 3; `Build_Software_Workflow.md` Stage 5
step 4c

**Expected:** Every drain path attaches a human-facing phase tag to the created issue.

**Result:** PASS. Both paths reuse the pre-existing `**Roadmap Phase:** Phase N — <theme>` body
line and `phase-N` label convention already used in `Plan_Sprint_Workflow.md` Stage 4 and
`Create_Stories_Workflow.md` Step 3 — not a newly invented, potentially-inconsistent scheme. The
new `**Roadmap Source:**` marker is kept as a distinct field for idempotency only (AC3/AC6),
correctly separating the human-facing tag from the machine dedup key.

---

### TS-03 — AC3: idempotency — exact-line-match fix re-verification + adversarial construction

**Files:** `Product_Owner_Rules_template.md` §11a step 2; `Plan_Sprint_Workflow_Shared_template.md`
Stage 1 step 7; `Build_Software_Workflow.md` Stage 5 step 4b — all three call sites, plus the
strict-mode `grep -Fxq` branches at each.

**Expected:** Re-authoring/updating the same roadmap does not create duplicate issues. The CR-2
fix (search/list result treated as candidate set, exact full-line match required before treating
a story as already drained) must hold for a prefix-title adversarial case in both directions.

**Independent verification:**
- Confirmed all 3 github-mode call sites use "candidate set, not verdict" language plus an
  explicit exact-full-line confirmation step, and all 3 strict-mode call sites use `grep -Fxq`
  (whole-line match) rather than a plain substring grep — mode-parity holds across all six
  branches (not just the 3 TL named; the implementer's round-2 fix independently caught the
  strict-mode branches TL's CR-2 didn't enumerate).
- Constructed adversarial case: Story A titled "Add auth", Story B titled "Add authentication
  flow", same Phase N, same roadmap file. Marker A and Marker B differ only in the title
  component and are never equal as full strings — exact-line comparison is symmetric string
  equality, so neither can produce a false match against the other's issue body regardless of
  which title is checked first. This holds for both check orders (A-then-B and B-then-A).
- Constructed same-pass case: two new stories drained in one authoring pass. All three call sites
  explicitly instruct tracking just-created items locally within the pass rather than re-querying
  GitHub's eventually-consistent search index — mitigates the within-pass index-lag duplicate
  risk documented in TL's memory. Build Software's Stage 5 path sidesteps index lag entirely by
  using `gh issue list` (immediate-consistency issues API) instead of `--search`.
- Residual risks already identified and accepted by TL as non-blocking (not new findings): Stage
  5's `--limit 500` could false-negative into duplicates if a repo's tracker ever exceeds 500
  issues (documented as safe by construction for a freshly-scaffolded repo); `grep -Fxq` does not
  normalize CRLF line endings.
- No new correctness bug found beyond what TL's round-1/round-2 review already identified and
  fixed.

**Result:** PASS.

---

### TS-04 — AC4: reconciliation backstop present and correctly scoped (CR-1 fix re-verified)

**File:** `.claude/agents/templates/shared/workflows/Plan_Sprint_Workflow_Shared_template.md`
Stage 1 step 7 (+ working mirror `Plan_Sprint_Workflow.md` step 7)

**Expected:** Backstop lives in `Plan_Sprint_Workflow.md` Stage 1 (per PO's explicit decision on
the issue thread — not `Sprint_Workflow.md` sprint-end), and the pre-fix `status:backlog`-only
false-drift bug (CR-1) is genuinely gone.

**Result:** PASS. Step 7 query is `--state all` with no `--label`/`--state open` filter, and the
step text explicitly states the check "must confirm the marker exists anywhere in the tracker, in
any status — a story that was correctly drained and has since moved past `status:backlog`
(`ready`/`in-progress`/`done`) is still tracked, not drift." This is the literal fix for CR-1's
false-drift bug, confirmed by reading the live step text (not the review summary). Step
renumbering (old step 7 "If done → Stage 2" → new step 8) is sequential and consistent in both
template and mirror.

---

### TS-05 — AC5: Build_Software_Workflow.md reflects the drain across Stage 3 + Stage 5, unconditional-on-resume, Stage 4 invariant undisturbed

**File:** `.claude/agents/workflows/Build_Software_Workflow.md`

**Expected:** Stage 3 emits a per-repo manifest; Stage 5 performs the actual drain; the CR-3 fix
makes Stage 5 step 4 unconditional on resume; the Stage 4 `Scaffolded Repos` resume invariant is
untouched.

**Result:** PASS.
- Stage 3 purpose statement and a new step 4 add table-parseable manifest emission
  (`roadmap_stories_<repo-name>.md`), with an explicit non-`TBD` rule for `Assigned` (CR-4 fix).
- Stage 5 gains a new Doc Copy step 4 ("Roadmap story drain") with sub-steps a–d, placed after
  Doc Copy steps 1–3 and before commit/push (step 5), per TL's design decision.
- Stage 5's "resumed" bullet was independently diffed byte-for-byte between `main` and the PR
  branch for the file-presence gate scope: confirmed it now reads "This check only gates Doc Copy
  steps 1–3 ... **Step 4 (roadmap drain) is unconditional on resume — always re-run it for every
  repo, regardless of whether steps 1–3 were skipped or re-run.**" — an actual instruction change,
  not just an added warning (the exact class of non-fix flagged in TL's own memory re: ST-000025).
- Stage 4's "resumed" bullet (the `Scaffolded Repos` invariant) was independently diffed via `git
  diff main origin/ST-000026/roadmap-story-drain -- Build_Software_Workflow.md` and confirmed
  **byte-identical** (appears only as unchanged context, zero `+`/`-` lines touching it) — TL's
  claim of "no change to the Stage 4 invariant" is independently corroborated, not just trusted.
- Pipeline Rules section gained a dedicated bullet restating the mandatory/unconditional-on-resume
  property for cross-reference.

---

### TS-06 — AC6: idempotency re-run verification step is real and marker-based

**Files:** `Product_Owner_Rules_template.md` §11a step 4; `Build_Software_Workflow.md` Stage 5
step 4b

**Expected:** A documented re-run verification step exists and genuinely checks for zero
duplicates via the marker mechanism (not merely asserted).

**Result:** PASS. §11a step 4: "re-running steps 1–3 against an unchanged roadmap must return an
existing match at step 2 for every story and create zero new issues — this is the mechanism that
satisfies 're-authoring the same roadmap does not create duplicates.'" Build Software Stage 5 step
4b contains the equivalent statement tied explicitly to AC6: "This exact-line check is also the
mechanism AC6 verifies: re-running this step against an unchanged manifest must find an existing
exact-line match for every row and create zero new issues." Both are direct restatements of the
same exact-line-match mechanism validated in TS-03, not a separate/weaker claim.

---

### TS-07 — Layer-1 automation gate (regression suite for template/workflow changes)

**Commands (run against `origin/ST-000026/roadmap-story-drain` via a git worktree):**
- `python scripts/validate_templates.py`
- `bash scripts/test/run.sh`

**Expected:** Both exit 0, per QA_Rules §8.

**Result:** PASS.
- `validate_templates.py` → `OK -- all hard invariants passed (3 known-issue note(s))`, exit 0.
  The 3 `[KNOWN_ISSUE]` notes are the pre-existing, already-documented
  `Blocked_Request_Template.md` capital-T typo (QA_Memory stored fact), unrelated to this change.
  This run's reference-integrity invariant also independently confirms every `§N` citation in the
  changed files resolves to a real header — including the `Story_Standard_PO.md §13`/`§15`
  citation in `Build_Software_Workflow.md` Stage 5 step 4c, spot-checked manually and confirmed
  against `Story_Standard_PO.md`'s real headers (§13 Story Creation Template, §15 Shell Command
  Rules) — not a stray citation.
- `scripts/test/run.sh` → `Results: 5 passed, 0 failed`, exit 0.

---

### TS-08 — Regression check: cross-reference scan for damage outside the diff

**Expected:** No broken or now-ambiguous cross-references to the changed sections elsewhere in
the corpus; no residual stray `§15`-for-Assignee-rule citations (the CR-4 self-inflicted error
TL's memory flagged) left in operative rule text.

**Result:** PASS.
- `grep -rn "Product_Owner_Rules.*§11"` across the corpus: all hits are either the new §11a
  content itself or the pre-existing, still-valid `Sprint_Workflow_Shared_template.md:107`
  reference to §11 "Project Plan Commit" (unrenumbered — §11a was inserted as a new subsection
  after §11, not a renumbering of it, so this reference remains correct).
- `grep -rn "Product_Owner_Rules.*§15"` across the corpus: the only remaining hits are inside
  `Technical_Lead_Memory.md` and the ST-000026 retro — both are meta-commentary *describing* the
  citation mistake as a lesson learned, not live citations in operative rule text. The actual
  operative citation (`Product_Owner_Rules.md §1`'s Assignee rule) is correctly cited in both
  `Build_Software_Workflow.md` occurrences.
- No changes to `Init_Project_Workflow.md`, `Update_Project_Workflow.md`, or any strict-mode-only
  file; both github and strict mode branches are present at every new decision point (§11a,
  Plan_Sprint backstop, Build Software drain is github-mode only since Build Software itself is
  github-mode-only) — no mode-parity gap introduced.

---

### TS-09 — Version / changes.json / CHANGELOG consistency

**Expected:** `version.txt` bumped; `changes.json` has a new entry for the bumped version
covering exactly the two `templates/` files changed; `CHANGELOG.md [Unreleased]` reflects the
change; `Build_Software_Workflow.md` (devkit-internal, not under `templates/`) correctly excluded
from `changes.json`.

**Result:** PASS. `version.txt`: `0.1.34` → `0.1.35`. `changes.json` new `"0.1.35"` entry lists
exactly `Product_Owner_Rules_template.md` and `Plan_Sprint_Workflow_Shared_template.md` under
`modified`, each with a description, matching format for v0.0.8+ (object with
`new`/`modified`/`descriptions`). `CHANGELOG.md [Unreleased]` has a new `### Added (v0.1.35 —
...)` block with 3 bullets (2 template files + 1 internal-only Build Software note, correctly
marked "internal, no changes.json entry"). Entry appended after the previous `0.1.34` entry per
Project_Priming §15's ascending-order requirement.

---

## Summary

All 6 AC independently re-derived from live file content on the PR branch — PASS. Layer-1
automation gate PASS (both scripts, exit 0). Adversarial idempotency construction (AC3) found no
new bug beyond what TL's round-1/round-2 review already fixed. Corpus-wide cross-reference scan
(regression check) found no damage outside the diff. Version/changes.json/CHANGELOG consistent.

QA sign-off granted 2026-07-28.
