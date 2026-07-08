# Report Data And Analytics Requirements v1

## Purpose

This document maps the redesigned report families to the data and analytics they need. It is architecture/design documentation only.

It does not implement code, generate analytics outputs, change UI, add endpoints, change Docker/deployment configuration, use live data, use real client data, or add dependencies.

The rule is direct:

```text
If required data or analytics do not exist, the report should be unavailable, advisor-readiness only, or explicitly caveated. It should not be fabricated.
```

## Current Local Synthetic Availability

Available now in the repo:

- synthetic portfolio and position universe;
- manager, account, sleeve, instrument, and broad classification fixture data;
- synthetic market states and two supported full-revaluation scenarios: `ai_chip_selloff` and `rate_shock`;
- position valuation results, position value comparisons, portfolio scenario summaries, coverage manifests, and scenario index artifacts;
- revaluation attribution by manager, account, sleeve, coverage, confidence, gross theme, and cross-scenario summary;
- thesis-bucket attribution readiness output, not real thesis-bucket attribution;
- Synthetic Report Prerequisite Pack v1 with local-only cash-flow support inputs, approved synthetic manager mandate catalog, and complete synthetic AI Adoption / Energy Security lens assignments;
- lean local product-review mockups for Portfolio Status, Aggregated Asset Allocation, Manager Role Summary, Concentration Review, Scenario Downside Summary, Coverage and Confidence Warning, and Cash-Flow Support Readiness;
- v2 local product-review mockups for Cash Flow Delivered and Cash-Flow Support Outlook, generated from the synthetic prerequisite pack and kept separate from Advisor Preview/Populate/Present wiring;
- Synthetic Attribution Prerequisite Pack v1 with local-only whole-portfolio benchmark, AI Adoption / Energy Security lens-bucket proxy map, synthetic period returns, weights/flows, decomposition inputs, and manager attribution prerequisites;
- Attribution Methodology and Calculation Audit v1 with a read-only local audit utility that classifies current synthetic attribution fields as arithmetic, supplied synthetic input, supplied formula allocation, or residual reconciler;
- Synthetic Attribution Calculation Inputs v1 with selected AI Adoption lens policy, equal-weight and actual-weight theme benchmark weights, theme benchmark return inputs, compact grouped per-theme asset inputs, explicit manager benchmark-basis metadata, residual policy, and timing-unavailable readiness;
- Calculated Synthetic Attribution Engine v1 with whole-portfolio calculated attribution, theme benchmark detail, theme asset detail, manager calculated attribution, quality/readiness summary, tie-outs, residual policy, and timing-unavailable gating under `data/simulation/attribution_calculated/synthetic_attribution_engine_v1/`;
- Synthetic Policy Allocation / Mandate Benchmark Pack v1 with explicit advisor/family policy targets, current manager allocation snapshot, drift/tolerance rows, imputed-current baseline, manager mandate benchmark catalog, policy-level attribution input scaffold, and equal-weight diagnostic classification under `data/simulation/policy_mandate_prerequisites/synthetic_policy_mandate_pack_v1/`;
- local `policy_allocation_v1` report inputs/views/mockups for Policy Allocation Review, Policy Allocation Drift Summary, Imputed Current Allocation Baseline, and Manager Mandate Benchmark Basis under `data/simulation/report_element_inputs/policy_allocation_v1/`, `data/simulation/report_element_views/policy_allocation_v1/`, and `docs/product/report_mockups/policy_allocation_v1/`;
- regenerated local `attribution_v1` report inputs/views/mockups for Integrated Performance Attribution Summary/Detail, Manager Attribution Summary, and Lens-Based Performance Attribution - AI Adoption that consume calculated attribution outputs;
- analytic pack choices and committed analytic-derived fragments for the current local demo path.

Missing or deferred:

- real cash-flow need, liability schedule, account cash history, and production projection basis;
- reliable manager/sleeve cash-flow source data sufficient for a Cash Flow by Manager/Sleeve report;
- production-approved benchmark/proxy maps beyond the synthetic attribution prerequisite pack;
- production or scenario-comparison lens-bucket benchmark maps beyond the synthetic attribution prerequisite pack;
- published position-thesis assignments beyond the synthetic AI Adoption and Energy Security prerequisite pack;
- production historical returns and performance calculation inputs;
- calculated Energy Security attribution inputs/outputs and regenerated Energy Security attribution mockup;
- trade/holding history sufficient for attribution timing;
- proposed allocation objects;
- probabilistic/range analytics;
- production data, live market data, live Plaid data, and real client data.

## Readiness Gates

| Gate | Required before report can claim | Missing-input behavior |
| --- | --- | --- |
| Representation gate | The row level is known: direct security, fund/NAV, manager-level, look-through, lens bucket, benchmark, or proposed allocation | Label as representation incomplete or keep advisor-only |
| Denominator gate | All rows in an additive table share one denominator/category system | Split the report or show as non-additive diagnostic |
| Lens gate | Each in-scope position has an approved assignment, neutral bucket, or review bucket for the selected lens | Show readiness/review status, not lens exposure claims |
| Benchmark gate | Benchmark or proxy map is approved for the report scope | Synthetic Attribution Prerequisite Pack v1 satisfies this only for local synthetic `attribution_v1` mockups; otherwise defer benchmark-relative reports |
| Cash need gate | For delivered cash: period, generated cash, paid-out cash, and retained/reinvested cash. For support outlook: stated need, period, funding policy, projected generation, and projection basis | Generate only local synthetic delivered/outlook summaries when these inputs exist; keep real/client support readiness gated |
| Performance history gate | Returns, holdings, flows, and benchmark history are available for the selected period | Synthetic Attribution Prerequisite Pack v1 supplies local synthetic attribution inputs; defer real/client performance attribution |
| Timing gate | Two clearly specified portfolio states, flow treatment, and enough trade/flow history exist | Omit timing; `Residual / unexplained` may include unmeasured timing, data, flow, or reconciliation effects, but must not be labeled timing |
| Probabilistic gate | Approved range methodology and inputs exist | Do not create ranges from deterministic scenarios |
| Proposal gate | Current and proposed portfolio states are both explicit | Defer current-versus-proposed reports |

## Requirements Matrix

| Report area | Portfolio data | Instrument/position data | Manager/sleeve data | Lens assignments | Benchmark/proxy maps | Historical returns | Trade/holding history | Cash-flow data | Scenario/revaluation outputs | Probabilistic analytics | Available now | Missing/deferred | Cannot fabricate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Portfolio Representation Status | Required | Required with representation type and coverage | Useful | Optional | Not required | Not required | Not required | Optional | Coverage/confidence summary useful | Not required | Synthetic portfolio, position catalog, coverage outputs | Better look-through/representation basis labels | Completeness of unknown look-through |
| Aggregated Asset Allocation | Required | Required with asset type | Optional | Not required unless asset class is modeled as lens | Not required | Not required | Not required | Not required | Not required | Not required | Synthetic broad asset classifications and values | Revised taxonomy approval | Asset taxonomy confidence beyond fixture |
| Allocation by Manager | Required | Position values by manager | Required | Optional | Not required | Not required | Not required | Not required | Optional scenario context | Not required | Manager/sleeve value aggregation exists | Product spec and manager role language | Manager mandate claims without data |
| Full Lens Exposure | Required | Required for every in-scope position | Optional manager rollup | Required | Not required unless comparing | Not required | Not required | Not required | Optional for impact lens | Optional later | Complete synthetic AI Adoption and Energy Security assignments now exist | Product-grade assignments for other lenses and report-view generation | Bucket totals for unassigned positions |
| Manager by Lens Exposure | Required | Required | Required | Required | Not required | Not required | Not required | Not required | Optional | Optional later | Manager mappings and complete synthetic AI Adoption / Energy Security assignments exist | Approved report shape and any non-synthetic lens assignments | Cross-manager lens claims without same lens |
| Manager Role Summary | Required | Useful | Required with mandate/role | Optional for role expression | Optional manager benchmark later | Optional | Optional | Optional | Scenario downside by manager available | Not required | Manager value, scenario attribution, and approved synthetic mandate catalog | Real/client mandate approval beyond synthetic demo | Why a manager is owned when mandate absent |
| Integrated Performance Attribution | Required | Required over period | Required for manager mode | Required for lens mode | Required | Required | Required | Required for flow-adjusted returns | Optional scenario overlay | Not required | Synthetic attribution prerequisite pack, local calculated `attribution_v1` report inputs/views/mockups, methodology audit, Synthetic Attribution Calculation Inputs v1, and Calculated Synthetic Attribution Engine v1 now exist for AI Adoption | Real/client benchmark maps, return history, holdings/trades, flows, approved production methodology, calculated Energy Security attribution outputs, and production timing inputs | Value-add, timing, or benchmark-relative claims beyond the local synthetic prerequisite/input/calculated-output packs and audit |
| Cash Flow Delivered | Required | Required where income/distributions matter | Optional manager rollup | Not required | Not required | Optional | Useful | Required: period, generated cash, paid-out cash, retained/reinvested cash | Optional stress overlay | Optional later | Synthetic prerequisite pack supplies whole-portfolio trailing-period demo inputs | Real/client cash-flow sources and reliable source history | Real delivered-cash claims |
| Cash-Flow Support Outlook | Required | Required where income/distributions matter | Optional manager rollup | Not required | Not required | Optional | Useful | Required: stated need, projected generation, surplus/shortfall, funding policy | Optional stress overlay | Optional later | Synthetic prerequisite pack supplies whole-portfolio support outlook inputs | Real/client cash-flow sources, liability schedule, and production projection basis | Real support/sufficiency conclusion |
| Cash Flow by Manager/Sleeve | Required | Required income/distribution records | Required | Not required | Optional | Optional | Useful | Required | Optional | Optional later | Not report-ready | Reliable cash-flow source data | Manager cash generation claims |
| Current Portfolio Scenario Downside | Required | Required with valuation coverage | Optional for contributor detail | Optional for lens variant | Not required | Not required | Not required | Not required | Required | Not required | Two full-revaluation scenarios and summaries | More scenarios, product caveat policy | Probability or forecast claim |
| Scenario by Manager | Required | Required | Required | Optional | Not required | Not required | Not required | Not required | Required manager attribution | Not required | Manager attribution for two scenarios | Client/advisor display policy | Manager causality beyond attribution |
| Scenario by Lens | Required | Required | Optional | Required | Optional | Not required | Not required | Not required | Required plus lens assignments | Optional later | Complete synthetic AI Adoption assignments can pair with AI / Chip Selloff in a future aggregation tranche | Report-view generation and any other scenario/lens pairs | Thesis-bucket impacts without assignments |
| Scenario Versus Benchmark | Required | Required | Optional | Optional | Required | Optional | Optional | Not required | Required for portfolio and benchmark/proxy | Optional | Portfolio scenario output exists | Benchmark/proxy scenario mapping | Benchmark comparison |
| Probabilistic Scenario Range | Required | Required depending on model | Optional | Optional | Optional/required for benchmark range | Possibly required | Possibly required | Optional | Deterministic scenarios may seed methodology but are not enough | Required | Not available | Approved range model and validation | Percentile range or probability |
| Coverage and Confidence Warning | Required | Required with valuation status | Useful for aggregation | Optional | Not required | Not required | Not required | Optional | Coverage/confidence attribution required | Not required | Coverage/confidence outputs exist | Client-facing threshold policy | Assurance that low-confidence values are reliable |
| Opaque / Review-Required Exposure | Required | Required with review flags and marks | Useful | Optional | Not required | Optional | Optional | Optional | Coverage/review outputs useful | Not required | Review-required and held-at-mark outputs exist | Review queue product spec | Resolved exposure without review |
| Concentration by Consistent Category | Required | Required for chosen category | Optional if manager category | Required if selected lens/theme | Not required | Not required | Not required | Not required | Optional for downside concentration | Optional later | Asset, manager, theme, coverage aggregations exist | One-category product spec | Mixed-category concentration table |
| Portfolio vs Benchmark Scenario Range | Required | Required | Optional | Optional | Required | Possibly required | Possibly required | Optional | Required scenario/range data | Required for range version | Not available | Benchmark map and range analytics | Benchmark range |
| Current vs Proposed Portfolio | Required for current and proposed | Required for current/proposed holdings | Required if manager change | Optional | Optional | Optional | Required for transition/timing | Optional | Revaluation of both states required | Optional | Not available | Proposed allocation object | Improvement claim without proposed state |
| Proposed Allocation Change | Required | Required for proposed rows | Required if manager change | Optional | Optional | Optional | Optional | Optional | Optional | Optional | Not available | Proposal workflow/object | Rationale for nonexistent proposal |
| Upside / Downside Tradeoff | Required | Required | Optional | Required if thesis/lens framing | Optional | Optional | Optional | Optional | Required upside/downside scenario set | Optional | Not available | Approved upside scenarios and lens assignments | Tradeoff score without model |
| Manager Rebalancing Rationale | Required current/proposed | Required | Required | Optional | Optional manager benchmarks | Useful | Useful | Optional | Optional scenario impact | Optional | Not available | Proposed manager changes and approval state | Recommendation/rationale without proposal |
| Thesis / Lens Positioning | Required | Required | Optional manager rollup | Required | Optional | Optional | Optional | Optional | Optional scenario overlay | Optional later | Thesis readiness only | Published assignments for chosen lens | Client thesis exposure claims |

## Report-Specific Notes

### Cash Flow Delivered And Support Outlook

Minimum Cash Flow Delivered evidence:

- prior-period label;
- cash generated last period;
- cash paid out last period;
- retained/reinvested cash or surplus if supported;
- one confidence caveat.

Minimum Cash-Flow Support Outlook evidence:

- stated annual or quarterly cash need;
- projected cash generation for the next period or periods;
- surplus/shortfall versus need;
- funding policy;
- one confidence caveat.

The older Cash-Flow Support Readiness note does not satisfy either report. Synthetic Report Prerequisite Pack v1 now satisfies the minimum fields for local-only whole-portfolio demo delivered/outlook summaries, but real/client cash-flow support remains gated until real cash-flow sources, plan data, and projection policy exist. Do not infer support from cash balances alone.

### Integrated Performance Attribution

Minimum report evidence:

- approved benchmark or proxy map;
- selected period;
- portfolio and benchmark returns;
- holdings, weights, and cash-flow treatment for the period;
- manager/sleeve mapping when manager mode is selected;
- lens assignments and theme-bucket benchmark maps when lens mode is selected;
- residual policy;
- timing gate outcome.

For local synthetic demo work, Synthetic Attribution Prerequisite Pack v1 supplies the benchmark, return, weight/flow, decomposition, theme-benchmark detail, lens-bucket proxy, manager, residual, and timing-unavailable inputs used by attribution work. Attribution Methodology and Calculation Audit v1 documents field provenance and earlier fixed-share mockup gaps. Synthetic Attribution Calculation Inputs v1 adds the lower-level selected-lens policy, theme benchmark weight states, theme benchmark returns, grouped asset inputs, manager benchmark-basis metadata, and residual policy. Calculated Synthetic Attribution Engine v1 turns those inputs into calculated whole-portfolio, theme benchmark, theme asset, manager, and quality output artifacts. The local `attribution_v1` product-review mockups now consume those calculated outputs for Integrated Performance Attribution Summary/Detail, Manager Attribution Summary, and Lens-Based Performance Attribution - AI Adoption. Energy Security attribution remains gated for calculated attribution until calculated outputs exist for that lens. For real/client or production reporting, if benchmark or history inputs are missing, do not show attribution. If timing is not cleanly measurable, omit timing.

Attribution Calculation Explanation Polish v1 adds a presentation rule for calculated local attribution: distinguish Active Return, the return gap versus a theme benchmark, from Total Attribution Effect, the calculated attribution effect after benchmark selection/sizing and asset effects. Manager summaries should identify manager benchmark basis and separate Largest Driver, Other Measured Effects, and Residual / unexplained. Residual may include unmeasured timing, data, flow, rounding, or reconciliation effects; timing still remains unavailable unless clean timing inputs and an approved method exist.

Attribution Effect Basis Polish v1 adds the unit-basis rule for calculated local attribution: return columns are shown on a 100% theme-bucket basis, while effect columns are measured in percentage points of total portfolio return. Detail reports should show Policy Weight and Actual Weight where theme weighting effects are visible, use effect terminology rather than contribution terminology, and explain that Active Return is not Total Effect. A strong but underweighted theme can have positive bucket-level active return and negative Total Effect.

Attribution Policy / Mandate Benchmark Design v1 adds the responsibility-layer rule for future attribution data requirements: advisor/family policy allocation, actual manager/sleeve allocation, and within-manager implementation require separate benchmark and allocation inputs. Equal-weight lens attribution is diagnostic unless selected as policy, so future production-oriented policy attribution needs explicit or imputed policy allocation artifacts before it can fairly evaluate advisor/family allocation decisions.

Synthetic Policy Allocation / Mandate Benchmark Pack v1 now satisfies those local synthetic prerequisite artifacts. Policy Allocation Review Mockups v1 uses the explicit policy targets, actual manager allocation snapshot, and drift rows for local product review. Policy-Level Attribution has input scaffolding but still needs a calculated engine before it should be treated as a calculated report. Manager mandate attribution can now source explicit benchmark-basis rows, and equal-weight attribution remains diagnostic unless a policy artifact says otherwise.

Policy Allocation Review Mockups v1 now consumes those prerequisite artifacts for local product review. The generated Policy Allocation Review shows target weight, actual weight, drift, tolerance, and status for all six managers. Policy Allocation Drift Summary shows only review/material watch-list rows. Imputed Current Allocation Baseline is a setup/readiness note that accepts current weights as the baseline and suppresses drift attribution. Manager Mandate Benchmark Basis shows the benchmark basis for all six current managers. Policy-Level Attribution remains calculation-engine gated.

### Probabilistic Scenario Range

Minimum report evidence:

- approved scenario family or stochastic model;
- horizon;
- central estimate or expected impact definition;
- range definition such as 5th-95th percentile;
- validation/caveat language;
- benchmark/proxy range if comparison is shown.

Deterministic `ai_chip_selloff` and `rate_shock` scenario points do not by themselves create a probabilistic range.

### Lens And Benchmark Reports

Minimum report evidence:

- approved lens definition;
- one primary bucket, neutral bucket, or review bucket for every in-scope position when the lens is additive;
- confidence/review treatment;
- approved benchmark/proxy map for any relative claim;
- representation basis label.

Lens reports should show unavailable/review buckets rather than silently forcing assignments.

## Implementation Implications

- Revised mockups should declare report family id, audience tier, representation level, denominator, and data readiness.
- Tests for future report views should block mixed category systems in additive tables.
- Benchmark-relative report fixtures should not be generated until benchmark/proxy maps exist. Synthetic Attribution Prerequisite Pack v1 satisfies this only for the local synthetic `attribution_v1` attribution mockups, not for scenario-versus-benchmark, probabilistic range, or production/client reports.
- Future attribution fixtures should carry effect provenance and manager benchmark-basis metadata. The local `attribution_v1` calculated mockups now source those fields and calculated effects from Calculated Synthetic Attribution Engine v1 where supported; final report fixtures should not return to supplied fixed-share allocations.
- Calculated attribution fixtures should show or explain active return separately from Total Effect when a theme-bucket return gap could be confused with the effect on total portfolio return.
- Calculated attribution detail/lens fixtures should carry return/effect-basis metadata and visible notes: returns on a 100% theme-bucket basis, effects in percentage points of total portfolio return, and Policy Weight / Actual Weight where weighting effects are visible.
- Future attribution fixtures should declare whether the benchmark basis is explicit policy, imputed current allocation, manager mandate, diagnostic equal weight, or actual-weight exposure. Equal-weight diagnostic reports must not be labeled as agreed policy unless a policy artifact says so.
- Policy allocation fixtures should keep target-versus-actual drift review separate from calculated policy-level attribution effects. Drift tables may show target weight, actual weight, drift, tolerance, and status; effect rows should wait for a policy-level calculated engine.
- Cash Flow Delivered and Cash-Flow Support Outlook may be generated only for the local synthetic demo from the prerequisite pack; real/client cash-flow support stays readiness-only until real cash-need and cash-flow inputs exist.
- Full Lens Exposure may be generated for the complete synthetic AI Adoption and Energy Security assignments; any other lens remains readiness/design-only until complete assignments exist.
- Probabilistic ranges should wait for explicit range analytics.
- Advisor UI wiring remains a later separate decision.
