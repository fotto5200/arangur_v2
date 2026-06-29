"""FastAPI routes for local file-backed demo workflow runs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from arangur.report_elements import ReportElementCatalogError, filter_templates, get_template

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
