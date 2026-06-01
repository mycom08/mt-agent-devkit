# Plan Next Sprint Workflow

Triggered by: `"plan next sprint"` or `"/plan-sprint"` in CLAUDE.md

**Sprint Capacity:** 60 points (update this value to change capacity)

---

## Stage 1 — Current Sprint Verification (PO)

1. **Spawn** Product Owner agent; save its `agentId` as `po_session`
2. PO reads its standard instruction files (`product_owner_instructions.md` + memory + rules)
3. PO checks the active sprint:
   - Read `Product_Backlog.md` to identify the current sprint
   - Read the current `Sprint_N_Overview.md`
   - Check GitHub Issues: confirm every sprint story has `status:done`
4. **If NOT done** → PO reports which stories are still open; orchestrator notifies user and **stops**
5. **One-Sprint-at-a-Time Guard:** PO also checks whether a `Sprint_{N+1}_Overview.md` draft already exists. If it does → orchestrator notifies user and **stops**
6. **If done** → proceed to Stage 2

**Completion report:** PO returns max 5 bullets — current sprint status, any open stories, guard check result.

---

## Stage 2 — Next Sprint Planning (PO)

1. **Resume** PO via `po_session` (spawn new if session expired)
2. PO reviews planning documents:
   - `ABAC_Implementation_Roadmap.md` — next sprint's planned stories, points, dependency graph
   - `Product_Backlog.md` — all `status:backlog` and `status:ready` items
3. PO selects stories up to **60 points** capacity, respecting dependency order from the roadmap
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
2. **Spawn or resume** each required agent **in parallel** (reuse existing sessions):
   - Track sessions as `tl_session`, `ba_session`, `dev_session`, `qa_session` as needed
3. Each agent reads `PO_questions.md`, locates their assigned questions, fills in the `A:` field inline — no separate file
4. Each agent saves the file and signals completion to the orchestrator (max 5-bullet summary)
5. Orchestrator confirms all `[TBD]` fields are filled → **resume PO** via `po_session` with notification that answers are ready
6. **Loop limit:** Max 3 question cycles. If questions remain unresolved after cycle 3 → orchestrator reports to user and **stops**

---

## Stage 4 — Sprint Plan Finalization (PO)

1. **Resume** PO via `po_session` (spawn new if session expired)
2. PO reviews all answers in `PO_questions.md`; if anything is still unclear → orchestrator notifies user and **stops**
3. PO creates `Sprint_{N+1}_Overview.md` under `docs/feature/<feature_name>/plan/` (follow existing Sprint Overview format)
4. PO updates `Product_Backlog.md`: add new sprint section with selected stories; set sprint status to `🔲 Planned`
5. PO creates GitHub Issues for any stories without issues (follow `STORY_STANDARD_PO.md` §13):
   - Labels: `status:backlog` + `feature:abac` + `sprint-N` + `phase-N` (create the `sprint-N` label first if it doesn't exist)
   - Use `--body-file` pattern per STORY_STANDARD_PO.md §15
6. PO deletes `.claude/agents/tmp/PO_questions.md` if it exists
7. PO updates Working Record

**Completion report:** PO returns max 5 bullets — sprint name, stories selected + total points, GitHub issue links, backlog updated.

---

## Pipeline Rules

- **One sprint at a time** — guard check in Stage 1; stop if next-sprint draft already exists
- **Session reuse** — always resume an existing session before spawning
- **Parallel agents** — when multiple agents must answer questions, spawn/resume them in a single message simultaneously
- **Dependency order** — stories selected must satisfy the roadmap dependency graph; no story enters the sprint if its dependency is not yet `status:done`
- **Loop limit** — max 3 question-answer cycles before escalating to user
- **Completion reports** — each agent returns max 5 bullets; details go in Working Records
- **Stop conditions** — current sprint not done; next sprint draft already exists; questions unresolved after 3 cycles; scope decision requires user judgment
