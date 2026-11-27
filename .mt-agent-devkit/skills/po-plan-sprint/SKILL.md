---
name: po-plan-sprint
description: Product Owner Plan Next Sprint procedure - verify the current sprint, select stories, questions file, sprint artifacts, release-gate sign-off, and the planning and backlog-refinement ceremonies.
---

# PO Plan Sprint

**Requires:** `po-core`, `po-write-story`, `po-plan-docs`, `sprint-status`, `po-roadmap-drain` (only when a roadmap changes)

Read `.mt-agent-devkit/workflows/Plan_Sprint_Workflow.md` for the pipeline rules before starting; the orchestrator always passes `feature_name`.

> **Plan sprint never promotes to `status:ready`.** Every planned story becomes `status:open`. Promotion belongs only to `refine sprint` Stage 4, after implementers confirm all questions are resolved (`po-promote-ready`).

## Ceremonies and Decisions

- **Sprint Planning:** confirm the sprint goal and clarify AC before stories enter the sprint.
- **Backlog Refinement:** keep the next sprint's backlog refined; break epics into stories of at most 13 points.
- **Sprint backlog finalization**, before each Sprint Planning, is yours; never delegate it.
- **Release gate:** approve cutting a devkit release when every Must-Have story in the sprint is done. The release is a manual `release` workflow dispatch; that job computes the version, never you.

## Steps

1. **Check sprint labels first** (`sprint-status` section 6). Violations: report every one to the orchestrator and wait until the user chooses to continue; change no label without the user's confirmation.
   **Then verify the current sprint is done and the next one is not planned** (`sprint-status` sections 1 to 4). Any failure: report the story IDs to the orchestrator and stop.
2. **Select stories:** `gh issue list --repo mycom08/mt-agent-devkit --label "status:backlog" --state open --limit 1000`; a feature adds `--label "feature:<feature_name>"`. No feature match: a `plan/` roadmap continues from that roadmap; otherwise report and stop, planning nothing.
   - Order: a `plan/` roadmap's dependency graph; a feature without one by `phase-N`, then `**Depends on:**` (done or in the same sprint), then priority; else `Must-Have`, `Should-Have`, `Nice-to-Have`.
3. **Open questions:** for each selected story, check that AC is clear and testable. If questions exist, create `{RUNTIME_ROOT}/tmp/PO_questions.md` and report to the orchestrator.
4. **Review answers:** after the orchestrator confirms answers are filled in, verify every `A:` field is complete before proceeding.
5. **Write sprint artifacts:**
   1. Labels are the only sprint artifact; write no backlog file.
   2. Stories without GitHub Issues: create them per `po-write-story` with `--body-file`; labels `status:open` + `sprint-N` (+ `feature:<feature_name>`, `phase-N`). Never for a feature without a `plan/` roadmap: only Analyze Requirements Stage 8 creates analysed stories.
   3. Stories that already have issues: add `sprint-N` if missing and replace `status:backlog` with `status:open`; **never set `status:ready`**.
   4. Delete `{RUNTIME_ROOT}/tmp/PO_questions.md` if it exists.
   5. Update your Working Record (`po-core`).
