# Report Element Input Mapping Contract v1

Status: implemented synthetic baseline.

This contract defines the first mapping layer from the three-surface simulation
kernel outputs into structured report-element input payloads. The payloads are
inputs for future rendering only. They are not final reports, charts, browser UI
state, client briefings, database records, or generated report packages.

## Source Fixtures

The mapper reads only committed synthetic simulation fixtures under
`data/simulation/`:

- `synthetic_position_universe.json`
- `synthetic_market_state_history.json`
- `synthetic_scenario_market_states.json`
- `daily_position_valuation_history.json`
- `daily_portfolio_valuation_history.json`
- `value_change_package.json`
- `scenario_revaluation_results.json`
- `simplified_valuation_summary.json`

No live market data, Plaid data, vendor data, credentials, external APIs,
Docker, Postgres, or real client data are used.

## Output Fixtures

The default writer emits:

- `data/simulation/report_element_inputs/portfolio_status.json`
- `data/simulation/report_element_inputs/concentration_theme.json`
- `data/simulation/report_element_inputs/concentration_sector_industry.json`
- `data/simulation/report_element_inputs/scenario_impact_by_manager_ai_chip_selloff.json`
- `data/simulation/report_element_inputs/cash_generation_summary.json`
- `data/simulation/report_element_inputs/manager_comparison.json`
- `data/simulation/report_element_inputs/data_confidence_note.json`
- `data/simulation/report_element_inputs/report_element_input_summary.json`

The two concentration payloads share the `concentration` template and differ by
configured lens.

## Common Payload Fields

Each payload uses `schema_version: report_element_input_payload.v1` and includes:

- `element_id`, `element_title`, `template_category`
- optional `target_branch` and `placement`
- `parameters_used`
- `as_of_date`, `portfolio_id`, `reporting_currency`
- `source_data` references for position universe, market state, valuation
  history, and scenario results
- `headline_metrics`
- `evidence_items`
- `tables`
- `confidence_summary`
- `caveats`
- `human_review_items`
- `synthetic_data: true`
- `validation`

The payloads intentionally avoid rendering keys such as final report content,
HTML, Markdown, chart configuration, browser UI routes, report packages, or
client briefing artifacts.

## Element Mapping Rules

`portfolio_status` uses the latest daily portfolio valuation and includes total
value, cash, manager/position counts, human-review value/count, manager values,
asset-class values, theme values, liquidity values, confidence, and caveats.

`concentration` groups latest position valuations by the requested lens. The
baseline fixtures cover `Theme` and `Sector / Industry`, include top holdings,
and include inferred overlap exposure where the same synthetic display name
appears across multiple managers.

`scenario_impact_by_manager` defaults to `ai_chip_selloff` and includes scenario
metadata, base value, scenario value, total impact, impact percent, manager
impacts, top position impacts, theme impacts, asset-class impacts, scenario
completeness, confidence, and human-review items. If the scenario id is missing,
the builder returns a validation payload with `SCENARIO_NOT_FOUND`.

`cash_generation_summary` combines the value-change package, transactions, and
latest cash-like positions. It includes period metadata, current cash, period
income/distributions, transaction flows, fees, cash-like positions, and
cash-generation rows by manager. It is simplified synthetic cash accounting.

`manager_comparison` combines latest manager aggregates, period value-change
aggregates, manager metadata, primary themes, liquidity profile, confidence,
position counts, and human-review counts/value.

`data_confidence_note` uses the simplified valuation summary and latest
confidence summary. It includes confidence label, confidence rows, valuation
treatment rows, data issue rows, market-state treatment rows, human-review
items, and stale/private/proxy/human-review caveats.

## Public Functions

The mapper is implemented in `src/arangur/report_elements/input_mapping.py`:

- `load_simulation_outputs(...)`
- `build_report_element_input(element_id, parameters, simulation_outputs)`
- `build_all_demo_report_element_inputs(...)`
- `validate_report_element_input(payload)`
- `write_demo_report_element_inputs(...)`

It can also be run from the repo root:

```powershell
python src\arangur\report_elements\input_mapping.py
```

## Validation Invariants

Validation requires the common fields, synthetic-data flag, source references,
headline metrics, confidence summary, caveats, and each element's required
structured tables. It also rejects prohibited real-data markers and
report-generation keys.

The summary payload reports payload count, element ids, output files, source
files used, `as_of_date`, current portfolio value, and validation status.
