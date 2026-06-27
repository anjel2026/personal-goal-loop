# Public / Private Boundary

This repository must be useful without private data.

## Public

- package code
- synthetic workbook generator
- synthetic rules
- synthetic denylist
- tests
- CI
- docs
- template vault

## Private

- real workbooks
- real identity maps
- business-specific rules
- customer or employee data
- private notes
- original images and scans

## Safe Handoff

Safe handoff notes are the bridge between private work and reusable public
improvements. They may be shared only after sensitive values are replaced with
synthetic IDs and raw files are removed.

Use [safe-codex-handoff.md](safe-codex-handoff.md) and
[private-vault-operating-guide.md](private-vault-operating-guide.md) before
promoting private workflow lessons into the public repository.

## Release Rule

Before publishing, run:

```powershell
pgl-pii-gate .tmp/synthetic_timecard_anonymized.xlsx --denylist examples/denylist.synthetic.json
pgl-pii-gate .tmp/synthetic_timecard_anonymized.anonymize-report.json --denylist examples/denylist.synthetic.json
```

For a real release, maintain a private denylist outside this repository and scan the public tree with it:

```powershell
pgl-pii-gate . --denylist C:\path\to\private-denylist.json
```

If you intentionally scan the public tree with the synthetic denylist, exclude files that define the synthetic fixture values:

```powershell
pgl-pii-gate . --denylist examples/denylist.synthetic.json --exclude examples/** --exclude tests/**
```
