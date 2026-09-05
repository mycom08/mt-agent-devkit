# Retrospective — ST-000145
**Date:** 2026-09-05
**Story:** Agent-authored commits leave the PR head with no checks, making the mandatory merge gate unpassable

## Implementer — Technical Lead
### Impediments & Unclear Points
- `[instruction]` The AC asking for a rule about "agent commits landing after review sign-off" implies comparing the file set at approval-time against the file set at merge-time, but nothing in the pipeline previously recorded *which* commit was approved — I had to design and add that recording step myself rather than being able to reuse an existing field.
- None beyond that — the disproven-ordering fact was already on record and saved a full re-investigation.

### Process Suggestions
- `[workflow]` A gate that compares "state at approval" to "state at merge" needs an approval-time checkpoint to diff against. Keeping that checkpoint as a value embedded in the existing sign-off artifact (a comment/record field already written at that moment) avoided widening a single-file Technical Scope into a state-file-schema change spanning multiple workflow files — worth calling out as a reusable pattern for future "audit a fact across two points in time" gates.
- `[workflow]` Found two pre-existing stale rule citations (`Technical_Lead_Rules_Bootstrap.md §2`, now a numbering-gap-only section after the file's v1.5 split) inside `Shared_Pipeline_Stages_Shared_template.md`'s Stage 2 (one instance) and its `.antigravity` mirror (one instance), plus one in a Developer rules template — all outside this story's Technical Scope so left untouched, but a follow-up citation sweep would catch what the earlier split's own grep pass missed.

### What Worked Well
- A prior story's Working Record already carried the disproven commit-ordering theory and the correct two-cause breakdown for an empty check rollup — reused directly instead of re-deriving it from scratch.

## Reviewer — Developer
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
