# Simulation Kernel Three-Surface Model v1

## Purpose

This document defines a three-surface simulation kernel for the next fuller Arangur demo. The kernel is a synthetic, replaceable layer that can generate a realistic portfolio universe, a coherent market/state-of-world environment, and daily economic valuation outputs without waiting for production ingestion, vendor market data, or a production accounting engine.

The three surfaces are:

1. Synthetic Position Universe.
2. Synthetic Market / State-of-World Generator.
3. Simplified Daily Valuation Engine.

Together they should let Arangur demonstrate the full product loop:

```text
synthetic portfolio universe
-> synthetic market/state history and scenarios
-> simplified daily valuation and value-change packages
-> report element templates
-> Client Briefing Set and Advisor Review Set
```

## Why This Enables A Fuller Demo

The current thin demo proves that synthetic local data can flow through canonical snapshots, simple valuation, exposure/overlap, scenarios, generated reports, and the browser app. The report element finder/composer now gives advisors a way to assemble briefing elements, but those elements need richer synthetic outputs to feel like a real product.

The simulation kernel gives the reporting system a plausible operating world:

- positions can cover public, private, cash, manager-level, and opaque assets;
- market state can include prices, rates, FX, volatility proxies, spreads, private marks, and confidence flags;
- daily valuation can distinguish flows from market/value changes;
- report elements can consume manager, theme, lens, scenario, and confidence summaries without using real client data.

The goal is not realism for its own sake. The goal is coherent demo behavior behind stable interfaces so downstream UI, reporting, briefing, scenario, and confidence workflows can mature before production integrations exist.

## Difference From Production Systems

This kernel is not production ingestion. It does not connect to custodians, Plaid, manager portals, statement extraction, order systems, or real client data. It produces synthetic records that should be clearly labeled as synthetic.

This kernel is not production market data. It does not license vendor feeds, fetch live prices, fetch curves, scrape data, or claim observed market truth. It generates a coherent local state-of-world that can later be replaced by vendor data, internal marks, or approved market data pipelines.

This kernel is not production accounting. It does not solve tax lots, corporate actions, settlement-date reconciliation, exact accrued interest, amortization, full fixed-income accounting, private fund capital-account accounting, or institutional performance reconciliation. It uses simplified economic valuation conventions for demo reporting.

## Surface 1: Synthetic Position Universe

### Purpose

The Synthetic Position Universe creates a plausible family-office portfolio with enough breadth, metadata, hierarchy, history, and data-quality variation to exercise Arangur's reporting and briefing model.

It should be synthetic from top to bottom. Names, identifiers, manager labels, transactions, marks, and flags should be fictional or generic demo constructs, not copied from real client portfolios or restricted data.

### Expected Asset And Instrument Coverage

The v1 universe should include 50-100 synthetic positions across:

- public equities;
- ETFs;
- fixed income and other rate-sensitive instruments;
- FX exposures or currency-linked instruments;
- commodities and energy;
- Bitcoin and other crypto exposure;
- private equity;
- private credit;
- real estate;
- data center investment;
- cash and money market positions;
- opaque manager-level positions where look-through is unavailable or deliberately summarized.

The coverage should be broad enough to demonstrate concentration, overlap, liquidity, rate sensitivity, private-market confidence, theme exposure, and scenario behavior.

### Manager, Account, And Sleeve Structure

The universe should include:

- a synthetic portfolio owner and advisor/team label;
- multiple managers with distinct roles or mandates;
- multiple accounts, each tied to a manager or internal sleeve;
- optional sleeves or mandates such as core public equity, opportunistic growth, income, liquidity reserve, private markets, real assets, and advisor review;
- holdings connected to account, manager, sleeve, and instrument records;
- cash balances represented explicitly rather than hidden inside holdings.

Manager roles should support downstream questions such as whether Manager 5 is differentiated, shadowing another manager, providing ballast, or carrying a deliberate private-market mandate.

### Transaction And History Support

The universe should support at least 90 calendar days of synthetic transaction and position history. The history does not need production-grade accounting precision, but it should be good enough to separate flows from market/value changes.

Transaction records should cover examples such as:

- buys and sells;
- contributions and withdrawals;
- income and distributions;
- private capital calls;
- private distributions;
- manager-level mark updates;
- cash sweep changes;
- fees or advisory charges if useful for reports.

For v1, transactions should preserve trade/effective dates and economic amount. Settlement reconciliation and tax-lot treatment remain out of scope.

### Themes And Lenses

Each position should carry enough metadata to support the current and future report element catalog. The starting theme/lens set should include:

- AI infrastructure;
- semiconductors;
- data center power demand;
- energy bottlenecks;
- rates sensitivity;
- private-market liquidity;
- cash generation;
- growth/value;
- defensive ballast;
- manager overlap;
- data confidence / valuation issue.

Themes can be many-to-many. A data center investment, for example, may carry AI infrastructure, real assets, data center power demand, energy bottlenecks, and private-market liquidity tags.

### Position Metadata Needed Downstream

Position-level metadata should include:

- stable position ID;
- stable instrument/security ID;
- display name;
- account ID;
- manager ID;
- sleeve or mandate ID when present;
- quantity or notional;
- quantity unit;
- currency;
- asset class;
- instrument type;
- public/private flag;
- liquidity bucket;
- sector, industry, geography, and theme tags where meaningful;
- manager role / mandate tags;
- direct price or valuation method reference;
- proxy mapping reference when needed;
- scenario sensitivity tags;
- source and synthetic provenance;
- data confidence score or tier;
- human-review flags.

### Data Quality And Human Review

The universe should deliberately include mixed data quality so reports can explain confidence rather than pretending every asset is equally clean.

Examples:

- stale private marks;
- opaque manager-level positions;
- missing look-through;
- missing cost basis;
- proxy-priced public assets;
- low-confidence classifications;
- human-review-required scenario mapping;
- cash treatment only;
- private marks that are manually updated instead of daily-priced.

These flags should flow into the market state generator, daily valuation engine, data coverage reports, Advisor Review Set elements, and any future client-facing caveats.

## Surface 2: Synthetic Market / State-of-World Generator

### Purpose

The Synthetic Market / State-of-World Generator creates a coherent valuation environment for every instrument, proxy, mark, and scenario input needed by the synthetic universe.

Market state is more than prices. It includes the assumptions and confidence metadata that explain how a position can be valued, shocked, or flagged for review.

### Generated State

The generated state should include:

- prices for directly priced public instruments;
- rates expressed through price-like instruments where useful, such as Treasury ETF proxies or zero/curve index proxy records;
- FX rates and FX-linked state variables;
- volatility proxies;
- credit spread proxies;
- private marks;
- proxy mappings;
- stale or opaque mark flags;
- data confidence;
- historical paths;
- scenario states.

The generator should cover both a current market snapshot and a rolling historical path, with at least 90 days aligned to the synthetic position/transaction history.

### Core Driver Covariance Matrix

The generator may start from a small core-driver covariance matrix rather than a giant instrument-by-instrument covariance matrix.

Example driver families:

- broad equity beta;
- growth / technology;
- semiconductors;
- rates duration;
- credit spreads;
- energy / commodities;
- USD / FX;
- volatility;
- private-market liquidity;
- crypto beta;
- real assets / inflation sensitivity.

The core drivers should have known covariance and correlation assumptions so generated history can be tested for coherence.

### Expanded Instrument-State Mapping

The larger instrument universe should be mapped from the core drivers through beta/proxy rules. Each instrument or proxy can reference:

- direct driver exposures;
- idiosyncratic noise assumptions;
- pricing lag behavior;
- stale mark behavior;
- direct price path override;
- proxy instrument ID;
- confidence tier;
- scenario mapping rule.

This avoids hand-authoring a full covariance matrix for every synthetic asset while still producing plausible co-movement across related holdings.

### Driver-To-Instrument Beta / Proxy Mapping

Public equities, ETFs, rates proxies, commodities, FX proxies, and crypto can be mapped with relatively direct beta assumptions. Private equity, private credit, real estate, and data center investments may use lagged, dampened, or manually marked proxy behavior.

Opaque manager-level positions may have a manager composite proxy instead of look-through. That is acceptable in v1 if the output clearly labels the position as proxy-valued or human-review-required.

### Covariance Recovery Check

The market generator should support a simple recovery check:

1. Start from the known source covariance matrix for the core drivers.
2. Generate synthetic driver history from that covariance.
3. Estimate covariance from the generated history.
4. Compare the estimated covariance to the source matrix within a documented tolerance.

This is not a production risk-model validation. It is a deterministic demo quality check that catches incoherent generation settings, broken seeding, and accidental driver independence.

### Scenario Library Reuse

Scenario states should reuse the same driver and proxy mapping concepts where possible. A scenario such as AI/chip selloff, rates up, liquidity stress, or energy bottleneck should specify driver shocks and then produce instrument-level or proxy-level state through the mapping layer.

This keeps deterministic scenario outputs, stochastic paths, and report element scenario requirements connected to the same state vocabulary.

### Completeness Concept

Every position should have one of the following before a valuation/reporting run proceeds:

- direct price;
- direct mark;
- proxy valuation mapping;
- simple model input;
- stale mark treatment;
- cash treatment;
- human-review flag.

The system should prefer explicit low-confidence or human-review treatment over silent omission. Missing state is itself reportable.

## Surface 3: Simplified Daily Valuation Engine

### Purpose

The Simplified Daily Valuation Engine values synthetic positions day by day using economic valuation conventions suitable for a demo. It is deliberately not a production accounting engine.

Its primary function is:

```text
positions + market state + transactions -> daily values and changes
```

The engine should create outputs that reporting can use to explain what changed, why it changed, where confidence is high or low, and which positions need advisor review.

### Daily Economic Valuation

For each date, the engine should:

- start from opening positions and values;
- apply transactions and flows;
- apply income and distributions;
- value positions using the available market state;
- separate market/value change from transaction activity;
- produce closing position, account, manager, theme, and portfolio values.

The focus is economic explanation, not accounting reconciliation.

### Value Change Components

Daily output should separate:

- opening value;
- transactions / flows;
- income / distributions;
- market/value change;
- closing value.

Attribution can be simple in v1. For example, a public equity position can use quantity times price change plus flow effects. A stale private mark can carry forward with zero daily market change until a mark update or manual valuation event occurs.

### Deliberately Avoided In V1

The v1 valuation engine should not attempt:

- tax lots;
- settlement-date reconciliation;
- institutional carry/accrual conventions;
- perfect day-count methods;
- production fixed-income accounting;
- production private-equity or real-estate accounting;
- corporate-action processing;
- custodian reconciliation;
- performance attribution suitable for client statements.

These are future replacement paths, not hidden requirements for the simulation kernel.

### Valuation Tiers

Each valued position should identify a valuation tier:

1. Direct price/mark.
2. Proxy valuation.
3. Simple formula/model.
4. Stale or manager mark.
5. Human-review required.

The valuation tier should flow into confidence summaries and Advisor Review Set elements. Client-facing output should expose confidence carefully and avoid implying production-grade valuation.

### Outputs Needed Downstream

The engine should emit:

- position values;
- manager values;
- account values;
- sleeve/mandate values when present;
- theme/lens values;
- scenario values;
- confidence summaries;
- value-change package;
- human-review and caveat lists.

These outputs should be JSON-friendly and stable enough for report element templates to consume.

## How The Three Surfaces Connect

The Synthetic Position Universe defines what exists. The Market / State-of-World Generator defines the valuation and scenario environment. The Simplified Daily Valuation Engine joins the two surfaces with transactions and produces the economic outputs used downstream.

```text
SyntheticPositionUniverse
  positions, managers, accounts, sleeves, transactions, metadata

MarketStateHistory / MarketStateSnapshot / ScenarioMarketState
  prices, proxies, marks, rates, FX, spreads, confidence, scenarios

DailyValuationEngine
  values positions date by date
  separates flows, income, market/value change
  emits valuation and value-change packages
```

The surfaces should be separately replaceable. Production ingestion can replace the synthetic universe. Vendor market data can replace the state generator. A production accounting/valuation engine can replace the simplified daily valuation engine.

## Downstream Reporting And Briefing Consumption

The report element system should consume simulation outputs through documented contracts rather than through generator internals.

Examples:

- Portfolio Status can use total value, opening/closing value, flows, value change, and confidence summary.
- Concentration elements can use position, manager, asset class, theme, and sleeve values.
- Scenario Impact by Manager can use scenario valuation packages.
- Cash Generation Summary can use income, distributions, cash positions, and liquidity tags.
- Manager Comparison can use manager values, themes, overlap signals, and confidence flags.
- Data Confidence Note can use valuation tiers, stale marks, proxy mappings, and human-review items.

Client Briefing Set elements should emphasize meeting-ready interpretation and caveats. Advisor Review Set elements can expose more diagnostic detail, proxy treatment, stale mark counts, and human-review queues.

## Deliberately Out Of Scope For V1

- Real client data.
- Live Plaid or Plaid Sandbox calls.
- Vendor market data.
- External APIs or web research.
- Production valuation or accounting policy.
- Tax-lot accounting.
- Settlement reconciliation.
- Full accrued income, amortization, or day-count treatment.
- Production fixed-income, private-equity, or real-estate accounting.
- Credentials, secrets, or `.env` inspection.
- Legacy MATLAB inspection or porting.
- Investment recommendations or market forecasts.
- Backend persistence beyond any later explicitly authorized demo-safe batch.

## Recommended Implementation Sequence

1. Define and generate the Synthetic Position Universe.

   Build 50-100 synthetic positions, accounts, managers, sleeves, themes, 90-day transactions, and data-quality flags. Validate that no real client or restricted source data is used.

2. Define and generate MarketStateSnapshot and MarketStateHistory.

   Create deterministic seeded history, direct prices, proxy mappings, rates/FX/spread/vol proxies, private marks, confidence flags, and scenario states.

3. Add covariance recovery checks.

   Generate history from a known core-driver covariance matrix and verify that estimated covariance is reasonably close to the source assumptions.

4. Implement the Simplified Daily Valuation Engine.

   Produce daily position/account/manager/portfolio values and separate opening value, flows, income/distributions, market/value change, and closing value.

5. Emit a ValueChangePackage and SimulationRunResult.

   Package outputs for downstream report elements without introducing production accounting claims.

6. Connect outputs to report element templates.

   Map existing templates to the new simulation outputs before adding new UI or report generation scope.

7. Later resume briefing set serialization/export if desired.

   Once outputs are coherent, the local Client Briefing Set and Advisor Review Set specs can serialize and eventually drive generated report packages.
