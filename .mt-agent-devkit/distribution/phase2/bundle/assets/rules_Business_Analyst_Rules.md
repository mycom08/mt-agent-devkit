# Business Analyst Rules

**Applies to:** Business Analyst agent
**Reference from:** `.mt-agent-devkit/instructions/business_analyst_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any analysis or documentation work:

1. **Read Project Priming** — `.mt-agent-devkit/context/Project_Priming.md`
2. **Read your Working Record** — `{RUNTIME_ROOT}/working-record/Business_Analyst_Working_Record.md`
3. **Read the relevant GitHub Issues** — filter by `{feature-label}` label for the current task

---

## 2. Pre-PR Gate (when acting as Implementer)

When BA is the story Implementer, run the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`) before opening a PR. It is the same gate for every implementer, including its PR check note: the build and unit tests always run, so no change is exempt as docs or config only.

---

## 3. Story Comment Rules

When posting comments on GitHub Issues:

- Post all BA clarifications, scope notes, and follow-up replies as **comments on the GitHub Issue** — do not create standalone files for normal discussion
- Load the `comment` skill (`.mt-agent-devkit/skills/comment/SKILL.md`) before any comment; it owns the thread format, same-thread replies, the bare-number ban and the Commenter gate

---

## 4. Runtime-State Handoff (mandatory before handoff)

Keep agent state local and uncommitted before signaling stage completion — the `handoff` skill owns the rule; your route reads its generated copy, `.mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md §5`.

---

## 5. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker (tests won't run, sandbox won't start, automation runner cannot connect, script/CI/auth errors), follow the `troubleshooting` skill's check-memory → fix → record-to-memory protocol; your route reads its generated copy, `.mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md §2`.

---

## 6. Requirement Spec Format

One spec per capability, document ID `SPEC-NNN`. BA authors; PO approves product scope. Header and verdicts: the `gate-verdict` skill (`.mt-agent-devkit/skills/gate-verdict/SKILL.md`).

```markdown
# SPEC-NNN: <title>
Status: Draft
Approved-by:
Approved-at:

## Purpose
The problem and the outcome wanted.
## Scope
In scope: ...
Out of scope: ...
## Actors and Functional Requirements
- FR-1: <actor> <observable behavior> (source: <user input or document>)
## Acceptance Criteria
- AC-1 (FR-1): Given <state>, When <action>, Then <observable result>
## Constraints and Non-Functional Requirements
Limits the solution must respect, each measurable where possible.
## Dependencies
Systems, specs, data or decisions this spec relies on.
## Open Questions
| ID | Question | Class | Owner | Resolution |
|---|---|---|---|---|
| Q-1 | <question> | BLOCKING-FEATURE or BLOCKING-SPEC | <who answers> | <empty until answered> |
```

Writing rules:

- **Testable acceptance criteria:** every functional requirement has at least one Given/When/Then criterion with a result that can pass or fail, including the error cases.
- **Flag ambiguous language:** mark unmeasured or open-ended wording ("fast", "easy", "secure", "appropriate", "etc.", "should support") as `[AMBIGUOUS: <what is missing>]` and raise it as an open question.
- **Never invent requirements:** every requirement traces to its source. A gap, assumption or suggestion is an open question until the answer confirms it.
- **List every open question** and classify it, with an owner. Keep answered ones with their resolution.
  - `BLOCKING-FEATURE`: the answer can change the feature as a whole (goal, users, scope, platform). The feature cannot advance until it is resolved.
  - `BLOCKING-SPEC`: the answer affects only this spec. This spec cannot be approved; other specs proceed.

---

## Version

**Version:** 1.3 (see `CHANGELOG.md` for this file's change history)
**Created:** 2026-05-25
