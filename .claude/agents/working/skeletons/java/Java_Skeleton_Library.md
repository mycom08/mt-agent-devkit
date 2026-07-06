# Java Skeleton — Pure Library Shape

> Companion to [`Java_Skeleton_Conventions.md`](./Java_Skeleton_Conventions.md) — read that file first for "When this applies," the shape-decision table, the Reference Project rule, and universal conventions (build tool, Java version, no-Lombok, package root). This file covers only the pure-library shape end-to-end; you should not need to open the REST Service or API Spec files while generating this shape.

**Reference:** cp-security-configure

---

## Core rule (both build tools)

**No Spring Boot "app" plugin/parent.** A library must not force its packaging/version choices onto consumers. Spring dependencies the library integrates with (`spring-context`, `spring-boot-starter-web`, `spring-boot-autoconfigure`) are **compile-time-only, not bundled** — the consuming application supplies the real versions at runtime. Only include these if the library actually needs Spring; a framework-agnostic library should have zero Spring dependency at all.

## Build file

**If Maven — `pom.xml`:** **no** `spring-boot-starter-parent` — plain `<packaging>jar</packaging>`, explicit `<properties>` for Java version, dependency versions pinned individually (or via a small `<dependencyManagement>` block for test deps like the JUnit BOM). Spring dependencies use `<scope>provided</scope>` (compile-time only, never bundled into the published jar, never pulled transitively into consumers).

**If Gradle — `build.gradle`:** apply the `java-library` plugin (**not** `org.springframework.boot`, **not** `application`) — `java-library` is the Gradle plugin built specifically for this case, distinguishing `api` (exposed to consumers transitively) from `implementation` (internal only). Spring dependencies map to Maven's `provided` scope via the **`compileOnly`** configuration (compile-time only, not in the published artifact, not exposed to consumers); if tests also need them, add matching `testImplementation` entries since `compileOnly` does not extend to the test source set automatically:
```groovy
plugins {
    id 'java-library'
}
dependencies {
    compileOnly 'org.springframework:spring-context:<springVersion>'
    compileOnly 'org.springframework.boot:spring-boot-starter-web:<springBootVersion>'
    compileOnly 'org.springframework.boot:spring-boot-autoconfigure:<springBootVersion>'
    testImplementation 'org.springframework.boot:spring-boot-starter-web:<springBootVersion>'

    testImplementation platform('org.junit:junit-bom:5.11.0')
    testImplementation 'org.junit.jupiter:junit-jupiter-api'
    testImplementation 'org.junit.jupiter:junit-jupiter-params'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
```

**If the library provides Spring auto-configuration** (optional — only if the library needs to register beans automatically in a consumer's Spring context): a `@Configuration` class, typically gated by `@ConditionalOnProperty(prefix = "{library-prefix}.autoconfigure", name = "enabled", havingValue = "true", matchIfMissing = true)` so consumers can opt out; registered via `src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (one fully-qualified class name per line) — **not** the legacy `spring.factories` mechanism.

**Package sub-structure:** under the universal `{groupId}.{artifactId}` root, sub-packaged by the library's actual concern (not a fixed controller/service/repository layering — a library's internal shape follows its own domain, e.g. `config/`, and whatever core abstraction the library exists to provide). Do not force REST-service layering onto a library that isn't one.

**Tests:** plain JUnit 5 (`junit-jupiter-api`, `junit-jupiter-params`), no Spring context needed unless testing the auto-configuration itself (in which case `spring-boot-starter-test` as a test-scope dependency is fine).

**GitHub Packages — publish config:** add the `<distributionManagement>` block (Maven) / `maven-publish` config (Gradle) described in `Java_Skeleton_Conventions.md`'s "Dependency management & GitHub Packages" section, pointing at this repo's own GitHub Packages endpoint. This is the release/distribution channel for the library jar — it does not affect local `mvn package`/`gradle build`, which never run `deploy`/`publish`.

---

## README.md

Every library skeleton gets one — what it does, how to add it as a dependency (including the GitHub Packages coordinates, since that's where consumers actually resolve this artifact from), minimal usage example.

## GitHub Actions CI — `.github/workflows/ci.yml`

Two jobs — `build-and-test` (`./mvnw -B verify` or `./gradlew build`; no lint/automation-test jobs unless the library already declares a linter) and `publish` (deploys to GitHub Packages on push to `main` — exact job shape is in `Java_Skeleton_Conventions.md`'s "Dependency management & GitHub Packages" section, copy it as-is, adjusting only the endpoint URL to this repo's own name).

---

## Release files — VERSION, CHANGELOG, release.yml

`VERSION` and `CHANGELOG.md` already exist by the time this generation step runs — the mechanical scaffold step creates them universally, for every repo regardless of language (see `.claude/agents/working/skeletons/shared/Version_Release_Conventions.md`). Do not recreate them; only `.github/workflows/release.yml` is generated here. `pom.xml`/`build.gradle`'s own `<version>` matches the existing `VERSION` value (`0.0.1-SNAPSHOT`), not a separate clean semver.

**`release.yml` step 6 for this shape (build and publish the release artifact):** no Docker image — deploy the release-version Maven/Gradle artifact directly to GitHub Packages, reusing the same `<distributionManagement>`/`maven-publish` config from "Dependency management & GitHub Packages" (the `VERSION`-stripped-to-clean value is what ends up in `pom.xml`/`build.gradle` at this point, so the same `deploy`/`publish` command now pushes a real, non-`SNAPSHOT` release instead of a snapshot):
```yaml
- name: Publish release artifact to GitHub Packages
  run: ./mvnw -B deploy -DskipTests
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
(Gradle equivalent: `./gradlew publish` with the same env.) This is the same `actions/setup-java@v4` `server-id: github` job wiring as the continuous `publish` job — no new credentials setup needed.

---

## What the agent must NOT do (library shape)

In addition to the universal list in `Java_Skeleton_Conventions.md`:

- Do not apply the Spring Boot Gradle plugin (`org.springframework.boot`) or `spring-boot-starter-parent` — those are for runnable apps only; libraries use `java-library` (Gradle) or a plain `<packaging>jar</packaging>` POM with no Spring Boot parent (Maven).
- Do not force REST-service layering (controller/service/repository) onto a library that isn't one.
- Do not generate a Dockerfile, docker-compose.yml, or start script — a library has no standalone runtime.
- Do not skip `.github/workflows/release.yml` — see "Version & Release Management" in `Java_Skeleton_Conventions.md`. Do not recreate `VERSION`/`CHANGELOG.md` — they already exist (mechanical scaffold step).
- Do not skip the `<distributionManagement>`/`publish` CI job — "release artifacts use GitHub Package" is a fixed devkit convention, not optional.
- Do not set the `pom.xml`/`build.gradle` version to anything other than the existing `VERSION` file's value (`0.0.1-SNAPSHOT`) at generation time — a plain release version would make the second CI publish onward fail, and would also fail `release.yml`'s own guard against releasing an already-released version.
