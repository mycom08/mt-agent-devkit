# Sprint none — Retro Summary
**Sprint:** none (single-story run)
**Last Updated:** 2026-06-23

---

## ST-000006 — Split mixed-mode templates into github/ and strict/ folders
**Date:** 2026-06-23
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 1

### Findings
- `[workflow]` No rule in TL review checklist for confirming file deletions/renames via branch tree *(Technical Lead)*
- `[context]` `changes.json` scope (template files only, devkit-internal excluded) was undocumented *(Technical Lead)*
- `[workflow]` TL review checklist missing old-path grep step for path-reference stories *(QA)*
- `[workflow]` `Init_Project_Workflow.md` had duplicate source declarations for CLAUDE.md — drift surface *(QA)*

### What Worked Well
- `<!-- SHARED-START -->` / `<!-- SHARED-END -->` marker strategy clean and easy to apply consistently across all 8 split candidates *(Developer, Technical Lead, QA)*
- TL mandatory design correction (delete originals) was unambiguous *(Developer)*
- Mode-specific variant files thin and clear — separation unambiguous at a glance *(Technical Lead)*
- `changes.json` 0.1.5 `new` array correctly grouped (shared → github → strict per workflow) *(Technical Lead, QA)*

### Actions Applied
- `.claude/agents/working/rules/Technical_Lead_Rules.md` — added file-deletion/rename verification step and old-path grep step to §2 documentation review checklist; added `changes.json` scope note to §4
- `.claude/agents/templates/rules/Technical_Lead_Rules_template.md` — added file-deletion/rename and old-path grep bullets to documentation stories review checklist
- `.claude/agents/working/context/Project_Priming.md` — expanded `changes.json` row in §7 with scope note
- `.claude/agents/workflows/Init_Project_Workflow.md` — added drift-guard comment to CLAUDE.md `**Source:**` line in Files to generate subsection
