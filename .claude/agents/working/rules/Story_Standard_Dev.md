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
2. Run pre-PR checks from `Developer_Rules_Bootstrap.md §5`
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

Only when the orchestrator assigns Developer the Stage 2 peer review role — steps and notify-comment template in `Developer_Rules_Read_On_Demand.md §16`. Otherwise skip.

---

## 6. Hotfix (post-Done bug)

Only when a bug is found after a story is `status:done` — steps in `Developer_Rules_Read_On_Demand.md §17`. Otherwise skip.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Developer** | Implement, write PR, ask for guidance, self-check AC | Tick AC, answer scope questions, review code |

**Red Flags:** ticking AC checkboxes; answering PO's scope questions.

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

- **One topic per comment** — answer the questions asked and nothing else; a finding that surfaces while answering posts as its own comment with its own thread status. Batching replies to questions asked together is fine; smuggling an unasked finding into an answer is not.
- Reply in the same thread for the same topic
- When a comment resolves a scope/AC question, update the issue body to match
- **Never use the `@` prefix** — write role names without it (e.g., `**TL**`, `**PO**`)
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, cap ~150–200 words, draft to shape rather than trim-and-recount; **never paste command output or check transcripts** — verdict in one line, logs in your working record; carve-out: paste the literal `gh pr checks <PR-number>` output when peer-reviewing (§12 Reviewer gate requires it in the approval comment) — nothing else gets pasted; a body edit made in the same pass is announced, not reproduced; facts already in your memory file are cited, not re-explained; corrections state the delta only; no comments about comments; one close-out line per thread. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rule: `Story_Standard.md §9`.

---

## 12. Gate Checklists

### Reviewer Gate — before approving a PR (Dev as peer reviewer)

Only when Dev is the peer reviewer — checklist in `Developer_Rules_Read_On_Demand.md §16`.

### Merge Gate — before merging dev branch to main

- [ ] Self-checked all AC locally (do NOT tick checkboxes)
- [ ] Pre-PR checks pass (see `Developer_Rules_Bootstrap.md §5`)
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
