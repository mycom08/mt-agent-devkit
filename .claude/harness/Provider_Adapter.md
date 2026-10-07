# Claude Internal Harness Adapter

`CLAUDE.md` routes here after checking actual enabled capabilities. Role discovery
wrappers retain Claude frontmatter; load the canonical role body they name before
working. Shared requirements live under `.mt-agent-devkit/`.

## Lifecycle and models

Use the live runtime's verified `Agent`/`SendMessage` mappings. Record returned
`agentId` as the opaque shared `session_handle`. Reuse sessions for fix/review
feedback, respawning with the full fresh-start packet if missing or expired.
Confirm actual completion, rather than treating a delivered message as a verdict.
The worker ends its turn after a bounded final report.

Claude baseline model policy: Developer implementation and Developer peer review
use opus with medium reasoning; TL design/review uses opus; standard role work
uses sonnet; PO closure uses haiku. The Developer discovery default remains
sonnet/high, while an explicit workflow assignment takes precedence. Only choose
models the active runtime actually exposes; no paid runtime is launched by this
adapter's discovery check.

## Tools, permissions, and CI waiting

Use Bash for `gh` where Claude's configured Bash allow-list applies. Multiline or
backtick-containing bodies go through temporary files, cleaned after the call.
Never assume these permissions exist in another provider. Use the active command
tool's documented session/completion support for long CI commands. Check finished,
successful CI at the current PR head; pending or failure never advances the gate.
Do not assume a background wakeup unless the active runtime documents it.

## Telemetry

For a fresh `agentId`, use the shared telemetry collector's `extract --agent-id`
with the project root. It finds the saved Claude subagent transcript without
loading raw content into the orchestrator. For a resume, use a bounded stage
transcript when available; never extract the entire reused session twice. If no
supported usage exists, use `harness` and report unavailable/null fields. Runtime
state and legacy memory retention follow the shared contract.
