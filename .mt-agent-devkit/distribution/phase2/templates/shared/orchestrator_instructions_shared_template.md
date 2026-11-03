<!-- Included by: templates/github/orchestrator_instructions_template.md, templates/strict/orchestrator_instructions_template.md -->

<!-- SHARED-START -->
# Orchestrator Instructions

> Read by the orchestrator only — workflow routing, session management, and completion-report format for running this project's AI Scrum team. No spawned subagent needs this file: each spawn receives its own instruction/rules/memory paths directly in its prompt. Content every role needs (Mode, Agent File Integrity, PR Approval Rule) lives in `{{ROOT_FILE}}`. **Agent Roster also stays in `{{ROOT_FILE}}`, not here** — it is project-mutable (per-project instruction paths, lean prototype rosters) and must survive `sync devkit`/`update project`, unlike everything in this file, which is always devkit-verbatim.

---

## Orchestrator Startup — Security Baseline

At workflow start, before the first issue/PR read or GitHub mutation, load the `agent-security` skill: read `.mt-agent-devkit/skills/agent-security/SKILL.md` in full (by path when the provider has no verified native skill discovery). Per its part C, read `{{AGENT_DIR_PREFIX}}/agents/rules/Agent_Common_Shell_Safety.md` in full before the first shell write, Git operation or GitHub mutation. Record the load as `**Security Skill:** agent-security` in the workflow's pipeline state file when it keeps one; a resumed run re-reads the skill if its session no longer holds it. This is an orchestrator read, never a read-manifest entry: workers already receive parts A and B through the generated blocks in their Common file.

**PO execution setting (every workflow).** At workflow start, after the security load and before the first PO touchpoint, resolve `po_execution` once with `python .mt-agent-devkit/scripts/project_settings.py po_execution`. It reads the project-owned `.mt-agent-devkit/project_settings.json` (`init` creates it with `subagent`; `sync` never overwrites it). An absent file or key resolves to `subagent`; an unrecognised value resolves to `subagent` and the script reports it once on stderr: relay that report to the user and never guess the intended value. Pin the result as `**PO Execution:** <subagent | orchestrator>` in the workflow's pipeline state file when it keeps one. A resumed run uses its pinned value and never re-reads the setting, so a mid-sprint change never flips a run halfway. `subagent` (the default) spawns the Product Owner as before. `orchestrator` lets the orchestrator act as PO for the activities the workflows name, loading the same `po-*` skills and owning the PO record and memory for that activity. **Accepted trade-off:** in `orchestrator` mode one actor both merges and records acceptance. That is acceptable only because the per-AC evidence producer stays independent (QA, or a spawned PO when QA is the implementer), Plan Sprint always spawns a PO, and every scope change after Stage 1 starts (defer, split or any AC body edit) goes to the user. Opt in knowingly.

---

## PO Touchpoints by `PO Execution`

Every PO touchpoint routes on the pinned `PO Execution` value. `subagent` keeps today's behavior unchanged. Each workflow names its row at the touchpoint; this section is the single procedure those rows cite. The last column lists the skills an inline activity may need, not a bulk-load list: inline procedure step 1 loads each one at its point of use.

| Touchpoint | `subagent` | `orchestrator` | Skills an inline activity may need |
|---|---|---|---|
| Create Stories | Inline (already) | Inline | `po-core`, `po-write-story` |
| Plan Sprint Stages 1, 2, 4 | Spawn/resume `po_session` | **Spawn/resume (forced)** | none (the spawned PO loads `po-plan-sprint`) |
| Refine Sprint Stage 2 (after TL) | Spawn/resume | Inline; TL still answers first | `po-core`, `po-answer-questions`, `po-comment` (+ `po-write-story` when an AC changes) |
| Refine Sprint Stage 4 | Resume | Inline | `po-core`, `po-promote-ready` |
| Pipeline Stage 2: Developer question with owner PO (Mid-Implementation Consultation) | Spawn/resume | Inline | `po-core`, `po-answer-questions`, `po-comment` |
| Scope change after Stage 1 starts (defer, split or **any** AC body edit) | PO decides | **Escalate to the user** | none |
| Pipeline Stage 3, QA is the implementer | Spawn | **Spawn (forced)** | none (the spawned PO loads `po-validate-ac`) |
| Pipeline Stage 4 non-behavioral | Inline (already) | Inline (unchanged) | none |
| Pipeline Stage 4 behavioral | Spawn (`closure` policy) | Inline | `po-core`, `po-verify-close`, `po-comment` |
| Sprint Workflow next-story promotion | PO | Inline | `po-core`, `po-promote-ready` |

**Forced spawns.** Plan Sprint and Stage 3 with QA as the implementer spawn a Product Owner in both modes. Never run them inline: planning is not delegated, and with QA as the implementer the spawned PO is the only independent evidence producer, so inline validation would certify the orchestrator's own merge gate.

**Inline PO activity procedure.** For every inline row above:
1. **Skills, at the point of use.** Load each skill immediately before the action it governs, never all at the start of the activity: `po-core` when the activity starts; `po-answer-questions` before writing an answer; `po-comment` (with `comment`) before each post; `po-write-story` only when an AC or other body text is about to change; `po-promote-ready` before each promotion; `po-verify-close` before closure. Also load any skill a loaded skill's `**Requires:**` line names that is not already loaded. When other work has passed since a skill was read, read it again before its action. Read the canonical file `.mt-agent-devkit/skills/<name>/SKILL.md` in full; a provider without verified native skill discovery always reads that path (a skill directory does not prove discovery).
2. **Pipeline state.** When the workflow keeps a state file, set `po_session: inline` and append one entry to `**PO Skills:**` naming the activity and the skills loaded (e.g. `stage4-closure: po-core, po-verify-close, po-comment, comment`).
3. **PO memory.** At the run's first PO activity, read `{{AGENT_DIR_PREFIX}}/agents/memory/Product_Owner_Memory.md` in full and record `**PO Memory:** read` in the state file. Write durable facts in the PO format, `## Stored Facts`, per `Agent_Common_Read_On_Demand.md §1` (fetch that section before the first write).
4. **PO Working Record.** Update `{{AGENT_DIR_PREFIX}}/agents/working-record/Product_Owner_Working_Record.md` at the start and end of each inline activity, in the `Agent_Common_Bootstrap.md §1` format: one inline activity counts as one PO session (`po-core` rules). Stage 4 closure skips it, as a spawned closure PO does.
5. **Separate state.** The orchestrator's own Working Record and state stay unchanged: PO facts never go into orchestrator state, and orchestrator state never goes into PO records.
6. **Retro identity.** The completion identity's role is `Orchestrator`, the actual actor, per `Agent_Common_Bootstrap.md §7`. Never record an unspawned `Product_Owner` identity.
7. **Telemetry.** Write exactly one Schema v1 row per inline activity through `python .mt-agent-devkit/scripts/telemetry.py harness`: metadata `role: PO`, `session_mode: orchestrator_inline`, the orchestrator's model, and no `session_final_tokens`, so the row records `usage_source: unavailable`. `story_id` is the story served (the sprint label for a multi-story activity); `stage` names the activity and, for a repeated cycle, its number (e.g. `refine-stage2-c2`). Never extract, capture boundaries or estimate inline usage.
8. **Model.** Inline work runs on the orchestrator's model. The `closure` and `standard` policies apply only to spawns.

**Scope-change escalation (`orchestrator` mode).** Once a story's Stage 1 has started, a defer, a split or **any** AC body edit is never decided inline, whatever its direction and whoever proposes it (a worker, an inline PO answer or the orchestrator itself). The merging actor must not judge whether its own edit lowers the bar. Stop the story and run the Blocked Story Procedure in `Shared_Pipeline_Stages.md` addressed to the user: the comment (GitHub mode) or `## Comments` entry (strict mode) states the proposed change and the AC it affects, and the story takes the blocked status. Continue only after the user's decision is recorded on the story; then apply exactly that decision, following `Story_Standard.md §14` for a split. An inline answer that needs no scope change continues normally. Before Stage 1 (Create Stories, Refine Sprint) inline AC edits follow the skills as usual.

**Observation checks.** Where a check asks whether `po_session` was saved after a spawn, `po_session: inline` with a matching `PO Skills` entry satisfies it for an inline touchpoint in `orchestrator` mode. A forced spawn still needs its real session handle.

**Measuring the saving (R1).** Compare the modes only through orchestrator-plus-worker totals per story. After each story's Stage 4, in both modes, write one `Orchestrator` story-total row through `telemetry.py harness` (`role: Orchestrator`, `stage: story_total`, `session_mode: orchestrator_inline`), with `session_final_tokens` only when the harness reports the orchestrator's real count (`usage_source: harness_report`); otherwise the row is `unavailable`. Then run `python .mt-agent-devkit/scripts/telemetry.py compare --subagent <subagent-run.jsonl> --orchestrator <orchestrator-run.jsonl>`. A story without a harness-reported orchestrator total, or with a worker row lacking `session_final_tokens`, is reported as **unmeasured**, never estimated.

---

## Agent Session Management

The orchestrator tracks the `agentId` returned by every spawned agent. On loop-back, always prefer resuming over spawning:

| Situation | Action |
|---|---|
| Loop-back to a stage whose agent is still active | **Resume** — `SendMessage` to the saved `agentId` with the new feedback |
| Loop-back but session has expired or ID is unavailable | **Spawn** — new `Agent` call with a fully self-contained prompt |
| First entry to any stage | **Spawn** — new `Agent` call |

Resuming keeps the agent's full prior context so it can act on feedback immediately without re-reading everything from scratch.

**Session ID update rule:** Only overwrite a saved session ID when a **new agent is spawned**. When resuming via `SendMessage`, do not change the stored ID — the interaction does not produce a new session.

---

## Agent Completion Reports

When any spawned agent completes and returns to the orchestrator, it **must** limit its summary to **5 bullets max**:

1. Story ID + what was done (e.g., "ST-000025 — PR #86 opened")
2. Key outcome (approved / blocked / passed / failed)
3. PR or commit reference if applicable
4. Any blockers or open items
5. Next action required (if any)

Detailed activity logs go in the agent's Working Record — not in the orchestrator message. The orchestrator relays a brief status update to the user after each stage.

---

## Workflows

Read the linked file before executing any workflow.

| Trigger | Workflow File |
|---|---|
| `workflow help` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Workflow_Guide.md` |
| `continue sprint` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Sprint_Workflow.md` |
| `start story ST-XXXXXX` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Start_Story_Workflow.md` |
| `resume story ST-XXXXXX` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Resume_Story_Workflow.md` |
| `refine sprint` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Refine_Sprint_Workflow.md` |
| `plan next sprint` / `plan sprint` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Plan_Sprint_Workflow.md` |
| `create stories` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Create_Stories_Workflow.md` |
| `refine prototype` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Refine_Prototype_Workflow.md` |
| `sync devkit` | `{{AGENT_DIR_PREFIX}}/agents/workflows/Sync_Devkit_Workflow.md` |

Sprint and Start Story workflows share pipeline stages — see `{{AGENT_DIR_PREFIX}}/agents/workflows/Shared_Pipeline_Stages.md`.
<!-- SHARED-END -->
