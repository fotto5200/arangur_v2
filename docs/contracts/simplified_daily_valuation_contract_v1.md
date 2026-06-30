# Simplified Daily Valuation Contract v1

## Purpose

`SimplifiedDailyValuation` is Surface 3 of the Arangur simulation kernel. It consumes:

- `SyntheticPositionUniverse`
- `SyntheticMarketStateHistory`
- `ScenarioMarketState`

and emits deterministic synthetic daily position values, portfolio aggregates, period value-change explanations, scenario revaluation results, confidence summaries, and validation output.

This is an internal support/runtime computation layer for the simulation kernel. It is not a user-facing workflow. It does not create UI, report packages, charts, client preview output, or browser routes.

## Output Files

Current generated files:

- `data/simulation/daily_position_valuation_history.json`
- `data/simulation/daily_portfolio_valuation_history.json`
- `data/simulation/value_change_package.json`
- `data/simulation/scenario_revaluation_results.json`
- `data/simulation/simplified_valuation_summary.json`

The current engine is:

- `src/arangur/simulation/daily_valuation.py`
- `src/arangur/simulation/simplified_daily_valuation_engine.py`

Regenerate from the repo root:

```powershell
python src\arangur\simulation\simplified_daily_valuation_engine.py
```

The engine reads:

- `data/simulation/synthetic_position_universe.json`
- `data/simulation/synthetic_market_state_history.json`
- `data/simulation/synthetic_scenario_market_states.json`

## Current Fixture Summary

Current default summary:

| Field | Value |
| --- | --- |
| Date range | `2026-04-01` through `2026-06-30` |
| Date count | 91 |
| Position count | 74 |
| Position valuation count | 6,734 |
| Portfolio valuation count | 91 |
| Scenario count | 5 |
| Current portfolio value | `40,695,000.00` |
| Human-review count | 12 positions |
| Validation status | `valid` |

## Daily Economic Valuation Model

The engine values the current Surface 1 positions on every Surface 2 market-state date. It intentionally uses current position quantities/notionals as the history baseline and records transactions separately as flow annotations. This keeps the demo deterministic and explainable without pretending to perform full portfolio accounting.

The general convention is:

```text
synthetic current reported value
* market-state ratio versus current market state
= simplified daily value
```

Market-state ratios are derived from each position's required market-state variables. The current date therefore ties back to the Surface 1 `current_reported_value` unless the position uses cash or bounded model treatment.

## Valuation Tiers

Supported valuation tiers:

- `direct_price_or_mark`
- `proxy_valuation`
- `simple_model_formula`
- `stale_or_manager_mark`
- `cash_face_value`
- `human_review_required`

These are explanatory tiers for simulation and downstream reporting. They are not production valuation policy.

## Instrument Behavior

Current simplified behavior:

| Instrument type | Simplified behavior |
| --- | --- |
| `cash` | Holds face/reference value through `cash_treatment`. |
| `money_market` | Blends `money_market_nav` and `cash_treatment`. |
| `public_equity` | Uses `underlying_price`. |
| `etf` | Blends `etf_price` and `optional_lookthrough_proxy`. |
| `fixed_income` | Blends `bond_price_proxy` and `duration_bucket_price`. |
| `fx_exposure` | Uses `fx_rate`. |
| `commodity` | Uses `commodity_price`. |
| `crypto` | Uses `crypto_price`. |
| `private_equity` | Blends `manager_mark` and `private_equity_proxy`. |
| `private_credit` | Blends `manager_mark` and inverse `credit_spread_proxy`. |
| `real_estate` | Blends `manager_mark`, `real_asset_proxy`, and `liquidity_discount_proxy`. |
| `data_center_investment` | Blends `private_mark`, `ai_infrastructure_proxy`, and `energy_price_proxy` as a cost pressure. |
| `opaque_manager_level` | Blends `manager_mark`, `manager_composite_proxy`, and `human_review_flag`. |
| `option_like` | Uses a bounded simple proxy formula from `underlying_price`, `volatility_proxy`, `rate_proxy`, and `time_to_maturity`. |

The option-like formula is deliberately small and caveated. It is not Black-Scholes and is not a production derivatives valuation model.

## Transaction And Flow Separation

Surface 1 transactions are not used to reconstruct exact historical tax lots or settlement positions. Instead, they are recorded as daily annotations and separated into:

- transaction/flow total;
- income and distributions;
- fees;
- mark-update amount annotations;
- economic value change excluding flows.

The daily position convention is:

```text
value_change_from_prior_date
- transaction_cash_flow_on_date
- income_distribution_on_date
- fee_on_date
= economic_value_change_excluding_flows
```

The period package excludes opening-date flow annotations from the tie-out because Surface 1 uses current positions as the starting baseline.

## DailyPositionValuation

Each position valuation record includes:

- `valuation_date`
- `position_id`
- `instrument_id`
- `manager_id`
- `account_id`
- `sleeve_id`
- `instrument_type`
- `asset_class`
- `themes`
- `liquidity_bucket`
- `valuation_method`
- `valuation_tier`
- `required_state_variables_used`
- `state_variable_values_used`
- `quantity_or_notional`
- `prior_value`
- `value`
- `value_change_from_prior_date`
- `transaction_cash_flow_on_date`
- `transaction_quantity_delta_on_date`
- `income_distribution_on_date`
- `fee_on_date`
- `mark_update_amount_on_date`
- `economic_value_change_excluding_flows`
- `confidence`
- `human_review_required`
- `caveats`
- `synthetic_data`

## DailyPortfolioValuation

Each daily portfolio valuation record includes:

- `valuation_date`
- `portfolio_id`
- `reporting_currency`
- `total_value`
- `value_change_from_prior_date`
- `transaction_flow_total`
- `income_distributions_total`
- `fees_total`
- `economic_value_change_total`
- `cash_value`
- `human_review_value`
- `human_review_count`
- `value_by_manager`
- `value_by_account`
- `value_by_sleeve`
- `value_by_asset_class`
- `value_by_theme`
- `value_by_liquidity_bucket`
- `confidence_summary`
- `human_review_items`
- `caveats`

Theme aggregation uses equal-split allocation across a position's themes so the theme total ties to portfolio value.

## ValueChangePackage

The period value-change package includes:

- `start_date`
- `end_date`
- `opening_value`
- `closing_value`
- `total_transactions_or_flows`
- `total_income_distributions`
- `total_fees`
- `total_market_or_economic_change`
- `opening_date_flow_annotations`
- `value_change_by_manager`
- `value_change_by_asset_class`
- `value_change_by_theme`
- `largest_positive_contributors`
- `largest_negative_contributors`
- `data_confidence_summary`
- `human_review_items`
- `caveats`

The package ties approximately as:

```text
opening_value
+ total_transactions_or_flows
+ total_income_distributions
+ total_fees
+ total_market_or_economic_change
= closing_value
```

## ScenarioRevaluationResult

Scenario revaluation consumes the current market state and every Surface 2 scenario market state. For each scenario, the engine:

- revalues every current position;
- compares scenario value to base current value;
- aggregates impact by manager;
- aggregates impact by asset class;
- aggregates impact by theme;
- emits confidence and human-review summaries;
- preserves scenario completeness and caveats.

This is deterministic scenario revaluation, not stochastic simulation or Monte Carlo.

## Validation Expectations

`validate_daily_valuation_history` returns:

- `status`
- `errors`
- `warnings`
- `counts`

Validation checks include:

- metadata and synthetic flags exist;
- every Surface 2 market-state date has portfolio valuation;
- every Surface 1 position has valuation for every Surface 2 date;
- position records include required transaction/flow and confidence fields;
- required state variables are used unless explicitly human-review-only;
- portfolio totals tie to summed position values;
- manager, account, sleeve, asset-class, theme, and liquidity aggregates tie to totals;
- value-change package ties opening value, flows, income, fees, and economic movement to closing value;
- scenario revaluation exists for every scenario;
- scenario impacts aggregate from positions to portfolio;
- prohibited external-source markers are absent;
- report-generation markers are absent.

## Demo Limitations

- Fully synthetic data only.
- No live Plaid.
- No external APIs.
- No vendor market data.
- No UI changes.
- No report generation.
- No production accounting.
- No tax-lot accounting.
- No settlement-date reconciliation.
- No full fixed-income accrual, carry, amortization, or day-count logic.
- No production private-equity, private-credit, or real-estate accounting.
- No client statement or performance-reporting claims.

## Future Production Replacement Path

A future production system can replace this engine with approved portfolio accounting, valuation, performance, and risk services. The useful downstream boundary is the stable output vocabulary:

- daily position values;
- daily portfolio aggregates;
- value-change packages;
- scenario revaluation results;
- confidence and human-review summaries;
- caveats and provenance.

Report elements should consume those outputs through contracts, not through generator internals.
