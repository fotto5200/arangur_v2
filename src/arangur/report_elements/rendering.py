"""Render report-element input payloads into simple deterministic views."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


VIEW_SCHEMA_VERSION = "report_element_view_payload.v1"
SUMMARY_SCHEMA_VERSION = "report_element_view_summary.v1"
RENDERER_VERSION = "report_element_rendering.v1"
GENERATED_AT = "2026-06-30T00:00:00Z"
ANALYTIC_INPUT_VARIANT = "analytic_pack_v1"

DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs")
DEFAULT_OUTPUT_DIR = Path("data/simulation/report_element_views")

REAL_DATA_MARKERS = {
    "access_token",
    "api key",
    "private key",
    "bloomberg",
    "factset",
    "refinitiv",
    "morningstar direct",
}

PRODUCTION_CLAIM_MARKERS = {
    "audited statement",
    "forecast certainty",
    "guaranteed",
    "production-ready",
    "tax advice",
}

FRAGMENT_PATH_MARKERS = {
    "data/simulation",
    ".json",
    "source_input_path",
}


def render_report_element_view(
    input_payload: dict[str, Any],
    source_input_path: str | Path | None = None,
) -> dict[str, Any]:
    """Render one report-element input payload into a compact view payload."""

    view = _base_view(input_payload, source_input_path)
    element_id = input_payload.get("element_id")
    if element_id == "portfolio_status":
        _render_portfolio_status(input_payload, view)
    elif element_id == "concentration":
        _render_concentration(input_payload, view)
    elif element_id == "scenario_impact_by_manager":
        _render_scenario_impact_by_manager(input_payload, view)
    elif element_id == "cash_generation_summary":
        _render_cash_generation_summary(input_payload, view)
    elif element_id == "manager_comparison":
        _render_manager_comparison(input_payload, view)
    elif element_id == "data_confidence_note":
        _render_data_confidence_note(input_payload, view)
    else:
        _render_generic(input_payload, view)

    view["validation"] = validate_report_element_view(view)
    return view


def render_report_element_markdown(input_payload: dict[str, Any]) -> str:
    """Render one input or view payload as a Markdown fragment."""

    view = _ensure_view(input_payload)
    lines = [
        f"## {_markdown_text(view['headline'])}",
        "",
        _markdown_text(view["summary_text"]),
        "",
    ]
    lines.extend(_markdown_metric_table(view.get("key_metrics", [])))
    evidence_rows = view.get("evidence_rows", [])
    if evidence_rows:
        lines.extend(["", "### Evidence", ""])
        lines.extend(_markdown_rows(evidence_rows, _evidence_columns(view)))
    confidence = view.get("confidence_summary", {})
    if confidence:
        lines.extend(["", "### Confidence", ""])
        lines.extend(_markdown_confidence(confidence))
    caveats = view.get("caveats", [])
    if caveats:
        lines.extend(["", "### Caveats", ""])
        lines.extend(f"- {_markdown_text(caveat)}" for caveat in caveats)
    return "\n".join(lines).strip() + "\n"


def render_report_element_html(input_payload: dict[str, Any]) -> str:
    """Render one input or view payload as a self-contained HTML fragment."""

    view = _ensure_view(input_payload)
    parts = [
        f'<section data-element-id="{html.escape(str(view["element_id"]), quote=True)}" data-view-type="report-element">',
        f"<h2>{html.escape(str(view['headline']))}</h2>",
        f"<p>{html.escape(str(view['summary_text']))}</p>",
    ]
    metrics = view.get("key_metrics", [])
    if metrics:
        parts.append("<h3>Key metrics</h3>")
        parts.append(_html_rows(metrics, ["label", "formatted_value"], {"label": "Metric", "formatted_value": "Value"}))
    evidence_rows = view.get("evidence_rows", [])
    if evidence_rows:
        parts.append("<h3>Evidence</h3>")
        parts.append(_html_rows(evidence_rows, _evidence_columns(view), _column_labels(_evidence_columns(view))))
    confidence = view.get("confidence_summary", {})
    if confidence:
        parts.append("<h3>Confidence</h3>")
        parts.append(_html_confidence(confidence))
    caveats = view.get("caveats", [])
    if caveats:
        parts.append("<h3>Caveats</h3>")
        parts.append("<ul>")
        for caveat in caveats:
            parts.append(f"<li><small>{html.escape(str(caveat))}</small></li>")
        parts.append("</ul>")
    parts.append("</section>")
    return "\n".join(parts) + "\n"


def render_all_demo_report_element_views(
    input_dir: str | Path = DEFAULT_INPUT_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Render all committed demo report-element input payloads."""

    return _render_report_element_views(
        input_dir=input_dir,
        output_dir=output_dir,
        input_summary_filename="report_element_input_summary.json",
        output_summary_filename="report_element_view_summary.json",
        summary_kind="demo_report_element_views",
    )


def render_all_analytic_report_element_views(
    input_dir: str | Path = DEFAULT_INPUT_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Render all committed analytic report-element input payloads."""

    return _render_report_element_views(
        input_dir=input_dir,
        output_dir=output_dir,
        input_summary_filename="report_element_analytic_input_summary.json",
        output_summary_filename="report_element_analytic_view_summary.json",
        summary_kind="analytic_report_element_views",
    )


def _render_report_element_views(
    *,
    input_dir: str | Path,
    output_dir: str | Path,
    input_summary_filename: str,
    output_summary_filename: str,
    summary_kind: str,
) -> dict[str, Any]:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    input_files = _ordered_input_files(input_path, input_summary_filename)
    output_path.mkdir(parents=True, exist_ok=True)

    rendered: list[dict[str, Any]] = []
    output_files: list[str] = []
    for source_path in input_files:
        input_payload = _load_json(source_path)
        view = render_report_element_view(input_payload, source_input_path=source_path)
        markdown = render_report_element_markdown(view)
        fragment_html = render_report_element_html(view)
        view["validation"] = validate_report_element_view(view, markdown, fragment_html)

        stem = source_path.stem
        view_filename = f"{stem}.view.json"
        markdown_filename = f"{stem}.md"
        html_filename = f"{stem}.html"
        _write_json(output_path / view_filename, view)
        (output_path / markdown_filename).write_text(markdown, encoding="utf-8")
        (output_path / html_filename).write_text(fragment_html, encoding="utf-8")
        output_files.extend([view_filename, markdown_filename, html_filename])
        rendered.append(
            {
                "input_file": source_path.name,
                "view_file": view_filename,
                "markdown_file": markdown_filename,
                "html_file": html_filename,
                "element_id": view["element_id"],
                "element_title": view["element_title"],
                "validation": view["validation"],
            }
        )

    summary = _build_summary(
        input_path,
        output_path,
        rendered,
        output_files,
        output_summary_filename=output_summary_filename,
        summary_kind=summary_kind,
    )
    _write_json(output_path / output_summary_filename, summary)
    return {"views": rendered, "summary": summary}


def validate_report_element_view(
    view_payload: dict[str, Any],
    markdown_fragment: str | None = None,
    html_fragment: str | None = None,
) -> dict[str, Any]:
    """Validate a view payload and optional rendered fragments."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(view_payload, dict):
        return {"status": "invalid", "errors": [{"code": "VIEW_NOT_OBJECT", "record_id": "view", "message": "View payload must be an object"}], "warnings": []}

    for field in (
        "schema_version",
        "element_id",
        "element_title",
        "view_type",
        "render_type",
        "as_of_date",
        "headline",
        "summary_text",
        "key_metrics",
        "evidence_rows",
        "caveats",
        "confidence_summary",
        "human_review_items",
        "synthetic_data",
    ):
        if field not in view_payload:
            _add_issue(errors, "MISSING_FIELD", field, f"Missing required field: {field}")

    if view_payload.get("schema_version") != VIEW_SCHEMA_VERSION:
        _add_issue(errors, "SCHEMA_VERSION_MISMATCH", "schema_version", f"Expected {VIEW_SCHEMA_VERSION}")
    if view_payload.get("synthetic_data") is not True:
        _add_issue(errors, "SYNTHETIC_DATA_REQUIRED", "synthetic_data", "View must be marked synthetic_data=true")
    if not _non_empty_string(view_payload.get("headline")):
        _add_issue(errors, "HEADLINE_REQUIRED", "headline", "View headline must be non-empty")
    if not _non_empty_string(view_payload.get("summary_text")):
        _add_issue(errors, "SUMMARY_REQUIRED", "summary_text", "View summary_text must be non-empty")
    if not isinstance(view_payload.get("key_metrics"), list):
        _add_issue(errors, "KEY_METRICS_REQUIRED", "key_metrics", "key_metrics must be a list")
    if not isinstance(view_payload.get("caveats"), list) or not view_payload.get("caveats"):
        _add_issue(errors, "CAVEATS_REQUIRED", "caveats", "caveats must be a non-empty list")
    if not isinstance(view_payload.get("confidence_summary"), dict):
        _add_issue(errors, "CONFIDENCE_SUMMARY_REQUIRED", "confidence_summary", "confidence_summary must be an object")

    if markdown_fragment is not None and not markdown_fragment.strip():
        _add_issue(errors, "MARKDOWN_EMPTY", "markdown_fragment", "Markdown fragment must be non-empty")
    if html_fragment is not None and not html_fragment.strip():
        _add_issue(errors, "HTML_EMPTY", "html_fragment", "HTML fragment must be non-empty")

    combined_view_text = " ".join(text for _, text in _walk_strings(view_payload)).lower()
    combined_fragment_text = f"{markdown_fragment or ''} {html_fragment or ''}".lower()
    for marker in PRODUCTION_CLAIM_MARKERS:
        if marker in combined_view_text or marker in combined_fragment_text:
            _add_issue(errors, "PRODUCTION_CLAIM_DETECTED", marker, f"Rendered output contains prohibited claim marker: {marker}")
    for marker in REAL_DATA_MARKERS:
        if marker in combined_view_text or marker in combined_fragment_text:
            _add_issue(errors, "REAL_DATA_MARKER_DETECTED", marker, f"Rendered output contains prohibited real-data marker: {marker}")
    if view_payload.get("element_id") == "scenario_impact_by_manager":
        if "not a forecast" not in combined_view_text and "not a forecast" not in combined_fragment_text:
            _add_issue(errors, "SCENARIO_CAVEAT_REQUIRED", "caveats", "Scenario output must state that it is not a forecast")
    for marker in FRAGMENT_PATH_MARKERS:
        if marker in combined_fragment_text:
            _add_issue(errors, "INTERNAL_PATH_IN_FRAGMENT", marker, f"User-facing fragment exposes internal path marker: {marker}")

    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "renderer_version": RENDERER_VERSION,
        "validated_at": GENERATED_AT,
    }


def _render_portfolio_status(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    if _is_analytic_input(input_payload):
        _render_portfolio_status_analytics(input_payload, view)
        return

    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    total = metrics.get("total_portfolio_value", {})
    cash = metrics.get("cash_value", {})
    managers = metrics.get("manager_count", {})
    positions = metrics.get("position_count", {})
    human_count = metrics.get("human_review_count", {})
    confidence_label = _confidence_label(input_payload)
    view["headline"] = f"Portfolio Status: {_format_metric(total)} synthetic value"
    view["summary_text"] = (
        f"As of {input_payload.get('as_of_date')}, the synthetic portfolio is valued at {_format_metric(total)} "
        f"with {_format_metric(cash)} in cash or cash-like positions across {_format_metric(managers)} managers "
        f"and {_format_metric(positions)} positions. Confidence is labeled {confidence_label}; "
        f"{_format_metric(human_count)} positions are flagged for human review."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("total_portfolio_value", "Total portfolio value"),
            ("cash_value", "Cash or cash-like value"),
            ("manager_count", "Managers"),
            ("position_count", "Positions"),
            ("human_review_count", "Human-review positions"),
            ("human_review_value", "Human-review value"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(tables.get("manager_values", []), row_type="manager_value")
    view["detail_tables"] = {
        "manager_values": tables.get("manager_values", []),
        "asset_class_values": tables.get("asset_class_values", [])[:8],
        "theme_values": tables.get("theme_values", [])[:8],
    }
    view["caveats"] = _view_caveats(
        input_payload,
        ["Rendered from synthetic report-element input; not a production valuation, client statement, or action recommendation."],
    )


def _render_concentration(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    if _is_analytic_input(input_payload):
        _render_concentration_analytics(input_payload, view)
        return

    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    lens = _metric_value(metrics.get("lens")) or input_payload.get("parameters_used", {}).get("lens") or "selected"
    largest_group = _metric_value(metrics.get("largest_group")) or "unavailable"
    largest_group_value = _format_metric(metrics.get("largest_group_value"))
    largest_group_percent = _format_metric(metrics.get("largest_group_percent"))
    group_rows = tables.get("grouped_rows", [])[:6]
    holding_rows = tables.get("top_holdings", [])[:5]
    view["headline"] = f"Concentration: {lens}"
    view["summary_text"] = (
        f"The {lens} lens shows {largest_group} as the largest concentration bucket at "
        f"{largest_group_value} ({largest_group_percent}). The view keeps top buckets and holdings visible "
        "as discussion prompts rather than recommendations."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("lens", "Lens"),
            ("group_count", "Group count"),
            ("largest_group", "Largest group"),
            ("largest_group_value", "Largest group value"),
            ("largest_group_percent", "Largest group percent"),
            ("top_holding_value", "Top holding value"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(group_rows, row_type="concentration_bucket") + _normalize_rows(holding_rows, row_type="top_holding")
    view["detail_tables"] = {
        "grouped_rows": tables.get("grouped_rows", []),
        "top_holdings": tables.get("top_holdings", []),
        "overlap_exposure_rows": tables.get("overlap_exposure_rows", []),
    }
    view["caveats"] = _view_caveats(
        input_payload,
        ["Concentration is rendered as a synthetic discussion prompt, not a recommendation or fund look-through claim."],
    )


def _render_scenario_impact_by_manager(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    if _is_analytic_input(input_payload):
        _render_scenario_impact_by_manager_analytics(input_payload, view)
        return

    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    scenario = input_payload.get("scenario", {})
    display_name = scenario.get("display_name") or "Selected scenario"
    impact = _format_metric(metrics.get("total_scenario_impact"))
    impact_percent = _format_metric(metrics.get("total_scenario_impact_percent"))
    manager_rows = sorted(
        tables.get("manager_impacts", []),
        key=lambda row: abs(float(row.get("scenario_impact", 0.0))),
        reverse=True,
    )
    view["headline"] = f"{display_name} impact: {impact}"
    view["summary_text"] = (
        f"The {display_name} scenario shows a deterministic synthetic portfolio impact of {impact} "
        f"({impact_percent}) over {scenario.get('horizon', 'the selected horizon')}. "
        "Manager-level impacts are shown for review; this scenario is not a forecast or probability estimate."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("base_total_value", "Base value"),
            ("scenario_total_value", "Scenario value"),
            ("total_scenario_impact", "Total scenario impact"),
            ("total_scenario_impact_percent", "Total scenario impact percent"),
            ("manager_count", "Managers"),
        ],
    )
    view["key_metrics"].append(_simple_metric("Scenario", display_name))
    view["evidence_rows"] = _normalize_rows(manager_rows, row_type="manager_scenario_impact")
    view["detail_tables"] = {
        "manager_impacts": tables.get("manager_impacts", []),
        "top_position_impacts": tables.get("top_position_impacts", []),
        "theme_impacts": tables.get("theme_impacts", [])[:8],
        "asset_class_impacts": tables.get("asset_class_impacts", [])[:8],
    }
    view["scenario"] = scenario
    view["caveats"] = _view_caveats(
        input_payload,
        ["Deterministic synthetic scenario output only; not a forecast, probability estimate, guarantee, or manager recommendation."],
    )


def _render_cash_generation_summary(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    current_cash = _format_metric(metrics.get("current_cash_value"))
    income = _format_metric(metrics.get("period_income_distributions"))
    flows = _format_metric(metrics.get("period_transaction_flows"))
    period = input_payload.get("period", {})
    manager_rows = tables.get("cash_generation_by_manager", [])
    view["headline"] = f"Cash Generation Summary: {current_cash} cash-like value"
    view["summary_text"] = (
        f"Across the synthetic period from {period.get('start_date')} to {period.get('end_date')}, "
        f"the portfolio has {current_cash} in cash-like value, {income} of income/distributions, "
        f"and {flows} of transaction flows. Cash accounting remains simplified and synthetic."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("current_cash_value", "Current cash-like value"),
            ("period_income_distributions", "Period income/distributions"),
            ("period_transaction_flows", "Period transaction flows"),
            ("period_fees", "Period fees"),
            ("cash_like_position_count", "Cash-like positions"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(manager_rows, row_type="manager_cash_generation")
    view["detail_tables"] = {
        "cash_generation_by_manager": manager_rows,
        "cash_like_positions": tables.get("cash_like_positions", []),
        "value_change_by_manager": tables.get("value_change_by_manager", []),
    }
    view["period"] = period
    view["caveats"] = _view_caveats(
        input_payload,
        ["Rendered cash generation is simplified synthetic cash accounting, not a statement-grade cash reconciliation."],
    )


def _render_manager_comparison(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    if _is_analytic_input(input_payload):
        _render_manager_comparison_analytics(input_payload, view)
        return

    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    manager_rows = tables.get("manager_rows", [])
    largest_value = _format_metric(metrics.get("largest_manager_value"))
    manager_count = _format_metric(metrics.get("manager_count"))
    view["headline"] = "Manager Comparison"
    view["summary_text"] = (
        f"The synthetic comparison includes {manager_count} managers. The largest current manager value is "
        f"{largest_value}; rows show mandate, current value, period value change, themes, and confidence notes "
        "without ranking managers as recommendations."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("manager_count", "Managers"),
            ("largest_manager_value", "Largest manager value"),
            ("period_economic_value_change", "Period economic value change"),
            ("human_review_manager_count", "Managers with human-review items"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(manager_rows, row_type="manager_comparison")
    view["detail_tables"] = {
        "manager_rows": manager_rows,
        "value_change_by_manager": tables.get("value_change_by_manager", []),
    }
    view["caveats"] = _view_caveats(
        input_payload,
        ["Manager rows compare synthetic mandate and valuation evidence; they are not manager rankings or recommendations."],
    )


def _render_data_confidence_note(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    if _is_analytic_input(input_payload):
        _render_data_confidence_note_analytics(input_payload, view)
        return

    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    label = _metric_value(metrics.get("confidence_label")) or _confidence_label(input_payload)
    human_count = _format_metric(metrics.get("human_review_count"))
    human_value = _format_metric(metrics.get("human_review_value"))
    confidence_rows = tables.get("confidence_rows", [])
    treatment_rows = tables.get("valuation_treatment_rows", [])
    view["headline"] = f"Data Confidence Note: {label}"
    view["summary_text"] = (
        f"Current synthetic data confidence is labeled {label}. Human review covers {human_count} positions "
        f"representing {human_value}; valuation treatment rows make direct, cash, proxy, stale/private, "
        "and human-review buckets visible before later preview or publication."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("confidence_label", "Confidence label"),
            ("human_review_count", "Human-review positions"),
            ("human_review_value", "Human-review value"),
            ("direct_or_cash_value", "Direct or cash value"),
            ("proxy_or_stale_value", "Proxy or stale/private value"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(confidence_rows, row_type="confidence_bucket") + _normalize_rows(treatment_rows, row_type="valuation_treatment")
    view["detail_tables"] = {
        "confidence_rows": confidence_rows,
        "valuation_treatment_rows": treatment_rows,
        "data_issue_rows": tables.get("data_issue_rows", []),
        "market_state_treatment_rows": tables.get("market_state_treatment_rows", []),
    }
    view["caveats"] = _view_caveats(
        input_payload,
        ["Confidence describes synthetic source readiness and valuation treatment, not investment quality."],
    )


def _render_portfolio_status_analytics(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    total = _format_metric(metrics.get("total_portfolio_value"))
    top_theme = tables.get("theme_values", [{}])[0]
    vulnerable = next((row for row in tables.get("resilience_rows", []) if row.get("id") == "most_vulnerable_scenario"), {})
    view["headline"] = f"Portfolio Analytic Status: {total}"
    view["summary_text"] = (
        f"As of {input_payload.get('as_of_date')}, the synthetic portfolio analytic view shows {total} "
        f"of current value. The largest approved theme is {top_theme.get('display_name', 'unavailable')}; "
        f"the largest deterministic scenario drawdown is {vulnerable.get('scenario_display_name', 'unavailable')}. "
        "This is local demo evidence for report composition, not production reporting."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("total_portfolio_value", "Total portfolio value"),
            ("top_theme_value", "Top theme value"),
            ("top_theme_percent", "Top theme percent"),
            ("most_vulnerable_scenario_impact", "Most vulnerable scenario impact"),
            ("human_review_value", "Human-review value"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(tables.get("status_rows", []), row_type="analytic_status")
    view["detail_tables"] = {
        "status_rows": tables.get("status_rows", []),
        "theme_values": tables.get("theme_values", []),
        "resilience_rows": tables.get("resilience_rows", []),
        "confidence_rows": tables.get("confidence_rows", []),
    }
    view["caveats"] = _view_caveats(
        input_payload,
        ["Analytic portfolio status is synthetic local evidence, not a client statement or production report."],
    )


def _render_concentration_analytics(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    largest_group = _metric_value(metrics.get("largest_group")) or "unavailable"
    largest_value = _format_metric(metrics.get("largest_group_value"))
    largest_percent = _format_metric(metrics.get("largest_group_percent"))
    high_overlap_count = _format_metric(metrics.get("high_overlap_theme_count"))
    grouped_rows = tables.get("grouped_rows", [])[:8]
    view["headline"] = "Concentration: Approved Themes"
    view["summary_text"] = (
        f"Approved theme exposure shows {largest_group} as the largest current concentration at "
        f"{largest_value} ({largest_percent}). {high_overlap_count} approved themes are flagged as high-overlap "
        "manager discussions, using synthetic local analytics only."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("lens", "Lens"),
            ("group_count", "Theme count"),
            ("largest_group", "Largest theme"),
            ("largest_group_value", "Largest theme value"),
            ("largest_group_percent", "Largest theme percent"),
            ("high_overlap_theme_count", "High-overlap themes"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(grouped_rows, row_type="theme_concentration")
    view["detail_tables"] = {
        "grouped_rows": tables.get("grouped_rows", []),
        "top_holdings": tables.get("top_holdings", []),
        "overlap_rows": tables.get("overlap_rows", []),
        "evidence_rows": tables.get("evidence_rows", []),
    }
    view["caveats"] = _view_caveats(
        input_payload,
        ["Theme concentration uses gross overlapping exposure and is a discussion prompt, not a recommendation."],
    )


def _render_scenario_impact_by_manager_analytics(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    scenario = input_payload.get("scenario", {})
    display_name = scenario.get("display_name") or "Selected scenario"
    impact = _format_metric(metrics.get("total_scenario_impact"))
    impact_percent = _format_metric(metrics.get("total_scenario_impact_percent"))
    manager_rows = tables.get("manager_impacts", [])
    theme_rows = tables.get("theme_impacts", [])[:6]
    view["headline"] = f"{display_name} Analytic Impact: {impact}"
    view["summary_text"] = (
        f"The {display_name} scenario shows a deterministic synthetic portfolio impact of {impact} "
        f"({impact_percent}). Manager and approved-theme impacts are shown together so the advisor can review "
        "where the stress concentrates; this scenario is not a forecast or probability estimate."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("base_total_value", "Base value"),
            ("scenario_total_value", "Scenario value"),
            ("total_scenario_impact", "Total scenario impact"),
            ("total_scenario_impact_percent", "Total scenario impact percent"),
            ("manager_count", "Manager rows"),
            ("theme_count", "Theme rows"),
        ],
    )
    view["key_metrics"].append(_simple_metric("Scenario", display_name))
    view["evidence_rows"] = _normalize_rows(manager_rows, row_type="manager_scenario_impact") + _normalize_rows(theme_rows, row_type="theme_scenario_impact")
    view["detail_tables"] = {
        "manager_impacts": tables.get("manager_impacts", []),
        "theme_impacts": tables.get("theme_impacts", []),
        "repeated_vulnerable_themes": tables.get("repeated_vulnerable_themes", []),
        "repeated_vulnerable_managers": tables.get("repeated_vulnerable_managers", []),
        "repeated_defensive_themes": tables.get("repeated_defensive_themes", []),
        "repeated_defensive_managers": tables.get("repeated_defensive_managers", []),
    }
    view["scenario"] = scenario
    view["caveats"] = _view_caveats(
        input_payload,
        ["Deterministic synthetic scenario output only; not a forecast, probability estimate, guarantee, or manager recommendation."],
    )


def _render_manager_comparison_analytics(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    manager_rows = tables.get("manager_rows", [])
    largest_value = _format_metric(metrics.get("largest_manager_theme_exposure"))
    manager_count = _format_metric(metrics.get("manager_count"))
    review_count = _format_metric(metrics.get("review_required_manager_count"))
    view["headline"] = "Manager Comparison: Theme Overlap"
    view["summary_text"] = (
        f"The analytic comparison includes {manager_count} managers. The largest gross approved-theme exposure is "
        f"{largest_value}, and {review_count} managers carry review-required exposure flags. Rows support discussion "
        "of overlap and confidence, not manager rankings."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("manager_count", "Managers"),
            ("largest_manager_theme_exposure", "Largest gross theme exposure"),
            ("high_overlap_theme_count", "Max high-overlap themes"),
            ("review_required_manager_count", "Managers with review-required exposure"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(manager_rows, row_type="analytic_manager_comparison")
    view["detail_tables"] = {
        "manager_rows": manager_rows,
        "manager_confidence_rows": tables.get("manager_confidence_rows", []),
        "overlap_rows": tables.get("overlap_rows", []),
    }
    view["caveats"] = _view_caveats(
        input_payload,
        ["Analytic manager comparison uses synthetic overlap evidence; it is not a recommendation or ranking."],
    )


def _render_data_confidence_note_analytics(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    metrics = input_payload.get("headline_metrics", {})
    tables = input_payload.get("tables", {})
    label = _metric_value(metrics.get("confidence_label")) or _confidence_label(input_payload)
    human_count = _format_metric(metrics.get("human_review_count"))
    human_value = _format_metric(metrics.get("human_review_value"))
    confidence_rows = tables.get("confidence_rows", [])
    view["headline"] = f"Data Confidence Note: {label}"
    view["summary_text"] = (
        f"Synthetic source readiness is labeled {label}. Human review covers {human_count} positions "
        f"representing {human_value}; the analytic rows separate high, medium, review-required, low, and unknown "
        "confidence before report use."
    )
    view["key_metrics"] = _metrics_from_headlines(
        metrics,
        [
            ("confidence_label", "Confidence label"),
            ("human_review_count", "Human-review positions"),
            ("human_review_value", "Human-review value"),
            ("direct_or_cash_value", "High-confidence value"),
            ("proxy_or_stale_value", "Other confidence value"),
        ],
    )
    view["evidence_rows"] = _normalize_rows(confidence_rows, row_type="confidence_bucket")
    view["detail_tables"] = {
        "confidence_rows": confidence_rows,
        "valuation_treatment_rows": tables.get("valuation_treatment_rows", []),
        "review_rows": tables.get("review_rows", []),
        "theme_confidence_rows": tables.get("theme_confidence_rows", []),
    }
    view["caveats"] = _view_caveats(
        input_payload,
        ["Confidence describes synthetic source readiness and valuation treatment, not investment quality."],
    )


def _render_generic(input_payload: dict[str, Any], view: dict[str, Any]) -> None:
    view["headline"] = str(input_payload.get("element_title") or input_payload.get("element_id") or "Report element")
    view["summary_text"] = "Structured synthetic report-element input rendered with the generic fallback view."
    view["key_metrics"] = _metrics_from_headlines(input_payload.get("headline_metrics", {}), [])
    if not view["key_metrics"]:
        view["key_metrics"] = [_simple_metric("Metric availability", "No headline metrics were supplied")]
    view["evidence_rows"] = _normalize_rows(input_payload.get("evidence_items", []), row_type="evidence")
    view["detail_tables"] = input_payload.get("tables", {})
    view["caveats"] = _view_caveats(input_payload, ["Generic fallback renderer; review before using in a preview flow."])


def _base_view(input_payload: dict[str, Any], source_input_path: str | Path | None) -> dict[str, Any]:
    return {
        "schema_version": VIEW_SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "renderer_version": RENDERER_VERSION,
        "view_type": "report_element_view",
        "render_type": "markdown_html_fragment",
        "element_id": input_payload.get("element_id"),
        "element_title": input_payload.get("element_title"),
        "template_category": input_payload.get("template_category"),
        "as_of_date": input_payload.get("as_of_date"),
        "headline": "",
        "summary_text": "",
        "key_metrics": [],
        "evidence_rows": [],
        "detail_tables": {},
        "caveats": [],
        "confidence_summary": input_payload.get("confidence_summary", {}),
        "human_review_items": input_payload.get("human_review_items", []),
        "source_input_path": _normalize_path(source_input_path) if source_input_path else None,
        "input_parameters": input_payload.get("parameters_used", {}),
        "input_variant": input_payload.get("input_variant"),
        "source_analytic_pack": input_payload.get("source_analytic_pack"),
        "synthetic_data": True,
    }


def _ensure_view(input_payload: dict[str, Any]) -> dict[str, Any]:
    if input_payload.get("schema_version") == VIEW_SCHEMA_VERSION:
        return input_payload
    return render_report_element_view(input_payload)


def _ordered_input_files(input_path: Path, summary_filename: str) -> list[Path]:
    summary_path = input_path / summary_filename
    if summary_path.exists():
        summary = _load_json(summary_path)
        ordered = []
        for filename in summary.get("output_files", []):
            if filename == summary_filename:
                continue
            path = input_path / filename
            if path.exists():
                ordered.append(path)
        if ordered:
            return ordered
    return sorted(path for path in input_path.glob("*.json") if path.name != summary_filename)


def _build_summary(
    input_path: Path,
    output_path: Path,
    rendered: list[dict[str, Any]],
    output_files: list[str],
    *,
    output_summary_filename: str,
    summary_kind: str,
) -> dict[str, Any]:
    validation_results = {row["view_file"]: row["validation"] for row in rendered}
    statuses = {result["status"] for result in validation_results.values()}
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "renderer_version": RENDERER_VERSION,
        "summary_kind": summary_kind,
        "synthetic_data": True,
        "input_dir": _normalize_path(input_path),
        "output_dir": _normalize_path(output_path),
        "view_count": len(rendered),
        "markdown_fragment_count": len(rendered),
        "html_fragment_count": len(rendered),
        "rendered_elements": [row["element_id"] for row in rendered],
        "output_files": output_files + [output_summary_filename],
        "rendered_files": rendered,
        "validation_status": "valid" if statuses == {"valid"} else "invalid",
        "validation_results": validation_results,
        "caveat": "Report-element view fragments only; no full client briefing, charts, browser UI integration, persistence, live data, or external APIs are produced.",
    }


def _metrics_from_headlines(metrics: dict[str, Any], keys: list[tuple[str, str]]) -> list[dict[str, Any]]:
    if not keys:
        keys = [(key, key.replace("_", " ").title()) for key in metrics]
    rendered = []
    for key, label in keys:
        if key in metrics:
            rendered.append(_metric_from_headline(label, metrics[key]))
    return rendered


def _metric_from_headline(label: str, metric: Any) -> dict[str, Any]:
    if isinstance(metric, dict):
        value = metric.get("value")
        unit = metric.get("unit")
    else:
        value = metric
        unit = None
    return {
        "label": label,
        "value": value,
        "unit": unit,
        "formatted_value": _format_value(value, unit),
        "synthetic_data": True,
    }


def _simple_metric(label: str, value: Any) -> dict[str, Any]:
    return {
        "label": label,
        "value": value,
        "unit": None,
        "formatted_value": _format_value(value, None),
        "synthetic_data": True,
    }


def _metric_value(metric: Any) -> Any:
    if isinstance(metric, dict):
        return metric.get("value")
    return metric


def _format_metric(metric: Any) -> str:
    if isinstance(metric, dict):
        return _format_value(metric.get("value"), metric.get("unit"))
    return _format_value(metric, None)


def _format_value(value: Any, unit: Any = None) -> str:
    if value is None:
        return "unavailable"
    if unit == "USD":
        return _format_money(float(value))
    if unit == "ratio":
        return _format_percent(float(value))
    if unit == "count":
        return str(int(value))
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _format_money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _normalize_rows(rows: Any, row_type: str) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    normalized = []
    for row in rows:
        if isinstance(row, dict):
            copy = dict(row)
            copy.setdefault("row_type", row_type)
            normalized.append(copy)
    return normalized


def _view_caveats(input_payload: dict[str, Any], extra: list[str]) -> list[str]:
    caveats = [
        "Synthetic demo data only.",
        "Rendered report-element fragment only; not a full client briefing, chart, or production report.",
    ]
    for caveat in input_payload.get("caveats", []):
        if caveat not in caveats:
            caveats.append(caveat)
    for caveat in extra:
        if caveat not in caveats:
            caveats.append(caveat)
    return caveats


def _is_analytic_input(input_payload: dict[str, Any]) -> bool:
    return input_payload.get("input_variant") == ANALYTIC_INPUT_VARIANT


def _confidence_label(input_payload: dict[str, Any]) -> str:
    confidence = input_payload.get("confidence_summary", {})
    return str(confidence.get("label") or "unknown")


def _evidence_columns(view: dict[str, Any]) -> list[str]:
    element_id = view.get("element_id")
    if view.get("input_variant") == ANALYTIC_INPUT_VARIANT:
        if element_id == "portfolio_status":
            return ["id", "display_name", "value", "percent_of_total", "status_text"]
        if element_id == "concentration":
            return ["theme_display_name", "value", "percent_of_total", "overlap_level", "manager_count"]
        if element_id == "scenario_impact_by_manager":
            return ["row_type", "manager_name", "theme_display_name", "base_value", "scenario_impact", "scenario_impact_percent"]
        if element_id == "manager_comparison":
            return ["manager_name", "theme_exposure_value", "shared_theme_count", "high_overlap_theme_count", "review_required_value"]
        if element_id == "data_confidence_note":
            return ["id", "count", "value", "percent_of_total", "advisor_language"]
    if element_id == "portfolio_status":
        return ["manager_name", "value", "percent_of_total"]
    if element_id == "concentration":
        return ["row_type", "id", "display_name", "manager_name", "value", "percent_of_total"]
    if element_id == "scenario_impact_by_manager":
        return ["manager_name", "base_value", "scenario_value", "scenario_impact", "scenario_impact_percent"]
    if element_id == "cash_generation_summary":
        return ["manager_name", "current_cash_like_value", "income_distributions", "transaction_flows", "fees"]
    if element_id == "manager_comparison":
        return ["manager_name", "mandate", "current_value", "value_change", "primary_themes", "human_review_count"]
    if element_id == "data_confidence_note":
        return ["row_type", "id", "count", "value", "percent_of_total"]
    keys: list[str] = []
    for row in view.get("evidence_rows", []):
        for key in row:
            if key not in keys:
                keys.append(key)
            if len(keys) == 5:
                return keys
    return keys


def _markdown_metric_table(metrics: list[dict[str, Any]]) -> list[str]:
    if not metrics:
        return ["### Key Metrics", "", "No key metrics were supplied for this view."]
    lines = ["### Key Metrics", "", "| Metric | Value |", "| --- | --- |"]
    for metric in metrics:
        lines.append(f"| {_markdown_text(metric.get('label'))} | {_markdown_text(metric.get('formatted_value'))} |")
    return lines


def _markdown_rows(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    if not rows or not columns:
        return ["No evidence rows supplied."]
    lines = [
        "| " + " | ".join(_markdown_text(_column_label(column)) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows[:12]:
        lines.append("| " + " | ".join(_markdown_text(_format_cell(row.get(column), column)) for column in columns) + " |")
    return lines


def _markdown_confidence(confidence: dict[str, Any]) -> list[str]:
    label = confidence.get("label")
    lines = []
    if label:
        lines.append(f"- Label: {_markdown_text(label)}")
    human_count = confidence.get("human_review_count")
    human_value = confidence.get("human_review_value")
    if human_count is not None:
        lines.append(f"- Human-review count: {_markdown_text(_format_value(human_count, 'count'))}")
    if human_value is not None:
        lines.append(f"- Human-review value: {_markdown_text(_format_money(float(human_value)))}")
    return lines or ["- Confidence summary supplied in structured payload."]


def _html_rows(rows: list[dict[str, Any]], columns: list[str], labels: dict[str, str]) -> str:
    if not rows or not columns:
        return "<p>No rows supplied.</p>"
    parts = ["<table>", "<thead><tr>"]
    for column in columns:
        parts.append(f"<th>{html.escape(labels.get(column, _column_label(column)))}</th>")
    parts.append("</tr></thead>")
    parts.append("<tbody>")
    for row in rows[:12]:
        parts.append("<tr>")
        for column in columns:
            parts.append(f"<td>{html.escape(_format_cell(row.get(column), column))}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def _html_confidence(confidence: dict[str, Any]) -> str:
    items = _markdown_confidence(confidence)
    parts = ["<ul>"]
    for item in items:
        parts.append(f"<li>{html.escape(item.removeprefix('- '))}</li>")
    parts.append("</ul>")
    return "".join(parts)


def _column_labels(columns: list[str]) -> dict[str, str]:
    return {column: _column_label(column) for column in columns}


def _column_label(column: str) -> str:
    return column.replace("_", " ").title()


def _format_cell(value: Any, column: str) -> str:
    if value is None:
        return ""
    if column.endswith("percent") or column == "percent_of_total" or column.startswith("percent_"):
        return _format_percent(float(value))
    if column.endswith("value") or "impact" in column or column in {"transaction_flows", "income_distributions", "fees", "current_cash_like_value"}:
        if isinstance(value, (int, float)):
            return _format_money(float(value))
    return _format_value(value, None)


def _markdown_text(value: Any) -> str:
    text = _format_value(value, None)
    return text.replace("|", "\\|").replace("\n", " ")


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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


def _walk_strings(value: Any, path: str = "view") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, str):
        found.append((path, value))
    elif isinstance(value, dict):
        for key, child in value.items():
            if key == "validation":
                continue
            found.extend(_walk_strings(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_walk_strings(child, f"{path}[{index}]"))
    return found


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})


def main() -> None:
    result = render_all_demo_report_element_views()
    summary = result["summary"]
    print(
        "report element views rendered: "
        f"{summary['view_count']} views; "
        f"markdown={summary['markdown_fragment_count']}; "
        f"html={summary['html_fragment_count']}; "
        f"status={summary['validation_status']}"
    )
    print("elements: " + ", ".join(summary["rendered_elements"]))


if __name__ == "__main__":
    main()
