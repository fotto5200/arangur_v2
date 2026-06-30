# Simulation Kernel Contracts v1

## Purpose

These first-pass contracts define the interfaces for the three-surface simulation kernel:

1. Synthetic Position Universe.
2. Synthetic Market / State-of-World Generator.
3. Simplified Daily Valuation Engine.

The contracts are intentionally JSON-friendly and demo-oriented. They should be stable enough for report element templates, briefing sets, and future implementation batches, while remaining replaceable by production ingestion, vendor market data, and production valuation/accounting systems later.

## Common Conventions

- All data is synthetic unless a future authorized production adapter says otherwise.
- Date fields use ISO `YYYY-MM-DD`.
- Timestamp fields use ISO datetime strings when needed.
- Money fields include currency unless inherited from an envelope.
- IDs are stable within a simulation run.
- Every output includes `schema_version`.
- Every output should include provenance and confidence where the result could be mistaken for production truth.

## SyntheticPositionUniverse

### Purpose

`SyntheticPositionUniverse` is the output of the synthetic position generator. It defines the demo portfolio, managers, accounts, sleeves, instruments, positions, cash, transactions, themes, and data-quality flags that downstream simulation and reporting consume.

### Key Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `simulation_position_universe.v1`. |
| `universe_id` | string | Stable ID for this generated synthetic universe. |
| `as_of_date` | string | Current synthetic portfolio date. |
| `history_start_date` | string | Start of supported transaction/history window, initially at least 90 days before `as_of_date`. |
| `reporting_currency` | string | Recommended `USD` for v1. |
| `source` | object | Must include `is_synthetic: true`, generator name, seed, and dataset label. |
| `portfolio` | object | Fictional portfolio owner, advisor/team label, and demo narrative metadata. |
| `managers` | array | Manager records with role, mandate, confidence, and source metadata. |
| `accounts` | array | Account records tied to managers and optional sleeves. |
| `sleeves` | array | Optional sleeve/mandate records. |
| `instruments` | array | Public, private, cash-like, proxy, and manager-level instrument records. |
| `positions` | array | Position records, expected 50-100 in v1. |
| `cash_balances` | array | Explicit cash and money-market balances. |
| `transactions` | array | 90-day synthetic transaction and flow records. |
| `themes` | array | Theme/lens definitions used by positions and reports. |
| `data_quality_flags` | array | Universe-level and record-level confidence or review flags. |
| `human_review_items` | array | Items that require advisor or data review. |

Instrument and position records should support public equities, ETFs, fixed income/rate-sensitive instruments, FX, commodities/energy, Bitcoin/crypto, private equity, private credit, real estate, data center investment, cash/money market, and opaque manager-level positions.

### Relationship To Existing Contracts

The universe should be able to emit or map into `CanonicalPortfolioSnapshot`. It may be richer than the current canonical snapshot contract because it includes broader private-market metadata, history, valuation tiers, themes, and data-confidence flags.

The report element system should not depend directly on generator internals. It should consume canonical snapshots, valuation outputs, value-change packages, confidence summaries, and scenario outputs derived from the universe.

### Demo Simplifications

- Fictional portfolio and manager records only.
- Long-only economic positions in v1.
- Simplified transaction records.
- No tax lots or settlement accounting.
- Opaque manager positions are allowed when explicitly flagged.
- Private marks may be stale or manual.

### Future Production Replacement Path

Production ingestion can replace this output with normalized records from Plaid, custodians, manager statements, CSV uploads, or manual review workflows. The replacement should still provide enough metadata for canonical snapshots, valuation confidence, and report elements.

## MarketStateSnapshot

### Purpose

`MarketStateSnapshot` describes the synthetic market/state-of-world for one date. It includes direct prices, price-like rates proxies, FX, volatility proxies, credit spread proxies, private marks, proxy mappings, confidence flags, and completeness status.

### Key Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `simulation_market_state_snapshot.v1`. |
| `market_state_id` | string | Stable snapshot ID. |
| `state_date` | string | ISO date for the state. |
| `reporting_currency` | string | Recommended `USD`. |
| `source` | object | Synthetic generator name, seed, scenario/run linkage, and `is_synthetic: true`. |
| `driver_values` | array | Core market driver levels or returns for the date. |
| `instrument_states` | array | Price, mark, proxy, model input, or cash treatment for each instrument. |
| `fx_rates` | array | Currency pair state. |
| `rates_proxies` | array | Price-like rates instruments or curve proxy state. |
| `volatility_proxies` | array | Vol or stress proxy state. |
| `credit_spread_proxies` | array | Spread proxy state. |
| `private_marks` | array | Private asset marks and stale/opaque flags. |
| `proxy_mappings` | array | Instrument-to-proxy or instrument-to-driver mapping metadata. |
| `data_confidence` | array | Confidence tiers by driver, instrument, proxy, or mark. |
| `completeness` | object | Counts of direct price, proxy, model, stale mark, cash, and human-review treatments. |
| `human_review_items` | array | Missing or low-confidence state items. |

### Relationship To Existing Contracts

`MarketStateSnapshot` generalizes the current `MarketDataFixture` idea. A future adapter can translate this state into the existing valuation inputs while richer report elements consume confidence and proxy details.

### Demo Simplifications

- Generated locally from deterministic assumptions.
- Rates may be expressed through proxy instruments instead of full yield curves.
- Private marks can be carried forward or updated by simple rules.
- Confidence is a demo signal, not a production certification.

### Future Production Replacement Path

Vendor prices, approved curves, FX feeds, internal marks, valuation committees, and data-quality workflows can replace the generator while preserving the same downstream state vocabulary.

## MarketStateHistory

### Purpose

`MarketStateHistory` is the generated historical path used for daily valuation, trend reporting, covariance checks, and scenario calibration examples.

### Key Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `simulation_market_state_history.v1`. |
| `history_id` | string | Stable history ID. |
| `start_date` | string | First generated date. |
| `end_date` | string | Last generated date. |
| `frequency` | string | Usually `daily`. |
| `source` | object | Synthetic generator metadata, seed, and covariance profile ID. |
| `core_drivers` | array | Driver definitions and source covariance assumptions. |
| `driver_history` | array | Date-by-date driver levels or returns. |
| `instrument_history` | array | Date-by-date prices, marks, proxies, or model state. |
| `snapshots` | array | Optional embedded or referenced `MarketStateSnapshot` records. |
| `covariance_recovery_check` | object | Estimated covariance, source covariance, tolerance, and status. |
| `data_confidence_history` | array | Date-by-date confidence and stale mark state when useful. |

### Relationship To Existing Contracts

The history supplies the market side of daily valuation. It can also support scenario reports, data coverage reports, and future report elements that need trailing-period context.

### Demo Simplifications

- Generated from synthetic covariance and beta assumptions.
- Short initial horizon, at least 90 days.
- No claim that generated history is observed market history.

### Future Production Replacement Path

Historical vendor data, approved internal marks, and production risk data can replace the generated path. The covariance recovery check can become one quality check among richer model validation tools.

## ScenarioMarketState

### Purpose

`ScenarioMarketState` represents a synthetic scenario applied to the market/state universe. It should reuse the same driver, instrument, proxy, and confidence vocabulary as `MarketStateSnapshot`.

### Key Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `simulation_scenario_market_state.v1`. |
| `scenario_state_id` | string | Stable scenario state ID. |
| `scenario_id` | string | Scenario library ID. |
| `base_market_state_id` | string | Snapshot or history point used as base. |
| `scenario_name` | string | Human-readable label. |
| `scenario_date` | string | Assumption date. |
| `horizon` | string | Example: `instant`, `30_day`, or `90_day`. |
| `driver_shocks` | array | Core driver shocks. |
| `instrument_states` | array | Shocked prices, marks, or proxy values. |
| `proxy_mappings` | array | Mapping used to translate driver shocks. |
| `confidence_summary` | object | Direct, proxy, stale, and human-review counts. |
| `caveats` | array | Scenario caveats for reports. |

### Relationship To Existing Contracts

This extends the current `ScenarioDefinition` and `ScenarioResult` flow. Scenario-dependent report element templates should use scenario IDs, scenario state, scenario valuation outputs, and completeness/confidence summaries.

### Demo Simplifications

- Hand-authored or generated assumptions only.
- No market forecast claims.
- No external scenario-source data unless a future authorized batch adds it.

### Future Production Replacement Path

Future scenario libraries can source assumptions from approved internal models, advisor templates, or licensed providers while preserving the scenario state contract for downstream reporting.

## DailyPositionValuation

### Purpose

`DailyPositionValuation` records one position's value and value-change components for one date.

### Key Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `simulation_daily_position_valuation.v1`. |
| `valuation_date` | string | ISO date. |
| `position_id` | string | References `SyntheticPositionUniverse.positions`. |
| `instrument_id` | string | References the instrument valued. |
| `account_id` | string | Account reference. |
| `manager_id` | string | Manager reference. |
| `sleeve_id` | string/null | Optional sleeve or mandate. |
| `currency` | string | Position valuation currency. |
| `opening_quantity` | number | Quantity at start of day. |
| `closing_quantity` | number | Quantity at end of day. |
| `opening_value` | number | Start-of-day value. |
| `transactions_value` | number | Net buys/sells/contributions/withdrawals applied to the position. |
| `income_distributions` | number | Income, coupons, dividends, distributions, or private distributions. |
| `market_value_change` | number | Economic value change excluding flows and income where possible. |
| `closing_value` | number | End-of-day value. |
| `valuation_tier` | string | `direct_price`, `proxy`, `simple_model`, `stale_manager_mark`, or `human_review_required`. |
| `market_state_ref` | object | Direct price, mark, proxy, or model inputs used. |
| `confidence` | object | Data and valuation confidence summary. |
| `review_flags` | array | Human-review flags. |

### Relationship To Existing Contracts

This is a richer daily version of current valuation output. Existing `ValuationResult` can be derived from the latest daily position valuations by aggregation.

### Demo Simplifications

- Economic value changes only.
- Simplified income/distribution handling.
- No tax lots, settlement reconciliation, or production carry/accrual.

### Future Production Replacement Path

A production accounting or valuation engine can replace this output while preserving downstream aggregation and report element fields.

## DailyPortfolioValuation

### Purpose

`DailyPortfolioValuation` aggregates daily position values to portfolio, manager, account, sleeve, asset class, theme/lens, liquidity, and confidence summaries.

### Key Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `simulation_daily_portfolio_valuation.v1`. |
| `valuation_date` | string | ISO date. |
| `portfolio_id` | string | Portfolio reference. |
| `reporting_currency` | string | Aggregation currency. |
| `opening_value` | number | Portfolio opening value. |
| `transactions_value` | number | Net flows. |
| `income_distributions` | number | Income and distributions. |
| `market_value_change` | number | Value change excluding flows/income where possible. |
| `closing_value` | number | Portfolio closing value. |
| `position_values` | array | `DailyPositionValuation` records or references. |
| `account_values` | array | Account-level aggregates. |
| `manager_values` | array | Manager-level aggregates. |
| `sleeve_values` | array | Sleeve/mandate-level aggregates. |
| `theme_values` | array | Theme and lens aggregates. |
| `asset_class_values` | array | Asset-class aggregates. |
| `confidence_summary` | object | Valuation tier and data confidence counts. |
| `human_review_items` | array | Review queue for the date. |

### Relationship To Existing Contracts

This can back portfolio status, manager comparison, concentration, data confidence, and scenario report elements. It can also be converted into current report packages while richer contracts are introduced.

### Demo Simplifications

- Single reporting currency unless a later batch adds FX translation.
- Simple aggregation from position-level output.
- Confidence is explanatory, not a production attestation.

### Future Production Replacement Path

Future portfolio accounting and performance systems can emit equivalent aggregates, ideally retaining the value-change component split and confidence summary.

## ValueChangePackage

### Purpose

`ValueChangePackage` packages value-change explanations over a period so reports can distinguish flows, income, market/value change, scenario impact, and confidence issues.

### Key Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `simulation_value_change_package.v1`. |
| `package_id` | string | Stable package ID. |
| `portfolio_id` | string | Portfolio reference. |
| `start_date` | string | Period start. |
| `end_date` | string | Period end. |
| `reporting_currency` | string | Aggregation currency. |
| `opening_value` | number | Beginning value. |
| `closing_value` | number | Ending value. |
| `net_flows` | number | Contributions, withdrawals, buys/sells, and other flow-like activity. |
| `income_distributions` | number | Income and distributions. |
| `market_value_change` | number | Residual or directly calculated value change. |
| `manager_changes` | array | Manager-level value-change components. |
| `account_changes` | array | Account-level components. |
| `theme_changes` | array | Theme/lens components. |
| `position_changes` | array | Position-level components and top movers. |
| `scenario_values` | array | Scenario valuation summaries when requested. |
| `confidence_summary` | object | Confidence and valuation-tier summary. |
| `narrative_facts` | array | Report-friendly facts with caveats. |
| `review_flags` | array | Items requiring human review. |

### Relationship To Existing Contracts

Report element templates should be able to draw facts from this package without invoking the valuation engine directly. It can become a bridge between simulation outputs and future serialized briefing set specs.

### Demo Simplifications

- Attribution is explanatory, not statement-grade.
- Residual value change may be acceptable when full attribution is out of scope.
- Scenario values are illustrative.

### Future Production Replacement Path

Production performance, accounting, risk, and reporting systems can replace this package with richer validated data while retaining report-facing field names where possible.

## SimulationRunResult

### Purpose

`SimulationRunResult` is the top-level envelope for one synthetic simulation run. It ties together the universe, market history, current market state, scenario states, daily valuations, value-change packages, validation results, and artifact references.

### Key Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start with `simulation_run_result.v1`. |
| `simulation_run_id` | string | Stable run ID. |
| `created_at` | string | ISO timestamp. |
| `run_mode` | string | Example: `demo_seeded`, `scenario_library`, `valuation_only`. |
| `source` | object | Generator versions, seeds, and synthetic-data flags. |
| `universe` | object/ref | `SyntheticPositionUniverse` or artifact reference. |
| `market_history` | object/ref | `MarketStateHistory` or artifact reference. |
| `current_market_state` | object/ref | `MarketStateSnapshot` or artifact reference. |
| `scenario_states` | array | `ScenarioMarketState` records or references. |
| `daily_valuations` | array/ref | `DailyPortfolioValuation` records or artifact reference. |
| `value_change_packages` | array | One or more report-ready value-change packages. |
| `canonical_snapshot_ref` | object | Optional emitted `CanonicalPortfolioSnapshot` reference. |
| `report_element_inputs` | object | Summary inputs intended for report element templates. |
| `validation` | object | Errors, warnings, covariance recovery status, completeness status. |
| `artifacts` | array | JSON/report artifact references if generated. |

### Relationship To Existing Contracts

This is the simulation equivalent of a run package. It should relate to existing `report_package`, `data_coverage_result`, `analytics_outputs`, and canonical snapshot contracts without requiring the browser report element composer to know how simulation internals work.

### Demo Simplifications

- Local files or in-memory objects are acceptable in v1.
- Artifact paths are local and synthetic-only.
- No database persistence is implied.
- No production audit trail is implied.

### Future Production Replacement Path

In production, this envelope may be replaced by a workflow run record backed by actual source adapters, data pipelines, valuation engines, and reporting jobs. The useful product boundary is the set of report-ready outputs and confidence metadata, not the synthetic generator itself.

## Contract Boundary With Report Element System

Report element templates should consume stable summaries:

- latest portfolio values;
- period value-change package;
- manager/account/sleeve/theme aggregates;
- scenario values;
- data-confidence and human-review summaries;
- caveats and provenance.

They should not depend on random seeds, generator internals, or unaggregated market-driver mechanics unless a future Advisor Review diagnostic element explicitly requires that detail.

## Versioning Strategy

Use explicit schema versions such as `simulation_run_result.v1`. Backward-incompatible changes should increment the major suffix. Additive optional fields may remain in v1 when downstream components tolerate missing values.
