# Update Agents Workflow

Triggered by: `"update agents"` in the target project's CLAUDE.md

Fetches the latest agent template files from the devkit GitHub repository and applies them to this project, preserving all project-specific content.

---

## Prerequisites

Before starting, read from this project's `CLAUDE.md`:
- `**Devkit source:**` — the raw GitHub base URL (e.g. `https://raw.githubusercontent.com/YOUR_ORG/mt-agent-devkit/main`)
- `**Devkit version:**` — the version currently installed in this project

If either field is missing or contains a placeholder URL, stop and notify the user that the devkit source is not configured.

---

## Stage 0 — Version Check

1. Read `**Devkit version:**` from `CLAUDE.md` → `CURRENT_VERSION`
2. Fetch `{DEVKIT_SOURCE_URL}/version.txt` using WebFetch → `LATEST_VERSION`
   - If the fetch fails (network error, 404) → stop and notify the user; do not modify any files
3. Compare versions:
   - If `CURRENT_VERSION == LATEST_VERSION` → notify the user: _"Agent files are already up to date (v{CURRENT_VERSION})."_ Stop.
   - If `CURRENT_VERSION != LATEST_VERSION` → notify the user: _"Update available: v{CURRENT_VERSION} → v{LATEST_VERSION}"_ and proceed to Stage 1

---

## Stage 1 — Preview Changes

Before writing anything, fetch and inspect each file in the update scope (see Stage 2 for the full list). For each file:
- Fetch the latest template content from `{DEVKIT_SOURCE_URL}`
- Compare against the local file
- Classify as: **overwrite**, **merge**, or **skip**

Report a summary to the user:

```
Files to overwrite:   rules/ (N files), workflows/ (N files)
Files to merge:       instructions/ (5 files), CLAUDE.md
Files to skip:        Project_Priming.md, memory/ (5 files), working-record/ (5 files)
```

Then ask: **"Proceed with update? Reply yes to apply or no to cancel."**

- **yes** → proceed to Stage 2
- **no** → stop; no files written

---

## Stage 2 — Apply Updates

Apply updates file by file according to the merge strategy below. After each file is written, log it. If any file fails, log the error and continue with the remaining files — do not abort the entire update.

### Rules files — Overwrite

**Source path pattern:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/rules/{filename}_template.md`
**Target path:** `.claude/agents/rules/{filename}.md`

Fetch each rules file and write it verbatim to the target path. These files contain no project-specific content.

Files:
- `Agent_Common.md`
- `Blocked_Request.md`
- `Business_Analyst_Rules.md`
- `CICD_Validation_Guide.md`
- `Clean_Code_Rules.md`
- `Developer_Rules.md`
- `Product_Owner_Rules.md`
- `QA_Rules.md`
- `Retro_Rules.md`
- `Story_Standard.md`
- `Story_Standard_Dev.md`
- `Story_Standard_PO.md`
- `Story_Standard_QA.md`
- `Story_Standard_TL.md`
- `Strict_Mode_Story_Guide.md` (only if `Mode: strict`)
- `Technical_Lead_Rules.md`

### Workflow files — Overwrite

**Source path pattern:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/workflows/{filename}_template.md`
**Target path:** `.claude/agents/workflows/{filename}.md`

Fetch each workflow file and write it verbatim. These files contain no project-specific content.

Files:
- `Create_Stories_Workflow.md`
- `Plan_Sprint_Workflow.md`
- `Refine_Sprint_Workflow.md`
- `Resume_Story_Workflow.md`
- `Shared_Pipeline_Stages.md`
- `Sprint_Workflow.md`
- `Start_Story_Workflow.md`
- `Update_Agents_Workflow.md` ← this file itself
- `Workflow_Guide.md`

### Instruction files — Merge

**Source path pattern:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/instructions/{role}_instructions_template.md`
**Target path:** `.claude/agents/instructions/{role}_instructions.md`

For each instruction file, the merge strategy is:

1. Fetch the latest template
2. Read the existing local file
3. Identify which sections in the local file contain **project-specific content** — these are sections that reference the project's actual tech stack, frameworks, tooling, commands, file paths, or conventions. They were generated or edited during `init project`.
4. Identify which sections are **pure role logic** — generic rules, workflow steps, memory/record instructions that apply to any project.
5. Apply the updated template's role-logic sections verbatim; preserve the local project-specific sections unchanged.
6. If the updated template adds a **new section** that does not exist locally → append it. If the new section is role-logic, append it verbatim. If it requires project-specific content, append it with `[UPDATE REQUIRED]` placeholders and notify the user.

### CLAUDE.md — Merge

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/CLAUDE_template.md`

1. Fetch the latest template
2. Read the existing local `CLAUDE.md`
3. Preserve these fields from the local file — never overwrite them:
   - `**Mode:**`
   - `**Devkit source:**`
   - `**Devkit version:**` (this will be updated in Stage 3)
   - The `## Project Overview` content (project name and description)
4. Replace all orchestrator sections verbatim from the updated template:
   - `## Agent Session Management`
   - `## Agent Completion Reports`
   - `## Workflows` routing table (re-add the `update agents` row after replacing)
   - `## Sprint Workflow`
   - `## Start Story Workflow`
   - `## Shared Pipeline Stages`
   - `## Refine Sprint Workflow`
   - `## Plan Next Sprint Workflow`
   - `## Analyst Workflow`
   - `## PR Approval Rule`
5. If the updated template adds a new top-level section not present locally → append it after the last existing section.

### Project_Priming.md — Skip

Never fetch or modify. This file is 100% project-specific.

### Memory files — Skip (append new sections only)

Never overwrite. If the latest template version adds a new named section (identified by a `##` heading) that does not exist in the local memory file → append it empty at the end of the file.

### Working-record files — Skip (append new sections only)

Same rule as memory files.

### devkit_version.txt — Never touch during update (updated in Stage 3)

---

## Stage 3 — Finalize

1. Update `**Devkit version:**` in `CLAUDE.md` to `LATEST_VERSION`
2. Write `LATEST_VERSION` to `.claude/agents/devkit_version.txt`
3. Report completion to the user:

```
Update complete: v{CURRENT_VERSION} → v{LATEST_VERSION}

Updated:
  - rules/         (N files overwritten)
  - workflows/     (N files overwritten)
  - instructions/  (5 files merged)
  - CLAUDE.md      (orchestrator sections replaced)

Skipped (project-owned):
  - Project_Priming.md
  - memory/        (5 files)
  - working-record/ (5 files)

[If any [UPDATE REQUIRED] placeholders were inserted]:
  Action needed: N instruction sections need project-specific content.
  Search for [UPDATE REQUIRED] in .claude/agents/instructions/ to find them.
```

---

## Pipeline Rules

- **Never write before user confirms** in Stage 1
- **Never overwrite** `Project_Priming.md`, `memory/`, `working-record/`, or `docs/`
- **Fail safe on network error** — if any fetch fails, log it and skip that file; never write partial content
- **Log every file written** — the user should be able to see exactly what changed
- **Merge preserves project content** — when in doubt about whether a section is project-specific, keep the local version and notify the user
- **This file updates itself** — `Update_Agents_Workflow.md` is in the overwrite list; the new version takes effect after this run completes
