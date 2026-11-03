---
name: comment
description: Comment standard for every agent role - the comment template and Thread Status, writing rules, the @ and bare # bans, announcing body edits, the Commenter gate and the gh pr checks carve-out. Load before posting any story or PR comment.
---

# Comment

Canonical owner of the comment standard for every role (Developer, Technical Lead, QA, Product Owner, Business Analyst, UI/UX Designer). Role rules add only what their role alone does; they never restate this file.

## Where comments go

All discussion happens as comments, never inside the story body.
- **GitHub mode:** a comment on the GitHub Issue (code review feedback may also be a PR comment).
- **Strict mode:** an entry in the story file's `## Comments` section (`{RUNTIME_ROOT}/docs/stories/ST-XXXXXX.md`, format in `Strict_Mode_Story_Guide.md`); read "issue comment" as "comment entry".

Use comments for scope questions, AC clarifications, technical decisions, blocker escalations and implementation issues.

## Template

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved
**Area:** [Endpoint / AC / Section / File]

**<Role> - YYYY-MM-DD**
Question, decision or finding.

**Decision:** [What we decided and why]
**Next:** [Owner or "None"]
```

**Thread Status** is the status of this discussion thread, independent of the story label. `<Role>` is your role name (`Developer`, `TL`, `QA`, `PO`, `BA`, `UI/UX Designer`); replies append their own author line.

## Writing rules

1. **Decision-first.** The first line states the decision or outcome. Rationale follows, at most 2–3 sentences per point.
2. **One topic per comment.** Answer the questions asked and nothing else. A finding that surfaces while answering posts as its own comment with its own Thread Status; a bundled thread cannot be resolved while any of its topics stays open. Replying to several questions genuinely asked together is fine.
3. **Length cap: about 150–200 words**, checked with `wc -w` at the Commenter gate. **Draft to the shape, not to the counter:** one short paragraph per topic (decision, one-line why, pointer). If the check fails by more than a little, you bundled a second topic or pasted a transcript: remove it whole, do not compress everything. Role exemptions are named in the role's own rules.
4. **Evidence by pointer, not transcript.** Applies to issue and PR comments alike. Cite what was checked (file or doc name plus a one-line result); full logs go in your working record. **Never paste command output, check transcripts or verification logs.**
   > **Single carve-out:** the literal `gh pr checks <PR-number>` output that the Reviewer gate (`Story_Standard.md §12`) requires in a **PR approval comment**. Nothing else may be pasted, in any comment, by any role. Strict mode has no PRs, so nothing is exempt there.
5. **Body edits are announced, not reproduced.** When a comment's decision is written into the story body in the same pass, state which section changed, what kind of change and why, never the resulting body text, which would go stale at the next edit. Example: "AC6 reworded — added an X carve-out, per the reviewer's point that <reason>. Body updated." The body edit itself follows `Story_Standard.md §3` (Body Amendments).
6. **Corrections state the delta only.** What changed, what didn't, one-line why.
7. **No comments about comments.** If a prior comment lacked substance, put the substance in your working record and post one pointer line.
8. **One close-out per thread.** Post the resolved or ready hand-off line once; never restate it.
9. **Default format:** compact bullets, claim → source checked → verdict. Not a license for thinner review.

**Thread and body:**
- Reply in the same thread for the same topic; a new topic gets its own comment (rule 2).
- When a comment changes scope, AC or delivery expectations, including a design-first approval that narrows or supersedes an AC, update the story body in the **same pass**.
- **Never use the `@` prefix**: write role names without it (`**TL**`, `**PO**`, `**Dev**`). It notifies a real user account.
- **Never use a bare `#` prefix**: use `ST-XXXXXX` or plain text. It cross-links an unrelated issue or PR.

## Commenter gate

Run on every comment, every role.

**Before you draft:**
- [ ] Shape chosen: one short paragraph per topic — decision, one-line why, pointer (rule 3)

**Before you post:**
- [ ] Answers only the questions asked; a new finding gets its own comment (rule 2)
- [ ] No command output, transcript or log pasted; the `gh pr checks` carve-out covers PR approval comments only (rule 4)
- [ ] A body edit made in this pass is announced, not reproduced (rule 5)
- [ ] Facts already in your memory file are cited, not re-explained (`Agent_Common_Read_On_Demand.md §1` rule 4)
- [ ] No `@` or bare `#` prefix
- [ ] Word count checked: `wc -w` ≤ 200, or your role's stated exemption noted in the comment

**Only then:** post the comment.
