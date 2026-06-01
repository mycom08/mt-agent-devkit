# Developer Working Record - ABAC Feature

This document tracks the Developer's progress on the ABAC (Attribute-Based Access Control) feature implementation. It records completed tasks, code changes, current work, and impediments across rolling 3-day windows.

---

## 2026-05-29 (Today)

### Completed
- ✅ **ST-000034 PEER REVIEW** — Reviewed TL-authored `docs/feature/Attribute_Based_Access_Control-ABAC/technical/ABAC_Refactoring_Guide.md` (commit `ba6bbca` on `feature/abac-phase-3`) against all 5 AC items in issue #98. All AC pass: scope matches (6 packages + main.go, correct exclusions), 20 issues documented with rationale, three-layer regression suite specified (Layer 1 ≥85% coverage on evaluation/service/api packages, Layer 2 full integration tests, Layer 3 Newman 0 failures), file at correct path, TL self-approved. Approval comment posted at https://github.com/lhtuwrk/authorization-service/issues/98#issuecomment-4572786120.
- ✅ **ST-000035 IN REVIEW** — Branch `ST-000035/abac-refactoring` from `feature/abac-phase-3`. Implemented all 20 refactoring items (I-01 through I-20) from `docs/feature/Attribute_Based_Access_Control-ABAC/technical/ABAC_Refactoring_Guide.md`. Key changes: `PolicyInput` pure computation type (type alias `Rule = PolicyInput`), `GetAllByTenantAndResource` explicit no-pagination method, `PolicyCache.Start` lifecycle, shared Redis client via `DialRedis`/`NewRedisRateLimitAdapter`, `BuildAllowedOriginsHandler` extracted to `internal/middleware/`, construction-time `TemplateLoader` caching, removed deprecated `RegisterRoutes`/`policyToResponse`/`ValidateRule`/log calls. Tests added: I-17 casbin routing, I-18 attribute provider fallback, errors_test.go, policy_cache_factory_test.go. Regression: evaluation 91.3%, `go test ./...` 0 failures, Newman 55 assertions 0 failures. PR #116 → `feature/abac-phase-3`. Issue #99 → `status:review`. Coverage note: `internal/service` (47.2%) and `internal/api` (64.1%) below 85% gate due to pre-existing legacy non-ABAC code; flagged for TL confirmation in PR description.
- ✅ **ST-000035 MERGED** — QA signed off (all AC passed, Newman 55/55 green). PR #116 merged into `feature/abac-phase-3`. Remote branch `ST-000035/abac-refactoring` deleted. Local branch switched to `feature/abac-phase-3` and pulled (up to date). Merge confirmation comment posted at https://github.com/lhtuwrk/authorization-service/issues/99#issuecomment-4575828798.

### In Progress
- None.

### Impediments
- None.

### Sprint Status
| Story | Status |
|---|---|
| ST-000034 | Done — peer review approved; awaiting PO closure |
| ST-000035 | Merged — PR #116 merged into `feature/abac-phase-3`; awaiting PO closure |

---

## 2026-05-22

### Completed
- ✅ **Sprint 7 Refinement** — Read issues #97 (ST-000033) and #99 (ST-000035). Analysed each against codebase (`internal/config/config.go`, `internal/auth/validator.go`, `docker/sandbox/docker-compose.yml`, `docker/sandbox/casbin_seed.sql`, automation `package.json`, Sprint 7 overview). Posted refinement comments: issue #97 comment at https://github.com/lhtuwrk/authorization-service/issues/97#issuecomment-4515998737 (2 TL questions, 1 PO question); issue #99 comment at https://github.com/lhtuwrk/authorization-service/issues/99#issuecomment-4516004860 (2 TL questions, 1 PO question). Both threads set to Open; awaiting TL and PO answers.
- ✅ **Sprint 7 Refinement Stage 3** — Reviewed all TL and PO answers on issues #97 and #99. All answers clear and sufficient. Posted all-clear final replies: issue #97 at https://github.com/lhtuwrk/authorization-service/issues/97#issuecomment-4516098813 (Thread Status: Resolved); issue #99 at https://github.com/lhtuwrk/authorization-service/issues/99#issuecomment-4516100174 (Thread Status: Resolved).
- ✅ **ST-000033 IN REVIEW** — Branch `ST-000033/sandbox-keycloak-integration` from `feature/abac-phase-3`. New files: `docker/sandbox/docker-compose.keycloak.yml` (Keycloak 26.2, bash /dev/tcp healthcheck, REDIS_URL cleared, OIDC env override), `docker/sandbox/keycloak/realm-export.json` (realm sandbox, public client authorization-service, dom claim protocol mapper on client, rbac-user + abac-user, documents-reader realm role), `docker/sandbox/README.md` (full sandbox usage docs, Keycloak profile startup, token endpoint, Casbin reload note). Updated `docker/sandbox/casbin_seed.sql` with named-role entry for documents-reader. Zero service code changes. Tested: Keycloak starts and imports realm, both user JWTs contain dom=sandbox-tenant and correct roles, ABAC evaluation passes (Finance+Confidential→allow, Engineering+Confidential→deny), named-role Casbin entry resolves correctly, Basic Auth sandbox unaffected. PR #100 → `feature/abac-phase-3`. Issue #97 → `status:review`.
- ✅ **ST-000033 CR-1 resolved** — Commit `d26f770` pushed to `ST-000033/sandbox-keycloak-integration`. Port mapping corrected from 9090:8080 to 8180:8080 in `docker/sandbox/docker-compose.keycloak.yml`; all four localhost:9090 references in `docker/sandbox/README.md` updated to localhost:8180. Comment posted on issue #97 requesting TL re-review.
- ✅ **ST-000033 REVIEW → TESTING** — TL approved PR #100. Removed label `status:review`, added `status:testing` on issue #97. Added PR #100 link to Deliverables section of issue body. QA notification comment posted at https://github.com/lhtuwrk/authorization-service/issues/97#issuecomment-4516887192.
- ✅ **ST-000033 MERGED** — QA signed off (all AC passed, Newman suite green). PR #100 merged into `feature/abac-phase-3`. Remote branch `ST-000033/sandbox-keycloak-integration` deleted. Local branch switched to `feature/abac-phase-3` and pulled (fast-forward to `bfd49a2`).

### In Progress
- None.

### Impediments
- None.

### Sprint Status
| Story | Status |
|---|---|
| ST-000033 | Done — PR #100 merged into `feature/abac-phase-3` |
| ST-000035 | Backlog — all refinement open points resolved; will remain backlog until ST-000034 is done and ABAC_Refactoring_Guide.md is committed |

---

## 2026-05-21

### Completed
- ✅ **ST-000028 IN REVIEW** — Branch `feature/ST-000028-redis-cache` from `feature/abac-phase-2`. Refactored `PolicyCache` from concrete struct to interface (`Get`, `Set`, `Evict`); renamed `InProcessPolicyCache`. Implemented `RedisPolicyCache` in `internal/service/redis_policy_cache.go` (local InProcessPolicyCache + Redis pub/sub invalidation on `abac:invalidate:<tenantDomain>:<resource>`). `newRedisPolicyCacheWithClient` constructor allows mock injection in tests. `NewPolicyCacheFromEnv(ctx)` factory in `internal/service/policy_cache_factory.go` returns `RedisPolicyCache` when `REDIS_URL` set, else `InProcessPolicyCache` (CACHE_TTL_SECONDS default 300). Updated `NewABACService` to accept `PolicyCache` interface parameter. `main.go` updated: factory call, `rc.Start(ctx)` for Redis subscriber, `signal.NotifyContext` + `http.Server.Shutdown` (5s drain). Config: `REDIS_URL` and `CACHE_TTL_SECONDS` fields added. Optional `redis:7-alpine` service (profile=redis) in `docker/sandbox/docker-compose.yml`. 24 unit tests with `mockRedisClient` in `internal/service/redis_policy_cache_test.go`; 1 integration test gated on `REDIS_URL`+`-short`. All tests pass; `go vet` clean. PR #92 → `feature/abac-phase-2`. Issue #89 → `status:review`.
- ✅ **ST-000029 IN REVIEW** — Branch `ST-000029/admin-ui-readiness` from `feature/abac-phase-2`. CORS: replaced hand-rolled `corsMiddleware` with `github.com/rs/cors`; `CORS_ALLOWED_ORIGINS` env var (empty=deny-all, `*`=allow all, comma list=whitelist); `buildCORSHandler` in `main.go`. Redoc: embedded at `GET /api/docs` and `GET /api/docs/openapi.yaml`; assets at `docs/api/assets/redoc.standalone.js` and `docs/api/ABAC_API.yaml`; embed package at `docs/api/docsembed.go` (package docsapi); handler at `internal/api/docs_handler.go`; routes outside auth group. Rate limiting: `internal/middleware` package with `RateLimiter` interface, `InProcessRateLimiter` (token bucket, configurable), `RedisRateLimiter` (fixed-window, configurable), `RateLimitMiddleware`, `NewRateLimiterFromEnv`; config: `RATE_LIMIT_ENABLED` (toggle, default true), `RATE_LIMIT_REQUESTS_PER_MINUTE` (default 100); `service.RedisRateLimitAdapter` shares Redis connection from ST-000028. `abac_api.go` refactored: added `RegisterRoutesExcludingCheck`. `ABAC_API.yaml` servers array updated to `http://localhost:8080`. README updated with CORS, rate limiting, docs sections. 100% middleware coverage (25 tests); 9 docs handler tests. All tests pass; `go vet` clean; spectral lint zero errors. PR #93 → `feature/abac-phase-2`. Issue #90 → `status:review`.
- ✅ **ST-000029 CR-1, CR-2, A3 resolved** — Commit `84a6030` pushed to `ST-000029/admin-ui-readiness`. CR-1: `go mod tidy` promoted `github.com/rs/cors` from indirect to direct in `go.mod`. CR-2: moved `docs/api/assets/redoc.standalone.js` → `docs/api/web/redoc.standalone.js`; updated `//go:embed` directive in `docs/api/docsembed.go` and `ReadFile` path in `internal/api/docs_handler.go`. A3: godoc comments moved above `//go:embed` directives. README expanded with Redoc route table, usage instructions, and bundle upgrade guide. All tests pass; build clean.

### In Progress
- None.

### Impediments
- None.

---

## Format Guidelines

**Completed:** One concise bullet per story — include key files, PR number, and outcome. No step-by-step sub-items.
- Example: "**ST-000009 DONE** — Implemented 4 CRUD handlers in `internal/api/abac_api.go`, added DI wiring in `main.go`, 19 unit tests pass. TL CR fixed in commit b466558. PR #38 merged → `feature/abac`."

**In Progress:** Current story being worked, or stories awaiting review/QA.
- Example: "ST-000013 PR #48 awaiting TL review."

**Impediments:** Blockers affecting developer work.
- Example: "ST-000017 blocked — awaiting TL answer on Thread 2 (rule_data size limit)."

**Retention:** Delete entries older than 3 days before writing today's entry.
