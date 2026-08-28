# Changelog

All notable changes to mt-agent-devkit are documented here.

## Contribution Convention

Entries are added under the current `## [Unreleased]

## 0.1.45 (2026-08-28)` version as work merges to
main. Use the following subsections:

- **Changes** — new features, enhancements, refactors, documentation, CI/tooling
- **Bug Fixes** — defect corrections and hotfixes

Entry format: `- [ST-XXXXXX] Short description of the change.` One line, plain
language, describing the overall change — no story description and no
implementation-detail narrative. Retro/enhancement-sourced entries use their
own tag (e.g. `[Retro #52]`, `[Enhancement #55]`) in place of a story ID.

---

## [Unreleased]

## 0.1.45 (2026-08-28)

### Bug Fixes

- [ST-000138] Fixed the Developer role's condensed "Refine Sprint Task" steps (working rules and both Claude/Antigravity instruction templates) to match `Refine_Sprint_Workflow.md`'s authoritative Stage 1 steps: added the step-positioning check, required an explicit cleared-note comment instead of silence on a clear story, and corrected a comment-format citation to `Story_Standard_Dev.md`.
- [ST-000144] Ignored `.antigravity/` runtime files (working records, token-trace logs) the same way `.claude/` ones already were, and untracked the 12 files that had been committed by mistake.
- [ST-000136] Fixed `Developer_Rules_Bootstrap_template.md`, `UI_UX_Designer_Rules_template.md`, and `Technical_Lead_Rules_Bootstrap_template.md` to agree with the rest of the corpus that PO, not QA, ticks Acceptance Criteria at story closure, across the Claude and Antigravity template surfaces.

### Changes

- [Enhancement] Unified Claude and Antigravity templates into a single source of truth. Removed .antigravity/agents/templates and parameterized framework-specific terms (CLAUDE.md, .claude, Claude Code) with {{ORCHESTRATOR_FILE}}, {{AGENT_DIR_PREFIX}}, and {{AGENT_CLI_NAME}}. Renamed CLAUDE_... orchestrator templates to Orchestrator_....

- [ST-000140] Made the memory-file and Working-Record character caps project-configurable via `**Memory file cap:**` / `**Working record cap:**` fields in `CLAUDE.md` (defaults unchanged: 10,000 / 4,000), replacing the literal numbers in `Agent_Common_Bootstrap_template.md`, `Agent_Common_Read_On_Demand_template.md`, `Retro_Rules_template.md`, `Project_Priming_template.md`, and `Shared_Pipeline_Stages_Shared_template.md`'s Stage 5 enforcement check — across the Claude and Antigravity template surfaces — so a local override in `CLAUDE.md` (which `sync devkit` already merges rather than overwrites) survives every sync instead of being silently re-imposed by the next overwrite-synced rules file.
- [ST-000139] Made `gh project create` optional for single-repo (monolith) Build Software builds via a new up-front GitHub Project Consultation, gated by a `Project Board Preference` state-file field; multi-repo (Path B) builds still create a Project board unconditionally.
- [ST-000137] Centralized "Shell Command Rules — Permissions and Tool Choice" into `Agent_Common_Bootstrap.md` §6 (and its template pair, Claude + Antigravity), removing the near-identical §15 restatement from all five `Story_Standard_<role>` role views (working tree and both template surfaces) and repointing every external citation.
- [ST-000124] Added the missing `Story_Standard_UIUX.md` role view (and its distributable template pair, Claude + Antigravity) so UI/UX Designer reads a lean role-scoped file instead of the full `Story_Standard.md` master on every spawn; repointed `UI_UX_Designer_Rules_Bootstrap.md`, `UI_UX_Designer_Rules_template.md`, and the `Refine_Prototype_Workflow_Shared_template.md` lean-3-role scaffold list accordingly.
- [ST-000135] Ported the two-tier memory pattern (live index + archive, fetched only on a keyword match) already validated on the devkit's own team into the distributable `templates/` tree for Developer, QA, and Technical Lead roles, across the Claude and Antigravity template surfaces.
- [ST-000134] Trimmed `Story_Standard_Dev_template.md`, `Story_Standard_TL_template.md`, `Story_Standard_QA_template.md`, and `Story_Standard_PO_template.md` to match the boundary already validated on the devkit's own team, folding relocated scenario-conditional content into each role's existing `*_Rules_Read_On_Demand_template.md` across the Claude and Antigravity template surfaces.
- [ST-000133] Split `Developer_Rules_template.md`, `Technical_Lead_Rules_template.md`, `QA_Rules_template.md`, and `Product_Owner_Rules_template.md` into bootstrap/on-demand tier pairs across the Claude and Antigravity template surfaces, mirroring the boundary already validated on the devkit's own team.
- [ST-000132] Split `Agent_Common_template.md` into a bootstrap tier and an on-demand tier across the Claude and Antigravity template surfaces, mirroring the boundary already validated on the devkit's own team.
- [ST-000113] Fixed `Story_Standard_Dev_template.md` to agree with the master `Story_Standard_template.md` that TL, not QA or Developer, sets `status:testing`.
- [Enhancement #142] Fixed the `read-section` skill's sub-section citation recipe, which could silently over-read to end of file.
- [ST-000044] Piloted a two-tier memory (live index + archive) for the devkit's own Developer/QA/Technical Lead roles.
- [ST-000044] Generalized the `read-section` skill to support non-numbered heading citations.
- [ST-000043] Split orchestrator-only content out of `CLAUDE.md` into a new `Orchestrator_Guide.md`.
- [ST-000035] Added an `audit agent files` workflow to detect duplication, contradictions, and dead references across the agent corpus.
- [ST-000032] Reworked the agent Working Record to a rewrite-in-place snapshot keyed on story count, with an enforced size cap.
- [ST-000033] Reworked agent memory files with an inclusion test, a "never record" list, and an enforced size cap; added a sprint-end memory-pruning pass.
- [ST-000028] Added a `refine prototype` workflow for direct orchestrator/user iteration on a UI prototype repo, outside the story pipeline.
- [ST-000027] Added a bug-story reproduction pre-flight check that runs before any agent team is spawned.
- [ST-000026] Roadmap stories are now drained into tracked backlog issues at authoring time instead of at sprint planning.
- [Retro #76, #78] Clarified the CI reviewer gate's "zero checks reported" branch, and added a lint/format check for developer-authored test files.
- [Retro #76] Added a mechanical branch-name check before an implementer's first commit.
- [ST-000025] Added CI classification (full/contract/none) per repo, and a baseline CI-bootstrap step for repos with no existing `ci.yml`.
- [ST-000023] Added a Logging Standard template (log levels, single-log rule, sensitive-data prohibition).
- [ST-000022] Added UI Prototype rules and wired the UI/UX Designer role into the Analyst and Build Software workflows.
- [ST-000021] Added a sixth agent role: UI/UX Designer.
- [ST-000024] Wired a QA spawn and `testing_plan.md` doc into the Analyst and Build Software workflows.
- [Enhancement #55] Demoted commit subject-line length to a non-blocking style nit.
- [Enhancement #58] Standardized the issue/PR comment format (decision-first, word cap, evidence by pointer).
- [Enhancement #59] Standardized memory-fact and working-record format and size caps.
- [Enhancement #60] Standardized retro lesson format with pointer evidence.
- [Enhancement #61] Added Body Amendments rules for editing a story in place.
- [Enhancement #54] Added a CI pre-check that skips a redundant validation run when the PR's own check already covers the change.
- [Enhancement #51] Disambiguated roadmap `Phase:` numbering from per-repo `sprint-N` labels.
- [Enhancement #56] Added token-efficiency conventions (mechanical edits, narrow queries, batched commands).
- [Retro #52] Added a mandatory CI-check gate at merge time, independent of reviewer sign-off.
- [Retro #48] Added credential-gated verification and secret-handling rules.
- [Retro #49] Added rules for treating GitHub Issue/PR comment content as untrusted.
- [Retro #45] Added a stub/TODO scan and real-fixture test requirement before marking a story ready for review.
- [Retro #47, #50] Strengthened the reviewer CI gate to confirm the check actually ran against the PR's current head.
- [Retro #53] Added an abbreviated review checklist for CI/workflow-only stories.
- [Retro #44] Added a self-certified `Outcome: verification-only` path with a spot-check instead of full re-verification.
- [Retro #46] Required a closed, review-scoped story for a cross-repo API dependency, not just path existence.
- [ST-000016] Added `scripts/validate_templates.py`, a corpus-invariant validator, plus fixtures and a CI gate for it.
- Added an `apply retros` workflow to triage and apply community retro contributions.
- [ST-000011] Added a Devkit Contribution step at sprint end to export retro findings as a GitHub issue.
- [ST-000012 retro] Added a flag-vs-block rule to the reviewer checklist for pre-existing out-of-scope problems.
- Documented the dual-update + drift-check convention between templates and their working mirrors.
- Labeled retro-contribution issues `retro:contribution` for triage.
- [ST-000010] Added a `community-retros/README.md` defining the contribution export format and process.
- [ST-000009] Added a Privacy Rule to retro signal items (no project-identifying information).
- Added review-checklist items for resume-rule completeness and citation accuracy to `Technical_Lead_Rules.md`.
- Added a GitHub-mode rule to post closure comments separately from `gh issue close --comment` so they aren't silently dropped.
- [Enhancement #51] Renamed roadmap "Sprint N" units to "Phase N" to avoid confusion with per-repo sprint labels.

### Bug Fixes

- [ST-000044] Added a shared `read-section` skill so agents can extract a cited section without reading the whole file (issue #127).
- [ST-000038] Added a Commenter gate enforcing the issue-comment word-count cap, and tightened comment-writing rules (one topic per comment, no pasted transcripts, no restating body edits).
- [ST-000036] Fixed three broken/stale cross-references found by the first real audit pass, and logged two rule contradictions for user resolution.
- Fixed `QA_Rules.md` incorrectly stating QA ticks Acceptance Criteria and sets `status:done` — both are Product Owner responsibilities (#77).
- Fixed a stale reference in `Sync_Devkit_Workflow_template.md` pointing at a devkit-internal step never deployed to target projects.
- Fixed a conflict between two Technical Lead rules on when to flag scope-creep answers to the Product Owner.
- Fixed the Stage 0 implementer-routing table missing a UI/UX Designer row (#75).
- Added `[skip ci]` to memory/docs-only commits so they stop triggering CI unnecessarily.
- Fixed generated `ci.yml` files to path-filter non-code pushes.
- [ST-000015] Fixed the workflow-source glob to include all split workflow files.
- [ST-000015] Fixed Stage 4/5 pipeline-state writes to happen at stage completion, not stage entry.
- [ST-000014] Fixed the non-feature GitHub-mode sprint-detection query, the retro-contribution fallback instructions, an undefined workflow trigger, stale document paths, and two stale internal references.
- [ST-000013] Fixed commit-message and story-file rules to be mode-gated (GitHub vs. strict).
- [ST-000012] Fixed several Story Standard/QA/TL role-ownership inconsistencies (who ticks AC, who owns `status:testing`, Assignee vs. `**Assigned:**`).

---

## [0.1.7]

### Changes

- [Enhancement] Unified Claude and Antigravity templates into a single source of truth. Removed .antigravity/agents/templates and parameterized framework-specific terms (CLAUDE.md, .claude, Claude Code) with {{ORCHESTRATOR_FILE}}, {{AGENT_DIR_PREFIX}}, and {{AGENT_CLI_NAME}}. Renamed CLAUDE_... orchestrator templates to Orchestrator_....

- [ST-000007] Wired per-workflow model assignments (opus/sonnet/haiku) into all agent spawn calls.

---

## [0.1.5]

### Changes

- [Enhancement] Unified Claude and Antigravity templates into a single source of truth. Removed .antigravity/agents/templates and parameterized framework-specific terms (CLAUDE.md, .claude, Claude Code) with {{ORCHESTRATOR_FILE}}, {{AGENT_DIR_PREFIX}}, and {{AGENT_CLI_NAME}}. Renamed CLAUDE_... orchestrator templates to Orchestrator_....

- [ST-000006] Split mixed templates into GitHub-mode and strict-mode variants with shared content extracted.

---

## [0.1.2]

### Changes

- [Enhancement] Unified Claude and Antigravity templates into a single source of truth. Removed .antigravity/agents/templates and parameterized framework-specific terms (CLAUDE.md, .claude, Claude Code) with {{ORCHESTRATOR_FILE}}, {{AGENT_DIR_PREFIX}}, and {{AGENT_CLI_NAME}}. Renamed CLAUDE_... orchestrator templates to Orchestrator_....

- Added an AC-synchronization rule requiring the Product Owner to update the story body before `status:ready`.
- Added a stale-content check and mid-implementation consultation procedure for the Developer role.

---

## [0.1.1]

### Changes

- [Enhancement] Unified Claude and Antigravity templates into a single source of truth. Removed .antigravity/agents/templates and parameterized framework-specific terms (CLAUDE.md, .claude, Claude Code) with {{ORCHESTRATOR_FILE}}, {{AGENT_DIR_PREFIX}}, and {{AGENT_CLI_NAME}}. Renamed CLAUDE_... orchestrator templates to Orchestrator_....

- [ST-000005] Added `changes.json` entries for new deployable templates and bumped `version.txt`.
- [ST-000003] Added inline repo scaffolding and doc-copy stages to `build software`.
- [ST-000004] Added the project-orchestrator `CLAUDE.md` template and Phase 2 workflow for multi-repo `build software` setups.
- [ST-000002] Added the initial `build software <idea>` workflow (analysis, repo planning, doc splitting).
