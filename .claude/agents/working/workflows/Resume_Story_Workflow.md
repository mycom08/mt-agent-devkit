# Resume Blocked Story Workflow

Triggered by: `"resume story ST-XXXXXX"` or `"/resume-story ST-XXXXXX"` in CLAUDE.md

Use this when a story has `status:blocked` and the required external information has been provided.

---

1. Fetch the story issue and read all comments — locate the blocked request comment and any replies
2. Validate that all items in the **Still Need From You** table have been answered
3. **If info is complete:**
   - Apply the provided values to any files with placeholders (docs, config, etc.)
   - Change label from `status:blocked` to `status:ready`
   - Proceed with [Shared Pipeline Stages](Shared_Pipeline_Stages.md) from Stage 0
4. **If info is still incomplete:**
   - Post an updated comment listing only the remaining missing items (using `.claude/agents/working/rules/Blocked_Request.md`)
   - Notify the user what is still needed before the story can proceed
