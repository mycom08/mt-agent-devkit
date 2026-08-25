param (
    [Parameter(Mandatory=$true)][string]$DevkitRoot,
    [Parameter(Mandatory=$true)][string]$TargetProject,
    [Parameter(Mandatory=$true)][ValidateSet('strict', 'github')][string]$Mode,
    [string]$GhSlug
)

$ErrorActionPreference = 'Stop'

$Tpl = Join-Path $DevkitRoot ".antigravity\agents\templates"
$Agents = Join-Path $TargetProject ".antigravity\agents"

# 1. Directories
$directories = @(
    "context", "memory", "rules", "working-record", 
    "workflows", "scripts", "retros", "tmp", "docs"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Agents $dir) | Out-Null
}
New-Item -ItemType Directory -Force -Path (Join-Path $TargetProject "docs\wiki") | Out-Null

if ($Mode -eq 'strict') {
    New-Item -ItemType Directory -Force -Path (Join-Path $Agents "docs\stories") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $Agents "docs\sprints") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $Agents "docs\reviews") | Out-Null
    Set-Content -Path (Join-Path $Agents "docs\story_counter.txt") -Value "0"
}

# 2. Verbatim rules files
$VerbatimRules = @(
    "Agent_Common_Bootstrap", "Agent_Common_Read_On_Demand", "Audit_Rules", "Blocked_Request",
    "CICD_Validation_Guide", "Clean_Code_Rules", "Product_Owner_Rules_Bootstrap",
    "Product_Owner_Rules_Read_On_Demand", "Retro_Rules",
    "Story_Standard_TL", "Strict_Mode_Story_Guide", "UI_Prototype_Rules"
)

$ghOrg = ""
$ghRepo = ""
if (-not [string]::IsNullOrEmpty($GhSlug)) {
    $parts = $GhSlug -split '/'
    if ($parts.Length -eq 2) {
        $ghOrg = $parts[0]
        $ghRepo = $parts[1]
    }
}

foreach ($f in $VerbatimRules) {
    $src = Join-Path $Tpl "rules\${f}_template.md"
    $dst = Join-Path $Agents "rules\${f}.md"
    
    if (-not [string]::IsNullOrEmpty($GhSlug)) {
        (Get-Content -Path $src -Raw) -replace '\{github-org\}', $ghOrg -replace '\{repo-name\}', $ghRepo | Set-Content -Path $dst -NoNewline
    } else {
        Copy-Item -Path $src -Destination $dst -Force
    }
}

# 3. Workflow files
$NonSplitWorkflows = @("Sync_Devkit_Workflow", "Workflow_Guide")
foreach ($f in $NonSplitWorkflows) {
    Copy-Item -Path (Join-Path $Tpl "workflows\${f}_template.md") -Destination (Join-Path $Agents "workflows\${f}.md") -Force
}

$SplitWorkflows = @(
    "Create_Stories_Workflow", "Plan_Sprint_Workflow", "Refine_Prototype_Workflow",
    "Refine_Sprint_Workflow", "Resume_Story_Workflow", "Shared_Pipeline_Stages",
    "Sprint_Workflow", "Start_Story_Workflow"
)

foreach ($f in $SplitWorkflows) {
    $shared = Join-Path $Tpl "shared\workflows\${f}_Shared_template.md"
    $modefile = Join-Path $Tpl "${Mode}\workflows\${f}_template.md"
    $dst = Join-Path $Agents "workflows\${f}.md"
    
    # Very basic merge for split workflows
    $sharedContent = Get-Content -Path $shared -Raw
    $sharedContent = [regex]::Match($sharedContent, '(?s)<!-- SHARED-START -->(.*?)<!-- SHARED-END -->').Groups[1].Value
    Set-Content -Path $dst -Value $sharedContent -NoNewline
}

# 4. Version check scripts
Copy-Item -Path (Join-Path $Tpl "scripts\check_devkit_version.ps1") -Destination (Join-Path $Agents "scripts\check_devkit_version.ps1") -Force
Copy-Item -Path (Join-Path $Tpl "scripts\check_devkit_version.sh") -Destination (Join-Path $Agents "scripts\check_devkit_version.sh") -Force

# 5. devkit_version.txt
Copy-Item -Path (Join-Path $DevkitRoot "version.txt") -Destination (Join-Path $Agents "devkit_version.txt") -Force

# 6. Blank memory files -- Developer/QA/Technical_Lead get a two-tier live-index + archive
#    pair (blank shape per Agent_Common_Read_On_Demand.md section 8); the other three roles
#    keep the single blank-file format unchanged.
# 7. Blank working records
$roles = @("Business_Analyst", "Developer", "Product_Owner", "QA", "Technical_Lead", "UI_UX_Designer")
$twoTierRoles = @("Developer", "QA", "Technical_Lead")
foreach ($role in $roles) {
    $roleLabel = if ($role -eq "UI_UX_Designer") { "UI/UX Designer" } else { $role -replace '_', ' ' }

    if ($twoTierRoles -contains $role) {
        "# $roleLabel Memory`n`n> Two-tier memory -- see Agent_Common_Read_On_Demand.md section 8. This is the lean, always-read index -- titles and grep-able keywords only, no fact bodies. Full text lives in ${role}_Memory_Archive.md. Before starting a task, scan the titles and keywords below for a match; if one matches, retrieve just that fact per the section 8 bounded-read recipe -- never read the whole archive.`n`n## Standing Checks`n`n*(none yet -- no current fact reduces to an unconditional always-do action; entries move here if a future fact qualifies)*`n`n## Keyword Index`n`n*(none yet)*`n`n## Troubleshooting Facts`n`n*(none yet)*`n" | Set-Content -Path (Join-Path $Agents "memory\${role}_Memory.md")

        "# $roleLabel Memory Archive`n`n> Full-text archive for ${role}_Memory.md Keyword Index tier -- see Agent_Common_Read_On_Demand.md section 8. Not read every spawn; open only when an index line keyword matches your current task, locating the matching fact by grep (heading marker ^### Fact ) -- never a full-file read.`n`n## Stored Facts`n`n*(none yet)*`n" | Set-Content -Path (Join-Path $Agents "memory\${role}_Memory_Archive.md")
    } else {
        "# $roleLabel Memory`n`nNo facts recorded yet.`n" | Set-Content -Path (Join-Path $Agents "memory\${role}_Memory.md")
    }

    "# $roleLabel Working Record`n`n**Story:** none yet`n**Completed:** —`n**In Progress:** —`n**Impediments:** —`n`n**Blockers & Watch-outs:**`n- (none)`n" | Set-Content -Path (Join-Path $Agents "working-record\${role}_Working_Record.md")
}

Write-Host "Mechanical scaffold complete: $TargetProject"
