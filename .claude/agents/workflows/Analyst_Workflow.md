# Analyst Workflow

Triggered by: `"analyze requirement: <brief description>"` or `"/analyze <brief description>"` in CLAUDE.md

The text after the trigger keyword is the user's **initial requirement context**. If no context is provided, the orchestrator asks the user for a one-line description before starting.

**Output folder:** `.claude/agents/tmp/analyst/`

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
**Stage:** <1 | 2a | 2b | 2c>
**Question Count:** <N>
**Discussion Cycle:** <0 | 1 | 2>
**Sessions:**
- ba_session: <agentId or empty>
- tl_session: <agentId or empty>
- po_session: <agentId or empty>
**Updated:** YYYY-MM-DDTHH:MM
```

**Write rules:** Create at Stage 1 entry. Update `Stage` + `Updated` after each transition. Update `Sessions` on spawn only. Update `Question Count` each Q&A turn. Delete after Stage 2c completes.

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
7. Orchestrator writes the full Q&A log to `.claude/agents/tmp/analyst/elicitation_notes.md`
8. **Spawn** BA agent; save its `agentId` as `ba_session`
9. BA reads `business_analyst_instructions.md` + its memory files + `elicitation_notes.md`
10. BA writes:
    - `spec.md` — the full elicited specification
    - `requirements.md` — structured requirements (functional, non-functional, constraints, assumptions, open items)
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
| `requirements.md` | BA | Structured requirements: functional, non-functional, constraints, assumptions, open items |
| `architecture.md` | TL | Architecture choices, component design, data handling, error handling, alternatives considered |
| `testing_plan.md` | TL | Testing strategy: unit, integration, E2E, acceptance criteria hints |
| `implementation_plan.md` | PO | Story breakdown, priorities, milestones, dependency order, effort estimates |
| `discussion.md` | TL + PO (shared write) | Questions needing user input and suggestions for the user to consider |

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
```

Agents omit a section entirely if they have nothing to add to it.

---

### Stage 2a — Initial Analysis (TL and PO in parallel)

1. **Spawn** TL agent and PO agent in the **same orchestrator message** — they run in parallel
   - Save TL `agentId` as `tl_session`; save PO `agentId` as `po_session`
2. TL reads `spec.md` + `requirements.md`:
   - Writes `architecture.md` covering: architecture choices, component design, data handling details, error handling strategies, and any alternatives considered
   - Writes `testing_plan.md` covering: unit, integration, E2E layers, acceptance criteria hints
   - **Proactively suggests** better technical solutions or trade-offs the user may not have considered — writes these to `discussion.md` under `## TL Suggestions`
   - Writes unresolvable questions to `discussion.md` under `## TL Questions`
3. PO reads `spec.md` + `requirements.md`:
   - Writes `implementation_plan.md` covering: story breakdown, priorities, milestones, dependency order, effort estimates
   - **Proactively suggests** scope simplifications, MVP trade-offs, or phasing alternatives — writes these to `discussion.md` under `## PO Suggestions`
   - Writes unresolvable questions to `discussion.md` under `## PO Questions`
4. Both agents report completion to the orchestrator (max 5 bullets each)
5. Orchestrator proceeds to Stage 2b

---

### Stage 2b — User Discussion (questions and suggestions)

1. Orchestrator reads `discussion.md`; if the file does not exist or is empty → skip to Stage 2c
2. **Spawn or resume** BA via `ba_session`; BA reads `discussion.md` and answers only the questions it can definitively resolve from `spec.md` and `requirements.md` — writes answers inline beneath each question; marks unanswerable questions `NEEDS_USER`; does not touch the `Suggestions` sections
3. Orchestrator collects all remaining `NEEDS_USER` questions and all `SUGGEST` items from `discussion.md`
4. Orchestrator presents each item to the user **one at a time** in this order: questions first, then suggestions
   - For questions: ask the user directly and record the answer
   - For suggestions: present the suggestion with its rationale and ask the user to accept, reject, or modify
5. After all items are addressed, orchestrator **resumes TL and PO in parallel** (via saved sessions or spawns new) with a summary of all user answers and decisions; TL and PO update their documents accordingly
6. Orchestrator increments `Discussion Cycle` in the state file
7. **Loop limit:** Max 2 discussion cycles. After cycle 2 → orchestrator records any remaining unresolved items as open decisions and continues to Stage 2c

---

### Stage 2c — Final Review (BA)

1. **Spawn or resume** BA via `ba_session`
2. BA reads all output documents (`requirements.md`, `architecture.md`, `testing_plan.md`, `implementation_plan.md`) and the resolved `discussion.md`
3. BA updates `requirements.md` to reflect any decisions made during Stage 2b
4. BA produces a brief consolidation summary and returns it to the orchestrator (max 5 bullets)
5. Orchestrator reports the list of all output documents to the user
6. Orchestrator deletes `analyst_workflow_state.md`

---

## Pipeline Rules

- **No agent spawning during Stage 1 Q&A** — orchestrator conducts elicitation directly; BA is spawned once only at the end of Stage 1 to write documents
- **Parallel spawning** — TL and PO are always spawned in a single orchestrator message in Stage 2a; never sequentially
- **One item at a time** — orchestrator presents exactly one question or suggestion per turn in all user-facing interaction (Stage 1 and Stage 2b)
- **Agents engage users directly** — in Stage 2b, TL and PO questions and suggestions go to the user without BA acting as a gatekeeper; BA only filters what it can answer from the spec
- **Suggest, don't just implement** — TL and PO must look beyond the literal spec and surface better alternatives; silence on a clearly improvable point is a miss
- **File ownership** — TL and PO write to `discussion.md`; BA answers questions inline but does not write suggestions; `spec.md` and `elicitation_notes.md` are read-only in Stage 2
- **Loop limit** — max 2 discussion cycles in Stage 2b before recording open items and continuing
- **Stop on blocker** — if any agent reports a blocking issue, orchestrator stops and reports to the user before continuing
- **Completion reports** — each agent returns max 5 bullets to the orchestrator; details go in Working Records

---

## Output Documents

All documents are written to `.claude/agents/tmp/analyst/` and remain there after the workflow completes.

| Document | Contents |
|---|---|
| `elicitation_notes.md` | Full Q&A log from Stage 1 |
| `spec.md` | Formalised specification written by BA |
| `requirements.md` | Structured requirements: functional, non-functional, constraints, assumptions, open items |
| `architecture.md` | Architecture choices, component design, data handling, error handling, alternatives considered |
| `testing_plan.md` | Testing strategy: unit, integration, E2E, acceptance criteria hints |
| `implementation_plan.md` | Story breakdown, priorities, milestones, dependency order, effort estimates |
