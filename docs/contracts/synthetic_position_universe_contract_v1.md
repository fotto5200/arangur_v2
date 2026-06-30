# Synthetic Position Universe Contract v1

## Purpose

`SyntheticPositionUniverse` is the Surface 1 fixture for the Arangur simulation kernel. It creates a deterministic, serializable, fully synthetic multi-manager family-office portfolio universe that future batches can feed into:

- synthetic market/state generation;
- simplified daily valuation;
- scenario simulation;
- report element templates;
- Client Briefing Set and Advisor Review Set composition.

This contract intentionally stops before market-state generation and valuation. It declares future market-state requirements, but it does not generate prices, rates, FX paths, volatility paths, scenario states, daily values, or value-change packages.

## Output Files

Current generated files:

- `data/simulation/synthetic_position_universe.json`
- `data/simulation/synthetic_position_universe_summary.json`

The current generator is:

- `src/arangur/simulation/position_universe.py`
- `src/arangur/simulation/synthetic_position_universe_generator.py`

Regenerate from the repo root:

```powershell
python src\arangur\simulation\synthetic_position_universe_generator.py
```

## Universe Metadata

Top-level fields:

| Field | Required | Notes |
| --- | --- | --- |
| `schema_version` | Yes | `simulation_position_universe.v1`. |
| `universe_id` | Yes | Stable deterministic universe ID, including the seed. |
| `generated_at` | Yes | Fixed timestamp for deterministic fixture output. |
| `generator_version` | Yes | Generator version string. |
| `synthetic_data` | Yes | Must be `true`. |
| `as_of_date` | Yes | Current synthetic universe date. |
| `history_start_date` | Yes | Start of transaction/history trace. |
| `history_end_date` | Yes | End of transaction/history trace. |
| `reporting_currency` | Yes | `USD` in v1. |
| `base_currency` | Yes | `USD` in v1. |
| `source` | Yes | Generator, seed, dataset, and synthetic flag. |
| `portfolio` | Yes | Fictional portfolio/client metadata. |
| `caveats` | Yes | Synthetic-data and non-valuation caveats. |

The current portfolio label is `Northstar Family Office`, a fictional demo family-office context.

## Managers, Accounts, And Sleeves

The current universe includes six synthetic managers:

- Manager A - Growth / AI Infrastructure
- Manager B - Core Quality Equity
- Manager C - Income and Cash Generation
- Manager D - Private Markets / Real Assets
- Manager E - Liquidity Reserve / Defensive Ballast
- Manager F - Opportunistic Macro / Hedge

Manager fields include:

- `manager_id`
- `display_name`
- `mandate`
- `intended_role`
- `strategy_summary`
- `expected_contribution`
- `liquidity_profile`
- `primary_themes`
- `accounts`
- `sleeves`
- `synthetic_data`

Accounts and sleeves are separate records, each linked to a manager. Every position references a manager, account, and sleeve. This supports future manager-role review, manager overlap analysis, and "why do we own this manager?" stories without treating plain `Manager` as a lens.

## Instruments

Instrument records define synthetic assets and their future state requirements.

Key fields:

- `instrument_id`
- `display_name`
- `synthetic_identifier`
- `instrument_type`
- `asset_class`
- `currency`
- `sector`
- `industry`
- `geography`
- `public_private`
- `required_market_state_variables`
- `valuation_method_hint`
- `proxy_mapping_hint`
- `scenario_exposure_hints`
- `lookthrough_status`
- `themes`
- `synthetic_data`

The current universe covers:

- public equities;
- ETFs;
- fixed income and rate-sensitive instruments;
- FX exposures;
- commodities and energy;
- Bitcoin/crypto-style exposures;
- private equity fund interests;
- private credit;
- real estate;
- data center investment;
- cash and money market positions;
- opaque manager-level positions;
- option-like or structured exposures.

## Positions

Position records are the main Surface 1 output. Current fixture size is 74 positions.

Key fields:

- `position_id`
- `instrument_id`
- `manager_id`
- `account_id`
- `sleeve_id`
- `display_name`
- `instrument_type`
- `synthetic_identifier`
- `quantity`
- `quantity_unit`
- `notional`
- `base_currency`
- `cost_basis`
- `initial_reference_value`
- `current_reported_value`
- `ownership_status`
- `valuation_method_hint`
- `required_market_state_variables`
- `liquidity_bucket`
- `valuation_confidence`
- `data_quality_flags`
- `human_review_required`
- `lookthrough_status`
- `proxy_mapping_hint`
- `scenario_exposure_hints`
- `classifications`
- `themes`
- `future_valuation_requirements`
- `synthetic_data`

`initial_reference_value` and `current_reported_value` are synthetic placeholder/reference amounts. They are not generated market prices and should not be interpreted as vendor data or valuation output.

## Lens And Classification Fields

Each position has a `classifications` object with:

- `asset_class`
- `sector`
- `industry`
- `geography`
- `currency_exposure`
- `liquidity_bucket`
- `value_growth_style`
- `cash_generation_role`
- `manager_role_or_mandate`
- `data_issue_category`
- `instrument_type`

Required themes include:

- AI infrastructure
- semiconductors
- data center power demand
- energy bottlenecks
- rates sensitivity
- private-market liquidity
- cash generation
- growth/value
- defensive ballast
- manager overlap
- inflation sensitivity
- USD exposure
- crypto risk
- opaque/private marks
- data confidence / valuation issue

Plain `Manager` is not a lens. `manager_role_or_mandate` is a supported lens because it classifies managers by their intended job.

## Future Valuation Requirement Fields

Each instrument and position declares `required_market_state_variables` for later Surface 2 and Surface 3 batches.

Examples:

- public equity: `underlying_price`
- ETF: `etf_price`, `optional_lookthrough_proxy`
- fixed income: `bond_price_proxy`, `duration_bucket_price`
- FX: `fx_rate`
- commodity: `commodity_price`
- crypto: `crypto_price`
- private equity: `manager_mark`, `private_equity_proxy`
- private credit: `manager_mark`, `credit_spread_proxy`
- real estate: `manager_mark`, `real_asset_proxy`, `liquidity_discount_proxy`
- data center: `private_mark`, `ai_infrastructure_proxy`, `energy_price_proxy`
- cash: `cash_treatment`
- money market: `money_market_nav`, `cash_treatment`
- opaque manager-level: `manager_mark`, `manager_composite_proxy`, `human_review_flag`
- option-like exposure: `underlying_price`, `volatility_proxy`, `rate_proxy`, `time_to_maturity`

The current fixture declares requirements only. It does not generate the required state variables.

## Data Quality And Confidence

Positions can carry:

- `valuation_confidence`: `high`, `medium`, `low`, or `unknown`;
- `data_quality_flags`;
- `human_review_required`;
- `lookthrough_status`;
- `data_issue_category`;
- `proxy_mapping_hint`.

The top-level universe also includes:

- `data_quality_flags`
- `human_review_items`

Intentional examples include stale private marks, opaque manager-level positions, missing look-through, missing cost basis, complex option-like terms, and energy-input requirements for data center assets.

## Transactions

The current universe includes 82 synthetic transactions spanning 90 days, from `2026-04-01` through `2026-06-30`.

Transaction fields:

- `transaction_id`
- `date`
- `account_id`
- `position_id`
- `manager_id`
- `transaction_type`
- `quantity_delta`
- `notional_delta`
- `cash_amount`
- `currency`
- `description`
- `synthetic_data`

Transaction types include:

- `buy`
- `sell`
- `contribution`
- `withdrawal`
- `income`
- `distribution`
- `fee`
- `mark_update`

These transactions are deliberately simple. They do not attempt tax-lot accounting, settlement-date modeling, perfect accrual, or production P&L recognition.

## Intentional Demo Stories

The fixture intentionally includes:

- AI/chip/growth overlap across Manager A and Manager B;
- a liquidity/defensive manager that may look weak on raw P&L but serves a mandate;
- private/opaque positions with lower confidence;
- data center and power infrastructure exposure;
- energy and commodity exposure;
- rate-sensitive holdings;
- FX and USD exposure;
- cash-generation assets;
- positions requiring proxy valuation later;
- positions requiring human review;
- stale/private marks;
- option-like and multi-input valuation requirements.

These stories are visible through `themes`, `position_story_tags`, `intentional_stories`, `data_quality_flags`, and `human_review_items`.

## Validation Expectations

`validate_synthetic_position_universe` returns:

- `status`
- `errors`
- `warnings`
- `counts`

Validation checks include:

- required metadata and sections exist;
- managers, accounts, sleeves, instruments, positions, and transactions exist;
- IDs are unique within each section;
- positions reference valid managers, accounts, sleeves, and instruments;
- transactions reference valid positions or accounts and managers;
- at least 50 positions exist;
- required asset classes are represented;
- required themes are represented;
- at least one human-review item exists;
- at least one private/opaque/stale mark exists;
- at least one manager-overlap story exists;
- every position declares required market-state variables;
- every position has required lens/classification fields;
- synthetic flags are present;
- prohibited real-client/credential markers are absent.

## Future Connection

The next Surface 2 batch should consume this universe and generate:

- direct prices or marks;
- rates proxies;
- FX;
- volatility proxies;
- credit spread proxies;
- private marks;
- proxy mappings;
- historical paths;
- scenario states;
- completeness and confidence summaries.

The Surface 3 valuation engine should then consume:

```text
SyntheticPositionUniverse + MarketStateHistory/Snapshot + transactions
```

and emit daily values and value-change packages.

## Demo Limitations

- Fully synthetic data only.
- No real client data.
- No live Plaid.
- No external APIs.
- No vendor market data.
- No prices or market-state paths in this batch.
- No valuation engine in this batch.
- No production accounting.
- No tax-lot, settlement, carry/accrual, day-count, or private-fund accounting.
- No report generation connection yet.
