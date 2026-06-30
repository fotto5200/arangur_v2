"""Optional workflow-run persistence for the FastAPI demo app."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from .settings import AppSettings


POSTGRES_ENGINE = "postgres"

CREATE_WORKFLOW_RUN_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS workflow_run (
    run_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_adapter TEXT,
    workflow_type TEXT NOT NULL,
    workflow_display_name TEXT,
    status TEXT NOT NULL,
    synthetic_data BOOLEAN NOT NULL DEFAULT TRUE,
    output_dir TEXT,
    generated_at TEXT,
    valuation_date TEXT,
    data_confidence_label TEXT,
    data_confidence_summary TEXT,
    human_review_item_count INTEGER,
    report_package_path TEXT,
    report_package_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_REPORT_ARTIFACT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS report_artifact (
    id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES workflow_run(run_id) ON DELETE CASCADE,
    artifact_type TEXT NOT NULL,
    label TEXT NOT NULL,
    path TEXT,
    url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, artifact_type)
)
"""

CREATE_RUN_EVENT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS run_event (
    id BIGSERIAL PRIMARY KEY,
    run_id TEXT REFERENCES workflow_run(run_id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    message TEXT,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_BRIEFING_SPEC_SET_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS briefing_spec_set (
    spec_set_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    title TEXT NOT NULL,
    client_name TEXT,
    portfolio_context TEXT,
    synthetic_data BOOLEAN NOT NULL DEFAULT TRUE,
    source TEXT NOT NULL,
    status TEXT NOT NULL,
    client_briefing_set_count INTEGER NOT NULL DEFAULT 0,
    advisor_review_set_count INTEGER NOT NULL DEFAULT 0,
    raw_spec_set_json JSONB NOT NULL,
    summary_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_BRIEFING_SPEC_ITEM_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS briefing_spec_item (
    item_id TEXT PRIMARY KEY,
    spec_set_id TEXT NOT NULL REFERENCES briefing_spec_set(spec_set_id) ON DELETE CASCADE,
    branch TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    element_id TEXT,
    element_title TEXT,
    placement TEXT,
    advisor_internal_purpose TEXT,
    parameters_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    matched_view_id TEXT,
    preview_available BOOLEAN NOT NULL DEFAULT FALSE,
    confidence_label TEXT,
    raw_spec_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (spec_set_id, branch, order_index)
)
"""

SCHEMA_STATEMENTS = (
    CREATE_WORKFLOW_RUN_TABLE_SQL,
    CREATE_REPORT_ARTIFACT_TABLE_SQL,
    CREATE_RUN_EVENT_TABLE_SQL,
    CREATE_BRIEFING_SPEC_SET_TABLE_SQL,
    CREATE_BRIEFING_SPEC_ITEM_TABLE_SQL,
)

UPSERT_WORKFLOW_RUN_SQL = """
INSERT INTO workflow_run (
    run_id,
    source,
    source_adapter,
    workflow_type,
    workflow_display_name,
    status,
    synthetic_data,
    output_dir,
    generated_at,
    valuation_date,
    data_confidence_label,
    data_confidence_summary,
    human_review_item_count,
    report_package_path,
    report_package_url
) VALUES (
    %(run_id)s,
    %(source)s,
    %(source_adapter)s,
    %(workflow_type)s,
    %(workflow_display_name)s,
    %(status)s,
    %(synthetic_data)s,
    %(output_dir)s,
    %(generated_at)s,
    %(valuation_date)s,
    %(data_confidence_label)s,
    %(data_confidence_summary)s,
    %(human_review_item_count)s,
    %(report_package_path)s,
    %(report_package_url)s
)
ON CONFLICT (run_id) DO UPDATE SET
    source = EXCLUDED.source,
    source_adapter = EXCLUDED.source_adapter,
    workflow_type = EXCLUDED.workflow_type,
    workflow_display_name = EXCLUDED.workflow_display_name,
    status = EXCLUDED.status,
    synthetic_data = EXCLUDED.synthetic_data,
    output_dir = EXCLUDED.output_dir,
    generated_at = EXCLUDED.generated_at,
    valuation_date = EXCLUDED.valuation_date,
    data_confidence_label = EXCLUDED.data_confidence_label,
    data_confidence_summary = EXCLUDED.data_confidence_summary,
    human_review_item_count = EXCLUDED.human_review_item_count,
    report_package_path = EXCLUDED.report_package_path,
    report_package_url = EXCLUDED.report_package_url,
    updated_at = NOW()
"""

INSERT_REPORT_ARTIFACT_SQL = """
INSERT INTO report_artifact (
    run_id,
    artifact_type,
    label,
    path,
    url
) VALUES (
    %(run_id)s,
    %(artifact_type)s,
    %(label)s,
    %(path)s,
    %(url)s
)
ON CONFLICT (run_id, artifact_type) DO UPDATE SET
    label = EXCLUDED.label,
    path = EXCLUDED.path,
    url = EXCLUDED.url
"""

INSERT_RUN_EVENT_SQL = """
INSERT INTO run_event (
    run_id,
    event_type,
    message,
    details_json
) VALUES (
    %(run_id)s,
    %(event_type)s,
    %(message)s,
    %(details_json)s::jsonb
)
"""

SELECT_WORKFLOW_RUNS_SQL = """
SELECT
    run_id,
    source,
    source_adapter,
    workflow_type,
    workflow_display_name,
    status,
    synthetic_data,
    output_dir,
    generated_at,
    valuation_date,
    data_confidence_label,
    data_confidence_summary,
    human_review_item_count,
    report_package_path,
    report_package_url
FROM workflow_run
ORDER BY COALESCE(generated_at, '') DESC, run_id DESC
"""

SELECT_WORKFLOW_RUN_SQL = """
SELECT
    run_id,
    source,
    source_adapter,
    workflow_type,
    workflow_display_name,
    status,
    synthetic_data,
    output_dir,
    generated_at,
    valuation_date,
    data_confidence_label,
    data_confidence_summary,
    human_review_item_count,
    report_package_path,
    report_package_url
FROM workflow_run
WHERE run_id = %s
"""

SELECT_ARTIFACTS_SQL = """
SELECT artifact_type, label, path, url
FROM report_artifact
WHERE run_id = %s
ORDER BY artifact_type
"""


class PersistenceError(RuntimeError):
    """Raised when optional workflow-run persistence cannot complete."""


def persistence_enabled(settings: AppSettings | None) -> bool:
    return bool(settings and settings.db_engine == POSTGRES_ENGINE and settings.database_url)


def initialize_schema_if_needed(settings: AppSettings | None) -> bool:
    """Create minimal Postgres tables when Postgres persistence is enabled."""

    if not persistence_enabled(settings):
        return False
    try:
        with _connect(settings) as connection:
            with connection.cursor() as cursor:
                for statement in SCHEMA_STATEMENTS:
                    cursor.execute(statement)
        return True
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not initialize workflow-run schema: {exc}") from exc


def persist_workflow_run_summary(settings: AppSettings | None, run_summary: dict[str, Any]) -> bool:
    """Persist a run summary, its artifact references, and a success event."""

    if not persistence_enabled(settings):
        return False
    try:
        initialize_schema_if_needed(settings)
        run_record = workflow_run_record_from_summary(run_summary)
        artifacts = artifact_records_from_run_summary(run_summary)
        with _connect(settings) as connection:
            with connection.cursor() as cursor:
                _record_workflow_run(cursor, run_record)
                _record_report_artifacts(cursor, run_record["run_id"], artifacts)
                _record_run_event(
                    cursor,
                    run_record["run_id"],
                    "run_succeeded",
                    "Workflow run persisted after local report generation.",
                    {"source": run_record["source"], "workflow_type": run_record["workflow_type"]},
                )
        return True
    except PersistenceError:
        raise
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not persist workflow run: {exc}") from exc


def record_workflow_run(settings: AppSettings | None, run_summary: dict[str, Any]) -> bool:
    if not persistence_enabled(settings):
        return False
    try:
        initialize_schema_if_needed(settings)
        with _connect(settings) as connection:
            with connection.cursor() as cursor:
                _record_workflow_run(cursor, workflow_run_record_from_summary(run_summary))
        return True
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not record workflow run: {exc}") from exc


def list_workflow_runs(settings: AppSettings | None) -> list[dict[str, Any]]:
    if not persistence_enabled(settings):
        return []
    try:
        initialize_schema_if_needed(settings)
        with _connect(settings, dict_rows=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(SELECT_WORKFLOW_RUNS_SQL)
                rows = list(cursor.fetchall())
                return [_summary_from_record(row, _artifact_rows(cursor, row["run_id"])) for row in rows]
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not list workflow runs: {exc}") from exc


def get_workflow_run(settings: AppSettings | None, run_id: str) -> dict[str, Any] | None:
    if not persistence_enabled(settings):
        return None
    try:
        initialize_schema_if_needed(settings)
        with _connect(settings, dict_rows=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(SELECT_WORKFLOW_RUN_SQL, (run_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return _summary_from_record(row, _artifact_rows(cursor, run_id))
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not read workflow run: {exc}") from exc


def record_report_artifacts(
    settings: AppSettings | None,
    run_id: str,
    artifacts: Iterable[dict[str, str | None]],
) -> bool:
    if not persistence_enabled(settings):
        return False
    try:
        initialize_schema_if_needed(settings)
        with _connect(settings) as connection:
            with connection.cursor() as cursor:
                _record_report_artifacts(cursor, run_id, artifacts)
        return True
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not record report artifacts: {exc}") from exc


def record_run_event(
    settings: AppSettings | None,
    run_id: str | None,
    event_type: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> bool:
    if not persistence_enabled(settings):
        return False
    try:
        initialize_schema_if_needed(settings)
        with _connect(settings) as connection:
            with connection.cursor() as cursor:
                _record_run_event(cursor, run_id, event_type, message, details)
        return True
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not record run event: {exc}") from exc


def workflow_run_record_from_summary(run_summary: dict[str, Any]) -> dict[str, Any]:
    report_package = _artifact(run_summary.get("report_package"))
    return {
        "run_id": run_summary["run_id"],
        "source": run_summary.get("source") or "unknown_source",
        "source_adapter": run_summary.get("source_adapter"),
        "workflow_type": run_summary.get("workflow") or "unknown_workflow",
        "workflow_display_name": run_summary.get("workflow_display_name"),
        "status": run_summary.get("status") or "unknown",
        "synthetic_data": bool(run_summary.get("synthetic_data")),
        "output_dir": run_summary.get("output_dir"),
        "generated_at": run_summary.get("generated_at"),
        "valuation_date": run_summary.get("valuation_date"),
        "data_confidence_label": run_summary.get("data_confidence"),
        "data_confidence_summary": run_summary.get("data_confidence_summary"),
        "human_review_item_count": run_summary.get("human_review_item_count"),
        "report_package_path": report_package.get("path"),
        "report_package_url": report_package.get("url"),
    }


def artifact_records_from_run_summary(run_summary: dict[str, Any]) -> list[dict[str, str | None]]:
    artifacts = []
    top_level_artifact_types = {"report_package", "markdown_report", "html_report", "index"}
    for artifact_type in ("report_package", "markdown_report", "html_report", "index"):
        record = _artifact(run_summary.get(artifact_type))
        if record:
            artifacts.append(
                {
                    "artifact_type": artifact_type,
                    "label": record.get("label") or _label(artifact_type),
                    "path": record.get("path"),
                    "url": record.get("url"),
                }
            )
    json_outputs = run_summary.get("json_outputs") or {}
    for artifact_type, record_value in sorted(json_outputs.items()):
        if artifact_type in top_level_artifact_types:
            continue
        record = _artifact(record_value)
        if record:
            artifacts.append(
                {
                    "artifact_type": artifact_type,
                    "label": record.get("label") or _label(artifact_type),
                    "path": record.get("path"),
                    "url": record.get("url"),
                }
            )
    return artifacts


def _record_workflow_run(cursor: Any, run_record: dict[str, Any]) -> None:
    cursor.execute(UPSERT_WORKFLOW_RUN_SQL, run_record)


def _record_report_artifacts(
    cursor: Any,
    run_id: str,
    artifacts: Iterable[dict[str, str | None]],
) -> None:
    for artifact in artifacts:
        cursor.execute(
            INSERT_REPORT_ARTIFACT_SQL,
            {
                "run_id": run_id,
                "artifact_type": artifact["artifact_type"],
                "label": artifact["label"],
                "path": artifact.get("path"),
                "url": artifact.get("url"),
            },
        )


def _record_run_event(
    cursor: Any,
    run_id: str | None,
    event_type: str,
    message: str,
    details: dict[str, Any] | None,
) -> None:
    cursor.execute(
        INSERT_RUN_EVENT_SQL,
        {
            "run_id": run_id,
            "event_type": event_type,
            "message": message,
            "details_json": json.dumps(details or {}, sort_keys=True),
        },
    )


def _artifact_rows(cursor: Any, run_id: str) -> list[dict[str, Any]]:
    cursor.execute(SELECT_ARTIFACTS_SQL, (run_id,))
    return list(cursor.fetchall())


def _summary_from_record(row: dict[str, Any], artifact_rows: list[dict[str, Any]]) -> dict[str, Any]:
    artifacts = {
        artifact["artifact_type"]: {
            "label": artifact["label"],
            "path": artifact["path"],
            "url": artifact["url"],
        }
        for artifact in artifact_rows
    }
    json_outputs = {
        key: value
        for key, value in artifacts.items()
        if key
        not in {
            "report_package",
            "markdown_report",
            "html_report",
            "index",
        }
    }
    return {
        "run_id": row["run_id"],
        "source": row["source"],
        "source_adapter": row["source_adapter"],
        "workflow": row["workflow_type"],
        "workflow_display_name": row["workflow_display_name"],
        "status": row["status"],
        "generated_at": row["generated_at"] or "",
        "valuation_date": row["valuation_date"] or "",
        "output_dir": row["output_dir"],
        "synthetic_data": bool(row["synthetic_data"]),
        "report_package": artifacts.get(
            "report_package",
            {
                "label": "Report package JSON",
                "path": row["report_package_path"],
                "url": row["report_package_url"],
            },
        ),
        "markdown_report": artifacts.get("markdown_report", _empty_artifact("Markdown report")),
        "html_report": artifacts.get("html_report", _empty_artifact("HTML report")),
        "index": artifacts.get("index", _empty_artifact("Report index")),
        "json_outputs": json_outputs,
        "data_confidence": row["data_confidence_label"] or "not_available",
        "data_confidence_summary": row["data_confidence_summary"] or "",
        "human_review_item_count": row["human_review_item_count"],
        "created_by": "postgres_persistence",
    }


def _connect(settings: AppSettings, dict_rows: bool = False) -> Any:
    if not settings.database_url:
        raise PersistenceError("DATABASE_URL is required when DB_ENGINE=postgres")
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - depends on optional installation.
        raise PersistenceError("psycopg is required when DB_ENGINE=postgres") from exc

    kwargs: dict[str, Any] = {}
    if dict_rows:
        try:
            from psycopg.rows import dict_row
        except ImportError as exc:  # pragma: no cover - depends on optional installation.
            raise PersistenceError("psycopg row helpers are required for persisted run reads") from exc
        kwargs["row_factory"] = dict_row
    return psycopg.connect(settings.database_url, **kwargs)


def _artifact(value: Any) -> dict[str, str | None]:
    if isinstance(value, dict):
        return {
            "label": value.get("label"),
            "path": value.get("path"),
            "url": value.get("url"),
        }
    return {}


def _empty_artifact(label: str) -> dict[str, str | None]:
    return {"label": label, "path": None, "url": None}


def _label(value: str) -> str:
    if value.lower() == "html":
        return "HTML"
    return value.replace("_", " ").title()
