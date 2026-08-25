# mt-agent-devkit — Priming Context (Bootstrap)

> This is a cheat sheet for AI agents — the minimum context needed to understand *what this project is*, before knowing what task you have been given. Read it in full at step 1 of `Agent_Common_Bootstrap.md §1`. It is not comprehensive documentation.

> **Section numbers are shared with `Project_Priming_Read_On_Demand.md` and are never reused**, so a `Project_Priming §N` citation resolves to whichever of the two files holds that number. The routing table below is the index.

---

## On-Demand Sections — Routing Table

Not loaded at spawn. When a trigger fires, fetch **only** that section from `.claude/agents/working/context/Project_Priming_Read_On_Demand.md` with the `read-section` skill.

| Trigger | Fetch |
|---|---|
| **Editing any file under `.claude/agents/templates/`** — dual-update rule, `version.txt` bump, `changes.json` entry shape and ordering. Also covers **adding a new agent role** and **splitting a shared rules/instructions file into bootstrap/on-demand tiers** — each has its own corpus-wide ripple checklist as a sub-section inside §15 | `§15` (How to Update a Template) |
| You have been assigned a story | `§3` (Story Workflow) |
| Starting a complex change — new workflow stage, major template restructure, new devkit command | `§4` (Design First Before Implementation) |
| Creating or updating a project document | `§6` (Internal Project Documents) — the canonical paths |
| You need the devkit's own command surface (writing or auditing docs about triggers) | `§10` (Core Commands) |
| You need the repo or raw-content URL | `§16` (Reference Links) |

---

## 1. Project Overview

**mt-agent-devkit** is a Claude Code devkit that scaffolds a complete AI Scrum team into any target project.

**Purpose:** Gives any project a fully wired AI agent team (Developer, TL, QA, PO, BA) plus sprint workflow files. Developers trigger the devkit once (`init project`), then run `continue sprint` or `start story` inside their project using the injected workflows.

**Status:** 🔄 Active development — see `version.txt` for current version

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
| Template | A `_template.md` file under `.claude/agents/templates/` used by `init project` |
| Target project | A project that has had `init project` run on it |
| Workflow | An `.md` instruction file read by the orchestrator to run a pipeline |

---

## 5. Agent Working Records

**Location:** `.claude/agents/working/working-record/{Agent_Name}_Working_Record.md`

Write format, access control, retention and the character cap are owned by `Agent_Common_Bootstrap.md §1` — that file is bootstrap-tier and already loaded, so this section is a pointer, not a restatement.

---

## 7. Key Directories

| What | Path |
|------|------|
| Devkit orchestrator | `CLAUDE.md` |
| Devkit workflows | `.claude/agents/workflows/` |
| Templates (for target projects) | `.claude/agents/templates/` |
| Agent working files | `.claude/agents/working/` |
| Analyst output | `result/analyst/` |
| Version | `version.txt` |
| Change manifest | `changes.json` — tracks **template files deployed to target projects only** (under `.claude/agents/templates/`); devkit-internal workflows (`.claude/agents/workflows/`) are excluded |

---

## 8. Tech Stack

| Layer | Technology |
|-------|-----------|
| Instruction files | Markdown (.md) |
| Windows scripts | PowerShell (.ps1) |
| Unix scripts | Shell (.sh) |
| VCS | Git / GitHub |

There is no compiled binary, no database, no web server, and no test framework. Pre-PR gate for `.sh` files: `bash -n <file>`. For `.ps1` files: PowerShell syntax check. For any PR touching `.claude/agents/templates/**` or `.claude/agents/workflows/**`: `python scripts/validate_templates.py` (Layer-1 corpus invariant check — must exit 0). See `docs/Template_Test_Strategy.md` for the full template test approach (3-layer model, the 6 invariant specs, risk tiers, and deferred Layer-2/3 coverage).

---

## 9. API Standards

Not applicable — this project has no API.

---

## 11. Current State

The devkit injects a complete AI Scrum team (5 agents, 15+ rules files, 9 sprint workflow files, 2 version-check scripts) into any target project. Two modes: `github` (full GitHub integration) and `strict` (local-only, no GitHub required).

**Known limitations:**
- ❌ No automated test suite for verifying template correctness
- ❌ Sprint workflow commands not yet wired into the devkit's own CLAUDE.md

---

## 12. Architectural Patterns

**Template injection:** `init project` reads from `.claude/agents/templates/`, adapts content, and writes to the target project's `.claude/agents/`.

**Version tracking:** `version.txt` + `changes.json` allow `sync devkit` (in target projects) to fetch only changed files from GitHub rather than re-installing everything.

**Mode bifurcation:** GitHub mode uses GitHub Issues/PRs/Actions. Strict mode stores everything locally and gitignores the entire `.claude/agents/` folder.

---

## 13. Feature Current State

No active feature sprint — devkit maintenance is handled as individual stories.

---

## 14. Local Sandbox Environment

Not applicable — no Docker or sandbox environment.

---

**Document Version:** 1.3 — preamble trimmed to drop the section inventory the routing table already carries; §15a's routing row folded into §15.
**Previous:** 1.2 — split into bootstrap + read-on-demand tiers 2026-08-21 (devkit's own team only)
**Last Updated:** 2026-08-21
**Audience:** Development team, architects, AI agents
