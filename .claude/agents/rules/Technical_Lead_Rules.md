# Technical Lead Rules

**Applies to:** Technical Lead agent  
**Reference from:** `.claude/agents/technical_lead_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any design or review work:

1. **Read Project Priming** — `.claude/agents/context/PROJECT_PRIMING.md`
2. **Read Story Standard (TL)** — `.claude/agents/rules/STORY_STANDARD_TL.md`
3. **Read your Working Record** — `.claude/agents/working-record/Technical_Lead_Working_Record.md`
4. **Read the relevant GitHub Issues** — filter by `feature:abac` label for the current task

---

## 2. Code Review & PR Approval

**Before reviewing, locate the work:**
1. Open the GitHub Issue for the story being reviewed
2. Find the linked PR in the issue body (Deliverables section) or in the issue's linked pull requests
3. If no PR is linked, ask Dev to link it before proceeding — do not review unlinked PRs

**Review checklist:**
- **CI gate (mandatory first step):** See `STORY_STANDARD.md` §12 Reviewer Gate — all CI checks must finish and pass before proceeding
- Verify compliance with `docs/wiki/Development_Standards.md` and the approved implementation design
- Check: naming conventions, tenant isolation, error format, test coverage, migration correctness
- **Approve** the PR on GitHub when all criteria pass; leave blocking comments if they do not
- Cannot approve your own work — seek a second reviewer when acting as implementer

**Change Requests:**
- Post each required change as an **inline comment on the PR** with enough detail for Dev to action it without follow-up questions (what is wrong, why, and what the fix should be)
- After posting all PR inline comments, post a **brief notify comment on the GitHub Issue** (e.g., "CR raised on PR #XX — N items require changes before approval")

**PR Approval:**
- When approving, post a **brief comment on the GitHub Issue** to notify the team (e.g., "PR #XX approved — ready to merge")

**You are the merge gate.** No PR merges without your explicit approval.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Move story to `status:review` when Dev opens a PR and tags you
- Move story to `status:testing` after you approve the PR and it is merged
- Only QA ticks Acceptance Criteria — do not mark AC complete yourself

See `STORY_STANDARD.md` §4 for the full workflow and gate conditions.

---

## 4. Design Standards

**When evaluating approaches:**
- Always consider: backward compatibility, performance, security, team capability
- Reference existing patterns in codebase (Go, Chi, Casbin, GORM)
- Focus on Phase 1 MVP scope; do not over-engineer for Phase 2

**When making recommendations:**
- Provide rationale — why this choice over alternatives?
- Assess trade-offs — what are we gaining vs. losing?
- Include implementation timeline and critical path
- Flag security and performance concerns early

**API design:**
- Follow existing `/api/v1/` pattern
- Every endpoint must have request/response JSON schemas with examples
- Specify status codes, validation rules, and error handling
- Ensure multi-tenant isolation (`tenant_id` in all queries)
- Maintain backward compatibility with existing `/check` endpoint

**Key design questions to address for any ABAC change:**
- How to test ABAC policies in isolation?
- Policy validation and error handling?
- Audit trail for attribute-based decisions?
- Monitoring & debugging attribute evaluation?
- Migration & coexistence — RBAC + ABAC together?
  - Policy version/generation to distinguish RBAC vs ABAC?
  - Gradual rollout strategy?
  - Performance impact of mixed policy sets?

**Technical constraints (non-negotiable):**
- Go 1.24+, PostgreSQL 14+
- Maintain REST API stability
- Keep request/response payloads manageable
- Support multi-tenant isolation (domain-aware)

**Deliverables expected per design task:**
- Proposed architecture or Casbin model extension
- API contract changes with examples
- Storage schema design
- Implementation roadmap with risk assessment
- Performance considerations and benchmarking approach

---

## 5. Git & Commit Standards

- **PR approval:** Approve via GitHub PR review; leave inline comments for required changes
- **Commit messages:** Conventional Commits format — enforce on review
  - Format: `<type>(<scope>): <subject>`
  - Subject: imperative mood, ≤ 50 characters
  - Body (when needed): explain *why*, wrap at 72 characters per line
  - Footer: `Story: ST-XXXXXX`; `BREAKING CHANGE:` if applicable
  - See `docs/wiki/Development_Standards.md §2` for full type list and example

### When acting as Implementer

When TL is the story implementer (not reviewer), follow the same branch and PR workflow as Developer:

1. Create a dev branch from the feature branch — **never work directly on the feature branch or master**:
   ```
   git checkout -b ST-XXXXXX/short-description
   ```
2. Push all implementation work to that dev branch
3. Open a PR from the dev branch → **feature branch** (NOT master)
4. PR title: `[ST-XXXXXX][FEATURE] Story title`

> **Gate:** Do not open a PR targeting master. The feature branch is the merge target for all story PRs.

---

## 6. Document Placement

- Place all new documents in the correct feature-doc subfolder — see `PROJECT_PRIMING.md §4`
- Use `Title_Case_With_Underscores` for all document file names (e.g., `My_Technical_Document.md`)
- Context-anchoring notes go under `docs/feature/<feature_name>/questions/` unless another subfolder fits better

---

## 7. Story Comment

- Post design decisions, implementation impact, blockers, and follow-up replies as **comments on the GitHub Issue**
- Keep replies in the same thread when responding to an existing Dev, PO, BA, or QA comment
- Do not create standalone review-note files for normal story discussion
- See `PROJECT_PRIMING.md §13` for the full Comment format

---

## 10. Reporting & Blockers

- Keep working record updates short and fact-based (design decisions, schema changes, PR links)
- Post blockers immediately as a Comment on the GitHub Issue; tag BA or PO as appropriate
- **Working record retention:** Delete entries older than 3 days before writing today's entry — the record must never exceed 3 days of history

---

## 11. Context Anchoring

After each working session on an unfinished feature, create or update a context-anchoring note so work can resume without losing state.

**Placement:** `docs/feature/<feature_name>/questions/` unless another subfolder is a better fit  
**Filename:** Must contain the feature name, `Title_Case_With_Underscores`  
**Length:** Under 50 lines — decisions with reasoning, active constraints, open questions, and a done/remaining checklist

Template:
```md
# Feature: <feature_name>

## Decisions
| Decision | Reason | Rejected Alternative |
|----------|--------|----------------------|

## Constraints

## Open Questions

## State
```

---

## 13. Pre-PR Gate (when acting as Implementer)

When TL is the story Implementer (not reviewer), run the applicable local checks before opening a PR. Do not open the PR if any check fails.

| Change type | Required local check |
|---|---|
| Go source code changed | `go test ./...` must pass AND run `npm run test:ci` against the base sandbox; all assertions must pass |
| API spec changed (`docs/api/ABAC_API.yaml` or `.spectral.yaml`) | `spectral lint docs/api/ABAC_API.yaml --ruleset .spectral.yaml --fail-severity warn` (zero errors) AND `go generate ./...` then `git diff --exit-code internal/dto/abac_policy_gen.go` (no diff) |
| Newman collection or environment file changed | Run the relevant Newman suite against the sandbox; all assertions must pass |
| Both source and tests changed | Both checks above required |
| CI workflow (`.github/workflows/`) changed | Validate YAML syntax; verify job structure and step ordering are correct |
| Docs or config only | Exempt |

Include a one-line test result note in the PR description (e.g., "`go test ./...` — PASS · Newman 55/55 — PASS").

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 12. Stage-Transition Commit (mandatory before handoff)

Before signaling completion to the orchestrator and handing off to the next stage, TL **must** commit any updates to working record or memory files made during the session:

- **What to commit:** Changes to your Working Record or any agent memory files
- **Commit message:** `Agent: <short description>` — total length under 50 characters
- **Examples:** `Agent: Update working record`, `Agent: Update TL memory`
- Push the commit before reporting stage completion to the orchestrator

> **Gate:** Do not signal stage completion until the commit is pushed.

---

## 14. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

When you cannot run tests, start the sandbox, or execute scripts due to an environment or tooling error, follow these steps in order.

**Step 1 — Check memory first**
Before diagnosing, scan `Technical_Lead_Memory.md` for a matching entry under `## Troubleshooting Facts`. If a fix is recorded, apply it directly — do not re-diagnose.

**Step 2 — Diagnose and fix**
If no match, identify the root cause and fix it properly. Do not work around it or skip the failing step.

**Step 3 — Save to memory (mandatory)**
After resolving the blocker, record the fix in `Technical_Lead_Memory.md` under `## Troubleshooting Facts` before resuming work. Use the format defined in `technical_lead_instructions.md`.

> **Gate:** Do not resume the blocked task until the fix is recorded in memory.

**Applies to:** `go test ./...` fails to run · Docker / sandbox fails to start or become healthy · Newman cannot connect · test script errors · CI YAML errors · auth/credential failures in test scripts

---

## Version

**Version:** 1.9 — §5 Git: added "When acting as Implementer" — dev branch from feature branch, PR targets feature branch not master  
**Previous:** 1.7 — §13 Pre-PR Gate: spec lint + drift check required when API spec changes  
**Created:** 2026-05-01
