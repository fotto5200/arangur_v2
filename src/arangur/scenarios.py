"""Deterministic scenario shocks for the local demo."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


PRECEDENCE = {
    "security_id": 1,
    "ticker": 2,
    "theme": 3,
    "sector": 4,
    "asset_class": 5,
    "cash": 6,
}


def calculate_scenario_results(
    snapshot: dict[str, Any],
    valuation: dict[str, Any],
    scenario_definitions: dict[str, Any],
) -> dict[str, Any]:
    results = [
        calculate_single_scenario(snapshot, valuation, scenario)
        for scenario in scenario_definitions["scenarios"]
    ]
    return {
        "schema_version": "scenario_result_set.v1",
        "snapshot_id": snapshot["snapshot_id"],
        "valuation_date": snapshot["as_of_date"],
        "scenario_results": results,
        "validation": {"status": "valid", "errors": [], "warnings": []},
    }


def calculate_single_scenario(
    snapshot: dict[str, Any],
    valuation: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    account_impacts: dict[str, dict[str, Any]] = {}
    manager_impacts: dict[str, dict[str, Any]] = {}
    exposure_impacts: dict[str, float] = defaultdict(float)
    position_impacts: list[dict[str, Any]] = []
    cash_impacts: list[dict[str, Any]] = []

    for account in valuation["account_totals"]:
        account_impacts[account["account_id"]] = {
            "account_id": account["account_id"],
            "account_name": account["account_name"],
            "before_value": 0.0,
            "impact_value": 0.0,
            "after_value": 0.0,
        }
    for manager in valuation["manager_totals"]:
        manager_impacts[manager["manager_id"]] = {
            "manager_id": manager["manager_id"],
            "manager_name": manager["manager_name"],
            "before_value": 0.0,
            "impact_value": 0.0,
            "after_value": 0.0,
        }

    for position in valuation["positions"]:
        shock_percent, matched_rule = _match_position_rule(position, scenario)
        before_value = position["market_value"]
        impact_value = _money(before_value * shock_percent)
        after_value = _money(before_value + impact_value)
        impact = {
            "holding_id": position["holding_id"],
            "security_id": position["security_id"],
            "ticker": position.get("ticker"),
            "display_name": position["display_name"],
            "account_id": position["account_id"],
            "manager_id": position["manager_id"],
            "sector": position.get("sector"),
            "themes": position.get("themes", []),
            "before_value": before_value,
            "shock_percent": shock_percent,
            "impact_value": impact_value,
            "after_value": after_value,
            "matched_rule": matched_rule,
        }
        position_impacts.append(impact)
        _add_impact(account_impacts[position["account_id"]], before_value, impact_value)
        _add_impact(manager_impacts[position["manager_id"]], before_value, impact_value)
        exposure_impacts[position.get("asset_class") or "unclassified"] += impact_value
        if position.get("sector"):
            exposure_impacts[position["sector"]] += impact_value
        for theme in position.get("themes", []):
            exposure_impacts[theme] += impact_value

    for cash in valuation["cash"]:
        shock_percent, matched_rule = _match_cash_rule(scenario)
        before_value = cash["market_value"]
        impact_value = _money(before_value * shock_percent)
        after_value = _money(before_value + impact_value)
        impact = {
            "cash_id": cash["cash_id"],
            "account_id": cash["account_id"],
            "manager_id": cash["manager_id"],
            "before_value": before_value,
            "shock_percent": shock_percent,
            "impact_value": impact_value,
            "after_value": after_value,
            "matched_rule": matched_rule,
        }
        cash_impacts.append(impact)
        _add_impact(account_impacts[cash["account_id"]], before_value, impact_value)
        _add_impact(manager_impacts[cash["manager_id"]], before_value, impact_value)
        exposure_impacts["cash"] += impact_value

    before_total = valuation["portfolio_total"]["market_value"]
    impact_total = _money(sum(row["impact_value"] for row in position_impacts) + sum(row["impact_value"] for row in cash_impacts))
    after_total = _money(before_total + impact_total)

    return {
        "schema_version": "scenario_result.v1",
        "snapshot_id": snapshot["snapshot_id"],
        "scenario_id": scenario["scenario_id"],
        "scenario_name": scenario["scenario_name"],
        "description": scenario["description"],
        "valuation_date": snapshot["as_of_date"],
        "portfolio_before_value": before_total,
        "portfolio_after_value": after_total,
        "portfolio_impact_value": impact_total,
        "portfolio_impact_percent": round(impact_total / before_total, 6) if before_total else 0.0,
        "position_impacts": position_impacts,
        "cash_impacts": cash_impacts,
        "account_impacts": _finish_impacts(account_impacts.values()),
        "manager_impacts": _finish_impacts(manager_impacts.values()),
        "exposure_impacts": [
            {"bucket_id": key, "bucket_label": key.replace("_", " ").title(), "impact_value": _money(value)}
            for key, value in sorted(exposure_impacts.items(), key=lambda item: abs(item[1]), reverse=True)
        ],
        "caveat": "Scenario shocks are deterministic demo approximations, not forecasts or investment advice.",
        "validation": {"status": "valid", "errors": [], "warnings": []},
    }


def _match_position_rule(position: dict[str, Any], scenario: dict[str, Any]) -> tuple[float, str]:
    matches: list[tuple[int, int, dict[str, Any]]] = []
    for index, rule in enumerate(scenario["shock_rules"]):
        if _rule_matches_position(rule, position):
            matches.append((PRECEDENCE[rule["match_type"]], index, rule))
    if not matches:
        return scenario.get("default_shock", 0), "default"
    _, _, rule = sorted(matches, key=lambda item: (item[0], item[1]))[0]
    return rule["shock_percent"], f"{rule['match_type']}:{rule['match_value']}"


def _match_cash_rule(scenario: dict[str, Any]) -> tuple[float, str]:
    for rule in scenario["shock_rules"]:
        if rule["match_type"] == "cash":
            return rule["shock_percent"], f"cash:{rule['match_value']}"
    return scenario.get("default_shock", 0), "default"


def _rule_matches_position(rule: dict[str, Any], position: dict[str, Any]) -> bool:
    match_type = rule["match_type"]
    match_value = str(rule["match_value"]).lower()
    if match_type == "cash":
        return False
    if match_type == "security_id":
        return str(position["security_id"]).lower() == match_value
    if match_type == "ticker":
        return str(position.get("ticker", "")).lower() == match_value
    if match_type == "asset_class":
        return str(position.get("asset_class", "")).lower() == match_value
    if match_type == "sector":
        return str(position.get("sector", "")).lower() == match_value
    if match_type == "theme":
        return match_value in {str(theme).lower() for theme in position.get("themes", [])}
    return False


def _add_impact(row: dict[str, Any], before_value: float, impact_value: float) -> None:
    row["before_value"] = _money(row["before_value"] + before_value)
    row["impact_value"] = _money(row["impact_value"] + impact_value)
    row["after_value"] = _money(row["before_value"] + row["impact_value"])


def _finish_impacts(rows: Any) -> list[dict[str, Any]]:
    return sorted(
        (
            {
                **row,
                "impact_percent": round(row["impact_value"] / row["before_value"], 6) if row["before_value"] else 0.0,
            }
            for row in rows
        ),
        key=lambda row: abs(row["impact_value"]),
        reverse=True,
    )


def _money(value: float) -> float:
    return round(float(value), 2)
