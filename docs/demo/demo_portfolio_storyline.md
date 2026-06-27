# Demo Portfolio Storyline

## Purpose

The first demo should feel like a plausible family-office or advisor review without using real client data. The storyline gives the next implementation batch a concrete portfolio to encode as synthetic fixtures.

## Fictional Portfolio

Working name: Northstar Family Office Demo Portfolio.

Audience: an advisor colleague reviewing how Arangur v2 consolidates multiple managers and turns holdings into a clear explanation.

Valuation date: use a fixed local date in the dataset, recommended `2026-06-30`.

Reporting currency: `USD`.

## Portfolio Shape

The Northstar family has several externally managed sleeves plus a cash reserve. The advisor wants to answer three practical questions:

- Where is the family concentrated across managers?
- Which holdings are duplicated across accounts?
- How would the portfolio respond to an illustrative AI/chips selloff?

## Proposed Managers And Accounts

| Manager | Account | Role |
| --- | --- | --- |
| Atlas Core Growth | Taxable Core Account | Large-cap growth and quality compounders. |
| Harbor Value Partners | Trust Value Account | Value and dividend-oriented equities. |
| Meridian Index Solutions | Foundation ETF Account | Broad ETF exposure. |
| Signal AI Opportunities | Growth Satellite Account | Concentrated AI/chips theme. |
| Northstar Treasury Desk | Cash Reserve Account | Liquidity and operating cash. |

## Holdings Story

The portfolio should include 12 to 16 securities in the first dataset. The exact prices can be synthetic fixture prices.

Candidate holdings:

| Security | Story Role | Themes |
| --- | --- | --- |
| Microsoft | Large core holding, duplicated across core and AI satellite. | AI, growth, quality |
| NVIDIA | High-conviction AI/chips exposure, duplicated across core and AI satellite. | AI, chips, growth |
| Apple | Core growth holding. | growth, quality |
| Alphabet | Core growth and AI-adjacent holding. | AI, growth |
| Exxon Mobil | Energy/value exposure from value manager. | energy, value |
| Chevron | Energy/value exposure. | energy, value |
| JPMorgan Chase | Financial/value exposure. | financials, value |
| Berkshire Hathaway | Quality/value anchor. | value, quality |
| Vanguard Total Stock Market ETF | Broad equity exposure in foundation account. | broad_market |
| iShares Core U.S. Aggregate Bond ETF | Fixed income ballast. | fixed_income, defensive |
| Treasury bill ETF or money market proxy | Liquidity-like holding if useful. | cash_buffer, defensive |
| Cash | Explicit cash balances in each account. | cash |

## Duplication Examples

At least one duplication should be intentionally visible:

- Microsoft appears in Atlas Core Growth and Signal AI Opportunities.
- NVIDIA appears in Atlas Core Growth and Signal AI Opportunities.
- Vanguard Total Stock Market ETF creates broad market overlap with direct large-cap holdings, but v1 should label only direct security overlap unless look-through is added later.

## Exposure Examples

The portfolio should show:

- Meaningful technology exposure from Microsoft, NVIDIA, Apple, Alphabet, and the AI satellite.
- Energy/value exposure from Exxon Mobil and Chevron.
- Financial/value exposure from JPMorgan.
- Defensive ballast from bonds and cash.
- Cash reserve large enough to appear in allocation summaries.

## Scenario Shock Example

Scenario: AI and chip leadership selloff.

Plain-language story: "The advisor wants to show how much of the portfolio's current value depends on AI/chip leadership and what a simple leadership reversal might do."

Suggested deterministic shocks:

- `ai` theme: -18 percent.
- `chips` theme: -18 percent.
- broad equity fallback: -5 percent.
- energy/value: -3 percent.
- fixed income: +1 percent.
- cash: 0 percent.

V1 should apply the most specific matching rule and explain that this is illustrative, not a forecast.

## Advisor Narrative

The demo report should tell a simple story:

The family is diversified across several managers, but the consolidated view shows more exposure to the AI/chips growth theme than any single account suggests. The overlap view highlights duplicated Microsoft and NVIDIA positions across core and satellite managers. Cash and fixed income reduce the total impact of a growth selloff, but the AI/chips sleeve still drives a visible share of scenario downside. The advisor can use the report to discuss whether that overlap is intentional, whether the satellite sleeve is sized appropriately, and where the family wants active concentration versus broad market exposure.

## What Not To Include

- Real client names.
- Real account numbers.
- Real custodian exports.
- Live prices.
- Investment recommendations.
- Claims that scenario results are forecasts.
