---
name: po-validate-ac
description: Stage 3 validation when QA is the implementer - the Product Owner exercises each AC independently and writes the per-AC validation report the acceptance gate requires before merge.
---

# PO Validate AC

**Requires:** `po-core`, `po-comment`. **Cites:** `Story_Standard.md §14`.

Applies when the story's `Implementer` is `QA` (Shared Pipeline Stage 3 step 1). No separate QA agent runs, so the PO is the independent validator and the only evidence producer; the orchestrator merges on this report.

1. Read `Story_Standard.md §14` and the current canonical story scope: every remaining AC, the Technical Scope and the PR diff at its current head.
2. Exercise each AC independently, with its required method, against the artifact being merged. The implementer's claims, green automation or reviewer approval never stand in for an unexercised AC.
3. Write the per-AC report as one issue comment (`po-comment`): for each AC its identity, verdict (`PASS`, `FAIL` or `NOT VERIFIED`), evidence pointer, tested scope/revision, and any reason or missing evidence.
4. Any FAIL, NOT VERIFIED or insufficient evidence stops advancement: state what is missing. Never reinterpret an earlier NOT VERIFIED as PASS.
5. Report to the orchestrator: the per-AC verdicts and the report comment link.

Do not tick AC checkboxes; that is Stage 4 (`po-verify-close`).
