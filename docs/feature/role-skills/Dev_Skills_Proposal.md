# Developer Skills Proposal

**Feature:** `role-skills`
**Status:** Revision 2, design points resolved (§10), ready for TL review
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
| U6 | A how-to that another role also uses becomes a common skill. Developer and the other roles' files point to it |
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

**Honest expectation.** `Developer_Rules_Bootstrap.md` v2.0 records a failed split: a full story spawn used all of §1–§6, so moving them on demand saved 3.6%. The same applies here. A full implementation story still loads most skills before it finishes, so its total read stays close to today's. The gains are:

1. **Narrow spawns** (peer review, refinement, answering a question) stop loading the implementation, pre-PR and git rules. A spawn of this kind drops from about 41 KB to about 15 KB (byte arithmetic, not a measurement).
2. **Correctness.** A rule read right before its action is applied more reliably than one read 40 KB and many tool calls earlier (#303).
3. **One owner per how-to.** Several rules exist in Developer, TL and QA copies that have already drifted (§6).

The saving is measured by byte counts per spawn type (§9). A native token comparison is out of scope; #266 can be re-scoped for it later.

---

## 3. Skill Set

Each skill is a `SKILL.md` with `name` and `description` frontmatter, under `.mt-agent-devkit/skills/<name>/`, with generated provider wrappers (PO proposal §3b). A skill names the skills it requires and never restates their rules. Size target: ≤ 4 KB per skill, ≤ 1.5 KB for `dev-core`.

### 3a. Common skills (new)

Named without a role prefix, like `agent-security` and `comment`.

| Skill | Purpose | Absorbs | Also used by |
|---|---|---|---|
| `pre-work` | Read order at fresh start and at resume, the native-reader and full-coverage gate, manifest consumption, provider bindings | Common Bootstrap §1 (without the Working Record format) | All roles (after they migrate) |
| `token-efficiency` | Tool-call conventions | Common Bootstrap §3 | All roles |
| `shell-rules` | Adapter-first shell choice, permissions, temporary body files, Shell Safety | Common Bootstrap §6, `Agent_Common_Shell_Safety.md` | All roles; the orchestrator already reads Shell Safety through `agent-security` part C |
| `working-record` | Snapshot format, retention, character cap, access control, Blockers & Watch-outs | Common Bootstrap §1 item 2, `Agent_Common_Working_Record.md`, Dev §19, the TL and QA "Reporting" bullets on the Working Record | All roles; `po-core` points to it |
| `agent-memory` | Fact format, Troubleshooting Facts, two-tier memory retrieval and writing | Common On-Demand §1 and §8, `Agent_Common_Memory.md` | All roles; `po-core` points to it |
| `troubleshooting` | Scan your own fixes first, then diagnose and record back | Common On-Demand §2, `Agent_Common_Troubleshooting.md`, TL §14, QA §13 | All roles |
| `credential-gate` | Missing secret means stop and report, never a dummy value | Common On-Demand §6, `Agent_Common_Credential_Gate.md`, the Dev §5 bullet | Every implementer and QA |
| `retro` | Trigger detection, clean/required/unknown reporting, `retro_completion.py`, writing a contribution | Common Bootstrap §7, Common On-Demand §3, `Agent_Common_Retro.md` | All roles |
| `handoff` | Runtime-state handoff before signalling completion | Common On-Demand §5, `Agent_Common_Stage_Transition.md`, TL §12, QA §12 | Implementer and reviewer roles |
| `raise-question` | Who owns a question (PO or TL), the question comment, the pre-start gate, the mid-implementation consultation report, blockers, live user instruction conflicts | Dev §2 step 2, §7, §12, §13; QA §10, §11; TL §10; the UI/UX mid-implementation rule | Every implementer |
| `project-docs` | Where documents go and how files are named (`Title_Case_With_Underscores`, the `_template` suffix) | Dev §4 (naming) and §8; TL §6; QA §5; the placement half of `po-plan-docs` | All roles; `po-plan-docs` keeps Plan Commit and requires this skill |
| `git-workflow` | Branch preflight `inspect`/`create`, branch naming, Conventional Commits, `[skip ci]` by CI path filter, PR title and body, post-QA merge sync | Dev §2 step 3, §6; TL §5 (commits); the UI/UX commit rule | Every implementer |
| `change-metadata` | `changes.json` entry and `descriptions` format, the `CHANGELOG.md` entry rule | Dev §4 (`changes.json`), Dev §5 (CHANGELOG) | Implementers write it; QA checks it (`QA_Rules_Bootstrap.md:75`) |
| `pre-pr-gate` | Local checks by change type, aggregate local-CI command, short-circuiting gates, production-build evidence, local-verify, PR check note, pre-merge checklist | Dev §5; TL On-Demand §3; QA On-Demand §1 | Every implementer |
| `pr-review` | Reviewer procedure: read the diff, CI actually ran on the current head SHA, reviewer gate, inline comments, issue notify comment, verdict through `gh pr comment` | Dev §14, §16; the shared part of TL On-Demand §5 | Dev as peer reviewer; TL keeps its approval authority rules in its own file until the TL migration |
| `clean-code` | Clean code rules, read in full for clean-code or refactor stories | `Clean_Code_Rules.md` | Dev, TL |

**Changed existing skills:**
- `comment` absorbs the "same-pass body update" rule. Today it exists in `po-comment` and in Dev On-Demand §20 (U5).
- `po-core` replaces its "PO Records" text with pointers to `working-record` and `agent-memory`, keeping only PO-specific facts (closure skips the Working Record; the orchestrator-as-PO exception).
- `po-plan-docs` requires `project-docs` and keeps only Plan Commit.

### 3b. Developer skills

| Skill | Purpose | Absorbs |
|---|---|---|
| `dev-core` | Role boundaries, status ownership, "do not tick AC", the skill load map (§4) as the single list of which skill loads when, and the always-on retro trigger watch (R1) | Dev §1, §3; `Story_Standard_Dev.md` (folded in, as `Story_Standard_PO.md` was) |
| `dev-implement` | Pre-start steps as numbered steps: read the story and touched files, raise questions and wait (requires `raise-question`), design-first rule, UI prototype reference, then start (requires `git-workflow`) | Dev §2 |
| `dev-deliver` | After the PR opens: PR-opened comment, status transitions, Deliverables links, review-to-testing handoff, fix rounds (address, push, re-run `pre-pr-gate`, re-request review) | Dev §6 (delivery transitions) |
| `dev-refine` | Sprint refinement procedure | Dev On-Demand §15 |
| `dev-hotfix` | Post-Done fix branch and cycle (requires `git-workflow`, `pre-pr-gate`) | Dev On-Demand §17 |

Peer review uses `pr-review` directly, so there is no `dev-review` skill.

---

## 4. Load Map (`developer_instructions.md`)

The instructions file keeps the role summary, record paths and Feature Context, and gains this table. `dev-core` repeats the point-of-use column so the rule is in front of the agent at every step.

| When | Skills |
|---|---|
| **At spawn, every task** | `agent-security`, `pre-work`, `token-efficiency`, `shell-rules`, `dev-core` |
| **At spawn, the task skill named in the assignment** | `dev-implement` (story), `pr-review` (peer review), `dev-refine` (refinement), `dev-hotfix` (post-Done bug) |
| Before posting any comment or editing the issue body | `comment` |
| A question or blocker comes up, or a live user instruction conflicts with the thread | `raise-question` |
| Creating or moving a document or file | `project-docs` |
| Writing code in a clean-code or refactor story | `clean-code` |
| Before creating a branch, committing or pushing | `git-workflow` |
| Before opening a PR | `change-metadata`, then `pre-pr-gate` |
| After the PR opens, and on each fix round | `dev-deliver` |
| Tooling or environment blocker | `troubleshooting` |
| Verification needs a secret you don't have | `credential-gate` |
| Retrieving or writing a memory fact | `agent-memory` |
| Before stage handoff | `retro`, then `handoff` |
| Before writing the Working Record at session end | `working-record` |

If the assignment names no task skill, the Developer reports that to the orchestrator rather than guessing, as the PO does.

---

## 5. Resumed Sessions

A fix round usually resumes the same Developer session, so the skills it already read are still in its context. The rule:

| Situation | What is loaded |
|---|---|
| Same session resumed, skills unchanged | Spawn-time skills are **not** re-read. Point-of-use skills **are** re-read right before their action (for example `pre-pr-gate` before the fix push). They are small and cached, and #303 showed that recall from earlier in the session misses checks |
| Session expired, or a fresh spawn | Full spawn set again, then point-of-use as normal |
| A skill file changed since it was read (sync or merge mid-sprint), or provenance is unknown | Re-read it. Unknown is treated as changed, matching the existing Common §1 rule |

---

## 6. Drift Found While Mapping

These are fixed by the common skills taking one owner:

- **TL pre-PR gate is weaker than the Developer's.** `Technical_Lead_Rules_Read_On_Demand.md §3` exempts "template / workflow / rules / docs only". The Developer rule (Dev §5) requires the harness validators for shared harness Markdown. `pre-pr-gate` adopts the stricter Developer rule, which changes TL-as-implementer and QA-as-implementer behavior (R2).
- **Stale citation.** `Story_Standard.md:111` cites `Developer_Rules_Read_On_Demand.md §5`; §5 is in the Bootstrap file. Repointed to `pre-pr-gate`.
- **Two document indexes.** QA §5 points to `context/Document_Index.md`; Dev, TL and PO point to `Project_Priming_Read_On_Demand.md §6`, which is a shorter list. `project-docs` points to `Document_Index.md` (R3).
- **Peer-review CI rules** live in `Technical_Lead_Rules_Read_On_Demand.md §5` and Dev §14 cites them. `pr-review` owns the shared part.

---

## 7. The Kept `Agent_Common_Bootstrap.md` (U3)

The old file stays the other roles' Common read. To stop the temporary duplicate from drifting, **its migrated sections become generated blocks** copied from the new common skills, exactly as `generate_security_blocks.py` already does for `agent-security` parts A and B. The same applies to the migrated sections of `Agent_Common_Read_On_Demand.md` and to the Phase 2 templates.

- The generator's `--check` fails CI when any copy differs from its skill.
- Other roles read the same text as before, so their behavior is unchanged.
- When the last role migrates, the old files are retired with the PO retirement mechanism, and the generator is removed.

`Agent_Common_Core.md` and its modules (`Agent_Common_Memory.md` and the rest) are only reached through `capability_routes`, which never runs (`verified_providers` is `[]`). Their content seeds the new skills, and the files themselves stay unchanged (R4).

---

## 8. Routing, Distribution and Retirement (U7, U8)

| Area | Change | Reused from PO |
|---|---|---|
| Wrappers | Skill wrappers for every new skill | `generate_wrappers.py` skill renderer, `migration-inventory.json` |
| Generated copies | Common Bootstrap and On-Demand blocks from common skills | `generate_security_blocks.py` pattern, generalised to more blocks |
| Manifests | `read_manifest.py` maps Developer to `dev-core` **and** replaces Common `Agent_Common_Bootstrap.md` with the spawn-time common skills, for the Developer only. Internal layout first, target layout in the distribution story | The per-layout role mapping (`read_manifest.py:135`) |
| `read-routing.json` | The 11 Developer entries (`peer_review` task; `story_comment`, `document_update`, `consultation`, `live_conflict`, `pre_pr`, `report_blocker`, `technical_doc_divergence`, `endpoint_change`, `behavioral_verification` triggers) point to skills | Same change as the PO citations |
| Other roles (U6) | TL, QA, UI/UX, BA and PO rule sections that duplicate a common skill become one-line pointers to it | — |
| Distribution | Skill templates, bundle entries, per-provider wrappers, slim `developer_instructions_template.md` | `build_bundle.py` skill entries |
| Retirement | `Developer_Rules_Bootstrap.md`, `Developer_Rules_Read_On_Demand.md`, `Story_Standard_Dev.md`, `Clean_Code_Rules.md`, internally and in targets | Retirement entries, receipt-based auto-resolution, the customised-file porting conflict, legacy fixture migration tests |
| Citation check | Add the four retired files to the bare-filename and `§`-citation validator | The PO validator |

---

## 9. Phasing

| Story | Scope | Estimate | Depends on | Exit criteria |
|---|---|---|---|---|
| **#303** Point-of-use loading for inline PO | The #303 proposal and its related gaps (R6) | 3 | — | Inline PO procedure loads each skill before its action; the per-action checks are numbered steps; citation and timing gaps fixed |
| **A** Common skills, internal | The 16 common skills; generated blocks in the old Common files; `comment`, `po-core`, `po-plan-docs` changes; TL/QA/UI/UX/BA pointers; the §6 drift fixes; `Document_Index.md` as the single path list (R3) | 13 | #303 | All internal gates green; generator `--check` green; other roles read identical Common text |
| **B** Developer skills, internal | The 5 Developer skills; slim `developer_instructions.md` with the load map; Developer manifest mapping and `read-routing.json` for the internal layout; delete the internal Developer rule files | 8 | A | Developer manifests resolve to skills; target-layout manifests unchanged and valid; citation validator green internally |
| **C** Distribution | Skill templates, bundle, wrappers, target-layout routing switch | 8 | B | Bundle `--check` green; targets receive the skills; target Developer manifests resolve to skills |
| **D** Retirement | Remove the four files from targets; legacy migration tests; validator over templates and bundle; CHANGELOG | 5 | C | Each legacy fixture migrates without leaving the files; a customised file raises the porting conflict |

**Total: 37 points.** Merge order #303 → A → B → C → D. A to D ship in one release, as the PO stories did; #303 may release earlier.

**Measurement (in story B):** a table of bytes read at spawn and in total, per spawn type (implementation story, fix round, peer review, refinement), before and after.

---

## 10. Resolved Design Points

Resolved before TL review (rev 2). TL review may still reopen any of them.

| ID | Point | Resolution | Basis |
|---|---|---|---|
| R1 | `retro` timing | `dev-core` carries an always-on **trigger watch**: the five trigger kinds from Common §7 in one line each, plus "when one occurs, note it in the Working Record's In Progress line". The full `retro` skill loads at handoff, where evaluation, `retro_completion.py` and the contribution happen. Detection stays during work; only the procedure moves to point of use | Common §7 requires evaluation "during work and before each stage handoff"; a missed trigger is a contract breach, so detection cannot depend on recall |
| R2 | Stricter pre-PR gate for TL and QA implementers | Adopt the Developer rule in `pre-pr-gate`. This is a **fix**, not a scope change: `Project_Priming_Bootstrap.md §8` already requires the harness validators for any `.mt-agent-devkit/**` change, whoever implements it. The TL On-Demand §3 and QA On-Demand §1 exemptions predate that rule. CHANGELOG states the behavior change | Priming §8 is the project-level authority |
| R3 | Document index owner | `context/Document_Index.md` is the single path list. It is the fuller list, it is deployed to targets (`build_bundle.py`), and it already says "update whenever a document is added, moved or removed". `Project_Priming_Read_On_Demand.md §6` becomes a one-line pointer to it, and any row only §6 has (Sprint Overviews) moves into the index | One owner; the deployed file wins |
| R4 | `Agent_Common_Core.md` and its modules | **Keep, unchanged.** They are referenced by `read-routing.json` `common_capabilities`, `generate_security_blocks.py`, `test_common_capabilities.py` and `test_internal_harness.py`, so retiring them is code and test work for a route that never runs. They are seed content for the new skills only. They retire together with the old Bootstrap when the last role migrates, or are redesigned if the Core route is enabled first (non-goal §11) | Smallest safe change |
| R5 | Common skill naming | Unprefixed, matching `comment`, `agent-security` and `read-section`. **One rename:** `memory` becomes `agent-memory`, because a bare `memory` name collides with the built-in `/memory` command in Claude Code. New names are checked against built-in commands of each supported provider during story A | Consistency; avoid discovery collisions |
| R6 | #303 | **Separate small story, merged first** (3 points). It fixes a live defect in orchestrator-as-PO runs today, and it puts the "load each skill right before its action" wording into `orchestrator_instructions.md` and the PO skills, which this proposal then mirrors for the Developer. Its smaller fixes (the `po-comment` citation of `Story_Standard.md` §12 that should be §11, the Working Record timing mismatch, the empty Stage Telemetry heading) ride along | Live defect; establishes the pattern before reuse |
| R7 | Strict mode | One skill file per skill, no mode variants. GitHub-specific steps carry an inline **Strict mode:** line, as `comment`, `po-write-story` and `po-promote-ready` already do in their Phase 2 templates. `build_bundle.py` keeps deploying skills to both modes | Existing template convention |

---

## 11. Non-Goals

- Migrating TL, QA, UI/UX or BA role-specific rules (they only gain pointers to common skills)
- Changing any gate, the Merge Procedure or PO acceptance
- An orchestrator-inline mode for the Developer
- Enabling the Core route (`verified_providers`)
- Editing the frozen `.claude/agents/templates/` corpus

---

## Revision History

| Rev | Change |
|---|---|
| 2 | §10 open points resolved as R1–R7; `memory` renamed `agent-memory`; #303 added as the first story (37 points) |
| 1 | Initial draft from the user's decisions U1–U8 |
