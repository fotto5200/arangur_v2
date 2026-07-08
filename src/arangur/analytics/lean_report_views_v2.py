from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-07T00:00:00Z"

INPUT_SCHEMA_VERSION = "revaluation_report_input.v2"
INPUT_SUMMARY_SCHEMA_VERSION = "revaluation_report_input_summary.v2"
VIEW_SCHEMA_VERSION = "revaluation_report_view.v2"
VIEW_SUMMARY_SCHEMA_VERSION = "revaluation_report_view_summary.v2"
GATED_INDEX_SCHEMA_VERSION = "revaluation_report_gated_deferred_index.v2"
GENERATOR_VERSION = "lean_report_views_v2.v1"

DEFAULT_REVALUATION_DIR = Path("data/simulation/revaluation")
DEFAULT_ATTRIBUTION_DIR = DEFAULT_REVALUATION_DIR / "attribution"
DEFAULT_PREREQUISITE_DIR = Path(
    "data/simulation/report_prerequisites/synthetic_report_prerequisite_pack_v1"
)
DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs/revaluation_v2")
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/revaluation_v2")
DEFAULT_MOCKUP_DIR = Path("docs/product/report_mockups/revaluation_v2")

SCENARIO_IDS = ("ai_chip_selloff", "rate_shock")
SCENARIO_LABELS = {
    "ai_chip_selloff": "AI / Chip Selloff",
    "rate_shock": "Rate Shock",
}

REPORT_SPECS: tuple[dict[str, str], ...] = (
    {
        "report_id": "portfolio_representation_status",
        "mockup_filename": "portfolio_representation_status_mockup_v2.md",
    },
    {
        "report_id": "aggregated_asset_allocation",
        "mockup_filename": "aggregated_asset_allocation_mockup_v2.md",
    },
    {
        "report_id": "allocation_by_manager",
        "mockup_filename": "allocation_by_manager_mockup_v2.md",
    },
    {
        "report_id": "coverage_confidence_warning",
        "mockup_filename": "coverage_confidence_warning_mockup_v2.md",
    },
    {
        "report_id": "concentration_by_asset_type",
        "mockup_filename": "concentration_by_asset_type_mockup_v2.md",
    },
    {
        "report_id": "concentration_by_manager_sleeve",
        "mockup_filename": "concentration_by_manager_sleeve_mockup_v2.md",
    },
    {
        "report_id": "current_portfolio_scenario_downside",
        "mockup_filename": "current_portfolio_scenario_downside_mockup_v2.md",
    },
    {
        "report_id": "manager_role_summary",
        "mockup_filename": "manager_role_summary_mockup_v2.md",
    },
    {
        "report_id": "cash_flow_delivered",
        "mockup_filename": "cash_flow_delivered_mockup_v2.md",
    },
    {
        "report_id": "cash_flow_support_outlook",
        "mockup_filename": "cash_flow_support_outlook_mockup_v2.md",
    },
    {
        "report_id": "full_lens_exposure_ai_adoption",
        "mockup_filename": "full_lens_exposure_ai_adoption_mockup_v2.md",
    },
    {
        "report_id": "full_lens_exposure_energy_security",
        "mockup_filename": "full_lens_exposure_energy_security_mockup_v2.md",
    },
    {
        "report_id": "manager_by_lens_exposure_ai_adoption",
        "mockup_filename": "manager_by_lens_exposure_ai_adoption_mockup_v2.md",
    },
    {
        "report_id": "manager_by_lens_exposure_energy_security",
        "mockup_filename": "manager_by_lens_exposure_energy_security_mockup_v2.md",
    },
)
BUILD_NOW_REPORT_IDS = tuple(spec["report_id"] for spec in REPORT_SPECS)
MOCKUP_FILENAME_BY_REPORT_ID = {
    spec["report_id"]: spec["mockup_filename"] for spec in REPORT_SPECS
}

GATED_REPORTS = (
    {
        "report_id": "scenario_versus_benchmark",
        "display_title": "Scenario Versus Benchmark",
        "status": "Design soon / prerequisite soon",
        "reason": "Needs approved benchmark maps and benchmark scenario values before any comparison is generated.",
    },
    {
        "report_id": "integrated_performance_attribution_summary",
        "display_title": "Integrated Performance Attribution Summary",
        "status": "Design soon / prerequisite soon",
        "reason": "Important report family; needs historical returns, benchmark returns, weights, flows, and an approved attribution method before mockups are generated.",
    },
    {
        "report_id": "integrated_performance_attribution_detail",
        "display_title": "Integrated Performance Attribution Detail",
        "status": "Design soon / prerequisite soon",
        "reason": "Important report family; needs summary prerequisites plus detailed holding, trade, and reconciliation policy before mockups are generated.",
    },
    {
        "report_id": "probabilistic_scenario_range",
        "display_title": "Probabilistic Scenario Range",
        "status": "Design soon / prerequisite soon",
        "reason": "Needs approved range analytics and methodology; deterministic stress reports are not probability ranges or forecasts.",
    },
    {
        "report_id": "current_versus_proposed_portfolio",
        "display_title": "Current Versus Proposed Portfolio",
        "status": "Gated",
        "reason": "Needs an explicit proposed allocation workflow and data object.",
    },
    {
        "report_id": "timing_attribution",
        "display_title": "Timing Attribution",
        "status": "Gated on clean methodology",
        "reason": "Needs clean timing methodology plus trade and holding history; residual/noise should not be labeled timing.",
    },
    {
        "report_id": "custom_benchmark_construction",
        "display_title": "Custom Benchmark Construction",
        "status": "Deferred",
        "reason": "Intentionally not part of the v2 mockup set.",
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
    r"\bai_chip_selloff\b",
    r"\brate_shock\b",
)

ASSET_TYPE_LABELS = {
    "cash": "Fixed Income / Cash",
    "commodity": "Other",
    "crypto": "Other",
    "data_center_investment": "Private Markets",
    "etf": "Funds / ETFs",
    "fixed_income": "Fixed Income / Cash",
    "fx_exposure": "Other",
    "money_market": "Fixed Income / Cash",
    "opaque_manager_level": "Other",
    "option_like": "Other",
    "private_credit": "Private Markets",
    "private_equity": "Private Markets",
    "public_equity": "Public Equity",
    "real_estate": "Private Markets",
}

ASSET_TYPE_MEANINGS = {
    "Public Equity": "Largest source of equity-market and growth sensitivity.",
    "Funds / ETFs": "Packaged exposure can reduce transparency versus direct holdings.",
    "Private Markets": "Illiquidity and mark timing can affect interpretation.",
    "Fixed Income / Cash": "Supports liquidity and income but remains rate-sensitive.",
    "Other": "Smaller exposures are grouped so the concentration report stays focused.",
}

COVERAGE_LABELS = {
    "held_at_mark_with_caveat": "Held At Mark",
    "not_valued": "Not Valued",
    "review_required": "Review Required",
    "valued": "Valued",
    "valued_with_approved_policy": "Approved Policy",
    "valued_with_substitute_input": "Substitute Input",
}

COVERAGE_MEANINGS = {
    "valued": "Usable for the current synthetic summary.",
    "valued_with_approved_policy": "Usable with policy caveat.",
    "held_at_mark_with_caveat": "May understate stress exposure.",
    "review_required": "Review before relying on point impact.",
    "not_valued": "Do not use for point impact.",
}

LENS_ASSIGNMENT_FILES = {
    "ai_adoption": "position_lens_assignments_ai_adoption_v1.json",
    "energy_security": "position_lens_assignments_energy_security_v1.json",
}

LENS_FILES = {
    "ai_adoption": "ai_adoption_lens_v1.json",
    "energy_security": "energy_security_lens_v1.json",
}


def load_source_context(
    *,
    revaluation_dir: str | Path = DEFAULT_REVALUATION_DIR,
    prerequisite_dir: str | Path = DEFAULT_PREREQUISITE_DIR,
) -> dict[str, Any]:
    revaluation_path = Path(revaluation_dir)
    attribution_path = revaluation_path / "attribution"
    prerequisite_path = Path(prerequisite_dir)

    return {
        "source_paths": _source_paths(revaluation_path, attribution_path, prerequisite_path),
        "scenario_index": _load_json(revaluation_path / "revaluation_scenario_index.json"),
        "position_catalog": _load_json(revaluation_path / "position_catalog.json"),
        "instrument_catalog": _load_json(revaluation_path / "instrument_catalog.json"),
        "base_valuation": _load_json(revaluation_path / "position_valuation_results_base.json"),
        "portfolio_summaries": {
            scenario_id: _load_json(
                revaluation_path / f"portfolio_revaluation_summary_{scenario_id}.json"
            )
            for scenario_id in SCENARIO_IDS
        },
        "position_comparisons": {
            scenario_id: _load_json(
                revaluation_path / f"position_value_comparison_{scenario_id}.json"
            )
            for scenario_id in SCENARIO_IDS
        },
        "attribution_index": _load_json(attribution_path / "revaluation_attribution_index.json"),
        "cross_scenario": _load_json(attribution_path / "cross_scenario_revaluation_summary.json"),
        "manager_attribution": {
            scenario_id: _load_json(
                attribution_path / f"manager_revaluation_attribution_{scenario_id}.json"
            )
            for scenario_id in SCENARIO_IDS
        },
        "account_attribution": {
            scenario_id: _load_json(
                attribution_path / f"account_revaluation_attribution_{scenario_id}.json"
            )
            for scenario_id in SCENARIO_IDS
        },
        "sleeve_attribution": {
            scenario_id: _load_json(
                attribution_path / f"sleeve_revaluation_attribution_{scenario_id}.json"
            )
            for scenario_id in SCENARIO_IDS
        },
        "coverage_attribution": {
            scenario_id: _load_json(
                attribution_path / f"coverage_revaluation_attribution_{scenario_id}.json"
            )
            for scenario_id in SCENARIO_IDS
        },
        "confidence_attribution": {
            scenario_id: _load_json(
                attribution_path / f"confidence_revaluation_attribution_{scenario_id}.json"
            )
            for scenario_id in SCENARIO_IDS
        },
        "theme_attribution": {
            scenario_id: _load_json(
                attribution_path / f"theme_revaluation_attribution_{scenario_id}.json"
            )
            for scenario_id in SCENARIO_IDS
        },
        "cash_flow_support_inputs": _load_json(prerequisite_path / "cash_flow_support_inputs.json"),
        "cash_flow_need_profile": _load_json(prerequisite_path / "cash_flow_need_profile.json"),
        "cash_flow_history_summary": _load_json(
            prerequisite_path / "cash_flow_history_summary.json"
        ),
        "cash_flow_projection_summary": _load_json(
            prerequisite_path / "cash_flow_projection_summary.json"
        ),
        "manager_mandate_catalog": _load_json(prerequisite_path / "manager_mandate_catalog.json"),
        "lens_exposure_summary": _load_json(
            prerequisite_path / "lens_exposure_prerequisite_summary.json"
        ),
        "scenario_lens_readiness": _load_json(
            prerequisite_path / "scenario_lens_readiness_summary.json"
        ),
        "lenses": {
            lens_id: _load_json(prerequisite_path / filename)
            for lens_id, filename in LENS_FILES.items()
        },
        "lens_assignments": {
            lens_id: _load_json(prerequisite_path / filename)
            for lens_id, filename in LENS_ASSIGNMENT_FILES.items()
        },
    }


def build_revaluation_report_inputs_v2(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = _position_rows(context)
    base_value = float(context["base_valuation"]["summary"]["total_value"])
    portfolio_summaries = context["portfolio_summaries"]
    cross_scenario = context["cross_scenario"]
    mandates = _manager_mandates_by_id(context)
    manager_rows = _manager_allocation_rows(context, base_value)
    asset_rows = _asset_allocation_rows(rows, base_value)
    coverage_rows = _coverage_rows(portfolio_summaries["ai_chip_selloff"], base_value)
    worst_scenario = _worst_scenario(cross_scenario["scenarios"])

    return {
        "portfolio_representation_status": _portfolio_representation_input(
            rows, base_value, context
        ),
        "aggregated_asset_allocation": _aggregated_asset_allocation_input(
            asset_rows, base_value, context
        ),
        "allocation_by_manager": _allocation_by_manager_input(
            manager_rows, base_value, context
        ),
        "coverage_confidence_warning": _coverage_confidence_warning_input(
            coverage_rows, portfolio_summaries["ai_chip_selloff"], context
        ),
        "concentration_by_asset_type": _concentration_by_asset_type_input(
            asset_rows, context
        ),
        "concentration_by_manager_sleeve": _concentration_by_manager_sleeve_input(
            manager_rows, context
        ),
        "current_portfolio_scenario_downside": _scenario_downside_input(
            cross_scenario, worst_scenario, context
        ),
        "manager_role_summary": _manager_role_summary_input(
            mandates, manager_rows, context
        ),
        "cash_flow_delivered": _cash_flow_delivered_input(context),
        "cash_flow_support_outlook": _cash_flow_support_outlook_input(context),
        "full_lens_exposure_ai_adoption": _full_lens_exposure_input(
            "ai_adoption", context
        ),
        "full_lens_exposure_energy_security": _full_lens_exposure_input(
            "energy_security", context
        ),
        "manager_by_lens_exposure_ai_adoption": _manager_by_lens_input(
            "ai_adoption", mandates, context
        ),
        "manager_by_lens_exposure_energy_security": _manager_by_lens_input(
            "energy_security", mandates, context
        ),
    }


def build_revaluation_report_views_v2(
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
            "master_question_family": payload["master_question_family"],
            "exact_report_question": payload["exact_report_question"],
            "audience_tier": payload["audience_tier"],
            "summary_detail_status": payload["summary_detail_status"],
            "representation_level": payload["representation_level"],
            "denominator_category_system": payload["denominator_category_system"],
            "rendering_mode": payload["rendering_mode"],
            "headline_sentence": visible["headline_sentence"],
            "headline_metrics": visible["headline_metrics"],
            "compact_table": visible.get("compact_table"),
            "caveats": visible.get("caveats", []),
            "advisor_note": visible.get("advisor_note"),
            "visual_placeholder": visible.get("visual_placeholder"),
            "internal_source_refs": payload["internal_source_refs"],
            "source_prerequisite_pack_refs": payload.get("source_prerequisite_pack_refs", []),
            "information_budget_applied": _budget_actuals(
                report_id=report_id,
                rendering_mode=payload["rendering_mode"],
                visible=visible,
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

    if view.get("visual_placeholder"):
        lines.extend(["## Visual", "", view["visual_placeholder"], ""])

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


def generate_revaluation_report_views_v2(
    *,
    revaluation_dir: str | Path = DEFAULT_REVALUATION_DIR,
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

    context = load_source_context(
        revaluation_dir=revaluation_dir,
        prerequisite_dir=prerequisite_dir,
    )
    inputs = build_revaluation_report_inputs_v2(context)
    views = build_revaluation_report_views_v2(inputs)

    input_files: list[str] = []
    for report_id in BUILD_NOW_REPORT_IDS:
        filename = f"{report_id}_input.json"
        _write_json(input_path / filename, inputs[report_id])
        input_files.append(filename)

    input_summary = _input_summary(input_files, inputs)
    _write_json(input_path / "revaluation_report_v2_input_summary.json", input_summary)
    input_files.append("revaluation_report_v2_input_summary.json")

    view_files: list[str] = []
    mockup_files: list[str] = []
    for report_id in BUILD_NOW_REPORT_IDS:
        view_filename = f"{report_id}_view.json"
        mockup_filename = MOCKUP_FILENAME_BY_REPORT_ID[report_id]
        view = views[report_id]
        markdown = render_markdown_mockup(view)
        _write_json(view_path / view_filename, view)
        (mockup_path / mockup_filename).write_text(markdown, encoding="utf-8")
        view_files.append(view_filename)
        mockup_files.append(mockup_filename)

    gated_index = _gated_deferred_index()
    _write_json(view_path / "gated_deferred_report_index.json", gated_index)
    view_files.append("gated_deferred_report_index.json")

    readme = render_mockup_readme(views, gated_index)
    (mockup_path / "README.md").write_text(readme, encoding="utf-8")
    mockup_files.append("README.md")

    view_summary = _view_summary(view_files, mockup_files, views, gated_index)
    _write_json(view_path / "revaluation_report_v2_view_summary.json", view_summary)
    view_files.append("revaluation_report_v2_view_summary.json")

    return {
        "schema_version": "revaluation_report_v2_generation_summary.v1",
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "report_input_count": len(inputs),
        "report_view_count": len(views),
        "markdown_mockup_count": len(MOCKUP_FILENAME_BY_REPORT_ID),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "gated_reports_not_generated": [row["report_id"] for row in GATED_REPORTS],
        "input_dir": _as_posix(input_path),
        "view_dir": _as_posix(view_path),
        "mockup_dir": _as_posix(mockup_path),
        "input_files": input_files,
        "view_files": view_files,
        "mockup_files": mockup_files,
        "mockups_generated_from_views": True,
    }


def render_mockup_readme(views: dict[str, dict[str, Any]], gated_index: dict[str, Any]) -> str:
    lines = [
        "# Revaluation v2 Report Mockups",
        "",
        "These product-review mockups are generated from v2 report view fixtures. They preserve the v1 mockups for comparison and stay local-only; they are not wired into Advisor Preview, Populate, Present, generated reports, Docker, or deployment.",
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
        status = row.get("status")
        prefix = f"{row['display_title']} ({status})" if status else row["display_title"]
        lines.append(f"- {prefix}: {row['reason']}")

    lines.append("")
    return "\n".join(lines)


def _portfolio_representation_input(
    rows: list[dict[str, Any]],
    base_value: float,
    context: dict[str, Any],
) -> dict[str, Any]:
    grouped = {
        "Direct positions": {"value": 0.0, "count": 0},
        "Fund/NAV positions with limited look-through": {"value": 0.0, "count": 0},
        "Manager/sleeve-level holdings requiring review": {"value": 0.0, "count": 0},
        "Other review-required exposure": {"value": 0.0, "count": 0},
    }
    for row in rows:
        if row["instrument_type"] in {"opaque_manager_level"}:
            bucket = "Manager/sleeve-level holdings requiring review"
        elif row["review_required"]:
            bucket = "Other review-required exposure"
        elif row["instrument_type"] in {
            "data_center_investment",
            "etf",
            "private_credit",
            "private_equity",
            "real_estate",
        }:
            bucket = "Fund/NAV positions with limited look-through"
        else:
            bucket = "Direct positions"
        grouped[bucket]["value"] += row["base_value"]
        grouped[bucket]["count"] += 1

    table_rows = []
    for label, values in grouped.items():
        if values["value"] or label == "Review-required exposure":
            table_rows.append(
                {
                    "Representation": label,
                    "Positions": _format_count(values["count"]),
                    "Value": _format_money(values["value"]),
                    "Portfolio Share": _format_percent(values["value"] / base_value),
                }
            )

    review_value = (
        grouped["Manager/sleeve-level holdings requiring review"]["value"]
        + grouped["Other review-required exposure"]["value"]
    )
    direct_share = grouped["Direct positions"]["value"] / base_value
    return _report_input(
        report_element_id="portfolio_representation_status",
        display_title="Portfolio Representation Status",
        master_question_family="Ownership / Exposure",
        exact_report_question="What is the current portfolio state, and how complete is our view?",
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="whole portfolio with representation-status rows",
        denominator_category_system="portfolio value by representation status",
        rendering_mode="summary_first",
        internal_source_refs=[
            context["source_paths"]["position_catalog"],
            context["source_paths"]["instrument_catalog"],
            context["source_paths"]["base_valuation"],
        ],
        visible_content={
            "headline_sentence": (
                f"The portfolio is {_format_money(base_value)}, with "
                f"{_format_percent(direct_share)} in direct positions and "
                f"{_format_money(review_value)} needing review before point-impact claims."
            ),
            "headline_metrics": [
                _metric("Base portfolio value", base_value, _format_money(base_value)),
                _metric("Direct position share", direct_share, _format_percent(direct_share)),
                _metric("Review-required value", review_value, _format_money(review_value)),
            ],
            "compact_table": _compact_table(
                "Representation Mix",
                ["Representation", "Positions", "Value", "Portfolio Share"],
                table_rows,
            ),
            "caveats": [
                "Fund/NAV and manager-level rows do not imply full underlying look-through.",
                "Review-required exposure should stay advisor-review until resolved.",
            ],
            "advisor_note": None,
        },
        table_validation={
            "row_value_total": round(sum(item["value"] for item in grouped.values()), 2),
            "base_value": round(base_value, 2),
            "row_share_total": 1.0,
            "category_system": "representation_status",
            "review_required_value": round(review_value, 2),
            "future_manager_level_representation_view_possible": True,
        },
    )


def _aggregated_asset_allocation_input(
    asset_rows: list[dict[str, Any]],
    base_value: float,
    context: dict[str, Any],
) -> dict[str, Any]:
    largest = asset_rows[0]
    table_rows = [
        {
            "Asset Type": row["label"],
            "Value": _format_money(row["value"]),
            "Portfolio Share": _format_percent(row["share"]),
        }
        for row in asset_rows
    ]
    return _report_input(
        report_element_id="aggregated_asset_allocation",
        display_title="Aggregated Asset Allocation",
        master_question_family="Ownership / Exposure",
        exact_report_question="What does the portfolio own by broad asset type?",
        audience_tier="client_briefing",
        summary_detail_status="summary",
        representation_level="portfolio holdings grouped by asset type",
        denominator_category_system="broad asset type share of base portfolio value",
        rendering_mode="table_first",
        internal_source_refs=[
            context["source_paths"]["position_catalog"],
            context["source_paths"]["instrument_catalog"],
            context["source_paths"]["base_valuation"],
        ],
        visible_content={
            "headline_sentence": (
                f"{largest['label']} is the largest broad allocation at "
                f"{_format_money(largest['value'])} ({_format_percent(largest['share'])})."
            ),
            "headline_metrics": [
                _metric("Largest asset type", largest["label"], largest["label"]),
                _metric("Largest asset value", largest["value"], _format_money(largest["value"])),
            ],
            "compact_table": _compact_table(
                "Asset Type Allocation",
                ["Asset Type", "Value", "Portfolio Share"],
                table_rows,
            ),
            "caveats": ["Small asset-type buckets are grouped into Other to keep the summary readable."],
            "advisor_note": None,
        },
        table_validation={
            "row_value_total": round(sum(row["value"] for row in asset_rows), 2),
            "base_value": round(base_value, 2),
            "row_share_total": round(sum(row["share"] for row in asset_rows), 6),
            "category_system": "asset_type",
        },
    )


def _allocation_by_manager_input(
    manager_rows: list[dict[str, Any]],
    base_value: float,
    context: dict[str, Any],
) -> dict[str, Any]:
    largest = manager_rows[0]
    table_rows = [
        {
            "Manager/Sleeve": row["label"],
            "Value": _format_money(row["value"]),
            "Portfolio Share": _format_percent(row["share"]),
        }
        for row in manager_rows
    ]
    return _report_input(
        report_element_id="allocation_by_manager",
        display_title="Allocation by Manager",
        master_question_family="Ownership / Exposure",
        exact_report_question="How is the portfolio allocated across managers or sleeves?",
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="manager/sleeve",
        denominator_category_system="manager/sleeve share of base portfolio value",
        rendering_mode="table_first",
        internal_source_refs=[
            context["source_paths"]["manager_mandate_catalog"],
            context["source_paths"]["base_valuation"],
        ],
        source_prerequisite_pack_refs=["manager_mandate_catalog.json"],
        visible_content={
            "headline_sentence": (
                f"{largest['label']} is the largest manager/sleeve at "
                f"{_format_percent(largest['share'])} of portfolio value."
            ),
            "headline_metrics": [
                _metric("Largest manager/sleeve", largest["label"], largest["label"]),
                _metric("Largest share", largest["share"], _format_percent(largest["share"])),
            ],
            "compact_table": _compact_table(
                "Manager/Sleeve Allocation",
                ["Manager/Sleeve", "Value", "Portfolio Share"],
                table_rows,
            ),
            "caveats": [
                "Smaller managers and sleeves are grouped; the grouped row is material enough for separate review if this becomes the meeting focus."
            ],
            "advisor_note": None,
        },
        table_validation={
            "row_value_total": round(sum(row["value"] for row in manager_rows), 2),
            "base_value": round(base_value, 2),
            "row_share_total": round(sum(row["share"] for row in manager_rows), 6),
            "category_system": "manager_sleeve",
            "grouped_row_label": "Smaller managers / sleeves",
            "future_full_manager_detail_possible": True,
        },
    )


def _coverage_confidence_warning_input(
    coverage_rows: list[dict[str, Any]],
    portfolio_summary: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    by_status = portfolio_summary["coverage_summary"]["by_status"]
    review = by_status["review_required"]
    held = by_status["held_at_mark_with_caveat"]
    policy = by_status["valued_with_approved_policy"]
    table_rows = [
        {
            "Status": row["label"],
            "Positions": _format_count(row["count"]),
            "Base Value": _format_money(row["value"]),
            "Advisor Meaning": row["meaning"],
        }
        for row in coverage_rows
    ]
    return _report_input(
        report_element_id="coverage_confidence_warning",
        display_title="Coverage and Confidence Warning",
        master_question_family="Risk / Downside",
        exact_report_question="Can the advisor trust the numbers enough to show them?",
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="coverage/confidence status buckets",
        denominator_category_system="coverage/confidence status",
        rendering_mode="summary_first",
        internal_source_refs=[
            context["source_paths"]["coverage_attribution_ai_chip_selloff"],
            context["source_paths"]["confidence_attribution_ai_chip_selloff"],
            context["source_paths"]["portfolio_summary_ai_chip_selloff"],
        ],
        visible_content={
            "headline_sentence": (
                f"{int(review['count'])} positions representing {_format_money(review['base_value'])} "
                "need review before relying on point scenario impact."
            ),
            "headline_metrics": [
                _metric("Review-required value", review["base_value"], _format_money(review["base_value"])),
                _metric("Held-at-mark value", held["base_value"], _format_money(held["base_value"])),
                _metric("Approved-policy value", policy["base_value"], _format_money(policy["base_value"])),
            ],
            "compact_table": _compact_table(
                "Coverage Summary",
                ["Status", "Positions", "Base Value", "Advisor Meaning"],
                table_rows,
            ),
            "caveats": [
                "Review-required exposure should not support strong point-impact claims.",
                "Held-at-mark exposure may understate stress exposure.",
            ],
            "advisor_note": "Resolve the review-required bucket before treating this as client-ready language.",
        },
        table_validation={
            "category_system": "coverage_confidence_status",
            "coverage_rows": [row["status"] for row in coverage_rows],
            "contains_review_required": True,
            "contains_held_at_mark": True,
            "contains_approved_policy": True,
            "future_coverage_by_manager_slice_possible": True,
        },
    )


def _concentration_by_asset_type_input(
    asset_rows: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    largest = asset_rows[0]
    table_rows = [
        {
            "Asset Type": row["label"],
            "Portfolio Share": _format_percent(row["share"]),
            "Value": _format_money(row["value"]),
            "Why It Matters": ASSET_TYPE_MEANINGS.get(row["label"], "Grouped exposure for readability."),
        }
        for row in asset_rows
    ]
    return _report_input(
        report_element_id="concentration_by_asset_type",
        display_title="Concentration by Asset Type",
        master_question_family="Risk / Downside",
        exact_report_question="Is the portfolio concentrated by broad asset type?",
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="asset-type bucket",
        denominator_category_system="broad asset type share of base portfolio value",
        rendering_mode="table_first",
        internal_source_refs=[
            context["source_paths"]["position_catalog"],
            context["source_paths"]["instrument_catalog"],
            context["source_paths"]["base_valuation"],
        ],
        visible_content={
            "headline_sentence": (
                f"{largest['label']} is the largest asset-type concentration at "
                f"{_format_percent(largest['share'])} of portfolio value."
            ),
            "headline_metrics": [
                _metric("Largest concentration", largest["label"], largest["label"]),
                _metric("Largest share", largest["share"], _format_percent(largest["share"])),
            ],
            "compact_table": _compact_table(
                "Asset-Type Concentrations",
                ["Asset Type", "Portfolio Share", "Value", "Why It Matters"],
                table_rows,
            ),
            "caveats": ["This concentration view uses asset type only; manager and coverage views are separate."],
            "advisor_note": None,
        },
        table_validation={
            "category_system": "asset_type",
            "row_share_total": round(sum(row["share"] for row in asset_rows), 6),
            "mixed_category_systems": False,
        },
    )


def _concentration_by_manager_sleeve_input(
    manager_rows: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    largest = manager_rows[0]
    table_rows = [
        {
            "Manager/Sleeve": row["label"],
            "Portfolio Share": _format_percent(row["share"]),
            "Value": _format_money(row["value"]),
            "Interpretation": (
                "Largest manager/sleeve exposure."
                if index == 0
                else (
                    "Grouped smaller managers/sleeves."
                    if row["label"] == "Smaller managers / sleeves"
                    else "Part of the same manager/sleeve grouping."
                )
            ),
        }
        for index, row in enumerate(manager_rows)
    ]
    return _report_input(
        report_element_id="concentration_by_manager_sleeve",
        display_title="Concentration by Manager/Sleeve",
        master_question_family="Risk / Downside",
        exact_report_question="Is the portfolio concentrated in one manager or sleeve?",
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="manager/sleeve",
        denominator_category_system="manager/sleeve share of base portfolio value",
        rendering_mode="table_first",
        internal_source_refs=[
            context["source_paths"]["manager_mandate_catalog"],
            context["source_paths"]["manager_attribution_ai_chip_selloff"],
        ],
        source_prerequisite_pack_refs=["manager_mandate_catalog.json"],
        visible_content={
            "headline_sentence": (
                f"{largest['label']} is the largest manager/sleeve concentration at "
                f"{_format_percent(largest['share'])}."
            ),
            "headline_metrics": [
                _metric("Largest manager/sleeve", largest["label"], largest["label"]),
                _metric("Largest share", largest["share"], _format_percent(largest["share"])),
            ],
            "compact_table": _compact_table(
                "Manager/Sleeve Concentrations",
                ["Manager/Sleeve", "Portfolio Share", "Value", "Interpretation"],
                table_rows,
            ),
            "caveats": [
                "This concentration view uses manager/sleeve only; asset type and coverage are separate.",
                "Smaller managers and sleeves are grouped; the grouped row is material enough for separate review if needed.",
            ],
            "advisor_note": (
                "The largest manager/sleeve is above a quarter of portfolio value, so size alone deserves review."
            ),
        },
        table_validation={
            "category_system": "manager_sleeve",
            "row_share_total": round(sum(row["share"] for row in manager_rows), 6),
            "mixed_category_systems": False,
            "grouped_row_label": "Smaller managers / sleeves",
            "future_full_manager_detail_possible": True,
        },
    )


def _scenario_downside_input(
    cross_scenario: dict[str, Any],
    worst_scenario: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    scenario_rows = []
    for row in sorted(cross_scenario["scenarios"], key=lambda item: float(item["impact"])):
        scenario_rows.append(
            {
                "Scenario": _scenario_label(row["scenario_id"]),
                "Portfolio Impact": _format_money(row["impact"]),
                "Portfolio Change": _format_percent(row["impact_percent"]),
                "Value After Scenario": _format_money(row["scenario_portfolio_value"]),
                "Status": "Deterministic stress",
            }
        )
    return _report_input(
        report_element_id="current_portfolio_scenario_downside",
        display_title="Current Portfolio Scenario Downside",
        master_question_family="Risk / Downside",
        exact_report_question=(
            "How does the current portfolio revalue under selected approved downside scenarios?"
        ),
        audience_tier="client_briefing",
        summary_detail_status="summary",
        representation_level="whole portfolio scenario result",
        denominator_category_system="approved deterministic scenarios",
        rendering_mode="table_first",
        internal_source_refs=[
            context["source_paths"]["cross_scenario"],
            context["source_paths"]["portfolio_summary_ai_chip_selloff"],
            context["source_paths"]["portfolio_summary_rate_shock"],
        ],
        visible_content={
            "headline_sentence": (
                f"{_scenario_label(worst_scenario['scenario_id'])} is the larger deterministic downside case, "
                f"reducing portfolio value by {_format_money(abs(worst_scenario['impact']))} "
                f"({_format_percent(worst_scenario['impact_percent'])})."
            ),
            "headline_metrics": [
                _metric(
                    "Larger downside case",
                    _scenario_label(worst_scenario["scenario_id"]),
                    _scenario_label(worst_scenario["scenario_id"]),
                ),
                _metric("Portfolio impact", worst_scenario["impact"], _format_money(worst_scenario["impact"])),
                _metric(
                    "Portfolio change",
                    worst_scenario["impact_percent"],
                    _format_percent(worst_scenario["impact_percent"]),
                ),
            ],
            "compact_table": _compact_table(
                "Scenario Results",
                [
                    "Scenario",
                    "Portfolio Impact",
                    "Portfolio Change",
                    "Value After Scenario",
                    "Status",
                ],
                scenario_rows,
            ),
            "caveats": [
                "Scenarios are deterministic stress views, not forecasts.",
                "This base report does not include benchmark, manager, or lens breakdowns.",
            ],
            "advisor_note": None,
        },
        table_validation={
            "category_system": "deterministic_scenario",
            "scenario_count": len(scenario_rows),
            "benchmark_comparison_included": False,
            "probabilistic_range_included": False,
            "deterministic_stress_not_forecast": True,
            "probabilistic_range_status": "design_soon_prerequisite_soon_not_included",
        },
    )


def _manager_role_summary_input(
    mandates: dict[str, dict[str, Any]],
    manager_rows: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    sorted_mandates = sorted(
        mandates.values(), key=lambda row: float(row["base_value"]), reverse=True
    )
    visible_mandates = sorted_mandates[: DEFAULT_INFORMATION_BUDGET["max_visible_table_rows"]]
    largest = visible_mandates[0]
    table_rows = [
        {
            "Manager/Sleeve": row["manager_display_name"],
            "Approved Role": row["intended_role"],
            "Portfolio Share": _format_percent(row["portfolio_share"]),
            "Actual Exposure / Key Risk": row["key_risk_for_report"],
            "Mandate Fit Note": row["mandate_expression_summary"],
        }
        for row in visible_mandates
    ]
    return _report_input(
        report_element_id="manager_role_summary",
        display_title="Manager Role Summary",
        master_question_family="Ownership / Exposure",
        exact_report_question=(
            "Why is each manager in the portfolio, and is the intended role being expressed?"
        ),
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="manager/sleeve",
        denominator_category_system="manager/sleeve share with approved role language",
        rendering_mode="table_first",
        internal_source_refs=[
            context["source_paths"]["manager_mandate_catalog"],
            context["source_paths"]["manager_attribution_ai_chip_selloff"],
            context["source_paths"]["manager_attribution_rate_shock"],
        ],
        source_prerequisite_pack_refs=["manager_mandate_catalog.json"],
        visible_content={
            "headline_sentence": (
                f"Each major manager has an approved synthetic role; {largest['manager_display_name']} "
                f"is the largest current manager/sleeve at {_format_percent(largest['portfolio_share'])}."
            ),
            "headline_metrics": [
                _metric("Largest manager/sleeve", largest["manager_display_name"], largest["manager_display_name"]),
                _metric(
                    "Largest share",
                    largest["portfolio_share"],
                    _format_percent(largest["portfolio_share"]),
                ),
                _metric("Managers shown", len(visible_mandates), _format_count(len(visible_mandates))),
            ],
            "compact_table": _compact_table(
                "Manager Roles",
                [
                    "Manager/Sleeve",
                    "Approved Role",
                    "Portfolio Share",
                    "Actual Exposure / Key Risk",
                    "Mandate Fit Note",
                ],
                table_rows,
            ),
            "caveats": [
                "Role language is approved for the synthetic local demo, not real client mandate approval.",
                "Rows show the five largest managers by base value to stay within the summary budget.",
            ],
            "advisor_note": "Use this report to explain manager purpose, not to rank managers.",
        },
        table_validation={
            "category_system": "manager_role",
            "role_language_source": "synthetic_manager_mandate_catalog",
            "role_language_repeats_manager_name": False,
            "visible_manager_count": len(visible_mandates),
            "manager_row_count": len(manager_rows),
        },
    )


def _cash_flow_delivered_input(context: dict[str, Any]) -> dict[str, Any]:
    history = context["cash_flow_history_summary"]
    generated = float(history["cash_generated_last_period"]["amount"])
    paid_out = float(history["cash_paid_out_last_period"]["amount"])
    retained = float(history["net_cash_after_paid_out"]["amount"])
    period_label = _period_label(history["history_period"])
    table_rows = [
        {
            "Period": period_label,
            "Generated": _format_money(generated),
            "Paid Out": _format_money(paid_out),
            "Retained/Reinvested": _format_money(retained),
        }
    ]
    return _report_input(
        report_element_id="cash_flow_delivered",
        display_title="Cash Flow Delivered",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "What cash did the portfolio actually generate and make available during the last period?"
        ),
        audience_tier="client_briefing",
        summary_detail_status="summary",
        representation_level="whole portfolio trailing-period cash flow",
        denominator_category_system="cash generated and paid out over the same trailing period",
        rendering_mode="summary_first",
        internal_source_refs=[
            context["source_paths"]["cash_flow_history_summary"],
        ],
        source_prerequisite_pack_refs=["cash_flow_history_summary.json"],
        visible_content={
            "headline_sentence": (
                f"During the {period_label}, the portfolio generated {_format_money(generated)} "
                f"and made {_format_money(paid_out)} available for payouts."
            ),
            "headline_metrics": [
                _metric("Cash generated", generated, _format_money(generated)),
                _metric("Cash paid out", paid_out, _format_money(paid_out)),
                _metric("Retained/reinvested", retained, _format_money(retained)),
            ],
            "compact_table": _compact_table(
                "Cash Delivered Last Period",
                ["Period", "Generated", "Paid Out", "Retained/Reinvested"],
                table_rows,
            ),
            "caveats": [history["confidence_caveat"]],
            "advisor_note": (
                "Forward-looking cash support is a separate report; manager/sleeve cash-flow detail waits for reliable source data."
            ),
        },
        table_validation={
            "cash_generated_last_period": generated,
            "cash_paid_out_last_period": paid_out,
            "net_cash_after_paid_out": retained,
            "period_label": period_label,
            "backward_looking": True,
            "next_period_projection_included": False,
            "cash_flow_by_manager_sleeve_ready": history["cash_flow_by_manager_sleeve_ready"],
            "future_cash_flow_by_manager_sleeve_view_possible_when_source_data_supports": True,
        },
    )


def _cash_flow_support_outlook_input(context: dict[str, Any]) -> dict[str, Any]:
    cash = context["cash_flow_support_inputs"]
    need = context["cash_flow_need_profile"]
    projection = context["cash_flow_projection_summary"]
    required = cash["required_inputs"]
    support = cash["support_logic"]
    surplus = float(required["projected_surplus_shortfall"])
    projection_period = _period_label(projection["projection_period"])
    funding_policy = need["funding_policy"]
    table_rows = [
        {
            "Measure": "Stated annual cash need",
            "Amount / Label": _format_money(required["stated_annual_cash_need"]),
        },
        {
            "Measure": "Projected next-period generation",
            "Amount / Label": _format_money(required["projected_cash_generation"]),
        },
        {
            "Measure": "Projected surplus versus need",
            "Amount / Label": _format_money(surplus),
        },
        {
            "Measure": "Projection period",
            "Amount / Label": projection_period,
        },
    ]
    return _report_input(
        report_element_id="cash_flow_support_outlook",
        display_title="Cash-Flow Support Outlook",
        master_question_family="Performance / Plan",
        exact_report_question=(
            "Will projected cash generation support the stated annual or quarterly cash need?"
        ),
        audience_tier="client_briefing",
        summary_detail_status="summary",
        representation_level="whole portfolio forward cash-flow support outlook",
        denominator_category_system="stated cash need versus projected cash generation",
        rendering_mode="summary_first",
        internal_source_refs=[
            context["source_paths"]["cash_flow_support_inputs"],
            context["source_paths"]["cash_flow_need_profile"],
            context["source_paths"]["cash_flow_projection_summary"],
        ],
        source_prerequisite_pack_refs=[
            "cash_flow_support_inputs.json",
            "cash_flow_need_profile.json",
            "cash_flow_projection_summary.json",
        ],
        visible_content={
            "headline_sentence": (
                f"Projected cash generation exceeds the stated annual need by "
                f"{_format_money(surplus)} in the synthetic local demo."
            ),
            "headline_metrics": [
                _metric(
                    "Annual cash need",
                    required["stated_annual_cash_need"],
                    _format_money(required["stated_annual_cash_need"]),
                ),
                _metric(
                    "Projected generation",
                    required["projected_cash_generation"],
                    _format_money(required["projected_cash_generation"]),
                ),
                _metric("Projected surplus", surplus, _format_money(surplus)),
            ],
            "compact_table": _compact_table(
                "Cash-Flow Support Outlook",
                ["Measure", "Amount / Label"],
                table_rows,
            ),
            "caveats": [
                projection["confidence_caveat"],
                "Do not infer support from cash balances alone; this outlook uses the stated need and projected generation inputs.",
            ],
            "advisor_note": (
                "Funding policy: use income and distributions first, then "
                f"{funding_policy['secondary_source'].replace('_', ' ')}, with advisor review rebalancing if needed."
            ),
        },
        table_validation={
            "cash_flow_support_status": cash["status"],
            "support_logic": support["calculation"],
            "need_coverage_ratio": support["need_coverage_ratio"],
            "projected_cash_generation": float(required["projected_cash_generation"]),
            "stated_annual_cash_need": float(required["stated_annual_cash_need"]),
            "projected_surplus_shortfall": surplus,
            "forward_looking": True,
            "last_period_generated_or_paid_out_included": False,
            "cash_flow_by_manager_sleeve_ready": False,
            "future_cash_flow_by_manager_sleeve_view_possible_when_source_data_supports": True,
        },
    )


def _full_lens_exposure_input(lens_key: str, context: dict[str, Any]) -> dict[str, Any]:
    lens = context["lenses"][lens_key]
    assignments = context["lens_assignments"][lens_key]
    bucket_rows = assignments["bucket_exposure_summary"]
    largest = max(bucket_rows, key=lambda row: float(row["base_value"]))
    review = next(
        row for row in bucket_rows if row["bucket_id"] == assignments["review_required_bucket_id"]
    )
    table_rows = [
        {
            "Lens Bucket": row["bucket_display_name"],
            "Value": _format_money(row["base_value"]),
            "Portfolio Share": _format_percent(row["portfolio_share"]),
            "Positions": _format_count(row["position_count"]),
        }
        for row in bucket_rows
    ]
    report_id = f"full_lens_exposure_{lens_key}"
    return _report_input(
        report_element_id=report_id,
        display_title=f"Full Lens Exposure - {lens['display_name']}",
        master_question_family="Ownership / Exposure",
        exact_report_question=(
            f"How does the whole portfolio map into every bucket of the {lens['display_name']} lens?"
        ),
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="lens bucket",
        denominator_category_system=f"{lens['display_name']} lens buckets over in-scope base value",
        rendering_mode="table_first",
        internal_source_refs=[
            context["source_paths"][f"{lens_key}_lens"],
            context["source_paths"][f"{lens_key}_assignments"],
        ],
        source_prerequisite_pack_refs=[
            LENS_FILES[lens_key],
            LENS_ASSIGNMENT_FILES[lens_key],
        ],
        visible_content={
            "headline_sentence": (
                f"Under the {lens['display_name']} lens, {largest['bucket_display_name']} "
                f"is the largest bucket at {_format_percent(largest['portfolio_share'])}, "
                f"with {_format_percent(review['portfolio_share'])} requiring review."
            ),
            "headline_metrics": [
                _metric("Largest bucket", largest["bucket_display_name"], largest["bucket_display_name"]),
                _metric(
                    "Largest bucket share",
                    largest["portfolio_share"],
                    _format_percent(largest["portfolio_share"]),
                ),
                _metric(
                    "Review bucket share",
                    review["portfolio_share"],
                    _format_percent(review["portfolio_share"]),
                ),
            ],
            "compact_table": _compact_table(
                f"{lens['display_name']} Buckets",
                ["Lens Bucket", "Value", "Portfolio Share", "Positions"],
                table_rows,
            ),
            "caveats": [
                "Every in-scope synthetic position has one primary bucket; no weighted splits are used.",
                "Review buckets remain visible instead of being forced into another category.",
            ],
            "advisor_note": None,
        },
        table_validation={
            "category_system": lens["lens_id"],
            "bucket_count": len(bucket_rows),
            "all_lens_buckets_included": True,
            "contains_neutral_bucket": any(
                row["bucket_id"] == assignments["neutral_bucket_id"] for row in bucket_rows
            ),
            "contains_review_bucket": any(
                row["bucket_id"] == assignments["review_required_bucket_id"] for row in bucket_rows
            ),
            "row_share_total": round(sum(float(row["portfolio_share"]) for row in bucket_rows), 6),
            "base_value_total": assignments["coverage_summary"]["base_value_total"],
            "assigned_base_value": assignments["coverage_summary"]["assigned_base_value"],
            "weighted_splits_used": False,
        },
    )


def _manager_by_lens_input(
    lens_key: str,
    mandates: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    lens = context["lenses"][lens_key]
    assignments = context["lens_assignments"][lens_key]
    bucket_ids = [row["bucket_id"] for row in lens["primary_buckets"]]
    bucket_labels = {
        row["bucket_id"]: _short_lens_bucket_label(row["display_name"])
        for row in lens["primary_buckets"]
    }
    top_managers = sorted(
        mandates.values(), key=lambda row: float(row["base_value"]), reverse=True
    )[:4]
    totals: dict[str, dict[str, float]] = {
        row["manager_id"]: defaultdict(float) for row in top_managers
    }
    for assignment in assignments["assignments"]:
        manager_id = assignment["manager_id"]
        if manager_id in totals:
            totals[manager_id][assignment["primary_bucket_id"]] += float(assignment["base_value"])

    table_rows: list[dict[str, str]] = []
    row_validation = []
    columns = ["Manager/Sleeve"] + [bucket_labels[bucket_id] for bucket_id in bucket_ids]
    for manager in top_managers:
        manager_id = manager["manager_id"]
        denominator = float(manager["base_value"])
        row: dict[str, str] = {"Manager/Sleeve": manager["manager_display_name"]}
        share_total = 0.0
        for bucket_id in bucket_ids:
            share = _safe_divide(totals[manager_id][bucket_id], denominator)
            share_total += share
            row[bucket_labels[bucket_id]] = _format_percent(share)
        table_rows.append(row)
        row_validation.append(
            {
                "manager_id": manager_id,
                "manager_display_name": manager["manager_display_name"],
                "denominator": "manager_base_value",
                "row_share_total": round(share_total, 6),
            }
        )

    largest_manager = top_managers[0]
    largest_bucket_id = max(totals[largest_manager["manager_id"]], key=totals[largest_manager["manager_id"]].get)
    report_id = f"manager_by_lens_exposure_{lens_key}"
    return _report_input(
        report_element_id=report_id,
        display_title=f"Manager by Lens Exposure - {lens['display_name']}",
        master_question_family="Ownership / Exposure",
        exact_report_question=(
            f"How do managers compare under the same selected {lens['display_name']} lens?"
        ),
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="manager/sleeve rows by lens bucket columns",
        denominator_category_system=(
            f"{lens['display_name']} buckets as percent of each manager's base value"
        ),
        rendering_mode="table_first",
        internal_source_refs=[
            context["source_paths"][f"{lens_key}_lens"],
            context["source_paths"][f"{lens_key}_assignments"],
            context["source_paths"]["manager_mandate_catalog"],
        ],
        source_prerequisite_pack_refs=[
            LENS_FILES[lens_key],
            LENS_ASSIGNMENT_FILES[lens_key],
            "manager_mandate_catalog.json",
        ],
        visible_content={
            "headline_sentence": (
                f"The four largest managers are shown under the same {lens['display_name']} lens; "
                f"{largest_manager['manager_display_name']} is most exposed to "
                f"{bucket_labels[largest_bucket_id]}."
            ),
            "headline_metrics": [
                _metric(
                    "Managers shown",
                    len(top_managers),
                    _format_count(len(top_managers)),
                ),
                _metric("Lens used", lens["display_name"], lens["display_name"]),
                _metric("Row denominator", "manager base value", "Manager base value"),
            ],
            "compact_table": _compact_table(
                f"Manager Mix by {lens['display_name']}",
                columns,
                table_rows,
            ),
            "caveats": [
                "Each manager row uses that manager's own base value as denominator.",
                "The grid is limited to the four largest managers by base value for readability.",
            ],
            "advisor_note": (
                "Use this to compare manager expression under one lens, not to compare across different lenses."
            ),
        },
        table_validation={
            "category_system": lens["lens_id"],
            "manager_count_shown": len(top_managers),
            "row_denominator": "manager_base_value",
            "row_reconciliations": row_validation,
            "all_rows_reconcile_to_one": all(
                abs(row["row_share_total"] - 1.0) <= 0.00001 for row in row_validation
            ),
            "complete_manager_lens_data_exists": True,
        },
    )


def _report_input(
    *,
    report_element_id: str,
    display_title: str,
    master_question_family: str,
    exact_report_question: str,
    audience_tier: str,
    summary_detail_status: str,
    representation_level: str,
    denominator_category_system: str,
    rendering_mode: str,
    internal_source_refs: list[str],
    visible_content: dict[str, Any],
    table_validation: dict[str, Any],
    source_prerequisite_pack_refs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": INPUT_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "report_element_id": report_element_id,
        "display_title": display_title,
        "master_question_family": master_question_family,
        "exact_report_question": exact_report_question,
        "audience_tier": audience_tier,
        "summary_detail_status": summary_detail_status,
        "representation_level": representation_level,
        "denominator_category_system": denominator_category_system,
        "rendering_mode": rendering_mode,
        "visible_content": visible_content,
        "internal_source_refs": internal_source_refs,
        "source_prerequisite_pack_refs": source_prerequisite_pack_refs or [],
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
        "purpose": "Product/readiness index for v2 reports deliberately not generated.",
        "gated_or_deferred_reports": list(GATED_REPORTS),
    }


def _position_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    positions = {row["position_id"]: row for row in context["position_catalog"]["positions"]}
    instruments = {
        row["instrument_id"]: row for row in context["instrument_catalog"]["instruments"]
    }
    rows = []
    for result in context["base_valuation"]["position_results"]:
        position = positions[result["position_id"]]
        instrument = instruments[result["instrument_id"]]
        rows.append(
            {
                "position_id": result["position_id"],
                "display_name": position["display_name"],
                "instrument_id": result["instrument_id"],
                "instrument_type": instrument["instrument_type"],
                "manager_id": position["manager_id"],
                "sleeve_id": position["sleeve_id"],
                "coverage_status": result["coverage_status"],
                "confidence": result["confidence"],
                "review_required": bool(result["review_required"]),
                "base_value": float(result["value"]),
            }
        )
    return rows


def _asset_allocation_rows(rows: list[dict[str, Any]], base_value: float) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, float]] = defaultdict(lambda: {"value": 0.0, "count": 0})
    for row in rows:
        label = ASSET_TYPE_LABELS.get(row["instrument_type"], "Other")
        grouped[label]["value"] += row["base_value"]
        grouped[label]["count"] += 1
    raw_rows = [
        {
            "label": label,
            "value": round(values["value"], 2),
            "count": int(values["count"]),
            "share": _safe_divide(values["value"], base_value),
        }
        for label, values in grouped.items()
        if values["value"]
    ]
    raw_rows.sort(key=lambda row: row["value"], reverse=True)
    return _group_with_other(raw_rows, max_rows=5)


def _manager_allocation_rows(context: dict[str, Any], base_value: float) -> list[dict[str, Any]]:
    mandates = list(context["manager_mandate_catalog"]["manager_mandates"])
    rows = [
        {
            "label": row["manager_display_name"],
            "manager_id": row["manager_id"],
            "value": round(float(row["base_value"]), 2),
            "count": int(row["position_count"]),
            "share": _safe_divide(row["base_value"], base_value),
        }
        for row in mandates
    ]
    rows.sort(key=lambda row: row["value"], reverse=True)
    return _group_with_other(rows, max_rows=5, other_label="Smaller managers / sleeves")


def _coverage_rows(portfolio_summary: dict[str, Any], base_value: float) -> list[dict[str, Any]]:
    by_status = portfolio_summary["coverage_summary"]["by_status"]
    ordered_statuses = (
        "valued",
        "valued_with_approved_policy",
        "held_at_mark_with_caveat",
        "review_required",
        "not_valued",
    )
    rows = []
    for status in ordered_statuses:
        values = by_status.get(status)
        if values is None:
            continue
        value = float(values["base_value"])
        count = int(values["count"])
        if value == 0 and count == 0 and status != "not_valued":
            continue
        rows.append(
            {
                "status": status,
                "label": COVERAGE_LABELS.get(status, _title_from_id(status)),
                "value": value,
                "count": count,
                "share": _safe_divide(value, base_value),
                "meaning": COVERAGE_MEANINGS.get(status, "Use with advisor review."),
            }
        )
    return rows[:5]


def _manager_mandates_by_id(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["manager_id"]: row
        for row in context["manager_mandate_catalog"]["manager_mandates"]
    }


def _group_with_other(
    rows: list[dict[str, Any]],
    *,
    max_rows: int,
    other_label: str = "Other",
) -> list[dict[str, Any]]:
    if len(rows) <= max_rows:
        total = sum(row["share"] for row in rows)
        if total:
            rows[-1]["share"] += round(1.0 - total, 6)
        return rows

    visible = [dict(row) for row in rows[: max_rows - 1]]
    other_rows = rows[max_rows - 1 :]
    other_value = round(sum(row["value"] for row in other_rows), 2)
    other_count = sum(row.get("count", 0) for row in other_rows)
    other_share = round(1.0 - sum(row["share"] for row in visible), 6)
    visible.append(
        {
            "label": other_label,
            "value": other_value,
            "count": other_count,
            "share": other_share,
        }
    )
    return visible


def _compact_table(title: str, columns: list[str], rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "title": title,
        "columns": columns,
        "rows": [{column: str(row[column]) for column in columns} for row in rows],
    }


def _metric(label: str, value: Any, formatted_value: str) -> dict[str, Any]:
    return {
        "label": label,
        "value": value,
        "formatted_value": formatted_value,
    }


def _period_label(period: dict[str, Any]) -> str:
    return f"{int(period['period_months'])} months ended {period['end_date']}"


def _budget_for_report(report_id: str) -> dict[str, Any]:
    budget = dict(DEFAULT_INFORMATION_BUDGET)
    if report_id.startswith("full_lens_exposure_"):
        budget["max_visible_table_rows"] = 8
        budget["exception_reason"] = "Full Lens Exposure must show every bucket in the selected lens."
    if report_id.startswith("manager_by_lens_exposure_"):
        budget["manager_by_lens_grid_allowed"] = True
    if report_id == "coverage_confidence_warning":
        budget["max_visible_table_rows"] = 5
    return budget


def _budget_actuals(
    *,
    report_id: str,
    rendering_mode: str,
    visible: dict[str, Any],
) -> dict[str, Any]:
    table = visible.get("compact_table")
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
            f"Unexpected v2 report id set. missing={sorted(missing)} unexpected={sorted(unexpected)}"
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
    parts.extend(f"{metric['label']} {metric['formatted_value']}" for metric in view["headline_metrics"])
    table = view.get("compact_table")
    if table:
        parts.append(table["title"])
        parts.extend(table["columns"])
        for row in table["rows"]:
            parts.extend(str(row[column]) for column in table["columns"])
    parts.extend(view.get("caveats") or [])
    if view.get("advisor_note"):
        parts.append(view["advisor_note"])
    if view.get("visual_placeholder"):
        parts.append(view["visual_placeholder"])
    return "\n".join(parts)


def _render_markdown_table(table: dict[str, Any]) -> list[str]:
    columns = table["columns"]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in table["rows"]:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def _worst_scenario(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return min(rows, key=lambda item: float(item["impact"]))


def _scenario_label(scenario_id: str) -> str:
    return SCENARIO_LABELS.get(scenario_id, _title_from_id(scenario_id))


def _short_lens_bucket_label(display_name: str) -> str:
    replacements = {
        "Core AI Infrastructure / Hardware": "Core AI Hardware",
        "AI Model / Platform Exposure": "AI Platform",
        "AI Downstream Productivity Beneficiary": "AI Beneficiary",
        "AI-Disrupted Incumbent": "AI Disrupted",
        "Data Center / Power Bottleneck Exposure": "Data Center/Power",
        "Neutral / Low Direct AI Exposure": "Neutral/Low",
        "Unclassified / Review Required": "Review",
        "Energy Supply Beneficiary": "Energy Supply",
        "Grid Infrastructure Beneficiary": "Grid Infrastructure",
        "Energy Input-Cost Sensitive": "Energy Cost Sensitive",
        "Transition Policy Sensitive": "Transition Policy",
        "Commodity Supply Security Exposure": "Commodity Security",
        "Neutral / Low Direct Energy Exposure": "Neutral/Low",
    }
    return replacements.get(display_name, display_name)


def _format_money(value: Any) -> str:
    number = float(value)
    sign = "-" if number < 0 else ""
    amount = abs(number)
    if amount >= 1_000_000:
        return f"{sign}${amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"{sign}${amount / 1_000:.0f}K"
    return f"{sign}${amount:,.0f}"


def _format_percent(value: Any) -> str:
    return f"{float(value) * 100:.1f}%"


def _format_count(value: Any) -> str:
    return f"{int(value):,}"


def _safe_divide(numerator: Any, denominator: Any) -> float:
    denominator_float = float(denominator)
    if denominator_float == 0:
        return 0.0
    return round(float(numerator) / denominator_float, 6)


def _title_from_id(value: Any) -> str:
    return str(value).replace("_", " ").title()


def _sentence_count(value: str) -> int:
    normalized = value.replace("?", ".").replace("!", ".")
    matches = re.findall(r"[.!?](?:\s|$)", normalized)
    return max(1, len(matches)) if normalized.strip() else 0


def _source_paths(
    revaluation_dir: Path,
    attribution_dir: Path,
    prerequisite_dir: Path,
) -> dict[str, str]:
    paths = {
        "position_catalog": _as_posix(revaluation_dir / "position_catalog.json"),
        "instrument_catalog": _as_posix(revaluation_dir / "instrument_catalog.json"),
        "base_valuation": _as_posix(revaluation_dir / "position_valuation_results_base.json"),
        "scenario_index": _as_posix(revaluation_dir / "revaluation_scenario_index.json"),
        "portfolio_summary_ai_chip_selloff": _as_posix(
            revaluation_dir / "portfolio_revaluation_summary_ai_chip_selloff.json"
        ),
        "portfolio_summary_rate_shock": _as_posix(
            revaluation_dir / "portfolio_revaluation_summary_rate_shock.json"
        ),
        "cross_scenario": _as_posix(
            attribution_dir / "cross_scenario_revaluation_summary.json"
        ),
        "manager_attribution_ai_chip_selloff": _as_posix(
            attribution_dir / "manager_revaluation_attribution_ai_chip_selloff.json"
        ),
        "manager_attribution_rate_shock": _as_posix(
            attribution_dir / "manager_revaluation_attribution_rate_shock.json"
        ),
        "coverage_attribution_ai_chip_selloff": _as_posix(
            attribution_dir / "coverage_revaluation_attribution_ai_chip_selloff.json"
        ),
        "confidence_attribution_ai_chip_selloff": _as_posix(
            attribution_dir / "confidence_revaluation_attribution_ai_chip_selloff.json"
        ),
        "manager_mandate_catalog": _as_posix(prerequisite_dir / "manager_mandate_catalog.json"),
        "cash_flow_support_inputs": _as_posix(prerequisite_dir / "cash_flow_support_inputs.json"),
        "cash_flow_need_profile": _as_posix(prerequisite_dir / "cash_flow_need_profile.json"),
        "cash_flow_history_summary": _as_posix(prerequisite_dir / "cash_flow_history_summary.json"),
        "cash_flow_projection_summary": _as_posix(
            prerequisite_dir / "cash_flow_projection_summary.json"
        ),
    }
    for lens_key, filename in LENS_FILES.items():
        paths[f"{lens_key}_lens"] = _as_posix(prerequisite_dir / filename)
    for lens_key, filename in LENS_ASSIGNMENT_FILES.items():
        paths[f"{lens_key}_assignments"] = _as_posix(prerequisite_dir / filename)
    return paths


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate v2 revaluation report fixtures and mockups.")
    parser.add_argument("--revaluation-dir", default=str(DEFAULT_REVALUATION_DIR))
    parser.add_argument("--prerequisite-dir", default=str(DEFAULT_PREREQUISITE_DIR))
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument("--mockup-dir", default=str(DEFAULT_MOCKUP_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_revaluation_report_views_v2(
        revaluation_dir=args.revaluation_dir,
        prerequisite_dir=args.prerequisite_dir,
        input_dir=args.input_dir,
        view_dir=args.view_dir,
        mockup_dir=args.mockup_dir,
    )

    print(f"V2 report inputs: {summary['report_input_count']} -> {summary['input_dir']}")
    print(f"V2 report views: {summary['report_view_count']} -> {summary['view_dir']}")
    print(f"V2 Markdown mockups: {summary['markdown_mockup_count']} -> {summary['mockup_dir']}")
    print("Generated report ids: " + ", ".join(summary["report_ids"]))
    print("Gated reports not generated: " + ", ".join(summary["gated_reports_not_generated"]))
    print("Output paths: " + summary["input_dir"] + "; " + summary["view_dir"] + "; " + summary["mockup_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
