---
name: mt-agent-devkit Orchestrator
description: Workflows for scaffolding and managing the mt-agent-devkit AI Scrum team
---

# mt-agent-devkit Orchestrator

This skill allows Antigravity to act as the orchestrator for the `mt-agent-devkit`.

## Devkit Commands

You can run the following workflows when the user triggers them:

| Command | What it does |
|---|---|
| `analyze <requirement>` | Analyzes a project idea from scratch using `.antigravity/agents/workflows/Analyst_Workflow.md` |
| `init project [path]` | Scaffolds a complete AI Scrum team setup into a target project using `.antigravity/agents/workflows/Init_Project_Workflow.md` |
| `update project [path]` | Applies latest local devkit templates to an already-initialized target project using `.antigravity/agents/workflows/Update_Project_Workflow.md` |
| `build software <idea>` | End-to-end workflow using `.antigravity/agents/workflows/Build_Software_Workflow.md` |

## Subagent Primitive Mapping

When orchestrating workflows in Antigravity, use the `define_subagent`, `invoke_subagent` and `send_message` tools.

Example mapping:
1. Orchestrator reads target agent's instructions (e.g. `Developer_Instructions.md`)
2. Orchestrator uses `define_subagent` to register the agent (e.g. `TypeName: "Developer"`), passing the instruction file content into `system_prompt`.
3. Orchestrator calls `invoke_subagent` to spawn the agent for the specific task.
4. **Workspace:** Set `Workspace: "share"` in the `invoke_subagent` call so all subagents can view and modify the exact same repository files.
5. **Asynchronous Execution:** After calling `invoke_subagent` or `send_message`, you MUST stop executing tools and wait for a reply message in your inbox. Do not proceed to the next stage until the subagent explicitly messages you.
6. When you need to resume an agent with feedback, use the `send_message` tool passing the agent's `ConversationId`. Wait for the agent to reply asynchronously via the inbox.

**Important:** Do NOT spawn an agent using Claude XML tags. Always use `define_subagent` followed by `invoke_subagent` and wait for a reply.
