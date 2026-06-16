# Story Standard — QA View

> QA working rules for story work. This is your day-to-day reference. `.claude/agents/working/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When |
|--------|-------------|------|
| Testing | QA | After TL approval & merge |
| **Done** | PO (after QA confirms) | After all AC pass and PO ticks |

**QA moves story to `status:done` after merge is confirmed and all AC pass.**

---

## 5. QA Workflow

### Status: Testing
1. Read story AC from the GitHub Issue body
2. Validate each criterion against the changed files or behavior described in the PR
3. Report verification results per AC in a comment (do **NOT** tick checkboxes — only PO ticks)
4. If AC fails: Comment describing the issue; request Dev fix

### Status: Testing → Done
1. Confirm dev branch is merged to main; if not, notify Dev and wait
2. All AC verification results reported in Comment
3. Notify PO that all AC have passed — PO ticks the checkboxes
4. Remove `status:testing`, add `status:done`

---

## 6. Hotfix (Post-Done Bug) — QA Role

When a bug is found after story is `status:done`:

1. **Report:** Post Comment on original issue describing the bug; tag Dev and TL
2. After Dev creates a fix branch and fix PR → **re-validate** all affected AC
3. Report re-test results in Comment; notify PO

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **QA** | Validate AC, report results in Comment, notify PO when all AC pass | Tick AC, review code, approve stories |

**Red Flags:** QA ticking AC checkboxes (only PO, after QA confirms); QA commenting on technical design instead of AC fitness.

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Workflow / Template / AC / File]

**QA - YYYY-MM-DD**
Validation results and findings per AC.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- Report per-AC validation results in a single comment per story
- Reply in the same thread when re-validating or following up on the same issue
- **Never use the `@` prefix** — write role names without it (e.g., `**Dev**`, `**TL**`)
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**QA:** Validate each AC criterion and report pass/fail in a Comment. Do **not** tick checkboxes. Notify PO when all AC have passed.

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Always use Bash (not PowerShell) for all `gh` CLI calls.** Never prepend `cd /path` to a command; the working directory is already set.

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:

```bash
gh issue edit <number> --repo mycom08/mt-agent-devkit --body-file /tmp/body.md
gh issue comment <number> --repo mycom08/mt-agent-devkit --body-file /tmp/comment.md
```

Delete the temp file immediately after the `gh` call completes.
