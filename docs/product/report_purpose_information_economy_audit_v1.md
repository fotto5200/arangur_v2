# Report Purpose And Information Economy Audit v1

## 1. Purpose

This audit decides what reports should show. It does not decide what analytics can produce.

The governing rule is simple:

```text
Every visible report item must justify its placement on the screen.
```

The system should not start from:

```text
What can the analytics produce?
```

It should start from:

```text
What client or advisor question deserves an answer, and what is the minimum evidence needed to answer it?
```

Do not show an analytic output merely because it exists. That is analytics tourism. It makes the product feel busy, defensive, and harder to trust. A table, label, paragraph, caveat, metric, or detail row earns screen space only if it helps someone explain, decide, reassure, question, compare, or act.

Multiple reports are allowed. A giant everything-report is not. Each report should answer one simple question with simple evidence.

## 2. Master Report Question Families

### A. Ownership / Exposure Explanation

Core question:

```text
What do I own across multiple accounts in one clear, aggregated view?
```

Possible sub-questions:

- What do I own by asset class?
- What do I own by manager?
- What do I own by geography?
- What do I own by strategy, theme, thesis, or exposure category?
- Why do I have each manager?
- What role is each manager or sleeve supposed to play?
- Where are apparent duplicates or overlaps?

Report posture: mostly descriptive. This family should make the portfolio legible before it becomes analytical.

### B. Performance / Plan Explanation

Core question:

```text
How am I doing versus benchmarks, objectives, and my plan?
```

Possible sub-questions:

- How am I doing versus benchmark?
- How am I doing versus family or institution goals?
- Is the portfolio supporting capital preservation?
- Is the portfolio producing needed cash flow?
- Are assets matched to expected liabilities or future commitments?
- Are charitable, lifestyle, housing, education, spending, or legacy goals on track?
- Which parts of the portfolio are helping or hurting the plan?

Report posture: outcome-oriented. This family should not be faked from holdings data alone. If plan, benchmark, liability, or cash-need inputs are missing, the report should say so or defer.

### C. Risk / Downside Explanation

Core question:

```text
Where are the concentration risks and downside exposures?
```

Possible sub-questions:

- Where are the largest concentrations?
- Which managers are not really diversifying one another?
- Which scenarios matter most?
- Where are hidden overlaps?
- Which positions, managers, sleeves, or themes dominate downside?
- Which risks are material enough to discuss with the client?
- Which risks are present but not worth screen space?

Report posture: selective. Risk reporting must not become a dump of every negative number. It should identify the few material exposures that change the conversation.

### D. Positioning / Forward View Explanation

Core question:

```text
How is the portfolio positioned to express strategic or thematic upside views?
```

Possible sub-questions:

- What themes or strategic views does the portfolio currently express?
- Is the portfolio positioned for the advisor's intended thesis?
- What would change if allocations shifted between managers, sleeves, or themes?
- What upside exposure would increase?
- What downside exposure would decrease?
- Which proposed changes are meaningful versus cosmetic?
- How should a hypothetical new allocation be explained simply?

Report posture: intentionality. This family should connect holdings to a thesis or proposed change. It should wait when the thesis, proposal, or position-to-thesis assignments are not published.

## 3. Client / Advisor Variability

Different clients and situations require different reports.

Some clients want only the big picture. Some clients want to go into the numbers. Some situations involve one advisor. Some involve multiple advisors, family-office staff, outside managers, trustees, or investment committees. Some are planning-focused. Some are risk-focused. Some are thematic or strategic. Some are mainly relationship and reassurance conversations.

Therefore the system may need multiple reports and report sets. But each report must still be simple.

The product should support:

- client briefings with only the few points that deserve conversation;
- advisor review packs with more diagnostics and review queues;
- internal analytic review with details that should never reach the main client screen;
- developer/QA views for testing and artifact inspection.

The system should not solve variability by making every report bigger. It should solve variability by choosing the right report for the right audience.

## 4. Report Audience Tiers

| Tier | What belongs | What does not belong | Detail level | Language style | Caveat policy |
| --- | --- | --- | --- | --- | --- |
| Client briefing view | Plain-English answer, one or two decisive metrics, a small table only when comparison matters, material caveat if it changes interpretation | Raw ids, source files, model names, full coverage tables, valuation traces, debug labels, long lists of positions | Lowest. Usually 1-3 headline metrics and 0-5 rows | Calm, explanatory, meeting-ready | Only material caveats. One practical sentence, not an audit trail |
| Advisor review view | Diagnostics, material contributors, review-required flags, confidence/coverage labels, more rows when they support prep | Raw JSON, schema names, file paths, implementation traces, internal model construction controls | Moderate. Enough to decide what should be client-facing | Direct and specific | Caveats can name review needs, assumptions, and limitations |
| Internal analytics/review view | Full attribution outputs, coverage details, validation results, reconciliation checks, source artifact references | Client-ready prose claims, recommendations, advisor UI controls | High. This is where machinery can live | Technical but disciplined | Exhaustive enough for review, still not a debug dump |
| Developer/QA view | Artifact ids, schema versions, file paths, API behavior, validation results, local storage behavior | Client/advisor presentation claims | As much as needed to test | Technical | Debug and test caveats are allowed only here |

Tier rule:

```text
If a field only helps prove the system worked, it is Developer/QA or internal analytics content, not report content.
```

## 5. Information Economy Principles

- One report element, one job.
- Show the conclusion before the machinery.
- Prefer one decisive sentence over five explanatory rows.
- Use tables only when comparison matters.
- Hide methodology unless it changes interpretation.
- Caveats must be material, not exhaustive.
- Confidence and coverage should guide trust, not overwhelm.
- No duplicate labels or meta-labels.
- No analytics tourism.
- No showing outputs merely because they exist.
- Avoid report elements that are really debug panels.
- Avoid source or methodology detail masquerading as client value.
- When in doubt, simplify.

Practical interpretation:

- A manager-impact table is useful only if manager comparison is the point.
- A top-position row is useful only if naming the position changes the conversation.
- A caveat is useful only if it affects whether the advisor can rely on the number.
- A confidence label is useful only if it helps decide whether to show, withhold, or qualify a point.

## 6. Report Admissibility Test

A report is admissible only if it can be stated as:

```text
This report helps [audience] answer [specific question] by showing [minimal evidence].
```

If that sentence is weak, the report should be merged, postponed, or removed.

For each report or report element, ask:

- What exact client/advisor question does this report answer?
- Who needs it?
- What conversation or decision does it support?
- What is the minimum visible evidence needed?
- What would be lost if the report disappeared?
- Is it useful now, or merely possible?
- Should it be client-facing, advisor-only, drilldown-only, or internal-only?
- Should it exist now, later, or not at all?

Default answer when uncertain:

```text
Do not build it yet.
```

## 7. Visible-Item Admissibility Test

Every visible item inside a report must answer:

- What does this item help the advisor or client understand?
- What would be lost if it disappeared?
- Is it essential evidence or merely available data?
- Can it be made shorter?
- Can it be merged with another item?
- Can it be moved to advisor review?
- Can it be hidden behind detail/drilldown?
- Can it be replaced by one sentence?
- Is it source, methodology, or debug information masquerading as report content?

Hard rule:

```text
If removing an item does not weaken the conversation, remove it.
```

## 8. Existing Report Element Inventory

This inventory covers current repo elements and near-term planned concepts. It is not a build list.

Each audit row uses this field order:

```text
id/name; family; exact question; purpose; audience; situation; implied visible content; decision;
essential visible fields; suppress by default; advisor-only; internal-only; caveat policy;
maximum detail; source analytics; open questions.
```

### Current repo elements

- `portfolio_status`; Ownership / Exposure plus Performance / Plan; "Where do we stand right now?"; meeting anchor; client and advisor; broad opening conversation; total value, cash, allocation, confidence; keep and simplify; total value, cash/liquidity, one status sentence, maybe one confidence label; suppress detailed allocation rows, source files, method labels; advisor-only confidence drilldown; internal-only validation/source traces; one synthetic/demo or valuation confidence caveat when material; 3 metrics, 0-3 rows, 1 caveat; valuation summaries, portfolio status inputs, analytic portfolio status; should this include performance once benchmarks exist?
- `concentration`; Risk / Downside; "Where is exposure unusually concentrated?"; find material concentration and overlap; client when material, advisor by default; risk prep and client discussion; largest themes/sectors/managers/overlaps; keep but split by purpose and simplify; top concentration, percent of portfolio, reason it matters; suppress all small buckets, duplicate concentration views, raw classifications; advisor-only overlap diagnostics; internal-only mapping/classification evidence; caveat only for proxy/incomplete classification or if concentration is not risk by itself; 1 sentence, 3 metrics, 5 rows; concentration inputs, theme exposure, manager overlap; should concentration by sector and concentration by theme stay separate or merge under one selector?
- `scenario_impact_by_manager`; Risk / Downside; "Which managers matter most under this scenario?"; manager-level stress explanation; advisor by default, client appendix only; scenario/risk meeting; scenario impact by manager and maybe theme; simplify and rename in client mode; scenario name, total impact, top 3 manager impacts, short interpretation; suppress raw scenario construction, all managers when not material, probability language; advisor-only full manager table and confidence mix; internal-only market-state ids, valuation traces, reconciliation; deterministic scenario caveat plus coverage caveat when material; 2 metrics, 3-5 rows, 2 caveats; full revaluation manager attribution, portfolio summary; should client view show manager names or only roles/themes?
- `cash_generation_summary`; Performance / Plan; "Is the portfolio producing or holding enough cash for the need?"; cash and liquidity support; client and advisor only when cash is a meeting question; spending, distribution, liquidity conversation; cash balance, cash generation proxy, liquidity caveat; defer as plan report until cash need inputs exist, keep as current demo support; cash balance, expected/observed cash generation, cash need label if provided; suppress all-manager cash comparisons and duplicate liquidity labels; advisor-only source/coverage of income proxy; internal-only transaction/source traces; caveat must distinguish cash balance from recurring income; 3 metrics, 0-5 rows, 2 caveats; cash generation input, daily valuation/history, future cash-flow outputs; what planning inputs define "enough"?
- `manager_comparison`; Ownership / Exposure plus Risk / Downside; "Why do we own each manager and how do they differ?"; manager role and mandate comparison; advisor default, client appendix when needed; manager review, overlap discussion; manager value, role, theme exposure, contribution/confidence; keep but turn into Manager Role Summary for client mode; manager name/role, value %, one role sentence, material overlap/risk flag; suppress exhaustive metrics by manager; advisor-only full comparison grid; internal-only raw mandate rules and classification evidence; caveat only for missing or synthetic mandate labels; 5 manager rows maximum; manager comparison inputs, manager attribution, theme exposure; should client mode compare managers or explain roles one by one?
- `data_confidence_note`; Risk / Downside plus Internal Readiness; "Can we trust the numbers enough to show them?"; readiness and caveat control; advisor review by default; client only if a limitation affects interpretation; confidence label, review count, material issue; move from standalone client report to compact warning unless central; confidence label, one issue sentence, material review-required amount/count; suppress full confidence taxonomy; advisor-only review queue; internal-only coverage map, manifest, raw issue ids; caveat must be practical interpretation guidance; 1 label, 1 sentence, 0-3 items; data confidence map, valuation coverage manifest, coverage/confidence attribution; should confidence be a label inside each element or a separate advisor review element?

### Planned or implied elements

- `aggregated_asset_allocation`; Ownership / Exposure; "What do I own by broad bucket?"; make ownership legible; client and advisor; first-meeting overview; asset class and maybe liquidity/geography mix; build now as a lean element; top buckets and "other"; suppress tiny buckets and implementation source; advisor-only classification exceptions; internal-only mapping rules; caveat only for incomplete classification; 1 chart/table, 5 rows; position universe, portfolio status, theme exposure; which bucket system should be default?
- `account_sleeve_overview`; Ownership / Exposure; "Where is the portfolio held and organized?"; explain account/sleeve structure; advisor and some clients; multi-account families, trustees; accounts/sleeves, values, roles; defer or merge into asset allocation unless account structure is central; account/sleeve name, value, purpose; suppress every account if not decision-relevant; advisor-only account-level diagnostics; internal-only account ids/source records; caveat if account data incomplete; 5 rows; position catalog, account/sleeve attribution; when does account detail help rather than clutter?
- `manager_role_summary`; Ownership / Exposure; "What role is each manager supposed to play?"; explain why managers exist; client and advisor; manager review, family-office overview; role, value, key exposure, one risk flag; build now; manager display name, role, value %, one sentence; suppress metric overload and ranking tone; advisor-only mandate diagnostics; internal-only classification rules; caveat missing mandate labels; 5 rows; manager comparison, manager attribution, pack role lens; are roles approved enough for client language?
- `geographic_exposure`; Ownership / Exposure plus Risk / Downside; "Where is geographic exposure concentrated?"; explain country/region risk; client only when geography matters; geopolitical/tax/currency conversation; top regions and material exception; defer; region, %, short note; suppress country long tail; advisor-only look-through limitations; internal-only mapping evidence; caveat if fund look-through incomplete; 5 rows; position classifications, future look-through; does current data support geography honestly?
- `cross_scenario_downside_resilience`; Risk / Downside; "Which downside scenarios matter most?"; compare scenario impacts; advisor default, client when scenario risk is central; risk review; worst scenario, best/less bad scenario, top common drivers; build now in lean form; two scenario impacts and one sentence; suppress all position lists by default; advisor-only top managers/positions; internal-only bundle references; caveat deterministic and two-scenario-only; 2 metrics, 2 rows, 2 caveats; cross-scenario revaluation summary; should client view show one worst-case number or a small table?
- `theme_exposure`; Positioning / Forward View plus Ownership / Exposure; "What strategic themes does the portfolio already express?"; show strategic positioning; advisor and client if theme is part of story; thematic discussion; top themes and overlap; defer or build as advisor-first; top themes, percent/value, one interpretation; suppress all themes and overlap diagnostics; advisor-only overlap and classification confidence; internal-only matcher values; caveat non-additive if using broad theme tags; 5 rows; theme exposure summary, theme attribution; are broad tags precise enough for client thesis language?
- `thesis_lens_attribution`; Positioning / Forward View; "Does the portfolio express the intended thesis?"; thesis-specific positioning; advisor first; thesis review; bucket totals under one approved lens; defer until assignments exist; lens name, bucket totals, confidence; suppress readiness-only placeholders in client view; advisor-only unresolved assignments; internal-only evidence packets/LLM rationale; caveat assignment confidence and review required; 5 bucket rows; future position-thesis assignments plus revaluation; which thesis lens is first?
- `top_impacted_positions`; Risk / Downside; "Which individual positions drive the result?"; detail support; advisor only by default; diagnostic review; top positions by absolute impact; move to advisor drilldown, not standalone client report; position display name, impact, manager, confidence; suppress from client default; advisor-only table; internal-only valuation trace; caveat when coverage low; 5 rows; position value comparisons, cross-scenario top positions; should client briefings ever name positions?
- `coverage_confidence_review`; Risk / Downside plus Internal Readiness; "What must be reviewed before relying on the report?"; readiness gate; advisor/internal; pre-publication QA; material review items; advisor-only, not client default; material issue count and top review items; suppress every issue; advisor-only queue; internal-only manifests and rule traces; caveat should block or qualify outputs; 5 rows; coverage/confidence attribution, valuation coverage manifests; what threshold blocks client-facing output?
- `performance_vs_benchmark`; Performance / Plan; "How did we do versus benchmark?"; benchmark comparison; client/advisor; performance review; returns, benchmark, attribution; defer until real benchmark/performance inputs exist; return vs benchmark, period, explanation; suppress if synthetic or incomplete; advisor-only performance diagnostics; internal-only calculation traces; caveat benchmark appropriateness; 3 metrics, 5 rows; future performance system; which benchmarks are approved?
- `performance_vs_plan`; Performance / Plan; "Are we on track versus the plan?"; plan progress; client/advisor; annual or quarterly planning review; plan target, actual, gap; defer until plan inputs exist; target, current, gap, status sentence; suppress generic market commentary; advisor-only assumption diagnostics; internal-only planning model; caveat assumptions and dates; 3 metrics; future planning inputs; what is the canonical plan object?
- `cash_flow_support`; Performance / Plan; "Can portfolio cash flows support expected needs?"; spending/liability support; client/advisor; spending, distributions, commitments; cash need, cash generation, liquidity runway; defer unless cash need is provided; need, available/expected, gap; suppress income proxy detail; advisor-only source coverage; internal-only cash-flow construction; caveat not guaranteed; 3 metrics, 3 rows; cash summary, future cash flows; what counts as committed cash need?
- `liability_goal_matching`; Performance / Plan; "Are assets matched to future commitments?"; liability matching; advisor/client; commitments, education, real estate, philanthropy; funded status by horizon; defer; horizon, commitment, matched assets, gap; suppress unrelated holdings; advisor-only assumptions; internal-only liability model; caveat assumptions and dates; 5 rows; future planning/liability inputs; which liabilities belong in v1?
- `capital_preservation_review`; Performance / Plan plus Risk / Downside; "Is downside risk consistent with preservation goals?"; risk-to-objective check; client/advisor; preservation mandate; downside exposure versus threshold; defer until objective/threshold exists; risk status, key downside, threshold; suppress arbitrary risk scores; advisor-only scenario diagnostics; internal-only model assumptions; caveat deterministic scenarios; 3 metrics, 3 rows; revaluation plus plan thresholds; what preservation rule is approved?
- `goal_progress_summary`; Performance / Plan; "Are goals on track?"; goal progress; client/advisor; planning meetings; goal status, funding, next review; defer; goal, status, gap; suppress investment internals; advisor-only assumptions; internal-only planning engine; caveat planning assumptions; 5 goals; future planning data; should Arangur own this or integrate later?
- `proposed_allocation_change`; Positioning / Forward View; "What would change if we rebalance?"; proposal explanation; advisor/client after proposal workflow exists; rebalance discussion; current vs proposed summary; defer; allocation change, expected exposure change, reason; suppress optimizer machinery; advisor-only before/after diagnostics; internal-only proposal engine; caveat hypothetical; 3 changes, 5 rows; future proposal outputs; when does proposal workflow exist?
- `scenario_before_after_comparison`; Positioning / Forward View plus Risk / Downside; "Does a proposed change improve the scenario picture?"; compare current/proposed downside; advisor/client if proposal exists; allocation decision; before/after scenario impacts; defer; current impact, proposed impact, difference; suppress all scenario internals; advisor-only detailed attribution; internal-only construction traces; caveat hypothetical and deterministic; 3 metrics, 3 rows; future proposed revaluation; should this wait for approved proposal objects?
- `upside_downside_tradeoff`; Positioning / Forward View; "What tradeoff does this positioning create?"; explain balance of opportunity and risk; advisor/client; strategic allocation; upside exposure vs downside exposure; defer; one upside, one downside, net interpretation; suppress pseudo-precision; advisor-only assumptions; internal-only scenario set; caveat no forecast; 2 metrics, 3 rows; future upside/downside scenario set; what upside scenarios are approved?
- `manager_rebalancing_rationale`; Positioning / Forward View; "Why move capital between managers?"; rebalancing explanation; advisor/client after proposal workflow; manager change discussion; current role, proposed change, rationale; defer; manager, change, reason, effect; suppress ranking tone and all diagnostics; advisor-only full comparison; internal-only proposal trace; caveat hypothetical; 5 rows; manager attribution plus proposal outputs; should manager changes be shown before investment committee approval?

## 9. Revaluation-Derived Output Audit

| Output | Default tier | Visible summary form | Max reasonable detail | Show more only when | Do not show | Master family | Evidence or machinery |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Portfolio revaluation summary | Advisor by default, client when scenario is central | One scenario impact sentence plus total impact | 2 metrics, 1 caveat | Client asks scenario question or preservation/risk objective is central | Base/scenario market-state ids, schema, manifest, full coverage table | Risk / Downside | Essential evidence |
| Manager attribution | Advisor default, client appendix selectively | Top 3 managers by impact or role-based explanation | 3-5 rows | Manager selection or mandate discussion is the point | All groups by default, raw group ids, reconciliation fields | Risk / Downside and Ownership | Essential when manager conversation exists |
| Account attribution | Advisor-only by default | Account-level warning only when account structure matters | 3-5 rows | Trustees/tax/account structure is part of decision | Every account, raw account ids | Ownership / Exposure | Supporting evidence |
| Sleeve attribution | Advisor default, client only for mandate explanation | Sleeve/mandate impact summary | 3-5 rows | Sleeve roles are known and meeting-relevant | Raw sleeve ids and full diagnostics | Ownership / Exposure and Risk / Downside | Supporting evidence |
| Coverage attribution | Advisor/internal default | Compact "review needed" warning | 1 label, 0-5 rows | Coverage materially affects a visible result | Full bucket tables in client briefing | Risk / Downside | Trust machinery, not main content |
| Confidence attribution | Advisor/internal default | Confidence label and practical warning | 1 label, 0-5 rows | Confidence changes whether a number should be shown | Full confidence taxonomy in client view | Risk / Downside | Trust machinery |
| Cross-scenario summary | Advisor default, client when risk review is explicit | Worst scenario plus small comparison | 2 scenarios, 2-3 rows | Comparing scenarios helps choose discussion focus | Source bundle references, all top positions | Risk / Downside | Essential risk evidence |
| Top impacted positions | Advisor-only by default | Drilldown table | 5 rows | Position names change the decision or question | Default client table of individual holdings | Risk / Downside | Supporting evidence |
| Theme attribution | Advisor default until taxonomy is approved for client | Top themes impacted or exposed | 5 rows | Theme is part of advisor/client story | Non-additive full tag table, matcher details | Positioning / Forward View | Supporting evidence |
| Thesis readiness / thesis attribution | Internal/advisor readiness until assignments exist | "Not available yet" or review status | 1 sentence | Advisor requested a thesis lens and needs to know why unavailable | Client-facing readiness artifact as report content | Positioning / Forward View | Machinery until assignments exist |
| Valuation coverage caveats | Advisor default, client only if material | Practical caveat sentence | 1-2 caveats per element | It changes trust or interpretation | Exhaustive caveat lists, valuation traces | All families | Trust guidance |

Opinion:

- The full revaluation layer is strong enough to support lean risk reports.
- It is not a reason to show full attribution tables by default.
- The most client-ready revaluation content is a scenario-level sentence plus one small comparison table.
- Manager and top-position detail belongs in advisor review unless the meeting is specifically about managers or positions.

## 10. Proposed Lean First Report Set

The first set should prove the grammar, not exhaust the analytics. Do not put all of these into every report. Pick the few that answer the meeting question.

### 1. Portfolio Status

- Master family: Ownership / Exposure, with Performance / Plan as future extension.
- One-sentence job: Anchor the conversation in current portfolio scale, liquidity, and readiness.
- Audience: Client briefing and advisor review.
- Situation served: Opening summary, broad check-in.
- Visible headline: "The portfolio is approximately $X, with Y in cash/liquidity and Z items needing review."
- Recommended visible content: total value, cash/liquidity, one confidence/readiness label, optional largest allocation bucket.
- Maximum headline metrics: 3.
- Maximum table rows: 0-3.
- Maximum caveats: 1.
- Source analytics: portfolio status inputs, valuation summaries, data confidence map.
- Caveat behavior: Only show confidence caveat when it changes trust.
- Do not show: source file names, schema, raw coverage tables.
- Deferred extensions: benchmark, plan progress, goal funding.

### 2. Aggregated Asset Allocation

- Master family: Ownership / Exposure.
- One-sentence job: Show what the client owns in broad, understandable buckets.
- Audience: Client briefing and advisor review.
- Situation served: Multi-account aggregation, first meeting, trustee overview.
- Visible headline: "Most exposure sits in these broad buckets."
- Recommended visible content: 4-5 asset/liquidity buckets and percent/value.
- Maximum headline metrics: 1.
- Maximum table rows: 5.
- Maximum caveats: 1.
- Source analytics: position universe, portfolio status, theme exposure if approved.
- Caveat behavior: Caveat only if classification/look-through is incomplete.
- Do not show: long tail, raw ids, tiny allocations.
- Deferred extensions: geography, currency, account-specific views.

### 3. Manager Role Summary

- Master family: Ownership / Exposure.
- One-sentence job: Explain why each major manager or sleeve is in the portfolio.
- Audience: Advisor review first, client briefing when manager explanation is needed.
- Situation served: Manager review, family-office review, overlap concern.
- Visible headline: "Each major manager should have a clear job."
- Recommended visible content: manager, role, portfolio %, one material exposure or risk flag.
- Maximum headline metrics: 2.
- Maximum table rows: 5.
- Maximum caveats: 1.
- Source analytics: manager comparison, manager attribution, approved manager role lens.
- Caveat behavior: Caveat missing/synthetic mandate labels.
- Do not show: manager rankings, all metric columns, raw mandate mapping.
- Deferred extensions: manager rebalancing rationale.

### 4. Concentration Review

- Master family: Risk / Downside.
- One-sentence job: Identify the few concentrations that deserve discussion.
- Audience: Advisor review and client briefing when material.
- Situation served: Risk prep, hidden overlap, concentration conversation.
- Visible headline: "These are the concentrations most worth discussing."
- Recommended visible content: top concentrations by theme/sector/manager role, percent/value, why it matters.
- Maximum headline metrics: 2.
- Maximum table rows: 5.
- Maximum caveats: 1.
- Source analytics: concentration inputs, theme exposure, manager overlap.
- Caveat behavior: Caveat only for proxy or incomplete classification.
- Do not show: multiple overlapping concentration tables saying the same thing.
- Deferred extensions: selected account/sleeve concentration.

### 5. Scenario Downside Summary

- Master family: Risk / Downside.
- One-sentence job: Show how the portfolio changes under one or two approved downside scenarios.
- Audience: Advisor review by default, client briefing for risk-focused meetings.
- Situation served: Downside risk review, preservation discussion.
- Visible headline: "Under the selected scenario, the portfolio revalues by about $X."
- Recommended visible content: scenario name, total impact, impact percent, top 3 manager/sleeve contributors if needed.
- Maximum headline metrics: 3.
- Maximum table rows: 3-5.
- Maximum caveats: 2.
- Source analytics: portfolio revaluation summary, manager/sleeve attribution, cross-scenario summary.
- Caveat behavior: Deterministic scenario and coverage caveat only.
- Do not show: probability, raw market-state construction, full position impact table.
- Deferred extensions: before/after proposed allocation comparison.

### 6. Coverage And Confidence Warning

- Master family: Risk / Downside, advisor readiness.
- One-sentence job: Warn when data or valuation coverage changes what can be trusted.
- Audience: Advisor review. Client only if material and unavoidable.
- Situation served: Pre-publication review, low-confidence valuation.
- Visible headline: "Some outputs need review before relying on them."
- Recommended visible content: confidence label, review-required count/value if material, top material review items.
- Maximum headline metrics: 2.
- Maximum table rows: 5.
- Maximum caveats: 1.
- Source analytics: coverage attribution, confidence attribution, valuation coverage manifests.
- Caveat behavior: Practical interpretation guidance, not audit trail.
- Do not show: full coverage taxonomy in client briefing.
- Deferred extensions: review workflow and approval status.

### 7. Cash-Flow Support

- Master family: Performance / Plan.
- One-sentence job: Answer whether available cash and income support a stated need.
- Audience: Client and advisor only when cash need is explicit.
- Situation served: Spending, distribution, commitments.
- Visible headline: "Cash support appears sufficient/insufficient for the stated need."
- Recommended visible content: need label, available cash/liquidity, expected cash generation or gap.
- Maximum headline metrics: 3.
- Maximum table rows: 3.
- Maximum caveats: 2.
- Source analytics: cash generation summary, future cash-flow outputs.
- Caveat behavior: Always distinguish cash balance from recurring income.
- Do not show: cash-generation report without a cash question.
- Deferred extensions: liability matching and goal funding.

Do not build a client-facing thesis/lens attribution report until position-thesis assignment artifacts exist. Do not build performance versus plan until plan inputs exist.

## 11. Report Element Content Budgets

Use these as design constraints for future fixtures and tests:

- Headline metrics: maximum 3 per element; 1-2 preferred.
- Visible table rows: maximum 5 in client view; maximum 8 in advisor review unless the element is explicitly a review table.
- Caveats: maximum 2 in client view; maximum 4 in advisor review.
- Top positions: maximum 0 by default in client view; maximum 5 in advisor review.
- Paragraphs: maximum 2 short paragraphs per element; 1 preferred.
- Explanatory labels: maximum 3 labels per element; avoid stacked labels.
- If a table and paragraph say the same thing, keep the paragraph or the table, not both.
- If more than 5 low-confidence or review-required positions exist, summarize the issue and show only material items.
- If an element needs more than 2 caveats to be honest, it probably belongs in advisor review.
- If a report element cannot be explained in one sentence, split it or defer it.

## 12. Recommended Suppression Rules

- Suppress zero or immaterial impacts.
- Suppress duplicate caveats.
- Suppress technical methodology unless in advisor-review view and it changes interpretation.
- Summarize many low-confidence positions as a single warning.
- Show only material review-required items.
- Avoid raw ids unless internal view.
- Avoid source file names in report views.
- Avoid full JSON/debug traces.
- Avoid long lists of small contributors.
- Avoid showing both a table and a paragraph that say the same thing.
- Avoid showing coverage/confidence unless it changes how the result should be interpreted.
- Avoid showing thesis readiness in client view unless it explains why a requested view is unavailable.
- Suppress all small buckets into "Other" when the long tail does not change the decision.
- Suppress source/reconciliation fields from client and advisor reports unless a reconciliation issue is material.

## 13. Advisor / Client Language Standards

Preferred language:

- plain English;
- short sentence first;
- methodology only when it builds trust;
- caveats as practical interpretation guidance;
- no internal jargon such as "artifact", "manifest", "schema", "scenario basis vector", "pricing function registry", "coverage manifest", or "valuation trace" in client-facing copy.

Bad vs better examples:

| Topic | Bad | Better |
| --- | --- | --- |
| Scenario impact | "The scenario bundle manifest produced manager attribution under market_state_scenario_rate_shock_2026-06-30." | "Under the Rate Shock scenario, the portfolio value falls by about $4.8 million." |
| Coverage caveat | "Seven rows are held_at_mark_with_caveat and twelve rows have review_required coverage status." | "Some private or opaque holdings need review, so use the scenario result directionally." |
| Cross-scenario | "Cross-scenario output has scenarios_included and source_bundle_references." | "AI / Chip Selloff is the larger downside case in the current two-scenario review." |
| Manager concentration | "Manager A has the largest absolute impact contribution in the attribution rows." | "The AI infrastructure manager drives the largest share of the downside in this scenario." |
| Thesis readiness | "Thesis bucket attribution requires published position thesis assignment artifacts." | "This thesis view is not ready yet because positions have not been approved into thesis buckets." |

Language rules:

- Say what changed before saying how it was calculated.
- Say "scenario", not "forecast".
- Say "use directionally" when coverage is limited.
- Say "needs review" instead of exposing coverage-status codes.
- Say "not ready yet" instead of showing readiness artifacts in client reports.

## 14. Build-Now / Defer / Kill Recommendations

### Build now

Build these as lean report-element input/view fixtures next, not as UI changes:

- Portfolio Status, simplified.
- Aggregated Asset Allocation.
- Manager Role Summary.
- Concentration Review, with one concentration lens per element.
- Scenario Downside Summary using full revaluation.
- Coverage And Confidence Warning for advisor review.

Cash-Flow Support can be included only if it is framed around an explicit cash need or clearly marked as a limited current demo support element.

### Defer

- Performance Versus Benchmark: defer until approved benchmark and performance inputs exist.
- Performance Versus Plan: defer until plan/objective inputs exist.
- Liability/Goal Matching: defer until liabilities/goals exist.
- Capital Preservation Review: defer until preservation thresholds exist.
- Goal Progress Summary: defer until goal data exists.
- Strategic Theme Positioning: defer for client mode until theme language is approved for the meeting.
- Thesis/Lens Attribution: defer until position-thesis assignments exist.
- Proposed Allocation Change: defer until proposal objects exist.
- Scenario Before/After Comparison: defer until proposed allocation revaluation exists.
- Upside/Downside Tradeoff: defer until approved upside scenario framing exists.
- Manager Rebalancing Rationale: defer until a proposal workflow exists.

### Advisor-only

- Top Impacted Positions.
- Full manager/account/sleeve attribution tables.
- Coverage/Confidence Review.
- Account/Sleeve Overview when used for operational structure.
- Theme overlap diagnostics.

### Internal-only

- Revaluation scenario index.
- Bundle manifests.
- Valuation coverage manifests.
- Pricing function assignments.
- Position valuation traces.
- Source file references.
- Schema/reconciliation/debug fields.
- Thesis readiness artifacts except as an advisor-safe unavailable explanation.

### Kill or merge

- Kill a standalone client-facing Top Impacted Positions element by default. Keep it as advisor drilldown.
- Merge Data Confidence Note into a compact confidence warning unless the meeting is specifically about data readiness.
- Merge Account/Sleeve Overview into Asset Allocation unless account structure is the question.
- Do not build separate table variants for every grouping dimension until the first lean grammar works.
- Do not show both legacy simplified scenario outputs and full revaluation outputs in the same report family.

## 15. Next Implementation Implications

The next implementation tranche should map revaluation outputs into lean report-element input/view fixtures using this audit.

It should:

- produce lean report-element input/view fixtures;
- not expose every available analytic field;
- preserve client/advisor/internal separation;
- include tests that prevent overstuffed report views;
- enforce information budgets;
- suppress source files, raw ids, manifests, schema names, and valuation traces from report fragments;
- use full revaluation outputs for scenario and cross-scenario report content;
- avoid adding advisor UI controls until report shape is approved.

The next tranche should not add:

- advisor UI changes;
- new top-level report choices;
- backend endpoints;
- report library/history;
- deployment work;
- live data;
- external APIs;
- real client data.

## 16. Open Questions For Frank

1. Should client briefings ever show top positions, or only manager/theme summaries?
2. How many caveats is too many?
3. Should coverage/confidence appear as a compact label or separate report element?
4. Should cross-scenario summaries show one worst-case number or a small comparison table?
5. Should report elements default to advisor-review mode first, then client mode later?
6. Which existing report elements should be killed entirely?
7. Which master question family should be strongest in the first demo?
8. Should performance/plan reports wait until planning inputs exist?
9. Should positioning/forward-view reports wait until proposed allocation workflows exist?
10. For numbers-oriented clients, should detail appear as separate report elements rather than expanding the client briefing element?
11. Should manager names appear in client downside reports, or should client reports use manager roles first?
12. What materiality threshold should suppress small scenario impacts?
13. What level of valuation coverage should block client-facing point numbers?
14. Should the first revaluation-derived client demo show AI / Chip Selloff, Rate Shock, or only the larger of the two?
