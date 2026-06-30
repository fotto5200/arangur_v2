"""Map synthetic simulation outputs into report-element input payloads."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arangur.report_elements.catalog import get_template


SCHEMA_VERSION = "report_element_input_payload.v1"
SUMMARY_SCHEMA_VERSION = "report_element_input_summary.v1"
MAPPER_VERSION = "report_element_input_mapping.v1"
GENERATED_AT = "2026-06-30T00:00:00Z"

DEFAULT_SIMULATION_DIR = Path("data/simulation")
DEFAULT_OUTPUT_DIR = DEFAULT_SIMULATION_DIR / "report_element_inputs"

DEFAULT_SOURCE_PATHS = {
    "position_universe": DEFAULT_SIMULATION_DIR / "synthetic_position_universe.json",
    "market_state_history": DEFAULT_SIMULATION_DIR / "synthetic_market_state_history.json",
    "scenario_market_states": DEFAULT_SIMULATION_DIR / "synthetic_scenario_market_states.json",
    "daily_position_valuation_history": DEFAULT_SIMULATION_DIR / "daily_position_valuation_history.json",
    "daily_portfolio_valuation_history": DEFAULT_SIMULATION_DIR / "daily_portfolio_valuation_history.json",
    "value_change_package": DEFAULT_SIMULATION_DIR / "value_change_package.json",
    "scenario_revaluation_results": DEFAULT_SIMULATION_DIR / "scenario_revaluation_results.json",
    "simplified_valuation_summary": DEFAULT_SIMULATION_DIR / "simplified_valuation_summary.json",
}

DEFAULT_DEMO_PAYLOAD_SPECS = [
    ("portfolio_status.json", "portfolio_status", {"branch": "Client Briefing", "placement": "Main body", "scope": "Whole portfolio"}),
    (
        "concentration_theme.json",
        "concentration",
        {
            "branch": "Advisor Review",
            "placement": "Risk review",
            "scope": "Whole portfolio",
            "lens": "Theme",
            "metric": "Market value",
        },
    ),
    (
        "concentration_sector_industry.json",
        "concentration",
        {
            "branch": "Advisor Review",
            "placement": "Risk review",
            "scope": "Whole portfolio",
            "lens": "Sector / Industry",
            "metric": "Market value",
        },
    ),
    (
        "scenario_impact_by_manager_ai_chip_selloff.json",
        "scenario_impact_by_manager",
        {
            "branch": "Advisor Review",
            "placement": "Scenario appendix",
            "scope": "All managers compared",
            "scenario_id": "ai_chip_selloff",
        },
    ),
    (
        "cash_generation_summary.json",
        "cash_generation_summary",
        {"branch": "Client Briefing", "placement": "Main body", "scope": "All managers compared", "period_days": 90},
    ),
    (
        "manager_comparison.json",
        "manager_comparison",
        {
            "branch": "Advisor Review",
            "placement": "Manager review",
            "scope": "All managers compared",
            "metric": "Current value and period value change",
        },
    ),
    (
        "data_confidence_note.json",
        "data_confidence_note",
        {"branch": "Client Briefing", "placement": "Appendix", "scope": "Whole portfolio"},
    ),
]

REAL_DATA_MARKERS = {
    "access_token",
    "api key",
    "private key",
    "bloomberg",
    "factset",
    "refinitiv",
    "morningstar direct",
}

REPORT_GENERATION_KEYS = {
    "browser_ui",
    "chart",
    "chart_config",
    "client_briefing",
    "html",
    "html_report",
    "markdown",
    "markdown_report",
    "rendered_report",
    "report_artifacts",
    "report_links",
    "report_package",
    "ui_route",
}


def load_simulation_outputs(
    source_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    """Load the committed synthetic simulation outputs needed by the mapper."""

    paths = {key: Path(value) for key, value in DEFAULT_SOURCE_PATHS.items()}
    if source_paths:
        paths.update({key: Path(value) for key, value in source_paths.items()})

    outputs = {key: _load_json(path) for key, path in paths.items()}
    outputs["_source_paths"] = {key: str(path).replace("\\", "/") for key, path in paths.items()}
    outputs["_positions_by_id"] = {
        position["position_id"]: position
        for position in outputs["position_universe"].get("positions", [])
    }
    outputs["_managers_by_id"] = {
        manager["manager_id"]: manager
        for manager in outputs["position_universe"].get("managers", [])
    }
    latest_portfolio = outputs["daily_portfolio_valuation_history"]["daily_portfolio_valuations"][-1]
    outputs["_latest_portfolio_valuation"] = latest_portfolio
    latest_date = latest_portfolio["valuation_date"]
    outputs["_latest_position_valuations"] = [
        record
        for record in outputs["daily_position_valuation_history"].get("position_valuations", [])
        if record.get("valuation_date") == latest_date
    ]
    outputs["_latest_position_valuations_by_id"] = {
        record["position_id"]: record
        for record in outputs["_latest_position_valuations"]
    }
    return outputs


def build_report_element_input(
    element_id: str,
    parameters: dict[str, Any] | None,
    simulation_outputs: dict[str, Any],
) -> dict[str, Any]:
    """Build one renderer-ready input payload for a supported report-element template."""

    parameters = dict(parameters or {})
    if element_id == "portfolio_status":
        payload = _build_portfolio_status(parameters, simulation_outputs)
    elif element_id == "concentration":
        payload = _build_concentration(parameters, simulation_outputs)
    elif element_id == "scenario_impact_by_manager":
        payload = _build_scenario_impact_by_manager(parameters, simulation_outputs)
    elif element_id == "cash_generation_summary":
        payload = _build_cash_generation_summary(parameters, simulation_outputs)
    elif element_id == "manager_comparison":
        payload = _build_manager_comparison(parameters, simulation_outputs)
    elif element_id == "data_confidence_note":
        payload = _build_data_confidence_note(parameters, simulation_outputs)
    else:
        payload = _invalid_payload(
            element_id,
            parameters,
            simulation_outputs,
            "UNKNOWN_ELEMENT_ID",
            f"Unsupported report element template: {element_id}",
        )
    payload["validation"] = validate_report_element_input(payload)
    return payload


def build_all_demo_report_element_inputs(
    simulation_outputs: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Build the default fixture payload set for the initial template catalog."""

    outputs = simulation_outputs or load_simulation_outputs()
    return {
        filename: build_report_element_input(element_id, parameters, outputs)
        for filename, element_id, parameters in DEFAULT_DEMO_PAYLOAD_SPECS
    }


def validate_report_element_input(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate common and element-specific report-element input payload fields."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(payload, dict):
        return {"status": "invalid", "errors": [{"code": "PAYLOAD_NOT_OBJECT", "message": "Payload must be an object"}], "warnings": []}

    for field in (
        "schema_version",
        "element_id",
        "element_title",
        "template_category",
        "parameters_used",
        "as_of_date",
        "source_data",
        "headline_metrics",
        "evidence_items",
        "tables",
        "confidence_summary",
        "caveats",
        "human_review_items",
        "synthetic_data",
    ):
        if field not in payload:
            _add_issue(errors, "MISSING_FIELD", field, f"Missing required field: {field}")

    if payload.get("schema_version") != SCHEMA_VERSION:
        _add_issue(errors, "SCHEMA_VERSION_MISMATCH", "schema_version", f"Expected {SCHEMA_VERSION}")
    if payload.get("synthetic_data") is not True:
        _add_issue(errors, "SYNTHETIC_DATA_REQUIRED", "synthetic_data", "Payload must be marked synthetic_data=true")
    if not isinstance(payload.get("headline_metrics"), dict) or not payload.get("headline_metrics"):
        _add_issue(errors, "HEADLINE_METRICS_REQUIRED", "headline_metrics", "headline_metrics must be a non-empty object")
    if not isinstance(payload.get("confidence_summary"), dict) or not payload.get("confidence_summary"):
        _add_issue(errors, "CONFIDENCE_SUMMARY_REQUIRED", "confidence_summary", "confidence_summary must be a non-empty object")
    if not isinstance(payload.get("caveats"), list) or not payload.get("caveats"):
        _add_issue(errors, "CAVEATS_REQUIRED", "caveats", "caveats must be a non-empty list")

    source_data = payload.get("source_data")
    if isinstance(source_data, dict):
        for source_key in ("position_universe", "market_state", "valuation_history", "scenario_results"):
            if source_key not in source_data:
                _add_issue(errors, "SOURCE_DATA_REQUIRED", f"source_data.{source_key}", f"Missing source data reference: {source_key}")

    tables = payload.get("tables") if isinstance(payload.get("tables"), dict) else {}
    element_id = payload.get("element_id")
    if element_id == "portfolio_status":
        _require_table(tables, "manager_values", errors)
        _require_table(tables, "asset_class_values", errors)
        _require_table(tables, "theme_values", errors)
    elif element_id == "concentration":
        _require_table(tables, "grouped_rows", errors)
        _require_table(tables, "top_holdings", errors)
    elif element_id == "scenario_impact_by_manager":
        if "scenario" not in payload:
            _add_issue(errors, "SCENARIO_REQUIRED", "scenario", "Scenario impact payloads must include scenario metadata")
        _require_table(tables, "manager_impacts", errors)
        _require_table(tables, "top_position_impacts", errors)
    elif element_id == "cash_generation_summary":
        if "period" not in payload:
            _add_issue(errors, "PERIOD_REQUIRED", "period", "Cash generation payloads must include period metadata")
        _require_table(tables, "cash_generation_by_manager", errors)
        _require_table(tables, "cash_like_positions", errors)
    elif element_id == "manager_comparison":
        _require_table(tables, "manager_rows", errors)
    elif element_id == "data_confidence_note":
        _require_table(tables, "confidence_rows", errors)
        _require_table(tables, "valuation_treatment_rows", errors)
    elif element_id and element_id != "_invalid":
        _add_issue(errors, "UNKNOWN_ELEMENT_ID", "element_id", f"Unsupported report element template: {element_id}")

    if payload.get("status") == "invalid":
        validation_errors = payload.get("validation_errors", [])
        if isinstance(validation_errors, list):
            for issue in validation_errors:
                if isinstance(issue, dict):
                    errors.append(issue)
        else:
            _add_issue(errors, "INVALID_PAYLOAD", "validation_errors", "Payload status is invalid")

    _validate_no_real_data_markers(payload, errors)
    _validate_no_report_generation_keys(payload, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "mapper_version": MAPPER_VERSION,
        "validated_at": GENERATED_AT,
    }


def write_demo_report_element_inputs(
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    simulation_outputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write the default payload fixtures and a compact summary JSON file."""

    output_path = Path(output_dir)
    outputs = simulation_outputs or load_simulation_outputs()
    payloads = build_all_demo_report_element_inputs(outputs)
    output_path.mkdir(parents=True, exist_ok=True)
    for filename, payload in payloads.items():
        _write_json(output_path / filename, payload)

    summary = _build_output_summary(output_path, payloads, outputs)
    _write_json(output_path / "report_element_input_summary.json", summary)
    return {"payloads": payloads, "summary": summary}


def _build_portfolio_status(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    latest = outputs["_latest_portfolio_valuation"]
    summary = outputs["simplified_valuation_summary"]
    payload = _base_payload("portfolio_status", parameters, outputs)
    payload.update(
        {
            "headline_metrics": {
                "total_portfolio_value": _money_metric(latest["total_value"], latest["reporting_currency"]),
                "cash_value": _money_metric(latest["cash_value"], latest["reporting_currency"]),
                "manager_count": {"value": len(outputs["_managers_by_id"]), "unit": "count"},
                "position_count": {"value": summary["position_count"], "unit": "count"},
                "human_review_count": {"value": latest["human_review_count"], "unit": "count"},
                "human_review_value": _money_metric(latest["human_review_value"], latest["reporting_currency"]),
            },
            "evidence_items": _named_contributors(outputs["value_change_package"].get("largest_negative_contributors", [])[:5], outputs),
            "tables": {
                "manager_values": _annotate_manager_rows(latest["value_by_manager"], outputs),
                "asset_class_values": latest["value_by_asset_class"],
                "theme_values": latest["value_by_theme"],
                "liquidity_values": latest["value_by_liquidity_bucket"],
            },
            "human_review_items": latest["human_review_items"],
            "confidence_summary": _confidence_summary_payload(latest["confidence_summary"]),
            "caveats": _common_caveats(latest.get("caveats", [])),
        }
    )
    return payload


def _build_concentration(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    latest = outputs["_latest_portfolio_valuation"]
    lens = str(parameters.get("lens") or "Theme")
    payload = _base_payload("concentration", parameters, outputs)
    grouped_rows = _concentration_grouped_rows(lens, outputs)
    top_holdings = _top_holdings(outputs)
    overlap_rows = _overlap_rows(outputs)
    largest_group = grouped_rows[0] if grouped_rows else {"id": "none", "value": 0.0, "percent_of_total": 0.0}
    payload.update(
        {
            "headline_metrics": {
                "lens": {"value": lens, "unit": "label"},
                "group_count": {"value": len(grouped_rows), "unit": "count"},
                "largest_group": {"value": largest_group["id"], "unit": "label"},
                "largest_group_value": _money_metric(largest_group.get("value", 0.0), latest["reporting_currency"]),
                "largest_group_percent": {"value": largest_group.get("percent_of_total", 0.0), "unit": "ratio"},
                "top_holding_value": _money_metric(top_holdings[0]["value"] if top_holdings else 0.0, latest["reporting_currency"]),
            },
            "evidence_items": top_holdings[:5],
            "tables": {
                "grouped_rows": grouped_rows,
                "top_holdings": top_holdings,
                "overlap_exposure_rows": overlap_rows,
            },
            "human_review_items": latest["human_review_items"],
            "confidence_summary": _confidence_summary_payload(latest["confidence_summary"]),
            "caveats": _common_caveats(
                [
                    "Concentration rows are grouped from synthetic current valuation records.",
                    "Theme exposure is split equally across each position's assigned themes.",
                    "Overlap exposure is inferred from repeated synthetic display names across managers.",
                ]
            ),
        }
    )
    return payload


def _build_scenario_impact_by_manager(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    scenario_id = str(parameters.get("scenario_id") or "ai_chip_selloff")
    scenarios = outputs["scenario_revaluation_results"].get("scenario_results", [])
    scenario = next((row for row in scenarios if row.get("scenario_id") == scenario_id), None)
    if scenario is None:
        payload = _invalid_payload(
            "scenario_impact_by_manager",
            parameters,
            outputs,
            "SCENARIO_NOT_FOUND",
            f"Scenario id not found in synthetic scenario revaluation results: {scenario_id}",
        )
        payload["headline_metrics"] = {"requested_scenario_id": {"value": scenario_id, "unit": "id"}}
        payload["tables"] = {"manager_impacts": [], "top_position_impacts": []}
        payload["confidence_summary"] = _confidence_summary_payload(outputs["_latest_portfolio_valuation"]["confidence_summary"])
        payload["human_review_items"] = []
        payload["caveats"] = _common_caveats(["Requested scenario is unavailable; choose a scenario id emitted by Surface 3."])
        return payload

    payload = _base_payload("scenario_impact_by_manager", parameters, outputs)
    top_impacts = sorted(
        scenario.get("position_impacts", []),
        key=lambda row: abs(float(row.get("scenario_impact", 0.0))),
        reverse=True,
    )[:10]
    payload.update(
        {
            "scenario": {
                "scenario_id": scenario["scenario_id"],
                "display_name": scenario["display_name"],
                "horizon": scenario["horizon"],
                "scenario_date": scenario["scenario_date"],
                "description": _scenario_description(scenario["scenario_id"], outputs),
                "scenario_completeness": scenario["scenario_completeness"],
                "synthetic_data": True,
            },
            "headline_metrics": {
                "base_total_value": _money_metric(scenario["base_total_value"], outputs["_latest_portfolio_valuation"]["reporting_currency"]),
                "scenario_total_value": _money_metric(scenario["scenario_total_value"], outputs["_latest_portfolio_valuation"]["reporting_currency"]),
                "total_scenario_impact": _money_metric(scenario["total_scenario_impact"], outputs["_latest_portfolio_valuation"]["reporting_currency"]),
                "total_scenario_impact_percent": {"value": scenario["total_scenario_impact_percent"], "unit": "ratio"},
                "manager_count": {"value": len(scenario["manager_impacts"]), "unit": "count"},
            },
            "evidence_items": _position_impact_rows(top_impacts, outputs),
            "tables": {
                "manager_impacts": _annotate_manager_rows(scenario["manager_impacts"], outputs),
                "top_position_impacts": _position_impact_rows(top_impacts, outputs),
                "theme_impacts": scenario["theme_impacts"],
                "asset_class_impacts": scenario["asset_class_impacts"],
            },
            "human_review_items": scenario.get("human_review_items", []),
            "confidence_summary": _confidence_summary_payload(scenario["confidence_summary"]),
            "caveats": _common_caveats(scenario.get("caveats", [])),
        }
    )
    return payload


def _build_cash_generation_summary(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    latest = outputs["_latest_portfolio_valuation"]
    package = outputs["value_change_package"]
    period_days = int(parameters.get("period_days") or 90)
    cash_positions = [
        _position_row(record, outputs)
        for record in outputs["_latest_position_valuations"]
        if record.get("instrument_type") in {"cash", "money_market"}
    ]
    manager_rows = _cash_generation_by_manager(period_days, outputs)
    payload = _base_payload("cash_generation_summary", parameters, outputs)
    payload.update(
        {
            "period": {
                "start_date": package["start_date"],
                "end_date": package["end_date"],
                "period_days": period_days,
                "basis": "synthetic_valuation_period",
            },
            "headline_metrics": {
                "current_cash_value": _money_metric(latest["cash_value"], latest["reporting_currency"]),
                "period_income_distributions": _money_metric(package["total_income_distributions"], latest["reporting_currency"]),
                "period_transaction_flows": _money_metric(package["total_transactions_or_flows"], latest["reporting_currency"]),
                "period_fees": _money_metric(package["total_fees"], latest["reporting_currency"]),
                "cash_like_position_count": {"value": len(cash_positions), "unit": "count"},
            },
            "evidence_items": manager_rows[:5],
            "tables": {
                "cash_generation_by_manager": manager_rows,
                "cash_like_positions": cash_positions,
                "value_change_by_manager": _annotate_manager_rows(package["value_change_by_manager"], outputs),
            },
            "human_review_items": latest["human_review_items"],
            "confidence_summary": _confidence_summary_payload(latest["confidence_summary"]),
            "caveats": _common_caveats(
                [
                    "Cash generation is a simplified synthetic summary from transactions and valuation outputs.",
                    "This payload separates flows, income/distributions, fees, and current cash-like positions without statement-grade cash accounting.",
                ]
            ),
        }
    )
    return payload


def _build_manager_comparison(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    latest = outputs["_latest_portfolio_valuation"]
    manager_rows = _manager_comparison_rows(outputs)
    payload = _base_payload("manager_comparison", parameters, outputs)
    payload.update(
        {
            "headline_metrics": {
                "manager_count": {"value": len(manager_rows), "unit": "count"},
                "largest_manager_value": _money_metric(max((row["current_value"] for row in manager_rows), default=0.0), latest["reporting_currency"]),
                "human_review_manager_count": {"value": sum(1 for row in manager_rows if row["human_review_count"] > 0), "unit": "count"},
                "period_economic_value_change": _money_metric(outputs["value_change_package"]["total_market_or_economic_change"], latest["reporting_currency"]),
            },
            "evidence_items": sorted(manager_rows, key=lambda row: float(row["current_value"]), reverse=True)[:5],
            "tables": {
                "manager_rows": manager_rows,
                "value_change_by_manager": _annotate_manager_rows(outputs["value_change_package"]["value_change_by_manager"], outputs),
            },
            "human_review_items": latest["human_review_items"],
            "confidence_summary": _confidence_summary_payload(latest["confidence_summary"]),
            "caveats": _common_caveats(
                [
                    "Manager comparison rows combine synthetic manager metadata, current valuation aggregates, and period value-change output.",
                    "Mandate and theme text is synthetic metadata, not due diligence or recommendation language.",
                ]
            ),
        }
    )
    return payload


def _build_data_confidence_note(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    latest = outputs["_latest_portfolio_valuation"]
    summary = outputs["simplified_valuation_summary"]
    confidence = latest["confidence_summary"]
    confidence_rows = confidence["by_confidence"]
    tier_rows = confidence["by_valuation_tier"]
    payload = _base_payload("data_confidence_note", parameters, outputs)
    payload.update(
        {
            "headline_metrics": {
                "confidence_label": {"value": _confidence_label(confidence_rows), "unit": "label"},
                "human_review_count": {"value": latest["human_review_count"], "unit": "count"},
                "human_review_value": _money_metric(latest["human_review_value"], latest["reporting_currency"]),
                "direct_or_cash_value": _money_metric(_sum_bucket_values(tier_rows, {"direct_price_or_mark", "cash_face_value"}), latest["reporting_currency"]),
                "proxy_or_stale_value": _money_metric(_sum_bucket_values(tier_rows, {"proxy_valuation", "stale_or_manager_mark"}), latest["reporting_currency"]),
            },
            "evidence_items": latest["human_review_items"][:8],
            "tables": {
                "confidence_rows": confidence_rows,
                "valuation_treatment_rows": tier_rows,
                "data_issue_rows": _data_issue_rows(outputs),
                "market_state_treatment_rows": _market_state_treatment_rows(outputs),
            },
            "human_review_items": latest["human_review_items"],
            "confidence_summary": _confidence_summary_payload(confidence),
            "caveats": _common_caveats(
                [
                    summary["caveat"],
                    "Data confidence rows summarize synthetic valuation treatments, stale/private marks, proxy usage, and human-review flags.",
                ]
            ),
        }
    )
    return payload


def _base_payload(element_id: str, parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    template = get_template(element_id)
    if template is None:
        raise ValueError(f"Unsupported report element template: {element_id}")
    latest = outputs["_latest_portfolio_valuation"]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "mapper_version": MAPPER_VERSION,
        "element_id": template["element_id"],
        "element_title": template["title"],
        "template_category": template["category"],
        "target_branch": parameters.get("branch"),
        "placement": parameters.get("placement"),
        "parameters_used": parameters,
        "as_of_date": latest["valuation_date"],
        "portfolio_id": latest["portfolio_id"],
        "reporting_currency": latest["reporting_currency"],
        "source_data": _source_data(outputs),
        "headline_metrics": {},
        "evidence_items": [],
        "tables": {},
        "confidence_summary": {},
        "caveats": [],
        "human_review_items": [],
        "synthetic_data": True,
    }


def _invalid_payload(
    element_id: str,
    parameters: dict[str, Any],
    outputs: dict[str, Any],
    code: str,
    message: str,
) -> dict[str, Any]:
    template = get_template(element_id)
    latest = outputs["_latest_portfolio_valuation"]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "mapper_version": MAPPER_VERSION,
        "status": "invalid",
        "element_id": element_id,
        "element_title": template["title"] if template else element_id,
        "template_category": template["category"] if template else "unknown",
        "target_branch": parameters.get("branch"),
        "placement": parameters.get("placement"),
        "parameters_used": parameters,
        "as_of_date": latest["valuation_date"],
        "portfolio_id": latest["portfolio_id"],
        "reporting_currency": latest["reporting_currency"],
        "source_data": _source_data(outputs),
        "headline_metrics": {},
        "evidence_items": [],
        "tables": {},
        "confidence_summary": {},
        "caveats": [],
        "human_review_items": [],
        "validation_errors": [{"code": code, "record_id": element_id, "message": message}],
        "synthetic_data": True,
    }


def _source_data(outputs: dict[str, Any]) -> dict[str, Any]:
    paths = outputs.get("_source_paths", {})
    position_universe = outputs["position_universe"]
    market_state_history = outputs["market_state_history"]
    position_history = outputs["daily_position_valuation_history"]
    portfolio_history = outputs["daily_portfolio_valuation_history"]
    scenario_results = outputs["scenario_revaluation_results"]
    return {
        "position_universe": {
            "path": paths.get("position_universe"),
            "schema_version": position_universe.get("schema_version"),
            "universe_id": position_universe.get("universe_id"),
            "synthetic_data": True,
        },
        "market_state": {
            "path": paths.get("market_state_history"),
            "scenario_path": paths.get("scenario_market_states"),
            "schema_version": market_state_history.get("schema_version"),
            "history_id": market_state_history.get("history_id"),
            "current_market_state_id": market_state_history.get("current_market_state", {}).get("market_state_id"),
            "synthetic_data": True,
        },
        "valuation_history": {
            "daily_position_path": paths.get("daily_position_valuation_history"),
            "daily_portfolio_path": paths.get("daily_portfolio_valuation_history"),
            "value_change_path": paths.get("value_change_package"),
            "position_valuation_history_id": position_history.get("valuation_history_id"),
            "portfolio_valuation_history_id": portfolio_history.get("portfolio_valuation_history_id"),
            "synthetic_data": True,
        },
        "scenario_results": {
            "path": paths.get("scenario_revaluation_results"),
            "schema_version": scenario_results.get("schema_version"),
            "scenario_revaluation_id": scenario_results.get("scenario_revaluation_id"),
            "scenario_count": scenario_results.get("scenario_count"),
            "synthetic_data": True,
        },
    }


def _concentration_grouped_rows(lens: str, outputs: dict[str, Any]) -> list[dict[str, Any]]:
    latest = outputs["_latest_portfolio_valuation"]
    normalized_lens = " ".join(lens.lower().replace("/", " ").split())
    if normalized_lens == "theme":
        return sorted(latest["value_by_theme"], key=lambda row: float(row["value"]), reverse=True)
    if normalized_lens in {"asset class", "asset classes"}:
        return sorted(latest["value_by_asset_class"], key=lambda row: float(row["value"]), reverse=True)
    if normalized_lens in {"liquidity bucket", "liquidity"}:
        return sorted(latest["value_by_liquidity_bucket"], key=lambda row: float(row["value"]), reverse=True)
    if normalized_lens in {"holding", "holdings"}:
        return _top_holdings(outputs)
    if normalized_lens in {"data issue", "data issues"}:
        return _group_current_positions_by_classification("data_issue_category", outputs)
    if normalized_lens in {"sector industry", "sector and industry"}:
        return _group_current_positions_by_sector_industry(outputs)
    if normalized_lens == "sector":
        return _group_current_positions_by_classification("sector", outputs)
    if normalized_lens == "industry":
        return _group_current_positions_by_classification("industry", outputs)
    return _group_current_positions_by_classification("asset_class", outputs)


def _group_current_positions_by_classification(field: str, outputs: dict[str, Any]) -> list[dict[str, Any]]:
    total = float(outputs["_latest_portfolio_valuation"]["total_value"])
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: {"value": 0.0, "position_count": 0.0, "human_review_count": 0.0})
    for record in outputs["_latest_position_valuations"]:
        position = outputs["_positions_by_id"][record["position_id"]]
        group_id = str(position.get("classifications", {}).get(field) or record.get(field) or "unassigned")
        bucket = buckets[group_id]
        bucket["value"] += float(record["value"])
        bucket["position_count"] += 1
        bucket["human_review_count"] += 1 if record.get("human_review_required") else 0
    return [_concentration_bucket(group_id, values, total) for group_id, values in sorted(buckets.items(), key=lambda item: item[1]["value"], reverse=True)]


def _group_current_positions_by_sector_industry(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    total = float(outputs["_latest_portfolio_valuation"]["total_value"])
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: {"value": 0.0, "position_count": 0.0, "human_review_count": 0.0})
    for record in outputs["_latest_position_valuations"]:
        position = outputs["_positions_by_id"][record["position_id"]]
        classifications = position.get("classifications", {})
        sector = classifications.get("sector") or "unassigned"
        industry = classifications.get("industry") or "unassigned"
        group_id = f"{sector} / {industry}"
        bucket = buckets[group_id]
        bucket["value"] += float(record["value"])
        bucket["position_count"] += 1
        bucket["human_review_count"] += 1 if record.get("human_review_required") else 0
    return [_concentration_bucket(group_id, values, total) for group_id, values in sorted(buckets.items(), key=lambda item: item[1]["value"], reverse=True)]


def _concentration_bucket(group_id: str, values: dict[str, float], total: float) -> dict[str, Any]:
    return {
        "id": group_id,
        "value": _round_money(values["value"]),
        "percent_of_total": _round_percent(_safe_divide(values["value"], total)),
        "position_count": int(values["position_count"]),
        "human_review_count": int(values["human_review_count"]),
        "synthetic_data": True,
    }


def _top_holdings(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [_position_row(record, outputs) for record in outputs["_latest_position_valuations"]]
    return sorted(rows, key=lambda row: float(row["value"]), reverse=True)[:10]


def _position_row(record: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    position = outputs["_positions_by_id"][record["position_id"]]
    manager = outputs["_managers_by_id"].get(record["manager_id"], {})
    total = float(outputs["_latest_portfolio_valuation"]["total_value"])
    return {
        "position_id": record["position_id"],
        "display_name": position["display_name"],
        "manager_id": record["manager_id"],
        "manager_name": manager.get("display_name", record["manager_id"]),
        "instrument_type": record["instrument_type"],
        "asset_class": record["asset_class"],
        "themes": record.get("themes", []),
        "value": record["value"],
        "percent_of_total": _round_percent(_safe_divide(float(record["value"]), total)),
        "valuation_tier": record["valuation_tier"],
        "confidence": record["confidence"],
        "human_review_required": record["human_review_required"],
        "synthetic_data": True,
    }


def _overlap_rows(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in outputs["_latest_position_valuations"]:
        position = outputs["_positions_by_id"][record["position_id"]]
        by_name[position["display_name"]].append(record)
    total = float(outputs["_latest_portfolio_valuation"]["total_value"])
    rows = []
    for display_name, records in by_name.items():
        manager_ids = sorted({record["manager_id"] for record in records})
        if len(manager_ids) < 2:
            continue
        value = sum(float(record["value"]) for record in records)
        rows.append(
            {
                "display_name": display_name,
                "manager_ids": manager_ids,
                "position_ids": [record["position_id"] for record in records],
                "value": _round_money(value),
                "percent_of_total": _round_percent(_safe_divide(value, total)),
                "synthetic_data": True,
            }
        )
    return sorted(rows, key=lambda row: float(row["value"]), reverse=True)


def _position_impact_rows(records: list[dict[str, Any]], outputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for record in records:
        position = outputs["_positions_by_id"].get(record["position_id"], {})
        manager = outputs["_managers_by_id"].get(record["manager_id"], {})
        rows.append(
            {
                "position_id": record["position_id"],
                "display_name": record.get("display_name") or position.get("display_name"),
                "manager_id": record["manager_id"],
                "manager_name": manager.get("display_name", record["manager_id"]),
                "asset_class": record["asset_class"],
                "themes": record.get("themes", []),
                "base_value": record["base_value"],
                "scenario_value": record["scenario_value"],
                "scenario_impact": record["scenario_impact"],
                "scenario_impact_percent": record["scenario_impact_percent"],
                "valuation_tier": record["valuation_tier"],
                "confidence": record["confidence"],
                "human_review_required": record["human_review_required"],
                "synthetic_data": True,
            }
        )
    return rows


def _cash_generation_by_manager(period_days: int, outputs: dict[str, Any]) -> list[dict[str, Any]]:
    package_rows = {row["id"]: row for row in outputs["value_change_package"]["value_change_by_manager"]}
    cash_by_manager: dict[str, float] = defaultdict(float)
    for record in outputs["_latest_position_valuations"]:
        if record.get("instrument_type") in {"cash", "money_market"}:
            cash_by_manager[record["manager_id"]] += float(record["value"])
    rows = []
    for manager in sorted(outputs["position_universe"].get("managers", []), key=lambda row: row["manager_id"]):
        row = package_rows.get(manager["manager_id"], {})
        rows.append(
            {
                "manager_id": manager["manager_id"],
                "manager_name": manager["display_name"],
                "mandate": manager["mandate"],
                "period_days": period_days,
                "current_cash_like_value": _round_money(cash_by_manager[manager["manager_id"]]),
                "transaction_flows": row.get("transaction_flows", 0.0),
                "income_distributions": row.get("income_distributions", 0.0),
                "fees": row.get("fees", 0.0),
                "economic_value_change": row.get("economic_value_change", 0.0),
                "synthetic_data": True,
            }
        )
    return rows


def _manager_comparison_rows(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    latest = outputs["_latest_portfolio_valuation"]
    current_by_manager = {row["id"]: row for row in latest["value_by_manager"]}
    change_by_manager = {row["id"]: row for row in outputs["value_change_package"]["value_change_by_manager"]}
    latest_records = outputs["_latest_position_valuations"]
    rows = []
    for manager in sorted(outputs["position_universe"].get("managers", []), key=lambda row: row["manager_id"]):
        manager_id = manager["manager_id"]
        current = current_by_manager.get(manager_id, {})
        change = change_by_manager.get(manager_id, {})
        manager_records = [record for record in latest_records if record["manager_id"] == manager_id]
        human_records = [record for record in manager_records if record["human_review_required"]]
        rows.append(
            {
                "manager_id": manager_id,
                "manager_name": manager["display_name"],
                "mandate": manager["mandate"],
                "intended_role": manager["intended_role"],
                "liquidity_profile": manager["liquidity_profile"],
                "primary_themes": manager["primary_themes"],
                "current_value": current.get("value", 0.0),
                "percent_of_total": current.get("percent_of_total", 0.0),
                "opening_value": change.get("opening_value", 0.0),
                "closing_value": change.get("closing_value", current.get("value", 0.0)),
                "value_change": change.get("value_change", 0.0),
                "transaction_flows": change.get("transaction_flows", 0.0),
                "income_distributions": change.get("income_distributions", 0.0),
                "economic_value_change": change.get("economic_value_change", 0.0),
                "position_count": len(manager_records),
                "human_review_count": len(human_records),
                "human_review_value": _round_money(sum(float(record["value"]) for record in human_records)),
                "confidence_summary": _record_confidence_summary(manager_records),
                "synthetic_data": True,
            }
        )
    return rows


def _data_issue_rows(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    return _group_current_positions_by_classification("data_issue_category", outputs)


def _market_state_treatment_rows(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    completeness = outputs["market_state_history"].get("current_market_state", {}).get("completeness", {})
    rows = []
    for key, value in sorted(completeness.items()):
        if key.endswith("_count") or key in {"status", "confidence_counts"}:
            rows.append({"id": key, "value": value, "synthetic_data": True})
    confidence_counts = completeness.get("confidence_counts", {})
    if isinstance(confidence_counts, dict):
        for confidence, count in sorted(confidence_counts.items()):
            rows.append({"id": f"market_state_confidence_{confidence}", "value": count, "synthetic_data": True})
    return rows


def _record_confidence_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(float(record["value"]) for record in records)
    by_confidence: dict[str, dict[str, float]] = defaultdict(lambda: {"count": 0.0, "value": 0.0})
    for record in records:
        bucket = by_confidence[record["confidence"]]
        bucket["count"] += 1
        bucket["value"] += float(record["value"])
    return {
        "by_confidence": [
            {
                "id": confidence,
                "count": int(values["count"]),
                "value": _round_money(values["value"]),
                "percent_of_total": _round_percent(_safe_divide(values["value"], total)),
                "synthetic_data": True,
            }
            for confidence, values in sorted(by_confidence.items())
        ]
    }


def _annotate_manager_rows(rows: list[dict[str, Any]], outputs: dict[str, Any]) -> list[dict[str, Any]]:
    annotated = []
    for row in rows:
        manager = outputs["_managers_by_id"].get(row["id"], {})
        copy = dict(row)
        copy["manager_id"] = row["id"]
        copy["manager_name"] = manager.get("display_name", row["id"])
        copy["mandate"] = manager.get("mandate")
        annotated.append(copy)
    return annotated


def _named_contributors(rows: list[dict[str, Any]], outputs: dict[str, Any]) -> list[dict[str, Any]]:
    named = []
    for row in rows:
        manager = outputs["_managers_by_id"].get(row["manager_id"], {})
        copy = dict(row)
        copy["manager_name"] = manager.get("display_name", row["manager_id"])
        named.append(copy)
    return named


def _scenario_description(scenario_id: str, outputs: dict[str, Any]) -> str:
    scenario_set = outputs.get("scenario_market_states", {})
    for scenario in scenario_set.get("scenarios", []):
        if scenario.get("scenario_id") == scenario_id:
            return scenario.get("description") or scenario.get("display_name") or scenario_id
    return scenario_id


def _confidence_summary_payload(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": _confidence_label(summary.get("by_confidence", [])),
        "by_confidence": summary.get("by_confidence", []),
        "by_valuation_tier": summary.get("by_valuation_tier", []),
        "human_review_count": summary.get("human_review_count", 0),
        "human_review_value": summary.get("human_review_value", 0.0),
        "synthetic_data": True,
    }


def _confidence_label(confidence_rows: list[dict[str, Any]]) -> str:
    by_id = {row["id"]: float(row.get("percent_of_total", 0.0)) for row in confidence_rows}
    if by_id.get("high", 0.0) >= 0.7 and by_id.get("low", 0.0) + by_id.get("unknown", 0.0) <= 0.1:
        return "high"
    if by_id.get("low", 0.0) + by_id.get("unknown", 0.0) >= 0.35:
        return "low"
    return "medium"


def _common_caveats(extra: list[str]) -> list[str]:
    caveats = [
        "Synthetic demo data only.",
        "Payload is a structured input for later rendering; it is not a generated report, chart, browser view, or client-ready briefing.",
    ]
    for item in extra:
        if item not in caveats:
            caveats.append(item)
    return caveats


def _build_output_summary(
    output_path: Path,
    payloads: dict[str, dict[str, Any]],
    outputs: dict[str, Any],
) -> dict[str, Any]:
    validation_results = {
        filename: payload.get("validation", validate_report_element_input(payload))
        for filename, payload in payloads.items()
    }
    statuses = {result["status"] for result in validation_results.values()}
    latest = outputs["_latest_portfolio_valuation"]
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "mapper_version": MAPPER_VERSION,
        "synthetic_data": True,
        "output_dir": str(output_path).replace("\\", "/"),
        "payload_count": len(payloads),
        "element_ids": [payload["element_id"] for payload in payloads.values()],
        "output_files": list(payloads.keys()) + ["report_element_input_summary.json"],
        "source_files_used": outputs.get("_source_paths", {}),
        "as_of_date": latest["valuation_date"],
        "current_portfolio_value": latest["total_value"],
        "validation_status": "valid" if statuses == {"valid"} else "invalid",
        "validation_results": validation_results,
        "caveat": "Structured report-element inputs only; no final reports, charts, browser UI, persistence, live data, or external APIs are produced.",
    }


def _money_metric(value: float, currency: str) -> dict[str, Any]:
    return {"value": _round_money(float(value)), "unit": currency}


def _sum_bucket_values(rows: list[dict[str, Any]], bucket_ids: set[str]) -> float:
    return _round_money(sum(float(row.get("value", 0.0)) for row in rows if row.get("id") in bucket_ids))


def _require_table(tables: dict[str, Any], table_name: str, errors: list[dict[str, str]]) -> None:
    value = tables.get(table_name)
    if not isinstance(value, list) or not value:
        _add_issue(errors, "TABLE_REQUIRED", f"tables.{table_name}", f"Missing or empty table: {table_name}")


def _validate_no_real_data_markers(value: Any, errors: list[dict[str, str]]) -> None:
    for path, text in _walk_strings(value):
        lowered = text.lower()
        for marker in REAL_DATA_MARKERS:
            if marker in lowered:
                _add_issue(errors, "REAL_DATA_MARKER_DETECTED", path, f"String contains prohibited marker: {marker}")


def _validate_no_report_generation_keys(value: Any, errors: list[dict[str, str]]) -> None:
    for path, key in _walk_keys(value):
        if key in REPORT_GENERATION_KEYS:
            _add_issue(errors, "REPORT_GENERATION_KEY_DETECTED", path, f"Unexpected report-generation key: {key}")


def _walk_strings(value: Any, path: str = "payload") -> list[tuple[str, str]]:
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


def _walk_keys(value: Any, path: str = "payload") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.append((f"{path}.{key}", str(key)))
            found.extend(_walk_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_walk_keys(child, f"{path}[{index}]"))
    return found


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


def _safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0.0:
        return default
    return numerator / denominator


def _round_money(value: float) -> float:
    return round(float(value), 2)


def _round_percent(value: float) -> float:
    return round(float(value), 6)


def main() -> None:
    written = write_demo_report_element_inputs()
    summary = written["summary"]
    print(
        "report element inputs written: "
        f"{summary['payload_count']} payloads; "
        f"status={summary['validation_status']}; "
        f"as_of={summary['as_of_date']}; "
        f"current_value={summary['current_portfolio_value']}"
    )
    print("elements: " + ", ".join(summary["element_ids"]))


if __name__ == "__main__":
    main()
