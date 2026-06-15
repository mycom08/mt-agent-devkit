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
| Testing | QA | After TL approval | `status:testing` |
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
1. Remove `status:review`, add `status:testing`
2. Add PR/commit links in issue Deliverables section (edit issue body)
3. Notify QA in issue Comment

### Developer as Reviewer (when TL is implementer)

When Developer is assigned the Stage 2 peer review role:
1. Review the PR diff via `gh pr diff <number> --repo {github-org}/{repo-name}`
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

When a bug is found after a story is `status:done`, **never fix on the feature branch or master**. Create a fix branch off the feature branch, then run the normal review/test cycle:

1. Create `fix/ST-XXXXXX/short-description` from the feature branch; set the issue to `status:hotfix`
2. Fix on that branch → open a PR targeting the **feature branch** → request TL review
3. After TL approval, merge → set `status:testing` → notify QA to re-test the affected AC
4. QA reports results → PO ticks AC → `status:done`

Full procedure with red flags: `Story_Standard.md` §6.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Developer** | Implement, write PR, ask for guidance, self-check AC | Tick AC, answer scope questions, review code |

**Red Flags:** Developer ticking AC checkboxes; developer answering PO scope questions.

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

- Open a new comment only for a new topic
- Reply in the same thread for the same topic
- When a comment resolves a scope/AC question, update the issue body to match
- **Never use the `@` prefix** — write role names without it (e.g., `**TL**`, `**PO**`). An `@` prefix triggers a GitHub mention to a real user account.
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text. A bare `#` creates a GitHub cross-reference to an unrelated issue or PR.

---

## 10. File Naming — Source Files

❌ Bad: `utils`, `helpers`, `types`, `errors`, `interface` — too generic

✅ Good: `rule_evaluator`, `policy_validator`, `condition_parser`, `auth_errors` — named after primary responsibility

**Rule:** Name after the primary interface/struct/responsibility; use the project's naming convention.

---

## 12. Gate Checklists

### Reviewer Gate — before approving a PR (Dev as peer reviewer)

- [ ] All CI checks on the PR have **finished** — do not review while CI is still running
- [ ] No CI check is in a **failed** state — if any failed, comment on the PR and ask for a fix; do not approve until green
- [ ] Code review criteria pass (per `Developer_Rules.md` §11)

### Merge Gate — before merging dev branch to feature branch

- [ ] API spec verified — implementation matches spec for all affected endpoints
- [ ] Self-checked all AC locally (do NOT tick checkboxes)
- [ ] **If behavioral change:** local docker service started and changes verified end-to-end before PR opened
- [ ] **If behavioral change:** integration test script exists and passes via Git Bash
- [ ] Source files have good names (no generic names like `utils`, `helpers`, `types`)
- [ ] Code follows Development Standard
- [ ] PR created with story ID in title: `[ST-XXXXXX][FEATURE] ...`
- [ ] TL has reviewed and approved PR ✓

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Always use Bash (not PowerShell) for all `gh` CLI calls.** `Bash(gh issue *)` and `Bash(gh pr *)` are pre-approved — no permission prompt. PowerShell `.NET` methods (`[System.IO.Path]::GetTempFileName()`, `[System.IO.File]::WriteAllText()`) trigger a permission prompt regardless of allow-list entries, and PowerShell interprets backticks as escape characters, silently corrupting Markdown. Never prepend `cd /path` to a command; the working directory is already set.

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:

```bash
gh issue edit <number> --repo {github-org}/{repo-name} --body-file /tmp/body.md
gh issue comment <number> --repo {github-org}/{repo-name} --body-file /tmp/comment.md
```

Delete the temp file immediately after the `gh` call completes — do not leave stale files in `/tmp/` or `.claude/agents/tmp/`.
