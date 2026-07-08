from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-07T00:00:00Z"
PACK_ID = "synthetic_attribution_prerequisite_pack_v1"
PACK_VERSION = "2026-07-07"
GENERATOR_VERSION = "synthetic_attribution_prerequisites.v1"

PERIOD_START = "2025-07-01"
PERIOD_END = "2026-06-30"
BASE_CURRENCY = "USD"
TIE_OUT_TOLERANCE = 0.000001

DEFAULT_REVALUATION_DIR = Path("data/simulation/revaluation")
DEFAULT_REPORT_PREREQUISITE_DIR = Path(
    "data/simulation/report_prerequisites/synthetic_report_prerequisite_pack_v1"
)
DEFAULT_OUTPUT_DIR = Path("data/simulation/attribution_prerequisites") / PACK_ID

ARTIFACT_FILES = {
    "synthetic_attribution_prerequisite_pack_manifest": (
        "synthetic_attribution_prerequisite_pack_manifest.json"
    ),
    "portfolio_benchmark_catalog": "portfolio_benchmark_catalog.json",
    "lens_bucket_benchmark_proxy_map": "lens_bucket_benchmark_proxy_map.json",
    "synthetic_period_returns": "synthetic_period_returns.json",
    "synthetic_attribution_weights_flows": "synthetic_attribution_weights_flows.json",
    "integrated_attribution_decomposition_inputs": (
        "integrated_attribution_decomposition_inputs.json"
    ),
    "manager_attribution_prerequisites": "manager_attribution_prerequisites.json",
    "attribution_readiness_summary": "attribution_readiness_summary.json",
}

MANAGER_RETURN_INPUTS = {
    "mgr_a_growth_ai_infrastructure": {
        "manager_return": 0.116,
        "benchmark_return": 0.095,
        "proxy_display_name": "Synthetic Growth / AI Infrastructure Manager Proxy",
    },
    "mgr_b_core_quality_equity": {
        "manager_return": 0.084,
        "benchmark_return": 0.076,
        "proxy_display_name": "Synthetic Core Quality Equity Manager Proxy",
    },
    "mgr_c_income_cash_generation": {
        "manager_return": 0.047,
        "benchmark_return": 0.043,
        "proxy_display_name": "Synthetic Income and Credit Manager Proxy",
    },
    "mgr_d_private_real_assets": {
        "manager_return": 0.071,
        "benchmark_return": 0.063,
        "proxy_display_name": "Synthetic Private Markets / Real Assets Manager Proxy",
    },
    "mgr_e_liquidity_defensive": {
        "manager_return": 0.034,
        "benchmark_return": 0.031,
        "proxy_display_name": "Synthetic Liquidity Reserve Policy Proxy",
    },
    "mgr_f_opportunistic_macro": {
        "manager_return": 0.089,
        "benchmark_return": 0.075,
        "proxy_display_name": "Synthetic Opportunistic Macro / Hedge Proxy",
    },
}

LENS_PROXY_RETURNS = {
    "ai_adoption": {
        "core_ai_infrastructure_hardware": 0.103,
        "ai_model_platform_exposure": 0.092,
        "ai_downstream_productivity_beneficiary": 0.071,
        "ai_disrupted_incumbent": 0.038,
        "data_center_power_bottleneck_exposure": 0.085,
        "neutral_low_direct_ai_exposure": 0.052,
        "unclassified_review_required": 0.04,
    },
    "energy_security": {
        "energy_supply_beneficiary": 0.079,
        "grid_infrastructure_beneficiary": 0.073,
        "energy_input_cost_sensitive": 0.058,
        "transition_policy_sensitive": 0.052,
        "commodity_supply_security_exposure": 0.081,
        "neutral_low_direct_energy_exposure": 0.048,
        "unclassified_review_required": 0.04,
    },
}

LENS_ACTIVE_DELTAS = {
    "ai_adoption": {
        "core_ai_infrastructure_hardware": 0.014,
        "ai_model_platform_exposure": 0.012,
        "ai_downstream_productivity_beneficiary": 0.006,
        "ai_disrupted_incumbent": -0.004,
        "data_center_power_bottleneck_exposure": 0.01,
        "neutral_low_direct_ai_exposure": 0.002,
        "unclassified_review_required": 0.0,
    },
    "energy_security": {
        "energy_supply_beneficiary": 0.006,
        "grid_infrastructure_beneficiary": 0.008,
        "energy_input_cost_sensitive": -0.002,
        "transition_policy_sensitive": 0.001,
        "commodity_supply_security_exposure": 0.007,
        "neutral_low_direct_energy_exposure": 0.002,
        "unclassified_review_required": 0.0,
    },
}


def generate_synthetic_attribution_prerequisite_pack(
    *,
    revaluation_dir: str | Path = DEFAULT_REVALUATION_DIR,
    report_prerequisite_dir: str | Path = DEFAULT_REPORT_PREREQUISITE_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    context = load_source_context(
        revaluation_dir=Path(revaluation_dir),
        report_prerequisite_dir=Path(report_prerequisite_dir),
    )

    outputs: dict[str, Any] = {}
    outputs["lens_bucket_benchmark_proxy_map"] = build_lens_bucket_benchmark_proxy_map(
        context
    )
    outputs["synthetic_period_returns"] = build_synthetic_period_returns(
        context,
        outputs["lens_bucket_benchmark_proxy_map"],
    )
    outputs["portfolio_benchmark_catalog"] = build_portfolio_benchmark_catalog(
        context,
        outputs["synthetic_period_returns"],
    )
    outputs["synthetic_attribution_weights_flows"] = build_synthetic_weights_flows(
        context,
        outputs["lens_bucket_benchmark_proxy_map"],
    )
    outputs["manager_attribution_prerequisites"] = build_manager_attribution_prerequisites(
        context,
        outputs["synthetic_period_returns"],
    )
    outputs["integrated_attribution_decomposition_inputs"] = (
        build_integrated_attribution_decomposition_inputs(
            context,
            outputs["synthetic_period_returns"],
            outputs["manager_attribution_prerequisites"],
        )
    )
    outputs["attribution_readiness_summary"] = build_attribution_readiness_summary(
        context,
        outputs,
    )
    outputs["synthetic_attribution_prerequisite_pack_manifest"] = build_manifest(
        context,
        outputs,
    )

    validate_pack(context, outputs)

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    for output_name, filename in ARTIFACT_FILES.items():
        _write_json(root / filename, outputs[output_name])

    return outputs


def load_source_context(
    *,
    revaluation_dir: Path,
    report_prerequisite_dir: Path,
) -> dict[str, Any]:
    position_catalog = _load_json(revaluation_dir / "position_catalog.json")
    instrument_catalog = _load_json(revaluation_dir / "instrument_catalog.json")
    base_valuation = _load_json(revaluation_dir / "position_valuation_results_base.json")
    manager_mandates = _load_json(report_prerequisite_dir / "manager_mandate_catalog.json")
    lens_catalog = _load_json(report_prerequisite_dir / "synthetic_lens_catalog.json")
    lenses = {
        "ai_adoption": _load_json(report_prerequisite_dir / "ai_adoption_lens_v1.json"),
        "energy_security": _load_json(report_prerequisite_dir / "energy_security_lens_v1.json"),
    }
    lens_assignments = {
        "ai_adoption": _load_json(
            report_prerequisite_dir / "position_lens_assignments_ai_adoption_v1.json"
        ),
        "energy_security": _load_json(
            report_prerequisite_dir / "position_lens_assignments_energy_security_v1.json"
        ),
    }

    positions_by_id = {row["position_id"]: row for row in position_catalog["positions"]}
    instruments_by_id = {
        row["instrument_id"]: row for row in instrument_catalog["instruments"]
    }
    base_rows = sorted(
        base_valuation["position_results"],
        key=lambda row: float(row["value"]),
        reverse=True,
    )

    return {
        "source_paths": {
            "position_catalog": _as_posix(revaluation_dir / "position_catalog.json"),
            "instrument_catalog": _as_posix(revaluation_dir / "instrument_catalog.json"),
            "base_valuation": _as_posix(revaluation_dir / "position_valuation_results_base.json"),
            "source_lens_catalog": _as_posix(report_prerequisite_dir / "synthetic_lens_catalog.json"),
            "source_manager_mandate_catalog": _as_posix(
                report_prerequisite_dir / "manager_mandate_catalog.json"
            ),
            "ai_adoption_lens": _as_posix(report_prerequisite_dir / "ai_adoption_lens_v1.json"),
            "energy_security_lens": _as_posix(
                report_prerequisite_dir / "energy_security_lens_v1.json"
            ),
            "ai_adoption_assignments": _as_posix(
                report_prerequisite_dir / "position_lens_assignments_ai_adoption_v1.json"
            ),
            "energy_security_assignments": _as_posix(
                report_prerequisite_dir / "position_lens_assignments_energy_security_v1.json"
            ),
        },
        "position_catalog": position_catalog,
        "instrument_catalog": instrument_catalog,
        "base_valuation": base_valuation,
        "manager_mandates": manager_mandates,
        "lens_catalog": lens_catalog,
        "lenses": lenses,
        "lens_assignments": lens_assignments,
        "positions_by_id": positions_by_id,
        "instruments_by_id": instruments_by_id,
        "base_rows": base_rows,
        "portfolio_id": str(position_catalog["portfolio_id"]),
        "portfolio_snapshot_id": str(position_catalog["portfolio_snapshot_id"]),
        "base_portfolio_value": round(float(base_valuation["summary"]["total_value"]), 2),
    }


def build_portfolio_benchmark_catalog(
    context: dict[str, Any],
    returns: dict[str, Any],
) -> dict[str, Any]:
    benchmark_return = returns["benchmark_return"]["period_return"]
    return {
        "schema_version": "portfolio_benchmark_catalog.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "base_currency": BASE_CURRENCY,
        "portfolio_id": context["portfolio_id"],
        "benchmarks": [
            {
                "benchmark_id": "northstar_synthetic_policy_benchmark_v1",
                "display_name": "Northstar Synthetic Policy Benchmark",
                "benchmark_type": "synthetic_policy_composite",
                "description": (
                    "A deterministic local-demo composite benchmark aligned to the current "
                    "synthetic manager mandate mix."
                ),
                "intended_use": (
                    "Synthetic prerequisite for future Integrated Performance Attribution "
                    "mockups; not a production benchmark recommendation."
                ),
                "base_currency": BASE_CURRENCY,
                "period_start": PERIOD_START,
                "period_end": PERIOD_END,
                "synthetic_return": benchmark_return,
                "approval_status": "synthetic_demo_approved",
                "caveats": [
                    "Synthetic local-demo benchmark only.",
                    "It is explicit about its policy-composite purpose and is not objectively correct for real portfolios.",
                ],
                "source_metadata": _source_metadata(
                    "weighted_synthetic_manager_policy_proxy_returns"
                ),
            }
        ],
    }


def build_lens_bucket_benchmark_proxy_map(context: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for lens_id, lens in context["lenses"].items():
        for bucket in lens["primary_buckets"]:
            bucket_id = bucket["bucket_id"]
            proxy_id = f"{lens_id}_{bucket_id}_synthetic_proxy_v1"
            rows.append(
                {
                    "lens_id": lens_id,
                    "lens_version": lens["lens_version"],
                    "bucket_id": bucket_id,
                    "bucket_display_name": bucket["display_name"],
                    "proxy_id": proxy_id,
                    "proxy_display_name": f"Synthetic {bucket['display_name']} Proxy",
                    "proxy_type": _proxy_type_for_bucket(bucket_id),
                    "intended_representation": (
                        f"Local-demo return proxy for the {bucket['display_name']} bucket "
                        f"inside the {lens['display_name']} lens."
                    ),
                    "synthetic_period_return": _round_return(
                        LENS_PROXY_RETURNS[lens_id][bucket_id]
                    ),
                    "approval_status": "synthetic_demo_approved",
                    "caveats": [
                        "Synthetic demo proxy only.",
                        "Not an investable recommendation, production benchmark, or live market return.",
                    ],
                }
            )

    return {
        "schema_version": "lens_bucket_benchmark_proxy_map.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "base_currency": BASE_CURRENCY,
        "proxy_map": rows,
        "coverage_summary": {
            "lens_count": len(context["lenses"]),
            "proxy_count": len(rows),
            "all_lens_buckets_have_proxy": True,
            "advisor_freeform_benchmark_construction_used": False,
        },
        "source_metadata": _source_metadata("synthetic_lens_catalog_and_assignments"),
    }


def build_synthetic_period_returns(
    context: dict[str, Any],
    proxy_map: dict[str, Any],
) -> dict[str, Any]:
    manager_rows = _manager_return_rows(context)
    manager_weights = {
        row["manager_id"]: row["portfolio_share"]
        for row in context["manager_mandates"]["manager_mandates"]
    }
    portfolio_return = _round_return(
        sum(row["manager_return"] * manager_weights[row["manager_id"]] for row in manager_rows)
    )
    benchmark_return = _round_return(
        sum(row["benchmark_return"] * manager_weights[row["manager_id"]] for row in manager_rows)
    )

    proxy_returns = [
        {
            "proxy_id": row["proxy_id"],
            "lens_id": row["lens_id"],
            "bucket_id": row["bucket_id"],
            "period_return": row["synthetic_period_return"],
            "synthetic_data": True,
        }
        for row in proxy_map["proxy_map"]
    ]
    lens_bucket_returns = []
    for row in proxy_map["proxy_map"]:
        active_delta = LENS_ACTIVE_DELTAS[row["lens_id"]][row["bucket_id"]]
        lens_bucket_returns.append(
            {
                "lens_id": row["lens_id"],
                "bucket_id": row["bucket_id"],
                "bucket_display_name": row["bucket_display_name"],
                "period_return": _round_return(row["synthetic_period_return"] + active_delta),
                "proxy_id": row["proxy_id"],
                "proxy_period_return": row["synthetic_period_return"],
                "relative_return": _round_return(active_delta),
                "synthetic_data": True,
            }
        )

    return {
        "schema_version": "synthetic_period_returns.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "return_basis": "total_return_synthetic",
        "base_currency": BASE_CURRENCY,
        "portfolio_return": {
            "portfolio_id": context["portfolio_id"],
            "period_return": portfolio_return,
            "return_source": "weighted_synthetic_manager_returns",
        },
        "benchmark_return": {
            "benchmark_id": "northstar_synthetic_policy_benchmark_v1",
            "period_return": benchmark_return,
            "return_source": "weighted_synthetic_manager_proxy_returns",
        },
        "manager_returns": manager_rows,
        "lens_bucket_returns": lens_bucket_returns,
        "proxy_returns": proxy_returns,
        "position_returns": _selected_position_returns(context, manager_rows),
        "caveats": [
            "Synthetic demo returns only.",
            "These values are deterministic local prerequisites and do not imply historical truth.",
        ],
        "source_metadata": _source_metadata("synthetic_attribution_return_fixture"),
    }


def build_synthetic_weights_flows(
    context: dict[str, Any],
    proxy_map: dict[str, Any],
) -> dict[str, Any]:
    manager_rows = _manager_weight_rows(context)
    lens_weights = _lens_weight_rows(context)
    proxy_weights = [
        {
            "lens_id": row["lens_id"],
            "bucket_id": row["bucket_id"],
            "proxy_id": row["proxy_id"],
            "weight": _lens_bucket_weight(context, row["lens_id"], row["bucket_id"]),
        }
        for row in proxy_map["proxy_map"]
    ]

    return {
        "schema_version": "synthetic_attribution_weights_flows.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "base_currency": BASE_CURRENCY,
        "return_basis": "total_return_synthetic",
        "manager_weights": manager_rows,
        "lens_bucket_weights": lens_weights,
        "benchmark_weights": [
            {
                "benchmark_id": "northstar_synthetic_policy_benchmark_v1",
                "component_id": row["manager_id"],
                "component_display_name": row["display_name"],
                "weight": row["average_weight"],
            }
            for row in manager_rows
        ],
        "proxy_weights": proxy_weights,
        "cash_flows": {
            "flow_policy": "no_external_flows_modeled_for_synthetic_total_return",
            "capital_contributions": 0.0,
            "capital_withdrawals": 0.0,
            "net_external_flows": 0.0,
            "income_distributions_handled_inside_total_return": True,
            "caveat": "No production flow normalization is implemented in this prerequisite pack.",
        },
        "reconciliation": {
            "manager_average_weights_sum": _round_weight(
                sum(row["average_weight"] for row in manager_rows)
            ),
            "lens_bucket_weights_sum_by_lens": {
                lens_id: _round_weight(
                    sum(row["weight"] for row in lens_weights if row["lens_id"] == lens_id)
                )
                for lens_id in context["lenses"]
            },
            "proxy_weights_sum_by_lens": {
                lens_id: _round_weight(
                    sum(row["weight"] for row in proxy_weights if row["lens_id"] == lens_id)
                )
                for lens_id in context["lenses"]
            },
        },
        "source_metadata": _source_metadata("synthetic_manager_and_lens_weights"),
    }


def build_integrated_attribution_decomposition_inputs(
    context: dict[str, Any],
    returns: dict[str, Any],
    manager_prerequisites: dict[str, Any],
) -> dict[str, Any]:
    portfolio_return = returns["portfolio_return"]["period_return"]
    benchmark_return = returns["benchmark_return"]["period_return"]
    active_return = _round_return(portfolio_return - benchmark_return)
    whole_effects = _effect_breakdown(active_return)
    whole_tie = _tie_out(benchmark_return, whole_effects, portfolio_return)
    theme_benchmark_detail = _theme_benchmark_detail(
        context,
        returns,
        active_return,
    )

    return {
        "schema_version": "integrated_attribution_decomposition_inputs.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "base_currency": BASE_CURRENCY,
        "supported_modes": [
            {
                "mode": "whole_portfolio",
                "benchmark_id": "northstar_synthetic_policy_benchmark_v1",
                "benchmark_return": benchmark_return,
                "actual_return": portfolio_return,
                "active_return": active_return,
                "effects": whole_effects,
                "theme_benchmark_detail": theme_benchmark_detail,
                "strategy_timing": _timing_unavailable(),
                "asset_timing": _timing_unavailable(),
                "tie_out": whole_tie,
            },
            {
                "mode": "manager_by_manager",
                "benchmark_id": "manager_specific_synthetic_policy_proxies",
                "manager_count": len(manager_prerequisites["managers"]),
                "manager_rows": manager_prerequisites["managers"],
                "strategy_timing": _timing_unavailable(),
                "asset_timing": _timing_unavailable(),
                "tie_out": {
                    "manager_relative_returns_tie_out": True,
                    "timing_used_as_residual": False,
                },
            },
        ],
        "methodology_notes": [
            "This artifact defines deterministic synthetic decomposition inputs for later report mockups.",
            "Timing is unavailable rather than forced into a residual bucket.",
        ],
        "source_metadata": _source_metadata("synthetic_decomposition_input_fixture"),
    }


def build_manager_attribution_prerequisites(
    context: dict[str, Any],
    returns: dict[str, Any],
) -> dict[str, Any]:
    return_by_manager = {
        row["manager_id"]: row for row in returns["manager_returns"]
    }
    managers = []
    for mandate in context["manager_mandates"]["manager_mandates"]:
        manager_id = mandate["manager_id"]
        manager_return = return_by_manager[manager_id]["manager_return"]
        benchmark_return = return_by_manager[manager_id]["benchmark_return"]
        relative_return = _round_return(manager_return - benchmark_return)
        effects = _effect_breakdown(relative_return)
        managers.append(
            {
                "manager_id": manager_id,
                "display_name": mandate["manager_display_name"],
                "approved_role": mandate["approved_role_label"],
                "mandate_reference": "synthetic_report_prerequisite_pack_v1.manager_mandate_catalog",
                "manager_benchmark_proxy": {
                    "proxy_id": f"{manager_id}_synthetic_manager_proxy_v1",
                    "proxy_display_name": MANAGER_RETURN_INPUTS[manager_id]["proxy_display_name"],
                    "approval_status": "synthetic_demo_approved",
                    "caveat": "Synthetic manager proxy only; not a production benchmark recommendation.",
                },
                "manager_return": manager_return,
                "benchmark_proxy_return": benchmark_return,
                "relative_return": relative_return,
                "portfolio_weight": _round_weight(float(mandate["portfolio_share"])),
                "portfolio_active_contribution": _round_return(
                    float(mandate["portfolio_share"]) * relative_return
                ),
                "strategy_selection_contribution": effects["strategy_lens_bucket_selection_effect"],
                "strategy_sizing_contribution": effects["strategy_lens_bucket_sizing_effect"],
                "asset_selection_contribution": effects["asset_selection_effect"],
                "asset_sizing_contribution": effects["asset_sizing_effect"],
                "timing_status": "unavailable",
                "timing_reason": "Missing clean trade/holding history and deferred timing methodology.",
                "residual_unexplained": effects["residual_unexplained"],
                "tie_out": _tie_out(benchmark_return, effects, manager_return),
                "caveats": [
                    "Synthetic manager attribution prerequisite only.",
                    "Timing is not used as a residual bucket.",
                ],
                "readiness_status": "ready_for_future_synthetic_manager_attribution_mockup",
                "synthetic_data": True,
            }
        )

    return {
        "schema_version": "manager_attribution_prerequisites.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "base_currency": BASE_CURRENCY,
        "managers": managers,
        "coverage_summary": {
            "current_manager_count": len(context["manager_mandates"]["manager_mandates"]),
            "manager_prerequisite_count": len(managers),
            "all_current_managers_covered": True,
            "manager_by_manager_attribution_supported": True,
            "timing_available": False,
        },
        "source_metadata": _source_metadata("synthetic_manager_attribution_fixture"),
    }


def build_attribution_readiness_summary(
    context: dict[str, Any],
    outputs: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "attribution_readiness_summary.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "whole_portfolio_attribution_readiness": "ready_for_synthetic_demo_mockup",
        "manager_attribution_readiness": "ready_for_synthetic_demo_mockup",
        "lens_based_attribution_readiness": "ready_for_synthetic_demo_mockup",
        "timing_attribution_readiness": {
            "status": "unavailable",
            "reason": "No clean two-state trade/holding history or approved timing methodology exists.",
        },
        "missing_production_prerequisites": [
            "real portfolio and benchmark returns",
            "approved production benchmark maps",
            "complete production holdings and flow history",
            "client-approved attribution method and residual policy",
            "clean timing methodology before any timing effect is shown",
        ],
        "synthetic_demo_limitations": [
            "Synthetic returns and proxies are deterministic local-demo inputs.",
            "No live market data, vendor returns, or real client records are used.",
            "Scenario Versus Benchmark remains gated because benchmark scenario values are not created here.",
            "Probabilistic Scenario Range remains gated because no range analytics are created here.",
        ],
        "future_reports_can_now_be_mocked_honestly": [
            "integrated_performance_attribution_summary",
            "integrated_performance_attribution_detail",
            "manager_attribution_summary",
            "lens_based_performance_attribution",
        ],
        "reports_still_gated": [
            "timing_attribution",
            "probabilistic_scenario_range",
            "scenario_versus_benchmark",
            "current_versus_proposed_portfolio",
        ],
        "report_readiness": {
            "integrated_performance_attribution_summary": "ready_for_synthetic_demo_mockup",
            "integrated_performance_attribution_detail": "ready_for_synthetic_demo_mockup",
            "manager_attribution_summary": "ready_for_synthetic_demo_mockup",
            "lens_based_performance_attribution": "ready_for_synthetic_demo_mockup",
            "timing_attribution": "unavailable",
            "probabilistic_scenario_range": "gated",
            "scenario_versus_benchmark": "gated_until_benchmark_scenario_values_exist",
        },
        "supporting_artifacts": [
            ARTIFACT_FILES["portfolio_benchmark_catalog"],
            ARTIFACT_FILES["lens_bucket_benchmark_proxy_map"],
            ARTIFACT_FILES["synthetic_period_returns"],
            ARTIFACT_FILES["synthetic_attribution_weights_flows"],
            ARTIFACT_FILES["integrated_attribution_decomposition_inputs"],
            ARTIFACT_FILES["manager_attribution_prerequisites"],
        ],
        "source_metadata": _source_metadata("synthetic_attribution_readiness_summary"),
        "source_counts": {
            "manager_count": len(context["manager_mandates"]["manager_mandates"]),
            "lens_count": len(context["lenses"]),
            "lens_proxy_count": outputs["lens_bucket_benchmark_proxy_map"]["coverage_summary"][
                "proxy_count"
            ],
        },
    }


def build_manifest(context: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    readiness = outputs["attribution_readiness_summary"]
    return {
        "schema_version": "synthetic_attribution_prerequisite_pack_manifest.v1",
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "generated_at": GENERATED_AT,
        "generated_by": "python -m arangur.analytics.synthetic_attribution_prerequisites",
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "local_only": True,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "base_currency": BASE_CURRENCY,
        "portfolio_id": context["portfolio_id"],
        "portfolio_snapshot_id": context["portfolio_snapshot_id"],
        "source_position_catalog": context["source_paths"]["position_catalog"],
        "source_lens_catalog": context["source_paths"]["source_lens_catalog"],
        "source_manager_mandate_catalog": context["source_paths"][
            "source_manager_mandate_catalog"
        ],
        "included_artifacts": list(ARTIFACT_FILES.values()),
        "attribution_families_supported": [
            "integrated_performance_attribution_summary",
            "integrated_performance_attribution_detail",
            "manager_attribution_summary",
            "lens_based_performance_attribution",
        ],
        "attribution_families_gated": readiness["reports_still_gated"],
        "limitations": readiness["synthetic_demo_limitations"],
        "approval_status": "synthetic_demo_approved",
        "readiness_summary": readiness["report_readiness"],
    }


def validate_pack(context: dict[str, Any], outputs: dict[str, Any]) -> None:
    manifest = outputs["synthetic_attribution_prerequisite_pack_manifest"]
    if not manifest["synthetic_data"] or manifest["approval_status"] != "synthetic_demo_approved":
        raise ValueError("Attribution prerequisite manifest must be synthetic-demo approved")

    proxy_rows = outputs["lens_bucket_benchmark_proxy_map"]["proxy_map"]
    expected_buckets = {
        (lens_id, bucket["bucket_id"])
        for lens_id, lens in context["lenses"].items()
        for bucket in lens["primary_buckets"]
    }
    actual_buckets = {(row["lens_id"], row["bucket_id"]) for row in proxy_rows}
    if expected_buckets != actual_buckets:
        raise ValueError("Lens bucket proxy map does not cover every current lens bucket")

    weights = outputs["synthetic_attribution_weights_flows"]
    if abs(weights["reconciliation"]["manager_average_weights_sum"] - 1.0) > TIE_OUT_TOLERANCE:
        raise ValueError("Manager attribution weights do not sum to 100 percent")
    for lens_id, value in weights["reconciliation"]["lens_bucket_weights_sum_by_lens"].items():
        if abs(value - 1.0) > TIE_OUT_TOLERANCE:
            raise ValueError(f"Lens bucket weights do not sum to 100 percent for {lens_id}")
    for lens_id, value in weights["reconciliation"]["proxy_weights_sum_by_lens"].items():
        if abs(value - 1.0) > TIE_OUT_TOLERANCE:
            raise ValueError(f"Proxy weights do not sum to 100 percent for {lens_id}")

    decomposition = outputs["integrated_attribution_decomposition_inputs"]
    for mode in decomposition["supported_modes"]:
        if mode["mode"] == "whole_portfolio" and not mode["tie_out"]["ties_to_actual_return"]:
            raise ValueError("Whole-portfolio attribution decomposition does not tie out")
        if mode["strategy_timing"]["timing_status"] != "unavailable":
            raise ValueError("Timing should remain unavailable in this synthetic pack")

    current_manager_ids = {
        row["manager_id"] for row in context["manager_mandates"]["manager_mandates"]
    }
    manager_ids = {
        row["manager_id"]
        for row in outputs["manager_attribution_prerequisites"]["managers"]
    }
    if current_manager_ids != manager_ids:
        raise ValueError("Manager attribution prerequisites do not cover current managers")


def _manager_return_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for mandate in context["manager_mandates"]["manager_mandates"]:
        manager_id = mandate["manager_id"]
        inputs = MANAGER_RETURN_INPUTS[manager_id]
        rows.append(
            {
                "manager_id": manager_id,
                "display_name": mandate["manager_display_name"],
                "manager_return": _round_return(inputs["manager_return"]),
                "benchmark_return": _round_return(inputs["benchmark_return"]),
                "relative_return": _round_return(
                    inputs["manager_return"] - inputs["benchmark_return"]
                ),
                "synthetic_data": True,
            }
        )
    return rows


def _manager_weight_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for mandate in context["manager_mandates"]["manager_mandates"]:
        weight = _round_weight(float(mandate["portfolio_share"]))
        rows.append(
            {
                "manager_id": mandate["manager_id"],
                "display_name": mandate["manager_display_name"],
                "beginning_weight": weight,
                "average_weight": weight,
                "ending_weight": weight,
                "weight_basis": "base_value_share_synthetic",
            }
        )
    return rows


def _lens_weight_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for lens_id, assignments in context["lens_assignments"].items():
        for bucket in assignments["bucket_exposure_summary"]:
            rows.append(
                {
                    "lens_id": lens_id,
                    "bucket_id": bucket["bucket_id"],
                    "bucket_display_name": bucket["bucket_display_name"],
                    "weight": _round_weight(float(bucket["portfolio_share"])),
                    "weight_basis": "base_value_share_within_lens",
                }
            )
    return rows


def _lens_bucket_weight(context: dict[str, Any], lens_id: str, bucket_id: str) -> float:
    assignments = context["lens_assignments"][lens_id]
    for bucket in assignments["bucket_exposure_summary"]:
        if bucket["bucket_id"] == bucket_id:
            return _round_weight(float(bucket["portfolio_share"]))
    raise KeyError(f"Missing bucket weight for {lens_id}:{bucket_id}")


def _theme_benchmark_detail(
    context: dict[str, Any],
    returns: dict[str, Any],
    active_return: float,
) -> dict[str, Any]:
    lens_id = "ai_adoption"
    lens = context["lenses"][lens_id]
    rows = []
    for return_row in returns["lens_bucket_returns"]:
        if return_row["lens_id"] != lens_id:
            continue
        weight = _lens_bucket_weight(context, lens_id, return_row["bucket_id"])
        relative_return = _round_return(
            float(return_row["period_return"]) - float(return_row["proxy_period_return"])
        )
        total_effect = _round_return(weight * relative_return)
        rows.append(
            {
                "lens_id": lens_id,
                "lens_display_name": lens["display_name"],
                "bucket_id": return_row["bucket_id"],
                "bucket_display_name": return_row["bucket_display_name"],
                "weight": weight,
                "portfolio_return": return_row["period_return"],
                "theme_benchmark_return": return_row["proxy_period_return"],
                "relative_return": relative_return,
                "theme_benchmark_selection_effect": None,
                "theme_benchmark_sizing_effect": None,
                "asset_selection_effect": None,
                "asset_sizing_effect": None,
                "total_effect": total_effect,
                "component_status": "total_effect_available_components_not_separately_measured",
                "synthetic_data": True,
            }
        )

    rows.sort(key=lambda row: abs(float(row["total_effect"])), reverse=True)
    row_total = _round_return(sum(row["total_effect"] for row in rows))
    residual_unexplained = _round_return(active_return - row_total)
    return {
        "lens_id": lens_id,
        "lens_display_name": lens["display_name"],
        "detail_basis": "theme_bucket_weight_times_portfolio_minus_theme_benchmark_return",
        "rows": rows,
        "theme_bucket_total_effect": row_total,
        "residual_unexplained": residual_unexplained,
        "tie_out": {
            "active_return": active_return,
            "theme_bucket_total_effect": row_total,
            "residual_unexplained": residual_unexplained,
            "recomputed_active_return": _round_return(row_total + residual_unexplained),
            "ties_to_active_return": abs(
                active_return - _round_return(row_total + residual_unexplained)
            )
            <= TIE_OUT_TOLERANCE,
        },
        "component_effect_policy": (
            "Theme-bucket total effect is measured from available synthetic weights and returns; "
            "selection and sizing components are not separately measured at bucket level in v1."
        ),
        "timing_status": "unavailable",
    }


def _selected_position_returns(
    context: dict[str, Any],
    manager_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    manager_returns = {row["manager_id"]: row["manager_return"] for row in manager_rows}
    position_rows = []
    for index, base_row in enumerate(context["base_rows"][:12]):
        position = context["positions_by_id"][base_row["position_id"]]
        instrument = context["instruments_by_id"][base_row["instrument_id"]]
        adjustment = ((index % 5) - 2) * 0.001
        position_rows.append(
            {
                "position_id": base_row["position_id"],
                "display_name": position["display_name"],
                "manager_id": position["manager_id"],
                "instrument_type": instrument["instrument_type"],
                "period_return": _round_return(
                    manager_returns[position["manager_id"]] + adjustment
                ),
                "return_basis": "selected_synthetic_position_total_return",
                "synthetic_data": True,
            }
        )
    return position_rows


def _effect_breakdown(active_return: float) -> dict[str, float]:
    effects = {
        "strategy_lens_bucket_selection_effect": _round_return(active_return * 0.36),
        "strategy_lens_bucket_sizing_effect": _round_return(active_return * 0.22),
        "asset_selection_effect": _round_return(active_return * 0.28),
        "asset_sizing_effect": _round_return(active_return * 0.09),
    }
    effects["residual_unexplained"] = _round_return(active_return - sum(effects.values()))
    return effects


def _tie_out(
    benchmark_return: float,
    effects: dict[str, float],
    actual_return: float,
) -> dict[str, Any]:
    effect_total = _round_return(sum(effects.values()))
    recomputed_actual = _round_return(benchmark_return + effect_total)
    difference = _round_return(actual_return - recomputed_actual)
    return {
        "benchmark_return": benchmark_return,
        "effect_total": effect_total,
        "actual_return": actual_return,
        "recomputed_actual_return": recomputed_actual,
        "difference": difference,
        "ties_to_actual_return": abs(difference) <= TIE_OUT_TOLERANCE,
        "timing_used_as_residual": False,
    }


def _timing_unavailable() -> dict[str, str]:
    return {
        "timing_status": "unavailable",
        "reason": "Missing clean trade/holding history or deferred methodology.",
    }


def _proxy_type_for_bucket(bucket_id: str) -> str:
    if "neutral" in bucket_id or "unclassified" in bucket_id:
        return "policy_proxy"
    if "commodity" in bucket_id:
        return "synthetic_basket"
    if "platform" in bucket_id or "infrastructure" in bucket_id or "grid" in bucket_id:
        return "synthetic_index"
    if "single" in bucket_id:
        return "synthetic_single_security_proxy"
    return "synthetic_etf_proxy"


def _source_metadata(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "synthetic_data": True,
        "local_only": True,
        "external_data_used": False,
        "live_market_data_used": False,
        "real_client_data_used": False,
    }


def _round_return(value: Any) -> float:
    return round(float(value), 6)


def _round_weight(value: Any) -> float:
    return round(float(value), 6)


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the local synthetic attribution prerequisite pack."
    )
    parser.add_argument("--revaluation-dir", default=str(DEFAULT_REVALUATION_DIR))
    parser.add_argument(
        "--report-prerequisite-dir",
        default=str(DEFAULT_REPORT_PREREQUISITE_DIR),
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outputs = generate_synthetic_attribution_prerequisite_pack(
        revaluation_dir=args.revaluation_dir,
        report_prerequisite_dir=args.report_prerequisite_dir,
        output_dir=args.output_dir,
    )
    proxy_summary = outputs["lens_bucket_benchmark_proxy_map"]["coverage_summary"]
    readiness = outputs["attribution_readiness_summary"]

    print(f"Synthetic attribution prerequisite pack: {PACK_ID} -> {args.output_dir}")
    print(f"Benchmarks: {len(outputs['portfolio_benchmark_catalog']['benchmarks'])}")
    print(f"Lens proxy rows: {proxy_summary['proxy_count']}")
    print(
        "Managers: "
        + str(
            outputs["manager_attribution_prerequisites"]["coverage_summary"][
                "manager_prerequisite_count"
            ]
        )
    )
    print(
        "Supported attribution families: "
        + ", ".join(readiness["future_reports_can_now_be_mocked_honestly"])
    )
    print(
        "Timing status: "
        + readiness["timing_attribution_readiness"]["status"]
    )
    print(f"Output path: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
