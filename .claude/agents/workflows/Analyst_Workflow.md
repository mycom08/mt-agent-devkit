# Analyst Workflow

Triggered by: `"analyze requirement: <brief description>"` or `"analyze <brief description>"` in CLAUDE.md

The text after the trigger keyword is the user's **initial requirement context**. If no context is provided, the orchestrator asks the user for a one-line description before starting.

**Output folder:** `/result/analyst/`

> **Independence note:** All output documents are written to be useful to any development team — they do not assume the reader is using this devkit. Avoid agent-speak, devkit-specific references, or placeholders in final documents.

---

## Pipeline State

The orchestrator maintains `.claude/agents/tmp/analyst_workflow_state.md` to support resumption after unexpected termination.

**On pipeline start — always check this file first:**
- If the file **exists** → read it and resume from the recorded stage
- If the file **does not exist** → start fresh from Stage 1

**State file format:**
```markdown
# Analyst Workflow State
**Topic:** <brief description of the requirement>
**Stage:** <1 | 2a | 2b | 2c | 2d>
**Question Count:** <N>
**Discussion Cycle:** <0 | 1 | 2>
**Sessions:**
- ba_session: <agentId or empty>
- tl_session: <agentId or empty>
- po_session: <agentId or empty>
- qa_session: <agentId or empty>
- uiux_session: <agentId or empty — only populated when a UI/UX Designer was spawned>
**Updated:** YYYY-MM-DDTHH:MM
```

**Write rules:** Create at Stage 1 entry. Update `Stage` + `Updated` after each transition. Update `Sessions` on spawn only. Update `Question Count` each Q&A turn. **Delete only after Stage 2d closes with no pending user feedback** — the state file (and its saved `tl_session`/`po_session`/`ba_session`/`qa_session`/`uiux_session`) stays alive through the entire post-completion review loop so agents can be resumed for revisions instead of re-spawned.

---

## Stage 1 — Requirements Elicitation (Orchestrator-led, Interactive)

The orchestrator conducts the entire Q&A loop directly using the natural conversation context, which persists across turns for free. **No BA agent is spawned during elicitation.** BA is spawned exactly once at the end of Stage 1 to formalise the spec into documents.

### How the interaction works

1. Orchestrator reads `.claude/agents/business_analyst_instructions.md` to internalise the BA questioning approach and domain knowledge
2. Orchestrator extracts the initial requirement context from the trigger message
3. Orchestrator asks the user **exactly one question** — grounded in the initial context, not generic
4. User answers; orchestrator increments `Question Count` in the state file
5. Orchestrator asks the next question, explicitly building on all prior answers
6. Repeat steps 4–5 until the orchestrator judges it has sufficient information for a complete spec (all features, constraints, open decisions, and non-functional requirements covered)
7. Orchestrator writes the full Q&A log to `/result/analyst/elicitation_notes.md`
8. **Spawn** BA agent (**model: sonnet**); save its `agentId` as `ba_session`
9. BA reads `business_analyst_instructions.md` + its memory files + `elicitation_notes.md`
10. BA writes:
    - `spec.md` — the full elicited specification
    - `business_requirements.md` — structured requirements (functional, non-functional, constraints, assumptions, open items)
11. BA reports completion to the orchestrator (max 5 bullets)
12. Orchestrator updates state to Stage 2a and proceeds

### Stage 1 rules
- **One question per turn** — orchestrator must never ask multiple questions in a single message
- Each question must explicitly build on the user's previous answers
- Orchestrator must not make assumptions or fill in unstated details — ask instead
- Orchestrator writes `elicitation_notes.md` after the final answer, before spawning BA
- BA in steps 9–11 only writes documents — it does not ask the user any further questions

---

## Stage 2 — Multi-agent Analysis & Planning

BA, TL, and PO analyse the spec and engage the user directly with clarifying questions and suggestions. Agents are encouraged to propose better or alternative solutions — not just implement what was literally stated.

### Shared file convention

| File | Writer | Purpose |
|---|---|---|
| `elicitation_notes.md` | Orchestrator (read-only in Stage 2) | Full Q&A log from Stage 1 |
| `spec.md` | BA (read-only after Stage 1) | Full elicited specification |
| `business_requirements.md` | BA | Structured requirements: functional, non-functional, constraints, assumptions, open items |
| `architecture.md` | TL | Architecture choices, component design, data handling, error handling, alternatives considered, and a **Testability Notes** section (test seams, mockable boundaries, contract-test candidates) as technical input for QA's `testing_plan.md`. All diagrams live in `diagrams/` and are referenced by relative link. |
| `testing_plan.md` | QA (sequenced after TL) | Testing strategy: unit, integration, E2E, risk-based prioritisation, environments, entry/exit criteria, acceptance criteria hints |
| `implementation_roadmap.md` | PO | Phased implementation plan: release goal, sprint breakdown, stories with AC in devkit story standard format, dependency graph (linked from `diagrams/`), release criteria, risks |
| `ui_design.md` | UI/UX Designer (conditional — only when the spec names a web/mobile/desktop UI surface) | Screen/component inventory, layout structure, interaction notes. BA/PO reference it from their own docs; they do not author it. |
| `discussion.md` | TL + PO + QA + UI/UX Designer (conditional; shared write) | Questions needing user input and suggestions for the user to consider |
| `summary.md` | TL (Stage 2c) | Human-readable overview: what is being built, architecture diagram (linked from `diagrams/`), key decisions, roadmap table, open items |
| `diagrams/` | TL, PO | Every diagram produced by the pipeline — Mermaid (`.mmd`) and PlantUML (`.puml`) files, one file per diagram |

### Diagram conventions

**Every diagram is a separate file under `diagrams/` — never inline in markdown.** This applies everywhere a diagram appears in the pipeline: `summary.md`'s architecture overview, `architecture.md`'s context/component/data-model diagrams, `implementation_roadmap.md`'s dependency graph, and all sequence/workflow diagrams.

**Use Mermaid (`.mmd` files in `diagrams/`) for:**
- Component and service relationship diagrams (`graph LR`, `graph TD`, `flowchart`)
- Entity relationship diagrams
- State machines
- Dependency graphs
- High-level architecture overview (linked from `summary.md`)

**Use PlantUML (`.puml` files in `diagrams/`) for:**
- API request/response sequence diagrams
- Detailed workflow and process flows
- Deployment and infrastructure diagrams
- Any diagram where PlantUML syntax is significantly clearer than Mermaid

Every diagram file (`.mmd` or `.puml`) must be referenced from the relevant markdown document with a relative link and a brief caption, e.g.:

```markdown
![Core-service Component View](diagrams/core_service_component_view.mmd)
> *Diagram: core_service_component_view.mmd — Core-service internal layering: controllers, domain services, repositories*
```

The agent writing the diagram decides Mermaid vs PlantUML based on what communicates the design most clearly for that specific diagram — the file always lives in `diagrams/` regardless of format.

### `discussion.md` format

Each agent writes under its own named sections. BA does not write to this file.

```markdown
## TL Questions
<!-- Questions TL cannot resolve from the spec alone -->
- QUESTION: <question text>

## TL Suggestions
<!-- Proactive suggestions: better approaches, alternatives, trade-offs -->
- SUGGEST: <suggestion with rationale and trade-offs>

## PO Questions
<!-- Questions PO cannot resolve from the spec alone -->
- QUESTION: <question text>

## PO Suggestions
<!-- Proactive suggestions: scope alternatives, priority trade-offs, MVP adjustments -->
- SUGGEST: <suggestion with rationale and trade-offs>

## QA Questions
<!-- Questions QA cannot resolve from spec.md/business_requirements.md/architecture.md alone -->
- QUESTION: <question text>

## QA Suggestions
<!-- Proactive suggestions: test-strategy improvements, architecture testability gaps -->
- SUGGEST: <suggestion with rationale and trade-offs>

## UI/UX Designer Questions
<!-- Questions UI/UX Designer cannot resolve from spec.md/business_requirements.md alone — only present when UI/UX Designer was spawned -->
- QUESTION: <question text>

## UI/UX Designer Suggestions
<!-- Proactive suggestions: screen/flow simplifications, interaction alternatives -->
- SUGGEST: <suggestion with rationale and trade-offs>
```

Agents omit a section entirely if they have nothing to add to it. The `UI/UX Designer` sections only appear at all when a UI/UX Designer was spawned this Stage 2a.

---

### Stage 2a — Initial Analysis (TL + PO + optional UI/UX Designer parallel, then QA sequenced)

1. **UI layer detection (orchestrator-direct, before any spawn).** `architecture.md` doesn't exist yet at this point — TL writes it *during* this stage — so detection cannot read "repo tech stack." Instead, the orchestrator reads `spec.md` + `business_requirements.md` (already on disk from Stage 1) and decides: does the product name a web/mobile/desktop UI surface (a screen, dashboard, app, GUI, frontend)? This is a judgment call, same class as the mandatory CI/CD question elsewhere in this stage — not a literal keyword match.
   - **If yes** → UI/UX Designer joins the parallel wave (step 2).
   - **If no** → proceed with just TL + PO; skip every UI/UX-Designer-conditional step below for the rest of Stage 2.
2. **Spawn** TL agent (**model: opus**), PO agent (**model: sonnet**), and — only if step 1 detected a UI layer — UI/UX Designer agent (**model: sonnet**) in the **same orchestrator message** — they run in parallel
   - Save TL `agentId` as `tl_session`; save PO `agentId` as `po_session`; if spawned, save UI/UX Designer `agentId` as `uiux_session`
3. TL reads `spec.md` + `business_requirements.md`:
   - Writes `architecture.md` covering: architecture choices, component design, data handling details, error handling strategies, CI/CD & deployment strategy, API-contract strategy, and any alternatives considered. Every diagram (Mermaid `.mmd` or PlantUML `.puml`) is written as a separate file under `diagrams/` and linked from `architecture.md` — never embedded inline.
     - **CI/CD & deployment strategy** covers: CI tooling and per-service CI needs, target environment(s) for CD (e.g. AWS/GCP/self-hosted/undecided), how a merged PR gets from code to a running instance (deploy pipeline shape, not full IaC detail), and what "automation test" means for this project beyond unit tests (real integration/API test scope, not just "we'll add tests later"). This is a **decision to make explicit and hand to PO for roadmap stories**, not something the devkit scaffold already solves — Build Software's generated Dockerfile/docker-compose/CI only bootstrap a local-dev baseline (build, unit test, lint, a stub automation-test job) and never invent a real deploy target on their own.
     - **Mandatory CI/CD question — a carve-out from the "don't interrogate" rule below; this one topic is always asked.** Regardless of what the spec says, TL always writes one scoped question to `discussion.md` under `## TL Questions`: has the user already defined CI and/or CD for this project, or should the devkit default apply? This is a single bounded question, not open-ended interrogation — it doesn't license asking about every other routine infra choice, which still follows the "default and move on" approach below.
       - **If CI is not already defined:** default to **GitHub Actions**. TL documents in `architecture.md` what CI needs to run for each service based on its tech stack (build, unit test, lint — and for a Java REST service, the same job shape Build Software's skeleton generator already produces as a baseline; for any other tech stack, describe the equivalent jobs). PO turns this into an actual roadmap story per the rule below — TL documents the need, it does not write stories directly into `implementation_roadmap.md`.
       - **If CD is not already defined:** default to **GitHub Actions** for the pipeline mechanics, but TL must still ask (same scoped question) whether the user has any infrastructure/cloud target for CD to actually deploy to. If not, TL proactively suggests 2–3 concrete options fitting the architecture (e.g. a managed platform like Fly.io/Render for a simple containerized service, AWS/GCP/Azure for anything needing more control, self-hosted if that fits the team) — written to `discussion.md` under `## TL Suggestions`. If the user still doesn't decide, TL records the deploy target as explicitly unresolved in `architecture.md` — see the PO roadmap rule below for how this becomes a blocked story rather than a silently-dropped Open Item.
     - If the spec doesn't name a deploy target and the mandatory question above doesn't resolve it either, don't block `architecture.md` itself on it: write a reasonable default assumption (e.g. "containerized service; deploy target not yet decided — local Docker Compose is the only environment until one is chosen"). This is about not stalling the *document*, not about skipping the question — that already happened above. For every other routine infra choice beyond CI/CD, continue to just default and note it as an **Open Item** in `summary.md` later, same as any other deferred decision — don't interrogate the user over those.
     - **API-contract strategy** — for every service that exposes an API (REST/gRPC/etc.), explicitly decide and document: is the contract written spec-first (hand-authored OpenAPI/proto before implementation) or code-first (generated from annotations on a running implementation, then committed)? Does the contract need to live as its own versioned artifact, or is in-repo enough? Reason about it the same way as any other architecture choice — e.g. multiple independent clients consuming one API (NFR around independent release cadence) usually justifies a versioned, separately-consumable contract; a single internal-only consumer usually doesn't.
       - **Know the devkit's own downstream behavior, so you don't get contradicted by it silently:** `Build_Software_Workflow.md` Stage 2 automatically splits **any Java REST service** into a companion `<repo-name>-api-spec` repo, unconditionally, regardless of what's decided here — that's a fixed devkit convention, not a TL decision, and it only triggers for Java. If your API-contract reasoning agrees with a dedicated contract artifact, just state that in `architecture.md` (for Java it'll match what Stage 2 does automatically; for non-Java stacks, say explicitly whether the contract should still get its own repo/package even though the devkit won't split it for you). If your reasoning concludes a dedicated contract split is a **poor fit** for this specific project (e.g. Java but trivial/internal-only, single consumer, unlikely to ever need independent versioning), say so explicitly and write it to `discussion.md` under `## TL Suggestions` or `## TL Questions` — don't let the automatic Java split contradict your own stated architecture without at least flagging the mismatch for the user to see at the Stage 2 confirmation gate.
   - Writes a **Testability Notes** section in `architecture.md`: test seams, mockable boundaries, and contract-test candidates the architecture exposes. This is technical input for QA's `testing_plan.md`, not a testing strategy itself — TL no longer writes `testing_plan.md`.
   - **Proactively suggests** better technical solutions or trade-offs the user may not have considered — writes these to `discussion.md` under `## TL Suggestions`
   - Writes unresolvable questions to `discussion.md` under `## TL Questions`
4. PO reads `spec.md` + `business_requirements.md`:
   - Writes `implementation_roadmap.md` (see format below)
   - **Proactively suggests** scope simplifications, MVP trade-offs, or phasing alternatives — writes these to `discussion.md` under `## PO Suggestions`
   - Writes unresolvable questions to `discussion.md` under `## PO Questions`
5. **If UI/UX Designer was spawned (step 1 detected a UI layer):** UI/UX Designer reads `spec.md` + `business_requirements.md`:
   - Writes `ui_design.md` — screen/component inventory, layout structure, interaction notes for every UI-bearing surface named in the spec
   - **Proactively suggests** screen or flow simplifications — writes these to `discussion.md` under `## UI/UX Designer Suggestions`
   - Writes unresolvable questions to `discussion.md` under `## UI/UX Designer Questions`
6. TL, PO, and (if spawned) UI/UX Designer each report completion to the orchestrator when done (max 5 bullets each) — these are independent background completions, not a joint synchronization point
7. **As soon as TL reports completion** — independent of PO's and UI/UX Designer's progress, since `testing_plan.md` is derived from `architecture.md` and has no data dependency on `implementation_roadmap.md` or `ui_design.md` — **spawn or resume** QA agent (**model: sonnet**) via `qa_session` (spawn new if no session exists)
   - QA reads `spec.md` + `business_requirements.md` + `architecture.md` (including the Testability Notes section)
   - Writes `testing_plan.md` covering: unit, integration, E2E strategy, risk-based prioritisation, environments, entry/exit criteria, acceptance-criteria hints
   - **Proactively suggests** test-strategy improvements or flags architecture testability gaps — writes these to `discussion.md` under `## QA Suggestions`
   - Writes unresolvable questions to `discussion.md` under `## QA Questions`
   - QA reports completion to the orchestrator (max 5 bullets)
8. Orchestrator proceeds to Stage 2b once TL, PO, QA, and (if spawned) UI/UX Designer have **all** reported completion

> **QA's spawn gate is TL-completion-only** — it never waits on the UI/UX Designer branch. `testing_plan.md` is derived from `architecture.md`'s Testability Notes, not from `ui_design.md`; QA may read `ui_design.md` if it already exists by the time QA spawns, but never blocks on it.

#### `implementation_roadmap.md` format

The PO writes this document in the same style as a Scrum implementation roadmap. Stories use the devkit story standard format so they are ready to be created as GitHub Issues in any project.

```markdown
# {Feature/Project Name} — Implementation Roadmap

**Product:** {project name}
**Feature / Scope:** {brief scope description}
**Timeline:** {design phase} + {N sprints} ({M weeks total})
**Delivery Date:** ~{M} weeks from start

---

## Release Goal

{1–2 sentences. What does the team deliver? What problem is solved for the end user?}

---

## Phase Planning Overview

> **Naming rule:** the roadmap's thematic units are **Phases** (`Phase 0` = design/discovery, then `Phase 1`, `Phase 2`, …) — a single global, cross-repo sequence. Never name them "Sprint N": each repo's GitHub `sprint-N` labels are a **per-repo local execution counter** assigned by `plan next sprint`/`create stories` (starting at 1 for that repo's own first executed sprint), independent of this roadmap's numbering. Using "Sprint" for both reads as a contradiction on every story whose repo doesn't start at the global sequence's first theme.

| Phase | Duration | Focus | Story Points | Deliverable |
|-------|----------|-------|--------------|-------------|
| **Phase 0 — Design** | Week N | API / design spec | N pts | {deliverable} |
| **Phase 1** | Week N–N | {focus area} | N pts | {deliverable} |
| ... | | | | |

---

## Design Phase: {Title} (Week N)

**Goal:** {goal sentence}
**Story Points:** N

> **Standard:** {any design-first rules relevant to the project}

### [ST-XXXXXX] {Story Title In Title Case}
**Points:** N | **Priority:** P0/P1/P2 | **Assigned:** {Developer | Technical Lead | QA | Business Analyst | UI/UX Designer}

**Acceptance Criteria:**
- [ ] {criterion}
- [ ] {criterion}

**Dependencies:** {none or list}

---

## Phase N: {Title}

**Goal:** {goal sentence}
**Story Points:** N

### [ST-XXXXXX] {Story Title}
**Points:** N | **Priority:** P0/P1/P2 | **Assigned:** {role}

**Acceptance Criteria:**
- [ ] {criterion}

**Dependencies:** {none or story IDs}

---

## Dependency Graph

{1 sentence introducing the diagram.} See [Dependency Graph](diagrams/dependency_graph.mmd).

> PO writes the Mermaid flowchart (`flowchart TD`) showing story dependencies across phases and sprints to `diagrams/dependency_graph.mmd` — not inline here.

---

## Release Criteria

**Must Have:**
- [ ] {criterion}

**Should Have:**
- [ ] {criterion}

**Nice to Have:**
- [ ] {criterion}

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| {risk} | High/Medium/Low | High/Medium/Low | {mitigation} |

---

## Glossary

| Term | Definition |
|------|-----------|
| {term} | {definition} |
```

**PO rules for the roadmap:**
- Story IDs are placeholders (`ST-XXXXXX`) — real IDs are assigned when GitHub Issues are created
- AC should be high-level and testable — detailed implementation tasks belong in the story comments, not the roadmap
- Every story must have an `**Assigned:**` field matching one of the six agent roles
- Include a Glossary section for domain terms that a new developer would not know
- **UI-bearing repo ⇒ prototype story is always first (Phase 0).** If `ui_design.md` exists (a UI/UX Designer was spawned this Stage 2a), the roadmap's Phase 0 always includes one prototype story per UI-bearing surface, `**Assigned:** UI/UX Designer`, ahead of any screen-implementation story for that surface. Later screen-implementation stories reference the prototype story via `**Dependencies:**` as a **pointer, not a hard blocker** — same non-blocking convention as the CD-story dependency note below; implementation can proceed once the prototype exists as a reference, it does not have to wait for the prototype story to formally close.
- **CI/CD stories are always included on the roadmap — never conditional on "beyond baseline."** Based on TL's CI/CD & deployment strategy in `architecture.md`, write: (a) one CI story per service (**Assigned: Technical Lead**) — even for a Java repo whose skeleton generator already produces a baseline CI pipeline, since that baseline (build/test/lint/stub automation-test) is a common starting case, not a complete CI setup for a real service; (b) one CD story (**Assigned: Technical Lead**) for the deploy pipeline itself; and (c) a real automation-test story (**Assigned: QA**) if the CI/CD strategy calls for one beyond the scaffold's stub job. **If `architecture.md` records an unresolved deploy target** (the user never decided on CD infrastructure/cloud, per TL's mandatory CI/CD question in Stage 2a), the CD story still goes on the roadmap, but its `**Dependencies:**` field states the block explicitly, e.g. `Blocked — no CD infrastructure decided; cannot start until the user selects a deploy target.` There is no separate "Blocked" status in the story standard — this Dependencies-field note is how a blocked story is represented.

---

### Stage 2b — User Discussion (questions and suggestions)

1. Orchestrator reads `discussion.md`; if the file does not exist or is empty → skip to Stage 2c
2. **Spawn or resume** BA (**model: sonnet**) via `ba_session`; BA reads `discussion.md` and answers only the questions it can definitively resolve from `spec.md` and `business_requirements.md` — writes answers inline beneath each question; marks unanswerable questions `NEEDS_USER`; does not touch the `Suggestions` sections
3. Orchestrator collects all remaining `NEEDS_USER` questions and all `SUGGEST` items from `discussion.md`
4. Orchestrator presents each item to the user **one at a time** in this order: questions first, then suggestions
   - For questions: ask the user directly and record the answer
   - For suggestions: present the suggestion with its rationale and ask the user to accept, reject, or modify
5. After all items are addressed, orchestrator **resumes TL and PO in parallel** (via saved sessions; if session expired spawn new: TL **model: opus**, PO **model: sonnet**) with a summary of all user answers and decisions; TL and PO update their documents accordingly. **If `uiux_session` is populated** (a UI/UX Designer was spawned this Stage 2a), resume it in the **same parallel message** (spawn new if expired: **model: sonnet**) with the same summary; UI/UX Designer updates `ui_design.md` accordingly if any answer or suggestion changed the screen/component inventory, layout, or interaction notes.
6. **After TL's resume in step 5 completes** (sequenced, not parallel with step 5 — QA derives `testing_plan.md` from `architecture.md`, so it must see TL's updated output, not stale content): if TL's update this cycle **changed `architecture.md`** (including its Testability Notes section), **resume** QA (via `qa_session`; spawn new if expired: **model: sonnet**) with TL's updated `architecture.md` and a summary of user answers/decisions; QA updates `testing_plan.md` accordingly. Skip this sub-step if `architecture.md` was not changed this cycle — QA's own `## QA Questions`/`## QA Suggestions` items being answered does not by itself require a resume unless the answer also changed `architecture.md`; the answers already live in `discussion.md` for QA to pick up on its next natural spawn.
7. Orchestrator increments `Discussion Cycle` in the state file
8. **Loop limit:** Max 2 discussion cycles. After cycle 2 → orchestrator records any remaining unresolved items as open decisions and continues to Stage 2c

---

### Stage 2c — Final Review (BA) + Developer Summary (TL)

**BA finalises requirements:**

1. **Spawn or resume** BA (**model: sonnet**) via `ba_session`
2. BA reads all output documents (`business_requirements.md`, `architecture.md`, `testing_plan.md`, `implementation_roadmap.md`, and `ui_design.md` if it exists) and the resolved `discussion.md`
3. BA updates `business_requirements.md` to reflect any decisions made during Stage 2b
4. BA reports completion to the orchestrator (max 5 bullets)

**TL writes human-readable summary:**

5. **Resume** TL via `tl_session` (spawn new if expired: **model: opus**); TL reads all finalised output documents and writes `/result/analyst/summary.md`.

   **Writing goal:** Anyone — developer, product manager, or stakeholder — who has never seen this feature should be able to read `summary.md` alone and understand what is being built, why the architecture is shaped the way it is, and what the delivery plan looks like. Write in plain language — no agent-speak, no placeholder prose. Every section must contain real content.

   **Required structure:**

```markdown
# {Feature/Project Name} — Summary

> {One sentence describing the feature from a user's perspective.}

## Background
{2–4 sentences. Why does this feature exist? What problem does it solve? What triggered it?}

## Architecture Overview

{1–2 sentences introducing the diagram — what it shows and why the system is structured this way.}

See [{Diagram Title}](diagrams/{diagram_file}.mmd) — {one-line caption}.

> TL writes the diagram to a separate file under `diagrams/`, never inline here. Choose the type that best communicates the design:
> - `flowchart TD` for request/data flow
> - `graph LR` for component relationships
> - `sequenceDiagram` for interaction between services/actors (or a PlantUML `.puml` sequence diagram if clearer)
> The diagram must be accurate to architecture.md — do not simplify to the point of being misleading.

## Key Technical Decisions

{For each significant decision, write a short paragraph. Explain what was decided, what the alternatives were, and why this choice was made.}

**{Decision title}**
{2–3 sentences: what, why, and what was rejected.}

## Delivery Plan

{Brief narrative paragraph summarising scope and timeline, followed by the phase table.}

| Phase | Duration | Focus | Points | Key Deliverable |
|-------|----------|-------|--------|-----------------|
| Phase 0 — Design | Week N | {focus} | N | {deliverable} |
| Phase 1 | Week N–N | {focus} | N | {deliverable} |

## Non-Functional Requirements
{Only include NFRs with real implications for how code is written — performance budgets, security constraints, data isolation rules. Skip generic boilerplate.}

- **{NFR}:** {specific constraint or target}

## Open Items
{Decisions not resolved during the workflow. List each as an actionable question with an owner. Write "None" only if genuinely nothing is left open.}

- **{question}** — Owner: {TL / PO / BA}
```

6. TL reports completion to the orchestrator (max 5 bullets)
7. Orchestrator updates state file: `Stage: 2c`, `Updated: <now>`, then proceeds to Stage 2d

---

### Stage 2d — Review & Feedback Gate

**Purpose:** Let the user review the finished documents and give feedback in plain conversation — no forced yes/no. If they have none, the workflow simply wraps up; if they do, the relevant agent revises in place and the loop repeats.

1. Orchestrator lists all output documents in `/result/analyst/` and presents:

   ```
   Analysis complete — all documents are in /result/analyst/.
   Start with summary.md for the overview.

   Please review and share any feedback — questions, concerns, or changes.
   If everything looks good, just say so and I'll wrap up here (no need for an explicit "yes").
   ```

2. Orchestrator waits for the user's response.
3. **If the user gives feedback** (questions, requested changes, concerns — in any amount, about any document):
   a. Orchestrator maps each piece of feedback to the owning agent by document: `architecture.md` → TL; `testing_plan.md` → QA; `implementation_roadmap.md` → PO; `business_requirements.md` / `spec.md` → BA; `ui_design.md` (if it exists) → UI/UX Designer. Feedback touching multiple domains goes to each relevant agent.
   b. Orchestrator **resumes** the relevant agent(s) via their saved session ID(s) in `analyst_workflow_state.md` (spawn fresh only if a session ID is missing or expired — see the orchestrator's general Agent Session Management rule). If more than one agent is needed, resume/spawn them in a single message.
   c. Each agent deep-verifies the feedback against its owned document(s) before changing anything, applies the agreed changes directly, and reports back (max 5 bullets + observations)
   d. Orchestrator relays a brief summary of what changed to the user, then returns to step 1 (re-present, ask again)
4. **If the user confirms no further feedback** → proceed to Completion below.
5. **No loop limit** — unlike Stage 2b's 2-cycle cap, this is a post-completion wrap-up gate, not a design-discussion cycle. It repeats for as many rounds as the user needs, including across separate sessions, since the state file (and its sessions) stay alive until this gate closes.

**Completion:**

6. Orchestrator updates state file: `Stage: 2d`, `Updated: <now>`
7. Orchestrator deletes `analyst_workflow_state.md`

---

## Pipeline Rules

- **No agent spawning during Stage 1 Q&A** — orchestrator conducts elicitation directly; BA is spawned once only at the end of Stage 1 to write documents
- **Parallel spawning** — TL, PO, and (conditionally) UI/UX Designer are always spawned in a single orchestrator message in Stage 2a; never sequentially. UI/UX Designer joins this parallel wave only when Stage 2a step 1 detects a UI layer from `spec.md`/`business_requirements.md`. QA is a **sequenced** spawn, fired as soon as TL reports completion (independent of PO's and UI/UX Designer's progress) — it is not part of the parallel wave.
- **UI/UX Designer never gates QA** — QA's spawn condition is TL completion only; `testing_plan.md` has no data dependency on `ui_design.md`.
- **One item at a time** — orchestrator presents exactly one question or suggestion per turn in all user-facing interaction (Stage 1 and Stage 2b)
- **Agents engage users directly** — in Stage 2b, TL, PO, QA, and UI/UX Designer questions and suggestions go to the user without BA acting as a gatekeeper; BA only filters what it can answer from the spec
- **Suggest, don't just implement** — TL, PO, QA, and UI/UX Designer must look beyond the literal spec and surface better alternatives; silence on a clearly improvable point is a miss
- **Diagram format ownership** — the agent writing the diagram chooses Mermaid or PlantUML based on what communicates the design most clearly for that specific diagram; PlantUML diagrams are always separate `.puml` files in `diagrams/`, never inline
- **File ownership** — TL, PO, QA, and (conditionally) UI/UX Designer write to `discussion.md`; BA answers questions inline but does not write suggestions; `spec.md` and `elicitation_notes.md` are read-only in Stage 2
- **Document ownership** — `architecture.md` (incl. Testability Notes) → TL; `implementation_roadmap.md` → PO; `testing_plan.md` → QA, written only after TL's `architecture.md` is available, using its Testability Notes as technical input; `ui_design.md` → UI/UX Designer (conditional — only when a UI layer was detected), referenced but never authored by BA/PO
- **QA sequencing in Stage 2b** — when TL's resume-and-update (step 5) changes `architecture.md`, QA is resumed **after** TL completes (never in parallel with TL's resume) so it works from TL's updated output, not stale content; QA's own `discussion.md` items being answered does not by itself trigger a resume unless the answer also changed `architecture.md`
- **Loop limit** — max 2 discussion cycles in Stage 2b before recording open items and continuing; Stage 2d's post-completion feedback loop has **no** cycle limit
- **No forced yes/no at completion** — Stage 2d presents results and invites feedback; the workflow only wraps up (and deletes its state file) once the user confirms nothing further, it never requires a literal "yes"
- **Stop on blocker** — if any agent reports a blocking issue, orchestrator stops and reports to the user before continuing
- **Completion reports** — each agent returns max 5 bullets to the orchestrator; details go in Working Records
- **Independence** — output documents must not reference devkit internals; they must be readable and actionable by any development team

---

## Output Documents

All documents are written to `/result/analyst/` and remain there after the workflow completes.

| Document | Audience | Contents |
|---|---|---|
| `summary.md` | **Everyone (start here)** | Human-readable overview: background, architecture diagram (linked from `diagrams/`), key decisions, delivery plan, open items |
| `architecture.md` | Developer / TL | Architecture choices, component design, data handling, error handling, alternatives considered, Testability Notes (test seams, mockable boundaries, contract-test candidates). Diagrams linked from `diagrams/`, never inline. |
| `implementation_roadmap.md` | Dev / PO | Phased plan: release goal, sprint breakdown, stories with AC, dependency graph (linked from `diagrams/`), release criteria, risks, glossary |
| `testing_plan.md` | Dev / QA | Testing strategy: unit, integration, E2E, risk-based prioritisation, environments, entry/exit criteria, acceptance criteria hints. Authored by QA (sequenced after TL's `architecture.md`), not TL. |
| `ui_design.md` (conditional — only when a UI layer was detected) | Dev / UI/UX Designer | Screen/component inventory, layout structure, interaction notes. Authored by UI/UX Designer; referenced (not authored) by BA/PO. |
| `business_requirements.md` | All | Structured requirements: functional, non-functional, constraints, assumptions, open items |
| `spec.md` | BA / PO | Full formalised specification written by BA |
| `elicitation_notes.md` | Reference | Full Q&A log from Stage 1 |
| `diagrams/*.mmd`, `diagrams/*.puml` | Developer / TL / PO | One file per diagram — Mermaid and PlantUML source for every component, context, sequence, dependency-graph, and infrastructure diagram in the pipeline |
