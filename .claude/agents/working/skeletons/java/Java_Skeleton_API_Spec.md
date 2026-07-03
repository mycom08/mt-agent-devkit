# Java Skeleton — API Spec Shape

> Companion to [`Java_Skeleton_Conventions.md`](./Java_Skeleton_Conventions.md) — read that file first for "When this applies," the shape-decision table, the Reference Project rule, and universal conventions (build tool, Java version, no-Lombok, package root). This file covers only the API spec shape end-to-end; you should not need to open the REST Service or Library files while generating this shape.

**Reference:** cp-tenant-service-api-spec

---

## Purpose

A **contract-first** OpenAPI/Swagger YAML file, compiled into Java API interfaces + model classes via `openapi-generator` at build time. It is its own Maven/Gradle artifact — no `@SpringBootApplication`, no database, no runtime. The companion REST service depends on it and implements the generated interface(s), rather than hand-writing controller method signatures or request/response DTOs.

## The spec file

One hand-written OpenAPI 3.x YAML file per service, e.g. `src/main/resources/api-spec/{service-name}-api-spec.yaml` (a resources path, not `src/main/java` — despite the reference project placing it under `src/main/java/api-spec/`, YAML belongs under `src/main/resources`; that placement is a **reference-project quirk, not a convention to copy**). Content: standard OpenAPI 3.x — `info`, `tags`, `paths` (one entry per real endpoint, with `operationId`, `parameters`, `requestBody`, and a `responses` map covering every real status code the service returns — 2xx success, 400/401/403/404/409 as applicable, 500/503), `components.schemas` (one schema per real resource, matching the entity's real fields), `components.securitySchemes` if the service has auth. Use the actual domain/resource names and endpoints from `architecture.md` — never a placeholder `Example` schema.

## Build file

**If Maven — `pom.xml`:** no Spring Boot parent (this isn't a runnable app). Dependencies: `jakarta.validation-api`, `jackson-databind-nullable` (required by openapi-generator's Spring output for nullable-vs-absent JSON fields). Plugin: `org.openapitools:openapi-generator-maven-plugin`, `generate` goal bound to a build phase, configured with:
```xml
<configuration>
    <inputSpec>${project.basedir}/src/main/resources/api-spec/<service-name>-api-spec.yaml</inputSpec>
    <generatorName>spring</generatorName>
    <apiPackage>{{SERVICE_PACKAGE_NAME}}.api.spec.api</apiPackage>
    <modelPackage>{{SERVICE_PACKAGE_NAME}}.api.spec.model</modelPackage>
    <configOptions>
        <interfaceOnly>true</interfaceOnly>          <!-- only generate interfaces + models, no controller impl -->
        <useSpringBoot3>true</useSpringBoot3>          <!-- set the flag matching the generator's support for the project's actual Spring Boot major version -->
        <documentationProvider>none</documentationProvider>  <!-- no Swagger annotations baked into generated code — springdoc in the REST service documents the live API instead -->
        <skipDefaultInterface>true</skipDefaultInterface>    <!-- force the controller to implement every operation explicitly, no silent 501 defaults -->
    </configOptions>
    <generateSupportingFiles>false</generateSupportingFiles>
</configuration>
```
**Important convention:** `apiPackage`/`modelPackage` are namespaced under the **consuming REST service's own package**, not the api-spec artifact's own package — e.g. an api-spec artifact for a `tenant-service` (package `com.example.tenantservice`) generates into `com.example.tenantservice.api.spec.api` / `.model`, so the service's controller can `implements TenantsApi` directly using its own package's classes. The consuming service's base package is deterministic, not something to infer from `architecture.md`: it's `{groupId}.{artifactId-without-dashes}` using the build's shared `groupId` and the REST service repo's own `name` from `repo_structure.md` as `artifactId` (see `Java_Skeleton_Conventions.md`'s "Package root" convention) — both values were passed into your generation prompt for the api-spec repo itself, and the REST service repo (its sibling, scaffolded right after) uses the same `groupId` with its own `artifactId`.

**If Gradle — `build.gradle`:** apply the `org.openapi.generator` plugin (community Gradle plugin, functionally equivalent to the Maven plugin above) instead of `java`/`java-library`, with the matching `openApiGenerate` task configuration (`inputSpec`, `generatorName = 'spring'`, `apiPackage`, `modelPackage`, `configOptions`, `generateApiDocumentation = false`). Same dependencies (`jakarta.validation-api`, `jackson-databind-nullable`) as `implementation`.

**GitHub Packages — publish config.** This is the most important shape to get this right for: the REST service resolves this artifact from GitHub Packages in any build context that doesn't have the sibling folder present (notably its own CI `build-and-test` job — see `Java_Skeleton_REST_Service.md`'s "Resolving the sibling API spec dependency"). Add the `<distributionManagement>` block (Maven) / `maven-publish` config (Gradle) described in `Java_Skeleton_Conventions.md`'s "Dependency management & GitHub Packages" section, pointing at this repo's own GitHub Packages endpoint, plus the `publish` CI job described there (on push to `main`). Without this, the REST service's CI build has no way to resolve this dependency at all.

## Versioning

The api-spec artifact versions **independently** from the service that consumes it (e.g. service at `0.0.1-SNAPSHOT`, its api-spec at its own separate `0.0.1-SNAPSHOT`, bumped on its own release schedule) — the version reflects the contract, bumped only when the contract itself changes, not on every service release. **This shape still gets its own `VERSION`/`CHANGELOG.md`/`release.yml` trio, same as every other shape** — "versions independently" means its version *number* moves on its own schedule relative to the REST service, not that it skips the VERSION/CHANGELOG/release mechanism itself. Both `VERSION` (`0.0.1-SNAPSHOT` at generation time) and `pom.xml`/`build.gradle`'s `<version>` start at the same value; the drift-check CI below is a separate, additional check on top, not a substitute for VERSION/CHANGELOG.

**Do NOT put a running Swagger UI in this project** — `springdoc-openapi-ui`/`springdoc-openapi-starter-webmvc-ui` belongs in the **REST service** project (it serves live docs generated from the implemented, running API), not in the contract-only api-spec artifact. Including it here (as the reference project does) has no effect since this artifact never runs — treat that as a **reference-project quirk, not a convention to copy**.

---

## No Dockerfile, no docker-compose, no start script

This shape has no runtime — nothing to containerize or start.

## GitHub Actions CI — three workflow files

- `.github/workflows/ci.yml` — two jobs: `build` (`./mvnw -B verify` or `./gradlew build`, to confirm the artifact compiles and the openapi-generator plugin runs cleanly) and `publish` (deploys to GitHub Packages on push to `main`, `needs: build` — exact job shape is in `Java_Skeleton_Conventions.md`'s "Dependency management & GitHub Packages" section, copy it as-is, adjusting only the endpoint URL to this repo's own name). The `publish` job is what makes this artifact resolvable at all from the REST service's own CI build (see "GitHub Packages — publish config" above).
- `.github/workflows/release.yml` — manually-triggered release workflow, per `Java_Skeleton_Conventions.md`'s "Version & Release Management" section. Step 6 (build and publish the release artifact) for this shape: no Docker image — deploy the release-version Maven/Gradle artifact to GitHub Packages, identical in shape to the `publish` job above but running against the clean (non-`SNAPSHOT`) `VERSION` a human set before triggering:
```yaml
- name: Publish release artifact to GitHub Packages
  run: ./mvnw -B deploy -DskipTests
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
(Gradle equivalent: `./gradlew publish` with the same env.)
- `.github/workflows/codegen-drift.yml` — verifies the committed spec and its generated output haven't drifted apart:
```yaml
name: Codegen Drift Check
on:
  push:
    paths: ['src/main/resources/api-spec/**', 'pom.xml']
  pull_request:
    paths: ['src/main/resources/api-spec/**', 'pom.xml']
  workflow_dispatch:
jobs:
  drift-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '<javaVersion>'
          distribution: temurin
      - name: Regenerate from spec
        run: ./mvnw -B generate-sources
      - name: Fail if generated sources differ from what's committed
        run: git diff --exit-code -- target/generated-sources
```
Adjust the `git diff` path if generated sources aren't committed to version control (in that case the drift check is implicitly every CI build regenerating cleanly — still add the job, just drop the `git diff` step and note in a comment that generated sources are gitignored).

## README.md — Getting Started

Cover the build/verify command only — there's nothing to run.

---

## What the agent must NOT do (API spec shape)

In addition to the universal list in `Java_Skeleton_Conventions.md`:

- Do not put `springdoc-openapi-ui`/Swagger-UI-serving dependencies in this project — that belongs in the REST service (the thing that actually runs).
- Do not generate the API spec YAML with placeholder paths/schemas — use the real endpoints and resource fields from `architecture.md`, matching exactly what the REST-service skeleton implements.
- Do not generate a Dockerfile, docker-compose.yml, or start script — this shape has no runtime.
- Do not skip `VERSION`, `CHANGELOG.md`, or `.github/workflows/release.yml` — despite versioning independently from the REST service, this shape still gets all three, same as every other shape (see "Version & Release Management" in `Java_Skeleton_Conventions.md`).
- Do not skip the `<distributionManagement>`/`publish` CI job — the REST service's own CI build depends on this artifact being resolvable from GitHub Packages; skipping it silently breaks the sibling service's `build-and-test` job.
- Do not set `VERSION`/the `pom.xml`/`build.gradle` version to anything other than `0.0.1-SNAPSHOT` at generation time.
