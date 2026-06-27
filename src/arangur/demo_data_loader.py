"""Load and validate local synthetic demo inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DemoDataError(ValueError):
    """Raised when demo input files are missing or structurally invalid."""


def load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise DemoDataError(f"Missing demo input file: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise DemoDataError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise DemoDataError(f"Expected JSON object in {path}")
    return data


def load_demo_portfolio(data_dir: Path) -> dict[str, Any]:
    data = load_json_file(data_dir / "demo_portfolio.json")
    errors = validate_demo_portfolio(data)
    if errors:
        raise DemoDataError(_format_errors("demo_portfolio.json", errors))
    return data


def load_market_data_fixture(data_dir: Path) -> dict[str, Any]:
    data = load_json_file(data_dir / "market_data_fixture.json")
    errors = validate_market_data_fixture(data)
    if errors:
        raise DemoDataError(_format_errors("market_data_fixture.json", errors))
    return data


def load_scenario_definitions(data_dir: Path) -> dict[str, Any]:
    data = load_json_file(data_dir / "scenario_definitions.json")
    errors = validate_scenario_definitions(data)
    if errors:
        raise DemoDataError(_format_errors("scenario_definitions.json", errors))
    return data


def load_demo_inputs(data_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        load_demo_portfolio(data_dir),
        load_market_data_fixture(data_dir),
        load_scenario_definitions(data_dir),
    )


def validate_demo_portfolio(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require_top_level(data, ["schema_version", "metadata", "managers", "accounts", "securities", "holdings", "cash_balances"], errors)

    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        _require_fields(
            metadata,
            [
                "dataset_id",
                "dataset_label",
                "is_synthetic",
                "valuation_date",
                "reporting_currency",
                "portfolio_owner_label",
            ],
            "metadata",
            errors,
        )
        if metadata.get("is_synthetic") is not True:
            errors.append("metadata.is_synthetic must be true")
    else:
        errors.append("metadata must be an object")

    _validate_required_array(data, "managers", errors)
    _validate_required_array(data, "accounts", errors)
    _validate_required_array(data, "securities", errors)
    _validate_required_array(data, "holdings", errors)
    _validate_required_array(data, "cash_balances", errors)

    for index, manager in enumerate(data.get("managers", [])):
        _require_fields(manager, ["manager_id", "manager_name"], f"managers[{index}]", errors)
    for index, account in enumerate(data.get("accounts", [])):
        _require_fields(account, ["account_id", "account_name", "manager_id", "account_type", "currency"], f"accounts[{index}]", errors)
    for index, security in enumerate(data.get("securities", [])):
        _require_fields(
            security,
            ["security_id", "name", "security_type", "currency", "asset_class"],
            f"securities[{index}]",
            errors,
        )
    for index, holding in enumerate(data.get("holdings", [])):
        _require_fields(holding, ["holding_id", "account_id", "security_id", "quantity"], f"holdings[{index}]", errors)
        if isinstance(holding, dict) and holding.get("quantity", 0) < 0:
            errors.append(f"holdings[{index}].quantity must be non-negative")
    for index, cash in enumerate(data.get("cash_balances", [])):
        _require_fields(cash, ["cash_id", "account_id", "currency", "amount"], f"cash_balances[{index}]", errors)
        if isinstance(cash, dict) and cash.get("amount", 0) < 0:
            errors.append(f"cash_balances[{index}].amount must be non-negative")

    return errors


def validate_market_data_fixture(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require_top_level(data, ["schema_version", "fixture_id", "valuation_date", "currency", "is_synthetic", "prices"], errors)
    if data.get("is_synthetic") is not True:
        errors.append("is_synthetic must be true")
    _validate_required_array(data, "prices", errors)
    for index, price in enumerate(data.get("prices", [])):
        _require_fields(price, ["security_id", "price", "currency", "price_date"], f"prices[{index}]", errors)
        if isinstance(price, dict) and price.get("price", 0) < 0:
            errors.append(f"prices[{index}].price must be non-negative")
    return errors


def validate_scenario_definitions(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require_top_level(data, ["schema_version", "fixture_id", "valuation_date", "is_synthetic", "scenarios"], errors)
    if data.get("is_synthetic") is not True:
        errors.append("is_synthetic must be true")
    _validate_required_array(data, "scenarios", errors)
    for index, scenario in enumerate(data.get("scenarios", [])):
        _require_fields(
            scenario,
            ["scenario_id", "scenario_name", "scenario_date", "description", "default_shock", "is_synthetic", "shock_rules"],
            f"scenarios[{index}]",
            errors,
        )
        if isinstance(scenario, dict) and scenario.get("is_synthetic") is not True:
            errors.append(f"scenarios[{index}].is_synthetic must be true")
        if isinstance(scenario, dict):
            _validate_required_array(scenario, "shock_rules", errors, context=f"scenarios[{index}]")
            for rule_index, rule in enumerate(scenario.get("shock_rules", [])):
                _require_fields(
                    rule,
                    ["match_type", "match_value", "shock_percent"],
                    f"scenarios[{index}].shock_rules[{rule_index}]",
                    errors,
                )
    return errors


def _require_top_level(data: dict[str, Any], fields: list[str], errors: list[str]) -> None:
    for field in fields:
        if field not in data:
            errors.append(f"missing top-level field: {field}")


def _require_fields(record: Any, fields: list[str], context: str, errors: list[str]) -> None:
    if not isinstance(record, dict):
        errors.append(f"{context} must be an object")
        return
    for field in fields:
        if field not in record:
            errors.append(f"{context} missing required field: {field}")


def _validate_required_array(data: dict[str, Any], field: str, errors: list[str], context: str | None = None) -> None:
    owner = f"{context}.{field}" if context else field
    value = data.get(field)
    if not isinstance(value, list):
        errors.append(f"{owner} must be an array")
    elif not value and field not in {"transactions"}:
        errors.append(f"{owner} must not be empty")


def _format_errors(filename: str, errors: list[str]) -> str:
    lines = [f"Demo input validation failed for {filename}:"]
    lines.extend(f"- {error}" for error in errors)
    return "\n".join(lines)
