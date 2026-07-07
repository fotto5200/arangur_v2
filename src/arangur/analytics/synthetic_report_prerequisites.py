from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-07T00:00:00Z"
PACK_ID = "synthetic_report_prerequisite_pack_v1"
PACK_VERSION = "2026-07-07"
GENERATOR_VERSION = "synthetic_report_prerequisites.v1"

DEFAULT_REVALUATION_DIR = Path("data/simulation/revaluation")
DEFAULT_POSITION_UNIVERSE_PATH = Path("data/simulation/synthetic_position_universe.json")
DEFAULT_OUTPUT_DIR = (
    Path("data/simulation/report_prerequisites") / PACK_ID
)

AI_LENS_ID = "ai_adoption"
ENERGY_LENS_ID = "energy_security"

ARTIFACT_FILES = {
    "synthetic_report_prerequisite_pack_manifest": "synthetic_report_prerequisite_pack_manifest.json",
    "cash_flow_need_profile": "cash_flow_need_profile.json",
    "cash_flow_history_summary": "cash_flow_history_summary.json",
    "cash_flow_projection_summary": "cash_flow_projection_summary.json",
    "cash_flow_support_inputs": "cash_flow_support_inputs.json",
    "manager_mandate_catalog": "manager_mandate_catalog.json",
    "synthetic_lens_catalog": "synthetic_lens_catalog.json",
    "ai_adoption_lens_v1": "ai_adoption_lens_v1.json",
    "energy_security_lens_v1": "energy_security_lens_v1.json",
    "position_lens_assignments_ai_adoption_v1": "position_lens_assignments_ai_adoption_v1.json",
    "position_lens_assignments_energy_security_v1": "position_lens_assignments_energy_security_v1.json",
    "lens_exposure_prerequisite_summary": "lens_exposure_prerequisite_summary.json",
    "scenario_lens_readiness_summary": "scenario_lens_readiness_summary.json",
}

AI_PRIMARY_BUCKETS = (
    (
        "core_ai_infrastructure_hardware",
        "Core AI Infrastructure / Hardware",
        "Direct compute, semiconductor, accelerator, and hardware infrastructure exposure.",
    ),
    (
        "ai_model_platform_exposure",
        "AI Model / Platform Exposure",
        "Cloud, platform, software, and data assets that enable AI adoption.",
    ),
    (
        "ai_downstream_productivity_beneficiary",
        "AI Downstream Productivity Beneficiary",
        "Operating businesses that may benefit from AI-enabled productivity.",
    ),
    (
        "ai_disrupted_incumbent",
        "AI-Disrupted Incumbent",
        "Businesses where AI may pressure legacy economics or workflows.",
    ),
    (
        "data_center_power_bottleneck_exposure",
        "Data Center / Power Bottleneck Exposure",
        "Data center, grid, cooling, and power bottleneck exposure tied to AI demand.",
    ),
    (
        "neutral_low_direct_ai_exposure",
        "Neutral / Low Direct AI Exposure",
        "Holdings with limited direct AI thesis exposure in the synthetic fixture.",
    ),
    (
        "unclassified_review_required",
        "Unclassified / Review Required",
        "Opaque, derivative, or insufficiently evidenced holdings that need review.",
    ),
)

AI_SECONDARY_FLAGS = (
    (
        "china_taiwan_supply_chain_exposure",
        "China/Taiwan Supply-Chain Exposure",
        "Semiconductor or Asia supply-chain exposure that may matter to AI thesis review.",
    ),
    (
        "power_demand_sensitivity",
        "Power Demand Sensitivity",
        "Exposure whose economics may be affected by data-center power demand.",
    ),
    (
        "regulatory_sensitivity",
        "Regulatory Sensitivity",
        "Exposure with material regulatory, policy, or financial-system sensitivity.",
    ),
    (
        "private_market_opacity",
        "Private-Market Opacity",
        "Private, stale-mark, manager-level, or review-required exposure.",
    ),
    (
        "hardware_cycle_sensitivity",
        "Hardware Cycle Sensitivity",
        "Compute, chip, accelerator, or semiconductor-cycle sensitivity.",
    ),
)

ENERGY_PRIMARY_BUCKETS = (
    (
        "energy_supply_beneficiary",
        "Energy Supply Beneficiary",
        "Direct energy, pipeline, fuel, uranium, or power supply exposure.",
    ),
    (
        "grid_infrastructure_beneficiary",
        "Grid Infrastructure Beneficiary",
        "Grid, power campus, renewable infrastructure, and related infrastructure exposure.",
    ),
    (
        "energy_input_cost_sensitive",
        "Energy Input-Cost Sensitive",
        "Businesses whose economics may be sensitive to power or energy input costs.",
    ),
    (
        "transition_policy_sensitive",
        "Transition Policy Sensitive",
        "Holdings with policy, transition, real-asset, or infrastructure sensitivity.",
    ),
    (
        "commodity_supply_security_exposure",
        "Commodity Supply Security Exposure",
        "Commodity, metals, gold, or resource security exposure.",
    ),
    (
        "neutral_low_direct_energy_exposure",
        "Neutral / Low Direct Energy Exposure",
        "Holdings with limited direct energy-security exposure in the synthetic fixture.",
    ),
    (
        "unclassified_review_required",
        "Unclassified / Review Required",
        "Opaque, derivative, or insufficiently evidenced holdings that need review.",
    ),
)

ENERGY_SECONDARY_FLAGS = (
    (
        "power_reliability_sensitivity",
        "Power Reliability Sensitivity",
        "Exposure affected by power availability, reliability, or grid constraints.",
    ),
    (
        "data_center_power_demand",
        "Data Center Power Demand",
        "Data center or AI infrastructure exposure tied to power demand.",
    ),
    (
        "transition_policy_sensitivity",
        "Transition Policy Sensitivity",
        "Exposure affected by energy transition or infrastructure policy.",
    ),
    (
        "commodity_price_sensitivity",
        "Commodity Price Sensitivity",
        "Resource, energy, metals, or commodity price exposure.",
    ),
    (
        "private_market_opacity",
        "Private-Market Opacity",
        "Private, stale-mark, manager-level, or review-required exposure.",
    ),
)


def generate_synthetic_report_prerequisite_pack(
    *,
    revaluation_dir: str | Path = DEFAULT_REVALUATION_DIR,
    position_universe_path: str | Path = DEFAULT_POSITION_UNIVERSE_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    context = load_source_context(
        revaluation_dir=Path(revaluation_dir),
        position_universe_path=Path(position_universe_path),
    )

    outputs: dict[str, Any] = {
        "cash_flow_need_profile": build_cash_flow_need_profile(context),
        "cash_flow_history_summary": build_cash_flow_history_summary(context),
        "cash_flow_projection_summary": build_cash_flow_projection_summary(context),
        "manager_mandate_catalog": build_manager_mandate_catalog(context),
        "ai_adoption_lens_v1": build_lens_definition(
            lens_id=AI_LENS_ID,
            display_name="AI Adoption",
            purpose=(
                "Classify the synthetic portfolio by economic exposure to AI adoption, "
                "infrastructure buildout, disruption, and bottlenecks."
            ),
            primary_buckets=AI_PRIMARY_BUCKETS,
            secondary_flags=AI_SECONDARY_FLAGS,
            neutral_bucket_id="neutral_low_direct_ai_exposure",
        ),
        "energy_security_lens_v1": build_lens_definition(
            lens_id=ENERGY_LENS_ID,
            display_name="Energy Security",
            purpose=(
                "Classify the synthetic portfolio by exposure to power reliability, "
                "energy supply, commodity availability, grid infrastructure, and transition bottlenecks."
            ),
            primary_buckets=ENERGY_PRIMARY_BUCKETS,
            secondary_flags=ENERGY_SECONDARY_FLAGS,
            neutral_bucket_id="neutral_low_direct_energy_exposure",
        ),
    }

    outputs["position_lens_assignments_ai_adoption_v1"] = build_position_lens_assignments(
        context,
        lens=outputs["ai_adoption_lens_v1"],
        classify=_classify_ai_adoption,
    )
    outputs["position_lens_assignments_energy_security_v1"] = build_position_lens_assignments(
        context,
        lens=outputs["energy_security_lens_v1"],
        classify=_classify_energy_security,
    )
    outputs["synthetic_lens_catalog"] = build_synthetic_lens_catalog(outputs)
    outputs["lens_exposure_prerequisite_summary"] = build_lens_exposure_prerequisite_summary(
        context, outputs
    )
    outputs["scenario_lens_readiness_summary"] = build_scenario_lens_readiness_summary(
        context, outputs
    )
    outputs["cash_flow_support_inputs"] = build_cash_flow_support_inputs(outputs)
    outputs["synthetic_report_prerequisite_pack_manifest"] = build_manifest(context, outputs)

    validate_pack(context, outputs)

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    for output_name, filename in ARTIFACT_FILES.items():
        _write_json(root / filename, outputs[output_name])

    return outputs


def load_source_context(
    *,
    revaluation_dir: Path,
    position_universe_path: Path,
) -> dict[str, Any]:
    position_universe = _load_json(position_universe_path)
    position_catalog = _load_json(revaluation_dir / "position_catalog.json")
    instrument_catalog = _load_json(revaluation_dir / "instrument_catalog.json")
    base_valuation = _load_json(revaluation_dir / "position_valuation_results_base.json")
    scenario_index = _load_json(revaluation_dir / "revaluation_scenario_index.json")
    ai_summary = _load_json(revaluation_dir / "portfolio_revaluation_summary_ai_chip_selloff.json")
    rate_summary = _load_json(revaluation_dir / "portfolio_revaluation_summary_rate_shock.json")

    source_positions_by_id = {
        row["position_id"]: row for row in position_universe["positions"]
    }
    positions_by_id = {row["position_id"]: row for row in position_catalog["positions"]}
    instruments_by_id = {
        row["instrument_id"]: row for row in instrument_catalog["instruments"]
    }
    base_rows_by_position = {
        row["position_id"]: row for row in base_valuation["position_results"]
    }

    in_scope_positions = []
    for row in sorted(
        base_valuation["position_results"],
        key=lambda item: source_positions_by_id[item["position_id"]].get("sort_order", item["position_id"]),
    ):
        position = positions_by_id[row["position_id"]]
        source_position = source_positions_by_id[row["position_id"]]
        instrument = instruments_by_id[position["instrument_id"]]
        in_scope_positions.append(
            {
                "base_valuation": row,
                "position": position,
                "source_position": source_position,
                "instrument": instrument,
            }
        )

    return {
        "source_paths": {
            "position_universe": _as_posix(position_universe_path),
            "position_catalog": _as_posix(revaluation_dir / "position_catalog.json"),
            "instrument_catalog": _as_posix(revaluation_dir / "instrument_catalog.json"),
            "base_valuation": _as_posix(revaluation_dir / "position_valuation_results_base.json"),
            "scenario_index": _as_posix(revaluation_dir / "revaluation_scenario_index.json"),
            "ai_chip_selloff_summary": _as_posix(
                revaluation_dir / "portfolio_revaluation_summary_ai_chip_selloff.json"
            ),
            "rate_shock_summary": _as_posix(
                revaluation_dir / "portfolio_revaluation_summary_rate_shock.json"
            ),
        },
        "position_universe": position_universe,
        "position_catalog": position_catalog,
        "instrument_catalog": instrument_catalog,
        "base_valuation": base_valuation,
        "scenario_index": scenario_index,
        "portfolio_summaries": {
            "ai_chip_selloff": ai_summary,
            "rate_shock": rate_summary,
        },
        "source_positions_by_id": source_positions_by_id,
        "positions_by_id": positions_by_id,
        "instruments_by_id": instruments_by_id,
        "base_rows_by_position": base_rows_by_position,
        "in_scope_positions": in_scope_positions,
        "valuation_date": str(base_valuation["valuation_date"]),
        "portfolio_id": str(position_catalog["portfolio_id"]),
        "portfolio_snapshot_id": str(position_catalog["portfolio_snapshot_id"]),
        "base_portfolio_value": round(float(base_valuation["summary"]["total_value"]), 2),
    }


def build_cash_flow_need_profile(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "cash_flow_need_profile.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "portfolio_snapshot_id": context["portfolio_snapshot_id"],
        "valuation_date": context["valuation_date"],
        "planning_period": {
            "period_id": "synthetic_next_12_months_2026_07_to_2027_06",
            "start_date": "2026-07-01",
            "end_date": "2027-06-30",
            "period_months": 12,
        },
        "stated_annual_cash_need": {
            "amount": 1200000.0,
            "currency": "USD",
            "need_basis": "synthetic_demo_stated_need",
            "display_label": "Synthetic stated annual cash need",
        },
        "funding_policy": {
            "policy_id": "synthetic_income_first_then_liquidity_buffer_v1",
            "primary_source": "portfolio_income_and_distributions",
            "secondary_source": "liquidity_reserve_buffer",
            "tertiary_source": "advisor_review_rebalancing_if_needed",
        },
        "source_metadata": _source_metadata(
            "synthetic_cash_need_fixture",
            ["No real client spending need, liability schedule, or account withdrawal record is used."],
        ),
    }


def build_cash_flow_history_summary(context: dict[str, Any]) -> dict[str, Any]:
    generated = 1365000.0
    paid_out = 1110000.0
    return {
        "schema_version": "cash_flow_history_summary.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "portfolio_snapshot_id": context["portfolio_snapshot_id"],
        "valuation_date": context["valuation_date"],
        "history_period": {
            "period_id": "synthetic_trailing_12_months_2025_07_to_2026_06",
            "start_date": "2025-07-01",
            "end_date": "2026-06-30",
            "period_months": 12,
        },
        "cash_generated_last_period": {
            "amount": generated,
            "currency": "USD",
            "components": [
                {"component": "income_distributions", "amount": 835000.0},
                {"component": "bond_interest_and_cash_yield", "amount": 310000.0},
                {"component": "option_premium_and_other_synthetic_income", "amount": 220000.0},
            ],
        },
        "cash_paid_out_last_period": {
            "amount": paid_out,
            "currency": "USD",
            "components": [
                {"component": "synthetic_spending_distributions", "amount": 990000.0},
                {"component": "synthetic_tax_reserve", "amount": 120000.0},
            ],
        },
        "net_cash_after_paid_out": {
            "amount": round(generated - paid_out, 2),
            "currency": "USD",
        },
        "cash_flow_by_manager_sleeve_ready": False,
        "manager_sleeve_detail_status": "not_reliable_as_report_source",
        "confidence": "medium",
        "confidence_caveat": (
            "Synthetic cash history is explicit enough for a whole-portfolio demo summary, "
            "but it is not a reliable manager/sleeve cash-flow source."
        ),
        "source_metadata": _source_metadata(
            "synthetic_cash_history_fixture",
            ["Generated for local demo prerequisite coverage only."],
        ),
    }


def build_cash_flow_projection_summary(context: dict[str, Any]) -> dict[str, Any]:
    projected_generation = 1315000.0
    projected_need = 1200000.0
    return {
        "schema_version": "cash_flow_projection_summary.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "portfolio_snapshot_id": context["portfolio_snapshot_id"],
        "valuation_date": context["valuation_date"],
        "projection_period": {
            "period_id": "synthetic_next_12_months_2026_07_to_2027_06",
            "start_date": "2026-07-01",
            "end_date": "2027-06-30",
            "period_months": 12,
        },
        "projected_cash_generation": {
            "amount": projected_generation,
            "currency": "USD",
            "projection_basis": "synthetic_income_run_rate_with_moderate_haircut",
        },
        "projected_paid_out_need": {
            "amount": projected_need,
            "currency": "USD",
            "need_source": "cash_flow_need_profile.stated_annual_cash_need",
        },
        "projected_surplus_shortfall": {
            "amount": round(projected_generation - projected_need, 2),
            "currency": "USD",
            "status": "projected_surplus",
        },
        "confidence": "medium",
        "confidence_caveat": (
            "Projection is a deterministic synthetic demo input, not a production forecast."
        ),
        "source_metadata": _source_metadata(
            "synthetic_cash_projection_fixture",
            ["No live market data, production cash-flow model, or real client plan is used."],
        ),
    }


def build_cash_flow_support_inputs(outputs: dict[str, Any]) -> dict[str, Any]:
    need = outputs["cash_flow_need_profile"]["stated_annual_cash_need"]["amount"]
    generated = outputs["cash_flow_history_summary"]["cash_generated_last_period"]["amount"]
    paid = outputs["cash_flow_history_summary"]["cash_paid_out_last_period"]["amount"]
    projected = outputs["cash_flow_projection_summary"]["projected_cash_generation"]["amount"]
    surplus = outputs["cash_flow_projection_summary"]["projected_surplus_shortfall"]["amount"]

    return {
        "schema_version": "cash_flow_support_inputs.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "report_family_id": "cash_flow_support_summary",
        "status": "ready_for_synthetic_demo_whole_portfolio_summary",
        "cash_flow_support_readiness_no_longer_only_missing_inputs": True,
        "required_inputs": {
            "stated_annual_cash_need": need,
            "cash_generated_last_period": generated,
            "cash_paid_out_last_period": paid,
            "projected_cash_generation": projected,
            "projected_surplus_shortfall": surplus,
            "currency": "USD",
        },
        "support_logic": {
            "need_coverage_ratio": round(projected / need, 6),
            "projected_surplus_shortfall": surplus,
            "support_status": "projected_surplus",
            "calculation": "projected_cash_generation - stated_annual_cash_need",
        },
        "readiness": {
            "cash_flow_support_summary_ready": True,
            "cash_flow_by_manager_sleeve_ready": False,
            "client_ready_with_real_data": False,
            "synthetic_demo_only": True,
        },
        "input_files": [
            ARTIFACT_FILES["cash_flow_need_profile"],
            ARTIFACT_FILES["cash_flow_history_summary"],
            ARTIFACT_FILES["cash_flow_projection_summary"],
        ],
        "caveats": [
            "Whole-portfolio synthetic cash inputs exist for demo report generation.",
            "Manager/sleeve cash-flow support remains gated until reliable source cash-flow detail exists.",
        ],
    }


def build_manager_mandate_catalog(context: dict[str, Any]) -> dict[str, Any]:
    base_value_by_manager: dict[str, float] = defaultdict(float)
    count_by_manager: dict[str, int] = defaultdict(int)
    for row in context["in_scope_positions"]:
        manager_id = row["position"]["manager_id"]
        base_value_by_manager[manager_id] += float(row["base_valuation"]["value"])
        count_by_manager[manager_id] += 1

    sleeve_by_id = {
        sleeve["sleeve_id"]: sleeve for sleeve in context["position_universe"]["sleeves"]
    }

    manager_mandates = []
    for manager in sorted(context["position_universe"]["managers"], key=lambda item: item["manager_id"]):
        manager_id = manager["manager_id"]
        base_value = round(base_value_by_manager[manager_id], 2)
        share = _safe_divide(base_value, context["base_portfolio_value"])
        manager_mandates.append(
            {
                "manager_id": manager_id,
                "manager_display_name": manager["display_name"],
                "sleeve_ids": list(manager["sleeves"]),
                "sleeve_display_names": [
                    sleeve_by_id[sleeve_id]["display_name"] for sleeve_id in manager["sleeves"]
                ],
                "approved_role_label": manager["mandate"],
                "intended_role": manager["intended_role"],
                "mandate_expression_summary": manager["strategy_summary"],
                "expected_contribution": manager["expected_contribution"],
                "liquidity_profile": manager["liquidity_profile"],
                "primary_themes": list(manager["primary_themes"]),
                "key_risk_for_report": _manager_key_risk(manager),
                "base_value": base_value,
                "portfolio_share": share,
                "position_count": count_by_manager[manager_id],
                "approval_status": "approved_for_synthetic_demo_reports",
                "synthetic_data": True,
            }
        )

    sleeve_mandates = [
        {
            "sleeve_id": sleeve["sleeve_id"],
            "sleeve_display_name": sleeve["display_name"],
            "manager_id": sleeve["manager_id"],
            "approved_role_label": sleeve["mandate"],
            "themes": list(sleeve["themes"]),
            "synthetic_data": True,
        }
        for sleeve in sorted(context["position_universe"]["sleeves"], key=lambda item: item["sleeve_id"])
    ]

    return {
        "schema_version": "manager_mandate_catalog.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "portfolio_snapshot_id": context["portfolio_snapshot_id"],
        "valuation_date": context["valuation_date"],
        "manager_mandates": manager_mandates,
        "sleeve_mandates": sleeve_mandates,
        "coverage_summary": {
            "manager_count": len(manager_mandates),
            "sleeve_count": len(sleeve_mandates),
            "current_managers_covered": True,
            "current_sleeves_covered": True,
            "role_language_repeats_manager_name": False,
        },
        "report_readiness": {
            "manager_role_summary_ready": True,
            "single_manager_detail_possible_later": True,
            "manager_by_lens_exposure_possible_with_lens_assignments": True,
        },
        "source_metadata": _source_metadata(
            "synthetic_position_universe_manager_fields",
            [context["source_paths"]["position_universe"]],
        ),
    }


def build_lens_definition(
    *,
    lens_id: str,
    display_name: str,
    purpose: str,
    primary_buckets: tuple[tuple[str, str, str], ...],
    secondary_flags: tuple[tuple[str, str, str], ...],
    neutral_bucket_id: str,
) -> dict[str, Any]:
    return {
        "schema_version": "synthetic_thesis_lens.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "lens_id": lens_id,
        "lens_version": "v1",
        "display_name": display_name,
        "purpose": purpose,
        "primary_buckets": [
            {
                "bucket_id": bucket_id,
                "display_name": label,
                "advisor_safe_description": description,
                "additive": True,
            }
            for bucket_id, label, description in primary_buckets
        ],
        "secondary_flags": [
            {
                "flag_id": flag_id,
                "display_name": label,
                "advisor_safe_description": description,
                "additive": False,
            }
            for flag_id, label, description in secondary_flags
        ],
        "neutral_bucket_id": neutral_bucket_id,
        "review_required_bucket_id": "unclassified_review_required",
        "assignment_policy": {
            "policy_id": f"{lens_id}_deterministic_synthetic_assignment_policy_v1",
            "assignment_mode": "one_primary_bucket_per_position",
            "weighted_splits_allowed": False,
            "secondary_flags_are_non_additive": True,
            "uses_llm": False,
            "rule_basis": [
                "synthetic position display name",
                "synthetic classifications",
                "synthetic themes",
                "synthetic scenario exposure hints",
                "synthetic manager and sleeve labels",
                "valuation coverage and review flags",
            ],
        },
        "validation_rules": {
            "every_in_scope_position_requires_assignment": True,
            "primary_bucket_ids_are_mutually_exclusive": True,
            "neutral_bucket_required": True,
            "review_bucket_required": True,
            "bucket_totals_must_reconcile_to_portfolio_base_value": True,
        },
        "approval_metadata": {
            "approval_status": "approved_for_synthetic_demo_prerequisite_pack",
            "approved_by": "synthetic_demo_fixture",
            "approved_at": GENERATED_AT,
            "local_only": True,
        },
    }


def build_position_lens_assignments(
    context: dict[str, Any],
    *,
    lens: dict[str, Any],
    classify: Any,
) -> dict[str, Any]:
    bucket_ids = {bucket["bucket_id"] for bucket in lens["primary_buckets"]}
    flag_ids = {flag["flag_id"] for flag in lens["secondary_flags"]}
    assignments = []

    for row in context["in_scope_positions"]:
        classification = classify(row)
        primary_bucket_id = classification["primary_bucket_id"]
        if primary_bucket_id not in bucket_ids:
            raise ValueError(f"Invalid bucket for {lens['lens_id']}: {primary_bucket_id}")
        secondary_flag_ids = [
            flag_id for flag_id in classification["secondary_flag_ids"] if flag_id in flag_ids
        ]
        base_value = round(float(row["base_valuation"]["value"]), 2)
        assignments.append(
            {
                "position_id": row["position"]["position_id"],
                "display_name": row["position"]["display_name"],
                "manager_id": row["position"]["manager_id"],
                "sleeve_id": row["position"]["sleeve_id"],
                "instrument_id": row["position"]["instrument_id"],
                "base_value": base_value,
                "primary_bucket_id": primary_bucket_id,
                "secondary_flag_ids": secondary_flag_ids,
                "assignment_method": classification["assignment_method"],
                "confidence": classification["confidence"],
                "advisor_safe_rationale": classification["advisor_safe_rationale"],
                "missing_evidence": classification["missing_evidence"],
                "review_status": classification["review_status"],
                "source_metadata": {
                    "source": "deterministic_synthetic_position_rule",
                    "synthetic_data": True,
                    "llm_used": False,
                    "external_data_used": False,
                },
            }
        )

    coverage = _assignment_coverage(lens, assignments, context["base_portfolio_value"])
    return {
        "schema_version": "position_lens_assignments.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "lens_id": lens["lens_id"],
        "lens_version": lens["lens_version"],
        "portfolio_id": context["portfolio_id"],
        "portfolio_snapshot_id": context["portfolio_snapshot_id"],
        "valuation_date": context["valuation_date"],
        "assignment_scope": {
            "scope_type": "whole_portfolio",
            "in_scope_position_count": len(assignments),
            "denominator": "base_portfolio_value",
            "base_portfolio_value": context["base_portfolio_value"],
        },
        "neutral_bucket_id": lens["neutral_bucket_id"],
        "review_required_bucket_id": lens["review_required_bucket_id"],
        "assignments": assignments,
        "coverage_summary": coverage["coverage_summary"],
        "bucket_exposure_summary": coverage["bucket_exposure_summary"],
        "review_summary": coverage["review_summary"],
        "source_metadata": _source_metadata(
            "synthetic_lens_assignment_rules",
            [
                "Assignments are deterministic synthetic prerequisite data.",
                "No raw evidence packets or LLM responses are included.",
            ],
        ),
    }


def build_synthetic_lens_catalog(outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "synthetic_lens_catalog.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "lens_count": 2,
        "lenses": [
            _catalog_lens_row(
                outputs["ai_adoption_lens_v1"],
                ARTIFACT_FILES["ai_adoption_lens_v1"],
                ARTIFACT_FILES["position_lens_assignments_ai_adoption_v1"],
            ),
            _catalog_lens_row(
                outputs["energy_security_lens_v1"],
                ARTIFACT_FILES["energy_security_lens_v1"],
                ARTIFACT_FILES["position_lens_assignments_energy_security_v1"],
            ),
        ],
        "approval_metadata": {
            "approval_status": "approved_for_synthetic_demo_prerequisite_pack",
            "local_only": True,
        },
    }


def build_lens_exposure_prerequisite_summary(
    context: dict[str, Any], outputs: dict[str, Any]
) -> dict[str, Any]:
    lens_rows = []
    for output_name, assignment_file_key, lens_file_key in (
        (
            "position_lens_assignments_ai_adoption_v1",
            "position_lens_assignments_ai_adoption_v1",
            "ai_adoption_lens_v1",
        ),
        (
            "position_lens_assignments_energy_security_v1",
            "position_lens_assignments_energy_security_v1",
            "energy_security_lens_v1",
        ),
    ):
        assignment = outputs[output_name]
        lens_rows.append(
            {
                "lens_id": assignment["lens_id"],
                "lens_display_name": outputs[lens_file_key]["display_name"],
                "lens_file": ARTIFACT_FILES[lens_file_key],
                "assignment_file": ARTIFACT_FILES[assignment_file_key],
                "full_lens_exposure_ready": True,
                "manager_by_lens_exposure_possible": True,
                "in_scope_position_count": assignment["assignment_scope"]["in_scope_position_count"],
                "assigned_position_count": assignment["coverage_summary"]["assigned_position_count"],
                "unassigned_position_count": assignment["coverage_summary"]["unassigned_position_count"],
                "base_value_total": assignment["coverage_summary"]["base_value_total"],
                "assigned_base_value": assignment["coverage_summary"]["assigned_base_value"],
                "assigned_base_value_share": assignment["coverage_summary"]["assigned_base_value_share"],
                "review_required_base_value_share": assignment["review_summary"][
                    "review_required_base_value_share"
                ],
                "bucket_exposure_summary": assignment["bucket_exposure_summary"],
            }
        )

    return {
        "schema_version": "lens_exposure_prerequisite_summary.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "portfolio_id": context["portfolio_id"],
        "portfolio_snapshot_id": context["portfolio_snapshot_id"],
        "valuation_date": context["valuation_date"],
        "base_portfolio_value": context["base_portfolio_value"],
        "lens_count": len(lens_rows),
        "lenses": lens_rows,
        "report_readiness": {
            "full_lens_exposure": "ready_for_synthetic_demo",
            "manager_by_lens_exposure": "possible_next_with_same_lens_and_manager_mapping",
            "scenario_by_lens": "possible_next_if_a_tranche_aggregates_existing_revaluation_impacts_by_lens",
        },
        "caveats": [
            "Assignments are synthetic, local-only prerequisite artifacts.",
            "Client-facing lens reports still need report-view generation and product review.",
        ],
    }


def build_scenario_lens_readiness_summary(
    context: dict[str, Any], outputs: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "scenario_lens_readiness_summary.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "available_full_revaluation_scenario_ids": list(context["portfolio_summaries"].keys()),
        "complete_lens_assignment_ids": [
            outputs["position_lens_assignments_ai_adoption_v1"]["lens_id"],
            outputs["position_lens_assignments_energy_security_v1"]["lens_id"],
        ],
        "scenario_lens_rows": [
            {
                "scenario_id": "ai_chip_selloff",
                "scenario_display_name": "AI / Chip Selloff",
                "compatible_lens_ids": [AI_LENS_ID],
                "readiness_status": "ready_for_future_scenario_by_lens_aggregation",
                "note": "Full revaluation rows and complete AI Adoption assignments both exist.",
            },
            {
                "scenario_id": "rate_shock",
                "scenario_display_name": "Rate Shock",
                "compatible_lens_ids": [],
                "readiness_status": "no_specific_lens_pair_selected",
                "note": "Rate Shock remains usable for current portfolio downside, not a lens report by itself.",
            },
            {
                "scenario_id": "energy_shock",
                "scenario_display_name": "Energy Shock",
                "compatible_lens_ids": [ENERGY_LENS_ID],
                "readiness_status": "lens_ready_but_full_revaluation_scenario_not_yet_generated",
                "note": "Energy Security assignments exist; a full energy-shock revaluation bundle is not part of this tranche.",
            },
        ],
        "not_created_in_this_pack": [
            "scenario_by_lens_report_view",
            "benchmark_or_proxy_comparison",
            "probabilistic_range",
        ],
    }


def build_manifest(context: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "synthetic_report_prerequisite_pack_manifest.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "portfolio_id": context["portfolio_id"],
        "portfolio_snapshot_id": context["portfolio_snapshot_id"],
        "valuation_date": context["valuation_date"],
        "base_portfolio_value": context["base_portfolio_value"],
        "artifact_count": len(ARTIFACT_FILES),
        "artifacts": [
            {
                "artifact_name": name,
                "path": _as_posix(DEFAULT_OUTPUT_DIR / filename),
                "synthetic_data": True,
            }
            for name, filename in ARTIFACT_FILES.items()
        ],
        "source_files": list(context["source_paths"].values()),
        "report_prerequisites_unblocked": [
            "cash_flow_support_summary_whole_portfolio_synthetic_demo",
            "manager_role_summary_synthetic_mandate_catalog",
            "full_lens_exposure_ai_adoption",
            "full_lens_exposure_energy_security",
        ],
        "possible_next_report_prerequisites": [
            "manager_by_lens_exposure_with_same_lens_and_manager_mapping",
            "scenario_by_lens_aggregation_from_existing_revaluation_rows",
        ],
        "still_gated": [
            "cash_flow_by_manager_sleeve",
            "scenario_versus_benchmark",
            "integrated_performance_attribution",
            "probabilistic_scenario_range",
            "current_vs_proposed_portfolio",
            "timing_attribution",
        ],
        "readiness_summary": {
            "cash_flow_support_summary_ready": outputs["cash_flow_support_inputs"]["readiness"][
                "cash_flow_support_summary_ready"
            ],
            "manager_role_summary_ready": outputs["manager_mandate_catalog"]["report_readiness"][
                "manager_role_summary_ready"
            ],
            "full_lens_exposure_ready": outputs["lens_exposure_prerequisite_summary"][
                "report_readiness"
            ]["full_lens_exposure"],
            "advisor_ui_report_wiring_paused": True,
        },
        "boundaries": [
            "No advisor UI changes.",
            "No generated-report wiring.",
            "No backend endpoints.",
            "No Docker or deployment changes.",
            "No live or real client data.",
            "No benchmark, performance, probabilistic, or proposed-portfolio analytics.",
        ],
    }


def validate_pack(context: dict[str, Any], outputs: dict[str, Any]) -> None:
    for name, payload in outputs.items():
        if payload.get("synthetic_data") is not True:
            raise ValueError(f"{name} must be marked synthetic_data=true")

    position_ids = {
        row["position"]["position_id"] for row in context["in_scope_positions"]
    }
    for output_name, lens_name in (
        ("position_lens_assignments_ai_adoption_v1", "ai_adoption_lens_v1"),
        ("position_lens_assignments_energy_security_v1", "energy_security_lens_v1"),
    ):
        assignments = outputs[output_name]
        lens = outputs[lens_name]
        valid_bucket_ids = {bucket["bucket_id"] for bucket in lens["primary_buckets"]}
        valid_flag_ids = {flag["flag_id"] for flag in lens["secondary_flags"]}
        assignment_ids = [row["position_id"] for row in assignments["assignments"]]
        if set(assignment_ids) != position_ids or len(assignment_ids) != len(position_ids):
            raise ValueError(f"{output_name} must assign every in-scope position exactly once")
        for row in assignments["assignments"]:
            if row["primary_bucket_id"] not in valid_bucket_ids:
                raise ValueError(f"{output_name} has invalid primary bucket")
            if not set(row["secondary_flag_ids"]) <= valid_flag_ids:
                raise ValueError(f"{output_name} has invalid secondary flag")
            for key in row:
                if "weight" in key.lower():
                    raise ValueError(f"{output_name} must not contain weighted assignment fields")

        coverage = assignments["coverage_summary"]
        if coverage["unassigned_position_count"] != 0:
            raise ValueError(f"{output_name} has unassigned positions")
        if coverage["assigned_base_value_share"] != 1.0:
            raise ValueError(f"{output_name} does not reconcile to 100 percent of base value")
        bucket_total = round(
            sum(float(row["base_value"]) for row in assignments["bucket_exposure_summary"]), 2
        )
        if bucket_total != context["base_portfolio_value"]:
            raise ValueError(f"{output_name} bucket base value does not reconcile")


def _classify_ai_adoption(row: dict[str, Any]) -> dict[str, Any]:
    text = _classification_text(row)
    review = _needs_review(row)
    flags = []
    method = "deterministic_keyword_rule"
    missing: list[str] = []

    if _contains_any(text, ("asia", "taiwan", "semiconductor", "chip", "packaging", "fabrication")):
        flags.append("china_taiwan_supply_chain_exposure")
    if _contains_any(text, ("power", "grid", "data center", "cooling", "copper", "uranium", "pipeline")):
        flags.append("power_demand_sensitivity")
    if _contains_any(text, ("bank", "healthcare", "municipal", "crypto", "bitcoin", "ethereum")):
        flags.append("regulatory_sensitivity")
    if _contains_any(text, ("private", "opaque", "lp", "fund", "sidecar", "held_at_mark", "review_required")):
        flags.append("private_market_opacity")
    if _contains_any(text, ("chip", "semiconductor", "accelerator", "compute", "semicap", "packaging")):
        flags.append("hardware_cycle_sensitivity")

    if _contains_any(text, ("opaque manager-level", "placeholder", "macro overlay", "collar", "put spread")):
        bucket = "unclassified_review_required"
        confidence = "review_required"
        method = "review_required_fallback_rule"
        rationale = "Opaque or derivative-like synthetic holding is routed to review for AI lens exposure."
        missing = ["approved look-through evidence"]
    elif _is_cash_like(row):
        bucket = "neutral_low_direct_ai_exposure"
        confidence = "medium"
        method = "neutral_default_rule"
        rationale = "Synthetic cash or money-market holding has low direct AI exposure."
    elif _contains_any(text, ("data center", "grid", "cooling", "power campus", "fiber interconnect")):
        bucket = "data_center_power_bottleneck_exposure"
        confidence = "review_required" if review else "high"
        rationale = "Synthetic labels indicate data center, power, cooling, grid, or interconnect exposure."
    elif _contains_any(text, ("cloud", "enterprise ai", "software", "platform", "ai growth")):
        bucket = "ai_model_platform_exposure"
        confidence = "review_required" if review else "high"
        rationale = "Synthetic labels indicate cloud, platform, software, or AI growth exposure."
    elif _contains_any(
        text,
        (
            "ai compute",
            "chip",
            "semiconductor",
            "accelerator",
            "semicap",
            "packaging",
            "ai chip basket",
            "edge server",
            "ai infrastructure",
        ),
    ):
        bucket = "core_ai_infrastructure_hardware"
        confidence = "review_required" if review else "high"
        rationale = "Synthetic labels indicate direct compute, chip, hardware, or AI infrastructure exposure."
    elif _contains_any(text, ("industrial", "payments", "healthcare", "consumer platform")):
        bucket = "ai_downstream_productivity_beneficiary"
        confidence = "medium"
        rationale = "Synthetic labels indicate operating businesses that may be downstream AI adopters."
    elif _contains_any(text, ("bank", "consumer staples")):
        bucket = "ai_disrupted_incumbent"
        confidence = "medium"
        rationale = "Synthetic labels indicate incumbents that may face AI-enabled business model pressure."
    elif review:
        bucket = "unclassified_review_required"
        confidence = "review_required"
        method = "review_required_fallback_rule"
        rationale = "Synthetic review flag prevents stronger AI lens assignment."
        missing = ["approved look-through evidence"]
    else:
        bucket = "neutral_low_direct_ai_exposure"
        confidence = "medium"
        method = "neutral_default_rule"
        rationale = "Synthetic labels do not indicate material direct AI exposure."

    return _classification_result(
        bucket=bucket,
        flags=flags,
        method=method,
        confidence=confidence,
        rationale=rationale,
        missing_evidence=missing,
    )


def _classify_energy_security(row: dict[str, Any]) -> dict[str, Any]:
    text = _classification_text(row)
    review = _needs_review(row)
    flags = []
    method = "deterministic_keyword_rule"
    missing: list[str] = []

    if _contains_any(text, ("power", "grid", "data center", "cooling", "renewable", "uranium")):
        flags.append("power_reliability_sensitivity")
    if _contains_any(text, ("data center", "ai infrastructure", "compute", "cloud", "cooling")):
        flags.append("data_center_power_demand")
    if _contains_any(text, ("renewable", "pipeline", "real estate", "infrastructure", "industrial")):
        flags.append("transition_policy_sensitivity")
    if _contains_any(text, ("commodity", "wti", "energy", "uranium", "copper", "gold", "pipeline")):
        flags.append("commodity_price_sensitivity")
    if _contains_any(text, ("private", "opaque", "lp", "fund", "sidecar", "held_at_mark", "review_required")):
        flags.append("private_market_opacity")

    if _contains_any(text, ("opaque manager-level", "placeholder", "macro overlay", "collar", "put spread")):
        bucket = "unclassified_review_required"
        confidence = "review_required"
        method = "review_required_fallback_rule"
        rationale = "Opaque or derivative-like synthetic holding is routed to review for Energy Security exposure."
        missing = ["approved look-through evidence"]
    elif _is_cash_like(row):
        bucket = "neutral_low_direct_energy_exposure"
        confidence = "medium"
        method = "neutral_default_rule"
        rationale = "Synthetic cash or money-market holding has low direct energy-security exposure."
    elif _contains_any(text, ("wti", "pipeline", "uranium", "power supply", "energy exposure")):
        bucket = "energy_supply_beneficiary"
        confidence = "review_required" if review else "high"
        rationale = "Synthetic labels indicate direct energy supply or fuel exposure."
    elif _contains_any(text, ("grid", "renewable power", "power campus", "fiber interconnect")):
        bucket = "grid_infrastructure_beneficiary"
        confidence = "review_required" if review else "high"
        rationale = "Synthetic labels indicate grid, power, or infrastructure beneficiary exposure."
    elif _contains_any(text, ("commodity", "copper", "gold")):
        bucket = "commodity_supply_security_exposure"
        confidence = "high"
        rationale = "Synthetic labels indicate commodity or resource security exposure."
    elif _contains_any(text, ("data center", "cooling", "compute", "cloud", "semiconductor", "industrial")):
        bucket = "energy_input_cost_sensitive"
        confidence = "review_required" if review else "medium"
        rationale = "Synthetic labels indicate power-intensive business exposure."
    elif _contains_any(text, ("real estate", "multifamily", "logistics", "renewable", "pipeline")):
        bucket = "transition_policy_sensitive"
        confidence = "review_required" if review else "medium"
        rationale = "Synthetic labels indicate real-asset or transition-policy sensitivity."
    elif review:
        bucket = "unclassified_review_required"
        confidence = "review_required"
        method = "review_required_fallback_rule"
        rationale = "Synthetic review flag prevents stronger Energy Security lens assignment."
        missing = ["approved look-through evidence"]
    else:
        bucket = "neutral_low_direct_energy_exposure"
        confidence = "medium"
        method = "neutral_default_rule"
        rationale = "Synthetic labels do not indicate material direct energy-security exposure."

    return _classification_result(
        bucket=bucket,
        flags=flags,
        method=method,
        confidence=confidence,
        rationale=rationale,
        missing_evidence=missing,
    )


def _assignment_coverage(
    lens: dict[str, Any], assignments: list[dict[str, Any]], base_portfolio_value: float
) -> dict[str, Any]:
    bucket_rows = []
    by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for assignment in assignments:
        by_bucket[assignment["primary_bucket_id"]].append(assignment)

    for bucket in lens["primary_buckets"]:
        rows = by_bucket.get(bucket["bucket_id"], [])
        base_value = round(sum(float(row["base_value"]) for row in rows), 2)
        bucket_rows.append(
            {
                "bucket_id": bucket["bucket_id"],
                "bucket_display_name": bucket["display_name"],
                "position_count": len(rows),
                "base_value": base_value,
                "portfolio_share": _safe_divide(base_value, base_portfolio_value),
                "review_required_position_count": sum(
                    1 for row in rows if row["confidence"] == "review_required"
                ),
                "review_required_base_value": round(
                    sum(
                        float(row["base_value"])
                        for row in rows
                        if row["confidence"] == "review_required"
                    ),
                    2,
                ),
            }
        )

    assigned_value = round(sum(float(row["base_value"]) for row in assignments), 2)
    review_value = round(
        sum(
            float(row["base_value"])
            for row in assignments
            if row["primary_bucket_id"] == lens["review_required_bucket_id"]
            or row["confidence"] == "review_required"
        ),
        2,
    )
    return {
        "coverage_summary": {
            "in_scope_position_count": len(assignments),
            "assigned_position_count": len(assignments),
            "unassigned_position_count": 0,
            "base_value_total": round(base_portfolio_value, 2),
            "assigned_base_value": assigned_value,
            "assigned_base_value_share": _safe_divide(assigned_value, base_portfolio_value),
            "assignment_policy": "single_primary_bucket_per_position_no_weighted_splits",
        },
        "bucket_exposure_summary": bucket_rows,
        "review_summary": {
            "review_required_bucket_id": lens["review_required_bucket_id"],
            "review_required_position_count": sum(
                1
                for row in assignments
                if row["primary_bucket_id"] == lens["review_required_bucket_id"]
                or row["confidence"] == "review_required"
            ),
            "review_required_base_value": review_value,
            "review_required_base_value_share": _safe_divide(review_value, base_portfolio_value),
        },
    }


def _classification_result(
    *,
    bucket: str,
    flags: list[str],
    method: str,
    confidence: str,
    rationale: str,
    missing_evidence: list[str],
) -> dict[str, Any]:
    deduped_flags = sorted(set(flags))
    return {
        "primary_bucket_id": bucket,
        "secondary_flag_ids": deduped_flags,
        "assignment_method": method,
        "confidence": confidence,
        "advisor_safe_rationale": rationale,
        "missing_evidence": missing_evidence,
        "review_status": (
            "review_required" if confidence == "review_required" else "approved_synthetic_demo"
        ),
    }


def _classification_text(row: dict[str, Any]) -> str:
    source = row["source_position"]
    position = row["position"]
    instrument = row["instrument"]
    classifications = dict(source.get("classifications", {}))
    classifications.pop("manager_role_or_mandate", None)
    fields = [
        position.get("display_name"),
        position.get("valuation_confidence"),
        position.get("valuation_method_hint"),
        row["base_valuation"].get("coverage_status"),
        row["base_valuation"].get("confidence"),
        instrument.get("display_name"),
        instrument.get("instrument_type"),
        json.dumps(instrument.get("reference_data", {}), sort_keys=True),
        json.dumps(classifications, sort_keys=True),
        json.dumps(source.get("themes", []), sort_keys=True),
        json.dumps(source.get("position_story_tags", []), sort_keys=True),
        json.dumps(source.get("scenario_exposure_hints", []), sort_keys=True),
        json.dumps(source.get("data_quality_flags", []), sort_keys=True),
    ]
    return " ".join(str(field).lower() for field in fields if field is not None)


def _needs_review(row: dict[str, Any]) -> bool:
    position = row["position"]
    base = row["base_valuation"]
    source = row["source_position"]
    return bool(
        position.get("human_review_required")
        or base.get("review_required")
        or base.get("coverage_status") in {"review_required", "held_at_mark_with_caveat"}
        or source.get("human_review_required")
    )


def _is_cash_like(row: dict[str, Any]) -> bool:
    source = row["source_position"]
    instrument = row["instrument"]
    classifications = source.get("classifications", {})
    text = " ".join(
        str(value).lower()
        for value in (
            classifications.get("asset_class"),
            classifications.get("instrument_type"),
            source.get("instrument_type"),
            instrument.get("instrument_type"),
            source.get("display_name"),
            instrument.get("display_name"),
        )
        if value is not None
    )
    return any(marker in text for marker in ("cash", "money_market", "money market", "treasury bill"))


def _contains_any(value: str, needles: tuple[str, ...]) -> bool:
    return any(needle in value for needle in needles)


def _catalog_lens_row(lens: dict[str, Any], lens_file: str, assignment_file: str) -> dict[str, Any]:
    return {
        "lens_id": lens["lens_id"],
        "lens_version": lens["lens_version"],
        "display_name": lens["display_name"],
        "lens_file": lens_file,
        "assignment_file": assignment_file,
        "neutral_bucket_id": lens["neutral_bucket_id"],
        "review_required_bucket_id": lens["review_required_bucket_id"],
        "full_lens_exposure_ready": True,
        "supported_report_families": [
            "full_lens_exposure",
            "manager_by_lens_exposure",
            "scenario_by_lens_after_aggregation",
        ],
    }


def _manager_key_risk(manager: dict[str, Any]) -> str:
    manager_id = manager["manager_id"]
    if manager_id == "mgr_a_growth_ai_infrastructure":
        return "AI cycle, semiconductor supply-chain, and power bottleneck drawdown sensitivity."
    if manager_id == "mgr_b_core_quality_equity":
        return "Broad equity drawdown and platform overlap with the growth sleeve."
    if manager_id == "mgr_c_income_cash_generation":
        return "Rate, credit-spread, and income sustainability sensitivity."
    if manager_id == "mgr_d_private_real_assets":
        return "Illiquidity, stale marks, and opaque private-market look-through."
    if manager_id == "mgr_e_liquidity_defensive":
        return "Opportunity cost in risk-on markets and short-rate reinvestment sensitivity."
    if manager_id == "mgr_f_opportunistic_macro":
        return "Complex macro, commodity, currency, crypto, and option-like exposure."
    return "Synthetic manager exposure requires advisor review."


def _source_metadata(source: str, notes: list[str]) -> dict[str, Any]:
    return {
        "source": source,
        "synthetic_data": True,
        "local_only": True,
        "external_data_used": False,
        "notes": notes,
    }


def _safe_divide(numerator: Any, denominator: Any) -> float:
    denominator_float = float(denominator)
    if denominator_float == 0:
        return 0.0
    return round(float(numerator) / denominator_float, 6)


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the local synthetic report prerequisite pack."
    )
    parser.add_argument("--revaluation-dir", default=str(DEFAULT_REVALUATION_DIR))
    parser.add_argument("--position-universe-path", default=str(DEFAULT_POSITION_UNIVERSE_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outputs = generate_synthetic_report_prerequisite_pack(
        revaluation_dir=args.revaluation_dir,
        position_universe_path=args.position_universe_path,
        output_dir=args.output_dir,
    )
    lens_summary = outputs["lens_exposure_prerequisite_summary"]
    cash = outputs["cash_flow_support_inputs"]

    print(f"Synthetic report prerequisite pack: {PACK_ID} -> {args.output_dir}")
    print(f"Artifacts: {len(ARTIFACT_FILES)}")
    print(
        "Cash-Flow Support Summary: "
        + ("ready" if cash["readiness"]["cash_flow_support_summary_ready"] else "not ready")
    )
    print(
        "Full Lens Exposure: "
        + lens_summary["report_readiness"]["full_lens_exposure"]
        + f" ({lens_summary['lens_count']} lenses)"
    )
    print("Manager Role Summary: ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
