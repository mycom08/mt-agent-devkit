# Story Standard — QA View

> Role-specific excerpt from `.claude/agents/rules/STORY_STANDARD.md` (v1.8). Read this instead of the full file.

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
1. **Verify the API spec** (`docs/api/`) for every endpoint being tested — use spec as the reference, not live behavior. If spec is missing or inconsistent, post a Comment tagging **TL** before testing
2. Read story AC from the GitHub Issue body
3. Run integration test script: `bash tests/feature/.../ST-XXXXXX_*.sh` (see `docs/wiki/Testing_Guidelines.md`)
4. Test each criterion against live code, cross-referencing the API spec
5. Report verification results per AC in a comment (do **NOT** tick checkboxes — only PO ticks)
6. If AC fails: Comment describing the issue; request Dev fix

### Status: Testing → Done
1. Confirm dev branch is merged to feature branch; if not, notify Dev and wait
2. All AC verification results reported in Comment
3. Notify PO that all AC have passed — PO ticks the checkboxes
4. Remove `status:testing`, add `status:done`

---

## 6. Hotfix (Post-Done Bug) — QA Role

When a bug is found after story is `status:done`:

1. **Report:** Post Comment on original issue describing the bug; tag Dev and TL
2. After Dev creates a fix branch and fix PR → **re-test** all affected AC against the API spec
3. Report re-test results in Comment; notify PO

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **QA** | Test AC, report results in Comment, notify PO when all AC pass | Tick AC, review code, approve stories |

**Red Flags:** QA ticking AC checkboxes (only PO, after QA confirms); QA commenting on code design instead of AC fitness.

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Endpoint / AC / Section / File]

**QA - YYYY-MM-DD**
Test results and findings per AC.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- Report per-AC test results in a single comment per story
- Reply in the same thread when re-testing or following up on the same issue
- **Never use the `@` prefix** — write role names without it (e.g., `**Dev**`, `**TL**`). An `@` prefix triggers a GitHub mention to a real user account.
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text. A bare `#` creates a GitHub cross-reference to an unrelated issue or PR.

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**QA:** Test each AC criterion and report pass/fail in a Comment. Do **not** tick checkboxes. Notify PO when all AC have passed.

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
