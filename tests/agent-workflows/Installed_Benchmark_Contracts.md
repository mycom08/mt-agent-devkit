# Installed WF-002 benchmark contracts

The installed benchmark uses `installed_benchmark_manifest.json`. The historical local-pilot manifest and results are unchanged. The installed manifest freezes integration `7d44623` versus FIX-02 `13e1421`, Claude Code 2.1.287, Python 3.12.10, the tool set, medium effort, a $4 cap per init/start-story session, three repetitions per arm, fixture hashes, LF-normalized runner/contract/permission-handler hashes, permission policy and resolved-model expectation `claude-sonnet-5-5`.

The resolved-model expectation comes from prior diagnostics, not a new run. Every top-level session and stage record must match it. If the installed workflow selects a different subagent model, the check fails; preserve the result, review and freeze a new role-specific configuration before restarting both arms. Do not change required TL/QA models to satisfy this check. Backend revisions remain unavailable: the model ID is checked, but a backend revision is not pinned.

## Preflight

```text
python tests/agent-workflows/run_installed_wf002.py
```

This prints validated inputs without launching an agent. Fixture, source, Python, CLI, budget, repetition or ref drift fails before paid sessions. The template delta must be exactly the three FIX-02 guidance files. Any deliberate configuration change needs a reviewed manifest update and fresh runs of both arms; do not combine it with earlier captures.

The runner's explicit `--execute` option launches paid sessions. This offline work did not use it. Init and story capture stay separate. Completed captures still exit 2 and leave G2 unassessed; failed/incomplete captures exit 1.

## Quality and telemetry

The checker requires the exact pricing change, a clean tracked/untracked working tree, no remote and unchanged installed `main`. The frozen story uses one exact changelog bullet:

```text
- [ST-000211] Fix standard shipping at the 5,000-cent threshold.
```

Only blank lines, conventional release/Changes/Bug Fixes headings and that bullet may be added. Deletions, unrelated text and additional entries fail. This same fixture-specific instruction is appended to both arms.

All four telemetry records must pass the canonical schema validator and the combined duplicate check, have one run identity and `ST-000211`, the correct Developer/TL/QA/PO stage mapping, fresh completed sessions, the expected model and duration consistent with UTC timestamps within 1 ms. Valid unavailable records remain explicitly unmeasured. Measured evidence requires `raw_transcript` usage for every stage. Schema validity cannot prove real timestamp or usage provenance; independent source-transcript review remains mandatory.

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
