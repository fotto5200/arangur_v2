"""Simplified deterministic daily valuation engine for simulation Surface 3."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .market_state import (
    DEFAULT_HISTORY_OUTPUT_PATH as DEFAULT_MARKET_STATE_HISTORY_PATH,
    DEFAULT_SCENARIO_OUTPUT_PATH as DEFAULT_SCENARIO_MARKET_STATES_PATH,
    load_synthetic_market_state_history,
)
from .position_universe import DEFAULT_OUTPUT_PATH as DEFAULT_POSITION_UNIVERSE_PATH
from .position_universe import load_synthetic_position_universe

GENERATOR_VERSION = "simplified_daily_valuation_engine.v1"
GENERATED_AT = "2026-06-30T00:00:00Z"

POSITION_HISTORY_SCHEMA_VERSION = "simulation_daily_position_valuation_history.v1"
PORTFOLIO_HISTORY_SCHEMA_VERSION = "simulation_daily_portfolio_valuation_history.v1"
VALUE_CHANGE_SCHEMA_VERSION = "simulation_value_change_package.v1"
SCENARIO_REVALUATION_SCHEMA_VERSION = "simulation_scenario_revaluation_results.v1"
SUMMARY_SCHEMA_VERSION = "simulation_simplified_valuation_summary.v1"

DEFAULT_DAILY_POSITION_OUTPUT_PATH = Path("data/simulation/daily_position_valuation_history.json")
DEFAULT_DAILY_PORTFOLIO_OUTPUT_PATH = Path("data/simulation/daily_portfolio_valuation_history.json")
DEFAULT_VALUE_CHANGE_OUTPUT_PATH = Path("data/simulation/value_change_package.json")
DEFAULT_SCENARIO_REVALUATION_OUTPUT_PATH = Path("data/simulation/scenario_revaluation_results.json")
DEFAULT_SUMMARY_OUTPUT_PATH = Path("data/simulation/simplified_valuation_summary.json")

REAL_DATA_MARKERS = {
    "bloomberg",
    "factset",
    "refinitiv",
    "morningstar direct",
    "plaid access token",
    "access_token",
    "api key",
    "private key",
    "client account number",
}

VALUATION_RULES: dict[str, list[tuple[str, float, str]]] = {
    "public_equity": [("underlying_price", 1.0, "index")],
    "etf": [("etf_price", 0.85, "index"), ("optional_lookthrough_proxy", 0.15, "index")],
    "fixed_income": [("bond_price_proxy", 0.65, "index"), ("duration_bucket_price", 0.35, "index")],
    "fx_exposure": [("fx_rate", 1.0, "index")],
    "commodity": [("commodity_price", 1.0, "index")],
    "crypto": [("crypto_price", 1.0, "index")],
    "private_equity": [("manager_mark", 0.55, "index"), ("private_equity_proxy", 0.45, "index")],
    "private_credit": [("manager_mark", 0.55, "index"), ("credit_spread_proxy", 0.45, "inverse_index")],
    "real_estate": [("manager_mark", 0.45, "index"), ("real_asset_proxy", 0.45, "index"), ("liquidity_discount_proxy", 0.10, "discount")],
    "data_center_investment": [("private_mark", 0.45, "index"), ("ai_infrastructure_proxy", 0.40, "index"), ("energy_price_proxy", 0.15, "energy_cost")],
    "cash": [("cash_treatment", 1.0, "cash")],
    "money_market": [("money_market_nav", 0.85, "index"), ("cash_treatment", 0.15, "cash")],
    "opaque_manager_level": [("manager_mark", 0.55, "index"), ("manager_composite_proxy", 0.35, "index"), ("human_review_flag", 0.10, "cash")],
}


def generate_daily_valuation_history(
    position_universe: dict[str, Any],
    market_state_history: dict[str, Any],
) -> dict[str, Any]:
    """Generate deterministic daily position, portfolio, and value-change outputs."""

    positions = sorted(position_universe["positions"], key=lambda row: row.get("sort_order", row["position_id"]))
    current_state_values = _state_values(market_state_history["current_market_state"]["expanded_state_values"])
    records_by_position: dict[str, dict[str, Any]] = {}
    position_valuations: list[dict[str, Any]] = []
    transactions_by_position_date = _transactions_by_position_date(position_universe.get("transactions", []))

    for market_record in market_state_history["history"]:
        valuation_date = market_record["date"]
        day_state_values = _state_values(market_record["expanded_state_values"])
        for position in positions:
            position_id = position["position_id"]
            prior = records_by_position.get(position_id)
            transaction_summary = _transaction_summary(transactions_by_position_date.get((position_id, valuation_date), []))
            valuation_result = _value_position(position, day_state_values, current_state_values)
            value = valuation_result["value"]
            prior_value = prior["value"] if prior is not None else value
            value_change = value - prior_value
            economic_change = (
                value_change
                - transaction_summary["transaction_cash_flow_on_date"]
                - transaction_summary["income_distribution_on_date"]
                - transaction_summary["fee_on_date"]
            )
            record = {
                "schema_version": "simulation_daily_position_valuation.v1",
                "valuation_date": valuation_date,
                "position_id": position_id,
                "instrument_id": position["instrument_id"],
                "manager_id": position["manager_id"],
                "account_id": position["account_id"],
                "sleeve_id": position.get("sleeve_id"),
                "instrument_type": position["instrument_type"],
                "asset_class": position["classifications"]["asset_class"],
                "themes": position.get("themes", []),
                "liquidity_bucket": position.get("liquidity_bucket"),
                "valuation_method": valuation_result["valuation_method"],
                "valuation_tier": valuation_result["valuation_tier"],
                "required_state_variables_used": valuation_result["required_state_variables_used"],
                "state_variable_values_used": valuation_result["state_variable_values_used"],
                "quantity_or_notional": _quantity_or_notional(position),
                "prior_value": _round_money(prior_value),
                "value": value,
                "value_change_from_prior_date": _round_money(value_change),
                "transaction_cash_flow_on_date": transaction_summary["transaction_cash_flow_on_date"],
                "transaction_quantity_delta_on_date": transaction_summary["transaction_quantity_delta_on_date"],
                "income_distribution_on_date": transaction_summary["income_distribution_on_date"],
                "fee_on_date": transaction_summary["fee_on_date"],
                "mark_update_amount_on_date": transaction_summary["mark_update_amount_on_date"],
                "transaction_count_on_date": transaction_summary["transaction_count_on_date"],
                "economic_value_change_excluding_flows": _round_money(economic_change),
                "confidence": valuation_result["confidence"],
                "position_valuation_confidence": position.get("valuation_confidence", "unknown"),
                "human_review_required": valuation_result["human_review_required"],
                "caveats": valuation_result["caveats"],
                "synthetic_data": True,
            }
            position_valuations.append(record)
            records_by_position[position_id] = record

    position_history = {
        "schema_version": POSITION_HISTORY_SCHEMA_VERSION,
        "valuation_history_id": f"daily_position_values_{position_universe['universe_id']}_{market_state_history['history_id']}",
        "generated_at": GENERATED_AT,
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "source": _source(position_universe, market_state_history),
        "start_date": market_state_history["start_date"],
        "end_date": market_state_history["end_date"],
        "date_count": market_state_history["date_count"],
        "position_count": len(positions),
        "position_valuation_count": len(position_valuations),
        "caveats": _valuation_caveats(),
        "position_valuations": position_valuations,
    }
    portfolio_history = build_daily_portfolio_valuation_history(position_universe, position_history)
    value_change_package = build_value_change_package(position_universe, position_history, portfolio_history)
    result = {
        "position_valuation_history": position_history,
        "portfolio_valuation_history": portfolio_history,
        "value_change_package": value_change_package,
    }
    result["validation"] = validate_daily_valuation_history(result, position_universe, market_state_history)
    return result


def build_daily_portfolio_valuation_history(
    position_universe: dict[str, Any],
    position_history: dict[str, Any],
) -> dict[str, Any]:
    """Aggregate daily position valuations to portfolio-level records."""

    records_by_date = _group_by(position_history["position_valuations"], "valuation_date")
    transaction_totals_by_date = _transactions_by_date(position_universe.get("transactions", []))
    daily_portfolio_valuations = []
    prior_total: float | None = None

    for valuation_date in sorted(records_by_date):
        records = records_by_date[valuation_date]
        total_value = sum(float(record["value"]) for record in records)
        transaction_summary = transaction_totals_by_date.get(valuation_date, _empty_transaction_summary())
        if prior_total is None:
            value_change = 0.0
            economic_change = 0.0
            prior_value = total_value
        else:
            prior_value = prior_total
            value_change = total_value - prior_total
            economic_change = (
                value_change
                - transaction_summary["transaction_flow_total"]
                - transaction_summary["income_distributions_total"]
                - transaction_summary["fees_total"]
            )
        confidence_summary = _confidence_summary(records)
        human_review_records = [record for record in records if record["human_review_required"]]
        daily_portfolio_valuations.append(
            {
                "schema_version": "simulation_daily_portfolio_valuation.v1",
                "valuation_date": valuation_date,
                "portfolio_id": position_universe["portfolio"]["portfolio_id"],
                "reporting_currency": position_universe.get("reporting_currency", "USD"),
                "prior_total_value": _round_money(prior_value),
                "total_value": _round_money(total_value),
                "value_change_from_prior_date": _round_money(value_change),
                "transaction_flow_total": transaction_summary["transaction_flow_total"],
                "income_distributions_total": transaction_summary["income_distributions_total"],
                "fees_total": transaction_summary["fees_total"],
                "mark_update_amount_total": transaction_summary["mark_update_amount_total"],
                "economic_value_change_total": _round_money(economic_change),
                "cash_value": _round_money(sum(float(record["value"]) for record in records if record["instrument_type"] in {"cash", "money_market"})),
                "human_review_value": _round_money(sum(float(record["value"]) for record in human_review_records)),
                "human_review_count": len(human_review_records),
                "value_by_manager": _aggregate_records(records, "manager_id"),
                "value_by_account": _aggregate_records(records, "account_id"),
                "value_by_sleeve": _aggregate_records(records, "sleeve_id"),
                "value_by_asset_class": _aggregate_records(records, "asset_class"),
                "value_by_theme": _aggregate_themes(records),
                "value_by_liquidity_bucket": _aggregate_records(records, "liquidity_bucket"),
                "confidence_summary": confidence_summary,
                "human_review_items": _human_review_items(human_review_records),
                "caveats": [
                    "Daily portfolio totals are simplified synthetic economic values.",
                    "Transactions are separated as flow annotations; this is not statement-grade accounting.",
                ],
                "synthetic_data": True,
            }
        )
        prior_total = total_value

    return {
        "schema_version": PORTFOLIO_HISTORY_SCHEMA_VERSION,
        "portfolio_valuation_history_id": f"daily_portfolio_values_{position_history['valuation_history_id']}",
        "generated_at": GENERATED_AT,
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "source": position_history["source"],
        "start_date": position_history["start_date"],
        "end_date": position_history["end_date"],
        "date_count": position_history["date_count"],
        "portfolio_valuation_count": len(daily_portfolio_valuations),
        "caveats": _valuation_caveats(),
        "daily_portfolio_valuations": daily_portfolio_valuations,
    }


def build_value_change_package(
    position_universe: dict[str, Any],
    position_history: dict[str, Any],
    portfolio_history: dict[str, Any],
) -> dict[str, Any]:
    """Build a period value-change package from generated daily valuations."""

    daily = portfolio_history["daily_portfolio_valuations"]
    start = daily[0]
    end = daily[-1]
    period_daily = daily[1:]
    opening_value = float(start["total_value"])
    closing_value = float(end["total_value"])
    flows = sum(float(row["transaction_flow_total"]) for row in period_daily)
    income = sum(float(row["income_distributions_total"]) for row in period_daily)
    fees = sum(float(row["fees_total"]) for row in period_daily)
    economic_change = closing_value - opening_value - flows - income - fees
    records_by_date = _group_by(position_history["position_valuations"], "valuation_date")
    start_positions = {record["position_id"]: record for record in records_by_date[start["valuation_date"]]}
    end_positions = {record["position_id"]: record for record in records_by_date[end["valuation_date"]]}
    transactions = [transaction for transaction in position_universe.get("transactions", []) if transaction.get("date") != start["valuation_date"]]

    position_changes = []
    for position in position_universe["positions"]:
        position_id = position["position_id"]
        start_record = start_positions[position_id]
        end_record = end_positions[position_id]
        transaction_summary = _transaction_summary(
            [transaction for transaction in transactions if transaction.get("position_id") == position_id]
        )
        value_change = float(end_record["value"]) - float(start_record["value"])
        position_changes.append(
            {
                "position_id": position_id,
                "display_name": position["display_name"],
                "manager_id": position["manager_id"],
                "asset_class": position["classifications"]["asset_class"],
                "opening_value": start_record["value"],
                "closing_value": end_record["value"],
                "value_change": _round_money(value_change),
                "transaction_flows": transaction_summary["transaction_cash_flow_on_date"],
                "income_distributions": transaction_summary["income_distribution_on_date"],
                "fees": transaction_summary["fee_on_date"],
                "economic_value_change": _round_money(
                    value_change
                    - transaction_summary["transaction_cash_flow_on_date"]
                    - transaction_summary["income_distribution_on_date"]
                    - transaction_summary["fee_on_date"]
                ),
                "valuation_tier": end_record["valuation_tier"],
                "confidence": end_record["confidence"],
                "human_review_required": end_record["human_review_required"],
                "synthetic_data": True,
            }
        )

    return {
        "schema_version": VALUE_CHANGE_SCHEMA_VERSION,
        "package_id": f"value_change_{position_history['valuation_history_id']}",
        "generated_at": GENERATED_AT,
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "source": position_history["source"],
        "portfolio_id": position_universe["portfolio"]["portfolio_id"],
        "start_date": start["valuation_date"],
        "end_date": end["valuation_date"],
        "reporting_currency": position_universe.get("reporting_currency", "USD"),
        "opening_value": _round_money(opening_value),
        "closing_value": _round_money(closing_value),
        "total_transactions_or_flows": _round_money(flows),
        "total_income_distributions": _round_money(income),
        "total_fees": _round_money(fees),
        "total_market_or_economic_change": _round_money(economic_change),
        "opening_date_flow_annotations": {
            "transaction_flow_total": start["transaction_flow_total"],
            "income_distributions_total": start["income_distributions_total"],
            "fees_total": start["fees_total"],
            "note": "Opening-date flows are recorded as annotations and excluded from period tie-out.",
        },
        "value_change_by_manager": _period_aggregate(position_changes, "manager_id"),
        "value_change_by_asset_class": _period_aggregate(position_changes, "asset_class"),
        "value_change_by_theme": _period_theme_aggregate(position_changes, position_universe["positions"]),
        "largest_positive_contributors": _largest_contributors(position_changes, reverse=True),
        "largest_negative_contributors": _largest_contributors(position_changes, reverse=False),
        "data_confidence_summary": end["confidence_summary"],
        "human_review_items": end["human_review_items"],
        "caveats": [
            "Synthetic simplified value-change package only.",
            "Opening-date flows are treated as setup annotations because Surface 1 uses current positions as the history baseline.",
            "The package separates flows from economic value movement but does not perform tax-lot, settlement, accrual, or performance accounting.",
        ],
    }


def generate_scenario_revaluations(
    position_universe: dict[str, Any],
    current_market_state: dict[str, Any],
    scenario_market_states: dict[str, Any] | list[dict[str, Any]],
) -> dict[str, Any]:
    """Revalue current positions under each deterministic scenario state."""

    scenarios = scenario_market_states["scenarios"] if isinstance(scenario_market_states, dict) else scenario_market_states
    base_state_values = _state_values(current_market_state["expanded_state_values"])
    positions = sorted(position_universe["positions"], key=lambda row: row.get("sort_order", row["position_id"]))
    base_values = {
        position["position_id"]: _value_position(position, base_state_values, base_state_values)
        for position in positions
    }
    base_total = sum(float(result["value"]) for result in base_values.values())
    scenario_results = []
    for scenario in scenarios:
        scenario_state_values = _state_values(scenario["expanded_state_values"])
        impacts = []
        for position in positions:
            base = base_values[position["position_id"]]
            scenario_value = _value_position(position, scenario_state_values, base_state_values)
            impact = scenario_value["value"] - base["value"]
            impacts.append(
                {
                    "position_id": position["position_id"],
                    "display_name": position["display_name"],
                    "instrument_id": position["instrument_id"],
                    "manager_id": position["manager_id"],
                    "asset_class": position["classifications"]["asset_class"],
                    "themes": position.get("themes", []),
                    "base_value": base["value"],
                    "scenario_value": scenario_value["value"],
                    "scenario_impact": _round_money(impact),
                    "scenario_impact_percent": _round_percent(_safe_divide(impact, base["value"])),
                    "valuation_tier": scenario_value["valuation_tier"],
                    "confidence": scenario_value["confidence"],
                    "human_review_required": scenario_value["human_review_required"],
                    "caveats": scenario_value["caveats"],
                    "synthetic_data": True,
                }
            )
        scenario_total = sum(float(row["scenario_value"]) for row in impacts)
        total_impact = scenario_total - base_total
        scenario_results.append(
            {
                "schema_version": "simulation_scenario_revaluation_result.v1",
                "scenario_id": scenario["scenario_id"],
                "scenario_state_id": scenario["scenario_state_id"],
                "display_name": scenario["display_name"],
                "scenario_date": scenario["scenario_date"],
                "horizon": scenario["horizon"],
                "base_market_state_id": scenario["base_market_state_id"],
                "base_total_value": _round_money(base_total),
                "scenario_total_value": _round_money(scenario_total),
                "total_scenario_impact": _round_money(total_impact),
                "total_scenario_impact_percent": _round_percent(_safe_divide(total_impact, base_total)),
                "position_impacts": impacts,
                "manager_impacts": _scenario_aggregate(impacts, "manager_id"),
                "asset_class_impacts": _scenario_aggregate(impacts, "asset_class"),
                "theme_impacts": _scenario_theme_aggregate(impacts),
                "confidence_summary": _scenario_confidence_summary(impacts),
                "human_review_items": _scenario_human_review_items(impacts),
                "scenario_completeness": scenario.get("completeness_summary", {}),
                "caveats": [
                    "Deterministic synthetic scenario revaluation, not a forecast.",
                    "Scenario results are simplified economic revaluations and are not connected to report generation in this batch.",
                ],
                "synthetic_data": True,
            }
        )

    return {
        "schema_version": SCENARIO_REVALUATION_SCHEMA_VERSION,
        "scenario_revaluation_id": f"scenario_revaluations_{position_universe['universe_id']}",
        "generated_at": GENERATED_AT,
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "portfolio_id": position_universe["portfolio"]["portfolio_id"],
        "base_market_state_id": current_market_state["market_state_id"],
        "base_state_date": current_market_state["state_date"],
        "scenario_count": len(scenario_results),
        "scenario_results": scenario_results,
        "caveats": [
            "Synthetic deterministic scenario revaluations only.",
            "No stochastic simulation, covariance Monte Carlo, UI update, or report generation is performed.",
        ],
    }


def write_daily_valuation_outputs(
    position_universe_path: str | Path = DEFAULT_POSITION_UNIVERSE_PATH,
    market_state_history_path: str | Path = DEFAULT_MARKET_STATE_HISTORY_PATH,
    scenario_market_states_path: str | Path = DEFAULT_SCENARIO_MARKET_STATES_PATH,
    daily_position_output_path: str | Path = DEFAULT_DAILY_POSITION_OUTPUT_PATH,
    daily_portfolio_output_path: str | Path = DEFAULT_DAILY_PORTFOLIO_OUTPUT_PATH,
    value_change_output_path: str | Path = DEFAULT_VALUE_CHANGE_OUTPUT_PATH,
    scenario_revaluation_output_path: str | Path = DEFAULT_SCENARIO_REVALUATION_OUTPUT_PATH,
    summary_output_path: str | Path = DEFAULT_SUMMARY_OUTPUT_PATH,
) -> dict[str, Any]:
    """Load Surface 1/2 fixtures, generate Surface 3 outputs, and write JSON files."""

    position_universe = load_synthetic_position_universe(position_universe_path)
    market_state_history = load_synthetic_market_state_history(market_state_history_path)
    scenario_market_states = _load_json(Path(scenario_market_states_path))
    generated = generate_daily_valuation_history(position_universe, market_state_history)
    scenario_revaluations = generate_scenario_revaluations(
        position_universe,
        market_state_history["current_market_state"],
        scenario_market_states,
    )
    generated["scenario_revaluation_results"] = scenario_revaluations
    generated["validation"] = validate_daily_valuation_history(generated, position_universe, market_state_history)

    position_history = generated["position_valuation_history"]
    portfolio_history = generated["portfolio_valuation_history"]
    value_change_package = generated["value_change_package"]
    summary = build_simplified_valuation_summary(
        position_history,
        portfolio_history,
        value_change_package,
        scenario_revaluations,
        generated["validation"],
    )
    position_history["validation"] = generated["validation"]
    portfolio_history["validation"] = generated["validation"]
    value_change_package["validation_status"] = generated["validation"]["status"]
    scenario_revaluations["validation_status"] = generated["validation"]["status"]

    _write_json(Path(daily_position_output_path), position_history)
    _write_json(Path(daily_portfolio_output_path), portfolio_history)
    _write_json(Path(value_change_output_path), value_change_package)
    _write_json(Path(scenario_revaluation_output_path), scenario_revaluations)
    _write_json(Path(summary_output_path), summary)
    generated["summary"] = summary
    return generated


def load_daily_valuation_history(path: str | Path = DEFAULT_DAILY_POSITION_OUTPUT_PATH) -> dict[str, Any]:
    """Load a daily position valuation history JSON file."""

    return _load_json(Path(path))


def build_simplified_valuation_summary(
    position_history: dict[str, Any],
    portfolio_history: dict[str, Any],
    value_change_package: dict[str, Any],
    scenario_revaluation_results: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact summary for generated valuation outputs."""

    current_portfolio = portfolio_history["daily_portfolio_valuations"][-1]
    value_change = value_change_package
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "start_date": position_history["start_date"],
        "end_date": position_history["end_date"],
        "date_count": position_history["date_count"],
        "position_count": position_history["position_count"],
        "position_valuation_count": position_history["position_valuation_count"],
        "portfolio_valuation_count": portfolio_history["portfolio_valuation_count"],
        "scenario_count": scenario_revaluation_results["scenario_count"],
        "total_current_portfolio_value": current_portfolio["total_value"],
        "human_review_value": current_portfolio["human_review_value"],
        "human_review_count": current_portfolio["human_review_count"],
        "confidence_summary": current_portfolio["confidence_summary"],
        "transaction_flow_summary": {
            "total_transactions_or_flows": value_change["total_transactions_or_flows"],
            "total_income_distributions": value_change["total_income_distributions"],
            "total_fees": value_change["total_fees"],
            "total_market_or_economic_change": value_change["total_market_or_economic_change"],
        },
        "largest_positive_contributors": value_change["largest_positive_contributors"],
        "largest_negative_contributors": value_change["largest_negative_contributors"],
        "validation_status": validation["status"],
        "caveat": "Synthetic simplified valuation fixture only; no UI or report generation output is produced.",
    }


def validate_daily_valuation_history(
    valuation_history: dict[str, Any],
    position_universe: dict[str, Any],
    market_state_history: dict[str, Any],
) -> dict[str, Any]:
    """Return structured validation results for Surface 3 valuation outputs."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    position_history = valuation_history.get("position_valuation_history", valuation_history)
    portfolio_history = valuation_history.get("portfolio_valuation_history", {})
    value_change_package = valuation_history.get("value_change_package", {})
    scenario_revaluations = valuation_history.get("scenario_revaluation_results", {})

    _require_fields(position_history, ["schema_version", "synthetic_data", "position_valuations"], "position_history", errors)
    if position_history.get("schema_version") != POSITION_HISTORY_SCHEMA_VERSION:
        _add_issue(errors, "SCHEMA_VERSION_MISMATCH", "position_history", "Unexpected position history schema")
    if position_history.get("synthetic_data") is not True:
        _add_issue(errors, "SYNTHETIC_FLAG_MISSING", "position_history", "position history synthetic_data must be true")

    positions = position_universe.get("positions", [])
    expected_dates = [record["date"] for record in market_state_history.get("history", [])]
    position_records = position_history.get("position_valuations", [])
    if not position_records:
        _add_issue(errors, "MISSING_POSITION_VALUATIONS", "position_valuations", "Daily position valuations are required")
    if len(position_records) != len(expected_dates) * len(positions):
        _add_issue(errors, "POSITION_VALUATION_COUNT_MISMATCH", "position_valuations", "Every position must be valued for every market-state date")

    required_positions = {position["position_id"] for position in positions}
    required_state_by_position = {position["position_id"]: set(position["required_market_state_variables"]) for position in positions}
    records_by_date = _group_by(position_records, "valuation_date")
    for valuation_date in expected_dates:
        day_records = records_by_date.get(valuation_date, [])
        position_ids = {record.get("position_id") for record in day_records}
        if position_ids != required_positions:
            _add_issue(errors, "DAILY_POSITION_COVERAGE_MISMATCH", valuation_date, "Each date must include every position")
        for record in day_records:
            _require_fields(
                record,
                [
                    "position_id",
                    "value",
                    "valuation_tier",
                    "required_state_variables_used",
                    "transaction_cash_flow_on_date",
                    "economic_value_change_excluding_flows",
                    "confidence",
                    "synthetic_data",
                ],
                f"position:{valuation_date}",
                errors,
            )
            if record.get("synthetic_data") is not True:
                _add_issue(errors, "POSITION_SYNTHETIC_FLAG_MISSING", str(record.get("position_id")), "Position valuation synthetic_data must be true")
            used = set(record.get("required_state_variables_used", []))
            missing = required_state_by_position.get(str(record.get("position_id")), set()) - used
            if missing and not record.get("human_review_required"):
                _add_issue(errors, "MISSING_REQUIRED_STATE_VARIABLE_USAGE", str(record.get("position_id")), f"Missing required state variables: {', '.join(sorted(missing))}")

    portfolio_records = portfolio_history.get("daily_portfolio_valuations", [])
    if len(portfolio_records) != len(expected_dates):
        _add_issue(errors, "PORTFOLIO_VALUATION_COUNT_MISMATCH", "portfolio_history", "Every market-state date must have one portfolio valuation")
    portfolio_by_date = {record.get("valuation_date"): record for record in portfolio_records}
    for valuation_date in expected_dates:
        portfolio_record = portfolio_by_date.get(valuation_date)
        if not portfolio_record:
            continue
        position_total = sum(float(record["value"]) for record in records_by_date.get(valuation_date, []))
        if not _approx_equal(position_total, float(portfolio_record.get("total_value", 0.0)), tolerance=0.10):
            _add_issue(errors, "PORTFOLIO_TOTAL_MISMATCH", valuation_date, "Portfolio total must equal sum of position values")
        for section in ["value_by_manager", "value_by_account", "value_by_sleeve", "value_by_asset_class", "value_by_theme", "value_by_liquidity_bucket"]:
            aggregate_total = sum(float(row["value"]) for row in portfolio_record.get(section, []))
            if not _approx_equal(aggregate_total, float(portfolio_record.get("total_value", 0.0)), tolerance=0.10):
                _add_issue(errors, "AGGREGATE_TOTAL_MISMATCH", f"{valuation_date}:{section}", "Aggregate values must tie to the portfolio total")

    if not value_change_package:
        _add_issue(errors, "MISSING_VALUE_CHANGE_PACKAGE", "value_change_package", "Value-change package is required")
    else:
        tie_value = (
            float(value_change_package.get("opening_value", 0.0))
            + float(value_change_package.get("total_transactions_or_flows", 0.0))
            + float(value_change_package.get("total_income_distributions", 0.0))
            + float(value_change_package.get("total_fees", 0.0))
            + float(value_change_package.get("total_market_or_economic_change", 0.0))
        )
        if not _approx_equal(tie_value, float(value_change_package.get("closing_value", 0.0)), tolerance=0.10):
            _add_issue(errors, "VALUE_CHANGE_TIE_OUT_FAILED", "value_change_package", "Opening + flows + income + fees + economic change must tie to closing")

    scenarios = scenario_revaluations.get("scenario_results", [])
    expected_scenarios = {scenario["scenario_id"] for scenario in market_state_history.get("scenario_market_states", [])}
    if scenario_revaluations and {scenario.get("scenario_id") for scenario in scenarios} != expected_scenarios:
        _add_issue(errors, "SCENARIO_COVERAGE_MISMATCH", "scenario_revaluation_results", "Scenario revaluations must exist for all scenario states")
    for scenario in scenarios:
        impact_total = sum(float(row["scenario_impact"]) for row in scenario.get("position_impacts", []))
        if not _approx_equal(impact_total, float(scenario.get("total_scenario_impact", 0.0)), tolerance=0.20):
            _add_issue(errors, "SCENARIO_IMPACT_TIE_OUT_FAILED", str(scenario.get("scenario_id")), "Scenario position impacts must tie to total scenario impact")

    _validate_no_real_data_markers(valuation_history, errors)
    _validate_no_report_generation_markers(valuation_history, errors)
    return {
        "status": "invalid" if errors else "valid",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "date_count": len(expected_dates),
            "position_count": len(positions),
            "position_valuation_count": len(position_records),
            "portfolio_valuation_count": len(portfolio_records),
            "scenario_count": len(scenarios),
        },
    }


def _value_position(
    position: dict[str, Any],
    state_values: dict[str, dict[str, Any]],
    reference_state_values: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    instrument_type = position["instrument_type"]
    if instrument_type == "option_like":
        components, multiplier, method = _option_components(position, state_values, reference_state_values)
    else:
        components, multiplier, method = _rule_components(
            VALUATION_RULES.get(instrument_type, [(state_variable, 1.0, "index") for state_variable in position["required_market_state_variables"]]),
            state_values,
            reference_state_values,
        )
    value = _round_money(max(0.0, _reference_value(position) * multiplier))
    state_variable_values_used = [_state_usage(row[0], state_values) for row in components if row[0] in state_values]
    treatment_types = {row.get("treatment_type") for row in state_variable_values_used}
    state_confidences = [row.get("confidence", "unknown") for row in state_variable_values_used]
    human_review_required = bool(position.get("human_review_required")) or "human_review" in treatment_types
    confidence = _overall_confidence(position.get("valuation_confidence", "unknown"), state_confidences, human_review_required)
    valuation_tier = _valuation_tier(position, method, treatment_types, human_review_required)
    caveats = _position_caveats(position, valuation_tier, state_variable_values_used)
    return {
        "value": value,
        "valuation_method": method,
        "valuation_tier": valuation_tier,
        "required_state_variables_used": [row["state_variable_id"] for row in state_variable_values_used],
        "state_variable_values_used": state_variable_values_used,
        "confidence": confidence,
        "human_review_required": human_review_required,
        "caveats": caveats,
    }


def _rule_components(
    rule: list[tuple[str, float, str]],
    state_values: dict[str, dict[str, Any]],
    reference_state_values: dict[str, dict[str, Any]],
) -> tuple[list[tuple[str, float, str]], float, str]:
    components = [component for component in rule if component[0] in state_values and component[0] in reference_state_values]
    if not components:
        return [], 1.0, "missing_state_fallback"
    total_weight = sum(weight for _, weight, _ in components)
    multiplier = 0.0
    methods = set()
    for state_variable_id, weight, mode in components:
        ratio = _state_ratio(state_variable_id, mode, state_values, reference_state_values)
        multiplier += ratio * (weight / total_weight)
        methods.add(mode)
    method = "cash_face_value" if methods == {"cash"} else "synthetic_state_proxy_blend"
    return components, _bounded(multiplier, 0.05, 3.00), method


def _option_components(
    position: dict[str, Any],
    state_values: dict[str, dict[str, Any]],
    reference_state_values: dict[str, dict[str, Any]],
) -> tuple[list[tuple[str, float, str]], float, str]:
    components = [
        ("underlying_price", 0.55, "index"),
        ("volatility_proxy", 0.25, "index"),
        ("rate_proxy", 0.10, "rate_delta"),
        ("time_to_maturity", 0.10, "index"),
    ]
    underlying_ratio = _state_ratio("underlying_price", "index", state_values, reference_state_values)
    volatility_ratio = _state_ratio("volatility_proxy", "index", state_values, reference_state_values)
    rate_delta = float(state_values["rate_proxy"]["value"]) - float(reference_state_values["rate_proxy"]["value"])
    time_ratio = _state_ratio("time_to_maturity", "index", state_values, reference_state_values)
    name = position.get("display_name", "").lower()
    equity_sensitivity = -0.45 if "put" in name or "downside" in name else 0.45
    multiplier = (
        1.0
        + equity_sensitivity * (underlying_ratio - 1.0)
        + 0.30 * (volatility_ratio - 1.0)
        - 1.25 * rate_delta
        + 0.10 * (time_ratio - 1.0)
    )
    return components, _bounded(multiplier, 0.15, 2.50), "simple_option_proxy_formula"


def _state_ratio(
    state_variable_id: str,
    mode: str,
    state_values: dict[str, dict[str, Any]],
    reference_state_values: dict[str, dict[str, Any]],
) -> float:
    value = float(state_values[state_variable_id]["value"])
    reference = float(reference_state_values[state_variable_id]["value"])
    if mode == "cash":
        return 1.0
    if mode == "inverse_index":
        return _bounded(_safe_divide(reference, value, default=1.0), 0.20, 2.00)
    if mode == "discount":
        return _bounded(_safe_divide(1.0 - value, 1.0 - reference, default=1.0), 0.50, 1.25)
    if mode == "energy_cost":
        return _bounded(1.0 - 0.35 * (_safe_divide(value, reference, default=1.0) - 1.0), 0.70, 1.25)
    if mode == "rate_delta":
        return _bounded(1.0 - 2.0 * (value - reference), 0.50, 1.50)
    return _bounded(_safe_divide(value, reference, default=1.0), 0.05, 3.00)


def _state_usage(state_variable_id: str, state_values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    row = state_values[state_variable_id]
    return {
        "state_variable_id": state_variable_id,
        "value": row["value"],
        "value_type": row["value_type"],
        "unit": row["unit"],
        "confidence": row["confidence"],
        "treatment_type": row["treatment_type"],
        "proxy_rule": row.get("proxy_rule"),
    }


def _valuation_tier(
    position: dict[str, Any],
    method: str,
    treatment_types: set[str | None],
    human_review_required: bool,
) -> str:
    if human_review_required:
        return "human_review_required"
    if position["instrument_type"] in {"cash", "money_market"}:
        return "cash_face_value"
    if method == "simple_option_proxy_formula" or position["valuation_method_hint"] == "simple_option_model":
        return "simple_model_formula"
    if "stale_mark" in treatment_types or position["instrument_type"] in {"private_equity", "private_credit", "real_estate", "data_center_investment", "opaque_manager_level"}:
        return "stale_or_manager_mark"
    if treatment_types.issubset({"direct", "cash_treatment"}):
        return "direct_price_or_mark"
    return "proxy_valuation"


def _overall_confidence(position_confidence: str, state_confidences: list[str], human_review_required: bool) -> str:
    order = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
    values = [order.get(position_confidence, 0)] + [order.get(value, 0) for value in state_confidences]
    score = min(values) if values else 0
    if human_review_required:
        score = min(score, 1)
    for confidence, rank in order.items():
        if rank == score:
            return confidence
    return "unknown"


def _position_caveats(
    position: dict[str, Any],
    valuation_tier: str,
    state_variable_values_used: list[dict[str, Any]],
) -> list[str]:
    caveats = [
        "Simplified synthetic economic valuation; not statement-grade accounting.",
        "Current position quantity/notional is held static across history while transactions are recorded separately as flow annotations.",
    ]
    if valuation_tier == "human_review_required":
        caveats.append("Position is explicitly flagged for human review before relying on valuation interpretation.")
    if valuation_tier == "stale_or_manager_mark":
        caveats.append("Valuation uses a stale, private, or manager-level mark/proxy treatment.")
    if valuation_tier == "simple_model_formula":
        caveats.append("Option-like exposure uses a simple synthetic proxy formula, not a full option-pricing model.")
    if any(row["confidence"] == "low" for row in state_variable_values_used):
        caveats.append("At least one market-state input has low synthetic confidence.")
    return caveats


def _reference_value(position: dict[str, Any]) -> float:
    return float(position.get("current_reported_value") or position.get("initial_reference_value") or position.get("notional") or 0.0)


def _quantity_or_notional(position: dict[str, Any]) -> dict[str, Any]:
    return {
        "quantity": position.get("quantity"),
        "quantity_unit": position.get("quantity_unit"),
        "notional": position.get("notional"),
        "reference_value": _round_money(_reference_value(position)),
    }


def _transactions_by_position_date(transactions: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for transaction in transactions:
        position_id = transaction.get("position_id")
        if position_id:
            grouped[(position_id, transaction["date"])].append(transaction)
    return grouped


def _transactions_by_date(transactions: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for transaction in transactions:
        grouped[transaction["date"]].append(transaction)
    return {date_value: _portfolio_transaction_summary(rows) for date_value, rows in grouped.items()}


def _transaction_summary(transactions: list[dict[str, Any]]) -> dict[str, float]:
    summary = {
        "transaction_cash_flow_on_date": 0.0,
        "transaction_quantity_delta_on_date": 0.0,
        "income_distribution_on_date": 0.0,
        "fee_on_date": 0.0,
        "mark_update_amount_on_date": 0.0,
        "transaction_count_on_date": float(len(transactions)),
    }
    for transaction in transactions:
        transaction_type = transaction.get("transaction_type")
        cash_amount = float(transaction.get("cash_amount") or 0.0)
        quantity_delta = float(transaction.get("quantity_delta") or 0.0)
        notional_delta = float(transaction.get("notional_delta") or 0.0)
        if transaction_type in {"buy", "sell", "contribution", "withdrawal"}:
            summary["transaction_cash_flow_on_date"] += cash_amount
            summary["transaction_quantity_delta_on_date"] += quantity_delta
        elif transaction_type in {"income", "distribution"}:
            summary["income_distribution_on_date"] += cash_amount
        elif transaction_type == "fee":
            summary["fee_on_date"] += cash_amount
        elif transaction_type == "mark_update":
            summary["mark_update_amount_on_date"] += notional_delta
    return {key: _round_money(value) if key != "transaction_count_on_date" else int(value) for key, value in summary.items()}


def _portfolio_transaction_summary(transactions: list[dict[str, Any]]) -> dict[str, float]:
    summary = _empty_transaction_summary()
    for transaction in transactions:
        transaction_type = transaction.get("transaction_type")
        cash_amount = float(transaction.get("cash_amount") or 0.0)
        notional_delta = float(transaction.get("notional_delta") or 0.0)
        if transaction_type in {"buy", "sell", "contribution", "withdrawal"}:
            summary["transaction_flow_total"] += cash_amount
        elif transaction_type in {"income", "distribution"}:
            summary["income_distributions_total"] += cash_amount
        elif transaction_type == "fee":
            summary["fees_total"] += cash_amount
        elif transaction_type == "mark_update":
            summary["mark_update_amount_total"] += notional_delta
    return {key: _round_money(value) for key, value in summary.items()}


def _empty_transaction_summary() -> dict[str, float]:
    return {
        "transaction_flow_total": 0.0,
        "income_distributions_total": 0.0,
        "fees_total": 0.0,
        "mark_update_amount_total": 0.0,
    }


def _aggregate_records(records: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    totals: dict[str, float] = defaultdict(float)
    total = sum(float(record["value"]) for record in records)
    for record in records:
        totals[str(record.get(key) or "unassigned")] += float(record["value"])
    return [
        {
            "id": record_id,
            "value": _round_money(value),
            "percent_of_total": _round_percent(_safe_divide(value, total)),
            "synthetic_data": True,
        }
        for record_id, value in sorted(totals.items())
    ]


def _aggregate_themes(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[str, float] = defaultdict(float)
    total = sum(float(record["value"]) for record in records)
    for record in records:
        themes = record.get("themes") or ["unassigned"]
        allocation = float(record["value"]) / len(themes)
        for theme in themes:
            totals[theme] += allocation
    return [
        {
            "id": theme,
            "value": _round_money(value),
            "percent_of_total": _round_percent(_safe_divide(value, total)),
            "allocation_method": "equal_split_across_position_themes",
            "synthetic_data": True,
        }
        for theme, value in sorted(totals.items())
    ]


def _period_aggregate(position_changes: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in position_changes:
        bucket = buckets[str(row.get(key) or "unassigned")]
        bucket["opening_value"] += float(row["opening_value"])
        bucket["closing_value"] += float(row["closing_value"])
        bucket["value_change"] += float(row["value_change"])
        bucket["transaction_flows"] += float(row["transaction_flows"])
        bucket["income_distributions"] += float(row["income_distributions"])
        bucket["fees"] += float(row["fees"])
        bucket["economic_value_change"] += float(row["economic_value_change"])
    return [_period_bucket(row_id, values) for row_id, values in sorted(buckets.items())]


def _period_theme_aggregate(position_changes: list[dict[str, Any]], positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    themes_by_position = {position["position_id"]: position.get("themes", []) or ["unassigned"] for position in positions}
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in position_changes:
        themes = themes_by_position[row["position_id"]]
        for theme in themes:
            bucket = buckets[theme]
            divisor = float(len(themes))
            for field in ["opening_value", "closing_value", "value_change", "transaction_flows", "income_distributions", "fees", "economic_value_change"]:
                bucket[field] += float(row[field]) / divisor
    return [_period_bucket(theme, values, allocation_method="equal_split_across_position_themes") for theme, values in sorted(buckets.items())]


def _period_bucket(row_id: str, values: dict[str, float], allocation_method: str | None = None) -> dict[str, Any]:
    bucket = {
        "id": row_id,
        "opening_value": _round_money(values["opening_value"]),
        "closing_value": _round_money(values["closing_value"]),
        "value_change": _round_money(values["value_change"]),
        "transaction_flows": _round_money(values["transaction_flows"]),
        "income_distributions": _round_money(values["income_distributions"]),
        "fees": _round_money(values["fees"]),
        "economic_value_change": _round_money(values["economic_value_change"]),
        "synthetic_data": True,
    }
    if allocation_method:
        bucket["allocation_method"] = allocation_method
    return bucket


def _largest_contributors(position_changes: list[dict[str, Any]], reverse: bool) -> list[dict[str, Any]]:
    if reverse:
        candidates = [row for row in position_changes if float(row["economic_value_change"]) > 0.0]
    else:
        candidates = [row for row in position_changes if float(row["economic_value_change"]) < 0.0]
    rows = sorted(candidates, key=lambda row: float(row["economic_value_change"]), reverse=reverse)[:8]
    return [
        {
            "position_id": row["position_id"],
            "display_name": row["display_name"],
            "manager_id": row["manager_id"],
            "asset_class": row["asset_class"],
            "economic_value_change": row["economic_value_change"],
            "closing_value": row["closing_value"],
            "valuation_tier": row["valuation_tier"],
            "confidence": row["confidence"],
            "synthetic_data": True,
        }
        for row in rows
    ]


def _scenario_aggregate(impacts: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    total_base = sum(float(row["base_value"]) for row in impacts)
    for row in impacts:
        bucket = buckets[str(row.get(key) or "unassigned")]
        bucket["base_value"] += float(row["base_value"])
        bucket["scenario_value"] += float(row["scenario_value"])
        bucket["scenario_impact"] += float(row["scenario_impact"])
    return [
        {
            "id": row_id,
            "base_value": _round_money(values["base_value"]),
            "scenario_value": _round_money(values["scenario_value"]),
            "scenario_impact": _round_money(values["scenario_impact"]),
            "scenario_impact_percent": _round_percent(_safe_divide(values["scenario_impact"], values["base_value"])),
            "percent_of_base_total": _round_percent(_safe_divide(values["base_value"], total_base)),
            "synthetic_data": True,
        }
        for row_id, values in sorted(buckets.items())
    ]


def _scenario_theme_aggregate(impacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    total_base = sum(float(row["base_value"]) for row in impacts)
    for row in impacts:
        themes = row.get("themes") or ["unassigned"]
        for theme in themes:
            divisor = float(len(themes))
            buckets[theme]["base_value"] += float(row["base_value"]) / divisor
            buckets[theme]["scenario_value"] += float(row["scenario_value"]) / divisor
            buckets[theme]["scenario_impact"] += float(row["scenario_impact"]) / divisor
    return [
        {
            "id": theme,
            "base_value": _round_money(values["base_value"]),
            "scenario_value": _round_money(values["scenario_value"]),
            "scenario_impact": _round_money(values["scenario_impact"]),
            "scenario_impact_percent": _round_percent(_safe_divide(values["scenario_impact"], values["base_value"])),
            "percent_of_base_total": _round_percent(_safe_divide(values["base_value"], total_base)),
            "allocation_method": "equal_split_across_position_themes",
            "synthetic_data": True,
        }
        for theme, values in sorted(buckets.items())
    ]


def _confidence_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_confidence: dict[str, dict[str, float]] = defaultdict(lambda: {"count": 0.0, "value": 0.0})
    by_tier: dict[str, dict[str, float]] = defaultdict(lambda: {"count": 0.0, "value": 0.0})
    total = sum(float(record["value"]) for record in records)
    for record in records:
        confidence_bucket = by_confidence[record["confidence"]]
        confidence_bucket["count"] += 1
        confidence_bucket["value"] += float(record["value"])
        tier_bucket = by_tier[record["valuation_tier"]]
        tier_bucket["count"] += 1
        tier_bucket["value"] += float(record["value"])
    return {
        "by_confidence": _bucket_summary(by_confidence, total),
        "by_valuation_tier": _bucket_summary(by_tier, total),
        "human_review_count": sum(1 for record in records if record["human_review_required"]),
        "human_review_value": _round_money(sum(float(record["value"]) for record in records if record["human_review_required"])),
    }


def _scenario_confidence_summary(impacts: list[dict[str, Any]]) -> dict[str, Any]:
    records = [
        {
            "value": row["scenario_value"],
            "confidence": row["confidence"],
            "valuation_tier": row["valuation_tier"],
            "human_review_required": row["human_review_required"],
        }
        for row in impacts
    ]
    return _confidence_summary(records)


def _bucket_summary(buckets: dict[str, dict[str, float]], total: float) -> list[dict[str, Any]]:
    return [
        {
            "id": bucket_id,
            "count": int(values["count"]),
            "value": _round_money(values["value"]),
            "percent_of_total": _round_percent(_safe_divide(values["value"], total)),
            "synthetic_data": True,
        }
        for bucket_id, values in sorted(buckets.items())
    ]


def _human_review_items(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "position_id": record["position_id"],
            "instrument_id": record["instrument_id"],
            "manager_id": record["manager_id"],
            "value": record["value"],
            "valuation_tier": record["valuation_tier"],
            "confidence": record["confidence"],
            "reason": "Human-review or low-confidence valuation treatment in simplified synthetic valuation.",
            "synthetic_data": True,
        }
        for record in records
    ]


def _scenario_human_review_items(impacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "position_id": row["position_id"],
            "manager_id": row["manager_id"],
            "scenario_value": row["scenario_value"],
            "scenario_impact": row["scenario_impact"],
            "valuation_tier": row["valuation_tier"],
            "confidence": row["confidence"],
            "reason": "Scenario revaluation includes human-review or low-confidence treatment.",
            "synthetic_data": True,
        }
        for row in impacts
        if row["human_review_required"]
    ]


def _state_values(expanded_state_values: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["state_variable_id"]: row for row in expanded_state_values}


def _source(position_universe: dict[str, Any], market_state_history: dict[str, Any]) -> dict[str, Any]:
    return {
        "generator": "arangur.simulation.simplified_daily_valuation_engine",
        "generator_version": GENERATOR_VERSION,
        "position_universe_id": position_universe["universe_id"],
        "position_universe_schema_version": position_universe["schema_version"],
        "market_state_history_id": market_state_history["history_id"],
        "market_state_schema_version": market_state_history["schema_version"],
        "is_synthetic": True,
    }


def _valuation_caveats() -> list[str]:
    return [
        "Synthetic simplified economic valuation only.",
        "No tax lots, settlement-date reconciliation, day-count accrual, production fixed-income accounting, or production private-asset accounting are implemented.",
        "No UI, report generation, live data, vendor data, external API calls, or client-specific source data are used.",
    ]


def _group_by(records: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record[key])].append(record)
    return dict(grouped)


def _require_fields(record: Any, fields: list[str], context: str, errors: list[dict[str, str]]) -> None:
    if not isinstance(record, dict):
        _add_issue(errors, "RECORD_NOT_OBJECT", context, "Record must be an object")
        return
    for field in fields:
        if field not in record:
            _add_issue(errors, "MISSING_FIELD", context, f"Missing required field: {field}")


def _validate_no_real_data_markers(value: Any, errors: list[dict[str, str]]) -> None:
    for path, text in _walk_strings(value):
        lowered = text.lower()
        for marker in REAL_DATA_MARKERS:
            if marker in lowered:
                _add_issue(errors, "REAL_DATA_MARKER_DETECTED", path, f"String contains prohibited marker: {marker}")


def _validate_no_report_generation_markers(value: Any, errors: list[dict[str, str]]) -> None:
    forbidden_keys = {"report_package", "report_artifacts", "report_links", "html_report", "markdown_report", "ui_route"}
    for path, key in _walk_keys(value):
        if key in forbidden_keys:
            _add_issue(errors, "REPORT_GENERATION_MARKER_DETECTED", path, f"Unexpected report-generation key: {key}")


def _walk_strings(value: Any, path: str = "valuation") -> list[tuple[str, str]]:
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


def _walk_keys(value: Any, path: str = "valuation") -> list[tuple[str, str]]:
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})


def _safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0.0:
        return default
    return numerator / denominator


def _bounded(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def _approx_equal(left: float, right: float, tolerance: float) -> bool:
    return abs(left - right) <= tolerance


def _round_money(value: float) -> float:
    return round(float(value), 2)


def _round_percent(value: float) -> float:
    return round(float(value), 6)
