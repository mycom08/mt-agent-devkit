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
- **Devkit Contribution privacy-scan source (ST-000011):** scan `.claude/agents/retros/sprint_N_summary.md` `### Findings` sections — NOT individual retro files (deleted at Batch Retro Review step 1e). Summary is the only durable, resumption-safe aggregate; resolve N from pipeline-state `Sprint` field.
- **Devkit Contribution access model (ST-000011):** authenticated path = issue-based (`gh issue create` on mycom08/mt-agent-devkit with ST-000010 export as body), uniform for all users (no push access / fork / write-detection needed). NOT PR/fork-based. Local-file fallback unchanged. AC reworded PR→Issue (PO owns the AC change).

- **status:testing canonical owner (ST-000012):** TL sets `status:testing` immediately after approving the PR and **before** merge. This is the canonical rule per `Technical_Lead_Rules_template.md §3` and `Shared_Pipeline_Stages_Shared_template.md` Stage 2 step 6. Implementer no longer sets this label.
- **Assignee disambiguation (ST-000012):** Two separate concepts in stories — the GitHub Issue Assignee (GitHub user account, sidebar, may be unset) vs the body `**Assigned:**` field (agent role, drives pipeline routing, mandatory). Story_Standard §2/§13 and Story_Standard_PO §2/§13 now include an explicit note.
- **Stage 4 next-story routing (ST-000012):** Stage 4 no longer promotes the next story to `in-progress`. Next-story routing is entirely Stage 0's responsibility (Story Discovery). This prevents double-routing in the sprint loop.
- **Template/working-mirror drift risk:** The working `Technical_Lead_Rules.md §3` had drifted from its template (said "after merge" vs template's "before merge"). Mirrors can drift silently between stories — verify both template and mirror when checking consistency.

## Troubleshooting Facts

No troubleshooting facts recorded yet.
