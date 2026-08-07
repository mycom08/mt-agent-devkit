# Sprint 1 Overview

**Sprint:** 1  
**Status:** Planned  
**Capacity:** 60 points  
**Planned Points:** 23  
**Sprint Goal:** Deliver the `build software` end-to-end workflow (Stages 1–5) including all supporting templates, project-level CLAUDE scaffolding, devkit trigger wiring, and protect retro-applied improvements from sync overwrites.

---

## Stories

| Issue | Story ID | Title | Priority | Points | Assigned | Status |
|-------|----------|-------|----------|--------|----------|--------|
| #2 | ST-000002 | Build Software Workflow — Phase 1 Stages 1–3 (Analyze, Repo Planning, Doc Splitting) | Must-Have | 5 | Developer | Ready |
| #3 | ST-000003 | Build Software Workflow — Phase 1 Stages 4–5 (Scaffold + Handoff) | Must-Have | 5 | Developer | Ready |
| #4 | ST-000004 | Project-Level CLAUDE Template and Phase 2 Build Software Workflow | Must-Have | 8 | Developer | Ready |
| #5 | ST-000005 | Wire build software Trigger + Update changes.json + Version Bump | Must-Have | 2 | Developer | Ready |
| #1 | ST-000001 | Protect retro-applied improvements from sync devkit overwrites | Should-Have | 3 | Developer | Ready |

---

## AC Summaries

**ST-000002 (5 pts — Must-Have)**  
`build software <idea>` trigger routes to `Build_Software_Workflow.md`. Stage 1 delegates to existing `analyze` workflow with confirmation gate. Stage 2 spawns TL to produce `repo_structure.md` (monolith vs multi-repo decision) with user confirmation. Stage 3 spawns TL + PO in parallel to split docs per repo under `/result/build/<repo-name>/`. Pipeline state file created and maintained across all stages.

**ST-000003 (5 pts — Must-Have)**  
Stages 4–5 appended to `Build_Software_Workflow.md`. Creates local project folder, git-initialises repos, runs `gh repo create` + `init project` per repo, creates GitHub Project, links repos. Stage 5 copies docs into each repo, writes `build_state.md`, prints handoff message, deletes state temp file.

**ST-000004 (8 pts — Must-Have)**  
New `Project_CLAUDE_template.md` with `build software` + `workflow help` triggers and repo roster placeholder. New `Build_Software_Project_Workflow_template.md`. Phase 2 workflow reads `build_state.md` / `repo_structure.md`, spawns repo orchestrators in parallel (multi-repo) or delegates directly (monolith), updates `build_state.md` to `ready` phase, and prints per-repo handoff.

**ST-000005 (2 pts — Must-Have)**  
Devkit `CLAUDE.md` wired with `build software` trigger. `workflow help` table updated. `changes.json` new version entry listing new template files. `version.txt` bumped to `0.0.9`. README prerequisites updated for `gh` CLI requirement.

**ST-000001 (3 pts — Should-Have)**  
`Shared_Pipeline_Stages_template.md` retro step instructs agents to mark modified sections with `<!-- retro-adapted: preserve on sync -->`. `Sync_Devkit_Workflow_template.md` overwrite and adapt-to-mode strategies preserve retro-marked sections. Stage 2 completion report in `sync devkit` lists preserved sections. `changes.json` updated.

---

## Dependency Order

ST-000002 must complete before ST-000003 and ST-000005.  
ST-000004 can run in parallel with ST-000002 and ST-000003.  
ST-000001 is independent — no dependencies.  
ST-000005 depends on ST-000002, ST-000003, ST-000004 all complete.

---

**Created:** 2026-06-17  
**Created by:** Product Owner
