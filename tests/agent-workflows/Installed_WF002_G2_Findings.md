# WF-002 installed G2 attempt — 2026-09-29

## G5 disposition for subsequent benchmark work

On 2026-09-30 the user directed the team to continue independent benchmark
work with FIX-02's G5 failure documented for later resolution. GitHub issue
#214 tracks that gap. P01/P02 still ran independent operations sequentially;
PR #209 remains draft. Any G2/G6 measurements taken before #214 is resolved
are diagnostic and cannot establish that FIX-02's parallel behavior passed or
that the optimization is release-ready.

One fresh baseline/candidate pair used `run_installed_wf002.py`, Claude Code
2.1.284, resolved model `claude-sonnet-5-5`, medium effort, and a $2 cap per CLI
session. The source refs were `a30460a87c6d439b1193c45b77cc638a8f237fdb`
and `e2e700aa2e1014011c07c789458d13501a92f661`. No repository remote
was configured. Raw evidence remains outside Git in the temporary directory
reported by the run; this report contains no raw transcript.

| Arm | Init cost | Start-story cost | Outcome |
|---|---:|---:|---|
| Baseline | $0.8343464 | $0.1449756 | Both stages stopped |
| Candidate | $0.6800668 | $0.1469384 | Both stages stopped |

Both init sessions returned CLI exit 0 with a result event, but their final
messages said the installation was incomplete. Claude's file tool refused
writes under `.claude/agents/`; copied adaptive files retained placeholders.
Both start-story sessions returned CLI exit 0 yet stopped at Stage 0 because
the injected story lacked `**Assigned:**`. The active branch remained `main`.
No product change, targeted verification, TL review, QA verdict, or PO closure
occurred. **G2 failed; G6 was not assessed.** These costs are failed-run costs,
not baseline or candidate efficiency measurements.

The frozen manifest names Claude Code 2.1.280 and `claude-sonnet-5`; this run
used 2.1.284 and `claude-sonnet-5-5`. The manifest lists `Read,PowerShell,Edit,Write`,
while this installed runner also exposes `Glob,Grep,Bash,Agent`. Update the
manifest or pin and re-run the original configuration before treating future
runs as comparable. The
runner now rejects a blocked final result, unresolved core adaptive files,
and a start-story session that remains on `main`; each CLI session has a
600-second wall-clock timeout with partial event count and model IDs recorded.
A complete set of recorded sessions exits 2 until tests, product diff, TL/QA
verdicts, closure, and telemetry are independently assessed; CLI completion is
not a G2 pass.

## Requirements for a preinstalled frozen fixture

A future installed-workflow benchmark can start from a trusted, preinstalled
strict-mode snapshot instead of asking the benchmark agent to run `init project`.
That changes the measured scope to **story execution after installation** and
must be labelled as such. It must not be combined with the failed init costs.

1. Generate a baseline and candidate snapshot from their respective pinned
   devkit refs through the ordinary init output path. Finish the project-specific
   adaptive files during fixture preparation, outside the measured agent run.
   Do not bypass or reinterpret Claude's refusal during the failed run.
2. Freeze the fixture repository, installed file hashes, source ref, installer
   inputs, CLI/model/tool configuration, and exact story body in a versioned
   manifest. The baseline and candidate must differ only in the intended
   FIX-02 guidance. Validate installed templates against each pinned source.
3. Include `**Assigned:** Developer`, `**Status:** ready`, `**Sprint:**
   sprint-1`, `**Project Base Branch:** main`, explicit `Feature` and `Phase`,
   and Technical Scope for `pricing.py`. Preserve the same AC and expected diff.
4. Commit the root scaffold changes to each disposable fixture's `main` before
   measurement so branch preflight sees a clean base. Keep `.claude/agents/`
   installed and ignored as strict mode expects. Assert no remote exists.
5. For each repetition, copy a fresh snapshot, start `ST-000211`, and require
   the exact pricing diff, six passing tests, independent TL and QA verdicts,
   PO closure, zero unauthorized mutations, and complete or explicitly
   unavailable per-stage telemetry. Keep failed attempts as evidence.
6. Keep installation checks as a separate deterministic gate. If the benchmark
   is intended to include `init project` cost or behavior, a preinstalled
   snapshot does not satisfy that objective; the init blocker needs a supported
   tool permission path and a fresh comparable run.
