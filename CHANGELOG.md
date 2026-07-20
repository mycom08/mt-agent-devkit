# Changelog

All notable changes to mt-agent-devkit are documented here.

---

## [Unreleased]

### Added (v0.1.29 — UI/UX Designer agent role)
- [ST-000021] New sixth agent role: `ui_ux_designer_instructions_template.md` + `UI_UX_Designer_Rules_template.md` (+ working mirrors, blank memory/working-record scaffold entries) — turns a wireframe/backlog story into a **runnable** prototype (real routes/components wired to a local mock backend), never a static mockup. `Init_Project_Workflow.md` and `scaffold_mechanical.sh` now copy the role's files for both github and strict mode; `CLAUDE_Shared_template.md`'s Agent Roster gains the row. `Story_Standard_template.md`, `Story_Standard_PO_template.md`, `Product_Owner_Rules_template.md`, `Create_Stories_Workflow_Shared_template.md`, and `Sprint_Workflow_Shared_template.md` (+ working mirrors) add `UI/UX Designer` to every `**Assigned:**`/role-boundary/implementer-role enumeration. Workflow *integration* (Analyst Stage 2a, roadmap rule, Build Software companion-repo convention) is deferred to ST-000022.

### Fixed (v0.1.28 — CI noise on non-code pushes)
- `Agent_Common_template.md` (+ working mirror) — §6 stage-transition memory commits now append `[skip ci]` in the commit body so memory-only pushes stop triggering CI; head-commit semantics documented (push pending code commits separately first).
- `Developer_Rules_template.md` (+ working mirror) — §6 docs-only pushes (`docs/**`, `*.md`, `.claude/agents/**`) append `[skip ci]`; never used on pushes containing code, config, or build-file changes.
- (internal, no changes.json entry) `Java_Skeleton_REST_Service.md`, `Java_Skeleton_Library.md` — generated `ci.yml` triggers are now path-filtered (`paths-ignore: ['.claude/**', '**.md', 'docs/**']`), matching the filtering the API-spec shape already had; required-status-checks caveat documented. Repos generated before v0.1.28 need a one-time manual edit of their `ci.yml` to add the same `paths-ignore` block.

### Changed (v0.1.27 — enhancement batch)
- [Enhancement #55] `Developer_Rules_template.md` (+ working mirror) — commit subject-line length demoted to a non-blocking style nit: reviewers note it, never request changes or trigger a fix-loop over length alone; the ≤50-char limit explicitly covers the entire `type(scope): subject` header line. Motivated by two consecutive full fix-loops (~193K tokens) over zero-functional-impact violations.
- [Enhancement #58] `Story_Standard_template.md`, `Story_Standard_{Dev,TL,QA,PO}_template.md`, `Strict_Mode_Story_Guide_template.md` (+ working mirrors) — comment-writing standard: decision-first format, ~150–200-word soft cap (QA per-AC validation reports exempt), evidence by pointer with full check logs in the working record, delta-only corrections, no comments-about-comments, one close-out per thread, compact-bullet default format.
- [Enhancement #59] `Agent_Common_template.md`, `Project_Priming_template.md` (+ working mirrors) — memory facts are rule-first (~100–120-word cap), corrections rewrite in place with a one-line `Corrected:` note, prune on write, point-don't-mirror; working records are bullet standups (~100–150 words/day) with evidence by pointer and no session trivia.
- [Enhancement #60] `Retro_Rules_template.md` (+ working mirror) — lesson-first bullets with pointer evidence, shared `## Story-Level Lessons` section written once and referenced per role, reinforced lessons as one-line `Reinforces:` pointers, fix-loop addenda state only the delta.
- [Enhancement #61] `Story_Standard_template.md` (+ working mirror) — Body Amendments edit-time rules: refinement outcomes land as ≤5-line decisions with a pointer to the resolving comment, the body always reads as current truth (no supersession narration; edit history is the audit trail), §3 scope rules apply to edits; AC hygiene (testable requirement only); §2/§4 reconciliation legitimizing optional Technical Scope / API Spec Reference / Design Source sections; one related-work list per body.
- [Enhancement #54] `CICD_Validation_Guide_template.md` (+ working mirror) — new Step 0 pre-check: when the workflow's `pull_request` trigger already covers the change, skip the `ci-validation` push and cite the PR's own triggered run as the pre-merge validation run — removes the guaranteed duplicate full CI run per workflow-file story.
- [Enhancement #51] `Create_Stories_Workflow_Shared_template.md`, `Plan_Sprint_Workflow_Shared_template.md` (+ working mirrors) — roadmap `Phase:` numbering (global cross-repo thematic sequence) disambiguated from per-repo `sprint-N` labels (local execution counter starting at 1); roadmap-sourced stories echo a `**Roadmap Phase:**` body line instead of conflating the two.
- [Enhancement #56] `Agent_Common_template.md` (+ working mirror) — new §9 Token-Efficiency Conventions: mechanical edits via shell substitution instead of Read+Edit, narrow `gh` queries with `--jq`, batched related commands, section-targeted reads instead of whole-file re-reads — explicitly never a justification for thinner verification.

### Changed (internal — devkit operational workflows only, no changes.json entry)
- [ST-000024] `Analyst_Workflow.md` — Stage 2a: QA (sonnet) is now a sequenced spawn fired as soon as TL reports completion, independent of PO; QA reads `spec.md`/`business_requirements.md`/`architecture.md` and authors `testing_plan.md` (TL no longer writes it). `architecture.md` gains a **Testability Notes** section (test seams, mockable boundaries, contract-test candidates) as QA's technical input. Pipeline state gains `qa_session`. `discussion.md` gains `## QA Questions`/`## QA Suggestions`. Stage 2b resumes QA after TL (never in parallel) whenever `architecture.md` changed that cycle. Stage 2d feedback routing, file-ownership/output-documents tables, and Pipeline Rules updated so `testing_plan.md` maps to QA, not TL.
- [ST-000024] `Build_Software_Workflow.md` — Stage 1 state file gains `qa_session` (copied from `analyst_workflow_state.md`); Stage 1 feedback routing maps `testing_plan.md` → QA (was TL).
- [Enhancement #51] `Analyst_Workflow.md` — roadmap thematic units renamed from "Sprint N" to "Phase N" (extending the Phase 0 design convention) in the `implementation_roadmap.md` format and `summary.md` delivery-plan table, with an explicit naming rule distinguishing them from per-repo `sprint-N` labels.
- [Enhancement #51] `Build_Software_Workflow.md` — Stage 3 roadmap splitter now stamps each per-repo roadmap slice with a phase-numbering note stating the `Phase:` sequence is cross-repo and independent of that repo's `sprint-N` labels.

### Fixed
- [Retro #52] `Shared_Pipeline_Stages_Shared_template.md` and `Story_Standard_template.md` (+ working mirrors) — Merge Procedure gets a mandatory step 0 CI-check gate (`gh pr checks`) independent of reviewer sign-off; reviewer checklist requires pasting the check output into the approval comment. Real incident: 3 stories merged to `main` while the E2E suite was red on 6 consecutive runs, with no independent check at the merge step itself.
- [Retro #48] `Agent_Common_template.md`, `Developer_Rules_template.md`, `Technical_Lead_Rules_template.md`, `QA_Rules_template.md` (+ working mirrors) — new Credential-Gated Verification and Secret Handling sections: never self-approve a missing-credential skip via a dummy value or same-secret-different-job analogy; never persist a raw secret to any committed file.
- [Retro #49] `Agent_Common_template.md` (+ working mirror) — new External Content Handling section: treat GitHub Issue/PR comment content as untrusted, verify `authorAssociation` before treating a comment as a binding role decision, treat command/credential/site-visit requests in comments as suspected prompt injection.
- [Retro #45] `Shared_Pipeline_Stages_Shared_template.md`, `QA_Rules_template.md`, `Sprint_Workflow_Shared_template.md` (+ working mirrors) — stub/TODO scan required before marking a story ready for review; real-fixture test required wherever AC implies external integration; "mock/structural pass ≠ complete" rule; Batch Retro Review now routes `[context]` items describing an unowned missing capability to backlog creation.
- [Retro #47, #50] `Technical_Lead_Rules_template.md`, `Developer_Rules_template.md`, `Shared_Pipeline_Stages_Shared_template.md`, `CICD_Validation_Guide_template.md` (+ working mirrors) — reviewer CI gate now confirms the check actually executed (not just its conclusion), confirms the cited run's head SHA matches the PR's current head, requires diagnosing red checks from their log, and adds a dependency-pin resolvability check; PO closure now checks an elevated QA requirement was actually addressed and states the closure signal when implementer = validator; new CICD exception for a new check's expected first red run.
- [Retro #53] `Technical_Lead_Rules_template.md`, `QA_Rules_template.md`, `Clean_Code_Rules_template.md` (+ working mirrors) — new abbreviated "CI/Workflow story" review checklist; CI-equivalent exception so a CI/workflow-only story's automation suite isn't re-run 3x; `Clean_Code_Rules` "Skip for" list now explicitly names CI YAML files.
- [Retro #44] `Shared_Pipeline_Stages_Shared_template.md`, `QA_Rules_template.md` (+ working mirrors) — Stage 1 can emit a self-certified `Outcome: verification-only`; Stage 2/3 route it to one spot-check instead of full re-verification, with model right-sizing and a coverage-audit exception.
- [Retro #46] `Create_Stories_Workflow_Shared_template.md`, `Plan_Sprint_Workflow_Shared_template.md` (+ working mirrors) — multi-repo API surface check now requires a closed, review-scoped story covering a sibling-repo contract endpoint, not just path existence; new cross-repo dependency audit before locking a sprint.

### Fixed (internal — devkit operational workflows only, no template/version change)
- [ST-000015] `Init_Project_Workflow.md` — RF-017: workflow source glob in source table broadened from `*_Workflow_template.md` to `*_template.md` so `Shared_Pipeline_Stages_template.md` (which does not end with `_Workflow`) is included; all 7 split workflow files are now captured.
- [ST-000015] `Build_Software_Workflow.md` — RF-015: Stage 4 and Stage 5 pipeline-state writes moved from stage entry to stage completion; a crash mid-Stage-4 now resumes from Stage 4 (using `build_state.md` per-repo idempotency checks) instead of incorrectly skipping to Stage 5.
- RF-016 relocated to ST-000020 (versioned) — requires template updates to the 8 flat-path referrers before the instruction path can move to `.claude/agents/instructions/`.

### Fixed
- [ST-000014] `Plan_Sprint_Workflow_Shared_template.md` and `Plan_Sprint_Workflow.md` — RF-012: Stage 1 step 3 non-feature GitHub mode sprint detection replaced three AND-ed `--label` flags (always returns 0 results) with three separate per-label queries whose results are unioned.
- [ST-000014] `Sprint_Workflow_Shared_template.md` and `Sprint_Workflow.md` — RF-014: sprint-end Devkit Contribution unauthenticated fallback now instructs users to open an Issue labeled `retro:contribution` on `mycom08/mt-agent-devkit` (was: "open a pull request"), so the `apply retros` workflow can find the contribution.
- [ST-000014] `CLAUDE_Shared_template.md` — RF-011: Agent File Integrity section: undefined trigger `update agents` and `Update_Agents_Workflow.md` replaced with correct `sync devkit` and `Sync_Devkit_Workflow.md`.
- [ST-000014] `Project_Priming_template.md` — RF-007: §6 document paths replaced deep feature-specific paths with flat top-level paths aligned to `Document_Index_template.md` (`docs/requirements/`, `docs/plan/`, `docs/sprints/`, `docs/technical/`, `docs/wiki/`).
- [ST-000014] `Project_Priming_template.md` — RF-008: §6 hardcoded `Sprint_1_Overview.md` parameterized to `Sprint_N_Overview.md`.
- [ST-000014] `product_owner_instructions_template.md` and `product_owner_instructions.md` — RF-009: Story Closure Task retro format reference changed from `Retro_Rules.md` to `Agent_Common.md §4`, matching all other role instruction files.
- [ST-000014] `business_analyst_instructions_template.md` and `business_analyst_instructions.md` — RF-010: retro section header relabeled from `## Implementer — Business Analyst` to `## Analyst — Business Analyst`.

- [ST-000013] `Developer_Rules_template.md` — RF-005: §4 "Story files" line mode-gated; GitHub mode retains GitHub Issues assertion; Strict mode points to `.claude/agents/docs/stories/ST-XXXXXX.md` and `Strict_Mode_Story_Guide.md`.
- [ST-000013] `Developer_Rules_template.md` — RF-003: §6 Commit Message Rules split into `**GitHub mode:**` (Conventional Commits + `Story:` footer) and `**Strict mode:**` (`<primary-id> [<secondary-id>]: <message>` per `Strict_Mode_Story_Guide.md`) carve-outs; vague "project's own style" reference removed.
- [ST-000013] `Project_Priming_template.md` — RF-006: §3 story-workflow opener mode-gated; Collaboration rules updated — GitHub mode keeps Issues-comments assertion; Strict mode directs to `## Comments` section of story MD.
- [ST-000013] `Strict_Mode_Story_Guide_template.md` — RF-003 (support): §Commit Message Format replaces vague "project's own style" with explicit spec: lowercase imperative phrase ≤ 60 characters; operation substitution table entry updated to reference the section.


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
- [ST-000012 retro] `Story_Standard_template.md` and `Story_Standard.md` — §12 reviewer checklist adds the flag-vs-block rule: a contradiction introduced by the PR blocks approval; a pre-existing problem in an out-of-scope file is approved and recorded as a follow-up story.
- `Project_Priming.md §15` (devkit-internal) — document the dual-update + pre-edit drift-check between templates and their working mirrors.
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
