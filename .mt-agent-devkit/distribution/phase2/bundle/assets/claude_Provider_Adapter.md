# Claude Target Harness Adapter

`CLAUDE.md` routes here after checking actual enabled capabilities. Role discovery
wrappers retain Claude frontmatter; load the canonical role body they name before
working. Shared requirements live under `.mt-agent-devkit/`.

## Lifecycle and models

Use the live runtime's verified `Agent`/`SendMessage` mappings. Record returned
`agentId` as the opaque shared `session_handle`. Reuse sessions for fix/review
feedback, respawning with the full fresh-start packet if missing or expired.
Confirm actual completion, rather than treating a delivered message as a verdict.
The worker ends its turn after a bounded final report.

Claude policy mappings: `implementation` uses opus with medium reasoning for
Developer implementation; `design-review` uses opus for TL architecture/review
and Developer peer review (medium reasoning for the Developer). `standard` uses
sonnet; `closure` uses haiku for PO closure. The Developer discovery default remains
sonnet/high, while an explicit workflow assignment takes precedence. Only choose
models the active runtime actually exposes; no paid runtime is launched by this
adapter's discovery check.

## Tools, permissions, and CI waiting

Use native `Read` directly on original paths for mandatory full-file instruction/rule reads. Read this selected adapter in full before any `Bash` command, including context loading or discovery. Shell `cat`/`sed`/Python batches and a `Read` of their persisted output do not satisfy those file-read gates. Follow up truncated `Read` responses until successful full coverage is returned. Auto permission mode does not change this read order or substitute tools; keep its configured permission checks intact.

Always use Bash for all `gh` CLI calls. Never prepend `cd /path` to a command;
use the tool's working-directory setting. Claude's configured `Bash(gh issue *)`
and `Bash(gh pr *)` allow-list is provider-specific; check active permissions.
PowerShell treats backticks as escapes and can silently corrupt Markdown, while
.NET file methods can trigger permission prompts despite shell allow-lists.
Write multiline or backtick-containing bodies to temporary files through the
file-writing tool, pass `--body-file`, and clean the file after the call.
Never assume these permissions exist in another provider. Use the active command
tool's documented session/completion support for long CI commands. Check finished,
successful CI at the current PR head; pending or failure never advances the gate.
Do not assume a background wakeup unless the active runtime documents it.

## Telemetry

For a fresh `agentId`, use the shared telemetry collector's `extract --agent-id`
with the project root. It finds the saved Claude subagent transcript without
loading raw content into the orchestrator. For every resume, follow
`Shared_Pipeline_Stages.md` → **Bounded same-session resume**: capture an explicit
start boundary immediately before the native resume, then an end boundary after
returned completion and before further reuse. Capture and extract through the
collector with `--provider claude --session-id <agentId>` and the same
`--agent-id <agentId> --project-root <project-root>` (or its validated explicit
transcript input). Pass both `--start-boundary` and `--end-boundary` at collection;
never extract the entire reused session twice. Keep the worker `agentId` separate
from native parent `session_id` checkpoint evidence. If no
supported usage exists, use `harness` and report unavailable/null fields. Runtime
state and legacy memory retention follow the shared contract.

For a fresh stage, after writing sanitized metadata, run:

```bash
python .mt-agent-devkit/scripts/telemetry.py extract --agent-id <agentId> --project-root <project-root> --metadata <stage-metadata.json> --output <RUNTIME_ROOT>/tmp/token-metrics/<run-id>.jsonl --append
```

Substitute the supplied concrete paths. `--append` retains earlier stage records;
never run fresh-session extraction again for the same resumed stage.

Both capture artifacts remain within the concrete provider-local runtime tmp
directory. Source mutations, incomplete evidence or unknown discovery use the
shared procedure's explicit unavailable fallback, never unbounded substitution.
The shared procedure owns command examples and evidence requirements; these
helpers do not certify native cumulative summaries absent their required markers.

## Provider-owned state paths

Load `.claude/harness/state-paths.json` through `provider_context.py`.
Pass its concrete `RUNTIME_ROOT`, `COMMAND_ROOT`, and `PROVIDER_ROOT` bindings
to every worker before any state read/write. Records, memory, retrospectives,
reports, temporary files and progress stay in this provider's existing paths.
Missing bindings block; never search other providers or runs for a substitute.
Run IDs identify telemetry/sessions; they do not relocate normal working state.
Disposable validation evidence may use separate provider-local run directories.

## Bounded CI and verification waits

When CI is pending in GitHub mode use `.mt-agent-devkit/contracts/Wait_Work.md`; long local checks use `.mt-agent-devkit/contracts/Local_Verify.md`. Invoke the shared wait helper with this provider and its concrete state-path bindings. Retain returned command/session identities and use only the active runtime's documented completion operations. Sequential bounded foreground waits are the fallback; unavailable command support blocks execution. Ending a worker turn is never a generic wakeup. Strict mode uses local verification and never GitHub. Revalidate exact-head evidence and approval scope after CI finishes. Mechanical installation does not certify native lifecycle behavior.

Target selection command: `python .mt-agent-devkit/scripts/provider_context.py --target . --tools <enabled-tools.json> --provider claude` (add `--capabilities <verified-runtime-manifests.json>` only for observed mappings). Target defaults use `.claude/agents`; preserve installed receipt bindings. Never use devkit `agents/working` paths for target state.
