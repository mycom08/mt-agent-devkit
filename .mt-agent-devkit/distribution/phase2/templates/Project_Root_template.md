# {{PROJECT_NAME}} — Project Orchestrator

## Orchestrator Startup

Before doing anything else, read `{{AGENT_DIR_PREFIX}}/agents/context/Project_Priming.md` — it has the project overview, repo structure, and this folder's own role. Do this at the start of every session opened here, not just the first one.

## Overview

This is the **project orchestrator folder** for a multi-repo build managed by mt-agent-devkit. It coordinates story creation and sprint planning across all repos in the project.

**Mode:** {{MODE}}
**Devkit source:** {{DEVKIT_SOURCE_URL}}
**Devkit version:** {{DEVKIT_VERSION}}

> This folder is **not** a scrum team. It does not have `continue sprint`, `plan next sprint`, `refine sprint`, or `start story` triggers. Those live in each individual repo's `{{ROOT_FILE}}`. Run sprint workflows from inside the relevant repo folder.

---

## Repo Roster

The following repos belong to this project. All paths are absolute.

{{REPOS}}

> Canonical repo structure: `/result/build/repo_structure.md`

---

## Workflows

| Trigger | What it does |
|---|---|
| `build software` | Phase 2 — coordinate story creation and sprint planning across all repos |
| `sync devkit` | Pull the latest version of this folder's 3 devkit-owned files (`{{ROOT_FILE}}`, `Build_Software_Project_Workflow.md`; `Project_Priming.md` is skipped, project-owned) |
| `workflow help` | Show this project orchestrator command reference |

---

## Build Software Workflow

Trigger: user says **"build software"**

This is Phase 2 of the `build software` pipeline. It assumes Phase 1 (Stages 1–3) is complete and all repos have been scaffolded (Stage 4 done). It reads `build_state.md` and `repo_structure.md`, then coordinates `create stories` and `plan next sprint` across all repos.

Read `{{AGENT_DIR_PREFIX}}/agents/workflows/Build_Software_Project_Workflow.md` for the complete pipeline before executing.

---

## Sync Devkit Workflow

Trigger: user says **"sync devkit"** or **"sync devkit --auto"**

Fetches the latest version of this folder's own devkit-templated files (`{{ROOT_FILE}}`, `{{AGENT_DIR_PREFIX}}/agents/workflows/Build_Software_Project_Workflow.md`) from the devkit source and applies them, preserving `Project_Priming.md` and this folder's own `Repo Roster`/`Mode`/`Devkit source`/`Devkit version` fields untouched.

Read `{{AGENT_DIR_PREFIX}}/agents/workflows/Sync_Devkit_Project_Workflow.md` for the complete pipeline before executing.

---

## Workflow Help

Trigger: user says **"workflow help"**

No agents are spawned. Print the following reference directly to the user.

---

### {{PROJECT_NAME}} Project Orchestrator — Available Commands

This is the project orchestrator for a multi-repo build. Sprint execution commands are **not** available here — they live inside each repo.

| Command | What it does |
|---|---|
| `build software` | Phase 2: coordinate story creation and sprint planning across all repos |
| `sync devkit` | Pull the latest version of this folder's devkit-owned files |
| `workflow help` | Show this reference |

**To run sprint workflows, open a {{AGENT_CLI_NAME}} session inside the target repo:**

{{REPOS}}

> Each repo has its own `{{ROOT_FILE}}` with `continue sprint`, `start story`, `plan next sprint`, and all other scrum team commands.

---

## Agent File Integrity

**Agents and the orchestrator must never create, modify, or delete agent infrastructure files during any workflow.**

Protected paths — read-only at all times:

| Path | Contents |
|---|---|
| `{{AGENT_DIR_PREFIX}}/agents/workflows/` | All workflow files |
| `{{AGENT_DIR_PREFIX}}/agents/context/` | Project priming |
| `{{AGENT_DIR_PREFIX}}/agents/devkit_version.txt` | Installed devkit version stamp |

Writable paths:

| Path | Who writes | What |
|---|---|---|
| `{{AGENT_DIR_PREFIX}}/agents/tmp/` | Orchestrator | Pipeline state files |
| `{{AGENT_DIR_PREFIX}}/agents/docs/` | Orchestrator | Build state, split docs |

**The only operation that may update protected paths is `sync devkit`**, which is triggered explicitly by the user and handled exclusively by `Sync_Devkit_Project_Workflow.md`. No agent, no workflow, and no orchestrator logic may modify these files for any other reason.
