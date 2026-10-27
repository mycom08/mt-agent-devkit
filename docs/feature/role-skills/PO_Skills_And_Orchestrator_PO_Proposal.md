# PO Skills and Orchestrator-as-PO Proposal

**Feature:** `role-skills`
**Status:** Revision 3. Addresses both TL reviews on PR #286 (B1–B8, N1–N6; NB1, NB2, N7–N10); awaiting re-review
**Date:** 2026-10-27
**Scope:** Devkit internal harness (`.mt-agent-devkit/`) **and** distributed Phase 2 templates (`.mt-agent-devkit/distribution/phase2/templates/`). The frozen legacy `.claude/agents/templates/` corpus is not touched.
**Goal:** Token and latency savings. Many PO spawns exist only to re-check evidence the orchestrator already holds, tick AC boxes and flip a label.

---

## 1. Problem

A PO spawn always pays the full bootstrap before doing any work:

| Read at spawn (Stage 4 closure, current) | Size |
|---|---|
| `Agent_Common_Bootstrap.md` (every manifest today resolves to Bootstrap; see §3d) | 17.9 KB |
| `Product_Owner_Rules_Bootstrap.md` | 9.7 KB |
| `Story_Standard_PO.md` | 5.6 KB |
| `product_owner_instructions.md` | 3.7 KB |
| `Product_Owner_Rules_Read_On_Demand.md §1` + `Story_Standard.md §14` | ~5 KB |
| `Product_Owner_Memory.md` | variable |

That is roughly 40 KB (~10k input tokens) **before** provider subagent overhead, plus spawn latency. These are byte counts, not measurements. §7 makes inline work measurable so the saving can be checked (N5).

For a behavioral story, the closure work that follows is: re-check per-AC PASS evidence (the orchestrator already did this in the Merge Procedure pre-check), judge Definition of Done, backward compatibility and any elevated verification requirement, then tick, label and close.

Two precedents already show that the orchestrator can act as PO:
- `Create_Stories_Workflow.md`: "The orchestrator acts as PO … **Do not spawn a PO agent.**"
- Stage 4 non-behavioral fast path: "Orchestrator executes closure directly — no PO agent spawn."

---

## 2. Proposal Summary

0. **Prerequisite: a shared `agent-security` skill** for the always-on security rules. Every role keeps a guaranteed load through a generated inline copy, and the orchestrator loads the skill itself (§3d).
1. **Move the PO procedures into `SKILL.md` skills.** A spawned PO and an orchestrator acting as PO load the **same** canonical skill files (§3).
2. **Add a project setting `po_execution: subagent | orchestrator`.** The default, `subagent`, keeps current behavior. With `orchestrator`, the orchestrator runs PO activities inline and owns PO memory and the PO Working Record for them (§4–§7).
3. **Independence guards.** Plan Sprint and Stage 3 validation with QA as implementer always spawn a PO. In `orchestrator` mode, any scope change after Stage 1 starts escalates to the user (§6).

---

## 3. Skill Set

Each skill is a `SKILL.md` with discovery frontmatter (`name`, `description`). Where a procedure depends on a rule another skill owns, it **names that skill** rather than restating the rule.

| Skill | Purpose | Absorbs (current source) | Requires |
|---|---|---|---|
| `po-core` | Rules for **every** PO activity: role boundaries, scope gating, PO records (memory format `## Stored Facts` per `Agent_Common_Read_On_Demand.md §1`; Working Record retention of at most 3 story entries; closure skips the Working Record) | PO Bootstrap §4, §11b; `Story_Standard_PO.md` §7; instructions Working Record section | `agent-security` |
| `po-comment` | Decisions, feedback and approvals go in issue comments (no standalone files), same thread per topic, comment format and `Thread Status` | PO Bootstrap §2; `Story_Standard_PO.md` §9 | `po-core` |
| `po-plan-docs` | Plan documents: placement, `Title_Case_With_Underscores` naming, commit and push each plan-file update right away (github mode) | PO Bootstrap §10, §11 | `po-core` |
| `po-write-story` | Create or edit a story: concise-story rules, Assigned rule, no version-bump AC, title/labels, structure and scope, body template, first-`--body-file` check | PO Bootstrap §1, PO On-Demand §5, `Story_Standard_PO.md` §2, §3, §13 | `po-core` |
| `po-roadmap-drain` | Drain roadmap-defined stories into tracked issues, idempotently | PO Bootstrap §11a, PO On-Demand §4 | `po-write-story`, `po-plan-docs` |
| `po-plan-sprint` | Plan Next Sprint steps 1–5 including the final Working Record step; questions file; never promote to ready; release-gate sign-off; sprint planning and backlog-refinement ceremonies (break epics into stories ≤ 13 points); backlog finalization is not delegated | PO On-Demand §3 (incl. Step 5.6), PO Bootstrap §3 (planning, refinement), §8 (backlog row), §9 | `po-core`, `po-write-story`, `po-plan-docs`, `po-roadmap-drain` |
| `po-answer-questions` | Answer scope/AC questions; binding decisions; AC body sync; decide, don't discuss; defer technical calls to TL; flag scope drift to BA; defer-vs-include is not delegated; daily-standup unblocking; scope-change escalation in `orchestrator` mode (§6) | PO On-Demand §2 Role A, PO Bootstrap §3 (standup), §5 (AC sync), §7, §8 (defer row) | `po-core`, `po-comment`, `po-write-story` (when an AC changes) |
| `po-promote-ready` | Story status workflow, readiness test, `backlog → ready` promotion, final Working Record step; next-story promotion in Sprint Workflow | PO Bootstrap §5, PO On-Demand §2 Role B (incl. step 4), `Story_Standard_PO.md` §1 | `po-core` |
| `po-verify-close` | Stage 4 closure: acceptance questions (all AC, Definition of Done and no open comments, backward compatible), evidence check, AC checkbox rules, elevated-verification check, implementer = validator closure signal, closure-comment ordering, tick/label/close, memory facts but no Working Record; sprint-review ceremony; accept/reject is not delegated | PO On-Demand §1 (incl. step 7), PO Bootstrap §3 (review), §6, §8 (accept row), `Story_Standard_PO.md` §14, Shared Pipeline Stage 4 behavioral steps 3–4, closure-comment ordering | `po-core`, `po-comment`; cites `Story_Standard.md §14` |
| `po-validate-ac` | Stage 3 validation with QA as implementer: exercise each AC, write the per-AC report | Shared Pipeline Stage 3 step 1 | `po-core`, `po-comment`; cites `Story_Standard.md §14` |

**Dropped from PO, with reasons:**
- PO Bootstrap §12 (runtime-state handoff): it only pointed to `Agent_Common_Read_On_Demand.md §5`, which every role gets through Common.
- PO Bootstrap §13 (routing table): replaced by the per-activity table below.

**Size targets:** `po-core` ≤ 1.5 KB; every other `po-*` skill ≤ 4 KB.

**Skills loaded per activity:**

| Activity | Skills |
|---|---|
| Stage 4 closure | `po-core`, `po-verify-close`, `po-comment` |
| Answer scope/AC questions | `po-core`, `po-answer-questions`, `po-comment` (+ `po-write-story` if an AC changes) |
| Promote to ready | `po-core`, `po-promote-ready` |
| Create stories | `po-core`, `po-write-story` |
| Plan Sprint (always spawned) | `po-core`, `po-plan-sprint`, `po-write-story`, `po-plan-docs` (+ `po-roadmap-drain` when a roadmap changes) |
| Stage 3 validation, QA as implementer (always spawned) | `po-core`, `po-validate-ac`, `po-comment` |

Splitting stops here. A further split would add a skill read per activity without saving meaningful bytes.

**Shared rules stay rules.** `Story_Standard.md`, `Agent_Common_*` and the workflow files are not PO-owned. Skills cite them; they don't absorb them. `Story_Standard.md` itself is amended for inline acceptance (§6). The QA, TL, Dev and UI/UX role views are unchanged. `Story_Standard_PO.md` is folded in because the PO is its only consumer.

### 3a. File Disposition

| File | Disposition | Copies affected |
|---|---|---|
| `Product_Owner_Rules_Bootstrap.md` | **Removed** | Canonical `.mt-agent-devkit/rules/`, Phase 2 template, bundle asset, `.claude/agents/working/rules/` and `.antigravity/agents/working/rules/` wrappers, legacy target paths (§3c) |
| `Product_Owner_Rules_Read_On_Demand.md` | **Removed** | Same set |
| `Story_Standard_PO.md` | **Removed**, folded into skills | Same set |
| `product_owner_instructions.md` | **Kept, slimmed**: role summary, Selected Common Routing, record paths, "load `po-core`, then the skill named in your assignment". It still defines the spawnable Product Owner agent | Canonical, Phase 2 template, bundle asset, wrappers |
| `Product_Owner_Memory.md`, `Product_Owner_Working_Record.md` | **Kept, unchanged** (runtime state) | — |
| `.claude/agents/templates/**` PO templates | **Kept** (frozen legacy corpus) | — |
| `po-*` and `agent-security` skills | **Added** | See §3b |

### 3b. Location and Discovery

**One canonical copy in both layouts (B1).** Every skill has a shared canonical file at `.mt-agent-devkit/skills/<name>/SKILL.md`, in the devkit and in every target. In the bundle it is a `shared`-owner, `managed` entry with no provider suffix. Provider discovery files are thin wrappers that carry the frontmatter and point to the canonical file:

| Layer | Canonical | Discovery wrappers |
|---|---|---|
| Devkit internal | `.mt-agent-devkit/skills/<name>/SKILL.md` | `.claude/skills/`, `.antigravity/skills/`, `.codex/skills/`, generated by `generate_wrappers.py` from `migration-inventory.json` |
| Target | `.mt-agent-devkit/skills/<name>/SKILL.md`, from `templates/skills/<name>/SKILL_template.md` | `.<provider>/skills/<name>/SKILL.md`, emitted by `build_bundle.py` per selected provider |

`generate_wrappers.py` gains a skill renderer: frontmatter plus a single pointer to the canonical file. Workflows name the canonical path as well as the skill name, so a provider without verified native discovery (Codex today) reads the file directly. Per `Provider_Contract.md`, a skill directory does not prove discovery.

### 3c. Retiring the Old Files in Target Projects

The deployment engine's `retirement` phase is the mechanism. These guarantees hold in the code today:
- Survivors are verified before any deletion (`deployment.py:506-511`).
- Retirement is managed-only and never touches runtime paths (`:291-293`, `:348-353`).
- An absent file is skipped only when `required` is false (`:283-284`). `entry()` defaults to `required: true`, so each retirement entry sets it explicitly, as `build_bundle.py:228` does.

The rest needs new work, all in story 1c (§9):

| Gap (TL finding) | Design |
|---|---|
| **Survivor IDs (B1).** Provider operation IDs carry `:<provider>`, so a fixed survivor list fails on targets that don't bind every provider | Survivors are the **shared** canonical skill IDs from §3b plus `product_owner_instructions.md`. Those IDs exist in every plan |
| **Legacy layouts (B2).** `build_bundle.py:202-229` derives legacy retirements from surviving shared entries, so deleting the PO templates drops their legacy retirements | Explicit retirement entries for every legacy variant of the three files (`.claude/agents/rules/...`, `.antigravity/agents/rules/...`, per mode), with the shared skills as survivors. Each legacy fixture (`v0.1.48.zip`, `v0.1.49.zip`, `v0.1.50.zip`) gets a migration test asserting the old PO files are gone and the skills are present |
| **Stale citations (B3a).** The engine gate matches full paths only, but the corpus cites bare filenames (`` `Story_Standard_PO.md` §14``) | A new validator rejects any bare-filename or `§`-citation of a retired file anywhere in the internal corpus, the Phase 2 templates and the bundle content (§10). The engine's full-path gate stays as a second net |
| **No resolution source (B3b, N9).** Production code never creates retirement resolutions, so every existing target's first sync stops at `deployment.py:297-298` | Sync generates a resolution **only** when all of these hold:<br>• The path is listed in the new manifest's `legacy_support.retirements`.<br>• The target has a receipt (`deployment.py:523`) whose entry has `adapted: false` and a present `stock_sha256`. A missing `adapted` or `stock_sha256` is unknown, never false (`:306`).<br>• The current hash equals the receipt's `rendered_sha256`.<br><br>The generated resolution has `after_sha256: null` and the reason `stock retirement in <version>`. The sync review step lists every generated retirement before apply. Every other case stays a conflict. Legacy 0.1.48–0.1.50 targets have no receipt (`lifecycle.py:37`), so they keep the manual reviewed-resolution path |
| **Customised files (B3c).** An `adapted: true` file would be deleted and its customization lost | Sync refuses with a dedicated conflict: "retired file <path> is customised; port the customization into the replacing skill, then resolve". It never auto-resolves. The Sync workflow and the CHANGELOG describe the porting step |

**Mid-sprint sync:** a target that syncs mid-sprint could resume a PO session that loaded the old rules. The CHANGELOG entry says to sync between sprints. A fresh spawn always reads the new files.

### 3d. Security Baseline (`agent-security`)

**Gap today:** `orchestrator_instructions.md`, the root entrypoints and the shared workflows load none of the Common security rules. The orchestrator already reads untrusted issue threads and merges PRs without them.

**Route reality (B4a).** `verified_providers` is `[]` (`read-routing.json:1468`), so `capability_routes` never runs (`read_manifest.py:175-176`) and every manifest resolves Common to `Agent_Common_Bootstrap.md`. No consumer uses the Core route today. The Bootstrap inline copy is therefore the guarantee that matters in practice. The Core route keeps the same guarantee for when it is enabled.

**Skill content:**

| Part | Content | Inlined into Core and Bootstrap? |
|---|---|---|
| A. Secret handling | Moved from `Agent_Common_Core.md §2` and its Bootstrap equivalent | Yes, generated copy |
| B. External content and prompt injection | Moved from `Agent_Common_Core.md §4` and its Bootstrap equivalent | Yes, generated copy |
| C. Shell authority for the orchestrator | "Before the first shell write, Git operation or GitHub mutation, read `Agent_Common_Shell_Safety.md` in full." | **No.** Workers keep their own route's shell rules (Core §1 extend flow, Bootstrap §6). Inlining C would add a new mandatory read to every Bootstrap-route worker (B4c) |

The credential gate is unchanged.

**Loading on each route (B4b):**

| Consumer | Guarantee |
|---|---|
| Core-route workers (when enabled) | Generated inline copy of parts A and B in `Agent_Common_Core.md`, read in full |
| Bootstrap-route workers (all of them today) | Generated inline copy of parts A and B in `Agent_Common_Bootstrap.md`, read in full |
| Orchestrator | Reads the full skill (A, B and C) at workflow start, before the first issue/PR read or GitHub mutation, and records it in the pipeline state |

There is **no manifest entry.** Manifests exist only for story tasks (`read_manifest.py:127-130`), so a spawn without one (Plan Sprint, refinement, a TL design review) would lose the rules if Common relied on a manifest entry. The inline copies cover every spawn.

**Drift check:** a generator writes parts A and B between generated-block markers in `Agent_Common_Core.md`, `Agent_Common_Bootstrap.md` and their Phase 2 templates. Its `--check` mode fails CI when any copy differs from the skill.

**Behavior change in Phase 0:** the orchestrator now reads `agent-security` and `Agent_Common_Shell_Safety.md`. Worker behavior is unchanged in substance, since workers read the same text from the same files.

**Size target:** `agent-security` ≤ 2.5 KB. Parts A and B alone are 1,569 bytes today (N2).

`po-core` requires `agent-security`. A spawned PO already has parts A and B through its Common read, and the orchestrator holds the full skill from workflow start, so the PO path adds no reads.

---

## 4. The Setting

| Item | Design |
|---|---|
| Key | `po_execution` |
| Values | `subagent` (default), `orchestrator` |
| File | `.mt-agent-devkit/project_settings.json`, in the devkit and in targets |
| Ownership | Bundle entry `ownership: project_owned`, `renderer: create_if_absent`. `init` creates it with the default; `sync` never overwrites it (N4) |
| Absent or unrecognised | `subagent`; an unrecognised value is reported once and not guessed |
| Visibility | The JSON file only. No mirrored entrypoint line: the `managed_sections` block is rewritten on every sync and would drift from the JSON (N4) |
| Read by | The top-level orchestrator, at workflow start |
| Pinned | Written into the pipeline state file as `PO Execution:`. A resumed run uses the pinned value, so a setting change mid-sprint never flips a run halfway |

---

## 5. Behavior Matrix

| Touchpoint | `subagent` (today) | `orchestrator` |
|---|---|---|
| Create Stories | Inline (already) | Inline: `po-core`, `po-write-story` |
| Plan Sprint Stages 1, 2, 4 | Spawn/resume `po_session` | **Spawn/resume (forced)**: `po-plan-sprint` |
| Refine Sprint Stage 2 (after TL) | Spawn/resume | Inline: `po-answer-questions`; TL-before-PO ordering kept |
| Refine Sprint Stage 4 | Resume | Inline: `po-promote-ready` |
| Pipeline Stage 2: Developer question with owner PO | Spawn/resume | Inline: `po-answer-questions` |
| **Scope change after Stage 1 starts** (defer, split, or **any** AC body edit) | PO decides | **Escalate to the user** through the existing blocked-story procedure. Never decided inline. Every AC body edit counts, not only ones the orchestrator judges a weakening, so the merging actor never decides whether its own edit lowers the bar (N10) |
| Pipeline Stage 3: QA is the implementer | Spawn | **Spawn (forced)**: `po-validate-ac` |
| Pipeline Stage 4 non-behavioral | Inline (already) | Inline (unchanged) |
| Pipeline Stage 4 behavioral | Spawn (`closure` policy) | Inline: `po-verify-close` |
| Sprint Workflow next-story promotion | PO | Inline: `po-promote-ready` |

In `orchestrator` mode, `po_session` records `inline` for inline touchpoints, and the observation checks accept it.

---

## 6. Independence Analysis

| Job | Who does it today | Independence requirement |
|---|---|---|
| **Produce** per-AC evidence | QA; PO when QA is the implementer | Not the implementer, and not the actor driving the pipeline forward |
| **Check** the evidence before merge | Orchestrator (Merge Procedure pre-check) | Already the orchestrator |
| **Change scope** after Stage 1 starts (defer, split, weaken an AC) | PO or the user (`Story_Standard.md:376`) | Not the actor that wants the merge |
| **Confirm** acceptance (tick, done, close) | PO | Judgement checks must actually run |

- **Stage 4 behavioral closure is safe inline.** The evidence still comes from an independent QA agent. The orchestrator already performed the §14 evidence check before merging. Inline closure is still not just a second reader: `po-verify-close` runs the checks the merge pre-check does **not** cover — Definition of Done and open comments, backward compatibility, and any elevated verification requirement (PO Bootstrap §6, `Shared_Pipeline_Stages.md:433`) (N3).
- **Stage 3 with QA as the implementer always spawns.** PO is the only evidence producer there. Inline, the orchestrator would certify its own gate and then merge on it.
- **Scope changes escalate (B5b).** In `orchestrator` mode, the actor that wants the merge could otherwise defer or split a story, or drop a NOT VERIFIED AC, and so advance its own gate. Any such change after Stage 1 starts goes to the user. That closes the remaining self-certification path, so the two forced spawns plus this escalation are sufficient.
- **The non-behavioral fast path is a deliberate, existing exception (B5c).** `Shared_Pipeline_Stages.md:359-366` already lets the orchestrator record sign-off and merge. It is acceptable because those ACs are confirmed by inspecting the files in the PR diff, which anyone can re-check from the PR. Any AC needing domain knowledge falls back to a full QA agent. Behavioral evidence cannot be re-derived from the diff, which is why the behavioral path keeps an independent producer.
- **Decision touchpoints** (scope answers before Stage 1, readiness, story creation) are about authority, not independence. In `orchestrator` mode the orchestrator is the channel to the human user, so escalation is shorter.
- **Accepted trade-off:** in `orchestrator` mode, one actor merges and records acceptance. That is acceptable because the evidence producer stays independent and scope changes go to the user. The setting's documentation says so, so adopters opt in knowingly.

**Contract amendments (B5a), in story 2a:** `Story_Standard.md` (and its Phase 2 template) names PO as the only acceptor in the §7 role table, the Done row (`:24`, `:180`) and §14 (`:369`, `:371`). Each becomes "the PO, or the orchestrator acting as PO under `po_execution: orchestrator`". §14's tracked-split rule (`:376`) adds: "in `orchestrator` mode, the scope decision is the user's".

---

## 7. State, Telemetry and Retro in `orchestrator` Mode

| Concern | Design |
|---|---|
| PO memory | The orchestrator reads `Product_Owner_Memory.md` at its first PO activity in the run. It writes durable facts in the PO format, `## Stored Facts` per `Agent_Common_Read_On_Demand.md §1` on the Bootstrap route |
| PO Working Record | Written at the end of each inline PO activity that writes it today (`po-core` rules). Stage 4 closure still skips it |
| Access control | Amend the "read and update only your own record" rule in `Agent_Common_Bootstrap.md` §1, `Agent_Common_Working_Record.md` and their templates: *the orchestrator acting as PO under `po_execution: orchestrator` owns the PO record and memory for that activity* |
| Orchestrator's own state | Unchanged. PO facts never go into orchestrator state, and orchestrator state never goes into PO records |
| Retro identity (B6b) | Recorded as `Orchestrator`, the actual actor, as Core and Bootstrap §7 already require for fast paths (`Agent_Common_Core.md:67`, `Agent_Common_Bootstrap.md:120`). No Common §7 amendment |
| Telemetry role (B6a) | `PO` (the normalised value for Product Owner; `Product_Owner` is rejected by `telemetry.py:64-69`) |
| Telemetry session mode | New `session_mode: orchestrator_inline`, an additive enum value in schema v1, in `telemetry.py` and its Phase 2 template |
| Telemetry usage (B6a, N5, NB1) | One row per inline PO activity with `usage_source: unavailable`. In-session boundary capture is **not** used. `telemetry.py boundary` checks session ownership over the whole transcript prefix (`telemetry.py:364-365`, `:476`), so it fails on a continued orchestrator session ("conflicting native session identities"). The orchestrator also has no discovery for its own transcript (`find_claude_agent_transcript`, `:167`, matches subagents only). The saving is measured instead by comparing **per-story totals** across modes: the spawned-PO rows a `subagent` story produces versus the orchestrator session total of an `orchestrator` story. Per-activity inline measurement is a possible later story: slice-only ownership, own-transcript discovery and a multi-session test |
| Attribution split (N8) | Telemetry records the **role performed** (`PO`, with `session_mode: orchestrator_inline` marking the actor). The retro records the **actual actor** (`Orchestrator`), as Common §7 requires. Both are deliberate |
| Read manifest | No worker spawn means no manifest, as with existing orchestrator-direct paths. Inline activities record the loaded skill names in the pipeline state |
| Model policy | Inline work runs on the orchestrator's model. The `closure` and `standard` policies apply only to spawns. The `orchestrator_inline` rows let adopters verify the cost |

---

## 8. Ripple Checklist

Lists are a minimum. Any other site using the same mechanism is in scope as well.

**Phase 0 (`agent-security`):**
- `Agent_Common_Core.md` §2 and §4, `Agent_Common_Bootstrap.md`, and their Phase 2 templates (generated blocks)
- every citation of Core §2/§4 across rules, instructions and workflows
- `orchestrator_instructions.md` and its Phase 2 shared template (load at workflow start, Shell Safety read)
- `docs/reviews/ST-000264_Common_Ownership.json` (ownership of the moved sections)
- `build_bundle.py`, `migration-inventory.json` and `generate_wrappers.py` (shared canonical skill plus discovery wrappers)
- the inline-copy generator and its `--check` mode

**Phase 1 (PO skills and retirement):**
- **Routing code:**
  - `read_manifest.py:134` hard-codes `<role>_Rules_Bootstrap.md` (B8); it maps PO to `po-core` instead
  - `scripts/test/test_read_manifest.py:80`
- **`read-routing.json`:**
  - PO citations at `:263`, `:410`, `:552`, `:574`, `:586`, `:670` and `:1334` (the `story_body_write` trigger)
  - a new `po_validation` task for `po-validate-ac`
- **Workflows:**
  - `Plan_Sprint_Workflow.md`, `Refine_Sprint_Workflow.md`, `Shared_Pipeline_Stages.md`, `Sprint_Workflow.md`, `Create_Stories_Workflow.md`, `Workflow_Guide.md`
  - `workflows/commands/Analyst_Workflow.md`, `workflows/commands/Audit_Agent_Files_Workflow.md`
  - their Phase 2 `*_Shared_template.md` files and the github/strict wrappers
- **Rules:** `Developer_Rules_*`, `QA_Rules_*`, `Technical_Lead_Rules_Bootstrap.md`, `Technical_Lead_Rules_Read_On_Demand.md`, `UI_UX_Designer_Rules_*`, `Audit_Rules.md`, `Retro_Rules.md`, and `Agent_Common_*` (including the bare `Story_Standard_PO.md` citations at `Agent_Common_Core.md:34` and `Agent_Common_Bootstrap.md:62`)
- **Phase 2 templates:** `templates/workflows/Sync_Devkit_Workflow_template.md` (retirement review and porting step), `templates/shared/Repo_Root_Shared_template.md`, `product_owner_instructions_template.md`
- **Bundle:** `build_bundle.py`, plus `bundle/deployment.json` and assets regenerated and checked with `build_bundle.py --check`
- **Engine:** `deployment.py` and `lifecycle.py` (resolution generation, customised-file conflict)
- **Tests and fixtures:**
  - `scripts/test/test_branch_preflight.py:355`
  - `test_phase2_legacy_contracts.py`, `test_phase2_deployment.py`, `test_phase2_bundle.py`
  - the legacy fixtures `v0.1.48.zip`, `v0.1.49.zip`, `v0.1.50.zip` (migration tests)
- **Scripts:** `migration-inventory.json`, `telemetry.py`, `retro_completion.py`
- **Context and docs:** `Project_Priming_*` (§15 ripple checklist for splitting a shared rules file applies), `changes.json` and `CHANGELOG.md`

**Phase 2 (setting and orchestrator mode):**
- `Story_Standard.md` §7, the Done row and §14 (`:24`, `:180`, `:369`, `:371`, `:376`) and its Phase 2 template (§6)
- `Agent_Common_Bootstrap.md` §1 and `Agent_Common_Working_Record.md` access-control amendment, plus templates (§7)
- `telemetry.py` and its Phase 2 template (`orchestrator_inline`, bounded inline extraction)
- `orchestrator_instructions.md`, all §5 workflows, the bundle entry for `project_settings.json`, and the init/sync workflows

---

## 9. Phasing

| Story | Scope | Estimate | Depends on | Exit criteria |
|---|---|---|---|---|
| **0** `agent-security` | Skill, shared canonical file plus wrappers, **skill renderer in `generate_wrappers.py`** (N7), inline-copy generator and drift check, Core and Bootstrap generated blocks, orchestrator load (skill and Shell Safety) | 8 | — | Drift check green; orchestrator loads the skill at workflow start; Phase 0 ripple done |
| **1a** PO skills, internal | Ten skills (canonical plus wrappers), slim instructions, delete the three internal PO files and their wrappers, `po_validation` task, internal ripple. PO routing in `read_manifest.py` and `read-routing.json` switches to `po-core` **for the internal layout only**, through the registry's per-layout mapping (`read_manifest.py:133-141`). `build_bundle.py:185-196` ships both files to targets, which don't have the skills yet (NB2) | 13 | 0 | All internal gates green; bare-citation validator green for the internal corpus; target-layout PO manifests unchanged and valid |
| **1b** PO skills, distribution | Skill templates, shared canonical plus per-provider wrappers in the bundle, slim instructions template, template ripple, and the **target-layout** PO routing switch to `po-core`. The old PO templates **stay** in the bundle, unused, so every merge is consistent | 8 | 1a | Bundle `--check` green; targets receive the skills; target-layout PO manifests resolve to `po-core` |
| **1c** Retirement | Remove the PO templates; shared and legacy retirement entries; resolution generation for unmodified receipt-based files; customised-file conflict; Sync workflow porting step; legacy migration tests; bare-citation validator over templates and bundle; CHANGELOG | 8 | 1b | Each legacy fixture migrates without leaving PO files (manual reviewed resolution); a customised file raises the porting conflict; a stock **receipt-based** target syncs with no manual resolution |
| **2a** Setting and contracts | `project_settings.json` plus bundle entry, state pinning, `Story_Standard.md` and access-control amendments, telemetry enum with `usage_source: unavailable` inline rows | 8 | 1a | Absent setting resolves to `subagent`; contract amendments merged; `orchestrator_inline` rows validate |
| **2b** Orchestrator mode | The §5 matrix in every workflow, forced spawns, scope-change escalation, observation checks, orchestrator skill loading | 13 | 0, 1a, 2a | Every §5 row implemented and covered by a test or a scenario |

**Total: 58 points**, against sprint capacity of 60. Every story is at most 13.

**Merge order:** 0 → 1a → (1b → 1c) and (2a → 2b), with 1b/1c and 2a/2b able to run in parallel. Each merge leaves `main` consistent: 1b keeps the old templates until 1c retires them.

**Release boundary:** all six stories ship in **one release**. The `release` workflow is dispatched only after all are merged.

**Capacity risk:** 58 of 60 leaves almost no buffer, and the single-release rule means any slip delays the whole release. The sprint should carry no other stories. If a story overruns, the release waits for it. The scope is not cut, because a partial release would ship skills without retirement, or the setting without its guards.

---

## 10. Validation

- `python scripts/validate_internal_harness.py`, `python .mt-agent-devkit/scripts/generate_wrappers.py --check`, `python -m unittest scripts.test.test_internal_harness`, `python scripts/validate_templates.py` and `bash scripts/test/run.sh` all exit 0
- New checks:
  - every `po-*` skill and `agent-security` has a shared canonical file plus a valid-frontmatter wrapper in every provider's discovery surface, internal and bundle
  - every skill-to-skill `requires` reference resolves
  - **no bare-filename or `§`-citation of a retired file** (`Product_Owner_Rules_Bootstrap.md`, `Product_Owner_Rules_Read_On_Demand.md`, `Story_Standard_PO.md`) in the internal corpus, the Phase 2 templates or the bundle content (B3a)
  - the generated `agent-security` blocks in Core, Bootstrap and their templates match the skill byte-for-byte (`--check`)
  - the orchestrator instructions load `agent-security` before the first issue/PR read
  - `read_manifest.py` builds valid manifests for every PO task, including `po_validation`, without the deleted bootstrap file
  - legacy migration tests (`v0.1.48`, `v0.1.49`, `v0.1.50`): no PO rule file remains and the skills are present
  - retirement: a stock file auto-resolves; an `adapted: true` file raises the porting conflict
  - `po_execution` absent → `subagent`; an unrecognised value → `subagent` plus a report
  - Stage 3 with QA as the implementer, and Plan Sprint, spawn in both modes
  - in `orchestrator` mode, a defer, split or any AC body edit after Stage 1 routes to the user
  - during 1a, target-layout PO manifests still build and validate
  - `orchestrator_inline` telemetry rows validate against the schema

---

## 11. Non-Goals

- Changing QA, TL or Developer gates, or the Merge Procedure
- Applying the role-skill pattern to other roles. Phase 0 touches every role only for `agent-security`. This proposal is shaped so #265 (Developer stage profiles) can reuse it
- Moving Shell Safety or the credential gate into skills
- Enabling the Core route (`verified_providers`)
- Editing the frozen `.claude/agents/templates/` corpus

---

## 12. Decisions

| ID | Decision | Outcome |
|---|---|---|
| D1 | Where the setting lives | `.mt-agent-devkit/project_settings.json`, `project_owned` + `create_if_absent`, with no entrypoint mirror (§4) |
| D2 | Retired rule files | Deleted in the same release, internally and in targets, through the retirement phase plus the new resolution and conflict handling (§3c). No stubs |
| D3 | Telemetry | Role `PO`, additive `session_mode: orchestrator_inline` in schema v1, inline rows with `usage_source: unavailable`, saving compared through per-story totals across modes (§7) |
| D4 | Stage 3 with QA as the implementer | Always spawn a PO, in both modes (§6) |
| D5 | Plan Sprint in `orchestrator` mode | Always spawn a PO. Planning reads the most context, and a spawned PO on the `standard` policy is likely cheaper than the orchestrator's model |
| D6 | Security rules | Shared `agent-security` skill; generated inline copies in Core and Bootstrap; the orchestrator loads the full skill; no manifest entry (§3d) |
| D7 | Scope changes after Stage 1 in `orchestrator` mode | Defer, split and **any** AC body edit escalate to the user; never decided inline (§5, §6) |
| D8 | Retro identity for inline PO work | `Orchestrator`, the actual actor, per Common §7 (§7) |

---

## Revision History

| Rev | Change |
|---|---|
| 3 | TL re-review:<br>• **NB1:** inline telemetry uses `usage_source: unavailable`, with the saving compared through per-story totals; in-session capture dropped<br>• **NB2:** 1a switches PO routing for the internal layout only; targets switch in 1b<br>• **N7:** skill renderer moved to story 0<br>• **N8:** attribution split stated<br>• **N9:** resolution conditions and the legacy manual path<br>• **N10:** any AC body edit after Stage 1 escalates |
| 2 | TL review on PR #286:<br>• **B1:** shared canonical skills in targets<br>• **B2:** explicit legacy retirements and migration tests<br>• **B3:** bare-citation validator, resolution generation for unmodified files, customised-file conflict<br>• **B4:** generated inline copies in both Common routes; no manifest entry; route-specific shell authority<br>• **B5:** `Story_Standard.md` amendments, scope-change escalation, fast-path rationale<br>• **B6:** telemetry role, inline measurement, `Orchestrator` retro identity<br>• **B7:** six stories with estimates, corrected dependencies<br>• **B8:** `read_manifest.py`, `po_validation` task, extended ripple<br>• **N1–N6:** content map completed, size targets restated, inline judgement checks, setting ownership, measurement, editorial order |
| 1 | Initial design (commit `ca0819b`) |
