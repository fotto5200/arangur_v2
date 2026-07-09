from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00Z"
CATALOG_ID = "demo_report_workflows_v1"
CATALOG_VERSION = "2026-07-09"
EXTERNAL_PACK_ID = "external_manager_story_translation_pack_v1"
EXTERNAL_PACK_VERSION = "2026-07-09"

DEFAULT_WORKFLOW_DIR = Path("data/simulation/report_workflows/demo_workflows_v1")
DEFAULT_EXTERNAL_PACK_DIR = Path(
    "data/simulation/external_story_translation"
) / EXTERNAL_PACK_ID
DEFAULT_DOCS_DIR = Path("docs/product")

WORKFLOW_FILENAMES = {
    "principal_family_office_briefing_minimal_v1": (
        "principal_family_office_briefing_minimal_v1.json"
    ),
    "engaged_client_investment_committee_review_v1": (
        "engaged_client_investment_committee_review_v1.json"
    ),
    "advisor_manager_oversight_v1": "advisor_manager_oversight_v1.json",
    "external_manager_story_translation_v1": (
        "external_manager_story_translation_v1.json"
    ),
}

REPORT_SOURCE_DIRECTORIES = {
    "revaluation_v2_mockups": "docs/product/report_mockups/revaluation_v2",
    "revaluation_v2_views": "data/simulation/report_element_views/revaluation_v2",
    "policy_allocation_v1_mockups": "docs/product/report_mockups/policy_allocation_v1",
    "policy_allocation_v1_views": "data/simulation/report_element_views/policy_allocation_v1",
    "policy_attribution_v2_mockups": "docs/product/report_mockups/policy_attribution_v2",
    "policy_attribution_v2_views": "data/simulation/report_element_views/policy_attribution_v2",
    "manager_attribution_v1_mockups": "docs/product/report_mockups/manager_attribution_v1",
    "manager_attribution_v1_views": "data/simulation/report_element_views/manager_attribution_v1",
    "attribution_v1_mockups": "docs/product/report_mockups/attribution_v1",
    "attribution_v1_views": "data/simulation/report_element_views/attribution_v1",
}

REPORT_REFS: dict[str, dict[str, str]] = {
    "portfolio_representation_status": {
        "display_title": "Portfolio Representation Status",
        "report_family": "portfolio_representation_status",
        "mockup": "docs/product/report_mockups/revaluation_v2/portfolio_representation_status_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/portfolio_representation_status_view.json",
    },
    "aggregated_asset_allocation": {
        "display_title": "Aggregated Asset Allocation",
        "report_family": "aggregated_asset_allocation",
        "mockup": "docs/product/report_mockups/revaluation_v2/aggregated_asset_allocation_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/aggregated_asset_allocation_view.json",
    },
    "allocation_by_manager": {
        "display_title": "Allocation by Manager",
        "report_family": "allocation_by_manager",
        "mockup": "docs/product/report_mockups/revaluation_v2/allocation_by_manager_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/allocation_by_manager_view.json",
    },
    "cash_flow_delivered": {
        "display_title": "Cash Flow Delivered",
        "report_family": "cash_flow_delivered",
        "mockup": "docs/product/report_mockups/revaluation_v2/cash_flow_delivered_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/cash_flow_delivered_view.json",
    },
    "cash_flow_support_outlook": {
        "display_title": "Cash-Flow Support Outlook",
        "report_family": "cash_flow_support_outlook",
        "mockup": "docs/product/report_mockups/revaluation_v2/cash_flow_support_outlook_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/cash_flow_support_outlook_view.json",
    },
    "coverage_confidence_warning": {
        "display_title": "Coverage and Confidence Warning",
        "report_family": "coverage_confidence_warning",
        "mockup": "docs/product/report_mockups/revaluation_v2/coverage_confidence_warning_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/coverage_confidence_warning_view.json",
    },
    "current_portfolio_scenario_downside": {
        "display_title": "Current Portfolio Scenario Downside",
        "report_family": "current_portfolio_scenario_downside",
        "mockup": "docs/product/report_mockups/revaluation_v2/current_portfolio_scenario_downside_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/current_portfolio_scenario_downside_view.json",
    },
    "full_lens_exposure_ai_adoption": {
        "display_title": "Full Lens Exposure - AI Adoption",
        "report_family": "full_lens_exposure",
        "mockup": "docs/product/report_mockups/revaluation_v2/full_lens_exposure_ai_adoption_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/full_lens_exposure_ai_adoption_view.json",
    },
    "full_lens_exposure_energy_security": {
        "display_title": "Full Lens Exposure - Energy Security",
        "report_family": "full_lens_exposure",
        "mockup": "docs/product/report_mockups/revaluation_v2/full_lens_exposure_energy_security_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/full_lens_exposure_energy_security_view.json",
    },
    "manager_by_lens_exposure_ai_adoption": {
        "display_title": "Manager by Lens Exposure - AI Adoption",
        "report_family": "manager_by_lens_exposure",
        "mockup": "docs/product/report_mockups/revaluation_v2/manager_by_lens_exposure_ai_adoption_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/manager_by_lens_exposure_ai_adoption_view.json",
    },
    "manager_by_lens_exposure_energy_security": {
        "display_title": "Manager by Lens Exposure - Energy Security",
        "report_family": "manager_by_lens_exposure",
        "mockup": "docs/product/report_mockups/revaluation_v2/manager_by_lens_exposure_energy_security_mockup_v2.md",
        "view": "data/simulation/report_element_views/revaluation_v2/manager_by_lens_exposure_energy_security_view.json",
    },
    "policy_allocation_review": {
        "display_title": "Policy Allocation Review",
        "report_family": "policy_allocation_review",
        "mockup": "docs/product/report_mockups/policy_allocation_v1/policy_allocation_review_mockup_v1.md",
        "view": "data/simulation/report_element_views/policy_allocation_v1/policy_allocation_review_view.json",
    },
    "policy_allocation_drift_summary": {
        "display_title": "Policy Allocation Drift Summary",
        "report_family": "policy_allocation_drift_summary",
        "mockup": "docs/product/report_mockups/policy_allocation_v1/policy_allocation_drift_summary_mockup_v1.md",
        "view": "data/simulation/report_element_views/policy_allocation_v1/policy_allocation_drift_summary_view.json",
    },
    "imputed_current_allocation_baseline": {
        "display_title": "Imputed Current Allocation Baseline",
        "report_family": "imputed_current_allocation_baseline",
        "mockup": "docs/product/report_mockups/policy_allocation_v1/imputed_current_allocation_baseline_mockup_v1.md",
        "view": "data/simulation/report_element_views/policy_allocation_v1/imputed_current_allocation_baseline_view.json",
    },
    "manager_mandate_benchmark_basis": {
        "display_title": "Manager Mandate Benchmark Basis",
        "report_family": "manager_mandate_benchmark_basis",
        "mockup": "docs/product/report_mockups/policy_allocation_v1/manager_mandate_benchmark_basis_mockup_v1.md",
        "view": "data/simulation/report_element_views/policy_allocation_v1/manager_mandate_benchmark_basis_view.json",
    },
    "advisor_policy_attribution_by_manager": {
        "display_title": "Advisor Policy Attribution by Manager/Sleeve",
        "report_family": "advisor_policy_attribution",
        "mockup": "docs/product/report_mockups/policy_attribution_v2/advisor_policy_attribution_by_manager_mockup_v2.md",
        "view": "data/simulation/report_element_views/policy_attribution_v2/advisor_policy_attribution_by_manager_view.json",
    },
    "advisor_policy_effect_totals": {
        "display_title": "Advisor Policy Effect Totals",
        "report_family": "advisor_policy_attribution",
        "mockup": "docs/product/report_mockups/policy_attribution_v2/advisor_policy_effect_totals_mockup_v2.md",
        "view": "data/simulation/report_element_views/policy_attribution_v2/advisor_policy_effect_totals_view.json",
    },
    "manager_mandate_attribution_summary": {
        "display_title": "Manager Mandate Attribution Summary",
        "report_family": "manager_mandate_attribution",
        "mockup": "docs/product/report_mockups/manager_attribution_v1/manager_mandate_attribution_summary_mockup_v1.md",
        "view": "data/simulation/report_element_views/manager_attribution_v1/manager_mandate_attribution_summary_view.json",
    },
    "manager_driver_attribution_matrix": {
        "display_title": "Manager Driver Attribution Matrix",
        "report_family": "manager_mandate_attribution",
        "mockup": "docs/product/report_mockups/manager_attribution_v1/manager_driver_attribution_matrix_mockup_v1.md",
        "view": "data/simulation/report_element_views/manager_attribution_v1/manager_driver_attribution_matrix_view.json",
    },
    "within_manager_attribution_detail": {
        "display_title": "Within-Manager Attribution Detail",
        "report_family": "manager_mandate_attribution",
        "mockup": "docs/product/report_mockups/manager_attribution_v1/within_manager_attribution_detail_mockup_v1.md",
        "view": "data/simulation/report_element_views/manager_attribution_v1/within_manager_attribution_detail_view.json",
    },
    "manager_implementation_handoff": {
        "display_title": "Manager Implementation Handoff",
        "report_family": "manager_mandate_attribution",
        "mockup": "docs/product/report_mockups/manager_attribution_v1/manager_implementation_handoff_mockup_v1.md",
        "view": "data/simulation/report_element_views/manager_attribution_v1/manager_implementation_handoff_view.json",
    },
    "integrated_performance_attribution_summary": {
        "display_title": "Integrated Performance Attribution Summary",
        "report_family": "integrated_performance_attribution",
        "mockup": "docs/product/report_mockups/attribution_v1/integrated_performance_attribution_summary_mockup_v1.md",
        "view": "data/simulation/report_element_views/attribution_v1/integrated_performance_attribution_summary_view.json",
    },
    "integrated_performance_attribution_detail": {
        "display_title": "Integrated Performance Attribution Detail",
        "report_family": "integrated_performance_attribution",
        "mockup": "docs/product/report_mockups/attribution_v1/integrated_performance_attribution_detail_mockup_v1.md",
        "view": "data/simulation/report_element_views/attribution_v1/integrated_performance_attribution_detail_view.json",
    },
    "lens_based_performance_attribution_ai_adoption": {
        "display_title": "Lens-Based Performance Attribution - AI Adoption",
        "report_family": "performance_attribution_by_lens",
        "mockup": "docs/product/report_mockups/attribution_v1/lens_based_performance_attribution_ai_adoption_mockup_v1.md",
        "view": "data/simulation/report_element_views/attribution_v1/lens_based_performance_attribution_ai_adoption_view.json",
    },
    "manager_attribution_summary": {
        "display_title": "Manager Attribution Summary",
        "report_family": "manager_attribution_summary",
        "mockup": "docs/product/report_mockups/attribution_v1/manager_attribution_summary_mockup_v1.md",
        "view": "data/simulation/report_element_views/attribution_v1/manager_attribution_summary_view.json",
    },
}

SUPERSEDED_REPORT_IDS = {
    "policy_level_attribution_summary_v1",
    "policy_level_manager_effect_detail_v1",
}


def generate_report_workflow_catalog(
    *,
    workflow_dir: str | Path = DEFAULT_WORKFLOW_DIR,
    external_pack_dir: str | Path = DEFAULT_EXTERNAL_PACK_DIR,
    docs_dir: str | Path = DEFAULT_DOCS_DIR,
) -> dict[str, Any]:
    workflow_path = Path(workflow_dir)
    external_path = Path(external_pack_dir)
    docs_path = Path(docs_dir)
    workflow_path.mkdir(parents=True, exist_ok=True)
    external_path.mkdir(parents=True, exist_ok=True)
    docs_path.mkdir(parents=True, exist_ok=True)

    external_pack = _external_story_pack(external_path)
    for filename, payload in external_pack.items():
        _write_json(external_path / filename, payload)

    workflows = _workflow_payloads(external_path)
    for workflow_id, payload in workflows.items():
        _write_json(workflow_path / WORKFLOW_FILENAMES[workflow_id], payload)

    manifest = _manifest(workflows, workflow_path, external_path)
    _write_json(workflow_path / "report_workflow_catalog_manifest.json", manifest)

    docs = _product_docs(workflows, external_pack)
    for filename, markdown in docs.items():
        (docs_path / filename).write_text(markdown, encoding="utf-8")

    validation = validate_catalog(
        workflow_dir=workflow_path,
        external_pack_dir=external_path,
        docs_dir=docs_path,
    )
    return {
        "schema_version": "report_workflow_catalog_generation_summary.v1",
        "catalog_id": CATALOG_ID,
        "catalog_version": CATALOG_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "workflow_count": len(workflows),
        "primary_workflow_ids": list(workflows),
        "available_report_reference_count": validation["available_report_reference_count"],
        "gated_reference_count": validation["gated_reference_count"],
        "external_story_pack_status": external_pack[
            "external_story_translation_manifest.json"
        ]["approval_status"],
        "workflow_dir": _as_posix(workflow_path),
        "external_story_pack_dir": _as_posix(external_path),
        "docs_dir": _as_posix(docs_path),
        "validation_status": validation["status"],
    }


def validate_catalog(
    *,
    workflow_dir: str | Path = DEFAULT_WORKFLOW_DIR,
    external_pack_dir: str | Path = DEFAULT_EXTERNAL_PACK_DIR,
    docs_dir: str | Path = DEFAULT_DOCS_DIR,
) -> dict[str, Any]:
    workflow_path = Path(workflow_dir)
    external_path = Path(external_pack_dir)
    docs_path = Path(docs_dir)
    workflows = {
        workflow_id: _load_json(workflow_path / filename)
        for workflow_id, filename in WORKFLOW_FILENAMES.items()
    }
    manifest = _load_json(workflow_path / "report_workflow_catalog_manifest.json")
    if manifest["workflow_count"] != 4:
        raise ValueError("Workflow manifest must declare exactly four workflows")
    if set(workflows) != set(WORKFLOW_FILENAMES):
        raise ValueError("Workflow ids do not match required workflow set")

    available_refs = 0
    gated_refs = 0
    for workflow_id, workflow in workflows.items():
        _validate_workflow_shape(workflow_id, workflow)
        for step in workflow["ordered_steps"]:
            status = step["status"]
            if step["step_role"] == "primary" and status == "superseded":
                raise ValueError(f"{workflow_id} uses superseded primary step")
            if step["report_id"] in SUPERSEDED_REPORT_IDS and step["step_role"] == "primary":
                raise ValueError(f"{workflow_id} uses superseded report as primary")
            if status in {"accepted", "accepted_with_minor_polish", "available"}:
                available_refs += 1
                if "source_mockup_path" in step:
                    _require_path(step["source_mockup_path"])
                if "source_view_path" in step:
                    _require_path(step["source_view_path"])
            if status in {"gated", "deferred"}:
                gated_refs += 1
                if step.get("source_mockup_path") or step.get("source_view_path"):
                    raise ValueError(f"{workflow_id} gated step should not claim generated paths")

    external_manifest = _load_json(external_path / "external_story_translation_manifest.json")
    if not external_manifest["translate_do_not_endorse"]:
        raise ValueError("External story pack must translate, not endorse")
    if not external_manifest["not_verified"]:
        raise ValueError("External story pack must be marked not verified")
    if not external_manifest["not_recommendation"]:
        raise ValueError("External story pack must be marked not recommendation")
    proxies = _load_json(external_path / "candidate_benchmark_proxy_map.json")
    for row in proxies["candidate_proxy_rows"]:
        if not row["requires_approval"] or not row["not_recommendation"]:
            raise ValueError("Candidate proxy rows must require approval and avoid recommendations")
        if not row["synthetic_candidate_only"]:
            raise ValueError("Candidate proxy rows must stay synthetic candidate only")

    for filename in (
        "report_workflow_catalog_v1.md",
        "demo_report_suite_v1.md",
        "report_family_acceptance_status_v1.md",
        "external_manager_story_workflow_v1.md",
    ):
        _require_path(docs_path / filename)

    return {
        "schema_version": "report_workflow_catalog_validation_summary.v1",
        "status": "pass",
        "workflow_count": len(workflows),
        "primary_workflow_ids": list(workflows),
        "available_report_reference_count": available_refs,
        "gated_reference_count": gated_refs,
        "external_story_pack_status": external_manifest["approval_status"],
    }


def _workflow_payloads(external_pack_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        "principal_family_office_briefing_minimal_v1": _workflow(
            workflow_id="principal_family_office_briefing_minimal_v1",
            display_name="Principal / Family Office Briefing",
            audience="Principal / family office member",
            audience_depth="minimal_client_briefing",
            core_user_question="What do I need to know without reading every analytic report?",
            conversation_goal=(
                "Answer where we are, whether cash/spending is covered, what the biggest risks are, "
                "what to watch next, and what the advisor is planning to do."
            ),
            ordered_steps=[
                _step(1, "portfolio_representation_status", "primary", "client_facing", "accepted", "Starts with portfolio scale and completeness.", "Where are we?"),
                _step(2, "cash_flow_delivered", "primary", "client_facing", "accepted", "Shows recent cash generated and paid out before discussing projections.", "What cash did the portfolio deliver?"),
                _step(3, "cash_flow_support_outlook", "primary", "client_facing", "accepted", "Separates stated cash need support from trailing cash delivery.", "Is cash/spending covered?"),
                _step(4, "coverage_confidence_warning", "supporting", "advisor_review", "accepted_with_minor_polish", "Warns when data confidence changes interpretation.", "Can we trust the numbers enough to show them?"),
                _step(5, "aggregated_asset_allocation", "supporting", "client_facing", "accepted", "Keeps broad ownership legible without manager detail.", "What does the portfolio own broadly?"),
                _step(6, "current_portfolio_scenario_downside", "supporting", "client_facing", "accepted", "Shows the few biggest current downside cases.", "What are the biggest portfolio risks?"),
                _gated_step(7, "high_level_advisor_plan_next_year_positioning", "High-Level Advisor Plan / Next-Year Positioning", "positioning_forward_view", "handoff", "client_facing", "gated", "No generated plan mockup exists yet; future UI/demo wiring should collect advisor plan language."),
            ],
            supporting_reports=["aggregated_asset_allocation", "current_portfolio_scenario_downside"],
            setup_or_readiness_notes=["coverage_confidence_warning"],
            diagnostic_reports=[],
            superseded_reports_excluded=list(SUPERSEDED_REPORT_IDS),
            gated_or_deferred_reports=["high_level_advisor_plan_next_year_positioning"],
            client_facing_status="client_facing_minimal",
            advisor_only_status="advisor_uses_setup_notes_before_showing",
            why_this_workflow_exists="Some principals want the smallest useful conversation, not the full analytic library.",
            what_this_workflow_proves="Arangur can order accepted reports into a concise principal briefing and leave dense attribution out unless needed.",
        ),
        "engaged_client_investment_committee_review_v1": _workflow(
            workflow_id="engaged_client_investment_committee_review_v1",
            display_name="Engaged Client / Investment Committee Review",
            audience="Engaged client, family investment committee, or sophisticated principal",
            audience_depth="sophisticated_client_or_committee",
            core_user_question="How did policy, managers, exposures, themes, and scenarios explain the portfolio?",
            conversation_goal="Explain performance, exposures, themes, and risk without turning the meeting into advisor internal diligence.",
            ordered_steps=[
                _step(1, "portfolio_representation_status", "setup_readiness", "client_facing", "accepted", "Anchors the committee in portfolio representation before deeper review.", "What portfolio view are we using?"),
                _step(2, "policy_allocation_review", "primary", "client_facing", "accepted", "Shows whether actual allocation lines up with the policy frame.", "Did the portfolio follow the policy allocation?"),
                _step(3, "advisor_policy_attribution_by_manager", "primary", "advisor_review", "accepted", "Explains advisor-level policy effects before manager implementation.", "Which advisor policy decisions drove return?"),
                _step(4, "manager_mandate_attribution_summary", "primary", "advisor_review", "accepted", "Shows whether managers added value versus their own mandates.", "How did managers do versus mandate benchmarks?"),
                _step(5, "full_lens_exposure_ai_adoption", "primary", "client_facing", "accepted", "Shows the portfolio through the AI Adoption lens.", "How exposed is the portfolio to AI Adoption?"),
                _step(6, "full_lens_exposure_energy_security", "primary", "client_facing", "accepted", "Shows the portfolio through the Energy Security lens.", "How exposed is the portfolio to Energy Security?"),
                _step(7, "manager_by_lens_exposure_ai_adoption", "supporting", "advisor_review", "accepted", "Adds manager context for the selected lens without becoming a full drilldown.", "Which managers express the AI lens?"),
                _step(8, "current_portfolio_scenario_downside", "primary", "client_facing", "accepted", "Closes with current downside scenarios.", "What could hurt the portfolio now?"),
                _step(9, "manager_driver_attribution_matrix", "supporting", "advisor_review", "accepted_with_minor_polish", "Optional dense manager implementation matrix for committee follow-up.", "Which internal manager drivers explain implementation?"),
            ],
            supporting_reports=["manager_by_lens_exposure_ai_adoption", "manager_driver_attribution_matrix"],
            setup_or_readiness_notes=["portfolio_representation_status"],
            diagnostic_reports=[],
            superseded_reports_excluded=list(SUPERSEDED_REPORT_IDS),
            gated_or_deferred_reports=[],
            client_facing_status="client_facing_when_sophisticated",
            advisor_only_status="manager_driver_matrix_optional_advisor_support",
            why_this_workflow_exists="Investment committees need performance, exposure, and risk in one ordered review without every internal diagnostic.",
            what_this_workflow_proves="Arangur can combine policy attribution, manager mandate attribution, lens exposure, and scenario risk while keeping detail optional.",
        ),
        "advisor_manager_oversight_v1": _workflow(
            workflow_id="advisor_manager_oversight_v1",
            display_name="Advisor / Manager Oversight",
            audience="Advisor/internal investment team",
            audience_depth="advisor_internal_diagnostic",
            core_user_question="Which mandates, managers, implementation effects, and review flags need attention before client conversations?",
            conversation_goal="Monitor mandates, manager performance, implementation quality, drift, and review flags.",
            ordered_steps=[
                _step(1, "policy_allocation_drift_summary", "primary", "advisor_only", "accepted", "Starts with allocation drift needing review.", "Which allocation drifts need attention?"),
                _step(2, "manager_mandate_benchmark_basis", "setup_readiness", "advisor_only", "accepted", "Confirms the benchmark basis for manager review.", "What benchmark frames each manager?"),
                _step(3, "advisor_policy_attribution_by_manager", "primary", "advisor_review", "accepted", "Separates advisor-level policy effects.", "What did advisor-level policy choices do?"),
                _step(4, "manager_mandate_attribution_summary", "primary", "advisor_review", "accepted", "Summarizes manager results versus mandate.", "Which managers added value versus mandate?"),
                _step(5, "manager_driver_attribution_matrix", "primary", "advisor_only", "accepted", "Shows all manager driver components before drilldown.", "Which internal manager drivers explain implementation?"),
                _step(6, "within_manager_attribution_detail", "diagnostic", "advisor_only", "accepted", "Drills into the selected manager from the matrix.", "What explains the selected manager's active return?"),
                _step(7, "manager_implementation_handoff", "handoff", "internal_control", "accepted", "Reconciles manager total to Advisor Policy Attribution handoff.", "Does the layer handoff tie out?"),
                _step(8, "coverage_confidence_warning", "supporting", "advisor_review", "accepted", "Keeps data confidence visible before client use.", "What coverage issues affect interpretation?"),
                _gated_step(9, "coverage_confidence_by_manager", "Coverage/Confidence by Manager", "coverage_confidence_warning", "diagnostic", "advisor_only", "gated", "No generated manager-sliced coverage report exists yet."),
            ],
            supporting_reports=["coverage_confidence_warning"],
            setup_or_readiness_notes=["manager_mandate_benchmark_basis"],
            diagnostic_reports=["manager_driver_attribution_matrix", "within_manager_attribution_detail", "manager_implementation_handoff"],
            superseded_reports_excluded=list(SUPERSEDED_REPORT_IDS),
            gated_or_deferred_reports=["coverage_confidence_by_manager"],
            client_facing_status="not_default_client_facing",
            advisor_only_status="advisor_only_diagnostic_workflow",
            why_this_workflow_exists="Advisors need dense mandate and implementation review before deciding what belongs in a client meeting.",
            what_this_workflow_proves="Arangur can keep advisor oversight separate from client-facing briefing workflows.",
        ),
        "external_manager_story_translation_v1": _external_story_workflow(external_pack_dir),
    }


def _external_story_workflow(external_pack_dir: Path) -> dict[str, Any]:
    return _workflow(
        workflow_id="external_manager_story_translation_v1",
        display_name="External Manager Story Translation",
        audience="Advisor, investment committee, or manager-facing discussion",
        audience_depth="advisor_or_committee_translation",
        core_user_question="How would Arangur translate an outside manager worldview into lenses, scenarios, proxies, and report workflows?",
        conversation_goal="Translate an external investment narrative into Arangur structures without endorsing or verifying it.",
        ordered_steps=[
            _artifact_step(1, "external_manager_story_summary", "Manager Story Summary", "manager_story_summary.json", external_pack_dir, "primary", "advisor_review", "setup_note", "Summarizes the outside worldview in plain English without endorsing it.", "What is the external story saying?"),
            _artifact_step(2, "external_story_implied_lenses", "Implied Lenses", "implied_lenses.json", external_pack_dir, "primary", "advisor_review", "setup_note", "Translates the story into candidate lens questions.", "What lenses does this worldview imply?"),
            _artifact_step(3, "external_story_key_price_scenarios", "Key-Price Scenario Set", "key_price_scenario_set.json", external_pack_dir, "primary", "advisor_review", "setup_note", "Turns the story into synthetic key-price scenario candidates.", "Which scenarios would test this worldview?"),
            _artifact_step(4, "external_story_candidate_proxies", "Candidate Benchmark/Proxy Map", "candidate_benchmark_proxy_map.json", external_pack_dir, "setup_readiness", "internal_control", "setup_note", "Lists candidate proxies that require approval before any use.", "What proxies might be reviewed later?"),
            _gated_step(5, "portfolio_through_external_lens", "Portfolio Through External Lens", "external_story_translation", "primary", "advisor_review", "gated", "No generated portfolio-through-external-lens report exists yet."),
            _gated_step(6, "manager_by_external_lens", "Manager by External Lens", "external_story_translation", "supporting", "advisor_review", "gated", "No generated manager-by-external-lens report exists yet."),
            _gated_step(7, "scenario_downside_under_external_story", "Scenario Downside under External Story", "external_story_translation", "supporting", "advisor_review", "gated", "No generated external-story scenario downside report exists yet."),
            _gated_step(8, "scenario_by_lens_external_story", "Scenario by Lens", "external_story_translation", "supporting", "advisor_review", "gated", "Scenario-by-lens report remains gated until approved lens assignments and scenario aggregation exist."),
            _artifact_step(9, "external_story_governance_caveat_note", "Governance/Caveat Note", "governance_caveats.json", external_pack_dir, "handoff", "advisor_review", "setup_note", "Closes the translation with governance boundaries.", "What does this translation not prove?"),
        ],
        supporting_reports=["portfolio_through_external_lens", "manager_by_external_lens", "scenario_downside_under_external_story", "scenario_by_lens_external_story"],
        setup_or_readiness_notes=[
            "external_manager_story_summary",
            "external_story_implied_lenses",
            "external_story_key_price_scenarios",
            "external_story_candidate_proxies",
            "external_story_governance_caveat_note",
        ],
        diagnostic_reports=[],
        superseded_reports_excluded=list(SUPERSEDED_REPORT_IDS),
        gated_or_deferred_reports=[
            "portfolio_through_external_lens",
            "manager_by_external_lens",
            "scenario_downside_under_external_story",
            "scenario_by_lens_external_story",
        ],
        client_facing_status="not_client_facing_until_reviewed",
        advisor_only_status="advisor_review_translation_workflow",
        why_this_workflow_exists="Outside manager stories often arrive as narrative; Arangur needs to translate them into governed lenses and scenarios.",
        what_this_workflow_proves="Arangur can structure an external worldview without accepting it as true or recommending its proxies.",
    )


def _workflow(
    *,
    workflow_id: str,
    display_name: str,
    audience: str,
    audience_depth: str,
    core_user_question: str,
    conversation_goal: str,
    ordered_steps: list[dict[str, Any]],
    supporting_reports: list[str],
    setup_or_readiness_notes: list[str],
    diagnostic_reports: list[str],
    superseded_reports_excluded: list[str],
    gated_or_deferred_reports: list[str],
    client_facing_status: str,
    advisor_only_status: str,
    why_this_workflow_exists: str,
    what_this_workflow_proves: str,
) -> dict[str, Any]:
    return {
        "schema_version": "report_workflow.v1",
        "workflow_id": workflow_id,
        "display_name": display_name,
        "audience": audience,
        "audience_depth": audience_depth,
        "core_user_question": core_user_question,
        "conversation_goal": conversation_goal,
        "ordered_steps": ordered_steps,
        "supporting_reports": supporting_reports,
        "setup_or_readiness_notes": setup_or_readiness_notes,
        "diagnostic_reports": diagnostic_reports,
        "superseded_reports_excluded": superseded_reports_excluded,
        "gated_or_deferred_reports": gated_or_deferred_reports,
        "client_facing_status": client_facing_status,
        "advisor_only_status": advisor_only_status,
        "why_this_workflow_exists": why_this_workflow_exists,
        "what_this_workflow_proves": what_this_workflow_proves,
        "not_production_recommendation": True,
        "synthetic_data": True,
    }


def _step(
    step_number: int,
    report_id: str,
    step_role: str,
    audience_visibility: str,
    status: str,
    why_included: str,
    visible_question_answered: str,
) -> dict[str, Any]:
    report = REPORT_REFS[report_id]
    return {
        "step_number": step_number,
        "report_id": report_id,
        "display_title": report["display_title"],
        "report_family": report["report_family"],
        "source_mockup_path": report["mockup"],
        "source_view_path": report["view"],
        "step_role": step_role,
        "audience_visibility": audience_visibility,
        "why_included": why_included,
        "visible_question_answered": visible_question_answered,
        "status": status,
        "caveat": "Local synthetic product-review report; not production reporting.",
    }


def _gated_step(
    step_number: int,
    report_id: str,
    display_title: str,
    report_family: str,
    step_role: str,
    audience_visibility: str,
    status: str,
    caveat: str,
) -> dict[str, Any]:
    return {
        "step_number": step_number,
        "report_id": report_id,
        "display_title": display_title,
        "report_family": report_family,
        "step_role": step_role,
        "audience_visibility": audience_visibility,
        "why_included": "Represents the next report needed to complete this conversation.",
        "visible_question_answered": "Unavailable until its data and report shape are approved.",
        "status": status,
        "caveat": caveat,
    }


def _artifact_step(
    step_number: int,
    report_id: str,
    display_title: str,
    filename: str,
    external_pack_dir: Path,
    step_role: str,
    audience_visibility: str,
    status: str,
    why_included: str,
    visible_question_answered: str,
) -> dict[str, Any]:
    return {
        "step_number": step_number,
        "report_id": report_id,
        "display_title": display_title,
        "report_family": "external_story_translation",
        "source_artifact_path": _as_posix(external_pack_dir / filename),
        "step_role": step_role,
        "audience_visibility": audience_visibility,
        "why_included": why_included,
        "visible_question_answered": visible_question_answered,
        "status": status,
        "caveat": "Synthetic translation only; not verified and not a recommendation.",
    }


def _external_story_pack(external_pack_dir: Path) -> dict[str, dict[str, Any]]:
    artifacts = {
        "manager_story_summary.json": _manager_story_summary(),
        "implied_lenses.json": _implied_lenses(),
        "key_price_scenario_set.json": _key_price_scenario_set(),
        "candidate_benchmark_proxy_map.json": _candidate_benchmark_proxy_map(),
        "external_story_report_workflow_map.json": _external_story_report_workflow_map(external_pack_dir),
        "governance_caveats.json": _governance_caveats(),
    }
    artifacts["external_story_translation_manifest.json"] = {
        "schema_version": "external_story_translation_manifest.v1",
        "pack_id": EXTERNAL_PACK_ID,
        "pack_version": EXTERNAL_PACK_VERSION,
        "generated_at": GENERATED_AT,
        "synthetic_data": True,
        "source_basis": "externally_inspired_manager_story_summary",
        "not_verified": True,
        "not_recommendation": True,
        "translate_do_not_endorse": True,
        "generated_artifacts": sorted(
            [*artifacts, "external_story_translation_manifest.json"]
        ),
        "intended_workflow": "external_manager_story_translation_v1",
        "limitations": [
            "Synthetic demo translation only.",
            "External manager views may be incomplete or wrong.",
            "Candidate lenses, scenarios, benchmarks, and proxies require review before any client use.",
            "No live market data, external APIs, or real client data were used.",
        ],
        "approval_status": "synthetic_demo_translation",
    }
    return artifacts


def _manager_story_summary() -> dict[str, Any]:
    return {
        "schema_version": "external_manager_story_summary.v1",
        "story_title": "Synthetic AI Growth and Macro-Risk Manager Worldview",
        "plain_english_summary": (
            "An external manager frames the world as AI-driven growth and capital formation upside "
            "occurring alongside geopolitical, energy, trade, inflation, rate, and duration risks."
        ),
        "core_worldview": [
            "AI infrastructure and capital formation may create growth upside.",
            "Energy supply, trade conflict, inflation, rates, and duration can pressure portfolios.",
            "The same portfolio can be reviewed through growth, bottleneck, macro, and geopolitical lenses.",
        ],
        "what_the_story_emphasizes": [
            "AI-related growth and infrastructure demand.",
            "Energy and oil shock sensitivity.",
            "Higher-for-longer rates and duration exposure.",
            "Trade-war, tariff, geography, and bloc-fragmentation risks.",
        ],
        "what_not_to_copy": [
            "Do not copy position recommendations.",
            "Do not treat candidate proxies as approved benchmarks.",
            "Do not treat the worldview as verified or complete.",
        ],
        "not_verified": True,
        "not_recommendation": True,
    }


def _implied_lenses() -> dict[str, Any]:
    lenses = [
        ("ai_supercycle_exposure", "AI Supercycle Exposure", "Where does the portfolio benefit if AI-driven growth and capital formation accelerate?", ["Direct AI enablers", "AI adopters", "Neutral exposure", "Review required"], ["valuation_sensitivity", "capex_intensity"]),
        ("ai_infrastructure_bottleneck", "AI Infrastructure Bottleneck", "Where could power, chips, data centers, or financing bottlenecks constrain AI upside?", ["Power and grid bottleneck", "Semiconductor supply", "Data-center capacity", "Financing bottleneck", "Neutral exposure"], ["supply_chain_dependency", "energy_intensity"]),
        ("energy_oil_shock_exposure", "Energy / Oil Shock Exposure", "Which holdings are hurt or helped by energy supply shock or oil-price spikes?", ["Energy beneficiaries", "Energy cost sensitive", "Transport/logistics exposed", "Neutral exposure", "Review required"], ["oil_beta", "margin_pressure"]),
        ("inflation_rates_duration_exposure", "Inflation / Rates / Duration Exposure", "Where is the portfolio sensitive to inflation, rates, and duration?", ["Long-duration growth", "Rate-sensitive credit", "Inflation pass-through", "Floating-rate or short-duration", "Neutral exposure"], ["duration_proxy", "spread_sensitivity"]),
        ("trade_war_tariff_exposure", "Trade War / Tariff Exposure", "Where could tariffs, trade restrictions, or supply-chain friction change outcomes?", ["Import-cost exposed", "Reshoring beneficiary", "Export restriction exposed", "Supply-chain diversified", "Neutral exposure"], ["tariff_sensitivity", "china_supply_chain_link"]),
        ("geography_bloc_exposure", "Geography / Bloc Exposure", "How does the portfolio map to geography, strategic blocs, and geopolitical disruption?", ["US-aligned exposure", "China/Asia supply-chain exposure", "Europe exposure", "Commodity-security exposure", "Neutral or unclear"], ["geopolitical_safe_haven_exposure", "sanctions_sensitivity"]),
    ]
    return {
        "schema_version": "external_story_implied_lenses.v1",
        "synthetic_data": True,
        "source_basis": "externally_inspired_manager_story_summary",
        "lenses": [
            {
                "lens_id": lens_id,
                "display_name": display_name,
                "core_question": core_question,
                "suggested_primary_buckets": buckets,
                "secondary_flags": flags,
                "translation_note": "Candidate lens for structuring the story; requires approval before client use.",
                "approval_status": "synthetic_demo_translation",
                "not_recommendation": True,
            }
            for lens_id, display_name, core_question, buckets, flags in lenses
        ],
    }


def _key_price_scenario_set() -> dict[str, Any]:
    scenarios = [
        ("hormuz_reclosure_oil_shock", "Hormuz Reclosure / Oil Shock", "Energy disruption branch of the story", ["oil / energy", "commodities / strategic inputs", "broad equity index", "credit spreads", "volatility / risk appetite"], {"oil / energy": "up", "broad equity index": "down", "credit spreads": "wider", "volatility / risk appetite": "risk appetite down"}),
        ("higher_for_longer_rates", "Higher-for-Longer Rates", "Inflation, rate, and duration branch of the story", ["rates / yield curve", "growth / AI / semiconductor basket", "credit spreads", "private liquidity / alternatives"], {"rates / yield curve": "higher front and intermediate rates", "growth / AI / semiconductor basket": "valuation pressure", "credit spreads": "modestly wider", "private liquidity / alternatives": "liquidity pressure"}),
        ("ai_capex_acceleration", "AI Capex Acceleration", "AI growth upside branch of the story", ["growth / AI / semiconductor basket", "commodities / strategic inputs", "oil / energy", "broad equity index"], {"growth / AI / semiconductor basket": "up", "commodities / strategic inputs": "up", "broad equity index": "up", "rates / yield curve": "possibly higher"}),
        ("ai_bottleneck_valuation_reversal", "AI Bottleneck / Valuation Reversal", "AI bottleneck and valuation-risk branch of the story", ["growth / AI / semiconductor basket", "rates / yield curve", "credit spreads", "volatility / risk appetite"], {"growth / AI / semiconductor basket": "down", "volatility / risk appetite": "risk appetite down", "credit spreads": "wider"}),
        ("trade_war_tariff_escalation", "Trade-War / Tariff Escalation", "Trade and geography branch of the story", ["broad equity index", "USD / FX", "commodities / strategic inputs", "credit spreads", "growth / AI / semiconductor basket"], {"broad equity index": "down", "USD / FX": "stronger USD stress", "commodities / strategic inputs": "mixed/up", "credit spreads": "wider"}),
    ]
    return {
        "schema_version": "external_story_key_price_scenario_set.v1",
        "synthetic_data": True,
        "source_basis": "externally_inspired_manager_story_summary",
        "scenarios": [
            {
                "scenario_id": scenario_id,
                "display_name": display_name,
                "story_link": story_link,
                "key_price_drivers": drivers,
                "expected_directional_moves": moves,
                "reports_that_would_use_it": [
                    "Scenario Downside under External Story",
                    "Scenario by Lens",
                    "Portfolio Through External Lens",
                ],
                "not_forecast": True,
                "not_recommendation": True,
            }
            for scenario_id, display_name, story_link, drivers, moves in scenarios
        ],
    }


def _candidate_benchmark_proxy_map() -> dict[str, Any]:
    rows = [
        ("ai_supercycle_exposure", "direct_ai_enablers", "growth / AI / semiconductor basket", "Candidate synthetic AI enabler basket"),
        ("ai_infrastructure_bottleneck", "power_and_grid_bottleneck", "commodities / strategic inputs", "Candidate power/grid bottleneck basket"),
        ("energy_oil_shock_exposure", "energy_beneficiaries", "oil / energy", "Candidate energy equity or commodity proxy"),
        ("inflation_rates_duration_exposure", "long_duration_growth", "rates / yield curve", "Candidate duration/rate sensitivity proxy"),
        ("trade_war_tariff_exposure", "import_cost_exposed", "USD / FX", "Candidate tariff and currency pressure proxy"),
        ("geography_bloc_exposure", "china_asia_supply_chain_exposure", "broad equity index", "Candidate geography or supply-chain proxy"),
    ]
    return {
        "schema_version": "external_story_candidate_benchmark_proxy_map.v1",
        "synthetic_data": True,
        "candidate_proxy_rows": [
            {
                "lens_id": lens_id,
                "bucket_id": bucket_id,
                "driver_category": driver_category,
                "candidate_proxy_description": proxy_description,
                "requires_approval": True,
                "not_recommendation": True,
                "synthetic_candidate_only": True,
            }
            for lens_id, bucket_id, driver_category, proxy_description in rows
        ],
    }


def _external_story_report_workflow_map(external_pack_dir: Path) -> dict[str, Any]:
    rows = [
        ("Manager Story Summary", "manager_story_summary.json", "synthetic_pack_artifact"),
        ("Implied Lenses", "implied_lenses.json", "synthetic_pack_artifact"),
        ("Key-Price Scenario Set", "key_price_scenario_set.json", "synthetic_pack_artifact"),
        ("Portfolio Through External Lens", None, "gated"),
        ("Manager by External Lens", None, "gated"),
        ("Scenario Downside under External Story", None, "gated"),
        ("Scenario by Lens", None, "gated"),
        ("Governance/Caveat note", "governance_caveats.json", "synthetic_pack_artifact"),
    ]
    return {
        "schema_version": "external_story_report_workflow_map.v1",
        "synthetic_data": True,
        "workflow_id": "external_manager_story_translation_v1",
        "workflow_rows": [
            {
                "workflow_item": item,
                "source_artifact_path": (
                    _as_posix(external_pack_dir / filename) if filename else None
                ),
                "status": status,
                "not_verified": True,
                "not_recommendation": True,
            }
            for item, filename, status in rows
        ],
    }


def _governance_caveats() -> dict[str, Any]:
    return {
        "schema_version": "external_story_governance_caveats.v1",
        "synthetic_data": True,
        "caveats": {
            "translate_do_not_endorse": True,
            "not_verified": True,
            "not_recommendation": True,
            "no_live_data": True,
            "synthetic_demo_only": True,
            "requires_review_before_client_use": True,
            "external_manager_views_may_be_incomplete_or_wrong": True,
            "candidate_proxies_need_approval": True,
        },
    }


def _manifest(
    workflows: dict[str, dict[str, Any]],
    workflow_dir: Path,
    external_pack_dir: Path,
) -> dict[str, Any]:
    return {
        "schema_version": "report_workflow_catalog_manifest.v1",
        "catalog_id": CATALOG_ID,
        "catalog_version": CATALOG_VERSION,
        "generated_at": GENERATED_AT,
        "deterministic_generation_note": "Generated from arangur.analytics.report_workflow_catalog with fixed local synthetic inputs.",
        "synthetic_data": True,
        "workflow_count": len(workflows),
        "workflows": [
            {
                "workflow_id": workflow_id,
                "display_name": workflow["display_name"],
                "filename": WORKFLOW_FILENAMES[workflow_id],
            }
            for workflow_id, workflow in workflows.items()
        ],
        "report_source_directories": dict(REPORT_SOURCE_DIRECTORIES),
        "external_story_pack_ref": _as_posix(external_pack_dir),
        "primary_demo_goal": "Consolidate generated reports into audience-specific demo workflows before advisor UI or deployment wiring.",
        "limitations": [
            "Catalog only; not wired to Advisor Home, Preview, Populate, Present, generated reports, backend endpoints, Docker, or deployment.",
            "Synthetic local product-review artifacts only.",
            "External story translation is not verified and not a recommendation.",
        ],
        "not_wired_to_ui": True,
        "not_production_reporting": True,
        "workflow_dir": _as_posix(workflow_dir),
    }


def _product_docs(
    workflows: dict[str, dict[str, Any]],
    external_pack: dict[str, dict[str, Any]],
) -> dict[str, str]:
    return {
        "report_workflow_catalog_v1.md": _report_workflow_catalog_doc(workflows),
        "demo_report_suite_v1.md": _demo_report_suite_doc(),
        "report_family_acceptance_status_v1.md": _report_family_acceptance_doc(),
        "external_manager_story_workflow_v1.md": _external_manager_story_doc(external_pack),
    }


def _report_workflow_catalog_doc(workflows: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# Report Workflow Catalog v1",
        "",
        "A report workflow is an ordered conversation for a specific audience and use case. It is not every report the system can produce.",
        "",
        "This catalog is local product structure only. It does not wire Advisor Home, Preview, Populate, Present, generated reports, backend endpoints, Docker, deployment, live data, external APIs, real data, or recommendations.",
        "",
        "## Workflows",
        "",
        "| Workflow | Audience | Detail level | Conversation goal |",
        "| --- | --- | --- | --- |",
    ]
    for workflow in workflows.values():
        lines.append(
            f"| {workflow['display_name']} | {workflow['audience']} | {workflow['audience_depth']} | {workflow['conversation_goal']} |"
        )
    lines.extend(
        [
            "",
            "## Workflow Versus Report Family",
            "",
            "A report family defines a reusable report type, such as Portfolio Representation Status or Advisor Policy Attribution. A workflow chooses a small ordered subset of report families for one meeting.",
            "",
            "## Accepted Attribution Sequence",
            "",
            "The accepted sequence is policy allocation setup, advisor policy attribution, manager mandate attribution, manager driver matrix when needed, selected-manager drill-down for advisor oversight, and handoff control only when reconciliation is the question.",
            "",
            "Policy-Level Attribution Summary v1 is superseded as the primary product-review surface. Equal-weight AI Adoption Attribution remains diagnostic unless explicitly selected as policy.",
            "",
            "## Setup Notes Versus Client-Facing Reports",
            "",
            "Setup/readiness notes explain whether data, coverage, benchmark basis, or allocation basis is ready. They can support a workflow, but they should not be presented as the main client answer unless the meeting topic is readiness.",
            "",
            "## External Manager Story Workflow",
            "",
            "The external story workflow matters because an outside manager worldview often arrives as narrative. Arangur can translate that narrative into lenses, key-price scenarios, candidate proxies, and report-workflow gates without endorsing or verifying it.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _demo_report_suite_doc() -> str:
    sections = [
        ("Accepted Primary Demo Reports", [
            "Portfolio Representation Status",
            "Cash Flow Delivered",
            "Cash-Flow Support Outlook",
            "Aggregated Asset Allocation",
            "Current Portfolio Scenario Downside",
            "Policy Allocation Review",
            "Advisor Policy Attribution by Manager/Sleeve",
            "Manager Mandate Attribution Summary",
            "Full Lens Exposure - AI Adoption",
            "Full Lens Exposure - Energy Security",
        ]),
        ("Accepted Supporting Reports", [
            "Allocation by Manager",
            "Manager by Lens Exposure - AI Adoption",
            "Manager by Lens Exposure - Energy Security",
            "Advisor Policy Effect Totals",
            "Manager Driver Attribution Matrix",
        ]),
        ("Advisor-Only Reports", [
            "Policy Allocation Drift Summary",
            "Within-Manager Attribution Detail",
            "Manager Implementation Handoff",
            "Coverage and Confidence Warning when confidence affects interpretation",
        ]),
        ("Setup/Readiness Notes", [
            "Imputed Current Allocation Baseline",
            "Manager Mandate Benchmark Basis",
            "Coverage and Confidence Warning when used before client presentation",
        ]),
        ("Diagnostics", [
            "Integrated Performance Attribution Summary",
            "Integrated Performance Attribution Detail",
            "Lens-Based Performance Attribution - AI Adoption",
            "Manager Attribution Summary",
            "Equal-weight AI Adoption Attribution unless explicitly selected as policy",
        ]),
        ("Superseded Reports", [
            "Policy-Level Attribution Summary v1 as primary workflow step",
            "Policy-Level Manager Effect Detail v1 as primary workflow step",
        ]),
        ("Gated/Deferred Reports", [
            "High-Level Advisor Plan / Next-Year Positioning",
            "Coverage/Confidence by Manager",
            "Portfolio Through External Lens",
            "Manager by External Lens",
            "Scenario Downside under External Story",
            "Scenario by Lens for external story",
            "Timing Attribution",
            "Dollar P&L Attribution",
            "Blended / All-In Attribution",
            "Position-Level Manager Attribution",
            "Production/client attribution",
        ]),
    ]
    lines = [
        "# Demo Report Suite v1",
        "",
        "This suite classifies current local product-review reports for future workflow wiring. It does not wire UI, backend, generated reports, deployment, live data, or recommendations.",
        "",
    ]
    for title, rows in sections:
        lines.extend([f"## {title}", ""])
        lines.extend(f"- {row}" for row in rows)
        lines.append("")
    lines.extend(
        [
            "## Wire First In A Future UI/Demo Tranche",
            "",
            "Wire the four workflow choices first, then show the ordered steps for Principal / Family Office Briefing and Engaged Client / Investment Committee Review. Keep Advisor / Manager Oversight and External Manager Story Translation behind advisor/internal review labels.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _report_family_acceptance_doc() -> str:
    rows = [
        ("Policy Allocation Review", "accepted primary"),
        ("Policy Allocation Drift Summary", "advisor-only"),
        ("Imputed Current Allocation Baseline", "setup/readiness"),
        ("Manager Mandate Benchmark Basis", "setup/readiness"),
        ("Advisor Policy Attribution by Manager/Sleeve", "accepted primary"),
        ("Advisor Policy Effect Totals", "accepted supporting"),
        ("Manager Mandate Attribution Summary", "accepted primary"),
        ("Manager Driver Attribution Matrix", "accepted supporting"),
        ("Within-Manager Attribution Detail", "advisor-only"),
        ("Manager Implementation Handoff", "diagnostic"),
        ("Policy-Level Attribution Summary v1", "superseded"),
        ("Equal-weight AI Adoption Attribution", "diagnostic unless explicitly selected as policy"),
        ("Cash Flow Delivered", "accepted primary"),
        ("Cash-Flow Support Outlook", "accepted primary"),
        ("Portfolio Representation Status", "accepted primary"),
        ("Aggregated Asset Allocation", "accepted primary"),
        ("Allocation by Manager", "accepted supporting"),
        ("Coverage and Confidence Warning", "advisor-only or setup/readiness unless material"),
        ("Concentration by Asset Type", "accepted supporting"),
        ("Concentration by Manager/Sleeve", "accepted supporting"),
        ("Current Portfolio Scenario Downside", "accepted primary"),
        ("Full Lens Exposure", "accepted primary for AI Adoption and Energy Security synthetic demo"),
        ("Manager by Lens Exposure", "accepted supporting for AI Adoption and Energy Security synthetic demo"),
    ]
    lines = [
        "# Report Family Acceptance Status v1",
        "",
        "This status sheet classifies current local product-review reports. It is not production approval and does not wire reports into UI or generated reports.",
        "",
        "| Report | Status |",
        "| --- | --- |",
    ]
    lines.extend(f"| {report} | {status} |" for report, status in rows)
    lines.extend(
        [
            "",
            "## Supersession Rules",
            "",
            "Advisor Policy Attribution v2 supersedes Policy-Level Attribution Summary v1 as the primary policy attribution surface. Manager Mandate Attribution Summary and Manager Driver Attribution Matrix now carry manager implementation review.",
            "",
            "Equal-weight AI Adoption attribution is diagnostic unless an explicit policy artifact says equal weight is the agreed policy.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _external_manager_story_doc(external_pack: dict[str, dict[str, Any]]) -> str:
    story = external_pack["manager_story_summary.json"]
    lens_rows = external_pack["implied_lenses.json"]["lenses"]
    scenario_rows = external_pack["key_price_scenario_set.json"]["scenarios"]
    lines = [
        "# External Manager Story Workflow v1",
        "",
        "## Purpose",
        "",
        "This workflow shows how Arangur can translate an outside manager worldview into governed report structures. It translates; it does not endorse, verify, or recommend.",
        "",
        "## Story Summary",
        "",
        story["plain_english_summary"],
        "",
        "## Translation Sequence",
        "",
        "1. Summarize the manager story in plain English.",
        "2. Convert the story into implied lenses.",
        "3. Convert the story into key-price scenario candidates.",
        "4. List candidate benchmark/proxy ideas for later approval.",
        "5. Gate portfolio-through-lens, manager-by-lens, scenario downside, and scenario-by-lens reports until approved report mockups and inputs exist.",
        "6. Close with governance caveats.",
        "",
        "## Implied Lenses",
        "",
    ]
    lines.extend(f"- {row['display_name']}: {row['core_question']}" for row in lens_rows)
    lines.extend(["", "## Key-Price Scenarios", ""])
    lines.extend(f"- {row['display_name']}: {row['story_link']}" for row in scenario_rows)
    lines.extend(
        [
            "",
            "## What This Workflow Proves",
            "",
            "Arangur can turn narrative manager language into lenses, scenarios, candidate proxies, report-workflow gates, and governance notes without making investment recommendations.",
            "",
            "## What It Does Not Prove",
            "",
            "It does not prove the external manager is correct, does not validate live market claims, does not approve any proxy or benchmark, and does not produce a client-ready recommendation.",
            "",
            "## Governance Caveats",
            "",
            "- Translate, do not endorse.",
            "- Not verified.",
            "- Not a recommendation.",
            "- No live data or external APIs were used.",
            "- Candidate proxies require approval.",
            "- External manager views may be incomplete or wrong.",
            "",
            "## Future Demo Use",
            "",
            "A future deployed demo could show this as an advisor/internal workflow choice, then reveal the story summary, implied lenses, key-price scenarios, gated report map, and governance note before any client-facing presentation is considered.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _validate_workflow_shape(workflow_id: str, workflow: dict[str, Any]) -> None:
    required = {
        "workflow_id",
        "display_name",
        "audience",
        "audience_depth",
        "core_user_question",
        "conversation_goal",
        "ordered_steps",
        "supporting_reports",
        "setup_or_readiness_notes",
        "diagnostic_reports",
        "superseded_reports_excluded",
        "gated_or_deferred_reports",
        "client_facing_status",
        "advisor_only_status",
        "why_this_workflow_exists",
        "what_this_workflow_proves",
        "not_production_recommendation",
        "synthetic_data",
    }
    missing = required - set(workflow)
    if missing:
        raise ValueError(f"{workflow_id} missing workflow fields: {sorted(missing)}")
    if workflow["workflow_id"] != workflow_id:
        raise ValueError(f"{workflow_id} payload id mismatch")
    if not workflow["ordered_steps"]:
        raise ValueError(f"{workflow_id} must include ordered steps")
    for index, step in enumerate(workflow["ordered_steps"], start=1):
        if step["step_number"] != index:
            raise ValueError(f"{workflow_id} step numbering mismatch")
        _validate_step_shape(workflow_id, step)


def _validate_step_shape(workflow_id: str, step: dict[str, Any]) -> None:
    required = {
        "step_number",
        "report_id",
        "display_title",
        "report_family",
        "step_role",
        "audience_visibility",
        "why_included",
        "visible_question_answered",
        "status",
        "caveat",
    }
    missing = required - set(step)
    if missing:
        raise ValueError(f"{workflow_id} step missing fields: {sorted(missing)}")
    if step["step_role"] not in {
        "primary",
        "supporting",
        "setup_readiness",
        "diagnostic",
        "handoff",
    }:
        raise ValueError(f"{workflow_id} invalid step role {step['step_role']}")
    if step["audience_visibility"] not in {
        "client_facing",
        "advisor_review",
        "advisor_only",
        "internal_control",
    }:
        raise ValueError(f"{workflow_id} invalid audience visibility")
    if step["status"] not in {
        "available",
        "accepted",
        "accepted_with_minor_polish",
        "diagnostic",
        "setup_note",
        "superseded",
        "gated",
        "deferred",
    }:
        raise ValueError(f"{workflow_id} invalid status {step['status']}")


def _require_path(path: str | Path) -> None:
    if not Path(path).exists():
        raise ValueError(f"Required path does not exist: {path}")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate and validate demo report workflow catalog fixtures."
    )
    parser.add_argument("--workflow-dir", default=str(DEFAULT_WORKFLOW_DIR))
    parser.add_argument("--external-pack-dir", default=str(DEFAULT_EXTERNAL_PACK_DIR))
    parser.add_argument("--docs-dir", default=str(DEFAULT_DOCS_DIR))
    parser.add_argument("--validate-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.validate_only:
        summary = validate_catalog(
            workflow_dir=args.workflow_dir,
            external_pack_dir=args.external_pack_dir,
            docs_dir=args.docs_dir,
        )
    else:
        summary = generate_report_workflow_catalog(
            workflow_dir=args.workflow_dir,
            external_pack_dir=args.external_pack_dir,
            docs_dir=args.docs_dir,
        )

    print(f"Report workflow count: {summary['workflow_count']}")
    print(
        "Primary workflow IDs: "
        + ", ".join(summary["primary_workflow_ids"])
    )
    print(
        "Available report references: "
        f"{summary['available_report_reference_count']}"
    )
    print(f"Gated references: {summary['gated_reference_count']}")
    print(f"External story pack status: {summary['external_story_pack_status']}")
    print(f"Output path: {args.workflow_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
