#!/usr/bin/env bash
# scripts/test/run.sh -- telemetry and validator fixture tests
#
# Runs deterministic telemetry tests, then validates each bad fixture and
# asserts its expected [ERROR] count. Clean adversarial fixtures must pass.
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
    local expected_errors="$2"
    shift 2
    local output
    if output=$(python "$VALIDATOR" "$@" 2>&1); then
        # Validator returned exit 0 -- no errors found (unexpected for bad fixtures).
        echo "[FAIL] $label -- expected violations but validator exited 0"
        echo "       Output: $output"
        fail=$((fail + 1))
    else
        # Exit non-zero -- verify the expected number of violations was printed.
        local error_count
        error_count=$(echo "$output" | grep -c "^\[ERROR\]" || true)
        if [ "$error_count" -eq "$expected_errors" ]; then
            echo "[PASS] $label"
            pass=$((pass + 1))
        else
            echo "[FAIL] $label -- expected $expected_errors [ERROR] line(s), found $error_count"
            echo "       Output: $output"
            fail=$((fail + 1))
        fi
    fi
}

run_clean_fixture() {
    local label="$1"
    shift
    local output
    if output=$(python "$VALIDATOR" "$@" 2>&1); then
        echo "[PASS] $label"
        pass=$((pass + 1))
    else
        echo "[FAIL] $label -- expected no violations"
        echo "       Output: $output"
        fail=$((fail + 1))
    fi
}

echo "=== telemetry.py -- deterministic tests ==="
if python -m unittest scripts.test.test_telemetry; then
    echo "[PASS] telemetry collector tests"
    pass=$((pass + 1))
else
    echo "[FAIL] telemetry collector tests"
    fail=$((fail + 1))
fi

echo ""
echo "=== validate_templates.py -- fixture self-tests ==="
echo ""

# Invariant #1 -- unresolved file reference
run_fixture "inv1: unresolved file reference" 1 \
    "$FIXTURES_BAD/inv1_bad_ref.md"

# Invariant #2 -- unknown placeholder token
run_fixture "inv2: unknown/malformed placeholder" 2 \
    "$FIXTURES_BAD/inv2_bad_placeholder.md"

# Invariant #3 -- unbalanced SHARED markers in a shared file
run_fixture "inv3: unbalanced SHARED-START/SHARED-END" 2 \
    "$FIXTURES_BAD/shared/inv3_bad_shared.md"

# Invariant #4 -- retired trigger (test-only token, seeded via --test-retired-trigger)
run_fixture "inv4: retired trigger string" 2 \
    --test-retired-trigger TEST_RETIRED_TRIGGER_DO_NOT_USE \
    "$FIXTURES_BAD/inv4_bad_trigger.md"

# Invariant #5 -- a full-read directive must not use a numeric mandatory range
run_fixture "inv5: numeric full-read mandatory range" 1 \
    "$FIXTURES_BAD/inv5_bad_full_read_range.md"

run_clean_fixture "inv5: full-read exclusions (negation, boundaries, indented fence)" \
    "$SCRIPT_DIR/fixtures/good/inv5_full_read_exclusions.md"

# Invariant #7 -- Markdown well-formedness (heading jump + unclosed fence)
# Fixture filename retains its pre-FIX-03 `inv6` name; the invariant was #6
# before the new full-read invariant was inserted.
run_fixture "inv6: Markdown well-formedness" 2 \
    "$FIXTURES_BAD/inv6_bad_markdown.md"

echo ""
echo "Results: $pass passed, $fail failed"
if [ "$fail" -gt 0 ]; then
    exit 1
fi
echo "All fixture checks passed."
