# Developer Skills Proposal

**Feature:** `role-skills`
**Status:** Revision 4. **TL-approved** on PR #306 (approved with changes; C1 and C2 folded in). Ready for story creation
**Date:** 2026-11-03
**Scope:** The devkit's internal harness (`.mt-agent-devkit/`) and the distributed Phase 2 templates (`.mt-agent-devkit/distribution/phase2/templates/`). The frozen legacy corpus under `.claude/agents/templates/` is not touched.
**Precedent:** `PO_Skills_And_Orchestrator_PO_Proposal.md` (Sprint 9). This proposal reuses its layout, generators, retirement mechanism and validators. It does not repeat their design.

---

## 1. Decisions Already Made (user, 2026-11-03)

| ID | Decision |
|---|---|
| U1 | #263, #265 and #266 stay on hold and are not used. Apply the PO skill pattern. Re-review those stories after this ships and consider closing them |
| U2 | Every Developer "how-to" (branching, committing, clean code, asking PO/TL, writing memory, and so on) becomes a skill. `developer_instructions.md` defines which skills load at spawn and which load on demand |
| U3 | `Agent_Common_Bootstrap.md` is split into skills as well, and the old file is **kept**. The Developer reads the new skills; the other roles keep reading the old file until they migrate. The duplication is accepted as temporary |
| U4 | Design around #303: each skill loads right before the action it governs, and checks that are easy to miss are numbered steps inside the skill |
| U5 | No skill may duplicate a PO skill. Where Developer and PO content overlap, the shared part becomes a common skill |
| U6 | A how-to that another role also uses becomes a common skill. Developer and the other roles' files and routes point to it |
| U7 | Routing, manifests and distribution follow the PO approach: internal layout first, then distribution, then retirement |
| U8 | Reuse the tools built for the PO migration |

---

## 2. Problem and Expected Saving

A Developer spawn reads this before any work:

| Read at spawn (today) | Size |
|---|---|
| `Agent_Common_Bootstrap.md` | 18.3 KB |
| `Developer_Rules_Bootstrap.md` | 18.7 KB |
| `developer_instructions.md` | 4.3 KB |
| **Total** | **41.3 KB**, plus Project Priming, the Working Record and memory |

**Honest expectation.** `Developer_Rules_Bootstrap.md` v2.0 records a failed split: a full story spawn used all of §1–§6, so moving them on demand saved 3.6%. The same applies here. A full implementation story still loads most skills before it finishes, so its total read stays close to today's, and it makes more read calls. The gains are:

1. **Narrow spawns** (peer review, refinement, answering a question) stop loading the implementation, pre-PR and git rules. A spawn of this kind drops from about 41 KB to about 15 KB (byte arithmetic, not a measurement).
2. **Correctness.** A rule read right before its action is applied more reliably than one read 40 KB and many tool calls earlier (#303).
3. **One owner per how-to.** Several rules exist in Developer, TL and QA copies that have already drifted (§6).

Story B reports bytes read **and read calls** per spawn type (§10). A native token comparison is out of scope; #266 can be re-scoped for it later.

---

## 3. Skill Set

Each skill is a `SKILL.md` with `name` and `description` frontmatter, under `.mt-agent-devkit/skills/<name>/`, with generated provider wrappers (PO proposal §3b). A skill names the skills it requires and never restates their rules. Size target: ≤ 4 KB per skill, ≤ 1.5 KB for `dev-core`.

**Two layers, two sources.** The internal skill (`.mt-agent-devkit/skills/<name>/SKILL.md`) and its Phase 2 template (`templates/skills/<name>/SKILL_template.md`) may differ where the layers differ: placeholders, the Working Record cap (10,000 internally, project-set in targets), the check table in `pre-pr-gate`, the devkit-only rules. Each layer's skill is the only owner of that layer's text (B1).

### 3a. Common skills (new)

Named without a role prefix, like `agent-security` and `comment`.

| Skill | Purpose | Absorbs | Also used by |
|---|---|---|---|
| `pre-work` | Read order at fresh start and at resume, the native-reader and full-coverage gate, manifest consumption, provider bindings | Common Bootstrap §1 (read-order paragraphs) | All roles (after they migrate) |
| `token-efficiency` | Tool-call conventions | Common Bootstrap §3 | All roles |
| `shell-rules` | Adapter-first shell choice, permissions, temporary body files, mutation safety | Common Bootstrap §6, `Agent_Common_Shell_Safety.md` | All roles; the orchestrator through `agent-security` part C |
| `working-record` | Snapshot format, retention, character cap, access control, Blockers & Watch-outs | Common Bootstrap §1 item 2, `Agent_Common_Working_Record.md`, Dev §19, the TL and QA "Reporting" bullets on the Working Record | All roles; `po-core` points to it |
| `agent-memory` | Fact format, Troubleshooting Facts, two-tier memory retrieval and writing | Common On-Demand §1 and §8, `Agent_Common_Memory.md` | All roles; `po-core` points to it |
| `troubleshooting` | Scan your own fixes first, then diagnose and record back | Common On-Demand §2, `Agent_Common_Troubleshooting.md`, TL §14, QA §13 | All roles |
| `credential-gate` | Missing secret means stop and report, never a dummy value | Common On-Demand §6, `Agent_Common_Credential_Gate.md`, the Dev §5 bullet | Every implementer and QA |
| `retro` | Trigger definitions, detection during work, recording each trigger **when detected** with `retro_completion.py record --state required`, clean/unknown reporting at each handoff | Common Bootstrap §7, `Agent_Common_Retro.md` (detection) | All roles |
| `retro-contribution` | Writing a role contribution, loaded only when a trigger was recorded | Common On-Demand §3 | All roles |
| `handoff` | Runtime-state handoff before signalling completion | Common On-Demand §5, `Agent_Common_Stage_Transition.md`, TL §12, QA §12 | Implementer and reviewer roles |
| `raise-question` | Who owns a question (PO or TL), the question comment, the pre-start gate, the mid-implementation consultation report, blockers, live user instruction conflicts | Dev §2 step 2, §7, §12, §13; QA §10, §11 and On-Demand §2; TL §10; the UI/UX mid-implementation rule | Every implementer |
| `project-docs` | Where documents go (`context/Document_Index.md`, R3) and how documents are named | Dev §4 (naming) and §8; TL §6; QA §5; the placement half of `po-plan-docs` | All roles; `po-plan-docs` keeps Plan Commit and requires this skill |
| `git-workflow` | Branch preflight `inspect`/`create`, branch naming, Conventional Commits, `[skip ci]` by CI path filter, PR title and body, post-QA merge sync | Dev §2 step 3, §6; TL §5 (commits); the UI/UX commit rule | Every implementer |
| `change-metadata` | `changes.json` entry and `descriptions` format, the `CHANGELOG.md` entry rule, `_template` naming. **Internal only, never distributed** (B5) | Dev §4 (`changes.json`, `_template`), Dev §5 (CHANGELOG) | Internal implementers write it; QA checks it (`QA_Rules_Bootstrap.md:75`) |
| `pre-pr-gate` | Local checks by change type, aggregate local-CI command, short-circuiting gates, production-build evidence, local-verify, rename/refactor reference sweep, PR check note, pre-merge checklist (without "Developer sets `status:done`", N4) | Dev §5; TL On-Demand §3; QA On-Demand §1 | Every implementer |
| `pr-review` | Reviewer procedure: read the diff, CI actually ran on the current head SHA, reviewer gate, inline comments, issue notify comment, the `gh pr checks` paste, verdict through `gh pr comment` | Dev §14, §16, the Dev §20 CI-paste note; the shared part of TL On-Demand §5 | Dev as peer reviewer; TL keeps its approval authority rules in its own file until the TL migration |
| `clean-code` | Clean code rules; in targets also the Development Standard compliance, source-file naming, shared-helper scope and caller-trace rules | `Clean_Code_Rules.md`; target Dev Bootstrap §4 | Dev, TL |

**Changed existing skills (N3):**
- `comment` already owns the same-pass body update rule (`comment` SKILL.md rule 5). The duplicates in `po-comment:13`, `po-answer-questions:16` and Dev On-Demand §20 are deleted and point to it.
- `po-core` replaces its "PO Records" text with pointers to `working-record` and `agent-memory`, keeping only PO-specific facts (closure skips the Working Record; the orchestrator-as-PO exception).
- `po-plan-docs` requires `project-docs` and keeps only Plan Commit.

### 3b. Developer skills

| Skill | Purpose | Absorbs (internal / target) |
|---|---|---|
| `dev-core` | Role boundaries, status ownership, "do not tick AC", story-file format by mode, the skill load map (§4) as the single list of which skill loads when | Dev §1, §3; `Story_Standard_Dev.md` (folded in); target §4 story files |
| `dev-implement` | Numbered pre-start steps: read the story and touched files, raise questions and wait (requires `raise-question`), design-first rule, UI prototype reference, spec-first rule (target), then start (requires `git-workflow`) | Dev §2; target §2 and the §5 spec-first rule |
| `dev-deliver` | After the PR opens: PR-opened comment, status transitions, Deliverables links, review-to-testing handoff, fix rounds (address, push, re-run `pre-pr-gate`, re-request review) | Dev §6 (delivery transitions) |
| `dev-verify` | Technical doc divergence (both layers); touched-endpoint verification and behavioral sandbox (target only, the internal skill says they do not apply to a Markdown-only repo) | Target On-Demand §16–§18 |
| `dev-refine` | Sprint refinement procedure | Dev On-Demand §15; target §14 |
| `dev-hotfix` | Post-Done fix branch and cycle (requires `git-workflow`, `pre-pr-gate`) | Dev On-Demand §17; target §13 |

Peer review uses `pr-review` directly, so there is no `dev-review` skill. The full target mapping is §9.

---

## 4. Load Map (`developer_instructions.md`)

The instructions file keeps the role summary, record paths and Feature Context. Its "Selected Common Routing" paragraph and the "read `Agent_Common_Bootstrap.md` in full" checklist line are replaced by this table (N5). `dev-core` repeats the point-of-use column so the rule is in front of the agent at every step.

| When | Skills |
|---|---|
| **At spawn, every task** | `agent-security`, `pre-work`, `token-efficiency`, `shell-rules`, `retro`, `dev-core` |
| **At spawn, the task skill named in the assignment** | `dev-implement` (story), `pr-review` (peer review), `dev-refine` (refinement), `dev-hotfix` (post-Done bug) |
| Before posting any comment or editing the issue body | `comment` |
| A question or blocker comes up, or a live user instruction conflicts with the thread | `raise-question` |
| A technical doc is wrong, a story touches an endpoint, or a behavioral change needs sandbox verification | `dev-verify` |
| Creating or moving a document or file | `project-docs` |
| Writing code, or a clean-code or refactor story | `clean-code` |
| Before creating a branch, committing or pushing | `git-workflow` |
| Before opening a PR | `change-metadata` (internal only), then `pre-pr-gate` |
| After the PR opens, and on each fix round | `dev-deliver` |
| Tooling or environment blocker | `troubleshooting` |
| Verification needs a secret you don't have | `credential-gate` |
| Retrieving or writing a memory fact | `agent-memory` |
| A retro trigger was recorded, before writing the contribution | `retro-contribution` |
| Before stage handoff | `handoff` |
| Before any Working Record write (N6) | `working-record` |

If the assignment names no task skill, the Developer reports that to the orchestrator rather than guessing, as the PO does. The spawn packets in `Shared_Pipeline_Stages.md` (`:254`, `:339`) name the task skill (N5).

---

## 5. Resumed Sessions

A fix round usually resumes the same Developer session, so the skills it already read are still in its context.

| Situation | What is loaded |
|---|---|
| Same session resumed, skills unchanged | Spawn-time skills are **not** re-read. Point-of-use skills **are** re-read right before their action (for example `pre-pr-gate` before the fix push). They are small and cached, and #303 showed that recall from earlier in the session misses checks |
| Session expired, or a fresh spawn | Full spawn set again, then point-of-use as normal |
| A skill file changed since it was read (sync or merge mid-sprint), or provenance is unknown | Re-read it. Unknown is treated as changed, matching the existing Common §1 rule and the manifest's `content_sha256` receipts |

---

## 6. Drift Found While Mapping

Fixed by the common skills taking one owner:

- **TL pre-PR gate is weaker than the Developer's.** `Technical_Lead_Rules_Read_On_Demand.md §3` exempts "template / workflow / rules / docs only", while Dev §5 and QA On-Demand §1 require the harness validators. `pre-pr-gate` adopts the stricter rule, which changes **TL-as-implementer** behavior only (R2, N2).
- **Stale citation.** `Story_Standard.md:111` cites `Developer_Rules_Read_On_Demand.md §5`; §5 is in the Bootstrap file. Repointed to `pre-pr-gate`.
- **Two document indexes.** QA §5 points to `context/Document_Index.md`; Dev, TL and PO point to the shorter `Project_Priming_Read_On_Demand.md §6`. Resolved by R3.
- **Peer-review CI rules** live in `Technical_Lead_Rules_Read_On_Demand.md §5` and Dev §14 cites them. `pr-review` owns the shared part.
- **Contradiction.** Dev §5 pre-merge item 6 has the Developer set `status:done`, which Dev §3 forbids. Not carried over (N4).

---

## 7. Generated Copies in the Kept Common Files (U3, B1, B4)

The other roles keep reading the old Common files. To stop the temporary duplicate from drifting, every Common text a skill absorbs becomes a **generated block** copied from that skill, as `generate_security_blocks.py` does today for `agent-security` parts A and B.

### 7a. Generator

`generate_security_blocks.py` is generalised into `generate_common_blocks.py` (the security parts become two rows of its table):

- **Explicit part markers.** A skill marks each copyable part with `<!-- part: <name> -->` … `<!-- /part: <name> -->`. The generator no longer bounds a part by the next `## ` heading, so parts may contain their own headings (On-Demand §1 has `## Stored Facts` and `## Troubleshooting Facts`).
- **Two sources.** Internal targets are generated from the internal skill; Phase 2 template targets from the Phase 2 skill template. A target never takes text from the other layer.
- **Mapping table** in the generator (one row per block): skill, part, layer, target file, block name. `--check` fails CI when any block differs from its part, when a block is missing or duplicated, or when a part has no target.

### 7b. Part-to-section map

| Target (internal; the Phase 2 template has the same blocks from the Phase 2 skill) | Block | Skill part |
|---|---|---|
| `Agent_Common_Bootstrap.md` §1 (read-order paragraphs) | `pre-work/read-order` | `pre-work` |
| `Agent_Common_Bootstrap.md` §1 item 2 (Working Record update, retention, format) | `working-record/format` | `working-record` |
| `Agent_Common_Bootstrap.md` §2, §4 | existing `agent-security` A, B | `agent-security` |
| `Agent_Common_Bootstrap.md` §3 | `token-efficiency/conventions` | `token-efficiency` |
| `Agent_Common_Bootstrap.md` §5 routing table | not generated; it is the other roles' routing, hand-maintained | — |
| `Agent_Common_Bootstrap.md` §6 | `shell-rules/rules` | `shell-rules` |
| `Agent_Common_Bootstrap.md` §7 | `retro/detection` | `retro` |
| `Agent_Common_Read_On_Demand.md` §1 | `agent-memory/facts` | `agent-memory` |
| `Agent_Common_Read_On_Demand.md` §2 | `troubleshooting/protocol` | `troubleshooting` |
| `Agent_Common_Read_On_Demand.md` §3 | `retro-contribution/writing` | `retro-contribution` |
| `Agent_Common_Read_On_Demand.md` §5 | `handoff/state` | `handoff` |
| `Agent_Common_Read_On_Demand.md` §6 | `credential-gate/gate` | `credential-gate` |
| `Agent_Common_Read_On_Demand.md` §8 | `agent-memory/two-tier` | `agent-memory` |
| `Agent_Common_Shell_Safety.md` body (B4: live through `agent-security` part C and the `shell_safety` trigger) | `shell-rules/safety` | `shell-rules` |
| `Agent_Common_Working_Record.md` body (B4: live through the `working_record` trigger) | `working-record/format` | `working-record` |
| `Agent_Common_Core.md` §3, §7 and the `Memory`, `Retro`, `Troubleshooting`, `Credential_Gate`, `Stage_Transition` modules | the matching parts above | as above |

The last row closes R4 fully: the Core-route files keep their paths, ids and references, so `capability_routes` needs no change in story A1, but their absorbed text is generated, so no rule has two hand-written owners on any route. Test impact (TL re-review C2):
- **A1:** the existing Core clause test in `test_common_capabilities.py` (`NOT VERIFIED`, truncation, sticky and the other asserted clauses) must keep passing once Core text is generated from the skills.
- **B:** two tests use the Developer as the sample role under a verified provider: `test_clean_required_and_forbidden_capabilities` (expects Core plus `Developer_Rules_Bootstrap.md`) and the legacy-memory test (expects `common` = `Agent_Common_Bootstrap.md`). Both break when the Developer gets its own Common skills and skips `capability_routes`. Story B switches them to TL or QA and adds the Developer skip test.

### 7c. What changes for the other roles

The skills rewrite some rules as numbered steps (U4), so the generated text the other roles read is **reworded, not identical**. The exit criterion is therefore a rule-by-rule ownership map (every absorbed rule → its skill part, none lost or weakened), plus the generator `--check`, not byte identity with today's text.

---

## 8. Routing and Manifests (U7, B2, B3)

### 8a. `read_manifest.py`

| Change | Detail |
|---|---|
| Per-role Common override | New registry key `common` beside `bootstrap`: `common.<role>.<layout>` is a list of skill reads. The first keeps the id `common`, so `priming`, `peer_review` and every `after: ["common"]` still resolve; the rest get their own ids (`common_agent_security`, `common_token_efficiency`, `common_shell_rules`, `common_retro`) with `after: ["common"]`. Developer gets the override for `internal` in story B and `target` in story C |
| Bootstrap override | `bootstrap.Developer.<layout>` → `dev-core`, the existing PO mechanism (`read_manifest.py:135`) |
| `agent-security` as a manifest entry | The Developer no longer reads the generated copy in Common, so `agent-security` becomes a Developer manifest entry (via the override) and stays in the load map for non-manifest spawns. `orchestrator_instructions.md:14` ("never a read-manifest entry") is amended to "a manifest entry only for roles whose Common is skill-based" |
| Role source substitutions | New registry key `role_sources.<role>.<layout>`: a map from an old source (with optional section) to a **list** of skill paths, applied in `add()` after formatting. It lets shared trigger and task entries route the Developer to skills without forking every entry. Rules (TL re-review C1):<br>• **One entry per skill.** The first keeps the original id; the rest get `<id>_<n>` with the same `after`.<br>• **Coverage becomes full.** A substituted entry's `coverage` is reset to `{"kind": "full"}`, because a skill has no `## N.` section headings (`trigger_memory_fact` §8, `trigger_memory_shape` §1, the On-Demand §2, §3, §5, §6 entries).<br>• **Duplicates by source are removed.** When two entries resolve to the same skill source (both `memory_fact` reads → `agent-memory`; `completion` → `retro`, already read at spawn), the first entry is kept, later ones are dropped, and every `after` that named a dropped id is rewritten to the kept id.<br>The `completion` trigger maps `Agent_Common_Bootstrap.md` (full) → [`retro`, `handoff`] for the Developer; after deduplication only `handoff` is added |
| `capability_routes` | Skipped for a role with a `common` override; the skill route is that role's only Common authority. The bare `next(...)` lookups in route building (`:157`, `:212`, `:223`, `:224`, `:237`) raise `Blocked` with a reason instead of `StopIteration`. A test enables a provider in a fixture registry and asserts the Developer route keeps its skills |

### 8b. `read-routing.json` inventory

Every entry that reads a Developer rule file, `Clean_Code_Rules.md`, or Common text a skill absorbs:

| Entry | Roles | Today | After |
|---|---|---|---|
| task `peer_review` (`review_checklist`, `review`) | Dev | Dev On-Demand §14, §16 (target §9, §12) | `pr-review` |
| trigger `story_comment` | Dev | `comment` + Dev §20 | `comment` only |
| trigger `document_update` → `trigger_document_update` | Dev | Dev On-Demand §8 | `project-docs` |
| trigger `document_update` → `trigger_document_paths` | all | Priming On-Demand §6 | `context/Document_Index.md` (R3) |
| trigger `consultation` | Dev, UI/UX | Dev §12, UI/UX On-Demand | `raise-question` (both roles) |
| trigger `live_conflict` | Dev, UI/UX, QA | Dev §13, UI/UX, QA On-Demand §2 | `raise-question` (all three) |
| trigger `report_blocker` | Dev | Dev On-Demand §7 | `raise-question` |
| trigger `pre_pr` | Dev, TL | Dev Bootstrap §5, TL On-Demand §3 | `pre-pr-gate` (both) |
| task reads `tl_implementation_3`, trigger `trigger_tl_pre_pr` | TL | TL On-Demand §3 | `pre-pr-gate` |
| task `qa_implementation` pre-PR read | QA | QA On-Demand §1 | `pre-pr-gate` |
| trigger `source_review` | TL, Dev | `Clean_Code_Rules.md` | `clean-code` |
| trigger `clean_code_change` | Dev | `Clean_Code_Rules.md` | `clean-code` |
| triggers `technical_doc_divergence`, `endpoint_change`, `behavioral_verification` | Dev (target) | target Dev On-Demand §16–§18 | `dev-verify` |
| trigger `development_convention` | Dev (target) | `docs/wiki/Development_Standards.md` | unchanged (a project document, not a rule file) |
| triggers `tooling_failure`, `credential_gate`, `memory_fact`, `memory_recall`, `retro_required`, `runtime_handoff` | all / Dev-TL-QA | Common On-Demand sections | other roles: unchanged paths (generated text). Developer: the matching skill through `role_sources` |
| trigger `completion` | all | `Agent_Common_Bootstrap.md` full | other roles unchanged; Developer `retro` + `handoff` through `role_sources` |
| triggers `shell_safety`, `working_record` | all | the Common modules | other roles unchanged (generated text); Developer `shell-rules`, `working-record` |
| trigger `simple_memory_fact`, `design_first` | PO/BA/UI/UX; all | Common On-Demand §1; Priming §4 | unchanged |

**Decision (B3):** the Developer reads the **skill**, never the generated copy. Other roles read the generated copy where they still read Common, and the skill where their own rule now points to a common skill (U6).

### 8c. Other ripple (N5)

- `Technical_Lead_Rules_Read_On_Demand.md:108` (`Clean_Code_Rules.md`) → `clean-code`.
- `Apply_Retros_Workflow.md` `:58`, `:84`, `:123`: Developer lessons target the owning skill template, not the retired rules template.
- `migration-inventory.json`: `retired` entries for the four retired files, `skill` entries for every new skill.
- The retired-citation validator allows history mentions inside `**Version:**`/`**Previous:**` lines (TL Bootstrap `:143`, QA On-Demand `:3`, `:44`).

---

## 9. Target-Layout Mapping (B5)

The Phase 2 Developer templates differ from the internal files. Every target section has an owner:

| Target section | Owner |
|---|---|
| Bootstrap §1 Implementation Read Contract | `dev-core` |
| §2 Before Starting a Story | `dev-implement` (+ `raise-question`, `git-workflow`) |
| §3 Story Status Management | `dev-core` |
| §4 Code Quality & Naming: Development Standard compliance, source naming, shared-helper scope, caller-trace | `clean-code` (Phase 2 template) |
| §4 Story files (github/strict) | `dev-core` |
| §5 Testing & Verification: local-verify, check table, aggregate command, short-circuit, production build, test note, pre-merge items 1–6, rename/refactor sweep | `pre-pr-gate` (Phase 2 template) |
| §5 credential bullet | `credential-gate` |
| §5 spec-first rule | `dev-implement` |
| §5 pre-merge item 7 (Developer sets `status:done`) | dropped (N4) |
| §6 Git Workflow | `git-workflow` |
| §12 Routing Table | replaced by the load map (§4) |
| §13 Always-On | `working-record` |
| On-Demand §7 Reporting & Blockers, §10 Consultation, §11 Live Conflicts | `raise-question` |
| §8 Document Placement | `project-docs` |
| §9 Peer Review, §12 Developer as Reviewer | `pr-review` |
| §13 Hotfix | `dev-hotfix` |
| §14 Refine Sprint | `dev-refine` |
| §15 Comment Standard | `comment`; the CI-paste note to `pr-review` |
| §16 Doc Divergence, §17 Endpoint Verification, §18 Behavioral Sandbox | `dev-verify` |

**Internal only, not distributed:** `change-metadata` (the bundle has no entry for it) and the `_template` naming rule. The `project-docs` Phase 2 template omits it.

---

## 10. Phasing

| Story | Scope | Estimate | Depends on | Exit criteria |
|---|---|---|---|---|
| **#303** Point-of-use loading for inline PO | The #303 proposal and its related gaps (R6) | 3 | — | Inline PO procedure loads each skill before its action; per-action checks are numbered steps; citation and timing gaps fixed |
| **A1** Common skills and generator, internal | The 17 common skills (internal); `generate_common_blocks.py` with part markers, two-source table and `--check`; internal generated blocks per §7b (Common Bootstrap, On-Demand, Core and modules); rule-by-rule ownership map | 8 | #303 | Generator `--check` green; ownership map shows no lost or weakened rule; the existing Core clause test passes on generated text; all internal gates green |
| **A2** Other roles point to common skills, internal | TL, QA, UI/UX, BA rule pointers; `comment`, `po-core`, `po-comment`, `po-answer-questions`, `po-plan-docs` changes; R3 index; §6 drift fixes; the non-Developer `read-routing.json` rows in §8b | 5 | A1 | No duplicate authority between role files and common skills; routing tests green |
| **B** Developer skills, internal | The 6 Developer skills; load map and slim `developer_instructions.md`; `read_manifest.py` per §8a (common override, `role_sources` with list mapping, full coverage and source deduplication, `capability_routes` guard, `Blocked` lookups) with tests; the two Developer-sample capability tests moved to TL or QA plus a Developer skip test (§7b); Developer `read-routing.json` rows; `orchestrator_instructions.md:14` amendment; `Shared_Pipeline_Stages.md` packets; delete the internal Developer rule files and `Story_Standard_Dev.md`; measurement table | 13 | A2 | Developer manifests resolve to skills for every task and trigger; target-layout manifests unchanged and valid; citation validator green internally; bytes and read calls reported per spawn type |
| **C** Distribution | Phase 2 skill templates for all common and Developer skills (except `change-metadata`); Phase 2 generated blocks; target mapping per §9; bundle entries and wrappers; target-layout `common`, `bootstrap` and `role_sources` overrides | 13 | B | Bundle `--check` green; generator `--check` green for Phase 2; target Developer manifests resolve to skills; every §9 row has its text in the named skill template |
| **D** Retirement | Remove `Developer_Rules_Bootstrap.md`, `Developer_Rules_Read_On_Demand.md`, `Story_Standard_Dev.md`, `Clean_Code_Rules.md` from targets; legacy migration tests; validator over templates and bundle; `migration-inventory.json` retired entries; `Apply_Retros_Workflow.md`; CHANGELOG | 5 | C | Each legacy fixture migrates without leaving the files; a customised file raises the porting conflict |

**Total: 47 points.** Merge order #303 → A1 → A2 → B → C → D. A1 to D ship in one release, as the PO stories did; #303 may release earlier.

---

## 11. Resolved Design Points

| ID | Point | Resolution | Basis |
|---|---|---|---|
| R1 | `retro` timing | **Revised after TL review (N1).** Trigger definitions live only in `retro`, which loads at spawn so detection happens during work. Each trigger is recorded when detected (`retro_completion.py record --state required --trigger <kind>`), with a secondary note in the Working Record. Contribution writing is a separate skill, `retro-contribution`, loaded only when a trigger was recorded, so a clean role never loads writing guidance (Common §7) | Common §7 requires detection "during work and before each stage handoff" |
| R2 | Stricter pre-PR gate | Adopt the stricter rule in `pre-pr-gate`. Only TL-as-implementer behavior changes (QA On-Demand §1 already requires the validators, N2). It is a fix: `Project_Priming_Bootstrap.md §8` requires the validators for any `.mt-agent-devkit/**` change. CHANGELOG states the change | Priming §8 |
| R3 | Document index owner | `context/Document_Index.md` is the single path list; `Project_Priming_Read_On_Demand.md §6` becomes a pointer, and its Sprint Overviews row moves into the index | Fuller list, deployed to targets, self-declared owner |
| R4 | Common Core files and modules | **Revised after TL review (B4).** Paths, ids and references stay, so route code and tests are unchanged, but all absorbed text in them (including the live `Agent_Common_Shell_Safety.md` and `Agent_Common_Working_Record.md`) becomes generated blocks (§7b). Retired together with the old Bootstrap when the last role migrates | One owner per rule on every route |
| R5 | Common skill naming | Unprefixed. `memory` is named `agent-memory` to avoid the built-in `/memory` command. Story A1 checks all new names against each supported provider's built-in commands | Consistency; no discovery collisions |
| R6 | #303 | Separate 3-point story, merged first; its smaller fixes ride along | Live defect; establishes the pattern |
| R7 | Strict mode | One file per skill per layer; GitHub-specific steps carry an inline **Strict mode:** line, as `comment` and `po-write-story` already do | Existing template convention |

---

## 12. Non-Goals

- Migrating TL, QA, UI/UX or BA role-specific rules (they only gain pointers to common skills)
- Changing any gate, the Merge Procedure or PO acceptance (R2 aligns TL with an existing project rule)
- An orchestrator-inline mode for the Developer
- Enabling the Core route (`verified_providers`)
- Editing the frozen `.claude/agents/templates/` corpus

---

## 13. TL Review Response (PR #306, revision 2)

| Finding | Resolution |
|---|---|
| B1 Generated copies: layer differences, multi-section skills, `part_body()` heading bound, identical-text exit criterion | Two sources per layer (§3, §7a); part markers (§7a); part-to-section map (§7b); Phase 2 blocks owned by story C; exit criterion is a rule ownership map (§7c) |
| B2 `read_manifest.py` | Per-role `common` override keeping the `common` anchor; `agent-security` manifest entry and `orchestrator_instructions.md:14` amendment; `role_sources` incl. `completion`; `capability_routes` skipped for skill-based roles; `Blocked` instead of `StopIteration` (§8a) |
| B3 `read-routing.json` inventory | Full inventory incl. `source_review`, `clean_code_change`, TL/QA pre-PR routes, `trigger_document_paths`; Developer reads skills, never generated copies (§8b); TL On-Demand `:108` (§8c) |
| B4 Live Common modules | Shell Safety and Working Record modules, and the rest of the Core route, become generated blocks (§7b, R4) |
| B5 Target mapping | §9 table; `dev-verify` added; `change-metadata` and `_template` naming internal only; C re-estimated to 13 |
| N1 R1 | Adopted (R1, `retro` / `retro-contribution` split) |
| N2 R2 | Corrected: only TL changes |
| N3 `comment` already owns same-pass rule | Duplicates deleted; CI-paste note to `pr-review` (§3a) |
| N4 Pre-merge item 6 | Dropped (§6, §9) |
| N5 Missing ripple | §4 (packets, Selected Common Routing), §8c |
| N6 Working Record trigger | "Before any Working Record write" (§4) |
| N7 Story A size; read calls | A split into A1 and A2; measurement counts read calls (§2, §10) |
| **Re-review (rev 3): Approved with changes** | |
| C1 `role_sources` too narrow | List mapping, full coverage on substitution, deduplication by source (§8a) |
| C2 `test_common_capabilities.py` changes in B | Test impact stated (§7b); A1 and B exit criteria updated (§10) |

---

## Revision History

| Rev | Change |
|---|---|
| 4 | TL re-review on PR #306: **Approved with changes**; C1 (`role_sources` list mapping, coverage, deduplication) and C2 (capability test impact) folded in |
| 3 | TL review on PR #306 (Changes requested): B1–B5 and N1–N7 addressed (§13). New: two-source generator with part markers and section map, manifest `common` override and `role_sources`, full routing inventory, target mapping, `retro-contribution` and `dev-verify` skills, A split into A1/A2; 47 points |
| 2 | §10 open points resolved as R1–R7; `memory` renamed `agent-memory`; #303 added as the first story (37 points) |
| 1 | Initial draft from the user's decisions U1–U8 |
