# Demo Dataset Plan

## Recommendation

Use JSON for the first implementation batch. JSON keeps the synthetic dataset readable while allowing nested metadata, tags, scenario rules, and validation output without introducing parsing dependencies beyond the standard library.

## Proposed Files

- `data/demo/portfolio.json`: Synthetic portfolio metadata, managers, accounts, securities, holdings, cash balances, and optional transactions.
- `data/demo/market_data.json`: Static price and classification fixture.
- `data/demo/scenarios.json`: One or two deterministic scenario definitions.
- `reports/demo/northstar_demo_report_2026_06_30.md`: Generated output from the first vertical slice.

Optional generated intermediary artifacts if useful:

- `reports/demo/canonical_snapshot.json`
- `reports/demo/valuation_result.json`
- `reports/demo/exposure_overlap_result.json`
- `reports/demo/scenario_result_ai_chips_selloff.json`

## Proposed Scale

| Element | Target Count |
| --- | --- |
| Fictional household/portfolio | 1 |
| Managers | 5 |
| Accounts | 5 |
| Securities | 12 to 16 |
| Holdings | 18 to 24 |
| Cash balances | 5 |
| Scenarios | 1 required, 2 optional |

## Managers And Accounts

1. Atlas Core Growth -> Taxable Core Account.
2. Harbor Value Partners -> Trust Value Account.
3. Meridian Index Solutions -> Foundation ETF Account.
4. Signal AI Opportunities -> Growth Satellite Account.
5. Northstar Treasury Desk -> Cash Reserve Account.

## Securities And Holdings

The dataset should include enough overlap to make the report interesting:

- Microsoft and NVIDIA held by both Atlas Core Growth and Signal AI Opportunities.
- Broad ETF exposure in the foundation account.
- Energy/value names in the value account.
- Bond or defensive exposure in the foundation or cash reserve account.
- Explicit cash in every account.

## Market Data Fixture Requirements

Every non-cash security must have:

- `security_id`
- `ticker`, if applicable
- `price`
- `currency`
- `price_date`
- `asset_class`
- `sector`, where applicable
- `themes`

Prices can be realistic-looking but should be synthetic fixture values. They should not be fetched from external APIs.

## Scenario Definitions

Required scenario:

- `scenario_ai_chips_selloff`: AI/chips -18 percent, broad equity -5 percent, energy/value -3 percent, fixed income +1 percent, cash 0 percent.

Optional scenario:

- `scenario_energy_rally`: energy +12 percent, broad equity +2 percent, fixed income -1 percent, cash 0 percent.

## Expected Generated Outputs

The next implementation batch should produce:

- A canonical portfolio snapshot.
- A valuation result.
- An exposure and overlap result.
- A scenario result for the AI/chips selloff.
- A Markdown report under `reports/demo/`.

The report should show:

- Total portfolio value.
- Account totals.
- Manager totals.
- Top holdings.
- Cash amount and percent.
- Sector/theme exposures.
- Microsoft and NVIDIA direct overlap.
- AI/chips scenario impact.
- Synthetic-data caveat.

## Validation Checklist

- Dataset has `is_synthetic: true`.
- All IDs are unique within each section.
- Accounts reference valid managers.
- Holdings reference valid accounts and securities.
- Cash balances reference valid accounts.
- Every non-cash held security has one market data price.
- All v1 currencies are `USD`.
- Quantities and cash balances are non-negative.
- Scenario rules reference known sectors, themes, asset classes, or securities.
- Valuation totals reconcile from positions and cash to accounts, managers, and portfolio.
- Exposure percentages reconcile to portfolio value within tolerance.
- Scenario before/after totals reconcile to position impacts.
- Generated report visibly states that the data is synthetic and not investment advice.
