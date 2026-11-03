# Developer Skills — Rule Ownership Map

**Feature:** `role-skills`
**Story:** ST-000307 (A1); ST-000308 (A2) adds §7. ST-000309 (B) extends this map.
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

These skills now hold the rules. The TL, QA, UI/UX and BA files point to them since ST-000308 (§7); the Developer files keep their text until ST-000309 deletes them.

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

The 17 skills are internal only in this story. `validate_internal_harness.py` lists them in `UNDISTRIBUTED_SKILLS`, which exempts them from the Phase 2 template and bundle checks only (wrappers, frontmatter, budget and `**Requires:**` checks still apply) and fails if the bundle ships one early. ST-000310 ships every common skill except `change-metadata` (internal only, B5) and removes those names from the exemption.

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
| `po-plan-docs` | requires `project-docs`; keeps only Plan Commit. Its frontmatter `description` still names placement, because it must match the Phase 2 template until ST-000312 |
| `project-docs`, `Document_Index.md`, Priming On-Demand §6 | the index is the single path list. Its row is renamed Sprint Overviews (the §6 row it absorbs), and §6 is a pointer (R3) |

### 7c. Routing (internal layout)

| Row | Internal | Target (until ST-000312) |
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
- The internal `Clean_Code_Rules.md` file: no internal route reads it any more (the target override still does), and ST-000309 deletes it.

---

**Document Version:** 1.1 — ST-000308 (A2) adds §7, the no-duplicate-authority check
**Previous:** 1.0 — ST-000307 (A1) map
