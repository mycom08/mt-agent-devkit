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
