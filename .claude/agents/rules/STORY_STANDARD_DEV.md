# Story Standard — Developer View

> Role-specific excerpt from `.claude/agents/rules/STORY_STANDARD.md` (v1.8). Read this instead of the full file.

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
2. Run integration test script: `bash tests/feature/.../ST-XXXXXX_*.sh` (see `docs/wiki/Testing_Guidelines.md`)
3. Source files follow naming standard (no `interface.go`, `helpers.go`, `types.go`)
4. Create PR with title: `[ST-XXXXXX][FEATURE] Story title`
5. Remove `status:in-progress`, add `status:review`
6. Request TL review in issue Comment

### Status: Review → In Progress (TL feedback)
1. Address feedback in dev branch
2. Push new commits
3. Re-request review in issue Comment

### Status: Review → Testing (after TL approval)
1. Remove `status:review`, add `status:testing`
2. Add PR/commit links in issue Deliverables section (edit issue body)
3. Notify QA in issue Comment

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

❌ Bad: `interface.go`, `types.go`, `helpers.go`, `errors.go`, `utils.go`

✅ Good: `rule_evaluator.go`, `evaluation_types.go`, `condition_helpers.go`, `validation_errors.go`

**Rule:** Name after the primary interface/struct; use `snake_case`.

---

## 12. Merge Gate Checklist

Before merging dev branch to feature branch:

- [ ] API spec verified — implementation matches spec for all affected endpoints
- [ ] Self-checked all AC locally (do NOT tick checkboxes)
- [ ] Integration test script exists and passes via Git Bash
- [ ] Service starts locally (`go run ./cmd/server`)
- [ ] Source files have good names (no `interface.go`, etc.)
- [ ] Code follows Development Standard
- [ ] PR created with story ID in title: `[ST-XXXXXX][FEATURE] ...`
- [ ] TL has reviewed and approved PR ✓

---

## 15. GitHub Issue CLI — PowerShell Safety Rule

**Never** pass multi-line or backtick-containing Markdown via `--body "..."`. Always write to a temp file:

```powershell
$body = @'
## Acceptance Criteria

- [ ] `field` uses `x-go-type: json.RawMessage`
'@

$tmp = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tmp, $body, [System.Text.Encoding]::UTF8)
gh issue edit <number> --body-file $tmp
gh issue comment <number> --body-file $tmp
Remove-Item $tmp
```

**Applies to:** `gh issue edit`, `gh issue create`, `gh issue comment` — any call with backticks, checkboxes, or multi-line content.
