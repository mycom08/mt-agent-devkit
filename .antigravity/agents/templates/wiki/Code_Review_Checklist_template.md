# Code Review Checklist

**Purpose:** TL review criteria and developer pre-PR checklist  
**Audience:** Technical Lead (reviewer), Developer (self-check)  
**Last Updated:** {{DATE}}

---

## Developer Pre-PR Checklist

Before creating a PR, verify all items:

### Code Quality

{{CODE_QUALITY_CHECKLIST}}

### Security

{{SECURITY_CHECKLIST}}

### Project Conventions

{{CONVENTIONS_CHECKLIST}}

### Story Workflow

- [ ] All AC ticked `[x]` in the story issue
- [ ] Story status label updated to `status:review`
- [ ] PR title format: `[ST-XXXXXX] Story title`
- [ ] Local tests pass: `{{TEST_RUN_COMMAND}}`
- [ ] Service/app starts cleanly: `{{START_COMMAND}}`

---

## TL Review Criteria

### Must Pass (Reject if violated)

{{TL_MUST_PASS}}

### Should Fix (Request changes)

{{TL_SHOULD_FIX}}

### May Suggest (Non-blocking)

{{TL_MAY_SUGGEST}}

---

## Error Response Format

{{ERROR_RESPONSE_FORMAT}}

---

**Version:** 1.0  
**Created:** {{DATE}}
