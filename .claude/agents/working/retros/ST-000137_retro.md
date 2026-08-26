# Retrospective — ST-000137
**Date:** 2026-08-26
**Story:** Move Shell Command Rules out of the five Story_Standard role views into Agent_Common_Bootstrap.md

## Implementer — Developer
### Impediments & Unclear Points
- `[instruction]` The spawn prompt said the retro skeleton "already has a skeleton" for this story, but `.claude/agents/working/retros/` had no such file — created it from scratch mirroring a prior story's shape.
  Reinforces: `ST-000124_retro.md` Process Suggestions bullet — same gap recurring, worth a workflow fix (orchestrator should verify the skeleton exists before asserting it does in the spawn prompt).
- `[context]` The issue's pre-drafted citation inventory (compiled by full-corpus grep before drafting) named two sites in `Product_Owner_Rules_Read_On_Demand_template.md` on each template surface, but current content on both surfaces has zero matching citations — that content had already been relocated to a different file by an earlier, unrelated story. A single-point-in-time grep snapshot can go stale between drafting and pickup even within the same sprint; re-verified by direct grep before touching that file rather than trusting the inventory blindly.

### Process Suggestions
- `[workflow]` When a story's Technical Scope embeds a "canonical text to move" block sourced from one surface (here, the Claude templates), it should explicitly call out any per-surface content divergence beyond simple placeholder substitution (e.g. a `--repo` value) — this story had a real wording difference (Bash-only vs. PowerShell-preferred) between the Claude and Antigravity template surfaces that wasn't mentioned in the canonical text block, requiring an extra verification pass to avoid silently dropping a platform-specific convention.
- `[failure]` A change-manifest file with both a per-version array (`new`/`modified` paths) and a separate nested per-path description dict is easy to half-update: appending to the array satisfies a schema-shape check but silently skips the description dict if the implementer only pattern-matches on the array structure during exploration. Caught in Stage 2 review, not self-caught. **Addendum:** re-verified by inspecting the manifest's actual nested structure (not just the top-level arrays) before writing the fix, then confirmed via key-count diff (`36 → 40`, matching the 4 newly-modified paths) that every touched path had a description — this two-step check (structure-first, then count-diff) is the concrete guard worth carrying into any future manifest edit on this file.

### What Worked Well
- The issue's exhaustive, numbered site list (5 working + 8 Claude template + 8 Antigravity mirror) made the mechanical repoint work verifiable file-by-file with a simple pre/post `§15` grep across the whole touched tree — zero stray citations remained after the pass.
- `python scripts/validate_templates.py` passed clean on the first run after all edits, and again after the fix-loop's `changes.json` addendum — no further rework.

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
