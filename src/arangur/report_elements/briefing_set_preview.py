"""Assemble rendered report-element views into deterministic briefing-set previews."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


PREVIEW_SCHEMA_VERSION = "briefing_set_preview.v1"
INDEX_SCHEMA_VERSION = "briefing_set_preview_index.v1"
BUILDER_VERSION = "briefing_set_preview_builder.v1"
GENERATED_AT = "2026-06-30T00:00:00Z"

DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views")
DEFAULT_OUTPUT_DIR = Path("data/simulation/briefing_set_previews")

CLIENT_PREVIEW_SEQUENCE = [
    ("portfolio_status", "Opening status"),
    ("cash_generation_summary", "Cash and liquidity check"),
    ("concentration_theme", "Concentration discussion"),
    ("scenario_impact_by_manager_ai_chip_selloff", "Scenario discussion"),
    ("data_confidence_note", "Confidence note"),
]

ADVISOR_PREVIEW_SEQUENCE = [
    ("manager_comparison", "Manager review"),
    ("data_confidence_note", "Data readiness review"),
    ("concentration_sector_industry", "Exposure diagnostic"),
    ("scenario_impact_by_manager_ai_chip_selloff", "Scenario diagnostic"),
    ("cash_generation_summary", "Cash and liquidity follow-up"),
]

PREVIEW_BODY_PATH_MARKERS = {
    ".json",
    "/api/",
    "data/simulation",
    "debug artifact",
    "element_view_path",
    "html_fragment_path",
    "markdown_fragment_path",
    "report package",
    "source_input_path",
}

PRODUCTION_CLAIM_MARKERS = {
    "audited statement",
    "forecast certainty",
    "guaranteed",
    "production-ready",
    "tax advice",
}

REAL_DATA_MARKERS = {
    "access_token",
    "api key",
    "bloomberg",
    "factset",
    "morningstar direct",
    "private key",
    "refinitiv",
}


def load_report_element_views(view_dir: str | Path = DEFAULT_VIEW_DIR) -> dict[str, dict[str, Any]]:
    """Load rendered report-element views and attach local fragment paths."""

    root = Path(view_dir)
    summary_path = root / "report_element_view_summary.json"
    ordered_files = _ordered_view_files(root, summary_path)
    views: dict[str, dict[str, Any]] = {}
    for view_path in ordered_files:
        view = _load_json(view_path)
        key = _view_key(view_path.name)
        view["_view_key"] = key
        view["_view_file_path"] = _normalize_path(view_path)
        view["_markdown_fragment_path"] = _normalize_path(root / f"{key}.md")
        view["_html_fragment_path"] = _normalize_path(root / f"{key}.html")
        views[key] = view
    return views


def build_default_client_briefing_set_preview(
    view_payloads: dict[str, dict[str, Any]] | list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the default client-facing briefing-set preview."""

    views = _coerce_views(view_payloads)
    ordered_elements = _ordered_elements(views, CLIENT_PREVIEW_SEQUENCE)
    preview = _base_preview(
        preview_id="client_briefing_set_preview",
        preview_type="client_briefing_set",
        title="Client Briefing Set Preview",
        purpose="Support a concise client conversation about current portfolio status, cash and liquidity, concentration, scenario sensitivity, and data confidence.",
        audience="Client Briefing Set",
        ordered_elements=ordered_elements,
        source_views=views,
    )
    preview["client_or_portfolio_context"].update(
        {
            "audience_tone": "client-facing",
            "context_note": "Synthetic Northstar Family Office demo portfolio preview assembled from rendered report elements.",
        }
    )
    preview["preview_summary"] = (
        "The synthetic client briefing opens with the current portfolio picture, connects cash and liquidity to the meeting, "
        "then uses concentration, scenario sensitivity, and data confidence as concise discussion prompts."
    )
    preview["advisor_notes"] = []
    preview["review_notes"] = [
        "Keep client-facing wording concise and caveated.",
        "Use the data confidence note as support material when verification questions arise.",
    ]
    preview["caveats"] = _common_caveats(
        [
            "Client briefing preview only; not a production report, recommendation, or advice.",
            "Scenario output is deterministic synthetic analysis and not a forecast.",
        ]
    )
    preview["validation"] = validate_briefing_set_preview(preview)
    return preview


def build_default_advisor_review_set_preview(
    view_payloads: dict[str, dict[str, Any]] | list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the default advisor/internal briefing-set preview."""

    views = _coerce_views(view_payloads)
    ordered_elements = _ordered_elements(views, ADVISOR_PREVIEW_SEQUENCE)
    preview = _base_preview(
        preview_id="advisor_review_set_preview",
        preview_type="advisor_review_set",
        title="Advisor Review Set Preview",
        purpose="Prepare the advisor to decide what is meeting-ready by reviewing manager roles, data readiness, concentration, scenario sensitivity, and cash/liquidity support.",
        audience="Advisor Review Set",
        ordered_elements=ordered_elements,
        source_views=views,
    )
    preview["client_or_portfolio_context"].update(
        {
            "audience_tone": "advisor/internal",
            "context_note": "Synthetic internal review sequence assembled from rendered report elements.",
        }
    )
    preview["preview_summary"] = (
        "The advisor review starts with manager role fit, checks data readiness, reviews concentration and scenario sensitivity, "
        "and closes with cash/liquidity support before any point is promoted to client material."
    )
    preview["advisor_notes"] = [
        "Review mandate fit before promoting manager-level content to a client briefing.",
        "Confirm cash-generation framing remains separate from statement-grade cash accounting.",
        "Resolve human-review and low-confidence items before using these views outside the synthetic demo.",
    ]
    preview["review_notes"] = [
        "Advisor/internal preview emphasizes diagnostics, confidence, and human-review items.",
        "Scenario output should remain a deterministic risk prompt, not a probability estimate.",
    ]
    preview["caveats"] = _common_caveats(
        [
            "Advisor review preview only; not a production report, recommendation, or advice.",
            "Human-review items and confidence labels are synthetic readiness signals.",
            "Scenario output is deterministic synthetic analysis and not a forecast.",
        ]
    )
    preview["validation"] = validate_briefing_set_preview(preview)
    return preview


def render_briefing_set_preview_markdown(preview_payload: dict[str, Any]) -> str:
    """Render a briefing-set preview as Markdown without internal artifact paths."""

    lines = [
        f"# {_markdown_text(preview_payload.get('title'))}",
        "",
        _markdown_text(preview_payload.get("preview_summary") or preview_payload.get("purpose")),
        "",
        "## Context",
        "",
        f"- Audience: {_markdown_text(preview_payload.get('client_or_portfolio_context', {}).get('audience_tone'))}",
        f"- As of: {_markdown_text(preview_payload.get('client_or_portfolio_context', {}).get('as_of_date'))}",
        f"- Synthetic/demo status: {_markdown_text('Synthetic demo preview only')}",
        "",
        "## Ordered Elements",
        "",
    ]
    for element in preview_payload.get("ordered_elements", []):
        lines.extend(_markdown_element(element))
    notes = preview_payload.get("advisor_notes") or preview_payload.get("review_notes") or []
    if notes:
        lines.extend(["", "## Review Notes", ""])
        lines.extend(f"- {_markdown_text(note)}" for note in notes)
    confidence = preview_payload.get("confidence_summary", {})
    if confidence:
        lines.extend(["", "## Confidence", ""])
        lines.extend(_markdown_confidence(confidence))
    caveats = preview_payload.get("caveats", [])
    if caveats:
        lines.extend(["", "## Caveats", ""])
        lines.extend(f"- {_markdown_text(caveat)}" for caveat in caveats)
    return "\n".join(lines).strip() + "\n"


def render_briefing_set_preview_html(preview_payload: dict[str, Any]) -> str:
    """Render a briefing-set preview as a small static HTML document."""

    context = preview_payload.get("client_or_portfolio_context", {})
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{html.escape(str(preview_payload.get('title') or 'Briefing Set Preview'))}</title>",
        "</head>",
        "<body>",
        f'<main data-preview-type="{html.escape(str(preview_payload.get("preview_type")), quote=True)}">',
        f"<h1>{html.escape(str(preview_payload.get('title')))}</h1>",
        f"<p>{html.escape(str(preview_payload.get('preview_summary') or preview_payload.get('purpose')))}</p>",
        "<section>",
        "<h2>Context</h2>",
        "<ul>",
        f"<li>Audience: {html.escape(str(context.get('audience_tone') or 'preview'))}</li>",
        f"<li>As of: {html.escape(str(context.get('as_of_date') or 'unknown'))}</li>",
        "<li>Synthetic/demo status: Synthetic demo preview only</li>",
        "</ul>",
        "</section>",
        "<section>",
        "<h2>Ordered Elements</h2>",
    ]
    for element in preview_payload.get("ordered_elements", []):
        parts.extend(_html_element(element))
    parts.append("</section>")
    notes = preview_payload.get("advisor_notes") or preview_payload.get("review_notes") or []
    if notes:
        parts.extend(["<section>", "<h2>Review Notes</h2>", "<ul>"])
        parts.extend(f"<li>{html.escape(str(note))}</li>" for note in notes)
        parts.extend(["</ul>", "</section>"])
    confidence = preview_payload.get("confidence_summary", {})
    if confidence:
        parts.extend(["<section>", "<h2>Confidence</h2>", "<ul>"])
        parts.extend(f"<li>{html.escape(line.removeprefix('- '))}</li>" for line in _markdown_confidence(confidence))
        parts.extend(["</ul>", "</section>"])
    caveats = preview_payload.get("caveats", [])
    if caveats:
        parts.extend(["<section>", "<h2>Caveats</h2>", "<ul>"])
        parts.extend(f"<li><small>{html.escape(str(caveat))}</small></li>" for caveat in caveats)
        parts.extend(["</ul>", "</section>"])
    parts.extend(["</main>", "</body>", "</html>"])
    return "\n".join(parts) + "\n"


def write_demo_briefing_set_previews(
    view_dir: str | Path = DEFAULT_VIEW_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Write default client/advisor briefing-set previews and a static index."""

    views = load_report_element_views(view_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    client_preview = build_default_client_briefing_set_preview(views)
    advisor_preview = build_default_advisor_review_set_preview(views)
    previews = [client_preview, advisor_preview]
    rendered_previews = []
    for preview in previews:
        markdown = render_briefing_set_preview_markdown(preview)
        fragment_html = render_briefing_set_preview_html(preview)
        preview["validation"] = validate_briefing_set_preview(preview, markdown, fragment_html)
        json_filename = f"{preview['preview_id']}.json"
        markdown_filename = f"{preview['preview_id']}.md"
        html_filename = f"{preview['preview_id']}.html"
        _write_json(output_path / json_filename, preview)
        (output_path / markdown_filename).write_text(markdown, encoding="utf-8")
        (output_path / html_filename).write_text(fragment_html, encoding="utf-8")
        rendered_previews.append(
            {
                "preview_id": preview["preview_id"],
                "preview_type": preview["preview_type"],
                "title": preview["title"],
                "json_file": json_filename,
                "markdown_file": markdown_filename,
                "html_file": html_filename,
                "element_count": len(preview["ordered_elements"]),
                "included_element_ids": preview["included_element_ids"],
                "validation": preview["validation"],
                "synthetic_data": True,
            }
        )

    index_payload = _build_index_payload(Path(view_dir), output_path, rendered_previews)
    _write_json(output_path / "briefing_set_preview_index.json", index_payload)
    (output_path / "index.html").write_text(_render_index_html(index_payload), encoding="utf-8")
    return {
        "client_preview": client_preview,
        "advisor_preview": advisor_preview,
        "index": index_payload,
    }


def validate_briefing_set_preview(
    preview_payload: dict[str, Any],
    markdown_preview: str | None = None,
    html_preview: str | None = None,
) -> dict[str, Any]:
    """Validate briefing-set preview payload and optional rendered files."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(preview_payload, dict):
        return {"status": "invalid", "errors": [{"code": "PREVIEW_NOT_OBJECT", "record_id": "preview", "message": "Preview payload must be an object"}], "warnings": []}
    for field in (
        "preview_id",
        "preview_type",
        "title",
        "purpose",
        "client_or_portfolio_context",
        "ordered_elements",
        "included_element_ids",
        "caveats",
        "confidence_summary",
        "synthetic_data",
    ):
        if field not in preview_payload:
            _add_issue(errors, "MISSING_FIELD", field, f"Missing required field: {field}")
    if preview_payload.get("schema_version") != PREVIEW_SCHEMA_VERSION:
        _add_issue(errors, "SCHEMA_VERSION_MISMATCH", "schema_version", f"Expected {PREVIEW_SCHEMA_VERSION}")
    if preview_payload.get("synthetic_data") is not True:
        _add_issue(errors, "SYNTHETIC_DATA_REQUIRED", "synthetic_data", "Preview must be marked synthetic_data=true")
    preview_type = preview_payload.get("preview_type")
    if preview_type not in {"client_briefing_set", "advisor_review_set"}:
        _add_issue(errors, "PREVIEW_TYPE_INVALID", "preview_type", "Preview type must be client_briefing_set or advisor_review_set")
    ordered_elements = preview_payload.get("ordered_elements", [])
    if not isinstance(ordered_elements, list) or not ordered_elements:
        _add_issue(errors, "ORDERED_ELEMENTS_REQUIRED", "ordered_elements", "Preview must include ordered elements")
    else:
        for expected_order, element in enumerate(ordered_elements, start=1):
            if element.get("order") != expected_order:
                _add_issue(errors, "ELEMENT_ORDER_INVALID", f"ordered_elements[{expected_order - 1}]", "Ordered element order must be sequential")
            for field in ("element_id", "element_title", "placement", "headline", "summary_text", "key_metrics", "confidence_summary", "caveats"):
                if field not in element:
                    _add_issue(errors, "ORDERED_ELEMENT_FIELD_MISSING", f"ordered_elements[{expected_order - 1}].{field}", f"Missing ordered element field: {field}")
            for path_field in ("element_view_path", "markdown_fragment_path", "html_fragment_path"):
                path_value = element.get(path_field)
                if not path_value:
                    _add_issue(errors, "ORDERED_ELEMENT_PATH_MISSING", f"ordered_elements[{expected_order - 1}].{path_field}", f"Missing path field: {path_field}")
                elif not Path(path_value).exists():
                    _add_issue(errors, "ORDERED_ELEMENT_PATH_NOT_FOUND", str(path_value), f"Referenced rendered element file does not exist: {path_value}")
    if preview_type == "client_briefing_set" and len(ordered_elements) < 3:
        _add_issue(errors, "CLIENT_PREVIEW_TOO_SHORT", "ordered_elements", "Client preview must include at least 3 elements")
    if preview_type == "advisor_review_set" and len(ordered_elements) < 4:
        _add_issue(errors, "ADVISOR_PREVIEW_TOO_SHORT", "ordered_elements", "Advisor preview must include at least 4 elements")
    if not isinstance(preview_payload.get("caveats"), list) or not preview_payload.get("caveats"):
        _add_issue(errors, "CAVEATS_REQUIRED", "caveats", "Preview must include caveats")
    if not isinstance(preview_payload.get("confidence_summary"), dict) or not preview_payload.get("confidence_summary"):
        _add_issue(errors, "CONFIDENCE_SUMMARY_REQUIRED", "confidence_summary", "Preview must include confidence summary")
    if markdown_preview is not None and not markdown_preview.strip():
        _add_issue(errors, "MARKDOWN_EMPTY", "markdown_preview", "Markdown preview must be non-empty")
    if html_preview is not None and not html_preview.strip():
        _add_issue(errors, "HTML_EMPTY", "html_preview", "HTML preview must be non-empty")

    body_text = f"{markdown_preview or ''} {html_preview or ''}".lower()
    if body_text:
        for marker in PREVIEW_BODY_PATH_MARKERS:
            if marker in body_text:
                _add_issue(errors, "INTERNAL_ARTIFACT_IN_BODY", marker, f"Preview body exposes internal artifact marker: {marker}")
    if preview_type == "advisor_review_set":
        combined = f"{json.dumps(preview_payload, sort_keys=True)} {body_text}".lower()
        if "data confidence" not in combined:
            _add_issue(errors, "ADVISOR_DATA_CONFIDENCE_REQUIRED", "ordered_elements", "Advisor preview must include data-confidence language")
        if "human-review" not in combined and "human review" not in combined:
            _add_issue(errors, "ADVISOR_HUMAN_REVIEW_REQUIRED", "ordered_elements", "Advisor preview must include human-review language")
    combined_payload = f"{json.dumps(preview_payload, sort_keys=True)} {body_text}".lower()
    for marker in PRODUCTION_CLAIM_MARKERS:
        if marker in combined_payload:
            _add_issue(errors, "PRODUCTION_CLAIM_DETECTED", marker, f"Preview contains prohibited claim marker: {marker}")
    for marker in REAL_DATA_MARKERS:
        if marker in combined_payload:
            _add_issue(errors, "REAL_DATA_MARKER_DETECTED", marker, f"Preview contains prohibited real-data marker: {marker}")
    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "builder_version": BUILDER_VERSION,
        "validated_at": GENERATED_AT,
    }


def _base_preview(
    preview_id: str,
    preview_type: str,
    title: str,
    purpose: str,
    audience: str,
    ordered_elements: list[dict[str, Any]],
    source_views: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    as_of_date = next((element.get("as_of_date") for element in ordered_elements if element.get("as_of_date")), None)
    return {
        "schema_version": PREVIEW_SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "builder_version": BUILDER_VERSION,
        "preview_id": preview_id,
        "preview_type": preview_type,
        "title": title,
        "purpose": purpose,
        "client_or_portfolio_context": {
            "portfolio_label": "Northstar Family Office synthetic demo portfolio",
            "as_of_date": as_of_date,
            "audience": audience,
            "synthetic_data": True,
        },
        "preview_summary": "",
        "ordered_elements": ordered_elements,
        "included_element_ids": [element["element_id"] for element in ordered_elements],
        "advisor_notes": [],
        "review_notes": [],
        "caveats": [],
        "confidence_summary": _preview_confidence_summary(ordered_elements),
        "source_view_summary": _source_view_summary(source_views),
        "synthetic_data": True,
    }


def _ordered_elements(
    views: dict[str, dict[str, Any]],
    sequence: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    elements = []
    for order, (key, placement) in enumerate(sequence, start=1):
        if key not in views:
            raise ValueError(f"Required rendered view not found: {key}")
        view = views[key]
        elements.append(
            {
                "order": order,
                "element_key": key,
                "element_id": view["element_id"],
                "element_title": view["element_title"],
                "placement": placement,
                "element_view_path": view.get("_view_file_path"),
                "markdown_fragment_path": view.get("_markdown_fragment_path"),
                "html_fragment_path": view.get("_html_fragment_path"),
                "headline": view["headline"],
                "summary_text": view["summary_text"],
                "key_metrics": view.get("key_metrics", []),
                "confidence_summary": view.get("confidence_summary", {}),
                "caveats": view.get("caveats", []),
                "human_review_count": len(view.get("human_review_items", [])),
                "human_review_items": view.get("human_review_items", [])[:5],
                "as_of_date": view.get("as_of_date"),
                "synthetic_data": True,
            }
        )
    return elements


def _preview_confidence_summary(ordered_elements: list[dict[str, Any]]) -> dict[str, Any]:
    data_element = next((element for element in ordered_elements if element["element_id"] == "data_confidence_note"), None)
    if data_element:
        confidence = dict(data_element.get("confidence_summary", {}))
        confidence["source_element_title"] = data_element["element_title"]
        return confidence
    for element in ordered_elements:
        if element.get("confidence_summary"):
            confidence = dict(element["confidence_summary"])
            confidence["source_element_title"] = element["element_title"]
            return confidence
    return {"label": "unknown", "synthetic_data": True}


def _source_view_summary(source_views: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "view_count": len(source_views),
        "view_keys": sorted(source_views),
        "summary_path": _normalize_path(DEFAULT_VIEW_DIR / "report_element_view_summary.json"),
        "synthetic_data": True,
    }


def _common_caveats(extra: list[str]) -> list[str]:
    caveats = [
        "Synthetic demo data only.",
        "Briefing-set preview only; not a persisted briefing set, chart, production report, or investment recommendation.",
    ]
    for caveat in extra:
        if caveat not in caveats:
            caveats.append(caveat)
    return caveats


def _markdown_element(element: dict[str, Any]) -> list[str]:
    lines = [
        f"### {int(element['order'])}. {_markdown_text(element.get('headline'))}",
        "",
        _markdown_text(element.get("summary_text")),
        "",
    ]
    metrics = element.get("key_metrics", [])[:5]
    if metrics:
        lines.extend(["| Metric | Value |", "| --- | --- |"])
        for metric in metrics:
            lines.append(f"| {_markdown_text(metric.get('label'))} | {_markdown_text(metric.get('formatted_value'))} |")
        lines.append("")
    confidence = element.get("confidence_summary", {})
    if confidence.get("label"):
        lines.append(f"Confidence: {_markdown_text(confidence.get('label'))}.")
        lines.append("")
    return lines


def _html_element(element: dict[str, Any]) -> list[str]:
    parts = [
        f'<section data-element-id="{html.escape(str(element.get("element_id")), quote=True)}">',
        f"<h3>{int(element['order'])}. {html.escape(str(element.get('headline')))}</h3>",
        f"<p>{html.escape(str(element.get('summary_text')))}</p>",
    ]
    metrics = element.get("key_metrics", [])[:5]
    if metrics:
        parts.extend(["<table>", "<thead><tr><th>Metric</th><th>Value</th></tr></thead>", "<tbody>"])
        for metric in metrics:
            parts.append(
                "<tr>"
                f"<td>{html.escape(str(metric.get('label')))}</td>"
                f"<td>{html.escape(str(metric.get('formatted_value')))}</td>"
                "</tr>"
            )
        parts.extend(["</tbody>", "</table>"])
    confidence = element.get("confidence_summary", {})
    if confidence.get("label"):
        parts.append(f"<p><small>Confidence: {html.escape(str(confidence.get('label')))}.</small></p>")
    parts.append("</section>")
    return parts


def _markdown_confidence(confidence: dict[str, Any]) -> list[str]:
    lines = []
    if confidence.get("label"):
        lines.append(f"- Label: {_markdown_text(confidence.get('label'))}")
    if confidence.get("human_review_count") is not None:
        lines.append(f"- Human-review count: {_markdown_text(confidence.get('human_review_count'))}")
    if confidence.get("human_review_value") is not None:
        lines.append(f"- Human-review value: {_markdown_text(_format_money(confidence.get('human_review_value')))}")
    return lines or ["- Confidence summary included in structured preview payload."]


def _build_index_payload(
    view_dir: Path,
    output_dir: Path,
    rendered_previews: list[dict[str, Any]],
) -> dict[str, Any]:
    validation_results = {preview["json_file"]: preview["validation"] for preview in rendered_previews}
    statuses = {result["status"] for result in validation_results.values()}
    output_files = []
    for preview in rendered_previews:
        output_files.extend([preview["json_file"], preview["markdown_file"], preview["html_file"]])
    output_files.extend(["briefing_set_preview_index.json", "index.html"])
    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "builder_version": BUILDER_VERSION,
        "synthetic_data": True,
        "output_dir": _normalize_path(output_dir),
        "preview_count": len(rendered_previews),
        "previews": rendered_previews,
        "source_rendered_element_view_summary": _normalize_path(view_dir / "report_element_view_summary.json"),
        "output_files": output_files,
        "validation_status": "valid" if statuses == {"valid"} else "invalid",
        "validation_results": validation_results,
        "caveat": "Static briefing-set previews only; no browser UI integration, persistence, charts, live data, or external APIs are produced.",
    }


def _render_index_html(index_payload: dict[str, Any]) -> str:
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>Briefing Set Preview Index</title>",
        "</head>",
        "<body>",
        "<main>",
        "<h1>Briefing Set Preview Index</h1>",
        "<p>Static synthetic previews assembled from rendered report element views.</p>",
        "<ul>",
    ]
    for preview in index_payload.get("previews", []):
        parts.append(
            "<li>"
            f"<a href=\"{html.escape(preview['html_file'], quote=True)}\">{html.escape(preview['title'])}</a>"
            f" ({html.escape(preview['preview_type'])}, {int(preview['element_count'])} elements)"
            f" - <a href=\"{html.escape(preview['markdown_file'], quote=True)}\">Markdown</a>"
            f" - <a href=\"{html.escape(preview['json_file'], quote=True)}\">JSON</a>"
            "</li>"
        )
    source_link = "../report_element_views/report_element_view_summary.json"
    parts.extend(
        [
            "</ul>",
            f"<p>Source rendered element view summary: <a href=\"{source_link}\">{source_link}</a></p>",
            "<p><small>Synthetic demo output only. No persistence, charts, browser composer integration, live data, or external APIs.</small></p>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )
    return "\n".join(parts) + "\n"


def _ordered_view_files(root: Path, summary_path: Path) -> list[Path]:
    if summary_path.exists():
        summary = _load_json(summary_path)
        ordered = []
        for row in summary.get("rendered_files", []):
            view_file = row.get("view_file")
            if view_file:
                path = root / view_file
                if path.exists():
                    ordered.append(path)
        if ordered:
            return ordered
    return sorted(root.glob("*.view.json"))


def _coerce_views(view_payloads: dict[str, dict[str, Any]] | list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if isinstance(view_payloads, dict):
        return view_payloads
    coerced = {}
    for view in view_payloads:
        key = view.get("_view_key") or str(view.get("element_id") or len(coerced))
        coerced[key] = view
    return coerced


def _view_key(filename: str) -> str:
    suffix = ".view.json"
    if filename.endswith(suffix):
        return filename[: -len(suffix)]
    return Path(filename).stem


def _format_money(value: Any) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return str(value)
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"


def _markdown_text(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _normalize_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    return str(path).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})


def main() -> None:
    result = write_demo_briefing_set_previews()
    index = result["index"]
    client_count = len(result["client_preview"]["ordered_elements"])
    advisor_count = len(result["advisor_preview"]["ordered_elements"])
    print(
        "briefing set previews written: "
        f"{index['preview_count']} previews; "
        f"client_elements={client_count}; "
        f"advisor_elements={advisor_count}; "
        f"status={index['validation_status']}"
    )


if __name__ == "__main__":
    main()
