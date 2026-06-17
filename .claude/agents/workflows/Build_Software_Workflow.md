# Build Software Workflow

Triggered by: `"build software <idea>"` in CLAUDE.md

The text after the trigger keyword is the user's **idea**. If no text is provided, the orchestrator asks the user for a one-line description before starting.

**Output folders:**
- `/result/analyst/` — all Analyst pipeline outputs (unchanged)
- `/result/build/` — all Phase 1 build-specific artifacts

> **Stages 4–5** (per-repo initialisation and wiring) are implemented in `Build_Software_Phase2_Workflow.md` and are not part of this file.

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
**Stage:** <1 | 2 | 3>
**Idea:** <the user's idea text>
**Repo Count:** <number of repos or 0 if not yet determined>
**Confirmed:** <false | stage1 | stage2>
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

Spawn **two general-purpose agents** in the same message:

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
| `/result/analyst/summary.md` | `/result/build/<repo-name>/summary.md` |
| `/result/analyst/testing_plan.md` | `/result/build/<repo-name>/testing_plan.md` |
| `/result/analyst/business_requirements.md` | `/result/build/<repo-name>/business_requirements.md` |

> `architecture.md` is NOT copied in full — the architecture splitter (Agent B) produces a filtered version per repo. The user can always reference the full version at `/result/analyst/architecture.md`.

### Completion

4. Update state file: `Stage: 3`, `Updated: <now>`.

5. Present to the user:

   ```
   Stage 3 complete — Documents split per repo.

   Per-repo folders created under /result/build/:

   <list each repo and its output files>

   The following docs were copied to all repos unchanged:
   - summary.md
   - testing_plan.md
   - business_requirements.md

   Phase 1 complete. Run `build software phase 2` to proceed to repo initialisation and wiring (Stages 4–5).
   ```

---

## Pipeline Rules

- **State file first** — always check `.claude/agents/tmp/build_software_state.md` before doing any work; never skip the resume check
- **Same trigger, auto-resume** — `build software` (with or without an idea) activates resume if the state file exists; no separate resume command
- **Confirmation gates are mandatory** — never proceed from Stage 1 to 2 or Stage 2 to 3 without an explicit "yes" from the user
- **Adjustment loop** — if the user requests changes to `repo_structure.md` at the Stage 2 gate, apply and re-present before asking for confirmation again
- **Orchestrator-direct for Stage 2** — no agent spawn; orchestrator writes `repo_structure.md` inline
- **Parallel Stage 3 spawns** — Agent A and Agent B are spawned in a single orchestrator message; never sequentially
- **Full-copy docs are never filtered** — `summary.md`, `testing_plan.md`, and `business_requirements.md` go to all repos verbatim
- **Stop on blocker** — if any agent reports a blocking issue, stop and report to the user before continuing
- **Completion reports** — each spawned agent returns its results to the orchestrator; orchestrator relays a brief status to the user after each stage
