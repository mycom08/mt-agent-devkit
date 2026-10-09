# mt-agent-devkit

A multi-provider agent devkit that installs shared AI Scrum instructions and sprint workflows into software projects. Its default team has six roles: Technical Lead, Developer, QA, Product Owner, Business Analyst, and UI/UX Designer.

**Provider layouts:** Claude Code, Antigravity, and Codex share instructions, rules, context, and workflows under `.mt-agent-devkit/`. Each provider keeps its adapter and runtime state under `.claude/`, `.antigravity/`, or `.codex/`. Claude uses `CLAUDE.md`; Antigravity and Codex use `AGENTS.md`.

**Support scope in v0.1.51:** Deployment is mechanically tested across all three providers in GitHub and strict modes. Workflows require verified live provider capabilities. Automatic installed discovery, some native provider/mode runs, native legacy migration interpretation, and native macOS behavior remain unverified; see [ST-000232](https://github.com/mycom08/mt-agent-devkit/issues/232). Antigravity's default capability mapping is unset and must be supplied from its actual runtime. The native Claude read-routing audit validates internal role stages; it does not certify every installed workflow.

---

## What it does

| Capability | How |
|---|---|
| **Multi-agent sprint pipeline** | Spawns and coordinates agents across Implementation → Review → QA → Closure stages |
| **Role-separated workflows** | Each agent has its own instructions, rules, memory, and working record |
| **Story lifecycle management** | Tracks stories from `backlog` through `done` — via GitHub Issues (default) or local MD files (strict mode) |
| **Sprint planning and refinement** | Plan and refine backlog stories before execution |
| **Feature analysis** | BA-led elicitation and planning for new requirements |
| **Session continuity** | Agents resume mid-session; pipeline state survives restarts |
| **Project initialization** | Scaffolds all agent files into any target project in one command |

---

## Modes

| Mode | When to use |
|---|---|
| **github** (default) | Project has GitHub Issues, PRs, and Actions. Full integration. |
| **strict** | No GitHub or MCP required. Local repo only. Stories stored under the selected provider's runtime `agents/docs/` (gitignored). You control all merges — agents never push to remote. |

`init project` establishes the selected provider and asks which mode you want before writing. All providers installed in one target share the same mode and source version.

---

## Quick start — adding agents to your project

Enter this in your selected provider's chat inside mt-agent-devkit to scaffold agent files into another project:

```
init project /absolute/path/to/your-project
```

Or omit the path and the workflow will ask:

```
init project
```

The workflow will:

1. Validate the selected provider and choose **github** or **strict** mode
2. Scan your project (language, framework, key directories, existing CI/CD, test tooling)
3. Prepare reviewed project context, entrypoint text, and role customizations
4. Show the deployment plan, including writes, preserved content, and any migration conflicts
5. Ask for confirmation before applying the reviewed plan
6. Apply and verify the installation, then record its source and managed files in an installation receipt

**After init completes**, open your selected provider in the project and type:

```
workflow help
```

This shows all available commands and the recommended order to use them.

---

## Devkit workflows

Type these commands in your selected provider's chat **inside mt-agent-devkit**. `init project` and `update project` use the shared [target deployment workflow](.mt-agent-devkit/workflows/commands/Target_Project_Deployment_Workflow.md).

### Workflow Help
```
workflow help
```
Shows all available commands and a quick-start guide.

### Analyze Requirement
```
analyze <brief description>
```
Elicits, analyses, and plans a requirement from scratch. Produces a `/result/analyst/` folder with documents and diagrams suitable for any development team:

| File | For |
|---|---|
| `summary.md` | **Start here** — human-readable overview, architecture diagram, delivery plan, open items |
| `architecture.md` | Component design, data handling, alternatives, diagrams |
| `implementation_roadmap.md` | Phases, sprints, stories with AC, dependency graph, release criteria, risks |
| `business_requirements.md` | Functional + non-functional requirements, constraints, assumptions |
| `testing_plan.md` | Unit / integration / E2E strategy |
| `spec.md` | Full formalised specification |
| `elicitation_notes.md` | Full Q&A log from the interview |
| `diagrams/*.puml` | PlantUML source files for workflow and sequence diagrams |

### Init Project
```
init project [path]
```
Installs the shared harness and selected provider adapter into a target project. Prompts for mode (github / strict), reviews project-specific adaptations, and asks for confirmation before applying the deployment plan.

### Update Project
```
update project [path]
```
Builds the current local shared distribution and plans an update or legacy migration for an initialized project. Uses the installation receipt and exact file hashes to detect changes and conflicts. Project customizations require explicit review. Local deployment needs no release download and records local commit/snapshot provenance.

---

## Keeping projects up to date

### From the target project — `sync devkit`

```text
sync devkit
```

Resolves the latest released `vX.Y.Z` tag, pins its immutable commit, and validates the complete shared deployment artifact before planning an update. The installation receipt at `.mt-agent-devkit/install-receipt.json` records source identity and managed-file hashes. The workflow previews the plan and asks for confirmation before applying it.

For supported legacy v0.1.48–v0.1.50 Claude/Antigravity installations, compatible sync bridges lead into reviewed migration to the shared layout. The bridge path is mechanically tested within two invocations; native interpretation remains unverified. Missing or unknown version stamps require inspection rather than an assumed successful upgrade.

### From the devkit — `update project [path]`

```text
update project /path/to/your-project
```

Uses the local shared distribution through the same deployment engine. This is useful for offline updates and reviewing unreleased changes; a local snapshot install is recorded separately from a released-tag install.

### What both workflows preserve and verify

- Review project-specific instructions and entrypoint sections; upstream changes to customized managed files require an explicit resolution.
- Preserve project-owned context, unknown extra files, and provider-local memory, records, counters, and other runtime data. Runtime seeds create missing files only.
- Retire legacy files only through exact reviewed paths with verified shared successors; unexpected files are preserved.
- Block conflicting file edits, mixed modes, and active legacy workflows before migration.
- Verify managed content before finalizing the receipt and compatibility version stamp. The receipt is authoritative; an entrypoint version hint or provider-local `devkit_version.txt` alone does not certify installation.

Interrupted deployment has a recorded journal and supported `resume`/`rollback` operations. See the [deployment and migration guide](docs/feature/multi-provider-harness/Phase_2_Deployment_Operations.md) for review and recovery steps.

---

## Devkit versioning (for maintainers)

The release workflow owns `VERSION`, release tags, changelog dates, and the next snapshot. Add change descriptions under the current `- Unreleased` heading; do not bump versions manually.

| File | Purpose |
|---|---|
| `VERSION` | Current in-progress `x.y.z-SNAPSHOT` |
| `CHANGELOG.md` | Per-release descriptions of merged changes |
| `changes.json` | Per-version compatibility metadata and shared deployment manifest declaration |
| `.mt-agent-devkit/distribution/phase2/bundle/deployment.json` | Shared asset hashes, target mappings, provider/mode selections, and legacy retirement rules |

The current `changes.json` version object declares the shared artifact:

```json
{
  "deployment": {
    "schema_version": 1,
    "manifest": ".mt-agent-devkit/distribution/phase2/bundle/deployment.json"
  }
}
```

Legacy `files`/`new`/`modified` lists, descriptions, and checksums remain for compatible clients. The two sync bridges stay in the legacy namespace; the new shared payload is declared separately. Older version entries retain their historical formats. Keep deployment metadata inside version objects.

### Release checklist

1. Edit internal harness sources under `.mt-agent-devkit/` and, for target behavior, the active templates under `.mt-agent-devkit/distribution/phase2/templates/` plus the relevant provider adapter.
2. Rebuild the shared artifact with `python .mt-agent-devkit/distribution/phase2/build_bundle.py --root . --output .mt-agent-devkit/distribution/phase2/bundle` and verify with the same command plus `--check`. Historical `.claude/agents/templates/` sources remain frozen compatibility inputs except for reviewed bridges.
3. Maintain the current snapshot's deployment declaration and any changed legacy bridge metadata/checksums in `changes.json`; add a changelog entry.
4. Complete the applicable checks, independent review/QA, and merge gates. Publish support limits with the release.
5. Run the **Release** workflow from the Actions tab on `main`. It stamps the version and changelog, renames the snapshot manifest key, creates `vX.Y.Z`, and opens the next snapshot while carrying deployment/bridge metadata forward.

---

## Sprint workflows (available after `init project`)

The selected provider's root entrypoint routes to the shared orchestrator and workflows. Run these commands inside an initialized repository; type `workflow help` for the guide. A `project_root` installation supplies build/sync workflows, while sprint workflows run in its repositories.

### Recommended order

```
1. create stories       ← draft and save stories to the backlog
2. plan next sprint     ← assign backlog stories to a sprint, create sprint plan
3. refine sprint        ← raise and resolve questions before work starts
4. continue sprint      ← execute all ready stories end-to-end
```

Repeat steps 3–4 each sprint. Use `start story` to run a single story outside the full sprint loop.

### All commands

#### Create Stories
```
create stories
```
The selected provider acts as PO — drafts stories from your description, you confirm, then stories are saved to the backlog. In GitHub mode they become GitHub Issues; in strict mode they are written as local MD files under `<provider-root>/agents/docs/stories/`.

#### Plan Next Sprint
```
plan next sprint [feature]
```
PO verifies the current sprint is done, selects backlog stories up to sprint capacity, resolves open questions with TL, and publishes the sprint plan. In GitHub mode creates/labels Issues; in strict mode writes a local sprint overview file.

#### Refine Sprint
```
refine sprint
```
Each implementer reviews their assigned stories, posts questions for TL or PO, TL and PO answer in parallel, implementers confirm, PO moves resolved stories to `ready`.

#### Continue Sprint
```
continue sprint
```
Runs the full pipeline for every `ready` story: Implementation → Review → QA → Closure. In strict mode, each story gets its own branch off `sprint-N-dev`; when all stories are done you are notified to merge `sprint-N-dev` into your branch.

#### Start Story
```
start story ST-XXXXXX
```
Runs the pipeline for a single story. Picks up at the correct stage based on the story's current status.

#### Resume Story
```
resume story ST-XXXXXX
```
Unblocks a story after you have provided the missing information. Validates all required input is present before restarting the pipeline.

---

## Agent roles

| Agent | Responsibility |
|---|---|
| **Technical Lead** | Architecture, API specs, code review, PR approval |
| **Developer** | Story implementation, branch management |
| **QA** | Acceptance criteria validation, test scenarios, regression suite |
| **Product Owner** | Backlog ownership, scope gating, story closure, AC sign-off |
| **Business Analyst** | Requirements elicitation, use-case analysis, cost-benefit assessment |
| **UI/UX Designer** | Feature designs and UI/UX review |

---

## Story status flow

```
backlog → ready → in-progress → review → testing → done
                                          ↑
                               blocked (waiting on input)
                               resolved via "resume story ST-XXXXXX"
```

In GitHub mode, status is tracked via `status:*` issue labels. In strict mode, status is a `**Status:**` field in the story MD file. Status values are identical in both modes.

---

## Folder structure (after `init project`)

A repository-profile installation shares its harness across selected providers:

```text
your-project/
├── CLAUDE.md or AGENTS.md                 # selected provider entrypoint
├── .gitignore                            # managed runtime/migration ignores
├── .mt-agent-devkit/
│   ├── context/                          # project-owned priming and document index
│   ├── instructions/                     # shared roles and orchestrator
│   ├── rules/                            # shared standards and rules
│   ├── workflows/                        # shared, mode-specific workflows
│   ├── contracts/                        # provider selection and section reads
│   ├── scripts/                          # deployment, sync, and shared helpers
│   └── install-receipt.json               # verified source and managed hashes
└── .claude/, .antigravity/, or .codex/    # selected provider roots
    ├── harness/                          # adapter, capabilities, state bindings
    └── agents/                           # provider-local runtime
        ├── memory/
        ├── working-record/
        ├── retros/
        ├── tmp/
        └── docs/                         # strict stories, sprints, reviews, counter
```

Claude also installs role discovery wrappers under `.claude/agents/`, its read-section skill, and merged settings. Provider directories alone do not prove automatic native discovery.

In **GitHub mode**, shared harness content can be committed; provider-local runtime data and migration locks are ignored. In **strict mode**, `.mt-agent-devkit/` and selected provider roots are ignored, so local stories and runtime records stay out of commits. Entrypoint/project files remain outside those ignored directories.

Installed targets use `<provider-root>/agents` for runtime state. The devkit's own internal team uses `<provider-root>/agents/working`; these are different bindings.

---

## Prerequisites

### Both modes

- A selected AI provider runtime with verified agent lifecycle capabilities; missing or ambiguous mappings block workflows.
- Python **3.10+** for shared deployment, sync, and helper scripts.
- Git and a local repository.
- Bash or PowerShell for the corresponding shell launchers and project tooling.

### GitHub mode

- Authenticated [GitHub CLI](https://cli.github.com/) (`gh`) and a repository with Issues enabled.
- Project-specific CI and test tools required by the story.

### Strict mode

Story execution uses local records without GitHub mutations. `sync devkit` still needs access to published release artifacts; `update project` can use a local devkit checkout offline. See the [deployment guide](docs/feature/multi-provider-harness/Phase_2_Deployment_Operations.md) for provider capability and platform limits.

---

## Devkit structure

```text
mt-agent-devkit/
├── CLAUDE.md / AGENTS.md                 # provider entrypoints
├── README.md
├── VERSION / CHANGELOG.md / changes.json
├── .mt-agent-devkit/
│   ├── context/                         # internal priming
│   ├── instructions/                    # internal shared roles and orchestrator
│   ├── rules/                           # internal shared rules
│   ├── workflows/                       # internal story/sprint workflows
│   │   └── commands/                    # analyst and target deployment workflows
│   ├── contracts/                       # shared provider contracts
│   ├── scripts/                         # provider resolver, section reader, telemetry
│   └── distribution/phase2/
│       ├── templates/                   # active target sources
│       ├── bundle/                      # generated manifest and hashed assets
│       └── lifecycle.py / deployment.py / sync.py
├── .claude/ / .antigravity/ / .codex/
│   ├── harness/                         # provider adapters and mappings
│   └── agents/working/                  # devkit-internal runtime
├── .claude/agents/templates/             # frozen legacy sources and sync bridges
└── scripts/test/                        # automated regression coverage
```

Target installs use the compiled shared distribution and selected provider mappings, with reviewed adaptations to the project's stack. Internal devkit workflow bodies are kept separate from target sources. For ownership, migration, and native evidence boundaries, see the [deployment guide](docs/feature/multi-provider-harness/Phase_2_Deployment_Operations.md).
