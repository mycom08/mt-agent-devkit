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

1. **Verify the current sprint is done and the next one is not planned.** Any failure: report the story IDs and stop.
   - **GitHub mode:**
     1. In-flight: three separate queries, `gh issue list --label "<status>" --state open --limit 1000 --json number,title,labels` for `status:in-progress`, `status:review` and `status:testing` (repeated `--label` flags require all). Any result is unfinished.
     2. Sprint N: feature sprint, the `🔄 In Progress` sprint in `docs/feature/<feature_name>/plan/Product_Backlog.md`. Non-feature: the highest `sprint-N` label, compared numerically, over those results and `gh issue list --label "status:done" --state all --limit 1000 --json labels`; none means N = 0.
     3. Done: every issue from `gh issue list --label "sprint-N" --state open --limit 1000 --json number,title,labels` carries `status:done`.
     4. Guard: any result from `gh issue list --label "sprint-{N+1}" --state open --limit 1` means it is already planned.
   - **Strict mode:** feature sprint: find the `🔄 In Progress` sprint in that `Product_Backlog.md`, read its `Sprint_N_Overview.md`, and confirm every story is `status:done`; if `Sprint_{N+1}_Overview.md` already exists, report and stop. Non-feature: workflow Stage 1.
2. **Select stories.** Feature sprint: read the `*Roadmap*.md` and backlog; respect dependency order (no story whose dependency is not done). Non-feature: GitHub mode `gh issue list --label "status:backlog" --state open --limit 1000`, strict mode workflow Stage 2; order `Must-Have`, `Should-Have`, `Nice-to-Have`. Note ID, title, points, priority and role.
3. **Open questions:** AC clear and testable? Design (TL), requirements (BA), feasibility (Dev), testability (QA)? If any, create `{RUNTIME_ROOT}/tmp/PO_questions.md` in the workflow's format and report who must answer.
4. **Review answers:** verify every `A:` field is complete; if anything is unclear, report rather than guess.
5. **Write sprint artifacts:**
   1. Feature sprint: add the sprint to `Product_Backlog.md` as `🔲 Planned`; strict mode also creates `Sprint_{N+1}_Overview.md` in the existing format; commit per `po-plan-docs`. Non-feature: GitHub mode labels are the only artifact; strict mode follows workflow Stage 4.
   2. Stories without a record: create them per `po-write-story`.
   3. Existing stories: add `sprint-N` if missing; **never change `status:backlog` to `status:ready`**.
   4. Delete `{RUNTIME_ROOT}/tmp/PO_questions.md` if it exists.
   5. Update your Working Record (`po-core`).
