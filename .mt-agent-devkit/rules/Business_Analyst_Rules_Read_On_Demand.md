# Business Analyst Rules — Read-On-Demand Tier

**Applies to:** Business Analyst agent
**Reference from:** `.mt-agent-devkit/instructions/business_analyst_instructions.md`

Not loaded at spawn. Fetch a section only when its named trigger fires — see `Business_Analyst_Rules_Bootstrap.md §6` for the routing table.

---

## 1. Pre-PR Gate (when acting as Implementer)

When BA is the story Implementer, load the `git-workflow` skill (`.mt-agent-devkit/skills/git-workflow/SKILL.md`) before creating the PR, and run the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`) before opening a PR. It is the same gate for every implementer: harness, template and workflow changes run the validators and are never exempt as docs-only.

---

## 7. Requirement Spec Format

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

**Version:** 1.2 — Added §7, the requirement spec format (ST-000245).
**Previous:** 1.1 — §1 points to `pre-pr-gate`, the stricter gate (ST-000308).
**Previous:** 1.0 — Split out of `Business_Analyst_Rules.md` (now `_Bootstrap.md`) §2, unchanged content, renumbered §1.
**Created:** 2026-08-25
