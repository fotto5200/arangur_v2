# Revised Report Mockup Spec v2

## 1. Purpose

This spec defines the next generation of Markdown report mockups before mockups or fixtures are regenerated.

The v1 lean mockups proved the generation path: full-revaluation and attribution outputs can be mapped into compact report view fixtures and Markdown review artifacts. The v2 mockups must now reflect the Report System Redesign Blueprint rather than merely exposing available analytics.

This spec determines what the revised mockups should show, what current mockups should change or stop being generated, what new mockups should be added, and what each mockup's visible content should contain.

This tranche does not implement code, modify advisor UI, add report views, wire report elements, regenerate report fixtures, regenerate Markdown mockups, generate analytics outputs, add backend endpoints, change runtime behavior, use live or real data, or add dependencies.

Update after Synthetic Report Prerequisite Pack v1: local-only synthetic prerequisites now exist for whole-portfolio cash-flow delivered/support views, approved synthetic manager mandate language, and complete AI Adoption / Energy Security lens assignments. This updates v2 mockup readiness only; it does not wire reports into Advisor Preview, Populate, Present, or generated reports, and it does not create real-client cash-flow, benchmark, performance, probabilistic, proposed-portfolio, or deployment readiness.

Update after first v2 mockup review: the cash-flow report shape is split into Cash Flow Delivered for prior-period advisor value delivered and Cash-Flow Support Outlook for forward-looking need support. The split keeps delivered cash, paid-out cash, projected generation, and surplus/shortfall from being overpacked into one report.

Update after Synthetic Attribution Prerequisite Pack v1: local-only synthetic benchmark, lens-bucket proxy, period return, weight/flow, decomposition, and manager attribution prerequisite artifacts now exist for future Integrated Performance Attribution Summary, Integrated Performance Attribution Detail, Manager Attribution Summary, and Lens-Based Performance Attribution mockups. This does not create final attribution reports, wire Advisor Preview / Populate / Present / generated reports, approve production benchmarks, or make timing, scenario-versus-benchmark, probabilistic range, proposed-portfolio, real-client, or deployment readiness available.

## 2. Governing Design Rules

- One report, one question.
- Every visible item earns screen space.
- No analytics tourism.
- One denominator and one category system per table.
- Every report declares an explicit representation level.
- Visual-first reports are allowed and often preferred when the visual explains faster than a table.
- Summary and detail variants are separate report shapes.
- The advisor chooses which report and detail level is appropriate for the client conversation.
- Missing inputs produce gated/readiness states, not fake client-facing reports.
- Timing attribution is optional and methodologically gated.
- Predefined benchmark/proxy maps come before any freeform advisor benchmark construction.
- Readiness artifacts may explain why a report is unavailable, but they are not client report substitutes.
- Current v2 specifications may include illustrative examples, but those examples are not regenerated fixtures.

## 3. Current v1 Mockup Disposition

| Current v1 mockup | v1 verdict | Problem found | v2 direction | Mockup v2? | Variant |
| --- | --- | --- | --- | --- | --- |
| Aggregated Asset Allocation | Keep / revise lightly | It is a good simple Ownership / Exposure report, but it should not carry manager detail | Keep broad asset-type allocation, small table, and Other grouping. Add companion Allocation by Manager. Do not mix asset type and manager rows in one table unless intentionally designed | Yes | `aggregated_asset_allocation_mockup_v2.md` |
| Cash-Flow Support Readiness | Kill / demote as report | Readiness is not a client/advisor report; v1 says inputs are missing rather than answering a cash-flow question | Move readiness to internal/advisor setup. When synthetic prerequisites exist, split report content into Cash Flow Delivered and Cash-Flow Support Outlook | Yes, as split v2 reports | `cash_flow_delivered_mockup_v2.md`; `cash_flow_support_outlook_mockup_v2.md` |
| Concentration Review | Redesign / split | v1 mixes asset type, theme/manager/sleeve, review-required status, and held-at-mark status in one Area column | Concentration must use one grouping system at a time. Create variants by asset type and by manager/sleeve; possibly by selected lens later. Move review-required and held-at-mark exposure to Coverage and Confidence | Yes | `concentration_by_asset_type_mockup_v2.md`; `concentration_by_manager_sleeve_mockup_v2.md` |
| Coverage and Confidence Warning | Keep / revise | Conceptually consistent, but should stay advisor-review default and avoid becoming a full audit table | Keep compact coverage summary, review-required count/value, held-at-mark exposure, approved policy exposure, and practical caveats. Add possible manager slice later | Yes | `coverage_confidence_warning_mockup_v2.md` |
| Manager Role Summary | Redesign | v1 role field repeats manager label and does not explain why the manager is owned or whether mandate is expressed | Make manager-centered: intended role, portfolio share, actual exposure, material downside/key risk, and mandate-fit/leakage warning when supported. Consider single-manager detail later | Yes | `manager_role_summary_mockup_v2.md` |
| Portfolio Status | Revise lightly | Useful anchor, but it may imply full position transparency | Keep high-level. Distinguish represented positions, direct positions, manager-level holdings, fund/NAV holdings, and look-through availability when relevant | Yes | `portfolio_representation_status_mockup_v2.md` |
| Scenario Downside Summary | Keep / expand family | Simple current-portfolio downside table works, but scenario reports are a family | Keep current-portfolio downside report. Label deterministic/probabilistic status clearly. Define later scenario-versus-benchmark, scenario-by-manager, scenario-by-lens, current-versus-proposed, and probabilistic range variants | Yes | `current_portfolio_scenario_downside_mockup_v2.md` |

## 4. V2 Mockup Set

### A. Build-Now Mockups

These are the exact v2 mockups or v2 mockup specs the next implementation tranche should produce after Frank approves this spec.

| Mockup target | Output expectation | Why it belongs now |
| --- | --- | --- |
| Portfolio Status / Portfolio Representation Status | Generate v2 Markdown mockup from v2 view fixture | High-level portfolio anchor, revised for representation clarity |
| Aggregated Asset Allocation | Generate v2 Markdown mockup from v2 view fixture | Simple broad ownership view by asset type |
| Allocation by Manager | Generate v2 Markdown mockup from v2 view fixture if manager value data is already available | Companion to asset allocation; avoids overloading asset allocation |
| Coverage and Confidence Warning | Generate v2 Markdown mockup from v2 view fixture | Advisor trust/readiness warning that already has source outputs |
| Concentration by Asset Type | Generate v2 Markdown mockup from v2 view fixture | Corrects v1 mixed-category concentration |
| Concentration by Manager/Sleeve | Generate v2 Markdown mockup from v2 view fixture | Separate concentration view using one manager/sleeve grouping |
| Current Portfolio Scenario Downside | Generate v2 Markdown mockup from v2 view fixture | Existing two-scenario full-revaluation outputs support this honestly |
| Cash Flow Delivered | Generate v2 Markdown mockup from v2 view fixture using the synthetic cash-flow history prerequisite | Backward-looking advisor-value report showing what cash was generated, paid out, and retained/reinvested last period |
| Cash-Flow Support Outlook | Generate v2 Markdown mockup from v2 view fixture using the synthetic cash-flow need/projection prerequisites | Forward-looking support report showing stated need, projected generation, projected surplus/shortfall, funding policy, and caveat |
| Manager Role Summary | Generate v2 Markdown mockup using the approved synthetic manager mandate catalog | Needed to explain why managers are in the portfolio without role text that merely repeats manager names |
| Full Lens Exposure | Generate v2 Markdown mockup for the complete synthetic AI Adoption and Energy Security assignments | Complete synthetic lens definitions and one primary assignment per in-scope position now exist; show neutral and review buckets |

### B. Optional / Possible-Next Mockups

These are now possible from the prerequisite pack or existing mappings, but should wait for Frank to approve the exact v2 report shape.

| Mockup target | Gate / note |
| --- | --- |
| Manager by Lens Exposure | Possible next because complete lens assignments and manager mappings now exist; use one selected lens and one denominator |
| Scenario by Lens | Possible next after a separate tranche aggregates existing full-revaluation rows by the selected complete lens |
| Integrated Performance Attribution Summary | Possible next as a synthetic demo mockup using Synthetic Attribution Prerequisite Pack v1; keep real/client mode gated |
| Integrated Performance Attribution Detail | Possible next as an advisor-review synthetic demo mockup using the synthetic decomposition inputs; show timing as unavailable |
| Manager Attribution Summary | Possible next because manager returns, manager benchmark proxies, contribution effects, and tie-outs now exist synthetically |
| Lens-Based Performance Attribution | Possible next because AI Adoption and Energy Security lens-bucket proxy returns and weights now exist synthetically |
| Cash Flow by Manager/Sleeve | Still gated until reliable manager/sleeve cash-flow source data and period logic exist |

### C. Still-Gated Mockups

These should not be generated as data-backed v2 mockups until their gates are satisfied.

| Gated mockup | Gate |
| --- | --- |
| Scenario Versus Benchmark | Approved benchmark/proxy maps and benchmark scenario values or approved scenario proxy methodology; the attribution pack does not create benchmark scenario values |
| Timing Attribution | Clean two-state portfolio definition, trade/holding history, flow treatment, and approved methodology; the synthetic attribution pack marks timing unavailable |
| Probabilistic Scenario Range | Design-soon / prerequisite-soon; needs approved probabilistic/range analytics and, for comparison, approved benchmark/proxy range |
| Current Versus Proposed Portfolio | Explicit proposed allocation workflow/object and revaluation or exposure outputs for current and proposed states |

### D. Do-Not-Generate-Yet Mockups

- Client-facing Top Impacted Positions as a default standalone report.
- Detailed data-confidence report unless data quality is the meeting topic.
- Custom benchmark construction report.
- Timing attribution report unless timing is methodologically clean.
- Any report that invents benchmark maps, lens assignments, performance data, cash-flow inputs, proposed allocation data, or probabilistic analytics.

## 5. Mockup-By-Mockup Specification

### Portfolio Representation Status

- Mockup filename: `portfolio_representation_status_mockup_v2.md`
- Report display title: Portfolio Representation Status
- Master question family: Ownership / Exposure
- Exact report question: What is the current portfolio state, and how complete is our view?
- Audience options: Client briefing or advisor review.
- Summary/detail status: Summary.
- Representation level: Whole portfolio, with representation breakdown for direct, fund/NAV, manager-level, look-through, and review-required holdings.
- Denominator/category system: Portfolio value by representation status. Rows must be additive or clearly marked as non-additive status indicators.
- Recommended rendering form: Summary-first with a small table.
- One-sentence job: Anchor the conversation in portfolio scale and completeness without implying full look-through.
- Headline sentence pattern: "The portfolio is approximately {value}, with {represented_share} represented and {review_required_value} needing review before point-impact claims."
- Maximum headline metrics: 3.
- Maximum table rows: 5.
- Maximum caveats: 2.
- Required visible fields: Base portfolio value; represented/coverage status; direct/fund/NAV/manager-level/look-through or review-required split; one practical caveat.
- Forbidden visible fields: Raw position ids, manifest names, pricing function ids, source filenames, valuation traces, full coverage taxonomy.
- Advisor-only fields: Review-required count/value, held-at-mark amount, material opaque exposure detail.
- Internal-only fields: Market-state ids, coverage manifest paths, pricing assignment details, instrument ids.
- Source analytics/data needed: Portfolio snapshot, position catalog, valuation coverage outputs, coverage/confidence attribution.
- Missing prerequisite behavior: If representation basis is incomplete, show advisor-only representation-readiness status rather than a client-ready summary.
- Acceptable visible content example: "Illustrative design example only: The portfolio is approximately $44.9M; most value is represented for current summary purposes, while $5.8M needs review before strong point-impact claims."
- Anti-clutter rule: Do not combine representation status with asset allocation, manager allocation, or scenario impact in the same table.

### Aggregated Asset Allocation

- Mockup filename: `aggregated_asset_allocation_mockup_v2.md`
- Report display title: Aggregated Asset Allocation
- Master question family: Ownership / Exposure
- Exact report question: What does the portfolio own by broad asset type?
- Audience options: Client briefing and advisor review.
- Summary/detail status: Summary.
- Representation level: Portfolio holdings grouped by asset type.
- Denominator/category system: Broad asset-type taxonomy; rows sum to 100% of base portfolio value after Other grouping.
- Recommended rendering form: Table-first or small chart.
- One-sentence job: Make broad ownership legible.
- Headline sentence pattern: "{largest_bucket} is the largest broad allocation at {value} ({share})."
- Maximum headline metrics: 2.
- Maximum table rows: 5.
- Maximum caveats: 1.
- Required visible fields: Asset type, value, portfolio share, Other bucket if the long tail is grouped.
- Forbidden visible fields: Manager rows, review-required rows, held-at-mark rows, raw classifications, tiny long-tail buckets, source filenames.
- Advisor-only fields: Classification exceptions, incomplete look-through note, taxonomy review note.
- Internal-only fields: Classification rule ids, raw mapping evidence, source artifact names.
- Source analytics/data needed: Portfolio values and broad asset-type classification.
- Missing prerequisite behavior: If asset taxonomy is incomplete, show advisor-only taxonomy-readiness note or caveat the affected share.
- Acceptable visible content example: "Illustrative design example only: Public Equity, Fixed Income, Funds / ETFs, Private Equity, and Other sum to 100% of the portfolio."
- Anti-clutter rule: Do not add manager, confidence, or scenario columns to the asset allocation table.

### Allocation by Manager

- Mockup filename: `allocation_by_manager_mockup_v2.md`
- Report display title: Allocation by Manager
- Master question family: Ownership / Exposure
- Exact report question: How is the portfolio allocated across managers or sleeves?
- Audience options: Advisor review; client briefing when the conversation is manager-oriented.
- Summary/detail status: Summary.
- Representation level: Manager/sleeve.
- Denominator/category system: Additive share of portfolio by manager or sleeve.
- Recommended rendering form: Table-first.
- One-sentence job: Show manager allocation without mixing it into asset allocation.
- Headline sentence pattern: "{largest_manager} is the largest manager/sleeve at {share} of portfolio value."
- Maximum headline metrics: 2.
- Maximum table rows: 5.
- Maximum caveats: 1.
- Required visible fields: Manager/sleeve display name, portfolio value, portfolio share, optional role label if approved.
- Forbidden visible fields: Asset-type rows, scenario loss columns by default, raw manager ids, rankings that imply recommendation.
- Advisor-only fields: Full manager list, data confidence by manager, coverage issue by manager.
- Internal-only fields: Raw manager ids, source-account mappings, reconciliation detail.
- Source analytics/data needed: Manager/sleeve mapping and base portfolio values.
- Missing prerequisite behavior: If manager labels are not approved, keep this advisor-only or use neutral sleeve labels.
- Acceptable visible content example: "Illustrative design example only: Growth / AI Infrastructure represents 31.8% of portfolio value."
- Anti-clutter rule: Do not use this report to explain manager mandate fit; that belongs in Manager Role Summary.

### Coverage and Confidence Warning

- Mockup filename: `coverage_confidence_warning_mockup_v2.md`
- Report display title: Coverage and Confidence Warning
- Master question family: Risk / Downside
- Exact report question: Can the advisor trust the numbers enough to show them?
- Audience options: Advisor review default; client only if coverage materially affects interpretation.
- Summary/detail status: Summary with optional advisor detail later.
- Representation level: Coverage/confidence status buckets.
- Denominator/category system: Coverage status taxonomy, not asset allocation or concentration category.
- Recommended rendering form: Summary-first.
- One-sentence job: Warn when coverage changes how report numbers should be used.
- Headline sentence pattern: "{review_required_count} positions representing {review_required_value} need review before relying on point scenario impact."
- Maximum headline metrics: 3.
- Maximum table rows: 5.
- Maximum caveats: 2.
- Required visible fields: Review-required count/value, held-at-mark exposure, approved policy exposure, practical advisor meaning.
- Forbidden visible fields: Full coverage taxonomy, pricing function names, manifests, valuation traces, source paths.
- Advisor-only fields: Manager slice of coverage, material review queue, affected report families.
- Internal-only fields: Position-level coverage map, pricing-function assignments, raw rule traces.
- Source analytics/data needed: Coverage attribution, confidence attribution, valuation coverage outputs.
- Missing prerequisite behavior: If coverage outputs are missing, block client report and show internal/advisor readiness.
- Acceptable visible content example: "Illustrative design example only: Most positions are valued, but $5.8M requires review before strong point-impact claims."
- Anti-clutter rule: Do not repeat held-at-mark or review-required rows inside concentration tables.

### Concentration by Asset Type

- Mockup filename: `concentration_by_asset_type_mockup_v2.md`
- Report display title: Concentration by Asset Type
- Master question family: Risk / Downside
- Exact report question: Is the portfolio concentrated by broad asset type?
- Audience options: Advisor review; client briefing when concentration is material.
- Summary/detail status: Summary.
- Representation level: Asset-type bucket.
- Denominator/category system: Broad asset-type taxonomy; additive share of portfolio value.
- Recommended rendering form: Table-first.
- One-sentence job: Identify material concentration using one category system.
- Headline sentence pattern: "{largest_asset_type} is the largest concentration at {share} of portfolio value."
- Maximum headline metrics: 2.
- Maximum table rows: 5.
- Maximum caveats: 1.
- Required visible fields: Asset type, portfolio share, value, short why-it-matters note.
- Forbidden visible fields: Manager/sleeve rows, review-required status rows, held-at-mark rows, raw security names by default, multiple category systems.
- Advisor-only fields: Classification caveat, top contributors if explicitly approved, threshold notes.
- Internal-only fields: Raw classification evidence, source file paths, mapping rule ids.
- Source analytics/data needed: Portfolio values and asset-type classification.
- Missing prerequisite behavior: If asset-type classification is incomplete, show caveat or advisor readiness; do not force unclassified positions into a bucket.
- Acceptable visible content example: "Illustrative design example only: Public Equity is the largest broad asset-type concentration at 40.9%."
- Anti-clutter rule: One concentration report, one grouping system.

### Concentration by Manager/Sleeve

- Mockup filename: `concentration_by_manager_sleeve_mockup_v2.md`
- Report display title: Concentration by Manager/Sleeve
- Master question family: Risk / Downside
- Exact report question: Is the portfolio concentrated in one manager or sleeve?
- Audience options: Advisor review; client briefing when manager concentration is part of the conversation.
- Summary/detail status: Summary.
- Representation level: Manager/sleeve.
- Denominator/category system: Additive share of portfolio by manager or sleeve.
- Recommended rendering form: Table-first.
- One-sentence job: Identify manager/sleeve concentration without mixing in asset-type or coverage statuses.
- Headline sentence pattern: "{largest_manager_or_sleeve} is the largest manager/sleeve concentration at {share}."
- Maximum headline metrics: 2.
- Maximum table rows: 5.
- Maximum caveats: 1.
- Required visible fields: Manager/sleeve, portfolio share, value, brief interpretation.
- Forbidden visible fields: Asset-type buckets, coverage status rows, held-at-mark rows, raw manager ids, scenario impact by default.
- Advisor-only fields: Downside contribution by manager, overlap notes, coverage by manager.
- Internal-only fields: Raw manager ids, account mapping, position-level table.
- Source analytics/data needed: Manager/sleeve value aggregation, optional manager attribution for advisor notes.
- Missing prerequisite behavior: If manager/sleeve mapping is incomplete, show advisor-readiness note and affected share.
- Acceptable visible content example: "Illustrative design example only: The largest manager/sleeve accounts for roughly one-third of base value."
- Anti-clutter rule: Do not turn this into Manager Role Summary; role and mandate fit are separate.

### Current Portfolio Scenario Downside

- Mockup filename: `current_portfolio_scenario_downside_mockup_v2.md`
- Report display title: Current Portfolio Scenario Downside
- Master question family: Risk / Downside
- Exact report question: How does the current portfolio revalue under selected approved downside scenarios?
- Audience options: Advisor review; client briefing for risk-focused meetings.
- Summary/detail status: Summary.
- Representation level: Whole portfolio scenario result.
- Denominator/category system: Approved deterministic scenarios; each row shows whole-portfolio impact.
- Recommended rendering form: Table-first, visual-friendly.
- One-sentence job: Show current-portfolio downside without implying probability.
- Headline sentence pattern: "{scenario_name} is the larger deterministic downside case, reducing portfolio value by {impact} ({impact_percent})."
- Maximum headline metrics: 3.
- Maximum table rows: 4.
- Maximum caveats: 2.
- Required visible fields: Scenario display name, portfolio impact, portfolio change percent, value after scenario, deterministic status.
- Forbidden visible fields: Probability, forecast language, raw market-state ids, full position impact table, scenario-construction machinery.
- Advisor-only fields: Top manager contributors, coverage mix, confidence mix.
- Internal-only fields: Scenario market-state ids, bundle manifest paths, valuation traces, position comparisons.
- Source analytics/data needed: Full revaluation portfolio summaries and cross-scenario revaluation summary.
- Missing prerequisite behavior: If fewer than two supported scenarios exist, show one-scenario summary and caveat scope; do not call it resilience.
- Acceptable visible content example: "Illustrative design example only: AI / Chip Selloff and Rate Shock appear as deterministic stress rows, not probability-weighted forecasts."
- Anti-clutter rule: Do not include manager, lens, or benchmark comparisons in this base report.

### Cash Flow Delivered

- Mockup filename: `cash_flow_delivered_mockup_v2.md`
- Report display title: Cash Flow Delivered
- Master question family: Performance / Plan
- Exact report question: What cash did the portfolio actually generate and make available during the last period?
- Audience options: Client briefing and advisor review when the meeting includes spending, distributions, or advisor value delivered.
- Summary/detail status: Summary.
- Representation level: Whole portfolio trailing-period cash flow.
- Denominator/category system: Cash generated and paid out over the same prior period.
- Recommended rendering form: Summary-first with one compact table.
- One-sentence job: Show prior-period cash generation and payouts without implying next-period support.
- Maximum headline metrics: 3.
- Maximum table rows: 3, with one preferred summary row when the period is clear.
- Maximum caveats: 1.
- Required visible fields: Period label, cash generated last period, cash paid out last period, net retained/reinvested or surplus if supported, one practical caveat.
- Forbidden visible fields: Next-period projection as the main evidence, manager/sleeve cash-flow claims without reliable source detail, raw transaction/source labels.
- Advisor-only fields: Source coverage note, manager/sleeve readiness note.
- Missing prerequisite behavior: If prior-period generated/paid-out cash is absent, keep this report unavailable or advisor-readiness only.
- Anti-clutter rule: Do not combine this with the forward-looking support outlook.

### Cash-Flow Support Outlook

- Mockup filename: `cash_flow_support_outlook_mockup_v2.md`
- Report display title: Cash-Flow Support Outlook
- Master question family: Performance / Plan
- Exact report question: Will projected cash generation support the stated annual or quarterly cash need?
- Audience options: Client briefing and advisor review when the stated cash need is explicit.
- Summary/detail status: Summary.
- Representation level: Whole portfolio forward cash-flow support outlook.
- Denominator/category system: Stated cash need versus projected cash generation.
- Recommended rendering form: Summary-first with a compact support table.
- One-sentence job: Show whether projected cash generation covers the stated need without relying on cash balances alone.
- Maximum headline metrics: 3.
- Maximum table rows: 5.
- Maximum caveats: 2.
- Required visible fields: Stated annual or quarterly need, projected next-period generation, projected surplus/shortfall, confidence/caveat, funding policy note.
- Forbidden visible fields: Prior-period generated/paid-out values as core outlook rows, production forecast language, manager/sleeve support claims without reliable source detail.
- Advisor-only fields: Projection basis note, manager/sleeve readiness note.
- Missing prerequisite behavior: If stated need or projected generation is absent, keep support outlook gated rather than inferring support from cash balances.
- Anti-clutter rule: Keep the backward-looking delivered report separate.

### Manager Role Summary

- Mockup filename: `manager_role_summary_mockup_v2.md`
- Report display title: Manager Role Summary
- Master question family: Ownership / Exposure
- Exact report question: Why is each manager in the portfolio, and is the intended role being expressed?
- Audience options: Advisor review default; client briefing when manager explanation is needed.
- Summary/detail status: Summary; Single-Manager Detail is a separate future shape.
- Representation level: Manager/sleeve.
- Denominator/category system: Manager/sleeve share of portfolio with approved role/mandate labels.
- Recommended rendering form: Summary/table-first.
- One-sentence job: Explain manager purpose, not just manager size.
- Headline sentence pattern: "Each major manager should have a clear role; {manager_name} is the largest current manager/sleeve at {share}."
- Maximum headline metrics: 3.
- Maximum table rows: 5.
- Maximum caveats: 2.
- Required visible fields: Manager/sleeve, intended role or mandate, portfolio share, actual exposure or key risk, mandate-fit/leakage note if supported.
- Forbidden visible fields: Role values that merely repeat manager names, raw manager ids, ranking tone, all metric columns, recommendation language.
- Advisor-only fields: Mandate leakage diagnostic, selected-lens exposure, scenario downside by manager, missing mandate flags.
- Internal-only fields: Raw mandate rules, classification evidence, source-account mappings, rule ids.
- Source analytics/data needed: Manager/sleeve values, approved role/mandate language, optional manager scenario attribution, optional selected-lens exposure.
- Missing prerequisite behavior: If approved mandate language is absent, generate advisor-review mockup with a clear mandate-language caveat or defer client mode.
- Acceptable visible content example: "Illustrative design example only: Growth manager role: long-term growth engine; actual exposure: high growth/AI sensitivity; note: review whether downside concentration fits mandate."
- Anti-clutter rule: Do not allow the Role column to duplicate the Manager column.

### Full Lens Exposure

- Mockup filename: `full_lens_exposure_mockup_v2.md` only if complete assignments exist; otherwise `full_lens_exposure_design_spec_v2.md`.
- Report display title: Full Lens Exposure
- Master question family: Ownership / Exposure
- Exact report question: How does the whole portfolio map into every bucket of one selected lens?
- Audience options: Advisor review; client briefing only when lens assignments and caveats are approved.
- Summary/detail status: Summary with optional detail later.
- Representation level: Lens bucket.
- Denominator/category system: One selected complete lens; allocation/concentration buckets sum to 100%, including neutral/review buckets.
- Recommended rendering form: Visual-friendly table or bar/stacked view.
- One-sentence job: Show the entire portfolio through one approved classification worldview.
- Headline sentence pattern: "Under the {lens_name} lens, {largest_bucket} is the largest bucket at {share}, with {review_bucket_share} requiring review."
- Maximum headline metrics: 3.
- Maximum table rows: All buckets in the selected lens, unless the lens has more than 8 buckets and Frank approves grouped display; do not hide review/neutral buckets.
- Maximum caveats: 2.
- Required visible fields: Lens name, all bucket labels, bucket share/value, neutral/review bucket, assignment confidence caveat.
- Forbidden visible fields: Partial bucket-only view, top-buckets-only table, raw position assignment ids, raw LLM rationale, mapping rule internals.
- Advisor-only fields: Unassigned positions, assignment confidence detail, affected managers.
- Internal-only fields: Evidence packets, LLM responses, rule traces, raw source descriptions.
- Source analytics/data needed: Published position-to-lens assignments for every in-scope position, lens catalog, portfolio values.
- Missing prerequisite behavior: For the synthetic AI Adoption and Energy Security lenses, use the prerequisite pack. For any future lens without complete assignments, produce design-only spec/readiness language, not fake bucket totals.
- Acceptable visible content example: "Illustrative design example only: AI Adoption lens rows would include all approved buckets, including Neutral / Low Direct AI Exposure and Unclassified / Review Required."
- Anti-clutter rule: Do not show only the largest lens bucket; a lens is a complete category system.

## 6. Visual-First Mockup Specifications

These are v2 visual mockup concepts. Do not implement visuals in this tranche.

### A. Scenario Range Number Line

- Used for: Probabilistic Scenario Range.
- Question answered: What range of outcomes is plausible under this scenario family and horizon?
- Rendering: Chart-first number line.
- Visible content: Portfolio range, benchmark range if approved, expected or central impact, horizon, one caveat.
- Gate: Approved probabilistic analytics and benchmark/proxy maps when a benchmark is shown.
- Forbidden: Probability ranges invented from deterministic scenario points.

### B. Portfolio vs Benchmark Range Comparison

- Used for: Portfolio vs Benchmark Scenario Range.
- Question answered: Does portfolio construction improve resilience versus the approved benchmark/proxy?
- Rendering: Two aligned number lines or compact range bars.
- Visible content: Portfolio range, benchmark/proxy range, central estimates, horizon, short interpretation.
- Gate: Approved benchmark/proxy map and range analytics for both portfolio and benchmark/proxy.
- Forbidden: Freeform benchmark setup or benchmark comparison without approved map.

### C. Performance Attribution Waterfall

- Used for: Integrated Performance Attribution Summary or Detail.
- Question answered: What decisions explain value added or lost versus benchmark?
- Rendering: Waterfall first, with optional supporting table.
- Visible content: Strategy/lens-bucket selection, strategy/lens-bucket sizing, asset selection, asset sizing, and timing only if clean.
- Gate: Benchmark returns, portfolio returns, weights, holdings, flows, benchmark map, attribution method, and timing gate if timing appears.
- Forbidden: Residual/noise labeled as timing.

### D. Full Lens Exposure Bar / Stacked View

- Used for: Full Lens Exposure.
- Question answered: How does the whole portfolio distribute across every bucket of one lens?
- Rendering: Bar or stacked view backed by a table.
- Visible content: All buckets in the selected lens, including neutral/review buckets, summing to 100%.
- Gate: Complete published position-to-lens assignments.
- Forbidden: Top-bucket-only lens report.

### E. Manager-by-Lens Grid

- Used for: Manager by Lens Exposure.
- Question answered: How do managers compare under one selected lens?
- Rendering: Compact grid or heatmap.
- Visible content: Managers as rows, lens buckets as columns, same lens and denominator across all rows.
- Gate: Complete lens assignments and manager mapping.
- Forbidden: Comparing managers under different lenses or mixed denominators.

## 7. Lens And Benchmark Mockup Implications

- A lens is a complete classification system.
- A lens exposure report should show all buckets in the selected lens, not only the largest bucket.
- Lens bucket totals should sum to 100% for allocation/concentration views.
- Manager-by-lens views should show each manager under the same selected lens.
- Lens reports should include neutral and review/unclassified buckets.
- Benchmarks/proxies should come from approved benchmark maps.
- V2 should not create freeform custom benchmark setup.
- V2 should not fabricate benchmark comparisons where benchmark data is missing.
- Lens-bucket benchmarks belong in future attribution and benchmark-relative reports only after maps are approved.

## 8. Integrated Performance Attribution Mockup Implications

### A. Summary Shape

The summary report should explain in plain language whether value was added versus benchmark and where. It should likely be visual-first, using a small waterfall or contribution bridge.

Summary should be suitable for many client conversations when data quality is high enough. It should show only the few components that change the conversation.

Required future visible content:

- benchmark display name;
- selected period;
- total portfolio result versus benchmark;
- largest positive and negative decision effects;
- short caveat on benchmark fit or data completeness.

For synthetic demo mockups, the benchmark, period returns, weights/flows, and contribution inputs should come from Synthetic Attribution Prerequisite Pack v1 rather than being invented inside a report generator. Real/client attribution remains gated until production return, benchmark, holding, flow, and methodology inputs exist.

### B. Detail Shape

The detail report should be advisor-review first. It should support whole-portfolio and manager-by-manager modes.

Detail should show:

- global benchmark to actual portfolio bridge;
- strategy or lens-bucket selection;
- strategy or lens-bucket sizing;
- strategy timing only if clean;
- asset selection;
- asset sizing;
- asset timing only if clean;
- residual/unexplained bucket when needed, without relabeling it as timing.

Synthetic demo attribution mockups may now be generated from the attribution prerequisite pack, but they should keep timing unavailable unless a later tranche defines two clean portfolio states and the required trade/flow history. Do not generate production/client attribution reports until historical return, benchmark, position history, holding/flow, and approved benchmark/proxy prerequisites exist.

## 9. Data And Prerequisite Gating

| Gated report | Missing data / prerequisite | Required behavior |
| --- | --- | --- |
| Cash Flow Delivered | For synthetic demo: prerequisite pack now supplies period, cash generated, cash paid out, retained/reinvested cash, and confidence caveat. For real/client mode: real cash-flow sources remain absent | Generate only synthetic-demo prior-period mockup content from the pack; keep real/client cash-flow readiness gated |
| Cash-Flow Support Outlook | For synthetic demo: prerequisite pack now supplies stated annual cash need, projected generation, funding policy, surplus/shortfall, and confidence caveat. For real/client mode: real cash-flow sources and plan data remain absent | Generate only synthetic-demo outlook content from the pack; keep real/client cash-flow readiness gated |
| Cash Flow by Manager/Sleeve | Reliable cash-flow history/projection by manager/sleeve | Gate until source data and period logic exist |
| Scenario Versus Benchmark | Approved benchmark/proxy map and benchmark scenario value or proxy methodology | Defer benchmark comparison |
| Manager by Lens Exposure | Published complete position-to-lens assignments plus manager mapping | Possible next for synthetic AI Adoption and Energy Security; defer for any lens without complete assignments |
| Integrated Performance Attribution Summary | For synthetic demo: Synthetic Attribution Prerequisite Pack v1 supplies benchmark, returns, weights/flows, decomposition inputs, and caveats. For real/client mode: production return, benchmark, holding, flow, and methodology inputs remain absent | Eligible for future synthetic demo mockup; keep real/client attribution gated |
| Integrated Performance Attribution Detail | For synthetic demo: decomposition inputs and manager rows exist, with timing unavailable. For real/client mode: detailed production holdings/trades and reconciliation policy remain absent | Eligible for future advisor-review synthetic demo mockup; omit timing unless cleanly defined |
| Timing Attribution | Two clearly specified portfolio states, trade/holding history, flow treatment, clean timing methodology | Omit timing or mark unavailable |
| Probabilistic Scenario Range | Covariance/probabilistic scenario engine outputs, range methodology, horizon, validation, benchmark range if compared | Do not create ranges from deterministic scenarios |
| Full Lens Exposure | Complete lens definition and published position-to-lens assignments for all in-scope positions | Generate synthetic AI Adoption and Energy Security mockups from the pack; produce design-only spec/readiness if missing for another lens |
| Current Versus Proposed Portfolio | Proposed allocation data/workflow and analytics for current/proposed states | Defer current-versus-proposed report |

Missing data should produce setup/readiness status for advisor/internal use, not a fake client-facing report.

## 10. Information Budget For V2 Mockups

Default v2 budget:

- Max 1 headline sentence.
- Max 3 headline metrics.
- Max 5 visible table rows.
- Max 2 caveats.
- Max 1 advisor note.
- No raw ids.
- No source filenames.
- No manifest/schema/artifact/debug terminology.
- No "more rows here" placeholders.
- No hidden expansion placeholders.

Report-specific exceptions:

- Full Lens Exposure may show all buckets in the selected lens, even if that exceeds 5 rows, because showing all buckets is part of the report's integrity. If the lens has many buckets, Frank should approve grouped display rules.
- Coverage and Confidence Warning may use up to 5 rows for coverage statuses, but client-facing versions should usually be shorter.
- Advisor-detail variants may use more rows only when the variant is explicitly named as detail or review.

## 11. V2 Mockup Review Checklist

Frank should be able to read each v2 mockup and:

- judge whether the report answers one clear question;
- see all visible content that would appear;
- confirm no hidden expansion is implied;
- confirm the report uses one denominator/category system;
- confirm representation level is clear;
- identify whether the report is client-ready, advisor-review, or internal-only;
- confirm missing data is gated rather than invented;
- confirm visual-first concepts have clear denominators/ranges;
- mark the report keep, revise, or kill.

## 12. Next Implementation Prompt Outline

The next implementation tranche should be created only after Frank approves or revises this spec.

It should:

- update/generate v2 Markdown mockups only after approval;
- generate mockups from view fixtures, not hand-written standalone Markdown;
- enforce information budgets with tests;
- avoid advisor UI wiring;
- avoid generated-report wiring;
- use the synthetic report prerequisite pack for Cash Flow Delivered, Cash-Flow Support Outlook, Manager Role Summary, and Full Lens Exposure rather than inventing report values inside mockups;
- use Synthetic Attribution Prerequisite Pack v1 for future Integrated Performance Attribution Summary/Detail, Manager Attribution Summary, and Lens-Based Performance Attribution mockups rather than inventing benchmark, return, weight, or decomposition values inside mockups;
- avoid generating still-gated reports as if data exists;
- preserve v1 artifacts if useful for comparison, or write v2 artifacts to a separate path;
- keep synthetic/local-only boundaries;
- avoid new analytics outputs unless separately authorized.
