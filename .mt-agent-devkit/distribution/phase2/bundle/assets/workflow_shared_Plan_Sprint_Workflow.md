<!-- Included by: templates/github/workflows/Plan_Sprint_Workflow_template.md, templates/strict/workflows/Plan_Sprint_Workflow_template.md -->

<!-- SHARED-START -->
# Plan Next Sprint Workflow

Triggered by: `"plan next sprint [feature-name]"` or `"/plan-sprint [feature-name]"` in {ENTRYPOINT}

**Sprint Capacity:** 60 points (update this value to change capacity)

---

## Open Topic Check (run first)

Before Stage 0, look for open analysis topics:

- **GitHub mode:** `gh issue list --label "analysis-open-topic" --state open --limit 1000 --json number,title,body,comments`
- **Strict mode:** the files in `{RUNTIME_ROOT}/docs/stories/` with an `**Analysis Open Topic:**` line and `**Status:** blocked`.

None: continue; nothing else changes. One or more: run the Open Topic Reminder section of `.mt-agent-devkit/workflows/Analyze_Requirements_Workflow.md`, and continue only when it says so.

---

## Stage 0 — Sprint Context

Before spawning any agent, the orchestrator resolves the sprint context.

1. Check if the trigger included a feature name argument (e.g., `/plan-sprint payments`)
   - **Argument provided** → set `feature_name = <argument>` (`none` means no feature). **GitHub mode:** no feature folder is required. **Strict mode:** verify `docs/feature/<feature_name>/plan/` exists — if not, stop and notify user
   - **No argument** → ask the user: "Which feature is this sprint for? Enter the feature name (e.g., `payments`) or `none` for a non-feature sprint."
2. Store `feature_name` (or `none`) — this drives all path and label decisions in every subsequent stage

---

## Stage 1 — Current Sprint Verification (PO)

1. **Spawn** Product Owner agent (**policy: standard**); save its `session_handle` as `po_session`; pass `feature_name` and name the `po-plan-sprint` skill in the assignment (**forced spawn:** Plan Sprint always spawns a PO in both `PO Execution` modes and never runs inline; see the PO touchpoint table in the orchestrator instructions)
2. PO reads its standard instruction files (`product_owner_instructions.md` + memory) and loads the `po-core` and `po-plan-sprint` skills (`.mt-agent-devkit/skills/po-plan-sprint/SKILL.md`), plus the skills `po-plan-sprint` requires
2a. **Sprint-label check (before any other planning step):** PO runs `sprint-status` section 6 (open-topic stories are skipped). No violation → continue. One or more → PO returns every violation and stops; the orchestrator reports them to the user and asks whether to continue planning. Continue → resume PO at step 3; otherwise **stop**. Never fix a violation silently: no label (strict mode: story `**Status:**` or `**Sprint:**` field) changes unless the user confirms that change.
3. PO checks the active sprint with the `sprint-status` skill (`.mt-agent-devkit/skills/sprint-status/SKILL.md`): in-flight stories (section 1) and the current sprint number N (section 2)
4. Confirm the current sprint is done (`sprint-status` section 3)
5. **If NOT done** → PO reports which stories are still open; orchestrator notifies user and **stops**
6. **One-Sprint-at-a-Time Guard:** check whether the next sprint is already planned (`sprint-status` section 4). If it is → orchestrator notifies user and **stops**
7. **Roadmap reconciliation backstop** (only a feature with a `plan/` roadmap; lightweight — this is the sprint-planning safety net for AC4, not the primary drain mechanism). If `feature_name` is set, glob `docs/feature/<feature_name>/plan/*Roadmap*.md`. If a roadmap file exists (a `roadmap/` roadmap from Analyze Requirements gets no backstop), for every story it defines, check whether a tracked issue/story already carries that story's `**Roadmap Source:** <roadmap-file> :: Phase N :: <story title>` marker (see the `po-roadmap-drain` skill). The check must confirm the marker exists **anywhere in the tracker, in any status** — a story that was correctly drained and has since moved past `status:backlog` (`ready`/`in-progress`/`done`) is still tracked, not drift:
   - **GitHub mode:** `gh issue list --state all --search "\"<marker>\" in:body" --json number,body` per story — no `--label`/`--state open` filter (a status filter here would report every already-progressed story as false drift). Search is a candidate filter, not a verdict: GitHub's phrase search matches a contiguous token subsequence, not an exact line, so a story whose title is a prefix of another drained story's title can return a false match. For each candidate, confirm the marker appears as an **exact, full line** in that issue's body before treating the story as tracked — an empty result, or a candidate set where none survives the exact-line check, means it's untracked.
   - **Strict mode:** grep `{RUNTIME_ROOT}/docs/stories/*.md` for each story's marker line using a whole-line match (e.g. `grep -Fxq "<marker>"` per file, not a plain substring grep, which has the same prefix-title false-positive risk) — no match means it's untracked.

   If any roadmap-defined story has no matching tracked issue/story, report it to the user as drift **before** proceeding to Stage 2 — this should be rare (the `po-roadmap-drain` authoring-time drain is the primary mechanism; this step only catches a roadmap that got out of sync some other way, e.g. a manual edit). Do not block Stage 2 on this — surface the gap, and if the user confirms, PO drains the missing stories on the spot using the same steps as the `po-roadmap-drain` skill before continuing.
8. **If done** → proceed to Stage 2

**Completion report:** PO returns max 5 bullets (sprint-label violations are listed in full, outside this cap) — current sprint status, any open stories, guard check result.

---

## Stage 2 — Next Sprint Planning (PO)

1. **Resume** PO via `po_session` (spawn new if session expired)
2. PO locates planning inputs based on context:
   - **Feature sprint**:
     - **GitHub mode:** run `gh issue list --label "feature:<feature_name>" --label "status:backlog" --state open --limit 1000 --json number,title,body,labels` as the backlog source, and glob `docs/feature/<feature_name>/plan/*Roadmap*.md` for a roadmap. With no matching story: a `plan/` roadmap continues from that roadmap (drained by Stage 1 step 7); any other feature → report that it has no backlog stories to the user and **stop**, nothing is planned
     - **Strict mode:** glob `docs/feature/<feature_name>/plan/*Roadmap*.md` to find the roadmap file; read `docs/feature/<feature_name>/plan/Product_Backlog.md` for all `status:backlog` items
   - **Non-feature sprint**:
     - **GitHub mode:** run `gh issue list --label "status:backlog" --state open --limit 1000` as the backlog source
     - **Strict mode:** glob `{RUNTIME_ROOT}/docs/stories/*.md`, filter by `**Status:** backlog`; sort by story ID (ascending)
2a. **Roadmap check (feature and non-feature sprints):** PO reads `docs/Project_Roadmap.md` and confirms its Now / Next / Later buckets match the sprint being planned. When a topic changes bucket or a new topic appears, PO edits that topic's one line and `Last updated`, committing straight to the base branch in github mode (per `po-plan-docs`) and locally on `sprint-N-dev` in strict mode. When the file is missing, report it and skip.
3. PO selects stories up to **60 points** capacity:
   - **If a roadmap exists** (for a feature, one under `plan/`): respect the roadmap's dependency graph and planned sprint order
   - **GitHub mode, feature without a `plan/` roadmap** (including an analysed one, roadmap in `roadmap/`): order by `phase-N` label, then `**Depends on:**` (a dependency must be done or in the same sprint), then priority label. The `Story Candidates` table in `roadmap/` is a cross-check only
   - **If no roadmap** (otherwise): order candidates by priority label (`Must-Have` first, then `Should-Have`, then `Nice-to-Have`)
3a. **Multi-repo cross-repo dependency audit** (skip for single-repo projects): before locking the sprint, for every contract/API-spec endpoint the selected stories touch in a sibling repo, verify the owning repo has a **closed, review-scoped** story whose AC actually covers that endpoint — not just a same-named "API contract design" dependency. Surface any gap as a planning blocker the same way other blockers are surfaced (add it to `PO_questions.md` or stop and notify the user, per the severity).
4. **If all AC and scope are clear** → skip to Stage 4
5. **If questions remain** → PO creates `{RUNTIME_ROOT}/tmp/PO_questions.md` using the format below; proceed to Stage 3

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
2. **Spawn or resume** each required agent **in parallel** (**policy: standard** for new spawns) (reuse existing sessions):
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
   - **GitHub mode:** GitHub issue labels are the only artifact, with or without a feature: add `sprint-N` (create the label first if missing) to every selected issue, and replace `status:backlog` with `status:open` (create the label first if missing)
   - **Strict mode, feature sprint:** create `docs/feature/<feature_name>/plan/Sprint_{N+1}_Overview.md` (follow existing Sprint Overview format); update `docs/feature/<feature_name>/plan/Product_Backlog.md`: add new sprint section; mark sprint status as `🔲 Planned`; set `**Status:** open` and `**Sprint:** sprint-N` in every selected story file
   - **Strict mode, non-feature sprint:** create `{RUNTIME_ROOT}/docs/sprints/sprint_N_overview.md` listing selected story IDs, titles, points, and total capacity used; set `**Status:** open` and `**Sprint:** sprint-N` in every selected story file
4. PO creates stories for any backlog items that do not yet have a story record. **GitHub mode:** a feature without a `plan/` roadmap gets none here: only Analyze Requirements Stage 8 creates an analysed feature's stories. Before creating one, obtain the exact existing base branch from the approved sprint plan or ask the user; never infer it from checkout:
   - **GitHub mode:** create GitHub Issues following the `po-write-story` skill with immutable `**Base Branch:** <selected branch>` inside every issue body; use `--body-file` pattern per `Agent_Common_Bootstrap.md §6`; create `sprint-N` label first if it does not exist; apply labels:
     - **Feature story:** `status:open` + `feature:<feature_name>` + `phase-N` + `sprint-N`
     - **Non-feature story:** `status:open` + `sprint-N`
   - **Strict mode:** for each new story, increment `story_counter.txt`, write `{RUNTIME_ROOT}/docs/stories/ST-XXXXXX.md` with `**Status:** open`, `**Sprint:** sprint-N`, `**Feature:**`, `**Phase:**`, and immutable `**Project Base Branch:** <selected branch>` fields set; the execution `**Base Branch:** sprint-N-dev` is recorded only after strict pre-flight verifies it; report file paths to PO
   - **Roadmap-sourced stories:** when a story is drafted from a roadmap doc, echo the roadmap's phase number as a separate `**Roadmap Phase:** Phase N — <theme>` line in the body. The roadmap phase is a global, cross-repo thematic sequence; the `sprint-N` label is this repo's own local execution counter (starting at 1) — the two are independent numbering systems and must not be conflated
5. PO deletes `{RUNTIME_ROOT}/tmp/PO_questions.md` if it exists
6. PO updates Working Record
7. **Workflow review (orchestrator):** check whether `{RUNTIME_ROOT}/tmp/plan_observations.md` exists
   - If **exists**: present each observation as a proposed improvement to the user; apply approved changes to this workflow file; delete the file
   - If **does not exist**: no action needed

**Completion report:** PO returns max 5 bullets — sprint name, stories selected + total points, GitHub issue links, artifacts created.

---

## Pipeline Rules

- **Stage 0 first** — after the Open Topic Check, sprint context must be resolved before any planning agent is spawned
- **One sprint at a time** — guard check in Stage 1 (`sprint-status` section 4); stop if the next sprint is already planned
- **Session reuse** — always resume an existing session before spawning
- **Forced PO spawn** — Stages 1, 2 and 4 spawn/resume a real PO session (`po_session`) whatever the pinned `PO Execution` value; `orchestrator` mode never runs planning inline
- **Parallel agents** — when multiple agents must answer questions, spawn/resume them in a single message simultaneously
- **Dependency order** — respect a roadmap's dependency graph; a GitHub-mode feature without a `plan/` roadmap orders by `phase-N`, `**Depends on:**`, then priority; otherwise priority label (`Must-Have` → `Should-Have` → `Nice-to-Have`)
- **Loop limit** — max 3 question-answer cycles before escalating to user
- **Completion reports** — each agent returns max 5 bullets; details go in Working Records. Agents may append an optional `**Observations:**` section for workflow friction (unclear instructions, rule gaps, uncovered edge cases); orchestrator appends each item to `plan_observations.md`, prefixed with the agent role
- **Stop conditions** — the user declines to continue after sprint-label violations; current sprint not done; next sprint already planned; GitHub mode: a feature with no backlog stories and no `plan/` roadmap; questions unresolved after 3 cycles; scope decision requires user judgment
- **Roadmap reconciliation backstop** — Stage 1 step 7 (features with a `plan/` roadmap only) checks every story the roadmap defines against tracked issues/stories via the `**Roadmap Source:**` marker, before Stage 2 selects candidates. This is a lightweight drift-catcher, not the primary drain mechanism — that happens at roadmap authoring time, see the `po-roadmap-drain` skill. On drift, PO drains the missing stories on the spot rather than blocking the plan.
- **Observations** — whenever the orchestrator makes a judgment call not covered by this workflow, append a one-line bullet to `{RUNTIME_ROOT}/tmp/plan_observations.md` (create the file if it does not exist). These are reviewed at the end of Stage 4.
<!-- SHARED-END -->
