# Java Skeleton — REST Service Shape

> Companion to [`Java_Skeleton_Conventions.md`](./Java_Skeleton_Conventions.md) — read that file first for "When this applies," the shape-decision table, the Reference Project rule, and universal conventions (build tool, Java version, no-Lombok, package root). This file covers only the REST service shape end-to-end; you should not need to open the Library or API Spec files while generating this shape.

**Reference:** cp-tenant-service

---

## Entity / DTO / Mapping / Layering

- **DTOs / value objects:** Java records — immutable, no Lombok.
- **Entities:** plain mutable classes (never records — JPA needs a no-arg constructor and mutable fields), never annotated with Lombok's `@Data`/`@ToString`/`@EqualsAndHashCode`. Primary key is a generated UUID string (`@UuidGenerator(style = UuidGenerator.Style.AUTO)`), `@Column(length = 36)`. Include `createdAt`/`updatedAt` (`OffsetDateTime`) with `@PrePersist`/`@PreUpdate` lifecycle callbacks — do not rely on `@CreationTimestamp` alone if the project also needs manual control.
- **Entity ↔ DTO mapping:** MapStruct (`@Mapper(componentModel = MappingConstants.ComponentModel.SPRING, unmappedTargetPolicy = ReportingPolicy.IGNORE)`), never hand-written mapping code. Partial-update mappers use `@BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)`.
- **Layering:** controller → service (interface + `Impl`) → repository, strictly one direction — controllers never touch repositories directly, services never depend on controllers.
- **Package sub-structure:** under the universal `{groupId}.{artifactId-without-dashes}` root: `controller`, `service` (+ `service.impl`), `repository`, `entity`, `dto`, `mapper`, `exception` (+ `exception.handler`), `config`. `{{SERVICE_PACKAGE_NAME}}` used throughout this file means exactly this root — the `groupId`/`artifactId` you were given for this repo in the generation prompt, not something to re-derive.

---

## Dependencies

- **Always (same set regardless of build tool):** `spring-boot-starter-web`, `spring-boot-starter-validation`, `spring-boot-starter-actuator` (see "Healthcheck" below), `spring-boot-starter-security` (see "Authentication" below), `mapstruct` + `mapstruct-processor` (annotation processor), `springdoc-openapi-starter-webmvc-ui` (serves live Swagger UI + `/v3/api-docs` from the actual running, implemented API — this is where Swagger UI belongs, not the api-spec artifact), `spring-boot-starter-test`, plus **the sibling API spec artifact** as a regular dependency (its real `groupId:artifactId:version`, read from that repo's own `pom.xml`/`build.gradle` once scaffolded — see `Java_Skeleton_API_Spec.md`). See "Resolving the sibling API spec dependency" below the Build file section for how this dependency is actually fetched in each build context (local, Docker, CI).
- **If this service owns a database** (see "Database — conditional" below): also `spring-boot-starter-data-jpa`, `liquibase-core`, `postgresql` (runtime), `h2` (test), `hibernate-jpamodelgen` (annotation processor).

**Do not include internal artifacts:** never add the reference project's internal `com.mycom.cp:cp-*` artifacts (`cp-security-configure`, `cp-scanner`, `cp-persistence-util`, `cp-rest-client`) as literal Maven/Gradle dependency coordinates — those only resolve against mycom's private Maven repo and would break the build for anyone else; the api-spec dependency is the one exception, since it's this devkit's own convention and will exist locally as a sibling repo. This still applies when `cp-security-configure` is the user-supplied reference project for a *different* repo's library shape (see `Java_Skeleton_Conventions.md`'s "Reference project" section) — follow its code structure/conventions, never its Maven coordinates. If the target project genuinely needs OAuth2 resource-server auth beyond the default baseline below, use plain `spring-security-oauth2-resource-server` + `spring-security-oauth2-jose`, not an internal wrapper.

**Database — conditional.** Not every REST service owns a database. Decide from `architecture.md` / this repo's purpose in `repo_structure.md`: if it describes persisted resources, a datastore, or CRUD over stored entities, this service has a database — default to **yes** for an ordinary REST service unless the architecture explicitly describes it as stateless, a pure proxy/gateway, or backed entirely by another service's API. When the service has no database: skip `spring-boot-starter-data-jpa`, `liquibase-core`, `postgresql`, `h2`, `hibernate-jpamodelgen` entirely; skip the Liquibase changelog and the `entity`/`repository` packages; skip `spring.datasource.*`/`spring.liquibase.*` properties. The vertical slice described below still applies to whatever domain objects the service manages — it just has no persistence layer (e.g. it may pass through the API spec's generated model types directly, or call another service).

**Authentication.** `spring-boot-starter-security` is included by default for every REST service skeleton — omit it only if `architecture.md` explicitly states the service has no authentication (e.g. an internal-only, unauthenticated health-check-style service). Baseline config: a `SecurityConfig` (`@Configuration` + `@EnableWebSecurity`) that permits `/actuator/health/**` and the Swagger UI/OpenAPI docs paths unauthenticated, and requires authentication on everything else. If `architecture.md` names a specific auth mechanism (JWT, OAuth2 resource server, session-based), configure that; if it doesn't say, default to `spring-security-oauth2-resource-server` + `spring-security-oauth2-jose` (JWT bearer-token validation) as the most common REST-API baseline, and note in the agent's report that the exact issuer/JWKS config is a placeholder the user must fill in for their real identity provider.

**Healthcheck (Kubernetes-style).** Every REST service skeleton exposes Kubernetes-style liveness/readiness probes via `spring-boot-starter-actuator`, not just a single flat `/actuator/health`:
```properties
management.endpoint.health.probes.enabled=true
management.health.livenessState.enabled=true
management.health.readinessState.enabled=true
management.endpoint.health.show-details=when-authorized
```
This exposes `/actuator/health/liveness` and `/actuator/health/readiness` in addition to `/actuator/health`. Wire both into the generated Docker artifacts (see "Docker" below): the `Dockerfile`'s `HEALTHCHECK` instruction and the `docker-compose.yml` app service's own `healthcheck:` block both target `/actuator/health/liveness`.

---

## Build file

**If Maven — `pom.xml`:** `spring-boot-starter-parent` as `<parent>` (pins Spring Boot's dependency-management BOM automatically); the annotation processors (`mapstruct-processor` always, plus `hibernate-jpamodelgen` if this service owns a database) go in `maven-compiler-plugin`'s `<annotationProcessorPaths>`; `spring-boot-maven-plugin` for the executable jar. **Every `annotationProcessorPaths` entry needs its own explicit `<version>`** — unlike regular `<dependencies>`, these entries don't reliably inherit a version from `spring-boot-starter-parent`'s BOM, and Maven fails the compile step outright with "Cannot find version for annotation processor path" if one is missing. `mapstruct-processor` already gets this right via `${mapstruct.version}`; give `hibernate-jpamodelgen` the same treatment via `${hibernate.version}` (a property Spring Boot's BOM exposes for exactly this), e.g.:
```xml
<path>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-jpamodelgen</artifactId>
    <version>${hibernate.version}</version>
</path>
```

**If Gradle — `build.gradle` (or `.kts`):** apply plugins `java`, `org.springframework.boot`, and `io.spring.dependency-management` (the last one pulls in Spring Boot's BOM the same way `spring-boot-starter-parent` does in Maven — without it, dependency versions must be pinned manually). Runtime/test deps use the `runtimeOnly` / `testImplementation` configurations (Gradle's equivalent of Maven's `runtime`/`test` scope). Annotation processors go in the `annotationProcessor` configuration, e.g.:
```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '<springBootVersion>'
    id 'io.spring.dependency-management' version '1.1.x'
}
dependencies {
    // always
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'org.springframework.security:spring-security-oauth2-resource-server'
    implementation 'org.springframework.security:spring-security-oauth2-jose'
    implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:<springdocVersion>'
    implementation 'org.mapstruct:mapstruct:1.6.3'
    annotationProcessor 'org.mapstruct:mapstruct-processor:1.6.3'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'

    // only if this service owns a database — see "Database — conditional" above
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.liquibase:liquibase-core'
    runtimeOnly 'org.postgresql:postgresql'
    testRuntimeOnly 'com.h2database:h2'
    annotationProcessor 'org.hibernate.orm:hibernate-jpamodelgen'
}
```

**Application class:** standard `@SpringBootApplication` + `SpringApplication.run(...)`, named `{ProjectName}Application`.

**GitHub Packages — publish config:** add the `<distributionManagement>` block (Maven) / `maven-publish` config (Gradle) described in `Java_Skeleton_Conventions.md`'s "Dependency management & GitHub Packages" section, pointing at this repo's own GitHub Packages endpoint. Same for the CI `publish` job described there.

**Resolving the sibling API spec dependency.** There are two build contexts, and they resolve the sibling artifact differently — no branching logic needed in the `pom.xml`/`build.gradle` itself, since Maven/Gradle always check the local dependency cache before any remote repository:
- **Local/Docker builds** (`docker compose up --build`, or a dev running the Dockerfile's build stage manually): the Dockerfile's build stage already `COPY`s the sibling `<repo-name>-api-spec` folder and runs `install`/`publishToMavenLocal` on it first (see "Dockerfile" below) — this populates the local cache directly, so the main build never needs network access or credentials to resolve it. This keeps working exactly as before; nothing about it changes.
- **Any build context without the sibling folder present** (most notably CI's `build-and-test` job, which only checks out this single repo — the sibling-folder trick is Docker-build-specific and CI's direct `mvn verify`/`gradle build` never sees it): add a `<repositories>` entry (Maven) / repository block (Gradle) pointing at the sibling's own GitHub Packages endpoint, `https://maven.pkg.github.com/<owner>/<repo-name>-api-spec`, with the same `<id>github</id>` used everywhere else (see `Java_Skeleton_Conventions.md`). Since the api-spec repo publishes to GitHub Packages on every push to main, this resolves cleanly as long as the api-spec repo has been scaffolded and pushed at least once already — which Stage 4's repo ordering already guarantees (the api-spec repo is always scaffolded, and Stage 5 pushes it, before the REST service's turn — see "Ordering matters" in `Build_Software_Workflow.md`). **First-run note:** if both repos' CI happen to run for the first time close together, the REST service's `build-and-test` can fail with "could not find artifact" if it runs before the api-spec's `publish` job finishes — this is a one-time bootstrap race, not a real problem; a re-run once the sibling's publish succeeds resolves it.

  This also means `build-and-test`'s CI job needs the same `actions/setup-java@v4` `server-id: github` wiring as the publish job, plus `permissions: packages: read` — without this, CI's own test/build job has no way to resolve the sibling dependency at all (this was a latent gap before GitHub Packages was configured: the sibling-folder trick only ever worked inside Docker, never in CI's direct Maven/Gradle invocation).

  **A PAT is required here — this is not the same "no PAT needed" case as the `publish` job.** `Java_Skeleton_Conventions.md`'s "GITHUB_TOKEN is the Actions-provided token — no PAT or extra secret needs creating" statement is true only for a repo publishing **its own** package. Reading a *different* repo's private package is a separate operation with its own access rules: on a personal (non-org) GitHub account, the automatic `GITHUB_TOKEN` is scoped strictly to the repository the workflow runs in and cannot read another repo's private package under any circumstances — there is no equivalent of an org's per-package "Manage Actions access" setting for personal accounts. Concretely, this means:
  - A PAT (classic, `read:packages` scope) stored as a repo secret (e.g. `CROSS_REPO_TOKEN`) is required for `build-and-test` to resolve the sibling artifact, on a personal account. For an org-owned repo, the alternative is granting the consuming repo explicit Actions access on the api-spec's package (its Settings → Manage Actions access) instead of a PAT — but that's also a manual step, never automatic.
  - Since `<repositories>` and `<distributionManagement>` share the same `<id>github</id>` server credential, **this repo's own `publish` job also needs that same PAT** (not the plain `secrets.GITHUB_TOKEN`) if it runs `deploy`/`publish` — `deploy` recompiles from scratch first, which means resolving the sibling dependency before it can push this repo's own artifact. So the PAT needs **both** `read:packages` (sibling) and `write:packages` (this repo's own package) scope.
  - This is a manual, external setup step the devkit cannot perform itself (creating a PAT and adding it as a secret requires GitHub UI access) — the generation agent should call this out explicitly in its completion report so the user isn't surprised when `build-and-test` fails on the first push with "could not find artifact" for a reason unrelated to the bootstrap-race note above.

```xml
<repositories>
    <repository>
        <id>github</id>
        <name>GitHub Packages - <repo-name>-api-spec</name>
        <url>https://maven.pkg.github.com/<owner>/<repo-name>-api-spec</url>
    </repository>
</repositories>
```

---

## Vertical slice

**Request/response types come from the API spec artifact, never hand-written here.** `dto/` in this project is only for types that are *not* part of the public contract (internal search/filter parameter objects, etc. — still records). Every request/response/resource type used at the controller boundary is the generated model class from `{{SERVICE_PACKAGE_NAME}}.api.spec.model` (the sibling api-spec artifact's output) — this is what keeps the contract and the implementation from drifting apart.

**Per real domain entity identified from `architecture.md`** (not one generic placeholder — generate the project's actual first entity/entities, e.g. for a tenant-management service that's `Tenant`; for an order service that's `Order`), generate the full vertical slice:
- `entity/{Name}Entity.java` — plain class, conventions above.
- `mapper/{Name}Mapper.java` — MapStruct interface mapping `{Name}Entity` to/from the **generated** `{{SERVICE_PACKAGE_NAME}}.api.spec.model` request/response classes (e.g. `from{X}Request(Create{Name}Request)`, `to{Name}(...)`, `update{Name}Entity(Update{Name}Request, @MappingTarget ...)`) — never a hand-written `dto/` class as the mapping target.
- `repository/{Name}Repository.java` — `extends JpaRepository<{Name}Entity, String>`.
- `service/{Name}Service.java` (interface) + `service/impl/{Name}ServiceImpl.java` — method signatures use the generated model types (matching the reference project's `TenantService`/`TenantServiceImpl`, which return/accept `com.mycom.cp.tenant.service.api.spec.model.Tenant` etc. directly, not a separate hand-rolled response type); constructor injection, `@Transactional` at class level, `@Transactional(readOnly = true)` on read methods.
- `controller/{Name}Controller.java` — `@RestController implements {Name}sApi` (the generated interface from the api-spec artifact) rather than declaring its own `@RequestMapping` methods from scratch; `@Override` each generated method, delegate to the service. Constructor injection.
- `exception/ResourceNotFoundException.java` (or project-specific name) + `exception/handler/GlobalExceptionHandler.java` — `@RestControllerAdvice`, handles not-found → 404, `MethodArgumentNotValidException` → 400 with field errors joined, generic `Exception` → 500 with no internal detail leaked.

  > The reference project's exception handler was a near-empty stub (`@ControllerAdvice` class with a logger and nothing else) — that is a **gap in the reference, not a convention to copy**. Generate a handler that actually handles the exceptions above.

**Config — `application.properties` + profile overlays** (`application-{env}.properties`, e.g. `dev`, `test`): `spring.application.name`, `spring.datasource.*` (Postgres for main/dev, H2 for test), `spring.jpa.hibernate.ddl-auto=validate` (schema is Liquibase-owned, Hibernate never auto-generates DDL outside test), `spring.liquibase.change-log=classpath:db/changelog/changelog.xml`. Never hardcode real credentials — use `${ENV_VAR:default}` placeholders as the reference project does for local dev only.

**Liquibase:** master `db/changelog/changelog.xml` that only `<include>`s versioned changelog files (`db/changelog/{version}/changelog-{version}.xml`); first changeset creates the table for the first real entity, columns matching the entity's fields exactly (including `created_at`/`updated_at` as `TIMESTAMP WITH TIME ZONE NOT NULL`, id as `VARCHAR(36) PRIMARY KEY`).

**Tests:** one Spring context-load test (`{ProjectName}ApplicationTests`) at minimum; `src/test/resources/application.properties` pointing at H2.

---

## Docker

Generated alongside the code in the same skeleton-generation pass — not a separate step, not optional, **except when the Docker Consultation in `Build_Software_Workflow.md`'s Stage 4 Entry resolved to skip Docker for this build** (see [`Docker_Conventions.md`](../docker/Docker_Conventions.md), which owns the consultation flow and the file-layout locations referenced throughout this section — read it first). Use the **real** entity/endpoint/env-var names already decided while generating the code above; never placeholders.

### Dockerfile

Lives at `<repo-name>/docker/Dockerfile` — under the `docker/` subfolder per `Docker_Conventions.md`'s File Layout, not at the repo root.

**Sibling api-spec dependency note:** every Java REST service under this devkit has a companion `<repo-name>-api-spec` artifact that is **not published anywhere** — it only exists as a sibling folder on disk (e.g. `../<repo-name>-api-spec` relative to the service repo). A Docker build whose context is just the service repo can't see it. So the build stage installs the sibling module first, and the **build context must be the parent directory that contains both sibling repos**, not the service repo itself:

```dockerfile
# ---- build stage ----
FROM eclipse-temurin:<javaVersion>-jdk AS build
WORKDIR /workspace
COPY <repo-name>-api-spec ./<repo-name>-api-spec
COPY <repo-name> ./<repo-name>
RUN cd <repo-name>-api-spec && ./mvnw -B -q install -DskipTests
RUN cd <repo-name> && ./mvnw -B -q package -DskipTests
# (Gradle equivalent: same two-step COPY + ./gradlew publishToMavenLocal / ./gradlew build -x test)

# ---- runtime stage ----
FROM eclipse-temurin:<javaVersion>-jre
WORKDIR /app
RUN useradd --system --create-home appuser
COPY --from=build /workspace/<repo-name>/target/*.jar app.jar
USER appuser
EXPOSE <serverPort>
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD wget -qO- http://localhost:<serverPort>/actuator/health/liveness || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
```
The runtime base image (`eclipse-temurin:*-jre`) doesn't include `wget` by default — install it (or use `curl` if preferred) in the runtime stage before the `HEALTHCHECK` line, e.g. `RUN apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/*`.
This `Dockerfile` still lives at `<repo-name>/docker/Dockerfile` — only the **build context** used to invoke it changes (see compose below). COPY paths inside the Dockerfile are relative to the build context, not to the Dockerfile's own location, so the two-repo `COPY` lines above are unaffected by which subfolder the Dockerfile itself sits in. If a REST service shape is ever generated without a sibling api-spec dependency (not the current devkit convention, but keep the logic general), skip the two-repo `COPY`/install steps and build directly like a normal single-repo Dockerfile (`COPY . .` from a `context: .`).

Use the Maven/Gradle wrapper (`mvnw`/`gradlew`) already committed by the skeleton in each repo, never a bare `mvn`/`gradle` the image can't resolve. `<serverPort>` is `server.port` from `application.properties` if set, else Spring Boot's default `8080`. Never bake real secrets into the image — runtime config comes from environment variables (see compose below), matching the `${ENV_VAR:default}` placeholders already used in `application.properties`.

### docker-compose.yml

One compose file at `<repo-name>/docker/sandbox/docker-compose.yml` (per `Docker_Conventions.md`'s File Layout, not the repo root) that brings up the service plus every piece of infrastructure the skeleton's `application.properties` actually references by env var — read that file (not `architecture.md` in isolation) to get the exact set: always a database if `spring.datasource.*` is present (Postgres, matching the `postgresql` dependency), plus any additional infra named in `architecture.md`'s tech-stack decision that the properties file also wires up via env var (e.g. an object-store service if `minio.*`-style properties exist, a cache if `redis.*`-style properties exist). Do not invent infra the properties file doesn't reference.

Because the Dockerfile's build context must be the **parent** directory containing both this repo and its sibling api-spec repo (see above), and the compose file itself now sits two levels deeper than the repo root (`docker/sandbox/`), `context` needs three `..` segments instead of one to reach that same parent directory — run via `cd <repo-name>/docker/sandbox && docker compose up --build`:

```yaml
services:
  <service-name>:
    build:
      context: ../../..
      dockerfile: <repo-name>/docker/Dockerfile
    ports:
      - "<serverPort>:<serverPort>"
    environment:
      DB_URL: jdbc:postgresql://db:5432/<db-name>
      DB_USERNAME: <db-name>
      DB_PASSWORD: <db-name>
      # ...one env var per ${ENV_VAR:default} placeholder actually present in application.properties
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:<serverPort>/actuator/health/liveness"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: <db-name>
      POSTGRES_USER: <db-name>
      POSTGRES_PASSWORD: <db-name>
    volumes:
      - <service-name>-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U <db-name>"]
      interval: 5s
      timeout: 5s
      retries: 10
volumes:
  <service-name>-db-data:
```
Dev-only credentials only (matching the defaults already in `application.properties` / `application-dev.properties`), never anything that looks like a real secret. Add one extra service block (with its own named volume if it's stateful) per additional infra dependency found in the properties file, following the same pattern.

### Single service without a database (e.g. a UI/SSR or processing service with no `spring.datasource.*`)

No docker-compose.yml — there's no multi-container orchestration to do. Two run paths still apply, side by side, per `Docker_Conventions.md`:

**Plain (no Docker):** `start.sh` (and `start.ps1` if the target platform is Windows-first) at the repo root — unaffected by anything below. Build once if needed, then run the app in the foreground:
```sh
#!/usr/bin/env sh
set -e
./mvnw -B -q package -DskipTests
java -jar target/*.jar
```

**Docker-based:** `docker/sandbox/run.sh` (and `run.ps1`) — build the image and run it in the foreground, using the same parent-directory build context as the compose case above (three levels up from `docker/sandbox/`, to see the sibling api-spec repo) and the same env vars a compose file's `environment:` block would set:
```sh
#!/usr/bin/env sh
set -e
cd "$(dirname "$0")/../../.."
docker build -f <repo-name>/docker/Dockerfile -t <service-name>:local .
docker run --rm -p <serverPort>:<serverPort> \
  # one -e ENV_VAR=default per ${ENV_VAR:default} placeholder actually present in application.properties
  <service-name>:local
```
The Dockerfile's `HEALTHCHECK` instruction (see above) still applies unchanged in both cases — it targets the app's own `/actuator/health/liveness`, not a database.

---

## GitHub Actions CI — `.github/workflows/ci.yml`

Four jobs:
- `build-and-test` — `./mvnw -B verify` (or `./gradlew build`): compiles, runs unit tests, packages. This is both the "build" and "unit test" requirement — Maven/Gradle's default lifecycle already runs unit tests as part of `verify`/`build`, so splitting them into two separate mvn/gradle invocations would just recompile twice for no benefit. **Needs `permissions: packages: read`** and the same `actions/setup-java@v4` `server-id: github` wiring as the publish job below — this is what lets it resolve the sibling API spec dependency from GitHub Packages (see "Resolving the sibling API spec dependency" above); without it this job cannot resolve that dependency at all.
- `lint` — runs `./mvnw -B spotless:check` (or Gradle Spotless equivalent). Add the `spotless-maven-plugin` (or `com.diffplug.spotless` Gradle plugin) to the build file with a standard Java formatter (`googleJavaFormat` or `palantirJavaFormat`) if the skeleton doesn't already declare a linter — this is what makes the CI job non-trivial rather than a no-op. **JDK-formatter compatibility check:** `palantirJavaFormat` (and to a lesser extent `googleJavaFormat`) hooks into javac's internal APIs, which have broken before on very new JDK releases — as of this writing, `spotless-maven-plugin` 2.44.3's bundled `palantirJavaFormat` throws `NoSuchMethodError` against JDK 25. If the universal convention's default Java version is a recent release, verify the formatter actually runs before finalizing the skeleton (or note the risk in the agent's report). If it's broken, don't downgrade the whole project's Java version to work around a linter — instead pin **only** the `lint` job's `actions/setup-java` step to an older stable LTS (e.g. `21`) while every other job stays on the real target version; Spotless only checks source-text formatting, not runtime bytecode compatibility, so this is safe unless the source uses preview syntax newer than the pinned version.
- `automation-test` — **stub job, depends on `build-and-test`.** No real Postman/Newman-style API test suite exists yet at skeleton-generation time (there's no story-authored collection to run). Generate the job shell (checkout, `depends_on: build-and-test` via `needs:`) with a single step that echoes `"TODO: no automation test suite yet — add Newman/Postman collections under tests/automation/ and replace this step (see codegen-drift.yml pattern in the sibling API-spec repo for the general CI shape to follow)."` and exits 0. The job exists from day one so the pipeline shape is correct; a later story replaces the stub with real collections, not a whole new job.
- `publish` — deploys this repo's own artifact to GitHub Packages on push to `main`. Exact job shape (trigger condition, `permissions`, `setup-java` wiring, `deploy` step) is in `Java_Skeleton_Conventions.md`'s "Dependency management & GitHub Packages" section — copy it as-is, adjusting only the endpoint URL to this repo's own name.

---

## README.md — Getting Started

Per `Docker_Conventions.md`, this repo also gets a `docker/README.md` documenting the Docker artifacts in detail — the repo-root `README.md`'s `{{GETTING_STARTED}}` content stays short and points to it rather than duplicating it: the plain-JVM path (`start.sh`, or for the with-database shape the fact that Docker is the only way to get the database dependency running locally), a one-line pointer to `docker/README.md` for the containerized run, the port(s) the service listens on, and how to confirm it's up (`curl http://localhost:<serverPort>/actuator/health/liveness`). `docker/README.md` itself carries the exact `cd <repo-name>/docker/sandbox && docker compose up --build` (or `run.sh`) command and the full table of environment variables a real deployment must set (name, purpose, dev default — pulled straight from the `${ENV_VAR:default}` placeholders in `application.properties`).

---

## Release files — VERSION, CHANGELOG, release.yml

`VERSION` and `CHANGELOG.md` already exist by the time this generation step runs — the mechanical scaffold step creates them universally, for every repo regardless of language (see `.claude/agents/working/skeletons/shared/Version_Release_Conventions.md`). Do not recreate them; only `.github/workflows/release.yml` is generated here. `pom.xml`/`build.gradle`'s own `<version>` matches the existing `VERSION` value (`0.0.1-SNAPSHOT`), not a separate clean semver — see "Dependency management & GitHub Packages" for why the build coordinate needs to stay `-SNAPSHOT`.

**`release.yml` step 6 for this shape (build and publish the release artifact):** build the Docker image from the repo's own `Dockerfile`, using the exact same two-repo build context the local/dev build needs (see "Dockerfile" above — this Dockerfile always `COPY`s a sibling `<repo-name>-api-spec` folder, never conditionally). Get both repos into the workflow's workspace as siblings with **two separate `actions/checkout` steps at named paths** (no `..` path traversal needed — both land under the same `$GITHUB_WORKSPACE`, which then *is* the parent directory the Dockerfile expects):
```yaml
- name: Checkout this repo
  uses: actions/checkout@v4
  with:
    path: <repo-name>

- name: Checkout sibling API spec repo
  uses: actions/checkout@v4
  with:
    repository: <owner>/<repo-name>-api-spec
    path: <repo-name>-api-spec
    token: ${{ secrets.GITHUB_TOKEN }}

- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build and push release image
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./<repo-name>/docker/Dockerfile
    push: true
    tags: ghcr.io/<owner>/<repo-name>:<version>
```
Because both repos were checked out to named paths (`<repo-name>`, `<repo-name>-api-spec`) directly under `$GITHUB_WORKSPACE` rather than the default single-checkout root, the build `context: .` here already **is** that shared parent directory — the Dockerfile's `COPY <repo-name>-api-spec ./<repo-name>-api-spec` / `COPY <repo-name> ./<repo-name>` lines resolve exactly as they do locally, unmodified. This differs from `build-and-test`'s dependency resolution (which uses GitHub Packages, not a sibling checkout — see "Resolving the sibling API spec dependency" above): `release.yml` runs rarely and by hand, so paying for a full second checkout + real Dockerfile build here is fine, and it guarantees the released image is built identically to what a developer tests locally.

---

## What the agent must NOT do (REST service shape)

In addition to the universal list in `Java_Skeleton_Conventions.md`:

- Do not generate a generic "Example"/"Item"/"Foo" placeholder entity when `architecture.md` already names real domain entities — use the real names.
- Do not make entities records, do not hand-write entity↔DTO mapping.
- Do not hand-write request/response DTOs directly — those come from the sibling API spec artifact's generated model classes. If the sibling api-spec repo doesn't exist yet when generating the REST service, stop and report the blocker rather than inventing local DTOs as a workaround.
- Do not add a docker-compose service for infrastructure `application.properties` doesn't actually reference by env var — the properties file is the source of truth for what the service needs at runtime, not a guess from `architecture.md` alone.
- Do not bake real credentials into a Dockerfile or docker-compose.yml — dev-only defaults matching `application.properties`'s own `${ENV_VAR:default}` placeholders only.
- Do not write a real Newman/Postman automation-test suite into the `automation-test` CI job — no test collections exist yet at skeleton-generation time; the stub-and-TODO job is the correct output, not an invented fake suite.
- Do not omit `spring-boot-starter-actuator`/the liveness+readiness healthcheck config, and do not omit `spring-boot-starter-security` unless `architecture.md` explicitly states the service has no authentication.
- Do not skip `.github/workflows/release.yml` — see "Version & Release Management" in `Java_Skeleton_Conventions.md`. Do not recreate `VERSION`/`CHANGELOG.md` — they already exist (mechanical scaffold step).
- Do not skip the `<distributionManagement>`/`publish` CI job, or the `<repositories>` entry + `permissions: packages: read` wiring on `build-and-test` — without the latter, CI's own build job cannot resolve the sibling API spec dependency at all (the Docker sibling-folder trick doesn't apply there).
- Do not set the `pom.xml`/`build.gradle` version to anything other than the existing `VERSION` file's value (`0.0.1-SNAPSHOT`) at generation time — a plain release version would make the second CI publish onward fail (GitHub Packages rejects republishing a non-`SNAPSHOT` version), and would also fail `release.yml`'s own guard against releasing an already-released version.
- Do not build the `release.yml` Docker image with `context: .` against a single-repo checkout — it will fail to find the sibling `<repo-name>-api-spec` folder. Use the two-named-path checkout pattern described above.
- Do not leave an `annotationProcessorPaths` entry (`hibernate-jpamodelgen` in particular) without an explicit `<version>` — it doesn't reliably inherit one from `spring-boot-starter-parent`'s BOM and fails the compile step outright.
- Do not report the GitHub Packages sibling-dependency wiring as fully self-sufficient — the agent's completion report must flag that a PAT (with `read:packages` + `write:packages` scope) needs to be created and added as a repo secret before CI will actually pass; this is a manual step outside the agent's own reach.
