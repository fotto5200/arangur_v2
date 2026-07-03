"""Resolve browser workflow specs to committed analytic report-element views."""

from __future__ import annotations

from typing import Any


ANALYTIC_INPUT_VARIANT = "analytic_pack_v1"
ANALYTIC_PACK_ID = "arranger_demo_pack_v1"

ANALYTIC_VIEW_KEYS_BY_ELEMENT = {
    "portfolio_status": "portfolio_status_analytics",
    "concentration": "concentration_theme_analytics",
    "manager_comparison": "manager_comparison_analytics",
    "scenario_impact_by_manager": "scenario_impact_by_theme_manager_analytics",
    "data_confidence_note": "data_confidence_note_analytics",
}

LEGACY_VIEW_KEYS_BY_ELEMENT = {
    "portfolio_status": "portfolio_status",
    "cash_generation_summary": "cash_generation_summary",
    "manager_comparison": "manager_comparison",
    "data_confidence_note": "data_confidence_note",
}

AI_CHIP_SELLOFF_CHOICES = {
    "ai chip selloff",
    "ai/chip selloff",
    "ai / chip selloff",
    "ai_chip_selloff",
}

PACK_LENS_CHOICES = {
    "strategic theme",
    "manager role / mandate",
    "liquidity profile",
    "data confidence",
}


def matched_view_key_for_parameters(element_id: str, parameters: dict[str, Any] | None) -> str | None:
    """Return the committed rendered-view key for a workflow spec, if one exists."""

    params = parameters or {}
    scope = _normalize(params.get("scope"))
    if scope.startswith("selected "):
        return None

    if element_id == "portfolio_status":
        return ANALYTIC_VIEW_KEYS_BY_ELEMENT["portfolio_status"]

    if element_id == "cash_generation_summary":
        return LEGACY_VIEW_KEYS_BY_ELEMENT["cash_generation_summary"]

    if element_id == "manager_comparison":
        lens = _normalize(params.get("lens"))
        if not lens or lens in PACK_LENS_CHOICES or "theme" in lens or "mandate" in lens:
            return ANALYTIC_VIEW_KEYS_BY_ELEMENT["manager_comparison"]
        return LEGACY_VIEW_KEYS_BY_ELEMENT["manager_comparison"]

    if element_id == "data_confidence_note":
        return ANALYTIC_VIEW_KEYS_BY_ELEMENT["data_confidence_note"]

    if element_id == "concentration":
        lens = _normalize(params.get("lens"))
        if lens in {"theme", "approved theme", "strategic theme"} or "theme" in lens:
            return ANALYTIC_VIEW_KEYS_BY_ELEMENT["concentration"]
        if "sector" in lens or "industry" in lens:
            return "concentration_sector_industry"
        return None

    if element_id == "scenario_impact_by_manager":
        scenario = _normalize(params.get("scenario_id")).replace(" / ", "/")
        if scenario in AI_CHIP_SELLOFF_CHOICES:
            return ANALYTIC_VIEW_KEYS_BY_ELEMENT["scenario_impact_by_manager"]
        return None

    return None


def advisor_selection_summary(parameters: dict[str, Any] | None) -> str:
    """Return advisor-facing selected configuration text without technical ids."""

    params = parameters or {}
    pieces: list[str] = []
    for key, label in (
        ("scope", "Scope"),
        ("lens", "Lens"),
        ("theme_focus", "Theme focus"),
        ("scenario_id", "Scenario"),
        ("confidence_focus", "Confidence focus"),
    ):
        value = _clean_string(params.get(key))
        if value:
            pieces.append(f"{label}: {value}")
    if not pieces:
        return ""
    summary = "Selected configuration: " + "; ".join(pieces)
    theme_focus = _normalize(params.get("theme_focus"))
    if theme_focus and theme_focus != "all approved themes":
        summary += ". Demo view shows the full approved-theme analytic view; it is not theme-filtered yet."
    return summary


def _clean_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize(value: Any) -> str:
    return " ".join(_clean_string(value).lower().replace("_", " ").split())
