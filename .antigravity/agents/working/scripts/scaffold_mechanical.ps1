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

# 6. Blank memory and 7. Blank working records
$roles = @("Business_Analyst", "Developer", "Product_Owner", "QA", "Technical_Lead", "UI_UX_Designer")
foreach ($role in $roles) {
    $roleLabel = if ($role -eq "UI_UX_Designer") { "UI/UX Designer" } else { $role -replace '_', ' ' }
    
    "# $roleLabel Memory`n`nNo facts recorded yet.`n" | Set-Content -Path (Join-Path $Agents "memory\${role}_Memory.md")
    
    "# $roleLabel Working Record`n`n**Story:** none yet`n**Completed:** —`n**In Progress:** —`n**Impediments:** —`n`n**Blockers & Watch-outs:**`n- (none)`n" | Set-Content -Path (Join-Path $Agents "working-record\${role}_Working_Record.md")
}

Write-Host "Mechanical scaffold complete: $TargetProject"
