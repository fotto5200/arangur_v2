from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-08T00:00:00Z"
PACK_ID = "synthetic_policy_mandate_pack_v1"
PACK_VERSION = "2026-07-08"
GENERATOR_VERSION = "synthetic_policy_mandate_prerequisites.v1"

PERIOD_START = "2025-07-01"
PERIOD_END = "2026-06-30"
VALUATION_DATE = "2026-06-30"
BASE_CURRENCY = "USD"
TIE_OUT_TOLERANCE = 0.000001

DEFAULT_REVALUATION_DIR = Path("data/simulation/revaluation")
DEFAULT_REPORT_PREREQUISITE_DIR = Path(
    "data/simulation/report_prerequisites/synthetic_report_prerequisite_pack_v1"
)
DEFAULT_ATTRIBUTION_PREREQUISITE_DIR = Path(
    "data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1"
)
DEFAULT_ATTRIBUTION_CALCULATED_DIR = Path(
    "data/simulation/attribution_calculated/synthetic_attribution_engine_v1"
)
DEFAULT_OUTPUT_DIR = Path("data/simulation/policy_mandate_prerequisites") / PACK_ID

ARTIFACT_FILES = {
    "manifest": "synthetic_policy_mandate_pack_manifest.json",
    "policy_allocation_mode": "policy_allocation_mode.json",
    "policy_allocation_profile": "policy_allocation_profile.json",
    "actual_manager_allocation_snapshot": "actual_manager_allocation_snapshot.json",
    "allocation_drift_summary": "allocation_drift_summary.json",
    "imputed_current_allocation_baseline": (
        "imputed_current_allocation_baseline.json"
    ),
    "manager_mandate_benchmark_catalog": "manager_mandate_benchmark_catalog.json",
    "manager_benchmark_basis_map": "manager_benchmark_basis_map.json",
    "policy_level_attribution_inputs": "policy_level_attribution_inputs.json",
    "equal_weight_diagnostic_attribution_classification": (
        "equal_weight_diagnostic_attribution_classification.json"
    ),
    "policy_mandate_readiness_summary": "policy_mandate_readiness_summary.json",
}

VALID_DRIFT_STATUSES = {
    "within_tolerance",
    "review",
    "material_drift",
    "imputed_baseline_no_drift",
}

MANAGER_POLICY_TARGETS = [
    {
        "manager_id": "mgr_a_growth_ai_infrastructure",
        "target_weight": 0.22,
        "policy_bucket_id": "high_upside_optionality_thematic_growth",
        "rebalance_tolerance": 0.035,
        "client_safe_description": (
            "Growth engine for AI infrastructure and related public equity exposure."
        ),
        "advisor_notes": (
            "High-upside sleeve; drift should be reviewed in context of volatility and "
            "realized performance."
        ),
    },
    {
        "manager_id": "mgr_b_core_quality_equity",
        "target_weight": 0.19,
        "policy_bucket_id": "core_quality_growth",
        "rebalance_tolerance": 0.035,
        "client_safe_description": (
            "Core public equity allocation intended to compound through higher-quality "
            "businesses."
        ),
        "advisor_notes": "Anchor public-equity growth sleeve with normal rebalance bands.",
    },
    {
        "manager_id": "mgr_c_income_cash_generation",
        "target_weight": 0.17,
        "policy_bucket_id": "income_capital_preservation",
        "rebalance_tolerance": 0.03,
        "client_safe_description": (
            "Income-oriented allocation intended to support cash generation and capital "
            "preservation."
        ),
        "advisor_notes": "Review underweights before assigning cause; flows may explain drift.",
    },
    {
        "manager_id": "mgr_d_private_real_assets",
        "target_weight": 0.2,
        "policy_bucket_id": "private_markets_real_assets",
        "rebalance_tolerance": 0.04,
        "client_safe_description": (
            "Private markets and real-asset allocation for diversification and inflation "
            "sensitivity."
        ),
        "advisor_notes": "Valuation marks can move slowly; drift should not be overread.",
    },
    {
        "manager_id": "mgr_e_liquidity_defensive",
        "target_weight": 0.14,
        "policy_bucket_id": "liquidity_reserve_defensive_ballast",
        "rebalance_tolerance": 0.025,
        "client_safe_description": (
            "Liquidity reserve and defensive ballast for near-term flexibility."
        ),
        "advisor_notes": "Useful quick-start baseline for cash and defensive allocation review.",
    },
    {
        "manager_id": "mgr_f_opportunistic_macro",
        "target_weight": 0.08,
        "policy_bucket_id": "high_upside_optionality_thematic_growth",
        "rebalance_tolerance": 0.025,
        "client_safe_description": (
            "Opportunistic macro allocation intended to add convexity and tactical breadth."
        ),
        "advisor_notes": "Small sleeve; evaluate in context of approved optionality budget.",
    },
]

POLICY_BUCKETS = [
    {
        "policy_bucket_id": "income_capital_preservation",
        "display_name": "Income / Capital Preservation",
        "linked_managers": ["mgr_c_income_cash_generation"],
        "role_description": "Support cash generation and preserve capital through income-oriented exposures.",
        "risk_budget_note": "Lower volatility role; review if materially below target.",
        "rebalance_tolerance": 0.03,
    },
    {
        "policy_bucket_id": "core_quality_growth",
        "display_name": "Core Quality Growth",
        "linked_managers": ["mgr_b_core_quality_equity"],
        "role_description": "Maintain a durable core public equity growth allocation.",
        "risk_budget_note": "Moderate equity risk budget with normal rebalance flexibility.",
        "rebalance_tolerance": 0.035,
    },
    {
        "policy_bucket_id": "private_markets_real_assets",
        "display_name": "Private Markets / Real Assets",
        "linked_managers": ["mgr_d_private_real_assets"],
        "role_description": "Diversify the portfolio through private market and real-asset exposures.",
        "risk_budget_note": "Valuation cadence can create apparent drift that needs review.",
        "rebalance_tolerance": 0.04,
    },
    {
        "policy_bucket_id": "liquidity_reserve_defensive_ballast",
        "display_name": "Liquidity Reserve / Defensive Ballast",
        "linked_managers": ["mgr_e_liquidity_defensive"],
        "role_description": "Keep near-term liquidity and defensive ballast explicit.",
        "risk_budget_note": "Tighter tolerance because this bucket supports flexibility.",
        "rebalance_tolerance": 0.025,
    },
    {
        "policy_bucket_id": "high_upside_optionality_thematic_growth",
        "display_name": "High-Upside Optionality / Thematic Growth",
        "linked_managers": [
            "mgr_a_growth_ai_infrastructure",
            "mgr_f_opportunistic_macro",
        ],
        "role_description": "Limit high-upside thematic and opportunistic exposure to an agreed sleeve.",
        "risk_budget_note": "Upside can create drift; review before interpreting as an error.",
        "rebalance_tolerance": 0.035,
    },
]


def generate_synthetic_policy_mandate_prerequisites(
    *,
    revaluation_dir: str | Path = DEFAULT_REVALUATION_DIR,
    report_prerequisite_dir: str | Path = DEFAULT_REPORT_PREREQUISITE_DIR,
    attribution_prerequisite_dir: str | Path = DEFAULT_ATTRIBUTION_PREREQUISITE_DIR,
    attribution_calculated_dir: str | Path = DEFAULT_ATTRIBUTION_CALCULATED_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    context = load_source_context(
        revaluation_dir=Path(revaluation_dir),
        report_prerequisite_dir=Path(report_prerequisite_dir),
        attribution_prerequisite_dir=Path(attribution_prerequisite_dir),
        attribution_calculated_dir=Path(attribution_calculated_dir),
    )

    outputs: dict[str, Any] = {}
    outputs["policy_allocation_mode"] = build_policy_allocation_mode(context)
    outputs["policy_allocation_profile"] = build_policy_allocation_profile(context)
    outputs["actual_manager_allocation_snapshot"] = (
        build_actual_manager_allocation_snapshot(context)
    )
    outputs["allocation_drift_summary"] = build_allocation_drift_summary(
        context,
        outputs["policy_allocation_profile"],
        outputs["actual_manager_allocation_snapshot"],
    )
    outputs["imputed_current_allocation_baseline"] = (
        build_imputed_current_allocation_baseline(
            context,
            outputs["actual_manager_allocation_snapshot"],
        )
    )
    outputs["manager_mandate_benchmark_catalog"] = (
        build_manager_mandate_benchmark_catalog(context)
    )
    outputs["manager_benchmark_basis_map"] = build_manager_benchmark_basis_map(
        context,
        outputs["policy_allocation_profile"],
        outputs["actual_manager_allocation_snapshot"],
        outputs["allocation_drift_summary"],
        outputs["manager_mandate_benchmark_catalog"],
    )
    outputs["policy_level_attribution_inputs"] = build_policy_level_attribution_inputs(
        context,
        outputs["policy_allocation_profile"],
        outputs["actual_manager_allocation_snapshot"],
        outputs["allocation_drift_summary"],
        outputs["manager_mandate_benchmark_catalog"],
    )
    outputs["equal_weight_diagnostic_attribution_classification"] = (
        build_equal_weight_diagnostic_classification(context)
    )
    outputs["policy_mandate_readiness_summary"] = build_readiness_summary(
        context,
        outputs,
    )
    outputs["manifest"] = build_manifest(context, outputs)

    validate_outputs(context, outputs)

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    for artifact_name, filename in ARTIFACT_FILES.items():
        _write_json(root / filename, outputs[artifact_name])

    return outputs


def load_source_context(
    *,
    revaluation_dir: Path,
    report_prerequisite_dir: Path,
    attribution_prerequisite_dir: Path,
    attribution_calculated_dir: Path,
) -> dict[str, Any]:
    position_catalog = _load_json(revaluation_dir / "position_catalog.json")
    instrument_catalog = _load_json(revaluation_dir / "instrument_catalog.json")
    manager_mandate_catalog = _load_json(
        report_prerequisite_dir / "manager_mandate_catalog.json"
    )
    attribution_manifest = _load_json(
        attribution_prerequisite_dir
        / "synthetic_attribution_prerequisite_pack_manifest.json"
    )
    manager_summary = _load_json(
        attribution_calculated_dir / "manager_calculated_attribution_summary.json"
    )
    whole_summary = _load_json(
        attribution_calculated_dir / "whole_portfolio_calculated_attribution_summary.json"
    )

    manager_mandates = {
        row["manager_id"]: row for row in manager_mandate_catalog["manager_mandates"]
    }
    manager_calculated = {
        row["manager_id"]: row for row in manager_summary["managers"]
    }

    return {
        "source_paths": {
            "source_position_catalog": _portable_path(
                revaluation_dir / "position_catalog.json"
            ),
            "source_instrument_catalog": _portable_path(
                revaluation_dir / "instrument_catalog.json"
            ),
            "source_manager_mandate_catalog": _portable_path(
                report_prerequisite_dir / "manager_mandate_catalog.json"
            ),
            "source_attribution_prerequisite_pack": _portable_path(
                attribution_prerequisite_dir
            ),
            "source_calculated_attribution_pack": _portable_path(
                attribution_calculated_dir
            ),
        },
        "position_catalog": position_catalog,
        "instrument_catalog": instrument_catalog,
        "manager_mandate_catalog": manager_mandate_catalog,
        "manager_mandates": manager_mandates,
        "attribution_manifest": attribution_manifest,
        "manager_summary": manager_summary,
        "manager_calculated": manager_calculated,
        "whole_summary": whole_summary,
        "manager_ids": [row["manager_id"] for row in MANAGER_POLICY_TARGETS],
        "manager_policy_targets": {
            row["manager_id"]: row for row in MANAGER_POLICY_TARGETS
        },
        "policy_bucket_map": {
            row["policy_bucket_id"]: row for row in POLICY_BUCKETS
        },
    }


def build_policy_allocation_mode(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "policy_allocation_mode.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "default_mode": "explicit_policy_allocation",
        "quick_start_alternative": "imputed_current_allocation",
        "modes": [
            {
                "mode": "explicit_policy_allocation",
                "display_name": "Explicit Policy Allocation",
                "purpose": "Use stated family/advisor target weights as the allocation benchmark.",
                "when_used": "Use when target weights by manager, mandate, sleeve, or policy bucket have been documented.",
                "what_question_it_answers": (
                    "Did the portfolio follow the agreed allocation, and did that allocation work?"
                ),
                "client_advisor_meaning": (
                    "Target-versus-actual drift can be discussed without blaming the manager for capital allocation."
                ),
                "caveats": [
                    "Synthetic local-demo policy only.",
                    "Drift needs interpretation before judgment.",
                ],
                "readiness_status": "ready_for_synthetic_demo",
            },
            {
                "mode": "imputed_current_allocation",
                "display_name": "Imputed Current Allocation",
                "purpose": "Accept current NAV weights as the starting policy baseline.",
                "when_used": "Use for quick-start setup or when no documented target weights exist yet.",
                "what_question_it_answers": (
                    "What happened given the capital already allocated today?"
                ),
                "client_advisor_meaning": (
                    "Suppresses policy allocation drift attribution until a target policy is agreed."
                ),
                "caveats": [
                    "Does not prove the current allocation was intentionally chosen.",
                    "Useful for setup, not a substitute for advisor/family policy approval.",
                ],
                "readiness_status": "ready_for_synthetic_demo_quick_start",
            },
            {
                "mode": "hybrid_policy_allocation",
                "display_name": "Hybrid Policy Allocation",
                "purpose": "Blend explicit targets with imputed or grouped baselines.",
                "when_used": "Use when only some sleeves have documented targets.",
                "what_question_it_answers": (
                    "Which parts of the allocation can be evaluated against targets, and which are baseline-only?"
                ),
                "client_advisor_meaning": (
                    "Keeps target-backed drift separate from current-baseline or grouped rows."
                ),
                "caveats": [
                    "Each row must disclose whether it is explicit, imputed, or grouped.",
                    "Do not calculate drift where no target exists.",
                ],
                "readiness_status": "design_ready_synthetic_demo_later",
            },
        ],
        "source_metadata": _source_metadata("synthetic_policy_allocation_modes"),
    }


def build_policy_allocation_profile(context: dict[str, Any]) -> dict[str, Any]:
    manager_rows = []
    for target in MANAGER_POLICY_TARGETS:
        mandate = context["manager_mandates"][target["manager_id"]]
        manager_rows.append(
            {
                "manager_id": target["manager_id"],
                "display_name": mandate["manager_display_name"],
                "target_weight": _round_weight(target["target_weight"]),
                "target_weight_source": "synthetic_policy_profile",
                "mandate_role": mandate["approved_role_label"],
                "policy_bucket_id": target["policy_bucket_id"],
                "rebalance_tolerance": _round_weight(target["rebalance_tolerance"]),
                "client_safe_description": target["client_safe_description"],
                "advisor_notes": target["advisor_notes"],
            }
        )

    manager_weight_by_id = {row["manager_id"]: row["target_weight"] for row in manager_rows}
    policy_bucket_rows = []
    for bucket in POLICY_BUCKETS:
        target_weight = _round_weight(
            sum(manager_weight_by_id[manager_id] for manager_id in bucket["linked_managers"])
        )
        policy_bucket_rows.append(
            {
                "policy_bucket_id": bucket["policy_bucket_id"],
                "display_name": bucket["display_name"],
                "target_weight": target_weight,
                "target_weight_source": "synthetic_policy_profile",
                "linked_managers": list(bucket["linked_managers"]),
                "role_description": bucket["role_description"],
                "risk_budget_note": bucket["risk_budget_note"],
                "rebalance_tolerance": _round_weight(bucket["rebalance_tolerance"]),
            }
        )

    return {
        "schema_version": "policy_allocation_profile.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "policy_profile_id": "northstar_synthetic_family_policy_allocation_v1",
        "policy_profile_display_name": "Northstar Synthetic Family Policy Allocation",
        "allocation_mode": "explicit_policy_allocation",
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "base_currency": BASE_CURRENCY,
        "manager_sleeve_target_allocation": manager_rows,
        "manager_sleeve_target_weight_sum": _round_weight(
            sum(row["target_weight"] for row in manager_rows)
        ),
        "policy_bucket_target_allocation": policy_bucket_rows,
        "policy_bucket_target_weight_sum": _round_weight(
            sum(row["target_weight"] for row in policy_bucket_rows)
        ),
        "equal_weight_theme_policy": False,
        "equal_weight_theme_policy_note": (
            "This policy profile does not use equal-weight AI Adoption theme buckets."
        ),
        "approval_status": "synthetic_demo_approved",
        "caveats": [
            "Synthetic advisor/family policy profile for local demo readiness.",
            "Not a client mandate document.",
        ],
        "source_metadata": _source_metadata("synthetic_policy_allocation_profile"),
    }


def build_actual_manager_allocation_snapshot(context: dict[str, Any]) -> dict[str, Any]:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    sleeve_ids: dict[str, set[str]] = defaultdict(set)
    for position in context["position_catalog"]["positions"]:
        manager_id = position["manager_id"]
        totals[manager_id] += float(position["current_mark"])
        counts[manager_id] += 1
        sleeve_ids[manager_id].add(position["sleeve_id"])

    total_value = _round_money(sum(totals.values()))
    manager_ids = list(context["manager_ids"])
    actual_weights = _round_values_preserve_sum(
        [totals[manager_id] / total_value for manager_id in manager_ids],
        1.0,
    )

    manager_rows = []
    for index, manager_id in enumerate(manager_ids):
        mandate = context["manager_mandates"][manager_id]
        manager_rows.append(
            {
                "manager_id": manager_id,
                "display_name": mandate["manager_display_name"],
                "actual_value": _round_money(totals[manager_id]),
                "actual_weight": actual_weights[index],
                "position_count": counts[manager_id],
                "sleeve_ids": sorted(sleeve_ids[manager_id]),
                "representation_notes": (
                    "Derived from current synthetic position marks grouped by manager."
                ),
            }
        )

    return {
        "schema_version": "actual_manager_allocation_snapshot.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "valuation_date": VALUATION_DATE,
        "base_currency": BASE_CURRENCY,
        "source_position_catalog": context["source_paths"]["source_position_catalog"],
        "manager_rows": manager_rows,
        "manager_count": len(manager_rows),
        "total_value": total_value,
        "actual_weight_sum": _round_weight(sum(row["actual_weight"] for row in manager_rows)),
        "reconciliation_status": "manager_weights_sum_to_100_percent",
        "caveats": [
            "Current synthetic marks are local demo values.",
            "Actual allocation is descriptive before it is evaluative.",
        ],
        "source_metadata": _source_metadata("actual_manager_allocation_snapshot"),
    }


def build_allocation_drift_summary(
    context: dict[str, Any],
    policy_profile: dict[str, Any],
    actual_snapshot: dict[str, Any],
) -> dict[str, Any]:
    actual_by_manager = {
        row["manager_id"]: row for row in actual_snapshot["manager_rows"]
    }
    policy_rows = policy_profile["manager_sleeve_target_allocation"]

    drift_rows = []
    for row in policy_rows:
        actual = actual_by_manager[row["manager_id"]]
        drift = _round_weight(actual["actual_weight"] - row["target_weight"])
        status = _drift_status(drift, row["rebalance_tolerance"])
        drift_rows.append(
            {
                "manager_id": row["manager_id"],
                "display_name": row["display_name"],
                "policy_bucket_id": row["policy_bucket_id"],
                "target_weight": row["target_weight"],
                "actual_weight": actual["actual_weight"],
                "drift": drift,
                "tolerance": row["rebalance_tolerance"],
                "drift_status": status,
                "likely_drift_causes": _likely_drift_causes(status, drift),
                "advisor_meaning": _advisor_meaning(status, drift),
                "caveats": [
                    "Drift is not automatically an advisor or manager error.",
                    "Synthetic causes are review prompts, not conclusions.",
                ],
            }
        )

    policy_bucket_rows = _policy_bucket_drift_rows(
        policy_profile=policy_profile,
        actual_snapshot=actual_snapshot,
        context=context,
    )
    counts = {status: 0 for status in sorted(VALID_DRIFT_STATUSES)}
    for row in drift_rows:
        counts[row["drift_status"]] += 1

    return {
        "schema_version": "allocation_drift_summary.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "policy_profile_id": policy_profile["policy_profile_id"],
        "actual_snapshot_date": actual_snapshot["valuation_date"],
        "drift_basis": "actual_current_weight_minus_target_policy_weight",
        "manager_rows": drift_rows,
        "policy_bucket_rows": policy_bucket_rows,
        "status_counts": counts,
        "managers_within_tolerance": counts["within_tolerance"],
        "managers_outside_tolerance": counts["review"] + counts["material_drift"],
        "drift_status_values": sorted(VALID_DRIFT_STATUSES),
        "interpretation_policy": (
            "Interpret drift before judging it; performance, flows, valuation marks, and "
            "implementation timing can all explain target-versus-actual differences."
        ),
        "source_metadata": _source_metadata("allocation_drift_summary"),
    }


def build_imputed_current_allocation_baseline(
    context: dict[str, Any],
    actual_snapshot: dict[str, Any],
) -> dict[str, Any]:
    baseline_weights = [
        {
            "manager_id": row["manager_id"],
            "display_name": row["display_name"],
            "baseline_weight": row["actual_weight"],
            "baseline_value": row["actual_value"],
            "baseline_status": "accepted_current_nav_weight",
        }
        for row in actual_snapshot["manager_rows"]
    ]

    return {
        "schema_version": "imputed_current_allocation_baseline.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "mode": "imputed_current_allocation",
        "baseline_date": actual_snapshot["valuation_date"],
        "source_actual_manager_allocation_snapshot": (
            "actual_manager_allocation_snapshot.json"
        ),
        "baseline_weights": baseline_weights,
        "baseline_weight_sum": _round_weight(
            sum(row["baseline_weight"] for row in baseline_weights)
        ),
        "meaning": (
            "Current synthetic manager NAV weights are accepted as the policy baseline for quick-start analysis."
        ),
        "use_cases": [
            "Initial setup when explicit advisor/family targets are not yet documented.",
            "Advisor review that wants manager implementation before policy drift review.",
        ],
        "caveats": [
            "This does not prove the current allocation was the agreed long-term policy.",
            "It should be replaced by explicit targets when policy documentation exists.",
        ],
        "what_this_suppresses": [
            "policy allocation drift attribution",
            "advisor allocation blame for current manager weights",
        ],
        "source_metadata": _source_metadata("imputed_current_allocation_baseline"),
    }


def build_manager_mandate_benchmark_catalog(context: dict[str, Any]) -> dict[str, Any]:
    benchmark_rows = []
    for manager_id in context["manager_ids"]:
        mandate = context["manager_mandates"][manager_id]
        calculated = context["manager_calculated"][manager_id]
        target = context["manager_policy_targets"][manager_id]
        benchmark_rows.append(
            {
                "manager_id": manager_id,
                "display_name": mandate["manager_display_name"],
                "mandate_benchmark_id": f"{manager_id}_mandate_benchmark_v1",
                "mandate_benchmark_display_name": (
                    f"Synthetic {mandate['approved_role_label']} Mandate Benchmark"
                ),
                "benchmark_type": calculated["manager_benchmark_basis_type"],
                "intended_representation": mandate["intended_role"],
                "synthetic_period_return": _round_return(
                    calculated["manager_benchmark_return"]
                ),
                "benchmark_basis_description": calculated[
                    "benchmark_basis_description"
                ],
                "linked_policy_bucket_id": target["policy_bucket_id"],
                "linked_theme_benchmarks": _theme_benchmark_components(calculated),
                "approval_status": "synthetic_demo_approved",
                "caveats": [
                    "Synthetic local-demo benchmark basis.",
                    "Not client benchmark advice.",
                ],
            }
        )

    return {
        "schema_version": "manager_mandate_benchmark_catalog.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "benchmark_rows": benchmark_rows,
        "manager_count": len(benchmark_rows),
        "coverage_summary": {
            "all_current_managers_covered": True,
            "all_benchmark_basis_types_explicit": True,
            "benchmark_basis_types": sorted(
                {row["benchmark_type"] for row in benchmark_rows}
            ),
        },
        "source_metadata": _source_metadata("manager_mandate_benchmark_catalog"),
    }


def build_manager_benchmark_basis_map(
    context: dict[str, Any],
    policy_profile: dict[str, Any],
    actual_snapshot: dict[str, Any],
    drift_summary: dict[str, Any],
    benchmark_catalog: dict[str, Any],
) -> dict[str, Any]:
    policy_by_manager = {
        row["manager_id"]: row for row in policy_profile["manager_sleeve_target_allocation"]
    }
    actual_by_manager = {
        row["manager_id"]: row for row in actual_snapshot["manager_rows"]
    }
    drift_by_manager = {
        row["manager_id"]: row for row in drift_summary["manager_rows"]
    }
    benchmark_by_manager = {
        row["manager_id"]: row for row in benchmark_catalog["benchmark_rows"]
    }
    rows = []
    for manager_id in context["manager_ids"]:
        benchmark = benchmark_by_manager[manager_id]
        rows.append(
            {
                "manager_id": manager_id,
                "display_name": benchmark["display_name"],
                "benchmark_basis_type": benchmark["benchmark_type"],
                "benchmark_basis_description": benchmark[
                    "benchmark_basis_description"
                ],
                "policy_weight": policy_by_manager[manager_id]["target_weight"],
                "actual_weight": actual_by_manager[manager_id]["actual_weight"],
                "mandate_benchmark_id": benchmark["mandate_benchmark_id"],
                "mandate_benchmark_return": benchmark["synthetic_period_return"],
                "theme_benchmark_blend": benchmark["linked_theme_benchmarks"],
                "drift_status": drift_by_manager[manager_id]["drift_status"],
                "attribution_layer_supported": [
                    "policy_allocation",
                    "manager_mandate",
                    "within_manager",
                ],
                "caveats": [
                    "Policy allocation uses target and actual weights.",
                    "Manager mandate attribution uses the mandate benchmark, not capital the manager did not control.",
                ],
            }
        )

    return {
        "schema_version": "manager_benchmark_basis_map.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "rows": rows,
        "manager_count": len(rows),
        "coverage_summary": {
            "all_current_managers_covered": True,
            "all_manager_benchmark_basis_explicit": True,
            "policy_actual_and_mandate_benchmark_linked": True,
        },
        "source_metadata": _source_metadata("manager_benchmark_basis_map"),
    }


def build_policy_level_attribution_inputs(
    context: dict[str, Any],
    policy_profile: dict[str, Any],
    actual_snapshot: dict[str, Any],
    drift_summary: dict[str, Any],
    benchmark_catalog: dict[str, Any],
) -> dict[str, Any]:
    policy_rows = policy_profile["manager_sleeve_target_allocation"]
    actual_by_manager = {
        row["manager_id"]: row for row in actual_snapshot["manager_rows"]
    }
    benchmark_by_manager = {
        row["manager_id"]: row for row in benchmark_catalog["benchmark_rows"]
    }
    calculated_by_manager = context["manager_calculated"]

    input_rows = []
    for policy_row in policy_rows:
        manager_id = policy_row["manager_id"]
        actual = actual_by_manager[manager_id]
        benchmark = benchmark_by_manager[manager_id]
        calculated = calculated_by_manager[manager_id]
        input_rows.append(
            {
                "manager_id": manager_id,
                "display_name": policy_row["display_name"],
                "policy_weight": policy_row["target_weight"],
                "actual_weight": actual["actual_weight"],
                "mandate_benchmark_return": benchmark["synthetic_period_return"],
                "manager_actual_return": _round_return(calculated["manager_return"]),
                "policy_benchmark_contribution": _round_return(
                    policy_row["target_weight"] * benchmark["synthetic_period_return"]
                ),
                "actual_allocation_benchmark_contribution": _round_return(
                    actual["actual_weight"] * benchmark["synthetic_period_return"]
                ),
                "actual_manager_return_contribution": _round_return(
                    actual["actual_weight"] * calculated["manager_return"]
                ),
            }
        )

    policy_benchmark_return = _round_return(
        sum(row["policy_benchmark_contribution"] for row in input_rows)
    )
    actual_allocation_benchmark_return = _round_return(
        sum(row["actual_allocation_benchmark_contribution"] for row in input_rows)
    )
    actual_manager_weight_return = _round_return(
        sum(row["actual_manager_return_contribution"] for row in input_rows)
    )
    whole = context["whole_summary"]
    global_benchmark_return = _round_return(whole["global_benchmark_return"])
    actual_portfolio_return = _round_return(whole["actual_portfolio_return"])

    return {
        "schema_version": "policy_level_attribution_inputs.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "scaffold_not_final_report": True,
        "calculated_report_ready": False,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "global_benchmark_return": global_benchmark_return,
        "policy_benchmark_return": policy_benchmark_return,
        "actual_allocation_benchmark_return": actual_allocation_benchmark_return,
        "actual_portfolio_return": actual_portfolio_return,
        "target_manager_weights": [
            {
                "manager_id": row["manager_id"],
                "target_weight": row["target_weight"],
            }
            for row in policy_rows
        ],
        "actual_manager_weights": [
            {
                "manager_id": row["manager_id"],
                "actual_weight": row["actual_weight"],
            }
            for row in actual_snapshot["manager_rows"]
        ],
        "manager_mandate_benchmark_returns": [
            {
                "manager_id": row["manager_id"],
                "mandate_benchmark_return": row["mandate_benchmark_return"],
            }
            for row in input_rows
        ],
        "manager_actual_returns": [
            {
                "manager_id": row["manager_id"],
                "manager_actual_return": row["manager_actual_return"],
            }
            for row in input_rows
        ],
        "policy_selection_mandate_mix_input": _round_return(
            policy_benchmark_return - global_benchmark_return
        ),
        "allocation_drift_input": drift_summary["manager_rows"],
        "policy_allocation_drift_effect_candidate": _round_return(
            actual_allocation_benchmark_return - policy_benchmark_return
        ),
        "manager_implementation_effect_candidate": _round_return(
            actual_manager_weight_return - actual_allocation_benchmark_return
        ),
        "input_rows": input_rows,
        "manager_current_weight_return_reconciliation": {
            "return_from_current_snapshot_weights": actual_manager_weight_return,
            "calculated_actual_portfolio_return": actual_portfolio_return,
            "difference": _round_return(
                actual_portfolio_return - actual_manager_weight_return
            ),
            "status": "scaffold_reconciliation_needed",
            "meaning": (
                "The policy scaffold uses current revaluation marks for actual weights; "
                "the existing calculated attribution pack uses its own synthetic period "
                "return basis."
            ),
        },
        "residual_policy": {
            "residual_is_explicit_reconciler": True,
            "timing_used_as_residual": False,
            "timing_status": "unavailable",
        },
        "tie_out_tolerance": TIE_OUT_TOLERANCE,
        "timing_status": "unavailable",
        "caveats": [
            "Preliminary arithmetic only; this artifact is an input scaffold, not a final policy attribution report.",
            "A future engine should define the exact return/flow basis before client use.",
        ],
        "source_metadata": _source_metadata("policy_level_attribution_inputs"),
    }


def build_equal_weight_diagnostic_classification(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "equal_weight_diagnostic_attribution_classification.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "diagnostic_id": "ai_adoption_equal_weight_selected_buckets_diagnostic_v1",
        "selected_lens": {
            "lens_id": "ai_adoption",
            "display_name": "AI Adoption",
        },
        "weight_basis": "equal_weight_selected_buckets",
        "default_policy_benchmark": False,
        "required_statement": (
            "Equal-weight attribution is an analytical diagnostic unless the advisor/family explicitly selected equal-weight theme buckets as policy."
        ),
        "why_useful": (
            "It shows how the selected lens would look if each AI Adoption bucket carried the same analytic weight."
        ),
        "why_not_default_policy": (
            "The synthetic policy profile uses advisor/family manager and mandate weights, not equal-weight theme buckets."
        ),
        "advisor_use": "Useful as an internal diagnostic for lens sensitivity and theme-bucket discussion.",
        "client_use": (
            "Client-facing only if the advisor/family explicitly selected equal-weight theme buckets as policy."
        ),
        "relation_to_policy_allocation": (
            "Separate from explicit policy allocation, imputed current allocation, and manager mandate benchmarks."
        ),
        "caveats": [
            "Do not label this as agreed policy without a policy artifact.",
            "Do not use this diagnostic to blame a manager for capital outside the manager mandate.",
        ],
        "readiness_status": "ready_as_advisor_internal_diagnostic",
        "source_metadata": _source_metadata("equal_weight_diagnostic_classification"),
    }


def build_readiness_summary(
    context: dict[str, Any],
    outputs: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "policy_mandate_readiness_summary.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "explicit_policy_allocation_readiness": "ready_for_synthetic_demo",
        "imputed_current_allocation_readiness": "ready_for_synthetic_demo_quick_start",
        "manager_mandate_benchmark_readiness": "ready_for_synthetic_demo",
        "policy_allocation_drift_readiness": "ready_for_synthetic_demo",
        "policy_level_attribution_input_readiness": "input_scaffold_ready_engine_needed",
        "manager_mandate_attribution_readiness": (
            "ready_to_align_future_reports_to_mandate_benchmarks"
        ),
        "within_manager_attribution_readiness": (
            "calculated_ai_adoption_path_exists_for_future_alignment"
        ),
        "equal_weight_diagnostic_readiness": "ready_as_advisor_internal_diagnostic",
        "future_report_readiness": [
            {
                "report_family": "Policy Allocation Review",
                "status": "ready_for_synthetic_demo_mockup",
            },
            {
                "report_family": "Policy-Level Attribution",
                "status": "input_scaffold_ready_calculated_engine_needed",
            },
            {
                "report_family": "Manager Mandate Attribution",
                "status": "ready_to_align_future_reports_to_mandate_benchmarks",
            },
            {
                "report_family": "Within-Manager Attribution Detail",
                "status": "foundation_ready_for_future_mandate_aligned_views",
            },
            {
                "report_family": "Equal-Weight Diagnostic Attribution",
                "status": "ready_as_advisor_internal_diagnostic",
            },
            {
                "report_family": "Blended All-In Attribution",
                "status": "deferred",
            },
        ],
        "missing_production_prerequisites": [
            "real client policy mandate approvals",
            "approved benchmark construction records",
            "production historical return and flow basis",
            "clean timing attribution inputs",
            "client-ready benchmark disclosure language",
        ],
        "advisor_ui_report_wiring": "paused",
        "generated_report_wiring": "paused",
        "recommended_next_tranche": (
            "Policy Allocation Review Mockups v1 or Policy-Level Attribution Calculation Engine v1"
        ),
        "source_metadata": _source_metadata("policy_mandate_readiness_summary"),
    }


def build_manifest(context: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "synthetic_policy_mandate_pack_manifest.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "base_currency": BASE_CURRENCY,
        "source_position_catalog": context["source_paths"]["source_position_catalog"],
        "source_manager_mandate_catalog": context["source_paths"][
            "source_manager_mandate_catalog"
        ],
        "source_attribution_prerequisite_pack": context["source_paths"][
            "source_attribution_prerequisite_pack"
        ],
        "source_calculated_attribution_pack": context["source_paths"][
            "source_calculated_attribution_pack"
        ],
        "included_artifacts": list(ARTIFACT_FILES.values()),
        "supported_future_reports": [
            "Policy Allocation Review",
            "Policy-Level Attribution input scaffold",
            "Manager Mandate Attribution Summary",
            "Within-Manager Attribution Detail alignment",
            "Equal-Weight Diagnostic Attribution",
        ],
        "gated_future_reports": [
            "Policy-Level Attribution calculated report",
            "Blended All-In Attribution",
            "Timing Attribution",
            "Scenario Versus Benchmark",
            "Probabilistic Scenario Range",
            "Current Versus Proposed Portfolio",
        ],
        "limitations": [
            "Synthetic local-only prerequisite pack.",
            "No Advisor Preview, Populate, Present, or generated-report wiring.",
            "No final policy attribution report or Markdown mockup generation.",
            "No external data, live market data, real client data, or dependency changes.",
        ],
        "timing_status": "unavailable",
        "approval_status": "synthetic_demo_approved",
        "generated_by": {
            "module": "arangur.analytics.synthetic_policy_mandate_prerequisites",
            "command": "python -m arangur.analytics.synthetic_policy_mandate_prerequisites",
        },
        "readiness_summary": {
            "policy_allocation_review": "ready_for_synthetic_demo_mockup",
            "policy_level_attribution": "input_scaffold_ready_engine_needed",
            "manager_mandate_attribution": (
                "ready_to_align_future_reports_to_mandate_benchmarks"
            ),
            "equal_weight_diagnostic": "ready_as_advisor_internal_diagnostic",
            "blended_all_in_attribution": "deferred",
        },
        "source_metadata": _source_metadata("synthetic_policy_mandate_pack_manifest"),
    }


def validate_outputs(context: dict[str, Any], outputs: dict[str, Any]) -> None:
    profile = outputs["policy_allocation_profile"]
    if abs(profile["manager_sleeve_target_weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
        raise ValueError("Manager policy target weights must sum to 1.0")
    if abs(profile["policy_bucket_target_weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
        raise ValueError("Policy bucket target weights must sum to 1.0")
    if profile["equal_weight_theme_policy"]:
        raise ValueError("Synthetic policy profile must not use equal-weight theme policy")

    actual = outputs["actual_manager_allocation_snapshot"]
    if abs(actual["actual_weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
        raise ValueError("Actual manager weights must sum to 1.0")

    expected_ids = set(context["manager_ids"])
    actual_ids = {row["manager_id"] for row in actual["manager_rows"]}
    if expected_ids != actual_ids:
        raise ValueError("Actual allocation snapshot does not cover all managers")

    drift_rows = outputs["allocation_drift_summary"]["manager_rows"]
    if {row["manager_id"] for row in drift_rows} != expected_ids:
        raise ValueError("Drift summary does not cover all managers")
    for row in drift_rows:
        expected_drift = _round_weight(row["actual_weight"] - row["target_weight"])
        if row["drift"] != expected_drift:
            raise ValueError(f"Bad drift calculation for {row['manager_id']}")
        if row["drift_status"] not in VALID_DRIFT_STATUSES:
            raise ValueError(f"Bad drift status for {row['manager_id']}")

    baseline = outputs["imputed_current_allocation_baseline"]
    baseline_by_manager = {
        row["manager_id"]: row["baseline_weight"] for row in baseline["baseline_weights"]
    }
    actual_by_manager = {row["manager_id"]: row["actual_weight"] for row in actual["manager_rows"]}
    if baseline_by_manager != actual_by_manager:
        raise ValueError("Imputed baseline must use actual current weights")

    benchmark_rows = outputs["manager_mandate_benchmark_catalog"]["benchmark_rows"]
    if {row["manager_id"] for row in benchmark_rows} != expected_ids:
        raise ValueError("Manager mandate benchmark catalog does not cover all managers")
    if any(not row["benchmark_type"] for row in benchmark_rows):
        raise ValueError("Each manager benchmark basis must be explicit")

    policy_inputs = outputs["policy_level_attribution_inputs"]
    if not policy_inputs["scaffold_not_final_report"]:
        raise ValueError("Policy-level attribution input must be marked as scaffold")
    if policy_inputs["calculated_report_ready"]:
        raise ValueError("Policy-level attribution report should remain engine-gated")

    equal_weight = outputs["equal_weight_diagnostic_attribution_classification"]
    if equal_weight["default_policy_benchmark"]:
        raise ValueError("Equal-weight diagnostic must not be default policy")


def _policy_bucket_drift_rows(
    *,
    policy_profile: dict[str, Any],
    actual_snapshot: dict[str, Any],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    actual_by_manager = {
        row["manager_id"]: row["actual_weight"] for row in actual_snapshot["manager_rows"]
    }
    rows = []
    for bucket in policy_profile["policy_bucket_target_allocation"]:
        actual_weight = _round_weight(
            sum(actual_by_manager[manager_id] for manager_id in bucket["linked_managers"])
        )
        drift = _round_weight(actual_weight - bucket["target_weight"])
        rows.append(
            {
                "policy_bucket_id": bucket["policy_bucket_id"],
                "display_name": bucket["display_name"],
                "target_weight": bucket["target_weight"],
                "actual_weight": actual_weight,
                "drift": drift,
                "tolerance": bucket["rebalance_tolerance"],
                "drift_status": _drift_status(drift, bucket["rebalance_tolerance"]),
                "linked_managers": list(bucket["linked_managers"]),
            }
        )
    return rows


def _drift_status(drift: float, tolerance: float) -> str:
    absolute = abs(float(drift))
    if absolute <= tolerance:
        return "within_tolerance"
    if absolute <= tolerance * 2:
        return "review"
    return "material_drift"


def _likely_drift_causes(status: str, drift: float) -> list[str]:
    if status == "within_tolerance":
        return ["performance_drift", "valuation_mark_effect"]
    if drift > 0:
        return [
            "performance_drift",
            "intentional_tactical_deviation",
            "valuation_mark_effect",
        ]
    return ["flow_or_withdrawal", "implementation_timing", "unknown"]


def _advisor_meaning(status: str, drift: float) -> str:
    if status == "within_tolerance":
        return "Within the synthetic rebalance tolerance; monitor without treating as an error."
    if drift > 0:
        return "Above target and outside tolerance; review whether appreciation, tactical choice, or marks explain it."
    return "Below target and outside tolerance; review flows, timing, and policy intent before assigning cause."


def _theme_benchmark_components(calculated: dict[str, Any]) -> list[dict[str, Any]]:
    components = []
    for component in calculated.get("manager_benchmark_components", []):
        if component.get("component_type") == "selected_lens_theme_benchmark_blend":
            components.append(
                {
                    "component_type": component["component_type"],
                    "selected_lens_id": component["selected_lens_id"],
                    "component_return": _round_return(component["component_return"]),
                }
            )
        elif component.get("component_type") == "manager_specific_synthetic_mandate_proxy":
            components.append(
                {
                    "component_type": component["component_type"],
                    "proxy_id": component["proxy_id"],
                    "proxy_display_name": component["proxy_display_name"],
                    "component_return": _round_return(component["component_return"]),
                }
            )
    return components


def _source_metadata(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "synthetic_data": True,
        "local_only": True,
        "external_data_used": False,
        "live_market_data_used": False,
        "real_client_data_used": False,
    }


def _round_values_preserve_sum(values: list[float], target: float) -> list[float]:
    if not values:
        raise ValueError("Cannot round an empty value set")
    rounded = [_round_weight(value) for value in values]
    difference = _round_weight(float(target) - sum(rounded))
    if difference:
        index = max(range(len(rounded)), key=lambda item: abs(values[item]))
        rounded[index] = _round_weight(rounded[index] + difference)
    return rounded


def _round_weight(value: Any) -> float:
    return round(float(value), 6)


def _round_return(value: Any) -> float:
    return round(float(value), 6)


def _round_money(value: Any) -> float:
    return round(float(value), 2)


def _portable_path(path: str | Path) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate synthetic policy allocation and mandate benchmark prerequisites."
    )
    parser.add_argument("--revaluation-dir", default=str(DEFAULT_REVALUATION_DIR))
    parser.add_argument(
        "--report-prerequisite-dir",
        default=str(DEFAULT_REPORT_PREREQUISITE_DIR),
    )
    parser.add_argument(
        "--attribution-prerequisite-dir",
        default=str(DEFAULT_ATTRIBUTION_PREREQUISITE_DIR),
    )
    parser.add_argument(
        "--attribution-calculated-dir",
        default=str(DEFAULT_ATTRIBUTION_CALCULATED_DIR),
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outputs = generate_synthetic_policy_mandate_prerequisites(
        revaluation_dir=args.revaluation_dir,
        report_prerequisite_dir=args.report_prerequisite_dir,
        attribution_prerequisite_dir=args.attribution_prerequisite_dir,
        attribution_calculated_dir=args.attribution_calculated_dir,
        output_dir=args.output_dir,
    )
    profile = outputs["policy_allocation_profile"]
    actual = outputs["actual_manager_allocation_snapshot"]
    drift = outputs["allocation_drift_summary"]
    benchmarks = outputs["manager_mandate_benchmark_catalog"]

    print(f"Synthetic policy mandate prerequisite pack: {PACK_ID} -> {args.output_dir}")
    print(f"Policy mode: {profile['allocation_mode']}")
    print(f"Manager count: {actual['manager_count']}")
    print(f"Target weight sum: {profile['manager_sleeve_target_weight_sum']:.6f}")
    print(f"Actual weight sum: {actual['actual_weight_sum']:.6f}")
    print(
        "Managers within/outside tolerance: "
        f"{drift['managers_within_tolerance']}/"
        f"{drift['managers_outside_tolerance']}"
    )
    print(
        "Benchmark coverage: "
        f"{benchmarks['coverage_summary']['all_current_managers_covered']}"
    )
    print(f"Timing status: {outputs['manifest']['timing_status']}")
    print(f"Output path: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
