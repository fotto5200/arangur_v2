"""Demo generated-report population from browser-local workflow payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arangur.report_elements.briefing_set_preview import GENERATED_AT, load_report_element_views
from arangur.report_elements.generated_report_artifact import (
    build_generated_report_artifact_from_briefing_preview,
    validate_generated_report_artifact,
)

from .briefing_spec_sets import BriefingSpecSetError, validate_briefing_spec_set_payload


GENERATED_REPORT_POPULATE_ENDPOINT = "/api/generated-reports/demo-populate"
DEMO_DATA_AS_OF = "2026-06-30"
DEMO_DATA_SNAPSHOT_LABEL = "Current synthetic demo snapshot"
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views")

REPORT_TYPE_TO_SET = {
    "client_briefing": {
        "set_key": "client_briefing_set",
        "preview_type": "client_briefing_set",
        "audience": "Client Briefing Set",
        "purpose": "Client briefing generated from a saved browser workflow and the current synthetic demo data snapshot.",
    },
    "advisor_review": {
        "set_key": "advisor_review_set",
        "preview_type": "advisor_review_set",
        "audience": "Advisor Review Set",
        "purpose": "Advisor review generated from a saved browser workflow and the current synthetic demo data snapshot.",
    },
}


class GeneratedReportError(ValueError):
    """Raised when a demo generated-report request is invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def build_demo_populated_report_artifact(
    payload: dict[str, Any],
    view_dir: str | Path = DEFAULT_VIEW_DIR,
) -> dict[str, Any]:
    """Build a deterministic generated report artifact from a browser workflow payload."""

    if not isinstance(payload, dict):
        raise GeneratedReportError("invalid_generated_report_request", "Generated report request must be a JSON object.")
    _assert_json_serializable(payload)

    report_type = _clean_string(payload.get("report_type"))
    if report_type not in REPORT_TYPE_TO_SET:
        raise GeneratedReportError(
            "invalid_report_type",
            "report_type must be client_briefing or advisor_review.",
        )

    try:
        validation = validate_briefing_spec_set_payload(payload)
    except BriefingSpecSetError as exc:
        raise GeneratedReportError("invalid_generated_report_request", exc.message) from exc

    config = REPORT_TYPE_TO_SET[report_type]
    selected_set = payload.get(config["set_key"])
    if not isinstance(selected_set, list) or not selected_set:
        raise GeneratedReportError(
            "invalid_generated_report_request",
            f"Selected workflow has no {config['audience']} elements to populate.",
        )

    workflow_id = _clean_optional_string(payload.get("workflow_id"))
    workflow_display_name = (
        _clean_optional_string(payload.get("workflow_display_name"))
        or _clean_optional_string(payload.get("workflow_name"))
        or validation["title"]
        or "Saved workflow"
    )
    data_as_of = _clean_optional_string(payload.get("data_as_of")) or DEMO_DATA_AS_OF
    data_snapshot_label = _clean_optional_string(payload.get("data_snapshot_label")) or DEMO_DATA_SNAPSHOT_LABEL
    views = load_report_element_views(view_dir)
    preview_payload = _build_preview_payload(
        payload=payload,
        report_type=report_type,
        selected_set=selected_set,
        workflow_id=workflow_id,
        workflow_display_name=workflow_display_name,
        data_as_of=data_as_of,
        data_snapshot_label=data_snapshot_label,
        views=views,
    )
    artifact = build_generated_report_artifact_from_briefing_preview(
        preview_payload,
        report_type=report_type,
        source_workflow_id=workflow_id,
        source_workflow_display_name=workflow_display_name,
        report_id=_report_id(report_type, workflow_id, workflow_display_name, data_as_of),
    )
    artifact["metadata_json"].update(
        {
            "source": "browser_local_saved_workflow",
            "source_workflow_item_count": len(selected_set),
            "data_snapshot_kind": "synthetic_demo",
            "endpoint": GENERATED_REPORT_POPULATE_ENDPOINT,
            "artifact_persistence": "ephemeral_local_demo",
        }
    )
    artifact["summary"].update(
        {
            "source_workflow_display_name": workflow_display_name,
            "data_as_of": data_as_of,
            "artifact_persistence": "ephemeral_local_demo",
        }
    )
    artifact["validation"] = validate_generated_report_artifact(artifact)
    if artifact["validation"]["status"] != "valid":
        raise GeneratedReportError("generated_report_invalid", "Generated report artifact failed demo validation.")
    return artifact


def _build_preview_payload(
    payload: dict[str, Any],
    report_type: str,
    selected_set: list[dict[str, Any]],
    workflow_id: str | None,
    workflow_display_name: str,
    data_as_of: str,
    data_snapshot_label: str,
    views: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    config = REPORT_TYPE_TO_SET[report_type]
    ordered_elements = [
        _preview_element_from_spec(item, order, views)
        for order, item in enumerate(selected_set, start=1)
    ]
    return {
        "schema_version": "briefing_set_preview.v1",
        "generated_at": GENERATED_AT,
        "builder_version": "generated_report_populate_service.v1",
        "preview_id": f"demo_populate_{report_type}_{_slug(workflow_id or workflow_display_name)}",
        "preview_type": config["preview_type"],
        "title": f"{workflow_display_name} Demo Populated Report",
        "purpose": config["purpose"],
        "client_or_portfolio_context": {
            **_safe_dict(payload.get("client_context")),
            "portfolio_label": data_snapshot_label,
            "as_of_date": data_as_of,
            "audience": config["audience"],
            "synthetic_data": True,
        },
        "preview_summary": (
            f"{workflow_display_name} populated with the current synthetic demo data snapshot. "
            "Generated report artifacts remain local demo objects, not a report library."
        ),
        "ordered_elements": ordered_elements,
        "included_element_ids": [
            element.get("element_id")
            for element in ordered_elements
            if _clean_optional_string(element.get("element_id"))
        ],
        "source_workflow_id": workflow_id,
        "source_workflow_display_name": workflow_display_name,
        "advisor_notes": [],
        "review_notes": [],
        "caveats": [
            "Synthetic demo data only.",
            "Demo generated report artifact only; not a production report, recommendation, or report history record.",
            "No real client data, live market data, external APIs, or external account data are used.",
        ],
        "confidence_summary": _confidence_summary(ordered_elements),
        "source_view_summary": {
            "source": "browser_local_saved_workflow",
            "view_count": len(views),
            "matched_view_count": sum(1 for element in ordered_elements if element.get("source_view_matched")),
        },
        "synthetic_data": True,
    }


def _preview_element_from_spec(
    item: dict[str, Any],
    order: int,
    views: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if item.get("element_kind") == "narrative":
        return _narrative_preview_element(item, order)

    view_key = _matched_view_key(item) or _view_key_for_spec_item(item)
    view = views.get(view_key or "")
    if not view:
        return _unsupported_preview_element(item, order)
    return {
        "order": order,
        "element_key": view_key,
        "element_id": _clean_optional_string(item.get("element_id")) or view.get("element_id"),
        "element_title": _clean_optional_string(item.get("element_title")) or view.get("element_title"),
        "placement": _clean_string(item.get("placement")),
        "element_view_path": view.get("_view_file_path"),
        "markdown_fragment_path": view.get("_markdown_fragment_path"),
        "html_fragment_path": view.get("_html_fragment_path"),
        "headline": view.get("headline"),
        "summary_text": view.get("summary_text"),
        "key_metrics": view.get("key_metrics", []),
        "confidence_summary": view.get("confidence_summary", {}),
        "caveats": view.get("caveats", []),
        "human_review_count": len(view.get("human_review_items", [])),
        "human_review_items": view.get("human_review_items", [])[:5],
        "as_of_date": view.get("as_of_date"),
        "source_view_matched": True,
        "synthetic_data": True,
    }


def _narrative_preview_element(item: dict[str, Any], order: int) -> dict[str, Any]:
    fields = _safe_dict(item.get("narrative_fields"))
    title = (
        _clean_optional_string(fields.get("title_text"))
        or _clean_optional_string(fields.get("heading"))
        or _clean_optional_string(item.get("element_title"))
        or "Narrative"
    )
    body = (
        _clean_optional_string(fields.get("body_text"))
        or _clean_optional_string(fields.get("prompt_text"))
        or _clean_optional_string(fields.get("note_text"))
        or _clean_optional_string(item.get("placement"))
        or "Advisor-authored narrative text for the demo populated report."
    )
    return {
        "order": order,
        "element_key": _clean_optional_string(item.get("local_spec_id")) or f"narrative_{order}",
        "element_kind": "narrative",
        "element_id": _clean_optional_string(item.get("element_id")),
        "element_title": _clean_optional_string(item.get("element_title")) or title,
        "placement": _clean_string(item.get("placement")),
        "headline": title,
        "summary_text": body,
        "key_metrics": [],
        "confidence_summary": {},
        "caveats": [_clean_string(item.get("caveat")) or "Browser-local narrative element."],
        "human_review_count": 0,
        "human_review_items": [],
        "as_of_date": DEMO_DATA_AS_OF,
        "source_view_matched": False,
        "synthetic_data": True,
    }


def _unsupported_preview_element(item: dict[str, Any], order: int) -> dict[str, Any]:
    title = _clean_optional_string(item.get("element_title")) or _clean_optional_string(item.get("element_id")) or "Unavailable section"
    return {
        "order": order,
        "element_key": _clean_optional_string(item.get("local_spec_id")) or _slug(title),
        "element_id": _clean_optional_string(item.get("element_id")),
        "element_title": title,
        "placement": _clean_string(item.get("placement")),
        "headline": title,
        "summary_text": "",
        "key_metrics": [],
        "confidence_summary": {},
        "caveats": [_clean_string(item.get("caveat")) or "No committed demo rendering exists for this section."],
        "human_review_count": 0,
        "human_review_items": [],
        "as_of_date": DEMO_DATA_AS_OF,
        "source_view_matched": False,
        "synthetic_data": True,
    }


def _matched_view_key(item: dict[str, Any]) -> str | None:
    matched = item.get("matched_rendered_view")
    if not isinstance(matched, dict):
        return None
    return _clean_optional_string(matched.get("view_id"))


def _view_key_for_spec_item(item: dict[str, Any]) -> str | None:
    element_id = _clean_string(item.get("element_id"))
    params = _safe_dict(item.get("configured_parameters"))
    scope = _normalize(params.get("scope"))
    if element_id in {"portfolio_status", "cash_generation_summary", "manager_comparison", "data_confidence_note"}:
        if scope.startswith("selected "):
            return None
        return element_id
    if element_id == "concentration":
        lens = _normalize(params.get("lens"))
        if "theme" in lens:
            return "concentration_theme"
        if "sector" in lens or "industry" in lens:
            return "concentration_sector_industry"
        return None
    if element_id == "scenario_impact_by_manager":
        scenario = _normalize(params.get("scenario_id")).replace("/", " ")
        if "ai chip selloff" in scenario or "ai_chip_selloff" in scenario:
            return "scenario_impact_by_manager_ai_chip_selloff"
    return None


def _confidence_summary(ordered_elements: list[dict[str, Any]]) -> dict[str, Any]:
    for element in ordered_elements:
        if element.get("element_id") == "data_confidence_note" and isinstance(element.get("confidence_summary"), dict):
            return dict(element["confidence_summary"])
    for element in ordered_elements:
        if isinstance(element.get("confidence_summary"), dict) and element["confidence_summary"]:
            return dict(element["confidence_summary"])
    return {}


def _report_id(report_type: str, workflow_id: str | None, workflow_display_name: str, data_as_of: str) -> str:
    workflow_part = _slug(workflow_id or workflow_display_name)
    return f"demo_{report_type}_{workflow_part}_{data_as_of.replace('-', '')}"


def _assert_json_serializable(payload: dict[str, Any]) -> None:
    try:
        json.dumps(payload, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise GeneratedReportError(
            "invalid_generated_report_request",
            "Generated report request must be JSON serializable.",
        ) from exc


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _clean_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _clean_optional_string(value: Any) -> str | None:
    cleaned = _clean_string(value)
    return cleaned or None


def _normalize(value: Any) -> str:
    return " ".join(_clean_string(value).lower().replace("_", " ").split())


def _slug(value: Any) -> str:
    text = _normalize(value)
    cleaned = []
    previous_dash = False
    for character in text:
        if character.isalnum():
            cleaned.append(character)
            previous_dash = False
        elif not previous_dash:
            cleaned.append("_")
            previous_dash = True
    return "".join(cleaned).strip("_") or "workflow"
