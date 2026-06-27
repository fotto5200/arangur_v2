# Scenario Engine Roadmap

## Purpose

The scenario engine roadmap defines how Arangur can grow from the current deterministic demo shocks into richer scenario analysis while preserving clear caveats and reportable outputs.

The product goal is portfolio-impact analysis under stated assumptions. Arangur should not claim to forecast markets, predict security returns, or produce investment advice.

## Current Level 1: Deterministic Scenario Shocks

Level 1 is the current implemented demo level.

- Inputs: `CanonicalPortfolioSnapshot`, `MarketDataFixture`, `ValuationResult`, and local `ScenarioDefinition` records.
- Method: apply deterministic shock rules by security, ticker, theme, sector, asset class, cash, or default fallback.
- Output: before value, after value, dollar impact, percent impact, and position/account/manager impact rows.
- Report stance: illustrative impact under assumptions, not a forecast.
- Status: valid for the local synthetic demo and colleague walkthroughs.

Level 1 is useful because it is simple, explainable, deterministic, testable, and compatible with the current advisor-readable report.

## Future Level 2: Scenario Library And Source Layer

Level 2 should separate scenario authoring and scenario sources from the execution engine.

Possible source types:

- Hand-authored local scenario fixtures.
- Internal advisor scenario templates.
- Firm-approved capital markets assumptions.
- Conference Board-style base scenarios or similar external macro scenario sources, if later authorized and properly licensed.
- Imported scenario assumption tables from files, not live APIs in the first version.

The source layer should normalize external or internal scenario records into Arangur scenario assumptions without forcing downstream reports to understand source-specific shapes.

Needed concepts:

- Scenario ID and version.
- Source name and source date.
- Narrative title and plain-language description.
- Assumption horizon.
- Driver assumptions, if present.
- Asset class, sector, theme, manager, or security mapping rules.
- Caveats and licensing/provenance metadata.

## Future Level 3: Key-Driver Scenario Model

Level 3 should introduce explicit market drivers that can connect narrative scenarios to portfolio impacts.

Example drivers:

- Equity market return.
- Growth factor return.
- Value factor return.
- Interest-rate shift.
- Credit-spread shift.
- Inflation assumption.
- Energy price shock.
- USD currency shock, if multi-currency enters scope.
- Private-market markdown assumption.

Narrative scenarios should remain human-readable, but their assumptions should be represented as driver values. For example, an "AI leadership reversal" narrative might set a broad equity shock, growth factor shock, semiconductor theme shock, and cash shock.

The key design point is traceability:

```text
narrative scenario
  -> driver assumptions
  -> exposure mapping
  -> portfolio impacts
  -> reportable caveats
```

This lets reports explain both the story and the assumptions used to calculate the impact.

## Future Level 4: Covariance And Random-Number-Driven Simulation

Level 4 is future work, not current implementation.

At this level, Arangur may use covariance matrices and random-number generation to produce a distribution of impacts rather than a single deterministic point estimate.

Possible approach:

- Define a vector of key market drivers.
- Attach expected driver shocks or scenario means.
- Attach covariance or correlation assumptions among drivers.
- Use a seed value to make random-number-driven simulations reproducible.
- Generate simulated driver paths or one-period driver draws.
- Map driver outcomes to position, account, manager, and portfolio impacts.
- Summarize impact ranges, percentiles, and error bars.

Seed values matter because report outputs must be reproducible. A report package should be able to say which simulation seed, scenario version, driver set, and covariance version produced the displayed result.

## Impact Ranges And Error Bars

Covariance-based simulation could support reportable ranges such as:

- Median portfolio impact.
- 5th and 95th percentile impact.
- Interquartile range.
- Account-level and manager-level impact ranges.
- Error bars around deterministic scenario estimates.

These ranges must be caveated. They would reflect model assumptions, covariance estimates, and supplied mappings, not known probabilities of future events.

## External Scenario Sources

Conference Board-style base scenarios or other external scenario sources could eventually plug in through the Level 2 source layer. Arangur should treat external sources as assumption providers, not as truth.

Future external source integration would need:

- Licensing review.
- Source provenance in report packages.
- A clear distinction between source narrative and Arangur-calculated portfolio impact.
- Mapping from macro assumptions into Arangur driver assumptions.
- Tests using synthetic or authorized fixtures, not live calls or restricted data.

## Reportability Requirements

Scenario outputs should remain easy to explain:

- Every scenario result should link back to its assumptions.
- Every report should distinguish deterministic point estimates from simulated ranges.
- Reports should show caveats near scenario outputs.
- Reports should avoid language like "will happen", "expected loss", or "forecast" unless a future approved methodology explicitly supports that language.
- Reports should focus on "under these assumptions, the portfolio impact would be..." rather than prediction.

## What Should Not Be Implemented Yet

Do not implement yet:

- Stochastic simulation.
- Covariance matrix estimation.
- Random-number-driven scenario runs.
- External market-data or macro-data ingestion.
- Conference Board or other licensed data integration.
- Live Plaid or custodian integration for scenario inputs.
- Production risk metrics.
- Forecasting claims.
- UI controls for scenario authoring.

The next safe step is a scenario library/source-model design or workflow-template implementation that still uses deterministic scenarios.
