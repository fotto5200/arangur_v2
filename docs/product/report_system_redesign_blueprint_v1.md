# Report System Redesign Blueprint v1

## Purpose

This blueprint consolidates Frank's product review of the lean revaluation mockups into a report-system design direction. It is design documentation only.

It does not implement code, change advisor UI, add report views, wire report elements, generate analytics outputs, add backend endpoints, change Docker/deployment configuration, use live or real data, or add dependencies.

The goal is to keep Arangur's report system simple while making room for richer analytic machinery underneath. Reports should answer client and advisor questions. They should not expose every available analytic output.

## Governing Principles

- Report purpose before analytics output.
- One report, one question.
- Every visible item earns its screen space.
- No analytics tourism.
- One denominator and one category system per table.
- Every row declares or implies a representation level.
- Visual reports are first-class when they explain faster than tables.
- Families can be broad, but each report instance should stay simple.
- Advisor chooses summary versus detail; the default report does not expand itself into a dashboard.
- High-dimensional analytics belong under low-dimensional reports.
- Coverage, confidence, and representation basis are product facts, not footnotes to hide.
- If data is missing, the report is unavailable, advisor-only, or caveated. It is not faked.

## Four Master Question Families

### Ownership / Exposure

Core question: What do I own, who is managing it, and how is the portfolio represented?

This family covers allocation, manager role, lens exposure, portfolio representation status, and concentration by a single grouping system.

### Performance / Plan

Core question: How did the portfolio, manager, or strategy do versus a benchmark, plan, cash need, or objective?

This family covers integrated performance attribution, cash-flow support, and future goal or liability reports. These reports require benchmark, plan, cash need, or history inputs. Holdings data alone is not enough.

### Risk / Downside

Core question: What could hurt, how much, and what drives the downside?

This family covers deterministic scenario downside, probabilistic scenario ranges, concentration, coverage/confidence warnings, opaque exposure, manager downside, and benchmark or proposed-allocation comparisons.

### Positioning / Forward View

Core question: What view does the portfolio express, and what would change if the portfolio changed?

This family covers thesis/lens positioning, current-versus-proposed portfolio views, upside/downside tradeoffs, and manager rebalancing rationale.

## Report Family Architecture

### Ownership / Exposure Families

- Aggregated Asset Allocation
- Allocation by Manager
- Full Lens Exposure
- Manager by Lens Exposure
- Multi-Lens Exposure Review
- Lens Exposure Index
- Portfolio Status / Portfolio Representation Status
- Manager Role Summary
- Single-Manager Detail

### Performance / Plan Families

- Integrated Performance Attribution Summary
- Integrated Performance Attribution Detail
- Performance Attribution by Lens
- Cash Flow Delivered
- Cash-Flow Support Outlook
- Cash Flow by Manager/Sleeve
- Goal / Liability Matching

### Risk / Downside Families

- Current Portfolio Scenario Downside
- Scenario by Manager
- Scenario by Lens
- Scenario Versus Benchmark
- Probabilistic Scenario Range
- Coverage and Confidence Warning
- Opaque / Review-Required Exposure
- Concentration by Consistent Category System

### Positioning / Forward View Families

- Portfolio vs Benchmark Scenario Range
- Current vs Proposed Portfolio
- Proposed Allocation Change
- Upside / Downside Tradeoff
- Manager Rebalancing Rationale
- Thesis / Lens Positioning

## Current Mockup Redesign Decisions

| Current mockup | Verdict | Product issue | Redesign direction | Timing |
| --- | --- | --- | --- | --- |
| Portfolio Status | Keep, revise representation language | Useful as a high-level anchor, but must not imply every underlying position is fully known | Show current state and completeness of view; distinguish direct holdings, fund/NAV positions, manager-level holdings, look-through holdings, and review-required exposure | Build now in revised mockup spec |
| Aggregated Asset Allocation | Keep | Broad allocation is useful, but manager detail should not be stuffed into this table | Keep broad asset-type buckets, small row count, and Other grouping; add a separate Allocation by Manager report | Build now for asset allocation; design soon for manager allocation |
| Cash-Flow Support Readiness | Replace as client/advisor report | "Cannot show because missing inputs" is readiness, not a report | Treat readiness as internal/advisor setup. Split report content into Cash Flow Delivered for prior-period generated/paid-out cash and Cash-Flow Support Outlook for stated-need support | Build only when matching cash-flow prerequisites exist; keep real/client readiness gated |
| Concentration Review | Redesign | Current table mixes asset type, theme/manager/sleeve, review-required status, and held-at-mark status in one Area column | Use one grouping system at a time: asset type, manager/sleeve, geography, selected lens, or selected theme. Move review/mark/confidence rows to Coverage and Confidence or Opaque Exposure reports | Build revised design now; implement later |
| Coverage and Confidence Warning | Keep | Useful and conceptually coherent | Show coverage summary, review-required count/value, held-at-mark exposure, approved policy exposure, and one or two practical caveats. Advisor-review default; client-facing only when material | Build now / advisor first |
| Manager Role Summary | Redesign as manager-centered family | Current role field repeats manager label and does not explain mandate or expression | Portfolio-level Manager Role Summary, Single-Manager Detail, and Manager-by-Lens Exposure. Show intended role, portfolio share, actual exposure, larger downside/key risk, and mandate leakage warning when supported | Design now; build when manager mandate data is approved |
| Scenario Downside Summary | Keep and expand into family | Simple current-portfolio scenario table works, but scenarios need comparison variants | Keep 2-4 deterministic scenarios max, portfolio impact, percent, value after, and clear scenario caveat. Add scenario by manager/lens, benchmark, current-vs-proposed, and probabilistic range variants | Build current downside now; design range/comparison next |

## Representation-Level Rule

A report row may represent any of these levels:

- direct security;
- fund/NAV position;
- manager-level sleeve;
- look-through holding;
- thematic bucket;
- lens bucket;
- benchmark or proxy;
- proposed allocation.

Reports must not mix these levels casually. If a table mixes representation levels, it must label the representation basis and denominator so the reader knows whether rows are additive, comparable, or diagnostic only.

## Lens Reports

A lens is a complete classification system for viewing the portfolio through one question. Examples include asset class, sector/industry, geography, value/growth, AI Adoption, Energy Security, supply-chain fragility, geopolitical bloc, private liquidity, and credit stress.

Lens report rules:

- The selected lens defines the whole category system.
- Allocation lens totals should show all buckets, not only the largest buckets.
- Additive allocation views should sum to 100% or clearly label a non-additive view.
- Whole-portfolio and manager-by-manager modes should share the same lens definitions.
- Lens assignment confidence and review buckets should not be hidden.

Core lens reports:

- Full Lens Exposure: maps the whole portfolio into every bucket of one selected lens.
- Manager by Lens Exposure: compares managers inside the same lens.
- Multi-Lens Exposure Review: shows a compact set of lens-level conclusions without pretending different lenses add together.
- Lens Exposure Index: a normalized summary score or bucket distribution for one lens, only after the lens has approved assignments and denominator rules.

## Benchmarks And Lens-Bucket Benchmarks

Benchmarks are explicit product objects. A benchmark may be:

- broad index;
- ETF;
- single equity;
- custom basket;
- manager-specific benchmark;
- policy benchmark;
- approved proxy for one lens bucket.

V1 should use predefined and approved benchmark/proxy maps. Advisor freeform benchmark creation should not be part of the first report build.

Synthetic Attribution Prerequisite Pack v1 now supplies a local-only policy benchmark and AI Adoption / Energy Security lens-bucket proxy map for future synthetic attribution mockups. These are demo prerequisites, not production benchmark recommendations and not benchmark scenario outputs.

Lens-bucket benchmark maps support:

- performance attribution;
- scenario comparison;
- probabilistic range comparison;
- manager value explanation;
- thesis/lens positioning.

Each benchmark map must state:

- benchmark/proxy id and display name;
- the report family it supports;
- the lens, bucket, manager, or policy scope it represents;
- denominator and representation basis;
- whether it is approved for client-facing use;
- caveat when it is a proxy rather than a true benchmark.

## Integrated Performance Attribution

Integrated Performance Attribution answers:

```text
Did the portfolio or manager add value versus benchmark, and what decision produced that value?
```

The user-facing product language should not force the term "Brinson" as the main label. Internally, the system may use Brinson-style allocation and selection logic where appropriate, but the report family is broader.

Synthetic Attribution Prerequisite Pack v1 supplies deterministic benchmark, return, weight/flow, theme-benchmark detail, decomposition, and manager prerequisite inputs for the local synthetic attribution mockups. Timing remains unavailable until it is tied to cleanly specified portfolio states and trade/flow history.

The attribution chain:

```text
global benchmark
-> theme benchmark selection
-> theme benchmark sizing
-> asset selection
-> asset sizing
-> residual / unexplained
-> actual portfolio
```

Required modes:

- whole-portfolio attribution;
- manager-by-manager attribution;
- lens-bucket attribution where approved lens assignments and benchmark maps exist;
- summary report for narrative and visual explanation;
- detail report for full decomposition.

Timing gate:

- Include timing only when comparing two clearly specified portfolio states over a defined period.
- Omit timing when clean trade/holding history, flow treatment, and an approved timing method are absent.
- Treat `Residual / unexplained` as the remaining reconciler; it may include unmeasured timing, data, flow, or reconciliation effects.
- Do not label residual/noise as timing.

Manager/advisor value explanation is a central product purpose of this family. Reports should help answer why the client is paying the advisor or manager: outperformance, risk reduction, scenario resilience, thesis expression, asset selection, exposure sizing, and timing only when actually measurable.

## Probabilistic Scenario Reports

Deterministic scenario reports answer "what happens under this approved scenario." Probabilistic scenario reports answer "what range of outcomes is plausible under an approved scenario family or model."

Probabilistic reports are not distant v2 by definition. They can come relatively early after the analytics have approved range methodology and benchmark/proxy maps.

Core range report:

- scenario name and horizon;
- portfolio expected impact or central estimate;
- portfolio 5th-95th percentile range, or approved equivalent;
- benchmark/proxy range when available;
- one sentence that explains the comparison;
- methodology caveat that this is a model range, not a forecast.

Candidate visual example:

```text
Energy Shock / Energy Security / 90 days / Portfolio vs Benchmark

Benchmark range: [ -8% ............ +2% ]
Portfolio range: [ -5% ........ +6% ]
Central estimate: Portfolio +1%, Benchmark -3%
```

Do not generate probabilistic report content from deterministic point scenarios alone.

## Chart-First / Visual-First Report Candidates

Visual-first reporting should be used when it reduces cognitive load. Candidate forms:

- probabilistic scenario range number line;
- portfolio vs benchmark scenario range;
- current vs proposed allocation range;
- manager vs benchmark comparison;
- integrated performance attribution waterfall;
- lens exposure distribution bar or small multiple;
- downside contribution by manager/theme;
- current vs proposed exposure shift chart.

Visual-first does not mean chart-heavy. A visual report should still have one question, one conclusion, a small number of metrics, and a clear denominator.

## Build Now / Design Soon / Defer

### Build Now

- Revised Portfolio Representation Status.
- Aggregated Asset Allocation with broad buckets and Other grouping.
- Coverage and Confidence Warning.
- Current Portfolio Scenario Downside using the existing two-scenario full-revaluation outputs.
- Concentration by one consistent grouping system at a time.
- Report mockup spec v2 that applies Frank's review before any UI wiring.

### Design Soon

- Allocation by Manager.
- Full Lens Exposure.
- Manager by Lens Exposure.
- Manager Role Summary and Single-Manager Detail.
- Integrated Performance Attribution Summary and Detail from Synthetic Attribution Prerequisite Pack v1.
- Manager Attribution Summary and Lens-Based Performance Attribution from the synthetic attribution prerequisite pack.
- Lens-bucket benchmark map contract for any production or scenario-comparison usage beyond the synthetic pack.
- Probabilistic Scenario Range.
- Portfolio vs Benchmark Scenario Range.

### Defer

- Real/client Cash Flow Delivered or Cash-Flow Support Outlook until reliable cash-flow history, stated need, projection basis, and funding-source logic exist.
- Cash Flow by Manager/Sleeve until cash-flow source data is reliable.
- Goal / Liability Matching until explicit plan/liability data exists.
- Current vs Proposed Portfolio until proposed allocation objects exist.
- Advisor freeform benchmark creation.
- Performance timing attribution until two clean portfolio states, period returns, cash flows, and holdings history are available.
- Client-facing lens/thematic reports until approved assignments and caveats exist.

## Implementation Sequencing

A. Revised report mockup spec v2.

- Rewrite current lean mockup decisions into a concrete product spec.
- Keep outputs as documents/mockups first.
- Do not wire to Advisor Preview, Populate, Present, or generated reports yet.

B. Lens/benchmark map design.

- Define lens assignment artifact shape, benchmark/proxy map shape, representation basis, and denominator rules.
- Use approved maps only.

C. Integrated attribution design.

- Define summary/detail variants, whole-portfolio and manager modes, benchmark prerequisites, residual/timing gate, and visual waterfall grammar.

D. Probabilistic scenario report design.

- Define approved range methodology, benchmark range comparisons, horizon labels, caveat policy, and visual number-line grammar.

E. Revised fixtures/mockups implementation.

- Only after Frank accepts the design direction, update fixture generators and mockups.
- Keep first implementation local/synthetic.
- Keep advisor UI/report wiring paused until separately approved.
