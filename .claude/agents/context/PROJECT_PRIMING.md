# authorization-service - Priming Context

> This is a cheat sheet for AI agents — the minimum context needed to understand the project, architecture, and team workflow. It is not comprehensive documentation.

## 1. Project Overview

**authorization-service** is a lightweight, centralized REST-based authorization service built with Go. It provides resource-level access control across multiple tenants or services using **Casbin RBAC** as the policy engine.

**Purpose:** Single source of truth for who can do what on which resources. Teams register resources here, define role-based policies, and query access decisions via REST API.

**Status:** ✅ RBAC fully implemented | 🔄 Next: ABAC expansion

**Key traits:** Multi-tenant, runtime policy management, PostgreSQL-backed, JWT/OIDC secured, centralized.

---

## 2. Glossary

| Term | Definition |
|------|-----------|
| PO | Product Owner — owns stories, defines AC, ticks checkboxes after QA confirms |
| TL | Technical Lead — owns architecture, reviews and approves PRs |
| Dev | Developer — implements stories, writes PRs |
| QA | Quality Assurance — tests AC, reports results, notifies PO |
| BA | Business Analyst — aligns requirements, flags scope creep |
| AC | Acceptance Criteria |
| RBAC | Role-Based Access Control |
| ABAC | Attribute-Based Access Control |
| Policy | `(subject, domain, resource, action, effect)` rule |
| Domain | Tenant/workspace for multi-tenancy isolation |
| Resource | Named object being protected |
| Action | Operation on resource (read, write, delete) |
| JWT | Stateless bearer token with claims |
| OIDC | OpenID Connect authentication protocol |

---

## 3. Story Workflow

Stories are **GitHub Issues** in `lhtuwrk/authorization-service` (label: `feature:abac`, title format: `[ST-XXXXXX][FEATURE] Title`).

**Status flow:**

```
Backlog → Ready → In Progress → Review → Testing → Done
                                                     ↓ (if bug found after Done)
                                                  Hotfix → Review → Testing → Done
```

| Status | Who Moves It | When |
|--------|-------------|------|
| Backlog | PO | After story creation |
| Ready | PO | After assigning to Developer |
| In Progress | Developer | Dev branch created |
| Review | Developer | PR created, TL review requested |
| Testing | QA | After TL approval and merge |
| Done | QA + PO | After all AC verified and ticked by PO |

**Collaboration rules:**
- Story body contains only: User Story, AC, Deliverables
- All discussions happen as **comments** on the GitHub Issue — never in the body
- One topic per comment thread

For the full workflow (status transitions, role boundaries, AC rules, merge gate, comment format): `.claude/agents/rules/STORY_STANDARD.md`

---

## 4. Design First Before Implementation

For complex features, the team follows a design-first process before any code is written:

1. **Developer** drafts a design and posts it as a story comment for TL review, using this structure:
   - **Capabilities:** scope constraints
   - **Components:** infrastructure and architecture constraints
   - **Interactions:** integration and data flow patterns
   - **Contracts:** type and interface conventions
2. **TL** reviews and approves each level before the next begins
3. No code is written until contracts are agreed

**What this means for each role:**
- **PO / BA:** Expect a design review step before implementation starts on complex stories — factor this into timeline expectations
- **QA:** Test scenarios for complex stories should align with the agreed contracts, not be written before TL approval

---

## 5. Agent Working Records

**Location:** `.claude/agents/working-record/{Agent_Name}_Working_Record.md`

**Access control:** Read and update only your own record. Never read or modify another agent's record.

Update at **start of session** (read yesterday's context, sync story statuses from GitHub) and at **end of session** (log completed work, in-progress items, impediments). Keep 3 most recent days.

**Format:** Each day is recorded as a standup entry with:
- **Date:** YYYY-MM-DD
- **Completed:** What was done (list of tasks, features, bug fixes)
- **In Progress:** Current work and next priorities
- **Impediments:** Any blockers, questions, or dependencies (none if clear)

---

## 6. Internal Project Documents

Navigate here for feature context:

- **Feature docs root** — `docs/feature/`
- **Business requirements** — `docs/feature/Attribute_Based_Access_Control-ABAC/business/ABAC_Requirements_Summary.md`
- **Technical analysis** — `docs/feature/Attribute_Based_Access_Control-ABAC/technical/ABAC_Strategic_Analysis.md`
- **Implementation design** — `docs/feature/Attribute_Based_Access_Control-ABAC/technical/ABAC_Technical_Implementation.md`
- **Database schema** — `docs/feature/Attribute_Based_Access_Control-ABAC/technical/ABAC_Database_Schema.md`
- **Security checklist** — `docs/feature/Attribute_Based_Access_Control-ABAC/technical/Security_Review_Checklist.md`
- **Developer guide** — `docs/feature/Attribute_Based_Access_Control-ABAC/developer/ABAC_Developer_Guide.md`
- **Frontend integration guide** — `docs/feature/Attribute_Based_Access_Control-ABAC/developer/ABAC_Frontend_Integration_Guide.md`
- **Operations runbook** — `docs/feature/Attribute_Based_Access_Control-ABAC/operations/ABAC_Deployment_Runbook.md`
- **Troubleshooting guide** — `docs/feature/Attribute_Based_Access_Control-ABAC/operations/ABAC_Troubleshooting_Guide.md`
- **Roadmap** — `docs/feature/Attribute_Based_Access_Control-ABAC/plan/ABAC_Implementation_Roadmap.md`
- **Backlog** — `docs/feature/Attribute_Based_Access_Control-ABAC/plan/Product_Backlog.md`
- **Sprint Plan** — `docs/feature/Attribute_Based_Access_Control-ABAC/plan/Sprint_1_Overview.md`
- **API spec** — `docs/api/ABAC_API.yaml`
- **Test Scenarios** — `docs/feature/Attribute_Based_Access_Control-ABAC/test-scenarios/` (one file per story)
- **Test Scripts** — `tests/feature/Attribute_Based_Access_Control-ABAC/scripts/` (SQL and shell scripts)
- **Test Reports** — `tests/feature/Attribute_Based_Access_Control-ABAC/report/` (execution logs, performance reports)
- **Postman Collection** — `tests/feature/Attribute_Based_Access_Control-ABAC/postman/ABAC_Postman_Collection.json`
- **Wiki (project-wide guidelines)**
  - **Development Standards** — `docs/wiki/Development_Standards.md`
  - **Go Style Guide** — `docs/wiki/Go_Style_Guide.md`
  - **Code Review Checklist** — `docs/wiki/Code_Review_Checklist.md`
  - **Testing Guidelines** — `docs/wiki/Testing_Guidelines.md`

Name new or renamed documents in `Title_Case_With_Underscores`, for example `My_Technical_Document.md`.

---

## 7. Key Directories

| What | Path |
|------|------|
| Entry point | `cmd/server/main.go` |
| HTTP handlers | `internal/api/` |
| Business logic | `internal/service/` |
| Data access | `internal/repository/` |
| DB models | `internal/model/` |
| Request/response DTOs | `internal/dto/` |
| ABAC evaluation logic | `internal/evaluation/` |
| Casbin model config | `configs/casbin/model.conf` |
| DB migrations | `internal/db/migrations/` |
| Feature docs | `docs/feature/` |
| API spec | `docs/api/` |
| Wiki / guidelines | `docs/wiki/` |
| Test scenarios | `docs/feature/Attribute_Based_Access_Control-ABAC/test-scenarios/` |
| Test scripts & reports | `tests/feature/Attribute_Based_Access_Control-ABAC/` |
| Frontend sandbox | `docker/sandbox/` |

---

## 8. Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Go | 1.24+ |
| Router | Chi | v5.2.5 |
| Policy Engine | Casbin | v2.135.0 |
| Database | PostgreSQL | 14+ |
| ORM | GORM | v1.31.1 |
| DB Adapter | Casbin GORM Adapter | v3.24.0 |
| Auth | JWT (golang-jwt) | v5.3.1 |

---

## 9. API Standards

- Keep OpenAPI/Swagger specs **short, explicit, and tool-safe** (validate in Swagger Editor)
- Prefer word enums (`EQ`, `LTE`, `NOT_IN`) over special characters

---

## 10. Core API

| Method | Endpoint | Auth | Purpose |
|--------|----------|:----:|---------|
| POST | `/api/resources` | ✓ | Create resource |
| POST | `/api/resources/list` | ✓ | Bulk create |
| GET | `/api/resources` | ✓ | List or get policies (dispatch on `?resource=X`) |
| POST | `/api/resources/access/check` | ✗ | Check access (public) |
| GET | `/api/resources/{id}/policies` | ✓ | Get resource policies |
| POST/PUT/DELETE | `/api/resources/policies` | ✓ | Policy CRUD |
| GET | `/api/resources/actions` | ✓ | List actions |

**Auth:** `Authorization: Bearer <JWT_TOKEN>`

---

## 11. RBAC Model (Current)

**Model file:** `configs/casbin/model.conf`

Request `(sub, dom, obj, act)` is matched against policies `(sub, dom, obj, act, eft)`. Role membership via `g(user, role, domain)`. Access is granted if any matching policy has `eft=allow`.

**Limitations:**
- ❌ No attribute conditions (e.g., "if user.dept == Finance")
- ❌ No dynamic evaluation (time, IP, headers)

---

## 12. Architectural Patterns

**Layered:** API → Service (business logic) → Repository (data access) → Database

**DI:** Services receive dependencies via constructor; circular deps resolved post-construction

**Casbin singleton:** One enforcer per service, thread-safe, shared state

**Token context:** JWT claims extracted → `TokenContext` → passed via `r.Context()` throughout call chain

**Auth middleware:** `authMiddleware.Authenticated` applied to all `/api/*` routes

**Multi-tenancy:** Domain as first-class field in all policies; user domain from JWT `dom` claim

**Policy-resource sync:** Creating resources may update policies; policy updates validate against existing resources

**Config:** 12-factor env vars (POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, PORT, OIDC_ENABLED, AUTH_SERVER_URL, AUTH_CLIENT_ID, CASBIN_MODEL_PATH)

---

## 13. ABAC Current State

- Casbin matcher uses RBAC-specific `g()` function — no attribute evaluation yet
- Request shape: 4 fields `(sub, dom, obj, act)`; policy shape: 5-tuple `(sub, dom, obj, act, eft)`
- No attribute metadata schema in DB yet
- Custom evaluation layer scaffolded in `internal/evaluation/`

---

## 14. Local Sandbox Environment

The sandbox docker-compose is **never in the project root** — it always lives under `docker/sandbox/`:

| File | Path |
|------|------|
| Compose file | `docker/sandbox/docker-compose.yml` |
| Env overrides | `docker/sandbox/.env` (git-ignored; may not exist) |
| Seed data | `docker/sandbox/seed.sql`, `docker/sandbox/casbin_seed.sql` |

**Before making any API call or running any test script**, read these two files to determine the active auth mode and credentials:

1. **Check `OIDC_ENABLED`** in `docker/sandbox/docker-compose.yml`
   - `"false"` → HTTP Basic Auth is active
   - `"true"` → OIDC Bearer token is active

2. **Resolve Basic Auth credentials** (when `OIDC_ENABLED=false`):
   - Read `docker/sandbox/.env` for `SANDBOX_DEV_USER` / `SANDBOX_DEV_PASSWORD` overrides
   - Fall back to compose defaults: `DEV_AUTH_USER` / `DEV_AUTH_PASSWORD` (currently `dev-user` / `dev-password`)
   - Use whichever value is set: `-u <user>:<password>`

3. **Required header on every request:** `tenantId: sandbox-tenant`

Never hardcode credentials or assume Bearer token auth is active — always derive from the files above.

---

## 15. Reference Links

1. **Casbin** — https://casbin.org/docs/overview
2. **ABAC Concepts** — https://casbin.org/docs/abac
3. **Chi Router** — https://pkg.go.dev/github.com/go-chi/chi/v5
4. **JWT/OIDC** — https://tools.ietf.org/html/rfc7519 | https://openid.net/connect/
5. **GORM** — https://gorm.io/docs/index.html

---

**Document Version:** 2.4
**Last Updated:** 2026-05-15
**Audience:** Development team, architects, AI agents
