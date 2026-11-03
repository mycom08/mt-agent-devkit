# Story Standard — UI/UX Designer View

> UI/UX Designer working rules for story work. This is your day-to-day reference. `{{AGENT_DIR_PREFIX}}/agents/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When |
|--------|-------------|------|
| **In Progress** | **UI/UX Designer** | Dev branch created |
| **Review** | **UI/UX Designer** | After PR opened |

**UI/UX Designer removes `status:ready` and adds `status:in-progress` only after verified story-branch creation; removes `status:in-progress` and adds `status:review` after opening the PR** — see `UI_UX_Designer_Rules.md` §5.

---

## 2. Story Structure

```markdown
**Phase:** [Phase/Sprint]  **Points:** [1-13]  **Priority:** Must/Should/Nice
**Assigned:** Developer | Technical Lead | QA | Business Analyst | UI/UX Designer

## User Story
> As a **[who]**, I want **[what]**, so that **[why]**.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Deliverables
- PR #123
```

**Design Source** — an optional pointer-style field (wireframe link, backlog reference). Read it in Step 1 of `UI_UX_Designer_Rules.md` §2 before building anything; it is the source of truth for which screens/flows to build. Do not invent screens or interactions the Design Source and AC do not call for.

Status is tracked via GitHub Issue labels — not inside the body. Discussions happen as **comments** only.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **UI/UX Designer** | Turn a wireframe/backlog story into a runnable prototype, write PR, ask for guidance, self-check AC before marking ready | Tick AC, answer scope questions, review code, ship a static-only mockup as the final deliverable |

**Red Flags:** ticking AC checkboxes; shipping a static-only mockup (image export, click-through-only deck, no mock backend) as the final deliverable.

---

## 9. Comment Standard

Load the `comment` skill (`.mt-agent-devkit/skills/comment/SKILL.md`) before any comment; it owns the template, Thread Status, writing rules, prefix bans and the Commenter gate. UI/UX Designer has no role-only comment rules.

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**UI/UX Designer:** Self-check each AC criterion before marking the story ready for review. Do **not** tick checkboxes.
