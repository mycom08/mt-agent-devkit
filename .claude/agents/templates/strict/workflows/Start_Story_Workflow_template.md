<!-- Shared logic: templates/shared/workflows/Start_Story_Workflow_Shared_template.md -->

## Strict-Mode Pre-Flight (for a new `status:ready` entry only)

Read the story status first. For `status:in-progress`, use the shared Stage Entry Check's resume path and existing state/branch; do not inspect or create a new story branch. For `status:review` or `status:testing`, enter the recorded review or QA stage. Run the following sprint setup only for `status:ready`.

For a Ready story, derive its intended story branch and check whether that local branch exists **before** switching to `sprint-N-dev` or calling `inspect`. If it exists, run the read-only Interrupted Stage 1 recovery check in `Shared_Pipeline_Stages.md` on the current checkout. A PASS resumes after `create`; a mismatch stops without switching or writing. Run the sprint setup below only when the story branch does not exist.

1. Read `{{AGENT_DIR_PREFIX}}/agents/docs/stories/ST-XXXXXX.md` to get the story's `**Sprint:**` field (e.g., `sprint-1`)
2. Read the story's immutable `Project Base Branch:` value. If missing, stop for explicit user selection; never infer it from checkout.
3. If `sprint-N-dev` is missing, run `branch_preflight.py inspect --mode strict --base <Project Base Branch> --story-branch sprint-N-dev`, then `create` with its full verified SHA. If it already exists, switch to it and run `inspect --mode strict --base sprint-N-dev --story-branch <this-story-branch>`; this verifies resume safety without treating the sprint branch as a new story-branch target.
4. Keep the verified `Sprint Branch: sprint-N-dev` and full SHA in memory. After Story Base Preflight `inspect` passes, record those values and this story's execution `Base Branch: sprint-N-dev`. Create the story branch only through Stage 1 `create` and record Story Branch only after its successful verification.
