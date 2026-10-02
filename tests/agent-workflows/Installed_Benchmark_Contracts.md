# Installed WF-002 benchmark contracts

The installed benchmark uses `installed_benchmark_manifest.json`. The historical local-pilot manifest and results are unchanged. The installed manifest freezes integration `7d44623` versus FIX-02 `13e1421`, Claude Code 2.1.287, Python 3.12.10, the tool set, medium effort, a $4 cap per init/start-story session, three repetitions per arm, fixture hashes, LF-normalized runner/contract/permission-handler hashes, permission policy, top-level resolved-model expectation `claude-sonnet-5-5`, and workflow model families by stage.

The top-level Sonnet expectation comes from prior diagnostics, not a new run. Stage families follow the installed behavioral workflow: Developer/Sonnet, TL/Opus, QA/Sonnet and PO/Haiku. Each stage must report its required family; the exact observed model IDs must match the first baseline across both arms and every repetition. A mismatch stops remaining arms and invalidates comparability. Backend revisions remain unavailable; exact subagent IDs are observed at execution rather than invented offline. Required TL/QA models are unchanged.

## Preflight

```text
python tests/agent-workflows/run_installed_wf002.py
```

This prints validated inputs without launching an agent. Fixture, source, Python, CLI, budget, repetition or ref drift fails before paid sessions. The template delta must be exactly the three FIX-02 guidance files. Any deliberate configuration change needs a reviewed manifest update and fresh runs of both arms; do not combine it with earlier captures.

The runner's explicit `--execute` option launches paid sessions. This offline work did not use it. Init and story capture stay separate. Completed captures still exit 2 and leave G2 unassessed; failed/incomplete captures exit 1. Any failed init/story arm, failed local capture prerequisite or model-parity mismatch stops both loops immediately, preserving the partial summary; no later repetitions are launched.

## Installation isolation

Before story execution, the runner fingerprints `CLAUDE.md` and every initial file under `.claude`, including role instructions, adaptive context, settings, skills, rules, workflows, memory and working records. Runtime `agents/tmp/` and Python bytecode caches are excluded. Hashes normalize line endings; redirected inputs are rejected.

The three intended FIX-02 installed guidance files are checked against their exported source templates, including strict-mode assembly and framework substitutions, then canonicalized for comparison. All other file paths and hashes must match the first baseline for every subsequent arm. Missing/extra files or adaptive/context differences stop the arm before scaffold commit or paid story execution. Raw installation hashes and canonical comparison hashes are both retained. This detects input divergence; it does not independently certify that a first installation's adaptive content is correct.

## Quality and telemetry

The checker requires the exact pricing change, a clean tracked/untracked working tree, no remote and unchanged installed `main`. The frozen story uses one exact changelog bullet:

```text
- [ST-000211] Fix standard shipping at the 5,000-cent threshold.
```

Only blank lines, conventional release/Changes/Bug Fixes headings and that bullet may be added. Deletions, unrelated text and additional entries fail. This same fixture-specific instruction is appended to both arms.

All four telemetry records must pass the canonical schema validator and the combined duplicate check, have one run identity and `ST-000211`, the correct Developer/TL/QA/PO stage mapping, fresh completed sessions, the required workflow model family and duration consistent with UTC timestamps within 1 ms. Valid unavailable records remain explicitly unmeasured. Measured evidence requires `raw_transcript` usage for every stage. Schema validity cannot prove real timestamp or usage provenance; independent source-transcript review remains mandatory.

Six unit tests, unchanged checked AC and PO `done` status are necessary. They do not replace independent TL/QA judgment, permission/tool trace review or G5/G6.

## External review evidence and offline reassessment

After reviewing the preserved TL/QA transcripts and their verdicts, an independent assessor places `quality-review.json` beside each arm's `target/` and `devkit/`, outside the agent-writable target. Copy preserved reviewer transcripts to that same capture directory. Do not ask the implementation agent to manufacture this evidence.

```json
{
  "schema_version": 1,
  "implementation_sha": "<full implementation SHA reported by product_diff>",
  "developer_session_id": "<observed developer session>",
  "reviews": {
    "TL": {
      "verdict": "approved",
      "reviewed_sha": "<same full SHA>",
      "session_id": "<observed TL session>",
      "transcript": "tl-transcript.jsonl",
      "transcript_sha256": "<SHA-256 of exact preserved bytes>"
    },
    "QA": {
      "verdict": "approved",
      "reviewed_sha": "<same full SHA>",
      "session_id": "<observed QA session>",
      "transcript": "qa-transcript.jsonl",
      "transcript_sha256": "<SHA-256 of exact preserved bytes>"
    }
  }
}
```

Missing evidence, stale SHAs, non-approvals, shared sessions, shared transcript files, path escapes and mismatched hashes fail. These structural checks make reviewer claims reviewable; they do not authenticate the assessor or independently judge transcript content.

```text
python tests/agent-workflows/run_installed_wf002.py --assess-artifacts <external-capture-directory>
```

Offline reassessment launches no Claude session and preserves `summary.json`, writing a separate `assessment.json`. It validates the capture's frozen configuration, reruns local quality checks and reads external review evidence. Exit 2 still means independent G2/G6 acceptance is pending. Historical captures with another configuration cannot be reassessed as this frozen comparison.
