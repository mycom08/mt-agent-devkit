---
name: clean-code
description: Clean code rules - names, functions, comments, error handling, unit tests and simple design. Load before writing code and when reviewing source or script changes.
---

# Clean Code

**Requires:** none

**Applies to:** a Developer before writing source code; a reviewer (TL, or Dev as peer reviewer) during code review.
**Skip for:** documentation-only, API spec, Dockerfile, docker-compose, migration SQL, `.github/workflows/` CI YAML or config-only stories.
**Clean Code or refactor stories** (title or scope contains "Clean Code", "refactor" or "violation"): read this skill in full before touching any file, whatever the violation labels suggest.

## 1. Project Standards

- **Development Standard:** code follows the project Development Standard; read `docs/wiki/Development_Standards.md` when a convention question is not covered here.
- **Source file names:** name a file after its primary interface, struct or responsibility, in the project's naming convention (`rule_evaluator`, `condition_parser`, `policy_validator`, `auth_errors`). Never generic names: `utils`, `helpers`, `types`, `errors`, `interface`.
- **Shared helper scope:** before introducing or changing a helper used by more than one handler or module, identify every caller. If the change alters behavior for existing callers (stricter validation, a new required parameter), document the blast radius in the PR description and confirm with TL first.
- **Caller trace:** before changing a function or method signature, return type or type name, or extracting a concrete type into an interface, trace every caller (`grep -rn "FuncName" .`), list the affected call sites in the PR description and update every one.

## 2. Names and Functions

- **Intention-revealing names** say why a thing exists, what it does and how it is used; no disinformation, no number series (`a1`, `a2`), no noise words (`Info`, `Data`, `Object`).
- A function does **one thing**, has **no side effects** and no output arguments, and reads top-down one abstraction level at a time. Make it work first, cover it with tests, then refactor toward these rules.

## 3. Comments

- Prefer a better name or an extracted function over a comment. Acceptable: legal notices, intent (*why*), clarification, warning of consequences, `TODO`, public API docs.
- Avoid: redundant, misleading, mandated, journal or noise comments, closing-brace comments and commented-out code (Git keeps it).

## 4. Objects, Errors and Boundaries

- Objects hide data behind behavior; data structures expose data. Avoid hybrids; follow the Law of Demeter.
- Use exceptions, not error codes; extract `try/catch` bodies; give each exception enough context; never return or pass null. Shell scripts check critical exit codes and fail fast with clear messages.
- Wrap third-party APIs behind your own interface; keep vendor references in as few places as possible; explore them with learning tests.

## 5. Unit Tests

- Test code is as clean as production code: Arrange-Act-Assert, one concept per test, **F.I.R.S.T** (Fast · Independent · Repeatable · Self-Validating · Timely).

## 6. Classes, Systems and Simple Design

- Classes are small, single-responsibility and cohesive, and depend on abstractions. Separate construction from use; grow the architecture incrementally.
- Simple design, highest priority first: **runs all tests**, **no duplication**, **expressive**, **minimal** classes and methods.
