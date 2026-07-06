# Sync Devkit Project Workflow

> **Note:** This file is for reference only in the devkit repo. The `sync devkit` command runs in a **project-orchestrator root folder** (injected by `build software`'s Stage 4 Path B), not in the devkit itself. This is the orchestrator-scoped counterpart to the regular-repo `Sync_Devkit_Workflow.md` — much smaller, since this folder owns only 3 devkit-templated files instead of a full Scrum-team scaffold.

Triggered by: `"sync devkit"` or `"sync devkit --auto"` in this project-orchestrator folder's `CLAUDE.md`

The `--auto` flag skips the Stage 1 user confirmation. The update plan is still printed but no reply is required before writing begins.

Fetches the latest orchestrator template files from the devkit GitHub repository and applies them to this folder, preserving all project-specific content.

---

## Prerequisites

Before starting, read from this folder's `CLAUDE.md`:
- `**Devkit source:**` — the raw GitHub base URL (e.g. `https://raw.githubusercontent.com/mycom08/mt-agent-devkit/main`)
- `**Devkit version:**` — the version currently installed in this folder

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

Fetch `{DEVKIT_SOURCE_URL}/changes.json` to determine which of this folder's 3 owned files need updating. Use the same version-range resolution as the regular-repo workflow: collect every version between `CURRENT_VERSION` (exclusive) and `LATEST_VERSION` (inclusive), gather each version's listed files, deduplicate. A missing version key still means "trigger full scan," but here a full scan only ever concerns the 3 files this folder owns — never fetch or reason about rules/instructions/memory/wiki files, none of which exist in this folder.

From the resolved file set, keep only the files relevant to this folder (ignore any entry for a regular-repo-only path like `templates/rules/*` or `templates/instructions/*` — those never apply here):

| File | Relevant `changes.json` path |
|---|---|
| `CLAUDE.md` | `.claude/agents/templates/Project_CLAUDE_template.md` |
| `.claude/agents/context/Project_Priming.md` | `.claude/agents/templates/context/Project_Orchestrator_Priming_template.md` |
| `.claude/agents/workflows/Build_Software_Project_Workflow.md` | `.claude/agents/templates/workflows/Build_Software_Project_Workflow_template.md` |
| `.claude/agents/workflows/Sync_Devkit_Project_Workflow.md` (this file) | `.claude/agents/templates/workflows/Sync_Devkit_Project_Workflow_template.md` |

### Update plan

Report the update plan to the user before writing anything:

```
Update plan: v{CURRENT_VERSION} → v{LATEST_VERSION}

Files to update:
  - CLAUDE.md (merge)
  - workflows/Build_Software_Project_Workflow.md (overwrite)

Skipped (project-owned):
  - context/Project_Priming.md
```

Then ask: **"Proceed with update? Reply yes to apply or no to cancel."**

- **yes** → proceed to Stage 2
- **no** → stop; no files written

**If `--auto` flag was passed**, skip the confirmation and proceed to Stage 2 immediately after printing the update plan.

---

## Stage 2 — Apply Updates

Apply only the files resolved in Stage 1. Log each file as it is written. If any file fails, log the error and continue — do not abort the entire update.

### Fetch strategy

Use WebFetch to retrieve remote files. If a fetched file appears truncated or summarized, fall back to Bash curl:

```bash
curl -sf "{DEVKIT_SOURCE_URL}/path/to/file"
```

If both WebFetch and curl fail for a file, log the failure and skip that file; do not write partial content.

### Merge strategy by file

#### `CLAUDE.md` — Merge

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/Project_CLAUDE_template.md`

1. Fetch the latest template
2. Read the existing local `CLAUDE.md`
3. **Preserve** — never overwrite:
   - `**Mode:**`
   - `**Devkit source:**`
   - `**Devkit version:**` (updated in Stage 3)
   - `## Repo Roster` content (the actual repo table — project-specific)
4. **Replace verbatim** from the updated template:
   - `## Overview`
   - `## Workflows` routing table (preserve the `Repo Roster` link, if any)
   - `## Build Software Workflow`
   - `## Sync Devkit Workflow`
   - `## Workflow Help`
   - `## Agent File Integrity`
5. New top-level sections in the template not present locally → append after the last existing section

#### `context/Project_Priming.md` — Skip

Never fetch or modify. This file is 100% project-specific (product overview, repo table, orchestrator role written once at scaffold time) — same rule as the regular per-repo `Project_Priming.md`.

#### `workflows/Build_Software_Project_Workflow.md` — Overwrite

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/workflows/Build_Software_Project_Workflow_template.md`

Fetch and write verbatim (strip the `_template` suffix). No project-specific content lives here.

#### `workflows/Sync_Devkit_Project_Workflow.md` (this file) — Overwrite

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/workflows/Sync_Devkit_Project_Workflow_template.md`

Fetch and write verbatim (strip the `_template` suffix). This file updates itself — the new version takes effect after this run completes.

#### Script files — Overwrite

**Source:** `{DEVKIT_SOURCE_URL}/.claude/agents/templates/scripts/check_devkit_version.ps1`
          `{DEVKIT_SOURCE_URL}/.claude/agents/templates/scripts/check_devkit_version.sh`
**Target:** `.claude/agents/scripts/check_devkit_version.ps1`
          `.claude/agents/scripts/check_devkit_version.sh`

Fetch and write verbatim. These are identical to the regular-repo versions — no orchestrator-specific behavior.

#### Settings hook — Inject if missing

Check `.claude/settings.json` for the devkit update-check hook:
- If a `SessionStart` entry whose command references `check_devkit_version` already exists → skip
- If missing → inject it using the same OS-detection logic as `scaffold_mechanical.sh`'s settings.json step (merge into existing `settings.json`, or create it if absent)

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
  - context/Project_Priming.md
```

---

## Pipeline Rules

- **Never write before user confirms** in Stage 1 — unless `--auto` flag was passed
- **Never overwrite** `context/Project_Priming.md` — 100% project-owned
- **Only 3 files are ever in scope** — `CLAUDE.md`, `context/Project_Priming.md` (skip), `workflows/Build_Software_Project_Workflow.md`, plus this workflow file itself. Ignore any `changes.json` entry for a regular-repo-only path (rules/instructions/memory/working-record/wiki) — those never apply to this folder.
- **Fail safe on network error** — if any fetch fails, log it and skip that file; never write partial content
- **WebFetch fallback** — if WebFetch returns truncated or summarized content, retry with `curl -sf`; never write content that appears incomplete
- **Missing version in changes.json = full scan** — scoped to the 3 files above only, never the regular-repo file set
- **Log every file written** — the user must be able to see exactly what changed
- **This file updates itself** — `Sync_Devkit_Project_Workflow.md` is in the overwrite list; the new version takes effect after this run completes
