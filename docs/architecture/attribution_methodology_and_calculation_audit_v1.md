# Attribution Methodology And Calculation Audit v1

## 1. Purpose

This document defines and audits the methodology behind the current local synthetic integrated performance attribution work.

Synthetic demo inputs are acceptable. Uncalculated or unexplained attribution effects are not acceptable for durable product design.

The current attribution mockups are useful product-review artifacts. They prove report shape, language, information budget, and gating posture. They should not be treated as final analytic methodology. The next durable attribution tranche should make each visible effect either calculated from lower-level synthetic inputs or explicitly labeled as a supplied synthetic input with a documented reason.

This document does not build final reports, wire Advisor Preview, Populate, Present, or generated reports, add production attribution math, call external APIs, use real client data, or change advisor UI.

## 2. Attribution Object Definitions

### A. Global Benchmark

The global benchmark is the benchmark for the whole portfolio over the selected period. In the current synthetic pack this is `Northstar Synthetic Policy Benchmark`, a synthetic policy composite aligned to the current synthetic manager mandate mix.

Minimum inputs:

- benchmark id and display name;
- period start and end;
- benchmark return;
- benchmark construction basis;
- approval or synthetic-demo status.

Current status: the global benchmark return is reproducible from current synthetic manager benchmark returns and manager weights.

### B. Theme Benchmark

A theme benchmark is the approved benchmark or proxy associated with one bucket inside one selected lens. For example, under the AI Adoption lens, `Core AI Infrastructure / Hardware` has a synthetic theme benchmark return.

Minimum inputs:

- lens id and lens display name;
- theme bucket id and display name;
- theme benchmark id or proxy id;
- benchmark/proxy return;
- approval status;
- caveat if the benchmark is a proxy.

Current status: theme benchmark returns are explicit supplied synthetic inputs. They are suitable for local demo calculations but are not production benchmark recommendations.

### C. Manager Benchmark

A manager benchmark is the benchmark used to evaluate one manager or sleeve. It may be:

- an approved manager mandate benchmark;
- a weighted blend of theme benchmarks represented in that manager;
- a policy benchmark assigned to the manager.

The benchmark type must be explicit. A manager benchmark should not be shown merely as a number without telling the advisor whether it represents a mandate benchmark, broad policy benchmark, or theme-benchmark blend.

Current status: each manager has a supplied synthetic benchmark return, but the current artifact does not yet explicitly classify the benchmark type beyond synthetic manager proxy language.

### D. Portfolio Return

Portfolio return is the actual whole-portfolio return over the selected period, after the selected return basis and flow treatment are applied.

Current status: the local synthetic portfolio return is calculated as the weighted sum of synthetic manager returns.

### E. Manager Return

Manager return is the actual return for a manager or sleeve over the selected period.

Current status: manager returns are supplied synthetic inputs in the attribution prerequisite generator. Portfolio-level aggregation uses them arithmetically.

### F. Theme Bucket Return

Theme bucket return is the return of portfolio holdings assigned to one theme bucket inside one selected lens.

Current status: current theme bucket returns are supplied synthetic inputs, and relative contribution is calculated as:

```text
theme_bucket_relative_contribution
  = theme_bucket_weight
  * (theme_bucket_portfolio_return - theme_bucket_benchmark_return)
```

### G. Asset Return

Asset return is the return of underlying assets or positions when known.

Current status: the current prerequisite pack includes a small selected-position return subset, but it does not yet provide complete position-level returns, per-theme position memberships, per-theme asset weights, or asset benchmark/reference returns needed for reproducible asset selection and asset sizing effects.

### H. Residual / Unexplained

Residual / unexplained is a separately labeled reconciler.

It may include unmeasured timing, flow, data, rounding, or methodological effects. It must not be mislabeled as timing.

Recommended formula:

```text
residual_unexplained
  = portfolio_return
  - global_benchmark_return
  - sum(calculated_or_supplied_attribution_effects)
```

Current status: residual is separately labeled and timing is not folded into it. The summary residual is small because summary effects are allocated to tie out. The detail residual is larger because only theme-bucket total effects are currently measured at row level.

### I. Timing

Timing is an optional effect that may be shown only if it has a clean definition and adequate trade, holding, price, and flow history.

Current status: timing remains unavailable. It should not be shown as a contribution and residual should not be described as "not timing."

## 3. Benchmark Hierarchy

The benchmark hierarchy should be:

```text
global benchmark
  -> whole portfolio comparison

theme benchmark
  -> one bucket inside one selected lens

manager benchmark
  -> one manager or sleeve
```

The global benchmark answers: "How did the whole portfolio do versus its policy benchmark?"

The theme benchmark answers: "How did this theme bucket do versus the benchmark/proxy assigned to that bucket?"

The manager benchmark answers: "How did this manager do versus the benchmark appropriate to that manager's mandate or benchmark basis?"

Current synthetic-demo assumption:

- Global benchmark: weighted synthetic manager policy benchmark returns.
- Theme benchmark: synthetic lens-bucket proxy returns for AI Adoption and Energy Security.
- Manager benchmark: manager-specific synthetic benchmark proxy return.

Production requirement:

- disclose benchmark type for each benchmark;
- define whether a manager benchmark is mandate-based, broad policy-based, or a theme-benchmark blend;
- store the manager benchmark construction basis in the artifact;
- require approval status and caveat language before showing benchmark-relative claims.

The current manager benchmark is best read as a manager-specific synthetic mandate proxy. It should not be implied to be a weighted theme-benchmark blend until manager-level theme weights and blend formulas exist.

## 4. Attribution Effects: Definitions And Formulas

The formulas below define a recommended v1 synthetic-demo convention. They are intentionally simple and testable.

Variables:

```text
R_portfolio       = actual whole-portfolio return
B_global          = global benchmark return
L                 = selected attribution lens
i                 = theme bucket inside L
j                 = asset or position inside theme bucket i
w_i_actual        = actual portfolio weight in theme bucket i
w_i_policy        = policy or benchmark weight in theme bucket i
B_i_theme         = theme benchmark return for bucket i
R_i_portfolio     = portfolio return for holdings in theme bucket i
w_ij_actual       = actual asset weight inside theme bucket i
w_ij_policy       = policy or equal asset weight inside theme bucket i
R_ij_asset        = asset return for asset j inside bucket i
B_ij_asset        = asset reference return for asset j inside bucket i, if available
```

### Theme Benchmark Selection Effect

Recommended v1 formula:

```text
theme_benchmark_selection_effect
  = sum_i(w_i_policy * B_i_theme)
  - B_global
```

Meaning: Did the selected lens's policy theme-benchmark mix beat the global benchmark before considering actual portfolio sizing?

Current status: not lower-level calculated. The current +0.41% value comes from fixed-share synthetic decomposition:

```text
+0.41% = active_return * 0.36
```

Alternative future conventions:

- equal-weight all theme benchmarks;
- equal-weight non-review theme benchmarks with neutral/review policy weights separately specified;
- externally approved policy theme weights.

Recommendation: use explicit policy weights. Equal weighting is easy, but it can overstate tiny or review buckets.

### Theme Benchmark Sizing Effect

Recommended v1 formula:

```text
theme_benchmark_sizing_effect
  = sum_i(w_i_actual * B_i_theme)
  - sum_i(w_i_policy * B_i_theme)
```

Meaning: Did the portfolio's actual sizing across theme buckets help or hurt relative to the policy theme-benchmark mix?

Current status: not lower-level calculated. The current +0.25% value comes from fixed-share synthetic decomposition:

```text
+0.25% = active_return * 0.22
```

### Asset Selection Effect

Recommended v1 formula:

```text
asset_selection_effect
  = sum_i(
      w_i_actual
      * (
          sum_j(w_ij_policy * R_ij_asset)
          - B_i_theme
        )
    )
```

Meaning: Within each theme bucket, did selected assets beat that bucket's theme benchmark before actual asset sizing effects?

Current status: not lower-level calculated. The current +0.32% value comes from fixed-share synthetic decomposition:

```text
+0.32% = active_return * 0.28
```

If position-level benchmark/reference returns are not available, a simpler v1 may use equal asset weights within each bucket as the policy asset mix.

### Asset Sizing Effect

Recommended v1 formula:

```text
asset_sizing_effect
  = sum_i(
      w_i_actual
      * (
          sum_j(w_ij_actual * R_ij_asset)
          - sum_j(w_ij_policy * R_ij_asset)
        )
    )
```

Meaning: Within each theme bucket, did actual position sizing help or hurt relative to equal or policy asset sizing?

Current status: not lower-level calculated. The current +0.10% value comes from fixed-share synthetic decomposition:

```text
+0.10% = active_return * 0.09
```

### Residual / Unexplained

Recommended v1 formula:

```text
residual_unexplained
  = R_portfolio
  - B_global
  - theme_benchmark_selection_effect
  - theme_benchmark_sizing_effect
  - asset_selection_effect
  - asset_sizing_effect
```

Meaning: What remains after the selected attribution effects are applied.

Current status: calculated as a reconciler. It may include unmeasured timing, data, flow, rounding, or method effects.

### Manager Relative Return

Formula:

```text
manager_relative_return
  = manager_return
  - manager_benchmark_return
```

Current status: calculated by simple arithmetic from current synthetic manager return and manager benchmark return.

### Manager Contribution To Portfolio Attribution

Formula:

```text
manager_portfolio_contribution
  = manager_portfolio_weight
  * manager_relative_return
```

Current status: calculated by simple arithmetic.

### Lens-Based Relative Contribution

Formula:

```text
lens_bucket_relative_contribution
  = theme_bucket_weight
  * (theme_bucket_portfolio_return - theme_benchmark_return)
```

Current status: calculated by simple arithmetic for AI Adoption and Energy Security.

## 5. Current Artifact Audit

| Artifact | Classification |
| --- | --- |
| `portfolio_benchmark_catalog.json` | Benchmark metadata and presentation/readiness fields. `synthetic_return` is copied from the synthetic period return benchmark value, which is derived by weighted manager benchmark arithmetic. |
| `lens_bucket_benchmark_proxy_map.json` | Supplied synthetic theme benchmark/proxy metadata and returns. Directly supports theme benchmark return labels, but does not calculate production benchmarks. |
| `synthetic_period_returns.json` | Mixed. Portfolio return and global benchmark return are derived by weighted manager arithmetic. Manager returns, manager benchmark returns, proxy returns, theme bucket returns, and selected position returns are supplied synthetic inputs. |
| `synthetic_attribution_weights_flows.json` | Mixed. Manager and lens bucket weights are derived from synthetic base value shares. Cash-flow fields are readiness/method metadata; no production flow normalization is implemented. |
| `integrated_attribution_decomposition_inputs.json` | Mixed. Active return and tie-outs are derived by arithmetic. Summary selection/sizing/asset effects are fixed-share synthetic allocations of active return. Theme-bucket total effects are calculated as weight times relative return. Theme-benchmark selection/sizing and asset selection/sizing at row level are not separately measured. |
| `manager_attribution_prerequisites.json` | Mixed. Manager relative returns and portfolio contributions are arithmetic. Manager benchmark returns are supplied synthetic inputs. Manager component effects are fixed-share synthetic allocations, not lower-level manager attribution calculations. |
| `attribution_readiness_summary.json` | Readiness metadata. It correctly keeps timing unavailable and production/client attribution gated. |
| `attribution_v1` report input/view fixtures | Presentation metadata generated from prerequisites. They should not be treated as calculation sources. |

The strongest currently calculated attribution quantities are:

- portfolio return from manager weights and manager returns;
- global benchmark return from manager weights and manager benchmark returns;
- manager relative return;
- manager portfolio contribution;
- lens-bucket relative contribution;
- tie-outs and residuals.

The weakest currently calculated quantities are:

- theme benchmark selection;
- theme benchmark sizing;
- asset selection;
- asset sizing;
- manager-level component effects.

Those values are deterministic, but they are not yet calculated from lower-level benchmark portfolios or asset inputs.

## 6. Calculation Gap Analysis

### What Produces The +0.41% Theme Benchmark Selection Value?

Current answer:

```text
active_return = 8.1456% - 6.9940% = 1.1516%
theme_benchmark_selection_effect = active_return * 0.36 = 0.4146%
```

This is a fixed-share synthetic decomposition. It is not a calculation from a selected theme-benchmark portfolio.

Required improvement: add a theme benchmark policy portfolio and calculate:

```text
sum_i(w_i_policy * B_i_theme) - B_global
```

### What Is The Blended Theme Benchmark Portfolio?

Current answer: it does not exist as a distinct artifact. The current detail row total uses actual AI Adoption bucket weights and theme benchmark returns, but there is no separate policy or equal-weight theme benchmark portfolio.

Required improvement: add explicit theme benchmark portfolio weights for the selected attribution lens.

### What Is It Compared Against?

Recommended v1: compare the policy theme benchmark portfolio to the global benchmark for selection. Then compare the actual-weight theme benchmark portfolio to the policy theme benchmark portfolio for sizing.

Current answer: summary selection and sizing are compared only through active-return allocation, not through explicit benchmark portfolios.

### What Produces Theme Benchmark Sizing?

Current answer:

```text
theme_benchmark_sizing_effect = active_return * 0.22
```

Required improvement:

```text
sum_i(w_i_actual * B_i_theme) - sum_i(w_i_policy * B_i_theme)
```

### What Produces Asset Selection?

Current answer:

```text
asset_selection_effect = active_return * 0.28
```

Required improvement: complete per-theme asset membership, asset returns, and policy or equal asset weights.

### What Produces Asset Sizing?

Current answer:

```text
asset_sizing_effect = active_return * 0.09
```

Required improvement: actual and policy/equal asset weights inside each theme bucket, plus asset returns.

### How Is Manager Benchmark Return Defined?

Current answer: it is a supplied synthetic manager-specific benchmark proxy return. The artifact gives each manager a benchmark return and proxy display name, but it does not yet classify whether the benchmark is mandate-based, broad policy-based, or a theme-benchmark blend.

Required improvement: add `manager_benchmark_type` and, where applicable, `manager_benchmark_components`.

### Are Manager Benchmarks Broad Mandate Benchmarks Or Blends Of Theme Benchmarks?

Current answer: they should be treated as manager-specific synthetic mandate proxies. They are not yet theme-benchmark blends.

Required improvement: make this explicit in the artifact and report caveats.

### What Must Be Added For A Genuine Detailed Attribution Report?

Minimum additions:

- selected attribution lens id;
- theme benchmark portfolio policy weights;
- policy/equal theme benchmark portfolio return;
- actual-weight theme benchmark portfolio return;
- complete per-theme asset lists;
- per-theme actual asset weights;
- per-theme policy or equal asset weights;
- per-asset returns;
- per-asset benchmark/reference returns or a documented fallback;
- manager benchmark type and construction basis;
- explicit residual policy and tie-out tolerance.

### What Can Remain Supplied Synthetic Input?

Acceptable supplied synthetic inputs for local demo:

- manager returns;
- manager benchmark returns, if benchmark type is explicit;
- theme benchmark returns, if caveated as synthetic proxies;
- asset returns, if generated deterministically from synthetic fixtures;
- policy weights, if the policy is declared as synthetic demo policy.

Not acceptable as durable methodology:

- selection/sizing effects that are merely allocated fixed percentages of active return without a benchmark portfolio or asset-level basis.

## 7. Recommended V1 Synthetic Attribution Convention

The next implementation tranche should use this convention:

1. Selected lens: AI Adoption for the initial detailed attribution demo.
2. Global benchmark: Northstar Synthetic Policy Benchmark.
3. Theme benchmark portfolio: one AI Adoption theme-benchmark portfolio with explicit policy weights.
4. Policy weights: start with explicit synthetic policy weights, initially equal to current AI Adoption lens bucket weights unless Frank wants a neutral policy mix. Store the policy basis even if it equals actual weights in the first fixture.
5. Theme benchmark selection:

```text
policy_theme_benchmark_return - global_benchmark_return
```

6. Theme benchmark sizing:

```text
actual_weight_theme_benchmark_return - policy_theme_benchmark_return
```

7. Theme bucket total effect:

```text
actual_theme_bucket_weight * (theme_bucket_portfolio_return - theme_benchmark_return)
```

8. Asset selection: within each theme bucket, compare the policy/equal-weight selected asset return to the bucket's theme benchmark.
9. Asset sizing: within each theme bucket, compare actual-weight selected asset return to policy/equal-weight selected asset return.
10. Manager benchmark convention: default to manager-specific synthetic mandate benchmarks, not theme-benchmark blends, until manager-level theme benchmark blends are explicitly added.
11. Residual convention: residual is the remaining reconciler after calculated effects, with a tolerance such as `0.000001`.
12. Timing gate: timing remains unavailable unless clean trade, holding, price, and flow history is added and the timing formula is approved.

This convention is intentionally simple enough to implement without production attribution modeling.

## 8. Required Synthetic Data Improvements

### Required For Summary Attribution

- selected attribution lens id;
- global benchmark return;
- theme benchmark returns;
- theme benchmark policy weights;
- actual theme weights;
- policy theme benchmark portfolio return;
- actual-weight theme benchmark portfolio return;
- residual calculation and tolerance.

### Required For Detail Attribution

- all summary inputs;
- per-theme asset list;
- per-theme asset actual weights;
- per-theme asset policy/equal weights;
- per-asset returns;
- per-asset benchmark/reference return or documented fallback;
- calculated per-theme selection and sizing rows;
- row-level tie-out to summary.

### Required For Manager Attribution

- manager return;
- manager benchmark return;
- manager benchmark type;
- manager benchmark construction basis;
- manager weight;
- manager relative return;
- manager portfolio contribution;
- optional manager-level theme weights if benchmark is a theme blend;
- manager residual policy.

### Required For Lens-Based Attribution

- complete lens assignment pack;
- theme bucket weights;
- theme bucket portfolio returns;
- theme benchmark returns;
- relative contribution formula;
- caveat explaining whether theme benchmarks are synthetic proxies.

## 9. Timing Policy

Timing remains unavailable unless defined as the difference between two clearly specified states.

Required before timing can be shown:

- beginning holdings;
- ending holdings;
- trade dates;
- external flows;
- prices through the period;
- target, equal, or average holding convention;
- clean comparison portfolio;
- approved formula and validation tolerance.

If unavailable:

- do not show timing as a contribution;
- do not say residual is "not timing";
- say residual may include unmeasured timing, data, flow, rounding, or reconciliation effects.

## 10. Future Report Implications

Future attribution reports should change as follows:

- Summary should include a benchmark-basis note: global benchmark, selected lens, and whether effects are calculated or supplied.
- Detail should show calculated theme-benchmark rows. The current `Not separately measured` component columns are honest but should be replaced only after calculated inputs exist.
- Manager reports should disclose manager benchmark basis: mandate benchmark, broad policy benchmark, or theme-benchmark blend.
- Lens-based reports should clarify theme benchmark construction and proxy status.
- Residual caveats should stay precise: residual may include unmeasured timing/data/flow/reconciliation effects.
- Reports should not imply production attribution readiness from synthetic fixture readiness.

## 11. Implementation Sequencing Recommendation

Recommended next tranche:

```text
Synthetic Attribution Calculation Inputs v1
```

Alternative name:

```text
Calculated Synthetic Attribution Engine v1
```

The next tranche should:

- add missing synthetic lower-level inputs;
- add explicit benchmark-basis metadata;
- calculate summary effects from theme benchmark portfolios and asset inputs;
- regenerate attribution prerequisites after calculations are reproducible;
- update attribution mockups only after calculated effects replace fixed-share synthetic allocations;
- keep Advisor Preview, Populate, Present, generated reports, backend endpoints, Docker/deployment, real data, external APIs, and production attribution modeling out of scope.

## 12. Open Questions For Frank

1. Should v1 detailed attribution use AI Adoption as the first selected lens?
2. Should theme benchmark selection use equal weights or a policy-weighted theme mix?
3. Should manager benchmarks default to mandate benchmarks or weighted theme-benchmark blends?
4. Should asset selection/sizing require position-level return data, or can it operate at grouped synthetic asset level?
5. How much residual is acceptable before a report should say attribution is incomplete?
6. Should the summary report disclose the selected attribution lens explicitly?
