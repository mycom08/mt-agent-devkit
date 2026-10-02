# mt-agent-devkit — Antigravity Instructions

## Project Context

When you first begin work in this repository during a session, read `.antigravity/agents/working/context/Project_Priming_Bootstrap.md` once for the minimum project context. Reuse that context for subsequent prompts and tasks in the same session; do not reread the bootstrap for every user message. Follow its routing table and read sections from `Project_Priming_Read_On_Demand.md` only when the current task matches a listed trigger.

This one-time, lightweight project-priming read is required when repository work starts; it does not trigger the full orchestrator startup sequence.

---

## Orchestrator Reference

The orchestrator (this top-level session) must read `.antigravity/agents/working/instructions/orchestrator_instructions.md` only when the user explicitly asks to start or resume an Antigravity workflow, or asks to start or resume work on a story. It carries the Orchestrator Startup sequence, all workflow trigger tables (devkit + sprint), session management, working-record rules, and completion-report format.

Do not read the orchestrator instructions for normal repository tasks, including project-status checks, locating files, inspecting code, answering questions, or making ordinary edits and fixes. Working in this repository or under `.antigravity/` does not by itself trigger the orchestrator workflow. No spawned subagent needs to read the orchestrator instructions; each workflow spawn receives its own instruction/rules/memory paths directly in its prompt.

---

## Project Overview

A devkit that injects a complete AI Scrum team setup into any project. It provides three workflows of its own: **Analyst** (idea-to-plan analysis), **Init Project** (scaffold the AI Scrum team into a target project), and **Build Software** (end-to-end workflow from idea analysis through repo initialisation). All sprint execution workflows live in the generated `AGENTS.md` that `init project` places into the target project.

**Devkit source:** https://github.com/mycom08/mt-agent-devkit

---

## Agent Harness Efficiency Work

When working on agent context efficiency, stage-specific read profiles, or
agent workflow testing, read in this order:

1. `docs/reviews/Stage_Specific_Read_Profiles_Proposal.md`
2. `docs/Agent_Workflow_Test_Strategy.md`

Read `docs/reviews/Agent_Harness_Token_Efficiency_Analysis.md` only when
supporting evidence or baseline measurements are needed. Read
`docs/Template_Test_Strategy.md` when changing test infrastructure.

---

## Agent Roster

Each specialized agent must read its instruction file before starting any work.

| Agent | Instruction File |
|---|---|
| Technical Lead | `.antigravity/agents/working/instructions/technical_lead_instructions.md` |
| Developer | `.antigravity/agents/working/instructions/developer_instructions.md` |
| QA | `.antigravity/agents/working/instructions/qa_instructions.md` |
| Product Owner | `.antigravity/agents/working/instructions/product_owner_instructions.md` |
| Business Analyst | `.antigravity/agents/working/instructions/business_analyst_instructions.md` |
| UI/UX Designer | `.antigravity/agents/working/instructions/ui_ux_designer_instructions.md` |

Agent memory, rules, working records, and context live under `.antigravity/agents/working/`.

---

## PR Approval Rule

GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.
