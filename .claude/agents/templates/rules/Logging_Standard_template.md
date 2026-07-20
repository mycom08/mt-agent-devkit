# Logging Standard

**Applies to:** Developer (before writing log statements), QA (during code review)
**Skip for:** documentation-only, API spec, Dockerfile, docker-compose, migration SQL, `.github/workflows/`/CI YAML, or config-only stories

---

## 1. Log Levels

Each level below carries the same rule: **use with weight — never indiscriminate logging.** A log statement should earn its place; logging every branch or every variable assignment buries the signal that matters in noise and makes real incidents harder to find, not easier.

### ERROR
The operation failed. Use for an uncaught exception, a crash, or any condition that stops the current operation from completing successfully.
- Example: a request handler cannot complete because a required downstream call failed with no fallback.
- Example: an unrecoverable startup failure that prevents the service from becoming ready.

### WARN
The system is degraded but recovered, or a condition exists that could become critical if not addressed.
- Example: a missing or malformed environment variable that was defaulted instead of failing the request.
- Example: a third-party/downstream connectivity failure that was retried successfully, or that triggered a fallback path.
- Example: a memory-leak signal (growing heap/connection-pool usage over time) that has not yet caused a failure.
- Example: a stale cache entry served because the refresh failed, with the caller unaffected.

### INFO
A significant business or runtime event — not routine internal detail.
- Example: an important incoming request (a state-changing operation, not every read).
- Example: a special process starting or completing (batch job, scheduled task, service startup/shutdown).

### DEBUG
Diagnostic detail intended for troubleshooting, not for routine review.
- Example: a handled exception where fallback logic allows the flow to continue — the exception did not fail the operation, so it does not qualify as ERROR or WARN, but the detail is useful when diagnosing why the fallback triggered.
- Example: intermediate computed values, request/response payload shapes, or branch decisions useful only when actively debugging.

---

## 2. Single-Log Rule

Each exception is logged **once**, at the layer that actually handles it — the layer that decides whether to recover, fall back, retry, or let the operation fail. Do not log-and-rethrow: catching an exception, logging it, and then rethrowing it (or wrapping and rethrowing) causes the same failure to be logged again by an outer catch block, producing duplicate noise for a single root cause.

- If a layer catches an exception only to add context and rethrow, add the context to the exception (message, wrapped cause, or structured fields) and let the layer that terminally handles it perform the single log call.
- **Full stack trace is included only at ERROR level.** WARN, INFO, and DEBUG log the exception message and relevant context, not the full trace — a full trace at every level defeats the purpose of level-based triage.

---

## 3. Sensitive-Data Prohibition

Never log the following, at any level, in any form (including inside serialized objects, request/response dumps, or debug payloads):
- Usernames or any personally identifying account identifier tied to credentials
- Passwords, tokens, API keys, or other secrets
- Card numbers or other payment instrument details
- Any other data classified as sensitive by the target project's data-handling policy (e.g. national ID numbers, health data)

Mask or omit these fields before logging (e.g. redact to `****`, log a non-reversible reference ID instead of the raw value). This rule holds even at DEBUG level — diagnostic convenience never overrides sensitive-data handling.

---

## 4. Log Format

Default example (Java, Logback/Log4j pattern layout):
```
%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n
```

This is a starting point, not a mandate. Adapt the format to the target project's actual tech-stack best practice — e.g. structured JSON logging for a service that ships logs to a log-aggregation pipeline, the standard `logging` module format for Python, `zap`/`zerolog` structured fields for Go. Whatever format is chosen, preserve the same information the example carries: timestamp, thread/request context, level, logger/component name, and message.

---

## Version

**Version:** 1.0 — Initial version (ST-000023): four log levels, single-log rule, sensitive-data prohibition, adaptable format guidance
**Created:** 2026-07-20
