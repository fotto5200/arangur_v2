"""Static report-element template catalog loader and filters."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Iterable


CATALOG_PATH = Path(__file__).resolve().with_name("templates.json")

REQUIRED_TEMPLATE_FIELDS = (
    "element_id",
    "title",
    "short_description",
    "category",
    "supported_branches",
    "supported_placements",
    "discovery_tags",
    "relevant_client_questions",
    "relevant_advisor_review_intents",
    "supported_scopes",
    "required_parameters",
    "optional_parameters",
    "fixed_metric",
    "supported_lenses",
    "scenario_requirement",
    "fixed_or_default_display",
    "supported_display_forms",
    "data_readiness_requirements",
    "completeness_checks",
    "default_caveat_rules",
)

LIST_FIELDS = (
    "supported_branches",
    "discovery_tags",
    "relevant_client_questions",
    "relevant_advisor_review_intents",
    "supported_scopes",
    "required_parameters",
    "optional_parameters",
    "supported_lenses",
    "supported_display_forms",
    "data_readiness_requirements",
    "completeness_checks",
    "default_caveat_rules",
)

OPTIONAL_LIST_FIELDS = (
    "advisor_internal_purposes",
    "supported_metrics",
)

SUPPORTED_BRANCHES = {"Client Briefing", "Advisor Review"}
SCENARIO_REQUIREMENTS = {"required", "optional", "not_applicable"}


class ReportElementCatalogError(ValueError):
    """Raised when the static report-element catalog is malformed."""


def load_templates() -> list[dict[str, Any]]:
    """Load and validate report-element templates from the static JSON catalog."""

    templates = _read_template_list()
    errors = validate_template_catalog(templates)
    if errors:
        raise ReportElementCatalogError("; ".join(errors))
    return deepcopy(templates)


def list_templates() -> list[dict[str, Any]]:
    """Return all report-element templates in catalog order."""

    return load_templates()


def get_template(element_id: str) -> dict[str, Any] | None:
    """Return one template by element_id, or None when it is not present."""

    for template in load_templates():
        if template["element_id"] == element_id:
            return template
    return None


def filter_templates(
    branch: str | None = None,
    category: str | None = None,
    query: str | None = None,
    tags: Iterable[str] | str | None = None,
    client_question: str | None = None,
    advisor_intent: str | None = None,
) -> list[dict[str, Any]]:
    """Filter templates for deterministic discovery in the future browser UI."""

    filtered = list_templates()
    if branch:
        filtered = [
            template
            for template in filtered
            if _contains_normalized(template["supported_branches"], branch)
        ]
    if category:
        category_key = _normalize(category)
        filtered = [
            template
            for template in filtered
            if _normalize(template["category"]) == category_key
        ]
    if query:
        query_key = _normalize(query)
        filtered = [
            template
            for template in filtered
            if query_key in _normalize(_searchable_text(template))
        ]
    tag_values = _normalize_filter_values(tags)
    if tag_values:
        filtered = [
            template
            for template in filtered
            if all(_contains_normalized(template["discovery_tags"], tag) for tag in tag_values)
        ]
    if client_question:
        filtered = [
            template
            for template in filtered
            if _contains_normalized(template["relevant_client_questions"], client_question)
        ]
    if advisor_intent:
        filtered = [
            template
            for template in filtered
            if _contains_normalized(template["relevant_advisor_review_intents"], advisor_intent)
        ]
    return filtered


def validate_template_catalog(templates: list[dict[str, Any]] | None = None) -> list[str]:
    """Return validation errors for the static catalog without mutating it."""

    if templates is None:
        templates = _read_template_list()
    errors: list[str] = []
    if not isinstance(templates, list):
        return ["catalog templates must be a list"]
    if not templates:
        return ["catalog must include at least one template"]

    seen_ids: set[str] = set()
    for index, template in enumerate(templates):
        label = str(template.get("element_id") or f"template[{index}]")
        for field in REQUIRED_TEMPLATE_FIELDS:
            if field not in template:
                errors.append(f"{label}: missing required field: {field}")
        element_id = template.get("element_id")
        if not isinstance(element_id, str) or not element_id:
            errors.append(f"{label}: element_id must be a non-empty string")
        elif element_id in seen_ids:
            errors.append(f"{label}: duplicate element_id")
        else:
            seen_ids.add(element_id)

        for field in ("title", "short_description", "category", "fixed_or_default_display"):
            if field in template and not _non_empty_string(template[field]):
                errors.append(f"{label}: {field} must be a non-empty string")

        fixed_metric = template.get("fixed_metric")
        if fixed_metric is not None and not _non_empty_string(fixed_metric):
            errors.append(f"{label}: fixed_metric must be null or a non-empty string")

        for field in LIST_FIELDS:
            if field in template and not _list_of_strings(template[field]):
                errors.append(f"{label}: {field} must be a list of strings")
        for field in OPTIONAL_LIST_FIELDS:
            if field in template and not _list_of_strings(template[field]):
                errors.append(f"{label}: {field} must be a list of strings")

        branches = template.get("supported_branches", [])
        if isinstance(branches, list):
            unsupported = [branch for branch in branches if branch not in SUPPORTED_BRANCHES]
            if unsupported:
                errors.append(f"{label}: unsupported branch values: {', '.join(unsupported)}")
        scenario_requirement = template.get("scenario_requirement")
        if scenario_requirement not in SCENARIO_REQUIREMENTS:
            errors.append(f"{label}: scenario_requirement must be required, optional, or not_applicable")

        placements = template.get("supported_placements")
        if not isinstance(placements, dict):
            errors.append(f"{label}: supported_placements must be a branch-to-list mapping")
        elif isinstance(branches, list):
            for branch in branches:
                if branch not in placements:
                    errors.append(f"{label}: supported_placements missing branch: {branch}")
                elif not _list_of_strings(placements[branch]):
                    errors.append(f"{label}: supported_placements[{branch}] must be a list of strings")

        lenses = template.get("supported_lenses", [])
        if isinstance(lenses, list) and any(lens == "Manager" for lens in lenses):
            errors.append(f"{label}: plain Manager cannot be used as a lens")

        if scenario_requirement == "required" and "scenario_id" not in template.get("required_parameters", []):
            errors.append(f"{label}: scenario-required templates must require scenario_id")
    return errors


def _read_template_list() -> list[dict[str, Any]]:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        catalog = json.load(handle)
    templates = catalog.get("templates") if isinstance(catalog, dict) else None
    if not isinstance(templates, list):
        raise ReportElementCatalogError("templates.json must contain a templates list")
    return templates


def _searchable_text(template: dict[str, Any]) -> str:
    values: list[str] = [
        template.get("element_id", ""),
        template.get("title", ""),
        template.get("short_description", ""),
        template.get("category", ""),
    ]
    for field in (
        "discovery_tags",
        "relevant_client_questions",
        "relevant_advisor_review_intents",
        "supported_scopes",
        "supported_lenses",
        "advisor_internal_purposes",
    ):
        values.extend(str(value) for value in template.get(field, []))
    return " ".join(values)


def _contains_normalized(values: Iterable[str], candidate: str) -> bool:
    candidate_key = _normalize(candidate)
    return any(_normalize(value) == candidate_key for value in values)


def _normalize_filter_values(values: Iterable[str] | str | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        raw_values = values.split(",")
    else:
        raw_values = []
        for value in values:
            raw_values.extend(str(value).split(","))
    return [_normalize(value) for value in raw_values if _normalize(value)]


def _normalize(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _list_of_strings(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)
