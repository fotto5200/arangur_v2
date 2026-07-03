from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_COMPONENTS: dict[str, tuple[str, str]] = {
    "theme_catalog": ("themes", "theme_id"),
    "classification_lens_catalog": ("lenses", "lens_id"),
    "scenario_catalog": ("scenarios", "scenario_id"),
    "scenario_shock_pack": ("scenario_shocks", "shock_id"),
    "data_confidence_rule_catalog": ("rules", "rule_id"),
    "report_analytic_capability_map": ("capabilities", "report_element_id"),
}

REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "pack_id",
    "pack_version",
    "display_name",
    "description",
    "created_by",
    "created_at",
    "approved_at",
    "synthetic_demo_pack",
    "component_paths",
    "notes",
}

REQUIRED_RECORD_FIELDS: dict[str, set[str]] = {
    "theme_catalog": {
        "theme_id",
        "display_name",
        "description",
        "exposure_direction_notes",
        "example_position_tags",
        "advisor_description",
    },
    "classification_lens_catalog": {
        "lens_id",
        "display_name",
        "description",
        "allowed_scope",
        "categories",
    },
    "scenario_catalog": {
        "scenario_id",
        "display_name",
        "short_description",
        "advisor_story",
        "primary_drivers",
        "supported_horizons",
        "supported_report_elements",
        "caveats",
    },
    "scenario_shock_pack": {
        "scenario_id",
        "shock_id",
        "variable_shocks",
        "qualitative_assumptions",
        "confidence_level",
        "caveats",
    },
    "data_confidence_rule_catalog": {
        "rule_id",
        "display_name",
        "applies_to",
        "confidence_effect",
        "advisor_language",
    },
    "report_analytic_capability_map": {
        "report_element_id",
        "supported_themes",
        "supported_scenarios",
        "supported_lenses",
        "supported_scopes",
        "required_inputs",
        "unsupported_reason_if_any",
    },
}

DEFAULT_TEMPLATE_CATALOG_PATH = Path("src/arangur/report_elements/templates.json")


def load_pack_manifest(pack_dir: Path | str) -> dict[str, Any]:
    """Load the manifest for a published analytic pack directory."""
    path = Path(pack_dir) / "pack_manifest.json"
    return _load_json(path)


def load_pack_components(pack_dir: Path | str) -> dict[str, dict[str, Any]]:
    """Load manifest-referenced component files for a published analytic pack."""
    root = Path(pack_dir)
    manifest = load_pack_manifest(root)
    components: dict[str, dict[str, Any]] = {}
    for component_name, relative_path in manifest.get("component_paths", {}).items():
        components[component_name] = _load_json(root / relative_path)
    return components


def load_analytic_pack(pack_dir: Path | str) -> dict[str, Any]:
    """Load manifest, components, summary, and validation in one small object."""
    root = Path(pack_dir)
    manifest = load_pack_manifest(root)
    components = load_pack_components(root)
    return {
        "pack_dir": str(root),
        "manifest": manifest,
        "components": components,
        "summary": summarize_analytic_pack(root),
        "validation": validate_pack_shape(root),
    }


def summarize_analytic_pack(pack_dir: Path | str) -> dict[str, Any]:
    """Return compact counts and ids for restart docs/tests."""
    manifest = load_pack_manifest(pack_dir)
    components = load_pack_components(pack_dir)
    summary: dict[str, Any] = {
        "pack_id": manifest.get("pack_id"),
        "pack_version": manifest.get("pack_version"),
        "display_name": manifest.get("display_name"),
        "synthetic_demo_pack": manifest.get("synthetic_demo_pack"),
        "component_counts": {},
        "component_ids": {},
    }
    for component_name, (list_key, id_key) in REQUIRED_COMPONENTS.items():
        records = components.get(component_name, {}).get(list_key, [])
        summary["component_counts"][component_name] = len(records) if isinstance(records, list) else 0
        summary["component_ids"][component_name] = [
            record.get(id_key)
            for record in records
            if isinstance(record, dict) and isinstance(record.get(id_key), str)
        ]
    return summary


def validate_pack_shape(
    pack_dir: Path | str,
    *,
    template_catalog_path: Path | str | None = DEFAULT_TEMPLATE_CATALOG_PATH,
) -> dict[str, Any]:
    """Validate the demo analytic pack shape without a JSON Schema dependency."""
    root = Path(pack_dir)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    manifest_path = root / "pack_manifest.json"
    if not manifest_path.exists():
        _add_issue(errors, "MANIFEST_MISSING", "pack_manifest", "pack_manifest.json is required.")
        return _validation_result(errors, warnings)

    try:
        manifest = _load_json(manifest_path)
    except ValueError as exc:
        _add_issue(errors, "MANIFEST_INVALID_JSON", "pack_manifest", str(exc))
        return _validation_result(errors, warnings)

    for field in sorted(REQUIRED_MANIFEST_FIELDS):
        if field not in manifest:
            _add_issue(errors, "MANIFEST_FIELD_MISSING", field, f"Manifest field {field} is required.")

    component_paths = manifest.get("component_paths")
    if not isinstance(component_paths, dict):
        _add_issue(errors, "COMPONENT_PATHS_INVALID", "component_paths", "component_paths must be an object.")
        component_paths = {}

    for component_name in REQUIRED_COMPONENTS:
        if component_name not in component_paths:
            _add_issue(errors, "COMPONENT_PATH_MISSING", component_name, f"{component_name} must be referenced.")

    components: dict[str, dict[str, Any]] = {}
    for component_name, relative_path in component_paths.items():
        if component_name not in REQUIRED_COMPONENTS:
            _add_issue(warnings, "UNKNOWN_COMPONENT", component_name, "Manifest references an unknown component.")
            continue
        path = _resolve_component_path(root, relative_path, errors, component_name)
        if path is None:
            continue
        try:
            components[component_name] = _load_json(path)
        except ValueError as exc:
            _add_issue(errors, "COMPONENT_INVALID_JSON", component_name, str(exc))

    pack_id = manifest.get("pack_id")
    for component_name, payload in components.items():
        if payload.get("schema_version") != "analytic_pack_component.v1":
            _add_issue(errors, "COMPONENT_SCHEMA_VERSION_INVALID", component_name, "Unexpected component schema_version.")
        if payload.get("pack_id") != pack_id:
            _add_issue(errors, "COMPONENT_PACK_ID_MISMATCH", component_name, "Component pack_id must match manifest pack_id.")
        if payload.get("component_type") != component_name:
            _add_issue(errors, "COMPONENT_TYPE_MISMATCH", component_name, "component_type must match manifest component key.")
        if manifest.get("synthetic_demo_pack") is True and payload.get("synthetic_demo_pack") is not True:
            _add_issue(errors, "SYNTHETIC_COMPONENT_REQUIRED", component_name, "Demo component must mark synthetic_demo_pack=true.")
        _validate_records(component_name, payload, errors)

    ids = _component_ids(components)
    _validate_references(components, ids, errors, warnings)

    if manifest.get("synthetic_demo_pack") is not True:
        _add_issue(errors, "SYNTHETIC_DEMO_PACK_REQUIRED", "synthetic_demo_pack", "Demo pack must mark synthetic_demo_pack=true.")

    if template_catalog_path is not None and "report_analytic_capability_map" in components:
        _validate_report_element_references(Path(template_catalog_path), components, errors, warnings)

    return _validation_result(errors, warnings)


def _resolve_component_path(
    root: Path,
    path_value: Any,
    errors: list[dict[str, str]],
    component_name: str,
) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        _add_issue(errors, "COMPONENT_PATH_INVALID", component_name, "Component path must be a non-empty string.")
        return None
    relative = Path(path_value)
    if relative.is_absolute() or ".." in relative.parts:
        _add_issue(errors, "COMPONENT_PATH_ESCAPES_PACK", component_name, "Component path must stay inside the pack directory.")
        return None
    path = root / relative
    if not path.exists():
        _add_issue(errors, "COMPONENT_FILE_MISSING", component_name, f"Component file is missing: {path_value}")
        return None
    return path


def _validate_records(component_name: str, payload: dict[str, Any], errors: list[dict[str, str]]) -> None:
    list_key, id_key = REQUIRED_COMPONENTS[component_name]
    records = payload.get(list_key)
    if not isinstance(records, list) or not records:
        _add_issue(errors, "COMPONENT_RECORDS_MISSING", component_name, f"{list_key} must be a non-empty list.")
        return

    seen: set[str] = set()
    required_fields = REQUIRED_RECORD_FIELDS[component_name]
    for index, record in enumerate(records):
        record_id = record.get(id_key) if isinstance(record, dict) else None
        record_label = record_id or f"{component_name}[{index}]"
        if not isinstance(record, dict):
            _add_issue(errors, "COMPONENT_RECORD_INVALID", record_label, "Component records must be objects.")
            continue
        if not isinstance(record_id, str) or not record_id:
            _add_issue(errors, "COMPONENT_RECORD_ID_MISSING", record_label, f"{id_key} is required.")
        elif record_id in seen:
            _add_issue(errors, "COMPONENT_RECORD_ID_DUPLICATE", record_id, f"Duplicate {id_key}.")
        else:
            seen.add(record_id)
        for field in sorted(required_fields):
            if field not in record:
                _add_issue(errors, "COMPONENT_RECORD_FIELD_MISSING", record_label, f"{field} is required.")
        _validate_human_facing_copy(component_name, record, record_label, errors)


def _validate_human_facing_copy(
    component_name: str,
    record: dict[str, Any],
    record_label: str,
    errors: list[dict[str, str]],
) -> None:
    copy_fields = {
        "theme_catalog": ("display_name", "description", "advisor_description"),
        "classification_lens_catalog": ("display_name", "description"),
        "scenario_catalog": ("display_name", "short_description", "advisor_story"),
        "data_confidence_rule_catalog": ("display_name", "advisor_language"),
    }.get(component_name, ())
    for field in copy_fields:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            _add_issue(errors, "HUMAN_FACING_COPY_MISSING", record_label, f"{field} must contain advisor-readable text.")


def _component_ids(components: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {}
    for component_name, (list_key, id_key) in REQUIRED_COMPONENTS.items():
        records = components.get(component_name, {}).get(list_key, [])
        ids[component_name] = {
            record[id_key]
            for record in records
            if isinstance(record, dict) and isinstance(record.get(id_key), str)
        }
    return ids


def _validate_references(
    components: dict[str, dict[str, Any]],
    ids: dict[str, set[str]],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    scenario_ids = ids.get("scenario_catalog", set())
    theme_ids = ids.get("theme_catalog", set())
    lens_ids = ids.get("classification_lens_catalog", set())

    for shock in components.get("scenario_shock_pack", {}).get("scenario_shocks", []):
        scenario_id = shock.get("scenario_id") if isinstance(shock, dict) else None
        shock_id = shock.get("shock_id") if isinstance(shock, dict) else "scenario_shock"
        if scenario_id not in scenario_ids:
            _add_issue(errors, "SCENARIO_SHOCK_REFERENCE_INVALID", str(shock_id), f"Unknown scenario_id: {scenario_id}")

    for capability in components.get("report_analytic_capability_map", {}).get("capabilities", []):
        if not isinstance(capability, dict):
            continue
        record_id = str(capability.get("report_element_id", "capability"))
        for theme_id in capability.get("supported_themes", []):
            if theme_id not in theme_ids:
                _add_issue(errors, "CAPABILITY_THEME_REFERENCE_INVALID", record_id, f"Unknown theme_id: {theme_id}")
        for scenario_id in capability.get("supported_scenarios", []):
            if scenario_id not in scenario_ids:
                _add_issue(errors, "CAPABILITY_SCENARIO_REFERENCE_INVALID", record_id, f"Unknown scenario_id: {scenario_id}")
        for lens_id in capability.get("supported_lenses", []):
            if lens_id not in lens_ids:
                _add_issue(errors, "CAPABILITY_LENS_REFERENCE_INVALID", record_id, f"Unknown lens_id: {lens_id}")
        if not capability.get("supported_themes") and not capability.get("supported_scenarios"):
            _add_issue(warnings, "CAPABILITY_HAS_NO_ANALYTIC_SELECTIONS", record_id, "Capability has no themes or scenarios.")


def _validate_report_element_references(
    template_catalog_path: Path,
    components: dict[str, dict[str, Any]],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    if not template_catalog_path.exists():
        _add_issue(warnings, "TEMPLATE_CATALOG_MISSING", str(template_catalog_path), "Report template catalog was not found.")
        return
    try:
        template_payload = _load_json(template_catalog_path)
    except ValueError as exc:
        _add_issue(warnings, "TEMPLATE_CATALOG_INVALID_JSON", str(template_catalog_path), str(exc))
        return
    template_ids = {
        template.get("element_id")
        for template in template_payload.get("templates", [])
        if isinstance(template, dict)
    }
    for capability in components.get("report_analytic_capability_map", {}).get("capabilities", []):
        if not isinstance(capability, dict):
            continue
        report_element_id = capability.get("report_element_id")
        if report_element_id not in template_ids:
            _add_issue(errors, "CAPABILITY_REPORT_ELEMENT_UNKNOWN", str(report_element_id), "Capability references an unknown report element id.")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: JSON payload must be an object.")
    return payload


def _validation_result(errors: list[dict[str, str]], warnings: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "status": "valid" if not errors else "invalid",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def _add_issue(target: list[dict[str, str]], code: str, record_id: str, message: str) -> None:
    target.append({"code": code, "record_id": record_id, "message": message})
