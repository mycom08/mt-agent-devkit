# mt-agent-devkit — Priming Context

> This is a cheat sheet for AI agents — the minimum context needed to understand the project, architecture, and team workflow. It is not comprehensive documentation.

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

## 3. Story Workflow

Stories are **GitHub Issues** in `mycom08/mt-agent-devkit` (title format: `[ST-XXXXXX][DEVKIT] Title`).

**Status flow:**

```
Backlog → Ready → In Progress → Review → Testing → Done
                                                     ↓ (if bug found after Done)
                                                  Hotfix → Review → Testing → Done
```

| Status | Who Moves It | When |
|--------|-------------|------|
| Backlog | PO | After story creation |
| Ready | PO | After assigning to implementer |
| In Progress | Implementer | Work branch created |
| Review | Implementer | PR created, reviewer requested |
| Testing | QA | After TL approval and merge |
| Done | PO | After all AC verified and ticked |

**Collaboration rules:**
- Story body contains only: User Story, AC, Deliverables
- All discussions happen as **comments** on the GitHub Issue — never in the body
- One topic per comment thread

For the full workflow: `.claude/agents/working/rules/Story_Standard.md`

---

## 4. Design First Before Implementation

For complex changes (new workflow stage, major template restructure, new devkit command), follow design-first:

1. **Developer** drafts a design as a story comment for TL review
2. **TL** approves before any file is written
3. No files changed until design is agreed

---

## 5. Agent Working Records

**Location:** `.claude/agents/working/working-record/{Agent_Name}_Working_Record.md`

**Access control:** Read and update only your own record. Never read or modify another agent's record.

Update at **start of session** and **end of session**. Keep 3 most recent days.

---

## 6. Internal Project Documents

| Document | Path |
|----------|------|
| Business Requirements | `docs/requirements/Business_Requirements.md` |
| Implementation Roadmap | `docs/plan/Implementation_Roadmap.md` |
| Product Backlog | `docs/plan/Product_Backlog.md` |
| Sprint Overviews | `docs/sprints/Sprint_N_Overview.md` |

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

## 10. Core Commands (devkit triggers)

| Command | What it does |
|---------|-------------|
| `analyze <requirement>` | Runs the Analyst pipeline — produces docs in `result/analyst/` |
| `init project [path]` | Scaffolds the AI Scrum team into a target project |
| `update project [path]` | Applies current local templates to an already-initialized project |
| `workflow help` | Shows this devkit's available commands |

Sprint execution commands (`continue sprint`, `start story`, etc.) live in the **target project** CLAUDE.md, not here.

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

## 15. How to Update a Template

When a rule, workflow, or instruction file needs to change, update the source template in `.claude/agents/templates/` — never edit a target project's installed copy directly.

**Steps (always in this order):**

1. **Edit the template file** under `.claude/agents/templates/` (e.g., `.claude/agents/templates/rules/QA_Rules_template.md`)
2. **Bump the patch version** in `version.txt` (e.g., `0.1.5` → `0.1.6`)
3. **Append a new entry** to `changes.json` — place it **after** the previous version entry (at the end of the object, before the closing `}`):

```json
"0.1.6": {
  "new": [],
  "modified": [
    ".claude/agents/templates/rules/QA_Rules_template.md"
  ],
  "descriptions": {
    ".claude/agents/templates/rules/QA_Rules_template.md": "Fix: one-line summary of what changed and why"
  }
}
```

Use `"new"` for files added for the first time; `"modified"` for files that already existed. Both can be non-empty in the same entry.

> Target projects running `sync devkit` compare their installed version against `version.txt` and fetch only the files listed in every version entry between their current version and the latest. Entries must be appended in ascending version order — inserting out of order will cause `sync devkit` to skip or double-apply changes.

---

## 16. Reference Links

1. **GitHub repo** — https://github.com/mycom08/mt-agent-devkit
2. **Raw content base URL** — https://raw.githubusercontent.com/mycom08/mt-agent-devkit/main

---

**Document Version:** 1.1
**Last Updated:** 2026-06-24
**Audience:** Development team, architects, AI agents
