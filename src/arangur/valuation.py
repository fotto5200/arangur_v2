"""Simple long-only valuation for the local demo."""

from __future__ import annotations

from typing import Any

from .market_data import build_price_index, validate_market_data_for_snapshot


def calculate_valuation(snapshot: dict[str, Any], market_data: dict[str, Any]) -> dict[str, Any]:
    validation = validate_market_data_for_snapshot(market_data, snapshot)
    price_index = build_price_index(market_data)
    accounts = {account["account_id"]: account for account in snapshot["accounts"]}
    managers = {manager["manager_id"]: manager for manager in snapshot["managers"]}
    securities = {security["security_id"]: security for security in snapshot["securities"]}

    positions: list[dict[str, Any]] = []
    cash_rows: list[dict[str, Any]] = []
    account_totals: dict[str, dict[str, Any]] = {}
    manager_totals: dict[str, dict[str, Any]] = {}

    for account in snapshot["accounts"]:
        account_totals[account["account_id"]] = {
            "account_id": account["account_id"],
            "account_name": account["display_name"],
            "manager_id": account["manager_id"],
            "manager_name": managers[account["manager_id"]]["display_name"],
            "market_value": 0.0,
            "positions_market_value": 0.0,
            "cash_value": 0.0,
            "currency": account["currency"],
        }

    for manager in snapshot["managers"]:
        manager_totals[manager["manager_id"]] = {
            "manager_id": manager["manager_id"],
            "manager_name": manager["display_name"],
            "market_value": 0.0,
            "positions_market_value": 0.0,
            "cash_value": 0.0,
            "currency": snapshot["reporting_currency"],
        }

    for holding in snapshot["holdings"]:
        security = securities[holding["security_id"]]
        account = accounts[holding["account_id"]]
        manager_id = account["manager_id"]
        price = price_index.get(holding["security_id"])
        if price is None:
            continue

        market_value = _money(holding["quantity"] * price["price"])
        cost_basis = holding.get("cost_basis")
        position = {
            "holding_id": holding["holding_id"],
            "account_id": account["account_id"],
            "account_name": account["display_name"],
            "manager_id": manager_id,
            "manager_name": managers[manager_id]["display_name"],
            "security_id": security["security_id"],
            "ticker": security.get("ticker"),
            "display_name": security["display_name"],
            "quantity": holding["quantity"],
            "price": price["price"],
            "market_value": market_value,
            "currency": price["currency"],
            "valuation_date": snapshot["as_of_date"],
            "cost_basis": cost_basis,
            "unrealized_gain_loss": _money(market_value - cost_basis) if cost_basis is not None else None,
            "asset_class": security["asset_class"],
            "sector": security.get("sector"),
            "themes": security.get("themes", []),
        }
        positions.append(position)
        _add_value(account_totals[account["account_id"]], market_value, "positions_market_value")
        _add_value(manager_totals[manager_id], market_value, "positions_market_value")

    for cash in snapshot["cash_balances"]:
        account = accounts[cash["account_id"]]
        manager_id = account["manager_id"]
        cash_value = _money(cash["amount"])
        row = {
            "cash_id": cash["cash_id"],
            "account_id": account["account_id"],
            "account_name": account["display_name"],
            "manager_id": manager_id,
            "manager_name": managers[manager_id]["display_name"],
            "currency": cash["currency"],
            "amount": cash["amount"],
            "market_value": cash_value,
            "cash_type": cash.get("cash_type"),
            "valuation_date": snapshot["as_of_date"],
        }
        cash_rows.append(row)
        _add_value(account_totals[account["account_id"]], cash_value, "cash_value")
        _add_value(manager_totals[manager_id], cash_value, "cash_value")

    for total in account_totals.values():
        total["market_value"] = _money(total["positions_market_value"] + total["cash_value"])
    for total in manager_totals.values():
        total["market_value"] = _money(total["positions_market_value"] + total["cash_value"])

    positions_value = _money(sum(position["market_value"] for position in positions))
    cash_value = _money(sum(cash["market_value"] for cash in cash_rows))
    portfolio_market_value = _money(positions_value + cash_value)

    return {
        "schema_version": "valuation_result.v1",
        "snapshot_id": snapshot["snapshot_id"],
        "valuation_date": snapshot["as_of_date"],
        "reporting_currency": snapshot["reporting_currency"],
        "positions": positions,
        "cash": cash_rows,
        "account_totals": sorted(account_totals.values(), key=lambda row: row["market_value"], reverse=True),
        "manager_totals": sorted(manager_totals.values(), key=lambda row: row["market_value"], reverse=True),
        "portfolio_total": {
            "market_value": portfolio_market_value,
            "positions_market_value": positions_value,
            "cash_value": cash_value,
            "currency": snapshot["reporting_currency"],
        },
        "validation": validation,
    }


def _add_value(total: dict[str, Any], market_value: float, field: str) -> None:
    total[field] = _money(total[field] + market_value)


def _money(value: float) -> float:
    return round(float(value), 2)
