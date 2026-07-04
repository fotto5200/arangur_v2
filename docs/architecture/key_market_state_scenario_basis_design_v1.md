# Key Market-State Scenario Basis Design v1

## 1. Purpose And Boundary

This document defines how Arranger constructs complete scenario market states from a small set of key market-state coordinates. It is internal Arranger machinery. It does not implement production code, change app behavior, modify UI, create report views, generate analytics outputs, add backend endpoints, fetch market data, use real client data, or add dependencies.

The scenario basis construction engine has one job:

```text
base_market_state
-> extract approved scenario basis vector
-> apply approved anchor shocks
-> complete the scenario basis vector
-> expand basis coordinates into full market inputs
-> publish scenario_market_state
```

It does not calculate portfolio impact. Full portfolio revaluation remains the only impact methodology:

```text
base_market_state -> value every position -> base_portfolio_value
scenario_market_state -> value every position -> scenario_portfolio_value
impact = scenario_portfolio_value - base_portfolio_value
```

Advisor-facing Arangur consumes approved scenario choices, report-ready outputs, confidence labels, and caveats. Advisors do not manipulate scenario basis models, completion models, covariance/PCA assumptions, anchor shocks, expansion rules, or valuation construction machinery.

## 2. Scenario Basis Model

A Scenario Basis Model is an Arranger-approved reduced coordinate system used to construct coherent scenario market states. It is intentionally smaller than the full market state and intentionally larger than a narrow Treasury key-rate grid.

Required fields:

- `basis_model_id`
- `display_name`
- `purpose`
- `supported_scenario_families`
- `basis_coordinates`
- `coordinate_units`
- `coordinate_representation`
- `covariance_or_completion_model`
- `anchor_shock_rules`
- `expansion_rules`
- `validation_rules`
- `confidence_policy`
- `caveats`
- `approval_status`

Design principles:

- There is no universal basis model.
- Each basis model should fit a purpose and scenario family.
- Basis coordinates should be price-like where possible.
- Completion happens in the reduced basis space.
- Expansion converts the completed basis vector into full market-state inputs.
- Full revaluation happens after the scenario market state is built.

Example shape:

```json
{
  "basis_model_id": "broad_multi_asset_basis_v1",
  "display_name": "Broad Multi-Asset Basis v1",
  "purpose": "Construct broad cross-asset scenario market states from a compact set of price-like coordinates.",
  "supported_scenario_families": ["growth_shock", "rate_shock", "energy_shock", "liquidity_shock"],
  "basis_coordinates": ["sp500_price", "growth_equity_price", "ai_semiconductor_basket_price", "oil_price", "usd_index", "zc_10y_price", "credit_index_price", "private_liquidity_discount"],
  "coordinate_representation": "price_like",
  "covariance_or_completion_model": "deterministic_completion_v1",
  "approval_status": "draft_internal"
}
```

## 3. Price-Coordinate Representation

Basis coordinates should be price-like where possible because scenario completion is more stable when coordinates share comparable interpretation. Price-like does not mean every coordinate is literally traded. It means the coordinate can be interpreted as a level, return, discount factor, index price, or policy index where up/down movement has a consistent economic meaning.

Examples:

- equity index levels or returns;
- growth/AI/semiconductor basket levels;
- commodity prices or commodity index levels;
- FX spot or forward prices;
- Bitcoin or crypto price levels;
- credit index prices;
- zero-coupon bond prices or log discount factors instead of raw yield levels;
- private liquidity discount indices or policy coordinates;
- volatility index or surface-level coordinates where the sign convention is explicit.

Rate coordinates need special care. Raw yield changes can mix awkwardly with equity, commodity, FX, and credit price changes in the same reduced covariance space. For broad multi-asset basis models, rates can be represented through:

- zero-coupon bond prices at key tenors;
- discount factors at key tenors;
- log discount factors;
- synthetic bond prices;
- spread-adjusted price-like credit coordinates.

The final valuation engine still consumes full yield curves, discount curves, spread curves, volatility surfaces, and market levels. The reduced basis is only a scenario construction layer.

## 4. Multiple Basis Models

Arranger should define multiple approved basis models. The examples below are design examples, not a frozen universal list.

### A. Broad Multi-Asset Basis

Purpose: broad portfolio scenario construction across public, private, rate, credit, commodity, crypto, and FX exposures.

Possible basis coordinates:

- broad equity price;
- growth equity price;
- small-cap equity price;
- AI/semiconductor basket price;
- oil/energy price;
- gold price;
- Bitcoin price;
- USD/FX price coordinate;
- zero-coupon bond price coordinates;
- credit index prices;
- private liquidity coordinate.

### B. Rates / Credit / Curve Basis

Purpose: curve, credit, duration, and income-oriented scenario construction.

Possible basis coordinates:

- zero-coupon bond prices or discount factors at key tenors;
- credit index prices;
- spread curve price-like coordinates;
- inflation or breakeven price-like coordinates;
- real-rate curve coordinates;
- liquidity spread coordinate.

### C. Equity / Growth / AI Basis

Purpose: equity, growth, AI infrastructure, semiconductor, and data-center scenario construction.

Possible basis coordinates:

- S&P 500 price;
- NASDAQ or growth equity price;
- semiconductor/AI basket price;
- data-center infrastructure basket price;
- volatility coordinate;
- credit/liquidity coordinate.

### D. Commodity / Energy Basis

Purpose: commodity, power, inflation, and energy-infrastructure scenario construction.

Possible basis coordinates:

- oil price;
- natural gas or power price;
- broad commodities price;
- energy equity index price;
- inflation/breakeven coordinate;
- FX/dollar coordinate.

### E. FX / Global Macro Basis

Purpose: global macro, dollar, currency, and cross-border scenario construction.

Possible basis coordinates:

- USD index;
- EUR/USD;
- JPY/USD;
- EM FX basket;
- rate differential price coordinates;
- commodity-linked currency coordinate.

### F. Private Liquidity / Alternatives Basis

Purpose: private asset liquidity, stale mark, secondary market, and alternatives stress construction.

Possible basis coordinates:

- private liquidity discount;
- secondary-market bid coordinate;
- private credit spread or price coordinate;
- public comparable index price;
- stale-mark policy coordinate.

## 5. Scenario Basis Construction Algorithm

High-level algorithm:

1. Extract the base basis vector from the base market state.
2. Apply scenario anchor shocks to selected basis coordinates.
3. Complete unstated basis coordinates with deterministic rules or a reduced covariance/PCA model.
4. Validate the completed basis vector.
5. Expand the completed basis vector into a full scenario market state.
6. Validate the full market state.
7. Pass the scenario market state to the full revaluation engine.

### `extract_basis_vector(base_market_state, basis_model)`

```python
def extract_basis_vector(base_market_state, basis_model):
    basis_vector = {}
    extraction_notes = []

    for coordinate in basis_model.basis_coordinates:
        source = basis_model.extraction_rules[coordinate.coordinate_id]
        value = read_market_state_coordinate(base_market_state, source)
        normalized = normalize_coordinate_value(
            value=value,
            source_unit=source.unit,
            target_unit=coordinate.unit,
            representation=coordinate.representation,
        )
        basis_vector[coordinate.coordinate_id] = {
            "value": normalized,
            "unit": coordinate.unit,
            "representation": coordinate.representation,
            "source": source.market_state_path,
            "confidence": confidence_for_market_state_path(base_market_state, source.market_state_path),
        }
        extraction_notes.append(source.note)

    return {
        "basis_model_id": basis_model.basis_model_id,
        "base_market_state_id": base_market_state["market_state_id"],
        "coordinates": basis_vector,
        "extraction_notes": extraction_notes,
    }
```

### `apply_anchor_shocks(base_basis_vector, anchor_shocks)`

```python
def apply_anchor_shocks(base_basis_vector, anchor_shocks):
    partial = copy_basis_vector(base_basis_vector)

    for shock in anchor_shocks:
        base_value = base_basis_vector["coordinates"][shock.coordinate_id]["value"]
        shocked_value = apply_coordinate_shock(
            base_value=base_value,
            shock_value=shock.value,
            shock_unit=shock.unit,
            representation=base_basis_vector["coordinates"][shock.coordinate_id]["representation"],
        )
        partial["coordinates"][shock.coordinate_id]["value"] = shocked_value
        partial["coordinates"][shock.coordinate_id]["shock_source"] = shock.shock_id
        partial["coordinates"][shock.coordinate_id]["anchored"] = True

    return partial
```

### `complete_basis_vector(base_basis_vector, partial_shocked_basis, completion_model)`

```python
def complete_basis_vector(base_basis_vector, partial_shocked_basis, completion_model):
    anchored_ids = [
        coordinate_id
        for coordinate_id, row in partial_shocked_basis["coordinates"].items()
        if row.get("anchored") is True
    ]

    completed = copy_basis_vector(partial_shocked_basis)

    if completion_model.method == "deterministic":
        completed = apply_curated_completion_rules(
            base_basis_vector=base_basis_vector,
            partial_shocked_basis=partial_shocked_basis,
            rules=completion_model.rules,
        )
    elif completion_model.method in {"reduced_covariance", "pca"}:
        completed = complete_with_reduced_statistical_model(
            base_basis_vector=base_basis_vector,
            partial_shocked_basis=partial_shocked_basis,
            anchored_coordinate_ids=anchored_ids,
            model=completion_model,
        )
    else:
        raise UnsupportedCompletionModel(completion_model.method)

    completed["completion_method"] = completion_model.method
    completed["anchored_coordinate_ids"] = anchored_ids
    return completed
```

### `validate_basis_vector(base_basis_vector, scenario_basis_vector, basis_model)`

```python
def validate_basis_vector(base_basis_vector, scenario_basis_vector, basis_model):
    issues = []
    caveats = []

    issues.extend(validate_anchor_shock_compatibility(scenario_basis_vector, basis_model.anchor_shock_rules))
    issues.extend(validate_coordinate_magnitude_bounds(base_basis_vector, scenario_basis_vector, basis_model.validation_rules))
    issues.extend(validate_sign_and_shape_rules(base_basis_vector, scenario_basis_vector, basis_model.validation_rules))
    issues.extend(validate_cross_coordinate_plausibility(base_basis_vector, scenario_basis_vector, basis_model.validation_rules))
    issues.extend(validate_scenario_family_consistency(scenario_basis_vector, basis_model.supported_scenario_families))
    caveats.extend(derive_basis_confidence_caveats(scenario_basis_vector, basis_model.confidence_policy))

    status = "valid" if not issues else "review_required"
    return {
        "status": status,
        "issues": issues,
        "caveats": caveats,
    }
```

### `expand_basis_to_market_state(base_market_state, scenario_basis_vector, expansion_rules)`

```python
def expand_basis_to_market_state(base_market_state, scenario_basis_vector, expansion_rules):
    scenario_market_state = copy_market_state(base_market_state)
    scenario_market_state["base_or_scenario"] = "scenario"

    for rule in expansion_rules:
        coordinate_values = select_coordinates(scenario_basis_vector, rule.input_coordinate_ids)

        if rule.expansion_family == "rates":
            update = expand_rate_basis_to_curves(base_market_state, coordinate_values, rule)
        elif rule.expansion_family == "credit":
            update = expand_credit_basis_to_spread_curves(base_market_state, coordinate_values, rule)
        elif rule.expansion_family == "equity":
            update = expand_equity_basis_to_index_levels(base_market_state, coordinate_values, rule)
        elif rule.expansion_family == "commodity":
            update = expand_commodity_basis_to_curves(base_market_state, coordinate_values, rule)
        elif rule.expansion_family == "fx":
            update = expand_fx_basis_to_fx_surface(base_market_state, coordinate_values, rule)
        elif rule.expansion_family == "private_liquidity":
            update = expand_private_liquidity_basis_to_mark_policy(base_market_state, coordinate_values, rule)
        else:
            raise UnsupportedExpansionFamily(rule.expansion_family)

        apply_market_state_update(scenario_market_state, update)

    validate_market_state_consistency(scenario_market_state)
    return scenario_market_state
```

### `construct_scenario_market_state_from_basis()`

```python
def construct_scenario_market_state_from_basis(base_market_state, scenario_definition, basis_model):
    base_basis_vector = extract_basis_vector(base_market_state, basis_model)
    partial_shocked_basis = apply_anchor_shocks(
        base_basis_vector=base_basis_vector,
        anchor_shocks=scenario_definition.anchor_shocks,
    )
    scenario_basis_vector = complete_basis_vector(
        base_basis_vector=base_basis_vector,
        partial_shocked_basis=partial_shocked_basis,
        completion_model=basis_model.covariance_or_completion_model,
    )
    basis_validation = validate_basis_vector(
        base_basis_vector=base_basis_vector,
        scenario_basis_vector=scenario_basis_vector,
        basis_model=basis_model,
    )
    if basis_validation["status"] != "valid":
        require_internal_review(basis_validation)

    scenario_market_state = expand_basis_to_market_state(
        base_market_state=base_market_state,
        scenario_basis_vector=scenario_basis_vector,
        expansion_rules=basis_model.expansion_rules,
    )
    scenario_market_state["scenario_id"] = scenario_definition.scenario_id
    scenario_market_state["basis_model_id"] = basis_model.basis_model_id
    scenario_market_state["basis_validation"] = basis_validation
    return scenario_market_state
```

## 6. Completion Methods

### A. Deterministic v1

Deterministic completion uses anchor shocks plus curated completion rules. It is best for early product review, synthetic demo fixtures, reproducibility, and human review.

Properties:

- no probability claim;
- no forecast claim;
- fully reviewable by Arranger;
- easy to version in an analytic pack;
- appropriate before enough data exists for stable reduced covariance or PCA estimates.

Examples:

- AI/semiconductor basket down implies growth equity down and volatility up by curated policy.
- Oil up implies energy equity up, inflation/breakeven coordinate up, and USD coordinate rule-driven by scenario family.
- Private liquidity discount wider implies stale-mark caveats and private credit price coordinate lower.

### B. Reduced Covariance / PCA v1.5 Or v2

Reduced covariance/PCA completion estimates relationships across basis coordinates, not across thousands of instruments.

Properties:

- covariance lives in reduced basis space;
- model conditions on anchor shocks;
- remaining basis coordinates are completed from the reduced model;
- PCA/factor compression can be used where appropriate;
- plausibility validation remains mandatory;
- output is an approved representative scenario basis and scenario market state;
- advisor never manipulates the covariance/PCA model.

This model can publish:

- completed basis vector;
- completion method and model version;
- confidence/caveat policy;
- representative scenario market state;
- optional internal diagnostics that are not advisor-facing.

## 7. Expansion Layer

Expansion converts completed basis coordinates into full valuation inputs. The expansion layer is the bridge between reduced scenario construction and full revaluation.

Examples:

- bond-price or discount-factor coordinates -> full yield/discount curves;
- credit index price coordinates -> credit spread curves;
- equity index/basket coordinates -> equity/index levels and related surfaces;
- commodity coordinates -> commodity curves or levels;
- FX coordinates -> FX rate matrix and forwards;
- volatility coordinate -> volatility surface shift policy;
- private liquidity coordinate -> private mark/liquidity policy.

### `expand_rate_basis_to_curves()`

```python
def expand_rate_basis_to_curves(base_market_state, coordinate_values, expansion_rule):
    discount_factors = convert_price_like_rate_coordinates_to_discount_factors(coordinate_values)
    full_curve = interpolate_and_extrapolate_curve(
        anchor_points=discount_factors,
        curve_policy=expansion_rule.curve_policy,
    )
    return {
        "market_state_path": expansion_rule.target_curve_path,
        "value": full_curve,
        "caveats": expansion_rule.caveats,
    }
```

### `expand_credit_basis_to_spread_curves()`

```python
def expand_credit_basis_to_spread_curves(base_market_state, coordinate_values, expansion_rule):
    spread_changes = infer_spread_curve_changes_from_credit_prices(coordinate_values, expansion_rule)
    full_spread_curve = apply_spread_changes(
        base_curve=read_market_state_path(base_market_state, expansion_rule.base_spread_curve_path),
        spread_changes=spread_changes,
    )
    return {
        "market_state_path": expansion_rule.target_spread_curve_path,
        "value": full_spread_curve,
        "caveats": expansion_rule.caveats,
    }
```

### `expand_equity_basis_to_index_levels()`

```python
def expand_equity_basis_to_index_levels(base_market_state, coordinate_values, expansion_rule):
    index_updates = {}
    for coordinate_id, coordinate_value in coordinate_values.items():
        target_index = expansion_rule.coordinate_to_index[coordinate_id]
        index_updates[target_index] = coordinate_value["value"]
    return {
        "market_state_path": "market_inputs.equity_index_levels",
        "value": index_updates,
        "caveats": expansion_rule.caveats,
    }
```

### `expand_commodity_basis_to_curves()`

```python
def expand_commodity_basis_to_curves(base_market_state, coordinate_values, expansion_rule):
    commodity_curve_updates = {}
    for coordinate_id, coordinate_value in coordinate_values.items():
        curve_id = expansion_rule.coordinate_to_curve[coordinate_id]
        commodity_curve_updates[curve_id] = apply_curve_shift_policy(
            base_curve=read_market_state_path(base_market_state, curve_id),
            anchor_price=coordinate_value["value"],
            policy=expansion_rule.curve_policy,
        )
    return {
        "market_state_path": "market_inputs.commodity_curves",
        "value": commodity_curve_updates,
        "caveats": expansion_rule.caveats,
    }
```

### `expand_fx_basis_to_fx_surface()`

```python
def expand_fx_basis_to_fx_surface(base_market_state, coordinate_values, expansion_rule):
    fx_updates = build_consistent_fx_matrix(
        base_fx=read_market_state_path(base_market_state, "market_inputs.fx_rates"),
        coordinate_values=coordinate_values,
        policy=expansion_rule.fx_consistency_policy,
    )
    return {
        "market_state_path": "market_inputs.fx_rates",
        "value": fx_updates,
        "caveats": expansion_rule.caveats,
    }
```

### `expand_private_liquidity_basis_to_mark_policy()`

```python
def expand_private_liquidity_basis_to_mark_policy(base_market_state, coordinate_values, expansion_rule):
    policy_update = {
        "private_liquidity_discount": coordinate_values["private_liquidity_discount"]["value"],
        "secondary_bid_policy": expansion_rule.secondary_bid_policy,
        "stale_mark_treatment": expansion_rule.stale_mark_treatment,
        "review_required_threshold": expansion_rule.review_required_threshold,
    }
    return {
        "market_state_path": "market_inputs.private_market_marks",
        "value": policy_update,
        "caveats": expansion_rule.caveats,
    }
```

## 8. Validation Rules

### A. Basis-Vector Validation

Basis-vector validation checks the reduced scenario before expansion.

Required checks:

- anchor shock compatibility;
- coordinate magnitude bounds;
- sign and shape checks;
- cross-coordinate plausibility;
- scenario-family consistency;
- coordinate confidence flags;
- caveat policy.

Examples:

- A growth selloff scenario should not leave growth equity unchanged unless explicitly explained.
- A private liquidity freeze should include private liquidity or secondary-market discount movement.
- A rates/curve basis should preserve plausible curve shape rules after key tenor changes.
- A broad multi-asset basis should not mix contradictory FX and rate-differential movements without review.

### B. Full Market-State Validation

Full market-state validation checks the expanded valuation input set.

Required checks:

- required input coverage;
- curve consistency;
- surface consistency;
- FX consistency;
- discount curve consistency;
- private mark policy validity;
- scenario metadata completeness;
- data confidence/source metadata completeness.

Full market-state validation must pass, or route to internal review, before the state is passed to full revaluation.

## 9. Interaction With Full Revaluation

Scenario basis construction ends by publishing a scenario market state. Full revaluation begins after that.

Sequence:

1. Basis model constructs scenario market state.
2. Valuation models consume market-state inputs.
3. Every position is valued under base and scenario states.
4. Portfolio impact equals scenario valuation minus base valuation.
5. Attribution by position, manager, sleeve, account, theme, and confidence happens after valuation.

The reduced basis vector is not a portfolio impact model. It is an internal construction layer for coherent scenario market states.

## 10. Interaction With Themes And Position Mapping

Themes are not part of scenario basis construction.

Themes:

- classify positions;
- support post-valuation attribution;
- support advisor/client explanation;
- help identify hidden concentrations;
- do not price positions;
- do not determine scenario market-state construction.

Position-to-theme mapping and position-to-market-input coverage require a separate design discussion. The next design tranche should address how positions map to valuation inputs, substitute inputs, coverage rules, and themes.

## 11. Implementation Sequencing Recommendation

Recommended implementation sequence:

A. Define scenario basis contract files.

B. Add one Broad Multi-Asset Basis fixture.

C. Add deterministic basis extraction, completion, and validation.

D. Add expansion from basis vector to simple synthetic market state.

E. Add scenario market-state manifest.

F. Then add full revaluation skeleton.

G. Then return to report consumption.

This sequencing keeps the architecture honest: basis construction produces market states, full revaluation calculates impacts, and report consumption renders approved outputs.

## 12. Open Questions For Frank

1. Which basis model should be implemented first: Broad Multi-Asset, Rates/Credit, or Equity/AI?
2. Should rate coordinates be zero-coupon bond prices, discount factors, or synthetic bond prices in v1?
3. How many basis coordinates should v1 allow before PCA/covariance reliability becomes questionable?
4. Should deterministic completion precede covariance/PCA completion, or should reduced covariance be included in the first skeleton?
5. Which non-rate coordinates are essential in the first demo: S&P, NASDAQ, AI/chip, oil, gold, Bitcoin, USD, credit, private liquidity?
6. How much scenario-basis construction metadata should be published into analytic packs versus kept internal?
