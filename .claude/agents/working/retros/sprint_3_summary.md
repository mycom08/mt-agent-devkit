# Sprint 3 — Retro Summary
**Sprint:** sprint-3
**Last Updated:** 2026-07-01

---

## ST-000015 — Fix devkit-internal workflow bugs: Build/Init/Update (RF-015/016/017)
**Date:** 2026-07-01
**Loop counts:** Impl→Reviewer: 2 | Impl→QA: 0

### Findings
- `[workflow]` RF-016 AC said "fix whichever makes the two consistent" — required reading both `Init_Project_Workflow.md` and `Update_Project_Workflow.md` in full to confirm which side was wrong; a cross-reference note naming the other file as owner/consumer of the shared path would have made it obvious *(Developer)*
- `[context]` RF-017 source-table annotation said "×7" but the glob only matched 6 — the mismatch between annotation and glob wasn't caught at authoring time *(Developer)*
- `[workflow]` When two workflow files reference the same path (writer + consumer), add a comment in each naming the other — makes future mismatches visible without a cross-file read *(Developer)*
- `[workflow]` Pipeline-state write-rules block said "update Stage to the last completed stage" but the body stages wrote at entry, violating its own stated rule — add an explicit "write at completion, never at entry" guardrail line *(Developer)*
- `[workflow]` RF-016 was scoped "devkit-internal, no version bump," but a complete fix necessarily edits versioned templates — a file-location move is almost never containable to the writer alone, it ripples to every reference *(Technical Lead)*
- `[workflow]` For any story that changes a file's target location, add a mandatory step: grep the full template+workflow corpus for old-path referrers before opening the PR — RF-016 had 8 referrers, only the writer was updated *(Technical Lead)*
- `[workflow]` When Update-side migration logic self-heals via a directory-existence check, moving Init to pre-create that directory silently disables the self-heal with no warning anywhere *(Technical Lead)*

### What Worked Well
- AC explicitly stated which side to fix for RF-016 if ambiguous, reducing decision uncertainty *(Developer)*
- `validate_templates.py` exit 0 confirmed no regressions from all three edits in one pass *(Developer)*
- Build_Software Stage 4 resume rules (per-repo idempotency checks) worked cleanly with the completion-point fix, no additional resume-rule changes needed *(Developer)*
- RF-015 and RF-017 were cleanly separable and independently correct, keeping the review block precise rather than rejecting the whole PR *(Technical Lead)*
- Story_Standard §12 "introduced vs pre-existing" gave a clean rule for separating the blocking regression from the pre-existing non-split-annotation quirk *(Technical Lead)*
- Diffing the affected file against `main` in full (not just the PR's commit range) was the fastest way to confirm a re-scoped revert left zero residue *(Technical Lead, round 2)*
- Re-deriving RF-015's correctness from the unmodified surrounding pipeline rules (rather than re-citing the round-1 verdict) caught that Stage 5's missing completion-write is intentional design, not a gap *(Technical Lead, round 2)*
- Descoping one AC (RF-016) out of a multi-fix story while keeping the other two moving avoided blocking delivery on an AC that structurally contradicted its own "no version bump" constraint *(Product Owner)*

### Actions Applied
- Created follow-up story **ST-000020** (Issue #42) — complete RF-016 properly: re-apply the Init instruction-path move plus align all 8 flat-path referrers in versioned templates, with a version bump
- *(Not applied — user did not respond to the retro-improvement proposal (items A–E: path cross-reference notes, glob/annotation sync check, write-at-completion guardrail, grep-referrers step, self-heal guardrail note); candidates preserved in this summary for future consideration)*

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

---

## ST-000013 — Add strict-mode gating to shared rules & priming (RF-003/005/006)
**Date:** 2026-07-01
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[context]` The dual-update rule was ambiguous when a working mirror was *intentionally* diverged from its template (devkit GitHub-mode-only vs target-project-generic); required a judgment call to skip the mirror update and document the divergence as intentional *(Developer)*
- `[context]` `Strict_Mode_Story_Guide.md` has no working mirror under `working/rules/` — the story mapped a mirror relationship that doesn't exist for a GitHub-mode devkit *(Developer)*
- `[instruction]` The dual-update rule should add a carve-out for intentionally-rewritten mirrors: document the divergence rather than flagging it as drift-to-fix *(Developer)*
- `[instruction]` The dual-update check should state that when a template has no working mirror, note the absence and proceed without creating one *(Developer)*

### What Worked Well
- The existing mode-gating precedent in `Developer_Rules §2` (`**GitHub mode:**` / `**Strict mode:**` inline labels) gave an unambiguous style to follow — no guessing *(Developer)*
- `validate_templates.py` passed on the first run, confirming the template edits broke no invariants *(Developer)*
- Non-behavioral fast path let the orchestrator verify all 5 ACs directly from the diff + reference files, closing the story without spawning TL/QA/PO agents *(Orchestrator)*

### Actions Applied
- `.claude/agents/working/context/Project_Priming.md` §15 — added dual-update carve-outs: intentionally-diverged mirror (document, don't force-match) and absent mirror (note absence, don't create) [devkit-internal, no version bump]
- *(Story-shipped changes already merged in PR #37: `Developer_Rules_template.md` §4/§6, `Project_Priming_template.md` §3, `Strict_Mode_Story_Guide_template.md` commit format; version 0.1.18 → 0.1.19)*

---

## ST-000014 — Fix stale references, retro routing & broken sprint query (RF-007/008/009/010/011/012/014)
**Date:** 2026-07-01
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[workflow]` RF-010 relabeled the BA retro header in instructions but the skeleton (`Shared_Pipeline_Stages`) + `Retro_Rules` heading map still emit `## Implementer — Business Analyst` — a partial fix until the retro subsystem is updated *(Developer/TL)*
- `[failure]` The 3-label AND `gh issue list` bug (RF-012 root cause) also lives in `product_owner_instructions` Plan-Next-Sprint step, which was out of AC scope — a partial fix leaves a live repeat of the bug *(TL/Developer)*
- `[workflow]` A rename/reference fix scoped to one file, when the renamed token is emitted/mapped by other files, forces a ship-vs-block judgment at review time; the tracing burden belongs on the implementer, not on the story creator enumerating files up front *(TL/Developer, refined by maintainer)*
- `[workflow]` Reference-integrity stories need a review step that greps to confirm each new target exists and each old target is absent — text-diff review alone can swap one broken reference for another *(TL)*
- `[instruction]` `Document_Index` should be the single source for §6 document paths to prevent drift (`Code_Review_Checklist` present in §6 but absent from `Document_Index`) *(TL)*

### What Worked Well
- Dual-update §15 carve-outs (added in ST-000013) were unambiguous — CLAUDE_Shared (no mirror) and devkit Project_Priming (intentionally diverged) were both correctly handled and documented *(Developer/TL)*
- The implementer proactively documented the RF-010 and RF-012 downstream issues in the PR body, so the follow-up decision was fully framed before review *(TL)*
- Full TL review (chosen over the fast path) verified reference targets actually exist (`Sync_Devkit_Workflow`, `Agent_Common §4`, `Document_Index` paths), catching what a text-only diff review would miss *(Orchestrator/TL)*

### Actions Applied
- `CLAUDE.md` (devkit-internal) — line 240 stale `update agents` → `sync devkit` [no version bump]
- Created follow-up story **ST-000018** (Issue #39) — fix the same AND-query bug in `product_owner_instructions` Plan-Next-Sprint step (FU-2 / `[failure]`)
- Created follow-up story **ST-000019** (Issue #40) — add implementer reference-trace rule (implementer-responsibility framing, per maintainer), reconcile reviewer reference-integrity checks between `Technical_Lead_Rules` template/mirror, and align `Document_Index` with Project_Priming §6 (FU-1 reviewer signals + FU-3)
- *(De-scoped by maintainer — RF-010 retro-skeleton/`Retro_Rules` Analyst-BA header alignment: low priority, not tracked)*
- *(Story-shipped changes already merged in PR #38: 6 templates + mirrors; version 0.1.19 → 0.1.20)*
