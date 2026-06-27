# Improvement Loop

The loop exists to make every project run produce better future project runs.

## Stages

1. Capture
   Record the request, context, inputs, constraints, and risk.

2. Synthesize
   Convert messy context into a project card with outcome, boundary, success criteria, and next action.

3. Evaluate
   After the run, record what worked, what failed, what was missing, and what was reused.

4. Promote
   Promote repeated useful ideas into a template, rule, script, checklist, or test.

5. Reuse
   Start the next project from promoted assets instead of starting from memory or chat history.

## Promotion Rule

Promote an artifact when it is useful in at least two runs or prevents a high-impact failure once.

Archive it when it is too specific, confusing, or not reused after review.

## Private-To-Public Promotion

Private vault material should not be promoted directly. Promote only the
reusable lesson that can survive without the private source.

Use this sequence:

1. Draft privately.
2. Create a safe handoff with synthetic identifiers.
3. Record what was sent to Codex.
4. Extract the reusable improvement.
5. Run the promotion gate.
6. Convert the result into a template, rule, script, checklist, doc, or issue draft.

See also:

- [Private Vault Operating Guide](private-vault-operating-guide.md)
- [Safe Codex Handoff](safe-codex-handoff.md)
- `template-vault/60_Improvements/IMPROVEMENT_PROMOTION_GATE.md`

## CLI Workflow

```powershell
pgl-create-project-card --intake template-vault/00_Inbox/Project_Intake.md --output .tmp/PROJECT_CARD.md --title "Example"
pgl-create-run-review --project-card .tmp/PROJECT_CARD.md --output .tmp/RUN_REVIEW.md
pgl-promotion-candidates .tmp --output .tmp/PROMOTION_CANDIDATES.md
pgl-update-promotion-log .tmp --log .tmp/PROMOTION_LOG.md --date 2026-01-01
pgl-github-issue-drafts .tmp --output .tmp/GITHUB_ISSUE_DRAFTS.md
```

The generated promotion candidates are meant to feed GitHub issues, PR descriptions, or an Obsidian promotion log.
