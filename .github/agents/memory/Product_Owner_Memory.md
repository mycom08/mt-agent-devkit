# Product_Owner_Memory

## Stored Facts

### Fact 1
- **Fact:** For OpenAPI contracts, symbolic ABAC operators should stay on the wire but be modeled with a tool-safe string pattern instead of a literal special-character enum when needed for Swagger compatibility.
- **Source:** `.github/agents/context/PROJECT_PRIMING.md` section 4.2 API Spec Standard; `docs/feature/Attribute_Based_Access_Control-ABAC/stories/D1_ABAC_Policy_API_Contract.md`
- **Reason:** This avoids reopening approved contracts for tooling issues and helps future PO reviews distinguish compatibility corrections from real scope changes.

### Fact 2
- **Fact:** Phase 1 D.2 must preserve existing `/api/resources/access/check` clients and explicitly document how any new `/api/v1/check` contract rolls out without breaking the legacy wire shape.
- **Source:** `docs/feature/Attribute_Based_Access_Control-ABAC/stories/D2_Check_Endpoint_Extension_Contract.md`
- **Reason:** Backward compatibility is a release-gate requirement for ABAC Phase 1, so future PO reviews need this preserved as a standing scope boundary.

### Fact 3
- **Fact:** On Windows/PowerShell, always use `--body-file` with a temp file (`GetTempFileName` + `WriteAllText` UTF-8) for `gh issue edit/create/comment`. Never use `--body "..."` with inline backtick-containing or multi-line text — PowerShell treats `` `r `` as a carriage return, silently corrupting Markdown content.
- **Source:** `.github/agents/rules/STORY_STANDARD.md` §15 (added 2026-05-13); discovered during ST-000020 Issue #65 AC body edit.
- **Reason:** Recurring trap for all agents on this Windows repo. Prevents silent content corruption when editing story bodies or posting comments with inline code fences or AC checkboxes.
