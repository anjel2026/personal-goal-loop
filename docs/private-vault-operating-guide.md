# Private Vault Operating Guide

Personal Goal Loop can be used with a private Obsidian vault, but the public
repository must never become the place where raw private material is stored.

This guide describes a safe operating pattern:

```text
private raw material -> safe handoff -> reusable improvement -> public artifact
```

## Vault Zones

Use separate locations for each risk level.

| Zone | Purpose | Share with Codex or GitHub |
|---|---|---|
| Private drafts | Raw notes, source files, screenshots, images, workbook originals | No |
| Safe handoff | Sanitized summaries, synthetic IDs, task instructions | Yes, after review |
| Improvements | Public-ready templates, rules, checklists, docs, issue drafts | Yes |

## Capture

Capture raw thoughts quickly, but keep them in a private-only area. Raw files
can include workbook originals, screenshots, images, identifiers, business
context, and personal notes. Do not move those files into this repository.

## Safe Handoff

Before asking an AI assistant to work on a sensitive workflow, create a safe
handoff note.

Safe handoff notes should include:

- The task outcome.
- The sanitized structure of the input.
- Synthetic identifiers such as `P001`, `ORG001`, and `EMP001`.
- The expected output.
- Stop rules, especially "do not use raw files" and "do not overwrite source files".

Safe handoff notes should not include:

- Real names, addresses, emails, or phone numbers.
- Real organization, store, department, or customer names.
- Raw workbooks, PDFs, screenshots, or images.
- Private local paths.
- Credentials, tokens, keys, or secrets.

## Promote

Promote only reusable, public-safe artifacts.

Good promotion candidates:

- A generic Markdown template.
- A synthetic fixture.
- A denylist pattern.
- A release checklist item.
- A script guardrail.
- A GitHub issue draft.

Do not promote the raw material that produced the insight.

## Weekly Review

Once a week, review private notes for reusable improvements:

1. Choose one workflow that was repeated or risky.
2. Remove private context and replace identifiers with synthetic IDs.
3. Convert the lesson into a template, rule, script, checklist, doc, or issue draft.
4. Run the promotion gate before opening a public issue or PR.

## Public-Ready Checklist

- [ ] No identity data.
- [ ] No business-specific data.
- [ ] No raw files or screenshots.
- [ ] No images.
- [ ] No private local paths.
- [ ] No credentials, tokens, keys, or secrets.
- [ ] Synthetic examples only.
- [ ] Clear acceptance criteria.

