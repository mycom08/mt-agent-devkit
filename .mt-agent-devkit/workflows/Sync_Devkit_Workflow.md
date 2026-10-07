# Sync Devkit — Phase 1 Lifecycle Routing

Target-project sync output is unchanged until Phase 2. After provider selection,
load the selected provider's existing operational lifecycle workflow at
`{PROVIDER_ROOT}/agents/working/workflows/Sync_Devkit_Workflow.md`.
For Codex, target installation currently supports only Claude/Antigravity output;
require the user's target-provider choice and delegate to that existing lifecycle
workflow. Do not invent a Codex target installer or rewrite global substitutions.
This delegation loads lifecycle content, never a foreign provider adapter.
