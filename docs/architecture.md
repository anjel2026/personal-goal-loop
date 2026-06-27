# Architecture

Personal Goal Loop has two public surfaces:

- a privacy toolchain that can be tested without private data
- a project improvement loop that turns repeated work into reusable assets

## Public Tree

```text
src/                  reusable package code
examples/             synthetic rules and denylist examples
tests/                generated synthetic fixture tests
template-vault/       Obsidian-ready public templates
docs/                 public operating model
.github/workflows/    reproducible checks
```

## Private Tree

Real operational data belongs outside this repository:

- raw workbooks
- identity maps
- business records
- private Obsidian notes
- user-specific rules

## Quality Gates

Every public change should pass:

- lint
- type check
- unit tests
- synthetic workbook anonymization
- dry-run receipt generation
- PII leak gate against the anonymized synthetic output
- PII leak gate against the default anonymization report
- project-card and run-review generation from public-safe Markdown templates
- promotion log update and GitHub issue draft generation from promotion candidates
