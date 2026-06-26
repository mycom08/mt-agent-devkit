<!-- Included by: templates/github/workflows/Plan_Sprint_Workflow_template.md, templates/strict/workflows/Plan_Sprint_Workflow_template.md -->

<!-- SHARED-START -->
# Plan Next Sprint Workflow

Triggered by: `"plan next sprint [feature-name]"` or `"/plan-sprint [feature-name]"` in CLAUDE.md

**Sprint Capacity:** 60 points (update this value to change capacity)

---

## Stage 0 — Sprint Context

Before spawning any agent, the orchestrator resolves the sprint context.

1. Check if the trigger included a feature name argument (e.g., `/plan-sprint payments`)
   - **Argument provided** → set `feature_name = <argument>`; verify `docs/feature/<feature_name>/plan/` exists — if not, stop and notify user
   - **No argument** → ask the user: "Which feature is this sprint for? Enter the feature name (e.g., `payments`) or `none` for a non-feature sprint."
2. Store `feature_name` (or `none`) — this drives all path and label decisions in every subsequent stage

---

## Stage 1 — Current Sprint Verification (PO)

1. **Spawn** Product Owner agent (**model: sonnet**); save its `agentId` as `po_session`; pass `feature_name`
2. PO reads its standard instruction files (`product_owner_instructions.md` + memory + rules)
3. PO checks the active sprint:
   - **Feature sprint** (`feature_name` is set): read `docs/feature/<feature_name>/plan/Product_Backlog.md` to identify the sprint marked `🔄 In Progress`; read its `Sprint_N_Overview.md`
   - **Non-feature sprint** (`feature_name: none`):
     - **GitHub mode:** run `gh issue list --label "status:in-progress" --label "status:review" --label "status:testing"` to identify stories in the current sprint; if empty, fall back to `gh issue list --state closed --label "status:done" --limit 1 --json number,title,labels` and read the `sprint-N` label from the most recent done story
     - **Strict mode:** glob `.claude/agents/docs/stories/*.md`, filter for `**Status:**` values of `in-progress`, `review`, or `testing` to find the active sprint; if none found, filter for `**Status:** done` and read the `**Sprint:**` field from the most recently created story (highest ID) — that is the current sprint N
4. Confirm every story in the current sprint has `status:done`:
   - **GitHub mode:** check GitHub Issues
   - **Strict mode:** read all story MD files for the identified sprint and confirm all have `**Status:** done`
5. **If NOT done** → PO reports which stories are still open; orchestrator notifies user and **stops**
6. **One-Sprint-at-a-Time Guard** (feature sprint only): check whether `Sprint_{N+1}_Overview.md` already exists in `docs/feature/<feature_name>/plan/`. If it does → orchestrator notifies user and **stops**
7. **If done** → proceed to Stage 2

**Completion report:** PO returns max 5 bullets — current sprint status, any open stories, guard check result.

---

## Stage 2 — Next Sprint Planning (PO)

1. **Resume** PO via `po_session` (spawn new if session expired)
2. PO locates planning inputs based on context:
   - **Feature sprint**: glob `docs/feature/<feature_name>/plan/*Roadmap*.md` to find the roadmap file; read `docs/feature/<feature_name>/plan/Product_Backlog.md` for all `status:backlog` items
   - **Non-feature sprint**:
     - **GitHub mode:** run `gh issue list --label "status:backlog" --state open` as the backlog source
     - **Strict mode:** glob `.claude/agents/docs/stories/*.md`, filter by `**Status:** backlog`; sort by story ID (ascending)
3. PO selects stories up to **60 points** capacity:
   - **If roadmap exists**: respect the roadmap's dependency graph and planned sprint order
   - **If no roadmap**: order candidates by priority label (`Must-Have` first, then `Should-Have`, then `Nice-to-Have`)
4. **If all AC and scope are clear** → skip to Stage 4
5. **If questions remain** → PO creates `.claude/agents/tmp/PO_questions.md` using the format below; proceed to Stage 3

**PO_questions.md format:**
```markdown
# PO Questions — Sprint [N+1] Planning
**Date:** YYYY-MM-DD
**Status:** Open

---

## Q1 — [Topic]
**Assigned to:** Technical Lead | Business Analyst | Developer | QA
**Q:** [Question text]
**A:** [TBD — awaiting answer]
```

**Completion report:** PO returns max 5 bullets — stories selected, total points, questions file created (yes/no), agents needed.

---

## Stage 3 — Question Resolution (other agents)

1. Orchestrator reads `PO_questions.md` to identify which agents have assigned questions
2. **Spawn or resume** each required agent **in parallel** (**model: sonnet** for new spawns) (reuse existing sessions):
   - Track sessions as `tl_session`, `ba_session`, `dev_session`, `qa_session` as needed
3. Each agent reads `PO_questions.md`, locates their assigned questions, fills in the `A:` field inline — no separate file
4. Each agent saves the file and signals completion to the orchestrator (max 5-bullet summary)
5. Orchestrator confirms all `[TBD]` fields are filled → **resume PO** via `po_session` with notification that answers are ready
6. **Loop limit:** Max 3 question cycles. If questions remain unresolved after cycle 3 → orchestrator reports to user and **stops**

---

## Stage 4 — Sprint Plan Finalization (PO)

1. **Resume** PO via `po_session` (spawn new if session expired)
2. PO reviews all answers in `PO_questions.md`; if anything is still unclear → orchestrator notifies user and **stops**
3. PO writes sprint artifacts based on context:
   - **Feature sprint**:
     - Create `docs/feature/<feature_name>/plan/Sprint_{N+1}_Overview.md` (follow existing Sprint Overview format)
     - Update `docs/feature/<feature_name>/plan/Product_Backlog.md`: add new sprint section; mark sprint status as `🔲 Planned`
   - **Non-feature sprint**:
     - **GitHub mode:** GitHub issue labels are the only artifact — no Sprint Overview file needed
     - **Strict mode:** create `.claude/agents/docs/sprints/sprint_N_overview.md` listing selected story IDs, titles, points, and total capacity used
4. PO creates stories for any backlog items that do not yet have a story record:
   - **GitHub mode:** create GitHub Issues following `Story_Standard_PO.md` §13; use `--body-file` pattern per §15; create `sprint-N` label first if it does not exist; apply labels:
     - **Feature story:** `status:backlog` + `feature:<feature_name>` + `phase-N` + `sprint-N`
     - **Non-feature story:** `status:backlog` + `sprint-N`
   - **Strict mode:** for each new story, increment `story_counter.txt`, write `.claude/agents/docs/stories/ST-XXXXXX.md` with `**Status:** backlog`, `**Sprint:** sprint-N`, `**Feature:**` and `**Phase:**` fields set; report file paths to PO
5. PO deletes `.claude/agents/tmp/PO_questions.md` if it exists
6. PO updates Working Record
7. **Workflow review (orchestrator):** check whether `.claude/agents/tmp/plan_observations.md` exists
   - If **exists**: present each observation as a proposed improvement to the user; apply approved changes to this workflow file; delete the file
   - If **does not exist**: no action needed

**Completion report:** PO returns max 5 bullets — sprint name, stories selected + total points, GitHub issue links, artifacts created.

---

## Pipeline Rules

- **Stage 0 first** — sprint context must be resolved before any agent is spawned
- **One sprint at a time** — guard check in Stage 1 (feature sprints only); stop if next-sprint draft already exists
- **Session reuse** — always resume an existing session before spawning
- **Parallel agents** — when multiple agents must answer questions, spawn/resume them in a single message simultaneously
- **Dependency order** — if a roadmap exists, respect its dependency graph; if no roadmap, order by priority label (`Must-Have` → `Should-Have` → `Nice-to-Have`)
- **Loop limit** — max 3 question-answer cycles before escalating to user
- **Completion reports** — each agent returns max 5 bullets; details go in Working Records. Agents may append an optional `**Observations:**` section for workflow friction (unclear instructions, rule gaps, uncovered edge cases); orchestrator appends each item to `plan_observations.md`, prefixed with the agent role
- **Stop conditions** — current sprint not done; next-sprint draft already exists; questions unresolved after 3 cycles; scope decision requires user judgment
- **Observations** — whenever the orchestrator makes a judgment call not covered by this workflow, append a one-line bullet to `.claude/agents/tmp/plan_observations.md` (create the file if it does not exist). These are reviewed at the end of Stage 4.
<!-- SHARED-END -->
