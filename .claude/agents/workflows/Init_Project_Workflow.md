# Init Project Workflow

Triggered by: `"init project"` or `"init project [path]"` in CLAUDE.md

Scaffolds all Claude Code agent files in a target project. Scans the project's tech stack and structure, generates customized agent files, asks the user for permission, then writes everything in place.

All template source files live under `.claude/agents/templates/` in this devkit.

---

## Pipeline State

The orchestrator maintains `.claude/agents/tmp/init_project_state.md` to support resumption.

**On pipeline start — always check this file first:**
- If the file **exists** → read it and resume from the recorded stage
- If the file **does not exist** → start fresh from Stage 0

**State file format:**
```markdown
# Init Project Workflow State
**Target:** <absolute path to target project>
**Stage:** <0 | 1 | 2 | 3 | 4>
**Mode:** <strict | github>
**Overwrite:** <yes | no | ask>
**Updated:** YYYY-MM-DDTHH:MM
```

**Write rules:** Create at Stage 0 entry. Update `Stage` + `Updated` after each transition. Delete after Stage 4 completes.

---

## Stage 0 — Project Path Resolution

1. If the user included a path in the trigger command, use it directly as `TARGET_PROJECT`.
2. If no path was provided, ask the user: **"What is the path to your target project?"** Wait for the answer.
3. Normalize the path (resolve `~`, relative paths, etc.) and verify the directory exists.
   - If the directory does not exist → stop and notify the user before continuing.
4. **Ask the user about mode:**
   > "Do you want **strict mode** for this project?
   >
   > **Strict mode** — no GitHub, MCP, or CI required. Stories and all agent docs are stored locally under `.claude/agents/` (gitignored). Branches and commits use your project's external story IDs if available. No pushes to remote — you control merges.
   >
   > **GitHub mode** (default) — full GitHub Issues, PRs, and Actions integration.
   >
   > Reply `strict` or `github` (default: github)."

   Store the answer as `Mode: strict` or `Mode: github` in the state file.
5. Write the state file with `Stage: 0`, the resolved `TARGET_PROJECT` path, and the selected mode.
6. Proceed to Stage 1.

---

## Stage 1 — Project Scan

Read the target project to understand its context. Look for:

| What to find | Where to look |
|---|---|
| Project name and purpose | README, package.json `name`/`description`, go.mod module name, pom.xml `artifactId`, Cargo.toml `name` |
| Language(s) | File extensions across `src/`, root, or similar; go.mod, package.json, requirements.txt, Cargo.toml, pom.xml, build.gradle |
| Framework(s) | Dependencies in manifest files; import patterns in source files |
| Key directories | Top-level folder names (src, internal, api, docs, tests, cmd, lib, etc.) |
| Existing agent files | Check if `.claude/agents/` already exists in `TARGET_PROJECT` |
| Existing CLAUDE.md | Check if `CLAUDE.md` exists at `TARGET_PROJECT` root |
| CI/CD setup | `.github/workflows/`, `Makefile`, `Dockerfile`, `docker-compose.yml` |
| Test tooling | Test framework imports/config files (jest.config, pytest.ini, go test, etc.) |
| API style | OpenAPI/Swagger files, GraphQL schemas, gRPC .proto files |
| Issue tracker / project management | `.github/` presence (implies GitHub Issues); Jira config if present |

**Existing agent files handling:**
- If `.claude/agents/` already exists in the target project → warn the user: list which files already exist and ask: **"Agent files already exist in this project. Overwrite all / Skip existing / Cancel?"**
  - `Overwrite all` → continue with full generation
  - `Skip existing` → generate only files that are missing
  - `Cancel` → stop and delete the state file
- If `.claude/agents/` does not exist → proceed normally

Summarize findings to the user in 5 bullets max before proceeding to Stage 2.

---

## Stage 2 — Content Generation

Scaffold files split into two tiers (see full detail below):
- **Mechanical tier** — 8/16 rules files, all 9 workflow files, scripts, blank memory/working-record files, `.gitignore`, `VERSION`, `CHANGELOG.md`, `devkit_version.txt`, `settings.json` hook. Zero project-specific judgment; written by `working/scripts/scaffold_mechanical.sh` in one call, not by reading+regenerating each template through an agent. `VERSION`/`CHANGELOG.md` are a universal devkit convention (any language) — see `.claude/agents/working/skeletons/shared/Version_Release_Conventions.md`.
- **Adaptive tier** — `CLAUDE.md`, `README.md`, `Project_Priming.md`, `Document_Index.md`, 6 instruction files, 9/17 rules files, 4 wiki docs. Genuinely needs the scanned project context; generate these by reading the source templates from `.claude/agents/templates/` and adapting their content. Replace all placeholder or example-specific content with content appropriate for the target project.

### Source template paths (in this devkit)

| Template file | Target path in generated project | Tier |
|---|---|---|
| `templates/{mode}/CLAUDE_template.md` (shared content from `templates/shared/CLAUDE_Shared_template.md`) | `CLAUDE.md` (root) | Adaptive |
| `templates/README_template.md` | `README.md` (root) | Adaptive |
| `templates/context/Project_Priming_template.md` | `.claude/agents/context/Project_Priming.md` | Adaptive |
| `templates/context/Document_Index_template.md` | `.claude/agents/context/Document_Index.md` | Adaptive |
| `templates/instructions/*_instructions_template.md` (×6) | `.claude/agents/[role]_instructions.md` | Adaptive |
| `templates/rules/*_template.md` (×17) | `.claude/agents/rules/[name].md` | 8 Mechanical, 9 Adaptive — see the Rules files section below for exactly which |
| `templates/{mode}/workflows/*_template.md` (×7 split) + `templates/workflows/*_Workflow_template.md` (×2 non-split) | `.claude/agents/workflows/[name].md` | Mechanical (all 9) |

Where `{mode}` is `github` or `strict` based on the user's Stage 0 choice.

**Split candidates (read from `templates/{mode}/workflows/`):**
- `Sprint_Workflow_template.md`
- `Shared_Pipeline_Stages_template.md`
- `Start_Story_Workflow_template.md`
- `Resume_Story_Workflow_template.md`
- `Create_Stories_Workflow_template.md`
- `Plan_Sprint_Workflow_template.md`
- `Refine_Sprint_Workflow_template.md`

**Non-split (read from `templates/workflows/`):**
- `Sync_Devkit_Workflow_template.md`
- `Workflow_Guide_template.md`
- `Build_Software_Project_Workflow_template.md` (not deployed to target projects)

**CLAUDE.md generation:** Read `templates/shared/CLAUDE_Shared_template.md` for the full content. The mode-specific file at `templates/{mode}/CLAUDE_template.md` contains only a reference comment — use the shared file's `<!-- SHARED-START -->` / `<!-- SHARED-END -->` block as the actual template content.

> **Strip the `_template` suffix** when writing to the target project. The suffix is devkit-only — generated files use clean names.

### Files to generate

#### `CLAUDE.md`

**Source:** `templates/{mode}/CLAUDE_template.md` ← must match the Stage 2 source table entry above; run `grep -n "CLAUDE_template" Init_Project_Workflow.md` when updating to catch all occurrences

If `CLAUDE.md` exists at `TARGET_PROJECT` root → generate a **CLAUDE.md addition** (a block to append, not a full replacement).
If `CLAUDE.md` does not exist → generate a **full CLAUDE.md**.

Adapt the template:
- Replace `{{PROJECT_NAME}}` with the detected project name
- Replace `{{PROJECT_DESCRIPTION}}` with a 1–2 sentence description of the project's purpose and tech stack, derived from the Stage 1 scan
- Replace `{{MODE}}` with `strict` or `github` based on the user's Stage 0 choice
- Replace `{{DEVKIT_SOURCE_URL}}` with the value of `**Devkit source:**` read from this devkit's own `CLAUDE.md`
- Replace `{{DEVKIT_VERSION}}` with the content of `version.txt` at the devkit root
- All other content is copied verbatim from the template

#### `README.md`

**Source:** `templates/README_template.md`

If `README.md` exists at `TARGET_PROJECT` root → do not overwrite it. Instead append an `## AI Scrum Team` section (with a `---` separator) pointing to `CLAUDE.md`, `.claude/agents/context/Project_Priming.md`, and the `workflow help` command — same append-not-replace handling as `CLAUDE.md`.
If `README.md` does not exist → generate a full README from the template.

Adapt the template:
- Replace `{{PROJECT_NAME}}` with the detected project name
- Replace `{{PROJECT_DESCRIPTION}}` with the same 1–2 sentence description used for `CLAUDE.md`
- Replace `{{TECH_STACK}}` with a short bulleted or comma-separated list of the detected/decided languages, frameworks, and key dependencies (from Stage 1 scan, or from `architecture.md` if this is a brand-new repo scaffolded under Build Software with no code to scan yet)
- Replace `{{KEY_DIRECTORIES}}` with a short list of the project's top-level directories and their purpose (from Stage 1 scan; for a brand-new repo, use the directories the Java Skeleton Generation step created, or a generic placeholder noting the structure isn't established yet)
- Replace `{{GETTING_STARTED}}` with real build/run/test commands if determinable (e.g., `./mvnw spring-boot:run`, `npm install && npm start`) — if no code exists yet, say so plainly rather than inventing commands
- **If a `Dockerfile` and/or `docker-compose.yml` exist at the repo root** (written by Build Software's Java Skeleton Generation, or already present in an existing project being scanned), `{{GETTING_STARTED}}` must lead with the exact `docker compose up --build` (or plain `docker build`/`docker run` if there's a Dockerfile but no compose file) command, a short table of required environment variables (name, purpose, dev default — read the `${ENV_VAR:default}` placeholders out of the actual config file, e.g. `application.properties`), and the port(s) the service listens on. If there's a start script (`start.sh`/`start.ps1`) instead, cover that command in the same place.
- Replace `{{DEVKIT_SOURCE_URL}}` with the value of `**Devkit source:**` read from this devkit's own `CLAUDE.md`
- Replace `{{MODE}}` with `strict` or `github` based on the user's Stage 0 choice

#### `.claude/agents/context/Document_Index.md`

**Source:** `templates/context/Document_Index_template.md`

Adapt to the target project:
- Replace `{{PROJECT_NAME}}` with the detected project name
- Replace `{{DATE}}` with today's date
- Update the API Specification row with the actual spec path or repo reference (if found during Stage 1 scan)
- Update any document paths that differ from the generic defaults (e.g., if the project uses `src/docs/` instead of `docs/`)
- If `Mode: strict` — add the strict-mode agent working files to the Agent Working Files table:

| What | Path |
|---|---|
| Stories | `.claude/agents/docs/stories/ST-XXXXXX.md` |
| Review Records | `.claude/agents/docs/reviews/ST-XXXXXX_review.md` |
| Story Counter | `.claude/agents/docs/story_counter.txt` |

---

#### `.claude/agents/context/Project_Priming.md`

**Source:** `templates/context/Project_Priming_template.md`

Adapt to the target project:
- §1 Project Overview: project name, language, framework, purpose, key architectural patterns, database if applicable, auth mechanism if applicable
- §2 Glossary: define terms specific to the target project's domain (keep PO, TL, Dev, QA, BA)
- §3 Story Workflow: status flow and label conventions
- §4–§5: copy verbatim (applies to any project)
- §6 Internal Project Documents: adapt document paths to fit the target project's `docs/` structure; if unknown, use generic placeholders
- §7 Key Directories: list the actual directories found in Stage 1
- §8 Tech Stack: list the detected language, framework, and key dependency versions
- §9–§12: adapt to detected API style (REST/GraphQL/gRPC); use generic patterns if no API detected
- §13–§15: include Docker setup if detected; leave as placeholder otherwise

#### Agent instruction files (6 files)

**Source:** `templates/instructions/[role]_instructions_template.md`
**Target:** `.claude/agents/[role]_instructions.md` (strip `_template` suffix; files go at the root of `.claude/agents/`, not in a subdirectory)

For each agent (`business_analyst`, `developer`, `product_owner`, `qa`, `technical_lead`, `ui_ux_designer`):
- Copy the structure from the template
- Replace example-project-specific references with the target project's equivalent tools and conventions
- Keep all session management, memory, and working record rules verbatim
- Adapt pre-PR gates to the detected test/build tooling (e.g., `npm test`, `pytest`, `cargo test`, `./mvnw test`)

#### Mechanical tier — run `scaffold_mechanical.sh` first, before any agent writes a single file

**Source:** `working/scripts/scaffold_mechanical.sh`
**Usage:** `bash working/scripts/scaffold_mechanical.sh <devkit_root> <target_project> <mode:strict|github> [github-org/repo-name]`

This one script call writes every file (or file family) that needs **zero project-specific judgment** — it was built and content-diffed against real, previously agent-generated scaffolds until every file matched byte-for-byte (the few residual diffs found were agent *drift bugs* — literal template dates silently rewritten to "today," a stray backtick moved — not legitimate adaptations; the script is the more faithful copy). Do not re-derive this list by re-reading the templates and eyeballing them for `{placeholder}` tokens — some files need real adaptation via plain prose with no bracketed token at all (see the Adaptive tier note below), which a token scan alone will miss. If you're ever unsure whether a "verbatim" file actually needs a specific line's content adapted, diff the script's output against a known-good previously-generated repo for that same file, not just against the template.

It creates all required directories (`context/`, `memory/`, `rules/`, `working-record/`, `workflows/`, `docs/wiki/`, `scripts/`, `retros/` (no `.gitkeep` — gitignored, see below), `tmp/`, and `docs/stories|sprints|reviews/` + `story_counter.txt` for strict mode) and writes:
- **8 of 17 rules files verbatim** (`{github-org}/{repo-name}` substituted, nothing else): `Agent_Common`, `Blocked_Request`, `CICD_Validation_Guide`, `Clean_Code_Rules`, `Product_Owner_Rules`, `Retro_Rules`, `Story_Standard_TL`, `Strict_Mode_Story_Guide`
- **All 9 workflow files** — the 7 split ones (shared block + mode-specific appendix, correctly omitting the appendix separator entirely when the mode file is pure internal-notes comments with no real content — most of them are) and the 2 non-split ones, verbatim, no substitution (workflow files intentionally leave `{github-org}/{repo-name}` and other `{{PLACEHOLDER}}` tokens as literal runtime-resolved text — devkit convention, never fill these in at scaffold time)
- Both version-check scripts, `devkit_version.txt`, 6 blank memory files, 6 blank working-record files, `.gitignore` additions (github mode also ignores `working-record/*_Working_Record.md` and `retros/` — ephemeral/human-review-only, never committed), and `.claude/settings.json`'s `SessionStart` hook (only when `settings.json` doesn't already exist — if it does, merging into arbitrary existing JSON needs a real parser, do that step separately, same as before)
- `VERSION` (`0.0.1-SNAPSHOT`) and `CHANGELOG.md` (single-next-version-heading format) at the target project root — a universal devkit convention, any language, written only if not already present (idempotent — a Java skeleton generation pass that ran earlier in `Build_Software_Workflow.md` never creates these itself anymore, so this is always the actual creator). See `.claude/agents/working/skeletons/shared/Version_Release_Conventions.md` for the format.

If `github-org/repo-name` is omitted, `{github-org}`/`{repo-name}` tokens in the 8 verbatim rules files are left as literal placeholders — fill them in with a follow-up run once the GitHub repo exists, or leave them (harmless, same convention as workflow files).

> **Not yet ported to PowerShell.** Only `scaffold_mechanical.sh` exists today; run it via Bash (Claude Code's Bash tool provides Git Bash on Windows — this is what every `build software` / `init project` run to date has used). A `.ps1` mirror is a reasonable follow-up but wasn't built yet, to avoid re-deriving the same validated logic twice without the same empirical diff-against-ground-truth loop.

#### Adaptive tier — everything the mechanical script does NOT cover

Everything below needs real judgment and should go through an agent (a much smaller one now — it's no longer also carrying ~35 mechanical files). Read the target repo's already-known context (`architecture.md` / `architecture_<repo>.md`, `repo_structure.md`, Stage 1 scan results) and write:

- `CLAUDE.md`, `README.md`, `Project_Priming.md`, `Document_Index.md`
- 5 agent instruction files — adapt pre-PR gates to detected tooling (e.g., `npm test`, `pytest`, `cargo test`, `./mvnw test`)
- **9 of 17 rules files need real adaptation**, not just token substitution — confirmed by diffing real generated repos, not by scanning for `{}` tokens (several of these have zero bracketed placeholders and still needed rewriting):
  - `Developer_Rules.md` — adapt §2 (pre-PR gate commands) to detected tooling
  - `QA_Rules.md` — adapt §4 (testing rules) to detected test framework
  - `Technical_Lead_Rules.md` — adapt §4 (design standards) to detected tech stack
  - `UI_UX_Designer_Rules.md` — adapt §5 (pre-PR gate) `{prototype-start-command}` / `{mock-backend-start-command}` to the detected or decided frontend stack and mock-backend tooling
  - `Business_Analyst_Rules.md` — despite reading as tool-agnostic, references a `{feature-label}`/test-command convention that needs a real decision (e.g., "this repo uses sprint labels, not per-feature labels")
  - `Story_Standard.md` (base) — references `{start-server-command}` and other tooling-specific AC/DoD language
  - `Story_Standard_Dev.md`, `Story_Standard_PO.md`, `Story_Standard_QA.md` — all three reference a hardcoded generic API-spec location (`docs/api/`) in plain prose with no `{}` marker; real scaffolds need this rewritten to the project's actual contract location (e.g., a sibling `-api-spec` repo, or wherever the spec actually lives) and to the actual migration/build tooling in use
- 4 wiki docs (`Testing_Guidelines.md`, `Development_Standards.md`, `Code_Review_Checklist.md`, `{Language}_Style_Guide.md`) — fill every `{{PLACEHOLDER}}` from reference material (if provided) and the Stage 1 scan / architecture docs

> **Do not copy** `Analyst_Workflow.md` or `Init_Project_Workflow.md` — these are devkit-internal workflows and have no place in the target project.

#### Wiki documentation files (4 files)

**Source:** `templates/wiki/*_template.md`  
**Target:** `docs/wiki/` in the target project

Wiki files are project-owned — always check before generating.

**Step 1 — Check which files are missing**

Scan `docs/wiki/` in the target project. For each of the four expected files:

| Template | Target file |
|---|---|
| `Testing_Guidelines_template.md` | `docs/wiki/Testing_Guidelines.md` |
| `Development_Standards_template.md` | `docs/wiki/Development_Standards.md` |
| `Code_Review_Checklist_template.md` | `docs/wiki/Code_Review_Checklist.md` |
| `Language_Style_Guide_template.md` | `docs/wiki/{Language}_Style_Guide.md` |

If a file **already exists** → **skip it**. Only proceed for files that are missing.

If **all four files exist** → skip this section entirely.

**Step 2 — Ask the user about existing guidelines**

If one or more files are missing, ask:

> "I'll generate the missing wiki docs (`docs/wiki/`). Do you have any existing guidelines for this project I can refer to — such as a Confluence page, a README section, or existing docs files?
>
> - Reply with the **file path(s)** to any existing guideline documents (e.g., `docs/old-standards.md`)
> - Or reply `no` to generate from the project scan alone"

Wait for the user's reply before proceeding.

**Step 3 — Collect reference material (if provided)**

If the user provided file paths → read each file and use its content as reference material when filling placeholders. The reference files set the baseline for conventions; the project scan fills in anything not covered.

If the user replied `no` → use only the Stage 1 project scan as the source.

**Step 4 — Generate missing files**

For each missing wiki file, fill every `{{PLACEHOLDER}}` in the template using the reference material (if any) and the Stage 1 scan:

| Placeholder guidance | |
|---|---|
| `Testing_Guidelines.md` | Test framework, test run commands, directory structure, coverage thresholds, automation suite — from reference docs and detected test tooling/CI config |
| `Development_Standards.md` | Branch naming, commit format, lint/format commands, file structure, error handling patterns, logging — from reference docs and detected language/tooling |
| `Code_Review_Checklist.md` | Code quality, security, and conventions checklists; TL review criteria — adapted from reference docs and detected tech stack |
| `{Language}_Style_Guide.md` | Naming, error handling, concurrency, design patterns — from reference docs and detected language idioms. File named after detected language (e.g., `Go_Style_Guide.md`); falls back to `Language_Style_Guide.md` if undetermined |

**Placeholder fill rules:**
- Replace every `{{PLACEHOLDER}}` with real, specific content — no empty sections, no unfilled markers
- Use actual commands, paths, and conventions from reference material and the project scan
- If a detail cannot be determined from either source, use the most common convention for the detected language/framework and add a `<!-- verify: ... -->` comment for the user
- `{{DATE}}` → today's date in `YYYY-MM-DD` format
- `{{PROJECT_NAME}}` → detected project name
- `{{LANGUAGE}}` → detected primary language (e.g., `Go`, `TypeScript`, `Python`)

#### Version check scripts (2 files)

**Source:** `templates/scripts/check_devkit_version.ps1`, `templates/scripts/check_devkit_version.sh`
**Target:** `.claude/agents/scripts/check_devkit_version.ps1`, `.claude/agents/scripts/check_devkit_version.sh`

Copy both scripts verbatim. These power the `SessionStart` hook that notifies users when a new devkit version is available.

---

#### Memory files (6 files)

Generate blank memory files:
```markdown
# {Agent} Memory

No facts recorded yet.
```

#### Working record files (6 files)

Generate blank working record files:
```markdown
# {Agent} Working Record

## {Today's Date}
**Completed:** —
**In Progress:** —
**Impediments:** —
```

#### `.gitignore` additions

**If `Mode: github`:**
```
# Claude Code agent temp files
.claude/agents/tmp/

# Workflow output documents
/result/
```

**If `Mode: strict`:**
```
# Claude Code agent files — all agent infrastructure and docs are local-only
.claude/agents/

# Workflow output documents
/result/
```

---

## Stage 3 — User Confirmation

Present a summary of what will be written:

1. List every file that will be **created** and every file that will be **overwritten** (if applicable).
2. For `CLAUDE.md`: specify whether it will be **appended to** or **created new**.
3. State the total file count.

Then ask: **"May I write these files to `[TARGET_PROJECT]`? Reply yes to proceed or no to cancel."**

- **yes** → proceed to Stage 4
- **no** → stop; display a note that no files were written; delete the state file

Do not proceed to Stage 4 until the user explicitly confirms.

---

## Stage 4 — Write Files

1. **Run the mechanical tier first, in one call:**
   ```
   bash .claude/agents/working/scripts/scaffold_mechanical.sh <devkit_root> <TARGET_PROJECT> <mode> [github-org/repo-name]
   ```
   This handles directory creation (including the strict-mode `docs/stories|sprints|reviews/` + `story_counter.txt`), the 8 verbatim rules files, all 9 workflow files, both version-check scripts, `devkit_version.txt`, blank memory/working-record files, `.gitignore` additions, and `.claude/settings.json`'s `SessionStart` hook (OS auto-detected from the environment the script runs in — always correct in practice, since `TARGET_PROJECT` is a local path on the same machine). Check its final line — `settings.json: already exists — SessionStart hook NOT merged, do this separately` means step 3 below is still needed.

2. Write the adaptive-tier files generated in Stage 2 to their target paths (with clean names — no `_template` suffix): `CLAUDE.md`, `README.md`, `Project_Priming.md`, `Document_Index.md`, 6 instruction files, the 9 adaptive rules files, 4 wiki docs.
   - For `CLAUDE.md` and `README.md`, each independently: if appending → add the generated block at the end of the existing file with a `---` separator; if creating → write the full file.

3. **Only if the mechanical script reported `settings.json` already existed:** read the existing `.claude/settings.json` and merge the `SessionStart` hook under `hooks` (do not remove existing hooks or keys) — use the same Windows/Mac-Linux hook JSON the script would have written (see the script source for both forms).

4. Report to the user:
   - Files written (count and list)
   - Mode selected (`strict` or `github`)
   - Any files skipped (if "Skip existing" was chosen in Stage 1)
   - Any write errors

Delete the state file after successful completion.

---

## Stage 5 — Post-Init Instructions

**If `Mode: github`** — display:

```
Setup complete.

Next steps:

1. Edit .claude/agents/context/Project_Priming.md
   Fill in any [PLACEHOLDER] sections with your project's actual details.

2. Review CLAUDE.md
   Confirm the agent instruction file paths are correct for your project layout.

3. Configure permissions in .claude/settings.json
   Add the shell commands your agents will need (e.g., npm, pytest, cargo, docker).
   See .claude/settings.local.json in mt-agent-devkit for an example.

4. Open Claude Code in your project and type:
   workflow help
   to see all available commands.

5. To sync future devkit improvements into this project, type:
   sync devkit
```

**If `Mode: strict`** — display:

```
Setup complete (strict mode — no GitHub/MCP required).

Next steps:

1. Edit .claude/agents/context/Project_Priming.md
   Fill in any [PLACEHOLDER] sections with your project's actual details.

2. Review CLAUDE.md and confirm: Mode: strict

3. Configure permissions in .claude/settings.json
   Add the shell commands your agents will need (e.g., npm, pytest, cargo, docker).
   No gh CLI permissions needed.
   See .claude/settings.local.json in mt-agent-devkit for an example.

4. Note: all agent files live under .claude/agents/ and are gitignored.
   Stories are stored at .claude/agents/docs/stories/ — never committed to git.

5. Open Claude Code in your project and type:
   workflow help
   to see all available commands.

6. To sync future devkit improvements into this project, type:
   sync devkit
```

---

## Pipeline Rules

- **One confirmation required** — the orchestrator must not write any files before the user explicitly says yes in Stage 3
- **Overwrite transparency** — always list existing files that will be overwritten before asking for confirmation
- **No assumptions about tech stack** — if the scan is inconclusive, use generic placeholders and note what needs manual completion
- **Stop on path error** — if `TARGET_PROJECT` does not exist or is not accessible, stop immediately and report
- **CLAUDE.md and README.md are additive** — never overwrite an existing file of either in full; always append the orchestrator block
- **Strip `_template` suffix** — all files written to the target project use clean names without the suffix
- **Never copy devkit-internal files** — `Analyst_Workflow.md` and `Init_Project_Workflow.md` are devkit-only; never write them to the target project
- **State file cleanup** — always delete the state file after successful Stage 4 completion or user cancellation
- **Mechanical tier never goes through an agent** — run `scaffold_mechanical.sh` for the 8 verbatim rules files, all 9 workflow files, scripts, blank memory/working-record files, `.gitignore`, `devkit_version.txt`, and the `settings.json` hook. Routing these through an LLM agent only adds cost and risks silent drift (confirmed in practice: agents rewrote literal template dates to "today's date" and reworded prose that should have been byte-identical) with zero benefit — the content is fixed and known before Stage 4 starts.
- **The rules-file mechanical/adaptive boundary is not just a `{placeholder}` token scan** — several adaptive-tier rules files (`Business_Analyst_Rules.md`, `Story_Standard.md`, `Story_Standard_Dev/PO/QA.md`) need real content changes expressed as plain prose with no bracketed token at all (e.g. a hardcoded `docs/api/` spec path that needs correcting per-project). Don't move a file into the mechanical tier without diffing its scripted output against a known-good previously-generated repo, not just grepping the template for `{}`.
