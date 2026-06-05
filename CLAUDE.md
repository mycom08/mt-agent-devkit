# mt-agent-devkit — Claude Code Instructions

## Project Overview

A devkit that injects a complete AI Scrum team setup into any project. It provides two workflows of its own: **Analyst** (idea-to-plan analysis) and **Init Project** (scaffold the AI Scrum team into a target project). All sprint execution workflows live in the generated `CLAUDE.md` that `init project` places into the target project.

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

1. What was done
2. Key outcome (completed / blocked / failed)
3. Files or documents written (if applicable)
4. Any blockers or open items
5. Next action required (if any)

Detailed activity logs go in the agent's Working Record — not in the orchestrator message. The orchestrator relays a brief status update to the user after each stage.

---

## Workflow Help

Trigger: user says **"workflow help"**

No agents are spawned. The orchestrator prints the following reference directly to the user.

---

### mt-agent-devkit — Available Commands

This devkit has two workflows of its own. All sprint execution workflows (`continue sprint`, `start story`, `plan sprint`, etc.) are injected into your target project by `init project` — they do not exist here.

| Command | Alias | What it does |
|---|---|---|
| `workflow help` | — | Show this reference |
| `analyze <requirement>` | `analyze requirement: <text>` | Analyse a project idea from scratch — produces business, technical, and planning documents plus diagrams |
| `init project [path]` | `init project` | Scaffold a complete AI Scrum team setup into a target project |

---

### Typical first-time flow

```
1. analyze <your idea>
   └─ Produces: summary.md, architecture.md, implementation_roadmap.md,
                business_requirements.md, testing_plan.md, diagrams/

2. init project <path/to/your/project>
   └─ Injects: CLAUDE.md (with sprint workflows), agent instructions,
               rules, memory files, working records

3. In your project — open Claude Code and use:
   plan sprint       → plan the first sprint
   continue sprint   → run the full sprint pipeline
   start story ST-XXXXX  → run a single story
   refine sprint     → refine backlog before a sprint
```

---

### What `analyze` produces

Output is written to `/result/analyst/`. Start with `summary.md`.

| File | Contents |
|---|---|
| `summary.md` | Human-readable overview — background, architecture diagram, delivery plan, open items |
| `architecture.md` | Architecture choices, component design, diagrams |
| `implementation_roadmap.md` | Phases, sprints, stories with AC, dependency graph, release criteria, risks |
| `business_requirements.md` | Functional & non-functional requirements, constraints, assumptions |
| `testing_plan.md` | Testing strategy: unit, integration, E2E |
| `diagrams/*.puml` | PlantUML source files for workflow and sequence diagrams |

> Output is generic — usable by any team, not only teams using this devkit.

---

### What `init project` produces

Scaffolds these files into the target project:

```
<project>/
├── CLAUDE.md                          ← Sprint workflow commands for your project
└── .claude/agents/
    ├── context/PROJECT_PRIMING.md     ← Project cheat sheet for agents
    ├── instructions/                  ← One file per agent role (5 files)
    ├── rules/                         ← Story standard + per-role rules
    ├── memory/                        ← Blank agent memory files (5 files)
    ├── working-record/                ← Blank working records (5 files)
    ├── workflows/                     ← Sprint workflow files
    └── templates/CLAUDE_TEMPLATE.md  ← Template used to generate CLAUDE.md
```

---

### Agent roles

| Agent | Responsible for |
|---|---|
| Developer | Story implementation, branch management, PRs |
| Technical Lead | Architecture, code review, PR approval |
| QA | Acceptance validation, test scenarios, regression suite |
| Product Owner | Backlog, story AC, sprint planning, story closure |
| Business Analyst | Requirements elicitation, spec writing |

---

## Analyst Workflow

Trigger: user says **"analyze requirement: \<brief description\>"** or **"analyze \<brief description\>"**

The text after the trigger keyword is the initial requirement context. Example:
> `analyze users should be able to define custom ABAC policies via a UI`

Output is written to `/result/analyst/`. Produces business, technical, and planning documents plus diagrams — suitable for any development team, not just teams using this devkit.

Read `.claude/agents/workflows/Analyst_Workflow.md` for the complete pipeline before executing.

---

## Init Project Workflow

Trigger: user says **"init project"** or **"init project [path]"**

The optional `[path]` argument is the absolute path to the target project. If omitted, the workflow asks the user.

Scaffolds a complete AI Scrum team setup into the target project by adapting `.claude/agents/templates/CLAUDE_TEMPLATE.md` and all supporting agent files.

Read `.claude/agents/workflows/Init_Project_Workflow.md` for the complete pipeline before executing.

---

## PR Approval Rule

GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.
