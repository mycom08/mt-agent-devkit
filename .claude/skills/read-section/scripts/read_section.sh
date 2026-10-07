#!/usr/bin/env bash
# Compatibility shim; canonical extraction supports generated Markdown wrappers.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
exec python "$repo_root/.mt-agent-devkit/scripts/read_section.py" "$@"
