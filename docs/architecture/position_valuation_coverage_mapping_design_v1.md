# Position Valuation Coverage Mapping Design v1

## 1. Purpose And Boundary

This document defines how Arranger maps positions to instruments, pricing functions, required market inputs, and valuation coverage status.

It is internal Arranger methodology. It does not implement production code, change app behavior, modify UI, create report views, generate analytics outputs, add backend endpoints, change Docker/deployment configuration, fetch market data, use real client data, or add dependencies.

The design principle is:

```text
position
-> instrument
-> pricing function
-> required market inputs
-> coverage status
-> valuation result
```

Every position should map to an instrument and a pricing function, or to an explicit review/coverage status. Missing valuation support should not be hidden behind unrelated heuristic scenario-impact formulas. If a position cannot be defensibly valued under a base or scenario market state, that is a coverage, confidence, caveat, or review issue.

This layer sits between complete market-state construction and full portfolio revaluation:

```text
base_market_state / scenario_market_state
-> position valuation coverage mapping
-> value every position
-> compare base and scenario values
-> aggregate impacts after valuation
```

Arangur Advisor App consumes approved valuation outputs, confidence labels, and caveats. It does not expose advisor-facing valuation controls, pricing model editors, substitute-input rule editors, or model-construction internals.

Thesis lenses classify values and impacts after valuation. They are separate from valuation coverage mapping: thesis buckets do not choose pricing functions, market inputs, or coverage treatment.

## 2. Core Abstractions

### A. Instrument

An instrument is the contract or asset definition being valued. It contains the terms and conditions sufficient to identify what the position represents.

Examples:

- equity share;
- listed option;
- ETF;
- bond;
- mutual fund;
- structured product;
- cash balance;
- private fund interest;
- manager-level opaque position.

An instrument should be stable across positions. Two accounts may hold different amounts of the same instrument.

### B. Position

A position is an owned amount of an instrument.

Examples:

- number of shares;
- face amount;
- notional amount;
- number of contracts;
- fund units;
- capital account value;
- cash amount.

A position adds ownership context: account, manager, sleeve, amount, book/current mark, acquisition metadata, and data freshness.

### C. Market State

A market state is the complete set of market inputs required to value positions on a valuation date. It may be a base market state or an approved scenario market state.

Market states include, as applicable, prices, curves, spreads, rates, FX, volatility surfaces, commodity curves, private marks, calendars, settlement assumptions, policy inputs, and source/confidence metadata.

### D. Pricing Function

A pricing function maps:

```text
instrument terms
+ position amount
+ market state
+ valuation context
-> valuation result
```

The function may be simple or complex. Examples include direct price lookup, cash valuation, bond cash-flow discounting, option pricing, fund NAV or look-through valuation, approved private mark policy, or explicit review-required handling.

Different pricing functions can be very different internally. The system-level methodology remains full revaluation: value every position under the base market state, value every position under the scenario market state, then compare.

### E. Valuation Context

The valuation context contains the policies and runtime context required to select and run pricing functions.

It should include:

- model registry;
- approved pricing-function registry;
- valuation policies;
- substitute-input policies;
- approved mark policies;
- calendars and conventions;
- data-source metadata;
- scenario id, nullable for base valuation;
- approval state;
- coverage policy;
- currency conversion policy;
- output trace policy.

### F. Valuation Result

A valuation result is the output of valuing one position under one market state.

It records value, currency, cash-flow output if applicable, model id, required inputs, used inputs, coverage status, confidence, caveats, review flag, and a concise valuation trace.

### G. Coverage Status

Coverage status describes whether the position could be valued directly, valued with substitute input, valued with approved policy, held at an approved mark, routed to review, or not valued.

Coverage status does not change the full revaluation methodology. It describes limits in the ability to perform the methodology for a position.

## 3. Universal Pricing-Function Interface

The system should expose a generic interface:

```python
def value_position(position, market_state, valuation_context):
    instrument = valuation_context.instrument_catalog.get(position.instrument_id)
    pricing_function = select_pricing_function(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
    )

    if pricing_function is None:
        return make_review_required_result(position, instrument, market_state)

    return pricing_function(
        instrument_terms=instrument.terms,
        position_amount=position.amount,
        market_state=market_state,
        valuation_context=valuation_context,
    )
```

Equivalent function shape:

```python
def pricing_function(instrument_terms, position_amount, market_state, valuation_context):
    required_inputs = required_market_inputs_for_instrument(instrument_terms)
    coverage = check_required_input_coverage(required_inputs, market_state)

    if not coverage.can_value:
        return approved_coverage_treatment(
            instrument_terms=instrument_terms,
            position_amount=position_amount,
            market_state=market_state,
            coverage=coverage,
            valuation_context=valuation_context,
        )

    value = run_model(
        instrument_terms=instrument_terms,
        position_amount=position_amount,
        market_inputs=market_state.market_inputs,
        valuation_context=valuation_context,
    )

    return build_valuation_result(value, required_inputs, coverage)
```

Required output fields:

- `position_id`
- `instrument_id`
- `market_state_id`
- `valuation_date`
- `value`
- `currency`
- `cash_flows`, if applicable
- `valuation_model_id`
- `required_market_inputs`
- `used_market_inputs`
- `coverage_status`
- `confidence`
- `caveats`
- `review_required`
- `valuation_trace`

Example result:

```json
{
  "position_id": "pos_public_equity_001",
  "instrument_id": "inst_public_equity_001",
  "market_state_id": "market_state_base_2026_06_30",
  "valuation_date": "2026-06-30",
  "value": 125000.0,
  "currency": "USD",
  "cash_flows": [],
  "valuation_model_id": "public_equity_price_lookup_v1",
  "required_market_inputs": ["equity_price:ABC"],
  "used_market_inputs": ["equity_price:ABC:2026-06-30"],
  "coverage_status": "valued",
  "confidence": "high",
  "caveats": [],
  "review_required": false,
  "valuation_trace": {
    "summary": "Shares multiplied by approved base equity price.",
    "input_completeness": "complete"
  }
}
```

## 4. Instrument And Position Schemas

### Instrument Record

Required fields:

- `instrument_id`
- `instrument_type`
- `issuer`
- `counterparty`
- `currency`
- `terms`
- `reference_data`
- `lifecycle_dates`
- `payoff_description`
- `required_input_families`
- `eligible_pricing_functions`
- `coverage_policy`

Example shape:

```json
{
  "instrument_id": "inst_bond_001",
  "instrument_type": "bond",
  "issuer": "Synthetic Issuer A",
  "counterparty": null,
  "currency": "USD",
  "terms": {
    "coupon_rate": 0.045,
    "coupon_frequency": "semi_annual",
    "maturity_date": "2031-06-30",
    "seniority": "senior_unsecured",
    "day_count": "30_360"
  },
  "reference_data": {
    "sector": "industrial",
    "rating": "BBB"
  },
  "lifecycle_dates": {
    "issue_date": "2021-06-30",
    "maturity_date": "2031-06-30"
  },
  "payoff_description": "Fixed coupon bond with principal repayment at maturity.",
  "required_input_families": ["discount_curve", "credit_spread_curve", "calendar"],
  "eligible_pricing_functions": ["bond_cash_flow_discounting_v1"],
  "coverage_policy": "standard_public_fixed_income_v1"
}
```

### Position Record

Required fields:

- `position_id`
- `instrument_id`
- `account_id`
- `manager_id`
- `sleeve_id`
- `amount_type`
- `amount`
- `book_value`
- `current_mark`
- `acquisition_metadata`
- `valuation_metadata`
- `data_freshness`
- `human_review_flags`

Example shape:

```json
{
  "position_id": "pos_bond_001",
  "instrument_id": "inst_bond_001",
  "account_id": "acct_taxable_001",
  "manager_id": "mgr_core_fixed_income",
  "sleeve_id": "sleeve_income",
  "amount_type": "face_amount",
  "amount": 1000000.0,
  "book_value": 985000.0,
  "current_mark": 992500.0,
  "acquisition_metadata": {
    "acquisition_date": "2024-02-15"
  },
  "valuation_metadata": {
    "last_valued_at": "2026-06-30",
    "last_value_source": "synthetic_demo"
  },
  "data_freshness": "current",
  "human_review_flags": []
}
```

## 5. Pricing Function Registry

The pricing function registry chooses which function values a position under a market state.

The registry should support:

- public equity price lookup valuation;
- cash valuation;
- bond cash-flow discounting;
- fund / ETF price or look-through valuation;
- option / structured product valuation;
- FX / currency translation;
- commodity / futures valuation;
- private fund approved policy valuation;
- opaque manager-level review treatment;
- fallback not-valued / review-required treatment.

Registry entry shape:

```json
{
  "pricing_function_id": "bond_cash_flow_discounting_v1",
  "display_name": "Bond Cash-Flow Discounting",
  "eligible_instrument_types": ["bond"],
  "required_input_families": ["discount_curve", "credit_spread_curve", "calendar"],
  "scenario_supported": true,
  "approval_status": "approved",
  "coverage_policy_id": "standard_public_fixed_income_v1"
}
```

Selection pseudocode:

```python
def select_pricing_function(position, instrument, market_state, valuation_context):
    candidates = valuation_context.pricing_function_registry.for_instrument_type(
        instrument.instrument_type
    )

    candidates = [
        candidate for candidate in candidates
        if candidate.approval_status == "approved"
    ]

    candidates = [
        candidate for candidate in candidates
        if candidate.supports_scenario(market_state.scenario_id)
    ]

    ranked = rank_pricing_candidates(
        candidates=candidates,
        position=position,
        instrument=instrument,
        market_state=market_state,
        coverage_policy=valuation_context.coverage_policy,
    )

    for candidate in ranked:
        required_inputs = candidate.required_market_inputs(instrument, position)
        coverage = check_required_input_coverage(required_inputs, market_state)
        if coverage.can_value or coverage.has_approved_treatment:
            return candidate

    return valuation_context.pricing_function_registry.fallback_review_required
```

Selection criteria:

- instrument type;
- required input families;
- base/scenario market-state support;
- direct input availability;
- substitute-input availability;
- coverage policy;
- model approval status;
- scenario support;
- human review flags;
- data freshness.

## 6. Required Market Input Mapping

Each pricing function should declare the market input families and specific input ids it requires.

Examples:

- Equity: approved equity price, or approved index/fund price input when direct price is unavailable.
- Bond: contractual cash flows, discount curve, spread curve, calendar, settlement assumptions, optional call/prepay assumptions.
- Option: underlying price, rates, dividend assumptions, volatility surface, exercise rules, contract multiplier.
- ETF/fund: NAV/market price or look-through holdings plus component valuation inputs.
- FX position: spot/forward rates and currency conventions.
- Commodity/futures: spot/futures curves, contract calendar, roll or settlement rules.
- Private fund: latest approved mark, manager data, appraisal policy, liquidity policy, stale-mark treatment.
- Opaque manager-level position: mandate, manager mark, review policy, coverage treatment.

Pseudocode:

```python
def required_market_inputs_for_instrument(instrument):
    if instrument.instrument_type == "public_equity":
        return [
            market_input("equity_price", instrument.reference_data["ticker"]),
            market_input("fx_rate", instrument.currency, optional_if_base_currency=True),
        ]

    if instrument.instrument_type == "bond":
        return [
            market_input("cash_flow_schedule", instrument.instrument_id),
            market_input("discount_curve", instrument.currency),
            market_input("credit_spread_curve", instrument.reference_data.get("rating")),
            market_input("calendar", instrument.currency),
            market_input("settlement_conventions", instrument.currency),
        ]

    if instrument.instrument_type == "listed_option":
        return [
            market_input("underlying_price", instrument.terms["underlying_id"]),
            market_input("risk_free_curve", instrument.currency),
            market_input("dividend_assumptions", instrument.terms["underlying_id"]),
            market_input("volatility_surface", instrument.terms["underlying_id"]),
            market_input("exercise_rules", instrument.instrument_id),
        ]

    if instrument.instrument_type in {"etf", "mutual_fund"}:
        return fund_price_or_lookthrough_inputs(instrument)

    if instrument.instrument_type == "private_fund_interest":
        return [
            market_input("latest_approved_mark", instrument.instrument_id),
            market_input("manager_reporting_metadata", instrument.instrument_id),
            market_input("approved_private_mark_policy", instrument.coverage_policy),
        ]

    return [market_input("review_policy", instrument.coverage_policy)]
```

The mapping can be instrument-specific even when the pricing function is shared. Two bonds may use the same pricing function but different issuer spread curves, currencies, calendars, and optionality assumptions.

## 7. Coverage Status And Treatment Policy

Coverage status values:

- `valued`
- `valued_with_substitute_input`
- `valued_with_approved_policy`
- `held_at_mark_with_caveat`
- `review_required`
- `not_valued`

### `valued`

Meaning: required inputs are available and the approved pricing function produced a direct valuation.

Applies when:

- instrument terms are sufficiently complete;
- position amount is known;
- required market inputs are available in the market state;
- pricing function is approved and scenario-supported.

Point impact: allowed.

Directional-only language: not required by coverage status alone.

Client briefing: allowed with ordinary methodology caveat.

Advisor review: no special coverage flag required unless material assumptions exist.

Required caveat language: "Position was valued under the approved market state."

### `valued_with_substitute_input`

Meaning: direct input was unavailable, but an approved substitute market input was used.

Applies when:

- direct price, curve, spread, or surface is missing;
- substitute input is approved for the instrument or policy;
- valuation trace records the substitution.

Point impact: allowed when policy permits, but confidence should usually be medium.

Directional-only language: recommended when substitute input is broad or imperfect.

Client briefing: allowed with concise substitute-input caveat.

Advisor review: should flag the substitute source.

Required caveat language: "Position was valued with an approved substitute market input; use the result directionally."

### `valued_with_approved_policy`

Meaning: the position was valued using an approved policy because full direct valuation inputs or look-through were incomplete.

Applies when:

- fund look-through is incomplete;
- private position uses approved policy inputs;
- mark or appraisal policy is approved for scenario handling;
- the policy is versioned and traceable.

Point impact: allowed only if the policy explicitly supports point impacts.

Directional-only language: often required.

Client briefing: allowed when policy permits and caveat is clear.

Advisor review: should flag policy use and materiality.

Required caveat language: "Position was valued with an approved policy because complete valuation inputs were unavailable."

### `held_at_mark_with_caveat`

Meaning: the current or latest approved mark was carried forward under the market state, with explicit caveat.

Applies when:

- private or opaque position lacks defensible scenario valuation inputs;
- latest mark is available but scenario sensitivity is not;
- approved policy says to hold at mark rather than invent impact.

Point impact: generally not allowed beyond zero or policy-defined mark movement.

Directional-only language: required.

Client briefing: allowed only with strong caveat and materiality review.

Advisor review: should flag prominently.

Required caveat language: "Position was held at an approved mark treatment; scenario impact may understate true exposure."

### `review_required`

Meaning: the position needs human review before relying on value or impact.

Applies when:

- instrument terms are incomplete;
- position amount is unclear;
- required inputs are missing without approved substitute;
- pricing function is not approved;
- private/opaque mark is stale or unsupported;
- low coverage affects a material position.

Point impact: not allowed.

Directional-only language: allowed only if clearly labeled as review-required.

Client briefing: generally blocked or shown only as unresolved exposure, depending on report policy.

Advisor review: required.

Required caveat language: "Position requires review before relying on scenario impact."

### `not_valued`

Meaning: no defensible valuation result was produced.

Applies when:

- instrument cannot be identified;
- position amount is missing;
- no pricing function or policy applies;
- data quality fails minimum acceptance.

Point impact: not allowed.

Directional-only language: not allowed as valuation output; may appear as unresolved data coverage.

Client briefing: should exclude point values and flag unresolved coverage if material.

Advisor review: required.

Required caveat language: "Position was not valued because required instrument, position, or market inputs were unavailable."

Coverage limitations do not change the methodology. They describe limits in the ability to perform full revaluation for a given position and market state.

## 8. Asset-Class Treatment Examples

These examples define design behavior only. They do not implement pricing models.

### A. Public Equity

- Instrument terms required: issuer, ticker or identifier, share class, currency, exchange, corporate-action assumptions.
- Position amount: shares.
- Market inputs required: equity price for the market state, FX rate if non-base currency, corporate-action/reference-data adjustments if applicable.
- Pricing function type: public equity price lookup.
- Ideal path: shares multiplied by approved market-state price, translated to reporting currency if needed.
- Fallback/coverage status: `valued_with_substitute_input` if approved proxy or index price is used; `review_required` if identifier or price is missing and no substitute is approved.
- Caveats: identify substitute price or stale/reference-data issue.

### B. Cash

- Instrument terms required: currency, account cash type, settlement availability, interest treatment if relevant.
- Position amount: cash amount.
- Market inputs required: FX spot for non-base currency, cash/yield treatment if income output is needed.
- Pricing function type: cash face value plus currency translation.
- Ideal path: cash amount valued at face in native currency and translated using approved FX input.
- Fallback/coverage status: `valued` for base-currency cash; `valued_with_substitute_input` if FX is substituted; `review_required` if currency or amount is unclear.
- Caveats: FX translation caveat for non-base currency or stale FX.

### C. Listed Option

- Instrument terms required: underlying, call/put, strike, expiration, exercise style, contract multiplier, currency, settlement terms.
- Position amount: number of contracts or notional.
- Market inputs required: underlying price, risk-free curve, dividends, volatility surface, calendar, exercise rules.
- Pricing function type: listed option model or approved market price lookup.
- Ideal path: use market quote when available or model with complete option inputs.
- Fallback/coverage status: `valued_with_substitute_input` for approved implied-vol proxy; `review_required` if option terms or volatility inputs are missing; `not_valued` if underlying cannot be identified.
- Caveats: model sensitivity, substitute volatility, stale quote, or exercise-style limitation.

### D. Bond / Fixed Income

- Instrument terms required: issuer, coupon, maturity, day count, payment frequency, seniority, call/prepay features, currency.
- Position amount: face amount or units.
- Market inputs required: cash-flow schedule, discount curve, credit spread curve, calendar, settlement assumptions, optional call/prepay assumptions.
- Pricing function type: bond cash-flow discounting.
- Ideal path: discount contractual cash flows under the market-state curves and spreads.
- Fallback/coverage status: `valued_with_substitute_input` if issuer spread is proxied by rating/sector curve; `valued_with_approved_policy` if complex optionality uses approved approximation; `review_required` if terms are incomplete.
- Caveats: substitute spread curve, stale rating, missing optionality, or settlement convention limits.

### E. ETF

- Instrument terms required: fund identifier, exchange, currency, share class, objective, benchmark, holdings look-through if available.
- Position amount: shares.
- Market inputs required: ETF market price or NAV; optional look-through holdings and component market inputs.
- Pricing function type: ETF price lookup or look-through valuation.
- Ideal path: use approved market price or NAV; use look-through when required and available.
- Fallback/coverage status: `valued_with_substitute_input` if price is proxied by benchmark; `valued_with_approved_policy` if look-through coverage is partial; `review_required` if fund identity or stale NAV is material.
- Caveats: benchmark proxy, stale NAV, premium/discount, or incomplete look-through.

### F. Mutual Fund

- Instrument terms required: fund identifier, share class, NAV convention, currency, redemption/liquidity terms, objective, holdings look-through if available.
- Position amount: shares or units.
- Market inputs required: NAV, fund price, look-through holdings if policy requires, FX if applicable.
- Pricing function type: NAV valuation or fund look-through policy.
- Ideal path: use approved NAV for valuation date or look-through valuation if required.
- Fallback/coverage status: `valued_with_approved_policy` when NAV timing or look-through is incomplete; `held_at_mark_with_caveat` for stale NAV; `review_required` for missing fund identity or stale material mark.
- Caveats: NAV lag, look-through limitation, liquidity terms.

### G. Private Equity Fund

- Instrument terms required: fund identity, vintage, strategy, commitment, unfunded commitment, capital account terms, manager, latest statement metadata, liquidity terms.
- Position amount: capital account value, units, commitment, or ownership interest.
- Market inputs required: latest approved mark, manager statement, appraisal/mark policy, private liquidity policy, optional public-market equivalent inputs.
- Pricing function type: approved private fund policy valuation.
- Ideal path: apply approved mark policy and scenario treatment with explicit confidence.
- Fallback/coverage status: `held_at_mark_with_caveat` when no defensible scenario sensitivity exists; `valued_with_approved_policy` when approved policy supports scenario adjustment; `review_required` for stale or unsupported marks.
- Caveats: mark lag, appraisal uncertainty, liquidity constraints, incomplete look-through.

### H. Private Credit

- Instrument terms required: borrower/fund identity, loan or fund terms, coupon, maturity, security, covenant/credit metadata, manager reporting.
- Position amount: principal, NAV, units, or capital account value.
- Market inputs required: latest mark, credit spread policy, cash-flow terms if direct loan, manager data, default/recovery assumptions if approved.
- Pricing function type: private credit cash-flow/policy valuation.
- Ideal path: value cash flows with approved private credit spread/default policy when terms are available.
- Fallback/coverage status: `valued_with_approved_policy` for approved policy; `held_at_mark_with_caveat` when only manager mark is defensible; `review_required` if terms or mark freshness fail.
- Caveats: stale mark, borrower opacity, private spread proxy, limited liquidity.

### I. Real Estate / Real Asset Fund

- Instrument terms required: fund or asset identity, property/asset exposure, appraisal policy, leverage terms, valuation frequency, liquidity terms.
- Position amount: NAV interest, units, or capital account value.
- Market inputs required: latest appraisal/mark, policy inputs, rates/cap-rate proxy if approved, manager data, liquidity policy.
- Pricing function type: approved real asset policy valuation.
- Ideal path: use approved appraisal/mark policy and scenario adjustment only when policy is approved.
- Fallback/coverage status: `held_at_mark_with_caveat` when scenario revaluation is not defensible; `valued_with_approved_policy` when cap-rate or policy sensitivity is approved; `review_required` for stale appraisals or missing exposure.
- Caveats: appraisal lag, cap-rate proxy, asset-level opacity, liquidity.

### J. Structured Product

- Instrument terms required: issuer/counterparty, payoff formula, underlying basket, barriers/caps/floors, maturity, coupons, call features, currency, settlement terms.
- Position amount: notional or units.
- Market inputs required: underlying levels, rates, volatility surfaces, correlation/basket assumptions if approved, credit/counterparty spread, calendars.
- Pricing function type: structured product model or approved vendor/mark policy.
- Ideal path: model payoff under complete market state when terms and inputs are complete.
- Fallback/coverage status: `valued_with_approved_policy` if approved mark/model policy applies; `held_at_mark_with_caveat` if only issuer mark is defensible; `review_required` if payoff terms or model inputs are missing.
- Caveats: model complexity, issuer mark dependency, volatility/correlation proxy, counterparty risk.

### K. FX Position

- Instrument terms required: currency pair, spot/forward/cash type, settlement date, notional, direction.
- Position amount: currency amount or notional.
- Market inputs required: spot rates, forward curve if forward-dated, settlement conventions.
- Pricing function type: FX spot or forward valuation.
- Ideal path: translate amount using approved spot/forward input.
- Fallback/coverage status: `valued_with_substitute_input` if approved stale/proxy FX rate is used; `review_required` if currency pair or settlement is missing.
- Caveats: stale FX, forward curve proxy, settlement date uncertainty.

### L. Crypto / Bitcoin Exposure

- Instrument terms required: token or vehicle identifier, custody/vehicle structure, currency, price source policy, liquidity terms.
- Position amount: token quantity, shares, units, or notional.
- Market inputs required: approved token price or vehicle price, FX if needed, liquidity/source metadata.
- Pricing function type: approved crypto price lookup or vehicle price valuation.
- Ideal path: use approved market-state crypto price or vehicle price with source metadata.
- Fallback/coverage status: `valued_with_substitute_input` if approved proxy is used; `review_required` if source, custody, or liquidity treatment is unclear.
- Caveats: source volatility, liquidity, custody/vehicle difference, stale price.

### M. Opaque Manager-Level Position

- Instrument terms required: manager, mandate, strategy, reporting basis, latest mark, liquidity/redemption terms, available holdings summary if any.
- Position amount: manager-reported NAV, capital account, or account-level value.
- Market inputs required: latest manager mark, approved opaque-position policy, mandate metadata, review policy.
- Pricing function type: opaque manager-level review or approved mark treatment.
- Ideal path: route to approved policy only if policy supports the mandate and data quality.
- Fallback/coverage status: often `held_at_mark_with_caveat`, `review_required`, or `not_valued`.
- Caveats: no holdings look-through, manager mark dependency, stale data, unknown scenario sensitivity.

## 9. Valuation Result And Cash-Flow Output

Valuation result shape:

```json
{
  "schema_version": "position_valuation_result.v1",
  "position_id": "pos_bond_001",
  "instrument_id": "inst_bond_001",
  "market_state_id": "market_state_scenario_rate_shock_2026_06_30",
  "valuation_date": "2026-06-30",
  "value": 963000.0,
  "currency": "USD",
  "cash_flows": [
    {
      "date": "2026-12-30",
      "amount": 22500.0,
      "currency": "USD",
      "cash_flow_type": "coupon",
      "confidence": "high"
    }
  ],
  "realized_or_expected_income": 45000.0,
  "valuation_model_id": "bond_cash_flow_discounting_v1",
  "required_market_inputs": ["cash_flow_schedule", "discount_curve:USD", "credit_spread_curve:BBB"],
  "used_market_inputs": ["discount_curve:USD:scenario_rate_shock", "credit_spread_curve:BBB:scenario_rate_shock"],
  "input_completeness": "complete",
  "coverage_status": "valued",
  "confidence": "high",
  "caveats": [],
  "review_required": false,
  "valuation_trace": {
    "summary": "Discounted scheduled bond cash flows using scenario discount and spread curves.",
    "trace_visibility": "internal_summary"
  }
}
```

Cash-flow output matters because future reports may need:

- income reporting;
- cash generation summaries;
- bond/fund coupon and distribution schedules;
- spending support analysis;
- liquidity timing analysis;
- scenario effects on income and projected cash flows.

Cash flows can be optional in v1, but the result schema should have a place for them. A simple equity price lookup may return an empty `cash_flows` list, while a bond or private credit result may return dated coupons, principal, amortization, or expected distributions.

## 10. Base/Scenario Comparison

Two valuation results are compared position by position.

```python
def compare_position_values(base_result, scenario_result):
    value_change = scenario_result["value"] - base_result["value"]
    confidence = combine_valuation_confidence(
        base_result["confidence"],
        scenario_result["confidence"],
        base_result["coverage_status"],
        scenario_result["coverage_status"],
    )

    return {
        "position_id": base_result["position_id"],
        "instrument_id": base_result["instrument_id"],
        "base_market_state_id": base_result["market_state_id"],
        "scenario_market_state_id": scenario_result["market_state_id"],
        "base_value": base_result["value"],
        "scenario_value": scenario_result["value"],
        "value_change": value_change,
        "value_change_percent": safe_divide(value_change, base_result["value"]),
        "base_coverage_status": base_result["coverage_status"],
        "scenario_coverage_status": scenario_result["coverage_status"],
        "confidence": confidence,
        "caveats": merge_caveats(base_result["caveats"], scenario_result["caveats"]),
    }
```

Portfolio aggregation then sums already-valued results:

```python
def aggregate_position_comparisons(position_comparisons):
    base_value = sum(row["base_value"] for row in position_comparisons)
    scenario_value = sum(row["scenario_value"] for row in position_comparisons)

    return {
        "base_portfolio_value": base_value,
        "scenario_portfolio_value": scenario_value,
        "impact": scenario_value - base_value,
        "impact_percent": safe_divide(scenario_value - base_value, base_value),
        "coverage_mix": summarize_coverage(position_comparisons),
        "confidence_mix": summarize_confidence(position_comparisons),
        "review_required_positions": positions_requiring_review(position_comparisons),
    }
```

Positions with `not_valued` or `review_required` must be handled explicitly in aggregation policy. They should not silently contribute fabricated impact.

## 11. Interaction With Scenario Basis Construction

Scenario basis construction produces a complete scenario market state.

Pricing functions consume the full market state. They should not consume key-rate coordinates, driver labels, or scenario-basis coordinates directly unless those coordinates have been expanded into the required market input families for the pricing function.

Correct flow:

```text
base_market_state
-> approved scenario basis perturbation
-> completed scenario basis vector
-> expanded scenario market state
-> pricing functions consume full market inputs
-> full revaluation
```

Position valuation should not depend on advisor-facing scenario labels. Labels such as "AI / Chip Selloff" or "Rate Shock" help advisors choose approved scenarios; pricing functions rely on the complete market-state inputs produced by the internal construction process.

## 12. Interaction With Thesis Lenses

Thesis lenses consume position values and impacts after valuation.

Boundaries:

- thesis buckets do not choose pricing functions;
- thesis buckets do not declare required market inputs;
- thesis buckets do not construct scenario market states;
- position-to-thesis classification is separate from valuation-input coverage mapping;
- valuation coverage mapping decides how positions are valued and caveated before thesis aggregation.

A position can have high valuation coverage but low thesis classification confidence. Example: a public utility stock has direct market prices and high valuation coverage, but uncertain bucket assignment under an AI Adoption lens.

A position can have low valuation coverage but high thesis classification confidence. Example: a private AI infrastructure fund may clearly belong to an AI infrastructure bucket, but lack enough look-through or mark policy to support point scenario impact.

Reports should keep these confidence dimensions distinct.

## 13. Internal Review And Governance

A position needs review when:

- instrument identity is missing or ambiguous;
- instrument terms are incomplete;
- position amount is missing or inconsistent;
- required market inputs are missing without approved substitute;
- substitute input is used for a material position;
- private mark is stale or unsupported;
- pricing function is not approved for the instrument or scenario;
- value change would be material and coverage is low;
- human review flags are present.

Approval responsibilities:

- Arranger control plane approves pricing functions, coverage policies, substitute-input policies, and mark policies.
- Internal analytics engine applies approved policies to a portfolio snapshot.
- Human reviewers approve overrides, stale-mark treatment, material substitute-input use, and unresolved private/opaque positions.
- Advisor-facing Arangur consumes only approved outputs, caveats, and confidence labels.

Stale marks should be flagged with:

- mark date;
- source;
- age in days;
- approved freshness threshold;
- materiality;
- policy treatment;
- review status.

Review queues should prioritize:

- market value;
- absolute scenario impact if available;
- low or review-required coverage;
- stale data;
- opaque/private exposure;
- client-facing report relevance;
- data quality failures.

Pricing-function mapping changes should be versioned. A change record should capture:

- prior pricing function;
- new pricing function;
- reason;
- approving reviewer or policy;
- effective date;
- affected instrument ids;
- expected output effect;
- compatibility notes.

## 14. Published Valuation Coverage Artifacts

Future implementation can publish versioned artifacts that feed the full revaluation bundle.

### `instrument_catalog.json`

Purpose: records normalized instruments and their terms.

Required fields:

- `schema_version`
- `portfolio_snapshot_id`
- `valuation_date`
- `instruments`
- `source_metadata`

Internal-only by default:

- raw source notes;
- private term documents;
- incomplete source records.

Advisor-facing fields:

- high-level instrument type and approved display labels only when needed in a report.

Relationship to revaluation bundle: pricing functions consume the instrument catalog to understand what is being valued.

### `position_catalog.json`

Purpose: records owned positions and amounts linked to instruments.

Required fields:

- `schema_version`
- `portfolio_snapshot_id`
- `valuation_date`
- `positions`
- `source_metadata`

Internal-only by default:

- raw account/source notes;
- acquisition metadata not approved for reporting;
- internal review flags.

Advisor-facing fields:

- summarized position, manager, account, sleeve, and amount context only when report policy allows.

Relationship to revaluation bundle: portfolio revaluation iterates over this position catalog.

### `pricing_function_registry.json`

Purpose: records approved pricing functions, eligibility, required inputs, approval status, and scenario support.

Required fields:

- `schema_version`
- `registry_version`
- `pricing_functions`
- `coverage_policies`
- `approval_metadata`

Internal-only by default:

- model internals;
- implementation details;
- calibration notes;
- substitute-input rules.

Advisor-facing fields:

- none by default, except approved model family labels if needed for advisor review.

Relationship to revaluation bundle: the valuation context uses the registry to select pricing functions.

### `position_pricing_function_assignments.json`

Purpose: records the selected pricing function for each position and market-state family.

Required fields:

- `schema_version`
- `portfolio_snapshot_id`
- `valuation_date`
- `assignments`
- `review_summary`

Each assignment should include:

- `position_id`
- `instrument_id`
- `pricing_function_id`
- `assignment_method`
- `required_input_families`
- `coverage_policy_id`
- `approval_status`
- `review_status`

Internal-only by default:

- detailed selection rationale;
- raw rule traces.

Advisor-facing fields:

- concise coverage explanation only when report policy allows.

Relationship to revaluation bundle: explains how each position was routed before valuation.

### `valuation_input_coverage_map.json`

Purpose: records required versus available inputs for each position.

Required fields:

- `schema_version`
- `market_state_id`
- `coverage_rows`
- `coverage_summary`

Each row should include:

- `position_id`
- `instrument_id`
- `required_market_inputs`
- `available_market_inputs`
- `missing_market_inputs`
- `substitute_inputs`
- `coverage_status`
- `confidence`
- `caveats`
- `review_required`

Internal-only by default:

- raw source metadata;
- substitute-rule detail;
- debug traces.

Advisor-facing fields:

- confidence label and concise caveat.

Relationship to revaluation bundle: supports coverage/confidence summaries and review queues.

### `position_valuation_results_base.json`

Purpose: records one valuation result per position under the base market state.

Required fields:

- `schema_version`
- `market_state_id`
- `valuation_date`
- `position_results`
- `summary`

Internal-only by default:

- raw valuation trace;
- private source notes.

Advisor-facing fields:

- approved values, confidence, and caveats through report elements.

Relationship to revaluation bundle: source for base values in position comparisons.

### `position_valuation_results_scenario_<scenario_id>.json`

Purpose: records one valuation result per position under a scenario market state.

Required fields match the base valuation result artifact, plus:

- `scenario_id`
- `scenario_market_state_id`
- `base_market_state_id`

Relationship to revaluation bundle: source for scenario values in position comparisons.

### `position_value_comparison_<scenario_id>.json`

Purpose: records base value, scenario value, value change, coverage, confidence, and caveats by position.

Required fields:

- `schema_version`
- `scenario_id`
- `base_market_state_id`
- `scenario_market_state_id`
- `position_comparisons`
- `portfolio_summary`

Advisor-facing fields:

- report-ready value/impact and confidence summaries after approval.

Internal-only by default:

- detailed trace and unresolved review notes.

Relationship to revaluation bundle: primary source for impact aggregation.

### `valuation_coverage_manifest.json`

Purpose: binds valuation coverage artifacts into one approved run output set.

Required fields:

- `schema_version`
- `portfolio_snapshot_id`
- `valuation_date`
- `base_market_state_id`
- `scenario_market_state_ids`
- `artifact_paths`
- `coverage_summary`
- `approval_metadata`
- `synthetic_data`

Relationship to revaluation bundle: becomes a component of the full revaluation bundle and supports data confidence/report caveat generation.

## 15. Advisor-Facing Consumption Rules

Advisor may see:

- value and impact;
- confidence label;
- concise coverage caveat;
- review-required warning;
- report-safe explanation;
- material unresolved exposure summary.

Advisor may not see by default:

- pricing model internals;
- substitute input rules;
- raw valuation trace;
- private source notes;
- debug data;
- model construction controls;
- unapproved source metadata.

Advisor-facing language should be compact:

- "Position was valued under the approved scenario market state."
- "Position was valued with an approved substitute input; use directionally."
- "Position was held at the latest approved mark; scenario impact may understate true exposure."
- "Position requires review before relying on scenario impact."

## 16. Implementation Sequencing Recommendation

Recommended next tranches:

A. Add contract fixtures for instruments, positions, pricing functions, and coverage statuses.

B. Add a pricing function registry skeleton.

C. Add deterministic simple valuation functions for synthetic demo positions.

D. Add base/scenario valuation result generation.

E. Add position value comparison outputs.

F. Add revaluation bundle manifest.

G. Then return to thesis-bucket/report aggregation.

The first implementation should stay synthetic and local. It should avoid live market data, external APIs, real client data, production reporting, advisor controls, or UI expansion.

## 17. Open Questions For Frank

1. Which instrument types need first-class support in the first skeleton?
2. Should public equities, cash, and simple fixed income be first?
3. How should private funds be handled in v1: held at mark, approved policy, or review required?
4. When is point impact allowed versus directional-only language?
5. Should cash flows be required in v1 valuation results, or optional until income reporting?
6. Which valuation traces should be internal-only versus advisor-review visible?
7. Should the first revaluation proof run one scenario or multiple scenarios?
8. Should opaque manager-level positions block client-facing impact reports when they are material?
