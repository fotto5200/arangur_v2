# Project Profile

Arangur v2 is a revived portfolio communication, consolidation, analytics, and advisor-reporting product. It should help turn scattered portfolio holdings and market assumptions into clear, advisor-readable analysis.

## Intended Users And Buyers

Primary users are likely advisors, investment teams, family-office operators, and portfolio service providers who need to explain client portfolios across accounts, managers, custodians, asset classes, and risk scenarios.

Likely buyers include advisory firms, wealth management teams, outsourced CIO providers, and portfolio analytics groups that need clearer client-facing reporting without rebuilding their whole operating stack.

## Background

The original Arangur system was MATLAB-centered and may contain useful ideas about valuation, attribution, accounting, portfolio structure, and analytics. For v2, that project is reference material only. The first phase should avoid becoming a MATLAB port.

## V2 Repositioning

Arangur v2 should be built as a thin, modular demo first. The system should define stable interfaces around data ingestion, canonical portfolio state, market data, valuation, analytics, scenarios, and reporting. Each component should be simple at first and replaceable later.

## Product Questions To Answer Eventually

- What does the client own across accounts and managers?
- What is the portfolio worth under consistent assumptions?
- Where are the major exposures, concentrations, overlaps, and gaps?
- How does the portfolio respond to simple market or factor shocks?
- What changed since the last reporting period?
- What should an advisor be able to explain quickly and confidently?
- Which source data needs normalization, cleansing, or escalation?

## First Demo Direction

The first demo should use local synthetic data and produce a canonical portfolio snapshot, market data fixture, simple valuation, exposure and overlap summary, scenario shock output, and advisor-readable report or viewer.

## Out Of Scope For The First Phase

- Live Plaid integration.
- Plaid Sandbox implementation.
- Real client data.
- Credentials, secrets, private keys, or auth tokens.
- Deep valuation engines.
- Full accounting, corporate actions, and data-cleansing systems.
- Legacy MATLAB porting or deep MATLAB inspection.
- Production UI/dashboard work.
