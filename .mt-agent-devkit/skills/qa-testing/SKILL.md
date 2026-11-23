---
name: qa-testing
description: QA testing rules for the devkit's Markdown-only repo - the test scenario document first, template and workflow checks, shell scripts, changes.json, UI prototype and the failure policy. Load with qa-validate at a story validation spawn.
---

# QA Testing

**Requires:** `qa-core`, `project-docs` (scenario location and naming), `change-metadata` (the `descriptions` format)

This devkit has no runtime service, database or API. QA validates by reading and checking that the template and workflow files are correct and complete.

## Before Testing

- Create the test scenario document first; do not begin testing without it. Place it under `docs/feature/<feature_name>/test-scenarios/` or `docs/sprints/`, named per `project-docs`.
- Cover the happy path, error cases and edge cases (missing placeholders, incorrect path references, mode-specific behavior).
- **Exceptions to the document:** a CI/workflow-only story (Technical Scope is `.github/workflows/**` only) captures the CI run URL(s) as the validation artifact instead; a verification-only story (`Outcome: verification-only`, `Shared_Pipeline_Stages.md` Stage 1) has a zero diff, so skip the document.

## Checks

- **Templates and workflows:** read every template file the story changed. Verify placeholders (`{{PROJECT_NAME}}`, `{github-org}`, etc.) are correct and present where expected, and the `_template` suffix convention (`change-metadata` section 3) under `.claude/agents/templates/`. Verify path references match the devkit's file structure. Check GitHub mode content is complete and accurate; check strict mode separately if the story affects it.
- **Shell scripts:** for each changed `.sh` run `bash -n <script>` with zero errors; for each changed `.ps1` confirm the PowerShell syntax check passes. Review the logic against the intended behavior in the AC.
- **`changes.json`:** if the story modifies template files, verify an entry for the current devkit version lists them, in the right format (array for older versions, object with `files`/`descriptions`/`checksums` from v0.0.8). Each touched `descriptions` entry is a compact `[ST-NNNNNN] <short delta>` clause list (`change-metadata` section 2); flag narrative prose, a restated earlier clause, or rationale in place of what changed.
- **UI prototype:** only if the story touches a repo from Build Software's UI-bearing companion-repo convention, apply `.mt-agent-devkit/rules/UI_Prototype_Rules.md` before sign-off. It does not apply to the devkit's own repo.

## Failure Policy

Any failure blocks sign-off. Post a blocker comment on the issue describing the failure, tagging **Dev**; keep the story in `status:testing`; do not sign off until every validation passes.
