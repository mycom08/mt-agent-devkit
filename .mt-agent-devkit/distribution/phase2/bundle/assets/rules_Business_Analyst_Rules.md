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

## Version

**Version:** 1.2 (see `changes.json` for this file's change history)
**Created:** 2026-05-25
