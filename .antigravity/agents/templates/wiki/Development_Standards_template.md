# Development Standards

**Purpose:** Project-specific development rules for {{PROJECT_NAME}}  
**Audience:** Developer, Technical Lead  
**Last Updated:** {{DATE}}

> For language conventions, see `{{LANGUAGE}}_Style_Guide.md`.  
> For PR/review checklists, see `Code_Review_Checklist.md`.

---

## 1. Git Branching Standard

**Branch Naming:**

```
{{BRANCH_NAMING_FORMAT}}
```

**Rules:**
- Include story ID for traceability
- Use lowercase with hyphens only
- Keep total length ≤ 60 characters

**Commit Message Format:**

```
{{COMMIT_FORMAT}}
```

**Commit Types:**

| Type | Use when |
|------|----------|
| `feat` | Introducing a new feature |
| `fix` | Fixing a bug |
| `docs` | Documentation only changes |
| `refactor` | Code restructure with no behavior change |
| `test` | Adding or updating tests |
| `chore` | Maintenance (deps, tooling, CI) |

**Rules:**
- Subject: imperative mood — `Add …`, `Fix …`, `Remove …`
- Subject length: ≤ 50 characters
- Body: explain *why* the change is needed; wrap at 72 characters

---

## 2. Testing Standards

### Workflow

```
1. Write failing test → 2. Minimal code to pass → 3. Refactor → 4. Repeat
```

### Test Placement

{{TEST_FILE_PLACEMENT}}

### Naming

{{TEST_NAMING_CONVENTION}}

### Coverage

- **Minimum:** {{COVERAGE_MINIMUM}}
- **Run:** `{{COVERAGE_COMMAND}}`

---

## 3. Error Handling

{{ERROR_HANDLING_STANDARDS}}

---

## 4. Linting & Formatting

**Required before every commit:**

```
{{LINT_FORMAT_COMMANDS}}
```

---

## 5. File Naming

{{FILE_NAMING_STANDARDS}}

---

## 6. File Structure

```
{{PROJECT_FILE_STRUCTURE}}
```

---

## 7. Logging

{{LOGGING_STANDARDS}}

---

## 8. Backward Compatibility

{{BACKWARD_COMPATIBILITY_RULES}}

---

**Document Version:** 1.0  
**Last Updated:** {{DATE}}  
**Owner:** Technical Lead
