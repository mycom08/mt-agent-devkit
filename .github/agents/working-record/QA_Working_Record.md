## QA Working Record

### 2026-05-14 (ST-000020) — Spec-First Code Generation (oapi-codegen)
**Completed:**
- Read QA_Rules.md, PROJECT_PRIMING.md, STORY_STANDARD.md, QA_Working_Record.md (mandatory docs)
- Synced ST-000019 status: PR #69 merged into feature/abac-phase-2 at commit 482b313 (confirmed via git log)
- Reviewed ST-000020 — GitHub Issue #65, PR #70, merged at commit 482b313 (feature/abac-phase-2)
- Read all 6 issue comments — Thread 1 (Dev + TL + PO resolved Q1-Q5), Thread 2 (Dev PR ready, TL APPROVED), Developer Guide comment
- Build: `go build ./...` clean; `go vet ./...` clean
- Unit tests: 55/55 PASS (`internal/api`), all packages PASS
- Static AC verification: go.mod tool directive, generate.go directive, oapi_codegen_config.yaml, x-go-type in 4 spec locations, generated types in abac_policy_gen.go, old DTOs removed, CI workflows confirmed
- `go generate ./...`: exit code 0; `git diff --exit-code abac_policy_gen.go`: exit code 0 (no drift)
- CI on PR #70: Spectral lint PASS, codegen drift PASS, GitGuardian PASS
- Created test scenarios doc: `docs/feature/Attribute_Based_Access_Control-ABAC/test-scenarios/ST-000020_Test_Scenarios.md`
- Created API test script: `tests/feature/Attribute_Based_Access_Control-ABAC/scripts/ST-000020_API_Test.sh`
- Live API tests: 8/8 PASS (TC-G3-06 through TC-EXTRA-02)
- QA sign-off posted to Issue #65 (Thread 3, comment #4449690862)

**In Progress:** None

**Impediments:**
- Story label is still `status:review` (from TL approval state). PO must tick all 5 AC checkboxes then label should move to `status:done`.

---

### 2026-05-13 (ST-000019) — Phase 2 Clean-up: API Contract & Schema Alignment
**Completed:**
- ✅ Read QA_Rules.md, PROJECT_PRIMING.md, STORY_STANDARD.md, QA_Working_Record.md (mandatory docs)
- ✅ Synced ST-000018 status: Issue #58 CLOSED, label `status:done` — prior impediment resolved
- ✅ Reviewed ST-000019 (Phase 2 Clean-up) — GitHub Issue #64, PR #69, branch `st-000019/api-contract-cleanup`
- ✅ Build: `go build ./...` clean; `go vet ./...` clean
- ✅ Unit tests: **55/55 PASS** (`internal/api`), all packages pass
- ✅ Created test scenarios doc: `docs/feature/Attribute_Based_Access_Control-ABAC/test-scenarios/ST-000019_Test_Scenarios.md`
- ✅ Created API test script: `tests/feature/Attribute_Based_Access_Control-ABAC/scripts/ST-000019_API_Test.sh`
- ✅ Live API tests Session 1 (HEAD e5ac1ab) — G1 ✅, G2 ❌ (GORM `default:true` defect), G3 ✅, G4 ✅
- ✅ QA Thread 6 posted to Issue #64 with G2 defect + root cause
- ✅ Dev fixed G2 in commit `af5c9e3` — removed `default:true` from `model.ABACPolicy.Enabled` GORM tag
- ✅ Live API tests Session 2 (HEAD af5c9e3) — **ALL PASS** including TC-G2-01b GET DB persistence confirmed
- ✅ All 4 AC checkboxes ticked on Issue #64 (G1, G2, G3, G4)
- ✅ QA sign-off posted to Issue #64 (Thread 7, comment #4437269801)
- ✅ Test scenarios doc updated with live results + final status

**In Progress:** None

**Impediments:**
- PR #69 not yet merged; label still `status:testing`. Dev must merge to `feature/abac-phase-2` and move label to `status:done`. QA notified Dev in sign-off comment (Thread 7).

---

### 2026-05-11 (ST-000018) — Health Check Endpoint
**Completed:**
- ✅ Read QA_Rules.md, PROJECT_PRIMING.md, STORY_STANDARD.md, QA_Working_Record.md (mandatory docs)
- ✅ Verified ST-000017 impediment resolved: Issue #47 closed with `status:done`
- ✅ Reviewed ST-000018 (Health Check Endpoint) — GitHub Issue #58, PR #62, branch `ST-000018/health-check-endpoint` commit `194a6c0`
- ✅ Read all 7 issue comments — Thread 1 resolved (self-implement, no caching); TL approved PR #62 after CR-1 fix (casbinChecker interface)
- ✅ Created test scenarios doc: `docs/feature/Infrastructure/test-scenarios/ST-000018_Test_Scenarios.md` (17 TCs across 6 ACs + edge + regression)
- ✅ Created API test script: `tests/feature/Infrastructure/scripts/ST-000018_API_Test.sh`
- ✅ Unit tests: **5/5 PASS** (`internal/api`) — TestLiveness_AlwaysReturns200, TestReadiness_AllHealthy_Returns200, TestReadiness_DBPingFails_Returns503, TestReadiness_CasbinNil_Returns503, TestReadiness_BothFail_Returns503
- ✅ Full regression suite: all packages PASS, `go vet ./...` clean
- ✅ Live API tests (OIDC_ENABLED=false, abac_test_db): 8/8 assertions PASS — HTTP 200 for both endpoints, omitempty on live, 405 wrong method, 401 regression
- ✅ Static: README Health Checks section with correct K8s probe YAML (AC-6) ✅; routes before /api group (AC-3) ✅
- ✅ All 6 AC checkboxes ticked on Issue #58
- ✅ QA sign-off posted to Issue #58 (comment #4419409996)

**In Progress:** None

**Impediments:**
- PR #62 not yet merged; label still `status:in-progress`. Dev must merge and move to `status:done`. QA notified Dev in sign-off comment.

