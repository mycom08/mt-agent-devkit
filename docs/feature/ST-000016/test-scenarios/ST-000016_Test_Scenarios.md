# Test Scenarios — ST-000016

**Story:** Establish template test strategy + Layer-1 validation tool & CI gate
**Date:** 2026-06-30
**Branch:** ST-000016/template-test-strategy-and-validator
**PR:** #34

---

## Scope

This story adds three deliverables: a testing strategy guide, a Layer-1 corpus
invariant validator script, and a CI gate. All are devkit-internal tooling
(none deployed to target projects). Validation is by execution and content
inspection, not by template diff.

---

## Test Scenarios

### TS-01 — Full corpus validator: clean pass (happy path)

**Command:** `python scripts/validate_templates.py`

**Expected:** exits 0; output ends with `OK -- all hard invariants passed`.
Known-issue notes (`[KNOWN_ISSUE]`) are printed but do not affect exit code.
No `[ERROR]` lines.

**Result (2026-06-30):** PASS. Exit 0. Three `[KNOWN_ISSUE]` notes for the
known typo `.claude/agents/rules/Blocked_Request_Template.md` in two shared
workflow files; output confirms `OK -- all hard invariants passed (3 known-issue note(s))`.

---

### TS-02 — Fixture self-test: all negative fixtures fire (error-path)

**Command:** `bash scripts/test/run.sh`

**Expected:** 5 PASS lines, "Results: 5 passed, 0 failed", exits 0.
Each fixture must produce at least one `[ERROR]` line.

| Fixture | Invariant | Expected error |
|---|---|---|
| `inv1_bad_ref.md` | #1 reference integrity | Unresolved file reference |
| `inv2_bad_placeholder.md` | #2 placeholder well-formedness | Unknown/malformed token |
| `shared/inv3_bad_shared.md` | #3 shared-block balance | Unbalanced SHARED-START without SHARED-END |
| `inv4_bad_trigger.md` | #4 retired trigger (via `--test-retired-trigger` flag) | Retired trigger match |
| `inv6_bad_markdown.md` | #6 Markdown well-formedness | Heading level jump + unclosed code fence |

**Result (2026-06-30):** PASS. All 5 fixtures flagged. `run.sh` reports
`Results: 5 passed, 0 failed` and exits 0.

---

### TS-03 — CI workflow: trigger paths and command (content check)

**File:** `.github/workflows/validate-templates.yml`

**Expected:**
- `pull_request` trigger with `paths:` filter for `.claude/agents/templates/**`
  and `.claude/agents/workflows/**`.
- Job runs on `ubuntu-latest`.
- Step runs `python scripts/validate_templates.py` (no `actions/setup-python`
  needed — uses preinstalled Python).

**Result (2026-06-30):** PASS. Workflow file matches all three requirements.
Push trigger on `ci-validation` branch is also present (added for CI smoke-test
verification; does not affect PR gate behavior).

---

### TS-04 — Testing guide: section coverage (content check)

**File:** `docs/Template_Test_Strategy.md`

**Expected sections:**

| Section | Content |
|---|---|
| §1 | Purpose and scope |
| §2 | Templates as executable specifications |
| §3 | 3-layer model (static/unit, deployment/integration, behavioral/E2E) |
| §4 | 6 Layer-1 corpus invariants (#1–#6, each fully described) |
| §5 | Risk tiers A/B/C |
| §6 | Coverage model |
| §7 | AC-as-oracle + re-run-refactor-scan for Tier-A changes |
| §8 | Running the checks (local pre-PR command, fixture self-test, CI gate) |
| §9 | Relationship to `Project_Priming §8` and `refactor templates` workflow |
| §10–§11 | Layer-2/3 roadmap and maintenance guide |

**Result (2026-06-30):** PASS. All sections present and complete.

---

### TS-05 — Project_Priming §8: pre-PR gate reference added (content check)

**File:** `.claude/agents/working/context/Project_Priming.md`

**Expected:** §8 mentions `python scripts/validate_templates.py` alongside the
existing `bash -n` and PowerShell syntax gate references.

**Result (2026-06-30):** PASS. §8 Tech Stack paragraph confirms:
"For any PR touching `.claude/agents/templates/**` or `.claude/agents/workflows/**`:
`python scripts/validate_templates.py` (Layer-1 corpus invariant check — must exit 0)."

---

### TS-06 — No version bump / no changes.json entry (AC 5)

**Expected:** `version.txt` unchanged (0.1.15); `changes.json` not modified;
`CHANGELOG.md [Unreleased]` contains ST-000016 bullets.

**Result (2026-06-30):** PASS. `git diff main..HEAD -- version.txt` empty;
`git diff main..HEAD -- changes.json` empty. CHANGELOG.md [Unreleased] contains
five ST-000016 bullets covering all deliverables.

---

### TS-07 — Regression check: init project / sync devkit unaffected

**Expected:** No template files modified; no changes to `Init_Project_Workflow.md`
or `Update_Project_Workflow.md`; `init project` and `sync devkit` behavior unchanged.

**Result (2026-06-30):** PASS. `git diff main..HEAD --name-only` shows only:
`.claude/agents/working/context/Project_Priming.md`, `.github/workflows/validate-templates.yml`,
`CHANGELOG.md`, `docs/Template_Test_Strategy.md`, `scripts/` tree.
No templates or workflows modified. Regression risk: none.

---

## Summary

All 7 test scenarios PASS. No AC failures, no regression risk.
QA sign-off granted 2026-06-30.
