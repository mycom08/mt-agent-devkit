# Technical_Lead_Memory

## Stored Facts

### Fact 1
- **Fact:** The canonical shared ABAC OpenAPI contract is `docs/api/ABAC_API.yaml`; story files define requirements and carry comment-thread review history, not the final implementation contract.
- **Source:** `.github/agents/context/PROJECT_PRIMING.md`, `docs/feature/Attribute_Based_Access_Control-ABAC/stories/D1_ABAC_Policy_API_Contract.md`
- **Reason:** This prevents future design or implementation work from drifting into story prose when the actual source of truth is the shared OpenAPI artifact.

### Fact 2
- **Fact:** Phase 1 preserves `POST /api/resources/access/check` unchanged and introduces `/api/v1/check` as an additive ABAC-capable contract.
- **Source:** `docs/feature/Attribute_Based_Access_Control-ABAC/stories/D2_Check_Endpoint_Extension_Contract.md`, `docs/api/ABAC_API.yaml`
- **Reason:** This is a durable compatibility boundary that affects future API design, implementation, and review decisions for the ABAC rollout.

### Fact 3
- **Fact:** Technical Lead approval of a design/story review does not by itself justify marking story acceptance, task, or delivery-completion checklists as done unless the underlying work is actually complete.
- **Source:** `docs/feature/Attribute_Based_Access_Control-ABAC/stories/D2_Check_Endpoint_Extension_Contract.md`, working-session correction on 2026-04-13
- **Reason:** This keeps story state accurate by separating review approval from implementation, merge, and delivery completion, which prevents misleading progress tracking in future story updates.

### Fact 4
- **Fact:** API specs must be validated in Swagger Editor and with `swagger-cli validate <spec-file>` before being sent for review.
- **Source:** `.github/agents/context/PROJECT_PRIMING.md`, `docs/wiki/Development_Standards.md`
- **Reason:** This gives the team one explicit manual and command-line validation rule for OpenAPI review readiness, reducing avoidable review churn caused by invalid specs.

### Fact 5
- **Fact:** Feature branches must use format: `feature/{feature-name}/{story-id}-kebab-case-title`. All branches must include the story ID for traceability; commit messages include `Story: {STORY_ID}` footer.
- **Source:** `docs/wiki/Development_Standards.md` (established pattern for ABAC, generalizable across features)
- **Reason:** Story IDs in branch names provide traceability, make branches discoverable by story and team, ensure consistency across distributed development, and integrate cleanly with project tracking systems (Jira, Azure DevOps).

### Fact 6
- **Fact:** Default decision when no ABAC rules match: no policies exist → ALLOW (backward compat), policies exist but none match → DENY (fail-secure). Resolved by PO Option B sign-off on 2026-04-20.
- **Source:** Issue #5 comment thread, PO sign-off 2026-04-20
- **Reason:** Documents the resolved decision for ST-000008 and future stories that depend on evaluation default behavior.

### Fact 7
- **Fact:** Code review changes-requested comments belong on the PR only, not on the story issue. Story issue comments are for story-level discussion (blockers, summaries, questions). PR comments are for code-specific review feedback.
- **Source:** User correction 2026-04-24
- **Reason:** Keeps review feedback co-located with the code diff, avoids cluttering the story issue with code-level details, and follows the project's separation between story discussion and PR review workflows.

