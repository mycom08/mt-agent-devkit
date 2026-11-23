# Developer Skills — Rule Ownership Map

**Feature:** `role-skills`
**Story:** ST-000307 (A1); ST-000308 (A2) adds §7; ST-000309 (B) adds §8; ST-000310 (C) adds §9; ST-000328 (TL, internal) adds §12; ST-000329 (TL, targets) adds §13; ST-000330 (TL, retirement) adds §14; ST-000331 (QA, internal) adds §15.
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
| TL Bootstrap §5 | commit format; approval | → `git-workflow` §2 (TL keeps the `BREAKING CHANGE:` footer: carried into `tl-implement` by ST-000330, §14b); `gh pr comment` verdict through `pr-review` |
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

## 12. Technical Lead Files to Technical Lead Skills (ST-000328)

The internal `Technical_Lead_Rules_Bootstrap.md`, `Technical_Lead_Rules_Read_On_Demand.md` and `Story_Standard_TL.md` are deleted with their wrappers (`retired` entries in `migration-inventory.json`). Six skills hold every TL-only rule: `tl-core`, `tl-design`, `tl-review`, `tl-answer`, `tl-implement`, `tl-anchor`. Rules a common skill already owns stay there (§4 and §7a). The Phase 2 templates keep their files until ST-000330; ST-000329 ships the skills to targets (§13).

### 12a. Technical Lead Rules Bootstrap

| Source rule | Owner | Change |
|---|---|---|
| §1 pre-start steps 1, 3 (priming, Working Record) | `pre-work` read order, `technical_lead_instructions.md` Pre-Work Checklist | pointer |
| §1 step 2 (read `Story_Standard_TL.md`) | `tl-core` (the standard is part of the bootstrap skill) | replaced |
| §1 step 4 (read the sprint's issues by `sprint-N`) | `tl-core` Role and Status | compacted |
| §2 numbering-gap note | none | dropped: history of the old file |
| §3 status flow, `status:review` when Dev opens a PR and tags you, `status:testing` after approval and before merge, only QA ticks AC, pointer to `Story_Standard.md` §4 | `tl-core` Role and Status | compacted, every rule kept |
| §4 evaluating approaches (compatibility, patterns, sprint scope) | `tl-design` §1 | verbatim |
| §4 recommendations (rationale, trade-offs, migration risks) | `tl-design` §2 | verbatim |
| §4 template and workflow design (purpose, completion signal, `changes.json`) | `tl-design` §3 | verbatim; `changes.json` scope stays with `change-metadata` |
| §4 key design questions | `tl-design` §4 | verbatim |
| §4 technical constraints (file names, `_template`, `VERSION` and `changes.json`) | `tl-design` §5 | verbatim |
| §5 PR approval through `gh pr comment`, inline comments | `pr-review` step 7, named by `tl-review` §2 | pointer |
| §5 commit messages | `git-workflow` §2 (§4 of this map) | pointer |
| §5 acting as implementer | `tl-implement` | step |
| §6 document placement | `project-docs`, named in the `tl-core` load map | pointer |
| §7 design decisions, impact, blockers as issue comments | `comment`, named in the `tl-core` load map | pointer |
| §10 Working Record entries (design decisions, PR links, story IDs) | `working-record`, named in the `tl-core` load map with the entry kinds | pointer |
| §10 blockers, tag BA or PO | `raise-question` §4, named in the `tl-core` load map with the tag targets | pointer |
| §11 context anchoring | `tl-anchor` | pointer |
| §12 runtime-state handoff | `handoff` (generated copy still read by other roles) | pointer |
| §13 pre-PR gate when implementing | `pre-pr-gate`, required by `tl-implement` | pointer |
| §14 troubleshooting protocol | `troubleshooting` | pointer |
| §15 on-demand routing table | `technical_lead_instructions.md` Load Map, repeated in `tl-core` | replaced |
| Version history | none | dropped: history of the old file |

### 12b. Technical Lead Rules Read On Demand and Story Standard TL

| Source rule | Owner | Change |
|---|---|---|
| On-Demand §1 branch, commits, push, PR | `tl-implement` §1 (requires `git-workflow`) | pointer |
| On-Demand §2 context-anchoring note and template | `tl-anchor` | verbatim |
| On-Demand §3 pre-PR gate; harness, template and rules changes never exempt | `tl-implement` §1 (requires `pre-pr-gate`) | verbatim |
| On-Demand §4 In Progress to Review (label swap, PR title, Deliverables link, notify comment) | `tl-implement` §2 | verbatim |
| On-Demand §4 Review to In Progress (address CR, push, re-request) | `tl-implement` §3 | verbatim |
| On-Demand §5 shared reviewer procedure | `pr-review`, required by `tl-review` | pointer |
| On-Demand §5 local-verify contract | `tl-review` §2 first bullet | verbatim |
| On-Demand §5 CI gate first step | `tl-review` §1 | merged with Story Standard TL §12 |
| On-Demand §5 dependency-pin check | `tl-review` §2 | compacted |
| On-Demand §5 resume-rule branch completeness | `tl-review` §2 | compacted, both failure cases kept |
| On-Demand §5 design compliance, template structure | `tl-review` §2 | verbatim |
| On-Demand §5 source and script changes against `clean-code` | `tl-review` §2 (requires `clean-code`) | verbatim |
| On-Demand §5 UI Prototype PRs | `tl-review` §2 | compacted: the "mirror stays in sync with the template" note dropped (it described the retired file) |
| On-Demand §5 approve by PR comment; cannot approve your own work | `tl-review` header and §2 | verbatim |
| On-Demand §5 CI/Workflow stories abbreviated checklist and skip list | `tl-review` §3 | verbatim |
| On-Demand §5 documentation and template stories | `tl-review` §4 | verbatim |
| On-Demand §5 AC clarifications; new deliverable flags PO | `tl-answer` steps 3–4 | verbatim, moved: the same rule serves the answer task |
| On-Demand §5 change requests and approval notices | `pr-review` steps 5–7, named by `tl-review` §2 | pointer |
| On-Demand §5 "you are the merge gate" | `tl-review` header | verbatim |
| On-Demand §6 reduced read set (Story Standard TL §9, Common Bootstrap in full, live memory) | `tl-answer` intro; the manifest reads spawn-time skills, `comment`, live memory | reworded |
| On-Demand §6 steps 1–4 | `tl-answer` steps 1, 2, 3, 5 | step |
| Story Standard TL §1 status table | `tl-core` Role and Status | reworded: the Testing row said "after approval and merge"; it now says before merge, as the old Bootstrap §3 and `Story_Standard.md` §4 already did |
| Story Standard TL §2 story structure | `tl-core` Role and Status | compacted |
| Story Standard TL §4 TL as implementer | `tl-implement` | pointer |
| Story Standard TL §7 role boundaries, red flags | `tl-core` Role and Status; AC-clarification distinction in `tl-answer` | compacted, every red flag kept |
| Story Standard TL §9 comment standard | `comment`; review comments to `pr-review` steps 5–7 | pointer |
| Story Standard TL §12 pending CI, strict mode | `pr-review` step 3 (word-for-word the same rule) | merged |
| Story Standard TL §12 checklist, zero checks not passing evidence | `tl-review` §1 | verbatim |
| `technical_lead_instructions.md` Selected Common Routing, Story Implementer, Context Anchoring, Answer-a-Question pointers | Load Map | replaced |
| `technical_lead_instructions.md` Project Memory paragraph | Pre-Work Checklist memory row, `agent-memory` | pointer |

### 12c. Routing (internal layout)

The internal Technical Lead route reads `pre-work`, `agent-security`, `token-efficiency`, `shell-rules` and `retro` through the registry `common` override, `tl-core` through `bootstrap` (the `standard` row is disabled internally), the task skill through its task row, `tl-design` through the new `design_standards` trigger, and the shared Common sections through `role_sources`, as for the Developer. ST-000329 removed the `layouts.target` overrides and routes targets the same way (§13). `validate_retired_citations.py` rejects citations of the three files in the internal corpus and in the registry outside `layouts.target`.

## 13. Technical Lead Skills in Targets (ST-000329)

Each `tl-*` skill has a Phase 2 template at `.mt-agent-devkit/distribution/phase2/templates/skills/<name>/SKILL_template.md`, with the internal skill's frontmatter and budget, shipped as a shared managed canonical skill plus one wrapper per provider (`TL_SKILLS` in `build_bundle.py`). The legacy TL templates (`Technical_Lead_Rules_Bootstrap_template.md`, `Technical_Lead_Rules_Read_On_Demand_template.md`, `Story_Standard_TL_template.md`) shipped, unread, until ST-000330 retired them behind these survivors (§14).

### 13a. Target layer differences

The target text keeps the old target rules, so it differs from the internal skills where the target file differed from the internal one (design §3: each layer's skill is the only owner of that layer's text).

| Skill | Layer difference in the Phase 2 template |
|---|---|
| `tl-core` | AC is ticked by the PO at closure, not QA; story discussion in strict mode names the story file's `**Status:**` and `## Comments`; the load map drops `change-metadata` (internal only) |
| `tl-design` | The project design standards (approach evaluation with performance, security and team capability, API design, deliverables per design task) replace the devkit template and `changes.json` rules; no `change-metadata` requirement; language and database versions come from `Project_Priming.md` instead of `{language-version}` placeholders |
| `tl-review` | "Review gate, not the merge gate": the approval moves the story to QA testing and never instructs a merge; adds citation accuracy, the data isolation, error format, test coverage and migration checks against `docs/wiki/Development_Standards.md`, and the refactor story checklist; strict mode posts the verdict as a story comment entry |
| `tl-answer` | Adds the technical doc divergence table (Story Standard TL §8) and the strict-mode comment note |
| `tl-implement` | The feature branch is the merge target (no PR to master); PR title `[ST-XXXXXX][FEATURE]`; strict-mode note |
| `tl-anchor` | Adds the file-name and 50-line rules |

### 13b. Target rows to skills

| Old target text | Owner | Change |
|---|---|---|
| Story Standard TL §1, §2, §7; Bootstrap §3 | `tl-core` | compacted, every rule kept |
| Bootstrap §4 | `tl-design` §1-§6 | verbatim, placeholders replaced by `Project_Priming.md` |
| Bootstrap §2 (checklists, AC clarifications, change requests); Story Standard TL §12 | `tl-review` §1-§5; `tl-answer` steps 3-4; `pr-review` steps 5-7 | as §12b, plus the target-only checks above |
| Story Standard TL §8 | `tl-answer` | moved |
| On-Demand §1, §3, §4 | `tl-implement` | step |
| On-Demand §2 | `tl-anchor` | verbatim |
| On-Demand §6 | `tl-answer` | reworded, as §12b |
| Story Standard TL §9, Bootstrap §5-§8, §10-§12 | `comment`, `git-workflow`, `project-docs`, `working-record`, `raise-question`, `pre-pr-gate`, `handoff`, `troubleshooting` | pointer, named by the `tl-core` load map |
| Bootstrap §13, `technical_lead_instructions_template.md` routing | Load Map in the instructions template, repeated in `tl-core` | replaced |

### 13c. Target routing

The registry gives the Technical Lead `bootstrap`, `common` and `role_sources` entries for `target` equal to the internal ones, and every `layouts.target` override that named a TL rules file is removed, so each row reads its skill in both layouts: `tl_implementation_4`, `review`, `question_rules`, the question `comment` row and `trigger_anchoring`. The `standard` row stays disabled in both layouts, so `Story_Standard_TL_template.md` is no longer read. `design_standards` is no longer internal only. `tl_implementation_3` stays off in targets: the `pre_pr` trigger already delivers `pre-pr-gate`. `validate_retired_citations.py` rejects the three TL names in every registry layout; the shipped templates and bundle assets were exempt until ST-000330 (§14). The `Story_Standard_template.md` Testing note and the `pr-review` template point to the TL skills.

## 14. Target Retirement of the Technical Lead Files (ST-000330)

The Phase 2 templates `Technical_Lead_Rules_Bootstrap_template.md`, `Technical_Lead_Rules_Read_On_Demand_template.md` and `Story_Standard_TL_template.md` are deleted, with their bundle assets. `ST-000264_Common_Ownership.json` has no TL rows, and `migration-inventory.json` is unchanged (its `retired` entries are the internal ST-000328 ones). Installed copies retire through the ST-000290 mechanism: `build_bundle.py` `RETIRED_SURVIVORS` gives each file its own survivors, and the bundle lists a shared and a per-provider/mode legacy retirement entry (`required: false`) for each.

### 14a. Retired target file to survivors (shared bundle IDs)

| Retired target file | Survivors |
|---|---|
| `Technical_Lead_Rules_Bootstrap.md` | `tl-core`, `tl-design`, `tl-review`, `tl-implement`, `tl-anchor`, `pr-review`, `git-workflow`, `pre-pr-gate`, `raise-question`, `working-record`, `project-docs`, `comment`, `handoff`, `troubleshooting`, `instructions/technical_lead_instructions.md` |
| `Technical_Lead_Rules_Read_On_Demand.md` | `tl-implement`, `tl-anchor`, `tl-review`, `tl-answer`, `pr-review`, `git-workflow`, `pre-pr-gate`, `instructions/technical_lead_instructions.md` |
| `Story_Standard_TL.md` | `tl-core`, `tl-implement`, `tl-review`, `tl-answer`, `comment`, `pr-review`, `instructions/technical_lead_instructions.md` |

The survivors are the §13b owners of each file's sections. `validate_retired_citations.py` now rejects the three names (and `TL Bootstrap`/`TL On-Demand` section citations) in the internal corpus, the Phase 2 templates and every bundle asset, both registry layouts included; the retirement ledgers and `**Version:**`/`**Previous:**` lines are exempt. The Sync template retired-file lists drop the three names, its porting step names the `tl-*` skills, and the Shared Pipeline Stages stub re-check and the Story Standard section 9 point to `tl-review` and `pr-review`.

### 14b. Rules the ST-000329 review found missing from the target skills

Each was in a legacy target TL file and in no `tl-*` skill. Each was resolved before the files were deleted; none was dropped silently.

| Legacy rule | Decision | Owner |
|---|---|---|
| "Actually executed" for a test suite means a non-zero test count (`Technical_Lead_Rules_Bootstrap` CI gate) | Carried, target only | Target `tl-review` Reviewer Gate: "No CI check is **failed**, and a test suite ran a non-zero test count." The template was at 3962 of 4000 bytes, so the limit is **not raised**: the cost was paid by trimming three phrases (the "(local-verify)" label, "companion" in the UI Prototype line, "plain-language explanation sits" to "plain language beside") with no rule weakened. It ends at 3999 bytes. Internal: retired on purpose, since the devkit has no test-suite CI gate that reports a test count |
| TL-only `BREAKING CHANGE:` commit footer (`Technical_Lead_Rules_Bootstrap` section 5; §10a said it was kept) | Carried, target only | Target `tl-implement` section 1, as the TL-only addition to `git-workflow`. Internal: retired on purpose; the devkit commits `[ST-NNNNNN][DEVKIT]:` messages and its release notes come from `CHANGELOG.md`, so no tool reads the footer |
| "Domain-specific NFR design questions" in the CI/workflow skip list (`Technical_Lead_Rules_Bootstrap`) | Carried, target only | Target `tl-review` section 3 skip list. Internal: retired on purpose; the devkit is Markdown-only and has no domain NFR design questions to skip |

The internal skills stay free of the three rules; `TlSkillsTests` pins both sides.

## 15. QA Files to QA Skills (ST-000331)

The internal `QA_Rules_Bootstrap.md`, `QA_Rules_Read_On_Demand.md` and `Story_Standard_QA.md` are deleted with their wrappers (`retired` entries in `migration-inventory.json`). Five skills hold every QA-only rule: `qa-core`, `qa-validate`, `qa-testing`, `qa-regression`, `qa-hotfix`. Rules a common skill already owns stay there (§4 and §7a). The Phase 2 QA templates keep their files until ST-000332, which ships the skills to targets; the QA skills are `UNDISTRIBUTED_SKILLS` until then. Rows marked **dropped** are the three drops TL confirmed on PR 342.

### 15a. QA Rules Bootstrap

| Source rule | Owner | Change |
|---|---|---|
| §1 steps 1, 3, 4 (priming, Working Record, memory) | `pre-work` read order, `qa_instructions.md` Pre-Work Checklist | pointer |
| §1 step 2 (read `Story_Standard_QA.md`) | `qa-core` (the standard is part of the bootstrap skill) | replaced |
| §1 step 5 (read the issues filtered by `status:testing`) | `qa-validate` step 1 | step |
| §2 locating work 1–4 (open the issue, find the linked PR, test on the dev branch before merge, comment for Dev when no PR is linked or the story is not in `status:testing`) | `qa-validate` steps 1–4 | step |
| §3 acceptance contract (`Story_Standard.md §14`, verdicts, NOT VERIFIED, no pass while any AC is FAIL or NOT VERIFIED, authorized skips do not certify) | `qa-validate` step 5 | compacted, every clause kept |
| §3 status flow; QA sign-off is the merge gate; verify AC on the dev branch | `qa-core` Role and Status | compacted |
| §3 sign-off by comment (or story MD in strict mode) before merge; AC ticked by PO | `qa-validate` steps 7 and 9 | step |
| §3 notify Dev to merge; closure at PO Stage 4; pointers to `Story_Standard.md §4` and Stage 3/4 | `qa-validate` step 11 | compacted |
| §3 AC cannot be validated: blocker comment, stay in `status:testing` | `qa-validate` step 8 | step |
| §4 scenario document first; location; happy path, error and edge cases | `qa-testing` Before Testing | verbatim |
| §4 exceptions (CI/workflow-only run URL; verification-only) | `qa-testing` Before Testing | verbatim |
| §4 template and workflow validation (placeholders, `_template` suffix, paths, GitHub and strict mode) | `qa-testing` Checks | compacted |
| §4 shell script validation (`bash -n`, PowerShell, logic review) | `qa-testing` Checks | verbatim |
| §4 `changes.json` validation (entry, format, `descriptions` clause list) | `qa-testing` Checks | compacted; the `change-metadata` section 2 pointer kept |
| §4 UI prototype validation | `qa-testing` Checks | compacted |
| §4 UI prototype note "this mirror stays in sync with the template per `Project_Priming_Read_On_Demand.md §15`" | none | **dropped**: it described the retired file |
| §4 test failure policy (blocker comment tagging Dev, stay in testing, no sign-off) | `qa-testing` Failure Policy; `qa-validate` step 8 | verbatim |
| §5 document placement | `project-docs`, required by `qa-testing` | pointer |
| §6 findings and sign-off as issue comments | `comment`, named in the `qa-core` load map | pointer |
| §7 post-pass commit (scenario document, message format, push, gate) | `qa-validate` step 10 | step |
| §8 local-verify; regression steps 1–5; gate | `qa-regression` | verbatim; item 4 names the `pre-pr-gate` section 1 table |
| §8 CI-equivalent exception | `qa-regression` | verbatim |
| §9 pre-PR gate when QA implements | `pre-pr-gate`, named in the `qa-core` load map | pointer |
| §10 live user instruction conflicts | `raise-question` §5, named in the `qa-core` load map | pointer |
| §11 Working Record and blockers (tag Dev or TL) | `working-record`, `raise-question` §4, named in the `qa-core` load map | pointer |
| §12 runtime-state handoff | `handoff`, named in the `qa-core` load map | pointer |
| §13 troubleshooting protocol | `troubleshooting`, named in the `qa-core` load map | pointer |
| §14 on-demand routing table | `qa_instructions.md` Load Map, repeated in `qa-core` | replaced |
| Version history | none | **dropped**: history of the old file |

### 15b. QA Rules Read On Demand and Story Standard QA

| Source rule | Owner | Change |
|---|---|---|
| On-Demand §1 pre-PR gate when QA implements | `pre-pr-gate`, named in the `qa-core` load map | pointer |
| On-Demand §2 live user instruction conflicts | `raise-question` §5, named in the `qa-core` load map | pointer |
| On-Demand §3 hotfix steps 1–3 (report and tag Dev and TL; re-validate every affected AC after the fix PR; report and notify PO) | `qa-hotfix` | verbatim; adds the `dev-hotfix` note |
| Story Standard QA §1 status table (Testing is QA's; Done is PO's) | `qa-core` Role and Status | compacted |
| Story Standard QA §1 "QA moves story to `status:done` after merge is confirmed" | none | **dropped** (QA setting `status:done`): contradicts the same table's Done row, `Story_Standard.md §4` and Bootstrap §3 |
| Story Standard QA §5 Testing steps 1–4 (read AC, validate each, per-AC comment without ticking, failed AC comment and Dev fix) | `qa-validate` steps 1, 5, 6, 8 | step |
| Story Standard QA §5 acceptance prerequisite (`Story_Standard.md §14`, any FAIL or NOT VERIFIED keeps the story unresolved) | `qa-validate` steps 5 and 9 | compacted |
| Story Standard QA §5 Testing to Done step 1 "confirm the dev branch is merged to main; if not, wait" | none | **dropped** (confirm dev branch merged before testing): contradicts testing on the dev branch before merge (Bootstrap §2) and the Stage 3 merge gate |
| Story Standard QA §5 Testing to Done steps 2–3 (results in a comment; notify PO that all AC passed) | `qa-validate` steps 6 and 11 | step |
| Story Standard QA §5 Testing to Done step 4 "remove `status:testing`, add `status:done`" | none | **dropped** (QA setting `status:done`): PO owns Done |
| Story Standard QA §6 hotfix pointer; `qa_instructions.md` Post-Done Bug section | `qa-hotfix`, Load Map | pointer |
| Story Standard QA §7 role boundaries and red flags | `qa-core` Role and Status | compacted, both red flags kept |
| Story Standard QA §9 comment standard | `comment`; QA additions (one comment per story, one line per AC, cap exemption) in `qa-validate` step 6 | pointer; verbatim additions |
| Story Standard QA §14 AC checkbox rules | `qa-validate` steps 5, 7, 11 | compacted |
| `qa_instructions.md` Selected Common Routing | Load Map | replaced |
| `qa_instructions.md` Project Memory paragraph | Pre-Work Checklist memory row, `agent-memory` | pointer |

### 15c. Routing (internal layout)

The internal QA route reads `pre-work`, `agent-security`, `token-efficiency`, `shell-rules` and `retro` through the registry `common` override, `qa-core` through `bootstrap` (the `standard` row is disabled internally), `qa-validate` and `qa-testing` through the `qa` task, and the shared Common sections through `role_sources`, as for the Technical Lead. Two internal-only triggers deliver point-of-use skills: `regression_check` reads `qa-regression`, `post_done_bug` reads `qa-hotfix`. The registry keeps `layouts.target` alternatives (the `standard` row reads `Story_Standard_QA.md`, the two task rows are disabled) and has no `bootstrap`, `common` or `role_sources` entry for `target`, so installed targets read their QA files until ST-000332. `validate_retired_citations.py` rejects citations of the three files in the internal corpus and in the registry outside `layouts.target`; the Phase 2 templates and bundle assets stay exempt until then. `test_common_capabilities.py` keeps its Core-route contracts on a fixture registry without QA's overrides, plus a test that the real QA route skips it.

---

**Document Version:** 1.9 — ST-000331 (QA, internal) adds §15, the QA files
**Previous:** 1.8 — ST-000330 (TL retirement) adds §14, the target retirement of the Technical Lead files
**Previous:** 1.7 — ST-000329 (TL targets) adds §13, the Technical Lead skills in targets
**Previous:** 1.6 — ST-000328 (TL) adds §12, the Technical Lead files
**Previous:** 1.5 — ST-000311 (D) adds §11, the target retirement of the Developer files
**Previous:** 1.4 — ST-000312 (A2-P2) adds §10, the Phase 2 pointers and target routing
**Previous:** 1.3 — ST-000310 (C) adds §9, Phase 2 templates and target routing
**Previous:** 1.2 — ST-000309 (B) adds §8, the Developer files
**Previous:** 1.1 — ST-000308 (A2) adds §7, the no-duplicate-authority check
**Previous:** 1.0 — ST-000307 (A1) map
