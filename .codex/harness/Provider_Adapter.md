# Codex Internal Harness Adapter

Load only after the shared provider contract selects Codex. Root `AGENTS.md`
is the discovery entrypoint; this directory does not imply automatic discovery.

## Agent lifecycle

Use the exposed `collaboration.spawn_agent` for authorized role delegation. Pass
the shared role instruction path and complete fresh-start context explicitly.
The returned canonical task name/agent ID is the opaque `session_handle`.
`collaboration.send_message` delivers feedback but does not activate an idle
agent; `collaboration.followup_task` sends a task and activates it. Prefer that
operation for a fix/review resume. An expired/missing agent requires a new spawn
with the shared fresh-start packet. `collaboration.list_agents` checks current
liveness; `wait_agent` waits for mailbox activity, whose actual message/final
status must be inspected. A wait timeout does not mean completion. Worker final
output returns to its parent and ends its turn; do not idle after a verdict.

Keep implementer, independent reviewer, and QA distinct. These tools share the
workspace, so use the recorded worktree and separate file ownership. Existing
concurrency limits govern scheduling; do not create unsupported parallelism.

## Model and effort policy

Use inherited runtime model/effort by default. When the user authorizes explicit
selection, choose an available model appropriate to implementation/design/review
complexity and the current task requirements; do not translate Claude model names
literally. Follow the spawn
tool's fork/override restrictions; never assert an override that was rejected.

## Shell, permissions, and CI

Use `functions.exec` with exposed shell tools, observing configured sandbox and
approval review. PowerShell is valid here; Claude's Bash allow-list does not
apply. Use structured temp-file bodies for multiline GitHub content and literal
PowerShell paths for file operations. A denied shell/network command may be
retried through the supported escalation mechanism when task-authorized; never
change proxy settings or weaken the sandbox to bypass denial.

For a long command, inspect the returned exec session ID and use `write_stdin`
to poll that process. For a yielded functions cell, use `functions.wait` only
after that cell reports its ID. Neither mechanism promises a background wakeup.
Use bounded waits and report progress; pending CI cannot advance a review/merge
gate. Recheck exact-head check status; failure routes to the implementer, and
zero checks uses the shared documented exception/evidence gate.

## Telemetry and state

Bind runtime paths through the shared contract. Codex agent identities are not
Claude transcript IDs. This adapter has no verified per-stage cumulative usage
extractor: invoke the shared collector's `harness` command, with a real reported
final-context counter only when available, otherwise unavailable/null fields.
Never scrape unrelated local sessions or estimate token savings.

## Provider-owned state paths

Load `.codex/harness/state-paths.json` through `provider_context.py`.
Pass its concrete `RUNTIME_ROOT`, `COMMAND_ROOT`, and `PROVIDER_ROOT` bindings
to every worker before any state read/write. Records, memory, retrospectives,
reports, temporary files and progress stay in this provider's existing paths.
Missing bindings block; never search other providers or runs for a substitute.
Run IDs identify telemetry/sessions; they do not relocate normal working state.
Disposable validation evidence may use separate provider-local run directories.
