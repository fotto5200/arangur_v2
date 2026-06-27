# Data Coverage Result Contract

## Purpose

`DataCoverageResult` explains what the local demo knows about source coverage, valuation confidence, and human-review needs. It is a transparent prototype over synthetic fixtures, not a production data-quality system.

## Required Output

Generated path for each report run:

- `data_coverage_result.json`

For the default native run this is `reports/demo/data_coverage_result.json`. Source-specific and workflow-specific runs write the same filename in their own output folders.

## Required Fields

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | `data_coverage_result.v1`. |
| `run_id` | string | Matches the local report-package run ID. |
| `source_name` | string | Example: `native_demo` or `plaid_mock`. |
| `source_adapter` | string | Adapter that produced the canonical snapshot. |
| `workflow_type` | string | Selected report workflow. |
| `valuation_date` | string | ISO date from the snapshot. |
| `synthetic_data` | boolean | Must be `true` for current demo outputs. |
| `portfolio_coverage_summary` | object | Overall label, counts, summary text, and human-review count. |
| `account_coverage` | array | Per-account confidence summary. |
| `holding_coverage` | array | Per-held-position confidence summary. |
| `security_coverage` | array | Per-security confidence summary, including unheld placeholders. |
| `valuation_confidence_summary` | object | Overall confidence, counts, dimension labels, and notes. |
| `data_quality_flags` | array | Deterministic flags produced by local rules. |
| `human_review_items` | array | Items that should be reviewed before production-style reporting. |
| `caveats` | array | Visible limitations and non-claims. |
| `next_data_work_items` | array | Follow-up work implied by the prototype. |

## Confidence Dimensions

Each record and summary should use these dimensions:

- `identifier_coverage`
- `price_coverage`
- `classification_coverage`
- `source_transparency`
- `valuation_method_confidence`
- `scenario_mapping_confidence`

Dimension values are limited to:

- `high`
- `medium`
- `low`
- `unknown`

Overall portfolio confidence may use `mixed` when multiple confidence levels are present.

## Local Prototype Rules

- Public equities and ETFs with ticker, price, sector, and theme metadata receive high or medium confidence depending on the dimension.
- Cash balances are high confidence at face value.
- Missing held-security prices create low price and valuation confidence plus a human-review item.
- Missing sector/theme classifications reduce classification confidence and may create a review item.
- Opaque, private, or placeholder securities are low confidence until a human valuation policy exists.
- Plaid-shaped mock data gets source-transparency caveats because the fixture proves intake shape, not production valuation proof.
- Scenario mapping is high only when a ticker, sector, or theme mapping is available.

## Current Demo Behavior

The native fixture includes one unheld `Synthetic Private Fund Placeholder` security so the report can show a low-confidence/private-asset review path without changing valuation totals. The Plaid-shaped mock path adds a source-transparency review item.

## Report-Package Linkage

`report_package.json` includes a `data_coverage_result` object with:

- `path`
- `valuation_summary`
- `summary`
- `key_flags`
- `human_review_item_count`
- `workflow_emphasis`

This is a convenience summary. The full contract artifact remains `data_coverage_result.json`.

## Non-Claims

The result must not claim:

- Production reconciliation.
- Vendor market-data proof.
- Live Plaid ingestion.
- Private asset valuation.
- Investment advice or forecasting.
- Completeness for real client portfolios.
