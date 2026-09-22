# PowerShell-equivalent local fixture matrix for hosts without Bash.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

python -m unittest scripts.test.test_branch_preflight scripts.test.test_telemetry
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = 'SilentlyContinue'  # Bad fixtures intentionally exit non-zero.
$badCases = @(
    @{ Args = @('scripts/test/fixtures/bad/inv1_bad_ref.md'); ExpectedErrors = 1 },
    @{ Args = @('scripts/test/fixtures/bad/inv2_bad_placeholder.md'); ExpectedErrors = 2 },
    @{ Args = @('scripts/test/fixtures/bad/shared/inv3_bad_shared.md'); ExpectedErrors = 2 },
    @{ Args = @('--test-retired-trigger', 'TEST_RETIRED_TRIGGER_DO_NOT_USE', 'scripts/test/fixtures/bad/inv4_bad_trigger.md'); ExpectedErrors = 2 },
    @{ Args = @('scripts/test/fixtures/bad/inv5_bad_full_read_range.md'); ExpectedErrors = 1 },
    # Filename retains its pre-FIX-03 `inv6` name; Markdown well-formedness is now invariant #7.
    @{ Args = @('scripts/test/fixtures/bad/inv6_bad_markdown.md'); ExpectedErrors = 2 }
)
foreach ($case in $badCases) {
    # Bad fixtures intentionally make Python exit non-zero; diagnostics are on
    # stdout, so suppress only its summary stderr to avoid native-error noise.
    $output = & python scripts/validate_templates.py @($case.Args) 2>$null
    $output | Write-Output
    if ($LASTEXITCODE -eq 0) { throw "Expected validator fixture failure did not occur: $($case.Args)" }
    $actualErrors = @($output | Where-Object { $_ -match '^\[ERROR\]' }).Count
    if ($actualErrors -ne $case.ExpectedErrors) { throw "Expected $($case.ExpectedErrors) [ERROR] line(s), found ${actualErrors}: $($case.Args)" }
}
$cleanOutput = & python scripts/validate_templates.py scripts/test/fixtures/good/inv5_full_read_exclusions.md
$cleanOutput | Write-Output
if ($LASTEXITCODE -ne 0) { throw 'Expected inv5 full-read exclusion fixture to pass.' }
$ErrorActionPreference = $previousErrorActionPreference
Write-Output 'All telemetry and validator fixture checks passed.'
