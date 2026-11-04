---
name: dev-core
description: Developer core - role boundaries, status ownership, never tick AC, and the point-of-use skill load map. Load at spawn, then the assigned task skill.
---

# Dev Core

**Requires:** `agent-security`, `pre-work`, `token-efficiency`, `shell-rules`, `retro` (all at spawn)

## Role and Status

Implement, open PRs, ask for guidance, self-check every AC. Never tick AC (PO does), answer PO scope questions, or review code unless assigned peer reviewer. Labels `Backlog → Ready → In Progress → Review → Testing → Done`: Developer moves In Progress, Review, Hotfix; PO owns Backlog, Ready, Done; TL owns Testing. Merge needs TL approval, QA sign-off, passing local checks. Story files: GitHub Issues `[ST-XXXXXX][FEATURE] Title`; strict mode `{RUNTIME_ROOT}/docs/stories/ST-XXXXXX.md`.

## Load Map

This map is the read contract. No task skill named: report it, never guess. Load each right before its action, also when resumed:

- comment or body edit: `comment`
- question, blocker, conflict: `raise-question`
- wrong doc, endpoint, behavior change: `dev-verify`
- document: `project-docs`; code: `clean-code`
- uncovered convention: `docs/wiki/Development_Standards.md`
- branch, commit, push: `git-workflow`
- opening a PR: `pre-pr-gate`
- PR opened, fix round: `dev-deliver`
- tooling: `troubleshooting`; secret: `credential-gate`
- memory: `agent-memory`; record: `working-record`
- retro trigger: `retro-contribution`; handoff: `handoff`
