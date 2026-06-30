# Synthetic Market State Contract v1

## Purpose

`SyntheticMarketStateHistory` is the Surface 2 fixture for the Arangur simulation kernel. It consumes the Surface 1 synthetic position universe and creates a deterministic, serializable, fully synthetic market/state-of-world environment for every market-state variable required by the positions.

This contract intentionally stops before valuation. It generates prices, proxies, model inputs, private/stale mark treatments, scenario states, confidence metadata, and completeness checks, but it does not calculate position values, portfolio values, value-change packages, reports, or charts.

## Output Files

Current generated files:

- `data/simulation/synthetic_market_state_history.json`
- `data/simulation/synthetic_market_state_summary.json`
- `data/simulation/synthetic_scenario_market_states.json`

The current generator is:

- `src/arangur/simulation/market_state.py`
- `src/arangur/simulation/synthetic_market_state_generator.py`

Regenerate from the repo root:

```powershell
python src\arangur\simulation\synthetic_market_state_generator.py
```

The generator reads:

- `data/simulation/synthetic_position_universe.json`

## Determinism And Provenance

The default seed is `20260701`. The default generated history ID is:

```text
northstar_synthetic_market_state_history_seed_20260701
```

The fixture is deterministic for the same Surface 1 universe and seed. All output files include synthetic provenance and caveats. No live market data, vendor feed, external API, credential, or real client data is used.

## Current Fixture Summary

Current default summary:

| Field | Value |
| --- | --- |
| Schema | `simulation_market_state_history.v1` |
| Date range | `2026-04-01` through `2026-06-30` |
| Date count | 91 calendar dates |
| Core driver count | 12 |
| Expanded state variable count | 23 |
| Scenario count | 5 |
| Covariance recovery status | `pass` |
| Validation status | `valid` |

## Top-Level History Fields

`synthetic_market_state_history.json` includes:

| Field | Required | Notes |
| --- | --- | --- |
| `schema_version` | Yes | `simulation_market_state_history.v1`. |
| `history_id` | Yes | Stable deterministic history ID including the seed. |
| `generated_at` | Yes | Fixed timestamp for deterministic fixture output. |
| `generator_version` | Yes | Generator version string. |
| `synthetic_data` | Yes | Must be `true`. |
| `start_date` | Yes | First generated market-state date. |
| `end_date` | Yes | Last generated market-state date. |
| `frequency` | Yes | `daily_calendar` in v1. |
| `reporting_currency` | Yes | `USD` in v1. |
| `source` | Yes | Generator, seed, Surface 1 universe ID, and synthetic flag. |
| `caveats` | Yes | Synthetic-data and non-valuation caveats. |
| `core_drivers` | Yes | Core driver definitions used by the factor model. |
| `factor_model` | Yes | Synthetic factor loading assumptions. |
| `intended_relationships` | Yes | Expected sign and target relationship checks. |
| `required_state_variables` | Yes | State variables required by the Surface 1 positions. |
| `expanded_state_variable_definitions` | Yes | Definitions for each generated expanded state variable. |
| `proxy_mappings` | Yes | Instrument-to-state mapping metadata. |
| `missing_or_human_review_state_items` | Yes | Low-confidence or human-review state queue. |
| `history` | Yes | Date-by-date core driver and expanded state values. |
| `current_market_state` | Yes | Latest-date snapshot derived from `history`. |
| `scenario_market_states` | Yes | Deterministic scenario state records. |
| `covariance_recovery_check` | Yes | Coherence check over generated driver returns. |
| `validation` | Yes | Structured validation status, counts, errors, and warnings. |

## Core Drivers

Surface 2 uses 12 synthetic core drivers:

- `us_large_cap_equity`
- `us_growth_tech_equity`
- `ai_infrastructure_semiconductor`
- `energy_oil`
- `bitcoin_crypto`
- `usd_fx_broad`
- `short_duration_bond_price`
- `long_duration_bond_price`
- `credit_spread_proxy`
- `volatility_proxy`
- `private_market_liquidity`
- `real_assets_infrastructure`

Core driver returns are generated from standard-library random factor shocks plus driver-specific idiosyncratic noise. This is a deterministic demo coherence model, not a production risk model.

## Factor And Covariance Recovery

The v1 factor model defines named synthetic factors such as risk-on, AI/tech, rates-down, energy supply, USD strength, volatility stress, private liquidity, and crypto beta. Core drivers carry factor loadings and idiosyncratic volatility assumptions.

`covariance_recovery_check` estimates sample Pearson correlations from generated core-driver daily returns and compares them to intended relationships. Current relationships include examples such as:

- growth tech and AI infrastructure should be positively related;
- volatility should be negatively related to broad equity and AI infrastructure;
- private-market liquidity should be negatively related to credit spreads;
- USD strength should be negatively related to energy;
- energy and AI infrastructure should remain weakly related.

The check is a deterministic fixture-quality guard. It is not production risk-model validation.

## Expanded State Variables

The current fixture covers all 23 market-state variables declared by the Surface 1 position universe:

- `ai_infrastructure_proxy`
- `bond_price_proxy`
- `cash_treatment`
- `commodity_price`
- `credit_spread_proxy`
- `crypto_price`
- `duration_bucket_price`
- `energy_price_proxy`
- `etf_price`
- `fx_rate`
- `human_review_flag`
- `liquidity_discount_proxy`
- `manager_composite_proxy`
- `manager_mark`
- `money_market_nav`
- `optional_lookthrough_proxy`
- `private_equity_proxy`
- `private_mark`
- `rate_proxy`
- `real_asset_proxy`
- `time_to_maturity`
- `underlying_price`
- `volatility_proxy`

Each expanded state value includes:

- `state_variable_id`
- `value`
- `unit`
- `value_type`
- `source_driver_ids`
- `proxy_rule`
- `confidence`
- `treatment_type`
- `description`
- `scenario_shock_percent`

Supported treatment types:

- `direct`
- `proxy`
- `model_input`
- `stale_mark`
- `cash_treatment`
- `human_review`

Supported confidence tiers:

- `high`
- `medium`
- `low`

## Proxy Mappings

`proxy_mappings` are built per instrument from Surface 1 `required_market_state_variables`. A mapping records:

- instrument identity and type;
- linked position IDs;
- required state variables;
- instrument proxy hint;
- look-through status;
- one state-variable mapping per required variable;
- treatment type, driver sources, proxy rule, and confidence;
- `synthetic_data: true`.

The mapping layer is the handoff between the broad position universe and the compact core-driver model. It also makes low-confidence and human-review cases explicit instead of silently omitting state.

## History Records

Each record in `history` represents one calendar date and includes:

- `date`
- `core_driver_values`
- `expanded_state_values`
- `data_quality_flags`
- `generation_metadata`

Every date must contain all 12 core drivers and all required expanded state variables. This keeps later daily valuation from needing to guess whether a missing input is an error or a deliberate low-confidence treatment.

## Current Market State

`current_market_state` is the latest-date snapshot, currently `2026-06-30`. It includes:

- `schema_version: simulation_market_state_snapshot.v1`
- `market_state_id`
- `state_date`
- `reporting_currency`
- source metadata linked to the position universe;
- latest core driver values;
- latest expanded state values;
- completeness summary;
- human-review items;
- `synthetic_data: true`.

## Scenario Market States

The current scenario set includes five deterministic scenario states:

- `ai_chip_selloff`
- `rate_shock`
- `energy_shock`
- `private_market_liquidity_freeze`
- `taiwan_disruption`

Scenario states reuse the same core-driver and expanded-state vocabulary as the current market state. Each scenario includes:

- scenario ID, display name, description, and horizon;
- base market state reference;
- shocked core driver values;
- scenario-expanded state values;
- completeness summary;
- direct/proxy/human-review treatment counts;
- scenario caveats;
- `synthetic_data: true`.

Scenario states are assumption inputs for future valuation. They are not forecasts and do not contain position or portfolio values.

## Separate Scenario Output

`synthetic_scenario_market_states.json` is a compact scenario-set file with:

- `schema_version: simulation_scenario_market_states.v1`
- `scenario_set_id`
- generation metadata;
- base market state reference;
- required state variables;
- all scenario records;
- synthetic scenario caveats.

## Summary Output

`synthetic_market_state_summary.json` is a compact status file with counts, date range, covered variables, scenario IDs, covariance recovery status, validation status, and a non-valuation caveat. It is intended for restart/audit checks and quick downstream sanity tests.

## Validation Expectations

`validate_synthetic_market_state_history` returns:

- `status`
- `errors`
- `warnings`
- `counts`

Validation checks include:

- required metadata and sections exist;
- schema version and synthetic flags are correct;
- dates match the Surface 1 position-universe history window;
- core driver IDs are unique;
- every date contains every core driver;
- every date covers every required state variable;
- expanded values carry value, value type, treatment type, and confidence;
- proxy mappings include required synthetic metadata;
- all five scenario states exist;
- every scenario covers every required state variable;
- scenario completeness summaries are consistent;
- covariance recovery check exists;
- prohibited real-source markers are absent;
- valuation outputs are absent.

## Future Connection

Surface 3 should consume:

```text
SyntheticPositionUniverse + SyntheticMarketStateHistory + transactions
```

and emit daily position/account/manager/portfolio values plus value-change packages. Surface 3 should treat the Surface 2 output as input state only. It should not mutate the market-state fixture or hide confidence and human-review treatments.

## Demo Limitations

- Fully synthetic data only.
- No real client data.
- No live Plaid.
- No external APIs.
- No vendor market data.
- No production risk model.
- No market forecasts.
- No position values in this batch.
- No portfolio values in this batch.
- No daily valuation engine in this batch.
- No report generation connection yet.
