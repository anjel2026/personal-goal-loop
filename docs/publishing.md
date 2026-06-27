# Publishing Guide

This project is designed to publish only reusable workflow assets. Real records, identity maps, private vault notes, and business-specific workbooks must remain outside the repository.

## Public Artifacts

- Python package: generic anonymizer, PII gate, and improvement-loop CLIs
- Synthetic fixtures and synthetic anonymization rules
- Documentation, CI workflows, and issue templates
- `template-vault.zip`: an Obsidian starter vault with no private notes

## Private Artifacts

- Real Excel workbooks
- Real identity maps or reversible pseudonym maps
- Business records, customer records, staff names, payroll data, or timecards
- Private Obsidian vaults and raw capture notes
- Local private denylist files used for final leak checks

## Local Preflight

Run this command from the repository root before pushing a release tag:

```powershell
.\scripts\release-preflight.ps1 -PrivateDenylist C:\path\to\private-denylist.json
```

Use `-KeepArtifacts` when you want to inspect `dist/` and `.tmp/` after the run. The private denylist path must be outside this repository.

The script runs the equivalent of:

```powershell
python -m pip install -e ".[dev]"
ruff check .
mypy src
pytest
python tests/fixtures/make_synthetic_workbook.py
pgl-anonymize-workbook `
  --input tests/fixtures/synthetic_timecard.xlsx `
  --output .tmp/synthetic_timecard_anonymized.xlsx `
  --rules examples/rules.synthetic.json `
  --overwrite
pgl-pii-gate .tmp/synthetic_timecard_anonymized.xlsx --denylist examples/denylist.synthetic.json
pgl-pii-gate .tmp/synthetic_timecard_anonymized.anonymize-report.json --denylist examples/denylist.synthetic.json
python -m build
Compress-Archive -Path template-vault\* -DestinationPath dist\template-vault.zip -Force
```

It also runs the improvement-loop smoke path:

```powershell
pgl-create-project-card
pgl-create-run-review
pgl-promotion-candidates
pgl-update-promotion-log
pgl-github-issue-drafts
```

If you need to run only the private leak scan, use a denylist stored outside this repo:

```powershell
pgl-pii-gate . --denylist C:\path\to\private-denylist.json
```

Do not commit the private denylist or its scan output if it contains sensitive matches.

The synthetic denylist is for generated anonymized outputs, not for an unfiltered full-tree scan, because `examples/` and `tests/` intentionally contain synthetic source values. If you still want a synthetic full-tree smoke test, exclude those fixture-definition paths:

```powershell
pgl-pii-gate . --denylist examples/denylist.synthetic.json --exclude examples/** --exclude tests/**
```

## GitHub Release Flow

1. Confirm `docs/release-checklist.md` is complete.
2. Confirm `git status --short` contains only intended public files.
3. Create a signed or normal tag such as `v0.1.0`.
4. Push the tag to trigger `.github/workflows/release.yml`.
5. Download the workflow artifacts and inspect the wheel, sdist, template vault zip, and synthetic anonymization report.
6. Draft GitHub release notes using the release checklist headings.

## PyPI

PyPI publishing is intentionally not automated in this repository yet. Add trusted publishing only after maintainers confirm the package name, release ownership, and incident-response process.
