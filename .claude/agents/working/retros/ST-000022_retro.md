# Retrospective — ST-000022
**Date:** 2026-07-20
**Story:** Integrate UI/UX Designer Into Analyst & Build Software Workflows

## Implementer — Developer
### Impediments & Unclear Points
- `[workflow]` AC phrased detection as "any repo's tech stack includes a UI layer," but the pipeline stage in question runs before repo-splitting exists — the condition had to be reworded to "the spec names a UI-bearing surface" during design. Story-writing for a stage that crosses a later repo-split boundary should state detection in terms of what's actually on disk at that point, not a downstream concept.
- `[failure]` Found three separate pre-existing stale-count references (a rules-file list missing the prior story's new role, a mechanical/adaptive file-count denominator that was never bumped, an instruction-file count still saying "5") left behind by the immediately-preceding sibling story that added a 6th role. A new-role addition touches enumerations in more places than the obvious rules/instructions folders — file-count prose and "expected files" cleanup lists in sync-workflow files are easy to miss.

### Process Suggestions
- `[workflow]` When a story adds a new template file, explicitly check the `changes.json`-only scope decided at design time against what's actually touched during implementation — fixing a stale reference discovered mid-implementation can pull in one more `templates/` file than the design comment enumerated, and that's expected, not scope creep, as long as it's the same file the design already touches for another reason.
- `[workflow]` Reserve dedicated lettered sub-steps in a Path-based Stage 4 (or similar) for one purpose only per convention (e.g. "the Java-shaped one"); adding a second similarly-shaped generation step meant re-lettering and updating every cross-reference to the old letter — a numbered-with-gaps scheme, or naming steps instead of lettering them, would make future insertions non-disruptive.

### What Worked Well
- The design-first gate caught a real cross-story sequencing question (this story vs. its sibling restructuring the same file) before any file was written, and TL's approval resolved six concrete open points in one pass instead of a back-and-forth loop.
- Existing precedent sections (Java REST service ⇒ api-spec convention, Java Skeleton Generation) served as a directly reusable template shape for the analogous UI-prototype convention and scaffold-generation subsection — kept the new prose consistent with house style with minimal invention.

## Reviewer — Technical Lead
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

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
