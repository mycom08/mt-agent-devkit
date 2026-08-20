<!-- Included by: templates/github/Orchestrator_Guide_template.md, templates/strict/Orchestrator_Guide_template.md -->

<!-- SHARED-START -->
# Orchestrator Guide

> Read by the orchestrator only — workflow routing, agent roster, session management, and completion-report format for running this project's AI Scrum team. No spawned subagent needs this file: each spawn receives its own instruction/rules/memory paths directly in its prompt. Content every role needs (Mode, Agent File Integrity, PR Approval Rule) lives in `CLAUDE.md`.

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
| UI/UX Designer | `.claude/agents/ui_ux_designer_instructions.md` |

Agent memory, rules, working records, and context live under `.claude/agents/`.

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
| `refine prototype` | `.claude/agents/workflows/Refine_Prototype_Workflow.md` |
| `sync devkit` | `.claude/agents/workflows/Sync_Devkit_Workflow.md` |

Sprint and Start Story workflows share pipeline stages — see `.claude/agents/workflows/Shared_Pipeline_Stages.md`.
<!-- SHARED-END -->
