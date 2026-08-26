# Story Standard — UI/UX Designer View

> UI/UX Designer working rules for story work. This is your day-to-day reference. `.claude/agents/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When |
|--------|-------------|------|
| **In Progress** | **UI/UX Designer** | Dev branch created |
| **Review** | **UI/UX Designer** | After PR opened |

**UI/UX Designer removes `status:ready`, adds `status:in-progress` when starting a story; removes `status:in-progress`, adds `status:review` after opening the PR** — see `UI_UX_Designer_Rules.md` §5.

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

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Flow / Screen / AC / File]

**UI/UX Designer - YYYY-MM-DD**
Question or concern.

**PO - YYYY-MM-DD**
Response and decision.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- **One topic per comment** — answer the questions asked and nothing else; a finding that surfaces while answering posts as its own comment with its own thread status. Batching replies to questions asked together is fine; smuggling an unasked finding into an answer is not.
- Reply in the same thread for the same topic
- **Never use the `@` prefix** — write role names without it (e.g., `**PO**`, `**TL**`). An `@` prefix triggers a GitHub mention to a real user account.
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text. A bare `#` creates a GitHub cross-reference to an unrelated issue or PR.
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, cap ~150–200 words, draft to shape rather than trim-and-recount; **never paste command output or check transcripts** — verdict in one line, logs in your working record; a body edit made in the same pass is announced, not reproduced; corrections state the delta only; no comments about comments; one close-out line per thread. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rule: `Story_Standard.md §9`.

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**UI/UX Designer:** Self-check each AC criterion before marking the story ready for review. Do **not** tick checkboxes.

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Always use Bash (not PowerShell) for all `gh` CLI calls.** `Bash(gh issue *)` and `Bash(gh pr *)` are pre-approved — no permission prompt. PowerShell `.NET` methods (`[System.IO.Path]::GetTempFileName()`, `[System.IO.File]::WriteAllText()`) trigger a permission prompt regardless of allow-list entries, and PowerShell interprets backticks as escape characters, silently corrupting Markdown. Never prepend `cd /path` to a command; the working directory is already set.

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:

```bash
gh issue edit <number> --repo {github-org}/{repo-name} --body-file /tmp/body.md
gh issue comment <number> --repo {github-org}/{repo-name} --body-file /tmp/comment.md
```

Delete the temp file immediately after the `gh` call completes — do not leave stale files in `/tmp/` or `.claude/agents/tmp/`.
