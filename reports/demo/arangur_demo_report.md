# Northstar Family Office Synthetic Portfolio Review

**Demo only:** this report uses synthetic data and local fixture prices. It is intended to demonstrate Arangur v2 product behavior and is not investment advice, a client statement, or a production valuation.

## Portfolio Summary

- Portfolio: Northstar Family
- Advisor label: Arangur Demo Advisory Team
- Valuation date: 2026-06-30
- Total value: $1,708,125.00
- Cash: $230,500.00 (13.5%)

## Manager Summary

| Manager | Market Value | Portfolio % |
| --- | --- | --- |
| Atlas Core Growth | $439,875.00 | 25.8% |
| Meridian Index Solutions | $399,200.00 | 23.4% |
| Harbor Value Partners | $340,800.00 | 20.0% |
| Northstar Treasury Desk | $294,000.00 | 17.2% |
| Signal AI Opportunities | $234,250.00 | 13.7% |

## Account Summary

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

## Sector Exposure

| Bucket | Market Value | Portfolio % |
| --- | --- | --- |
| Technology | $456,475.00 | 26.7% |
| Multi Sector | $261,250.00 | 15.3% |
| Financials | $189,900.00 | 11.1% |
| Treasury | $180,900.00 | 10.6% |
| Fixed Income | $137,200.00 | 8.0% |
| Energy | $111,400.00 | 6.5% |
| Communication Services | $70,000.00 | 4.1% |
| Healthcare | $56,100.00 | 3.3% |

## Theme Exposure

Theme exposure can exceed 100% in aggregate because a security can carry multiple theme tags.

| Bucket | Market Value | Portfolio % |
| --- | --- | --- |
| Growth | $787,725.00 | 46.1% |
| Value | $562,550.00 | 32.9% |
| Quality | $490,600.00 | 28.7% |
| Ai | $438,275.00 | 25.7% |
| Cash Buffer | $411,400.00 | 24.1% |
| Defensive | $388,600.00 | 22.8% |
| Broad Market | $261,250.00 | 15.3% |
| Chips | $152,475.00 | 8.9% |
| Fixed Income | $137,200.00 | 8.0% |
| Energy | $125,800.00 | 7.4% |

## Overlap And Duplication Findings

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

Primary scenario: **AI and chip leadership selloff**

Illustrative shock to AI and semiconductor leadership with a mild broad equity drag.

| Before | After | Impact | Impact % |
| --- | --- | --- | --- |
| $1,708,125.00 | $1,605,247.00 | $-102,878.00 | -6.0% |

Largest position impacts:

| Holding | Ticker | Rule | Impact |
| --- | --- | --- | --- |
| Microsoft Corp. | MSFT | theme:ai | $-19,422.00 |
| NVIDIA Corp. | NVDA | theme:ai | $-15,903.00 |
| Microsoft Corp. | MSFT | theme:ai | $-13,446.00 |
| NVIDIA Corp. | NVDA | theme:ai | $-11,542.50 |
| Alphabet Inc. | GOOGL | theme:ai | $-7,560.00 |
| Microsoft Corp. | MSFT | theme:ai | $-5,976.00 |
| Vanguard Total Stock Market ETF | VTI | theme:value | $-5,775.00 |
| Apple Inc. | AAPL | sector:technology | $-5,040.00 |

## Advisor Talking Points

- The consolidated view shows that AI/chips exposure is larger than any single account suggests.
- Microsoft and NVIDIA appear across multiple managers, making the overlap intentionality worth discussing.
- Cash and fixed income reduce total scenario impact, but the growth sleeve still drives visible downside in the AI/chips shock.
- The first demo is useful for discussing concentration, overlap, and scenario storytelling before adding live ingestion.

## Limitations And Caveats

- Data is synthetic and hand-authored for product demonstration.
- Prices, sectors, themes, and scenario rules come from local fixtures.
- Scenario shocks are deterministic approximations, not forecasts.
- The report is not investment advice and should not be treated as a client statement.
- V1 uses long-only holdings, cash at face value, one reporting currency, direct holdings, and simple aggregation.
- Plaid, custodian ingestion, market data vendors, deeper valuation, accounting, and MATLAB-informed upgrades are future adapters or upgrades.
