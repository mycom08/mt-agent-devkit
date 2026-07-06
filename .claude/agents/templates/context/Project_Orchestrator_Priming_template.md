# {{PROJECT_NAME}} — Project Orchestrator Priming Context

> This is a cheat sheet for AI agents opening a session in this **project orchestrator folder** — the minimum context needed to understand what the product is, how it's split into repos, and what this folder itself is (and isn't) for. It is not comprehensive documentation; see `docs/` for the full analysis.

## 1. What This Project Does

{{PROJECT_OVERVIEW}}

Full detail: `docs/summary.md` (overview), `docs/business_requirements.md` (requirements), `docs/architecture.md` (architecture).

---

## 2. Structure

This product is split into the following repos. All local paths are absolute; each repo is its own git repository with its own remote (not a submodule of this folder).

{{REPOS}}

> Canonical repo structure and rationale for the split: `docs/repo_structure.md`

---

## 3. Role of This Orchestrator Folder

**This folder coordinates across repos — it does not implement anything itself and is not a Scrum team.**

- It has no `continue sprint`, `start story`, `plan next sprint`, or `refine sprint` triggers. Those live in each individual repo's own `CLAUDE.md` — open a session inside that repo folder to run them.
- Its only workflow trigger is `build software`, which (once every repo is scaffolded) coordinates `create stories` + `plan next sprint` across all repos listed above. See `.claude/agents/workflows/Build_Software_Project_Workflow.md`.
- `.claude/agents/docs/build_state.md` tracks this folder's own build phase and the GitHub Project URL shared by every repo.
- `docs/` holds the full analysis (architecture, business requirements, testing plan, implementation roadmap, diagrams) that every repo's own analysis docs were split from — read it here for whole-product context that no single repo's filtered docs cover.

---

**Document Version:** 1.0
**Last Updated:** {{DATE}}
