# Demo Data Contract

## Purpose

The demo data contract defines the local synthetic inputs for the first Arangur v2 vertical slice. The data should be easy to hand-author, deterministic, and safe to commit. It must not contain real client data.

Recommended v1 format: JSON files under `data/demo/`. JSON is preferable for the first batch because account metadata, holdings, themes, and scenarios are nested enough that one readable file is easier than multiple CSV joins. CSV can be added later for adapter testing.

## Expected Files

- `data/demo/portfolio.json`: Portfolio, family/client metadata, managers, accounts, holdings, cash, and optional transactions.
- `data/demo/market_data.json`: Prices and classifications, defined in `market_data_fixture_contract.md`.
- `data/demo/scenarios.json`: Scenario definitions, defined in `analytics_outputs_contract.md`.

The next implementation batch may choose a single combined JSON file if that keeps the first vertical slice simpler, but it should keep sections aligned with these contracts.

## Portfolio Metadata

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `dataset_id` | Yes | string | Stable synthetic dataset identifier, such as `demo_family_office_v1`. |
| `dataset_label` | Yes | string | Human-readable demo name. |
| `is_synthetic` | Yes | boolean | Must be `true` for committed demo data. |
| `valuation_date` | Yes | string | ISO date, such as `2026-06-30`. |
| `reporting_currency` | Yes | string | Recommended `USD` for v1. |
| `portfolio_owner_label` | Yes | string | Fictional family/client label. |
| `advisor_label` | Optional | string | Fictional advisor or team label. |
| `notes` | Optional | string | Demo storyline notes. |

Example:

```json
{
  "dataset_id": "demo_family_office_v1",
  "dataset_label": "Northstar Family Office Synthetic Portfolio",
  "is_synthetic": true,
  "valuation_date": "2026-06-30",
  "reporting_currency": "USD",
  "portfolio_owner_label": "Northstar Family",
  "advisor_label": "Arangur Demo Advisory Team"
}
```

## Manager Records

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `manager_id` | Yes | string | Stable local identifier. |
| `manager_name` | Yes | string | Fictional manager name. |
| `manager_type` | Optional | string | Example: `advisor`, `direct_index`, `satellite_manager`, `cash_provider`. |
| `strategy_label` | Optional | string | Example: `Core Growth`, `Value Sleeve`. |
| `notes` | Optional | string | Demo explanation. |

```json
{
  "manager_id": "mgr_core_growth",
  "manager_name": "Atlas Core Growth",
  "manager_type": "advisor",
  "strategy_label": "Core Growth"
}
```

## Account Records

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `account_id` | Yes | string | Stable local identifier. |
| `account_name` | Yes | string | Fictional account label. |
| `manager_id` | Yes | string | Must reference a manager. |
| `account_type` | Yes | string | Example: `taxable`, `ira`, `trust`, `foundation`, `cash`. |
| `currency` | Yes | string | Recommended `USD` in v1. |
| `custodian_label` | Optional | string | Fictional custodian label. |
| `household_member` | Optional | string | Fictional owner label, if useful. |
| `tags` | Optional | array | Account-level themes. |

```json
{
  "account_id": "acct_taxable_core",
  "account_name": "Taxable Core Account",
  "manager_id": "mgr_core_growth",
  "account_type": "taxable",
  "currency": "USD",
  "custodian_label": "Demo Custody"
}
```

## Security Records

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `security_id` | Yes | string | Canonical local identifier used by holdings and market data. |
| `name` | Yes | string | Security name. |
| `ticker` | Optional | string | Public ticker when available. |
| `security_type` | Yes | string | Example: `equity`, `etf`, `mutual_fund`, `cash`, `bond`. |
| `currency` | Yes | string | Price currency. |
| `asset_class` | Yes | string | Example: `equity`, `fixed_income`, `cash`. |
| `sector` | Optional | string | Sector label. |
| `themes` | Optional | array | Example: `["ai", "chips", "growth"]`. |
| `scenario_tags` | Optional | array | Tags used by deterministic shocks. |

```json
{
  "security_id": "sec_nvda",
  "ticker": "NVDA",
  "name": "NVIDIA Corp.",
  "security_type": "equity",
  "currency": "USD",
  "asset_class": "equity",
  "sector": "technology",
  "themes": ["ai", "chips", "growth"],
  "scenario_tags": ["ai_chips"]
}
```

## Holding Records

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `holding_id` | Yes | string | Stable local identifier. |
| `account_id` | Yes | string | Must reference an account. |
| `security_id` | Yes | string | Must reference a security. |
| `quantity` | Yes | number | Long-only in v1; must be non-negative. |
| `cost_basis` | Optional | number | Total cost basis in account currency. |
| `acquired_date` | Optional | string | ISO date if useful. |
| `manager_note` | Optional | string | Demo explanation for duplication or exposure. |

```json
{
  "holding_id": "hold_core_nvda",
  "account_id": "acct_taxable_core",
  "security_id": "sec_nvda",
  "quantity": 120,
  "cost_basis": 51000,
  "manager_note": "Core manager position also appears in satellite account."
}
```

## Cash Balances

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `cash_id` | Yes | string | Stable local identifier. |
| `account_id` | Yes | string | Must reference an account. |
| `currency` | Yes | string | Recommended `USD` in v1. |
| `amount` | Yes | number | Cash balance at valuation date. |
| `cash_type` | Optional | string | Example: `sweep`, `money_market`, `operating_cash`. |

```json
{
  "cash_id": "cash_taxable_core_usd",
  "account_id": "acct_taxable_core",
  "currency": "USD",
  "amount": 42500,
  "cash_type": "sweep"
}
```

## Optional Transactions

Transactions are optional in v1 and should not be required for valuation.

| Field | Required If Present | Type | Notes |
| --- | --- | --- | --- |
| `transaction_id` | Yes | string | Stable local identifier. |
| `account_id` | Yes | string | Must reference an account. |
| `security_id` | Optional | string | Required for buy/sell/dividend tied to a security. |
| `trade_date` | Yes | string | ISO date. |
| `transaction_type` | Yes | string | Example: `buy`, `sell`, `deposit`, `withdrawal`, `dividend`. |
| `quantity` | Optional | number | Security quantity. |
| `amount` | Yes | number | Cash amount. |
| `currency` | Yes | string | Transaction currency. |

## Optional Themes And Tags

Themes and tags may appear on accounts, securities, or holdings. V1 analytics should treat security-level tags as the primary source for exposure and scenario grouping.

Recommended theme examples:

- `ai`
- `chips`
- `energy`
- `value`
- `growth`
- `quality`
- `defensive`
- `cash_buffer`

## Optional Scenario Classification Fields

Scenario classification can be supplied on securities as `scenario_tags` or in market data as `shock_sensitivity`. V1 should prefer explicit scenario tags over inferred tags.

## Validation Expectations

- `is_synthetic` must be `true`.
- All IDs must be unique within their section.
- Holdings must reference known accounts and securities.
- Accounts must reference known managers.
- Cash balances must reference known accounts.
- Quantities and cash amounts must be non-negative in v1.
- All currencies should equal the reporting currency in v1 unless multi-currency support is explicitly added later.
- Every non-cash security with a holding must have a market data price.
- Validation errors should identify the section, record identifier, field, and issue.

## Fields Required Vs Optional Summary

Required sections for v1:

- Portfolio metadata.
- Managers.
- Accounts.
- Securities.
- Holdings.
- Cash balances, even if represented as an empty list.

Optional sections for v1:

- Transactions.
- Themes beyond basic sector tags.
- Scenario classification beyond simple supplied tags.
- Narrative notes.
