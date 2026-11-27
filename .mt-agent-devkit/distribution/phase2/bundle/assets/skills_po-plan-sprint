---
name: po-plan-sprint
description: Product Owner Plan Next Sprint procedure - verify the current sprint, select stories, questions file, sprint artifacts, release-gate sign-off, and the planning and backlog-refinement ceremonies.
---

# PO Plan Sprint

**Requires:** `po-core`, `po-write-story`, `po-plan-docs`, `sprint-status`, `po-roadmap-drain` (only when a roadmap changes)

Read `.mt-agent-devkit/workflows/Plan_Sprint_Workflow.md` for the pipeline rules and sprint capacity first. The orchestrator passes `feature_name` (a feature, or `none`).

> **Plan sprint never promotes to `status:ready`.** Every planned story becomes `status:open`. Only `refine sprint` Stage 4 promotes (`po-promote-ready`).

## Ceremonies and Decisions

- **Sprint Planning:** confirm the sprint goal and clarify AC before stories enter the sprint.
- **Backlog Refinement:** keep the next sprint's backlog refined; break epics into stories of at most 13 points.
- **Sprint backlog finalization**, before each Sprint Planning, is yours; never delegate it.
- **Release gate:** approve the release when every Must-Have criterion is met (full criteria in the feature's Implementation Roadmap). The Sprint Workflow's Sprint end Release Decision asks you with the current `VERSION` and pending `CHANGELOG.md` entries; declining is normal. Report progress and release risks against the roadmap.

## Steps

1. **Check sprint labels first** (`sprint-status` section 6). Violations: report all, wait for the user's choice to continue; change nothing unconfirmed.
   **Then verify the current sprint is done and the next one is not planned** (`sprint-status` sections 1 to 4). Any failure: report story IDs, stop.
2. **Select stories**; note ID, title, points, priority, role.
   - **GitHub mode:** `gh issue list --label "status:backlog" --state open --limit 1000`; a feature adds `--label "feature:<feature_name>"`. No feature match and no `plan/` roadmap: report and stop. Order: `plan/` roadmap graph; feature without one: `phase-N`, `**Depends on:**` (done or same sprint), priority.
   - **Strict mode:** feature: read `*Roadmap*.md` and backlog; no story whose dependency is not done. Non-feature: workflow Stage 2.
   - Else order `Must-Have`, `Should-Have`, `Nice-to-Have`.
3. **Open questions:** AC testable? Design (TL), requirements (BA), feasibility (Dev), testability (QA)? If any, create `{RUNTIME_ROOT}/tmp/PO_questions.md` in the workflow's format; report who must answer.
4. **Review answers:** every `A:` field complete; report anything unclear, never guess.
5. **Write sprint artifacts:**
   1. GitHub mode: labels only. Strict mode: feature adds the sprint to `Product_Backlog.md` as `🔲 Planned`, creates `Sprint_{N+1}_Overview.md` in the existing format, commits per `po-plan-docs`; non-feature: workflow Stage 4.
   2. Stories without a record: create them per `po-write-story`; never for a GitHub-mode feature without a `plan/` roadmap.
   3. Existing stories: add `sprint-N` and set `status:open` (replacing `status:backlog`); **never set `status:ready`**.
   4. Delete `{RUNTIME_ROOT}/tmp/PO_questions.md` if it exists.
   5. Update your Working Record (`po-core`).
