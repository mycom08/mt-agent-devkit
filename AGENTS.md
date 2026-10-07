# mt-agent-devkit — Multi-Provider Instructions

## Project Context

At the start of every repository task read
`.mt-agent-devkit/context/Project_Priming_Bootstrap.md` in full. Fetch only
triggered sections from the canonical on-demand context. Ordinary repository
work uses neutral priming and does not start the orchestrator workflow.

## Provider Selection

Before a workflow, read `.mt-agent-devkit/contracts/Provider_Contract.md`.
Inspect actual enabled tools and validate their mapping with
`.mt-agent-devkit/scripts/provider_context.py`. Load only the selected adapter:

- Claude: `.claude/harness/Provider_Adapter.md`
- Antigravity: `.antigravity/harness/Provider_Adapter.md`
- Codex: `.codex/harness/Provider_Adapter.md`

Unknown, ambiguous, or unsupported capability mappings block workflows before
state writes or spawning. Neutral repository tasks remain available. Directory
names do not prove discovery or capabilities. Pass selected provider and runtime
bindings explicitly to each role; never load every adapter together.

## Orchestrator Reference

Only the top-level orchestrator reads
`.mt-agent-devkit/instructions/orchestrator_instructions.md` when the user asks
to start or resume a workflow/story. Normal checks, questions, and ordinary edits
do not trigger it. Spawned agents receive their own shared role paths directly.

## Project Overview

mt-agent-devkit scaffolds an AI Scrum team into target projects. Internal harness
sources live under `.mt-agent-devkit/`; target templates remain unchanged under
`.claude/agents/templates/` until Phase 2. Existing init/update/build commands and
provider-local scaffold helpers remain operational with the same target output.

**Devkit source:** https://github.com/mycom08/mt-agent-devkit

## Agent Harness Efficiency Work

Read `docs/reviews/Stage_Specific_Read_Profiles_Proposal.md`, then
`docs/Agent_Workflow_Test_Strategy.md` for harness efficiency/routing/testing work.
Read the token-efficiency analysis only for baseline evidence, and
`docs/Template_Test_Strategy.md` for test-infrastructure changes.

## Agent Roster

Every specialized agent reads its shared role instruction before work.

| Agent | Instruction File |
|---|---|
| Technical Lead | `.mt-agent-devkit/instructions/technical_lead_instructions.md` |
| Developer | `.mt-agent-devkit/instructions/developer_instructions.md` |
| QA | `.mt-agent-devkit/instructions/qa_instructions.md` |
| Product Owner | `.mt-agent-devkit/instructions/product_owner_instructions.md` |
| Business Analyst | `.mt-agent-devkit/instructions/business_analyst_instructions.md` |
| UI/UX Designer | `.mt-agent-devkit/instructions/ui_ux_designer_instructions.md` |

## PR Approval Rule

GitHub blocks self-approval. Post verdicts through `gh pr comment`; never
`gh pr review --approve`. Independent review/QA gates remain mandatory.
