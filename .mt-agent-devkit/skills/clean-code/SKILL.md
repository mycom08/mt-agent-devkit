---
name: clean-code
description: Clean code rules - names, functions, comments, error handling, unit tests and simple design. Load before writing code and when reviewing source or script changes.
---

# Clean Code

**Requires:** none

**Applies to:** a Developer before writing scripts or structured content; a reviewer (TL, or Dev as peer reviewer) checking source and script changes.
**Skip for:** Markdown template files, workflow instruction files, `.github/workflows/` CI YAML, documentation-only stories.

## 1. Meaningful Names

- **Intention-revealing:** a name says *why* it exists, *what* it does and *how* it is used. If it needs a comment, it does not reveal its intent.
- **No disinformation:** no names whose common meaning conflicts with intent, and no names that differ only subtly.
- **Meaningful distinctions:** no number series (`a1`, `a2`); no noise words (`Info`, `Data`, `Object`).

## 2. Functions

- **Do one thing**, do it well, do it only.
- **No side effects:** a function does exactly what its name says, nothing else.
- **Error handling:** prefer exceptions over returned error codes; extract `try/catch` bodies into their own functions.

## 3. Comments

- Avoid comments where possible; they become misinformation over time. If a block needs a comment to explain what it does, extract it into a well-named function.
- **Acceptable:** explanation of intent (*why*, not *what*), warning of a non-obvious consequence, `TODO` marking known incomplete work.
- **Avoid:** redundant comments restating the code, commented-out code (delete it; Git keeps it), journal or changelog comments (use Git history).

## 4. Shell Error Handling

- Always check exit codes of critical commands.
- Use `set -e` or explicit exit-code checks to fail fast.
- Give clear error messages that identify the source of the failure.

## 5. Unit Tests

- Tests are what make code safely changeable; without them every change is a potential bug.
- Clean tests are readable above all else.
- **F.I.R.S.T:** Fast · Independent · Repeatable · Self-Validating · Timely.

## 6. Simple Design (priority order, highest first)

1. **Runs all tests:** a script that cannot be verified is not merged.
2. **No duplication:** the primary enemy of good design.
3. **Expressive:** the code clearly states the author's intent.
4. **Minimal:** do not over-engineer; keep counts low.
