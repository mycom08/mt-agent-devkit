# Story Standard — Developer View

> Developer working rules for story work. This is your day-to-day reference. `.claude/agents/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When | GitHub Label |
|--------|-------------|------|--------------|
| Backlog | PO | After creation | `status:backlog` |
| Ready | PO | After assigning to Developer | `status:ready` |
| **In Progress** | **Developer** | Dev branch created | `status:in-progress` |
| **Review** | **Developer** | After creating PR | `status:review` |
| Testing | TL | After TL approval | `status:testing` |
| Done | PO | After all AC pass | `status:done` |
| Hotfix | Developer | After hotfix branch created | `status:hotfix` |

---

## 4. Developer Workflow

### Status: Ready → In Progress
1. Remove `status:ready`, add `status:in-progress`
2. Read the full story: User Story, all AC, Technical Scope, and linked technical docs
3. **Verify the API spec** (`docs/api/`) for every endpoint the story touches — confirm shape, required fields, enums, constraints. If spec is missing or inconsistent, post a Comment tagging **TL** before writing any code
4. Identify open points — post comments tagging **PO** (scope/AC) or **TL** (technical) for any blockers
5. **Read PO and TL answers** — push back in the same thread if insufficient; wait for all blocking points to resolve
6. Create dev branch from feature branch: `git checkout -b ST-XXXXXX/description`

### Status: In Progress → Review
1. Self-check all AC locally — confirm each criterion is met (do **NOT** tick checkboxes; only PO ticks)
2. **Determine change type** and test accordingly:
   - **Behavioral changes** (source code, SQL migrations, config files, Docker files, environment variables, CI pipeline logic) → start the local docker service and verify your changes produce the expected behaviour before opening the PR. Use `docker compose` to bring up the sandbox stack and run requests against it.
   - **Non-behavioral changes** (docs, README, API spec where only names/descriptions change with no impact on request/response shape) → no local service test required.
3. Run integration test script if one exists: `bash tests/feature/.../ST-XXXXXX_*.sh` (see `docs/wiki/Testing_Guidelines.md`)
4. Source files follow naming standard (no generic names like `utils`, `helpers`, `types`)
5. Create PR with title: `[ST-XXXXXX][FEATURE] Story title`
6. Remove `status:in-progress`, add `status:review`
7. Request TL review in issue Comment

### Status: Review → In Progress (TL feedback)
1. Address feedback in dev branch
2. Push new commits
3. Re-request review in issue Comment

### Status: Review → Testing (after TL approval)
1. Add PR/commit links in issue Deliverables section (edit issue body)
2. Notify QA in issue Comment

### Developer as Reviewer (when TL is implementer)

Only when the orchestrator assigns Developer the Stage 2 peer review role — steps and notify-comment template in `Developer_Rules_Read_On_Demand.md` §12. Otherwise skip.

---

## 6. Hotfix (post-Done bug)

Only when a bug is found after a story is `status:done` — steps in `Developer_Rules_Read_On_Demand.md` §13. Otherwise skip.

Full procedure with red flags: `Story_Standard.md` §6.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Developer** | Implement, write PR, ask for guidance, self-check AC | Tick AC, answer scope questions, review code |

**Red Flags:** ticking AC checkboxes; answering PO's scope questions.

---

## 8. Technical Doc Divergence Rule

If a technical document is inaccurate, contradictory, or ambiguous during implementation:

1. **Do NOT silently deviate** — post immediately in the story Comment, tag TL
2. **TL decides:** fix now (blocking) or after story (non-blocking)

| Severity | Action |
|----------|--------|
| Blocks implementation | [BLOCKING] Stop. Post comment. Wait for TL fix. |
| Non-blocking | [NON-BLOCKING] Post comment. Continue. TL fixes after story. |
| Ambiguous | [NON-BLOCKING] Post comment. Ask TL to clarify before implementing. |

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Endpoint / AC / Section / File]

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
- **Never use the `@` prefix** — write role names without it (e.g., `**TL**`, `**PO**`). An `@` prefix triggers a GitHub mention to a real user account.
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text. A bare `#` creates a GitHub cross-reference to an unrelated issue or PR.
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, cap ~150–200 words, draft to shape rather than trim-and-recount; **never paste command output or check transcripts** — verdict in one line, logs in your working record; carve-out: paste the literal `gh pr checks <PR-number>` output when peer-reviewing (§12 Reviewer gate requires it in the approval comment) — nothing else gets pasted; a body edit made in the same pass is announced, not reproduced; facts already in your memory file are cited, not re-explained; corrections state the delta only; no comments about comments; one close-out line per thread. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rule: `Story_Standard.md §9`.

---

## 10. File Naming — Source Files

❌ Bad: `utils`, `helpers`, `types`, `errors`, `interface` — too generic

✅ Good: `rule_evaluator`, `policy_validator`, `condition_parser`, `auth_errors` — named after primary responsibility

**Rule:** Name after the primary interface/struct/responsibility; use the project's naming convention.

---

## 12. Gate Checklists

### Reviewer Gate — before approving a PR (Dev as peer reviewer)

Only when Dev is the peer reviewer — checklist in `Developer_Rules_Read_On_Demand.md` §12.

### Merge Gate — before merging dev branch to feature branch

- [ ] API spec verified — implementation matches spec for all affected endpoints
- [ ] Self-checked all AC locally (do NOT tick checkboxes)
- [ ] **If behavioral change:** local docker service started and changes verified end-to-end before PR opened
- [ ] **If behavioral change:** integration test script exists and passes via Git Bash
- [ ] Source files have good names (no generic names like `utils`, `helpers`, `types`)
- [ ] Code follows Development Standard
- [ ] PR created with story ID in title: `[ST-XXXXXX][FEATURE] ...`
- [ ] TL has reviewed and approved PR ✓
