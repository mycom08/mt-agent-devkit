# Sprint none — Retro Summary
**Sprint:** none (single-story run)
**Last Updated:** 2026-08-25

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

---

## ST-000132 — Carry Agent_Common bootstrap/on-demand split into templates/ (Claude + Antigravity)
**Date:** 2026-08-25
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[instruction]` Reference files named but the section-boundary/renumbering scheme itself had to be reverse-engineered via `git show` before any file could be written *(Developer)*
- `[workflow]` `validate_templates.py`'s section-ref checker treats any bare `§N` substring as a citation, with no carve-out for prose describing an intentional numbering gap *(Developer)*
- `[context]` `changes.json` only ever tracks `.claude/agents/templates/...` paths, never `.antigravity/...` — no manifest-integrity check for the Antigravity template split *(Developer)*
- `[workflow]` A "splitting a shared rules file into bootstrap/on-demand tiers" checklist would turn a multi-hour discovery pass into a lookup *(Developer)*
- `[instruction]` Dev branch should be confirmed as created before the *first file write*, not just before the first commit *(Developer)*
- `[workflow]` The `read-section` skill's own worked example went stale when its cited source file was deleted/split; no documented convention for repointing it, and two independent ad hoc fixes have now happened *(Developer)*

### What Worked Well
- `python scripts/validate_templates.py` caught the numbering-gap false-positive immediately and precisely (file:line) *(Developer)*
- Reading the reference commit (`git show e691bd9 --stat` + diffing citing files) gave an exact, unambiguous model for the split boundary *(Developer)*
- `git stash push -u` / branch-recreate / `git stash pop` cleanly recovered from starting work on the wrong base branch, zero lost work *(Developer)*

### Actions Applied
- `.claude/agents/working/context/Project_Priming_Bootstrap.md` — §15 routing-table row now also names the split-file checklist
- `.claude/agents/working/context/Project_Priming_Read_On_Demand.md` — added "Splitting a Shared Rules/Instructions File into Bootstrap/On-Demand Tiers" checklist to §15 (citations, workflow enumerations, `changes.json`, validator allowlists, `read-section` worked example, §N-vs-prose convention)
- `scripts/validate_templates.py` — documented the §N-vs-prose limitation as a code comment on `check_section_refs`
- `.claude/agents/working/rules/Product_Owner_Rules_Read_On_Demand.md` — added "Porting an already-validated pattern" guidance to the Story Creation Template section
- `.claude/agents/working/rules/Story_Standard.md` — mirrored the same guidance in the master §13
- *(not applied — user deferred)* `changes.json` Antigravity manifest-coverage gap and Dev branch-before-write ordering tightening
