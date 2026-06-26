# Testing Guidelines

**Project:** {{PROJECT_NAME}}  
**Last Updated:** {{DATE}}

---

## Test File Organization

{{TEST_FILE_ORGANIZATION}}

### File Naming Convention

{{TEST_FILE_NAMING_CONVENTION}}

---

## Unit Tests

### Placement

{{UNIT_TEST_PLACEMENT}}

### Naming Convention

{{UNIT_TEST_NAMING}}

### Test Structure

{{UNIT_TEST_STRUCTURE}}

### Coverage

- **Minimum:** {{COVERAGE_MINIMUM}}
- **Target:** {{COVERAGE_TARGET}}
- **Check:** `{{COVERAGE_COMMAND}}`

### Required Edge Cases

For every function, test: happy path, error cases (invalid input, missing fields), and edge cases (empty values, boundary conditions).

---

## Integration Tests

### Placement

{{INTEGRATION_TEST_PLACEMENT}}

### Running Integration Tests

{{INTEGRATION_TEST_COMMANDS}}

### Test Data Rules

- Keep test scripts idempotent (safe to run multiple times)
- Clean up test data after verification
- Do not leave orphaned test records in the database or state stores

---

## Running Tests

{{TEST_RUN_COMMANDS}}

---

## Automation Suite

{{AUTOMATION_SUITE}}

---

**Last Updated:** {{DATE}}  
**Established by:** Developer
