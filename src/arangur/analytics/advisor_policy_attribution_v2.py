from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00Z"

ENGINE_ID = "advisor_policy_attribution_engine_v2"
ENGINE_VERSION = "2026-07-09"
GENERATOR_VERSION = "advisor_policy_attribution_v2.v2"

CALCULATION_SCHEMA_VERSION = "advisor_policy_attribution_calculated_output.v2"
REPORT_INPUT_SCHEMA_VERSION = "advisor_policy_attribution_report_input.v2"
REPORT_INPUT_INDEX_SCHEMA_VERSION = "advisor_policy_attribution_report_input_index.v2"
REPORT_VIEW_SCHEMA_VERSION = "advisor_policy_attribution_report_view.v2"
REPORT_VIEW_INDEX_SCHEMA_VERSION = "advisor_policy_attribution_report_view_index.v2"
GATED_INDEX_SCHEMA_VERSION = "advisor_policy_attribution_gated_deferred_index.v2"

DEFAULT_POLICY_PACK_DIR = Path(
    "data/simulation/policy_mandate_prerequisites/synthetic_policy_mandate_pack_v1"
)
DEFAULT_OUTPUT_DIR = Path("data/simulation/policy_level_attribution") / ENGINE_ID
DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs/policy_attribution_v2")
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/policy_attribution_v2")
DEFAULT_MOCKUP_DIR = Path("docs/product/report_mockups/policy_attribution_v2")

RETURN_QUANT = Decimal("0.000000000001")
WEIGHT_QUANT = Decimal("0.000000001")
TIE_OUT_TOLERANCE = Decimal("0.000001")

POLICY_PACK_FILES = {
    "manifest": "synthetic_policy_mandate_pack_manifest.json",
    "policy_allocation_mode": "policy_allocation_mode.json",
    "policy_allocation_profile": "policy_allocation_profile.json",
    "actual_manager_allocation_snapshot": "actual_manager_allocation_snapshot.json",
    "allocation_drift_summary": "allocation_drift_summary.json",
    "manager_mandate_benchmark_catalog": "manager_mandate_benchmark_catalog.json",
    "manager_benchmark_basis_map": "manager_benchmark_basis_map.json",
    "policy_level_attribution_inputs": "policy_level_attribution_inputs.json",
    "equal_weight_diagnostic_attribution_classification": (
        "equal_weight_diagnostic_attribution_classification.json"
    ),
    "policy_mandate_readiness_summary": "policy_mandate_readiness_summary.json",
}

CALCULATED_ARTIFACT_FILES = {
    "manifest": "advisor_policy_attribution_v2_manifest.json",
    "summary": "advisor_policy_attribution_summary_v2.json",
    "manager_rows": "advisor_policy_attribution_manager_rows_v2.json",
    "quality_summary": "advisor_policy_attribution_quality_summary_v2.json",
}

REPORT_SPECS: tuple[dict[str, str], ...] = (
    {
        "report_id": "advisor_policy_attribution_by_manager",
        "input_filename": "advisor_policy_attribution_by_manager_input.json",
        "view_filename": "advisor_policy_attribution_by_manager_view.json",
        "mockup_filename": "advisor_policy_attribution_by_manager_mockup_v2.md",
    },
    {
        "report_id": "advisor_policy_effect_totals",
        "input_filename": "advisor_policy_effect_totals_input.json",
        "view_filename": "advisor_policy_effect_totals_view.json",
        "mockup_filename": "advisor_policy_effect_totals_mockup_v2.md",
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
        "report_id": "manager_within_mandate_attribution_detail",
        "display_title": "Manager / Within-Mandate Attribution Detail",
        "status": "Future tranche",
        "reason": "Requires a separate manager-driver report using manager mandate responsibility.",
    },
    {
        "report_id": "blended_all_in_attribution",
        "display_title": "Blended / All-In Attribution",
        "status": "Deferred",
        "reason": "Deferred so advisor policy and manager implementation stay separate.",
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
        "reason": "Gated on approved real policy targets and benchmarks.",
    },
    {
        "report_id": "current_vs_proposed_policy_attribution",
        "display_title": "Current-vs-Proposed Policy Attribution",
        "status": "Gated",
        "reason": "Gated on a proposed allocation workflow.",
    },
    {
        "report_id": "old_bridge_summary",
        "display_title": "Old Bridge Summary",
        "status": "Superseded",
        "reason": "Superseded as the primary report surface by the manager/sleeve advisor policy report.",
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


def load_source_context(
    *,
    policy_pack_dir: str | Path = DEFAULT_POLICY_PACK_DIR,
) -> dict[str, Any]:
    root = Path(policy_pack_dir)
    policy_pack = {
        name: _load_json(root / filename)
        for name, filename in POLICY_PACK_FILES.items()
    }
    manifest = policy_pack["manifest"]
    profile = policy_pack["policy_allocation_profile"]
    policy_inputs = policy_pack["policy_level_attribution_inputs"]
    equal_weight = policy_pack["equal_weight_diagnostic_attribution_classification"]

    if manifest["pack_id"] != "synthetic_policy_mandate_pack_v1":
        raise ValueError("Unexpected policy mandate pack id")
    if not manifest["synthetic_data"] or not manifest["local_only"]:
        raise ValueError("Advisor policy attribution requires local synthetic inputs")
    if profile["allocation_mode"] != "explicit_policy_allocation":
        raise ValueError("Advisor policy attribution v2 requires explicit policy allocation")
    if not policy_inputs["synthetic_data"] or not policy_inputs["local_only"]:
        raise ValueError("Advisor policy attribution input scaffold must be local synthetic")
    if equal_weight["default_policy_benchmark"] is not False:
        raise ValueError("Diagnostic equal weighting must not be the default policy benchmark")

    return {
        "policy_pack_dir": _as_posix(root),
        "policy_pack": policy_pack,
        "source_paths": {
            name: _as_posix(root / filename)
            for name, filename in POLICY_PACK_FILES.items()
        },
    }


def calculate_advisor_policy_attribution(context: dict[str, Any]) -> dict[str, Any]:
    pack = context["policy_pack"]
    policy_inputs = pack["policy_level_attribution_inputs"]
    profile = pack["policy_allocation_profile"]
    actual_snapshot = pack["actual_manager_allocation_snapshot"]
    drift_summary = pack["allocation_drift_summary"]
    benchmark_catalog = pack["manager_mandate_benchmark_catalog"]
    basis_map = pack["manager_benchmark_basis_map"]

    profile_by_manager = _by_manager(profile["manager_sleeve_target_allocation"])
    actual_by_manager = _by_manager(actual_snapshot["manager_rows"])
    drift_by_manager = _by_manager(drift_summary["manager_rows"])
    benchmark_by_manager = _by_manager(benchmark_catalog["benchmark_rows"])
    basis_by_manager = _by_manager(basis_map["rows"])
    input_rows = policy_inputs["input_rows"]

    selected_count = Decimal(len(input_rows))
    neutral_weight = Decimal("1") / selected_count
    global_benchmark_return = _d(policy_inputs["global_benchmark_return"])

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
        mandate_benchmark_return = _d(benchmark_row["synthetic_period_return"])
        actual_manager_return_context = _d(input_row["manager_actual_return"])
        weight_drift = actual_weight - target_weight

        decimal_rows.append(
            {
                "manager_id": manager_id,
                "display_name": input_row["display_name"],
                "neutral_weight": neutral_weight,
                "target_weight": target_weight,
                "actual_weight": actual_weight,
                "weight_drift": weight_drift,
                "mandate_benchmark_return": mandate_benchmark_return,
                "actual_manager_return_context": actual_manager_return_context,
                "drift_status": drift_row["drift_status"],
                "benchmark_basis": benchmark_row["mandate_benchmark_display_name"],
                "benchmark_basis_type": basis_row["benchmark_basis_type"],
                "caveats": [
                    "Synthetic local-demo mandate benchmark basis.",
                    "Actual return is context for a separate manager implementation review.",
                ],
            }
        )

    neutral_selected_mandate_basket_return = sum(
        row["neutral_weight"] * row["mandate_benchmark_return"] for row in decimal_rows
    )
    target_policy_benchmark_return = sum(
        row["target_weight"] * row["mandate_benchmark_return"] for row in decimal_rows
    )
    actual_allocation_benchmark_return = sum(
        row["actual_weight"] * row["mandate_benchmark_return"] for row in decimal_rows
    )
    actual_portfolio_return_context = sum(
        row["actual_weight"] * row["actual_manager_return_context"]
        for row in decimal_rows
    )

    for row in decimal_rows:
        row["selected_mandate_effect"] = row["neutral_weight"] * (
            row["mandate_benchmark_return"] - global_benchmark_return
        )
        row["target_weighting_effect"] = (
            row["target_weight"] - row["neutral_weight"]
        ) * (row["mandate_benchmark_return"] - neutral_selected_mandate_basket_return)
        row["funding_drift_effect"] = (
            row["actual_weight"] - row["target_weight"]
        ) * (row["mandate_benchmark_return"] - target_policy_benchmark_return)
        row["advisor_policy_effect"] = (
            row["selected_mandate_effect"]
            + row["target_weighting_effect"]
            + row["funding_drift_effect"]
        )

    selected_mandate_effect = (
        neutral_selected_mandate_basket_return - global_benchmark_return
    )
    target_weighting_effect = (
        target_policy_benchmark_return - neutral_selected_mandate_basket_return
    )
    funding_drift_effect = (
        actual_allocation_benchmark_return - target_policy_benchmark_return
    )
    advisor_policy_effect = (
        selected_mandate_effect + target_weighting_effect + funding_drift_effect
    )
    advisor_policy_effect_equivalent = (
        actual_allocation_benchmark_return - global_benchmark_return
    )
    manager_implementation_effect_handoff = (
        actual_portfolio_return_context - actual_allocation_benchmark_return
    )
    residual = advisor_policy_effect - advisor_policy_effect_equivalent

    summary = {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "global_benchmark_return": _return_number(global_benchmark_return),
        "neutral_selected_mandate_basket_return": _return_number(
            neutral_selected_mandate_basket_return
        ),
        "target_policy_benchmark_return": _return_number(
            target_policy_benchmark_return
        ),
        "actual_allocation_benchmark_return": _return_number(
            actual_allocation_benchmark_return
        ),
        "selected_mandate_effect": _return_number(selected_mandate_effect),
        "target_weighting_effect": _return_number(target_weighting_effect),
        "funding_drift_effect": _return_number(funding_drift_effect),
        "advisor_policy_effect": _return_number(advisor_policy_effect),
        "advisor_policy_effect_equivalent": _return_number(
            advisor_policy_effect_equivalent
        ),
        "manager_implementation_effect_handoff": _return_number(
            manager_implementation_effect_handoff
        ),
        "manager_implementation_visible_in_primary_report": False,
        "actual_portfolio_return_context": _return_number(actual_portfolio_return_context),
        "source_reported_actual_portfolio_return_context": _return_number(
            _d(policy_inputs["actual_portfolio_return"])
        ),
        "source_actual_portfolio_return_reconciliation": policy_inputs[
            "manager_current_weight_return_reconciliation"
        ],
        "residual": _return_number(residual),
        "residual_status": _residual_status(residual),
        "effect_basis": "percentage_points_of_total_portfolio_return",
        "headline_interpretation": (
            "Advisor policy decisions finished below the global benchmark before "
            "manager implementation, with target weighting and funding drift offsetting "
            "part of the selected mandate drag."
        ),
        "caveats": [
            "Synthetic demo attribution only; production use needs approved real policy targets and benchmarks.",
            "Manager implementation belongs to a separate within-manager attribution report.",
        ],
    }

    manager_rows = [_serializable_manager_row(row) for row in decimal_rows]
    total_row = {
        "display_name": "Total advisor policy effect",
        "neutral_weight": _weight_number(sum(row["neutral_weight"] for row in decimal_rows)),
        "target_weight": _weight_number(sum(row["target_weight"] for row in decimal_rows)),
        "actual_weight": _weight_number(sum(row["actual_weight"] for row in decimal_rows)),
        "weight_drift": _weight_number(sum(row["weight_drift"] for row in decimal_rows)),
        "mandate_benchmark_return": None,
        "actual_manager_return_context": None,
        "selected_mandate_effect": _return_number(selected_mandate_effect),
        "target_weighting_effect": _return_number(target_weighting_effect),
        "funding_drift_effect": _return_number(funding_drift_effect),
        "advisor_policy_effect": _return_number(advisor_policy_effect),
        "drift_status": "total",
        "benchmark_basis": "Selected manager mandate basket",
        "caveats": [],
    }
    manager_rows_payload = {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "effect_basis": "percentage_points_of_total_portfolio_return",
        "manager_implementation_visible_in_primary_report": False,
        "manager_count": len(manager_rows),
        "manager_rows": manager_rows,
        "total_row": total_row,
        "tie_out": {
            "selected_mandate_effect_from_rows": _return_number(
                sum(row["selected_mandate_effect"] for row in decimal_rows)
            ),
            "target_weighting_effect_from_rows": _return_number(
                sum(row["target_weighting_effect"] for row in decimal_rows)
            ),
            "funding_drift_effect_from_rows": _return_number(
                sum(row["funding_drift_effect"] for row in decimal_rows)
            ),
            "advisor_policy_effect_from_rows": _return_number(
                sum(row["advisor_policy_effect"] for row in decimal_rows)
            ),
            "status": "pass",
        },
    }
    quality_summary = _quality_summary(
        context=context,
        decimal_rows=decimal_rows,
        summary=summary,
        residual=residual,
    )
    manifest = _manifest(context, summary, quality_summary)

    return {
        "manifest": manifest,
        "summary": summary,
        "manager_rows": manager_rows_payload,
        "quality_summary": quality_summary,
    }


def build_advisor_policy_attribution_report_inputs(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    inputs = {
        "advisor_policy_attribution_by_manager": _by_manager_report_input(
            artifacts, context
        ),
        "advisor_policy_effect_totals": _effect_totals_report_input(
            artifacts, context
        ),
    }
    _validate_report_ids(inputs)
    return inputs


def build_advisor_policy_attribution_report_views(
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
            "report_family": "advisor_policy_attribution",
            "master_question_family": "Performance / Plan",
            "exact_report_question": payload["exact_report_question"],
            "audience_tier": payload["audience_tier"],
            "summary_detail_status": payload["summary_detail_status"],
            "representation_level": payload["representation_level"],
            "denominator_category_system": payload["denominator_category_system"],
            "rendering_mode": payload["rendering_mode"],
            "headline_sentence": visible["headline_sentence"],
            "headline_metrics": visible["headline_metrics"],
            "compact_table": visible["compact_table"],
            "total_row": visible["total_row"],
            "effect_basis_note": visible["effect_basis_note"],
            "caveats": visible["caveats"],
            "advisor_note": visible["advisor_note"],
            "policy_allocation_mode": payload["policy_allocation_mode"],
            "baseline_type": payload["baseline_type"],
            "manager_implementation_visible_in_primary_report": False,
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
        views[report_id] = view
    return views


def render_markdown_mockup(view: dict[str, Any]) -> str:
    lines = [f"# {view['display_title']}", "", view["headline_sentence"], ""]

    if view["headline_metrics"]:
        lines.extend(["## Key Metrics", ""])
        for metric in view["headline_metrics"]:
            lines.append(f"- **{metric['label']}:** {metric['formatted_value']}")
        lines.append("")

    table = view.get("compact_table")
    if table:
        lines.extend([f"## {table['title']}", ""])
        lines.extend(_render_markdown_table(table, view.get("total_row")))
        lines.append("")

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


def generate_advisor_policy_attribution_v2(
    *,
    policy_pack_dir: str | Path = DEFAULT_POLICY_PACK_DIR,
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

    context = load_source_context(policy_pack_dir=policy_pack_dir)
    artifacts = calculate_advisor_policy_attribution(context)
    inputs = build_advisor_policy_attribution_report_inputs(artifacts, context)
    views = build_advisor_policy_attribution_report_views(inputs)

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
    _write_json(input_path / "advisor_policy_attribution_report_input_index.json", input_index)
    input_files.append("advisor_policy_attribution_report_input_index.json")

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
        view_path / "gated_deferred_advisor_policy_attribution_index.json",
        gated_index,
    )
    view_files.append("gated_deferred_advisor_policy_attribution_index.json")

    readme = render_mockup_readme(views, gated_index)
    (mockup_path / "README.md").write_text(readme, encoding="utf-8")
    mockup_files.append("README.md")

    view_index = _view_index(view_files, mockup_files, views, gated_index)
    _write_json(view_path / "advisor_policy_attribution_report_view_index.json", view_index)
    view_files.append("advisor_policy_attribution_report_view_index.json")

    return {
        "schema_version": "advisor_policy_attribution_generation_summary.v2",
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack_id": context["policy_pack"]["manifest"]["pack_id"],
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
        "row_tie_outs_passed": (
            artifacts["manager_rows"]["tie_out"]["status"] == "pass"
            and artifacts["quality_summary"]["row_tie_out_checks"]["advisor_policy_effect_tie_out"]["status"]
            == "pass"
        ),
        "manager_implementation_visible_in_primary_report": False,
        "bridge_grid_not_primary": True,
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
        "# Advisor Policy Attribution v2 Report Mockups",
        "",
        (
            "These local product-review mockups show advisor policy attribution by manager/sleeve."
        ),
        (
            "The primary report separates selected mandate, target weighting, and funding drift effects before manager implementation review."
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
            "## V1 Supersession",
            "",
            (
                "Policy-Level Attribution Summary v1 remains a local calculation reference, but it is superseded as the primary product-review surface."
            ),
            (
                "Advisor Policy Attribution by Manager/Sleeve v2 is the primary review surface for advisor-level policy effects."
            ),
            "",
            "## Gated Or Deferred",
            "",
        ]
    )
    for row in gated_index["gated_or_deferred_reports"]:
        lines.append(f"- {row['display_title']} ({row['status']}): {row['reason']}")

    return "\n".join(lines).rstrip() + "\n"


def _by_manager_report_input(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    summary = artifacts["summary"]
    manager_payload = artifacts["manager_rows"]
    rows = [
        {
            "Manager/Sleeve": row["display_name"],
            "Neutral Weight": _format_percent(row["neutral_weight"]),
            "Target Weight": _format_percent(row["target_weight"]),
            "Actual Weight": _format_percent(row["actual_weight"]),
            "Weight Drift": _format_signed_percent(row["weight_drift"]),
            "Mandate Benchmark Return": _format_percent(row["mandate_benchmark_return"]),
            "Actual Return": _format_percent(row["actual_manager_return_context"]),
            "Selected Mandate Effect": _format_effect_pp(row["selected_mandate_effect"]),
            "Target Weighting Effect": _format_effect_pp(row["target_weighting_effect"]),
            "Funding Drift Effect": _format_effect_pp(row["funding_drift_effect"]),
            "Advisor Policy Effect": _format_effect_pp(row["advisor_policy_effect"]),
            "Status": _status_label(row["drift_status"]),
        }
        for row in manager_payload["manager_rows"]
    ]
    total = manager_payload["total_row"]
    total_row = {
        "Manager/Sleeve": "Total",
        "Neutral Weight": _format_percent(total["neutral_weight"]),
        "Target Weight": _format_percent(total["target_weight"]),
        "Actual Weight": _format_percent(total["actual_weight"]),
        "Weight Drift": _format_signed_percent(total["weight_drift"]),
        "Mandate Benchmark Return": "N/A",
        "Actual Return": "Context only",
        "Selected Mandate Effect": _format_effect_pp(total["selected_mandate_effect"]),
        "Target Weighting Effect": _format_effect_pp(total["target_weighting_effect"]),
        "Funding Drift Effect": _format_effect_pp(total["funding_drift_effect"]),
        "Advisor Policy Effect": _format_effect_pp(total["advisor_policy_effect"]),
        "Status": "Advisor policy total",
    }
    visible_content = {
        "headline_sentence": (
            "Advisor policy decisions were -0.26 pp versus the global benchmark before manager implementation, as target weighting and funding drift partly offset selected mandate drag."
        ),
        "headline_metrics": [
            _metric(
                "Advisor policy effect before manager implementation",
                summary["advisor_policy_effect"],
                _format_effect_pp(summary["advisor_policy_effect"]),
            ),
            _metric(
                "Selected mandate effect",
                summary["selected_mandate_effect"],
                _format_effect_pp(summary["selected_mandate_effect"]),
            ),
            _metric(
                "Funding drift effect",
                summary["funding_drift_effect"],
                _format_effect_pp(summary["funding_drift_effect"]),
            ),
        ],
        "compact_table": _table(
            "Advisor Policy Attribution by Manager/Sleeve",
            [
                "Manager/Sleeve",
                "Neutral Weight",
                "Target Weight",
                "Actual Weight",
                "Weight Drift",
                "Mandate Benchmark Return",
                "Actual Return",
                "Selected Mandate Effect",
                "Target Weighting Effect",
                "Funding Drift Effect",
                "Advisor Policy Effect",
                "Status",
            ],
            rows,
        ),
        "total_row": total_row,
        "effect_basis_note": (
            "Selected mandate effect compares neutral selected mandate exposure with the global benchmark. "
            "Target weighting effect compares target weights with neutral selected-mandate weights. "
            "Funding drift effect compares actual weights with target weights. "
            "Effects are percentage points of total portfolio return. "
            "Manager implementation is not attributed in this report."
        ),
        "caveats": [
            "Neutral selected-mandate weights are a decomposition baseline, not the client policy allocation."
        ],
        "advisor_note": (
            "Actual return is shown only as context for a separate manager implementation review."
        ),
    }
    return _report_input(
        report_element_id="advisor_policy_attribution_by_manager",
        display_title="Advisor Policy Attribution by Manager/Sleeve",
        exact_report_question=(
            "Which advisor-level mandate selection, target weighting, and funding drift decisions drove return versus the global benchmark?"
        ),
        audience_tier="advisor_review_and_client_briefing_when_sophisticated",
        summary_detail_status="summary_with_manager_rows",
        representation_level="manager_sleeve_advisor_policy_effect_rows",
        denominator_category_system="percentage_points_of_total_portfolio_return",
        rendering_mode="compact_manager_sleeve_table",
        visible_content=visible_content,
        context=context,
        artifacts=artifacts,
        source_artifact_keys=(
            "manifest",
            "policy_allocation_profile",
            "actual_manager_allocation_snapshot",
            "allocation_drift_summary",
            "manager_mandate_benchmark_catalog",
            "policy_level_attribution_inputs",
        ),
        table_validation={
            "manager_rows_shown": len(rows),
            "total_row_visible": True,
            "selected_mandate_effect_column_index": 7,
            "target_weighting_effect_column_index": 8,
            "manager_implementation_effect_primary_column": False,
            "actual_return_labeled_context": True,
            "old_bridge_grid_primary": False,
        },
    )


def _effect_totals_report_input(
    artifacts: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    summary = artifacts["summary"]
    rows = [
        {
            "Effect": "Selected mandate effect",
            "Value": _format_effect_pp(summary["selected_mandate_effect"]),
            "Meaning": "Neutral selected mandate exposure versus the global benchmark.",
        },
        {
            "Effect": "Target weighting effect",
            "Value": _format_effect_pp(summary["target_weighting_effect"]),
            "Meaning": "Target weights versus neutral selected-mandate weights.",
        },
        {
            "Effect": "Funding drift effect",
            "Value": _format_effect_pp(summary["funding_drift_effect"]),
            "Meaning": "Actual weights versus target weights.",
        },
    ]
    total_row = {
        "Effect": "Total advisor policy effect",
        "Value": _format_effect_pp(summary["advisor_policy_effect"]),
        "Meaning": "Actual allocation benchmark return minus global benchmark return.",
    }
    visible_content = {
        "headline_sentence": (
            "Advisor policy effects totaled -0.26 pp before manager implementation."
        ),
        "headline_metrics": [
            _metric(
                "Advisor policy effect before manager implementation",
                summary["advisor_policy_effect"],
                _format_effect_pp(summary["advisor_policy_effect"]),
            ),
            _metric(
                "Selected mandate effect",
                summary["selected_mandate_effect"],
                _format_effect_pp(summary["selected_mandate_effect"]),
            ),
            _metric(
                "Funding drift effect",
                summary["funding_drift_effect"],
                _format_effect_pp(summary["funding_drift_effect"]),
            ),
        ],
        "compact_table": _table(
            "Advisor Policy Effect Totals",
            ["Effect", "Value", "Meaning"],
            rows,
        ),
        "total_row": total_row,
        "effect_basis_note": (
            "Selected mandate, target weighting, and funding drift effects are percentage points of total portfolio return before manager implementation."
        ),
        "caveats": [
            "This totals note is a companion to the manager/sleeve report, not the old bridge summary."
        ],
        "advisor_note": (
            "Use the manager/sleeve report when row-level explanation is needed."
        ),
    }
    return _report_input(
        report_element_id="advisor_policy_effect_totals",
        display_title="Advisor Policy Effect Totals",
        exact_report_question=(
            "What are the total advisor-level effects before manager implementation?"
        ),
        audience_tier="advisor_review_and_client_briefing_when_sophisticated",
        summary_detail_status="concise_totals_note",
        representation_level="portfolio_advisor_policy_effect_totals",
        denominator_category_system="percentage_points_of_total_portfolio_return",
        rendering_mode="concise_totals_note",
        visible_content=visible_content,
        context=context,
        artifacts=artifacts,
        source_artifact_keys=("manifest", "policy_level_attribution_inputs"),
        table_validation={
            "old_bridge_grid_primary": False,
            "total_effect_visible": True,
            "manager_implementation_effect_primary_column": False,
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
    artifacts: dict[str, Any],
    source_artifact_keys: tuple[str, ...],
    table_validation: dict[str, Any],
) -> dict[str, Any]:
    pack = context["policy_pack"]
    source_refs = [context["source_paths"][key] for key in source_artifact_keys]
    return {
        "schema_version": REPORT_INPUT_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "report_element_id": report_element_id,
        "display_title": display_title,
        "report_family": "advisor_policy_attribution",
        "master_question_family": "Performance / Plan",
        "exact_report_question": exact_report_question,
        "audience_tier": audience_tier,
        "summary_detail_status": summary_detail_status,
        "representation_level": representation_level,
        "denominator_category_system": denominator_category_system,
        "rendering_mode": rendering_mode,
        "visible_content": visible_content,
        "policy_allocation_mode": "explicit_policy_allocation",
        "baseline_type": "neutral_selected_mandate_to_target_to_actual_allocation",
        "manager_implementation_visible_in_primary_report": False,
        "manager_implementation_handoff_status": "metadata_only",
        "source_policy_mandate_pack_id": pack["manifest"]["pack_id"],
        "source_advisor_policy_attribution_engine_id": ENGINE_ID,
        "internal_source_refs": source_refs,
        "internal_source_metadata": {
            "calculated_engine_id": artifacts["summary"]["engine_id"],
            "source_policy_mandate_pack_id": pack["manifest"]["pack_id"],
            "source_policy_level_v1_outputs_used": False,
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
        "schema_version": "advisor_policy_attribution_manifest.v2",
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack": context["policy_pack"]["manifest"]["pack_id"],
        "source_policy_mandate_pack_dir": context["policy_pack_dir"],
        "source_policy_level_v1_outputs": [],
        "source_policy_level_v1_outputs_used": False,
        "generated_artifacts": dict(CALCULATED_ARTIFACT_FILES),
        "methodology_summary": {
            "global_benchmark_return": "Whole-portfolio comparator selected for advisor policy attribution.",
            "neutral_selected_mandate_basket_return": "Neutral basket of selected manager mandate benchmark returns.",
            "target_policy_benchmark_return": "Sum of target manager weights times manager mandate benchmark returns.",
            "actual_allocation_benchmark_return": "Sum of actual manager weights times manager mandate benchmark returns.",
            "advisor_policy_effect": "Actual allocation benchmark return minus global benchmark return.",
            "manager_implementation": "Calculated only as handoff metadata and excluded from the primary report.",
        },
        "calculations_supported": [
            "global_benchmark_return",
            "neutral_selected_mandate_basket_return",
            "target_policy_benchmark_return",
            "actual_allocation_benchmark_return",
            "selected_mandate_effect",
            "target_weighting_effect",
            "funding_drift_effect",
            "advisor_policy_effect_before_manager_implementation",
            "manager_implementation_effect_handoff_metadata",
            "row_tie_outs",
        ],
        "calculations_gated": [
            "within_manager_attribution_detail",
            "timing_attribution",
            "dollar_pnl_attribution",
            "production_client_attribution",
            "current_vs_proposed_policy_attribution",
            "blended_all_in_attribution",
        ],
        "limitations": [
            "Synthetic local demo only.",
            "Neutral selected-mandate weighting is a decomposition baseline, not a client policy allocation.",
            "Actual manager returns are context for later manager implementation review.",
            "Production use requires approved real targets, benchmarks, and return methodology.",
        ],
        "timing_status": "unavailable",
        "dollar_pnl_status": "gated_no_reliable_beginning_portfolio_value",
        "approval_status": "synthetic_demo_approved",
        "manager_implementation_visible_in_primary_report": False,
        "quality_summary_status": quality_summary["overall_status"],
        "advisor_policy_effect": summary["advisor_policy_effect"],
    }


def _quality_summary(
    *,
    context: dict[str, Any],
    decimal_rows: list[dict[str, Any]],
    summary: dict[str, Any],
    residual: Decimal,
) -> dict[str, Any]:
    neutral_weight_sum = sum(row["neutral_weight"] for row in decimal_rows)
    target_weight_sum = sum(row["target_weight"] for row in decimal_rows)
    actual_weight_sum = sum(row["actual_weight"] for row in decimal_rows)
    selected_row_sum = sum(row["selected_mandate_effect"] for row in decimal_rows)
    target_row_sum = sum(row["target_weighting_effect"] for row in decimal_rows)
    funding_row_sum = sum(row["funding_drift_effect"] for row in decimal_rows)
    advisor_row_sum = sum(row["advisor_policy_effect"] for row in decimal_rows)

    return {
        "schema_version": CALCULATION_SCHEMA_VERSION,
        "engine_id": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "overall_status": "pass",
        "weight_sum_checks": {
            "neutral_weight_sum": _weight_number(neutral_weight_sum),
            "neutral_weight_sum_status": _weight_sum_status(neutral_weight_sum),
            "target_weight_sum": _weight_number(target_weight_sum),
            "target_weight_sum_status": _weight_sum_status(target_weight_sum),
            "actual_weight_sum": _weight_number(actual_weight_sum),
            "actual_weight_sum_status": _weight_sum_status(actual_weight_sum),
        },
        "row_tie_out_checks": {
            "selected_mandate_effect_tie_out": _tie_out(
                selected_row_sum, _d(summary["selected_mandate_effect"])
            ),
            "target_weighting_effect_tie_out": _tie_out(
                target_row_sum, _d(summary["target_weighting_effect"])
            ),
            "funding_drift_effect_tie_out": _tie_out(
                funding_row_sum, _d(summary["funding_drift_effect"])
            ),
            "advisor_policy_effect_tie_out": _tie_out(
                advisor_row_sum, _d(summary["advisor_policy_effect"])
            ),
        },
        "advisor_policy_effect_equivalent_tie_out": _tie_out(
            _d(summary["advisor_policy_effect"]),
            _d(summary["advisor_policy_effect_equivalent"]),
        ),
        "residual_tie_out_check": {
            "residual": summary["residual"],
            "tolerance": _return_number(TIE_OUT_TOLERANCE),
            "status": _residual_status(residual),
        },
        "manager_implementation_handoff_status": {
            "status": "metadata_only",
            "manager_implementation_visible_in_primary_report": False,
            "handoff_value": summary["manager_implementation_effect_handoff"],
            "next_report_family": "manager_within_mandate_attribution_detail",
        },
        "no_blended_report": True,
        "old_bridge_summary_not_primary": True,
        "production_readiness_caveats": [
            "Requires approved real policy targets.",
            "Requires approved real manager mandate benchmarks.",
            "Requires production performance and flow methodology review.",
        ],
        "recommended_next_tranche": "Manager / Within-Mandate Attribution Detail",
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
        "source_advisor_policy_attribution_engine_id": ENGINE_ID,
        "report_input_count": len(inputs),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "input_files": input_files,
        "mockups_generated_from_views": True,
        "manager_implementation_visible_in_primary_report": False,
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
        "source_advisor_policy_attribution_engine_id": ENGINE_ID,
        "report_view_count": len(views),
        "markdown_mockup_count": len(MOCKUP_FILENAME_BY_REPORT_ID),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "view_files": view_files,
        "mockup_files": mockup_files,
        "mockups_generated_from_views": True,
        "manager_implementation_visible_in_primary_report": False,
        "bridge_grid_not_primary": True,
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
        "source_advisor_policy_attribution_engine_id": ENGINE_ID,
        "purpose": "Product/readiness index for advisor policy attribution reports deliberately not generated as primary v2 reports.",
        "gated_or_deferred_reports": list(GATED_REPORTS),
    }


def _budget_for_report(report_id: str) -> dict[str, Any]:
    budget = dict(DEFAULT_INFORMATION_BUDGET)
    if report_id == "advisor_policy_attribution_by_manager":
        budget["max_visible_table_rows"] = 7
        budget["exception_reason"] = (
            "Primary advisor policy report shows all six manager/sleeve rows plus a total row."
        )
    elif report_id == "advisor_policy_effect_totals":
        budget["max_visible_table_rows"] = 4
    return budget


def _budget_actuals(
    *,
    report_id: str,
    visible: dict[str, Any],
    rendering_mode: str,
) -> dict[str, Any]:
    table = visible.get("compact_table")
    total_row = visible.get("total_row")
    advisor_note = visible.get("advisor_note")
    budget = _budget_for_report(report_id)
    visible_table_rows = (len(table["rows"]) if table else 0) + (1 if total_row else 0)
    return {
        **budget,
        "actual_headline_sentences": _sentence_count(visible["headline_sentence"]),
        "actual_headline_metrics": len(visible["headline_metrics"]),
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
    if budget["actual_visible_table_rows"] > budget["max_visible_table_rows"]:
        raise ValueError(f"{view['report_element_id']} exceeds table row budget")
    if budget["actual_caveats"] > budget["max_caveats"]:
        raise ValueError(f"{view['report_element_id']} exceeds caveat budget")
    if budget["actual_advisor_notes"] > budget["max_advisor_notes"]:
        raise ValueError(f"{view['report_element_id']} exceeds advisor note budget")
    if (
        budget["actual_visible_table_rows"]
        > DEFAULT_INFORMATION_BUDGET["max_visible_table_rows"]
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
    if "selected mandate effect" not in visible_text:
        raise ValueError(f"{view['report_element_id']} lacks selected mandate effect")
    if "percentage points of total portfolio return" not in view["effect_basis_note"]:
        raise ValueError(f"{view['report_element_id']} lacks effect basis note")
    if view["manager_implementation_visible_in_primary_report"]:
        raise ValueError("Manager implementation cannot be visible in primary report")


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
    table = view.get("compact_table")
    if table:
        parts.append(table["title"])
        parts.extend(table["columns"])
        for row in table["rows"]:
            parts.extend(str(row[column]) for column in table["columns"])
    total_row = view.get("total_row")
    if total_row:
        parts.extend(str(value) for value in total_row.values())
    parts.append(view["effect_basis_note"])
    parts.extend(view.get("caveats") or [])
    if view.get("advisor_note"):
        parts.append(view["advisor_note"])
    return "\n".join(parts)


def _serializable_manager_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "manager_id": row["manager_id"],
        "display_name": row["display_name"],
        "neutral_weight": _weight_number(row["neutral_weight"]),
        "target_weight": _weight_number(row["target_weight"]),
        "actual_weight": _weight_number(row["actual_weight"]),
        "weight_drift": _weight_number(row["weight_drift"]),
        "mandate_benchmark_return": _return_number(row["mandate_benchmark_return"]),
        "actual_manager_return_context": _return_number(
            row["actual_manager_return_context"]
        ),
        "selected_mandate_effect": _return_number(row["selected_mandate_effect"]),
        "target_weighting_effect": _return_number(row["target_weighting_effect"]),
        "funding_drift_effect": _return_number(row["funding_drift_effect"]),
        "advisor_policy_effect": _return_number(row["advisor_policy_effect"]),
        "drift_status": row["drift_status"],
        "benchmark_basis": row["benchmark_basis"],
        "benchmark_basis_type": row["benchmark_basis_type"],
        "effect_basis": "percentage_points_of_total_portfolio_return",
        "caveats": row["caveats"],
    }


def _tie_out(observed: Decimal, expected: Decimal) -> dict[str, Any]:
    difference = observed - expected
    return {
        "observed": _return_number(observed),
        "expected": _return_number(expected),
        "difference": _return_number(difference),
        "tolerance": _return_number(TIE_OUT_TOLERANCE),
        "status": _residual_status(difference),
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


def _render_markdown_table(
    table: dict[str, Any], total_row: dict[str, Any] | None = None
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
        "within_tolerance": "Within tolerance",
        "review": "Review",
        "material_drift": "Material drift",
        "total": "Advisor policy total",
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
        description="Generate advisor policy attribution v2 outputs and mockups."
    )
    parser.add_argument("--policy-pack-dir", default=str(DEFAULT_POLICY_PACK_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument("--mockup-dir", default=str(DEFAULT_MOCKUP_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_advisor_policy_attribution_v2(
        policy_pack_dir=args.policy_pack_dir,
        output_dir=args.output_dir,
        input_dir=args.input_dir,
        view_dir=args.view_dir,
        mockup_dir=args.mockup_dir,
    )

    print(
        "Advisor policy attribution outputs: "
        f"{summary['calculated_artifact_count']} -> {summary['output_dir']}"
    )
    print(
        "Advisor policy attribution report inputs: "
        f"{summary['report_input_count']} -> {summary['input_dir']}"
    )
    print(
        "Advisor policy attribution report views: "
        f"{summary['report_view_count']} -> {summary['view_dir']}"
    )
    print(
        "Advisor policy attribution Markdown mockups: "
        f"{summary['markdown_mockup_count']} -> {summary['mockup_dir']}"
    )
    print("Source policy pack: " + summary["source_policy_mandate_pack_id"])
    print("Generated report ids: " + ", ".join(summary["report_ids"]))
    print("Row tie-outs passed: " + str(summary["row_tie_outs_passed"]))
    print("Manager implementation visible in primary report: False")
    print("Gated reports not generated: " + ", ".join(summary["gated_reports_not_generated"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
