# Sprint 3 — Retro Summary
**Sprint:** sprint-3
**Last Updated:** 2026-06-30

---

## ST-000016 — Establish template test strategy + Layer-1 validation tool & CI gate
**Date:** 2026-06-30
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[workflow]` When specifying fixture-coverage AC, distinguish per-file checks from global/aggregate checks — a global check can't be isolated to one per-file negative fixture *(TL)*
- `[workflow]` "One negative fixture per check" ACs should exempt global/aggregate checks or require a parameter-override hook so they stay testable *(TL)*
- `[context]` Literal AC wording ("versions ascending") contradicted the actual descending data-file convention; the authoritative interpretation lived only in the design-first comment and the body AC was never reconciled *(TL)*
- `[instruction]` A design-first approval comment that narrows/supersedes body AC wording should trigger a same-pass body-AC edit, so later-stage reviewers don't reconcile two sources *(TL)*
- `[workflow]` QA Rules §4 "create test scenario first" is in tension with execution-driven tooling stories — the scenario can be drafted in parallel with the first run rather than as a strict prerequisite gate *(QA)*
- `[context]` For additive-only PRs (no templates/workflows modified), a `git diff --name-only` blast-radius check can replace the behavioral walkthrough; for tooling stories the regression suite IS the new tool runs *(QA)*

### What Worked Well
- Separating the 4 root-cause bug categories before rewriting the validator kept the rewrite targeted and verifiable *(Developer)*
- The `--test-retired-trigger` flag cleanly tests empty-seed invariants without contaminating production constants *(Developer)*
- Running the validator + fixture self-test locally before approving confirmed the PR's captured outputs were reproducible *(TL)*
- The design-first approval comment fully specified the invariant set, so review was a straight conformance check rather than a fresh design debate *(TL/PO)*
- Execution-based QA validation plus the `git diff main..HEAD --name-only` blast-radius view gave a one-step zero-regression confirmation *(QA)*
- AC was precise and testable — each of the 5 criteria mapped unambiguously to a deliverable *(PO)*

### Actions Applied
- `.claude/agents/templates/rules/Story_Standard_template.md` (+ working copy) — §3 per-file vs global fixture-coverage AC guidance; §9 same-pass body-AC reconciliation when a design-first approval narrows an AC
- `.claude/agents/templates/rules/CICD_Validation_Guide_template.md` (+ working copy) — notes: PR-triggered gates need a `push:[ci-validation]` trigger; gitignored reference paths won't exist on the runner
- `version.txt` — bumped 0.1.15 → 0.1.16
- `changes.json` — added 0.1.16 entry (both template files above)
- *(Not applied — user declined: QA Rules §4/§8 timing + blast-radius shortcut)*

---

## ST-000012 — Resolve story-workflow status, gate & assignee contradictions (RF-001/002/004/013)
**Date:** 2026-06-30
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[context]` The four RF items each touched a cross-role file plus its working mirror; confirming no new contradictions required reading all six files before editing — a read-set not called out in the story scope *(TL)*
- `[instruction]` The working copy of `Technical_Lead_Rules.md` had silently drifted from its template (§3 "after merge" vs "before merge"); no drift detection exists between templates and working mirrors *(TL)*
- `[workflow]` For stories that list template/mirror pairs, add a drift-check: read each mirror against its template before editing and flag pre-existing out-of-scope divergence *(TL)*
- `[instruction]` AC phrased "verify X is the canonical statement (adjust if needed)" should name the working-mirror counterpart to check, not just the template *(TL)*
- `[context]` Review instruction was broader than the formal AC scope; a residual contradiction was found in out-of-scope files, forcing a block-vs-flag judgment call *(Dev)*
- `[instruction]` Technical Scope omitted the role-view files (`Story_Standard_Dev`) yet the review implied a full-repo scan — scope and review expectations were misaligned *(Dev)*
- `[workflow]` A consistency story fixing the main cross-role file should state in its AC whether the role-view files (Dev/PO/QA views) are in scope *(Dev)*
- `[instruction]` Review guidance should state: pre-existing contradiction in an out-of-scope file = flag as follow-up, don't block; contradiction introduced by the PR = block *(Dev)*

### What Worked Well
- Design-first gate (recording the `status:testing` ownership decision before any edit) prevented mid-implementation second-guessing and left a clear rationale trail on the issue *(TL)*
- The Layer-1 validator confirmed the SHARED-block and reference integrity were unaffected by the surgical edits — no new invariant violations *(TL)*
- Grepping all `.md` files for `status:testing` gave a comprehensive "nothing elsewhere" verification in a single call *(Dev)*
- The validator pass acted as a fast-fail safety net for structural regressions even though the changes were purely textual *(Dev)*

### Actions Applied
- `.claude/agents/templates/rules/Story_Standard_template.md` (+ working copy) — §12 reviewer flag-vs-block rule [P2, ships]
- `.claude/agents/working/context/Project_Priming.md` §15 — dual-update + pre-edit drift-check note [P4, devkit-internal]
- `version.txt` 0.1.17 → 0.1.18; `changes.json` 0.1.18 entry; `CHANGELOG.md` updated
- Created follow-up story **ST-000017** (Issue #36) — extend the RF-001 fix to the Dev/QA/TL role-view files
- *(Not applied — user declined: P3 consistency-story AC-scoping note)*
