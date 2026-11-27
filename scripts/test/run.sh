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

echo "=== branch preflight + telemetry -- deterministic tests ==="
if python -m unittest scripts.test.test_common_capabilities scripts.test.test_read_manifest scripts.test.test_wait_work scripts.test.test_branch_preflight scripts.test.test_telemetry scripts.test.test_project_settings scripts.test.test_retro_completion scripts.test.test_upgrade_deployment scripts.test.test_phase2_deployment scripts.test.test_phase2_bundle scripts.test.test_phase2_sync scripts.test.test_phase2_legacy_contracts scripts.test.test_version_notice scripts.test.test_check_gh_posts; then
    echo "[PASS] branch preflight and telemetry tests"
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

# Invariant #5 -- a full-read directive must not require a numeric section range
run_fixture "inv5: numeric full-read mandatory range" 1 \
    "$FIXTURES_BAD/inv5_bad_full_read_range.md"
run_fixture "inv5: numeric full-read required range" 1 \
    "$FIXTURES_BAD/inv5_bad_full_read_required.md"
run_fixture "inv5: passive full-read necessary range" 1 \
    "$FIXTURES_BAD/inv5_bad_full_read_necessary.md"

run_clean_fixture "inv5: full-read exclusions (negation, boundaries, indented fence)" \
    "$SCRIPT_DIR/fixtures/good/inv5_full_read_exclusions.md"

# Invariant #6 -- changes.json format and deployment manifest integrity.
# Each fixture feeds the check through --changes-json / --manifest-root;
# the repo-root changes.json is never replaced. A clean Markdown file is the
# scan target so only invariant #6 errors count.
INV6_SCAN="$SCRIPT_DIR/fixtures/good/inv5_full_read_exclusions.md"
run_fixture "inv6: invalid version key" 1 \
    --changes-json "$FIXTURES_BAD/manifest_bad_version.json" "$INV6_SCAN"
run_fixture "inv6: invalid deployment declaration" 1 \
    --changes-json "$FIXTURES_BAD/manifest_bad_deployment.json" "$INV6_SCAN"
run_fixture "inv6: legacy arrays are not the two bridges" 1 \
    --changes-json "$FIXTURES_BAD/manifest_bad_legacy_arrays.json" \
    --manifest-root "$FIXTURES_BAD/manifest_empty_root" "$INV6_SCAN"
run_fixture "inv6: unsafe deployment asset path" 1 \
    --changes-json "$FIXTURES_BAD/manifest_unsafe_asset.json" \
    --manifest-root "$FIXTURES_BAD/manifest_unsafe_asset_root" "$INV6_SCAN"
run_fixture "inv6: duplicate deployment asset path" 1 \
    --changes-json "$FIXTURES_BAD/manifest_duplicate_asset.json" \
    --manifest-root "$FIXTURES_BAD/manifest_duplicate_asset_root" "$INV6_SCAN"
run_fixture "inv6: deployment asset hash mismatch" 1 \
    --changes-json "$FIXTURES_BAD/manifest_bad_hash.json" \
    --manifest-root "$FIXTURES_BAD/manifest_bad_hash_root" "$INV6_SCAN"

# A changes.json holding only the three newest entries must pass.
TRIMMED_CHANGES="$(mktemp)"
python - "$REPO_ROOT/changes.json" "$TRIMMED_CHANGES" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
trimmed = dict(list(data.items())[:3])
json.dump(trimmed, open(sys.argv[2], "w", encoding="utf-8"))
PY
run_clean_fixture "inv6: three newest changes.json entries pass" \
    --changes-json "$TRIMMED_CHANGES"
rm -f "$TRIMMED_CHANGES"

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
