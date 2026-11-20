---
name: tl-review
description: Technical Lead approval authority - the Reviewer Gate, the TL-only review checklist, the CI/workflow and documentation story variants, and the merge gate. Load when assigned as Stage 2 reviewer or otherwise reviewing a PR, after pr-review.
---

# TL Review

**Requires:** `pr-review` (shared reviewer procedure; load it first), `clean-code` (source changes), `credential-gate` (credential evidence)

You are the review gate: your approval moves the story to QA testing; the orchestrator merges after QA passes, so never instruct anyone to merge. You cannot approve your own work; seek a second reviewer.

## 1. Reviewer Gate (before approving)

Pending CI follows `pr-review` step 3 (ci-watch, exact head, strict mode). Tick each before approving:

- [ ] All CI checks on the PR have **finished**.
- [ ] No CI check is **failed**, and a test suite ran a non-zero test count.
- [ ] **Zero checks reported is not passing evidence.** Apply the explicit zero-check exception in `Shared_Pipeline_Stages.md` Merge Procedure: record suppression/path eligibility, prior SHA/current head and the complete changed-file scope. A helper prior candidate stays NO RUN until that evidenced decision; no prior success or missing evidence is silently waived.
- [ ] The review criteria below pass.

## 2. Review Checklist (TL-only, on top of `pr-review`)

- For long local verification use `.mt-agent-devkit/contracts/Local_Verify.md`: the full required command, selected provider bindings and a new run ID. Launch once; resume only supported waits on that identity; missing completion is not success.
- **Dependency pin:** a changed or new version pin must be resolvable from the shared registry the CI runner uses (check the publish/release job's run history), not only present in a local build cache.
- **Resume-rule completeness (state-file or pipeline stories):** a new state field, status value or step in a resumable workflow needs a resume branch for every value its write rules can produce.
- **Citation accuracy:** before citing a rule as `<file> §N`, open the file; a `grep -n` hit is a line number, not a section number.
- Verify compliance with `docs/wiki/Development_Standards.md` and the approved implementation design. Check data isolation, error format, test coverage and migration correctness.
- **Source code changes only:** verify the `clean-code` skill.
- **UI Prototype PRs** (a repo with or paired with a `-ui-prototype` repo): apply `.mt-agent-devkit/rules/UI_Prototype_Rules.md` before approving a screen with a prototype counterpart.
- **Approve** by PR comment when all criteria pass; leave blocking comments if not. Change requests and notices: `pr-review` steps 5-7. Strict mode: post the verdict as a story comment entry.

## 3. CI/Workflow Stories (Technical Scope is `.github/workflows/**` only)

Use this checklist instead of section 2:

- Gate-logic correctness (job-level vs step-level `if`).
- Secret and credential scope: no wider access than the job needs.
- Blast radius: no unrelated job or trigger changes behavior.
- Rollback safety: revertible without side effects.
- The `pr-review` CI gate still applies.

Skip naming, entity conventions, migration correctness, layering, clean-code review and domain-specific NFR design questions.

## 4. Refactor and Clean Code Stories (no API surface change)

Use this instead of section 2: old symbol fully removed, all call sites updated, a test exercises the changed path, CI passes cleanly. Skip spec diff, migration risk and backward-compatibility checks.

## 5. Documentation Stories (no source, migrations or API spec changes)

Focus on `pr-review` stale-reference and deleted-file criteria, plus:

- **Accuracy:** the document reflects the current implementation; cross-check key claims against source files.
- **Section completeness:** each AC-specified section covers what the AC requires, not only names.
- **Audience fit:** plain language beside technical detail for non-technical readers.
