# Local Safety Scan Checklist

Use this checklist before sending a private-vault handoff to Codex or promoting
an improvement into a public repository.

## Scope

- [ ] Scan target is a shareable folder.
- [ ] Private drafts are not being shared.
- [ ] Raw files are not in the scan target.

## Detection

- [ ] Email patterns checked.
- [ ] Phone number-like values checked.
- [ ] Local paths checked.
- [ ] Raw workbook, PDF, image, and screenshot files checked.
- [ ] Credential-like assignments checked.
- [ ] Private key blocks checked.
- [ ] Local danger words checked without exposing the danger-word list.

## Logs

- [ ] Logs are stored in a private vault.
- [ ] Logs use relative paths.
- [ ] Matched values are redacted.
- [ ] Logs are not committed to the public repository.

## Promotion

- [ ] The promoted artifact uses synthetic examples only.
- [ ] No private local paths are included.
- [ ] No raw files, images, screenshots, or private logs are included.
- [ ] The reusable lesson is separated from the private source material.

