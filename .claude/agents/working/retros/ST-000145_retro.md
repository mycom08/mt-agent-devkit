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
- `[workflow]` The `read-section` skill returned its own usage instructions instead of extracting the target section when invoked with `skill` + `args`, for two separate citations. Fell back to the documented grep/sed recipe both times with no loss of accuracy, but the skill itself did not do the extraction it exists for.
- None beyond that on the review content itself — the AC list, the disproven-ordering fact, and the validator's explicit-path baseline were all already correctly recorded in prior stories' records and reused directly.

### Process Suggestions
- `[workflow]` After creating and then removing two detached-HEAD worktrees for a differential `validate_templates.py` check, the primary checkout was found on the feature branch instead of the `main` it started the session on — exact causal mechanism not isolated (no explicit checkout was issued against the primary checkout in between), but a `git worktree list` run right after worktree removal caught it before anything was committed, and `git checkout main` restored it with no data loss. Recommend running `git branch --show-current` on the primary checkout immediately after any worktree add/remove sequence, not only at session end, regardless of suspected cause.
- `[workflow]` A gate this size (three CI states plus an independent approval-scope gate, mirrored across a template and two working copies) benefits from a differential worktree check as the default verification method for `validate_templates.py`, rather than trusting a single-tree run — the same recipe used here (bare CI-equivalent invocation plus an explicit-path diff against a same-tree base) cleanly separated "new regression" from "known pre-existing findings" without re-deriving the ~160-line baseline from scratch.

### What Worked Well
- Comparing the touched section of the two working mirrors (`.claude/agents/working/workflows/Shared_Pipeline_Stages.md` and its `.antigravity` counterpart) as an exact line-range diff — rather than reading each in full — caught full parity on the actual PR delta in one command, with no risk of the mirror's known pre-existing staleness being misread as this story's fault.
- The disproven-ordering fact and the two-cause empty-rollup breakdown were both already on record from a prior story; the new gate text cites the disproof correctly instead of re-introducing the folk theory, confirming the record transferred cleanly into new instruction text.

## QA
### Impediments & Unclear Points
*(stage skipped — non-behavioral fast path, no agent spawned)*

### Process Suggestions
*(stage skipped — non-behavioral fast path, no agent spawned)*

### What Worked Well
*(stage skipped — non-behavioral fast path, no agent spawned)*

## Product Owner
### Impediments & Unclear Points
*(stage skipped — non-behavioral fast path, no agent spawned)*

### Process Suggestions
*(stage skipped — non-behavioral fast path, no agent spawned)*

### What Worked Well
*(stage skipped — non-behavioral fast path, no agent spawned)*

## Orchestrator
### Observations
- [orchestrator] ST-000148's Retro Review never ran — the user moved straight to this story, so its 15 signal-tagged items are still unapproved and `sprint_6_summary.md` has no ST-000148 section. Its retro file is deliberately **not** deleted and its observations were committed to git (`ec1a876`) before this state file was overwritten. ST-000148's Observations are not carried forward here; they live in that retro file.
- [orchestrator] AC 9 instructed the manual `version.txt` bump that ST-000148 removed from the corpus one merge earlier. Corrected in the issue body at story start rather than left for the implementer to trip over, with the edit stamped in the AC text. A story sitting in the backlog across a process change can carry an AC that the corpus now forbids; nothing checks for that.
- [Technical Lead] The `read-section` skill returned its own usage instructions rather than performing the extraction; the agent ran the grep/sed steps by hand each time, costing extra round-trips.
- [orchestrator] Stage 2 specifies the Developer peer reviewer at model opus / effort medium, but the user changed the Developer agent definition to `model: sonnet` / `effort: high` this session. Honoured the user's explicit override — no model argument passed, so the definition applies. The workflow text and the agent definition now disagree in writing.
- [Developer] The `read-section` skill returned its own usage instructions instead of performing the extraction — second agent this story to hit it, after the TL. Both fell back to manual grep/sed.
- [orchestrator] Both new gates were run against this PR itself before merging, even though the merged text does not bind its own merge. Worth making the standard for a story that closes a process gap.
- [orchestrator] My first mirror-parity check normalised `.claude` to a placeholder in one file only, which flagged a false divergence on a line that correctly cites the real CI filter paths in both mirrors. Path-normalised comparison is unsafe when the text legitimately names one specific tree.
