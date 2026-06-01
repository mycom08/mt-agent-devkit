# Technical_Lead_Memory

## Stored Facts

### Fact 1
- **Fact:** The canonical shared ABAC OpenAPI contract is `docs/api/ABAC_API.yaml`; story files define requirements and carry comment-thread review history, not the final implementation contract.
- **Source:** `.claude/agents/context/PROJECT_PRIMING.md`, `docs/feature/Attribute_Based_Access_Control-ABAC/stories/D1_ABAC_Policy_API_Contract.md`
- **Reason:** This prevents future design or implementation work from drifting into story prose when the actual source of truth is the shared OpenAPI artifact.

### Fact 2
- **Fact:** Phase 1 preserves `POST /api/resources/access/check` unchanged and introduces `/api/v1/check` as an additive ABAC-capable contract.
- **Source:** `docs/feature/Attribute_Based_Access_Control-ABAC/stories/D2_Check_Endpoint_Extension_Contract.md`, `docs/api/ABAC_API.yaml`
- **Reason:** This is a durable compatibility boundary that affects future API design, implementation, and review decisions for the ABAC rollout.

### Fact 3
- **Fact:** Technical Lead approval of a design/story review does not by itself justify marking story acceptance, task, or delivery-completion checklists as done unless the underlying work is actually complete.
- **Source:** `docs/feature/Attribute_Based_Access_Control-ABAC/stories/D2_Check_Endpoint_Extension_Contract.md`, working-session correction on 2026-04-13
- **Reason:** This keeps story state accurate by separating review approval from implementation, merge, and delivery completion, which prevents misleading progress tracking in future story updates.

### Fact 4
- **Fact:** API specs must be validated in Swagger Editor and with `swagger-cli validate <spec-file>` before being sent for review.
- **Source:** `.claude/agents/context/PROJECT_PRIMING.md`, `docs/wiki/Development_Standards.md`
- **Reason:** This gives the team one explicit manual and command-line validation rule for OpenAPI review readiness, reducing avoidable review churn caused by invalid specs.

### Fact 5
- **Fact:** Feature branches must use format: `feature/{feature-name}/{story-id}-kebab-case-title`. All branches must include the story ID for traceability; commit messages include `Story: {STORY_ID}` footer.
- **Source:** `docs/wiki/Development_Standards.md` (established pattern for ABAC, generalizable across features)
- **Reason:** Story IDs in branch names provide traceability, make branches discoverable by story and team, ensure consistency across distributed development, and integrate cleanly with project tracking systems (Jira, Azure DevOps).

### Fact 6
- **Fact:** Default decision when no ABAC rules match: no policies exist → ALLOW (backward compat), policies exist but none match → DENY (fail-secure). Resolved by PO Option B sign-off on 2026-04-20.
- **Source:** Issue #5 comment thread, PO sign-off 2026-04-20
- **Reason:** Documents the resolved decision for ST-000008 and future stories that depend on evaluation default behavior.

### Fact 7
- **Fact:** Code review changes-requested comments belong on the PR only, not on the story issue. Story issue comments are for story-level discussion (blockers, summaries, questions). PR comments are for code-specific review feedback.
- **Source:** User correction 2026-04-24
- **Reason:** Keeps review feedback co-located with the code diff, avoids cluttering the story issue with code-level details, and follows the project's separation between story discussion and PR review workflows.

### Fact 8
- **Fact:** When approving a PR, use `gh pr comment <number> --body "..."` instead of `gh pr review --approve`. GitHub blocks self-approval ("Can not approve your own pull request") because the PR author and the account Claude operates under are the same.
- **Source:** User correction 2026-05-14
- **Reason:** Prevents a failed `gh pr review --approve` call; posting a comment with the full review body achieves the same communication goal without hitting the GitHub API restriction.

### Fact 9
- **Fact:** Phase 2 (Sprint 5) ABAC limits raised: max nesting depth ≤5, max conditions per rule ≤11. Enforced in the shared `ValidateConditionNode` helper in `helpers.go` — both `JSONEvaluator` and `CasbinEvaluator` inherit these. Decision made 2026-05-18 answering Issue #82 Q1.
- **Source:** Issue #82 comment #4476133111 (TL decision 2026-05-18)
- **Reason:** Durable constraint change — any future story that adds evaluators or modifies validation must use the Phase 2 limits, not the Phase 1 limits (depth 3, conditions 10).

### Fact 10
- **Fact:** Casbin-format `rule_data` shape is `{"expression": "..."}` — a flat JSON object with a single string field. This is distinct from the JSON-format `ConditionNode` tree. `CasbinRuleData` is the Go struct for it.
- **Source:** Issue #82 comment #4476133111 (TL decision 2026-05-18)
- **Reason:** Prevents confusion between the two rule_data shapes when implementing or reviewing Casbin evaluator code.

### Fact 11
- **Fact:** For `CasbinEvaluator`, attribute re-nesting convention is: `user.*` flat keys → `r.sub.*`, `resource.*` flat keys → `r.obj.*`, all other namespaces → `r.env.*`. This happens inside `CasbinEvaluator.Evaluate`; the shared `EvaluationRequest` stays flat.
- **Source:** Issue #82 comment #4476133111 (TL decision 2026-05-18)
- **Reason:** Fixed mapping convention needed by Dev to implement parameter binding and by QA/TL to verify tests.

### Fact 12
- **Fact:** `AttributeProvider` (ST-000027) is injected into `ABACService`, not `EvaluationEngine`. When `ATTRIBUTE_PROVIDER_URL` is unset, pass `nil` — no-op path. Merge nested maps (provider wins on conflict) before `flattenAttributes` inside `EvaluateAccess`.
- **Source:** Issue #84 comment #4476135778 (TL decision 2026-05-18)
- **Reason:** Keeps `EvaluationEngine` as pure computation; documents the injection point so future reviews can verify placement is correct.

### Fact 13
- **Fact:** `JSONEvaluator.regexCache` (`sync.Map`) is keyed by **pattern string**, not rule ID. Patterns are immutable after creation-time validation, so the cache is always correct and no `InvalidateRule` mechanism is needed. Identical patterns used across different rules share one compiled `*regexp.Regexp` entry. `EvaluationEngine` holds no reference to `JSONEvaluator` directly — `InvalidateRule` does not exist anywhere in the codebase.
- **Source:** ST-000026 CR-1 fix commit `1370236`; `internal/evaluation/json_evaluator.go`
- **Reason:** Documents the final cache design so future reviews of evaluator changes do not reintroduce a rule-ID-keyed cache or an unnecessary invalidation path.

### Fact 14
- **Fact:** ST-000028 (Redis Pub/Sub cache): `PolicyCache` becomes a Go interface with `Get`, `Set`, `Evict`. Struct renamed `InProcessPolicyCache`. Factory `NewPolicyCacheFromEnv(ctx context.Context) (PolicyCache, error)` in `service` package. `NewABACService` accepts `PolicyCache` as a constructor parameter (no longer constructs internally). Redis client: `github.com/redis/go-redis/v9`. Subscriber goroutine tied to `signal.NotifyContext` shutdown context; `RedisPolicyCache` exposes `Start(ctx)`. `main.go` must adopt `http.Server.Shutdown` with 5-second drain.
- **Source:** Issue #89 comment #4497214394 (TL decision 2026-05-20)
- **Reason:** Interface refactoring affects every future story that touches the cache layer or `NewABACService` constructor.

### Fact 15
- **Fact:** ST-000029 (Admin UI Readiness): hand-rolled `corsMiddleware` in `main.go` removed; replaced with `github.com/rs/cors` wired from `CORS_ALLOWED_ORIGINS` (empty = no open CORS). Rate limiter is a Chi middleware in `internal/middleware` package on `POST /api/v1/check` only; shares Redis client from ST-000028 (not re-created). Redoc static assets live in `web/` directory; `//go:embed web/redoc.standalone.js` and `//go:embed web/openapi.yaml`; both `/api/docs` routes bypass auth middleware group.
- **Source:** Issue #90 comment #4497221648 (TL decision 2026-05-20)
- **Reason:** Documents integration boundary between ST-000028 and ST-000029 (shared Redis client) and the CORS/asset placement decisions needed for future implementation and review.

### Fact 16
- **Fact:** Phase 3 Keycloak sandbox (ST-000033): image `quay.io/keycloak/keycloak:26`; seeding via realm import JSON at `docker/sandbox/keycloak/realm-export.json` with `--import-realm`; activated as opt-in `--profile keycloak` compose override (default Basic Auth sandbox unchanged). No service code changes needed — existing `realm_access.roles` extraction in `internal/auth/context.go` already feeds Casbin RBAC via `TokenContext.Roles`. Custom `dom` claim must be mapped in the realm JSON client scope. Casbin seed must add a named-role policy (e.g., `documents-reader`) alongside the existing wildcard entry.
- **Source:** `.claude/agents/tmp/questions_for_TL.md` TL-B1 through TL-B4, resolved 2026-05-22
- **Reason:** These decisions affect ST-000033 implementation, ST-000031 test design, and any future OIDC-related stories.

### Fact 17
- **Fact:** Phase 3 rate-limit testing (ST-000032): tests run against a separate compose override with `RATE_LIMIT_ENABLED=true` and `RATE_LIMIT_REQUESTS_PER_MINUTE=5` (not 100). Newman fires 6 requests; asserts 6th returns HTTP 429 with `{"code":"RATE_LIMIT_EXCEEDED",...}`. Existing automation suite (ST-000030) runs with `RATE_LIMIT_ENABLED=false` and must not be modified. In-process `InProcessRateLimiter` (token bucket) is sufficient — no Redis needed for rate-limit tests.
- **Source:** `.claude/agents/tmp/questions_for_TL.md` TL-A1, resolved 2026-05-22
- **Reason:** Prevents Dev and QA from assuming the default sandbox can test rate limiting or that Redis is required for ST-000032.

### Fact 18
- **Fact:** Phase 3 refactoring guide (ST-000034) path confirmed: `docs/feature/Attribute_Based_Access_Control-ABAC/technical/ABAC_Refactoring_Guide.md`. Scope: `internal/evaluation/`, `internal/service/`, `internal/api/`, `internal/repository/`, `internal/model/`, `cmd/server/main.go`. Excluded: `internal/auth/`, `internal/casbin/`, `internal/db/migrations/`, `configs/`. Regression verification (ST-000035) requires all three layers: `go test ./... -short` ≥85% per package (applies to `internal/evaluation/`, `internal/service/`, `internal/api/` only — not `internal/model/` or `internal/repository/`) + `go test ./...` (integration) + Newman `npm run test:ci` 0 failures against pre-Sprint-7 `ABAC_Collection.json` only (no Keycloak dependency).
- **Source:** `.claude/agents/tmp/questions_for_TL.md` TL-C1, TL-C2, TL-C3, resolved 2026-05-22; Issue #99 Q1/Q2 answers 2026-05-22
- **Reason:** Documents scope and verification gate for Dev to implement ST-000035 without ambiguity.

### Fact 19
- **Fact:** ST-000033 Keycloak realm mapper: user attribute name is `dom` on both `rbac-user` and `abac-user`, mapper type is `User Attribute`, token claim name is `dom` (String, added to access token). Commands in README run from `docker/sandbox/` directory. Keycloak port mapped to `8180`; realm name is `sandbox`; client `authorization-service` is public (password grant, no client_secret). Newman pre-request in ST-000031 uses `http://localhost:8180/realms/sandbox/protocol/openid-connect/token`.
- **Source:** Issue #97 Q1/Q2, Issue #95 Q2 answers 2026-05-22
- **Reason:** Durable decisions for ST-000033 implementation and ST-000031 test authoring — both depend on these exact values.

### Fact 20
- **Fact:** ST-000032 API spec gap: `POST /api/v1/check` must have a `429 TooManyRequests` response added to `ABAC_API.yaml` as a deliverable of ST-000032 (not a pre-existing spec entry). Rate-limit sandbox (docker-compose.rate-limit.yml) inherits `OIDC_ENABLED=false`; Newman collection uses Basic Auth. `InProcessRateLimiter` token bucket is not fixed-window — 6 sequential requests in milliseconds safely consume 6 tokens without triggering a refill, so no inter-request delay is needed in Newman. All ST-000031 test cases target `POST /api/v1/check` only; legacy endpoint excluded.
- **Source:** Issue #96 Q1/Q2/Q3, Issue #95 Q1 answers 2026-05-22
- **Reason:** Documents the spec update obligation and test design decisions so future reviews can verify both.

