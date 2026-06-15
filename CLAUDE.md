# mt-agent-devkit — Claude Code Instructions

## Project Overview

A devkit that injects a complete AI Scrum team setup into any project. It provides two workflows of its own: **Analyst** (idea-to-plan analysis) and **Init Project** (scaffold the AI Scrum team into a target project). All sprint execution workflows live in the generated `CLAUDE.md` that `init project` places into the target project.

**Devkit source:** https://raw.githubusercontent.com/YOUR_ORG/mt-agent-devkit/main

> Update this URL to your actual GitHub raw content base URL before running `init project`. It is embedded into every target project so they can run `update agents` without needing the devkit.

---

## Agent Roster

Each specialized agent must read its instruction file before starting any work.

| Agent | Instruction File |
|---|---|
| Technical Lead | `.claude/agents/templates/instructions/technical_lead_instructions_template.md` |
| Developer | `.claude/agents/templates/instructions/developer_instructions_template.md` |
| QA | `.claude/agents/templates/instructions/qa_instructions_template.md` |
| Product Owner | `.claude/agents/templates/instructions/product_owner_instructions_template.md` |
| Business Analyst | `.claude/agents/templates/instructions/business_analyst_instructions_template.md` |

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

**Agent observations (optional):** After the 5 bullets, an agent may append an `**Observations:**` section listing any workflow friction it encountered — unclear instructions, gaps in the rules, edge cases not covered. One line per item. The orchestrator appends each observation to the `Observations:` field in the pipeline state file, prefixed with the agent role (e.g., `[Developer] <observation>`). Agents should only report genuine friction, not commentary on their own work.

---

## Workflow Help

Trigger: user says **"workflow help"**

No agents are spawned. The orchestrator prints the following reference directly to the user.

---

### mt-agent-devkit — Available Commands

This devkit has three workflows of its own. All sprint execution workflows (`continue sprint`, `start story`, `plan sprint`, etc.) are injected into your target project by `init project` — they do not exist here.

| Command | Alias | What it does |
|---|---|---|
| `workflow help` | — | Show this reference |
| `analyze <requirement>` | `analyze requirement: <text>` | Analyse a project idea from scratch — produces business, technical, and planning documents plus diagrams |
| `init project [path]` | `init project` | Scaffold a complete AI Scrum team setup into a target project (prompts for mode) |
| `update project [path]` | `update project` | Apply latest local devkit templates to an already-initialized target project (same logic as `sync devkit` but uses local files) |

---

### Modes

| Mode | When to use |
|---|---|
| **github** (default) | Project has GitHub Issues, PRs, and Actions. Full integration. |
| **strict** | No GitHub/MCP required. Local repo only. Stories and docs stored locally under `.claude/agents/` (gitignored). No pushes to remote — you control all merges. |

`init project` asks which mode you want. The choice is written to the generated `CLAUDE.md` as `**Mode:** strict` or `**Mode:** github` and drives all workflow behavior in the target project.

---

### Typical first-time flow — GitHub mode

```
1. analyze <your idea>
   └─ Produces: summary.md, architecture.md, implementation_roadmap.md,
                business_requirements.md, testing_plan.md, diagrams/

2. init project <path/to/your/project>
   └─ Select: github
   └─ Injects: CLAUDE.md, agent instructions, rules, memory files, working records

3. In your project — open Claude Code and use:
   plan next sprint     → plan the first sprint (creates GitHub Issues)
   continue sprint      → run the full sprint pipeline
   start story ST-XXXXX → run a single story
   refine sprint        → refine backlog before a sprint
```

### Typical first-time flow — Strict mode

```
1. analyze <your idea>                   (optional)

2. init project <path/to/your/project>
   └─ Select: strict
   └─ Injects: CLAUDE.md (mode: strict), agent files (all gitignored)
   └─ Creates: .claude/agents/docs/ structure + story_counter.txt

3. In your project — open Claude Code and use:
   create stories       → create stories as local MD files
   plan next sprint     → plan sprint from local backlog
   continue sprint      → run the full sprint pipeline
                          (auto-creates sprint-N-dev branch; you merge it when done)
   start story ST-XXXXX → run a single story
   refine sprint        → refine backlog before a sprint
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

Scaffolds these files into the target project. The exact structure depends on the selected mode.

**GitHub mode:**
```
<project>/
├── CLAUDE.md                          ← Mode: github + sprint workflow commands
├── .gitignore                         ← .claude/agents/tmp/ + /result/ added
└── .claude/agents/
    ├── context/Project_Priming.md
    ├── instructions/                  ← 5 agent instruction files
    ├── rules/                         ← Story standard + per-role rules
    ├── memory/                        ← Blank agent memory files (5 files)
    ├── working-record/                ← Blank working records (5 files)
    └── workflows/                     ← Sprint workflow files
```

**Strict mode:**
```
<project>/
├── CLAUDE.md                          ← Mode: strict + sprint workflow commands
├── .gitignore                         ← .claude/agents/ (entire folder) + /result/ added
└── .claude/agents/                    ← entirely gitignored
    ├── context/Project_Priming.md
    ├── instructions/                  ← 5 agent instruction files
    ├── rules/                         ← Story standard + per-role rules + Strict_Mode_Story_Guide.md
    ├── memory/                        ← Blank agent memory files (5 files)
    ├── working-record/                ← Blank working records (5 files)
    ├── workflows/                     ← Sprint workflow files
    └── docs/                          ← All agent-generated data (stories, reviews, sprints)
        ├── stories/                   ← ST-XXXXXX.md files
        ├── sprints/                   ← Sprint overview files
        ├── reviews/                   ← Local review-record files (replaces PRs)
        └── story_counter.txt          ← Auto-increment ID counter (starts at 0)
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

Scaffolds a complete AI Scrum team setup into the target project by adapting `.claude/agents/templates/CLAUDE_template.md` and all supporting agent files.

Read `.claude/agents/workflows/Init_Project_Workflow.md` for the complete pipeline before executing.

---

## Update Project Workflow

Trigger: user says **"update project"** or **"update project [path]"**

The optional `[path]` argument is the absolute path to an already-initialized target project. If omitted, the workflow asks the user.

Applies the current local devkit templates to the target project using the same merge strategy as `update agents` — but reads from local files instead of GitHub. Uses `changes.json` to resolve only the files that changed between the project's installed version and the current devkit version, with automatic full-scan fallback if a version entry is missing.

Read `.claude/agents/workflows/Update_Project_Workflow.md` for the complete pipeline before executing.

---

## PR Approval Rule

GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.
