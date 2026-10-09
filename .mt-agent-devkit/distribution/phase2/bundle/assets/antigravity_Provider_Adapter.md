# Antigravity Target Harness Adapter

Root `AGENTS.md` selects this adapter only after the active runtime's explicit
operation mapping passes the shared capability check. Runtime behavior is
must be verified in the active runtime. The default capability mapping is unset,
so workflow execution fails closed until the runtime provides verified mappings.

## Capability mapping and lifecycle

The existing Antigravity devkit skill describes `define_subagent`,
`invoke_subagent`, and `send_message` and a shared workspace option. These are
unverified candidate names. Inspect native tool schemas before mapping spawn,
resume, message, and completion; do not call candidate aliases blindly. Supply
verified mappings through `provider_context.py --capabilities <runtime-file>`
and the actual enabled tool identity list. A missing required operation blocks
before any workflow state or spawn write.

`conversationId` is the baseline native session identifier. Keep it opaque and
provider-qualified; do not turn it into a Claude `agentId`. Native resume and
completion signaling must come from the verified active API. Expired sessions
require a fresh role spawn with the shared context packet. Worker completion
ends its turn; independent reviewer/QA gates remain shared obligations.

## Models, permissions, CI and telemetry

Baseline analyst work names Gemini Pro, with high effort for TL architecture.
Verify actual model availability instead of copying Claude opus/sonnet/haiku
settings. Use native shell/permissions and supported command completion APIs;
never reuse Claude allow-lists or assume CI wakeups. Pending CI blocks advancement,
failure routes to fixes, and zero-checks requires the shared evidence decision.

No native cumulative usage extraction or wakeup behavior is verified here. Use
the shared telemetry collector's `harness` mode with only real reported counters,
otherwise unavailable/null. State bindings and legacy memory retention follow
the shared provider contract. Do not launch external runtimes to fabricate a pass.

## Provider-owned state paths

Load `.antigravity/harness/state-paths.json` through `provider_context.py`.
Pass its concrete `RUNTIME_ROOT`, `COMMAND_ROOT`, and `PROVIDER_ROOT` bindings
to every worker before any state read/write. Records, memory, retrospectives,
reports, temporary files and progress stay in this provider's existing paths.
Missing bindings block; never search other providers or runs for a substitute.
Run IDs identify telemetry/sessions; they do not relocate normal working state.
Disposable validation evidence may use separate provider-local run directories.

Target selection command: `python .mt-agent-devkit/scripts/provider_context.py --target . --tools <enabled-tools.json> --provider antigravity` (add `--capabilities <verified-runtime-manifests.json>` only for observed mappings). Target defaults use `.antigravity/agents`; preserve installed receipt bindings. Never use devkit `agents/working` paths for target state.
