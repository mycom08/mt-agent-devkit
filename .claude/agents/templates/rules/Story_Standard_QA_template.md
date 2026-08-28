# Story Standard — QA View

> QA working rules for story work. This is your day-to-day reference. `{{AGENT_DIR_PREFIX}}/agents/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

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

Only when a bug is found after story is `status:done` — steps in `QA_Rules_Read_On_Demand.md` §3. Otherwise skip.

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
- **One topic per comment** — a finding outside the AC you were asked to validate gets its own comment, not a paragraph inside the validation report.
- **Writing standard:** decision-first (first line = the verdict), evidence by pointer, corrections state the delta only, no comments about comments, one close-out line per thread. **Never paste raw command output or test transcripts** — one-line verdict per AC, full logs in your working record. **Draft to shape:** one line per AC — criterion, verdict, pointer. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rule: `Story_Standard.md §9`.
- **Exemption — yours alone:** per-AC validation reports may exceed the general ~150–200 word cap; thorough per-AC evidence is high-signal and expected. The gate's `wc -w` item is satisfied by stating the exemption in the comment — it is an exemption from the *cap*, not from the transcript and one-topic rules, which still apply.

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms

**QA:** Test each AC criterion and report pass/fail in a Comment. Do **not** tick checkboxes. Notify PO when all AC have passed.
