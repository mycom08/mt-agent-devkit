# Sync Devkit Workflow

Triggered by: `"sync devkit"` or `"sync devkit --auto"` in the target project's CLAUDE.md

The `--auto` flag skips the Stage 1 user confirmation. The update plan is still printed but no reply is required before writing begins.

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

### changes.json format

Two formats are supported. Entries for older versions use a plain array; entries for v0.0.8 and later use an object:

```json
{
  "0.0.7": [".claude/agents/templates/..."],
  "0.0.8": {
    "files": [".claude/agents/templates/..."],
    "descriptions": {
      ".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md": "Added auto-approve, checksums, WebFetch fallback"
    },
    "checksums": {
      ".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md": "sha256:abc123"
    }
  }
}
```

When parsing, if the version value is an array → treat as `files` only (no descriptions or checksums). If it is an object → read `files`, `descriptions`, and `checksums` fields.

### Resolving the file set

Collect every version between `CURRENT_VERSION` (exclusive) and `LATEST_VERSION` (inclusive) in ascending order. For each version:

| Condition | Action |
|---|---|
| Version key exists AND file list is non-empty | Add listed files to the **targeted update set** |
| Version key exists AND file list is empty | No files changed in this version — skip |
| Version key is **missing** from `changes.json` | **Trigger full scan** — fetch and compare all template files |

Deduplicate the targeted update set after collecting across all versions.

**If full scan was triggered**, notify the user:
> _"No change manifest found for one or more versions — running full scan to ensure nothing is missed."_

### Checksum pre-filter (overwrite-strategy files only)

For each file in the targeted update set that uses the **overwrite** strategy (workflow files, script files, skill files), and where `changes.json` provides a checksum for that file:

1. Read the local installed file
2. Compute its SHA-256
3. If it matches the checksum in `changes.json` → mark the file as **skip (already up to date)** and exclude it from the write set

This avoids fetching and rewriting files whose content is already current.

### Update plan

After resolving, report the update plan to the user before writing anything:

```
Update plan: v{CURRENT_VERSION} → v{LATEST_VERSION}

Files to update (targeted):
  - CLAUDE.md (merge)
  - rules/Developer_Rules.md (overwrite) — Added strict-mode gate    ← description shown when available
  - workflows/Sprint_Workflow.md (skip — already up to date)          ← checksum match

  — or —

Full scan triggered (N files)
  Files to overwrite:  rules/ (N), workflows/ (N), Orchestrator_Guide.md, skills/read-section/SKILL.md
  Files to merge:      instructions/ (6), CLAUDE.md
  Files to skip:       Project_Priming.md, memory/ (6), working-record/ (6)
```

Then ask: **"Proceed with update? Reply yes to apply or no to cancel."**

- **yes** → proceed to Stage 2
- **no** → stop; no files written

**If `--auto` flag was passed**, skip the confirmation and proceed to Stage 2 immediately after printing the update plan.

---

## Stage 2 — Apply Updates

Apply only the files resolved in Stage 1. Each file is processed according to its merge strategy below. Log each file as it is written. If any file fails, log the error and continue — do not abort the entire update.

### Fetch strategy

Use WebFetch to retrieve all remote files. If a fetched file appears truncated or summarized — content is abnormally short, contains ellipsis, or is missing sections that are expected based on the file type — fall back to Bash curl:

```bash
curl -sf "{DEVKIT_SOURCE_URL}/path/to/file"
```

If both WebFetch and curl fail for a file, log the failure and skip that file; do not write partial content.

### Merge strategy by file type

#### Rules files — Adapt to mode

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/rules/{filename}_template.md`
**Target:** `.claude/agents/rules/{filename}.md`

Rules files were originally generated by `init project` with mode-specific content adapted to the project. Do not overwrite verbatim — apply the same adaptation that `init project` uses:

1. Read `**Mode:**` from this project's `CLAUDE.md`
2. Fetch the template
3. Adapt the content to the project's mode:
   - **`Mode: strict`** — remove or replace any GitHub-specific content (references to `gh` CLI commands, `status:` issue labels, GitHub mentions, PR workflows, GitHub Actions). Replace with the strict-mode equivalent (local MD file operations, `**Status:**` field updates, local review records). Use `Strict_Mode_Story_Guide.md` as the reference for strict-mode substitutions.
   - **`Mode: github`** — apply the template content as-is; it is already written for GitHub mode
4. Preserve any project-specific customizations already in the local file (tech stack references, tooling commands, project-specific conventions) — do not overwrite them
5. Write the adapted result

Applies to: `Agent_Common_Bootstrap.md`, `Agent_Common_Read_On_Demand.md`, `Audit_Rules.md`, `Blocked_Request.md`, `Business_Analyst_Rules.md`, `CICD_Validation_Guide.md`, `Clean_Code_Rules.md`, `Developer_Rules.md`, `Logging_Standard.md`, `Product_Owner_Rules.md`, `QA_Rules.md`, `Retro_Rules.md`, `Story_Standard.md`, `Story_Standard_Dev.md`, `Story_Standard_PO.md`, `Story_Standard_QA.md`, `Story_Standard_TL.md`, `Technical_Lead_Rules.md`, `UI_UX_Designer_Rules.md`, `UI_Prototype_Rules.md`, and `Strict_Mode_Story_Guide.md` (only if `Mode: strict`).

#### Workflow files — Overwrite

**Source (split — mode-specific):** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/{mode}/workflows/{filename}_template.md`
**Source (non-split):** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/workflows/{filename}_template.md`
**Target:** `.claude/agents/workflows/{filename}.md`

Read `**Mode:**` from this project's `CLAUDE.md` to resolve `{mode}` (`github` or `strict`).

For split candidates, fetch the mode-specific variant. Also fetch the referenced shared file at `{DEVKIT_SOURCE_URL}/.claude/agents/templates/shared/workflows/{name}_Shared_template.md`. Combine: shared `<!-- SHARED-START -->` / `<!-- SHARED-END -->` block first, then any non-comment content from the mode-specific variant. Write the combined result verbatim.

**Split candidates (fetch from `templates/{mode}/workflows/`):**
`Create_Stories_Workflow.md`, `Plan_Sprint_Workflow.md`, `Refine_Prototype_Workflow.md`, `Refine_Sprint_Workflow.md`, `Resume_Story_Workflow.md`, `Shared_Pipeline_Stages.md`, `Sprint_Workflow.md`, `Start_Story_Workflow.md`

**Non-split (fetch from `templates/workflows/`):**
`Sync_Devkit_Workflow.md` (this file), `Workflow_Guide.md`

Applies to all 10 files listed above.

#### Script files — Overwrite

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/scripts/check_devkit_version.ps1`
          `{DEVKIT_SOURCE_URL}/.claude/agents/templates/scripts/check_devkit_version.sh`
**Target:** `.claude/agents/scripts/check_devkit_version.ps1`
          `.claude/agents/scripts/check_devkit_version.sh`

Fetch and write verbatim. Create `.claude/agents/scripts/` if it does not exist.

#### Skill files — Overwrite

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/skills/read-section/SKILL_template.md`
**Target:** `.claude/skills/read-section/SKILL.md`

Fetch and write verbatim (strip the `_template` suffix). Create `.claude/skills/read-section/` if it does not exist. Carries no project-specific content, same reasoning as script files above.

Applies to: `SKILL.md` under `skills/read-section/` (1 file).

#### Settings hook — Inject if missing

Check `.claude/settings.json` for the devkit update-check hook:
- If a `SessionStart` entry whose command references `check_devkit_version` already exists → skip
- If missing → detect OS from the environment `sync devkit` is running in, then inject the matching hook JSON. If `.claude/settings.json` already exists, merge this under its existing `hooks` key — do not remove existing hooks or keys. If it does not exist, create it with this content:
  - **Windows:**
    ```json
    { "hooks": { "SessionStart": [{ "matcher": "startup", "hooks": [{ "type": "command", "command": "powershell -File .claude/agents/scripts/check_devkit_version.ps1", "timeout": 10 }] }] } }
    ```
  - **Mac/Linux:**
    ```json
    { "hooks": { "SessionStart": [{ "matcher": "startup", "hooks": [{ "type": "command", "command": "bash .claude/agents/scripts/check_devkit_version.sh", "timeout": 10 }] }] } }
    ```

#### Instruction files — Merge

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/instructions/{role}_instructions_template.md`
**Target:** `.claude/agents/instructions/{role}_instructions.md`

1. Fetch the latest template
2. Read the existing local file
3. Identify **project-specific sections** — sections referencing the project's actual tech stack, frameworks, tooling, commands, file paths, or conventions (written or edited during `init project`)
4. Identify **role-logic sections** — generic rules, workflow steps, memory/record instructions that apply to any project
5. Apply updated role-logic sections verbatim; preserve project-specific sections unchanged
6. New sections added by the template → append verbatim if role-logic; append with `[UPDATE REQUIRED]` placeholder if project-specific, and notify the user

#### Orchestrator_Guide.md — Overwrite

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/shared/Orchestrator_Guide_Shared_template.md` (use the `<!-- SHARED-START -->` / `<!-- SHARED-END -->` block content), combined with any non-comment content from `{DEVKIT_SOURCE_URL}/.claude/agents/templates/{mode}/Orchestrator_Guide_template.md` — same combine rule as split workflow files above.
**Target:** `.claude/agents/Orchestrator_Guide.md`

Devkit-authored, devkit-merged (protected, same as `rules/` and `workflows/`) — carries no project-specific content, so always overwrite in full. Create the file if it does not exist locally yet (the common case on the first sync after ST-000043).

Applies to: `Orchestrator_Guide.md` (1 file).

**Process this file before the CLAUDE.md — Merge step below whenever both are in this run's update set.** The CLAUDE.md migration step (step 5 below) deletes local sections whose only surviving copy is this file — if the fetch/write here fails, skip the migration step entirely this run (leave the old sections in place) so a failed write never leaves the project with neither copy. Log the skip and retry both on the next sync.

#### CLAUDE.md — Merge

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/shared/CLAUDE_Shared_template.md` (use the `<!-- SHARED-START -->` / `<!-- SHARED-END -->` block content)

1. Fetch the latest template
2. Read the existing local `CLAUDE.md`
3. **Preserve** — never overwrite:
   - `**Mode:**`
   - `**Devkit source:**`
   - `**Devkit version:**` (updated in Stage 3)
   - `## Project Overview` content
   - `## Agent Roster` — project-mutable (per-project instruction-file paths, lean prototype rosters); if the template adds a new role row not already present locally, append that row only — never touch existing rows or replace the section wholesale
4. **Replace verbatim** from the updated template:
   - `## Orchestrator Reference`
   - `## Agent File Integrity`
   - `## PR Approval Rule`
5. **Migrate a pre-split install (one-time, auto-split — only if the `Orchestrator_Guide.md — Overwrite` step above wrote successfully this run):** if the local `CLAUDE.md` still contains any of `## Agent Session Management`, `## Agent Completion Reports`, or `## Workflows` — this is an install from before ST-000043 — remove those sections (and only those three; `## Agent Roster` is never stripped, per step 3 above) from `CLAUDE.md` entirely and notify the user: _"Split the orchestrator-only sections out of CLAUDE.md into .claude/agents/Orchestrator_Guide.md (new file) — this reduces the fixed context cost every spawned subagent pays."_
6. New top-level sections in the template not present locally → append after the last existing section

#### Project_Priming.md — Skip

Never fetch or modify. This file is 100% project-specific.

#### context/Document_Index.md — Skip (append new sections only)

Never overwrite. This file is project-specific (document paths, API spec location, agent working file references). If the template adds a new `##` section not present locally → append it empty at the end of the file. The `Last Updated` field is maintained by agents during normal workflow execution, not by sync.

#### Memory files — Skip (append new sections only)

Never overwrite. If the template adds a new `##` section not present locally → append it empty at the end of the file.

#### Working-record files — Skip (append new sections only)

Same rule as memory files.

#### Wiki files — Merge (append new sections only)

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/wiki/*_template.md`  
**Target:** `docs/wiki/` in the target project

Wiki files are project-owned — never overwrite existing content. Apply this merge strategy:

1. Fetch the latest template version
2. Read the existing local wiki file
3. Identify any `##` section heading in the template that is **not present** in the local file
4. Append each missing section at the end of the local file with its heading and an `[UPDATE REQUIRED]` placeholder body, then notify the user
5. Sections already present in the local file → leave untouched

**If a wiki file does not exist locally:**
1. Ask the user once (covering all missing wiki files):
   > "Some wiki docs are missing (`docs/wiki/`). Do you have existing guidelines I can refer to — such as a Confluence page, a README section, or existing doc files?
   >
   > - Reply with **file path(s)** to any existing guideline documents
   > - Or reply `no` to write placeholder templates"
2. **If the user provides paths** → read those files and use them as reference to fill `{{PLACEHOLDER}}` markers in the templates before writing
3. **If the user replies `no`** → fetch and write the template with all `{{PLACEHOLDER}}` values replaced by `[UPDATE REQUIRED]` markers; notify the user to fill them in

**Expected wiki files:**
`Testing_Guidelines.md`, `Development_Standards.md`, `Code_Review_Checklist.md`, `{Language}_Style_Guide.md` (name varies by project)

> The language style guide file name is project-specific (e.g., `Go_Style_Guide.md`). Sync does not rename existing style guide files. If no style guide file exists, write `Language_Style_Guide.md` as the fallback.

### Cleanup — Remove Stale Files

After all updates are applied, scan each managed directory and flag any file not in the known expected set.

**Expected files — `rules/`:**
`Agent_Common_Bootstrap.md`, `Agent_Common_Read_On_Demand.md`, `Audit_Rules.md`, `Blocked_Request.md`, `Business_Analyst_Rules.md`, `CICD_Validation_Guide.md`, `Clean_Code_Rules.md`, `Developer_Rules.md`, `Logging_Standard.md`, `Product_Owner_Rules.md`, `QA_Rules.md`, `Retro_Rules.md`, `Story_Standard.md`, `Story_Standard_Dev.md`, `Story_Standard_PO.md`, `Story_Standard_QA.md`, `Story_Standard_TL.md`, `Technical_Lead_Rules.md`, `UI_UX_Designer_Rules.md`, `UI_Prototype_Rules.md`, `Strict_Mode_Story_Guide.md` (strict mode only)

**Expected files — `workflows/`:**
`Create_Stories_Workflow.md`, `Plan_Sprint_Workflow.md`, `Refine_Prototype_Workflow.md`, `Refine_Sprint_Workflow.md`, `Resume_Story_Workflow.md`, `Shared_Pipeline_Stages.md`, `Sprint_Workflow.md`, `Start_Story_Workflow.md`, `Sync_Devkit_Workflow.md`, `Workflow_Guide.md`

**Expected files — `scripts/`:**
`check_devkit_version.ps1`, `check_devkit_version.sh`

**Expected files — `.claude/skills/`** (sibling of `.claude/agents/`, not scanned as part of it — check separately):
`read-section/SKILL.md`

Directories never scanned for cleanup: `memory/`, `working-record/`, `docs/`, `tmp/`, `context/`, `internal/` — these are project-owned, runtime-output, or agent-managed and may contain custom or transient files. `internal/` specifically holds only this workflow's own audit report while a Stage 4 run is in flight (see Stage 4) and is always empty between runs.

If any unexpected files are found, report them to the user:

```
Stale files found:
  workflows/Update_Agents_Workflow.md

These files are not part of the devkit structure. Remove them? Reply yes to delete or no to keep.
```

- **yes** → delete the listed files and log each deletion
- **no** → leave them in place; note them in the completion report

If no unexpected files are found, skip this step silently.

**Missing expected files:** After checking for unexpected files, also check the reverse — any file in the expected set that is absent from the local directory. Report them to the user:

```
Missing expected files:
  rules/Blocked_Request.md

These files are part of the devkit structure but were not found locally. Restore them? Reply yes to fetch and write or no to skip.
```

- **yes** → fetch each missing file from the devkit source and write it using the appropriate merge strategy
- **no** → leave them absent; note them in the completion report

If no expected files are missing, skip this step silently.

---

## Stage 3 — Finalize

1. Update `**Devkit version:**` in `CLAUDE.md` to `LATEST_VERSION`
2. Write `LATEST_VERSION` to `.claude/agents/devkit_version.txt`
3. Report completion to the user:

```
Sync complete: v{CURRENT_VERSION} → v{LATEST_VERSION}

Updated:
  - <list each file written>

Skipped (project-owned):
  - Project_Priming.md
  - memory/        (6 files)
  - working-record/ (6 files)

[If any [UPDATE REQUIRED] placeholders were inserted]:
  Action needed: N instruction sections need project-specific content.
  Search for [UPDATE REQUIRED] in .claude/agents/instructions/ to find them.
```

---

## Stage 4 — Audit Pass (detect-only)

**Runs only if Stage 2 wrote at least one file in scope.** Scope = the files Stage 2's written-files log actually wrote in this run whose strategy is model-generated: `rules/*.md` (adapt to mode), `instructions/*.md` (merge), and `CLAUDE.md` (merge). Excluded, even if Stage 2 touched them this run: workflow files, script files, skill files, and `Orchestrator_Guide.md` (all verbatim overwrite — can't carry a mode-adaptation artifact, self-heals via the checksum pre-filter on the next sync), wiki files (project-owned, not devkit-authored content), and anything Stage 1 resolved but Stage 2 never actually wrote (checksum skip, failed fetch/write).

If the scope list is empty (nothing in those three categories was written this run — e.g. only workflow files changed, or the whole run was a no-op) → **skip this stage silently.** Print nothing, spawn nothing.

**1. Spawn one general-purpose subagent** (never a persistent role or session — fresh every run) with a fully self-contained prompt naming this project's own deployed `.claude/agents/rules/Audit_Rules.md` as the complete behavior spec:

```
Scan the following files, just written by this project's sync devkit run, for mode-adaptation drift and return a compact finding list only — never the raw file contents you read.

Step 1 — read the detection spec in full before scanning anything:
.claude/agents/rules/Audit_Rules.md

This file is the complete and only behavior spec for this scan: the single MA-n finding class, its four recognizable shapes, the <!-- audit:keep --> absolute exclusion, and what's explicitly out of scope. Do not invent detection criteria beyond what that file states — if something is ambiguous under the spec, do not report it as a finding.

Step 2 — scan only these files (do not read anything else in the project):
<scope list — the files this run actually wrote via rules/instructions/CLAUDE.md merge, from Stage 2's written-files log>

Step 3 — apply Audit_Rules.md's MA-n rules exactly, one finding class, report-only — you are not proposing an edit, only describing what you found and where.

Step 4 — return your findings as a single compact Markdown block:

<file>:<line-or-line-range> — <one-clause description of the drift and which shape it matches>
(or "_None found._" if empty)

Do not edit any file. Return the finding list as your final response; the orchestrator persists it if non-empty.
```

**2. If the subagent's return is `_None found._`** → this stage's work is done. Report nothing beyond the normal Stage 3 completion report — a clean audit pass produces no visible output.

**3. If the subagent returned one or more findings:**

a. Write them to `.claude/agents/internal/audit_report_YYYYMMDD_HHMMSS.md` (create `.claude/agents/internal/` if it does not exist):
   ```markdown
   # Sync Audit Report — YYYYMMDD_HHMMSS
   **Devkit Version:** {LATEST_VERSION}
   **Scanned:** <count> file(s) written this run

   <findings block, verbatim from the subagent>
   ```
b. Run `gh auth status` to check authentication:
   - **Authenticated:** file an Issue on the devkit repository:
     ```bash
     gh issue create --repo mycom08/mt-agent-devkit \
       --title "Sync Audit Finding — <project name> (YYYY-MM-DD)" \
       --label "audit:contribution" \
       --body-file .claude/agents/internal/audit_report_YYYYMMDD_HHMMSS.md
     ```
     Report the Issue URL to the user, then **delete the report file** — the Issue is now the record.
   - **Not authenticated or `gh` unavailable:** tell the user the report has been written to `.claude/agents/internal/audit_report_YYYYMMDD_HHMMSS.md` and instruct them to open an Issue labeled `audit:contribution` on `mycom08/mt-agent-devkit` with the report's contents. Leave the report file in place in this case — it is the only record until the user files it manually.

---

## Pipeline Rules

- **Never write before user confirms** in Stage 1 — unless `--auto` flag was passed
- **Never overwrite** `Project_Priming.md`, `context/Document_Index.md`, `memory/`, `working-record/`, or `docs/`
- **Fail safe on network error** — if any fetch fails, log it and skip that file; never write partial content
- **WebFetch fallback** — if WebFetch returns truncated or summarized content, retry with `curl -sf`; never write content that appears incomplete
- **Missing version in changes.json = full scan** — never silently skip an unknown version
- **Checksum skip is silent** — files skipped due to checksum match are listed in the update plan as "already up to date" but do not appear in the final written-files report
- **Log every file written** — the user must be able to see exactly what changed
- **Merge preserves project content** — when in doubt about whether a section is project-specific, keep the local version and notify the user
- **Report both unexpected and missing files** in cleanup — unexpected files may be stale; missing files may indicate a broken install
- **This file updates itself** — `Sync_Devkit_Workflow.md` is in the overwrite list; the new version takes effect after this run completes
- **Stage 4 is detect-only and silent when clean** — it never writes to `rules/`, `instructions/`, or `CLAUDE.md`; a scoped run that finds nothing produces no output at all, only a filed Issue (or an instruction to file one manually) when it finds something
- **Stage 4's scan subagent is spawned fresh every run** — never a persistent role or session, and it reads only the files this run actually wrote via a model-generated merge strategy, never the full `.claude/agents/` tree
