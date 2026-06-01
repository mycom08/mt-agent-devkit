# Story Standard — Technical Lead View

> Role-specific excerpt from `.claude/agents/rules/STORY_STANDARD.md` (v1.8). Read this instead of the full file.

---

## 1. Story Status Workflow

| Status | Who Changes | When |
|--------|-------------|------|
| Backlog | PO | After creation |
| Ready | PO | After assigning to Developer |
| In Progress | Developer | Dev branch created |
| **Review** | Developer | After PR created — **TL reviews here** |
| **Testing** | TL (notifies QA) | After TL approval & merge |
| Done | PO | After all AC pass |

---

## 2. Story Structure (reference)

Story body contains: `**Assigned:**` field above `## User Story`, `## Acceptance Criteria`, `## Deliverables`. No technical specs or field lists in the body. All discussions happen as **comments** on the issue.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **TL** | Review code, approve PR, discuss technical design | Tick AC, test, clarify scope, implement |

**Red Flags:** TL ticking AC checkboxes; TL commenting on scope (PO only); TL self-approving PR (GitHub blocks it — use `gh pr comment` instead).

---

## 8. Technical Doc Divergence Rule

When Dev flags a technical doc as inaccurate via a story comment:

| Severity | TL Action |
|----------|-----------|
| Blocks implementation | Fix the doc immediately; unblock Dev in the same comment thread |
| Non-blocking | Acknowledge in comment; fix after story completes |
| Ambiguous | Clarify the correct behavior definitively in the comment thread |

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Endpoint / AC / Section / File]

**TL - YYYY-MM-DD**
Technical decision or review feedback.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- Post code review changes as **inline PR comments** + a brief notify comment on the GitHub Issue
- Reply in the same thread for the same topic; do not open new threads for follow-up on the same question
- **Never use the `@` prefix** — write role names without it (e.g., `**Dev**`, `**PO**`). An `@` prefix triggers a GitHub mention to a real user account.
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text. A bare `#` creates a GitHub cross-reference to an unrelated issue or PR.

---

## 15. GitHub Issue CLI — PowerShell Safety Rule

**Never** pass multi-line or backtick-containing Markdown via `--body "..."`. Always write to a temp file:

```powershell
$body = @'
...content...
'@

$tmp = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tmp, $body, [System.Text.Encoding]::UTF8)
gh issue edit <number> --body-file $tmp
gh issue comment <number> --body-file $tmp
Remove-Item $tmp
```

**Applies to:** `gh issue edit`, `gh issue create`, `gh issue comment` — any call with backticks, checkboxes, or multi-line content.
