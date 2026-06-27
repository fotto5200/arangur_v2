"""Normalize local Plaid-shaped mock investment data into the canonical snapshot."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .demo_data_loader import DemoDataError, load_json_file


def load_plaid_mock_fixture(data_dir: Path) -> dict[str, Any]:
    data = load_json_file(data_dir / "plaid_mock_investments.json")
    errors = validate_plaid_mock_fixture(data)
    if errors:
        lines = ["Plaid mock fixture validation failed for plaid_mock_investments.json:"]
        lines.extend(f"- {error}" for error in errors)
        raise DemoDataError("\n".join(lines))
    return data


def build_canonical_snapshot_from_plaid_mock(
    plaid_data: dict[str, Any],
    source_files: list[str] | None = None,
) -> dict[str, Any]:
    metadata = plaid_data["metadata"]
    validation = _validate_references(plaid_data)
    as_of_date = metadata["valuation_date"]
    generated_at = f"{as_of_date}T00:00:00+00:00"
    dataset_id = metadata["dataset_id"]

    managers = _build_managers(plaid_data["accounts"])
    accounts = [_map_account(account) for account in plaid_data["accounts"]]
    securities = [_map_security(security) for security in plaid_data["securities"]]
    security_id_by_plaid_id = {
        security["security_id"]: security["canonical_security_id"]
        for security in plaid_data["securities"]
    }
    account_id_by_plaid_id = {
        account["account_id"]: account["arangur_mapping"]["canonical_account_id"]
        for account in plaid_data["accounts"]
    }

    holdings = [
        {
            "holding_id": f"plaid_hold_{index + 1}_{holding['account_id']}_{holding['security_id']}",
            "account_id": account_id_by_plaid_id[holding["account_id"]],
            "security_id": security_id_by_plaid_id[holding["security_id"]],
            "quantity": holding["quantity"],
            "quantity_unit": "shares",
            "cost_basis": holding.get("cost_basis"),
            "cost_basis_currency": metadata["reporting_currency"] if holding.get("cost_basis") is not None else None,
            "source_ref": _source_ref("holding", f"{holding['account_id']}:{holding['security_id']}"),
            "tags": [],
        }
        for index, holding in enumerate(plaid_data["holdings"])
    ]

    cash_balances = [
        {
            "cash_id": cash["cash_id"],
            "account_id": account_id_by_plaid_id[cash["account_id"]],
            "currency": cash["currency"],
            "amount": cash["amount"],
            "cash_type": cash.get("cash_type", "brokerage_cash"),
            "source_ref": _source_ref("cash_balance", cash["cash_id"]),
        }
        for cash in plaid_data.get("cash_balances", [])
    ]

    transactions = [
        _map_transaction(transaction, account_id_by_plaid_id, security_id_by_plaid_id)
        for transaction in plaid_data.get("investment_transactions", [])
    ]

    return {
        "schema_version": "canonical_portfolio_snapshot.v1",
        "snapshot_id": f"snap_{dataset_id}_{as_of_date.replace('-', '_')}",
        "as_of_date": as_of_date,
        "created_at": generated_at,
        "reporting_currency": metadata["reporting_currency"],
        "source": {
            "adapter": "plaid_mock",
            "source_adapter": "plaid_mock",
            "dataset_id": dataset_id,
            "dataset_label": metadata["dataset_label"],
            "source_files": source_files or [],
            "imported_at": generated_at,
            "is_synthetic": metadata["is_synthetic"],
            "mock_item_id": plaid_data["item"].get("mock_item_id"),
            "institution_name": plaid_data["item"].get("institution_name"),
            "provenance_notes": [
                "Local synthetic Plaid-shaped fixture generated for Arangur v2 adapter testing.",
                "No Plaid APIs, credentials, access tokens, item IDs, Plaid Link, or real account data are used.",
            ],
        },
        "portfolio": {
            "portfolio_id": "portfolio_northstar_plaid_mock",
            "portfolio_name": metadata["dataset_label"],
            "owner_label": metadata["portfolio_owner_label"],
            "advisor_label": metadata.get("advisor_label"),
            "base_currency": metadata["reporting_currency"],
            "is_synthetic": metadata["is_synthetic"],
            "notes": metadata.get("source_caveat"),
        },
        "managers": managers,
        "accounts": accounts,
        "securities": securities,
        "holdings": holdings,
        "cash_balances": cash_balances,
        "transactions": transactions,
        "validation": validation,
    }


def validate_plaid_mock_fixture(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require_top_level(data, ["schema_version", "metadata", "item", "accounts", "securities", "holdings", "cash_balances"], errors)

    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        _require_fields(
            metadata,
            ["dataset_id", "dataset_label", "is_synthetic", "valuation_date", "reporting_currency", "portfolio_owner_label"],
            "metadata",
            errors,
        )
        if metadata.get("is_synthetic") is not True:
            errors.append("metadata.is_synthetic must be true")
        if metadata.get("source_adapter") != "plaid_mock":
            errors.append("metadata.source_adapter must be plaid_mock")
    else:
        errors.append("metadata must be an object")

    item = data.get("item")
    if isinstance(item, dict):
        _require_fields(item, ["mock_item_id", "institution_name", "source_system", "is_synthetic"], "item", errors)
        if item.get("is_synthetic") is not True:
            errors.append("item.is_synthetic must be true")
    else:
        errors.append("item must be an object")

    _validate_required_array(data, "accounts", errors)
    _validate_required_array(data, "securities", errors)
    _validate_required_array(data, "holdings", errors)
    _validate_required_array(data, "cash_balances", errors)

    account_ids = _collect_ids(data.get("accounts", []), "account_id", "accounts", errors)
    security_ids = _collect_ids(data.get("securities", []), "security_id", "securities", errors)
    _collect_ids(data.get("cash_balances", []), "cash_id", "cash_balances", errors)

    for index, account in enumerate(data.get("accounts", [])):
        _require_fields(account, ["account_id", "name", "type", "subtype", "balances", "arangur_mapping"], f"accounts[{index}]", errors)
        if isinstance(account, dict):
            mapping = account.get("arangur_mapping")
            if isinstance(mapping, dict):
                _require_fields(
                    mapping,
                    ["canonical_account_id", "manager_id", "manager_name", "manager_type", "strategy_label", "account_type"],
                    f"accounts[{index}].arangur_mapping",
                    errors,
                )
            else:
                errors.append(f"accounts[{index}].arangur_mapping must be an object")
            balances = account.get("balances")
            if isinstance(balances, dict):
                _require_fields(balances, ["available", "iso_currency_code"], f"accounts[{index}].balances", errors)
            else:
                errors.append(f"accounts[{index}].balances must be an object")

    for index, security in enumerate(data.get("securities", [])):
        _require_fields(
            security,
            ["security_id", "canonical_security_id", "name", "type", "iso_currency_code", "arangur_classification"],
            f"securities[{index}]",
            errors,
        )
        if isinstance(security, dict):
            classification = security.get("arangur_classification")
            if isinstance(classification, dict):
                _require_fields(
                    classification,
                    ["asset_class", "sector", "themes", "scenario_tags"],
                    f"securities[{index}].arangur_classification",
                    errors,
                )
            else:
                errors.append(f"securities[{index}].arangur_classification must be an object")

    for index, holding in enumerate(data.get("holdings", [])):
        _require_fields(holding, ["account_id", "security_id", "quantity"], f"holdings[{index}]", errors)
        if isinstance(holding, dict):
            if holding.get("account_id") not in account_ids:
                errors.append(f"holdings[{index}].account_id references unknown account: {holding.get('account_id')}")
            if holding.get("security_id") not in security_ids:
                errors.append(f"holdings[{index}].security_id references unknown security: {holding.get('security_id')}")
            if holding.get("quantity", 0) < 0:
                errors.append(f"holdings[{index}].quantity must be non-negative")

    for index, cash in enumerate(data.get("cash_balances", [])):
        _require_fields(cash, ["cash_id", "account_id", "currency", "amount"], f"cash_balances[{index}]", errors)
        if isinstance(cash, dict):
            if cash.get("account_id") not in account_ids:
                errors.append(f"cash_balances[{index}].account_id references unknown account: {cash.get('account_id')}")
            if cash.get("amount", 0) < 0:
                errors.append(f"cash_balances[{index}].amount must be non-negative")

    return errors


def _build_managers(accounts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    managers: dict[str, dict[str, Any]] = {}
    for account in accounts:
        mapping = account["arangur_mapping"]
        manager_id = mapping["manager_id"]
        managers[manager_id] = {
            "manager_id": manager_id,
            "display_name": mapping["manager_name"],
            "manager_type": mapping.get("manager_type"),
            "strategy_label": mapping.get("strategy_label"),
            "source_ref": _source_ref("account_manager_mapping", manager_id),
        }
    return list(managers.values())


def _map_account(account: dict[str, Any]) -> dict[str, Any]:
    mapping = account["arangur_mapping"]
    return {
        "account_id": mapping["canonical_account_id"],
        "display_name": account["name"],
        "manager_id": mapping["manager_id"],
        "account_type": mapping["account_type"],
        "currency": account["balances"]["iso_currency_code"],
        "custodian_label": account.get("official_name"),
        "plaid_type": account.get("type"),
        "plaid_subtype": account.get("subtype"),
        "tags": mapping.get("tags", []),
        "source_ref": _source_ref("account", account["account_id"]),
    }


def _map_security(security: dict[str, Any]) -> dict[str, Any]:
    classification = security["arangur_classification"]
    return {
        "security_id": security["canonical_security_id"],
        "display_name": security["name"],
        "ticker": security.get("ticker_symbol"),
        "security_type": _map_security_type(security["type"]),
        "currency": security["iso_currency_code"],
        "asset_class": classification["asset_class"],
        "sector": classification.get("sector"),
        "themes": classification.get("themes", []),
        "scenario_tags": classification.get("scenario_tags", []),
        "source_ref": _source_ref("security", security["security_id"]),
    }


def _map_transaction(
    transaction: dict[str, Any],
    account_id_by_plaid_id: dict[str, str],
    security_id_by_plaid_id: dict[str, str],
) -> dict[str, Any]:
    plaid_security_id = transaction.get("security_id")
    return {
        "transaction_id": transaction["investment_transaction_id"],
        "account_id": account_id_by_plaid_id[transaction["account_id"]],
        "security_id": security_id_by_plaid_id.get(plaid_security_id) if plaid_security_id else None,
        "trade_date": transaction["date"],
        "transaction_type": transaction["type"],
        "transaction_subtype": transaction.get("subtype"),
        "quantity": transaction.get("quantity"),
        "amount": transaction["amount"],
        "currency": transaction["iso_currency_code"],
        "source_ref": _source_ref("investment_transaction", transaction["investment_transaction_id"]),
    }


def _validate_references(plaid_data: dict[str, Any]) -> dict[str, Any]:
    errors = [{"code": "PLAID_MOCK_VALIDATION", "record_id": "fixture", "message": error} for error in validate_plaid_mock_fixture(plaid_data)]
    return {
        "status": "invalid" if errors else "valid",
        "errors": errors,
        "warnings": [],
    }


def _map_security_type(plaid_type: str) -> str:
    if plaid_type == "etf":
        return "etf"
    if plaid_type == "equity":
        return "equity"
    return plaid_type


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


def _validate_required_array(data: dict[str, Any], field: str, errors: list[str]) -> None:
    value = data.get(field)
    if not isinstance(value, list):
        errors.append(f"{field} must be an array")
    elif not value:
        errors.append(f"{field} must not be empty")


def _collect_ids(records: Any, id_field: str, section: str, errors: list[str]) -> set[str]:
    if not isinstance(records, list):
        return set()
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict) or id_field not in record:
            continue
        record_id = record[id_field]
        if record_id in seen:
            errors.append(f"{section}[{index}].{id_field} duplicates identifier: {record_id}")
        seen.add(record_id)
    return seen


def _source_ref(section: str, source_id: str) -> dict[str, str]:
    return {
        "source_system": "plaid_mock",
        "source_section": section,
        "source_id": source_id,
    }
