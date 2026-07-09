from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-08T00:00:00Z"

ENGINE_ID = "policy_level_attribution_engine_v1"
ENGINE_VERSION = "2026-07-08"
GENERATOR_VERSION = "policy_level_attribution.v1"

CALCULATION_SCHEMA_VERSION = "policy_level_attribution_calculated_output.v1"
REPORT_INPUT_SCHEMA_VERSION = "policy_attribution_report_input.v1"
REPORT_INPUT_INDEX_SCHEMA_VERSION = "policy_attribution_report_input_index.v1"
REPORT_VIEW_SCHEMA_VERSION = "policy_attribution_report_view.v1"
REPORT_VIEW_INDEX_SCHEMA_VERSION = "policy_attribution_report_view_index.v1"
GATED_INDEX_SCHEMA_VERSION = "policy_attribution_gated_deferred_index.v1"

DEFAULT_POLICY_PACK_DIR = Path(
    "data/simulation/policy_mandate_prerequisites/synthetic_policy_mandate_pack_v1"
)
DEFAULT_ATTRIBUTION_OUTPUT_DIR = Path(
    "data/simulation/attribution_calculated/synthetic_attribution_engine_v1"
)
DEFAULT_OUTPUT_DIR = Path("data/simulation/policy_level_attribution") / ENGINE_ID
DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs/policy_attribution_v1")
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/policy_attribution_v1")
DEFAULT_MOCKUP_DIR = Path("docs/product/report_mockups/policy_attribution_v1")

RETURN_QUANT = Decimal("0.000000001")
WEIGHT_QUANT = Decimal("0.000001")
TIE_OUT_TOLERANCE = Decimal("0.000001")

POLICY_PACK_FILES = {
    "manifest": "synthetic_policy_mandate_pack_manifest.json",
    "policy_allocation_mode": "policy_allocation_mode.json",
    "policy_allocation_profile": "policy_allocation_profile.json",
    "actual_manager_allocation_snapshot": "actual_manager_allocation_snapshot.json",
    "allocation_drift_summary": "allocation_drift_summary.json",
    "imputed_current_allocation_baseline": "imputed_current_allocation_baseline.json",
    "manager_mandate_benchmark_catalog": "manager_mandate_benchmark_catalog.json",
    "manager_benchmark_basis_map": "manager_benchmark_basis_map.json",
    "policy_level_attribution_inputs": "policy_level_attribution_inputs.json",
    "equal_weight_diagnostic_attribution_classification": (
        "equal_weight_diagnostic_attribution_classification.json"
    ),
    "policy_mandate_readiness_summary": "policy_mandate_readiness_summary.json",
}

ATTRIBUTION_OUTPUT_FILES = {
    "whole_portfolio_calculated_attribution_summary": (
        "whole_portfolio_calculated_attribution_summary.json"
    ),
    "manager_calculated_attribution_summary": "manager_calculated_attribution_summary.json",
}

CALCULATED_ARTIFACT_FILES = {
    "manifest": "policy_level_attribution_manifest.json",
    "summary": "policy_level_attribution_summary.json",
    "bridge": "policy_level_attribution_bridge.json",
    "manager_rows": "policy_level_manager_effect_rows.json",
    "imputed_variant": "policy_level_attribution_imputed_baseline_variant.json",
    "quality_summary": "policy_level_attribution_quality_summary.json",
}

REPORT_SPECS: tuple[dict[str, str], ...] = (
    {
        "report_id": "policy_level_attribution_summary",
        "input_filename": "policy_level_attribution_summary_input.json",
        "view_filename": "policy_level_attribution_summary_view.json",
        "mockup_filename": "policy_level_attribution_summary_mockup_v1.md",
    },
    {
        "report_id": "policy_level_manager_effect_detail",
        "input_filename": "policy_level_manager_effect_detail_input.json",
        "view_filename": "policy_level_manager_effect_detail_view.json",
        "mockup_filename": "policy_level_manager_effect_detail_mockup_v1.md",
    },
    {
        "report_id": "imputed_baseline_policy_attribution_variant",
        "input_filename": "imputed_baseline_policy_attribution_variant_input.json",
        "view_filename": "imputed_baseline_policy_attribution_variant_view.json",
        "mockup_filename": "imputed_baseline_policy_attribution_variant_mockup_v1.md",
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
        "report_id": "within_manager_attribution_detail",
        "display_title": "Within-Manager Attribution Detail",
        "status": "Future tranche",
        "reason": "Requires separate manager-driver report design and lower-level inputs.",
    },
    {
        "report_id": "blended_all_in_attribution",
        "display_title": "Blended / All-In Attribution",
        "status": "Deferred",
        "reason": "Deferred until separate policy-level and manager-level reports are understood.",
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
        "report_id": "production_client_attribution",
        "display_title": "Production Client Attribution",
        "status": "Gated",
        "reason": (
            "Gated on approved real policy targets, real benchmarks, and production review."
        ),
    },
    {
        "report_id": "current_vs_proposed_policy_attribution",
        "display_title": "Current-vs-Proposed Policy Attribution",
        "status": "Gated",
        "reason": "Gated on a proposed allocation workflow.",
    },
)

DEFAULT_INFORMATION_BUDGET = {
    "max_headline_sentences": 1,
    "max_headline_metrics": 3,
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
    "equal-weight",
    "blame",
    "at fault",
    "bad allocation",
    "wrong allocation",
    "manager failed",
    "advisor failed",
    "full within-manager",
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


def load_source_context(
    *,
    policy_pack_dir: str | Path = DEFAULT_POLICY_PACK_DIR,
    attribution_output_dir: str | Path = DEFAULT_ATTRIBUTION_OUTPUT_DIR,
) -> dict[str, Any]:
    policy_root = Path(policy_pack_dir)
    attribution_root = Path(attribution_output_dir)
    policy_pack = {
        name: _load_json(policy_root / filename)
        for name, filename in POLICY_PACK_FILES.items()
    }
    attribution_outputs = {
        name: _load_json(attribution_root / filename)
        for name, filename in ATTRIBUTION_OUTPUT_FILES.items()
    }

    manifest = policy_pack["manifest"]
    profile = policy_pack["policy_allocation_profile"]
    policy_inputs = policy_pack["policy_level_attribution_inputs"]
    readiness = policy_pack["policy_mandate_readiness_summary"]
    equal_weight = policy_pack["equal_weight_diagnostic_attribution_classification"]

    if manifest["pack_id"] != "synthetic_policy_mandate_pack_v1":
        raise ValueError("Unexpected policy mandate pack id")
    if not manifest["synthetic_data"] or not manifest["local_only"]:
        raise ValueError("Policy-level attribution requires local synthetic inputs")
    if profile["allocation_mode"] != "explicit_policy_allocation":
        raise ValueError("Primary policy-level attribution requires explicit policy allocation")
    if not policy_inputs["synthetic_data"] or not policy_inputs["local_only"]:
        raise ValueError("Policy-level attribution input scaffold must be local synthetic")
    if readiness["policy_level_attribution_input_readiness"] not in {
        "input_scaffold_ready_engine_needed",
        "calculated_engine_ready",
    }:
        raise ValueError("Policy-level attribution inputs are not ready")
    if equal_weight["default_policy_benchmark"] is not False:
        raise ValueError("Equal-weight diagnostic must not be the default policy benchmark")

    return {
        "policy_pack_dir": _as_posix(policy_root),
        "attribution_output_dir": _as_posix(attribution_root),
        "policy_pack": policy_pack,
        "attribution_outputs": attribution_outputs,
        "source_paths": {
            name: _as_posix(policy_root / filename)
            for name, filename in POLICY_PACK_FILES.items()
        },
        "attribution_source_paths": {
            name: _as_posix(attribution_root / filename)
            for name, filename in ATTRIBUTION_OUTPUT_FILES.items()
        },
    }


def calculate_policy_level_attribution(context: dict[str, Any]) -> dict[str, Any]:
    pack = context["policy_pack"]
    policy_inputs = pack["policy_level_attribution_inputs"]
    profile = pack["policy_allocation_profile"]
    actual_snapshot = pack["actual_manager_allocation_snapshot"]
    drift_summary = pack["allocation_drift_summary"]
    benchmark_catalog = pack["manager_mandate_benchmark_catalog"]
    basis_map = pack["manager_benchmark_basis_map"]
    whole_calculated = context["attribution_outputs"][
        "whole_portfolio_calculated_attribution_summary"
    ]

    profile_by_manager = _by_manager(profile["manager_sleeve_target_allocation"])
    actual_by_manager = _by_manager(actual_snapshot["manager_rows"])
    drift_by_manager = _by_manager(drift_summary["manager_rows"])
    benchmark_by_manager = _by_manager(benchmark_catalog["benchmark_rows"])
    basis_by_manager = _by_manager(basis_map["rows"])
    input_rows = policy_inputs["input_rows"]

    decimal_rows: list[dict[str, Any]] = []
    for input_row in input_rows:
        manager_id = input_row["manager_id"]
        profile_row = profile_by_manager[manager_id]
        actual_row = actual_by_manager[manager_id]
        drift_row = drift_by_manager[manager_id]
        benchmark_row = benchmark_by_manager[manager_id]
        basis_row = basis_by_manager[manager_id]

        target_weight = _d(profile_row["target_weight"])
        actual_weight = _d(actual_row["actual_weight"])
        weight_drift = actual_weight - target_weight
        mandate_benchmark_return = _d(benchmark_row["synthetic_period_return"])
        manager_actual_return = _d(input_row["manager_actual_return"])
        target_benchmark_effect = target_weight * mandate_benchmark_return
        actual_allocation_benchmark_effect = actual_weight * mandate_benchmark_return
        allocation_drift_effect = weight_drift * mandate_benchmark_return
        manager_implementation_effect = actual_weight * (
            manager_actual_return - mandate_benchmark_return
        )
        actual_portfolio_effect = actual_weight * manager_actual_return

        decimal_rows.append(
            {
                "manager_id": manager_id,
                "manager_sleeve": input_row["display_name"],
                "target_weight": target_weight,
                "actual_weight": actual_weight,
                "weight_drift": weight_drift,
                "mandate_benchmark_return": mandate_benchmark_return,
                "manager_actual_return": manager_actual_return,
                "target_benchmark_return_effect": target_benchmark_effect,
                "actual_allocation_benchmark_effect": (
                    actual_allocation_benchmark_effect
                ),
                "allocation_drift_effect": allocation_drift_effect,
                "manager_implementation_effect": manager_implementation_effect,
                "actual_portfolio_effect": actual_portfolio_effect,
                "drift_status": drift_row["drift_status"],
                "benchmark_basis": benchmark_row["mandate_benchmark_display_name"],
                "benchmark_basis_type": basis_row["benchmark_basis_type"],
                "caveats": [
                    "Synthetic local-demo mandate benchmark basis.",
                    "Manager effect is measured only on actual capital assigned to the manager.",
                ],
            }
        )

    target_policy_benchmark_return = sum(
        row["target_benchmark_return_effect"] for row in decimal_rows
    )
    actual_allocation_benchmark_return = sum(
        row["actual_allocation_benchmark_effect"] for row in decimal_rows
    )
    actual_portfolio_return = sum(row["actual_portfolio_effect"] for row in decimal_rows)
    global_benchmark_return = _d(policy_inputs["global_benchmark_return"])
    policy_design_effect = target_policy_benchmark_return - global_benchmark_return
    allocation_drift_effect = (
        actual_allocation_benchmark_return - target_policy_benchmark_return
    )
    manager_implementation_effect = (
        actual_portfolio_return - actual_allocation_benchmark_return
    )
    total_relative_effect = actual_portfolio_return - global_benchmark_return
    residual = (
        total_relative_effect
        - policy_design_effect
        - allocation_drift_effect
        - manager_implementation_effect
    )

    summary = {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "global_benchmark_return": _return_number(global_benchmark_return),
        "target_policy_benchmark_return": _return_number(
            target_policy_benchmark_return
        ),
        "actual_allocation_benchmark_return": _return_number(
            actual_allocation_benchmark_return
        ),
        "actual_portfolio_return": _return_number(actual_portfolio_return),
        "policy_design_effect": _return_number(policy_design_effect),
        "allocation_drift_effect": _return_number(allocation_drift_effect),
        "manager_implementation_effect": _return_number(
            manager_implementation_effect
        ),
        "total_relative_effect": _return_number(total_relative_effect),
        "residual": _return_number(residual),
        "residual_status": _residual_status(residual),
        "effect_basis": "percentage_points_of_total_portfolio_return",
        "headline_interpretation": (
            "The policy bridge ties to actual portfolio return with separated "
            "policy design, allocation drift, and manager implementation effects."
        ),
        "source_actual_portfolio_return_from_calculated_pack": _return_number(
            _d(whole_calculated["actual_portfolio_return"])
        ),
        "source_current_weight_formula_return": _return_number(
            actual_portfolio_return
        ),
        "source_actual_portfolio_return_reconciliation": policy_inputs[
            "manager_current_weight_return_reconciliation"
        ],
        "caveats": [
            "Synthetic demo return attribution only; production use needs approved real targets and benchmarks.",
            "Dollar P&L is gated because no reliable beginning portfolio value is available.",
        ],
    }

    manager_rows = [_serializable_manager_row(row) for row in decimal_rows]
    bridge = _bridge_rows(
        global_benchmark_return=global_benchmark_return,
        target_policy_benchmark_return=target_policy_benchmark_return,
        actual_allocation_benchmark_return=actual_allocation_benchmark_return,
        actual_portfolio_return=actual_portfolio_return,
        policy_design_effect=policy_design_effect,
        allocation_drift_effect=allocation_drift_effect,
        manager_implementation_effect=manager_implementation_effect,
    )
    imputed_variant = _imputed_baseline_variant(
        decimal_rows=decimal_rows,
        global_benchmark_return=global_benchmark_return,
        actual_allocation_benchmark_return=actual_allocation_benchmark_return,
        actual_portfolio_return=actual_portfolio_return,
        manager_implementation_effect=manager_implementation_effect,
    )
    quality_summary = _quality_summary(
        context=context,
        decimal_rows=decimal_rows,
        residual=residual,
        summary=summary,
    )
    manifest = _manifest(context, summary, quality_summary)

    return {
        "manifest": manifest,
        "summary": summary,
        "bridge": bridge,
        "manager_rows": {
            "schema_version": CALCULATION_SCHEMA_VERSION,
            "engine_id": ENGINE_ID,
            "engine_version": ENGINE_VERSION,
            "generated_at": GENERATED_AT,
            "synthetic_data": True,
            "local_only": True,
            "effect_basis": "percentage_points_of_total_portfolio_return",
            "manager_count": len(manager_rows),
            "manager_rows": manager_rows,
            "tie_out": {
                "target_policy_benchmark_return_from_rows": _return_number(
                    target_policy_benchmark_return
                ),
                "actual_allocation_benchmark_return_from_rows": _return_number(
                    actual_allocation_benchmark_return
                ),
                "actual_portfolio_return_from_rows": _return_number(
                    actual_portfolio_return
                ),
                "allocation_drift_effect_from_rows": _return_number(
                    sum(row["allocation_drift_effect"] for row in decimal_rows)
                ),
                "manager_implementation_effect_from_rows": _return_number(
                    sum(row["manager_implementation_effect"] for row in decimal_rows)
                ),
                "status": "pass",
            },
        },
        "imputed_variant": imputed_variant,
        "quality_summary": quality_summary,
    }


def build_policy_attribution_report_inputs(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    inputs = {
        "policy_level_attribution_summary": _summary_report_input(artifacts, context),
        "policy_level_manager_effect_detail": _manager_detail_report_input(
            artifacts, context
        ),
        "imputed_baseline_policy_attribution_variant": _imputed_variant_report_input(
            artifacts, context
        ),
    }
    _validate_report_ids(inputs)
    return inputs


def build_policy_attribution_report_views(
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
            "report_family": payload["report_family"],
            "master_question_family": payload["master_question_family"],
            "exact_report_question": payload["exact_report_question"],
            "audience_tier": payload["audience_tier"],
            "summary_detail_status": payload["summary_detail_status"],
            "representation_level": payload["representation_level"],
            "denominator_category_system": payload["denominator_category_system"],
            "rendering_mode": payload["rendering_mode"],
            "headline_sentence": visible["headline_sentence"],
            "headline_metrics": visible["headline_metrics"],
            "bridge_table": visible.get("bridge_table"),
            "compact_table": visible.get("compact_table"),
            "caveats": visible.get("caveats", []),
            "advisor_note": visible.get("advisor_note"),
            "policy_allocation_mode": payload["policy_allocation_mode"],
            "baseline_type": payload["baseline_type"],
            "effect_basis_note": payload["effect_basis_note"],
            "source_policy_mandate_pack_id": payload["source_policy_mandate_pack_id"],
            "source_policy_level_attribution_engine_id": payload[
                "source_policy_level_attribution_engine_id"
            ],
            "internal_source_refs": payload["internal_source_refs"],
            "calculation_trace": payload["calculation_trace"],
            "information_budget_applied": _budget_actuals(
                report_id=report_id,
                visible=visible,
                rendering_mode=payload["rendering_mode"],
            ),
            "table_validation": payload.get("table_validation", {}),
            "gated_or_deferred": False,
        }
        _validate_view_budget(view)
        views[report_id] = view
    return views


def render_markdown_mockup(view: dict[str, Any]) -> str:
    lines = [f"# {view['display_title']}", "", view["headline_sentence"], ""]

    if view["headline_metrics"]:
        lines.extend(["## Key Metrics", ""])
        for metric in view["headline_metrics"]:
            lines.append(f"- **{metric['label']}:** {metric['formatted_value']}")
        lines.append("")

    bridge_table = view.get("bridge_table")
    if bridge_table:
        lines.extend([f"## {bridge_table['title']}", ""])
        lines.extend(_render_markdown_table(bridge_table))
        lines.append("")

    compact_table = view.get("compact_table")
    if compact_table:
        lines.extend([f"## {compact_table['title']}", ""])
        lines.extend(_render_markdown_table(compact_table))
        lines.append("")

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


def generate_policy_level_attribution(
    *,
    policy_pack_dir: str | Path = DEFAULT_POLICY_PACK_DIR,
    attribution_output_dir: str | Path = DEFAULT_ATTRIBUTION_OUTPUT_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    input_dir: str | Path = DEFAULT_INPUT_DIR,
    view_dir: str | Path = DEFAULT_VIEW_DIR,
    mockup_dir: str | Path = DEFAULT_MOCKUP_DIR,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    input_path = Path(input_dir)
    view_path = Path(view_dir)
    mockup_path = Path(mockup_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    input_path.mkdir(parents=True, exist_ok=True)
    view_path.mkdir(parents=True, exist_ok=True)
    mockup_path.mkdir(parents=True, exist_ok=True)

    context = load_source_context(
        policy_pack_dir=policy_pack_dir,
        attribution_output_dir=attribution_output_dir,
    )
    artifacts = calculate_policy_level_attribution(context)

    calculated_files: list[str] = []
    for artifact_key, filename in CALCULATED_ARTIFACT_FILES.items():
        _write_json(output_path / filename, artifacts[artifact_key])
        calculated_files.append(filename)

    inputs = build_policy_attribution_report_inputs(artifacts, context)
    views = build_policy_attribution_report_views(inputs)

    input_files: list[str] = []
    for report_id in BUILD_NOW_REPORT_IDS:
        filename = INPUT_FILENAME_BY_REPORT_ID[report_id]
        _write_json(input_path / filename, inputs[report_id])
        input_files.append(filename)

    input_index = _input_index(input_files, inputs)
    _write_json(input_path / "policy_attribution_report_input_index.json", input_index)
    input_files.append("policy_attribution_report_input_index.json")

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
        view_path / "gated_deferred_policy_attribution_index.json", gated_index
    )
    view_files.append("gated_deferred_policy_attribution_index.json")

    readme = render_mockup_readme(views, gated_index)
    (mockup_path / "README.md").write_text(readme, encoding="utf-8")
    mockup_files.append("README.md")

    view_index = _view_index(view_files, mockup_files, views, gated_index)
    _write_json(view_path / "policy_attribution_report_view_index.json", view_index)
    view_files.append("policy_attribution_report_view_index.json")

    return {
        "schema_version": "policy_level_attribution_generation_summary.v1",
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "engine_id": ENGINE_ID,
        "source_policy_mandate_pack_id": context["policy_pack"]["manifest"]["pack_id"],
        "calculated_artifact_count": len(calculated_files),
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
        "bridge_tie_out_passed": (
            artifacts["summary"]["residual_status"] == "pass"
            and artifacts["quality_summary"]["residual_tie_out_check"]["status"]
            == "pass"
        ),
        "manager_rows_generated": artifacts["manager_rows"]["manager_count"],
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
        "# Policy Attribution v1 Report Mockups",
        "",
        (
            "These local product-review mockups are generated from Policy Attribution "
            "v1 view data backed by the synthetic policy/mandate pack."
        ),
        (
            "They are not wired into Advisor Preview, Populate, Present, generated "
            "reports, Docker, deployment, live data, external data, or production "
            "reporting."
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
            "## Bridge Behavior",
            "",
            (
                "Policy-Level Attribution bridges Global benchmark -> Target policy "
                "benchmark -> Actual allocation benchmark -> Actual portfolio."
            ),
            (
                "Policy allocation review remains allocation hygiene; this set "
                "separates return effects from target-versus-actual drift review."
            ),
            "",
            "## Superseded Primary Surface",
            "",
            (
                "Policy-Level Attribution Summary v1 is superseded for product "
                "review by Advisor Policy Attribution by Manager/Sleeve v2."
            ),
            (
                "V1 remains a local calculation reference but should not be "
                "treated as the primary report surface."
            ),
            (
                "The v2 report separates selected mandate, target weighting, and "
                "funding drift effects and excludes manager implementation from "
                "the primary advisor report."
            ),
            "",
            "## Gated Or Deferred",
            "",
        ]
    )
    for row in gated_index["gated_or_deferred_reports"]:
        lines.append(
            f"- {row['display_title']} ({row['status']}): {row['reason']}"
        )
    return "\n".join(lines).rstrip() + "\n"


def _summary_report_input(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    summary = artifacts["summary"]
    bridge = artifacts["bridge"]
    effect_rows = [
        {
            "Effect": "Policy design effect",
            "Value": _format_effect_pp(summary["policy_design_effect"]),
            "Meaning": "Target policy benchmark return minus global benchmark return.",
        },
        {
            "Effect": "Allocation drift effect",
            "Value": _format_effect_pp(summary["allocation_drift_effect"]),
            "Meaning": "Actual allocation benchmark return minus target policy benchmark return.",
        },
        {
            "Effect": "Manager implementation effect",
            "Value": _format_effect_pp(summary["manager_implementation_effect"]),
            "Meaning": "Actual portfolio return minus actual allocation benchmark return.",
        },
    ]
    visible = {
        "headline_sentence": (
            "The synthetic policy bridge finishes "
            f"{_format_effect_pp(summary['total_relative_effect'])} above the global "
            "benchmark after separating policy design, allocation drift, and manager "
            "implementation effects."
        ),
        "headline_metrics": [
            _metric(
                "Total relative effect",
                summary["total_relative_effect"],
                _format_effect_pp(summary["total_relative_effect"]),
            ),
            _metric(
                "Policy design effect",
                summary["policy_design_effect"],
                _format_effect_pp(summary["policy_design_effect"]),
            ),
            _metric(
                "Allocation drift effect",
                summary["allocation_drift_effect"],
                _format_effect_pp(summary["allocation_drift_effect"]),
            ),
        ],
        "bridge_table": _table(
            "Policy-Level Attribution Bridge",
            ["Stage", "Return", "Incremental Effect", "Cumulative Effect", "Meaning"],
            [
                {
                    "Stage": row["stage"],
                    "Return": _format_percent(row["return"]),
                    "Incremental Effect": _format_effect_pp(
                        row["incremental_effect_from_prior_stage"]
                    ),
                    "Cumulative Effect": _format_effect_pp(
                        row["cumulative_effect_vs_global"]
                    ),
                    "Meaning": row["meaning"],
                }
                for row in bridge["bridge_rows"]
            ],
        ),
        "compact_table": _table(
            "Effect Explanation",
            ["Effect", "Value", "Meaning"],
            effect_rows,
        ),
        "caveats": [
            "Effects are measured in percentage points of total portfolio return and require review before client use."
        ],
        "advisor_note": (
            "Manager implementation is a high-level mandate-benchmark effect; "
            "detailed manager drivers remain a separate future report."
        ),
    }
    return _report_input(
        report_element_id="policy_level_attribution_summary",
        display_title="Policy-Level Attribution Summary",
        report_family="policy_level_attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "Did the advisor/family policy allocation add value versus the global "
            "benchmark, and did allocation drift help or hurt?"
        ),
        audience_tier="advisor_review_and_client_briefing_when_sophisticated",
        summary_detail_status="summary",
        representation_level="policy_level_bridge",
        denominator_category_system="total_portfolio_return",
        rendering_mode="summary_first_bridge",
        context=context,
        visible_content=visible,
        policy_allocation_mode="explicit_policy_allocation",
        baseline_type="explicit_policy_target_vs_current_actual",
        effect_basis_note="Effect values are percentage points of total portfolio return.",
        source_artifact_keys=("summary", "bridge", "quality_summary"),
        calculation_trace={
            "bridge_tie_out_status": summary["residual_status"],
            "residual": summary["residual"],
        },
        table_validation={
            "bridge_stages": [row["stage"] for row in bridge["bridge_rows"]],
            "effect_rows_shown": 3,
        },
    )


def _manager_detail_report_input(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    summary = artifacts["summary"]
    rows = artifacts["manager_rows"]["manager_rows"]
    largest_drift = max(rows, key=lambda row: abs(row["allocation_drift_effect"]))
    visible_rows = [
        {
            "Manager/Sleeve": row["manager_sleeve"],
            "Target Weight": _format_percent(row["target_weight"]),
            "Actual Weight": _format_percent(row["actual_weight"]),
            "Benchmark Return": _format_percent(row["mandate_benchmark_return"]),
            "Actual Return": _format_percent(row["manager_actual_return"]),
            "Drift Effect": _format_effect_pp(row["allocation_drift_effect"]),
            "Manager Effect": _format_effect_pp(row["manager_implementation_effect"]),
            "Status": _status_label(row["drift_status"]),
        }
        for row in rows
    ]
    visible = {
        "headline_sentence": (
            "Manager A shows the largest allocation drift effect because 24.86% "
            "actual weight exceeded its 22.00% target while its mandate benchmark "
            "return was 9.50%."
        ),
        "headline_metrics": [
            _metric("Managers covered", len(rows), f"{len(rows)} of {len(rows)}"),
            _metric(
                "Manager implementation effect",
                summary["manager_implementation_effect"],
                _format_effect_pp(summary["manager_implementation_effect"]),
            ),
            _metric(
                "Largest allocation drift effect",
                largest_drift["allocation_drift_effect"],
                (
                    f"{largest_drift['manager_sleeve'].split(' - ')[0]} "
                    f"{_format_effect_pp(largest_drift['allocation_drift_effect'])}"
                ),
            ),
        ],
        "compact_table": _table(
            "Manager Effect Detail",
            [
                "Manager/Sleeve",
                "Target Weight",
                "Actual Weight",
                "Benchmark Return",
                "Actual Return",
                "Drift Effect",
                "Manager Effect",
                "Status",
            ],
            visible_rows,
        ),
        "caveats": [
            "Drift effect measures target-to-actual weight difference at the mandate benchmark return; it does not assign cause."
        ],
        "advisor_note": (
            "Use this table to see how target versus actual weight changes return "
            "impact before moving to detailed manager-driver analysis."
        ),
    }
    return _report_input(
        report_element_id="policy_level_manager_effect_detail",
        display_title="Policy-Level Manager Effect Detail",
        report_family="policy_level_attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "Which manager/sleeve target weights, actual weights, benchmark returns, "
            "and actual returns drove the policy-level attribution bridge?"
        ),
        audience_tier="advisor_review_default_client_briefing_on_request",
        summary_detail_status="detail",
        representation_level="manager_sleeve_policy_effect_rows",
        denominator_category_system="total_portfolio_return",
        rendering_mode="compact_manager_effect_table",
        context=context,
        visible_content=visible,
        policy_allocation_mode="explicit_policy_allocation",
        baseline_type="explicit_policy_target_vs_current_actual",
        effect_basis_note="Effect values are percentage points of total portfolio return.",
        source_artifact_keys=("manager_rows", "summary", "quality_summary"),
        calculation_trace={
            "manager_count": len(rows),
            "row_effect_basis": "percentage_points_of_total_portfolio_return",
        },
        table_validation={
            "all_six_managers_visible": len(rows) == 6,
            "target_actual_performance_effect_visible": True,
            "manager_a_target_weight": rows[0]["target_weight"],
            "manager_a_actual_weight": rows[0]["actual_weight"],
            "manager_a_allocation_drift_effect": rows[0]["allocation_drift_effect"],
            "manager_a_manager_effect": rows[0]["manager_implementation_effect"],
        },
    )


def _imputed_variant_report_input(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    imputed = artifacts["imputed_variant"]
    visible = {
        "headline_sentence": (
            "When current manager weights are accepted as the baseline, allocation "
            "drift effect is suppressed and manager implementation remains measurable."
        ),
        "headline_metrics": [
            _metric("Allocation drift effect", 0.0, "0.00 pp (suppressed)"),
            _metric("Baseline", "current_manager_weights", "Current manager weights"),
            _metric(
                "Manager implementation effect",
                imputed["manager_implementation_effect"],
                _format_effect_pp(imputed["manager_implementation_effect"]),
            ),
        ],
        "compact_table": _table(
            "Imputed Baseline Variant",
            ["Item", "Status", "Meaning"],
            [
                {
                    "Item": "Baseline",
                    "Status": "Current manager weights",
                    "Meaning": "Actual weights are treated as target weights for setup review.",
                },
                {
                    "Item": "Allocation drift effect",
                    "Status": "Suppressed",
                    "Meaning": "Target-versus-actual policy drift is not shown in this variant.",
                },
                {
                    "Item": "Manager implementation effect",
                    "Status": "Available",
                    "Meaning": "Actual manager returns are compared with mandate benchmark returns.",
                },
                {
                    "Item": "Use",
                    "Status": "Advisor setup",
                    "Meaning": "This variant is not the standard client report and does not prove the current allocation is ideal.",
                },
            ],
        ),
        "caveats": [
            "This variant is a setup/readiness view, not proof that the current allocation is ideal."
        ],
        "advisor_note": (
            "Use the explicit policy report when advisor/family target weights are "
            "available."
        ),
    }
    return _report_input(
        report_element_id="imputed_baseline_policy_attribution_variant",
        display_title="Imputed Baseline Policy Attribution Variant",
        report_family="policy_level_attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "What changes when current manager weights are accepted as the policy baseline?"
        ),
        audience_tier="advisor_setup_and_advisor_review",
        summary_detail_status="setup_variant",
        representation_level="policy_level_setup_variant",
        denominator_category_system="total_portfolio_return",
        rendering_mode="setup_variant_note",
        context=context,
        visible_content=visible,
        policy_allocation_mode="imputed_current_allocation",
        baseline_type="accepted_current_manager_weights",
        effect_basis_note="Effect values are percentage points of total portfolio return.",
        source_artifact_keys=("imputed_variant", "summary", "quality_summary"),
        calculation_trace={
            "allocation_drift_effect_suppressed": True,
            "allocation_drift_effect": imputed["allocation_drift_effect"],
        },
        table_validation={
            "current_weights_accepted_as_baseline": True,
            "allocation_drift_effect_zero_or_suppressed": True,
            "not_standard_client_report": True,
            "current_allocation_not_proven_ideal": True,
        },
    )


def _report_input(
    *,
    report_element_id: str,
    display_title: str,
    report_family: str,
    master_question_family: str,
    exact_report_question: str,
    audience_tier: str,
    summary_detail_status: str,
    representation_level: str,
    denominator_category_system: str,
    rendering_mode: str,
    context: dict[str, Any],
    visible_content: dict[str, Any],
    policy_allocation_mode: str,
    baseline_type: str,
    effect_basis_note: str,
    source_artifact_keys: tuple[str, ...],
    calculation_trace: dict[str, Any],
    table_validation: dict[str, Any],
) -> dict[str, Any]:
    pack = context["policy_pack"]
    artifact_refs = [
        _as_posix(DEFAULT_OUTPUT_DIR / CALCULATED_ARTIFACT_FILES[key])
        for key in source_artifact_keys
    ]
    return {
        "schema_version": REPORT_INPUT_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "report_element_id": report_element_id,
        "display_title": display_title,
        "report_family": report_family,
        "master_question_family": master_question_family,
        "exact_report_question": exact_report_question,
        "audience_tier": audience_tier,
        "summary_detail_status": summary_detail_status,
        "representation_level": representation_level,
        "denominator_category_system": denominator_category_system,
        "rendering_mode": rendering_mode,
        "visible_content": visible_content,
        "policy_allocation_mode": policy_allocation_mode,
        "baseline_type": baseline_type,
        "effect_basis_note": effect_basis_note,
        "source_policy_mandate_pack_id": pack["manifest"]["pack_id"],
        "source_policy_level_attribution_engine_id": ENGINE_ID,
        "source_calculated_artifacts": [
            CALCULATED_ARTIFACT_FILES[key] for key in source_artifact_keys
        ],
        "internal_source_refs": [
            context["source_paths"]["policy_level_attribution_inputs"],
            context["source_paths"]["policy_allocation_profile"],
            context["source_paths"]["actual_manager_allocation_snapshot"],
            context["source_paths"]["manager_mandate_benchmark_catalog"],
            *artifact_refs,
        ],
        "calculation_trace": calculation_trace,
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
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "policy_allocation_mode": "explicit_policy_allocation",
        "source_policy_mandate_pack": context["policy_pack"]["manifest"]["pack_id"],
        "source_attribution_inputs": [
            context["source_paths"]["policy_level_attribution_inputs"],
            context["attribution_source_paths"][
                "manager_calculated_attribution_summary"
            ],
            context["attribution_source_paths"][
                "whole_portfolio_calculated_attribution_summary"
            ],
        ],
        "generated_artifacts": list(CALCULATED_ARTIFACT_FILES.values()),
        "calculations_supported": [
            "target_policy_benchmark_return",
            "actual_allocation_benchmark_return",
            "actual_portfolio_return",
            "policy_design_effect",
            "allocation_drift_effect",
            "manager_implementation_effect",
            "total_relative_effect",
            "residual_tie_out",
            "imputed_current_baseline_variant",
        ],
        "calculations_gated": [
            "within_manager_attribution_detail",
            "blended_all_in_attribution",
            "timing_attribution",
            "dollar_pnl_attribution",
            "production_client_attribution",
            "current_vs_proposed_policy_attribution",
        ],
        "limitations": [
            "Synthetic local-demo calculation only.",
            "Actual portfolio return uses current manager weights times manager actual returns for this policy bridge.",
            "Within-manager detail remains a future report.",
        ],
        "timing_status": "unavailable",
        "dollar_pnl_status": quality_summary["dollar_pnl_availability"]["status"],
        "approval_status": "synthetic_demo_approved",
        "residual_status": summary["residual_status"],
    }


def _bridge_rows(
    *,
    global_benchmark_return: Decimal,
    target_policy_benchmark_return: Decimal,
    actual_allocation_benchmark_return: Decimal,
    actual_portfolio_return: Decimal,
    policy_design_effect: Decimal,
    allocation_drift_effect: Decimal,
    manager_implementation_effect: Decimal,
) -> dict[str, Any]:
    return {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "effect_basis": "percentage_points_of_total_portfolio_return",
        "bridge_rows": [
            {
                "stage": "Global benchmark",
                "return": _return_number(global_benchmark_return),
                "incremental_effect_from_prior_stage": _return_number(Decimal("0")),
                "cumulative_effect_vs_global": _return_number(Decimal("0")),
                "meaning": "Broad agreed comparison return.",
            },
            {
                "stage": "Target policy benchmark",
                "return": _return_number(target_policy_benchmark_return),
                "incremental_effect_from_prior_stage": _return_number(
                    policy_design_effect
                ),
                "cumulative_effect_vs_global": _return_number(policy_design_effect),
                "meaning": "Agreed target manager weights with mandate benchmark returns.",
            },
            {
                "stage": "Actual allocation benchmark",
                "return": _return_number(actual_allocation_benchmark_return),
                "incremental_effect_from_prior_stage": _return_number(
                    allocation_drift_effect
                ),
                "cumulative_effect_vs_global": _return_number(
                    actual_allocation_benchmark_return - global_benchmark_return
                ),
                "meaning": "Actual manager weights with mandate benchmark returns.",
            },
            {
                "stage": "Actual portfolio",
                "return": _return_number(actual_portfolio_return),
                "incremental_effect_from_prior_stage": _return_number(
                    manager_implementation_effect
                ),
                "cumulative_effect_vs_global": _return_number(
                    actual_portfolio_return - global_benchmark_return
                ),
                "meaning": "Actual manager weights with actual manager returns.",
            },
        ],
    }


def _imputed_baseline_variant(
    *,
    decimal_rows: list[dict[str, Any]],
    global_benchmark_return: Decimal,
    actual_allocation_benchmark_return: Decimal,
    actual_portfolio_return: Decimal,
    manager_implementation_effect: Decimal,
) -> dict[str, Any]:
    policy_design_effect = actual_allocation_benchmark_return - global_benchmark_return
    allocation_drift_effect = Decimal("0")
    total_relative_effect = actual_portfolio_return - global_benchmark_return
    residual = (
        total_relative_effect
        - policy_design_effect
        - allocation_drift_effect
        - manager_implementation_effect
    )
    return {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "policy_allocation_mode": "imputed_current_allocation",
        "baseline_type": "accepted_current_manager_weights",
        "target_weights_set_equal_to_actual_weights": True,
        "target_policy_benchmark_return": _return_number(
            actual_allocation_benchmark_return
        ),
        "actual_allocation_benchmark_return": _return_number(
            actual_allocation_benchmark_return
        ),
        "actual_portfolio_return": _return_number(actual_portfolio_return),
        "policy_design_effect": _return_number(policy_design_effect),
        "allocation_drift_effect": _return_number(allocation_drift_effect),
        "allocation_drift_effect_status": "suppressed",
        "manager_implementation_effect": _return_number(
            manager_implementation_effect
        ),
        "total_relative_effect": _return_number(total_relative_effect),
        "residual": _return_number(residual),
        "residual_status": _residual_status(residual),
        "not_default_client_report": True,
        "current_allocation_not_proven_ideal": True,
        "manager_rows": [
            {
                "manager_sleeve": row["manager_sleeve"],
                "target_weight": _weight_number(row["actual_weight"]),
                "actual_weight": _weight_number(row["actual_weight"]),
                "allocation_drift_effect": 0.0,
                "manager_implementation_effect": _return_number(
                    row["manager_implementation_effect"]
                ),
            }
            for row in decimal_rows
        ],
        "caveats": [
            "The imputed-current variant is a setup/readiness view, not proof that current weights are ideal."
        ],
    }


def _quality_summary(
    *,
    context: dict[str, Any],
    decimal_rows: list[dict[str, Any]],
    residual: Decimal,
    summary: dict[str, Any],
) -> dict[str, Any]:
    target_weight_sum = sum(row["target_weight"] for row in decimal_rows)
    actual_weight_sum = sum(row["actual_weight"] for row in decimal_rows)
    benchmark_coverage = all(
        row["mandate_benchmark_return"] is not None for row in decimal_rows
    )
    manager_return_coverage = all(
        row["manager_actual_return"] is not None for row in decimal_rows
    )
    return {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "weight_sum_checks": {
            "target_weight_sum": _weight_number(target_weight_sum),
            "target_weight_sum_status": _weight_sum_status(target_weight_sum),
            "actual_weight_sum": _weight_number(actual_weight_sum),
            "actual_weight_sum_status": _weight_sum_status(actual_weight_sum),
        },
        "return_input_coverage": {
            "manager_actual_return_coverage": f"{len(decimal_rows)}_of_{len(decimal_rows)}"
            if manager_return_coverage
            else "incomplete",
            "global_benchmark_return_present": True,
            "source_actual_portfolio_formula": "sum_actual_weight_times_manager_actual_return",
        },
        "benchmark_coverage": {
            "manager_mandate_benchmark_coverage": f"{len(decimal_rows)}_of_{len(decimal_rows)}"
            if benchmark_coverage
            else "incomplete",
            "status": "pass" if benchmark_coverage else "fail",
        },
        "residual_tie_out_check": {
            "residual": summary["residual"],
            "tolerance": _return_number(TIE_OUT_TOLERANCE),
            "status": _residual_status(residual),
        },
        "dollar_pnl_availability": {
            "status": "gated_no_reliable_beginning_portfolio_value",
            "reason": "Current synthetic inputs do not provide a reliable beginning portfolio value for dollar attribution.",
        },
        "timing_availability": {
            "status": "unavailable",
            "reason": "Clean timing inputs and an approved timing method are absent.",
        },
        "production_readiness_caveats": [
            "Requires approved real policy targets.",
            "Requires approved real manager mandate benchmarks.",
            "Requires production review before client use.",
        ],
        "next_recommended_tranche": (
            "Frank review of policy_attribution_v1 mockups, then optional "
            "within-manager detail or report-content polish."
        ),
        "source_policy_mandate_pack_id": context["policy_pack"]["manifest"]["pack_id"],
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
        "source_policy_level_attribution_engine_id": ENGINE_ID,
        "report_input_count": len(inputs),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "input_files": input_files,
        "mockups_generated_from_views": True,
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
        "source_policy_mandate_pack_id": first["source_policy_mandate_pack_id"],
        "source_policy_level_attribution_engine_id": ENGINE_ID,
        "report_view_count": len(views),
        "markdown_mockup_count": len(MOCKUP_FILENAME_BY_REPORT_ID),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "view_files": view_files,
        "mockup_files": mockup_files,
        "mockups_generated_from_views": True,
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
        "source_policy_level_attribution_engine_id": ENGINE_ID,
        "purpose": "Product/readiness index for policy attribution reports deliberately not generated.",
        "gated_or_deferred_reports": list(GATED_REPORTS),
    }


def _budget_for_report(report_id: str) -> dict[str, Any]:
    budget = dict(DEFAULT_INFORMATION_BUDGET)
    if report_id == "policy_level_attribution_summary":
        budget["max_visible_table_rows"] = 7
        budget["exception_reason"] = (
            "Summary shows a four-stage bridge plus three effect explanation rows."
        )
    elif report_id == "policy_level_manager_effect_detail":
        budget["max_visible_table_rows"] = 6
        budget["exception_reason"] = (
            "Manager effect detail shows all six current manager/sleeve rows."
        )
    elif report_id == "imputed_baseline_policy_attribution_variant":
        budget["max_visible_table_rows"] = 4
    return budget


def _budget_actuals(
    *,
    report_id: str,
    visible: dict[str, Any],
    rendering_mode: str,
) -> dict[str, Any]:
    compact_table = visible.get("compact_table")
    bridge_table = visible.get("bridge_table")
    advisor_note = visible.get("advisor_note")
    budget = _budget_for_report(report_id)
    table_rows = 0
    if compact_table:
        table_rows += len(compact_table["rows"])
    if bridge_table:
        table_rows += len(bridge_table["rows"])
    return {
        **budget,
        "actual_headline_sentences": _sentence_count(visible["headline_sentence"]),
        "actual_headline_metrics": len(visible["headline_metrics"]),
        "actual_visible_table_rows": table_rows,
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
    if budget["actual_visible_table_rows"] > budget["max_visible_table_rows"]:
        raise ValueError(f"{view['report_element_id']} exceeds table row budget")
    if budget["actual_caveats"] > budget["max_caveats"]:
        raise ValueError(f"{view['report_element_id']} exceeds caveat budget")
    if budget["actual_advisor_notes"] > budget["max_advisor_notes"]:
        raise ValueError(f"{view['report_element_id']} exceeds advisor note budget")
    if (
        budget["actual_visible_table_rows"] > DEFAULT_INFORMATION_BUDGET["max_visible_table_rows"]
        and "exception_reason" not in budget
    ):
        raise ValueError(f"{view['report_element_id']} needs table budget exception")

    visible_text = _visible_text(view).lower()
    for term in FORBIDDEN_VISIBLE_TERMS + FORBIDDEN_PLACEHOLDER_TERMS:
        if term in visible_text:
            raise ValueError(f"{view['report_element_id']} leaks forbidden visible term: {term}")
    for pattern in RAW_ID_PATTERNS:
        if re.search(pattern, visible_text):
            raise ValueError(f"{view['report_element_id']} leaks raw id pattern: {pattern}")
    if "percentage points of total portfolio return" not in view["effect_basis_note"]:
        raise ValueError(f"{view['report_element_id']} lacks effect basis note")


def _validate_markdown(view: dict[str, Any], markdown: str) -> None:
    lowered = markdown.lower()
    for term in FORBIDDEN_VISIBLE_TERMS + FORBIDDEN_PLACEHOLDER_TERMS:
        if term in lowered:
            raise ValueError(f"{view['report_element_id']} markdown leaks forbidden term: {term}")
    for pattern in RAW_ID_PATTERNS:
        if re.search(pattern, lowered):
            raise ValueError(f"{view['report_element_id']} markdown leaks raw id pattern: {pattern}")


def _visible_text(view: dict[str, Any]) -> str:
    parts = [view["display_title"], view["headline_sentence"]]
    parts.extend(
        f"{metric['label']} {metric['formatted_value']}"
        for metric in view["headline_metrics"]
    )
    for table_key in ("bridge_table", "compact_table"):
        table = view.get(table_key)
        if table:
            parts.append(table["title"])
            parts.extend(table["columns"])
            for row in table["rows"]:
                parts.extend(str(row[column]) for column in table["columns"])
    parts.extend(view.get("caveats") or [])
    if view.get("advisor_note"):
        parts.append(view["advisor_note"])
    return "\n".join(parts)


def _serializable_manager_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "manager_id": row["manager_id"],
        "manager_sleeve": row["manager_sleeve"],
        "target_weight": _weight_number(row["target_weight"]),
        "actual_weight": _weight_number(row["actual_weight"]),
        "weight_drift": _weight_number(row["weight_drift"]),
        "mandate_benchmark_return": _return_number(row["mandate_benchmark_return"]),
        "manager_actual_return": _return_number(row["manager_actual_return"]),
        "target_benchmark_return_effect": _return_number(
            row["target_benchmark_return_effect"]
        ),
        "actual_allocation_benchmark_effect": _return_number(
            row["actual_allocation_benchmark_effect"]
        ),
        "allocation_drift_effect": _return_number(row["allocation_drift_effect"]),
        "manager_implementation_effect": _return_number(
            row["manager_implementation_effect"]
        ),
        "actual_portfolio_effect": _return_number(row["actual_portfolio_effect"]),
        "effect_basis": "percentage_points_of_total_portfolio_return",
        "drift_status": row["drift_status"],
        "benchmark_basis": row["benchmark_basis"],
        "benchmark_basis_type": row["benchmark_basis_type"],
        "caveats": row["caveats"],
    }


def _by_manager(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["manager_id"]: row for row in rows}


def _d(value: Any) -> Decimal:
    return Decimal(str(value))


def _return_number(value: Decimal) -> float:
    return float(value.quantize(RETURN_QUANT, rounding=ROUND_HALF_UP))


def _weight_number(value: Decimal) -> float:
    return float(value.quantize(WEIGHT_QUANT, rounding=ROUND_HALF_UP))


def _residual_status(value: Decimal) -> str:
    return "pass" if abs(value) <= TIE_OUT_TOLERANCE else "fail"


def _weight_sum_status(value: Decimal) -> str:
    return "pass" if abs(value - Decimal("1")) <= TIE_OUT_TOLERANCE else "fail"


def _format_percent(value: Any) -> str:
    return f"{float(value) * 100:.2f}%"


def _format_effect_pp(value: Any) -> str:
    number = float(value)
    sign = "+" if number >= 0 else "-"
    return f"{sign}{abs(number) * 100:.2f} pp"


def _metric(label: str, value: Any, formatted_value: str) -> dict[str, Any]:
    return {
        "label": label,
        "value": value,
        "formatted_value": formatted_value,
    }


def _table(title: str, columns: list[str], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "title": title,
        "columns": columns,
        "rows": [{column: str(row[column]) for column in columns} for row in rows],
    }


def _render_markdown_table(table: dict[str, Any]) -> list[str]:
    columns = table["columns"]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in table["rows"]:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def _status_label(status: str) -> str:
    return {
        "within_tolerance": "Within tolerance",
        "review": "Review",
        "material_drift": "Material drift",
        "imputed_baseline_no_drift": "No drift in baseline",
    }.get(status, status.replace("_", " ").title())


def _sentence_count(value: str) -> int:
    normalized = value.replace("?", ".").replace("!", ".")
    matches = re.findall(r"[.!?](?:\s|$)", normalized)
    return max(1, len(matches)) if normalized.strip() else 0


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate synthetic policy-level attribution outputs and mockups."
    )
    parser.add_argument("--policy-pack-dir", default=str(DEFAULT_POLICY_PACK_DIR))
    parser.add_argument(
        "--attribution-output-dir", default=str(DEFAULT_ATTRIBUTION_OUTPUT_DIR)
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument("--mockup-dir", default=str(DEFAULT_MOCKUP_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_policy_level_attribution(
        policy_pack_dir=args.policy_pack_dir,
        attribution_output_dir=args.attribution_output_dir,
        output_dir=args.output_dir,
        input_dir=args.input_dir,
        view_dir=args.view_dir,
        mockup_dir=args.mockup_dir,
    )

    print(
        f"Policy-level attribution outputs: {summary['calculated_artifact_count']} -> {summary['output_dir']}"
    )
    print(
        f"Policy attribution report inputs: {summary['report_input_count']} -> {summary['input_dir']}"
    )
    print(
        f"Policy attribution report views: {summary['report_view_count']} -> {summary['view_dir']}"
    )
    print(
        "Policy attribution Markdown mockups: "
        f"{summary['markdown_mockup_count']} -> {summary['mockup_dir']}"
    )
    print("Source policy pack: " + summary["source_policy_mandate_pack_id"])
    print("Generated report ids: " + ", ".join(summary["report_ids"]))
    print("Bridge tie-out passed: " + str(summary["bridge_tie_out_passed"]))
    print("Gated reports not generated: " + ", ".join(summary["gated_reports_not_generated"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
