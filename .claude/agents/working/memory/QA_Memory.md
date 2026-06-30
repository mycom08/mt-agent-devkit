# QA Memory

## Stored Facts

- ST-000016 (PR #34): The Layer-1 validator produces `[KNOWN_ISSUE]` output (not `[ERROR]`) for the known Blocked_Request_Template.md capital-T typo in two shared workflow files — this is expected and does not block CI or QA sign-off.
- `docs/Template_Test_Strategy.md` is the canonical test-approach reference for template/workflow changes (3-layer model: Layer-1 static / Layer-2 deployment / Layer-3 behavioral; the 6 invariant specs; risk tiers A/B/C; coverage model; AC-as-oracle pattern; deferred Layer-2/3 roadmap). Read it for the *why/how*; the scripts below are the Layer-1 *mechanics*. Wired into QA_Rules §8/§9 and Project_Priming §8.
- The full automation suite for this devkit (no runtime, no API) is: `python scripts/validate_templates.py` (corpus invariant check) + `bash scripts/test/run.sh` (fixture self-test). Both must exit 0.
- For additive-only PRs (scripts/docs/CI only, no templates or workflows changed), regression check is: confirm `git diff main..HEAD --name-only` contains no files under `.claude/agents/templates/` or `.claude/agents/workflows/`.
- Fixture for invariant #4 (retired-trigger) requires `--test-retired-trigger TEST_RETIRED_TRIGGER_DO_NOT_USE` flag because `RETIRED_TRIGGERS` is empty in production. This is by design.
- Invariant #5 (manifest integrity) has no standalone bad fixture — it is validated by running `python scripts/validate_templates.py` against the full corpus.

## Troubleshooting Facts

No troubleshooting facts recorded yet.
