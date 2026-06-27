# Report Workflow Implications

## Purpose

This note explains how the scenario roadmap and data availability workstream should shape future Arangur report families.

The current demo supports advisor-readable reports with deterministic valuation, exposure, overlap, and scenario sections. Local workflow templates now make those sections more intentional without turning the demo into a production UI or advisor assistant.

## Current Reporting Baseline

Current support:

- Synthetic native demo source.
- Synthetic Plaid-shaped mock source.
- Canonical snapshot normalization.
- Simple valuation.
- Exposure and direct overlap analytics.
- Deterministic scenario shocks.
- Markdown and HTML advisor reports.
- Static local report index.
- Workflow-run metadata and templates with labels such as `quarterly_review`, `manager_overlap_review`, `scenario_risk_review`, `intake_review`, and `data_coverage_review`.

## First-Round Report Families

### Portfolio Overview Report

- Purpose: Give an advisor or colleague a concise view of total value, accounts, managers, top holdings, cash, and major exposures.
- Likely audience: Advisor colleague, product reviewer, or internal stakeholder.
- Required inputs: Canonical snapshot, valuation result, exposure summary, report package metadata, synthetic-data caveats.
- Current demo support level: Strong for public long-only synthetic holdings, cash, accounts, managers, and top holdings.
- Future upgrades: Add workflow-specific summary blocks, data coverage indicators, account-level validation warnings, and optional appendix tables.
- Caveats: Not a client statement, not audited, synthetic only, and no guarantee of production reconciliation.

### Exposure / Overlap Report

- Purpose: Explain concentration, duplicated holdings, sector/theme exposure, manager overlap, and possible follow-up questions.
- Likely audience: Advisor reviewing multi-manager portfolios or a product reviewer evaluating the overlap value proposition.
- Required inputs: Canonical snapshot, valuation result, exposure overlap result, security classification fields, manager/account mappings.
- Current demo support level: Strong for direct security overlap and supplied theme/sector tags; no fund look-through yet.
- Future upgrades: Add fund look-through when licensed data exists, manager-level exposure narratives, threshold-based flags, and overlap severity labels.
- Caveats: Theme exposure can exceed 100 percent in aggregate, classifications are supplied by fixtures, and current overlap is direct-holding overlap only.

### Scenario Risk Report

- Purpose: Show how portfolio value changes under stated scenario assumptions.
- Likely audience: Advisor, investment committee support user, or product reviewer focused on scenario explainability.
- Required inputs: Canonical snapshot, valuation result, scenario definitions, scenario results, assumption caveats.
- Current demo support level: Good for deterministic point-estimate shocks by theme, sector, asset class, security, and cash.
- Future upgrades: Add scenario library/source metadata, key-driver assumptions, scenario comparison views, and eventually covariance-based impact ranges.
- Caveats: Deterministic scenario outputs are illustrative and are not forecasts. Future covariance/error-bar outputs would still describe model-driven ranges under assumptions, not known probabilities of future events.

### Data Coverage / Valuation Confidence Report

- Purpose: Explain what data is available, what is missing or stale, how each asset was valued, and where human review is required.
- Likely audience: Advisor, operations reviewer, analyst, or implementation team assessing whether a portfolio can be reported responsibly.
- Required inputs: Source inventory, valuation results, data freshness fields, identifier quality, reconciliation status, licensing/provenance metadata, and human-review flags.
- Current demo support level: Workflow framing exists through `data_coverage_review`, but the current synthetic fixtures assume clean data and do not yet score coverage or confidence.
- Future upgrades: Add coverage summaries by asset class, missing-field tables, valuation-confidence labels, stale-data warnings, and domain-specific review requirements.
- Caveats: Data confidence is not investment forecasting. A high-confidence valuation only means the source and method are clearer, not that the asset will perform well.

## Deterministic Scenario Reporting Now

Current scenario reporting should continue to:

- Show a single before/after point estimate.
- List the matched shock rule.
- Explain the scenario narrative in plain language.
- Label the scenario as deterministic and illustrative.
- Avoid probability, forecast, or expected-return language.

Good report language:

```text
Under this illustrative shock, the portfolio impact is...
```

Avoid report language:

```text
The portfolio is expected to lose...
```

## Covariance And Error-Bar Reporting Later

If Arangur later adds covariance or random-number-driven simulation, scenario reports may include:

- Median impact.
- Percentile range.
- Error bars by account, manager, asset class, or total portfolio.
- Simulation seed and model version.
- Driver assumptions and covariance provenance.

The report should still make the assumption chain visible:

```text
narrative scenario -> driver assumptions -> simulated driver outcomes -> portfolio impact range
```

The report must state that ranges depend on model assumptions and input data quality.

## Why Data Coverage Could Be A Differentiator

Many portfolio tools show polished values without explaining how reliable the underlying data is. Arangur can differentiate by making data coverage and valuation confidence visible:

- Which assets are priced from observable public data?
- Which assets use manager-reported NAV?
- Which records are stale?
- Which identifiers are missing or ambiguous?
- Which values require human review?
- Which report conclusions are limited by data coverage?

This can make reports more trustworthy, especially for family-office portfolios with public securities, private funds, real assets, and opaque managers in the same view.

## Workflow Template Implications

Workflow templates use the report families as building blocks:

- `quarterly_review`: portfolio overview plus selected exposure and scenario highlights.
- `manager_overlap_review`: exposure / overlap report first, with supporting valuation tables.
- `scenario_risk_review`: scenario risk report first, with deterministic assumptions and caveats.
- `intake_review`: source mapping and readiness first, with follow-up questions for validation gaps.
- `data_coverage_review`: valuation-confidence and data-coverage framing first, with explicit caveats that scoring is not implemented yet.

The next implementation batch can add actual synthetic data coverage metadata and confidence scoring without changing the analytics engine.
