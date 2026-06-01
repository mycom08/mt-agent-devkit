# Developer_Memory

> **READ THIS FILE** at the start of every session, immediately after reading `Developer_Working_Record.md` and before starting any story work. Facts here are durable conventions that override default assumptions.

## Stored Facts

### Fact 1
- **Fact:** When an OpenAPI field must keep symbolic operator wire values such as `==` or `<=`, model it as `type: string` with a validating `pattern` and examples instead of a literal enum.
- **Source:** PROJECT_PRIMING.md section 4.2 API Spec Standard
- **Reason:** Keeps ABAC API contracts Swagger Editor compatible while preserving wire format.

### Fact 3
- **Fact:** ABAC docs use `Title_Case_With_Underscores` under `docs/feature/Attribute_Based_Access_Control-ABAC/` with subdirs: `business/`, `technical/`, `stories/`, `questions/`, `plan/`, `developer/`.
- **Source:** PROJECT_PRIMING.md section 4; ST-000003 implementation
- **Reason:** Consistent naming and organization makes ABAC docs discoverable and maintainable.

### Fact 4
- **Fact:** Use explicit SQL migrations (`internal/db/migrations/NNNN_*.{up,down}.sql`) with migration runner, not GORM AutoMigrate for new schemas.
- **Source:** ST-000003 TL decision; `internal/db/migration_runner.go`
- **Reason:** Explicit migrations enable versioning, rollback testing, and safe multi-environment deployment.

### Fact 5
- **Fact:** Soft-deleted ABAC policies are hidden by default (`deleted_at IS NULL`); audit records immutable and retained indefinitely.
- **Source:** ST-000003 PO Response
- **Reason:** Preserves audit trail while keeping active data clean; supports compliance requirements.

### Fact 6
- **Fact:** Use `json.RawMessage` for GORM JSONB columns instead of `gorm.io/datatypes.JSONType` (generic type).
- **Source:** internal/model/abac_policy.go
- **Reason:** Simpler, no generic parameter instantiation needed.

### Fact 7
- **Fact:** Avoid variable name collisions with package names (e.g., `db` shadowing the `db` package). Use `dbConnection` for GORM instances.
- **Source:** cmd/server/main.go
- **Reason:** Prevents import shadowing and enables proper package function calls.

### Fact 8
- **Fact:** Migration runner tracks applied migrations in `migrations_applied(id, migration_name, applied_at)` table to ensure idempotence.
- **Source:** internal/db/migration_runner.go; integration tests
- **Reason:** Prevents duplicate execution and enables rollback tracking.

### Fact 9
- **Fact:** Startup order: resource table check → explicit SQL migrations → Casbin init. Migration runner must execute before Casbin.
- **Source:** cmd/server/main.go
- **Reason:** Ensures ABAC schema exists before Casbin adapter initializes.

### Fact 10
- **Fact:** GitHub closing keywords (`Closes #N`) only auto-link a PR to an issue when the PR targets the **default branch**. For PRs targeting feature branches, manually link via the PR sidebar → Development → "Link an issue" in the GitHub UI. No programmatic API supports this for non-default-branch PRs.
- **Source:** ST-000008 PR #31 workflow; GitHub GraphQL API limitation
- **Reason:** All story branches target `feature/abac`, not `main`. Every PR must be manually linked to its issue via the GitHub UI after creation.

### Fact 11
- **Fact:** When addressing a TL code review (CR), exercise judgment — do not just execute the suggestions blindly. Cross-check the CR against the full handler logic, identify any gaps the TL may not have explicitly listed, and raise questions on the PR before pushing the fix.
- **Source:** ST-000018 CR-1 review session (2026-05-11)
- **Reason:** The TL's CR redirected `TestReadiness_CasbinNil_Returns503` to test "enforcer nil" but left the "nil-interface casbin" readiness path untested. A developer who only executes without thinking would miss this gap. Raising it proactively is part of the developer's responsibility.

### Fact 12
- **Fact:** For paginated list endpoints, pair each `GetByXxx(ctx, limit, offset)` repo method with a corresponding `CountByXxx(ctx)` method in the same interface. The service computes `offset = (page-1)*pageSize` and calls both in sequence to produce `{ items, total, page, pageSize }`. Defaults (page=1, pageSize=20) and cap (pageSize≤100) are enforced in the service, not the handler.
- **Source:** ST-000021 implementation
- **Reason:** Keeps pagination logic centralised in the service layer and makes the repository interface symmetric (list + count always go together).

### Fact 13
- **Fact:** For read-only "test/preview" endpoints that evaluate but do not persist, implement the logic in the service layer (not the handler), call `EvaluationEngine.EvaluateRules` directly, and walk the `ConditionNode` tree with a `walkConditionNode` helper to collect per-leaf match details. The handler must extend the `abacServiceInterface` with the new method to maintain testability.
- **Source:** ST-000022 implementation
- **Reason:** Keeps evaluation logic in the service, ensures the handler's mock interface stays in sync, and separates the read-only preview path clearly from the persisting CRUD path.

### Fact 14
- **Fact:** govaluate (github.com/casbin/govaluate) parses dot-notation access like `r.sub.department` as a single `ACCESSOR` token whose `Value` is `[]string{"r", "sub", "department"}` — not a `VARIABLE` token. Token whitelisting must check `tok.Kind == govaluate.ACCESSOR` and validate `parts[0] == "r"` and `parts[1]` in the allowed namespace set. Function calls with an undefined function name cause a parse error before token inspection is reached.
- **Source:** ST-000025 CasbinEvaluator implementation; manual token inspection
- **Reason:** Critical for correct token whitelist implementation; VARIABLE kind is never produced for dotted paths.

### Fact 15
- **Fact:** Shared evaluation limits are `MaxConditionDepth = 5` and `MaxTotalConditions = 11` (raised in Phase 2 from 3/10). Both constants live in `internal/evaluation/helpers.go` and apply to both JSONEvaluator and CasbinEvaluator.
- **Source:** ST-000025 TL refinement answers; helpers.go
- **Reason:** Single enforcement point so any future evaluator inherits limits automatically without per-evaluator duplication.

### Fact 16
- **Fact:** `JSONEvaluator` has a `sync.Map regexCache` keyed by **pattern string** (not rule ID) storing compiled `*regexp.Regexp`. Patterns are immutable after creation-time validation so the cache never becomes stale — no `InvalidateRule` method exists. Identical patterns used across multiple rules share one compiled entry. There is no `ruleID` parameter in the internal evaluateNode/evaluateCondition/evaluateAnd/evaluateOr/evalMatches chain.
- **Source:** ST-000026 CR-1 fix (commit 1370236); json_evaluator.go, evaluation_engine.go, abac_service.go
- **Reason:** The original rule-ID-keyed cache caused collisions when one rule had two MATCHES conditions with different patterns. Pattern-keyed cache is correct, simpler, and more memory-efficient.

### Fact 17
- **Fact:** `DATE_BETWEEN` uses RFC3339 (`time.RFC3339`) for both the attribute value and the two-element `[start, end]` array. Comparison is `!attrTime.Before(startTime) && !attrTime.After(endTime)` (inclusive on both sides). Timezone offsets are handled correctly by `time.Parse(time.RFC3339, ...)`.
- **Source:** ST-000026 TL/PO refinement answers; json_evaluator.go
- **Reason:** Inclusive-both-sides is the PO-decided product behaviour; `time.Parse` normalises timezones so cross-timezone comparisons are always correct.

### Fact 18
- **Fact:** `AttributeProvider` interface lives in `internal/evaluation/attribute_provider.go`. `HTTPAttributeProvider` enforces a 500ms client timeout and returns an error on non-2xx, timeout, or network failure. `MergeAttributes` is a standalone helper (non-mutating, provider wins on conflict). The provider is injected into `ABACService` via the last constructor parameter (nil = disabled). The merge happens in `EvaluateAccess` before `NewEvaluationRequest`; on provider failure the service logs at WARN and continues with caller-supplied attributes (soft fallback). Integration tests use `httptest.NewServer` (not shell scripts) for provider mocking.
- **Source:** ST-000027 TL refinement answers; attribute_provider.go, abac_service.go
- **Reason:** Provider I/O belongs in the service layer (not the engine). Soft fallback pattern is critical — panics propagate to Chi's Recoverer, not silently swallowed.

### Fact 19
- **Fact:** `RedisPolicyCache` uses an internal `redisClientAdapter` interface (Ping, Publish, PSubscribe, Close) so tests can inject a `mockRedisClient` without a live Redis server. The real `*redis.Client` satisfies the interface directly. Production code constructs via `NewRedisPolicyCache`; tests use `newRedisPolicyCacheWithClient`. `Evict` publishes to `abac:invalidate:<tenantDomain>:<resource>`; `handleInvalidation` calls `local.Evict` (not `c.Evict`) to avoid re-publishing. Subscriber goroutine tied to `signal.NotifyContext` context; `Start(ctx)` is called from `main.go` after factory construction.
- **Source:** ST-000028 TL refinement answers; redis_policy_cache.go
- **Reason:** Interface injection is the standard Go testability pattern for external clients. Calling `local.Evict` in the subscriber is critical to prevent infinite pub/sub loops.

### Fact 20
- **Fact:** `github.com/rs/cors` defaults to allowing ALL origins when `AllowedOrigins` is an empty slice (`len == 0` → sets `allowedOriginsAll = true`). To achieve deny-all default, set `AllowOriginFunc: func(origin string) bool { return false }` instead of passing an empty slice.
- **Source:** ST-000029 implementation; rs/cors v1.11.1 cors.go line 163-167
- **Reason:** The go-chi/cors package behaviour is counterintuitive — empty slice means "allow all", not "allow none". Always use AllowOriginFunc for deny-all semantics.

### Fact 21
- **Fact:** `//go:embed` paths are relative to the Go source file's package directory. Paths cannot contain `..`. To embed files from a directory like `docs/api/`, the Go source file containing `//go:embed` must live at `docs/api/` or a subdirectory of it. A dedicated embed-only package (e.g., `docs/api/docsembed.go`) is a clean pattern when the asset source is not under any existing Go package directory.
- **Source:** ST-000029 implementation; Go embed documentation
- **Reason:** Avoids asset duplication — one canonical location for assets, one embed package, handler imports the embed package.

### Fact 22
- **Fact:** To share a Redis connection between `RedisPolicyCache` (pub/sub) and a rate limiter (INCR/EXPIRE), add a `RateLimitAdapter() *RedisRateLimitAdapter` method to `RedisPolicyCache` that type-asserts the internal `redisClientAdapter` to `*redis.Client`. The rate limiter middleware defines its own `RedisIncrExpirer` interface; `RedisRateLimitAdapter` in the service package satisfies it. This avoids a second Redis dial and keeps the middleware package free of a direct go-redis dependency.
- **Source:** ST-000029 TL refinement answers; internal/service/redis_rate_limit_adapter.go
- **Reason:** Single Redis connection is the correct pattern; adapter lives in service package to avoid circular import (middleware → service → middleware).

### Fact 23
- **Fact:** Keycloak 26 (`quay.io/keycloak/keycloak:26.2`) uses a ubi-micro base image without `curl` or `wget`. The healthcheck must use bash `/dev/tcp` TCP: `exec 3<>/dev/tcp/localhost/8080 && printf 'GET /path HTTP/1.0\r\nHost: localhost\r\n\r\n' >&3 && grep -q '200 OK' <&3`. The tag `26` does not exist in quay.io — use `26.2` (or specific patch tag).
- **Source:** ST-000033 sandbox testing
- **Reason:** curl/wget are not in ubi-micro; bash TCP is the only built-in HTTP check available in Keycloak containers.

### Fact 24
- **Fact:** In the sandbox, the Casbin enforcer loads policies at service startup (before `casbin-seed` runs). After the sandbox starts and casbin-seed completes, the authorization-service must be restarted (`docker compose restart authorization-service`) to reload the seeded Casbin rules. This is a known timing issue in the compose ordering: casbin-seed waits for `/healthz/live` (service up) but Casbin has already loaded empty policies.
- **Source:** ST-000033 sandbox testing; internal/casbin/provider.go LoadPolicy()
- **Reason:** Critical for sandbox usage — without restart, all RBAC checks fail even though rules are in the DB.

### Fact 25
- **Fact:** Keycloak realm JSON import with `--import-realm`: do not reference Keycloak built-in client scopes (`web-origins`, `acr`, `roles`, `profile`, `email`) in `defaultClientScopes` — these are created by Keycloak per-realm and the import fails to resolve them with warnings. Instead, add custom mappers directly as `protocolMappers` on the client. Keycloak auto-assigns built-in scopes to clients created during import.
- **Source:** ST-000033 realm-export.json testing; Keycloak 26.2 import logs
- **Reason:** Avoids "Referenced client scope 'X' doesn't exist. Ignoring" warnings and ensures all tokens contain standard claims (realm_access, profile, email) alongside custom claims.

### Fact 26
- **Fact:** `evaluation.PolicyInput` (aliased as `type Rule = PolicyInput`) is a pure computation type with no GORM tags. Fields: ID, Name, Effect, Format, Data, Priority, Enabled. TenantID and Resource are NOT in PolicyInput — they stay on model.ABACPolicy. `policyToRule` must not copy TenantID/Resource. The type alias makes `evaluation.Rule` a synonym for `evaluation.PolicyInput` at zero allocation cost.
- **Source:** ST-000035 I-01/I-02 implementation; internal/evaluation/types.go
- **Reason:** Separation of concerns: model.ABACPolicy owns storage/tenant fields; PolicyInput is the pure evaluation contract passed to the engine.

### Fact 27
- **Fact:** When the `internal/service` and `internal/api` packages contain large legacy non-ABAC code (ResourceService, PolicyService, TenantService, ResourceHandler etc.) at 0% unit coverage, overall package coverage will be dragged far below 85% even when ABAC code is fully covered. The 85% coverage gate intended by TL applies to ABAC-specific code; the base coverage of the service package is ~43-47% due to these legacy files. Always flag this in PR descriptions when coverage gates are written as package-level percentages.
- **Source:** ST-000035 Layer 1 coverage analysis
- **Reason:** Prevents wasted effort writing tests for unrelated legacy code when the TL's intent is ABAC code coverage.