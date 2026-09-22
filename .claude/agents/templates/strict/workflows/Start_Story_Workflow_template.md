<!-- Shared logic: templates/shared/workflows/Start_Story_Workflow_Shared_template.md -->

## Strict-Mode Pre-Flight (run before Stage Entry Check — strict mode only)

1. Read `{{AGENT_DIR_PREFIX}}/agents/docs/stories/ST-XXXXXX.md` to get the story's `**Sprint:**` field (e.g., `sprint-1`)
2. Read the story's immutable `Project Base Branch:` value. If missing, stop for explicit user selection; never infer it from checkout.
3. If `sprint-N-dev` is missing, run `branch_preflight.py inspect --mode strict --base <Project Base Branch> --story-branch sprint-N-dev`, then `create` with its full verified SHA. If it already exists, switch to it and run `inspect --mode strict --base sprint-N-dev --story-branch <this-story-branch>`; this verifies resume safety without treating the sprint branch as a new story-branch target.
4. Only after successful create or resumed verification, record `Sprint Branch: sprint-N-dev`, its full SHA, and this story's execution `Base Branch: sprint-N-dev`. Create the story branch only through its own preflight and record Story Branch only after its successful verification.
