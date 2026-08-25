# Retrospective — ST-000135
**Date:** 2026-08-25
**Story:** Carry two-tier memory split (Dev/QA/TL) into templates/ (Claude + Antigravity)

## Implementer — Developer
### Impediments & Unclear Points
- `[workflow]` The story pointed at a reference commit's diff to derive the pattern, but reading the *current* working copy state (`Agent_Common_Read_On_Demand.md §8`, three instruction files, blank memory-file shape) was cheaper and more reliable than re-deriving the diff from the merged commits — the working copy already carries the final, validated form.
- `[context]` `Agent_Common_Read_On_Demand_template.md`'s header note already referenced "§1's closing two-tier note" before this story started, but §1 itself had no such note — a stale forward reference anticipating this exact story. Fixed as part of implementation per the mandatory-read-before-editing rule (note stale placeholders/forward references and fix them in scope), not filed as a separate finding.
- `[context]` The template's own `Agent_Common_Read_On_Demand_template.md` had no §7 at all (unlike the working copy, where §7 is a retired/gap section) — so appending §8 left two numbering gaps (§4, §7) instead of one. Updated the file's own header gap-note to describe both, rather than leaving the note stale for the next reader.

### Process Suggestions
- `[workflow]` The Antigravity surface has no `read-section` skill and no `.claude/skills/` mirror, so every "use the `read-section` skill" sentence in the Claude-surface source needed a hand-adapted "locate by grep" rewrite, not a mechanical find-replace — worth calling out explicitly in `Project_Priming_Read_On_Demand.md §15`'s split/port checklist as its own line item, since it's easy to port prose verbatim and only notice the skill doesn't exist on that surface during review.
- `[workflow]` `.claude/agents/working/scripts/scaffold_mechanical.ps1` (Claude surface) does not exist at all — only `.sh` — while the Antigravity surface has both `.sh` and `.ps1`. A story prompt phrased as "scaffold_mechanical.sh/.ps1 (both Claude and Antigravity surfaces)" reads as 4 files but resolves to 3; worth a quick `find -iname` check before assuming a symmetric file matrix across surfaces.

### What Worked Well
- Dry-running both `scaffold_mechanical.sh` variants (Claude and Antigravity) against a scratch scaffold target before opening the PR caught the exact rendered output (blank two-tier pair for Dev/QA/TL, unchanged single file for PO/BA/UI-UX Designer) rather than trusting the bash logic by inspection alone — cheap and specific.
- `validate_templates.py`'s Root-2 resolution (`.claude/agents/<rest>` → `.claude/agents/working/<rest>`) already resolved every new `<Role>_Memory_Archive.md` reference for free, since the devkit's own working copy already has those files from the original pilot (PR #139) — no validator config change was needed for the new instruction-file citations.

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
