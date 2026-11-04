# Developer Skills — Rule Ownership Map

**Feature:** `role-skills`
**Story:** ST-000307 (A1); ST-000308 (A2) adds §7; ST-000309 (B) adds §8; ST-000310 (C) adds §9.
**Design:** `Dev_Skills_Proposal.md` §3a, §6, §7, §8b, §11 (R3, R4, R5)
**Date:** 2026-11-03

Exit criterion (design §7c): every absorbed rule is mapped to its skill part, none lost or weakened, plus `generate_common_blocks.py --check`. Byte identity with the old text is not the criterion: some rules are reworded, compacted or turned into numbered steps.

**Change column:** *verbatim* (same text) · *reworded* (same rule, new wording) · *compacted* (same rule, shorter; only rationale or examples trimmed, named below) · *step* (now a numbered step) · *route-neutral* (a file-specific pointer rewritten so one text serves every route).

---

## 1. Generated Blocks

`generate_common_blocks.py` writes each block from its skill part. Internal targets read only the internal skill. The agent-security Phase 2 rows are kept from `generate_security_blocks.py`, which this story removes.

| Target (`.mt-agent-devkit/rules/`) | Section | Blocks, in order |
|---|---|---|
| `Agent_Common_Bootstrap.md` | §1 | `pre-work` read-order, `working-record` format, `pre-work` resume |
| `Agent_Common_Bootstrap.md` | §2, §4 | `agent-security` A, B (unchanged rows) |
| `Agent_Common_Bootstrap.md` | §3 | `token-efficiency` conventions |
| `Agent_Common_Bootstrap.md` | §5 | none: the other roles' routing table stays hand-maintained |
| `Agent_Common_Bootstrap.md` | §6 | `shell-rules` rules |
| `Agent_Common_Bootstrap.md` | §7 | `retro` detection, `retro-contribution` orchestration |
| `Agent_Common_Read_On_Demand.md` | §1 | `agent-memory` facts, `troubleshooting` format |
| `Agent_Common_Read_On_Demand.md` | §2, §3, §5, §6, §8 | `troubleshooting` protocol, `retro-contribution` writing, `handoff` state, `credential-gate` gate, `agent-memory` two-tier |
| `Agent_Common_Core.md` | §2, §4 | `agent-security` A, B (unchanged rows) |
| `Agent_Common_Core.md` | §3, §7 | `token-efficiency` conventions; `retro` detection, `retro-contribution` orchestration |
| `Agent_Common_Shell_Safety.md` | §6 | `shell-rules` safety |
| `Agent_Common_Working_Record.md` | §1 | `working-record` format |
| `Agent_Common_Memory.md` | §1, §8 | `agent-memory` facts, `troubleshooting` format; `agent-memory` two-tier |
| `Agent_Common_Retro.md`, `_Troubleshooting.md`, `_Credential_Gate.md`, `_Stage_Transition.md` | §3, §2, §6, §5 | `retro-contribution` writing, `troubleshooting` protocol, `credential-gate` gate, `handoff` state |
| Phase 2 `Agent_Common_Core_template.md`, `Agent_Common_Bootstrap_template.md` | §2, §4 | `agent-security` A, B from the byte-copied Phase 2 skill template |

**Kept hand-written (not absorbed):** Core §1 (verified-route authority and entry), Bootstrap §5 routing table, each module's one-line load trigger above its heading, and the Working Record module's trigger paragraph ("Interruption, blocking, multi-session continuation ... Sync authoritative tracker status before reporting"), which is Core-route specific. Each has one owner, as before.

---

## 2. Common Bootstrap and Core

| Source rule | Owner (skill part) | Change |
|---|---|---|
| Bootstrap §1: validated manifest consumption, prerequisite order, adapter-first/native-reader/coverage gates, attestations, same-session skips, reduced task exceptions, triggered guidance, manifest never authorizes mutations | `pre-work` read-order | verbatim |
| Bootstrap §1: native reader on original path, full coverage, truncation follow-up, shell batches and summaries do not count, bounded section extraction, sanctioned mechanism without a native reader | `pre-work` read-order | verbatim |
| Bootstrap §1: concrete provider bindings before state access; missing `{RUNTIME_ROOT}` blocks; never search another provider or run | `pre-work` read-order | verbatim |
| Bootstrap §1: fresh-start order items 1–2 (priming bootstrap tier; Working Record and GitHub status sync) | `pre-work` read-order | verbatim |
| Bootstrap §1 item 2: rewrite-in-place snapshot, session start and end, own record only, orchestrator-as-PO exception | `working-record` format | verbatim |
| Bootstrap §1 item 2: 3-entry retention, ≤ 10,000 characters by `wc -c`, 60 lines non-enforced, gitignored | `working-record` format | verbatim |
| Bootstrap §1 item 2: snapshot entry format, bullets, evidence by pointer; Blockers & Watch-outs; inclusion test | `working-record` format | verbatim |
| Bootstrap §1: items 3–4 (one rules file; memory); resumed-session skips | `pre-work` resume | verbatim |
| Bootstrap §1: lightweight tasks never override "the mandatory full read of this bootstrap file" | `pre-work` resume | route-neutral: "of your Common entry (the Common bootstrap file, or the spawn-time common skills ...)" |
| Bootstrap/Core §3 items 1–5 and the closing "how, not how much" note | `token-efficiency` conventions | verbatim, except item 4 |
| §3 item 4: "This file and your `*_Rules_Bootstrap.md` are always full-file reads" | `token-efficiency` conventions | route-neutral: names `Agent_Common_Bootstrap.md` or `Agent_Common_Core.md` |
| Bootstrap §6: adapter first, permissions, completion, no foreign allow-list, temporary body files, secret rules apply in any shell | `shell-rules` rules | verbatim |
| Bootstrap/Core §7: single detection policy; evaluate during work and before handoff; independent obligations | `retro` detection | reworded |
| §7 trigger table (five events, kinds, examples) | `retro` detection | compacted: examples moved into the event column, none dropped |
| §7 non-triggers and first-fix exemption, independent exceptions, repeated rounds | `retro` detection | reworded into one list |
| §7 report `clean`/`required`/`unknown`; uncertain is unknown; sticky; late triggers | `retro` detection step 2 | step |
| §7 "Record the trigger before loading writing guidance"; `--state required --trigger <kind>` per kind | `retro` detection step 1 | step; now recorded **when detected** (R1) |
| §7 "A triggered role loads `Agent_Common_Read_On_Demand.md §3`" (Bootstrap) / "`Agent_Common_Retro.md §3`" (Core) | `retro` detection step 3 | route-neutral: "the contribution guidance its route names" |
| §7 clean role loads no writing guidance or Retro_Rules, no skeleton/section/no-op entry | `retro` detection step 3 | step |
| §7 handoff `record ... --state clean`/`unknown`; `--contribution`/`--evidence`; missing contribution blocks; evidence confinement | `retro` detection step 4 | step |
| §7 `check` before accepting completion; blocking conditions; story files prove nothing; clean-only/mixed results | `retro` detection step 5 | step |
| §7 helper never writes retros; identity fields, underscored roles; separate identities; runtime-local, uncommitted; never bypasses TL/QA or acceptance | `retro` detection (closing paragraph) | compacted: the `Product_Owner` example dropped (`Technical_Lead` kept) |
| §7 orchestrator records expected identities (≤ 128), carries them across transitions, actual actors, no unspawned QA | `retro-contribution` orchestration | moved (size budget); same text into the same §7 |
| §7 explicit sprint retro; legacy-started transition; memory pruning exception | `retro-contribution` orchestration | verbatim |

## 3. Common On-Demand and Modules

| Source rule | Owner (skill part) | Change |
|---|---|---|
| On-Demand/Memory §1 purpose (not a diary or tracker substitute) | `agent-memory` facts | compacted |
| §1 durable facts only; update over duplicate; short entries | `agent-memory` facts | compacted (three bullets into one sentence) |
| §1 inclusion test; never-record list (four items) | `agent-memory` facts | compacted, all four items kept |
| §1 rules 1–3 (rule-first ≤ ~100–120 words; correct in place; prune on write, sprint-end pruning) | `agent-memory` facts | compacted |
| §1 rule 4 point-don't-mirror, comment scope, Commenter gate | `agent-memory` facts | compacted: the "more expensive in a comment" rationale shortened to "every downstream role re-reads them" |
| §1 ≤ 40,000-character cap, 200 lines non-enforced | `agent-memory` facts | compacted: the ~7,250-token rationale dropped |
| §1 Stored Facts four-field shape (all six roles) | `agent-memory` facts | verbatim fence; field hints shortened to rule pointers |
| §1 two-tier note for Dev/QA/TL | `agent-memory` facts | reworded ("see §8" → "the two-tier variant below") |
| §1 Troubleshooting Facts five-field shape; PO/BA record Stored Facts only; scoped to Dev/TL/QA | `troubleshooting` format | moved (size budget); fence verbatim |
| On-Demand/module §2 applies-to list; steps 1–3; resume gate | `troubleshooting` protocol | verbatim, step 3 route-neutral ("the §1 format" / "`Agent_Common_Memory.md` §1 format" → "the Troubleshooting Facts shape") |
| On-Demand/Retro module §3 load condition ("when `Agent_Common_Bootstrap.md §7`" / "`Agent_Common_Core.md §7` records ...") | `retro-contribution` writing | route-neutral ("after retro detection recorded ...") |
| §3 steps 1–5 | `retro-contribution` writing | verbatim |
| On-Demand/Stage Transition §5 runtime state never committed; report after local handoff | `handoff` state | verbatim |
| On-Demand/Credential Gate §6 scope; never self-approve a skip; stop and report; wait; authorization is not PASS | `credential-gate` gate | verbatim |
| On-Demand §8 / Memory §8 live file: Standing Checks, Keyword Index, Troubleshooting Facts stays | `agent-memory` two-tier | reworded; unifies the two routes' wording ("read every spawn" / "bounded ... on fresh/expired entry") |
| §8 archive opened only on keyword match; bounded retrieval with `read-section` | `agent-memory` two-tier | compacted |
| §8 writing a fact: archive then index, both together, numbers never reused | `agent-memory` two-tier | compacted: the `Technical_Lead_Memory.md` example pointer dropped |
| §8 caps | `agent-memory` two-tier | compacted |
| Shell Safety §6 both paragraphs | `shell-rules` safety | verbatim |
| Working Record module paragraphs (same as Bootstrap §1 item 2) | `working-record` format | verbatim |

## 4. Developer, TL, QA and UI/UX Rules (no generated copy yet)

These skills now hold the rules. The TL, QA, UI/UX and BA files point to them since ST-000308 (§7); ST-000309 deleted the internal Developer files (§8).

| Source rule | Owner | Change |
|---|---|---|
| Dev §2 step 2 questions to PO/TL, do not invent, reply in thread, gate | `raise-question` §2 | step |
| Dev On-Demand §7, TL §10, QA §11, UI/UX §7 post blockers immediately, tag owner | `raise-question` §4 | merged; each role's tag targets kept |
| Dev On-Demand §12, UI/UX On-Demand §1 consultation steps 1–5, both formats, scope note | `raise-question` §3 | verbatim steps; "Flow" (UI/UX) added to the PO row |
| Dev On-Demand §13, QA On-Demand §2, UI/UX On-Demand §2 live user instruction conflicts | `raise-question` §5 | verbatim |
| Dev §19, TL §10, QA §11, UI/UX §7 short fact-based record; retention before write | `working-record` (Before Every Write) | step |
| Dev On-Demand §8, TL §6, QA §5, `po-plan-docs` placement | `project-docs` Placement | reworded: `context/Document_Index.md` is the single path list (R3); Priming On-Demand §6 is a pointer since ST-000308 |
| TL §6 context-anchoring note folders | `project-docs` Placement 3 | verbatim |
| Dev §4 Title_Case names for workflow and rules files; general naming rule; TL §6 and QA §5 document names | `project-docs` Naming | merged |
| Dev §2 step 3 inspect/create, block stops, after create record branch, status, verify | `git-workflow` §1 | step |
| Dev §6 branch name; PR title; `Closes #N`; wait for TL approval | `git-workflow` §1, §4 | verbatim |
| Dev §6, TL §5, UI/UX §6 Conventional Commits, ≤ 50 header, `Story:` footer, length is a non-blocking nit | `git-workflow` §2 | merged |
| Dev §6 `[skip ci]` by path filter, repo specifics, safe-to-skip, why, empty commit, never on code | `git-workflow` §3 | compacted, every sub-rule kept |
| UI/UX §6 "docs-only pushes skip CI" by file type | `git-workflow` §3 | superseded by the stricter path-filter rule (strengthened, not weakened) |
| Dev §6 post-QA merge sync steps 1–3 | `git-workflow` §5 | verbatim |
| Dev §4 `changes.json` `new`/`modified` format, `descriptions` rules, append-clause rule and example | `change-metadata` §2 | verbatim |
| Dev §4 `_template` suffix | `change-metadata` §3 | verbatim |
| Dev §5 CHANGELOG rule | `change-metadata` §1 | step; adds the Priming §7 facts (VERSION never hand-edited, `changes.json` scope) |
| Dev §5 local-verify; harness gates; check table; docs-only exemption | `pre-pr-gate` §1, §2 | merged with QA On-Demand §1 table |
| TL On-Demand §3 "Template / workflow / rules / docs only → Exempt" | `pre-pr-gate` §1 | replaced by the stricter rule (R2, design §6); TL On-Demand §3 points to it since ST-000308 |
| Dev §5 aggregate command, short-circuit, production build, PR note | `pre-pr-gate` §2, §3 | compacted, all five build triggers kept |
| Dev §5 credential bullet | `credential-gate` (required by `pre-pr-gate`) | pointer |
| Dev §5 pre-merge items 1–5 | `pre-pr-gate` §4 | verbatim |
| Dev §5 pre-merge item 6 (Developer sets `status:done`) | none | dropped (N4: contradicts Dev §3, PO owns Done) |
| Design §3a rename/refactor reference sweep | `pre-pr-gate` §2 step 5 | new step from the target rule set and TL review checklist |
| Dev On-Demand §14 and §16 diff, inline comments, issue notify template, `gh pr comment` verdict, reviewer gate | `pr-review` steps 2–7 | step |
| TL On-Demand §5 shared part: locate work, CI executed, head SHA, red-check diagnosis, citation accuracy, deletions via `git ls-tree`, path grep, credential evidence, "at minimum these" change requests | `pr-review` steps 1, 3–5 | step; TL keeps approval authority, design compliance and the CI/doc checklists in its own file |
| Dev On-Demand §20 `gh pr checks` paste | `pr-review` step 7 | verbatim |
| `Clean_Code_Rules.md` §1–§4, §7, §10, Applies to, Skip for | `clean-code` §1–§6 | compacted, every bullet kept; sections renumbered inside the skill |

---

## 5. R5 — Built-in Command Name Check

Checked on 2026-11-03: each new skill name against every supported provider's built-in commands and against existing skill names in this repo. **No collision.**

| Provider | Built-in commands compared |
|---|---|
| Claude Code | `add-dir`, `agents`, `bashes`, `bug`, `clear`, `compact`, `config`, `context`, `cost`, `doctor`, `exit`, `export`, `help`, `hooks`, `ide`, `init`, `install-github-app`, `login`, `logout`, `mcp`, `memory`, `model`, `output-style`, `permissions`, `plugin`, `pr-comments`, `privacy-settings`, `release-notes`, `resume`, `review`, `rewind`, `sandbox`, `security-review`, `status`, `statusline`, `terminal-setup`, `todos`, `upgrade`, `usage`, `vim`; bundled skills `code-review`, `simplify`, `loop`, `schedule`, `run`, `update-config`, `keybindings-help`, `fewer-permission-prompts`, `claude-api` |
| Codex | `approvals`, `compact`, `diff`, `exit`, `feedback`, `init`, `logout`, `mcp`, `mention`, `model`, `new`, `prompts`, `quit`, `review`, `status`, `undo` |
| Antigravity | no documented built-in slash commands beyond workspace workflows; compared against this repo's `.antigravity/skills/` (`devkit`, `read-section`) |
| This repo | `agent-security`, `comment`, the ten `po-*` skills, `read-section`, `devkit` |

| New name | Nearest built-in | Result |
|---|---|---|
| `agent-memory` | `memory` (Claude) | distinct; this is why the skill is not named `memory` (R5) |
| `pr-review` | `review` (Claude, Codex), `pr-comments`, `code-review` | distinct names |
| `pre-work`, `token-efficiency`, `shell-rules`, `working-record`, `troubleshooting`, `credential-gate`, `retro`, `retro-contribution`, `handoff`, `raise-question`, `project-docs`, `git-workflow`, `change-metadata`, `pre-pr-gate`, `clean-code` | none | distinct |

---

## 6. Distribution Status

ST-000307 kept the 17 common skills internal through the `UNDISTRIBUTED_SKILLS` exemption in `validate_internal_harness.py`. Since ST-000310 every common and Developer skill ships as a Phase 2 template, a shared canonical bundle entry and one wrapper per provider (§9); `UNDISTRIBUTED_SKILLS` holds only `change-metadata`, which is internal only (B5) and fails the check if the bundle ever ships it.

---

## 7. No-Duplicate-Authority Check (ST-000308)

Checked on 2026-11-03, internal layer only (the Phase 2 templates are ST-000312). **Result: no rule has two hand-written owners between the TL, QA, UI/UX and BA files, the PO skills and a common skill.** Developer files are out of this check: ST-000309 deletes them. The one Developer change here is the AC2 same-pass pointer, plus two citations this story would otherwise leave stale.

**Method.** (1) Every absorbed rule in §4 and design §3a was traced to the role file that held it, and that text was replaced by a pointer naming the skill. Role-only additions stay with the role. (2) The in-scope files were grepped for each skill's distinctive phrases (check tables, `Conventional Commits`, `[skip ci]`, `branch_preflight`, the consultation format, "live instruction takes precedence", retention, `Title_Case_With_Underscores`, Priming §6, same-pass and same-thread rules, `Clean_Code_Rules.md`, the CI head-SHA checks, "at minimum these", `git ls-tree`). Every remaining hit is a pointer, a role-only rule listed below, or a generated copy.

### 7a. Role files

| Role file section | Was | Now |
|---|---|---|
| TL On-Demand §1 | branch preflight, push, PR, title | pointer → `git-workflow` |
| TL On-Demand §3 | weaker check table ("Template / workflow / rules / docs only → Exempt") | pointer → `pre-pr-gate` (R2: TL as implementer now runs the harness validators) |
| TL On-Demand §5 | shared review steps (locate work, CI executed, head SHA, red-check diagnosis, citation accuracy, deleted files, old-path grep, credential evidence, change requests, notify) | pointer → `pr-review`. TL-only kept: local-verify, Reviewer Gate link, dependency pin, resume-rule completeness, design compliance, template structure, UI prototype, approval authority, CI/workflow and doc-story checklists, AC clarifications, merge gate. The `gh api .../git/trees` alternative was dropped; `git ls-tree` is kept in `pr-review` |
| TL On-Demand §5 `Clean_Code_Rules.md` bullet | rule file reference | → `clean-code` (design §8c) |
| TL Bootstrap §5 | commit format; "approve via GitHub PR review" | → `git-workflow` §2; approval via `gh pr comment` (`pr-review` step 7). This fixes a contradiction with the PR approval rule |
| TL Bootstrap §4 | `changes.json` scope, `_template` suffix | → `change-metadata`; TL design questions kept |
| TL Bootstrap §6, QA Bootstrap §5, BA instructions | placement and naming | → `project-docs` |
| TL §7, QA §6, BA §3 | same-thread reply, bare-number ban | → `comment` |
| TL §10, QA §11, UI/UX §7 | Working Record retention and style; blockers | → `working-record`, `raise-question` §4 (each role's tag targets kept) |
| TL §12/§14, QA §12/§13, UI/UX §8/§9, BA §4/§5 | handoff, troubleshooting | name `handoff` and `troubleshooting` as owners. The route keeps the generated Common copy (design §8b), so there is no second hand-written owner |
| TL §13, QA §9, QA On-Demand §1, BA On-Demand §1 | pre-PR check tables | pointer → `pre-pr-gate`. BA's own "Docs / template / workflow only → Exempt" row was the same weak gate as TL's, so BA as implementer also changes (flagged for TL review) |
| QA §10, QA On-Demand §2, UI/UX On-Demand §2 | live user instruction conflicts | → `raise-question` §5 |
| UI/UX §2 steps 2–3, UI/UX On-Demand §1 | question gate, branch and status, consultation | → `raise-question` §2/§3, `git-workflow` §1; UI/UX question examples kept |
| UI/UX §6 | branch, title, `Closes`, commits, file-type `[skip ci]` | → `git-workflow`; start command, mock-only handoff note and PR-opened comment kept |
| QA §4 `descriptions`, `_template`, scenario naming | cited `Developer_Rules_Bootstrap.md §4` | → `change-metadata` §2/§3, `project-docs` |
| QA §8 item 4 | harness gate list (missing `generate_common_blocks.py --check`) | → `pre-pr-gate` §1 table |
| `Story_Standard_TL.md §9` | review comments and the `gh pr checks` paste | → `pr-review` steps 5–7 |
| `Story_Standard.md` §4 step 2, §12 implementer gate | stale `Developer_Rules_Read_On_Demand.md §5`; "role-specific rules §5/§13" | → `pre-pr-gate` (design §6) |
| Dev On-Demand §20 same-pass bullet | restated rule | pointer → `comment` (AC2) |
| Dev On-Demand §8, §14 | Priming §6; TL §5 CI rules | → `Document_Index.md`; `pr-review` step 3 (citations that would otherwise be stale) |

### 7b. PO skills and documents

| File | Change |
|---|---|
| `po-comment`, `po-answer-questions` | same-pass rule deleted, points to `comment`; PO-only kept (body edit through `po-write-story`, ≤ 5-line decision, AC sync before `status:ready`) |
| `po-core` | PO Records point to `working-record` and `agent-memory`. Kept: PO paths, Stored Facts only, per-activity timing, the orchestrator-as-PO exception, closure skips the record |
| `po-plan-docs` | requires `project-docs`; keeps only Plan Commit. Its frontmatter `description` dropped placement in ST-000312, with the Phase 2 template (§10a) |
| `project-docs`, `Document_Index.md`, Priming On-Demand §6 | the index is the single path list. Its row is renamed Sprint Overviews (the §6 row it absorbs), and §6 is a pointer (R3) |

### 7c. Routing (internal layout)

| Row | Internal | Target until ST-000312 (§10c: now the skill) |
|---|---|---|
| `tl_implementation_1` | `git-workflow` | TL On-Demand §1 (override) |
| `tl_implementation_3`, `ba_implementation` | `pre-pr-gate` | disabled, as before |
| `qa_implementation` | `pre-pr-gate` | QA On-Demand §1 (override) |
| `qa_implementation_conflict`, `trigger_qa_conflict` | `raise-question` | QA On-Demand §2 (override) |
| `trigger_ui_consultation`, `trigger_ui_live_conflict` | `raise-question` | `UI_UX_Designer_Rules.md` §2 (existing override) |
| `trigger_tl_pre_pr` | `pre-pr-gate` | TL On-Demand §3 (override) |
| `trigger_clean_code` (TL, Dev) | `clean-code` | `Clean_Code_Rules.md` (override) |
| `trigger_document_paths` | `context/Document_Index.md` | `{priming}` (existing override) |
| new `review_procedure` (TL `review`) | `pr-review` | disabled |

`tl_implementation_1`, `qa_implementation_conflict`, `ba_implementation` and `review_procedure` are not in design §8b. Each one either reads a section that is now a pointer-only stub, or follows a pointer the section adds; without the row, the manifest would deliver the pointer but not the rule.

### 7d. Kept on purpose (not duplicates)

- Role-only procedures: the UI/UX §5 prototype gate, the QA §4 test duties (`bash -n` on the story's scripts), QA §7 post-pass commit, TL §4 design questions, the TL §2 context anchoring template.
- The CI-wait paragraph in `Story_Standard.md §12`, `Story_Standard_TL.md §12` and `pr-review` step 3 summarises `contracts/Wait_Work.md`, its owner. It is not a common-skill rule.
- Generated Common copies the other roles still read (§1–§3); `generate_common_blocks.py --check` keeps them in sync.
- The internal `Clean_Code_Rules.md` file: no internal route read it any more (the target override still does); ST-000309 deleted it.

---

## 8. Developer Files to Developer Skills (ST-000309)

The internal `Developer_Rules_Bootstrap.md`, `Developer_Rules_Read_On_Demand.md`, `Story_Standard_Dev.md` and `Clean_Code_Rules.md` are deleted. Every rule they held has one owner below; rules already absorbed by a common skill are in §4. The Phase 2 templates keep their text until ST-000310 and ST-000311.

| Source rule | Owner | Change |
|---|---|---|
| Bootstrap §1 implementation read contract (Bootstrap is the read; Story Standard Dev is not mandatory; fetch on trigger) | `developer_instructions.md` Load Map, `dev-core` load map | reworded: the load map is the read contract |
| Bootstrap §2 step 1 read story, comments, touched files; fix stale references in-story | `dev-implement` steps 1–3 | step |
| Bootstrap §2 step 2 questions and gate | `raise-question` §2, named by `dev-implement` step 4 | pointer |
| Bootstrap §2 design-first rule, "Design approved" | `dev-implement` step 5 | verbatim |
| Bootstrap §2 UI prototype reference | `dev-implement` step 6 | compacted |
| Bootstrap §2 step 3 start | `git-workflow` §1, named by `dev-implement` step 7 | pointer |
| Bootstrap §3 status flow, label moves, merge preconditions, do not tick AC, role boundaries | `dev-core` Role and Status | compacted, every rule kept |
| Bootstrap §3 pointer to `Story_Standard.md` §4 | none | dropped: a pointer only, the flow is restated in `dev-core` |
| Bootstrap §4, §5 | `change-metadata`, `project-docs`, `pre-pr-gate`, `credential-gate` (§4 of this map) | as §4 |
| Bootstrap §6 PR-opened comment, delivery transitions, fix rounds, Deliverables, review-to-testing handoff, independent QA sign-off | `dev-deliver` §1–§3 | step |
| Bootstrap §6 git rules | `git-workflow` (§4 of this map) | as §4 |
| Bootstrap §18 routing table | `developer_instructions.md` Load Map, repeated in `dev-core` | replaced (design §4) |
| Bootstrap §19 short records, retention | `working-record` (§4 of this map) | as §4 |
| On-Demand §7, §12, §13 | `raise-question` §4, §3, §5 | as §4 |
| On-Demand §8 | `project-docs` | as §4 |
| On-Demand §14, §16 review checklist, reviewer procedure, reviewer gate | `pr-review` steps 2–7 | as §4 |
| On-Demand §15 Refine Sprint steps 1–4, step-positioning check, cleared note | `dev-refine` §1–§4 | verbatim steps |
| On-Demand §17 hotfix steps 1–4 | `dev-hotfix` steps 1–4 | verbatim; adds "run `pre-pr-gate`" from the Bootstrap §5 gate |
| On-Demand §20 Dev-only comment notes | `comment` (same-pass), `pr-review` step 7 (CI paste) | pointer |
| Target On-Demand §16 doc divergence (new internally) | `dev-verify` §1 | the target rule, now internal too |
| Target On-Demand §17, §18 endpoint and sandbox verification | `dev-verify` §2 | states they do not apply internally |
| `Story_Standard_Dev.md` §1, §4, §6, §7, §9, §12 | `dev-core`, `dev-implement`, `dev-hotfix`, `comment`, `pre-pr-gate`, `pr-review` | it was a pointer index; every target above |
| `Clean_Code_Rules.md` | `clean-code` (§4 of this map) | as §4 |

**Routing:** the internal Developer route reads `pre-work`, `agent-security`, `token-efficiency`, `shell-rules` and `retro` through the registry `common` override, `dev-core` through `bootstrap`, the task skill through its task row, and the shared Common sections through `role_sources` (design §8a). Each Developer row keeps its pre-skill source under `layouts.target`.

---

## 9. Phase 2 Templates and Target Routing (ST-000310)

Every common and Developer skill except `change-metadata` has a Phase 2 template at `.mt-agent-devkit/distribution/phase2/templates/skills/<name>/SKILL_template.md`, with the internal skill's frontmatter and budget. Each layer's skill is the only owner of that layer's text (design §3).

### 9a. Phase 2 generated blocks

`generate_common_blocks.py` has a Phase 2 row for every internal row in §1 (agent-security keeps its own rows). Each Phase 2 Common rule template takes its blocks only from the Phase 2 skill templates; the internal copies never take Phase 2 text. Five layer-neutral skills are byte copies of their internal skill (`COPIES`): `agent-security`, `shell-rules`, `retro`, `retro-contribution`, `credential-gate`.

| Skill | Layer difference in the Phase 2 template |
|---|---|
| `pre-work` | Priming is the single `Project_Priming.md`; status sync names the tracker (strict mode: story files); resumed sessions use the adapter's resume operation |
| `token-efficiency` | Item 5 (devkit bare-filename resolution) dropped |
| `working-record` | Cap is the project's `**Working record cap:**` field (default 4,000) |
| `agent-memory` | Cap is the project's `**Memory file cap:**` field (default 10,000); no internal-pilot note |
| `troubleshooting` | Target applies-to list and example |
| `handoff` | Target text kept: the versioned-agent-knowledge sentence |

### 9b. Design §9 rows

| Target section (old Developer templates) | Owner (Phase 2 skill template) | Change |
|---|---|---|
| Bootstrap §1 read contract; Development Standards fallback | `dev-core` load map; `clean-code` §1 | reworded: the load map is the read contract |
| §2 steps 1–3, touched endpoints, design-first criteria, Clean Code and Logging Standard reads, UI prototype reference | `dev-implement` steps 1–9 | step |
| §2 questions and gate | `raise-question` §2 | step; non-blocking questions kept |
| §3 status flow, merge preconditions, AC ticking, role boundaries ("TL owns Testing") | `dev-core` | compacted |
| §4 Development Standard, source naming, shared-helper scope, caller trace | `clean-code` §1 | verbatim rules, compacted examples |
| §4 story files by mode | `dev-core` | compacted |
| §5 local-verify, check table, aggregate command, short-circuit, production build, test note, rename sweep, pre-merge items 1–6 | `pre-pr-gate` | target check table kept; item 7 (`status:done`) dropped (N4) |
| §5 credential bullet | `credential-gate` (required by `pre-pr-gate`) | pointer |
| §5 spec-first rule | `dev-implement` step 10 | step |
| §5 behavioral and endpoint pointers | `pre-pr-gate` §1 → `dev-verify` | pointer |
| §6 branch, PR, commits (both modes), `[skip ci]`, merge sync | `git-workflow` | `[skip ci]` by CI path filter (stricter than the old file-type rule); feature-branch targets kept |
| §6 PR-opened comment, delivery transitions | `dev-deliver` | step |
| §12 routing table | `developer_instructions_template.md` load map, repeated in `dev-core` | replaced (design §4) |
| §13 always-on | `working-record` | step |
| On-Demand §7, §10, §11 | `raise-question` §4, §3, §5 | strict-mode line added (R7) |
| On-Demand §8 | `project-docs` | the `_template` naming rule omitted (B5) |
| On-Demand §9, §12 | `pr-review` | step; `{github-org}/{repo-name}` kept |
| On-Demand §13 | `dev-hotfix` | fix branch and PR target the feature branch |
| On-Demand §14 | `dev-refine` | Product Backlog lookup and `docs/api/` check kept |
| On-Demand §15 | `comment`; CI paste in `pr-review` step 7 | pointer |
| On-Demand §16, §17, §18 | `dev-verify` §1, §2, §3 | verbatim steps |
| `Clean_Code_Rules_template.md` chapters 1–12 | `clean-code` §2–§6 | compacted to one rule line per chapter |

### 9c. Target routing

The registry gives the Developer `common`, `bootstrap` and `role_sources` overrides for `target` as well. Rows keep their old `layouts.target` sources; the target `role_sources` map each one to its shipped skill, so the old Developer templates stay in the bundle but no target Developer manifest reads them. ST-000311 retires those files and their keys. `dev_implementation` and `dev_fix` read their skill in both layouts; `pre_pr` reads `pre-pr-gate` in targets (`change-metadata` stays internal). `trigger_clean_code` is shared with TL: TL target manifests kept `Clean_Code_Rules.md` until ST-000312, which switched the row to `clean-code` in both layouts (§10c).

---

## 10. Phase 2 Pointers for the Other Roles (ST-000312)

The Phase 2 counterpart of §7. Checked on 2026-11-04 over the Phase 2 TL, QA, UI/UX and BA templates, their instruction templates, the `po-*` skill templates, the Story Standard templates and the context templates. **Result: no rule has two hand-written owners between those templates and a common skill template.** The legacy Developer templates and `Sync_Devkit_Workflow_template.md` are out of this check: ST-000311 retires or changes them, and they are the only Phase 2 templates still citing `Clean_Code_Rules.md`. Method as §7.

### 10a. Templates

| Template section | Was | Now |
|---|---|---|
| TL Bootstrap §2 | shared review steps (locate work, CI wait, executed, head SHA, red-check diagnosis, stale references, deleted files, old-path grep, credential evidence, change requests, notify) | pointer → `pr-review`. TL-only kept: local-verify, Reviewer Gate link (a test suite's non-zero count), dependency pin, resume-rule completeness, citation accuracy, Development Standards and design compliance, data isolation/error/test/migration checks, approval authority, the CI/workflow, refactor and documentation checklists, UI prototype, AC clarifications, the do-not-instruct-merge rule, the review gate |
| TL Bootstrap §2 `Clean_Code_Rules.md` bullet | rule file reference | → `clean-code` |
| TL Bootstrap §5 | commit format; approval | → `git-workflow` §2 (TL keeps the `BREAKING CHANGE:` footer); `gh pr comment` verdict through `pr-review` |
| TL Bootstrap §6–§8, §10–§12 | placement and naming; same-thread replies; Working Record and blockers; pre-PR pointer; handoff; troubleshooting | → `project-docs`, `comment`, `working-record` and `raise-question` §4, `pre-pr-gate`, `handoff`, `troubleshooting` (generated Common copy kept on the route) |
| TL On-Demand §1, §2, §3 | branch/PR steps; anchoring placement and naming; weaker check table ("Docs or config only → Exempt") | → `git-workflow` (master-PR gate kept); `project-docs`; `pre-pr-gate` (design §6: TL as implementer always runs build and unit tests) |
| QA Bootstrap §4–§6, §9–§13 | scenario and script naming; placement; same-thread replies; pre-PR and live-conflict pointers; Working Record and blockers; handoff; troubleshooting | → `project-docs`, `comment`, `pre-pr-gate`, `raise-question` §5 and §4, `working-record`, `handoff`, `troubleshooting` |
| QA On-Demand §1, §2 | check table; live-conflict rule | → `pre-pr-gate`; `raise-question` §5 |
| UI/UX §2 steps 2–3, consultation, live conflicts | question gate, branch and status, consultation format, live-conflict rule | → `raise-question` §2, §3, §5, `git-workflow` §1; UI/UX question examples and the decide-it-yourself examples kept |
| UI/UX §6–§10 | branch, title, `Closes`, commits; placement (`§Internal Documents`); Working Record and blockers; handoff; troubleshooting | → `git-workflow` (start command, handoff note, PR-opened comment kept), `project-docs`, `working-record`, `raise-question` §4, `handoff`, `troubleshooting` |
| BA §2, §3, §4, §5; BA instructions placement | check table ("Docs or config only → Exempt"); same-thread and bare-number rules; handoff; troubleshooting; placement | → `pre-pr-gate`, `comment`, `handoff`, `troubleshooting`, `project-docs` |
| `Story_Standard_TL` §9, `Story_Standard` §4, §9, §12 | review comments and the `gh pr checks` paste; pre-PR checks; Dev On-Demand §15 citation; "agent-specific rules" for spec commands | → `pr-review` steps 5–7; `pre-pr-gate`; `pr-review` (the citation ST-000311 would leave dangling) |
| `Shared_Pipeline_Stages` Stage 2 stub re-check | TL Bootstrap §2 for the CI checks | names the `pr-review` CI gate plus the TL-only checks |
| `po-core`, `po-comment`, `po-answer-questions`, `po-plan-docs` | as §7b, plus the scope-gating `Project_Priming.md §6` citation | as §7b; scope docs → `Document_Index.md`. The `po-plan-docs` frontmatter `description` drops placement in both layers |
| `Project_Priming_template` §6, `Document_Index_template` | two path lists | §6 is a pointer (R3); the index absorbs Code Review Checklist, the API spec path, Feature Docs, Test Reports and per-story scenario files, and its row is renamed Sprint Overviews |

### 10b. Kept on purpose

The Phase 2 BA and UI/UX rules stay single files (no On-Demand tier), so their pointers sit in the one file. QA §4 keeps `Agent_Common_Read_On_Demand.md §6` for a missing credential: QA's route reads the generated Common copy of `credential-gate` (design §8b).

### 10c. Target routing

The ST-000308 `layouts.target` overrides in §7c are removed, so each row reads its skill in both layouts: `tl_implementation_1`, `qa_implementation`, `qa_implementation_conflict`, `trigger_qa_conflict`, `trigger_tl_pre_pr`, `trigger_clean_code` and `review_procedure`. The older overrides on `trigger_ui_consultation`, `trigger_ui_live_conflict`, `trigger_document_paths` and `ba_implementation` go too, because the templates they read are now pointers. `tl_implementation_3` stays off in targets: TL's `pre_pr` trigger already delivers `pre-pr-gate` there. The Developer `role_sources` key for `Clean_Code_Rules.md` still serves `trigger_clean_code_change` until ST-000311.

---

## 11. Target Retirement of the Developer Files (ST-000311)

The Phase 2 templates `Developer_Rules_Bootstrap_template.md`, `Developer_Rules_Read_On_Demand_template.md`, `Story_Standard_Dev_template.md` and `Clean_Code_Rules_template.md` are deleted, with their bundle assets and their `ST-000264_Common_Ownership.json` rows. Installed copies retire through the ST-000290 mechanism: `build_bundle.py` `RETIRED_SURVIVORS` gives each file its own survivors, and the bundle lists a shared and a per-provider/mode legacy retirement entry (`required: false`) for each. `migration-inventory.json` is unchanged; its `retired` entries are the internal ones (§8).

| Retired target file | Survivors (shared bundle IDs) |
|---|---|
| `Developer_Rules_Bootstrap.md` | `dev-core`, `dev-implement`, `dev-deliver`, `raise-question`, `clean-code`, `pre-pr-gate`, `credential-gate`, `dev-verify`, `git-workflow`, `working-record`, `instructions/developer_instructions.md` |
| `Developer_Rules_Read_On_Demand.md` | `raise-question`, `project-docs`, `pr-review`, `dev-hotfix`, `dev-refine`, `comment`, `dev-verify`, `instructions/developer_instructions.md` |
| `Story_Standard_Dev.md` | `dev-core`, `dev-implement`, `dev-hotfix`, `comment`, `pre-pr-gate`, `pr-review`, `instructions/developer_instructions.md` |
| `Clean_Code_Rules.md` | `clean-code` |

The survivors are the §9b owners of each file's sections (§8 for `Story_Standard_Dev.md`). **Routing:** the registry rows lose their old Developer `layouts.target` sources and the matching target `role_sources` keys, so each row reads its skill in both layouts. `trigger_pre_pr` keeps one target alternative, `pre-pr-gate`, because `change-metadata` is internal only; the Dev-only `trigger_story_comment` row is removed, since both layouts read the `comment` skill once. **Citations:** `validate_retired_citations.py` rejects the four names in the internal corpus, the Phase 2 templates and every bundle asset (both registry layouts included); `**Version:**`/`**Previous:**` lines and the retirement ledgers are exempt. The Sync template retired-file lists drop the four names, and `Apply_Retros_Workflow.md` sends Developer lessons to the owning skill template.

---

**Document Version:** 1.5 — ST-000311 (D) adds §11, the target retirement of the Developer files
**Previous:** 1.4 — ST-000312 (A2-P2) adds §10, the Phase 2 pointers and target routing
**Previous:** 1.3 — ST-000310 (C) adds §9, Phase 2 templates and target routing
**Previous:** 1.2 — ST-000309 (B) adds §8, the Developer files
**Previous:** 1.1 — ST-000308 (A2) adds §7, the no-duplicate-authority check
**Previous:** 1.0 — ST-000307 (A1) map
