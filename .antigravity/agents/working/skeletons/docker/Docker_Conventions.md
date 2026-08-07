# Docker Conventions

> Cross-language convention for how any generated service gets containerized and run locally. This document owns the **consultation flow** (does the user even want Docker, is it installed) and the **file-layout** (where Dockerfiles, compose files, run scripts, and the README live). It does not own language-specific build/runtime details (base images, dependency installs, healthcheck wiring) — those live in the shape file for that language (e.g. [`Java_Skeleton_REST_Service.md`](../java/Java_Skeleton_REST_Service.md)'s "Docker" section), which defers to this document for layout and links back here rather than restating it.

---

## Docker Consultation (once per build, orchestrator-direct)

Asked once, up front, by `Build_Software_Workflow.md`'s Stage 4 Entry — not per repo, not per shape file. Never assume; always ask unless the user already stated a preference earlier in the same build.

```
This build can generate Docker artifacts (Dockerfile, compose, run scripts) for containerized services.

1. Do you want to use Docker for running these services locally?
   - "yes" — generate Docker artifacts as described below
   - "no, I have my own setup" — skip all Docker artifact generation; services still get a plain run script where applicable
   - "no" — skip Docker artifact generation entirely
   - "default" — use Docker (this devkit's default)
```

**If the answer is "yes" or "default":**
1. Detect Docker: run `docker --version`.
2. If found, proceed — no further action needed.
3. If **not** found, ask the user:
   ```
   Docker isn't installed on this machine. Want me to install it now?
   - "yes" — attempt a best-effort install for your OS (winget/choco on Windows, brew on Mac, apt on Linux)
   - "no" — I'll skip Docker artifact generation for this build; you can install it later and re-run
   ```
   - If **yes**: attempt the OS-appropriate install command. This is a real environment-mutating action (may need admin/sudo, may fail depending on permissions) — report success/failure back to the user plainly, don't silently continue past a failed install.
   - If **no**: treat this build as if the Docker Consultation answer were "no" — skip Docker artifact generation, fall back to plain run scripts only.

**If the answer is "no, I have my own setup" or "no":** skip Docker artifact generation for every repo in this build. A shape file's plain (non-Docker) run script/start script — where one exists — is still generated; nothing else under "File Layout" below applies.

---

## File Layout

Applies per repo, only when the Docker Consultation resolved to generating Docker artifacts.

| Artifact | Location | When |
|---|---|---|
| `Dockerfile` | `<repo-root>/docker/Dockerfile` | Every containerized service |
| Docker-based run script (`run.sh` / `run.ps1`) | `<repo-root>/docker/sandbox/` | Service with **no** other infra dependency (build + configure env + `docker run`) |
| `docker-compose.yml` (service + its own infra) | `<repo-root>/docker/sandbox/` | Service that depends on other infra (database, cache, identity provider, etc.) |
| `docker-compose.yml` (whole-project aggregation) | `<project-orchestrator-root>/docker/sandbox/` | Multi-repo project — brings up every dockerized sub-repo together |
| `README.md` | `<repo-root>/docker/README.md` (and `<project-orchestrator-root>/docker/README.md` for the aggregation compose) | Always, alongside whichever of the above were generated |

**`<repo-root>` is the individual service repo's own root** (e.g. `tenant-service/docker/Dockerfile`), never the overall project/orchestrator root. **`<project-orchestrator-root>` is the top-level folder that holds all sibling service repos** in a multi-repo build (see `Build_Software_Workflow.md` Path B) — the whole-project compose lives there, one level above the individual services, not inside any one of them.

**A service always keeps its non-Docker run path too.** Where a shape file defines a plain, no-Docker run script (e.g. Java's `start.sh`/`start.ps1` for the no-database case), that script is unaffected by this document — it stays at the repo root, unchanged. The Docker run script/compose described here is an *additional*, Docker-specific way to run the same service, not a replacement.

**Build-context math when the Dockerfile moves under `docker/`.** A shape file's Dockerfile may need to see sibling repos outside its own repo root (e.g. Java's sibling API-spec dependency) — that requirement is unchanged by this document, but the *relative path* from a compose file at `<repo-root>/docker/sandbox/docker-compose.yml` up to that shared parent directory is now three levels (`../../..`), not one (`..`), since the compose file sits two directories deeper than it used to (repo root → `docker/` → `sandbox/`). The Dockerfile's own path relative to that context remains `<repo-name>/docker/Dockerfile`. See the shape file's own Docker section for the concrete compose snippet.

**CI/release references to the Dockerfile's path** (e.g. a `docker/build-push-action` step's `file:` input) must include the `docker/` segment — `./<repo-name>/docker/Dockerfile`, not `./<repo-name>/Dockerfile`. The build `context:` for CI is unaffected by this — it was never anchored to the Dockerfile's own location to begin with.

---

## `docker/README.md`

Generated alongside the Docker artifacts, one per repo (plus one at the project-orchestrator root when a whole-project compose exists). Explains, in plain language:
- What's in this folder (`Dockerfile`, and whichever of `sandbox/run.sh`/`sandbox/run.ps1`/`sandbox/docker-compose.yml` were generated)
- The exact command to run each one
- Which environment variables the run script/compose sets, and what a real deployment should override
- How this relates to the non-Docker run path, if one exists (e.g. "prefer `start.sh` for a fast local edit-loop without rebuilding a container; use `docker/sandbox/` for a container-parity run")

The repo-root `README.md`'s own "Getting Started" section keeps a short pointer rather than duplicating this content, e.g.:
```markdown
## Getting Started

Two ways to run this service locally:
- **Plain JVM:** `./start.sh` (or `start.ps1` on Windows) — fastest edit-loop, no container.
- **Docker:** see [`docker/README.md`](docker/README.md) for the containerized run.
```

---

## What must NOT be done

- Do not generate Docker artifacts at all if the Docker Consultation resolved to "no"/"no, I have my own setup" — a plain run script (where the shape file defines one) is still fine, Docker-specific files are not.
- Do not attempt to install Docker without asking first, and do not silently continue past a failed install as if it succeeded.
- Do not put a per-service Dockerfile or compose file at the project-orchestrator root, or the whole-project aggregation compose inside a single service repo — each lives at its own layout location above.
- Do not remove or replace an existing non-Docker run script (e.g. `start.sh`) when adding the Docker-based run script — both exist side by side.
- Do not bake real credentials into any generated Dockerfile, compose file, or run script — dev-only defaults matching the service's own config placeholders only.
