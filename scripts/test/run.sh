#!/usr/bin/env bash
# scripts/test/run.sh -- validator self-test: fixture files
#
# Runs validate_templates.py against each bad fixture and asserts that every
# fixture produces at least one [ERROR] line (proving each invariant fires).
#
# Usage (from repo root):
#   bash scripts/test/run.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VALIDATOR="$REPO_ROOT/scripts/validate_templates.py"
FIXTURES_BAD="$SCRIPT_DIR/fixtures/bad"

pass=0
fail=0

run_fixture() {
    local label="$1"
    shift
    local output
    if output=$(python "$VALIDATOR" "$@" 2>&1); then
        # Validator returned exit 0 -- no errors found (unexpected for bad fixtures).
        echo "[FAIL] $label -- expected violations but validator exited 0"
        echo "       Output: $output"
        fail=$((fail + 1))
    else
        # Exit non-zero -- check that at least one [ERROR] line was printed.
        if echo "$output" | grep -q "^\[ERROR\]"; then
            echo "[PASS] $label"
            pass=$((pass + 1))
        else
            echo "[FAIL] $label -- exited non-zero but no [ERROR] lines found"
            echo "       Output: $output"
            fail=$((fail + 1))
        fi
    fi
}

echo "=== validate_templates.py -- fixture self-tests ==="
echo ""

# Invariant #1 -- unresolved file reference
run_fixture "inv1: unresolved file reference" \
    "$FIXTURES_BAD/inv1_bad_ref.md"

# Invariant #2 -- unknown placeholder token
run_fixture "inv2: unknown/malformed placeholder" \
    "$FIXTURES_BAD/inv2_bad_placeholder.md"

# Invariant #3 -- unbalanced SHARED markers in a shared file
run_fixture "inv3: unbalanced SHARED-START/SHARED-END" \
    "$FIXTURES_BAD/shared/inv3_bad_shared.md"

# Invariant #4 -- retired trigger (test-only token, seeded via --test-retired-trigger)
run_fixture "inv4: retired trigger string" \
    --test-retired-trigger TEST_RETIRED_TRIGGER_DO_NOT_USE \
    "$FIXTURES_BAD/inv4_bad_trigger.md"

# Invariant #6 -- Markdown well-formedness (heading jump + unclosed fence)
run_fixture "inv6: Markdown well-formedness" \
    "$FIXTURES_BAD/inv6_bad_markdown.md"

echo ""
echo "Results: $pass passed, $fail failed"
if [ "$fail" -gt 0 ]; then
    exit 1
fi
echo "All fixture checks passed."
