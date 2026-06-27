from __future__ import annotations

import json
from pathlib import Path

from personal_goal_loop.improvement_loop import (
    collect_promotion_candidates,
    create_project_card_from_intake,
    create_run_review,
    parse_markdown_fields,
    render_github_issue_drafts,
    render_promotion_candidates_json,
    render_promotion_candidates_markdown,
    update_promotion_log,
    write_text,
)


INTAKE = """# Project Intake

## Capture

- Date: 2026-01-01
- Request: Build a repeatable synthetic workbook check
- Source: issue
- Inputs: synthetic fixture
- Constraints: public data only
- Sensitive data present: no
- Desired output: CI-ready validation path

## Initial Boundary

- Public-safe: tests and docs
- Private: none
- Needs anonymization: no

## Next Action

- Create tests and promotion review
"""


def test_parse_markdown_fields_normalizes_labels() -> None:
    fields = parse_markdown_fields(INTAKE)
    assert fields["desired_output"] == "CI-ready validation path"
    assert fields["sensitive_data_present"] == "no"
    assert fields["public_safe"] == "tests and docs"


def test_create_project_card_from_intake() -> None:
    card = create_project_card_from_intake(INTAKE, title="Synthetic Checks")
    assert "# Project Card: Synthetic Checks" in card
    assert "- CI-ready validation path" in card
    assert "- In scope: Build a repeatable synthetic workbook check" in card
    assert "- Next action: Create tests and promotion review" in card
    assert "- Sensitive data present: no" in card


def test_create_run_review_from_project_card() -> None:
    card = create_project_card_from_intake(INTAKE, title="Synthetic Checks")
    review = create_run_review(card, title="Synthetic Check Review")
    assert "# Synthetic Check Review" in review
    assert "- Reviewed artifact: Project Card: Synthetic Checks" in review
    assert "- Promote to test: " not in review
    assert "- Promote to checklist: -" in review


def test_collect_promotion_candidates(tmp_path: Path) -> None:
    review = tmp_path / "RUN_REVIEW.md"
    review.write_text(
        """# Run Review

## Promote

- Promote to template: Project card for public fixtures
- Promote to rule: public data only
- Promote to script: -
- Promote to checklist: release privacy check
- Archive: -
""",
        encoding="utf-8",
    )

    candidates = collect_promotion_candidates([tmp_path])
    assert [candidate.promotion_type for candidate in candidates] == [
        "template",
        "rule",
        "checklist",
    ]
    assert candidates[0].source_path == "RUN_REVIEW.md"
    markdown = render_promotion_candidates_markdown(candidates)
    assert "| template | Project card for public fixtures |" in markdown
    payload = json.loads(render_promotion_candidates_json(candidates))
    assert payload[0]["promotion_type"] == "template"


def test_update_promotion_log_appends_candidates_once(tmp_path: Path) -> None:
    review = tmp_path / "RUN_REVIEW.md"
    review.write_text(
        """# Run Review

## Promote

- Promote to template: Project card for public fixtures
- Promote to rule: public data only
""",
        encoding="utf-8",
    )
    candidates = collect_promotion_candidates([tmp_path])
    log = """# Promotion Log

| Date | Artifact | Type | Reason | Status |
|---|---|---|---|---|
"""

    updated_once = update_promotion_log(log, candidates, date="2026-01-02")
    updated_twice = update_promotion_log(updated_once, candidates, date="2026-01-02")

    assert updated_once == updated_twice
    assert "| 2026-01-02 | Project card for public fixtures | template |" in updated_once
    assert "| 2026-01-02 | public data only | rule |" in updated_once


def test_render_github_issue_drafts(tmp_path: Path) -> None:
    review = tmp_path / "RUN_REVIEW.md"
    review.write_text(
        """# Run Review

## Promote

- Promote to checklist: release privacy check
""",
        encoding="utf-8",
    )
    candidates = collect_promotion_candidates([tmp_path])
    draft = render_github_issue_drafts(candidates)

    assert "Title: [Idea]: Promote checklist: release privacy check" in draft
    assert f"{tmp_path}" not in draft
    assert "### Capture" in draft
    assert "### Synthesis" in draft
    assert "### Privacy notes" in draft


def test_write_text_refuses_overwrite_by_default(tmp_path: Path) -> None:
    output = tmp_path / "PROJECT_CARD.md"
    write_text(output, "first")
    try:
        write_text(output, "second")
    except FileExistsError as exc:
        assert "use --overwrite" in str(exc)
    else:
        raise AssertionError("write_text should refuse overwrite by default")

    write_text(output, "second", overwrite=True)
    assert output.read_text(encoding="utf-8") == "second"
