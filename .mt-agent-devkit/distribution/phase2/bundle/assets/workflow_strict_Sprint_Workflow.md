<!-- Shared logic: templates/shared/workflows/Sprint_Workflow_Shared_template.md -->

## Story Discovery (Strict mode)

Glob `{RUNTIME_ROOT}/docs/stories/*.md`, read each file, filter by `**Status:** ready`. Sort by `**Sprint:**` field then by story ID (ascending). Process in that order.

---

## Strict-Mode Pre-Flight (run once before first story)

For the selected Ready story, derive its intended story branch and check whether that local branch exists **before** switching to `sprint-N-dev` or calling `inspect`. If it exists, run the read-only Interrupted Stage 1 recovery check in `Shared_Pipeline_Stages.md` on the current checkout. A PASS resumes after `create`; a mismatch stops without switching or writing. Run the sprint setup below only when the story branch does not exist.

1. Identify the sprint name from the first `status:ready` story's `**Sprint:**` field (e.g., `sprint-1`)
2. Read the story's immutable `Project Base Branch:` value. If missing, stop for explicit user selection; never infer it from checkout.
3. If `sprint-N-dev` is missing, run `branch_preflight.py inspect --mode strict --base <Project Base Branch> --story-branch sprint-N-dev`, then `create` with its full verified SHA. If it already exists, switch to it and run `inspect --mode strict --base sprint-N-dev --story-branch <next-story-branch>`; this verifies resume safety without treating the sprint branch as a new story-branch target.
4. Keep the verified `Sprint Branch: sprint-N-dev` and full SHA in memory. For each story, run Story Base Preflight `inspect` before storing that story's execution `Base Branch: sprint-N-dev` and Verified Base SHA. Record no Story Branch until Stage 1 `create` succeeds.

---

## Strict-Mode Sprint Complete Notification

When no more `status:ready` stories remain and before Batch Retro Review: notify the user:
`"Sprint N complete. All stories merged into sprint-N-dev. Review and merge that branch into your own branch when ready — agents will not push or merge further."` Then proceed to Batch Retro Review.
