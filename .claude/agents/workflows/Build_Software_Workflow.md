# Build Software Workflow

Triggered by: `"build software <idea>"` in CLAUDE.md

The text after the trigger keyword is the user's **idea**. If no text is provided, the orchestrator asks the user for a one-line description before starting.

**Output folders:**
- `/result/analyst/` — all Analyst pipeline outputs (unchanged)
- `/result/build/` — all Phase 1 build-specific artifacts

> **Stages 4–5** (per-repo initialisation and doc copy) are appended to this file below Stage 3.

---

## Pipeline State

The orchestrator maintains `.claude/agents/tmp/build_software_state.md` to support resumption after unexpected termination.

**On pipeline start — always check this file first:**
- If the file **exists** → read it and resume from the stage **after** the recorded `Stage` value
- If the file **does not exist** → start fresh from Stage 1

**State file format:**

```markdown
# Build Software Pipeline State
**Story:** ST-000002
**Stage:** <1 | 2 | 3 | 4 | 5>
**Idea:** <the user's idea text>
**Repo Count:** <number of repos or 0 if not yet determined>
**Confirmed:** <false | stage1 | stage2>
**GitHub Project URL:** <url or empty>
**Sessions:**
- tl_session: <agentId or empty>
- po_session: <agentId or empty>
- ba_session: <agentId or empty>
**Updated:** YYYY-MM-DDTHH:MM
```

**Write rules:**
- Create at Stage 1 entry (if it does not exist)
- Update `Stage` to the **last completed stage** + `Updated` after each stage transition
- Update `Sessions` when agents are spawned
- Update `Repo Count` after Stage 2 produces `repo_structure.md`
- Update `Confirmed` after each user confirmation gate: `false` → `stage1` → `stage2`

**Resume rules (per stage):**
- **Stage 1 — resumed:** Re-run Stage 1 from scratch. The `analyze` workflow manages its own state file (`analyst_workflow_state.md`) and will resume internally if that file exists. After Stage 1 completes, re-confirm with user before Stage 2.
- **Stage 2 — resumed:** Check if `/result/build/repo_structure.md` already exists. If it does, skip Stage 2 execution and present the existing file to the user for re-confirmation before Stage 3. If it does not exist, run Stage 2 normally.
- **Stage 3 — resumed:** Check if per-repo split files already exist under `/result/build/<repo-name>/`. If all expected repo folders exist (count from state file `Repo Count`), skip Stage 3. If any are missing, re-run Stage 3 for missing repos only.
- **Stage 4 — resumed:** Check which repos already have a `git init`-initialized folder **and** contain `.claude/agents/docs/build_state.md`. Skip those repos; continue scaffolding only the remaining ones. If the GitHub Project already exists (URL in state file), skip `gh project create` and reuse the stored URL.
- **Stage 5 — resumed:** Check which repos already have `.claude/agents/docs/analysis/` populated (non-empty directory). Skip those; copy docs only to repos where the folder is absent or empty.

---

## Stage 1 — Analysis (Analyst Workflow)

**Purpose:** Fully delegate to the existing `analyze` workflow to produce all analyst documents in `/result/analyst/`.

### Entry

1. Check for state file `.claude/agents/tmp/build_software_state.md`:
   - If it **does not exist** → create it now with `Stage: 0`, `Idea: <user's idea>`, `Confirmed: false`, `Repo Count: 0`, all sessions empty
   - If it **exists** and `Stage` is `1` or higher → apply resume rules above before continuing

2. If the state file shows `Stage: 0` (or was just created) → proceed to run Stage 1 from scratch

### Execution

3. Invoke the `analyze` workflow by reading `.claude/agents/workflows/Analyst_Workflow.md` and executing the full pipeline with the user's idea as the requirement context. All `/result/analyst/` documents are produced exactly as defined in that workflow — no modification.

   > Do not modify or shorten the Analyst_Workflow pipeline. All documents (`summary.md`, `architecture.md`, `implementation_roadmap.md`, `business_requirements.md`, `testing_plan.md`, `spec.md`, `elicitation_notes.md`, `diagrams/`) must be produced.

4. After the Analyst pipeline completes, update state file: `Stage: 1`, `Updated: <now>`.

### Confirmation Gate

5. Present to the user:

   ```
   Stage 1 complete — Analysis done.

   All analysis documents are available in /result/analyst/.
   Start with summary.md for an overview.

   Ready to proceed to Stage 2 (Repo Structure Planning)?
   Type "yes" to continue or "no" to stop here.
   ```

6. If user says **"no"** → stop and inform the user they can resume by running `build software` again (the state file will resume from Stage 2 on next run).

7. If user says **"yes"** → update state file: `Confirmed: stage1`, `Updated: <now>`, then proceed to Stage 2.

---

## Stage 2 — Repo Planning (Orchestrator-direct)

**Purpose:** Read `architecture.md` from Stage 1 and decide on the repository structure. This is orchestrator-executed logic — no agent is spawned.

> **Design note (binding TL decision 2026-06-17):** Stage 2 is orchestrator-direct. The devkit's own TL agent is not spawned — its instructions assume sprint story context and would produce unreliable behavior outside that context. The orchestrator reads `architecture.md` directly and writes `repo_structure.md` inline.

### Execution

1. Read `/result/analyst/architecture.md` in full.

2. Based on the architecture content, decide:
   - **Decision:** `monolith` or `multi-repo`
   - **Rationale:** 2–4 sentences explaining the decision based on the architecture (coupling, team structure, deployment requirements, etc.)
   - **Repo Table:** For each repo (or the single monolith):
     - `name` — short, lowercase, hyphenated slug (e.g., `api-service`, `web-app`)
     - `purpose` — one sentence
     - `tech stack` — comma-separated key technologies
     - `local path` — relative path where the user will clone/create this repo (e.g., `./api-service`)

3. Write `/result/build/repo_structure.md` using the format below:

```markdown
# Repository Structure

**Decision:** monolith | multi-repo
**Rationale:** <2–4 sentences>

## Repos

| Name | Purpose | Tech Stack | Local Path |
|------|---------|------------|------------|
| <name> | <purpose> | <tech stack> | <local path> |
```

4. Update state file: `Stage: 2`, `Repo Count: <N>`, `Updated: <now>`.

### Confirmation Gate

5. Read `/result/build/repo_structure.md` and present it to the user verbatim, followed by:

   ```
   Stage 2 complete — Repository structure planned.

   Review the repo structure above. Does this look correct?
   Type "yes" to continue to Stage 3 (Doc Splitting) or "no" to stop here.
   You can also ask me to adjust the structure before continuing.
   ```

6. If the user requests adjustments → update `repo_structure.md` accordingly and re-present.

7. If user says **"no"** (without adjustment request) → stop and inform the user they can resume by running `build software` again.

8. If user says **"yes"** → update state file: `Confirmed: stage2`, `Updated: <now>`, then proceed to Stage 3.

---

## Stage 3 — Doc Splitting (Parallel general-purpose agents)

**Purpose:** Split `implementation_roadmap.md` and `architecture.md` into per-repo files. Full summary docs are marked for copy to all repos.

> **Design note (binding TL decision 2026-06-17):** Stage 3 spawns anonymous general-purpose agents with inline instructions — not the devkit's own TL or PO agents. Their instructions assume sprint story context. Parallel spawn pattern matches `analyze` workflow Stage 2a.

### Preparation

1. Read `/result/build/repo_structure.md` to get the list of repos (names and purposes).
2. Read `/result/analyst/implementation_roadmap.md` and `/result/analyst/architecture.md` in full.
3. Create the output folder structure: `/result/build/<repo-name>/` for each repo.

### Agent Spawns (parallel — send in a single orchestrator message)

Spawn **two general-purpose agents** (**model: sonnet**) in the same message:

---

#### Agent A — Roadmap Splitter

Inline prompt:

```
You are a document splitter. Your task is to produce per-repo filtered versions of the implementation roadmap.

Source file: /result/analyst/implementation_roadmap.md
Repo list: <paste repo table from repo_structure.md here — name, purpose, tech stack>

For EACH repo:
1. Read the full implementation_roadmap.md.
2. Extract all phases, sprints, and stories that are relevant to this repo based on:
   - The repo's tech stack (include stories whose implementation involves these technologies)
   - The repo's purpose (include stories whose scope touches this repo's domain)
   - Explicit repo name mentions in the roadmap (if any)
3. Write the filtered result to: /result/build/<repo-name>/implementation_roadmap_<repo-name>.md

Filtering rules:
- Keep the original document structure (headings, tables, dependency graph, release criteria, risks, glossary)
- Remove stories, sprints, and sections that have no relevance to this repo
- If a story spans multiple repos, include it in ALL relevant repos' filtered docs — do not split a story
- If a section (e.g., Risks, Release Criteria) applies across repos, include a copy in all repos' docs
- Preserve all Mermaid diagram blocks that include this repo's stories; remove blocks with no relevant nodes
- If fewer than 20% of the original content is relevant, note at the top: "> Note: Most roadmap content belongs to other repos. Only directly relevant items are shown."

After writing all files, report: "Roadmap split complete — <N> files written: <list of output paths>"
```

---

#### Agent B — Architecture Splitter

Inline prompt:

```
You are a document splitter. Your task is to produce per-repo filtered versions of the architecture document.

Source file: /result/analyst/architecture.md
Repo list: <paste repo table from repo_structure.md here — name, purpose, tech stack>

For EACH repo:
1. Read the full architecture.md.
2. Extract all sections relevant to this repo based on:
   - The repo's tech stack (include sections whose implementation involves these technologies)
   - The repo's purpose (include sections covering this repo's domain or components)
   - Explicit component or service names that belong to this repo
3. Write the filtered result to: /result/build/<repo-name>/architecture_<repo-name>.md

Filtering rules:
- Keep the original document structure (headings, decision sections, component diagrams)
- Include all cross-cutting sections (error handling strategy, security model, data handling) in ALL repos' docs
- For Mermaid diagrams: include diagrams that show this repo's components; add a note "Full system diagram available in /result/analyst/architecture.md" if omitting the full diagram
- For PlantUML references: include the reference link if the diagram involves this repo; omit otherwise
- If fewer than 20% of the original content is relevant, note at the top: "> Note: Most architecture content belongs to other repos. Only directly relevant excerpts are shown."

After writing all files, report: "Architecture split complete — <N> files written: <list of output paths>"
```

---

### Full-copy docs (orchestrator action — after agents complete)

After both agents complete, the orchestrator copies the following files from `/result/analyst/` to **each** repo's folder under `/result/build/<repo-name>/`:

| Source | Destination |
|--------|-------------|
| `/result/analyst/architecture.md` | `/result/build/<repo-name>/architecture.md` |
| `/result/analyst/summary.md` | `/result/build/<repo-name>/summary.md` |
| `/result/analyst/testing_plan.md` | `/result/build/<repo-name>/testing_plan.md` |
| `/result/analyst/business_requirements.md` | `/result/build/<repo-name>/business_requirements.md` |

> Both a full copy and a filtered version of `architecture.md` exist per repo. The full copy (`/result/build/<repo-name>/architecture.md`) is placed here for completeness and is the authoritative reference. The filtered version (`/result/build/<repo-name>/architecture_<repo-name>.md`), produced by Agent B, is an additional quick-reference artifact scoped to that repo's components — it does not replace the full copy.

### Completion

4. Update state file: `Stage: 3`, `Updated: <now>`.

5. Present to the user:

   ```
   Stage 3 complete — Documents split per repo.

   Per-repo folders created under /result/build/:

   <list each repo and its output files>

   The following docs were copied to all repos unchanged:
   - architecture.md
   - summary.md
   - testing_plan.md
   - business_requirements.md

   Proceeding to Stage 4 (Repo Scaffolding)...
   ```

---

## Stage 4 — Repo Scaffolding

**Purpose:** Create local project folders, initialise git repos, create GitHub repos, scaffold agent files inline (equivalent to `init project` GitHub-mode steps), create a GitHub Project, and link all repos to it.

> **Design note:** Stage 4 executes the GitHub-mode scaffold steps from `Init_Project_Workflow.md` directly — it does **not** call `init project` as a trigger and does **not** add any new flag to `init project`. Read `Init_Project_Workflow.md` Stages 1–4 (GitHub mode) and apply those steps inline for each repo path.

### Entry

1. Verify the state file shows `Confirmed: stage2`. If not, stop and report an unexpected state to the user.
2. Update state file: `Stage: 4`, `Updated: <now>`.
3. Read `/result/build/repo_structure.md` to determine: `monolith` or `multi-repo`, repo names, and local paths.

### Path A — Monolith

1. **Local folder:** If the user provided a path in Stage 3 (or state file), use it. If no path is available, ask the user: **"Where should I create the project folder? Provide an absolute path."** Wait for the answer before continuing.

2. Create the local project folder at the user-specified path (if it does not already exist).

3. Run `git init` inside the folder.

4. Run `gh repo create` for the project repo (use the product name from the user's idea as the repo name; prompt the user for visibility — public or private — if not previously specified).

5. Read `Init_Project_Workflow.md` and execute its **GitHub-mode scaffold steps** (Stages 1–4) inline for this repo path:
   - Stage 1: scan the repo folder (it is brand-new, so use the product name and description derived from the user's idea and `/result/analyst/summary.md`)
   - Stage 2: generate all agent scaffold files adapted to the product (CLAUDE.md, Project_Priming.md, Document_Index.md, 5 instruction files, rules files, workflow files, version check scripts, blank memory files, blank working records)
   - Stage 3: skip the user-confirmation sub-step — you already have user consent from the overall Stage 4 flow
   - Stage 4 equivalent: write all generated files to the repo folder; create required directories; append `.gitignore` additions (github mode); inject `SessionStart` hook into `.claude/settings.json`

6. Run `gh project create` to create a GitHub Project named after the product (from the user's idea). Store the returned project URL.

7. Link the repo to the project: `gh project item-add <project-number> --owner <owner> --url <repo-url>`

8. Write `.claude/agents/docs/build_state.md` inside the repo:

   ```markdown
   # Build State
   **Product:** <product name from user's idea>
   **Repo Role:** monolith
   **GitHub Project URL:** <project-url>
   **Phase:** scaffold
   **Analysis Docs:** .claude/agents/docs/analysis/
   ```

9. Update state file: `GitHub Project URL: <url>`, `Updated: <now>`.

10. Proceed to Stage 5.

---

### Path B — Multi-Repo

1. **Local paths:** Read each repo's `local path` from `/result/build/repo_structure.md`. For any repo whose `local path` is missing or set to a placeholder, ask the user: **"Provide an absolute local path for repo `<repo-name>`."** Collect all missing paths before continuing.

2. For **each sub-repo** (in order; not parallel — each scaffold step is sequential):

   a. Create the repo sub-folder at the resolved `local path` (if it does not already exist).

   b. Run `git init` inside the sub-folder.

   c. Run `gh repo create` for the sub-repo (use `<repo-name>` as the repo slug; same visibility as chosen for other repos).

   d. Read `Init_Project_Workflow.md` and execute its **GitHub-mode scaffold steps** (Stages 1–4) inline for this repo path:
      - Stage 1: scan the repo folder using the repo's `purpose` and `tech stack` from `repo_structure.md`
      - Stage 2: generate all agent scaffold files adapted to this repo's purpose and tech stack
      - Stage 3: skip the user-confirmation sub-step
      - Stage 4 equivalent: write all generated files; create directories; append `.gitignore` additions; inject `SessionStart` hook

   e. Write `.claude/agents/docs/build_state.md` inside the sub-repo:

      ```markdown
      # Build State
      **Product:** <product name from user's idea>
      **Repo Role:** <repo-name from repo_structure.md>
      **GitHub Project URL:** <project-url — fill after project creation>
      **Phase:** scaffold
      **Analysis Docs:** .claude/agents/docs/analysis/
      ```

   f. Update state file: `Updated: <now>` (repo count is already set from Stage 2).

3. **Project orchestrator folder:**

   a. Ask the user for the project orchestrator folder path if not already known: **"Where should I create the project orchestrator folder? Provide an absolute path."**

   b. Create the folder (if it does not already exist).

   c. Run `git init` inside the project folder.

   d. Run `gh repo create` for the project folder repo.

4. Run `gh project create` to create a GitHub Project named after the product. Store the returned project URL.

5. Link **all repos** (each sub-repo + the project folder repo) to the GitHub Project:
   ```
   gh project item-add <project-number> --owner <owner> --url <sub-repo-url>
   ```
   Repeat for each repo.

6. Go back and fill in `GitHub Project URL` in every sub-repo's `.claude/agents/docs/build_state.md` that was written with an empty placeholder in step 2e.

7. Read `.claude/agents/templates/Project_CLAUDE_template.md` and write it to the project orchestrator folder as `CLAUDE.md`, substituting:
   - `{{PROJECT_NAME}}` → product name from user's idea
   - `{{MODE}}` → `github`
   - `{{REPOS}}` → a Markdown table listing each sub-repo: name, purpose, absolute local path, GitHub repo URL

8. Read `.claude/agents/templates/workflows/Build_Software_Project_Workflow_template.md` and write it to the project orchestrator folder as `.claude/agents/workflows/Build_Software_Project_Workflow.md` (strip the `_template` suffix).

9. Write `.claude/agents/docs/build_state.md` inside the project orchestrator folder:

   ```markdown
   # Build State
   **Product:** <product name from user's idea>
   **Repo Role:** project-orchestrator
   **GitHub Project URL:** <project-url>
   **Phase:** scaffold
   **Repos:** <comma-separated list of sub-repo names>
   **Analysis Docs:** .claude/agents/docs/analysis/
   ```

10. Update state file: `GitHub Project URL: <url>`, `Updated: <now>`.

11. Proceed to Stage 5.

---

## Stage 5 — Doc Copy + Handoff

**Purpose:** Distribute analysis documents into each repo and print the handoff message to the user.

### Entry

1. Update state file: `Stage: 5`, `Updated: <now>`.
2. Read `/result/build/repo_structure.md` to get the list of repos (monolith = one repo; multi-repo = each sub-repo, excluding the project orchestrator folder).

### Doc Copy (for each repo)

For each repo in the list:

1. Create `.claude/agents/docs/analysis/` inside the repo (if it does not already exist).

2. Copy the following **full summary docs** from `/result/analyst/` into `.claude/agents/docs/analysis/` inside the repo:

   | Source | Destination |
   |--------|-------------|
   | `/result/analyst/summary.md` | `<repo-path>/.claude/agents/docs/analysis/summary.md` |
   | `/result/analyst/architecture.md` | `<repo-path>/.claude/agents/docs/analysis/architecture.md` |
   | `/result/analyst/testing_plan.md` | `<repo-path>/.claude/agents/docs/analysis/testing_plan.md` |
   | `/result/analyst/business_requirements.md` | `<repo-path>/.claude/agents/docs/analysis/business_requirements.md` |

3. Copy the **per-repo split files** from `/result/build/<repo-name>/` into `.claude/agents/docs/analysis/` inside the repo:

   | Source | Destination |
   |--------|-------------|
   | `/result/build/<repo-name>/implementation_roadmap_<repo-name>.md` | `<repo-path>/.claude/agents/docs/analysis/implementation_roadmap_<repo-name>.md` |
   | `/result/build/<repo-name>/architecture_<repo-name>.md` | `<repo-path>/.claude/agents/docs/analysis/architecture_<repo-name>.md` |

   > For a monolith, `<repo-name>` is the single repo's name slug as recorded in `repo_structure.md`.

### State File Cleanup

After all doc copies complete successfully, delete `.claude/agents/tmp/build_software_state.md`.

### Handoff Message

Print the following to the user:

```
Phase 1 complete — repos scaffolded and analysis docs distributed.

Project folder: <project-orchestrator-path>     (multi-repo only)
                <repo-path>                      (monolith: the single repo path)
GitHub Project: <github-project-url>

Next step:
```

**For monolith:**
```
- Open a Claude Code session in <repo-path> and run: plan next sprint
```

**For multi-repo:**
```
- Open a Claude Code session in <project-orchestrator-path> and run: build software
```

---

## Pipeline Rules

- **State file first** — always check `.claude/agents/tmp/build_software_state.md` before doing any work; never skip the resume check
- **Same trigger, auto-resume** — `build software` (with or without an idea) activates resume if the state file exists; no separate resume command
- **Confirmation gates are mandatory** — never proceed from Stage 1 to 2 or Stage 2 to 3 without an explicit "yes" from the user
- **Adjustment loop** — if the user requests changes to `repo_structure.md` at the Stage 2 gate, apply and re-present before asking for confirmation again
- **Orchestrator-direct for Stage 2** — no agent spawn; orchestrator writes `repo_structure.md` inline
- **Parallel Stage 3 spawns** — Agent A and Agent B are spawned in a single orchestrator message; never sequentially
- **Stage 4 is sequential** — scaffold each repo one at a time; do not spawn parallel agents for repo scaffolding
- **Full-copy docs are never filtered** — `architecture.md`, `summary.md`, `testing_plan.md`, and `business_requirements.md` go to all repos verbatim
- **Stop on blocker** — if any agent reports a blocking issue, stop and report to the user before continuing
- **Completion reports** — each spawned agent returns its results to the orchestrator; orchestrator relays a brief status to the user after each stage
- **State file deleted on Stage 5 success** — if Stage 5 fails mid-copy, the state file remains for resume; only delete after all copies complete
