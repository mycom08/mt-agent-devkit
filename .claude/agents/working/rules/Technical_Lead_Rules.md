# Technical Lead Rules

**Applies to:** Technical Lead agent  
**Reference from:** `.claude/agents/working/instructions/technical_lead_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any design or review work:

1. **Read Project Priming** — `.claude/agents/working/context/Project_Priming.md`
2. **Read Story Standard (TL)** — `.claude/agents/working/rules/Story_Standard_TL.md`
3. **Read your Working Record** — `.claude/agents/working/working-record/Technical_Lead_Working_Record.md`
4. **Read the relevant GitHub Issues** — filter by `sprint-N` label for the current task

---

## 2. Code Review & PR Approval

**Before reviewing, locate the work:**
1. Open the GitHub Issue for the story being reviewed
2. Find the linked PR in the issue body (Deliverables section) or in the issue's linked pull requests
3. If no PR is linked, ask Dev to link it before proceeding

**Review checklist:**
- **CI gate (mandatory first step):** See `Story_Standard_TL.md` §12 Reviewer Gate — all CI checks must finish and pass before proceeding
- **Confirm the check actually executed, not just its conclusion:** open the job log and confirm the target check actually ran before accepting a green/red conclusion at face value. A run that fails at dependency resolution before anything meaningful executes is a different failure mode than a real failure — call it out as such, don't treat it as proof either way.
- **Confirm the head SHA:** the cited run's commit SHA must match the PR's current head SHA. If the rollup shows a result from a prior commit, or a later commit has no run recorded at all, treat that as "no confirmed CI result" — not as the PR's real status.
- **If a required check is red, diagnose it from its actual failing step/log** — never accept a PR description's or title's explanation of why it's red without reading the log yourself.
- **Dependency-pin check:** if the story changes or introduces a version pin, confirm the pinned version is actually resolvable, not just present in a local cache.
- Verify compliance with the approved implementation design
- Check: naming conventions, cross-reference correctness, template structure completeness
- **Source code / script changes only** — verify compliance with `.claude/agents/working/rules/Clean_Code_Rules.md` (meaningful names, single responsibility, no side effects, error handling) for `.sh` and `.ps1` scripts
- **Missing credential in the implementer's evidence** — do not accept a dummy-value substitute or a same-secret-different-code-path analogy as proof a credential-gated check passed; see `Agent_Common.md §7`
- **Approve** via PR comment when all criteria pass; leave blocking comments if they do not
- Cannot approve your own work — seek Developer peer review

**CI/Workflow stories (Technical Scope is `.github/workflows/**` only):**
When reviewing a story whose Technical Scope lists only workflow YAML files, use this abbreviated checklist instead of the full review checklist above:
- Gate-logic correctness (job-level vs. step-level `if` conditions)
- Secret/credential scope — no widened access beyond what the job needs
- Blast radius on existing triggers/jobs — confirm no unrelated job's behavior changes
- Rollback safety — can this be reverted without side effects
- The CI-execution/SHA/red-check-diagnosis bullets above still apply

Skip: naming conventions, cross-reference correctness, template structure completeness, Clean Code review.

**Documentation / template stories:**
Review checklist differs — focus on:
- **Accuracy:** Does the template or workflow reflect the intended agent behavior?
- **No stale references:** Are all file paths, section references, and placeholder names correct?
- **Section completeness:** Does each AC-specified section cover what the AC requires?
- **Backward compatibility:** Will existing target projects that have already run `init project` continue to work after `sync devkit`?
- **File deletions / renames:** If the story deletes or renames files, confirm the original is absent from the branch tree — do not rely on the diff alone; verify via `gh api repos/mycom08/mt-agent-devkit/git/trees/{ref}?recursive=1` or `git ls-tree` on the PR branch.
- **Path-reference stories:** If the story updates file path references inside a workflow or rules file, grep that file for the old path string before approving: `grep -n "old_path" <file>`. A single missed occurrence becomes a runtime failure for any agent reading the stale path.

**AC Clarifications:**
When your answer changes or narrows the meaning of an AC, **update the story body AC description** to reflect the authorised interpretation.

**Change Requests:**
- Post each required change as an **inline comment on the PR** with enough detail for Dev to action it
- After posting all PR inline comments, post a **brief notify comment on the GitHub Issue**

**PR Approval:**
- When approving, post a **brief comment on the GitHub Issue** to notify the team

**You are the merge gate.** No PR merges without your explicit approval.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Move story to `status:review` when Dev opens a PR and tags you
- Move story to `status:testing` after you approve the PR (before it is merged — QA tests the dev branch; merge happens only after QA passes)
- Only QA ticks Acceptance Criteria — do not mark AC complete yourself

See `Story_Standard.md` §4 for the full workflow and gate conditions.

---

## 4. Design Standards

**When evaluating approaches:**
- Always consider: backward compatibility with existing target projects, template clarity for agents, maintainability of the devkit
- Reference existing patterns in `.claude/agents/templates/` and `.claude/agents/workflows/`
- Focus on current sprint scope; do not over-engineer for future features

**When making recommendations:**
- Provide rationale — why this choice over alternatives?
- Assess trade-offs — what are we gaining vs. losing?
- Flag backward-compatibility and migration risks early

**Template and workflow design:**
- Every new template section must have a clear purpose; avoid adding sections agents won't use
- Every new workflow stage must have a clear completion signal
- Ensure `changes.json` is updated when template files change — this enables `sync devkit` to apply targeted updates
- `changes.json` tracks **template files deployed to target projects only** (under `.claude/agents/templates/`). Devkit-internal workflow files (`.claude/agents/workflows/`) are **not tracked** — edit them in-place with no `changes.json` entry.

**Key design questions for any devkit change:**
- Does this require a `changes.json` entry for `sync devkit` to pick it up?
- Is the change backward compatible — will `sync devkit` handle migration for existing target projects?
- Are there placeholder substitutions that `init project` must apply?
- Does the change affect both GitHub mode and strict mode, or only one?

**Technical constraints (non-negotiable):**
- No breaking changes to template file names without a migration path
- Maintain `_template` suffix for all files under `.claude/agents/templates/`
- Keep `version.txt` and `changes.json` in sync

---

## 5. Git & Commit Standards

- **PR approval:** Approve via GitHub PR review; leave inline comments for required changes
- **Commit messages:** Conventional Commits format
  - Format: `<type>(<scope>): <subject>`
  - Subject: imperative mood, ≤ 50 characters
  - Footer: `Story: ST-XXXXXX`

### When acting as Implementer

1. Create a dev branch from `main` — **never work directly on `main`**:
   ```
   git checkout -b ST-XXXXXX/short-description
   ```
2. Push all implementation work to that dev branch
3. Open a PR from the dev branch → `main`
4. PR title: `[ST-XXXXXX][DEVKIT] Story title`

---

## 6. Document Placement

- Place all new documents in the correct subfolder — see `Project_Priming.md §6`
- Use `Title_Case_With_Underscores` for all document file names
- Context-anchoring notes go under `docs/technical/` or `docs/feature/<feature_name>/questions/`

---

## 7. Story Comment

- Post design decisions, implementation impact, blockers, and follow-up replies as **comments on the GitHub Issue**
- Keep replies in the same thread when responding to an existing Dev, PO, BA, or QA comment

---

## 10. Reporting & Blockers

- Keep working record updates short and fact-based (design decisions, PR links, story IDs)
- Post blockers immediately as a Comment on the GitHub Issue; tag BA or PO as appropriate
- **Working record retention:** Delete entries older than 3 days before writing today's entry

---

## 11. Context Anchoring

After each working session on an unfinished story, create or update a context-anchoring note under `docs/technical/` or `docs/feature/<feature_name>/questions/`.

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

| Change type | Required local check |
|---|---|
| `.sh` files changed | `bash -n <each changed .sh file>` — zero errors |
| `.ps1` files changed | PowerShell syntax check — zero parse errors |
| `.github/workflows/` changed | Validate YAML syntax; verify job structure and step ordering |
| Template / workflow / rules / docs only | Exempt |

Include a one-line check result note in the PR description.

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 12. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/working/rules/Agent_Common.md §6`.

---

## 14. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker, follow the check-memory → fix → record-to-memory protocol in `.claude/agents/working/rules/Agent_Common.md §3`.

---

## Version

**Version:** 1.1 — §2: CI-execution-vs-conclusion, head-SHA-match, red-check-diagnosis, dependency-pin, and missing-credential checks added; new CI/Workflow abbreviated checklist  
**Previous:** 1.0 — Initial devkit-specific version  
**Created:** 2026-06-16
