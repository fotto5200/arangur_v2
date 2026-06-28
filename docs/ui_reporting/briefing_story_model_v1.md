# Briefing Story Model v1

## Purpose

The briefing story model defines the outward-facing product structure for Arangur. It organizes analytics around client questions and advisor conversations.

## Standard Briefing Hierarchy

Every briefing story should use this hierarchy:

1. Client question
2. Plain-English answer
3. Key evidence
4. Interpretation
5. Proposed action
6. Confidence and caveats
7. Drill-down / appendix

The hierarchy should be visible in UI and reports. Analytics appear as evidence, not as the starting point.

## Canonical Client Questions

### 1. Are We On Track?

- Purpose: Establish whether the portfolio still supports the client's stated goals, cash needs, risk tolerance, and role expectations.
- Likely audience: Client, advisor, family office principal, or investment committee.
- Analytics/evidence needed: Portfolio value, cash level, allocation summary, manager allocation, recent changes, data confidence, and scenario context.
- Current Arangur support level: Partial. The current demo can show valuation, cash, manager totals, exposures, and deterministic scenario impact, but does not yet model client goals or plan targets.
- Future upgrades: Add goal/IPS context, target ranges, distribution requirements, liquidity needs, and period-over-period change.
- Caveats: "On track" should not imply financial planning certainty. Current demo answers portfolio evidence, not full wealth planning.

### 2. What Changed?

- Purpose: Explain material changes in value, allocation, exposure, manager roles, or data quality since the last review.
- Likely audience: Advisor and client in a regular review meeting.
- Analytics/evidence needed: Prior snapshot, current snapshot, contribution by manager/account/asset class, exposure deltas, cash-flow context, and data changes.
- Current Arangur support level: Low. Current artifacts are mostly single-period; they can explain current state but not robust changes over time.
- Future upgrades: Add historical synthetic snapshots, change attribution, cash-flow adjusted returns, manager change logs, and report diffs.
- Caveats: Changes must distinguish market movement, cash flow, manager action, source update, and data correction.

### 3. Are We Generating The Cash We Need?

- Purpose: Connect portfolio liquidity and income to client spending, distributions, commitments, or operating needs.
- Likely audience: Client, advisor, family office CFO, or operations reviewer.
- Analytics/evidence needed: Cash balances, income estimates, distribution schedule, private commitment schedule, liquidity buckets, and expected cash needs.
- Current Arangur support level: Partial. Current demo tracks cash balances but not income generation, commitments, or spending schedules.
- Future upgrades: Add liquidity schedule, income classification, capital calls/distributions, and client cash-need assumptions.
- Caveats: Cash availability is not the same as sustainable income. Current synthetic demo does not prove cash-flow forecasting.

### 4. How Safe Is That Cash Or Strategy?

- Purpose: Explain reliability, liquidity, concentration, drawdown risk, and data confidence behind a cash source or strategy.
- Likely audience: Client, advisor, family office principal, or risk-focused stakeholder.
- Analytics/evidence needed: Cash location, instrument type, manager exposure, credit/liquidity characteristics, scenario impact, concentration, and data confidence.
- Current Arangur support level: Partial. Current demo can identify cash and scenario impact, but not full cash safety, credit risk, or liquidity terms.
- Future upgrades: Add cash instrument classification, liquidity terms, credit exposure, concentration thresholds, and mandate-level risk notes.
- Caveats: Safety language must be careful. Arangur can explain exposure and assumptions; it should not certify safety.

### 5. Is The Original Thesis Still Intact?

- Purpose: Compare the current portfolio or manager against the reason it was originally owned.
- Likely audience: Advisor, client, investment committee, or internal due diligence reviewer.
- Analytics/evidence needed: Original thesis, intended role, current exposures, manager allocations, scenario behavior, performance attribution, and data confidence.
- Current Arangur support level: Low to partial. Current demo can show current exposures and scenario impact but does not yet store original thesis metadata.
- Future upgrades: Add manager thesis metadata, mandate notes, benchmark/context frames, expected role, and thesis drift detection.
- Caveats: Thesis review requires advisor-approved context. The system should prompt a review, not declare a thesis broken without mandate evidence.

### 6. Where Are We Too Concentrated Or Duplicated?

- Purpose: Identify direct holdings, themes, sectors, managers, or mandates that create unintended concentration or duplication.
- Likely audience: Advisor, client, investment committee, or manager oversight user.
- Analytics/evidence needed: Exposure summary, top holdings, sector/theme tags, direct overlap, manager allocations, and manager role comparison.
- Current Arangur support level: Strong for direct security overlap and fixture-supplied sector/theme exposure; limited for mandate or look-through overlap.
- Future upgrades: Add fund look-through, manager mandate metadata, threshold labels, category-level duplication scoring, and role review cards.
- Caveats: Duplication is not automatically bad. The report should distinguish intentional thesis reinforcement from accidental overlap.

### 7. What Drove The Result?

- Purpose: Explain the major contributors to return, risk, valuation change, or scenario impact.
- Likely audience: Client, advisor, analytical stakeholder, or investment committee.
- Analytics/evidence needed: Contribution by manager, account, security, sector, theme, asset class, and scenario rule.
- Current Arangur support level: Partial. Current scenario output can show position/account/manager impact under assumptions, but current performance attribution is not implemented.
- Future upgrades: Add period-over-period valuation, cash-flow adjusted attribution, return contribution, and manager/security drivers.
- Caveats: Drivers must be tied to a defined result period and methodology.

### 8. Why Do We Own Each Manager?

- Purpose: Explain each manager's role, mandate, diversification value, overlap, and usefulness in the client conversation.
- Likely audience: Advisor, client, family office principal, or manager oversight user.
- Analytics/evidence needed: Manager allocation, manager exposures by agreed categories/themes/macros/mandates, overlap/shadowing comparison, scenario behavior, and intended role metadata.
- Current Arangur support level: Partial. Current demo can show manager allocation, direct overlap, themes, sectors, and scenario impact, but does not yet store intended manager roles.
- Future upgrades: Add manager mandate, intended role, thesis, expected diversification contribution, benchmark/context frame, and role-drift review.
- Caveats: A manager that shadows another may still be intentional. The correct product action is a role/mandate question, not an automatic recommendation.

### 9. What Could Hurt Us?

- Purpose: Turn scenarios, concentration, liquidity, and data coverage into a focused risk conversation.
- Likely audience: Client, advisor, investment committee, or risk stakeholder.
- Analytics/evidence needed: Scenario impacts, largest negative contributors, concentrated exposures, manager overlap, liquidity notes, and confidence flags.
- Current Arangur support level: Good for deterministic scenario impact and concentration highlights; limited for liquidity and real-world scenario libraries.
- Future upgrades: Add scenario source model, key drivers, multiple scenario comparison, and eventually reproducible stochastic ranges when authorized.
- Caveats: Scenario results are illustrative impacts under assumptions, not forecasts.

### 10. What Should We Change Now?

- Purpose: Convert evidence into advisor-reviewed action options.
- Likely audience: Advisor and client, with advisor approval before client-facing use.
- Analytics/evidence needed: Concentration flags, overlap, scenario impact, data confidence, mandate fit, tax/liquidity constraints, and advisor-approved action rules.
- Current Arangur support level: Low. Current demo can suggest follow-up questions but not recommend portfolio changes.
- Future upgrades: Add advisor-approved action templates, planning constraints, tax/liquidity notes, and review workflow.
- Caveats: Arangur should not provide autonomous investment advice. It should propose questions or options for advisor approval.

### 11. What Needs Verification?

- Purpose: Make data gaps, stale values, missing identifiers, opaque private assets, and human-review items explicit.
- Likely audience: Advisor, operations reviewer, analyst, or family office operations user.
- Analytics/evidence needed: Data coverage result, valuation confidence, missing price/identifier flags, stale data, source transparency, and human-review items.
- Current Arangur support level: Strong for the local synthetic data-coverage prototype.
- Future upgrades: Add source inventory, reconciliation status, stale-value checks, extraction confidence, and verification task workflow.
- Caveats: Data confidence is about source readiness, not investment quality or future returns.
