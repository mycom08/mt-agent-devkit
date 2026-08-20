# Story Standard — Technical Lead View

> Technical Lead working rules for story work. This is your day-to-day reference. `.claude/agents/working/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When |
|--------|-------------|------|
| Backlog | PO | After creation |
| Ready | PO | After assigning |
| In Progress | Implementer | Dev branch created |
| **Review** | Implementer | After PR created — **TL reviews here** |
| **Testing** | TL (notifies QA) | After TL approval & merge |
| Done | PO | After all AC pass |

---

## 2. Story Structure (reference)

Story body contains: `**Assigned:**` field above `## User Story`, `## Acceptance Criteria`, `## Deliverables`. All discussions happen as **comments** on the issue.

---

## 4. TL as Implementer

Only when `**Assigned:** Technical Lead` and TL is running Stage 1 (implementation) — status-transition steps and peer-notify template in `Technical_Lead_Rules_Extended.md §4`. Otherwise skip.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **TL** | Review code, approve PR, discuss technical design, implement when assigned | Tick AC, test, clarify scope |

**Red Flags:** ticking AC checkboxes; commenting on scope (PO's) — see `Technical_Lead_Rules.md §2` for the AC-clarification-edit distinction; self-approving a PR (blocked — use `gh pr comment`).

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Workflow / Template / AC / File]

**TL - YYYY-MM-DD**
Technical decision or review feedback.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- Post code review changes as **inline PR comments** + a brief notify comment on the GitHub Issue
- Reply in the same thread for the same topic
- **Never use the `@` prefix** — write role names without it (e.g., `**Dev**`, `**PO**`)
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text
- **One topic per comment** — answer the questions asked and nothing else. A finding that surfaces *while* reviewing — however relevant — posts as its own comment with its own thread status; a bundled thread cannot be resolved while any of its topics stays open. Batching replies to questions asked together is fine.
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, cap ~150–200 words, draft to shape rather than trim-and-recount; evidence by pointer — **never paste command output, check transcripts, or verification logs**, state the verdict in one line and cite your working record; carve-out: paste the literal `gh pr checks <PR-number>` output when it's the §12 Reviewer gate's PR approval comment — nothing else gets pasted; facts already recorded in your memory file are cited, not re-explained (`Agent_Common_Records.md §1` rule 4); corrections state the delta only; no comments about comments; one close-out line per thread. Story-body edits: decision itself, ≤ 5 lines, pointer to the resolving comment — announce, never reproduce. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rules: `Story_Standard.md §3 (Body Amendments), §9`.

---

## 12. Reviewer Gate — before approving a PR

- [ ] All CI checks on the PR have **finished**
- [ ] No CI check is in a **failed** state
- [ ] **Zero checks reported ≠ CI failing.** Check whether the head commit is path-filtered/`[skip ci]` (docs-only) — if so, that's "nothing runnable changed," proceed. If the commit touched CI-relevant paths and still shows zero checks, CI is genuinely missing — do not approve without a real run or an explicit deviation note
- [ ] Code review criteria pass (per `Technical_Lead_Rules.md §2`)

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Always use Bash (not PowerShell) for all `gh` CLI calls.** Never prepend `cd /path` to a command; the working directory is already set.

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:

```bash
gh issue edit <number> --repo mycom08/mt-agent-devkit --body-file /tmp/body.md
gh issue comment <number> --repo mycom08/mt-agent-devkit --body-file /tmp/comment.md
```

Delete the temp file immediately after the `gh` call completes.
