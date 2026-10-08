# Multi-Provider Harness — Provider Architecture

**Feature:** Multi-Provider Harness (`multi-provider-harness`)  
**Date:** 2026-10-07  
**Status:** Agreed direction; implementation pending  
**Scope:** Two-phase migration for Claude, Antigravity, and Codex

## 1. Decisions

The canonical shared harness lives in `.mt-agent-devkit/`. Provider-specific harness files remain in `.claude/`, `.antigravity/`, and `.codex/`.

Claude's current harness is the migration baseline for shared rules, section order, bootstrap/on-demand placement, wording, and routing. Editorial and organizational differences in the Antigravity copy do not require independent reconciliation. Preserve the safety, authority, verification, and independent TL/QA gates in that baseline.

Extract provider-specific execution behavior rather than applying Claude runtime instructions to every provider. An instruction combining a workflow obligation and runtime mechanics must be split into a shared requirement and an adapter procedure. Provider capability claims require evidence; an unavailable capability is reported as unsupported or blocked, never silently substituted.

Migrate this devkit's own harness first. Distributable templates and target-project installation/update behavior change only in Phase 2. Parallel tool execution optimization and its benchmark remain deferred; this migration does not claim token savings.

## 2. Ownership and Layout

Proposed shared layout:

```text
.mt-agent-devkit/
  instructions/    # Shared role responsibilities and completion requirements
  rules/           # Shared rules with Claude's bootstrap/on-demand organization
  workflows/       # Shared stages, dependencies, and verification gates
  context/         # Project context and document routing
  contracts/       # Provider adapter, handoff, and capability contracts
  scripts/         # Helpers whose behavior is provider-independent

.claude/           # Claude discovery files, configuration, and adapter
.antigravity/      # Antigravity discovery files, configuration, and adapter
.codex/            # Codex discovery files, configuration, and adapter
```

Native provider discovery requirements determine adapter filenames and entrypoint locations. Root entrypoints such as `CLAUDE.md` and `AGENTS.md` route to shared content and the selected adapter; directory names alone do not establish provider discovery. Define how an AGENTS.md consumer selects Codex versus Antigravity without loading contradictory adapters.

| Shared owner | Provider adapter owner |
|---|---|
| Role authority, acceptance criteria, review and merge gates | Agent spawning, messaging, lifecycle, and completion signals |
| Workflow stages and dependency ordering | Native session identifiers, resume/expiry handling |
| Required evidence and handoff semantics | Model/effort selection and runtime configuration |
| Safety and permission requirements | Tool invocation and permission/sandbox mechanisms |
| CI completion requirement and failure outcomes | Foreground/background waiting and wakeup support |
| Telemetry fields and privacy requirements | Runtime transcript discovery and usage extraction |
| Project context and canonical document locations | Native skill/agent discovery locations |

Runtime memory, working records, retrospectives, telemetry, and pipeline state are separate from reusable harness sources. Preserve existing provider paths and lifecycles: records, memory, retro, reports, tmp and agent progress remain under each provider folder. Provider harness configuration supplies concrete bindings; no normal state migration to per-run storage is in scope. Disposable validation fixtures may remain run-isolated. Define ownership and collision prevention explicitly; do not merge provider histories or commit runtime state as product content.

Shared rules have one editable authoritative copy. Provider wrappers may reference or load that copy; generated discovery artifacts must identify their source and have a regeneration procedure. Do not retain independent editable mirrors.

## 3. Verification Basis

The local Claude/Antigravity comparison found matching rules after provider-path substitutions, as well as runtime-specific model assignments and `agentId` versus `conversationId` session handling. Claude's TL review rules are on-demand while Antigravity's are in bootstrap; use Claude's organization. Other branch/state and wording differences also take Claude as the baseline, subject to preserving applicable safety gates.

Provider-specific candidates requiring extraction include agent/session APIs, model frontmatter, shell/tool assumptions, CI task completion, transcript lookup, and provider discovery paths. The Antigravity sync reference also documents older behavior; it is not the Phase 2 specification. No `.codex/` harness exists in the inspected checkout.

The implementation inventory must record the actual source revision. The earlier comparison was from a preserved feature checkout, not proof of parity at current main. Re-inventory the verified implementation base before moving files.

## 4. Phase 1 — This Devkit's Harness

### Outcome

Claude, Antigravity, and Codex use one shared internal harness, with explicit adapters for their execution mechanics.

### Work

1. Inventory internal instructions, rules, workflows, context, helpers, skills, and entrypoints. Classify each as shared, provider-specific, runtime state, or reference-only. Record source paths, revision, destination, and consumers.
2. Establish the adapter contract: provider selection, supported capabilities, model policy, session identity, spawn/resume/completion, permissions, CI waits, telemetry, and failure behavior.
3. Move one coherent story-execution path first, using Claude's shared content. Validate it before migrating the remaining internal harness in bounded batches.
4. Add Codex's adapter and update Claude/Antigravity adapters, entrypoints, internal path references, helper callers, and document indexes. Keep native discovery wrappers where required.
5. Remove redundant editable internal copies only after consumer references and checks pass. Preserve runtime state and provide a migration map and Git-based rollback instructions.
6. Extend relevant validation/CI coverage to shared sources and adapters, including dangling references and incorrect provider selection.

### Acceptance and Evidence

- Inventory accounts for every in-scope internal file; exclusions have a reason.
- Shared procedures resolve to one owner and follow the Claude baseline.
- Each provider loads the selected adapter plus the same shared workflow obligations without loading another provider's execution instructions.
- Routing and adapter checks cover fresh spawn, resume/expired session, review/QA handoff, permissions, pending/failed CI, and completion without an open-ended wait.
- Retained, sanitized evidence demonstrates one complete internal story path for each provider, with independent TL/QA gates. A missing runtime leaves the corresponding behavioral criterion unverified.
- Reference/static checks pass, and no existing runtime state is lost or committed.
- Templates, target-project installers/update logic, release version files, and template change metadata remain unchanged in this phase.

## 5. Phase 2 — Templates and Target-Project Lifecycle

### Dependency and Outcome

Start after Phase 1's layout and adapter contract are accepted. Fresh and existing target projects receive `.mt-agent-devkit/` shared content plus the selected provider adapters through init, update, and sync operations.

### Work

1. Adapt the distributable source templates to emit the accepted shared/provider layout. The source-template storage location is an implementation decision; consumer output must obey the new ownership contract.
2. Update init project, update project, sync devkit, and build software integration, including PowerShell/Bash scaffold helpers, fetch mappings, file lists, substitutions, native discovery artifacts, and supported GitHub/strict modes.
3. Specify legacy migration: detection, preservation/backup of project-customized content and runtime state, path rewrites, conflict handling, removal of obsolete managed files, and rollback. Do not overwrite divergent user content silently.
4. Make updates idempotent and release-tag-pinned. Keep provider adapters distinct, including projects configured for multiple providers; applying one provider must not damage another.
5. Extend deployment, migration, reference, and lifecycle checks. Update user documentation and the existing unreleased change metadata through the established release-owned version process; never manually bump VERSION or version.txt.

### Acceptance and Evidence

- Fresh install, local update, and release-pinned sync produce the same expected shared/provider file ownership for each supported provider and mode.
- A repeat operation has no unintended content changes, duplicate rules, or stale managed references.
- Legacy fixtures cover customized files, interrupted migration, runtime state preservation, and actionable conflicts/rollback.
- Provider selection and native discovery load the right adapter; multi-provider fixtures show no cross-provider overwrite.
- Static/template checks, PowerShell/Bash checks where applicable, deployment tests, and representative installed behavior pass. Unavailable runtime checks are reported unverified.
- Distributed additions/modifications/migrations are discoverable through release metadata; a target project can update from an older supported release without reinstalling manually.

## 6. Story Tracking and Boundaries

| Phase | Story | Dependency |
|---|---|---|
| 1 | [#220](https://github.com/mycom08/mt-agent-devkit/issues/220) | None; verify current base and refine adapter contract |
| 2 | [#221](https://github.com/mycom08/mt-agent-devkit/issues/221) | Phase 1 accepted |

Both stories begin in backlog. They implement architecture migration, not FIX-02, its G2/G5/G6 benchmark, or unrelated enhancement stories. Existing enhancements must be retargeted to the canonical shared owner once Phase 1 lands; do not duplicate their acceptance scope here.

## 7. Related Documents

- [Stage-Specific Read Profiles Proposal](../../reviews/Stage_Specific_Read_Profiles_Proposal.md)
- [Stage Profile Proposal Feedback](https://github.com/mycom08/mt-agent-devkit/blob/main/docs/reviews/Stage_Profile_Proposal_Feedback.md)
- [Agent Workflow Test Strategy](../../Agent_Workflow_Test_Strategy.md)
- [Template Test Strategy](../../Template_Test_Strategy.md)

The profile proposal provides context; this migration preserves Claude's current tiering rather than implementing the proposed full profile split.
