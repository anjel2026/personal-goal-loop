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

function Remove-RepoPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if (-not ($resolved.StartsWith($RepoRoot + [IO.Path]::DirectorySeparatorChar))) {
        throw "Refusing to remove outside repository: $resolved"
    }

    Remove-Item -LiteralPath $resolved -Recurse -Force
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
    $residue = Get-ChildItem -Recurse -File -Include *.xlsx,*.xlsm,*.anonymize-report.json |
        Where-Object { $_.FullName -notlike "*\.tmp\*" }

    if ($residue) {
        $paths = ($residue | Select-Object -ExpandProperty FullName) -join [Environment]::NewLine
        throw "Generated workbook/report residue found outside .tmp:$([Environment]::NewLine)$paths"
    }
}

Invoke-Step "Clean previous generated state" { Clear-GeneratedState }

if (-not $SkipInstall) {
    Invoke-Step "Install package with dev dependencies" {
        python -m pip install -e ".[dev]"
    }
}

Invoke-Step "Lint" { python -m ruff check . }
Invoke-Step "Type check" { python -m mypy src }
Invoke-Step "Tests" { python -m pytest }

Invoke-Step "Generate synthetic workbook" {
    python tests/fixtures/make_synthetic_workbook.py
}

Invoke-Step "Anonymizer dry run" {
    pgl-anonymize-workbook `
        --input tests/fixtures/synthetic_timecard.xlsx `
        --output .tmp/synthetic_timecard_anonymized.xlsx `
        --rules examples/rules.synthetic.json `
        --dry-run
}

Invoke-Step "Anonymize synthetic workbook" {
    pgl-anonymize-workbook `
        --input tests/fixtures/synthetic_timecard.xlsx `
        --output .tmp/synthetic_timecard_anonymized.xlsx `
        --rules examples/rules.synthetic.json `
        --overwrite
}

Invoke-Step "Synthetic output PII gate" {
    pgl-pii-gate .tmp/synthetic_timecard_anonymized.xlsx --denylist examples/denylist.synthetic.json
    pgl-pii-gate .tmp/synthetic_timecard_anonymized.anonymize-report.json --denylist examples/denylist.synthetic.json
}

Invoke-Step "Synthetic full-tree smoke gate" {
    pgl-pii-gate . --denylist examples/denylist.synthetic.json --exclude examples/** --exclude tests/**
}

Invoke-Step "Improvement loop smoke test" {
    pgl-create-project-card `
        --intake template-vault/00_Inbox/Project_Intake.md `
        --output .tmp/PROJECT_CARD.md `
        --title "Synthetic Fixture Work" `
        --overwrite
    pgl-create-run-review `
        --project-card .tmp/PROJECT_CARD.md `
        --output .tmp/RUN_REVIEW.md `
        --overwrite
    pgl-promotion-candidates .tmp --output .tmp/PROMOTION_CANDIDATES.md --overwrite
    pgl-update-promotion-log .tmp --log .tmp/PROMOTION_LOG.md --date 2026-01-01
    pgl-github-issue-drafts .tmp --output .tmp/GITHUB_ISSUE_DRAFTS.md --overwrite
}

if ($PrivateDenylist) {
    Invoke-Step "Private denylist gate" {
        $denylistPath = (Resolve-Path -LiteralPath $PrivateDenylist).Path
        if ($denylistPath.StartsWith($RepoRoot + [IO.Path]::DirectorySeparatorChar)) {
            throw "Private denylist must be stored outside the repository: $denylistPath"
        }
        pgl-pii-gate . --denylist $denylistPath
    }
}
else {
    Write-Host ""
    Write-Host "==> Private denylist gate skipped; pass -PrivateDenylist <path-outside-repo> for release."
}

Invoke-Step "Build Python package" { python -m build }

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
