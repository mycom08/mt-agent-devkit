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

### What Worked Well
- The issue's exhaustive, numbered site list (5 working + 8 Claude template + 8 Antigravity mirror) made the mechanical repoint work verifiable file-by-file with a simple pre/post `§15` grep across the whole touched tree — zero stray citations remained after the pass.
- `python scripts/validate_templates.py` passed clean on the first run after all edits — no rework needed.

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
