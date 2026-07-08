from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


AUDIT_SCHEMA_VERSION = "attribution_methodology_audit_summary.v1"
AUDIT_VERSION = "attribution_methodology_audit.v1"

DEFAULT_PREREQUISITE_DIR = Path(
    "data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1"
)
DEFAULT_CALCULATED_DIR = Path(
    "data/simulation/attribution_calculated/synthetic_attribution_engine_v1"
)
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/attribution_v1")


def build_attribution_methodology_audit(
    *,
    prerequisite_dir: str | Path = DEFAULT_PREREQUISITE_DIR,
    calculated_dir: str | Path = DEFAULT_CALCULATED_DIR,
    view_dir: str | Path = DEFAULT_VIEW_DIR,
) -> dict[str, Any]:
    root = Path(prerequisite_dir)
    calculated_root = Path(calculated_dir)
    views_root = Path(view_dir)
    readiness = _load_json(root / "attribution_readiness_summary.json")
    calculated_manifest = _load_json(
        calculated_root / "calculated_attribution_engine_manifest.json"
    )
    whole_calculated = _load_json(
        calculated_root / "whole_portfolio_calculated_attribution_summary.json"
    )
    theme_detail_calculated = _load_json(
        calculated_root / "theme_benchmark_calculated_detail.json"
    )
    manager_calculated = _load_json(
        calculated_root / "manager_calculated_attribution_summary.json"
    )
    quality_summary = _load_json(
        calculated_root / "calculated_attribution_quality_summary.json"
    )
    summary_view = _load_json(views_root / "integrated_performance_attribution_summary_view.json")
    detail_view = _load_json(views_root / "integrated_performance_attribution_detail_view.json")
    manager_view = _load_json(views_root / "manager_attribution_summary_view.json")

    not_measured_count = _count_not_separately_measured(detail_view)
    selected_lens = whole_calculated["selected_attribution_lens"]["display_name"]
    manager_basis_types = sorted(
        {
            manager["manager_benchmark_basis_type"]
            for manager in manager_calculated["managers"]
        }
    )

    manager_benchmark_basis = {
        "current_basis": "hybrid_synthetic_demo",
        "classification": "explicit_synthetic_demo_basis",
        "manager_count": manager_calculated["manager_count"],
        "manager_benchmark_basis_types": manager_basis_types,
        "all_current_managers_covered": manager_calculated["coverage_summary"][
            "all_current_managers_covered"
        ],
        "all_manager_benchmark_basis_types_explicit": manager_calculated[
            "coverage_summary"
        ]["all_manager_benchmark_basis_types_explicit"],
        "disclosure_gap": None,
        "basis_description": manager_calculated["managers"][0][
            "benchmark_basis_description"
        ],
    }

    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "audit_version": AUDIT_VERSION,
        "synthetic_data": True,
        "local_only": True,
        "external_data_used": False,
        "live_market_data_used": False,
        "real_client_data_used": False,
        "prerequisite_pack_id": readiness["pack_id"],
        "calculated_output_engine_id": calculated_manifest["engine_id"],
        "calculated_outputs_source_of_truth": True,
        "selected_attribution_lens": selected_lens,
        "period_start": readiness["period_start"],
        "period_end": readiness["period_end"],
        "field_classification": {
            "global_benchmark_return": {
                "value": whole_calculated["global_benchmark_return"],
                "classification": "calculated_from_synthetic_inputs",
                "source": "whole_portfolio_calculated_attribution_summary",
                "current_status": "reproducible_from_current_synthetic_inputs",
            },
            "portfolio_return": {
                "value": whole_calculated["actual_portfolio_return"],
                "classification": "calculated_from_synthetic_inputs",
                "source": "whole_portfolio_calculated_attribution_summary",
                "current_status": "reproducible_from_current_synthetic_inputs",
            },
            "theme_benchmark_return": {
                "classification": "calculated_from_synthetic_theme_benchmark_inputs",
                "source": "theme_benchmark_calculated_detail",
                "current_status": "calculated_for_selected_ai_adoption_lens",
            },
            "theme_bucket_relative_contribution": {
                "value": theme_detail_calculated["totals"]["total_effect"],
                "classification": "calculated_from_lower_level_inputs",
                "formula": "sum of calculated theme benchmark and asset effects",
                "current_status": "calculated_from_current_synthetic_inputs",
            },
            "theme_benchmark_selection_effect": {
                "value": whole_calculated["theme_benchmark_selection_effect"],
                "classification": "calculated_from_lower_level_inputs",
                "formula": (
                    "policy or equal-weight theme benchmark return minus global "
                    "benchmark return"
                ),
                "current_status": "calculated_from_current_synthetic_inputs",
            },
            "theme_benchmark_sizing_effect": {
                "value": whole_calculated["theme_benchmark_sizing_effect"],
                "classification": "calculated_from_lower_level_inputs",
                "formula": (
                    "actual-weight theme benchmark return minus policy or "
                    "equal-weight theme benchmark return"
                ),
                "current_status": "calculated_from_current_synthetic_inputs",
            },
            "asset_selection_effect": {
                "value": whole_calculated["asset_selection_effect"],
                "classification": "calculated_from_lower_level_inputs",
                "formula": "calculated from per-theme reference-weight asset returns",
                "current_status": "calculated_from_current_synthetic_inputs",
            },
            "asset_sizing_effect": {
                "value": whole_calculated["asset_sizing_effect"],
                "classification": "calculated_from_lower_level_inputs",
                "formula": "calculated from per-theme actual-weight asset returns",
                "current_status": "calculated_from_current_synthetic_inputs",
            },
            "manager_benchmark_return": {
                "classification": "explicit_synthetic_demo_benchmark_basis",
                "source": "manager_calculated_attribution_summary",
                "current_status": "basis_type_explicit_for_current_managers",
            },
            "manager_relative_return": {
                "classification": "derived_by_simple_arithmetic",
                "formula": "manager return - manager benchmark return",
                "current_status": "reproducible_from_current_synthetic_inputs",
            },
            "manager_portfolio_contribution": {
                "classification": "derived_by_simple_arithmetic",
                "formula": "manager portfolio weight * manager relative return",
                "current_status": "reproducible_from_current_synthetic_inputs",
            },
            "manager_component_effects": {
                "classification": "calculated_from_lower_level_inputs",
                "source": "manager_calculated_attribution_summary",
                "current_status": "calculated_for_current_manager_rows",
            },
            "residual_unexplained": {
                "value": whole_calculated["residual_unexplained"],
                "classification": "derived_reconciler",
                "formula": "relative return minus visible calculated attribution effects",
                "current_status": "calculated_reconciler_not_timing",
            },
        },
        "artifact_audit": {
            "portfolio_benchmark_catalog": "presentation and benchmark metadata; synthetic_return is copied from derived benchmark return",
            "lens_bucket_benchmark_proxy_map": "supplied synthetic theme benchmark/proxy metadata and returns",
            "synthetic_period_returns": "mixed: portfolio and global benchmark returns are weighted arithmetic; manager, proxy, bucket, and selected position returns are synthetic inputs",
            "synthetic_attribution_weights_flows": "weights are derived from synthetic base value shares; cash-flow section is readiness metadata",
            "integrated_attribution_decomposition_inputs": "historical prerequisite artifact retained for audit; no longer the report source of truth for calculated-supported attribution_v1 fixtures",
            "manager_attribution_prerequisites": "historical prerequisite artifact retained for audit; calculated manager outputs now carry benchmark-basis disclosure",
            "calculated_attribution_outputs": "current source of truth for local attribution_v1 inputs, views, and mockups where calculated outputs exist",
            "attribution_readiness_summary": "readiness metadata",
            "attribution_v1_report_views": "presentation metadata generated from calculated outputs for supported local reports; not a calculation source",
        },
        "tie_out_status": {
            "whole_portfolio_ties_to_actual_return": whole_calculated["tie_out"][
                "ties_to_actual_portfolio_return"
            ],
            "summary_effects_sum": summary_view["table_validation"]["effects_sum"],
            "relative_return": whole_calculated["relative_return"],
            "theme_detail_ties_to_summary_calculated_effects": theme_detail_calculated[
                "tie_out_status"
            ]["ties_to_summary_calculated_effects"],
            "detail_effect_total": detail_view["table_validation"]["theme_row_total_effect"],
            "detail_residual_unexplained": detail_view["table_validation"][
                "residual_unexplained"
            ],
            "manager_rows_covered": manager_view["table_validation"]["manager_rows_shown"],
            "manager_tie_outs_reconcile": manager_calculated["coverage_summary"][
                "manager_tie_outs_reconcile"
            ],
        },
        "timing_policy": {
            "timing_status": whole_calculated["timing_status"],
            "timing_contribution_included": False,
            "residual_is_timing": False,
            "required_before_timing": [
                "beginning holdings",
                "ending holdings",
                "trade dates",
                "external flows",
                "prices through the period",
                "approved comparison portfolio convention",
            ],
        },
        "calculation_gaps": {
            "summary_effects_are_calculated_from_lower_level_inputs": True,
            "summary_effects_are_not_lower_level_calculated": False,
            "detail_component_fields_not_separately_measured": not_measured_count,
            "detail_component_effects_calculated": detail_view["table_validation"][
                "component_effects_calculated"
            ],
            "manager_benchmark_basis_needs_explicit_type": False,
            "manager_component_effects_are_not_lower_level_calculated": False,
            "manager_component_effects_calculated": True,
            "theme_benchmark_selection_portfolio_missing": False,
            "theme_benchmark_sizing_portfolio_missing": False,
            "per_theme_asset_benchmark_inputs_missing": False,
            "energy_security_calculated_outputs_missing": True,
            "timing_inputs_missing": True,
            "production_data_missing": True,
            "real_client_data_missing": True,
        },
        "manager_benchmark_basis": manager_benchmark_basis,
        "calculated_output_readiness": {
            "summary_ready_from_calculated_outputs": quality_summary[
                "summary_ready_from_calculated_outputs"
            ],
            "detail_ready_from_calculated_outputs": quality_summary[
                "detail_ready_from_calculated_outputs"
            ],
            "manager_ready_from_calculated_outputs": quality_summary[
                "manager_ready_from_calculated_outputs"
            ],
            "supported_lenses": [selected_lens],
            "unsupported_calculated_lenses": ["Energy Security"],
        },
        "missing_inputs_for_calculated_attribution": [
            "Energy Security calculation inputs and calculated attribution outputs",
            "production benchmark, return, holding, and flow data",
            "real client data and approval controls",
            "clean trade, holding, price, and external-flow history for timing attribution",
            "approved timing methodology and comparison-portfolio convention",
        ],
        "recommended_next_tranche": "Frank Review of Regenerated Calculated Attribution Mockups v1",
    }


def _count_not_separately_measured(detail_view: dict[str, Any]) -> int:
    table = detail_view["compact_table"]
    count = 0
    for row in table["rows"]:
        for value in row.values():
            if value == "Not separately measured":
                count += 1
    return count


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit current synthetic attribution calculation provenance."
    )
    parser.add_argument("--prerequisite-dir", default=str(DEFAULT_PREREQUISITE_DIR))
    parser.add_argument("--calculated-dir", default=str(DEFAULT_CALCULATED_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path for writing the audit summary JSON. Omit for read-only stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = build_attribution_methodology_audit(
        prerequisite_dir=args.prerequisite_dir,
        calculated_dir=args.calculated_dir,
        view_dir=args.view_dir,
    )
    if args.output:
        _write_json(Path(args.output), summary)
        print(f"Attribution methodology audit summary written: {args.output}")
    else:
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
