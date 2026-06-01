# Authorization Service — Claude Code Instructions

## Project Overview

Go-based authorization service delivering an ABAC (Attribute-Based Access Control) feature.
Canonical project context: `.claude/agents/context/PROJECT_PRIMING.md`

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

1. Story ID + what was done (e.g., "ST-000025 — PR #86 opened")
2. Key outcome (approved / blocked / passed / failed)
3. PR or commit reference if applicable
4. Any blockers or open items
5. Next action required (if any)

Detailed activity logs go in the agent's Working Record — not in the orchestrator message. The orchestrator relays a brief status update to the user after each stage.

---

## Sprint Workflow

Trigger: user says **"continue sprint"** or **"/sprint"**

The orchestrator runs the [Shared Pipeline Stages](#shared-pipeline-stages) for each `status:ready` story in sequence. After Stage 4 of each story, PO promotes the next `status:ready` story if applicable. Pipeline completes when no more `status:ready` stories exist.

### Pipeline State

The orchestrator maintains `.claude/agents/tmp/sprint_pipeline_state.md` to support resumption after unexpected termination.

**On pipeline start — always check this file first:**
- If the file **exists** → read it and resume from the recorded story and stage
- If the file **does not exist** → start fresh from Stage 1 of the next `status:ready` story

**State file format:**
```markdown
# Sprint Pipeline State
**Story:** ST-XXXXXX
**Stage:** <0 | 1 | 2 | 3 | 4>
**Implementer:** <Developer | Technical Lead | QA | Business Analyst>
**Loop Impl→Reviewer:** <count>
**Loop Impl→QA:** <count>
**Sessions:**
- impl_session: <agentId or empty>
- reviewer_session: <agentId or empty>
- qa_session: <agentId or empty>
- po_session: <agentId or empty>
**Updated:** YYYY-MM-DDTHH:MM
```

**Write rules:** Create/overwrite at Stage 0 entry of each new story. Update `Stage` + `Updated` after each transition. Update `Sessions` on spawn only. Update loop counts at each retry cycle start. Delete after final story is closed.

### Sprint Pipeline Rules
- Each stage must complete before the next starts
- Loop limit: max 3 Impl→Reviewer or Impl→QA cycles per story before escalating to the user
- **Session reuse** — always resume an existing session before spawning
- Report pipeline status to the user after each stage
- If any agent is blocked, stop and report to the user before continuing

---

## Start Story Workflow

Trigger: user says **"start story ST-XXXXXX"** or **"/story ST-XXXXXX"**

The orchestrator runs the [Shared Pipeline Stages](#shared-pipeline-stages) for the specified story only. **Pipeline stops after Stage 4 — PO does NOT promote the next story.**

### Stage Entry Check (run before anything else)

Read the story's current GitHub label and route:

| Story label | Entry point |
|---|---|
| `status:ready` or `status:in-progress` | Stage 0 — Implementer Routing |
| `status:review` | Stage 2 — Review |
| `status:testing` | Stage 3 — QA Validation |
| `status:done` | Stop — story is already closed; notify user |

> If the story label is missing or unrecognised, stop and notify the user before proceeding.

### Start Story Pipeline Rules
- Targets only the story specified in the trigger command
- Loop limit: max 3 Impl→Reviewer or Impl→QA cycles before escalating to the user
- **Session reuse** — always resume an existing session before spawning
- **Pipeline stops after Stage 4 completes for the targeted story**

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
6. **If story AC passed** → QA runs the full Newman automation suite to check for regressions (see QA Rules §8)
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

Trigger: user says **"refine sprint"** or **"/refine-sprint"**

Read `.claude/agents/workflows/Refine_Sprint_Workflow.md` for the complete pipeline before executing.

---

## Plan Next Sprint Workflow

Trigger: user says **"plan next sprint"** or **"/plan-sprint"**

Read `.claude/agents/workflows/Plan_Sprint_Workflow.md` for the complete pipeline before executing.

---

## Analyst Workflow

Trigger: user says **"analyze requirement: \<brief description\>"** or **"/analyze \<brief description\>"**

The text after the trigger keyword is the initial requirement context passed to the BA agent. Example:
> `/analyze users should be able to define custom ABAC policies via a UI`

Read `.claude/agents/workflows/Analyst_Workflow.md` for the complete pipeline before executing.

---

## PR Approval Rule

GitHub blocks self-approval. Always use `gh pr comment <number>` to post review verdicts — never `gh pr review --approve`.
