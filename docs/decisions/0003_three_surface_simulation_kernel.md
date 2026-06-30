# Decision 0003: Three-Surface Simulation Kernel

## Status

Accepted for near-term full-system demo development.

## Date

2026-06-30

## Decision

Arangur v2 will use a three-surface simulation kernel for the next fuller working demo:

1. Synthetic Position Universe.
2. Synthetic Market / State-of-World Generator.
3. Simplified Daily Valuation Engine.

The kernel will remain synthetic, local, and replaceable. It will provide realistic enough outputs for report elements, scenario reports, Client Briefing Sets, Advisor Review Sets, and confidence workflows without requiring production ingestion, live market data, or production accounting.

## Reason

The current product loop has the app shell, synthetic pipeline, report element catalog, and local briefing-set composer, but the downstream reporting experience needs richer portfolio and valuation state to feel coherent.

Production ingestion, vendor market data, and production accounting are each large surfaces. Building all three first would delay the product demo and force decisions that are not yet needed. Simulating them behind explicit contracts gives Arangur a path to test the full advisor/client workflow while keeping the hard surfaces replaceable.

## Consequences

Positive consequences:

- A fuller demo can operate on plausible public, private, cash, manager-level, and opaque holdings.
- Scenario and confidence reports can use coherent synthetic market state.
- Daily valuation can separate flows, income/distributions, market/value change, and closing value.
- Report element templates can consume realistic synthetic outputs before production data exists.
- Future production systems have clearer replacement boundaries.

Tradeoffs:

- The simulation kernel must be clearly labeled synthetic.
- Outputs are demo-quality and should not imply production accounting, market truth, or investment advice.
- Implementation batches need to preserve explicit confidence, caveat, and human-review metadata.
- Some current thin-demo contracts may need additive expansion for private assets, stale marks, and value-change packages.

## What This Enables

- Synthetic position universe generation with 50-100 positions.
- Coherent market/state history and scenario states.
- Covariance recovery checks for synthetic driver generation.
- Daily economic valuation by position, account, manager, sleeve, theme, and portfolio.
- Value-change packages for briefing and report elements.
- Data confidence and human-review summaries that can be surfaced in Advisor Review and client-facing caveats.

## What It Does Not Claim

- No real client ingestion.
- No live Plaid or external API usage.
- No vendor market-data integration.
- No production valuation or accounting policy.
- No tax-lot, settlement, carry/accrual, or institutional reconciliation accuracy.
- No production private-equity, private-credit, or real-estate accounting.
- No market forecasts or investment recommendations.
- No legacy MATLAB inspection or porting.

## Open Questions

- Which synthetic family-office storyline should anchor the first 50-100 position universe?
- How many managers, accounts, and sleeves are needed for the first convincing demo?
- Which core market drivers should be in the first covariance matrix?
- What tolerance is appropriate for the first covariance recovery check?
- How should generated simulation artifacts relate to existing `reports/demo/` output packages?
- Which report element templates should be connected to simulation outputs first?
- Should briefing set serialization/export resume before or after the first valuation-backed report elements?
