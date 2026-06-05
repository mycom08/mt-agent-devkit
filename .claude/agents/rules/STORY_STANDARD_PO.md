# Story Standard — Product Owner View

> Role-specific excerpt from `.claude/agents/rules/STORY_STANDARD.md` (v1.8). Read this instead of the full file.

---

## 1. Story Status Workflow

| Status | Who Changes | When | GitHub Label |
|--------|-------------|------|--------------|
| **Backlog** | **PO** | After creation | `status:backlog` |
| **Ready** | **PO** | After assigning to Developer | `status:ready` |
| In Progress | Developer | Dev branch created | `status:in-progress` |
| Review | Developer | After PR created | `status:review` |
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

Keep stories concise (2-3 pages). Reference technical docs (`docs/feature/`) rather than embedding specs. If 4+ pages, move technical detail out. No field-by-field struct definitions, pseudo-code, or algorithm descriptions in the story body.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **PO** | Create stories, define AC, clarify scope in Comment, tick AC checkboxes after QA confirms | Approve code, comment on implementation |

**Red Flags:** PO ticking checkboxes before QA confirms; PO commenting on code decisions.

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Endpoint / AC / Section / File]

**PO - YYYY-MM-DD**
Scope decision or AC clarification.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- Post scope decisions, AC clarifications, and acceptance feedback as **comments**
- Reply in the same thread for the same topic
- When a comment changes AC or delivery expectations, update the issue body to match
- **Never use the `@` prefix** — write role names without it (e.g., `**Dev**`, `**TL**`). An `@` prefix triggers a GitHub mention to a real user account.
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text. A bare `#` creates a GitHub cross-reference to an unrelated issue or PR.

---

## 13. Story Creation Template

**Issue title:** `[ST-XXXXXX][FEATURE] Clear Title`  
**Labels:** `status:backlog`, `{feature-label}`, `sprint-N`, `phase-N`  
**Assignee:** Responsible agent role (not "TBD")

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

## API Spec Reference

[Affected endpoints and link to spec file, or "N/A"]

## Technical Scope

[Optional: architecture notes, API changes, database migrations]

## Deliverables

[Filled in after work complete: PR links, commits, artifacts]
```

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**PO:** After receiving QA confirmation, tick each AC checkbox `[x]` in the issue body. Always use `--body-file` (see §15) to avoid PowerShell corruption.

---

## 15. GitHub Issue CLI — PowerShell Safety Rule

**Never** pass multi-line or backtick-containing Markdown via `--body "..."`. Always write to a temp file:

```powershell
$body = @'
## Acceptance Criteria

- [ ] `field` uses `x-go-type: json.RawMessage`
- [x] Criterion already ticked
'@

$tmp = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tmp, $body, [System.Text.Encoding]::UTF8)
gh issue edit <number> --body-file $tmp
gh issue comment <number> --body-file $tmp
Remove-Item $tmp
```

**Why `WriteAllText` with explicit UTF-8?** `Set-Content` may add a BOM or alter line endings. `WriteAllText` is reliable.

**Applies to:** `gh issue edit`, `gh issue create`, `gh issue comment` — any call where body contains backticks, checkboxes, or spans multiple lines.
