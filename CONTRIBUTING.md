# Contributing

## Ground Rules

- Use synthetic data only.
- Do not commit real workbooks, identity maps, business records, or private notes.
- Add or update tests for behavior changes.
- Update docs when a workflow or boundary changes.

## Pull Request Checklist

- `ruff check .`
- `mypy src`
- `pytest`
- synthetic anonymization run passes
- PII gate passes on generated anonymized output

## Promotion Rule

When a repeated manual step appears, propose whether it should become one of:

- template
- rule
- script
- checklist
- test

