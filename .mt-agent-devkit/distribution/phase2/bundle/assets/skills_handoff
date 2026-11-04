---
name: handoff
description: Runtime-state handoff for implementer and reviewer roles - memory, working records, retros, telemetry and pipeline state stay local and uncommitted before you signal stage completion. Load before stage handoff.
---

# Handoff

**Requires:** `retro` (evaluate and record the stage state first)

Canonical owner. Part `state` is also copied into `Agent_Common_Read_On_Demand.md` §5 and `Agent_Common_Stage_Transition.md`.

## Before Signalling Stage Completion

1. Evaluate retro detection and record the stage state (`retro`).
2. Confirm no runtime-state file is staged, committed or pushed on the product branch (`git status`).
3. Then report stage completion.

<!-- part: state -->
Before signaling completion, write any needed Memory, Working Record, retrospective,
telemetry, or pipeline-state update to its runtime path. These are local runtime state:
never `git add`, commit, or push them on a product branch in either mode. Report stage
completion after the local handoff is complete. A project that needs versioned agent
knowledge requires a separately designed repository and branch policy.
<!-- /part: state -->
