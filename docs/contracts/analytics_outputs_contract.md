# Analytics Outputs Contract

## Scope

The first analytics are deliberately simple:

- Long-only positions.
- Cash.
- Simple market value.
- Manager and account aggregation.
- Direct security overlap.
- Sector/theme exposure from supplied tags.
- Deterministic scenario shocks.

No v1 analytics should imply production-grade risk, advice, attribution, tax, or accounting treatment.

## ValuationResult

### Purpose

`ValuationResult` converts a `CanonicalPortfolioSnapshot` plus `MarketDataFixture` into position, cash, account, manager, and portfolio market values.

### Inputs

- `CanonicalPortfolioSnapshot`
- `MarketDataFixture`

### Required Output Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `valuation_result.v1`. |
| `snapshot_id` | string | Links to canonical snapshot. |
| `valuation_date` | string | ISO date. |
| `reporting_currency` | string | Recommended `USD`. |
| `positions` | array | Valued non-cash holdings. |
| `cash` | array | Cash balances valued at face amount. |
| `account_totals` | array | Totals by account. |
| `manager_totals` | array | Totals by manager. |
| `portfolio_total` | object | Total market value and cash included. |
| `validation` | object | Errors/warnings. |

### Position Fields

Required: `holding_id`, `account_id`, `manager_id`, `security_id`, `quantity`, `price`, `market_value`, `currency`, `valuation_date`.

Optional: `ticker`, `display_name`, `cost_basis`, `unrealized_gain_loss`, `asset_class`, `sector`, `themes`.

### Example

```json
{
  "holding_id": "hold_core_nvda",
  "security_id": "sec_nvda",
  "quantity": 120,
  "price": 142.50,
  "market_value": 17100.00,
  "currency": "USD"
}
```

### Known Limitations

- No accrued interest.
- No FX conversion.
- No tax-lot valuation.
- No private asset valuation.
- No short positions or derivatives.

## ExposureOverlapResult

### Purpose

`ExposureOverlapResult` summarizes how the valued portfolio is distributed across accounts, managers, asset classes, sectors, themes, and directly duplicated securities.

### Inputs

- `CanonicalPortfolioSnapshot`
- `MarketDataFixture`
- `ValuationResult`

### Required Output Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `exposure_overlap_result.v1`. |
| `snapshot_id` | string | Links to canonical snapshot. |
| `valuation_date` | string | ISO date. |
| `portfolio_market_value` | number | Denominator for exposure percentages. |
| `exposures` | object | Exposure arrays by dimension. |
| `overlaps` | array | Direct security overlaps across accounts/managers. |
| `concentration_notes` | array | Optional report-ready flags. |
| `validation` | object | Errors/warnings. |

### Exposure Dimensions

Required dimensions in v1:

- `by_account`
- `by_manager`
- `by_asset_class`
- `by_sector`
- `by_theme`
- `cash`

Each exposure row should include `bucket_id`, `bucket_label`, `market_value`, `portfolio_percent`, and optional `members`.

### Direct Overlap Fields

Required: `security_id`, `display_name`, `total_market_value`, `portfolio_percent`, `accounts`, `managers`.

Optional: `ticker`, `sector`, `themes`, `narrative_note`.

### Example

```json
{
  "security_id": "sec_msft",
  "ticker": "MSFT",
  "display_name": "Microsoft Corp.",
  "total_market_value": 88000,
  "portfolio_percent": 0.044,
  "accounts": ["acct_taxable_core", "acct_growth_satellite"],
  "managers": ["mgr_core_growth", "mgr_ai_satellite"]
}
```

### Assumptions

Exposure percentages should reconcile to portfolio market value within a small tolerance. Theme exposure can exceed 100 percent in aggregate when securities have multiple themes; reports should label this clearly.

## ScenarioDefinition

### Purpose

`ScenarioDefinition` describes a deterministic shock that can be applied to valued positions and cash.

### Required Fields

| Field | Type | Notes |
| --- | --- | --- |
| `scenario_id` | string | Stable scenario ID. |
| `scenario_name` | string | Report-facing name. |
| `scenario_date` | string | ISO assumption date or valuation date. |
| `description` | string | Plain-language explanation. |
| `shock_rules` | array | Ordered deterministic shock rules. |
| `default_shock` | number | Decimal return if no rule matches; often `0`. |
| `is_synthetic` | boolean | Must be `true` in demo fixtures. |

### Shock Rule Fields

Required: `match_type`, `match_value`, `shock_percent`.

Supported v1 `match_type` values:

- `security_id`
- `ticker`
- `asset_class`
- `sector`
- `theme`
- `cash`

Example:

```json
{
  "scenario_id": "scenario_ai_chips_selloff",
  "scenario_name": "AI and chip leadership selloff",
  "scenario_date": "2026-06-30",
  "description": "Illustrative shock to AI/chip-related holdings with a mild broad equity drag.",
  "default_shock": 0,
  "is_synthetic": true,
  "shock_rules": [
    { "match_type": "theme", "match_value": "ai", "shock_percent": -0.18 },
    { "match_type": "theme", "match_value": "chips", "shock_percent": -0.18 },
    { "match_type": "asset_class", "match_value": "equity", "shock_percent": -0.05 },
    { "match_type": "cash", "match_value": "cash", "shock_percent": 0 }
  ]
}
```

### Assumptions

If multiple rules match a position, v1 should use the most specific rule by this precedence: `security_id`, `ticker`, `theme`, `sector`, `asset_class`, `cash`, `default_shock`.

## ScenarioResult

### Purpose

`ScenarioResult` shows estimated value impact under one `ScenarioDefinition`.

### Inputs

- `CanonicalPortfolioSnapshot`
- `MarketDataFixture`
- `ValuationResult`
- `ScenarioDefinition`

### Required Output Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `scenario_result.v1`. |
| `snapshot_id` | string | Links to canonical snapshot. |
| `scenario_id` | string | Links to scenario definition. |
| `valuation_date` | string | ISO date. |
| `portfolio_before_value` | number | Baseline value. |
| `portfolio_after_value` | number | Shocked value. |
| `portfolio_impact_value` | number | After minus before. |
| `portfolio_impact_percent` | number | Impact divided by before. |
| `position_impacts` | array | Per-position shock output. |
| `account_impacts` | array | Aggregated by account. |
| `manager_impacts` | array | Aggregated by manager. |
| `exposure_impacts` | array | Optional sector/theme/asset-class impact buckets. |
| `validation` | object | Errors/warnings. |

### Position Impact Fields

Required: `holding_id`, `security_id`, `before_value`, `shock_percent`, `impact_value`, `after_value`, `matched_rule`.

Optional: `ticker`, `display_name`, `account_id`, `manager_id`, `sector`, `themes`.

### Example

```json
{
  "holding_id": "hold_core_nvda",
  "security_id": "sec_nvda",
  "before_value": 17100,
  "shock_percent": -0.18,
  "impact_value": -3078,
  "after_value": 14022,
  "matched_rule": "theme:ai"
}
```

### Known Limitations

- No covariance or portfolio risk model.
- No path dependency.
- No liquidity modeling.
- No tax impact.
- No macro calibration.
- Results are illustrative and deterministic.
