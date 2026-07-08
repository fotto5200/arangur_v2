from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-08T00:00:00Z"
GENERATOR_VERSION = "synthetic_attribution_calculation_inputs.v1"
SOURCE_PACK_ID = "synthetic_attribution_prerequisite_pack_v1"
CALCULATION_PACK_ID = "synthetic_attribution_calculation_inputs_v1"
CALCULATION_PACK_VERSION = "2026-07-08"
SELECTED_LENS_ID = "ai_adoption"
TIE_OUT_TOLERANCE = 0.000001

DEFAULT_PREREQUISITE_DIR = Path(
    "data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1"
)
DEFAULT_REPORT_PREREQUISITE_DIR = Path(
    "data/simulation/report_prerequisites/synthetic_report_prerequisite_pack_v1"
)
DEFAULT_OUTPUT_DIR = DEFAULT_PREREQUISITE_DIR / "calculation_inputs"

ARTIFACT_FILES = {
    "manifest": "calculated_attribution_inputs_manifest.json",
    "selected_attribution_lens_policy": "selected_attribution_lens_policy.json",
    "theme_benchmark_weight_policy": "theme_benchmark_weight_policy.json",
    "theme_benchmark_return_inputs": "theme_benchmark_return_inputs.json",
    "theme_asset_calculation_inputs": "theme_asset_calculation_inputs.json",
    "manager_calculated_attribution_inputs": "manager_calculated_attribution_inputs.json",
    "calculated_attribution_readiness_summary": (
        "calculated_attribution_readiness_summary.json"
    ),
}

VALID_MANAGER_BENCHMARK_BASIS_TYPES = {
    "mandate_benchmark",
    "theme_benchmark_blend",
    "policy_benchmark",
    "hybrid_synthetic_demo",
}


def generate_synthetic_attribution_calculation_inputs(
    *,
    prerequisite_dir: str | Path = DEFAULT_PREREQUISITE_DIR,
    report_prerequisite_dir: str | Path = DEFAULT_REPORT_PREREQUISITE_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    context = load_source_context(
        prerequisite_dir=Path(prerequisite_dir),
        report_prerequisite_dir=Path(report_prerequisite_dir),
    )

    outputs: dict[str, Any] = {}
    outputs["selected_attribution_lens_policy"] = build_selected_lens_policy(context)
    outputs["theme_benchmark_weight_policy"] = build_theme_benchmark_weight_policy(
        context
    )
    outputs["theme_benchmark_return_inputs"] = build_theme_benchmark_return_inputs(
        context,
        outputs["theme_benchmark_weight_policy"],
    )
    outputs["theme_asset_calculation_inputs"] = build_theme_asset_calculation_inputs(
        context,
        outputs["theme_benchmark_return_inputs"],
    )
    outputs["manager_calculated_attribution_inputs"] = (
        build_manager_calculated_attribution_inputs(
            context,
            outputs["theme_benchmark_return_inputs"],
            outputs["theme_asset_calculation_inputs"],
        )
    )
    outputs["calculated_attribution_readiness_summary"] = build_readiness_summary(
        context,
        outputs,
    )
    outputs["manifest"] = build_manifest(context, outputs)

    validate_calculation_inputs(context, outputs)

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    for artifact_name, filename in ARTIFACT_FILES.items():
        _write_json(root / filename, outputs[artifact_name])

    return outputs


def load_source_context(
    *,
    prerequisite_dir: Path,
    report_prerequisite_dir: Path,
) -> dict[str, Any]:
    manifest = _load_json(prerequisite_dir / "synthetic_attribution_prerequisite_pack_manifest.json")
    benchmark_catalog = _load_json(prerequisite_dir / "portfolio_benchmark_catalog.json")
    period_returns = _load_json(prerequisite_dir / "synthetic_period_returns.json")
    weights_flows = _load_json(prerequisite_dir / "synthetic_attribution_weights_flows.json")
    manager_prerequisites = _load_json(prerequisite_dir / "manager_attribution_prerequisites.json")
    readiness = _load_json(prerequisite_dir / "attribution_readiness_summary.json")
    lens = _load_json(report_prerequisite_dir / "ai_adoption_lens_v1.json")
    lens_assignments = _load_json(
        report_prerequisite_dir / "position_lens_assignments_ai_adoption_v1.json"
    )
    manager_mandates = _load_json(report_prerequisite_dir / "manager_mandate_catalog.json")

    if lens["lens_id"] != SELECTED_LENS_ID:
        raise ValueError("Expected AI Adoption lens source")

    return {
        "source_paths": {
            "source_position_catalog": manifest["source_position_catalog"],
            "source_lens_assignments": _as_posix(
                report_prerequisite_dir
                / "position_lens_assignments_ai_adoption_v1.json"
            ),
            "source_lens_definition": _as_posix(
                report_prerequisite_dir / "ai_adoption_lens_v1.json"
            ),
            "source_benchmark_catalog": _as_posix(
                prerequisite_dir / "portfolio_benchmark_catalog.json"
            ),
            "source_period_returns": _as_posix(
                prerequisite_dir / "synthetic_period_returns.json"
            ),
            "source_weights_flows": _as_posix(
                prerequisite_dir / "synthetic_attribution_weights_flows.json"
            ),
            "source_manager_prerequisites": _as_posix(
                prerequisite_dir / "manager_attribution_prerequisites.json"
            ),
            "source_manager_mandates": _as_posix(
                report_prerequisite_dir / "manager_mandate_catalog.json"
            ),
        },
        "source_manifest": manifest,
        "benchmark_catalog": benchmark_catalog,
        "period_returns": period_returns,
        "weights_flows": weights_flows,
        "manager_prerequisites": manager_prerequisites,
        "readiness": readiness,
        "lens": lens,
        "lens_assignments": lens_assignments,
        "manager_mandates": manager_mandates,
        "bucket_order": [row["bucket_id"] for row in lens["primary_buckets"]],
        "bucket_display_names": {
            row["bucket_id"]: row["display_name"] for row in lens["primary_buckets"]
        },
    }


def build_selected_lens_policy(context: dict[str, Any]) -> dict[str, Any]:
    lens = context["lens"]
    return {
        "schema_version": "selected_attribution_lens_policy.v1",
        "pack_id": CALCULATION_PACK_ID,
        "pack_version": CALCULATION_PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_approved",
        "selected_lens_id": lens["lens_id"],
        "selected_lens_display_name": lens["display_name"],
        "lens_version": lens["lens_version"],
        "rationale": (
            "AI Adoption is the first calculated-attribution lens because the current "
            "synthetic prerequisite pack has complete position assignments, all seven "
            "bucket benchmark proxies, and existing attribution mockup alignment."
        ),
        "supported_scope": ["whole_portfolio", "manager_by_manager"],
        "bucket_ids": list(context["bucket_order"]),
        "buckets": [
            {
                "bucket_id": bucket["bucket_id"],
                "bucket_display_name": bucket["display_name"],
                "additive": bool(bucket["additive"]),
            }
            for bucket in lens["primary_buckets"]
        ],
        "neutral_bucket_treatment": {
            "bucket_id": lens["neutral_bucket_id"],
            "treatment": (
                "Included as an explicit additive bucket in policy, actual, detail, and "
                "manager calculations."
            ),
        },
        "review_bucket_treatment": {
            "bucket_id": lens["review_required_bucket_id"],
            "treatment": (
                "Included as an explicit additive bucket so review-required exposure is "
                "not hidden; caveats remain synthetic-demo only."
            ),
        },
        "buckets_are_additive": True,
        "timing_status": "unavailable",
        "limitations": [
            "Synthetic lens assignments are local demo inputs.",
            "This policy does not regenerate attribution reports or advisor-facing views.",
            "Timing remains gated until clean trade, holding, price, and flow history exists.",
        ],
        "source_metadata": _source_metadata("synthetic_ai_adoption_lens_policy"),
    }


def build_theme_benchmark_weight_policy(context: dict[str, Any]) -> dict[str, Any]:
    buckets = _selected_bucket_rows(context)
    equal_weights = _equal_weights(len(buckets))
    actual_weights = _actual_theme_weights(context)

    equal_bucket_rows = [
        {
            "bucket_id": row["bucket_id"],
            "bucket_display_name": row["bucket_display_name"],
            "weight": equal_weights[index],
        }
        for index, row in enumerate(buckets)
    ]
    actual_bucket_rows = [
        {
            "bucket_id": row["bucket_id"],
            "bucket_display_name": row["bucket_display_name"],
            "weight": actual_weights[row["bucket_id"]],
        }
        for row in buckets
    ]

    return {
        "schema_version": "theme_benchmark_weight_policy.v1",
        "pack_id": CALCULATION_PACK_ID,
        "pack_version": CALCULATION_PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_approved",
        "selected_lens_id": SELECTED_LENS_ID,
        "selected_lens_display_name": context["lens"]["display_name"],
        "weight_policies": [
            {
                "weight_policy_id": "ai_adoption_equal_weight_selected_buckets_v1",
                "weight_policy_type": "equal_weight_selected_buckets",
                "included_buckets": equal_bucket_rows,
                "weight_sum": _round_weight(
                    sum(row["weight"] for row in equal_bucket_rows)
                ),
                "return_calculation_convention": (
                    "sum(bucket_weight * theme_benchmark_return)"
                ),
                "rationale": (
                    "Equal weights provide a neutral synthetic policy mix for the first "
                    "calculation-input tranche and avoid claiming a real approved policy mix."
                ),
                "neutral_bucket_treatment": "included_with_equal_weight",
                "review_bucket_treatment": "included_with_equal_weight",
                "caveats": [
                    "Synthetic demo policy only.",
                    "Equal weights are not a production benchmark recommendation.",
                ],
            },
            {
                "weight_policy_id": "ai_adoption_actual_portfolio_theme_weights_v1",
                "weight_policy_type": "actual_portfolio_theme_weights",
                "included_buckets": actual_bucket_rows,
                "weight_sum": _round_weight(
                    sum(row["weight"] for row in actual_bucket_rows)
                ),
                "return_calculation_convention": (
                    "sum(actual_portfolio_theme_weight * theme_benchmark_return)"
                ),
                "rationale": (
                    "Actual weights come from the complete synthetic AI Adoption lens "
                    "assignment base-value shares."
                ),
                "neutral_bucket_treatment": "included_at_actual_portfolio_weight",
                "review_bucket_treatment": "included_at_actual_portfolio_weight",
                "caveats": [
                    "Synthetic demo actual weights only.",
                    "Review-required exposure remains visible rather than hidden.",
                ],
            },
        ],
        "policy_weight_sum_validation": {
            "ai_adoption_equal_weight_selected_buckets_v1": _round_weight(
                sum(row["weight"] for row in equal_bucket_rows)
            ),
            "ai_adoption_actual_portfolio_theme_weights_v1": _round_weight(
                sum(row["weight"] for row in actual_bucket_rows)
            ),
        },
        "source_metadata": _source_metadata("synthetic_ai_adoption_theme_weight_policy"),
    }


def build_theme_benchmark_return_inputs(
    context: dict[str, Any],
    weight_policy: dict[str, Any],
) -> dict[str, Any]:
    return_rows = _selected_bucket_rows(context)
    policy_weights = _weights_from_policy(
        weight_policy,
        "ai_adoption_equal_weight_selected_buckets_v1",
    )
    actual_weights = _weights_from_policy(
        weight_policy,
        "ai_adoption_actual_portfolio_theme_weights_v1",
    )
    global_benchmark_return = float(
        context["period_returns"]["benchmark_return"]["period_return"]
    )

    rows = []
    for row in return_rows:
        bucket_id = row["bucket_id"]
        policy_weight = policy_weights[bucket_id]
        actual_weight = actual_weights[bucket_id]
        theme_benchmark_return = float(row["theme_benchmark_return"])
        actual_theme_return = float(row["actual_portfolio_theme_return"])
        rows.append(
            {
                "bucket_id": bucket_id,
                "bucket_display_name": row["bucket_display_name"],
                "theme_benchmark_id": row["theme_benchmark_id"],
                "theme_benchmark_return": _round_return(theme_benchmark_return),
                "actual_portfolio_theme_return": _round_return(actual_theme_return),
                "policy_or_equal_weight": policy_weight,
                "actual_portfolio_weight": actual_weight,
                "benchmark_contribution_under_policy_weight": _round_return(
                    policy_weight * theme_benchmark_return
                ),
                "benchmark_contribution_under_actual_weight": _round_return(
                    actual_weight * theme_benchmark_return
                ),
                "portfolio_contribution_under_actual_weight": _round_return(
                    actual_weight * actual_theme_return
                ),
                "source_metadata": _source_metadata(
                    "synthetic_period_returns_and_ai_adoption_assignments"
                ),
            }
        )

    policy_benchmark_return = _round_return(
        sum(row["benchmark_contribution_under_policy_weight"] for row in rows)
    )
    actual_weight_benchmark_return = _round_return(
        sum(row["benchmark_contribution_under_actual_weight"] for row in rows)
    )
    actual_portfolio_theme_return = _round_return(
        sum(row["portfolio_contribution_under_actual_weight"] for row in rows)
    )
    theme_benchmark_selection = _round_return(
        policy_benchmark_return - global_benchmark_return
    )
    theme_benchmark_sizing = _round_return(
        actual_weight_benchmark_return - policy_benchmark_return
    )
    theme_asset_total = _round_return(
        actual_portfolio_theme_return - actual_weight_benchmark_return
    )
    residual_to_global = _round_return(
        actual_portfolio_theme_return
        - global_benchmark_return
        - theme_benchmark_selection
        - theme_benchmark_sizing
        - theme_asset_total
    )

    return {
        "schema_version": "theme_benchmark_return_inputs.v1",
        "pack_id": CALCULATION_PACK_ID,
        "pack_version": CALCULATION_PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_approved",
        "selected_lens_id": SELECTED_LENS_ID,
        "selected_lens_display_name": context["lens"]["display_name"],
        "global_benchmark_id": context["period_returns"]["benchmark_return"][
            "benchmark_id"
        ],
        "global_benchmark_return": _round_return(global_benchmark_return),
        "policy_weight_policy_id": "ai_adoption_equal_weight_selected_buckets_v1",
        "actual_weight_policy_id": "ai_adoption_actual_portfolio_theme_weights_v1",
        "policy_or_equal_weight_theme_benchmark_return": policy_benchmark_return,
        "actual_weight_theme_benchmark_return": actual_weight_benchmark_return,
        "actual_portfolio_theme_return": actual_portfolio_theme_return,
        "theme_benchmark_selection_effect_input": theme_benchmark_selection,
        "theme_benchmark_sizing_effect_input": theme_benchmark_sizing,
        "theme_asset_total_effect_input": theme_asset_total,
        "initial_residual_to_global_benchmark": residual_to_global,
        "rows": rows,
        "calculation_conventions": {
            "policy_or_equal_weight_theme_benchmark_return": (
                "sum(policy_or_equal_weight * theme_benchmark_return)"
            ),
            "actual_weight_theme_benchmark_return": (
                "sum(actual_portfolio_weight * theme_benchmark_return)"
            ),
            "theme_benchmark_selection_effect_input": (
                "policy_or_equal_weight_theme_benchmark_return - global_benchmark_return"
            ),
            "theme_benchmark_sizing_effect_input": (
                "actual_weight_theme_benchmark_return - policy_or_equal_weight_theme_benchmark_return"
            ),
            "theme_asset_total_effect_input": (
                "actual_portfolio_theme_return - actual_weight_theme_benchmark_return"
            ),
        },
        "source_metadata": _source_metadata("synthetic_ai_adoption_theme_return_inputs"),
    }


def build_theme_asset_calculation_inputs(
    context: dict[str, Any],
    theme_returns: dict[str, Any],
) -> dict[str, Any]:
    buckets = []
    rows_by_bucket = {row["bucket_id"]: row for row in theme_returns["rows"]}
    for bucket_id in context["bucket_order"]:
        return_row = rows_by_bucket[bucket_id]
        bucket_assignments = [
            row
            for row in context["lens_assignments"]["assignments"]
            if row["primary_bucket_id"] == bucket_id
        ]
        compact_assets = _compact_asset_rows(
            bucket_assignments,
            bucket_display_name=return_row["bucket_display_name"],
            bucket_return=float(return_row["actual_portfolio_theme_return"]),
            bucket_benchmark_return=float(return_row["theme_benchmark_return"]),
        )
        reference_weight_asset_return = _round_return(
            sum(
                asset["reference_asset_weight_within_bucket"]
                * asset["asset_return"]
                for asset in compact_assets
            )
        )
        actual_weight_asset_return = _round_return(
            sum(
                asset["actual_asset_weight_within_bucket"] * asset["asset_return"]
                for asset in compact_assets
            )
        )
        actual_portfolio_weight = float(return_row["actual_portfolio_weight"])
        theme_benchmark_return = float(return_row["theme_benchmark_return"])
        asset_selection_effect = _round_return(
            actual_portfolio_weight
            * (reference_weight_asset_return - theme_benchmark_return)
        )
        asset_sizing_effect = _round_return(
            actual_portfolio_weight
            * (actual_weight_asset_return - reference_weight_asset_return)
        )
        buckets.append(
            {
                "bucket_id": bucket_id,
                "bucket_display_name": return_row["bucket_display_name"],
                "actual_portfolio_weight": _round_weight(actual_portfolio_weight),
                "theme_benchmark_return": _round_return(theme_benchmark_return),
                "assets": compact_assets,
                "bucket_level_totals": {
                    "actual_asset_weight_sum": _round_weight(
                        sum(
                            asset["actual_asset_weight_within_bucket"]
                            for asset in compact_assets
                        )
                    ),
                    "reference_asset_weight_sum": _round_weight(
                        sum(
                            asset["reference_asset_weight_within_bucket"]
                            for asset in compact_assets
                        )
                    ),
                    "actual_weight_asset_return": actual_weight_asset_return,
                    "reference_weight_asset_return": reference_weight_asset_return,
                    "asset_selection_effect_input": asset_selection_effect,
                    "asset_sizing_effect_input": asset_sizing_effect,
                    "asset_total_effect_input": _round_return(
                        asset_selection_effect + asset_sizing_effect
                    ),
                    "actual_minus_theme_benchmark_effect_input": _round_return(
                        actual_portfolio_weight
                        * (actual_weight_asset_return - theme_benchmark_return)
                    ),
                    "caveats": [
                        "Compact grouped synthetic assets only.",
                        "These rows are calculation inputs, not final report rows.",
                    ],
                },
            }
        )

    total_asset_selection = _round_return(
        sum(row["bucket_level_totals"]["asset_selection_effect_input"] for row in buckets)
    )
    total_asset_sizing = _round_return(
        sum(row["bucket_level_totals"]["asset_sizing_effect_input"] for row in buckets)
    )

    return {
        "schema_version": "theme_asset_calculation_inputs.v1",
        "pack_id": CALCULATION_PACK_ID,
        "pack_version": CALCULATION_PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_approved",
        "selected_lens_id": SELECTED_LENS_ID,
        "selected_lens_display_name": context["lens"]["display_name"],
        "asset_set_policy": {
            "asset_set_type": "compact_grouped_synthetic_assets",
            "max_named_positions_per_bucket": 3,
            "grouped_remaining_positions": True,
            "reference_weight_policy": "equal_weight_within_compact_bucket_asset_set",
            "source_position_ids_available": True,
        },
        "buckets": buckets,
        "portfolio_level_totals": {
            "asset_selection_effect_input": total_asset_selection,
            "asset_sizing_effect_input": total_asset_sizing,
            "asset_total_effect_input": _round_return(
                total_asset_selection + total_asset_sizing
            ),
        },
        "source_metadata": _source_metadata("synthetic_ai_adoption_asset_inputs"),
    }


def build_manager_calculated_attribution_inputs(
    context: dict[str, Any],
    theme_returns: dict[str, Any],
    asset_inputs: dict[str, Any],
) -> dict[str, Any]:
    manager_rows = []
    theme_return_rows = {row["bucket_id"]: row for row in theme_returns["rows"]}
    asset_totals = {
        row["bucket_id"]: row["bucket_level_totals"]
        for row in asset_inputs["buckets"]
    }
    manager_prereq_by_id = {
        row["manager_id"]: row for row in context["manager_prerequisites"]["managers"]
    }
    manager_mandates_by_id = {
        row["manager_id"]: row for row in context["manager_mandates"]["manager_mandates"]
    }
    policy_return = float(
        theme_returns["policy_or_equal_weight_theme_benchmark_return"]
    )

    for manager_id in sorted(manager_prereq_by_id):
        prereq = manager_prereq_by_id[manager_id]
        mandate = manager_mandates_by_id[manager_id]
        manager_theme_weights = _manager_theme_weights(context, manager_id)
        theme_benchmark_blend_return = _round_return(
            sum(
                row["weight"] * theme_return_rows[row["bucket_id"]]["theme_benchmark_return"]
                for row in manager_theme_weights
            )
        )
        manager_actual_theme_return = _round_return(
            sum(
                row["weight"]
                * theme_return_rows[row["bucket_id"]]["actual_portfolio_theme_return"]
                for row in manager_theme_weights
            )
        )
        manager_asset_selection = _round_return(
            sum(
                row["weight"]
                * (
                    asset_totals[row["bucket_id"]]["reference_weight_asset_return"]
                    - theme_return_rows[row["bucket_id"]]["theme_benchmark_return"]
                )
                for row in manager_theme_weights
            )
        )
        manager_asset_sizing = _round_return(
            sum(
                row["weight"]
                * (
                    asset_totals[row["bucket_id"]]["actual_weight_asset_return"]
                    - asset_totals[row["bucket_id"]]["reference_weight_asset_return"]
                )
                for row in manager_theme_weights
            )
        )
        manager_return = float(prereq["manager_return"])
        manager_benchmark_return = float(prereq["benchmark_proxy_return"])
        manager_theme_selection = _round_return(policy_return - manager_benchmark_return)
        manager_theme_sizing = _round_return(theme_benchmark_blend_return - policy_return)
        relative_return = _round_return(manager_return - manager_benchmark_return)
        residual = _round_return(
            relative_return
            - manager_theme_selection
            - manager_theme_sizing
            - manager_asset_selection
            - manager_asset_sizing
        )
        recomputed_relative = _round_return(
            manager_theme_selection
            + manager_theme_sizing
            + manager_asset_selection
            + manager_asset_sizing
            + residual
        )
        manager_rows.append(
            {
                "manager_id": manager_id,
                "display_name": prereq["display_name"],
                "approved_role": prereq["approved_role"],
                "portfolio_weight": prereq["portfolio_weight"],
                "manager_benchmark_basis_type": "hybrid_synthetic_demo",
                "benchmark_basis_description": (
                    "Uses the existing manager-specific synthetic mandate proxy as the "
                    "manager comparison benchmark, while separately storing the selected "
                    "AI Adoption theme-benchmark blend needed for future calculated effects."
                ),
                "manager_benchmark_components": [
                    {
                        "component_type": "manager_specific_synthetic_mandate_proxy",
                        "proxy_id": prereq["manager_benchmark_proxy"]["proxy_id"],
                        "proxy_display_name": prereq["manager_benchmark_proxy"][
                            "proxy_display_name"
                        ],
                        "component_return": _round_return(manager_benchmark_return),
                    },
                    {
                        "component_type": "selected_lens_theme_benchmark_blend",
                        "selected_lens_id": SELECTED_LENS_ID,
                        "component_return": theme_benchmark_blend_return,
                    },
                ],
                "manager_return": _round_return(manager_return),
                "manager_benchmark_return": _round_return(manager_benchmark_return),
                "manager_theme_weights": manager_theme_weights,
                "manager_theme_weight_sum": _round_weight(
                    sum(row["weight"] for row in manager_theme_weights)
                ),
                "manager_theme_benchmark_blend_return": theme_benchmark_blend_return,
                "manager_actual_theme_return": manager_actual_theme_return,
                "manager_theme_selection_input": manager_theme_selection,
                "manager_theme_sizing_input": manager_theme_sizing,
                "manager_asset_selection_input": manager_asset_selection,
                "manager_asset_sizing_input": manager_asset_sizing,
                "residual_input": residual,
                "timing_status": "unavailable",
                "tie_out_status": {
                    "manager_relative_return": relative_return,
                    "recomputed_relative_return": recomputed_relative,
                    "difference": _round_return(relative_return - recomputed_relative),
                    "ties_to_manager_relative_return": abs(
                        relative_return - recomputed_relative
                    )
                    <= TIE_OUT_TOLERANCE,
                    "timing_used_as_residual": False,
                },
                "caveats": [
                    "Synthetic demo manager calculation inputs only.",
                    "Manager benchmark basis is explicit but not production-approved.",
                ],
                "source_metadata": {
                    **_source_metadata("synthetic_manager_calculated_attribution_inputs"),
                    "mandate_source": mandate["approval_status"],
                },
            }
        )

    return {
        "schema_version": "manager_calculated_attribution_inputs.v1",
        "pack_id": CALCULATION_PACK_ID,
        "pack_version": CALCULATION_PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_approved",
        "selected_lens_id": SELECTED_LENS_ID,
        "selected_lens_display_name": context["lens"]["display_name"],
        "managers": manager_rows,
        "coverage_summary": {
            "manager_count": len(manager_rows),
            "all_current_managers_covered": True,
            "all_manager_benchmark_basis_types_explicit": True,
            "manager_theme_weights_reconcile": all(
                abs(row["manager_theme_weight_sum"] - 1.0) <= TIE_OUT_TOLERANCE
                for row in manager_rows
            ),
            "manager_tie_outs_reconcile": all(
                row["tie_out_status"]["ties_to_manager_relative_return"]
                for row in manager_rows
            ),
        },
        "source_metadata": _source_metadata("synthetic_manager_calculation_inputs"),
    }


def build_readiness_summary(
    context: dict[str, Any],
    outputs: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "calculated_attribution_readiness_summary.v1",
        "pack_id": CALCULATION_PACK_ID,
        "pack_version": CALCULATION_PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_approved",
        "selected_lens_id": SELECTED_LENS_ID,
        "selected_lens_display_name": context["lens"]["display_name"],
        "summary_attribution_calculation_inputs": "ready_for_synthetic_demo_calculation",
        "detail_attribution_calculation_inputs": "ready_for_selected_lens_synthetic_demo_calculation",
        "manager_level_calculation_inputs": "ready_for_synthetic_demo_calculation",
        "theme_benchmark_selection_can_be_calculated": True,
        "theme_benchmark_sizing_can_be_calculated": True,
        "asset_selection_can_be_calculated": True,
        "asset_sizing_can_be_calculated": True,
        "manager_effects_can_be_calculated": True,
        "timing_status": "unavailable",
        "timing_gate": {
            "status": "unavailable",
            "reason": (
                "No clean beginning/ending holdings, trade dates, external flows, "
                "price path, and approved timing methodology are included."
            ),
        },
        "residual_policy": {
            "policy": "explicit_reconciler_after_calculated_effects",
            "tolerance": TIE_OUT_TOLERANCE,
            "timing_used_as_residual": False,
        },
        "missing_inputs": [
            "Production-approved return and benchmark history.",
            "Client-approved attribution method and report disclosure policy.",
            "Clean timing history and approved timing methodology.",
        ],
        "recommended_next_implementation_tranche": (
            "Calculated Synthetic Attribution Engine v1"
        ),
        "supporting_artifacts": [
            ARTIFACT_FILES["selected_attribution_lens_policy"],
            ARTIFACT_FILES["theme_benchmark_weight_policy"],
            ARTIFACT_FILES["theme_benchmark_return_inputs"],
            ARTIFACT_FILES["theme_asset_calculation_inputs"],
            ARTIFACT_FILES["manager_calculated_attribution_inputs"],
        ],
        "source_metadata": _source_metadata("synthetic_calculated_attribution_readiness"),
    }


def build_manifest(context: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    readiness = outputs["calculated_attribution_readiness_summary"]
    return {
        "schema_version": "calculated_attribution_inputs_manifest.v1",
        "pack_id": CALCULATION_PACK_ID,
        "source_pack_id": SOURCE_PACK_ID,
        "pack_version": CALCULATION_PACK_VERSION,
        "generated_at": GENERATED_AT,
        "generated_by": "python -m arangur.analytics.synthetic_attribution_calculation_inputs",
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "local_only": True,
        "period_start": context["source_manifest"]["period_start"],
        "period_end": context["source_manifest"]["period_end"],
        "selected_attribution_lens": {
            "lens_id": SELECTED_LENS_ID,
            "display_name": context["lens"]["display_name"],
            "lens_version": context["lens"]["lens_version"],
        },
        "source_position_catalog": context["source_paths"]["source_position_catalog"],
        "source_lens_assignments": context["source_paths"]["source_lens_assignments"],
        "source_benchmark_catalog": context["source_paths"]["source_benchmark_catalog"],
        "included_artifacts": list(ARTIFACT_FILES.values()),
        "supported_future_calculations": [
            "theme_benchmark_selection",
            "theme_benchmark_sizing",
            "asset_selection",
            "asset_sizing",
            "manager_level_effects",
            "residual_unexplained",
        ],
        "unsupported_future_calculations": [
            "timing_attribution",
            "production_attribution",
            "scenario_versus_benchmark",
            "probabilistic_scenario_range",
            "current_versus_proposed_attribution",
        ],
        "timing_status": readiness["timing_status"],
        "residual_policy": readiness["residual_policy"],
        "limitations": [
            "Synthetic calculation-input artifacts only.",
            "No final attribution report mockups are regenerated by this tranche.",
            "No advisor UI or generated-report wiring is changed by this tranche.",
            "Timing remains gated and is not used as residual noise.",
        ],
        "approval_status": "synthetic_demo_approved",
    }


def validate_calculation_inputs(
    context: dict[str, Any],
    outputs: dict[str, Any],
) -> None:
    manifest = outputs["manifest"]
    if not manifest["synthetic_data"]:
        raise ValueError("Calculation input manifest must declare synthetic data")
    if manifest["approval_status"] != "synthetic_demo_approved":
        raise ValueError("Calculation input manifest must be synthetic-demo approved")

    weight_policy = outputs["theme_benchmark_weight_policy"]
    for policy in weight_policy["weight_policies"]:
        if abs(policy["weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
            raise ValueError(f"Theme weight policy does not sum to 1: {policy['weight_policy_id']}")

    expected_actual_weights = {
        row["bucket_id"]: _round_weight(float(row["portfolio_share"]))
        for row in context["lens_assignments"]["bucket_exposure_summary"]
    }
    actual_policy = _weights_from_policy(
        weight_policy,
        "ai_adoption_actual_portfolio_theme_weights_v1",
    )
    if actual_policy != expected_actual_weights:
        raise ValueError("Actual theme weights do not reconcile to source assignments")

    theme_returns = outputs["theme_benchmark_return_inputs"]
    if {row["bucket_id"] for row in theme_returns["rows"]} != set(context["bucket_order"]):
        raise ValueError("Theme benchmark return inputs do not cover selected lens buckets")
    recomputed_policy_return = _round_return(
        sum(row["benchmark_contribution_under_policy_weight"] for row in theme_returns["rows"])
    )
    if recomputed_policy_return != theme_returns["policy_or_equal_weight_theme_benchmark_return"]:
        raise ValueError("Policy theme benchmark return does not reconcile")
    recomputed_actual_benchmark_return = _round_return(
        sum(row["benchmark_contribution_under_actual_weight"] for row in theme_returns["rows"])
    )
    if recomputed_actual_benchmark_return != theme_returns["actual_weight_theme_benchmark_return"]:
        raise ValueError("Actual-weight theme benchmark return does not reconcile")

    asset_inputs = outputs["theme_asset_calculation_inputs"]
    for bucket in asset_inputs["buckets"]:
        totals = bucket["bucket_level_totals"]
        if abs(totals["actual_asset_weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
            raise ValueError(f"Actual asset weights do not sum to 1 for {bucket['bucket_id']}")
        if abs(totals["reference_asset_weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
            raise ValueError(f"Reference asset weights do not sum to 1 for {bucket['bucket_id']}")
        if not isinstance(totals["asset_selection_effect_input"], float):
            raise ValueError("Asset selection input must be numeric")
        if not isinstance(totals["asset_sizing_effect_input"], float):
            raise ValueError("Asset sizing input must be numeric")

    manager_inputs = outputs["manager_calculated_attribution_inputs"]
    current_manager_ids = {
        row["manager_id"] for row in context["manager_prerequisites"]["managers"]
    }
    generated_manager_ids = {row["manager_id"] for row in manager_inputs["managers"]}
    if current_manager_ids != generated_manager_ids:
        raise ValueError("Manager calculation inputs do not cover every current manager")
    for row in manager_inputs["managers"]:
        if row["manager_benchmark_basis_type"] not in VALID_MANAGER_BENCHMARK_BASIS_TYPES:
            raise ValueError(f"Invalid manager benchmark basis: {row['manager_id']}")
        if abs(row["manager_theme_weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
            raise ValueError(f"Manager theme weights do not sum to 1: {row['manager_id']}")
        if not row["tie_out_status"]["ties_to_manager_relative_return"]:
            raise ValueError(f"Manager input does not tie out: {row['manager_id']}")
        if row["timing_status"] != "unavailable":
            raise ValueError("Timing must remain unavailable")
        if row["tie_out_status"]["timing_used_as_residual"]:
            raise ValueError("Timing must not be used as residual")

    readiness = outputs["calculated_attribution_readiness_summary"]
    if readiness["timing_status"] != "unavailable":
        raise ValueError("Readiness summary must keep timing unavailable")
    if readiness["residual_policy"]["timing_used_as_residual"]:
        raise ValueError("Residual policy must not use timing as residual")


def _selected_bucket_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    returns_by_bucket = {
        row["bucket_id"]: row
        for row in context["period_returns"]["lens_bucket_returns"]
        if row["lens_id"] == SELECTED_LENS_ID
    }
    rows = []
    for bucket_id in context["bucket_order"]:
        row = returns_by_bucket[bucket_id]
        rows.append(
            {
                "bucket_id": bucket_id,
                "bucket_display_name": row["bucket_display_name"],
                "theme_benchmark_id": row["proxy_id"],
                "theme_benchmark_return": row["proxy_period_return"],
                "actual_portfolio_theme_return": row["period_return"],
            }
        )
    return rows


def _actual_theme_weights(context: dict[str, Any]) -> dict[str, float]:
    return {
        row["bucket_id"]: _round_weight(float(row["weight"]))
        for row in context["weights_flows"]["lens_bucket_weights"]
        if row["lens_id"] == SELECTED_LENS_ID
    }


def _weights_from_policy(
    weight_policy: dict[str, Any],
    weight_policy_id: str,
) -> dict[str, float]:
    policy = next(
        row for row in weight_policy["weight_policies"]
        if row["weight_policy_id"] == weight_policy_id
    )
    return {
        row["bucket_id"]: _round_weight(float(row["weight"]))
        for row in policy["included_buckets"]
    }


def _compact_asset_rows(
    assignments: list[dict[str, Any]],
    *,
    bucket_display_name: str,
    bucket_return: float,
    bucket_benchmark_return: float,
) -> list[dict[str, Any]]:
    sorted_rows = sorted(
        assignments,
        key=lambda row: (-float(row["base_value"]), row["position_id"]),
    )
    if not sorted_rows:
        raise ValueError(f"No assignments for bucket {bucket_display_name}")

    grouped_rows: list[dict[str, Any]] = []
    for row in sorted_rows[:3]:
        grouped_rows.append(
            {
                "synthetic_asset_id": row["position_id"],
                "display_name": row["display_name"],
                "position_ids": [row["position_id"]],
                "base_value": float(row["base_value"]),
                "source_kind": "source_position",
            }
        )
    remaining = sorted_rows[3:]
    if remaining:
        grouped_rows.append(
            {
                "synthetic_asset_id": (
                    "grouped_remaining_"
                    + _slug(bucket_display_name)
                    + "_synthetic_assets"
                ),
                "display_name": f"Grouped remaining {bucket_display_name} exposure",
                "position_ids": [row["position_id"] for row in remaining],
                "base_value": sum(float(row["base_value"]) for row in remaining),
                "source_kind": "grouped_synthetic_positions",
            }
        )

    base_value_total = sum(row["base_value"] for row in grouped_rows)
    actual_weights = _round_weights_preserve_sum(
        [row["base_value"] / base_value_total for row in grouped_rows]
    )
    reference_weights = _equal_weights(len(grouped_rows))
    asset_returns = _asset_returns_for_bucket(
        actual_weights=actual_weights,
        bucket_return=bucket_return,
    )

    assets = []
    for row, actual_weight, reference_weight, asset_return in zip(
        grouped_rows,
        actual_weights,
        reference_weights,
        asset_returns,
    ):
        assets.append(
            {
                "synthetic_asset_id": row["synthetic_asset_id"],
                "display_name": row["display_name"],
                "position_ids": row["position_ids"],
                "actual_asset_weight_within_bucket": actual_weight,
                "reference_asset_weight_within_bucket": reference_weight,
                "asset_return": asset_return,
                "reference_return": _round_return(bucket_benchmark_return),
                "benchmark_component_return": _round_return(bucket_benchmark_return),
                "source_metadata": {
                    **_source_metadata("synthetic_grouped_asset_calculation_input"),
                    "source_kind": row["source_kind"],
                },
            }
        )
    return assets


def _asset_returns_for_bucket(
    *,
    actual_weights: list[float],
    bucket_return: float,
) -> list[float]:
    if len(actual_weights) == 1:
        return [_round_return(bucket_return)]

    center = (len(actual_weights) - 1) / 2
    spread = 0.0035
    preliminary = [
        bucket_return + ((index - center) * spread)
        for index in range(len(actual_weights))
    ]
    actual_preliminary = sum(
        weight * value for weight, value in zip(actual_weights, preliminary)
    )
    adjustment = bucket_return - actual_preliminary
    returns = [_round_return(value + adjustment) for value in preliminary]
    if actual_weights[-1] > 0:
        prior = sum(
            weight * value
            for weight, value in zip(actual_weights[:-1], returns[:-1])
        )
        returns[-1] = _round_return((bucket_return - prior) / actual_weights[-1])
    return returns


def _manager_theme_weights(context: dict[str, Any], manager_id: str) -> list[dict[str, Any]]:
    assignments = [
        row for row in context["lens_assignments"]["assignments"]
        if row["manager_id"] == manager_id
    ]
    total_base_value = sum(float(row["base_value"]) for row in assignments)
    if total_base_value <= 0:
        raise ValueError(f"Manager has no AI Adoption assignment base value: {manager_id}")

    raw_weights = []
    for bucket_id in context["bucket_order"]:
        bucket_base_value = sum(
            float(row["base_value"])
            for row in assignments
            if row["primary_bucket_id"] == bucket_id
        )
        raw_weights.append(bucket_base_value / total_base_value)

    weights = _round_weights_preserve_sum(raw_weights)

    return [
        {
            "bucket_id": bucket_id,
            "bucket_display_name": context["bucket_display_names"][bucket_id],
            "weight": weight,
            "weight_basis": "manager_base_value_share_within_selected_lens",
        }
        for bucket_id, weight in zip(context["bucket_order"], weights)
    ]


def _equal_weights(count: int) -> list[float]:
    if count <= 0:
        raise ValueError("Cannot build equal weights for an empty set")
    weight = _round_weight(1.0 / count)
    weights = [weight for _ in range(count)]
    weights[-1] = _round_weight(1.0 - sum(weights[:-1]))
    return weights


def _round_weights_preserve_sum(values: list[float]) -> list[float]:
    if not values:
        raise ValueError("Cannot round an empty weight set")
    weights = [_round_weight(value) for value in values]
    difference = _round_weight(1.0 - sum(weights))
    if difference:
        index = max(range(len(weights)), key=lambda item: values[item])
        weights[index] = _round_weight(weights[index] + difference)
    return weights


def _source_metadata(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "synthetic_data": True,
        "local_only": True,
        "external_data_used": False,
        "live_market_data_used": False,
        "real_client_data_used": False,
    }


def _slug(value: str) -> str:
    return (
        value.lower()
        .replace("/", " ")
        .replace("-", " ")
        .replace("&", " and ")
        .replace("  ", " ")
        .strip()
        .replace(" ", "_")
    )


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
        description="Generate lower-level synthetic attribution calculation inputs."
    )
    parser.add_argument("--prerequisite-dir", default=str(DEFAULT_PREREQUISITE_DIR))
    parser.add_argument(
        "--report-prerequisite-dir",
        default=str(DEFAULT_REPORT_PREREQUISITE_DIR),
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outputs = generate_synthetic_attribution_calculation_inputs(
        prerequisite_dir=args.prerequisite_dir,
        report_prerequisite_dir=args.report_prerequisite_dir,
        output_dir=args.output_dir,
    )
    lens = outputs["selected_attribution_lens_policy"]
    readiness = outputs["calculated_attribution_readiness_summary"]
    manager_inputs = outputs["manager_calculated_attribution_inputs"]

    print(
        f"Synthetic attribution calculation inputs: {CALCULATION_PACK_ID} -> {args.output_dir}"
    )
    print(f"Selected lens: {lens['selected_lens_display_name']}")
    print(f"Buckets: {len(lens['buckets'])}")
    print(f"Managers: {manager_inputs['coverage_summary']['manager_count']}")
    print(
        "Summary inputs ready: "
        + str(
            readiness["summary_attribution_calculation_inputs"]
            == "ready_for_synthetic_demo_calculation"
        )
    )
    print(
        "Detail inputs ready: "
        + str(
            readiness["detail_attribution_calculation_inputs"]
            == "ready_for_selected_lens_synthetic_demo_calculation"
        )
    )
    print(
        "Manager inputs ready: "
        + str(
            readiness["manager_level_calculation_inputs"]
            == "ready_for_synthetic_demo_calculation"
        )
    )
    print(f"Timing status: {readiness['timing_status']}")
    print(f"Output path: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
