# {project-name} — Priming Context

> This is a cheat sheet for AI agents — the minimum context needed to understand the project, architecture, and team workflow. It is not comprehensive documentation.

## 1. Project Overview

**{project-name}** is a {brief-description — e.g., "lightweight REST-based service that..."}.

**Purpose:** {what problem it solves and who uses it}.

**Status:** {current implementation status, e.g., "✅ Phase 1 complete | 🔄 Next: Phase 2"}

**Key traits:** {key architectural or operational traits, e.g., multi-tenant, event-driven, REST-based, etc.}

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
| {Term} | {Definition — add domain-specific terms here} |

---

## 3. Story Workflow

**GitHub mode:** Stories are **GitHub Issues** in `{github-org}/{repo-name}` (label: `{feature-label}`, title format: `[ST-XXXXXX][FEATURE] Title`).

**Strict mode:** Stories are **local MD files** under `.claude/agents/docs/stories/` (filename: `ST-XXXXXX.md`). No GitHub Issues are created. See `Strict_Mode_Story_Guide.md` for the full format and lifecycle.

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
- Story body/file contains only: User Story, AC, Deliverables
- **GitHub mode:** All discussions happen as **comments** on the GitHub Issue — never in the body
- **Strict mode:** All discussions are appended to the `## Comments` section of the story MD file
- One topic per comment thread

For the full workflow (status transitions, role boundaries, AC rules, merge gate, comment format): `.claude/agents/rules/Story_Standard.md`

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

Entries are **bullets, not paragraphs** — one line per item with story ID + outcome + PR/commit ref, hard cap ~100–150 words per day; detail lives in the retro/PR/memory fact by pointer (see `Agent_Common.md §5`).

---

## 6. Internal Project Documents

Navigate here for project context:

- **Business requirements** — `docs/requirements/Business_Requirements.md`
- **Implementation roadmap** — `docs/plan/Implementation_Roadmap.md`
- **Product backlog** — `docs/plan/Product_Backlog.md`
- **Sprint plan** — `docs/sprints/Sprint_N_Overview.md`
- **Technical analysis** — `docs/technical/Technical_Analysis.md`
- **Architecture overview** — `docs/technical/Architecture.md`
- **Development standards** — `docs/wiki/Development_Standards.md`
- **Code review checklist** — `docs/wiki/Code_Review_Checklist.md`
- **Testing guidelines** — `docs/wiki/Testing_Guidelines.md`
- **API spec** — `docs/api/{project-api-spec}.yaml`
- **Feature docs** — `docs/feature/<feature_name>/`
- **Test Scenarios** — `docs/feature/<feature_name>/test-scenarios/` (one file per story)
- **Test Scripts** — `tests/feature/<feature_name>/scripts/`
- **Test Reports** — `tests/feature/<feature_name>/report/`

Name new or renamed documents in `Title_Case_With_Underscores`, for example `My_Technical_Document.md`.

---

## 7. Key Directories

| What | Path |
|------|------|
| Entry point | `{entry-point-path}` |
| HTTP handlers / controllers | `{handlers-path}` |
| Business logic | `{services-path}` |
| Data access | `{repository-path}` |
| DB models / entities | `{models-path}` |
| Feature docs | `docs/feature/` |
| API spec | `docs/api/` |
| Wiki / guidelines | `docs/wiki/` |
| Test scenarios | `docs/feature/{feature-name}/test-scenarios/` |
| Test scripts & reports | `tests/feature/{feature-name}/` |
| Local sandbox | `{sandbox-path}` |

---

## 8. Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | {language} | {version} |
| Framework / Router | {framework} | {version} |
| Database | {database} | {version} |
| ORM / Data layer | {orm-or-data-library} | {version} |
| Auth | {auth-mechanism} | {version} |

---

## 9. API Standards

- Keep API specs **short, explicit, and tool-safe** (validate in {api-spec-tool, e.g., Swagger Editor})
- {Any project-specific API conventions, e.g., versioning pattern, error envelope format, naming rules}

---

## 10. Core API

| Method | Endpoint | Auth | Purpose |
|--------|----------|:----:|---------|
| {METHOD} | `{/path}` | ✓/✗ | {purpose} |
| {METHOD} | `{/path}` | ✓/✗ | {purpose} |

**Auth:** `{auth-header-format, e.g., Authorization: Bearer <TOKEN>}`

---

## 11. Current State

{Brief description of what is currently implemented and what is next.}

**Known limitations:**
- ❌ {Known limitation 1}
- ❌ {Known limitation 2}

---

## 12. Architectural Patterns

{Describe the key architectural patterns used in this project, for example:}

**Layered:** API → Service (business logic) → Repository (data access) → Database

**DI:** Services receive dependencies via constructor

**Config:** Environment-variable based (list key env vars if applicable)

---

## 13. Feature Current State

- {Current implementation status for the active feature}
- {What is scaffolded but not yet implemented}

---

## 14. Local Sandbox Environment

The sandbox configuration lives under `{sandbox-path}`:

| File | Path |
|------|------|
| Compose file | `{sandbox-path}/docker-compose.yml` |
| Env overrides | `{sandbox-path}/.env` (git-ignored; may not exist) |
| Seed data | `{sandbox-path}/{seed-file}` |

**Before making any API call or running any test script**, verify the active auth mode and credentials from the sandbox config files. Never hardcode credentials.

---

## 15. Reference Links

1. **{Technology}** — {link}
2. **{Technology}** — {link}

---

**Document Version:** 1.0
**Last Updated:** {YYYY-MM-DD}
**Audience:** Development team, architects, AI agents