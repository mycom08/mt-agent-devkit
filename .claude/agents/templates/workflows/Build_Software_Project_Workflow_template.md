# Build Software Project Workflow

Triggered by: `"build software"` in the project orchestrator `CLAUDE.md`

This is **Phase 2** of the `build software` pipeline. It assumes:
- Phase 1 (Stages 1–3 of `Build_Software_Workflow.md`) is complete
- All repos have been scaffolded with an AI Scrum team (Stage 4 of `Build_Software_Workflow.md`)
- Split analysis docs exist under `/result/build/<repo-name>/`

**Purpose:** Coordinate `create stories` and `plan next sprint` across all repos so each repo's agent team is ready to begin sprint execution independently.

---

## Startup

### Step 1 — Read state files

1. Read `.claude/agents/docs/build_state.md` (relative to this project orchestrator folder).
2. Read `/result/build/repo_structure.md`.

### Step 2 — Phase guard

- Check the `**Phase:**` field in `build_state.md`.
- If phase is **not** `scaffold` → print the following error and stop:

  ```
  Error: build_state.md phase is "<current-phase>", expected "scaffold".

  Phase 2 can only run when repos have been scaffolded and are awaiting sprint planning.
  Current phase indicates this workflow has already run or was not started correctly.

  If you believe this is wrong, check .claude/agents/docs/build_state.md and correct the Phase field manually.
  ```

- If phase is `scaffold` → continue to Step 3.

### Step 3 — Detect monolith vs multi-repo

Read the `**Repo Role:**` field in `build_state.md`:

- If value is `monolith` → follow the **Monolith Path** below.
- Any other value → follow the **Multi-Repo Path** below.

---

## Monolith Path

The project folder is the single repo. The standard `CLAUDE.md` (already injected by Stage 4) handles all sprint workflows.

1. Print to the user:

   ```
   Project is a monolith — no sub-orchestrators needed.

   The scrum team is already set up in this folder. To begin sprint execution:

     1. Run: plan next sprint
        (uses the analysis docs in .claude/agents/docs/analysis/ as input)

     2. Then run: continue sprint

   All scrum team commands are available in this folder's CLAUDE.md.
   ```

2. Stop. No further orchestration is needed.

---

## Multi-Repo Path

### Step 4 — Prepare repo list

From `repo_structure.md`, extract:
- Each repo's `name`
- Each repo's `local path` (absolute path — resolve relative paths against the user's working directory if needed)

From `build_state.md`, confirm the GitHub Project URL for context.

For each repo, determine:
- **Repo path** — absolute path on disk
- **Repo role** — the `name` value from `repo_structure.md` (e.g., `api-service`, `web-app`)
- **Analysis docs path** — `<repo-path>/.claude/agents/docs/analysis/` (where Stage 4 placed the split docs)
- **CLAUDE.md path** — `<repo-path>/CLAUDE.md`
- **Sprint workflow path** — `<repo-path>/.claude/agents/workflows/Sprint_Workflow.md` (or equivalent for the installed mode)

### Step 5 — Spawn repo orchestrators (parallel)

Spawn **one general-purpose agent per repo** in a **single orchestrator message** (all spawns in parallel).

For each repo, use the following inline prompt template, substituting all `<placeholders>` with the actual values from Step 4:

---

```
You are a repo orchestrator for the project build pipeline. Your job is to run `create stories` and `plan next sprint` for one repo using pre-existing analysis documents.

## Repo details

- **Repo path (absolute):** <absolute-repo-path>
- **Repo role:** <repo-role>
- **Analysis docs:** <absolute-repo-path>/.claude/agents/docs/analysis/
- **CLAUDE.md:** <absolute-repo-path>/CLAUDE.md
- **Sprint workflow:** <absolute-repo-path>/.claude/agents/workflows/Sprint_Workflow.md

## What to do

1. Read `<absolute-repo-path>/CLAUDE.md` to understand the repo's mode (github or strict) and available triggers.
2. Read `<absolute-repo-path>/.claude/agents/docs/analysis/` — this folder contains the split analysis documents for this repo (implementation roadmap, architecture, etc.).
3. Run `create stories` using the analysis docs as input:
   - Read `<absolute-repo-path>/.claude/agents/workflows/Create_Stories_Workflow.md` for instructions.
   - All story files, issue operations, and gh commands must use the absolute repo path `<absolute-repo-path>` and, for GitHub mode, `--repo <github-org/repo-slug>`.
4. After stories are created, run `plan next sprint`:
   - Read `<absolute-repo-path>/.claude/agents/workflows/Plan_Sprint_Workflow.md` for instructions.
   - All file operations and gh commands must use the absolute repo path.
5. Report back when sprint 1 is planned. Your report must include:
   - Repo path
   - Number of stories created
   - Sprint 1 name (e.g., sprint-1)
   - Any blockers or errors encountered

## Rules

- Never assume the working directory is the repo path — always use the absolute path for every file read, file write, and gh command.
- Do not run `continue sprint` — stop after `plan next sprint` completes.
- If you encounter a blocker (missing file, gh auth error, etc.), report it immediately rather than guessing.
```

---

### Step 6 — Wait for all repo orchestrators to complete

Collect the completion report from each repo orchestrator. Do not proceed until all repos have reported.

**On blocker:** If any repo orchestrator reports a blocker, print the blocker to the user and ask how to proceed before continuing with the remaining repos.

### Step 7 — Update build state

After all repos report sprint 1 planned:

1. Read `.claude/agents/docs/build_state.md`.
2. Update the `**Phase:**` field from `scaffold` to `ready`.
3. Write the updated file back.

### Step 8 — Print handoff

Print the following to the user (substituting actual values):

```
Phase 2 complete — Sprint 1 planned across all repos.

Each repo's scrum team is ready for sprint execution. Run `continue sprint` from inside each repo:

<for each repo>
  Repo: <repo-name> (<repo-role>)
  Path: <absolute-repo-path>
  Command: continue sprint
</for each repo>

build_state.md updated: Phase → ready
```

---

## Pipeline Rules

- **Phase guard is mandatory** — never skip the `build_state.md` phase check; stop with the error message if phase is not `scaffold`
- **Monolith detection first** — always check `Repo Role` before deciding to spawn agents
- **All repo orchestrators spawn in parallel** — never spawn sequentially; send a single orchestrator message with all agent spawns
- **Absolute paths only** — repo orchestrators must never use relative paths or assume working directory
- **Stop on blocker** — if any orchestrator reports a blocking issue, surface it to the user before proceeding
- **State update is mandatory** — always update `build_state.md` phase to `ready` after all repos complete, before printing the handoff
