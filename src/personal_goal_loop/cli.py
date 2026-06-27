from __future__ import annotations

import argparse
import json
from pathlib import Path

from personal_goal_loop.workbook_anonymizer import (
    anonymize_workbook,
    default_output_path,
    default_report_path,
    load_rules,
    write_report,
)


def anonymize_workbook_main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an anonymized copy of an Excel workbook without overwriting the source."
    )
    parser.add_argument("--input", required=True, type=Path, help="Source workbook path")
    parser.add_argument("--output", type=Path, help="Output workbook path")
    parser.add_argument("--rules", type=Path, help="JSON rules file")
    parser.add_argument("--report", type=Path, help="JSON report path")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute the anonymization summary without writing an output workbook",
    )
    parser.add_argument(
        "--include-sensitive-report",
        action="store_true",
        help="Include original paths and sheet names in the report. Use only in private runs.",
    )
    args = parser.parse_args()

    source_path = args.input.expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Input workbook does not exist: {source_path}")

    output_path = args.output.expanduser().resolve() if args.output else default_output_path(source_path)
    if output_path.exists() and not args.overwrite and not args.dry_run:
        raise FileExistsError(
            f"Output workbook already exists: {output_path} (use --overwrite to replace it)"
        )

    rules_path = args.rules.expanduser().resolve() if args.rules else None
    report_path = args.report.expanduser().resolve() if args.report else default_report_path(output_path)
    rules = load_rules(rules_path)
    summary = anonymize_workbook(
        source_path,
        output_path,
        rules,
        dry_run=args.dry_run,
        rules_path=rules_path,
    )
    write_report(summary, report_path, include_sensitive=args.include_sensitive_report)
    print(
        json.dumps(
            summary.to_dict(include_sensitive=args.include_sensitive_report),
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"Report written to: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(anonymize_workbook_main())
