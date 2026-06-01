# QA_Memory

## Stored Facts

### Fact 1: ABAC Schema Uses Explicit SQL Migrations
- **Fact:** ABAC feature uses explicit SQL migration files in `internal/db/migrations/` instead of GORM AutoMigrate; migrations are tracked in `migrations_applied` table and executed at startup before Casbin initialization.
- **Source:** ST-000003 implementation, `cmd/server/main.go:46-52`, `internal/db/migration_runner.go`
- **Reason:** This pattern provides atomic, versioned deployments with clean rollback support. Unlike AutoMigrate which lacks idempotence tracking, the migration runner prevents re-applying migrations and enables easy rollback testing. QA must verify idempotence on every service restart and confirm migrations_applied tracking works correctly.

### Fact 2: ABAC Policies Use Soft-Delete with Audit Trail
- **Fact:** ABAC policies implement soft-delete (deleted_at, deleted_by fields) to preserve audit history; queries must filter `deleted_at IS NULL` to hide deleted policies by default. Audit records are immutable and retained indefinitely.
- **Source:** ST-000003 acceptance criteria, ABAC_Database_Schema.md, story comment thread (PO Response - 2026-04-16)
- **Reason:** Multi-tenant compliance requires audit trails that survive policy deletions. QA must verify soft-deleted policies don't appear in list operations and that audit records remain even after policy deletion (CASCADE on policy, but no cascade on audit).

### Fact 3: ABAC Uses Multi-Tenant Isolation via tenant_id
- **Fact:** `tenant_id` is validated from JWT claims (never exposed in API); all ABAC queries must filter by tenant_id to prevent cross-tenant data leakage. Phase 1 has no tenants table; tenant_id is a string key derived from JWT domain context.
- **Source:** ST-000003 background notes, internal/model/abac_policy.go (TenantID field indexed twice), story acceptance criteria
- **Reason:** QA must validate that tenant isolation is enforced at repository layer (not DB constraints in Phase 1). Test scenarios should include multi-tenant queries to ensure filters work correctly.

### Fact 4: Test Against Live Service, Not Direct SQL
- **Fact:** ABAC QA tests must run against the live service via `psql` CLI, not direct SQL scripts. This validates the full startup sequence including migration runner execution and idempotence tracking. Tests are numbered TC-001 through TC-00X and documented in ST-XXXXXX_Test_Scenarios.md.
- **Source:** ST-000003 QA testing session (2026-04-16), successful integration tests
- **Reason:** Direct SQL tests miss startup integration bugs. Testing live service ensures migrations run before Casbin init, migration_applied tracking works, and idempotence is preserved across restarts.

### Fact 5: ABAC Index Count and Composition
- **Fact:** ABAC creates exactly 2 composite indexes on abac_policy table: idx_tenant_resource(tenant_id, resource) and idx_tenant_effect(tenant_id, effect). Plus 1 on audit: idx_policy_created(policy_id, created_at). All use tenant_id as first key to support multi-tenant queries.
- **Source:** ST-000003 migration SQL, TC-007 verification
- **Reason:** QA regression tests must verify index count (expect 2 on policy table, 1 on audit) to catch schema regressions. Composite design prioritizes tenant_id filtering.

### Fact 6: Unique Constraint (tenant_id, name) Allows Cross-Tenant Reuse
- **Fact:** ABAC unique constraint uq_tenant_policy_name is composite (tenant_id, name), not name-only. Same policy name can exist across tenants; duplicates only fail within same tenant. Test both cases: duplicate (tenant, name) fails; same name different tenant succeeds.
- **Source:** ST-000003 TC-004 verification
- **Reason:** Enables multi-tenant isolation while preventing policy name collisions. QA must verify constraint in both success and failure scenarios for regression.

### Fact 7: Integration Tests Required — Never Defer Without Running
- **Fact:** When story AC explicitly lists integration tests, QA must run them against real PostgreSQL before ticking AC checkboxes. TL saying "QA will track integration tests separately" means QA must execute them, not skip them. Use SQL test scripts in `tests/feature/.../scripts/` per Testing Guidelines.
- **Source:** ST-000007 QA session (2026-04-20), TL Thread 8 comment, user feedback
- **Reason:** Unit tests with sqlmock only verify query patterns, not actual database behavior (constraints, indexes, cascades, data persistence). Integration tests catch real-world issues that mocks cannot. QA should never mark integration test AC as passed based on unit test coverage alone.

### Fact 9: Soft-Delete Unique Constraint Includes Deleted Rows
- **Fact:** The `uq_tenant_policy_name` unique constraint on `abac_policy` covers soft-deleted rows (deleted_at IS NOT NULL). Re-creating a policy with the same (tenant_id, name) after soft-deleting it fails with POLICY_NAME_CONFLICT. QA must hard-delete test policies from the DB (or use unique names per test run) when cleaning up between runs.
- **Source:** ST-000022 QA session (2026-05-15), name conflict during second test run after soft-delete from first run
- **Reason:** Test scripts that create then delete (soft) a policy will block re-runs under the same name. Use `DELETE FROM abac_policy WHERE id = '...'` to hard-delete stale test data, or ensure test policy names are unique per test execution.

### Fact 10: Attribute Templates Endpoint Uses ABAC_TEMPLATES_CONFIG Env Var
- **Fact:** `GET /api/v1/abac/templates` reads config from the path in `ABAC_TEMPLATES_CONFIG` env var. When unset, it returns `{"namespaces":[]}` without error. The sandbox docker-compose does not set this var, so the live sandbox always returns empty namespaces. The config-present path is covered by unit tests only.
- **Source:** ST-000023 QA session (2026-05-15), internal/config/config.go line 44, service/abac_template_loader.go
- **Reason:** QA testing this endpoint in the sandbox will always see `{"namespaces":[]}`. To test config-present path against a live service, `ABAC_TEMPLATES_CONFIG=configs/abac_attribute_templates.yaml` must be passed to the container.

### Fact 11: CasbinEvaluator r.env Namespace Not Reachable via HTTP API
- **Fact:** The `r.env.*` namespace in casbin expressions works at the unit test level (direct flat key injection like `{"ip": "127.0.0.1"}`) but is not reachable via the HTTP API. The HTTP API always flattens attributes as `namespace.key` strings (e.g., `{"network": {"ip": "127.0.0.1"}}` → `"network.ip": "127.0.0.1"`). `buildCasbinParams` stores these as string keys with dots in the `env` map (e.g., `env["network.ip"]`), but govaluate ACCESSOR descent for `r.env.network.ip` expects nested map levels, not a single dotted string key. QA should test r.env coverage via unit tests, not HTTP integration tests.
- **Source:** ST-000025 QA session (2026-05-19), TC-009 investigation
- **Reason:** Saves time on future integration test design for casbin r.env expressions.

### Fact 12: Casbin Expression Test Scripts Need RUN_ID Suffix on Policy Names
- **Fact:** Integration test scripts for casbin policies must append a unique run timestamp to policy names (e.g., `$RUN_ID=$(date +%s)`, then `"name": "TC-001-policy-$RUN_ID"`) to avoid POLICY_NAME_CONFLICT 409 on re-runs. Applies even to policies that return 400 (validation errors) because the soft-delete unique constraint (see Fact 9) blocks re-use of names regardless of whether the policy was created successfully.
- **Source:** ST-000025 QA session (2026-05-19), 409 failures on second script run
- **Reason:** Prevents test failures from name conflicts across multiple test runs.

### Fact 13: govaluate LOGICALOP Token Count for Casbin Condition Limits
- **Fact:** For `format=casbin` policies, the conditions-per-rule limit (≤11) cannot be enforced via the shared `ValidateConditionNode` helper (which only processes ConditionNode trees). The correct implementation is to count `govaluate.LOGICALOP` tokens in `validateCasbinTokens` — each logical operator (`&&`, `||`) separates two conditions, so `count(LOGICALOP) + 1` approximates the number of conditions. Reject when `count(LOGICALOP) >= MaxTotalConditions`.
- **Source:** ST-000025 QA session (2026-05-19), F-001 finding, AC-4 gap investigation
- **Reason:** Documents the expected fix approach for the Developer when AC-4 is addressed for casbin format.

### Fact 8: Sandbox Uses Basic Auth; jq Now Available via WinGet
- **Fact:** The sandbox environment (docker/sandbox/docker-compose.yml) uses OIDC_ENABLED=false with HTTP Basic Auth. Credentials are admin:admin (from docker/sandbox/.env). `jq` is now installed via WinGet (at `C:/Users/Admin/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe/jq`) and available in Git Bash. Test scripts that use Bearer token auth will fail — all scripts must use `-u admin:admin` for Basic Auth when OIDC is disabled.
- **Source:** ST-000021 QA session (2026-05-15), ST-000020 test script pattern, second re-run 2026-05-15
- **Reason:** Scripts using `Authorization: Bearer dev-token` receive 401 from the sandbox ("invalid JWT format"). Basic Auth with -u admin:admin and tenantId header is the correct pattern. jq is now available so no need for PowerShell fallback.

### Fact 14: Newman 6.x Environment Variables Override Collection Variables
- **Fact:** In Newman 6.x, environment-scoped variables take precedence over collection variables during template resolution. If a Newman environment file defines a key (even with empty value), `pm.collectionVariables.set('key', value)` in a test script will not override it — `{{key}}` still resolves to the environment file's value. To store runtime values (e.g., tokens from a token acquisition request) for use in subsequent requests, use `pm.environment.set('key', value)` not `pm.collectionVariables.set()`.
- **Source:** ST-000031 QA validation run (2026-05-25), ABAC_RBAC_Collection.json bug investigation
- **Reason:** Token injection in ABAC_RBAC_Collection.json failed because sandbox-keycloak.json defined rbac_user_token and abac_user_token as empty environment variables. pm.collectionVariables.set() set the collection variable but Newman resolved the empty environment value, causing all Bearer token requests to fail with "invalid Authorization header format".

### Fact 15: Keycloak Sandbox Regression Suite Must Use Base Sandbox, Not Keycloak Overlay
- **Fact:** The Basic Auth regression suite (npm run test:ci, ABAC_Collection.json) must be run against the base sandbox without the Keycloak overlay. Running it against the Keycloak profile (OIDC_ENABLED=true) produces blanket 401s for all authenticated requests because Basic Auth is rejected in OIDC mode. This is expected behavior, not a regression.
- **Source:** ST-000031 QA validation run (2026-05-25)
- **Reason:** Prevents false regression failures when running the full automation suite in Keycloak context. The two suites target different auth modes and must run against their respective sandboxes.

### Fact 17: Casbin Enforcer Requires Service Restart to Pick Up Seed Data Applied After Service Start
- **Fact:** When the Keycloak (or base) sandbox starts, the `casbin-seed` init container inserts rows into `casbin_rule` AFTER the authorization service has initialized. The Casbin enforcer loads rules from DB at startup and does not poll for changes. Newly seeded rules are NOT visible to the live service until it is restarted (`docker restart fun-authorization-sandbox-authorization-service-1`). Run the restart and wait for `healthy` before running any RBAC-dependent test.
- **Source:** ST-000031 hotfix session (2026-05-25); RBAC deny on TC-R01 resolved by service restart.
- **Reason:** Prevents false RBAC denials when testing after a fresh sandbox bring-up. Always restart the auth service after casbin-seed completes if the service started before seed finished.

### Fact 16: docker/sandbox/.env REDIS_URL Must Be Empty for Base Sandbox
- **Fact:** docker/sandbox/.env is gitignored and may contain REDIS_URL=redis://redis:6379/0 from prior sessions. When REDIS_URL is set but the redis service is not started (no --profile redis), the authorization-service crashes at startup with "failed to initialize policy cache: Redis PING failed: dial tcp: lookup redis". Fix by setting REDIS_URL= (empty) in docker/sandbox/.env.
- **Source:** ST-000031 QA validation run (2026-05-25), base sandbox startup failure
- **Reason:** Quick diagnosis path when the service container exits with Redis DNS error. Check .env first.

