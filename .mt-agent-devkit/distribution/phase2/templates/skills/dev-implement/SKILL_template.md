---
name: dev-implement
description: Developer story implementation task - numbered pre-start steps (read the story and touched files, raise questions and wait, design-first rule, UI prototype reference), then start through branch preflight. Load at spawn for a story assignment.
---

# Dev Implement

**Requires:** `dev-core`, `raise-question` (questions), `git-workflow` (branch and status), `comment` (before any comment), `dev-verify` (touched endpoints)

Task skill for a story implementation spawn. Do the steps in order; none is optional.

## Before Starting a Story

1. **Read the story in full** before writing any code, whatever its status: User Story, every Acceptance Criterion, Technical Scope and every linked technical doc.
2. **Read every existing comment** on the GitHub Issue (strict mode: the story file's `## Comments`); PO and TL may already have added context.
3. **Read every existing file the story modifies or appends to.** Note stale placeholders, forward references and superseded instructions the change will make wrong, and fix them in this story, not as a separate task.
4. **Touched endpoints:** run `dev-verify` section 2 before writing code.
5. **Raise questions and wait:** `raise-question` section 2. Do not begin until every blocking question has a confirmed PO or TL answer.
6. **Design first** when the story is complex (8+ points, multiple layers, data model changes, third-party integration, security-sensitive logic, or a breaking API contract): post a design as an issue comment tagging TL (`Project_Priming.md` Design First). Proceed only after TL replies with the exact phrase **"Design approved"**.
7. **Standards before code:** source code changes load `clean-code`; log statements read `.mt-agent-devkit/rules/Logging_Standard.md`. Skip both for documentation, API spec, Dockerfile, docker-compose, migration SQL or config-only stories.
8. **UI prototype reference:** if this repo has (or is paired with) a `-ui-prototype` companion repo, read `.mt-agent-devkit/rules/UI_Prototype_Rules.md` before implementing any screen with a prototype counterpart; it governs what may and must not be reused.

## Start

9. Run branch preflight `create` from the immutable Base Branch and full Base/Remote Base SHAs, then move the story to `in-progress` and verify the branch (`git-workflow` section 1). A BLOCKED preflight stops for direction.
10. **Spec first:** when the story's **API Spec Reference** section names endpoints, update the API spec before any implementation code, run codegen immediately, and commit both as the first working commit on the branch.
11. Implement. Load each point-of-use skill in the `dev-core` load map right before its action, even if you read it earlier in the session.
12. A question that surfaces mid-implementation: `raise-question` section 3 (post the question, report, pause).
