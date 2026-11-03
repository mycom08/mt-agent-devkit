---
name: credential-gate
description: Credential-gated verification for implementers, reviewers and QA - a missing runtime secret means stop and report, never a dummy value or an analogy, and an authorization to proceed is not PASS evidence. Load when verification needs a secret you don't have.
---

# Credential Gate

**Requires:** `agent-security` (never handle or request the secret itself)

Canonical owner. `generate_common_blocks.py` copies part `gate` into `Agent_Common_Read_On_Demand.md` §6 and `Agent_Common_Credential_Gate.md`; edit here, then regenerate.

A missing credential blocks the check that needs it: do not substitute a dummy value and call it verified.

<!-- part: gate -->
Applies whenever a story's verification requires a runtime secret (API token, PAT, signing key, DB password, etc.) that is not available in your working environment.

- **Never self-approve a skip.** A dummy-value substitute, or an analogy to a different code path/CI job that happens to use the same secret, is not equivalent to exercising the real credential — do not treat it as sufficient verification.
- **Stop and report** the specific constraint: what credential is missing, why, what you verified without it, and what the credential would additionally prove.
- **Wait** for either the real credential or explicit user authorization to proceed with permitted work. Quote that authorization in your report or retro. An authorization to proceed is not PASS evidence: unexercised AC remain NOT VERIFIED, and acceptance/merge/closure require verification or an approved tracked split with renewed QA under `Story_Standard.md §14`.
<!-- /part: gate -->
