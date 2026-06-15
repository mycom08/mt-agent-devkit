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

## Stage 1 — Resolve Changed Files

Fetch `{DEVKIT_SOURCE_URL}/changes.json` to determine which files need updating.

Collect every version between `CURRENT_VERSION` (exclusive) and `LATEST_VERSION` (inclusive) in ascending order. For each version:

| Condition | Action |
|---|---|
| Version key exists in `changes.json` AND file list is non-empty | Add listed files to the **targeted update set** |
| Version key exists in `changes.json` AND file list is empty `[]` | No files changed in this version — skip |
| Version key is **missing** from `changes.json` | **Trigger full scan** — fetch and compare all template files |

Deduplicate the targeted update set after collecting across all versions.

**If full scan was triggered**, notify the user:
> _"No change manifest found for one or more versions — running full scan to ensure nothing is missed."_

After resolving, report the update plan to the user before writing anything:

```
Update plan: v{CURRENT_VERSION} → v{LATEST_VERSION}

Files to update (targeted):        ← if changes.json resolved cleanly
  - CLAUDE.md (merge)
  - rules/Developer_Rules.md (overwrite)
  ...

  — or —

Full scan triggered (N files)      ← if any version was missing from changes.json
  Files to overwrite:  rules/ (N), workflows/ (N)
  Files to merge:      instructions/ (5), CLAUDE.md
  Files to skip:       Project_Priming.md, memory/ (5), working-record/ (5)
```

Then ask: **"Proceed with update? Reply yes to apply or no to cancel."**

- **yes** → proceed to Stage 2
- **no** → stop; no files written

---

## Stage 2 — Apply Updates

Apply only the files resolved in Stage 1. Each file is processed according to its merge strategy below. Log each file as it is written. If any file fails, log the error and continue — do not abort the entire update.

### Merge strategy by file type

#### Rules files — Overwrite

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/rules/{filename}_template.md`
**Target:** `.claude/agents/rules/{filename}.md`

Fetch and write verbatim. No project-specific content lives here.

Applies to: `Agent_Common.md`, `Blocked_Request.md`, `Business_Analyst_Rules.md`, `CICD_Validation_Guide.md`, `Clean_Code_Rules.md`, `Developer_Rules.md`, `Product_Owner_Rules.md`, `QA_Rules.md`, `Retro_Rules.md`, `Story_Standard.md`, `Story_Standard_Dev.md`, `Story_Standard_PO.md`, `Story_Standard_QA.md`, `Story_Standard_TL.md`, `Technical_Lead_Rules.md`, and `Strict_Mode_Story_Guide.md` (only if `Mode: strict`).

#### Workflow files — Overwrite

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/workflows/{filename}_template.md`
**Target:** `.claude/agents/workflows/{filename}.md`

Fetch and write verbatim. No project-specific content lives here.

Applies to: `Create_Stories_Workflow.md`, `Plan_Sprint_Workflow.md`, `Refine_Sprint_Workflow.md`, `Resume_Story_Workflow.md`, `Shared_Pipeline_Stages.md`, `Sprint_Workflow.md`, `Start_Story_Workflow.md`, `Update_Agents_Workflow.md` (this file), `Workflow_Guide.md`.

#### Instruction files — Merge

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/instructions/{role}_instructions_template.md`
**Target:** `.claude/agents/instructions/{role}_instructions.md`

1. Fetch the latest template
2. Read the existing local file
3. Identify **project-specific sections** — sections referencing the project's actual tech stack, frameworks, tooling, commands, file paths, or conventions (written or edited during `init project`)
4. Identify **role-logic sections** — generic rules, workflow steps, memory/record instructions that apply to any project
5. Apply updated role-logic sections verbatim; preserve project-specific sections unchanged
6. New sections added by the template → append verbatim if role-logic; append with `[UPDATE REQUIRED]` placeholder if project-specific, and notify the user

#### CLAUDE.md — Merge

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/CLAUDE_TEMPLATE.md`

1. Fetch the latest template
2. Read the existing local `CLAUDE.md`
3. **Preserve** — never overwrite:
   - `**Mode:**`
   - `**Devkit source:**`
   - `**Devkit version:**` (updated in Stage 3)
   - `## Project Overview` content
4. **Replace verbatim** from the updated template:
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

#### Project_Priming.md — Skip

Never fetch or modify. This file is 100% project-specific.

#### Memory files — Skip (append new sections only)

Never overwrite. If the template adds a new `##` section not present locally → append it empty at the end of the file.

#### Working-record files — Skip (append new sections only)

Same rule as memory files.

### Cleanup — Remove Stale Files

After all updates are applied, scan each managed directory and flag any file not in the known expected set.

**Expected files — `rules/`:**
`Agent_Common.md`, `Blocked_Request.md`, `Business_Analyst_Rules.md`, `CICD_Validation_Guide.md`, `Clean_Code_Rules.md`, `Developer_Rules.md`, `Product_Owner_Rules.md`, `QA_Rules.md`, `Retro_Rules.md`, `Story_Standard.md`, `Story_Standard_Dev.md`, `Story_Standard_PO.md`, `Story_Standard_QA.md`, `Story_Standard_TL.md`, `Technical_Lead_Rules.md`, `Strict_Mode_Story_Guide.md` (strict mode only)

**Expected files — `workflows/`:**
`Create_Stories_Workflow.md`, `Plan_Sprint_Workflow.md`, `Refine_Sprint_Workflow.md`, `Resume_Story_Workflow.md`, `Shared_Pipeline_Stages.md`, `Sprint_Workflow.md`, `Start_Story_Workflow.md`, `Update_Agents_Workflow.md`, `Workflow_Guide.md`

Directories never scanned for cleanup: `memory/`, `working-record/`, `docs/`, `tmp/`, `context/` — these are project-owned and may contain custom files.

If any unexpected files are found, report them to the user:

```
Stale files found:
  rules/Developer_Rules_template.md
  workflows/Token_Probe_Workflow.md

These files are not part of the devkit structure. Remove them? Reply yes to delete or no to keep.
```

- **yes** → delete the listed files and log each deletion
- **no** → leave them in place; note them in the completion report

If no unexpected files are found, skip this step silently.

---

## Stage 3 — Finalize

1. Update `**Devkit version:**` in `CLAUDE.md` to `LATEST_VERSION`
2. Write `LATEST_VERSION` to `.claude/agents/devkit_version.txt`
3. Report completion to the user:

```
Update complete: v{CURRENT_VERSION} → v{LATEST_VERSION}

Updated:
  - <list each file written>

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
- **Missing version in changes.json = full scan** — never silently skip an unknown version
- **Log every file written** — the user must be able to see exactly what changed
- **Merge preserves project content** — when in doubt about whether a section is project-specific, keep the local version and notify the user
- **This file updates itself** — `Update_Agents_Workflow.md` is in the overwrite list; the new version takes effect after this run completes
