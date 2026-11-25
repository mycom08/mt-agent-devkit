---
name: qa-test-docs
description: Test strategy and test design document formats - required sections, the test case table, when a detailed design is mandatory and who approves. Load before writing or reviewing a test strategy or test design.
---

# QA Test Documents

**Requires:** `qa-core`, `gate-verdict` (header and approval), `project-docs` (location and naming)

Feature-level documents. The per-story test scenario document stays with `qa-testing`.

## 1. What to Write

- **Test strategy:** always.
- **Test design:** mandatory for nontrivial behavior, security or data integrity, integration, regression fixes, and ambiguous or risky paths. A mechanical documentation-only change may use the strategy or a checklist instead; state why it applies under `Test Design Decision`.

## 2. Test Strategy Format

```markdown
# TEST-STRATEGY: <feature>
Status: Draft
Approved-by:
Approved-at:

## Scope and Risks
In scope, out of scope; each risk (`R-1`) with likelihood, impact and mitigation.
## Test Levels and Types
What is tested at unit, integration, end-to-end and non-functional level, and why.
## Environment, Data and Isolation
Environments, test data source, setup and cleanup, isolation between runs and users.
## Coverage and Traceability
| AC / Risk | Level | Design or checklist |
## Entry and Exit Criteria
Conditions to start; pass conditions, allowed open defects.
## Evidence Responsibilities
Who produces which evidence, and where it is kept.
## Test Design Decision
Per spec: `required` or `not required`, with the reason.
```

## 3. Test Design Format

```markdown
# TEST-DESIGN-NNN: <spec title>
Status: Draft
Approved-by:
Approved-at:

| Case ID | Linked AC / Risk | Preconditions and data | Steps | Expected result | Evidence |
|---|---|---|---|---|---|
| TC-001 | SPEC-001 AC-1 | <state, input data> | 1. <action> | <observable result> | <test name, log or screenshot> |
```

- Every linked AC and high risk has at least one case; cover the happy path, errors and edge cases.
- Expected results are observable and decide pass or fail; "works correctly" is not one.
- A case ID is never reused.

## 4. Approval

QA authors. TL approves technical coverage and PO confirms scope; the document is `Approved` only after both (`gate-verdict`).
