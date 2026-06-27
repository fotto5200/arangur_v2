"""Data coverage and valuation-confidence scoring for the local demo."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

from .market_data import build_price_index


SCHEMA_VERSION = "data_coverage_result.v1"
CONFIDENCE_LEVELS = ("high", "medium", "low", "unknown")
OVERALL_CONFIDENCE_LEVELS = (*CONFIDENCE_LEVELS, "mixed")
DIMENSION_FIELDS = (
    "identifier_coverage",
    "price_coverage",
    "classification_coverage",
    "source_transparency",
    "valuation_method_confidence",
    "scenario_mapping_confidence",
)
PUBLIC_SECURITY_TYPES = {"equity", "etf", "fund", "mutual_fund", "reit", "adr"}
OPAQUE_TERMS = (
    "private",
    "opaque",
    "placeholder",
    "alternative",
    "hedge",
    "real_estate",
    "real estate",
    "venture",
)


@dataclass(frozen=True)
class DataCoverageResult:
    """Serializable data coverage result for local demo reports."""

    run_id: str
    source_adapter: str
    valuation_date: str
    synthetic_data: bool
    portfolio_coverage_summary: dict[str, Any]
    account_coverage: list[dict[str, Any]]
    holding_coverage: list[dict[str, Any]]
    security_coverage: list[dict[str, Any]]
    valuation_confidence_summary: dict[str, Any]
    data_quality_flags: list[dict[str, Any]]
    human_review_items: list[dict[str, Any]]
    caveats: list[str]
    next_data_work_items: list[str]
    source_name: str = "unknown_source"
    workflow_type: str = "unknown_workflow"
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "source_name": self.source_name,
            "source_adapter": self.source_adapter,
            "workflow_type": self.workflow_type,
            "valuation_date": self.valuation_date,
            "synthetic_data": self.synthetic_data,
            "portfolio_coverage_summary": self.portfolio_coverage_summary,
            "account_coverage": self.account_coverage,
            "holding_coverage": self.holding_coverage,
            "security_coverage": self.security_coverage,
            "valuation_confidence_summary": self.valuation_confidence_summary,
            "data_quality_flags": self.data_quality_flags,
            "human_review_items": self.human_review_items,
            "caveats": self.caveats,
            "next_data_work_items": self.next_data_work_items,
        }


def calculate_data_coverage(
    snapshot: dict[str, Any],
    valuation: dict[str, Any],
    market_data: dict[str, Any],
    scenario_result_set: dict[str, Any],
    run_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate local, transparent coverage and valuation-confidence labels."""

    metadata = run_metadata or {}
    source_adapter = (
        metadata.get("source_adapter")
        or snapshot.get("source", {}).get("source_adapter")
        or snapshot.get("source", {}).get("adapter")
        or "unknown_source_adapter"
    )
    source_name = metadata.get("source_name") or source_adapter
    workflow_type = metadata.get("workflow_type") or "unknown_workflow"
    valuation_date = metadata.get("valuation_date") or snapshot["as_of_date"]
    run_id = metadata.get("run_id") or f"run_{source_name}_{workflow_type}_{valuation_date.replace('-', '_')}"
    synthetic_data = bool(metadata.get("synthetic_data", snapshot["portfolio"].get("is_synthetic", False)))

    price_index = build_price_index(market_data)
    position_index = {position["holding_id"]: position for position in valuation.get("positions", [])}
    managers = {manager["manager_id"]: manager for manager in snapshot["managers"]}
    accounts = {account["account_id"]: account for account in snapshot["accounts"]}
    securities = {security["security_id"]: security for security in snapshot["securities"]}
    holdings_by_security = _group_by(snapshot["holdings"], "security_id")
    cash_by_account = _group_by(snapshot.get("cash_balances", []), "account_id")

    data_quality_flags: list[dict[str, Any]] = []
    human_review_items: list[dict[str, Any]] = []

    source_transparency = _source_transparency_confidence(source_adapter)
    if source_adapter == "plaid_mock":
        _add_flag(
            data_quality_flags,
            "PLAID_MOCK_TRANSPARENCY_CAVEAT",
            "medium",
            "source",
            source_adapter,
            "Plaid-shaped mock intake proves canonical mapping shape, not live Plaid valuation proof.",
        )
        _add_review_item(
            human_review_items,
            "PLAID_MOCK_SOURCE_SHAPE_REVIEW",
            "medium",
            "source",
            source_adapter,
            "Review source provenance before treating Plaid-shaped mock data as production-ready.",
        )

    security_coverage = _build_security_coverage(
        snapshot,
        price_index,
        holdings_by_security,
        source_transparency,
        data_quality_flags,
        human_review_items,
    )
    security_coverage_by_id = {row["security_id"]: row for row in security_coverage}

    holding_coverage = _build_holding_coverage(
        snapshot,
        price_index,
        position_index,
        accounts,
        managers,
        securities,
        source_transparency,
        scenario_result_set,
        data_quality_flags,
        human_review_items,
    )

    account_coverage = _build_account_coverage(snapshot, accounts, managers, holding_coverage, cash_by_account)
    valuation_confidence_summary = _build_valuation_confidence_summary(
        account_coverage,
        holding_coverage,
        security_coverage,
    )
    portfolio_coverage_summary = _build_portfolio_coverage_summary(
        snapshot,
        valuation,
        account_coverage,
        holding_coverage,
        security_coverage_by_id,
        valuation_confidence_summary,
        human_review_items,
    )

    result = DataCoverageResult(
        run_id=run_id,
        source_name=source_name,
        source_adapter=source_adapter,
        workflow_type=workflow_type,
        valuation_date=valuation_date,
        synthetic_data=synthetic_data,
        portfolio_coverage_summary=portfolio_coverage_summary,
        account_coverage=account_coverage,
        holding_coverage=holding_coverage,
        security_coverage=security_coverage,
        valuation_confidence_summary=valuation_confidence_summary,
        data_quality_flags=data_quality_flags,
        human_review_items=human_review_items,
        caveats=_coverage_caveats(source_adapter, synthetic_data),
        next_data_work_items=_next_data_work_items(source_adapter),
    )
    return result.to_dict()


def _build_security_coverage(
    snapshot: dict[str, Any],
    price_index: dict[str, dict[str, Any]],
    holdings_by_security: dict[str, list[dict[str, Any]]],
    source_transparency: str,
    data_quality_flags: list[dict[str, Any]],
    human_review_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for security in snapshot["securities"]:
        security_id = security["security_id"]
        price = price_index.get(security_id)
        holding_count = len(holdings_by_security.get(security_id, []))
        identifier = _identifier_confidence(security)
        price_confidence = _security_price_confidence(security, price, holding_count, snapshot["as_of_date"])
        classification = _classification_confidence(security)
        valuation_method = _security_valuation_method_confidence(security, price, holding_count)
        scenario_mapping = _scenario_mapping_confidence(security)
        row_dimensions = {
            "identifier_coverage": identifier,
            "price_coverage": price_confidence,
            "classification_coverage": classification,
            "source_transparency": source_transparency,
            "valuation_method_confidence": valuation_method,
            "scenario_mapping_confidence": scenario_mapping,
        }
        row = {
            "security_id": security_id,
            "display_name": security["display_name"],
            "ticker": security.get("ticker"),
            "security_type": security.get("security_type"),
            "asset_class": security.get("asset_class"),
            "sector": security.get("sector"),
            "themes": security.get("themes", []),
            "holding_count": holding_count,
            "price": price.get("price") if price else None,
            "price_date": price.get("price_date") if price else None,
            **row_dimensions,
            "overall_confidence": _combine_record_confidence(row_dimensions.values()),
            "coverage_notes": _security_notes(security, price, holding_count),
        }
        rows.append(row)
        _add_security_review_items(row, security, data_quality_flags, human_review_items)
    return sorted(rows, key=lambda row: (row["holding_count"] == 0, row["display_name"]))


def _build_holding_coverage(
    snapshot: dict[str, Any],
    price_index: dict[str, dict[str, Any]],
    position_index: dict[str, dict[str, Any]],
    accounts: dict[str, dict[str, Any]],
    managers: dict[str, dict[str, Any]],
    securities: dict[str, dict[str, Any]],
    source_transparency: str,
    scenario_result_set: dict[str, Any],
    data_quality_flags: list[dict[str, Any]],
    human_review_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    scenario_holding_ids = _scenario_mapped_holding_ids(scenario_result_set)
    for holding in snapshot["holdings"]:
        account = accounts[holding["account_id"]]
        manager = managers[account["manager_id"]]
        security = securities[holding["security_id"]]
        price = price_index.get(security["security_id"])
        position = position_index.get(holding["holding_id"])
        identifier = _identifier_confidence(security)
        price_confidence = _holding_price_confidence(security, price, snapshot["as_of_date"])
        classification = _classification_confidence(security)
        valuation_method = _holding_valuation_method_confidence(security, price)
        scenario_mapping = _holding_scenario_mapping_confidence(holding, security, scenario_holding_ids)
        row_dimensions = {
            "identifier_coverage": identifier,
            "price_coverage": price_confidence,
            "classification_coverage": classification,
            "source_transparency": source_transparency,
            "valuation_method_confidence": valuation_method,
            "scenario_mapping_confidence": scenario_mapping,
        }
        row = {
            "holding_id": holding["holding_id"],
            "account_id": holding["account_id"],
            "account_name": account["display_name"],
            "manager_id": account["manager_id"],
            "manager_name": manager["display_name"],
            "security_id": security["security_id"],
            "display_name": security["display_name"],
            "ticker": security.get("ticker"),
            "quantity": holding["quantity"],
            "price": price.get("price") if price else None,
            "price_date": price.get("price_date") if price else None,
            "market_value": position.get("market_value") if position else None,
            "valuation_method": _valuation_method_label(security, price),
            **row_dimensions,
            "overall_confidence": _combine_record_confidence(row_dimensions.values()),
            "coverage_notes": _holding_notes(security, price),
        }
        rows.append(row)
        _add_holding_review_items(row, data_quality_flags, human_review_items)
    return rows


def _build_account_coverage(
    snapshot: dict[str, Any],
    accounts: dict[str, dict[str, Any]],
    managers: dict[str, dict[str, Any]],
    holding_coverage: list[dict[str, Any]],
    cash_by_account: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    holdings_by_account = _group_by(holding_coverage, "account_id")
    rows = []
    for account in snapshot["accounts"]:
        account_holdings = holdings_by_account.get(account["account_id"], [])
        cash_rows = cash_by_account.get(account["account_id"], [])
        confidence_values = [row["overall_confidence"] for row in account_holdings]
        confidence_values.extend("high" for _ in cash_rows)
        if not confidence_values:
            confidence_values.append("unknown")
        low_count = sum(1 for row in account_holdings if row["overall_confidence"] == "low")
        medium_count = sum(1 for row in account_holdings if row["overall_confidence"] == "medium")
        missing_price_count = sum(1 for row in account_holdings if row["price_coverage"] == "low")
        row = {
            "account_id": account["account_id"],
            "account_name": account["display_name"],
            "manager_id": account["manager_id"],
            "manager_name": managers[account["manager_id"]]["display_name"],
            "account_type": account["account_type"],
            "holding_count": len(account_holdings),
            "cash_balance_count": len(cash_rows),
            "cash_coverage": "high" if cash_rows else "unknown",
            "low_confidence_holding_count": low_count,
            "medium_confidence_holding_count": medium_count,
            "missing_price_holding_count": missing_price_count,
            "overall_confidence": _combine_record_confidence(confidence_values),
        }
        rows.append(row)
    return rows


def _build_valuation_confidence_summary(
    account_coverage: list[dict[str, Any]],
    holding_coverage: list[dict[str, Any]],
    security_coverage: list[dict[str, Any]],
) -> dict[str, Any]:
    dimension_confidence = {
        dimension: _aggregate_dimension_confidence(
            [row[dimension] for row in holding_coverage] + [row[dimension] for row in security_coverage]
        )
        for dimension in DIMENSION_FIELDS
    }
    values: list[str] = []
    values.extend(row["overall_confidence"] for row in account_coverage)
    values.extend(row["overall_confidence"] for row in holding_coverage)
    values.extend(row["overall_confidence"] for row in security_coverage)
    for dimension in DIMENSION_FIELDS:
        values.append(dimension_confidence[dimension])
    confidence_counts = _confidence_counts(values)
    return {
        "overall_confidence": _overall_confidence_label(confidence_counts),
        "confidence_counts": confidence_counts,
        "dimension_confidence": dimension_confidence,
        "dimension_notes": [
            "Identifier coverage checks ticker/security identifiers for public securities.",
            "Price coverage checks local fixture prices and valuation-date alignment.",
            "Classification coverage checks sector and theme fields used by exposure reporting.",
            "Source transparency reflects whether the adapter is a native synthetic fixture or Plaid-shaped mock.",
            "Valuation method confidence is high for priced public securities/cash, medium for ETFs, and low for private or missing-price placeholders.",
            "Scenario mapping confidence is high only when ticker, sector, or theme mapping is available.",
        ],
    }


def _build_portfolio_coverage_summary(
    snapshot: dict[str, Any],
    valuation: dict[str, Any],
    account_coverage: list[dict[str, Any]],
    holding_coverage: list[dict[str, Any]],
    security_coverage_by_id: dict[str, dict[str, Any]],
    valuation_confidence_summary: dict[str, Any],
    human_review_items: list[dict[str, Any]],
) -> dict[str, Any]:
    held_security_ids = {holding["security_id"] for holding in snapshot["holdings"]}
    unheld_low_security_count = sum(
        1
        for security_id, row in security_coverage_by_id.items()
        if security_id not in held_security_ids and row["overall_confidence"] == "low"
    )
    priced_holding_count = sum(1 for row in holding_coverage if row["price_coverage"] == "high")
    missing_price_count = sum(1 for row in holding_coverage if row["price_coverage"] == "low")
    classification_complete_count = sum(1 for row in holding_coverage if row["classification_coverage"] == "high")
    summary_label = valuation_confidence_summary["overall_confidence"]
    return {
        "overall_confidence": summary_label,
        "summary": (
            f"Coverage is {summary_label}: {priced_holding_count} of {len(holding_coverage)} held positions have local fixture prices, "
            f"{classification_complete_count} holdings have complete sector/theme classifications, "
            f"and {len(human_review_items)} item(s) need human review before production use."
        ),
        "accounts_total": len(account_coverage),
        "holdings_total": len(holding_coverage),
        "securities_total": len(security_coverage_by_id),
        "cash_balances_total": len(snapshot.get("cash_balances", [])),
        "priced_holdings": priced_holding_count,
        "missing_price_holdings": missing_price_count,
        "classification_complete_holdings": classification_complete_count,
        "unheld_low_confidence_securities": unheld_low_security_count,
        "portfolio_market_value": valuation["portfolio_total"]["market_value"],
        "portfolio_cash_value": valuation["portfolio_total"]["cash_value"],
        "human_review_item_count": len(human_review_items),
    }


def _add_holding_review_items(
    row: dict[str, Any],
    data_quality_flags: list[dict[str, Any]],
    human_review_items: list[dict[str, Any]],
) -> None:
    if row["price_coverage"] == "low":
        _add_flag(
            data_quality_flags,
            "MISSING_MARKET_PRICE",
            "high",
            "holding",
            row["holding_id"],
            f"Missing local fixture price for {row['display_name']}; valuation omitted or requires review.",
        )
        _add_review_item(
            human_review_items,
            "MISSING_MARKET_PRICE",
            "high",
            "holding",
            row["holding_id"],
            f"Supply or verify a price for {row['display_name']} before treating the valuation as complete.",
        )
    if row["identifier_coverage"] == "low":
        _add_flag(
            data_quality_flags,
            "PUBLIC_IDENTIFIER_MISSING",
            "medium",
            "holding",
            row["holding_id"],
            f"Public holding {row['display_name']} is missing a ticker or identifier.",
        )
    if row["classification_coverage"] == "low":
        _add_flag(
            data_quality_flags,
            "CLASSIFICATION_MISSING",
            "medium",
            "holding",
            row["holding_id"],
            f"Holding {row['display_name']} is missing sector and/or theme classification.",
        )
        _add_review_item(
            human_review_items,
            "CLASSIFICATION_REVIEW",
            "medium",
            "holding",
            row["holding_id"],
            f"Review sector/theme classification for {row['display_name']}.",
        )
    if row["scenario_mapping_confidence"] == "low":
        _add_flag(
            data_quality_flags,
            "SCENARIO_MAPPING_MISSING",
            "medium",
            "holding",
            row["holding_id"],
            f"Holding {row['display_name']} lacks ticker, sector, or theme mapping for scenario rules.",
        )


def _add_security_review_items(
    row: dict[str, Any],
    security: dict[str, Any],
    data_quality_flags: list[dict[str, Any]],
    human_review_items: list[dict[str, Any]],
) -> None:
    if _is_opaque_or_private(security):
        _add_flag(
            data_quality_flags,
            "OPAQUE_PRIVATE_PLACEHOLDER",
            "high",
            "security",
            row["security_id"],
            f"{row['display_name']} is an opaque/private placeholder and needs a human valuation policy.",
        )
        _add_review_item(
            human_review_items,
            "OPAQUE_PRIVATE_PLACEHOLDER",
            "high",
            "security",
            row["security_id"],
            f"Define source documents and valuation method before including {row['display_name']} in production reporting.",
        )


def _identifier_confidence(security: dict[str, Any]) -> str:
    if _is_opaque_or_private(security):
        return "medium" if security.get("security_id") else "low"
    if _is_public_security(security):
        return "high" if security.get("ticker") else "low"
    return "medium" if security.get("security_id") else "unknown"


def _holding_price_confidence(security: dict[str, Any], price: dict[str, Any] | None, valuation_date: str) -> str:
    if _is_opaque_or_private(security):
        return "low"
    if price is None:
        return "low"
    if price.get("price_date") != valuation_date:
        return "medium"
    return "high"


def _security_price_confidence(
    security: dict[str, Any],
    price: dict[str, Any] | None,
    holding_count: int,
    valuation_date: str,
) -> str:
    if _is_opaque_or_private(security):
        return "low"
    if price is None:
        return "low" if holding_count else "unknown"
    if price.get("price_date") != valuation_date:
        return "medium"
    return "high"


def _classification_confidence(security: dict[str, Any]) -> str:
    if _is_opaque_or_private(security):
        return "low"
    has_sector = bool(security.get("sector"))
    has_themes = bool(security.get("themes"))
    if has_sector and has_themes:
        return "high"
    if has_sector or has_themes:
        return "medium"
    return "low"


def _security_valuation_method_confidence(
    security: dict[str, Any],
    price: dict[str, Any] | None,
    holding_count: int,
) -> str:
    if _is_opaque_or_private(security):
        return "low"
    if price is None:
        return "low" if holding_count else "unknown"
    if security.get("security_type") == "etf":
        return "medium"
    if _is_public_security(security):
        return "high"
    return "medium"


def _holding_valuation_method_confidence(security: dict[str, Any], price: dict[str, Any] | None) -> str:
    if _is_opaque_or_private(security) or price is None:
        return "low"
    if security.get("security_type") == "etf":
        return "medium"
    if _is_public_security(security):
        return "high"
    return "medium"


def _scenario_mapping_confidence(security: dict[str, Any]) -> str:
    if _is_opaque_or_private(security):
        return "low"
    if security.get("ticker") or security.get("sector") or security.get("themes"):
        return "high"
    if security.get("asset_class") or security.get("scenario_tags"):
        return "medium"
    return "low"


def _holding_scenario_mapping_confidence(
    holding: dict[str, Any],
    security: dict[str, Any],
    scenario_holding_ids: set[str],
) -> str:
    if holding["holding_id"] in scenario_holding_ids:
        return "high"
    return _scenario_mapping_confidence(security)


def _scenario_mapped_holding_ids(scenario_result_set: dict[str, Any]) -> set[str]:
    holding_ids: set[str] = set()
    for scenario in scenario_result_set.get("scenario_results", []):
        for impact in scenario.get("position_impacts", []):
            matched_rule = impact.get("matched_rule")
            if matched_rule and matched_rule != "default":
                holding_ids.add(impact["holding_id"])
    return holding_ids


def _source_transparency_confidence(source_adapter: str) -> str:
    if source_adapter == "demo_json":
        return "high"
    if source_adapter == "plaid_mock":
        return "medium"
    return "unknown"


def _valuation_method_label(security: dict[str, Any], price: dict[str, Any] | None) -> str:
    if _is_opaque_or_private(security):
        return "human_review_required_private_placeholder"
    if price is None:
        return "missing_price_review_required"
    if security.get("security_type") == "etf":
        return "local_fixture_price_times_quantity_etf"
    if _is_public_security(security):
        return "local_fixture_price_times_quantity_public_security"
    return "local_fixture_price_times_quantity_review_recommended"


def _security_notes(security: dict[str, Any], price: dict[str, Any] | None, holding_count: int) -> list[str]:
    notes: list[str] = []
    if _is_opaque_or_private(security):
        notes.append("Opaque/private placeholder requires human valuation policy before production use.")
    if price is None:
        if holding_count:
            notes.append("No local fixture price is available for a held security.")
        else:
            notes.append("No local fixture price is attached; security is not held in the current snapshot.")
    if security.get("security_type") == "etf" and price is not None:
        notes.append("ETF is valued from a local fixture price; no fund look-through is implemented.")
    if not notes:
        notes.append("Coverage is complete for the current local prototype rules.")
    return notes


def _holding_notes(security: dict[str, Any], price: dict[str, Any] | None) -> list[str]:
    notes: list[str] = []
    if price is None:
        notes.append("Missing local fixture price creates a valuation human-review item.")
    if _is_opaque_or_private(security):
        notes.append("Opaque/private asset valuation is outside the current prototype.")
    if security.get("security_type") == "etf" and price is not None:
        notes.append("ETF price is available, but look-through exposure and vendor proof are not implemented.")
    if not security.get("sector") or not security.get("themes"):
        notes.append("Classification should be reviewed before production reporting.")
    if not notes:
        notes.append("Held public security has identifier, price, classification, and scenario mapping coverage.")
    return notes


def _coverage_caveats(source_adapter: str, synthetic_data: bool) -> list[str]:
    caveats = [
        "Data coverage uses local deterministic rules and synthetic fixtures only.",
        "Valuation confidence describes source/readiness quality; it is not investment advice or a forecast.",
        "Local fixture prices are not market-data vendor evidence, custodian statements, or reconciliation proof.",
    ]
    if synthetic_data:
        caveats.append("All generated coverage labels are demo labels over synthetic data, not client data.")
    if source_adapter == "plaid_mock":
        caveats.append("Plaid-shaped mock data demonstrates intake shape and canonical mapping, not live Plaid behavior.")
    return caveats


def _next_data_work_items(source_adapter: str) -> list[str]:
    items = [
        "Define source inventory fields for statements, custodians, market-data vendors, and manual overrides.",
        "Add stale-price and reconciliation checks once historical synthetic fixtures exist.",
        "Create a private/opaque asset valuation rubric before adding real private holdings.",
        "Link human-review items to future workflow tasks or report-package review status.",
    ]
    if source_adapter == "plaid_mock":
        items.append("Separate Plaid Sandbox design from this mock fixture before any live credential work.")
    return items


def _confidence_counts(values: list[str]) -> dict[str, int]:
    counts = Counter(value for value in values if value in CONFIDENCE_LEVELS)
    return {level: counts.get(level, 0) for level in CONFIDENCE_LEVELS}


def _aggregate_dimension_confidence(values: list[str]) -> str:
    valid_values = [value for value in values if value in CONFIDENCE_LEVELS]
    if not valid_values:
        return "unknown"
    if "low" in valid_values:
        return "low"
    if "unknown" in valid_values:
        return "unknown"
    if "medium" in valid_values:
        return "medium"
    return "high"


def _overall_confidence_label(confidence_counts: dict[str, int]) -> str:
    present = [level for level, count in confidence_counts.items() if count]
    if not present:
        return "unknown"
    if len(present) > 1:
        return "mixed"
    return present[0]


def _combine_record_confidence(values: Any) -> str:
    confidences = [value for value in values if value in OVERALL_CONFIDENCE_LEVELS]
    if not confidences:
        return "unknown"
    if "low" in confidences:
        return "low"
    if "unknown" in confidences:
        return "unknown"
    if "medium" in confidences:
        return "medium"
    if "mixed" in confidences:
        return "mixed"
    return "high"


def _group_by(records: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record[field]].append(record)
    return grouped


def _is_public_security(security: dict[str, Any]) -> bool:
    return str(security.get("security_type", "")).lower() in PUBLIC_SECURITY_TYPES


def _is_opaque_or_private(security: dict[str, Any]) -> bool:
    values = [
        security.get("security_type"),
        security.get("asset_class"),
        security.get("display_name"),
        security.get("security_id"),
    ]
    text = " ".join(str(value).lower() for value in values if value)
    return any(term in text for term in OPAQUE_TERMS)


def _add_flag(
    flags: list[dict[str, Any]],
    code: str,
    severity: str,
    scope: str,
    record_id: str,
    message: str,
) -> None:
    flags.append(
        {
            "code": code,
            "severity": severity,
            "scope": scope,
            "record_id": record_id,
            "message": message,
        }
    )


def _add_review_item(
    review_items: list[dict[str, Any]],
    code: str,
    priority: str,
    scope: str,
    record_id: str,
    message: str,
) -> None:
    review_items.append(
        {
            "code": code,
            "priority": priority,
            "scope": scope,
            "record_id": record_id,
            "message": message,
        }
    )
