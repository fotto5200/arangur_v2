# Report Package Contract

## Purpose

`ReportPackage` defines the first advisor-readable output for the thin demo. It should package synthetic portfolio analytics into a clear Markdown report that a colleague can read without needing to inspect raw data.

## Report Metadata

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `schema_version` | Yes | string | Start with `report_package.v1`. |
| `report_id` | Yes | string | Stable generated report identifier. |
| `report_title` | Yes | string | Human-readable title. |
| `generated_at` | Optional | string | ISO timestamp. |
| `valuation_date` | Yes | string | ISO date. |
| `portfolio_id` | Yes | string | Links to canonical snapshot. |
| `snapshot_id` | Yes | string | Links to canonical snapshot. |
| `is_synthetic` | Yes | boolean | Must be `true` for demo reports. |
| `audience` | Yes | string | Example: `advisor_colleague_demo`. |

## Intended Audience

The v1 report is for an advisor or internal colleague evaluating the Arangur v2 demo. It should be readable, concise, and caveated. It is not a client-ready production report and must not be presented as investment advice.

## Required Analytics Inputs

- `CanonicalPortfolioSnapshot`
- `MarketDataFixture`
- `ValuationResult`
- `ExposureOverlapResult`
- At least one `ScenarioDefinition`
- At least one `ScenarioResult`

## Required Report Sections

1. Title and synthetic-data caveat.
2. Portfolio snapshot summary.
3. Account and manager summary.
4. Top holdings.
5. Cash summary.
6. Sector and theme exposure.
7. Direct overlap observations.
8. Scenario shock result.
9. Advisor narrative.
10. Methodology and limitations.

Optional sections:

- Data validation warnings.
- Appendix tables.
- Suggested advisor follow-up questions.

## Generated Outputs

V1 required output:

- `reports/demo/<report_id>.md`

Optional later outputs:

- `reports/demo/<report_id>.html`
- `reports/demo/<report_id>.json`
- chart images or viewer-ready assets

Markdown should be the first output format because it is easy to diff, test, and review.

## Markdown Output Expectations

The Markdown report should include:

- Clear title.
- Synthetic-data warning near the top.
- Tables for account totals, manager totals, top holdings, exposures, overlaps, and scenario impact.
- Short narrative paragraphs that explain why the results matter.
- Values formatted consistently in the reporting currency.
- Percentages formatted consistently.

## Caveat Language Requirements

Every demo report must state:

- The data is synthetic.
- The report is generated for product demonstration.
- The output is not investment advice.
- Values and classifications come from local fixtures.
- Scenario shocks are illustrative and deterministic.

Suggested caveat:

```text
Demo only: this report uses synthetic data and local fixture prices. It is intended to demonstrate Arangur v2 product behavior and is not investment advice, a client statement, or a production valuation.
```

## What The Report Must Not Claim

The report must not claim:

- Data is complete, reconciled, audited, or production-grade.
- The portfolio belongs to a real person or entity.
- Results are suitable for investment decisions.
- Scenario results are forecasts.
- Plaid, custodian, or live market data was used unless a future authorized batch actually implements that path.
- MATLAB-derived valuation or accounting logic was used unless a future authorized batch adds it.

## Synthetic Vs Real Data Distinction

The report should include `is_synthetic: true` in metadata and visible caveat text in the report body. Synthetic portfolio names should be fictional and should avoid names that could be confused with real clients.

## Example Package Metadata

```json
{
  "schema_version": "report_package.v1",
  "report_id": "northstar_demo_report_2026_06_30",
  "report_title": "Northstar Family Office Demo Portfolio Review",
  "valuation_date": "2026-06-30",
  "portfolio_id": "portfolio_northstar_demo",
  "snapshot_id": "snap_demo_family_office_2026_06_30",
  "is_synthetic": true,
  "audience": "advisor_colleague_demo",
  "outputs": [
    {
      "format": "markdown",
      "path": "reports/demo/northstar_demo_report_2026_06_30.md"
    }
  ]
}
```
