# Story Standard — Product Owner View

> Product Owner working rules for story work. This is your day-to-day reference. `.claude/agents/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

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
**Assignee:** Responsible agent role (not "TBD")

**Labels — feature story:** `status:backlog`, `feature:<name>`, `phase-N`, `sprint-N`  
**Labels — non-feature story:** `status:backlog`, `sprint-N`  
**Labels — bug/defect story:** `status:backlog`, `bug`, `sprint-N` (add `feature:<name>` and `phase-N` if the bug is tied to a specific feature)

> Omit the sprint label if the story has not been assigned to a sprint yet. Sprint and backlog stories are not scoped to a feature; use `feature:` and `phase-` labels only when the story is part of a named feature.  
> Add `bug` to any story that reports a defect, regression, unexpected system behaviour, or infrastructure failure — even if it also carries a `feature:` label.

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

## 13a. AC Authoring Rules (apply when drafting or refining ACs)

- **API surface:** Every endpoint, field, or behavior named in an AC must exist in the API spec or be explicitly in scope for the same sprint. If it does not yet exist, note the dependency explicitly in the AC text (e.g., "after ST-XXXXXX merges") or split the work into a separate story.
- **Unit-test AC for new service logic:** If the story introduces new or modified service-layer methods, include an explicit AC: `- [ ] Unit tests added for all new service methods (empty-input guard, error path, happy path)`.
- **Test ordering for collection changes:** If an AC requires adding or reordering an automated test item, include a note on execution-order dependencies relative to sibling tests (e.g., "TC-08 must execute before TC-07 which deletes the resource").
- **Scoped-removal ACs:** If an AC removes, cleans up, or replaces a symbol, comment, or pattern across a named set of files, end the AC line with: `"Files outside this list are out of scope for this story."` This prevents Dev and QA from treating unlisted occurrences as missed violations rather than intentional deferrals.

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**PO:** After receiving QA confirmation, tick each AC checkbox `[x]` in the issue body. Always use `--body-file` (see §15).

**Authoritative verification signal:** The closing signal for AC ticking is QA's final testing-pass comment on the story issue, or a merged PR where QA has previously posted sign-off. A Developer or TL comment alone is not sufficient. When multiple agent comments exist on the issue, locate the QA sign-off comment specifically before ticking any checkbox.

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Always use Bash (not PowerShell) for all `gh` CLI calls.** `Bash(gh issue *)` and `Bash(gh pr *)` are pre-approved — no permission prompt. Never prepend `cd /path` to a command; the working directory is already set.

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:

```bash
gh issue edit <number> --repo {github-org}/{repo-name} --body-file /tmp/body.md
gh issue comment <number> --repo {github-org}/{repo-name} --body-file /tmp/comment.md
```

Delete the temp file immediately after the `gh` call completes — do not leave stale files in `/tmp/` or `.claude/agents/tmp/`.
