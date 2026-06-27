# Northstar Family Office Synthetic Portfolio Review

## Synthetic-Data Caveat

Demo only: this report uses synthetic data and local fixture prices. It is intended to demonstrate Arangur v2 product behavior and is not investment advice, a client statement, or a production valuation.

## Workflow Focus

- Workflow: Quarterly Review (quarterly_review)
- Audience: Advisor preparing a recurring portfolio review meeting.
- Meeting goal: Summarize portfolio value, manager allocation, major exposures, direct overlap, and the current deterministic scenario result for a routine review.

### Primary Questions

- What changed enough to discuss in the quarterly review?
- Where are the largest manager, account, sector, theme, and cash exposures?
- Which scenario result should be used as the meeting's risk prompt?

### Emphasized Report Sections

- Executive Summary
- Portfolio Value Summary
- Manager/Account Summary
- Scenario Shock Summary

## Data Coverage and Valuation Confidence

- Valuation confidence: Mixed. Coverage is mixed: 22 of 22 held positions have local fixture prices, 22 holdings have complete sector/theme classifications, and 1 item(s) need human review before production use.
- Human review items: 1.
- Data coverage result: data_coverage_result.json.

### Key Data Quality Flags

- Synthetic Private Fund Placeholder is an opaque/private placeholder and needs a human valuation policy.

## Executive Summary

- The synthetic Northstar portfolio totals $1,708,125.00 across 5 managers and 5 accounts.
- Cash and cash-like reserves are $230,500.00, or 13.5% of the portfolio.
- The largest supplied theme exposure is Growth at 46.1%; the largest sector exposure is Technology at 26.7%.
- The largest direct overlap is Vanguard Total Stock Market ETF across Atlas Core Growth, Meridian Index Solutions, totaling $261,250.00.
- The primary scenario, AI and chip leadership selloff, shows an illustrative -$102,878.00 impact (-6.0%).

## Portfolio Value Summary

- Portfolio: Northstar Family
- Advisor label: Arangur Demo Advisory Team
- Valuation date: 2026-06-30
- Total value: $1,708,125.00
- Cash: $230,500.00 (13.5%)

## Manager/Account Summary

### Manager Summary

| Manager | Market Value | Portfolio % |
| --- | --- | --- |
| Atlas Core Growth | $439,875.00 | 25.8% |
| Meridian Index Solutions | $399,200.00 | 23.4% |
| Harbor Value Partners | $340,800.00 | 20.0% |
| Northstar Treasury Desk | $294,000.00 | 17.2% |
| Signal AI Opportunities | $234,250.00 | 13.7% |

### Account Summary

| Account | Manager | Market Value | Cash |
| --- | --- | --- | --- |
| Taxable Core Account | Atlas Core Growth | $439,875.00 | $42,500.00 |
| Foundation ETF Account | Meridian Index Solutions | $399,200.00 | $25,000.00 |
| Trust Value Account | Harbor Value Partners | $340,800.00 | $35,000.00 |
| Cash Reserve Account | Northstar Treasury Desk | $294,000.00 | $110,000.00 |
| Growth Satellite Account | Signal AI Opportunities | $234,250.00 | $18,000.00 |

## Top Holdings

| Holding | Ticker | Manager | Market Value | Portfolio % |
| --- | --- | --- | --- | --- |
| Vanguard Total Stock Market ETF | VTI | Meridian Index Solutions | $192,500.00 | 11.3% |
| iShares 0-3 Month Treasury Bond ETF | SGOV | Northstar Treasury Desk | $120,600.00 | 7.1% |
| Microsoft Corp. | MSFT | Atlas Core Growth | $107,900.00 | 6.3% |
| NVIDIA Corp. | NVDA | Signal AI Opportunities | $88,350.00 | 5.2% |
| iShares Core U.S. Aggregate Bond ETF | AGG | Meridian Index Solutions | $88,200.00 | 5.2% |
| Microsoft Corp. | MSFT | Signal AI Opportunities | $74,700.00 | 4.4% |
| JPMorgan Chase & Co. | JPM | Harbor Value Partners | $73,800.00 | 4.3% |
| Vanguard Total Stock Market ETF | VTI | Atlas Core Growth | $68,750.00 | 4.0% |
| Exxon Mobil Corp. | XOM | Harbor Value Partners | $64,900.00 | 3.8% |
| Berkshire Hathaway Class B | BRK.B | Harbor Value Partners | $64,500.00 | 3.8% |

## Sector Exposure

| Sector | Market Value | Portfolio % |
| --- | --- | --- |
| Technology | $456,475.00 | 26.7% |
| Multi Sector | $261,250.00 | 15.3% |
| Financials | $189,900.00 | 11.1% |
| Treasury | $180,900.00 | 10.6% |
| Fixed Income | $137,200.00 | 8.0% |
| Energy | $111,400.00 | 6.5% |
| Communication Services | $70,000.00 | 4.1% |
| Healthcare | $56,100.00 | 3.3% |
| Utilities | $14,400.00 | 0.8% |

## Theme Exposure

Theme exposure can exceed 100% in aggregate because a security can carry multiple theme tags.

| Theme | Market Value | Portfolio % |
| --- | --- | --- |
| Growth | $787,725.00 | 46.1% |
| Value | $562,550.00 | 32.9% |
| Quality | $490,600.00 | 28.7% |
| AI | $438,275.00 | 25.7% |
| Cash Buffer | $411,400.00 | 24.1% |
| Defensive | $388,600.00 | 22.8% |
| Broad Market | $261,250.00 | 15.3% |
| Chips | $152,475.00 | 8.9% |
| Fixed Income | $137,200.00 | 8.0% |
| Energy | $125,800.00 | 7.4% |
| Financials | $73,800.00 | 4.3% |

## Manager Overlap / Duplication Findings

| Security | Ticker | Managers | Market Value | Portfolio % |
| --- | --- | --- | --- | --- |
| Vanguard Total Stock Market ETF | VTI | Atlas Core Growth, Meridian Index Solutions | $261,250.00 | 15.3% |
| Microsoft Corp. | MSFT | Signal AI Opportunities, Atlas Core Growth, Meridian Index Solutions | $215,800.00 | 12.6% |
| iShares 0-3 Month Treasury Bond ETF | SGOV | Meridian Index Solutions, Northstar Treasury Desk | $180,900.00 | 10.6% |
| NVIDIA Corp. | NVDA | Signal AI Opportunities, Atlas Core Growth | $152,475.00 | 8.9% |
| iShares Core U.S. Aggregate Bond ETF | AGG | Meridian Index Solutions, Northstar Treasury Desk | $137,200.00 | 8.0% |
| Berkshire Hathaway Class B | BRK.B | Atlas Core Growth, Harbor Value Partners | $116,100.00 | 6.8% |
| Apple Inc. | AAPL | Signal AI Opportunities, Atlas Core Growth | $88,200.00 | 5.2% |
| Alphabet Inc. | GOOGL | Signal AI Opportunities, Atlas Core Growth | $70,000.00 | 4.1% |

## Scenario Shock Summary

Scenario shocks are deterministic demo approximations, not forecasts.

| Scenario | Before | After | Impact | Impact % |
| --- | --- | --- | --- | --- |
| AI and chip leadership selloff | $1,708,125.00 | $1,605,247.00 | -$102,878.00 | -6.0% |
| Energy rally with rate pressure | $1,708,125.00 | $1,740,714.50 | $32,589.50 | 1.9% |

Primary scenario detail: **AI and chip leadership selloff**

Illustrative shock to AI and semiconductor leadership with a mild broad equity drag.

| Holding | Ticker | Matched Rule | Before | Impact |
| --- | --- | --- | --- | --- |
| Microsoft Corp. | MSFT | theme:ai | $107,900.00 | -$19,422.00 |
| NVIDIA Corp. | NVDA | theme:ai | $88,350.00 | -$15,903.00 |
| Microsoft Corp. | MSFT | theme:ai | $74,700.00 | -$13,446.00 |
| NVIDIA Corp. | NVDA | theme:ai | $64,125.00 | -$11,542.50 |
| Alphabet Inc. | GOOGL | theme:ai | $42,000.00 | -$7,560.00 |
| Microsoft Corp. | MSFT | theme:ai | $33,200.00 | -$5,976.00 |
| Vanguard Total Stock Market ETF | VTI | theme:value | $192,500.00 | -$5,775.00 |
| Apple Inc. | AAPL | sector:technology | $63,000.00 | -$5,040.00 |

## Advisor Talking Points

- Use the quarterly review to anchor the conversation in total value, cash, manager mix, and the most visible concentration themes.
- Confirm whether the Microsoft and NVIDIA overlap is intentional before treating it as a problem.
- Use the deterministic AI/chips scenario as a discussion prompt rather than a prediction.
- Frame cash and fixed income as ballast that reduces, but does not erase, growth-theme concentration.

## Suggested Follow-Up Actions

- Ask whether the current AI/chips concentration remains intentional.
- Decide whether duplicated direct holdings should be reviewed with each manager.
- Flag any account or manager naming that should be cleaned up before a real client workflow.

## Workflow Caveats

- Quarterly review framing is synthetic and local-only.
- Scenario shocks are deterministic assumptions, not forecasts.
- The report does not prove production reconciliation or advisor suitability.

## What This Demo Proves

- Arangur v2 can run a complete local portfolio-analysis loop from synthetic fixtures.
- The canonical snapshot can feed valuation, exposure, overlap, scenario, and report generation without source-specific coupling.
- The report can explain holdings, overlap, and scenario impact in advisor-readable language.

## What This Demo Does Not Yet Prove

- It does not prove live ingestion, Plaid integration, custodian reconciliation, market-data vendor integration, or production data quality.
- It does not implement tax lots, FX, shorts, derivatives, fees, corporate actions, performance attribution, or advanced accounting.
- It does not use or validate legacy MATLAB logic.

## Next Planned Upgrades

- Add workflow-specific summary cards and period-over-period changes once historical synthetic fixtures exist.
- Add stronger validation edge cases and report-quality tests around malformed local fixtures.
- Design the future Plaid Sandbox boundary without committing credentials or using real client data.
