# Technical Lead Memory

## Stored Facts

- **Version sequence (sprint 1):** `version.txt` is currently `0.0.9`. ST-000001 (retro marker story) claims `0.1.0`. ST-000005 (build software wiring) targets `0.1.1`. ST-000002/003/004 do not touch version.txt.
- **changes.json format note:** The `0.0.9` entry uses the newer object format (files + descriptions + checksums). Earlier entries (`0.0.1`–`0.0.7`) use the legacy flat array format. New entries should use the object format.
- **Stage 2 of Build_Software_Workflow:** orchestrator-direct action (no TL agent spawn). Orchestrator reads architecture.md and writes repo_structure.md directly.
- **Stage 3 of Build_Software_Workflow:** parallel general-purpose agents with inline instructions (not the devkit's own TL/PO agents). Split: one agent per output type across all repos.
- **Stage 4 of Build_Software_Workflow (init project):** orchestrator executes init-project-equivalent steps inline; does not call `init project` as a trigger; no --mode flag added to init project.
- **Story sequencing sprint 1:** ST-000002 first, then ST-000004 in parallel with ST-000002 (no shared files), then ST-000003 Stages 4–5 after ST-000004 merges.
- **Cross-project gh commands:** always use `--repo <slug>` explicitly — never rely on working directory git remote.
- **build software resume:** same trigger (`build software`) auto-detects state file at entry; Stage = last completed stage in state file; jump to Stage+1.
- **Retro marker placement:** `<!-- retro-adapted: preserve on sync -->` instruction belongs only in Stage 5 retro application step of Shared_Pipeline_Stages_template.md. Not on every stage.

## Troubleshooting Facts

No troubleshooting facts recorded yet.
