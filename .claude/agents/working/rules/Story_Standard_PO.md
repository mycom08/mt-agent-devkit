# Story Standard — Product Owner View

> Product Owner working rules for story work. This is your day-to-day reference. `.claude/agents/working/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When | GitHub Label |
|--------|-------------|------|--------------|
| **Backlog** | **PO** | After creation | `status:backlog` |
| **Ready** | **PO** | After assigning to implementer | `status:ready` |
| In Progress | Implementer | Dev branch created | `status:in-progress` |
| Review | Implementer | After PR created | `status:review` |
| Testing | QA | After TL approval | `status:testing` |
| **Done** | **PO** | After all AC pass and checkboxes ticked | `status:done` |

---

## 2. Story Structure

```markdown
**Phase:** [Phase/Sprint]  **Points:** [1-13]  **Priority:** Must/Should/Nice  
**Assigned:** Developer | Technical Lead | QA | Business Analyst

## User Story
> As a **[who]**, I want **[what]**, so that **[why]**.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Deliverables
- PR #123
```

`**Assigned:**` is **mandatory** — must appear **above** `## User Story`. Valid values: `Developer`, `Technical Lead`, `QA`, `Business Analyst`. "TBD" is not permitted.

Status is tracked via GitHub Issue labels — not inside the body. Discussions happen as **comments** only.

---

## 3. Story Scope

Keep stories concise (2-3 pages). Reference technical docs (`docs/technical/`) rather than embedding specifications. No file-by-file content walkthroughs in the story body.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **PO** | Create stories, define AC, clarify scope in Comment, tick AC checkboxes after QA confirms | Approve code, comment on implementation |

**Red Flags:** PO ticking checkboxes before QA confirms; PO commenting on technical decisions.

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Workflow / Template / AC / File]

**PO - YYYY-MM-DD**
Scope decision or AC clarification.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- Post scope decisions, AC clarifications, and acceptance feedback as **comments**
- Reply in the same thread for the same topic
- When a comment changes AC or delivery expectations, update the issue body to match
- **Never use the `@` prefix** — write role names without it (e.g., `**Dev**`, `**TL**`)
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text

---

## 13. Story Creation Template

**Issue title:** `[ST-XXXXXX][DEVKIT] Clear Title`  
**Assignee:** Responsible agent role (not "TBD")

**Labels:** `status:backlog`, `sprint-N`  
**Labels — bug/defect story:** `status:backlog`, `bug`, `sprint-N`

```markdown
**Phase:** [Phase/Sprint]  
**Story Points:** [1-13]  
**Priority:** Must-Have | Should-Have | Nice-to-Have  
**Assigned:** Developer | Technical Lead | QA | Business Analyst

## User Story

> As a **[persona]**,  
> I want **[feature]**,  
> So that **[benefit]**.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Technical Scope

[Optional: design notes, template changes, workflow changes]

## Deliverables

[Filled in after work complete: PR links, commits, artifacts]
```

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**PO:** After receiving QA confirmation, tick each AC checkbox `[x]` in the issue body. Always use `--body-file` (see §15).

**Authoritative verification signal:** The closing signal for AC ticking is QA's final testing-pass comment on the story issue. A Developer or TL comment alone is not sufficient.

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Always use Bash (not PowerShell) for all `gh` CLI calls.** Never prepend `cd /path` to a command; the working directory is already set.

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:

```bash
gh issue edit <number> --repo mycom08/mt-agent-devkit --body-file /tmp/body.md
gh issue comment <number> --repo mycom08/mt-agent-devkit --body-file /tmp/comment.md
```

Delete the temp file immediately after the `gh` call completes.
