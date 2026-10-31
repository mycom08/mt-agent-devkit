---
name: po-plan-sprint
description: Product Owner Plan Next Sprint procedure - verify the current sprint, select stories, questions file, sprint artifacts, release-gate sign-off, and the planning and backlog-refinement ceremonies.
---

# PO Plan Sprint

**Requires:** `po-core`, `po-write-story`, `po-plan-docs`, `po-roadmap-drain` (only when a roadmap changes)

Read `.mt-agent-devkit/workflows/Plan_Sprint_Workflow.md` for the pipeline rules before starting; the orchestrator always passes `feature_name`.

> **Plan sprint never promotes to `status:ready`.** Every planned story stays `status:backlog`. Promotion belongs only to `refine sprint` Stage 4, after implementers confirm all questions are resolved (`po-promote-ready`).

## Ceremonies and Decisions

- **Sprint Planning:** confirm the sprint goal and clarify AC before stories enter the sprint.
- **Backlog Refinement:** keep the next sprint's backlog refined; break epics into stories of at most 13 points.
- **Sprint backlog finalization**, before each Sprint Planning, is yours; never delegate it.
- **Release gate:** approve cutting a devkit release when every Must-Have story in the sprint is done. The release is a manual `release` workflow dispatch; that job computes the version, never you.

## Steps

1. **Verify the current sprint is done:** `gh issue list --repo mycom08/mt-agent-devkit --label "status:in-progress" --label "status:review" --label "status:testing" --state open`. Any story not done: report its ID to the orchestrator and stop.
2. **Select stories:** `gh issue list --repo mycom08/mt-agent-devkit --label "status:backlog" --state open`; order `Must-Have`, then `Should-Have`, then `Nice-to-Have`.
3. **Open questions:** for each selected story, check that AC is clear and testable. If questions exist, create `{RUNTIME_ROOT}/tmp/PO_questions.md` and report to the orchestrator.
4. **Review answers:** after the orchestrator confirms answers are filled in, verify every `A:` field is complete before proceeding.
5. **Write sprint artifacts:**
   1. Create `docs/sprints/Sprint_{N+1}_Overview.md`.
   2. Update `docs/plan/Product_Backlog.md`; commit each plan file per `po-plan-docs`.
   3. Stories without GitHub Issues: create them per `po-write-story` with `--body-file`; labels `status:backlog` + `sprint-N`.
   4. Stories that already have issues: add `sprint-N` if missing; **do not change `status:backlog` to `status:ready`**.
   5. Delete `{RUNTIME_ROOT}/tmp/PO_questions.md` if it exists.
   6. Update your Working Record (`po-core`).
