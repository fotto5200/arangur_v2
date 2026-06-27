"""File-backed workflow-run service for the FastAPI demo app."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arangur.demo_pipeline import PipelineError, project_root, run_pipeline
from arangur.workflow_templates import WorkflowTemplateError, get_workflow_template, list_workflow_types

from .persistence import (
    PersistenceError,
    get_workflow_run as get_persisted_workflow_run,
    list_workflow_runs as list_persisted_workflow_runs,
    persist_workflow_run_summary,
    persistence_enabled,
)
from .settings import AppSettings


API_SOURCES = {
    "native_demo": {
        "source": "native_demo",
        "pipeline_source": "demo_json",
        "display_name": "Native Demo",
        "description": "Synthetic native JSON fixture pipeline.",
    },
    "plaid_mock": {
        "source": "plaid_mock",
        "pipeline_source": "plaid_mock",
        "display_name": "Plaid-Shaped Mock",
        "description": "Synthetic Plaid-shaped fixture normalized through the mock adapter.",
    },
}

REPORTS_DEMO_PATH = "reports/demo"


class RunServiceError(ValueError):
    """Raised when a file-backed workflow-run operation cannot complete."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def list_sources() -> list[dict[str, str]]:
    return [
        {
            "source": source["source"],
            "display_name": source["display_name"],
            "description": source["description"],
        }
        for source in API_SOURCES.values()
    ]


def list_workflows() -> list[dict[str, Any]]:
    workflows: list[dict[str, Any]] = []
    for workflow_type in list_workflow_types():
        template = get_workflow_template(workflow_type)
        workflows.append(
            {
                "workflow": workflow_type,
                "display_name": template["display_name"],
                "meeting_goal": template["meeting_goal"],
                "required_inputs": template["required_inputs"],
            }
        )
    return workflows


def create_workflow_run(
    source: str,
    workflow: str,
    root: Path | None = None,
    settings: AppSettings | None = None,
) -> dict[str, Any]:
    resolved_root = root or project_root()
    source_config = _validate_source(source)
    _validate_workflow(workflow)
    try:
        outputs = run_pipeline(
            resolved_root,
            source=source_config["pipeline_source"],
            workflow_type=workflow,
            refresh_index=True,
        )
    except (PipelineError, WorkflowTemplateError) as exc:
        raise RunServiceError("pipeline_failed", str(exc)) from exc

    package_path = outputs["report_package"]
    package = _load_json(package_path)
    summary = _run_summary_from_package(resolved_root, package_path, package)
    summary["status"] = "succeeded"
    summary["created_by"] = "file_backed_pipeline"
    _persist_run_summary(settings, summary)
    return summary


def list_runs(root: Path | None = None, settings: AppSettings | None = None) -> list[dict[str, Any]]:
    resolved_root = root or project_root()
    if persistence_enabled(settings):
        persisted_runs = _list_persisted_runs(settings)
        if persisted_runs:
            return persisted_runs
    reports_dir = resolved_root / REPORTS_DEMO_PATH
    runs = []
    for package_path in sorted(reports_dir.rglob("report_package.json")):
        package = _load_json(package_path)
        runs.append(_run_summary_from_package(resolved_root, package_path, package))
    return sorted(runs, key=lambda run: (run.get("generated_at") or "", run["run_id"]), reverse=True)


def get_run(run_id: str, root: Path | None = None, settings: AppSettings | None = None) -> dict[str, Any]:
    if persistence_enabled(settings):
        persisted_run = _get_persisted_run(settings, run_id)
        if persisted_run:
            return persisted_run
    for run in list_runs(root, settings=None):
        if run["run_id"] == run_id:
            return run
    raise RunServiceError("run_not_found", f"Workflow run not found: {run_id}")


def report_index_metadata(root: Path | None = None) -> dict[str, Any]:
    resolved_root = root or project_root()
    index_path = resolved_root / REPORTS_DEMO_PATH / "index.html"
    return {
        "status": "available" if index_path.exists() else "missing",
        "path": _repo_relative_path(resolved_root, index_path),
        "url": _artifact_url(_repo_relative_path(resolved_root, index_path)),
        "run_count": _count_report_packages(resolved_root),
    }


def reports_demo_dir(root: Path | None = None) -> Path:
    return (root or project_root()) / REPORTS_DEMO_PATH


def _run_summary_from_package(root: Path, package_path: Path, package: dict[str, Any]) -> dict[str, Any]:
    metadata = package.get("run_metadata", {})
    workflow_template = package.get("workflow_template") or metadata.get("workflow_template") or {}
    data_coverage = package.get("data_coverage_result", {})
    valuation_summary = data_coverage.get("valuation_summary", {})
    source_name = metadata.get("source_name") or package.get("source_name") or "unknown_source"
    workflow_type = metadata.get("workflow_type") or package.get("workflow_type") or "unknown_workflow"
    output_dir = metadata.get("output_directory") or _repo_relative_path(root, package_path.parent)
    json_outputs = metadata.get("json_outputs", {})
    report_links = metadata.get("report_links", {})
    return {
        "run_id": metadata.get("run_id") or package.get("run_id") or package["report_id"],
        "source": source_name,
        "source_adapter": metadata.get("source_adapter") or package.get("source_adapter") or source_name,
        "workflow": workflow_type,
        "workflow_display_name": (
            metadata.get("workflow_display_name")
            or metadata.get("workflow_label")
            or workflow_template.get("display_name")
            or _label(workflow_type)
        ),
        "status": "succeeded",
        "generated_at": metadata.get("generated_at") or "",
        "valuation_date": metadata.get("valuation_date") or package.get("valuation_date") or "",
        "output_dir": output_dir,
        "synthetic_data": bool(metadata.get("synthetic_data", package.get("is_synthetic"))),
        "report_package": _artifact_record("Report package JSON", _repo_relative_path(root, package_path)),
        "markdown_report": _artifact_record("Markdown report", report_links.get("markdown")),
        "html_report": _artifact_record("HTML report", report_links.get("html")),
        "index": report_index_metadata(root),
        "json_outputs": {
            key: _artifact_record(_label(key), value)
            for key, value in sorted(json_outputs.items())
        },
        "data_confidence": valuation_summary.get("overall_confidence") or "not_available",
        "data_confidence_summary": data_coverage.get("summary") or "",
        "human_review_item_count": data_coverage.get("human_review_item_count"),
    }


def _validate_source(source: str) -> dict[str, str]:
    source_config = API_SOURCES.get(source)
    if not source_config:
        supported = ", ".join(API_SOURCES)
        raise RunServiceError("invalid_source", f"Unsupported source: {source}. Supported sources: {supported}")
    return source_config


def _validate_workflow(workflow: str) -> None:
    try:
        get_workflow_template(workflow)
    except WorkflowTemplateError as exc:
        raise RunServiceError("invalid_workflow", str(exc)) from exc


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise RunServiceError("invalid_artifact", f"Expected JSON object in {path.name}")
    return data


def _persist_run_summary(settings: AppSettings | None, summary: dict[str, Any]) -> None:
    try:
        persist_workflow_run_summary(settings, summary)
    except PersistenceError as exc:
        raise RunServiceError("persistence_failed", str(exc)) from exc


def _list_persisted_runs(settings: AppSettings | None) -> list[dict[str, Any]]:
    try:
        return list_persisted_workflow_runs(settings)
    except PersistenceError as exc:
        raise RunServiceError("persistence_failed", str(exc)) from exc


def _get_persisted_run(settings: AppSettings | None, run_id: str) -> dict[str, Any] | None:
    try:
        return get_persisted_workflow_run(settings, run_id)
    except PersistenceError as exc:
        raise RunServiceError("persistence_failed", str(exc)) from exc


def _count_report_packages(root: Path) -> int:
    return sum(1 for _ in (root / REPORTS_DEMO_PATH).rglob("report_package.json"))


def _artifact_record(label: str, path: str | None) -> dict[str, str | None]:
    return {
        "label": label,
        "path": path,
        "url": _artifact_url(path) if path else None,
    }


def _artifact_url(path: str | None) -> str | None:
    if not path:
        return None
    normalized = path.replace("\\", "/")
    if normalized.startswith("/") or ".." in normalized.split("/"):
        return None
    if normalized.startswith(f"{REPORTS_DEMO_PATH}/") or normalized == REPORTS_DEMO_PATH:
        return f"/{normalized}"
    return None


def _repo_relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as exc:
        raise RunServiceError("unsafe_artifact_path", f"Artifact path is outside project root: {path}") from exc


def _label(value: str) -> str:
    if value.lower() == "html":
        return "HTML"
    return value.replace("_", " ").title()
