# QA Memory

## Stored Facts

- ST-000016 (PR #34): The Layer-1 validator produces `[KNOWN_ISSUE]` output (not `[ERROR]`) for the known Blocked_Request_Template.md capital-T typo in two shared workflow files — this is expected and does not block CI or QA sign-off.
- `docs/Template_Test_Strategy.md` is the canonical test-approach reference for template/workflow changes (3-layer model: Layer-1 static / Layer-2 deployment / Layer-3 behavioral; the 6 invariant specs; risk tiers A/B/C; coverage model; AC-as-oracle pattern; deferred Layer-2/3 roadmap). Read it for the *why/how*; the scripts below are the Layer-1 *mechanics*. Wired into QA_Rules §8/§9 and Project_Priming §8.
- The full automation suite for this devkit (no runtime, no API) is: `python scripts/validate_templates.py` (corpus invariant check) + `bash scripts/test/run.sh` (fixture self-test). Both must exit 0.
- For additive-only PRs (scripts/docs/CI only, no templates or workflows changed), regression check is: confirm `git diff main..HEAD --name-only` contains no files under `.claude/agents/templates/` or `.claude/agents/workflows/`.
- Fixture for invariant #4 (retired-trigger) requires `--test-retired-trigger TEST_RETIRED_TRIGGER_DO_NOT_USE` flag because `RETIRED_TRIGGERS` is empty in production. This is by design.
- Invariant #5 (manifest integrity) has no standalone bad fixture — it is validated by running `python scripts/validate_templates.py` against the full corpus.
- To run the Layer-1 gate against a PR branch without disturbing the current working tree, use `git worktree add <scratch-path> origin/<branch>` then run both scripts against `<scratch-path>`; `git worktree remove <scratch-path> --force` to clean up. If the working tree happens to already be on the dev branch (common — implementers/reviewers often leave it checked out there), running directly is fine too; check `git branch --show-current` first.
- When a PR claims an invariant/resume-rule bullet is "untouched" by a change, verify with `git diff main origin/<branch> -- <file>` scoped to that bullet's text and confirm it shows zero `+`/`-` lines (appears only as context) — do not infer "untouched" from the absence of a hunk elsewhere in the diff or from trusting the reviewer's summary (ST-000026, ST-000025 precedent).
- For any AC whose correctness mechanism is a `gh`/CLI query (idempotency checks, dedup keys, filters), construct at least one adversarial input by hand (e.g. a prefix-title case for exact-line-match idempotency) rather than only re-reading the fix's prose — mirrors the TL-side review lesson recorded in Technical_Lead_Memory for ST-000026.

## Troubleshooting Facts

No troubleshooting facts recorded yet.
