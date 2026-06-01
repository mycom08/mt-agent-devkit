# QA Rules

**Applies to:** QA agent  
**Reference from:** `.github/agents/qa_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any testing or validation work:

1. **Read Project Priming** — `.github/agents/context/PROJECT_PRIMING.md`
2. **Read Story Standard** including §6 Role Boundaries — `.github/agents/rules/STORY_STANDARD.md`
3. **Read your Working Record** — `.github/agents/working-record/QA_Working_Record.md`
4. **Read the relevant GitHub Issues** — filter by `status:testing` label for the current task

---

## 2. Locating Work Before Testing

Before testing any story:

1. Open the GitHub Issue for the story
2. Find the linked PR in the issue body (Deliverables section) or in the issue's linked pull requests
3. **Test on the dev branch** — do not wait for the PR to be merged; testing happens before merge
4. If no PR is linked or the story is not in `status:testing`, comment in issue for Dev

---

## 3. Story Status & Acceptance Criteria

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- **Only QA ticks Acceptance Criteria** — do not mark AC complete if you are another role
- **Tick AC on the dev branch before the PR is merged** — QA sign-off is a merge gate
- Once all AC are checked and sign-off is complete, notify Dev to proceed with the merge
- Move story label to `status:done` after the PR is merged
- If AC cannot be validated (missing impl, env issue), post a blocker Comment and keep in `status:testing`

See `STORY_STANDARD.md` §4 for the full workflow and gate conditions.

---

## 4. Testing Rules

- Follow the testing guidelines in `docs/wiki/Testing_Guidelines.md`

**Before testing:**
- Always create a test scenario document first — do not begin testing without it
- Place it under `docs/feature/<feature_name>/test-scenarios/` using `Title_Case_With_Underscores`
- The scenario must cover: happy path, error cases, edge cases (empty values, invalid input, multi-tenant isolation)

**Integration tests:**
- Always check whether integration tests exist for the story
- If integration tests can be run, **they must be run** — no exceptions
- The only valid reasons to skip: the story is API-contract only, **or** TL has explicitly stated not to run them in a Story comment
- Record integration test results (pass/fail + evidence) as a Comment on the GitHub Issue

**API testing:**
- Test all API endpoints using `curl`
- When a story requires more than one curl call, create a shell script (`.sh`) to run them all
- Place the script under `tests/feature/<feature_name>/scripts/` using `Title_Case_With_Underscores` (e.g., `ST-XXXXXX_API_Test.sh`)
- The script must be runnable as-is — include base URL variable, required headers, and a clear echo label before each request

---

## 5. Document Placement

- Place all new documents in the correct feature-doc subfolder — see `PROJECT_PRIMING.md §4`
- Use `Title_Case_With_Underscores` for all document file names (e.g., `My_Technical_Document.md`)
- Test scenario docs go under `docs/feature/<feature_name>/test-scenarios/`

---

## 6. Story Comment

- Post QA findings, acceptance gaps, regression risks, and sign-off notes as **comments on the GitHub Issue**
- Reply in the same comment when retesting or validating the same issue
- Do not create standalone review-note files for normal story discussion
- See `PROJECT_PRIMING.md §13` for the full Comment format

---

## 9. Reporting & Blockers

- Keep working record updates short and fact-based (story IDs, test results, AC status)
- Post blockers immediately as a Comment on the GitHub Issue; tag Dev or TL as appropriate

---

## Version

**Version:** 1.2 — Added API testing rules: use curl, create .sh script for multiple tests  
**Previous:** 1.1 — QA tests on dev branch before merge; AC ticked before merge  
**Created:** 2026-05-01
