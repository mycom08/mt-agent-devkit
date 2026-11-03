---
name: project-docs
description: Project documents for every role - where a document goes (the document index), Title_Case_With_Underscores naming and purpose-based file names. Load before creating, moving or renaming a document or file.
---

# Project Docs

**Requires:** none

## Placement

1. Look up the path in `.mt-agent-devkit/context/Document_Index.md`, the single document path list (planning documents included), and place the document in that folder.
2. Feature technical docs go under `docs/feature/<Feature>/` when the assignment names a feature, otherwise under `docs/`.
3. Context-anchoring notes go under `docs/technical/` or `docs/feature/<feature_name>/questions/`.
4. When you add, move or remove a document, update `Document_Index.md` in the same change.

## Naming

- Use `Title_Case_With_Underscores` for every document file name, and for workflow and rules files (`Sprint_Workflow.md`, `Agent_Common_Bootstrap.md`).
- Name a file after its primary purpose. No generic names.
- Template files under `.claude/agents/templates/` follow `change-metadata`.
