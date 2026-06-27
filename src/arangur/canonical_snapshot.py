"""Build the canonical portfolio snapshot from local demo inputs."""

from __future__ import annotations

from typing import Any


def build_canonical_snapshot(
    portfolio_data: dict[str, Any],
    source_files: list[str] | None = None,
) -> dict[str, Any]:
    metadata = portfolio_data["metadata"]
    validation = _validate_references(portfolio_data)
    as_of_date = metadata["valuation_date"]
    generated_at = f"{as_of_date}T00:00:00+00:00"
    dataset_id = metadata["dataset_id"]
    snapshot_id = f"snap_{dataset_id}_{as_of_date.replace('-', '_')}"

    managers = [
        {
            "manager_id": manager["manager_id"],
            "display_name": manager["manager_name"],
            "manager_type": manager.get("manager_type"),
            "strategy_label": manager.get("strategy_label"),
            "source_ref": _source_ref("manager", manager["manager_id"]),
        }
        for manager in portfolio_data["managers"]
    ]

    accounts = [
        {
            "account_id": account["account_id"],
            "display_name": account["account_name"],
            "manager_id": account["manager_id"],
            "account_type": account["account_type"],
            "currency": account["currency"],
            "custodian_label": account.get("custodian_label"),
            "household_member": account.get("household_member"),
            "tags": account.get("tags", []),
            "source_ref": _source_ref("account", account["account_id"]),
        }
        for account in portfolio_data["accounts"]
    ]

    securities = [
        {
            "security_id": security["security_id"],
            "display_name": security["name"],
            "ticker": security.get("ticker"),
            "security_type": security["security_type"],
            "currency": security["currency"],
            "asset_class": security["asset_class"],
            "sector": security.get("sector"),
            "themes": security.get("themes", []),
            "scenario_tags": security.get("scenario_tags", []),
            "source_ref": _source_ref("security", security["security_id"]),
        }
        for security in portfolio_data["securities"]
    ]

    holdings = [
        {
            "holding_id": holding["holding_id"],
            "account_id": holding["account_id"],
            "security_id": holding["security_id"],
            "quantity": holding["quantity"],
            "quantity_unit": holding.get("quantity_unit", "shares"),
            "cost_basis": holding.get("cost_basis"),
            "cost_basis_currency": metadata["reporting_currency"] if holding.get("cost_basis") is not None else None,
            "manager_note": holding.get("manager_note"),
            "tags": holding.get("tags", []),
            "source_ref": _source_ref("holding", holding["holding_id"]),
        }
        for holding in portfolio_data["holdings"]
    ]

    cash_balances = [
        {
            "cash_id": cash["cash_id"],
            "account_id": cash["account_id"],
            "currency": cash["currency"],
            "amount": cash["amount"],
            "cash_type": cash.get("cash_type"),
            "source_ref": _source_ref("cash_balance", cash["cash_id"]),
        }
        for cash in portfolio_data["cash_balances"]
    ]

    return {
        "schema_version": "canonical_portfolio_snapshot.v1",
        "snapshot_id": snapshot_id,
        "as_of_date": as_of_date,
        "created_at": generated_at,
        "reporting_currency": metadata["reporting_currency"],
        "source": {
            "adapter": "demo_json",
            "dataset_id": dataset_id,
            "dataset_label": metadata["dataset_label"],
            "source_files": source_files or [],
            "imported_at": generated_at,
            "is_synthetic": metadata["is_synthetic"],
            "provenance_notes": [
                "Local synthetic JSON fixtures generated for the Arangur v2 demo.",
                "No real client data, Plaid payloads, external APIs, or legacy MATLAB outputs are used.",
            ],
        },
        "portfolio": {
            "portfolio_id": "portfolio_northstar_demo",
            "portfolio_name": metadata["dataset_label"],
            "owner_label": metadata["portfolio_owner_label"],
            "advisor_label": metadata.get("advisor_label"),
            "base_currency": metadata["reporting_currency"],
            "is_synthetic": metadata["is_synthetic"],
            "notes": metadata.get("notes"),
        },
        "managers": managers,
        "accounts": accounts,
        "securities": securities,
        "holdings": holdings,
        "cash_balances": cash_balances,
        "transactions": portfolio_data.get("transactions", []),
        "validation": validation,
    }


def _validate_references(portfolio_data: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    metadata = portfolio_data["metadata"]
    reporting_currency = metadata["reporting_currency"]

    manager_ids = _collect_unique_ids(portfolio_data["managers"], "manager_id", "manager", errors)
    account_ids = _collect_unique_ids(portfolio_data["accounts"], "account_id", "account", errors)
    security_ids = _collect_unique_ids(portfolio_data["securities"], "security_id", "security", errors)
    _collect_unique_ids(portfolio_data["holdings"], "holding_id", "holding", errors)
    _collect_unique_ids(portfolio_data["cash_balances"], "cash_id", "cash_balance", errors)

    for account in portfolio_data["accounts"]:
        if account["manager_id"] not in manager_ids:
            _add_issue(errors, "UNKNOWN_MANAGER", account["account_id"], f"Unknown manager_id {account['manager_id']}")
        if account["currency"] != reporting_currency:
            _add_issue(errors, "UNSUPPORTED_ACCOUNT_CURRENCY", account["account_id"], "V1 requires account currency to match reporting currency")

    for security in portfolio_data["securities"]:
        if security["currency"] != reporting_currency:
            _add_issue(errors, "UNSUPPORTED_SECURITY_CURRENCY", security["security_id"], "V1 requires security currency to match reporting currency")

    for holding in portfolio_data["holdings"]:
        if holding["account_id"] not in account_ids:
            _add_issue(errors, "UNKNOWN_ACCOUNT", holding["holding_id"], f"Unknown account_id {holding['account_id']}")
        if holding["security_id"] not in security_ids:
            _add_issue(errors, "UNKNOWN_SECURITY", holding["holding_id"], f"Unknown security_id {holding['security_id']}")
        if holding["quantity"] < 0:
            _add_issue(errors, "NEGATIVE_QUANTITY", holding["holding_id"], "V1 requires long-only non-negative quantities")
        if "cost_basis" not in holding:
            _add_issue(warnings, "OPTIONAL_COST_BASIS_MISSING", holding["holding_id"], "Cost basis was not supplied")

    for cash in portfolio_data["cash_balances"]:
        if cash["account_id"] not in account_ids:
            _add_issue(errors, "UNKNOWN_ACCOUNT", cash["cash_id"], f"Unknown account_id {cash['account_id']}")
        if cash["currency"] != reporting_currency:
            _add_issue(errors, "UNSUPPORTED_CASH_CURRENCY", cash["cash_id"], "V1 requires cash currency to match reporting currency")
        if cash["amount"] < 0:
            _add_issue(errors, "NEGATIVE_CASH", cash["cash_id"], "Cash amount must be non-negative")

    return {
        "status": "invalid" if errors else "valid",
        "errors": errors,
        "warnings": warnings,
    }


def _collect_unique_ids(records: list[dict[str, Any]], id_field: str, label: str, errors: list[dict[str, str]]) -> set[str]:
    seen: set[str] = set()
    for record in records:
        record_id = record[id_field]
        if record_id in seen:
            _add_issue(errors, "DUPLICATE_ID", record_id, f"Duplicate {label} id")
        seen.add(record_id)
    return seen


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})


def _source_ref(section: str, source_id: str) -> dict[str, str]:
    return {
        "source_system": "demo_json",
        "source_section": section,
        "source_id": source_id,
    }
