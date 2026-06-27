"""FastAPI routes for local file-backed demo workflow runs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

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
