# Update Project Workflow

Triggered by: `"update project [path]"` in the devkit's CLAUDE.md

Applies the current local devkit templates to an already-initialized target project, using the same merge strategy as the `update agents` command that runs inside target projects. Uses local template files directly — no GitHub fetch required.

---

## Stage 0 — Path Resolution and Version Check

1. If the user included a path in the trigger command, use it as `TARGET_PROJECT`.
   If no path was provided, ask: **"What is the path to the target project?"** Wait for the answer.
2. Verify `TARGET_PROJECT` exists and contains a `CLAUDE.md` at its root.
   - If not found → stop and notify the user.
3. Verify `TARGET_PROJECT/CLAUDE.md` contains `**Devkit version:**`.
   - If missing → stop and notify: _"This project was initialized before version tracking was added. Add `**Devkit version:** 0.0.0` to its CLAUDE.md to enable updates."_
4. Read `**Devkit version:**` from `TARGET_PROJECT/CLAUDE.md` → `PROJECT_VERSION`
5. Read `version.txt` from the devkit root → `DEVKIT_VERSION`
6. Compare:
   - If `PROJECT_VERSION == DEVKIT_VERSION` → notify: _"Project is already up to date (v{DEVKIT_VERSION})."_ Stop.
   - If `PROJECT_VERSION != DEVKIT_VERSION` → notify: _"Updating v{PROJECT_VERSION} → v{DEVKIT_VERSION}"_ and proceed to Stage 1.

---

## Stage 1 — Resolve Changed Files

Read `changes.json` from the devkit root to determine which files need updating.

Collect every version between `PROJECT_VERSION` (exclusive) and `DEVKIT_VERSION` (inclusive) in ascending order. For each version:

| Condition | Action |
|---|---|
| Version key exists AND file list is non-empty | Add listed files to the **targeted update set** |
| Version key exists AND file list is empty `[]` | No files changed in this version — skip |
| Version key is **missing** from `changes.json` | **Trigger full scan** — compare all template files |

Deduplicate the targeted update set after collecting across all versions.

**If full scan was triggered**, notify the user:
> _"No change manifest found for one or more versions — running full scan to ensure nothing is missed."_

After resolving, report the update plan before writing anything:

```
Update plan: v{PROJECT_VERSION} → v{DEVKIT_VERSION}
Target: {TARGET_PROJECT}

Files to update (targeted):        ← if changes.json resolved cleanly
  - CLAUDE.md (merge)
  - rules/Developer_Rules.md (overwrite)
  ...

  — or —

Full scan triggered                ← if any version was missing from changes.json
  Files to overwrite:  rules/ (N), workflows/ (N)
  Files to merge:      instructions/ (5), CLAUDE.md
  Files to skip:       Project_Priming.md, memory/ (5), working-record/ (5)
```

Then ask: **"Proceed with update? Reply yes to apply or no to cancel."**

- **yes** → proceed to Stage 2
- **no** → stop; no files written

---

## Stage 2 — Apply Updates

All source files are read from the **local devkit** at `.claude/agents/templates/`. Apply only the files resolved in Stage 1 according to their merge strategy. Log each file as it is written. If any file fails, log the error and continue — do not abort the entire update.

### Rules files — Overwrite

**Source:** `.claude/agents/templates/rules/{filename}_template.md` (local devkit)
**Target:** `{TARGET_PROJECT}/.claude/agents/rules/{filename}.md`

Read locally and write verbatim. No project-specific content lives here.

Files: all rules template files. Include `Strict_Mode_Story_Guide.md` only if the target project's `**Mode:**` is `strict`.

### Workflow files — Overwrite

**Source:** `.claude/agents/templates/workflows/{filename}_template.md` (local devkit)
**Target:** `{TARGET_PROJECT}/.claude/agents/workflows/{filename}.md`

Read locally and write verbatim. No project-specific content lives here.

Files: all workflow template files except `Analyst_Workflow.md` and `Init_Project_Workflow.md` (devkit-internal — never written to target projects).

### Instruction files — Merge

**Source:** `.claude/agents/templates/instructions/{role}_instructions_template.md` (local devkit)
**Target:** `{TARGET_PROJECT}/.claude/agents/instructions/{role}_instructions.md`

1. Read the local template
2. Read the existing file in the target project
3. Identify **project-specific sections** — sections referencing the project's actual tech stack, frameworks, tooling, commands, file paths, or conventions
4. Identify **role-logic sections** — generic rules, workflow steps, memory/record instructions that apply to any project
5. Apply updated role-logic sections verbatim; preserve project-specific sections unchanged
6. New sections in the template not present locally → append verbatim if role-logic; append with `[UPDATE REQUIRED]` placeholder if project-specific, and notify the user

### CLAUDE.md — Merge

**Source:** `.claude/agents/templates/CLAUDE_TEMPLATE.md` (local devkit)
**Target:** `{TARGET_PROJECT}/CLAUDE.md`

1. Read the local template
2. Read the existing `CLAUDE.md` in the target project
3. **Preserve** — never overwrite:
   - `**Mode:**`
   - `**Devkit source:**`
   - `**Devkit version:**` (updated in Stage 3)
   - `## Project Overview` content
4. **Replace verbatim** from the local template:
   - `## Agent File Integrity`
   - `## Agent Session Management`
   - `## Agent Completion Reports`
   - `## Workflows` routing table (preserve `update agents` row)
   - `## Sprint Workflow`
   - `## Start Story Workflow`
   - `## Shared Pipeline Stages`
   - `## Refine Sprint Workflow`
   - `## Plan Next Sprint Workflow`
   - `## Analyst Workflow`
   - `## PR Approval Rule`
5. New top-level sections in the template not present locally → append after the last existing section

### Project_Priming.md — Skip

Never modify. This file is 100% project-specific.

### Memory files — Skip (append new sections only)

Never overwrite. If the local template adds a new `##` section not present in the target project's memory file → append it empty at the end of the file.

### Working-record files — Skip (append new sections only)

Same rule as memory files.

### Cleanup — Remove Stale Files

After all updates are applied, scan each managed directory in `TARGET_PROJECT` and flag any file not in the known expected set.

**Expected files — `rules/`:**
`Agent_Common.md`, `Blocked_Request.md`, `Business_Analyst_Rules.md`, `CICD_Validation_Guide.md`, `Clean_Code_Rules.md`, `Developer_Rules.md`, `Product_Owner_Rules.md`, `QA_Rules.md`, `Retro_Rules.md`, `Story_Standard.md`, `Story_Standard_Dev.md`, `Story_Standard_PO.md`, `Story_Standard_QA.md`, `Story_Standard_TL.md`, `Technical_Lead_Rules.md`, `Strict_Mode_Story_Guide.md` (strict mode only)

**Expected files — `workflows/`:**
`Create_Stories_Workflow.md`, `Plan_Sprint_Workflow.md`, `Refine_Sprint_Workflow.md`, `Resume_Story_Workflow.md`, `Shared_Pipeline_Stages.md`, `Sprint_Workflow.md`, `Start_Story_Workflow.md`, `Update_Agents_Workflow.md`, `Workflow_Guide.md`

Directories never scanned for cleanup: `memory/`, `working-record/`, `docs/`, `tmp/`, `context/` — these are project-owned and may contain custom files.

If any unexpected files are found, report them to the user:

```
Stale files found in {TARGET_PROJECT}:
  rules/Developer_Rules_template.md
  workflows/Token_Probe_Workflow.md

These files are not part of the devkit structure. Remove them? Reply yes to delete or no to keep.
```

- **yes** → delete the listed files and log each deletion
- **no** → leave them in place; note them in the completion report

If no unexpected files are found, skip this step silently.

---

## Stage 3 — Finalize

1. Update `**Devkit version:**` in `{TARGET_PROJECT}/CLAUDE.md` to `DEVKIT_VERSION`
2. Write `DEVKIT_VERSION` to `{TARGET_PROJECT}/.claude/agents/devkit_version.txt`
3. Report completion to the user:

```
Update complete: v{PROJECT_VERSION} → v{DEVKIT_VERSION}
Target: {TARGET_PROJECT}

Updated:
  - <list each file written>

Skipped (project-owned):
  - Project_Priming.md
  - memory/        (5 files)
  - working-record/ (5 files)

[If any [UPDATE REQUIRED] placeholders were inserted]:
  Action needed: N instruction sections need project-specific content.
  Search for [UPDATE REQUIRED] in {TARGET_PROJECT}/.claude/agents/instructions/ to find them.
```

---

## Pipeline Rules

- **Never write before user confirms** in Stage 1
- **Never overwrite** `Project_Priming.md`, `memory/`, `working-record/`, or `docs/`
- **Missing version in changes.json = full scan** — never silently skip an unknown version
- **Log every file written** — the user must be able to see exactly what changed
- **Merge preserves project content** — when in doubt about whether a section is project-specific, keep the existing file and notify the user
- **Source is always local** — this workflow reads from the devkit's own template files, never from GitHub
- **State file cleanup** — no persistent state file needed; the workflow is short enough to restart cleanly if interrupted
