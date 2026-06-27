# Data Availability And Valuation Confidence Workstream

## Purpose

Arangur needs to understand what data is actually available before it can make credible valuation, exposure, and reporting claims across asset types.

This workstream is about source coverage, field availability, identifiers, cleansing, reconciliation, and valuation feasibility. It is not about forecasting investment performance.

## Why This Matters

The current demo works because synthetic fixtures provide clean positions, prices, classifications, and scenario tags. Real portfolios will not be that clean.

Arangur needs a disciplined way to answer:

- What records are available for each asset type?
- Which identifiers can be used to reconcile holdings, statements, and prices?
- How frequently does the data update?
- Which fields are licensed, restricted, stale, or manually supplied?
- What valuation methods are reasonable for the MVP?
- Where is human review required before a report can be trusted?

This workstream should feed a future Data Coverage / Valuation Confidence Report.

## Analyst Or Practicum Fit

This is a good candidate for analyst or practicum-style research because it can be divided into bounded domain briefs. Each brief can inventory data sources, compare fields, identify reconciliation issues, and assign an Arangur MVP feasibility rating.

The research output should be practical and implementation-facing, not academic prediction work.

## Standard Domain Brief Template

Each asset or data domain should produce a brief with:

- Source inventory.
- Available fields.
- Identifier coverage.
- Update frequency.
- Licensing or access constraints.
- Cleansing and reconciliation issues.
- Valuation approximation options.
- Arangur MVP feasibility rating: high, medium, low, or research-only.
- Human-review requirements.
- Known report caveats.
- Example synthetic records that could become future fixtures.

## Initial Domain Map

| Domain | Source Inventory And Fields | Identifiers And Frequency | Licensing / Access Constraints | Cleansing And Reconciliation Issues | Valuation Approximation Options | MVP Feasibility And Human Review |
| --- | --- | --- | --- | --- | --- | --- |
| Private equity | Capital account statements, manager portals, capital call notices, distribution notices, quarterly letters; fields include commitment, called capital, NAV, unfunded commitment, distributions, vintage, strategy, and fund name. | Fund name, manager name, legal entity, account, vintage year, statement date; updates usually quarterly with event notices between quarters. | Often manager-provided and not standardized; portal access and document use may be restricted. | Names and vintages may vary across statements; capital calls and distributions must reconcile to cash movements. | Last reported NAV, cash-flow adjusted NAV, manager estimate, or stale-value flag. | Medium to low for MVP; human review required for fund identity, stale values, and cash-flow adjustments. |
| Real estate | Appraisals, property schedules, debt schedules, rent rolls, manager statements; fields include property value, NOI, occupancy, debt, location, property type, and appraisal date. | Property name, address, legal entity, loan ID, manager ID; updates vary monthly, quarterly, or annually. | Appraisal and rent-roll data may be confidential and manually provided. | Property names and entities can be inconsistent; debt and ownership percentages must be reconciled. | Last appraisal, cap-rate approximation, debt-adjusted NAV, or manager-stated NAV. | Medium for simple reported values; human review required for ownership, debt, and stale appraisals. |
| Private credit | Loan tapes, manager statements, borrower reports, fund statements; fields include principal, coupon, maturity, rating, accrual status, sector, collateral, and NAV. | Borrower, loan ID, CUSIP if syndicated, manager ID, fund ID; updates monthly or quarterly. | Loan-level data may be restricted by manager or borrower confidentiality. | Accrual status, amendments, defaults, and partial repayments require careful treatment. | Manager NAV, amortized cost, mark-to-market if pricing exists, or impairment flag. | Medium to low; human review required for impaired loans and missing marks. |
| Mutual funds | Custodian holdings, fund reference data, NAV files, statements; fields include ticker, CUSIP, shares, NAV, expense ratio, asset class, and fund family. | Ticker, CUSIP, ISIN, fund ID; NAV typically daily for public funds. | Public fund data is easier, but look-through and licensing vary. | Share classes and reinvestments must be reconciled; look-through may not be available. | Shares times NAV; optional asset-class classification without look-through. | High for basic valuation; human review for look-through and share-class mapping. |
| ETFs | Custodian holdings, issuer data, NAV/price files, holdings files; fields include ticker, CUSIP, shares, price, NAV, sector/asset class, and sometimes holdings. | Ticker, CUSIP, ISIN; prices daily, holdings often daily or periodic. | Prices and holdings may have vendor or issuer terms. | Ticker changes, stale holdings, and overlap look-through need controlled sources. | Shares times price or NAV; optional look-through when licensed. | High for basic valuation; human review for look-through and thematic classification. |
| Data centers | Real asset schedules, property/company financials, lease summaries, power contracts; fields include capacity, occupancy, tenant concentration, power cost, location, and valuation date. | Asset name, property ID, legal entity, location, tenant IDs; updates monthly, quarterly, or ad hoc. | Highly private and manager-specific. | Operational metrics may not align to financial statements; ownership and debt matter. | Manager NAV, appraisal value, income approach, or scenario haircut. | Low for automated MVP; human review required for almost all valuation assumptions. |
| Energy infrastructure | Asset schedules, project finance reports, reserve reports, power purchase agreements, manager statements; fields include capacity, contracted revenue, commodity exposure, debt, and valuation. | Asset name, project ID, legal entity, location, contract ID; updates monthly, quarterly, or event-driven. | Contract and operating data may be confidential. | Commodity exposure, contract terms, debt, and ownership percentages are complex. | Manager NAV, DCF approximation, appraisal, or scenario haircut. | Low to medium; human review required for contracts, debt, and commodity sensitivity. |
| Hedge funds / opaque managers | Manager statements, administrator reports, risk summaries, exposure letters; fields include NAV, returns, liquidity terms, strategy, gates, and limited exposure data. | Fund name, manager, administrator, share class, account ID; updates monthly or quarterly. | Holdings may be unavailable; terms often confidential. | Share classes, side pockets, gates, and performance fees complicate reporting. | Manager NAV with liquidity and opacity caveats; strategy-level exposure tags. | Medium for NAV reporting; low for exposure precision; human review required. |
| Custodian exports | CSV/PDF/API exports, account statements, tax lots, transaction history; fields include account, security, quantity, price, market value, cash, cost basis, and transactions. | Account number or masked account, CUSIP, ticker, ISIN, security ID, transaction ID; updates daily to monthly. | Depends on custodian and export permissions; real credentials must not be committed. | Duplicate securities, missing identifiers, cash sweeps, corporate actions, and timing differences. | Direct market value if supplied, or quantity times price from trusted fixture/vendor. | High for public holdings; human review for private assets, missing IDs, and reconciliation breaks. |
| Corporate actions and identifiers | Identifier masters, corporate action feeds, issuer data, custodian notices; fields include CUSIP, ISIN, ticker, splits, mergers, spinoffs, dividends, and effective dates. | CUSIP, ISIN, ticker, FIGI or vendor IDs; updates event-driven. | Identifier and corporate-action data often requires licensed vendors. | Ticker reuse, identifier changes, split adjustments, and historical positions can break reconciliation. | Not a valuation method itself; supports accurate positions and history. | Medium as a support domain; human review required until licensed data and rules are mature. |
| Manager statements | PDF statements, portals, spreadsheets, letters; fields include NAV, holdings, exposures, cash flows, fees, commentary, and valuation date. | Manager name, fund name, account, statement date, legal entity; updates monthly or quarterly. | Often confidential and manually downloaded; extraction may require permission. | PDF extraction, naming inconsistencies, stale statements, and restatements. | Manager-stated NAV, extracted holdings if available, or confidence score by field completeness. | Medium for statement-level reporting; human review required for extraction and stale data. |

## Data Availability Versus Forecasting

Data availability asks, "Can Arangur see enough reliable information to value and explain this asset?"

Forecasting asks, "What will this asset do in the future?"

Arangur should keep these separate. Data coverage and valuation confidence can improve report trust even when the system makes no prediction at all.

## Valuation Confidence Dimensions

Possible confidence dimensions:

- Source reliability.
- Recency of valuation.
- Identifier quality.
- Reconciliation status.
- Price or NAV observability.
- Manual review status.
- Asset complexity.
- Licensing clarity.
- Methodology fit for the report purpose.

Future reports can combine these into simple labels such as high, medium, low, or needs review.

## Practicum Project Shape

A practicum or analyst project could produce:

- One domain brief per asset/data domain.
- A cross-domain field dictionary.
- A source-to-field coverage matrix.
- A proposed valuation-confidence rubric.
- Sample synthetic records for future test fixtures.
- Recommendations for MVP inclusion versus deferred research.

The output should be reviewed before it changes product behavior. The first implementation step should use synthetic examples only.

## What Should Not Be Implemented Yet

Do not implement yet:

- Vendor selection.
- Market-data ingestion.
- Document extraction.
- OCR or PDF parsing workflows.
- Real custodian ingestion.
- Real client data review.
- Automated private asset valuation.
- Investment forecasting.

This roadmap should guide future design and research batches before implementation.
