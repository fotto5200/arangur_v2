# Canonical Portfolio Snapshot Contract

## Purpose

`CanonicalPortfolioSnapshot` is the source-neutral portfolio state consumed by valuation, exposure, scenario, and reporting components. Demo JSON, CSV, manual entry, Plaid, and future custodian or manager adapters should all normalize into this shape.

The snapshot should be deterministic, explicit about provenance, and stable enough for downstream code to avoid knowing which ingestion adapter produced it.

## Snapshot Envelope

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `schema_version` | Yes | string | Start with `canonical_portfolio_snapshot.v1`. |
| `snapshot_id` | Yes | string | Stable ID for this generated snapshot. |
| `as_of_date` | Yes | string | ISO valuation/snapshot date. |
| `created_at` | Optional | string | ISO timestamp if available. |
| `reporting_currency` | Yes | string | Recommended `USD` for v1. |
| `source` | Yes | object | Import metadata and provenance. |
| `portfolio` | Yes | object | Portfolio owner and demo metadata. |
| `managers` | Yes | array | Manager records. |
| `accounts` | Yes | array | Account records. |
| `securities` | Yes | array | Security master records. |
| `holdings` | Yes | array | Position records. |
| `cash_balances` | Yes | array | Cash records. |
| `transactions` | Optional | array | Optional transaction records. |
| `validation` | Yes | object | Warnings/errors produced during normalization. |

Example:

```json
{
  "schema_version": "canonical_portfolio_snapshot.v1",
  "snapshot_id": "snap_demo_family_office_2026_06_30",
  "as_of_date": "2026-06-30",
  "reporting_currency": "USD",
  "source": {
    "adapter": "demo_json",
    "dataset_id": "demo_family_office_v1",
    "is_synthetic": true
  }
}
```

## Source And Import Metadata

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `adapter` | Yes | string | Example: `demo_json`, `csv_import`, `plaid_mock`, `plaid`. |
| `dataset_id` | Optional | string | Source dataset identifier. |
| `source_files` | Optional | array | Local relative paths for fixture inputs. |
| `imported_at` | Optional | string | ISO timestamp. |
| `is_synthetic` | Yes | boolean | Must be `true` for demo fixtures. |
| `provenance_notes` | Optional | array | Human-readable notes. |

Downstream components may assume `source.adapter` exists and `source.is_synthetic` is explicit.

## Portfolio

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `portfolio_id` | Yes | string | Stable canonical portfolio identifier. |
| `portfolio_name` | Yes | string | Human-readable label. |
| `owner_label` | Yes | string | Fictional owner in demo data. |
| `advisor_label` | Optional | string | Advisor/team label. |
| `base_currency` | Yes | string | Same as reporting currency in v1. |
| `is_synthetic` | Yes | boolean | Must match source flag for demo data. |

## Managers

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `manager_id` | Yes | string | Canonical manager ID. |
| `display_name` | Yes | string | Manager name for reports. |
| `manager_type` | Optional | string | Source or strategy type. |
| `strategy_label` | Optional | string | Report-facing strategy name. |
| `source_ref` | Optional | object | Original source identifiers. |

## Accounts

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `account_id` | Yes | string | Canonical account ID. |
| `display_name` | Yes | string | Account name for reports. |
| `manager_id` | Yes | string | Must reference a manager. |
| `account_type` | Yes | string | Taxable, trust, IRA, foundation, cash, etc. |
| `currency` | Yes | string | Account currency. |
| `custodian_label` | Optional | string | Fictional in demo data. |
| `source_ref` | Optional | object | Original source identifiers. |
| `tags` | Optional | array | Account-level tags. |

## Securities

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `security_id` | Yes | string | Canonical security ID. |
| `display_name` | Yes | string | Security name. |
| `ticker` | Optional | string | Public ticker when useful. |
| `security_type` | Yes | string | Equity, ETF, fund, bond, cash, etc. |
| `currency` | Yes | string | Price currency. |
| `asset_class` | Yes | string | Basic asset class. |
| `sector` | Optional | string | Sector classification. |
| `themes` | Optional | array | Report and exposure tags. |
| `scenario_tags` | Optional | array | Scenario grouping tags. |
| `source_ref` | Optional | object | Original source identifiers. |

## Holdings

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `holding_id` | Yes | string | Canonical holding ID. |
| `account_id` | Yes | string | Must reference an account. |
| `security_id` | Yes | string | Must reference a security. |
| `quantity` | Yes | number | Non-negative in v1. |
| `quantity_unit` | Optional | string | Default `shares` for equities/funds. |
| `cost_basis` | Optional | number | Total cost basis, if supplied. |
| `cost_basis_currency` | Optional | string | Required when cost basis is supplied. |
| `source_ref` | Optional | object | Original source identifiers. |
| `tags` | Optional | array | Holding-level report tags. |

## Balances And Cash

Cash should be represented separately from security holdings in v1.

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `cash_id` | Yes | string | Canonical cash balance ID. |
| `account_id` | Yes | string | Must reference an account. |
| `currency` | Yes | string | Cash currency. |
| `amount` | Yes | number | Non-negative in v1. |
| `cash_type` | Optional | string | Sweep, money market, operating cash. |
| `source_ref` | Optional | object | Original source identifiers. |

## Transactions

Transactions are optional for the first vertical slice. If included, they should be preserved for narrative or later reconciliation, but valuation should not depend on them in v1.

Required fields if present: `transaction_id`, `account_id`, `trade_date`, `transaction_type`, `amount`, and `currency`.

## Valuation Date

The snapshot `as_of_date` is the valuation date used by local market data fixtures and reports. All holdings and cash balances in v1 are assumed to be valid as of that date.

## Provenance Fields

Every major entity may include a `source_ref` object. It should be opaque to downstream analytics except when reports need to explain synthetic/demo provenance.

Example:

```json
{
  "source_ref": {
    "source_system": "demo_json",
    "source_id": "hold_core_nvda"
  }
}
```

## Validation And Error Fields

The snapshot should carry validation output so downstream reports and tests can surface warnings.

```json
{
  "validation": {
    "status": "valid",
    "errors": [],
    "warnings": [
      {
        "code": "OPTIONAL_COST_BASIS_MISSING",
        "record_id": "hold_satellite_xom",
        "message": "Cost basis was not supplied."
      }
    ]
  }
}
```

Downstream components may proceed only when `validation.status` is `valid` or when a batch explicitly allows warnings.

## Assumptions And Limitations

- Long-only holdings.
- Cash is separate from securities.
- Single reporting currency in v1.
- No short positions, options, swaps, private assets, or look-through holdings.
- No tax-lot accounting.
- No performance attribution.
- No corporate actions.
- No live data or external APIs.

## Versioning Strategy

Use explicit string versions such as `canonical_portfolio_snapshot.v1`. Backward-incompatible changes should increment the major suffix. Small additive optional fields may remain in v1 if downstream components tolerate missing values.
