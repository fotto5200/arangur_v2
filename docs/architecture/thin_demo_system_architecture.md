# Thin Demo System Architecture

## Purpose

The thin demo system proves the first Arangur v2 product loop with synthetic local data and stable replaceable component boundaries. It should show how a family-office or advisor portfolio can be loaded, normalized, valued, analyzed for exposure and overlap, shocked under a simple scenario, and turned into an advisor-readable report.

This is not the production system. It is the smallest coherent vertical slice that demonstrates the product shape and gives future Plaid, market data, MATLAB-informed analytics, and UI work a stable contract to plug into.

## End-To-End Flow

```text
data/demo/*.json
  -> DemoDataLoader
  -> CanonicalPortfolioSnapshot
  -> MarketDataFixture
  -> ValuationService
  -> ExposureOverlapService
  -> ScenarioService
  -> ReportGenerator
  -> reports/demo/*.md
```

## Component Diagram

```text
+-------------------+      +----------------------------+
| Local Demo Data   | ---> | DemoDataLoader             |
| portfolio + md    |      | validates and normalizes   |
+-------------------+      +-------------+--------------+
                                          |
                                          v
                            +-------------+--------------+
                            | CanonicalPortfolioSnapshot |
                            | source-neutral portfolio   |
                            +------+------+--------------+
                                   |      |
                  +----------------+      +----------------+
                  v                                      v
       +----------+----------+              +------------+----------+
       | MarketDataFixture   |              | ScenarioDefinition    |
       | prices + tags       |              | deterministic shocks  |
       +----------+----------+              +------------+----------+
                  |                                      |
                  v                                      |
       +----------+----------+                           |
       | ValuationService    |                           |
       | market values       |                           |
       +----------+----------+                           |
                  |                                      |
                  v                                      v
       +----------+----------+              +------------+----------+
       | ExposureOverlap     |              | ScenarioService       |
       | exposures + overlap |              | shocked impact        |
       +----------+----------+              +------------+----------+
                  |                                      |
                  +----------------+      +--------------+
                                   v      v
                            +------+------+--------------+
                            | ReportGenerator            |
                            | advisor-readable package   |
                            +-------------+--------------+
                                          |
                                          v
                                  reports/demo/*.md
```

## Component Responsibilities

### DemoDataLoader

- Read hand-authored synthetic demo data from `data/demo/`.
- Validate required identifiers, account records, securities, holdings, cash balances, and scenario metadata.
- Normalize the source shape into a `CanonicalPortfolioSnapshot`.
- Emit clear validation errors without touching external services.

### CanonicalPortfolioSnapshot

- Represent source-neutral portfolio state for one valuation date.
- Preserve source provenance so downstream reports can explain where demo records came from.
- Give downstream components stable account, manager, security, holding, and cash identifiers.
- Remain independent of Plaid, CSV, manual-entry, and future custodian-specific shapes.

### MarketDataFixture

- Provide deterministic local prices, currency, sectors, themes, and optional shock sensitivity values.
- Fail clearly or mark exceptions when a priced security is missing from the fixture.
- Stay simple enough for local JSON or CSV.

### ValuationService

- Calculate simple market value for long-only positions: `quantity * price`.
- Include cash at face value in the relevant currency.
- Aggregate market value by account, manager, security, asset class, and total portfolio.
- Keep currency conversion out of v1 unless all records use one reporting currency.

### ExposureOverlapService

- Calculate direct exposure from supplied security classifications and market values.
- Summarize account, manager, sector, theme, asset class, and cash exposure.
- Identify direct security overlap across accounts or managers.
- Avoid look-through, derivatives, attribution, and advanced risk modeling in v1.

### ScenarioService

- Apply deterministic shocks from local scenario definitions.
- Support simple shocks by security, sector, asset class, theme, or cash bucket.
- Produce before/after values and dollar/percent impact.
- Label outputs as illustrative demo scenarios.

### ReportGenerator

- Generate an advisor-readable Markdown report under `reports/demo/`.
- Present portfolio summary, valuation, exposures, overlap, scenario impact, caveats, and synthetic-data labeling.
- Avoid investment advice, suitability claims, or production-grade data quality claims.

## Data Flow

1. Local demo portfolio and market data are read from static files.
2. The loader validates and normalizes demo source records.
3. The canonical snapshot becomes the only portfolio input consumed downstream.
4. Market data fixture records are joined by canonical security identifier, ticker, or fixture identifier.
5. Valuation produces position, account, manager, and total market values.
6. Exposure and overlap analytics consume valuation outputs and supplied classifications.
7. Scenario analytics apply one or more deterministic shock definitions.
8. The report package combines all outputs into Markdown for an advisor-style walkthrough.

## File And Folder Expectations

- `docs/architecture/`: Architecture notes for implementation batches.
- `docs/contracts/`: Detailed data and output contracts.
- `docs/demo/`: Demo storyline, dataset plan, and expected report narrative.
- `data/demo/`: Future synthetic JSON or CSV fixtures only.
- `reports/demo/`: Generated synthetic demo reports and any viewer-ready output packages.
- `src/`: Future implementation code, not used in this design batch.
- `tests/`: Future focused tests for loaders, validation, valuation, analytics, scenarios, and report generation.

## Deliberately Simple In V1

- Synthetic data only.
- Long-only positions.
- Cash at face value.
- Single reporting currency, recommended `USD`.
- Static local market prices.
- Direct holdings only, no fund look-through.
- Simple account and manager aggregation.
- Direct security overlap only.
- Sector/theme exposure from supplied tags.
- Deterministic scenario shocks.
- Static Markdown report output.

## Must Remain Replaceable

- Demo data file format.
- Source adapters and normalization logic.
- Canonical snapshot schema implementation details.
- Market data source.
- Pricing and valuation method.
- Exposure taxonomy.
- Scenario shock model.
- Report renderer and output format.
- Future UI or dashboard layer.

The stable boundary is the canonical snapshot plus documented analytics/report package contracts, not the first loader or fixture implementation.

## Later Plaid Integration

Plaid should plug in as an ingestion adapter after the canonical snapshot boundary exists. A future Plaid adapter should:

- Read Plaid account, holding, security, and balance payloads from Sandbox or live sources.
- Map Plaid-specific identifiers and fields into canonical accounts, securities, holdings, and cash balances.
- Preserve Plaid provenance fields without forcing downstream analytics to understand Plaid payloads.
- Emit the same `CanonicalPortfolioSnapshot` shape as the local demo loader.

The first Plaid-related implementation should be a Plaid-shaped mock fixture, not live Plaid.

## Later MATLAB-Informed Upgrades

Legacy MATLAB may inform future valuation, accounting, attribution, and portfolio-structure upgrades only after a specific audit batch is authorized. The v1 architecture should leave room for richer valuation/accounting modules without copying or organizing around MATLAB internals now.

## Acceptance Criteria For First Working Vertical Slice

- A synthetic local dataset can be loaded from `data/demo/`.
- The loader emits a valid canonical portfolio snapshot with accounts, managers, securities, holdings, cash, valuation date, and provenance.
- A local market data fixture provides prices and classifications for every non-cash demo holding.
- Valuation output reconciles position values to account, manager, and portfolio totals.
- Exposure output summarizes at least asset class, sector, theme, account, manager, and cash exposure.
- Overlap output identifies at least one duplicated security across managers or accounts.
- Scenario output applies at least one deterministic shock and reports portfolio impact.
- A Markdown report is generated under `reports/demo/` with synthetic-data caveats.
- Focused tests or deterministic checks verify the main calculations.

## Non-Goals For First Working Vertical Slice

- Live Plaid or Plaid Sandbox integration.
- External market data APIs.
- Real client data.
- Credentials, secrets, or `.env` handling.
- Legacy MATLAB inspection or porting.
- Full accounting, tax-lot, corporate-action, or performance attribution logic.
- Multi-currency conversion.
- Derivatives, short positions, leverage, or private asset valuation.
- Production UI/dashboard.
- Investment advice or suitability recommendations.
