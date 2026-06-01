# authorization-service - Priming Context

> One mistake is treating the priming document like comprehensive documentation. It is not. It is a cheat sheet for AI agents—the minimum context needed to generate aligned code.

## 1. Project Overview

**authorization-service** is a lightweight, centralized REST-based authorization service built with Go. It provides resource-level access control across multiple tenants or services using **Casbin RBAC** as the policy engine.

**Purpose:** Single source of truth for who can do what on which resources. Teams register resources here, define role-based policies, and query access decisions via REST API.

**Status:** ✅ RBAC fully implemented | 🔄 Next: ABAC expansion

**Key traits:** Multi-tenant, runtime policy management, PostgreSQL-backed, JWT/OIDC secured, centralized.

---

## 2. Tech Stack

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

## 3. Reference Links

1. **Casbin** — https://casbin.org/docs/overview
2. **ABAC Concepts** — https://casbin.org/docs/abac
3. **Chi Router** — https://pkg.go.dev/github.com/go-chi/chi/v5
4. **JWT/OIDC** — https://tools.ietf.org/html/rfc7519 | https://openid.net/connect/
5. **GORM** — https://gorm.io/docs/index.html

---

## 4. Internal Project Documents

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
- **Stories** — GitHub Issues in `lhtuwrk/authorization-service` (label: `feature:abac`, title format: `[ST-XXXXXX][FEATURE] Title`)
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

## 5. Project Structure

```
authorization-service/
├── .github/agents/
│   ├── context/                           # Agent context documents (PROJECT_PRIMING.md)
│   ├── rules/                             # Agent operational rules (*_Rules.md, STORY_STANDARD.md)
│   ├── memory/                            # Agent long-term memory files
│   └── working-record/                    # Agent daily standup logs
├── cmd/server/main.go                      # Entry point, router, DI
├── configs/casbin/model.conf              # RBAC model
├── docker/sandbox/                        # Frontend sandbox environment
│   ├── docker-compose.yml
│   ├── seed.sql
│   └── .env.example
├── docs/
│   ├── api/                               # OpenAPI spec (ABAC_API.yaml)
│   ├── feature/
│   │   └── Attribute_Based_Access_Control-ABAC/
│   │       ├── business/                  # Requirements and business framing
│   │       ├── developer/                 # Developer and integration guides
│   │       ├── operations/                # Deployment runbook and troubleshooting
│   │       ├── plan/                      # Roadmap, backlog, and sprint plans
│   │       ├── technical/                 # Technical analysis and implementation design
│   │       └── test-scenarios/            # Test scenarios (one .md per story)
│   └── wiki/                              # Project-wide guidelines and standards
├── internal/
│   ├── api/                               # HTTP handlers
│   ├── auth/                              # JWT middleware and context
│   ├── casbin/                            # Casbin singleton provider
│   ├── config/                            # Env var config
│   ├── db/migrations/                     # SQL migration files
│   ├── dto/                               # Request/response DTOs
│   ├── evaluation/                        # ABAC evaluation logic
│   ├── model/                             # DB models
│   ├── repository/                        # Data access layer
│   └── service/                           # Business logic
├── scripts/                               # Utility scripts (parity tests, etc.)
├── tests/feature/
│   └── Attribute_Based_Access_Control-ABAC/
│       ├── postman/                       # Postman collection
│       ├── report/                        # Execution logs and performance reports
│       └── scripts/                       # SQL and shell test scripts
├── go.mod, go.sum
└── README.md, CONTRIBUTING.md, MIGRATION_DOC.md, LICENSE
```

---

## 6. API Standards

- Keep OpenAPI/Swagger specs **short, explicit, and tool-safe** (validate in Swagger Editor)
- Prefer word enums (`EQ`, `LTE`, `NOT_IN`) over special characters
- Story discussions → GitHub Issues in `lhtuwrk/authorization-service` as issue comments (Jira-like Issue comment)

---

## 7. RBAC Model (Current)

**Definition** (`configs/casbin/model.conf`):
```
[request_definition]
r = sub, dom, obj, act

[policy_definition]
p = sub, dom, obj, act, eft

[role_definition]
g = _, _, _        # (user, role, domain)

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = (p.sub == "*" || g(r.sub, p.sub, r.dom)) && 
    (p.dom == "*" || r.dom == p.dom) && 
    r.obj == p.obj && r.act == p.act
```

**How it works:**
- Request → `(subject, domain, object, action)`
- Policies → `(subject|role, domain, resource, action, effect)`
- Roles → `(user, role, domain)` with 3-ary inheritance
- Effect → If any policy matches with `eft=allow`, grant access

**Limitations:**
- ❌ No attribute conditions (e.g., "if user.dept == Finance")
- ❌ No dynamic evaluation (time, IP, headers)

---

## 8. Core API

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

## 9. Key Interfaces

```go
// ResourceService
CreateResource(r *http.Request, req CreateResourceRequest) (string, error)
IsAllowed(r *http.Request, req CheckResourceRequest) (*CheckResourceResponse, error)

// PolicyService
GetPolicies(r *http.Request, domain, resource string) ([]ResourcePolicy, error)
AddPolicy(policy ResourcePolicy) error
UpdatePolicy(r *http.Request, req UpdateResourcePolicy) error
RemovePolicy(r *http.Request, policy ResourcePolicy) error
```

---

## 10. Architectural Patterns

**Layered:** API → Service (business logic) → Repository (data access) → Database

**DI:** Services receive dependencies via constructor; circular deps resolved post-construction

**Casbin singleton:** One enforcer per service, thread-safe, shared state

**Token context:** JWT claims extracted → `TokenContext` → passed via `r.Context()` throughout call chain

**Auth middleware:** `authMiddleware.Authenticated` applied to all `/api/*` routes

**Multi-tenancy:** Domain as first-class field in all policies; user domain from JWT `dom` claim

**Policy-resource sync:** Creating resources may update policies; policy updates validate against existing resources

**Config:** 12-factor env vars (POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, PORT, OIDC_ENABLED, AUTH_SERVER_URL, AUTH_CLIENT_ID, CASBIN_MODEL_PATH)

---

## 11. ABAC Design Notes

**Current constraints:**
- Casbin matcher uses RBAC-specific `g()` function
- Request: only 4 fields `(sub, dom, obj, act)`
- Policies: 5-tuple `(sub, dom, obj, act, eft)` in Casbin rule table
- No attribute metadata schema

**Design questions for ABAC:**
1. How to pass attributes? (JWT claims, request body, service lookup?)
2. Policy storage? (Extend rule table or new schema?)
3. Matcher? (Extend Casbin syntax or custom evaluation?)
4. Performance vs. RBAC baseline?
5. RBAC/ABAC coexistence?

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| RBAC | Role-Based Access Control |
| ABAC | Attribute-Based Access Control |
| Policy | `(subject, domain, resource, action, effect)` rule |
| Domain | Tenant/workspace for multi-tenancy isolation |
| Resource | Named object being protected |
| Action | Operation on resource (read, write, delete) |
| JWT | Stateless bearer token with claims |
| OIDC | OpenID Connect authentication protocol |

---

## 13. Story Collaboration Workflow

Stories are **GitHub Issues** in `lhtuwrk/authorization-service`.

For story-level collaboration, post discussions as **comments on the GitHub Issue** using the `## Comment Format` format.

- Do not put discussion threads inside the issue body — the body is for User Story, AC, and Deliverables only.
- Do not create separate per-story review-note files for normal BA, PO, TL, Developer, or QA discussion.
- Use a Jira-like thread structure so one topic stays in one place. Post each thread as a new issue comment:

```md
## Comment Format

Must Follow section 9 `## 9. Comment Standard` in the `.github\agents\rules\STORY_STANDARD.md`

## 14. Design first before Implementation

If the feature need to Implement is complex, need to design the solution first and comment to story to let TL review. Below is structure:

- Capabilities: [your scope constraints]
- Components: [your infrastructure and architecture constraints]
- Interactions: [your integration and data flow patterns]
- Contracts: [your type and interface conventions]

Present each level separately. Wait for TL approval before moving to the next. No code until the contracts are agreed.

---

## 15. Agent Working Records

Agent Working Records are **personal daily logs** that help agents remember what they accomplished yesterday and plan today's work. Each agent maintains their own record. It follows a scrum standup format and maintains a rolling 3-day history.

**Location:** `.github/agents/working-record/{Agent_Name}_Working_Record.md`

**Access Control:** Each agent can only read and update their own working record. An agent must not read or modify the working records of other agents.

**Purpose:**
- Track what was completed each day
- Document current work in progress
- Flag impediments and blockers
- Provide context across agent sessions

**Format:** Each day is recorded as a standup entry with:
- **Date:** YYYY-MM-DD
- **Completed:** What was done (list of tasks, features, bug fixes)
- **In Progress:** Current work and next priorities
- **Impediments:** Any blockers, questions, or dependencies (none if clear)

**Retention:** Keep the 3 most recent days; remove oldest entries when adding new ones.

**Update workflow:**
- At **start of session:** Read only your own working record to understand yesterday's context. If your record contain any stories, then **sync story statuses with GitHub** — check the current status on each story and update the record if it differs before reporting status
- **During work:** Keep notes on progress
- **At end of session:** Use the `edit` tool to update "Completed", "In Progress", and "Impediments" sections in your record
- **Every 3 days:** Remove the oldest entry when adding a new day

The record must be short but enough information. Include specific file paths, PR numbers, story IDs, or commit SHAs when relevant. Keep entries concise and factual.

**Template structure:**
```md
## {Agent_Name} Working Record

### 2026-04-15 (Today)
**Completed:** ...
**In Progress:** ...
**Impediments:** ...

### 2026-04-14
**Completed:** ...
**In Progress:** ...
**Impediments:** ...

### 2026-04-13
**Completed:** ...
**In Progress:** ...
**Impediments:** ...
```

---

**Document Version:** 2.1  
**Last Updated:** 2026-05-08  
**Audience:** Development team, architects, AI agents
