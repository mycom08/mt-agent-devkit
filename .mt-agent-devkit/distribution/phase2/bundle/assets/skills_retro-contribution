---
name: retro-contribution
description: Writing a role's retrospective contribution after a retro trigger was recorded - Retro_Rules first, own section only, completion pointers - and the orchestrator's expected identities, sprint retros and legacy-started runs. Never load on a clean stage.
---

# Retro Contribution

**Requires:** `retro` (the trigger must already be recorded)

Canonical owner. `generate_common_blocks.py` copies part `writing` into `Agent_Common_Read_On_Demand.md` §3 and `Agent_Common_Retro.md`, and part `orchestration` (expected identities, sprint retros, legacy runs) into `Agent_Common_Bootstrap.md` §7 and `Agent_Common_Core.md` §7; edit here, then regenerate.

## Writing a Contribution

<!-- part: writing -->
Load this guidance only after retro detection recorded a required contribution. Clean stages skip it entirely.

1. Read Retro_Rules in full using the selected provider's supported mechanism before writing; preserve lesson-first, privacy, shared deduplication and role ownership.
2. Create the bound story retro only if missing, with its story/date header and your triggered role section. Do not create other roles or pending placeholders. If it exists, preserve all prior history and other sections.
3. Write only your actual role contribution and new observations. A late/resumed trigger updates existing lessons or records the new delta; do not duplicate earlier findings. Populate required observations, not a no-op “None” section.
4. Update the same completion identity with its confined exact role contribution and evidence pointers; run the helper check for the expected stage identity before handoff. Unknown or missing required contributions block completion.
5. For an explicitly grandfathered already-started legacy run, retain its existing skeleton and write your owned section under that prior contract; do not erase other placeholders/history.
<!-- /part: writing -->

## Orchestrator Bookkeeping

<!-- part: orchestration -->
Before first governed work, the orchestrator records the exact expected stage identities (runtime JSON list, maximum 128), carrying completed identities across story/sprint transitions; include the actual actor for fast paths (Orchestrator) and independent PO validation when QA implements, never an unspawned QA or skipped worker.

An explicit sprint-retro request records an actual Orchestrator `sprint_retro` stage under the last real story/run in the selected sprint, adds that identity to the expected list, and triggers `explicit_request`. The contribution states the requested sprint scope and evidence; reuse existing lessons by pointer. Do not invent a story or require previously clean workers to fabricate observations. Empty/mixed sprint reports remain supported; a user-requested analysis may identify that no additional lesson was found, while still recording the actual requested analysis/evidence.

Transition: a run demonstrably started under the prior contract may be explicitly marked `Retro Contract: legacy-started` in its existing pipeline state. Preserve its skeleton/history and complete its existing role-owned sections without applying new expected-record requirements retroactively. Only already-started runs qualify; a new run uses `exception-v1` and may not infer cleanliness from a legacy file. Preserve source history after review/aggregation rather than deleting it. Memory pruning may read only its named section in Retro_Rules even when no retro exists.
<!-- /part: orchestration -->
