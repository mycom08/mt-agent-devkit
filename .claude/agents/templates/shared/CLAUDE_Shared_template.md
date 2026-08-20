<!-- Included by: templates/github/CLAUDE_template.md, templates/strict/CLAUDE_template.md -->

<!-- SHARED-START -->
# {{PROJECT_NAME}} — Claude Code Instructions

## Project Overview

{{PROJECT_DESCRIPTION}}
Canonical project context: `.claude/agents/context/Project_Priming.md`

**Mode:** {{MODE}}
**Devkit source:** {{DEVKIT_SOURCE_URL}}
**Devkit version:** {{DEVKIT_VERSION}}

> Agents must read `**Mode:**` at the start of every workflow. When `Mode: strict`, follow strict-mode paths throughout (local MD files, local branches — no GitHub/MCP calls). See `.claude/agents/rules/Strict_Mode_Story_Guide.md` for the full operation substitution reference.

---

## Orchestrator Reference

The orchestrator (this top-level session) must read `.claude/agents/Orchestrator_Guide.md` before executing any workflow — it carries the workflow trigger table, agent roster, session management, and completion-report format. No spawned subagent needs to read it; each spawn receives its own instruction/rules/memory paths directly in its prompt.

---

## Agent File Integrity

**Agents and the orchestrator must never create, modify, or delete agent infrastructure files during sprint work or any other workflow.**

Protected paths — read-only for all agents and the orchestrator at all times:

| Path | Contents |
|---|---|
| `.claude/agents/*_instructions.md` | Role instruction files |
| `.claude/agents/rules/` | All rules files |
| `.claude/agents/workflows/` | All workflow files |
| `.claude/agents/context/` | Project priming and document index |
| `.claude/agents/devkit_version.txt` | Installed devkit version stamp |
| `.claude/agents/Orchestrator_Guide.md` | Orchestrator-only routing, roster, and session-management reference |

Writable paths during normal work:

| Path | Who writes | What |
|---|---|---|
| `.claude/agents/memory/` | Each agent | Their own memory file only |
| `.claude/agents/working-record/` | Each agent | Their own working record only |
| `.claude/agents/tmp/` | Orchestrator | Pipeline state files |
| `.claude/agents/docs/` | All agents | Stories, sprints, reviews (strict mode only) |

**The only operation that may update protected paths is `sync devkit`**, which is triggered explicitly by the user and handled exclusively by `Sync_Devkit_Workflow.md`. No agent, no workflow, and no orchestrator logic may modify these files for any other reason — including fixes, improvements, or adjustments discovered during sprint work.

If an agent identifies an error or improvement needed in a rules or workflow file, it must report it to the user as an observation — never self-correct by editing the file.

**Audit carve-out.** `sync devkit` and `update project` (the devkit-side command that applies local templates to this project) may each run a scoped, detect-only audit pass as their own final stage — this is a **workflow step, not an agent role or a third writer of protected paths**. The audit pass never writes to `rules/`, `instructions/`, or `CLAUDE.md` itself; it only reads the files that same run just wrote and, if it finds mode-adaptation drift, files a report Issue on the devkit repository — the fix, if any, lands upstream in `templates/`, never as a local edit here. No other workflow may invoke this audit pass.

---

## PR Approval Rule

**If `Mode: github`:** GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.

**If `Mode: strict`:** No PRs. The reviewer writes their verdict to the local review-record file at `.claude/agents/docs/reviews/ST-XXXXXX_review.md` and appends a summary comment to the story MD `## Comments` section. See `Strict_Mode_Story_Guide.md` for the review-record format.
<!-- SHARED-END -->
