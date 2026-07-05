from __future__ import annotations

from typing import Any, Callable


VALID_COVERAGE_STATUSES = {
    "valued",
    "valued_with_substitute_input",
    "valued_with_approved_policy",
    "held_at_mark_with_caveat",
    "review_required",
    "not_valued",
}

VALID_CONFIDENCE_LEVELS = {"high", "medium", "low", "review_required"}


PricingFunction = Callable[[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]


PRICING_FUNCTIONS: dict[str, PricingFunction] = {}


def pricing_function(function_id: str) -> Callable[[PricingFunction], PricingFunction]:
    def decorator(func: PricingFunction) -> PricingFunction:
        PRICING_FUNCTIONS[function_id] = func
        return func

    return decorator


def select_pricing_function(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    """Select the first approved pricing function with an explicit coverage path."""
    candidates = [
        entry
        for entry in registry.get("pricing_functions", [])
        if instrument.get("instrument_type") in entry.get("eligible_instrument_types", [])
        and entry.get("approval_status") == "approved"
        and (entry.get("scenario_supported") is True or market_state.get("base_or_scenario") == "base")
    ]
    if not candidates:
        return _fallback_entry(registry)

    for entry in candidates:
        coverage = check_market_input_coverage(
            required_market_inputs=required_market_inputs(entry, position, instrument),
            market_state=market_state,
        )
        if coverage["can_value"] or entry.get("allows_explicit_review_treatment") is True:
            return entry
    return _fallback_entry(registry)


def value_with_pricing_function(
    *,
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    registry = valuation_context["pricing_function_registry"]
    entry = select_pricing_function(position, instrument, market_state, registry)
    function_id = entry["pricing_function_id"]
    func = PRICING_FUNCTIONS.get(function_id)
    if func is None:
        return _review_required_result(
            position=position,
            instrument=instrument,
            market_state=market_state,
            pricing_function_id=function_id,
            caveat=f"Pricing function {function_id} is not implemented in the skeleton.",
        )
    return func(position, instrument, market_state, valuation_context)


def required_market_inputs(
    pricing_function_entry: dict[str, Any],
    position: dict[str, Any],
    instrument: dict[str, Any],
) -> list[str]:
    input_families = pricing_function_entry.get("required_input_families", [])
    instrument_id = instrument["instrument_id"]
    currency = instrument.get("currency", "USD")
    required: list[str] = []
    for family in input_families:
        if family in {
            "equity_prices",
            "fund_prices",
            "money_market_navs",
            "bond_price_scalars",
            "commodity_prices",
            "crypto_prices",
            "private_marks",
        }:
            required.append(f"{family}:{instrument_id}")
        elif family == "cash_scalars":
            required.append(f"cash_scalars:{currency}")
        elif family == "fx_rates":
            required.append(f"fx_rates:{currency}")
        elif family == "review_policies":
            required.append(f"review_policies:{instrument.get('coverage_policy', 'fallback_review_required_v1')}")
        else:
            required.append(f"{family}:{instrument_id}")
    return required


def check_market_input_coverage(
    *,
    required_market_inputs: list[str],
    market_state: dict[str, Any],
) -> dict[str, Any]:
    available: list[str] = []
    missing: list[str] = []
    market_inputs = market_state.get("market_inputs", {})
    for input_id in required_market_inputs:
        family, key = _split_input_id(input_id)
        if _market_input_exists(market_inputs, family, key):
            available.append(input_id)
        else:
            missing.append(input_id)
    return {
        "required_market_inputs": required_market_inputs,
        "available_market_inputs": available,
        "missing_market_inputs": missing,
        "can_value": not missing,
    }


@pricing_function("public_equity_price_lookup_v1")
def public_equity_price_lookup(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    price_entry = _input_entry(market_state, "equity_prices", instrument["instrument_id"])
    if price_entry is None:
        return _review_required_result(position, instrument, market_state, "public_equity_price_lookup_v1", "Missing equity price input.")
    amount = _amount(position)
    value = amount * float(price_entry["price"])
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="public_equity_price_lookup_v1",
        value=value,
        required_inputs=[f"equity_prices:{instrument['instrument_id']}"],
        used_inputs=[price_entry["input_id"]],
        coverage_status="valued",
        confidence=_confidence(position),
        caveats=[],
        trace_summary="Shares multiplied by approved market-state equity price.",
    )


@pricing_function("cash_face_value_v1")
def cash_face_value(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    currency = instrument.get("currency", "USD")
    scalar = _input_entry(market_state, "cash_scalars", currency)
    if scalar is None:
        return _review_required_result(position, instrument, market_state, "cash_face_value_v1", "Missing cash scalar input.")
    value = _amount(position) * float(scalar["scalar"])
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="cash_face_value_v1",
        value=value,
        required_inputs=[f"cash_scalars:{currency}"],
        used_inputs=[scalar["input_id"]],
        coverage_status="valued",
        confidence="high",
        caveats=[],
        trace_summary="Cash amount valued at approved face-value treatment.",
    )


@pricing_function("money_market_nav_lookup_v1")
def money_market_nav_lookup(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    nav_entry = _input_entry(market_state, "money_market_navs", instrument["instrument_id"])
    if nav_entry is None:
        return _review_required_result(position, instrument, market_state, "money_market_nav_lookup_v1", "Missing money-market NAV input.")
    value = _amount(position) * float(nav_entry["nav"])
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="money_market_nav_lookup_v1",
        value=value,
        required_inputs=[f"money_market_navs:{instrument['instrument_id']}"],
        used_inputs=[nav_entry["input_id"]],
        coverage_status="valued",
        confidence=_confidence(position),
        caveats=[],
        trace_summary="Money-market units multiplied by approved market-state NAV.",
    )


@pricing_function("fund_nav_lookup_v1")
def fund_nav_lookup(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    price_entry = _input_entry(market_state, "fund_prices", instrument["instrument_id"])
    if price_entry is None:
        return _review_required_result(position, instrument, market_state, "fund_nav_lookup_v1", "Missing fund price or NAV input.")
    value = _amount(position) * float(price_entry["price"])
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="fund_nav_lookup_v1",
        value=value,
        required_inputs=[f"fund_prices:{instrument['instrument_id']}"],
        used_inputs=[price_entry["input_id"]],
        coverage_status="valued",
        confidence=_confidence(position),
        caveats=[],
        trace_summary="Fund or ETF units multiplied by approved market-state price or NAV.",
    )


@pricing_function("bond_mark_scalar_v1")
def bond_mark_scalar(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    scalar = _input_entry(market_state, "bond_price_scalars", instrument["instrument_id"])
    if scalar is None:
        return _review_required_result(position, instrument, market_state, "bond_mark_scalar_v1", "Missing bond price scalar input.")
    notional = _amount(position)
    value = notional * float(scalar["price_per_100"]) / 100.0
    cash_flows = _bond_cash_flows(instrument, market_state)
    caveats = ["Simplified synthetic bond valuation; not production fixed-income accounting."]
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="bond_mark_scalar_v1",
        value=value,
        required_inputs=[f"bond_price_scalars:{instrument['instrument_id']}"],
        used_inputs=[scalar["input_id"]],
        coverage_status="valued_with_approved_policy",
        confidence=_confidence(position),
        caveats=caveats,
        trace_summary="Applied approved synthetic bond price scalar to position notional.",
        cash_flows=cash_flows,
    )


@pricing_function("fx_notional_translation_v1")
def fx_notional_translation(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    currency = instrument.get("currency", "USD")
    fx_entry = _input_entry(market_state, "fx_rates", currency)
    if fx_entry is None:
        return _review_required_result(position, instrument, market_state, "fx_notional_translation_v1", "Missing FX input.")
    value = _amount(position) * float(fx_entry["rate_to_usd"])
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="fx_notional_translation_v1",
        value=value,
        required_inputs=[f"fx_rates:{currency}"],
        used_inputs=[fx_entry["input_id"]],
        coverage_status="valued",
        confidence=_confidence(position),
        caveats=[],
        trace_summary="Translated notional exposure with approved market-state FX input.",
    )


@pricing_function("commodity_price_lookup_v1")
def commodity_price_lookup(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    entry = _input_entry(market_state, "commodity_prices", instrument["instrument_id"])
    if entry is None:
        return _review_required_result(position, instrument, market_state, "commodity_price_lookup_v1", "Missing commodity price input.")
    value = _amount(position) * float(entry["price"])
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="commodity_price_lookup_v1",
        value=value,
        required_inputs=[f"commodity_prices:{instrument['instrument_id']}"],
        used_inputs=[entry["input_id"]],
        coverage_status="valued",
        confidence=_confidence(position),
        caveats=[],
        trace_summary="Commodity exposure amount multiplied by approved market-state price scalar.",
    )


@pricing_function("crypto_price_lookup_v1")
def crypto_price_lookup(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    entry = _input_entry(market_state, "crypto_prices", instrument["instrument_id"])
    if entry is None:
        return _review_required_result(position, instrument, market_state, "crypto_price_lookup_v1", "Missing crypto price input.")
    value = _amount(position) * float(entry["price"])
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="crypto_price_lookup_v1",
        value=value,
        required_inputs=[f"crypto_prices:{instrument['instrument_id']}"],
        used_inputs=[entry["input_id"]],
        coverage_status="valued",
        confidence=_confidence(position),
        caveats=["Synthetic crypto price input; not live market data."],
        trace_summary="Crypto vehicle units multiplied by approved synthetic market-state price.",
    )


@pricing_function("approved_private_mark_policy_v1")
def approved_private_mark_policy(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    entry = _input_entry(market_state, "private_marks", instrument["instrument_id"])
    if entry is None:
        return _review_required_result(position, instrument, market_state, "approved_private_mark_policy_v1", "Missing approved private mark.")
    review_required = bool(position.get("human_review_required")) or _confidence(position) == "review_required"
    status = "review_required" if review_required else "held_at_mark_with_caveat"
    confidence = "review_required" if review_required else _low_or_medium(position)
    caveat = (
        "Position requires review before relying on scenario impact."
        if review_required
        else "Position was held at an approved mark treatment; scenario impact may understate true exposure."
    )
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="approved_private_mark_policy_v1",
        value=float(entry["mark"]),
        required_inputs=[f"private_marks:{instrument['instrument_id']}"],
        used_inputs=[entry["input_id"]],
        coverage_status=status,
        confidence=confidence,
        caveats=[caveat],
        trace_summary="Applied approved private/opaque mark policy; no unsupported scenario sensitivity was invented.",
        review_required=review_required,
    )


@pricing_function("review_required_treatment_v1")
def review_required_treatment(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
) -> dict[str, Any]:
    mark_entry = _input_entry(market_state, "private_marks", instrument["instrument_id"])
    value = float(mark_entry["mark"]) if mark_entry is not None else float(position.get("current_mark") or 0.0)
    used_inputs = [mark_entry["input_id"]] if mark_entry is not None else []
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context=valuation_context,
        valuation_model_id="review_required_treatment_v1",
        value=value,
        required_inputs=[f"review_policies:{instrument.get('coverage_policy', 'fallback_review_required_v1')}"],
        used_inputs=used_inputs,
        coverage_status="review_required",
        confidence="review_required",
        caveats=["Position requires review before relying on scenario impact."],
        trace_summary="Held latest synthetic mark for reconciliation while routing the position to review.",
        review_required=True,
    )


def _fallback_entry(registry: dict[str, Any]) -> dict[str, Any]:
    for entry in registry.get("pricing_functions", []):
        if entry.get("pricing_function_id") == "review_required_treatment_v1":
            return entry
    return {
        "pricing_function_id": "review_required_treatment_v1",
        "required_input_families": ["review_policies"],
        "eligible_instrument_types": [],
        "approval_status": "approved",
        "scenario_supported": True,
        "allows_explicit_review_treatment": True,
    }


def _valued_result(
    *,
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    valuation_context: dict[str, Any],
    valuation_model_id: str,
    value: float,
    required_inputs: list[str],
    used_inputs: list[str],
    coverage_status: str,
    confidence: str,
    caveats: list[str],
    trace_summary: str,
    cash_flows: list[dict[str, Any]] | None = None,
    review_required: bool | None = None,
) -> dict[str, Any]:
    if coverage_status not in VALID_COVERAGE_STATUSES:
        raise ValueError(f"Invalid coverage status: {coverage_status}")
    if confidence not in VALID_CONFIDENCE_LEVELS:
        raise ValueError(f"Invalid confidence level: {confidence}")
    return {
        "schema_version": "position_valuation_result.v1",
        "position_id": position["position_id"],
        "instrument_id": instrument["instrument_id"],
        "market_state_id": market_state["market_state_id"],
        "valuation_date": market_state["valuation_date"],
        "value": _round_money(value),
        "currency": instrument.get("currency", "USD"),
        "cash_flows": cash_flows or [],
        "valuation_model_id": valuation_model_id,
        "required_market_inputs": required_inputs,
        "used_market_inputs": used_inputs,
        "coverage_status": coverage_status,
        "confidence": confidence,
        "caveats": caveats,
        "review_required": review_required if review_required is not None else coverage_status == "review_required",
        "valuation_trace": {
            "summary": trace_summary,
            "trace_visibility": "internal_summary",
            "input_completeness": "complete" if set(required_inputs) <= set(used_inputs) else "policy_or_review",
        },
        "source_position": {
            "manager_id": position.get("manager_id"),
            "account_id": position.get("account_id"),
            "sleeve_id": position.get("sleeve_id"),
            "display_name": position.get("display_name"),
        },
        "synthetic_data": True,
    }


def _review_required_result(
    position: dict[str, Any],
    instrument: dict[str, Any],
    market_state: dict[str, Any],
    pricing_function_id: str,
    caveat: str,
) -> dict[str, Any]:
    return _valued_result(
        position=position,
        instrument=instrument,
        market_state=market_state,
        valuation_context={},
        valuation_model_id=pricing_function_id,
        value=float(position.get("current_mark") or 0.0),
        required_inputs=[],
        used_inputs=[],
        coverage_status="review_required",
        confidence="review_required",
        caveats=[caveat],
        trace_summary="Position routed to review by the synthetic pricing registry.",
        review_required=True,
    )


def _amount(position: dict[str, Any]) -> float:
    return float(position.get("amount") or position.get("current_mark") or 0.0)


def _confidence(position: dict[str, Any]) -> str:
    if position.get("human_review_required") is True:
        return "review_required"
    confidence = str(position.get("valuation_confidence") or "medium").lower()
    if confidence in {"high", "medium", "low"}:
        return confidence
    return "review_required"


def _low_or_medium(position: dict[str, Any]) -> str:
    return "low" if _confidence(position) in {"low", "review_required"} else "medium"


def _input_entry(market_state: dict[str, Any], family: str, key: str) -> dict[str, Any] | None:
    entry = market_state.get("market_inputs", {}).get(family, {}).get(key)
    return entry if isinstance(entry, dict) else None


def _market_input_exists(market_inputs: dict[str, Any], family: str, key: str) -> bool:
    values = market_inputs.get(family)
    if isinstance(values, dict):
        return key in values
    return False


def _split_input_id(input_id: str) -> tuple[str, str]:
    if ":" not in input_id:
        return input_id, ""
    family, key = input_id.split(":", 1)
    return family, key


def _bond_cash_flows(instrument: dict[str, Any], market_state: dict[str, Any]) -> list[dict[str, Any]]:
    terms = instrument.get("terms", {})
    coupon_rate = float(terms.get("coupon_rate", 0.0))
    notional = float(terms.get("face_amount", 0.0))
    if coupon_rate <= 0 or notional <= 0:
        return []
    return [
        {
            "date": "2026-12-31",
            "amount": _round_money(notional * coupon_rate / 2.0),
            "currency": instrument.get("currency", "USD"),
            "cash_flow_type": "coupon",
            "confidence": "medium",
            "market_state_id": market_state["market_state_id"],
        }
    ]


def _round_money(value: float) -> float:
    return round(float(value), 2)
