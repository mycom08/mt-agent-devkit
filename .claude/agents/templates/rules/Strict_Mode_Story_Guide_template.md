# Strict Mode Story Guide

Reference for all agents operating in `mode: strict`. Replaces all GitHub Issues, GitHub PR, and GitHub Actions operations with local equivalents. All files live under `.claude/agents/` and are gitignored — no agent files are ever committed to the project.

---

## Story File Location

```
.claude/agents/docs/stories/ST-XXXXXX.md
```

All stories are single MD files. The story ID is the canonical identifier across all operations.

---

## Story ID Generation

1. Read `.claude/agents/docs/story_counter.txt` — contains the last used integer (e.g., `3`)
2. Increment by 1 → new ID integer (e.g., `4`)
3. Format as zero-padded 6-digit string: `ST-000004`
4. Write the new integer back to `story_counter.txt`
5. Create the story file: `.claude/agents/docs/stories/ST-000004.md`

Never reuse or skip numbers. If the counter file is missing, start from `0`.

---

## Story MD Format

```markdown
# ST-000001 — <Title>

**Status:** backlog
**Assigned:** Developer
**External ID:** PROJ-123
**Points:** 3
**Sprint:** sprint-1
**Feature:** none
**Phase:** none
**Created:** YYYY-MM-DD

---

## User Story
As a [...], I want [...], so that [...].

## Acceptance Criteria
- [ ] AC 1
- [ ] AC 2

## Technical Scope
- `path/to/file.ts` — description of change

---

## Comments
```

**Field rules:**
- `**Status:**` — one of the values in the Status Values table below; always present
- `**External ID:**` — optional; omit the entire line if the project has no external tracker
- `**Sprint:**` — `sprint-N` format; omit the line if not yet assigned to a sprint
- `**Feature:**` / `**Phase:**` — write `none` if not part of a feature

---

## Status Values

| Value | Equivalent GitHub label | Meaning |
|---|---|---|
| `backlog` | `status:backlog` | Not yet scheduled |
| `ready` | `status:ready` | Refined, ready to start |
| `in-progress` | `status:in-progress` | Being implemented |
| `review` | `status:review` | PR / review-record open |
| `testing` | `status:testing` | QA validation in progress |
| `blocked` | `status:blocked` | Waiting on external input |
| `done` | `status:done` | Accepted and closed |

Agents update `**Status:**` by editing the field in the story MD file directly.

---

## Comments Section

All communication that would go to GitHub Issue / PR comments goes into the `## Comments` section at the bottom of the story MD file.

**Format for each comment entry:**

```markdown
## Comments

---
**[YYYY-MM-DD HH:MM] Developer**
Implemented the login endpoint. All ACs confirmed. Awaiting review.

---
**[YYYY-MM-DD HH:MM] Technical Lead**
LGTM — minor: rename `authToken` to `accessToken` for consistency with §3 naming conventions. Otherwise approved.

---
**[YYYY-MM-DD HH:MM] Developer**
Renamed. Branch ready for QA.
```

Rules:
- Always append — never delete or overwrite existing comment entries
- Include role name and ISO timestamp on the header line
- Keep entries concise — details go in the agent's Working Record
- **Writing standard (same as GitHub-mode `Story_Standard.md §9`):** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, soft cap ~150–200 words per entry (QA per-AC validation reports exempt); evidence by pointer, full check logs in your Working Record; corrections state the delta only; no entries about prior entries; one close-out line per story hand-off

---

## Local Review Record

Replaces `gh pr create` / `gh pr comment` / `gh pr diff`.

**Location:** `.claude/agents/docs/reviews/ST-XXXXXX_review.md`

**Format:**

```markdown
# Review Record — ST-000001

**Story:** <title>
**Branch:** story/PROJ-123-brief-title
**Sprint Branch:** sprint-1-dev
**Reviewer:** Technical Lead
**Created:** YYYY-MM-DD
**Status:** pending | changes-requested | approved

---

## Diff Summary

<!-- Orchestrator writes: git diff sprint-N-dev...story/XXXX --stat output here -->

---

## Review Notes

*(pending)*

---

## Verdict

*(pending — Technical Lead writes: approved / changes-requested + required changes)*
```

The orchestrator creates this file before spawning the reviewer agent. The reviewer reads it, appends notes and verdict, and updates `**Status:**`. If changes are requested, the implementer appends a reply under a new `## Round N Response` heading.

---

## Branch Naming

### Sprint dev branch
```
sprint-N-dev
```
Example: `sprint-1-dev`, `sprint-3-dev`

Created from the user's current branch at sprint start. Never pushed to remote. The user merges this into their branch manually when ready.

### Story branch
Created from the sprint dev branch. Named using the external ID when available, otherwise the internal ST-XXXX ID:

```
story/<external-id>-<slug>        # when External ID is set
story/ST-XXXXXX-<slug>            # when no External ID
```

`<slug>` = story title lowercased, spaces replaced with hyphens, truncated to 30 characters, non-alphanumeric characters removed.

Examples:
```
story/PROJ-123-add-login-endpoint
story/ST-000004-fix-token-refresh
```

---

## Commit Message Format

```
<primary-id> [<secondary-id>]: <message>
```

- **With External ID:** `PROJ-123 [ST-000001]: add login endpoint`
- **Without External ID:** `ST-000001: add login endpoint`

`<message>` is a lowercase imperative phrase ≤ 60 characters (e.g. `add login endpoint`, not `Added login endpoint`). If the project already has a commit history, match its tense and capitalization conventions; if there is no prior history, use lowercase imperative.

---

## Branch Lifecycle

```
sprint start:
  check if sprint-N-dev exists (git branch --list sprint-N-dev)
  → exists: git checkout sprint-N-dev
  → missing: git checkout -b sprint-N-dev   (from current branch)

story start (Stage 1):
  git checkout -b story/<id>-<slug>   (from sprint-N-dev)

story done (after Stage 4 PO closure):
  git checkout sprint-N-dev
  git merge story/<id>-<slug> --no-ff -m "Merge ST-XXXXXX: <title>"
  git branch -d story/<id>-<slug>
  → append to story MD ## Comments:
    "[YYYY-MM-DD] Orchestrator — story merged into sprint-N-dev. Awaiting user review."
  → notify user: "ST-XXXXXX done — merged into sprint-N-dev"

sprint done:
  → notify user:
    "Sprint N complete. All stories merged into `sprint-N-dev`.
     Review and merge into your branch when ready. No action needed from agents."
  → do NOT touch the user's branch
```

---

## Operation Substitution Reference

Quick lookup for all GitHub → strict-mode equivalents used in workflows.

| GitHub operation | Strict-mode equivalent |
|---|---|
| `gh issue list --label "status:X"` | Glob `docs/stories/*.md`, filter by `**Status:** X` |
| `gh issue list --label "sprint-N"` | Glob `docs/stories/*.md`, filter by `**Sprint:** sprint-N` |
| `gh issue view <n>` | Read `.claude/agents/docs/stories/ST-XXXXXX.md` |
| `gh issue edit --add-label status:X` | Edit `**Status:** X` in story MD |
| `gh issue edit --body-file` | Edit story MD body directly |
| `gh issue comment -b "..."` | Append comment entry to `## Comments` in story MD |
| `gh issue close` | Set `**Status:** done` — no separate close action |
| `gh pr create` | Create review-record MD; commit to story branch |
| `gh pr diff` | `git diff sprint-N-dev...story/<branch> ` |
| `gh pr comment -b "..."` | Append to `## Comments` in story MD or review-record MD |
| `gh pr merge` | `git checkout sprint-N-dev && git merge story/<branch> --no-ff` |
| `git push origin --delete <branch>` | `git branch -d <branch>` (local delete only) |
| `git pull origin <target>` | Not needed — no remote sync |
| `gh label list \| grep "sprint-"` | Glob `docs/stories/*.md`, collect unique `**Sprint:**` values |
| CI run URL in PR | Not required — CI gate skipped in strict mode |
| `gh issue create` | Increment counter, write story MD |
| `Agent: <message>` commit prefix | **Never use** — see `## Commit Message Format` above for the correct format |
| `git add .claude/agents/...` | **Never do this** — entire `.claude/agents/` is gitignored |
| Commit memory/working-record/docs | **Never commit agent files** — they are local-only by design |
