from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-05T00:00:00Z"

INPUT_SCHEMA_VERSION = "lean_revaluation_report_input.v1"
INPUT_SUMMARY_SCHEMA_VERSION = "lean_revaluation_report_input_summary.v1"
VIEW_SCHEMA_VERSION = "lean_revaluation_report_view.v1"
VIEW_SUMMARY_SCHEMA_VERSION = "lean_revaluation_report_view_summary.v1"
GENERATOR_VERSION = "lean_revaluation_report_views.v1"

DEFAULT_REVALUATION_DIR = Path("data/simulation/revaluation")
DEFAULT_ATTRIBUTION_DIR = DEFAULT_REVALUATION_DIR / "attribution"
DEFAULT_POSITION_UNIVERSE_PATH = Path("data/simulation/synthetic_position_universe.json")
DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs/lean_revaluation_v1")
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/lean_revaluation_v1")
DEFAULT_MOCKUP_DIR = Path("docs/product/report_mockups")

SCENARIO_IDS = ("ai_chip_selloff", "rate_shock")
SCENARIO_LABELS = {
    "ai_chip_selloff": "AI / Chip Selloff",
    "rate_shock": "Rate Shock",
}

BUILD_NOW_REPORT_IDS = (
    "portfolio_status",
    "aggregated_asset_allocation",
    "manager_role_summary",
    "concentration_review",
    "scenario_downside_summary",
    "coverage_confidence_warning",
    "cash_flow_support_readiness",
)

DEFERRED_REPORT_IDS = (
    "performance_vs_benchmark",
    "performance_vs_plan",
    "goal_liability_match",
    "capital_preservation",
    "thesis_lens_attribution",
    "proposed_allocation_change",
    "scenario_before_after_proposal",
    "upside_downside_tradeoff",
    "top_impacted_positions",
)

INFORMATION_BUDGET = {
    "max_headline_sentences": 1,
    "max_headline_metrics": 3,
    "max_visible_table_rows": 5,
    "max_caveats": 2,
    "max_advisor_notes": 1,
    "max_explanatory_paragraphs": 1,
    "max_markdown_lines": 45,
    "no_client_or_advisor_raw_ids": True,
    "no_visible_internal_jargon": True,
}

FORBIDDEN_VISIBLE_TERMS = (
    "artifact",
    "manifest",
    "schema",
    "valuation trace",
    "pricing function registry",
    "scenario basis vector",
    "raw json",
)

ASSET_CLASS_LABELS = {
    "cash": "Cash",
    "commodity": "Commodities",
    "crypto": "Crypto",
    "etf": "Funds / ETFs",
    "fixed_income": "Fixed Income",
    "money_market": "Money Market",
    "option_like": "Option-Like Exposure",
    "private_credit": "Private Credit",
    "private_equity": "Private Equity",
    "private_real_assets": "Private Real Assets",
    "public_equity": "Public Equity",
}

COVERAGE_LABELS = {
    "held_at_mark_with_caveat": "Held At Mark",
    "not_valued": "Not Valued",
    "review_required": "Review Required",
    "valued": "Valued",
    "valued_with_approved_policy": "Approved Policy",
    "valued_with_substitute_input": "Substitute Input",
}


def load_source_context(
    *,
    revaluation_dir: str | Path = DEFAULT_REVALUATION_DIR,
    position_universe_path: str | Path = DEFAULT_POSITION_UNIVERSE_PATH,
) -> dict[str, Any]:
    revaluation_path = Path(revaluation_dir)
    attribution_path = revaluation_path / "attribution"
    universe_path = Path(position_universe_path)

    return {
        "source_paths": _source_paths(revaluation_path, attribution_path, universe_path),
        "scenario_index": _load_json(revaluation_path / "revaluation_scenario_index.json"),
        "base_valuation": _load_json(revaluation_path / "position_valuation_results_base.json"),
        "position_catalog": _load_json(revaluation_path / "position_catalog.json"),
        "position_universe": _load_json(universe_path),
        "portfolio_summaries": {
            scenario_id: _load_json(revaluation_path / f"portfolio_revaluation_summary_{scenario_id}.json")
            for scenario_id in SCENARIO_IDS
        },
        "position_comparisons": {
            scenario_id: _load_json(revaluation_path / f"position_value_comparison_{scenario_id}.json")
            for scenario_id in SCENARIO_IDS
        },
        "manager_attribution": {
            scenario_id: _load_json(
                attribution_path / f"manager_revaluation_attribution_{scenario_id}.json"
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
        "cross_scenario": _load_json(attribution_path / "cross_scenario_revaluation_summary.json"),
    }


def build_lean_report_inputs(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    base_valuation = context["base_valuation"]
    base_value = float(base_valuation["summary"]["total_value"])
    position_count = int(base_valuation["position_count"])
    review_required_count = int(base_valuation["summary"]["review_required_count"])
    portfolio_summaries = context["portfolio_summaries"]
    cross_scenario = context["cross_scenario"]

    worst = _worst_scenario(cross_scenario["scenarios"])
    asset_rows = _asset_allocation_rows(context, base_value)
    manager_rows = _manager_role_rows(context)
    concentration_rows = _concentration_rows(context, asset_rows, manager_rows, base_value)
    downside_rows = _scenario_downside_rows(cross_scenario)
    coverage_rows = _coverage_rows(context["coverage_attribution"]["ai_chip_selloff"], base_value)
    coverage_metrics = _coverage_metrics(portfolio_summaries["ai_chip_selloff"])

    inputs = {
        "portfolio_status": _report_input(
            report_element_id="portfolio_status",
            display_title="Portfolio Status",
            master_question_family="Ownership / Exposure Explanation",
            audience_tier="client_briefing",
            one_sentence_job=(
                "Give the client a small status anchor before moving into concentration or downside."
            ),
            source_analytics=[
                context["source_paths"]["base_valuation"],
                context["source_paths"]["cross_scenario"],
            ],
            visible_fields={
                "headline_sentence": (
                    f"The portfolio starts at {_format_money(base_value)} across {position_count} positions; "
                    f"{_scenario_label(worst['scenario_id'])} is the largest current downside at "
                    f"{_format_money(worst['impact'])} ({_format_percent(worst['impact_percent'])})."
                ),
                "headline_metrics": [
                    _metric("Base value", base_value, _format_money(base_value)),
                    _metric("Positions", position_count, _format_count(position_count)),
                    _metric(
                        "Largest downside",
                        worst["impact"],
                        f"{_format_money(worst['impact'])} ({_format_percent(worst['impact_percent'])})",
                    ),
                ],
                "table": None,
                "caveats": [
                    "Synthetic demo data; review-required positions should not support point-impact claims."
                ],
                "advisor_note": None,
                "explanatory_paragraph": None,
            },
            suppressed_fields=[
                "position-level valuation rows",
                "pricing model details",
                "source file names",
                "raw internal identifiers",
            ],
            internal_only_fields=[
                "source_analytics",
                "portfolio summary reconciliation",
                "position coverage detail",
            ],
        ),
        "aggregated_asset_allocation": _report_input(
            report_element_id="aggregated_asset_allocation",
            display_title="Aggregated Asset Allocation",
            master_question_family="Ownership / Exposure Explanation",
            audience_tier="client_briefing",
            one_sentence_job="Show the broad allocation mix without long position lists.",
            source_analytics=[
                context["source_paths"]["base_valuation"],
                context["source_paths"]["position_universe"],
            ],
            visible_fields={
                "headline_sentence": (
                    f"{asset_rows[0]['allocation']} is the largest allocation at "
                    f"{asset_rows[0]['value']} ({asset_rows[0]['portfolio_share']})."
                ),
                "headline_metrics": [
                    _metric("Largest allocation", asset_rows[0]["allocation"], asset_rows[0]["allocation"]),
                    _metric("Largest allocation value", asset_rows[0]["value_raw"], asset_rows[0]["value"]),
                    _metric("Rows shown", len(asset_rows), _format_count(len(asset_rows))),
                ],
                "table": _table(
                    "Allocation Mix",
                    ["Allocation", "Value", "Portfolio Share"],
                    asset_rows,
                    ["allocation", "value", "portfolio_share"],
                ),
                "caveats": ["Small allocation buckets are grouped into Other when needed."],
                "advisor_note": None,
                "explanatory_paragraph": None,
            },
            suppressed_fields=[
                "individual position rows",
                "raw asset-class codes",
                "instrument-level reference data",
            ],
            internal_only_fields=[
                "source_analytics",
                "position-to-classification join fields",
            ],
        ),
        "manager_role_summary": _report_input(
            report_element_id="manager_role_summary",
            display_title="Manager Role Summary",
            master_question_family="Ownership / Exposure Explanation",
            audience_tier="advisor_review",
            one_sentence_job="Show each material manager role and its larger current downside contribution.",
            source_analytics=[
                context["source_paths"]["manager_attribution_ai_chip_selloff"],
                context["source_paths"]["manager_attribution_rate_shock"],
                context["source_paths"]["position_universe"],
            ],
            visible_fields={
                "headline_sentence": (
                    f"{manager_rows[0]['manager']} is the largest manager sleeve at "
                    f"{manager_rows[0]['portfolio_share']} of base value."
                ),
                "headline_metrics": [
                    _metric("Largest manager", manager_rows[0]["manager"], manager_rows[0]["manager"]),
                    _metric(
                        "Largest manager share",
                        manager_rows[0]["portfolio_share_raw"],
                        manager_rows[0]["portfolio_share"],
                    ),
                    _metric(
                        "Larger downside for largest manager",
                        manager_rows[0]["larger_downside_raw"],
                        manager_rows[0]["larger_downside"],
                    ),
                ],
                "table": _table(
                    "Manager Roles",
                    ["Manager", "Role", "Portfolio Share", "Larger Downside"],
                    manager_rows,
                    ["manager", "role", "portfolio_share", "larger_downside"],
                ),
                "caveats": ["The table shows the five largest managers by base value."],
                "advisor_note": "Use the larger downside column as a conversation guide, not a recommendation.",
                "explanatory_paragraph": None,
            },
            suppressed_fields=[
                "manager ids",
                "account ids",
                "top impacted positions",
                "scenario construction detail",
            ],
            advisor_only_fields=["advisor_note"],
            internal_only_fields=["source_analytics", "manager reconciliation fields"],
        ),
        "concentration_review": _report_input(
            report_element_id="concentration_review",
            display_title="Concentration Review",
            master_question_family="Risk / Downside Explanation",
            audience_tier="advisor_review",
            one_sentence_job="Identify the few concentration points worth discussing before showing scenario detail.",
            source_analytics=[
                context["source_paths"]["base_valuation"],
                context["source_paths"]["coverage_attribution_ai_chip_selloff"],
                context["source_paths"]["manager_attribution_ai_chip_selloff"],
                context["source_paths"]["position_universe"],
            ],
            visible_fields={
                "headline_sentence": (
                    f"The main concentration is {concentration_rows[0]['area']} at "
                    f"{concentration_rows[0]['portfolio_share']} of base value."
                ),
                "headline_metrics": [
                    _metric(
                        "Largest concentration",
                        concentration_rows[0]["area"],
                        concentration_rows[0]["area"],
                    ),
                    _metric(
                        "Largest concentration share",
                        concentration_rows[0]["portfolio_share_raw"],
                        concentration_rows[0]["portfolio_share"],
                    ),
                    _metric("Review-required exposure", coverage_metrics["review_value"], coverage_metrics["review_value_text"]),
                ],
                "table": _table(
                    "Watch List",
                    ["Area", "Portfolio Share", "What To Watch"],
                    concentration_rows,
                    ["area", "portfolio_share", "what_to_watch"],
                ),
                "caveats": [
                    "Concentration rows are intentionally grouped; individual holdings stay hidden by default."
                ],
                "advisor_note": "Open a position-level review only if that report shape is explicitly approved later.",
                "explanatory_paragraph": None,
            },
            suppressed_fields=[
                "top position names",
                "position identifiers",
                "full manager attribution tables",
                "full coverage bucket detail",
            ],
            advisor_only_fields=["advisor_note"],
            internal_only_fields=["source_analytics", "coverage and manager source joins"],
        ),
        "scenario_downside_summary": _report_input(
            report_element_id="scenario_downside_summary",
            display_title="Scenario Downside Summary",
            master_question_family="Risk / Downside Explanation",
            audience_tier="client_briefing",
            one_sentence_job="Compare the current supported downside scenarios without a long attribution report.",
            source_analytics=[context["source_paths"]["cross_scenario"]],
            visible_fields={
                "headline_sentence": (
                    f"{_scenario_label(worst['scenario_id'])} is the larger downside case, reducing the "
                    f"portfolio value by {_format_money(abs(worst['impact']))} ({_format_percent(worst['impact_percent'])})."
                ),
                "headline_metrics": [
                    _metric("Worst case shown", _scenario_label(worst["scenario_id"]), _scenario_label(worst["scenario_id"])),
                    _metric("Worst impact", worst["impact"], _format_money(worst["impact"])),
                    _metric("Worst change", worst["impact_percent"], _format_percent(worst["impact_percent"])),
                ],
                "table": _table(
                    "Scenario Results",
                    ["Scenario", "Portfolio Impact", "Portfolio Change", "Value After Scenario"],
                    downside_rows,
                    ["scenario", "portfolio_impact", "portfolio_change", "value_after_scenario"],
                ),
                "caveats": [
                    "Scenarios are deterministic stress views, not forecasts.",
                    "Only the two currently supported scenarios are shown.",
                ],
                "advisor_note": None,
                "explanatory_paragraph": None,
            },
            suppressed_fields=[
                "position-level impacts",
                "scenario market-state construction",
                "raw scenario ids",
            ],
            internal_only_fields=["source_analytics", "cross-scenario source references"],
        ),
        "coverage_confidence_warning": _report_input(
            report_element_id="coverage_confidence_warning",
            display_title="Coverage and Confidence Warning",
            master_question_family="Risk / Downside Explanation",
            audience_tier="advisor_review",
            one_sentence_job="Warn the advisor where the current scenario output should not be overread.",
            source_analytics=[
                context["source_paths"]["coverage_attribution_ai_chip_selloff"],
                context["source_paths"]["confidence_attribution_ai_chip_selloff"],
            ],
            visible_fields={
                "headline_sentence": (
                    f"Most positions are valued, but {coverage_metrics['review_count']} positions representing "
                    f"{coverage_metrics['review_value_text']} require review before relying on point scenario impact."
                ),
                "headline_metrics": [
                    _metric("Review-required positions", coverage_metrics["review_count"], _format_count(coverage_metrics["review_count"])),
                    _metric("Held at mark", coverage_metrics["held_at_mark_count"], _format_count(coverage_metrics["held_at_mark_count"])),
                    _metric("Not valued", coverage_metrics["not_valued_count"], _format_count(coverage_metrics["not_valued_count"])),
                ],
                "table": _table(
                    "Coverage Summary",
                    ["Coverage", "Positions", "Base Value", "Advisor Meaning"],
                    coverage_rows,
                    ["coverage", "positions", "base_value", "advisor_meaning"],
                ),
                "caveats": [
                    "Review-required exposure should not be used for strong point-impact claims.",
                    "Held-at-mark exposure may understate true stress exposure.",
                ],
                "advisor_note": "Resolve the review-required bucket before turning this into client-ready language.",
                "explanatory_paragraph": None,
            },
            suppressed_fields=[
                "position-level review list",
                "model ids",
                "raw coverage codes",
                "internal valuation detail",
            ],
            advisor_only_fields=["advisor_note"],
            internal_only_fields=["source_analytics", "coverage bucket reconciliation"],
        ),
        "cash_flow_support_readiness": _report_input(
            report_element_id="cash_flow_support_readiness",
            display_title="Cash-Flow Support Readiness",
            master_question_family="Performance / Plan Explanation",
            audience_tier="advisor_review",
            one_sentence_job=(
                "State why cash-flow support should not be generated until the cash need and timing are explicit."
            ),
            source_analytics=[],
            visible_fields={
                "headline_sentence": (
                    "Cash-flow support is not ready for a client report because no explicit cash need or "
                    "liability schedule is present."
                ),
                "headline_metrics": [
                    _metric("Cash need supplied", False, "No"),
                    _metric("Liability schedule supplied", False, "No"),
                    _metric("Report status", "Readiness-only", "Readiness-only"),
                ],
                "table": None,
                "caveats": ["Do not infer spending support from cash balances or income labels alone."],
                "advisor_note": (
                    "Collect the specific cash need, timing, and approved funding sources before producing this report."
                ),
                "explanatory_paragraph": None,
            },
            suppressed_fields=[
                "cash-generation forecast",
                "plan funding claim",
                "liability matching result",
                "performance claim",
            ],
            advisor_only_fields=["advisor_note"],
            internal_only_fields=["source_gap", "readiness policy"],
            status="gated_readiness_only",
            source_gap={
                "reason": "No explicit cash-flow question, cash need, liability schedule, or approved funding source is present.",
                "fake_inputs_blocked": True,
            },
        ),
    }

    _validate_report_ids(inputs)
    return inputs


def build_lean_report_views(inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    views: dict[str, dict[str, Any]] = {}
    for report_id, input_payload in inputs.items():
        visible = input_payload["visible_fields"]
        view = {
            "schema_version": VIEW_SCHEMA_VERSION,
            "generator_version": GENERATOR_VERSION,
            "generated_at": GENERATED_AT,
            "synthetic_data": True,
            "report_element_id": report_id,
            "status": input_payload["status"],
            "display_title": input_payload["display_title"],
            "master_question_family": input_payload["master_question_family"],
            "audience_tier": input_payload["audience_tier"],
            "one_sentence_job": input_payload["one_sentence_job"],
            "headline_sentence": visible["headline_sentence"],
            "headline_metrics": visible["headline_metrics"],
            "table": visible["table"],
            "caveats": visible["caveats"],
            "advisor_note": visible["advisor_note"],
            "explanatory_paragraph": visible["explanatory_paragraph"],
            "internal_source_refs": input_payload["source_analytics"],
            "information_budget_applied": _budget_actuals(visible),
            "visible_fields_rendered_by_mockup": [
                "display_title",
                "headline_sentence",
                "headline_metrics",
                "table",
                "caveats",
                "advisor_note",
                "explanatory_paragraph",
            ],
        }
        _validate_view_budget(view)
        views[report_id] = view
    return views


def render_markdown_mockup(view: dict[str, Any]) -> str:
    lines = [
        f"# {view['display_title']}",
        "",
        view["headline_sentence"],
        "",
        "## Key Metrics",
    ]
    for metric in view["headline_metrics"]:
        lines.append(f"- **{metric['label']}:** {metric['formatted_value']}")

    table = view.get("table")
    if table:
        lines.extend(["", f"## {table['title']}", ""])
        lines.extend(_render_markdown_table(table))

    explanatory_paragraph = view.get("explanatory_paragraph")
    if explanatory_paragraph:
        lines.extend(["", "## Explanation", "", explanatory_paragraph])

    caveats = view.get("caveats") or []
    if caveats:
        lines.extend(["", "## Caveats"])
        for caveat in caveats:
            lines.append(f"- {caveat}")

    advisor_note = view.get("advisor_note")
    if advisor_note:
        lines.extend(["", "## Advisor Note", advisor_note])

    markdown = "\n".join(lines).rstrip() + "\n"
    _validate_markdown_budget(view, markdown)
    return markdown


def generate_lean_report_views(
    *,
    revaluation_dir: str | Path = DEFAULT_REVALUATION_DIR,
    position_universe_path: str | Path = DEFAULT_POSITION_UNIVERSE_PATH,
    input_dir: str | Path = DEFAULT_INPUT_DIR,
    view_dir: str | Path = DEFAULT_VIEW_DIR,
    mockup_dir: str | Path = DEFAULT_MOCKUP_DIR,
) -> dict[str, Any]:
    context = load_source_context(
        revaluation_dir=revaluation_dir,
        position_universe_path=position_universe_path,
    )
    inputs = build_lean_report_inputs(context)
    views = build_lean_report_views(inputs)

    input_path = Path(input_dir)
    view_path = Path(view_dir)
    mockup_path = Path(mockup_dir)
    input_path.mkdir(parents=True, exist_ok=True)
    view_path.mkdir(parents=True, exist_ok=True)
    mockup_path.mkdir(parents=True, exist_ok=True)

    input_files = []
    for report_id, payload in inputs.items():
        filename = f"{report_id}_input.json"
        _write_json(input_path / filename, payload)
        input_files.append(filename)

    view_files = []
    mockup_files = []
    for report_id, view in views.items():
        view_filename = f"{report_id}_view.json"
        mockup_filename = f"{report_id}_mockup.md"
        _write_json(view_path / view_filename, view)
        (mockup_path / mockup_filename).write_text(render_markdown_mockup(view), encoding="utf-8")
        view_files.append(view_filename)
        mockup_files.append(mockup_filename)

    input_summary = _input_summary(input_files, inputs)
    view_summary = _view_summary(view_files, mockup_files, views)
    _write_json(input_path / "lean_revaluation_report_input_summary.json", input_summary)
    _write_json(view_path / "lean_revaluation_report_view_summary.json", view_summary)
    (mockup_path / "README.md").write_text(_render_mockup_index(views), encoding="utf-8")

    return {
        "status": "generated",
        "report_count": len(views),
        "mockup_count": len(mockup_files),
        "input_dir": _as_posix(input_path),
        "view_dir": _as_posix(view_path),
        "mockup_dir": _as_posix(mockup_path),
        "input_files": input_files + ["lean_revaluation_report_input_summary.json"],
        "view_files": view_files + ["lean_revaluation_report_view_summary.json"],
        "mockup_files": mockup_files + ["README.md"],
        "gated_reports": [
            report_id for report_id, payload in inputs.items() if payload["status"] == "gated_readiness_only"
        ],
        "deferred_reports": list(DEFERRED_REPORT_IDS),
    }


def _report_input(
    *,
    report_element_id: str,
    display_title: str,
    master_question_family: str,
    audience_tier: str,
    one_sentence_job: str,
    source_analytics: list[str],
    visible_fields: dict[str, Any],
    suppressed_fields: list[str],
    internal_only_fields: list[str],
    advisor_only_fields: list[str] | None = None,
    status: str = "generated",
    source_gap: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schema_version": INPUT_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "report_element_id": report_element_id,
        "status": status,
        "display_title": display_title,
        "master_question_family": master_question_family,
        "audience_tier": audience_tier,
        "one_sentence_job": one_sentence_job,
        "source_analytics": source_analytics,
        "visible_fields": visible_fields,
        "suppressed_fields": suppressed_fields,
        "advisor_only_fields": advisor_only_fields or [],
        "internal_only_fields": internal_only_fields,
        "information_budget": dict(INFORMATION_BUDGET),
        "caveat_policy": {
            "max_visible_caveats": INFORMATION_BUDGET["max_caveats"],
            "no_duplicate_caveats": True,
            "coverage_limits_must_be_explicit_when_material": True,
        },
    }
    if source_gap is not None:
        payload["source_gap"] = source_gap
    return payload


def _input_summary(input_files: list[str], inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": INPUT_SUMMARY_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "report_count": len(inputs),
        "report_ids": list(inputs),
        "output_files": input_files,
        "gated_reports": [
            report_id for report_id, payload in inputs.items() if payload["status"] == "gated_readiness_only"
        ],
        "deferred_reports": list(DEFERRED_REPORT_IDS),
        "information_budget": dict(INFORMATION_BUDGET),
    }


def _view_summary(
    view_files: list[str],
    mockup_files: list[str],
    views: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": VIEW_SUMMARY_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "report_count": len(views),
        "view_count": len(view_files),
        "mockup_count": len(mockup_files),
        "report_ids": list(views),
        "view_files": view_files,
        "mockup_files": mockup_files,
        "mockups_generated_from_views": True,
        "gated_reports": [
            report_id for report_id, view in views.items() if view["status"] == "gated_readiness_only"
        ],
        "deferred_reports": list(DEFERRED_REPORT_IDS),
        "information_budget": dict(INFORMATION_BUDGET),
    }


def _asset_allocation_rows(context: dict[str, Any], base_value: float) -> list[dict[str, Any]]:
    position_by_id = {
        row["position_id"]: row for row in context["position_universe"]["positions"]
    }
    grouped: dict[str, dict[str, float]] = defaultdict(lambda: {"value": 0.0, "count": 0})
    for row in context["base_valuation"]["position_results"]:
        position = position_by_id[row["position_id"]]
        asset_class = position.get("classifications", {}).get("asset_class") or position.get("instrument_type")
        grouped[asset_class]["value"] += float(row["value"])
        grouped[asset_class]["count"] += 1

    rows = [
        {
            "allocation": ASSET_CLASS_LABELS.get(asset_class, _title_from_id(asset_class)),
            "value_raw": round(values["value"], 2),
            "value": _format_money(values["value"]),
            "portfolio_share_raw": _safe_divide(values["value"], base_value),
            "portfolio_share": _format_percent(_safe_divide(values["value"], base_value)),
            "position_count": int(values["count"]),
        }
        for asset_class, values in grouped.items()
        if values["value"]
    ]
    rows.sort(key=lambda item: item["value_raw"], reverse=True)

    if len(rows) > INFORMATION_BUDGET["max_visible_table_rows"]:
        visible = rows[: INFORMATION_BUDGET["max_visible_table_rows"] - 1]
        other_rows = rows[INFORMATION_BUDGET["max_visible_table_rows"] - 1 :]
        other_value = sum(row["value_raw"] for row in other_rows)
        other_count = sum(row["position_count"] for row in other_rows)
        visible.append(
            {
                "allocation": "Other",
                "value_raw": round(other_value, 2),
                "value": _format_money(other_value),
                "portfolio_share_raw": _safe_divide(other_value, base_value),
                "portfolio_share": _format_percent(_safe_divide(other_value, base_value)),
                "position_count": other_count,
            }
        )
        rows = visible
    return rows


def _manager_role_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    managers = {row["manager_id"]: row for row in context["position_universe"]["managers"]}
    ai_rows = context["manager_attribution"]["ai_chip_selloff"]["rows"]
    rate_rows_by_id = {
        row["group_id"]: row for row in context["manager_attribution"]["rate_shock"]["rows"]
    }
    rows = []
    for row in ai_rows:
        manager = managers[row["group_id"]]
        rate_row = rate_rows_by_id[row["group_id"]]
        larger_downside = min(float(row["impact"]), float(rate_row["impact"]))
        rows.append(
            {
                "manager": _strip_manager_prefix(row["display_name"]),
                "role": manager["mandate"],
                "portfolio_share_raw": float(row["percent_of_portfolio_base"]),
                "portfolio_share": _format_percent(row["percent_of_portfolio_base"]),
                "larger_downside_raw": round(larger_downside, 2),
                "larger_downside": _format_money(larger_downside),
                "base_value_raw": float(row["base_value"]),
            }
        )
    rows.sort(key=lambda item: item["base_value_raw"], reverse=True)
    return rows[: INFORMATION_BUDGET["max_visible_table_rows"]]


def _concentration_rows(
    context: dict[str, Any],
    asset_rows: list[dict[str, Any]],
    manager_rows: list[dict[str, Any]],
    base_value: float,
) -> list[dict[str, Any]]:
    coverage_by_status = context["portfolio_summaries"]["ai_chip_selloff"]["coverage_summary"]["by_status"]
    held_at_mark = coverage_by_status["held_at_mark_with_caveat"]
    review_required = coverage_by_status["review_required"]

    top_manager = manager_rows[0]
    top_asset = asset_rows[0]
    rows = [
        {
            "area": top_manager["manager"],
            "portfolio_share_raw": top_manager["portfolio_share_raw"],
            "portfolio_share": top_manager["portfolio_share"],
            "what_to_watch": "Largest manager sleeve and largest scenario loss contributor.",
        },
        {
            "area": top_asset["allocation"],
            "portfolio_share_raw": top_asset["portfolio_share_raw"],
            "portfolio_share": top_asset["portfolio_share"],
            "what_to_watch": "Largest broad allocation before manager or position detail.",
        },
        {
            "area": "Review-required exposure",
            "portfolio_share_raw": _safe_divide(review_required["base_value"], base_value),
            "portfolio_share": _format_percent(_safe_divide(review_required["base_value"], base_value)),
            "what_to_watch": "Needs review before relying on point scenario impact.",
        },
        {
            "area": "Held-at-mark exposure",
            "portfolio_share_raw": _safe_divide(held_at_mark["base_value"], base_value),
            "portfolio_share": _format_percent(_safe_divide(held_at_mark["base_value"], base_value)),
            "what_to_watch": "May understate stress exposure for private or opaque holdings.",
        },
    ]
    rows.sort(key=lambda item: item["portfolio_share_raw"], reverse=True)
    return rows


def _scenario_downside_rows(cross_scenario: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in sorted(cross_scenario["scenarios"], key=lambda item: float(item["impact"])):
        rows.append(
            {
                "scenario": _scenario_label(row["scenario_id"]),
                "portfolio_impact_raw": round(float(row["impact"]), 2),
                "portfolio_impact": _format_money(row["impact"]),
                "portfolio_change_raw": float(row["impact_percent"]),
                "portfolio_change": _format_percent(row["impact_percent"]),
                "value_after_scenario_raw": round(float(row["scenario_portfolio_value"]), 2),
                "value_after_scenario": _format_money(row["scenario_portfolio_value"]),
            }
        )
    return rows


def _coverage_rows(coverage_payload: dict[str, Any], base_value: float) -> list[dict[str, Any]]:
    meanings = {
        "valued": "Directly usable for current scenario summaries.",
        "review_required": "Do not rely on point impact until reviewed.",
        "held_at_mark_with_caveat": "May understate true stress exposure.",
        "valued_with_approved_policy": "Usable with policy caveat.",
        "valued_with_substitute_input": "Use directionally.",
        "not_valued": "Unresolved for point-impact claims.",
    }
    rows = []
    for row in coverage_payload["rows"]:
        rows.append(
            {
                "coverage": COVERAGE_LABELS.get(row["bucket_id"], _title_from_id(row["bucket_id"])),
                "positions_raw": int(row["position_count"]),
                "positions": _format_count(row["position_count"]),
                "base_value_raw": round(float(row["base_value"]), 2),
                "base_value": _format_money(row["base_value"]),
                "portfolio_share_raw": _safe_divide(row["base_value"], base_value),
                "advisor_meaning": meanings.get(row["bucket_id"], "Use with advisor review."),
            }
        )
    rows.sort(key=lambda item: item["base_value_raw"], reverse=True)
    return rows[: INFORMATION_BUDGET["max_visible_table_rows"]]


def _coverage_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    by_status = summary["coverage_summary"]["by_status"]
    review_required = by_status["review_required"]
    held_at_mark = by_status["held_at_mark_with_caveat"]
    not_valued = by_status["not_valued"]
    return {
        "review_count": int(review_required["count"]),
        "review_value": float(review_required["base_value"]),
        "review_value_text": _format_money(review_required["base_value"]),
        "held_at_mark_count": int(held_at_mark["count"]),
        "held_at_mark_value": float(held_at_mark["base_value"]),
        "not_valued_count": int(not_valued["count"]),
        "not_valued_value": float(not_valued["base_value"]),
    }


def _table(
    title: str,
    columns: list[str],
    source_rows: list[dict[str, Any]],
    keys: list[str],
) -> dict[str, Any]:
    rows = []
    for source_row in source_rows[: INFORMATION_BUDGET["max_visible_table_rows"]]:
        rows.append({column: str(source_row[key]) for column, key in zip(columns, keys)})
    return {
        "title": title,
        "columns": columns,
        "rows": rows,
    }


def _metric(label: str, value: Any, formatted_value: str) -> dict[str, Any]:
    return {
        "label": label,
        "value": value,
        "formatted_value": formatted_value,
    }


def _budget_actuals(visible: dict[str, Any]) -> dict[str, Any]:
    table = visible.get("table")
    advisor_note = visible.get("advisor_note")
    explanatory_paragraph = visible.get("explanatory_paragraph")
    return {
        **dict(INFORMATION_BUDGET),
        "actual_headline_sentences": _sentence_count(visible["headline_sentence"]),
        "actual_headline_metrics": len(visible["headline_metrics"]),
        "actual_visible_table_rows": len(table["rows"]) if table else 0,
        "actual_caveats": len(visible["caveats"]),
        "actual_advisor_notes": 1 if advisor_note else 0,
        "actual_explanatory_paragraphs": 1 if explanatory_paragraph else 0,
    }


def _validate_report_ids(inputs: dict[str, dict[str, Any]]) -> None:
    missing = set(BUILD_NOW_REPORT_IDS) - set(inputs)
    unexpected = set(inputs) - set(BUILD_NOW_REPORT_IDS)
    if missing or unexpected:
        raise ValueError(f"Unexpected report id set. missing={sorted(missing)} unexpected={sorted(unexpected)}")


def _validate_view_budget(view: dict[str, Any]) -> None:
    budget = INFORMATION_BUDGET
    if _sentence_count(view["headline_sentence"]) > budget["max_headline_sentences"]:
        raise ValueError(f"{view['report_element_id']} exceeds headline sentence budget")
    if len(view["headline_metrics"]) > budget["max_headline_metrics"]:
        raise ValueError(f"{view['report_element_id']} exceeds metric budget")
    table = view.get("table")
    if table and len(table["rows"]) > budget["max_visible_table_rows"]:
        raise ValueError(f"{view['report_element_id']} exceeds table row budget")
    if len(view.get("caveats") or []) > budget["max_caveats"]:
        raise ValueError(f"{view['report_element_id']} exceeds caveat budget")
    if view.get("advisor_note") and budget["max_advisor_notes"] < 1:
        raise ValueError(f"{view['report_element_id']} exceeds advisor note budget")

    visible_text = _visible_text(view).lower()
    for term in FORBIDDEN_VISIBLE_TERMS:
        if term in visible_text:
            raise ValueError(f"{view['report_element_id']} leaks visible internal term: {term}")


def _validate_markdown_budget(view: dict[str, Any], markdown: str) -> None:
    max_lines = int(INFORMATION_BUDGET["max_markdown_lines"])
    line_count = len([line for line in markdown.splitlines() if line.strip()])
    if line_count > max_lines:
        raise ValueError(f"{view['report_element_id']} markdown exceeds line budget")
    lowered = markdown.lower()
    for term in FORBIDDEN_VISIBLE_TERMS:
        if term in lowered:
            raise ValueError(f"{view['report_element_id']} markdown leaks visible internal term: {term}")


def _visible_text(view: dict[str, Any]) -> str:
    parts = [
        view["display_title"],
        view["headline_sentence"],
    ]
    parts.extend(f"{metric['label']} {metric['formatted_value']}" for metric in view["headline_metrics"])
    table = view.get("table")
    if table:
        parts.append(table["title"])
        parts.extend(table["columns"])
        for row in table["rows"]:
            parts.extend(str(value) for value in row.values())
    parts.extend(view.get("caveats") or [])
    if view.get("advisor_note"):
        parts.append(view["advisor_note"])
    if view.get("explanatory_paragraph"):
        parts.append(view["explanatory_paragraph"])
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


def _render_mockup_index(views: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# Lean Revaluation Report Mockups",
        "",
        "Generated from lean report views for product review.",
        "",
    ]
    for view in views.values():
        lines.append(f"- {view['display_title']}")
    lines.append("")
    return "\n".join(lines)


def _worst_scenario(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return min(rows, key=lambda item: float(item["impact"]))


def _scenario_label(scenario_id: str) -> str:
    return SCENARIO_LABELS.get(scenario_id, _title_from_id(scenario_id))


def _strip_manager_prefix(display_name: str) -> str:
    if " - " in display_name:
        return display_name.split(" - ", 1)[1]
    return display_name


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


def _title_from_id(value: Any) -> str:
    return str(value).replace("_", " ").title()


def _sentence_count(value: str) -> int:
    normalized = value.replace("?", ".").replace("!", ".")
    matches = re.findall(r"[.!?](?:\s|$)", normalized)
    return max(1, len(matches)) if normalized.strip() else 0


def _safe_divide(numerator: Any, denominator: Any) -> float:
    denominator_float = float(denominator)
    if denominator_float == 0:
        return 0.0
    return round(float(numerator) / denominator_float, 6)


def _source_paths(revaluation_dir: Path, attribution_dir: Path, universe_path: Path) -> dict[str, str]:
    return {
        "base_valuation": _as_posix(revaluation_dir / "position_valuation_results_base.json"),
        "position_universe": _as_posix(universe_path),
        "cross_scenario": _as_posix(attribution_dir / "cross_scenario_revaluation_summary.json"),
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
    }


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate lean revaluation-derived report views and mockups.")
    parser.add_argument("--revaluation-dir", default=str(DEFAULT_REVALUATION_DIR))
    parser.add_argument("--position-universe-path", default=str(DEFAULT_POSITION_UNIVERSE_PATH))
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument("--mockup-dir", default=str(DEFAULT_MOCKUP_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_lean_report_views(
        revaluation_dir=args.revaluation_dir,
        position_universe_path=args.position_universe_path,
        input_dir=args.input_dir,
        view_dir=args.view_dir,
        mockup_dir=args.mockup_dir,
    )

    print(f"Lean report inputs: {summary['report_count']} -> {summary['input_dir']}")
    print(f"Lean report views: {summary['report_count']} -> {summary['view_dir']}")
    print(f"Markdown mockups: {summary['mockup_count']} -> {summary['mockup_dir']}")
    print("Gated reports: " + (", ".join(summary["gated_reports"]) or "none"))
    print("Deferred reports: " + ", ".join(summary["deferred_reports"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
