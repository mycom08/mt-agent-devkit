---
name: po-plan-docs
description: Product Owner plan documents - committing and pushing each plan-file update right away in github mode; placement and naming come from project-docs.
---

# PO Plan Docs

**Requires:** `po-core`, `project-docs` (placement and naming of every plan document)

## Plan Commit (mandatory after any plan update)

Applies after creating or updating any project plan file: Sprint Overviews, Product Backlog, Implementation Roadmap, or any file under `docs/feature/<feature_name>/plan/`.

**GitHub mode:**

- Commit message: `Agent: <short description>`, total length under 50 characters (e.g. `Agent: Update sprint 3 overview`).
- Commit each plan file update as soon as it is written; do not batch.
- Push before continuing.

**Strict mode:** plan files live under `{RUNTIME_ROOT}/docs/`, which is gitignored. Never `git add` anything under the runtime root; write the file and continue.

> **Gate (github mode only):** never leave plan file changes uncommitted while continuing other work.
