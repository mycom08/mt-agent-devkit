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

Generate customized versions of all agent scaffold files by reading the source templates from `.claude/agents/templates/` and adapting their content to the scanned project context. Replace all placeholder or example-specific content with content appropriate for the target project.

### Source template paths (in this devkit)

| Template file | Target path in generated project |
|---|---|
| `templates/CLAUDE_template.md` | `CLAUDE.md` (root) |
| `templates/context/Project_Priming_template.md` | `.claude/agents/context/Project_Priming.md` |
| `templates/context/Document_Index_template.md` | `.claude/agents/context/Document_Index.md` |
| `templates/instructions/*_instructions_template.md` (×5) | `.claude/agents/[role]_instructions.md` |
| `templates/rules/*_template.md` (×16) | `.claude/agents/rules/[name].md` |
| `templates/workflows/*_Workflow_template.md` (×8) | `.claude/agents/workflows/[name].md` |

> **Strip the `_template` suffix** when writing to the target project. The suffix is devkit-only — generated files use clean names.

### Files to generate

#### `CLAUDE.md`

**Source:** `templates/CLAUDE_template.md`

If `CLAUDE.md` exists at `TARGET_PROJECT` root → generate a **CLAUDE.md addition** (a block to append, not a full replacement).
If `CLAUDE.md` does not exist → generate a **full CLAUDE.md**.

Adapt the template:
- Replace `{{PROJECT_NAME}}` with the detected project name
- Replace `{{PROJECT_DESCRIPTION}}` with a 1–2 sentence description of the project's purpose and tech stack, derived from the Stage 1 scan
- Replace `{{MODE}}` with `strict` or `github` based on the user's Stage 0 choice
- Replace `{{DEVKIT_SOURCE_URL}}` with the value of `**Devkit source:**` read from this devkit's own `CLAUDE.md`
- Replace `{{DEVKIT_VERSION}}` with the content of `version.txt` at the devkit root
- All other content is copied verbatim from the template

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

#### Agent instruction files (5 files)

**Source:** `templates/instructions/[role]_instructions_template.md`
**Target:** `.claude/agents/[role]_instructions.md` (strip `_template` suffix; files go at the root of `.claude/agents/`, not in a subdirectory)

For each agent (`business_analyst`, `developer`, `product_owner`, `qa`, `technical_lead`):
- Copy the structure from the template
- Replace example-project-specific references with the target project's equivalent tools and conventions
- Keep all session management, memory, and working record rules verbatim
- Adapt pre-PR gates to the detected test/build tooling (e.g., `npm test`, `pytest`, `cargo test`, `./mvnw test`)

#### Rules files (16 files)

**Source:** `templates/rules/*_template.md`
**Target:** `.claude/agents/rules/[name].md` (strip `_template` suffix)

Copy all rules files. Replace example-project-specific tooling references:
- `Developer_Rules.md` — adapt §2 (pre-PR gate commands) to detected tooling
- `QA_Rules.md` — adapt §4 (testing rules) to detected test framework
- `Technical_Lead_Rules.md` — adapt §4 (design standards) to detected tech stack
- `Product_Owner_Rules.md` — copy verbatim (tool-agnostic)
- `Business_Analyst_Rules.md` — copy verbatim (tool-agnostic)
- `Story_Standard*.md` — copy all verbatim (tool-agnostic)
- All other rules files — copy verbatim

#### Workflow files (8 files)

**Source:** `templates/workflows/*_Workflow_template.md` + `templates/workflows/Workflow_Guide_template.md`
**Target:** `.claude/agents/workflows/[name].md` (strip `_template` suffix)

Copy all scrum team workflow files verbatim:
- `Create_Stories_Workflow.md`
- `Plan_Sprint_Workflow.md`
- `Refine_Sprint_Workflow.md`
- `Resume_Story_Workflow.md`
- `Shared_Pipeline_Stages.md`
- `Sprint_Workflow.md`
- `Start_Story_Workflow.md`
- `Sync_Devkit_Workflow.md`
- `Workflow_Guide.md`

> **Do not copy** `Analyst_Workflow.md` or `Init_Project_Workflow.md` — these are devkit-internal workflows and have no place in the target project.

#### Version check scripts (2 files)

**Source:** `templates/scripts/check_devkit_version.ps1`, `templates/scripts/check_devkit_version.sh`
**Target:** `.claude/agents/scripts/check_devkit_version.ps1`, `.claude/agents/scripts/check_devkit_version.sh`

Copy both scripts verbatim. These power the `SessionStart` hook that notifies users when a new devkit version is available.

---

#### Memory files (5 files)

Generate blank memory files:
```markdown
# {Agent} Memory

No facts recorded yet.
```

#### Working record files (5 files)

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

Write all generated files to `TARGET_PROJECT`:

1. Create directories as needed:
   `.claude/agents/context/`, `.claude/agents/memory/`,
   `.claude/agents/rules/`, `.claude/agents/working-record/`, `.claude/agents/workflows/`,
   `.claude/agents/scripts/`, `.claude/agents/retros/`, `.claude/agents/tmp/`
   Write a `.gitkeep` placeholder inside `.claude/agents/retros/` so the directory is tracked in git.
2. **If `Mode: strict`** — also create:
   `.claude/agents/docs/stories/`, `.claude/agents/docs/sprints/`, `.claude/agents/docs/reviews/`;
   write `.claude/agents/docs/story_counter.txt` containing `0`.
   Write `.claude/agents/devkit_version.txt` containing the current devkit version (read from `version.txt` at the devkit root).

   **If `Mode: github`** — also write `.claude/agents/devkit_version.txt` containing the current devkit version.
3. For `CLAUDE.md`:
   - If appending → add the generated block at the end of the existing file with a `---` separator
   - If creating → write the full file
4. Write each generated file to its target path (with clean name — no `_template` suffix).
5. Append the `.gitignore` additions (or create `.gitignore` if missing).
6. Inject the devkit update-check `SessionStart` hook into `.claude/settings.json` in the target project:
   - If `.claude/settings.json` already exists → read it and **merge** the `SessionStart` hook under `hooks` (do not remove existing hooks or keys)
   - If it does not exist → create it with only the hook block

   Detect the target OS from Stage 1 (`.ps1` files, Windows-style paths, PowerShell config → Windows; otherwise Unix):

   **Windows:**
   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "matcher": "startup",
           "hooks": [{ "type": "command", "command": "powershell -File .claude/agents/scripts/check_devkit_version.ps1", "timeout": 10 }]
         }
       ]
     }
   }
   ```

   **Mac / Linux:**
   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "matcher": "startup",
           "hooks": [{ "type": "command", "command": "bash .claude/agents/scripts/check_devkit_version.sh", "timeout": 10 }]
         }
       ]
     }
   }
   ```

   If OS cannot be determined, default to the Unix form.

7. Report to the user:
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
- **CLAUDE.md is additive** — never overwrite an existing CLAUDE.md in full; always append the orchestrator block
- **Strip `_template` suffix** — all files written to the target project use clean names without the suffix
- **Never copy devkit-internal files** — `Analyst_Workflow.md` and `Init_Project_Workflow.md` are devkit-only; never write them to the target project
- **State file cleanup** — always delete the state file after successful Stage 4 completion or user cancellation
