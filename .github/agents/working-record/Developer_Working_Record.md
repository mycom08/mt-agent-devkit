# Developer Working Record - ABAC Feature

This document tracks the Developer's progress on the ABAC (Attribute-Based Access Control) feature implementation. It records completed tasks, code changes, current work, and impediments across rolling 3-day windows.

---

## 2026-05-14 (Today)

### Completed
- ✅ **ST-000020 IN REVIEW** — Branch `st-000020/spec-first-code-generation` from `feature/abac-phase-2`. Installed oapi-codegen v2.7.0 as Go tool; added `x-go-type: json.RawMessage` to all 4 `rule_data` spec fields; generated `internal/dto/abac_policy_gen.go`; migrated handler/tests to generated types; added `spectral-lint.yml` and `codegen-drift.yml` CI workflows; `.spectral.yaml` ruleset. 55/55 tests pass; `go vet` clean; drift check idempotent. PR #70 → `feature/abac-phase-2`. Issue #65 → `status:review`.
- ✅ **ST-000020 spectral-lint CI fix** — Fixed 4 `no-$ref-siblings` errors in `docs/api/ABAC_API.yaml` by wrapping each `rule_data` `$ref` in `allOf`; added `operationId` to all 8 operations and `info.contact` to resolve 9 warning-level violations (CI uses `--fail-severity warn`). Regenerated `internal/dto/abac_policy_gen.go` — type alias names updated, no call-site changes. Commit c8796a1 pushed. Both CI workflows now pass (spectral-lint and codegen-drift).
- ✅ **ST-000020 developer guide comment** — Posted developer guide for updating the API spec as a comment on GitHub Issue #20 (https://github.com/lhtuwrk/authorization-service/issues/20#issuecomment-4449322035). Covers lint, codegen, handler fixes, spec rules, and CI checks.
- ✅ **ST-000020 README update** — Added "API Spec & Code Generation" section to `README.md` (after Testing, before Contributing). Commit 6df372f pushed to `st-000020/spec-first-code-generation`.

### In Progress
- None.

### Impediments
- None.

### Sprint Status
| Story | Status |
|---|---|
| ST-000003 – ST-000019 | ✅ DONE — Issues closed |
| ST-000020 | 🔍 IN REVIEW — PR #70 awaiting TL review |
| ST-000021 – ST-000023 | 📋 BACKLOG — Phase 2, not yet started |

---

## 2026-05-13

### Completed
- ✅ **ST-000019 IN REVIEW** — Branch `st-000019/api-contract-cleanup` from `feature/abac-phase-2`. Fixes 4 API/schema deviations: G1 DELETE → 204, G2 `enabled` field in CreatePolicy, G3 `resource` immutability on UpdatePolicy, G4 audit indexes migration. 4 new unit tests; all tests pass; go vet clean. PR #69 created → `feature/abac-phase-2`.
- ✅ **ST-000019 G2 hotfix** — Removed `default:true` GORM tag from `model.ABACPolicy.Enabled`; GORM v2 was skipping the zero-value `false` and letting DB apply DEFAULT. Fix commit af5c9e3 pushed. Integration-tested live: POST `{enabled:false}` now persists correctly; omitted `enabled` still defaults to true.
- ✅ **ST-000019 DONE** — QA Thread 7 signed off all 4 ACs (55/55 tests PASS on af5c9e3). PO Thread 8 accepted. PR #69 squash-merged → `feature/abac-phase-2`. Issue #64 closed `status:done`.
- ✅ **GitHub sync** — Confirmed ST-000019 closed. ST-000020–ST-000023 all `status:backlog`. No stories in `status:ready` or `status:in-progress`.

### In Progress
- None.

### Impediments
- None.

---

## 2026-05-11

### Completed
- ✅ **Synced master** — Pulled `feature/abac` merge (commit c63f3f1); master now contains all ABAC Phase 1 work.
- ✅ **ST-000018 initial implementation** — Branch `ST-000018/health-check-endpoint` from master. `internal/api/health_handler.go`, `internal/api/health_handler_test.go` (5 tests), `cmd/server/main.go` wiring, `README.md` K8s probe docs. Commit d6cbd75. PR #62 created → master.
- ✅ **ST-000018 CR-1 fixed** — Extracted `casbinChecker` interface; changed `HealthHandler.casbin` from concrete `*casbinpkg.Provider` to interface; added typed-nil guard in constructor; added `mockCasbinChecker` in tests; rewrote `TestReadiness_AllHealthy_Returns200` with non-nil enforcer mock and `rr.Code == 200` assertion; updated `TestReadiness_CasbinNil_Returns503` to use `mockCasbinChecker{enforcer: nil}`. All 5 tests PASS. Commit 194a6c0, pushed to PR #62.

- ✅ **ST-000018 DONE** — Sandbox healthcheck updated to `/healthz/live` (commit 3ac81fa). PR #62 squash-merged into master (TL approved 194a6c0, QA all 6 ACs pass). Issue #58 moved to `status:done`.

### In Progress
- None

### Impediments
- None

### Sprint Status
| Story | Status |
|---|---|
| ST-000003 – ST-000017 | ✅ DONE — Issues closed |
| ST-000018 | ✅ DONE — PR #62 merged → master |

---

## 2026-05-07

### Completed
- ✅ **Working record corrected** — Synced story statuses with GitHub; ST-000006 through ST-000016 (all except ST-000015) confirmed closed/done.
- ✅ **ST-000015 PR #50 merged** — Squash-merged into `feature/abac` (branch deleted).
- ✅ **ST-000015 FIND-LIST-01 fix** — Corrected `ABAC_API.yaml` and `ABAC_Postman_Collection.json`: replaced paginated `PolicyListResponse` with flat array schema; removed `Page`/`PageSize` params. Commit 077fabb, PR #51 TL-approved and squash-merged into `feature/abac` (commit ceda8fc). Merge summary posted on issue #46 — PO unblocked to share handoff package.
- ✅ **ST-000017 DONE** — `http.MaxBytesReader` 64KB added to `CreatePolicy`/`UpdatePolicy`; 6 adversarial API tests (`abac_security_test.go`); 9 adversarial evaluator tests (`json_evaluator_security_test.go`); `Security_Review_Checklist.md` (all 6 checks PASS). TL approved + QA 35/35 tests PASS. PR #52 squash-merged (commit 9a8be8e), issue #47 closed.

### In Progress
- None

### Impediments
- None

---

## 2026-05-06

### Completed
- ✅ **ST-000013 merged** — PR #48 squash-merged into `feature/abac` (commit f6ff56c); issue #44 moved to testing.
- ✅ **ST-000014 DONE** — Implemented ABAC_Developer_Guide.md, corrected ABAC_Database_Schema.md, created ABAC_Troubleshooting_Guide.md and ABAC_Deployment_Runbook.md. TL CR-1–CR-4 resolved (commit 44dd0d7). PR #49 merged (commit 94ad251); issue #45 moved to testing.
- ✅ **ST-000015 DONE** — Delivered: `Dockerfile`, `docker-compose.frontend-sandbox.yml`, `scripts/docker/sandbox-seed.sql`, `docs/api/ABAC_Postman_Collection.json`, `docs/feature/.../ABAC_Frontend_Integration_Guide.md`. PR #50 created; handoff summary posted on issue #46.

### In Progress
- None

### Impediments
- None

---

## 2026-05-05

### Completed
- ✅ **ST-000013 DONE** — Implemented `internal/service/abac_policy_cache.go` (TTL + RWMutex); wired cache into ABACService; cache-first `getPoliciesForEvaluation` + active eviction on mutation. 3 benchmarks (CacheHit ~11.7µs, CacheMiss ~16.2µs, WarmCache ~13.0µs) all under 10ms P99. 7 new unit tests; all tests pass; go vet clean. Performance report at `docs/.../test/ST-000013_Performance_Report.md`. PR #48 created → `feature/abac`.

### In Progress
- None

### Impediments
- None

---

## Format Guidelines

**Completed:** One concise bullet per story — include key files, PR number, and outcome. No step-by-step sub-items.
- Example: "**ST-000009 DONE** — Implemented 4 CRUD handlers in `internal/api/abac_api.go`, added DI wiring in `main.go`, 19 unit tests pass. TL CR fixed in commit b466558. PR #38 merged → `feature/abac`."

**In Progress:** Current story being worked, or stories awaiting review/QA.
- Example: "ST-000013 PR #48 awaiting TL review."

**Impediments:** Blockers affecting developer work.
- Example: "ST-000017 blocked — awaiting TL answer on Thread 2 (rule_data size limit)."
