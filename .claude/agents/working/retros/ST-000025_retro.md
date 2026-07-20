# Retrospective — ST-000025
**Date:** 2026-07-20
**Story:** Stack-agnostic CI bootstrap + per-repo CI classification in build software

## Implementer — Developer
### Impediments & Unclear Points
- My first design draft placed CI Bootstrap as a wave-closing step *after* the whole wave's `Scaffolded Repos` append, missing that this violated the Pipeline State write-rules invariant ("append the moment `build_state.md` is written... before anything else"). I'd checked the resume-rules prose but not the specific write-rules sentence — the gate caught it before any file was touched, exactly as designed, but it's a reminder to re-read the literal invariant text, not just the general resume-rules summary, whenever a new step is inserted near a state-append.
- Choosing between TL's two fix options (per-repo sequential vs. keep-wave-batching) required weighing a design tradeoff against an already-locked AC clause (AC-3's "parallel-batched per wave" from refinement) rather than picking the simpler option — worth flagging explicitly for sign-off rather than deciding unilaterally, which is what I did.

### Process Suggestions
- Reusing existing shared-conventions-file precedent (`Version_Release_Conventions.md`'s structure, `Java_Skeleton_REST_Service.md`'s verbatim trigger block + required-checks caveat) for a brand-new file (`CI_Bootstrap_Conventions.md`) kept the new file consistent with established shape on the first pass — worth continuing as the default move whenever a story adds a new shared-conventions doc.
- When a step-insertion story renumbers existing steps, grep the whole file for `step N` / `step letter` self-references before finalizing the design, not just the two the reviewer happens to catch — I found and fixed a third stale reference (line 682, the Pipeline Rules "resume source of truth" bullet) during implementation that TL hadn't explicitly named but which made the same now-inaccurate absolute claim as the one TL did catch.

### What Worked Well
- The design-first gate worked as intended: a genuine resume-invariant bug was caught and fixed as a two-round comment exchange before any workflow file was touched, at near-zero cost compared to finding it in code review or, worse, in a real `build software` run.
- TL's two-option framing (fix (a) vs (b), with explicit tradeoffs stated for each) made the revision fast — no back-and-forth needed to understand what "acceptable" meant, just a clear choice with a stated rationale.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- Design-first gate did its job here: the Developer's Path B placement of CI Bootstrap (new wave-closing step *after* the whole wave's `Scaffolded Repos` append) would have shipped a silent resume bug — any crash in the window between the last repo's append and CI Bootstrap completing would permanently skip CI Bootstrap for every repo in that wave on resume, since the Stage 4 resume rule treats an appended repo as fully done with "no filesystem check needed." Catching this at design time (not in a code-review diff) is exactly what the gate is for — would have been much more expensive to find/unwind post-implementation.
- The design's own renumbering of Path A's steps (7→8…11→12) would have left two stale numeric cross-references elsewhere in the same file (line 52 "Path A step 9", line 687 "Path A step 8") — a mechanical consequence of the step-insertion that wasn't mentioned anywhere in the draft. Worth normalizing as a standing check: any design that inserts/renumbers lettered or numbered sub-steps should explicitly grep the same file for self-referencing step numbers before finalizing.

### Process Suggestions
- Confirmed useful: cross-checking a new pipeline step's placement against the *specific* invariant sentence in "Pipeline State" write-rules (not just against the general resume-rules prose) is what surfaced the gap — the write-rules line literally says "before anything else." Reviewing new Stage-4-step designs should always re-read that one line as a checklist item, not just skim the Resume rules bullets.
- Grep-verifying `.github/workflows/ci.yml` filename match between the new CI Bootstrap guard and what Java Skeleton Generation actually writes (both REST-service and library shapes) was cheap and caught a real compatibility question before it became a bug — worth keeping as a standard step whenever a new guard condition is defined against a file another step already writes.

### What Worked Well
- The Developer's draft was thorough and well-organized against the AC and the two TL-resolved open points from the earlier Q&A round — 4 of 5 flagged sign-off points needed no rework, and the taxonomy/conventions-file/agent-prompt-shape portions were solid on first read. The one real defect found was narrow and specific (a step-ordering/resume-invariant violation), not a fundamental rethink — a good outcome for a first design-review pass on a story with real pipeline-state complexity.

### Round 2 (revision review, same day)
- Developer chose fix (b) (keep wave-batching, move the append) over (a), reasoning that AC-3's "parallel-batched per wave" wording was a deliberate refinement outcome and (a) would have silently walked it back — a good instinct to flag the trade-off explicitly for sign-off rather than picking silently.
- Verified, not trusted: re-pulled the live file and independently confirmed all 4 cited line numbers (52, 60, 682, 687) matched verbatim, re-grepped the whole repo for `Path A step|Path B step` to make sure no third stale reference existed (found none beyond what was already fixed — two other hits at lines 499/557 were untouched by the lettering change and remained correct as-is). Confirmed the resume-rule extension reused the exact existing filesystem-fallback condition text (`git init` + `build_state.md` present) rather than inventing a new mechanism — matches the claim made in the revision.
- Developer proactively fixed line 682 (a bullet I hadn't explicitly named in round 1, but which made the same now-stale absolute claim as line 52) — good sign of understanding the underlying invariant rather than just patching the two lines literally called out.
- Verdict: **Design approved**, second round. Comment: https://github.com/mycom08/mt-agent-devkit/issues/66#issuecomment-5024097255. Total time from first design-first draft to approval: one changes-requested round + one revision round, same day — the gate did its job without becoming a bottleneck.

## QA
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Product Owner
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Orchestrator
### Observations
*(pending)*
