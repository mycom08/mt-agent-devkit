# Orchestrator Instructions

> Read by the orchestrator only — workflow routing, session management, and completion-report format for running the devkit's own AI Scrum team. No spawned subagent needs this file: each spawn receives its own instruction/rules/memory paths directly in its prompt. Content every role needs (Project Overview, Agent Roster, PR Approval Rule) lives in `CLAUDE.md`.

---

## Orchestrator Startup

Before doing anything else, read the following files to understand the project context:

1. `.claude/agents/working/context/Project_Priming_Bootstrap.md` — project overview, glossary, architecture, and current state
2. `version.txt` — current devkit version

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

## Token-Trace Log (devkit-internal only — deliberately not mirrored to `templates/`)

**This section is the sole home of the trace convention.** No agent rules file carries it: the directive
travels in the spawn prompt, not via a rule an agent has to fetch. That is deliberate — a trace must
account for the agent's own pre-work reads, which happen before any rule could be read, so any agent-side
placement is either circular (on-demand) or charges every spawn for a convention most spawns never use
(bootstrap; measured, and it did not improve the traces). Never write a spawn prompt that asks for a trace
without including the block below — an agent that is not given the format will not produce one.

**Why devkit-only.** Observability for our own team's spawn cost, not a designed target-project feature —
`Agent_Common_template.md` does not carry it and neither does any template. Intentional
`Project_Priming_Read_On_Demand.md §15`-style divergence.

> **Two similarly-named directories — do not confuse them.** `token-trace_sprint/` holds the per-story
> trace **output** written by agents and is gitignored; it accumulates over a sprint and is cleared at
> sprint end. `tokentrace/` (no hyphen) holds the **tooling** — `token_cost.sh` and its README — and is
> committed. The `_sprint` suffix exists to keep the two apart at a glance.

### What you paste into the spawn/resume prompt

Include this verbatim when you want a trace from a spawned or resumed pipeline agent (Developer,
Technical Lead, QA, Product Owner, Business Analyst, UI/UX Designer):

> Before reporting back, write a step trace to
> `.claude/agents/working/token-trace_sprint/<StoryID>_<RoleTag>_steps_done.md` (`RoleTag`: `dev`, `TL`,
> `qa`, `po`, `ba`, `uiux` — never share a file across roles or stories; gitignored, never commit).
> Format:
> ```markdown
> # <StoryID> — <Role> Step Trace
>
> **Session:** spawn | resume
> **Round:** <1 for first entry; increment per loop-back>
> **Steps:** <count of step lines below>
>
> - Step 1: <what you did> — ~<N> tokens approx (<why, e.g. "read Agent_Common_Bootstrap.md + own rules + memory">)
> - Step 2: <what you did> — ~<N> tokens approx
> ...
> **Estimated total:** ~<sum of the step values above — add them up; do not estimate the total separately>
> **Actual total (orchestrator-reported):** <left blank — the orchestrator fills this in>
> ```
> Base each estimate on a visible proxy (files read, tool calls made, comment length written) — never a
> guess pulled from nowhere, and never present a step estimate as exact; you have no introspective access
> to your real per-step usage. Your estimates will run well under the orchestrator-reported actual, which
> also includes per-turn fixed overhead (system prompt, tool schemas, injected reminders), your own output
> and reasoning tokens, and any retried or failed calls — none of which are visible to you. That gap is
> expected; don't spend tokens re-deriving or apologising for it.

**Why the `Session:` field matters.** Spawn-vs-resume is the largest single cost lever you have — a resumed
round skips all pre-work reads and re-establishes no context, and has measured several times cheaper per
step than a cold spawn. `CLAUDE.md`'s resume-over-spawn rule depends on it; this field is what makes it
verifiable rather than assumed.

### What you do after the agent completes

Append the real `subagent_tokens` figure to the same file — the one real number in it; every line above is
the agent's own approximation.

**Record the reported figure verbatim, and label what it covers.** On a **resumed** session the reported
`subagent_tokens` has been observed to be a session-lifetime cumulative, not the cost of that call alone.
Never silently write a subtracted figure as if it were reported. Write both, labelled:

```md
**Actual total (orchestrator-reported):** <figure exactly as reported> (session-cumulative | per-call)
**This round (derived):** <cumulative minus the prior round's recorded figure — omit on round 1>
```

If the completion report does not make clear which of the two it is, write `(unlabelled)` rather than
guessing. A derived number presented as a measurement is worse than an honest gap. Treat
`subagent_tokens` as unresolved in general: rounds have reported 70,652 / 77,975 / 77,274 where round 3
made zero tool calls and still came in lower than round 2, so it is neither per-call nor strictly
cumulative. Do not derive from it beyond the labelled subtraction above.

---

## Harness Benchmark Runs

Trigger: user says **"run harness benchmark"** (aliases: "benchmark the harness", "A/B the harness")

Read `.claude/agents/working/enhancement/Harness_Benchmark_Guide.md` and follow it. It covers baseline choice, story selection, the four kinds of state that survive a branch checkout and contaminate the second arm, the runbook, and the traps in reading the result.

Devkit-internal, like the trace convention above. **Never give this file to a spawned agent** — an agent that knows it is being benchmarked changes what it reads. The agent gets its arm's issue and the trace block, nothing else.

---

## Orchestrator Working Record

**Location:** `.claude/agents/working/working-record/Orchestrator_Working_Record.md` — gitignored, same folder and rewrite-in-place snapshot format as agent working records (see `Agent_Common_Bootstrap.md` for the full spec: **Completed / In Progress / Impediments** overwritten in place each write, not appended alongside the prior entry).

**Retention:** keep only the **3 most recent entries** — the retention unit is a distinct piece of work, not a calendar day. Most entries are keyed `**Story:** ST-XXXXXX`; an entry with no single owning story (an `apply retros` batch, an `update project` run, a multi-story sprint stage) is keyed by that workflow name and date instead, e.g. `**Story:** apply retros — 2026-07-30`. Delete older entries before writing a new one. Enforced cap is **≤ 10,000 characters** (`wc -c`), not a line count. Apply the same inclusion test as `Agent_Common_Bootstrap.md`: *would the next session take a different action if this line were missing?*

**Blockers & Watch-outs** (own section, ≤ 5 lines): sprint-scoped conditions too transient for memory and too cross-cutting for one entry — carries forward across rewrites until resolved or sprint end, same as `Agent_Common_Bootstrap.md`.

**When to update (rewrite the current entry in place, or start a new one for a new piece of work):**
- **On workflow or stage completion** — after `analyze`, `init project`, `update project`, an `apply retros` batch, a `build software` stage, or a devkit sprint stage finishes, log what was done (deliverables, paths, versions bumped, PR/story refs).
- **On explicit close** — if the user says "end session" or "wrap up", finalize the current entry before ending, even if no stage completed since the last write.

**Trigger:** user says **"report working status"** (aliases: "status report", "daily status"). No agents are spawned — read the record directly and summarize the most recent entry to the user (include earlier retained entries only if asked for more history).

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
| `build software <idea>` | — | End-to-end workflow: analyze idea, plan repo structure, split docs per repo, initialise repos, and wire the AI Scrum team (Stages 1–3 available; Stages 4–5 in a future release) |
| `apply retros [label]` | `process retros` | Scan community retro contribution Issues (label `retro:contribution`), prioritise the signals, let you pick which to apply, edit the templates, and bump the version once |
| `audit agent files` | — | Scan the devkit's own agent instruction/rules/workflow corpus for cross-file duplication, contradictions, and dead references (Tier A detection only); write a timestamped report and apply only user-approved findings on a dedicated branch |

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
    ├── context/Project_Priming_Bootstrap.md
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
    ├── context/Project_Priming_Bootstrap.md
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

Applies the current local devkit templates to the target project using the same merge strategy as `sync devkit` — but reads from local files instead of GitHub. Uses `changes.json` to resolve only the files that changed between the project's installed version and the current devkit version, with automatic full-scan fallback if a version entry is missing.

Read `.claude/agents/workflows/Update_Project_Workflow.md` for the complete pipeline before executing.

---

## Build Software Workflow

Trigger: user says **"build software \<idea\>"**

The text after the trigger keyword is the user's idea. If omitted, the workflow asks the user for a one-line description before starting.

End-to-end workflow that takes a software idea from raw description through to initialised repositories with a wired AI Scrum team:

- **Stage 1** — Runs the full `analyze` workflow; produces all analyst documents in `/result/analyst/`
- **Stage 2** — Orchestrator reads `architecture.md` and produces `/result/build/repo_structure.md` (repo decision + table)
- **Stage 3** — Parallel agents split `implementation_roadmap.md` and `architecture.md` per repo; full summary docs copied to all repos
- **Stages 4–5** — Repo initialisation and Scrum team wiring (implemented in ST-000003)

Pipeline state is stored in `.claude/agents/tmp/build_software_state.md`. Running `build software` when the state file exists automatically resumes from the last completed stage.

Read `.claude/agents/workflows/Build_Software_Workflow.md` for the complete pipeline before executing.

---

## Apply Retros Workflow

Trigger: user says **"apply retros"** or **"process retros"** (optionally followed by a label, e.g. `apply retros sprint-3`).

Maintainer workflow that scans community retro contribution Issues on `mycom08/mt-agent-devkit` (label `retro:contribution`), aggregates and prioritises the signals, lets the user pick which to apply, edits the relevant templates directly, and bumps the version once for the whole batch — then archives and closes the processed Issues.

- Default scope is **all** open `retro:contribution` Issues. If a label is supplied, only Issues carrying both that label and `retro:contribution` are scanned.
- Items are ordered most-worth-applying first: critical `[failure]` guardrails, then token/efficiency reductions, then workflow-correctness fixes, then recurring signals, then clarity tweaks.
- Only template files under `.claude/agents/templates/` count toward `changes.json`; devkit-internal workflow edits do not.

Read `.claude/agents/workflows/Apply_Retros_Workflow.md` for the complete pipeline before executing.

---

## Audit Agent Files Workflow

Trigger: user says **"audit agent files"**

Devkit-internal maintainer workflow that scans the devkit's own agent instruction/rules/workflow corpus (`.claude/agents/templates/`, `.claude/agents/workflows/`, `.claude/agents/working/`) for Tier A findings only: cross-file duplication (byte-identical and role-parallel), contradictions, and dead or orphaned references. Spawns a general-purpose subagent to perform the scan so the corpus text never enters the orchestrator's own context. Writes a single timestamped report and applies **only** user-approved findings — per-finding approval, never a whole-report accept — on a dedicated branch with a git-diff-scoped revert path.

**Not an agent role.** There is no `auditor_instructions.md` and no roster entry — this workflow is reached purely through this trigger row, the same pattern `analyze` already uses.

Read `.claude/agents/workflows/Audit_Agent_Files_Workflow.md` for the complete pipeline before executing.

---

## Sprint Workflows (Devkit)

The devkit runs its own sprint workflows using the AI Scrum team under `.claude/agents/working/`. Trigger routing:

| Trigger | File |
|---|---|
| `continue sprint` | `.claude/agents/working/workflows/Sprint_Workflow.md` |
| `start story ST-XXXXXX` | `.claude/agents/working/workflows/Start_Story_Workflow.md` |
| `refine sprint` | `.claude/agents/working/workflows/Refine_Sprint_Workflow.md` |
| `plan next sprint` | `.claude/agents/working/workflows/Plan_Sprint_Workflow.md` |
| `create stories` | `.claude/agents/working/workflows/Create_Stories_Workflow.md` |
| `resume story ST-XXXXXX` | `.claude/agents/working/workflows/Resume_Story_Workflow.md` |

> `workflow help` (without further context) shows the devkit command reference above, not the sprint guide. If the user asks for sprint workflow help, read `.claude/agents/working/workflows/Workflow_Guide.md` and present it.
