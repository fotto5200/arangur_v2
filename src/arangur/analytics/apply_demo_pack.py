from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from arangur.analytics.analytic_pack_loader import load_analytic_pack


GENERATED_AT = "2026-07-03T00:00:00Z"
DEFAULT_PACK_DIR = Path("data/analytic_packs/arranger_demo_pack_v1")
DEFAULT_OUTPUT_DIR = Path("data/simulation/analytics")
DEFAULT_POSITION_UNIVERSE_PATH = Path("data/simulation/synthetic_position_universe.json")
DEFAULT_SCENARIO_REVALUATION_PATH = Path("data/simulation/scenario_revaluation_results.json")
DEFAULT_VALUATION_SUMMARY_PATH = Path("data/simulation/simplified_valuation_summary.json")

OUTPUT_FILES = {
    "theme_exposure_summary": "theme_exposure_summary.json",
    "manager_theme_overlap_summary": "manager_theme_overlap_summary.json",
    "scenario_impact_by_theme_manager": "scenario_impact_by_theme_manager.json",
    "data_confidence_map": "data_confidence_map.json",
    "cross_scenario_resilience_summary": "cross_scenario_resilience_summary.json",
    "analytics_output_index": "analytics_output_index.json",
}


def generate_demo_pack_outputs(
    *,
    pack_dir: Path | str = DEFAULT_PACK_DIR,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    position_universe_path: Path | str = DEFAULT_POSITION_UNIVERSE_PATH,
    scenario_revaluation_path: Path | str = DEFAULT_SCENARIO_REVALUATION_PATH,
    valuation_summary_path: Path | str = DEFAULT_VALUATION_SUMMARY_PATH,
) -> dict[str, Any]:
    """Apply the approved synthetic demo pack to committed simulation fixtures."""
    pack = load_analytic_pack(Path(pack_dir))
    if pack["validation"]["status"] != "valid":
        raise ValueError(f"Analytic pack is invalid: {pack['validation']['errors']}")

    universe = _load_json(Path(position_universe_path))
    scenario_revaluations = _load_json(Path(scenario_revaluation_path))
    valuation_summary = _load_json(Path(valuation_summary_path))

    context = _build_context(pack, universe, scenario_revaluations, valuation_summary)
    outputs = {
        "theme_exposure_summary": build_theme_exposure_summary(context),
        "manager_theme_overlap_summary": build_manager_theme_overlap_summary(context),
        "scenario_impact_by_theme_manager": build_scenario_impact_by_theme_manager(context),
        "data_confidence_map": build_data_confidence_map(context),
    }
    outputs["cross_scenario_resilience_summary"] = build_cross_scenario_resilience_summary(
        context,
        outputs["scenario_impact_by_theme_manager"],
    )
    outputs["analytics_output_index"] = build_output_index(context, outputs)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    for output_name, filename in OUTPUT_FILES.items():
        _write_json(output_path / filename, outputs[output_name])
    return outputs


def build_theme_exposure_summary(context: dict[str, Any]) -> dict[str, Any]:
    total_value = context["total_portfolio_value"]
    theme_rows: list[dict[str, Any]] = []

    for theme in context["themes"]:
        theme_id = theme["theme_id"]
        matched_positions = [
            position
            for position in context["positions"]
            if theme_id in _matched_theme_ids(position, context)
        ]
        exposure_value = sum(_position_value(position) for position in matched_positions)
        manager_values = _sum_positions_by(matched_positions, "manager_id")
        sleeve_values = _sum_positions_by(matched_positions, "sleeve_id")
        top_positions = sorted(matched_positions, key=_position_value, reverse=True)[:5]
        caveats = list(theme.get("caveats", []))
        if len(matched_positions) > 0 and len(_all_position_themes(matched_positions)) > 1:
            caveats.append("Theme exposure is gross thematic exposure; themes can overlap and should not be summed.")

        theme_rows.append(
            {
                "theme_id": theme_id,
                "theme_display_name": theme["display_name"],
                "market_value": _round_money(exposure_value),
                "percent_of_portfolio": _round_percent(_safe_divide(exposure_value, total_value)),
                "position_count": len(matched_positions),
                "top_managers": _top_group_rows(manager_values, context["manager_labels"], exposure_value),
                "top_sleeves": _top_group_rows(sleeve_values, context["sleeve_labels"], exposure_value),
                "top_positions": [
                    {
                        "position_id": position["position_id"],
                        "display_name": position["display_name"],
                        "manager_id": position["manager_id"],
                        "manager_display_name": context["manager_labels"].get(position["manager_id"], position["manager_id"]),
                        "market_value": _round_money(_position_value(position)),
                        "confidence": position.get("valuation_confidence", "unknown"),
                    }
                    for position in top_positions
                ],
                "confidence_notes": _confidence_notes_for_positions(matched_positions),
                "advisor_description": theme["advisor_description"],
                "likely_affected_portfolio_areas": theme.get("likely_affected_portfolio_areas", []),
                "caveats": caveats,
            }
        )

    theme_rows.sort(key=lambda row: row["market_value"], reverse=True)
    return {
        "schema_version": "analytics_theme_exposure_summary.v1",
        "generated_at": GENERATED_AT,
        "pack_id": context["pack_id"],
        "pack_version": context["pack_version"],
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "data_as_of": context["data_as_of"],
        "total_portfolio_value": _round_money(total_value),
        "theme_count": len(theme_rows),
        "themes": theme_rows,
        "caveats": [
            "Synthetic demo analytics only; not investment advice or a production exposure engine.",
            "Theme exposure is based on approved pack mappings over existing synthetic position tags and metadata.",
        ],
    }


def build_manager_theme_overlap_summary(context: dict[str, Any]) -> dict[str, Any]:
    total_value = context["total_portfolio_value"]
    overlap_rows: list[dict[str, Any]] = []

    for theme in context["themes"]:
        theme_id = theme["theme_id"]
        matched_positions = [
            position
            for position in context["positions"]
            if theme_id in _matched_theme_ids(position, context)
        ]
        manager_values = _sum_positions_by(matched_positions, "manager_id")
        active_manager_values = {
            manager_id: value
            for manager_id, value in manager_values.items()
            if value > 0
        }
        aggregate_exposure = sum(active_manager_values.values())
        manager_count = len(active_manager_values)
        exposure_percent = _safe_divide(aggregate_exposure, total_value)
        overlap_level = _overlap_level(manager_count, exposure_percent)
        evidence_rows = _top_group_rows(active_manager_values, context["manager_labels"], aggregate_exposure, limit=6)
        overlap_rows.append(
            {
                "theme_id": theme_id,
                "theme_display_name": theme["display_name"],
                "managers_with_exposure": [
                    {
                        "manager_id": manager_id,
                        "manager_display_name": context["manager_labels"].get(manager_id, manager_id),
                    }
                    for manager_id, value in sorted(active_manager_values.items(), key=lambda item: (-item[1], item[0]))
                ],
                "aggregate_exposure": _round_money(aggregate_exposure),
                "percent_of_portfolio": _round_percent(exposure_percent),
                "overlap_level": overlap_level,
                "advisor_interpretation": _overlap_interpretation(theme["display_name"], overlap_level, manager_count),
                "evidence_rows": evidence_rows,
            }
        )

    overlap_rows.sort(key=lambda row: ({"high": 0, "moderate": 1, "low": 2}[row["overlap_level"]], -row["aggregate_exposure"]))
    return {
        "schema_version": "analytics_manager_theme_overlap_summary.v1",
        "generated_at": GENERATED_AT,
        "pack_id": context["pack_id"],
        "pack_version": context["pack_version"],
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "data_as_of": context["data_as_of"],
        "overlap_count": len(overlap_rows),
        "themes": overlap_rows,
        "caveats": [
            "Overlap is a deterministic discussion prompt, not a recommendation or manager ranking.",
            "Theme matches use synthetic position metadata and approved demo pack mappings.",
        ],
    }


def build_scenario_impact_by_theme_manager(context: dict[str, Any]) -> dict[str, Any]:
    scenario_results_by_id = {
        result["scenario_id"]: result
        for result in context["scenario_results"]
    }
    scenario_rows: list[dict[str, Any]] = []

    for scenario in context["scenarios"]:
        scenario_id = scenario["scenario_id"]
        result = scenario_results_by_id.get(scenario_id)
        if result is None:
            scenario_rows.append(_missing_scenario_row(context, scenario))
            continue

        manager_rows = _manager_impact_rows(result, context)
        theme_rows = _theme_impact_rows(result, context)
        scenario_rows.append(
            {
                "scenario_id": scenario_id,
                "scenario_display_name": scenario["display_name"],
                "advisor_story": scenario["advisor_story"],
                "scenario_status": "available_from_existing_synthetic_revaluation",
                "total_impact": _round_money(result["total_scenario_impact"]),
                "total_impact_percent": _round_percent(result["total_scenario_impact_percent"]),
                "base_total_value": _round_money(result["base_total_value"]),
                "scenario_total_value": _round_money(result["scenario_total_value"]),
                "top_negative_managers": manager_rows["top_negative_managers"],
                "top_positive_or_defensive_managers": manager_rows["top_positive_or_defensive_managers"],
                "theme_impacts": theme_rows,
                "confidence": _scenario_confidence(result),
                "caveats": list(dict.fromkeys(scenario.get("caveats", []) + result.get("caveats", []))),
            }
        )

    return {
        "schema_version": "analytics_scenario_impact_by_theme_manager.v1",
        "generated_at": GENERATED_AT,
        "pack_id": context["pack_id"],
        "pack_version": context["pack_version"],
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "data_as_of": context["data_as_of"],
        "scenario_count": len(scenario_rows),
        "scenarios": scenario_rows,
        "caveats": [
            "Uses existing deterministic scenario_revaluation_results.json; this module does not implement a new scenario engine.",
            "Theme-level impact allocates position impacts across approved pack theme mappings and is approximate.",
        ],
    }


def build_data_confidence_map(context: dict[str, Any]) -> dict[str, Any]:
    total_value = context["total_portfolio_value"]
    bucket_positions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for position in context["positions"]:
        bucket_positions[_confidence_bucket(position)].append(position)

    bucket_order = ["high", "medium", "low", "review_required", "unknown"]
    confidence_rows: list[dict[str, Any]] = []
    for bucket in bucket_order:
        positions = bucket_positions.get(bucket, [])
        exposure_value = sum(_position_value(position) for position in positions)
        theme_values: dict[str, float] = defaultdict(float)
        manager_values = _sum_positions_by(positions, "manager_id")
        for position in positions:
            matched_themes = _matched_theme_ids(position, context)
            for theme_id in matched_themes:
                theme_values[theme_id] += _position_value(position)
        confidence_rows.append(
            {
                "confidence_bucket": bucket,
                "exposure_value": _round_money(exposure_value),
                "percent_of_portfolio": _round_percent(_safe_divide(exposure_value, total_value)),
                "position_count": len(positions),
                "affected_themes": _top_theme_rows(theme_values, context, exposure_value, limit=8),
                "affected_managers": _top_group_rows(manager_values, context["manager_labels"], exposure_value, limit=6),
                "advisor_language": _advisor_language_for_bucket(bucket, context["confidence_rules"]),
            }
        )

    return {
        "schema_version": "analytics_data_confidence_map.v1",
        "generated_at": GENERATED_AT,
        "pack_id": context["pack_id"],
        "pack_version": context["pack_version"],
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "data_as_of": context["data_as_of"],
        "confidence_buckets": confidence_rows,
        "valuation_summary_reference": {
            "schema_version": context["valuation_summary"].get("schema_version"),
            "human_review_count": context["valuation_summary"].get("human_review_count"),
            "human_review_value": context["valuation_summary"].get("human_review_value"),
        },
        "caveats": [
            "Confidence summarizes source readiness and valuation treatment, not investment quality.",
            "Review-required records are separated before ordinary low/medium/high buckets.",
        ],
    }


def build_cross_scenario_resilience_summary(
    context: dict[str, Any],
    scenario_output: dict[str, Any],
) -> dict[str, Any]:
    available = [
        scenario
        for scenario in scenario_output["scenarios"]
        if scenario["scenario_status"] == "available_from_existing_synthetic_revaluation"
    ]
    most_vulnerable = min(available, key=lambda scenario: scenario["total_impact"])
    most_resilient = max(available, key=lambda scenario: scenario["total_impact"])

    vulnerable_theme_counts: Counter[str] = Counter()
    defensive_theme_counts: Counter[str] = Counter()
    vulnerable_manager_counts: Counter[str] = Counter()
    defensive_manager_counts: Counter[str] = Counter()
    for scenario in available:
        negative_themes = [row for row in scenario["theme_impacts"] if row["scenario_impact"] < 0][:3]
        defensive_themes = sorted(scenario["theme_impacts"], key=lambda row: row["scenario_impact"], reverse=True)[:3]
        vulnerable_theme_counts.update(row["theme_id"] for row in negative_themes)
        defensive_theme_counts.update(row["theme_id"] for row in defensive_themes)
        vulnerable_manager_counts.update(row["manager_id"] for row in scenario["top_negative_managers"][:3])
        defensive_manager_counts.update(row["manager_id"] for row in scenario["top_positive_or_defensive_managers"][:3])

    repeated_vulnerable_themes = _counter_theme_rows(vulnerable_theme_counts, context)
    repeated_defensive_themes = _counter_theme_rows(defensive_theme_counts, context)
    repeated_vulnerable_managers = _counter_manager_rows(vulnerable_manager_counts, context)
    repeated_defensive_managers = _counter_manager_rows(defensive_manager_counts, context)

    return {
        "schema_version": "analytics_cross_scenario_resilience_summary.v1",
        "generated_at": GENERATED_AT,
        "pack_id": context["pack_id"],
        "pack_version": context["pack_version"],
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "data_as_of": context["data_as_of"],
        "most_vulnerable_scenario": _scenario_resilience_row(most_vulnerable),
        "most_resilient_scenario": _scenario_resilience_row(most_resilient),
        "repeated_vulnerable_themes": repeated_vulnerable_themes,
        "repeated_defensive_themes": repeated_defensive_themes,
        "repeated_vulnerable_managers": repeated_vulnerable_managers,
        "repeated_defensive_managers": repeated_defensive_managers,
        "key_advisor_discussion_points": _discussion_points(
            most_vulnerable,
            most_resilient,
            repeated_vulnerable_themes,
            repeated_vulnerable_managers,
        ),
        "caveats": [
            "Cross-scenario resilience is a simple deterministic summary across existing synthetic scenario outputs.",
            "Repeated vulnerability counts are based on top affected themes/managers per scenario, not a probability model.",
        ],
    }


def build_output_index(context: dict[str, Any], outputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "analytics_output_index.v1",
        "generated_at": GENERATED_AT,
        "pack_id": context["pack_id"],
        "pack_version": context["pack_version"],
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "data_as_of": context["data_as_of"],
        "output_count": len(OUTPUT_FILES) - 1,
        "outputs": [
            {
                "output_name": output_name,
                "path": f"data/simulation/analytics/{filename}",
                "schema_version": outputs[output_name]["schema_version"],
            }
            for output_name, filename in OUTPUT_FILES.items()
            if output_name != "analytics_output_index"
        ],
        "source_inputs": [
            "data/analytic_packs/arranger_demo_pack_v1/pack_manifest.json",
            "data/simulation/synthetic_position_universe.json",
            "data/simulation/scenario_revaluation_results.json",
            "data/simulation/simplified_valuation_summary.json",
        ],
        "caveats": [
            "Synthetic proof outputs only; not wired into report-element inputs or advisor UI in this tranche.",
            "No external APIs, live data, Docker, Postgres, or production services are required.",
        ],
    }


def _build_context(
    pack: dict[str, Any],
    universe: dict[str, Any],
    scenario_revaluations: dict[str, Any],
    valuation_summary: dict[str, Any],
) -> dict[str, Any]:
    components = pack["components"]
    positions = universe["positions"]
    managers = universe.get("managers", [])
    sleeves = universe.get("sleeves", [])
    context = {
        "pack_id": pack["manifest"]["pack_id"],
        "pack_version": pack["manifest"]["pack_version"],
        "themes": components["theme_catalog"]["themes"],
        "scenarios": components["scenario_catalog"]["scenarios"],
        "confidence_rules": components["data_confidence_rule_catalog"]["rules"],
        "positions": positions,
        "positions_by_id": {position["position_id"]: position for position in positions},
        "manager_labels": {manager["manager_id"]: manager["display_name"] for manager in managers},
        "sleeve_labels": {sleeve["sleeve_id"]: sleeve["display_name"] for sleeve in sleeves},
        "portfolio_id": universe.get("portfolio", {}).get("portfolio_id"),
        "data_as_of": universe.get("as_of_date"),
        "total_portfolio_value": float(valuation_summary.get("total_current_portfolio_value") or sum(_position_value(position) for position in positions)),
        "scenario_results": scenario_revaluations.get("scenario_results", []),
        "valuation_summary": valuation_summary,
    }
    context["theme_by_id"] = {theme["theme_id"]: theme for theme in context["themes"]}
    context["theme_matchers"] = {
        theme["theme_id"]: _theme_matcher_values(theme)
        for theme in context["themes"]
    }
    return context


def _matched_theme_ids(position: dict[str, Any], context: dict[str, Any]) -> list[str]:
    values = _position_match_values(position)
    matched: list[str] = []
    for theme_id, matchers in context["theme_matchers"].items():
        if values & matchers:
            matched.append(theme_id)
    return matched


def _theme_matcher_values(theme: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for key in (
        "source_theme_names",
        "source_story_tags",
        "source_scenario_hints",
        "source_asset_classes",
        "source_classification_values",
        "example_position_tags",
    ):
        values.update(_normalize(item) for item in theme.get(key, []) if isinstance(item, str))
    return {value for value in values if value}


def _position_match_values(position: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for key in (
        "themes",
        "position_story_tags",
        "scenario_exposure_hints",
        "data_quality_flags",
        "required_market_state_variables",
    ):
        values.update(_normalize(item) for item in position.get(key, []) if isinstance(item, str))
    for key in (
        "instrument_type",
        "liquidity_bucket",
        "valuation_confidence",
        "valuation_method_hint",
        "proxy_mapping_hint",
    ):
        value = position.get(key)
        if isinstance(value, str):
            values.add(_normalize(value))
    classifications = position.get("classifications", {})
    if isinstance(classifications, dict):
        values.update(_normalize(value) for value in classifications.values() if isinstance(value, str))
        values.update(_normalize(key) for key in classifications if isinstance(key, str))
    return {value for value in values if value}


def _manager_impact_rows(result: dict[str, Any], context: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rows = [
        {
            "manager_id": row["id"],
            "manager_display_name": context["manager_labels"].get(row["id"], row["id"]),
            "base_value": _round_money(row["base_value"]),
            "scenario_impact": _round_money(row["scenario_impact"]),
            "scenario_impact_percent": _round_percent(row["scenario_impact_percent"]),
        }
        for row in result.get("manager_impacts", [])
    ]
    negative = sorted(rows, key=lambda row: row["scenario_impact"])[:3]
    positive = [row for row in rows if row["scenario_impact"] > 0]
    defensive_source = positive if positive else rows
    defensive = sorted(defensive_source, key=lambda row: row["scenario_impact"], reverse=True)[:3]
    return {
        "top_negative_managers": negative,
        "top_positive_or_defensive_managers": defensive,
    }


def _theme_impact_rows(result: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    theme_values: dict[str, dict[str, float]] = defaultdict(lambda: {"base_value": 0.0, "scenario_impact": 0.0, "scenario_value": 0.0})
    for impact in result.get("position_impacts", []):
        source_position = context["positions_by_id"].get(impact.get("position_id"), {})
        merged_position = {**source_position, **impact}
        matched_theme_ids = _matched_theme_ids(merged_position, context)
        if not matched_theme_ids:
            continue
        share = 1.0 / len(matched_theme_ids)
        for theme_id in matched_theme_ids:
            theme_values[theme_id]["base_value"] += float(impact.get("base_value", 0.0)) * share
            theme_values[theme_id]["scenario_impact"] += float(impact.get("scenario_impact", 0.0)) * share
            theme_values[theme_id]["scenario_value"] += float(impact.get("scenario_value", 0.0)) * share

    rows: list[dict[str, Any]] = []
    for theme_id, values in theme_values.items():
        theme = context["theme_by_id"][theme_id]
        rows.append(
            {
                "theme_id": theme_id,
                "theme_display_name": theme["display_name"],
                "base_value": _round_money(values["base_value"]),
                "scenario_impact": _round_money(values["scenario_impact"]),
                "scenario_impact_percent": _round_percent(_safe_divide(values["scenario_impact"], values["base_value"])),
                "scenario_value": _round_money(values["scenario_value"]),
                "allocation_method": "equal_split_across_approved_pack_theme_matches",
            }
        )
    rows.sort(key=lambda row: row["scenario_impact"])
    return rows


def _missing_scenario_row(context: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": scenario["scenario_id"],
        "scenario_display_name": scenario["display_name"],
        "advisor_story": scenario["advisor_story"],
        "scenario_status": "not_available_in_existing_synthetic_revaluation",
        "total_impact": None,
        "total_impact_percent": None,
        "base_total_value": _round_money(context["total_portfolio_value"]),
        "scenario_total_value": None,
        "top_negative_managers": [],
        "top_positive_or_defensive_managers": [],
        "theme_impacts": [],
        "confidence": "not_available",
        "caveats": list(scenario.get("caveats", [])) + ["No existing deterministic scenario revaluation output is available for this scenario."],
    }


def _confidence_bucket(position: dict[str, Any]) -> str:
    flags = set(position.get("data_quality_flags", []))
    if position.get("human_review_required") is True or "human_review_required" in flags:
        return "review_required"
    confidence = str(position.get("valuation_confidence", "unknown")).lower()
    if confidence in {"high", "medium", "low"}:
        return confidence
    return "unknown"


def _advisor_language_for_bucket(bucket: str, rules: list[dict[str, Any]]) -> str:
    rules_by_id = {rule["rule_id"]: rule["advisor_language"] for rule in rules}
    if bucket == "review_required":
        return rules_by_id.get("human_review_required", "Human review is required before treating this result as meeting-ready.")
    if bucket == "low":
        return rules_by_id.get("stale_or_manager_mark", "Low-confidence records should be called out with caveats.")
    if bucket == "medium":
        return rules_by_id.get("proxy_valuation", "Medium-confidence records are usable with explicit proxy caveats.")
    if bucket == "high":
        return rules_by_id.get("direct_price_or_mark", "High-confidence records are the cleanest source for demo analytics.")
    return "Unknown-confidence records should be reviewed before client-facing use."


def _confidence_notes_for_positions(positions: list[dict[str, Any]]) -> list[str]:
    counts = Counter(_confidence_bucket(position) for position in positions)
    notes = []
    for bucket in ("review_required", "low", "medium", "unknown", "high"):
        if counts[bucket]:
            notes.append(f"{counts[bucket]} positions: {bucket.replace('_', ' ')}")
    return notes


def _scenario_confidence(result: dict[str, Any]) -> str:
    completeness = result.get("scenario_completeness", {})
    if completeness.get("status") == "complete":
        return "medium"
    return "review_required"


def _scenario_resilience_row(scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": scenario["scenario_id"],
        "scenario_display_name": scenario["scenario_display_name"],
        "total_impact": scenario["total_impact"],
        "total_impact_percent": scenario["total_impact_percent"],
    }


def _discussion_points(
    most_vulnerable: dict[str, Any],
    most_resilient: dict[str, Any],
    vulnerable_themes: list[dict[str, Any]],
    vulnerable_managers: list[dict[str, Any]],
) -> list[str]:
    points = [
        f"Most vulnerable scenario in the synthetic set: {most_vulnerable['scenario_display_name']}.",
        f"Most resilient scenario in the synthetic set: {most_resilient['scenario_display_name']}.",
    ]
    if vulnerable_themes:
        points.append(f"Repeated vulnerable theme to review: {vulnerable_themes[0]['theme_display_name']}.")
    if vulnerable_managers:
        points.append(f"Repeated vulnerable manager to review: {vulnerable_managers[0]['manager_display_name']}.")
    points.append("Use these as advisor discussion prompts, not as probabilities or recommendations.")
    return points


def _sum_positions_by(positions: list[dict[str, Any]], key: str) -> dict[str, float]:
    values: dict[str, float] = defaultdict(float)
    for position in positions:
        group_id = position.get(key)
        if isinstance(group_id, str):
            values[group_id] += _position_value(position)
    return values


def _top_group_rows(
    grouped_values: dict[str, float],
    labels: dict[str, str],
    denominator: float,
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    rows = []
    for group_id, value in sorted(grouped_values.items(), key=lambda item: (-item[1], item[0]))[:limit]:
        rows.append(
            {
                "id": group_id,
                "display_name": labels.get(group_id, group_id),
                "exposure_value": _round_money(value),
                "percent_of_theme": _round_percent(_safe_divide(value, denominator)),
            }
        )
    return rows


def _top_theme_rows(
    theme_values: dict[str, float],
    context: dict[str, Any],
    denominator: float,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    rows = []
    for theme_id, value in sorted(theme_values.items(), key=lambda item: (-item[1], item[0]))[:limit]:
        theme = context["theme_by_id"].get(theme_id, {"display_name": theme_id})
        rows.append(
            {
                "theme_id": theme_id,
                "theme_display_name": theme["display_name"],
                "exposure_value": _round_money(value),
                "percent_of_bucket": _round_percent(_safe_divide(value, denominator)),
            }
        )
    return rows


def _counter_theme_rows(counter: Counter[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "theme_id": theme_id,
            "theme_display_name": context["theme_by_id"].get(theme_id, {"display_name": theme_id})["display_name"],
            "scenario_count": count,
        }
        for theme_id, count in counter.most_common()
        if count >= 2
    ]


def _counter_manager_rows(counter: Counter[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "manager_id": manager_id,
            "manager_display_name": context["manager_labels"].get(manager_id, manager_id),
            "scenario_count": count,
        }
        for manager_id, count in counter.most_common()
        if count >= 2
    ]


def _overlap_level(manager_count: int, exposure_percent: float) -> str:
    if manager_count >= 4 and exposure_percent >= 0.10:
        return "high"
    if manager_count >= 3 and exposure_percent >= 0.15:
        return "high"
    if manager_count >= 2 and exposure_percent >= 0.05:
        return "moderate"
    return "low"


def _overlap_interpretation(theme_display_name: str, overlap_level: str, manager_count: int) -> str:
    if overlap_level == "high":
        return f"{theme_display_name} appears across {manager_count} managers and should be treated as a hidden concentration discussion."
    if overlap_level == "moderate":
        return f"{theme_display_name} appears in more than one manager and may be worth checking for intentional overlap."
    return f"{theme_display_name} is relatively contained in the current synthetic portfolio."


def _all_position_themes(positions: list[dict[str, Any]]) -> set[str]:
    values: set[str] = set()
    for position in positions:
        values.update(theme for theme in position.get("themes", []) if isinstance(theme, str))
    return values


def _position_value(position: dict[str, Any]) -> float:
    return float(position.get("current_reported_value") or position.get("base_value") or 0.0)


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _round_money(value: float) -> float:
    return round(float(value), 2)


def _round_percent(value: float) -> float:
    return round(float(value), 6)


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic analytics proof outputs for the Arranger demo pack.")
    parser.add_argument("--pack-dir", default=str(DEFAULT_PACK_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    outputs = generate_demo_pack_outputs(pack_dir=Path(args.pack_dir), output_dir=Path(args.output_dir))
    index = outputs["analytics_output_index"]
    print(f"wrote {index['output_count']} analytics outputs to {args.output_dir}")


if __name__ == "__main__":
    main()
