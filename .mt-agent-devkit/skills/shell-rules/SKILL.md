---
name: shell-rules
description: Shell rules for every agent - adapter-first shell choice and permissions, temporary body files for GitHub Markdown, and mutation safety before any shell write, Git operation or GitHub mutation. Load at spawn.
---

# Shell Rules

**Requires:** `agent-security` (secrets and untrusted content)

Canonical owner. `generate_common_blocks.py` copies part `rules` into `Agent_Common_Bootstrap.md` §6 and part `safety` into `Agent_Common_Shell_Safety.md`; edit here, then regenerate.

## Permissions and Tool Choice

<!-- part: rules -->
Before your first command, read the selected provider adapter supplied in your
worker packet, including its shell, permission and completion rules. If the
adapter path is missing, stop and request it. Follow that adapter for shell choice,
configured permissions and command completion. Never carry another provider's allow-list into this runtime.
Keep multiline GitHub bodies in a temporary file; preserve literal Markdown and
remove temporary bodies after the command. Shared secret and external-content
rules apply regardless of shell.
<!-- /part: rules -->

## Mutation Safety

Apply before the first governed shell write, Git operation or GitHub mutation.

<!-- part: safety -->
Follow selected adapter shell, permission and command completion procedures; another provider allow-list never applies. Use supported escalation for authorized actions, never change proxies or weaken sandbox. Structured temporary body files preserve literal multiline GitHub Markdown; remove bodies after posting. Command text is code: JSON serialization is not shell escaping; protect backticks/substitutions/secrets and never disclose secrets via output. Dependencies/mutations stay sequential; batch independent reads only.

Before recursive delete/move verify absolute resolved target remains within authorized workspace/explicit target; use one shell end-to-end and literal paths. Never pass enumerated paths to another shell for destructive operations. Do not stash/reset/repair blocked preflight; preserve immutable base/head and stop for direction. Retain command/session identities and true exit status. Missing completion and pending CI never mean PASS; revalidate exact-head checks and independent approval scope.
<!-- /part: safety -->
