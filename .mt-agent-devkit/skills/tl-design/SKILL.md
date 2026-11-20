---
name: tl-design
description: Technical Lead design standards - how to evaluate approaches and make recommendations, template and workflow design rules, key design questions and the non-negotiable constraints. Load before a design, recommendation or design review.
---

# TL Design

**Requires:** `change-metadata` (`changes.json` scope, entry format and `_template` naming)

## 1. Evaluating Approaches

- Always consider backward compatibility with existing target projects, template clarity for agents, and maintainability of the devkit.
- Reference existing patterns in `.claude/agents/templates/` and `.mt-agent-devkit/workflows/commands/`.
- Focus on current sprint scope; do not over-engineer for future features.

## 2. Recommendations

- Give the rationale: why this choice over the alternatives.
- Assess trade-offs: what is gained, what is lost.
- Flag backward-compatibility and migration risks early.

## 3. Template and Workflow Design

- Every new template section has a clear purpose; add no section agents will not use.
- Every new workflow stage has a clear completion signal.
- Update `changes.json` when template files change so `sync devkit` applies targeted updates (`change-metadata`).

## 4. Key Design Questions

For any devkit change, answer:

1. Does it need a `changes.json` entry for `sync devkit` to pick it up?
2. Is it backward compatible, and will `sync devkit` migrate existing target projects?
3. Are there placeholder substitutions `init project` must apply?
4. Does it affect both GitHub mode and strict mode, or only one?

## 5. Constraints (non-negotiable)

- No breaking change to template file names without a migration path.
- Keep the `_template` suffix on every file under `.claude/agents/templates/` (`change-metadata` section 3).
- Fold `changes.json` into the current `-SNAPSHOT` key named by the root `VERSION` file. `.github/workflows/release.yml` owns `VERSION` end to end: never hand-edit it, and never let a PR add a new `changes.json` version key.
