<!-- Shared logic: templates/shared/workflows/Sprint_Workflow_Shared_template.md -->

## Story Discovery (Strict mode)

Glob `{{AGENT_DIR_PREFIX}}/agents/docs/stories/*.md`, read each file, filter by `**Status:** ready`. Sort by `**Sprint:**` field then by story ID (ascending). Process in that order.

---

## Strict-Mode Pre-Flight (run once before first story)

1. Identify the sprint name from the first `status:ready` story's `**Sprint:**` field (e.g., `sprint-1`)
2. Read the story's immutable `Project Base Branch:` value. If missing, stop for explicit user selection; never infer it from checkout.
3. If `sprint-N-dev` is missing, run `branch_preflight.py inspect --mode strict --base <Project Base Branch> --story-branch sprint-N-dev`, then `create` with its full verified SHA. If it already exists, switch to it and run `inspect --mode strict --base sprint-N-dev --story-branch <next-story-branch>`; this verifies resume safety without treating the sprint branch as a new story-branch target.
4. Only after successful create or resumed verification, store `Sprint Branch: sprint-N-dev` and its full SHA. Set every story's execution `Base Branch: sprint-N-dev` and Verified Base SHA to that result; record no Story Branch until its own successful create/verification.

---

## Strict-Mode Sprint Complete Notification

When no more `status:ready` stories remain and before Batch Retro Review: notify the user:
`"Sprint N complete. All stories merged into sprint-N-dev. Review and merge that branch into your own branch when ready — agents will not push or merge further."` Then proceed to Batch Retro Review.
