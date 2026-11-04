---
name: dev-verify
description: Developer verification rules - technical doc divergence (stop or continue, tag TL), plus the target-only touched-endpoint and behavioral sandbox checks that do not apply to the devkit's Markdown-only repo. Load when a technical doc is wrong or a change needs endpoint or sandbox verification.
---

# Dev Verify

**Requires:** `comment` (before posting on the issue), `raise-question` (blockers)

## 1. Technical Doc Divergence

If a technical document (design, proposal, ownership map, contract) is inaccurate, contradictory or ambiguous during implementation:

1. **Do not silently deviate.** Post on the story issue immediately and tag **TL**.
2. **TL decides** whether it is fixed now (blocking) or after the story (non-blocking).

| Severity | Action |
|---|---|
| Blocks implementation | [BLOCKING] Stop. Post the comment. Wait for the TL fix. |
| Non-blocking | [NON-BLOCKING] Post the comment. Continue. TL fixes it after the story. |
| Ambiguous | [NON-BLOCKING] Post the comment. Ask TL to clarify before implementing that part. |

## 2. Endpoint and Sandbox Verification

Touched-endpoint verification and behavioral sandbox/integration verification apply to target projects only. The devkit has no API, service or sandbox (Project Priming §9 and §14), so neither applies here: its behavior is verified by the `pre-pr-gate` checks.
