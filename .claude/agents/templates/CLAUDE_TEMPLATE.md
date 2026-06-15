# {{PROJECT_NAME}} — Claude Code Instructions

## Project Overview

{{PROJECT_DESCRIPTION}}
Canonical project context: `.claude/agents/context/Project_Priming.md`

**Mode:** {{MODE}}
**Devkit source:** {{DEVKIT_SOURCE_URL}}
**Devkit version:** {{DEVKIT_VERSION}}

> Agents must read `**Mode:**` at the start of every workflow. When `Mode: strict`, follow strict-mode paths throughout (local MD files, local branches — no GitHub/MCP calls). See `.claude/agents/rules/Strict_Mode_Story_Guide.md` for the full operation substitution reference.

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

## Agent File Integrity

**Agents and the orchestrator must never create, modify, or delete agent infrastructure files during sprint work or any other workflow.**

Protected paths — read-only for all agents and the orchestrator at all times:

| Path | Contents |
|---|---|
| `.claude/agents/*_instructions.md` | Role instruction files |
| `.claude/agents/rules/` | All rules files |
| `.claude/agents/workflows/` | All workflow files |
| `.claude/agents/context/` | Project priming and document index |
| `.claude/agents/devkit_version.txt` | Installed devkit version stamp |

Writable paths during normal work:

| Path | Who writes | What |
|---|---|---|
| `.claude/agents/memory/` | Each agent | Their own memory file only |
| `.claude/agents/working-record/` | Each agent | Their own working record only |
| `.claude/agents/tmp/` | Orchestrator | Pipeline state files |
| `.claude/agents/docs/` | All agents | Stories, sprints, reviews (strict mode only) |

**The only operation that may update protected paths is `update agents`**, which is triggered explicitly by the user and handled exclusively by `Update_Agents_Workflow.md`. No agent, no workflow, and no orchestrator logic may modify these files for any other reason — including fixes, improvements, or adjustments discovered during sprint work.

If an agent identifies an error or improvement needed in a rules or workflow file, it must report it to the user as an observation — never self-correct by editing the file.

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

Quick-reference routing table. The orchestrator reads the trigger from the user's message and dispatches accordingly.

| Trigger | Handled by |
|---|---|
| `continue sprint` | Sprint Workflow — inline below |
| `start story ST-XXXXXX` | Start Story Workflow — inline below |
| `refine sprint` | `.claude/agents/workflows/Refine_Sprint_Workflow.md` |
| `plan next sprint` / `plan sprint` | `.claude/agents/workflows/Plan_Sprint_Workflow.md` |
| `create stories` | `.claude/agents/workflows/Create_Stories_Workflow.md` |
| `resume story ST-XXXXXX` | `.claude/agents/workflows/Resume_Story_Workflow.md` |
| `workflow help` | `.claude/agents/workflows/Workflow_Guide.md` |
| `analyze <requirement>` | `.claude/agents/workflows/Analyst_Workflow.md` |
| `update agents` | `.claude/agents/workflows/Update_Agents_Workflow.md` |

---

## Sprint Workflow

Trigger: user says **"continue sprint"**

The orchestrator runs the [Shared Pipeline Stages](#shared-pipeline-stages) for each `status:ready` story in sequence. After Stage 4 of each story, PO promotes the next `status:ready` story if applicable. Pipeline completes when no more `status:ready` stories exist.

**If `Mode: strict` — sprint branch setup (run once before first story):**
1. Identify the sprint name from the first `status:ready` story's `**Sprint:**` field (e.g., `sprint-1`)
2. Check if the sprint dev branch exists: `git branch --list sprint-N-dev`
   - Exists → `git checkout sprint-N-dev`
   - Missing → `git checkout -b sprint-N-dev` (from the user's current branch)
3. Store `Sprint Branch: sprint-N-dev` in the pipeline state file

**If `Mode: strict` — story discovery** (replaces `gh issue list --label "status:ready"`):
- Glob `.claude/agents/docs/stories/*.md`, read each file, filter by `**Status:** ready`
- Sort by `**Sprint:**` then by story ID (ascending) to preserve expected order

### Pipeline State

The orchestrator maintains `.claude/agents/tmp/sprint_pipeline_state.md` to support resumption after unexpected termination.

**On pipeline start — always check this file first:**
- If the file **exists** → read it and resume from the recorded story and stage
- If the file **does not exist** → start fresh from Stage 1 of the next `status:ready` story

**State file format:**
```markdown
# Sprint Pipeline State
**Story:** ST-XXXXXX
**Stage:** <0 | 1 | 2 | 3 | 4 | 5>
**Implementer:** <Developer | Technical Lead | QA | Business Analyst>
**Type:** <behavioral | non-behavioral>
**Feature:** <feature-name or none>
**Phase:** <phase-number or none>
**Sprint:** sprint-N
**Sprint Branch:** sprint-N-dev
**Story Branch:** story/<id>-<slug>
**Docs SHA:** <git short SHA captured at Stage 0>
**Loop Impl→Reviewer:** <count>
**Loop Impl→QA:** <count>
**Sessions:**
- impl_session: <agentId or empty>
- reviewer_session: <agentId or empty>
- qa_session: <agentId or empty>
- po_session: <agentId or empty>
**Updated:** YYYY-MM-DDTHH:MM
**Observations:**
```

> `Sprint Branch` and `Story Branch` are strict-mode only fields. In GitHub mode write `Sprint Branch: n/a` and `Story Branch: n/a`.

**Write rules:** Create/overwrite at Stage 0 entry of each new story. Update `Stage` + `Updated` after each transition. Update `Sessions` on spawn only. Update loop counts at each retry cycle start. Append one-line bullets to `Observations:` whenever the orchestrator makes a judgment call not covered by the workflow. Delete after final story is closed.

### Sprint Pipeline Rules
- Each stage must complete before the next starts
- Loop limit: max 3 Impl→Reviewer or Impl→QA cycles per story before escalating to the user
- **Session reuse** — always resume an existing session before spawning
- Report pipeline status to the user after each stage
- If any agent is blocked, stop and report to the user before continuing
- **Agent files are read-only** — no agent or orchestrator step may write to instructions, rules, workflows, or context files; see [Agent File Integrity](#agent-file-integrity)

---

## Start Story Workflow

Trigger: user says **"start story ST-XXXXXX"**

The orchestrator runs the [Shared Pipeline Stages](#shared-pipeline-stages) for the specified story only. **Pipeline stops after Stage 4 — PO does NOT promote the next story.**

### Stage Entry Check (run before anything else)

**If `Mode: github`** — read the story's current GitHub label and route:

| Story label | Entry point |
|---|---|
| `status:ready` or `status:in-progress` | Stage 0 — Implementer Routing |
| `status:review` | Stage 2 — Review |
| `status:testing` | Stage 3 — QA Validation |
| `status:blocked` | Stop — notify user to run `resume story ST-XXXXXX` |
| `status:done` | Stop — story is already closed; notify user |

**If `Mode: strict`** — read `**Status:**` field from `.claude/agents/docs/stories/ST-XXXXXX.md` and route using the same table (status values match — see `Strict_Mode_Story_Guide.md`).

> If the status is missing or unrecognised, stop and notify the user before proceeding.

### Start Story Pipeline Rules
- Targets only the story specified in the trigger command
- Loop limit: max 3 Impl→Reviewer or Impl→QA cycles before escalating to the user
- **Session reuse** — always resume an existing session before spawning
- **Pipeline stops after Stage 4 completes for the targeted story**
- **Agent files are read-only** — no agent or orchestrator step may write to instructions, rules, workflows, or context files; see [Agent File Integrity](#agent-file-integrity)

---

## Shared Pipeline Stages

Used by both Sprint Workflow and Start Story Workflow. Session IDs are maintained by the orchestrator across stages.

### Stage 0 — Implementer Routing

Read the story's `**Assigned:**` field from the GitHub issue body and store `Implementer` in the pipeline state file. This determines which agent runs Stage 1 and which agent reviews in Stage 2.

| `**Assigned:**` value | Stage 1 agent | Stage 2 reviewer | Stage 3 validator |
|---|---|---|---|
| `Developer` | Developer | Technical Lead | QA |
| `Technical Lead` | Technical Lead | Developer (peer review) | QA |
| `QA` | QA | Technical Lead | Skipped — PO validates AC directly |
| `Business Analyst` | Business Analyst | Technical Lead | QA |

> If the `**Assigned:**` field is missing or contains an unrecognised value, stop and notify the user before proceeding.

### Stage 1 — Implementation
1. **Spawn** the agent matching the `Implementer` role; save its `agentId` as `impl_session`
2. Agent reads its own instruction files, memory, and rules
3. Agent checks GitHub for the assigned story (`status:in-progress` or next `status:ready` story)
4. Agent implements, opens PR (if applicable), updates working record
5. On completion → proceed to Stage 2

### Stage 2 — Review
1. **Spawn** the reviewer agent based on the routing table in Stage 0; save its `agentId` as `reviewer_session`
   - Default: **Technical Lead** reviews
   - Exception: if `Implementer` is `Technical Lead` → **Developer** does peer review
2. Reviewer reads its own instruction files, memory, and rules
3. Reviewer reviews PR (use `gh pr comment` — GitHub blocks self-approval via `gh pr review --approve`)
4. **If changes requested** → resume Implementer via `SendMessage` to `impl_session` with reviewer feedback (spawn new if expired); on Implementer completion **resume Reviewer via `reviewer_session` to re-review** (spawn new if expired)
5. **If approved** → proceed to Stage 3

### Stage 3 — QA Validation
1. **If `Implementer` is `QA`** → skip this stage; proceed directly to Stage 4
2. **Spawn** QA agent; save its `agentId` as `qa_session`
3. QA reads `qa_instructions.md` + `QA_Memory.md` + `QA_Rules.md`
4. QA validates story acceptance criteria, runs test scenarios, checks regression risk
5. **If story AC issues found** → resume Implementer via `SendMessage` to `impl_session` with QA findings (spawn new if expired); on Implementer completion **resume QA via `SendMessage` to `qa_session`** to revalidate (spawn new if expired)
6. **If story AC passed** → QA runs the full automation suite to check for regressions (see QA Rules §8)
   - **If automation fails** → QA reports regression failures as a story comment; resume Implementer via `impl_session` to fix (spawn new if expired); on completion resume QA to revalidate (counts toward loop limit)
   - **If automation passes** → resume Implementer via `SendMessage` to `impl_session` (spawn new if expired) and instruct Implementer to:
     - Merge the PR into the feature branch (or master)
     - Delete the remote dev branch: `git push origin --delete <branch-name>` — do **not** delete the local branch
     - Switch local branch to the feature branch (or master)
     - Pull from remote to sync (`git pull origin <target-branch>`)
7. On merge confirmed → proceed to Stage 4

### Stage 4 — PO Story Closure
1. **Spawn** Product Owner agent; save its `agentId` as `po_session` (resume via `po_session` if still active from a previous story in this sprint)
2. PO reads `product_owner_instructions.md` + `Product_Owner_Memory.md` + `Product_Owner_Rules.md`
3. PO ticks AC checkboxes on the story issue, updates label to `status:done`, closes story
4. **Sprint Workflow only:** PO updates backlog — promotes next `status:ready` story if applicable
5. **Start Story Workflow:** pipeline ends here — PO does NOT promote the next story

---

## Refine Sprint Workflow

Trigger: user says **"refine sprint"**

Read `.claude/agents/workflows/Refine_Sprint_Workflow.md` for the complete pipeline before executing.

---

## Plan Next Sprint Workflow

Trigger: user says **"plan next sprint"** or **"plan sprint"**

Read `.claude/agents/workflows/Plan_Sprint_Workflow.md` for the complete pipeline before executing.

---

## Analyst Workflow

Trigger: user says **"analyze requirement: \<brief description\>"** or **"analyze \<brief description\>"**

The text after the trigger keyword is the initial requirement context. Example:
> `analyze users should be able to invite team members and manage their permissions`

Output is written to `/result/analyst/`. The key deliverable for developers is `summary.md` — a plain-language overview with architecture diagrams, key decisions, and implementation roadmap.

Read `.claude/agents/workflows/Analyst_Workflow.md` for the complete pipeline before executing.

---

## PR Approval Rule

**If `Mode: github`:** GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.

**If `Mode: strict`:** No PRs. The reviewer writes their verdict to the local review-record file at `.claude/agents/docs/reviews/ST-XXXXXX_review.md` and appends a summary comment to the story MD `## Comments` section. See `Strict_Mode_Story_Guide.md` for the review-record format.
