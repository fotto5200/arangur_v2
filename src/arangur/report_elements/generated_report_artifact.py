"""Generated report artifact model for the synthetic private demo path."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .briefing_set_preview import (
    build_default_advisor_review_set_preview,
    build_default_client_briefing_set_preview,
    load_report_element_views,
)


ARTIFACT_SCHEMA_VERSION = "generated_report_artifact.v1"
ARTIFACT_INDEX_SCHEMA_VERSION = "generated_report_artifact_index.v1"
ARTIFACT_BUILDER_VERSION = "generated_report_artifact_builder.v1"
GENERATED_AT = "2026-06-30T00:00:00Z"
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views")
DEFAULT_OUTPUT_DIR = Path("data/simulation/generated_reports")

REPORT_TYPES = {"client_briefing", "advisor_review"}
PREVIEW_TO_REPORT_TYPE = {
    "client_briefing_set": "client_briefing",
    "advisor_review_set": "advisor_review",
}
REPORT_TYPE_TITLES = {
    "client_briefing": "Client Briefing",
    "advisor_review": "Advisor Review",
}
ANALYTIC_SECTION_TITLES = {
    "portfolio_status": "Portfolio Status",
    "cash_generation_summary": "Cash & Liquidity",
    "concentration": {
        "client_briefing": "Concentration Watch",
        "advisor_review": "Concentration Diagnostic",
    },
    "scenario_impact_by_manager": "Scenario Sensitivity",
    "data_confidence_note": "Data Confidence",
    "manager_comparison": "Manager Role Review",
}
SECTION_TYPES = {"narrative", "report_element", "unsupported", "caveat"}
SECTION_STATUSES = {"rendered", "placeholder", "omitted", "unsupported"}
RENDER_STATUSES = {"complete", "partial", "demo_partial"}

REAL_DATA_MARKERS = {
    "access_token",
    "api key",
    "bearer ",
    "bloomberg",
    "client_secret",
    "factset",
    "private key",
    "refinitiv",
}
EXTERNAL_API_MARKERS = {
    "httpx",
    "requests.",
    "urllib.request",
    "plaid",
}
DEVELOPER_ERROR_MARKERS = {
    "debug artifact",
    "exception",
    "stack trace",
    "traceback",
}


def create_demo_generated_report_artifact(
    report_type: str,
    view_dir: str | Path = DEFAULT_VIEW_DIR,
) -> dict[str, Any]:
    """Create a deterministic demo generated-report artifact from committed preview inputs."""

    views = load_report_element_views(view_dir)
    if report_type == "client_briefing":
        preview = build_default_client_briefing_set_preview(views)
    elif report_type == "advisor_review":
        preview = build_default_advisor_review_set_preview(views)
    else:
        raise ValueError(f"Unsupported generated report type: {report_type}")
    return build_generated_report_artifact_from_briefing_preview(preview, report_type=report_type)


def build_generated_report_artifact_from_briefing_preview(
    preview_payload: dict[str, Any],
    report_type: str | None = None,
    source_workflow_id: str | None = None,
    source_workflow_display_name: str | None = None,
    report_id: str | None = None,
    report_title: str | None = None,
    app_environment: str = "private_demo",
    runtime_mode: str = "private_demo",
) -> dict[str, Any]:
    """Convert a briefing-set preview payload into a generated report artifact."""

    resolved_report_type = report_type or PREVIEW_TO_REPORT_TYPE.get(str(preview_payload.get("preview_type")))
    if resolved_report_type not in REPORT_TYPES:
        raise ValueError(f"Unsupported generated report type: {resolved_report_type}")

    context = preview_payload.get("client_or_portfolio_context", {})
    data_as_of = _clean_string(context.get("as_of_date")) or "unknown"
    data_snapshot_label = _clean_string(context.get("portfolio_label")) or "Synthetic demo data snapshot"
    resolved_report_title = _clean_optional_string(report_title) or _report_title(resolved_report_type, data_as_of)
    resolved_report_id = report_id or f"demo_{resolved_report_type}_{data_as_of.replace('-', '')}"
    workflow_display_name = source_workflow_display_name or f"Default demo {REPORT_TYPE_TITLES[resolved_report_type]} Workflow"

    sections: list[dict[str, Any]] = []
    unsupported_sections: list[dict[str, Any]] = []
    sections.append(_narrative_section(resolved_report_type, 1, "opening", *_opening_framing(resolved_report_type)))
    for element in preview_payload.get("ordered_elements", []):
        section = _section_from_preview_element(element, len(sections) + 1, resolved_report_type)
        sections.append(section)
        if section["status"] in {"placeholder", "unsupported"}:
            unsupported_sections.append(
                {
                    "section_id": section["section_id"],
                    "title": section["title"],
                    "status": section["status"],
                    "source_element_id": section.get("source_element_id"),
                    "source_element_title": section.get("source_element_title"),
                }
            )

    sections.append(_narrative_section(resolved_report_type, len(sections) + 1, "discussion_prompts", *_closing_prompts(resolved_report_type)))

    artifact_caveats = _artifact_caveats(preview_payload.get("caveats", []))
    caveat_section = _caveat_section(artifact_caveats, len(sections) + 1)
    sections.append(caveat_section)

    text_content = _render_artifact_text(resolved_report_title, preview_payload, sections, data_as_of, data_snapshot_label)
    html_content = _render_artifact_html(resolved_report_title, preview_payload, sections, data_as_of, data_snapshot_label)
    artifact = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "builder_version": ARTIFACT_BUILDER_VERSION,
        "report_id": resolved_report_id,
        "report_type": resolved_report_type,
        "source_workflow_id": source_workflow_id,
        "source_workflow_display_name": workflow_display_name,
        "source_preview_id": preview_payload.get("preview_id"),
        "report_title": resolved_report_title,
        "generated_at": preview_payload.get("generated_at") or GENERATED_AT,
        "data_as_of": data_as_of,
        "data_snapshot_label": data_snapshot_label,
        "synthetic_data": True,
        "app_environment": app_environment,
        "runtime_mode": runtime_mode,
        "ordered_sections": sections,
        "unsupported_sections": unsupported_sections,
        "caveats": artifact_caveats,
        "render_status": "demo_partial",
        "text_content": text_content,
        "html_content": html_content,
        "metadata_json": {
            "source_preview_type": preview_payload.get("preview_type"),
            "included_element_ids": list(preview_payload.get("included_element_ids", [])),
            "section_count": len(sections),
            "unsupported_section_count": len(unsupported_sections),
            "confidence_summary": preview_payload.get("confidence_summary", {}),
            "demo_caveat": artifact_caveats[0],
        },
        "summary": {
            "report_type_label": REPORT_TYPE_TITLES[resolved_report_type],
            "section_count": len(sections),
            "data_snapshot_label": data_snapshot_label,
            "synthetic_data": True,
        },
    }
    artifact["validation"] = validate_generated_report_artifact(artifact)
    return artifact


def validate_generated_report_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate the generated-report artifact contract without external services."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(artifact, dict):
        return {
            "status": "invalid",
            "errors": [{"code": "ARTIFACT_NOT_OBJECT", "record_id": "artifact", "message": "Artifact must be a JSON object."}],
            "warnings": [],
        }
    for field in (
        "schema_version",
        "report_id",
        "report_type",
        "source_workflow_id",
        "source_workflow_display_name",
        "report_title",
        "generated_at",
        "data_as_of",
        "data_snapshot_label",
        "synthetic_data",
        "ordered_sections",
        "unsupported_sections",
        "render_status",
        "text_content",
        "html_content",
        "metadata_json",
    ):
        if field not in artifact:
            _add_issue(errors, "MISSING_FIELD", field, f"Missing required field: {field}")
    if artifact.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
        _add_issue(errors, "SCHEMA_VERSION_MISMATCH", "schema_version", f"Expected {ARTIFACT_SCHEMA_VERSION}.")
    if artifact.get("report_type") not in REPORT_TYPES:
        _add_issue(errors, "REPORT_TYPE_INVALID", "report_type", "Report type must be client_briefing or advisor_review.")
    if artifact.get("synthetic_data") is not True:
        _add_issue(errors, "SYNTHETIC_DATA_REQUIRED", "synthetic_data", "Demo artifact must be synthetic_data=true.")
    if artifact.get("render_status") not in RENDER_STATUSES:
        _add_issue(errors, "RENDER_STATUS_INVALID", "render_status", "Unexpected render_status.")
    if not _non_empty_string(artifact.get("text_content")):
        _add_issue(errors, "TEXT_CONTENT_REQUIRED", "text_content", "text_content must be non-empty.")
    if not _non_empty_string(artifact.get("html_content")):
        _add_issue(errors, "HTML_CONTENT_REQUIRED", "html_content", "html_content must be non-empty.")

    sections = artifact.get("ordered_sections")
    if not isinstance(sections, list) or not sections:
        _add_issue(errors, "SECTIONS_REQUIRED", "ordered_sections", "Artifact must include ordered sections.")
    elif isinstance(sections, list):
        for expected_order, section in enumerate(sections, start=1):
            _validate_section(section, expected_order, errors)

    combined = json.dumps({key: value for key, value in artifact.items() if key != "validation"}, sort_keys=True).lower()
    for marker in REAL_DATA_MARKERS:
        if marker in combined:
            _add_issue(errors, "REAL_DATA_MARKER_DETECTED", marker, f"Artifact contains prohibited real-data marker: {marker}")
    for marker in EXTERNAL_API_MARKERS:
        if marker in combined:
            _add_issue(errors, "EXTERNAL_API_MARKER_DETECTED", marker, f"Artifact contains external API marker: {marker}")
    user_content = f"{artifact.get('text_content') or ''} {artifact.get('html_content') or ''}".lower()
    for marker in DEVELOPER_ERROR_MARKERS:
        if marker in user_content:
            _add_issue(errors, "DEVELOPER_ERROR_LANGUAGE_DETECTED", marker, f"Artifact content exposes developer language: {marker}")

    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "builder_version": ARTIFACT_BUILDER_VERSION,
        "validated_at": artifact.get("generated_at") or GENERATED_AT,
    }


def write_demo_generated_report_artifacts(
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    view_dir: str | Path = DEFAULT_VIEW_DIR,
) -> dict[str, Any]:
    """Write one client and one advisor demo artifact plus a compact index."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    artifacts = [
        create_demo_generated_report_artifact("client_briefing", view_dir=view_dir),
        create_demo_generated_report_artifact("advisor_review", view_dir=view_dir),
    ]
    index_entries = []
    for artifact in artifacts:
        report_id = artifact["report_id"]
        json_file = f"{report_id}.json"
        html_file = f"{report_id}.html"
        text_file = f"{report_id}.txt"
        _write_json(output_path / json_file, artifact)
        (output_path / html_file).write_text(artifact["html_content"], encoding="utf-8")
        (output_path / text_file).write_text(artifact["text_content"], encoding="utf-8")
        index_entries.append(
            {
                "report_id": report_id,
                "report_type": artifact["report_type"],
                "report_title": artifact["report_title"],
                "generated_at": artifact["generated_at"],
                "data_as_of": artifact["data_as_of"],
                "render_status": artifact["render_status"],
                "json_file": json_file,
                "html_file": html_file,
                "text_file": text_file,
                "synthetic_data": True,
            }
        )
    index = {
        "schema_version": ARTIFACT_INDEX_SCHEMA_VERSION,
        "builder_version": ARTIFACT_BUILDER_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "artifact_count": len(index_entries),
        "artifacts": index_entries,
        "caveat": "Synthetic generated report artifacts only; not a production report archive or report library.",
    }
    _write_json(output_path / "generated_report_artifact_index.json", index)
    return {"artifacts": artifacts, "index": index}


def _section_from_preview_element(element: dict[str, Any], order_index: int, report_type: str) -> dict[str, Any]:
    title = _section_title_from_element(element, report_type)
    section_id = f"{report_type}_{order_index:02d}_{_slug(element.get('element_key') or element.get('element_id') or title)}"
    section_type = "narrative" if element.get("element_kind") == "narrative" else "report_element"
    if not _clean_string(element.get("headline")) or not _clean_string(element.get("summary_text")):
        text = "This section is not available in the demo generated report."
        return {
            "section_id": section_id,
            "title": title,
            "section_type": "unsupported",
            "order_index": order_index,
            "html": f"<section><h2>{html.escape(title)}</h2><p>{html.escape(text)}</p></section>",
            "text": f"{title}\n{text}",
            "source_element_id": _clean_optional_string(element.get("element_id")),
            "source_element_title": _clean_optional_string(element.get("element_title")),
            "status": "placeholder",
        }
    html_fragment = _html_for_element_section(element, section_id, title)
    text_fragment = _text_for_element_section(element, title)
    return {
        "section_id": section_id,
        "title": title,
        "section_type": section_type,
        "order_index": order_index,
        "html": html_fragment,
        "text": text_fragment,
        "source_element_id": _clean_optional_string(element.get("element_id")),
        "source_element_title": _clean_optional_string(element.get("element_title")),
        "status": "rendered",
    }


def _narrative_section(report_type: str, order_index: int, slug: str, title: str, body: str) -> dict[str, Any]:
    section_id = f"{report_type}_{order_index:02d}_{slug}"
    return {
        "section_id": section_id,
        "title": title,
        "section_type": "narrative",
        "order_index": order_index,
        "html": (
            f'<section data-section-id="{html.escape(section_id, quote=True)}">'
            f"<h2>{html.escape(title)}</h2>"
            f"<p>{html.escape(body)}</p>"
            "</section>"
        ),
        "text": f"{title}\n{body}",
        "source_element_id": None,
        "source_element_title": None,
        "status": "rendered",
    }


def _opening_framing(report_type: str) -> tuple[str, str]:
    if report_type == "advisor_review":
        return (
            "Advisor Prep Framing",
            "Use this internal prep and risk/readiness review to decide which manager, concentration, scenario, and data-confidence points are ready for the client conversation.",
        )
    return (
        "Conversation Framing",
        "Use this concise client conversation aid to anchor the meeting in current portfolio status, cash and liquidity, concentration, scenario sensitivity, and data confidence.",
    )


def _closing_prompts(report_type: str) -> tuple[str, str]:
    if report_type == "advisor_review":
        return (
            "Internal Follow-Ups",
            "Confirm manager mandate fit, resolve human-review data items, and choose which concentration or scenario points should be promoted to client-facing material.",
        )
    return (
        "Discussion Prompts",
        "Use the briefing to ask what changed, whether cash and liquidity still fit near-term needs, and which concentration or scenario questions deserve follow-up.",
    )


def _artifact_caveats(caveats: list[Any]) -> list[str]:
    cleaned = [_clean_string(caveat) for caveat in caveats if _clean_string(caveat)]
    scenario_note = next((caveat for caveat in cleaned if "not a forecast" in caveat.lower()), "")
    caveat = "Synthetic demo only; not investment advice, a recommendation, or a production report."
    if scenario_note:
        caveat += " Scenario output is deterministic synthetic analysis, not a forecast."
    caveat += " No real client data, live market data, external APIs, or external account data are used."
    return [caveat]


def _caveat_section(caveats: list[Any], order_index: int) -> dict[str, Any]:
    cleaned = [_clean_string(caveat) for caveat in caveats if _clean_string(caveat)]
    if not cleaned:
        cleaned = ["Synthetic demo only; not investment advice, a recommendation, or a production report."]
    body = " ".join(cleaned)
    text = f"Demo Note\n{body}"
    return {
        "section_id": "demo_caveats",
        "title": "Demo Note",
        "section_type": "caveat",
        "order_index": order_index,
        "html": f"<section data-section-id=\"demo_caveats\"><h2>Demo Note</h2><p><small>{html.escape(body)}</small></p></section>",
        "text": text,
        "source_element_id": None,
        "source_element_title": None,
        "status": "rendered",
    }


def _html_for_element_section(element: dict[str, Any], section_id: str, section_title: str) -> str:
    headline = _clean_string(element.get("headline"))
    parts = [
        (
            f'<section data-section-id="{html.escape(section_id, quote=True)}" '
            f'data-source-element-id="{html.escape(str(element.get("element_id") or ""), quote=True)}">'
        ),
        f"<h2>{html.escape(section_title)}</h2>",
    ]
    if headline and headline != section_title:
        parts.append(f"<p><strong>{html.escape(headline)}</strong></p>")
    parts.append(f"<p>{html.escape(str(element.get('summary_text')))}</p>")
    metrics = element.get("key_metrics", [])
    if metrics:
        parts.extend(["<table>", "<thead><tr><th>Metric</th><th>Value</th></tr></thead>", "<tbody>"])
        for metric in metrics[:6]:
            parts.append(
                "<tr>"
                f"<td>{html.escape(str(metric.get('label') or 'Metric'))}</td>"
                f"<td>{html.escape(str(metric.get('formatted_value') or metric.get('value') or ''))}</td>"
                "</tr>"
            )
        parts.extend(["</tbody>", "</table>"])
    confidence = element.get("confidence_summary") if isinstance(element.get("confidence_summary"), dict) else {}
    if confidence.get("label"):
        parts.append(f"<p><small>Confidence: {html.escape(str(confidence.get('label')))}.</small></p>")
    parts.append("</section>")
    return "\n".join(parts)


def _text_for_element_section(element: dict[str, Any], section_title: str) -> str:
    headline = _clean_string(element.get("headline"))
    lines = [section_title]
    if headline and headline != section_title:
        lines.append(headline)
    lines.append(str(element.get("summary_text")))
    metrics = element.get("key_metrics", [])
    if metrics:
        lines.append("Key metrics:")
        for metric in metrics[:6]:
            lines.append(f"- {metric.get('label')}: {metric.get('formatted_value') or metric.get('value')}")
    confidence = element.get("confidence_summary") if isinstance(element.get("confidence_summary"), dict) else {}
    if confidence.get("label"):
        lines.append(f"Confidence: {confidence.get('label')}.")
    return "\n".join(line for line in lines if _clean_string(line))


def _section_title_from_element(element: dict[str, Any], report_type: str) -> str:
    if element.get("element_kind") == "narrative":
        return _clean_string(element.get("headline")) or _clean_string(element.get("element_title")) or "Narrative"
    element_id = _clean_string(element.get("element_id"))
    title = ANALYTIC_SECTION_TITLES.get(element_id)
    if isinstance(title, dict):
        return title.get(report_type) or next(iter(title.values()))
    if isinstance(title, str):
        return title
    return _clean_string(element.get("element_title")) or _clean_string(element.get("headline")) or "Report Section"


def _render_artifact_text(
    report_title: str,
    preview_payload: dict[str, Any],
    sections: list[dict[str, Any]],
    data_as_of: str,
    data_snapshot_label: str,
) -> str:
    lines = [
        report_title,
        f"{data_snapshot_label} | Data as of {data_as_of}",
        f"Generated {preview_payload.get('generated_at') or GENERATED_AT}",
        "",
        _clean_string(preview_payload.get("preview_summary") or preview_payload.get("purpose")),
        "",
    ]
    for section in sections:
        lines.extend([section["text"], ""])
    return "\n".join(lines).strip() + "\n"


def _render_artifact_html(
    report_title: str,
    preview_payload: dict[str, Any],
    sections: list[dict[str, Any]],
    data_as_of: str,
    data_snapshot_label: str,
) -> str:
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{html.escape(report_title)}</title>",
        "</head>",
        "<body>",
        '<main data-artifact-schema="generated_report_artifact.v1">',
        f"<h1>{html.escape(report_title)}</h1>",
        "<p>"
        f"{html.escape(data_snapshot_label)} | "
        f"Data as of {html.escape(data_as_of)} | "
        f"Generated {html.escape(str(preview_payload.get('generated_at') or GENERATED_AT))}"
        "</p>",
        f"<p>{html.escape(_clean_string(preview_payload.get('preview_summary') or preview_payload.get('purpose')))}</p>",
    ]
    parts.extend(section["html"] for section in sections)
    parts.extend(["</main>", "</body>", "</html>"])
    return "\n".join(parts) + "\n"


def _report_title(report_type: str, data_as_of: str) -> str:
    return f"{REPORT_TYPE_TITLES[report_type]} - {data_as_of}"


def _validate_section(section: Any, expected_order: int, errors: list[dict[str, str]]) -> None:
    if not isinstance(section, dict):
        _add_issue(errors, "SECTION_NOT_OBJECT", f"ordered_sections[{expected_order - 1}]", "Section must be an object.")
        return
    for field in (
        "section_id",
        "title",
        "section_type",
        "order_index",
        "html",
        "text",
        "source_element_id",
        "source_element_title",
        "status",
    ):
        if field not in section:
            _add_issue(errors, "SECTION_FIELD_MISSING", f"ordered_sections[{expected_order - 1}].{field}", f"Missing section field: {field}")
    if section.get("order_index") != expected_order:
        _add_issue(errors, "SECTION_ORDER_INVALID", str(section.get("section_id")), "Section order_index must be sequential.")
    if section.get("section_type") not in SECTION_TYPES:
        _add_issue(errors, "SECTION_TYPE_INVALID", str(section.get("section_id")), "Unexpected section_type.")
    if section.get("status") not in SECTION_STATUSES:
        _add_issue(errors, "SECTION_STATUS_INVALID", str(section.get("section_id")), "Unexpected section status.")
    if not _non_empty_string(section.get("html")) or not _non_empty_string(section.get("text")):
        _add_issue(errors, "SECTION_CONTENT_REQUIRED", str(section.get("section_id")), "Section html and text must be non-empty.")


def _slug(value: Any) -> str:
    text = _clean_string(value).lower()
    cleaned = []
    previous_dash = False
    for character in text:
        if character.isalnum():
            cleaned.append(character)
            previous_dash = False
        elif not previous_dash:
            cleaned.append("_")
            previous_dash = True
    return "".join(cleaned).strip("_") or "section"


def _clean_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _clean_optional_string(value: Any) -> str | None:
    cleaned = _clean_string(value)
    return cleaned or None


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})
