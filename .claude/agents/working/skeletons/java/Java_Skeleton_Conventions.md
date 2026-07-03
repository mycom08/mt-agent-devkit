# Java Skeleton Conventions

> Read by the Stage 4 skeleton-generation agent (`Build_Software_Workflow.md`), never copied verbatim. This document and its three shape-specific companions in this folder describe **conventions and illustrative shapes**, not literal files — the agent generates real, project-specific code that follows these patterns, using the actual domain from `architecture.md` (real entity/resource names, real endpoints), not a generic placeholder like "Example".
>
> Distilled from three real internal reference projects, with all proprietary/internal dependencies stripped to public Maven Central equivalents so the result builds for any devkit user.

---

## When this applies

Only for repos whose tech stack (from `repo_structure.md` / `architecture.md`) is Java-based, **and** whose local path has no `pom.xml`, `build.gradle`, or `build.gradle.kts`, and no `src/` directory yet (see Stage 4 for the exact check). If any exists, skip skeleton generation entirely — never scaffold over or alongside existing code.

Three shapes, chosen by the agent from the repo's stated purpose in `repo_structure.md`. **Decide the shape here, then read only that shape's file below — never all three:**

| Shape | When | Reference | Read |
|---|---|---|---|
| **API spec** | Repo purpose describes the OpenAPI/Swagger contract for a REST service (no runtime, no database — just a compiled contract artifact) | cp-tenant-service-api-spec | [`Java_Skeleton_API_Spec.md`](./Java_Skeleton_API_Spec.md) |
| **REST service** | Repo purpose describes a backend/API/service (runs standalone, owns a database, exposes HTTP endpoints) | cp-tenant-service | [`Java_Skeleton_REST_Service.md`](./Java_Skeleton_REST_Service.md) |
| **Pure library** | Repo purpose describes a reusable library/SDK/client consumed by other Java projects (no standalone runtime, no database of its own) | cp-security-configure | [`Java_Skeleton_Library.md`](./Java_Skeleton_Library.md) |

**Every Java REST service always has a companion API spec repo — this is a fixed devkit convention, not conditional on `architecture.md`.** `Build_Software_Workflow.md` Stage 2 adds the companion `<repo-name>-api-spec` repo to `repo_structure.md` automatically whenever a Java REST service is planned, ordered *before* its service in the repo table so Stage 4 scaffolds the contract first — the REST service's skeleton depends on it existing.

---

## Reference project (optional, user-supplied)

`Build_Software_Workflow.md` Stage 4 asks the user, once per Java repo and before any generation starts, whether they have an existing local project to use as a structural reference — a path outside this devkit and outside the repo being scaffolded (e.g. a service already on their machine that follows their team's conventions). If the user supplies one, the generation agent reads that reference project's actual folder layout, build file, and package conventions and follows its structural/style choices for anything this document or its shape file leaves as a judgment call (e.g. extra layers beyond the ones listed, naming variations, module boundaries).

**The reference project never overrides a fixed rule in this document or its shape file.** Every convention marked as a fixed rule (no Lombok, DTOs are records, MapStruct for mapping, layering direction, the Healthcheck / Authentication / VERSION+CHANGELOG requirements) applies regardless of what the reference project does. If the reference project conflicts with a fixed rule (e.g. it uses Lombok, or has no health endpoint), generate the skeleton per the rule anyway and note the deviation in the agent's report. A reference project only ever narrows down the *unconstrained* choices — it never loosens a fixed one. This also applies to a reference project's own dependency coordinates: you may follow its **code structure and conventions**, but never copy a private/internal Maven coordinate out of it (see "Do not include internal artifacts" in the REST service file) — a reference project informs how you write your own code, not what proprietary artifact you depend on.

If the user does not supply a reference project (answer is "default"), generate purely from these documents with no external project to consult.

---

## Universal conventions (apply before, or regardless of, the chosen shape)

- **Build tool:** Maven (`pom.xml`) or Gradle (`build.gradle` / `build.gradle.kts`) — asked explicitly at `Build_Software_Workflow.md` Stage 4's Java Repo Consultation gate, shared by every Java repo in the build, and passed into the generation prompt as a fixed input. Default **Apache Maven** if the user doesn't specify. Do not infer the build tool from `architecture.md` or choose independently per repo — the consultation answer always wins. The two build tools are **structurally equivalent conventions** in each shape file, just expressed differently — same dependencies, same annotation processors, same layering; only the manifest syntax and dependency-scope keywords differ (Maven `scope` ↔ Gradle `configuration`). Never mix build tools in one repo, and never generate both a `pom.xml` and a `build.gradle` in the same skeleton.
- **Java version / Spring Boot version:** pull the exact versions from `architecture.md`'s tech-stack decision if it names them; otherwise default to **Java 25 (LTS)** and the latest stable Spring Boot GA release that supports it at generation time.
- **No Lombok anywhere, in any shape.** DTOs / value objects are Java records; the REST service shape's entities are hand-written plain classes (never records — JPA needs a no-arg constructor and mutable fields). This also sidesteps the Lombok↔MapStruct annotation-processor ordering issue entirely. See the REST service file for entity/DTO/mapper specifics.
- **Package root:** `{groupId}.{artifactId-without-dashes}` in every shape. Both values come from `Build_Software_Workflow.md` Stage 4's Java Repo Consultation gate, asked once before any repo is generated — never invented or guessed by the generation agent from `architecture.md`. `groupId` is the single value the user supplied there (`com.example` if they didn't), shared by every Java repo in the build. `artifactId` is always this repo's own `name` from `repo_structure.md` (already a lowercase, hyphenated slug by that table's own convention), with dashes stripped for the package segment. The orchestrator passes the resolved `groupId`, `artifactId`, and base package straight into the generation prompt — treat them as fixed inputs, not something to derive. How the root is sub-packaged from there is shape-specific — see each shape's file.

---

## Dependency management & GitHub Packages (every shape)

**Every Java repo publishes its build artifact to GitHub Packages — a fixed devkit convention, not optional, regardless of shape.** This is the release/distribution channel; it is separate from, and does not change, how a repo is built locally.

**Publish config (in the build file, generated alongside everything else):**
- **Maven:** a `<distributionManagement>` block pointing at this repo's own GitHub Packages endpoint, `https://maven.pkg.github.com/<owner>/<repo-name>`, with `<id>github</id>`.
- **Gradle:** the `maven-publish` plugin, publishing to a `maven { name = "GitHubPackages"; url = uri("https://maven.pkg.github.com/<owner>/<repo-name>") }` repository, credentials from the `GITHUB_ACTOR`/`GITHUB_TOKEN` environment variables (never hardcoded).

**Use `github` as the `<id>`/repository name everywhere**, in every shape's `<distributionManagement>` and in any `<repositories>` entry that resolves a *different* repo's published package (see the REST service file for the sibling-api-spec case) — not a per-repo-unique id. This lets a single CI credentials setup (one `actions/setup-java` call with `server-id: github`) authenticate against every GitHub Packages URL in the build file, publish or resolve, without juggling multiple server entries.

**CI publish job (add to `.github/workflows/ci.yml` in every shape, alongside the existing jobs):** triggered on push to `main` only (not on pull requests), runs after `build-and-test` succeeds, uses `actions/setup-java@v4`'s `server-id: github` input (which auto-writes a `~/.m2/settings.xml`-equivalent wired to `GITHUB_ACTOR`/`GITHUB_TOKEN` at runtime — never commit a settings.xml to the repo), needs `permissions: packages: write`, and runs `./mvnw -B deploy -DskipTests` (or the Gradle `publish` task). `GITHUB_TOKEN` is the Actions-provided token — no PAT or extra secret needs creating for this job to work.

```yaml
publish:
  needs: build-and-test
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  runs-on: ubuntu-latest
  permissions:
    contents: read
    packages: write
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-java@v4
      with:
        java-version: '<javaVersion>'
        distribution: temurin
        server-id: github
        server-username: GITHUB_ACTOR
        server-password: GITHUB_TOKEN
    - name: Publish to GitHub Packages
      run: ./mvnw -B deploy -DskipTests
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
(Gradle equivalent: same job shape, final step `./gradlew publish` with the same env.)

**This only ever publishes — it never triggers from a local build.** `<distributionManagement>`/`maven-publish` config is inert for `package`, `install`, `test`, or `docker compose up --build` — those never run `deploy`/`publish`. Only this CI job, and a developer explicitly running `mvn deploy` by hand (which would itself need a personal PAT with `write:packages` to succeed), can push a build to GitHub Packages. Local/Docker builds are never affected by this section.

**Versions stay `-SNAPSHOT` for this to work continuously.** GitHub Packages rejects republishing the same non-`SNAPSHOT` (release) version — `SNAPSHOT` versions can be overwritten on every push. The skeleton's initial `pom.xml`/`build.gradle` version (see "Version & Release Management" below) should carry `-SNAPSHOT` so "publish on every push to main" doesn't start failing after the second push; bumping to a real release version is a later, separate action outside skeleton generation.

---

## Version & Release Management (every shape)

**Every generated repo gets a `VERSION` file, a `CHANGELOG.md`, and a manually-triggered `.github/workflows/release.yml` — no exceptions, including the API spec shape** (this overrides any earlier notion that API spec's independent Maven `<version>` was enough on its own; it still versions independently, it just also gets the same VERSION/CHANGELOG/release.yml trio as every other shape). "Release artifact" differs by shape — a Docker image for the REST service shape, a release-version Maven package for library and API spec — see each shape's own Release files section for the exact step.

Adapted from a real internal reference project's release workflow (`lhtuwrk/authorization-service`, `.github/workflows/release.yml` and `CHANGELOG.md`) — branch names, image registry paths, and the dual-branch guard are genericized for any devkit user; the underlying validate → build → tag → bump-forward flow is kept as-is.

### `VERSION`

A single-line file at the repo root, no trailing whitespace, one of two shapes:
- **Snapshot** (the normal day-to-day state): `x.x.x-SNAPSHOT`. This is what the continuous `publish` job (above) deploys on every push to main.
- **Release** (only momentarily true, set by hand right before triggering `release.yml`): `x.x.x`, no suffix.

**Initial value at generation time: `0.0.1-SNAPSHOT`** — every shape, no exceptions, always this exact value regardless of what `architecture.md` might otherwise suggest. Stripping the `-SNAPSHOT` suffix to cut an actual release is a deliberate, manual, later action by a human — skeleton generation never produces a non-`-SNAPSHOT` `VERSION`.

### `CHANGELOG.md`

Not [Keep a Changelog](https://keepachangelog.com/)'s two-permanent-section format — this devkit follows the reference project's single-next-version-heading style instead, since `release.yml` validates directly against it:

```markdown
# Changelog

All notable changes to this project are documented in this file.

## Contribution Convention

After merging a PR to main, the implementer adds a bullet entry under the relevant
subsection of the current Unreleased version below. Use the following subsections:

- **Changes** — new features, enhancements, refactors, documentation, CI/tooling
- **Bug Fixes** — defect corrections and hotfixes

Entry format: `- [ST-XXXXXX] Short description of the change.`

---

## [0.0.1] - Unreleased

### Changes

### Bug Fixes
```

The top heading always names the *next* version to be cut (matching `VERSION` once its `-SNAPSHOT` suffix is stripped), suffixed `- Unreleased` until `release.yml` stamps it with the actual release date. `[ST-XXXXXX]` matches this devkit's own story ID convention (`Story_Standard.md`) — target-project developers add one bullet per merged story under `### Changes` or `### Bug Fixes` as they go, so the section is never empty by the time someone wants to release.

### `.github/workflows/release.yml`

Manually triggered (`workflow_dispatch`) — never automatic, unlike the continuous `publish` job. A human decides when to cut a release, strips `VERSION`'s `-SNAPSHOT` suffix by hand, confirms the CHANGELOG section for that version has real entries, then runs this workflow. Steps, in order:

1. **Guard** — fail immediately unless running from `main` (the reference project's `master`/`ci-validation` dual-branch guard is a reference-project quirk, not a convention to copy — adapt to whatever the target project's actual default branch is if it differs from `main`).
2. **Read and validate `VERSION`** — must match `^[0-9]+\.[0-9]+\.[0-9]+$` exactly (no `-SNAPSHOT`, no stray characters). Fail the job if it doesn't — this is what stops someone accidentally releasing a snapshot.
3. **Check the tag doesn't already exist** — `git ls-remote --tags origin v{version}`; fail if found.
4. **Validate `CHANGELOG.md` has a `## [{version}]` heading** — fail if missing.
5. **Validate that heading's section is non-empty** — at least one `-` bullet under `### Changes` or `### Bug Fixes` between this heading and the next `## [`; fail if empty.
6. **Build and publish the release artifact** — shape-dependent, see each shape's own Release files section for the exact step (Docker image build+push for REST service; `mvn deploy`/`gradle publish` at the clean release version for library and API spec).
7. **Stamp the CHANGELOG heading** — `## [{version}] - Unreleased` → `## [{version}] - {today's date}`, commit directly to the release branch (bot git identity, e.g. `github-actions[bot]`).
8. **Create a GitHub Release + tag** `v{version}` on the now-stamped commit.
9. **Bump forward** — compute the next patch version, prepend a fresh `## [{next-version}] - Unreleased` / `### Changes` / `### Bug Fixes` section to the top of `CHANGELOG.md`, set `VERSION` to `{next-version}-SNAPSHOT`, commit and push. This is what keeps the repo always sitting on a snapshot version between releases, ready for the next `release.yml` run.

The reference project also gates step 9 behind a post-release smoke-test job (deploying the freshly-tagged image and running smoke tests) before bumping forward. **Skip that gate in the generated skeleton** — a brand-new repo has no deployment target configured yet, so there's nothing to smoke-test against. Run step 9 directly after step 8 instead. Wiring a real deploy-and-smoke gate back in is a separate, later instruction once an actual deployment target exists.

### How this coexists with the continuous `publish` job

Two different GitHub-Packages-touching CI jobs exist side by side, for two different purposes — this is intentional, not a duplication:

| | `publish` (Dependency management & GitHub Packages, above) | `release` (this section) |
|---|---|---|
| Trigger | Every push to `main` | Manual (`workflow_dispatch`) |
| Version published | Whatever's currently in `VERSION`/build file — normally `-SNAPSHOT` | The clean release version, stripped of `-SNAPSHOT` by hand beforehand |
| Purpose | Keeps the latest snapshot resolvable in GitHub Packages so sibling repos (e.g. a REST service resolving its api-spec) always see current `main` | Cuts an actual numbered release: Docker image (REST service) or release-version Maven package (library/API spec), GitHub Release, tag, CHANGELOG entry |
| Artifact target | `maven.pkg.github.com` (Maven jar) | `ghcr.io` (REST service Docker image) or `maven.pkg.github.com` (library/API spec release jar) |

---

## What every shape must NOT do

- Do not invent proprietary-looking internal dependencies (`com.mycom.cp:*` or similar) — only use real, publicly-resolvable Maven Central artifacts.
- Do not scaffold into a repo that already has `pom.xml`/`build.gradle` or a `src/` directory — that repo already has a real project; leave it untouched.
- Do not generate both `pom.xml` and `build.gradle` in the same repo.
- Do not add Lombok, in any shape.
- Do not let a user-supplied reference project override a fixed rule in this document or the shape file (Lombok, entity/DTO conventions, layering, healthcheck, security baseline, VERSION/CHANGELOG, GitHub Packages publishing) — a reference project only informs structural/style choices left open. Never copy a reference project's private Maven coordinates into the generated build file.
- Do not choose the build tool independently per repo, or infer it from `architecture.md` — use the `Build tool` value passed into the generation prompt (see "Build tool" above), the same for every Java repo in this build.
- Do not skip the `<distributionManagement>`/`maven-publish` GitHub Packages config or its CI `publish` job, in any shape — "release artifacts use GitHub Package" is a fixed devkit convention, not optional.
- Do not skip `VERSION`, `CHANGELOG.md`, or `.github/workflows/release.yml` in any shape, including API spec — every generated repo gets all three, regardless of what it does or doesn't otherwise version independently.
- Do not generate `VERSION` with any value other than `0.0.1-SNAPSHOT` at generation time.
- Do not use the Keep a Changelog two-permanent-section format for `CHANGELOG.md` — use the single-next-version-heading style in "Version & Release Management" above; `release.yml` validates against it directly and would fail against a different structure.

Each shape file has its own additional "must not do" list for rules specific to that shape.
