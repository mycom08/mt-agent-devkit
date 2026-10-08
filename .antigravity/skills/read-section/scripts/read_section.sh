#!/usr/bin/env bash
# Compatibility shim; canonical extraction supports generated Markdown wrappers.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
if command -v python >/dev/null 2>&1; then
    exec python "$repo_root/.mt-agent-devkit/scripts/read_section.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 "$repo_root/.mt-agent-devkit/scripts/read_section.py" "$@"
else
    echo "read-section: Python is required (python or python3)" >&2
    exit 127
fi
