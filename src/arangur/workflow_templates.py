"""Local advisor workflow templates for demo report generation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


REQUIRED_TEMPLATE_FIELDS = (
    "workflow_type",
    "display_name",
    "intended_audience",
    "meeting_goal",
    "primary_questions",
    "emphasized_report_sections",
    "de_emphasized_sections",
    "required_inputs",
    "advisor_talking_points",
    "caveats",
    "suggested_follow_up_actions",
    "next_upgrade_path",
)


WORKFLOW_TEMPLATES: dict[str, dict[str, Any]] = {
    "quarterly_review": {
        "workflow_type": "quarterly_review",
        "display_name": "Quarterly Review",
        "intended_audience": "Advisor preparing a recurring portfolio review meeting.",
        "meeting_goal": "Summarize portfolio value, manager allocation, major exposures, direct overlap, and the current deterministic scenario result for a routine review.",
        "primary_questions": [
            "What changed enough to discuss in the quarterly review?",
            "Where are the largest manager, account, sector, theme, and cash exposures?",
            "Which scenario result should be used as the meeting's risk prompt?",
        ],
        "emphasized_report_sections": [
            "Executive Summary",
            "Portfolio Value Summary",
            "Manager/Account Summary",
            "Scenario Shock Summary",
        ],
        "de_emphasized_sections": [
            "Deep data coverage diagnostics",
            "Implementation roadmap",
        ],
        "required_inputs": [
            "CanonicalPortfolioSnapshot",
            "ValuationResult",
            "ExposureOverlapResult",
            "ScenarioResult",
        ],
        "advisor_talking_points": [
            "Use the quarterly review to anchor the conversation in total value, cash, manager mix, and the most visible concentration themes.",
            "Confirm whether the Microsoft and NVIDIA overlap is intentional before treating it as a problem.",
            "Use the deterministic AI/chips scenario as a discussion prompt rather than a prediction.",
            "Frame cash and fixed income as ballast that reduces, but does not erase, growth-theme concentration.",
        ],
        "caveats": [
            "Quarterly review framing is synthetic and local-only.",
            "Scenario shocks are deterministic assumptions, not forecasts.",
            "The report does not prove production reconciliation or advisor suitability.",
        ],
        "suggested_follow_up_actions": [
            "Ask whether the current AI/chips concentration remains intentional.",
            "Decide whether duplicated direct holdings should be reviewed with each manager.",
            "Flag any account or manager naming that should be cleaned up before a real client workflow.",
        ],
        "next_upgrade_path": "Add workflow-specific summary cards and period-over-period changes once historical synthetic fixtures exist.",
    },
    "manager_overlap_review": {
        "workflow_type": "manager_overlap_review",
        "display_name": "Manager Overlap Review",
        "intended_audience": "Advisor or investment lead reviewing duplicated exposures across managers and accounts.",
        "meeting_goal": "Focus the meeting on direct holding duplication, concentration, and whether overlap across managers is intentional.",
        "primary_questions": [
            "Which holdings are duplicated across accounts or managers?",
            "Do duplicated positions reinforce a deliberate thesis or create accidental concentration?",
            "Which manager conversations should happen before changing allocations?",
        ],
        "emphasized_report_sections": [
            "Manager Overlap / Duplication Findings",
            "Top Holdings",
            "Theme Exposure",
            "Manager/Account Summary",
        ],
        "de_emphasized_sections": [
            "Broad quarterly summary",
            "Data coverage diagnostics",
        ],
        "required_inputs": [
            "CanonicalPortfolioSnapshot",
            "ValuationResult",
            "ExposureOverlapResult",
        ],
        "advisor_talking_points": [
            "The overlap review should start with duplicated direct holdings, especially Microsoft and NVIDIA across core and satellite managers.",
            "Separate intentional thesis reinforcement from accidental duplication before recommending any action.",
            "Use manager-level totals to decide which manager conversations matter most.",
            "Theme exposure can exceed 100% in aggregate, so use direct overlap rows for concrete duplication discussions.",
        ],
        "caveats": [
            "Current overlap analysis is direct-holding overlap only.",
            "The workflow does not include ETF or fund look-through.",
            "Classifications come from synthetic local fixtures and are not production data.",
        ],
        "suggested_follow_up_actions": [
            "Review duplicated direct holdings with each manager.",
            "Document whether the overlap is intentional, acceptable, or needs further research.",
            "Identify any fund look-through data that would be needed for a stronger overlap review.",
        ],
        "next_upgrade_path": "Add threshold-based overlap severity labels and optional fund look-through when licensed data exists.",
    },
    "scenario_risk_review": {
        "workflow_type": "scenario_risk_review",
        "display_name": "Scenario Risk Review",
        "intended_audience": "Advisor or investment committee support user discussing portfolio impact under stated assumptions.",
        "meeting_goal": "Lead with deterministic scenario impact, matched assumptions, and risk caveats while avoiding forecast language.",
        "primary_questions": [
            "What is the portfolio impact under the current deterministic AI/chips shock?",
            "Which positions and managers drive the largest downside in the scenario?",
            "Which assumptions should be reviewed before the scenario is used in a meeting?",
        ],
        "emphasized_report_sections": [
            "Scenario Shock Summary",
            "Theme Exposure",
            "Top Holdings",
            "What This Demo Does Not Yet Prove",
        ],
        "de_emphasized_sections": [
            "Routine quarterly meeting flow",
            "Data coverage diagnostics",
        ],
        "required_inputs": [
            "CanonicalPortfolioSnapshot",
            "ValuationResult",
            "ScenarioDefinition",
            "ScenarioResult",
        ],
        "advisor_talking_points": [
            "This scenario risk review is about portfolio impact under stated assumptions, not market forecasting.",
            "The AI/chips scenario shows where theme concentration could matter if leadership reverses.",
            "Review the largest negative position impacts before deciding whether to refine the scenario assumptions.",
            "Cash and fixed income are visible offsets, but the scenario still concentrates downside in growth-oriented holdings.",
        ],
        "caveats": [
            "Scenario results are deterministic demo approximations and are not forecasts.",
            "No stochastic, covariance, probability, or path-dependent simulation is implemented in this workflow.",
            "Scenario assumptions come from synthetic local fixtures.",
        ],
        "suggested_follow_up_actions": [
            "Confirm the scenario narrative and shock assumptions with the advisory team.",
            "Identify whether a second scenario should be added before a client-style review.",
            "Capture which driver assumptions should feed a future scenario library design.",
        ],
        "next_upgrade_path": "Design a scenario library/source model before adding seeded stochastic simulation.",
    },
    "intake_review": {
        "workflow_type": "intake_review",
        "display_name": "Intake Review",
        "intended_audience": "Advisor or operations reviewer checking whether a new source can feed the Arangur workflow.",
        "meeting_goal": "Check source shape, canonical mapping, basic valuation readiness, and obvious follow-up items before deeper analysis.",
        "primary_questions": [
            "Did the source adapter produce a valid canonical snapshot?",
            "Are accounts, managers, holdings, cash, and securities mapped clearly enough for review?",
            "What needs human cleanup before the portfolio can become a stronger workflow example?",
        ],
        "emphasized_report_sections": [
            "Portfolio Value Summary",
            "Manager/Account Summary",
            "What This Demo Proves",
            "What This Demo Does Not Yet Prove",
        ],
        "de_emphasized_sections": [
            "Advanced scenario interpretation",
            "Production data confidence scoring",
        ],
        "required_inputs": [
            "CanonicalPortfolioSnapshot",
            "ValuationResult",
            "ReportPackage",
            "Source provenance metadata",
        ],
        "advisor_talking_points": [
            "Use the intake review to confirm that the source maps cleanly into the canonical snapshot before over-interpreting analytics.",
            "For the Plaid-shaped mock path, focus on account, security, holding, and cash mapping rather than live Plaid behavior.",
            "The downstream analytics working from the canonical snapshot is the main product proof in this workflow.",
            "Any missing identifiers, stale values, or manual classification gaps should become follow-up tasks.",
        ],
        "caveats": [
            "This intake review uses synthetic local data only.",
            "Plaid-shaped mock input is not live Plaid, Plaid Sandbox, Plaid Link, or real account data.",
            "The workflow does not prove production reconciliation or data completeness.",
        ],
        "suggested_follow_up_actions": [
            "Review source provenance and mapping fields before expanding the adapter.",
            "Record any account, security, or manager labels that should be normalized.",
            "Decide which source-specific validations should be added next.",
        ],
        "next_upgrade_path": "Add adapter-specific validation summaries and source coverage checks before live ingestion design.",
    },
    "data_coverage_review": {
        "workflow_type": "data_coverage_review",
        "display_name": "Data Coverage Review",
        "intended_audience": "Advisor, analyst, or operations reviewer assessing valuation confidence and data readiness.",
        "meeting_goal": "Frame what the current demo can and cannot say about data coverage, valuation confidence, and human-review needs.",
        "primary_questions": [
            "Which data fields are cleanly available in the current synthetic fixtures?",
            "Which valuation-confidence concepts are not implemented yet?",
            "Where would real portfolios need source inventory, reconciliation, or human review?",
        ],
        "emphasized_report_sections": [
            "Synthetic-Data Caveat",
            "What This Demo Does Not Yet Prove",
            "Portfolio Value Summary",
            "Next Planned Upgrades",
        ],
        "de_emphasized_sections": [
            "Client-ready recommendations",
            "Forecasting or performance prediction",
        ],
        "required_inputs": [
            "CanonicalPortfolioSnapshot",
            "ValuationResult",
            "ReportPackage",
            "Future data coverage metadata",
        ],
        "advisor_talking_points": [
            "This data coverage review introduces valuation confidence as a future report dimension, not as a completed scoring model.",
            "The current public-security synthetic data is clean by design; real private assets, opaque managers, and statements would need coverage checks.",
            "Valuation confidence should distinguish source quality and freshness from investment forecasting.",
            "Human review requirements should be visible before a portfolio is treated as report-ready.",
        ],
        "caveats": [
            "No formal valuation-confidence scoring is implemented yet.",
            "No market-data vendor, statement extraction, or real custodian data is used.",
            "Data coverage describes source readiness and does not forecast investment performance.",
        ],
        "suggested_follow_up_actions": [
            "Prototype synthetic coverage metadata for each holding, account, and source file.",
            "Define a simple high/medium/low valuation-confidence rubric.",
            "Add a Data Coverage / Valuation Confidence report prototype as the next implementation batch.",
        ],
        "next_upgrade_path": "Create a synthetic data coverage fixture and report section that labels source coverage, stale values, and human-review needs.",
    },
}


SUPPORTED_WORKFLOW_TYPES = tuple(WORKFLOW_TEMPLATES)


class WorkflowTemplateError(ValueError):
    """Raised when a workflow template is missing or malformed."""


def get_workflow_template(workflow_type: str) -> dict[str, Any]:
    if workflow_type not in WORKFLOW_TEMPLATES:
        raise WorkflowTemplateError(_unsupported_workflow_message(workflow_type))
    template = deepcopy(WORKFLOW_TEMPLATES[workflow_type])
    errors = validate_workflow_template(template)
    if errors:
        raise WorkflowTemplateError(f"Workflow template {workflow_type} is invalid: {'; '.join(errors)}")
    return template


def list_workflow_types() -> tuple[str, ...]:
    return SUPPORTED_WORKFLOW_TYPES


def validate_workflow_template(template: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_TEMPLATE_FIELDS:
        if field not in template:
            errors.append(f"missing required field: {field}")
    workflow_type = template.get("workflow_type")
    if workflow_type not in WORKFLOW_TEMPLATES:
        errors.append(f"unsupported workflow_type: {workflow_type}")
    for field in (
        "primary_questions",
        "emphasized_report_sections",
        "de_emphasized_sections",
        "required_inputs",
        "advisor_talking_points",
        "caveats",
        "suggested_follow_up_actions",
    ):
        if field in template and not isinstance(template[field], list):
            errors.append(f"{field} must be a list")
    return errors


def _unsupported_workflow_message(workflow_type: str) -> str:
    return (
        f"Unsupported workflow: {workflow_type}. "
        f"Supported workflows: {', '.join(SUPPORTED_WORKFLOW_TYPES)}"
    )
