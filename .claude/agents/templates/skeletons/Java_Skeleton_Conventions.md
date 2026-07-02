# Java Skeleton Conventions

> Read by the Stage 4 skeleton-generation agent (`Build_Software_Workflow.md`), never copied verbatim. This document describes **conventions and illustrative shapes**, not literal files — the agent generates real, project-specific code that follows these patterns, using the actual domain from `architecture.md` (real entity/resource names, real endpoints), not a generic placeholder like "Example".
>
> Distilled from three real internal reference projects, with all proprietary/internal dependencies stripped to public Maven Central equivalents so the result builds for any devkit user.

---

## When this applies

Only for repos whose tech stack (from `repo_structure.md` / `architecture.md`) is Java-based, **and** whose local path has no `pom.xml`, `build.gradle`, or `build.gradle.kts`, and no `src/` directory yet (see Stage 4 for the exact check). If any exists, skip skeleton generation entirely — never scaffold over or alongside existing code.

Three shapes, chosen by the agent from the repo's stated purpose in `repo_structure.md`:

| Shape | When | Reference |
|---|---|---|
| **API spec** | Repo purpose describes the OpenAPI/Swagger contract for a REST service (no runtime, no database — just a compiled contract artifact) | cp-tenant-service-api-spec |
| **REST service** | Repo purpose describes a backend/API/service (runs standalone, owns a database, exposes HTTP endpoints) | cp-tenant-service |
| **Pure library** | Repo purpose describes a reusable library/SDK/client consumed by other Java projects (no standalone runtime, no database of its own) | cp-rest-client |

**Every Java REST service always has a companion API spec repo — this is a fixed devkit convention, not conditional on `architecture.md`.** `Build_Software_Workflow.md` Stage 2 adds the companion `<repo-name>-api-spec` repo to `repo_structure.md` automatically whenever a Java REST service is planned, ordered *before* its service in the repo table so Stage 4 scaffolds the contract first — the REST service's skeleton depends on it existing.

---

## Shared conventions (all three shapes, where applicable — the API spec shape has no entities/DTOs/layering of its own, see below)

- **Build tool:** Maven (`pom.xml`) or Gradle (`build.gradle` / `build.gradle.kts`) — whichever `architecture.md`'s tech-stack decision names. If unspecified, default to Maven. The two build tools are **structurally equivalent conventions** below, just expressed differently — same dependencies, same annotation processors, same layering; only the manifest syntax and dependency-scope keywords differ (Maven `scope` ↔ Gradle `configuration`). Never mix build tools in one repo, and never generate both a `pom.xml` and a `build.gradle` in the same skeleton.
- **Java version / Spring Boot version:** pull the exact versions from `architecture.md`'s tech-stack decision if it names them; otherwise default to the latest stable LTS Java and latest stable Spring Boot GA at generation time.
- **DTOs / value objects:** Java records — immutable, no Lombok.
- **Entities:** plain mutable classes (never records — JPA needs a no-arg constructor and mutable fields), never annotated with Lombok's `@Data`/`@ToString`/`@EqualsAndHashCode`. Primary key is a generated UUID string (`@UuidGenerator(style = UuidGenerator.Style.AUTO)`), `@Column(length = 36)`. Include `createdAt`/`updatedAt` (`OffsetDateTime`) with `@PrePersist`/`@PreUpdate` lifecycle callbacks — do not rely on `@CreationTimestamp` alone if the project also needs manual control.
- **Entity ↔ DTO mapping:** MapStruct (`@Mapper(componentModel = MappingConstants.ComponentModel.SPRING, unmappedTargetPolicy = ReportingPolicy.IGNORE)`), never hand-written mapping code. Partial-update mappers use `@BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)`.
- **No Lombok anywhere** — records cover the immutable case, entities are hand-written plain classes; this also sidesteps the Lombok↔MapStruct annotation-processor ordering issue entirely.
- **Layering:** controller → service (interface + `Impl`) → repository, strictly one direction — controllers never touch repositories directly, services never depend on controllers.
- **Package root:** `{groupId}.{artifactId-without-dashes}`, sub-packaged by layer: `controller`, `service` (+ `service.impl`), `repository`, `entity`, `dto`, `mapper`, `exception` (+ `exception.handler`), `config`.

---

## API spec shape (reference: cp-tenant-service-api-spec)

**Purpose:** a **contract-first** OpenAPI/Swagger YAML file, compiled into Java API interfaces + model classes via `openapi-generator` at build time. It is its own Maven/Gradle artifact — no `@SpringBootApplication`, no database, no runtime. The companion REST service depends on it and implements the generated interface(s), rather than hand-writing controller method signatures or request/response DTOs.

**File:** one hand-written OpenAPI 3.x YAML file per service, e.g. `src/main/resources/api-spec/{service-name}-api-spec.yaml` (a resources path, not `src/main/java` — despite the reference project placing it under `src/main/java/api-spec/`, YAML belongs under `src/main/resources`; that placement is a **reference-project quirk, not a convention to copy**). Content: standard OpenAPI 3.x — `info`, `tags`, `paths` (one entry per real endpoint, with `operationId`, `parameters`, `requestBody`, and a `responses` map covering every real status code the service returns — 2xx success, 400/401/403/404/409 as applicable, 500/503), `components.schemas` (one schema per real resource, matching the entity's real fields), `components.securitySchemes` if the service has auth. Use the actual domain/resource names and endpoints from `architecture.md` — never a placeholder `Example` schema.

**If Maven — `pom.xml`:** no Spring Boot parent (this isn't a runnable app). Dependencies: `jakarta.validation-api`, `jackson-databind-nullable` (required by openapi-generator's Spring output for nullable-vs-absent JSON fields). Plugin: `org.openapitools:openapi-generator-maven-plugin`, `generate` goal bound to a build phase, configured with:
```xml
<configuration>
    <inputSpec>${project.basedir}/src/main/resources/api-spec/{{service-name}}-api-spec.yaml</inputSpec>
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
**Important convention:** `apiPackage`/`modelPackage` are namespaced under the **consuming REST service's own package**, not the api-spec artifact's own package — e.g. an api-spec artifact for a `tenant-service` (package `com.example.tenantservice`) generates into `com.example.tenantservice.api.spec.api` / `.model`, so the service's controller can `implements TenantsApi` directly using its own package's classes. Get the consuming service's real base package from `architecture.md`/`repo_structure.md` (or from the sibling REST-service repo's own generated `{{PACKAGE_NAME}}` if it was already scaffolded).

**If Gradle — `build.gradle`:** apply the `org.openapi.generator` plugin (community Gradle plugin, functionally equivalent to the Maven plugin above) instead of `java`/`java-library`, with the matching `openApiGenerate` task configuration (`inputSpec`, `generatorName = 'spring'`, `apiPackage`, `modelPackage`, `configOptions`, `generateApiDocumentation = false`). Same dependencies (`jakarta.validation-api`, `jackson-databind-nullable`) as `implementation`.

**Versioning:** the api-spec artifact versions **independently** from the service that consumes it (e.g. service at `0.0.1-SNAPSHOT`, its api-spec at `1.0.0-SNAPSHOT`) — the version reflects the contract, bumped only when the contract itself changes, not on every service release.

**Do NOT put a running Swagger UI in this project** — `springdoc-openapi-ui`/`springdoc-openapi-starter-webmvc-ui` belongs in the **REST service** project (it serves live docs generated from the implemented, running API), not in the contract-only api-spec artifact. Including it here (as the reference project does) has no effect since this artifact never runs — treat that as a **reference-project quirk, not a convention to copy**.

---

## REST service shape (reference: cp-tenant-service)

**Dependencies (same set regardless of build tool):** `spring-boot-starter-web`, `spring-boot-starter-data-jpa`, `spring-boot-starter-validation`, `liquibase-core`, `postgresql` (runtime), `h2` (test), `mapstruct` + `mapstruct-processor` (annotation processor), `hibernate-jpamodelgen` (annotation processor), `springdoc-openapi-starter-webmvc-ui` (serves live Swagger UI + `/v3/api-docs` from the actual running, implemented API — this is where Swagger UI belongs, not the api-spec artifact), `spring-boot-starter-test`, plus **the sibling API spec artifact** as a regular dependency (its real `groupId:artifactId:version`, read from that repo's own `pom.xml`/`build.gradle` once scaffolded — see "API spec shape" above). **Do not** include the reference project's internal `com.mycom.cp:cp-*` artifacts (`cp-security-configure`, `cp-scanner`, `cp-persistence-util`, `cp-rest-client`) — those only resolve against mycom's private Maven repo and would break the build for anyone else; the api-spec dependency is the one exception, since it's this devkit's own convention and will exist locally as a sibling repo. If the target project genuinely needs OAuth2 resource-server auth, use plain `spring-security-oauth2-resource-server` + `spring-security-oauth2-jose`, not the internal wrapper.

**If Maven — `pom.xml`:** `spring-boot-starter-parent` as `<parent>` (pins Spring Boot's dependency-management BOM automatically); the annotation processors (`mapstruct-processor`, `hibernate-jpamodelgen`) go in `maven-compiler-plugin`'s `<annotationProcessorPaths>`; `spring-boot-maven-plugin` for the executable jar.

**If Gradle — `build.gradle` (or `.kts`):** apply plugins `java`, `org.springframework.boot`, and `io.spring.dependency-management` (the last one pulls in Spring Boot's BOM the same way `spring-boot-starter-parent` does in Maven — without it, dependency versions must be pinned manually). Runtime/test deps use the `runtimeOnly` / `testImplementation` configurations (Gradle's equivalent of Maven's `runtime`/`test` scope). Annotation processors go in the `annotationProcessor` configuration, e.g.:
```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '{{springBootVersion}}'
    id 'io.spring.dependency-management' version '1.1.x'
}
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.liquibase:liquibase-core'
    runtimeOnly 'org.postgresql:postgresql'
    testRuntimeOnly 'com.h2database:h2'
    implementation 'org.mapstruct:mapstruct:1.6.3'
    annotationProcessor 'org.mapstruct:mapstruct-processor:1.6.3'
    annotationProcessor 'org.hibernate.orm:hibernate-jpamodelgen'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

**Application class:** standard `@SpringBootApplication` + `SpringApplication.run(...)`, named `{ProjectName}Application`.

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

## Pure library shape (reference: cp-rest-client)

**Core rule (both build tools): no Spring Boot "app" plugin/parent.** A library must not force its packaging/version choices onto consumers. Spring dependencies the library integrates with (`spring-context`, `spring-boot-starter-web`, `spring-boot-autoconfigure`) are **compile-time-only, not bundled** — the consuming application supplies the real versions at runtime. Only include these if the library actually needs Spring; a framework-agnostic library should have zero Spring dependency at all.

**If Maven — `pom.xml`:** **no** `spring-boot-starter-parent` — plain `<packaging>jar</packaging>`, explicit `<properties>` for Java version, dependency versions pinned individually (or via a small `<dependencyManagement>` block for test deps like the JUnit BOM). Spring dependencies use `<scope>provided</scope>` (compile-time only, never bundled into the published jar, never pulled transitively into consumers).

**If Gradle — `build.gradle`:** apply the `java-library` plugin (**not** `org.springframework.boot`, **not** `application`) — `java-library` is the Gradle plugin built specifically for this case, distinguishing `api` (exposed to consumers transitively) from `implementation` (internal only). Spring dependencies map to Maven's `provided` scope via the **`compileOnly`** configuration (compile-time only, not in the published artifact, not exposed to consumers); if tests also need them, add matching `testImplementation` entries since `compileOnly` does not extend to the test source set automatically:
```groovy
plugins {
    id 'java-library'
}
dependencies {
    compileOnly 'org.springframework:spring-context:{{springVersion}}'
    compileOnly 'org.springframework.boot:spring-boot-starter-web:{{springBootVersion}}'
    compileOnly 'org.springframework.boot:spring-boot-autoconfigure:{{springBootVersion}}'
    testImplementation 'org.springframework.boot:spring-boot-starter-web:{{springBootVersion}}'

    testImplementation platform('org.junit:junit-bom:5.11.0')
    testImplementation 'org.junit.jupiter:junit-jupiter-api'
    testImplementation 'org.junit.jupiter:junit-jupiter-params'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
```

**If the library provides Spring auto-configuration** (optional — only if the library needs to register beans automatically in a consumer's Spring context): a `@Configuration` class, typically gated by `@ConditionalOnProperty(prefix = "{library-prefix}.autoconfigure", name = "enabled", havingValue = "true", matchIfMissing = true)` so consumers can opt out; registered via `src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (one fully-qualified class name per line) — **not** the legacy `spring.factories` mechanism.

**Package root:** same `{groupId}.{artifactId}` pattern as the service shape, but sub-packaged by the library's actual concern (not a fixed controller/service/repository layering — a library's internal shape follows its own domain, e.g. `config/`, and whatever core abstraction the library exists to provide). Do not force REST-service layering onto a library that isn't one.

**Tests:** plain JUnit 5 (`junit-jupiter-api`, `junit-jupiter-params`), no Spring context needed unless testing the auto-configuration itself (in which case `spring-boot-starter-test` as a test-scope dependency is fine).

**README.md:** every library skeleton gets one — what it does, how to add it as a dependency, minimal usage example. Services don't strictly need this (their `CLAUDE.md` + `docs/` already cover onboarding), but a short one is fine too.

---

## What the agent must NOT do

- Do not invent proprietary-looking internal dependencies (`com.mycom.cp:*` or similar) — only use real, publicly-resolvable Maven Central artifacts.
- Do not generate a generic "Example"/"Item"/"Foo" placeholder entity when `architecture.md` already names real domain entities — use the real names.
- Do not add Lombok, do not make entities records, do not hand-write entity↔DTO mapping.
- Do not scaffold into a repo that already has `pom.xml`/`build.gradle` or a `src/` directory — that repo already has a real project; leave it untouched.
- Do not generate both `pom.xml` and `build.gradle` in the same repo, and do not apply the Spring Boot Gradle plugin (`org.springframework.boot`) or `spring-boot-starter-parent` to a pure-library skeleton — those are for runnable apps only; libraries use `java-library` (Gradle) or a plain `<packaging>jar</packaging>` POM with no Spring Boot parent (Maven).
- Do not hand-write request/response DTOs directly in a REST-service skeleton — those come from the sibling API spec artifact's generated model classes. If the sibling api-spec repo doesn't exist yet when generating the REST service, stop and report the blocker rather than inventing local DTOs as a workaround.
- Do not put `springdoc-openapi-ui`/Swagger-UI-serving dependencies in the API spec project — that belongs in the REST service (the thing that actually runs).
- Do not generate an API spec YAML with placeholder paths/schemas — use the real endpoints and resource fields from `architecture.md`, matching exactly what the REST-service skeleton implements.
