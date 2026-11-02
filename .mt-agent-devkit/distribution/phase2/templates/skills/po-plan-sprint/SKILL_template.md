---
name: po-plan-sprint
description: Product Owner Plan Next Sprint procedure - verify the current sprint, select stories, questions file, sprint artifacts, release-gate sign-off, and the planning and backlog-refinement ceremonies.
---

# PO Plan Sprint

**Requires:** `po-core`, `po-write-story`, `po-plan-docs`, `po-roadmap-drain` (only when a roadmap changes)

Read `.mt-agent-devkit/workflows/Plan_Sprint_Workflow.md` for the pipeline rules and sprint capacity before starting. The orchestrator always passes `feature_name` (a feature such as `payments`, or `none`); it drives every path and label below.

> **Plan sprint never promotes to `status:ready`.** Every planned story stays `status:backlog`. Promotion belongs only to `refine sprint` Stage 4 (`po-promote-ready`).

## Ceremonies and Decisions

- **Sprint Planning:** confirm the sprint goal and clarify AC before stories enter the sprint.
- **Backlog Refinement:** keep the next sprint's backlog refined; break epics into stories of at most 13 points.
- **Sprint backlog finalization**, before each Sprint Planning, is yours; never delegate it.
- **Release gate:** approve the release when every Must-Have criterion is met (full criteria in the feature's Implementation Roadmap). The Sprint Workflow's Sprint end Release Decision asks you with the current `VERSION` and pending `CHANGELOG.md` entries; declining is normal. Report sprint progress and release risks against the roadmap.

## Steps

1. **Verify the current sprint is done.** Feature sprint: find the `🔄 In Progress` sprint in `docs/feature/<feature_name>/plan/Product_Backlog.md`, read its `Sprint_N_Overview.md`, and confirm every story is `status:done`; if `Sprint_{N+1}_Overview.md` already exists, report and stop. Non-feature sprint: `gh issue list --label "status:in-progress" --label "status:review" --label "status:testing" --state open`. Any story not done: report its ID and stop.
2. **Select stories.** Feature sprint: read the `*Roadmap*.md` and backlog; respect dependency order (no story whose dependency is not done). Non-feature: `gh issue list --label "status:backlog" --state open`, ordered `Must-Have`, `Should-Have`, `Nice-to-Have`. Note ID, title, points, priority and assigned role.
3. **Open questions:** AC clear and testable? Design (TL), requirements (BA), feasibility (Dev), testability (QA)? If any, create `{RUNTIME_ROOT}/tmp/PO_questions.md` in the workflow's format and report who must answer.
4. **Review answers:** verify every `A:` field is complete; if anything is unclear, report rather than guess.
5. **Write sprint artifacts:**
   1. Feature sprint: create `Sprint_{N+1}_Overview.md` in the existing format and add the sprint to `Product_Backlog.md` as `🔲 Planned`; commit per `po-plan-docs`. Non-feature: labels are the only artifact.
   2. Stories without a record: create them per `po-write-story`.
   3. Existing stories: add `sprint-N` if missing; **never change `status:backlog` to `status:ready`**.
   4. Delete `{RUNTIME_ROOT}/tmp/PO_questions.md` if it exists.
   5. Update your Working Record (`po-core`).
