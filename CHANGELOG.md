# Changelog

All notable changes to mt-agent-devkit are documented here.

---

## [Unreleased]

### Fixed
- [ST-000012] `Story_Standard_template.md` and `Story_Standard.md` — RF-001: §1 Testing row "Who Changes" corrected to TL (was QA); §4 Implementer Workflow: remove conflicting Review→Testing subsection (TL owns `status:testing`, not the Implementer).
- [ST-000012] `Story_Standard_template.md` and `Story_Standard.md` — RF-002: §12 Merge Gate now includes QA sign-off requirement alongside TL approval.
- [ST-000012] `Story_Standard_template.md`, `Story_Standard_PO_template.md`, and working mirrors — RF-004: §2/§13 clarify that the GitHub Issue Assignee (GitHub user account, may be unset) is distinct from the body `**Assigned:**` field (agent role, mandatory); remove the "TBD" Assignee instruction that contradicted the mandatory-Assigned rule.
- [ST-000012] `Shared_Pipeline_Stages_Shared_template.md` and `Shared_Pipeline_Stages.md` — RF-013: Stage 4 non-behavioral and behavioral paths no longer pre-set the next story to `in-progress`; next-story routing is delegated to Stage 0 (Story Discovery).
- [ST-000012] `Technical_Lead_Rules.md` (working mirror) — RF-001: §3 corrected to "before it is merged" (was "after merge") to match the canonical owner statement in `Technical_Lead_Rules_template.md`.

### Added
- [ST-000016] `scripts/validate_templates.py` — Layer-1 corpus invariant validator for `.claude/agents/templates/**` and `.claude/agents/workflows/**`; enforces 6 deterministic checks (reference integrity, placeholder well-formedness, shared-block include integrity, retired-trigger guard, manifest integrity, Markdown well-formedness); exits non-zero on any hard violation; known-issue notes printed as `[KNOWN_ISSUE]` without affecting exit code.
- [ST-000016] `scripts/test/fixtures/bad/` — 5 intentionally-broken fixture files (one per per-file invariant class); validated by `scripts/test/run.sh`; invariant #4 uses `--test-retired-trigger` flag so the real seed remains empty.
- [ST-000016] `scripts/test/run.sh` — fixture self-test runner; asserts each bad fixture produces at least one `[ERROR]` line.
- [ST-000016] `.github/workflows/validate-templates.yml` — CI gate (repo's first GitHub Actions workflow); triggers on PRs touching `templates/**` or `workflows/**`; runs `python scripts/validate_templates.py`.
- [ST-000016] `docs/Template_Test_Strategy.md` — 3-layer test strategy (Layer-1 static, Layer-2 deployment, Layer-3 behavioral); documents all 6 invariants, risk tiers A/B/C, coverage model, AC-as-oracle pattern, and Layer-2/3 roadmap.
- `Apply_Retros_Workflow.md` (devkit-internal) — new `apply retros` / `process retros` workflow: scans `retro:contribution` Issues on `mycom08/mt-agent-devkit`, aggregates and prioritises signals (critical `[failure]` guardrails → token/efficiency → workflow correctness → recurring → clarity), lets the user pick which to apply, edits templates directly, bumps the version once, then archives and closes the processed Issues. Wired into devkit `CLAUDE.md` (routing section + `workflow help` table).
- New GitHub label `retro:contribution` to mark and group community retro contribution Issues.
- [ST-000011] `Sprint_Workflow_Shared_template.md` and `Sprint_Workflow.md` — add Devkit Contribution step at sprint end (step 3, before Cleanup): privacy scan of `sprint_N_summary.md` Findings sections, user opt-in prompt, `gh issue create` on `mycom08/mt-agent-devkit` if authenticated, local export file fallback at `.claude/agents/retros/devkit_contribution_sprint_N.md` if not.

### Changed
- `Sprint_Workflow_Shared_template.md` and `Sprint_Workflow.md` — `gh issue create` for retro contributions now adds `--label "retro:contribution"` so contributed retros are scannable as a group.
- `community-retros/README.md` — reference the `retro:contribution` label in the contributor and maintainer flows; point maintainers to the `apply retros` workflow for triage.
- [ST-000010] `community-retros/README.md` — landing area for community retro export files; defines the export file format (Sprint, Date, Signal items grouped by `[context]`/`[instruction]`/`[workflow]`/`[failure]`, What Worked Well), privacy requirements (no project-specific information), and the maintainer review/triage/archive process.

### Changed
- [ST-000009] `Retro_Rules_template.md` and `Retro_Rules.md` — add Privacy Rule section before Format; signal items must not reference project names, repo names, domain-specific file paths, business logic terms, or client/user identifiers; includes bad/good phrasing examples for self-checking.

---

## [0.1.7]

### Changed
- [ST-000007] Wire per-workflow model assignments into all agent spawn calls across devkit-level workflows (`Analyst_Workflow.md`, `Build_Software_Workflow.md`), sprint workflows (`Shared_Pipeline_Stages.md`, `Plan_Sprint_Workflow.md`, `Refine_Sprint_Workflow.md`), and their shared template equivalents. Model rule: TL doing evaluation/design → `opus`; all other agents → `sonnet`; PO story closure (Stage 4 behavioral) → `haiku`.

---

## [0.1.5]

### Added
- [ST-000006] Split 8 mixed templates into mode-specific variants: `templates/github/` and `templates/strict/` each contain `CLAUDE_template.md` and 7 workflow variants; shared content extracted to `templates/shared/` and `templates/shared/workflows/` using `<!-- SHARED-START -->` / `<!-- SHARED-END -->` markers. `Init_Project_Workflow.md` and `Update_Project_Workflow.md` Stage 2 source paths updated to `templates/{mode}/` for split candidates. `Sync_Devkit_Workflow_template.md` Stage 2 fetch URLs updated to use `{DEVKIT_SOURCE_URL}/.claude/agents/templates/{mode}/workflows/` for split candidates. Original 7 workflow templates and root `CLAUDE_TEMPLATE.md` deleted via `git rm`.

---

## [0.1.2]

### Changed
- `Product_Owner_Rules_template.md` — AC synchronisation rule: PO must update story body before `status:ready` when TL decisions override AC wording
- `Developer_Rules_template.md` — stale-content check on existing-file reads; mid-implementation consultation procedure (both GitHub and strict mode)
- `Shared_Pipeline_Stages_template.md` — mid-implementation consultation orchestrator loop (both GitHub and strict mode)

---

## [0.1.1]

### Added
- [ST-000005] `changes.json` version entry `0.1.1` listing new template files (`Project_CLAUDE_template.md`, `Build_Software_Project_Workflow_template.md`) deployable to target projects via `sync devkit`. `version.txt` bumped to `0.1.1`. `CLAUDE.md` `build software` trigger confirmed wired to `Build_Software_Workflow.md`. README Prerequisites updated with `build software` `gh` CLI requirement note.
- [ST-000003] `Build_Software_Workflow.md` Stages 4–5: Stage 4 scaffolds all repos inline (git init, gh repo create, Init_Project_Workflow GitHub-mode steps, gh project create, repo-to-project linking, build_state.md) for both monolith and multi-repo paths; Stage 5 copies full summary docs and per-repo split files into each repo under `.claude/agents/docs/analysis/`, deletes the state file on success, and prints the handoff message. Pipeline State section updated with Stage 4/5 resume rules and GitHub Project URL field.
- [ST-000004] `Project_CLAUDE_template.md` — project orchestrator CLAUDE.md template for multi-repo `build software` setups; contains `build software` and `workflow help` triggers, repo roster placeholder, and an explicit note that scrum team triggers are not available in the project orchestrator folder.
- [ST-000004] `Build_Software_Project_Workflow_template.md` — Phase 2 workflow for the project orchestrator; reads `build_state.md` and `repo_structure.md`, detects monolith vs multi-repo, spawns parallel repo orchestrator agents to run `create stories` and `plan next sprint` per repo, then updates `build_state.md` phase to `ready`.
- [ST-000002] `build software <idea>` workflow — Stages 1–3: Analysis (delegates to `analyze`), Repo Planning (orchestrator-direct, produces `repo_structure.md`), Doc Splitting (parallel general-purpose agents produce per-repo filtered roadmap and architecture files). Pipeline state stored in `.claude/agents/tmp/build_software_state.md` with automatic resume on re-trigger. New file: `.claude/agents/workflows/Build_Software_Workflow.md`.

---
