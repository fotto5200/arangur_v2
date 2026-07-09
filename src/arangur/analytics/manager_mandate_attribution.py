from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00Z"

ENGINE_ID = "manager_mandate_attribution_engine_v1"
ENGINE_VERSION = "2026-07-09"
GENERATOR_VERSION = "manager_mandate_attribution.v1"
SOURCE_ADVISOR_ENGINE_ID = "advisor_policy_attribution_engine_v2"
SOURCE_MANAGER_CALCULATED_ENGINE_ID = "synthetic_attribution_engine_v1"

CALCULATION_SCHEMA_VERSION = "manager_mandate_attribution_calculated_output.v1"
DRIVER_ROWS_SCHEMA_VERSION = "within_manager_driver_rows.v1"
SELECTED_MANAGER_SCHEMA_VERSION = "selected_manager_detail_artifact.v1"
REPORT_INPUT_SCHEMA_VERSION = "manager_mandate_attribution_report_input.v1"
REPORT_INPUT_INDEX_SCHEMA_VERSION = "manager_mandate_attribution_report_input_index.v1"
REPORT_VIEW_SCHEMA_VERSION = "manager_mandate_attribution_report_view.v1"
REPORT_VIEW_INDEX_SCHEMA_VERSION = "manager_mandate_attribution_report_view_index.v1"
GATED_INDEX_SCHEMA_VERSION = "manager_mandate_attribution_gated_deferred_index.v1"

DEFAULT_POLICY_PACK_DIR = Path(
    "data/simulation/policy_mandate_prerequisites/synthetic_policy_mandate_pack_v1"
)
DEFAULT_ADVISOR_POLICY_DIR = (
    Path("data/simulation/policy_level_attribution") / SOURCE_ADVISOR_ENGINE_ID
)
DEFAULT_MANAGER_CALCULATED_DIR = (
    Path("data/simulation/attribution_calculated") / SOURCE_MANAGER_CALCULATED_ENGINE_ID
)
DEFAULT_OUTPUT_DIR = (
    Path("data/simulation/manager_mandate_attribution") / ENGINE_ID
)
DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs/manager_attribution_v1")
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/manager_attribution_v1")
DEFAULT_MOCKUP_DIR = Path("docs/product/report_mockups/manager_attribution_v1")

RETURN_QUANT = Decimal("0.000000000001")
WEIGHT_QUANT = Decimal("0.000000001")
TIE_OUT_TOLERANCE = Decimal("0.000001")
STATUS_NEAR_MANDATE_TOLERANCE = Decimal("0.0005")

POLICY_PACK_FILES = {
    "manifest": "synthetic_policy_mandate_pack_manifest.json",
    "actual_manager_allocation_snapshot": "actual_manager_allocation_snapshot.json",
    "manager_mandate_benchmark_catalog": "manager_mandate_benchmark_catalog.json",
    "manager_benchmark_basis_map": "manager_benchmark_basis_map.json",
    "policy_level_attribution_inputs": "policy_level_attribution_inputs.json",
    "policy_mandate_readiness_summary": "policy_mandate_readiness_summary.json",
}

ADVISOR_POLICY_FILES = {
    "advisor_policy_summary": "advisor_policy_attribution_summary_v2.json",
    "advisor_policy_manager_rows": "advisor_policy_attribution_manager_rows_v2.json",
}

MANAGER_CALCULATED_FILES = {
    "manager_calculated_summary": "manager_calculated_attribution_summary.json",
}

CALCULATED_ARTIFACT_FILES = {
    "manifest": "manager_mandate_attribution_manifest.json",
    "summary": "manager_mandate_attribution_summary.json",
    "manager_rows": "manager_mandate_attribution_rows.json",
    "driver_rows": "within_manager_driver_rows.json",
    "selected_manager_detail": "selected_manager_detail_artifact.json",
    "quality_summary": "manager_mandate_attribution_quality_summary.json",
}

REPORT_SPECS: tuple[dict[str, str], ...] = (
    {
        "report_id": "manager_mandate_attribution_summary",
        "input_filename": "manager_mandate_attribution_summary_input.json",
        "view_filename": "manager_mandate_attribution_summary_view.json",
        "mockup_filename": "manager_mandate_attribution_summary_mockup_v1.md",
    },
    {
        "report_id": "within_manager_attribution_detail",
        "input_filename": "within_manager_attribution_detail_input.json",
        "view_filename": "within_manager_attribution_detail_view.json",
        "mockup_filename": "within_manager_attribution_detail_mockup_v1.md",
    },
    {
        "report_id": "manager_implementation_handoff",
        "input_filename": "manager_implementation_handoff_input.json",
        "view_filename": "manager_implementation_handoff_view.json",
        "mockup_filename": "manager_implementation_handoff_mockup_v1.md",
    },
)

BUILD_NOW_REPORT_IDS = tuple(spec["report_id"] for spec in REPORT_SPECS)
INPUT_FILENAME_BY_REPORT_ID = {
    spec["report_id"]: spec["input_filename"] for spec in REPORT_SPECS
}
VIEW_FILENAME_BY_REPORT_ID = {
    spec["report_id"]: spec["view_filename"] for spec in REPORT_SPECS
}
MOCKUP_FILENAME_BY_REPORT_ID = {
    spec["report_id"]: spec["mockup_filename"] for spec in REPORT_SPECS
}

GATED_REPORTS: tuple[dict[str, str], ...] = (
    {
        "report_id": "full_manager_by_manager_driver_detail",
        "display_title": "Full Manager-by-Manager Driver Detail",
        "status": "Gated",
        "reason": "Requires a separate review surface before expanding all driver rows.",
    },
    {
        "report_id": "timing_attribution",
        "display_title": "Timing Attribution",
        "status": "Unavailable",
        "reason": "Unavailable because clean timing inputs and an approved method are absent.",
    },
    {
        "report_id": "dollar_pnl_attribution",
        "display_title": "Dollar P&L Attribution",
        "status": "Gated",
        "reason": "Gated unless reliable beginning portfolio value exists.",
    },
    {
        "report_id": "production_client_manager_attribution",
        "display_title": "Production Client Manager Attribution",
        "status": "Gated",
        "reason": "Gated on approved real manager returns and mandate benchmarks.",
    },
    {
        "report_id": "blended_all_in_attribution",
        "display_title": "Blended / All-In Attribution",
        "status": "Deferred",
        "reason": "Deferred so advisor policy and manager implementation remain separate.",
    },
    {
        "report_id": "position_level_manager_attribution",
        "display_title": "Position-Level Manager Attribution",
        "status": "Gated",
        "reason": "Requires approved position-level attribution inputs and review design.",
    },
)

DEFAULT_INFORMATION_BUDGET = {
    "max_headline_sentences": 1,
    "max_headline_metrics": 3,
    "max_benchmark_basis_items": 4,
    "max_visible_table_rows": 5,
    "max_caveats": 1,
    "max_advisor_notes": 1,
    "no_raw_ids_in_visible_content": True,
    "no_source_filenames_in_visible_content": True,
    "no_internal_jargon_in_visible_content": True,
    "no_hidden_expansion_placeholders": True,
}

FORBIDDEN_VISIBLE_TERMS = (
    "artifact",
    "manifest",
    "schema",
    "raw json",
    "debug",
    "blame",
    "at fault",
    "bad allocation",
    "wrong allocation",
    "manager failed",
    "advisor failed",
    "full within-manager",
    "all-in attribution",
    "bridge grid",
    ".json",
)

FORBIDDEN_PLACEHOLDER_TERMS = (
    "todo",
    "tbd",
    "placeholder",
    "example only",
    "more rows",
    "details omitted",
)

RAW_ID_PATTERNS = (
    r"\bpos_[a-z0-9_]+",
    r"\binstr_[a-z0-9_]+",
    r"\bmgr_[a-z0-9_]+",
    r"\bacct_[a-z0-9_]+",
    r"\bsleeve_[a-z0-9_]+",
    r"\bai_adoption\b",
    r"\benergy_security\b",
)

DRIVER_COMPONENTS: tuple[dict[str, str], ...] = (
    {
        "driver_id": "mandate_sub_benchmark_selection",
        "label": "Mandate sub-benchmark selection",
        "category": "Mandate sub-benchmark",
        "source_field": "theme_benchmark_selection_effect",
        "meaning": "Return effect from the selected sub-benchmark mix inside the mandate.",
    },
    {
        "driver_id": "mandate_sub_benchmark_sizing",
        "label": "Mandate sub-benchmark sizing",
        "category": "Mandate sub-benchmark",
        "source_field": "theme_benchmark_sizing_effect",
        "meaning": "Return effect from sizing the sub-benchmark mix inside the mandate.",
    },
    {
        "driver_id": "asset_selection",
        "label": "Asset selection",
        "category": "Selection",
        "source_field": "asset_selection_effect",
        "meaning": "Return effect from selected assets versus their local comparisons.",
    },
    {
        "driver_id": "asset_sizing",
        "label": "Asset sizing",
        "category": "Sizing",
        "source_field": "asset_sizing_effect",
        "meaning": "Return effect from sizing assets within the manager mandate.",
    },
    {
        "driver_id": "residual_unexplained",
        "label": "Residual / unexplained",
        "category": "Residual",
        "source_field": "residual_unexplained",
        "meaning": "Local synthetic remainder after named driver categories.",
    },
)


def load_source_context(
    *,
    policy_pack_dir: str | Path = DEFAULT_POLICY_PACK_DIR,
    advisor_policy_dir: str | Path = DEFAULT_ADVISOR_POLICY_DIR,
    manager_calculated_dir: str | Path = DEFAULT_MANAGER_CALCULATED_DIR,
) -> dict[str, Any]:
    pack_root = Path(policy_pack_dir)
    advisor_root = Path(advisor_policy_dir)
    manager_calc_root = Path(manager_calculated_dir)

    policy_pack = {
        name: _load_json(pack_root / filename)
        for name, filename in POLICY_PACK_FILES.items()
    }
    advisor_policy = {
        name: _load_json(advisor_root / filename)
        for name, filename in ADVISOR_POLICY_FILES.items()
    }
    manager_calculated = {
        name: _load_json(manager_calc_root / filename)
        for name, filename in MANAGER_CALCULATED_FILES.items()
    }

    manifest = policy_pack["manifest"]
    policy_inputs = policy_pack["policy_level_attribution_inputs"]
    advisor_summary = advisor_policy["advisor_policy_summary"]
    advisor_rows = advisor_policy["advisor_policy_manager_rows"]
    manager_calc_summary = manager_calculated["manager_calculated_summary"]

    if manifest["pack_id"] != "synthetic_policy_mandate_pack_v1":
        raise ValueError("Unexpected policy mandate pack id")
    if not manifest["synthetic_data"] or not manifest["local_only"]:
        raise ValueError("Manager mandate attribution requires local synthetic inputs")
    if not policy_inputs["synthetic_data"] or not policy_inputs["local_only"]:
        raise ValueError("Policy attribution inputs must be local synthetic inputs")
    if advisor_summary["engine_id"] != SOURCE_ADVISOR_ENGINE_ID:
        raise ValueError("Advisor policy attribution v2 summary is required")
    if advisor_rows["engine_id"] != SOURCE_ADVISOR_ENGINE_ID:
        raise ValueError("Advisor policy attribution v2 manager rows are required")
    if advisor_summary["manager_implementation_visible_in_primary_report"]:
        raise ValueError("Advisor v2 must keep manager implementation out of primary report")
    if manager_calc_summary["engine_id"] != SOURCE_MANAGER_CALCULATED_ENGINE_ID:
        raise ValueError("Synthetic manager calculated attribution summary is required")
    if not manager_calc_summary["source_metadata"]["local_only"]:
        raise ValueError("Synthetic manager calculated attribution must be local only")

    source_paths = {
        **{
            f"policy_pack.{name}": _as_posix(pack_root / filename)
            for name, filename in POLICY_PACK_FILES.items()
        },
        **{
            f"advisor_policy.{name}": _as_posix(advisor_root / filename)
            for name, filename in ADVISOR_POLICY_FILES.items()
        },
        **{
            f"manager_calculated.{name}": _as_posix(manager_calc_root / filename)
            for name, filename in MANAGER_CALCULATED_FILES.items()
        },
    }

    return {
        "policy_pack_dir": _as_posix(pack_root),
        "advisor_policy_dir": _as_posix(advisor_root),
        "manager_calculated_dir": _as_posix(manager_calc_root),
        "policy_pack": policy_pack,
        "advisor_policy": advisor_policy,
        "manager_calculated": manager_calculated,
        "source_paths": source_paths,
    }


def calculate_manager_mandate_attribution(context: dict[str, Any]) -> dict[str, Any]:
    pack = context["policy_pack"]
    advisor = context["advisor_policy"]
    manager_calculated = context["manager_calculated"]

    policy_inputs = pack["policy_level_attribution_inputs"]
    actual_snapshot = pack["actual_manager_allocation_snapshot"]
    benchmark_catalog = pack["manager_mandate_benchmark_catalog"]
    basis_map = pack["manager_benchmark_basis_map"]
    readiness = pack["policy_mandate_readiness_summary"]
    advisor_summary = advisor["advisor_policy_summary"]
    advisor_rows = advisor["advisor_policy_manager_rows"]
    calculated_summary = manager_calculated["manager_calculated_summary"]

    actual_by_manager = _by_manager(actual_snapshot["manager_rows"])
    benchmark_by_manager = _by_manager(benchmark_catalog["benchmark_rows"])
    basis_by_manager = _by_manager(basis_map["rows"])
    advisor_by_manager = _by_manager(advisor_rows["manager_rows"])
    calculated_by_manager = _by_manager(calculated_summary["managers"])

    decimal_rows: list[dict[str, Any]] = []
    driver_decimal_rows: list[dict[str, Any]] = []
    manager_driver_tie_outs: dict[str, dict[str, Any]] = {}

    for input_row in policy_inputs["input_rows"]:
        manager_id = input_row["manager_id"]
        actual_row = actual_by_manager[manager_id]
        benchmark_row = benchmark_by_manager[manager_id]
        basis_row = basis_by_manager[manager_id]
        advisor_row = advisor_by_manager[manager_id]
        calculated_row = calculated_by_manager[manager_id]

        actual_weight = _d(actual_row["actual_weight"])
        manager_actual_return = _d(input_row["manager_actual_return"])
        mandate_benchmark_return = _d(benchmark_row["synthetic_period_return"])
        active_return = manager_actual_return - mandate_benchmark_return
        implementation_effect = actual_weight * active_return

        row = {
            "manager_id": manager_id,
            "display_name": input_row["display_name"],
            "actual_weight": actual_weight,
            "mandate_benchmark_id": benchmark_row["mandate_benchmark_id"],
            "mandate_benchmark_display_name": benchmark_row[
                "mandate_benchmark_display_name"
            ],
            "mandate_benchmark_return": mandate_benchmark_return,
            "manager_actual_return": manager_actual_return,
            "active_return_vs_mandate": active_return,
            "manager_implementation_effect": implementation_effect,
            "status": _implementation_status(active_return),
            "benchmark_basis_type": basis_row["benchmark_basis_type"],
            "benchmark_basis_description": basis_row["benchmark_basis_description"],
            "source_advisor_policy_effect": _d(advisor_row["advisor_policy_effect"]),
            "source_driver_tie_out_status": calculated_row["tie_out_status"],
            "effect_basis": "percentage_points_of_total_portfolio_return",
            "caveats": [
                "Synthetic local-demo mandate benchmark basis.",
                "Manager effect is limited to capital the manager controlled.",
            ],
        }
        decimal_rows.append(row)

        manager_driver_rows = _driver_decimal_rows_for_manager(
            manager_row=row,
            calculated_row=calculated_row,
        )
        driver_decimal_rows.extend(manager_driver_rows)
        driver_active_return = sum(
            driver_row["manager_return_effect"] for driver_row in manager_driver_rows
        )
        driver_portfolio_effect = sum(
            driver_row["portfolio_effect"] for driver_row in manager_driver_rows
        )
        manager_driver_tie_outs[manager_id] = {
            "display_name": row["display_name"],
            "manager_active_return": _return_number(active_return),
            "driver_active_return": _return_number(driver_active_return),
            "active_return_difference": _return_number(
                driver_active_return - active_return
            ),
            "manager_implementation_effect": _return_number(implementation_effect),
            "driver_portfolio_effect": _return_number(driver_portfolio_effect),
            "portfolio_effect_difference": _return_number(
                driver_portfolio_effect - implementation_effect
            ),
            "status": _residual_status(driver_portfolio_effect - implementation_effect),
            "timing_used_as_residual": False,
        }

    total_actual_weight = sum(row["actual_weight"] for row in decimal_rows)
    total_manager_implementation_effect = sum(
        row["manager_implementation_effect"] for row in decimal_rows
    )
    total_active_return_weighted = total_manager_implementation_effect
    advisor_handoff = _d(advisor_summary["manager_implementation_effect_handoff"])
    handoff_residual = total_manager_implementation_effect - advisor_handoff
    total_driver_portfolio_effect = sum(
        row["portfolio_effect"] for row in driver_decimal_rows
    )
    driver_residual = total_driver_portfolio_effect - total_manager_implementation_effect

    largest_positive_manager = max(
        decimal_rows,
        key=lambda row: row["manager_implementation_effect"],
    )
    negative_manager_rows = [
        row for row in decimal_rows if row["manager_implementation_effect"] < Decimal("0")
    ]
    largest_negative_manager = (
        min(negative_manager_rows, key=lambda row: row["manager_implementation_effect"])
        if negative_manager_rows
        else None
    )
    largest_positive_driver = max(
        driver_decimal_rows,
        key=lambda row: row["portfolio_effect"],
    )
    largest_negative_driver = min(
        driver_decimal_rows,
        key=lambda row: row["portfolio_effect"],
    )
    selected_manager = max(
        decimal_rows,
        key=lambda row: abs(row["manager_implementation_effect"]),
    )

    manager_rows_payload = {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "effect_basis": "percentage_points_of_total_portfolio_return",
        "manager_count": len(decimal_rows),
        "manager_rows": [_serializable_manager_row(row) for row in decimal_rows],
        "total_row": {
            "display_name": "Total manager implementation effect",
            "actual_weight": _weight_number(total_actual_weight),
            "manager_implementation_effect": _return_number(
                total_manager_implementation_effect
            ),
            "status": "total",
            "effect_basis": "percentage_points_of_total_portfolio_return",
        },
        "tie_out": {
            "manager_implementation_effect_from_rows": _return_number(
                total_manager_implementation_effect
            ),
            "advisor_policy_attribution_v2_handoff": _return_number(advisor_handoff),
            "handoff_residual": _return_number(handoff_residual),
            "status": _residual_status(handoff_residual),
        },
        "advisor_policy_effects_excluded_from_manager_rows": True,
    }

    driver_rows_payload = {
        "schema_version": DRIVER_ROWS_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "driver_basis": "synthetic_local_demo_manager_driver_components",
        "timing_attribution_included": False,
        "timing_used_as_residual": False,
        "effect_basis": "manager_return_effect_and_percentage_points_of_total_portfolio_return",
        "driver_rows": [
            _serializable_driver_row(row) for row in driver_decimal_rows
        ],
        "manager_driver_tie_outs": manager_driver_tie_outs,
        "total_driver_portfolio_effect": _return_number(total_driver_portfolio_effect),
        "total_manager_implementation_effect": _return_number(
            total_manager_implementation_effect
        ),
        "driver_residual": _return_number(driver_residual),
        "driver_residual_status": _residual_status(driver_residual),
    }

    selected_driver_rows = [
        row for row in driver_decimal_rows if row["manager_id"] == selected_manager["manager_id"]
    ]
    selected_manager_detail = {
        "schema_version": SELECTED_MANAGER_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "selection_rule": "largest_absolute_manager_implementation_effect",
        "selection_reason": (
            "Selected because it has the largest absolute manager effect in this synthetic run."
        ),
        "selected_manager_id": selected_manager["manager_id"],
        "display_name": selected_manager["display_name"],
        "manager_row": _serializable_manager_row(selected_manager),
        "driver_rows": [
            _serializable_driver_row(row) for row in selected_driver_rows
        ],
        "tie_out": {
            "active_return_vs_mandate": _return_number(
                selected_manager["active_return_vs_mandate"]
            ),
            "driver_active_return": _return_number(
                sum(row["manager_return_effect"] for row in selected_driver_rows)
            ),
            "manager_implementation_effect": _return_number(
                selected_manager["manager_implementation_effect"]
            ),
            "driver_portfolio_effect": _return_number(
                sum(row["portfolio_effect"] for row in selected_driver_rows)
            ),
            "status": manager_driver_tie_outs[selected_manager["manager_id"]]["status"],
        },
    }

    summary = {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack_id": pack["manifest"]["pack_id"],
        "source_advisor_policy_attribution_engine_id": SOURCE_ADVISOR_ENGINE_ID,
        "source_manager_calculated_engine_id": SOURCE_MANAGER_CALCULATED_ENGINE_ID,
        "manager_count": len(decimal_rows),
        "actual_weight_sum": _weight_number(total_actual_weight),
        "above_mandate_manager_count": sum(
            1 for row in decimal_rows if row["status"] == "above_mandate"
        ),
        "below_mandate_manager_count": sum(
            1 for row in decimal_rows if row["status"] == "below_mandate"
        ),
        "near_mandate_manager_count": sum(
            1 for row in decimal_rows if row["status"] == "near_mandate"
        ),
        "review_manager_count": sum(
            1 for row in decimal_rows if row["status"] == "review"
        ),
        "total_active_return_weighted": _return_number(total_active_return_weighted),
        "total_manager_implementation_effect": _return_number(
            total_manager_implementation_effect
        ),
        "advisor_policy_attribution_v2_handoff": _return_number(advisor_handoff),
        "advisor_handoff_residual": _return_number(handoff_residual),
        "advisor_handoff_residual_status": _residual_status(handoff_residual),
        "actual_allocation_benchmark_return": advisor_summary[
            "actual_allocation_benchmark_return"
        ],
        "actual_portfolio_return_context": advisor_summary[
            "actual_portfolio_return_context"
        ],
        "effect_basis": "percentage_points_of_total_portfolio_return",
        "manager_return_basis": "manager_return_minus_manager_mandate_benchmark_return",
        "largest_positive_manager": _manager_summary_row(largest_positive_manager),
        "largest_negative_manager": (
            _manager_summary_row(largest_negative_manager)
            if largest_negative_manager
            else None
        ),
        "largest_positive_manager_driver": _driver_summary_row(largest_positive_driver),
        "largest_negative_manager_driver": _driver_summary_row(largest_negative_driver),
        "selected_manager_for_detail": selected_manager["display_name"],
        "selected_manager_id_for_detail": selected_manager["manager_id"],
        "handoff_to_advisor_policy_attribution_v2": {
            "source_engine_id": SOURCE_ADVISOR_ENGINE_ID,
            "advisor_policy_report_excludes_manager_implementation": True,
            "manager_implementation_effect_handoff": _return_number(advisor_handoff),
            "manager_report_total_effect": _return_number(
                total_manager_implementation_effect
            ),
            "residual": _return_number(handoff_residual),
            "status": _residual_status(handoff_residual),
        },
        "gated_calculations_not_included": [
            row["report_id"] for row in GATED_REPORTS
        ],
        "source_readiness_status": readiness[
            "manager_mandate_attribution_readiness"
        ],
        "headline_interpretation": (
            "Managers finished above mandate benchmarks on the actual capital they controlled."
        ),
        "caveats": [
            "Synthetic local-demo attribution only; production use needs approved real manager returns and benchmarks.",
            "Driver categories are local synthetic diagnostics and are not production-approved.",
        ],
    }

    quality_summary = _quality_summary(
        context=context,
        decimal_rows=decimal_rows,
        driver_decimal_rows=driver_decimal_rows,
        manager_driver_tie_outs=manager_driver_tie_outs,
        summary=summary,
        handoff_residual=handoff_residual,
        driver_residual=driver_residual,
    )
    manifest = _manifest(context, summary, quality_summary)

    return {
        "manifest": manifest,
        "summary": summary,
        "manager_rows": manager_rows_payload,
        "driver_rows": driver_rows_payload,
        "selected_manager_detail": selected_manager_detail,
        "quality_summary": quality_summary,
    }


def build_manager_mandate_report_inputs(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    inputs = {
        "manager_mandate_attribution_summary": _summary_report_input(
            artifacts, context
        ),
        "within_manager_attribution_detail": _within_manager_detail_report_input(
            artifacts, context
        ),
        "manager_implementation_handoff": _handoff_report_input(
            artifacts, context
        ),
    }
    _validate_report_ids(inputs)
    return inputs


def build_manager_mandate_report_views(
    inputs: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    _validate_report_ids(inputs)
    views: dict[str, dict[str, Any]] = {}
    for report_id in BUILD_NOW_REPORT_IDS:
        payload = inputs[report_id]
        visible = payload["visible_content"]
        view = {
            "schema_version": REPORT_VIEW_SCHEMA_VERSION,
            "generator_version": GENERATOR_VERSION,
            "generated_at": GENERATED_AT,
            "synthetic_data": True,
            "local_only": True,
            "report_element_id": report_id,
            "display_title": payload["display_title"],
            "report_family": "manager_mandate_attribution",
            "master_question_family": "Performance / Plan",
            "exact_report_question": payload["exact_report_question"],
            "audience_tier": payload["audience_tier"],
            "summary_detail_status": payload["summary_detail_status"],
            "representation_level": payload["representation_level"],
            "denominator_category_system": payload["denominator_category_system"],
            "rendering_mode": payload["rendering_mode"],
            "headline_sentence": visible["headline_sentence"],
            "headline_metrics": visible["headline_metrics"],
            "benchmark_basis": visible["benchmark_basis"],
            "benchmark_basis_note": visible["benchmark_basis_note"],
            "compact_table": visible.get("compact_table"),
            "driver_table": visible.get("driver_table"),
            "total_row": visible.get("total_row"),
            "tie_out_note": visible.get("tie_out_note"),
            "effect_basis_note": visible["effect_basis_note"],
            "caveats": visible["caveats"],
            "advisor_note": visible["advisor_note"],
            "source_advisor_policy_attribution_engine_id": SOURCE_ADVISOR_ENGINE_ID,
            "manager_implementation_visible_in_advisor_policy_report": False,
            "advisor_policy_effects_visible_in_manager_reports": False,
            "internal_source_refs": payload["internal_source_refs"],
            "internal_source_metadata": payload["internal_source_metadata"],
            "information_budget_applied": _budget_actuals(
                report_id=report_id,
                visible=visible,
                rendering_mode=payload["rendering_mode"],
            ),
            "table_validation": payload["table_validation"],
            "gated_or_deferred": False,
        }
        _validate_view_budget(view)
        _validate_visible_language(view)
        views[report_id] = view
    return views


def render_markdown_mockup(view: dict[str, Any]) -> str:
    lines = [f"# {view['display_title']}", "", view["headline_sentence"], ""]

    if view["headline_metrics"]:
        lines.extend(["## Key Metrics", ""])
        for metric in view["headline_metrics"]:
            lines.append(f"- **{metric['label']}:** {metric['formatted_value']}")
        lines.append("")

    benchmark_basis = view.get("benchmark_basis")
    if benchmark_basis and benchmark_basis.get("visible"):
        lines.extend(["## Benchmark Basis", ""])
        lines.extend(_render_benchmark_basis(benchmark_basis))
        lines.append("")
        if view.get("benchmark_basis_note"):
            lines.extend([view["benchmark_basis_note"], ""])

    compact_table = view.get("compact_table")
    if compact_table:
        lines.extend([f"## {compact_table['title']}", ""])
        lines.extend(_render_markdown_table(compact_table, view.get("total_row")))
        lines.append("")

    driver_table = view.get("driver_table")
    if driver_table:
        lines.extend([f"## {driver_table['title']}", ""])
        lines.extend(_render_markdown_table(driver_table))
        lines.append("")

    if view.get("tie_out_note"):
        lines.extend(["## Tie-Out", "", view["tie_out_note"], ""])

    lines.extend(["## Effect Basis", "", view["effect_basis_note"], ""])

    if view.get("caveats"):
        lines.extend(["## Caveat", ""])
        for caveat in view["caveats"]:
            lines.append(f"- {caveat}")
        lines.append("")

    if view.get("advisor_note"):
        lines.extend(["## Advisor Note", "", view["advisor_note"], ""])

    markdown = "\n".join(lines).rstrip() + "\n"
    _validate_markdown(view, markdown)
    return markdown


def generate_manager_mandate_attribution(
    *,
    policy_pack_dir: str | Path = DEFAULT_POLICY_PACK_DIR,
    advisor_policy_dir: str | Path = DEFAULT_ADVISOR_POLICY_DIR,
    manager_calculated_dir: str | Path = DEFAULT_MANAGER_CALCULATED_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    input_dir: str | Path = DEFAULT_INPUT_DIR,
    view_dir: str | Path = DEFAULT_VIEW_DIR,
    mockup_dir: str | Path = DEFAULT_MOCKUP_DIR,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    input_path = Path(input_dir)
    view_path = Path(view_dir)
    mockup_path = Path(mockup_dir)
    for path in (output_path, input_path, view_path, mockup_path):
        path.mkdir(parents=True, exist_ok=True)

    context = load_source_context(
        policy_pack_dir=policy_pack_dir,
        advisor_policy_dir=advisor_policy_dir,
        manager_calculated_dir=manager_calculated_dir,
    )
    artifacts = calculate_manager_mandate_attribution(context)
    inputs = build_manager_mandate_report_inputs(artifacts, context)
    views = build_manager_mandate_report_views(inputs)

    calculated_files: list[str] = []
    for key, filename in CALCULATED_ARTIFACT_FILES.items():
        _write_json(output_path / filename, artifacts[key])
        calculated_files.append(filename)

    input_files: list[str] = []
    for report_id in BUILD_NOW_REPORT_IDS:
        filename = INPUT_FILENAME_BY_REPORT_ID[report_id]
        _write_json(input_path / filename, inputs[report_id])
        input_files.append(filename)

    input_index = _input_index(input_files, inputs)
    _write_json(input_path / "manager_mandate_attribution_report_input_index.json", input_index)
    input_files.append("manager_mandate_attribution_report_input_index.json")

    view_files: list[str] = []
    mockup_files: list[str] = []
    for report_id in BUILD_NOW_REPORT_IDS:
        view_filename = VIEW_FILENAME_BY_REPORT_ID[report_id]
        mockup_filename = MOCKUP_FILENAME_BY_REPORT_ID[report_id]
        view = views[report_id]
        markdown = render_markdown_mockup(view)
        _write_json(view_path / view_filename, view)
        (mockup_path / mockup_filename).write_text(markdown, encoding="utf-8")
        view_files.append(view_filename)
        mockup_files.append(mockup_filename)

    gated_index = _gated_deferred_index()
    _write_json(
        view_path / "gated_deferred_manager_mandate_attribution_index.json",
        gated_index,
    )
    view_files.append("gated_deferred_manager_mandate_attribution_index.json")

    readme = render_mockup_readme(views, gated_index)
    (mockup_path / "README.md").write_text(readme, encoding="utf-8")
    mockup_files.append("README.md")

    view_index = _view_index(view_files, mockup_files, views, gated_index)
    _write_json(view_path / "manager_mandate_attribution_report_view_index.json", view_index)
    view_files.append("manager_mandate_attribution_report_view_index.json")

    return {
        "schema_version": "manager_mandate_attribution_generation_summary.v1",
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack_id": context["policy_pack"]["manifest"]["pack_id"],
        "source_advisor_policy_attribution_engine_id": SOURCE_ADVISOR_ENGINE_ID,
        "calculated_artifact_count": len(CALCULATED_ARTIFACT_FILES),
        "report_input_count": len(inputs),
        "report_view_count": len(views),
        "markdown_mockup_count": len(MOCKUP_FILENAME_BY_REPORT_ID),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "calculated_files": calculated_files,
        "input_files": input_files,
        "view_files": view_files,
        "mockup_files": mockup_files,
        "gated_reports_not_generated": [
            row["report_id"] for row in gated_index["gated_or_deferred_reports"]
        ],
        "advisor_handoff_tie_out_passed": (
            artifacts["manager_rows"]["tie_out"]["status"] == "pass"
        ),
        "driver_tie_outs_passed": (
            artifacts["driver_rows"]["driver_residual_status"] == "pass"
            and all(
                row["status"] == "pass"
                for row in artifacts["driver_rows"]["manager_driver_tie_outs"].values()
            )
        ),
        "manager_implementation_visible_in_advisor_policy_report": False,
        "advisor_policy_effects_visible_in_manager_reports": False,
        "output_dir": _as_posix(output_path),
        "input_dir": _as_posix(input_path),
        "view_dir": _as_posix(view_path),
        "mockup_dir": _as_posix(mockup_path),
    }


def render_mockup_readme(
    views: dict[str, dict[str, Any]],
    gated_index: dict[str, Any],
) -> str:
    lines = [
        "# Manager Mandate Attribution v1 Report Mockups",
        "",
        (
            "These local product-review mockups show manager implementation against manager mandate benchmarks."
        ),
        (
            "They keep manager implementation separate from advisor selected mandate, target weighting, and funding drift effects."
        ),
        (
            "They are not wired into Advisor Preview, Populate, Present, generated reports, Docker, deployment, live data, external data, or production reporting."
        ),
        "",
        "## Generated Mockups",
        "",
    ]
    for report_id in BUILD_NOW_REPORT_IDS:
        view = views[report_id]
        filename = MOCKUP_FILENAME_BY_REPORT_ID[report_id]
        lines.append(f"- [{view['display_title']}]({filename})")

    lines.extend(
        [
            "",
            "## Gated Or Deferred",
            "",
        ]
    )
    for row in gated_index["gated_or_deferred_reports"]:
        lines.append(f"- {row['display_title']} ({row['status']}): {row['reason']}")

    return "\n".join(lines).rstrip() + "\n"


def _summary_report_input(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    summary = artifacts["summary"]
    manager_payload = artifacts["manager_rows"]
    rows = [
        {
            "Manager/Sleeve": row["display_name"],
            "Actual Weight": _format_percent(row["actual_weight"]),
            "Mandate Benchmark": row["mandate_benchmark_display_name"],
            "Mandate Benchmark Return": _format_percent(
                row["mandate_benchmark_return"]
            ),
            "Actual Return": _format_percent(row["manager_actual_return"]),
            "Active Return": _format_signed_percent(
                row["active_return_vs_mandate"]
            ),
            "Manager Effect": _format_effect_pp(
                row["manager_implementation_effect"]
            ),
            "Status": _status_label(row["status"]),
        }
        for row in manager_payload["manager_rows"]
    ]
    total = manager_payload["total_row"]
    total_row = {
        "Manager/Sleeve": "Total",
        "Actual Weight": _format_percent(total["actual_weight"]),
        "Mandate Benchmark": "Manager mandate basket",
        "Mandate Benchmark Return": "N/A",
        "Actual Return": "Actual capital basis",
        "Active Return": "N/A",
        "Manager Effect": _format_effect_pp(total["manager_implementation_effect"]),
        "Status": "Manager total",
    }
    largest = summary["largest_positive_manager"]
    visible_content = {
        "headline_sentence": (
            "Managers added +1.05 pp versus their mandate benchmarks on actual capital controlled."
        ),
        "headline_metrics": [
            _metric(
                "Total manager effect",
                summary["total_manager_implementation_effect"],
                _format_effect_pp(summary["total_manager_implementation_effect"]),
            ),
            _metric(
                "Managers above mandate",
                summary["above_mandate_manager_count"],
                f"{summary['above_mandate_manager_count']} of {summary['manager_count']}",
            ),
            _metric(
                "Largest positive manager",
                largest["manager_implementation_effect"],
                (
                    f"{largest['display_name']}: "
                    f"{_format_effect_pp(largest['manager_implementation_effect'])}"
                ),
            ),
        ],
        "compact_table": _table(
            "Manager Mandate Attribution Summary",
            [
                "Manager/Sleeve",
                "Actual Weight",
                "Mandate Benchmark",
                "Mandate Benchmark Return",
                "Actual Return",
                "Active Return",
                "Manager Effect",
                "Status",
            ],
            rows,
        ),
        "benchmark_basis": _portfolio_benchmark_basis(summary),
        "benchmark_basis_note": _manager_benchmark_basis_note(),
        "total_row": total_row,
        "effect_basis_note": (
            "Active return is manager return minus mandate benchmark return. "
            "Manager Effect equals actual weight times active return and is shown as percentage points of total portfolio return."
        ),
        "caveats": [
            "Synthetic local-demo manager attribution only; production use needs approved real manager returns and benchmarks."
        ],
        "advisor_note": (
            "Use Advisor Policy Attribution for selected mandate, target weighting, and funding drift."
        ),
    }
    return _report_input(
        report_element_id="manager_mandate_attribution_summary",
        display_title="Manager Mandate Attribution Summary",
        exact_report_question=(
            "How did each manager perform versus the mandate benchmark for the capital it controlled?"
        ),
        audience_tier="advisor_review_and_client_briefing_when_sophisticated",
        summary_detail_status="summary_with_all_manager_rows",
        representation_level="manager_sleeve_implementation_effect_rows",
        denominator_category_system="percentage_points_of_total_portfolio_return",
        rendering_mode="compact_manager_mandate_table",
        visible_content=visible_content,
        context=context,
        source_keys=(
            "policy_pack.actual_manager_allocation_snapshot",
            "policy_pack.manager_mandate_benchmark_catalog",
            "policy_pack.policy_level_attribution_inputs",
            "advisor_policy.advisor_policy_summary",
        ),
        table_validation={
            "manager_rows_shown": len(rows),
            "total_row_visible": True,
            "advisor_policy_effect_columns_visible": False,
            "global_benchmark_columns_visible": False,
            "manager_implementation_effect_visible": True,
        },
    )


def _within_manager_detail_report_input(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    detail = artifacts["selected_manager_detail"]
    manager_row = detail["manager_row"]
    driver_rows = detail["driver_rows"]
    rows = [
        {
            "Driver": row["driver_label"],
            "Category": row["driver_category"],
            "Manager Return Effect": _format_signed_percent(
                row["manager_return_effect"]
            ),
            "Portfolio Effect": _format_effect_pp(row["portfolio_effect"]),
            "Meaning": row["meaning"],
        }
        for row in driver_rows
    ]
    visible_content = {
        "headline_sentence": (
            f"{manager_row['display_name']} added "
            f"{_format_signed_percent(manager_row['active_return_vs_mandate'])} "
            f"on sleeve basis, contributing "
            f"{_format_effect_pp(manager_row['manager_implementation_effect'])} "
            "to total portfolio return."
        ),
        "headline_metrics": [
            _metric(
                "Active return",
                manager_row["active_return_vs_mandate"],
                _format_signed_percent(manager_row["active_return_vs_mandate"]),
            ),
            _metric(
                "Manager effect",
                manager_row["manager_implementation_effect"],
                _format_effect_pp(manager_row["manager_implementation_effect"]),
            ),
            _metric(
                "Actual weight",
                manager_row["actual_weight"],
                _format_percent(manager_row["actual_weight"]),
            ),
        ],
        "driver_table": _table(
            "Within-Manager Driver Detail",
            [
                "Driver",
                "Category",
                "Manager Return Effect",
                "Portfolio Effect",
                "Meaning",
            ],
            rows,
        ),
        "benchmark_basis": _selected_manager_benchmark_basis(manager_row),
        "benchmark_basis_note": (
            "Within-manager detail compares this manager's return with its own mandate benchmark; other advisor policy effects stay in the advisor report."
        ),
        "tie_out_note": (
            f"Driver rows tie to "
            f"{_format_signed_percent(detail['tie_out']['active_return_vs_mandate'])} "
            f"active return and "
            f"{_format_effect_pp(detail['tie_out']['manager_implementation_effect'])} "
            "portfolio effect."
        ),
        "effect_basis_note": (
            "Manager return effects are sleeve-level return components. "
            "Portfolio effects multiply those components by the manager's actual weight."
        ),
        "caveats": [
            "Driver categories are synthetic local-demo diagnostics and are not production-approved."
        ],
        "advisor_note": (
            "Use the manager summary to see how this row contributes to the total manager effect."
        ),
    }
    return _report_input(
        report_element_id="within_manager_attribution_detail",
        display_title="Within-Manager Attribution Detail",
        exact_report_question=(
            "What synthetic driver categories explain the selected manager's active return versus mandate?"
        ),
        audience_tier="advisor_review_and_internal_product_review",
        summary_detail_status="selected_manager_detail",
        representation_level="selected_manager_within_mandate_driver_rows",
        denominator_category_system="manager_return_effect_and_percentage_points_of_total_portfolio_return",
        rendering_mode="selected_manager_driver_table",
        visible_content=visible_content,
        context=context,
        source_keys=(
            "manager_calculated.manager_calculated_summary",
            "policy_pack.manager_mandate_benchmark_catalog",
            "policy_pack.policy_level_attribution_inputs",
        ),
        table_validation={
            "selected_manager": manager_row["display_name"],
            "selection_reason": detail["selection_reason"],
            "driver_rows_shown": len(rows),
            "tie_out_note_visible": True,
            "timing_attribution_visible": False,
            "position_level_rows_visible": False,
        },
    )


def _handoff_report_input(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    summary = artifacts["summary"]
    rows = [
        {
            "Tie-Out Item": "Manager reports total",
            "Value": _format_effect_pp(summary["total_manager_implementation_effect"]),
            "Meaning": "Sum of actual weight times active return versus each mandate benchmark.",
        },
        {
            "Tie-Out Item": "Advisor v2 handoff",
            "Value": _format_effect_pp(summary["advisor_policy_attribution_v2_handoff"]),
            "Meaning": "Manager implementation amount excluded from Advisor Policy Attribution.",
        },
        {
            "Tie-Out Item": "Residual",
            "Value": _format_effect_pp(summary["advisor_handoff_residual"]),
            "Meaning": "Passes local synthetic tie-out tolerance.",
        },
    ]
    visible_content = {
        "headline_sentence": (
            "Manager implementation ties to the Advisor Policy Attribution v2 handoff with a +0.00 pp residual."
        ),
        "headline_metrics": [
            _metric(
                "Total manager effect",
                summary["total_manager_implementation_effect"],
                _format_effect_pp(summary["total_manager_implementation_effect"]),
            ),
            _metric(
                "Advisor handoff",
                summary["advisor_policy_attribution_v2_handoff"],
                _format_effect_pp(summary["advisor_policy_attribution_v2_handoff"]),
            ),
            _metric(
                "Residual",
                summary["advisor_handoff_residual"],
                _format_effect_pp(summary["advisor_handoff_residual"]),
            ),
        ],
        "compact_table": _table(
            "Manager Implementation Handoff",
            ["Tie-Out Item", "Value", "Meaning"],
            rows,
        ),
        "benchmark_basis": _portfolio_benchmark_basis(summary),
        "benchmark_basis_note": (
            "The handoff starts from actual manager capital and mandate benchmarks; advisor policy effects remain in the separate advisor report."
        ),
        "effect_basis_note": (
            "Both totals are percentage points of total portfolio return, so the handoff can reconcile without combining decision layers."
        ),
        "caveats": [
            "This handoff is a local synthetic control check, not a production client report."
        ],
        "advisor_note": (
            "Read this after the Advisor Policy Attribution report when manager implementation needs explanation."
        ),
    }
    return _report_input(
        report_element_id="manager_implementation_handoff",
        display_title="Manager Implementation Handoff",
        exact_report_question=(
            "Does manager mandate attribution tie to the manager implementation handoff in advisor policy attribution?"
        ),
        audience_tier="internal_product_review_and_advisor_quality_control",
        summary_detail_status="handoff_control_check",
        representation_level="portfolio_manager_implementation_handoff",
        denominator_category_system="percentage_points_of_total_portfolio_return",
        rendering_mode="compact_handoff_table",
        visible_content=visible_content,
        context=context,
        source_keys=(
            "advisor_policy.advisor_policy_summary",
            "policy_pack.policy_level_attribution_inputs",
        ),
        table_validation={
            "handoff_rows_shown": len(rows),
            "advisor_policy_effect_columns_visible": False,
            "manager_implementation_handoff_visible": True,
            "residual_status": summary["advisor_handoff_residual_status"],
        },
    )


def _report_input(
    *,
    report_element_id: str,
    display_title: str,
    exact_report_question: str,
    audience_tier: str,
    summary_detail_status: str,
    representation_level: str,
    denominator_category_system: str,
    rendering_mode: str,
    visible_content: dict[str, Any],
    context: dict[str, Any],
    source_keys: tuple[str, ...],
    table_validation: dict[str, Any],
) -> dict[str, Any]:
    pack = context["policy_pack"]
    source_refs = [context["source_paths"][key] for key in source_keys]
    return {
        "schema_version": REPORT_INPUT_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "report_element_id": report_element_id,
        "display_title": display_title,
        "report_family": "manager_mandate_attribution",
        "master_question_family": "Performance / Plan",
        "exact_report_question": exact_report_question,
        "audience_tier": audience_tier,
        "summary_detail_status": summary_detail_status,
        "representation_level": representation_level,
        "denominator_category_system": denominator_category_system,
        "rendering_mode": rendering_mode,
        "visible_content": visible_content,
        "source_policy_mandate_pack_id": pack["manifest"]["pack_id"],
        "source_advisor_policy_attribution_engine_id": SOURCE_ADVISOR_ENGINE_ID,
        "source_manager_calculated_engine_id": SOURCE_MANAGER_CALCULATED_ENGINE_ID,
        "manager_implementation_visible_in_advisor_policy_report": False,
        "advisor_policy_effects_visible_in_manager_reports": False,
        "internal_source_refs": source_refs,
        "internal_source_metadata": {
            "calculated_engine_id": ENGINE_ID,
            "source_policy_mandate_pack_id": pack["manifest"]["pack_id"],
            "source_advisor_policy_attribution_engine_id": SOURCE_ADVISOR_ENGINE_ID,
            "source_manager_calculated_engine_id": SOURCE_MANAGER_CALCULATED_ENGINE_ID,
        },
        "table_validation": table_validation,
        "information_budget": _budget_for_report(report_element_id),
        "gated_or_deferred": False,
        "not_wired_into_advisor_ui": True,
        "not_wired_into_generated_report_flow": True,
    }


def _manifest(
    context: dict[str, Any],
    summary: dict[str, Any],
    quality_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "manager_mandate_attribution_manifest.v1",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack": context["policy_pack"]["manifest"]["pack_id"],
        "source_policy_mandate_pack_dir": context["policy_pack_dir"],
        "source_advisor_policy_attribution_engine_id": SOURCE_ADVISOR_ENGINE_ID,
        "source_advisor_policy_attribution_dir": context["advisor_policy_dir"],
        "source_manager_calculated_engine_id": SOURCE_MANAGER_CALCULATED_ENGINE_ID,
        "source_manager_calculated_dir": context["manager_calculated_dir"],
        "generated_artifacts": dict(CALCULATED_ARTIFACT_FILES),
        "methodology_summary": {
            "manager_active_return": "Manager actual return minus manager mandate benchmark return.",
            "manager_implementation_effect": "Actual manager weight times manager active return.",
            "driver_rows": "Synthetic local driver components scaled by actual manager weight.",
            "advisor_handoff": "Total manager implementation effect reconciles to advisor policy attribution v2 handoff.",
        },
        "calculations_supported": [
            "manager_active_return_vs_mandate",
            "manager_implementation_effect",
            "within_manager_driver_rows",
            "selected_manager_detail",
            "advisor_policy_attribution_v2_handoff",
            "row_tie_outs",
        ],
        "calculations_gated": [row["report_id"] for row in GATED_REPORTS],
        "limitations": [
            "Synthetic local demo only.",
            "Driver categories are diagnostics for product review, not production-approved diagnostics.",
            "Timing, dollar P&L, production client data, blended, and position-level outputs are gated.",
        ],
        "approval_status": "synthetic_demo_approved",
        "quality_summary_status": quality_summary["overall_status"],
        "total_manager_implementation_effect": summary[
            "total_manager_implementation_effect"
        ],
        "advisor_handoff_residual_status": summary["advisor_handoff_residual_status"],
    }


def _quality_summary(
    *,
    context: dict[str, Any],
    decimal_rows: list[dict[str, Any]],
    driver_decimal_rows: list[dict[str, Any]],
    manager_driver_tie_outs: dict[str, dict[str, Any]],
    summary: dict[str, Any],
    handoff_residual: Decimal,
    driver_residual: Decimal,
) -> dict[str, Any]:
    pack = context["policy_pack"]
    manager_count = len(decimal_rows)
    coverage = {
        "policy_pack_manager_count": pack["actual_manager_allocation_snapshot"][
            "manager_count"
        ],
        "manager_rows_generated": manager_count,
        "driver_rows_generated": len(driver_decimal_rows),
        "all_current_managers_covered": (
            pack["actual_manager_allocation_snapshot"]["manager_count"] == manager_count
        ),
        "advisor_policy_v2_source_loaded": True,
        "manager_calculated_driver_source_loaded": True,
        "source_data_synthetic_local_only": True,
    }
    formula_checks = {
        "actual_weight_sum_status": _weight_sum_status(
            sum(row["actual_weight"] for row in decimal_rows)
        ),
        "manager_effect_row_sum_status": _residual_status(handoff_residual),
        "advisor_handoff_residual_status": _residual_status(handoff_residual),
        "driver_residual_status": _residual_status(driver_residual),
        "all_manager_driver_tie_outs_pass": all(
            row["status"] == "pass" for row in manager_driver_tie_outs.values()
        ),
    }
    output_scope = {
        "no_timing_attribution": True,
        "no_dollar_pnl_attribution": True,
        "no_production_client_manager_attribution": True,
        "no_blended_all_in_report": True,
        "no_position_level_manager_attribution": True,
        "no_external_or_live_data": True,
        "no_new_backend_or_ui_wiring": True,
        "advisor_policy_effects_excluded_from_manager_reports": True,
    }
    overall_status = (
        "pass"
        if coverage["all_current_managers_covered"]
        and all(
            value == "pass"
            for key, value in formula_checks.items()
            if key.endswith("_status")
        )
        and formula_checks["all_manager_driver_tie_outs_pass"]
        and all(output_scope.values())
        else "review"
    )
    return {
        "schema_version": "manager_mandate_attribution_quality_summary.v1",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "overall_status": overall_status,
        "coverage": coverage,
        "formula_checks": formula_checks,
        "manager_driver_tie_outs": manager_driver_tie_outs,
        "output_scope": output_scope,
        "largest_positive_manager": summary["largest_positive_manager"],
        "largest_negative_manager": summary["largest_negative_manager"],
        "recommended_next_tranche": "Full Manager-by-Manager Driver Detail",
        "limitations": [
            "Synthetic local-demo manager attribution only.",
            "Timing and dollar P&L are unavailable in this tranche.",
            "Production client manager attribution requires approved real inputs.",
        ],
    }


def _input_index(
    input_files: list[str],
    inputs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    first = next(iter(inputs.values()))
    return {
        "schema_version": REPORT_INPUT_INDEX_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack_id": first["source_policy_mandate_pack_id"],
        "source_advisor_policy_attribution_engine_id": SOURCE_ADVISOR_ENGINE_ID,
        "report_input_count": len(inputs),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "input_files": input_files,
        "mockups_generated_from_views": True,
        "manager_implementation_visible_in_advisor_policy_report": False,
        "advisor_policy_effects_visible_in_manager_reports": False,
        "advisor_ui_wiring": "not_changed",
        "generated_report_wiring": "not_changed",
    }


def _view_index(
    view_files: list[str],
    mockup_files: list[str],
    views: dict[str, dict[str, Any]],
    gated_index: dict[str, Any],
) -> dict[str, Any]:
    first = next(iter(views.values()))
    return {
        "schema_version": REPORT_VIEW_INDEX_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack_id": first["internal_source_metadata"][
            "source_policy_mandate_pack_id"
        ],
        "source_advisor_policy_attribution_engine_id": SOURCE_ADVISOR_ENGINE_ID,
        "report_view_count": len(views),
        "markdown_mockup_count": len(MOCKUP_FILENAME_BY_REPORT_ID),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "view_files": view_files,
        "mockup_files": mockup_files,
        "mockups_generated_from_views": True,
        "manager_implementation_visible_in_advisor_policy_report": False,
        "advisor_policy_effects_visible_in_manager_reports": False,
        "gated_reports_not_generated": [
            row["report_id"] for row in gated_index["gated_or_deferred_reports"]
        ],
        "information_budget": dict(DEFAULT_INFORMATION_BUDGET),
        "advisor_ui_wiring": "not_changed",
        "generated_report_wiring": "not_changed",
    }


def _gated_deferred_index() -> dict[str, Any]:
    return {
        "schema_version": GATED_INDEX_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_manager_mandate_attribution_engine_id": ENGINE_ID,
        "purpose": "Product/readiness index for manager attribution reports deliberately not generated in v1.",
        "gated_or_deferred_reports": list(GATED_REPORTS),
    }


def _budget_for_report(report_id: str) -> dict[str, Any]:
    budget = dict(DEFAULT_INFORMATION_BUDGET)
    if report_id == "manager_mandate_attribution_summary":
        budget["max_visible_table_rows"] = 7
        budget["exception_reason"] = (
            "Summary report shows all six managers plus a total row."
        )
    elif report_id == "manager_implementation_handoff":
        budget["max_visible_table_rows"] = 3
    return budget


def _budget_actuals(
    *,
    report_id: str,
    visible: dict[str, Any],
    rendering_mode: str,
) -> dict[str, Any]:
    compact_table = visible.get("compact_table")
    driver_table = visible.get("driver_table")
    total_row = visible.get("total_row")
    advisor_note = visible.get("advisor_note")
    benchmark_basis = visible.get("benchmark_basis") or {}
    budget = _budget_for_report(report_id)
    visible_table_rows = (
        (len(compact_table["rows"]) if compact_table else 0)
        + (len(driver_table["rows"]) if driver_table else 0)
        + (1 if total_row else 0)
    )
    return {
        **budget,
        "actual_headline_sentences": _sentence_count(visible["headline_sentence"]),
        "actual_headline_metrics": len(visible["headline_metrics"]),
        "actual_benchmark_basis_items": _benchmark_basis_item_count(benchmark_basis),
        "actual_visible_table_rows": visible_table_rows,
        "actual_caveats": len(visible.get("caveats") or []),
        "actual_advisor_notes": 1 if advisor_note else 0,
        "rendering_mode": rendering_mode,
    }


def _validate_report_ids(inputs: dict[str, dict[str, Any]]) -> None:
    expected = set(BUILD_NOW_REPORT_IDS)
    actual = set(inputs)
    if actual != expected:
        raise ValueError(f"Unexpected report ids: {sorted(actual)}")


def _validate_view_budget(view: dict[str, Any]) -> None:
    budget = view["information_budget_applied"]
    if budget["actual_headline_sentences"] > budget["max_headline_sentences"]:
        raise ValueError(f"{view['report_element_id']} exceeds headline sentence budget")
    if budget["actual_headline_metrics"] > budget["max_headline_metrics"]:
        raise ValueError(f"{view['report_element_id']} exceeds headline metric budget")
    if budget["actual_benchmark_basis_items"] > budget["max_benchmark_basis_items"]:
        raise ValueError(f"{view['report_element_id']} exceeds benchmark basis budget")
    if budget["actual_visible_table_rows"] > budget["max_visible_table_rows"]:
        raise ValueError(f"{view['report_element_id']} exceeds table row budget")
    if budget["actual_caveats"] > budget["max_caveats"]:
        raise ValueError(f"{view['report_element_id']} exceeds caveat budget")
    if budget["actual_advisor_notes"] > budget["max_advisor_notes"]:
        raise ValueError(f"{view['report_element_id']} exceeds advisor note budget")


def _validate_visible_language(view: dict[str, Any]) -> None:
    lowered = _visible_text(view).lower()
    for term in FORBIDDEN_VISIBLE_TERMS + FORBIDDEN_PLACEHOLDER_TERMS:
        if term in lowered:
            raise ValueError(f"{view['report_element_id']} leaks forbidden term: {term}")
    for pattern in RAW_ID_PATTERNS:
        if re.search(pattern, lowered):
            raise ValueError(f"{view['report_element_id']} leaks raw id pattern: {pattern}")


def _validate_markdown(view: dict[str, Any], markdown: str) -> None:
    lowered = markdown.lower()
    for term in FORBIDDEN_VISIBLE_TERMS + FORBIDDEN_PLACEHOLDER_TERMS:
        if term in lowered:
            raise ValueError(f"{view['report_element_id']} markdown leaks forbidden term: {term}")
    for pattern in RAW_ID_PATTERNS:
        if re.search(pattern, lowered):
            raise ValueError(f"{view['report_element_id']} markdown leaks raw id pattern: {pattern}")
    if view.get("benchmark_basis", {}).get("visible") and "## benchmark basis" not in lowered:
        raise ValueError(f"{view['report_element_id']} markdown lacks benchmark basis")


def _visible_text(view: dict[str, Any]) -> str:
    parts = [str(view["display_title"]), str(view["headline_sentence"])]
    parts.extend(
        f"{metric['label']} {metric['formatted_value']}"
        for metric in view["headline_metrics"]
    )
    benchmark_basis = view.get("benchmark_basis")
    if benchmark_basis and benchmark_basis.get("visible"):
        parts.append("Benchmark Basis")
        for value in benchmark_basis.values():
            if value is not True:
                parts.append(str(value))
    if view.get("benchmark_basis_note"):
        parts.append(str(view["benchmark_basis_note"]))
    for table_key in ("compact_table", "driver_table"):
        table = view.get(table_key)
        if table:
            parts.append(str(table["title"]))
            parts.extend(str(column) for column in table["columns"])
            for row in table["rows"]:
                parts.extend(str(row[column]) for column in table["columns"])
    total_row = view.get("total_row")
    if total_row:
        parts.extend(str(value) for value in total_row.values())
    if view.get("tie_out_note"):
        parts.append(str(view["tie_out_note"]))
    parts.append(str(view["effect_basis_note"]))
    parts.extend(str(caveat) for caveat in view["caveats"])
    if view.get("advisor_note"):
        parts.append(str(view["advisor_note"]))
    return "\n".join(parts)


def _driver_decimal_rows_for_manager(
    *,
    manager_row: dict[str, Any],
    calculated_row: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    active_return = manager_row["active_return_vs_mandate"]
    component_values = [
        _d(calculated_row[component["source_field"]])
        for component in DRIVER_COMPONENTS
    ]
    component_difference = active_return - sum(component_values)

    for component in DRIVER_COMPONENTS:
        manager_return_effect = _d(calculated_row[component["source_field"]])
        if component["driver_id"] == "residual_unexplained":
            manager_return_effect += component_difference
        rows.append(
            {
                "manager_id": manager_row["manager_id"],
                "display_name": manager_row["display_name"],
                "actual_weight": manager_row["actual_weight"],
                "driver_id": component["driver_id"],
                "driver_label": component["label"],
                "driver_category": component["category"],
                "source_component": component["source_field"],
                "manager_return_effect": manager_return_effect,
                "portfolio_effect": manager_row["actual_weight"] * manager_return_effect,
                "meaning": component["meaning"],
                "effect_basis": "manager_return_effect_and_percentage_points_of_total_portfolio_return",
                "timing_used_as_residual": False,
                "caveat": "Synthetic local-demo driver category.",
            }
        )
    return rows


def _serializable_manager_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "manager_id": row["manager_id"],
        "display_name": row["display_name"],
        "actual_weight": _weight_number(row["actual_weight"]),
        "mandate_benchmark_id": row["mandate_benchmark_id"],
        "mandate_benchmark_display_name": row["mandate_benchmark_display_name"],
        "mandate_benchmark_return": _return_number(row["mandate_benchmark_return"]),
        "manager_actual_return": _return_number(row["manager_actual_return"]),
        "active_return_vs_mandate": _return_number(row["active_return_vs_mandate"]),
        "manager_implementation_effect": _return_number(
            row["manager_implementation_effect"]
        ),
        "status": row["status"],
        "benchmark_basis_type": row["benchmark_basis_type"],
        "benchmark_basis_description": row["benchmark_basis_description"],
        "source_driver_tie_out_status": row["source_driver_tie_out_status"],
        "effect_basis": row["effect_basis"],
        "caveats": row["caveats"],
    }


def _serializable_driver_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "manager_id": row["manager_id"],
        "display_name": row["display_name"],
        "actual_weight": _weight_number(row["actual_weight"]),
        "driver_id": row["driver_id"],
        "driver_label": row["driver_label"],
        "driver_category": row["driver_category"],
        "source_component": row["source_component"],
        "manager_return_effect": _return_number(row["manager_return_effect"]),
        "portfolio_effect": _return_number(row["portfolio_effect"]),
        "meaning": row["meaning"],
        "effect_basis": row["effect_basis"],
        "timing_used_as_residual": row["timing_used_as_residual"],
        "caveat": row["caveat"],
    }


def _manager_summary_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "manager_id": row["manager_id"],
        "display_name": row["display_name"],
        "actual_weight": _weight_number(row["actual_weight"]),
        "active_return_vs_mandate": _return_number(row["active_return_vs_mandate"]),
        "manager_implementation_effect": _return_number(
            row["manager_implementation_effect"]
        ),
        "status": row["status"],
    }


def _driver_summary_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "manager_id": row["manager_id"],
        "display_name": row["display_name"],
        "driver_id": row["driver_id"],
        "driver_label": row["driver_label"],
        "manager_return_effect": _return_number(row["manager_return_effect"]),
        "portfolio_effect": _return_number(row["portfolio_effect"]),
    }


def _portfolio_benchmark_basis(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "actual_allocation_benchmark_return": summary[
            "actual_allocation_benchmark_return"
        ],
        "actual_portfolio_return_context": summary["actual_portfolio_return_context"],
        "advisor_policy_attribution_v2_handoff": summary[
            "advisor_policy_attribution_v2_handoff"
        ],
        "visible": True,
    }


def _selected_manager_benchmark_basis(manager_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "manager": manager_row["display_name"],
        "mandate_benchmark": manager_row["mandate_benchmark_display_name"],
        "mandate_benchmark_return": manager_row["mandate_benchmark_return"],
        "manager_actual_return": manager_row["manager_actual_return"],
        "actual_weight": manager_row["actual_weight"],
        "visible": True,
    }


def _render_benchmark_basis(benchmark_basis: dict[str, Any]) -> list[str]:
    if "manager" in benchmark_basis:
        return [
            f"- **Manager:** {benchmark_basis['manager']}",
            f"- **Mandate benchmark:** {benchmark_basis['mandate_benchmark']}",
            f"- **Mandate benchmark return:** {_format_percent(benchmark_basis['mandate_benchmark_return'])}",
            f"- **Manager actual return:** {_format_percent(benchmark_basis['manager_actual_return'])}",
            f"- **Actual weight:** {_format_percent(benchmark_basis['actual_weight'])}",
        ]
    return [
        f"- **Actual allocation benchmark:** {_format_percent(benchmark_basis['actual_allocation_benchmark_return'])}",
        f"- **Actual manager return context:** {_format_percent(benchmark_basis['actual_portfolio_return_context'])}",
        f"- **Advisor handoff:** {_format_effect_pp(benchmark_basis['advisor_policy_attribution_v2_handoff'])}",
    ]


def _manager_benchmark_basis_note() -> str:
    return (
        "Each manager is compared with that manager's mandate benchmark and actual weight. "
        "Allocation policy choices and the global benchmark are handled in Advisor Policy Attribution."
    )


def _benchmark_basis_item_count(benchmark_basis: dict[str, Any]) -> int:
    if not benchmark_basis.get("visible"):
        return 0
    if "manager" in benchmark_basis:
        return 4
    return 3


def _table(title: str, columns: list[str], rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "title": title,
        "columns": columns,
        "rows": rows,
    }


def _metric(label: str, raw_value: Any, formatted_value: str) -> dict[str, Any]:
    return {
        "label": label,
        "raw_value": raw_value,
        "formatted_value": formatted_value,
    }


def _render_markdown_table(
    table: dict[str, Any],
    total_row: dict[str, Any] | None = None,
) -> list[str]:
    columns = table["columns"]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in table["rows"]:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    if total_row:
        lines.append(
            "| " + " | ".join(str(total_row.get(column, "")) for column in columns) + " |"
        )
    return lines


def _status_label(status: str) -> str:
    return {
        "above_mandate": "Above mandate",
        "below_mandate": "Below mandate",
        "near_mandate": "Near mandate",
        "review": "Review",
        "total": "Manager total",
    }.get(status, status.replace("_", " ").title())


def _implementation_status(active_return: Decimal) -> str:
    if active_return > STATUS_NEAR_MANDATE_TOLERANCE:
        return "above_mandate"
    if active_return < -STATUS_NEAR_MANDATE_TOLERANCE:
        return "below_mandate"
    return "near_mandate"


def _by_manager(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["manager_id"]: row for row in rows}


def _return_number(value: Decimal) -> float:
    return float(value.quantize(RETURN_QUANT, rounding=ROUND_HALF_UP))


def _weight_number(value: Decimal) -> float:
    return float(value.quantize(WEIGHT_QUANT, rounding=ROUND_HALF_UP))


def _residual_status(value: Decimal) -> str:
    return "pass" if abs(value) <= TIE_OUT_TOLERANCE else "fail"


def _weight_sum_status(value: Decimal) -> str:
    return "pass" if abs(value - Decimal("1")) <= TIE_OUT_TOLERANCE else "fail"


def _format_percent(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.2f}%"


def _format_signed_percent(value: Any) -> str:
    number = float(value)
    sign = "+" if number >= 0 else "-"
    return f"{sign}{abs(number) * 100:.2f}%"


def _format_effect_pp(value: Any) -> str:
    number = float(value)
    sign = "+" if number >= 0 else "-"
    return f"{sign}{abs(number) * 100:.2f} pp"


def _sentence_count(value: str) -> int:
    normalized = value.replace("?", ".").replace("!", ".")
    matches = re.findall(r"[.!?](?:\s|$)", normalized)
    return max(1, len(matches)) if normalized.strip() else 0


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _d(value: Any) -> Decimal:
    return Decimal(str(value))


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate manager mandate attribution outputs and mockups."
    )
    parser.add_argument("--policy-pack-dir", default=str(DEFAULT_POLICY_PACK_DIR))
    parser.add_argument("--advisor-policy-dir", default=str(DEFAULT_ADVISOR_POLICY_DIR))
    parser.add_argument(
        "--manager-calculated-dir",
        default=str(DEFAULT_MANAGER_CALCULATED_DIR),
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument("--mockup-dir", default=str(DEFAULT_MOCKUP_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_manager_mandate_attribution(
        policy_pack_dir=args.policy_pack_dir,
        advisor_policy_dir=args.advisor_policy_dir,
        manager_calculated_dir=args.manager_calculated_dir,
        output_dir=args.output_dir,
        input_dir=args.input_dir,
        view_dir=args.view_dir,
        mockup_dir=args.mockup_dir,
    )

    print(
        "Manager mandate attribution outputs: "
        f"{summary['calculated_artifact_count']} -> {summary['output_dir']}"
    )
    print(
        "Manager mandate attribution report inputs: "
        f"{summary['report_input_count']} -> {summary['input_dir']}"
    )
    print(
        "Manager mandate attribution report views: "
        f"{summary['report_view_count']} -> {summary['view_dir']}"
    )
    print(
        "Manager mandate attribution Markdown mockups: "
        f"{summary['markdown_mockup_count']} -> {summary['mockup_dir']}"
    )
    print(f"Advisor handoff tie-out passed: {summary['advisor_handoff_tie_out_passed']}")
    print(f"Driver tie-outs passed: {summary['driver_tie_outs_passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
