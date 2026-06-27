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
| `run_id` | Optional | string | Stable local workflow run identifier. |
| `source_name` | Optional | string | Example: `native_demo` or `plaid_mock`. |
| `source_adapter` | Optional | string | Adapter that produced the canonical snapshot. |
| `workflow_type` | Optional | string | Selected advisor workflow, such as `quarterly_review`. |
| `workflow_template` | Optional | object | Snapshot of selected workflow template fields. |
| `run_metadata` | Optional | object | Local run metadata, output links, workflow metadata, and synthetic-data flag. |
| `data_coverage_result` | Optional | object | Link and summary for the generated `DataCoverageResult`. |

## Intended Audience

The v1 report is for an advisor or internal colleague evaluating the Arangur v2 demo. It should be readable, concise, and caveated. It is not a client-ready production report and must not be presented as investment advice.

## Required Analytics Inputs

- `CanonicalPortfolioSnapshot`
- `MarketDataFixture`
- `ValuationResult`
- `ExposureOverlapResult`
- At least one `ScenarioDefinition`
- At least one `ScenarioResult`
- `DataCoverageResult` for current local demo runs

## Required Report Sections

1. Title and synthetic-data caveat.
2. Workflow focus / meeting purpose.
3. Data coverage and valuation confidence.
4. Portfolio snapshot summary.
5. Account and manager summary.
6. Top holdings.
7. Cash summary.
8. Sector and theme exposure.
9. Direct overlap observations.
10. Scenario shock result.
11. Advisor narrative.
12. Methodology and limitations.

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
  "run_id": "run_native_demo_quarterly_review_2026_06_30",
  "source_name": "native_demo",
  "source_adapter": "demo_json",
  "workflow_type": "quarterly_review",
  "workflow_template": {
    "workflow_type": "quarterly_review",
    "display_name": "Quarterly Review",
    "meeting_goal": "Summarize portfolio value, manager allocation, major exposures, direct overlap, and scenario result for a routine review."
  },
  "data_coverage_result": {
    "path": "reports/demo/data_coverage_result.json",
    "valuation_summary": {
      "valuation_date": "2026-06-30",
      "overall_confidence": "mixed"
    },
    "human_review_item_count": 1,
    "workflow_emphasis": "Concise data confidence context supports the advisor report without changing analytics outputs."
  },
  "outputs": [
    {
      "format": "markdown",
      "path": "reports/demo/northstar_demo_report_2026_06_30.md"
    }
  ]
}
```
