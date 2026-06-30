"""Deterministic synthetic market/state-of-world generator."""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .position_universe import DEFAULT_OUTPUT_PATH as DEFAULT_POSITION_UNIVERSE_PATH
from .position_universe import load_synthetic_position_universe

DEFAULT_SEED = 20260701
GENERATOR_VERSION = "synthetic_market_state_generator.v1"
HISTORY_SCHEMA_VERSION = "simulation_market_state_history.v1"
SCENARIO_SCHEMA_VERSION = "simulation_scenario_market_states.v1"
SUMMARY_SCHEMA_VERSION = "simulation_market_state_summary.v1"
GENERATED_AT = "2026-06-30T00:00:00Z"
DEFAULT_HISTORY_OUTPUT_PATH = Path("data/simulation/synthetic_market_state_history.json")
DEFAULT_SUMMARY_OUTPUT_PATH = Path("data/simulation/synthetic_market_state_summary.json")
DEFAULT_SCENARIO_OUTPUT_PATH = Path("data/simulation/synthetic_scenario_market_states.json")

REAL_DATA_MARKERS = {
    "bloomberg",
    "factset",
    "refinitiv",
    "morningstar direct",
    "plaid access token",
    "access_token",
    "private key",
    "api key",
    "client account number",
}

FACTOR_MODEL = {
    "method": "standard-library factor shocks with idiosyncratic noise",
    "description": (
        "Core driver returns are generated from named common synthetic factors plus "
        "driver-specific idiosyncratic noise. This is a deterministic demo coherence "
        "model, not a production risk model."
    ),
    "factors": [
        {"factor_id": "risk_on", "daily_volatility": 0.009, "description": "Broad risk appetite."},
        {"factor_id": "tech_ai", "daily_volatility": 0.011, "description": "Growth, AI, and semiconductor risk."},
        {"factor_id": "rates_down", "daily_volatility": 0.004, "description": "Bond-price-positive rates factor."},
        {"factor_id": "energy_supply", "daily_volatility": 0.012, "description": "Energy and power bottleneck factor."},
        {"factor_id": "usd_strength", "daily_volatility": 0.005, "description": "Broad USD/FX strength factor."},
        {"factor_id": "vol_stress", "daily_volatility": 0.012, "description": "Volatility and market stress factor."},
        {"factor_id": "private_liquidity", "daily_volatility": 0.006, "description": "Private-market liquidity factor."},
        {"factor_id": "crypto_beta", "daily_volatility": 0.026, "description": "Crypto-specific risk factor."},
    ],
}

CORE_DRIVER_DEFINITIONS = [
    {
        "driver_id": "us_large_cap_equity",
        "display_name": "US Large-Cap Equity",
        "driver_type": "price_index",
        "base_value": 100.0,
        "volatility_assumption": 0.010,
        "description": "Synthetic broad US equity price-like index.",
        "relevant_themes": ["growth/value", "manager overlap"],
        "factor_loadings": {"risk_on": 0.75, "tech_ai": 0.15, "vol_stress": -0.25, "usd_strength": -0.05},
        "idiosyncratic_volatility": 0.003,
        "drift": 0.00015,
    },
    {
        "driver_id": "us_growth_tech_equity",
        "display_name": "US Growth / Technology Equity",
        "driver_type": "price_index",
        "base_value": 100.0,
        "volatility_assumption": 0.014,
        "description": "Synthetic growth and technology equity index.",
        "relevant_themes": ["AI infrastructure", "growth/value"],
        "factor_loadings": {"risk_on": 0.55, "tech_ai": 0.60, "vol_stress": -0.30, "rates_down": 0.10},
        "idiosyncratic_volatility": 0.004,
        "drift": 0.00018,
    },
    {
        "driver_id": "ai_infrastructure_semiconductor",
        "display_name": "AI Infrastructure / Semiconductor",
        "driver_type": "price_index",
        "base_value": 100.0,
        "volatility_assumption": 0.018,
        "description": "Synthetic AI compute, chip, and data-center infrastructure index.",
        "relevant_themes": ["AI infrastructure", "semiconductors", "data center power demand"],
        "factor_loadings": {"risk_on": 0.45, "tech_ai": 0.85, "vol_stress": -0.35, "energy_supply": -0.08},
        "idiosyncratic_volatility": 0.006,
        "drift": 0.00022,
    },
    {
        "driver_id": "energy_oil",
        "display_name": "Energy / Oil",
        "driver_type": "price_index",
        "base_value": 100.0,
        "volatility_assumption": 0.016,
        "description": "Synthetic energy and oil price-like index.",
        "relevant_themes": ["energy bottlenecks", "inflation sensitivity"],
        "factor_loadings": {"energy_supply": 0.82, "risk_on": 0.12, "usd_strength": -0.25, "vol_stress": 0.08},
        "idiosyncratic_volatility": 0.006,
        "drift": 0.00008,
    },
    {
        "driver_id": "bitcoin_crypto",
        "display_name": "Bitcoin / Crypto",
        "driver_type": "price_index",
        "base_value": 100.0,
        "volatility_assumption": 0.040,
        "description": "Synthetic crypto risk index.",
        "relevant_themes": ["crypto risk", "growth/value"],
        "factor_loadings": {"crypto_beta": 0.90, "risk_on": 0.35, "tech_ai": 0.12, "vol_stress": -0.18},
        "idiosyncratic_volatility": 0.014,
        "drift": 0.00025,
    },
    {
        "driver_id": "usd_fx_broad",
        "display_name": "Broad USD / FX",
        "driver_type": "fx_index",
        "base_value": 100.0,
        "volatility_assumption": 0.006,
        "description": "Synthetic broad USD strength index.",
        "relevant_themes": ["USD exposure"],
        "factor_loadings": {"usd_strength": 0.90, "risk_on": -0.10, "vol_stress": 0.15},
        "idiosyncratic_volatility": 0.002,
        "drift": 0.0,
    },
    {
        "driver_id": "short_duration_bond_price",
        "display_name": "Short-Duration Bond Price",
        "driver_type": "price_index",
        "base_value": 100.0,
        "volatility_assumption": 0.002,
        "description": "Synthetic short-duration bond price proxy.",
        "relevant_themes": ["rates sensitivity", "defensive ballast"],
        "factor_loadings": {"rates_down": 0.70, "risk_on": -0.05, "vol_stress": 0.08},
        "idiosyncratic_volatility": 0.001,
        "drift": 0.00003,
    },
    {
        "driver_id": "long_duration_bond_price",
        "display_name": "Long-Duration Bond Price",
        "driver_type": "price_index",
        "base_value": 100.0,
        "volatility_assumption": 0.007,
        "description": "Synthetic long-duration bond price proxy.",
        "relevant_themes": ["rates sensitivity"],
        "factor_loadings": {"rates_down": 0.95, "risk_on": -0.12, "vol_stress": 0.15},
        "idiosyncratic_volatility": 0.002,
        "drift": 0.00002,
    },
    {
        "driver_id": "credit_spread_proxy",
        "display_name": "Credit Spread Proxy",
        "driver_type": "spread_index",
        "base_value": 100.0,
        "volatility_assumption": 0.009,
        "description": "Synthetic credit spread stress proxy where higher values mean wider spreads.",
        "relevant_themes": ["rates sensitivity", "cash generation", "private-market liquidity"],
        "factor_loadings": {"risk_on": -0.35, "vol_stress": 0.60, "private_liquidity": -0.30},
        "idiosyncratic_volatility": 0.003,
        "drift": 0.0,
    },
    {
        "driver_id": "volatility_proxy",
        "display_name": "Volatility Proxy",
        "driver_type": "volatility_index",
        "base_value": 20.0,
        "volatility_assumption": 0.045,
        "description": "Synthetic volatility/stress proxy.",
        "relevant_themes": ["defensive ballast", "data confidence / valuation issue"],
        "factor_loadings": {"vol_stress": 0.90, "risk_on": -0.45, "tech_ai": -0.18},
        "idiosyncratic_volatility": 0.008,
        "drift": 0.0,
    },
    {
        "driver_id": "private_market_liquidity",
        "display_name": "Private-Market Liquidity",
        "driver_type": "liquidity_index",
        "base_value": 100.0,
        "volatility_assumption": 0.007,
        "description": "Synthetic private-market liquidity index where lower values mean tighter liquidity.",
        "relevant_themes": ["private-market liquidity", "opaque/private marks"],
        "factor_loadings": {"private_liquidity": 0.80, "risk_on": 0.25, "vol_stress": -0.35},
        "idiosyncratic_volatility": 0.002,
        "drift": -0.00002,
    },
    {
        "driver_id": "real_assets_infrastructure",
        "display_name": "Real Assets / Infrastructure",
        "driver_type": "price_index",
        "base_value": 100.0,
        "volatility_assumption": 0.009,
        "description": "Synthetic real assets and infrastructure proxy.",
        "relevant_themes": ["inflation sensitivity", "data center power demand", "energy bottlenecks"],
        "factor_loadings": {"energy_supply": 0.35, "rates_down": 0.18, "risk_on": 0.25, "private_liquidity": 0.14},
        "idiosyncratic_volatility": 0.003,
        "drift": 0.00008,
    },
]

INTENDED_RELATIONSHIPS = [
    ("us_growth_tech_equity", "ai_infrastructure_semiconductor", "positive", 0.65),
    ("us_large_cap_equity", "us_growth_tech_equity", "positive", 0.45),
    ("energy_oil", "ai_infrastructure_semiconductor", "weak", 0.05),
    ("long_duration_bond_price", "us_growth_tech_equity", "mixed_or_negative", -0.10),
    ("volatility_proxy", "us_large_cap_equity", "negative", -0.45),
    ("volatility_proxy", "ai_infrastructure_semiconductor", "negative", -0.45),
    ("private_market_liquidity", "credit_spread_proxy", "negative", -0.40),
    ("bitcoin_crypto", "us_growth_tech_equity", "positive", 0.35),
    ("usd_fx_broad", "energy_oil", "negative", -0.20),
]

SCENARIO_DEFINITIONS = [
    {
        "scenario_id": "ai_chip_selloff",
        "display_name": "AI / Chip Selloff",
        "description": "Synthetic stress to AI infrastructure, semiconductors, growth tech, and risk appetite.",
        "horizon": "3 months",
        "core_driver_shocks": {
            "ai_infrastructure_semiconductor": -0.24,
            "us_growth_tech_equity": -0.16,
            "us_large_cap_equity": -0.08,
            "volatility_proxy": 0.35,
            "private_market_liquidity": -0.06,
            "credit_spread_proxy": 0.08,
        },
    },
    {
        "scenario_id": "rate_shock",
        "display_name": "Rate Shock",
        "description": "Synthetic upward-rate shock reflected through bond-price proxies and credit stress.",
        "horizon": "3 months",
        "core_driver_shocks": {
            "short_duration_bond_price": -0.015,
            "long_duration_bond_price": -0.095,
            "credit_spread_proxy": 0.12,
            "us_growth_tech_equity": -0.06,
            "private_market_liquidity": -0.07,
            "volatility_proxy": 0.18,
        },
    },
    {
        "scenario_id": "energy_shock",
        "display_name": "Energy Shock",
        "description": "Synthetic energy and power bottleneck shock with inflation-sensitive pressure.",
        "horizon": "3 months",
        "core_driver_shocks": {
            "energy_oil": 0.28,
            "real_assets_infrastructure": 0.08,
            "ai_infrastructure_semiconductor": -0.07,
            "us_large_cap_equity": -0.03,
            "volatility_proxy": 0.16,
            "usd_fx_broad": 0.04,
        },
    },
    {
        "scenario_id": "private_market_liquidity_freeze",
        "display_name": "Private-Market Liquidity Freeze",
        "description": "Synthetic stress to private-market liquidity, credit spreads, stale marks, and opaque manager books.",
        "horizon": "3 months",
        "core_driver_shocks": {
            "private_market_liquidity": -0.22,
            "credit_spread_proxy": 0.22,
            "volatility_proxy": 0.28,
            "us_large_cap_equity": -0.06,
            "real_assets_infrastructure": -0.08,
            "long_duration_bond_price": 0.025,
        },
    },
    {
        "scenario_id": "taiwan_disruption",
        "display_name": "Taiwan Disruption",
        "description": "Synthetic geopolitical semiconductor and supply-chain stress scenario.",
        "horizon": "3 months",
        "core_driver_shocks": {
            "ai_infrastructure_semiconductor": -0.30,
            "us_growth_tech_equity": -0.14,
            "energy_oil": 0.10,
            "usd_fx_broad": 0.08,
            "volatility_proxy": 0.42,
            "private_market_liquidity": -0.10,
            "bitcoin_crypto": -0.16,
        },
    },
]


def generate_synthetic_market_state_history(
    position_universe: dict[str, Any],
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Generate deterministic synthetic market state history and scenario states."""

    rng = random.Random(seed)
    start_date = date.fromisoformat(position_universe["history_start_date"])
    end_date = date.fromisoformat(position_universe["history_end_date"])
    dates = _date_range(start_date, end_date)
    required_variables = _required_state_variables(position_universe)
    core_drivers = _core_driver_definitions()
    driver_history = _generate_core_driver_history(dates, rng)
    expanded_definitions = _expanded_state_variable_definitions(required_variables)
    proxy_mappings = _build_proxy_mappings(position_universe, expanded_definitions)
    history_records = _build_history_records(dates, driver_history, expanded_definitions, required_variables)
    covariance_recovery = _build_covariance_recovery_check(driver_history)
    current_snapshot = _build_current_market_state_snapshot(
        position_universe,
        history_records[-1],
        required_variables,
    )
    scenario_market_states = _build_scenario_market_states(
        position_universe,
        current_snapshot,
        expanded_definitions,
        required_variables,
    )
    missing_or_review_items = _missing_or_human_review_state_items(position_universe, proxy_mappings)

    history = {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "history_id": f"northstar_synthetic_market_state_history_seed_{seed}",
        "generated_at": GENERATED_AT,
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "start_date": dates[0].isoformat(),
        "end_date": dates[-1].isoformat(),
        "frequency": "daily_calendar",
        "date_count": len(dates),
        "reporting_currency": position_universe.get("reporting_currency", "USD"),
        "source": {
            "generator": "arangur.simulation.synthetic_market_state_generator",
            "generator_version": GENERATOR_VERSION,
            "seed": seed,
            "position_universe_id": position_universe["universe_id"],
            "position_universe_schema_version": position_universe["schema_version"],
            "is_synthetic": True,
        },
        "caveats": [
            "Synthetic demo/testing market state only.",
            "No vendor feeds, live prices, external APIs, real client data, or production valuation are used.",
            "State variables are inputs for later valuation; this file does not compute position or portfolio values.",
        ],
        "core_drivers": core_drivers,
        "factor_model": FACTOR_MODEL,
        "intended_relationships": _intended_relationship_records(),
        "required_state_variables": required_variables,
        "expanded_state_variable_definitions": list(expanded_definitions.values()),
        "proxy_mappings": proxy_mappings,
        "missing_or_human_review_state_items": missing_or_review_items,
        "history": history_records,
        "current_market_state": current_snapshot,
        "scenario_market_states": scenario_market_states,
        "covariance_recovery_check": covariance_recovery,
    }
    history["validation"] = validate_synthetic_market_state_history(history, position_universe)
    return history


def write_synthetic_market_state_history(
    path: str | Path = DEFAULT_HISTORY_OUTPUT_PATH,
    position_universe_path: str | Path = DEFAULT_POSITION_UNIVERSE_PATH,
    seed: int = DEFAULT_SEED,
    summary_path: str | Path | None = DEFAULT_SUMMARY_OUTPUT_PATH,
    scenario_path: str | Path | None = DEFAULT_SCENARIO_OUTPUT_PATH,
) -> dict[str, Any]:
    """Generate, validate, and write synthetic market-state history outputs."""

    position_universe = load_synthetic_position_universe(position_universe_path)
    history = generate_synthetic_market_state_history(position_universe, seed=seed)
    validation = history["validation"]
    if validation["status"] != "valid":
        messages = [f"{issue['code']}: {issue['record_id']} - {issue['message']}" for issue in validation["errors"]]
        raise ValueError("Synthetic market-state history validation failed:\n" + "\n".join(messages))

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(output_path, history)
    if summary_path is not None:
        summary_output_path = Path(summary_path)
        summary_output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(summary_output_path, build_synthetic_market_state_summary(history, position_universe))
    if scenario_path is not None:
        scenario_output_path = Path(scenario_path)
        scenario_output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(scenario_output_path, build_synthetic_scenario_market_state_set(history))
    return history


def load_synthetic_market_state_history(path: str | Path = DEFAULT_HISTORY_OUTPUT_PATH) -> dict[str, Any]:
    """Load a synthetic market-state history JSON file."""

    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {input_path}")
    return data


def validate_synthetic_market_state_history(
    history: dict[str, Any],
    position_universe: dict[str, Any],
) -> dict[str, Any]:
    """Return structured validation results for synthetic market-state history."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    _require_top_level(
        history,
        [
            "schema_version",
            "history_id",
            "generator_version",
            "synthetic_data",
            "start_date",
            "end_date",
            "source",
            "core_drivers",
            "required_state_variables",
            "expanded_state_variable_definitions",
            "proxy_mappings",
            "history",
            "current_market_state",
            "scenario_market_states",
            "covariance_recovery_check",
        ],
        errors,
    )
    if history.get("schema_version") != HISTORY_SCHEMA_VERSION:
        _add_issue(errors, "SCHEMA_VERSION_MISMATCH", "history", "Unexpected schema_version")
    if history.get("synthetic_data") is not True:
        _add_issue(errors, "SYNTHETIC_FLAG_MISSING", "history", "synthetic_data must be true")
    source = history.get("source", {})
    if not isinstance(source, dict) or source.get("is_synthetic") is not True:
        _add_issue(errors, "SOURCE_SYNTHETIC_FLAG_MISSING", "source", "source.is_synthetic must be true")

    core_drivers = _list(history.get("core_drivers"))
    history_records = _list(history.get("history"))
    scenarios = _list(history.get("scenario_market_states"))
    required_variables = set(_required_state_variables(position_universe))
    covered_variables = set(history.get("required_state_variables", []))
    if not core_drivers:
        _add_issue(errors, "MISSING_CORE_DRIVERS", "core_drivers", "At least one core driver is required")
    if not history_records:
        _add_issue(errors, "MISSING_HISTORY", "history", "At least one history record is required")
    if required_variables - covered_variables:
        _add_issue(
            errors,
            "MISSING_REQUIRED_STATE_VARIABLES",
            "required_state_variables",
            f"Missing required variables: {', '.join(sorted(required_variables - covered_variables))}",
        )

    core_driver_ids = {driver.get("driver_id") for driver in core_drivers}
    if len(core_driver_ids) != len(core_drivers):
        _add_issue(errors, "DUPLICATE_CORE_DRIVER", "core_drivers", "Core driver IDs must be unique")

    expected_dates = [day.isoformat() for day in _date_range(date.fromisoformat(position_universe["history_start_date"]), date.fromisoformat(position_universe["history_end_date"]))]
    actual_dates = [record.get("date") for record in history_records]
    if actual_dates != expected_dates:
        _add_issue(errors, "HISTORY_DATE_MISMATCH", "history", "History dates must match the position universe history window")

    for record in history_records:
        record_id = str(record.get("date"))
        _require_fields(record, ["date", "core_driver_values", "expanded_state_values", "generation_metadata"], f"history:{record_id}", errors)
        day_driver_ids = {row.get("driver_id") for row in _list(record.get("core_driver_values"))}
        if day_driver_ids != core_driver_ids:
            _add_issue(errors, "CORE_DRIVER_COVERAGE_MISMATCH", record_id, "Each date must contain every core driver")
        day_variables = {row.get("state_variable_id") for row in _list(record.get("expanded_state_values"))}
        if not required_variables.issubset(day_variables):
            _add_issue(errors, "STATE_VARIABLE_COVERAGE_MISMATCH", record_id, "Each date must cover every required state variable")
        for row in _list(record.get("expanded_state_values")):
            _require_fields(row, ["state_variable_id", "value", "value_type", "treatment_type", "confidence"], f"state:{record_id}", errors)

    for mapping in _list(history.get("proxy_mappings")):
        _require_fields(
            mapping,
            ["instrument_id", "required_state_variables", "state_variable_mappings", "synthetic_data"],
            f"mapping:{mapping.get('instrument_id')}",
            errors,
        )
        if mapping.get("synthetic_data") is not True:
            _add_issue(errors, "MAPPING_SYNTHETIC_FLAG_MISSING", str(mapping.get("instrument_id")), "mapping.synthetic_data must be true")

    required_scenarios = {scenario["scenario_id"] for scenario in SCENARIO_DEFINITIONS}
    scenario_ids = {scenario.get("scenario_id") for scenario in scenarios}
    if not required_scenarios.issubset(scenario_ids):
        _add_issue(errors, "MISSING_SCENARIOS", "scenario_market_states", "Required scenario market states are missing")
    for scenario in scenarios:
        scenario_id = str(scenario.get("scenario_id"))
        _require_fields(
            scenario,
            ["scenario_id", "display_name", "horizon", "core_driver_shocks", "expanded_state_values", "completeness_summary", "caveats", "synthetic_data"],
            f"scenario:{scenario_id}",
            errors,
        )
        scenario_variables = {row.get("state_variable_id") for row in _list(scenario.get("expanded_state_values"))}
        if not required_variables.issubset(scenario_variables):
            _add_issue(errors, "SCENARIO_VARIABLE_COVERAGE_MISMATCH", scenario_id, "Scenario must cover every required state variable")
        summary = scenario.get("completeness_summary", {})
        if not isinstance(summary, dict) or summary.get("required_variable_count") != len(required_variables):
            _add_issue(errors, "SCENARIO_COMPLETENESS_INVALID", scenario_id, "Scenario completeness summary is missing or inconsistent")
        if scenario.get("synthetic_data") is not True:
            _add_issue(errors, "SCENARIO_SYNTHETIC_FLAG_MISSING", scenario_id, "scenario.synthetic_data must be true")

    covariance = history.get("covariance_recovery_check", {})
    if not isinstance(covariance, dict) or not covariance.get("estimated_relationships"):
        _add_issue(errors, "MISSING_COVARIANCE_RECOVERY", "covariance_recovery_check", "Covariance recovery summary is required")
    _validate_no_real_data_markers(history, errors)
    _validate_no_valuation_outputs(history, errors)

    return {
        "status": "invalid" if errors else "valid",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "date_count": len(history_records),
            "core_driver_count": len(core_drivers),
            "expanded_state_variable_count": len(covered_variables),
            "scenario_count": len(scenarios),
            "human_review_state_count": _human_review_state_count(history_records[-1] if history_records else {}),
        },
    }


def build_synthetic_market_state_summary(
    history: dict[str, Any],
    position_universe: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact summary for generated synthetic market state."""

    current = history["current_market_state"]
    scenarios = history["scenario_market_states"]
    covariance = history["covariance_recovery_check"]
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "history_id": history["history_id"],
        "position_universe_id": position_universe["universe_id"],
        "generated_at": history["generated_at"],
        "generator_version": history["generator_version"],
        "synthetic_data": True,
        "start_date": history["start_date"],
        "end_date": history["end_date"],
        "date_count": history["date_count"],
        "core_driver_count": len(history["core_drivers"]),
        "expanded_state_variable_count": len(history["required_state_variables"]),
        "scenario_count": len(scenarios),
        "required_state_variables_covered": history["required_state_variables"],
        "human_review_state_count": _human_review_state_count(current),
        "covariance_recovery_summary": {
            "status": covariance["status"],
            "warning_count": covariance["warning_count"],
            "relationship_count": len(covariance["estimated_relationships"]),
        },
        "scenario_ids": [scenario["scenario_id"] for scenario in scenarios],
        "caveat": "Synthetic market/state-of-world fixture only; no valuation or reporting output is generated.",
        "validation_status": history.get("validation", {}).get("status"),
    }


def build_synthetic_scenario_market_state_set(history: dict[str, Any]) -> dict[str, Any]:
    """Build the separate scenario market-state output file."""

    return {
        "schema_version": SCENARIO_SCHEMA_VERSION,
        "scenario_set_id": f"scenario_set_{history['history_id']}",
        "generated_at": history["generated_at"],
        "generator_version": history["generator_version"],
        "synthetic_data": True,
        "base_market_state_id": history["current_market_state"]["market_state_id"],
        "base_state_date": history["current_market_state"]["state_date"],
        "required_state_variables": history["required_state_variables"],
        "scenarios": history["scenario_market_states"],
        "caveats": [
            "Synthetic deterministic scenario states only.",
            "Scenario states are assumption inputs, not forecasts or valuation outputs.",
        ],
    }


def _core_driver_definitions() -> list[dict[str, Any]]:
    rows = []
    for driver in CORE_DRIVER_DEFINITIONS:
        row = {key: value for key, value in driver.items() if key not in {"factor_loadings", "idiosyncratic_volatility", "drift"}}
        row["factor_loadings"] = dict(driver["factor_loadings"])
        row["idiosyncratic_volatility"] = driver["idiosyncratic_volatility"]
        row["synthetic_data"] = True
        rows.append(row)
    return rows


def _generate_core_driver_history(dates: list[date], rng: random.Random) -> list[dict[str, Any]]:
    values = {driver["driver_id"]: float(driver["base_value"]) for driver in CORE_DRIVER_DEFINITIONS}
    records: list[dict[str, Any]] = []
    factor_defs = {factor["factor_id"]: factor for factor in FACTOR_MODEL["factors"]}
    for index, day in enumerate(dates):
        if index == 0:
            returns = {driver["driver_id"]: 0.0 for driver in CORE_DRIVER_DEFINITIONS}
            factor_shocks = {factor_id: 0.0 for factor_id in factor_defs}
        else:
            factor_shocks = {
                factor_id: rng.gauss(0.0, factor["daily_volatility"])
                for factor_id, factor in factor_defs.items()
            }
            returns = {}
            for driver in CORE_DRIVER_DEFINITIONS:
                raw_return = driver.get("drift", 0.0)
                for factor_id, loading in driver["factor_loadings"].items():
                    raw_return += loading * factor_shocks[factor_id]
                raw_return += rng.gauss(0.0, driver["idiosyncratic_volatility"])
                returns[driver["driver_id"]] = raw_return
                values[driver["driver_id"]] = _next_driver_value(driver, values[driver["driver_id"]], raw_return)
        records.append(
            {
                "date": day.isoformat(),
                "factor_shocks": {factor_id: round(value, 8) for factor_id, value in sorted(factor_shocks.items())},
                "core_driver_values": [
                    {
                        "driver_id": driver["driver_id"],
                        "value": round(values[driver["driver_id"]], 6),
                        "daily_return": round(returns[driver["driver_id"]], 8),
                    }
                    for driver in CORE_DRIVER_DEFINITIONS
                ],
            }
        )
    return records


def _next_driver_value(driver: dict[str, Any], previous_value: float, daily_return: float) -> float:
    next_value = previous_value * (1.0 + daily_return)
    if driver["driver_type"] == "volatility_index":
        return min(85.0, max(8.0, next_value))
    if driver["driver_type"] == "spread_index":
        return min(180.0, max(45.0, next_value))
    if driver["driver_type"] == "liquidity_index":
        return min(130.0, max(55.0, next_value))
    return max(1.0, next_value)


def _expanded_state_variable_definitions(required_variables: list[str]) -> dict[str, dict[str, Any]]:
    all_definitions = {
        "underlying_price": _state_def("underlying_price", "Synthetic underlying public security price proxy.", "price_index", "direct", "high", ["us_large_cap_equity", "us_growth_tech_equity", "ai_infrastructure_semiconductor"], [0.45, 0.35, 0.20], 100.0),
        "etf_price": _state_def("etf_price", "Synthetic ETF price proxy.", "price_index", "direct", "high", ["us_large_cap_equity", "us_growth_tech_equity"], [0.70, 0.30], 100.0),
        "optional_lookthrough_proxy": _state_def("optional_lookthrough_proxy", "Synthetic ETF look-through proxy.", "index", "proxy", "medium", ["us_large_cap_equity", "ai_infrastructure_semiconductor", "real_assets_infrastructure"], [0.55, 0.25, 0.20], 100.0),
        "bond_price_proxy": _state_def("bond_price_proxy", "Synthetic bond price proxy.", "price_index", "proxy", "high", ["short_duration_bond_price", "long_duration_bond_price"], [0.45, 0.55], 100.0),
        "duration_bucket_price": _state_def("duration_bucket_price", "Synthetic duration-bucket price proxy.", "price_index", "proxy", "high", ["short_duration_bond_price", "long_duration_bond_price"], [0.30, 0.70], 100.0),
        "fx_rate": _state_def("fx_rate", "Synthetic broad FX rate proxy.", "fx_index", "direct", "medium", ["usd_fx_broad"], [1.0], 1.0),
        "commodity_price": _state_def("commodity_price", "Synthetic commodity price proxy.", "price_index", "direct", "medium", ["energy_oil", "real_assets_infrastructure"], [0.80, 0.20], 100.0),
        "crypto_price": _state_def("crypto_price", "Synthetic crypto price proxy.", "price_index", "direct", "medium", ["bitcoin_crypto"], [1.0], 100.0),
        "manager_mark": _state_def("manager_mark", "Synthetic manager mark input, updated in coarse stale buckets.", "mark_index", "stale_mark", "low", ["private_market_liquidity", "real_assets_infrastructure", "credit_spread_proxy"], [0.45, 0.35, -0.20], 100.0),
        "private_equity_proxy": _state_def("private_equity_proxy", "Synthetic private equity proxy.", "index", "proxy", "medium", ["private_market_liquidity", "us_growth_tech_equity", "us_large_cap_equity"], [0.45, 0.35, 0.20], 100.0),
        "credit_spread_proxy": _state_def("credit_spread_proxy", "Synthetic credit spread proxy.", "spread_index", "proxy", "medium", ["credit_spread_proxy"], [1.0], 100.0),
        "real_asset_proxy": _state_def("real_asset_proxy", "Synthetic real asset proxy.", "index", "proxy", "medium", ["real_assets_infrastructure", "energy_oil", "long_duration_bond_price"], [0.60, 0.25, 0.15], 100.0),
        "liquidity_discount_proxy": _state_def("liquidity_discount_proxy", "Synthetic liquidity discount model input.", "discount_percent", "model_input", "medium", ["private_market_liquidity", "volatility_proxy"], [-0.65, 0.35], 0.10),
        "ai_infrastructure_proxy": _state_def("ai_infrastructure_proxy", "Synthetic AI infrastructure proxy.", "index", "proxy", "medium", ["ai_infrastructure_semiconductor", "us_growth_tech_equity", "real_assets_infrastructure"], [0.65, 0.25, 0.10], 100.0),
        "energy_price_proxy": _state_def("energy_price_proxy", "Synthetic energy price proxy.", "price_index", "proxy", "medium", ["energy_oil"], [1.0], 100.0),
        "private_mark": _state_def("private_mark", "Synthetic stale private mark input.", "mark_index", "stale_mark", "low", ["private_market_liquidity", "real_assets_infrastructure"], [0.50, 0.50], 100.0),
        "volatility_proxy": _state_def("volatility_proxy", "Synthetic volatility proxy.", "volatility_index", "direct", "medium", ["volatility_proxy"], [1.0], 20.0),
        "rate_proxy": _state_def("rate_proxy", "Synthetic rate model input derived from bond proxies.", "rate_index", "model_input", "medium", ["short_duration_bond_price", "long_duration_bond_price"], [-0.30, -0.70], 0.04),
        "time_to_maturity": _state_def("time_to_maturity", "Synthetic option time-to-maturity input.", "years", "model_input", "high", [], [], 0.75),
        "cash_treatment": _state_def("cash_treatment", "Cash face-value treatment.", "cash_scalar", "cash_treatment", "high", [], [], 1.0),
        "money_market_nav": _state_def("money_market_nav", "Synthetic money-market NAV treatment.", "nav", "cash_treatment", "high", ["short_duration_bond_price"], [1.0], 1.0),
        "manager_composite_proxy": _state_def("manager_composite_proxy", "Synthetic opaque manager composite proxy.", "index", "proxy", "low", ["private_market_liquidity", "credit_spread_proxy", "volatility_proxy"], [0.50, -0.25, -0.25], 100.0),
        "human_review_flag": _state_def("human_review_flag", "Explicit human-review state treatment.", "flag", "human_review", "low", [], [], 1.0),
    }
    return {state_variable_id: all_definitions[state_variable_id] for state_variable_id in required_variables}


def _state_def(
    state_variable_id: str,
    description: str,
    value_type: str,
    treatment_type: str,
    confidence: str,
    source_driver_ids: list[str],
    driver_weights: list[float],
    base_value: float,
) -> dict[str, Any]:
    return {
        "state_variable_id": state_variable_id,
        "description": description,
        "value_type": value_type,
        "treatment_type": treatment_type,
        "confidence": confidence,
        "source_driver_ids": source_driver_ids,
        "driver_weights": driver_weights,
        "base_value": base_value,
        "synthetic_data": True,
    }


def _build_history_records(
    dates: list[date],
    driver_history: list[dict[str, Any]],
    expanded_definitions: dict[str, dict[str, Any]],
    required_variables: list[str],
) -> list[dict[str, Any]]:
    records = []
    for day_index, day_record in enumerate(driver_history):
        driver_values = {row["driver_id"]: row["value"] for row in day_record["core_driver_values"]}
        expanded_values = [
            _expanded_state_value(definition, driver_values, day_index, len(dates), scenario_shock_percent=0.0)
            for definition in expanded_definitions.values()
        ]
        records.append(
            {
                "date": day_record["date"],
                "core_driver_values": day_record["core_driver_values"],
                "expanded_state_values": expanded_values,
                "data_quality_flags": _state_data_quality_flags(expanded_values),
                "generation_metadata": {
                    "method": FACTOR_MODEL["method"],
                    "required_state_variable_count": len(required_variables),
                    "synthetic_data": True,
                },
            }
        )
    return records


def _expanded_state_value(
    definition: dict[str, Any],
    driver_values: dict[str, float],
    day_index: int,
    date_count: int,
    scenario_shock_percent: float,
) -> dict[str, Any]:
    state_id = definition["state_variable_id"]
    base_value = float(definition["base_value"])
    value_type = definition["value_type"]
    treatment_type = definition["treatment_type"]
    source_driver_ids = definition["source_driver_ids"]
    driver_weights = definition["driver_weights"]

    if state_id == "cash_treatment":
        value = 1.0
    elif state_id == "human_review_flag":
        value = 1.0
    elif state_id == "time_to_maturity":
        value = max(0.05, base_value - (day_index / 365.0))
    elif state_id == "liquidity_discount_proxy":
        liquidity = driver_values["private_market_liquidity"]
        volatility = driver_values["volatility_proxy"]
        value = min(0.35, max(0.02, base_value + (100.0 - liquidity) / 500.0 + (volatility - 20.0) / 400.0))
    elif state_id == "rate_proxy":
        short_bond = driver_values["short_duration_bond_price"]
        long_bond = driver_values["long_duration_bond_price"]
        value = min(0.11, max(0.005, base_value + (100.0 - short_bond) / 1500.0 + (100.0 - long_bond) / 900.0))
    elif treatment_type == "stale_mark":
        bucket_index = day_index // 30
        driver_component = _weighted_driver_index(driver_values, source_driver_ids, driver_weights)
        value = base_value * (1.0 + bucket_index * 0.006 + (driver_component - 100.0) / 800.0)
    else:
        driver_component = _weighted_driver_index(driver_values, source_driver_ids, driver_weights)
        if value_type == "fx_index":
            value = base_value * driver_component / 100.0
        elif value_type == "nav":
            value = 1.0 + (driver_component - 100.0) / 10000.0
        elif value_type == "volatility_index":
            value = driver_component
        else:
            value = base_value * driver_component / 100.0

    if scenario_shock_percent and treatment_type not in {"cash_treatment", "human_review"}:
        shock_multiplier = 0.30 if treatment_type == "stale_mark" else 1.0
        value *= 1.0 + scenario_shock_percent * shock_multiplier

    return {
        "state_variable_id": state_id,
        "value": round(value, 6),
        "unit": _unit_for_value_type(value_type),
        "value_type": value_type,
        "source_driver_ids": source_driver_ids,
        "proxy_rule": _proxy_rule(definition),
        "confidence": definition["confidence"],
        "treatment_type": treatment_type,
        "description": definition["description"],
        "scenario_shock_percent": round(scenario_shock_percent, 6),
    }


def _weighted_driver_index(driver_values: dict[str, float], source_driver_ids: list[str], driver_weights: list[float]) -> float:
    if not source_driver_ids:
        return 100.0
    return sum(driver_values[driver_id] * weight for driver_id, weight in zip(source_driver_ids, driver_weights))


def _build_proxy_mappings(
    position_universe: dict[str, Any],
    expanded_definitions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    positions_by_instrument: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for position in position_universe["positions"]:
        positions_by_instrument[position["instrument_id"]].append(position)

    mappings = []
    for instrument in position_universe["instruments"]:
        required_variables = list(instrument["required_market_state_variables"])
        state_mappings = []
        for state_variable_id in required_variables:
            definition = expanded_definitions[state_variable_id]
            state_mappings.append(
                {
                    "state_variable_id": state_variable_id,
                    "treatment_type": definition["treatment_type"],
                    "source_driver_ids": definition["source_driver_ids"],
                    "proxy_rule": _proxy_rule(definition),
                    "confidence": _mapping_confidence(instrument, definition),
                }
            )
        mappings.append(
            {
                "instrument_id": instrument["instrument_id"],
                "display_name": instrument["display_name"],
                "instrument_type": instrument["instrument_type"],
                "position_ids": [position["position_id"] for position in positions_by_instrument[instrument["instrument_id"]]],
                "required_state_variables": required_variables,
                "instrument_proxy_hint": instrument.get("proxy_mapping_hint"),
                "lookthrough_status": instrument.get("lookthrough_status"),
                "state_variable_mappings": state_mappings,
                "synthetic_data": True,
            }
        )
    return mappings


def _mapping_confidence(instrument: dict[str, Any], definition: dict[str, Any]) -> str:
    if instrument.get("lookthrough_status") in {"missing", "manager_summary"}:
        return "low"
    if definition["treatment_type"] in {"human_review", "stale_mark"}:
        return "low"
    if definition["treatment_type"] in {"proxy", "model_input"}:
        return "medium"
    return definition["confidence"]


def _missing_or_human_review_state_items(
    position_universe: dict[str, Any],
    proxy_mappings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    mapping_by_instrument = {mapping["instrument_id"]: mapping for mapping in proxy_mappings}
    items = []
    for position in position_universe["positions"]:
        mapping = mapping_by_instrument[position["instrument_id"]]
        if position.get("human_review_required") or any(row["treatment_type"] == "human_review" for row in mapping["state_variable_mappings"]):
            items.append(
                {
                    "item_id": f"state_review_{position['position_id']}",
                    "position_id": position["position_id"],
                    "instrument_id": position["instrument_id"],
                    "manager_id": position["manager_id"],
                    "required_state_variables": position["required_market_state_variables"],
                    "reason": "Human review or low-confidence state treatment required before downstream valuation.",
                    "synthetic_data": True,
                }
            )
    return items


def _build_current_market_state_snapshot(
    position_universe: dict[str, Any],
    latest_record: dict[str, Any],
    required_variables: list[str],
) -> dict[str, Any]:
    expanded_values = latest_record["expanded_state_values"]
    return {
        "schema_version": "simulation_market_state_snapshot.v1",
        "market_state_id": f"market_state_{latest_record['date'].replace('-', '_')}",
        "state_date": latest_record["date"],
        "reporting_currency": position_universe.get("reporting_currency", "USD"),
        "source": {
            "position_universe_id": position_universe["universe_id"],
            "is_synthetic": True,
        },
        "core_driver_values": latest_record["core_driver_values"],
        "expanded_state_values": expanded_values,
        "completeness": _completeness_summary(expanded_values, required_variables),
        "human_review_items": [
            row for row in expanded_values if row["treatment_type"] == "human_review" or row["confidence"] == "low"
        ],
        "synthetic_data": True,
    }


def _build_scenario_market_states(
    position_universe: dict[str, Any],
    current_snapshot: dict[str, Any],
    expanded_definitions: dict[str, dict[str, Any]],
    required_variables: list[str],
) -> list[dict[str, Any]]:
    base_driver_values = {row["driver_id"]: row["value"] for row in current_snapshot["core_driver_values"]}
    scenarios = []
    for definition in SCENARIO_DEFINITIONS:
        shocks = definition["core_driver_shocks"]
        shocked_driver_values = {
            driver_id: base_driver_values[driver_id] * (1.0 + shocks.get(driver_id, 0.0))
            for driver_id in base_driver_values
        }
        expanded_values = []
        for state_definition in expanded_definitions.values():
            variable_shock = _scenario_shock_for_state_variable(state_definition, shocks)
            expanded_values.append(
                _expanded_state_value(
                    state_definition,
                    shocked_driver_values,
                    day_index=90,
                    date_count=91,
                    scenario_shock_percent=variable_shock,
                )
            )
        scenarios.append(
            {
                "schema_version": "simulation_scenario_market_state.v1",
                "scenario_state_id": f"scenario_state_{definition['scenario_id']}",
                "scenario_id": definition["scenario_id"],
                "display_name": definition["display_name"],
                "description": definition["description"],
                "horizon": definition["horizon"],
                "base_market_state_id": current_snapshot["market_state_id"],
                "scenario_date": current_snapshot["state_date"],
                "core_driver_shocks": [
                    {
                        "driver_id": driver_id,
                        "base_value": round(base_driver_values[driver_id], 6),
                        "shocked_value": round(shocked_driver_values[driver_id], 6),
                        "shock_percent": shocks.get(driver_id, 0.0),
                    }
                    for driver_id in sorted(base_driver_values)
                ],
                "expanded_state_values": expanded_values,
                "completeness_summary": _completeness_summary(expanded_values, required_variables),
                "direct_treatment_count": _count_treatment(expanded_values, "direct"),
                "proxy_treatment_count": _count_treatment(expanded_values, "proxy"),
                "human_review_count": _count_treatment(expanded_values, "human_review"),
                "caveats": [
                    "Deterministic synthetic scenario state, not a forecast.",
                    "No position values or portfolio values are calculated in this scenario state.",
                ],
                "synthetic_data": True,
            }
        )
    return scenarios


def _scenario_shock_for_state_variable(definition: dict[str, Any], shocks: dict[str, float]) -> float:
    source_driver_ids = definition["source_driver_ids"]
    weights = definition["driver_weights"]
    if not source_driver_ids:
        return 0.0
    return sum(shocks.get(driver_id, 0.0) * weight for driver_id, weight in zip(source_driver_ids, weights))


def _build_covariance_recovery_check(driver_history: list[dict[str, Any]]) -> dict[str, Any]:
    returns_by_driver: dict[str, list[float]] = defaultdict(list)
    for record in driver_history[1:]:
        for row in record["core_driver_values"]:
            returns_by_driver[row["driver_id"]].append(float(row["daily_return"]))

    estimated_relationships = []
    warning_count = 0
    for left, right, expected_sign, target in INTENDED_RELATIONSHIPS:
        estimated = _correlation(returns_by_driver[left], returns_by_driver[right])
        sign_status = _relationship_status(estimated, expected_sign)
        distance = abs(estimated - target)
        status = "pass" if sign_status == "pass" and distance <= 0.55 else "warning"
        if status != "pass":
            warning_count += 1
        estimated_relationships.append(
            {
                "left_driver_id": left,
                "right_driver_id": right,
                "expected_relationship": expected_sign,
                "target_correlation": target,
                "estimated_correlation": round(estimated, 4),
                "absolute_difference": round(distance, 4),
                "status": status,
            }
        )
    return {
        "method": "sample Pearson correlation over generated daily core-driver returns",
        "intended_relationships": _intended_relationship_records(),
        "estimated_relationships": estimated_relationships,
        "warning_count": warning_count,
        "status": "pass" if warning_count <= 2 else "warning",
        "recovery_notes": [
            "This is a synthetic factor-model coherence check, not production risk-model validation.",
            "Small sample noise is expected over the 90-day demo path.",
        ],
    }


def _intended_relationship_records() -> list[dict[str, Any]]:
    return [
        {
            "left_driver_id": left,
            "right_driver_id": right,
            "expected_relationship": expected,
            "target_correlation": target,
        }
        for left, right, expected, target in INTENDED_RELATIONSHIPS
    ]


def _relationship_status(estimated: float, expected_sign: str) -> str:
    if expected_sign == "positive":
        return "pass" if estimated > 0.10 else "warning"
    if expected_sign == "negative":
        return "pass" if estimated < -0.10 else "warning"
    if expected_sign == "mixed_or_negative":
        return "pass" if estimated < 0.20 else "warning"
    if expected_sign == "weak":
        return "pass" if abs(estimated) < 0.35 else "warning"
    return "warning"


def _correlation(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    covariance = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_var = sum((x - left_mean) ** 2 for x in left)
    right_var = sum((y - right_mean) ** 2 for y in right)
    if left_var == 0.0 or right_var == 0.0:
        return 0.0
    return covariance / math.sqrt(left_var * right_var)


def _completeness_summary(expanded_values: list[dict[str, Any]], required_variables: list[str]) -> dict[str, Any]:
    treatment_counts: dict[str, int] = defaultdict(int)
    confidence_counts: dict[str, int] = defaultdict(int)
    for row in expanded_values:
        treatment_counts[row["treatment_type"]] += 1
        confidence_counts[row["confidence"]] += 1
    covered_variables = {row["state_variable_id"] for row in expanded_values}
    return {
        "required_variable_count": len(required_variables),
        "covered_variable_count": len(covered_variables),
        "missing_variable_count": len(set(required_variables) - covered_variables),
        "direct_treatment_count": treatment_counts.get("direct", 0),
        "proxy_treatment_count": treatment_counts.get("proxy", 0),
        "model_input_treatment_count": treatment_counts.get("model_input", 0),
        "stale_mark_treatment_count": treatment_counts.get("stale_mark", 0),
        "cash_treatment_count": treatment_counts.get("cash_treatment", 0),
        "human_review_count": treatment_counts.get("human_review", 0),
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "status": "complete" if len(set(required_variables) - covered_variables) == 0 else "incomplete",
    }


def _state_data_quality_flags(expanded_values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flags = []
    for row in expanded_values:
        if row["confidence"] == "low" or row["treatment_type"] in {"human_review", "stale_mark"}:
            flags.append(
                {
                    "state_variable_id": row["state_variable_id"],
                    "category": row["treatment_type"],
                    "confidence": row["confidence"],
                    "message": f"Synthetic {row['state_variable_id']} uses {row['treatment_type']} treatment.",
                    "synthetic_data": True,
                }
            )
    return flags


def _count_treatment(expanded_values: list[dict[str, Any]], treatment_type: str) -> int:
    return sum(1 for row in expanded_values if row["treatment_type"] == treatment_type)


def _human_review_state_count(record: dict[str, Any]) -> int:
    return sum(
        1
        for row in _list(record.get("expanded_state_values"))
        if row.get("treatment_type") == "human_review" or row.get("confidence") == "low"
    )


def _required_state_variables(position_universe: dict[str, Any]) -> list[str]:
    variables = {
        variable
        for position in position_universe["positions"]
        for variable in position["required_market_state_variables"]
    }
    return sorted(variables)


def _date_range(start_date: date, end_date: date) -> list[date]:
    day_count = (end_date - start_date).days
    return [start_date + timedelta(days=offset) for offset in range(day_count + 1)]


def _unit_for_value_type(value_type: str) -> str:
    return {
        "discount_percent": "decimal_percent",
        "flag": "boolean_scalar",
        "fx_index": "index_ratio",
        "nav": "nav",
        "rate_index": "decimal_rate",
        "years": "years",
        "cash_scalar": "face_value_scalar",
    }.get(value_type, "index_level")


def _proxy_rule(definition: dict[str, Any]) -> str:
    if not definition["source_driver_ids"]:
        return f"{definition['treatment_type']}:fixed_or_explicit_treatment"
    drivers = ", ".join(definition["source_driver_ids"])
    return f"{definition['treatment_type']}:weighted_driver_map({drivers})"


def _require_top_level(data: dict[str, Any], fields: list[str], errors: list[dict[str, str]]) -> None:
    for field in fields:
        if field not in data:
            _add_issue(errors, "MISSING_TOP_LEVEL_FIELD", field, f"Missing top-level field: {field}")


def _require_fields(record: Any, fields: list[str], context: str, errors: list[dict[str, str]]) -> None:
    if not isinstance(record, dict):
        _add_issue(errors, "RECORD_NOT_OBJECT", context, "Record must be an object")
        return
    for field in fields:
        if field not in record:
            _add_issue(errors, "MISSING_FIELD", context, f"Missing required field: {field}")


def _validate_no_real_data_markers(history: dict[str, Any], errors: list[dict[str, str]]) -> None:
    for path, value in _walk_strings(history):
        lowered = value.lower()
        for marker in REAL_DATA_MARKERS:
            if marker in lowered:
                _add_issue(errors, "REAL_DATA_MARKER_DETECTED", path, f"String contains prohibited marker: {marker}")


def _validate_no_valuation_outputs(history: dict[str, Any], errors: list[dict[str, str]]) -> None:
    forbidden = {
        "daily_valuations",
        "daily_portfolio_valuations",
        "position_values",
        "portfolio_values",
        "portfolio_total",
        "value_change_packages",
    }
    for key in forbidden:
        if key in history:
            _add_issue(errors, "VALUATION_OUTPUT_DETECTED", key, "Market-state history must not contain valuation outputs")


def _walk_strings(value: Any, path: str = "history") -> list[tuple[str, str]]:
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


def _list(value: Any) -> list[dict[str, Any]]:
    return value if isinstance(value, list) else []


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
