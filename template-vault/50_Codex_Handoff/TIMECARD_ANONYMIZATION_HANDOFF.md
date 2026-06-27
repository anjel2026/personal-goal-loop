# Timecard Anonymization Handoff

## Purpose

Prepare an attendance or timecard workflow for AI-assisted work without sharing
raw private data.

## Source Policy

- Source file location: private only
- Share source file with Codex: No
- Overwrite source file: No

## Synthetic Replacement Plan

| Source type | Replacement |
|---|---|
| Person name | P001 |
| Organization or location | ORG001 |
| Employee ID | EMP001 |
| Contact information | `[redacted-contact]` |
| Private path | `[private-path]` |

## Shareable Artifacts

- Anonymized workbook:
- Anonymization report:
- Verification log:

## Stop Rules

- [ ] Stop if only the raw source file exists.
- [ ] Stop if the anonymization report is missing.
- [ ] Stop if real names remain.
- [ ] Stop if output path equals source path.

## Codex Request

```text
Use only the anonymized workbook, anonymization report, and verification log.
Do not open or modify the raw source file. Do not attempt to recover real
identities. Produce a separate output and explain the verification steps.
```

