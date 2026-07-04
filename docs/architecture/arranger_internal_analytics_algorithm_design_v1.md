# Arranger Internal Analytics Algorithm Design v1

## 1. Purpose And Boundary

This document defines the first algorithmic design for the Arranger Internal Analytic Studio / Control Plane. It is a design packet, not an implementation. It does not change app behavior, advisor UI, backend endpoints, Docker, deployment, live data, or dependencies.

The boundary is:

- Arranger Internal Analytic Studio / Control Plane owns analytic construction: scenario design, driver shocks, covariance/key-rate methodology, theme taxonomy, classification rules, proxy policy, data-confidence policy, and approved report capability maps.
- Arangur Advisor App consumes approved analytic packs and analytics bundles. It lets advisors select approved scenarios, themes, lenses, scopes, and report elements.
- Advisors do not create market-state vectors, key-rate shock curves, covariance matrices, PCA/factor models, scenario shock vectors, theme taxonomies, classification rules, proxy rules, or confidence rules.

Three decision layers must stay separate:

| Layer | Owner | Examples | Advisor-facing? |
| --- | --- | --- | --- |
| Pre-authored by Arranger | Control plane | Theme catalog, classification lenses, scenario catalog, deterministic shock vectors, covariance model metadata, confidence rules, report capability map | Only approved labels, stories, caveats, and supported choices |
| Calculated at portfolio run | Internal analytics module | Position-theme assignments, proxy assignments, confidence scores, scenario impacts, overlap/resilience summaries, run manifest | Only summarized through approved report elements |
| Selected by advisor | Arangur Advisor App | Approved scenario, theme focus, lens, scope, report element sequence, narrative sections | Yes |

Current repo baseline:

- `data/analytic_packs/arranger_demo_pack_v1/` contains the current synthetic approved pack.
- `src/arangur/analytics/apply_demo_pack.py` is a deterministic proof mapper over committed synthetic fixtures.
- `data/simulation/analytics/` contains local-only proof outputs.

This document describes the intended internal algorithms behind that proof layer. It preserves the current publish-consume boundary: the Advisor App consumes outputs, not construction tools.

## 2. Key-Rate / Scenario Construction Algorithm

### 2.1 Market State Vector

A market state vector is the internal representation of scenario-relevant drivers at a point in time. It should be explicit, versioned, and unit-aware.

Required fields:

- `market_state_id`
- `as_of_date`
- `horizon`
- `driver_values`
- `driver_units`
- `driver_confidence`
- `driver_sources`
- `driver_covariance_group`
- `synthetic_or_live_data_flag`
- `model_version`

Typical drivers:

- Rates: overnight, 2Y, 5Y, 10Y, 30Y, real rates, breakevens.
- Credit: IG spread, HY spread, private credit spread proxy.
- Equities: broad equity, growth/tech, semiconductors, quality/defensive, small cap.
- FX: broad USD, EUR/USD, JPY/USD.
- Commodities/real assets: oil, gas, power, copper, broad commodities, real estate cap-rate proxy.
- Volatility/liquidity: equity volatility, rates volatility, private-market liquidity, secondary-market discount.
- Thematic drivers: AI infrastructure/semiconductor, data center power, Taiwan supply-chain disruption.

```python
def build_market_state_vector(as_of_date, market_inputs, driver_catalog):
    state = {
        "as_of_date": as_of_date,
        "driver_values": {},
        "driver_units": {},
        "driver_confidence": {},
        "driver_sources": {},
        "missing_drivers": [],
    }

    for driver in driver_catalog:
        observation = market_inputs.get(driver.driver_id)
        if observation is None:
            state["missing_drivers"].append(driver.driver_id)
            state["driver_confidence"][driver.driver_id] = "missing"
            continue

        state["driver_values"][driver.driver_id] = normalize_unit(
            observation.value,
            observation.unit,
            driver.required_unit,
        )
        state["driver_units"][driver.driver_id] = driver.required_unit
        state["driver_confidence"][driver.driver_id] = score_driver_confidence(observation)
        state["driver_sources"][driver.driver_id] = observation.source_id

    validate_required_drivers(state, driver_catalog)
    return state
```

### 2.2 Scenario Construction Levels

#### A. Simple Deterministic v1

The simple v1 engine publishes curated shock vectors across named drivers. It does not need a live covariance engine. It is useful for local demo, early product review, and deterministic report fragments.

Inputs:

- Approved scenario catalog.
- Approved shock vectors.
- Driver catalog and units.
- Optional qualitative assumptions.
- Plausibility constraints.

Outputs:

- Scenario market state deltas by driver.
- Scenario metadata and caveats.
- Supported report element mapping.

Properties:

- Deterministic.
- Reviewable by Frank and Arranger.
- Easy to version and reproduce.
- Does not claim probability, forecast, VaR, or live-market calibration.

```python
def define_scenario_driver_shocks(scenario_id, scenario_catalog, shock_pack):
    scenario = scenario_catalog.require(scenario_id)
    shock = shock_pack.require_for_scenario(scenario_id)

    driver_shocks = {}
    for driver_id, shock_spec in shock.variable_shocks.items():
        driver_shocks[driver_id] = {
            "delta": shock_spec.delta,
            "unit": shock_spec.unit,
            "direction": shock_spec.direction,
            "confidence": shock.confidence_level,
            "source": "curated_arranger_pack",
        }

    return {
        "scenario_id": scenario_id,
        "horizon": scenario.default_horizon,
        "driver_shocks": driver_shocks,
        "qualitative_assumptions": shock.qualitative_assumptions,
        "caveats": scenario.caveats + shock.caveats,
    }
```

#### B. Full Covariance / Key-Rate v2

The full v2 engine adds conditional propagation. It starts with one or more anchored shocks, then uses a covariance/correlation model, PCA model, or factor model to propagate related driver moves.

Inputs:

- Market state vector.
- Driver covariance or correlation matrix.
- Factor/PCA model and loadings, if used.
- Scenario anchor shocks.
- Driver bounds and plausibility constraints.
- Historical stress library, if approved.

Outputs:

- Representative shocked market state.
- Conditional propagated shocks.
- Optional scenario cloud/distribution.
- Summary statistics: median, p10/p90, worst plausible path, factor attribution.
- Published scenario pack with only approved representative path/statistics.

Key principle: the Advisor App still receives approved scenario choices and report-ready outputs, not the covariance matrix or model controls.

```python
def propagate_shocks_through_covariance(base_state, anchor_shocks, covariance_model):
    driver_ids = covariance_model.driver_ids
    known = vectorize(anchor_shocks, driver_ids)
    unknown_driver_ids = [d for d in driver_ids if d not in anchor_shocks]

    conditional_mean = condition_multivariate_normal(
        mean=covariance_model.mean_vector,
        covariance=covariance_model.covariance_matrix,
        observed=known,
        observed_driver_ids=list(anchor_shocks.keys()),
        target_driver_ids=unknown_driver_ids,
    )

    propagated = dict(anchor_shocks)
    for driver_id, delta in zip(unknown_driver_ids, conditional_mean):
        propagated[driver_id] = {
            "delta": delta,
            "unit": covariance_model.driver_units[driver_id],
            "direction": sign_label(delta),
            "confidence": covariance_model.driver_confidence[driver_id],
            "source": "conditional_covariance_propagation",
        }

    return propagated
```

```python
def validate_scenario_plausibility(base_state, shocked_state, constraints):
    issues = []

    for rule in constraints.driver_bounds:
        value = shocked_state.driver_values.get(rule.driver_id)
        if value is not None and not rule.min_value <= value <= rule.max_value:
            issues.append(("driver_bound", rule.driver_id, value))

    for rule in constraints.curve_shape_rules:
        curve = extract_curve(shocked_state, rule.curve_driver_ids)
        if not rule.accepts(curve):
            issues.append(("curve_shape", rule.rule_id, curve))

    for rule in constraints.cross_driver_rules:
        if not rule.accepts(shocked_state.driver_values):
            issues.append(("cross_driver", rule.rule_id, rule.description))

    status = "valid" if not issues else "review_required"
    return {"status": status, "issues": issues}
```

```python
def publish_scenario_pack(base_state, scenario, propagated_shocks, validation):
    if validation["status"] != "valid":
        require_internal_approval(validation["issues"])

    representative_state = apply_driver_shocks(base_state, propagated_shocks)
    return {
        "scenario_id": scenario.scenario_id,
        "display_name": scenario.display_name,
        "horizon": scenario.horizon,
        "driver_shocks": propagated_shocks,
        "representative_market_state": representative_state,
        "construction_method": scenario.construction_method,
        "model_version": scenario.model_version,
        "approval_status": "approved_for_pack",
        "advisor_story": scenario.advisor_story,
        "caveats": scenario.caveats,
    }
```

### 2.3 Shock Constraints

Every scenario should carry constraints before publication:

- Unit constraints: bps for rates/spreads, percent returns for risk assets, index-level percent moves for proxies.
- Sign constraints: e.g. rate shock should not lower all key rates unless explicitly named as a rally.
- Curve constraints: parallel, steepener, flattener, twist, or custom key-rate move.
- Cross-driver constraints: e.g. AI/chip selloff should usually include higher volatility; energy shock should usually include oil/power moves.
- Magnitude constraints: driver-level min/max and aggregate scenario severity.
- Horizon constraints: short shock, 3-month, 12-month, or structural.
- Confidence constraints: low-confidence propagated drivers require caveats or exclusion from advisor-facing claims.

## 3. Scenario Catalog Design

Required scenario fields:

- `scenario_id`
- `display_name`
- `scenario_family`
- `short_description`
- `advisor_story`
- `default_horizon`
- `supported_horizons`
- `primary_drivers`
- `anchor_shocks`
- `propagated_drivers`
- `shock_units`
- `affected_themes`
- `expected_direction_by_theme`
- `supported_report_elements`
- `confidence_level`
- `construction_method`
- `plausibility_constraints`
- `caveats`
- `approval_status`
- `pack_version`

Recommended initial scenario library:

| Scenario | Scenario ID | Primary anchors | Typical propagated drivers | Notes |
| --- | --- | --- | --- | --- |
| AI / Chip Selloff | `ai_chip_selloff` | Semiconductor/AI infrastructure equity, growth tech, volatility | Broad equity, credit spreads, private liquidity | Existing demo scenario. Highlights hidden AI and semiconductor concentration. |
| Rate Shock | `rate_shock` | 2Y/10Y/30Y rates, long-duration bond price | Credit spreads, private liquidity, volatility | Existing demo scenario. v2 should move key rates directly before price effects. |
| Curve Steepening | `curve_steepening` | 2Y down/flat, 10Y and 30Y up | Banks, duration, real estate cap-rate proxy | Adds key-rate curve shape beyond simple parallel shock. |
| Energy Shock | `energy_shock` | Oil, gas/power, energy equities | Inflation breakevens, USD, broad equity, real assets | Existing demo scenario. Useful for inflation and infrastructure themes. |
| Private Liquidity Freeze | `private_market_liquidity_freeze` | Private liquidity discount, secondary-market bid, credit spread | Volatility, stale marks, private equity/credit valuation haircuts | Existing demo scenario. Low confidence by design. |
| Taiwan Disruption | `taiwan_disruption` | Semiconductor supply chain, Taiwan/geopolitical risk | AI infrastructure, energy, USD, private liquidity | Existing demo scenario. Requires careful caveats. |
| Credit Spread Widening | `credit_spread_widening` | IG/HY/private credit spreads | Broad equity, rates, private liquidity | Needed for credit and income manager review. |
| Inflation Persistence | `inflation_persistence` | Breakevens, real rates, commodities, wage/price proxy | Rates, real assets, consumer demand, duration | Useful for real assets and spending sensitivity. |

## 4. Theme / Classification Schema Design

Definitions:

- Theme taxonomy: Arranger-approved non-exclusive investment themes, such as AI Infrastructure, Rate Sensitivity, Private Market Liquidity, Energy Security, Credit Stress, Dollar Exposure, China/Taiwan Supply Chain, Real Asset Inflation Hedge, Data Center Infrastructure, Consumer Demand Sensitivity, Duration Exposure, and Defensive Cash Flow.
- Classification lens: A way to view the portfolio. Examples: Strategic Theme, Manager Role / Mandate, Liquidity Profile, Data Confidence.
- Report lens: A report-element-specific use of a classification lens. Example: Manager Comparison may use Manager Role / Mandate, while Data Confidence Note uses Data Confidence.
- Advisor-facing category: The label exposed in the Advisor App, chosen from approved pack metadata.
- Internal mapping rule: Deterministic or reviewed rule that assigns positions to themes/categories based on identifiers, issuer, sector, asset class, manager mandate, look-through, tags, or overrides.

Mutual exclusivity:

- Strategic themes are non-exclusive. One position can have multiple themes.
- Some report allocation views need weights that sum to 1. These should use `theme_weight` assignments.
- Some lenses are mutually exclusive by design. Example: a position should have one primary liquidity bucket.
- Some lenses allow multiple tags. Example: a manager can be both growth equity and AI infrastructure specialist.

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
  "assignment_sources": ["ticker_rule", "sector_rule", "manual_review"],
  "review_status": "approved"
}
```

Unresolved positions must stay explicit:

- `primary_theme_id = null`
- `theme_weights = []`
- `classification_confidence = low`
- `review_status = review_required`
- `review_reason` explains what is missing.

## 5. Position-To-Theme Mapping Algorithm

Inputs:

- Normalized position: id, display name, ticker, CUSIP/ISIN if available, issuer, manager, sleeve, account, asset class, instrument type, sector, industry, geography, currency, market value, tags, scenario hints, valuation tier, confidence flags.
- Theme catalog.
- Mapping rules.
- Manual overrides.
- Optional look-through holdings or manager exposure file.

Precedence:

1. Manual override approved by Arranger.
2. Exact identifier/ticker/issuer rule.
3. Fund or index look-through rule.
4. Sector/industry/geography rule.
5. Manager/sleeve/mandate rule.
6. Text/tag/scenario-hint rule.
7. Fallback to unresolved review.

```python
def classify_position_to_themes(position, theme_catalog, mapping_rules):
    candidates = []

    candidates += apply_manual_overrides(position, mapping_rules.manual_overrides)
    candidates += apply_ticker_or_issuer_rules(position, mapping_rules.identifier_rules)
    candidates += apply_fund_lookthrough_rules(position, mapping_rules.lookthrough_rules)
    candidates += apply_sector_industry_rules(position, mapping_rules.sector_rules)
    candidates += apply_manager_sleeve_rules(position, mapping_rules.manager_rules)
    candidates += apply_tag_rules(position, mapping_rules.tag_rules)

    candidates = remove_invalid_theme_ids(candidates, theme_catalog)
    if not candidates:
        return route_unclassified_positions_to_review(position)

    weighted = assign_theme_weights(position, candidates)
    confidence = calculate_assignment_confidence(position, weighted)

    return {
        "position_id": position.position_id,
        "primary_theme_id": weighted[0].theme_id,
        "secondary_theme_ids": [item.theme_id for item in weighted[1:]],
        "theme_weights": [item.to_dict() for item in weighted],
        "classification_confidence": confidence,
        "assignment_sources": unique_sources(weighted),
        "review_status": "approved" if confidence != "low" else "review_recommended",
    }
```

```python
def apply_manual_overrides(position, overrides):
    override = overrides.get(position.position_id) or overrides.get(position.instrument_id)
    if override is None:
        return []

    return [
        CandidateTheme(
            theme_id=item.theme_id,
            raw_weight=item.weight,
            source="manual_override",
            confidence="high",
            rationale=override.rationale,
        )
        for item in override.theme_assignments
    ]
```

```python
def apply_ticker_or_issuer_rules(position, identifier_rules):
    keys = [
        position.ticker,
        position.issuer_id,
        position.instrument_id,
        position.cusip,
        position.isin,
    ]
    candidates = []
    for key in keys:
        if key and key in identifier_rules:
            candidates += identifier_rules[key].theme_candidates
    return candidates
```

```python
def apply_sector_industry_rules(position, sector_rules):
    rule_keys = [
        (position.asset_class, position.sector, position.industry),
        (position.asset_class, position.sector, None),
        (position.asset_class, None, None),
    ]
    for key in rule_keys:
        if key in sector_rules:
            return sector_rules[key].theme_candidates
    return []
```

```python
def apply_manager_sleeve_rules(position, manager_rules):
    keys = [
        (position.manager_id, position.sleeve_id),
        (position.manager_id, position.mandate_id),
        (position.manager_id, None),
    ]
    candidates = []
    for key in keys:
        if key in manager_rules:
            candidates += manager_rules[key].theme_candidates
    return candidates
```

```python
def assign_theme_weights(position, candidates):
    manual = [c for c in candidates if c.source == "manual_override"]
    source = manual if manual else candidates

    scored = []
    for candidate in source:
        score = candidate.raw_weight or score_candidate_strength(position, candidate)
        scored.append((candidate.theme_id, score, candidate.source, candidate.confidence))

    by_theme = combine_duplicate_theme_scores(scored)
    total = sum(max(item.score, 0.0) for item in by_theme)
    if total <= 0:
        return []

    weighted = [
        ThemeWeight(
            theme_id=item.theme_id,
            weight=item.score / total,
            source=item.source,
            confidence=item.confidence,
        )
        for item in by_theme
    ]
    return sorted(weighted, key=lambda item: item.weight, reverse=True)
```

```python
def calculate_assignment_confidence(position, weighted_assignments):
    if not weighted_assignments:
        return "low"

    source_scores = {
        "manual_override": 1.00,
        "identifier_rule": 0.95,
        "issuer_rule": 0.90,
        "lookthrough_rule": 0.85,
        "sector_rule": 0.70,
        "manager_rule": 0.60,
        "tag_rule": 0.55,
    }
    weighted_score = sum(
        assignment.weight * source_scores.get(assignment.source, 0.40)
        for assignment in weighted_assignments
    )

    if position.valuation_tier in {"human_review_required", "stale_or_manager_mark"}:
        weighted_score -= 0.15
    if position.asset_class in {"opaque_manager_level", "private_equity", "private_credit"}:
        weighted_score -= 0.10

    if weighted_score >= 0.80:
        return "high"
    if weighted_score >= 0.55:
        return "medium"
    return "low"
```

```python
def route_unclassified_positions_to_review(position):
    return {
        "position_id": position.position_id,
        "primary_theme_id": None,
        "secondary_theme_ids": [],
        "theme_weights": [],
        "classification_confidence": "low",
        "assignment_sources": [],
        "review_status": "review_required",
        "review_reason": "No approved mapping rule matched this position.",
    }
```

Examples:

- Nvidia-like public equity: exact ticker/issuer rule maps primarily to AI Infrastructure, secondarily to China/Taiwan Supply Chain and Data Center Infrastructure. Confidence should be high if market value and identifier data are direct.
- AI chip ETF: ETF look-through maps to AI Infrastructure and China/Taiwan Supply Chain, with medium confidence unless holdings are current and complete.
- Opaque private fund: manager mandate maps to Private Market Liquidity and possibly Data Center Infrastructure, with low or medium classification confidence depending on look-through. Position should keep a caveat and may route to review.
- Manager-level private book: manager/sleeve rule can assign high-level themes, but `review_status` should remain review_required if holdings are absent.

## 6. Proxy Assignment Algorithm

Proxy assignment estimates exposures when direct valuation or scenario sensitivity is unavailable. It must be explicit and caveated.

Proxy hierarchy:

1. Direct instrument pricing and sensitivity.
2. Public ticker comparable.
3. ETF or index proxy.
4. Factor proxy.
5. Manager mandate proxy.
6. Sector/geography proxy.
7. Stale/private mark proxy.
8. Unacceptable proxy, route to review.

Proxy quality inputs:

- Asset-class match.
- Economic exposure match.
- Geography/currency match.
- Liquidity/horizon match.
- Data freshness.
- Look-through coverage.
- Manager mandate specificity.
- Scenario driver coverage.
- Historical fit, if available.
- Human override status.

```python
def choose_proxy_for_position(position, proxy_catalog, scenario_driver_ids):
    if has_direct_sensitivity(position, scenario_driver_ids):
        return direct_proxy(position)

    candidates = []
    candidates += public_ticker_comparables(position, proxy_catalog)
    candidates += etf_or_index_proxies(position, proxy_catalog)
    candidates += factor_proxies(position, proxy_catalog)
    candidates += manager_mandate_proxies(position, proxy_catalog)
    candidates += sector_geography_proxies(position, proxy_catalog)
    candidates += stale_private_mark_proxies(position, proxy_catalog)

    scored = [
        score_proxy_quality(position, candidate, scenario_driver_ids)
        for candidate in candidates
    ]
    scored = [candidate for candidate in scored if candidate.score >= proxy_catalog.minimum_score]

    if not scored:
        return unacceptable_proxy(position, "No proxy met minimum quality threshold.")

    best = max(scored, key=lambda candidate: candidate.score)
    if best.requires_human_review:
        best.review_status = "review_required"
    return best
```

```python
def score_proxy_quality(position, proxy, scenario_driver_ids):
    score = 0.0
    score += 0.25 * match_asset_class(position, proxy)
    score += 0.25 * match_economic_exposure(position, proxy)
    score += 0.15 * match_geography_currency(position, proxy)
    score += 0.15 * match_scenario_driver_coverage(proxy, scenario_driver_ids)
    score += 0.10 * score_data_freshness(proxy)
    score += 0.10 * score_lookthrough_coverage(position, proxy)

    if position.valuation_tier == "stale_or_manager_mark":
        score -= 0.10
    if position.asset_class == "opaque_manager_level":
        score -= 0.20
    if proxy.source == "manual_override":
        score += 0.10

    tier = "high" if score >= 0.80 else "medium" if score >= 0.55 else "low"
    return proxy.with_score(score=score, quality_tier=tier)
```

```python
def apply_proxy_exposure(position, proxy, shock_vector):
    if proxy.quality_tier == "unacceptable":
        return {
            "position_id": position.position_id,
            "scenario_impact": None,
            "confidence": "review_required",
            "caveat": generate_proxy_caveat(position, proxy),
        }

    beta = proxy.beta_to_driver or 1.0
    driver_delta = shock_vector.get(proxy.driver_id, 0.0)
    impact_percent = beta * driver_delta

    return {
        "position_id": position.position_id,
        "proxy_id": proxy.proxy_id,
        "driver_id": proxy.driver_id,
        "impact_percent": impact_percent,
        "scenario_impact": position.market_value * impact_percent,
        "confidence": proxy.quality_tier,
        "caveat": generate_proxy_caveat(position, proxy),
    }
```

```python
def generate_proxy_caveat(position, proxy):
    if proxy.quality_tier == "high":
        return "Direct or close proxy used for scenario sensitivity."
    if proxy.quality_tier == "medium":
        return "Scenario sensitivity uses a proxy; interpretation should focus on direction and relative exposure."
    if proxy.quality_tier == "low":
        return "Scenario sensitivity is approximate because the position lacks direct or close look-through data."
    return "No acceptable proxy is available; this position should be reviewed before relying on scenario impact."
```

Unacceptable proxy triggers:

- No economic relationship to scenario drivers.
- Missing market value or notional.
- Unclear long/short exposure.
- Option-like payoff without approved approximation.
- Opaque manager-level book with no mandate or look-through.
- Stale private mark with no review or policy-approved proxy.

## 7. Data Confidence / Opacity Algorithm

Data confidence is an analytic output, not a cosmetic label. It controls caveats, review routing, and whether report elements may present results as directional only.

Inputs:

- Valuation source.
- Data freshness.
- Identifier completeness.
- Position type and asset class.
- Direct vs proxy valuation.
- Proxy quality.
- Classification confidence.
- Scenario driver coverage.
- Human review flag.
- Stale/private mark status.
- Look-through coverage.

Outputs:

- `high`
- `medium`
- `low`
- `review_required`

```python
def score_position_confidence(position, classification, proxy_assignment):
    score = 1.0

    if position.valuation_tier == "direct_price_or_mark":
        score -= 0.00
    elif position.valuation_tier == "cash_face_value":
        score -= 0.05
    elif position.valuation_tier == "proxy_valuation":
        score -= 0.20
    elif position.valuation_tier == "stale_or_manager_mark":
        score -= 0.35
    elif position.valuation_tier == "human_review_required":
        score -= 0.50
    else:
        score -= 0.40

    if position.is_stale:
        score -= 0.15
    if position.human_review_required:
        score -= 0.30
    if classification.classification_confidence == "medium":
        score -= 0.10
    if classification.classification_confidence == "low":
        score -= 0.25
    if proxy_assignment.quality_tier == "medium":
        score -= 0.10
    if proxy_assignment.quality_tier == "low":
        score -= 0.25
    if proxy_assignment.quality_tier == "unacceptable":
        return "review_required"

    if position.human_review_required or score < 0.35:
        return "review_required"
    if score >= 0.80:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"
```

```python
def aggregate_confidence_by_theme(position_confidence_rows, theme_assignments):
    buckets_by_theme = {}

    for row in position_confidence_rows:
        assignments = theme_assignments[row.position_id].theme_weights
        for assignment in assignments:
            exposure = row.market_value * assignment.weight
            bucket = row.confidence_bucket
            buckets_by_theme.setdefault(assignment.theme_id, Counter())
            buckets_by_theme[assignment.theme_id][bucket] += exposure

    return {
        theme_id: summarize_confidence_counter(counter)
        for theme_id, counter in buckets_by_theme.items()
    }
```

```python
def aggregate_confidence_by_manager(position_confidence_rows):
    buckets_by_manager = {}

    for row in position_confidence_rows:
        counter = buckets_by_manager.setdefault(row.manager_id, Counter())
        counter[row.confidence_bucket] += row.market_value

    return {
        manager_id: summarize_confidence_counter(counter)
        for manager_id, counter in buckets_by_manager.items()
    }
```

```python
def generate_advisor_confidence_language(confidence_summary):
    if confidence_summary.review_required_percent >= 0.15:
        return "A meaningful share of this view depends on positions that need review before relying on exact scenario impact."
    if confidence_summary.low_percent >= 0.20:
        return "Several positions use approximate or stale inputs; use the result directionally."
    if confidence_summary.medium_percent >= 0.30:
        return "Some exposure uses proxy or manager-level inputs; compare relative exposure more than point estimates."
    return "Most exposure in this view is supported by direct or high-confidence inputs."
```

## 8. Portfolio Analytics Run Algorithm

The internal analytics run consumes an approved pack and a portfolio snapshot, then publishes an analytics bundle.

Pipeline:

1. Load approved pack.
2. Validate pack shape, references, version, and approval status.
3. Load portfolio snapshot.
4. Normalize positions.
5. Build or load market state vector.
6. Classify positions to themes/lenses.
7. Assign proxies.
8. Score confidence and opacity.
9. Apply scenarios.
10. Aggregate results by theme, manager, lens, and scenario.
11. Generate caveat and advisor-language fields.
12. Publish output bundle and manifest.

```python
def run_internal_analytics(pack_id, portfolio_snapshot, market_inputs, options):
    pack = load_approved_pack(pack_id)
    validate_pack_for_run(pack, portfolio_snapshot)

    positions = normalize_portfolio_positions(portfolio_snapshot)
    market_state = build_market_state_vector(
        options.as_of_date,
        market_inputs,
        pack.driver_catalog,
    )

    theme_assignments = {}
    proxy_assignments = {}
    confidence_rows = {}

    for position in positions:
        classification = classify_position_to_themes(
            position,
            pack.theme_catalog,
            pack.mapping_rules,
        )
        proxy = choose_proxy_for_position(
            position,
            pack.proxy_catalog,
            pack.all_scenario_driver_ids,
        )
        confidence = score_position_confidence(position, classification, proxy)

        theme_assignments[position.position_id] = classification
        proxy_assignments[position.position_id] = proxy
        confidence_rows[position.position_id] = confidence

    scenario_results = []
    for scenario in pack.scenario_catalog:
        shocks = define_scenario_driver_shocks(
            scenario.scenario_id,
            pack.scenario_catalog,
            pack.scenario_shock_pack,
        )
        if options.use_covariance_propagation:
            shocks = propagate_shocks_through_covariance(
                market_state,
                shocks["driver_shocks"],
                pack.covariance_model,
            )
        validation = validate_scenario_plausibility(
            market_state,
            apply_driver_shocks(market_state, shocks),
            scenario.plausibility_constraints,
        )
        scenario_results.append(
            calculate_scenario_impacts(
                positions,
                shocks,
                proxy_assignments,
                confidence_rows,
                validation,
            )
        )

    return publish_analytics_bundle(
        pack=pack,
        portfolio_snapshot=portfolio_snapshot,
        market_state=market_state,
        theme_assignments=theme_assignments,
        proxy_assignments=proxy_assignments,
        confidence_rows=confidence_rows,
        scenario_results=scenario_results,
    )
```

```python
def publish_analytics_bundle(
    pack,
    portfolio_snapshot,
    market_state,
    theme_assignments,
    proxy_assignments,
    confidence_rows,
    scenario_results,
):
    outputs = {
        "position_theme_assignments": build_position_theme_assignments(theme_assignments),
        "theme_exposure_summary": build_theme_exposure_summary(theme_assignments, confidence_rows),
        "manager_theme_overlap_summary": build_manager_theme_overlap_summary(theme_assignments),
        "scenario_impact_by_theme_manager": build_scenario_impact_summary(scenario_results, theme_assignments),
        "data_confidence_map": build_data_confidence_map(confidence_rows, theme_assignments),
        "cross_scenario_resilience_summary": build_cross_scenario_resilience_summary(scenario_results),
    }

    outputs["analytics_run_manifest"] = {
        "schema_version": "analytics_run_manifest.v1",
        "pack_id": pack.pack_id,
        "pack_version": pack.pack_version,
        "portfolio_id": portfolio_snapshot.portfolio_id,
        "as_of_date": market_state.as_of_date,
        "output_names": sorted(outputs.keys()),
        "source_inputs": list_source_input_ids(pack, portfolio_snapshot, market_state),
        "model_versions": collect_model_versions(pack),
        "synthetic_data": portfolio_snapshot.synthetic_data,
        "approval_status": "internal_analytics_output",
    }
    return outputs
```

## 9. Published Output Bundle

These are the internal analytics outputs Arangur can consume. The Advisor App should consume them through report-element input mapping and rendered views.

### `position_theme_assignments.json`

Purpose: records position-to-theme and lens assignments; provides provenance for exposure summaries.

Required fields: `schema_version`, `pack_id`, `pack_version`, `portfolio_id`, `as_of_date`, `positions`, `assignment_method`, `review_required_count`.

Position fields: `position_id`, `manager_id`, `instrument_id`, `market_value`, `primary_theme_id`, `secondary_theme_ids`, `theme_weights`, `classification_confidence`, `assignment_sources`, `review_status`, `review_reason`.

Consumer report elements: Concentration, Manager Comparison, Portfolio Status.

Not included: raw model controls, raw covariance matrix, secret source credentials, advisor-editable taxonomy.

### `theme_exposure_summary.json`

Purpose: summarizes exposure by approved theme; separates gross thematic exposure from allocation-weighted exposure.

Required fields: `themes`, `total_market_value`, `theme_count`, `gross_overlap_warning`, `confidence_notes`.

Theme fields: `theme_id`, `theme_display_name`, `market_value`, `percent_of_portfolio`, `top_managers`, `top_positions`, `confidence_mix`, `advisor_description`, `caveats`.

Consumer report elements: Concentration, Portfolio Status.

Not included: claims that overlapping themes sum to 100%, unapproved theme names.

### `manager_theme_overlap_summary.json`

Purpose: shows where multiple managers carry similar approved themes; supports hidden concentration discussion.

Required fields: `themes`, `manager_count`, `overlap_level`, `advisor_interpretation`.

Consumer report elements: Manager Comparison, Concentration.

Not included: manager rankings beyond the approved demo metrics, recommendations to hire/fire managers.

### `scenario_impact_by_theme_manager.json`

Purpose: shows scenario impact by theme and manager; connects approved scenario choices to reportable exposure.

Required fields: `scenarios`, `scenario_id`, `scenario_display_name`, `scenario_status`, `total_impact`, `total_impact_percent`, `theme_impacts`, `top_negative_managers`, `top_positive_or_defensive_managers`, `confidence`, `caveats`.

Consumer report elements: Scenario Impact by Manager, Manager Comparison, Portfolio Status.

Not included: probability of scenario occurrence unless explicitly approved, live forecast language, advisor-authored shock controls.

### `data_confidence_map.json`

Purpose: tracks confidence, opacity, and review requirements; drives caveats in report elements.

Required fields: `confidence_buckets`, `affected_themes`, `affected_managers`, `review_required_positions`, `advisor_language`.

Consumer report elements: Data Confidence Note, Portfolio Status, Concentration, Manager Comparison.

Not included: sensitive data-source credentials, raw vendor responses, unapproved compliance claims.

### `cross_scenario_resilience_summary.json`

Purpose: summarizes repeated vulnerabilities and defensive themes across approved scenarios; gives the advisor a structured discussion guide.

Required fields: `most_vulnerable_scenario`, `most_resilient_scenario`, `repeated_vulnerable_themes`, `repeated_defensive_themes`, `repeated_vulnerable_managers`, `repeated_defensive_managers`, `discussion_points`, `caveats`.

Consumer report elements: Portfolio Status, Manager Comparison, Scenario Impact by Manager.

Not included: optimization recommendations, trading instructions, probabilistic risk distribution unless v2 publishes approved statistics.

### `analytics_run_manifest.json`

Purpose: makes the run reproducible; records pack version, model versions, inputs, outputs, and synthetic/live status.

Required fields: `schema_version`, `run_id`, `pack_id`, `pack_version`, `portfolio_id`, `as_of_date`, `generated_at`, `source_inputs`, `output_files`, `model_versions`, `synthetic_data`, `validation_status`, `caveats`.

Consumer report elements: not usually rendered directly; used by input mapping, debugging, audit, and restart docs.

Not included: secrets, external credentials, unapproved raw client data.

## 10. Advisor-Facing Consumption Rules

The Advisor App must obey these rules:

- Show only approved scenario, theme, lens, and confidence labels.
- Do not expose shock vectors, covariance controls, PCA controls, proxy scoring knobs, or mapping-rule editors.
- Do not let unsupported choices pretend to be supported. Use placeholders when no committed output exists.
- Do not sum overlapping gross themes as if mutually exclusive.
- Do not hide low-confidence or review-required exposure.
- Keep scenario language directional unless the output explicitly supports point estimates.
- Preserve advisor-authored workflow order in Preview, Populate, and Present.
- Keep source workflow, generated timestamp, data snapshot, and synthetic-demo caveats as metadata/header/footer content.
- Use rendered report elements as the user-facing surface. Do not expose raw analytics JSON in the advisor path.

## 11. Implementation Sequencing Recommendation

A. Manifest + explicit assignment output

- Add `analytics_run_manifest.json`.
- Add `position_theme_assignments.json`.
- Keep existing proof outputs stable.
- Validate pack/run/output references.

B. Deterministic position-to-theme mapping

- Convert the current implicit theme matching into explicit assignment records.
- Add provenance fields and review routing.
- Keep v1 deterministic and synthetic-only.

C. Scenario application summary/provenance

- Preserve current deterministic scenario revaluation consumption.
- Add scenario construction metadata, shock provenance, and plausibility status.
- Do not introduce covariance/key-rate v2 yet unless Frank explicitly prioritizes it.

D. Proxy/confidence algorithms

- Add explicit proxy assignments.
- Add confidence scoring and aggregation policy.
- Connect caveat generation to confidence tiers.

E. Return report consumption/rendering

- Map the richer bundle into the existing report-element input/rendering path.
- Keep the advisor path simple: approved choices, supported previews, clean placeholders.
- Only after this, revisit richer scenario library or full covariance/key-rate v2.

## 12. Open Questions For Frank

1. Which themes must be product-grade first: AI/semis, rates/duration, private liquidity, credit, inflation, energy, or data confidence?
2. Should private funds default to manager-mandate mapping until look-through exists, or should they always require review before theme exposure is shown?
3. Which scenario additions matter first beyond the current five: Curve Steepening, Credit Spread Widening, or Inflation Persistence?
4. What confidence threshold should block client-facing point estimates and force directional language only?
5. Should proxy methodology be visible only as caveats, or should advisor reports show a small proxy-quality table?
6. For v1, is deterministic curated scenario output enough, or should the next algorithm tranche start preparing key-rate/covariance model metadata?
7. Should analytics bundles remain committed local synthetic fixtures for now, or become run-generated local artifacts before deployment planning resumes?
