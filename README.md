# Personal Goal Loop

Personal Goal Loop is an OSS-ready toolkit for turning repeated AI-assisted work into reusable project knowledge.

The repository is intentionally split into public-safe assets and private operational data:

- public: anonymizer code, synthetic fixtures, leak gates, CI, docs, and template vault notes
- private: real workbooks, identity maps, business records, personal notes, and private Obsidian vaults

## Core Loop

```text
capture -> synthesize -> evaluate -> promote -> reuse
```

Each run should leave behind a small artifact that can be reviewed, rejected, or promoted into a reusable template, rule, script, or checklist.

## Initial Tools

- `pgl-anonymize-workbook`: create an anonymized copy of an Excel workbook
- `pgl-pii-gate`: fail when configured sensitive tokens remain in text or workbook files, with repeatable `--exclude` rules for fixture-heavy repos
- `pgl-create-project-card`: synthesize an Obsidian intake note into a project card
- `pgl-create-run-review`: create a review note from a project card
- `pgl-promotion-candidates`: collect reusable template/rule/script/checklist candidates
- `pgl-update-promotion-log`: update a durable promotion log from reviewed run notes
- `pgl-github-issue-drafts`: turn promotion candidates into copy-pasteable GitHub issue drafts
- `template-vault/`: Obsidian-ready notes for project intake and post-run review

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest
```

Run the synthetic workbook path:

```powershell
python tests/fixtures/make_synthetic_workbook.py
pgl-anonymize-workbook `
  --input tests/fixtures/synthetic_timecard.xlsx `
  --output .tmp/synthetic_timecard_anonymized.xlsx `
  --rules examples/rules.synthetic.json `
  --dry-run

pgl-anonymize-workbook `
  --input tests/fixtures/synthetic_timecard.xlsx `
  --output .tmp/synthetic_timecard_anonymized.xlsx `
  --rules examples/rules.synthetic.json `
  --overwrite
```

The anonymization report includes source, output, and rules SHA-256 values so a run can be audited later.
Original paths and sheet names are redacted from reports by default. Use `--include-sensitive-report` only for private local runs.

Run the improvement loop path:

```powershell
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

pgl-update-promotion-log `
  .tmp `
  --log .tmp/PROMOTION_LOG.md `
  --date 2026-01-01

pgl-github-issue-drafts .tmp --output .tmp/GITHUB_ISSUE_DRAFTS.md --overwrite
```

## Publishing

Use [docs/publishing.md](docs/publishing.md) and [docs/release-checklist.md](docs/release-checklist.md) before pushing tags or creating GitHub releases. Release artifacts are built locally and in GitHub Actions; PyPI publishing is intentionally manual for now.

For local release verification:

```powershell
.\scripts\release-preflight.ps1 -PrivateDenylist C:\path\to\private-denylist.json
```

Use `-KeepArtifacts` when you want to inspect `dist/` and `.tmp/` after the run.

## Non-Goals

- This repo does not store real identity maps.
- This repo does not publish private vault contents.
- This repo does not guarantee legal compliance by itself. Treat it as a verifiable workflow layer.
