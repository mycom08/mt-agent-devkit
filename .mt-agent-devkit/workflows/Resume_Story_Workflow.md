# Resume Blocked Story Workflow

Triggered by: `"resume story ST-XXXXXX"` or `"/resume-story ST-XXXXXX"` in the selected provider entrypoint

Every worker spawn or resume uses the validated manifest dispatch in Shared Pipeline Stages and `.mt-agent-devkit/contracts/Read_Manifest.md`; routing comes only from the canonical registry, including specialist handoffs and safe resumes.

Use this when a story has `status:blocked` and the required external information has been provided.

---

**Scope-change escalation (`PO Execution: orchestrator`):** when the blocked request is a Scope-Change Escalation from `Shared_Pipeline_Stages.md`, the user's recorded decision is the scope decision. Apply exactly that decision (a split follows `Story_Standard.md §14`; an AC body edit is the user's, not the orchestrator's), restore the status the story held before the block, and resume the recorded stage from the pipeline state file instead of restarting at Stage 0. A missing decision keeps the story blocked; the orchestrator never fills the gap itself.

1. Fetch the story issue and read all comments — locate the blocked request comment and any replies
2. Validate that all items in the **Still Need From You** table have been answered
3. **If info is complete:**
   - Apply the provided values to any files with placeholders (docs, config, etc.)
   - Change label from `status:blocked` to `status:ready`
   - Proceed with [Shared Pipeline Stages](Shared_Pipeline_Stages.md) from Stage 0
4. **If info is still incomplete:**
   - Post an updated comment listing only the remaining missing items (using `.mt-agent-devkit/rules/Blocked_Request.md`)
   - Notify the user what is still needed before the story can proceed
