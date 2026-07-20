# Story Standard — Developer View

> Developer working rules for story work. This is your day-to-day reference. `.claude/agents/working/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When | GitHub Label |
|--------|-------------|------|--------------|
| Backlog | PO | After creation | `status:backlog` |
| Ready | PO | After assigning to Developer | `status:ready` |
| **In Progress** | **Developer** | Dev branch created | `status:in-progress` |
| **Review** | **Developer** | After creating PR | `status:review` |
| Testing | QA | After TL approval | `status:testing` |
| Done | PO | After all AC pass | `status:done` |
| Hotfix | Developer | After hotfix branch created | `status:hotfix` |

---

## 4. Developer Workflow

### Status: Ready → In Progress
1. Remove `status:ready`, add `status:in-progress`
2. Read the full story: User Story, all AC, Technical Scope, and linked technical docs
3. Identify open points — post comments tagging **PO** (scope/AC) or **TL** (technical) for any blockers
4. **Read PO and TL answers** — push back in the same thread if insufficient; wait for all blocking points to resolve
5. Create dev branch from main: `git checkout -b ST-XXXXXX/description`

### Status: In Progress → Review
1. Self-check all AC locally — confirm each criterion is met (do **NOT** tick checkboxes; only PO ticks)
2. Run pre-PR checks from `Developer_Rules.md §5`
3. Create PR with title: `[ST-XXXXXX][DEVKIT] Story title`
4. Remove `status:in-progress`, add `status:review`
5. Request TL review in issue Comment

### Status: Review → In Progress (TL feedback)
1. Address feedback in dev branch
2. Push new commits
3. Re-request review in issue Comment

### Status: Review → Testing (after TL approval)
1. Remove `status:review`, add `status:testing`
2. Add PR/commit links in issue Deliverables section (edit issue body)
3. Notify QA in issue Comment

### Developer as Reviewer (when TL is implementer)

When Developer is assigned the Stage 2 peer review role:
1. Review the PR diff via `gh pr diff <number> --repo mycom08/mt-agent-devkit`
2. Post inline PR comments for specific line-level feedback
3. **Always post a brief notify comment on the GitHub Issue** — whether approving or requesting changes:

   ```
   ## PR #NNN peer review — <Approved | Changes Requested>
   **Thread Status:** Open | Resolved
   **Area:** Implementation

   **Developer - YYYY-MM-DD**
   <Summary of findings or approval rationale>

   **Next:** TL to address CR items | None
   ```

4. Use `gh pr comment` for the PR-level verdict (not `gh pr review --approve` — GitHub blocks self-approval)

---

## 6. Hotfix (post-Done bug)

When a bug is found after a story is `status:done`, **never fix on main**. Create a fix branch off main, then run the normal review/test cycle:

1. Create `fix/ST-XXXXXX/short-description` from main; set the issue to `status:hotfix`
2. Fix on that branch → open a PR targeting `main` → request TL review
3. After TL approval, merge → set `status:testing` → notify QA to re-validate the affected AC
4. QA reports results → PO ticks AC → `status:done`

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Developer** | Implement, write PR, ask for guidance, self-check AC | Tick AC, answer scope questions, review code |

**Red Flags:** Developer ticking AC checkboxes; developer answering PO scope questions.

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Workflow / Template / AC / File]

**Developer - YYYY-MM-DD**
Question or concern.

**TL - YYYY-MM-DD**
Response and decision.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- Open a new comment only for a new topic
- Reply in the same thread for the same topic
- When a comment resolves a scope/AC question, update the issue body to match
- **Never use the `@` prefix** — write role names without it (e.g., `**TL**`, `**PO**`)
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, soft cap ~150–200 words; evidence by pointer — full check logs go in your working record, not the thread; corrections state the delta only; no comments about comments; one close-out line per thread. Full rule: `Story_Standard.md §9`.

---

## 12. Gate Checklists

### Reviewer Gate — before approving a PR (Dev as peer reviewer)

- [ ] All CI checks on the PR have **finished**
- [ ] No CI check is in a **failed** state
- [ ] Code review criteria pass (per `Developer_Rules.md §11`)

### Merge Gate — before merging dev branch to main

- [ ] Self-checked all AC locally (do NOT tick checkboxes)
- [ ] Pre-PR checks pass (see `Developer_Rules.md §5`)
- [ ] PR created with story ID in title: `[ST-XXXXXX][DEVKIT] ...`
- [ ] TL has reviewed and approved PR ✓

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Always use Bash (not PowerShell) for all `gh` CLI calls.** `Bash(gh issue *)` and `Bash(gh pr *)` are pre-approved — no permission prompt. Never prepend `cd /path` to a command; the working directory is already set.

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:

```bash
gh issue edit <number> --repo mycom08/mt-agent-devkit --body-file /tmp/body.md
gh issue comment <number> --repo mycom08/mt-agent-devkit --body-file /tmp/comment.md
```

Delete the temp file immediately after the `gh` call completes.
