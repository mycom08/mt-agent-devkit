# Developer Rules

**Applies to:** Developer agent  
**Reference from:** `.github/agents/developer_instructions.md`

---

## 1. Mandatory Reading Before Any Implementation

Before writing a single line of code on any story, Dev **must** read:

| Document | Path | What it covers |
|---|---|---|
| Development Standards | `docs/wiki/Development_Standards.md` | Coding conventions, commit format, API standards |
| Developer Rules | `.github/agents/rules/Developer_Rules.md` | This file — workflow gates and naming rules |
| Story Standard | `.github/agents/rules/STORY_STANDARD.md` | Story workflow and role boundaries |

> **Gate:** Do not begin implementation until all three documents above have been read in the current session.

---

## 2. Before Starting a Story (Mandatory Pre-Start Steps)

### On `status:backlog` — Read & Clear Questions Only

When a story is in `status:backlog`, Dev may **not** write code. Dev **must**:

1. Read the full story — User Story, all AC, Technical Scope, and any linked technical docs
2. Identify any unclear AC, scope gaps, or technical ambiguities
3. Post open questions as comments on the GitHub Issue:
   - Tag **PO** for scope/AC questions
   - Tag **TL** for technical/design questions
4. **Read PO and TL answers** when they respond — do not skip or assume
5. If an answer is insufficient, raises a new concern, or Dev disagrees, **post a push-back comment** before proceeding — tag the same role again with a clear follow-up question
6. Wait until all blocking questions are fully resolved before moving to implementation

> Non-blocking questions may be noted and continued; only blocking questions must be resolved before moving forward.

### On `status:ready` — Implementation Allowed

A story reaches `status:ready` only when all blocking open points are resolved. At that point:

1. **Update story status** — Remove label `status:ready`, add label `status:in-progress`
2. Create your dev branch: `ST-XXXXXX/short-description` (branch off feature branch)
3. Begin implementation

> If the story is complex, follow the design-first rule — refer to section `Design first before Implementation` in `PROJECT_PRIMING.md`.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Update story status by changing the GitHub Issue label at each stage.
- Cannot merge without: TL approval + QA sign-off on dev branch + local tests passing.
- **Do NOT tick Acceptance Criteria** — AC is owned by QA. Ticking AC yourself is a role violation.

See `STORY_STANDARD.md` §4 for the full workflow and gate conditions.

---

## 4. Code Quality & Naming

**Source files:** Use descriptive names. Do NOT use:
- `interface.go`, `helpers.go`, `types.go`, `errors.go`, `utils.go`

✅ Good examples:
- `rule_evaluator.go` — implements RuleEvaluator interface
- `condition_helpers.go` — helpers for conditions
- `evaluation_types.go` — types used in evaluation
- `validation_errors.go` — validation error definitions

**Rule:** Name files after their primary interface/struct; use `snake_case`.

**Story files:** Stories are GitHub Issues — title format `[ST-XXXXXX][FEATURE] Title In Title Case`. No `.md` story files.

---

## 5. Testing & Verification

Run before creating a PR:
- `go test ./...` — all tests must pass
- `go run ./cmd/server` — service must start cleanly

**Pre-merge checklist:**
1. Local tests pass
2. Source files follow naming convention above
3. PR created with title `[ST-XXXXXX][FEATURE] Story title`
4. TL has reviewed and approved PR
5. QA has tested on the dev branch and ticked all AC
6. Update story label to `status:done` after merge

---

## 6. Git Workflow

- **Dev branch:** `ST-XXXXXX/short-description` (branch off feature branch)
- **PR title:** `[ST-XXXXXX][FEATURE] Story title`
- Link PR to working issue
- **Wait for TL approval** before merging dev branch to feature branch
- No merge without TL code review

**Commit Message Rules:**
- Format: `<type>(<scope>): <subject>` — Conventional Commits
- Subject: imperative mood, ≤ 50 characters (`Add …` not `Added …`)
- Body (when needed): explain *why*, wrap at 72 characters per line
- Footer: always include `Story: ST-XXXXXX`; add `BREAKING CHANGE:` if applicable
- See `docs/wiki/Development_Standards.md §2` for the full type list and a complete example

---

## 7. Reporting & Blockers

- Keep working record updates short and fact-based (file paths, PR #s, story IDs, commits)
- Post blockers immediately as a comment in the GitHub Issue; tag TL or PO as appropriate
- **When starting a session:** Read your working record, then **sync story statuses with GitHub** — check the current label on each in-progress or recently completed story and correct the record before reporting status

---

## 8. Document Placement
- When you update or create project documents, use the current feature-doc structure. Refer section `## 4. Internal Project Documents` in project priming document.

---

## Version

**Version:** 1.4 — Fixed duplicate §2; Dev must not tick AC; merge gate requires QA sign-off on dev branch  
**Previous:** 1.3 — Added §1 mandatory reading gate  
**Created:** 2026-04-24
