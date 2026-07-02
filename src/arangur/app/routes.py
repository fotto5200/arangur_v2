"""FastAPI routes for local file-backed demo workflow runs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from arangur.report_elements import ReportElementCatalogError, filter_templates, get_template

from .briefing_spec_sets import (
    BriefingSpecSetError,
    delete_briefing_spec_set,
    get_briefing_spec_set,
    list_briefing_spec_sets,
    save_briefing_spec_set,
)
from .generated_reports import GeneratedReportError, build_demo_populated_report_artifact
from .persistence import PersistenceError, persistence_enabled
from .run_service import (
    RunServiceError,
    create_workflow_run,
    get_run,
    list_runs,
    list_sources,
    list_workflows,
    report_index_metadata,
)


router = APIRouter(prefix="/api")


class RunCreateRequest(BaseModel):
    source: str
    workflow: str


@router.get("/sources")
def sources() -> dict[str, Any]:
    return {"sources": list_sources()}


@router.get("/workflows")
def workflows() -> dict[str, Any]:
    return {"workflows": list_workflows()}


@router.get("/report-elements")
def report_elements(
    branch: str | None = None,
    category: str | None = None,
    q: str | None = None,
    client_question: str | None = None,
    advisor_intent: str | None = None,
    tag: list[str] | None = Query(default=None),
) -> dict[str, Any]:
    try:
        templates = filter_templates(
            branch=branch,
            category=category,
            query=q,
            tags=tag,
            client_question=client_question,
            advisor_intent=advisor_intent,
        )
    except ReportElementCatalogError as exc:
        raise _catalog_http_error(exc) from exc
    return {
        "templates": templates,
        "count": len(templates),
    }


@router.get("/report-elements/{element_id}")
def report_element_detail(element_id: str) -> dict[str, Any]:
    try:
        template = get_template(element_id)
    except ReportElementCatalogError as exc:
        raise _catalog_http_error(exc) from exc
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "report_element_template_not_found",
                "message": f"Report element template not found: {element_id}",
            },
        )
    return template


@router.post("/briefing-spec-sets")
def create_briefing_spec_set(payload: dict[str, Any], http_request: Request) -> dict[str, Any]:
    try:
        return save_briefing_spec_set(http_request.app.state.settings, payload)
    except BriefingSpecSetError as exc:
        raise _briefing_spec_set_http_error(exc) from exc
    except PersistenceError as exc:
        raise _persistence_http_error(exc) from exc


@router.get("/briefing-spec-sets")
def briefing_spec_sets(http_request: Request) -> dict[str, Any]:
    settings = http_request.app.state.settings
    try:
        configured = persistence_enabled(settings)
        return {
            "persistence_configured": configured,
            "message": ""
            if configured
            else "Backend persistence is not configured. Use local export/download for now.",
            "spec_sets": list_briefing_spec_sets(settings),
        }
    except PersistenceError as exc:
        raise _persistence_http_error(exc) from exc


@router.get("/briefing-spec-sets/{spec_set_id}")
def briefing_spec_set_detail(spec_set_id: str, http_request: Request) -> dict[str, Any]:
    try:
        detail = get_briefing_spec_set(http_request.app.state.settings, spec_set_id)
    except PersistenceError as exc:
        raise _persistence_http_error(exc) from exc
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "briefing_spec_set_not_found",
                "message": f"Briefing spec set not found: {spec_set_id}",
            },
        )
    return detail


@router.post("/generated-reports/demo-populate")
def demo_populate_generated_report(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return build_demo_populated_report_artifact(payload)
    except GeneratedReportError as exc:
        raise _generated_report_http_error(exc) from exc


@router.delete("/briefing-spec-sets/{spec_set_id}")
def remove_briefing_spec_set(spec_set_id: str, http_request: Request) -> dict[str, Any]:
    settings = http_request.app.state.settings
    try:
        configured = persistence_enabled(settings)
        deleted = delete_briefing_spec_set(settings, spec_set_id)
    except PersistenceError as exc:
        raise _persistence_http_error(exc) from exc
    return {
        "persistence_configured": configured,
        "deleted": deleted,
        "message": ""
        if configured
        else "Backend persistence is not configured. Use local export/download for now.",
    }


@router.post("/runs")
def create_run(request: RunCreateRequest, http_request: Request) -> dict[str, Any]:
    try:
        return create_workflow_run(
            request.source,
            request.workflow,
            settings=http_request.app.state.settings,
        )
    except RunServiceError as exc:
        raise _http_error(exc) from exc


@router.get("/runs")
def runs(http_request: Request) -> dict[str, Any]:
    try:
        return {"runs": list_runs(settings=http_request.app.state.settings)}
    except RunServiceError as exc:
        raise _http_error(exc) from exc


@router.get("/runs/{run_id}")
def run_detail(run_id: str, http_request: Request) -> dict[str, Any]:
    try:
        return get_run(run_id, settings=http_request.app.state.settings)
    except RunServiceError as exc:
        raise _http_error(exc) from exc


@router.get("/reports/index")
def report_index() -> dict[str, Any]:
    return report_index_metadata()


def _http_error(exc: RunServiceError) -> HTTPException:
    status_code = 404 if exc.code == "run_not_found" else 400
    if exc.code in {"pipeline_failed", "persistence_failed"}:
        status_code = 500
    return HTTPException(
        status_code=status_code,
        detail={
            "code": exc.code,
            "message": exc.message,
        },
    )


def _catalog_http_error(exc: ReportElementCatalogError) -> HTTPException:
    return HTTPException(
        status_code=500,
        detail={
            "code": "report_element_catalog_invalid",
            "message": str(exc),
        },
    )


def _briefing_spec_set_http_error(exc: BriefingSpecSetError) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "code": exc.code,
            "message": exc.message,
        },
    )


def _persistence_http_error(exc: PersistenceError) -> HTTPException:
    return HTTPException(
        status_code=500,
        detail={
            "code": "persistence_failed",
            "message": str(exc),
        },
    )


def _generated_report_http_error(exc: GeneratedReportError) -> HTTPException:
    status_code = 400
    if exc.code == "generated_report_invalid":
        status_code = 500
    return HTTPException(
        status_code=status_code,
        detail={
            "code": exc.code,
            "message": exc.message,
        },
    )
