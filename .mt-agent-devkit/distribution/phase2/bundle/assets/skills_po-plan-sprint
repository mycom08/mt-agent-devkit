---
name: po-plan-sprint
description: Product Owner Plan Next Sprint procedure - verify the current sprint, select stories, questions file, sprint artifacts, release-gate sign-off, and the planning and backlog-refinement ceremonies.
---

# PO Plan Sprint

**Requires:** `po-core`, `po-write-story`, `po-plan-docs`, `po-roadmap-drain` (only when a roadmap changes)

Read `.mt-agent-devkit/workflows/Plan_Sprint_Workflow.md` for the pipeline rules and sprint capacity first. The orchestrator passes `feature_name` (a feature, or `none`).

> **Plan sprint never promotes to `status:ready`.** Every planned story stays `status:backlog`. Only `refine sprint` Stage 4 promotes (`po-promote-ready`).

## Ceremonies and Decisions

- **Sprint Planning:** confirm the sprint goal and clarify AC before stories enter the sprint.
- **Backlog Refinement:** keep the next sprint's backlog refined; break epics into stories of at most 13 points.
- **Sprint backlog finalization**, before each Sprint Planning, is yours; never delegate it.
- **Release gate:** approve the release when every Must-Have criterion is met (full criteria in the feature's Implementation Roadmap). The Sprint Workflow's Sprint end Release Decision asks you with the current `VERSION` and pending `CHANGELOG.md` entries; declining is normal. Report progress and release risks against the roadmap.

## Steps

1. **Verify the current sprint is done and the next one is not planned.** Any failure: report story IDs, stop.
   - **GitHub mode** (feature or not, repo-wide):
     1. In-flight: separate queries, `gh issue list --label "<status>" --state open --limit 1000 --json number,title,labels` for `status:in-progress`, `status:review` and `status:testing` (repeated `--label` flags require all). Any result is unfinished.
     2. Sprint N: the highest `sprint-N` label, compared numerically, over those results and `gh issue list --label "status:done" --state all --limit 1000 --json labels`; none means N = 0.
     3. Done: every issue from `gh issue list --label "sprint-N" --state open --limit 1000 --json number,title,labels` carries `status:done`.
     4. Guard: any result from `gh issue list --label "sprint-{N+1}" --state open --limit 1` means already planned.
   - **Strict mode:** feature sprint: find the `🔄 In Progress` sprint in `docs/feature/<feature_name>/plan/Product_Backlog.md`, read its `Sprint_N_Overview.md`, confirm every story is `status:done`; if `Sprint_{N+1}_Overview.md` already exists, report and stop. Non-feature: workflow Stage 1.
2. **Select stories**; note ID, title, points, priority, role.
   - **GitHub mode:** `gh issue list --label "status:backlog" --state open --limit 1000`; a feature adds `--label "feature:<feature_name>"`. No feature match and no `plan/` roadmap: report and stop. Order: `plan/` roadmap graph; feature without one: `phase-N`, `**Depends on:**` (done or same sprint), priority.
   - **Strict mode:** feature: read `*Roadmap*.md` and backlog; no story whose dependency is not done. Non-feature: workflow Stage 2.
   - Else order `Must-Have`, `Should-Have`, `Nice-to-Have`.
3. **Open questions:** AC testable? Design (TL), requirements (BA), feasibility (Dev), testability (QA)? If any, create `{RUNTIME_ROOT}/tmp/PO_questions.md` in the workflow's format; report who must answer.
4. **Review answers:** every `A:` field complete; report anything unclear, never guess.
5. **Write sprint artifacts:**
   1. GitHub mode: labels only. Strict mode: feature adds the sprint to `Product_Backlog.md` as `🔲 Planned`, creates `Sprint_{N+1}_Overview.md` in the existing format, commits per `po-plan-docs`; non-feature: workflow Stage 4.
   2. Stories without a record: create them per `po-write-story`; never for a GitHub-mode feature without a `plan/` roadmap.
   3. Existing stories: add `sprint-N` if missing; **never change `status:backlog` to `status:ready`**.
   4. Delete `{RUNTIME_ROOT}/tmp/PO_questions.md` if it exists.
   5. Update your Working Record (`po-core`).
