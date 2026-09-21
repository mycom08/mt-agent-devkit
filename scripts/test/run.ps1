# PowerShell-equivalent local fixture matrix for hosts without Bash.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

python -m unittest scripts.test.test_telemetry
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$cases = @(
    @('scripts/test/fixtures/bad/inv1_bad_ref.md'),
    @('scripts/test/fixtures/bad/inv2_bad_placeholder.md'),
    @('scripts/test/fixtures/bad/shared/inv3_bad_shared.md'),
    @('--test-retired-trigger', 'TEST_RETIRED_TRIGGER_DO_NOT_USE', 'scripts/test/fixtures/bad/inv4_bad_trigger.md'),
    @('scripts/test/fixtures/bad/inv6_bad_markdown.md')
)
foreach ($case in $cases) {
    & python scripts/validate_templates.py @case
    if ($LASTEXITCODE -eq 0) { throw "Expected validator fixture failure did not occur: $case" }
}
Write-Output 'All telemetry and validator fixture checks passed.'
