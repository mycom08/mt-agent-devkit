<!-- Included by: templates/github/Repo_Root_template.md, templates/strict/Repo_Root_template.md -->

<!-- SHARED-START -->
# {{PROJECT_NAME}} — {{AGENT_CLI_NAME}} Instructions

## Project Overview

{{PROJECT_DESCRIPTION}}
Canonical project context: `{{AGENT_DIR_PREFIX}}/agents/context/Project_Priming.md`

**Mode:** {{MODE}}
**Devkit source:** {{DEVKIT_SOURCE_URL}}
**Devkit version:** {{DEVKIT_VERSION}}

> Agents must read `**Mode:**` at the start of every workflow. When `Mode: strict`, follow strict-mode paths throughout (local MD files, local branches — no GitHub/MCP calls). See `{{AGENT_DIR_PREFIX}}/agents/rules/Strict_Mode_Story_Guide.md` for the full operation substitution reference.

---

## Agent Roster

Each specialized agent must read its instruction file before starting any work.

| Agent | Instruction File |
|---|---|
| Technical Lead | `{{AGENT_DIR_PREFIX}}/agents/technical_lead_instructions.md` |
| Developer | `{{AGENT_DIR_PREFIX}}/agents/developer_instructions.md` |
| QA | `{{AGENT_DIR_PREFIX}}/agents/qa_instructions.md` |
| Product Owner | `{{AGENT_DIR_PREFIX}}/agents/product_owner_instructions.md` |
| Business Analyst | `{{AGENT_DIR_PREFIX}}/agents/business_analyst_instructions.md` |
| UI/UX Designer | `{{AGENT_DIR_PREFIX}}/agents/ui_ux_designer_instructions.md` |

Agent memory, rules, working records, and context live under `{{AGENT_DIR_PREFIX}}/agents/`.

> **Project-mutable — never blindly overwritten on sync/update.** This table's paths and role set are edited locally per project: a `-ui-prototype` companion repo trims it to 3 roles, and a project migrated from the old flat instruction-file layout has its paths rewritten in place (`Update_Project_Workflow.md`'s "Path structure detection" step). It stays in `{{ROOT_FILE}}` rather than `orchestrator_instructions.md` for exactly that reason — `orchestrator_instructions.md` is devkit-verbatim, always overwritten in full, with no per-project preservation.

---

## Orchestrator Reference

The orchestrator (this top-level session) must read `{{AGENT_DIR_PREFIX}}/agents/orchestrator_instructions.md` before executing any workflow — it carries the workflow trigger table, session management, and completion-report format. No spawned subagent needs to read it; each spawn receives its own instruction/rules/memory paths directly in its prompt.

---

## Agent File Integrity

**Agents and the orchestrator must never create, modify, or delete agent infrastructure files during sprint work or any other workflow.**

Protected paths — read-only for all agents and the orchestrator at all times:

| Path | Contents |
|---|---|
| `{{AGENT_DIR_PREFIX}}/agents/*_instructions.md` | Role instruction files |
| `{{AGENT_DIR_PREFIX}}/agents/rules/` | All rules files |
| `{{AGENT_DIR_PREFIX}}/agents/workflows/` | All workflow files |
| `{{AGENT_DIR_PREFIX}}/agents/context/` | Project priming and document index |
| `{{AGENT_DIR_PREFIX}}/agents/devkit_version.txt` | Installed devkit version stamp |
| `{{AGENT_DIR_PREFIX}}/agents/orchestrator_instructions.md` | Orchestrator-only routing, session-management, and completion-report reference |

Writable paths during normal work:

| Path | Who writes | What |
|---|---|---|
| `{{AGENT_DIR_PREFIX}}/agents/memory/` | Each agent | Their own memory file only |
| `{{AGENT_DIR_PREFIX}}/agents/working-record/` | Each agent | Their own working record only |
| `{{AGENT_DIR_PREFIX}}/agents/tmp/` | Orchestrator | Pipeline state files |
| `{{AGENT_DIR_PREFIX}}/agents/docs/` | All agents | Stories, sprints, reviews (strict mode only) |

**The only operation that may update protected paths is `sync devkit`**, which is triggered explicitly by the user and handled exclusively by `Sync_Devkit_Workflow.md`. No agent, no workflow, and no orchestrator logic may modify these files for any other reason — including fixes, improvements, or adjustments discovered during sprint work.

If an agent identifies an error or improvement needed in a rules or workflow file, it must report it to the user as an observation — never self-correct by editing the file.

**Audit carve-out.** `sync devkit` and `update project` (the devkit-side command that applies local templates to this project) may each run a scoped, detect-only audit pass as their own final stage — this is a **workflow step, not an agent role or a third writer of protected paths**. The audit pass never writes to `rules/`, `instructions/`, or `{{ROOT_FILE}}` itself; it only reads the files that same run just wrote and, if it finds mode-adaptation drift, files a report Issue on the devkit repository — the fix, if any, lands upstream in `templates/`, never as a local edit here. No other workflow may invoke this audit pass.

---

## PR Approval Rule

**If `Mode: github`:** GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.

**If `Mode: strict`:** No PRs. The reviewer writes their verdict to the local review-record file at `{{AGENT_DIR_PREFIX}}/agents/docs/reviews/ST-XXXXXX_review.md` and appends a summary comment to the story MD `## Comments` section. See `Strict_Mode_Story_Guide.md` for the review-record format.
<!-- SHARED-END -->
