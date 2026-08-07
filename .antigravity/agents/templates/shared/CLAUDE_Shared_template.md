<!-- Included by: templates/github/CLAUDE_template.md, templates/strict/CLAUDE_template.md -->

<!-- SHARED-START -->
# {{PROJECT_NAME}} — Claude Code Instructions

## Project Overview

{{PROJECT_DESCRIPTION}}
Canonical project context: `.antigravity/agents/context/Project_Priming.md`

**Mode:** {{MODE}}
**Devkit source:** {{DEVKIT_SOURCE_URL}}
**Devkit version:** {{DEVKIT_VERSION}}

> Agents must read `**Mode:**` at the start of every workflow. When `Mode: strict`, follow strict-mode paths throughout (local MD files, local branches — no GitHub/MCP calls). See `.antigravity/agents/rules/Strict_Mode_Story_Guide.md` for the full operation substitution reference.

---

## Agent Roster

Each specialized agent must read its instruction file before starting any work.

| Agent | Instruction File |
|---|---|
| Technical Lead | `.antigravity/agents/technical_lead_instructions.md` |
| Developer | `.antigravity/agents/developer_instructions.md` |
| QA | `.antigravity/agents/qa_instructions.md` |
| Product Owner | `.antigravity/agents/product_owner_instructions.md` |
| Business Analyst | `.antigravity/agents/business_analyst_instructions.md` |
| UI/UX Designer | `.antigravity/agents/ui_ux_designer_instructions.md` |

Agent memory, rules, working records, and context live under `.antigravity/agents/`.

---

## Agent File Integrity

**Agents and the orchestrator must never create, modify, or delete agent infrastructure files during sprint work or any other workflow.**

Protected paths — read-only for all agents and the orchestrator at all times:

| Path | Contents |
|---|---|
| `.antigravity/agents/*_instructions.md` | Role instruction files |
| `.antigravity/agents/rules/` | All rules files |
| `.antigravity/agents/workflows/` | All workflow files |
| `.antigravity/agents/context/` | Project priming and document index |
| `.antigravity/agents/devkit_version.txt` | Installed devkit version stamp |

Writable paths during normal work:

| Path | Who writes | What |
|---|---|---|
| `.antigravity/agents/memory/` | Each agent | Their own memory file only |
| `.antigravity/agents/working-record/` | Each agent | Their own working record only |
| `.antigravity/agents/tmp/` | Orchestrator | Pipeline state files |
| `.antigravity/agents/docs/` | All agents | Stories, sprints, reviews (strict mode only) |

**The only operation that may update protected paths is `sync devkit`**, which is triggered explicitly by the user and handled exclusively by `Sync_Devkit_Workflow.md`. No agent, no workflow, and no orchestrator logic may modify these files for any other reason — including fixes, improvements, or adjustments discovered during sprint work.

If an agent identifies an error or improvement needed in a rules or workflow file, it must report it to the user as an observation — never self-correct by editing the file.

**Audit carve-out.** `sync devkit` and `update project` (the devkit-side command that applies local templates to this project) may each run a scoped, detect-only audit pass as their own final stage — this is a **workflow step, not an agent role or a third writer of protected paths**. The audit pass never writes to `rules/`, `instructions/`, or `CLAUDE.md` itself; it only reads the files that same run just wrote and, if it finds mode-adaptation drift, files a report Issue on the devkit repository — the fix, if any, lands upstream in `templates/`, never as a local edit here. No other workflow may invoke this audit pass.

---

## Agent Session Management

The orchestrator tracks the `conversationId` returned by every spawned agent. On loop-back, always prefer resuming over spawning:

| Situation | Action |
|---|---|
| Loop-back to a stage whose agent is still active | **Resume** — `send_message` to the saved `conversationId` with the new feedback |
| Loop-back but session has expired or ID is unavailable | **Spawn** — new `Agent` call with a fully self-contained prompt |
| First entry to any stage | **Spawn** — new `Agent` call |

Resuming keeps the agent's full prior context so it can act on feedback immediately without re-reading everything from scratch.

**Session ID update rule:** Only overwrite a saved session ID when a **new agent is spawned**. When resuming via `send_message`, do not change the stored ID — the interaction does not produce a new session.

---

## Agent Completion Reports

When any spawned agent completes and returns to the orchestrator, it **must** limit its summary to **5 bullets max**:

1. Story ID + what was done (e.g., "ST-000025 — PR #86 opened")
2. Key outcome (approved / blocked / passed / failed)
3. PR or commit reference if applicable
4. Any blockers or open items
5. Next action required (if any)

Detailed activity logs go in the agent's Working Record — not in the orchestrator message. The orchestrator relays a brief status update to the user after each stage.

---

## Workflows

Read the linked file before executing any workflow.

| Trigger | Workflow File |
|---|---|
| `workflow help` | `.antigravity/agents/workflows/Workflow_Guide.md` |
| `continue sprint` | `.antigravity/agents/workflows/Sprint_Workflow.md` |
| `start story ST-XXXXXX` | `.antigravity/agents/workflows/Start_Story_Workflow.md` |
| `resume story ST-XXXXXX` | `.antigravity/agents/workflows/Resume_Story_Workflow.md` |
| `refine sprint` | `.antigravity/agents/workflows/Refine_Sprint_Workflow.md` |
| `plan next sprint` / `plan sprint` | `.antigravity/agents/workflows/Plan_Sprint_Workflow.md` |
| `create stories` | `.antigravity/agents/workflows/Create_Stories_Workflow.md` |
| `refine prototype` | `.antigravity/agents/workflows/Refine_Prototype_Workflow.md` |
| `sync devkit` | `.antigravity/agents/workflows/Sync_Devkit_Workflow.md` |

Sprint and Start Story workflows share pipeline stages — see `.antigravity/agents/workflows/Shared_Pipeline_Stages.md`.

---

## PR Approval Rule

**If `Mode: github`:** GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.

**If `Mode: strict`:** No PRs. The reviewer writes their verdict to the local review-record file at `.antigravity/agents/docs/reviews/ST-XXXXXX_review.md` and appends a summary comment to the story MD `## Comments` section. See `Strict_Mode_Story_Guide.md` for the review-record format.
<!-- SHARED-END -->
