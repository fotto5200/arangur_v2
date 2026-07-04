# Arranger Internal Analytics Algorithm Design v1

## 1. Purpose And Controlling Methodology

This document defines the controlling internal analytic methodology for Arranger scenario analytics. It is architecture/design documentation only. It does not implement production code, change app behavior, modify UI, create report views, generate analytics outputs, add backend endpoints, change Docker/deployment configuration, fetch market data, use real client data, or add dependencies.

The controlling product methodology is full portfolio revaluation under two internally consistent market states:

```text
base_market_state
-> value every position
-> base_portfolio_value

scenario_market_state
-> value every position
-> scenario_portfolio_value

impact = scenario_portfolio_value - base_portfolio_value
```

Scenario impact is not defined as a direct exposure formula. Key-rate moves, driver perturbations, covariance assumptions, interpolation rules, look-through policies, and instrument-specific approximations may be internal inputs to a valuation model, but they are not the product explanation and they are not advisor-facing controls.

Core implications:

- Arranger defines approved scenarios by constructing complete scenario market states.
- Scenario market states are generated from approved key-rate or driver perturbations expanded into complete market input surfaces.
- Every position is valued under the base market state and under the scenario market state.
- Every position maps to an instrument and a pricing function, or to an explicit coverage/review status.
- Differences are aggregated and attributed after valuation.
- Themes classify and explain positions and impacts after valuation; they do not price positions.
- Coverage, substitute inputs, and confidence describe limits in full revaluation capability; they do not replace the methodology.
- Arangur Advisor App consumes approved outputs and does not expose control-plane or valuation-construction machinery.

## 2. Boundary

Three layers must stay separate:

| Layer | Owner | Examples | Advisor-facing? |
| --- | --- | --- | --- |
| Pre-authored by Arranger | Internal control plane | Scenario catalog, market-state transformation rules, key-rate expansion policy, theme taxonomy, classification rules, confidence rules, report capability map | Only approved labels, stories, caveats, and supported choices |
| Calculated at portfolio run | Internal analytics engine | Base valuation, scenario valuation, position impacts, attribution summaries, confidence/coverage map, run manifest | Only summarized through approved report elements |
| Selected by advisor | Arangur Advisor App | Approved scenario, theme focus, lens, scope, report element sequence, narrative sections | Yes |

Advisor-facing Arangur must not expose:

- model-building tools;
- raw covariance matrices or propagation controls;
- key-rate construction controls;
- valuation internals;
- shock-vector editing;
- substitute-input or coverage-rule editors;
- theme taxonomy editors.

Advisor-facing Arangur may expose:

- approved scenario names and descriptions;
- approved theme/lens choices;
- report-ready impacts and explanations;
- confidence labels, coverage caveats, and review language.

## 3. Full Market State

A full market state is the central input to valuation. It is not merely a list of named shocks. It is the complete set of market inputs required to value the portfolio for a valuation date.

Required top-level fields:

- `market_state_id`
- `valuation_date`
- `as_of_timestamp`
- `base_or_scenario`
- `scenario_id`, nullable for base state
- `source_pack_id`
- `source_pack_version`
- `data_confidence`
- `source_metadata`
- `market_inputs`
- `consistency_checks`
- `caveats`

Market inputs should include, as applicable:

- yield curves;
- credit curves;
- discount curves;
- inflation curves;
- FX spot and forward rates;
- equity and index levels;
- commodity levels;
- volatility surfaces;
- private-market marks and approved mark policies;
- calendars and settlement assumptions;
- corporate-action assumptions;
- instrument reference data needed for valuation;
- data confidence and source metadata for each input family.

Example shape:

```json
{
  "market_state_id": "market_state_base_2026_06_30",
  "valuation_date": "2026-06-30",
  "base_or_scenario": "base",
  "scenario_id": null,
  "market_inputs": {
    "yield_curves": {},
    "credit_curves": {},
    "discount_curves": {},
    "inflation_curves": {},
    "fx_rates": {},
    "equity_index_levels": {},
    "commodity_levels": {},
    "volatility_surfaces": {},
    "private_market_marks": {},
    "calendars": {}
  },
  "data_confidence": {
    "overall": "synthetic_demo",
    "input_family_confidence": {}
  }
}
```

## 4. Scenario Market State

A scenario is a method for producing a complete alternate market state from the base market state. It is not a direct position impact formula.

Scenario construction:

1. Start from a validated base market state.
2. Load an approved scenario definition from an approved analytic pack.
3. Apply approved key-rate, driver, or broader key market-state scenario-basis perturbations.
4. Expand sparse perturbations into complete required curves, surfaces, levels, marks, and policies.
5. Validate market-state consistency.
6. Publish the scenario market state, or a complete enough market-state change set plus reconstruction instructions.

Required scenario market-state fields:

- `scenario_market_state_id`
- `scenario_id`
- `scenario_display_name`
- `base_market_state_id`
- `valuation_date`
- `scenario_horizon`
- `construction_method`
- `approved_perturbations`
- `expanded_market_inputs`
- `consistency_checks`
- `data_confidence`
- `caveats`
- `approval_status`

The scenario catalog should define advisor-readable scenarios, but the valuation engine should consume full market states.

Recommended scenario library:

| Scenario | Scenario ID | Construction focus | Notes |
| --- | --- | --- | --- |
| AI / Chip Selloff | `ai_chip_selloff` | Build alternate equity/index, volatility, credit, private-liquidity, and related input surfaces | Existing demo scenario. |
| Rate Shock | `rate_shock` | Build full shocked yield, discount, and spread curves | Existing demo scenario should be reframed around full curves. |
| Curve Steepening | `curve_steepening` | Build full yield/discount curves from key-tenor perturbations | Adds explicit curve-shape scenario support. |
| Energy Shock | `energy_shock` | Build commodity, inflation, FX, equity, and real-asset inputs | Existing demo scenario. |
| Private Liquidity Freeze | `private_market_liquidity_freeze` | Build private-market mark policy, secondary-discount, credit, and liquidity inputs | Should carry conservative confidence/review language. |
| Taiwan Disruption | `taiwan_disruption` | Build semiconductor, supply-chain, energy, FX, and volatility inputs | Existing demo scenario. |
| Credit Spread Widening | `credit_spread_widening` | Build full public/private credit curves and related liquidity inputs | Needed for income and credit manager review. |
| Inflation Persistence | `inflation_persistence` | Build inflation, real-rate, commodity, and related nominal-rate inputs | Useful for real assets and spending-sensitivity discussion. |

## 5. Key-Rate Expansion

Key-rate shocks are compact scenario-construction inputs used to build full shocked curves. They are one special case of the broader key market-state scenario basis construction defined in `docs/architecture/key_market_state_scenario_basis_design_v1.md`. They are not final valuation outputs and are not advisor-facing controls.

Key-rate expansion must define:

- key tenor points, such as 3M, 1Y, 2Y, 5Y, 10Y, and 30Y;
- curve family, such as Treasury, discount, real-rate, inflation, municipal, IG, HY, or private credit;
- interpolation policy between key tenors;
- extrapolation policy beyond key tenors;
- compounding/day-count conventions where needed;
- curve consistency rules;
- supported shapes: parallel, steepener, flattener, twist, and custom key-rate scenarios;
- validation tolerances;
- source and confidence metadata.

Distinction:

- Key-rate perturbation: compact Arranger-approved input.
- Full shocked curve: complete valuation input generated from the perturbation.
- Scenario market state: complete set of shocked curves, surfaces, levels, marks, policies, and metadata.

Key-rate expansion should never be used as a stand-alone explanation of portfolio impact. Broader scenario basis completion likewise stops at scenario market-state construction. The portfolio impact comes from valuing positions with the full shocked market state.

## 6. Full Position Valuation

Every position should be valued through the same generic interface:

`docs/architecture/position_valuation_coverage_mapping_design_v1.md` defines the detailed valuation coverage mapping layer behind this interface: positions map to instruments, pricing functions, required market inputs, valuation results, and explicit coverage statuses. Pricing functions consume full base or scenario market states. This mapping is separate from thesis classification, which happens after valuation.

```python
def value_position(position, market_state, valuation_context):
    model = valuation_context.model_registry.select(position)
    required_inputs = model.required_market_inputs(position)
    coverage = check_market_input_coverage(required_inputs, market_state)

    if not coverage.can_value:
        return approved_coverage_treatment(position, market_state, coverage, valuation_context)

    value_result = model.value(
        position=position,
        market_inputs=market_state.market_inputs,
        valuation_date=market_state.valuation_date,
        assumptions=valuation_context.assumptions_for(position),
    )

    return {
        "position_id": position.position_id,
        "market_state_id": market_state.market_state_id,
        "value": value_result.value,
        "valuation_model_id": model.model_id,
        "coverage_status": "valued",
        "confidence": score_valuation_confidence(position, market_state, coverage, value_result),
        "caveats": value_result.caveats,
        "required_inputs": required_inputs,
        "used_inputs": value_result.used_inputs,
    }
```

Examples:

- Bond: value expected cash flows using the scenario discount/yield curves, spread curves, calendar, settlement, and instrument terms.
- Option or structured product: reprice under scenario underlyings, rates, volatility surfaces, calendars, and product terms.
- ETF or fund: use look-through holdings when available; otherwise apply an approved valuation policy with explicit coverage limits.
- Private or opaque asset: use approved mark policy, manager mark treatment, appraisal policy, or review-required treatment with explicit limitations.
- Cash: use face value, currency, settlement date, and cash/yield treatment as applicable.

Instrument-specific internal calculations may use whatever mathematics the selected valuation model requires. Those calculations are implementation details. The product methodology remains: value the position under the base market state, value it under the scenario market state, compare the results.

## 7. Portfolio Revaluation

Portfolio revaluation is the only scenario impact methodology.

```text
base_portfolio_value = sum(value_position(position, base_market_state))
scenario_portfolio_value = sum(value_position(position, scenario_market_state))
impact = scenario_portfolio_value - base_portfolio_value
impact_percent = impact / base_portfolio_value
```

Required run outputs:

- position base values;
- position scenario values;
- position impacts;
- base portfolio value;
- scenario portfolio value;
- portfolio impact;
- coverage status by position;
- confidence/caveats by position;
- attribution summaries after valuation.

Attribution happens after valuation:

- by position;
- by manager;
- by account;
- by sleeve;
- by theme;
- by scenario;
- by confidence bucket.

## 8. Themes And Classification

Themes classify positions and impacts after valuation. They do not price positions and do not substitute for valuation.

Theme/classification rules:

- Theme taxonomy is Arranger-approved and versioned.
- A position can belong to multiple themes.
- Theme weights are attribution/reporting weights, not valuation weights.
- Theme mapping supports explanation, grouping, hidden concentration review, and advisor/client discussion.
- Theme mapping should preserve unresolved or review-required classifications rather than forcing every position into a clean story.

Thesis-specific lenses are a stricter post-valuation classification layer. `docs/architecture/thesis_lens_position_mapping_design_v1.md` defines complete thesis lenses such as AI Adoption, Deglobalization, and Geopolitical Bloc, where each in-scope position maps to exactly one primary bucket per lens plus optional non-additive secondary flags. Those thesis buckets classify already-valued positions and impacts; they do not price positions, construct scenario market states, or replace valuation-input coverage rules. Position-to-market-input coverage mapping and scenario-basis construction remain separate internal design areas.

Position assignment shape:

```json
{
  "position_id": "pos_a_ai_compute_leader",
  "primary_theme_id": "ai_infrastructure",
  "secondary_theme_ids": ["china_taiwan_supply_chain", "data_center_infrastructure"],
  "theme_weights": [
    {"theme_id": "ai_infrastructure", "weight": 0.60},
    {"theme_id": "china_taiwan_supply_chain", "weight": 0.25},
    {"theme_id": "data_center_infrastructure", "weight": 0.15}
  ],
  "classification_confidence": "high",
  "assignment_sources": ["identifier_rule", "issuer_rule", "manual_review"],
  "review_status": "approved"
}
```

Theme impact attribution should consume the revaluation result:

```python
def classify_impacts_by_theme(revaluation_results, theme_assignments):
    theme_rows = {}

    for position_result in revaluation_results.position_results:
        assignment = theme_assignments.get(position_result.position_id)
        if assignment is None or not assignment.theme_weights:
            add_unclassified_review_row(theme_rows, position_result)
            continue

        for theme_weight in assignment.theme_weights:
            contribution = position_result.impact * theme_weight.weight
            base_value = position_result.base_value * theme_weight.weight
            scenario_value = position_result.scenario_value * theme_weight.weight
            add_theme_contribution(
                theme_rows,
                theme_id=theme_weight.theme_id,
                base_value=base_value,
                scenario_value=scenario_value,
                impact=contribution,
                confidence=position_result.confidence,
                coverage_status=position_result.coverage_status,
            )

    return summarize_theme_rows(theme_rows)
```

## 9. Coverage, Substitute Inputs, And Confidence

The design should use coverage and confidence language rather than alternate impact-formula language.

Preferred terms:

- valuation coverage;
- approved valuation policy;
- substitute market input;
- look-through limitation;
- review-required treatment;
- confidence tier;
- caveat.

Coverage policy:

- If full revaluation is available, value the position under both market states.
- If an input is missing but a defensible substitute market input is approved, use the approved policy and mark confidence appropriately.
- If look-through is unavailable for a fund, use the approved fund valuation policy and describe the limitation.
- If a private or opaque asset cannot be defensibly valued under the scenario state, use the approved mark/review treatment and route to review as needed.
- Do not pretend that an approximation has the same status as full revaluation.

Coverage status values:

- `valued`
- `valued_with_substitute_input`
- `valued_with_approved_policy`
- `held_at_mark_with_caveat`
- `review_required`
- `not_valued`

Confidence tiers:

- `high`: direct or complete valuation inputs are available and internally consistent.
- `medium`: valued with approved substitute input or incomplete but usable look-through.
- `low`: valuation relies on stale, private, or incomplete policy inputs and should be used directionally.
- `review_required`: position needs human review before relying on point impact.

```python
def score_position_confidence(position, base_value_result, scenario_value_result, coverage_policy):
    statuses = {
        base_value_result.coverage_status,
        scenario_value_result.coverage_status,
    }

    if "review_required" in statuses or "not_valued" in statuses:
        return "review_required"
    if "held_at_mark_with_caveat" in statuses:
        return "low"
    if "valued_with_approved_policy" in statuses:
        return "medium" if coverage_policy.is_strong(position) else "low"
    if "valued_with_substitute_input" in statuses:
        return "medium"
    return "high"
```

```python
def generate_coverage_caveat(position, base_value_result, scenario_value_result):
    status = worst_coverage_status(base_value_result, scenario_value_result)

    if status == "valued":
        return "Position was valued under both base and scenario market states."
    if status == "valued_with_substitute_input":
        return "Position was valued with an approved substitute market input; use the result directionally."
    if status == "valued_with_approved_policy":
        return "Position was valued with an approved policy because complete look-through was unavailable."
    if status == "held_at_mark_with_caveat":
        return "Position was held at an approved mark treatment; scenario impact may understate true exposure."
    return "Position requires review before relying on scenario impact."
```

## 10. Required Pseudocode

### `build_base_market_state()`

```python
def build_base_market_state(valuation_date, market_sources, market_state_schema):
    market_inputs = {}
    confidence = {}
    caveats = []

    for input_family in market_state_schema.required_input_families:
        raw_inputs = market_sources.load(input_family, valuation_date)
        normalized = normalize_market_inputs(input_family, raw_inputs)
        validation = validate_input_family(input_family, normalized)

        market_inputs[input_family.id] = normalized
        confidence[input_family.id] = validation.confidence
        caveats.extend(validation.caveats)

    base_state = {
        "market_state_id": make_market_state_id("base", valuation_date),
        "valuation_date": valuation_date,
        "base_or_scenario": "base",
        "scenario_id": None,
        "market_inputs": market_inputs,
        "data_confidence": confidence,
        "caveats": caveats,
    }
    validate_market_state_consistency(base_state)
    return base_state
```

### `build_scenario_market_state()`

```python
def build_scenario_market_state(base_market_state, scenario_definition, construction_policy):
    scenario_inputs = deep_copy_market_inputs(base_market_state["market_inputs"])

    expanded_changes = {}
    for perturbation in scenario_definition.approved_perturbations:
        if perturbation.kind == "key_rate":
            expanded = expand_key_rate_shocks(
                base_curve=scenario_inputs[perturbation.curve_family],
                key_rate_shocks=perturbation.key_rate_shocks,
                expansion_policy=construction_policy.curve_policy_for(perturbation.curve_family),
            )
            expanded_changes[perturbation.curve_family] = expanded
        else:
            expanded = expand_non_curve_perturbation(
                base_inputs=scenario_inputs,
                perturbation=perturbation,
                construction_policy=construction_policy,
            )
            expanded_changes[perturbation.input_family] = expanded

    scenario_inputs = apply_expanded_market_changes(scenario_inputs, expanded_changes)

    scenario_state = {
        "market_state_id": make_market_state_id("scenario", scenario_definition.scenario_id, base_market_state["valuation_date"]),
        "valuation_date": base_market_state["valuation_date"],
        "base_or_scenario": "scenario",
        "scenario_id": scenario_definition.scenario_id,
        "base_market_state_id": base_market_state["market_state_id"],
        "market_inputs": scenario_inputs,
        "construction_method": scenario_definition.construction_method,
        "approved_perturbations": scenario_definition.approved_perturbations,
        "expanded_changes": expanded_changes,
        "data_confidence": merge_confidence(base_market_state, expanded_changes),
        "caveats": list(scenario_definition.caveats),
    }
    validate_market_state_consistency(scenario_state)
    return scenario_state
```

### `expand_key_rate_shocks()`

```python
def expand_key_rate_shocks(base_curve, key_rate_shocks, expansion_policy):
    shocked_points = {}

    for tenor, base_rate in base_curve.key_tenor_points.items():
        perturbation = key_rate_shocks.get(tenor, 0.0)
        shocked_points[tenor] = base_rate + perturbation

    full_curve = interpolate_curve(
        key_points=shocked_points,
        interpolation_method=expansion_policy.interpolation_method,
        output_tenors=expansion_policy.required_output_tenors,
    )

    full_curve = extrapolate_curve(
        curve=full_curve,
        extrapolation_method=expansion_policy.extrapolation_method,
        min_tenor=expansion_policy.min_tenor,
        max_tenor=expansion_policy.max_tenor,
    )

    curve_validation = validate_curve_shape(
        curve=full_curve,
        base_curve=base_curve,
        consistency_rules=expansion_policy.consistency_rules,
    )

    return {
        "curve": full_curve,
        "source_key_rate_shocks": key_rate_shocks,
        "interpolation_policy": expansion_policy.interpolation_method,
        "extrapolation_policy": expansion_policy.extrapolation_method,
        "validation": curve_validation,
    }
```

### `validate_market_state_consistency()`

```python
def validate_market_state_consistency(market_state):
    issues = []

    issues.extend(validate_required_input_families(market_state["market_inputs"]))
    issues.extend(validate_curve_families(market_state["market_inputs"].get("yield_curves", {})))
    issues.extend(validate_discount_curve_links(market_state["market_inputs"]))
    issues.extend(validate_fx_triangle_consistency(market_state["market_inputs"].get("fx_rates", {})))
    issues.extend(validate_surface_dimensions(market_state["market_inputs"].get("volatility_surfaces", {})))
    issues.extend(validate_private_mark_policies(market_state["market_inputs"].get("private_market_marks", {})))
    issues.extend(validate_calendar_and_settlement_inputs(market_state["market_inputs"].get("calendars", {})))

    if issues:
        market_state["consistency_checks"] = {"status": "review_required", "issues": issues}
        raise MarketStateConsistencyError(issues)

    market_state["consistency_checks"] = {"status": "valid", "issues": []}
    return market_state
```

### `value_position()`

```python
def value_position(position, market_state, valuation_context):
    model = valuation_context.model_registry.select(position)
    required_inputs = model.required_market_inputs(position)
    coverage = check_market_input_coverage(required_inputs, market_state)

    if not coverage.can_value:
        return approved_coverage_treatment(
            position=position,
            market_state=market_state,
            coverage=coverage,
            valuation_context=valuation_context,
        )

    result = model.value(
        position=position,
        market_inputs=market_state["market_inputs"],
        valuation_date=market_state["valuation_date"],
        assumptions=valuation_context.assumptions_for(position),
    )

    return {
        "position_id": position.position_id,
        "market_state_id": market_state["market_state_id"],
        "value": result.value,
        "coverage_status": "valued",
        "valuation_model_id": model.model_id,
        "confidence": result.confidence,
        "caveats": result.caveats,
        "used_inputs": result.used_inputs,
    }
```

### `run_full_portfolio_revaluation()`

```python
def run_full_portfolio_revaluation(portfolio, base_market_state, scenario_market_state, valuation_context):
    position_results = []

    for position in portfolio.positions:
        base_result = value_position(position, base_market_state, valuation_context)
        scenario_result = value_position(position, scenario_market_state, valuation_context)

        confidence = score_position_confidence(
            position,
            base_value_result=base_result,
            scenario_value_result=scenario_result,
            coverage_policy=valuation_context.coverage_policy,
        )

        impact = scenario_result["value"] - base_result["value"]
        position_results.append({
            "position_id": position.position_id,
            "manager_id": position.manager_id,
            "account_id": position.account_id,
            "sleeve_id": position.sleeve_id,
            "base_value": base_result["value"],
            "scenario_value": scenario_result["value"],
            "impact": impact,
            "impact_percent": safe_divide(impact, base_result["value"]),
            "base_coverage_status": base_result["coverage_status"],
            "scenario_coverage_status": scenario_result["coverage_status"],
            "confidence": confidence,
            "caveats": merge_caveats(base_result, scenario_result),
        })

    base_total = sum(row["base_value"] for row in position_results)
    scenario_total = sum(row["scenario_value"] for row in position_results)

    return {
        "base_market_state_id": base_market_state["market_state_id"],
        "scenario_market_state_id": scenario_market_state["market_state_id"],
        "base_portfolio_value": base_total,
        "scenario_portfolio_value": scenario_total,
        "impact": scenario_total - base_total,
        "impact_percent": safe_divide(scenario_total - base_total, base_total),
        "position_results": position_results,
    }
```

### `aggregate_revaluation_results()`

```python
def aggregate_revaluation_results(revaluation_results, grouping_dimensions):
    summaries = {}

    for dimension in grouping_dimensions:
        grouped = group_by(revaluation_results["position_results"], dimension)
        summaries[dimension] = []

        for group_id, rows in grouped.items():
            base_value = sum(row["base_value"] for row in rows)
            scenario_value = sum(row["scenario_value"] for row in rows)
            impact = scenario_value - base_value
            summaries[dimension].append({
                "group_id": group_id,
                "base_value": base_value,
                "scenario_value": scenario_value,
                "impact": impact,
                "impact_percent": safe_divide(impact, base_value),
                "confidence_mix": summarize_confidence(rows),
                "coverage_mix": summarize_coverage(rows),
                "top_positions": top_positions_by_absolute_impact(rows),
            })

    return summaries
```

### `publish_revaluation_bundle()`

```python
def publish_revaluation_bundle(pack, portfolio, base_market_state, scenario_market_state, revaluation_results, attribution):
    bundle = {
        "analytics_run_manifest": {
            "schema_version": "analytics_run_manifest.v1",
            "pack_id": pack.pack_id,
            "pack_version": pack.pack_version,
            "portfolio_id": portfolio.portfolio_id,
            "valuation_date": base_market_state["valuation_date"],
            "base_market_state_id": base_market_state["market_state_id"],
            "scenario_market_state_id": scenario_market_state["market_state_id"],
            "methodology": "full_portfolio_revaluation",
            "synthetic_data": portfolio.synthetic_data,
        },
        "position_revaluation_results": revaluation_results["position_results"],
        "portfolio_revaluation_summary": {
            "base_portfolio_value": revaluation_results["base_portfolio_value"],
            "scenario_portfolio_value": revaluation_results["scenario_portfolio_value"],
            "impact": revaluation_results["impact"],
            "impact_percent": revaluation_results["impact_percent"],
        },
        "scenario_impact_by_theme_manager": attribution["theme_manager"],
        "data_confidence_map": attribution["confidence"],
        "cross_scenario_resilience_summary": attribution.get("cross_scenario_resilience"),
    }
    validate_revaluation_bundle(bundle)
    return bundle
```

## 11. Portfolio Analytics Run

End-to-end internal flow:

```python
def run_internal_analytics(pack_id, portfolio_snapshot, market_sources, options):
    pack = load_approved_pack(pack_id)
    portfolio = normalize_portfolio_snapshot(portfolio_snapshot)
    valuation_context = build_valuation_context(pack, portfolio, options)

    base_market_state = build_base_market_state(
        valuation_date=options.valuation_date,
        market_sources=market_sources,
        market_state_schema=pack.market_state_schema,
    )

    theme_assignments = classify_positions_to_themes(
        positions=portfolio.positions,
        theme_catalog=pack.theme_catalog,
        mapping_rules=pack.classification_rules,
    )

    bundles = []
    for scenario_definition in pack.scenario_catalog:
        scenario_market_state = build_scenario_market_state(
            base_market_state=base_market_state,
            scenario_definition=scenario_definition,
            construction_policy=pack.market_state_construction_policy,
        )

        revaluation_results = run_full_portfolio_revaluation(
            portfolio=portfolio,
            base_market_state=base_market_state,
            scenario_market_state=scenario_market_state,
            valuation_context=valuation_context,
        )

        grouped = aggregate_revaluation_results(
            revaluation_results,
            grouping_dimensions=["manager_id", "account_id", "sleeve_id"],
        )
        theme_rows = classify_impacts_by_theme(revaluation_results, theme_assignments)
        confidence_rows = build_data_confidence_map(revaluation_results, theme_assignments)

        bundles.append(publish_revaluation_bundle(
            pack=pack,
            portfolio=portfolio,
            base_market_state=base_market_state,
            scenario_market_state=scenario_market_state,
            revaluation_results=revaluation_results,
            attribution={
                "grouped": grouped,
                "theme_manager": theme_rows,
                "confidence": confidence_rows,
            },
        ))

    return publish_multi_scenario_index(bundles)
```

## 12. Published Output Bundle

The future internal revaluation bundle should include:

- `analytics_run_manifest.json`
- `base_market_state_summary.json`
- `scenario_market_state_summary.json`
- `position_revaluation_results.json`
- `portfolio_revaluation_summary.json`
- `scenario_impact_by_theme_manager.json`
- `data_confidence_map.json`
- `cross_scenario_resilience_summary.json`

### `position_revaluation_results.json`

Purpose: records base value, scenario value, impact, coverage, confidence, and caveats for each position.

Required fields:

- `position_id`
- `base_market_state_id`
- `scenario_market_state_id`
- `base_value`
- `scenario_value`
- `impact`
- `impact_percent`
- `base_coverage_status`
- `scenario_coverage_status`
- `confidence`
- `caveats`

Not included: advisor-editable model controls, raw credentials, or unapproved market data.

### `portfolio_revaluation_summary.json`

Purpose: records the total base value, total scenario value, total impact, and confidence/coverage summary.

Required fields:

- `base_portfolio_value`
- `scenario_portfolio_value`
- `impact`
- `impact_percent`
- `confidence_mix`
- `coverage_mix`
- `review_required_count`

### `scenario_impact_by_theme_manager.json`

Purpose: aggregates already-valued position impacts by approved theme and manager.

Required fields:

- `scenario_id`
- `scenario_display_name`
- `theme_impacts`
- `manager_impacts`
- `theme_manager_intersections`
- `confidence_mix`
- `coverage_caveats`

### `data_confidence_map.json`

Purpose: identifies valuation coverage limitations, substitute inputs, review-required positions, and advisor-safe caveat language.

Required fields:

- `confidence_buckets`
- `coverage_status_buckets`
- `review_required_positions`
- `affected_themes`
- `affected_managers`
- `advisor_language`

## 13. Advisor-Facing Consumption Rules

The Advisor App consumes approved outputs. It does not construct scenarios or valuations.

Advisor sees:

- approved scenario names;
- approved themes and lenses;
- report-ready base/scenario impact summaries;
- confidence labels;
- caveats and review-required notes;
- advisor-authored workflow sequence.

Advisor does not see:

- model-building tools;
- raw covariance matrices;
- key-rate construction controls;
- valuation model internals;
- shock-vector editing;
- substitute-input rule editors;
- raw analytics JSON in the main product path.

Report language should say, in product terms:

- "The portfolio was revalued under the approved scenario market state."
- "Impact is the difference between scenario value and base value."
- "Theme and manager views attribute that impact after valuation."
- "Coverage notes identify where valuation inputs are incomplete or review is required."

## 14. Implementation Sequencing Recommendation

Next implementation should pause additional advisor UI/report-consumption work until the internal methodology is aligned in code.

Recommended next tranche:

1. If Frank approves implementation, design and implement a full revaluation scenario-engine skeleton using existing synthetic market-state and valuation fixtures.
2. Define or fixture `instrument_catalog`, `position_catalog`, `pricing_function_registry`, and valuation coverage outputs.
3. Define `base_market_state` and `scenario_market_state` input contracts.
4. Add a generic `value_position(position, market_state, valuation_context)` boundary.
5. Produce position-level base/scenario/impact records.
6. Aggregate those records by manager, account, sleeve, theme, thesis lens bucket, and confidence.
7. Publish a revaluation bundle manifest.
8. Only then map the richer bundle back into report-element inputs/views.

Do not add advisor controls, new report views, deployment docs, live data, or external APIs as part of this methodology-alignment step.

## 15. Open Questions For Frank

1. Which asset classes need first-class valuation treatment in the initial skeleton: public equity, fixed income, cash, funds, options/structured products, private funds, or opaque manager books?
2. For private or opaque positions, when should the engine hold an approved mark with caveat versus mark the position review-required?
3. Which scenario should be the first full revaluation proof: AI / Chip Selloff, Rate Shock, or Private Liquidity Freeze?
4. What confidence threshold should block client-facing point impacts and force directional language only?
5. Should report elements show a compact coverage table, or only concise caveat language?
6. Should the next local fixture continue using committed synthetic market states, or should the scenario engine generate scenario market states at run time from approved pack rules?
