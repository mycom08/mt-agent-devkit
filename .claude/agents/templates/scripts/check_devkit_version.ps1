$ErrorActionPreference = "SilentlyContinue"

$versionFile = ".claude/agents/devkit_version.txt"
if (-not (Test-Path $versionFile)) { exit 0 }
$currentVersion = (Get-Content $versionFile -Raw).Trim()

if (-not (Test-Path "CLAUDE.md")) { exit 0 }
$claudeContent = Get-Content "CLAUDE.md" -Raw
if ($claudeContent -notmatch '\*\*Devkit source:\*\*\s+(https?://\S+)') { exit 0 }
$sourceUrl = $Matches[1].TrimEnd('/')

try {
    $latestVersion = (Invoke-WebRequest "$sourceUrl/version.txt" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop).Content.Trim()
} catch { exit 0 }

if ([string]::IsNullOrEmpty($latestVersion)) { exit 0 }

if ($currentVersion -ne $latestVersion) {
    Write-Output "{`"systemMessage`": `"Devkit update available: v$currentVersion -> v$latestVersion. Run 'sync devkit' to update.`"}"
}
