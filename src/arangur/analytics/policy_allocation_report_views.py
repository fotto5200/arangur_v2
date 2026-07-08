from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-08T00:00:00Z"

INPUT_SCHEMA_VERSION = "policy_allocation_report_input.v1"
INPUT_INDEX_SCHEMA_VERSION = "policy_allocation_report_input_index.v1"
VIEW_SCHEMA_VERSION = "policy_allocation_report_view.v1"
VIEW_INDEX_SCHEMA_VERSION = "policy_allocation_report_view_index.v1"
GATED_INDEX_SCHEMA_VERSION = "policy_allocation_report_gated_deferred_index.v1"
GENERATOR_VERSION = "policy_allocation_report_views.v1"

DEFAULT_POLICY_PACK_DIR = Path(
    "data/simulation/policy_mandate_prerequisites/synthetic_policy_mandate_pack_v1"
)
DEFAULT_INPUT_DIR = Path("data/simulation/report_element_inputs/policy_allocation_v1")
DEFAULT_VIEW_DIR = Path("data/simulation/report_element_views/policy_allocation_v1")
DEFAULT_MOCKUP_DIR = Path("docs/product/report_mockups/policy_allocation_v1")

POLICY_PACK_FILES = {
    "manifest": "synthetic_policy_mandate_pack_manifest.json",
    "policy_allocation_mode": "policy_allocation_mode.json",
    "policy_allocation_profile": "policy_allocation_profile.json",
    "actual_manager_allocation_snapshot": "actual_manager_allocation_snapshot.json",
    "allocation_drift_summary": "allocation_drift_summary.json",
    "imputed_current_allocation_baseline": "imputed_current_allocation_baseline.json",
    "manager_mandate_benchmark_catalog": "manager_mandate_benchmark_catalog.json",
    "manager_benchmark_basis_map": "manager_benchmark_basis_map.json",
    "policy_mandate_readiness_summary": "policy_mandate_readiness_summary.json",
}

REPORT_SPECS: tuple[dict[str, str], ...] = (
    {
        "report_id": "policy_allocation_review",
        "input_filename": "policy_allocation_review_input.json",
        "view_filename": "policy_allocation_review_view.json",
        "mockup_filename": "policy_allocation_review_mockup_v1.md",
    },
    {
        "report_id": "policy_allocation_drift_summary",
        "input_filename": "policy_allocation_drift_summary_input.json",
        "view_filename": "policy_allocation_drift_summary_view.json",
        "mockup_filename": "policy_allocation_drift_summary_mockup_v1.md",
    },
    {
        "report_id": "imputed_current_allocation_baseline",
        "input_filename": "imputed_current_allocation_baseline_input.json",
        "view_filename": "imputed_current_allocation_baseline_view.json",
        "mockup_filename": "imputed_current_allocation_baseline_mockup_v1.md",
    },
    {
        "report_id": "manager_mandate_benchmark_basis",
        "input_filename": "manager_mandate_benchmark_basis_input.json",
        "view_filename": "manager_mandate_benchmark_basis_view.json",
        "mockup_filename": "manager_mandate_benchmark_basis_mockup_v1.md",
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
        "report_id": "policy_level_attribution",
        "display_title": "Policy-Level Attribution",
        "status": "Gated",
        "reason": "Needs a policy-level calculated engine before showing allocation effects.",
    },
    {
        "report_id": "blended_all_in_attribution",
        "display_title": "Blended / All-In Attribution",
        "status": "Deferred",
        "reason": "Deferred until separate policy allocation and manager mandate reports are understood first.",
    },
    {
        "report_id": "production_policy_allocation_report",
        "display_title": "Production Policy Allocation Report",
        "status": "Gated",
        "reason": "Gated on real target allocations, approved mandates, and client-ready approval.",
    },
    {
        "report_id": "current_vs_proposed_policy_allocation",
        "display_title": "Current-vs-Proposed Policy Allocation",
        "status": "Gated",
        "reason": "Gated on a proposed allocation workflow and current/proposed comparison outputs.",
    },
    {
        "report_id": "timing_attribution",
        "display_title": "Timing Attribution",
        "status": "Unavailable",
        "reason": "Unavailable because clean timing inputs and an approved method are absent.",
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
    "raw json",
    "debug",
    "performance attribution",
    "blame",
    "fault",
    "bad allocation",
    "wrong allocation",
    "manager failed",
    "advisor failed",
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
    readiness = policy_pack["policy_mandate_readiness_summary"]
    profile = policy_pack["policy_allocation_profile"]
    drift = policy_pack["allocation_drift_summary"]

    if manifest["pack_id"] != "synthetic_policy_mandate_pack_v1":
        raise ValueError("Unexpected policy mandate pack id")
    if not manifest["synthetic_data"] or not manifest["local_only"]:
        raise ValueError("Policy allocation report mockups require local synthetic inputs")
    if profile["allocation_mode"] != "explicit_policy_allocation":
        raise ValueError("Policy Allocation Review requires explicit policy allocation mode")
    if readiness["policy_level_attribution_input_readiness"] != "input_scaffold_ready_engine_needed":
        raise ValueError("Policy-Level Attribution must remain engine-gated")
    if drift["drift_basis"] != "actual_current_weight_minus_target_policy_weight":
        raise ValueError("Unexpected allocation drift basis")

    return {
        "policy_pack_dir": _as_posix(root),
        "policy_pack": policy_pack,
        "source_paths": {
            name: _as_posix(root / filename)
            for name, filename in POLICY_PACK_FILES.items()
        },
    }


def build_policy_allocation_report_inputs(
    context: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    inputs = {
        "policy_allocation_review": _policy_allocation_review_input(context),
        "policy_allocation_drift_summary": _policy_allocation_drift_summary_input(context),
        "imputed_current_allocation_baseline": _imputed_current_baseline_input(context),
        "manager_mandate_benchmark_basis": _manager_mandate_benchmark_basis_input(context),
    }
    _validate_report_ids(inputs)
    return inputs


def build_policy_allocation_report_views(
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
            "period_start": payload["period_start"],
            "period_end": payload["period_end"],
            "valuation_date": payload["valuation_date"],
            "headline_sentence": visible["headline_sentence"],
            "headline_metrics": visible["headline_metrics"],
            "compact_table": visible.get("compact_table"),
            "caveats": visible.get("caveats", []),
            "advisor_note": visible.get("advisor_note"),
            "policy_allocation_mode": payload["policy_allocation_mode"],
            "baseline_type": payload["baseline_type"],
            "responsibility_layer": payload["responsibility_layer"],
            "benchmark_basis_status": payload["benchmark_basis_status"],
            "policy_level_attribution_status": payload["policy_level_attribution_status"],
            "equal_weight_theme_policy": payload["equal_weight_theme_policy"],
            "diagnostic_equal_weight_not_policy": payload[
                "diagnostic_equal_weight_not_policy"
            ],
            "source_policy_mandate_pack_id": payload["source_policy_mandate_pack_id"],
            "source_policy_pack_artifacts": payload["source_policy_pack_artifacts"],
            "internal_source_refs": payload["internal_source_refs"],
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


def generate_policy_allocation_report_views(
    *,
    policy_pack_dir: str | Path = DEFAULT_POLICY_PACK_DIR,
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

    context = load_source_context(policy_pack_dir=policy_pack_dir)
    inputs = build_policy_allocation_report_inputs(context)
    views = build_policy_allocation_report_views(inputs)

    input_files: list[str] = []
    for report_id in BUILD_NOW_REPORT_IDS:
        filename = INPUT_FILENAME_BY_REPORT_ID[report_id]
        _write_json(input_path / filename, inputs[report_id])
        input_files.append(filename)

    input_index = _input_index(input_files, inputs)
    _write_json(input_path / "policy_allocation_report_input_index.json", input_index)
    input_files.append("policy_allocation_report_input_index.json")

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
    _write_json(view_path / "gated_deferred_policy_report_index.json", gated_index)
    view_files.append("gated_deferred_policy_report_index.json")

    readme = render_mockup_readme(views, gated_index)
    (mockup_path / "README.md").write_text(readme, encoding="utf-8")
    mockup_files.append("README.md")

    view_index = _view_index(view_files, mockup_files, views, gated_index)
    _write_json(view_path / "policy_allocation_report_view_index.json", view_index)
    view_files.append("policy_allocation_report_view_index.json")

    return {
        "schema_version": "policy_allocation_report_generation_summary.v1",
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack_id": context["policy_pack"]["manifest"]["pack_id"],
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
        "# Policy Allocation v1 Report Mockups",
        "",
        (
            "These local product-review mockups are generated from Policy Allocation v1 "
            "view data backed by the synthetic policy/mandate prerequisite pack."
        ),
        (
            "They are not wired into Advisor Preview, Populate, Present, generated reports, "
            "Docker, deployment, live data, external data, or production reporting."
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


def _policy_allocation_review_input(context: dict[str, Any]) -> dict[str, Any]:
    pack = context["policy_pack"]
    manifest = pack["manifest"]
    drift = pack["allocation_drift_summary"]
    largest = _largest_abs_drift_row(drift["manager_rows"])
    rows = [
        {
            "Manager/Sleeve": row["display_name"],
            "Target Weight": _format_percent(row["target_weight"]),
            "Actual Weight": _format_percent(row["actual_weight"]),
            "Drift": _format_signed_percent(row["drift"]),
            "Tolerance": _format_percent(row["tolerance"]),
            "Status": _status_label(row["drift_status"]),
        }
        for row in drift["manager_rows"]
    ]

    visible_content = {
        "headline_sentence": (
            "Current manager allocation is mostly inside tolerance, with Manager C below target and needing review."
        ),
        "headline_metrics": [
            _metric("Within tolerance", drift["managers_within_tolerance"], "5 of 6"),
            _metric("Needs review", drift["managers_outside_tolerance"], "1"),
            _metric(
                "Largest drift",
                largest["drift"],
                f"{largest['display_name']} {_format_signed_percent(largest['drift'])}",
            ),
        ],
        "compact_table": _table(
            "Target Versus Actual Manager/Sleeve Allocation",
            ["Manager/Sleeve", "Target Weight", "Actual Weight", "Drift", "Tolerance", "Status"],
            rows,
        ),
        "caveats": [
            "Drift needs review before interpretation; performance, flows, marks, or implementation timing may explain differences."
        ],
        "advisor_note": (
            "Use this as an allocation review before any policy-level effect discussion."
        ),
    }
    return _report_input(
        report_element_id="policy_allocation_review",
        display_title="Policy Allocation Review",
        report_family="policy_allocation_review",
        master_question_family="Performance / Plan",
        exact_report_question="Did the current portfolio follow the advisor/family target allocation?",
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="manager_sleeve_policy_allocation",
        denominator_category_system="share_of_total_portfolio_by_manager_sleeve",
        rendering_mode="summary_first_compact_table",
        context=context,
        visible_content=visible_content,
        policy_allocation_mode="explicit_policy_allocation",
        baseline_type="explicit_policy_target_vs_current_actual",
        responsibility_layer="advisor_family_policy_allocation",
        benchmark_basis_status="manager_mandate_basis_available_for_future_reports",
        policy_level_attribution_status="engine_gated",
        source_artifact_keys=(
            "manifest",
            "policy_allocation_profile",
            "actual_manager_allocation_snapshot",
            "allocation_drift_summary",
        ),
        table_validation={
            "manager_rows_shown": len(rows),
            "all_current_managers_covered": True,
            "target_actual_drift_tolerance_status_columns": True,
            "managers_within_tolerance": drift["managers_within_tolerance"],
            "managers_requiring_review": drift["managers_outside_tolerance"],
            "largest_abs_drift_manager": largest["display_name"],
            "largest_abs_drift": largest["drift"],
        },
        period_start=manifest["period_start"],
        period_end=manifest["period_end"],
        valuation_date=drift["actual_snapshot_date"],
    )


def _policy_allocation_drift_summary_input(context: dict[str, Any]) -> dict[str, Any]:
    pack = context["policy_pack"]
    manifest = pack["manifest"]
    drift = pack["allocation_drift_summary"]
    largest = _largest_abs_drift_row(drift["manager_rows"])
    watch_rows = [
        row
        for row in drift["manager_rows"]
        if row["drift_status"] in {"review", "material_drift"}
    ]
    rows = [
        {
            "Manager/Sleeve": row["display_name"],
            "Drift": _format_signed_percent(row["drift"]),
            "Tolerance": _format_percent(row["tolerance"]),
            "Status": _status_label(row["drift_status"]),
            "Review Focus": _review_focus(row),
        }
        for row in watch_rows
    ]

    visible_content = {
        "headline_sentence": (
            "One manager/sleeve is outside tolerance and should be reviewed before policy allocation conclusions."
        ),
        "headline_metrics": [
            _metric("Within tolerance", drift["managers_within_tolerance"], "5 of 6"),
            _metric("Requires review", drift["managers_outside_tolerance"], "1"),
            _metric(
                "Largest drift",
                largest["drift"],
                f"{largest['display_name']} {_format_signed_percent(largest['drift'])}",
            ),
        ],
        "compact_table": _table(
            "Allocation Drift Watch List",
            ["Manager/Sleeve", "Drift", "Tolerance", "Status", "Review Focus"],
            rows,
        ),
        "caveats": [
            "Watch-list rows are prompts for review, not conclusions about cause."
        ],
        "advisor_note": (
            "Start with review rows; within-tolerance managers can stay in the full allocation review."
        ),
    }
    return _report_input(
        report_element_id="policy_allocation_drift_summary",
        display_title="Policy Allocation Drift Summary",
        report_family="policy_allocation_review",
        master_question_family="Performance / Plan",
        exact_report_question="Which allocation drifts require review before explanation?",
        audience_tier="advisor_review",
        summary_detail_status="summary",
        representation_level="manager_sleeve_policy_allocation_watch_list",
        denominator_category_system="share_of_total_portfolio_by_manager_sleeve",
        rendering_mode="summary_first_watch_list",
        context=context,
        visible_content=visible_content,
        policy_allocation_mode="explicit_policy_allocation",
        baseline_type="explicit_policy_target_vs_current_actual",
        responsibility_layer="advisor_family_policy_allocation",
        benchmark_basis_status="manager_mandate_basis_available_for_future_reports",
        policy_level_attribution_status="engine_gated",
        source_artifact_keys=(
            "manifest",
            "policy_allocation_profile",
            "allocation_drift_summary",
        ),
        table_validation={
            "watch_list_only": True,
            "visible_statuses": sorted({row["drift_status"] for row in watch_rows}),
            "material_or_review_rows_shown": len(rows),
            "within_tolerance_rows_suppressed": drift["managers_within_tolerance"],
            "largest_abs_drift_manager": largest["display_name"],
            "largest_abs_drift": largest["drift"],
        },
        period_start=manifest["period_start"],
        period_end=manifest["period_end"],
        valuation_date=drift["actual_snapshot_date"],
    )


def _imputed_current_baseline_input(context: dict[str, Any]) -> dict[str, Any]:
    pack = context["policy_pack"]
    manifest = pack["manifest"]
    baseline = pack["imputed_current_allocation_baseline"]
    visible_content = {
        "headline_sentence": (
            "Imputed-current mode accepts current manager weights as the baseline and suppresses drift attribution."
        ),
        "headline_metrics": [
            _metric("Baseline weights", "current_manager_weights", "Current weights"),
            _metric("Drift status", "suppressed", "Suppressed"),
            _metric("Use case", "quick_start", "Quick start"),
        ],
        "compact_table": _table(
            "Imputed-Current Baseline Use",
            ["Topic", "Meaning"],
            [
                {
                    "Topic": "Mode",
                    "Meaning": "Current manager weights are accepted as the baseline.",
                },
                {
                    "Topic": "What it enables",
                    "Meaning": "Manager and mandate review can start before explicit targets are entered.",
                },
                {
                    "Topic": "What it suppresses",
                    "Meaning": "Target-versus-actual drift attribution is suppressed.",
                },
                {
                    "Topic": "When to use",
                    "Meaning": "Use for quick-start review when documented policy targets are missing.",
                },
                {
                    "Topic": "Limit",
                    "Meaning": "It does not prove the current allocation is ideal.",
                },
            ],
        ),
        "caveats": [
            "Replace this baseline with explicit policy targets when policy documentation is available."
        ],
        "advisor_note": "This is a setup/readiness note, not a standard client report.",
    }
    return _report_input(
        report_element_id="imputed_current_allocation_baseline",
        display_title="Imputed Current Allocation Baseline",
        report_family="policy_allocation_review",
        master_question_family="Performance / Plan",
        exact_report_question="How can review start when explicit target allocations are not documented?",
        audience_tier="advisor_setup_review",
        summary_detail_status="setup_note",
        representation_level="current_manager_sleeve_baseline",
        denominator_category_system="current_nav_share_by_manager_sleeve",
        rendering_mode="setup_note",
        context=context,
        visible_content=visible_content,
        policy_allocation_mode="imputed_current_allocation",
        baseline_type="accepted_current_manager_weights",
        responsibility_layer="actual_manager_sleeve_allocation_baseline",
        benchmark_basis_status="manager_mandate_basis_available_for_future_reports",
        policy_level_attribution_status="drift_suppressed_until_explicit_targets_exist",
        source_artifact_keys=(
            "manifest",
            "imputed_current_allocation_baseline",
            "actual_manager_allocation_snapshot",
        ),
        table_validation={
            "baseline_weight_count": len(baseline["baseline_weights"]),
            "current_weights_accepted_as_baseline": True,
            "policy_allocation_drift_suppressed": True,
            "not_default_client_report": True,
        },
        period_start=manifest["period_start"],
        period_end=manifest["period_end"],
        valuation_date=baseline["baseline_date"],
    )


def _manager_mandate_benchmark_basis_input(context: dict[str, Any]) -> dict[str, Any]:
    pack = context["policy_pack"]
    manifest = pack["manifest"]
    catalog = pack["manager_mandate_benchmark_catalog"]
    rows = [
        {
            "Manager/Sleeve": row["display_name"],
            "Mandate Benchmark": row["mandate_benchmark_display_name"],
            "Basis Type": _basis_type_label(row["benchmark_type"]),
            "Meaning": row["intended_representation"],
        }
        for row in catalog["benchmark_rows"]
    ]
    visible_content = {
        "headline_sentence": (
            "All six current managers have a documented mandate benchmark basis for local review."
        ),
        "headline_metrics": [
            _metric("Managers covered", catalog["manager_count"], "6 of 6"),
            _metric("Basis status", "explicit", "Explicit"),
            _metric("Use", "advisor_review", "Advisor review"),
        ],
        "compact_table": _table(
            "Manager Mandate Benchmark Basis",
            ["Manager/Sleeve", "Mandate Benchmark", "Basis Type", "Meaning"],
            rows,
        ),
        "caveats": [
            "Use these rows to frame mandate review; production benchmark approval is separate."
        ],
        "advisor_note": (
            "Keep this basis separate from policy allocation drift and any later blended report."
        ),
    }
    return _report_input(
        report_element_id="manager_mandate_benchmark_basis",
        display_title="Manager Mandate Benchmark Basis",
        report_family="manager_mandate_benchmark_basis",
        master_question_family="Performance / Plan",
        exact_report_question="What benchmark basis should frame each manager's mandate review?",
        audience_tier="advisor_review",
        summary_detail_status="summary_reference",
        representation_level="manager_sleeve_mandate_benchmark",
        denominator_category_system="one_manager_mandate_benchmark_basis_per_row",
        rendering_mode="compact_reference_table",
        context=context,
        visible_content=visible_content,
        policy_allocation_mode="explicit_policy_allocation",
        baseline_type="manager_mandate_benchmark_basis",
        responsibility_layer="manager_mandate_implementation_basis",
        benchmark_basis_status="all_current_managers_covered",
        policy_level_attribution_status="engine_gated",
        source_artifact_keys=(
            "manifest",
            "manager_mandate_benchmark_catalog",
            "manager_benchmark_basis_map",
        ),
        table_validation={
            "manager_rows_shown": len(rows),
            "all_current_managers_covered": catalog["coverage_summary"][
                "all_current_managers_covered"
            ],
            "all_benchmark_basis_types_explicit": catalog["coverage_summary"][
                "all_benchmark_basis_types_explicit"
            ],
        },
        period_start=manifest["period_start"],
        period_end=manifest["period_end"],
        valuation_date=manifest["period_end"],
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
    responsibility_layer: str,
    benchmark_basis_status: str,
    policy_level_attribution_status: str,
    source_artifact_keys: tuple[str, ...],
    table_validation: dict[str, Any],
    period_start: str,
    period_end: str,
    valuation_date: str,
) -> dict[str, Any]:
    pack = context["policy_pack"]
    source_artifacts = [POLICY_PACK_FILES[key] for key in source_artifact_keys]
    source_refs = [context["source_paths"][key] for key in source_artifact_keys]
    return {
        "schema_version": INPUT_SCHEMA_VERSION,
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
        "period_start": period_start,
        "period_end": period_end,
        "valuation_date": valuation_date,
        "visible_content": visible_content,
        "policy_allocation_mode": policy_allocation_mode,
        "baseline_type": baseline_type,
        "responsibility_layer": responsibility_layer,
        "benchmark_basis_status": benchmark_basis_status,
        "policy_level_attribution_status": policy_level_attribution_status,
        "equal_weight_theme_policy": pack["policy_allocation_profile"][
            "equal_weight_theme_policy"
        ],
        "diagnostic_equal_weight_not_policy": True,
        "source_policy_mandate_pack_id": pack["manifest"]["pack_id"],
        "source_policy_pack_artifacts": source_artifacts,
        "internal_source_refs": source_refs,
        "source_policy_pack_refs": [pack["manifest"]["pack_id"]],
        "table_validation": table_validation,
        "information_budget": _budget_for_report(report_element_id),
        "gated_or_deferred": False,
        "not_wired_into_advisor_ui": True,
        "not_wired_into_generated_report_flow": True,
    }


def _input_index(
    input_files: list[str],
    inputs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    first = next(iter(inputs.values()))
    return {
        "schema_version": INPUT_INDEX_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack_id": first["source_policy_mandate_pack_id"],
        "report_input_count": len(inputs),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "input_files": input_files,
        "mockups_generated_from_views": True,
        "manager_mandate_benchmark_basis_status": "generated",
        "policy_level_attribution_status": "engine_gated",
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
        "schema_version": VIEW_INDEX_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "local_only": True,
        "source_policy_mandate_pack_id": first["source_policy_mandate_pack_id"],
        "report_view_count": len(views),
        "markdown_mockup_count": len(MOCKUP_FILENAME_BY_REPORT_ID),
        "report_ids": list(BUILD_NOW_REPORT_IDS),
        "view_files": view_files,
        "mockup_files": mockup_files,
        "mockups_generated_from_views": True,
        "manager_mandate_benchmark_basis_status": "generated",
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
        "source_policy_mandate_pack_id": "synthetic_policy_mandate_pack_v1",
        "purpose": "Product/readiness index for policy reports deliberately not generated.",
        "gated_or_deferred_reports": list(GATED_REPORTS),
    }


def _budget_for_report(report_id: str) -> dict[str, Any]:
    budget = dict(DEFAULT_INFORMATION_BUDGET)
    if report_id == "policy_allocation_review":
        budget["max_visible_table_rows"] = 6
        budget["exception_reason"] = "Policy Allocation Review shows all six current manager/sleeve rows."
    elif report_id == "policy_allocation_drift_summary":
        budget["max_visible_table_rows"] = 3
    elif report_id == "imputed_current_allocation_baseline":
        budget["max_visible_table_rows"] = 5
    elif report_id == "manager_mandate_benchmark_basis":
        budget["max_visible_table_rows"] = 6
        budget["exception_reason"] = "Manager Mandate Benchmark Basis shows all six current manager/sleeve rows."
    return budget


def _budget_actuals(
    *,
    report_id: str,
    visible: dict[str, Any],
    rendering_mode: str,
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
            f"Unexpected policy allocation report id set. missing={sorted(missing)} unexpected={sorted(unexpected)}"
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
    table = view.get("compact_table")
    if table:
        parts.append(table["title"])
        parts.extend(table["columns"])
        for row in table["rows"]:
            parts.extend(str(row[column]) for column in table["columns"])
    parts.extend(view.get("caveats") or [])
    if view.get("advisor_note"):
        parts.append(view["advisor_note"])
    return "\n".join(parts)


def _largest_abs_drift_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(rows, key=lambda row: abs(float(row["drift"])))


def _review_focus(row: dict[str, Any]) -> str:
    if row["drift"] < 0:
        return "Below target; review flows, timing, and policy intent."
    return "Above target; review appreciation, marks, and policy intent."


def _status_label(status: str) -> str:
    return {
        "within_tolerance": "Within tolerance",
        "review": "Review",
        "material_drift": "Material drift",
        "imputed_baseline_no_drift": "No drift in baseline",
    }.get(status, status.replace("_", " ").title())


def _basis_type_label(status: str) -> str:
    return {
        "hybrid_synthetic_demo": "Hybrid synthetic demo",
        "mandate_benchmark": "Mandate benchmark",
        "theme_benchmark_blend": "Theme benchmark blend",
        "policy_benchmark": "Policy benchmark",
    }.get(status, status.replace("_", " ").title())


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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate synthetic policy allocation report fixtures and mockups."
    )
    parser.add_argument("--policy-pack-dir", default=str(DEFAULT_POLICY_PACK_DIR))
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--view-dir", default=str(DEFAULT_VIEW_DIR))
    parser.add_argument("--mockup-dir", default=str(DEFAULT_MOCKUP_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = generate_policy_allocation_report_views(
        policy_pack_dir=args.policy_pack_dir,
        input_dir=args.input_dir,
        view_dir=args.view_dir,
        mockup_dir=args.mockup_dir,
    )

    print(
        f"Policy allocation report inputs: {summary['report_input_count']} -> {summary['input_dir']}"
    )
    print(
        f"Policy allocation report views: {summary['report_view_count']} -> {summary['view_dir']}"
    )
    print(
        "Policy allocation Markdown mockups: "
        f"{summary['markdown_mockup_count']} -> {summary['mockup_dir']}"
    )
    print("Source policy pack: " + summary["source_policy_mandate_pack_id"])
    print("Generated report ids: " + ", ".join(summary["report_ids"]))
    print("Gated reports not generated: " + ", ".join(summary["gated_reports_not_generated"]))
    print("Output paths: " + summary["input_dir"] + "; " + summary["view_dir"] + "; " + summary["mockup_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
