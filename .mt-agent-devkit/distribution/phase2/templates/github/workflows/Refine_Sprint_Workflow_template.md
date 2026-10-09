<!-- Shared logic: templates/shared/workflows/Refine_Sprint_Workflow_Shared_template.md -->

<!-- GitHub mode: sprint identification uses gh issue list with jq numeric sort (NOT gh label list). -->
<!-- Story fetch: gh issue list --label "sprint-N" --label "status:backlog" --state open -->
<!-- Questions posted as GitHub issue comments; PO updates issue body via --body-file. -->
<!-- Status promotion: remove status:backlog label, add status:ready label via gh CLI. -->
