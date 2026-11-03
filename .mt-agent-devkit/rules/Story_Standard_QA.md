# Story Standard — QA View

> QA working rules for story work. This is your day-to-day reference. `.mt-agent-devkit/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

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
**Acceptance prerequisite:** Apply `Story_Standard.md §14` before notifying PO or changing status. Any FAIL, NOT VERIFIED, missing verdict, or insufficient evidence keeps the story unresolved; all remaining AC require current independent PASS evidence.

1. Confirm dev branch is merged to main; if not, notify Dev and wait
2. All AC verification results reported in Comment
3. Notify PO that all AC have passed — PO ticks the checkboxes
4. Remove `status:testing`, add `status:done`

---

## 6. Hotfix (Post-Done Bug) — QA Role

Only when a bug is found after story is `status:done` — steps in `QA_Rules_Read_On_Demand.md §3`. Otherwise skip.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **QA** | Validate AC, report results in Comment, notify PO when all AC pass | Tick AC, review code, approve stories |

**Red Flags:** ticking AC (PO's job, after QA confirms); commenting on technical design instead of AC fitness.

---

## 9. Comment Standard

Load the `comment` skill (`.mt-agent-devkit/skills/comment/SKILL.md`) before any comment; it owns the template, Thread Status, writing rules, prefix bans and the Commenter gate. QA-only additions:

- Report per-AC validation results in a single comment per story, one line per AC (criterion, verdict, pointer); reply in the same thread when re-validating.
- **Cap exemption, yours alone:** a per-AC validation report may exceed the ~150–200 word cap. State the exemption in the comment to satisfy the gate's `wc -w` item. It exempts the *cap* only, never the transcript or one-topic rules.

---

## 14. AC Checkbox Rules

Before reporting results, read `Story_Standard.md §14` for verdict definitions, examples, evidence requirements, and tracked-split ordering. Report each AC as PASS, FAIL, or NOT VERIFIED with evidence; NOT VERIFIED includes its reason and missing evidence. No testing-pass or done notification while any current AC remains unverified. Only PO accepts checkboxes.

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**QA:** Validate each AC criterion and report PASS/FAIL/NOT VERIFIED in a Comment. Do **not** tick checkboxes. Notify PO when all AC have passed.
