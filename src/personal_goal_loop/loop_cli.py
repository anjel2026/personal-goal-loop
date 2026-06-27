from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from personal_goal_loop.improvement_loop import (
    collect_promotion_candidates,
    create_project_card_from_intake,
    create_run_review,
    render_github_issue_drafts,
    render_promotion_candidates_json,
    render_promotion_candidates_markdown,
    update_promotion_log,
    write_text,
)


def create_project_card_main() -> int:
    parser = argparse.ArgumentParser(description="Create a project card from an intake note.")
    parser.add_argument("--intake", required=True, type=Path, help="Project intake Markdown file")
    parser.add_argument("--output", required=True, type=Path, help="Project card output path")
    parser.add_argument("--title", default="Untitled Project", help="Project title")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    args = parser.parse_args()

    intake_text = args.intake.expanduser().resolve().read_text(encoding="utf-8")
    card = create_project_card_from_intake(intake_text, title=args.title)
    write_text(args.output.expanduser().resolve(), card, overwrite=args.overwrite)
    print(str(args.output.expanduser().resolve()))
    return 0


def create_run_review_main() -> int:
    parser = argparse.ArgumentParser(description="Create a run review from a project card.")
    parser.add_argument("--project-card", required=True, type=Path, help="Project card Markdown file")
    parser.add_argument("--output", required=True, type=Path, help="Run review output path")
    parser.add_argument("--title", default="Run Review", help="Run review title")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    args = parser.parse_args()

    project_card_text = args.project_card.expanduser().resolve().read_text(encoding="utf-8")
    review = create_run_review(project_card_text, title=args.title)
    write_text(args.output.expanduser().resolve(), review, overwrite=args.overwrite)
    print(str(args.output.expanduser().resolve()))
    return 0


def promotion_candidates_main() -> int:
    parser = argparse.ArgumentParser(description="Collect promotion candidates from run reviews.")
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories to scan")
    parser.add_argument("--output", type=Path, help="Optional output path")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    args = parser.parse_args()

    candidates = collect_promotion_candidates(args.paths)
    rendered = (
        render_promotion_candidates_json(candidates)
        if args.json
        else render_promotion_candidates_markdown(candidates)
    )
    if args.output:
        write_text(args.output.expanduser().resolve(), rendered, overwrite=args.overwrite)
        print(str(args.output.expanduser().resolve()))
    else:
        print(rendered)
    return 0


def update_promotion_log_main() -> int:
    parser = argparse.ArgumentParser(description="Append promotion candidates to a Promotion Log.")
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories to scan")
    parser.add_argument("--log", required=True, type=Path, help="Promotion Log Markdown file")
    parser.add_argument("--date", default=date.today().isoformat(), help="Promotion row date")
    parser.add_argument("--status", default="candidate", help="Promotion row status")
    args = parser.parse_args()

    log_path = args.log.expanduser().resolve()
    log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    candidates = collect_promotion_candidates(args.paths)
    updated = update_promotion_log(log_text, candidates, date=args.date, status=args.status)
    write_text(log_path, updated, overwrite=True)
    print(str(log_path))
    return 0


def github_issue_drafts_main() -> int:
    parser = argparse.ArgumentParser(description="Render GitHub issue drafts from promotion candidates.")
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories to scan")
    parser.add_argument("--output", type=Path, help="Optional output path")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    args = parser.parse_args()

    candidates = collect_promotion_candidates(args.paths)
    rendered = render_github_issue_drafts(candidates)
    if args.output:
        write_text(args.output.expanduser().resolve(), rendered, overwrite=args.overwrite)
        print(str(args.output.expanduser().resolve()))
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(promotion_candidates_main())
