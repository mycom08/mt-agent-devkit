# QA Memory

## Stored Facts

- ST-000016 (PR #34): The Layer-1 validator produces `[KNOWN_ISSUE]` output (not `[ERROR]`) for the known Blocked_Request_Template.md capital-T typo in two shared workflow files — this is expected and does not block CI or QA sign-off.
- The full automation suite for this devkit (no runtime, no API) is: `python scripts/validate_templates.py` (corpus invariant check) + `bash scripts/test/run.sh` (fixture self-test). Both must exit 0.
- For additive-only PRs (scripts/docs/CI only, no templates or workflows changed), regression check is: confirm `git diff main..HEAD --name-only` contains no files under `.claude/agents/templates/` or `.claude/agents/workflows/`.
- Fixture for invariant #4 (retired-trigger) requires `--test-retired-trigger TEST_RETIRED_TRIGGER_DO_NOT_USE` flag because `RETIRED_TRIGGERS` is empty in production. This is by design.
- Invariant #5 (manifest integrity) has no standalone bad fixture — it is validated by running `python scripts/validate_templates.py` against the full corpus.

## Troubleshooting Facts

No troubleshooting facts recorded yet.
