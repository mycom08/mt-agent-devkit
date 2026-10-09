$ErrorActionPreference = "SilentlyContinue"

$versionFile = "{{AGENT_DIR_PREFIX}}/agents/devkit_version.txt"
if (-not (Test-Path $versionFile)) { exit 0 }
$currentVersion = (Get-Content $versionFile -Raw).Trim()

if (-not (Test-Path "{{ROOT_FILE}}")) { exit 0 }
$claudeContent = Get-Content "{{ROOT_FILE}}" -Raw
if ($claudeContent -notmatch '\*\*Devkit source:\*\*\s+(https?://\S+)') { exit 0 }
$sourceUrl = ($Matches[1].TrimEnd('/')) -replace '\.git$', ''

# Tolerate an older install whose field still holds a raw base URL
# (https://raw.githubusercontent.com/{owner}/{repo}/<ref>) — reduce it to the
# canonical repository URL so the tag lookup below still resolves. The next
# `sync devkit` rewrites the field itself.
if ($sourceUrl -match '^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)') {
    $sourceUrl = "https://github.com/$($Matches[1])/$($Matches[2])"
}

# Latest release = highest tag matching vX.Y.Z. git ls-remote needs no credentials
# on a public repo and has no rate limit, unlike the GitHub REST API (60/hour per
# IP unauthenticated) — a rate-limited call would suppress update notices silently.
# The ^v\d+\.\d+\.\d+$ filter is required: -v:refname sorts a bare v7-style tag
# above v7.0.0, so an unfiltered first match can return a non-release tag.
$env:GIT_TERMINAL_PROMPT = "0"
try {
    $refs = & git ls-remote --tags --refs --sort=-v:refname "$sourceUrl.git" 2>$null
    if ($LASTEXITCODE -ne 0) { exit 0 }
} catch { exit 0 }

$latestTag = $refs |
    ForEach-Object { ($_ -split 'refs/tags/')[-1] } |
    Where-Object { $_ -match '^v\d+\.\d+\.\d+$' } |
    Select-Object -First 1

if ([string]::IsNullOrEmpty($latestTag)) { exit 0 }
$latestVersion = $latestTag.Substring(1)

if ($currentVersion -ne $latestVersion) {
    Write-Output "{`"systemMessage`": `"Devkit update available: v$currentVersion -> v$latestVersion. Run 'sync devkit' to update.`"}"
}
