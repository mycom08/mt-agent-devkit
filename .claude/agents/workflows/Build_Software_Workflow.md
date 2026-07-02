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

3. Invoke the `analyze` workflow by reading `.claude/agents/workflows/Analyst_Workflow.md` and executing the full pipeline with the user's idea as the requirement context, **including its Stage 2d Review & Feedback Gate** — do not skip or shortcut Stage 2d just because it's being run under Build Software. All `/result/analyst/` documents are produced exactly as defined in that workflow — no modification.

   > Do not modify or shorten the Analyst_Workflow pipeline. All documents (`summary.md`, `architecture.md`, `implementation_roadmap.md`, `business_requirements.md`, `testing_plan.md`, `spec.md`, `elicitation_notes.md`, `diagrams/`) must be produced.

4. After the Analyst pipeline (including Stage 2d) completes, update state file: `Stage: 1`, `Updated: <now>`, and copy `tl_session` / `po_session` / `ba_session` from `analyst_workflow_state.md` (or from the orchestrator's own record of which agents it spawned/resumed during the delegated run, if that file is already gone) into **this** state file's `Sessions` block. This is what keeps those sessions resumable for any later feedback round — `analyst_workflow_state.md` itself is deleted once Stage 2d closes, per the Analyst workflow's own rules.

### Confirmation Gate

5. Present to the user:

   ```
   Stage 1 complete — Analysis done.

   All analysis documents are available in /result/analyst/.
   Start with summary.md for an overview.

   If you have any further feedback, share it now — otherwise just say so and I'll continue to Stage 2 (Repo Structure Planning).
   ```

6. **If the user gives feedback** → route it to the relevant agent (TL for `architecture.md`/`testing_plan.md`, PO for `implementation_roadmap.md`, BA for `business_requirements.md`/`spec.md`) via the sessions saved in this state file (resume; spawn fresh only if expired), apply the change, re-present, and ask again. No loop limit — same pattern as `Analyst_Workflow.md` Stage 2d.

7. If user says to **stop** without giving feedback → stop and inform the user they can resume by running `build software` again (the state file will resume at this same gate on next run).

8. If the user **confirms no further feedback** → update state file: `Confirmed: stage1`, `Updated: <now>`, then proceed to Stage 2.

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

   > **Java REST service ⇒ API spec companion repo (fixed devkit convention, not optional).** For every repo whose tech stack is a Java REST service, add a second repo entry `<repo-name>-api-spec` (purpose: "OpenAPI/Swagger contract for `<repo-name>`", tech stack: "Java, OpenAPI Generator", local path a sibling of the service's own path) **immediately before** that service's row in the table — Stage 4 scaffolds repos in table order, and the service's skeleton depends on the api-spec repo already existing. This applies even when the overall `Decision` is `monolith`: a Java REST service and its contract are always two repos, regardless of how the rest of the system is structured. See `.claude/agents/templates/skeletons/Java_Skeleton_Conventions.md` for why.

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
- Keep the original document structure (headings, tables, dependency graph section, release criteria, risks, glossary)
- Remove stories, sprints, and sections that have no relevance to this repo
- If a story spans multiple repos, include it in ALL relevant repos' filtered docs — do not split a story
- If a section (e.g., Risks, Release Criteria) applies across repos, include a copy in all repos' docs
- The dependency graph is a linked file (`diagrams/dependency_graph.mmd`), not inline — keep the link and caption as-is; do not attempt to split or filter the diagram file itself (the orchestrator copies the whole `diagrams/` folder to every repo separately, see Full-copy docs below)
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
- Keep the original document structure (headings, decision sections, diagram links)
- Include all cross-cutting sections (error handling strategy, security model, data handling) in ALL repos' docs
- All diagrams are linked files under `diagrams/` (Mermaid `.mmd` or PlantUML `.puml`), never inline — keep the link and caption for any diagram relevant to this repo's components; drop the link (not the file) for diagrams with no relevant nodes, and add a note "Full diagram available in /result/analyst/diagrams/" when omitting one. Do not edit diagram file contents — the orchestrator copies the whole `diagrams/` folder to every repo separately (see Full-copy docs below), so every repo always has access to every diagram file regardless of which links you keep.
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
| `/result/analyst/diagrams/` (entire folder) | `/result/build/<repo-name>/diagrams/` |

> Both a full copy and a filtered version of `architecture.md` exist per repo. The full copy (`/result/build/<repo-name>/architecture.md`) is placed here for completeness and is the authoritative reference. The filtered version (`/result/build/<repo-name>/architecture_<repo-name>.md`), produced by Agent B, is an additional quick-reference artifact scoped to that repo's components — it does not replace the full copy.
>
> The entire `diagrams/` folder is copied whole to every repo — never filtered — so every diagram link kept by Agent A/B (or found in the full-copy docs) always resolves.

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
2. Read `/result/build/repo_structure.md` to determine repo names and local paths.
3. **Route by actual row count in the Repos table, not by the `Decision` label** — use Path A only if the table has exactly one row. A `Decision: monolith` architecture that includes a Java REST service has **two** rows (the service + its `-api-spec` companion, per Stage 2's fixed convention) and must use Path B even though `Decision` still reads `monolith`; the `Decision` field describes the overall system's coupling, not literally "one repo".

### Path A — Monolith

1. **Local folder:** If the user provided a path in Stage 3 (or state file), use it. If no path is available, ask the user: **"Where should I create the project folder? Provide an absolute path."** Wait for the answer before continuing.

2. Create the local project folder at the user-specified path (if it does not already exist).

3. Run `git init` inside the folder.

4. Run `gh repo create` for the project repo (use the product name from the user's idea as the repo name; prompt the user for visibility — public or private — if not previously specified).

5. **Java skeleton generation (conditional — see "Java Skeleton Generation" below for full rules):** if the repo's tech stack (from `/result/analyst/architecture.md`) is Java-based **and** the folder has no `pom.xml`/`build.gradle`/`build.gradle.kts` and no `src/` directory, spawn a general-purpose agent to generate a real, buildable skeleton before the devkit scaffold step below. Skip entirely for non-Java repos or repos that already have code.

6. Read `Init_Project_Workflow.md` and execute its **GitHub-mode scaffold steps** (Stages 1–4) inline for this repo path:
   - Stage 1: scan the repo folder (it is brand-new, so use the product name and description derived from the user's idea and `/result/analyst/summary.md`)
   - Stage 2: generate all agent scaffold files adapted to the product (CLAUDE.md, Project_Priming.md, Document_Index.md, 5 instruction files, rules files, workflow files, version check scripts, blank memory files, blank working records)
   - Stage 3: skip the user-confirmation sub-step — you already have user consent from the overall Stage 4 flow
   - Stage 4 equivalent: write all generated files to the repo folder; create required directories; append `.gitignore` additions (github mode); inject `SessionStart` hook into `.claude/settings.json`

7. Run `gh project create` to create a GitHub Project named after the product (from the user's idea). Store the returned project URL.

8. Link the repo to the project: `gh project item-add <project-number> --owner <owner> --url <repo-url>`

9. Write `.claude/agents/docs/build_state.md` inside the repo:

   ```markdown
   # Build State
   **Product:** <product name from user's idea>
   **Repo Role:** monolith
   **GitHub Project URL:** <project-url>
   **Phase:** scaffold
   **Analysis Docs:** .claude/agents/docs/analysis/
   ```

10. Update state file: `Stage: 4`, `GitHub Project URL: <url>`, `Updated: <now>`.

11. Proceed to Stage 5.

---

### Path B — Multi-Repo

1. **Local paths:** Read each repo's `local path` from `/result/build/repo_structure.md`. For any repo whose `local path` is missing or set to a placeholder, ask the user: **"Provide an absolute local path for repo `<repo-name>`."** Collect all missing paths before continuing.

2. For **each sub-repo** (in order; not parallel — each scaffold step is sequential):

   a. Create the repo sub-folder at the resolved `local path` (if it does not already exist).

   b. Run `git init` inside the sub-folder.

   c. Run `gh repo create` for the sub-repo (use `<repo-name>` as the repo slug; same visibility as chosen for other repos).

   d. **Java skeleton generation (conditional — see "Java Skeleton Generation" below for full rules):** if this sub-repo's tech stack (from `repo_structure.md` / `architecture_<repo-name>.md`) is Java-based **and** the folder has no `pom.xml`/`build.gradle`/`build.gradle.kts` and no `src/` directory, spawn a general-purpose agent to generate a real, buildable skeleton before the devkit scaffold step below. Skip entirely for non-Java repos or repos that already have code.

   e. Read `Init_Project_Workflow.md` and execute its **GitHub-mode scaffold steps** (Stages 1–4) inline for this repo path:
      - Stage 1: scan the repo folder using the repo's `purpose` and `tech stack` from `repo_structure.md`
      - Stage 2: generate all agent scaffold files adapted to this repo's purpose and tech stack
      - Stage 3: skip the user-confirmation sub-step
      - Stage 4 equivalent: write all generated files; create directories; append `.gitignore` additions; inject `SessionStart` hook

   f. Write `.claude/agents/docs/build_state.md` inside the sub-repo:

      ```markdown
      # Build State
      **Product:** <product name from user's idea>
      **Repo Role:** <repo-name from repo_structure.md>
      **GitHub Project URL:** <project-url — fill after project creation>
      **Phase:** scaffold
      **Analysis Docs:** .claude/agents/docs/analysis/
      ```

   g. Update state file: `Updated: <now>` (repo count is already set from Stage 2).

3. **Project orchestrator folder** — **skip this step entirely if the only reason there's more than one repo is the Java REST service + API spec companion pattern under an otherwise-`monolith` decision** (i.e. exactly a service + its own `-api-spec` repo, nothing else). In that case there is no real multi-repo product to orchestrate — treat the REST service repo as the product's primary repo (it already gets the full devkit scaffold in step 2e) and proceed directly to step 4 below. For genuine multi-repo systems (independently deployable components beyond just a service+contract pair), create the orchestrator folder:

   a. Ask the user for the project orchestrator folder path if not already known: **"Where should I create the project orchestrator folder? Provide an absolute path."**

   b. Create the folder (if it does not already exist).

   c. Run `git init` inside the project folder.

   d. Run `gh repo create` for the project folder repo.

4. Run `gh project create` to create a GitHub Project named after the product. Store the returned project URL.

5. Link **all repos** (each sub-repo + the project folder repo, if one was created) to the GitHub Project:
   ```
   gh project item-add <project-number> --owner <owner> --url <sub-repo-url>
   ```
   Repeat for each repo.

6. Go back and fill in `GitHub Project URL` in every sub-repo's `.claude/agents/docs/build_state.md` that was written with an empty placeholder in step 2e.

**Steps 7–9 apply only if a project orchestrator folder was created in step 3** (skip all three for the service+api-spec-only case):

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

10. Update state file: `Stage: 4`, `GitHub Project URL: <url>`, `Updated: <now>`.

11. Proceed to Stage 5.

> **Handoff message note:** the Stage 5 handoff message below assumes a project-orchestrator path exists for multi-repo. For the service+api-spec-only case (no orchestrator folder), use the monolith-style handoff instead — "Open a Claude Code session in `<service-repo-path>` and run: `plan next sprint`" — pointing at the REST service repo, not a project-orchestrator folder that doesn't exist.

---

### Java Skeleton Generation

**Purpose:** For a brand-new (empty) Java repo, generate a real, buildable starting skeleton — package layout, `pom.xml`/`build.gradle`, and (shape-dependent) an OpenAPI contract, a real domain vertical slice (entity/mapper/repository/service/controller), Liquibase changelog, config — instead of leaving the repo with only the devkit's `.claude/agents/` scaffold and no actual code. Referenced from Path A step 5 and Path B step 2d above.

**Applies only when both are true** (check before spawning anything):
1. **Tech stack is Java** — the repo's tech stack column in `repo_structure.md` (or `architecture.md` / `architecture_<repo-name>.md`) names Java/Spring Boot/a JVM framework, **or** the repo's purpose names it as the API spec companion of a Java REST service (Stage 2 always tags these that way).
2. **Repo is code-empty** — the local path has **no** `pom.xml`, **no** `build.gradle`/`build.gradle.kts`, and **no** `src/` directory. Incidental files the earlier Stage 4 steps may already have created (`.git/`, `.claude/`, `CLAUDE.md`, `.gitignore`, `README.md`) do **not** count as "existing project" and do not block generation.

If either condition fails, **skip entirely** — do not touch the repo's code. This is a strict guard: never scaffold over or alongside a user's existing project.

**Ordering matters for the API spec ⇒ REST service pair:** Stage 2 orders the `-api-spec` repo before its REST service in `repo_structure.md`, and Path A/B process repos in table order, so by the time a REST service's turn comes up, its sibling api-spec repo has already been scaffolded and has a real `pom.xml`/`build.gradle` (with real `groupId:artifactId:version`) and a real `.yaml` contract to read.

**Execution (per repo, when both conditions hold):**

1. Spawn **one general-purpose agent** (**model: sonnet**) with a fully self-contained inline prompt (the agent has no memory of this conversation):

   ```
   Generate a real, buildable Java project skeleton at <repo-path>.

   Read these first, in order:
   1. .claude/agents/templates/skeletons/Java_Skeleton_Conventions.md — conventions and rules to follow (build tool, layering, DTO/entity/mapping conventions, what NOT to do). This is guidance, not a template to copy — you generate original files that follow these patterns.
   2. /result/analyst/architecture.md and, if it exists, /result/build/<repo-name>/architecture_<repo-name>.md — the actual project this repo belongs to: real domain entities, real endpoints, the decided Java/Spring Boot versions, any API-contract or persistence decisions already made.
   3. This repo's purpose and tech stack from /result/build/repo_structure.md.

   Decide the shape from the repo's stated purpose, per Java_Skeleton_Conventions.md: API spec (OpenAPI/Swagger contract for another service, no runtime) vs REST service (backend/API/service, runs standalone) vs pure library (SDK/library/client consumed by other Java code).

   If this repo is a REST service: its sibling API spec repo (named <repo-name>-api-spec) should already exist as a sibling folder — read its pom.xml/build.gradle (for real groupId:artifactId:version) and its .yaml spec (for real operationIds/schema names) before generating, so the service's dependency declaration and controller (implements {Resource}sApi) are correct against the real generated contract. If that sibling repo does NOT exist yet, stop and report this as a blocker rather than inventing local DTOs as a workaround.

   Generate a complete, real skeleton directly into <repo-path> — actual domain entity/resource/endpoint names from architecture.md, not a generic placeholder. Follow every convention in Java_Skeleton_Conventions.md exactly, including the "What the agent must NOT do" section.

   Do not touch anything under <repo-path>/.claude/ or any devkit scaffold files — those are written by a separate step. Only write build files (pom.xml, or build.gradle/build.gradle.kts), the OpenAPI yaml (API spec shape only), and src/.

   Report back: which shape you chose and why, the real entity/resource name(s) used, and the full list of files written (max 5 bullets + observations).
   ```

2. Agent reports back to the orchestrator (max 5 bullets + observations, per the standard Agent Completion Reports rule).
3. Orchestrator relays a one-line status to the user (e.g. "Java REST-service skeleton generated for `core-service` — `Tenant` entity, 11 files, wired to `core-service-api-spec`.") and continues to the devkit scaffold step.
4. **Stop on blocker** — if the agent reports it could not determine a real domain entity/resource from `architecture.md` (e.g. architecture is too abstract to name one), it should still generate the skeleton using the closest reasonable real name from the architecture rather than a generic placeholder, and note the ambiguity in its observations — this is not a blocking condition. A REST service whose sibling api-spec repo is genuinely missing **is** a blocking condition — stop and report to the user rather than working around it.

---

## Stage 5 — Doc Copy + Handoff

**Purpose:** Distribute analysis documents into each repo and print the handoff message to the user.

### Entry

1. Read `/result/build/repo_structure.md` to get the list of repos (monolith = one repo; multi-repo = each sub-repo, excluding the project orchestrator folder).

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
   | `/result/analyst/diagrams/` (entire folder) | `<repo-path>/.claude/agents/docs/analysis/diagrams/` |

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
- **Confirmation gates are mandatory** — never proceed from Stage 1 to 2 or Stage 2 to 3 without explicit user confirmation. Stage 1's gate accepts either an open feedback round (looped until resolved, see Stage 1's Confirmation Gate) or a plain confirmation that there's nothing further — it does not require a literal "yes". Stage 2's gate still requires the user to confirm the repo structure explicitly.
- **Adjustment loop** — if the user requests changes to `repo_structure.md` at the Stage 2 gate, apply and re-present before asking for confirmation again
- **Orchestrator-direct for Stage 2** — no agent spawn; orchestrator writes `repo_structure.md` inline
- **Parallel Stage 3 spawns** — Agent A and Agent B are spawned in a single orchestrator message; never sequentially
- **Stage 4 is sequential** — scaffold each repo one at a time; do not spawn parallel agents for repo scaffolding
- **Java skeleton generation is guarded and additive** — only for Java repos with no existing `pom.xml`/`build.gradle`/`build.gradle.kts`/`src/`; never overwrites or runs alongside an existing project; supports both Maven and Gradle (chosen from `architecture.md`, default Maven) but never mixes the two in one repo; generated skeletons use only public Maven Central dependencies, never invented proprietary artifacts
- **Every Java REST service gets a companion API spec repo** — Stage 2 adds it automatically, ordered before the service in `repo_structure.md`; the service's skeleton depends on the contract repo already existing and stops as a blocker (not a silent workaround) if it's missing; a monolith-with-a-Java-REST-service is routed through Path B for this pair even though `Decision` still reads `monolith`
- **Full-copy docs are never filtered** — `architecture.md`, `summary.md`, `testing_plan.md`, and `business_requirements.md` go to all repos verbatim
- **Stop on blocker** — if any agent reports a blocking issue, stop and report to the user before continuing
- **Completion reports** — each spawned agent returns its results to the orchestrator; orchestrator relays a brief status to the user after each stage
- **State file deleted on Stage 5 success** — if Stage 5 fails mid-copy, the state file remains for resume; only delete after all copies complete
