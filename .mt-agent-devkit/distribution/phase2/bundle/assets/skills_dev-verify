---
name: dev-verify
description: Developer verification rules - technical doc divergence (stop or continue, tag TL), plus the target-only touched-endpoint and behavioral sandbox checks that do not apply to the devkit's Markdown-only repo. Load when a technical doc is wrong or a change needs endpoint or sandbox verification.
---

# Dev Verify

**Requires:** `comment` (before posting on the issue), `raise-question` (blockers), `pre-pr-gate` (the other verification gates)

## 1. Technical Doc Divergence

If a technical document is inaccurate, contradictory or ambiguous during implementation:

1. **Do not silently deviate.** Post on the story immediately and tag **TL**.
2. **TL decides** whether it is fixed now (blocking) or after the story (non-blocking).

| Severity | Action |
|---|---|
| Blocks implementation | [BLOCKING] Stop. Post the comment. Wait for the TL fix. |
| Non-blocking | [NON-BLOCKING] Post the comment. Continue. TL fixes it after the story. |
| Ambiguous | [NON-BLOCKING] Post the comment. Ask TL to clarify before implementing that part. |

## 2. Touched-Endpoint Verification

When the story touches an endpoint:

1. Before writing code, verify its API spec (`docs/api/`): shape, required fields, enums and constraints.
2. If the spec is missing or inconsistent, post a comment to TL and wait for the blocking decision.
3. Before merge, confirm the implementation matches the spec for every affected endpoint.

This is distinct from the spec-first update and codegen step in `dev-implement`.

## 3. Behavioral Sandbox and Integration Verification

1. Before opening a PR, a behavioral change (source code, SQL migrations, config files, Docker files, environment variables or CI pipeline logic) starts the local services with `docker compose` and runs requests against the sandbox stack to verify the expected behavior end to end.
2. A behavioral change needs an integration test script that exists and passes via Git Bash.
3. Any story with an existing integration script runs it: `bash tests/feature/.../ST-XXXXXX_*.sh` (see `docs/wiki/Testing_Guidelines.md`). This duty also applies to non-behavioral stories.
4. Docs, README and API-spec name or description changes with no request/response-shape impact need no local service test. Every `pre-pr-gate` check still applies.
