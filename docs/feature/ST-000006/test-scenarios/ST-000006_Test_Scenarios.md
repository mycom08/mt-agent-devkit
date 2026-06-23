# Test Scenarios — ST-000006
**Story:** Split 8 mixed-mode templates into separate github/ and strict/ variants, shared logic in templates/shared/
**Validated against:** PR #11 (branch: story/ST-000006-split-mode-templates)
**Date:** 2026-06-23
**QA:** QA agent

---

## Happy Path — Template Restructure

### TS-01: Folder structure
- **Check:** `templates/github/`, `templates/strict/`, and `templates/shared/` folders exist
- **Method:** `gh api repos/.../git/trees/HEAD?recursive=1` listing
- **Result:** PASS — all three folders present with correct content

### TS-02: All 8 split candidates have a variant in each mode folder
- **Check:** github/ and strict/ each contain CLAUDE_template.md + 7 workflow variants
- **Method:** Tree listing from PR branch HEAD
- **Result:** PASS — confirmed 1 CLAUDE + 7 workflow files in each of github/ and strict/

### TS-03: Shared files with SHARED-START/END markers
- **Check:** Each of the 8 shared files has `<!-- SHARED-START -->` / `<!-- SHARED-END -->` wrapping all reused content
- **Method:** PR diff — checked all 8 shared file diffs
- **Result:** PASS — all 8 shared files have markers; header comment lists which variants include each file

### TS-04: Mode-specific variants open with reference comment
- **Check:** Every mode-specific variant (16 files = 8 github + 8 strict) starts with `<!-- Shared logic: ... -->` comment
- **Method:** PR diff
- **Result:** PASS — all mode-specific variants open with the reference comment

### TS-05: Non-split templates remain at templates/ root
- **Check:** `Sync_Devkit_Workflow_template.md`, `Workflow_Guide_template.md`, `Build_Software_Project_Workflow_template.md`, and all rules/instructions/context/scripts templates remain in original locations
- **Method:** Tree listing from PR branch HEAD
- **Result:** PASS — non-split files verified in original locations

---

## Happy Path — Workflow Updates

### TS-06: Init_Project_Workflow.md Stage 2 table
- **Check:** Stage 2 source paths table uses `templates/{mode}/` for all 8 split candidates
- **Method:** Direct file read line 90
- **Result:** PASS — table at line 90 correctly shows `templates/{mode}/CLAUDE_template.md` and `templates/{mode}/workflows/`

### TS-07: Init_Project_Workflow.md split/non-split lists
- **Check:** Split candidates list (7 workflows) and non-split list correctly differentiated
- **Method:** Lines 99-111
- **Result:** PASS — correct

### TS-08: Init_Project_Workflow.md Workflow files section
- **Check:** Section at line ~195 correctly lists split vs non-split sourcing
- **Method:** Lines 195-215
- **Result:** PASS — mode-specific sourcing correctly specified with combination instructions

### TS-09: Update_Project_Workflow.md workflow files section
- **Check:** Split candidates sourced from `templates/{mode}/workflows/`; reads Mode from target CLAUDE.md
- **Method:** Line 91-103
- **Result:** PASS — correct split/non-split sourcing with combination instructions

### TS-10: Update_Project_Workflow.md CLAUDE.md source
- **Check:** CLAUDE.md merge section uses `templates/shared/CLAUDE_Shared_template.md`
- **Method:** Line 137
- **Result:** PASS

### TS-11: Sync_Devkit_Workflow_template.md workflow files section
- **Check:** Mode-aware fetch URL `{DEVKIT_SOURCE_URL}/.claude/agents/templates/{mode}/workflows/` for split candidates
- **Method:** Diff + line 150-158
- **Result:** PASS — split candidates listed with mode-aware URL; non-split listed separately

### TS-12: Sync_Devkit_Workflow_template.md CLAUDE.md merge source
- **Check:** Uses `{DEVKIT_SOURCE_URL}/.claude/agents/templates/shared/CLAUDE_Shared_template.md`
- **Method:** Line 191
- **Result:** PASS

---

## Happy Path — Compatibility

### TS-13: changes.json 0.1.5 entry
- **Check:** Entry lists both github/ and strict/ paths for all 8 split candidates (24 new files + 1 modified)
- **Method:** changes.json content read from branch
- **Result:** PASS — 24 new files correctly enumerated; 1 modified (Sync_Devkit_Workflow_template.md)

### TS-14: Sync_Devkit cleanup expected-files list unchanged
- **Check:** The cleanup section at line 238 lists target project file names (not template paths) — unchanged
- **Method:** Sync_Devkit_Workflow_template.md lines 230-245
- **Result:** PASS — target file names (`Create_Stories_Workflow.md`, etc.) unchanged in cleanup section

### TS-15: Original 8 mixed-mode template files deleted
- **Check:** `templates/CLAUDE_TEMPLATE.md`, `templates/workflows/Sprint_Workflow_template.md`, and other 6 originals not in branch tree
- **Method:** gh api tree filtered for originals
- **Result:** PASS — empty result; originals confirmed deleted

---

## Error Case / Edge Case

### TS-16: Init_Project_Workflow.md "Files to generate" CLAUDE.md subsection — stale source reference
- **Check:** The detailed CLAUDE.md subsection (line 121) should reference the new shared/mode-specific path, not the old `templates/CLAUDE_template.md`
- **Method:** Direct read of Init_Project_Workflow.md line 121
- **Result:** **FAIL** — Line 121 still says `**Source:** \`templates/CLAUDE_template.md\`` (old deleted path). The table at line 90 and generation note at line 113 are correct but the detail subsection is stale and inconsistent.

---

## Summary

| AC | Status |
|---|---|
| templates/github/ and templates/strict/ with 8 variants each | PASS |
| templates/shared/ with 8 shared files | PASS |
| SHARED-START/END markers on all shared files | PASS |
| Header comment on each shared file listing variants | PASS |
| Mode-specific variants open with reference comment | PASS |
| Non-split templates remain at templates/ root | PASS |
| All 8 split candidates present in each mode folder | PASS |
| Init_Project_Workflow.md Stage 2 table updated | PASS |
| Init_Project_Workflow.md "Files to generate" CLAUDE.md subsection | **FAIL** |
| Update_Project_Workflow.md Stage 2 sourcing | PASS |
| Sync_Devkit_Workflow_template.md mode-aware fetch URL | PASS |
| changes.json 0.1.5 entry with all paths | PASS |
| Sync_Devkit cleanup expected-files list unchanged | PASS |
| Original 8 files deleted | PASS |

**Overall: BLOCKED — 1 AC failure (see TS-16)**
