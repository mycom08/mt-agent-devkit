# {{PROJECT_NAME}} — Claude Code Instructions

## Project Overview

{{PROJECT_DESCRIPTION}}
Canonical project context: `.claude/agents/context/Project_Priming.md`

**Mode:** {{MODE}}
**Devkit source:** {{DEVKIT_SOURCE_URL}}
**Devkit version:** {{DEVKIT_VERSION}}

> Agents must read `**Mode:**` at the start of every workflow. When `Mode: strict`, follow strict-mode paths throughout (local MD files, local branches — no GitHub/MCP calls). See `.claude/agents/rules/Strict_Mode_Story_Guide.md` for the full operation substitution reference.

---

## Agent Roster

Each specialized agent must read its instruction file before starting any work.

| Agent | Instruction File |
|---|---|
| Technical Lead | `.claude/agents/technical_lead_instructions.md` |
| Developer | `.claude/agents/developer_instructions.md` |
| QA | `.claude/agents/qa_instructions.md` |
| Product Owner | `.claude/agents/product_owner_instructions.md` |
| Business Analyst | `.claude/agents/business_analyst_instructions.md` |

Agent memory, rules, working records, and context live under `.claude/agents/`.

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

Writable paths during normal work:

| Path | Who writes | What |
|---|---|---|
| `.claude/agents/memory/` | Each agent | Their own memory file only |
| `.claude/agents/working-record/` | Each agent | Their own working record only |
| `.claude/agents/tmp/` | Orchestrator | Pipeline state files |
| `.claude/agents/docs/` | All agents | Stories, sprints, reviews (strict mode only) |

**The only operation that may update protected paths is `update agents`**, which is triggered explicitly by the user and handled exclusively by `Update_Agents_Workflow.md`. No agent, no workflow, and no orchestrator logic may modify these files for any other reason — including fixes, improvements, or adjustments discovered during sprint work.

If an agent identifies an error or improvement needed in a rules or workflow file, it must report it to the user as an observation — never self-correct by editing the file.

---

## Agent Session Management

The orchestrator tracks the `agentId` returned by every spawned agent. On loop-back, always prefer resuming over spawning:

| Situation | Action |
|---|---|
| Loop-back to a stage whose agent is still active | **Resume** — `SendMessage` to the saved `agentId` with the new feedback |
| Loop-back but session has expired or ID is unavailable | **Spawn** — new `Agent` call with a fully self-contained prompt |
| First entry to any stage | **Spawn** — new `Agent` call |

Resuming keeps the agent's full prior context so it can act on feedback immediately without re-reading everything from scratch.

**Session ID update rule:** Only overwrite a saved session ID when a **new agent is spawned**. When resuming via `SendMessage`, do not change the stored ID — the interaction does not produce a new session.

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
| `workflow help` | `.claude/agents/workflows/Workflow_Guide.md` |
| `continue sprint` | `.claude/agents/workflows/Sprint_Workflow.md` |
| `start story ST-XXXXXX` | `.claude/agents/workflows/Start_Story_Workflow.md` |
| `resume story ST-XXXXXX` | `.claude/agents/workflows/Resume_Story_Workflow.md` |
| `refine sprint` | `.claude/agents/workflows/Refine_Sprint_Workflow.md` |
| `plan next sprint` / `plan sprint` | `.claude/agents/workflows/Plan_Sprint_Workflow.md` |
| `create stories` | `.claude/agents/workflows/Create_Stories_Workflow.md` |
| `analyze <requirement>` | `.claude/agents/workflows/Analyst_Workflow.md` |
| `sync devkit` | `.claude/agents/workflows/Sync_Devkit_Workflow.md` |

Sprint and Start Story workflows share pipeline stages — see `.claude/agents/workflows/Shared_Pipeline_Stages.md`.

---

## PR Approval Rule

**If `Mode: github`:** GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.

**If `Mode: strict`:** No PRs. The reviewer writes their verdict to the local review-record file at `.claude/agents/docs/reviews/ST-XXXXXX_review.md` and appends a summary comment to the story MD `## Comments` section. See `Strict_Mode_Story_Guide.md` for the review-record format.
