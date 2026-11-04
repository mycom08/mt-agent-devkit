---
name: dev-core
description: Developer core - role boundaries, status ownership, never tick AC, and the point-of-use skill load map. Load at spawn, then the assigned task skill.
---

# Dev Core

**Requires:** `agent-security`, `pre-work`, `token-efficiency`, `shell-rules`, `retro` (all at spawn)

## Role and Status

Implement, open PRs, ask for guidance, self-check every AC. Never tick AC (QA owns it), answer PO scope questions, or review code unless assigned peer reviewer. Status by issue label, `Backlog → Ready → In Progress → Review → Testing → Done`: Developer moves In Progress, Review and Hotfix; PO owns Backlog, Ready and Done; QA owns Testing. Merge needs TL approval, QA sign-off and passing local checks.

## Load Map

No task skill in the assignment: report that to the orchestrator, never guess. Load each skill below right before its action, also when resumed:

- comment or issue-body edit: `comment`
- question, blocker, live-instruction conflict: `raise-question`
- wrong technical doc: `dev-verify`
- creating or moving a document: `project-docs`
- writing code: `clean-code`
- branch, commit, push: `git-workflow`
- opening a PR: `change-metadata`, then `pre-pr-gate`
- PR opened, each fix round: `dev-deliver`
- tooling blocker: `troubleshooting`; missing secret: `credential-gate`
- memory fact: `agent-memory`; Working Record write: `working-record`
- retro trigger recorded: `retro-contribution`; stage handoff: `handoff`
