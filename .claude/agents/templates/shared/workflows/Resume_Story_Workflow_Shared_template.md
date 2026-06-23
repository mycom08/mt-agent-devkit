<!-- Included by: templates/github/workflows/Resume_Story_Workflow_template.md, templates/strict/workflows/Resume_Story_Workflow_template.md -->

<!-- SHARED-START -->
# Resume Blocked Story Workflow

Triggered by: `"resume story ST-XXXXXX"` or `"/resume-story ST-XXXXXX"` in CLAUDE.md

Use this when a story has `status:blocked` and the required external information has been provided.

---

**If `Mode: github`:**
1. Fetch the story issue and read all comments — locate the blocked request comment and any replies
2. Validate that all items in the **Still Need From You** table have been answered
3. **If info is complete:**
   - Apply the provided values to any files with placeholders (docs, config, etc.)
   - Change label from `status:blocked` to `status:ready`
   - Proceed with [Shared Pipeline Stages](Shared_Pipeline_Stages.md) from Stage 0
4. **If info is still incomplete:**
   - Post an updated comment listing only the remaining missing items (using `.claude/agents/rules/Blocked_Request_Template.md`)
   - Notify the user what is still needed before the story can proceed

**If `Mode: strict`:**
1. Read `.claude/agents/docs/stories/ST-XXXXXX.md` — locate the blocked request entry in the `## Comments` section and any subsequent replies
2. Validate that all items in the **Still Need From You** table in that comment entry have been answered (check for user replies appended after the blocked entry)
3. **If info is complete:**
   - Apply the provided values to any files with placeholders (docs, config, etc.)
   - Edit `**Status:** ready` in the story MD file
   - Also check `.claude/agents/tmp/blocked_ST-XXXXXX.md` — if it exists, delete it
   - Proceed with [Shared Pipeline Stages](Shared_Pipeline_Stages.md) from Stage 0
4. **If info is still incomplete:**
   - Append an updated comment entry to the story MD `## Comments` section listing only the remaining missing items (using `.claude/agents/rules/Blocked_Request_Template.md` as the template)
   - Notify the user what is still needed before the story can proceed
<!-- SHARED-END -->
