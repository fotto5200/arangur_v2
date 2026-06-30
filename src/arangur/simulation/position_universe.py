"""Deterministic synthetic position universe generator."""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

DEFAULT_SEED = 20260630
GENERATOR_VERSION = "synthetic_position_universe_generator.v1"
SCHEMA_VERSION = "simulation_position_universe.v1"
AS_OF_DATE = "2026-06-30"
HISTORY_START_DATE = "2026-04-01"
HISTORY_END_DATE = AS_OF_DATE
GENERATED_AT = "2026-06-30T00:00:00Z"
DEFAULT_OUTPUT_PATH = Path("data/simulation/synthetic_position_universe.json")
DEFAULT_SUMMARY_OUTPUT_PATH = Path("data/simulation/synthetic_position_universe_summary.json")

REQUIRED_ASSET_CLASSES = {
    "public_equity",
    "etf",
    "fixed_income",
    "fx",
    "commodities_energy",
    "crypto",
    "private_equity",
    "private_credit",
    "real_estate",
    "data_center_investment",
    "cash_money_market",
    "opaque_manager_level",
    "option_like",
}

REQUIRED_THEMES = {
    "AI infrastructure",
    "semiconductors",
    "data center power demand",
    "energy bottlenecks",
    "rates sensitivity",
    "private-market liquidity",
    "cash generation",
    "growth/value",
    "defensive ballast",
    "manager overlap",
    "inflation sensitivity",
    "USD exposure",
    "crypto risk",
    "opaque/private marks",
    "data confidence / valuation issue",
}

REQUIRED_POSITION_CLASSIFICATIONS = {
    "asset_class",
    "sector",
    "industry",
    "geography",
    "currency_exposure",
    "liquidity_bucket",
    "value_growth_style",
    "cash_generation_role",
    "manager_role_or_mandate",
    "data_issue_category",
    "instrument_type",
}

REAL_DATA_MARKERS = {
    "real client",
    "actual client",
    "ssn",
    "social security",
    "tax id",
    "account number",
    "routing number",
    "plaid access token",
    "access_token",
    "secret",
    "private key",
}

MANAGER_CONFIGS = [
    {
        "manager_id": "mgr_a_growth_ai_infrastructure",
        "display_name": "Manager A - Growth / AI Infrastructure",
        "short_code": "a",
        "mandate": "Growth / AI Infrastructure",
        "intended_role": "High-conviction public growth and AI infrastructure exposure.",
        "strategy_summary": "Owns synthetic compute, semiconductor, cloud, data-center, and grid-enablement names.",
        "expected_contribution": "Long-term growth engine; may create concentration and drawdown risk.",
        "liquidity_profile": "mostly_liquid",
        "primary_themes": ["AI infrastructure", "semiconductors", "data center power demand", "growth/value"],
        "account_id": "acct_a_public_equity",
        "sleeve_id": "sleeve_public_equity",
        "account_display_name": "Manager A Public Equity Sleeve",
        "account_type": "taxable",
        "sleeve_display_name": "Public Equity / AI Infrastructure Sleeve",
    },
    {
        "manager_id": "mgr_b_core_quality_equity",
        "display_name": "Manager B - Core Quality Equity",
        "short_code": "b",
        "mandate": "Core Quality Equity",
        "intended_role": "Durable core public equity exposure with quality and valuation discipline.",
        "strategy_summary": "Balances quality compounders, broad equity, and selective AI overlap.",
        "expected_contribution": "Core compounding with less thematic concentration than Manager A.",
        "liquidity_profile": "liquid",
        "primary_themes": ["growth/value", "defensive ballast", "manager overlap"],
        "account_id": "acct_b_core_quality",
        "sleeve_id": "sleeve_core_quality",
        "account_display_name": "Manager B Core Quality Account",
        "account_type": "trust",
        "sleeve_display_name": "Core Quality Equity Sleeve",
    },
    {
        "manager_id": "mgr_c_income_cash_generation",
        "display_name": "Manager C - Income and Cash Generation",
        "short_code": "c",
        "mandate": "Income and Cash Generation",
        "intended_role": "Income, credit, and rate-sensitive exposure for spending support.",
        "strategy_summary": "Owns public credit, municipal income, floating-rate exposure, and income-oriented real assets.",
        "expected_contribution": "Cash yield and portfolio income, with rate and credit spread sensitivity.",
        "liquidity_profile": "mixed_liquid",
        "primary_themes": ["cash generation", "rates sensitivity", "defensive ballast"],
        "account_id": "acct_c_income",
        "sleeve_id": "sleeve_income",
        "account_display_name": "Manager C Income Account",
        "account_type": "taxable",
        "sleeve_display_name": "Income / Cash Generation Sleeve",
    },
    {
        "manager_id": "mgr_d_private_real_assets",
        "display_name": "Manager D - Private Markets / Real Assets",
        "short_code": "d",
        "mandate": "Private Markets / Real Assets",
        "intended_role": "Illiquid growth, real assets, private credit, and data center exposure.",
        "strategy_summary": "Holds synthetic fund interests, real estate, infrastructure, data centers, and opaque private marks.",
        "expected_contribution": "Private-market return and inflation-sensitive exposure with lower transparency.",
        "liquidity_profile": "illiquid",
        "primary_themes": ["private-market liquidity", "opaque/private marks", "data center power demand"],
        "account_id": "acct_d_private_markets",
        "sleeve_id": "sleeve_private_markets",
        "account_display_name": "Manager D Private Markets Account",
        "account_type": "partnership",
        "sleeve_display_name": "Private Markets / Real Assets Sleeve",
    },
    {
        "manager_id": "mgr_e_liquidity_defensive",
        "display_name": "Manager E - Liquidity Reserve / Defensive Ballast",
        "short_code": "e",
        "mandate": "Liquidity Reserve / Defensive Ballast",
        "intended_role": "Liquidity, capital preservation, and spending buffer.",
        "strategy_summary": "Holds cash, Treasury bills, short-duration bonds, defensive ETFs, and inflation hedges.",
        "expected_contribution": "May lag in risk-on markets but supports liquidity and drawdown control.",
        "liquidity_profile": "daily_liquidity",
        "primary_themes": ["defensive ballast", "USD exposure", "rates sensitivity"],
        "account_id": "acct_e_liquidity_reserve",
        "sleeve_id": "sleeve_liquidity_reserve",
        "account_display_name": "Manager E Liquidity Reserve Account",
        "account_type": "cash_reserve",
        "sleeve_display_name": "Liquidity Reserve / Defensive Ballast Sleeve",
    },
    {
        "manager_id": "mgr_f_opportunistic_macro",
        "display_name": "Manager F - Opportunistic Macro / Hedge",
        "short_code": "f",
        "mandate": "Opportunistic Macro / Hedge",
        "intended_role": "Macro hedges, currency exposure, commodities, crypto, and option-like risk controls.",
        "strategy_summary": "Uses synthetic FX, commodity, volatility, crypto, and structured exposures.",
        "expected_contribution": "Crisis convexity and differentiated macro exposure, with more complex valuation needs.",
        "liquidity_profile": "mixed_liquid",
        "primary_themes": ["energy bottlenecks", "inflation sensitivity", "crypto risk", "USD exposure"],
        "account_id": "acct_f_opportunistic_macro",
        "sleeve_id": "sleeve_opportunistic_macro",
        "account_display_name": "Manager F Opportunistic Macro Account",
        "account_type": "hedge",
        "sleeve_display_name": "Opportunistic Macro / Hedge Sleeve",
    },
]

THEME_DEFINITIONS = [
    {"theme_id": "theme_ai_infrastructure", "display_name": "AI infrastructure", "description": "Compute, cloud, data center, and grid enablement exposure."},
    {"theme_id": "theme_semiconductors", "display_name": "semiconductors", "description": "Chip design, manufacturing, equipment, and semiconductor ETFs."},
    {"theme_id": "theme_data_center_power", "display_name": "data center power demand", "description": "Data center, power, grid, and cooling requirements."},
    {"theme_id": "theme_energy_bottlenecks", "display_name": "energy bottlenecks", "description": "Energy supply, power bottlenecks, and commodity constraints."},
    {"theme_id": "theme_rates_sensitivity", "display_name": "rates sensitivity", "description": "Duration, curve, credit spread, and rate-proxy exposure."},
    {"theme_id": "theme_private_liquidity", "display_name": "private-market liquidity", "description": "Illiquid private funds, real assets, and secondary liquidity limits."},
    {"theme_id": "theme_cash_generation", "display_name": "cash generation", "description": "Income, distributions, dividends, coupons, and spending support."},
    {"theme_id": "theme_growth_value", "display_name": "growth/value", "description": "Style classification for growth, value, or balanced exposure."},
    {"theme_id": "theme_defensive_ballast", "display_name": "defensive ballast", "description": "Liquidity, short duration, minimum volatility, and stabilizing assets."},
    {"theme_id": "theme_manager_overlap", "display_name": "manager overlap", "description": "Shared or shadowed exposures across managers."},
    {"theme_id": "theme_inflation_sensitivity", "display_name": "inflation sensitivity", "description": "Inflation-linked, commodity, real asset, and pricing power exposure."},
    {"theme_id": "theme_usd_exposure", "display_name": "USD exposure", "description": "USD liquidity, USD strength, and currency hedge exposure."},
    {"theme_id": "theme_crypto_risk", "display_name": "crypto risk", "description": "Bitcoin, crypto infrastructure, and digital asset volatility exposure."},
    {"theme_id": "theme_opaque_marks", "display_name": "opaque/private marks", "description": "Private, stale, low-transparency, or manager-level valuation marks."},
    {"theme_id": "theme_data_confidence_issue", "display_name": "data confidence / valuation issue", "description": "Positions with incomplete, stale, proxy, or human-review valuation needs."},
]

STATE_REQUIREMENTS_BY_TYPE = {
    "public_equity": ["underlying_price"],
    "etf": ["etf_price", "optional_lookthrough_proxy"],
    "fixed_income": ["bond_price_proxy", "duration_bucket_price"],
    "fx_exposure": ["fx_rate"],
    "commodity": ["commodity_price"],
    "crypto": ["crypto_price"],
    "private_equity": ["manager_mark", "private_equity_proxy"],
    "private_credit": ["manager_mark", "credit_spread_proxy"],
    "real_estate": ["manager_mark", "real_asset_proxy", "liquidity_discount_proxy"],
    "data_center_investment": ["private_mark", "ai_infrastructure_proxy", "energy_price_proxy"],
    "cash": ["cash_treatment"],
    "money_market": ["money_market_nav", "cash_treatment"],
    "opaque_manager_level": ["manager_mark", "manager_composite_proxy", "human_review_flag"],
    "option_like": ["underlying_price", "volatility_proxy", "rate_proxy", "time_to_maturity"],
}


def generate_synthetic_position_universe(seed: int = DEFAULT_SEED) -> dict[str, Any]:
    """Generate a deterministic synthetic position universe."""

    rng = random.Random(seed)
    managers = _build_managers()
    accounts = _build_accounts()
    sleeves = _build_sleeves()
    positions, instruments = _build_positions_and_instruments(rng)
    transactions = _build_transactions(positions, seed)
    data_quality_flags, human_review_items = _build_quality_flags(positions)
    universe = {
        "schema_version": SCHEMA_VERSION,
        "universe_id": f"northstar_synthetic_position_universe_seed_{seed}",
        "generated_at": GENERATED_AT,
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "as_of_date": AS_OF_DATE,
        "history_start_date": HISTORY_START_DATE,
        "history_end_date": HISTORY_END_DATE,
        "reporting_currency": "USD",
        "base_currency": "USD",
        "description": (
            "Deterministic synthetic multi-manager family-office position universe for "
            "Arangur simulation kernel Surface 1."
        ),
        "caveats": [
            "Synthetic demo/testing data only.",
            "No prices, market-state paths, scenario states, or valuation outputs are generated in this fixture.",
            "Reported values are placeholder/reference amounts for downstream simulation setup, not market data.",
        ],
        "source": {
            "generator": "arangur.simulation.synthetic_position_universe_generator",
            "generator_version": GENERATOR_VERSION,
            "seed": seed,
            "dataset_id": "northstar_synthetic_position_universe_v1",
            "dataset_label": "Northstar Family Office Synthetic Position Universe",
            "is_synthetic": True,
        },
        "portfolio": {
            "portfolio_id": "portfolio_northstar_family_office",
            "client_family_name": "Northstar Family Office",
            "owner_label": "Northstar Family",
            "advisor_label": "Arangur Demo Advisory Team",
            "base_currency": "USD",
            "is_synthetic": True,
            "description": (
                "Fictional multi-manager portfolio built to exercise manager role review, "
                "theme exposure, private-market confidence, liquidity, and future valuation workflows."
            ),
        },
        "managers": managers,
        "accounts": accounts,
        "sleeves": sleeves,
        "themes": THEME_DEFINITIONS,
        "instruments": instruments,
        "positions": positions,
        "transactions": transactions,
        "data_quality_flags": data_quality_flags,
        "human_review_items": human_review_items,
        "intentional_stories": _build_intentional_stories(),
    }
    universe["validation"] = validate_synthetic_position_universe(universe)
    return universe


def write_synthetic_position_universe(
    path: str | Path = DEFAULT_OUTPUT_PATH,
    seed: int = DEFAULT_SEED,
    summary_path: str | Path | None = None,
) -> dict[str, Any]:
    """Generate, validate, and write the synthetic position universe."""

    universe = generate_synthetic_position_universe(seed=seed)
    validation = universe["validation"]
    if validation["status"] != "valid":
        messages = [f"{issue['code']}: {issue['record_id']} - {issue['message']}" for issue in validation["errors"]]
        raise ValueError("Synthetic position universe validation failed:\n" + "\n".join(messages))

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(output_path, universe)
    if summary_path is not None:
        summary_output_path = Path(summary_path)
        summary_output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(summary_output_path, build_synthetic_position_universe_summary(universe))
    return universe


def load_synthetic_position_universe(path: str | Path = DEFAULT_OUTPUT_PATH) -> dict[str, Any]:
    """Load a synthetic position universe JSON file."""

    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {input_path}")
    return data


def validate_synthetic_position_universe(universe: dict[str, Any]) -> dict[str, Any]:
    """Return structured validation results for a synthetic position universe."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    _require_top_level(
        universe,
        [
            "schema_version",
            "universe_id",
            "generator_version",
            "synthetic_data",
            "as_of_date",
            "history_start_date",
            "history_end_date",
            "reporting_currency",
            "source",
            "portfolio",
            "managers",
            "accounts",
            "sleeves",
            "instruments",
            "positions",
            "transactions",
            "themes",
        ],
        errors,
    )
    if universe.get("schema_version") != SCHEMA_VERSION:
        _add_issue(errors, "SCHEMA_VERSION_MISMATCH", "universe", "Unexpected schema_version")
    if universe.get("synthetic_data") is not True:
        _add_issue(errors, "SYNTHETIC_FLAG_MISSING", "universe", "synthetic_data must be true")

    source = universe.get("source", {})
    if not isinstance(source, dict) or source.get("is_synthetic") is not True:
        _add_issue(errors, "SOURCE_SYNTHETIC_FLAG_MISSING", "source", "source.is_synthetic must be true")
    portfolio = universe.get("portfolio", {})
    if not isinstance(portfolio, dict) or portfolio.get("is_synthetic") is not True:
        _add_issue(errors, "PORTFOLIO_SYNTHETIC_FLAG_MISSING", "portfolio", "portfolio.is_synthetic must be true")

    managers = _list(universe.get("managers"))
    accounts = _list(universe.get("accounts"))
    sleeves = _list(universe.get("sleeves"))
    instruments = _list(universe.get("instruments"))
    positions = _list(universe.get("positions"))
    transactions = _list(universe.get("transactions"))

    if not managers:
        _add_issue(errors, "MISSING_MANAGERS", "managers", "At least one manager is required")
    if not accounts:
        _add_issue(errors, "MISSING_ACCOUNTS", "accounts", "At least one account is required")
    if not sleeves:
        _add_issue(errors, "MISSING_SLEEVES", "sleeves", "At least one sleeve is required")
    if len(positions) < 50:
        _add_issue(errors, "TOO_FEW_POSITIONS", "positions", "At least 50 positions are required")

    manager_ids = _collect_unique_ids(managers, "manager_id", "managers", errors)
    account_ids = _collect_unique_ids(accounts, "account_id", "accounts", errors)
    sleeve_ids = _collect_unique_ids(sleeves, "sleeve_id", "sleeves", errors)
    instrument_ids = _collect_unique_ids(instruments, "instrument_id", "instruments", errors)
    position_ids = _collect_unique_ids(positions, "position_id", "positions", errors)
    _collect_unique_ids(transactions, "transaction_id", "transactions", errors)

    for manager in managers:
        _require_fields(
            manager,
            [
                "manager_id",
                "display_name",
                "mandate",
                "strategy_summary",
                "expected_contribution",
                "liquidity_profile",
                "primary_themes",
                "accounts",
                "sleeves",
                "synthetic_data",
            ],
            f"manager:{manager.get('manager_id')}",
            errors,
        )
        if manager.get("synthetic_data") is not True:
            _add_issue(errors, "MANAGER_SYNTHETIC_FLAG_MISSING", str(manager.get("manager_id")), "manager.synthetic_data must be true")

    for account in accounts:
        _require_fields(account, ["account_id", "manager_id", "sleeve_id", "display_name", "account_type", "currency", "synthetic_data"], f"account:{account.get('account_id')}", errors)
        if account.get("manager_id") not in manager_ids:
            _add_issue(errors, "UNKNOWN_ACCOUNT_MANAGER", str(account.get("account_id")), "Account references unknown manager")
        if account.get("sleeve_id") not in sleeve_ids:
            _add_issue(errors, "UNKNOWN_ACCOUNT_SLEEVE", str(account.get("account_id")), "Account references unknown sleeve")
        if account.get("synthetic_data") is not True:
            _add_issue(errors, "ACCOUNT_SYNTHETIC_FLAG_MISSING", str(account.get("account_id")), "account.synthetic_data must be true")

    for sleeve in sleeves:
        _require_fields(sleeve, ["sleeve_id", "manager_id", "account_id", "display_name", "mandate", "synthetic_data"], f"sleeve:{sleeve.get('sleeve_id')}", errors)
        if sleeve.get("manager_id") not in manager_ids:
            _add_issue(errors, "UNKNOWN_SLEEVE_MANAGER", str(sleeve.get("sleeve_id")), "Sleeve references unknown manager")
        if sleeve.get("account_id") not in account_ids:
            _add_issue(errors, "UNKNOWN_SLEEVE_ACCOUNT", str(sleeve.get("sleeve_id")), "Sleeve references unknown account")

    for instrument in instruments:
        _require_fields(
            instrument,
            [
                "instrument_id",
                "display_name",
                "instrument_type",
                "synthetic_identifier",
                "asset_class",
                "currency",
                "required_market_state_variables",
                "valuation_method_hint",
                "synthetic_data",
            ],
            f"instrument:{instrument.get('instrument_id')}",
            errors,
        )
        if instrument.get("synthetic_data") is not True:
            _add_issue(errors, "INSTRUMENT_SYNTHETIC_FLAG_MISSING", str(instrument.get("instrument_id")), "instrument.synthetic_data must be true")
        if not instrument.get("required_market_state_variables"):
            _add_issue(errors, "MISSING_INSTRUMENT_STATE_REQUIREMENTS", str(instrument.get("instrument_id")), "Instrument must declare future market-state requirements")

    asset_classes = set()
    themes = set()
    private_or_stale_count = 0
    human_review_count = 0
    overlap_tracker: dict[str, set[str]] = defaultdict(set)
    for position in positions:
        _require_fields(
            position,
            [
                "position_id",
                "instrument_id",
                "manager_id",
                "account_id",
                "sleeve_id",
                "display_name",
                "instrument_type",
                "synthetic_identifier",
                "base_currency",
                "ownership_status",
                "valuation_method_hint",
                "required_market_state_variables",
                "liquidity_bucket",
                "valuation_confidence",
                "data_quality_flags",
                "human_review_required",
                "lookthrough_status",
                "classifications",
                "themes",
                "synthetic_data",
            ],
            f"position:{position.get('position_id')}",
            errors,
        )
        record_id = str(position.get("position_id"))
        if position.get("instrument_id") not in instrument_ids:
            _add_issue(errors, "UNKNOWN_POSITION_INSTRUMENT", record_id, "Position references unknown instrument")
        if position.get("manager_id") not in manager_ids:
            _add_issue(errors, "UNKNOWN_POSITION_MANAGER", record_id, "Position references unknown manager")
        if position.get("account_id") not in account_ids:
            _add_issue(errors, "UNKNOWN_POSITION_ACCOUNT", record_id, "Position references unknown account")
        if position.get("sleeve_id") not in sleeve_ids:
            _add_issue(errors, "UNKNOWN_POSITION_SLEEVE", record_id, "Position references unknown sleeve")
        if position.get("synthetic_data") is not True:
            _add_issue(errors, "POSITION_SYNTHETIC_FLAG_MISSING", record_id, "position.synthetic_data must be true")
        if not position.get("required_market_state_variables"):
            _add_issue(errors, "MISSING_POSITION_STATE_REQUIREMENTS", record_id, "Position must declare future market-state requirements")

        classifications = position.get("classifications", {})
        if not isinstance(classifications, dict):
            _add_issue(errors, "POSITION_CLASSIFICATIONS_INVALID", record_id, "classifications must be an object")
            classifications = {}
        missing_classifications = REQUIRED_POSITION_CLASSIFICATIONS - set(classifications)
        if missing_classifications:
            _add_issue(errors, "MISSING_POSITION_CLASSIFICATIONS", record_id, f"Missing lens fields: {', '.join(sorted(missing_classifications))}")
        if classifications.get("asset_class"):
            asset_classes.add(classifications["asset_class"])
        if position.get("themes"):
            themes.update(position["themes"])
        if position.get("instrument_id") and position.get("manager_id"):
            overlap_tracker[position["instrument_id"]].add(position["manager_id"])
        if position.get("human_review_required") is True:
            human_review_count += 1
        if _has_any_flag(position, {"stale_private_mark", "opaque_manager_mark", "private_mark", "human_review_required"}):
            private_or_stale_count += 1

    missing_asset_classes = REQUIRED_ASSET_CLASSES - asset_classes
    if missing_asset_classes:
        _add_issue(errors, "MISSING_REQUIRED_ASSET_CLASSES", "positions", f"Missing asset classes: {', '.join(sorted(missing_asset_classes))}")
    missing_themes = REQUIRED_THEMES - themes
    if missing_themes:
        _add_issue(errors, "MISSING_REQUIRED_THEMES", "positions", f"Missing themes: {', '.join(sorted(missing_themes))}")
    if human_review_count < 1:
        _add_issue(errors, "MISSING_HUMAN_REVIEW_ITEM", "positions", "At least one position must require human review")
    if private_or_stale_count < 1:
        _add_issue(errors, "MISSING_PRIVATE_OR_STALE_MARK", "positions", "At least one private/opaque/stale mark example is required")
    if not any(len(managers_for_instrument) >= 2 for managers_for_instrument in overlap_tracker.values()):
        _add_issue(errors, "MISSING_MANAGER_OVERLAP_STORY", "positions", "At least one instrument must appear across multiple managers")

    for transaction in transactions:
        _require_fields(
            transaction,
            ["transaction_id", "date", "manager_id", "transaction_type", "cash_amount", "currency", "description", "synthetic_data"],
            f"transaction:{transaction.get('transaction_id')}",
            errors,
        )
        record_id = str(transaction.get("transaction_id"))
        if transaction.get("manager_id") not in manager_ids:
            _add_issue(errors, "UNKNOWN_TRANSACTION_MANAGER", record_id, "Transaction references unknown manager")
        position_id = transaction.get("position_id")
        account_id = transaction.get("account_id")
        if position_id is None and account_id is None:
            _add_issue(errors, "TRANSACTION_REFERENCE_MISSING", record_id, "Transaction must reference a position_id or account_id")
        if position_id is not None and position_id not in position_ids:
            _add_issue(errors, "UNKNOWN_TRANSACTION_POSITION", record_id, "Transaction references unknown position")
        if account_id is not None and account_id not in account_ids:
            _add_issue(errors, "UNKNOWN_TRANSACTION_ACCOUNT", record_id, "Transaction references unknown account")
        if transaction.get("synthetic_data") is not True:
            _add_issue(errors, "TRANSACTION_SYNTHETIC_FLAG_MISSING", record_id, "transaction.synthetic_data must be true")

    _validate_history_dates(universe, transactions, warnings)
    _validate_no_real_data_markers(universe, errors)

    return {
        "status": "invalid" if errors else "valid",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "manager_count": len(managers),
            "account_count": len(accounts),
            "sleeve_count": len(sleeves),
            "instrument_count": len(instruments),
            "position_count": len(positions),
            "transaction_count": len(transactions),
            "human_review_item_count": human_review_count,
        },
    }


def build_synthetic_position_universe_summary(universe: dict[str, Any]) -> dict[str, Any]:
    """Build a compact review summary for a synthetic position universe."""

    positions = _list(universe.get("positions"))
    transactions = _list(universe.get("transactions"))
    asset_classes = sorted({position["classifications"]["asset_class"] for position in positions})
    themes = sorted({theme for position in positions for theme in position.get("themes", [])})
    human_review_positions = [position["position_id"] for position in positions if position.get("human_review_required")]
    stale_or_private_positions = [
        position["position_id"]
        for position in positions
        if _has_any_flag(position, {"stale_private_mark", "opaque_manager_mark", "private_mark", "human_review_required"})
    ]
    overlap = _manager_overlap_summary(positions)
    transaction_dates = sorted(transaction["date"] for transaction in transactions)
    return {
        "schema_version": "simulation_position_universe_summary.v1",
        "universe_id": universe["universe_id"],
        "seed": universe["source"]["seed"],
        "as_of_date": universe["as_of_date"],
        "history_start_date": universe["history_start_date"],
        "history_end_date": universe["history_end_date"],
        "manager_count": len(_list(universe.get("managers"))),
        "account_count": len(_list(universe.get("accounts"))),
        "sleeve_count": len(_list(universe.get("sleeves"))),
        "instrument_count": len(_list(universe.get("instruments"))),
        "position_count": len(positions),
        "transaction_count": len(transactions),
        "asset_classes": asset_classes,
        "themes": themes,
        "human_review_count": len(human_review_positions),
        "human_review_positions": human_review_positions,
        "stale_or_private_mark_count": len(stale_or_private_positions),
        "manager_overlap_examples": overlap,
        "transaction_date_range": {
            "start": transaction_dates[0] if transaction_dates else None,
            "end": transaction_dates[-1] if transaction_dates else None,
            "day_span": _date_span(transaction_dates) if transaction_dates else 0,
        },
        "validation_status": universe.get("validation", {}).get("status"),
    }


def _build_managers() -> list[dict[str, Any]]:
    managers = []
    for config in MANAGER_CONFIGS:
        managers.append(
            {
                "manager_id": config["manager_id"],
                "display_name": config["display_name"],
                "mandate": config["mandate"],
                "intended_role": config["intended_role"],
                "strategy_summary": config["strategy_summary"],
                "expected_contribution": config["expected_contribution"],
                "liquidity_profile": config["liquidity_profile"],
                "primary_themes": config["primary_themes"],
                "accounts": [config["account_id"]],
                "sleeves": [config["sleeve_id"]],
                "synthetic_data": True,
            }
        )
    return managers


def _build_accounts() -> list[dict[str, Any]]:
    accounts = []
    for config in MANAGER_CONFIGS:
        accounts.append(
            {
                "account_id": config["account_id"],
                "display_name": config["account_display_name"],
                "manager_id": config["manager_id"],
                "sleeve_id": config["sleeve_id"],
                "account_type": config["account_type"],
                "currency": "USD",
                "custodian_label": "Synthetic Demo Custody",
                "household_member": "Northstar Family Office",
                "tags": [config["mandate"], *config["primary_themes"]],
                "synthetic_data": True,
            }
        )
    return accounts


def _build_sleeves() -> list[dict[str, Any]]:
    sleeves = []
    for config in MANAGER_CONFIGS:
        sleeves.append(
            {
                "sleeve_id": config["sleeve_id"],
                "display_name": config["sleeve_display_name"],
                "manager_id": config["manager_id"],
                "account_id": config["account_id"],
                "mandate": config["mandate"],
                "lens_label": "Manager role / mandate",
                "themes": config["primary_themes"],
                "synthetic_data": True,
            }
        )
    return sleeves


def _build_positions_and_instruments(rng: random.Random) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    positions: list[dict[str, Any]] = []
    instruments_by_id: dict[str, dict[str, Any]] = {}
    manager_by_code = {config["short_code"]: config for config in MANAGER_CONFIGS}
    for index, blueprint in enumerate(_position_blueprints(), start=1):
        manager = manager_by_code[blueprint["manager_code"]]
        instrument_id = f"instr_{blueprint['instrument_slug']}"
        state_requirements = list(STATE_REQUIREMENTS_BY_TYPE[blueprint["instrument_type"]])
        data_quality_flags = list(blueprint.get("data_quality_flags", []))
        human_review_required = bool(blueprint.get("human_review_required", False))
        if human_review_required and "human_review_required" not in data_quality_flags:
            data_quality_flags.append("human_review_required")
        if blueprint["valuation_confidence"] in {"low", "unknown"} and "valuation_confidence_issue" not in data_quality_flags:
            data_quality_flags.append("valuation_confidence_issue")

        instrument = {
            "instrument_id": instrument_id,
            "display_name": blueprint["display_name"],
            "synthetic_identifier": blueprint["synthetic_identifier"],
            "instrument_type": blueprint["instrument_type"],
            "asset_class": blueprint["asset_class"],
            "currency": blueprint.get("currency", "USD"),
            "sector": blueprint["sector"],
            "industry": blueprint["industry"],
            "geography": blueprint["geography"],
            "public_private": blueprint["public_private"],
            "required_market_state_variables": state_requirements,
            "valuation_method_hint": blueprint["valuation_method_hint"],
            "proxy_mapping_hint": blueprint["proxy_mapping_hint"],
            "scenario_exposure_hints": blueprint["scenario_exposure_hints"],
            "lookthrough_status": blueprint["lookthrough_status"],
            "themes": sorted(blueprint["themes"]),
            "synthetic_data": True,
        }
        instruments_by_id.setdefault(instrument_id, instrument)

        value = float(blueprint["target_value"])
        quantity = _quantity_for_position(blueprint, value, rng)
        cost_basis = None if "missing_cost_basis" in data_quality_flags else round(value * rng.uniform(0.78, 1.12), 2)
        position = {
            "position_id": f"pos_{manager['short_code']}_{blueprint['position_slug']}",
            "instrument_id": instrument_id,
            "manager_id": manager["manager_id"],
            "account_id": manager["account_id"],
            "sleeve_id": manager["sleeve_id"],
            "display_name": blueprint["display_name"],
            "instrument_type": blueprint["instrument_type"],
            "synthetic_identifier": blueprint["synthetic_identifier"],
            "quantity": quantity,
            "quantity_unit": blueprint["quantity_unit"],
            "notional": round(value, 2) if blueprint["quantity_unit"] != "shares" else None,
            "base_currency": blueprint.get("currency", "USD"),
            "cost_basis": cost_basis,
            "initial_reference_value": round(value * rng.uniform(0.84, 1.06), 2),
            "current_reported_value": round(value, 2),
            "ownership_status": blueprint.get("ownership_status", "active"),
            "valuation_method_hint": blueprint["valuation_method_hint"],
            "required_market_state_variables": state_requirements,
            "liquidity_bucket": blueprint["liquidity_bucket"],
            "valuation_confidence": blueprint["valuation_confidence"],
            "data_quality_flags": sorted(data_quality_flags),
            "human_review_required": human_review_required,
            "lookthrough_status": blueprint["lookthrough_status"],
            "proxy_mapping_hint": blueprint["proxy_mapping_hint"],
            "scenario_exposure_hints": blueprint["scenario_exposure_hints"],
            "classifications": {
                "asset_class": blueprint["asset_class"],
                "sector": blueprint["sector"],
                "industry": blueprint["industry"],
                "geography": blueprint["geography"],
                "currency_exposure": blueprint.get("currency_exposure", "USD"),
                "liquidity_bucket": blueprint["liquidity_bucket"],
                "value_growth_style": blueprint["value_growth_style"],
                "cash_generation_role": blueprint["cash_generation_role"],
                "manager_role_or_mandate": manager["mandate"],
                "data_issue_category": blueprint["data_issue_category"],
                "instrument_type": blueprint["instrument_type"],
            },
            "themes": sorted(blueprint["themes"]),
            "position_story_tags": sorted(blueprint.get("position_story_tags", [])),
            "future_valuation_requirements": {
                "required_market_state_variables": state_requirements,
                "valuation_method_hint": blueprint["valuation_method_hint"],
                "proxy_mapping_hint": blueprint["proxy_mapping_hint"],
                "notes": blueprint["valuation_notes"],
            },
            "synthetic_data": True,
            "sort_order": index,
        }
        positions.append(position)
    return positions, sorted(instruments_by_id.values(), key=lambda row: row["instrument_id"])


def _build_transactions(positions: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed + 17)
    transactions: list[dict[str, Any]] = []
    start = date.fromisoformat(HISTORY_START_DATE)
    end = date.fromisoformat(HISTORY_END_DATE)
    day_count = (end - start).days
    manager_account = {config["manager_id"]: config["account_id"] for config in MANAGER_CONFIGS}

    for manager_index, config in enumerate(MANAGER_CONFIGS, start=1):
        transactions.append(
            {
                "transaction_id": f"txn_{manager_index:03d}_opening_contribution",
                "date": HISTORY_START_DATE,
                "account_id": config["account_id"],
                "position_id": None,
                "manager_id": config["manager_id"],
                "transaction_type": "contribution",
                "quantity_delta": None,
                "notional_delta": 250000.0 + manager_index * 35000.0,
                "cash_amount": 250000.0 + manager_index * 35000.0,
                "currency": "USD",
                "description": f"Synthetic opening liquidity contribution for {config['display_name']}.",
                "synthetic_data": True,
            }
        )

    for index, position in enumerate(positions, start=1):
        txn_date = start + timedelta(days=(index * 7 + rng.randint(0, 6)) % (day_count + 1))
        txn_type = _transaction_type_for_position(position, index)
        cash_amount, quantity_delta, notional_delta = _transaction_amounts(position, txn_type, rng)
        transactions.append(
            {
                "transaction_id": f"txn_{index + len(MANAGER_CONFIGS):03d}_{position['position_id']}",
                "date": txn_date.isoformat(),
                "account_id": position["account_id"],
                "position_id": position["position_id"],
                "manager_id": position["manager_id"],
                "transaction_type": txn_type,
                "quantity_delta": quantity_delta,
                "notional_delta": notional_delta,
                "cash_amount": cash_amount,
                "currency": position["base_currency"],
                "description": _transaction_description(position, txn_type),
                "synthetic_data": True,
            }
        )

    transactions.extend(
        [
            {
                "transaction_id": "txn_999_family_withdrawal",
                "date": (end - timedelta(days=9)).isoformat(),
                "account_id": manager_account["mgr_e_liquidity_defensive"],
                "position_id": None,
                "manager_id": "mgr_e_liquidity_defensive",
                "transaction_type": "withdrawal",
                "quantity_delta": None,
                "notional_delta": -180000.0,
                "cash_amount": -180000.0,
                "currency": "USD",
                "description": "Synthetic family office spending withdrawal from liquidity reserve.",
                "synthetic_data": True,
            },
            {
                "transaction_id": "txn_998_advisory_fee",
                "date": HISTORY_END_DATE,
                "account_id": manager_account["mgr_b_core_quality_equity"],
                "position_id": None,
                "manager_id": "mgr_b_core_quality_equity",
                "transaction_type": "fee",
                "quantity_delta": None,
                "notional_delta": -42000.0,
                "cash_amount": -42000.0,
                "currency": "USD",
                "description": "Synthetic quarterly advisory and custody fee accrual.",
                "synthetic_data": True,
            },
        ]
    )
    return sorted(transactions, key=lambda row: (row["date"], row["transaction_id"]))


def _build_quality_flags(positions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    flags: list[dict[str, Any]] = []
    review_items: list[dict[str, Any]] = []
    for position in positions:
        for flag in position["data_quality_flags"]:
            severity = "high" if flag == "human_review_required" else "medium"
            flags.append(
                {
                    "flag_id": f"dq_{position['position_id']}_{flag}",
                    "record_type": "position",
                    "record_id": position["position_id"],
                    "category": flag,
                    "severity": severity,
                    "human_review_required": position["human_review_required"],
                    "message": _quality_flag_message(position, flag),
                    "synthetic_data": True,
                }
            )
        if position["human_review_required"]:
            review_items.append(
                {
                    "review_item_id": f"review_{position['position_id']}",
                    "record_type": "position",
                    "record_id": position["position_id"],
                    "manager_id": position["manager_id"],
                    "category": position["classifications"]["data_issue_category"],
                    "reason": _human_review_reason(position),
                    "synthetic_data": True,
                }
            )
    return flags, review_items


def _build_intentional_stories() -> list[dict[str, Any]]:
    return [
        {
            "story_id": "story_ai_chip_overlap",
            "title": "AI and semiconductor overlap across managers",
            "description": "Manager A, Manager B, and Manager F intentionally share synthetic compute, chip, and AI infrastructure exposure.",
            "themes": ["AI infrastructure", "semiconductors", "manager overlap"],
        },
        {
            "story_id": "story_liquidity_ballast",
            "title": "Liquidity reserve may lag but serves a mandate",
            "description": "Manager E owns cash, T-bills, short duration bonds, and defensive ballast that may look weak in raw P&L during risk-on periods.",
            "themes": ["defensive ballast", "USD exposure", "rates sensitivity"],
        },
        {
            "story_id": "story_private_opaque_marks",
            "title": "Private and opaque positions need confidence review",
            "description": "Manager D contains stale private marks, opaque fund interests, and data center investments requiring proxy or human-review treatment later.",
            "themes": ["private-market liquidity", "opaque/private marks", "data confidence / valuation issue"],
        },
        {
            "story_id": "story_power_and_energy",
            "title": "Data center power and energy bottleneck exposure",
            "description": "The universe includes data center, grid, power campus, LNG, uranium, copper, and energy positions.",
            "themes": ["data center power demand", "energy bottlenecks", "inflation sensitivity"],
        },
    ]


def _position_blueprints() -> list[dict[str, Any]]:
    rows = [
        # Manager A: Growth / AI Infrastructure
        _bp("a", "ai_compute_leader", "AI Compute Leader", "AICL", "public_equity", "public_equity", "technology", "semiconductors", 1850000, ["AI infrastructure", "semiconductors", "manager overlap", "growth/value"], "high", "large_cap_growth", "none", "direct_price", "direct_public_equity", ["ai_compute", "semiconductor_beta"], "liquid", "growth", "none", "public", "North America", "shares"),
        _bp("a", "cloud_platform_compounder", "Cloud Platform Compounder", "CLDP", "public_equity", "public_equity", "technology", "cloud infrastructure", 1480000, ["AI infrastructure", "manager overlap", "growth/value"], "high", "large_cap_growth", "none", "direct_price", "direct_public_equity", ["cloud_ai", "broad_equity"], "liquid", "growth", "none", "public", "North America", "shares"),
        _bp("a", "chip_fabrication_partner", "Chip Fabrication Partner", "CFAB", "public_equity", "public_equity", "technology", "semiconductor manufacturing", 1125000, ["AI infrastructure", "semiconductors", "growth/value"], "medium", "large_cap_growth", "none", "direct_price", "direct_public_equity", ["semiconductor_beta", "asia_supply_chain"], "liquid", "growth", "proxy_classification", "public", "Asia", "shares"),
        _bp("a", "semicap_equipment_maker", "Semicap Equipment Maker", "SEMI", "public_equity", "public_equity", "technology", "semiconductor equipment", 920000, ["semiconductors", "AI infrastructure", "growth/value"], "high", "large_cap_growth", "none", "direct_price", "direct_public_equity", ["semiconductor_beta"], "liquid", "growth", "none", "public", "Europe", "shares"),
        _bp("a", "accelerator_design_house", "Accelerator Design House", "ACCD", "public_equity", "public_equity", "technology", "chip design", 740000, ["AI infrastructure", "semiconductors", "growth/value"], "medium", "large_cap_growth", "none", "direct_price", "direct_public_equity", ["ai_compute", "semiconductor_beta"], "liquid", "growth", "proxy_classification", "public", "North America", "shares"),
        _bp("a", "advanced_packaging_supplier", "Advanced Packaging Supplier", "PACK", "public_equity", "public_equity", "technology", "semiconductor packaging", 510000, ["semiconductors", "AI infrastructure"], "medium", "growth", "none", "direct_price", "direct_public_equity", ["semiconductor_beta"], "liquid", "growth", "proxy_classification", "public", "Asia", "shares"),
        _bp("a", "ai_chip_etf", "AI Chip Basket ETF", "AICH", "etf", "etf", "technology", "semiconductor ETF", 680000, ["AI infrastructure", "semiconductors", "manager overlap", "growth/value"], "high", "growth_etf", "none", "etf_proxy", "lookthrough_proxy:semiconductors", ["semiconductor_beta", "broad_equity"], "liquid", "growth", "none", "public", "Global", "shares"),
        _bp("a", "data_center_cooling_leader", "Data Center Cooling Leader", "COOL", "public_equity", "public_equity", "industrials", "thermal management", 455000, ["AI infrastructure", "data center power demand", "energy bottlenecks"], "medium", "growth", "none", "direct_price", "direct_public_equity", ["data_center_power", "industrial_beta"], "liquid", "growth", "proxy_classification", "public", "North America", "shares"),
        _bp("a", "edge_server_platform", "Edge Server Platform", "EDGE", "public_equity", "public_equity", "technology", "server infrastructure", 410000, ["AI infrastructure", "data center power demand"], "medium", "growth", "none", "direct_price", "direct_public_equity", ["ai_compute", "hardware_beta"], "liquid", "growth", "proxy_classification", "public", "North America", "shares"),
        _bp("a", "enterprise_ai_software", "Enterprise AI Software", "EAI", "public_equity", "public_equity", "technology", "enterprise software", 575000, ["AI infrastructure", "growth/value"], "high", "large_cap_growth", "none", "direct_price", "direct_public_equity", ["software_beta", "ai_adoption"], "liquid", "growth", "none", "public", "North America", "shares"),
        _bp("a", "grid_enabler_equity", "Grid Enabler Equity", "GRID", "public_equity", "public_equity", "utilities", "grid equipment", 365000, ["data center power demand", "energy bottlenecks", "inflation sensitivity"], "medium", "growth", "none", "direct_price", "direct_public_equity", ["power_grid", "industrial_beta"], "liquid", "balanced", "proxy_classification", "public", "North America", "shares"),
        _bp("a", "data_center_public_reit", "Public Data Center REIT", "DCRT", "public_equity", "real_estate", "real estate", "data center REIT", 420000, ["data center power demand", "AI infrastructure", "rates sensitivity"], "medium", "growth_income", "dividend", "direct_price", "reit_proxy:data_center", ["data_center_power", "rates_duration"], "liquid", "balanced", "proxy_classification", "public", "North America", "shares"),
        _bp("a", "ai_infra_call_spread_note", "AI Infrastructure Call Spread Note", "AICN", "option_like", "option_like", "structured products", "equity-linked note", 275000, ["AI infrastructure", "semiconductors", "data confidence / valuation issue"], "low", "option_like", "none", "simple_option_model", "underlying_basket:AI infrastructure", ["ai_compute", "volatility"], "monthly_liquidity", "growth", "model_required", "structured", "North America", "notional_usd", human=True, flags=["complex_terms"]),
        _bp("a", "public_ai_money_market_sweep", "Public AI Sleeve Money Market Sweep", "MMDA", "money_market", "cash_money_market", "cash", "money market", 310000, ["USD exposure", "defensive ballast"], "high", "cash", "cash_buffer", "cash_treatment", "cash_like", ["cash"], "daily_liquidity", "neutral", "none", "cash", "North America", "shares"),
        # Manager B: Core Quality Equity
        _bp("b", "cloud_platform_compounder", "Cloud Platform Compounder", "CLDP", "public_equity", "public_equity", "technology", "cloud infrastructure", 1320000, ["AI infrastructure", "manager overlap", "growth/value"], "high", "quality_growth", "none", "direct_price", "direct_public_equity", ["cloud_ai", "broad_equity"], "liquid", "growth", "none", "public", "North America", "shares"),
        _bp("b", "ai_compute_leader", "AI Compute Leader", "AICL", "public_equity", "public_equity", "technology", "semiconductors", 620000, ["AI infrastructure", "semiconductors", "manager overlap", "growth/value"], "high", "quality_growth", "none", "direct_price", "direct_public_equity", ["ai_compute", "semiconductor_beta"], "liquid", "growth", "none", "public", "North America", "shares"),
        _bp("b", "consumer_platform_quality", "Consumer Platform Quality", "CPQ", "public_equity", "public_equity", "technology", "consumer platforms", 910000, ["growth/value", "defensive ballast"], "high", "quality_growth", "none", "direct_price", "direct_public_equity", ["quality_growth"], "liquid", "growth", "none", "public", "North America", "shares"),
        _bp("b", "payments_network_core", "Payments Network Core", "PAYN", "public_equity", "public_equity", "financials", "payments", 760000, ["growth/value", "cash generation"], "high", "quality_growth", "dividend", "direct_price", "direct_public_equity", ["quality_growth", "consumer_spending"], "liquid", "balanced", "none", "public", "North America", "shares"),
        _bp("b", "quality_consumer_staples", "Quality Consumer Staples", "STPL", "public_equity", "public_equity", "consumer staples", "consumer staples", 635000, ["defensive ballast", "cash generation", "growth/value"], "high", "quality_defensive", "dividend", "direct_price", "direct_public_equity", ["defensive_equity"], "liquid", "value", "none", "public", "North America", "shares"),
        _bp("b", "healthcare_resilience", "Healthcare Resilience", "HLTH", "public_equity", "public_equity", "health care", "managed care", 540000, ["defensive ballast", "growth/value"], "high", "quality_defensive", "none", "direct_price", "direct_public_equity", ["defensive_equity"], "liquid", "balanced", "none", "public", "North America", "shares"),
        _bp("b", "core_bank_quality", "Core Bank Quality", "CBKQ", "public_equity", "public_equity", "financials", "banking", 495000, ["cash generation", "rates sensitivity", "growth/value"], "medium", "quality_value", "dividend", "direct_price", "direct_public_equity", ["financials", "rates_sensitivity"], "liquid", "value", "proxy_classification", "public", "North America", "shares"),
        _bp("b", "industrial_compounder", "Industrial Compounder", "INDQ", "public_equity", "public_equity", "industrials", "industrial automation", 470000, ["AI infrastructure", "growth/value"], "medium", "quality_growth", "none", "direct_price", "direct_public_equity", ["industrial_beta"], "liquid", "balanced", "none", "public", "North America", "shares"),
        _bp("b", "quality_factor_etf", "Quality Factor ETF", "QUALX", "etf", "etf", "multi-sector", "quality ETF", 880000, ["defensive ballast", "growth/value"], "high", "quality_etf", "none", "etf_proxy", "lookthrough_proxy:quality_equity", ["broad_equity", "quality_factor"], "liquid", "balanced", "none", "public", "North America", "shares"),
        _bp("b", "value_factor_etf", "Value Factor ETF", "VALX", "etf", "etf", "multi-sector", "value ETF", 415000, ["growth/value", "cash generation"], "high", "value_etf", "dividend", "etf_proxy", "lookthrough_proxy:value_equity", ["value_factor"], "liquid", "value", "none", "public", "North America", "shares"),
        _bp("b", "broad_developed_equity_etf", "Developed Market Equity ETF", "DMKT", "etf", "etf", "multi-sector", "developed market ETF", 390000, ["growth/value", "USD exposure"], "high", "core_equity_etf", "none", "etf_proxy", "lookthrough_proxy:developed_equity", ["broad_equity", "fx_translation"], "liquid", "balanced", "none", "public", "Global", "shares"),
        _bp("b", "core_quality_cash_sweep", "Core Quality Cash Sweep", "MMQB", "money_market", "cash_money_market", "cash", "money market", 220000, ["USD exposure", "defensive ballast"], "high", "cash", "cash_buffer", "cash_treatment", "cash_like", ["cash"], "daily_liquidity", "neutral", "none", "cash", "North America", "shares"),
        # Manager C: Income and Cash Generation
        _bp("c", "short_tips_etf", "Short TIPS ETF", "TIPZ", "etf", "fixed_income", "fixed income", "inflation linked", 720000, ["rates sensitivity", "inflation sensitivity", "defensive ballast"], "high", "income", "income", "etf_proxy", "duration_bucket:short_tips", ["rates_duration", "inflation"], "daily_liquidity", "neutral", "none", "public", "North America", "shares"),
        _bp("c", "investment_grade_bond_etf", "Investment Grade Bond ETF", "IGBD", "etf", "fixed_income", "fixed income", "investment grade credit", 840000, ["rates sensitivity", "cash generation", "defensive ballast"], "high", "income", "income", "etf_proxy", "duration_bucket:intermediate_credit", ["rates_duration", "credit_spreads"], "daily_liquidity", "neutral", "none", "public", "North America", "shares"),
        _bp("c", "municipal_income_ladder", "Municipal Income Ladder", "MUNI", "fixed_income", "fixed_income", "fixed income", "municipal bonds", 560000, ["cash generation", "rates sensitivity", "defensive ballast"], "medium", "income", "income", "bond_proxy", "duration_bucket:muni_intermediate", ["rates_duration", "municipal_spreads"], "monthly_liquidity", "neutral", "proxy_required", "public", "North America", "notional_usd"),
        _bp("c", "agency_mbs_proxy", "Agency MBS Proxy", "AMBS", "fixed_income", "fixed_income", "fixed income", "mortgage backed securities", 430000, ["rates sensitivity", "cash generation"], "medium", "income", "income", "bond_proxy", "duration_bucket:mortgage", ["rates_duration", "mortgage_spread"], "monthly_liquidity", "neutral", "proxy_required", "public", "North America", "notional_usd"),
        _bp("c", "preferred_income_etf", "Preferred Income ETF", "PRFD", "etf", "fixed_income", "financials", "preferred securities", 335000, ["cash generation", "rates sensitivity"], "medium", "income", "income", "etf_proxy", "lookthrough_proxy:preferreds", ["credit_spreads", "rates_duration"], "daily_liquidity", "value", "none", "public", "North America", "shares"),
        _bp("c", "floating_rate_credit_etf", "Floating Rate Credit ETF", "FLRT", "etf", "fixed_income", "fixed income", "floating-rate loans", 475000, ["cash generation", "rates sensitivity"], "medium", "income", "income", "etf_proxy", "lookthrough_proxy:floating_rate_credit", ["credit_spreads", "short_rates"], "daily_liquidity", "neutral", "none", "public", "North America", "shares"),
        _bp("c", "public_direct_lending_bdc", "Public Direct Lending BDC", "BDCI", "public_equity", "private_credit", "financials", "business development company", 290000, ["cash generation", "private-market liquidity", "rates sensitivity"], "medium", "income", "income", "direct_price", "public_private_credit_proxy", ["credit_spreads", "private_credit"], "liquid", "value", "proxy_classification", "public", "North America", "shares"),
        _bp("c", "pipeline_cash_yield", "Pipeline Cash Yield", "PIPE", "public_equity", "commodities_energy", "energy", "midstream energy", 360000, ["cash generation", "energy bottlenecks", "inflation sensitivity"], "high", "income", "income", "direct_price", "direct_public_equity", ["energy", "inflation"], "liquid", "value", "none", "public", "North America", "shares"),
        _bp("c", "covered_call_income_etf", "Covered Call Income ETF", "CALL", "etf", "etf", "multi-sector", "covered call ETF", 310000, ["cash generation", "growth/value"], "medium", "income", "income", "etf_proxy", "lookthrough_proxy:covered_call", ["equity_income", "volatility"], "daily_liquidity", "value", "proxy_required", "public", "North America", "shares"),
        _bp("c", "reit_income_etf", "REIT Income ETF", "RINC", "etf", "real_estate", "real estate", "real estate income", 260000, ["cash generation", "rates sensitivity", "inflation sensitivity"], "medium", "income", "income", "etf_proxy", "lookthrough_proxy:reit_income", ["rates_duration", "real_assets"], "daily_liquidity", "value", "none", "public", "North America", "shares"),
        _bp("c", "private_credit_income_fund", "Private Credit Income Fund", "PCIF", "private_credit", "private_credit", "private credit", "direct lending", 540000, ["private-market liquidity", "cash generation", "data confidence / valuation issue"], "low", "income", "income", "manager_mark", "private_credit_proxy:direct_lending", ["credit_spreads", "private_credit"], "quarterly_liquidity", "value", "stale_private_mark", "private", "North America", "interest", human=True, flags=["stale_private_mark"]),
        _bp("c", "income_sleeve_cash", "Income Sleeve Cash Reserve", "MMCI", "money_market", "cash_money_market", "cash", "money market", 180000, ["USD exposure", "cash generation", "defensive ballast"], "high", "cash", "cash_buffer", "cash_treatment", "cash_like", ["cash"], "daily_liquidity", "neutral", "none", "cash", "North America", "shares"),
        # Manager D: Private Markets / Real Assets
        _bp("d", "northstar_ai_growth_fund", "Northstar AI Growth Fund LP", "NAGF", "private_equity", "private_equity", "private equity", "growth buyout", 1260000, ["AI infrastructure", "private-market liquidity", "opaque/private marks", "data confidence / valuation issue"], "low", "private_growth", "none", "manager_mark", "private_equity_proxy:growth", ["ai_private_growth", "private_liquidity"], "illiquid", "growth", "stale_private_mark", "private", "North America", "interest", human=True, flags=["stale_private_mark", "missing_lookthrough"]),
        _bp("d", "venture_ai_infrastructure_fund", "Venture AI Infrastructure Fund", "VAIF", "private_equity", "private_equity", "venture capital", "AI infrastructure venture", 740000, ["AI infrastructure", "data center power demand", "private-market liquidity", "opaque/private marks"], "low", "venture_growth", "none", "manager_mark", "private_equity_proxy:venture_ai", ["ai_private_growth", "venture_beta"], "illiquid", "growth", "opaque_private_mark", "private", "North America", "interest", human=True, flags=["opaque_private_mark", "missing_lookthrough"]),
        _bp("d", "secondary_pe_fund", "Secondary PE Fund", "SPEF", "private_equity", "private_equity", "private equity", "secondary fund", 690000, ["private-market liquidity", "growth/value", "opaque/private marks"], "medium", "private_balanced", "distribution", "manager_mark", "private_equity_proxy:secondary", ["private_equity", "liquidity_discount"], "illiquid", "balanced", "private_mark", "private", "Global", "interest", flags=["private_mark"]),
        _bp("d", "private_credit_sidecar", "Private Credit Sidecar", "PCSC", "private_credit", "private_credit", "private credit", "asset-backed lending", 580000, ["private-market liquidity", "cash generation", "rates sensitivity"], "medium", "private_income", "income", "manager_mark", "private_credit_proxy:asset_backed", ["credit_spreads", "private_credit"], "quarterly_liquidity", "value", "private_mark", "private", "North America", "interest", flags=["private_mark"]),
        _bp("d", "asset_backed_credit_fund", "Asset-Backed Credit Fund", "ABCF", "private_credit", "private_credit", "private credit", "asset-backed credit", 490000, ["cash generation", "rates sensitivity", "private-market liquidity"], "medium", "private_income", "income", "manager_mark", "private_credit_proxy:asset_backed", ["credit_spreads", "asset_backed_credit"], "quarterly_liquidity", "value", "private_mark", "private", "North America", "interest", flags=["private_mark"]),
        _bp("d", "industrial_logistics_real_estate", "Industrial Logistics Real Estate Fund", "ILRE", "real_estate", "real_estate", "real estate", "industrial logistics", 820000, ["inflation sensitivity", "private-market liquidity", "cash generation"], "medium", "real_asset_income", "income", "manager_mark", "real_asset_proxy:industrial", ["real_assets", "rates_duration"], "illiquid", "value", "private_mark", "private", "North America", "interest", flags=["private_mark"]),
        _bp("d", "multifamily_real_estate_fund", "Multifamily Real Estate Fund", "MFRE", "real_estate", "real_estate", "real estate", "multifamily", 510000, ["inflation sensitivity", "rates sensitivity", "private-market liquidity"], "medium", "real_asset_income", "income", "manager_mark", "real_asset_proxy:multifamily", ["real_assets", "rates_duration"], "illiquid", "value", "private_mark", "private", "North America", "interest", flags=["private_mark"]),
        _bp("d", "data_center_development_jv", "Data Center Development JV", "DCDV", "data_center_investment", "data_center_investment", "real assets", "data center development", 940000, ["AI infrastructure", "data center power demand", "energy bottlenecks", "private-market liquidity", "opaque/private marks"], "low", "private_growth", "none", "private_mark", "data_center_proxy:development", ["data_center_power", "energy", "private_liquidity"], "illiquid", "growth", "human_review", "private", "North America", "interest", human=True, flags=["stale_private_mark", "energy_input_required"]),
        _bp("d", "power_campus_preferred", "Power Campus Preferred Equity", "PCPE", "data_center_investment", "data_center_investment", "real assets", "power campus preferred", 455000, ["data center power demand", "energy bottlenecks", "cash generation", "private-market liquidity"], "low", "private_income", "income", "private_mark", "data_center_proxy:power_campus", ["energy", "power_grid", "private_credit"], "illiquid", "value", "human_review", "private", "North America", "interest", human=True, flags=["private_mark", "energy_input_required"]),
        _bp("d", "fiber_interconnect_infra_lp", "Fiber Interconnect Infrastructure LP", "FIIL", "data_center_investment", "data_center_investment", "infrastructure", "fiber and interconnect", 390000, ["AI infrastructure", "data center power demand", "private-market liquidity"], "medium", "real_asset_growth", "distribution", "manager_mark", "infrastructure_proxy:fiber", ["data_center_power", "infrastructure"], "illiquid", "balanced", "private_mark", "private", "North America", "interest", flags=["private_mark"]),
        _bp("d", "renewable_power_infra_lp", "Renewable Power Infrastructure LP", "RPIL", "real_estate", "real_estate", "infrastructure", "renewable power", 470000, ["energy bottlenecks", "inflation sensitivity", "cash generation"], "medium", "real_asset_income", "income", "manager_mark", "real_asset_proxy:power", ["energy", "inflation"], "illiquid", "value", "private_mark", "private", "North America", "interest", flags=["private_mark"]),
        _bp("d", "data_center_land_option", "Data Center Land Option", "DCLO", "option_like", "option_like", "real assets", "land option", 185000, ["data center power demand", "energy bottlenecks", "data confidence / valuation issue"], "unknown", "option_like", "none", "simple_option_model", "underlying:data_center_land", ["data_center_power", "volatility", "rates_duration"], "illiquid", "growth", "human_review", "private", "North America", "notional_usd", human=True, flags=["human_review_required", "complex_terms"]),
        _bp("d", "opaque_manager_level_private_book", "Opaque Manager-Level Private Book", "OMPB", "opaque_manager_level", "opaque_manager_level", "private markets", "manager composite", 610000, ["opaque/private marks", "private-market liquidity", "data confidence / valuation issue"], "unknown", "opaque_private", "unknown", "manager_mark", "manager_composite_proxy:private_book", ["private_liquidity", "human_review"], "illiquid", "private/opaque", "human_review", "private", "Global", "interest", human=True, flags=["opaque_manager_mark", "missing_lookthrough", "missing_cost_basis"]),
        _bp("d", "private_mark_placeholder", "Private Mark Placeholder Position", "PMPD", "opaque_manager_level", "opaque_manager_level", "private markets", "manual placeholder", 125000, ["opaque/private marks", "data confidence / valuation issue"], "unknown", "opaque_private", "unknown", "manager_mark", "human_review_required", ["human_review"], "illiquid", "private/opaque", "human_review", "private", "Global", "interest", human=True, flags=["human_review_required", "missing_cost_basis"]),
        # Manager E: Liquidity / Defensive
        _bp("e", "treasury_bill_ladder", "Treasury Bill Ladder", "TBIL", "fixed_income", "fixed_income", "fixed income", "treasury bills", 1340000, ["defensive ballast", "USD exposure", "rates sensitivity"], "high", "cash", "cash_buffer", "bond_proxy", "duration_bucket:short_treasury", ["short_rates", "usd_liquidity"], "daily_liquidity", "neutral", "none", "public", "North America", "notional_usd"),
        _bp("e", "government_money_market", "Government Money Market Fund", "GMMF", "money_market", "cash_money_market", "cash", "government money market", 980000, ["defensive ballast", "USD exposure", "cash generation"], "high", "cash", "cash_buffer", "cash_treatment", "cash_like", ["cash", "short_rates"], "daily_liquidity", "neutral", "none", "cash", "North America", "shares"),
        _bp("e", "short_treasury_etf", "Short Treasury ETF", "STSY", "etf", "fixed_income", "fixed income", "short treasury ETF", 725000, ["defensive ballast", "rates sensitivity", "USD exposure"], "high", "cash", "income", "etf_proxy", "duration_bucket:short_treasury", ["short_rates"], "daily_liquidity", "neutral", "none", "public", "North America", "shares"),
        _bp("e", "short_duration_ig_bond", "Short Duration IG Bond ETF", "SDIG", "etf", "fixed_income", "fixed income", "short investment grade credit", 540000, ["defensive ballast", "rates sensitivity", "cash generation"], "high", "income", "income", "etf_proxy", "duration_bucket:short_credit", ["short_rates", "credit_spreads"], "daily_liquidity", "neutral", "none", "public", "North America", "shares"),
        _bp("e", "minimum_volatility_equity", "Minimum Volatility Equity ETF", "MVOL", "etf", "etf", "multi-sector", "minimum volatility ETF", 420000, ["defensive ballast", "growth/value"], "high", "defensive_equity", "none", "etf_proxy", "lookthrough_proxy:min_vol_equity", ["broad_equity", "low_vol"], "daily_liquidity", "balanced", "none", "public", "North America", "shares"),
        _bp("e", "gold_defensive_etf", "Gold Defensive ETF", "GLDX", "etf", "commodities_energy", "commodities", "gold ETF", 300000, ["defensive ballast", "inflation sensitivity", "USD exposure"], "high", "real_asset", "none", "etf_proxy", "commodity_proxy:gold", ["gold", "usd"], "daily_liquidity", "neutral", "none", "public", "Global", "shares"),
        _bp("e", "municipal_cash_reserve", "Municipal Cash Reserve", "MCAS", "money_market", "cash_money_market", "cash", "municipal cash", 260000, ["defensive ballast", "cash generation", "USD exposure"], "high", "cash", "cash_buffer", "cash_treatment", "cash_like", ["cash", "short_rates"], "daily_liquidity", "neutral", "none", "cash", "North America", "shares"),
        _bp("e", "inflation_linked_short_note", "Inflation-Linked Short Note", "ILSN", "fixed_income", "fixed_income", "fixed income", "short TIPS", 345000, ["inflation sensitivity", "rates sensitivity", "defensive ballast"], "high", "cash", "income", "bond_proxy", "duration_bucket:short_tips", ["inflation", "short_rates"], "monthly_liquidity", "neutral", "none", "public", "North America", "notional_usd"),
        _bp("e", "operating_cash_usd", "Operating Cash USD", "CASH", "cash", "cash_money_market", "cash", "operating cash", 510000, ["defensive ballast", "USD exposure"], "high", "cash", "cash_buffer", "cash_treatment", "cash_like", ["cash"], "daily_liquidity", "neutral", "none", "cash", "North America", "notional_usd"),
        _bp("e", "defensive_quality_etf", "Defensive Quality ETF", "DQET", "etf", "etf", "multi-sector", "defensive quality ETF", 295000, ["defensive ballast", "growth/value"], "high", "defensive_equity", "dividend", "etf_proxy", "lookthrough_proxy:defensive_quality", ["quality_factor", "low_vol"], "daily_liquidity", "balanced", "none", "public", "North America", "shares"),
        # Manager F: Opportunistic Macro / Hedge
        _bp("f", "eurusd_forward_exposure", "EUR/USD Forward Exposure", "EURF", "fx_exposure", "fx", "currency", "FX forward", 420000, ["USD exposure", "data confidence / valuation issue"], "medium", "macro", "none", "fx_rate", "fx_pair:EURUSD", ["eurusd", "usd"], "weekly_liquidity", "neutral", "proxy_required", "derivative", "Europe", "notional_usd"),
        _bp("f", "jpy_defensive_hedge", "JPY Defensive Hedge", "JPYH", "fx_exposure", "fx", "currency", "FX hedge", 360000, ["USD exposure", "defensive ballast"], "medium", "macro", "none", "fx_rate", "fx_pair:USDJPY", ["jpy_safe_haven", "usd"], "weekly_liquidity", "neutral", "proxy_required", "derivative", "Japan", "notional_usd"),
        _bp("f", "usd_strength_proxy", "USD Strength Proxy", "USDX", "etf", "fx", "currency", "USD basket ETF", 310000, ["USD exposure", "defensive ballast"], "high", "macro", "none", "etf_proxy", "currency_proxy:usd_basket", ["usd"], "daily_liquidity", "neutral", "none", "public", "Global", "shares"),
        _bp("f", "commodity_basket_fund", "Commodity Basket Fund", "COMB", "etf", "commodities_energy", "commodities", "commodity basket", 470000, ["energy bottlenecks", "inflation sensitivity"], "high", "real_asset", "none", "etf_proxy", "commodity_proxy:basket", ["commodities", "inflation"], "daily_liquidity", "neutral", "none", "public", "Global", "shares"),
        _bp("f", "wti_energy_exposure", "WTI Energy Exposure", "WTIE", "commodity", "commodities_energy", "energy", "oil-linked exposure", 280000, ["energy bottlenecks", "inflation sensitivity"], "medium", "real_asset", "none", "commodity_proxy", "commodity_proxy:wti", ["oil", "energy"], "weekly_liquidity", "neutral", "proxy_required", "derivative", "Global", "notional_usd"),
        _bp("f", "copper_power_demand_etf", "Copper Power Demand ETF", "CPWR", "etf", "commodities_energy", "commodities", "copper ETF", 235000, ["data center power demand", "energy bottlenecks", "inflation sensitivity"], "high", "real_asset", "none", "etf_proxy", "commodity_proxy:copper", ["copper", "power_grid"], "daily_liquidity", "neutral", "none", "public", "Global", "shares"),
        _bp("f", "uranium_power_supply_etf", "Uranium Power Supply ETF", "URAN", "etf", "commodities_energy", "energy", "uranium ETF", 220000, ["data center power demand", "energy bottlenecks", "inflation sensitivity"], "medium", "real_asset", "none", "etf_proxy", "commodity_proxy:uranium", ["uranium", "power_grid"], "daily_liquidity", "neutral", "proxy_required", "public", "Global", "shares"),
        _bp("f", "bitcoin_synthetic_trust", "Bitcoin Synthetic Trust", "BTCX", "crypto", "crypto", "digital assets", "bitcoin exposure", 410000, ["crypto risk", "growth/value", "data confidence / valuation issue"], "medium", "macro", "none", "crypto_price", "crypto_proxy:bitcoin", ["bitcoin", "crypto"], "daily_liquidity", "growth", "proxy_required", "public", "Global", "shares"),
        _bp("f", "ethereum_synthetic_trust", "Ethereum Synthetic Trust", "ETHX", "crypto", "crypto", "digital assets", "ethereum exposure", 245000, ["crypto risk", "AI infrastructure", "data confidence / valuation issue"], "medium", "macro", "none", "crypto_price", "crypto_proxy:ethereum", ["ethereum", "crypto"], "daily_liquidity", "growth", "proxy_required", "public", "Global", "shares"),
        _bp("f", "macro_overlay_manager_book", "Macro Overlay Manager Book", "MOMB", "opaque_manager_level", "opaque_manager_level", "macro", "manager overlay", 330000, ["opaque/private marks", "data confidence / valuation issue", "USD exposure"], "unknown", "macro", "unknown", "manager_mark", "manager_composite_proxy:macro_overlay", ["fx", "rates", "volatility"], "monthly_liquidity", "private/opaque", "human_review", "opaque", "Global", "notional_usd", human=True, flags=["opaque_manager_mark", "missing_lookthrough"]),
        _bp("f", "rates_volatility_collar", "Rates Volatility Collar", "RVOL", "option_like", "option_like", "structured products", "rates option", 210000, ["rates sensitivity", "defensive ballast", "data confidence / valuation issue"], "low", "macro", "none", "simple_option_model", "underlying:rates_proxy", ["rates_duration", "volatility"], "monthly_liquidity", "neutral", "model_required", "derivative", "North America", "notional_usd", human=True, flags=["complex_terms"]),
        _bp("f", "ai_chip_downside_put_spread", "AI Chip Downside Put Spread", "AIPS", "option_like", "option_like", "structured products", "equity index option", 155000, ["AI infrastructure", "semiconductors", "manager overlap", "data confidence / valuation issue"], "low", "macro", "none", "simple_option_model", "underlying_basket:semiconductors", ["semiconductor_beta", "volatility"], "monthly_liquidity", "neutral", "model_required", "derivative", "North America", "notional_usd", human=True, flags=["complex_terms"]),
    ]
    return rows


def _bp(
    manager_code: str,
    instrument_slug: str,
    display_name: str,
    synthetic_identifier: str,
    instrument_type: str,
    asset_class: str,
    sector: str,
    industry: str,
    target_value: float,
    themes: list[str],
    valuation_confidence: str,
    exposure_style: str,
    cash_generation_role: str,
    valuation_method_hint: str,
    proxy_mapping_hint: str,
    scenario_exposure_hints: list[str],
    liquidity_bucket: str,
    value_growth_style: str,
    data_issue_category: str,
    public_private: str,
    geography: str,
    quantity_unit: str,
    human: bool = False,
    flags: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "manager_code": manager_code,
        "instrument_slug": instrument_slug,
        "position_slug": instrument_slug,
        "display_name": display_name,
        "synthetic_identifier": synthetic_identifier,
        "instrument_type": instrument_type,
        "asset_class": asset_class,
        "sector": sector,
        "industry": industry,
        "target_value": target_value,
        "themes": themes,
        "valuation_confidence": valuation_confidence,
        "exposure_style": exposure_style,
        "cash_generation_role": cash_generation_role,
        "valuation_method_hint": valuation_method_hint,
        "proxy_mapping_hint": proxy_mapping_hint,
        "scenario_exposure_hints": scenario_exposure_hints,
        "liquidity_bucket": liquidity_bucket,
        "value_growth_style": value_growth_style,
        "data_issue_category": data_issue_category,
        "public_private": public_private,
        "geography": geography,
        "quantity_unit": quantity_unit,
        "lookthrough_status": _lookthrough_status(public_private, data_issue_category, flags or []),
        "human_review_required": human,
        "data_quality_flags": flags or [],
        "position_story_tags": _story_tags(themes, data_issue_category),
        "valuation_notes": _valuation_notes(instrument_type, valuation_method_hint, proxy_mapping_hint),
    }


def _lookthrough_status(public_private: str, data_issue_category: str, flags: list[str]) -> str:
    if "missing_lookthrough" in flags:
        return "missing"
    if public_private in {"private", "opaque"}:
        return "manager_summary"
    if data_issue_category in {"proxy_required", "model_required"}:
        return "partial"
    return "available"


def _story_tags(themes: list[str], data_issue_category: str) -> list[str]:
    tags = []
    if "manager overlap" in themes:
        tags.append("manager_overlap")
    if "AI infrastructure" in themes or "semiconductors" in themes:
        tags.append("ai_chip_growth")
    if "defensive ballast" in themes:
        tags.append("liquidity_ballast")
    if data_issue_category not in {"none", ""}:
        tags.append("data_confidence_review")
    return tags


def _valuation_notes(instrument_type: str, valuation_method_hint: str, proxy_mapping_hint: str) -> str:
    return (
        f"Future valuation should use {valuation_method_hint} for {instrument_type}; "
        f"state requirement declared through {proxy_mapping_hint}."
    )


def _quantity_for_position(blueprint: dict[str, Any], value: float, rng: random.Random) -> float:
    if blueprint["quantity_unit"] == "shares":
        synthetic_unit_reference = rng.uniform(18.0, 410.0)
        return round(value / synthetic_unit_reference, 3)
    if blueprint["quantity_unit"] == "interest":
        return round(rng.uniform(0.35, 4.5), 4)
    if blueprint["quantity_unit"] == "notional_usd":
        return round(value, 2)
    return round(value, 2)


def _transaction_type_for_position(position: dict[str, Any], index: int) -> str:
    instrument_type = position["instrument_type"]
    if position["human_review_required"] and instrument_type in {"private_equity", "private_credit", "real_estate", "data_center_investment", "opaque_manager_level"}:
        return "mark_update"
    if position["classifications"]["cash_generation_role"] in {"income", "distribution"}:
        return "income" if index % 2 else "distribution"
    if instrument_type in {"cash", "money_market"}:
        return "income"
    if instrument_type in {"private_equity", "private_credit", "real_estate", "data_center_investment"}:
        return "distribution" if index % 3 == 0 else "contribution"
    return "sell" if index % 11 == 0 else "buy"


def _transaction_amounts(position: dict[str, Any], txn_type: str, rng: random.Random) -> tuple[float, float | None, float | None]:
    value = float(position["current_reported_value"])
    if txn_type == "buy":
        notional = round(value * rng.uniform(0.015, 0.045), 2)
        quantity = round(position["quantity"] * rng.uniform(0.015, 0.045), 4) if position["quantity_unit"] == "shares" else None
        return -notional, quantity, notional
    if txn_type == "sell":
        notional = round(value * rng.uniform(0.012, 0.035), 2)
        quantity = round(-position["quantity"] * rng.uniform(0.012, 0.035), 4) if position["quantity_unit"] == "shares" else None
        return notional, quantity, -notional
    if txn_type == "income":
        income = round(value * rng.uniform(0.002, 0.012), 2)
        return income, 0.0, 0.0
    if txn_type == "distribution":
        distribution = round(value * rng.uniform(0.01, 0.035), 2)
        return distribution, 0.0, -distribution
    if txn_type == "contribution":
        contribution = round(value * rng.uniform(0.025, 0.075), 2)
        return -contribution, 0.0, contribution
    if txn_type == "mark_update":
        adjustment = round(value * rng.uniform(-0.035, 0.045), 2)
        return 0.0, 0.0, adjustment
    return 0.0, 0.0, 0.0


def _transaction_description(position: dict[str, Any], txn_type: str) -> str:
    if txn_type == "mark_update":
        return f"Synthetic manager mark update for {position['display_name']}."
    if txn_type == "income":
        return f"Synthetic income event for {position['display_name']}."
    if txn_type == "distribution":
        return f"Synthetic distribution event for {position['display_name']}."
    if txn_type == "contribution":
        return f"Synthetic capital contribution or private funding event for {position['display_name']}."
    return f"Synthetic {txn_type} activity for {position['display_name']}."


def _quality_flag_message(position: dict[str, Any], flag: str) -> str:
    messages = {
        "stale_private_mark": "Private or manager mark is intentionally stale for confidence review.",
        "opaque_private_mark": "Private mark is intentionally opaque and lacks full look-through.",
        "opaque_manager_mark": "Manager-level composite requires advisor review before client-facing use.",
        "missing_lookthrough": "Look-through detail is not available in the synthetic universe.",
        "missing_cost_basis": "Cost basis is intentionally missing for demo validation.",
        "complex_terms": "Option-like or structured terms require future model inputs.",
        "energy_input_required": "Energy/power inputs must be supplied by the future market-state generator.",
        "valuation_confidence_issue": "Position carries medium, low, or unknown valuation confidence.",
        "human_review_required": "Advisor or data review is required before relying on this position.",
    }
    return messages.get(flag, f"Synthetic data quality flag on {position['display_name']}: {flag}.")


def _human_review_reason(position: dict[str, Any]) -> str:
    if "complex_terms" in position["data_quality_flags"]:
        return "Complex option-like or structured exposure requires future model input review."
    if "opaque_manager_mark" in position["data_quality_flags"]:
        return "Opaque manager-level mark lacks sufficient look-through for automatic interpretation."
    if "stale_private_mark" in position["data_quality_flags"]:
        return "Stale private mark requires review before downstream valuation confidence claims."
    return "Position is marked for human review by the synthetic generator."


def _manager_overlap_summary(positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    instrument_to_positions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for position in positions:
        instrument_to_positions[position["instrument_id"]].append(position)
    examples = []
    for instrument_id, rows in sorted(instrument_to_positions.items()):
        manager_ids = sorted({row["manager_id"] for row in rows})
        if len(manager_ids) >= 2:
            examples.append(
                {
                    "instrument_id": instrument_id,
                    "display_name": rows[0]["display_name"],
                    "manager_ids": manager_ids,
                    "position_ids": [row["position_id"] for row in rows],
                    "themes": sorted({theme for row in rows for theme in row.get("themes", [])}),
                }
            )
    return examples


def _validate_history_dates(universe: dict[str, Any], transactions: list[dict[str, Any]], warnings: list[dict[str, str]]) -> None:
    if not transactions:
        _add_issue(warnings, "NO_TRANSACTIONS", "transactions", "No transactions supplied")
        return
    start = date.fromisoformat(universe["history_start_date"])
    end = date.fromisoformat(universe["history_end_date"])
    dates = [date.fromisoformat(transaction["date"]) for transaction in transactions if transaction.get("date")]
    if min(dates) > start:
        _add_issue(warnings, "HISTORY_START_NOT_USED", "transactions", "Earliest transaction is after history_start_date")
    if max(dates) < end:
        _add_issue(warnings, "HISTORY_END_NOT_USED", "transactions", "Latest transaction is before history_end_date")
    span = (max(dates) - min(dates)).days
    if span < 85:
        _add_issue(warnings, "SHORT_TRANSACTION_HISTORY", "transactions", f"Transaction date span is only {span} days")


def _validate_no_real_data_markers(universe: dict[str, Any], errors: list[dict[str, str]]) -> None:
    for path, value in _walk_strings(universe):
        lowered = value.lower()
        for marker in REAL_DATA_MARKERS:
            if marker in lowered:
                _add_issue(errors, "REAL_DATA_MARKER_DETECTED", path, f"String contains prohibited marker: {marker}")


def _walk_strings(value: Any, path: str = "universe") -> list[tuple[str, str]]:
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


def _collect_unique_ids(records: list[dict[str, Any]], id_field: str, section: str, errors: list[dict[str, str]]) -> set[str]:
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict) or id_field not in record:
            _add_issue(errors, "MISSING_ID", f"{section}[{index}]", f"Missing ID field: {id_field}")
            continue
        record_id = str(record[id_field])
        if record_id in seen:
            _add_issue(errors, "DUPLICATE_ID", record_id, f"Duplicate {id_field} in {section}")
        seen.add(record_id)
    return seen


def _has_any_flag(position: dict[str, Any], flags: set[str]) -> bool:
    position_flags = set(position.get("data_quality_flags", []))
    if position.get("human_review_required"):
        position_flags.add("human_review_required")
    return bool(position_flags & flags)


def _date_span(dates: list[str]) -> int:
    parsed = [date.fromisoformat(value) for value in dates]
    return (max(parsed) - min(parsed)).days


def _list(value: Any) -> list[dict[str, Any]]:
    return value if isinstance(value, list) else []


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
