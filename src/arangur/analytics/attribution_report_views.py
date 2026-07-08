from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-08T00:00:00Z"

INPUT_SCHEMA_VERSION = "attribution_report_input.v1"
INPUT_SUMMARY_SCHEMA_VERSION = "attribution_report_input_summary.v1"
VIEW_SCHEMA_VERSION = "attribution_report_view.v1"
VIEW_SUMMARY_SCHEMA_VERSION = "attribution_report_view_summary.v1"
GATED_INDEX_SCHEMA_VERSION = "attribution_report_gated_deferred_index.v1"
GENERATOR_VERSION = "attribution_report_views.calculated.v1"

DEFAULT_PREREQUISITE_DIR = Path(
    "data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1"
)
DEFAULT_CALCULATED_DIR = Path(
    "data/simulation/attribution_calculated/synthetic_attribution_engine_v1"
)
DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs/attribution_v1")
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/attribution_v1")
DEFAULT_MOCKUP_DIR = Path("docs/product/report_mockups/attribution_v1")

TIMING_UNAVAILABLE_TEXT = (
    "Timing is not shown separately because clean trade/holding history, flow treatment, "
    "and an approved timing method are not present."
)
RETURN_BASIS_EXPLANATION = "Return columns are shown on a 100% theme-bucket basis."
EFFECT_BASIS_EXPLANATION = (
    "Effect columns are measured in percentage points of total portfolio return."
)
POLICY_WEIGHT_LABEL = "Policy Weight"
ACTUAL_WEIGHT_LABEL = "Actual Weight"
ACTIVE_RETURN_DEFINITION_TEXT = (
    "Active Return is Portfolio Return minus Theme Benchmark Return inside the bucket."
)
ACTIVE_RETURN_NOT_TOTAL_EFFECT_TEXT = (
    "Active Return is not the same as Total Effect because Total Effect is measured "
    "against the whole portfolio and includes theme choice/weighting effects."
)
UNDERWEIGHTING_NOTE_TEXT = (
    "A theme can beat its theme benchmark but still have a negative total effect if "
    "the portfolio was underweight that theme relative to the policy/global benchmark mix."
)

CALCULATED_ARTIFACT_FILES = {
    "manifest": "calculated_attribution_engine_manifest.json",
    "whole_portfolio_summary": "whole_portfolio_calculated_attribution_summary.json",
    "theme_benchmark_detail": "theme_benchmark_calculated_detail.json",
    "theme_asset_detail": "theme_asset_calculated_attribution_detail.json",
    "manager_summary": "manager_calculated_attribution_summary.json",
    "quality_summary": "calculated_attribution_quality_summary.json",
}

REPORT_SPECS: tuple[dict[str, str], ...] = (
    {
        "report_id": "integrated_performance_attribution_summary",
        "input_filename": "integrated_performance_attribution_summary_input.json",
        "view_filename": "integrated_performance_attribution_summary_view.json",
        "mockup_filename": "integrated_performance_attribution_summary_mockup_v1.md",
    },
    {
        "report_id": "integrated_performance_attribution_detail",
        "input_filename": "integrated_performance_attribution_detail_input.json",
        "view_filename": "integrated_performance_attribution_detail_view.json",
        "mockup_filename": "integrated_performance_attribution_detail_mockup_v1.md",
    },
    {
        "report_id": "manager_attribution_summary",
        "input_filename": "manager_attribution_summary_input.json",
        "view_filename": "manager_attribution_summary_view.json",
        "mockup_filename": "manager_attribution_summary_mockup_v1.md",
    },
    {
        "report_id": "lens_based_performance_attribution_ai_adoption",
        "input_filename": "lens_based_performance_attribution_ai_adoption_input.json",
        "view_filename": "lens_based_performance_attribution_ai_adoption_view.json",
        "mockup_filename": "lens_based_performance_attribution_ai_adoption_mockup_v1.md",
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

UNSUPPORTED_CALCULATED_OUTPUTS = {
    "input": ("lens_based_performance_attribution_energy_security_input.json",),
    "view": ("lens_based_performance_attribution_energy_security_view.json",),
    "mockup": ("lens_based_performance_attribution_energy_security_mockup_v1.md",),
}

GATED_REPORTS: tuple[dict[str, str], ...] = (
    {
        "report_id": "timing_attribution",
        "display_title": "Timing Attribution",
        "status": "Unavailable",
        "reason": "Unavailable unless clean history, flow treatment, and an approved timing methodology exist.",
    },
    {
        "report_id": "production_attribution_report",
        "display_title": "Production Attribution Report",
        "status": "Gated",
        "reason": "Gated on real benchmark, return, holding, flow data, and formal approval.",
    },
    {
        "report_id": "scenario_versus_benchmark",
        "display_title": "Scenario Versus Benchmark",
        "status": "Gated",
        "reason": "Gated unless benchmark scenario values or an approved benchmark scenario methodology exist.",
    },
    {
        "report_id": "probabilistic_scenario_range",
        "display_title": "Probabilistic Scenario Range",
        "status": "Gated",
        "reason": "Gated until probabilistic analytics and range methodology exist.",
    },
    {
        "report_id": "current_versus_proposed_attribution",
        "display_title": "Current Versus Proposed Attribution",
        "status": "Gated",
        "reason": "Gated on proposed allocation data, comparison methodology, and approval.",
    },
    {
        "report_id": "integrated_attribution_summary_by_manager",
        "display_title": "Integrated Attribution Summary - By Manager",
        "status": "Design soon",
        "reason": "Future variant; keep separate from Manager Attribution Summary until manager-level integrated summary shape is approved.",
    },
    {
        "report_id": "integrated_attribution_detail_by_manager",
        "display_title": "Integrated Attribution Detail - By Manager",
        "status": "Design soon",
        "reason": "Future variant; needs approved manager-level integrated detail shape before mockup generation.",
    },
    {
        "report_id": "lens_based_performance_attribution_energy_security",
        "display_title": "Lens-Based Performance Attribution - Energy Security",
        "status": "Gated for calculated attribution",
        "reason": "Gated until Energy Security calculation inputs and calculated attribution outputs exist; the current calculated engine supports AI Adoption only.",
    },
)

DEFAULT_INFORMATION_BUDGET = {
    "max_headline_sentences": 1,
    "max_headline_metrics": 3,
    "max_visible_table_rows": 5,
    "max_caveats": 2,
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
    "valuation trace",
    "pricing function registry",
    "scenario basis vector",
    "raw json",
    "debug",
    "brinson",
    "strategy/lens-bucket",
    "strategy lens-bucket",
    "strategy lens bucket",
    "proxy return",
    "bucket return",
    "contribution",
    "not separately measured",
    "not timing",
    "residual is not timing",
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
    prerequisite_dir: str | Path = DEFAULT_PREREQUISITE_DIR,
    calculated_dir: str | Path = DEFAULT_CALCULATED_DIR,
) -> dict[str, Any]:
    prerequisite_root = Path(prerequisite_dir)
    calculated_root = Path(calculated_dir)
    calculated_outputs = {
        name: _load_json(calculated_root / filename)
        for name, filename in CALCULATED_ARTIFACT_FILES.items()
    }
    manifest = calculated_outputs["manifest"]
    quality = calculated_outputs["quality_summary"]
    selected_lens = manifest["selected_attribution_lens"]
    if manifest["engine_id"] != "synthetic_attribution_engine_v1":
        raise ValueError("Unexpected calculated attribution engine id")
    if selected_lens["lens_id"] != "ai_adoption":
        raise ValueError("Attribution report v1 calculated mockups require AI Adoption outputs")
    if quality["timing_status"] != "unavailable":
        raise ValueError("Timing attribution must remain unavailable")
    if not quality["summary_ready_from_calculated_outputs"]:
        raise ValueError("Calculated summary output is not marked ready")
    if not quality["detail_ready_from_calculated_outputs"]:
        raise ValueError("Calculated detail output is not marked ready")
    if not quality["manager_ready_from_calculated_outputs"]:
        raise ValueError("Calculated manager output is not marked ready")

    return {
        "source_paths": _source_paths(prerequisite_root, calculated_root),
        "prerequisite_manifest": _load_json(
            prerequisite_root / "synthetic_attribution_prerequisite_pack_manifest.json"
        ),
        "benchmark_catalog": _load_json(prerequisite_root / "portfolio_benchmark_catalog.json"),
        "proxy_map": _load_json(prerequisite_root / "lens_bucket_benchmark_proxy_map.json"),
        "calculated": calculated_outputs,
        "calculated_artifact_files": dict(CALCULATED_ARTIFACT_FILES),
        "selected_calculated_lens": selected_lens,
    }


def build_attribution_report_inputs(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    benchmark = context["benchmark_catalog"]["benchmarks"][0]
    inputs = {
        "integrated_performance_attribution_summary": _integrated_summary_input(
            context,
            benchmark,
        ),
        "integrated_performance_attribution_detail": _integrated_detail_input(
            context,
            benchmark,
        ),
        "manager_attribution_summary": _manager_summary_input(context),
        "lens_based_performance_attribution_ai_adoption": _lens_attribution_input(context),
    }

    _validate_report_ids(inputs)
    return inputs


def build_attribution_report_views(
    inputs: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    _validate_report_ids(inputs)
    views: dict[str, dict[str, Any]] = {}
    for report_id in BUILD_NOW_REPORT_IDS:
        payload = inputs[report_id]
        visible = payload["visible_content"]
        view = {
            "schema_version": VIEW_SCHEMA_VERSION,
            "generator_version": GENERATOR_VERSION,
            "generated_at": GENERATED_AT,
            "synthetic_data": True,
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
            "period_start": payload["period_start"],
            "period_end": payload["period_end"],
            "headline_sentence": visible["headline_sentence"],
            "headline_metrics": visible["headline_metrics"],
            "contribution_bridge": visible.get("contribution_bridge"),
            "compact_table": visible.get("compact_table"),
            "caveats": visible.get("caveats", []),
            "advisor_note": visible.get("advisor_note"),
            "timing_status": payload["timing_status"],
            "residual_policy": payload["residual_policy"],
            "benchmark_or_proxy_basis": payload["benchmark_or_proxy_basis"],
            "source_calculated_attribution_engine_id": payload[
                "source_calculated_attribution_engine_id"
            ],
            "source_calculated_output_artifacts": payload[
                "source_calculated_output_artifacts"
            ],
            "source_calculated_output_refs": payload["source_calculated_output_refs"],
            "calculated_from_lower_level_inputs": payload[
                "calculated_from_lower_level_inputs"
            ],
            "supplied_or_legacy_sections": payload["supplied_or_legacy_sections"],
            "internal_source_refs": payload["internal_source_refs"],
            "source_prerequisite_pack_refs": payload["source_prerequisite_pack_refs"],
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

    bridge = view.get("contribution_bridge")
    if bridge:
        lines.extend([f"## {bridge['title']}", ""])
        lines.extend(_render_markdown_table(bridge))
        lines.append("")

    table = view.get("compact_table")
    if table:
        lines.extend([f"## {table['title']}", ""])
        lines.extend(_render_markdown_table(table))
        lines.append("")

    if view.get("caveats"):
        lines.extend(["## Caveats", ""])
        for caveat in view["caveats"]:
            lines.append(f"- {caveat}")
        lines.append("")

    if view.get("advisor_note"):
        lines.extend(["## Advisor Note", "", view["advisor_note"], ""])

    markdown = "\n".join(lines).rstrip() + "\n"
    _validate_markdown(view, markdown)
    return markdown


def generate_attribution_report_views(
    *,
    prerequisite_dir: str | Path = DEFAULT_PREREQUISITE_DIR,
    calculated_dir: str | Path = DEFAULT_CALCULATED_DIR,
    input_dir: str | Path = DEFAULT_INPUT_DIR,
    view_dir: str | Path = DEFAULT_VIEW_DIR,
    mockup_dir: str | Path = DEFAULT_MOCKUP_DIR,
) -> dict[str, Any]:
    input_path = Path(input_dir)
    view_path = Path(view_dir)
    mockup_path = Path(mockup_dir)
    input_path.mkdir(parents=True, exist_ok=True)
    view_path.mkdir(parents=True, exist_ok=True)
    mockup_path.mkdir(parents=True, exist_ok=True)

    context = load_source_context(
        prerequisite_dir=prerequisite_dir,
        calculated_dir=calculated_dir,
    )
    inputs = build_attribution_report_inputs(context)
    views = build_attribution_report_views(inputs)
    _remove_unsupported_calculated_outputs(input_path, view_path, mockup_path)

    input_files: list[str] = []
    for report_id in BUILD_NOW_REPORT_IDS:
        filename = INPUT_FILENAME_BY_REPORT_ID[report_id]
        _write_json(input_path / filename, inputs[report_id])
        input_files.append(filename)

    input_summary = _input_summary(input_files, inputs)
    _write_json(input_path / "attribution_report_input_summary.json", input_summary)
    input_files.append("attribution_report_input_summary.json")

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
    _write_json(view_path / "gated_deferred_attribution_report_index.json", gated_index)
    view_files.append("gated_deferred_attribution_report_index.json")

    readme = render_mockup_readme(views, gated_index)
    (mockup_path / "README.md").write_text(readme, encoding="utf-8")
    mockup_files.append("README.md")

    view_summary = _view_summary(view_files, mockup_files, views, gated_index)
    _write_json(view_path / "attribution_report_view_summary.json", view_summary)
    view_files.append("attribution_report_view_summary.json")

    return {
        "schema_version": "attribution_report_generation_summary.v1",
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "source_calculated_attribution_engine_id": context["calculated"]["manifest"][
            "engine_id"
        ],
        "report_input_count": len(inputs),
        "report_view_count": len(views),
        "markdown_mockup_count": len(MOCKUP_FILENAME_BY_REPORT_ID),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "input_files": input_files,
        "view_files": view_files,
        "mockup_files": mockup_files,
        "gated_reports_not_generated": [
            row["report_id"] for row in gated_index["gated_or_deferred_reports"]
        ],
        "input_dir": _as_posix(input_path),
        "view_dir": _as_posix(view_path),
        "mockup_dir": _as_posix(mockup_path),
    }


def render_mockup_readme(
    views: dict[str, dict[str, Any]],
    gated_index: dict[str, Any],
) -> str:
    lines = [
        "# Attribution v1 Report Mockups",
        "",
        (
            "These product-review mockups are generated from attribution v1 view fixtures "
            "that consume the calculated synthetic attribution output pack. They remain "
            "local synthetic-demo only and are not wired into Advisor Preview, Populate, "
            "Present, generated reports, Docker, deployment, live data, or dependencies."
        ),
        (
            "AI Adoption is the selected calculated attribution lens. Timing remains "
            "unavailable, residual / unexplained stays separate, and production/client "
            "attribution remains gated."
        ),
        (
            "Detail and lens tables distinguish bucket-level return columns from effects "
            "on total portfolio return, and Manager Attribution Summary separates largest driver, other "
            "measured effects, and residual / unexplained."
        ),
        "",
        "## Generated Mockups",
        "",
    ]
    for report_id in BUILD_NOW_REPORT_IDS:
        view = views[report_id]
        filename = MOCKUP_FILENAME_BY_REPORT_ID[report_id]
        lines.append(f"- [{view['display_title']}]({filename})")
    lines.extend(["", "## Gated Or Deferred", ""])
    for row in gated_index["gated_or_deferred_reports"]:
        lines.append(f"- {row['display_title']} ({row['status']}): {row['reason']}")
    return "\n".join(lines).rstrip() + "\n"


def _integrated_summary_input(
    context: dict[str, Any],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    whole = context["calculated"]["whole_portfolio_summary"]
    rows = [
        _bridge_row(
            "Theme Choice Effect",
            whole["theme_benchmark_selection_effect"],
            "Calculated from policy theme benchmark return minus global benchmark return.",
        ),
        _bridge_row(
            "Theme Weight Effect",
            whole["theme_benchmark_sizing_effect"],
            "Calculated from actual-weight theme benchmark return minus policy theme benchmark return.",
        ),
        _bridge_row(
            "Asset Choice Effect",
            whole["asset_selection_effect"],
            "Calculated from per-theme reference-weight asset returns.",
        ),
        _bridge_row(
            "Asset Weight Effect",
            whole["asset_sizing_effect"],
            "Calculated from per-theme actual-weight asset returns.",
        ),
        _bridge_row(
            "Residual / unexplained",
            whole["residual_unexplained"],
            "Calculated reconciler after visible attribution effects.",
        ),
    ]
    largest = max(rows, key=lambda row: abs(float(row["numeric_value"])))
    visible = {
        "headline_sentence": (
            f"Portfolio return exceeded the global benchmark by "
            f"{_format_signed_percent(whole['relative_return'])}, with "
            f"{largest['Effect Driver'].lower()} the largest calculated driver."
        ),
        "headline_metrics": [
            _metric(
                "Portfolio return",
                whole["actual_portfolio_return"],
                _format_percent(whole["actual_portfolio_return"]),
            ),
            _metric(
                "Global benchmark return",
                whole["global_benchmark_return"],
                _format_percent(whole["global_benchmark_return"]),
            ),
            _metric(
                "Relative return",
                whole["relative_return"],
                _format_signed_percent(whole["relative_return"]),
            ),
        ],
        "contribution_bridge": _table(
            "Calculated Effect Summary",
            ["Effect Driver", "Effect", "Interpretation"],
            rows,
        ),
        "caveats": [
            "Synthetic local-demo returns and benchmark inputs only.",
            TIMING_UNAVAILABLE_TEXT,
        ],
        "advisor_note": (
            "Global benchmark is the whole-portfolio benchmark; theme benchmarks are "
            "bucket-level benchmarks inside the selected AI Adoption lens. Real/client "
            "attribution remains gated until production returns, benchmark maps, flows, "
            "and methodology are approved."
        ),
    }
    return _report_input(
        report_element_id="integrated_performance_attribution_summary",
        display_title="Integrated Performance Attribution Summary",
        report_family="Integrated Performance Attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "Did the portfolio add value versus the global benchmark, and what were the largest calculated effects?"
        ),
        audience_tier="Client briefing and advisor review",
        summary_detail_status="Summary",
        representation_level="Whole portfolio versus benchmark",
        denominator_category_system="Benchmark-relative effect bridge",
        rendering_mode="summary_first",
        context=context,
        visible_content=visible,
        timing_status=whole["timing_status"],
        residual_policy=_residual_policy_text(),
        benchmark_or_proxy_basis=benchmark["display_name"],
        source_calculated_output_artifact_keys=(
            "manifest",
            "whole_portfolio_summary",
            "quality_summary",
        ),
        table_validation={
            "bridge_row_count": len(rows),
            "effects_sum": _round_return(
                sum(float(row["numeric_value"]) for row in rows)
            ),
            "relative_return": whole["relative_return"],
            "ties_to_relative_return": abs(
                sum(float(row["numeric_value"]) for row in rows)
                - whole["relative_return"]
            )
            <= 0.000001,
            "uses_calculated_whole_portfolio_summary": True,
            "timing_contribution_included": False,
            "residual_label": "Residual / unexplained",
        },
    )


def _integrated_detail_input(
    context: dict[str, Any],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    whole = context["calculated"]["whole_portfolio_summary"]
    detail = context["calculated"]["theme_benchmark_detail"]
    visible_rows = [_theme_detail_visible_row(row) for row in detail["rows"]]
    visible = {
        "headline_sentence": (
            f"Calculated AI Adoption theme rows explain "
            f"{_format_signed_percent(detail['totals']['total_effect'])} of relative return "
            "before the separate residual / unexplained reconciler."
        ),
        "headline_metrics": [
            _metric(
                "Theme row total",
                detail["totals"]["total_effect"],
                _format_signed_percent(detail["totals"]["total_effect"]),
            ),
            _metric(
                "Residual / unexplained",
                whole["residual_unexplained"],
                _format_signed_percent(whole["residual_unexplained"]),
            ),
            _metric(
                "Relative return",
                whole["relative_return"],
                _format_signed_percent(whole["relative_return"]),
            ),
        ],
        "compact_table": _table(
            "Calculated Theme Return and Effect Detail",
            [
                "Theme Bucket",
                POLICY_WEIGHT_LABEL,
                ACTUAL_WEIGHT_LABEL,
                "Portfolio Return",
                "Theme Benchmark Return",
                "Active Return",
                "Theme Choice Effect",
                "Theme Weight Effect",
                "Asset Choice Effect",
                "Asset Weight Effect",
                "Residual / Reconciler",
                "Total Effect",
            ],
            visible_rows,
        ),
        "caveats": [
            "Synthetic local-demo returns and theme benchmarks only; some theme benchmarks are synthetic proxy benchmarks for demo purposes.",
            TIMING_UNAVAILABLE_TEXT,
        ],
        "advisor_note": (
            f"Policy Weight is the policy/equal-weight benchmark mix for AI Adoption; "
            f"Actual Weight is the portfolio's actual share in that theme bucket. "
            f"{RETURN_BASIS_EXPLANATION} {EFFECT_BASIS_EXPLANATION} "
            f"{ACTIVE_RETURN_DEFINITION_TEXT} {ACTIVE_RETURN_NOT_TOTAL_EFFECT_TEXT} "
            f"{UNDERWEIGHTING_NOTE_TEXT}"
        ),
    }
    return _report_input(
        report_element_id="integrated_performance_attribution_detail",
        display_title="Integrated Performance Attribution Detail",
        report_family="Integrated Performance Attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "How do calculated theme benchmark and asset effects explain the synthetic benchmark-to-portfolio bridge?"
        ),
        audience_tier="Advisor review",
        summary_detail_status="Detail",
        representation_level="Whole portfolio versus benchmark",
        denominator_category_system="AI Adoption theme benchmark calculated rows",
        rendering_mode="detail_first",
        context=context,
        visible_content=visible,
        timing_status=detail["timing_status"],
        residual_policy=_residual_policy_text(),
        benchmark_or_proxy_basis=benchmark["display_name"],
        source_calculated_output_artifact_keys=(
            "manifest",
            "whole_portfolio_summary",
            "theme_benchmark_detail",
            "theme_asset_detail",
            "quality_summary",
        ),
        table_validation={
            "theme_benchmark_lens": detail["selected_attribution_lens"]["display_name"],
            "theme_bucket_row_count": len(detail["rows"]),
            "theme_benchmark_selection_total": detail["totals"][
                "theme_benchmark_selection_effect"
            ],
            "theme_benchmark_sizing_total": detail["totals"][
                "theme_benchmark_sizing_effect"
            ],
            "asset_selection_total": detail["totals"]["asset_selection_effect"],
            "asset_sizing_total": detail["totals"]["asset_sizing_effect"],
            "theme_row_total_effect": detail["totals"]["total_effect"],
            "residual_unexplained": whole["residual_unexplained"],
            "relative_return": whole["relative_return"],
            "ties_to_summary_calculated_effects": detail["tie_out_status"][
                "ties_to_summary_calculated_effects"
            ],
            "uses_calculated_theme_benchmark_detail": True,
            "component_effects_calculated": True,
            "detail_is_not_summary_bridge": True,
            "active_return_bridge_included": True,
            "active_return_definition": "portfolio_return_minus_theme_benchmark_return",
            "return_basis_explanation": RETURN_BASIS_EXPLANATION,
            "effect_basis_explanation": EFFECT_BASIS_EXPLANATION,
            "policy_weight_label": POLICY_WEIGHT_LABEL,
            "actual_weight_label": ACTUAL_WEIGHT_LABEL,
            "effect_columns_basis": "percentage_points_of_total_portfolio_return",
            "active_return_is_not_total_effect": True,
            "total_effect_distinguished_from_active_return": True,
            "underweighting_note_included": True,
            "timing_contribution_included": False,
            "residual_label": "Residual / unexplained",
        },
    )


def _manager_summary_input(context: dict[str, Any]) -> dict[str, Any]:
    manager_summary = context["calculated"]["manager_summary"]
    managers = list(manager_summary["managers"])
    rows = []
    for manager in managers:
        rows.append(
            {
                "Manager": manager["display_name"],
                "Return": _format_percent(manager["manager_return"]),
                "Manager Benchmark Return": _format_percent(
                    manager["manager_benchmark_return"]
                ),
                "Relative Return": _format_signed_percent(manager["relative_return"]),
                "Largest Driver": _largest_manager_driver(manager),
                "Other Measured Effects": _format_signed_percent(
                    _manager_other_measured_effects(manager)
                ),
                "Residual / unexplained": _format_signed_percent(
                    manager["residual_unexplained"]
                ),
                "relative_return": manager["relative_return"],
            }
        )
    visible_rows = [
        {
            "Manager": row["Manager"],
            "Return": row["Return"],
            "Manager Benchmark Return": row["Manager Benchmark Return"],
            "Relative Return": row["Relative Return"],
            "Largest Driver": row["Largest Driver"],
            "Other Measured Effects": row["Other Measured Effects"],
            "Residual / unexplained": row["Residual / unexplained"],
        }
        for row in rows
    ]
    visible = {
        "headline_sentence": (
            "All six current managers tie to calculated manager attribution outputs, with timing unavailable."
        ),
        "headline_metrics": [
            _metric("Managers covered", len(rows), str(len(rows))),
            _metric(
                "Manager tie-outs",
                manager_summary["coverage_summary"]["manager_count"],
                "All pass",
            ),
            _metric("Timing status", manager_summary["timing_status"], "Unavailable"),
        ],
        "compact_table": _table(
            "Calculated Manager Attribution Summary",
            [
                "Manager",
                "Return",
                "Manager Benchmark Return",
                "Relative Return",
                "Largest Driver",
                "Other Measured Effects",
                "Residual / unexplained",
            ],
            visible_rows,
        ),
        "caveats": [
            "Synthetic manager benchmarks may use proxy benchmarks for demo purposes; they are not production recommendations.",
            TIMING_UNAVAILABLE_TEXT,
        ],
        "advisor_note": (
            "Manager Benchmark Return is the manager/sleeve benchmark; this synthetic demo "
            "uses an explicit manager-specific mandate proxy plus an AI Adoption "
            "theme-benchmark blend. The table shows each manager's largest driver; other "
            "measured effects and residual complete the tie-out."
        ),
    }
    return _report_input(
        report_element_id="manager_attribution_summary",
        display_title="Manager Attribution Summary",
        report_family="Manager Attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "Which managers added or lost value versus their manager benchmarks, and what calculated driver mattered most?"
        ),
        audience_tier="Advisor review",
        summary_detail_status="Summary",
        representation_level="Manager versus manager-specific benchmark",
        denominator_category_system="Manager-specific benchmark relative returns",
        rendering_mode="table_first",
        context=context,
        visible_content=visible,
        timing_status=manager_summary["timing_status"],
        residual_policy=_manager_residual_policy_text(),
        benchmark_or_proxy_basis="Manager-specific synthetic benchmarks",
        source_calculated_output_artifact_keys=(
            "manifest",
            "manager_summary",
            "quality_summary",
        ),
        table_validation={
            "current_manager_count": len(managers),
            "manager_rows_shown": len(visible_rows),
            "all_current_managers_covered": manager_summary["coverage_summary"][
                "all_current_managers_covered"
            ],
            "all_manager_benchmark_basis_types_explicit": manager_summary[
                "coverage_summary"
            ]["all_manager_benchmark_basis_types_explicit"],
            "manager_tie_outs_reconcile": manager_summary["coverage_summary"][
                "manager_tie_outs_reconcile"
            ],
            "uses_calculated_manager_summary": True,
            "timing_column_removed": True,
            "residual_labeled_separately": True,
            "other_measured_effects_column_included": True,
            "largest_driver_plus_other_measured_plus_residual_ties": all(
                _manager_driver_tie_out(manager) for manager in managers
            ),
        },
    )


def _lens_attribution_input(context: dict[str, Any]) -> dict[str, Any]:
    detail = context["calculated"]["theme_benchmark_detail"]
    selected_lens = detail["selected_attribution_lens"]
    rows = [
        {
            "Theme Bucket": row["bucket_display_name"],
            ACTUAL_WEIGHT_LABEL: _format_percent(row["actual_portfolio_weight"]),
            "Portfolio Return": _format_percent(row["actual_portfolio_theme_return"]),
            "Theme Benchmark Return": _format_percent(row["theme_benchmark_return"]),
            "Active Return": _format_signed_percent(_theme_active_return(row)),
            "Total Effect": _format_signed_percent(row["total_effect"]),
            "total_effect": row["total_effect"],
        }
        for row in detail["rows"]
    ]
    total = _round_return(sum(float(row["total_effect"]) for row in rows))
    top_positive = max(rows, key=lambda row: float(row["total_effect"]))
    top_negative = min(rows, key=lambda row: float(row["total_effect"]))
    visible_rows = [
        {
            "Theme Bucket": row["Theme Bucket"],
            ACTUAL_WEIGHT_LABEL: row[ACTUAL_WEIGHT_LABEL],
            "Portfolio Return": row["Portfolio Return"],
            "Theme Benchmark Return": row["Theme Benchmark Return"],
            "Active Return": row["Active Return"],
            "Total Effect": row["Total Effect"],
        }
        for row in rows
    ]
    visible = {
        "headline_sentence": (
            f"Under the {selected_lens['display_name']} lens, {top_positive['Theme Bucket']} "
            "is the largest positive Total Effect; Active Return is shown separately."
        ),
        "headline_metrics": [
            _metric("Net calculated theme effect", total, _format_signed_percent(total)),
            _metric(
                "Largest positive theme bucket",
                top_positive["total_effect"],
                f"{top_positive['Theme Bucket']} ({_format_signed_percent(top_positive['total_effect'])})",
            ),
            _metric(
                "Largest negative theme bucket",
                top_negative["total_effect"],
                f"{top_negative['Theme Bucket']} ({_format_signed_percent(top_negative['total_effect'])})",
            ),
        ],
        "compact_table": _table(
            f"{selected_lens['display_name']} Calculated Theme Performance",
            [
                "Theme Bucket",
                ACTUAL_WEIGHT_LABEL,
                "Portfolio Return",
                "Theme Benchmark Return",
                "Active Return",
                "Total Effect",
            ],
            visible_rows,
        ),
        "caveats": [
            "Some synthetic theme benchmarks are proxy benchmarks for demo purposes; they are not production recommendations.",
            "Energy Security calculated attribution remains gated until a calculated output pack exists for that lens.",
        ],
        "advisor_note": (
            f"Theme benchmarks apply bucket-by-bucket inside AI Adoption. "
            f"{RETURN_BASIS_EXPLANATION} {EFFECT_BASIS_EXPLANATION} "
            f"{ACTIVE_RETURN_DEFINITION_TEXT} {ACTIVE_RETURN_NOT_TOTAL_EFFECT_TEXT} "
            f"{TIMING_UNAVAILABLE_TEXT}"
        ),
    }
    return _report_input(
        report_element_id="lens_based_performance_attribution_ai_adoption",
        display_title="Lens-Based Performance Attribution - AI Adoption",
        report_family="Lens-Based Performance Attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "Which AI Adoption theme buckets explain relative performance versus their theme benchmarks?"
        ),
        audience_tier="Advisor review",
        summary_detail_status="Summary",
        representation_level="AI Adoption theme bucket",
        denominator_category_system="AI Adoption theme buckets versus synthetic theme benchmarks",
        rendering_mode="table_first",
        context=context,
        visible_content=visible,
        timing_status=detail["timing_status"],
        residual_policy=(
            "No residual row is shown in the calculated theme-bucket summary; portfolio residual remains in the integrated summary/detail reports. "
            "Residual / unexplained may include unmeasured timing, data, flow, rounding, or reconciliation effects."
        ),
        benchmark_or_proxy_basis="Synthetic AI Adoption theme benchmark set",
        source_calculated_output_artifact_keys=(
            "manifest",
            "theme_benchmark_detail",
            "quality_summary",
        ),
        table_validation={
            "selected_calculated_lens": selected_lens["display_name"],
            "lens_bucket_count": len(rows),
            "all_lens_buckets_included": True,
            "contains_neutral_bucket": any("Neutral" in row["Theme Bucket"] for row in rows),
            "contains_review_bucket": any("Review" in row["Theme Bucket"] for row in rows),
            "relative_contribution_total": total,
            "uses_calculated_theme_benchmark_detail": True,
            "unsupported_calculated_lenses_gated": ["Energy Security"],
            "active_return_bridge_included": True,
            "active_return_definition": "portfolio_return_minus_theme_benchmark_return",
            "return_basis_explanation": RETURN_BASIS_EXPLANATION,
            "effect_basis_explanation": EFFECT_BASIS_EXPLANATION,
            "actual_weight_label": ACTUAL_WEIGHT_LABEL,
            "effect_columns_basis": "percentage_points_of_total_portfolio_return",
            "active_return_is_not_total_effect": True,
            "total_effect_distinguished_from_active_return": True,
            "timing_contribution_included": False,
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
    timing_status: str,
    residual_policy: str,
    benchmark_or_proxy_basis: str,
    source_calculated_output_artifact_keys: tuple[str, ...],
    table_validation: dict[str, Any],
) -> dict[str, Any]:
    manifest = context["calculated"]["manifest"]
    source_artifacts = [
        context["calculated_artifact_files"][key]
        for key in source_calculated_output_artifact_keys
    ]
    source_refs = [
        context["source_paths"]["calculated"][key]
        for key in source_calculated_output_artifact_keys
    ]
    return {
        "schema_version": INPUT_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
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
        "period_start": manifest["period_start"],
        "period_end": manifest["period_end"],
        "selected_calculated_lens": manifest["selected_attribution_lens"],
        "visible_content": visible_content,
        "timing_status": timing_status,
        "residual_policy": residual_policy,
        "residual_policy_details": manifest["residual_policy"],
        "benchmark_or_proxy_basis": benchmark_or_proxy_basis,
        "source_calculated_attribution_engine_id": manifest["engine_id"],
        "source_calculated_output_artifacts": source_artifacts,
        "source_calculated_output_refs": source_refs,
        "calculated_from_lower_level_inputs": True,
        "calculated_outputs_source_of_truth": True,
        "supplied_or_legacy_sections": [],
        "internal_source_refs": [
            *source_refs,
            context["source_paths"]["prerequisite"]["benchmark_catalog"],
        ],
        "source_prerequisite_pack_refs": [
            context["prerequisite_manifest"]["pack_id"],
        ],
        "table_validation": table_validation,
        "information_budget": _budget_for_report(report_element_id),
        "gated_or_deferred": False,
        "not_wired_into_advisor_ui": True,
        "not_wired_into_generated_reports": True,
    }


def _input_summary(input_files: list[str], inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    first = next(iter(inputs.values()))
    return {
        "schema_version": INPUT_SUMMARY_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "source_calculated_attribution_engine_id": first[
            "source_calculated_attribution_engine_id"
        ],
        "calculated_outputs_source_of_truth": True,
        "report_input_count": len(inputs),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "input_files": input_files,
        "mockups_generated_from_views": True,
        "gated_reports_not_generated": [row["report_id"] for row in GATED_REPORTS],
        "unsupported_calculated_lens_reports_gated": [
            "lens_based_performance_attribution_energy_security"
        ],
        "advisor_ui_wiring": "not_changed",
        "generated_report_wiring": "not_changed",
    }


def _view_summary(
    view_files: list[str],
    mockup_files: list[str],
    views: dict[str, dict[str, Any]],
    gated_index: dict[str, Any],
) -> dict[str, Any]:
    first = next(iter(views.values()))
    return {
        "schema_version": VIEW_SUMMARY_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "source_calculated_attribution_engine_id": first[
            "source_calculated_attribution_engine_id"
        ],
        "calculated_outputs_source_of_truth": True,
        "report_view_count": len(views),
        "markdown_mockup_count": len(MOCKUP_FILENAME_BY_REPORT_ID),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "view_files": view_files,
        "mockup_files": mockup_files,
        "mockups_generated_from_views": True,
        "gated_reports_not_generated": [
            row["report_id"] for row in gated_index["gated_or_deferred_reports"]
        ],
        "unsupported_calculated_lens_reports_gated": [
            "lens_based_performance_attribution_energy_security"
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
        "source_calculated_attribution_engine_id": "synthetic_attribution_engine_v1",
        "purpose": "Product/readiness index for attribution reports deliberately not generated.",
        "gated_or_deferred_reports": list(GATED_REPORTS),
    }


def _bridge_row(label: str, value: float, interpretation: str) -> dict[str, Any]:
    return {
        "Effect Driver": label,
        "Effect": _format_signed_percent(value),
        "Interpretation": interpretation,
        "numeric_value": value,
        "row_type": "calculated_effect",
    }


def _theme_detail_visible_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "Theme Bucket": row["bucket_display_name"],
        POLICY_WEIGHT_LABEL: _format_percent(row["policy_or_equal_weight"]),
        ACTUAL_WEIGHT_LABEL: _format_percent(row["actual_portfolio_weight"]),
        "Portfolio Return": _format_percent(row["actual_portfolio_theme_return"]),
        "Theme Benchmark Return": _format_percent(row["theme_benchmark_return"]),
        "Active Return": _format_signed_percent(_theme_active_return(row)),
        "Theme Choice Effect": _format_signed_percent(
            row["theme_benchmark_selection_effect"]
        ),
        "Theme Weight Effect": _format_signed_percent(
            row["theme_benchmark_sizing_effect"]
        ),
        "Asset Choice Effect": _format_signed_percent(row["asset_selection_effect"]),
        "Asset Weight Effect": _format_signed_percent(row["asset_sizing_effect"]),
        "Residual / Reconciler": _format_signed_percent(row["residual_unexplained"]),
        "Total Effect": _format_signed_percent(row["total_effect"]),
    }


def _theme_active_return(row: dict[str, Any]) -> float:
    return _round_return(
        row["actual_portfolio_theme_return"] - row["theme_benchmark_return"]
    )


def _largest_manager_driver(manager: dict[str, Any]) -> str:
    return (
        f"{_visible_effect_driver_label(manager['largest_driver']['label'])} "
        f"({_format_signed_percent(manager['largest_driver']['value'])})"
    )


def _visible_effect_driver_label(label: str) -> str:
    return {
        "Theme benchmark selection": "Theme Choice Effect",
        "Theme benchmark sizing": "Theme Weight Effect",
        "Asset selection": "Asset Choice Effect",
        "Asset sizing": "Asset Weight Effect",
    }.get(label, label)


def _manager_other_measured_effects(manager: dict[str, Any]) -> float:
    measured_fields = (
        "theme_benchmark_selection_effect",
        "theme_benchmark_sizing_effect",
        "asset_selection_effect",
        "asset_sizing_effect",
    )
    measured_total = _round_return(sum(float(manager[field]) for field in measured_fields))
    if manager["largest_driver"]["label"] == "Residual / unexplained":
        return measured_total
    return _round_return(measured_total - float(manager["largest_driver"]["value"]))


def _manager_driver_tie_out(manager: dict[str, Any]) -> bool:
    largest_value = float(manager["largest_driver"]["value"])
    other_measured = _manager_other_measured_effects(manager)
    residual = float(manager["residual_unexplained"])
    if manager["largest_driver"]["label"] == "Residual / unexplained":
        total = other_measured + residual
    else:
        total = largest_value + other_measured + residual
    return abs(_round_return(total) - manager["relative_return"]) <= 0.000001


def _residual_policy_text() -> str:
    return (
        "Residual / unexplained is the calculated reconciler after visible attribution effects. "
        "Residual / unexplained may include unmeasured timing, data, flow, rounding, or reconciliation effects."
    )


def _manager_residual_policy_text() -> str:
    return (
        "Residual / unexplained is the manager-level reconciler after calculated manager effects. "
        "Residual / unexplained may include unmeasured timing, data, flow, rounding, or reconciliation effects."
    )


def _budget_for_report(report_id: str) -> dict[str, Any]:
    budget = dict(DEFAULT_INFORMATION_BUDGET)
    if report_id == "integrated_performance_attribution_detail":
        budget["max_visible_table_rows"] = 7
        budget["exception_reason"] = "Calculated detail shows every AI Adoption theme bucket."
    if report_id == "manager_attribution_summary":
        budget["max_visible_table_rows"] = 6
        budget["exception_reason"] = "Manager Attribution Summary may show all six current managers."
    if report_id.startswith("lens_based_performance_attribution_"):
        budget["max_visible_table_rows"] = 7
        budget["exception_reason"] = "Lens-Based Performance Attribution shows every calculated theme bucket."
    return budget


def _budget_actuals(
    *,
    report_id: str,
    visible: dict[str, Any],
    rendering_mode: str,
) -> dict[str, Any]:
    table = visible.get("compact_table") or visible.get("contribution_bridge")
    advisor_note = visible.get("advisor_note")
    budget = _budget_for_report(report_id)
    return {
        **budget,
        "actual_headline_sentences": _sentence_count(visible["headline_sentence"]),
        "actual_headline_metrics": len(visible["headline_metrics"]),
        "actual_visible_table_rows": len(table["rows"]) if table else 0,
        "actual_caveats": len(visible.get("caveats") or []),
        "actual_advisor_notes": 1 if advisor_note else 0,
        "rendering_mode": rendering_mode,
    }


def _validate_report_ids(inputs: dict[str, dict[str, Any]]) -> None:
    missing = set(BUILD_NOW_REPORT_IDS) - set(inputs)
    unexpected = set(inputs) - set(BUILD_NOW_REPORT_IDS)
    if missing or unexpected:
        raise ValueError(
            f"Unexpected attribution report id set. missing={sorted(missing)} unexpected={sorted(unexpected)}"
        )


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

    visible_text = _visible_text(view).lower()
    for term in FORBIDDEN_VISIBLE_TERMS + FORBIDDEN_PLACEHOLDER_TERMS:
        if term in visible_text:
            raise ValueError(f"{view['report_element_id']} leaks forbidden visible term: {term}")
    for pattern in RAW_ID_PATTERNS:
        if re.search(pattern, visible_text):
            raise ValueError(f"{view['report_element_id']} leaks raw id pattern: {pattern}")


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
        f"{metric['label']} {metric['formatted_value']}" for metric in view["headline_metrics"]
    )
    for table_key in ("contribution_bridge", "compact_table"):
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


def _metric(label: str, value: Any, formatted_value: str) -> dict[str, Any]:
    return {
        "label": label,
        "value": value,
        "formatted_value": formatted_value,
    }


def _format_percent(value: Any) -> str:
    return f"{float(value) * 100:.2f}%"


def _format_signed_percent(value: Any) -> str:
    number = float(value)
    sign = "+" if number >= 0 else "-"
    return f"{sign}{abs(number) * 100:.2f}%"


def _sentence_count(value: str) -> int:
    normalized = value.replace("?", ".").replace("!", ".")
    matches = re.findall(r"[.!?](?:\s|$)", normalized)
    return max(1, len(matches)) if normalized.strip() else 0


def _source_paths(prerequisite_root: Path, calculated_root: Path) -> dict[str, Any]:
    return {
        "prerequisite": {
            "manifest": _as_posix(
                prerequisite_root / "synthetic_attribution_prerequisite_pack_manifest.json"
            ),
            "benchmark_catalog": _as_posix(
                prerequisite_root / "portfolio_benchmark_catalog.json"
            ),
            "proxy_map": _as_posix(
                prerequisite_root / "lens_bucket_benchmark_proxy_map.json"
            ),
        },
        "calculated": {
            key: _as_posix(calculated_root / filename)
            for key, filename in CALCULATED_ARTIFACT_FILES.items()
        },
    }


def _remove_unsupported_calculated_outputs(
    input_path: Path,
    view_path: Path,
    mockup_path: Path,
) -> None:
    for filename in UNSUPPORTED_CALCULATED_OUTPUTS["input"]:
        _unlink_if_exists(input_path / filename)
    for filename in UNSUPPORTED_CALCULATED_OUTPUTS["view"]:
        _unlink_if_exists(view_path / filename)
    for filename in UNSUPPORTED_CALCULATED_OUTPUTS["mockup"]:
        _unlink_if_exists(mockup_path / filename)


def _unlink_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def _round_return(value: Any) -> float:
    return round(float(value), 6)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate synthetic attribution report fixtures and mockups."
    )
    parser.add_argument("--prerequisite-dir", default=str(DEFAULT_PREREQUISITE_DIR))
    parser.add_argument("--calculated-dir", default=str(DEFAULT_CALCULATED_DIR))
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument("--mockup-dir", default=str(DEFAULT_MOCKUP_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_attribution_report_views(
        prerequisite_dir=args.prerequisite_dir,
        calculated_dir=args.calculated_dir,
        input_dir=args.input_dir,
        view_dir=args.view_dir,
        mockup_dir=args.mockup_dir,
    )

    print(f"Attribution report inputs: {summary['report_input_count']} -> {summary['input_dir']}")
    print(f"Attribution report views: {summary['report_view_count']} -> {summary['view_dir']}")
    print(
        f"Attribution Markdown mockups: {summary['markdown_mockup_count']} -> {summary['mockup_dir']}"
    )
    print(
        "Calculated source: "
        + summary["source_calculated_attribution_engine_id"]
    )
    print("Generated report ids: " + ", ".join(summary["report_ids"]))
    print("Gated reports not generated: " + ", ".join(summary["gated_reports_not_generated"]))
    print("Output paths: " + summary["input_dir"] + "; " + summary["view_dir"] + "; " + summary["mockup_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
