---
name: tl-design
description: Technical Lead design standards - how to evaluate approaches and make recommendations, template and workflow design rules, key design questions and the non-negotiable constraints. Load before a design, recommendation or design review.
---

# TL Design

**Requires:** none

## 1. Evaluating Approaches

- Consider backward compatibility, performance, security and team capability.
- Reference existing patterns in the codebase (stack in `Project_Priming.md`, conventions in `docs/wiki/Development_Standards.md`).
- Focus on the current phase MVP scope; do not over-engineer for future phases.

## 2. Recommendations

- Give the rationale: why this choice over the alternatives.
- Assess trade-offs: what is gained, what is lost.
- Include the implementation timeline and critical path.
- Flag security and performance concerns early.

## 3. API Design

- Follow the existing API versioning pattern.
- Every endpoint has request and response schemas with examples.
- Specify status codes, validation rules and error handling.
- Ensure data isolation (tenant or access-scope boundaries in all queries).
- Keep existing public endpoints backward compatible.

## 4. Key Design Questions

For any feature change, address:

1. How to test the feature's behavior in isolation?
2. Input validation and error handling approach?
3. Audit trail and observability requirements?
4. Migration and coexistence with existing behavior?
5. Gradual rollout strategy, if applicable?
6. Performance impact of the change?

## 5. Constraints (non-negotiable)

- Stay within the language and database versions in `Project_Priming.md`.
- Maintain API stability.
- Keep request and response payloads manageable.
- Support the data isolation requirements.

## 6. Deliverables per Design Task

- Proposed architecture or system model.
- API contract changes with examples.
- Storage schema design.
- Implementation roadmap with risk assessment.
- Performance considerations and benchmarking approach.
