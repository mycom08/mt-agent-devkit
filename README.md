# mt-agent-devkit

A Claude Code agent devkit that installs multi-agent sprint workflows into any software project. It provides a team of five specialized AI agents — Technical Lead, Developer, QA, Product Owner, and Business Analyst — that collaborate to plan, implement, review, test, and close stories end-to-end.

---

## What it does

| Capability | How |
|---|---|
| **Multi-agent sprint pipeline** | Spawns and coordinates agents across Implementation → Review → QA → Closure stages |
| **Role-separated workflows** | Each agent has its own instructions, rules, memory, and working record |
| **Story lifecycle management** | Tracks stories from `backlog` through `done` — via GitHub Issues (default) or local MD files (strict mode) |
| **Sprint planning and refinement** | Plan and refine backlog stories before execution |
| **Feature analysis** | BA-led elicitation and planning for new requirements |
| **Session continuity** | Agents resume mid-session; pipeline state survives restarts |
| **Project initialization** | Scaffolds all agent files into any target project in one command |

---

## Modes

| Mode | When to use |
|---|---|
| **github** (default) | Project has GitHub Issues, PRs, and Actions. Full integration. |
| **strict** | No GitHub or MCP required. Local repo only. Stories stored locally under `.claude/agents/` (gitignored). You control all merges — agents never push to remote. |

`init project` asks which mode you want before writing any files.

---

## Quick start — adding agents to your project

Run this inside mt-agent-devkit to scaffold agent files into another project:

```
init project /absolute/path/to/your-project
```

Or omit the path and the workflow will ask:

```
init project
```

The workflow will:
1. Ask whether you want **github** or **strict** mode
2. Scan your project (language, framework, key directories, existing CI/CD, test tooling)
3. Generate customized agent files adapted to your tech stack
4. Show you every file it will create or modify
5. Ask for your confirmation before writing anything
6. Write all files and display next steps

**After init completes**, open Claude Code in your project and type:

```
workflow help
```

This shows all available commands and the recommended order to use them.

---

## Devkit workflows

Type any of the following in the Claude Code chat **inside mt-agent-devkit**. These two workflows exist in the devkit itself — not in your target project.

### Workflow Help
```
workflow help
```
Shows all available commands and a quick-start guide.

### Analyze Requirement
```
analyze <brief description>
```
Elicits, analyses, and plans a requirement from scratch. Produces a `/result/analyst/` folder with documents and diagrams suitable for any development team:

| File | For |
|---|---|
| `summary.md` | **Start here** — human-readable overview, architecture diagram, delivery plan, open items |
| `architecture.md` | Component design, data handling, alternatives, diagrams |
| `implementation_roadmap.md` | Phases, sprints, stories with AC, dependency graph, release criteria, risks |
| `business_requirements.md` | Functional + non-functional requirements, constraints, assumptions |
| `testing_plan.md` | Unit / integration / E2E strategy |
| `spec.md` | Full formalised specification |
| `elicitation_notes.md` | Full Q&A log from the interview |
| `diagrams/*.puml` | PlantUML source files for workflow and sequence diagrams |

### Init Project
```
init project [path]
```
Scaffolds all agent files into a target project. Prompts for mode (github / strict). Safe by default — asks for confirmation before writing.

---

## Sprint workflows (available after `init project`)

These commands are injected into your target project's `CLAUDE.md` by `init project`. Run them from inside your project. Type `workflow help` in your project to see this guide at any time.

### Recommended order

```
1. create stories       ← draft and save stories to the backlog
2. plan next sprint     ← assign backlog stories to a sprint, create sprint plan
3. refine sprint        ← raise and resolve questions before work starts
4. continue sprint      ← execute all ready stories end-to-end
```

Repeat steps 3–4 each sprint. Use `start story` to run a single story outside the full sprint loop.

### All commands

#### Create Stories
```
create stories
```
Claude acts as PO — drafts stories from your description, you confirm, then stories are saved to the backlog. In GitHub mode they become GitHub Issues; in strict mode they are written as local MD files under `.claude/agents/docs/stories/`.

#### Plan Next Sprint
```
plan next sprint [feature]
```
PO verifies the current sprint is done, selects backlog stories up to sprint capacity, resolves open questions with TL, and publishes the sprint plan. In GitHub mode creates/labels Issues; in strict mode writes a local sprint overview file.

#### Refine Sprint
```
refine sprint
```
Each implementer reviews their assigned stories, posts questions for TL or PO, TL and PO answer in parallel, implementers confirm, PO moves resolved stories to `ready`.

#### Continue Sprint
```
continue sprint
```
Runs the full pipeline for every `ready` story: Implementation → Review → QA → Closure. In strict mode, each story gets its own branch off `sprint-N-dev`; when all stories are done you are notified to merge `sprint-N-dev` into your branch.

#### Start Story
```
start story ST-XXXXXX
```
Runs the pipeline for a single story. Picks up at the correct stage based on the story's current status.

#### Resume Story
```
resume story ST-XXXXXX
```
Unblocks a story after you have provided the missing information. Validates all required input is present before restarting the pipeline.

---

## Agent roles

| Agent | Responsibility |
|---|---|
| **Technical Lead** | Architecture, API specs, code review, PR approval |
| **Developer** | Story implementation, branch management |
| **QA** | Acceptance criteria validation, test scenarios, regression suite |
| **Product Owner** | Backlog ownership, scope gating, story closure, AC sign-off |
| **Business Analyst** | Requirements elicitation, use-case analysis, cost-benefit assessment |

---

## Story status flow

```
backlog → ready → in-progress → review → testing → done
                                          ↑
                               blocked (waiting on input)
                               resolved via "resume story ST-XXXXXX"
```

In GitHub mode, status is tracked via `status:*` issue labels. In strict mode, status is a `**Status:**` field in the story MD file. Status values are identical in both modes.

---

## Folder structure (after `init project`)

### GitHub mode

```
your-project/
├── CLAUDE.md                              ← Mode: github + orchestrator instructions
├── .gitignore                             ← .claude/agents/tmp/ added
└── .claude/agents/
    ├── context/Project_Priming.md         ← project cheat sheet for all agents
    ├── instructions/                      ← one instruction file per agent role (5 files)
    ├── rules/                             ← story standards + per-role rules
    ├── memory/                            ← agent memory files (5 files)
    ├── working-record/                    ← agent working records (5 files)
    ├── workflows/                         ← all sprint workflow definitions
    └── templates/CLAUDE_TEMPLATE.md
```

### Strict mode

```
your-project/
├── CLAUDE.md                              ← Mode: strict + orchestrator instructions
├── .gitignore                             ← .claude/agents/ (entire folder) added
└── .claude/agents/                        ← entirely gitignored — never committed
    ├── context/Project_Priming.md
    ├── instructions/                      ← one instruction file per agent role (5 files)
    ├── rules/                             ← story standards + per-role rules
    ├── memory/                            ← agent memory files (5 files)
    ├── working-record/                    ← agent working records (5 files)
    ├── workflows/                         ← all sprint workflow definitions
    ├── templates/CLAUDE_TEMPLATE.md
    └── docs/                             ← all agent-generated data (gitignored)
        ├── stories/                      ← ST-XXXXXX.md files
        ├── sprints/                      ← sprint overview files
        ├── reviews/                      ← local review records (replaces PRs)
        └── story_counter.txt             ← auto-increment ID counter
```

---

## Prerequisites

### Both modes
- [Claude Code](https://claude.ai/code) CLI or desktop app

### GitHub mode only
- [GitHub CLI](https://cli.github.com/) (`gh`) — authenticated and pointing at your project's repo
- A GitHub repository with Issues enabled

### Strict mode
- No additional tools required — works with a local git repo only

---

## Devkit structure

```
mt-agent-devkit/
├── CLAUDE.md                          ← orchestrator triggers and pipeline rules
├── README.md
└── .claude/
    └── agents/
        ├── context/PROJECT_PRIMING.md ← sample priming (authorization service)
        ├── memory/                    ← sample memory files
        ├── rules/                     ← all rule files (story standards, per-role, strict-mode guide)
        ├── working-record/            ← sample working records
        ├── workflows/                 ← all workflow definitions
        │   ├── Analyst_Workflow.md
        │   ├── Sprint_Workflow.md
        │   ├── Start_Story_Workflow.md
        │   ├── Shared_Pipeline_Stages.md
        │   ├── Plan_Sprint_Workflow.md
        │   ├── Refine_Sprint_Workflow.md
        │   ├── Create_Stories_Workflow.md
        │   ├── Resume_Story_Workflow.md
        │   ├── Init_Project_Workflow.md
        │   ├── Token_Probe_Workflow.md
        │   └── Workflow_Guide.md
        ├── templates/
        │   └── CLAUDE_TEMPLATE.md     ← sprint workflow template for target projects
        └── *_instructions.md          ← per-role instruction files (5 files)
```

The sample files are adapted from a Go-based authorization service. When you run `init project`, the workflow replaces all project-specific content with content matched to your target project's tech stack.
