---
name: po-verify-close
description: Product Owner Stage 4 story closure - acceptance questions, evidence and elevated-verification checks, AC checkbox rules, closure-comment ordering, tick/label/close, and the sprint-review accept/reject decision.
---

# PO Verify Close

**Requires:** `po-core`, `po-comment`. **Cites:** `Story_Standard.md §14`.

Closure skips Project Priming and the Working Record (`po-core`). Accept or reject of each story, the sprint-review decision, is yours; never delegate it.

## Acceptance Questions

1. **All AC met?** Each checkbox is demonstrably satisfied.
2. **Definition of Done?** Reviewed, validated, no open comments.
3. **Backward compatible?** Target projects that ran `init project` are not broken without a migration path.

Any **No** → not accepted; state clearly what is missing.

## Evidence Check

1. Read the full story body and every AC checkbox.
2. Read `Story_Standard.md §14` and the applicable independent per-AC verification report for the current scope. Confirm PASS with sufficient evidence for every remaining AC. FAIL, NOT VERIFIED, absent verdicts, insufficient evidence or stale-scope sign-off stop closure before any checkbox or status write. An approved tracked split completes its sequence and renewed QA first; an earlier NOT VERIFIED never becomes PASS. A merged or auto-closed issue alone is not verification.
3. **Authoritative signal:** QA's final testing-pass comment on the issue. A Developer or TL comment alone is not sufficient.
4. **Elevated verification:** if the body names an explicit elevated or extra QA requirement (distinct from standard AC), QA's sign-off must address its named conditions; a generic "AC pass / tests green" is not enough.
5. **Implementer = validator:** when Stage 0 assigned one role to both and validation was skipped, the signal is the independent per-AC validation report (`po-validate-ac`) plus a confirmed merge. Reviewer approval alone cannot verify an unexercised AC.

## AC Checkbox Rules

- `- [ ]` = not yet signed off; `- [x]` = signed off by PO after QA confirms.
- Tick each AC `[x]` in the issue body with `--body-file` (`Agent_Common_Bootstrap.md §6`).

## Close

1. **Closure-comment ordering (github mode):** before any closure comment run `gh issue view <number> --json state --jq '.state'`. `CLOSED` (the PR's `Closes` keyword auto-closed it) → post the comment with a separate `gh issue comment`, never `gh issue close --comment`, which errors on a closed issue and drops the comment. `OPEN` → `gh issue close --comment` is safe.
2. Remove the current `status:*` labels, add `status:done`, and close the issue: `gh issue close <number> --repo mycom08/mt-agent-devkit`.
3. Evaluate `Agent_Common_Bootstrap.md §7`; only a required trigger loads the retrospective section and writes the PO contribution.
4. Do not write the Working Record. Record durable facts in PO memory (`po-core`).
