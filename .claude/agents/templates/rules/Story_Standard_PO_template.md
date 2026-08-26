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
| Testing | TL | After TL PR approval | `status:testing` |
| **Done** | **PO** | After all AC pass and checkboxes ticked | `status:done` |

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

`**Assigned:**` is **mandatory** — must appear **above** `## User Story`. Valid values: `Developer`, `Technical Lead`, `QA`, `Business Analyst`, `UI/UX Designer`. "TBD" is not permitted.

> **Note — two separate "assignee" concepts:** The `**Assigned:**` field in the issue body (an agent role) drives pipeline routing and must always be set. It is distinct from the **GitHub Issue Assignee** (a GitHub user account set in the sidebar), which may be left unset in agent-driven workflows.

Status is tracked via GitHub Issue labels — not inside the body. Discussions happen as **comments** only.

---

## 3. Story Scope

Keep stories concise (2-3 pages). Reference technical docs (`docs/feature/`) rather than embedding specs. If 4+ pages, move technical detail out. No field-by-field struct definitions, pseudo-code, or algorithm descriptions in the story body.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **PO** | Create stories, define AC, clarify scope in Comment, tick AC checkboxes after QA confirms | Approve code, comment on implementation |

**Red Flags:** ticking checkboxes before QA confirms; commenting on code decisions.

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
- **One topic per comment** — answer what was asked and nothing else; a new finding gets its own comment. Batching replies to questions asked together is fine; an unasked finding smuggled into an answer is not.
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, cap ~150–200 words, draft to shape rather than trim-and-recount; corrections state the delta only; one close-out line per thread. Story-body decisions: the decision itself, ≤ 5 lines, pointer to the resolving comment — current truth, no supersession notes. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rules: `Story_Standard.md §3 (Body Amendments), §9`.
- **Announce body edits, never reproduce them.** As the only role that edits the story body, you are the one at risk here: after amending an AC, the comment states *which* section changed, *what kind* of change, and *why* — never the resulting AC text. A wording copied into a comment goes stale the next time that AC is reworded, and the thread then contradicts the body. Example: "AC6 reworded — added an X carve-out, per the reviewer's point that <reason>. Body updated." (`Story_Standard.md §9` rule 5)

---

## 13. Story Creation Template

Full template (title/label conventions, body skeleton, bug-repro block) relocated to `Product_Owner_Rules_Read_On_Demand.md` §2 — triggers whenever you create a new story (most PO spawns are status/comment work on existing stories, not this). Read it before your first `gh issue create`/`gh issue edit --body-file` of the session.

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

**PO:** After receiving QA confirmation, tick each AC checkbox `[x]` in the issue body. Always use `--body-file` (see `Agent_Common_Bootstrap.md §6`).

**Authoritative verification signal:** The closing signal for AC ticking is QA's final testing-pass comment on the story issue, or a merged PR where QA has previously posted sign-off. A Developer or TL comment alone is not sufficient. When multiple agent comments exist on the issue, locate the QA sign-off comment specifically before ticking any checkbox.
