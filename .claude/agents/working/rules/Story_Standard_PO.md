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
- **One topic per comment** — answer what was asked and nothing else; a new finding gets its own comment. Batching replies to questions asked together is fine; an unasked finding smuggled into an answer is not.
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, cap ~150–200 words — draft to shape (one short paragraph per topic: decision, one-line why, pointer) so the `wc -w` check is a backstop, not a trim-and-recount loop; corrections state the delta only; one close-out line per thread. When writing a decision into the story body: the decision itself, ≤ 5 lines, pointer to the resolving comment — the body stays current truth with no supersession notes. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rules: `Story_Standard.md §3 (Body Amendments), §9`.
- **Announce body edits, never reproduce them.** As the only role that edits the story body, you are the one at risk here: after amending an AC, the comment states *which* section changed, *what kind* of change, and *why* — never the resulting AC text. A wording copied into a comment goes stale the next time that AC is reworded, and the thread then contradicts the body. Example: "AC6 reworded — added an X carve-out, per the reviewer's point that <reason>. Body updated." (`Story_Standard.md §9` rule 5)

---

## 13. Story Creation Template

**Issue title:** `[ST-XXXXXX][DEVKIT] Clear Title`  
**GitHub Assignee:** (Optional — a GitHub user account; may be left unset in agent-driven workflows)

**Labels:** `status:backlog`, `sprint-N`  
**Labels — bug/defect story:** `status:backlog`, `bug`, `sprint-N`

```markdown
**Phase:** [Phase/Sprint]  
**Story Points:** [1-13]  
**Priority:** Must-Have | Should-Have | Nice-to-Have  
**Assigned:** Developer | Technical Lead | QA | Business Analyst | UI/UX Designer

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

> **Bug/defect stories** (carry the `bug` label): insert a `## Reproduction` section immediately after `## Acceptance Criteria` (before `## Technical Scope`):
> ```markdown
> ## Reproduction
>
> **Repro Command:** [exact command/test to run verbatim, or `unknown`]
> **Expected:** [what should happen]
> **Actual:** [what actually happens — the observed defect]
> ```
> The Bug Reproduction Pre-Flight step (`Shared_Pipeline_Stages.md`, runs ahead of Stage 0) executes `Repro Command` verbatim before any implementer is spawned — it never parses AC prose to derive a command. If `Repro Command` is absent or `unknown`, pre-flight is skipped and Stage 1 proceeds normally (the implementer reproduces as part of its own work, same as before this convention existed).

**Writing AC for a devkit workflow stage (devkit-internal, no target-project equivalent):**
- **State detection in terms of what's actually on disk at that stage, not a downstream concept.** A stage that runs before a later pipeline boundary exists (e.g. Analyst Stage 2a runs before Build Software's repo-splitting) cannot gate on that downstream concept ("any repo's tech stack") — phrase the AC against the artifacts genuinely available at that point (e.g. "the spec names a UI-bearing surface"), or the Developer has to reword it mid-design.
- **When two same-sprint stories restructure the same workflow section, name the land order in Technical Scope.** Don't rely on a Developer-initiated cross-reference comment to surface the sequencing question — state which story lands first and how the sections compose once both are merged.

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
