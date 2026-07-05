from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-05T00:00:00Z"
SCENARIO_ID = "ai_chip_selloff"
METHODOLOGY = "full_portfolio_revaluation_attribution"
DEFAULT_REVALUATION_DIR = Path("data/simulation/revaluation")
DEFAULT_ATTRIBUTION_DIR = DEFAULT_REVALUATION_DIR / "attribution"
DEFAULT_POSITION_UNIVERSE_PATH = Path("data/simulation/synthetic_position_universe.json")
DEFAULT_PACK_DIR = Path("data/analytic_packs/arranger_demo_pack_v1")

INPUT_FILES = {
    "revaluation_bundle_manifest": "revaluation_bundle_manifest.json",
    "position_value_comparison": "position_value_comparison_ai_chip_selloff.json",
    "portfolio_revaluation_summary": "portfolio_revaluation_summary_ai_chip_selloff.json",
    "valuation_coverage_manifest": "valuation_coverage_manifest.json",
    "position_catalog": "position_catalog.json",
    "instrument_catalog": "instrument_catalog.json",
}

OUTPUT_FILES = {
    "manager_revaluation_attribution": "manager_revaluation_attribution_ai_chip_selloff.json",
    "account_revaluation_attribution": "account_revaluation_attribution_ai_chip_selloff.json",
    "sleeve_revaluation_attribution": "sleeve_revaluation_attribution_ai_chip_selloff.json",
    "coverage_revaluation_attribution": "coverage_revaluation_attribution_ai_chip_selloff.json",
    "confidence_revaluation_attribution": "confidence_revaluation_attribution_ai_chip_selloff.json",
    "theme_revaluation_attribution": "theme_revaluation_attribution_ai_chip_selloff.json",
    "thesis_bucket_revaluation_attribution_readiness": "thesis_bucket_revaluation_attribution_readiness.json",
    "cross_scenario_revaluation_readiness": "cross_scenario_revaluation_readiness.json",
    "revaluation_attribution_index": "revaluation_attribution_index.json",
}


def generate_revaluation_attribution_outputs(
    *,
    revaluation_dir: Path | str = DEFAULT_REVALUATION_DIR,
    output_dir: Path | str = DEFAULT_ATTRIBUTION_DIR,
    position_universe_path: Path | str = DEFAULT_POSITION_UNIVERSE_PATH,
    pack_dir: Path | str = DEFAULT_PACK_DIR,
) -> dict[str, Any]:
    """Generate attribution outputs from full revaluation comparison rows."""
    context = load_attribution_context(
        revaluation_dir=Path(revaluation_dir),
        position_universe_path=Path(position_universe_path),
        pack_dir=Path(pack_dir),
    )
    outputs = {
        "manager_revaluation_attribution": build_group_attribution(context, group_key="manager_id", group_kind="manager"),
        "account_revaluation_attribution": build_group_attribution(context, group_key="account_id", group_kind="account"),
        "sleeve_revaluation_attribution": build_group_attribution(context, group_key="sleeve_id", group_kind="sleeve"),
        "coverage_revaluation_attribution": build_bucket_attribution(context, bucket_key="scenario_coverage_status", bucket_kind="coverage"),
        "confidence_revaluation_attribution": build_bucket_attribution(context, bucket_key="confidence", bucket_kind="confidence"),
        "theme_revaluation_attribution": build_theme_attribution(context),
        "thesis_bucket_revaluation_attribution_readiness": build_thesis_bucket_readiness(context),
        "cross_scenario_revaluation_readiness": build_cross_scenario_readiness(context),
    }
    outputs["revaluation_attribution_index"] = build_attribution_index(context, outputs)

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    for output_name, filename in OUTPUT_FILES.items():
        _write_json(root / filename, outputs[output_name])
    return outputs


def load_attribution_context(
    *,
    revaluation_dir: Path,
    position_universe_path: Path,
    pack_dir: Path,
) -> dict[str, Any]:
    inputs = {
        name: _load_json(revaluation_dir / filename)
        for name, filename in INPUT_FILES.items()
    }
    universe = _load_json(position_universe_path) if position_universe_path.exists() else {}
    theme_catalog_path = pack_dir / "theme_catalog.json"
    theme_catalog = _load_json(theme_catalog_path) if theme_catalog_path.exists() else {}

    positions = inputs["position_catalog"].get("positions", [])
    instruments = inputs["instrument_catalog"].get("instruments", [])
    comparison_rows = inputs["position_value_comparison"].get("position_comparisons", [])
    portfolio_summary = inputs["portfolio_revaluation_summary"]
    bundle_manifest = inputs["revaluation_bundle_manifest"]

    position_by_id = {position["position_id"]: position for position in positions}
    instrument_by_id = {instrument["instrument_id"]: instrument for instrument in instruments}
    source_position_by_id = {
        position["position_id"]: position
        for position in universe.get("positions", [])
        if isinstance(position, dict) and isinstance(position.get("position_id"), str)
    }

    rows = []
    for comparison in comparison_rows:
        position = position_by_id[comparison["position_id"]]
        instrument = instrument_by_id[comparison["instrument_id"]]
        source_position = source_position_by_id.get(comparison["position_id"], {})
        rows.append(
            {
                **comparison,
                "display_name": position.get("display_name", comparison["position_id"]),
                "manager_id": position.get("manager_id"),
                "account_id": position.get("account_id"),
                "sleeve_id": position.get("sleeve_id"),
                "valuation_confidence": position.get("valuation_confidence"),
                "human_review_required": position.get("human_review_required", False),
                "human_review_flags": position.get("human_review_flags", []),
                "instrument_type": instrument.get("instrument_type"),
                "instrument_display_name": instrument.get("display_name"),
                "instrument_reference_data": instrument.get("reference_data", {}),
                "source_position": source_position,
            }
        )

    context = {
        **inputs,
        "rows": rows,
        "portfolio_summary": portfolio_summary,
        "bundle_manifest": bundle_manifest,
        "source_revaluation_bundle_id": _source_revaluation_bundle_id(bundle_manifest),
        "position_universe": universe,
        "theme_catalog": theme_catalog,
        "theme_catalog_path": theme_catalog_path,
        "revaluation_dir": revaluation_dir,
        "manager_labels": _labels(universe, "managers", "manager_id"),
        "account_labels": _labels(universe, "accounts", "account_id"),
        "sleeve_labels": _labels(universe, "sleeves", "sleeve_id"),
        "thesis_assignment_artifacts": _find_thesis_assignment_artifacts(pack_dir, revaluation_dir),
        "scenario_bundle_count": _count_full_revaluation_scenario_bundles(revaluation_dir),
    }
    return context


def build_group_attribution(context: dict[str, Any], *, group_key: str, group_kind: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in context["rows"]:
        group_id = row.get(group_key)
        if isinstance(group_id, str) and group_id:
            grouped[group_id].append(row)

    label_map = context[f"{group_kind}_labels"]
    rows = [
        _group_row(group_id, group_rows, label_map.get(group_id, group_id), context)
        for group_id, group_rows in grouped.items()
    ]
    rows.sort(key=lambda row: (abs(row["impact"]), row["group_id"]), reverse=True)
    return _base_output(
        context,
        schema_version=f"{group_kind}_revaluation_attribution.v1",
        extra={
            "group_kind": group_kind,
            "group_count": len(rows),
            "rows": rows,
            "reconciliation": _reconciliation(rows, context),
            "caveats": [
                "Attribution is computed from full revaluation position comparisons.",
                "Percent of portfolio impact is signed and may be negative for offsetting groups.",
            ],
        },
    )


def build_bucket_attribution(context: dict[str, Any], *, bucket_key: str, bucket_kind: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in context["rows"]:
        grouped[str(row.get(bucket_key, "unknown"))].append(row)

    rows = []
    for bucket_id, bucket_rows in grouped.items():
        row = _value_summary(bucket_rows, context)
        row.update(
            {
                "bucket_id": bucket_id,
                "display_name": _bucket_display_name(bucket_id),
                "position_count": len(bucket_rows),
                "review_required_position_count": sum(1 for item in bucket_rows if item.get("review_required")),
                "top_positions_by_absolute_impact": _top_positions(bucket_rows),
                "advisor_safe_caveat": _bucket_caveat(bucket_kind, bucket_id),
            }
        )
        rows.append(row)
    rows.sort(key=lambda row: (row["display_name"], row["bucket_id"]))

    material_key = (
        "top_material_review_required_positions"
        if bucket_kind == "coverage"
        else "top_material_low_or_review_confidence_positions"
    )
    material_rows = [
        row
        for row in context["rows"]
        if (
            row.get("review_required")
            if bucket_kind == "coverage"
            else row.get("confidence") in {"low", "review_required"}
        )
    ]
    return _base_output(
        context,
        schema_version=f"{bucket_kind}_revaluation_attribution.v1",
        extra={
            "bucket_kind": bucket_kind,
            "bucket_count": len(rows),
            "rows": rows,
            material_key: _top_positions(material_rows, limit=10),
            "reconciliation": _reconciliation(rows, context),
            "caveats": [
                "Buckets summarize valuation coverage and confidence after full revaluation.",
                "Review-required records are kept visible instead of being converted into unsupported point claims.",
            ],
        },
    )


def build_theme_attribution(context: dict[str, Any]) -> dict[str, Any]:
    themes = context.get("theme_catalog", {}).get("themes", [])
    if not themes:
        return _theme_placeholder(context, "missing_theme_catalog", "No approved theme catalog was available.")

    matchers = {
        theme["theme_id"]: _theme_matcher_values(theme)
        for theme in themes
        if isinstance(theme.get("theme_id"), str)
    }
    theme_by_id = {theme["theme_id"]: theme for theme in themes if isinstance(theme.get("theme_id"), str)}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unclassified = []
    for row in context["rows"]:
        matched = _matched_theme_ids(row, matchers)
        if not matched:
            unclassified.append(row)
        for theme_id in matched:
            grouped[theme_id].append(row)

    if not grouped:
        return _theme_placeholder(
            context,
            "no_position_level_theme_matches",
            "No compatible position-level theme tags or classifications matched the approved theme catalog.",
        )

    rows = []
    for theme_id, theme_rows in grouped.items():
        theme = theme_by_id[theme_id]
        row = _value_summary(theme_rows, context)
        row.update(
            {
                "theme_id": theme_id,
                "theme_display_name": theme.get("display_name", theme_id),
                "position_count": len(theme_rows),
                "top_positions_by_absolute_impact": _top_positions(theme_rows),
                "coverage_mix": _mix(theme_rows, "scenario_coverage_status"),
                "confidence_mix": _mix(theme_rows, "confidence"),
                "matching_basis": "approved_pack_theme_matchers_against_position_tags_and_classifications",
                "advisor_description": theme.get("advisor_description"),
                "caveats": list(theme.get("caveats", [])),
            }
        )
        rows.append(row)
    rows.sort(key=lambda row: abs(row["impact"]), reverse=True)

    return _base_output(
        context,
        schema_version="theme_revaluation_attribution.v1",
        extra={
            "attribution_status": "limited_gross_position_tag_attribution",
            "additivity": "non_additive_gross_theme_tags",
            "reconciles_to_portfolio": False,
            "theme_count": len(rows),
            "unclassified_position_count": len(unclassified),
            "rows": rows,
            "limitations": [
                "General theme tags can overlap, so theme values and impacts are gross and should not be summed.",
                "No value-weighted split or thesis primary-bucket assignment is fabricated in this artifact.",
                "Report-ready additive thesis buckets require published position-thesis assignments.",
            ],
            "caveats": [
                "Theme attribution uses full revaluation position impacts plus existing synthetic position tags/classifications.",
                "This artifact supersedes legacy proof impact views only for the single full-revaluation scenario shown here.",
            ],
        },
    )


def build_thesis_bucket_readiness(context: dict[str, Any]) -> dict[str, Any]:
    artifacts = context["thesis_assignment_artifacts"]
    return _base_output(
        context,
        schema_version="thesis_bucket_revaluation_attribution_readiness.v1",
        extra={
            "status": "requires_published_position_thesis_assignments",
            "thesis_assignment_artifacts_found": artifacts,
            "bucket_rows": [],
            "totals_generated": False,
            "readiness_notes": [
                "Thesis-bucket attribution requires one published primary bucket assignment per in-scope position.",
                "Thesis lenses are post-valuation classification artifacts; they do not price positions or construct scenario market states.",
                "No thesis-bucket totals are generated until approved assignments exist.",
            ],
            "caveats": [
                "No fake thesis assignments were created in this tranche.",
            ],
        },
    )


def build_cross_scenario_readiness(context: dict[str, Any]) -> dict[str, Any]:
    return _base_output(
        context,
        schema_version="cross_scenario_revaluation_readiness.v1",
        extra={
            "status": "requires_additional_full_revaluation_scenario_bundles",
            "available_full_revaluation_scenario_count": context["scenario_bundle_count"],
            "available_scenario_ids": [context["bundle_manifest"]["scenario_id"]],
            "cross_scenario_rows": [],
            "readiness_notes": [
                "Cross-scenario revaluation resilience requires at least two scenario revaluation bundles.",
                "Existing legacy proof outputs may remain useful as reference, but they are not mixed into this full-revaluation attribution set.",
            ],
            "caveats": [
                "Only AI / Chip Selloff has a committed full revaluation bundle in this checkpoint.",
            ],
        },
    )


def build_attribution_index(context: dict[str, Any], outputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    output_rows = []
    for output_name, filename in OUTPUT_FILES.items():
        if output_name == "revaluation_attribution_index":
            continue
        payload = outputs[output_name]
        output_rows.append(
            {
                "output_name": output_name,
                "path": f"data/simulation/revaluation/attribution/{filename}",
                "schema_version": payload["schema_version"],
                "status": payload.get("status") or payload.get("attribution_status") or "available",
            }
        )
    return _base_output(
        context,
        schema_version="revaluation_attribution_index.v1",
        extra={
            "output_count": len(output_rows),
            "outputs": output_rows,
            "source_manifests": [
                "data/simulation/revaluation/revaluation_bundle_manifest.json",
                "data/simulation/revaluation/valuation_coverage_manifest.json",
            ],
            "source_inputs": [
                "data/simulation/revaluation/position_value_comparison_ai_chip_selloff.json",
                "data/simulation/revaluation/position_catalog.json",
                "data/simulation/revaluation/instrument_catalog.json",
                "data/simulation/synthetic_position_universe.json",
                "data/analytic_packs/arranger_demo_pack_v1/theme_catalog.json",
            ],
            "current_limitations": [
                "Only one full-revaluation scenario bundle is available.",
                "Theme attribution is non-additive because general theme tags can overlap.",
                "Thesis-bucket attribution is readiness-only until position-thesis assignment artifacts are published.",
                "Outputs are not wired into report elements or advisor UI in this tranche.",
            ],
            "caveats": [
                "Synthetic internal analytics outputs only.",
                "No external APIs, live data, Docker, Postgres, production services, or production reporting are required.",
            ],
        },
    )


def _base_output(context: dict[str, Any], *, schema_version: str, extra: dict[str, Any]) -> dict[str, Any]:
    bundle = context["bundle_manifest"]
    summary = context["portfolio_summary"]
    return {
        "schema_version": schema_version,
        "generated_at": GENERATED_AT,
        "methodology": METHODOLOGY,
        "synthetic_data": True,
        "source_revaluation_bundle_id": context["source_revaluation_bundle_id"],
        "source_revaluation_manifest": "data/simulation/revaluation/revaluation_bundle_manifest.json",
        "scenario_id": bundle["scenario_id"],
        "base_market_state_id": bundle["base_market_state_id"],
        "scenario_market_state_id": bundle["scenario_market_state_id"],
        "base_portfolio_value": summary["base_portfolio_value"],
        "scenario_portfolio_value": summary["scenario_portfolio_value"],
        "portfolio_impact": summary["impact"],
        "portfolio_impact_percent": summary["impact_percent"],
        **extra,
    }


def _group_row(group_id: str, rows: list[dict[str, Any]], display_name: str, context: dict[str, Any]) -> dict[str, Any]:
    summary = _value_summary(rows, context)
    summary.update(
        {
            "group_id": group_id,
            "display_name": display_name,
            "position_count": len(rows),
            "top_positions_by_absolute_impact": _top_positions(rows),
            "coverage_mix": _mix(rows, "scenario_coverage_status"),
            "confidence_mix": _mix(rows, "confidence"),
            "caveats": _group_caveats(rows),
        }
    )
    return summary


def _value_summary(rows: list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]:
    base_value = _round_money(sum(float(row["base_value"]) for row in rows))
    scenario_value = _round_money(sum(float(row["scenario_value"]) for row in rows))
    impact = _round_money(scenario_value - base_value)
    summary = context["portfolio_summary"]
    return {
        "base_value": base_value,
        "scenario_value": scenario_value,
        "impact": impact,
        "impact_percent": _round_percent(_safe_divide(impact, base_value)),
        "percent_of_portfolio_base": _round_percent(_safe_divide(base_value, summary["base_portfolio_value"])),
        "percent_of_portfolio_impact": _round_percent(_safe_divide(impact, summary["impact"])),
    }


def _top_positions(rows: list[dict[str, Any]], *, limit: int = 5) -> list[dict[str, Any]]:
    sorted_rows = sorted(rows, key=lambda row: (abs(float(row["value_change"])), row["position_id"]), reverse=True)
    return [
        {
            "position_id": row["position_id"],
            "display_name": row["display_name"],
            "manager_id": row.get("manager_id"),
            "account_id": row.get("account_id"),
            "sleeve_id": row.get("sleeve_id"),
            "base_value": row["base_value"],
            "scenario_value": row["scenario_value"],
            "impact": row["value_change"],
            "impact_percent": row["value_change_percent"],
            "coverage_status": row["scenario_coverage_status"],
            "confidence": row["confidence"],
            "review_required": row["review_required"],
        }
        for row in sorted_rows[:limit]
    ]


def _mix(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, "unknown"))].append(row)
    return {
        bucket: {
            "count": len(bucket_rows),
            "base_value": _round_money(sum(float(row["base_value"]) for row in bucket_rows)),
            "scenario_value": _round_money(sum(float(row["scenario_value"]) for row in bucket_rows)),
            "impact": _round_money(sum(float(row["value_change"]) for row in bucket_rows)),
        }
        for bucket, bucket_rows in sorted(grouped.items())
    }


def _reconciliation(rows: list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]:
    summary = context["portfolio_summary"]
    base_total = _round_money(sum(float(row["base_value"]) for row in rows))
    scenario_total = _round_money(sum(float(row["scenario_value"]) for row in rows))
    impact_total = _round_money(sum(float(row["impact"]) for row in rows))
    return {
        "base_value_matches_portfolio": base_total == summary["base_portfolio_value"],
        "scenario_value_matches_portfolio": scenario_total == summary["scenario_portfolio_value"],
        "impact_matches_portfolio": impact_total == summary["impact"],
        "base_value_total": base_total,
        "scenario_value_total": scenario_total,
        "impact_total": impact_total,
    }


def _theme_placeholder(context: dict[str, Any], status: str, note: str) -> dict[str, Any]:
    return _base_output(
        context,
        schema_version="theme_revaluation_attribution.v1",
        extra={
            "attribution_status": status,
            "additivity": "not_available",
            "reconciles_to_portfolio": False,
            "theme_count": 0,
            "unclassified_position_count": len(context["rows"]),
            "rows": [],
            "limitations": [note, "No theme totals are generated without compatible position-level mappings."],
            "caveats": ["No fake theme mappings were created in this tranche."],
        },
    )


def _matched_theme_ids(row: dict[str, Any], matchers: dict[str, set[str]]) -> list[str]:
    values = _position_match_values(row)
    return [
        theme_id
        for theme_id, matcher_values in sorted(matchers.items())
        if values & matcher_values
    ]


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


def _position_match_values(row: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    source_position = row.get("source_position", {})
    for key in (
        "themes",
        "position_story_tags",
        "scenario_exposure_hints",
        "data_quality_flags",
        "required_market_state_variables",
        "human_review_flags",
    ):
        raw = source_position.get(key) or row.get(key) or []
        values.update(_normalize(item) for item in raw if isinstance(item, str))
    for key in (
        "instrument_type",
        "valuation_confidence",
        "valuation_method_hint",
        "display_name",
        "instrument_display_name",
    ):
        value = source_position.get(key) or row.get(key)
        if isinstance(value, str):
            values.add(_normalize(value))
    for mapping in (
        source_position.get("classifications", {}),
        row.get("instrument_reference_data", {}),
    ):
        if isinstance(mapping, dict):
            values.update(_normalize(value) for value in mapping.values() if isinstance(value, str))
            values.update(_normalize(key) for key in mapping if isinstance(key, str))
    return {value for value in values if value}


def _labels(universe: dict[str, Any], list_key: str, id_key: str) -> dict[str, str]:
    labels = {}
    for row in universe.get(list_key, []):
        if isinstance(row, dict) and isinstance(row.get(id_key), str):
            labels[row[id_key]] = row.get("display_name") or row[id_key]
    return labels


def _source_revaluation_bundle_id(bundle: dict[str, Any]) -> str:
    return f"{bundle['scenario_id']}:{bundle['base_market_state_id']}:{bundle['scenario_market_state_id']}"


def _find_thesis_assignment_artifacts(pack_dir: Path, revaluation_dir: Path) -> list[str]:
    candidates = [
        pack_dir / "position_thesis_assignment_manifest.json",
        revaluation_dir / "position_thesis_assignment_manifest.json",
    ]
    artifacts = []
    for path in candidates:
        if path.exists():
            artifacts.append(str(path).replace("\\", "/"))
    return artifacts


def _count_full_revaluation_scenario_bundles(revaluation_dir: Path) -> int:
    manifest_path = revaluation_dir / "revaluation_bundle_manifest.json"
    if not manifest_path.exists():
        return 0
    return 1


def _group_caveats(rows: list[dict[str, Any]]) -> list[str]:
    caveats = []
    if any(row.get("review_required") for row in rows):
        caveats.append("At least one position requires review before relying on point impact.")
    if any(row.get("scenario_coverage_status") == "held_at_mark_with_caveat" for row in rows):
        caveats.append("Some positions were held at approved marks; scenario impact may understate true exposure.")
    if not caveats:
        caveats.append("Attribution derives from valued position comparisons under the approved scenario market state.")
    return caveats


def _bucket_caveat(bucket_kind: str, bucket_id: str) -> str:
    if bucket_kind == "coverage":
        return {
            "valued": "Positions were valued under the approved scenario market state.",
            "valued_with_substitute_input": "Positions used approved substitute inputs and should carry source caveats.",
            "valued_with_approved_policy": "Positions were valued with approved synthetic policies where direct production valuation is out of scope.",
            "held_at_mark_with_caveat": "Positions were held at approved marks; scenario impact may understate true exposure.",
            "review_required": "Positions require review before relying on scenario impact.",
            "not_valued": "Positions were not valued and should remain unresolved until coverage improves.",
        }.get(bucket_id, "Coverage bucket requires review.")
    return {
        "high": "High-confidence records are the cleanest synthetic source for this attribution.",
        "medium": "Medium-confidence records are usable with explicit caveats.",
        "low": "Low-confidence records should be treated directionally and reviewed if material.",
        "review_required": "Review-required records should not support strong point-impact claims without review.",
    }.get(bucket_id, "Confidence bucket requires review.")


def _bucket_display_name(bucket_id: str) -> str:
    return bucket_id.replace("_", " ").title()


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate full-revaluation attribution outputs.")
    parser.add_argument("--revaluation-dir", default=str(DEFAULT_REVALUATION_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_ATTRIBUTION_DIR))
    parser.add_argument("--position-universe", default=str(DEFAULT_POSITION_UNIVERSE_PATH))
    parser.add_argument("--pack-dir", default=str(DEFAULT_PACK_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outputs = generate_revaluation_attribution_outputs(
        revaluation_dir=Path(args.revaluation_dir),
        output_dir=Path(args.output_dir),
        position_universe_path=Path(args.position_universe),
        pack_dir=Path(args.pack_dir),
    )
    manager = outputs["manager_revaluation_attribution"]
    account = outputs["account_revaluation_attribution"]
    sleeve = outputs["sleeve_revaluation_attribution"]
    coverage = outputs["coverage_revaluation_attribution"]
    confidence = outputs["confidence_revaluation_attribution"]

    print("Full-revaluation attribution outputs generated")
    print(f"Scenario: {manager['scenario_id']}")
    print(f"Managers: {manager['group_count']}")
    print(f"Accounts: {account['group_count']}")
    print(f"Sleeves: {sleeve['group_count']}")
    print(f"Coverage buckets: {coverage['bucket_count']}")
    print(f"Confidence buckets: {confidence['bucket_count']}")
    print(f"Output directory: {Path(args.output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
