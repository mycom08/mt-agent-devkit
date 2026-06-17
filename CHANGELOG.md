# Changelog

All notable changes to mt-agent-devkit are documented here.

---

## [Unreleased]

### Added
- [ST-000002] `build software <idea>` workflow — Stages 1–3: Analysis (delegates to `analyze`), Repo Planning (orchestrator-direct, produces `repo_structure.md`), Doc Splitting (parallel general-purpose agents produce per-repo filtered roadmap and architecture files). Pipeline state stored in `.claude/agents/tmp/build_software_state.md` with automatic resume on re-trigger. New file: `.claude/agents/workflows/Build_Software_Workflow.md`.

---
