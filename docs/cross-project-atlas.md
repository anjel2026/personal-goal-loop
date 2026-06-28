# Cross-Project Atlas

A Cross-Project Atlas turns scattered AI-assisted work into reusable workflow
knowledge. It is designed for users who keep raw work in a private vault and
promote only public-safe lessons into this repository.

## Purpose

Use the Atlas to answer:

- What have we already solved?
- Which workflow patterns are reusable?
- Which assets should become templates, rules, scripts, checklists, docs, or issues?
- Which details must stay private?

## Card Model

Each project card should separate private context from reusable knowledge.

Recommended fields:

- Safe project key.
- Domain.
- Status.
- Privacy level.
- Outcome.
- Artifacts.
- Reusable knowledge.
- Reusable assets.
- Risks and boundaries.
- Open questions.
- Promotion candidate type.

Use safe project keys such as `PGL-001`, `BUS-001`, `OCR-001`, `OPS-001`, or
`ATLAS-001`. Do not use real person names, organization names, or source file
names as card identifiers in public exports.

## Views

Useful Atlas views:

- Dashboard: current focus and project groups.
- Matrix: projects by domain, status, privacy, reusable asset, and next action.
- Reuse patterns: common rules discovered across projects.
- Promotion candidates: public-safe ideas ready for the repo.
- Unresolved questions: things that need a future pass.
- Privacy map: what stays private versus what can be exported.

## Promotion Rule

Promote the reusable pattern, not the raw source.

Good promotions:

- A generic checklist.
- A synthetic template.
- A script guardrail.
- A safety rule.
- A documentation page.
- A GitHub issue draft.

Bad promotions:

- Raw workbooks.
- Raw screenshots or images.
- Private local paths.
- Real identity maps.
- Business-specific content.
- Scan logs or danger-word lists.

## Safety Flow

1. Create or update a private Atlas card.
2. Extract a public-safe summary.
3. Place the summary in a shareable handoff folder.
4. Run a local safety scan.
5. Promote only generic assets into this repository.

## Template

Use `template-vault/60_Improvements/CROSS_PROJECT_ATLAS_CARD.md` as the public
card template.

