# Clean Code Rules

**Applies to:** Developer (before writing scripts or structured content), Technical Lead (during code review)  
**Skip for:** markdown template files, workflow instruction files, `.github/workflows/` CI YAML, documentation-only stories

---

## 1. Meaningful Names

### Use Intention-Revealing Names
- A name should tell you *why* it exists, *what* it does, and *how* it is used.
- If a name requires a comment, the name does not reveal its intent.

### Avoid Disinformation
- Do not use names whose common meaning conflicts with intent.
- Avoid names that differ only subtly.

### Make Meaningful Distinctions
- Number-series naming (`a1`, `a2`) is noninformative — avoid it.
- Noise words (`Info`, `Data`, `Object`) add nothing.

---

## 2. Functions

### Do One Thing
- A function should do one thing, do it well, do it only.

### Have No Side Effects
- A function should do exactly what its name says — nothing else.

### Error Handling
- Prefer exceptions over returning error codes.
- Extract `try/catch` bodies into their own functions.

---

## 3. Code Comments

- Avoid comments where possible — they become misinformation over time.
- If a block needs a comment to explain what it does, extract it into a well-named function instead.

### Good Comments (acceptable)
- **Explanation of intent** — explains *why* the code is written this way, not *what* it does.
- **Warning of consequences** — warns about a non-obvious constraint.
- **TODO comments** — marks known incomplete work.

### Bad Comments (avoid)
- **Redundant comments** — restates what the code already clearly says.
- **Commented-out code** — delete it; Git will preserve it if needed.
- **Journal comments** — changelog entries in code; use Git history instead.

---

## 4. Error Handling (shell scripts)

- Always check exit codes of critical commands in shell scripts.
- Use `set -e` or explicit exit code checks to fail fast on errors.
- Provide clear error messages that identify the source of failure.

---

## 7. Unit Tests

- Tests are what make code safely changeable. Without tests, every change is a potential bug.
- Clean tests are readable above all else.
- **F.I.R.S.T:** Fast · Independent · Repeatable · Self-Validating · Timely

---

## 10. Simple Design Rules

*(Priority order — highest to lowest)*

1. **Runs All Tests** — a script that can't be verified shouldn't be merged.
2. **No Duplication** — duplication is the primary enemy of good design.
3. **Expressive** — code should clearly express the author's intent.
4. **Minimal** — don't over-engineer; keep counts low.

---

## Version

**Version:** 1.1 — "Skip for" list now explicitly names `.github/workflows/` CI YAML  
**Previous:** 1.0 — Initial devkit-specific version (simplified for Markdown/shell project)  
**Created:** 2026-06-16
