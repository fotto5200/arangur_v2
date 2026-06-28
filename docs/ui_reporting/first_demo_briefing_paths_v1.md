# First Demo Briefing Paths v1

## Purpose

The first demo should lead with briefing paths instead of technical workflow labels. Each path starts with a client question, maps to internal analytics, and produces a clear advisor briefing.

## 1. Are We On Track?

- Client question: Are we on track?
- Advisor setup: Use this for a regular review where the advisor wants to anchor the conversation in total value, cash, manager allocation, and major exposures.
- Expected plain-English answer style: "The portfolio is positioned broadly as expected in the demo data, with visible cash, manager allocation, and concentration themes to review."
- Supporting evidence cards/sections: Portfolio value, cash, manager/account summary, top holdings, major sector/theme exposures, data confidence.
- Current analytics used: Valuation result, exposure overlap result, data coverage result, report package metadata.
- Gaps in current implementation: No client goal, target allocation, spending need, historical change, or IPS metadata.
- Minimum viable UI behavior: `Client question` selector value "Are we on track?", audience depth default, prepare briefing button, answer card, evidence cards, report links.
- Report output behavior: Lead with executive summary, value/cash, manager summary, evidence, caveats, and appendix links.
- Caveats: Do not claim full planning readiness or suitability.

## 2. Where Are We Too Concentrated?

- Client question: Where are we too concentrated or duplicated?
- Advisor setup: Use this when the client has asked whether managers are repeating the same bets or whether growth themes dominate the portfolio.
- Expected plain-English answer style: "The demo portfolio has visible concentration in supplied technology/AI themes and direct overlap in selected holdings."
- Supporting evidence cards/sections: Top holdings, sector/theme exposure, direct overlap rows, manager/account exposure, data confidence.
- Current analytics used: Exposure overlap result, valuation result, report package metadata.
- Gaps in current implementation: No fund look-through, no mandate metadata, no threshold scoring, no client-agreed categories beyond fixture tags.
- Minimum viable UI behavior: Show top concentration evidence first, then direct overlap and manager evidence.
- Report output behavior: Lead with concentration answer, duplicated holdings, manager context, interpretation, and "intentional or accidental?" follow-up.
- Caveats: Duplication can be intentional and should not be treated as automatically bad.

## 3. What Could Hurt Us?

- Client question: What could hurt us?
- Advisor setup: Use this for scenario risk discussion under stated assumptions.
- Expected plain-English answer style: "Under the current illustrative shock, downside is concentrated in the positions and themes matched by the scenario rules."
- Supporting evidence cards/sections: Scenario summary, largest negative contributors, affected managers/accounts, concentration evidence, scenario caveats.
- Current analytics used: Scenario result, exposure overlap result, valuation result, data coverage result.
- Gaps in current implementation: No scenario library/source layer, no stochastic range, no external macro sources, no liquidity stress.
- Minimum viable UI behavior: Show scenario answer, impact number, top contributors, assumptions, and caveats.
- Report output behavior: Lead with scenario narrative, before/after impact, drivers, manager impact, and caveats.
- Caveats: Scenario output is deterministic and illustrative, not a forecast.

## 4. Why Do We Own Manager 5?

- Client question: Why do we own Manager 5?
- Advisor setup: Use this when the advisor wants to explain a manager's role, whether it is differentiated, and whether it adds useful diversification or scenario behavior.
- Expected plain-English answer style: "Manager 5 should be justified by its mandate and differentiated role. If another manager closely shadows it across the categories that matter, that is a role question to review."
- Supporting evidence cards/sections: Manager 5 allocation, category/theme/macro exposure comparison, overlap/shadowing flags, scenario usefulness, manager role/mandate notes, data confidence.
- Current analytics used: Manager/account summary, exposure overlap result, theme/sector tags, deterministic scenario impact, data coverage result.
- Gaps in current implementation: No explicit Manager 5 mandate, intended role, expected diversification contribution, benchmark/context frame, or manager thesis metadata.
- Minimum viable UI behavior: Select Manager 5 path, show manager allocation and exposure comparison against peers, identify possible shadowing, and frame the follow-up as a mandate question.
- Report output behavior: Lead with manager role question, current evidence, overlap/shadowing interpretation, scenario usefulness, and advisor follow-up.
- Caveats: Do not automatically conclude "fire the manager." The right follow-up is: what was the mandate, why are these managers doing the same thing, and is the duplication intentional or accidental?

Frank-specific logic for this path:

- Advisor and client may have agreed on relevant categories, macro concerns, themes, mandates, or exposure buckets.
- A manager-role view can compare manager allocations across those categories.
- If Manager 5 is closely shadowed by another manager across the categories that matter, that is a red flag.
- The red flag should prompt a mandate/role question, not an automatic recommendation.
- This path connects manager overlap, role/mandate, diversification value, and scenario usefulness.

## 5. What Needs Verification?

- Client question: What needs verification?
- Advisor setup: Use this before relying on a report for client-facing discussion or when source quality matters.
- Expected plain-English answer style: "The demo data is mostly clean by design, but opaque or low-confidence items should be reviewed before overinterpreting conclusions."
- Supporting evidence cards/sections: Data confidence summary, human-review items, missing/stale/opaque flags, source transparency, artifact links.
- Current analytics used: Data coverage result, report package metadata, valuation validation.
- Gaps in current implementation: No source inventory, reconciliation status, stale-value checks by source, or verification task workflow.
- Minimum viable UI behavior: Show confidence label, review item count, key flags, and links to data coverage details.
- Report output behavior: Lead with verification status and what not to overclaim.
- Caveats: Data confidence does not forecast investment performance.
