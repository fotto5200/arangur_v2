# Attribution Policy / Mandate Benchmark Design v1

## 1. Purpose

This document defines the policy and mandate benchmark layer that must exist before attribution reports can fairly evaluate advisors, families, and managers.

Governing rule: attribution should compare each decision-maker to the benchmark or allocation they were responsible for, not to an artificial benchmark they never agreed to manage against.

The current calculated attribution work proves that Arangur can calculate local synthetic effects. The next architecture step is to separate responsibility levels so mathematically correct effects do not blame the wrong decision-maker.

## 2. Core Problem

The main flaw is treating an equal-weight lens-bucket benchmark as the default portfolio-level policy benchmark.

Equal-weight theme allocation can be useful as a diagnostic. It answers: what would the attribution result look like if every selected theme bucket had the same policy weight? It does not automatically answer whether the advisor, family, or manager made a good decision.

Example: a small optionality sleeve may perform extremely well. If the agreed policy was to allocate only 5-10% to that sleeve, the advisor should not automatically be penalized after the fact for not allocating 40% to it. The correct question is whether the portfolio followed the agreed allocation, whether that allocation worked, and whether the sleeve was implemented well inside its mandate.

Equal-weight theme allocation is therefore diagnostic unless the advisor and family explicitly agreed to equal weights as policy.

## 3. Attribution Responsibility Layers

### A. Family / Advisor Policy Allocation Layer

Question: did the advisor/family's agreed policy allocation work, and was the portfolio allocated according to it?

This layer evaluates:

- agreed allocation across managers, mandates, sleeves, or policy buckets;
- drift from target allocation;
- whether deviations are due to flows, performance, rebalancing policy, or implementation shortfall;
- policy-level value added or lost versus a global benchmark.

This layer belongs to the family/advisor policy conversation. It should not automatically assign blame to a manager for capital the manager never controlled.

### B. Actual Manager / Sleeve Allocation Layer

Question: what capital actually ended up with each manager or sleeve?

This layer records:

- actual NAV/share by manager;
- imputed current allocation if accepted as policy baseline;
- allocation drift from explicit policy if targets exist;
- rebalance tolerance;
- contribution of manager allocation choices to portfolio outcome.

This layer is descriptive before it is evaluative. If current NAV weights are accepted as the baseline, allocation differences should not be treated as advisor errors.

### C. Within-Manager Implementation Layer

Question: given the capital and mandate assigned to the manager, did the manager implement well?

This layer evaluates:

- manager return versus manager mandate benchmark;
- theme/lens bucket choices inside the manager's mandate;
- asset selection and sizing inside the manager's investable universe;
- residual / unexplained;
- timing only if cleanly measurable.

This layer should not penalize a manager for not receiving more capital or for not operating outside the mandate they were hired to implement.

### D. Optional Blended / All-In Attribution Layer

Question: can all layers be shown in one full bridge?

This can be allowed later, but should not be the default. A blended report may be mathematically complete while still being hard to explain. The safer product path is two easy-to-understand reports first: one at the policy allocation level and one within the manager's mandate/allocation.

## 4. Benchmark Hierarchy

| Benchmark | What it is | Owner / approver | Question it answers | Client-facing attribution? | Advisor/internal diagnostic? |
| --- | --- | --- | --- | --- | --- |
| Global benchmark | Top-level whole-portfolio comparison benchmark. | Advisor/family, firm model, or approved benchmark catalog. | Did the portfolio outperform the broad agreed comparison? | Yes, when approved and disclosed. | Yes. |
| Family/advisor policy benchmark | Agreed allocation benchmark across managers, mandates, sleeves, policy buckets, or broad exposure categories. | Advisor/family, with firm-approved representation where needed. | Did the agreed allocation work, and did actual allocation follow it? | Yes, when explicitly agreed or documented. | Yes. |
| Imputed current allocation baseline | Current manager/sleeve NAV weights accepted as the baseline policy allocation. | Advisor/family or demo setup mode. | What happened given the capital already allocated today? | Cautiously, with caveat. | Yes, especially for quick start. |
| Manager mandate benchmark | Benchmark used to evaluate a manager against the role they were hired to perform. | Advisor/firm manager research, mandate document, or approved synthetic/demo catalog. | Did the manager add value inside the assigned mandate? | Yes, when approved and explainable. | Yes. |
| Theme benchmark | Benchmark/proxy for one bucket inside a selected lens. | Approved analytic pack, benchmark map, or synthetic demo map. | Did exposure within a theme bucket beat its bucket benchmark? | Yes only with clear proxy/benchmark caveat. | Yes. |
| Equal-weight diagnostic benchmark | Analytical lens that gives each selected bucket equal policy weight. | Analytics/design team unless explicitly adopted by advisor/family. | What would attribution look like under a neutral/equal-weight diagnostic? | No, unless explicitly selected as policy. | Yes. |
| Actual-weight exposure benchmark | Benchmark blend reflecting the portfolio's actual exposures. | Analytics engine from holdings/allocation snapshot. | What benchmark return corresponds to the exposures actually held? | Sometimes, with clear caveat. | Yes. |

The hierarchy should be visible in report metadata. A report should not blur these benchmark types or imply that a diagnostic benchmark is the agreed client policy.

## 5. Policy Allocation Modes

### A. Explicit Policy Allocation Mode

The advisor/family enters intended target weights.

Example by manager:

- Manager A: 10%
- Manager B: 20%
- Manager C: 20%
- Manager D: 20%
- Manager E: 30%

Example by mandate:

- Income / capital preservation: 40%
- Stable/core growth: 50%
- Optionality sleeve: 10%

This mode supports allocation drift reporting and policy-level attribution because the system knows the intended target.

### B. Imputed Current Allocation Mode

The imported current NAV weights are accepted as the baseline policy allocation.

This mode is important for usability. It means:

- the system does not penalize the advisor for manager allocation differences;
- current allocations are treated as the accepted mandate baseline;
- attribution focuses first on what managers did within their allocations.

This mode is useful for early setup, Plaid-import demos, and cases where the family has not yet formalized target weights.

### C. Hybrid Mode

Some allocations may be explicit while others are imputed or grouped.

Example: the advisor may define a 10% optionality sleeve target, while all stable/core managers are grouped and imputed from current NAV weights.

Hybrid mode should be caveated clearly:

- explicit targets should be labeled as explicit;
- imputed targets should be labeled as current-allocation baseline;
- grouped rows should state what is included;
- drift should be calculated only where a target exists or where a current baseline has been accepted.

## 6. Policy Allocation Drift

Allocation drift is the difference between target policy weight and actual current weight. It should be interpreted before it is judged.

Possible causes:

- market performance;
- cash flows, withdrawals, or contributions;
- delayed implementation;
- rebalancing tolerance;
- intentional tactical deviation;
- missing data;
- manager valuation marks.

Reports should distinguish:

- target policy weight;
- actual current weight;
- drift;
- drift within tolerance;
- drift needing review;
- attribution impact of drift where measurable.

Do not assume every drift is a mistake. A drift caused by market appreciation inside a tolerance band is different from an unimplemented target allocation or a cash-flow delay.

## 7. Attribution Report Family Redesign

### A. Policy Allocation Review

Core question: did the portfolio follow the agreed advisor/family allocation?

Visible evidence:

- target policy weights;
- actual weights;
- drift;
- tolerance;
- review flags.

### B. Policy-Level Attribution

Core question: did the agreed policy allocation add value versus the global benchmark?

Visible evidence:

- global benchmark return;
- policy benchmark return;
- actual allocation return if different;
- policy selection effect;
- policy allocation/drift effect;
- residual/caveat.

### C. Manager Mandate Attribution Summary

Core question: did each manager add value versus the benchmark implied by their mandate?

Visible evidence:

- manager return;
- manager mandate benchmark return;
- relative return;
- largest measured driver;
- residual / unexplained;
- caveats.

### D. Within-Manager Attribution Detail

Core question: within the manager's assigned mandate, which theme/asset choices drove performance?

Visible evidence:

- manager-specific benchmark basis;
- theme/asset returns;
- effect columns;
- residual;
- timing unavailable unless clean.

### E. Equal-Weight Diagnostic Attribution

Core question: what would attribution look like under an equal-weight diagnostic lens?

Visible evidence:

- clearly labeled diagnostic/equal-weight basis;
- clear caveat that it is not the agreed policy benchmark unless selected as policy;
- same effect-basis clarity as other attribution reports.

### F. Blended / All-In Attribution

Core question: can all layers be combined in one bridge?

Status: defer or advisor-review-only until users explicitly want it and have already understood the separate policy and manager/mandate reports.

## 8. Decision-Maker Accountability Rule

- Family/advisor policy allocation evaluates the advisor/family's chosen allocation.
- Manager mandate attribution evaluates manager implementation inside assigned capital and mandate.
- A manager should not be penalized for not receiving more capital.
- An advisor should not be penalized for not overweighting a winning high-volatility sleeve beyond the agreed mandate.
- Equal-weight diagnostics should not be confused with client-agreed policy.

This rule should be enforced in report naming, caveats, metadata, and future calculation inputs.

## 9. Synthetic Demo Implications

Current issue: the calculated attribution detail currently uses equal policy weights across AI Adoption buckets. That is useful for calculation testing, but it should be labeled as equal-weight diagnostic unless the policy really is equal-weight.

Recommended synthetic next steps:

- create a synthetic policy allocation artifact;
- create explicit policy weights by manager/mandate;
- create an imputed-current-allocation baseline option;
- create manager mandate benchmark definitions;
- create a Policy Allocation Review mockup;
- create a Policy-Level Attribution mockup;
- keep equal-weight AI Adoption attribution as diagnostic unless explicitly selected.

This should not invalidate the current calculated attribution mockups. It reclassifies their equal-weight policy assumption as a diagnostic benchmark basis unless a future policy artifact explicitly adopts those weights.

## 10. Data Contract Requirements

| Future artifact | Purpose | Key fields |
| --- | --- | --- |
| `policy_allocation_profile.json` | Defines the family/advisor allocation profile. | profile id, owner, period, mode, target categories, approval/caveat status. |
| `policy_allocation_mode.json` | Records explicit, imputed, or hybrid setup mode. | mode, selected baseline date, explicit rows, imputed rows, grouping rules, caveats. |
| `manager_target_allocation.json` | Captures target weights by manager or sleeve. | manager id/display name, target weight, tolerance band, mandate id, effective date. |
| `actual_manager_allocation_snapshot.json` | Captures current actual manager/sleeve allocation. | as-of date, manager NAV, portfolio NAV, actual weight, source quality, valuation status. |
| `allocation_drift_summary.json` | Summarizes target versus actual allocation drift. | target weight, actual weight, drift, tolerance, drift status, drift cause when known. |
| `manager_mandate_benchmark_catalog.json` | Defines approved manager mandate benchmarks. | manager/mandate id, benchmark id/name, basis type, source, approval status, caveat. |
| `manager_benchmark_basis_map.json` | Maps managers to mandate benchmark basis. | manager id, mandate id, benchmark id, blend components if any, fallback policy. |
| `policy_level_attribution_inputs.json` | Provides inputs for policy-level attribution. | global benchmark return, policy weights, policy bucket returns, actual weights, flows, period. |
| `policy_level_attribution_results.json` | Stores calculated policy-level attribution outputs. | policy benchmark return, actual allocation return, policy selection effect, allocation/drift effect, residual. |
| `within_manager_attribution_inputs.json` | Provides manager-specific implementation inputs. | assigned capital, manager return, mandate benchmark return, internal theme/asset weights and returns. |
| `equal_weight_diagnostic_attribution_results.json` | Stores diagnostic equal-weight outputs. | selected lens, equal weights, diagnostic benchmark return, effects, caveats, non-policy flag. |

Each artifact should carry synthetic/local-only metadata when used in the demo path and should not imply production readiness without approved real/client inputs.

## 11. User / Setup Experience Implications

Advisors should not be forced to define every benchmark upfront. The setup path should support a quick-start mode where current NAV is accepted as the baseline, then let advisors add explicit policy allocation later.

Product implications:

- support current-NAV-imputed baseline for quick start;
- support explicit policy allocation when available;
- support hybrid profiles when only some targets are known;
- defer custom benchmark construction;
- reuse approved benchmark maps when possible;
- keep setup small enough that advisors do not abandon the tool.

The product should make it easy to start honestly, then become more precise as policy and mandate data improves.

## 12. Report Wording Implications

Preferred language:

- policy allocation;
- target allocation;
- actual allocation;
- drift;
- within tolerance;
- manager mandate benchmark;
- diagnostic equal-weight lens;
- effect;
- residual / unexplained.

Avoid:

- implying equal weight is the policy;
- blaming a manager for capital allocation decisions outside the manager's control;
- blaming an advisor for not overweighting a winning optionality sleeve beyond agreed policy;
- calling a diagnostic benchmark the client benchmark.

Report titles should carry the level of responsibility. "Policy Allocation Review" and "Within-Manager Attribution Detail" are clearer than one blended "attribution" label.

## 13. Implementation Sequencing Recommendation

Recommended tranches:

A. Synthetic Policy Allocation / Mandate Benchmark Pack v1

Create synthetic policy allocation and manager mandate benchmark artifacts.

B. Policy Allocation Review Mockups

Generate mockups showing target versus actual manager/mandate allocation and drift.

C. Policy-Level Attribution Calculation Inputs

Create inputs to calculate policy-level attribution versus global benchmark.

D. Manager Mandate Attribution Redesign

Adjust manager attribution to use mandate benchmark basis clearly.

E. Optional Equal-Weight Diagnostic Attribution

Keep equal-weight AI Adoption attribution as a diagnostic report.

F. Blended All-In Attribution

Defer until separate reports are understood and accepted.

## 14. Open Questions For Frank

- Should quick-start mode default to imputed current allocation baseline?
- Should explicit policy allocation be manager-based, mandate-based, lens-based, or all three?
- How should rebalancing tolerance be represented?
- Should drift caused by performance be treated differently from drift caused by flows or implementation?
- Should policy allocation reports be client-facing by default?
- Should equal-weight diagnostic attribution remain advisor-only?
- How much setup should be required before attribution reports are allowed?

## 15. Follow-Up: Synthetic Policy Allocation / Mandate Benchmark Pack v1

Synthetic Policy Allocation / Mandate Benchmark Pack v1 now provides deterministic local-only artifacts for explicit policy allocations, actual manager allocation snapshots, allocation drift summaries, imputed-current baseline, manager mandate benchmarks, manager benchmark-basis mapping, policy-level attribution input scaffolding, and equal-weight diagnostic classification.

This pack feeds the local Policy Allocation Review mockups and gives Policy-Level Attribution an input scaffold for a future calculation engine. Equal-weight AI Adoption attribution remains diagnostic unless the advisor/family explicitly selected equal-weight theme buckets as policy. Advisor UI/report wiring, generated-report integration, calculated policy-level attribution, timing attribution, live/real data, external APIs, deployment, and production attribution modeling remain out of scope.

## 16. Follow-Up: Policy Allocation Review Mockups v1

Policy Allocation Review Mockups v1 now turns the synthetic policy/mandate prerequisite pack into local product-review artifacts under `policy_allocation_v1`.

Generated reports:

- Policy Allocation Review: target weight, actual weight, drift, tolerance, and status for all six current managers.
- Policy Allocation Drift Summary: compact review/material watch list, currently the Manager C under-target row.
- Imputed Current Allocation Baseline: setup/readiness note that accepts current weights as the baseline, suppresses drift attribution, supports quick-start use, and does not prove the current allocation is ideal.
- Manager Mandate Benchmark Basis: all six current manager mandate benchmark-basis rows.

Policy-Level Attribution Calculation and Mockups v1 now exists under `policy_attribution_v1` and calculates the local synthetic bridge from Global benchmark to Target policy benchmark to Actual allocation benchmark to Actual portfolio. Blended / All-In Attribution remains deferred until separate policy-level and manager-level reports are understood. Production policy allocation reporting, current-vs-proposed allocation, timing attribution, Advisor Preview/Populate/Present wiring, generated-report integration, live/real data, external APIs, deployment, and production attribution modeling remain out of scope.

## 17. Follow-Up: Policy-Level Attribution Calculation and Mockups v1

Policy-Level Attribution Calculation and Mockups v1 now turns the synthetic policy/mandate prerequisite pack into calculated local product-review outputs under `data/simulation/policy_level_attribution/policy_level_attribution_engine_v1/` plus report fixtures and Markdown mockups under `policy_attribution_v1`.

The calculated bridge separates:

- Global benchmark return;
- Target policy benchmark return;
- Actual allocation benchmark return;
- Actual portfolio return.

It reports policy design effect, allocation drift effect, and manager implementation effect in percentage points of total portfolio return, with a zero residual tie-out for the synthetic pack. The manager detail report shows all six manager/sleeve rows, and the imputed-current variant suppresses allocation drift effect while making clear that current allocation is not proven ideal. Within-manager attribution detail, blended/all-in attribution, timing attribution, dollar P&L attribution, production client attribution, and current-vs-proposed policy attribution remain future or gated work.

## 18. Follow-Up: Advisor Policy Attribution Redesign v2

Advisor Policy Attribution Redesign v2 now supersedes the v1 policy-level attribution summary as the primary product-review surface for advisor policy attribution. It writes local-only calculated artifacts under `data/simulation/policy_level_attribution/advisor_policy_attribution_engine_v2/`, report fixtures under `policy_attribution_v2`, and Markdown mockups under `docs/product/report_mockups/policy_attribution_v2/`.

The v2 surface decomposes advisor policy effect before manager implementation into selected mandate effect, target weighting effect, and funding drift effect. Actual Return remains context only, and manager implementation is excluded from the primary advisor policy report with a separate handoff marker for future Manager / Within-Mandate Attribution Detail work. Blended/all-in attribution, timing attribution, dollar P&L attribution, production client attribution, and current-vs-proposed policy attribution remain gated or deferred.
