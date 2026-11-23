---
name: qa-testing
description: QA testing rules for the devkit's Markdown-only repo - the test scenario document first, template and workflow checks, shell scripts, changes.json, UI prototype and the failure policy. Load with qa-validate at a story validation spawn.
---

# QA Testing

**Requires:** `qa-core`, `project-docs` (scenario location and naming)

Follow `docs/wiki/Testing_Guidelines.md`.

## Before Testing

- Create the test scenario document first; do not begin testing without it. Place it under `docs/feature/<feature_name>/test-scenarios/`, named per `project-docs`. Cover the happy path, error cases and edge cases (empty values, invalid input, data isolation).
- **Exceptions:** a CI/workflow-only story (Technical Scope is `.github/workflows/**` only) captures the CI run URL(s) plus relevant job log excerpts instead; a verification-only story (`Outcome: verification-only`, `Shared_Pipeline_Stages.md` Stage 1) has a zero diff, so skip the document.

## Coverage

- Each behavior the story adds or changes needs a named test whose primary purpose is that behavior. A side-effect pass, or a test updated to stop failing, is not coverage; add the missing happy-path and primary error-path case.
- An AC that parses, scrapes or calls an external system needs a test driven by a captured real-world fixture, not only mocks. A mock or structural pass is not complete: exercise the code and confirm real output.
- Integration tests with shared setup or teardown: re-run the scenario in isolation before inspecting persisted output, besides the full batch.
- Field-removal stories test both branches: omit the field (succeeds) and include it (rejected, 400 or the spec's code).
- Changed log statements: check `.mt-agent-devkit/rules/Logging_Standard.md`. A screen with a `-ui-prototype` counterpart: apply `.mt-agent-devkit/rules/UI_Prototype_Rules.md`.

## Integration and API

- Derive cases from the API spec (`docs/api/`), never from implementation code; read code only to debug a failure.
- Test every endpoint with `curl` or an equivalent. For several calls, write a runnable `tests/feature/<feature_name>/scripts/ST-XXXXXX_API_Test.sh` (named per `project-docs`) with a base URL variable, headers and a label per request.
- Before any call, read the auth mode from `{sandbox-docker-compose-file}` and `{sandbox-env-file}`: Basic Auth credentials come from the env file, base64-encoded, never hardcoded; token auth gets a bearer token first.
- Run existing integration tests. Skip only for an API-contract-only story or when TL said so in a story comment. Any other constraint (auth mismatch, mode-gated endpoint, missing sandbox config, missing secret per `credential-gate`): report to the user and wait; if escalated, tag **TL** and quote the approved decision in the sign-off.
- The designated script is the only accepted method: fix a failing script's root cause, or post a blocker and stop. Never work around it.

## Failure Policy

Any failure blocks sign-off, whatever the cause ("environmental" is no exception). Post a blocker comment tagging **Dev**, keep the story in `status:testing`, sign off only when every test passes. Every test present must pass: remove a known-broken test and create a backlog story, never disable it.
