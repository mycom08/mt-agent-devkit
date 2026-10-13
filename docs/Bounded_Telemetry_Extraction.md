# Bounded Telemetry Extraction

ST-000252 extends the active schema 1 collector without changing metric meanings.
The canonical implementation is
`.mt-agent-devkit/distribution/phase2/templates/scripts/telemetry.py`; the internal
`.mt-agent-devkit/scripts/telemetry.py` delegates to it. Frozen legacy templates
remain unchanged. The generated bundle installs the active implementation in
each supported layout.

The authoritative capture/resume/complete procedure and command examples live
in [Shared Pipeline Stages](../.mt-agent-devkit/workflows/Shared_Pipeline_Stages.md#bounded-same-session-resume).
It covers both explicit transcript paths and Claude agent-ID discovery. Provider
adapters refer to that procedure. A future read manifest carries its stage
handoff fields without duplicating the extraction policy.

## Boundary representation

A runtime-local boundary JSON object contains exactly these fields:

| Field | Meaning |
|---|---|
| `boundary_version` | Boundary format version 1; independent of telemetry schema 1 |
| `provider` | Supported transcript provider, currently Claude |
| `session` | SHA-256 of the explicitly supplied worker handle or native session identity |
| `source` | SHA-256 of the resolved selected transcript path |
| `device`, `inode` | Stable regular-file identity; unavailable identity rejects capture |
| `offset` | Byte length at a complete JSONL line endpoint |
| `sha256` | Digest of every byte up to that endpoint |

Boundary capture reads only the selected file and publishes its artifact
atomically. Raw paths, prompts, tool input and session identifiers are excluded
from boundary output and sanitized telemetry. Digests are integrity evidence,
not encryption; keep all snapshots runtime-local and uncommitted.

Extraction verifies both artifacts against the current file before decoding the
interval. Appended later-stage bytes are excluded. A same-size edit, replacement,
truncation, invalid offset, changed prefix, conflicting owner, malformed record
or interrupted read fails without a telemetry row or whole-session retry.

## Attributable usage

The collector deduplicates assistant request IDs and request-scoped tool IDs
inside the interval. Reusing a tool ID in another request still counts another
invocation. A repeated pre-boundary request fails; the collector never assigns a
late streamed event from that request to the new stage.

Complete request evidence requires a supported terminal `stop_reason` and all
four token metrics. Streamed input/cache values must agree, terminal output must
agree across duplicates and equal the maximum stream count, and duplicate tool
records must agree. Generic session totals do not replace request output.

The conservative cumulative alternative requires the source's existing
`usage_scope: session` and `usage_definition: claude-token-usage-v1` result
markers. Both endpoints must align with comparable result checkpoints in the
same native session. Every intervening checkpoint must use that definition and
monotonic counters. Input/cache deltas must equal attributable request totals;
the output delta must cover their streamed output. Request/tool counts always
come from actual bounded events. These explicit synthetic fixture markers prove
helper behavior; they make no claim that every native Claude transcript emits
such checkpoints. Do not annotate a native source to manufacture support.

An unchanged validated interval with established owner/session evidence proves
zero requests and tools. Missing discovery, an empty file, partial requests,
incomplete checkpoints and interrupted stages remain unknown. CLI errors are
actionable and leave usage unreported; the orchestrator records a factual reason
through the schema's existing wholly unavailable/null fallback. A separately
reported final-context counter retains its existing harness semantics.

## Deterministic evidence

`scripts/test/fixtures/telemetry/bounded_session.jsonl` and
`bounded_expected.json` define one fresh stage and two resumes:

| Stage | Requests | Tools | Input | Cache creation | Cache read | Output |
|---|---:|---:|---:|---:|---:|---:|
| Fresh | 1 | 1 | 10 | 100 | 1,000 | 40 |
| Resume 1 | 1 | 2 | 20 | 200 | 2,000 | 60 |
| Resume 2 | 1 | 1 | 5 | 50 | 500 | 10 |
| Complete fixture session | 3 | 4 | 35 | 350 | 3,500 | 110 |

The regression suite asserts exact per-stage metrics and additive reconciliation
against the independently declared whole-session fixture totals. It also covers
request-only evidence, zero versus unknown, streamed duplicates, crossing
requests, invalid boundaries, changed files, ownership, nonmonotonic summaries,
missing metrics, atomic capture, read interruption, both CLI input forms and
privacy. Run `python -m unittest scripts.test.test_telemetry`; the repository's
aggregate local fixture runner includes this module and the deployment matrix.

Providers without verified extraction continue to use unavailable telemetry.
Mechanical deployment tests do not certify native provider execution or costs.
