# Developer Memory

## Stored Facts

- `scripts/validate_templates.py` (ST-000016): Layer-1 corpus invariant checker. 6 invariants, cross-platform Python 3. RETIRED_TRIGGERS=[] by design; `--test-retired-trigger <token>` for fixture testing. `_is_shared`/`_is_thin_variant` check path.parts (not TEMPLATES_DIR-relative) so fixtures work without being under templates/. RUNTIME_PATH_PREFIXES includes `.claude/agents/working-record/` (gitignored in devkit) and `.claude/agents/tmp/`, `.claude/agents/docs/`, `.claude/agents/retros/` (runtime-generated).
- `changes.json` uses newest-first (descending) key order by convention. Validator checks semver parseability only, not ordering direction.
- `.github/workflows/validate-templates.yml` (ST-000016): triggers on `push: branches: [ci-validation]` AND `pull_request: paths: [templates/**, workflows/**]`. The push trigger satisfies CICD_Validation_Guide requirement for pre-merge ci-validation run. First workflow in the repo.
- CICD guide requirement: workflows must have `on.push.branches: [ci-validation]` OR no branch filter. PR-only workflows need the push trigger added permanently to enable ci-validation gate.

## Troubleshooting Facts

- Working-record files (`.claude/agents/working-record/`) referenced in instruction templates are gitignored in the devkit. They fail reference-integrity checks in CI (runner can't find them via Root 2 since the gitignored files aren't checked out). Fix: add `.claude/agents/working-record/` to RUNTIME_PATH_PREFIXES. This was discovered only after the first ci-validation run (not catchable locally).
