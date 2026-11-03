---
name: pre-work
description: Read order at fresh start and at resume - manifest consumption, adapter-first native-reader and full-coverage gate, provider bindings, then priming, Working Record, rules and memory. Load at spawn, before the first tool call.
---

# Pre-Work

**Requires:** `working-record` (record format), `token-efficiency` (section reads), `shell-rules` (before the first command)

Canonical owner of the read order. `generate_common_blocks.py` copies parts `read-order` and `resume` into `Agent_Common_Bootstrap.md` §1; edit here, then regenerate.

## Read Order

<!-- part: read-order -->
Story-execution workers consume the validated explicit manifest under `.mt-agent-devkit/contracts/Read_Manifest.md`. Follow its prerequisite order, adapter-first/native-reader/full-coverage gates and actual returned-coverage attestations. Same-session skip statements below apply only to proven unchanged reads; unknown provenance restores the complete safe path. Reduced task exceptions remain exact. Add observable triggered guidance before action; the manifest never authorizes mutations or waives independent gates.

Mandatory full-file reads use the runtime's native file-reading tool when available (Claude: `Read`), directly on the original file path. Complete successful returned coverage; follow up any truncation with that same tool. Shell `cat`/`sed`/Python batches, persisted command-output files and preloaded summaries do not satisfy this gate when a native reader exists. On-demand section extraction remains bounded per its existing contract after the adapter read gate. Without a native file reader, use the selected provider's sanctioned mechanism, never an invented tool.

Before state access, require the concrete provider bindings supplied by the
orchestrator. Missing or unresolved `{RUNTIME_ROOT}` blocks; never search another
provider or run for records.

Your instruction file lists the exact paths for your Project Priming, Working Record, Rules, and Memory. Read them in this order:

**Fresh start (newly spawned):**
1. Project Priming — the **bootstrap tier only** (`*_Priming_Bootstrap.md`): what the project *is* — overview, glossary, key directories, tech stack, architectural patterns, current state. Task-conditional priming (story workflow, template-update procedure, document paths, command surface) sits behind that file's routing table; fetch a section only when its trigger fires.
2. Your Working Record — last session's progress and impediments. Roles that own GitHub story status (Developer, TL, QA) also **sync story statuses with GitHub** here — check the current label on each in-progress story and correct the record before reporting status.
<!-- /part: read-order -->

   How to update the record (snapshot, retention, cap, format): `working-record`.

<!-- part: resume -->
3. Your Rules — read exactly the one rules file named in your instruction file's Pre-Work Checklist, and nothing else from your role's rules set. Where that file is a `*_Rules_Bootstrap.md`, it is the *whole* bootstrap-tier read: everything else is behind its own routing table, fetched only when a trigger fires. Where your role has no `_Bootstrap` file yet, the named `*_Rules.md` is still read in full.
4. Your Memory — durable conventions and decisions

**Resumed session (continuing via the selected adapter):**
1. Skip Project Priming — already in context
2. Skip your Working Record too — no other agent can write it, so a resumed agent is only re-reading its own words from earlier in the same session; nothing has changed since the last turn

> Lightweight tasks (e.g., PO story closure) override the state-read/write sequence — see your role instructions for the reduced read set. They never override the mandatory full read of your Common entry (the Common bootstrap file, or the spawn-time common skills where your role reads skills instead).
<!-- /part: resume -->
