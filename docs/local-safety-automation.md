# Local Safety Automation

Local safety automation is a pre-share gate for private vault workflows. It is
meant to run before a safe handoff is sent to Codex, GitHub, or another public
workflow.

The scanner itself can live in a private vault. This repository documents the
public-safe rules and templates, not private danger words or private scan logs.

## Recommended Targets

Scan only folders that are intended to become shareable:

- `50_Codex_Handoff/10_SAFE_TO_SHARE`
- `60_Improvements/Ready_for_OSS`

Do not scan or publish private drafts as a substitute for redaction. Drafts
should stay private.

## What To Detect

Use local checks for:

- Email addresses.
- Phone number-like values.
- Local paths.
- Raw workbook, PDF, image, and screenshot files.
- Credential-like assignments.
- Private key blocks.
- Locally configured danger words.

The danger-word list should be private. It can contain real names or business
terms, so it should not be committed or pasted into an AI chat.

## Logging Rule

Store scan results in the private vault, not in the public repository.

Good log content:

- Scan timestamp.
- Relative path inside the vault.
- Rule ID.
- Redacted finding value.
- Pass/fail count.

Do not log:

- Full private local paths.
- Unredacted matched values.
- Raw file content.
- Private danger-word lists.

## Exit Codes

A useful local scanner should return:

- `0` when no high-risk findings are present.
- `1` when high-risk findings are present.

This makes it easy to use the scanner before copying a handoff into Codex.

## Public-Ready Workflow

1. Draft privately.
2. Redact into a safe handoff.
3. Run a local safety scan.
4. Fix any findings.
5. Send only the safe handoff.
6. Record what was sent.
7. Promote only generic lessons into this repository.

## Template

Use `template-vault/60_Improvements/LOCAL_SAFETY_SCAN_CHECKLIST.md` before
promoting a private-vault lesson into a public artifact.

