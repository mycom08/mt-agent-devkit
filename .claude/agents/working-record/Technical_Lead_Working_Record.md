# Technical Lead Working Record - ABAC Feature

This document tracks the Technical Lead progress on the ABAC (Attribute-Based Access Control) feature design and architecture. It records design decisions, API contracts, schema designs, roadmap updates, and impediments across rolling 3-day windows.

---

## 2026-05-29

### Completed
- ✅ **ST-000035 — ABAC Refactoring Code Review — PR #116 — APPROVED (Issue #99):** All 20 refactoring items (I-01 through I-20) verified. `PolicyInput` pure value type replaces `evaluation.Rule` (type alias kept for compat). `NewEvaluationRequestFromMerged` eliminates intermediate `CheckRequest` allocation. `collectConditionMatches` checks `rule.Format` first; leaf eval delegates to engine. `ListPolicies` effect filter pushed to repository (I-06). `PolicyCache.Start` in interface; `main.go` calls unconditionally (I-07). Shared `*redis.Client` via `DialRedis`; rate-limit adapter decoupled from cache (I-08). Deprecated `RegisterRoutes` and `policyToResponse` removed. `BuildAllowedOriginsHandler` extracted to `internal/middleware/`. `TemplateLoader` caches at construction. I-17/I-18 tests added. Coverage gate clarified: 85% applies to evaluation/service/api only (TL Fact 18 — `internal/model/` and `internal/repository/` excluded). Regression: Layer 1 evaluation 91.3%, Layer 2 0 failures, Layer 3 Newman 55/55 pass. Advisory A1: commit subject 59 chars (non-blocking). APPROVED on PR #116 (comment #4575635515). Notify posted on Issue #99 (comment #4575637718).
- ✅ **ST-000034 — ABAC Refactoring Guide (Issue #98):** Analysed all 6 in-scope packages plus `main.go`. Produced `docs/feature/Attribute_Based_Access_Control-ABAC/technical/ABAC_Refactoring_Guide.md` with 20 identified issues (I-01 through I-20) covering: duplicate `evaluation.Rule`/`model.ABACPolicy` types (I-01, I-02), redundant flatten round-trip (I-03), duplicated operator logic in TestPolicy path (I-04, I-05), in-process effect filter pagination bug (I-06), `RedisPolicyCache.Start` not in `PolicyCache` interface (I-07), rate-limit adapter coupling (I-08), dead deprecated `RegisterRoutes` (I-09), conflicting `ValidateRule` implementations (I-10), DTO duplication (I-11), eval engine logging (I-12), magic-zero pagination convention (I-13), double domain derivation (I-14), pointer/value field inconsistency (I-15), TemplateLoader repeated disk reads (I-16), missing Casbin evaluator routing tests (I-17), missing attr-provider fallback test (I-18), unused writeError helper (I-19), untested buildCORSHandler (I-20). Three-layer regression suite specified per AC. PR #115 opened. Issue label updated to status:review.

### In Progress
- None.

### Impediments
- **Story ID discrepancy:** Roadmap IDs vs GitHub issue IDs still unreconciled. PO must update roadmap. (Carry-over)

---

## 2026-05-25

### Completed
- ✅ **ST-000032 Re-Review — PR #114 — APPROVED (Issue #96):** CR-1 resolved in commit e9a1d68. `docs/api/ABAC_API.yaml` — `429` response entry added to `POST /api/v1/check` referencing new `TooManyRequestsError` reusable component; component body matches `rate_limit_middleware.go` (`code: RATE_LIMIT_EXCEEDED`, `message: "too many requests — retry after one minute"`, `details: {}`). Correctly positioned between 401 and 500 entries. Spectral lint PASS. No other files affected. APPROVED on PR #114 (comment #4533366637). Issue #96 label updated to `status:review`.
- ✅ **ST-000032 Code Review — PR #114 — CHANGES REQUESTED (Issue #96):** All 7 ACs structurally verified. Compose override correct (RATE_LIMIT_ENABLED=true, RATE_LIMIT_REQUESTS_PER_MINUTE=5, project name consistent, REDIS_URL not set). TC-RL01–RL05 assert 200; TC-RL06 asserts 429 with exact RATE_LIMIT_EXCEEDED body matching rate_limit_middleware.go line 25. Happy/error-path labels present. ABAC_Collection.json unmodified; existing CI jobs untouched. Token bucket determinism confirmed — no flakiness risk. File placement correct. One blocking item: CR-1 — missing 429 response entry on POST /api/v1/check in ABAC_API.yaml (required deliverable per Issue #96 Q1/Memory Fact 20). Review posted on PR #114 (comment #4533338765). Notify posted on Issue #96 (comment #4533339306).
- ✅ **ST-000031 Hotfix Review — PR #113 — APPROVED (Issue #95):** Bug 1 fix verified — `pm.collectionVariables.set` → `pm.environment.set` in TC-TK01 and TC-TK02 is correct and complete; `sandbox-keycloak.json` defines both token vars as empty strings at env scope, confirming Newman 6.x would always override collection-scope writes. Bug 2 assertion corrections verified accurate: TC-R02/R03 wildcard-allow path was genuine pre-existing test design error (wildcard rule `('*', sandbox-tenant, documents, read, allow)` was always seeded); TC-CA03 resource change to `restricted-docs` is the correct approach for gating RBAC deny (no wildcard on that resource); TC-CA04 401→200 correction aligns with OIDC `dom`-claim domain derivation (Memory Fact 16/19); TC-CA06 `no_policies` assertion is precise. Two new Casbin seed rules (`reports` wildcard, `restricted-docs` named-role) are additive, no conflicts, `ON CONFLICT DO NOTHING` safe for re-runs. Scope clean — no out-of-scope changes. Minor advisory: `casbin_seed.sql` header comment slightly stale (still describes only original named-role rule) — not a blocker. APPROVED on PR #113 (comment #4533047737).
- ✅ **ST-000031 Code Review — PR #112 — CHANGES REQUESTED (Issue #95):** All 7 ACs structurally verified. Collection structure solid — 14 test cases across Token Acquisition, RBAC-Only, and Combined RBAC+ABAC groups. JWT acquisition via Keycloak password grant correct; Keycloak URL/realm/client align with TL decisions (Fact 19). TC-CA06 `reports` resource confirmed intentional — `seed.sql` has no ABAC policies for `reports`, backward-compat allow path (`no_policies`) is correct. AC-4 (Bearer JWTs only) fully satisfied — no Basic Auth anywhere in collection or environment. AC-5 (no casbin seed duplication) verified — `casbin_seed.sql` untouched. One blocking item: CR-1 — CI workflow rewrite drops the entire 29-test Basic Auth `ABAC_Collection.json` job (ST-000030 regression suite) — workflow must run both jobs (Keycloak + Basic Auth) not replace one with the other. Two advisory items: A1 — branch name deviation (recurring); A2 — TC-R01 does not assert final `decision` field (ABAC will deny with empty attributes under fail-secure rule). Review posted on PR #112 (comment #4532687745). Notify posted on Issue #95 (comment #4532689155).
- ✅ **ST-000031 Re-Review — PR #112 — APPROVED (Issue #95):** CR-1 resolved in commit c1cecd7 — `newman.yml` now has two jobs: `api-automation` (Basic Auth, `ABAC_Collection.json`) and `api-automation-keycloak` (Keycloak profile, `ABAC_RBAC_Collection.json`). Both run independently on PR merge or `workflow_dispatch`. A2 addressed — TC-R01 test name and inline comment updated to clarify assertion targets RBAC Check step only; final `decision` is `deny` under fail-secure with empty attributes (comment explains this explicitly). No new issues. APPROVED on PR #112 (comment #4532734320). Issue #95 label updated to `status:review`. Notify posted on Issue #95 (comment #4532735999).

### In Progress
- None.

### Impediments
- **Story ID discrepancy:** Roadmap IDs vs GitHub issue IDs still unreconciled. PO must update roadmap. (Carry-over)



---

## Format Guidelines

**Completed:** Include design decisions, API contracts, schema designs, roadmap updates, and security assessments.
- Example: "Finalized ABAC policy API contract (ST-000001) | Designed extended check endpoint with attributes support (ST-000002)"

**In Progress:** Current designs, technical decisions pending, or design reviews in progress.

**Impediments:** Blockers affecting TL design or technical decisions.

**Retention:** Delete entries older than 3 days before writing today's entry.
