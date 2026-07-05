from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from arangur.analytics.pricing_functions import (
    VALID_COVERAGE_STATUSES,
    check_market_input_coverage,
    required_market_inputs,
    select_pricing_function as _select_pricing_function,
    value_with_pricing_function,
)


GENERATED_AT = "2026-07-05T00:00:00Z"
SCENARIO_ID = "ai_chip_selloff"
DEFAULT_POSITION_UNIVERSE_PATH = Path("data/simulation/synthetic_position_universe.json")
DEFAULT_SCENARIO_MARKET_STATES_PATH = Path("data/simulation/synthetic_scenario_market_states.json")
DEFAULT_OUTPUT_DIR = Path("data/simulation/revaluation")

INPUT_FILES = {
    "instrument_catalog": "instrument_catalog.json",
    "position_catalog": "position_catalog.json",
    "pricing_function_registry": "pricing_function_registry.json",
    "base_market_state": "base_market_state.json",
    "scenario_market_state": "scenario_market_state_ai_chip_selloff.json",
    "position_pricing_function_assignments": "position_pricing_function_assignments.json",
    "valuation_input_coverage_map_base": "valuation_input_coverage_map_base.json",
    "valuation_input_coverage_map_ai_chip_selloff": "valuation_input_coverage_map_ai_chip_selloff.json",
}

OUTPUT_FILES = {
    "position_valuation_results_base": "position_valuation_results_base.json",
    "position_valuation_results_ai_chip_selloff": "position_valuation_results_ai_chip_selloff.json",
    "position_value_comparison_ai_chip_selloff": "position_value_comparison_ai_chip_selloff.json",
    "portfolio_revaluation_summary_ai_chip_selloff": "portfolio_revaluation_summary_ai_chip_selloff.json",
    "valuation_coverage_manifest": "valuation_coverage_manifest.json",
    "revaluation_bundle_manifest": "revaluation_bundle_manifest.json",
}

PRIVATE_OR_OPAQUE_TYPES = {
    "private_credit",
    "private_equity",
    "real_estate",
    "data_center_investment",
    "opaque_manager_level",
}


def load_revaluation_fixtures(output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """Load generated synthetic revaluation fixture inputs."""
    root = Path(output_dir)
    return {
        name: _load_json(root / filename)
        for name, filename in INPUT_FILES.items()
    }


def generate_revaluation_fixtures(
    *,
    position_universe_path: Path | str = DEFAULT_POSITION_UNIVERSE_PATH,
    scenario_market_states_path: Path | str = DEFAULT_SCENARIO_MARKET_STATES_PATH,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Generate normalized fixture inputs for the synthetic full revaluation skeleton."""
    universe = _load_json(Path(position_universe_path))
    scenario_payload = _load_json(Path(scenario_market_states_path))
    scenario_source = _scenario_by_id(scenario_payload, SCENARIO_ID)

    instruments = build_instrument_catalog(universe)
    positions = build_position_catalog(universe)
    registry = build_pricing_function_registry()
    base_market_state = build_market_state(
        positions=positions["positions"],
        instruments=instruments["instruments"],
        scenario_source=None,
        universe=universe,
    )
    scenario_market_state = build_market_state(
        positions=positions["positions"],
        instruments=instruments["instruments"],
        scenario_source=scenario_source,
        universe=universe,
    )
    assignments = build_position_pricing_function_assignments(
        positions=positions,
        instruments=instruments,
        registry=registry,
        market_state=base_market_state,
    )
    base_coverage = build_valuation_input_coverage_map(
        positions=positions,
        instruments=instruments,
        registry=registry,
        market_state=base_market_state,
    )
    scenario_coverage = build_valuation_input_coverage_map(
        positions=positions,
        instruments=instruments,
        registry=registry,
        market_state=scenario_market_state,
    )

    fixtures = {
        "instrument_catalog": instruments,
        "position_catalog": positions,
        "pricing_function_registry": registry,
        "base_market_state": base_market_state,
        "scenario_market_state": scenario_market_state,
        "position_pricing_function_assignments": assignments,
        "valuation_input_coverage_map_base": base_coverage,
        "valuation_input_coverage_map_ai_chip_selloff": scenario_coverage,
    }
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    for name, filename in INPUT_FILES.items():
        _write_json(output_path / filename, fixtures[name])
    return fixtures


def run_full_revaluation(
    *,
    position_universe_path: Path | str = DEFAULT_POSITION_UNIVERSE_PATH,
    scenario_market_states_path: Path | str = DEFAULT_SCENARIO_MARKET_STATES_PATH,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Generate fixture inputs, value every position, compare, aggregate, and write outputs."""
    fixtures = generate_revaluation_fixtures(
        position_universe_path=position_universe_path,
        scenario_market_states_path=scenario_market_states_path,
        output_dir=output_dir,
    )
    base_results = value_portfolio(
        positions=fixtures["position_catalog"],
        instruments=fixtures["instrument_catalog"],
        market_state=fixtures["base_market_state"],
        pricing_function_registry=fixtures["pricing_function_registry"],
    )
    scenario_results = value_portfolio(
        positions=fixtures["position_catalog"],
        instruments=fixtures["instrument_catalog"],
        market_state=fixtures["scenario_market_state"],
        pricing_function_registry=fixtures["pricing_function_registry"],
    )
    comparisons = compare_position_values(
        base_results["position_results"],
        scenario_results["position_results"],
        fixtures["scenario_market_state"],
    )
    portfolio_summary = aggregate_position_comparisons(comparisons)
    coverage_manifest = build_valuation_coverage_manifest(fixtures, comparisons)
    bundle_manifest = publish_revaluation_bundle(
        output_dir=Path(output_dir),
        base_results=base_results,
        scenario_results=scenario_results,
        comparisons=comparisons,
        portfolio_summary=portfolio_summary,
        coverage_manifest=coverage_manifest,
    )
    return {
        "fixtures": fixtures,
        "position_valuation_results_base": base_results,
        "position_valuation_results_ai_chip_selloff": scenario_results,
        "position_value_comparison_ai_chip_selloff": comparisons,
        "portfolio_revaluation_summary_ai_chip_selloff": portfolio_summary,
        "valuation_coverage_manifest": coverage_manifest,
        "revaluation_bundle_manifest": bundle_manifest,
    }


def select_pricing_function(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    return _select_pricing_function(position, instrument, market_state, registry)


def value_position(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    return value_with_pricing_function(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
    )


def value_portfolio(
    *,
    positions: dict[str, Any],
    instruments: dict[str, Any],
    market_state: dict[str, Any],
    pricing_function_registry: dict[str, Any],
) -> dict[str, Any]:
    instruments_by_id = {
        instrument["instrument_id"]: instrument
        for instrument in instruments["instruments"]
    }
    valuation_context = {
        "pricing_function_registry": pricing_function_registry,
        "instrument_catalog": instruments,
    }
    results = []
    for position in positions["positions"]:
        instrument = instruments_by_id[position["instrument_id"]]
        results.append(value_position(position, instrument, market_state, valuation_context))
    return {
        "schema_version": "position_valuation_results.v1",
        "generated_at": GENERATED_AT,
        "methodology": "full_portfolio_revaluation",
        "synthetic_data": True,
        "portfolio_id": positions["portfolio_id"],
        "market_state_id": market_state["market_state_id"],
        "valuation_date": market_state["valuation_date"],
        "base_or_scenario": market_state["base_or_scenario"],
        "scenario_id": market_state.get("scenario_id"),
        "position_count": len(results),
        "position_results": results,
        "summary": _valuation_result_summary(results),
    }


def compare_position_values(
    base_results: list[dict[str, Any]],
    scenario_results: list[dict[str, Any]],
    scenario_market_state: dict[str, Any],
) -> dict[str, Any]:
    scenario_by_position = {
        result["position_id"]: result
        for result in scenario_results
    }
    comparisons = []
    for base in base_results:
        scenario = scenario_by_position[base["position_id"]]
        value_change = _round_money(float(scenario["value"]) - float(base["value"]))
        comparisons.append(
            {
                "position_id": base["position_id"],
                "instrument_id": base["instrument_id"],
                "base_market_state_id": base["market_state_id"],
                "scenario_market_state_id": scenario["market_state_id"],
                "scenario_id": scenario_market_state["scenario_id"],
                "base_value": base["value"],
                "scenario_value": scenario["value"],
                "value_change": value_change,
                "value_change_percent": _round_percent(_safe_divide(value_change, float(base["value"]))),
                "base_coverage_status": base["coverage_status"],
                "scenario_coverage_status": scenario["coverage_status"],
                "confidence": _combine_confidence(base["confidence"], scenario["confidence"]),
                "caveats": _unique(base.get("caveats", []) + scenario.get("caveats", [])),
                "review_required": bool(base["review_required"] or scenario["review_required"]),
                "synthetic_data": True,
            }
        )
    return {
        "schema_version": "position_value_comparison.v1",
        "generated_at": GENERATED_AT,
        "methodology": "full_portfolio_revaluation",
        "synthetic_data": True,
        "scenario_id": scenario_market_state["scenario_id"],
        "base_market_state_id": scenario_market_state["base_market_state_id"],
        "scenario_market_state_id": scenario_market_state["market_state_id"],
        "position_count": len(comparisons),
        "position_comparisons": comparisons,
        "portfolio_summary": aggregate_position_comparisons({"position_comparisons": comparisons}),
    }


def aggregate_position_comparisons(comparisons_payload: dict[str, Any]) -> dict[str, Any]:
    rows = comparisons_payload["position_comparisons"]
    base_total = sum(float(row["base_value"]) for row in rows)
    scenario_total = sum(float(row["scenario_value"]) for row in rows)
    impact = _round_money(scenario_total - base_total)
    return {
        "schema_version": "portfolio_revaluation_summary.v1",
        "generated_at": GENERATED_AT,
        "methodology": "full_portfolio_revaluation",
        "synthetic_data": True,
        "scenario_id": SCENARIO_ID,
        "base_portfolio_value": _round_money(base_total),
        "scenario_portfolio_value": _round_money(scenario_total),
        "impact": impact,
        "impact_percent": _round_percent(_safe_divide(impact, base_total)),
        "position_count": len(rows),
        "coverage_summary": _comparison_coverage_summary(rows),
        "confidence_summary": _comparison_confidence_summary(rows),
        "review_required_count": sum(1 for row in rows if row["review_required"]),
        "caveats": [
            "Synthetic internal full-revaluation skeleton only.",
            "Advisor UI and report-element wiring remain paused.",
        ],
    }


def publish_revaluation_bundle(
    *,
    output_dir: Path,
    base_results: dict[str, Any],
    scenario_results: dict[str, Any],
    comparisons: dict[str, Any],
    portfolio_summary: dict[str, Any],
    coverage_manifest: dict[str, Any],
) -> dict[str, Any]:
    outputs = {
        "position_valuation_results_base": base_results,
        "position_valuation_results_ai_chip_selloff": scenario_results,
        "position_value_comparison_ai_chip_selloff": comparisons,
        "portfolio_revaluation_summary_ai_chip_selloff": portfolio_summary,
        "valuation_coverage_manifest": coverage_manifest,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        _write_json(output_dir / OUTPUT_FILES[name], payload)
    manifest = {
        "schema_version": "revaluation_bundle_manifest.v1",
        "generated_at": GENERATED_AT,
        "methodology": "full_portfolio_revaluation",
        "synthetic_data": True,
        "scenario_id": SCENARIO_ID,
        "base_market_state_id": comparisons["base_market_state_id"],
        "scenario_market_state_id": comparisons["scenario_market_state_id"],
        "position_count": comparisons["position_count"],
        "base_portfolio_value": portfolio_summary["base_portfolio_value"],
        "scenario_portfolio_value": portfolio_summary["scenario_portfolio_value"],
        "impact": portfolio_summary["impact"],
        "impact_percent": portfolio_summary["impact_percent"],
        "coverage_summary": portfolio_summary["coverage_summary"],
        "confidence_summary": portfolio_summary["confidence_summary"],
        "review_required_count": portfolio_summary["review_required_count"],
        "input_files": [
            f"data/simulation/revaluation/{filename}"
            for filename in INPUT_FILES.values()
        ],
        "output_files": [
            f"data/simulation/revaluation/{filename}"
            for filename in OUTPUT_FILES.values()
        ],
        "caveats": [
            "Synthetic internal analytics infrastructure only.",
            "No advisor UI, report views, backend endpoints, external APIs, live data, or real client data are used.",
            "Scenario impact is scenario portfolio value minus base portfolio value after valuing every position.",
        ],
    }
    _write_json(output_dir / OUTPUT_FILES["revaluation_bundle_manifest"], manifest)
    return manifest


def build_instrument_catalog(universe: dict[str, Any]) -> dict[str, Any]:
    seen: dict[str, dict[str, Any]] = {}
    for position in universe["positions"]:
        instrument_id = position["instrument_id"]
        if instrument_id in seen:
            continue
        instrument_type = position["instrument_type"]
        seen[instrument_id] = {
            "instrument_id": instrument_id,
            "instrument_type": instrument_type,
            "display_name": position["display_name"],
            "issuer": position["display_name"] if instrument_type in {"public_equity", "fixed_income"} else None,
            "counterparty": None,
            "currency": position.get("base_currency", "USD"),
            "terms": _instrument_terms(position),
            "reference_data": {
                "synthetic_identifier": position.get("synthetic_identifier"),
                "asset_class": position.get("classifications", {}).get("asset_class", instrument_type),
                "sector": position.get("classifications", {}).get("sector"),
                "industry": position.get("classifications", {}).get("industry"),
                "geography": position.get("classifications", {}).get("geography"),
                "source_position_id": position["position_id"],
            },
            "lifecycle_dates": _lifecycle_dates(instrument_type),
            "payoff_description": _payoff_description(instrument_type),
            "required_input_families": _required_input_families_for_type(instrument_type),
            "eligible_pricing_functions": _eligible_pricing_functions_for_type(instrument_type),
            "coverage_policy": _coverage_policy_for_type(instrument_type, position),
            "synthetic_data": True,
        }
    return {
        "schema_version": "instrument_catalog.v1",
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "portfolio_snapshot_id": universe["universe_id"],
        "portfolio_id": universe["portfolio"]["portfolio_id"],
        "valuation_date": universe["as_of_date"],
        "instrument_count": len(seen),
        "instruments": sorted(seen.values(), key=lambda row: row["instrument_id"]),
        "source_metadata": {
            "source_path": str(DEFAULT_POSITION_UNIVERSE_PATH),
            "derived_from": universe["schema_version"],
        },
    }


def build_position_catalog(universe: dict[str, Any]) -> dict[str, Any]:
    positions = []
    for source in universe["positions"]:
        current_mark = float(source.get("current_reported_value") or 0.0)
        amount = _position_amount(source, current_mark)
        positions.append(
            {
                "position_id": source["position_id"],
                "instrument_id": source["instrument_id"],
                "display_name": source["display_name"],
                "account_id": source["account_id"],
                "manager_id": source["manager_id"],
                "sleeve_id": source["sleeve_id"],
                "amount_type": source.get("quantity_unit") or "amount",
                "amount": amount,
                "book_value": source.get("cost_basis"),
                "current_mark": current_mark,
                "currency": source.get("base_currency", "USD"),
                "valuation_confidence": source.get("valuation_confidence", "medium"),
                "valuation_method_hint": source.get("valuation_method_hint"),
                "data_freshness": "current" if source.get("valuation_confidence") in {"high", "medium"} else "review",
                "human_review_required": bool(source.get("human_review_required")),
                "human_review_flags": source.get("data_quality_flags", []),
                "synthetic_data": True,
            }
        )
    return {
        "schema_version": "position_catalog.v1",
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "portfolio_snapshot_id": universe["universe_id"],
        "portfolio_id": universe["portfolio"]["portfolio_id"],
        "valuation_date": universe["as_of_date"],
        "position_count": len(positions),
        "positions": positions,
        "source_metadata": {
            "source_path": str(DEFAULT_POSITION_UNIVERSE_PATH),
            "derived_from": universe["schema_version"],
        },
    }


def build_pricing_function_registry() -> dict[str, Any]:
    entries = [
        _pricing_entry("public_equity_price_lookup_v1", ["public_equity"], ["equity_prices"], "standard_public_equity_v1"),
        _pricing_entry("cash_face_value_v1", ["cash"], ["cash_scalars"], "cash_face_value_v1"),
        _pricing_entry("money_market_nav_lookup_v1", ["money_market"], ["money_market_navs"], "money_market_nav_v1"),
        _pricing_entry("fund_nav_lookup_v1", ["etf"], ["fund_prices"], "fund_or_etf_nav_v1"),
        _pricing_entry("bond_mark_scalar_v1", ["fixed_income"], ["bond_price_scalars"], "synthetic_bond_policy_v1"),
        _pricing_entry("fx_notional_translation_v1", ["fx_exposure"], ["fx_rates"], "fx_translation_v1"),
        _pricing_entry("commodity_price_lookup_v1", ["commodity"], ["commodity_prices"], "commodity_price_lookup_v1"),
        _pricing_entry("crypto_price_lookup_v1", ["crypto"], ["crypto_prices"], "crypto_price_lookup_v1"),
        _pricing_entry(
            "approved_private_mark_policy_v1",
            sorted(PRIVATE_OR_OPAQUE_TYPES),
            ["private_marks"],
            "approved_private_mark_policy_v1",
            allows_explicit_review_treatment=True,
        ),
        _pricing_entry(
            "review_required_treatment_v1",
            ["option_like", "structured_product", "opaque_manager_level"],
            ["review_policies"],
            "fallback_review_required_v1",
            allows_explicit_review_treatment=True,
        ),
    ]
    return {
        "schema_version": "pricing_function_registry.v1",
        "generated_at": GENERATED_AT,
        "registry_version": "synthetic_full_revaluation_skeleton_v1",
        "synthetic_data": True,
        "pricing_functions": entries,
        "coverage_policies": [
            "standard_public_equity_v1",
            "cash_face_value_v1",
            "money_market_nav_v1",
            "fund_or_etf_nav_v1",
            "synthetic_bond_policy_v1",
            "fx_translation_v1",
            "commodity_price_lookup_v1",
            "crypto_price_lookup_v1",
            "approved_private_mark_policy_v1",
            "fallback_review_required_v1",
        ],
        "approval_metadata": {
            "approval_status": "approved_for_synthetic_internal_skeleton",
            "approved_at": GENERATED_AT,
        },
    }


def build_market_state(
    *,
    positions: list[dict[str, Any]],
    instruments: list[dict[str, Any]],
    scenario_source: dict[str, Any] | None,
    universe: dict[str, Any],
) -> dict[str, Any]:
    instrument_by_id = {instrument["instrument_id"]: instrument for instrument in instruments}
    base_or_scenario = "scenario" if scenario_source else "base"
    scenario_id = scenario_source["scenario_id"] if scenario_source else None
    state_values = _state_variable_values(scenario_source)
    market_state_id = (
        f"market_state_scenario_{scenario_id}_{universe['as_of_date']}"
        if scenario_id
        else f"market_state_base_{universe['as_of_date']}"
    )
    market_inputs = _market_inputs_for_positions(positions, instrument_by_id, state_values, base_or_scenario)
    return {
        "schema_version": "revaluation_market_state.v1",
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "market_state_id": market_state_id,
        "valuation_date": universe["as_of_date"],
        "base_or_scenario": base_or_scenario,
        "scenario_id": scenario_id,
        "scenario_display_name": scenario_source.get("display_name") if scenario_source else None,
        "base_market_state_id": f"market_state_base_{universe['as_of_date']}" if scenario_source else None,
        "source_scenario_state_id": scenario_source.get("scenario_state_id") if scenario_source else None,
        "source_scenario_state_path": str(DEFAULT_SCENARIO_MARKET_STATES_PATH) if scenario_source else None,
        "market_inputs": market_inputs,
        "state_variable_values": state_values,
        "consistency_checks": {
            "required_input_families_present": sorted(market_inputs),
            "position_count": len(positions),
            "status": "complete",
        },
        "caveats": [
            "Synthetic full market-state fixture for internal revaluation skeleton only.",
            "Market inputs are deterministic synthetic values, not live market data.",
        ],
    }


def build_position_pricing_function_assignments(
    *,
    positions: dict[str, Any],
    instruments: dict[str, Any],
    registry: dict[str, Any],
    market_state: dict[str, Any],
) -> dict[str, Any]:
    instrument_by_id = {instrument["instrument_id"]: instrument for instrument in instruments["instruments"]}
    rows = []
    for position in positions["positions"]:
        instrument = instrument_by_id[position["instrument_id"]]
        entry = select_pricing_function(position, instrument, market_state, registry)
        rows.append(
            {
                "position_id": position["position_id"],
                "instrument_id": instrument["instrument_id"],
                "instrument_type": instrument["instrument_type"],
                "pricing_function_id": entry["pricing_function_id"],
                "assignment_method": "instrument_type_registry",
                "required_input_families": entry.get("required_input_families", []),
                "coverage_policy_id": entry.get("coverage_policy_id"),
                "approval_status": entry.get("approval_status"),
                "review_status": "review_required" if position["human_review_required"] else "not_required",
                "synthetic_data": True,
            }
        )
    return {
        "schema_version": "position_pricing_function_assignments.v1",
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "portfolio_snapshot_id": positions["portfolio_snapshot_id"],
        "valuation_date": positions["valuation_date"],
        "assignment_count": len(rows),
        "assignments": rows,
        "review_summary": _assignment_review_summary(rows),
    }


def build_valuation_input_coverage_map(
    *,
    positions: dict[str, Any],
    instruments: dict[str, Any],
    registry: dict[str, Any],
    market_state: dict[str, Any],
) -> dict[str, Any]:
    instrument_by_id = {instrument["instrument_id"]: instrument for instrument in instruments["instruments"]}
    rows = []
    for position in positions["positions"]:
        instrument = instrument_by_id[position["instrument_id"]]
        entry = select_pricing_function(position, instrument, market_state, registry)
        required = required_market_inputs(entry, position, instrument)
        coverage = check_market_input_coverage(required_market_inputs=required, market_state=market_state)
        status = _coverage_status_for_assignment(position, instrument, entry, coverage)
        rows.append(
            {
                "position_id": position["position_id"],
                "instrument_id": instrument["instrument_id"],
                "pricing_function_id": entry["pricing_function_id"],
                "required_market_inputs": required,
                "available_market_inputs": coverage["available_market_inputs"],
                "missing_market_inputs": coverage["missing_market_inputs"],
                "substitute_inputs": [],
                "coverage_status": status,
                "confidence": _coverage_confidence(position, status),
                "caveats": _coverage_caveats(status),
                "review_required": status == "review_required",
                "synthetic_data": True,
            }
        )
    return {
        "schema_version": "valuation_input_coverage_map.v1",
        "generated_at": GENERATED_AT,
        "methodology": "full_portfolio_revaluation",
        "synthetic_data": True,
        "market_state_id": market_state["market_state_id"],
        "valuation_date": market_state["valuation_date"],
        "coverage_rows": rows,
        "coverage_summary": _coverage_summary(rows),
    }


def build_valuation_coverage_manifest(fixtures: dict[str, Any], comparisons: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "valuation_coverage_manifest.v1",
        "generated_at": GENERATED_AT,
        "methodology": "full_portfolio_revaluation",
        "synthetic_data": True,
        "portfolio_snapshot_id": fixtures["position_catalog"]["portfolio_snapshot_id"],
        "valuation_date": fixtures["position_catalog"]["valuation_date"],
        "base_market_state_id": fixtures["base_market_state"]["market_state_id"],
        "scenario_market_state_ids": [fixtures["scenario_market_state"]["market_state_id"]],
        "artifact_paths": {
            name: f"data/simulation/revaluation/{filename}"
            for name, filename in {**INPUT_FILES, **OUTPUT_FILES}.items()
            if name != "revaluation_bundle_manifest"
        },
        "coverage_summary": comparisons["portfolio_summary"]["coverage_summary"],
        "approval_metadata": {
            "approval_status": "approved_for_synthetic_internal_skeleton",
            "approved_at": GENERATED_AT,
        },
        "caveats": [
            "Coverage manifest is internal and synthetic.",
            "Review-required records are not client-ready point impact claims.",
        ],
    }


def _market_inputs_for_positions(
    positions: list[dict[str, Any]],
    instrument_by_id: dict[str, dict[str, Any]],
    state_values: dict[str, float],
    base_or_scenario: str,
) -> dict[str, Any]:
    market_inputs: dict[str, Any] = {
        "equity_prices": {},
        "fund_prices": {},
        "money_market_navs": {},
        "bond_price_scalars": {},
        "cash_scalars": {"USD": _input("cash_scalars:USD", 1.0, "scalar")},
        "fx_rates": {"USD": _input("fx_rates:USD", 1.0, "rate_to_usd")},
        "commodity_prices": {},
        "crypto_prices": {},
        "private_marks": {},
        "review_policies": {
            "fallback_review_required_v1": _input("review_policies:fallback_review_required_v1", 1.0, "policy"),
        },
    }
    for position in positions:
        instrument = instrument_by_id[position["instrument_id"]]
        instrument_type = instrument["instrument_type"]
        amount = _position_amount_from_catalog(position)
        current_mark = float(position["current_mark"])
        if instrument_type == "public_equity":
            price = _safe_price(current_mark, amount) * _factor_for("underlying_price", state_values, base_or_scenario)
            market_inputs["equity_prices"][instrument["instrument_id"]] = _input(
                f"equity_prices:{instrument['instrument_id']}",
                price,
                "price",
            )
        elif instrument_type == "etf":
            price = _safe_price(current_mark, amount) * _factor_for("etf_price", state_values, base_or_scenario)
            market_inputs["fund_prices"][instrument["instrument_id"]] = _input(
                f"fund_prices:{instrument['instrument_id']}",
                price,
                "price",
            )
        elif instrument_type == "money_market":
            nav = _safe_price(current_mark, amount) * _factor_for("money_market_nav", state_values, base_or_scenario)
            market_inputs["money_market_navs"][instrument["instrument_id"]] = _input(
                f"money_market_navs:{instrument['instrument_id']}",
                nav,
                "nav",
            )
        elif instrument_type == "fixed_income":
            base_price = _safe_divide(current_mark, amount) * 100.0
            price_per_100 = base_price * _factor_for("bond_price_proxy", state_values, base_or_scenario)
            market_inputs["bond_price_scalars"][instrument["instrument_id"]] = _input(
                f"bond_price_scalars:{instrument['instrument_id']}",
                price_per_100,
                "price_per_100",
            )
        elif instrument_type == "commodity":
            price = _safe_price(current_mark, amount) * _factor_for("commodity_price", state_values, base_or_scenario)
            market_inputs["commodity_prices"][instrument["instrument_id"]] = _input(
                f"commodity_prices:{instrument['instrument_id']}",
                price,
                "price",
            )
        elif instrument_type == "crypto":
            price = _safe_price(current_mark, amount) * _factor_for("crypto_price", state_values, base_or_scenario)
            market_inputs["crypto_prices"][instrument["instrument_id"]] = _input(
                f"crypto_prices:{instrument['instrument_id']}",
                price,
                "price",
            )
        elif instrument_type in PRIVATE_OR_OPAQUE_TYPES or instrument_type == "option_like":
            market_inputs["private_marks"][instrument["instrument_id"]] = _input(
                f"private_marks:{instrument['instrument_id']}",
                current_mark,
                "mark",
            )
    return market_inputs


def _state_variable_values(scenario_source: dict[str, Any] | None) -> dict[str, float]:
    base_values = {
        "ai_infrastructure_proxy": 100.0,
        "bond_price_proxy": 100.0,
        "cash_treatment": 1.0,
        "commodity_price": 100.0,
        "credit_spread_proxy": 100.0,
        "crypto_price": 100.0,
        "duration_bucket_price": 100.0,
        "energy_price_proxy": 100.0,
        "etf_price": 100.0,
        "fx_rate": 1.0,
        "human_review_flag": 1.0,
        "liquidity_discount_proxy": 0.0,
        "manager_composite_proxy": 100.0,
        "manager_mark": 100.0,
        "money_market_nav": 1.0,
        "optional_lookthrough_proxy": 100.0,
        "private_equity_proxy": 100.0,
        "private_mark": 100.0,
        "rate_proxy": 0.035,
        "real_asset_proxy": 100.0,
        "time_to_maturity": 0.5,
        "underlying_price": 100.0,
        "volatility_proxy": 20.0,
    }
    if scenario_source is None:
        return base_values
    values = dict(base_values)
    for row in scenario_source.get("expanded_state_values", []):
        values[row["state_variable_id"]] = float(row["value"])
    return values


def _scenario_by_id(payload: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    for scenario in payload.get("scenarios", []):
        if scenario.get("scenario_id") == scenario_id:
            return scenario
    raise ValueError(f"Scenario not found: {scenario_id}")


def _pricing_entry(
    pricing_function_id: str,
    instrument_types: list[str],
    required_input_families: list[str],
    coverage_policy_id: str,
    *,
    allows_explicit_review_treatment: bool = False,
) -> dict[str, Any]:
    return {
        "pricing_function_id": pricing_function_id,
        "display_name": pricing_function_id.replace("_", " ").title(),
        "eligible_instrument_types": instrument_types,
        "required_input_families": required_input_families,
        "scenario_supported": True,
        "approval_status": "approved",
        "coverage_policy_id": coverage_policy_id,
        "allows_explicit_review_treatment": allows_explicit_review_treatment,
    }


def _instrument_terms(position: dict[str, Any]) -> dict[str, Any]:
    instrument_type = position["instrument_type"]
    terms: dict[str, Any] = {
        "synthetic_identifier": position.get("synthetic_identifier"),
        "source_valuation_method_hint": position.get("valuation_method_hint"),
        "source_required_market_state_variables": position.get("required_market_state_variables", []),
    }
    if instrument_type in {"public_equity", "etf", "money_market", "crypto"}:
        terms.update({"share_class": "synthetic_demo", "base_quantity_unit": "shares"})
    elif instrument_type == "fixed_income":
        terms.update(
            {
                "face_amount": float(position.get("notional") or position.get("current_reported_value") or 0.0),
                "coupon_rate": 0.04,
                "coupon_frequency": "semi_annual",
                "maturity_date": "2031-06-30",
                "day_count": "30_360",
            }
        )
    elif instrument_type == "cash":
        terms.update({"cash_currency": position.get("base_currency", "USD")})
    elif instrument_type in PRIVATE_OR_OPAQUE_TYPES:
        terms.update({"mark_policy": "approved_private_mark_policy_v1"})
    elif instrument_type == "option_like":
        terms.update({"review_policy": "fallback_review_required_v1"})
    return terms


def _lifecycle_dates(instrument_type: str) -> dict[str, Any]:
    if instrument_type == "fixed_income":
        return {"issue_date": "2021-06-30", "maturity_date": "2031-06-30"}
    return {"as_of_date": "2026-06-30"}


def _payoff_description(instrument_type: str) -> str:
    return {
        "public_equity": "Common equity share valued with approved market-state price.",
        "etf": "Fund or ETF interest valued with approved market-state NAV or price.",
        "money_market": "Money-market units valued with approved NAV treatment.",
        "cash": "Cash balance valued at face-value treatment.",
        "fixed_income": "Synthetic fixed-income instrument valued with approved mark scalar and simple cash-flow output.",
        "fx_exposure": "Synthetic FX exposure valued through approved notional translation.",
        "commodity": "Synthetic commodity exposure valued with approved price input.",
        "crypto": "Synthetic crypto vehicle valued with approved price input.",
        "option_like": "Option-like instrument routed to explicit review-required treatment in v1.",
    }.get(instrument_type, "Private or opaque instrument valued with approved mark or review treatment.")


def _required_input_families_for_type(instrument_type: str) -> list[str]:
    return {
        "public_equity": ["equity_prices"],
        "etf": ["fund_prices"],
        "money_market": ["money_market_navs"],
        "cash": ["cash_scalars"],
        "fixed_income": ["bond_price_scalars"],
        "fx_exposure": ["fx_rates"],
        "commodity": ["commodity_prices"],
        "crypto": ["crypto_prices"],
        "option_like": ["review_policies"],
    }.get(instrument_type, ["private_marks"])


def _eligible_pricing_functions_for_type(instrument_type: str) -> list[str]:
    return {
        "public_equity": ["public_equity_price_lookup_v1"],
        "etf": ["fund_nav_lookup_v1"],
        "money_market": ["money_market_nav_lookup_v1"],
        "cash": ["cash_face_value_v1"],
        "fixed_income": ["bond_mark_scalar_v1"],
        "fx_exposure": ["fx_notional_translation_v1"],
        "commodity": ["commodity_price_lookup_v1"],
        "crypto": ["crypto_price_lookup_v1"],
        "option_like": ["review_required_treatment_v1"],
    }.get(instrument_type, ["approved_private_mark_policy_v1"])


def _coverage_policy_for_type(instrument_type: str, position: dict[str, Any]) -> str:
    if position.get("human_review_required") or instrument_type == "option_like":
        return "fallback_review_required_v1"
    return {
        "public_equity": "standard_public_equity_v1",
        "etf": "fund_or_etf_nav_v1",
        "money_market": "money_market_nav_v1",
        "cash": "cash_face_value_v1",
        "fixed_income": "synthetic_bond_policy_v1",
        "fx_exposure": "fx_translation_v1",
        "commodity": "commodity_price_lookup_v1",
        "crypto": "crypto_price_lookup_v1",
    }.get(instrument_type, "approved_private_mark_policy_v1")


def _position_amount(source: dict[str, Any], current_mark: float) -> float:
    quantity = source.get("quantity")
    if isinstance(quantity, (int, float)) and quantity > 0:
        return float(quantity)
    notional = source.get("notional")
    if isinstance(notional, (int, float)) and notional > 0:
        return float(notional)
    return current_mark


def _position_amount_from_catalog(position: dict[str, Any]) -> float:
    return float(position.get("amount") or position.get("current_mark") or 0.0)


def _safe_price(value: float, amount: float) -> float:
    if amount == 0:
        return 0.0
    return float(value) / float(amount)


def _factor_for(variable_id: str, state_values: dict[str, float], base_or_scenario: str) -> float:
    if base_or_scenario == "base":
        return 1.0
    denominator = 1.0 if variable_id in {"money_market_nav", "fx_rate"} else 100.0
    return float(state_values.get(variable_id, denominator)) / denominator


def _input(input_id: str, value: float, value_key: str) -> dict[str, Any]:
    return {
        "input_id": input_id,
        value_key: _round_money(value) if value_key not in {"nav", "rate_to_usd"} else round(float(value), 6),
        "source": "synthetic_revaluation_fixture",
        "confidence": "high",
        "synthetic_data": True,
    }


def _coverage_status_for_assignment(
    position: dict[str, Any],
    instrument: dict[str, Any],
    entry: dict[str, Any],
    coverage: dict[str, Any],
) -> str:
    if position.get("human_review_required") or entry["pricing_function_id"] == "review_required_treatment_v1":
        return "review_required"
    if instrument["instrument_type"] in PRIVATE_OR_OPAQUE_TYPES:
        return "held_at_mark_with_caveat"
    if not coverage["can_value"]:
        return "review_required"
    if entry["pricing_function_id"] == "bond_mark_scalar_v1":
        return "valued_with_approved_policy"
    return "valued"


def _coverage_confidence(position: dict[str, Any], status: str) -> str:
    if status == "review_required":
        return "review_required"
    if status == "held_at_mark_with_caveat":
        return "low"
    confidence = str(position.get("valuation_confidence") or "medium").lower()
    return confidence if confidence in {"high", "medium", "low"} else "review_required"


def _coverage_caveats(status: str) -> list[str]:
    return {
        "valued": ["Position was valued under the approved market state."],
        "valued_with_approved_policy": ["Position was valued with an approved synthetic policy because production valuation is out of scope."],
        "held_at_mark_with_caveat": ["Position was held at an approved mark treatment; scenario impact may understate true exposure."],
        "review_required": ["Position requires review before relying on scenario impact."],
    }.get(status, ["Position coverage status requires review."])


def _valuation_result_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total_value": _round_money(sum(float(result["value"]) for result in results)),
        "coverage_summary": _coverage_summary(results),
        "confidence_summary": _confidence_summary(results),
        "review_required_count": sum(1 for result in results if result["review_required"]),
    }


def _comparison_coverage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, dict[str, Any]] = {}
    for status in sorted(VALID_COVERAGE_STATUSES):
        matching = [row for row in rows if row["scenario_coverage_status"] == status]
        by_status[status] = {
            "count": len(matching),
            "base_value": _round_money(sum(float(row["base_value"]) for row in matching)),
            "scenario_value": _round_money(sum(float(row["scenario_value"]) for row in matching)),
        }
    return {"by_status": by_status}


def _comparison_confidence_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["confidence"] for row in rows)
    return {
        "by_confidence": {
            confidence: {
                "count": counts.get(confidence, 0),
                "base_value": _round_money(sum(float(row["base_value"]) for row in rows if row["confidence"] == confidence)),
            }
            for confidence in ("high", "medium", "low", "review_required")
        }
    }


def _coverage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["coverage_status"] for row in rows)
    return {
        "by_status": {
            status: counts.get(status, 0)
            for status in sorted(VALID_COVERAGE_STATUSES)
        },
        "review_required_count": counts.get("review_required", 0),
    }


def _confidence_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["confidence"] for row in rows)
    return {
        "by_confidence": {
            confidence: counts.get(confidence, 0)
            for confidence in ("high", "medium", "low", "review_required")
        }
    }


def _assignment_review_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["review_status"] for row in rows)
    return {
        "review_required": counts.get("review_required", 0),
        "not_required": counts.get("not_required", 0),
    }


def _combine_confidence(base_confidence: str, scenario_confidence: str) -> str:
    order = {"high": 0, "medium": 1, "low": 2, "review_required": 3}
    return max((base_confidence, scenario_confidence), key=lambda item: order.get(item, 3))


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _round_money(value: float) -> float:
    return round(float(value), 2)


def _round_percent(value: float) -> float:
    return round(float(value), 6)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
