# ST-000042 Test Scenarios

## Happy Path
- Ensure `.antigravity/` folder scaffolds correctly and contains all templates.
- Ensure `scaffold_mechanical.ps1` runs correctly on Windows.
- Ensure `Init_Project_Workflow.md` correctly asks the user for provider (`claude` vs `antigravity`) and records it in state.
- Ensure all sprint workflows successfully trigger using `define_subagent` and `invoke_subagent` JSON primitives without any Claude XML tag usage.
- Ensure `SKILL.md` maps the behavior appropriately.

## Edge Cases
- Test missing inputs in `Init_Project_Workflow.md`.
- Test running `scaffold_mechanical.ps1` on an unsupported platform.
- Test missing `Workspace: share` configuration and observe subagent context drift.

## Error Cases
- Test orchestrator refusing to spawn subagents if Claude XML tags are used.
