# mt-agent-devkit — Priming Context (Bootstrap)

> This is a cheat sheet for AI agents — the minimum context needed to understand *what this project is*, before knowing what task you have been given. Read it in full at step 1 of `Agent_Common_Bootstrap.md §1`. It is not comprehensive documentation.

> **Section numbers are shared with `Project_Priming_Read_On_Demand.md` and are never reused**, so a `Project_Priming §N` citation resolves to whichever of the two files holds that number. The routing table below is the index.

---

## On-Demand Sections — Routing Table

Not loaded at spawn. When a trigger fires, fetch **only** that section from `.mt-agent-devkit/context/Project_Priming_Read_On_Demand.md` with the `read-section` skill.

| Trigger | Fetch |
|---|---|
| **Editing any file under `.mt-agent-devkit/distribution/phase2/templates/`** — dual-update rule, bundle rebuild, `changes.json` fold-in shape (the version itself is never hand-edited). Also covers **adding a new agent role** and **splitting a shared rules/instructions file into bootstrap/on-demand tiers** — each has its own corpus-wide ripple checklist as a sub-section inside §15 | `§15` (How to Update a Template) |
| You have been assigned a story | `§3` (Story Workflow) |
| Starting a complex change — new workflow stage, major template restructure, new devkit command | `§4` (Design First Before Implementation) |
| Creating or updating a project document | `§6` (Internal Project Documents) — a pointer to `context/Document_Index.md`, the single document path list |
| You need the devkit's own command surface (writing or auditing docs about triggers) | `§10` (Core Commands) |
| You need the repo or raw-content URL | `§16` (Reference Links) |

---

## 1. Project Overview

**mt-agent-devkit** is a multi-provider devkit that scaffolds a complete AI Scrum team into any target project.

**Purpose:** Gives any project a fully wired AI agent team (Developer, TL, QA, PO, BA) plus sprint workflow files. Developers trigger the devkit once (`init project`), then run `continue sprint` or `start story` inside their project using the injected workflows.

**Status:** 🔄 Active development — see `VERSION` for the current in-progress version

**Key traits:** Markdown-first, no compiled artifact, no runtime service. All deliverables are `.md` template files, `.ps1`/`.sh` scripts, and workflow instruction files.

---

## 2. Glossary

| Term | Definition |
|------|-----------|
| PO | Product Owner — owns stories, defines AC, ticks checkboxes after QA confirms |
| TL | Technical Lead — owns architecture, reviews and approves PRs |
| Dev | Developer — implements stories, writes PRs |
| QA | Quality Assurance — tests AC, reports results, notifies PO |
| BA | Business Analyst — aligns requirements, flags scope creep |
| AC | Acceptance Criteria |
| Devkit | mt-agent-devkit — this project |
| Template | A `_template.md` file under `.mt-agent-devkit/distribution/phase2/templates/`, compiled into the deployment bundle that `init project` installs |
| Target project | A project that has had `init project` run on it |
| Workflow | An `.md` instruction file read by the orchestrator to run a pipeline |

---

## 5. Agent Working Records

**Location:** `{RUNTIME_ROOT}/working-record/{Agent_Name}_Working_Record.md`

Write format, access control, retention and the character cap are owned by `Agent_Common_Bootstrap.md §1` — that file is bootstrap-tier and already loaded, so this section is a pointer, not a restatement.

---

## 7. Key Directories

| What | Path |
|------|------|
| Devkit orchestrator | Selected entrypoint: `AGENTS.md` or `CLAUDE.md` |
| Devkit workflows | `.mt-agent-devkit/workflows/commands/` |
| Templates (for target projects) | `.mt-agent-devkit/distribution/phase2/templates/` (active); `.claude/agents/templates/` is frozen legacy plus the sync bridges |
| Shared agent sources | `.mt-agent-devkit/` |
| Shared skills | `.mt-agent-devkit/skills/<name>/SKILL.md` (canonical); `.claude/`, `.antigravity/`, `.codex/` `skills/` hold generated discovery wrappers. PO procedures are the `po-*` skills |
| Analyst output | `result/analyst/` |
| Version | `VERSION` (`x.y.z-SNAPSHOT` on `main`) — owned by `.github/workflows/release.yml`, never hand-edited |
| Change manifest | `changes.json` — deployment declaration for target projects; format owned by the `change-metadata` skill |

---

## 8. Tech Stack

| Layer | Technology |
|-------|-----------|
| Instruction files | Markdown (.md) |
| Windows scripts | PowerShell (.ps1) |
| Unix scripts | Shell (.sh) |
| VCS | Git / GitHub |

There is no compiled binary, no database, no web server, and no test framework. Pre-PR gate for `.sh` files: `bash -n <file>`. For `.ps1` files: PowerShell syntax check. For any PR touching `.claude/agents/templates/**` or `.claude/agents/workflows/**`: `python scripts/validate_templates.py` (Layer-1 corpus invariant check — must exit 0). For changes to `.mt-agent-devkit/**`, any provider's `harness/**`, internal working wrappers/skills, or root entrypoints, run `python scripts/validate_internal_harness.py`, `python .mt-agent-devkit/scripts/generate_wrappers.py --check`, and `python -m unittest scripts.test.test_internal_harness`, all exit 0. Run `python scripts/validate_templates.py` and `bash scripts/test/run.sh` for the existing template/deployment regressions. The optional `--migration-preservation` audit is for this migration only; never require it for later releases or ordinary maintenance. See `docs/Template_Test_Strategy.md` for the full template test approach (3-layer model, the 7 invariant specs, risk tiers, and deferred Layer-2/3 coverage).

---

## 9. API Standards

Not applicable — this project has no API.

---

## 11. Current State

The devkit injects a complete AI Scrum team (6 agent roles with their rules, skills, sprint workflows and scripts) into any target project. Two modes: `github` (full GitHub integration) and `strict` (local-only, no GitHub required).

**Known limitations:**
- ❌ Template tests are partial: the full `init`/`update` workflow matrix and agent behavior are not automated (`docs/Template_Test_Strategy.md`)

---

## 12. Architectural Patterns

**Template injection:** `build_bundle.py` compiles `.mt-agent-devkit/distribution/phase2/templates/` into the deployment bundle; `init project`, `update project` and `sync devkit` install that bundle into the target through a shared lifecycle engine.

**Version tracking:** `VERSION` + `changes.json` + released `vX.Y.Z` tags allow `sync devkit` (in target projects) to fetch only changed files from GitHub rather than re-installing everything. `sync devkit` resolves the latest release from the highest tag and reads that tag's `changes.json`; the release job stamps `VERSION`, the `CHANGELOG.md` heading, and the `changes.json` key together, so no agent ever edits a version by hand. (`version.txt` is a frozen `0.1.48` bridge artifact for installs predating the tag-based scheme — never bumped, never deleted.)

**Mode bifurcation:** GitHub mode uses GitHub Issues/PRs/Actions. Strict mode stores everything locally and gitignores the entire `.claude/agents/` folder.

---

## 13. Feature Current State

Current project status (Now / Next / Later / Done) lives in `docs/Project_Roadmap.md`, owned by the Product Owner and read by planners only. Live story state is the issue list: `gh issue list --label sprint-N --state all`.

---

## 14. Local Sandbox Environment

Not applicable — no Docker or sandbox environment.

---

**Document Version:** 1.10 — §11 team size and known limitations corrected.
**Previous:** 1.9 — §1-§12 name the Phase 2 templates as the active source.
**Last Updated:** 2026-11-26
**Audience:** Development team, architects, AI agents

