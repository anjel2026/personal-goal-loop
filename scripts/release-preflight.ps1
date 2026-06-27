[CmdletBinding()]
param(
    [string]$PrivateDenylist = "",
    [switch]$KeepArtifacts,
    [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Script
    )

    Write-Host ""
    Write-Host "==> $Name"
    & $Script
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$ArgumentList
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($ArgumentList -join ' ')"
    }
}

function Remove-RepoPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if (-not ($resolved.StartsWith($RepoRoot + [IO.Path]::DirectorySeparatorChar))) {
        throw "Refusing to remove outside repository: $resolved"
    }

    try {
        Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop
    }
    catch {
        Write-Warning "Could not remove generated path: $resolved"
        Write-Warning $_.Exception.Message
    }
}

function Clear-GeneratedState {
    param([switch]$KeepReviewArtifacts)

    $targets = @(
        "build",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "src\personal_goal_loop.egg-info",
        "tests\fixtures\synthetic_timecard.xlsx",
        "src\personal_goal_loop\__pycache__",
        "tests\__pycache__",
        "tests\fixtures\__pycache__"
    )

    if (-not $KeepReviewArtifacts) {
        $targets += @(".tmp", "dist")
    }

    foreach ($target in $targets) {
        Remove-RepoPath $target
    }
}

function Assert-NoGeneratedWorkbookResidue {
    $patterns = @("*.xlsx", "*.xlsm", "*.anonymize-report.json")
    $excludedRootDirs = @(
        ".git",
        ".tmp",
        "build",
        "dist",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache"
    )
    $residue = @()

    foreach ($item in Get-ChildItem -LiteralPath $RepoRoot -Force) {
        if ($item.PSIsContainer) {
            if ($excludedRootDirs -contains $item.Name) {
                continue
            }
            $residue += Get-ChildItem -LiteralPath $item.FullName -Recurse -File -Include $patterns
            continue
        }

        foreach ($pattern in $patterns) {
            if ($item.Name -like $pattern) {
                $residue += $item
            }
        }
    }

    if ($residue) {
        $paths = ($residue | Select-Object -ExpandProperty FullName) -join [Environment]::NewLine
        throw "Generated workbook/report residue found outside .tmp:$([Environment]::NewLine)$paths"
    }
}

Invoke-Step "Clean previous generated state" { Clear-GeneratedState }

$TempRoot = Join-Path $RepoRoot (".tmp\p" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null
$env:TMP = $TempRoot
$env:TEMP = $TempRoot
$env:PYTEST_DEBUG_TEMPROOT = $TempRoot
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

if (-not $SkipInstall) {
    Invoke-Step "Install package with dev dependencies" {
        Invoke-Native python -m pip install -e ".[dev]"
    }
}

Invoke-Step "Lint" { Invoke-Native python -m ruff check . }
Invoke-Step "Type check" { Invoke-Native python -m mypy src }
Invoke-Step "Tests" { Invoke-Native python "-m" "pytest" "-p" "no:cacheprovider" }

Invoke-Step "Generate synthetic workbook" {
    Invoke-Native python tests/fixtures/make_synthetic_workbook.py
}

Invoke-Step "Anonymizer dry run" {
    Invoke-Native pgl-anonymize-workbook `
        --input tests/fixtures/synthetic_timecard.xlsx `
        --output .tmp/synthetic_timecard_anonymized.xlsx `
        --rules examples/rules.synthetic.json `
        --dry-run
}

Invoke-Step "Anonymize synthetic workbook" {
    Invoke-Native pgl-anonymize-workbook `
        --input tests/fixtures/synthetic_timecard.xlsx `
        --output .tmp/synthetic_timecard_anonymized.xlsx `
        --rules examples/rules.synthetic.json `
        --overwrite
}

Invoke-Step "Synthetic output PII gate" {
    Invoke-Native pgl-pii-gate .tmp/synthetic_timecard_anonymized.xlsx --denylist examples/denylist.synthetic.json
    Invoke-Native pgl-pii-gate .tmp/synthetic_timecard_anonymized.anonymize-report.json --denylist examples/denylist.synthetic.json
}

Invoke-Step "Synthetic full-tree smoke gate" {
    Invoke-Native pgl-pii-gate . --denylist examples/denylist.synthetic.json --exclude examples/** --exclude tests/**
}

Invoke-Step "Improvement loop smoke test" {
    Invoke-Native pgl-create-project-card `
        --intake template-vault/00_Inbox/Project_Intake.md `
        --output .tmp/PROJECT_CARD.md `
        --title "Synthetic Fixture Work" `
        --overwrite
    Invoke-Native pgl-create-run-review `
        --project-card .tmp/PROJECT_CARD.md `
        --output .tmp/RUN_REVIEW.md `
        --overwrite
    Invoke-Native pgl-promotion-candidates .tmp --output .tmp/PROMOTION_CANDIDATES.md --overwrite
    Invoke-Native pgl-update-promotion-log .tmp --log .tmp/PROMOTION_LOG.md --date 2026-01-01
    Invoke-Native pgl-github-issue-drafts .tmp --output .tmp/GITHUB_ISSUE_DRAFTS.md --overwrite
}

if ($PrivateDenylist) {
    Invoke-Step "Private denylist gate" {
        $denylistPath = (Resolve-Path -LiteralPath $PrivateDenylist).Path
        if ($denylistPath.StartsWith($RepoRoot + [IO.Path]::DirectorySeparatorChar)) {
            throw "Private denylist must be stored outside the repository: $denylistPath"
        }
        Invoke-Native pgl-pii-gate . --denylist $denylistPath
    }
}
else {
    Write-Host ""
    Write-Host "==> Private denylist gate skipped; pass -PrivateDenylist <path-outside-repo> for release."
}

Invoke-Step "Build Python package" { Invoke-Native python -m build }

Invoke-Step "Package template vault" {
    Compress-Archive -Path template-vault\* -DestinationPath dist\template-vault.zip -Force
}

Invoke-Step "Audit release artifacts" {
    @'
from pathlib import Path
import tarfile
import zipfile

artifacts = [
    Path("dist/personal_goal_loop-0.1.0.tar.gz"),
    Path("dist/personal_goal_loop-0.1.0-py3-none-any.whl"),
    Path("dist/template-vault.zip"),
]
for artifact in artifacts:
    if not artifact.exists():
        raise SystemExit(f"missing artifact: {artifact}")
    if artifact.name.endswith(".tar.gz"):
        with tarfile.open(artifact, "r:gz") as archive:
            names = archive.getnames()
    else:
        with zipfile.ZipFile(artifact) as archive:
            names = archive.namelist()
    flags = [
        name for name in names
        if any(token in name.lower() for token in [".xlsx", ".xlsm", "anonymize-report", ".env", "identity"])
    ]
    if flags:
        raise SystemExit(f"{artifact} contains blocked entries: {flags}")
    print(f"{artifact}: entries={len(names)}")
'@ | python -
    if ($LASTEXITCODE -ne 0) {
        throw "Release artifact audit failed."
    }
}

if ($KeepArtifacts) {
    Invoke-Step "Clean generated state except review artifacts" { Clear-GeneratedState -KeepReviewArtifacts }
}
else {
    Invoke-Step "Clean generated state" { Clear-GeneratedState }
}

Invoke-Step "Check generated workbook/report residue" { Assert-NoGeneratedWorkbookResidue }

Write-Host ""
Write-Host "Release preflight completed."
if ($KeepArtifacts) {
    Write-Host "Artifacts kept in dist/ and .tmp/ for review."
}
