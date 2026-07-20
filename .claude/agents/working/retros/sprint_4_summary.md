# Sprint 4 — Retro Summary
**Sprint:** sprint-4
**Last Updated:** 2026-07-20

---

## ST-000021 — Add UI/UX Designer Agent Role Templates
**Date:** 2026-07-20
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[context]` New role touches every existing 5-role enumeration corpus-wide (Story_Standard*, Product_Owner_Rules, shared workflow files, Init_Project file-count tables, scaffold_mechanical.sh loops), but nothing flags this as a ripple effect — found by grep-and-hope. *(Developer)*
- `[context]` No documented rule states a new role skips the working-record mirror (gitignored for the devkit's own team) — inferred from `.gitignore` + `git ls-files`. *(Developer)*
- `[workflow]` A named "add a 6th/Nth role" checklist in `Project_Priming.md` §15 would remove the grep-and-hope step for future role additions. *(Developer)*

### What Worked Well
- `validate_templates.py`'s reference-integrity and changes.json coverage checks caught the mechanical parts (new files listed, no dangling refs) immediately.
- The dual-update + drift-check convention in Project_Priming §15 correctly predicted that `Story_Standard.md`'s working mirror needed the same edits as the template.

### Actions Applied
- `.claude/agents/working/context/Project_Priming.md` — added §15a: "Adding a New Agent Role (Nth Role)" checklist covering every enumeration point + the working-record mirror carve-out.

---

## ST-000022 — Integrate UI/UX Designer Into Analyst & Build Software Workflows
**Date:** 2026-07-20
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[workflow]` AC phrased detection as "any repo's tech stack includes a UI layer," but the pipeline stage runs before repo-splitting exists — the condition had to be reworded to "the spec names a UI-bearing surface" during design. *(Developer)*
- `[failure]` Found three separate pre-existing stale-count references left behind by the immediately-preceding sibling story (ST-000021) that added a 6th role. *(Developer)*
- `[workflow]` When a story adds a new template file, check the `changes.json`-only scope decided at design time against what's actually touched during implementation — a mid-implementation stale-reference fix can legitimately pull in one more file. *(Developer)*
- `[workflow]` Reserve dedicated lettered sub-steps in a Path-based Stage 4 for one purpose only; adding a second similarly-shaped generation step meant re-lettering every cross-reference. *(Developer)*
- `[workflow]` A design review approving a new "verbatim tier" rules file should explicitly check the `Sync_Devkit_Workflow_template.md` enumeration as a required consequence — this design review's own item had a gap here. *(Technical Lead)*
- `[workflow]` When an implementer's `changes.json` file count diverges from what an approved design comment enumerated, verify the reviewer's original enumeration was actually complete before treating the divergence as scope creep. *(Technical Lead)*

### What Worked Well
- The design-first gate caught a real cross-story sequencing question (this story vs. ST-000024, both restructuring the same file) before any file was written.
- Existing precedent sections (Java REST service ⇒ api-spec convention, Java Skeleton Generation) served as a directly reusable template shape for the analogous UI-prototype convention.
- Reproducing the CI validator locally against the exact PR head gave independent confirmation matching the CI job log byte-for-byte.
- Corpus-wide greps for stale count references after the implementer's fix confirmed zero remaining stale hits.

### Actions Applied
- *(none — items 5/6 (detection phrasing, land-order note) captured under ST-000024's near-identical findings and applied there to `Story_Standard_PO.md`; item on Sync_Devkit_Workflow enumeration check and stale-count-drift were reviewed but not applied as standalone rule edits this round, per user selection)*

---

## ST-000023 — Define Logging Standard template and inject it into target projects
**Date:** 2026-07-20
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[workflow]` Adding a 10th adaptive-tier rules file meant hunting down every hardcoded rules-file count across internal workflow files — none AC-listed, all stale-if-unfixed side effects. *(Developer)*
- `[context]` PO's pre-refinement scope-addition comment already named the exact `Sync_Devkit_Workflow_template.md` list locations to update, matching the Developer Memory note from ST-000021/ST-000022 about this file's two separate enumerations. *(Developer)*
- `[workflow]` A single "N rules files" constant referenced by name (vs. count repeated as prose in 5+ places) would remove this whole class of drift risk. *(Developer)*
- `[context]` Local git checkout ended up on the story's dev branch mid-pipeline (agent work happens in the same working tree, not an isolated worktree) — required a stash/checkout-main/pull/stash-pop sequence to preserve uncommitted retro edits. *(Orchestrator)*

### What Worked Well
- The Technical Scope's explicit working-mirror carve-out meant no ambiguity; extended the same reasoning to intentionally not add the pointer to the devkit's own working mirrors either.
- PO's pre-emptive scope-addition comment meant zero mid-implementation consultation was needed.

### Actions Applied
- *(none this round, per user selection)*

---

## ST-000024 — QA authors testing_plan.md in the Analyst workflow (independent test planning)
**Date:** 2026-07-20
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[workflow]` A cross-story sequencing question (this story's Stage 2a rewrite overlaps ST-000022's parallel-spawn addition to the same section) needed a design-first TL check before the mandatory design-first gate for this story even started. *(Developer)*
- `[workflow]` When two stories restructure the same workflow section in the same sprint, the story that lands second benefits from an explicit "land order + composition" note in its own Technical Scope, not just a Developer-initiated cross-reference comment. *(Developer)*

### What Worked Well
- Grepping both changed files for every existing `testing_plan.md`/TL co-reference before writing anything caught every location needing updating in one pass.
- The design-first gate worked as intended: TL caught a real correctness issue (QA resuming from stale `architecture.md`) before any implementation.

### Actions Applied
- `.claude/agents/working/rules/Story_Standard_PO.md` — added guidance under §13 (Story Creation Template): state detection conditions in terms of what's on disk at that pipeline stage, not a downstream concept; name land-order explicitly in Technical Scope when two same-sprint stories touch the same workflow section. Devkit-internal only (intentionally-diverged mirror — no target-project equivalent, since target-project stories don't typically restructure the devkit's own meta-workflow files).

---

## ST-000025 — Stack-agnostic CI bootstrap + per-repo CI classification in build software
**Date:** 2026-07-20
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- The Developer's first design draft placed CI Bootstrap as a wave-closing step *after* the whole wave's `Scaffolded Repos` append, violating the Pipeline State write-rules invariant ("append the moment `build_state.md` is written... before anything else"). Caught by the design-first gate before any file was touched. *(Developer / Technical Lead — untagged in the source retro, a retro-tagging gap noted separately)*
- Any design that inserts/renumbers lettered or numbered sub-steps should explicitly grep the same file for self-referencing step numbers before finalizing — round 1 missed two stale cross-references, round 2 implementation found a third. *(Technical Lead)*
- Developer/TL retro entries for this story mostly omitted the `[tag]` convention despite containing solid signal — a `Retro_Rules.md` gap flagged but not selected for a rule edit this round.

### What Worked Well
- The design-first gate worked as intended: a genuine resume-invariant bug was caught and fixed as a two-round comment exchange before any workflow file was touched.
- TL's two-option framing (fix (a) vs (b), with explicit tradeoffs) made the revision fast — no back-and-forth needed.
- TL's code review verified claims rather than trusting them at every step (opened CI job logs, byte-for-byte diffed reused conventions, full-file grep for stale refs, confirmed exact file-touch count for the "no changes.json" AC).

### Actions Applied
- *(none this round, per user selection — retro-tagging gap and CI-bootstrap process notes reviewed but not applied as standalone rule edits)*

---

## Sprint Consolidated Summary

**Scope:** 5 stories, all `Type: non-behavioral`, all Developer-implemented, all merged same day. Two stories (ST-000024, ST-000025) went through the mandatory design-first gate; ST-000025 needed two review rounds. Three stories (ST-000021, ST-000023, and Stage 3/4 of most others) ran the non-behavioral fast path with the orchestrator verifying AC directly instead of spawning TL/QA/PO agents.

**Common theme — corpus-wide ripple from small-looking changes.** Every story that added a new file to an existing enumerated set (a 6th agent role in ST-000021, a 9th verbatim/10th adaptive rules file in ST-000022/ST-000023, a new Stage 4 step in ST-000025) triggered stale-reference cleanup beyond what its own AC listed — file-count prose, "expected files" cleanup lists, and numbered/lettered step cross-references were consistently the class of thing missed by AC alone and caught only by grep-driven diligence or design/code review. This pattern repeated in 4 of 5 stories.

**Recurring blocker — none rose to a full blocker**, but two operational frictions repeated across stories: (1) GitHub Actions produced zero check-runs on a PR's `opened` event after a long gap since the previous PR (ST-000021, ST-000022), worked around with a diagnostic empty commit each time; (2) the orchestrator's local git checkout ended up on the story's dev branch mid-pipeline three times (agent work isn't isolated to a worktree), requiring a stash/checkout-main/pull/stash-pop sequence each time to avoid losing uncommitted retro edits.

**What went well:**
- The design-first gate did real work this sprint — it caught a genuine correctness bug in ST-000024 (QA resuming from stale `architecture.md`) and a genuine resume-invariant violation in ST-000025 (a wave-batched step that would have permanently skipped CI Bootstrap on a crash-resume), both before any implementation file was touched.
- Reviewers (TL) consistently verified claims rather than trusting summaries — reproducing CI locally, byte-for-byte diffing "reused verbatim" claims, full-file greps confirming no stale references were missed, and independently checking file-touch counts against "no changes.json" claims. This showed up in every TL review this sprint.
- Precedent reuse (Java REST service ⇒ api-spec convention as the template for the UI-prototype convention and later the CI Bootstrap step) kept new sections consistent with house style with minimal invention.

**Top process improvement suggestions:**
1. **Add a standing "new enumerated file" checklist** (partially addressed this sprint via `Project_Priming.md §15a` for agent roles) — generalize it to cover any addition to a corpus-tracked set (rules file, workflow step, role) so file-count prose and enumeration lists stop being found ad hoc, sprint after sprint.
2. **Adopt a numbered-with-gaps or named-step scheme** for Path-based Stage 4 (instead of lettered sub-steps) so future step insertions don't require re-lettering every cross-reference — flagged twice this sprint (ST-000022, implicitly ST-000025) as a source of avoidable review overhead.
3. **Investigate the CI event-delivery quirk** (zero check-runs on `opened` after a long PR gap) properly instead of continuing to route around it with diagnostic empty commits — it's cost real review time twice this sprint alone.
