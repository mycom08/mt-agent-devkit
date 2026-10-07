# CI Bootstrap Conventions (stack-generic baseline CI)

**This file is guidance for the CI Bootstrap generation agent to adapt, not a template to copy verbatim.** Unlike the Java skeleton shape files (which the Java Skeleton Generation agent does copy fairly literally, since Java gets a full domain skeleton), CI Bootstrap only ever writes one file — `.github/workflows/ci.yml` — for a repo whose actual code the agent did not generate. The agent must inspect the real repo (lockfile/manifest) before choosing commands, not assume the shape below applies unmodified.

Referenced from `Build_Software_Workflow.md`'s "CI Bootstrap" section (Path A step 7, Path B step h).

---

## When this applies

Only for a repo classified `full` in `repo_structure.md`'s CI column with no `.github/workflows/ci.yml` yet. `contract` (API-spec companion) and `none` (docs-only) repos are never touched — see the CI Bootstrap section's guard in `Build_Software_Workflow.md`. A Java repo almost always already has `ci.yml` by the time this step would run (Java Skeleton Generation writes one) — if a Java repo genuinely reaches this step, do not use this file's job graph; follow `java/Java_Skeleton_Conventions.md`'s "GitHub Actions CI" guidance instead.

---

## Triggers — always path-filtered

Same convention as the Java skeleton shapes, reused verbatim — agent memory commits (`.claude/agents/memory/`), README/docs edits, and other non-code changes must not burn CI runs:

```yaml
on:
  push:
    branches: [main]
    paths-ignore: ['.claude/**', '**.md', 'docs/**']
  pull_request:
    paths-ignore: ['.claude/**', '**.md', 'docs/**']
```

> **Required-checks caveat (note it in the completion report):** if the project later marks any of these jobs as a *required* status check, docs-only PRs will wait forever on checks that never start. Either keep the jobs non-required, or add a trivially-passing fallback workflow with the same job names triggered on the inverse `paths:` filter.

---

## Job graph — 3 jobs, no deploy/release job

Baseline only. Never invent a deploy target — the PO roadmap CI story (Analyst workflow rule) is the upgrade path from this baseline to a real deploy pipeline, not this step.

- **`build-and-test`** — toolchain setup + install dependencies + build + unit test. Combine build and unit test into one job step sequence where the stack's own tooling already runs tests as part of its normal build/test command (e.g. `npm test`, `pytest`, `go test ./...`) — don't split into two jobs for no benefit, same reasoning as the Java shapes' `mvnw verify`.
- **`lint`** — the stack's standard linter/formatter check (see the mapping table below). If the repo has no linter configured yet, add the ecosystem's conventional default rather than skipping the job — a no-op lint job provides no signal.
- **`automation-test`** — stub job, `needs: build-and-test`. No real end-to-end/API test suite exists yet at bootstrap time. Generate the job shell (checkout, `needs: build-and-test`) with a single step that echoes `"TODO: no automation test suite yet — add one under tests/automation/ and replace this step."` and exits 0. The job exists from day one so the pipeline shape is correct; a later story replaces the stub, not a whole new job.

---

## Per-stack tool mappings (adapt, don't copy)

Detect the real stack from the repo's own lockfile/manifest file, not just the `repo_structure.md` Tech Stack text (that text is a hint, the manifest is the source of truth if they disagree).

| Stack (detected via) | Setup action | Build/test | Lint |
|---|---|---|---|
| Node (`package.json`) | `actions/setup-node@v4` | `npm ci` → `npm run build --if-present` → `npm test` | `npm run lint --if-present`, else `npx eslint .` if an eslint config exists |
| Python (`pyproject.toml` / `requirements.txt`) | `actions/setup-python@v5` | `pip install -r requirements.txt` (or `poetry install` if `pyproject.toml` uses Poetry) → `pytest` | `ruff check .` (fallback `flake8` if no ruff config) |
| Go (`go.mod`) | `actions/setup-go@v5` | `go build ./...` → `go test ./...` | `golangci-lint run` (fallback `go vet ./...` if no golangci-lint config) |
| Gradle/Maven (`pom.xml` / `build.gradle*`) | — | **Fallback pointer only, not this file's job graph** — reuse `java/Java_Skeleton_Conventions.md`'s "GitHub Actions CI" guidance as-is. This path is rare: a brand-new Java repo normally already got `ci.yml` from Java Skeleton Generation before Bootstrap would ever run; this only covers a pre-existing Java repo with code and no `ci.yml`. |
| Unrecognized stack | — | Best-effort: guess the toolchain from whatever manifest/lockfile is actually present. If genuinely undetectable, still generate the 3-job shell with a `TODO` step (same pattern as `automation-test`) — never fabricate a plausible-looking build/test/lint command for a stack you can't identify. State this plainly in the agent's report. |

---

## Must not do

- Do not write a deploy/release/publish job of any kind.
- Do not overwrite an existing `.github/workflows/ci.yml` — the generation agent is only ever spawned because the file doesn't exist yet.
- Do not touch a `contract`- or `none`-classified repo.
- Do not fabricate a build/test/lint command for a stack you cannot identify from the repo's own manifest/lockfile — generate the job shell with a `TODO` step instead and say so in the report.
- Do not use this file's job graph for a Java (Gradle/Maven) repo — defer to `java/Java_Skeleton_Conventions.md`'s CI guidance instead.
