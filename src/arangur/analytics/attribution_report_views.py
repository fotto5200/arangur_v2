from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-07T00:00:00Z"

INPUT_SCHEMA_VERSION = "attribution_report_input.v1"
INPUT_SUMMARY_SCHEMA_VERSION = "attribution_report_input_summary.v1"
VIEW_SCHEMA_VERSION = "attribution_report_view.v1"
VIEW_SUMMARY_SCHEMA_VERSION = "attribution_report_view_summary.v1"
GATED_INDEX_SCHEMA_VERSION = "attribution_report_gated_deferred_index.v1"
GENERATOR_VERSION = "attribution_report_views.v1"

DEFAULT_PREREQUISITE_DIR = Path(
    "data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1"
)
DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs/attribution_v1")
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/attribution_v1")
DEFAULT_MOCKUP_DIR = Path("docs/product/report_mockups/attribution_v1")

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
    {
        "report_id": "lens_based_performance_attribution_energy_security",
        "input_filename": "lens_based_performance_attribution_energy_security_input.json",
        "view_filename": "lens_based_performance_attribution_energy_security_view.json",
        "mockup_filename": "lens_based_performance_attribution_energy_security_mockup_v1.md",
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

EFFECT_LABELS = {
    "strategy_lens_bucket_selection_effect": "Theme benchmark selection",
    "strategy_lens_bucket_sizing_effect": "Theme benchmark sizing",
    "asset_selection_effect": "Asset selection",
    "asset_sizing_effect": "Asset sizing",
    "residual_unexplained": "Residual / unexplained",
}

EFFECT_INTERPRETATIONS = {
    "strategy_lens_bucket_selection_effect": "Theme benchmark choices helped relative return.",
    "strategy_lens_bucket_sizing_effect": "Theme benchmark sizing helped relative return.",
    "asset_selection_effect": "Selected assets outperformed their reference mix.",
    "asset_sizing_effect": "Sizing within selected assets helped modestly.",
    "residual_unexplained": (
        "Remaining reconciler; may include unmeasured timing, data, flow, or reconciliation effects."
    ),
}

LENS_REPORTS = {
    "ai_adoption": {
        "report_id": "lens_based_performance_attribution_ai_adoption",
        "display_title": "Lens-Based Performance Attribution - AI Adoption",
        "lens_display_name": "AI Adoption",
        "exact_report_question": (
            "Which AI Adoption theme buckets explain relative performance versus their theme benchmarks?"
        ),
        "denominator_category_system": "AI Adoption theme buckets versus synthetic theme benchmarks",
    },
    "energy_security": {
        "report_id": "lens_based_performance_attribution_energy_security",
        "display_title": "Lens-Based Performance Attribution - Energy Security",
        "lens_display_name": "Energy Security",
        "exact_report_question": (
            "Which Energy Security theme buckets explain relative performance versus their theme benchmarks?"
        ),
        "denominator_category_system": "Energy Security theme buckets versus synthetic theme benchmarks",
    },
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
    "proxy return",
    "bucket return",
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
) -> dict[str, Any]:
    root = Path(prerequisite_dir)
    return {
        "source_paths": _source_paths(root),
        "manifest": _load_json(root / "synthetic_attribution_prerequisite_pack_manifest.json"),
        "benchmark_catalog": _load_json(root / "portfolio_benchmark_catalog.json"),
        "proxy_map": _load_json(root / "lens_bucket_benchmark_proxy_map.json"),
        "period_returns": _load_json(root / "synthetic_period_returns.json"),
        "weights_flows": _load_json(root / "synthetic_attribution_weights_flows.json"),
        "decomposition": _load_json(root / "integrated_attribution_decomposition_inputs.json"),
        "manager_prerequisites": _load_json(root / "manager_attribution_prerequisites.json"),
        "readiness": _load_json(root / "attribution_readiness_summary.json"),
    }


def build_attribution_report_inputs(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    whole = _whole_portfolio_mode(context)
    managers = list(context["manager_prerequisites"]["managers"])
    benchmark = context["benchmark_catalog"]["benchmarks"][0]

    inputs = {
        "integrated_performance_attribution_summary": _integrated_summary_input(
            context, whole, benchmark
        ),
        "integrated_performance_attribution_detail": _integrated_detail_input(
            context, whole, benchmark
        ),
        "manager_attribution_summary": _manager_summary_input(context, managers),
    }
    for lens_id in ("ai_adoption", "energy_security"):
        report_id = LENS_REPORTS[lens_id]["report_id"]
        inputs[report_id] = _lens_attribution_input(context, lens_id)

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

    context = load_source_context(prerequisite_dir=prerequisite_dir)
    inputs = build_attribution_report_inputs(context)
    views = build_attribution_report_views(inputs)

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
            "These product-review mockups are generated from attribution v1 view fixtures. "
            "They remain local synthetic-demo only and are not wired into Advisor Preview, "
            "Populate, Present, generated reports, Docker, deployment, live data, or dependencies."
        ),
        (
            "Visible attribution wording uses global benchmark, theme benchmark, asset selection/sizing, "
            "and residual / unexplained labels; proxy benchmarks appear only as synthetic-demo caveats."
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
    whole: dict[str, Any],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        _bridge_row(effect_key, value, include_numeric=True)
        for effect_key, value in _ordered_effects(whole["effects"])
    ]
    largest = max(rows, key=lambda row: abs(float(row["numeric_value"])))
    visible = {
        "headline_sentence": (
            f"Portfolio return exceeded the global benchmark by "
            f"{_format_signed_percent(whole['active_return'])}, with "
            f"{largest['Contribution'].lower()} the largest visible driver."
        ),
        "headline_metrics": [
            _metric("Portfolio return", whole["actual_return"], _format_percent(whole["actual_return"])),
            _metric("Global benchmark return", whole["benchmark_return"], _format_percent(whole["benchmark_return"])),
            _metric("Relative return", whole["active_return"], _format_signed_percent(whole["active_return"])),
        ],
        "contribution_bridge": _table(
            "Contribution Summary",
            ["Contribution", "Effect", "Interpretation"],
            rows,
        ),
        "caveats": [
            "Synthetic local-demo returns and benchmark inputs only.",
            "Timing attribution is not shown separately because clean trade/holding history, flow treatment, and an approved timing method are not present.",
        ],
        "advisor_note": (
            "Use this as a compact product-review shape; real/client attribution remains gated "
            "until production returns, benchmark maps, flows, and methodology are approved."
        ),
    }
    return _report_input(
        report_element_id="integrated_performance_attribution_summary",
        display_title="Integrated Performance Attribution Summary",
        report_family="Integrated Performance Attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "Did the portfolio add value versus the global benchmark, and what were the largest visible decision effects?"
        ),
        audience_tier="Client briefing and advisor review",
        summary_detail_status="Summary",
        representation_level="Whole portfolio versus benchmark",
        denominator_category_system="Benchmark-relative contribution bridge",
        rendering_mode="summary_first",
        context=context,
        visible_content=visible,
        timing_status="unavailable",
        residual_policy=(
            "Residual / unexplained is the remaining reconciler and may include unmeasured timing, data, flow, or reconciliation effects."
        ),
        benchmark_or_proxy_basis=benchmark["display_name"],
        table_validation={
            "bridge_row_count": len(rows),
            "effects_sum": round(sum(float(row["numeric_value"]) for row in rows), 6),
            "active_return": whole["active_return"],
            "ties_to_active_return": abs(
                sum(float(row["numeric_value"]) for row in rows) - whole["active_return"]
            )
            <= 0.000001,
            "timing_contribution_included": False,
            "residual_label": "Residual / unexplained",
        },
    )


def _integrated_detail_input(
    context: dict[str, Any],
    whole: dict[str, Any],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    detail = whole["theme_benchmark_detail"]
    rows = []
    for row in detail["rows"]:
        rows.append(
            {
                "Theme Bucket": row["bucket_display_name"],
                "Weight": _format_percent(row["weight"]),
                "Portfolio Return": _format_percent(row["portfolio_return"]),
                "Theme Benchmark Return": _format_percent(row["theme_benchmark_return"]),
                "Theme Benchmark Selection": _format_component(row["theme_benchmark_selection_effect"]),
                "Theme Benchmark Sizing": _format_component(row["theme_benchmark_sizing_effect"]),
                "Asset Selection": _format_component(row["asset_selection_effect"]),
                "Asset Sizing": _format_component(row["asset_sizing_effect"]),
                "Total Effect": _format_signed_percent(row["total_effect"]),
                "numeric_total_effect": row["total_effect"],
            }
        )
    rows.append(
        {
            "Theme Bucket": "Residual / unexplained",
            "Weight": "n/a",
            "Portfolio Return": "n/a",
            "Theme Benchmark Return": "n/a",
            "Theme Benchmark Selection": "Not separately measured",
            "Theme Benchmark Sizing": "Not separately measured",
            "Asset Selection": "Not separately measured",
            "Asset Sizing": "Not separately measured",
            "Total Effect": _format_signed_percent(detail["residual_unexplained"]),
            "numeric_total_effect": detail["residual_unexplained"],
        }
    )
    visible_rows = [
        {
            "Theme Bucket": row["Theme Bucket"],
            "Weight": row["Weight"],
            "Portfolio Return": row["Portfolio Return"],
            "Theme Benchmark Return": row["Theme Benchmark Return"],
            "Theme Benchmark Selection": row["Theme Benchmark Selection"],
            "Theme Benchmark Sizing": row["Theme Benchmark Sizing"],
            "Asset Selection": row["Asset Selection"],
            "Asset Sizing": row["Asset Sizing"],
            "Total Effect": row["Total Effect"],
        }
        for row in rows
    ]
    theme_total = detail["theme_bucket_total_effect"]
    residual = detail["residual_unexplained"]
    visible = {
        "headline_sentence": (
            "Theme benchmark rows show the measured bucket-level effects, with residual / unexplained completing the global benchmark-to-portfolio tie-out."
        ),
        "headline_metrics": [
            _metric("Global benchmark return", whole["benchmark_return"], _format_percent(whole["benchmark_return"])),
            _metric("Theme row total", theme_total, _format_signed_percent(theme_total)),
            _metric("Actual portfolio return", whole["actual_return"], _format_percent(whole["actual_return"])),
        ],
        "compact_table": _table(
            "Theme Benchmark Detail",
            [
                "Theme Bucket",
                "Weight",
                "Portfolio Return",
                "Theme Benchmark Return",
                "Theme Benchmark Selection",
                "Theme Benchmark Sizing",
                "Asset Selection",
                "Asset Sizing",
                "Total Effect",
            ],
            visible_rows,
        ),
        "caveats": [
            "Synthetic local-demo returns and theme benchmarks only; some theme benchmarks are proxy benchmarks for demo purposes, not production recommendations.",
            "Timing attribution is not shown separately because clean trade/holding history, flow treatment, and an approved timing method are not present.",
        ],
        "advisor_note": (
            "Bucket-level selection and sizing components are not separately measured in this v1 synthetic input; use total effect and the residual tie-out for review."
        ),
    }
    return _report_input(
        report_element_id="integrated_performance_attribution_detail",
        display_title="Integrated Performance Attribution Detail",
        report_family="Integrated Performance Attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "How do theme benchmarks / lens buckets explain the synthetic benchmark-to-portfolio attribution bridge?"
        ),
        audience_tier="Advisor review",
        summary_detail_status="Detail",
        representation_level="Whole portfolio versus benchmark",
        denominator_category_system="Theme benchmark bucket total effects plus residual tie-out",
        rendering_mode="detail_first",
        context=context,
        visible_content=visible,
        timing_status="unavailable",
        residual_policy=(
            "Residual / unexplained is the remaining reconciler and may include unmeasured timing, data, flow, or reconciliation effects."
        ),
        benchmark_or_proxy_basis=benchmark["display_name"],
        table_validation={
            "bridge_row_count": len(visible_rows),
            "theme_benchmark_lens": detail["lens_display_name"],
            "theme_bucket_row_count": len(detail["rows"]),
            "theme_bucket_total_effect": theme_total,
            "residual_unexplained": residual,
            "effect_total": round(theme_total + residual, 6),
            "actual_return": whole["actual_return"],
            "global_benchmark_return": whole["benchmark_return"],
            "recomputed_actual_return": round(whole["benchmark_return"] + theme_total + residual, 6),
            "ties_to_actual_return": abs(
                whole["actual_return"] - round(whole["benchmark_return"] + theme_total + residual, 6)
            )
            <= 0.000001,
            "component_effects_not_separately_measured": True,
            "timing_contribution_included": False,
            "residual_label": "Residual / unexplained",
        },
    )


def _manager_summary_input(
    context: dict[str, Any],
    managers: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = []
    for manager in sorted(
        managers,
        key=lambda row: abs(float(row["portfolio_active_contribution"])),
        reverse=True,
    ):
        rows.append(
            {
                "Manager": manager["display_name"],
                "Return": _format_percent(manager["manager_return"]),
                "Manager Benchmark Return": _format_percent(manager["benchmark_proxy_return"]),
                "Relative Return": _format_signed_percent(manager["relative_return"]),
                "Largest Driver": _largest_manager_driver(manager),
                "portfolio_active_contribution": manager["portfolio_active_contribution"],
            }
        )
    total_contribution = round(
        sum(float(row["portfolio_active_contribution"]) for row in rows), 6
    )
    visible_rows = [
        {
            "Manager": row["Manager"],
            "Return": row["Return"],
            "Manager Benchmark Return": row["Manager Benchmark Return"],
            "Relative Return": row["Relative Return"],
            "Largest Driver": row["Largest Driver"],
        }
        for row in rows
    ]
    visible = {
        "headline_sentence": (
            "All six current managers have synthetic manager benchmark returns, with contribution direction shown against each benchmark."
        ),
        "headline_metrics": [
            _metric("Managers covered", len(rows), str(len(rows))),
            _metric(
                "Total manager contribution",
                total_contribution,
                _format_signed_percent(total_contribution),
            ),
            _metric("Manager benchmark coverage", len(rows), f"{len(rows)} of {len(managers)}"),
        ],
        "compact_table": _table(
            "Manager Contribution Summary",
            [
                "Manager",
                "Return",
                "Manager Benchmark Return",
                "Relative Return",
                "Largest Driver",
            ],
            visible_rows,
        ),
        "caveats": [
            "Synthetic manager benchmarks may use proxy benchmarks for demo purposes; they are not production recommendations.",
            "Timing attribution is not shown separately because clean trade/holding history, flow treatment, and an approved timing method are not present.",
        ],
        "advisor_note": (
            "This summary is not a replacement for future manager-level integrated attribution summary/detail variants."
        ),
    }
    return _report_input(
        report_element_id="manager_attribution_summary",
        display_title="Manager Attribution Summary",
        report_family="Manager Attribution",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "Which managers added or lost value versus their manager benchmarks, and what kind of contribution drove it?"
        ),
        audience_tier="Advisor review",
        summary_detail_status="Summary",
        representation_level="Manager versus manager-specific benchmark",
        denominator_category_system="Manager-specific benchmark relative returns",
        rendering_mode="table_first",
        context=context,
        visible_content=visible,
        timing_status="unavailable",
        residual_policy=(
            "Residual / unexplained is the manager-level reconciler and may include unmeasured timing, data, flow, or reconciliation effects."
        ),
        benchmark_or_proxy_basis="Manager-specific synthetic benchmarks",
        table_validation={
            "current_manager_count": len(managers),
            "manager_rows_shown": len(visible_rows),
            "all_current_managers_covered": True,
            "coverage_justification": (
                "All six current managers are shown because the product budget allows six rows."
            ),
            "timing_column_removed": True,
            "manager_benchmark_coverage": f"{len(visible_rows)} of {len(managers)}",
            "residual_labeled_separately": True,
        },
    )


def _lens_attribution_input(context: dict[str, Any], lens_id: str) -> dict[str, Any]:
    spec = LENS_REPORTS[lens_id]
    returns_by_bucket = {
        row["bucket_id"]: row
        for row in context["period_returns"]["lens_bucket_returns"]
        if row["lens_id"] == lens_id
    }
    weights_by_bucket = {
        row["bucket_id"]: row
        for row in context["weights_flows"]["lens_bucket_weights"]
        if row["lens_id"] == lens_id
    }

    rows = []
    for bucket_id, return_row in returns_by_bucket.items():
        weight = float(weights_by_bucket[bucket_id]["weight"])
        relative_return = float(return_row["relative_return"])
        relative_contribution = round(weight * relative_return, 6)
        rows.append(
            {
                "Theme Bucket": return_row["bucket_display_name"],
                "Weight": _format_percent(weight),
                "Portfolio Return": _format_percent(return_row["period_return"]),
                "Theme Benchmark Return": _format_percent(return_row["proxy_period_return"]),
                "Relative Contribution": _format_signed_percent(relative_contribution),
                "bucket_id": bucket_id,
                "relative_contribution": relative_contribution,
            }
        )
    rows.sort(key=lambda row: abs(float(row["relative_contribution"])), reverse=True)
    visible_rows = [
        {
            "Theme Bucket": row["Theme Bucket"],
            "Weight": row["Weight"],
            "Portfolio Return": row["Portfolio Return"],
            "Theme Benchmark Return": row["Theme Benchmark Return"],
            "Relative Contribution": row["Relative Contribution"],
        }
        for row in rows
    ]
    total = round(sum(float(row["relative_contribution"]) for row in rows), 6)
    top_positive = max(rows, key=lambda row: float(row["relative_contribution"]))
    top_negative = min(rows, key=lambda row: float(row["relative_contribution"]))
    visible = {
        "headline_sentence": (
            f"Under the {spec['lens_display_name']} lens, {top_positive['Theme Bucket']} "
            "is the largest positive relative contributor versus its theme benchmark."
        ),
        "headline_metrics": [
            _metric("Net relative contribution", total, _format_signed_percent(total)),
            _metric(
                "Largest positive theme bucket",
                top_positive["relative_contribution"],
                f"{top_positive['Theme Bucket']} ({_format_signed_percent(top_positive['relative_contribution'])})",
            ),
            _metric(
                "Largest negative theme bucket",
                top_negative["relative_contribution"],
                f"{top_negative['Theme Bucket']} ({_format_signed_percent(top_negative['relative_contribution'])})",
            ),
        ],
        "compact_table": _table(
            f"{spec['lens_display_name']} Theme Bucket Performance",
            [
                "Theme Bucket",
                "Weight",
                "Portfolio Return",
                "Theme Benchmark Return",
                "Relative Contribution",
            ],
            visible_rows,
        ),
        "caveats": [
            "Some synthetic theme benchmarks are proxy benchmarks for demo purposes; they are not production recommendations.",
            "Bucket weights use the complete synthetic lens assignment pack, including neutral and review buckets.",
        ],
        "advisor_note": (
            "Read this as a one-lens theme performance view; do not compare these rows to "
            "scenario or proposed-allocation results."
        ),
    }
    return _report_input(
        report_element_id=spec["report_id"],
        display_title=spec["display_title"],
        report_family="Lens-Based Performance Attribution",
        master_question_family="Performance / Plan",
        exact_report_question=spec["exact_report_question"],
        audience_tier="Advisor review",
        summary_detail_status="Summary",
        representation_level=f"{spec['lens_display_name']} theme bucket",
        denominator_category_system=spec["denominator_category_system"],
        rendering_mode="table_first",
        context=context,
        visible_content=visible,
        timing_status="unavailable",
        residual_policy=(
            "No residual row is shown in the theme-bucket summary; timing attribution is not separately measured."
        ),
        benchmark_or_proxy_basis=f"Synthetic {spec['lens_display_name']} theme benchmark set",
        table_validation={
            "lens_id": lens_id,
            "lens_bucket_count": len(rows),
            "all_lens_buckets_included": True,
            "contains_neutral_bucket": any("Neutral" in row["Theme Bucket"] for row in rows),
            "contains_review_bucket": any("Review" in row["Theme Bucket"] for row in rows),
            "relative_contribution_total": total,
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
    table_validation: dict[str, Any],
) -> dict[str, Any]:
    period = context["manifest"]
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
        "period_start": period["period_start"],
        "period_end": period["period_end"],
        "visible_content": visible_content,
        "timing_status": timing_status,
        "residual_policy": residual_policy,
        "benchmark_or_proxy_basis": benchmark_or_proxy_basis,
        "internal_source_refs": _internal_refs_for_report(report_element_id, context),
        "source_prerequisite_pack_refs": [context["manifest"]["pack_id"]],
        "table_validation": table_validation,
        "information_budget": _budget_for_report(report_element_id),
        "gated_or_deferred": False,
        "not_wired_into_advisor_ui": True,
        "not_wired_into_generated_reports": True,
    }


def _input_summary(input_files: list[str], inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": INPUT_SUMMARY_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "report_input_count": len(inputs),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "input_files": input_files,
        "mockups_generated_from_views": True,
        "gated_reports_not_generated": [row["report_id"] for row in GATED_REPORTS],
        "advisor_ui_wiring": "not_changed",
        "generated_report_wiring": "not_changed",
    }


def _view_summary(
    view_files: list[str],
    mockup_files: list[str],
    views: dict[str, dict[str, Any]],
    gated_index: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": VIEW_SUMMARY_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
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
        "purpose": "Product/readiness index for attribution reports deliberately not generated.",
        "gated_or_deferred_reports": list(GATED_REPORTS),
    }


def _whole_portfolio_mode(context: dict[str, Any]) -> dict[str, Any]:
    return next(
        row
        for row in context["decomposition"]["supported_modes"]
        if row["mode"] == "whole_portfolio"
    )


def _ordered_effects(effects: dict[str, float]) -> list[tuple[str, float]]:
    return [
        (effect_key, float(effects[effect_key]))
        for effect_key in (
            "strategy_lens_bucket_selection_effect",
            "strategy_lens_bucket_sizing_effect",
            "asset_selection_effect",
            "asset_sizing_effect",
            "residual_unexplained",
        )
    ]


def _bridge_row(effect_key: str, value: float, *, include_numeric: bool = False) -> dict[str, Any]:
    row = {
        "Contribution": EFFECT_LABELS[effect_key],
        "Effect": _format_signed_percent(value),
        "Interpretation": EFFECT_INTERPRETATIONS[effect_key],
    }
    if include_numeric:
        row["effect_key"] = effect_key
        row["numeric_value"] = value
        row["row_type"] = "effect"
    return row


def _largest_manager_driver(manager: dict[str, Any]) -> str:
    candidates = {
        "Theme benchmark selection": manager["strategy_selection_contribution"],
        "Theme benchmark sizing": manager["strategy_sizing_contribution"],
        "Asset selection": manager["asset_selection_contribution"],
        "Asset sizing": manager["asset_sizing_contribution"],
        "Residual / unexplained": manager["residual_unexplained"],
    }
    label, value = max(candidates.items(), key=lambda item: abs(float(item[1])))
    return f"{label} ({_format_signed_percent(value)})"


def _budget_for_report(report_id: str) -> dict[str, Any]:
    budget = dict(DEFAULT_INFORMATION_BUDGET)
    if report_id == "integrated_performance_attribution_detail":
        budget["max_visible_table_rows"] = 8
    if report_id == "manager_attribution_summary":
        budget["max_visible_table_rows"] = 6
        budget["exception_reason"] = "Manager Attribution Summary may show all six current managers."
    if report_id.startswith("lens_based_performance_attribution_"):
        budget["max_visible_table_rows"] = 7
        budget["exception_reason"] = "Lens-Based Performance Attribution shows every theme bucket in the selected lens."
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


def _format_component(value: Any) -> str:
    if value is None:
        return "Not separately measured"
    return _format_signed_percent(value)


def _sentence_count(value: str) -> int:
    normalized = value.replace("?", ".").replace("!", ".")
    matches = re.findall(r"[.!?](?:\s|$)", normalized)
    return max(1, len(matches)) if normalized.strip() else 0


def _internal_refs_for_report(report_id: str, context: dict[str, Any]) -> list[str]:
    common = [
        context["source_paths"]["manifest"],
        context["source_paths"]["period_returns"],
        context["source_paths"]["weights_flows"],
    ]
    if report_id.startswith("integrated_performance_attribution_"):
        return [
            *common,
            context["source_paths"]["benchmark_catalog"],
            context["source_paths"]["decomposition"],
        ]
    if report_id == "manager_attribution_summary":
        return [
            *common,
            context["source_paths"]["manager_prerequisites"],
        ]
    return [
        *common,
        context["source_paths"]["proxy_map"],
    ]


def _source_paths(root: Path) -> dict[str, str]:
    return {
        "manifest": _as_posix(root / "synthetic_attribution_prerequisite_pack_manifest.json"),
        "benchmark_catalog": _as_posix(root / "portfolio_benchmark_catalog.json"),
        "proxy_map": _as_posix(root / "lens_bucket_benchmark_proxy_map.json"),
        "period_returns": _as_posix(root / "synthetic_period_returns.json"),
        "weights_flows": _as_posix(root / "synthetic_attribution_weights_flows.json"),
        "decomposition": _as_posix(root / "integrated_attribution_decomposition_inputs.json"),
        "manager_prerequisites": _as_posix(root / "manager_attribution_prerequisites.json"),
        "readiness": _as_posix(root / "attribution_readiness_summary.json"),
    }


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
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument("--mockup-dir", default=str(DEFAULT_MOCKUP_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_attribution_report_views(
        prerequisite_dir=args.prerequisite_dir,
        input_dir=args.input_dir,
        view_dir=args.view_dir,
        mockup_dir=args.mockup_dir,
    )

    print(f"Attribution report inputs: {summary['report_input_count']} -> {summary['input_dir']}")
    print(f"Attribution report views: {summary['report_view_count']} -> {summary['view_dir']}")
    print(
        f"Attribution Markdown mockups: {summary['markdown_mockup_count']} -> {summary['mockup_dir']}"
    )
    print("Generated report ids: " + ", ".join(summary["report_ids"]))
    print("Gated reports not generated: " + ", ".join(summary["gated_reports_not_generated"]))
    print("Output paths: " + summary["input_dir"] + "; " + summary["view_dir"] + "; " + summary["mockup_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
