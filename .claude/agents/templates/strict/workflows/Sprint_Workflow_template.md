<!-- Shared logic: templates/shared/workflows/Sprint_Workflow_Shared_template.md -->

## Story Discovery (Strict mode)

Glob `.claude/agents/docs/stories/*.md`, read each file, filter by `**Status:** ready`. Sort by `**Sprint:**` field then by story ID (ascending). Process in that order.

---

## Strict-Mode Pre-Flight (run once before first story)

1. Identify the sprint name from the first `status:ready` story's `**Sprint:**` field (e.g., `sprint-1`)
2. Check if the sprint dev branch exists: `git branch --list sprint-N-dev`
   - Exists → `git checkout sprint-N-dev`
   - Missing → `git checkout -b sprint-N-dev` (from the user's current branch at invocation time)
3. Store `Sprint Branch: sprint-N-dev` in the pipeline state file

---

## Strict-Mode Sprint Complete Notification

When no more `status:ready` stories remain and before Batch Retro Review: notify the user:
`"Sprint N complete. All stories merged into sprint-N-dev. Review and merge that branch into your own branch when ready — agents will not push or merge further."` Then proceed to Batch Retro Review.
