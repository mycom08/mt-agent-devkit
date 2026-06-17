# Changelog

All notable changes to mt-agent-devkit are documented here.

---

## [Unreleased]

### Added
- [ST-000003] `Build_Software_Workflow.md` Stages 4–5: Stage 4 scaffolds all repos inline (git init, gh repo create, Init_Project_Workflow GitHub-mode steps, gh project create, repo-to-project linking, build_state.md) for both monolith and multi-repo paths; Stage 5 copies full summary docs and per-repo split files into each repo under `.claude/agents/docs/analysis/`, deletes the state file on success, and prints the handoff message. Pipeline State section updated with Stage 4/5 resume rules and GitHub Project URL field.
- [ST-000004] `Project_CLAUDE_template.md` — project orchestrator CLAUDE.md template for multi-repo `build software` setups; contains `build software` and `workflow help` triggers, repo roster placeholder, and an explicit note that scrum team triggers are not available in the project orchestrator folder.
- [ST-000004] `Build_Software_Project_Workflow_template.md` — Phase 2 workflow for the project orchestrator; reads `build_state.md` and `repo_structure.md`, detects monolith vs multi-repo, spawns parallel repo orchestrator agents to run `create stories` and `plan next sprint` per repo, then updates `build_state.md` phase to `ready`.
- [ST-000002] `build software <idea>` workflow — Stages 1–3: Analysis (delegates to `analyze`), Repo Planning (orchestrator-direct, produces `repo_structure.md`), Doc Splitting (parallel general-purpose agents produce per-repo filtered roadmap and architecture files). Pipeline state stored in `.claude/agents/tmp/build_software_state.md` with automatic resume on re-trigger. New file: `.claude/agents/workflows/Build_Software_Workflow.md`.

---
