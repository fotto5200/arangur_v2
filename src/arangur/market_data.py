"""Market data fixture helpers for the local demo."""

from __future__ import annotations

from typing import Any


def build_price_index(market_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["security_id"]: record for record in market_data["prices"]}


def validate_market_data_for_snapshot(
    market_data: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    missing_prices: list[dict[str, str]] = []

    if market_data["valuation_date"] != snapshot["as_of_date"]:
        _add_issue(
            errors,
            "VALUATION_DATE_MISMATCH",
            market_data["fixture_id"],
            "Market data valuation date must match snapshot as_of_date",
        )
    if market_data["currency"] != snapshot["reporting_currency"]:
        _add_issue(errors, "CURRENCY_MISMATCH", market_data["fixture_id"], "Market data currency must match reporting currency")

    seen_prices: set[str] = set()
    price_index: dict[str, dict[str, Any]] = {}
    for price in market_data["prices"]:
        security_id = price["security_id"]
        if security_id in seen_prices:
            _add_issue(errors, "DUPLICATE_PRICE", security_id, "Duplicate market data price record")
        seen_prices.add(security_id)
        price_index[security_id] = price

    securities = {security["security_id"]: security for security in snapshot["securities"]}
    for holding in snapshot["holdings"]:
        security_id = holding["security_id"]
        security = securities[security_id]
        if security["security_type"] == "cash":
            continue
        price = price_index.get(security_id)
        if price is None:
            issue = {
                "code": "MISSING_PRICE",
                "record_id": security_id,
                "holding_id": holding["holding_id"],
                "message": f"Missing price for holding {holding['holding_id']}",
            }
            errors.append(issue)
            missing_prices.append(issue)
            continue
        if price["currency"] != security["currency"]:
            _add_issue(errors, "PRICE_CURRENCY_MISMATCH", security_id, "Price currency must match security currency")
        if price["price_date"] != snapshot["as_of_date"]:
            _add_issue(warnings, "PRICE_DATE_MISMATCH", security_id, "Price date differs from snapshot as_of_date")

    return {
        "status": "invalid" if errors else "valid",
        "errors": errors,
        "warnings": warnings,
        "missing_prices": missing_prices,
    }


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})
