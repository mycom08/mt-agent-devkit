# Developer_Memory

> **READ THIS FILE** at the start of every session, immediately after reading `Developer_Working_Record.md` and before starting any story work. Facts here are durable conventions that override default assumptions.

## Stored Facts

### Fact 1
- **Fact:** When an OpenAPI field must keep symbolic operator wire values such as `==` or `<=`, model it as `type: string` with a validating `pattern` and examples instead of a literal enum.
- **Source:** PROJECT_PRIMING.md section 4.2 API Spec Standard
- **Reason:** Keeps ABAC API contracts Swagger Editor compatible while preserving wire format.

### Fact 2
- **Fact:** Story questions go directly in the story's `## Comment` section (Jira-like), not separate review files.
- **Source:** PROJECT_PRIMING.md section 13 (Story Collaboration Workflow)
- **Reason:** All story-level discussion stays in one place for traceability and team visibility.

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

### Fact 12
- **Fact:** `go get -tool <pkg>@<version>` registers a package as a `tool` directive in `go.mod` (Go 1.24+), making it accessible via `go tool <name>`. This is the correct way to install dev tools like `oapi-codegen` — not `go get` alone.
- **Source:** ST-000020 implementation
- **Reason:** `go get` without `-tool` adds the dep to `go.mod` but does not register it as a tool; `go tool oapi-codegen` only works after `-tool`.

### Fact 13
- **Fact:** When running `oapi-codegen` via `//go:generate`, the config's `output` path and spec path are relative to the package directory (where `generate.go` lives), not the repo root. Set `output: abac_policy_gen.go` (filename only) in the config; use `../../docs/api/ABAC_API.yaml` for the spec path.
- **Source:** ST-000020 implementation (misplaced generated file debugging)
- **Reason:** `go generate ./...` runs each `//go:generate` command with cwd set to the package dir. An `output: internal/dto/abac_policy_gen.go` in the config would create `internal/dto/internal/dto/abac_policy_gen.go`.

### Fact 14
- **Fact:** `x-go-type: json.RawMessage` on a spec field overrides the generated Go type. Do NOT use `x-go-type-import` alongside it for `encoding/json` — oapi-codegen already imports `encoding/json` when it generates union types, causing a duplicate import.
- **Source:** ST-000020 spec update
- **Reason:** Duplicate import (`"encoding/json"` and `json "encoding/json"`) breaks compilation.

### Fact 11
- **Fact:** When addressing a TL code review (CR), exercise judgment — do not just execute the suggestions blindly. Cross-check the CR against the full handler logic, identify any gaps the TL may not have explicitly listed, and raise questions on the PR before pushing the fix.
- **Source:** ST-000018 CR-1 review session (2026-05-11)
- **Reason:** The TL's CR redirected `TestReadiness_CasbinNil_Returns503` to test "enforcer nil" but left the "nil-interface casbin" readiness path untested. A developer who only executes without thinking would miss this gap. Raising it proactively is part of the developer's responsibility.