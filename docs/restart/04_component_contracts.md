# Component Contracts

These are first-pass high-level contracts. Detailed schemas may later live under `docs/contracts/` or `src/arangur/schemas/`.

## DemoDataLoader

- Purpose: Load local synthetic demo data and convert it into the canonical portfolio shape.
- Likely inputs: Demo account, position, instrument, price, and classification fixtures from `data/demo/`.
- Likely outputs: A `CanonicalPortfolioSnapshot`.
- Downstream assumptions: Output is deterministic, synthetic, and free of real client data.
- Replaceable parts: File format, fixture structure, and source-specific normalization logic.

## CanonicalPortfolioSnapshot

- Purpose: Represent portfolio state at a point in time, independent of ingestion source.
- Likely inputs: Normalized accounts, holdings, instruments, quantities, cost basis fields, and snapshot date.
- Likely outputs: The shared input for valuation, exposure, overlap, scenarios, and reporting.
- Downstream assumptions: Stable identifiers exist for accounts, positions, and instruments; quantities and units are explicit.
- Replaceable parts: Source adapters and schema details, as long as the canonical contract remains stable.

## MarketDataFixture

- Purpose: Provide deterministic demo market data for valuation and analytics.
- Likely inputs: Local price, asset class, sector, geography, currency, and factor classification fixtures.
- Likely outputs: Price and classification lookups keyed by canonical instrument identifiers.
- Downstream assumptions: Prices and classifications are available for every demo instrument.
- Replaceable parts: Fixture source, vendor pipeline, classification depth, and freshness model.

## ValuationResult

- Purpose: Capture simple valuation outputs for accounts, positions, and the total portfolio.
- Likely inputs: `CanonicalPortfolioSnapshot` and `MarketDataFixture`.
- Likely outputs: Position market values, account totals, portfolio total value, and valuation date.
- Downstream assumptions: Values are deterministic and traceable to quantities and fixture prices.
- Replaceable parts: Pricing method, currency handling, accrued income, accounting treatment, and valuation model.

## ExposureOverlapResult

- Purpose: Summarize exposures, concentrations, and overlapping holdings.
- Likely inputs: `CanonicalPortfolioSnapshot`, `MarketDataFixture`, and `ValuationResult`.
- Likely outputs: Asset class, sector, geography, currency, account, manager, and holding-level exposure summaries.
- Downstream assumptions: Exposure percentages reconcile to the valuation result within stated tolerances.
- Replaceable parts: Exposure dimensions, look-through methods, overlap rules, and concentration thresholds.

## ScenarioDefinition

- Purpose: Define a deterministic market or factor shock to apply to the portfolio.
- Likely inputs: Scenario name, shock date or assumption date, affected dimensions, shock magnitudes, and explanatory text.
- Likely outputs: A reusable scenario specification for scenario services.
- Downstream assumptions: The definition is explicit enough to reproduce scenario results.
- Replaceable parts: Shock model, factor taxonomy, calibration source, and scenario library structure.

## ScenarioResult

- Purpose: Show estimated portfolio impact under a scenario definition.
- Likely inputs: `CanonicalPortfolioSnapshot`, `MarketDataFixture`, `ValuationResult`, and `ScenarioDefinition`.
- Likely outputs: Position, account, exposure bucket, and total portfolio impact summaries.
- Downstream assumptions: Scenario math is simple, deterministic, and labeled as illustrative in early demos.
- Replaceable parts: Risk model, factor mapping, stress methodology, and aggregation logic.

## ReportPackage

- Purpose: Package advisor-readable outputs from the demo pipeline.
- Likely inputs: Portfolio snapshot, valuation, exposure/overlap, scenario results, narrative metadata, and generated assets.
- Likely outputs: Static report files, viewer data, charts, tables, and summary text under `reports/demo/`.
- Downstream assumptions: Report data is synthetic unless explicitly labeled otherwise.
- Replaceable parts: Report format, rendering engine, charting layer, assistant-generated commentary, and UI destination.
