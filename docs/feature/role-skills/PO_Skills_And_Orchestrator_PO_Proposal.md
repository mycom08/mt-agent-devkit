# PO Skills and Orchestrator-as-PO Proposal

**Status:** Design agreed (D1–D6 decided), no implementation yet
**Date:** 2026-10-27
**Scope:** Devkit internal harness (`.mt-agent-devkit/`) **and** distributed Phase 2 templates (`.mt-agent-devkit/distribution/phase2/templates/`). The frozen legacy `.claude/agents/templates/` corpus is not touched.
**Goal:** Token and latency savings. Many PO spawns exist only to re-check evidence the orchestrator already holds, tick AC boxes and flip a label.

---

## 1. Problem

A PO spawn always pays the full bootstrap before doing any work:

| Read at spawn (Stage 4 closure, current) | Size |
|---|---|
| `Agent_Common_Bootstrap.md` (or `Agent_Common_Core.md` on verified routing) | 17.9 KB (13.7 KB) |
| `Product_Owner_Rules_Bootstrap.md` | 9.7 KB |
| `Story_Standard_PO.md` | 5.6 KB |
| `product_owner_instructions.md` | 3.7 KB |
| `Product_Owner_Rules_Read_On_Demand.md §1` + `Story_Standard.md §14` | ~5 KB |
| `Product_Owner_Memory.md` | variable |

That is roughly 40 KB (~10k input tokens) **before** any provider subagent overhead, plus spawn latency. These numbers are byte counts, not measurements.

For a behavioral story, the closure work that follows is:
1. Re-check per-AC PASS evidence. The orchestrator already did this in the Merge Procedure's acceptance evidence pre-check (`Shared_Pipeline_Stages.md`, Merge Procedure).
2. Tick checkboxes, set `status:done`, close the issue.

The same pattern repeats for Refine Sprint Stage 4 (promote labels), Developer questions with owner PO, and the resumes during Plan Sprint.

Two precedents already show that the orchestrator can act as PO:
- `Create_Stories_Workflow.md`: "The orchestrator acts as PO … **Do not spawn a PO agent.**"
- Stage 4 non-behavioral fast path: "Orchestrator executes closure directly — no PO agent spawn."

---

## 2. Proposal Summary

0. **Prerequisite: move the always-on security rules into a shared `agent-security` skill** that every role and the orchestrator load in an enforced way (§3d).
1. **Move the PO procedures into `SKILL.md` skills.** Skills don't belong to a role, so a spawned PO and an orchestrator acting as PO load the **same** source. There is no second copy to drift.
2. **Add a project setting `po_execution: subagent | orchestrator`.** The default, `subagent`, keeps current behavior. With `orchestrator`, the orchestrator runs PO activities inline by loading the same skills, and it owns PO memory and the PO Working Record for those activities.
3. **Two forced-spawn exceptions.** Stage 3 validation where the QA role is the implementer always spawns a PO, for independence (§6). Plan Sprint always spawns a PO, for cost: it is the heaviest-reading PO activity, and it runs on the `standard` model policy instead of the orchestrator's model (D5).

---

## 3. Skill Set

Each skill is a `SKILL.md` with discovery frontmatter (`name`, `description`). Where a procedure depends on a rule that another skill owns, it **names that skill** rather than restating the rule or citing a rules-file section.

| Skill | Purpose | Absorbs (current source) | References |
|---|---|---|---|
| `po-core` | Rules true for **every** PO activity only: role boundaries and scope gating | PO Bootstrap §4; `Story_Standard_PO.md` §7 | `agent-security` (§3d) |
| `po-comment` | PO comments on issues: decisions, feedback and approvals go in issue comments (no standalone files), same thread for the same topic, comment format and `Thread Status` | PO Bootstrap §2; `Story_Standard_PO.md` §9 | `po-core` |
| `po-plan-docs` | Writing project plan documents: placement, `Title_Case_With_Underscores` naming, commit and push each plan-file update right away (github mode) | PO Bootstrap §10, §11 | `po-core` |
| `po-write-story` | Create or edit a story issue: concise-story rules, Assigned rule, no version-bump AC, title/labels, story structure and scope, body template, first-`--body-file` check | PO Bootstrap §1 (including the version-bump rule), PO On-Demand §5, `Story_Standard_PO.md` §2, §3, §13 | `po-core` |
| `po-roadmap-drain` | Drain roadmap-defined stories into tracked issues, idempotently | PO Bootstrap §11a, PO On-Demand §4 | `po-write-story`, `po-plan-docs` |
| `po-plan-sprint` | Plan Next Sprint steps 1–5, questions file, sprint artifacts, never promote to ready; release-gate sign-off when verifying the current sprint; sprint backlog finalization is not delegated | PO On-Demand §3, PO Bootstrap §9, §8 (backlog row) | `po-core`, `po-write-story`, `po-plan-docs`, `po-roadmap-drain` |
| `po-answer-questions` | Answer scope/AC questions on a thread; binding decisions; AC body sync; decide, don't discuss; defer technical calls to TL; flag scope drift to BA; defer-vs-include is not delegated | PO On-Demand §2 Role A, PO Bootstrap §5 (AC sync), §7, §8 (defer row) | `po-core`, `po-comment`, `po-write-story` (when an AC changes) |
| `po-promote-ready` | Story status workflow, readiness test and `backlog → ready` promotion; next-story promotion in Sprint Workflow | PO Bootstrap §5, PO On-Demand §2 Role B, `Story_Standard_PO.md` §1 | `po-core` |
| `po-verify-close` | Stage 4 closure: acceptance questions (AC, Definition of Done, backward compatible), evidence check, AC checkbox rules, elevated-verification check, implementer = validator closure signal, closure-comment ordering, tick, label, close; accept/reject is not delegated | PO On-Demand §1, PO Bootstrap §6, §8 (accept row), `Story_Standard_PO.md` §14, Shared Pipeline Stage 4 behavioral steps 3–4, closure-comment ordering pre-check | `po-core`, `po-comment`; `Story_Standard.md §14` stays a rule citation (it is not PO-owned) |
| `po-validate-ac` | Stage 3 validation when QA is the implementer: exercise each AC, write the per-AC report | Shared Pipeline Stage 3 step 1 | `po-core`, `po-comment`; `Story_Standard.md §14` |

**Dropped from PO:** PO Bootstrap §12 (runtime-state handoff). It only pointed to `Agent_Common_Read_On_Demand.md §5`, which every role already gets through Common routing.

**Size target:** `po-core` ≤ 1 KB; every other skill ≤ 4 KB.

**Skills loaded per activity:**

| Activity | Skills |
|---|---|
| Stage 4 closure | `po-core`, `po-verify-close`, `po-comment` |
| Answer scope/AC questions | `po-core`, `po-answer-questions`, `po-comment` (+ `po-write-story` if an AC changes) |
| Promote to ready | `po-core`, `po-promote-ready` |
| Create stories | `po-core`, `po-write-story` |
| Plan Sprint (always spawned) | `po-core`, `po-plan-sprint`, `po-write-story`, `po-plan-docs` (+ `po-roadmap-drain` when a roadmap changes) |
| Stage 3 validation, QA as implementer (always spawned) | `po-core`, `po-validate-ac`, `po-comment` |

Splitting stops here. A further split (for example, scope gating on its own) would add a skill read per activity without saving meaningful bytes.

**Shared rules stay rules.** `Story_Standard.md` (including §14), `Agent_Common_*`, and the workflow files are not PO-owned, so skills cite them; they don't absorb them. The other roles' views (`Story_Standard_QA.md`, `_TL`, `_Dev`, `_UIUX`) are unchanged. `Story_Standard_PO.md` is the one role view that is folded in, because the PO is its only consumer.

### 3a. What remains outside the skills

- `product_owner_instructions.md` becomes a thin role file: role summary, Selected Common Routing, record paths, and "load `po-core`, then the skill named in your assignment".
- `Product_Owner_Rules_Bootstrap.md`, `Product_Owner_Rules_Read_On_Demand.md` and `Story_Standard_PO.md` are **deleted in the same release** that introduces the skills, internally and in target projects. There are no redirect stubs. See §3c.

#### File disposition

| File | Disposition | Copies affected |
|---|---|---|
| `Product_Owner_Rules_Bootstrap.md` | **Removed** | Canonical `.mt-agent-devkit/rules/`, Phase 2 template, bundle asset, wrappers in `.claude/agents/working/rules/` and `.antigravity/agents/working/rules/` |
| `Product_Owner_Rules_Read_On_Demand.md` | **Removed** | Same set |
| `Story_Standard_PO.md` | **Removed**, folded into skills | Same set |
| `product_owner_instructions.md` | **Kept, slimmed.** It still defines the spawnable Product Owner agent, needed for the forced spawns | Canonical, Phase 2 template, bundle asset, provider wrappers |
| `Product_Owner_Memory.md`, `Product_Owner_Working_Record.md` | **Kept, unchanged** (runtime state) | — |
| `.claude/agents/templates/**` PO templates | **Kept** (frozen legacy corpus) | — |
| `po-*` skills | **Added** | Canonical `.mt-agent-devkit/skills/`, provider wrappers, Phase 2 skill templates |

### 3c. Retiring the old rule files in target projects

The Phase 2 deployment engine (`deployment.py`) already supports a `retirement` operation phase. Today `build_bundle.py` emits retirements only for legacy `.<provider>/agents/...` layout paths. This proposal adds explicit retirement entries for the PO rule files:

| Retired path | Surviving dependencies (`after_verified_ids`) |
|---|---|
| `.mt-agent-devkit/rules/Product_Owner_Rules_Bootstrap.md` | `po-core` and every `po-*` skill entry, `product_owner_instructions.md` |
| `.mt-agent-devkit/rules/Product_Owner_Rules_Read_On_Demand.md` | Same |
| `.mt-agent-devkit/rules/Story_Standard_PO.md` | Same |

What the engine already guarantees, with no new code:
- A file is deleted only after its survivors are written and verified. A failed sync never leaves a target with neither rules nor skills.
- The plan is refused if any surviving managed file still contains a retired path. That works as a built-in stale-citation gate for target output.
- The plan is refused if a project-adapted file references a retired path. A customised project gets an explicit conflict to review, never a silent broken link.
- Only `managed` files are deleted. A retirement needs a reviewed resolution matching the file's current hash. A fresh install skips it, because the entry is `required: False`.

**Mid-sprint sync:** a target project that syncs mid-sprint could resume a PO session that loaded the old rules. The `CHANGELOG.md` entry says to sync between sprints. A fresh spawn always reads the new files.

### 3b. Location and discovery

| Layer | Canonical source | Discovery surface |
|---|---|---|
| Devkit internal | `.mt-agent-devkit/skills/po-*/SKILL.md` | Generated wrappers in `.claude/skills/`, `.antigravity/skills/`, `.codex/skills/` via `migration-inventory.json` `generated-wrapper` entries and `generate_wrappers.py` |
| Target projects | `.mt-agent-devkit/distribution/phase2/templates/skills/po-*/SKILL_template.md` | `build_bundle.py` emits `.<provider>/skills/po-*/SKILL.md` per provider, the same pattern as `ci-watch` and `local-verify` today |

`generate_wrappers.py` needs a skill renderer. Today's renderer emits "load the canonical file" prose. A skill wrapper must carry the frontmatter plus a single pointer to the canonical `SKILL.md`.

Per `Provider_Contract.md`, a skill directory does not prove native discovery. Workflows therefore name the canonical path as well as the skill name, so a provider without verified discovery (Codex today) reads the file directly.

### 3d. Security baseline

**Gap today:** `orchestrator_instructions.md`, the root entrypoints and the shared workflows load none of the Common security rules. The orchestrator already reads untrusted issue threads and merges PRs without them, and an inline PO activity would add GitHub writes on top.

**Change:** the always-on security rules move into one shared skill, `agent-security`, that every role and the orchestrator use. This is a **prerequisite story** (Phase 0, §9). It is not PO-specific.

| Content | Disposition |
|---|---|
| Secret handling (`Agent_Common_Core.md §2` and its `Agent_Common_Bootstrap.md` equivalent) | **Moved** into `agent-security` |
| External content and prompt injection (`Agent_Common_Core.md §4` and its Bootstrap equivalent) | **Moved** into `agent-security` |
| Shell and GitHub mutation safety (`Agent_Common_Shell_Safety.md`) | **Referenced, not absorbed.** Its trigger is part of the manifest `extend --trigger shell_safety` flow and the "no persistence before safety" ordering in Core §1. The skill says: before the first shell write, Git operation or GitHub mutation, read Shell Safety in full |
| Credential gate (`Agent_Common_Credential_Gate.md`) | **Unchanged.** It is conditional and already a separate triggered module |

Size target: `agent-security` ≤ 1.5 KB.

**Loading is enforced, not pointed to.** A bare pointer in a full-read Common file can be skipped, and nothing would detect it. Each route therefore keeps a guaranteed load:

| Route | Who | How `agent-security` is loaded |
|---|---|---|
| `Agent_Common_Core.md` (verified manifest routing) | Spawned roles | Core §2 and §4 are replaced by a **required manifest entry** for `agent-security` in `read-routing.json`. `read_manifest.py` validates it and the worker attests coverage with a receipt |
| `Agent_Common_Bootstrap.md` (routes without manifests) | Spawned roles | The text stays **inline, as a generated copy of the skill**. A `--check` validator, like `generate_wrappers.py --check`, fails CI on drift. One source, and loading stays guaranteed by the full-file read |
| Orchestrator | Every workflow, every `po_execution` mode | Reads `agent-security` at workflow start, before the first issue/PR read or GitHub mutation. The loaded skill is recorded in the pipeline state |

`po-core` declares `requires: agent-security`. A spawned PO already has it through its Common route, and the orchestrator has it from workflow start, so the PO path adds no further reads.

---

## 4. The Setting

| Item | Design |
|---|---|
| Key | `po_execution` |
| Values | `subagent` (default), `orchestrator` |
| Absent or unrecognised | `subagent`; an unrecognised value is reported once and not guessed |
| Location | Project-owned settings file that sync never overwrites. Open decision **D1** |
| Read by | The top-level orchestrator, at workflow start |
| Pinned | Written into the pipeline state file as `PO Execution:`. A resumed run uses the pinned value, so a setting change mid-sprint never flips a run halfway |

Target projects: `init project` writes the default. `sync devkit` keeps the existing value. The bundle already supports `owner="project"` entries.

---

## 5. Behavior Matrix

| Touchpoint | `subagent` (today) | `orchestrator` |
|---|---|---|
| Create Stories | Inline (already) | Inline, loads `po-core` + `po-write-story` |
| Plan Sprint Stages 1, 2, 4 | Spawn/resume `po_session` | **Spawn/resume (forced)**, `po-plan-sprint` |
| Refine Sprint Stage 2 (after TL) | Spawn/resume | Inline, `po-answer-questions`; TL-before-PO ordering kept |
| Refine Sprint Stage 4 | Resume | Inline, `po-promote-ready` |
| Pipeline Stage 2: Developer question with owner PO | Spawn/resume | Inline, `po-answer-questions` |
| Pipeline Stage 3: QA is the implementer | Spawn | **Spawn (forced)**, `po-validate-ac` |
| Pipeline Stage 4 non-behavioral | Inline (already) | Inline (unchanged) |
| Pipeline Stage 4 behavioral | Spawn (`closure` policy) | Inline, `po-verify-close` |
| Sprint Workflow next-story promotion | PO | Inline, `po-promote-ready` |

In `orchestrator` mode, `po_session` records `inline` for the inline touchpoints, and the observation checks accept it.

---

## 6. Independence Analysis

The acceptance chain has three distinct jobs. Only one of them needs a separate actor.

| Job | Who does it today | Independence requirement |
|---|---|---|
| **Produce** per-AC evidence (exercise the AC) | QA; or PO when QA is the implementer | Must not be the implementer **and** must not be the actor driving the pipeline forward |
| **Check** the evidence before merge | Orchestrator (Merge Procedure pre-check) | Already the orchestrator |
| **Confirm** and record acceptance (tick, done, close) | PO | No new independence; it re-reads evidence the orchestrator already checked |

- **Stage 4 behavioral closure is safe to inline.** The evidence still comes from an independent QA agent. The orchestrator already performed the same §14 check before merging. Today's PO spawn adds a second reader, not a second validator.
- **Stage 3 with QA as the implementer is not safe to inline.** PO is the **only** producer of evidence there. If the orchestrator produced it, the actor that wants the pipeline to advance would certify its own gate, and then merge on the strength of that certification. Exercising ACs also pulls test output into the orchestrator's long-lived context. **This touchpoint always spawns.**
- **Decision touchpoints** (scope answers, readiness, sprint selection) are about authority, not independence. In `orchestrator` mode the orchestrator is also the channel to the human user, so escalation is shorter, not weaker.
- **Accepted trade-off:** in `orchestrator` mode, one actor both merges and records acceptance. That is acceptable because the evidence producer stays independent. It must be stated in the setting's documentation so adopters opt in knowingly.

---

## 7. State Ownership in `orchestrator` Mode

| Concern | Design |
|---|---|
| PO memory | The orchestrator reads `Product_Owner_Memory.md` at its first PO activity in the run, and writes durable facts per `Agent_Common_Memory.md` |
| PO Working Record | Written at the end of each inline PO activity that writes it today. Stage 4 closure still skips it, as it does now |
| Access control | Amend the "read and update only your own record" rule in `Agent_Common_Bootstrap.md` §1, `Agent_Common_Working_Record.md` and their templates: *the orchestrator acting as PO under `po_execution: orchestrator` owns the PO record and memory for that activity* |
| Orchestrator's own state | Unchanged. PO facts never go into orchestrator state, and orchestrator state never goes into PO records |
| Retro contribution | The orchestrator evaluates `Agent_Common_Bootstrap.md §7` in its PO capacity, attributed to Product Owner |
| Read manifest | No worker spawn means no manifest. This is consistent with existing orchestrator-direct paths (Merge Procedure, non-behavioral closure). Inline activities record the loaded skill names in the pipeline state for auditability |
| Telemetry | `session_mode` allows only `fresh`, `same_session_resume` and `expired_session_resume`. Add `orchestrator_inline` with role `Product_Owner`. That is an additive enum change; see **D3** |
| Model policy | Inline work runs on the orchestrator's model. The `closure` and `standard` policies apply only to spawns |

---

## 8. Ripple Checklist

Citations to retired PO rule sections exist across the corpus. At minimum:

- **Workflows:** `Plan_Sprint_Workflow.md`, `Refine_Sprint_Workflow.md`, `Shared_Pipeline_Stages.md`, `Sprint_Workflow.md`, `Create_Stories_Workflow.md`, `Workflow_Guide.md`, plus their Phase 2 `*_Shared_template.md` and the github/strict wrappers
- **Rules:** `Story_Standard.md` (its role-view index must drop the PO view), `Developer_Rules_*`, `QA_Rules_*`, `Technical_Lead_Rules_Bootstrap.md`, `UI_UX_Designer_Rules_*`, `Audit_Rules.md`, `Retro_Rules.md`, `Agent_Common_*`
- **Contracts and scripts:** `read-routing.json` (`po_standard` entries), `migration-inventory.json`, `build_bundle.py`, `telemetry.py`, `retro_completion.py`
- **Validators and tests:** `validate_internal_harness.py`, `validate_templates.py`, `scripts/test/`, `scripts/test/test_internal_harness`
- **Context and docs:** `Project_Priming_*` (§15 has the "splitting a shared rules file" ripple checklist, which applies here), `changes.json` and `CHANGELOG.md` for the template side

Phase 0 (`agent-security`) has its own ripple:
- `Agent_Common_Core.md` §2, §4 and `Agent_Common_Bootstrap.md`, plus their Phase 2 templates
- every citation of Core §2/§4 across rules, instructions and workflows
- `read-routing.json` (a required entry for every role), `read_manifest.py` tests
- `docs/reviews/ST-000264_Common_Ownership.json` (ownership of the moved sections)
- `orchestrator_instructions.md` and its Phase 2 shared template (load at workflow start)
- `build_bundle.py` and `migration-inventory.json` (skill discovery per provider)
- the generator and drift check for the Bootstrap inline copy

---

## 9. Phasing

| Phase | Story | Behavior change | Exit criteria |
|---|---|---|---|
| 0 | **`agent-security` skill** (prerequisite, all roles and the orchestrator; §3d) | Orchestrator gains the security baseline; workers unchanged in substance | Skill in every provider's discovery surface; required manifest entry on the Core route; generated inline copy on the Bootstrap route with a drift check; orchestrator loads it at workflow start; all existing gates green |
| 1 | **Extract PO skills.** The spawned PO loads skills instead of rule sections, in internal and Phase 2 | None | All existing gates green; every retired section's content traceable to a skill (migration map in the PR); no stale citations |
| 2 | **Add `po_execution` setting and orchestrator mode**, default `subagent` | Opt-in only | Matrix §5 implemented; state pinning; ownership amendments; telemetry enum; forced spawn on Stage 3 with QA as implementer and on Plan Sprint |

**Order:** Phase 0 merges before Phase 2, which needs the orchestrator to hold `agent-security` before any inline PO work. Phase 0 and Phase 1 are independent of each other.

**Release boundary:** Phases 0, 1 and 2 ship in **one release**. All three stories go in the same sprint, and the `release` workflow is dispatched only after all are merged. Each merge leaves `main` consistent on its own, so there is no intermediate broken `SNAPSHOT`. The retirement entries (§3c) land in Phase 1, because that is where the old files stop being read. No benchmark phase is planned: `subagent` stays the default and adopters opt in to `orchestrator`.

Phase 1 delivers value on its own: a spawned PO reads a ~1 KB core skill plus the task skills its activity needs, instead of ~15 KB of PO rules and the 5.6 KB `Story_Standard_PO.md`.

---

## 10. Validation

- `python scripts/validate_internal_harness.py`, `python .mt-agent-devkit/scripts/generate_wrappers.py --check`, `python -m unittest scripts.test.test_internal_harness`, `python scripts/validate_templates.py` and `bash scripts/test/run.sh` all exit 0
- New checks:
  - every `po-*` skill and `agent-security` exists with valid frontmatter in every provider's discovery surface (internal and bundle)
  - the `agent-security` inline copy in `Agent_Common_Bootstrap.md` and its template matches the skill byte-for-byte (`--check`)
  - every Core-route role manifest contains the required `agent-security` entry; a manifest without it fails `read_manifest.py validate`
  - the orchestrator instructions load `agent-security` before the first issue/PR read
  - every skill-to-skill reference resolves to an existing skill
  - no citation targets a retired PO rules section
  - `po_execution` absent → `subagent`
  - Stage 3 with QA as the implementer, and Plan Sprint, spawn in both modes

---

## 11. Non-Goals

- Changing QA, TL or Developer gates, or the Merge Procedure
- Applying the role-skill pattern to other roles. Phase 0 touches every role only for `agent-security`. This proposal is shaped so #265 (Developer stage profiles) can reuse it
- Moving Shell Safety or the credential gate into skills
- Editing the frozen `.claude/agents/templates/` corpus

---

## 12. Open Decisions

| ID | Decision | Recommendation |
|---|---|---|
| D1 | Where the setting lives | **Decided:** a project-owned JSON file (machine-checkable, survives sync), mirrored as a read-only line in the entrypoint for visibility |
| D2 | Retired rule files | **Decided:** delete in the same release, internally and in targets, through the deployment engine's retirement phase (§3c). No stubs |
| D3 | Telemetry | **Decided:** add `orchestrator_inline` to the schema v1 `session_mode` enum additively |
| D4 | Stage 3 with QA as the implementer | **Decided:** always spawn a PO, in both modes (§6) |
| D6 | Security rules | **Decided:** move to a shared `agent-security` skill as prerequisite Phase 0. Enforced through a manifest entry on the Core route and a generated inline copy on the Bootstrap route; the orchestrator loads it at workflow start (§3d) |
| D5 | Plan Sprint in `orchestrator` mode | **Decided:** always spawn a PO. Planning reads the most context, and a spawned PO on the `standard` policy is likely cheaper than the orchestrator's model |
