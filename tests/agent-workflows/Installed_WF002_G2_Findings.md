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

**Permission limit for the proposed snapshot route:** Preinstalling the files
does not by itself make a strict story run executable. The installed workflow
must write story status, review records, retro records, and telemetry under
`.claude/agents/`. The failed init run already showed Claude's file tool
refusing writes under that path. It is therefore likely that a story-only run
with the same headless permission configuration would stop on its first state
write. This is an inference from the workflow's required writes, not a measured
story-only failure. A supported permission handler for those disposable paths
must be established and tested before paying for three full repetitions; the
runner must not silently substitute shell writes for denied file-tool writes.

**Auto-mode probe (2026-09-30):** A separate disposable fixture invoked Claude
Code with the installed runner's `--restricted`/headless settings, changing
only `--permission-mode` from `acceptEdits` to `auto`. It asked `Write` to create
`.claude/agents/tmp/probe.txt` and explicitly prohibited shell alternatives.
The `Write` tool was denied as requiring approval; the file was not created.
The probe cost $0.0205456. Thus auto mode alone does not resolve this protected
path under the current `--permission-prompts none` configuration. The raw
probe stream remains local in an ignored disposable directory.

A separate `acceptEdits` probe used the original restricted/headless settings
and asked `Write` to create `.wf002-tmp/probe.py` in a disposable target.
It succeeded without a prompt and cost $0.0064888. The installed runner now
directs temporary helpers to that ordinary staging folder, while requiring
normal file-tool writes for final `.claude/agents/` content. This confirms a
safe staging location for helper code; it does not yet show that Claude can
complete every protected final write in the installed workflow.

**Baseline-only init retry (2026-09-30):** With the helper staged outside
`.claude/` and final agent files required to use normal file tools, a fresh
baseline init used Claude Code 2.1.285, resolved model `claude-sonnet-5-5`,
and a $1.50 session cap. It spent $0.4350228. The mechanical scaffold and
root `CLAUDE.md`/README adaptation succeeded. Direct `Write` attempts for
`.claude/agents/context/Project_Priming.md` and `Document_Index.md` then
required approval and were denied in the headless session. `verify_install`
found the six role instruction files and `Story_Standard.md` still missing.
The candidate arm was not launched. This confirms that moving the temporary
helper solves its own path denial but does not solve final adaptive-file writes.
G2 remains failed; no baseline measurement resulted.

## Interactive baseline diagnostic (2026-10-01)

The user confirmed that a person can approve a direct Claude Code `Write` under
the protected `.claude/agents/` path. A fresh disposable target was then seeded
from the frozen WF-002 fixture, and the baseline devkit was exported from
`a30460a87c6d439b1193c45b77cc638a8f237fdb`. The target had no remote.
Claude Code 2.1.286 ran interactively with `--restricted`, `acceptEdits`, the
installed runner's tool set, resolved model `claude-sonnet-5-5`, and medium
effort. The user approved
protected writes during init. The installed-file verifier passed all required
files, the non-ignored scaffold was committed on `main` as `59fa570`, and the
fixed story was seeded with a clean working tree. Raw session transcripts and
the disposable target remain outside tracked Git content.

The baseline `start story ST-000211` run reached PO closure. The Developer's
`bc324c9` commit changed `pricing.py` from `>` to `>=`; the TL review approved
that SHA, QA recorded an independent AC-by-AC verdict, the PO marked all five
AC complete and set the story to `done`, and the story was merged into
`sprint-1-dev` as `2e24dcf`. A separate local verification ran all six unit
tests successfully on the merged branch. `main` was untouched and no remote
was added.

This is **diagnostic, not a G2 pass or efficiency baseline**:

- The quality contract's `changed_paths_exactly` value is `pricing.py`, but the
  committed diff also contains a `CHANGELOG.md` entry required by the installed
  workflow. The contract and workflow need a consistent scope rule before a
  comparable run.
- All four stage telemetry rows explicitly report unavailable token and request
  fields. Their start/end timestamps are approximate placeholders; the saved
  subagent transcripts permit a separate extraction of real stage durations
  and usage, but the written rows are not valid measurement evidence.
- The installed workflow stopped after Stage 5 to ask for a retro decision.
  The user answered `none`; Claude applied no proposed rules or workflow edits,
  wrote the sprint summary, and removed the retro and pipeline state files.
- Interactive user approval time and the lack of a `--max-budget-usd` cap make
  this run different from the frozen headless configuration. No repeated
  baseline/candidate pairs have been run with this permission path.

The saved Claude subagent transcripts are present for Developer, TL, QA, and PO.
An independent read-only pass through the installed telemetry parser recovered
8, 11, 6, and 6 API requests respectively, plus usage and tool counts. This
shows that the four `unavailable` stage rows are an extraction gap, not absent
raw evidence. The recorded stage start/end timestamps remain inaccurate and
must not be used for a duration comparison. The transcript event ranges and
`duration_ms` values agree for each stage; they exclude orchestration and user
approval time.

## Interactive candidate diagnostic (2026-10-01)

The candidate devkit was exported from
`e2e700aa2e1014011c07c789458d13501a92f661` into a fresh remote-free
target. The same installed-file verifier passed, the non-ignored scaffold was
committed on `main` as `09d7933`, and the same ST-000211 story was seeded.
Claude Code 2.1.286 ran interactively with the same top-level model, effort,
tool list, and restricted permission mode. The user approved protected writes.

The candidate `start story` run changed the same threshold comparison, with
Developer commit `096a64d`, TL approval at that SHA, an independent QA verdict,
and PO closure. It merged into `sprint-1-dev` as `aeb7c6c`; `main` and remote
state were untouched. An independent local run of the six unit tests passed.
The committed diff again contains `CHANGELOG.md` as well as `pricing.py`.
The retro review received `none`; Claude wrote the sprint summary and deleted
the per-story retro and pipeline state files.

The PO accepted all five AC and set the story to `done`, but left the seeded
numbered AC list as numbered items. In the baseline, PO converted those same
items to checked boxes. The installed workflow expects checkboxes for PO
closure, so this is a fixture ambiguity and a behavioral difference. Formal
repetitions should seed valid unchecked boxes and keep the AC wording fixed.

Both runs wrote four telemetry rows with usage fields marked unavailable.
Their saved subagent transcripts were parsed afterward with the installed
`telemetry.py` logic, yielding these **diagnostic stage totals** (excluding
the orchestrator and human approval time):

| Arm | Requests | Tool calls | Cache create tokens | Cache read tokens | Output tokens | Sum of stage durations |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 31 | 73 | 189,133 | 1,021,626 | 21,392 | 215.8 s |
| Candidate | 43 | 57 | 155,951 | 1,501,415 | 23,788 | 294.5 s |

This single pair does not establish a FIX-02 efficiency benefit. Candidate
requests, cache reads, output tokens, and summed stage duration were higher;
tool calls and cache creation tokens were lower. The TL and PO stages account
for much of the increase. The original frozen manifest pins Claude Code
2.1.280, a different resolved model, and a narrower tool set, so this
interactive installed pair needs its own exact configuration manifest before
it can contribute to a formal G2 comparison. Repair the installed fixture's
AC format, define whether the workflow-required CHANGELOG entry is in the
allowed diff, and extract real transcript telemetry during the run before
starting repeated pairs.

The installed runner now converts the frozen story's five numbered AC into
unchecked boxes when seeding an installed target, preserving their wording and
order. It also commits the non-ignored init scaffold on local `main` and
requires a clean tree before starting the story. Nine deterministic runner
tests pass. These fixture repairs have not received a new paid agent run;
the interactive pair above remains diagnostic. The installed diff contract,
in-run transcript extraction, and a repeatable approved permission path remain
open before formal G2 repetitions.

## G2 preparation follow-up (2026-10-01)

The runner now evaluates the installed product diff against the frozen
`pricing.py` oracle while treating the workflow-required `CHANGELOG.md` entry
as separate bookkeeping. It reports unrelated changed paths and rejects a
missing or non-exact threshold edit. It also checks for one telemetry row per
Developer, TL, QA, and PO stage, and distinguishes recorded rows from measured
request/cache usage. An independent target check requires the five unchanged
AC to be checked and all six unit tests to pass. Twelve deterministic
preparation tests pass. These checks
make the earlier diagnostic gaps visible in each run summary; they do not
convert the diagnostic pair into G2 evidence or resolve the protected-write
permission path. A new installed run remains necessary.
## 2026-10-02: headless protected-write reproduction and scoped fix

Claude Code 2.1.287, resolved model `claude-sonnet-5-5`, medium effort,
`--restricted --permission-mode acceptEdits --permission-prompts none`, and
explicit `Read,Edit,Write` tools still deny a normal `Write` to
`.claude/agents/tmp/probe.txt`. The target file was absent despite CLI exit 0
and a result event with `is_error: false`.

The installed runner now supplies a trusted `--settings` file outside the
disposable target containing a `PermissionRequest` command hook. Its handler
approves only `Write` and `Edit` paths resolving below the disposable target's
`.claude/` directory. Other tools, source checkout paths, `.git`, traversal,
and symlink escapes are denied. Restricted mode, tool limits, and
`--permission-prompts none` remain enabled. This uses Claude Code's documented
[PermissionRequest decision control](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control).

Live headless verification in a fresh disposable directory:

- Original configuration: protected write denied; no file created.
- With handler: protected write created `HEADLESS_PROBE_OK`; zero denials.
- Protected `Edit`: content changed to `HEADLESS_EDIT_OK`.
- Out-of-workspace write: denied; no file created.
- Foreground general-purpose subagent: created `SUBAGENT_OK`; zero denials.

The 14 installed preparation tests pass. Two permission boundary tests pass;
the directory symlink test is skipped on this Windows host because symlink
creation is unavailable. The runner treats recorded permission denials as
workflow failure and records the policy description and handler SHA-256 in
the benchmark configuration. These are permission smoke checks, not completed
G2/G6 benchmarks. Fresh comparable installed runs are still required.
