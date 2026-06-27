# Current Architecture

The current intended architecture is a thin end-to-end demo pipeline with stable replaceable boundaries:

1. Simple local demo data.
2. Canonical portfolio snapshot.
3. Market data fixture.
4. Simple valuation.
5. Exposure and overlap analytics.
6. Scenario shock service.
7. Report or view generation.

## First Demo Flow

Demo data should be synthetic and local. It should include enough accounts, positions, instruments, prices, and advisor-facing names to demonstrate the product without touching real client data.

The demo data loader should normalize synthetic input into a canonical portfolio snapshot. Downstream components should depend on the canonical snapshot rather than on the original source shape.

The market data fixture should provide deterministic prices and simple classification fields. Initial valuation can be straightforward market value math. Exposure, overlap, and scenario outputs should be simple enough to explain in a first advisor report.

The report/view generation layer should consume the outputs and produce something advisor-readable, even if the first version is a static file.

## Future Adapters And Upgrades

- Plaid adapter: produce canonical portfolio snapshots from Plaid-shaped holdings and account data.
- Custodian, manager, and CSV ingestion: add source adapters that conform to the same snapshot boundary.
- Market data vendor pipeline: replace fixtures with richer prices, classifications, factors, and metadata.
- Corporate actions and data cleansing: add normalization, exception handling, and reconciliation.
- MATLAB-informed valuation and accounting upgrades: audit legacy ideas only after an authorized batch.
- Advisor report assistant: help explain results, draft commentary, and surface follow-up questions.
- UI/dashboard: support interactive review once the data and analytics contracts stabilize.
