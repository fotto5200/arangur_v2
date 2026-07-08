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
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/attribution_v1")


def build_attribution_methodology_audit(
    *,
    prerequisite_dir: str | Path = DEFAULT_PREREQUISITE_DIR,
    view_dir: str | Path = DEFAULT_VIEW_DIR,
) -> dict[str, Any]:
    root = Path(prerequisite_dir)
    views_root = Path(view_dir)
    benchmark_catalog = _load_json(root / "portfolio_benchmark_catalog.json")
    period_returns = _load_json(root / "synthetic_period_returns.json")
    weights_flows = _load_json(root / "synthetic_attribution_weights_flows.json")
    decomposition = _load_json(root / "integrated_attribution_decomposition_inputs.json")
    manager_prerequisites = _load_json(root / "manager_attribution_prerequisites.json")
    readiness = _load_json(root / "attribution_readiness_summary.json")
    summary_view = _load_json(views_root / "integrated_performance_attribution_summary_view.json")
    detail_view = _load_json(views_root / "integrated_performance_attribution_detail_view.json")
    manager_view = _load_json(views_root / "manager_attribution_summary_view.json")

    whole = next(
        row
        for row in decomposition["supported_modes"]
        if row["mode"] == "whole_portfolio"
    )
    detail = whole["theme_benchmark_detail"]
    summary_effects = whole["effects"]
    not_measured_count = _count_not_separately_measured(detail_view)

    manager_benchmark_basis = {
        "current_basis": "manager_specific_synthetic_benchmark_proxy",
        "classification": "supplied_synthetic_input_needs_basis_clarification",
        "manager_count": len(manager_prerequisites["managers"]),
        "all_current_managers_covered": manager_prerequisites["coverage_summary"][
            "all_current_managers_covered"
        ],
        "disclosure_gap": (
            "Each manager has a synthetic benchmark return, but the artifact does not yet "
            "state whether each benchmark is a mandate benchmark, broad policy benchmark, "
            "or weighted theme-benchmark blend."
        ),
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
        "period_start": readiness["period_start"],
        "period_end": readiness["period_end"],
        "field_classification": {
            "global_benchmark_return": {
                "value": period_returns["benchmark_return"]["period_return"],
                "classification": "derived_by_simple_arithmetic",
                "source": "weighted synthetic manager benchmark returns",
                "current_status": "reproducible_from_current_synthetic_inputs",
            },
            "portfolio_return": {
                "value": period_returns["portfolio_return"]["period_return"],
                "classification": "derived_by_simple_arithmetic",
                "source": "weighted synthetic manager returns",
                "current_status": "reproducible_from_current_synthetic_inputs",
            },
            "theme_benchmark_return": {
                "classification": "supplied_synthetic_input",
                "source": "lens bucket benchmark proxy map and synthetic period returns",
                "current_status": "explicit_but_not_market_calculated",
            },
            "theme_bucket_relative_contribution": {
                "value": detail["theme_bucket_total_effect"],
                "classification": "derived_by_simple_arithmetic",
                "formula": "theme bucket weight * (portfolio bucket return - theme benchmark return)",
                "current_status": "reproducible_from_current_synthetic_inputs",
            },
            "theme_benchmark_selection_effect": {
                "value": summary_effects["strategy_lens_bucket_selection_effect"],
                "classification": "supplied_formula_allocation",
                "formula": "active return * fixed synthetic share",
                "current_status": "not_lower_level_calculated",
            },
            "theme_benchmark_sizing_effect": {
                "value": summary_effects["strategy_lens_bucket_sizing_effect"],
                "classification": "supplied_formula_allocation",
                "formula": "active return * fixed synthetic share",
                "current_status": "not_lower_level_calculated",
            },
            "asset_selection_effect": {
                "value": summary_effects["asset_selection_effect"],
                "classification": "supplied_formula_allocation",
                "formula": "active return * fixed synthetic share",
                "current_status": "not_lower_level_calculated",
            },
            "asset_sizing_effect": {
                "value": summary_effects["asset_sizing_effect"],
                "classification": "supplied_formula_allocation",
                "formula": "active return * fixed synthetic share",
                "current_status": "not_lower_level_calculated",
            },
            "manager_benchmark_return": {
                "classification": "supplied_synthetic_input",
                "source": "manager-specific synthetic benchmark proxy returns",
                "current_status": "explicit_values_need_benchmark_type_disclosure",
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
            "residual_unexplained": {
                "value": summary_effects["residual_unexplained"],
                "classification": "derived_reconciler",
                "formula": "active return - measured or supplied effects",
                "current_status": "reconciler_may_include_unmeasured_effects",
            },
        },
        "artifact_audit": {
            "portfolio_benchmark_catalog": "presentation and benchmark metadata; synthetic_return is copied from derived benchmark return",
            "lens_bucket_benchmark_proxy_map": "supplied synthetic theme benchmark/proxy metadata and returns",
            "synthetic_period_returns": "mixed: portfolio and global benchmark returns are weighted arithmetic; manager, proxy, bucket, and selected position returns are synthetic inputs",
            "synthetic_attribution_weights_flows": "weights are derived from synthetic base value shares; cash-flow section is readiness metadata",
            "integrated_attribution_decomposition_inputs": "mixed: active return and tie-outs are arithmetic; summary effects are fixed-share synthetic allocation; theme-bucket total effects are arithmetic; component columns are not separately measured",
            "manager_attribution_prerequisites": "mixed: manager relative return and contribution are arithmetic; component effects are fixed-share synthetic allocation; benchmark type needs clarification",
            "attribution_readiness_summary": "readiness metadata",
            "attribution_v1_report_views": "presentation metadata generated from prerequisite fields; not a calculation source",
        },
        "tie_out_status": {
            "whole_portfolio_ties_to_actual_return": whole["tie_out"]["ties_to_actual_return"],
            "summary_effects_sum": summary_view["table_validation"]["effects_sum"],
            "active_return": whole["active_return"],
            "theme_detail_ties_to_active_return": detail["tie_out"]["ties_to_active_return"],
            "detail_effect_total": detail_view["table_validation"]["effect_total"],
            "manager_rows_covered": manager_view["table_validation"]["manager_rows_shown"],
        },
        "timing_policy": {
            "timing_status": readiness["timing_attribution_readiness"]["status"],
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
            "summary_effects_are_not_lower_level_calculated": True,
            "detail_component_fields_not_separately_measured": not_measured_count,
            "manager_benchmark_basis_needs_explicit_type": True,
            "manager_component_effects_are_not_lower_level_calculated": True,
            "theme_benchmark_selection_portfolio_missing": True,
            "theme_benchmark_sizing_portfolio_missing": True,
            "per_theme_asset_benchmark_inputs_missing": True,
        },
        "manager_benchmark_basis": manager_benchmark_basis,
        "missing_inputs_for_calculated_attribution": [
            "selected attribution lens id and approved rationale",
            "theme benchmark portfolio policy weights",
            "theme benchmark portfolio equal-weight or policy-weight return",
            "actual-weight theme benchmark portfolio return",
            "per-theme asset lists and weights",
            "per-theme asset benchmark or reference returns",
            "manager benchmark type for every manager",
            "manager-level theme weights if manager benchmarks blend theme benchmarks",
            "explicit residual calculation policy and tolerance",
        ],
        "recommended_next_tranche": "Synthetic Attribution Calculation Inputs v1",
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
