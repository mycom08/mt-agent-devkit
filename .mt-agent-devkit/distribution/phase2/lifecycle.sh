#!/usr/bin/env bash
set -euo pipefail
script_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -n "${MT_DEVKIT_PYTHON:-}" ]]; then
  "$MT_DEVKIT_PYTHON" -c 'import sys; assert sys.version_info >= (3,10)' || exit 2
  exec "$MT_DEVKIT_PYTHON" "$script_root/lifecycle.py" "$@"
fi
for interpreter in python3 python; do
  if "$interpreter" -c 'import sys; assert sys.version_info >= (3,10)' >/dev/null 2>&1; then
    exec "$interpreter" "$script_root/lifecycle.py" "$@"
  fi
done
echo 'Python 3.10+ required; set MT_DEVKIT_PYTHON to its executable.' >&2
exit 2
