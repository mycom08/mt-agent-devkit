# mt-agent-devkit — Claude Code Instructions

## Orchestrator Reference

The orchestrator (this top-level session) must read `.claude/agents/working/instructions/orchestrator_instructions.md` before executing any workflow — it carries the Orchestrator Startup sequence, all workflow trigger tables (devkit + sprint), session management, working-record rules, and completion-report format. No spawned subagent needs to read it; each spawn receives its own instruction/rules/memory paths directly in its prompt.

---

## Project Overview

A devkit that injects a complete AI Scrum team setup into any project. It provides three workflows of its own: **Analyst** (idea-to-plan analysis), **Init Project** (scaffold the AI Scrum team into a target project), and **Build Software** (end-to-end workflow from idea analysis through repo initialisation). All sprint execution workflows live in the generated `CLAUDE.md` that `init project` places into the target project.

**Devkit source:** https://raw.githubusercontent.com/mycom08/mt-agent-devkit/main

---

## Agent Roster

Each specialized agent must read its instruction file before starting any work.

| Agent | Instruction File |
|---|---|
| Technical Lead | `.claude/agents/working/instructions/technical_lead_instructions.md` |
| Developer | `.claude/agents/working/instructions/developer_instructions.md` |
| QA | `.claude/agents/working/instructions/qa_instructions.md` |
| Product Owner | `.claude/agents/working/instructions/product_owner_instructions.md` |
| Business Analyst | `.claude/agents/working/instructions/business_analyst_instructions.md` |
| UI/UX Designer | `.claude/agents/working/instructions/ui_ux_designer_instructions.md` |

Agent memory, rules, working records, and context live under `.claude/agents/working/`.

---

## PR Approval Rule

GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.
