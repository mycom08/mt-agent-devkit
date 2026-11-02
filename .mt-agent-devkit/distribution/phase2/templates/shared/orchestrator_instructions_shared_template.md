<!-- Included by: templates/github/orchestrator_instructions_template.md, templates/strict/orchestrator_instructions_template.md -->

<!-- SHARED-START -->
# Orchestrator Instructions

> Read by the orchestrator only — workflow routing, session management, and completion-report format for running this project's AI Scrum team. No spawned subagent needs this file: each spawn receives its own instruction/rules/memory paths directly in its prompt. Content every role needs (Mode, Agent File Integrity, PR Approval Rule) lives in `{{ROOT_FILE}}`. **Agent Roster also stays in `{{ROOT_FILE}}`, not here** — it is project-mutable (per-project instruction paths, lean prototype rosters) and must survive `sync devkit`/`update project`, unlike everything in this file, which is always devkit-verbatim.

---

## Orchestrator Startup — Security Baseline

At workflow start, before the first issue/PR read or GitHub mutation, load the `agent-security` skill: read `.mt-agent-devkit/skills/agent-security/SKILL.md` in full (by path when the provider has no verified native skill discovery). Per its part C, read `{{AGENT_DIR_PREFIX}}/agents/rules/Agent_Common_Shell_Safety.md` in full before the first shell write, Git operation or GitHub mutation. Record the load as `**Security Skill:** agent-security` in the workflow's pipeline state file when it keeps one; a resumed run re-reads the skill if its session no longer holds it. This is an orchestrator read, never a read-manifest entry: workers already receive parts A and B through the generated blocks in their Common file.

**PO execution setting (every workflow).** At workflow start, after the security load and before the first PO touchpoint, resolve `po_execution` once with `python .mt-agent-devkit/scripts/project_settings.py po_execution`. It reads the project-owned `.mt-agent-devkit/project_settings.json` (`init` creates it with `subagent`; `sync` never overwrites it). An absent file or key resolves to `subagent`; an unrecognised value resolves to `subagent` and the script reports it once on stderr: relay that report to the user and never guess the intended value. Pin the result as `**PO Execution:** <subagent | orchestrator>` in the workflow's pipeline state file when it keeps one. A resumed run uses its pinned value and never re-reads the setting, so a mid-sprint change never flips a run halfway. `subagent` (the default) spawns the Product Owner as before. `orchestrator` lets the orchestrator act as PO for the activities the workflows name, loading the same `po-*` skills and owning the PO record and memory for that activity. **Accepted trade-off:** in `orchestrator` mode one actor both merges and records acceptance. That is acceptable only because the per-AC evidence producer stays independent (QA, or a spawned PO when QA is the implementer), Plan Sprint always spawns a PO, and every scope change after Stage 1 starts (defer, split or any AC body edit) goes to the user. Opt in knowingly.

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
| `workflow help` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Workflow_Guide.md` |
| `continue sprint` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Sprint_Workflow.md` |
| `start story ST-XXXXXX` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Start_Story_Workflow.md` |
| `resume story ST-XXXXXX` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Resume_Story_Workflow.md` |
| `refine sprint` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Refine_Sprint_Workflow.md` |
| `plan next sprint` / `plan sprint` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Plan_Sprint_Workflow.md` |
| `create stories` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Create_Stories_Workflow.md` |
| `refine prototype` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Refine_Prototype_Workflow.md` |
| `sync devkit` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Sync_Devkit_Workflow.md` |

Sprint and Start Story workflows share pipeline stages — see `{{AGENT_DIR_PREFIX}}/agents/workflows/Shared_Pipeline_Stages.md`.
<!-- SHARED-END -->
