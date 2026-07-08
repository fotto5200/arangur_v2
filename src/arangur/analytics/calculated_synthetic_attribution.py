from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-08T00:00:00Z"
ENGINE_ID = "synthetic_attribution_engine_v1"
ENGINE_VERSION = "2026-07-08"
GENERATOR_VERSION = "calculated_synthetic_attribution.v1"
SOURCE_PREREQUISITE_PACK_ID = "synthetic_attribution_prerequisite_pack_v1"
SOURCE_CALCULATION_PACK_ID = "synthetic_attribution_calculation_inputs_v1"
SELECTED_LENS_ID = "ai_adoption"
TIE_OUT_TOLERANCE = 0.000001
RESIDUAL_REVIEW_THRESHOLD = 0.005
ASSET_DISTRIBUTION_ROUNDING_TOLERANCE = 0.00001

DEFAULT_CALCULATION_INPUT_DIR = Path(
    "data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1/calculation_inputs"
)
DEFAULT_SOURCE_PREREQUISITE_DIR = DEFAULT_CALCULATION_INPUT_DIR.parent
DEFAULT_OUTPUT_DIR = Path("data/simulation/attribution_calculated") / ENGINE_ID

CALCULATION_INPUT_FILES = {
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

ARTIFACT_FILES = {
    "manifest": "calculated_attribution_engine_manifest.json",
    "whole_portfolio_summary": "whole_portfolio_calculated_attribution_summary.json",
    "theme_benchmark_detail": "theme_benchmark_calculated_detail.json",
    "theme_asset_detail": "theme_asset_calculated_attribution_detail.json",
    "manager_summary": "manager_calculated_attribution_summary.json",
    "quality_summary": "calculated_attribution_quality_summary.json",
}


def generate_calculated_synthetic_attribution(
    *,
    calculation_input_dir: str | Path = DEFAULT_CALCULATION_INPUT_DIR,
    source_prerequisite_dir: str | Path = DEFAULT_SOURCE_PREREQUISITE_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    context = load_source_context(
        calculation_input_dir=Path(calculation_input_dir),
        source_prerequisite_dir=Path(source_prerequisite_dir),
    )

    outputs: dict[str, Any] = {}
    outputs["theme_asset_detail"] = build_theme_asset_calculated_detail(context)
    outputs["theme_benchmark_detail"] = build_theme_benchmark_calculated_detail(
        context,
        outputs["theme_asset_detail"],
    )
    outputs["whole_portfolio_summary"] = build_whole_portfolio_summary(
        context,
        outputs["theme_asset_detail"],
    )
    outputs["manager_summary"] = build_manager_calculated_summary(context)
    outputs["quality_summary"] = build_quality_summary(context, outputs)
    outputs["manifest"] = build_manifest(context, outputs)

    validate_calculated_outputs(context, outputs)

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    for artifact_name, filename in ARTIFACT_FILES.items():
        _write_json(root / filename, outputs[artifact_name])

    return outputs


def load_source_context(
    *,
    calculation_input_dir: Path,
    source_prerequisite_dir: Path,
) -> dict[str, Any]:
    calculation_inputs = {
        artifact_name: _load_json(calculation_input_dir / filename)
        for artifact_name, filename in CALCULATION_INPUT_FILES.items()
    }
    period_returns = _load_json(source_prerequisite_dir / "synthetic_period_returns.json")

    manifest = calculation_inputs["manifest"]
    selected_lens = manifest["selected_attribution_lens"]
    if selected_lens["lens_id"] != SELECTED_LENS_ID:
        raise ValueError("Calculated synthetic attribution v1 expects AI Adoption inputs")
    if manifest["pack_id"] != SOURCE_CALCULATION_PACK_ID:
        raise ValueError("Unexpected source calculation input pack")

    return {
        "source_paths": {
            "calculation_input_dir": _portable_path(calculation_input_dir),
            "source_prerequisite_dir": _portable_path(source_prerequisite_dir),
            "source_period_returns": _portable_path(
                source_prerequisite_dir / "synthetic_period_returns.json"
            ),
            **{
                artifact_name: _portable_path(calculation_input_dir / filename)
                for artifact_name, filename in CALCULATION_INPUT_FILES.items()
            },
        },
        "calculation_inputs": calculation_inputs,
        "period_returns": period_returns,
        "period_start": manifest["period_start"],
        "period_end": manifest["period_end"],
        "selected_attribution_lens": selected_lens,
        "residual_policy": manifest["residual_policy"],
        "timing_status": manifest["timing_status"],
        "bucket_order": calculation_inputs["selected_attribution_lens_policy"][
            "bucket_ids"
        ],
    }


def build_whole_portfolio_summary(
    context: dict[str, Any],
    asset_detail: dict[str, Any],
) -> dict[str, Any]:
    theme_returns = context["calculation_inputs"]["theme_benchmark_return_inputs"]
    period_returns = context["period_returns"]
    asset_totals = asset_detail["portfolio_level_totals"]

    global_benchmark_return = _round_return(theme_returns["global_benchmark_return"])
    policy_theme_benchmark_return = _round_return(
        theme_returns["policy_or_equal_weight_theme_benchmark_return"]
    )
    actual_weight_theme_benchmark_return = _round_return(
        theme_returns["actual_weight_theme_benchmark_return"]
    )
    actual_portfolio_theme_return = _round_return(
        theme_returns["actual_portfolio_theme_return"]
    )
    actual_portfolio_return = _round_return(
        period_returns["portfolio_return"]["period_return"]
    )

    theme_benchmark_selection_effect = _round_return(
        policy_theme_benchmark_return - global_benchmark_return
    )
    theme_benchmark_sizing_effect = _round_return(
        actual_weight_theme_benchmark_return - policy_theme_benchmark_return
    )
    asset_selection_effect = _round_return(asset_totals["asset_selection_effect"])
    asset_sizing_effect = _round_return(asset_totals["asset_sizing_effect"])
    asset_total_from_returns = _round_return(
        actual_portfolio_theme_return - actual_weight_theme_benchmark_return
    )
    asset_total_from_assets = _round_return(
        asset_selection_effect + asset_sizing_effect
    )
    asset_difference = _round_return(asset_total_from_returns - asset_total_from_assets)

    relative_return = _round_return(actual_portfolio_return - global_benchmark_return)
    residual_unexplained = _round_return(
        relative_return
        - theme_benchmark_selection_effect
        - theme_benchmark_sizing_effect
        - asset_selection_effect
        - asset_sizing_effect
    )
    recomputed_actual_return = _round_return(
        global_benchmark_return
        + theme_benchmark_selection_effect
        + theme_benchmark_sizing_effect
        + asset_selection_effect
        + asset_sizing_effect
        + residual_unexplained
    )
    tie_out_difference = _round_return(actual_portfolio_return - recomputed_actual_return)

    return {
        "schema_version": "whole_portfolio_calculated_attribution_summary.v1",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_calculated",
        "period_start": context["period_start"],
        "period_end": context["period_end"],
        "selected_attribution_lens": context["selected_attribution_lens"],
        "global_benchmark_return": global_benchmark_return,
        "policy_or_equal_weight_theme_benchmark_return": policy_theme_benchmark_return,
        "actual_weight_theme_benchmark_return": actual_weight_theme_benchmark_return,
        "actual_portfolio_theme_return": actual_portfolio_theme_return,
        "actual_portfolio_return": actual_portfolio_return,
        "relative_return": relative_return,
        "theme_benchmark_selection_effect": theme_benchmark_selection_effect,
        "theme_benchmark_sizing_effect": theme_benchmark_sizing_effect,
        "asset_selection_effect": asset_selection_effect,
        "asset_sizing_effect": asset_sizing_effect,
        "residual_unexplained": residual_unexplained,
        "timing_status": "unavailable",
        "tie_out_status": (
            "ties_to_actual_portfolio_return"
            if abs(tie_out_difference) <= TIE_OUT_TOLERANCE
            else "does_not_tie_to_actual_portfolio_return"
        ),
        "tie_out_difference": tie_out_difference,
        "tie_out": {
            "global_benchmark_return": global_benchmark_return,
            "effect_total": _round_return(
                theme_benchmark_selection_effect
                + theme_benchmark_sizing_effect
                + asset_selection_effect
                + asset_sizing_effect
                + residual_unexplained
            ),
            "actual_portfolio_return": actual_portfolio_return,
            "recomputed_actual_portfolio_return": recomputed_actual_return,
            "difference": tie_out_difference,
            "ties_to_actual_portfolio_return": abs(tie_out_difference)
            <= TIE_OUT_TOLERANCE,
            "timing_used_as_residual": False,
        },
        "asset_effect_reconciliation": {
            "asset_total_from_theme_return_inputs": asset_total_from_returns,
            "asset_total_from_asset_detail": asset_total_from_assets,
            "difference": asset_difference,
            "used_asset_detail_effects": abs(asset_difference) <= TIE_OUT_TOLERANCE,
        },
        "effect_provenance": {
            "theme_benchmark_selection_effect": "calculated_from_policy_theme_benchmark_return_minus_global_benchmark_return",
            "theme_benchmark_sizing_effect": "calculated_from_actual_weight_theme_benchmark_return_minus_policy_theme_benchmark_return",
            "asset_selection_effect": "calculated_from_per_theme_reference_weight_asset_returns",
            "asset_sizing_effect": "calculated_from_per_theme_actual_weight_asset_returns",
            "residual_unexplained": "calculated_reconciler_after_visible_effects",
        },
        "caveats": [
            "Synthetic local-demo calculated attribution output only.",
            "Residual / unexplained is a reconciler and is not labeled as timing.",
            "Timing remains unavailable because clean trade, holding, price, and flow history is not included.",
        ],
        "source_metadata": _source_metadata("whole_portfolio_calculated_attribution"),
    }


def build_theme_benchmark_calculated_detail(
    context: dict[str, Any],
    asset_detail: dict[str, Any],
) -> dict[str, Any]:
    theme_returns = context["calculation_inputs"]["theme_benchmark_return_inputs"]
    asset_by_bucket = {
        row["bucket_id"]: row for row in asset_detail["buckets"]
    }
    global_benchmark_return = _round_return(theme_returns["global_benchmark_return"])

    selection_values = [
        float(row["policy_or_equal_weight"])
        * (float(row["theme_benchmark_return"]) - global_benchmark_return)
        for row in theme_returns["rows"]
    ]
    sizing_values = [
        (
            float(row["actual_portfolio_weight"])
            - float(row["policy_or_equal_weight"])
        )
        * float(row["theme_benchmark_return"])
        for row in theme_returns["rows"]
    ]
    asset_selection_values = [
        asset_by_bucket[row["bucket_id"]]["bucket_level_totals"][
            "asset_selection_effect"
        ]
        for row in theme_returns["rows"]
    ]
    asset_sizing_values = [
        asset_by_bucket[row["bucket_id"]]["bucket_level_totals"][
            "asset_sizing_effect"
        ]
        for row in theme_returns["rows"]
    ]

    selection_effects = _round_values_preserve_sum(
        selection_values,
        theme_returns["theme_benchmark_selection_effect_input"],
    )
    sizing_effects = _round_values_preserve_sum(
        sizing_values,
        theme_returns["theme_benchmark_sizing_effect_input"],
    )
    asset_selection_effects = _round_values_preserve_sum(
        asset_selection_values,
        asset_detail["portfolio_level_totals"]["asset_selection_effect"],
    )
    asset_sizing_effects = _round_values_preserve_sum(
        asset_sizing_values,
        asset_detail["portfolio_level_totals"]["asset_sizing_effect"],
    )

    rows = []
    for index, source_row in enumerate(theme_returns["rows"]):
        bucket_id = source_row["bucket_id"]
        asset_bucket = asset_by_bucket[bucket_id]
        total_effect = _round_return(
            selection_effects[index]
            + sizing_effects[index]
            + asset_selection_effects[index]
            + asset_sizing_effects[index]
        )
        rows.append(
            {
                "bucket_id": bucket_id,
                "bucket_display_name": source_row["bucket_display_name"],
                "actual_portfolio_weight": source_row["actual_portfolio_weight"],
                "policy_or_equal_weight": source_row["policy_or_equal_weight"],
                "theme_benchmark_return": source_row["theme_benchmark_return"],
                "actual_portfolio_theme_return": source_row[
                    "actual_portfolio_theme_return"
                ],
                "theme_benchmark_selection_effect": selection_effects[index],
                "theme_benchmark_sizing_effect": sizing_effects[index],
                "asset_selection_effect": asset_selection_effects[index],
                "asset_sizing_effect": asset_sizing_effects[index],
                "total_effect": total_effect,
                "residual_unexplained": 0.0,
                "contribution_to_portfolio_relative_return": total_effect,
                "theme_bucket_asset_total_effect": asset_bucket[
                    "bucket_level_totals"
                ]["total_asset_effect"],
                "component_status": "calculated_from_synthetic_inputs",
                "caveats": [
                    "Synthetic theme benchmark and compact asset inputs only.",
                    "This row is a calculated output for future report generation, not a report row yet.",
                ],
            }
        )

    totals = {
        "theme_benchmark_selection_effect": _round_return(
            sum(row["theme_benchmark_selection_effect"] for row in rows)
        ),
        "theme_benchmark_sizing_effect": _round_return(
            sum(row["theme_benchmark_sizing_effect"] for row in rows)
        ),
        "asset_selection_effect": _round_return(
            sum(row["asset_selection_effect"] for row in rows)
        ),
        "asset_sizing_effect": _round_return(
            sum(row["asset_sizing_effect"] for row in rows)
        ),
        "residual_unexplained": _round_return(
            sum(row["residual_unexplained"] for row in rows)
        ),
    }
    totals["total_effect"] = _round_return(sum(totals.values()))

    return {
        "schema_version": "theme_benchmark_calculated_detail.v1",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_calculated",
        "period_start": context["period_start"],
        "period_end": context["period_end"],
        "selected_attribution_lens": context["selected_attribution_lens"],
        "detail_basis": "calculated_theme_benchmark_and_asset_effects",
        "rows": rows,
        "totals": totals,
        "tie_out_status": {
            "ties_to_summary_calculated_effects": True,
            "theme_benchmark_selection_difference": _round_return(
                theme_returns["theme_benchmark_selection_effect_input"]
                - totals["theme_benchmark_selection_effect"]
            ),
            "theme_benchmark_sizing_difference": _round_return(
                theme_returns["theme_benchmark_sizing_effect_input"]
                - totals["theme_benchmark_sizing_effect"]
            ),
            "asset_selection_difference": _round_return(
                asset_detail["portfolio_level_totals"]["asset_selection_effect"]
                - totals["asset_selection_effect"]
            ),
            "asset_sizing_difference": _round_return(
                asset_detail["portfolio_level_totals"]["asset_sizing_effect"]
                - totals["asset_sizing_effect"]
            ),
            "timing_used_as_residual": False,
        },
        "timing_status": "unavailable",
        "source_metadata": _source_metadata("theme_benchmark_calculated_detail"),
    }


def build_theme_asset_calculated_detail(context: dict[str, Any]) -> dict[str, Any]:
    asset_inputs = context["calculation_inputs"]["theme_asset_calculation_inputs"]
    buckets = []
    for bucket in asset_inputs["buckets"]:
        actual_portfolio_weight = float(bucket["actual_portfolio_weight"])
        theme_benchmark_return = float(bucket["theme_benchmark_return"])
        assets = []
        for asset in bucket["assets"]:
            actual_weight = float(asset["actual_asset_weight_within_bucket"])
            reference_weight = float(asset["reference_asset_weight_within_bucket"])
            asset_return = float(asset["asset_return"])
            actual_contribution = _round_return(actual_weight * asset_return)
            reference_contribution = _round_return(reference_weight * asset_return)
            asset_selection_effect = _round_return(
                actual_portfolio_weight
                * reference_weight
                * (asset_return - theme_benchmark_return)
            )
            asset_sizing_effect = _round_return(
                actual_portfolio_weight
                * (actual_weight - reference_weight)
                * asset_return
            )
            assets.append(
                {
                    "synthetic_asset_id": asset["synthetic_asset_id"],
                    "display_name": asset["display_name"],
                    "position_ids": list(asset["position_ids"]),
                    "actual_asset_weight_within_bucket": asset[
                        "actual_asset_weight_within_bucket"
                    ],
                    "reference_asset_weight_within_bucket": asset[
                        "reference_asset_weight_within_bucket"
                    ],
                    "asset_return": asset["asset_return"],
                    "reference_return": asset["reference_return"],
                    "benchmark_component_return": asset["benchmark_component_return"],
                    "actual_weight_asset_contribution_within_bucket": actual_contribution,
                    "reference_weight_asset_contribution_within_bucket": reference_contribution,
                    "actual_weight_asset_contribution_to_portfolio": _round_return(
                        actual_portfolio_weight * actual_contribution
                    ),
                    "reference_weight_asset_contribution_to_portfolio": _round_return(
                        actual_portfolio_weight * reference_contribution
                    ),
                    "asset_selection_effect": asset_selection_effect,
                    "asset_sizing_effect": asset_sizing_effect,
                    "total_asset_effect": _round_return(
                        asset_selection_effect + asset_sizing_effect
                    ),
                    "source_metadata": asset["source_metadata"],
                }
            )

        input_totals = bucket["bucket_level_totals"]
        bucket_selection = _round_return(
            sum(row["asset_selection_effect"] for row in assets)
        )
        bucket_sizing = _round_return(
            sum(row["asset_sizing_effect"] for row in assets)
        )
        input_selection = _round_return(input_totals["asset_selection_effect_input"])
        input_sizing = _round_return(input_totals["asset_sizing_effect_input"])
        selection_difference = _round_return(input_selection - bucket_selection)
        sizing_difference = _round_return(input_sizing - bucket_sizing)
        if assets:
            if abs(selection_difference) <= ASSET_DISTRIBUTION_ROUNDING_TOLERANCE:
                assets[-1]["asset_selection_effect"] = _round_return(
                    assets[-1]["asset_selection_effect"] + selection_difference
                )
                bucket_selection = _round_return(
                    sum(row["asset_selection_effect"] for row in assets)
                )
            if abs(sizing_difference) <= ASSET_DISTRIBUTION_ROUNDING_TOLERANCE:
                assets[-1]["asset_sizing_effect"] = _round_return(
                    assets[-1]["asset_sizing_effect"] + sizing_difference
                )
                bucket_sizing = _round_return(
                    sum(row["asset_sizing_effect"] for row in assets)
                )
            assets[-1]["total_asset_effect"] = _round_return(
                assets[-1]["asset_selection_effect"] + assets[-1]["asset_sizing_effect"]
            )

        bucket_total = _round_return(bucket_selection + bucket_sizing)
        input_total = _round_return(input_totals["asset_total_effect_input"])
        difference = _round_return(input_total - bucket_total)
        if assets and abs(difference) <= ASSET_DISTRIBUTION_ROUNDING_TOLERANCE:
            assets[-1]["asset_sizing_effect"] = _round_return(
                assets[-1]["asset_sizing_effect"] + difference
            )
            assets[-1]["total_asset_effect"] = _round_return(
                assets[-1]["asset_selection_effect"] + assets[-1]["asset_sizing_effect"]
            )
            bucket_sizing = _round_return(
                sum(row["asset_sizing_effect"] for row in assets)
            )
            bucket_total = _round_return(bucket_selection + bucket_sizing)

        bucket_difference = _round_return(input_total - bucket_total)
        buckets.append(
            {
                "bucket_id": bucket["bucket_id"],
                "bucket_display_name": bucket["bucket_display_name"],
                "actual_portfolio_weight": bucket["actual_portfolio_weight"],
                "theme_benchmark_return": bucket["theme_benchmark_return"],
                "assets": assets,
                "bucket_level_totals": {
                    "actual_asset_weight_sum": input_totals[
                        "actual_asset_weight_sum"
                    ],
                    "reference_asset_weight_sum": input_totals[
                        "reference_asset_weight_sum"
                    ],
                    "actual_weight_asset_return": input_totals[
                        "actual_weight_asset_return"
                    ],
                    "reference_weight_asset_return": input_totals[
                        "reference_weight_asset_return"
                    ],
                    "actual_weight_asset_contribution": _round_return(
                        sum(
                            row["actual_weight_asset_contribution_within_bucket"]
                            for row in assets
                        )
                    ),
                    "reference_weight_asset_contribution": _round_return(
                        sum(
                            row["reference_weight_asset_contribution_within_bucket"]
                            for row in assets
                        )
                    ),
                    "asset_selection_effect": bucket_selection,
                    "asset_sizing_effect": bucket_sizing,
                    "total_asset_effect": bucket_total,
                    "input_total_asset_effect": input_total,
                    "tie_out_difference": bucket_difference,
                    "ties_to_input_total_asset_effect": abs(bucket_difference)
                    <= TIE_OUT_TOLERANCE,
                },
                "caveats": list(input_totals["caveats"]),
            }
        )

    portfolio_totals = {
        "asset_selection_effect": _round_return(
            sum(row["bucket_level_totals"]["asset_selection_effect"] for row in buckets)
        ),
        "asset_sizing_effect": _round_return(
            sum(row["bucket_level_totals"]["asset_sizing_effect"] for row in buckets)
        ),
    }
    portfolio_totals["total_asset_effect"] = _round_return(
        portfolio_totals["asset_selection_effect"]
        + portfolio_totals["asset_sizing_effect"]
    )
    portfolio_totals["max_bucket_tie_out_difference"] = _max_abs(
        row["bucket_level_totals"]["tie_out_difference"] for row in buckets
    )
    portfolio_totals["all_bucket_tie_outs_pass"] = all(
        row["bucket_level_totals"]["ties_to_input_total_asset_effect"]
        for row in buckets
    )

    return {
        "schema_version": "theme_asset_calculated_attribution_detail.v1",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_calculated",
        "period_start": context["period_start"],
        "period_end": context["period_end"],
        "selected_attribution_lens": context["selected_attribution_lens"],
        "asset_detail_basis": "compact_grouped_synthetic_assets_from_calculation_inputs",
        "buckets": buckets,
        "portfolio_level_totals": portfolio_totals,
        "timing_status": "unavailable",
        "source_metadata": _source_metadata("theme_asset_calculated_attribution_detail"),
    }


def build_manager_calculated_summary(context: dict[str, Any]) -> dict[str, Any]:
    manager_inputs = context["calculation_inputs"]["manager_calculated_attribution_inputs"]
    theme_returns = context["calculation_inputs"]["theme_benchmark_return_inputs"]
    asset_inputs = context["calculation_inputs"]["theme_asset_calculation_inputs"]

    policy_theme_benchmark_return = float(
        theme_returns["policy_or_equal_weight_theme_benchmark_return"]
    )
    asset_totals_by_bucket = {
        row["bucket_id"]: row["bucket_level_totals"] for row in asset_inputs["buckets"]
    }
    theme_return_by_bucket = {row["bucket_id"]: row for row in theme_returns["rows"]}

    managers = []
    for manager in manager_inputs["managers"]:
        relative_return = _round_return(
            float(manager["manager_return"])
            - float(manager["manager_benchmark_return"])
        )
        theme_benchmark_selection = _round_return(
            policy_theme_benchmark_return - float(manager["manager_benchmark_return"])
        )
        theme_benchmark_sizing = _round_return(
            float(manager["manager_theme_benchmark_blend_return"])
            - policy_theme_benchmark_return
        )
        asset_selection = _round_return(
            sum(
                float(weight["weight"])
                * (
                    float(
                        asset_totals_by_bucket[weight["bucket_id"]][
                            "reference_weight_asset_return"
                        ]
                    )
                    - float(
                        theme_return_by_bucket[weight["bucket_id"]][
                            "theme_benchmark_return"
                        ]
                    )
                )
                for weight in manager["manager_theme_weights"]
            )
        )
        asset_sizing = _round_return(
            sum(
                float(weight["weight"])
                * (
                    float(
                        asset_totals_by_bucket[weight["bucket_id"]][
                            "actual_weight_asset_return"
                        ]
                    )
                    - float(
                        asset_totals_by_bucket[weight["bucket_id"]][
                            "reference_weight_asset_return"
                        ]
                    )
                )
                for weight in manager["manager_theme_weights"]
            )
        )
        residual = _round_return(
            relative_return
            - theme_benchmark_selection
            - theme_benchmark_sizing
            - asset_selection
            - asset_sizing
        )
        recomputed_relative = _round_return(
            theme_benchmark_selection
            + theme_benchmark_sizing
            + asset_selection
            + asset_sizing
            + residual
        )
        tie_out_difference = _round_return(relative_return - recomputed_relative)
        effects = {
            "Theme benchmark selection": theme_benchmark_selection,
            "Theme benchmark sizing": theme_benchmark_sizing,
            "Asset selection": asset_selection,
            "Asset sizing": asset_sizing,
            "Residual / unexplained": residual,
        }
        largest_driver_label, largest_driver_value = max(
            effects.items(),
            key=lambda item: abs(item[1]),
        )
        managers.append(
            {
                "manager_id": manager["manager_id"],
                "display_name": manager["display_name"],
                "manager_return": manager["manager_return"],
                "manager_benchmark_basis_type": manager[
                    "manager_benchmark_basis_type"
                ],
                "benchmark_basis_description": manager[
                    "benchmark_basis_description"
                ],
                "manager_benchmark_return": manager["manager_benchmark_return"],
                "relative_return": relative_return,
                "theme_benchmark_selection_effect": theme_benchmark_selection,
                "theme_benchmark_sizing_effect": theme_benchmark_sizing,
                "asset_selection_effect": asset_selection,
                "asset_sizing_effect": asset_sizing,
                "residual_unexplained": residual,
                "timing_status": "unavailable",
                "timing_used_as_residual": False,
                "tie_out_status": (
                    "ties_to_manager_relative_return"
                    if abs(tie_out_difference) <= TIE_OUT_TOLERANCE
                    else "does_not_tie_to_manager_relative_return"
                ),
                "tie_out_difference": tie_out_difference,
                "largest_driver": {
                    "label": largest_driver_label,
                    "value": largest_driver_value,
                },
                "manager_benchmark_components": manager[
                    "manager_benchmark_components"
                ],
                "caveats": [
                    "Synthetic demo manager calculated attribution output only.",
                    "Residual / unexplained is not labeled as timing.",
                ],
                "source_metadata": manager["source_metadata"],
            }
        )

    manager_tie_differences = [row["tie_out_difference"] for row in managers]
    return {
        "schema_version": "manager_calculated_attribution_summary.v1",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_calculated",
        "period_start": context["period_start"],
        "period_end": context["period_end"],
        "selected_attribution_lens": context["selected_attribution_lens"],
        "manager_count": len(managers),
        "managers": managers,
        "coverage_summary": {
            "all_current_managers_covered": True,
            "manager_count": len(managers),
            "all_manager_benchmark_basis_types_explicit": True,
            "manager_tie_outs_reconcile": all(
                abs(value) <= TIE_OUT_TOLERANCE for value in manager_tie_differences
            ),
            "max_manager_tie_out_difference": _max_abs(manager_tie_differences),
        },
        "timing_status": "unavailable",
        "source_metadata": _source_metadata("manager_calculated_attribution_summary"),
    }


def build_quality_summary(
    context: dict[str, Any],
    outputs: dict[str, Any],
) -> dict[str, Any]:
    whole = outputs["whole_portfolio_summary"]
    theme_detail = outputs["theme_benchmark_detail"]
    asset_detail = outputs["theme_asset_detail"]
    managers = outputs["manager_summary"]

    tie_differences = [
        whole["tie_out_difference"],
        theme_detail["tie_out_status"]["theme_benchmark_selection_difference"],
        theme_detail["tie_out_status"]["theme_benchmark_sizing_difference"],
        theme_detail["tie_out_status"]["asset_selection_difference"],
        theme_detail["tie_out_status"]["asset_sizing_difference"],
        asset_detail["portfolio_level_totals"]["max_bucket_tie_out_difference"],
        managers["coverage_summary"]["max_manager_tie_out_difference"],
    ]
    residual_size = abs(float(whole["residual_unexplained"]))

    return {
        "schema_version": "calculated_attribution_quality_summary.v1",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "approval_status": "synthetic_demo_calculated",
        "period_start": context["period_start"],
        "period_end": context["period_end"],
        "selected_attribution_lens": context["selected_attribution_lens"],
        "whole_portfolio_tie_out_status": whole["tie_out_status"],
        "theme_detail_tie_out_status": (
            "ties_to_summary_calculated_effects"
            if _all_tie_differences_pass(
                [
                    theme_detail["tie_out_status"][
                        "theme_benchmark_selection_difference"
                    ],
                    theme_detail["tie_out_status"][
                        "theme_benchmark_sizing_difference"
                    ],
                    theme_detail["tie_out_status"]["asset_selection_difference"],
                    theme_detail["tie_out_status"]["asset_sizing_difference"],
                ]
            )
            else "does_not_tie_to_summary_calculated_effects"
        ),
        "asset_detail_tie_out_status": (
            "all_bucket_tie_outs_pass"
            if asset_detail["portfolio_level_totals"]["all_bucket_tie_outs_pass"]
            else "asset_bucket_tie_outs_need_review"
        ),
        "manager_tie_out_status": (
            "all_manager_tie_outs_pass"
            if managers["coverage_summary"]["manager_tie_outs_reconcile"]
            else "manager_tie_outs_need_review"
        ),
        "max_tie_out_difference": _max_abs(tie_differences),
        "residual_size": _round_return(residual_size),
        "residual_review_threshold": RESIDUAL_REVIEW_THRESHOLD,
        "residual_threshold_status": (
            "within_synthetic_demo_review_threshold"
            if residual_size <= RESIDUAL_REVIEW_THRESHOLD
            else "exceeds_synthetic_demo_review_threshold"
        ),
        "timing_status": "unavailable",
        "future_report_mockups_ready_from_calculated_outputs": [
            "integrated_performance_attribution_summary",
            "integrated_performance_attribution_detail",
            "manager_attribution_summary",
            "lens_based_performance_attribution_ai_adoption",
        ],
        "future_reports_still_gated": [
            "timing_attribution",
            "production_attribution_report",
            "scenario_versus_benchmark",
            "probabilistic_scenario_range",
            "current_versus_proposed_attribution",
        ],
        "report_readiness": {
            "integrated_performance_attribution_summary": "ready_from_calculated_outputs",
            "integrated_performance_attribution_detail": "ready_from_calculated_theme_detail",
            "manager_attribution_summary": "ready_from_calculated_manager_outputs",
            "lens_based_performance_attribution": "ready_from_calculated_theme_detail",
            "timing_attribution": "unavailable",
            "production_attribution": "gated",
        },
        "summary_ready_from_calculated_outputs": True,
        "detail_ready_from_calculated_outputs": True,
        "manager_ready_from_calculated_outputs": True,
        "residual_policy": whole["tie_out"],
        "source_metadata": _source_metadata("calculated_attribution_quality_summary"),
    }


def build_manifest(context: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "calculated_attribution_engine_manifest.v1",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "generated_by": "python -m arangur.analytics.calculated_synthetic_attribution",
        "generator_version": GENERATOR_VERSION,
        "synthetic_data": True,
        "local_only": True,
        "source_prerequisite_pack_id": SOURCE_PREREQUISITE_PACK_ID,
        "source_calculation_pack_id": SOURCE_CALCULATION_PACK_ID,
        "source_calculation_inputs_path": context["source_paths"][
            "calculation_input_dir"
        ],
        "selected_attribution_lens": context["selected_attribution_lens"],
        "period_start": context["period_start"],
        "period_end": context["period_end"],
        "included_artifacts": list(ARTIFACT_FILES.values()),
        "methodology": {
            "whole_portfolio": (
                "Global benchmark -> policy theme benchmark -> actual-weight theme "
                "benchmark -> asset effects -> residual / unexplained -> actual portfolio."
            ),
            "theme_benchmark_selection_effect": "P - G",
            "theme_benchmark_sizing_effect": "A - P",
            "asset_selection_effect": (
                "sum_i(actual_theme_weight_i * (reference_weight_asset_return_i - theme_benchmark_return_i))"
            ),
            "asset_sizing_effect": (
                "sum_i(actual_theme_weight_i * (actual_weight_asset_return_i - reference_weight_asset_return_i))"
            ),
            "manager_effects": (
                "Manager relative return decomposed using explicit manager benchmark basis, "
                "selected-lens theme weights, per-theme asset inputs, and residual."
            ),
        },
        "timing_status": "unavailable",
        "residual_policy": {
            "policy": "explicit_reconciler_after_calculated_effects",
            "tolerance": TIE_OUT_TOLERANCE,
            "timing_used_as_residual": False,
        },
        "limitations": [
            "Synthetic calculated attribution outputs only.",
            "No attribution report mockups are regenerated by this tranche.",
            "No advisor UI or generated-report wiring is changed by this tranche.",
            "Timing remains unavailable and is not used as residual noise.",
        ],
        "approval_status": "synthetic_demo_calculated",
        "quality_summary": {
            "summary_ready_from_calculated_outputs": outputs["quality_summary"][
                "summary_ready_from_calculated_outputs"
            ],
            "detail_ready_from_calculated_outputs": outputs["quality_summary"][
                "detail_ready_from_calculated_outputs"
            ],
            "manager_ready_from_calculated_outputs": outputs["quality_summary"][
                "manager_ready_from_calculated_outputs"
            ],
        },
    }


def validate_calculated_outputs(
    context: dict[str, Any],
    outputs: dict[str, Any],
) -> None:
    manifest = outputs["manifest"]
    if not manifest["synthetic_data"] or not manifest["local_only"]:
        raise ValueError("Calculated attribution manifest must be local synthetic")
    if manifest["approval_status"] != "synthetic_demo_calculated":
        raise ValueError("Calculated attribution outputs must be synthetic-demo calculated")

    whole = outputs["whole_portfolio_summary"]
    if whole["timing_status"] != "unavailable":
        raise ValueError("Timing must remain unavailable")
    if whole["tie_out"]["timing_used_as_residual"]:
        raise ValueError("Timing must not be used as residual")
    if not whole["tie_out"]["ties_to_actual_portfolio_return"]:
        raise ValueError("Whole-portfolio calculated attribution does not tie out")

    theme_detail = outputs["theme_benchmark_detail"]
    expected_bucket_ids = set(context["bucket_order"])
    actual_bucket_ids = {row["bucket_id"] for row in theme_detail["rows"]}
    if expected_bucket_ids != actual_bucket_ids:
        raise ValueError("Theme detail does not cover every selected lens bucket")
    if not _all_tie_differences_pass(
        [
            theme_detail["tie_out_status"]["theme_benchmark_selection_difference"],
            theme_detail["tie_out_status"]["theme_benchmark_sizing_difference"],
            theme_detail["tie_out_status"]["asset_selection_difference"],
            theme_detail["tie_out_status"]["asset_sizing_difference"],
        ]
    ):
        raise ValueError("Theme detail does not reconcile to summary effects")

    asset_detail = outputs["theme_asset_detail"]
    for bucket in asset_detail["buckets"]:
        totals = bucket["bucket_level_totals"]
        if abs(totals["actual_asset_weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
            raise ValueError(f"Actual asset weights do not sum to 1 for {bucket['bucket_id']}")
        if abs(totals["reference_asset_weight_sum"] - 1.0) > TIE_OUT_TOLERANCE:
            raise ValueError(f"Reference asset weights do not sum to 1 for {bucket['bucket_id']}")
        if not totals["ties_to_input_total_asset_effect"]:
            raise ValueError(f"Asset detail does not tie out for {bucket['bucket_id']}")

    manager_summary = outputs["manager_summary"]
    if manager_summary["manager_count"] != 6:
        raise ValueError("Manager calculated summary must cover all six current managers")
    if not manager_summary["coverage_summary"]["manager_tie_outs_reconcile"]:
        raise ValueError("Manager calculated summary does not tie out")
    if any(row["timing_status"] != "unavailable" for row in manager_summary["managers"]):
        raise ValueError("Manager timing status must remain unavailable")

    quality = outputs["quality_summary"]
    if quality["timing_status"] != "unavailable":
        raise ValueError("Quality summary must keep timing unavailable")
    if not quality["summary_ready_from_calculated_outputs"]:
        raise ValueError("Summary should be ready from calculated outputs")
    if not quality["detail_ready_from_calculated_outputs"]:
        raise ValueError("Detail should be ready from calculated outputs")
    if not quality["manager_ready_from_calculated_outputs"]:
        raise ValueError("Manager summary should be ready from calculated outputs")


def _all_tie_differences_pass(values: list[float]) -> bool:
    return all(abs(float(value)) <= TIE_OUT_TOLERANCE for value in values)


def _round_values_preserve_sum(values: list[float], target: float) -> list[float]:
    if not values:
        raise ValueError("Cannot round an empty value set")
    rounded = [_round_return(value) for value in values]
    difference = _round_return(float(target) - sum(rounded))
    if difference:
        index = max(range(len(rounded)), key=lambda item: abs(values[item]))
        rounded[index] = _round_return(rounded[index] + difference)
    return rounded


def _source_metadata(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "synthetic_data": True,
        "local_only": True,
        "external_data_used": False,
        "live_market_data_used": False,
        "real_client_data_used": False,
    }


def _max_abs(values: Any) -> float:
    materialized = [abs(float(value)) for value in values]
    if not materialized:
        return 0.0
    return _round_return(max(materialized))


def _round_return(value: Any) -> float:
    return round(float(value), 6)


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


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
        description="Generate calculated synthetic attribution outputs."
    )
    parser.add_argument(
        "--calculation-input-dir",
        default=str(DEFAULT_CALCULATION_INPUT_DIR),
    )
    parser.add_argument(
        "--source-prerequisite-dir",
        default=str(DEFAULT_SOURCE_PREREQUISITE_DIR),
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outputs = generate_calculated_synthetic_attribution(
        calculation_input_dir=args.calculation_input_dir,
        source_prerequisite_dir=args.source_prerequisite_dir,
        output_dir=args.output_dir,
    )
    whole = outputs["whole_portfolio_summary"]
    quality = outputs["quality_summary"]
    managers = outputs["manager_summary"]

    print(f"Calculated synthetic attribution engine: {ENGINE_ID} -> {args.output_dir}")
    print(f"Selected lens: {whole['selected_attribution_lens']['display_name']}")
    print(f"Global benchmark return: {whole['global_benchmark_return']:.6f}")
    print(f"Actual portfolio return: {whole['actual_portfolio_return']:.6f}")
    print(f"Relative return: {whole['relative_return']:.6f}")
    print(
        "Calculated selection/sizing totals: "
        f"{whole['theme_benchmark_selection_effect']:.6f}, "
        f"{whole['theme_benchmark_sizing_effect']:.6f}, "
        f"{whole['asset_selection_effect']:.6f}, "
        f"{whole['asset_sizing_effect']:.6f}"
    )
    print(f"Residual / unexplained: {whole['residual_unexplained']:.6f}")
    print(f"Manager count: {managers['manager_count']}")
    print(f"Timing status: {quality['timing_status']}")
    print(f"Output path: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
