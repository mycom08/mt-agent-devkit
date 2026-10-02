# Sync Devkit Project Workflow

> **Note:** This file is for reference only in the devkit repo. The `sync devkit` command runs in a **project-orchestrator root folder** (injected by `build software`'s Stage 4 Path B), not in the devkit itself. This is the orchestrator-scoped counterpart to the regular-repo `Sync_Devkit_Workflow.md` — much smaller, since this folder owns a small orchestrator file set plus four scripts instead of a full Scrum-team scaffold.

Triggered by: `"sync devkit"` or `"sync devkit --auto"` in this project-orchestrator folder's `{{ROOT_FILE}}`

The `--auto` flag skips the Stage 1 user confirmation. The update plan is still printed but no reply is required before writing begins.

Fetches the latest orchestrator template files from the devkit GitHub repository and applies them to this folder, preserving all project-specific content.

---

## Prerequisites

Before starting, read from this folder's `{{ROOT_FILE}}`:
- `**Devkit source:**` — the devkit's GitHub repository URL (e.g. `https://github.com/mycom08/mt-agent-devkit`)
- `**Devkit version:**` — the version currently installed in this folder

If either field is missing or contains a placeholder URL, stop and notify the user that the devkit source is not configured.

**Older installs may still hold a raw base URL** of the form `https://raw.githubusercontent.com/{owner}/{repo}/main`. Read `{owner}` and `{repo}` out of whichever shape is present and carry on; the `{{ROOT_FILE}} — Merge` step in Stage 2 rewrites the field to the canonical repository form.

---

## Stage 0 — Resolve the Latest Release

1. Read `**Devkit version:**` from `{{ROOT_FILE}}` → `CURRENT_VERSION`
2. Resolve `{owner}` and `{repo}` from `**Devkit source:**`, then list the devkit's release tags:

   ```bash
   git ls-remote --tags --refs --sort=-v:refname https://github.com/{owner}/{repo}.git
   ```

   Keep only tags matching `^v[0-9]+\.[0-9]+\.[0-9]+$`, take the first, and strip the leading `v` → `LATEST_VERSION`.

   - **The tag filter is required.** `-v:refname` sorts a bare `v7`-style tag above `v7.0.0`, so an unfiltered first result can be a non-release tag.
   - **Never use the GitHub REST API for this.** Unauthenticated calls are capped at 60 requests/hour per IP; `git ls-remote` on a public repo needs no credentials and has no such cap.
   - If the command fails (network error, repo unreachable) or no tag matches the filter → stop and notify the user; do not modify any files.
3. Set the fetch base for every remote read in this workflow:

   `{DEVKIT_RAW_BASE}` = `https://raw.githubusercontent.com/{owner}/{repo}/v{LATEST_VERSION}`

   Pinning it to the tag means the resolved version and the file contents come from the same immutable commit. **Never fetch from `/main`** — `main` carries work that has not been released.
4. Compare versions:
   - If `CURRENT_VERSION == LATEST_VERSION` → notify the user: _"Agent files are already up to date (v{CURRENT_VERSION})."_ Stop.
   - If `CURRENT_VERSION != LATEST_VERSION` → notify the user: _"Update available: v{CURRENT_VERSION} → v{LATEST_VERSION}"_ and proceed to Stage 1

---

## Stage 1 — Resolve Changed Files

Fetch `{DEVKIT_RAW_BASE}/changes.json` to determine which of this folder's owned files and four scripts need updating. Use the same version-range resolution as the regular-repo workflow: collect every version between `CURRENT_VERSION` (exclusive) and `LATEST_VERSION` (inclusive), combine each version's `files`, `new`, and `modified` arrays (missing arrays are empty), deduplicate. A missing version key still means "trigger full scan," but here a full scan only ever concerns the owned files and four scripts — never fetch or reason about rules/instructions/memory/wiki files, none of which exist in this folder.

From the resolved file set, keep only the files relevant to this folder (ignore any entry for a regular-repo-only path like `templates/rules/*` or `templates/instructions/*` — those never apply here):

| File | Relevant `changes.json` path |
|---|---|
| `{{ROOT_FILE}}` | `.claude/agents/templates/Project_Root_template.md` |
| `{{AGENT_DIR_PREFIX}}/agents/context/Project_Priming.md` | `.claude/agents/templates/context/Project_Root_Priming_template.md` |
| `{{AGENT_DIR_PREFIX}}/agents/workflows/Build_Software_Project_Workflow.md` | `.claude/agents/templates/workflows/Build_Software_Project_Workflow_template.md` |
| `{{AGENT_DIR_PREFIX}}/agents/workflows/Sync_Devkit_Project_Workflow.md` (this file) | `.claude/agents/templates/workflows/Sync_Devkit_Project_Workflow_template.md` |
| `{{AGENT_DIR_PREFIX}}/agents/scripts/branch_preflight.py` | `.claude/agents/templates/scripts/branch_preflight.py` |
| `{{AGENT_DIR_PREFIX}}/agents/scripts/check_devkit_version.ps1` | `.claude/agents/templates/scripts/check_devkit_version.ps1` |
| `{{AGENT_DIR_PREFIX}}/agents/scripts/check_devkit_version.sh` | `.claude/agents/templates/scripts/check_devkit_version.sh` |
| `{{AGENT_DIR_PREFIX}}/agents/scripts/telemetry.py` | `.claude/agents/templates/scripts/telemetry.py` |

### Update plan

Report the update plan to the user before writing anything:

```
Update plan: v{CURRENT_VERSION} → v{LATEST_VERSION}

Files to update:
  - {{ROOT_FILE}} (merge)
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
curl -sf "{DEVKIT_RAW_BASE}/path/to/file"
```

If both WebFetch and curl fail for a file, log the failure and skip that file; do not write partial content.

### Merge strategy by file

#### `{{ROOT_FILE}}` — Merge

**Source:** `{DEVKIT_RAW_BASE}/.claude/agents/templates/Project_Root_template.md`

1. Fetch the latest template
2. Read the existing local `{{ROOT_FILE}}`
3. **Preserve** — never overwrite:
   - `**Mode:**`
   - `**Devkit source:**` — one exception: if the local value is a raw base URL (`https://raw.githubusercontent.com/{owner}/{repo}/<ref>`), rewrite it in place to `https://github.com/{owner}/{repo}`, keeping the same `{owner}`/`{repo}`. This is the canonical shape Stage 0 and the version-check scripts expect. Never substitute the template's own placeholder value.
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

**Source:** `{DEVKIT_RAW_BASE}/.claude/agents/templates/workflows/Build_Software_Project_Workflow_template.md`

Fetch and write verbatim (strip the `_template` suffix). No project-specific content lives here.

#### `workflows/Sync_Devkit_Project_Workflow.md` (this file) — Overwrite

**Source:** `{DEVKIT_RAW_BASE}/.claude/agents/templates/workflows/Sync_Devkit_Project_Workflow_template.md`

Fetch and write verbatim (strip the `_template` suffix). This file updates itself — the new version takes effect after this run completes.

#### Script files — Overwrite

**Source:** `{DEVKIT_RAW_BASE}/.claude/agents/templates/scripts/check_devkit_version.ps1`
          `{DEVKIT_RAW_BASE}/.claude/agents/templates/scripts/check_devkit_version.sh`
          `{DEVKIT_RAW_BASE}/.claude/agents/templates/scripts/telemetry.py`
          `{DEVKIT_RAW_BASE}/.claude/agents/templates/scripts/branch_preflight.py`
**Target:** `{{AGENT_DIR_PREFIX}}/agents/scripts/check_devkit_version.ps1`
          `{{AGENT_DIR_PREFIX}}/agents/scripts/check_devkit_version.sh`
          `{{AGENT_DIR_PREFIX}}/agents/scripts/telemetry.py`
          `{{AGENT_DIR_PREFIX}}/agents/scripts/branch_preflight.py`

Fetch and write verbatim. These are identical to the regular-repo versions — no orchestrator-specific behavior.

#### Settings hook — Inject if missing

Check `{{AGENT_DIR_PREFIX}}/settings.json` for the devkit update-check hook:
- If a `SessionStart` entry whose command references `check_devkit_version` already exists → skip
- If missing → inject it using the same OS-detection logic as `scaffold_mechanical.sh`'s settings.json step (merge into existing `settings.json`, or create it if absent)

---

### Legacy runtime-state migration

Run this compatibility check after scripts/rules are updated and before reporting readiness for new stories. Append missing ignore entries without replacing existing project patterns:

```gitignore
{{AGENT_DIR_PREFIX}}/agents/memory/
{{AGENT_DIR_PREFIX}}/agents/working-record/
{{AGENT_DIR_PREFIX}}/agents/retros/
{{AGENT_DIR_PREFIX}}/agents/tmp/
{{AGENT_DIR_PREFIX}}/agents/internal/
```

Strict mode's existing blanket `{{AGENT_DIR_PREFIX}}/agents/` ignore already covers these entries; do not untrack its scaffold automatically. In GitHub mode, inspect tracked runtime files with `git ls-files --` for the five directories above. Ignore patterns do not remove already tracked files.

If any runtime files are tracked, report their exact paths and mark migration pending. **--auto does not authorize** index removal, branch creation, committing, pushing, or changing story metadata. Obtain explicit authorization for a separate one-time maintenance migration, with its reviewed base and exact file allowlist. The maintenance migration is an explicit exception for legacy configuration, not automatic recovery from a BLOCKED story preflight. Stop on unrelated dirty files, unpushed commits, or an unsynchronized base; do not stash, reset, rebase, or delete files.

Before switching to that authorized maintenance branch, copy every reviewed runtime file to a user-selected local backup outside the checkout and record its content hash; never commit the backup. On the maintenance branch, remove only reviewed runtime paths from the index using `git rm --cached -- "<reviewed-runtime-file>"` (one exact path per invocation; no wildcard or recursive filesystem deletion). Commit the ignore additions and index removals as an ordinary migration change, review/merge it through the project's required gates, and synchronize the selected base normally. Switching/merging the old base can delete formerly tracked working files despite `--cached`; after base synchronization, restore missing runtime files from the backup and verify every original content hash. Keep the backup local until verification succeeds. Verify local memory files still exist, historical commits still retain their original contents, and runtime files are absent from `git ls-files` on the new base. Do not rewrite published history. Never commit runtime content merely to unblock preflight.

For every legacy ready/in-progress story missing **Base Branch**, ask the user/PO to confirm its intended existing base from the story/sprint decision; do not guess `main`, the current branch, or a default. PO records the confirmed `**Base Branch:**` once in the GitHub issue (strict mode: local story). Treat it as immutable thereafter; record unresolved stories as migration pending. In-progress stories keep their approved branch/SHA and do not create a replacement branch. A project-orchestrator root applies this check only to its own files; each roster repository performs its own migration and story decisions.

After the reviewed migration lands, rerun installed `branch_preflight.py inspect` for the confirmed base before new story creation. A PASS must identify a clean synchronized base and no tracked runtime state. If it remains BLOCKED, report the exact reason and take no automatic recovery action. Include pending migrations or missing Base Branch decisions in the completion report; updated templates alone do not prove story readiness.

---

## Stage 3 — Finalize

1. Update `**Devkit version:**` in `{{ROOT_FILE}}` to `LATEST_VERSION`
2. Write `LATEST_VERSION` to `{{AGENT_DIR_PREFIX}}/agents/devkit_version.txt`
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

- **Every remote read is pinned to the release tag** — `{DEVKIT_RAW_BASE}` resolved in Stage 0, never `/main`. A fetch from `main` would deliver unreleased content under a released version number
- **Never write before user confirms** in Stage 1 — unless `--auto` flag was passed
- **Never overwrite** `context/Project_Priming.md` — 100% project-owned
- **Only the owned orchestrator files and four scripts are in scope** — `{{ROOT_FILE}}`, `context/Project_Priming.md` (skip), `workflows/Build_Software_Project_Workflow.md`, plus this workflow file itself and the four script files listed in Stage 1. Ignore any `changes.json` entry for a regular-repo-only path (rules/instructions/memory/working-record/wiki) — those never apply to this folder.
- **Fail safe on network error** — if any fetch fails, log it and skip that file; never write partial content
- **WebFetch fallback** — if WebFetch returns truncated or summarized content, retry with `curl -sf`; never write content that appears incomplete
- **Missing version in changes.json = full scan** — scoped to the owned files and four scripts above only, never the regular-repo file set
- **Log every file written** — the user must be able to see exactly what changed
- **This file updates itself** — `Sync_Devkit_Project_Workflow.md` is in the overwrite list; the new version takes effect after this run completes
