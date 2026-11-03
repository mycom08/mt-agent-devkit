---
name: handoff
description: Runtime-state handoff for implementer and reviewer roles - memory, working records, retros, telemetry and pipeline state stay local and uncommitted before you signal stage completion. Load before stage handoff.
---

# Handoff

**Requires:** `retro` (evaluate and record the stage state first)

Canonical owner. `generate_common_blocks.py` copies part `state` into `Agent_Common_Read_On_Demand.md` §5 and `Agent_Common_Stage_Transition.md`; edit here, then regenerate.

## Before Signalling Stage Completion

1. Evaluate retro detection and record the stage state (`retro`).
2. Confirm no runtime-state file is staged, committed or pushed on the product branch (`git status`).
3. Then report stage completion.

<!-- part: state -->
Memory, Working Records, retrospectives, telemetry, and pipeline state are local runtime state. Never `git add`, commit, or push them on a product branch; report stage completion after the local handoff.
<!-- /part: state -->
