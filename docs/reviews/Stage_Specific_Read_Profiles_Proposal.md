# Stage-Specific Read Profiles Proposal

**Status:** Proposed; no template changes have been implemented

**Scope:** Developer and Agent Common context loading in mt-agent-devkit

**Related analysis:** [Agent Harness Token Efficiency Analysis](./Agent_Harness_Token_Efficiency_Analysis.md)

**Date:** 2026-09-19

---

## 1. Purpose

Reduce fixed context by replacing broad role bootstraps with explicit
`role + stage + risk` read profiles. An agent should receive only the rules,
story state, and evidence needed for its current action while preserving safety,
verification, Technical Lead review, and QA independence.

The orchestrator should assemble an exact read manifest for each spawn or
expired-session resume. Agents should not recursively discover and load every
role rule at startup.

## 2. Design Principles

1. **Use an explicit manifest.** The orchestrator names every required file or
   bounded section for the current stage.
2. **Keep the universal core small.** Always-loaded rules cover safety,
   authority, role boundaries, bounded output, resume behavior, and completion.
3. **Load by stage and risk.** Implementation, pre-PR, fix, review, refinement,
   and hotfix work receive different profiles.
4. **Trigger capabilities when needed.** Shell safety, memory, retros,
   troubleshooting, credentials, and Working Records are conditional modules.
5. **Prefer deltas on resume.** A valid session receives only new findings,
   changed SHAs, changed requirements, and new evidence.
6. **Give each state one owner.** Requirements, workflow state, implementation
   evidence, durable memory, and interrupted-work notes must not compete.
7. **Retain independent safeguards.** Context reduction must not remove required
   tests or independent Technical Lead and QA judgment.

## 3. Proposed Developer Files

The following filenames are proposed additions or replacements; they do not yet
exist in the templates.

```text
.claude/agents/templates/
|-- instructions/
|   `-- developer_instructions_template.md
`-- rules/
    |-- Developer_Rules_Core_template.md
    |-- Developer_Profile_Implementation_Start_template.md
    |-- Developer_Profile_Pre_PR_template.md
    |-- Developer_Profile_Fix_Round_template.md
    |-- Developer_Profile_Peer_Review_template.md
    |-- Developer_Profile_Refinement_template.md
    |-- Developer_Profile_Hotfix_template.md
    `-- Developer_Rules_Scenarios_template.md
```

### `developer_instructions_template.md`

Keep only the Developer identity and boundary, profile-selection contract,
installed paths, and completion-report format. Remove broad pre-work sequences;
the orchestrator-provided manifest becomes authoritative.

### `Developer_Rules_Core_template.md`

Always load this file for Developer work. Keep it near 1,000–2,000 proxy tokens
and include:

- role authority and the prohibition on inventing product decisions;
- no self-approval or manual acceptance-criteria completion;
- the active stage profile as the authoritative procedure;
- bounded reads, bounded output, and same-session resume behavior;
- routing for blockers or missing decisions;
- required completion fields and the prohibition on merging without gates.

### `Developer_Profile_Implementation_Start_template.md`

Load for a fresh implementation stage. Include:

- canonical story body, unresolved decision threads, and latest verdict;
- design-first and clarification rules;
- clean and synchronized branch preflight;
- conditional Clean Code, Logging, and UI Prototype guidance;
- affected-caller tracing, naming checks, and implementation verification.

Do not include PR creation, merge, full review, or fix-loop procedures.

### `Developer_Profile_Pre_PR_template.md`

Load only when preparing the implementation for review. Include:

- targeted tests and aggregate local CI requirements;
- production-build triggers;
- acceptance-criteria self-check and rename/reference sweep;
- commit, push, PR, evidence, and pipeline-status requirements.

### `Developer_Profile_Fix_Round_template.md`

Load when addressing review or QA findings. The input packet should contain the
finding, affected acceptance criteria, reviewed SHA, current head SHA, and code
delta. Require targeted verification first, followed by regression proportional
to the risk. A valid existing session should receive this delta packet without
rereading its earlier context.

### `Developer_Profile_Peer_Review_template.md`

Load when the Developer acts as a peer reviewer. Move the current peer-review
and reviewer-gate rules here, including CI/head-SHA validation and the approved
SHA contract. Do not load implementation-start procedures.

### `Developer_Profile_Refinement_template.md`

Load only for Developer participation in refinement. Move the current
Developer refinement procedure here, including feasibility, dependency,
testability, and technical-risk input.

### `Developer_Profile_Hotfix_template.md`

Load only for hotfix work. Include the current hotfix procedure and the relevant
story-standard exception rules. Route to the pre-PR profile when the patch is
ready for review instead of duplicating PR instructions.

### `Developer_Rules_Scenarios_template.md`

Load a bounded section only when its trigger occurs. Candidate sections are:

- blocked work and escalation;
- specialist consultation;
- live-user worktree conflicts;
- documentation divergence and placement;
- issue/PR comment formatting;
- credential-pointer handling.

## 4. Developer Rule Migration Map

| Current content | Proposed owner |
|---|---|
| Developer Bootstrap startup sequence | Orchestrator manifest; remove recursive discovery |
| Bootstrap implementation preparation | `Developer_Profile_Implementation_Start_template.md` |
| Bootstrap implementation actions | Core or Implementation Start, according to scope |
| Bootstrap tests, build, and PR preparation | `Developer_Profile_Pre_PR_template.md` |
| Bootstrap branch preparation | Implementation Start |
| Bootstrap commit and PR rules | Pre-PR |
| Bootstrap post-QA merge flow | Orchestrator-owned shared pipeline |
| Bootstrap routing and completion | `Developer_Rules_Core_template.md` |
| Read-on-Demand blocker and consultation sections | `Developer_Rules_Scenarios_template.md` |
| Read-on-Demand peer-review sections | `Developer_Profile_Peer_Review_template.md` |
| Read-on-Demand hotfix section | `Developer_Profile_Hotfix_template.md` |
| Read-on-Demand refinement section | `Developer_Profile_Refinement_template.md` |
| Story Standard universal constraints | Core |
| Story Standard implementation guidance | Implementation Start |
| Story Standard verification and review guidance | Pre-PR or Peer Review |
| Story Standard exceptional scenarios | Scenarios |

After references have migrated and validation passes, retire:

- `Developer_Rules_Bootstrap_template.md`;
- `Developer_Rules_Read_On_Demand_template.md`;
- `Story_Standard_Dev_template.md`.

## 5. Proposed Agent Common Files

Agent Common should be split into a small universal core and triggered capability
modules.

```text
.claude/agents/templates/rules/
|-- Agent_Common_Core_template.md
|-- Agent_Common_Shell_Safety_template.md
|-- Agent_Common_Working_Record_template.md
|-- Agent_Common_Memory_template.md
|-- Agent_Common_Troubleshooting_template.md
|-- Agent_Common_Credential_Gate_template.md
|-- Agent_Common_Retro_template.md
`-- Agent_Common_Stage_Transition_template.md
```

### `Agent_Common_Core_template.md`

Always load this file. Target roughly 1,500–2,500 proxy tokens. Include secret
handling, untrusted-content boundaries, authority and role boundaries, bounded
reads and output, batching, resume semantics, verification safeguards, and the
completion contract.

### `Agent_Common_Shell_Safety_template.md`

Load before the first shell write or Git/GitHub mutation. Move the current shell,
quoting, destructive-operation, and mutation-safety rules here.

### `Agent_Common_Working_Record_template.md`

Load only for interrupted, blocked, or multi-session work, or when an explicit
status snapshot is required. Clean single-session stages should neither read nor
write a Working Record.

### `Agent_Common_Memory_template.md`

Load only after a keyword match or when a genuinely durable cross-story fact is
identified. Combine the current memory lookup and update rules. Prefer passing
matched facts in the context packet over loading the full live-memory file, and
set separate caps for the live index and archive.

### `Agent_Common_Troubleshooting_template.md`

Load after a command, tool, environment, or workflow failure—not at routine
startup.

### `Agent_Common_Credential_Gate_template.md`

Load only when a required credential or authenticated capability is absent.

### `Agent_Common_Retro_template.md`

Make retros exception-driven. Trigger on failures, blocked work, repeated fix
loops, environment issues, important ambiguity, a reusable lesson, or an
explicit sprint-retro request. A clean stage should not produce a retro.

### `Agent_Common_Stage_Transition_template.md`

Load only for a persistent handoff. Define pipeline-state updates, product
artifacts, completion evidence, and SHA ownership. Do not automatically commit
agent memory to the product branch; use gitignored or dedicated memory storage.

## 6. Agent Common Migration Map

| Current content | Proposed owner |
|---|---|
| Common Bootstrap pre-work and read sequence | Orchestrator manifest |
| Working Record rules | `Agent_Common_Working_Record_template.md` |
| Same-session resume rules | `Agent_Common_Core_template.md` |
| Secrets, authority, output discipline, completion | Core |
| Generic role/stage router | Orchestrator; remove from Common |
| Shell and mutation safety | `Agent_Common_Shell_Safety_template.md` |
| Memory lookup and update | `Agent_Common_Memory_template.md` |
| Troubleshooting | `Agent_Common_Troubleshooting_template.md` |
| Retrospective | `Agent_Common_Retro_template.md` |
| Stage transition and durable handoff | `Agent_Common_Stage_Transition_template.md` |
| Credential gate | `Agent_Common_Credential_Gate_template.md` |

After migration and validation, retire the broad Common Bootstrap and
Read-on-Demand files rather than keeping parallel copies.

## 7. Example Read Manifests

### Fresh Developer implementation

```text
Agent_Common_Core.md
developer_instructions.md
Developer_Rules_Core.md
Developer_Profile_Implementation_Start.md
bounded canonical story context
matched memory facts, if any
Agent_Common_Shell_Safety.md before the first write
```

### Same-session fix resume

Do not reread the startup files. Send only the new finding, affected acceptance
criteria, reviewed and current SHAs, relevant diff, and required verification.

### Expired-session fix round

```text
Agent_Common_Core.md
developer_instructions.md
Developer_Rules_Core.md
Developer_Profile_Fix_Round.md
bounded fix context packet
```

### Pre-PR transition

Add `Developer_Profile_Pre_PR.md` to the active session. Do not replay the
implementation-start profile unless implementation scope has materially changed.

## 8. State Ownership

| Information | Canonical owner |
|---|---|
| Requirements and product decisions | Refined story body |
| Current stage, active session, and handoff | Pipeline state |
| Implementation and verification evidence | Pull request and CI |
| Durable cross-story knowledge | Agent memory |
| Interrupted or multi-session notes | Working Record |
| Exceptional process lessons | Retrospective |

Other artifacts may link to the canonical source but should not copy its full
content.

## 9. Migration Sequence

1. Inventory every current rule and assign one canonical owner.
2. Create the proposed files by moving rules without changing behavior.
3. Make the orchestrator emit an explicit read manifest for each stage.
4. Add a bounded canonical story-context helper.
5. Update all references, generated-file mappings, and change metadata; then
   retire the old broad files.
6. Run template and generated-output validation to detect dead references and
   duplicated rules.
7. Benchmark the old and new harness on the same representative story shapes.

## 10. Validation Criteria

- No agent performs recursive startup discovery.
- Every stage has an explicit, inspectable read manifest.
- Fresh Developer fixed context initially targets roughly 3,000–5,000 proxy
  tokens; this is a hypothesis for measurement, not a hard completion budget.
- A same-session fix resume does not reload unchanged instructions or evidence.
- A non-behavioral fast path avoids the full specialized-agent bootstrap.
- Safety requirements and independent Technical Lead and QA gates remain intact.
- Validation finds no dead file references or duplicated authoritative rules.
- Before-and-after measurements use the same story shape and clearly defined
  token semantics.

## 11. Non-Goals and Open Decisions

This proposal does not remove Technical Lead or QA review, skip required checks,
set hard token limits, or implement the new files.

Before implementation, decide:

- whether profiles should be separate files or extracted sections of one file;
  separate files are recommended because manifests are easier to audit;
- how memory is persisted without contaminating product branches;
- the exact exception threshold for retrospective creation;
- whether peer review needs the complete Developer core or a smaller reviewer
  core.
