# Market Data Fixture Contract

## Purpose

The market data fixture provides deterministic local prices and classifications for the first demo. It should be static, hand-reviewable, and compatible with JSON or CSV.

Recommended v1 file: `data/demo/market_data.json`.

## Fixture Envelope

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `schema_version` | Yes | string | Start with `market_data_fixture.v1`. |
| `fixture_id` | Yes | string | Stable fixture identifier. |
| `valuation_date` | Yes | string | ISO date matching the canonical snapshot `as_of_date`. |
| `currency` | Yes | string | Recommended `USD` for v1. |
| `is_synthetic` | Yes | boolean | Must be `true` for committed demo fixtures. |
| `prices` | Yes | array | Price/classification records. |

## Price Records

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `security_id` | Yes | string | Should match canonical security ID. |
| `ticker` | Optional | string | Useful for readability. |
| `price` | Yes | number | Must be non-negative. |
| `currency` | Yes | string | Price currency. |
| `price_date` | Yes | string | ISO date, usually fixture valuation date. |
| `prior_price` | Optional | number | Useful for simple change examples. |
| `prior_price_date` | Optional | string | ISO date when prior price is supplied. |
| `asset_class` | Optional | string | May duplicate security classification for convenience. |
| `sector` | Optional | string | Sector classification. |
| `themes` | Optional | array | Theme tags such as `ai`, `chips`, `energy`, `value`, `growth`. |
| `shock_sensitivity` | Optional | object | Optional scenario sensitivities by shock tag. |

Example:

```json
{
  "security_id": "sec_nvda",
  "ticker": "NVDA",
  "price": 142.50,
  "currency": "USD",
  "price_date": "2026-06-30",
  "prior_price": 130.00,
  "prior_price_date": "2026-03-31",
  "asset_class": "equity",
  "sector": "technology",
  "themes": ["ai", "chips", "growth"],
  "shock_sensitivity": {
    "ai_chips_selloff": -0.18,
    "broad_equity_down": -0.10
  }
}
```

## Optional Shock Sensitivity Fields

Scenario sensitivity can be supplied as decimal returns keyed by scenario shock tag. A value of `-0.18` means the security value declines by 18 percent for that shock.

If no explicit sensitivity exists, the scenario service may fall back to sector, theme, asset-class, or default shocks defined by `ScenarioDefinition`.

## Missing-Price Behavior

For v1, missing prices should block valuation for non-cash holdings. The error should identify:

- `security_id`
- `ticker`, if available
- affected `holding_id` values
- expected `valuation_date`

Cash should not require a market price; it is valued at face amount.

## Validation Expectations

- `valuation_date` must match the canonical snapshot `as_of_date`.
- Every non-cash security with a holding must have exactly one price record.
- Price records must use non-negative prices.
- Price currency should match the security currency in v1.
- Fixture currency should match the reporting currency in v1.
- Duplicate `security_id` records are invalid unless a future version supports multiple dates.
- Optional classifications should not contradict canonical security classifications; if they differ, validation should warn.

## Static JSON Shape

```json
{
  "schema_version": "market_data_fixture.v1",
  "fixture_id": "demo_market_data_2026_06_30",
  "valuation_date": "2026-06-30",
  "currency": "USD",
  "is_synthetic": true,
  "prices": []
}
```

## CSV Compatibility

A CSV version should be flat and use delimited strings for arrays:

| security_id | ticker | price | currency | price_date | asset_class | sector | themes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sec_nvda` | `NVDA` | `142.50` | `USD` | `2026-06-30` | `equity` | `technology` | `ai;chips;growth` |
