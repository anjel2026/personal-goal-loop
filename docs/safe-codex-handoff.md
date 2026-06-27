# Safe Codex Handoff

A safe handoff is the public-safe bridge between private work and an AI-assisted
task. It should be specific enough to be useful, but sanitized enough to share.

## Minimum Shape

```markdown
# Codex Safe Handoff

## Task

Describe the requested outcome.

## Safe Context

- People are replaced with `P001`, `P002`.
- Organizations are replaced with `ORG001`.
- Source files are described structurally, not attached.

## Do Not Share

- Raw files.
- Real identity data.
- Business-specific data.
- Images or screenshots.
- Private local paths.
- Credentials.

## Success Criteria

- The output is public-safe.
- The source file is not overwritten.
- The result can be verified.
```

## Workflow

1. Draft privately.
2. Replace sensitive values with synthetic IDs.
3. Remove raw files, images, screenshots, and local paths.
4. Check the safe-share checklist.
5. Send only the safe handoff text.
6. Record what was sent.
7. Promote reusable improvements through the improvement gate.

## Stop Rules

Stop before sharing if the handoff contains any of these:

- A real person, organization, or account identifier.
- A raw workbook, PDF, image, screenshot, or export.
- A private file path.
- A credential, token, key, or secret.
- Enough context to reconstruct private data.

## Template Pack

The public template vault includes:

- `template-vault/50_Codex_Handoff/CODEX_SAFE_HANDOFF.md`
- `template-vault/50_Codex_Handoff/SAFE_SHARE_CHECKLIST.md`
- `template-vault/50_Codex_Handoff/SENT_TO_CODEX_LOG.md`
- `template-vault/50_Codex_Handoff/TIMECARD_ANONYMIZATION_HANDOFF.md`
- `template-vault/60_Improvements/IMPROVEMENT_PROMOTION_GATE.md`

