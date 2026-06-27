"""Exposure and direct overlap analytics for the local demo."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def calculate_exposure_overlap(snapshot: dict[str, Any], valuation: dict[str, Any]) -> dict[str, Any]:
    total_value = valuation["portfolio_total"]["market_value"]
    securities = {security["security_id"]: security for security in snapshot["securities"]}
    account_names = {account["account_id"]: account["display_name"] for account in snapshot["accounts"]}
    manager_names = {manager["manager_id"]: manager["display_name"] for manager in snapshot["managers"]}

    by_asset_class: dict[str, float] = defaultdict(float)
    by_sector: dict[str, float] = defaultdict(float)
    by_theme: dict[str, float] = defaultdict(float)
    positions_by_security: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for position in valuation["positions"]:
        value = position["market_value"]
        by_asset_class[position.get("asset_class") or "unclassified"] += value
        by_sector[position.get("sector") or "unclassified"] += value
        themes = position.get("themes") or ["unclassified"]
        for theme in themes:
            by_theme[theme] += value
        positions_by_security[position["security_id"]].append(position)

    cash_value = valuation["portfolio_total"]["cash_value"]
    if cash_value:
        by_asset_class["cash"] += cash_value
        by_theme["cash_buffer"] += cash_value

    overlaps = _build_overlaps(positions_by_security, securities, account_names, manager_names, total_value)
    top_holdings = sorted(valuation["positions"], key=lambda row: row["market_value"], reverse=True)[:10]
    largest_duplicated = sorted(overlaps, key=lambda row: row["total_market_value"], reverse=True)[:5]

    concentration_notes = []
    for row in _bucket_rows(by_theme, total_value):
        if row["portfolio_percent"] >= 0.20:
            concentration_notes.append(
                {
                    "code": "LARGE_THEME_EXPOSURE",
                    "bucket": row["bucket_label"],
                    "message": f"{row['bucket_label']} theme exposure is above 20% of portfolio value.",
                }
            )

    return {
        "schema_version": "exposure_overlap_result.v1",
        "snapshot_id": snapshot["snapshot_id"],
        "valuation_date": snapshot["as_of_date"],
        "portfolio_market_value": total_value,
        "exposures": {
            "by_account": _total_rows(valuation["account_totals"], "account_id", "account_name", total_value),
            "by_manager": _total_rows(valuation["manager_totals"], "manager_id", "manager_name", total_value),
            "by_asset_class": _bucket_rows(by_asset_class, total_value),
            "by_sector": _bucket_rows(by_sector, total_value),
            "by_theme": _bucket_rows(by_theme, total_value),
            "cash": [
                {
                    "bucket_id": "cash",
                    "bucket_label": "Cash",
                    "market_value": cash_value,
                    "portfolio_percent": _percent(cash_value, total_value),
                }
            ],
        },
        "overlaps": overlaps,
        "top_holdings": [_trim_position(position, total_value) for position in top_holdings],
        "largest_duplicated_holdings": largest_duplicated,
        "concentration_notes": concentration_notes,
        "validation": {"status": "valid", "errors": [], "warnings": []},
    }


def _build_overlaps(
    positions_by_security: dict[str, list[dict[str, Any]]],
    securities: dict[str, dict[str, Any]],
    account_names: dict[str, str],
    manager_names: dict[str, str],
    total_value: float,
) -> list[dict[str, Any]]:
    overlaps: list[dict[str, Any]] = []
    for security_id, positions in positions_by_security.items():
        accounts = sorted({position["account_id"] for position in positions})
        managers = sorted({position["manager_id"] for position in positions})
        if len(accounts) < 2 and len(managers) < 2:
            continue
        security = securities[security_id]
        total_market_value = round(sum(position["market_value"] for position in positions), 2)
        overlaps.append(
            {
                "security_id": security_id,
                "ticker": security.get("ticker"),
                "display_name": security["display_name"],
                "total_market_value": total_market_value,
                "portfolio_percent": _percent(total_market_value, total_value),
                "accounts": accounts,
                "account_names": [account_names[account_id] for account_id in accounts],
                "managers": managers,
                "manager_names": [manager_names[manager_id] for manager_id in managers],
                "sector": security.get("sector"),
                "themes": security.get("themes", []),
                "narrative_note": "Direct holding appears across multiple accounts or managers.",
            }
        )
    return sorted(overlaps, key=lambda row: row["total_market_value"], reverse=True)


def _total_rows(rows: list[dict[str, Any]], id_field: str, label_field: str, total_value: float) -> list[dict[str, Any]]:
    return [
        {
            "bucket_id": row[id_field],
            "bucket_label": row[label_field],
            "market_value": row["market_value"],
            "portfolio_percent": _percent(row["market_value"], total_value),
        }
        for row in rows
    ]


def _bucket_rows(values: dict[str, float], total_value: float) -> list[dict[str, Any]]:
    return [
        {
            "bucket_id": key,
            "bucket_label": _label(key),
            "market_value": round(value, 2),
            "portfolio_percent": _percent(value, total_value),
        }
        for key, value in sorted(values.items(), key=lambda item: item[1], reverse=True)
    ]


def _trim_position(position: dict[str, Any], total_value: float) -> dict[str, Any]:
    return {
        "holding_id": position["holding_id"],
        "security_id": position["security_id"],
        "ticker": position.get("ticker"),
        "display_name": position["display_name"],
        "account_id": position["account_id"],
        "account_name": position["account_name"],
        "manager_id": position["manager_id"],
        "manager_name": position["manager_name"],
        "market_value": position["market_value"],
        "portfolio_percent": _percent(position["market_value"], total_value),
        "sector": position.get("sector"),
        "themes": position.get("themes", []),
    }


def _percent(value: float, total_value: float) -> float:
    if not total_value:
        return 0.0
    return round(float(value) / total_value, 6)


def _label(value: str) -> str:
    if value.lower() == "ai":
        return "AI"
    return value.replace("_", " ").title()
