"""Map synthetic analytic proof outputs into report-element input payloads."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arangur.report_elements.catalog import get_template
from arangur.report_elements.input_mapping import SCHEMA_VERSION, validate_report_element_input


SUMMARY_SCHEMA_VERSION = "report_element_analytic_input_summary.v1"
MAPPER_VERSION = "report_element_analytic_input_mapping.v1"
GENERATED_AT = "2026-07-03T00:00:00Z"
INPUT_VARIANT = "analytic_pack_v1"
REPORTING_CURRENCY = "USD"

DEFAULT_ANALYTICS_DIR = Path("data/simulation/analytics")
DEFAULT_OUTPUT_DIR = Path("data/simulation/report_element_inputs")

ANALYTIC_OUTPUT_FILES = {
    "theme_exposure_summary": "theme_exposure_summary.json",
    "manager_theme_overlap_summary": "manager_theme_overlap_summary.json",
    "scenario_impact_by_theme_manager": "scenario_impact_by_theme_manager.json",
    "data_confidence_map": "data_confidence_map.json",
    "cross_scenario_resilience_summary": "cross_scenario_resilience_summary.json",
    "analytics_output_index": "analytics_output_index.json",
}

DEFAULT_ANALYTIC_PAYLOAD_SPECS = [
    (
        "concentration_theme_analytics.json",
        "concentration",
        {
            "branch": "Advisor Review",
            "placement": "Risk review",
            "scope": "Whole portfolio",
            "lens": "Approved theme",
            "metric": "Gross thematic exposure",
        },
    ),
    (
        "manager_comparison_analytics.json",
        "manager_comparison",
        {
            "branch": "Advisor Review",
            "placement": "Manager review",
            "scope": "All managers compared",
            "metric": "Theme overlap and confidence flags",
        },
    ),
    (
        "scenario_impact_by_theme_manager_analytics.json",
        "scenario_impact_by_manager",
        {
            "branch": "Advisor Review",
            "placement": "Scenario appendix",
            "scope": "All managers and themes compared",
            "scenario_id": "most_vulnerable_from_analytic_pack",
        },
    ),
    (
        "data_confidence_note_analytics.json",
        "data_confidence_note",
        {
            "branch": "Client Briefing",
            "placement": "Appendix",
            "scope": "Whole portfolio",
            "lens": "Source readiness",
        },
    ),
    (
        "portfolio_status_analytics.json",
        "portfolio_status",
        {
            "branch": "Client Briefing",
            "placement": "Main body",
            "scope": "Whole portfolio",
            "lens": "Analytic readiness",
        },
    ),
]


def load_analytic_outputs(
    analytics_dir: str | Path = DEFAULT_ANALYTICS_DIR,
) -> dict[str, Any]:
    """Load the committed synthetic analytic proof outputs."""

    root = Path(analytics_dir)
    outputs = {
        output_name: _load_json(root / filename)
        for output_name, filename in ANALYTIC_OUTPUT_FILES.items()
    }
    outputs["_source_paths"] = {
        output_name: _normalize_path(root / filename)
        for output_name, filename in ANALYTIC_OUTPUT_FILES.items()
    }
    return outputs


def build_analytic_report_element_input(
    element_id: str,
    parameters: dict[str, Any] | None,
    analytic_outputs: dict[str, Any],
) -> dict[str, Any]:
    """Build one report-element input payload from analytic proof outputs."""

    parameters = dict(parameters or {})
    if element_id == "concentration":
        payload = _build_concentration(parameters, analytic_outputs)
    elif element_id == "manager_comparison":
        payload = _build_manager_comparison(parameters, analytic_outputs)
    elif element_id == "scenario_impact_by_manager":
        payload = _build_scenario_impact_by_manager(parameters, analytic_outputs)
    elif element_id == "data_confidence_note":
        payload = _build_data_confidence_note(parameters, analytic_outputs)
    elif element_id == "portfolio_status":
        payload = _build_portfolio_status(parameters, analytic_outputs)
    else:
        raise ValueError(f"Unsupported analytic report element template: {element_id}")
    payload["validation"] = validate_report_element_input(payload)
    return payload


def build_all_analytic_report_element_inputs(
    analytic_outputs: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Build the default analytic report-element input payload set."""

    outputs = analytic_outputs or load_analytic_outputs()
    return {
        filename: build_analytic_report_element_input(element_id, parameters, outputs)
        for filename, element_id, parameters in DEFAULT_ANALYTIC_PAYLOAD_SPECS
    }


def write_analytic_report_element_inputs(
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    analytic_outputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write analytic report-element input fixtures and a summary file."""

    output_path = Path(output_dir)
    outputs = analytic_outputs or load_analytic_outputs()
    payloads = build_all_analytic_report_element_inputs(outputs)
    output_path.mkdir(parents=True, exist_ok=True)
    for filename, payload in payloads.items():
        _write_json(output_path / filename, payload)

    summary = _build_output_summary(output_path, payloads, outputs)
    _write_json(output_path / "report_element_analytic_input_summary.json", summary)
    return {"payloads": payloads, "summary": summary}


def _build_concentration(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    theme_summary = outputs["theme_exposure_summary"]
    overlap_summary = outputs["manager_theme_overlap_summary"]
    grouped_rows = _theme_concentration_rows(theme_summary, overlap_summary)
    top_holdings = _top_theme_position_rows(theme_summary)
    largest = grouped_rows[0]
    payload = _base_payload("concentration", parameters, outputs)
    payload.update(
        {
            "headline_metrics": {
                "lens": {"value": "Approved theme", "unit": "label"},
                "group_count": {"value": len(grouped_rows), "unit": "count"},
                "largest_group": {"value": largest["theme_display_name"], "unit": "label"},
                "largest_group_value": _money_metric(largest["value"]),
                "largest_group_percent": {"value": largest["percent_of_total"], "unit": "ratio"},
                "high_overlap_theme_count": {
                    "value": sum(1 for row in grouped_rows if row.get("overlap_level") == "high"),
                    "unit": "count",
                },
            },
            "evidence_items": grouped_rows[:5],
            "tables": {
                "grouped_rows": grouped_rows,
                "top_holdings": top_holdings,
                "overlap_rows": _overlap_rows(overlap_summary),
                "evidence_rows": _theme_manager_evidence_rows(overlap_summary),
            },
            "human_review_items": _human_review_items(outputs),
            "confidence_summary": _confidence_summary(outputs),
            "caveats": _common_caveats(
                [
                    "Theme exposure is gross thematic exposure from approved synthetic pack mappings; themes can overlap and should not be summed.",
                    "Overlap rows are discussion prompts for concentration review, not manager rankings or recommendations.",
                ],
                theme_summary,
                overlap_summary,
            ),
        }
    )
    return payload


def _build_manager_comparison(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    manager_rows = _manager_theme_rows(outputs)
    largest = max(manager_rows, key=lambda row: float(row["theme_exposure_value"]))
    review_managers = [row for row in manager_rows if row.get("review_required_value", 0.0) > 0.0]
    payload = _base_payload("manager_comparison", parameters, outputs)
    payload.update(
        {
            "headline_metrics": {
                "manager_count": {"value": len(manager_rows), "unit": "count"},
                "largest_manager_theme_exposure": _money_metric(largest["theme_exposure_value"]),
                "high_overlap_theme_count": {"value": max(row["high_overlap_theme_count"] for row in manager_rows), "unit": "count"},
                "review_required_manager_count": {"value": len(review_managers), "unit": "count"},
            },
            "evidence_items": manager_rows,
            "tables": {
                "manager_rows": manager_rows,
                "manager_confidence_rows": _manager_confidence_rows(outputs["data_confidence_map"]),
                "overlap_rows": _overlap_rows(outputs["manager_theme_overlap_summary"]),
            },
            "human_review_items": _human_review_items(outputs),
            "confidence_summary": _confidence_summary(outputs),
            "caveats": _common_caveats(
                [
                    "Manager comparison uses synthetic theme overlap and confidence evidence; it is not a manager ranking.",
                    "Gross theme exposure can double count overlapping themes and should be read as a discussion lens.",
                ],
                outputs["manager_theme_overlap_summary"],
                outputs["data_confidence_map"],
            ),
        }
    )
    return payload


def _build_scenario_impact_by_manager(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    scenario_output = outputs["scenario_impact_by_theme_manager"]
    resilience = outputs["cross_scenario_resilience_summary"]
    scenario_id = resilience["most_vulnerable_scenario"]["scenario_id"]
    scenario = next(row for row in scenario_output["scenarios"] if row["scenario_id"] == scenario_id)
    manager_impacts = _scenario_manager_rows(scenario)
    theme_impacts = _scenario_theme_rows(scenario)
    payload = _base_payload("scenario_impact_by_manager", parameters, outputs)
    payload.update(
        {
            "scenario": {
                "scenario_id": scenario["scenario_id"],
                "display_name": scenario["scenario_display_name"],
                "horizon": "synthetic scenario horizon",
                "scenario_date": scenario_output["data_as_of"],
                "description": scenario["advisor_story"],
                "scenario_completeness": {"status": scenario["scenario_status"]},
                "synthetic_data": True,
            },
            "headline_metrics": {
                "base_total_value": _money_metric(scenario["base_total_value"]),
                "scenario_total_value": _money_metric(scenario["scenario_total_value"]),
                "total_scenario_impact": _money_metric(scenario["total_impact"]),
                "total_scenario_impact_percent": {"value": scenario["total_impact_percent"], "unit": "ratio"},
                "manager_count": {"value": len(manager_impacts), "unit": "count"},
                "theme_count": {"value": len(theme_impacts), "unit": "count"},
            },
            "evidence_items": manager_impacts[:6] + theme_impacts[:6],
            "tables": {
                "manager_impacts": manager_impacts,
                "theme_impacts": theme_impacts,
                "repeated_vulnerable_themes": resilience["repeated_vulnerable_themes"],
                "repeated_vulnerable_managers": resilience["repeated_vulnerable_managers"],
                "repeated_defensive_themes": resilience["repeated_defensive_themes"],
                "repeated_defensive_managers": resilience["repeated_defensive_managers"],
            },
            "human_review_items": _human_review_items(outputs),
            "confidence_summary": _confidence_summary(outputs),
            "caveats": _common_caveats(
                [
                    "Deterministic synthetic scenario output only; not a forecast, probability estimate, guarantee, or manager recommendation.",
                    "Theme-level impact allocates position impacts across approved theme matches and is approximate.",
                ],
                scenario_output,
                resilience,
            ),
        }
    )
    return payload


def _build_data_confidence_note(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    confidence_map = outputs["data_confidence_map"]
    confidence_rows = _confidence_rows(confidence_map)
    review_row = next((row for row in confidence_rows if row["id"] == "review_required"), confidence_rows[0])
    payload = _base_payload("data_confidence_note", parameters, outputs)
    payload.update(
        {
            "headline_metrics": {
                "confidence_label": {"value": _confidence_label(confidence_rows), "unit": "label"},
                "human_review_count": {"value": review_row["count"], "unit": "count"},
                "human_review_value": _money_metric(review_row["value"]),
                "direct_or_cash_value": _money_metric(_bucket_value(confidence_rows, {"high"})),
                "proxy_or_stale_value": _money_metric(_bucket_value(confidence_rows, {"medium", "low", "unknown", "review_required"})),
            },
            "evidence_items": confidence_rows,
            "tables": {
                "confidence_rows": confidence_rows,
                "valuation_treatment_rows": _valuation_treatment_rows(confidence_rows),
                "review_rows": _review_rows(confidence_map),
                "theme_confidence_rows": _theme_confidence_rows(confidence_map),
            },
            "human_review_items": _human_review_items(outputs),
            "confidence_summary": _confidence_summary(outputs),
            "caveats": _common_caveats(
                [
                    "Confidence describes synthetic source readiness and valuation treatment, not investment quality.",
                    "Review-required rows are separated before ordinary low, medium, and high buckets.",
                ],
                confidence_map,
            ),
        }
    )
    return payload


def _build_portfolio_status(parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    theme_summary = outputs["theme_exposure_summary"]
    resilience = outputs["cross_scenario_resilience_summary"]
    confidence_rows = _confidence_rows(outputs["data_confidence_map"])
    top_theme = theme_summary["themes"][0]
    review_value = _bucket_value(confidence_rows, {"review_required"})
    payload = _base_payload("portfolio_status", parameters, outputs)
    payload.update(
        {
            "headline_metrics": {
                "total_portfolio_value": _money_metric(theme_summary["total_portfolio_value"]),
                "top_theme_value": _money_metric(top_theme["market_value"]),
                "top_theme_percent": {"value": top_theme["percent_of_portfolio"], "unit": "ratio"},
                "most_vulnerable_scenario_impact": _money_metric(resilience["most_vulnerable_scenario"]["total_impact"]),
                "human_review_value": _money_metric(review_value),
            },
            "evidence_items": _status_rows(theme_summary, resilience, confidence_rows),
            "tables": {
                "manager_values": _portfolio_manager_values(outputs),
                "asset_class_values": _portfolio_status_bucket_rows(theme_summary, resilience),
                "theme_values": _theme_value_rows(theme_summary),
                "status_rows": _status_rows(theme_summary, resilience, confidence_rows),
                "resilience_rows": _resilience_rows(resilience),
                "confidence_rows": confidence_rows,
            },
            "human_review_items": _human_review_items(outputs),
            "confidence_summary": _confidence_summary(outputs),
            "caveats": _common_caveats(
                [
                    "Portfolio status uses synthetic analytic proof outputs as local demo evidence only.",
                    "Cross-scenario resilience is a simple deterministic summary, not a probability model.",
                ],
                theme_summary,
                resilience,
            ),
        }
    )
    return payload


def _base_payload(element_id: str, parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    template = get_template(element_id)
    if template is None:
        raise ValueError(f"Unsupported report element template: {element_id}")
    index = outputs["analytics_output_index"]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "mapper_version": MAPPER_VERSION,
        "input_variant": INPUT_VARIANT,
        "element_id": template["element_id"],
        "element_title": template["title"],
        "template_category": template["category"],
        "target_branch": parameters.get("branch"),
        "placement": parameters.get("placement"),
        "parameters_used": parameters,
        "as_of_date": index["data_as_of"],
        "portfolio_id": index["portfolio_id"],
        "reporting_currency": REPORTING_CURRENCY,
        "source_data": _source_data(outputs),
        "headline_metrics": {},
        "evidence_items": [],
        "tables": {},
        "confidence_summary": {},
        "caveats": [],
        "human_review_items": [],
        "source_analytic_pack": {
            "pack_id": index["pack_id"],
            "pack_version": index["pack_version"],
            "synthetic_data": True,
        },
        "synthetic_data": True,
    }


def _source_data(outputs: dict[str, Any]) -> dict[str, Any]:
    index = outputs["analytics_output_index"]
    paths = outputs.get("_source_paths", {})
    return {
        "position_universe": {
            "path": "data/simulation/synthetic_position_universe.json",
            "synthetic_data": True,
        },
        "market_state": {
            "path": "data/simulation/synthetic_market_state_history.json",
            "synthetic_data": True,
        },
        "valuation_history": {
            "daily_position_path": "data/simulation/daily_position_valuation_history.json",
            "daily_portfolio_path": "data/simulation/daily_portfolio_valuation_history.json",
            "summary_path": "data/simulation/simplified_valuation_summary.json",
            "synthetic_data": True,
        },
        "scenario_results": {
            "path": "data/simulation/scenario_revaluation_results.json",
            "synthetic_data": True,
        },
        "analytic_pack": {
            "pack_id": index["pack_id"],
            "pack_version": index["pack_version"],
            "output_index_path": paths.get("analytics_output_index"),
            "synthetic_data": True,
        },
        "analytics_outputs": [
            {
                "output_name": row["output_name"],
                "path": row["path"],
                "schema_version": row["schema_version"],
                "synthetic_data": True,
            }
            for row in index.get("outputs", [])
        ],
    }


def _theme_concentration_rows(theme_summary: dict[str, Any], overlap_summary: dict[str, Any]) -> list[dict[str, Any]]:
    overlap_by_theme = {row["theme_id"]: row for row in overlap_summary.get("themes", [])}
    rows = []
    for theme in theme_summary.get("themes", []):
        overlap = overlap_by_theme.get(theme["theme_id"], {})
        rows.append(
            {
                "id": theme["theme_id"],
                "theme_id": theme["theme_id"],
                "display_name": theme["theme_display_name"],
                "theme_display_name": theme["theme_display_name"],
                "value": _round_money(theme["market_value"]),
                "percent_of_total": _round_percent(theme["percent_of_portfolio"]),
                "position_count": theme["position_count"],
                "overlap_level": overlap.get("overlap_level", "unavailable"),
                "manager_count": len(overlap.get("managers_with_exposure", [])),
                "top_manager_names": [row["display_name"] for row in theme.get("top_managers", [])[:3]],
                "advisor_interpretation": overlap.get("advisor_interpretation") or theme.get("advisor_description"),
                "confidence_notes": theme.get("confidence_notes", []),
                "synthetic_data": True,
            }
        )
    return sorted(rows, key=lambda row: float(row["value"]), reverse=True)


def _top_theme_position_rows(theme_summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    seen: set[tuple[str, str]] = set()
    total = float(theme_summary["total_portfolio_value"])
    for theme in theme_summary.get("themes", []):
        for position in theme.get("top_positions", []):
            key = (theme["theme_id"], position["position_id"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "theme_id": theme["theme_id"],
                    "theme_display_name": theme["theme_display_name"],
                    "position_id": position["position_id"],
                    "display_name": position["display_name"],
                    "manager_id": position["manager_id"],
                    "manager_name": position["manager_display_name"],
                    "value": _round_money(position["market_value"]),
                    "percent_of_total": _round_percent(_safe_divide(position["market_value"], total)),
                    "confidence": position.get("confidence"),
                    "synthetic_data": True,
                }
            )
    return sorted(rows, key=lambda row: float(row["value"]), reverse=True)[:12]


def _overlap_rows(overlap_summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "theme_id": row["theme_id"],
            "theme_display_name": row["theme_display_name"],
            "value": _round_money(row["aggregate_exposure"]),
            "percent_of_total": _round_percent(row["percent_of_portfolio"]),
            "manager_count": len(row.get("managers_with_exposure", [])),
            "overlap_level": row["overlap_level"],
            "advisor_interpretation": row["advisor_interpretation"],
            "synthetic_data": True,
        }
        for row in overlap_summary.get("themes", [])
    ]


def _theme_manager_evidence_rows(overlap_summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for theme in overlap_summary.get("themes", []):
        for evidence in theme.get("evidence_rows", [])[:4]:
            rows.append(
                {
                    "theme_id": theme["theme_id"],
                    "theme_display_name": theme["theme_display_name"],
                    "manager_id": evidence["id"],
                    "manager_name": evidence["display_name"],
                    "value": _round_money(evidence["exposure_value"]),
                    "percent_of_theme": _round_percent(evidence["percent_of_theme"]),
                    "overlap_level": theme["overlap_level"],
                    "synthetic_data": True,
                }
            )
    return rows


def _manager_theme_rows(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    overlap = outputs["manager_theme_overlap_summary"]
    confidence_by_manager = {
        row["manager_id"]: row
        for row in _manager_confidence_rows(outputs["data_confidence_map"])
    }
    managers: dict[str, dict[str, Any]] = {}
    for theme in overlap.get("themes", []):
        for evidence in theme.get("evidence_rows", []):
            manager_id = evidence["id"]
            manager = managers.setdefault(
                manager_id,
                {
                    "manager_id": manager_id,
                    "manager_name": evidence["display_name"],
                    "theme_exposure_value": 0.0,
                    "shared_theme_count": 0,
                    "high_overlap_theme_count": 0,
                    "primary_themes": [],
                    "review_required_value": 0.0,
                    "confidence_notes": [],
                    "synthetic_data": True,
                },
            )
            manager["theme_exposure_value"] += float(evidence["exposure_value"])
            manager["shared_theme_count"] += 1
            if theme.get("overlap_level") == "high":
                manager["high_overlap_theme_count"] += 1
            if len(manager["primary_themes"]) < 5:
                manager["primary_themes"].append(theme["theme_display_name"])
    for manager in managers.values():
        confidence = confidence_by_manager.get(manager["manager_id"], {})
        manager["theme_exposure_value"] = _round_money(manager["theme_exposure_value"])
        manager["review_required_value"] = _round_money(confidence.get("review_required_value", 0.0))
        if confidence.get("dominant_confidence_bucket"):
            manager["confidence_notes"].append(f"Dominant confidence bucket: {confidence['dominant_confidence_bucket']}")
        if manager["review_required_value"] > 0.0:
            manager["confidence_notes"].append("Contains review-required exposure.")
    return sorted(managers.values(), key=lambda row: (-float(row["theme_exposure_value"]), row["manager_name"]))


def _manager_confidence_rows(confidence_map: dict[str, Any]) -> list[dict[str, Any]]:
    manager_values: dict[str, dict[str, Any]] = defaultdict(lambda: {"manager_id": "", "manager_name": "", "buckets": defaultdict(float)})
    for bucket in confidence_map.get("confidence_buckets", []):
        bucket_id = bucket["confidence_bucket"]
        for manager in bucket.get("affected_managers", []):
            record = manager_values[manager["id"]]
            record["manager_id"] = manager["id"]
            record["manager_name"] = manager["display_name"]
            record["buckets"][bucket_id] += float(manager["exposure_value"])
    rows = []
    for record in manager_values.values():
        buckets = dict(record["buckets"])
        dominant = max(buckets.items(), key=lambda item: item[1])[0] if buckets else "unavailable"
        rows.append(
            {
                "manager_id": record["manager_id"],
                "manager_name": record["manager_name"],
                "dominant_confidence_bucket": dominant,
                "high_value": _round_money(buckets.get("high", 0.0)),
                "medium_value": _round_money(buckets.get("medium", 0.0)),
                "review_required_value": _round_money(buckets.get("review_required", 0.0)),
                "synthetic_data": True,
            }
        )
    return sorted(rows, key=lambda row: (-float(row["review_required_value"]), row["manager_name"]))


def _scenario_manager_rows(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row_type, source_rows in (
        ("top_negative_manager", scenario.get("top_negative_managers", [])),
        ("defensive_manager", scenario.get("top_positive_or_defensive_managers", [])),
    ):
        for row in source_rows:
            rows.append(
                {
                    "row_type": row_type,
                    "manager_id": row["manager_id"],
                    "manager_name": row["manager_display_name"],
                    "base_value": _round_money(row["base_value"]),
                    "scenario_impact": _round_money(row["scenario_impact"]),
                    "scenario_impact_percent": _round_percent(row["scenario_impact_percent"]),
                    "synthetic_data": True,
                }
            )
    return rows


def _scenario_theme_rows(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "theme_id": row["theme_id"],
            "theme_display_name": row["theme_display_name"],
            "base_value": _round_money(row["base_value"]),
            "scenario_value": _round_money(row["scenario_value"]),
            "scenario_impact": _round_money(row["scenario_impact"]),
            "scenario_impact_percent": _round_percent(row["scenario_impact_percent"]),
            "synthetic_data": True,
        }
        for row in scenario.get("theme_impacts", [])
    ]


def _confidence_rows(confidence_map: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["confidence_bucket"],
            "display_name": row["confidence_bucket"].replace("_", " ").title(),
            "count": row["position_count"],
            "value": _round_money(row["exposure_value"]),
            "percent_of_total": _round_percent(row["percent_of_portfolio"]),
            "advisor_language": row["advisor_language"],
            "affected_manager_names": [manager["display_name"] for manager in row.get("affected_managers", [])[:3]],
            "affected_theme_names": [theme["theme_display_name"] for theme in row.get("affected_themes", [])[:3]],
            "synthetic_data": True,
        }
        for row in confidence_map.get("confidence_buckets", [])
    ]


def _valuation_treatment_rows(confidence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["id"],
            "display_name": row["display_name"],
            "count": row["count"],
            "value": row["value"],
            "percent_of_total": row["percent_of_total"],
            "treatment_note": row["advisor_language"],
            "synthetic_data": True,
        }
        for row in confidence_rows
    ]


def _review_rows(confidence_map: dict[str, Any]) -> list[dict[str, Any]]:
    review = next((row for row in confidence_map.get("confidence_buckets", []) if row["confidence_bucket"] == "review_required"), {})
    rows = []
    for manager in review.get("affected_managers", []):
        rows.append(
            {
                "row_type": "manager_review",
                "id": manager["id"],
                "display_name": manager["display_name"],
                "value": _round_money(manager["exposure_value"]),
                "percent_of_total": _round_percent(manager["percent_of_theme"]),
                "synthetic_data": True,
            }
        )
    for theme in review.get("affected_themes", []):
        rows.append(
            {
                "row_type": "theme_review",
                "id": theme["theme_id"],
                "display_name": theme["theme_display_name"],
                "value": _round_money(theme["exposure_value"]),
                "percent_of_total": _round_percent(theme["percent_of_bucket"]),
                "synthetic_data": True,
            }
        )
    return rows


def _theme_confidence_rows(confidence_map: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for bucket in confidence_map.get("confidence_buckets", []):
        for theme in bucket.get("affected_themes", [])[:8]:
            rows.append(
                {
                    "confidence_bucket": bucket["confidence_bucket"],
                    "theme_id": theme["theme_id"],
                    "theme_display_name": theme["theme_display_name"],
                    "value": _round_money(theme["exposure_value"]),
                    "percent_of_bucket": _round_percent(theme["percent_of_bucket"]),
                    "synthetic_data": True,
                }
            )
    return rows


def _portfolio_manager_values(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    manager_rows = _manager_theme_rows(outputs)
    total = float(outputs["theme_exposure_summary"]["total_portfolio_value"])
    return [
        {
            "manager_id": row["manager_id"],
            "manager_name": row["manager_name"],
            "value": row["theme_exposure_value"],
            "percent_of_total": _round_percent(_safe_divide(row["theme_exposure_value"], total)),
            "shared_theme_count": row["shared_theme_count"],
            "synthetic_data": True,
        }
        for row in manager_rows
    ]


def _portfolio_status_bucket_rows(theme_summary: dict[str, Any], resilience: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": "theme_coverage",
            "display_name": "Approved theme coverage",
            "value": _round_money(theme_summary["total_portfolio_value"]),
            "percent_of_total": 1.0,
            "synthetic_data": True,
        },
        {
            "id": "most_vulnerable_scenario",
            "display_name": resilience["most_vulnerable_scenario"]["scenario_display_name"],
            "value": _round_money(resilience["most_vulnerable_scenario"]["total_impact"]),
            "percent_of_total": _round_percent(resilience["most_vulnerable_scenario"]["total_impact_percent"]),
            "synthetic_data": True,
        },
        {
            "id": "most_resilient_scenario",
            "display_name": resilience["most_resilient_scenario"]["scenario_display_name"],
            "value": _round_money(resilience["most_resilient_scenario"]["total_impact"]),
            "percent_of_total": _round_percent(resilience["most_resilient_scenario"]["total_impact_percent"]),
            "synthetic_data": True,
        },
    ]


def _theme_value_rows(theme_summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["theme_id"],
            "display_name": row["theme_display_name"],
            "value": _round_money(row["market_value"]),
            "percent_of_total": _round_percent(row["percent_of_portfolio"]),
            "position_count": row["position_count"],
            "synthetic_data": True,
        }
        for row in theme_summary.get("themes", [])
    ]


def _status_rows(theme_summary: dict[str, Any], resilience: dict[str, Any], confidence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top_theme = theme_summary["themes"][0]
    review_value = _bucket_value(confidence_rows, {"review_required"})
    return [
        {
            "id": "total_portfolio_value",
            "display_name": "Synthetic portfolio value",
            "value": _round_money(theme_summary["total_portfolio_value"]),
            "status_text": "Current synthetic demo snapshot",
            "synthetic_data": True,
        },
        {
            "id": "top_theme",
            "display_name": top_theme["theme_display_name"],
            "value": _round_money(top_theme["market_value"]),
            "percent_of_total": _round_percent(top_theme["percent_of_portfolio"]),
            "status_text": "Largest approved theme exposure",
            "synthetic_data": True,
        },
        {
            "id": "most_vulnerable_scenario",
            "display_name": resilience["most_vulnerable_scenario"]["scenario_display_name"],
            "value": _round_money(resilience["most_vulnerable_scenario"]["total_impact"]),
            "percent_of_total": _round_percent(resilience["most_vulnerable_scenario"]["total_impact_percent"]),
            "status_text": "Largest deterministic scenario drawdown",
            "synthetic_data": True,
        },
        {
            "id": "review_required_value",
            "display_name": "Review-required exposure",
            "value": _round_money(review_value),
            "status_text": "Call out before meeting-ready use",
            "synthetic_data": True,
        },
    ]


def _resilience_rows(resilience: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": "most_vulnerable_scenario",
            **resilience["most_vulnerable_scenario"],
            "synthetic_data": True,
        },
        {
            "id": "most_resilient_scenario",
            **resilience["most_resilient_scenario"],
            "synthetic_data": True,
        },
    ] + [
        {
            "id": row["theme_id"],
            "theme_display_name": row["theme_display_name"],
            "scenario_count": row["scenario_count"],
            "row_type": "repeated_vulnerable_theme",
            "synthetic_data": True,
        }
        for row in resilience.get("repeated_vulnerable_themes", [])
    ]


def _human_review_items(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    return _review_rows(outputs["data_confidence_map"])[:8]


def _confidence_summary(outputs: dict[str, Any]) -> dict[str, Any]:
    confidence_rows = _confidence_rows(outputs["data_confidence_map"])
    review_row = next((row for row in confidence_rows if row["id"] == "review_required"), {})
    return {
        "label": _confidence_label(confidence_rows),
        "by_confidence": confidence_rows,
        "human_review_count": int(review_row.get("count", 0)),
        "human_review_value": _round_money(review_row.get("value", 0.0)),
        "synthetic_data": True,
    }


def _confidence_label(confidence_rows: list[dict[str, Any]]) -> str:
    by_id = {row["id"]: float(row.get("percent_of_total", 0.0)) for row in confidence_rows}
    if by_id.get("review_required", 0.0) > 0.0:
        return "mixed"
    if by_id.get("high", 0.0) >= 0.7:
        return "high"
    if by_id.get("medium", 0.0) >= 0.25:
        return "medium"
    return "low"


def _common_caveats(extra: list[str], *sources: dict[str, Any]) -> list[str]:
    caveats = [
        "Synthetic demo data only.",
        "Structured report-element input fixture only; no live data, external API, production storage, or production reporting is produced.",
    ]
    for source in sources:
        for caveat in source.get("caveats", []):
            if "not wired into report-element inputs" in caveat:
                continue
            public_caveat = _public_caveat(caveat)
            if public_caveat not in caveats:
                caveats.append(public_caveat)
    for caveat in extra:
        if caveat not in caveats:
            caveats.append(caveat)
    return caveats


def _public_caveat(caveat: str) -> str:
    replacements = {
        "existing deterministic scenario_revaluation_results.json": "existing deterministic scenario source",
        "scenario_revaluation_results.json": "the existing deterministic scenario source",
    }
    public = str(caveat)
    for internal, replacement in replacements.items():
        public = public.replace(internal, replacement)
    return public


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
    index = outputs["analytics_output_index"]
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "mapper_version": MAPPER_VERSION,
        "input_variant": INPUT_VARIANT,
        "synthetic_data": True,
        "output_dir": _normalize_path(output_path),
        "payload_count": len(payloads),
        "element_ids": [payload["element_id"] for payload in payloads.values()],
        "output_files": list(payloads.keys()) + ["report_element_analytic_input_summary.json"],
        "source_files_used": outputs.get("_source_paths", {}),
        "source_analytic_pack": {
            "pack_id": index["pack_id"],
            "pack_version": index["pack_version"],
            "synthetic_data": True,
        },
        "as_of_date": index["data_as_of"],
        "portfolio_id": index["portfolio_id"],
        "validation_status": "valid" if statuses == {"valid"} else "invalid",
        "validation_results": validation_results,
        "caveat": "Analytic report-element inputs feed local rendered views and browser-local Preview, Populate, and Present flows only; no live data, external APIs, production storage, or production reporting is produced.",
    }


def _money_metric(value: float) -> dict[str, Any]:
    return {"value": _round_money(float(value)), "unit": REPORTING_CURRENCY}


def _bucket_value(rows: list[dict[str, Any]], bucket_ids: set[str]) -> float:
    return _round_money(sum(float(row.get("value", 0.0)) for row in rows if row.get("id") in bucket_ids))


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def _round_money(value: float) -> float:
    return round(float(value), 2)


def _round_percent(value: float) -> float:
    return round(float(value), 6)


def _normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Write analytic report-element input fixtures.")
    parser.add_argument("--analytics-dir", default=str(DEFAULT_ANALYTICS_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    written = write_analytic_report_element_inputs(
        output_dir=Path(args.output_dir),
        analytic_outputs=load_analytic_outputs(Path(args.analytics_dir)),
    )
    summary = written["summary"]
    print(
        "analytic report element inputs written: "
        f"{summary['payload_count']} payloads; "
        f"status={summary['validation_status']}; "
        f"as_of={summary['as_of_date']}"
    )
    print("elements: " + ", ".join(summary["element_ids"]))


if __name__ == "__main__":
    main()
