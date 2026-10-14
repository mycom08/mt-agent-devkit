# Agent Common Credential Gate

## 6. Credential-Gated Verification

Applies whenever a story's verification requires a runtime secret (API token, PAT, signing key, DB password, etc.) that is not available in your working environment.

- **Never self-approve a skip.** A dummy-value substitute, or an analogy to a different code path/CI job that happens to use the same secret, is not equivalent to exercising the real credential — do not treat it as sufficient verification.
- **Stop and report** the specific constraint: what credential is missing, why, what you verified without it, and what the credential would additionally prove.
- **Wait** for either the real credential or explicit user authorization to proceed with permitted work. Quote that authorization in your report or retro. An authorization to proceed is not PASS evidence: unexercised AC remain NOT VERIFIED, and acceptance/merge/closure require verification or an approved tracked split with renewed QA under `Story_Standard.md §14`.

---

