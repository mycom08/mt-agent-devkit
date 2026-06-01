# Tech Lead Work Log

---


### 2026-05-24 | OIDC Phase 2 Issue Creation | N/A (no PR reviewed)
**PR:** N/A | **CI:** N/A
Created 11 GitHub issues from plan-oidc-phase2-agile-scrum-roadmap.md: milestone "Phase 2 - Multi-IdP & Rate Limiting" (#3), Epics E6 (#101) and E7 (#102), and user stories US-18 through US-26 (#103-#111) across Sprints 8 and 9. No duplicates found; all issues are net-new.
### 2026-05-16 | #22 Service API Key Repository | Approved for QA (Round 2)
**PR:** [#78](https://github.com/lhtuwrk/authorization-service/pull/78) | **CI:** pass
All 4 Round-1 blocking items verified fixed: down migration added, context.Context on all 5 methods with WithContext, Delete+UpdateLastUsed RowsAffected==0 not-found errors, 2 new NotFound tests. 15 tests green.

### 2026-05-16 | #23 Service API key service and management endpoints | Revision R1
**PR:** [#80](https://github.com/lhtuwrk/authorization-service/pull/80) | **CI:** pass
One blocking correctness bug: `revokeServiceKey` returns HTTP 500 for all errors from `Revoke`, including the not-found case which should be 404. The error chain loses type information — the repository returns a plain `fmt.Errorf` for missing keys, the service re-wraps it, and the handler hardcodes `http.StatusInternalServerError`. Fix requires the service to return a typed `NotFoundError` on not-found, the handler to use the existing `writeError` helper, and the test to add a 404 assertion. All other aspects (crypto/rand key generation, SHA-256, sak_ prefix, plaintext-once guarantee, interface refactor, test coverage for the other three methods) are correct and well-implemented.

### 2026-05-16 | #23 Service API key service and management endpoints | Approved (Round 2)
**PR:** [#80](https://github.com/lhtuwrk/authorization-service/pull/80) | **CI:** pass
R1 blocking issue fully resolved: service.Revoke now returns *NotFoundError on not-found (via strings.Contains detection), revokeServiceKey uses writeError for correct 404 dispatch, and two new tests cover both layers. All 8 acceptance criteria verified; 21 tests green; no security issues in new code (pre-existing empty AdminApiKey bypass noted as non-blocking observation).

### 2026-05-16 | #23 Service API key service and management endpoints | Merged
**PR:** [#80](https://github.com/lhtuwrk/authorization-service/pull/80) | **CI:** pass
QA returned a full pass (43 tests, 0 failures; all 8 acceptance criteria verified). CI checks green (build + GitGuardian). PR squash-merged to lhtu/OIDC_enhancement, issue #23 closed with label updated to `done`.

### 2026-05-16 | #24 ServiceApiKeyAuth middleware | Revision R1
**PR:** [#81](https://github.com/lhtuwrk/authorization-service/pull/81) | **CI:** pass
Two blocking issues found. (1) `ServiceApiKeyAuth` accesses `m.apiKeySvc` without a nil guard -- misconfiguration causes a nil-deref panic instead of a controlled error response. (2) In SaaS mode, `RegisterAuthenticatedRoutes` re-registers `POST /api/resources` and `POST /api/resources/list` under the `Authenticated` Bearer group, making them unreachable dead code (Chi first-match wins) and a future maintenance trap; fix requires extracting a `RegisterReadOnlyRoutes` method. One non-blocking note: `UpdateLastUsed` does a second `FindByHash` round-trip that could be eliminated by returning the key ID from `ValidateKey` in a future ticket.

### 2026-05-16 | #24 ServiceApiKeyAuth middleware | Approved for QA (Round 2)
**PR:** [#81](https://github.com/lhtuwrk/authorization-service/pull/81) | **CI:** pass
Both R1 blocking issues correctly resolved: nil guard added at the top of ServiceApiKeyAuth (returns 500 on misconfiguration), and RegisterReadOnlyRoutes extracted so the SaaS Bearer group no longer re-registers the two POST management routes. All 6 acceptance criteria met; 10 new unit tests (7 middleware, 3 service) are meaningful and pass. SaaS/selfhost mutual exclusion enforced via if/else in main.go. No issues found in R2.

### 2026-05-18 | #24 ServiceApiKeyAuth middleware | Merged
**PR:** [#81](https://github.com/lhtuwrk/authorization-service/pull/81) | **CI:** pass
QA returned a full pass (413 tests, 0 failures; 100% statement coverage on ServiceApiKeyAuth; all acceptance criteria verified). CI checks green (build + GitGuardian). PR squash-merged to lhtu/OIDC_enhancement, issue #24 closed with label updated to `done`.

### 2026-05-18 | #25 Mode-aware server bootstrap | Revision R1
**PR:** [#85](https://github.com/lhtuwrk/authorization-service/pull/85) | **CI:** fail (GitGuardian)
One blocking security issue: `internal/config/config.go` line 47 — the `POSTGRES_PASSWORD` default was changed from `"postgres"` to `"tu0764"`, committing what appears to be a real developer password. GitGuardian flagged it (incident #29316528) and the security check is failing. All other changes (mode-aware bootstrap, `config.Validate()`, route helpers, tests) are correct and cover all 14 acceptance criteria. Sending back for credential removal only.

### 2026-05-18 | #25 Mode-aware server bootstrap | Revision R2
**PR:** [#85](https://github.com/lhtuwrk/authorization-service/pull/85) | **CI:** fail (GitGuardian)
The R1 fix correctly reverted `POSTGRES_PASSWORD` to `"postgres"` in the live code at commit `c3a78fdb`. However, GitGuardian continues to fail because it scans all commits in the PR diff: incident #29316528 is re-triggered by the original commit `c177c28` (still in branch history), and a new incident #30457631 was opened against the fix commit (likely a false positive). The build check passes; the code is clean at the tip. Developer must either squash the two PR commits (rebase/force-push) to eliminate the offending commit from the diff, or dismiss both incidents in the GitGuardian dashboard. No additional code changes are needed.

### 2026-05-18 | #25 Mode-aware server bootstrap | Approved for QA (Round 3)
**PR:** [#85](https://github.com/lhtuwrk/authorization-service/pull/85) | **CI:** pass
Developer squashed the branch into a single clean commit (7cfd3a9) eliminating the credential from the PR diff; GitGuardian re-scanned and returned success. Build also green. All 14 acceptance criteria verified in code: selfhost/SaaS route separation, ValidatorCache wiring, ServiceApiKeyService wiring, config.Validate() fail-fast with 9-case table-driven tests, admin routes absent in selfhost. No security, correctness, or quality issues in the current diff. Handed off to QA.

### 2026-05-18 | #25 Mode-aware server bootstrap | Merged
**PR:** [#85](https://github.com/lhtuwrk/authorization-service/pull/85) | **CI:** pass
QA returned a full pass. CI checks green (build passing). PR squash-merged to master, branch deleted, issue #25 closed with label updated to `done`. PR went through 3 revision rounds: R1 blocked on exposed credential, R2 blocked on GitGuardian re-trigger from historical commit, R3 approved after developer squash-forced the branch to remove the offending commit from the diff.

### 2026-05-19 | Phase 1 Cumulative PR (#11-#25) | Revision R1
**PR:** [#79](https://github.com/lhtuwrk/authorization-service/pull/79) | **CI:** fail (GitGuardian)
GitGuardian Security Check is failing because two historical commits in the 28-commit PR diff contain hardcoded "postgres" defaults: commit 8ffdeed (POSTGRES_PASSWORD default in config.go and :-postgres inline fallbacks in docker-compose.yml) and commit 833a6d1 (SANDBOX_POSTGRES_PASSWORD=postgres in .env.example). The current HEAD is clean; fix requires squashing both commits out of the diff (same resolution as PR #85) and changing .env.example to use a non-sensitive placeholder. One non-blocking scope-gap noted: JWT aud claim is not validated (out of Phase 1 scope). All 15 Go stories are fully implemented and correct; build CI is green.

### 2026-05-21 | #79 Phase 1 OIDC Enhancement (#11-#25) | Approved R2
**PR:** [#79](https://github.com/lhtuwrk/authorization-service/pull/79) | **CI:** pass
Round 2 full Phase B review completed. GitGuardian and Go build both green; all 9 test packages pass with zero failures. No blocking issues found: all 15 stories implemented correctly, no hardcoded credentials, JWT validator rejects HMAC/none via explicit RSA/ECDSA allow-list, ServiceApiKey stored as SHA-256 hex, config.Validate() fails fast, admin routes absent in selfhost. Two non-blocking observations logged (timing-safe admin key comparison, JWT aud validation) recommended for Phase 2 hardening tickets. PR approved and handed off to QA.

### 2026-05-22 | #11-#25 Phase 1 OIDC Enhancement | Merged
**PR:** [#79](https://github.com/lhtuwrk/authorization-service/pull/79) | **CI:** pass
QA returned a full pass (442 tests, 0 failures across all 15 Phase 1 stories). All CI checks green (GitGuardian, build, verify) at commit f8d274c. PR squash-merged to master (merge commit a82ea255), branch lhtu/OIDC_enhancement deleted. Issues #11-#25 confirmed closed and all labelled `done`. Phase 1 of the OIDC decoupling roadmap complete.

### 2026-05-24 | OIDC Phase 2 Sprint Label Renumber | N/A (no PR reviewed)
**PR:** N/A | **CI:** N/A
Renamed sprint labels on all 9 Phase 2 issues: #103–#107 changed from sprint-8 to sprint-7; #108–#111 changed from sprint-9 to sprint-8. Updated milestone 3 description from "Sprints 8–9" to "Sprints 7–8". Updated plan file ai/claude/plans/plan-oidc-phase2-agile-scrum-roadmap.md — replaced "Sprint 8" heading and all body references with "Sprint 7", and "Sprint 9" with "Sprint 8". No new label creation required (sprint-7 and sprint-8 already existed).
