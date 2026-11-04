---
name: token-efficiency
description: Tool-call conventions for every agent - mechanical edits via shell, narrow gh queries, batched commands, named-section reads and working-copy filename resolution. Load at spawn.
---

# Token Efficiency

**Requires:** none

Canonical owner. Part `conventions` is also copied into `Agent_Common_Bootstrap.md` §3 and `Agent_Common_Core.md` §3. Section reads use the `read-section` contract (`.mt-agent-devkit/contracts/Read_Section.md`).

## Conventions

<!-- part: conventions -->
Every tool call resends the whole transcript, but prompt caching makes repeats within one session cheap — so **call count** and **needless session fragmentation** (a new agent has no cache to inherit) drive cost, not a large read's size. Defaults for all agents:

1. **Mechanical edits via shell, not Read+Edit.** AC-checkbox ticks in an issue body or placeholder replacement in a file use a `sed`-style in-place substitution — don't read the whole file into context and regenerate it.
2. **Narrow `gh` queries with `-q`/`--jq`.** Fetch only the fields you need (e.g. just comment bodies, not author/timestamp/edit-history metadata); cap to the last N comments when full history isn't required.
3. **Batch related commands.** Chain `gh`/`git` commands in one shell call when there's no dependency on intermediate output.
4. **Read the named section, not the whole file.** When a prompt or rule cites a specific section (e.g. "`Story_Standard.md` §14"), use the `read-section` skill (`.mt-agent-devkit/contracts/Read_Section.md`) to extract just that section instead of re-reading the entire file — unless your role's mandatory-read gate requires the full file. **Your Common entry file (`Agent_Common_Bootstrap.md` or `Agent_Common_Core.md`, where your route reads one) and your `*_Rules_Bootstrap.md` are always full-file reads**; the convention applies to what they route you to, never to them.

> These conventions govern *how* work is done, never *how much* verification is done — do not use them to justify thinner review or skipped checks.
<!-- /part: conventions -->
