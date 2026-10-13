# ST-000252 Bounded Telemetry Extraction Scenarios

Oracle: current story 252 acceptance criteria and approved bounded cumulative
semantics. Use frozen `scripts/test/fixtures/telemetry/bounded_session.jsonl`
and `bounded_expected.json`; never modify a native transcript to add support.

| Case | AC | Exercise and expected result |
|---|---|---|
| TC01 | 1, 5 | Extract fresh stage, capture before each of two resumes, capture after completion, then extract only each interval. Explicit paths and owned agent-ID discovery both work. Fresh metrics remain compatible; additive fixture totals are 3 requests, 4 tools, 35 input, 350 cache creation, 3500 cache read, 110 output. |
| TC02 | 2, 7 | Walk the shared orchestrator procedure through start capture, supported resume, returned completion, end capture and bounded collection. Both examples carry the same provider/session/source; snapshots stay local; only successful bounded evidence produces raw_transcript and same_session_resume. |
| TC03 | 3 | Duplicate streamed requests/tools count once. Complete finalized requests or comparable endpoint checkpoints produce complete schema 1 metrics. Conflicting streams, nonmonotonic/mismatched summaries, missing metrics and crossing requests reject the entire result. |
| TC04 | 3, 4 | Equal validated bounds with owner evidence prove zero. Empty source/discovery and unknown nonempty stages remain unknown. Missing start/end or interrupted completion never falls back to whole-session totals. |
| TC05 | 4, 6 | Reject invalid types/digests/offsets, foreign provider/session/source, malformed/partial records, changed prefixes, replacement/truncation and interrupted reads/publication. Preserve previous atomic boundary output and selected transcript bytes. |
| TC06 | 6 | Run telemetry regressions including sanitized boundary/result checks. Raw prompt/secret/session identity and absolute local paths are absent; unavailable metrics remain null. |
| TC07 | 7 | Inspect active shared guidance, Claude adapter, internal delegate, generated assets, changelog and manifest; verify Codex/Antigravity unavailable fallback and frozen legacy compatibility. Exercise all provider/mode/profile deployment layouts and regression gates. |

Required automation: telemetry and internal unittest modules, internal/template
validators, wrapper check, Phase 2 bundle/deployment checks, and canonical
PowerShell aggregate runner including validator fixtures. Results belong in
provider-local QA evidence and the issue's per-AC report, with exact tested SHA.

This deterministic fixture and guidance validation does not certify native
Claude execution, native cumulative checkpoint availability, unrelated provider
support, token savings, or model costs.
