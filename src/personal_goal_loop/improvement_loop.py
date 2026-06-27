from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


FIELD_RE = re.compile(r"^\s*-\s*([^:]+):\s*(.*)$")


@dataclass(frozen=True)
class PromotionCandidate:
    source_path: str
    promotion_type: str
    value: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source_path": self.source_path,
            "promotion_type": self.promotion_type,
            "value": self.value,
        }


def create_project_card_from_intake(
    intake_text: str,
    *,
    title: str = "Untitled Project",
) -> str:
    fields = parse_markdown_fields(intake_text)
    request = fields.get("request", "")
    desired_output = fields.get("desired_output", "")
    sensitive_data = fields.get("sensitive_data_present", "unknown")
    needs_anonymization = fields.get("needs_anonymization", "")

    outcome = desired_output or request or "-"
    risk_lines = [
        f"- Sensitive data present: {sensitive_data or 'unknown'}",
        f"- Needs anonymization: {needs_anonymization or 'unknown'}",
    ]

    return "\n".join(
        [
            "---",
            "type: project_card",
            "status: active",
            "---",
            "",
            f"# Project Card: {title}",
            "",
            "## Outcome",
            "",
            f"- {outcome}",
            "",
            "## Boundary",
            "",
            f"- In scope: {request or '-'}",
            "- Out of scope: -",
            f"- Private data: {fields.get('private', '-') or '-'}",
            f"- Public-safe artifacts: {fields.get('public_safe', '-') or '-'}",
            "",
            "## Success Criteria",
            "",
            f"- Desired output: {desired_output or '-'}",
            f"- Next action: {extract_next_action(intake_text) or '-'}",
            "",
            "## Risks",
            "",
            *risk_lines,
            "",
            "## Reusable Assets",
            "",
            "- Templates: -",
            "- Rules: -",
            "- Scripts: -",
            "- Checklists: -",
            "",
            "## Source Capture",
            "",
            f"- Date: {fields.get('date', '-') or '-'}",
            f"- Source: {fields.get('source', '-') or '-'}",
            f"- Inputs: {fields.get('inputs', '-') or '-'}",
            f"- Constraints: {fields.get('constraints', '-') or '-'}",
            "",
        ]
    )


def create_run_review(
    project_card_text: str,
    *,
    title: str = "Run Review",
) -> str:
    project_title = extract_heading(project_card_text) or "Project Card"
    return "\n".join(
        [
            "---",
            "type: run_review",
            "status: draft",
            "---",
            "",
            f"# {title}",
            "",
            "## Evaluate",
            "",
            f"- Reviewed artifact: {project_title}",
            "- What worked: -",
            "- What failed: -",
            "- What was missing: -",
            "- What was reused: -",
            "- What should change next time: -",
            "",
            "## Promote",
            "",
            "- Promote to template: -",
            "- Promote to rule: -",
            "- Promote to script: -",
            "- Promote to checklist: -",
            "- Archive: -",
            "",
        ]
    )


def parse_markdown_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = FIELD_RE.match(line)
        if match is None:
            continue
        label = normalize_label(match.group(1))
        fields[label] = clean_field_value(match.group(2))
    return fields


def extract_next_action(text: str) -> str:
    in_next_action = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_next_action = normalize_label(stripped.removeprefix("## ")) == "next_action"
            continue
        if in_next_action and stripped.startswith("-"):
            value = stripped.lstrip("-").strip()
            if value:
                return value
    return ""


def extract_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.removeprefix("# ").strip()
    return ""


def collect_promotion_candidates(paths: Iterable[Path]) -> list[PromotionCandidate]:
    candidates: list[PromotionCandidate] = []
    for file_path in iter_markdown_files(paths):
        text = file_path.read_text(encoding="utf-8")
        fields = parse_markdown_fields(text)
        for field_name, promotion_type in [
            ("promote_to_template", "template"),
            ("promote_to_rule", "rule"),
            ("promote_to_script", "script"),
            ("promote_to_checklist", "checklist"),
        ]:
            value = fields.get(field_name, "").strip()
            if is_meaningful_value(value):
                candidates.append(
                    PromotionCandidate(
                        source_path=safe_display_path(file_path),
                        promotion_type=promotion_type,
                        value=value,
                    )
                )
    return candidates


def render_promotion_candidates_markdown(candidates: list[PromotionCandidate]) -> str:
    lines = [
        "# Promotion Candidates",
        "",
        "| Type | Value | Source |",
        "|---|---|---|",
    ]
    if not candidates:
        lines.append("| - | - | - |")
    for candidate in candidates:
        lines.append(
            f"| {escape_table_cell(candidate.promotion_type)} | "
            f"{escape_table_cell(candidate.value)} | "
            f"{escape_table_cell(candidate.source_path)} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_promotion_candidates_json(candidates: list[PromotionCandidate]) -> str:
    return json.dumps([candidate.to_dict() for candidate in candidates], ensure_ascii=False, indent=2)


def update_promotion_log(
    log_text: str,
    candidates: list[PromotionCandidate],
    *,
    date: str,
    status: str = "candidate",
) -> str:
    lines = log_text.rstrip().splitlines()
    if not lines:
        lines = [
            "# Promotion Log",
            "",
            "| Date | Artifact | Type | Reason | Status |",
            "|---|---|---|---|---|",
        ]

    existing_rows = set(lines)
    for candidate in candidates:
        row = (
            f"| {escape_table_cell(date)} | "
            f"{escape_table_cell(candidate.value)} | "
            f"{escape_table_cell(candidate.promotion_type)} | "
            f"{escape_table_cell(candidate.source_path)} | "
            f"{escape_table_cell(status)} |"
        )
        if row not in existing_rows:
            lines.append(row)
            existing_rows.add(row)
    lines.append("")
    return "\n".join(lines)


def render_github_issue_drafts(candidates: list[PromotionCandidate]) -> str:
    lines = ["# GitHub Issue Drafts", ""]
    if not candidates:
        lines.extend(["No promotion candidates found.", ""])
        return "\n".join(lines)

    for index, candidate in enumerate(candidates, start=1):
        title = f"[Idea]: Promote {candidate.promotion_type}: {candidate.value}"
        lines.extend(
            [
                f"## Issue {index}",
                "",
                f"Title: {title}",
                "",
                "### Capture",
                "",
                f"- Source: {candidate.source_path}",
                f"- Observation: {candidate.value}",
                "",
                "### Synthesis",
                "",
                f"- Candidate should become a reusable {candidate.promotion_type}.",
                "",
                "### Promotion target",
                "",
                f"- {candidate.promotion_type}",
                "",
                "### Privacy notes",
                "",
                "- Uses public-safe or synthetic context only. Do not attach private data.",
                "",
            ]
        )
    return "\n".join(lines)


def iter_markdown_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved.is_dir():
            for file_path in sorted(resolved.rglob("*.md")):
                if file_path.is_file():
                    yield file_path
        elif resolved.is_file() and resolved.suffix.lower() == ".md":
            yield resolved


def write_text(path: Path, text: str, *, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists: {path} (use --overwrite to replace it)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_label(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z]+", "_", value.strip().lower())
    return normalized.strip("_")


def is_meaningful_value(value: str) -> bool:
    return bool(value and value not in {"-", "none", "n/a", "N/A"})


def clean_field_value(value: str) -> str:
    stripped = value.strip()
    if stripped in {"", "-", "yes / no / unknown"}:
        return ""
    return stripped


def safe_display_path(path: Path) -> str:
    resolved = path.expanduser().resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return resolved.name


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def candidates_to_dicts(candidates: list[PromotionCandidate]) -> list[dict[str, Any]]:
    return [candidate.to_dict() for candidate in candidates]
