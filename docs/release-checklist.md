# Release Checklist

## Required

- Run `ruff check .`
- Run `mypy src`
- Run `pytest`
- Run `.\scripts\release-preflight.ps1 -PrivateDenylist C:\path\to\private-denylist.json`
- Run `python -m build`
- Generate `dist/template-vault.zip`
- Generate the synthetic workbook
- Run anonymization in dry-run mode and review the receipt fields
- Run anonymization on the synthetic workbook
- Run `pgl-pii-gate` on the anonymized synthetic workbook
- Run `pgl-pii-gate` on the default anonymization report
- Do not use `--include-sensitive-report` for public artifacts
- Scan the public tree with a private denylist kept outside the repo
- Confirm no real workbook, identity map, business note, or private vault content is tracked
- Confirm release artifacts contain only package files, synthetic reports, and the public template vault
- Confirm PyPI publishing remains manual unless maintainers explicitly enable trusted publishing

## Release Notes

Every release note should include:

- behavior changes
- privacy boundary changes
- new promoted templates, rules, scripts, checklists, or tests
- known limitations
