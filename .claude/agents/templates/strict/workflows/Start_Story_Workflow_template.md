<!-- Shared logic: templates/shared/workflows/Start_Story_Workflow_Shared_template.md -->

## Strict-Mode Pre-Flight (run before Stage Entry Check — strict mode only)

1. Read `.claude/agents/docs/stories/ST-XXXXXX.md` to get the story's `**Sprint:**` field (e.g., `sprint-1`)
2. Check if the sprint dev branch exists: `git branch --list sprint-N-dev`
   - Exists → `git checkout sprint-N-dev`
   - Missing → `git checkout -b sprint-N-dev` (from the user's current branch at invocation time)
3. Store `Sprint Branch: sprint-N-dev` in the pipeline state file
